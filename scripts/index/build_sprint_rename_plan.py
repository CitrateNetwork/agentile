#!/usr/bin/env python3
"""Generate a chronological rename plan for sprint folders.

For each sprint directory under
.agentile/sprints/{active,completed,archived,backlog}:

  - Determine kickoff timestamp = SPRINT.md frontmatter `created` if present,
    else git-log first-commit time across all files in the sprint dir.
  - Propose new dir name: `<state>/YYYY-MM-DD-<original-name>/`

Also computes cross-reference counts: how many .md files in .agentile/
mention the old sprint dir name, so the project owner can see the rewrite
blast radius before approving.

Read-only: emits .agentile/INDEX/SPRINT_RENAME_PLAN.{md,tsv}. Does NOT
rename or rewrite anything. The TSV is consumed by
`apply_sprint_rename_plan.py` and `rewrite_sprint_xrefs.py`.
"""
from __future__ import annotations

import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import find_project_root, parse_frontmatter, to_utc_iso  # noqa: E402

REPO_ROOT = find_project_root()
AGENTILE = REPO_ROOT / ".agentile"
SPRINTS = AGENTILE / "sprints"
OUT = AGENTILE / "INDEX"
OUT.mkdir(exist_ok=True)

STATES = ("active", "completed", "archived", "backlog")


def git_first_commit_time_dir(rel_dir: str) -> datetime | None:
    cmd = [
        "git",
        "-C",
        str(REPO_ROOT),
        "log",
        "--diff-filter=A",
        "--format=%aI",
        "--",
        rel_dir,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    lines = [ln for ln in proc.stdout.splitlines() if ln.strip()]
    if not lines:
        return None
    return to_utc_iso(lines[-1])


def count_xref(old_basename: str, exclude_path: Path) -> int:
    """Count .md files under .agentile/ that reference `old_basename`,
    EXCLUDING files inside `exclude_path` (the sprint folder itself).
    Used to size the cross-reference rewrite blast radius."""
    if not old_basename:
        return 0
    cmd = ["grep", "-rl", "--include=*.md", old_basename, str(AGENTILE)]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode > 1:
        return 0
    files = [ln for ln in proc.stdout.splitlines() if ln.strip()]
    n = 0
    for f in files:
        try:
            Path(f).relative_to(exclude_path)
        except ValueError:
            n += 1
    return n


def collect() -> list[dict]:
    rows: list[dict] = []
    if not SPRINTS.exists():
        return rows
    for state in STATES:
        state_dir = SPRINTS / state
        if not state_dir.exists():
            continue
        for sprint_dir in sorted(state_dir.iterdir()):
            if not sprint_dir.is_dir():
                continue
            old_name = sprint_dir.name
            rel_dir = str(sprint_dir.relative_to(REPO_ROOT))

            # Already prefixed?
            if re.match(r"^\d{4}-\d{2}-\d{2}-", old_name):
                rows.append(
                    {
                        "state": state,
                        "old_path": rel_dir,
                        "old_name": old_name,
                        "best_iso": "",
                        "ts_source": "already-prefixed",
                        "new_name": old_name,
                        "new_path": rel_dir,
                        "rename_needed": "N",
                        "xref_count": 0,
                    }
                )
                continue

            # Kickoff date: SPRINT.md frontmatter, else git
            best: datetime | None = None
            source = "unknown"
            sprint_md = sprint_dir / "SPRINT.md"
            if sprint_md.exists():
                fm = parse_frontmatter(sprint_md.read_text(encoding="utf-8", errors="replace"))
                d = to_utc_iso(fm.get("created", ""))
                if d:
                    best, source = d, "frontmatter"
            if best is None:
                d = git_first_commit_time_dir(rel_dir)
                if d:
                    best, source = d, "git"

            if best is None:
                rows.append(
                    {
                        "state": state,
                        "old_path": rel_dir,
                        "old_name": old_name,
                        "best_iso": "",
                        "ts_source": source,
                        "new_name": "",
                        "new_path": "",
                        "rename_needed": "BLOCKED",
                        "xref_count": count_xref(old_name, sprint_dir),
                    }
                )
                continue

            new_name = f"{best.strftime('%Y-%m-%d')}-{old_name}"
            new_path = str((state_dir / new_name).relative_to(REPO_ROOT))
            xref = count_xref(old_name, sprint_dir)
            rows.append(
                {
                    "state": state,
                    "old_path": rel_dir,
                    "old_name": old_name,
                    "best_iso": best.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "ts_source": source,
                    "new_name": new_name,
                    "new_path": new_path,
                    "rename_needed": "Y",
                    "xref_count": xref,
                }
            )
    return rows


def emit(rows: list[dict]) -> None:
    cols = [
        "state",
        "rename_needed",
        "ts_source",
        "best_iso",
        "xref_count",
        "old_path",
        "new_path",
    ]
    tsv = OUT / "SPRINT_RENAME_PLAN.tsv"
    with tsv.open("w", encoding="utf-8") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows:
            f.write("\t".join(str(r.get(c, "")) for c in cols) + "\n")

    md = OUT / "SPRINT_RENAME_PLAN.md"
    with md.open("w", encoding="utf-8") as f:
        f.write("# Sprint folder rename plan — chronological prefix\n\n")
        f.write(
            "Generated by `scripts/index/build_sprint_rename_plan.py`. "
            "Read-only — nothing renamed until the project owner runs "
            "`apply_sprint_rename_plan.py` followed by "
            "`rewrite_sprint_xrefs.py`.\n\n"
        )
        n = len(rows)
        n_rename = sum(1 for r in rows if r["rename_needed"] == "Y")
        n_clean = sum(1 for r in rows if r["rename_needed"] == "N")
        n_blocked = sum(1 for r in rows if r["rename_needed"] == "BLOCKED")
        n_xref = sum(int(r["xref_count"]) for r in rows if r["rename_needed"] == "Y")
        f.write(f"Total sprint folders: **{n}**  \n")
        f.write(f"Will be renamed: **{n_rename}**  \n")
        f.write(f"Already prefixed: **{n_clean}**  \n")
        f.write(f"Blocked (no usable timestamp): **{n_blocked}**  \n")
        f.write(f"Cross-reference rewrites needed across .agentile/: **{n_xref}** files  \n\n")
        f.write(
            "Pattern: `<state>/YYYY-MM-DD-<original-folder-name>/` — date is the "
            "kickoff (SPRINT.md frontmatter `created`, or git first-commit of any "
            "file in the dir).\n\n"
        )
        if not rows:
            f.write("_No sprint folders found under `.agentile/sprints/`._\n")
            return
        for state in STATES:
            state_rows = sorted(
                (r for r in rows if r["state"] == state),
                key=lambda r: r["best_iso"] or "9999",
            )
            if not state_rows:
                continue
            f.write(f"## {state} ({len(state_rows)})\n\n")
            f.write("| Action | Source | Kickoff | Xrefs | Old → New |\n")
            f.write("|---|---|---|---|---|\n")
            for r in state_rows:
                action = {"Y": "RENAME", "N": "keep", "BLOCKED": "BLOCKED"}[r["rename_needed"]]
                f.write(
                    f"| {action} | {r['ts_source']} | {r['best_iso']} | "
                    f"{r['xref_count']} | `{r['old_name']}` → `{r['new_name']}` |\n"
                )
            f.write("\n")
    print(f"Wrote {md.relative_to(REPO_ROOT)}")
    print(f"Wrote {tsv.relative_to(REPO_ROOT)}")


def main() -> int:
    rows = collect()
    emit(rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
