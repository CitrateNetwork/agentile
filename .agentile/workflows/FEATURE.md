---
created: 2026-04-30T05:00:00Z
branch: main
author: agentile-skeleton
status: active
---

# Feature Workflow

> The default per-WP execution sequence inside a sprint. Use this
> when the sprint is delivering new functionality. For
> audit-finding-driven work see `AUDIT_DRIVEN.md`. For multi-sprint
> remediation tracks see `REMEDIATION_TRACK.md`. For production
> rerolls see `CEREMONY.md`.

This workflow is the standard fall-through. If you don't have a
reason to use a different one, use this one.

---

## The seven steps

For each Work Package, in order:

1. **TLA+** *(when applicable)*
2. **BDD / Gherkin** *(when applicable)*
3. **RED — failing test + tripwire**
4. **GREEN — implement**
5. **REFACTOR — only after green**
6. **Adversarial check — fuzz, mutation, property, adversarial spec**
7. **Tripwire + journal — close the loop**

Skipping a step is allowed when it doesn't apply to the WP, but
the WP block in SPRINT.md must say so explicitly. "Skipped step 1
because no state-machine change" is fine; silent skipping is not.

---

### 1. TLA+

**When it applies:** the WP touches consensus, finality, proposer
election, cross-actor invariants, or any other state-machine that
admits race conditions.

**When it doesn't:** pure functions, format conversions, UI
rendering, statistical estimation, performance tuning of an
already-correct implementation.

**Output:** a `.tla` + `.cfg` pair under `<project>/specs/tla/<area>/`,
mirrored into `.agentile/formal/specs/<area>/`, indexed in
`.agentile/formal/SPEC_INDEX.md`. The spec must run clean under TLC
before code is written.

The point of TLA+ first is to discover impossible invariants
*before* implementing them. A spec that fails TLC reveals a design
problem that would otherwise show up as a flaky integration test
weeks later.

---

### 2. BDD / Gherkin

**When it applies:** the WP delivers user-observable or
external-actor-observable behavior. CLI, API, contract, daemon
endpoint.

**When it doesn't:** internal refactors, lint fixes, build infra.

**Output:** a `.feature` file with Given/When/Then scenarios
covering happy path, primary error case, and at least one boundary
case. Each scenario is wired to a test fixture in the next step.

Gherkin earns its keep when reviewers re-read the scenarios in
RETRO and discover that the lived behavior matches them
character-for-character. That fidelity check is the whole point.

---

### 3. RED — failing test + tripwire

The change does not begin until its regression detector exists and
fails. This is the most-skipped step and the source of most
"how did this regress?" surprises later.

**Test:** a unit, integration, property, or fuzz test that
demonstrates the missing behavior. Run it; confirm RED.

**Tripwire** (optional but encouraged): a CI check — `grep`/`rg`
pattern, `semgrep` rule, lint rule, or CI script — that catches
the *class* of bug the test catches a single instance of. Tests
verify behavior; tripwires verify the absence of bug-class
recurrence.

If the test cannot be written before the implementation (legitimate
cases exist — e.g. exploratory research), say so in the WP block
and write it in step 5.

---

### 4. GREEN — implement

Smallest change that turns the failing test green. Do not refactor
under a red bar. Do not generalize prematurely. Production-ready,
no stubs, no TODOs (Rule 2).

**Acceptance:** the failing test now passes; no previously-passing
test now fails (Rule 3).

---

### 5. REFACTOR — only after green

Once the bar is green, restructure for readability and reuse.
Tests stay green throughout. If a refactor breaks a test, revert
the refactor; the test is a constraint, not a suggestion.

A WP can legitimately have an empty refactor step — sometimes the
green code is already shaped the way it should be.

---

### 6. Adversarial check

The change survives an attempt to break it. Pick the appropriate
mode:

| Mode | When to use |
|------|-------------|
| **Property test** (proptest, fast-check, hypothesis) | Pure functions, parsers, serializers |
| **Mutation test** (cargo-mutants, mutmut) | Test-suite quality check on a tightened invariant |
| **Fuzz** (cargo-fuzz, AFL, Echidna) | Inputs from untrusted sources; cryptographic boundaries |
| **Adversarial TLA+** | Add a Byzantine actor to the spec; re-run TLC |
| **Differential test** | A reference implementation exists; cross-check |

The adversarial check is a gate, not a nicety. A WP without one
either lives in a domain where adversarial inputs cannot occur
(rare) or is incomplete.

---

### 7. Tripwire + journal — close the loop

**Tripwire:** if step 3 deferred the tripwire, land it now. CI
must enforce it on the next push.

**Journal:** if this WP produced a non-obvious learning, write a
journal entry under `.agentile/docs/journals/`. Most WPs don't.
Some do. The judgement of "non-obvious" is the WP author's; bias
toward writing if you discovered something that would not survive
in commit messages alone.

**SPRINT.md update:** WP block status, commit hash, tests added.
The sprint file is the source of truth (Rule 9). If the work isn't
recorded there, it didn't happen.

---

## Order of operations summary

```
TLA+ (if applicable)
  → BDD / Gherkin (if applicable)
    → RED test + tripwire
      → GREEN implement
        → REFACTOR
          → Adversarial check
            → Tripwire + journal
              → SPRINT.md update + commit
```

A WP commit message should reference the WP ID and the step it
closes when partial:
`feat(WP-3.2): GREEN — ECVRF P-256 proposer election`.
