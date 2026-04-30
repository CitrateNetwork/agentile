---
created: 2026-04-30T05:00:00Z
branch: main
author: agentile-skeleton
status: active
---

# Sprint Lifecycle

> The shape every sprint follows. Specific workflows (FEATURE,
> AUDIT_DRIVEN, REMEDIATION_TRACK, CEREMONY) layer on top of this
> base lifecycle — they don't replace it.

A sprint moves through four named phases: **kickoff**, **execute**,
**daily**, **close**. Each phase has explicit gates. The gates are
the point: skipping them is what produces orphan work, lost
context, and ratchet regressions.

---

## Phase 1: Kickoff

A new sprint cannot begin until kickoff completes. If any item
below is incomplete, the sprint is in pre-kickoff and code work
does not start.

**Pre-kickoff checks:**

1. The previous sprint is **closed** — `SPRINT.md` final state
   recorded, `RETRO.md` written, directory moved to
   `.agentile/sprints/completed/`.
2. The closing commit hash of the predecessor is known.
3. `.agentile/coverage/BASELINE.md` baseline numbers are current.
4. `sprints/CURRENT.md` no longer points at the previous sprint.

**Kickoff steps:**

1. **Pick the goal.** One sentence. If you can't write it, the
   sprint isn't ready to start. Do not paper over scope ambiguity
   with a list of WPs.
2. **Cut the branch.** Convention: `feat/<sprint-id>-<slug>` or
   `remediation/<track>-<id>`. Branch from the predecessor's
   closing commit, not from a moving ref.
3. **Copy `templates/SPRINT_TEMPLATE.md`** to
   `.agentile/sprints/active/YYYY-MM-DD-sprint-<track>-<id>-<slug>/SPRINT.md`.
4. **Snapshot baselines.** Record start-of-sprint numbers for all
   four ratchets (tests, formal specs, tripwires, frontmatter
   coverage) in the SPRINT.md "Test Baseline" table. Baseline
   commands come from `.agentile/coverage/BASELINE.md`.
5. **Author Work Packages.** One per discrete, independently-
   landable change. Each WP's acceptance criteria MUST name the
   data source (Rule 11). If a WP can't name its data source,
   it isn't ready — refine until it can.
6. **Update `sprints/CURRENT.md`** to point at the new sprint.
7. **Commit the kickoff** as a single commit:
   `chore(<sprint-id>): kickoff — branch + SPRINT.md + baselines`.

**Kickoff gate (cannot proceed until all green):**

- [ ] Goal is one sentence
- [ ] Branch cut from a pinned commit
- [ ] SPRINT.md exists with Rule-12 frontmatter
- [ ] All four ratchet baselines recorded
- [ ] Every WP names a data source
- [ ] CURRENT.md points at the new sprint

---

## Phase 2: Execute

The bulk of the sprint. Work packages flow through the workflow
chosen at kickoff (FEATURE.md is the default; AUDIT_DRIVEN.md and
REMEDIATION_TRACK.md are alternates for those sprint shapes).

**Per-WP sequence (default; FEATURE.md elaborates):**

1. **TLA+** if the WP touches state-machine or consensus behavior.
   Otherwise skip with a note in the WP block.
2. **Failing test or tripwire first** — RED phase. The change
   doesn't begin until the regression has a way to be detected.
3. **Implement** — GREEN phase. Smallest change that turns the
   test green.
4. **Refactor** — only after green. Do not reshape code under a
   red bar.
5. **Adversarial check** — fuzz, mutation, property test, or
   adversarial TLA+ extension as the WP demands.
6. **Update WP block in SPRINT.md** — status, commit hash, tests
   added. The sprint file is the source of truth (Rule 9).
7. **Journal if appropriate.** Most WPs don't need a journal entry.
   Some do — write one at sprint boundaries or when a session
   produced a non-obvious learning.

**Cross-WP rules during execute:**

- Test count never decreases between commits (Rule 3).
- Frontmatter on every new doc (Rule 12).
- WPs that close pin their commit hash in the WP block.
- WPs that block surface to the sprint's "Risks" section with the
  reason and what would unblock them.

---

## Phase 3: Daily

Once per active work day. Append a dated entry to
`.agentile/sprints/active/<sprint-folder>/DAILY.md` using
`templates/DAILY_TEMPLATE.md`.

**Required fields per day:**

- Active WP(s)
- Commits today (hashes + one-line descriptions)
- Tests now / baseline (and the delta)
- Specs now / baseline
- Tripwires now / baseline
- Done today
- Blockers (with named owner if waiting on someone external)
- Tomorrow's plan
- Notes / surprises

**DAILY.md is append-only within the sprint.** Do not overwrite
yesterday's entry. The chronology IS the daily log.

---

## Phase 4: Close

Closure is a discipline. A sprint that runs out of time but is
not formally closed will silently bleed into the next sprint and
poison its planning. Close honestly, even if the goal wasn't met.

**Close checklist:**

1. **Final SPRINT.md update.** Every WP block has a final status
   (COMPLETE / BLOCKED / DEFERRED). Every COMPLETE WP has a
   commit hash. Every BLOCKED / DEFERRED WP has a reason and a
   destination (next sprint, backlog, killed).
2. **Run all four ratchets** and record final numbers.
3. **Author RETRO.md** from `templates/RETRO_TEMPLATE.md`.
   Honest reporting (Rule 0). Reframing failures as successes
   poisons the record.
4. **Carry-forward** — every BLOCKED / DEFERRED WP either becomes
   a backlog entry or is explicitly killed in RETRO.md.
5. **Move the sprint directory** from `sprints/active/` to
   `sprints/completed/`.
6. **Update `sprints/CURRENT.md`** to "no active sprint" (or
   point at the next sprint if pre-kickoff is already done).
7. **Tag the closing commit** if the project uses semver tags
   for sprint closes (optional).
8. **Push.** Closure must land on the remote, not stay local.

**Close gate (cannot mark sprint complete until all green):**

- [ ] Every WP has a final status
- [ ] All four ratchet final numbers recorded
- [ ] RETRO.md exists with Rule-12 frontmatter
- [ ] Test count >= start-of-sprint baseline (Rule 3)
- [ ] No new docs without frontmatter (Rule 12)
- [ ] Sprint directory moved to `completed/`
- [ ] CURRENT.md updated
- [ ] All work pushed to remote

---

## Anti-patterns

These look like progress and aren't.

- **"Done by inspection."** A WP marked COMPLETE without a commit
  hash and tests didn't actually close. Update the WP or revert
  the claim.
- **"We'll catch it next sprint."** Carry-forward is legitimate;
  pretending closure is not. If a WP carries forward, name it
  carry-forward in RETRO.md.
- **Ratchet drift.** "Tests dropped because we deleted obsolete
  ones" is acceptable only if equivalent or better tests landed
  in the same commit. Otherwise it's Rule 3 violation.
- **Goal mutation.** If the goal changed mid-sprint, the sprint
  ends and a new sprint begins with the new goal. Do not edit the
  original goal in retrospect.
