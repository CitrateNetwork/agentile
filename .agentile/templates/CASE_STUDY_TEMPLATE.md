---
created: 2026-04-30T05:00:00Z
branch: main
author: agentile-skeleton
status: template
---

<!--
CASE STUDY TEMPLATE — Agentile.

Filename convention (Rule 12 + chronology):
  .agentile/docs/case_studies/YYYY-MM-DDTHHMM_<slug>.md

A case study is anchored to a specific incident and turns it into
a durable lesson. It is the bridge between an essay (idea-first)
and an audit finding (defect-first): the case study takes a thing
that actually happened, names what it teaches, and proposes the
enforcement surface that would catch its recurrence.

Write a case study when:
  - A bug, near-miss, or surprising outcome reveals a pattern that
    could recur in different forms
  - A particularly costly or instructive remediation is closing
  - Something novel emerged — a concept or implementation worth
    reusing — and the "incident" is the discovery itself
  - An external incident (Knight Capital, log4shell, etc.) maps
    cleanly onto a class of risk this project carries

Don't write a case study for routine bugs. The point is the
generalizable lesson, not the diary entry.
-->

# Case study: <one-line incident name>

> One-sentence dek that names the lesson. The reader should know
> within five seconds what they're getting.

## TL;DR

<3–5 sentences. The whole case study, compressed. Anyone who
reads only this paragraph should know: what happened, what it
cost, what to do about it.>

## Anchor incident

<What actually happened. Dates, commits, components, observed
behavior. Cite file:line where possible. If the anchor is
external (a known industry incident), cite the original source.>

| Field | Value |
|-------|-------|
| **When** | YYYY-MM-DD |
| **Where** | <component / repo / external system> |
| **Cost** | <wall-clock time, dollars, lost trust, etc — be specific> |
| **Detected by** | <who or what surfaced it> |

## What we expected vs. what we got

| Expectation | Reality |
|-------------|---------|
| <what the design implied> | <what the code did> |

## Why it happened

<2–4 paragraphs. The mechanism. Don't stop at proximate cause —
keep asking "and why did THAT happen?" until the answer is a
property of how the team / tool / process works.>

## The repair — and the anti-repair

<Document the correct fix AND the tempting-but-wrong fix, and why
the wrong one is wrong. The anti-repair is usually the one that
makes the symptom disappear without re-earning the truth — e.g.
updating a pinned expected value to whatever the code now
produces, turning a referee into a mirror.>

| | What | Why |
|---|------|-----|
| **Repair** | <the fix that landed> | <why it re-earns trust> |
| **Anti-repair** | <the tempting fix, rejected> | <why it is wrong> |

## Indicators (early warning signs)

<Things that, in retrospect, should have flagged the issue
before it landed. These become the basis for tripwires.>

- <indicator 1>
- <indicator 2>

## Enforcement surface

<The durable change that prevents recurrence. Specific. A case
study without an enforcement surface is just a war story.>

| Mechanism | What it catches | Where it lives |
|-----------|-----------------|----------------|
| <e.g. CI tripwire, TLA+ invariant, lint rule, review gate> | <the class of bug> | <file or workflow> |

## What this does NOT cover

<Adjacent failure modes the proposed enforcement does NOT prevent.
Naming these honestly is the difference between a useful case
study and a smug one.>

## References

- Sprint(s): <SPRINT.md path>
- Audit finding(s): <audit ID>
- Related case study / essay: <path>
- External source(s): <link>
