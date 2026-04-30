#!/usr/bin/env python3
"""Rule 11 enforcer: every IPC command, RPC method, or service-layer
endpoint claims a named data source.

Heuristic scan over changed files. For each detected "endpoint-like"
declaration, verify there's a `data source:` comment within N lines
above the declaration. If not, the change is flagged for human
review.

What counts as an "endpoint-like" declaration (Rust default; adapter
patterns are project-specific):

  - `#[tauri::command]` — Tauri IPC command
  - `#[rpc(...)]` / `#[method(...)]` — JSON-RPC method (jsonrpsee)
  - `pub async fn handler_*(` / `pub async fn get_*(` /
    `pub async fn list_*(` — service-layer methods that look like
    they wrap a data source

What counts as a `data source:` comment:

  - `// data source: <named source>` — within 6 lines above
  - `/// Data source: <named source>` — Rust doc comment, same window
  - `# data source: <named source>` — for adapters in Python/etc.

The named source must be specific: a contract address, contract
method name, RPC method, file path, or external service URL. The
script does not validate the *name* (an LLM grader would); it only
checks that something follows the `data source:` keyword.

This check is INTENTIONALLY a soft gate (default: warn-only). False
positives are common because the heuristic is regex-level. CI runs
it in shadow mode; humans review the comment posted to the PR.

Exit codes:
  0 — no missing data sources OR --shadow mode (always 0)
  1 — missing data sources detected (only with --strict)
  2 — usage error
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "index"))
from _common import find_project_root  # type: ignore  # noqa: E402

PROJECT_ROOT = find_project_root()

# Endpoint-like declaration patterns, language-keyed.
RUST_PATTERNS = [
    (re.compile(r"^\s*#\[tauri::command\]"), "tauri ipc"),
    (re.compile(r"^\s*#\[rpc\b"), "rpc"),
    (re.compile(r"^\s*#\[method\b"), "rpc method"),
    (re.compile(r"^\s*pub\s+(async\s+)?fn\s+(handler|get|list|fetch|read)_\w+\s*\("), "service-layer method"),
]

DATA_SOURCE_RE = re.compile(
    r"^\s*(///+|//|#)\s*[Dd]ata\s+source\s*:",
)
WINDOW = 6  # lines above the declaration to scan for a data-source comment


def changed_files(base: str | None) -> list[Path]:
    if not base:
        # Default: every file under common source dirs. Slow on large repos;
        # CI uses --base to scope.
        out: list[Path] = []
        for d in ("src", "core", "node", "wallet", "cli", "faucet"):
            root = PROJECT_ROOT / d
            if root.exists():
                out.extend(root.rglob("*.rs"))
        return out
    proc = subprocess.run(
        ["git", "-C", str(PROJECT_ROOT),
         "diff", "--name-only", "--diff-filter=AM",
         f"{base}..HEAD"],
        capture_output=True, text=True, check=False,
    )
    if proc.returncode != 0:
        return []
    out: list[Path] = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        if not line.endswith(".rs"):
            continue
        if "/tests/" in line or line.endswith("_test.rs") or line.endswith("_tests.rs"):
            continue
        path = PROJECT_ROOT / line
        if path.exists():
            out.append(path)
    return out


def find_endpoints_rust(path: Path) -> list[tuple[int, str, str]]:
    """Returns list of (lineno, kind, declaration) tuples."""
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []
    out: list[tuple[int, str, str]] = []
    for i, line in enumerate(lines):
        for pat, kind in RUST_PATTERNS:
            if pat.search(line):
                out.append((i, kind, line.strip()))
                break
    return out


def has_data_source_comment(path: Path, decl_line: int) -> bool:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return False
    start = max(0, decl_line - WINDOW)
    for j in range(start, decl_line):
        if DATA_SOURCE_RE.search(lines[j]):
            return True
    return False


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--base", help="Git base ref; only check files changed in base..HEAD")
    p.add_argument("--strict", action="store_true",
                   help="Exit 1 on missing data sources (default: shadow / always 0)")
    p.add_argument("--out-md", help="Write a markdown summary to this path")
    args = p.parse_args()

    files = changed_files(args.base)
    findings: list[dict] = []

    for path in files:
        endpoints = find_endpoints_rust(path)
        for lineno, kind, decl in endpoints:
            if not has_data_source_comment(path, lineno):
                findings.append({
                    "file": str(path.relative_to(PROJECT_ROOT)),
                    "line": lineno + 1,
                    "kind": kind,
                    "declaration": decl[:120],
                })

    if not findings:
        print("OK: every endpoint-like declaration in scope has a `data source:` comment.")
        if args.out_md:
            Path(args.out_md).write_text(
                "## Data-source check (shadow mode)\n\n"
                "OK — every endpoint-like declaration in this PR has a "
                "named data source within 6 lines above it.\n",
                encoding="utf-8",
            )
        return 0

    print(f"{len(findings)} endpoint-like declaration(s) without a `data source:` comment:")
    for f in findings:
        print(f"  {f['file']}:{f['line']} ({f['kind']}): {f['declaration']}")

    if args.out_md:
        lines: list[str] = []
        lines.append("## Data-source check (shadow mode)")
        lines.append("")
        lines.append(f"{len(findings)} endpoint-like declaration(s) lack a `data source:` "
                     f"comment in the {WINDOW} lines above them. This is a SOFT signal — "
                     f"the heuristic is regex-level and produces false positives. Human "
                     f"reviewers should verify Rule 11 compliance for each.")
        lines.append("")
        lines.append("| File:line | Kind | Declaration |")
        lines.append("|-----------|------|-------------|")
        for f in findings:
            lines.append(f"| `{f['file']}:{f['line']}` | {f['kind']} | `{f['declaration']}` |")
        lines.append("")
        lines.append("To suppress on a true positive, add a comment immediately above the "
                     "declaration:")
        lines.append("")
        lines.append("```rust")
        lines.append("// data source: ContractName.methodName via eth_call")
        lines.append("#[tauri::command]")
        lines.append("pub async fn handler_x(...) -> Result<...> { ... }")
        lines.append("```")
        Path(args.out_md).write_text("\n".join(lines), encoding="utf-8")

    return 1 if args.strict else 0


if __name__ == "__main__":
    sys.exit(main())
