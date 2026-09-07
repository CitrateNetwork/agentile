#!/usr/bin/env bash
# pre-commit-frontmatter.sh — Rule 12 enforcer at commit time.
#
# Runs `check_frontmatter.py --files <staged .md files>` on the staged
# changes. If any new .md under .agentile/ lacks Rule-12 frontmatter,
# the commit is blocked.
#
# Wired via .claude/settings.json's `hooks.PreToolUse` and via
# bootstrap.sh installing it as a git pre-commit hook (.git/hooks/pre-commit).
# The same script handles both invocations.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
find_project_root() {
  local d="$SCRIPT_DIR"
  while [[ "$d" != "/" ]]; do
    [[ -d "$d/.agentile" ]] && { echo "$d"; return 0; }
    d="$(dirname "$d")"
  done
  echo "ERROR: no .agentile/ found above ${SCRIPT_DIR}" >&2
  exit 0   # Hook should be no-op outside agentile-equipped repos
}
PROJECT_ROOT="$(find_project_root)"

# Collect staged .md files under .agentile/, excluding INDEX/.
#
# NOTE: use a portable `while read` loop, not `mapfile`/`readarray`.
# `mapfile` is a bash-4 builtin; macOS ships bash 3.2.57 as /bin/bash,
# where `mapfile: command not found` would abort *every* commit in the
# adopter's repo. This loop works identically on bash 3.2 and 5.x.
staged=()
while IFS= read -r line; do
  [[ -n "$line" ]] && staged+=("$line")
done < <(
  git -C "$PROJECT_ROOT" diff --cached --name-only --diff-filter=AM \
    -- '.agentile/**/*.md' \
    | grep -v '^\.agentile/INDEX/' || true
)

if [[ "${#staged[@]}" -eq 0 ]]; then
  exit 0
fi

# shellcheck disable=SC2086
"$PROJECT_ROOT/scripts/ci/check_frontmatter.py" --files "${staged[@]}"
