# Changelog

Notable changes to the Agentile skeleton. Versioned per semver.

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
