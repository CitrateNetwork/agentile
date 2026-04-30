---
created: 2026-04-30T05:00:00Z
branch: main
author: agentile-skeleton
status: active
---

# `scripts/eval/` — human eval, data-source check, benchmark harness

> The "softer" enforcement layer. Where `scripts/ci/` enforces
> mechanical rules and `scripts/ai/` runs LLM-graded soft gates,
> `scripts/eval/` is the layer that interfaces with humans
> (eval protocol) and with measurement (benchmarks).

## Files

| File | Purpose |
|------|---------|
| `human_eval_protocol.md` | The protocol a human reviewer follows at sprint close, audit closure, or security-sensitive PR |
| `data_source_check.py` | Rule 11 heuristic — flags endpoints lacking `data source:` comments |
| `benchmark_harness.sh` | Runs every executable in `scenarios/`, aggregates BENCH lines into a JSON report |
| `check_regression.py` | Compares a fresh run against a stored baseline; flags regressions per metric direction |
| `scenarios/` | Project-specific benchmark adapters (drop executables in) |
| `baselines/` | Per-run JSON snapshots; `canonical.json` is the pinned reference |

## How they fit together

The four-ratchet model (test count, formal specs, CI tripwires,
frontmatter coverage) measures *correctness floor*. The benchmark
harness measures *performance floor*. Performance is intentionally
NOT a fifth ratchet because:

- Performance varies across CI runners (noisy).
- Regressions are sometimes acceptable (a security fix that costs
  10% throughput is usually a win).
- The regression check should produce a comment that humans review,
  not a hard block — same shape as the AI graders.

For projects that want a hard performance gate, the regression
check supports `--strict --threshold N`; the workflow can be
modified to use it.

The data-source check is the heuristic counterpart to the AI claim
grader: it catches Rule 11 violations at regex level (specific,
fast, false-positive-prone). The AI grader catches them
semantically (slower, more accurate, costs API calls). Together they
cover different parts of the fault surface.

The human eval protocol is what makes everything else trustworthy:
the mechanical gates, AI gates, and benchmark gates all have known
false negatives. A human reviewer is the last entity that holds
the *whole* claim in mind and decides whether the work matches the
words.

## Shadow mode

All `scripts/eval/` tools default to shadow mode: they post
informational comments on PRs but never block merges. The hard-mode
opt-in is the same pattern as `scripts/ai/`:

1. Add `--strict` to the script invocation in the workflow.
2. Remove `continue-on-error: true` from the workflow job.
3. Add the job as a required check in branch protection rules.

The 2-week calibration period (per project planset) is when the
project owner watches the comments and confirms the false-positive
rate is acceptable. After calibration, hard mode is opt-in.

## See also

- `scripts/ci/` — hard mechanical gates
- `scripts/ai/` — AI-graded soft gates
- `scripts/semgrep/` — AST-grade tripwire rules
- `.github/workflows/data-source-check.yml`
- `.github/workflows/benchmark-nightly.yml`
- `.agentile/rules/CORE_RULES.md` — the rules these tools support
