"""Shared baseline-loading helpers for the ratchet check scripts.

The four ratchets (test count, formal specs, CI tripwires, frontmatter
coverage) all read their day-zero numbers from
`.agentile/coverage/baseline.json`. Bootstrap (Phase 6) writes that
file from `BASELINE.md`; sprint close updates it. Scripts here parse
it.

On pull requests, ``AGENTILE_BASELINE_REF`` points at the merge-base
commit. The ratchets read that committed baseline instead of trusting
the PR checkout, which could lower both the count and the baseline in
one change. If no baseline exists yet, the ratchets retain their
skeleton-friendly zero baseline.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

# Allow running scripts directly: scripts/ci/foo.py finds the project root.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "index"))
from _common import find_project_root  # type: ignore  # noqa: E402

PROJECT_ROOT = find_project_root()
BASELINE_PATH = PROJECT_ROOT / ".agentile" / "coverage" / "baseline.json"
BASELINE_RELATIVE = Path(".agentile") / "coverage" / "baseline.json"


def _default_baseline() -> dict:
    return {
        "tests": {"count": 0, "command": ""},
        "specs": {"count": 0, "command": ""},
        "tripwires": {"count": 0, "command": ""},
        "frontmatter": {"covered": 0, "total": 0},
    }


def _read_baseline(ref: str | None) -> str | None:
    """Read the baseline from ``ref`` or the checked-out file."""
    if ref:
        try:
            proc = subprocess.run(
                ["git", "show", f"{ref}:{BASELINE_RELATIVE}"],
                cwd=str(PROJECT_ROOT),
                capture_output=True,
                text=True,
                timeout=30,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            print(f"WARN: could not read baseline at {ref}: {exc}", file=sys.stderr)
            return None
        if proc.returncode != 0:
            print(
                f"WARN: no baseline at merge-base {ref}; using zero baseline.",
                file=sys.stderr,
            )
            return None
        return proc.stdout

    if not BASELINE_PATH.exists():
        return None
    try:
        return BASELINE_PATH.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"WARN: could not read {BASELINE_PATH}: {exc}", file=sys.stderr)
        return None


def load_baseline(ref: str | None = None) -> dict:
    """Return the baseline JSON from ``ref`` or the current checkout.

    Default shape:
      {
        "tests":       {"count": 0, "command": ""},
        "specs":       {"count": 0, "command": ""},
        "tripwires":   {"count": 0, "command": ""},
        "frontmatter": {"covered": 0, "total": 0}
      }
    """
    default = _default_baseline()
    ref = ref or os.environ.get("AGENTILE_BASELINE_REF", "").strip() or None
    raw = _read_baseline(ref)
    if raw is None:
        return default
    try:
        loaded = json.loads(raw)
    except json.JSONDecodeError as e:
        source = ref or str(BASELINE_PATH)
        print(f"WARN: could not parse baseline at {source}: {e}", file=sys.stderr)
        return default
    # Merge into default so missing keys don't crash callers.
    for key, val in default.items():
        if key not in loaded:
            loaded[key] = val
        elif isinstance(val, dict):
            for subkey, subval in val.items():
                loaded[key].setdefault(subkey, subval)
    return loaded
