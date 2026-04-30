---
created: 2026-04-30T04:30:00Z
branch: main
author: Claude Opus 4.7 (1M context) — outgoing session
status: active
---

# Phase 2 Handoff — for the next Claude session

> **Read me first.** If you're a fresh Claude session being asked to
> start Phase 2 of the agentile skeleton build, this document is your
> ground truth. It's self-contained — you don't need to chase five
> other files. Pointers below are absolute paths.

## Who you are

You're a Claude Code session being asked to execute **Phase 2** of a
six-phase rollout to build the `agentile` skeleton repo at
`github.com/CitrateNetwork/agentile`. Phase 1 (foundation tier port +
methodology + boilerplate) is **done and pushed**. Your job is
templates + workflows + coverage gates.

This is the second of six phases. Each phase is sized to fit one
session. The plan was authored by the previous Claude session
(Opus 4.7, 1M context) on 2026-04-30 and lives in the source
repository.

## Where to read first (in order, ~15 minutes)

1. **This file**, end-to-end. It tells you everything.
2. `/home/saul/Projects/Mozi Group/citrate-old-history/citrate/.agentile/planset/2026-04-30-agentile-skeleton/06_ROLLOUT.md`
   — Phase 2 task list (lines containing "### Phase 2 — Templates")
   plus the locked decisions section (lines containing "## Decisions").
3. `/home/saul/Projects/Mozi Group/agentile/.agentile/AGENT_ENTRY.md`
   — the foundation tier entry point (so you know what you're working
   under).
4. `/home/saul/Projects/Mozi Group/agentile/.agentile/rules/CORE_RULES.md`
   — the 12 rules that bind your work. Pay particular attention to
   Rule 12 (frontmatter on every doc).

You do NOT need to read the full METHODOLOGY.md or 04_FAILURE_MODES.md
unless you hit a question this handoff doesn't answer.

## Where the repos are

- **Source repo** (Citrate, where the planset lives, do NOT modify):
  `/home/saul/Projects/Mozi Group/citrate-old-history/citrate/`
  — On `main` branch. Has the planset under
  `.agentile/planset/2026-04-30-agentile-skeleton/`.
- **Target repo** (agentile, where you commit your work):
  `/home/saul/Projects/Mozi Group/agentile/`
  — On `main` branch. Pushes to `github.com/CitrateNetwork/agentile`.
  License is MIT. Owner is Saul Loveman; he's an admin of CitrateNetwork.

The user's GitHub identity is `SaulBuilds`; gh CLI is authenticated
with `repo` scope.

## What's already done (Phase 1, commit `91087c2`)

```
agentile/
├── README.md                               # Quick-start placeholder
├── CHANGELOG.md                            # v0.1.0-rc1 entry
├── LICENSE                                 # MIT
├── .gitignore
├── .agentile/
│   ├── AGENT_ENTRY.md                      # Project-agnostic rewrite
│   ├── SPIRIT.md, SOUL.md, AGENT.md        # Verbatim from Citrate, frontmatter refreshed
│   ├── MANIFEST.md
│   ├── CONFIG.md.template
│   ├── PRODUCT_SPEC.md.template
│   ├── rules/
│   │   └── CORE_RULES.md                   # 12 rules, ported with banner annotation
│   ├── docs/
│   │   └── methodology/                    # 4 files (METHODOLOGY, 04_FAILURE_MODES,
│   │       │                                # 06_CHRONOLOGY, README), all with banners
│   │       └── (rest .gitkeep'd)
│   ├── sprints/
│   │   ├── CURRENT.md                      # Sprint 0 placeholder
│   │   ├── active/, completed/, archived/, backlog/  # all .gitkeep'd
│   ├── audits/.gitkeep
│   ├── coverage/                           # EMPTY — Phase 2 fills this
│   ├── formal/                             # EMPTY — Phase 2 fills this
│   ├── INDEX/.gitkeep
│   ├── planset/
│   │   └── 2026-04-30-phase-handoffs/
│   │       └── PHASE_2_HANDOFF.md          # ← you are here
│   ├── templates/                          # EMPTY — Phase 2 fills this
│   └── workflows/                          # EMPTY — Phase 2 fills this
├── .claude/                                # EMPTY — Phase 6
├── scripts/                                # EMPTY — Phases 3-5
└── .github/workflows/                      # EMPTY — Phase 4
```

## What you must produce (Phase 2)

Per `06_ROLLOUT.md` Phase 2 section. Land all of this in **one
commit** on `main`, push to `github.com/CitrateNetwork/agentile`.

### 1. Templates (`.agentile/templates/`)

Author each as a copyable starting point. Each template has Rule-12
frontmatter with `status: template` and placeholder fields the user
fills in.

| File | Purpose |
|---|---|
| `SPRINT_TEMPLATE.md` | New-sprint scaffold. Fields: goal, branch, WPs with WP-IDs, baseline metrics table (with the canonical commands), acceptance criteria with named data sources, risk register. |
| `DAILY_TEMPLATE.md` | Per-day-of-sprint progress entry. Fields: date, commits, tests-now/baseline, blockers, next-day plan. |
| `RETRO_TEMPLATE.md` | Sprint close. Fields: what worked, what didn't, what carries forward, ratchet deltas. |
| `AUDIT_TEMPLATE.md` | Audit report scaffold. Fields: findings table with file:line refs, threat-model statement, suggested tripwire form, severity. Banner reminding that `audits/` is immutable (Rule 6). |
| `ADR_TEMPLATE.md` | Architecture Decision Record. Standard ADR format (context, decision, consequences). |
| `JOURNAL_TEMPLATE.md` | Sprint-boundary reflection scaffold. Filename should already encode `YYYY-MM-DDTHHMM_<slug>.md`. |
| `ESSAY_TEMPLATE.md` | Conceptual argument scaffold. Same filename pattern. Banner warning that essays are historical context, not governance. |
| `CASE_STUDY_TEMPLATE.md` | Anchor-incident-driven lesson. Fields: anchor incident, indicators, enforcement surface, references. Same filename pattern. |
| `TLA_SPEC_TEMPLATE.tla` | Bare-bones TLA+ spec template + companion `.cfg` template. With comments pointing at `formal/VERIFICATION_WORKFLOW.md`. |

For each, look at how Citrate uses the equivalent file (under
`/home/saul/Projects/Mozi Group/citrate-old-history/citrate/.agentile/templates/`
and `.agentile/sprints/active/2026-04-29-sprint-rm-fl-5-hypothesis-rigs/SPRINT.md`
for a real recent example). Strip Citrate-specifics; preserve structure.

### 2. Workflows (`.agentile/workflows/`)

Five lifecycle docs. Source: `06_CHRONOLOGY.md` describes the
patterns, but you're authoring fresh — these aren't ported from a
specific Citrate workflow file because Citrate didn't always
externalize them this cleanly.

| File | What it specifies |
|---|---|
| `SPRINT_LIFECYCLE.md` | Standard kickoff → execute → daily → close pattern. The shape every sprint follows. |
| `FEATURE.md` | Standard feature sprint workflow (TLA+ → RED → impl → mutation → tripwire → commit, repeated per WP). |
| `AUDIT_DRIVEN.md` | When the audit IS the WBS. File:line refs become WPs directly. Per `2026-04-25T2230_AUDIT_DRIVEN_SPRINT.md` case study. |
| `REMEDIATION_TRACK.md` | Multi-sprint RM-* track pattern. Track-naming, per-finding scoping, cross-agent authorship. |
| `CEREMONY.md` | Production reroll lifecycle. Pre-flight, halt, wipe, rebuild, deploy contracts in dependency order, post-flight. Per the 2026-04-29 reroll experience documented in METHODOLOGY.md §6.4. |

Each workflow doc gets Rule-12 frontmatter with `status: active`.

### 3. Coverage gates (`.agentile/coverage/`)

| File | Content |
|---|---|
| `GATES.md` | Defines the four ratchets (test count, TLA+ specs, CI tripwires, frontmatter coverage). Per METHODOLOGY.md §4. Documents each ratchet's: name, what it counts, canonical command, where the baseline lives, what BLOCKER vs GATE response looks like. |
| `BASELINE.md.template` | Filled in by `bootstrap.sh` (Phase 6). Records the project's day-zero numbers. |

### 4. Formal verification scaffold (`.agentile/formal/`)

| File | Content |
|---|---|
| `README.md` | What `formal/` is for, when to add a TLA+ spec, link to TLA+ Toolbox install instructions. |
| `VERIFICATION_WORKFLOW.md` | The 6-step method (state machine identify → write spec → run TLC → fix spec → write code → regress) from METHODOLOGY.md §6.1. With invocation examples. |
| `SPEC_INDEX.md.template` | Bootstrap fills in. Records the project's spec inventory. |

### 5. Sprint 0 bootstrap template (`.agentile/sprints/active/`)

Pre-write a `2026-XX-XX-sprint-0-bootstrap/SPRINT.md` (with `XX` as a
placeholder the user fills in via bootstrap.sh) that walks them
through:

- WP-0.1: read foundation tier
- WP-0.2: fill in CONFIG.md from template
- WP-0.3: fill in PRODUCT_SPEC.md from template
- WP-0.4: pick the project's primary language(s) and record canonical
  test/spec/tripwire-count commands in `coverage/BASELINE.md`
- WP-0.5: write the project's first journal (`status: active`,
  in `docs/journals/`)
- WP-0.6: kick off Sprint 1

Each WP has acceptance criteria with named outputs. The point is to
make the first sprint mechanical so a new project owner doesn't have
to design their bootstrap.

### 6. CHANGELOG.md update

Append a `[v0.2.0-rc1] — 2026-04-XX` (or whenever you commit) entry
listing what Phase 2 added.

## Critical constraints (will trip you up if ignored)

1. **Rule 12 frontmatter on every new doc.** No exceptions. `status:`
   should be `template` for templates, `active` for everything else.
   The CI ratchets in Phase 4 will reject docs missing frontmatter.
2. **Don't modify the foundation tier.** SPIRIT.md, SOUL.md, AGENT.md,
   AGENT_ENTRY.md, MANIFEST.md, rules/CORE_RULES.md are Phase 1's
   work. Don't touch them. If you find a typo, fix it in a separate
   commit.
3. **Don't modify the methodology folder.** Same as above. The
   skeleton-port banners are intentional.
4. **Banner pattern for ported content.** When porting an example
   from Citrate, include a banner like:
   `> **Skeleton port note.** Examples below cite Citrate. Adapt to your project.`
5. **Filename conventions.**
   - Sprint folders: `YYYY-MM-DD-sprint-<track>-<id>-<slug>/`
   - Journals/essays/case studies: `YYYY-MM-DDTHHMM_<slug>.md`
   - Audit folders: `audits/YYYY-MM/YYYY-MM-DD-<slug>/`
   - Plansets (dated): `planset/YYYY-MM-DD-<slug>/`
6. **The Sprint 0 bootstrap template uses placeholder dates.** Don't
   resolve `YYYY-XX-XX` to today — that's the user's job. The
   placeholder is a feature, not a bug.
7. **Don't push `.agentile/INDEX/` content.** It's auto-generated.
   Just keep `.gitkeep`.
8. **Don't author code in this phase.** Phase 2 is documents only.
   Indexer scripts (Python) come in Phase 3. CI workflows (YAML)
   come in Phase 4.

## Locked decisions (from `06_ROLLOUT.md`)

| # | Question | Decision |
|---|---|---|
| 1 | License | MIT (already set) |
| 2 | Repo | `github.com/CitrateNetwork/agentile` (created) |
| 3 | Skeleton name | `agentile` |
| 4 | Versioning | Semver (currently `v0.1.0-rc1` post-Phase-1) |
| 5 | First-test-project | None planned — Saul will adopt skeleton in a real project later |
| 6 | Calibration period | 2 weeks for shadow-mode evals (Phase 5+) |
| 7 | Default merge gate | Shadow mode at v1.0.0; opt-in to hard mode |

These are locked. Don't second-guess.

## Source paths in Citrate (where to crib templates from)

```
/home/saul/Projects/Mozi Group/citrate-old-history/citrate/
├── .agentile/
│   ├── templates/                          # Some exist; check first
│   │   └── (whatever's there)
│   ├── workflows/                          # Some exist
│   ├── sprints/active/2026-04-29-sprint-rm-fl-5-hypothesis-rigs/SPRINT.md
│   │                                       # Best example of a mature sprint file
│   ├── docs/methodology/METHODOLOGY.md     # Workflow patterns in §6
│   └── docs/case_studies/2026-04-25T2230_AUDIT_DRIVEN_SPRINT.md
│                                           # Anchor for AUDIT_DRIVEN.md
└── runbooks/FEDERATED_LEARNING_NODE.md     # Example operational runbook
```

For each Phase 2 deliverable, glance at the Citrate equivalent (if
any), extract the structural pattern, then write fresh.

If a template doesn't have a Citrate counterpart (e.g.,
ESSAY_TEMPLATE.md — Citrate has essays but no template file for them),
write fresh based on the in-the-wild examples
(`.agentile/docs/essays/2026-04-29T1316_THE_CARPENTER_AND_THE_TAR.md`
is a representative recent essay; observe its structure).

## Checkpoint + commit pattern

Make ONE commit at the end of Phase 2 with all the work bundled.
Suggested message format:

```
Phase 2: templates + workflows + coverage gates + formal scaffold (v0.2.0-rc1)

Authors:
  - 9 templates under .agentile/templates/ (SPRINT, DAILY, RETRO,
    AUDIT, ADR, JOURNAL, ESSAY, CASE_STUDY, TLA_SPEC)
  - 5 workflow docs under .agentile/workflows/ (SPRINT_LIFECYCLE,
    FEATURE, AUDIT_DRIVEN, REMEDIATION_TRACK, CEREMONY)
  - .agentile/coverage/GATES.md + BASELINE.md.template
  - .agentile/formal/{README,VERIFICATION_WORKFLOW,SPEC_INDEX.md.template}
  - .agentile/sprints/active/<date>-sprint-0-bootstrap/SPRINT.md
  - CHANGELOG.md updated

[Co-Authored-By line]
```

Push: `git push origin main`.

After push, update task #81 to completed via TaskUpdate (status:
completed) and queue Phase 3 by marking #82 as in_progress in the
NEXT session.

## Who's tracking the phases

The parent project (Citrate) has TaskCreate-tracked phases #80-#85
for the six rollouts. Phase 2 = task #81. After your commit, set
that task to completed.

Tasks live in the parent project's session, not the agentile repo.
Don't try to read them — they're surfaced in your session
automatically when you start.

## Questions you may have

**Q: Should I author tests for the templates?**
A: No. Templates are markdown. They get exercised when a project
adopts the skeleton and uses them. Phase 4 will add CI checks that
ensure new docs have frontmatter (which is the only "test" that
applies to templates).

**Q: How do I handle TLA_SPEC_TEMPLATE.tla? I don't have TLA+ tools.**
A: You're authoring a template file, not running TLC. Just author
the .tla syntax with placeholders and a `.cfg.template` companion.
The Citrate repo has many `.tla` files at
`/home/saul/Projects/Mozi Group/citrate-old-history/citrate/citrate_v0.01.1/specs/tla/`
to reference. Pick a small one, generalize.

**Q: How long should each template be?**
A: Templates should be short (<200 lines) and high-signal. The user
will copy and modify; verbose templates are noisy. Look at how
Citrate's `templates/SPRINT_TEMPLATE.md` is structured if it exists,
otherwise model on its `.agentile/sprints/active/2026-04-29-sprint-rm-fl-5-hypothesis-rigs/SPRINT.md`
content stripped of project-specifics.

**Q: What if I get partway through and run out of context?**
A: Commit what you have with a descriptive message, write a
`PHASE_2_PARTIAL_HANDOFF.md` in this same dir (this handoff dir),
and stop. Better to land 50% with a clear handoff than 80% in a fog.

## Final checklist before commit

- [ ] All 9 templates exist in `.agentile/templates/` with Rule-12
      frontmatter.
- [ ] All 5 workflow docs in `.agentile/workflows/`.
- [ ] `.agentile/coverage/GATES.md` exists.
- [ ] `.agentile/coverage/BASELINE.md.template` exists.
- [ ] `.agentile/formal/{README,VERIFICATION_WORKFLOW}.md` exist.
- [ ] `.agentile/formal/SPEC_INDEX.md.template` exists.
- [ ] Sprint 0 bootstrap directory + SPRINT.md exists.
- [ ] CHANGELOG.md has a `[v0.2.0-rc1]` entry.
- [ ] `git status` shows no unintended modifications to Phase 1 files.
- [ ] One bundled commit; pushed to origin/main.

When the checklist is green, you're done with Phase 2. The next
session will read this same dir's `PHASE_3_HANDOFF.md` (which you can
optionally seed if you have spare cycles, but don't have to).

Good luck.

— Outgoing Claude session, 2026-04-30T04:30:00Z
