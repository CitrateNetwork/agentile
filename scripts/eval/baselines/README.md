---
created: 2026-04-30T05:00:00Z
branch: main
author: agentile-skeleton
status: active
---

# `scripts/eval/baselines/` — benchmark run history

> Per-run JSON snapshots produced by `benchmark_harness.sh`. Each
> file is one timestamped run; `latest.json` is a symlink to the
> most recent.

## File format

Filename: `<UTC-timestamp>_<short-git-sha>.json`

Example: `2026-05-14T030000Z_a3b4c5d6.json`

Shape:

```json
{
  "run_id":     "<timestamp>_<sha>",
  "timestamp":  "YYYY-MM-DDTHHMMSSZ",
  "git_sha":    "<full sha>",
  "git_branch": "<branch name>",
  "scenarios": [
    {
      "name":             "<scenario filename>",
      "status":           "ok" | "failed",
      "elapsed_seconds":  <float>,
      "metrics":          { "<metric>": {"value": ..., "unit": "..."}, ... },
      "log_excerpt":      "<last 500 bytes of stdout/stderr, JSON-escaped>"
    },
    ...
  ],
  "metrics": {
    "<scenario>.<metric>": {"value": ..., "unit": "..."},
    ...
  }
}
```

## Retention

The skeleton's default `.gitignore` excludes
`scripts/eval/baselines/*.json` (so per-run snapshots don't bloat
the repo) but keeps `README.md`. Projects that want to retain a
specific reference run in git can `git add -f` it; everything else
lives in CI artifacts.

The `benchmark-nightly.yml` workflow uploads each run as a workflow
artifact with 90-day retention by default. If a project wants
longer history, increase the artifact retention or push selected
runs into an S3-style bucket via an additional workflow step.

## Promoting a run to "the baseline"

To establish a stable baseline run that the regression checker
compares against:

```bash
# Run the harness against a known-good commit.
git checkout <good-commit>
./scripts/eval/benchmark_harness.sh
# Copy that run as the canonical baseline.
cp scripts/eval/baselines/<that-run>.json scripts/eval/baselines/canonical.json
git add -f scripts/eval/baselines/canonical.json
git commit -m "chore: pin benchmark canonical baseline at <good-commit>"
```

Subsequent regression checks pass `--baseline scripts/eval/baselines/canonical.json`.
The canonical baseline is updated deliberately (not on every run);
the cadence is a project-level decision (typically: at every release
tag, or every N weeks).

## See also

- `../benchmark_harness.sh` — produces these files
- `../check_regression.py` — consumes them
- `../scenarios/README.md` — the scenarios that emit metrics
