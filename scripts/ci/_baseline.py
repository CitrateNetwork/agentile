"""Shared baseline-loading helpers for the ratchet check scripts.

The four ratchets (test count, formal specs, CI tripwires, frontmatter
coverage) all read their day-zero numbers from
`.agentile/coverage/baseline.json`. Bootstrap (Phase 6) writes that
file from `BASELINE.md`; sprint close updates it. Scripts here parse
it.

If the baseline file is missing, the ratchets degrade gracefully:
they log a warning and treat the baseline as 0 (i.e. growth is good,
no regression possible). This is the right behavior for a freshly-
adopted skeleton that hasn't run bootstrap yet.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Allow running scripts directly: scripts/ci/foo.py finds the project root.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "index"))
from _common import find_project_root  # type: ignore  # noqa: E402

PROJECT_ROOT = find_project_root()
BASELINE_PATH = PROJECT_ROOT / ".agentile" / "coverage" / "baseline.json"


def load_baseline() -> dict:
    """Return the baseline JSON, or an empty default if missing.

    Default shape:
      {
        "tests":       {"count": 0, "command": ""},
        "specs":       {"count": 0, "command": ""},
        "tripwires":   {"count": 0, "command": ""},
        "frontmatter": {"covered": 0, "total": 0}
      }
    """
    default = {
        "tests": {"count": 0, "command": ""},
        "specs": {"count": 0, "command": ""},
        "tripwires": {"count": 0, "command": ""},
        "frontmatter": {"covered": 0, "total": 0},
    }
    if not BASELINE_PATH.exists():
        return default
    try:
        loaded = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"WARN: could not parse {BASELINE_PATH}: {e}", file=sys.stderr)
        return default
    # Merge into default so missing keys don't crash callers.
    for key, val in default.items():
        if key not in loaded:
            loaded[key] = val
        elif isinstance(val, dict):
            for subkey, subval in val.items():
                loaded[key].setdefault(subkey, subval)
    return loaded
