#!/usr/bin/env bash
# post-commit-journal-prompt.sh — gentle nudge to journal at sprint
# boundaries.
#
# Runs after every commit. If the commit looks like a sprint kickoff
# or close (subject matches `kickoff` or `RETRO` or `close`), prints
# a one-line suggestion to write a journal entry. Otherwise silent.
#
# Never blocks — this is purely a reminder. Disable by removing the
# hook from .git/hooks/post-commit (bootstrap.sh installs it; the
# user can opt out at install time).

set -euo pipefail

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

subject=$(git -C "$PROJECT_ROOT" log -1 --format=%s 2>/dev/null || true)
if [[ -z "$subject" ]]; then
  exit 0
fi

case "$subject" in
  *kickoff*|*"sprint open"*|*RETRO*|*"sprint close"*)
    echo
    echo "💡 Sprint boundary committed. Consider writing a journal entry:"
    echo "   /journal      (slash command in Claude Code)"
    echo "   or seed manually from .agentile/templates/JOURNAL_TEMPLATE.md"
    echo
    ;;
esac

exit 0
