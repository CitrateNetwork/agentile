---
name: claim-grade
description: Run the Agentile AI claim grader on a piece of text — a commit message, PR body, or sprint section — and report the score, reasons, and suggested rewrite. Use when the user says "grade this", "claim-grade", "score my PR", or wants a soft gate on claim honesty before merging.
allowed-tools: Bash
---

# Claim Grader

Runs the Agentile claim grader on text the user provides.

## When to Use

- The user wants a soft gate on claim honesty for a commit message, PR body, or sprint section.
- The user says "grade this", "claim-grade", "score my PR", "is this honest".

## When NOT to Use

- The user wants a hard CI gate → this is a soft gate only; a low score means "a human should look," not "this is bad."
- The user wants to lint code → use the appropriate linter.
- The user wants the four ratchet checks → use the `ratchet-check` skill.

## Procedure

1. Determine the input source:
   - If the user pasted text inline → use that directly.
   - If the user references a file → read the file.
   - If the user references a PR number → `gh pr view <N> --json title,body`.
   - If the user references a commit → `git show <hash> --format=%B --no-patch`.

2. Pipe the text into `scripts/ai/grade_claim.py`:
   ```bash
   echo "<text>" | scripts/ai/grade_claim.py
   ```
   Or for a PR:
   ```bash
   scripts/ai/grade_pr.py --pr <N>
   ```

3. Parse the JSON output and present to the user:
   - The score (0-10) and verdict.
   - The reasons (concise).
   - The suggested rewrite, if the score < 7.
   - Note if the grader returned `verdict: "grader-unavailable"` because no API key is set — point them at the README for setup.

## Provider note

The grader auto-selects:
- Anthropic via `ANTHROPIC_API_KEY` (preferred — Claude Haiku 4.5).
- OpenAI via `OPENAI_API_KEY` (fallback — gpt-4o-mini).
- Returns informational no-op if neither is set.

Don't try to set the API key for the user. If neither is set, explain the setup options and stop.

## Rationalizations to Reject

- Pressuring the user to rewrite when they say the score was wrong — that's a calibration data point, not a verdict.
- Treating a low score as "the work is bad" — it means "a human should look at this."

## Interpretation

The grader is a **soft gate**. The user decides whether to rewrite. Don't pressure for a rewrite if the user says the score was wrong.
