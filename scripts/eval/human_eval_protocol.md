---
created: 2026-04-30T05:00:00Z
branch: main
author: agentile-skeleton
status: active
---

# Human Eval Protocol

> The protocol a human reviewer follows when evaluating a sprint
> close, an audit closure, or a high-stakes PR. Distinct from
> code-level review: this is the gate that asks whether the *claim
> matches reality*, not whether the code compiles.

The mechanical gates (CI tripwires, ratchets, Semgrep rules) catch
syntactic violations. The AI gates (claim grader, data-source check)
flag suspected judgement violations. The human eval is the last
backstop: a person reads the work and decides whether the
sprint/audit/PR is *actually* closed end-to-end.

This protocol exists because every other gate has known false
negatives. Tests pass on the wrong invariants. Tripwires fire on
syntactic surface. AI graders hallucinate. A human reviewer is the
only entity that can hold the *whole* claim — code plus tests plus
docs plus deployed artifact — in mind at once and ask "does this
add up?"

## When to invoke

| Trigger | Eval depth |
|---------|------------|
| Sprint close (any sprint) | **Full eval** — see protocol below |
| Audit closure (any track) | **Full eval** + audit-specific spot checks |
| Security-sensitive PR | **Full eval** + Rule 8 review |
| Routine feature PR (FEATURE.md) | **Light eval** — see "light" below |
| Pure refactor with tests | Light or skip if reviewer trusts the diff |
| Documentation-only PR | Skip (CI handles frontmatter) |

The default is light eval. Full eval is invoked when the work
crosses a sprint or audit boundary, or when the PR touches
consensus / crypto / keys / access control.

## Light eval (≤ 5 minutes)

For routine work where the reviewer trusts the author and the
mechanical gates are clean:

1. **Read the WP block in SPRINT.md.** What did this PR claim to
   close?
2. **Run the canonical test count** locally if you have any reason
   to suspect a ratchet bypass. `git log --stat` of the PR usually
   makes ratchet status obvious.
3. **Check the WP block's "Tests added" list** — every named test
   exists and passes.
4. **Approve.**

If anything in steps 1-3 doesn't match, escalate to full eval.

## Full eval (15-45 minutes)

### 1. Spec → code traceability

For each WP closed in this sprint/PR:

- [ ] WP block names a TLA+ spec (when applicable). The spec
      exists, runs clean under TLC, and is indexed in
      `formal/SPEC_INDEX.md`.
- [ ] WP block lists Gherkin scenarios (when applicable). The
      `.feature` file exists and has at least one scenario per
      acceptance criterion.
- [ ] Every named test exists, passes, and tests something
      non-trivial (not a tautology).
- [ ] Every acceptance criterion's named **data source** is real:
      the contract method exists, the RPC endpoint responds, the
      file path is on disk.

### 2. Claim → reality

Read the sprint's RETRO.md alongside its SPRINT.md. Ask:

- [ ] Did every "COMPLETE" WP actually close, by your reading of
      the diff and tests?
- [ ] Are deferred WPs honestly named as deferred (not silently
      promoted to "complete")?
- [ ] Are blocked items routed somewhere — backlog or next sprint
      — rather than just dropped?
- [ ] Does the metrics-delta table match what `git log --stat` and
      the test counts actually show?

### 3. Ratchet sanity

- [ ] All four ratchets at or above start-of-sprint baseline.
- [ ] Any ratchet that decreased has an explicit "and here's why"
      paragraph in RETRO.md (typically: a test was replaced with a
      better test in the same commit).

### 4. Audit closure (audit sprints only)

- [ ] Every in-scope finding has a final disposition (CLOSED /
      CARRIED-FORWARD / DEFERRED-WITH-AUDIT).
- [ ] Each CLOSED finding has a closing commit hash and the fix
      reproducibly resolves the audit's reproduction steps.
- [ ] CARRIED-FORWARD findings are listed in the next sprint's
      backlog or in `<audit-dir>/CLOSURE.md`.
- [ ] No edits to the original audit file (Rule 6).

### 5. Security review (Rule 8 sprints)

When the PR touches consensus, crypto, keys, or access control:

- [ ] At least one OTHER reviewer (not the author) has approved.
- [ ] No self-approvals on security-sensitive paths.
- [ ] If formal verification was required (Rule 10), the spec
      exists and runs clean.
- [ ] Threat-model assumptions are stated explicitly somewhere
      reviewable (PR body, SPRINT.md WP block, or a journal
      entry).

### 6. Decision

After steps 1-5:

| Outcome | Action |
|---------|--------|
| All green, work matches claim | Approve |
| Mechanical green but claim doesn't match work | **Block.** Request the author rewrite the claim. The work itself may be fine; the claim isn't. |
| Mechanical issue | **Block.** Request the underlying fix. |
| Mostly green with isolated issues | Approve with comments naming what to fix in the next iteration |

The "block on claim mismatch even when the work is fine" rule is
the heart of this protocol. Claim integrity matters because future
sessions plan against it. A claim that's 80% true is functionally
identical to a claim that's 0% true once it's frozen in the sprint
record.

## Recording the eval

For full evals on sprint or audit closure:

- A short note in RETRO.md (or a separate `EVAL.md`) under
  "Notes" naming: who reviewed, when, what found.
- For audit closures: the eval becomes part of the audit's
  CLOSURE.md.
- For routine PRs: GitHub PR review comments are sufficient — the
  protocol's job is judgement, not paperwork.

## Calibration

The protocol's weakest step is "do you trust the author?" Two
calibration pressures:

1. **Authors miscalibrate themselves.** The same person consistently
   over-claims, the same agent consistently under-claims. After a
   few full evals you learn which way the bias runs and adjust.
2. **Reviewers drift.** A tired reviewer skips step 4. The way to
   fix this is to do full evals on a schedule (every 2-4 weeks)
   even when nothing requires one — recalibrating the reviewer's
   eye before they're needed in earnest.

## See also

- `.agentile/rules/CORE_RULES.md` — Rules 0, 6, 8, 9 are the rule-
  side anchors
- `scripts/ai/grade_pr.py` — the AI's first-pass on claim
  compression
- `scripts/eval/data_source_check.py` — Rule 11 heuristic
- `workflows/SPRINT_LIFECYCLE.md` — close phase, where this
  protocol fires
- `workflows/AUDIT_DRIVEN.md` — audit closure invokes the
  audit-specific spot checks above
