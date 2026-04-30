---
created: 2026-04-30T05:00:00Z
branch: main
author: agentile-skeleton
status: active
---

# Coverage Gates

> The four ratchets that bound a project's quality floor over
> time. A ratchet only turns one direction: numbers go up, never
> down. Sprints close on the values; CI enforces the values
> between sprints.

The ratchet model is the spine of Agentile's quality enforcement.
Where conventional CI says "tests must pass," the ratchet says
"tests must pass *and the count must not have decreased*." The
asymmetry is deliberate: in any sufficiently large codebase,
"tests pass" is achievable by deleting awkward tests. The ratchet
makes that move visible.

There are four axes. Each is independently enforced.

---

## The four ratchets

| # | Ratchet | What it counts | Failure mode it catches |
|---|---------|----------------|-------------------------|
| 1 | **Test count** | Total passing tests across all suites | Test deletion to make CI green |
| 2 | **Formal specs** | TLA+ specs that pass TLC | Removal or weakening of a state-machine proof |
| 3 | **CI tripwires** | Active regression-prevention rules in CI | Disabling a tripwire after it failed once |
| 4 | **Frontmatter coverage** | Fraction of `.md` files with Rule-12 frontmatter | Pre-rule artifacts becoming current guidance again |

A sprint close runs all four. A CI build runs all four on every
PR. A merge that drops any of them is a BLOCKER (Rule 3, Rule 6,
Rule 10, Rule 12).

---

## Ratchet 1: Test count

### What it counts

Every passing test in every test suite the project runs. Languages
and frameworks vary; the *count* is what matters. The canonical
counting commands live in `BASELINE.md` for the specific project
and are re-quoted in every sprint's `SPRINT.md`.

Common shapes:

| Suite type | Example canonical command |
|------------|---------------------------|
| Rust workspace | `cargo test --workspace 2>&1 \| grep -E "test result:" \| awk '{s+=$4}END{print s}'` |
| TypeScript / vitest | `npx vitest run --reporter=json \| jq '.numTotalTests'` |
| Python / pytest | `pytest --collect-only -q \| tail -n 1` |
| Solidity / forge | `forge test --summary 2>&1 \| grep "Suite result" \| awk '{s+=$4}END{print s}'` |

### Where the baseline lives

- Project-level baseline: `.agentile/coverage/BASELINE.md` (filled
  in by `bootstrap.sh` at project setup; updated on each sprint
  close).
- Per-sprint baseline: `SPRINT.md` "Test Baseline (start of
  sprint)" table.

### Enforcement

- **Sprint close (BLOCKER, Rule 3):** Final count must be `>=`
  start-of-sprint count.
- **CI (GATE, Rule 3):** Each PR runs the canonical count. CI
  rejects merges where the post-PR count drops below the most
  recent main-branch baseline.
- **Mid-sprint (operator-led):** DAILY.md records the count after
  each work day. A dropping daily count is a yellow flag worth
  examining; if intentional (e.g. an obsolete test was replaced
  with an equivalent), name the trade-off in DAILY.md.

### When the count *can* go down

A test count can legitimately decrease only when:

1. **Equivalent or better test lands in the same commit.** Net
   count is the same or higher, and the trade is recorded.
2. **The test was incorrect.** Removing a wrong test is correct;
   replacing it with a right test is required.

A test count cannot decrease because the test was "flaky," "slow,"
or "in the way of refactoring." Those are signals to fix the test
or the implementation, not delete the test.

---

## Ratchet 2: Formal specs

### What it counts

Each TLA+ spec under the project's `specs/tla/` (or equivalent
formal-verification directory) that:

- Has a companion `.cfg`
- Runs clean under TLC at the most recent CI check
- Is referenced from `.agentile/formal/SPEC_INDEX.md`

A `.tla` file that exists but doesn't run, or runs but isn't
indexed, doesn't count.

### Where the baseline lives

- `.agentile/formal/SPEC_INDEX.md` — the canonical inventory.
- `BASELINE.md` records the count and the canonical command.

### Canonical command shape

```
find <project>/specs/tla -name '*.tla' \
  | xargs -I{} <tla-runner> {} \
  | grep -c "PASS"
```

Each project's TLA toolchain wraps differently; record the exact
command in `BASELINE.md`.

### Enforcement

- **Sprint close (GATE, Rule 10):** If the sprint touched
  consensus or state-machine code, the relevant TLA+ spec exists
  and passes. Spec count `>=` start-of-sprint count.
- **CI (GATE):** A nightly or per-PR TLC run checks every indexed
  spec. PRs that delete or weaken a spec without an
  equivalent-or-better replacement are rejected.
- **When a spec is correctly removed:** Same rule as test deletion.
  An incorrect spec is correctly removed if a corrected spec
  lands in the same commit.

---

## Ratchet 3: CI tripwires

### What it counts

Every active CI check that:

- Detects a *class* of regression (not a single test case)
- Has a documented finding it traces to (audit ID, case study, or
  bug report)
- Fails the build if violated

Common tripwire forms: `grep` / `rg` patterns, `semgrep` rules,
custom lint rules, dependency scanners, contract-invariant tests
in CI, GitHub Actions step assertions.

### Where the baseline lives

- `BASELINE.md` records the count and the canonical command for
  enumerating active tripwires.
- Each tripwire's source-of-truth file references the audit
  finding or case study that motivates it.

### Canonical command shape

The exact command depends on where tripwires live in the
project. Examples:

```
# Semgrep rule files
find .semgrep/ -name '*.yml' | wc -l

# Tripwire scripts in CI
find .github/scripts/tripwires/ -name '*.sh' -o -name '*.py' | wc -l

# Tagged invariant tests
grep -rln "@tripwire\|TRIPWIRE:" tests/ | wc -l
```

Whatever the project picks, record the chosen counting query in
`BASELINE.md`.

### Enforcement

- **Sprint close (GATE):** Tripwire count `>=` start-of-sprint
  count.
- **CI (GATE, Rule 6):** A tripwire cannot be disabled without a
  paired audit entry naming why. PRs that delete a tripwire
  without that audit reference are rejected.
- **A tripwire firing is not a tripwire being broken.** Fix the
  underlying violation; do not delete the tripwire.

---

## Ratchet 4: Frontmatter coverage

### What it counts

The fraction of `.md` files under `.agentile/` that begin with a
Rule-12 frontmatter block:

```
---
created: ...
branch: ...
author: ...
status: ...
---
```

Pre-rule artifacts (documents that predate Rule 12) are exempt
*until they're touched* — the moment a pre-rule file is edited,
it must gain frontmatter.

### Where the baseline lives

- `BASELINE.md` records `<frontmatter_count>/<total_md_count>`
  and the counting query.

### Canonical command shape

```
total=$(find .agentile -name '*.md' | wc -l)
covered=$(find .agentile -name '*.md' | xargs -I{} sh -c 'head -1 "{}" | grep -q "^---$" && echo 1' | wc -l)
echo "$covered/$total"
```

### Enforcement

- **Sprint close (GATE, Rule 12):** Coverage `>=` start-of-sprint
  fraction. New files that lack frontmatter block sprint closure.
- **CI (GATE, Rule 12):** A PR-time check refuses any new `.md`
  file under `.agentile/` that lacks frontmatter.

### Non-`.agentile/` documents

The frontmatter requirement applies to docs under `.agentile/` by
default. Projects MAY extend the requirement to crate READMEs,
guides, or other documentation directories — record the chosen
scope in `BASELINE.md`. The skeleton's default scope is
`.agentile/` only because that's where governance documents live.

---

## Reading the ratchets together

Any one ratchet in isolation is gameable:

- A test ratchet without a tripwire ratchet permits "passing tests
  for the wrong invariants."
- A tripwire ratchet without a test ratchet permits "regression
  detection without behavioral verification."
- A spec ratchet without a tripwire ratchet permits "formal proofs
  that don't connect to lived code."
- A frontmatter ratchet without the others permits "well-organized
  paperwork over rotting code."

The four together form a closed loop. Tests verify behavior; specs
verify state-machine properties; tripwires prevent regression of
finding *classes*; frontmatter coverage keeps the documentary
record honest about what's current vs. historical. A project that
ratchets all four monotonically is a project where the quality
floor cannot quietly drop.

---

## See also

- `BASELINE.md.template` — the per-project baseline file
- `CORE_RULES.md` — Rules 3, 6, 10, 12 are the rule-side anchors
- `formal/VERIFICATION_WORKFLOW.md` — how to add to ratchet 2
- `workflows/AUDIT_DRIVEN.md` — how to add to ratchet 3
