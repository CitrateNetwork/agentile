---
name: essay
description: Seed a new Agentile essay with Rule-12 frontmatter under .agentile/docs/essays/. Essays are historical context, not governance — they survive across branches even when the architecture they describe is replaced. Use when the user says "essay" and wants to defend a sharp claim with historical framing.
allowed-tools: Bash, Write, Read
---

# Essay

Seeds an essay under `.agentile/docs/essays/`.

## When to Use

- The user wants to write historical context / a defended claim with a sharp frame.
- The user says "essay" and understands this is NOT governance (essays survive even when architecture changes).

## When NOT to Use

- The user wants to write rules or procedures → that's a workflow doc or an ADR, not an essay.
- The user has a specific incident + generalizable lesson + enforcement surface → use the `case-study` skill.
- The user just wants today's work logged → use the `journal` skill.
- The user is making an architecture decision → write an ADR under `.agentile/adrs/`.

## Procedure

Same procedure as the `journal` skill but:

- Output directory: `.agentile/docs/essays/`
- Template: `.agentile/templates/ESSAY_TEMPLATE.md`
- Banner reminder: essays are HISTORICAL CONTEXT, not governance (the template's leading comment block enforces this — preserve it in the seeded file).

## After seeding

Remind the user that:

1. The essay's frame should be sharp — name the claim it defends in the epigraph.
2. Essays survive across branches even when the architecture they describe is replaced — that's a feature, not a bug.
3. If the user finds themselves wanting to write rules or procedures, they want a workflow doc or an ADR, not an essay.
