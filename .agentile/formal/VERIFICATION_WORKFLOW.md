---
created: 2026-04-30T05:00:00Z
branch: main
author: agentile-skeleton
status: active
---

# Formal Verification Workflow

> The 6-step method for adding a TLA+ spec to a feature, audit
> finding, or remediation WP. This is the canonical sequence.
> Skipping a step is allowed only when it doesn't apply, and the
> WP block must say so explicitly.

The method exists because the most common failure mode of formal
verification isn't bad specs — it's specs that get written *after*
the code, "to document what we already built." Those specs add
zero correctness signal: they encode the bugs the code already
ships with. Specs are useful exactly to the extent that they get
written *before* the code and have a chance to falsify the design
before any line of implementation is committed.

---

## The six steps

```
1. Identify the state machine
2. Write the spec
3. Run TLC
4. Fix the spec until clean
5. Write the implementation
6. Add a regression test that re-runs TLC in CI
```

Steps 1–4 are pre-implementation. Step 5 is the WP's GREEN phase.
Step 6 is what makes the spec count toward ratchet 2.

---

### Step 1: Identify the state machine

The work that admits formal verification is the work where:

- More than one actor takes actions that affect a shared state.
- The order of actions can vary in production.
- The correctness of the system depends on an invariant that
  must hold across *all* possible orderings.

Identify the actors, the shared state, and the actions. Name them
in plain English first; the TLA+ encoding comes in step 2.

A useful self-check: write a one-paragraph description of the
state machine that does NOT use any TLA+ syntax. If you can't,
you don't yet understand what you're verifying.

**Operator-vs-variable principle.** Distinguish between:

- **Operators** — pure functions of state. Computed, never
  mutated. Examples: a routing function over a registry, an
  aggregation function over a vote set.
- **Variables** — the mutable state itself. Examples: the
  registry, the vote set, the validator's view number.

Pinning operators as CONSTANTS and variables as VARIABLES at the
spec level is what bounds TLC's state space. Conflating the two
produces specs that are intractable to model-check.

---

### Step 2: Write the spec

Copy `templates/TLA_SPEC_TEMPLATE.tla` and `.cfg` to your
project's `specs/tla/<area>/<SpecName>.{tla,cfg}`.

Author:

- **CONSTANTS** for inputs the model takes from the cfg.
- **VARIABLES** for the mutable state.
- **Init** for the initial state.
- **Actions** — one operator per action an actor can take.
  Convention: parameterize by the actor.
- **Next** disjuncting over all actions.
- **Spec** as `Init /\ [][Next]_vars`.
- **Invariants** — the things you claim are always true.

Bound the state space aggressively. Set sizes of 3–5, step counts
of 10, validator counts of 7–10 with 2–3 Byzantine. TLC's job is
to falsify the invariants in a *small* state space — if the bug
isn't reachable in the small model, scaling up rarely surfaces it
either.

---

### Step 3: Run TLC

```bash
java -cp tla2tools.jar tlc2.TLC \
  -config <SpecName>.cfg \
  -workers <N> \
  <SpecName>.tla
```

Three possible outcomes:

| Outcome | Meaning | Action |
|---------|---------|--------|
| **PASS** (no error, "Model checking completed") | Spec is consistent with its invariants in the configured state space | Proceed to step 5 |
| **FAIL** (invariant violated, with counterexample trace) | Spec or invariant has a real bug | Step 4 |
| **DEADLOCK** ("Deadlock reached") | Next has no enabled actions in some state | Step 4 |
| **TIMEOUT / OOM** | State space too large | Tighten constants in the cfg, then re-run |

The counterexample trace from a FAIL is the most valuable output
TLA+ produces. Read it action by action; the bug is concrete.

---

### Step 4: Fix the spec until clean

The fix can be in three places:

1. **The invariant is wrong.** What you claimed was always true
   isn't. Update the invariant; possibly the design itself is
   wrong, in which case escalate before step 5.
2. **The action is wrong.** An action permits a transition the
   real protocol wouldn't. Tighten the action's preconditions.
3. **The model is wrong.** A constant should have been a variable
   (or vice versa); a state-space bound is masking a real bug.

After every change, re-run TLC. Iterate until clean.

If iteration doesn't converge — the spec keeps producing
counterexamples that look like real bugs in the design — that's
the most valuable signal TLA+ can give you. **Stop coding.** The
design has a flaw that needs to be resolved at the design layer.
Fixing it in code first guarantees you'll re-discover the same
flaw later as a flaky integration test.

---

### Step 5: Write the implementation

Now and only now is the WP's GREEN phase. Implement against the
spec. The spec is the contract; the code's job is to honor the
contract.

Practical rule: name the spec's actions as functions or methods
in the code. `RegisterAdapter` in the spec becomes
`register_adapter` in the code. Reviewers reading both should be
able to map line by line.

When the implementation diverges from the spec — and it will, in
small ways — record the divergence in a code comment that names
the spec line, and decide deliberately:

- Implementation should change to match the spec, OR
- Spec should change to match the implementation (which means
  going back to step 3 with the updated spec).

A divergence that exists silently is a bug waiting to fire.

---

### Step 6: Regression test in CI

Add a CI job that runs TLC on every PR. The job:

- Iterates over every `.tla`/`.cfg` pair indexed in
  `SPEC_INDEX.md` (or under `.agentile/formal/specs/` if the
  index is auto-generated).
- Reports PASS / FAIL per spec.
- Fails the build on any FAIL.
- Reports the spec count to the ratchet (ratchet 2).

Example shape (pseudocode):

```bash
for spec in $(find .agentile/formal/specs -name '*.tla'); do
  cfg="${spec%.tla}.cfg"
  java -cp tla2tools.jar tlc2.TLC -config "$cfg" -workers 4 "$spec"
done
```

The CI job is what makes the spec count toward the ratchet.
Without it, the spec is a write-once document that drifts from
the implementation as the code changes. Specs that aren't run
are worse than no specs — they create false confidence.

---

## Deep verification

Some specs benefit from periodic deep runs: larger state spaces,
longer run times, possibly distributed-TLC. Schedule these
nightly or weekly, not per-PR.

A typical setup:

| Cadence | State-space scale | When to use |
|---------|-------------------|-------------|
| Per-PR | Small (Sets size 3–5) | Catch regressions during development |
| Nightly | Medium (Sets size 5–8) | Catch bugs the small model misses |
| Pre-release | Large (Sets size 8–12) | Final-confidence run before tagging |

Record the deep-verification command in `BASELINE.md` next to the
per-PR command.

---

## Anti-patterns

- **Specs after the code.** The spec encodes existing bugs
  rather than catching them. Write the spec first or accept
  that you're writing documentation, not verification.
- **Untested specs.** A `.tla` that exists but isn't run in CI
  is a write-once document. Index it and run it, or delete it.
- **State-space inflation.** Increasing constants until TLC OOMs
  in the hope of "stronger" verification. The state space exists
  to bound exploration; very large state spaces don't find more
  bugs, they find the same bugs more slowly. Use a small space
  for development, a deep space for pre-release.
- **Pet specs.** Specs that nobody but their author understands.
  A spec that can't be read by a teammate isn't verifying
  anything except the author's preferences. Add comments,
  document the operator-vs-variable choices, and pair-review.

---

## See also

- `README.md` — what `formal/` is for
- `SPEC_INDEX.md` — the project's spec inventory
- `templates/TLA_SPEC_TEMPLATE.tla` — starting point
- `coverage/GATES.md` ratchet 2 — enforcement
- `CORE_RULES.md` Rule 10 — when verification is required
