# Changelog

Notable changes to the Agentile skeleton. Versioned per semver.

## [v0.3.0-rc1] — 2026-04-30

**Phase 3 (indexer scripts + sprint CLI).**

### Added

- **Indexer scripts** under `scripts/index/` (Python 3, no third-party
  deps), ported from the source project and sanitized for project-
  agnostic use:
  - `_common.py` — shared helpers: `find_project_root` walks upward
    for `.agentile/`, plus `parse_frontmatter` and `to_utc_iso`.
  - `build_agentile_index.py` — chronological index of every `.md`
    under `.agentile/`. Emits `INDEX_CHRONOLOGICAL.md`,
    `INDEX_BY_CATEGORY.md`, `INDEX_RAW.tsv`, and
    `NAMING_INCONSISTENCIES.md`.
  - `backfill_frontmatter.py` — adds Rule-12 frontmatter to docs
    that predate the rule, sourcing `created` from git first-commit
    time (filesystem mtime fallback for untracked files).
  - `build_rename_plan.py` / `apply_rename_plan.py` — plan-then-
    apply migration for journal/essay/case-study filenames to the
    `YYYY-MM-DDTHHMM_<slug>.md` convention.
  - `build_sprint_rename_plan.py` / `apply_sprint_rename_plan.py` /
    `rewrite_sprint_xrefs.py` — three-step sprint-folder rename
    pipeline with cross-reference rewrite (idempotent via
    negative-lookbehind regex).
  - `scripts/index/README.md` — when to run each script, output
    locations, sequencing rules, empty-`.agentile/` behavior.
- **Sprint CLI** at `scripts/sprint.sh` — agent-agnostic Bash wrapper:
  `kickoff <ID> <slug>` seeds a new active sprint from
  `templates/SPRINT_TEMPLATE.md` with frontmatter pre-filled;
  `daily` appends a dated entry to the active sprint's DAILY.md;
  `close` seeds RETRO.md and prints the close-out checklist;
  `index` and `backfill` proxy the underlying Python tools;
  `status` shows project root and active sprints.

### Notes

- All scripts auto-discover the project root by walking upward from
  their own location. Invoke from any working directory.
- Scripts handle empty / near-empty `.agentile/` gracefully — the
  skeleton itself was used as a smoke test (29 docs, 100% Rule-12
  coverage at day zero).
- `.agentile/INDEX/` outputs are auto-generated and gitignored;
  the directory's `.gitkeep` survives.
- No CI / GitHub Actions wiring this phase. CI tripwires and ratchet
  workflows ship in Phase 4.

## [v0.2.0-rc1] — 2026-04-30

**Phase 2 (templates + workflows + coverage gates + formal scaffold).**

### Added

- **Templates** under `.agentile/templates/` (9 starting points,
  all with Rule-12 frontmatter, `status: template`):
  - `SPRINT_TEMPLATE.md` — sprint scaffold with WPs, baselines,
    risk register; acceptance criteria require named data sources.
  - `DAILY_TEMPLATE.md` — append-only per-day progress entries.
  - `RETRO_TEMPLATE.md` — sprint close with metrics delta and
    honest-reporting prompts.
  - `AUDIT_TEMPLATE.md` — audit report with stable finding IDs,
    threat model, suggested tripwires, immutability banner.
  - `ADR_TEMPLATE.md` — architecture decision record, append-only
    once accepted.
  - `JOURNAL_TEMPLATE.md` — short-form session reflection with
    ISO-timestamped filename.
  - `ESSAY_TEMPLATE.md` — conceptual argument scaffold with
    explicit not-governance banner.
  - `CASE_STUDY_TEMPLATE.md` — anchor-incident-driven lesson with
    enforcement-surface section.
  - `TLA_SPEC_TEMPLATE.tla` + `TLA_SPEC_TEMPLATE.cfg` — bare-bones
    TLA+ pair pointing at `formal/VERIFICATION_WORKFLOW.md`.
- **Workflows** under `.agentile/workflows/`:
  - `SPRINT_LIFECYCLE.md` — kickoff → execute → daily → close
    base lifecycle.
  - `FEATURE.md` — default seven-step per-WP sequence (TLA+ → BDD
    → RED → GREEN → REFACTOR → adversarial → tripwire/journal).
  - `AUDIT_DRIVEN.md` — when the audit IS the WBS; tripwire-first
    closure pattern.
  - `REMEDIATION_TRACK.md` — multi-sprint RM-* track shape with
    cross-agent handoff discipline.
  - `CEREMONY.md` — production-reroll lifecycle: pre-flight, halt,
    wipe/migrate, rebuild, deploy, post-flight.
- **Coverage gates** under `.agentile/coverage/`:
  - `GATES.md` — the four ratchets (test count, formal specs, CI
    tripwires, frontmatter coverage), each with what it counts,
    canonical command shape, and BLOCKER/GATE enforcement.
  - `BASELINE.md.template` — per-project day-zero numbers, filled
    in by `bootstrap.sh`.
- **Formal verification scaffold** under `.agentile/formal/`:
  - `README.md` — what the directory is for and when to add a spec.
  - `VERIFICATION_WORKFLOW.md` — six-step method (identify state
    machine → spec → TLC → fix → implement → CI regression).
  - `SPEC_INDEX.md.template` — project-side spec inventory.
- **Sprint 0 bootstrap** under `.agentile/sprints/active/YYYY-XX-XX-sprint-0-bootstrap/SPRINT.md`
  — pre-written sprint with six mechanical WPs (read foundation,
  fill CONFIG, fill PRODUCT_SPEC, capture BASELINE, write first
  journal, kick off Sprint 1). Date placeholders are intentional —
  resolved by `bootstrap.sh` at adoption time.

### Notes

- All new documents carry Rule-12 frontmatter. Phase 4's CI ratchet
  for frontmatter coverage will gate this on every PR.
- Templates use `status: template`; living workflow / coverage /
  formal docs use `status: active`.
- No code authored this phase. Indexer scripts ship in Phase 3,
  CI tripwires in Phase 4.

## [v0.1.0-rc1] — 2026-04-30

**Phase 1 (foundation tier port).** First commit.

### Added
- `.agentile/SPIRIT.md`, `.agentile/SOUL.md`, `.agentile/AGENT.md`,
  `.agentile/AGENT_ENTRY.md`, `.agentile/MANIFEST.md` — foundation
  tier ported from `github.com/SaulBuilds/citrate` with frontmatter
  refreshed to `status: active`.
- `.agentile/rules/CORE_RULES.md` — 12 enforceable rules, BLOCKER/GATE
  severity, ported with a banner annotation about example commands
  being Citrate-specific.
- `.agentile/docs/methodology/METHODOLOGY.md` — top-level synthesis.
- `.agentile/docs/methodology/04_FAILURE_MODES.md` — catalog of named
  anti-patterns.
- `.agentile/docs/methodology/06_CHRONOLOGY.md` — example chronology
  (Citrate's 8 phases) for reference.
- `.agentile/docs/methodology/README.md` — folder index.
- `.agentile/CONFIG.md.template`, `.agentile/PRODUCT_SPEC.md.template`
  — project-specific tier-1 docs awaiting `bootstrap.sh`.
- Empty placeholder directories for `sprints/{active,completed,archived,backlog}/`,
  `audits/`, `docs/{journals,essays,case_studies,reports}/`,
  `formal/`, `INDEX/`, `planset/`.
- Top-level `README.md`, `CHANGELOG.md`, `.gitignore`.

### Pending (later phases)
- Phase 2: templates + workflows + coverage gates.
- Phase 3: indexer scripts ported from Citrate.
- Phase 4: CI tripwires + ratchet checks + Semgrep rules.
- Phase 5: AI grading + human eval + benchmark harness (shadow mode).
- Phase 6: Claude tuning (`.claude/`) + `bootstrap.sh` + INSTALL.md.

### Source
This skeleton was synthesized from the Citrate project's
`.agentile/` corpus (1,283 markdown documents accumulated 2025-12 → 2026-04).
The synthesis is recorded at
`https://github.com/SaulBuilds/citrate/tree/main/.agentile/docs/methodology`
and the planset that drove this skeleton's design at
`https://github.com/SaulBuilds/citrate/tree/main/.agentile/planset/2026-04-30-agentile-skeleton`.
