# `scripts/ci/` — CI tripwire and ratchet check scripts

> The seven Python scripts that the CI workflows in
> `.github/workflows/` invoke. Each is a standalone tool that exits
> 0 on success and non-zero on a finding. All share a project-root
> discovery convention (walk upward for `.agentile/`) so they can
> be invoked from any cwd.

## Scripts

| Script | Type | What it enforces | Rule |
|--------|------|------------------|------|
| `check_frontmatter.py` | tripwire | Every `.md` under `.agentile/` has Rule-12 frontmatter | 12 |
| `check_no_unwraps.py` | tripwire | No bare `.unwrap()` in Rust production code | 5 |
| `check_no_mocks.py` | tripwire | No `Stub*`/`Mock*`/`Fake*` types outside `#[cfg(test)]`; MOCKS.md entries reference replacement WPs | 2, 11 |
| `check_test_ratchet.py` | ratchet | Test count >= baseline | 3 |
| `check_spec_ratchet.py` | ratchet | TLA+ spec count >= baseline | 10 |
| `check_tripwire_ratchet.py` | ratchet | Active tripwire count >= baseline | 6 (spirit) |
| `check_audit_immutability.py` | tripwire | No modifications to existing files under `.agentile/audits/` | 6 |

A **tripwire** detects a *class* of issue (the bug exists or it doesn't).
A **ratchet** measures a number against a stored baseline (the count
went up, stayed the same, or went down).

## Baseline file

The three ratchet scripts read `.agentile/coverage/baseline.json`:

```json
{
  "tests":       {"count": <N>, "command": "<canonical test-count command>"},
  "specs":       {"count": <N>, "command": "...", "directories": ["..."]},
  "tripwires":   {"count": <N>, "command": "..."},
  "frontmatter": {"covered": <N>, "total": <N>}
}
```

The file is written by `bootstrap.sh` (Phase 6) at project setup and
updated at every sprint close. If the file is missing or the relevant
`command` is empty, the ratchet is a no-op (returns 0 with a warning).

This degraded mode is intentional: a freshly-adopted skeleton hasn't
run bootstrap yet, so the ratchets cannot be enforced until the
project owner records the baseline. CI tripwires (no-unwrap, no-mocks,
audit-immutability, frontmatter-required) work from day zero without
a baseline.

## Invocation patterns

### Local pre-commit / pre-push

```bash
./scripts/ci/check_frontmatter.py
./scripts/ci/check_no_unwraps.py
./scripts/ci/check_no_mocks.py
./scripts/ci/check_audit_immutability.py
./scripts/ci/check_test_ratchet.py
./scripts/ci/check_spec_ratchet.py
./scripts/ci/check_tripwire_ratchet.py
```

Run the last three only when the relevant sub-system has changed —
they're slow.

### CI (GitHub Actions)

The workflows in `.github/workflows/` invoke these scripts directly.
See `lint-frontmatter.yml`, `tripwires.yml`, `ratchet-check.yml`,
`audit-immutability.yml`.

### Scoped to changed files

The two file-walking checks (`check_frontmatter`, `check_no_unwraps`,
`check_no_mocks`) accept `--files <path>...`:

```bash
./scripts/ci/check_frontmatter.py --files \
  $(git diff --name-only HEAD~1 HEAD | grep '\.md$')
```

This is what the GitHub workflows do for PR-time scoping — they only
check the files the PR touched, not the whole repo.

`check_audit_immutability.py` accepts `--since <commit>` for the same
purpose:

```bash
./scripts/ci/check_audit_immutability.py --since origin/main
```

## Rust adapter assumptions

`check_no_unwraps.py` and `check_no_mocks.py` ship Rust-default. They
expect a project layout with one or more of: `src/`, `core/`, `node/`,
`wallet/`, `cli/`, `faucet/`. Adapters for other languages are
straightforward — see the `ADAPTERS` table at the top of
`check_no_unwraps.py`.

The Semgrep rules in `scripts/semgrep/` ship parallel AST-grade
versions of the unwrap and mock checks for projects that prefer
Semgrep over regex. The Python checks are the floor; Semgrep is the
upgrade.

## Exit codes

All scripts use the same convention:

| Code | Meaning |
|------|---------|
| 0 | Clean — no violations, ratchet not regressed |
| 1 | Violation found — script prints offenders, CI blocks merge |
| 2 | Usage error or unexpected failure (e.g. command timeout) |

CI workflows check for non-zero and fail the job; they do not
distinguish 1 vs. 2 (a usage error is also a failure).

## See also

- `.agentile/coverage/GATES.md` — the four ratchets, defined
- `.agentile/coverage/BASELINE.md.template` — human-readable baseline
- `.agentile/rules/CORE_RULES.md` — the rules these scripts enforce
- `scripts/semgrep/` — AST-grade companion rules
- `.github/workflows/` — CI wiring
