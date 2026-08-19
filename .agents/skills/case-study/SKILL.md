---
name: case-study
description: Seed a new Agentile case study with Rule-12 frontmatter under .agentile/docs/case_studies/. A case study anchors a specific incident to a generalizable lesson and a proposed enforcement surface. Use when the user says "case study" and has all three: anchor incident, generalizable lesson, enforcement surface.
allowed-tools: Bash, Write, Read
---

# Case Study

Seeds a case study under `.agentile/docs/case_studies/`.

## When to Use

- The user wants to write a case study AND can articulate all three bars (see below).
- The user says "case study" and has a specific incident + a lesson that could recur + a sketch of what tripwire/lint/workflow change would catch the next occurrence.

## When NOT to Use

- Only an incident, no generalization → use the `journal` skill instead.
- Decision-driven, no anchor incident → write an ADR under `.agentile/adrs/`.
- Argumentative/historical-context prose → use the `essay` skill.

## The three-bar gate

Before seeding, confirm with the user that this work meets the case-study bar:

- **Anchor incident** — there's a specific thing that happened (date, files, observed behavior).
- **Generalizable lesson** — the failure mode could recur in other forms; this isn't just a war story.
- **Enforcement surface** — the user has at least a sketch of what tripwire / lint rule / workflow change would catch the next occurrence.

If any of those three are missing, the work probably wants to be a journal entry (incident only, no generalization) or an ADR (decision-driven, no anchor incident) instead. Suggest the alternative.

## Procedure

Same procedure as the `journal` skill but:

- Output directory: `.agentile/docs/case_studies/`
- Template: `.agentile/templates/CASE_STUDY_TEMPLATE.md`

## After seeding

Remind the user that the case study's value comes from the **enforcement surface** section. A case study without a proposed enforcement is a war story.
