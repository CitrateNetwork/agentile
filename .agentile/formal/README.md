---
created: 2026-04-30T05:00:00Z
branch: main
author: agentile-skeleton
status: active
---

# Formal Verification

> What `.agentile/formal/` is, when to use it, and how it plugs
> into the rest of the framework.

This directory holds the project's formal-verification scaffold:
TLA+ specs (mirrored from the project's `specs/tla/` source-of-
truth directory), an inventory index, and the workflow that
governs how specs are added, updated, or removed.

Formal verification in Agentile is one of the four ratchets (see
`coverage/GATES.md` ratchet 2). A project that touches consensus,
finality, proposer election, or any other state-machine boundary
either has TLA+ coverage or has explicit, documented justification
for why not. There is no third option.

---

## Directory layout

```
.agentile/formal/
├── README.md                  # this file
├── VERIFICATION_WORKFLOW.md   # the 6-step method
├── SPEC_INDEX.md              # canonical inventory (filled by bootstrap)
└── specs/                     # mirrored from <project>/specs/tla/
    └── <area>/
        ├── <SpecName>.tla
        └── <SpecName>.cfg
```

The `.tla` and `.cfg` files in `.agentile/formal/specs/` are
**mirrors** of the project's source-of-truth specs (typically
under `<project-root>/specs/tla/` for code-adjacent locality).
The mirror exists so that:

- The skeleton's CI tooling can find specs without knowing each
  project's source-of-truth path.
- `SPEC_INDEX.md` gives a stable, queryable inventory.
- A repo with multiple specs directories (mono-repo with several
  workspaces) has a single agentile-side aggregation point.

The mirror is a one-way sync: source-of-truth → `.agentile/formal/
specs/`. Editing the mirror without editing the source is a
correctness bug. Bootstrap and CI tooling enforces sync.

---

## When to add a TLA+ spec

Add a spec when the work touches:

- Consensus (block production, block selection, fork choice)
- Finality (checkpoints, BFT votes, slashing conditions)
- Proposer election (VRF, leader selection, view changes)
- Cross-actor invariants (handshake protocols, state-channel
  exchanges, cross-chain bridges)
- State-machine replication (any place a "happens-before"
  relationship between actors matters for correctness)

Skip a spec when the work is:

- Pure functions (parsers, serializers, format conversions)
- Statistical / numerical estimation (TLA+ is the wrong tool —
  add a property test instead)
- UI rendering / IPC plumbing (model the protocol it speaks to,
  not the UI itself)
- Performance optimization of an already-correct implementation

When in doubt, ask: "Could a race condition between two actors
violate this invariant?" If yes, write a spec. If no, write a
property test.

---

## Adding a spec — quick path

Full procedure in `VERIFICATION_WORKFLOW.md`. Quick version:

1. Copy `templates/TLA_SPEC_TEMPLATE.tla` and `.cfg` to your
   project's `specs/tla/<area>/<SpecName>.{tla,cfg}`.
2. Fill in the state machine, actions, and invariants.
3. Run TLC. Fix the spec until clean.
4. Mirror to `.agentile/formal/specs/<area>/`.
5. Add an entry to `SPEC_INDEX.md`.
6. Add a CI step that re-runs TLC on every PR.

Step 6 is what makes the spec count in ratchet 2. A spec that is
not run in CI does not count toward the ratchet — TLA+ proofs
that don't get re-run rot the same way unrun tests do.

---

## TLA+ Toolbox

Specs are checked with TLC, the explicit-state model checker that
ships with the TLA+ Toolbox. Two practical install paths:

| Approach | When to use |
|----------|-------------|
| **TLA+ Toolbox (Eclipse-based GUI)** | Local exploration; rich counterexample browser |
| **`tla2tools.jar` (CLI)** | CI integration; reproducible runs |

The CLI path is what CI uses. A typical invocation:

```bash
java -cp tla2tools.jar tlc2.TLC \
  -config <SpecName>.cfg \
  -workers <N> \
  <SpecName>.tla
```

Projects often check `tla2tools.jar` into the repo (under
`tools/` or similar) to pin the TLC version. See the project's
`BASELINE.md` for the canonical TLC invocation.

Reference: https://lamport.azurewebsites.net/tla/tla.html

---

## Removing a spec

A spec can be removed only if:

1. The state machine it modeled no longer exists in the codebase
   (i.e. the feature was retired), AND
2. The removal commit lands the deletion of both the source-of-
   truth `.tla`/`.cfg` and the mirror, AND
3. `SPEC_INDEX.md` is updated to remove the entry, AND
4. The removal is documented in the sprint's RETRO.md (or a
   journal entry) explaining what was retired.

A spec cannot be removed because:

- It's slow (run it less often in CI; don't remove it)
- It's complex (refactor it; don't remove it)
- It found a bug that is now fixed (the bug fix is exactly when
  the spec earned its keep — keep it)
- The team forgot how it works (document it; don't remove it)

A removed-and-replaced spec is two coordinated commits: the
replacement lands first and is verified passing, then the original
is removed. Net spec count cannot drop.

---

## See also

- `VERIFICATION_WORKFLOW.md` — the 6-step method
- `SPEC_INDEX.md` — the inventory (or `SPEC_INDEX.md.template`
  before bootstrap fills it in)
- `coverage/GATES.md` — ratchet 2 enforcement
- `templates/TLA_SPEC_TEMPLATE.tla` — starting point for new specs
- `CORE_RULES.md` Rule 10 — formal verification for consensus
