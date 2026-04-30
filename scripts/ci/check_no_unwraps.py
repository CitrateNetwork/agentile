#!/usr/bin/env python3
"""Rule 5 enforcer: zero `.unwrap()` calls in production Rust code.

Default behavior (Rust):
  - Searches for `.unwrap()` calls under `src/` and `core/` directories
    project-wide (excluding `tests/`, `**/test_*.rs`, `**/*_test.rs`,
    `target/`).
  - Distinguishes `.unwrap()` from `.unwrap_or(...)`, `.unwrap_or_else(...)`,
    `.unwrap_or_default()` — only the bare form is a violation.

Adapter friendly:
  - The list of language adapters is read from `.agentile/coverage/
    baseline.json` under `unwraps.adapters` (a list of language names),
    or defaults to `["rust"]`.
  - Each adapter is a function below; non-default languages can be added
    by extending `ADAPTERS`.

Exit codes:
  0 — no violations
  1 — violations found; lists file:line for each
  2 — usage error

Flags:
  --files <path>...   Only check these files (used by tripwires.yml to
                      scope checks to changed files in a PR).

For the skeleton, this script is intentionally regex-based rather than
AST-based. AST checks are stronger but require a compiled language
toolchain in CI; regex catches the common cases and runs on any
substrate. The Semgrep rule `no-unwrap-in-prod.yaml` ships alongside
this script for projects that want AST-grade enforcement.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "index"))
from _common import find_project_root  # type: ignore  # noqa: E402

PROJECT_ROOT = find_project_root()

# Catches `.unwrap()` but NOT `.unwrap_or(...)`, `.unwrap_or_default()`,
# `.unwrap_or_else(...)`, `.unwrap_err()`. The trailing `(` and absence
# of `_` after `unwrap` is what distinguishes the bare form.
RUST_UNWRAP_RE = re.compile(r"\.unwrap\s*\(")

RUST_PROD_DIRS = ["src", "core", "node", "wallet", "cli", "faucet"]
RUST_EXCLUDE_PATTERNS = [
    re.compile(r"(?:^|/)tests/"),
    re.compile(r"(?:^|/)target/"),
    re.compile(r"(?:^|/)benches/"),
    re.compile(r"test_[^/]+\.rs$"),
    re.compile(r"_test\.rs$"),
    re.compile(r"_tests\.rs$"),
]


def is_excluded_rust(rel: str) -> bool:
    return any(p.search(rel) for p in RUST_EXCLUDE_PATTERNS)


def is_test_context(line_above: str | None, line: str) -> bool:
    """Heuristic: lines guarded by `#[cfg(test)]` or inside an explicit
    test attribute don't count. This is a soft check — the AST-level
    rule lives in Semgrep — but it cuts the most common false positives.
    """
    if line_above and "#[cfg(test)]" in line_above:
        return True
    if "// allow-unwrap:" in line:
        # Explicit pragma for justified exceptions. The reason is required
        # but not parsed here — code review enforces.
        return True
    return False


def check_rust(files: list[Path]) -> list[tuple[Path, int, str]]:
    violations: list[tuple[Path, int, str]] = []
    for path in files:
        rel = str(path.relative_to(PROJECT_ROOT))
        if is_excluded_rust(rel):
            continue
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for i, line in enumerate(lines):
            if not RUST_UNWRAP_RE.search(line):
                continue
            line_above = lines[i - 1] if i > 0 else None
            if is_test_context(line_above, line):
                continue
            violations.append((path, i + 1, line.strip()))
    return violations


def collect_rust_files(explicit_files: list[str]) -> list[Path]:
    if explicit_files:
        return [
            (Path(f).resolve() if Path(f).is_absolute() else (PROJECT_ROOT / f).resolve())
            for f in explicit_files
            if f.endswith(".rs")
        ]
    out: list[Path] = []
    for d in RUST_PROD_DIRS:
        root = PROJECT_ROOT / d
        if not root.exists():
            continue
        out.extend(root.rglob("*.rs"))
    return out


ADAPTERS = {
    "rust": (collect_rust_files, check_rust),
}


def main() -> int:
    args = sys.argv[1:]
    explicit_files: list[str] = []
    languages = ["rust"]

    i = 0
    while i < len(args):
        a = args[i]
        if a in ("-h", "--help"):
            print(__doc__)
            return 0
        if a == "--files":
            explicit_files = args[i + 1:]
            break
        if a == "--lang":
            languages = args[i + 1].split(",")
            i += 2
            continue
        i += 1

    total_violations = 0
    for lang in languages:
        if lang not in ADAPTERS:
            print(f"WARN: no adapter for language '{lang}'; skipping", file=sys.stderr)
            continue
        collect, check = ADAPTERS[lang]
        files = collect(explicit_files)
        violations = check(files)
        if violations:
            print(f"=== {lang}: {len(violations)} violations ===")
            for path, lineno, line in violations:
                print(f"  {path.relative_to(PROJECT_ROOT)}:{lineno}: {line}")
            total_violations += len(violations)

    if total_violations == 0:
        print("OK: no `.unwrap()` calls in production code.")
        return 0
    print()
    print(f"BLOCKER: {total_violations} `.unwrap()` calls in production code.")
    print("Use `?`, `.expect(\"reason\")`, or `match` instead.")
    print("If a specific call is justified, add `// allow-unwrap: <reason>`")
    print("on the same line and document in the WP.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
