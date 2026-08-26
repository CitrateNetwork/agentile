---
name: journal
description: Seed a new Agentile journal entry with Rule-12 frontmatter and an ISO-timestamped filename under .agentile/docs/journals/. Use when the user says "journal", "log entry", "new journal", or wants to record today's work in the journal corpus.
allowed-tools: Bash, Write, Read
---

# Journal Entry

Seeds a journal entry under `.agentile/docs/journals/`.

## When to Use

- The user wants to record a session's work as a dated journal entry.
- The user says "journal", "log entry", "new journal", "today's entry".

## When NOT to Use

- The work has a generalizable lesson + a proposed enforcement surface → use the `case-study` skill instead (case studies have a higher bar).
- The work is a decision-driven architecture record → write an ADR under `.agentile/adrs/`.
- The work is historical-context/argumentative prose → use the `essay` skill.
- The user wants the sprint daily entry → use the `sprint` skill (`scripts/sprint.sh daily`).

## Procedure

1. Get the current UTC time in ISO 8601 with file-friendly minute precision (`YYYY-MM-DDTHHMM`):
   ```bash
   date -u +%Y-%m-%dT%H%M
   ```
   Also capture the full second-precision timestamp for frontmatter:
   ```bash
   date -u +%Y-%m-%dT%H:%M:%SZ
   ```

2. Get the current git branch:
   ```bash
   git rev-parse --abbrev-ref HEAD
   ```

3. Determine the active sprint ID, if any:
   ```bash
   ls -1 .agentile/sprints/active/ 2>/dev/null | head -1
   ```
   If empty, leave the `sprint:` field blank.

4. Ask the user for:
   - **Title** — descriptive, short, present tense (used in the H1).
   - **Slug** — kebab-case, used in the filename. If they don't provide one, derive it from the title.

5. Read `.agentile/templates/JOURNAL_TEMPLATE.md`. Adapt the frontmatter:
   ```markdown
   ---
   created: <full ISO timestamp>
   branch: <branch>
   author: <user's name if known, else the agent identity>
   sprint: <sprint ID if active>
   status: active
   ---
   ```

6. Write the file at: `.agentile/docs/journals/<HHMM-timestamp>_<slug>.md`

7. Tell the user the filename and offer to open it.

## Important

- Filename ISO timestamp MUST match the frontmatter `created` to the minute (Rule 12).
- Don't fill in the body — the user writes that. Your job is to make the file land in the right shape.
- If the file already exists for that minute + slug, ask whether to append or pick a new slug — never overwrite a journal.
