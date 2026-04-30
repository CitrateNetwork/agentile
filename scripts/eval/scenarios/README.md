---
created: 2026-04-30T05:00:00Z
branch: main
author: agentile-skeleton
status: active
---

# `scripts/eval/scenarios/` — benchmark scenario adapters

> Drop executable scenarios in this directory. The harness runs each
> one as a subprocess and aggregates its output into a single JSON
> report. Language-agnostic: bash, Python, Rust binaries, anything
> chmod +x will work.

## The contract

Each scenario file:

1. Lives directly in `scripts/eval/scenarios/` (not in a subdirectory).
2. Is executable (`chmod +x`).
3. Sets up its own preconditions (start a node, prepare data, etc.).
4. Runs its workload.
5. Emits one or more lines to stdout in the form:

   ```
   BENCH <metric_name> <value> [unit]
   ```

   Where:
   - `<metric_name>` is a stable identifier (no spaces, snake_case).
   - `<value>` is a number (integer or float; no commas).
   - `[unit]` is optional (e.g. `tps`, `seconds`, `ms`, `bytes`).

6. Cleans up after itself if applicable.
7. Exits 0 on success, non-zero on failure (failure flags the
   scenario as `status: failed` in the report; metrics already
   emitted are still recorded).

## Example: bash scenario

`scripts/eval/scenarios/echo_throughput.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail
# Measures how many lines /bin/echo can emit per second. Toy example.
start=$(date +%s.%N)
N=100000
for ((i=0; i<N; i++)); do echo "$i" >/dev/null; done
end=$(date +%s.%N)
elapsed=$(awk "BEGIN{print $end - $start}")
tps=$(awk "BEGIN{print $N / $elapsed}")
echo "BENCH echo_lines_per_second $tps lines_per_sec"
echo "BENCH echo_elapsed $elapsed seconds"
```

## Example: Python scenario

`scripts/eval/scenarios/parser_throughput.py`

```python
#!/usr/bin/env python3
"""Parser throughput benchmark — toy example."""
import json
import time
N = 50_000
sample = '{"a": 1, "b": [2, 3, 4]}'
start = time.perf_counter()
for _ in range(N):
    json.loads(sample)
elapsed = time.perf_counter() - start
print(f"BENCH json_loads_per_second {int(N / elapsed)} ops_per_sec")
print(f"BENCH json_loads_elapsed {elapsed:.4f} seconds")
```

## Example: wrapping a real benchmark framework

`scripts/eval/scenarios/cargo_bench_wrap.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail
# Run cargo bench and translate its output to BENCH lines.
output=$(cargo bench --bench tps 2>/dev/null)
# Adapt the parser to your framework's output format.
tps=$(echo "$output" | grep "tps:" | awk '{print $NF}')
echo "BENCH workspace_tps $tps tps"
```

## Direction conventions

The regression checker assumes "lower is better" by default and
"higher is better" for metrics whose names end in `_tps`, `_rps`,
`_qps`, `_throughput`, `_count`, `_bytes_per_sec`. Override per-metric
directions in `scripts/eval/direction.json`:

```json
{
  "scenario_name.metric_name": "higher_better",
  "scenario_name.error_count": "lower_better"
}
```

The metric key in `direction.json` matches the harness's flattened
key (`<scenario_filename>.<metric_name>`).

## What scenarios should NOT do

- **Don't depend on external services** unless the scenario exists
  to measure those services. CI runs scenarios in fresh runners
  with no persistent state.
- **Don't write outside `/tmp`.** Scenarios should be hermetic —
  writing into the repo causes spurious diffs in CI.
- **Don't take longer than ~5 minutes.** The nightly workflow has
  a 60-minute total cap; staying under 5min/scenario keeps the
  fleet manageable. If a scenario is genuinely longer, schedule
  it on a separate weekly cadence.
- **Don't print anything to stderr that isn't an error.** stderr
  is captured but not parsed for metrics; chatty scenarios make
  CI logs hard to read.

## Failure semantics

If a scenario fails (non-zero exit):
- The harness records `status: failed` for that scenario.
- Metrics already emitted (before the failure) are recorded.
- Other scenarios continue running.
- The harness itself returns 0 — failures here aren't infrastructure
  failures.

A scenario that consistently fails should either be fixed or
removed. Don't leave broken scenarios in tree.

## See also

- `../benchmark_harness.sh` — the runner that invokes each scenario
- `../check_regression.py` — compares a fresh run against a baseline
- `.github/workflows/benchmark-nightly.yml` — schedules the harness
- `.agentile/coverage/GATES.md` — performance is not one of the
  four ratchets, but a project may add it as a fifth project-level
  ratchet by reading the harness's JSON output
