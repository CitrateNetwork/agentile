---
created: 2026-04-30T05:00:00Z
branch: main
author: agentile-skeleton
status: active
---

# Remediation Track Workflow

> When closure spans multiple sprints. A *track* is a named
> sequence of sprints that share a goal, a finding pool, and a
> score target. Use this when an audit produces too many findings
> for one sprint and the work decomposes into phases.

A remediation track sits one level above a sprint. Where a sprint
delivers WPs, a track delivers a closed audit. The track names the
phases (RM-A, RM-B, RM-C, ...), each phase is one or more sprints,
and the track closes when the score target is met or the
remaining findings are accepted as out-of-scope.

This is the right shape for non-trivial security audits, large
quality remediations, or any body of related work that is too big
to land in one sprint without losing coherence.

---

## Track anatomy

| Element | Description |
|---------|-------------|
| **Track ID** | Two-letter prefix following `RM-` (e.g. `RM-A`, `RM-FL`). Track-level naming is short by design. |
| **Phases** | Sub-tracks. `RM-A-1`, `RM-A-2`, ... Each phase is one sprint, or a small cluster (`RM-A-3a`, `RM-A-3b`) when the same phase needs to be split for context. |
| **Pool** | The set of audit findings the track is responsible for closing. |
| **Score target** | Numeric closure target (e.g. lift project score from 786/1000 to 920/1000). |
| **Planset** | A document under `.agentile/planset/RM_<TRACK>_<DATE>/` describing the phasing strategy. |
| **Cross-agent authorship** | Tracks routinely span multiple sessions. The planset is what gives later sessions enough context to start without re-deriving the phasing. |

---

## When to open a track

Open a track when:

- An audit produces >20 findings, OR
- The findings span multiple components and reasonable closure
  needs sequencing (e.g. consensus fixes before wallet fixes
  before SDK fixes), OR
- The work crosses a release boundary and needs to be tagged
  separately, OR
- A senior reviewer / steerer has asked for a track-level plan.

Don't open a track for: 1–2 findings (just use FEATURE.md);
findings that aren't yet triaged (triage first); aspirational
work without a closure target (write an essay or planset, not a
track).

---

## Phasing the track

The planset (`.agentile/planset/RM_<TRACK>_<DATE>/00_PLANSET.md`)
carves the finding pool into ordered phases. Each phase becomes
one sprint. Useful phasing heuristics:

1. **By layer.** Consensus → execution → API → SDK → docs. Bugs
   in lower layers can produce false positives in upper layers,
   so close them first.
2. **By severity.** All CRITICAL findings in phase 1, regardless
   of layer. HIGH in phase 2 with layered ordering. MEDIUM/LOW
   batched into the final phases.
3. **By dependency.** If finding B is reachable only after fixing
   A, A goes first. The planset lists these explicitly.
4. **By blast radius.** Changes that touch many files go later in
   the track when the team has built up familiarity with the
   audit's vocabulary.

Most real tracks combine these: severity-sliced first, layered
within severity, with explicit dependency annotations.

---

## Per-phase sprint shape

Each phase is a sprint that runs `AUDIT_DRIVEN.md`. The phase's
SPRINT.md adds a track-specific header section:

```
## Track context

| Field | Value |
|-------|-------|
| **Track ID** | RM-<TRACK>-<PHASE> |
| **Track parent** | <link to track planset> |
| **Phase position** | <N> of <M> |
| **Findings in scope** | <list of finding IDs> |
| **Predecessor phase** | <RM-X-Y, with closing commit and score> |
| **Score target this phase** | +<X> (cumulative <Y>/<denom>) |
```

The phase's WPs are the in-scope findings, one WP per finding,
following `AUDIT_DRIVEN.md` Per-finding execution.

The phase's RETRO.md captures track-level signals: was the
phasing right? Did fixes in this phase reveal that another phase
is mis-scoped? Track plansets are living documents for exactly
this reason — adjust them between phases.

---

## Cross-agent handoff inside a track

A track typically outlives any one Claude session. Handoff is
explicit, not implicit:

**At every phase close:**

1. SPRINT.md final state recorded.
2. RETRO.md written, including any phasing adjustments.
3. Planset updated if the sprint discovered the next phase needs
   re-shaping.
4. CURRENT.md points at the next phase if pre-kickoff is done,
   otherwise to "track <ID> phase <N> closed; next phase
   pending."
5. A short kickoff note for the next phase pre-written into the
   next phase's SPRINT.md draft, with: closing commit hash of
   this phase, score state, list of findings already closed,
   list of findings carried into this phase.

**At every phase open:**

1. New session reads this workflow doc, the track planset, and
   the predecessor's RETRO.md before authoring any code.
2. New session does NOT trust phasing from memory — re-checks
   the planset and adjusts if RETRO.md flagged the need.
3. New session inherits the score target unless the planset
   says otherwise.

The track planset is what makes cross-agent continuity work. A
track without a planset is a sprint that someone happens to call
a track; it will lose coherence when sessions change.

---

## Closing a track

A track closes in one of three ways. Choose the right one and
record it.

### 1. Goal closure

All in-scope findings closed; score target met. Authoritatively
the success outcome.

**Required artifacts:**

- Final phase's RETRO.md
- Track-level closure document at
  `.agentile/planset/RM_<TRACK>_<DATE>/CLOSURE.md` listing every
  finding's closing commit.
- Audit's `CLOSURE.md` updated with all closing commits.
- A track-closing essay or case study under `.agentile/docs/`
  capturing the durable lessons. Optional but strongly preferred
  — the track's lessons evaporate without it.

### 2. Acceptance closure

Some findings remain open but are formally accepted as out-of-
scope, won't-fix, or upstream-blocked. The track closes with
documented acceptance.

**Required artifacts:**

- Same as goal closure, plus:
- An ACCEPTANCE.md per accepted finding listing: severity, why
  acceptance is the right call, named accepter, and (if any)
  compensating control.
- Score target may not be met; record the actual final score and
  the gap.

### 3. Track abandonment

The track was opened on the wrong premise and is being killed.
Rare but legitimate.

**Required artifacts:**

- Final phase RETRO.md naming the abandonment reason.
- A new audit (Rule 6 — never edit the original) explaining why
  the original audit's framing was wrong.
- Findings reassigned: most likely to a new track with a refined
  planset.

---

## Anti-patterns specific to tracks

- **Phase fusion.** Closing two phases in one sprint because "we
  had time." Phases exist to bound context; fusing them produces
  sprints whose SPRINT.md becomes too long for the next session
  to fully load. If you genuinely have spare capacity, open the
  next phase as a separate sprint immediately.
- **Score creep.** Adjusting the target down mid-track because
  the original was hard. The original target is part of the
  audit's evidentiary value. Miss it openly; don't move it.
- **Plan-of-record drift.** The planset and the actual sprints
  diverge silently. Adjust the planset between phases if you
  must — explicitly, with rationale — but never let the gap
  accumulate unrecorded.
- **Stale handoff context.** A new session is given verbal context
  ("just close the rest of the findings") instead of being
  pointed at the planset. The skipped reading produces work that
  duplicates or contradicts earlier phases.
