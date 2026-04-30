#!/usr/bin/env python3
"""Rewrite cross-references to renamed sprint folders across .agentile/.

For each {old_slug → new_slug} pair in SPRINT_RENAME_PLAN.tsv (rows where
rename_needed == Y), replace every occurrence of `old_slug` with `new_slug`
in every .md under .agentile/ — EXCEPT when the slug is already preceded
by a YYYY-MM-DD- prefix (idempotency guard, so rerunning is safe).

The plan's SPRINT_RENAME_PLAN.{md,tsv} files are excluded from the rewrite
— those are the historical record of what the rename was.

Run AFTER `apply_sprint_rename_plan.py` has done the actual `git mv`s.
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import find_project_root  # noqa: E402

REPO_ROOT = find_project_root()
AGENTILE = REPO_ROOT / ".agentile"
PLAN = AGENTILE / "INDEX" / "SPRINT_RENAME_PLAN.tsv"

SKIP_PATHS = {
    AGENTILE / "INDEX" / "SPRINT_RENAME_PLAN.md",
    AGENTILE / "INDEX" / "SPRINT_RENAME_PLAN.tsv",
}


def load_pairs() -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    with PLAN.open(newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            if row.get("rename_needed") != "Y":
                continue
            old = Path(row["old_path"]).name
            new = Path(row["new_path"]).name
            if old and new and old != new:
                pairs.append((old, new))
    # Longest-first so longer slugs match before shorter ones with overlap.
    pairs.sort(key=lambda p: -len(p[0]))
    return pairs


def make_pattern(old_slug: str) -> re.Pattern[str]:
    # Negative lookbehind: don't match if already prefixed with YYYY-MM-DD-.
    return re.compile(rf"(?<!\d{{4}}-\d{{2}}-\d{{2}}-)" + re.escape(old_slug))


def main() -> int:
    if not PLAN.exists():
        print(f"ERROR: plan not found at {PLAN}", file=sys.stderr)
        print("       Run `scripts/index/build_sprint_rename_plan.py` first.", file=sys.stderr)
        return 1

    pairs = load_pairs()
    print(f"Loaded {len(pairs)} rename pairs", file=sys.stderr)

    if not pairs:
        print("No rename pairs to apply.")
        return 0

    patterns = [(make_pattern(o), n, o) for o, n in pairs]

    files_changed = 0
    total_subs = 0

    for path in AGENTILE.rglob("*.md"):
        if path in SKIP_PATHS:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        new_text = text
        local_subs = 0
        for pat, new, _ in patterns:
            new_text, n = pat.subn(new, new_text)
            local_subs += n
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            files_changed += 1
            total_subs += local_subs

    print(f"Files modified:        {files_changed}")
    print(f"Substitutions applied: {total_subs}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
