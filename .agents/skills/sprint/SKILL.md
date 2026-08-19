---
name: sprint
description: Run Agentile sprint lifecycle commands — kickoff a new sprint, write today's daily entry, close a sprint, check status, or regenerate the sprint index. Use when the user says "kickoff", "start sprint", "daily", "close sprint", "sprint status", or references the sprint CLI.
allowed-tools: Bash
---

# Sprint Lifecycle

Runs the Agentile sprint CLI (`scripts/sprint.sh`) on behalf of the user.

## When to Use

- User wants to start a new sprint ("kickoff", "start", "new sprint" with an ID + slug).
- User wants today's daily entry ("daily", "today's entry", "log today").
- User wants to close a sprint ("close", "wrap up", "finish sprint").
- User wants to know what's active ("status", "what's active").
- User wants to regenerate the sprint index.

## When NOT to Use

- The work is audit-driven (turning audit findings into a remediation sprint) → use the `audit-drive` skill, which calls `sprint.sh kickoff` with the right WP structure.
- The user just wants to write a journal entry → use the `journal` skill.
- The user wants the four ratchet checks → use the `ratchet-check` skill.

## Procedure

Parse the user's request to determine the subcommand:

| User says | Run |
|-----------|-----|
| "kickoff" / "start" / "new sprint" with an ID and slug | `scripts/sprint.sh kickoff <ID> <slug>` |
| "daily" / "today's entry" / "log today" | `scripts/sprint.sh daily` |
| "close" / "wrap up" / "finish sprint" | `scripts/sprint.sh close` |
| "status" / "what's active" | `scripts/sprint.sh status` |
| "index" / "regenerate index" | `scripts/sprint.sh index` |

If the request is ambiguous (e.g. just "sprint" with no further context), run `scripts/sprint.sh help` and report the menu of subcommands, then ask which one to execute.

For `kickoff`, the user must supply both an ID (e.g. `S-1`, `RM-A-2`, `FEAT-AUTH`) and a kebab-case slug (e.g. `first-feature`, `consensus-findings`). If either is missing, ask for it before invoking the script.

## After running

Summarize what changed in 2-3 sentences. Do not paste the full script output unless the user asks.

After `kickoff`, also remind the user to:

1. Edit the seeded `SPRINT.md` to fill in goal, WPs, and baselines.
2. Update `.agentile/sprints/CURRENT.md` to point at the new sprint.
3. Commit the kickoff: `chore(<sprint-id>): kickoff`.
