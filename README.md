# Agentile

> Institutional methodology for human-agent software engineering.
> Cloneable starter — foundation tier, four CI ratchets, named failure
> modes catalog, agent-agnostic interface, and bindings for Claude Code.

Agentile is the workflow that built the [Citrate](https://github.com/SaulBuilds/citrate)
Layer-1 blockchain in 4 months with one engineer plus an AI. The
artifact is not the blockchain. The artifact is the workflow that made
it possible — extracted here so it can travel.

> **Status: v0.1.0-rc1** — foundation tier landed. Templates,
> indexers, CI tripwires, AI grading, human eval, benchmark harness,
> Claude tuning, and `bootstrap.sh` are coming in subsequent phases.
> See `.agentile/planset/2026-04-30-agentile-skeleton/06_ROLLOUT.md`
> in the parent project for the build plan, or the issue tracker
> here once it's enabled.

---

## What's inside

```
.agentile/                    # Pre-populated framework
  SPIRIT.md, SOUL.md,         # Foundation tier — verbatim portable
  AGENT.md, AGENT_ENTRY.md
  rules/CORE_RULES.md         # 12 enforceable rules, BLOCKER/GATE
  docs/methodology/            # The synthesis: METHODOLOGY, FAILURE_MODES, CHRONOLOGY
  templates/                   # SPRINT, DAILY, RETRO, AUDIT, ADR, JOURNAL, ESSAY, CASE_STUDY
  workflows/                   # FEATURE, AUDIT_DRIVEN, REMEDIATION_TRACK, CEREMONY
  sprints/                     # active/, completed/, archived/, backlog/
  audits/                      # immutable dated audit reports
  formal/                      # TLA+ spec workflow
  coverage/                    # Test-count baselines + gate definitions

.claude/                       # Claude Code tuning (Phase 6)
scripts/                       # Indexers, CI checks, AI grading, benchmarks (Phases 3-5)
.github/workflows/             # CI ratchet + tripwire enforcement (Phase 4)
```

---

## Quick start (placeholder — fills in at Phase 6)

```bash
# Clone and bootstrap a new project
git clone https://github.com/CitrateNetwork/agentile.git my-project
cd my-project
./bootstrap.sh    # interactive setup — fills in CONFIG.md + PRODUCT_SPEC.md
```

Until `bootstrap.sh` ships in Phase 6, you can adopt the skeleton
manually:

1. Clone this repo.
2. Read `.agentile/AGENT_ENTRY.md` end-to-end.
3. Fill in `.agentile/CONFIG.md.template` → `.agentile/CONFIG.md`.
4. Fill in `.agentile/PRODUCT_SPEC.md.template` → `.agentile/PRODUCT_SPEC.md`.
5. Author your first sprint under `.agentile/sprints/active/YYYY-MM-DD-sprint-0-bootstrap/SPRINT.md`.
6. Commit; you've started.

---

## Why "Agentile"

Agile workflows assume a team of humans. Agentile workflows assume a
team of humans **and** agents — and lean into the failure modes that
specifically arise when agents generate plausible code faster than
humans can review it.

The methodology is documented in `.agentile/docs/methodology/`. The
single most important file is
`.agentile/docs/methodology/METHODOLOGY.md` (top-level synthesis).
The single most actionable file for new projects is
`.agentile/docs/methodology/04_FAILURE_MODES.md` (catalog of named
anti-patterns with enforcement surfaces).

---

## License

MIT — see [LICENSE](LICENSE).

## Acknowledgments

This skeleton is the institutional output of the Citrate project
(Saul Loveman + Claude). The foundation tier (SPIRIT/SOUL/AGENT/CORE_RULES)
was authored in the Cnidarian Foundation context for that project.
TLA+ as a discipline was suggested early by Hawkeye. The Wittgenstein
framing came out of a session in March 2026 about mock persistence.
The methodology folder you're reading was synthesized 2026-04-30.

If you use this and improve it, send a PR. If you fork it for a
different domain, please link back so others can find your variant.
