---
created: 2026-08-11T00:00:00Z
branch: main
author: Devin (GLM-5.2 High) + Thales
status: active
sprint: AGNOSTIC-01-agent-skills-and-agents-md
---

# `.agents/skills/` — Agentile methodology as cross-harness skills

This directory packages the Agentile methodology's workflow commands as
[Agent Skills](https://agentskills.io/specification) in the cross-harness
`.agents/skills/` convention. Any agentskills.io-compliant harness (Devin,
Claude Code, Cursor, Codex, Cognition, Windsurf, Copilot, OpenCode) discovers
these skills automatically — no per-harness configuration required.

## Why this exists

The Agentile methodology ships Claude Code slash commands under
[`.claude/commands/`](../.claude/commands/) (`/sprint`, `/journal`,
`/audit-drive`, etc.). Those are Claude-specific. Non-Claude harnesses cannot
invoke them. The skills in this directory are the **harness-agnostic** equivalent:
the same workflows, expressed as `SKILL.md` files that every compliant harness
can load.

## Skills

| Skill | Replaces (Claude command) | What it does |
|-------|---------------------------|--------------|
| [`audit-drive`](audit-drive/SKILL.md) | `/audit-drive` | Author an audit, open a remediation sprint, or close findings |
| [`sprint`](sprint/SKILL.md) | `/sprint` | Sprint lifecycle: kickoff, daily, close, status, index |
| [`journal`](journal/SKILL.md) | `/journal` | Seed a Rule-12-frontmatter journal entry |
| [`case-study`](case-study/SKILL.md) | `/case-study` | Seed a case study (anchor incident + generalizable lesson + enforcement surface) |
| [`essay`](essay/SKILL.md) | `/essay` | Seed a historical-context essay (not governance) |
| [`claim-grade`](claim-grade/SKILL.md) | `/claim-grade` | Run the AI claim grader on a commit/PR/sprint section |
| [`ratchet-check`](ratchet-check/SKILL.md) | `/ratchet-check` | Run the four ratchet checks (tests, specs, tripwires, frontmatter) |

## Relationship to `.claude/commands/`

The Claude slash commands under `.claude/commands/` are **not modified** by this
addition. They remain the Claude-specific invocation surface. The `.agents/skills/`
files are the harness-agnostic equivalent; the workflow content is adapted from
the commands but lives independently so non-Claude harnesses can use it.

If a future sprint wants to deduplicate, the `.claude/commands/*.md` files could
be regenerated from the `SKILL.md` files (or vice versa). That is out of scope
for the sprint that created this directory.

## Progressive disclosure

Per the agentskills.io spec, only the `name` + `description` frontmatter
(~100 tokens per skill) loads at session start. The full `SKILL.md` body loads
only when the skill is activated. This keeps session-start cost minimal.

## See also

- [`../AGENTILE.md`](../AGENTILE.md) — the methodology overview (in repos bootstrapped from this skeleton).
- [`../.agentile/rules/CORE_RULES.md`](../.agentile/rules/CORE_RULES.md) — the 13 non-negotiable rules.
- [`../.agentile/AGENT_ENTRY.md`](../.agentile/AGENT_ENTRY.md) — the agent entry point.
- [Sprint file](https://github.com/CitrateNetwork/citrate-federation/blob/main/agentile/sprints/active/2026-08-11-agent-agnostic-skills-and-agents-md.md) — AGNOSTIC-01 (the work package that created this directory).
- [agentskills.io specification](https://agentskills.io/specification)
