#!/usr/bin/env python3
"""Execute the sprint rename plan in .agentile/INDEX/SPRINT_RENAME_PLAN.tsv.

Runs `git mv old_path new_path` for each row marked Y. Stops on collision
or git error. Idempotent: skips rows where source is already missing or
target already matches.

Cross-reference rewrites are NOT done here — see `rewrite_sprint_xrefs.py`.
The intended sequence is:
  1. build_sprint_rename_plan.py   (read-only, generates the plan)
  2. apply_sprint_rename_plan.py   (this script — moves the directories)
  3. rewrite_sprint_xrefs.py       (rewrites slug references in .md files)
"""
from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import find_project_root  # noqa: E402

REPO_ROOT = find_project_root()
PLAN = REPO_ROOT / ".agentile" / "INDEX" / "SPRINT_RENAME_PLAN.tsv"


def main() -> int:
    if not PLAN.exists():
        print(f"ERROR: plan not found at {PLAN}", file=sys.stderr)
        print("       Run `scripts/index/build_sprint_rename_plan.py` first.", file=sys.stderr)
        return 1

    moved = skipped = failed = 0
    failures: list[tuple[str, str, str]] = []

    with PLAN.open(newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            if row["rename_needed"] != "Y":
                skipped += 1
                continue
            old, new = row["old_path"], row["new_path"]
            old_full, new_full = REPO_ROOT / old, REPO_ROOT / new
            if not old_full.exists():
                skipped += 1
                continue
            if old == new:
                skipped += 1
                continue
            if new_full.exists():
                failed += 1
                failures.append((old, new, "target already exists"))
                continue
            proc = subprocess.run(
                ["git", "-C", str(REPO_ROOT), "mv", old, new],
                capture_output=True,
                text=True,
            )
            if proc.returncode == 0:
                moved += 1
            else:
                failed += 1
                failures.append((old, new, (proc.stderr or proc.stdout).strip()))

    print(f"Renamed: {moved}")
    print(f"Skipped: {skipped}")
    print(f"Failed:  {failed}")
    for old, new, err in failures[:20]:
        print(f"  ! {old} -> {new}  ({err})")
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
