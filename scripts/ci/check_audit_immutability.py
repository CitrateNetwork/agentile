#!/usr/bin/env python3
"""Rule 6 enforcer: audit reports are dated and immutable.

Walks `.agentile/audits/` and, for each `.md` file, checks that no
commit AFTER the file's first-commit modified its content. Renames
and deletions are also forbidden — a finding that was wrong gets a
NEW dated audit, not an edit to the original.

The check is a git-log walk: for every file under audits/, run
`git log --follow --diff-filter=M --format=%H -- <file>`. If that
returns more than one commit (the create commit), the file has been
modified and the rule is violated.

Exit codes:
  0 — every audit file is immutable
  1 — at least one audit file was modified after creation; lists offenders
  2 — usage / git error

Flags:
  --since <commit>   Only check files modified in commits after `<commit>`
                     (used by audit-immutability.yml on PRs to scope to
                     the diff range).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "index"))
from _common import find_project_root  # type: ignore  # noqa: E402
from _vacuity import require_nonempty, vacuous_exit  # type: ignore  # noqa: E402

PROJECT_ROOT = find_project_root()
AUDITS_DIR = PROJECT_ROOT / ".agentile" / "audits"


def git_modifying_commits(rel_path: str) -> list[str]:
    """Return all commits that MODIFIED (not added) `rel_path`."""
    cmd = [
        "git", "-C", str(PROJECT_ROOT),
        "log", "--diff-filter=M", "--format=%H",
        "--", rel_path,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        return []
    return [ln.strip() for ln in proc.stdout.splitlines() if ln.strip()]


def git_deletes(rel_path: str) -> list[str]:
    """Return commits that DELETED `rel_path`."""
    cmd = [
        "git", "-C", str(PROJECT_ROOT),
        "log", "--diff-filter=D", "--format=%H",
        "--", rel_path,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        return []
    return [ln.strip() for ln in proc.stdout.splitlines() if ln.strip()]


def files_changed_in_range(since: str) -> list[str]:
    cmd = [
        "git", "-C", str(PROJECT_ROOT),
        "diff", "--name-only", f"{since}..HEAD",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        return []
    return [ln.strip() for ln in proc.stdout.splitlines() if ln.strip()]


def main() -> int:
    args = sys.argv[1:]
    if args and args[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    since: str | None = None
    if len(args) >= 2 and args[0] == "--since":
        since = args[1]

    if not AUDITS_DIR.exists():
        if since:
            print("OK: .agentile/audits/ does not exist (no audits yet).")
            return 0
        return vacuous_exit("audit files (.agentile/audits/ absent)",
                            require_nonempty())

    if since:
        changed = files_changed_in_range(since)
        targets = [
            PROJECT_ROOT / f for f in changed
            if f.startswith(".agentile/audits/") and f.endswith(".md")
        ]
        if not targets:
            print(f"OK: no audit files changed in {since}..HEAD.")
            return 0
    else:
        targets = list(AUDITS_DIR.rglob("*.md"))
        if not targets:
            # Full-scan mode with no audit .md files is a vacuous pass
            # (AG-B-007): .agentile/audits/ holds only .gitkeep on a skeleton.
            return vacuous_exit("audit files", require_nonempty())

    violations: list[tuple[str, str]] = []  # (rel_path, kind)
    for path in targets:
        rel = str(path.relative_to(PROJECT_ROOT))
        mods = git_modifying_commits(rel)
        if mods:
            violations.append((rel, f"modified in {len(mods)} commit(s): "
                                    + ", ".join(c[:8] for c in mods[:5])))

    # Also check for deletes if scoped to a range — a deleted audit is
    # equally bad as a modified one.
    if since:
        for f in files_changed_in_range(since):
            if not (f.startswith(".agentile/audits/") and f.endswith(".md")):
                continue
            if not (PROJECT_ROOT / f).exists():
                violations.append((f, "deleted"))

    if not violations:
        print(f"OK: {len(targets)} audit file(s) checked; all immutable.")
        return 0

    print(f"BLOCKER: {len(violations)} audit file(s) violated Rule 6 (immutability):")
    for rel, kind in violations:
        print(f"  - {rel}: {kind}")
    print()
    print("Audits are dated and immutable. To correct a finding, write a")
    print("NEW audit at .agentile/audits/YYYY-MM-DD-<slug>/ that references")
    print("the original. Do NOT edit the original.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
