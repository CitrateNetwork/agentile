---
description: Start a new journal entry with proper Rule-12 frontmatter and ISO-timestamped filename
allowed-tools: Bash, Write, Read
---

You are seeding a journal entry under
`.agentile/docs/journals/`.

## Procedure

1. Get the current UTC time in ISO 8601 with the file-friendly minute
   precision (`YYYY-MM-DDTHHMM`):

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
   - **Title** — descriptive, short, present tense (used in the H1)
   - **Slug** — kebab-case, used in the filename. If they don't
     provide one, derive it from the title.

5. Read the journal template at
   `.agentile/templates/JOURNAL_TEMPLATE.md`. Adapt the frontmatter
   block with the values you collected:

   ```markdown
   ---
   created: <full ISO timestamp>
   branch: <branch>
   author: <user's name if known, else "Claude" or whatever they set>
   sprint: <sprint ID if active>
   status: active
   ---
   ```

6. Write the file at:
   `.agentile/docs/journals/<HHMM-timestamp>_<slug>.md`

7. Tell the user the filename and offer to open it in the editor.

## Important

- Filename ISO timestamp MUST match the frontmatter `created` to the
  minute (Rule 12).
- Don't fill in the body — the user writes that. Your job is to make
  the file land in the right shape.
- If the file already exists for that minute + slug, ask the user
  whether to append or pick a new slug — never overwrite a journal.
