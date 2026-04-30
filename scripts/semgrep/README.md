# `scripts/semgrep/` — AST-grade tripwire rules

> Semgrep rules ship as the AST-grade companion to the regex-level
> Python checks under `scripts/ci/`. A project that runs only the
> Python checks is protected at the floor; adding Semgrep raises the
> bar to AST precision (fewer false positives, harder to bypass).

## Rules

| Rule | Languages | Severity | Companion check |
|------|-----------|----------|-----------------|
| `no-unwrap-in-prod.yaml` | rust | ERROR | `scripts/ci/check_no_unwraps.py` |
| `no-stub-default-constructor.yaml` | rust | ERROR | `scripts/ci/check_no_mocks.py` |
| `no-real-backend-loophole.yaml` | rust | WARNING | (none — too noisy for hard-block) |
| `frontmatter-required.yaml` | generic / markdown | ERROR | `scripts/ci/check_frontmatter.py` |
| `claim-compression-detector.yaml` | generic / commit messages | WARNING | (soft gate; manual review) |

## Local invocation

```bash
# Run all rules in this directory across the whole repo:
semgrep --config scripts/semgrep/

# Run a single rule:
semgrep --config scripts/semgrep/no-unwrap-in-prod.yaml

# Run with --error to fail the shell on any finding:
semgrep --config scripts/semgrep/ --error
```

## CI invocation

The `tripwires.yml` GitHub Actions workflow runs `semgrep` against
this directory on every PR. See `.github/workflows/tripwires.yml`.

## When to add a rule

Add a Semgrep rule when a finding from an audit or case study can be
expressed as an AST pattern AND would be a recurring issue if not
caught by CI. The rule should:

1. Cite the audit ID or case study that motivates it (in the
   leading comment block).
2. Specify language(s) and path filters explicitly.
3. Include a "how to suppress on a true positive" note in the message.
4. Have a companion regex check in `scripts/ci/` if the project wants
   defense-in-depth (recommended for ERROR-severity rules).

When you add a rule, the active tripwire count goes up — that's the
point. The tripwire-count ratchet (ratchet 3) ensures it doesn't
silently come back down later.

## When to remove a rule

A rule can be removed when:

1. The finding class has been eliminated by a stronger upstream
   guarantee (e.g. a type-system change makes the bug impossible).
2. A more precise rule replaces it (the old one was a false-positive
   factory).
3. The finding turned out to never apply to this project.

In all cases, the removal commit must include a justification in the
PR description naming the audit / case study reference, the
replacement (if any), and why the finding class no longer applies.
The tripwire-count ratchet enforces that this paper trail exists.

## See also

- `.agentile/coverage/GATES.md` ratchet 3 — tripwire enforcement
- `scripts/ci/README.md` — Python companion checks
- `.agentile/templates/AUDIT_TEMPLATE.md` — audit findings often
  produce new tripwire rules
