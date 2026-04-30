---
created: 2026-04-30T05:00:00Z
branch: main
author: agentile-skeleton
status: template
---

<!--
ADR TEMPLATE — Agentile.

Copy this file to:
  .agentile/planset/adr/ADR-<NNN>-<slug>.md

Numbering: zero-padded to 3 digits, monotonically increasing.
Once an ADR is ACCEPTED it is append-only. To reverse a decision,
write a new ADR that supersedes it and update this one's
frontmatter status to `superseded`, with `superseded_by` pointing
at the new ADR.
-->

# ADR-<NNN>: <title>

| Field | Value |
|-------|-------|
| **ADR Number** | ADR-<NNN> |
| **Date** | YYYY-MM-DD |
| **Status** | PROPOSED / ACCEPTED / DEPRECATED / SUPERSEDED BY ADR-<N> |
| **Author** | <name or zooid> |
| **Sprint** | <sprint ID, if scoped to a sprint> |

## Context

<What is the problem or situation that motivates this decision?
What constraints exist? What forces are in tension? Be specific —
"we need to make a choice" is not context; "library X requires
serde 1.0.x but our wallet crate is pinned to 0.9.x" is.>

## Decision

**We will <decision statement>.**

<2–4 sentences elaborating on the decision and naming the boundary
of what it does and does NOT change.>

## Rationale

<Why this decision was made. Cite measurements, constraints, prior
incidents, or ADRs. Decisions backed by data outlive decisions
backed by preference.>

### Alternatives considered

| Alternative | Pros | Cons | Why rejected |
|-------------|------|------|--------------|
| <Option A> | <pros> | <cons> | <reason> |
| <Option B> | <pros> | <cons> | <reason> |
| **<Chosen option>** | <pros> | <cons> | **Selected** |

## Consequences

### Positive

- <consequence 1>
- <consequence 2>

### Negative

- <consequence 1, and how it will be mitigated>
- <consequence 2, and how it will be mitigated>

### Neutral

- <observation>

## Affected components

| Component | Impact |
|-----------|--------|
| `<crate / module / contract>` | <how it is affected> |

## Compliance check

- [ ] Consistent with `CONFIG.md` canonical values
- [ ] Does not violate any rule in `CORE_RULES.md`
- [ ] If consensus / state-machine touching: TLA+ spec exists or
      is explicitly carried forward
- [ ] Rule-12 frontmatter present

## References

- <related ADR / issue / PR / spec>
- <prior incident or audit finding>

## Revision history

| Date | Author | Change |
|------|--------|--------|
| YYYY-MM-DD | <name> | Initial proposal |
| YYYY-MM-DD | <name> | Accepted |
