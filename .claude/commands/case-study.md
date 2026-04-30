---
description: Start a new case study with proper Rule-12 frontmatter and ISO-timestamped filename
allowed-tools: Bash, Write, Read
---

You are seeding a case study under `.agentile/docs/case_studies/`.

Same procedure as `/journal` but:

- Output directory: `.agentile/docs/case_studies/`
- Template: `.agentile/templates/CASE_STUDY_TEMPLATE.md`

Before seeding, confirm with the user that this work meets the
case-study bar:

- **Anchor incident** — there's a specific thing that happened
  (date, files, observed behavior)
- **Generalizable lesson** — the failure mode could recur in other
  forms; this isn't just a war story
- **Enforcement surface** — the user has at least a sketch of what
  tripwire / lint rule / workflow change would catch the next
  occurrence

If any of those three are missing, the work probably wants to be a
journal entry (incident only, no generalization) or an ADR
(decision-driven, no anchor incident) instead. Suggest the
alternative.

After seeding, remind the user that the case study's value comes
from the **enforcement surface** section. A case study without a
proposed enforcement is a war story.
