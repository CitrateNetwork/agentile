# Changelog

Notable changes to the Agentile skeleton. Versioned per semver.

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
