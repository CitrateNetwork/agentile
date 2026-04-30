---
created: 2026-04-30T05:00:00Z
branch: main
author: agentile-skeleton
status: template
---

<!--
AUDIT TEMPLATE — Agentile.

Copy this file to:
  .agentile/audits/YYYY-MM/YYYY-MM-DD-<slug>/AUDIT.md

⚠️  RULE 6: AUDITS ARE IMMUTABLE.

Once committed, this directory and every file in it are read-only.
Corrections, addenda, or partial retractions go in a NEW dated
audit directory that references this one. Do NOT amend an existing
audit — git history of edits to an audit destroys its evidentiary
value.

If a finding turns out to be wrong, write a follow-up audit titled
e.g. "2026-MM-DD-<slug>-correction" that references the original
finding's ID and explains the correction. The original stands.
-->

# Audit: <subject> — YYYY-MM-DD

## Header

| Field | Value |
|-------|-------|
| **Auditor** | <name or zooid> |
| **Audit type** | full-repo / scoped (<scope>) / threat-model / dependency / regression |
| **Target commit** | `<full git hash>` (do NOT use a moving ref like `main`) |
| **Target branch** | `<branch at the time of audit>` |
| **Target version** | <semver tag if any> |
| **Score (if scored)** | <N> / <denominator> |
| **Score target** | <N> / <denominator> (e.g. production-readiness gate) |
| **Audit ID** | `<TRACK>-<DATE>-<SLUG>` (used to reference findings cross-document) |

## Threat model

<Single paragraph. What classes of attacker / failure are in scope
for this audit, and what is explicitly out of scope. An auditor
who can't state their threat model can't write a coherent audit.>

**In scope:**
- <attacker class 1, e.g. "external party with funded RPC access">
- <failure mode 2, e.g. "supply-chain compromise of a build toolchain">

**Out of scope:**
- <e.g. "physical access to validator hardware">
- <e.g. "user-side phishing">

## Methodology

<How the audit was performed. Tools, queries, manual review steps.
A reproducible audit is one a second auditor could re-run to verify
results.>

## Summary by severity

| Severity | Count |
|----------|-------|
| CRITICAL | <N> |
| HIGH | <N> |
| MEDIUM | <N> |
| LOW | <N> |
| INFO | <N> |
| **Total** | **<N>** |

## Findings

<!--
Each finding gets a stable ID of the form <TRACK>-<NNN> (e.g.
WAL-014, AGT-003, CI-022). The ID never changes once assigned, even
if severity is later revised — revisions go in a follow-up audit.

Every finding MUST cite file:line. Findings without file:line refs
cannot be made into WPs and therefore can't be remediated against.
-->

### <ID> — <one-line title> [SEVERITY]

| Field | Value |
|-------|-------|
| **Severity** | CRITICAL / HIGH / MEDIUM / LOW / INFO |
| **Component** | <crate / module / contract / pipeline> |
| **File:line** | `path/to/file.ext:NNN` |
| **CWE / class** | <CWE-XXX or descriptive class> |

**Description:**
<2–4 sentences. What the issue is.>

**Impact:**
<What an attacker / failure can do with this. Concrete.>

**Reproduction:**
<Steps, command, or test that demonstrates the issue. If the
finding is preventative (no live exploit), say so.>

**Suggested remediation:**
<Specific, file:line-anchored fix. The auditor proposes; the
remediation sprint executes.>

**Suggested tripwire:**
<A regression-prevention check the project should add to CI so this
class of bug cannot return without a deliberate exception. State as
either a `grep`/`semgrep`/`rg` rule, an invariant test, or a
state-machine spec amendment.>

---

### <ID> — <next finding>

_(Copy block. Repeat for every finding.)_

## Track suggestion

<If this audit's findings are large enough to warrant their own
remediation track (RM-<letter>), suggest the track structure here.
Map findings to phases / sub-sprints. The remediation sprint
authors will refine, but a starting carve-up saves a session.>

| Track phase | Findings included | Score delta target |
|-------------|-------------------|--------------------|
| RM-A | <list of finding IDs> | +<N> |
| RM-B | <list> | +<N> |

## References

- <link to prior audit this supersedes / extends>
- <link to spec, ADR, or external advisory>
- <link to threat model document>
