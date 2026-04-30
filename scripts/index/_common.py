"""Shared helpers for the agentile indexer scripts.

Each indexer script imports `find_project_root`, `parse_frontmatter`, and
`to_utc_iso`. Centralizing them here means the scripts stay short and the
project-root convention has one definition.

The project root is the nearest ancestor of this script that contains a
`.agentile/` directory. This is robust against invocation from anywhere in
the project tree.
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

FRONTMATTER_KEYS = ("created", "branch", "author", "sprint", "status", "superseded_by")


def find_project_root() -> Path:
    """Walk upward from this file to find the directory containing .agentile/.

    Raises SystemExit if not found — the indexers cannot do anything useful
    outside an agentile-equipped project.
    """
    here = Path(__file__).resolve()
    for parent in [here] + list(here.parents):
        if (parent / ".agentile").is_dir():
            return parent
    sys.stderr.write(
        "ERROR: no .agentile/ directory found above this script. "
        "Indexer scripts only run inside an agentile-equipped project.\n"
    )
    raise SystemExit(2)


def parse_frontmatter(text: str) -> dict[str, str]:
    """Extract Rule-12 frontmatter fields. Returns {} if absent or malformed."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[3:end]
    out: dict[str, str] = {}
    for line in block.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            k, _, v = line.partition(":")
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k in FRONTMATTER_KEYS:
                out[k] = v
    return out


def to_utc_iso(s: str) -> datetime | None:
    """Parse a frontmatter `created` value or git ISO timestamp into UTC."""
    if not s:
        return None
    s = s.strip()
    try:
        if " " in s and "T" not in s:
            s = s.replace(" ", "T", 1)
        if s.endswith("Z"):
            dt = datetime.fromisoformat(s[:-1]).replace(tzinfo=timezone.utc)
        else:
            dt = datetime.fromisoformat(s)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            else:
                dt = dt.astimezone(timezone.utc)
        return dt
    except ValueError:
        return None
