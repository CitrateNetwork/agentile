#!/usr/bin/env bash
# bootstrap.sh — interactive setup for a fresh agentile-equipped project.
#
# Run once per project, after cloning the skeleton or copying it into
# place. Walks the project owner through:
#
#   1. Project name, description, languages, license
#   2. Filling in .agentile/CONFIG.md from the template
#   3. Filling in .agentile/PRODUCT_SPEC.md from the template
#   4. Generating CLAUDE.md from .claude/CLAUDE.md.template
#   5. Renaming Sprint 0 bootstrap folder to today's date
#   6. Capturing day-zero baselines into .agentile/coverage/baseline.json
#      and .agentile/coverage/BASELINE.md
#   7. (Optional) installing git hooks from .claude/hooks/
#   8. Running the indexer to seed .agentile/INDEX/
#   9. Committing: `chore: bootstrap from agentile-skeleton vX.Y.Z`
#
# Idempotent: re-running detects already-bootstrapped state and offers
# to update individual sections rather than starting over.
#
# Non-interactive mode for CI / automation:
#   bootstrap.sh --non-interactive --project-name="..." --license="MIT" ...

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PROJECT_ROOT="$SCRIPT_DIR"
AGENTILE="$PROJECT_ROOT/.agentile"
SKELETON_VERSION="v1.0.0-rc1"

# ---------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------

INTERACTIVE=1
PROJECT_NAME=""
PROJECT_DESC=""
LANGUAGES=""
LICENSE_KIND=""
INSTALL_HOOKS=1

usage() {
  cat <<USAGE
bootstrap.sh — set up a fresh agentile-equipped project.

Usage:
  bootstrap.sh                        Interactive (default)
  bootstrap.sh --non-interactive \\
    --project-name="<name>" \\
    --description="<one line>" \\
    --languages="rust,typescript" \\
    --license="MIT" \\
    [--no-hooks]

Flags:
  --non-interactive       Skip prompts; require all values via flags
  --project-name=<str>    Required in non-interactive mode
  --description=<str>     Optional
  --languages=<csv>       Comma-separated, e.g. "rust,typescript"
  --license=<str>         e.g. "MIT", "Apache-2.0", "Proprietary"
  --no-hooks              Skip git-hooks install
  -h, --help              Show this message

Re-running on an already-bootstrapped project is safe: the script
detects existing values and asks whether to update each section.
USAGE
}

for arg in "$@"; do
  case "$arg" in
    --non-interactive) INTERACTIVE=0 ;;
    --project-name=*)  PROJECT_NAME="${arg#*=}" ;;
    --description=*)   PROJECT_DESC="${arg#*=}" ;;
    --languages=*)     LANGUAGES="${arg#*=}" ;;
    --license=*)       LICENSE_KIND="${arg#*=}" ;;
    --no-hooks)        INSTALL_HOOKS=0 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $arg" >&2; usage; exit 1 ;;
  esac
done

# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

ask() {
  local prompt="$1"
  local default="${2:-}"
  local var
  if [[ "$INTERACTIVE" -eq 0 ]]; then
    echo "$default"
    return
  fi
  if [[ -n "$default" ]]; then
    read -r -p "$prompt [$default]: " var
    echo "${var:-$default}"
  else
    read -r -p "$prompt: " var
    echo "$var"
  fi
}

confirm() {
  local prompt="$1"
  if [[ "$INTERACTIVE" -eq 0 ]]; then
    return 0
  fi
  local ans
  read -r -p "$prompt [Y/n]: " ans
  [[ -z "$ans" || "$ans" =~ ^[Yy] ]]
}

require_clean_tree() {
  if [[ -n "$(git -C "$PROJECT_ROOT" status --porcelain 2>/dev/null || true)" ]]; then
    echo "WARNING: working tree has uncommitted changes." >&2
    if [[ "$INTERACTIVE" -eq 1 ]]; then
      confirm "Continue anyway?" || exit 1
    fi
  fi
}

today_iso() { date -u +%Y-%m-%d; }
now_iso()   { date -u +%Y-%m-%dT%H:%M:%SZ; }

# Escape an arbitrary string for safe use as a `sed` s/// REPLACEMENT.
# `&` expands to the whole match and `\`/`/` are structural, so all three
# must be escaped. A newline terminates the s/// command and could start a
# new sed command (GNU sed's `e` runs a shell) — so we reject control
# characters outright rather than try to escape them. This closes the
# template-injection vector when --project-name/--description/etc. come from
# a non-interactive caller feeding untrusted input.
sed_escape() {
  local value="$1"
  # Reject newlines/carriage returns explicitly (a line-oriented grep would
  # not "see" a bare newline as a character within a line) plus any other
  # control character via bash's own regex over the whole string.
  if [[ "$value" == *$'\n'* || "$value" == *$'\r'* || "$value" =~ [[:cntrl:]] ]]; then
    echo "ERROR: template value contains a control character or newline; refusing (template-injection guard)" >&2
    exit 1
  fi
  # Order matters: backslash first, then the delimiter and ampersand.
  value="${value//\\/\\\\}"
  value="${value//\//\\/}"
  value="${value//&/\\&}"
  printf '%s' "$value"
}

# ---------------------------------------------------------------------
# Step 0: Sanity
# ---------------------------------------------------------------------

if [[ ! -d "$AGENTILE" ]]; then
  echo "ERROR: $AGENTILE does not exist. Are you in the agentile skeleton root?" >&2
  exit 1
fi

if ! git -C "$PROJECT_ROOT" rev-parse --git-dir >/dev/null 2>&1; then
  echo "ERROR: not a git repository. Run 'git init' first, or clone the skeleton." >&2
  exit 1
fi

echo "==================================================================="
echo "  Agentile bootstrap — skeleton $SKELETON_VERSION"
echo "==================================================================="
echo

# ---------------------------------------------------------------------
# Step 1: Project metadata
# ---------------------------------------------------------------------

if [[ -z "$PROJECT_NAME" ]]; then
  default_name="$(basename "$PROJECT_ROOT")"
  PROJECT_NAME="$(ask 'Project name' "$default_name")"
fi
[[ -z "$PROJECT_DESC"   ]] && PROJECT_DESC="$(ask 'One-line description' '')"
[[ -z "$LANGUAGES"      ]] && LANGUAGES="$(ask 'Primary language(s), comma-separated' 'rust')"
[[ -z "$LICENSE_KIND"   ]] && LICENSE_KIND="$(ask 'License' 'MIT')"

DAY_ZERO_DATE="$(today_iso)"
DAY_ZERO_TS="$(now_iso)"
DAY_ZERO_COMMIT="$(git -C "$PROJECT_ROOT" rev-parse HEAD 2>/dev/null || echo unknown)"
GIT_BRANCH="$(git -C "$PROJECT_ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null || echo main)"

echo
echo "Project:    $PROJECT_NAME"
echo "Languages:  $LANGUAGES"
echo "License:    $LICENSE_KIND"
echo "Day zero:   $DAY_ZERO_DATE @ ${DAY_ZERO_COMMIT:0:8}"
echo

# Pre-escape operator-supplied values once for safe sed templating below.
# sed_escape rejects control characters (template-injection guard) and
# escapes \, /, and & so the replacement text is inert.
ESC_PROJECT_NAME="$(sed_escape "$PROJECT_NAME")"
ESC_PROJECT_DESC="$(sed_escape "$PROJECT_DESC")"
ESC_LANGUAGES="$(sed_escape "$LANGUAGES")"
ESC_LICENSE_KIND="$(sed_escape "$LICENSE_KIND")"
ESC_SKELETON_VERSION="$(sed_escape "$SKELETON_VERSION")"

# ---------------------------------------------------------------------
# Step 2: CONFIG.md
# ---------------------------------------------------------------------

if [[ ! -f "$AGENTILE/CONFIG.md" ]]; then
  echo "[2/9] Seeding .agentile/CONFIG.md from template ..."
  if [[ -f "$AGENTILE/CONFIG.md.template" ]]; then
    cp "$AGENTILE/CONFIG.md.template" "$AGENTILE/CONFIG.md"
    # Light substitution of obvious placeholders. The user fills in the rest.
    sed -i.bak \
      -e "s/<PROJECT_NAME>/${ESC_PROJECT_NAME}/g" \
      -e "s/<PROJECT_DESCRIPTION>/${ESC_PROJECT_DESC}/g" \
      -e "s/<LANGUAGES>/${ESC_LANGUAGES}/g" \
      -e "s/<LICENSE>/${ESC_LICENSE_KIND}/g" \
      "$AGENTILE/CONFIG.md"
    rm -f "$AGENTILE/CONFIG.md.bak"
    echo "       Edit .agentile/CONFIG.md to fill in remaining placeholders."
  else
    echo "       (CONFIG.md.template not found; skipping)"
  fi
else
  echo "[2/9] .agentile/CONFIG.md already exists; leaving in place."
fi

# ---------------------------------------------------------------------
# Step 3: PRODUCT_SPEC.md
# ---------------------------------------------------------------------

if [[ ! -f "$AGENTILE/PRODUCT_SPEC.md" ]]; then
  echo "[3/9] Seeding .agentile/PRODUCT_SPEC.md from template ..."
  if [[ -f "$AGENTILE/PRODUCT_SPEC.md.template" ]]; then
    cp "$AGENTILE/PRODUCT_SPEC.md.template" "$AGENTILE/PRODUCT_SPEC.md"
    sed -i.bak \
      -e "s/<PROJECT_NAME>/${ESC_PROJECT_NAME}/g" \
      -e "s/<PROJECT_DESCRIPTION>/${ESC_PROJECT_DESC}/g" \
      "$AGENTILE/PRODUCT_SPEC.md"
    rm -f "$AGENTILE/PRODUCT_SPEC.md.bak"
    echo "       Edit .agentile/PRODUCT_SPEC.md to define the finished product."
  fi
else
  echo "[3/9] .agentile/PRODUCT_SPEC.md already exists; leaving in place."
fi

# ---------------------------------------------------------------------
# Step 4: CLAUDE.md
# ---------------------------------------------------------------------

if [[ ! -f "$PROJECT_ROOT/CLAUDE.md" ]] && [[ -f "$PROJECT_ROOT/.claude/CLAUDE.md.template" ]]; then
  echo "[4/9] Generating CLAUDE.md from .claude/CLAUDE.md.template ..."
  cp "$PROJECT_ROOT/.claude/CLAUDE.md.template" "$PROJECT_ROOT/CLAUDE.md"
  sed -i.bak \
    -e "s/<PROJECT_NAME>/${ESC_PROJECT_NAME}/g" \
    -e "s/<PROJECT_DESCRIPTION>/${ESC_PROJECT_DESC}/g" \
    -e "s/<LANGUAGES>/${ESC_LANGUAGES}/g" \
    -e "s/<LICENSE>/${ESC_LICENSE_KIND}/g" \
    -e "s/<AGENTILE_VERSION>/${ESC_SKELETON_VERSION}/g" \
    "$PROJECT_ROOT/CLAUDE.md"
  rm -f "$PROJECT_ROOT/CLAUDE.md.bak"
elif [[ -f "$PROJECT_ROOT/CLAUDE.md" ]]; then
  echo "[4/9] CLAUDE.md already exists; leaving in place."
else
  echo "[4/9] No .claude/CLAUDE.md.template found; skipping."
fi

# Also seed .claude/settings.json from template (gitignored target).
if [[ ! -f "$PROJECT_ROOT/.claude/settings.json" ]] && [[ -f "$PROJECT_ROOT/.claude/settings.json.template" ]]; then
  cp "$PROJECT_ROOT/.claude/settings.json.template" "$PROJECT_ROOT/.claude/settings.json"
  echo "       Seeded .claude/settings.json from template (gitignored)."
fi

# ---------------------------------------------------------------------
# Step 5: Sprint 0 folder rename
# ---------------------------------------------------------------------

placeholder_dir="$AGENTILE/sprints/active/YYYY-XX-XX-sprint-0-bootstrap"
if [[ -d "$placeholder_dir" ]]; then
  new_dir="$AGENTILE/sprints/active/${DAY_ZERO_DATE}-sprint-0-bootstrap"
  if [[ ! -e "$new_dir" ]]; then
    echo "[5/9] Renaming Sprint 0 placeholder to ${DAY_ZERO_DATE}-sprint-0-bootstrap ..."
    git -C "$PROJECT_ROOT" mv \
      ".agentile/sprints/active/YYYY-XX-XX-sprint-0-bootstrap" \
      ".agentile/sprints/active/${DAY_ZERO_DATE}-sprint-0-bootstrap" 2>/dev/null \
      || mv "$placeholder_dir" "$new_dir"
    # Flip status: template -> active in the SPRINT.md frontmatter.
    sprint_md="$new_dir/SPRINT.md"
    if [[ -f "$sprint_md" ]]; then
      sed -i.bak 's/^status: template$/status: active/' "$sprint_md"
      sed -i.bak "s/| \*\*Start Date\*\* | YYYY-MM-DD |/| **Start Date** | ${DAY_ZERO_DATE} |/" "$sprint_md"
      rm -f "$sprint_md.bak"
    fi
  fi
else
  echo "[5/9] No Sprint 0 placeholder to rename."
fi

# ---------------------------------------------------------------------
# Step 6: Baseline
# ---------------------------------------------------------------------

baseline_md="$AGENTILE/coverage/BASELINE.md"
baseline_json="$AGENTILE/coverage/baseline.json"

if [[ ! -f "$baseline_md" ]] && [[ -f "$AGENTILE/coverage/BASELINE.md.template" ]]; then
  echo "[6/9] Seeding .agentile/coverage/BASELINE.md from template ..."
  cp "$AGENTILE/coverage/BASELINE.md.template" "$baseline_md"
  sed -i.bak \
    -e "s/<PROJECT NAME>/${ESC_PROJECT_NAME}/g" \
    -e "s/<full git hash>/${DAY_ZERO_COMMIT}/g" \
    "$baseline_md"
  rm -f "$baseline_md.bak"
fi

if [[ ! -f "$baseline_json" ]] && [[ -f "$AGENTILE/coverage/baseline.json.template" ]]; then
  echo "       Seeding .agentile/coverage/baseline.json from template ..."
  python3 - "$AGENTILE/coverage/baseline.json.template" "$baseline_json" \
    "$PROJECT_NAME" "$DAY_ZERO_COMMIT" "$DAY_ZERO_DATE" <<'PYEOF'
import json, sys
src, dst, name, sha, date = sys.argv[1:6]
data = json.loads(open(src).read())
data["project"] = name
data["day_zero_commit"] = sha
data["day_zero_date"] = date
# Drop the schema-comment fields for the live file.
for top in ("$schema_comment",):
    data.pop(top, None)
for sub in data.values():
    if isinstance(sub, dict):
        sub.pop("_examples", None)
open(dst, "w").write(json.dumps(data, indent=2) + "\n")
PYEOF
  echo "       Test command not yet recorded — set baseline.tests.command and"
  echo "       re-run scripts/ci/check_test_ratchet.py to capture day-zero count."
fi

# ---------------------------------------------------------------------
# Step 7: Install git hooks (optional)
# ---------------------------------------------------------------------

if [[ "$INSTALL_HOOKS" -eq 1 ]] && [[ -d "$PROJECT_ROOT/.claude/hooks" ]]; then
  echo "[7/9] Installing git hooks ..."
  git_hooks_dir="$(git -C "$PROJECT_ROOT" rev-parse --git-path hooks)"
  mkdir -p "$git_hooks_dir"
  # Stable, unambiguous marker so re-runs recognise our own bridge and can
  # UPDATE it (e.g. to ship a hook security fix), while still refusing to
  # clobber a genuinely foreign hook. The marker is matched with `grep -qF`
  # against the exact string we write — no case-sensitivity trap.
  local hook_marker="agentile-hook-bridge"
  install_hook() {
    local src="$1" dst_name="$2"
    local dst="$git_hooks_dir/$dst_name"
    if [[ -f "$dst" ]] && ! grep -qF "$hook_marker" "$dst" 2>/dev/null; then
      echo "       Existing $dst_name hook at $dst — leaving in place; agentile hook NOT installed."
      return
    fi
    local action="Installed"
    [[ -f "$dst" ]] && action="Updated"
    cat > "$dst" <<EOF
#!/usr/bin/env bash
# ${hook_marker} v1 — invokes the script in .claude/hooks/.
exec "\$(git rev-parse --show-toplevel)/$src" "\$@"
EOF
    chmod +x "$dst"
    echo "       $action $dst_name -> $src"
  }
  install_hook ".claude/hooks/pre-commit-frontmatter.sh"   pre-commit
  install_hook ".claude/hooks/pre-commit-claim-grade.sh"   commit-msg
  install_hook ".claude/hooks/post-commit-journal-prompt.sh" post-commit
else
  echo "[7/9] Skipping git-hooks install (use --no-hooks=0 or rerun without --no-hooks)."
fi

# ---------------------------------------------------------------------
# Step 8: Index
# ---------------------------------------------------------------------

if [[ -x "$PROJECT_ROOT/scripts/index/build_agentile_index.py" ]]; then
  echo "[8/9] Building .agentile/INDEX/ ..."
  "$PROJECT_ROOT/scripts/index/build_agentile_index.py" >/dev/null
  echo "       Done. See .agentile/INDEX/INDEX_CHRONOLOGICAL.md."
else
  echo "[8/9] Indexer not found; skipping."
fi

# ---------------------------------------------------------------------
# Step 9: Commit
# ---------------------------------------------------------------------

echo "[9/9] Staging bootstrap changes ..."
git -C "$PROJECT_ROOT" add -A 2>/dev/null || true
if [[ -z "$(git -C "$PROJECT_ROOT" diff --cached --name-only 2>/dev/null)" ]]; then
  echo "       Nothing to commit."
else
  if confirm "Commit the bootstrap now?"; then
    # Report the ACTUAL git-commit exit status. A failing commit hook
    # (e.g. a pre-commit that rejects the change) must not be masked by a
    # cheerful "Bootstrap complete." at the end — surface it here.
    if git -C "$PROJECT_ROOT" commit -m "chore: bootstrap from agentile-skeleton ${SKELETON_VERSION}

- Project: ${PROJECT_NAME}
- License: ${LICENSE_KIND}
- Languages: ${LANGUAGES}
- Day zero: ${DAY_ZERO_DATE} @ ${DAY_ZERO_COMMIT:0:8}
" >/dev/null; then
      echo "       Committed."
    else
      echo "       ERROR: 'git commit' failed (exit $?). Bootstrap changes remain STAGED." >&2
      echo "       Resolve the failure (often a commit hook) and commit manually." >&2
      exit 1
    fi
  else
    echo "       Skipped commit. Review staged changes and commit manually."
  fi
fi

# ---------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------

cat <<DONE

==================================================================
  Bootstrap complete.
==================================================================

Next:
  1. Read .agentile/AGENT_ENTRY.md end-to-end (~10 min)
  2. Edit .agentile/CONFIG.md and .agentile/PRODUCT_SPEC.md to fill
     in placeholders (Sprint 0 walks through this)
  3. Set baseline.tests.command in .agentile/coverage/baseline.json
     to your project's canonical test count command
  4. Open the seeded Sprint 0:
       .agentile/sprints/active/${DAY_ZERO_DATE}-sprint-0-bootstrap/SPRINT.md
  5. Follow Sprint 0's WPs to complete the adoption.

Quick reference:
  scripts/sprint.sh status        # See active sprints + CURRENT.md head
  scripts/sprint.sh kickoff <id>  # Start a new sprint
  scripts/sprint.sh index         # Regenerate .agentile/INDEX/
  scripts/ci/check_frontmatter.py # Run Rule 12 check locally

DONE
