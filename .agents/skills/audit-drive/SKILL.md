---
name: audit-drive
description: Walk through the Agentile audit-driven sprint workflow — author an audit, open a remediation sprint from findings, or close findings within an active sprint. Use when the user mentions "audit-driven", "remediation sprint", "turn findings into WPs", or references an audit file they want to act on.
allowed-tools: Read, Write, Bash
---

# Audit-Driven Sprint Workflow

Guides opening or executing an audit-driven sprint per `.agentile/workflows/AUDIT_DRIVEN.md`.

## When to Use

- The user wants to **author a new audit** (no audit exists yet).
- The user has an **existing audit** and wants to turn its findings into a remediation sprint.
- The user is in an **active remediation sprint** and wants to close the next finding.

## When NOT to Use

- Generic sprint kickoff without an audit backing it → use the `sprint` skill (`scripts/sprint.sh kickoff`).
- Filing a single bug with no audit context → just open an issue.
- Writing a case study about an incident → use the `case-study` skill.

## First: which mode?

Ask the user which of these they're doing:

1. **Author the audit** (no audit exists yet; they want to write one)
2. **Open a remediation sprint** (audit exists; turn findings into WPs)
3. **Close findings within an active sprint** (sprint is open; process the next finding)

Don't proceed until you know which mode. The procedures diverge.

## Mode 1: Author the audit

1. Confirm the user has `AUDIT_TEMPLATE.md` handy (`.agentile/templates/AUDIT_TEMPLATE.md`).
2. Help them pick a slug and dated directory: `.agentile/audits/YYYY-MM/YYYY-MM-DD-<slug>/AUDIT.md`.
3. Remind them: every finding MUST have a stable ID and file:line reference. Findings without file:line refs cannot be made into WPs and the remediation sprint will block on them.
4. Once the audit is committed, **it is immutable** (Rule 6). Corrections go in a NEW dated audit, not edits.

## Mode 2: Open a remediation sprint

1. Read the audit file the user references. Extract: Audit ID, target commit, score baseline + target, list of findings (ID, severity, file:line, suggested remediation, suggested tripwire).
2. If the finding count is large (>20), this is a multi-sprint **track**, not one sprint. Direct the user to `.agentile/workflows/REMEDIATION_TRACK.md`. Help them carve findings into phases (RM-A, RM-B, …) by severity slice (CRITICAL → HIGH → MEDIUM/LOW), layer order (consensus → execution → API → SDK → docs), and dependency annotations.
3. For a single-sprint audit: run `scripts/sprint.sh kickoff <ID> <track>-<phase>-<short-slug>`; open the seeded `SPRINT.md`; replace WP placeholders with one WP per finding (WP-ID = finding ID, e.g. `WP-WAL-014`); make sure each WP block names the finding's file:line + suggested tripwire.
4. Update `.agentile/sprints/CURRENT.md`.
5. Commit the kickoff.

## Mode 3: Close findings (sprint is open)

For the next finding:

1. **Reproduce.** Confirm the finding is real on the audit's pinned commit. If you cannot reproduce, do NOT close "by inspection." See AUDIT_DRIVEN.md §"Per-finding execution" step 2.
2. **Tripwire FIRST.** Author or update the regression check that would have caught this class of bug. Confirm it fires on the unfixed code.
3. **Fix.** Smallest change that closes the finding without breaking adjacent behavior.
4. **Verify.** Tripwire flips green. Reproduction no longer triggers. No previously-passing test now fails.
5. **Cross-check.** Are there adjacent findings (same component, similar mechanism) this fix also closes? If so, mark them in the WP block.
6. **Update SPRINT.md.** WP block status, commit hash, tests added, tripwire reference.
7. **Update audit closure record.** The audit itself is immutable (Rule 6); the closure record lives in `<audit-dir>/CLOSURE.md` (create if absent) with the closing commit hash.

## Rationalizations to Reject

- Marking a WP "as designed" without a follow-up audit downgrading the severity.
- Closing a finding "by inspection" without reproducing it on the pinned commit.
- Skipping the tripwire-first step because "the fix is obvious."

## Honest non-closure

If a finding can't close in this sprint, four legitimate options: out of scope (deferred), requires upstream fix (file the issue), auditor over-scoped (write a new audit downgrading severity), operationally infeasible (carry-forward). Disagreements are recorded, not silently dismissed.
