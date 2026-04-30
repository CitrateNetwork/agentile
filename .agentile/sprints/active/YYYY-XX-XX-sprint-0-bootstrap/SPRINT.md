---
created: 2026-04-30T05:00:00Z
branch: main
author: agentile-skeleton
sprint: S-0
status: template
---

<!--
SPRINT 0 BOOTSTRAP — Agentile.

This is a TEMPLATE sprint shipped with the skeleton. The folder
name uses placeholder dates (YYYY-XX-XX) on purpose: bootstrap.sh
(Phase 6 of the skeleton rollout) renames this folder to the
project's actual day-zero date and sets the frontmatter `status`
to `active`.

If you are reading this in your own project and the folder is
still named `YYYY-XX-XX-sprint-0-bootstrap`, you have not yet
run bootstrap. Either:
  1. Run bootstrap.sh, OR
  2. Rename this folder manually to today's date and update the
     frontmatter `status` to `active`.

Sprint 0 is intentionally mechanical. Its job is to fill in the
project-specific fields the skeleton can't pre-fill — chain ID,
test commands, baseline numbers, the project's own first journal —
so that Sprint 1 can begin without bootstrap exercises consuming
its time.
-->

# Sprint S-0: Bootstrap

## Sprint Metadata

| Field | Value |
|-------|-------|
| **Sprint ID** | S-0 |
| **Sprint Name** | Bootstrap — adopt the agentile skeleton in this project |
| **Goal** | Fill in CONFIG.md, PRODUCT_SPEC.md, and BASELINE.md so the framework knows what project it's running in. Author the project's first journal. End in a state where Sprint 1 can begin under FEATURE.md without bootstrap exercises. |
| **Branch** | `chore/agentile-bootstrap` (or per project convention) |
| **Start Date** | YYYY-MM-DD |
| **End Date (target)** | YYYY-MM-DD (typically same day or next day) |
| **Status** | NOT STARTED — bootstrap.sh has not yet replaced this placeholder |

## Why this sprint

The agentile skeleton is project-agnostic. It ships with templates
and workflows but does not know your project's chain ID, your
project's test commands, or your project's day-zero numbers.
Sprint 0 is the one-time exercise that puts those values in the
right places. After it closes, every subsequent sprint can run
under the standard `FEATURE.md` / `AUDIT_DRIVEN.md` / etc.
workflows without further bootstrap overhead.

## Test Baseline (start of sprint)

The whole point of this sprint is to produce a real baseline. At
sprint start the values below are placeholders; WP-0.4 fills them
in.

| Metric | Count | Captured | Canonical command |
|--------|-------|----------|-------------------|
| **Tests** | TBD (WP-0.4) | — | TBD (WP-0.4) |
| **Formal specs** | TBD (WP-0.4) | — | TBD (WP-0.4) |
| **CI tripwires** | TBD (WP-0.4) | — | TBD (WP-0.4) |
| **Frontmatter coverage** | TBD (WP-0.4) | — | TBD (WP-0.4) |

## Method

Bootstrap is configuration work, not feature work. The standard
TLA+ → BDD → RED → GREEN sequence does not apply here. WPs
proceed in numeric order; each unblocks the next.

## Work Packages

### WP-0.1: Read foundation tier

| Field | Value |
|-------|-------|
| **Status** | `[ ] NOT STARTED` |
| **Estimated effort** | S |
| **Commit(s)** | — |

**Scope:**
The agentile foundation tier (`SPIRIT.md`, `SOUL.md`, `AGENT.md`,
`AGENT_ENTRY.md`, `MANIFEST.md`, `rules/CORE_RULES.md`) defines
the operating norms that every contributor — human or AI — works
under. Read all six end-to-end before touching configuration. The
rules in `CORE_RULES.md` are not aspirational; they bind the
remaining WPs in this sprint and every WP after.

**Acceptance Criteria:**

- [ ] All six foundation files read (verifiable via session log
      or contributor confirmation)
- [ ] The contributor can name, from memory, the four ratchets
      (test count, formal specs, CI tripwires, frontmatter
      coverage) — pulled from `coverage/GATES.md`
- [ ] The contributor can name Rule 12 (frontmatter requirement)
      from `CORE_RULES.md` and apply it to every doc this sprint
      creates

**Tests added:** none — this WP delivers shared context, not code.

---

### WP-0.2: Fill in CONFIG.md from template

| Field | Value |
|-------|-------|
| **Status** | `[ ] NOT STARTED` |
| **Estimated effort** | S |
| **Commit(s)** | — |

**Scope:**
Copy `CONFIG.md.template` to `CONFIG.md` and fill in every
placeholder. CONFIG.md is the project's canonical-constants
document — chain ID, token name, VM, consensus parameters,
canonical commands. Tier-1 authority (see `AGENT_ENTRY.md`):
when any other document disagrees with CONFIG.md, CONFIG.md is
correct.

**Acceptance Criteria:**

- [ ] `CONFIG.md` exists with all placeholders replaced
- [ ] Rule-12 frontmatter present (`status: active`)
- [ ] Every constant has a single, unambiguous value (no "TBD"
      or "approximately X")
- [ ] If the project has external surfaces (RPC URLs, public
      explorer URLs, contract addresses), they are pinned with
      values that are CURRENT, not aspirational
- [ ] `CONFIG.md.template` is left in place — do NOT delete the
      template, future sessions may need to compare

**Tests added:** none.

---

### WP-0.3: Fill in PRODUCT_SPEC.md from template

| Field | Value |
|-------|-------|
| **Status** | `[ ] NOT STARTED` |
| **Estimated effort** | M |
| **Commit(s)** | — |

**Scope:**
Copy `PRODUCT_SPEC.md.template` to `PRODUCT_SPEC.md` and fill in
the project's product definition. PRODUCT_SPEC.md is what defines
"in scope" vs. "out of scope" for every future sprint — Tier 1
authority. If a feature isn't in PRODUCT_SPEC.md, it's not in
scope.

The temptation is to write the spec as a wishlist. Resist. Spec
the *finished* product as you understand it today; aspirational
work goes in the backlog or planset, not the spec.

**Acceptance Criteria:**

- [ ] `PRODUCT_SPEC.md` exists with all placeholders replaced
- [ ] Rule-12 frontmatter present
- [ ] Every named feature has a one-line description that names
      the data source (Rule 11) — what the feature reads, where
      it writes, what it returns
- [ ] Out-of-scope section explicitly lists at least three things
      the project deliberately does NOT do (this prevents scope
      creep more than the in-scope list does)
- [ ] `PRODUCT_SPEC.md.template` is left in place

**Tests added:** none.

---

### WP-0.4: Capture day-zero baselines in BASELINE.md

| Field | Value |
|-------|-------|
| **Status** | `[ ] NOT STARTED` |
| **Estimated effort** | M |
| **Commit(s)** | — |

**Scope:**
Copy `coverage/BASELINE.md.template` to `coverage/BASELINE.md`
and fill in the day-zero numbers and canonical commands for all
four ratchets:

1. **Test count** — pick the project's primary language(s) and
   test runners. Record the exact command(s) and the count they
   produce on the day-zero commit.
2. **Formal specs** — count `.tla` specs that pass TLC. If the
   project is starting with zero specs, record 0 and the empty-
   inventory `SPEC_INDEX.md`.
3. **CI tripwires** — count active regression-prevention rules in
   the project's CI. If starting from zero, record 0.
4. **Frontmatter coverage** — run the canonical command on the
   `.agentile/` directory. Most files at day zero will already be
   covered (the skeleton ships with frontmatter on every doc);
   any uncovered files are pre-rule artifacts the project owner
   wants to backfill or accept as historical.

**Acceptance Criteria:**

- [ ] `coverage/BASELINE.md` exists with all four ratchets filled
- [ ] Each ratchet's canonical command is reproducible — paste
      it into a fresh shell, verify it produces the documented
      number
- [ ] Day-zero commit hash recorded
- [ ] `BASELINE.md.template` is left in place
- [ ] `SPRINT.md` "Test Baseline (start of sprint)" table for
      THIS sprint (S-0) is updated with the captured numbers

**Tests added:** none — but this WP is what *enables* the test
ratchet to function from sprint S-1 onward.

---

### WP-0.5: Author the project's first journal

| Field | Value |
|-------|-------|
| **Status** | `[ ] NOT STARTED` |
| **Estimated effort** | S |
| **Commit(s)** | — |

**Scope:**
Copy `templates/JOURNAL_TEMPLATE.md` to
`.agentile/docs/journals/YYYY-MM-DDTHHMM_bootstrap.md` (using the
real date and time). Write the project's first journal entry —
the one that captures *why this project exists* and *what it
expects to deliver*. This is the project's chronological zero.

The journal is short — one screen. It's not a manifesto, not a
business plan. It's the durable answer to "what was this project
trying to do?" that future sessions and future contributors can
read in two minutes.

**Acceptance Criteria:**

- [ ] Journal file exists at the dated path
- [ ] Filename ISO timestamp matches frontmatter `created` to
      the minute
- [ ] Rule-12 frontmatter present (`status: active`)
- [ ] All five JOURNAL_TEMPLATE fields populated (Context, What
      happened, What I learned, What I'd do differently, Open
      questions)
- [ ] Length: one to three screens. If it's longer, it should
      probably be an essay instead.

**Tests added:** none.

---

### WP-0.6: Kick off Sprint 1

| Field | Value |
|-------|-------|
| **Status** | `[ ] NOT STARTED` |
| **Estimated effort** | S |
| **Commit(s)** | — |

**Scope:**
Move this S-0 sprint folder from `sprints/active/` to
`sprints/completed/` (after writing this sprint's RETRO.md), and
follow `workflows/SPRINT_LIFECYCLE.md` Phase 1 to kick off Sprint
1 against whatever the project's first real work item is.

Sprint 1's goal comes from the project — not from the skeleton.
Likely candidates: implementing the first feature in
PRODUCT_SPEC.md, closing a day-zero audit, or hardening an
existing prototype to meet `CORE_RULES.md`. Pick one and proceed.

**Acceptance Criteria:**

- [ ] `RETRO.md` written for S-0 using `templates/RETRO_TEMPLATE.md`
- [ ] S-0 folder moved to `.agentile/sprints/completed/`
- [ ] S-1 folder created in `.agentile/sprints/active/` with a
      filled-in `SPRINT.md`
- [ ] `sprints/CURRENT.md` updated to point at S-1
- [ ] All four ratchet baselines snapshotted into S-1's
      `SPRINT.md`

**Tests added:** none — Sprint 1 is where real work begins.

---

## Dependencies

| Dependency | Status | Impact if blocked |
|------------|--------|-------------------|
| Project has chosen primary language(s) and test runner(s) | required | WP-0.4 cannot complete without a runnable test suite |
| Project has a public PRODUCT_SPEC concept (even if incomplete) | required | WP-0.3 cannot produce a real spec without a starting concept |
| `bootstrap.sh` (Phase 6 of skeleton rollout) has been run | optional | If not run, the contributor handles renames and frontmatter manually |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Contributor skips foundation tier reading | Med | High | WP-0.1 acceptance includes a recall check; do not let WP-0.2 begin without it |
| PRODUCT_SPEC over-promises (wishlist) | Med | Med | Reviewer compares spec against runnable code; everything in spec must be at least partially implementable in S-1 |
| Baselines captured against an unstable commit | Low | Med | Use the day-zero commit; if work is ongoing, freeze a checkpoint commit and use that |

## Notes

The skeleton ships with this Sprint 0 file pre-written so that the
first thing a new project owner reads is *the work to do*, not
the framework's mechanics. If the bootstrap experience surfaces
shortcomings in this template, update it directly — improvements
to S-0 benefit every project that adopts the skeleton next.
