"""Shared "vacuous green" guard for the CI check scripts (AG-B-004/AG-B-007).

Five of the enforcement scripts pass with exit 0 while examining zero
artifacts — no test command, no `.tla` specs, no Rust, no audit files. On a
freshly-bootstrapped skeleton that is correct (there is genuinely nothing to
check yet); the defect flagged in AG-B-007 is that the empty pass is
*indistinguishable* from a real pass and stays that way silently after the
project has grown past Sprint 0.

This module gives every check two things:

  1. `require_nonempty()` — a project past bootstrap opts into "an empty
     corpus is a failure" by passing `--require-nonempty` (or exporting
     `AGENTILE_REQUIRE_NONEMPTY=1`). Default is off, so the skeleton's own CI
     and a genuine day-zero adopter stay green.

  2. `vacuous_exit()` — prints an explicit `VACUOUS:` marker (never the same
     "OK" a real pass prints) so a no-op is always legible in the log, and
     returns the right exit code for the current mode.
"""
from __future__ import annotations

import os
import sys


def require_nonempty(argv: list[str] | None = None) -> bool:
    """True when this run must treat an empty examined-set as a failure."""
    argv = sys.argv[1:] if argv is None else argv
    if "--require-nonempty" in argv:
        return True
    env = os.environ.get("AGENTILE_REQUIRE_NONEMPTY", "").strip()
    return env not in ("", "0", "false", "False", "no", "off")


def vacuous_exit(kind: str, strict: bool) -> int:
    """Emit the vacuity marker and return the exit code for an empty corpus.

    `strict` is the result of `require_nonempty()`. When strict, an empty
    corpus is a hard failure (exit 1); otherwise it is a visible no-op
    (exit 0) so the skeleton and the bootstrap window still pass.
    """
    if strict:
        print(f"BLOCKER: VACUOUS — examined 0 {kind} while --require-nonempty "
              "is set.")
        print("This gate measured nothing. A project past Sprint 0 must have a")
        print("non-empty corpus for it, or record the empty state as a")
        print("deliberate decision in .agentile/coverage/baseline.json.")
        return 1
    print(f"VACUOUS: examined 0 {kind}; this gate measured nothing (no-op).")
    print("Pass --require-nonempty (or set AGENTILE_REQUIRE_NONEMPTY=1) to make")
    print("an empty corpus a hard failure once the project is past Sprint 0.")
    return 0
