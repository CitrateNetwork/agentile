---
description: Walk through the audit-driven sprint workflow — turn an audit's findings into a sprint plan
allowed-tools: Read, Write, Bash
---

You are guiding the user through opening or executing an audit-
driven sprint per `.agentile/workflows/AUDIT_DRIVEN.md`.

## First: which mode?

Ask the user which of these they're doing:

1. **Author the audit** (no audit exists yet; they want to write one)
2. **Open a remediation sprint** (audit exists; turn findings into WPs)
3. **Close findings within an active sprint** (sprint is open;
   process the next finding)

Don't proceed until you know which mode. The procedures diverge.

## Mode 1: Author the audit

1. Confirm the user has the AUDIT_TEMPLATE.md handy
   (`.agentile/templates/AUDIT_TEMPLATE.md`)
2. Help them pick a slug and dated directory:
   `.agentile/audits/YYYY-MM/YYYY-MM-DD-<slug>/AUDIT.md`
3. Remind them: every finding MUST have a stable ID and file:line
   reference. Findings without file:line refs cannot be made into
   WPs and the remediation sprint will block on them.
4. Once the audit is committed, **it is immutable** (Rule 6).
   Corrections go in a NEW dated audit, not edits.

## Mode 2: Open a remediation sprint

1. Read the audit file the user references. Extract:
   - Audit ID and target commit
   - Score baseline and target
   - List of findings (ID, severity, file:line, suggested
     remediation, suggested tripwire)
2. If the finding count is large (>20), this is a multi-sprint
   **track**, not one sprint. Direct the user to
   `.agentile/workflows/REMEDIATION_TRACK.md`. Help them carve the
   findings into phases (RM-A, RM-B, ...) by:
   - Severity slice (CRITICAL first, then HIGH, then MEDIUM/LOW)
   - Layer order (consensus → execution → API → SDK → docs)
   - Dependency annotations from the audit
3. For a single-sprint audit:
   - Run `scripts/sprint.sh kickoff <ID>
     <track>-<phase>-<short-slug>` to seed the sprint
   - Open the seeded `SPRINT.md`
   - Replace WP placeholders with one WP per finding (WP-ID =
     finding ID, e.g. `WP-WAL-014`)
   - Make sure each WP block names the finding's file:line and the
     suggested tripwire
4. Update `.agentile/sprints/CURRENT.md`
5. Commit the kickoff

## Mode 3: Close findings (sprint is open)

For the next finding the user wants to close:

1. **Reproduce.** Confirm the finding is real on the audit's pinned
   commit. If you cannot reproduce, do NOT close the finding "by
   inspection." See AUDIT_DRIVEN.md §"Per-finding execution" step 2.

2. **Tripwire FIRST.** Author or update the regression check that
   would have caught this class of bug. Confirm the tripwire fires
   on the unfixed code.

3. **Fix.** Smallest change that closes the finding without breaking
   adjacent behavior.

4. **Verify.** Tripwire flips green. Reproduction no longer
   triggers. No previously-passing test now fails.

5. **Cross-check.** Are there adjacent findings (same component,
   similar mechanism) that this fix also closes? If so, mark them
   in the WP block.

6. **Update SPRINT.md.** WP block status, commit hash, tests added,
   tripwire reference.

7. **Update audit closure record.** The audit itself is immutable
   (Rule 6); the closure record lives in
   `<audit-dir>/CLOSURE.md` (create if absent) with the closing
   commit hash.

## Honest non-closure

If a finding can't close in this sprint, the user has four legitimate
options (see AUDIT_DRIVEN.md):

- Out of scope (deferred to appropriate track)
- Requires upstream fix (file the upstream issue)
- Auditor over-scoped (write a new audit downgrading severity)
- Operationally infeasible (carry-forward)

What is NOT acceptable: marking the WP "as designed" without a
follow-up audit. Disagreements are recorded, not silently dismissed.
