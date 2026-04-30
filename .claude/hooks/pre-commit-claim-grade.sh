#!/usr/bin/env bash
# pre-commit-claim-grade.sh — soft-gate: grade the commit message.
#
# Pipes the staged commit message into `grade_claim.py`. If the score
# is below CLAIM_GRADE_THRESHOLD (default: 4), prints the suggested
# rewrite and asks the user to confirm before proceeding.
#
# This hook is INFORMATIONAL by default — it does not block the commit
# regardless of the score. Block-mode is opt-in via
# CLAIM_GRADE_STRICT=1 in the environment.
#
# Wired by bootstrap.sh as .git/hooks/prepare-commit-msg or
# commit-msg, depending on user preference. Skips silently if the
# grader is unavailable (no API key).

set -euo pipefail

# Argv from git's commit-msg hook: $1 = path to commit message file
COMMIT_MSG_FILE="${1:-}"
if [[ -z "$COMMIT_MSG_FILE" || ! -f "$COMMIT_MSG_FILE" ]]; then
  exit 0   # Not in commit-msg context; no-op.
fi

# Skip merge commits and amends-with-no-message.
if [[ -n "${GIT_REFLOG_ACTION:-}" ]] && [[ "$GIT_REFLOG_ACTION" == merge* ]]; then
  exit 0
fi

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
GRADER="$PROJECT_ROOT/scripts/ai/grade_claim.py"

if [[ ! -x "$GRADER" ]]; then
  exit 0
fi

# Strip comment lines (git's # prefix) from the message before grading.
msg=$(grep -v '^#' "$COMMIT_MSG_FILE" | sed '/^$/N;/^\n$/D' || true)
if [[ -z "$msg" ]]; then
  exit 0
fi

threshold="${CLAIM_GRADE_THRESHOLD:-4}"
strict="${CLAIM_GRADE_STRICT:-0}"

# Capture the JSON output. The grader returns 0 even when no API key is
# set (it emits a "grader-unavailable" verdict), so we don't need to
# disable -e here.
report=$(echo "$msg" | "$GRADER" 2>/dev/null || true)

# Best-effort parse: extract `score` and `verdict` from the JSON.
score=$(echo "$report" | python3 -c "import json,sys
try:
    d = json.load(sys.stdin)
    s = d.get('score')
    print(s if s is not None else '')
except Exception:
    print('')" 2>/dev/null || true)

verdict=$(echo "$report" | python3 -c "import json,sys
try:
    d = json.load(sys.stdin)
    print(d.get('verdict', ''))
except Exception:
    print('')" 2>/dev/null || true)

if [[ -z "$score" ]]; then
  # Grader unavailable or parse failure — silent.
  exit 0
fi

if [[ "$score" -ge "$threshold" ]]; then
  # Honest enough to skip the prompt.
  exit 0
fi

echo
echo "==== Claim grader: score $score ($verdict) ===="
echo "$report" | python3 -c "import json,sys
d=json.load(sys.stdin)
for r in d.get('reasons', []): print(f'  - {r}')
sw = d.get('suggested_rewrite')
if sw:
    print()
    print('Suggested rewrite:')
    for line in sw.splitlines(): print(f'  > {line}')
" 2>/dev/null || true
echo "==============================================="
echo

if [[ "$strict" == "1" ]]; then
  echo "CLAIM_GRADE_STRICT=1: blocking commit." >&2
  exit 1
fi

echo "(Informational only — set CLAIM_GRADE_STRICT=1 to block on low scores.)"
exit 0
