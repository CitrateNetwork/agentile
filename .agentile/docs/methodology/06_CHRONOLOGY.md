---
created: 2026-04-30T03:45:00Z
branch: main
author: Claude Opus 4.7 (1M context)
status: active
ported_from: github.com/CitrateNetwork/citrate (2026-04-30)
---

> **EXAMPLE chronology.** Your project will have its own phase
> structure with its own instruments accumulating reactively. Use
> this document as a *template* for tracking your project's
> install-record. The pattern (each phase adds one durable
> instrument; none gets removed) is the durable insight; the
> specific 8-phase trajectory below is Citrate's.

# The 8 Phases of Citrate

> A walking tour of how the methodology installed itself, phase by
> phase. Each phase added one durable instrument. None has been
> removed. Together they constitute the workflow that built a
> Layer-1 in 4 months.

---

## Phase 1 — Pre-Audit Greenfield (through 2026-02-16)

**Move:** Unstructured velocity.

The repo arrives at the framework boundary already containing a
working Layer-1 implementation: GhostDAG consensus, Tauri+React GUI,
EVM stack, multiple sprints' worth of code. Sprint folders existed
under `.sprint/`, but no audit framework, no track naming convention,
no Rule 12, no tripwires. Most documents from this period have no
frontmatter — they were backfilled retroactively in 2026-04-30.

This phase is visible only as fossils. The pre-rule-12 docs that say
`status: archived` are mostly from this phase.

**What got built:** the substrate. The methodology had not yet named
itself.

---

## Phase 2 — First Adversarial Program (2026-02-17 → 2026-03-01)

**Move:** Finding-ID → WP traceability. Release gates as objective
acceptance criteria.

**Trigger:** The 2026-02-17 production-readiness audit produced
`ADVERSARIAL_DEEP_AUDIT.md`, `THREAT_MATRIX.md`, and
`ARCHITECTURE_CONFLICTS.md`. Nothing on the chain was safe yet.

**Sprints:** F (transaction authenticity), G (block integrity), H
(network trust BFT), I (RPC operational hardening), J (adversarial
verification gates), K (post-remediation closure), K' (parallel CI
hygiene).

The alphabetic letters had no semantic meaning at the start — they
were just a sequence. But because each sprint took ~2 weeks and the
audit had clear dependency ordering (transactions → blocks → network
→ ops → gates → residuals), the alphabet *became* the ordering.

**What got named for the first time:**
- Audit-finding-ID → WP traceability (C-01 → WP-F.1).
- Release gates as objective acceptance ("no unauthorized admission,
  nonce equality enforced, fork-choice integrated, peer ID
  cryptographically bound, adversarial CI green").
- The lesson that "remediation complete" and "audit complete" are
  different (Sprint K had to exist because Sprint J's
  release-gate-passed declaration didn't actually close the audit).
- Sprint K' as the first acknowledgment that hygiene cleanup is
  itself a sprint.

**The instrument added to the toolkit:** the OVERVIEW + FINDINGS_MAP +
REVALIDATION_DELTA_MAP triad. This three-document pattern would
become the template for every later remediation track.

---

## Phase 3 — Paper-Driven Build (2026-03-01 → 2026-03-15)

**Move:** Scope-via-paper. Every WP traceable to a paper section.

**Sprints:** L (paraconsensus foundation), M (aggregation
checkpoints), N (routing), O (LoRA adapters), P (cooperation bridge),
Q (GUI E2E), R (SDK), S (public testnet launch), T (school pilot).

Long alphabetic-letter chain, but now with semantic content: each
sprint had a "Paper Element / Implementation / Module" mapping table
in its `SPRINT.md`. Paper II (the federated learning paper) drove the
WBS directly.

**The instrument added:** scope traceability to a primary source.
When a WP says "implement φ classification function," the SPRINT.md
shows that φ comes from Paper II §3.2. Scope creep gets caught when
someone proposes a WP that has no paper anchor — Amendment 1 to
Sprint L (φ added mid-sprint) is the model: scope amendment with
traceable origin, not stealth.

**What this phase made possible:** the rest of the project could
diverge from "what feels right" to "what the paper says." The agent's
ambiguity-as-permission failure mode (Class E1) lost its main fuel.

---

## Phase 4 — Audit-Readiness Hardening (2026-03-02 → 2026-03-18)

**Move:** Test count, TLA+ count, unwrap count, coverage % all gated
as ratchets.

**Sprints:** V (assessment), W (P0 remediation), X (P1/P2 + API
hardening), Y (audit readiness — first sprint to publish baseline +
target metrics for tests + specs), Z (VRF prevrandao), AA (critical
test gaps), BB (fuzzing + property tests), CC (formal verification),
DD (integration polish), EE/FF/GG (final hardening + distribution).

**The instrument added:** explicit baseline + target tables in every
sprint's SPRINT.md. Sprint Y was the first to publish:

| Metric | Baseline | Target |
|---|---:|---:|
| Rust unit tests | 1,081 | 1,081 + new |
| Proptest declarations | 10 | 50+ |
| TLA+ specs | 7 | 10 |
| TLA+ invariants | 26 | 64 |
| `.unwrap()` in consensus | 6 | 0 |

By the end of Phase 4 the test count had climbed to ~2,000 and the
TLA+ spec count to 10+. The ratchets were live.

**What got systematized:** the per-crate coverage ratchet (each crate
has documented current % / target % / gap %); the unwrap classification
(HIGH/MEDIUM/LOW with 5 transformation rules); the sub-sprint pattern
(HH/II/JJ for unwrap elimination, RR/SS/TT/UU for coverage).

---

## Phase 5 — Soft Launch + v1 Phases (2026-03-19 → 2026-03-20)

**Move:** UX as acceptance criterion. "Non-technical user" framing.

**Sprints:** the v1 Phase 1-4 cluster (HH, II, JJ, KK, LL, MM, NN,
OO, PP, QQ, RR, SS, TT, UU); Sprint LAUNCH (systemd services, web
faucet, contract deployment, IPFS bundle, model registry UX, agent
onboarding).

**The instrument added:** acceptance criteria phrased as user
journeys, not feature lists. Sprint LAUNCH's deliverable was *a
non-technical user can download the GUI, onboard, run a model, and
interact with testnet without ever touching a terminal*.

**What got named:** the deferred-polish-with-named-suspects
discipline. Sprint LAUNCH discovered the embedded node was running
chain ID 1; the fix landed mid-sprint. Visual bugs (the Compute
Marketplace card not rendering) got documented as known unknowns
without blocking close — Saul's call: "move forward, we'll tweak
layout after the build is complete."

**The trap that Phase 5 invented:** count inflation. With 12+ services
running, 36+ agent tools, 4 economic-sim integration tests, the
volume of artifacts began to outrun any single agent's review
capacity. Phase 4's ratchets caught it.

---

## Phase 6 — Slint Migration (2026-03-27 → 2026-04-21)

**Move:** Scrap-and-rebuild when the framework is the bottleneck. Per-WP
"Data Sources (Rule 11)" enforcement.

**Sprints:** SLINT-A (foundation), SLINT-B (core user), SLINT-C (DAG
explorer), SLINT-D (AI models). All four squash-merged to main on
2026-03-31.

**Trigger:** Tauri + WebKit fragility on Linux had been accumulating
since Phase 1. The third-greenfield case study (`THIRD_GREENFIELD_IS_THE_CHARM.md`)
captured the rewrite-decision framework: 5 conditions to justify a
rewrite, 5 conditions that mean you're patching around a runtime-layer
bug below the layer you control.

**The instrument added:** the headless service crate.
`citrate-desktop-app` compiles and tests without Tauri/WebKit/window
framework. View model traits separate domain from UI. The Slint
binary depends on the headless crate, not the other way around. This
made the Tauri-to-Slint migration a *replace-the-shell* operation
rather than a rewrite.

**What this phase systematized:** Rule 11 (data source tracing)
became enforceable per-WP. Every IPC command now lists "Data Source
(contract + RPC method)" in its WP definition. The Real Backend
Loophole (Class A3) was named in this phase.

**What got abandoned:** Tauri + React. The 22 Slint files of the
SLINT-A handoff had to compile with no callback drift. The 716+
existing GUI tests of the React era were not all carried over;
Slint's UI tests are largely view-model tests, not the integration
tests of the previous era. (This is the methodology's pressure point
on test-quality-vs-count, addressed by Gherkin + TLA+ pairing in Phase
8.)

---

## Phase 7 — P950 Executor Parallelism + CM Marketplace (2026-04-21 → 2026-04-23)

**Move:** TLA+-first reflexive. Staged execution (S0/S1+) gates on
operational soak.

**Sprints:** P950-A.1 → A.5 (executor MVCC: spec → impl → tests →
bench → docs); P950-B (embedded weights removal); P950-C (GUI polish);
P960 family (agent-chain tools, contracts IDE, IPFS UX, compute
opt-in, brand typography, contracts simplification, learning rebuild,
MCP host); CM-01 → CM-07 (compute marketplace listing → x402 → batch
inference → buyer webapp → compute pool → gateway billing →
DataParallel training).

**The instrument added:** TLA+-first as the explicit gate, codified
in P950-A.1's SPRINT.md: "We are not going to write that code until
we have a verified TLA+ specification saying what it must do."

P950-A.5 proved the pattern paid off: 14 safety invariants + Progress
liveness proven before any concurrency code. No scramble debugging
concurrency bugs. Stress tests written before removing the executor
mutex; speedup gate (≥2×) met at 2.41× across 1→8 workers.

**What got named:** the WP-as-sprint pattern. What was a 5-task WP
under earlier conventions was now 5 separate sprints (A.1 → A.5)
each with its own SPRINT.md. This enabled per-WP frontmatter scoping
and per-WP commit traceability.

**Staged execution (S0/S1+):** CM-07 DataParallel training shipped at
S0 level (spec gate + first contract); S1+ deferred until CM-05
soaks ≥1 month in production. The whole DataParallel epic exists as
TLA+ spec + contract + worker crate + coordinator + webapp tab — but
production rollout is gated on operational evidence of upstream
stability.

---

## Phase 8 — Re-audit Remediation Tracks (2026-04-24 → present)

**Move:** Track-naming reflexive. Per-finding frontmatter scoping.
Cross-agent authorship recorded. Honesty-as-deliverable.

**Tracks:** RM-A (KDF/AEAD), RM-B (consensus correctness), RM-C (RPC
bounds, validate-then-relay, atomicity), RM-D (Solidity), RM-E (GUI
agent), RM-F (CI/CD permissions hardening), RM-J (testnet Tier-0
blockers — authored by Codex GPT-5), RM-K (Tier-1), RM-M1/M2/M3 (AI
verification precompiles), RM-DOC-1 (documentation parity + Gradient
Papers v3), RM-FL-1..5 (federated learning production track).

**The instruments added:**

1. **The track unit.** When an audit produces enough findings that
   one sprint can't close them, the RM-track is the unit of
   remediation, not the sprint. Each track has its own planset
   folder, its own phase reports, its own per-track baseline metrics.

2. **Per-finding frontmatter scoping.** RM-A1 frontmatter says
   `audit_findings_in_scope: [WAL-01, GUI-L-02, M-05 (partial),
   EXT-01 (param decision)]`. The closure record carries the audit
   ID forward.

3. **Cross-agent authorship.** RM-J was authored by Codex GPT-5; the
   sprint frontmatter records it. Tracks are durable enough to
   survive author handoffs because the planset (not the agent's
   memory) holds the state.

4. **Semgrep tripwire ratchet.** Every audit-finding-class becomes a
   Semgrep rule (`wal-01-argon2-default.yaml`,
   `gui-l-02-edu-sha3-kdf.yaml`). Started at zero in Phase 1; reached
   27 by RM-FL-5.

5. **The mature 8-step method per WP**, codified in RM-FL-1's
   frontmatter:
   - TLA+ spec audit + adversarial extension
   - Gherkin scenarios
   - Failing tests + tripwires (RED)
   - Implementation (GREEN)
   - Refactor + optimize
   - Adversarial fuzz + e2e
   - Adversarial TLA+ model-check
   - Journal

6. **Honesty-as-deliverable.** RM-FL-5 frontmatter explicitly says
   the closing essay must report what was found, not what was hoped.
   Falsified is a valid closing state, pre-authorized.

**The deepest revelation of Phase 8:** the workflow distrusts its own
claims of completion. Sprint J in Phase 2 declared "all release gates
passed." Sprint K had to exist because revalidation found residuals.
RM-J in Phase 8 had to exist because *another* re-audit (2026-04-26)
found Tier-0 blockers the sprint-of-record had not actually closed
(audit score 865/1000 vs the team's 870 self-assessment). Each `RM-`
prefix is the workflow saying: "we claimed this was done. an audit
said no. here is the track that disagrees with our past selves."

That self-distrust is the project's most durable asset.

---

## What each phase added to the methodology

| Phase | Window | Instrument added |
|---|---|---|
| 1 | through 2026-02-16 | (substrate; methodology not yet named) |
| 2 | 2026-02-17 → 03-01 | Finding-ID → WP traceability; release gates; OVERVIEW+FINDINGS+DELTA triad |
| 3 | 2026-03-01 → 03-15 | Scope-via-paper; amendment with traceable origin |
| 4 | 2026-03-02 → 03-18 | Test ratchet; TLA+ ratchet; unwrap classification; coverage ratchet; per-crate baselines |
| 5 | 2026-03-19 → 03-20 | UX as acceptance; deferred-polish-with-named-suspects |
| 6 | 2026-03-27 → 04-21 | Headless service crate; per-WP Rule 11 enforcement; Real Backend Loophole named |
| 7 | 2026-04-21 → 04-23 | TLA+-first as gate; WP-as-sprint; staged execution (S0/S1+) |
| 8 | 2026-04-24 → ongoing | Track unit; per-finding scoping; cross-agent authorship; Semgrep tripwire ratchet; honesty-as-deliverable; mature 8-step method |

---

## What the chronology says about the methodology

Three observations:

1. **The methodology installed itself reactively.** Each instrument
   was a response to a specific failure. Phase 2's release gates
   responded to "audit complete ≠ remediation complete." Phase 4's
   ratchets responded to "speed without depth produced 15 mocks."
   Phase 6's Rule 11 enforcement responded to the Real Backend
   Loophole. Phase 8's tripwire ratchet responded to fix-without-
   tripwire findings recurring.

2. **No instrument has been removed.** Every ratchet still holds.
   Every workflow document still applies. The `.agentile/` corpus is
   load-bearing — pulling out any single layer would break a downstream
   discipline.

3. **The methodology became more durable as the agent's role
   expanded.** Phase 1: agent does what it's told. Phase 4: agent
   measures and reports. Phase 6: agent designs services within
   constraints. Phase 8: agent runs sprints autonomously, with
   cross-agent review (Codex GPT-5 reviewing Claude's work in RM-J).
   The methodology scaled because it offloaded *trust* from the agent
   to the artifacts the agent produces.

The pattern that emerges: **trust in the process, not the agent**.
The agent without guardrails is a liability. The agent with a proven
methodology, mechanical enforcement, and a clear sprint plan is an
asset that works through the night while the founder sleeps.
