#!/usr/bin/env python3
"""Backfill Rule-12 frontmatter on .agentile/ docs that lack it.

For every .md under .agentile/ (excluding .agentile/INDEX/ which is
auto-generated) that does NOT begin with a `---` frontmatter block,
prepend:

    ---
    created: <git first-commit time, UTC, ISO-8601>
    branch: main
    author: historical-import
    status: archived
    ---
    <!-- Backfilled <timestamp>: original written before Rule-12. -->

Idempotent: files that already have frontmatter are skipped.
"""
from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import find_project_root  # noqa: E402

REPO_ROOT = find_project_root()
AGENTILE = REPO_ROOT / ".agentile"
EXCLUDE_DIRS = {AGENTILE / "INDEX"}
NOW_UTC = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def has_frontmatter(text: str) -> bool:
    return text.startswith("---") and text.find("\n---", 3) != -1


def git_first_commit_iso(rel: str) -> str:
    cmd = [
        "git",
        "-C",
        str(REPO_ROOT),
        "log",
        "--diff-filter=A",
        "--follow",
        "--format=%aI",
        "--",
        rel,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    lines = [ln for ln in proc.stdout.splitlines() if ln.strip()]
    if not lines:
        return ""
    raw = lines[-1].strip()
    try:
        dt = datetime.fromisoformat(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return ""


def is_excluded(path: Path) -> bool:
    for excl in EXCLUDE_DIRS:
        try:
            path.relative_to(excl)
            return True
        except ValueError:
            continue
    return False


def main() -> int:
    targets: list[Path] = []
    for path in AGENTILE.rglob("*.md"):
        if is_excluded(path):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if has_frontmatter(text):
            continue
        targets.append(path)

    print(f"Files without frontmatter: {len(targets)}", file=sys.stderr)

    written = blocked = 0
    for path in sorted(targets):
        rel = str(path.relative_to(REPO_ROOT))
        created = git_first_commit_iso(rel)
        ts_source = "git first-commit"
        if not created:
            try:
                mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
                created = mtime.strftime("%Y-%m-%dT%H:%M:%SZ")
                ts_source = "filesystem mtime (file is untracked)"
            except OSError:
                blocked += 1
                print(f"  BLOCKED (no git, no mtime): {rel}", file=sys.stderr)
                continue

        original = path.read_text(encoding="utf-8", errors="replace")
        block = (
            "---\n"
            f"created: {created}\n"
            "branch: main\n"
            "author: historical-import\n"
            "status: archived\n"
            "---\n"
            f"<!-- Backfilled {NOW_UTC} from {ts_source}: original written before Rule-12. -->\n"
        )
        new = block + original.lstrip("\n")
        path.write_text(new, encoding="utf-8")
        written += 1

    print(f"Backfilled: {written}")
    print(f"Blocked:    {blocked}")
    return 0 if blocked == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
