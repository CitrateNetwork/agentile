#!/usr/bin/env python3
"""Ratchet 3: CI tripwire count never decreases.

Counts active tripwires:
  - `scripts/semgrep/*.yaml` and `scripts/semgrep/*.yml`
  - `scripts/ci/check_*.py` (the check scripts themselves)

Compares to baseline.tripwires.count from
`.agentile/coverage/baseline.json`.

The principle: tripwires are append-only. You may add new ones; you
may not silently delete one. A removal requires explicit justification
in the PR description (which the reviewer enforces — this script only
catches silent removal by counting).

Exit codes:
  0 — count >= baseline
  1 — count decreased
  2 — usage error
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "index"))
from _common import find_project_root  # type: ignore  # noqa: E402
from _baseline import load_baseline  # type: ignore  # noqa: E402

PROJECT_ROOT = find_project_root()


def collect_tripwires() -> list[Path]:
    out: list[Path] = []
    semgrep_dir = PROJECT_ROOT / "scripts" / "semgrep"
    if semgrep_dir.exists():
        out.extend(p for p in semgrep_dir.rglob("*.yaml") if p.is_file())
        out.extend(p for p in semgrep_dir.rglob("*.yml") if p.is_file())
    ci_dir = PROJECT_ROOT / "scripts" / "ci"
    if ci_dir.exists():
        # Exclude the ratchet scripts themselves (they enforce the count;
        # they are not themselves tripwires being counted). Definitionally,
        # a tripwire detects a finding-class; ratchet checks measure deltas.
        ratchet_names = {
            "check_test_ratchet.py",
            "check_spec_ratchet.py",
            "check_tripwire_ratchet.py",
        }
        for p in ci_dir.glob("check_*.py"):
            if p.name not in ratchet_names:
                out.append(p)
    return sorted(out)


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        return 0

    baseline = load_baseline().get("tripwires", {})
    base_count = int(baseline.get("count", 0) or 0)

    tripwires = collect_tripwires()
    current = len(tripwires)

    print(f"Tripwire count: {current}")
    print(f"Baseline:       {base_count}")
    if tripwires and len(tripwires) <= 30:
        print()
        print("Active tripwires:")
        for p in tripwires:
            print(f"  - {p.relative_to(PROJECT_ROOT)}")

    if current < base_count:
        print()
        print(f"BLOCKER: tripwire count decreased ({base_count} -> {current}).")
        print("Removing a tripwire requires explicit justification in the PR")
        print("description — typically 'superseded by AST-level rule X' or")
        print("'finding class no longer applicable: <reason>'.")
        return 1
    if current > base_count:
        print(f"Tripwire count grew by {current - base_count} (good).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
