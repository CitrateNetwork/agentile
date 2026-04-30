---
description: Sprint lifecycle commands — kickoff, daily, close, status
allowed-tools: Bash
---

You are running the agentile sprint CLI on behalf of the user.

Parse the user's request to determine the subcommand:

| User says | Run |
|-----------|-----|
| "kickoff" / "start" / "new sprint" with an ID and slug | `scripts/sprint.sh kickoff <ID> <slug>` |
| "daily" / "today's entry" / "log today" | `scripts/sprint.sh daily` |
| "close" / "wrap up" / "finish sprint" | `scripts/sprint.sh close` |
| "status" / "what's active" | `scripts/sprint.sh status` |
| "index" / "regenerate index" | `scripts/sprint.sh index` |

If the request is ambiguous (e.g. just "/sprint" with no further
context), run `scripts/sprint.sh help` and report the menu of
subcommands to the user, then ask which one to execute.

For `kickoff`, the user must supply both an ID (e.g. `S-1`,
`RM-A-2`, `FEAT-AUTH`) and a kebab-case slug (e.g.
`first-feature`, `consensus-findings`). If either is missing,
ask for it before invoking the script.

After running any subcommand, summarize what changed in 2-3
sentences. Do not paste the full script output unless the user asks.

After `kickoff`, also remind the user to:

1. Edit the seeded `SPRINT.md` to fill in goal, WPs, and baselines
2. Update `.agentile/sprints/CURRENT.md` to point at the new sprint
3. Commit the kickoff: `chore(<sprint-id>): kickoff`
