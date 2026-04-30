# Agentile

> Institutional methodology for human-agent software engineering.
> Cloneable starter — foundation rules, four CI ratchets, named
> failure modes catalog, an agent-agnostic interface, and bindings
> for Claude Code.

Agentile is the workflow that built the [Citrate](https://github.com/SaulBuilds/citrate)
Layer-1 blockchain in 4 months with one engineer plus an AI. The
artifact is not the blockchain. The artifact is the workflow that
made it possible — extracted here so it can travel.

> **Status: v1.0.0-rc1.** Foundation tier, templates, indexers, CI
> tripwires + ratchets, AI grading, human eval, benchmark harness,
> Claude tuning, and `bootstrap.sh` are all in place. Bumping to
> v1.0.0 after the first real-project adoption.

---

## Quick start

```bash
# Clone the skeleton into a fresh directory and bootstrap a new project.
git clone https://github.com/CitrateNetwork/agentile.git my-project
cd my-project
./bootstrap.sh
```

`bootstrap.sh` walks you through:

1. Project name, description, languages, license
2. Filling in `.agentile/CONFIG.md` and `.agentile/PRODUCT_SPEC.md`
3. Generating `CLAUDE.md` from the template
4. Renaming the Sprint 0 placeholder folder to today's date
5. Capturing day-zero baselines into `coverage/baseline.json`
6. Installing git hooks (optional)
7. Seeding `.agentile/INDEX/` chronological index
8. Committing the bootstrap

Total time: ≈ 5 minutes. After that, follow the seeded Sprint 0
walk-through in
`.agentile/sprints/active/<today>-sprint-0-bootstrap/SPRINT.md`.

For a detailed walkthrough including first-sprint planning, see
[`INSTALL.md`](INSTALL.md).

---

## What's inside

```
.agentile/                    Pre-populated framework
  SPIRIT.md, SOUL.md,         Foundation tier — verbatim portable
  AGENT.md, AGENT_ENTRY.md
  rules/CORE_RULES.md         13 enforceable rules, BLOCKER/GATE
  docs/methodology/           METHODOLOGY, FAILURE_MODES, CHRONOLOGY
  templates/                  9 starting points (SPRINT, JOURNAL, ADR, …)
  workflows/                  FEATURE, AUDIT_DRIVEN, REMEDIATION_TRACK,
                              CEREMONY, SPRINT_LIFECYCLE
  sprints/                    active/, completed/, archived/, backlog/
  audits/                     immutable dated audit reports
  formal/                     TLA+ spec workflow + index
  coverage/                   GATES.md + baseline.json + BASELINE.md

.claude/                      Claude Code tuning
  CLAUDE.md.template          project-level guidance, filled by bootstrap
  commands/                   /sprint, /journal, /essay, /case-study,
                              /claim-grade, /ratchet-check, /audit-drive
  agents/                     methodology-guide, tripwire-author,
                              claim-grader, journal-coach
  hooks/                      pre-commit-frontmatter, pre-commit-claim-grade,
                              pre-merge-data-source, post-commit-journal-prompt
  settings.json.template      seeded by bootstrap (gitignored target)

scripts/                      Agent-agnostic primitives
  index/                      chronological indexer + rename pipeline
  ci/                         frontmatter, no-unwraps, no-mocks, ratchets,
                              audit-immutability checks
  semgrep/                    AST-grade tripwires (5 starter rules)
  ai/                         claim-grader prompt + runners
  eval/                       human-eval protocol, data-source heuristic,
                              benchmark harness + regression check
  sprint.sh                   agent-agnostic sprint CLI

.github/workflows/            CI enforcement
  lint-frontmatter.yml        Rule 12 on PR-changed .md
  lint-workflows.yml          actionlint
  ratchet-check.yml           all four ratchets
  tripwires.yml               semgrep + python tripwires
  audit-immutability.yml      Rule 6 on .agentile/audits/**
  claim-grade.yml             AI claim grader (shadow mode)
  data-source-check.yml       Rule 11 heuristic (shadow mode)
  benchmark-nightly.yml       perf harness + regression (shadow mode)

bootstrap.sh                  one-command project setup
INSTALL.md                    detailed walkthrough
CHANGELOG.md                  semver history
LICENSE                       MIT
```

---

## The four ratchets

Once a project is bootstrapped, CI enforces four numbers that can
only go up:

| # | Ratchet | What it counts |
|---|---------|----------------|
| 1 | **Test count** | Total passing tests (Rule 3) |
| 2 | **Formal specs** | TLA+ specs that pass TLC (Rule 10) |
| 3 | **CI tripwires** | Active regression-prevention rules |
| 4 | **Frontmatter coverage** | Fraction of `.md` with Rule-12 frontmatter |

A merge that drops any of them is a BLOCKER. The whole framework
is designed around that asymmetry: it's easy to add quality, hard
to silently subtract it.

See [`.agentile/coverage/GATES.md`](.agentile/coverage/GATES.md)
for the model.

---

## The 13 rules

Defined in [`.agentile/rules/CORE_RULES.md`](.agentile/rules/CORE_RULES.md):

| # | Rule | Severity |
|---|------|----------|
| 0 | Read AGENT_ENTRY.md first | BLOCKER |
| 1 | Plan before you code | GATE |
| 2 | No mocks/stubs/TODOs | GATE |
| 3 | Test ratchet (count never decreases) | BLOCKER |
| 4 | Every feature traces to a sprint item | GATE |
| 5 | Clippy clean + zero unwraps | GATE |
| 6 | Audits are immutable | BLOCKER |
| 7 | Docs accompany code changes | GATE |
| 8 | Security changes need review | BLOCKER |
| 9 | Sprint file is source of truth | GATE |
| 10 | Formal verification for consensus | GATE |
| 11 | Mock budget = 0; data source tracing | GATE |
| 12 | All docs have timestamps + branch context | GATE |

Each rule has a "verification" section (how CI proves it) and an
"on violation" section (BLOCKER vs GATE response).

---

## Why "Agentile"

Agile workflows assume a team of humans. Agentile workflows assume
a team of humans **and** agents — and lean into the failure modes
that specifically arise when agents generate plausible code faster
than humans can review it.

The methodology is documented in `.agentile/docs/methodology/`. The
single most actionable file for new projects is
[`.agentile/docs/methodology/04_FAILURE_MODES.md`](.agentile/docs/methodology/04_FAILURE_MODES.md)
(catalog of named anti-patterns with enforcement surfaces).

---

## Adoption checklist

- [ ] Clone the skeleton
- [ ] Run `./bootstrap.sh`
- [ ] Read `.agentile/AGENT_ENTRY.md` end-to-end
- [ ] Edit `.agentile/CONFIG.md` to fill in canonical constants
- [ ] Edit `.agentile/PRODUCT_SPEC.md` to define the finished product
- [ ] Set `baseline.tests.command` in
      `.agentile/coverage/baseline.json` to your project's
      canonical test count command
- [ ] Open the seeded Sprint 0 and walk through WPs 0.1–0.6
- [ ] Kick off Sprint 1 against your first real feature

If your project has pre-existing audits, code, or sprint history,
the indexer scripts in `scripts/index/` can backfill frontmatter
on legacy docs and propose chronological renames. See
[`scripts/index/README.md`](scripts/index/README.md).

---

## Non-Claude tools

Everything in `.claude/` is convenience for Claude Code. The
methodology runs without Claude:

- `scripts/sprint.sh` — agent-agnostic sprint CLI (kickoff, daily,
  close, status)
- `scripts/ci/check_*.py` — every ratchet and tripwire as a
  standalone Python script
- `scripts/semgrep/*.yaml` — AST-grade rules invoked by `semgrep`
- `scripts/ai/grade_claim.py` — auto-falls back to OpenAI or no-op
  if Anthropic key is absent

A team using Codex / Cursor / GPT-5 / Aider can adopt the same
framework — they just don't get the slash commands.

---

## License

MIT — see [LICENSE](LICENSE).

## Acknowledgments

This skeleton is the institutional output of the Citrate project
(Saul Loveman + Claude). The foundation tier (SPIRIT/SOUL/AGENT/
CORE_RULES) was authored in the Cnidarian Foundation context for
that project. TLA+ as a discipline was suggested early by
Hawkeye. The Wittgenstein framing came out of a session in
March 2026 about mock persistence. The methodology folder was
synthesized 2026-04-30.

If you use this and improve it, send a PR. If you fork it for a
different domain, please link back so others can find your
variant.
