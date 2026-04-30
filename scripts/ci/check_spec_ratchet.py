#!/usr/bin/env python3
"""Ratchet 2: TLA+ spec count never decreases.

Counts `.tla` files under the project's spec directories:
  - `.agentile/formal/specs/` (the agentile-side mirror)
  - Any directory listed in baseline.specs.directories (project-specific
    source-of-truth paths, typically `specs/tla/` or similar)

Ignores TLC artifacts: `**/states/`, `*_TTrace_*.tla`.

Compares to baseline.specs.count from `.agentile/coverage/baseline.json`.

If the project has no specs (count == 0), the ratchet is a no-op until
the first spec lands. Once any spec exists, it cannot be removed
without an equivalent replacement.

Exit codes:
  0 — count >= baseline
  1 — count decreased; lists removed specs
  2 — usage / unexpected error
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "index"))
from _common import find_project_root  # type: ignore  # noqa: E402
from _baseline import load_baseline  # type: ignore  # noqa: E402

PROJECT_ROOT = find_project_root()

DEFAULT_SPEC_DIRS = [".agentile/formal/specs"]
TTRACE_RE = re.compile(r"_TTrace_\d+\.tla$")


def collect_specs(dirs: list[str]) -> list[Path]:
    out: list[Path] = []
    for d in dirs:
        root = PROJECT_ROOT / d
        if not root.exists():
            continue
        for p in root.rglob("*.tla"):
            rel = str(p.relative_to(PROJECT_ROOT))
            if "/states/" in rel or TTRACE_RE.search(rel):
                continue
            out.append(p)
    return out


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        return 0

    baseline = load_baseline().get("specs", {})
    base_count = int(baseline.get("count", 0) or 0)
    dirs = baseline.get("directories", DEFAULT_SPEC_DIRS)

    specs = collect_specs(dirs)
    current = len(specs)

    print(f"TLA+ spec count: {current}")
    print(f"Baseline:        {base_count}")
    print(f"Searched: {', '.join(dirs)}")

    if current < base_count:
        print()
        print(f"BLOCKER: spec count decreased ({base_count} -> {current}).")
        print("A spec can only be removed if a corrected replacement lands")
        print("in the same commit (Rule 10). See .agentile/formal/README.md.")
        return 1
    if current > base_count:
        print(f"Spec count grew by {current - base_count} (good).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
