---
created: 2026-04-30T03:45:00Z
branch: main
author: Claude Opus 4.7 (1M context)
status: active
ported_from: github.com/SaulBuilds/citrate (2026-04-30)
---

# Methodology — Index

This folder is the synthesis of how the methodology actually works,
ported from the Citrate blockchain project where it was first
extracted from a corpus of 1,283 markdown documents accumulated
across 13 months of development.

The artifact extracted here is the *workflow*, not the blockchain.
The blockchain was the proving ground; the workflow ports to anything.

## How to read this folder

If you have 5 minutes: read **`METHODOLOGY.md`** §1 (the thesis) and
§10 (the methodology in one paragraph).

If you have 30 minutes: read all of `METHODOLOGY.md` end-to-end.

If you are starting a new project and want the lessons: read
`04_FAILURE_MODES.md` first (the catalog of named anti-patterns), then
`05_WORKFLOWS.md` (how a sprint actually runs), then `METHODOLOGY.md`
§9 (what ports vs what doesn't).

If you are evaluating whether to adopt Agentile: read
`06_CHRONOLOGY.md` (the 8 phases) to see how the methodology installed
itself reactively, not by design.

## Files

| File | What's in it |
|---|---|
| **`METHODOLOGY.md`** | Top-level synthesis. The thesis, the foundations, the rules, the ratchets, the failure modes (in brief), the workflows, the agent-specific layer, the chronology in one table, what ports. |
| `04_FAILURE_MODES.md` | The named anti-patterns catalog — 5 classes, 25+ entries. Each has anchor incident + enforcement surface. The most actionable single document for new projects. |
| `06_CHRONOLOGY.md` | The 8 phases of Citrate. What got built when, what instrument got added at each phase, what failure mode it responded to. |

## Files to come (deliverables in flight)

| File | What's planned |
|---|---|
| `01_THESIS.md` | One-page distillation for non-engineering stakeholders. |
| `02_FOUNDATIONS.md` | Philosophy + institutional layers (SPIRIT/SOUL/AGENT) + the 12 rules in detail. |
| `03_RATCHETS.md` | The 4 ratchets (test count, TLA+ specs, CI tripwires, frontmatter coverage) with their command lines, baselines, and how they hold under refactors. |
| `05_WORKFLOWS.md` | The 4 lifecycle patterns (standard sprint / audit-driven sprint / remediation track / ceremony) at the level of executable runbook. |
| `07_PORTABILITY.md` | What ports verbatim to a fresh project; what ports in spirit but needs adapting; what's Citrate-specific. The skeleton-repo design lives here. |

## What lives outside this folder

- The **chronological index** of every doc:
  `.agentile/INDEX/INDEX_CHRONOLOGICAL.md`
- The **naming convention** that made chronological reading possible:
  `.agentile/INDEX/PROPOSED_NAMING_CONVENTION.md`
- The **rename plans** documenting what was renamed when:
  `.agentile/INDEX/RENAME_PLAN.md`,
  `.agentile/INDEX/SPRINT_RENAME_PLAN.md`
- The **case studies** these documents synthesize:
  `.agentile/docs/case_studies/`
- The **essays** that argue the methodology in different vocabularies:
  `.agentile/docs/essays/`
- The **journals** that record the reasoning at the time:
  `.agentile/docs/journals/`
- The **rules** themselves: `.agentile/rules/CORE_RULES.md`
- The **foundation tier**: `.agentile/SPIRIT.md`, `.agentile/SOUL.md`,
  `.agentile/AGENT.md`, `.agentile/AGENT_ENTRY.md`

## How this folder was produced

This synthesis was written 2026-04-30 by Claude Opus 4.7 (1M
context), reading the chronologically-ordered corpus that the
2026-04-29 → 2026-04-30 cleanup made readable for the first time
(575 historical docs were backfilled with Rule-12 frontmatter; 285
journals/essays/case-studies were renamed to
`YYYY-MM-DDTHHMM_<slug>.md`; 96 sprint folders were renamed to
`YYYY-MM-DD-sprint-<slug>/`; 735 cross-references were rewritten).
Without that cleanup, the corpus could not have been read in
chronological order, and this synthesis could not have been written
faithfully.

The synthesis is intended as the source for three downstream
deliverables (still in flight):

1. **A skill set + workflow set** specifically tuned for Claude Code
   (`.claude/` setup, slash commands, hooks).
2. **An agent-agnostic version** of the same that works with any
   tool-using LLM agent.
3. **A skeleton repository** anyone can clone to start a new project
   with the methodology pre-installed, including:
   - inline AI-internal-speech grading (CI pass that reads commit
     messages, sprint files, journal entries for compressed-level
     claims, and grades them against the release-truth standard);
   - human eval + grading hooks at PR-merge gates;
   - benchmarking harness aligned with the daily benchmark rule.

Those three are tracked as tasks #77 and #78 in the project's
`.task` system.
