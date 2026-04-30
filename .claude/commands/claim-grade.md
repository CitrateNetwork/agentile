---
description: Run the AI claim grader on a piece of text — commit message, PR body, or sprint section
allowed-tools: Bash
---

You are running the agentile claim grader on text the user provides.

## Procedure

1. Determine the input source:
   - If the user pasted text inline → use that directly
   - If the user references a file → read the file
   - If the user references a PR number → use `gh pr view <N>
     --json title,body` to fetch
   - If the user references a commit → use `git show <hash>
     --format=%B --no-patch` to fetch the message

2. Pipe the text into `scripts/ai/grade_claim.py`:

   ```bash
   echo "<text>" | scripts/ai/grade_claim.py
   ```

   Or for a PR:

   ```bash
   scripts/ai/grade_pr.py --pr <N>
   ```

3. Parse the JSON output and present to the user:
   - The score (0-10) and verdict
   - The reasons (concise)
   - The suggested rewrite, if the score < 7
   - Note if the grader returned `verdict: "grader-unavailable"`
     because no API key is set — point them at the README for setup

## Provider note

The grader auto-selects:
- Anthropic via `ANTHROPIC_API_KEY` (preferred — Claude Haiku 4.5)
- OpenAI via `OPENAI_API_KEY` (fallback — gpt-4o-mini)
- Returns informational no-op if neither is set

Don't try to set the API key for the user. If neither is set,
explain the setup options and stop.

## Interpretation

The grader is a **soft gate**. A low score means "a human should
look at this," not "this work is bad." The user decides whether to
rewrite. Don't pressure for a rewrite if the user says the score
was wrong — that's a calibration data point, not a verdict.
