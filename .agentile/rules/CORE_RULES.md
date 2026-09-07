---
created: 2026-04-30T03:40:00Z
branch: main
author: Saul Loveman + Claude Opus 4.7 (1M context)
status: active
ported_from: github.com/CitrateNetwork/citrate (2026-04-30)
---

> **Note on examples.** The verification commands and path examples
> below are from the Citrate blockchain project (Rust + Solidity + Slint).
> The *rules* are language- and domain-agnostic; the *commands* are
> the example invocations. Adapt them to your project's toolchain.
> The four-ratchet enforcement model holds regardless of language —
> only the canonical-count commands change.

# Core Rules

> 10 non-negotiable rules for every contributor — human or AI.
> Violations are marked as **BLOCKER** (stops all work) or **GATE** (stops the current step).

---

## Rule 0: Read AGENT_ENTRY.md Before Any Work

**Statement:** Every session begins by reading `AGENT_ENTRY.md`. No exceptions.

**Why:** Context drift is the primary cause of wasted work. Cold-starting without orientation produces code that conflicts with active sprints, duplicates existing implementations, or violates architectural decisions.

**Verification:**
- The first action in any session log is reading `AGENT_ENTRY.md`.
- CONFIG.md constants are referenced correctly in all produced artifacts.

**On violation:** **BLOCKER.** All work produced without reading AGENT_ENTRY.md is suspect and must be re-reviewed from scratch.

---

## Rule 1: Plan Before You Code

**Statement:** Check `sprints/CURRENT.md` and the active sprint's `SPRINT.md` before writing any code. If no sprint exists for the work, create one first.

**Why:** Unplanned work creates orphan code that nobody expects, nobody reviews, and nobody maintains. Sprint files are how the team (and future agents) know what happened and why.

**Verification:**
- Every commit traces to a Work Package (WP) in an active sprint.
- `sprints/CURRENT.md` reflects the work being done.

**On violation:** **GATE.** Code written without a sprint item will not be merged. Create the sprint entry retroactively and justify the gap.

---

## Rule 2: No Mocks, Stubs, or TODOs in Production Code

**Statement:** All delivered code must be fully functional and production-ready. Do not create mock implementations, placeholder functions, TODO comments, or stub methods. **This includes default constructors that silently use fake backends.**

**Why:** Incomplete code is tech debt with compound interest. It misleads other contributors into thinking functionality exists when it does not. In a blockchain system, stubs can mask critical safety gaps.

**Known Failure Mode — The "Testing Backend" Loophole (see `THE_RULE_FOLLOWERS_PARADOX.md`):**

An AI agent will create types named `StubXxxBackend` and rationalize them as "for testing only," then wire them as the **default** in production constructors (`Service::new()`). The result: `AppCore::new()` silently creates an application where every service returns fake data. This satisfies the surface pattern ("no function named mock()") while violating the semantic property ("every code path connects to real data").

**To prevent this:**
1. Test-only backend types MUST be behind `#[cfg(test)]`. If it doesn't compile in `--release`, it can't ship.
2. Default constructors (`new()`) MUST use real backends that connect to real data sources (filesystem, network, database).
3. `with_backend()` constructors for dependency injection in tests are fine — but the injected type must be `#[cfg(test)]`.
4. If the real backend cannot be implemented yet, the service CANNOT be created. Do not create a service with a fake backend and call it "ready."

**Verification:**
- `grep -rn "TODO\|FIXME\|HACK\|STUB\|unimplemented!\|todo!" src/` returns zero hits in new code.
- `grep -rn "Stub\|Mock\|Fake\|Dummy" src/ --include="*.rs"` — any hits must be behind `#[cfg(test)]`.
- All public functions have complete implementations with error handling.
- `cargo build --release` compiles cleanly without any test-only types.
- Default constructors (`::new()`) instantiate real backends, not test doubles.

**On violation:** **GATE.** PR will not be approved. Replace every stub with a working implementation or remove the dead code entirely.

---

## Rule 3: Test Count Only Increases (Test Ratchet)

**Statement:** The total number of passing tests must increase or stay the same with every sprint. It must never decrease.

**Why:** Removing tests to make the build green is a hallmark of codebase decay. If a test is genuinely obsolete, it must be replaced with an equivalent or better test in the same commit.

**Verification:**
- Record baseline in `coverage/BASELINE.md` at sprint start.
- Record final count in sprint `REPORT.md` at sprint end.
- `cargo test --workspace 2>&1 | grep "test result"` shows count >= previous sprint.

**On violation:** **BLOCKER.** Sprint cannot close with fewer passing tests than it started with. Restore or replace removed tests before proceeding.

---

## Rule 4: Every Feature Traces to a Sprint Item

**Statement:** Every feature, bug fix, or refactor must be linked to a Work Package in an active sprint. Untracked work is not permitted.

**Why:** Traceability is how we maintain accountability, generate accurate reports, and enable future agents to understand the provenance of every change.

**Verification:**
- Commit messages reference a WP (e.g., `feat(WP-3.2): add ECVRF proposer election`).
- Sprint `SPRINT.md` has a corresponding entry with status updates.

**On violation:** **GATE.** Commit must be amended with a WP reference, or a sprint entry must be created retroactively.

---

## Rule 5: All Code Must Pass Clippy with -D warnings + Zero Unwraps

**Statement:** Rust code must compile cleanly under `cargo clippy --all-targets --all-features -D warnings`. No suppressions without documented justification. **Additionally, zero `.unwrap()` calls are permitted in production or test code.**

**Why:** Clippy warnings catch real bugs. `.unwrap()` calls provide zero context on failure — use `.expect("reason")` in tests or `?` in production code. In a blockchain wallet, a panic from `.unwrap()` in production means lost user trust. In tests, `.unwrap()` produces "called Option::unwrap on None" — useless for debugging.

**Verification:**
- CI runs clippy with `-D warnings` on every PR.
- Local verification: `cargo clippy --all-targets --all-features -D warnings` exits 0.
- Any `#[allow(...)]` annotation must have an adjacent comment explaining why.
- `grep -rn '\.unwrap()' src/ tests/ | grep -v unwrap_or | wc -l` returns **0**.
- Production code uses `?` or `match` for error handling.
- Test code uses `.expect("descriptive message")` or `.expect_err("expected error")`.

**On violation:** **GATE.** PR will not merge. Fix the warnings, replace unwraps, or document the suppression justification.

---

## Rule 6: Audits Are Dated and Immutable

**Statement:** Audit reports are created in dated directories (`audits/YYYY-MM-DD-name/`) and are never modified after creation. Corrections go in new audit files.

**Why:** Audit integrity depends on immutability. If audits can be retroactively edited, they lose all evidentiary value. Historical accuracy requires that past findings remain exactly as they were recorded.

**Verification:**
- Audit directories follow `YYYY-MM-DD-name` format.
- Git log shows no modifications to files in `audits/` directories after their creation date.
- New findings produce new audit files, not edits to old ones.

**On violation:** **BLOCKER.** Revert the edit. Create a new audit file with the correction and a reference to the original.

---

## Rule 7: Documentation Updates Accompany Code Changes

**Statement:** Code changes that affect public APIs, configuration, architecture, or user-facing behavior must include corresponding documentation updates in the same PR.

**Why:** Documentation that lags behind code is worse than no documentation — it actively misleads. Keeping docs and code in the same commit ensures they stay synchronized.

**Verification:**
- PRs that touch `pub fn`, `pub struct`, config files, or CLI arguments include doc updates.
- Crate `README.md` reflects current API surface.
- `CHANGELOG.md` has an entry for user-facing changes.

**On violation:** **GATE.** PR will not merge until documentation is updated. Reviewers check for doc changes alongside code changes.

---

## Rule 8: Security-Sensitive Changes Require Review

**Statement:** Changes to consensus, cryptography, key management, transaction validation, or access control must be reviewed by at least one other contributor (human or qualified agent) before merge.

**Why:** Security bugs in a blockchain are exploitable and potentially irreversible. The cost of a missed vulnerability far exceeds the cost of a review cycle.

**Verification:**
- PRs touching `core/consensus/`, `core/execution/` (precompiles, signature verification), `wallet/` (key handling), or `core/bridge/` require an approving review.
- The reviewer is recorded in the PR metadata.
- Formal verification (TLA+ or invariant tests) is strongly recommended for consensus changes (see `FORMAL_VERIFICATION_RULES.md`).

**On violation:** **BLOCKER.** Merge is blocked. No self-approvals for security-sensitive paths.

---

## Rule 9: The Sprint File Is the Source of Truth

**Statement:** The sprint `SPRINT.md` file is the canonical record of what was planned, what was done, and what the outcome was. Not your memory. Not a chat log. Not an internal plan file.

**Why:** Agents have no persistent memory across sessions. Humans forget. Chat logs are unsearchable and ephemeral. The sprint file is the only artifact that survives and is accessible to all future contributors.

**Verification:**
- Sprint status is updated in `SPRINT.md` after every work session.
- `DAILY.md` entries exist for each active work day.
- Completed sprints have a `REPORT.md` and `RETRO.md`.

**On violation:** **GATE.** Work that is not recorded in the sprint file did not happen. Update the file before claiming completion.

---

## Rule 10: Formal Verification for Consensus Changes

**Statement:** Changes to consensus, finality, or proposer election logic should have corresponding TLA+ specs or invariant tests. See `FORMAL_VERIFICATION_RULES.md` for details.

**On violation:** **GATE.** Consensus PRs without formal verification artifacts require explicit justification.

---

## Rule 11: Mock Budget and Data Source Tracing

**Statement:** Every sprint has a mock budget of 0 for production code. If seed data is required for development, it must be:
1. Registered in a `MOCKS.md` file at the project root
2. Gated behind a `dev-mode` feature flag
3. Accompanied by a replacement WP in the next sprint's backlog
4. Blocked from release builds via compile-time check

**Acceptance criteria must name data sources:**
- BAD: "Dashboard shows earnings"
- GOOD: "Dashboard shows earnings from ContributionAccounting.sol via eth_call"

**Data Source Tracing — every IPC command must identify its source BEFORE implementation:**

| Step | Requirement | Gate |
|------|-------------|------|
| 1 | Name the on-chain contract + method | BLOCKER — cannot create IPC command without this |
| 2 | Implement the contract query/transaction code FIRST | BLOCKER |
| 3 | Write the IPC command wrapping the real call | — |
| 4 | Write an integration test verifying end-to-end data flow | GATE — WP cannot close without this |

If the contract doesn't exist yet, write the contract FIRST. If the contract can't be written this sprint, the IPC command CANNOT be created — the frontend shows a loading/unavailable state, not fake data.

**Verification:**
- `grep -rn "seed data\|mock\|hardcoded\|placeholder" src/ --include="*.rs" --include="*.ts"` returns 0 results in release builds.
- `MOCKS.md` is empty or absent in release-ready branches.
- All WP acceptance criteria include a named data source.

**On violation:** **GATE.** Sprint cannot close with unregistered mocks. Registered mocks must have replacement WPs.

**Background:** See `docs/case_studies/MOCK_PERSISTENCE.md` for the full rationale — Knight Capital ($440M), TODO lifespan research, and 6 mechanisms that cause temporary code to become permanent.

---

## Rule 12: All Documentation Must Have Timestamps and Branch Context

**Statement:** Every document created or updated in this repository — journals, essays, case studies, sprint files, ADRs, specs, planset files — MUST include a frontmatter block with creation timestamp, branch, and author. Updates append a changelog entry rather than modifying the timestamp.

**Why:** Without timestamps and branch context, documents from different phases of development are indistinguishable. An essay written during the Tauri/React era (pre-March 27) looks identical to one written during the Slint era (March 27+). This causes agents and humans to act on stale information, repeat solved problems, and build on deprecated architecture. Branch context tells you whether the document applies to the current work or is historical.

**Required frontmatter format:**

```markdown
---
created: YYYY-MM-DDTHH:MM:SSZ
branch: <git branch name>
author: <contributor name or zooid>
sprint: <sprint ID if applicable>
status: active | superseded | archived
superseded_by: <path to replacement doc, if status=superseded>
---
```

**Rules:**
1. **Every new document** gets this frontmatter at creation time. No exceptions.
2. **Journals** use ISO 8601 timestamps in both the filename (`YYYY-MM-DDTHH_TITLE.md`) AND the frontmatter.
3. **Sprint files** include the sprint ID and branch in frontmatter.
4. **ADRs and specs** include status field. When an ADR is superseded, update status to `superseded` and add `superseded_by` pointer.
5. **Essays and case studies** include the branch they were written on — this determines whether conclusions still apply.
6. **When updating an existing document**, do NOT change the `created` timestamp. Instead, add a `## Changelog` section at the bottom with the update date and what changed.
7. **Documents without frontmatter are pre-rule artifacts** — they are treated as historical context, not current guidance.

**Verification:**
- New documents have the frontmatter block as the first content.
- `grep -rL "^---" .agentile/docs/ .agentile/sprints/ .agentile/planset/` on new files returns 0 results.
- Branch field matches the branch the document was committed on.

**On violation:** **GATE.** Document is incomplete until frontmatter is added. Existing pre-rule documents are exempt but should be updated when touched.

---

## Quick Reference

| # | Rule | Enforcement |
|---|------|-------------|
| 0 | Read AGENT_ENTRY.md first | BLOCKER |
| 1 | Plan before you code | GATE |
| 2 | No mocks/stubs/TODOs | GATE |
| 3 | Test ratchet (count never decreases) | BLOCKER |
| 4 | Every feature traces to a sprint item | GATE |
| 5 | Clippy -D warnings clean | GATE |
| 6 | Audits are immutable | BLOCKER |
| 7 | Docs accompany code changes | GATE |
| 8 | Security changes need review | BLOCKER |
| 9 | Sprint file is source of truth | GATE |
| 10 | Formal verification for consensus | GATE |
| 11 | Mock budget = 0, data source tracing | GATE |
| 12 | All docs must have timestamps + branch context | GATE |
