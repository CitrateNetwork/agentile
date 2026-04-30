#!/usr/bin/env bash
# pre-merge-data-source.sh — Rule 11 heuristic before merging a PR locally.
#
# Run before `git merge` to check whether the incoming branch adds
# endpoints lacking `data source: ...` comments. Informational by
# default; opt-in to block via DATA_SOURCE_STRICT=1.
#
# This is for local merges. The CI version of the same check runs in
# .github/workflows/data-source-check.yml against PR diffs.

set -euo pipefail

# Optional argv: branch to check against. Default: HEAD.
BASE_REF="${1:-HEAD}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
find_project_root() {
  local d="$SCRIPT_DIR"
  while [[ "$d" != "/" ]]; do
    [[ -d "$d/.agentile" ]] && { echo "$d"; return 0; }
    d="$(dirname "$d")"
  done
  exit 0
}
PROJECT_ROOT="$(find_project_root)"
CHECKER="$PROJECT_ROOT/scripts/eval/data_source_check.py"

if [[ ! -x "$CHECKER" ]]; then
  exit 0
fi

strict="${DATA_SOURCE_STRICT:-0}"

if [[ "$strict" == "1" ]]; then
  "$CHECKER" --base "$BASE_REF" --strict
else
  "$CHECKER" --base "$BASE_REF" || true
  echo
  echo "(Informational only — set DATA_SOURCE_STRICT=1 to block.)"
fi
