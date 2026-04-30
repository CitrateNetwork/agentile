\* ---
\* created: 2026-04-30T05:00:00Z
\* branch: main
\* author: agentile-skeleton
\* status: template
\* ---
\*
\* TLA+ SPEC TEMPLATE — Agentile.
\*
\* Copy this file to:
\*   <project-root>/specs/tla/<area>/<SpecName>.tla
\* And copy the companion .cfg to:
\*   <project-root>/specs/tla/<area>/<SpecName>.cfg
\*
\* The TLA+ frontmatter convention is comment lines starting with `\* `.
\* TLC ignores them; humans and the frontmatter checker can read them.
\*
\* See .agentile/formal/VERIFICATION_WORKFLOW.md for the 6-step method
\* this template plugs into:
\*   1. identify the state machine
\*   2. write the spec (this file)
\*   3. run TLC
\*   4. fix the spec until it's clean
\*   5. write the implementation
\*   6. add a regression test that re-runs TLC in CI
\*
\* RULE OF THUMB:
\*   - Anything that touches consensus, finality, proposer election,
\*     or cross-actor invariants gets a TLA+ spec.
\*   - Pure-function math (e.g. fitting a power law) does NOT need TLA+.
\*     Specs verify state-machine properties, not statistical claims.
\*
\* Rename `Template` to your spec name everywhere below.

------------------------------ MODULE Template ------------------------------
EXTENDS Naturals, FiniteSets, Sequences, TLC

(***********************************************************************
* WHAT THIS SPEC MODELS
* ---------------------
* <One paragraph. The state machine you are formalizing. Name the
* contract / module / pipeline whose behavior this mirrors. Anyone
* reading the spec should know in 30 seconds what real-world thing
* it claims to be a model of.>
*
* WHAT TLA+ CHECKS
* ----------------
* <Bullet the invariants this spec verifies. Distinguish what TLA+
* CAN check (state-machine properties) from what it CANNOT (e.g.
* statistical, performance, or empirical claims). If your hypothesis
* has both, name the protocol-level slice that lives here.>
*
* OPERATOR-VS-VARIABLE PRINCIPLE
* ------------------------------
* <Which things are CONSTANTS (configuration, fixed at start), which
* are VARIABLES (mutable state)? Pinning this consciously prevents
* state-space explosion.>
***********************************************************************)

CONSTANTS
    \* Inputs the model takes from the .cfg file. Each is one of:
    \*   - a finite set (e.g. validator IDs)
    \*   - a function from one set to another
    \*   - a numeric bound (state-space cap)
    Actor,                \* SET — agents that take actions
    MaxSteps              \* Nat — state-space bound

ASSUME Actor # {}
ASSUME MaxSteps \in Nat /\ MaxSteps >= 1

VARIABLES
    \* The mutable state. Keep this small — the state space is
    \* exponential in the number of variables for many specs.
    state,                \* current protocol state (define as a record below)
    stepCount             \* Nat — number of Next-steps taken

vars == << state, stepCount >>

(***********************************************************************
* INITIAL STATE
***********************************************************************)
Init ==
    /\ state = [ \* fill in the record schema you want
                 phase |-> "init"
               ]
    /\ stepCount = 0

(***********************************************************************
* ACTIONS
* Each action is a parameterized predicate over (vars, vars').
* Convention: actions name the actor in the parameter list.
***********************************************************************)

\* Replace with the real action names for your protocol.
ActionA(a) ==
    /\ a \in Actor
    /\ stepCount < MaxSteps
    /\ state' = [ state EXCEPT !.phase = "after-A" ]
    /\ stepCount' = stepCount + 1

ActionB(a) ==
    /\ a \in Actor
    /\ stepCount < MaxSteps
    /\ state.phase = "after-A"
    /\ state' = [ state EXCEPT !.phase = "after-B" ]
    /\ stepCount' = stepCount + 1

Next ==
    \/ \E a \in Actor: ActionA(a)
    \/ \E a \in Actor: ActionB(a)

Spec == Init /\ [][Next]_vars

(***********************************************************************
* INVARIANTS — what we claim is always true.
* Each invariant gets named in the .cfg under INVARIANTS.
***********************************************************************)

\* Type invariant — every variable stays in its declared domain.
TypeOK ==
    /\ state.phase \in {"init", "after-A", "after-B"}
    /\ stepCount \in 0..MaxSteps

\* A protocol-level safety property. Replace with whatever the spec
\* exists to verify.
SafetyExample ==
    state.phase = "after-B" => stepCount >= 2

THEOREM Safety ==
    Spec => [](
        TypeOK
        /\ SafetyExample
    )

==========================================================================
