#!/usr/bin/env python3
"""Ratchet 4: frontmatter coverage.

Walks `.agentile/` and counts `.md` files with vs. without the Rule-12
frontmatter block. Asserts that the (covered / total) fraction has
NOT decreased relative to the baseline.

After the initial backfill the goal is 100% — once reached, regression
to <100% blocks merge.

Exit codes:
  0 — coverage at or above baseline
  1 — coverage decreased; lists the files missing frontmatter
  2 — usage / unexpected error

Flags:
  --files <path>...   Only check these files (used by lint-frontmatter.yml
                      to scope checks to changed files in a PR).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "index"))
from _common import find_project_root  # type: ignore  # noqa: E402
from _baseline import load_baseline  # type: ignore  # noqa: E402

PROJECT_ROOT = find_project_root()
AGENTILE = PROJECT_ROOT / ".agentile"


def has_frontmatter(text: str) -> bool:
    return text.startswith("---") and text.find("\n---", 3) != -1


def collect_targets(explicit_files: list[str]) -> list[Path]:
    if explicit_files:
        out = []
        for f in explicit_files:
            p = Path(f).resolve() if Path(f).is_absolute() else (PROJECT_ROOT / f).resolve()
            if p.suffix == ".md" and AGENTILE in p.parents:
                out.append(p)
        return out
    return [
        p for p in AGENTILE.rglob("*.md")
        if "INDEX/" not in str(p.relative_to(PROJECT_ROOT))
    ]


def main() -> int:
    args = sys.argv[1:]
    explicit_files: list[str] = []
    if args and args[0] == "--files":
        explicit_files = args[1:]
    elif args and args[0] in ("-h", "--help"):
        print(__doc__)
        return 0

    targets = collect_targets(explicit_files)
    total = len(targets)
    if total == 0:
        # Nothing to check. CI scoping (--files) may legitimately produce
        # an empty set when a PR doesn't touch any .md under .agentile/.
        print("OK: no .md files under .agentile/ to check.")
        return 0

    missing: list[Path] = []
    for path in targets:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            missing.append(path)
            continue
        if not has_frontmatter(text):
            missing.append(path)

    covered = total - len(missing)
    fraction = covered / total

    baseline = load_baseline().get("frontmatter", {"covered": 0, "total": 0})
    base_total = baseline.get("total", 0)
    base_covered = baseline.get("covered", 0)
    base_fraction = base_covered / base_total if base_total else 1.0

    print(f"Frontmatter coverage: {covered}/{total} ({fraction*100:.1f}%)")
    print(f"Baseline:             {base_covered}/{base_total} ({base_fraction*100:.1f}%)")

    if missing:
        print()
        print("Files missing Rule-12 frontmatter:")
        for p in sorted(missing):
            print(f"  - {p.relative_to(PROJECT_ROOT)}")

    # The ratchet: fraction must not decrease.
    # Use a tiny epsilon to permit floating-point equality.
    if fraction + 1e-9 < base_fraction:
        print()
        print("BLOCKER: frontmatter coverage decreased.")
        print("Add Rule-12 frontmatter to the files above before merging.")
        return 1

    # If the baseline was 100% and we now have any missing, also block.
    if base_fraction >= 0.999999 and missing:
        print()
        print("BLOCKER: project baseline is 100%; new docs must include "
              "Rule-12 frontmatter.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
