#!/usr/bin/env python3
"""Compare a fresh benchmark run against a stored baseline.

Reads two JSON files (produced by `benchmark_harness.sh`):
  - --baseline    the reference run (typically last week's main-branch run)
  - --current     the run to evaluate (defaults to baselines/latest.json)

For each metric present in BOTH files, computes the delta and flags
metrics that regressed by more than `--threshold` percent (default
10%). Output is JSON + a markdown summary.

Direction-aware: by default, "lower is better" for latency-style
metrics (suffix `_seconds`, `_ms`, `_us`, `_latency`, `_p50`, `_p95`,
`_p99`); "higher is better" for throughput-style metrics (suffix
`_tps`, `_rps`, `_qps`, `_throughput`, `_count`, `_bytes_per_sec`).
Metrics not matching either suffix pattern are treated as "lower is
better" (the conservative default — a metric you're not measuring
in throughput terms is usually a cost you want minimized).

Override per-metric direction via `direction.json`:
  {"my_custom_metric": "higher_better"}
co-located with this script. Same shape as the metrics map produced
by the harness, but values are direction strings.

Exit codes:
  0 — no regressions exceeded threshold OR shadow mode (always 0)
  1 — regressions found (only with --strict)
  2 — usage / file-not-found
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "index"))
from _common import find_project_root  # type: ignore  # noqa: E402

PROJECT_ROOT = find_project_root()
DEFAULT_LATEST = PROJECT_ROOT / "scripts" / "eval" / "baselines" / "latest.json"
DIRECTION_OVERRIDE_PATH = PROJECT_ROOT / "scripts" / "eval" / "direction.json"

LOWER_BETTER_SUFFIXES = ("_seconds", "_ms", "_us", "_latency", "_p50", "_p95", "_p99")
HIGHER_BETTER_SUFFIXES = ("_tps", "_rps", "_qps", "_throughput", "_count", "_bytes_per_sec")


def metric_direction(name: str, override: dict[str, str]) -> str:
    if name in override:
        return override[name]
    if any(name.endswith(s) for s in HIGHER_BETTER_SUFFIXES):
        return "higher_better"
    return "lower_better"


def load_json(path: Path) -> dict:
    if not path.exists():
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        raise SystemExit(2)
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--baseline", required=True,
                   help="Path to the reference run's JSON file")
    p.add_argument("--current", default=str(DEFAULT_LATEST),
                   help="Path to the current run's JSON (default: baselines/latest.json)")
    p.add_argument("--threshold", type=float, default=10.0,
                   help="Regression threshold in percent (default: 10.0)")
    p.add_argument("--strict", action="store_true",
                   help="Exit 1 on regression (default: shadow / always 0)")
    p.add_argument("--out-md", help="Write a markdown summary to this path")
    args = p.parse_args()

    base = load_json(Path(args.baseline))
    cur = load_json(Path(args.current))

    direction_override: dict[str, str] = {}
    if DIRECTION_OVERRIDE_PATH.exists():
        try:
            direction_override = json.loads(DIRECTION_OVERRIDE_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"WARN: could not parse {DIRECTION_OVERRIDE_PATH}: {e}", file=sys.stderr)

    base_metrics = base.get("metrics", {})
    cur_metrics = cur.get("metrics", {})

    results: list[dict] = []
    regressions: list[dict] = []

    for name in sorted(set(base_metrics) | set(cur_metrics)):
        b = base_metrics.get(name)
        c = cur_metrics.get(name)
        if b is None:
            results.append({"metric": name, "status": "new", "current": c})
            continue
        if c is None:
            results.append({"metric": name, "status": "missing", "baseline": b})
            continue
        b_val = float(b["value"])
        c_val = float(c["value"])
        if b_val == 0:
            pct = float("inf") if c_val != 0 else 0.0
        else:
            pct = ((c_val - b_val) / abs(b_val)) * 100.0
        direction = metric_direction(name, direction_override)
        # Regression: change in the wrong direction beyond threshold.
        regressed = (
            (direction == "lower_better" and pct > args.threshold)
            or (direction == "higher_better" and pct < -args.threshold)
        )
        entry = {
            "metric": name,
            "status": "regressed" if regressed else "ok",
            "baseline": b_val,
            "current": c_val,
            "delta_pct": round(pct, 2),
            "direction": direction,
            "unit": c.get("unit", b.get("unit", "")),
        }
        results.append(entry)
        if regressed:
            regressions.append(entry)

    report = {
        "baseline_run": base.get("run_id"),
        "current_run": cur.get("run_id"),
        "threshold_pct": args.threshold,
        "regressions": regressions,
        "results": results,
    }
    print(json.dumps(report, indent=2))

    if args.out_md:
        lines: list[str] = []
        lines.append("## Benchmark regression check (shadow mode)")
        lines.append("")
        lines.append(f"- Baseline run: `{base.get('run_id', '?')}`")
        lines.append(f"- Current run: `{cur.get('run_id', '?')}`")
        lines.append(f"- Threshold: ±{args.threshold}%")
        lines.append("")
        if not regressions:
            lines.append(f"**No regressions** — {len(results)} metric(s) compared.")
        else:
            lines.append(f"**{len(regressions)} regression(s) detected:**")
            lines.append("")
            lines.append("| Metric | Baseline | Current | Δ% | Direction |")
            lines.append("|--------|----------|---------|-----|-----------|")
            for r in regressions:
                lines.append(f"| `{r['metric']}` | {r['baseline']} {r['unit']} | "
                             f"{r['current']} {r['unit']} | {r['delta_pct']:+.2f}% | "
                             f"{r['direction']} |")
        Path(args.out_md).write_text("\n".join(lines), encoding="utf-8")

    if args.strict and regressions:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
