#!/usr/bin/env python3
"""Ratchet 1: test count never decreases.

Reads `.agentile/coverage/baseline.json`. If the file is missing or
the test command is empty, the ratchet is a no-op (returns 0 with a
warning). This is the right behavior for a freshly-adopted skeleton
where the project hasn't run bootstrap.sh yet.

Otherwise:
  - Runs the canonical test command from baseline.tests.command
  - Compares the resulting count to baseline.tests.count
  - Asserts current >= baseline

Exit codes:
  0 — count is at or above baseline (or baseline is unset)
  1 — count decreased; print delta
  2 — usage / exec error
"""
from __future__ import annotations

import shlex
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "index"))
from _common import find_project_root  # type: ignore  # noqa: E402
from _baseline import load_baseline  # type: ignore  # noqa: E402
from _vacuity import require_nonempty, vacuous_exit  # type: ignore  # noqa: E402

PROJECT_ROOT = find_project_root()


def run_test_count(command: str) -> int | None:
    """Execute the canonical test-count command. Returns the integer it
    prints to stdout (last numeric token), or None on failure."""
    if not command.strip():
        return None
    try:
        proc = subprocess.run(
            ["bash", "-c", command],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=600,
        )
    except subprocess.TimeoutExpired:
        print("ERROR: test count command timed out after 600s.", file=sys.stderr)
        return None
    if proc.returncode != 0:
        print("ERROR: test count command exited with non-zero status:", file=sys.stderr)
        print(f"  command: {command}", file=sys.stderr)
        print(f"  stderr:  {proc.stderr.strip()[:500]}", file=sys.stderr)
        return None
    # Parse last numeric token from stdout.
    tokens = proc.stdout.split()
    for token in reversed(tokens):
        try:
            return int(token.replace(",", ""))
        except ValueError:
            continue
    print("ERROR: could not parse a count from command output:", file=sys.stderr)
    print(proc.stdout[:500], file=sys.stderr)
    return None


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        return 0

    baseline = load_baseline().get("tests", {})
    command = baseline.get("command", "")
    base_count = int(baseline.get("count", 0) or 0)

    if not command:
        print("WARN: no test command set in .agentile/coverage/baseline.json.")
        print("      Test ratchet is a no-op until bootstrap.sh fills it in.")
        return vacuous_exit("tests (no test command configured)",
                            require_nonempty())

    print(f"Running test count command: {shlex.quote(command)}")
    current = run_test_count(command)
    if current is None:
        return 2
    print(f"Current test count: {current}")
    print(f"Baseline:           {base_count}")

    if current < base_count:
        delta = base_count - current
        print()
        print(f"BLOCKER: test count decreased by {delta} ({base_count} -> {current}).")
        print("Tests cannot be removed without an equivalent or better")
        print("replacement landing in the same commit (Rule 3).")
        return 1
    if current > base_count:
        delta = current - base_count
        print(f"Test count grew by {delta} (good — ratchet advanced).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
