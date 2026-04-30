---
created: 2026-04-30T03:50:00Z
branch: main
author: Saul Loveman + Claude Opus 4.7 (1M context)
status: active
---

# Agent Entry Point

> **Read this file first.** Every contributor — human or AI — starts here.

## Who Are You?

| If you are... | Go to... |
|---------------|----------|
| **A new contributor (human or AI)** | [Cold Start](#cold-start) below |
| **Returning to an active sprint** | [sprints/CURRENT.md](sprints/CURRENT.md) |

---

## Cold Start

If you have no prior context about this project:

1. **Read** [SPIRIT.md](SPIRIT.md) — the public rule-of-meaning layer.
2. **Read** [SOUL.md](SOUL.md) — the values guiding tradeoffs and learning.
3. **Read** [AGENT.md](AGENT.md) — how humans and agents interpret rules without drifting into private language.
4. **Read** [CONFIG.md](CONFIG.md) — canonical project constants (filled in by `bootstrap.sh`).
5. **Read** [PRODUCT_SPEC.md](PRODUCT_SPEC.md) — what the finished product does (filled in by `bootstrap.sh`).
6. **Read** [rules/CORE_RULES.md](rules/CORE_RULES.md) — non-negotiable operating rules.
7. **Check** [sprints/CURRENT.md](sprints/CURRENT.md) — what work is active right now.
8. **Check** [sprints/backlog/](sprints/backlog/) — what needs to be done next.
9. **Pick a task** from the current sprint or backlog.
10. **Follow** the relevant [workflow](workflows/) for execution.

**GATE: Do NOT write code until you have read SPIRIT.md, SOUL.md, AGENT.md, CONFIG.md, and CORE_RULES.md.**

---

## Project Overview

**This is a placeholder.** The bootstrap script
(`bootstrap.sh` at repo root) fills this section in from the answers
you give during initial project setup, including:

- Project name and one-line description
- Primary language(s) and toolchain
- Top-level architectural shape
- Test suite invocation (so the test-count ratchet works on day one)
- Whether TLA+ is in scope (informs `formal/` workflow)

For the finished product spec, see [PRODUCT_SPEC.md](PRODUCT_SPEC.md).
For canonical constants (versioned IDs, environment names, etc.), see
[CONFIG.md](CONFIG.md).

---

## Framework Structure

```
.agentile/
├── AGENT_ENTRY.md          # You are here
├── SPIRIT.md               # Public rule-of-meaning
├── SOUL.md                 # Values
├── AGENT.md                # Human/agent cooperation rules
├── CONFIG.md               # Canonical project constants (filled by bootstrap)
├── PRODUCT_SPEC.md         # What the finished product does (filled by bootstrap)
├── MANIFEST.md             # Index of framework files
├── rules/                  # Non-negotiable operating rules
├── workflows/              # Step-by-step execution procedures
├── templates/              # Copyable document templates
├── docs/                   # Living documentation + canonical essays
│   ├── methodology/        # The synthesis of how the workflow works
│   ├── journals/           # Sprint-boundary reflections
│   ├── essays/             # Conceptual arguments
│   ├── case_studies/       # Anchor-incident-driven lessons
│   └── reports/            # Generated artifacts
├── sprints/                # active/, completed/, archived/, backlog/
├── audits/                 # Dated audit reports (immutable)
├── coverage/               # Test-count baselines + gate definitions
├── formal/                 # TLA+ specs + verification workflow
├── INDEX/                  # .gitignored — generated chronological views
└── planset/                # Architecture decisions + executive docs
```

---

## The Golden Rules

1. **Plan before you code** — check `sprints/CURRENT.md`, follow the workflow.
2. **No stubs, no TODOs in production** — every line is production-ready (Rule 11).
3. **Test count only goes up** — the test ratchet never decreases (Rule 3).
4. **Audits are immutable** — dated directories, never edited after creation (Rule 6).
5. **The sprint file is authoritative for status** — not memory, not chat (Rule 9).
6. **Every document has a timestamp and branch** — Rule 12 frontmatter, no exceptions.

For the full rule set, see [rules/CORE_RULES.md](rules/CORE_RULES.md).
For the named-failure-mode catalog, see
[docs/methodology/04_FAILURE_MODES.md](docs/methodology/04_FAILURE_MODES.md).
For the synthesis of how it all works, see
[docs/methodology/METHODOLOGY.md](docs/methodology/METHODOLOGY.md).

---

## Document Timestamp Requirement (Rule 12)

**Every document you create** — journal, essay, case study, ADR, sprint
file, spec — MUST have this frontmatter:

```markdown
---
created: YYYY-MM-DDTHH:MM:SSZ
branch: <current git branch>
author: <your name or zooid>
sprint: <sprint ID if applicable>
status: active | superseded | archived
---
```

Documents without this frontmatter are pre-rule artifacts (or skeleton-
ported historical material) and should be treated as **historical
context only**, not current guidance. When in doubt about whether a
document reflects current state, check its `branch` and `status`
fields.

See [rules/CORE_RULES.md](rules/CORE_RULES.md) Rule 12 for the full
specification.

---

## Document Authority

Each topic has one authoritative document. When documents disagree, the
higher-authority file wins.

| Authority | Document | Scope |
|-----------|----------|-------|
| **Foundation** | [`SPIRIT.md`](SPIRIT.md) | Public institutional rule meaning; no-private-language governance |
| **Foundation** | [`SOUL.md`](SOUL.md) | Values and moral posture |
| **Foundation** | [`AGENT.md`](AGENT.md) | Human-agent cooperation model and rule interpretation |
| **Tier 1** | [`CONFIG.md`](CONFIG.md) | Canonical constants for this project |
| **Tier 1** | [`PRODUCT_SPEC.md`](PRODUCT_SPEC.md) | What the finished product does, module by module |
| **Tier 1** | [`rules/CORE_RULES.md`](rules/CORE_RULES.md) | Non-negotiable operating rules (0–12) |
| **Tier 2** | [`sprints/CURRENT.md`](sprints/CURRENT.md) | Live sprint status, scores, test counts |
| **Tier 2** | [`formal/SPEC_INDEX.md`](formal/SPEC_INDEX.md) | TLA+ spec inventory and verification status |
| **Tier 3** | Module / package READMEs | Per-module usage, API, test commands |
| **Tier 3** | Workflow + template docs | Operational procedures |
| **Historical** | `docs/essays/`, `docs/journals/` | Reflections and learnings — context, not governance |

If a README contradicts CONFIG.md, CONFIG.md is correct. If a guide
contradicts PRODUCT_SPEC.md, the spec is correct. If an execution rule
seems to conflict with the institution's intended meaning, read it back
through SPIRIT.md, SOUL.md, and AGENT.md before interpreting
optimistically. Essays and journals are never authoritative — they
document what was true at a point in time.
