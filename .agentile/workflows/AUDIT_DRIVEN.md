---
created: 2026-04-30T05:00:00Z
branch: main
author: agentile-skeleton
status: active
---

# Audit-Driven Sprint Workflow

> When the audit IS the WBS. Findings become Work Packages directly.
> Use this when you are responding to a multi-finding security or
> quality audit, not designing new functionality from scratch.

The audit-driven sprint inverts the normal planning relationship.
In a feature sprint, you decide what to build and write tests
afterward. In an audit-driven sprint, the audit has already
written the spec — every finding is a defect with a file:line
reference, a severity, and (ideally) a suggested fix. The sprint's
job is to close findings, not to invent scope.

This is the workflow used when an external auditor, a sibling
agent session, or an automated tool produces a body of findings
large enough that converting them into a normal sprint plan would
be its own multi-day exercise.

---

## When to use this workflow

| Use audit-driven when... | Use FEATURE.md when... |
|---|---|
| You have an audit doc with file:line refs | You're designing new behavior |
| Findings outnumber planned features | Tests come from product requirements, not findings |
| Closure is measured by score delta | Closure is measured by goal achievement |
| The audit's structure can become the sprint's structure | Sprint structure is yours to design |

If you have one or two findings to fix, those are FEATURE.md WPs.
This workflow exists for the case where the audit is dozens of
findings and using FEATURE.md would mean re-typing the audit into
a sprint plan.

---

## Setup

**Pre-conditions:**

1. The audit lives in `.agentile/audits/YYYY-MM-DD-<slug>/AUDIT.md`
   and is immutable (Rule 6).
2. Every finding has a stable ID (e.g. `WAL-014`, `AGT-003`).
3. Every finding cites file:line. **Findings without file:line
   refs cannot be made into WPs**; they go back to the auditor
   for elaboration before the remediation sprint can start.
4. Severities are assigned. CRITICAL and HIGH gate the sprint;
   MEDIUM and LOW may be batched or deferred.

**Kickoff variant:**

Follow `SPRINT_LIFECYCLE.md` Phase 1 with these substitutions:

- Goal becomes "Close <N> findings from <audit ID>, lifting score
  from <X>/<denom> to <Y>/<denom>."
- WPs are sourced from the audit, **not** authored fresh.
  Convention: WP-ID = audit finding ID. If `WAL-014` is in scope,
  the WP block is titled `WP-WAL-014`.
- The sprint may close partial — not every finding has to land in
  one sprint. Use phased sprints (`RM-A`, `RM-B`, ...) for tracks
  that need multi-sprint closure.

---

## Per-finding execution

Each finding becomes a WP. The per-WP sequence:

### 1. Re-read the finding

Open the audit file. Read the full finding block. Do NOT skim. The
auditor's framing is the spec — if the WP author misreads it, the
fix will close the wrong thing.

### 2. Reproduce

Confirm the finding is real on the audit's pinned commit. If you
cannot reproduce, do NOT close the finding "by inspection." Either:

- The finding is wrong → write a follow-up audit (new dated dir)
  with a correction citing the original ID.
- Your reproduction setup is wrong → fix it before proceeding.

A WP that closes a finding without reproducing it is the most
common way an audit-driven sprint produces fake closure.

### 3. Tripwire FIRST

This is the inversion that distinguishes audit-driven from
feature work. The tripwire — a regression check that would have
caught the bug class — comes BEFORE the fix.

The tripwire's job is to fail on the unfixed code. That confirms:
1. The tripwire is real (it catches something).
2. The class of bug is detectable in CI.
3. The fix in step 4 is what flips the tripwire from red to green.

Tripwires take many forms: `grep` / `semgrep` rules, lint config,
invariant tests, TLA+ amendments, dependency scanners. Pick the
form that catches the *class*, not the *instance*.

### 4. Fix

Smallest change that closes the finding without breaking adjacent
behavior. Production-ready (Rule 2). Tests stay green (Rule 3).

### 5. Verify

- Tripwire flips from red to green on the fix.
- Reproduction from step 2 no longer triggers the bug.
- No previously-passing test now fails.
- If the audit suggested a remediation, your fix is at least as
  strong; if you chose differently, document why in the WP block.

### 6. Cross-check related findings

A non-trivial fix often closes adjacent findings. Re-read the
audit for findings in the same component or with similar
mechanisms. Mark them in the WP block; if they're closed by this
fix, give them their own commit hash and close them in this WP's
update.

Conversely, your fix might surface a previously-unfindable bug.
That's a NEW audit, not an edit to the original. Write it.

### 7. Update SPRINT.md and the audit's track table

Two updates per finding:

- WP block in SPRINT.md → status, commit, tests, tripwire
- Track suggestion table in the audit (or a separate
  `<audit-dir>/CLOSURE.md` if the audit is immutable) → finding
  marked closed, with closing commit hash

The audit itself stays untouched (Rule 6). The closure record
lives alongside it.

---

## Score tracking

Audit-driven sprints are typically scored. The score table goes
in SPRINT.md and updates as findings close:

| Phase | Findings closed | Score delta | Cumulative |
|-------|-----------------|-------------|------------|
| Start | 0 | 0 | <baseline>/<denom> |
| WP-WAL-014 closed | 1 | +<X> | <new>/<denom> |
| WP-AGT-003 closed | 1 | +<Y> | <new>/<denom> |
| End | <N> | +<sum> | <final>/<denom> |

If a fix produces a score delta different from the audit's
estimate, note the discrepancy. Auditor and remediator can have
different views of severity; the difference is signal, not noise.

---

## Honest non-closure

Some findings will not close in the sprint. Reasons that are
acceptable, with required handling:

| Reason | Handling |
|--------|----------|
| Out of scope (sprint is RM-A; finding is in RM-C territory) | Defer to the appropriate track sprint. Note in WP. |
| Requires upstream fix | File the upstream issue. Track its status in the WP. |
| Auditor over-scoped | New audit (not edit) downgrading severity. |
| Operationally infeasible this sprint | Carry-forward to next remediation sprint. |

What is **not** acceptable:

- Closing the WP "as designed" without a follow-up audit
  documenting the disagreement.
- Marking it closed because the tripwire was disabled.
- Reframing the bug as "not actually a bug" without an audit
  paper trail.

The audit's evidentiary value depends on it being treated as a
spec, not a wishlist. Disagreements are legitimate and must be
recorded; silent dismissal is not.

---

## Closure

Standard `SPRINT_LIFECYCLE.md` Phase 4 close. Specific
requirements for audit-driven sprints:

- Every in-scope finding has a final disposition (CLOSED /
  CARRIED-FORWARD / DEFERRED-WITH-AUDIT).
- The cumulative score is recorded against the audit's target.
- The CLOSURE.md (or equivalent closure record) sits next to the
  immutable audit, naming each finding's closing commit.
- Carry-forward findings appear in the next sprint's plan (or in
  the backlog if no next sprint is yet defined).

---

## See also

- `SPRINT_LIFECYCLE.md` — base lifecycle this layers on
- `REMEDIATION_TRACK.md` — multi-sprint version of audit-driven work
- `CORE_RULES.md` Rule 6 — audit immutability
- `templates/AUDIT_TEMPLATE.md` — when authoring the audit itself
