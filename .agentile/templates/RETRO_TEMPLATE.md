---
created: 2026-04-30T05:00:00Z
branch: main
author: agentile-skeleton
status: template
---

<!--
RETRO TEMPLATE — Agentile.

Copy this file to:
  .agentile/sprints/completed/<sprint-folder>/RETRO.md

Authored at sprint close, alongside the final SPRINT.md update.
Honest reporting (Rule 0): "what didn't work" is at least as
valuable as "what worked." Reframing failures as successes
poisons the record for the next session.
-->

# Sprint <ID> — Retrospective

## Outcome

| Field | Value |
|-------|-------|
| **Goal achieved?** | YES / PARTIALLY / NO |
| **WPs planned / closed** | <N> / <N> |
| **Carry-forward WPs** | <list of WP-IDs moved to next sprint, or "none"> |
| **Closing branch** | `<branch>` at `<closing commit hash>` |

## Metrics delta

| Axis | Start | End | Δ |
|------|-------|-----|----|
| Tests | <N> | <N> | <+N> |
| Formal specs | <N> | <N> | <+N> |
| CI tripwires | <N> | <N> | <+N> |
| Frontmatter coverage | <N>/<N> | <N>/<N> | <+N> |

If any axis went DOWN, name the reason here. The ratchets exist
because tests/specs/tripwires/coverage going down is almost always
the symptom of a problem the team is rationalizing away.

## What worked

- <thing 1: what specifically, and why it worked — be concrete>
- <thing 2>

## What didn't work

- <thing 1: name the failure, name the cost. Don't dress it up.>
- <thing 2>

## What surprised us

- <observation 1: an outcome that contradicted the going model.
  These are the highest-value entries in a retro because they're
  what an outside reader can't reconstruct from the commit log.>
- <observation 2>

## Carry-forward

| Item | Where it goes | Why deferred |
|------|---------------|--------------|
| <WP-ID or named item> | <next sprint or backlog> | <reason> |

## Decisions ratified mid-sprint

<List any decisions that were made during execution and that should
become durable. If they justify an ADR, link to it here.>

- <decision 1> — ADR-<N> if applicable

## Action items for next sprint

- [ ] <action 1, with named owner>
- [ ] <action 2>

## Notes

<Anything else the next session needs. Calibration on velocity,
pointers to journals/essays/case studies that this sprint produced,
or open questions that did not block closure but should be revisited.>
