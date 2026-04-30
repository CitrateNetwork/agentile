---
created: 2026-04-30T05:00:00Z
branch: main
author: agentile-skeleton
status: template
---

<!--
SPRINT TEMPLATE — Agentile.

Copy this file to:
  .agentile/sprints/active/YYYY-MM-DD-sprint-<track>-<id>-<slug>/SPRINT.md

Then:
  1. Replace placeholders (anything in <ANGLE_BRACKETS> or PLACEHOLDER_*)
  2. Update frontmatter: created, branch, author, sprint, status: active
  3. Snapshot baseline metrics on day 0 (see "Test Baseline" below)
  4. Author one WP block per work package (copy WP-1 as a starting point)
  5. Every WP acceptance criterion MUST name its data source (Rule 11)
  6. When the sprint closes, move the directory to .agentile/sprints/completed/
     and add RETRO.md and (if used) REPORT.md alongside this file
-->

# Sprint <ID>: <NAME>

## Sprint Metadata

| Field | Value |
|-------|-------|
| **Sprint ID** | `<TRACK>-<ID>` (e.g. `RM-A-3`, `S-7`, `FEAT-AUTH`) |
| **Sprint Name** | <one-line name> |
| **Goal** | <One sentence. The single outcome that determines success.> |
| **Branch** | `<branch-name>` |
| **Start Date** | YYYY-MM-DD |
| **End Date (target)** | YYYY-MM-DD |
| **Status** | `KICKED OFF` / `IN PROGRESS` / `REVIEW` / `COMPLETE` / `BLOCKED` |
| **Planset** | <relative path to planset doc, if any> |
| **Predecessors** | <list closed sprints whose work this builds on, with closing commit hashes> |

## Why this sprint

<2–4 sentences. What problem this sprint exists to solve, and why it
needs to happen now. If the sprint is part of a multi-sprint track,
state the track-level goal and where this sprint sits in it.>

## Deliverables

<Bulleted list of named, inspectable artifacts. Specs, crates, files,
endpoints, dashboards, runbooks. If a deliverable lands in another
sprint, name that sprint.>

- <Deliverable 1: file path or named artifact>
- <Deliverable 2>
- <Deliverable 3>

## Test Baseline (start of sprint)

<!--
Snapshot the canonical counts on day 0. Commands below are EXAMPLES —
record the canonical commands for YOUR project in
.agentile/coverage/BASELINE.md once at project setup, then quote them
here every sprint. The four ratchet axes are: tests, formal specs,
tripwires, frontmatter coverage.
-->

| Metric | Count | Captured | Canonical command |
|--------|-------|----------|-------------------|
| **Tests** | <N> | <commit> | `<test command from BASELINE.md>` |
| **Formal specs** | <N> | <date> | `<spec count command>` |
| **CI tripwires** | <N> | <date> | `<tripwire count command>` |
| **Frontmatter coverage** | <N>/<N> | <date> | `<coverage command>` |

## Method

For each WP: TLA+ (if state-machine touching) → BDD/Gherkin → failing
test + tripwire → code → refactor → adversarial check → journal entry.

If any step does not apply to a WP, document why in the WP block.

## Work Packages

### WP-1: <name>

| Field | Value |
|-------|-------|
| **Status** | `[ ] NOT STARTED` / `[~] IN PROGRESS` / `[x] COMPLETE` / `[!] BLOCKED` |
| **Order step** | <which method step this is> |
| **Estimated effort** | S / M / L / XL |
| **Commit(s)** | — (filled at completion) |

**Scope:**
<2–4 sentences. What this WP delivers and the boundary of what it
does NOT cover.>

**Acceptance Criteria** *(every criterion names its data source — Rule 11)*

- [ ] <Specific, testable condition. e.g. "Frontend X displays Y from
      contract Z via method W, verified by integration test
      `tests/integration_x.rs::test_y_from_z`">
- [ ] <Criterion 2>
- [ ] <Criterion 3>

**Tests added:**
- <test name> — <what it verifies>

---

### WP-2: <name>

_(Copy the WP-1 block. Add as many as the sprint needs.)_

---

## Dependencies

| Dependency | Status | Impact if blocked |
|------------|--------|-------------------|
| <named dependency> | Available / Blocked | <which WPs are affected> |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| <risk> | Low / Med / High | Low / Med / High | <strategy> |

## Notes

<Free-form. Decisions made mid-sprint, deferred work, things future
agents will want to know. Update this section as the sprint runs;
it becomes the seed for RETRO.md.>
