---
created: 2026-04-30T05:00:00Z
branch: main
author: agentile-skeleton
status: active
---

# Ceremony Workflow

> Production rerolls, network restarts, contract redeployments,
> and any other multi-step operation where order matters and
> mid-flight aborts have downstream consequences. A ceremony is
> not a feature, not a remediation, not a sprint — it's an
> orchestrated sequence with strict pre/post-conditions.

A ceremony differs from a sprint:

| Sprint | Ceremony |
|--------|----------|
| Delivers code over days/weeks | Executes a sequence over hours |
| Iterative; mid-flight changes are expected | Linear; mid-flight changes are mostly bugs |
| RETRO.md captures lessons | Ceremony record captures step-by-step state |
| Branch can be discarded if it goes wrong | Some steps are externally observable; "discard" is partial |

Use this workflow when the operation manipulates **persistent,
externally-visible state** (chain state, deployed contracts,
staging databases, public endpoints) and the cost of a botched
mid-flight abort is non-trivial.

---

## When to invoke a ceremony

Common triggers:

- Rerolling a network (devnet/testnet/mainnet) from genesis
- Deploying a contract suite to a fresh environment
- A coordinated upgrade that requires nodes to halt, swap state,
  and resume in lockstep
- A scheduled key rotation across multiple components
- A migration where the new state cannot be derived from the old
  state in real time

If any of those apply, write a CEREMONY plan before touching the
keys.

---

## Phases

A ceremony has five phases. Each is gated by a checklist; do not
proceed past a gate until every box is checked.

```
PRE-FLIGHT  →  HALT  →  WIPE/MIGRATE  →  REBUILD  →  DEPLOY  →  POST-FLIGHT
```

Below, "the operator" is the human or agent driving the ceremony.
The operator can be one person; for high-stakes ceremonies (e.g.
mainnet) two operators are encouraged with explicit roles
(driver / verifier).

---

### Phase 1: Pre-flight

The ceremony does not begin until pre-flight completes. If a box
fails, abort — pre-flight failure is cheap; mid-ceremony failure
is not.

**Pre-flight checklist:**

- [ ] **Plan exists.** Written CEREMONY.md (use this workflow
      doc as the model) with named steps, named operator(s),
      named time window, named rollback procedure.
- [ ] **Backups verified.** Every piece of state being modified
      has a fresh backup that has been *restored to a sandbox*
      at least once. A backup that has never been restored is
      not a backup.
- [ ] **Dependencies pinned.** Contract versions, image tags,
      binary hashes, key fingerprints — every artifact in the
      ceremony has a pinned identifier.
- [ ] **Dry run passed.** The ceremony has been executed end-to-
      end against a non-production environment. If the production
      ceremony is the first time anything has been tried in this
      order, abort.
- [ ] **Rollback procedure rehearsed.** The "things went wrong"
      path has been executed in dry run. You know how to undo
      every reversible step.
- [ ] **Communication plan.** Who gets notified at start, at
      each phase boundary, at finish, on abort.
- [ ] **Time window confirmed.** Ceremony fits in the window
      with margin. If the window is "as fast as possible," that
      is not a window — define one.
- [ ] **Pre-flight metrics snapshotted.** Block height, account
      counts, contract addresses, balances, whatever you'll
      verify against in post-flight. Without a snapshot, "did
      it work?" has no answer.

---

### Phase 2: Halt

Bring the system to a controlled stop. Halt is the boundary
between "rollback is a button" and "rollback is a procedure."

**Halt steps:**

1. Stop block production (or write traffic, or whatever the
   ceremony's "no new state" line is).
2. Wait for in-flight operations to drain or hit timeout.
3. Verify every component is at the expected halt state. Pin
   the snapshot — last block hash, last tx, last write LSN.
4. Mark the halt time in the ceremony record.

**Halt checklist:**

- [ ] No new writes accepted
- [ ] All in-flight operations resolved or timed out
- [ ] Halt-state snapshot recorded
- [ ] All operators acknowledge halt

---

### Phase 3: Wipe / migrate

Modify persistent state per the ceremony plan. This is the most
dangerous phase — most ceremonies that go wrong, go wrong here.

**Wipe/migrate principles:**

- One change at a time. If the plan has three migrations, run
  them in order with verification between each.
- Verify after every step. "Did the migration succeed?" gets a
  yes/no answer with evidence (rowcounts, hashes, byte-for-byte
  diff against expected).
- If a step fails, halt the ceremony. Do not "skip and come
  back" — pre-flight should have made this impossible, but if
  it happens, abort to rollback.

**Wipe/migrate checklist:**

- [ ] Each step verified before the next begins
- [ ] No skipped steps
- [ ] Migrated-state hash matches the expected hash from dry run
- [ ] Rollback still possible (last-checkpoint snapshot retained)

---

### Phase 4: Rebuild

Re-stand the system on the new state. Build artifacts, start
services, accept reads (but not writes yet — see post-flight).

**Rebuild principles:**

- Bring up in dependency order. A service that depends on the
  chain comes up after the chain. A service that depends on
  contracts comes up after contracts deploy.
- Health-check each component before bringing up the next.
- Do NOT accept production traffic yet. Read-only or restricted
  access is fine.

**Rebuild checklist:**

- [ ] Every component up and health-checking green
- [ ] Inter-component connectivity verified (e.g. node sees peers,
      indexer sees node, GUI sees indexer)
- [ ] Contract deployment in dependency order, each verified
      before the next deploys
- [ ] Read-path smoke test passes

---

### Phase 5: Deploy / Open

Open writes. Move from controlled-availability to production-
availability. Sometimes this is a single config flip; sometimes
it's a graduated rollout (5% → 25% → 100%).

**Deploy checklist:**

- [ ] Write-path smoke test passes (one transaction end-to-end)
- [ ] Monitoring shows expected baseline traffic
- [ ] Communication plan executed (announcement sent)
- [ ] Operator confirms "no aborts in progress"

---

### Phase 6: Post-flight

The ceremony is not done at "writes opened." It's done when
post-flight passes.

**Post-flight checklist:**

- [ ] All pre-flight metrics re-checked against post-flight
      values, with deltas explained
- [ ] No new error rates or latency regressions vs. pre-halt
      baseline
- [ ] Backups taken of new state (forms the rollback point for
      the *next* ceremony)
- [ ] Ceremony record committed to repo:
      `.agentile/ceremonies/YYYY-MM-DD-<slug>/CEREMONY.md` with
      timestamps, step outcomes, surprises
- [ ] Pre-existing rollback artifacts (migration backups, halt
      snapshots) retained for a defined period, then deleted on
      a documented schedule
- [ ] Lessons captured: anything surprising goes in a journal or
      case study under `.agentile/docs/`

---

## Rollback

Every ceremony needs a defined rollback. Two flavors:

**Reversible step rollback** — the ceremony is between halt and
deploy. Restore the halt-state snapshot, abort the ceremony, run
post-flight against the restored state. Acceptable.

**Irreversible step rollback** — the ceremony has progressed past
a one-way door (e.g. mainnet contracts are deployed and external
parties have referenced them). True rollback is impossible;
"forward fix" is the only option. Pre-flight should have flagged
this; if you reached this state without flagging, the post-flight
record names the gap and a new audit is opened.

---

## Ceremony record

Every ceremony produces a record:
`.agentile/ceremonies/YYYY-MM-DD-<slug>/CEREMONY.md`

Mandatory contents:

- Frontmatter (Rule 12): created, branch, author, status: active
- Plan as committed pre-flight (do NOT edit retroactively)
- Per-step actual time, command, output excerpt or hash, status
- Surprises encountered (in-line, alongside the step they
  occurred at, not relegated to a footer)
- Final disposition: SUCCESS / PARTIAL / ABORTED-ROLLED-BACK /
  ABORTED-FORWARD-FIX
- Pointers to relevant journals, case studies, audits

Ceremonies are forgettable when they go right and unforgettable
when they go wrong. The record exists so the next ceremony can
trust the outcome of this one and learn from any wrong turns.

---

## See also

- `SPRINT_LIFECYCLE.md` — what a ceremony is *not*
- `templates/AUDIT_TEMPLATE.md` — when a ceremony surfaces a class
  of risk that warrants an audit
- `CORE_RULES.md` Rule 0 — the imperative against context drift
  applies doubly during ceremonies; checklists exist because
  memory fails
