# `.github/workflows/` — CI workflows

> Eight GitHub Actions workflows that wire the agentile rules and
> ratchets into PR-time enforcement. Each workflow invokes a script
> from `scripts/ci/` or `scripts/semgrep/`; the workflow itself only
> handles GitHub-side glue (when to run, what to check out, how to
> scope to changed files).

## Workflows

The `Perms` column is the top-level `permissions:` each workflow declares;
`Secrets` is the repo secrets it consumes. **Read these before copying
`.github/` into your project** — two workflows can write to PRs, and one
sends PR text to a third-party LLM endpoint.

| Workflow | Triggers | Enforces | Rule(s) | Perms | Secrets |
|----------|----------|----------|---------|-------|---------|
| `lint-frontmatter.yml` | PR / push to .md | `check_frontmatter.py` on changed `.md` files | 12 | `contents: read` | — |
| `lint-workflows.yml` | PR / push to `.github/workflows/**` | `actionlint` on workflow YAML | (supply chain hygiene) | `contents: read` | — |
| `ratchet-check.yml` | every PR / push to main | All four ratchets | 3, 10, 12, tripwire discipline | `contents: read` | — |
| `tripwires.yml` | every PR / push to main | `check_no_unwraps`, `check_no_mocks`, Semgrep, frontmatter-on-added | 2, 5, 11, 12 | `contents: read` | — |
| `audit-immutability.yml` | PR / push to `.agentile/audits/**` | No modification to existing audit files | 6 | `contents: read` | — |
| `claim-grade.yml` | PR / `workflow_dispatch` | AI claim-compression grader (shadow mode) | (honesty gate) | `contents: read`, **`pull-requests: write`** | **`ANTHROPIC_API_KEY` / `OPENAI_API_KEY`** (sends PR text off-platform) |
| `data-source-check.yml` | PR / `workflow_dispatch` | Data-source provenance check (shadow mode) | (Rule 11 support) | `contents: read`, **`pull-requests: write`** | — |
| `benchmark-nightly.yml` | schedule / `workflow_dispatch` | Nightly benchmark harness | (perf regression) | `contents: read` | — |

## Non-GitHub CI

The logic lives in `scripts/`, not in the workflow YAML. To run the
same checks on GitLab / CircleCI / Jenkins / Buildkite:

```bash
# Tripwires:
./scripts/ci/check_no_unwraps.py
./scripts/ci/check_no_mocks.py
./scripts/ci/check_frontmatter.py

# Ratchets:
./scripts/ci/check_test_ratchet.py
./scripts/ci/check_spec_ratchet.py
./scripts/ci/check_tripwire_ratchet.py

# Audit immutability (against your CI's known base ref):
./scripts/ci/check_audit_immutability.py --since "$BASE_REF"

# Semgrep:
semgrep --config scripts/semgrep/ --error
```

Port the workflows by translating the `runs-on:` and step structure;
the underlying invocations are language-agnostic.

## Adding language-specific tooling

`ratchet-check.yml`'s `test-ratchet` job is a placeholder — the
skeleton can't know whether the project uses Rust, TypeScript,
Python, or something else. Projects extend that job with toolchain
setup steps (e.g. `dtolnay/rust-toolchain@stable`, `actions/setup-node`,
`actions/setup-python`) before the `check_test_ratchet.py` invocation.

If `.agentile/coverage/baseline.json` has an empty `tests.command`,
the ratchet is a no-op and the toolchain step doesn't matter — useful
on a brand-new project that hasn't run bootstrap.sh yet.

## Concurrency model

Each workflow uses GitHub's `concurrency:` group to cancel superseded
runs (e.g. when a PR is force-pushed). The group key includes the
workflow name and the branch ref, so different workflows don't
cancel each other.

## Permissions

Every workflow declares an explicit top-level `permissions:` block —
none inherit the default token scope. Six workflows are
`contents: read` only. **Two — `claim-grade.yml` and
`data-source-check.yml` — additionally declare `pull-requests: write`**
so they can post a comment on the PR. **`claim-grade.yml` also consumes
`ANTHROPIC_API_KEY` / `OPENAI_API_KEY` and sends PR title/body/commit
text to that third-party LLM endpoint.** If you adopt these workflows,
know that before you copy `.github/` in: they can comment on any PR
using the repo token, and one makes an outbound network call under a
repo secret. A project that does not want the AI grader should delete
`claim-grade.yml` (and its secrets) rather than leave it inert.

## See also

- `scripts/ci/README.md` — the underlying check scripts
- `scripts/semgrep/README.md` — the Semgrep rule set
- `.agentile/coverage/GATES.md` — the four-ratchet model the
  workflows enforce
- `.agentile/rules/CORE_RULES.md` — the rules these workflows
  back-stop
