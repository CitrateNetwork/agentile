#!/usr/bin/env bash
# sprint.sh — agent-agnostic sprint CLI.
#
# Wraps the recurring sprint-lifecycle moves (kickoff, daily, close,
# index, rename) so they can be invoked the same way by humans, agents,
# CI scripts, and shell aliases. Subcommands are thin shims around the
# underlying Python tools and templates — the CLI exists for ergonomics
# and discoverability, not to add behavior.
#
# Project-root resolution: walks upward from this script to find the
# nearest ancestor containing a `.agentile/` directory. Same convention
# as the indexer scripts in `scripts/index/`.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

find_project_root() {
  local d="$SCRIPT_DIR"
  while [[ "$d" != "/" ]]; do
    if [[ -d "$d/.agentile" ]]; then
      echo "$d"
      return 0
    fi
    d="$(dirname "$d")"
  done
  echo "ERROR: no .agentile/ directory found above ${SCRIPT_DIR}" >&2
  exit 2
}

PROJECT_ROOT="$(find_project_root)"
AGENTILE="$PROJECT_ROOT/.agentile"
INDEX_DIR="$SCRIPT_DIR/index"

# ---------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------

cmd_kickoff() {
  local id="${1:-}"
  local slug="${2:-}"
  if [[ -z "$id" || -z "$slug" ]]; then
    cat <<'USAGE' >&2
Usage: sprint.sh kickoff <SPRINT_ID> <slug>

Examples:
  sprint.sh kickoff S-1 first-feature
  sprint.sh kickoff RM-A-1 consensus-findings

Creates .agentile/sprints/active/YYYY-MM-DD-sprint-<id>-<slug>/SPRINT.md
seeded from templates/SPRINT_TEMPLATE.md, with frontmatter prefilled.
USAGE
    exit 1
  fi

  local today
  today="$(date -u +%Y-%m-%d)"
  local now_iso
  now_iso="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  local branch
  branch="$(git -C "$PROJECT_ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)"

  local lower_id
  lower_id="$(echo "$id" | tr '[:upper:]' '[:lower:]')"
  local sprint_dir="$AGENTILE/sprints/active/${today}-sprint-${lower_id}-${slug}"

  if [[ -e "$sprint_dir" ]]; then
    echo "ERROR: $sprint_dir already exists" >&2
    exit 1
  fi

  local template="$AGENTILE/templates/SPRINT_TEMPLATE.md"
  if [[ ! -f "$template" ]]; then
    echo "ERROR: template not found at $template" >&2
    exit 1
  fi

  mkdir -p "$sprint_dir"

  # Replace the frontmatter block with project-specific values, leaving
  # the body of the template intact for the project owner to fill in.
  awk -v iso="$now_iso" -v branch="$branch" -v id="$id" '
    BEGIN { in_fm = 0; fm_count = 0 }
    /^---$/ {
      fm_count++
      if (fm_count == 1) {
        in_fm = 1
        print "---"
        print "created: " iso
        print "branch: " branch
        print "author: "
        print "sprint: " id
        print "status: active"
        next
      }
      if (fm_count == 2) {
        in_fm = 0
        print "---"
        next
      }
    }
    !in_fm { print }
  ' "$template" > "$sprint_dir/SPRINT.md"

  # Also seed an empty DAILY.md.
  if [[ -f "$AGENTILE/templates/DAILY_TEMPLATE.md" ]]; then
    awk -v iso="$now_iso" -v branch="$branch" -v id="$id" '
      BEGIN { in_fm = 0; fm_count = 0 }
      /^---$/ {
        fm_count++
        if (fm_count == 1) {
          in_fm = 1
          print "---"
          print "created: " iso
          print "branch: " branch
          print "author: "
          print "sprint: " id
          print "status: active"
          next
        }
        if (fm_count == 2) {
          in_fm = 0
          print "---"
          next
        }
      }
      !in_fm { print }
    ' "$AGENTILE/templates/DAILY_TEMPLATE.md" > "$sprint_dir/DAILY.md"
  fi

  echo "Created: $sprint_dir/SPRINT.md"
  echo "Created: $sprint_dir/DAILY.md"
  echo
  echo "Next steps:"
  echo "  1. Edit $sprint_dir/SPRINT.md — fill in goal, WPs, baselines"
  echo "  2. Update $AGENTILE/sprints/CURRENT.md to point at this sprint"
  echo "  3. Commit the kickoff: git add $sprint_dir && git commit -m 'chore(${id}): kickoff'"
}

cmd_daily() {
  local sprint_dir
  sprint_dir="$(_active_sprint_dir)" || exit 1

  local today
  today="$(date -u +%Y-%m-%d)"
  local daily_file="$sprint_dir/DAILY.md"

  if [[ ! -f "$daily_file" ]]; then
    echo "ERROR: $daily_file does not exist" >&2
    exit 1
  fi

  if grep -q "^## ${today}$" "$daily_file" 2>/dev/null; then
    echo "Daily entry for $today already exists in $daily_file"
    exit 0
  fi

  cat >> "$daily_file" <<EOF

## ${today}

**Active WP(s):**

**Commits today:**
-

**Tests now / baseline:**  /

**Done today:**
-

**Blockers:**
-

**Tomorrow's plan:**
-

**Notes / surprises:**

EOF
  echo "Appended daily entry: $daily_file"
}

cmd_close() {
  local sprint_dir
  sprint_dir="$(_active_sprint_dir)" || exit 1

  local sprint_name
  sprint_name="$(basename "$sprint_dir")"
  local completed_dir="$AGENTILE/sprints/completed/$sprint_name"

  if [[ -e "$completed_dir" ]]; then
    echo "ERROR: $completed_dir already exists" >&2
    exit 1
  fi

  # Seed RETRO.md from template if it doesn't already exist.
  if [[ ! -f "$sprint_dir/RETRO.md" ]] && [[ -f "$AGENTILE/templates/RETRO_TEMPLATE.md" ]]; then
    local now_iso
    now_iso="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    local branch
    branch="$(git -C "$PROJECT_ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)"

    awk -v iso="$now_iso" -v branch="$branch" '
      BEGIN { in_fm = 0; fm_count = 0 }
      /^---$/ {
        fm_count++
        if (fm_count == 1) {
          in_fm = 1
          print "---"
          print "created: " iso
          print "branch: " branch
          print "author: "
          print "status: active"
          next
        }
        if (fm_count == 2) {
          in_fm = 0
          print "---"
          next
        }
      }
      !in_fm { print }
    ' "$AGENTILE/templates/RETRO_TEMPLATE.md" > "$sprint_dir/RETRO.md"
    echo "Seeded $sprint_dir/RETRO.md from template (fill it in before final commit)"
  fi

  echo
  echo "Sprint $sprint_name is ready to close. To complete:"
  echo "  1. Finish editing $sprint_dir/RETRO.md"
  echo "  2. git mv $sprint_dir $completed_dir"
  echo "  3. Update $AGENTILE/sprints/CURRENT.md"
  echo "  4. Commit + push"
  echo
  echo "(This script does not move the directory automatically — that"
  echo " step is gated on the project owner reviewing RETRO.md first.)"
}

cmd_index() {
  "$INDEX_DIR/build_agentile_index.py"
}

cmd_backfill() {
  "$INDEX_DIR/backfill_frontmatter.py"
}

cmd_status() {
  echo "Project root: $PROJECT_ROOT"
  echo
  echo "Active sprints:"
  if [[ -d "$AGENTILE/sprints/active" ]]; then
    find "$AGENTILE/sprints/active" -mindepth 1 -maxdepth 1 -type d -printf "  %f\n" | sort
  else
    echo "  (no sprints/active/ directory)"
  fi
  echo
  if [[ -f "$AGENTILE/sprints/CURRENT.md" ]]; then
    echo "CURRENT.md:"
    sed -n '1,12p' "$AGENTILE/sprints/CURRENT.md" | sed 's/^/  /'
  fi
}

# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

_active_sprint_dir() {
  local active_root="$AGENTILE/sprints/active"
  if [[ ! -d "$active_root" ]]; then
    echo "ERROR: no $active_root directory" >&2
    return 1
  fi
  local count
  count="$(find "$active_root" -mindepth 1 -maxdepth 1 -type d | wc -l)"
  if [[ "$count" -eq 0 ]]; then
    echo "ERROR: no active sprint" >&2
    return 1
  fi
  if [[ "$count" -gt 1 ]]; then
    echo "ERROR: multiple active sprints found; pass the sprint dir explicitly:" >&2
    find "$active_root" -mindepth 1 -maxdepth 1 -type d -printf "  %f\n" >&2
    return 1
  fi
  find "$active_root" -mindepth 1 -maxdepth 1 -type d
}

usage() {
  cat <<'USAGE'
sprint.sh — agent-agnostic sprint CLI.

Subcommands:
  kickoff <ID> <slug>   Create a new active sprint dir from templates
  daily                 Append a dated entry to the active sprint's DAILY.md
  close                 Seed RETRO.md and print close-out checklist
  index                 Run scripts/index/build_agentile_index.py
  backfill              Run scripts/index/backfill_frontmatter.py
  status                Show project root, active sprints, CURRENT.md head
  help                  Show this message

Examples:
  scripts/sprint.sh kickoff S-1 first-feature
  scripts/sprint.sh daily
  scripts/sprint.sh index
  scripts/sprint.sh status

The CLI is a thin wrapper around the indexer scripts and the
templates in .agentile/templates/. It does not introduce behavior
beyond what those underlying tools and conventions provide.
USAGE
}

# ---------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------

cmd="${1:-help}"
shift || true

case "$cmd" in
  kickoff)  cmd_kickoff "$@" ;;
  daily)    cmd_daily "$@" ;;
  close)    cmd_close "$@" ;;
  index)    cmd_index "$@" ;;
  backfill) cmd_backfill "$@" ;;
  status)   cmd_status "$@" ;;
  help|-h|--help) usage ;;
  *)
    echo "Unknown subcommand: $cmd" >&2
    echo
    usage
    exit 1
    ;;
esac
