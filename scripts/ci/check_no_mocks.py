#!/usr/bin/env python3
"""Rule 2 + Rule 11 enforcer: no mocks/stubs/fakes in production code paths.

Catches the "Testing Backend Loophole" (THE_RULE_FOLLOWERS_PARADOX):
an agent creates `StubFooBackend` / `MockFooBackend` / `FakeFooBackend`
and wires it as the default in `Service::new()`. The result is
production code silently returning fake data while passing surface
checks like `grep -r "TODO"`.

Heuristics (Rust default):
  1. Type definitions named `*Stub*`, `*Mock*`, `*Fake*`, `*Dummy*` MUST
     be guarded by `#[cfg(test)]` or live in a `tests/`-rooted file.
  2. Files matching `MOCKS.md` at the project root are checked: if it
     exists and contains entries, each entry must reference a
     replacement WP (regex: `WP-[A-Z0-9-]+`). Otherwise the entry is a
     forgotten mock.

Exit codes:
  0 — no offenders
  1 — violations found; lists file:line
  2 — usage error

Flags:
  --files <path>...   Only check these files.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "index"))
from _common import find_project_root  # type: ignore  # noqa: E402

PROJECT_ROOT = find_project_root()

RUST_PROD_DIRS = ["src", "core", "node", "wallet", "cli", "faucet"]
EXCLUDE_PATTERNS = [
    re.compile(r"(?:^|/)tests/"),
    re.compile(r"(?:^|/)target/"),
    re.compile(r"(?:^|/)benches/"),
    re.compile(r"test_[^/]+\.rs$"),
    re.compile(r"_test\.rs$"),
    re.compile(r"_tests\.rs$"),
]

# `pub struct StubFooBackend`, `struct MockBlah`, `pub enum FakeXxx`,
# `pub trait DummyYyy`, etc. The constraint is `(struct|enum|trait|type)`
# followed by an identifier whose substring is one of the marker words.
TYPE_DEF_RE = re.compile(
    r"\b(?:pub\s+)?(?:pub\s*\(\s*[^)]+\s*\)\s*)?(struct|enum|trait|type)\s+"
    r"(?P<name>[A-Za-z_][A-Za-z0-9_]*)"
)
MARKERS = ("Stub", "Mock", "Fake", "Dummy")


def is_excluded(rel: str) -> bool:
    return any(p.search(rel) for p in EXCLUDE_PATTERNS)


def has_cfg_test_guard(lines: list[str], idx: int) -> bool:
    """Walk upward from line index `idx` looking for #[cfg(test)] or
    #[cfg(any(test, ...))] attributes attached to the type definition.
    Stop at a blank line or non-attribute line."""
    j = idx - 1
    while j >= 0:
        s = lines[j].strip()
        if not s:
            return False
        if s.startswith("//"):
            j -= 1
            continue
        if s.startswith("#["):
            if "cfg(test)" in s or "cfg(any(test" in s:
                return True
            j -= 1
            continue
        return False
    return False


def in_cfg_test_module(lines: list[str], idx: int) -> bool:
    """Detect `mod tests { ... }` enclosing the line. Naive — counts
    braces upward from idx looking for a `mod tests` opener with a
    `#[cfg(test)]` attribute on it. Good enough for the common case."""
    depth = 0
    j = idx
    while j >= 0:
        s = lines[j]
        for ch in reversed(s):
            if ch == "}":
                depth += 1
            elif ch == "{":
                depth -= 1
                if depth < 0:
                    # Found enclosing block opener.
                    if re.search(r"\bmod\s+tests?\b", s):
                        # Look up for #[cfg(test)] attr on this mod.
                        k = j - 1
                        while k >= 0 and lines[k].strip().startswith(("//", "#[")):
                            if "cfg(test)" in lines[k] or "cfg(any(test" in lines[k]:
                                return True
                            k -= 1
                        return False
                    return False
        j -= 1
    return False


def check_rust_files(files: list[Path]) -> list[tuple[Path, int, str]]:
    violations: list[tuple[Path, int, str]] = []
    for path in files:
        rel = str(path.relative_to(PROJECT_ROOT))
        if is_excluded(rel):
            continue
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for i, line in enumerate(lines):
            m = TYPE_DEF_RE.search(line)
            if not m:
                continue
            name = m.group("name")
            if not any(marker in name for marker in MARKERS):
                continue
            if has_cfg_test_guard(lines, i) or in_cfg_test_module(lines, i):
                continue
            violations.append((path, i + 1, line.strip()))
    return violations


def check_mocks_registry() -> list[str]:
    """If MOCKS.md exists at project root, every entry must reference a
    replacement WP. Returns a list of "registry violation" strings."""
    issues: list[str] = []
    mocks_md = PROJECT_ROOT / "MOCKS.md"
    if not mocks_md.exists():
        return issues
    try:
        text = mocks_md.read_text(encoding="utf-8")
    except OSError:
        return ["MOCKS.md is unreadable."]
    # Heuristic: each "## " section is one mock. Each section must mention WP-XXX.
    sections = re.split(r"^## ", text, flags=re.MULTILINE)
    for sec in sections[1:]:
        title = sec.splitlines()[0].strip() if sec.splitlines() else "(unknown)"
        if not re.search(r"WP-[A-Za-z0-9.-]+", sec):
            issues.append(f"MOCKS.md entry '{title}' has no replacement WP reference.")
    return issues


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


def main() -> int:
    args = sys.argv[1:]
    if args and args[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    explicit_files: list[str] = []
    if args and args[0] == "--files":
        explicit_files = args[1:]

    files = collect_rust_files(explicit_files)
    rust_violations = check_rust_files(files)
    registry_issues = check_mocks_registry()

    if not rust_violations and not registry_issues:
        print("OK: no mock/stub types in production code paths; "
              "MOCKS.md (if present) is well-formed.")
        return 0

    if rust_violations:
        print(f"=== {len(rust_violations)} mock/stub type definition(s) outside #[cfg(test)] ===")
        for path, lineno, line in rust_violations:
            print(f"  {path.relative_to(PROJECT_ROOT)}:{lineno}: {line}")
        print()
        print("Each Stub/Mock/Fake/Dummy type MUST be behind #[cfg(test)] or in")
        print("a tests/-rooted file. If the production code legitimately needs a")
        print("'fake-by-design' type (e.g. a noop handler), rename it to express")
        print("its real role (e.g. NoopHandler, NullSink) — the marker words are")
        print("reserved for test scaffolding.")

    if registry_issues:
        print(f"=== MOCKS.md registry issues ({len(registry_issues)}) ===")
        for s in registry_issues:
            print(f"  {s}")

    return 1


if __name__ == "__main__":
    sys.exit(main())
