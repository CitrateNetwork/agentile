#!/usr/bin/env python3
"""Execute the rename plan in .agentile/INDEX/RENAME_PLAN.tsv.

Runs `git mv old_path new_path` for every row marked Y. Stops on any
collision (target already exists) or git error. Idempotent: rows where
old_path is already missing OR new_path already matches are skipped.

Run `scripts/index/build_rename_plan.py` first to generate the plan.
"""
from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import find_project_root  # noqa: E402

REPO_ROOT = find_project_root()
PLAN = REPO_ROOT / ".agentile" / "INDEX" / "RENAME_PLAN.tsv"


def run_git_mv(old: str, new: str) -> tuple[bool, str]:
    cmd = ["git", "-C", str(REPO_ROOT), "mv", old, new]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode == 0:
        return True, ""
    return False, (proc.stderr or proc.stdout).strip()


def main() -> int:
    if not PLAN.exists():
        print(f"ERROR: rename plan not found at {PLAN}", file=sys.stderr)
        print("       Run `scripts/index/build_rename_plan.py` first.", file=sys.stderr)
        return 1

    moved = skipped = failed = 0
    failures: list[tuple[str, str, str]] = []

    with PLAN.open(newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            if row["rename_needed"] != "Y":
                skipped += 1
                continue
            old = row["old_path"]
            new = row["new_path"]
            old_full = REPO_ROOT / old
            new_full = REPO_ROOT / new

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

            ok, err = run_git_mv(old, new)
            if ok:
                moved += 1
            else:
                failed += 1
                failures.append((old, new, err))

    print(f"Renamed: {moved}")
    print(f"Skipped: {skipped}")
    print(f"Failed:  {failed}")
    for old, new, err in failures[:20]:
        print(f"  ! {old} -> {new}  ({err})")
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
