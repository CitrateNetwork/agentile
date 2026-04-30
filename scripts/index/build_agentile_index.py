#!/usr/bin/env python3
"""Build a chronological index of every .md file under .agentile/.

For each file:
  - Parse Rule-12 frontmatter (created / branch / author / sprint / status)
  - Look up git first-commit time + sha (one batched git log pass)
  - Categorize by path heuristic
  - Compute best_timestamp = frontmatter.created if present else git first-commit time

Outputs (under .agentile/INDEX/):
  - INDEX_CHRONOLOGICAL.md  — table sorted oldest → newest, all categories interleaved
  - INDEX_BY_CATEGORY.md    — same data grouped by category, then chronological inside
  - INDEX_RAW.tsv           — machine-readable for downstream analysis
  - NAMING_INCONSISTENCIES.md — files missing frontmatter, divergent dates, name patterns

Read-only on the source files. Does not rename or modify any document.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

# Allow running as `./scripts/index/build_agentile_index.py` without setting PYTHONPATH.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import find_project_root, parse_frontmatter  # noqa: E402

REPO_ROOT = find_project_root()
AGENTILE = REPO_ROOT / ".agentile"
OUT = AGENTILE / "INDEX"
OUT.mkdir(exist_ok=True)


def categorize(rel_path: str) -> str:
    """Heuristic from the path string. `rel_path` is repo-relative; we strip
    the `.agentile/` prefix so the rules table reads naturally.

    Categories include both common shapes (journals, sprints, audits) and
    project-specific shapes (quorum, zooids, ceremonies). Categories that
    don't exist in a particular project are simply unused — the heuristic
    is additive."""
    p = rel_path
    if p.startswith(".agentile/"):
        p = p[len(".agentile/"):]
    rules = [
        ("docs/journals/", "journal"),
        ("docs/essays/", "essay"),
        ("docs/case_studies/", "case_study"),
        ("docs/reports/", "report"),
        ("docs/guides/", "guide"),
        ("docs/reference/", "reference_doc"),
        ("docs/methodology/", "methodology"),
        ("docs/", "doc"),
        ("audits/", "audit"),
        ("sprints/active/", "sprint_active"),
        ("sprints/completed/", "sprint_completed"),
        ("sprints/archived/", "sprint_archived"),
        ("sprints/backlog/", "sprint_backlog"),
        ("sprints/", "sprint_governance"),
        ("planset/adr/", "planset_adr"),
        ("planset/", "planset_other"),
        ("quorum/workitems/", "quorum_workitem"),
        ("quorum/tracks/", "quorum_track"),
        ("quorum/", "quorum_governance"),
        ("rules/", "rule"),
        ("workflows/", "workflow"),
        ("templates/", "template"),
        ("formal/specs/", "spec"),
        ("formal/", "formal_governance"),
        ("launch/", "launch"),
        ("zooids/", "zooid"),
        ("teamwork/", "teamwork"),
        ("compliance/", "compliance"),
        ("ceremonies/", "ceremony"),
        ("coverage/", "coverage"),
        ("source_of_truth/", "source_of_truth"),
        ("onboarding/", "onboarding"),
        ("INDEX/", "index_output"),
    ]
    for prefix, cat in rules:
        if p.startswith(prefix):
            return cat
    # After stripping `.agentile/`, a bare filename like `CONFIG.md` is
    # top-level governance (no subdirectory).
    if "/" not in p:
        return "root_governance"
    return "other"


def git_first_commit_map(scope_relative: str) -> dict[str, tuple[str, str]]:
    """Return {repo-relative-path: (first_commit_iso_time, first_commit_sha)}.

    One git log call with --diff-filter=A --name-only and consume the output
    stream. That's O(commits-touching-scope) instead of O(files).

    Returns {} if the scope has no git history (e.g. uncommitted skeleton).
    """
    cmd = [
        "git",
        "-C",
        str(REPO_ROOT),
        "log",
        "--diff-filter=A",
        "--name-only",
        "--format=COMMIT %H %aI",
        "--",
        scope_relative,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        return {}
    out: dict[str, tuple[str, str]] = {}
    cur_sha, cur_time = "", ""
    for raw in proc.stdout.splitlines():
        if raw.startswith("COMMIT "):
            parts = raw.split()
            cur_sha = parts[1]
            cur_time = parts[2]
        elif raw.strip():
            out[raw] = (cur_time, cur_sha)
    return out


def main() -> int:
    md_files = sorted(
        str(p.relative_to(REPO_ROOT))
        for p in AGENTILE.rglob("*.md")
        if "INDEX/" not in str(p.relative_to(REPO_ROOT))
    )
    print(f"Scanning {len(md_files)} .md files under .agentile/", file=sys.stderr)

    git_map = git_first_commit_map(".agentile")
    print(f"Got git first-commit info for {len(git_map)} paths", file=sys.stderr)

    rows: list[dict[str, str]] = []
    for rel in md_files:
        full = REPO_ROOT / rel
        try:
            text = full.read_text(encoding="utf-8", errors="replace")
        except Exception as e:  # noqa: BLE001
            print(f"  read-error {rel}: {e}", file=sys.stderr)
            text = ""
        fm = parse_frontmatter(text)
        first_time, first_sha = git_map.get(rel, ("", ""))
        best = fm.get("created") or first_time
        best_short = best[:19] if best else ""
        rows.append(
            {
                "path": rel,
                "filename": os.path.basename(rel),
                "category": categorize(rel),
                "fm_created": fm.get("created", ""),
                "fm_branch": fm.get("branch", ""),
                "fm_author": fm.get("author", ""),
                "fm_sprint": fm.get("sprint", ""),
                "fm_status": fm.get("status", ""),
                "git_first_time": first_time,
                "git_first_sha": first_sha[:8] if first_sha else "",
                "best_timestamp": best,
                "best_short": best_short,
                "has_frontmatter": "Y" if fm else "N",
                "ts_source": "frontmatter" if fm.get("created") else ("git" if first_time else "unknown"),
            }
        )

    rows.sort(key=lambda r: (r["best_timestamp"] or "9999"))

    # === TSV (machine-readable) ===
    tsv_path = OUT / "INDEX_RAW.tsv"
    cols = [
        "best_short",
        "ts_source",
        "category",
        "has_frontmatter",
        "fm_branch",
        "fm_author",
        "fm_status",
        "git_first_sha",
        "path",
    ]
    with tsv_path.open("w", encoding="utf-8") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows:
            f.write("\t".join(r.get(c, "") for c in cols) + "\n")

    # === Chronological Markdown ===
    chrono_path = OUT / "INDEX_CHRONOLOGICAL.md"
    with chrono_path.open("w", encoding="utf-8") as f:
        f.write("# .agentile/ Chronological Index\n\n")
        f.write(f"Generated: {os.popen('date -u +%Y-%m-%dT%H:%M:%SZ').read().strip()}  \n")
        f.write(f"Total documents: **{len(rows)}**  \n")
        with_fm = sum(1 for r in rows if r["has_frontmatter"] == "Y")
        f.write(f"With Rule-12 frontmatter: **{with_fm}**  \n")
        f.write(f"Without frontmatter (using git first-commit time): **{len(rows) - with_fm}**\n\n")
        f.write(
            "Sorted by `best_timestamp` = frontmatter `created` field if present, else "
            "git first-commit time.  \n`ts_source` column tells you which.\n\n"
        )
        if not rows:
            f.write("_No `.md` files found under `.agentile/` yet._\n")
        else:
            f.write("| Best timestamp | Src | Category | Path | Branch | Status |\n")
            f.write("|---|---|---|---|---|---|\n")
            for r in rows:
                f.write(
                    f"| {r['best_short']} | {r['ts_source']} | {r['category']} | "
                    f"`{r['path']}` | {r['fm_branch']} | {r['fm_status']} |\n"
                )

    # === By-category Markdown ===
    cat_path = OUT / "INDEX_BY_CATEGORY.md"
    by_cat: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_cat[r["category"]].append(r)
    with cat_path.open("w", encoding="utf-8") as f:
        f.write("# .agentile/ Index by Category\n\n")
        f.write("Within each category, sorted oldest → newest by `best_timestamp`.\n\n")
        if not by_cat:
            f.write("_No categories yet — `.agentile/` is empty of .md files._\n")
        for cat in sorted(by_cat.keys()):
            entries = by_cat[cat]
            entries.sort(key=lambda r: (r["best_timestamp"] or "9999"))
            f.write(f"## {cat} ({len(entries)})\n\n")
            f.write("| Best timestamp | Src | Path | Status |\n")
            f.write("|---|---|---|---|\n")
            for r in entries:
                f.write(
                    f"| {r['best_short']} | {r['ts_source']} | "
                    f"`{r['path']}` | {r['fm_status']} |\n"
                )
            f.write("\n")

    # === Naming Inconsistencies ===
    issues_path = OUT / "NAMING_INCONSISTENCIES.md"
    with issues_path.open("w", encoding="utf-8") as f:
        f.write("# .agentile/ Naming Inconsistencies\n\n")

        no_fm = [r for r in rows if r["has_frontmatter"] == "N"]
        f.write(f"## Files without Rule-12 frontmatter ({len(no_fm)})\n\n")
        f.write("These need backfilled `created` from git first-commit time. "
                "Run `scripts/index/backfill_frontmatter.py`.\n\n")
        no_fm_by_cat: dict[str, list[dict]] = defaultdict(list)
        for r in no_fm:
            no_fm_by_cat[r["category"]].append(r)
        for cat in sorted(no_fm_by_cat.keys()):
            f.write(f"### {cat} ({len(no_fm_by_cat[cat])})\n\n")
            for r in sorted(no_fm_by_cat[cat], key=lambda r: r["best_timestamp"] or "9999"):
                f.write(f"- `{r['path']}` — proposed `created: {r['best_timestamp']}`\n")
            f.write("\n")

        f.write("\n## Sprint folder naming patterns\n\n")
        sprint_dirs = sorted({
            os.path.dirname(r["path"]).split("/", 2)[-1]
            for r in rows
            if r["category"].startswith("sprint_")
        })
        if not sprint_dirs:
            f.write("_(none yet)_\n")
        for d in sprint_dirs:
            f.write(f"- `{d}`\n")

        f.write("\n## Audit folder naming patterns\n\n")
        audit_dirs = sorted({
            "/".join(r["path"].split("/")[:3])
            for r in rows
            if r["category"] == "audit"
        })
        if not audit_dirs:
            f.write("_(none yet)_\n")
        for d in audit_dirs[:60]:
            f.write(f"- `{d}`\n")
        if len(audit_dirs) > 60:
            f.write(f"\n_… and {len(audit_dirs) - 60} more (full list in INDEX_RAW.tsv)._\n")

        f.write("\n## Planset folder naming patterns\n\n")
        planset_dirs = sorted({
            "/".join(r["path"].split("/")[:3])
            for r in rows
            if r["category"].startswith("planset_")
        })
        if not planset_dirs:
            f.write("_(none yet)_\n")
        for d in planset_dirs:
            f.write(f"- `{d}`\n")

        f.write("\n## Journals/essays missing YYYY-MM-DD chronological prefix\n\n")
        no_prefix = [
            r for r in rows
            if r["category"] in ("journal", "essay", "case_study")
            and not re.match(r"^\d{4}-\d{2}-\d{2}", r["filename"])
        ]
        f.write(f"Total: {len(no_prefix)}\n\n")
        for r in no_prefix[:80]:
            f.write(f"- `{r['path']}` — first commit `{r['best_timestamp']}`\n")
        if len(no_prefix) > 80:
            f.write(f"\n_… and {len(no_prefix) - 80} more._\n")

    print(f"Wrote: {chrono_path.relative_to(REPO_ROOT)}")
    print(f"Wrote: {cat_path.relative_to(REPO_ROOT)}")
    print(f"Wrote: {tsv_path.relative_to(REPO_ROOT)}")
    print(f"Wrote: {issues_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
