#!/usr/bin/env python3
"""Tripwire (AG-B-007): a check that examines nothing must be able to fail.

Five enforcement scripts return exit 0 while examining zero artifacts. That
is correct on a fresh skeleton but must be (a) always visible and (b)
convertible into a hard failure once a project is past Sprint 0. These tests
encode the inverse of the finding: with `--require-nonempty` an empty corpus
is a non-zero exit, and without it the no-op is loudly marked `VACUOUS`
rather than printing the same "OK" a real pass prints.

The unit tests exercise the shared `_vacuity` helper directly (deterministic,
independent of the repo's own corpus). The subprocess tests assert the
flag flips the exit code, but only for checks that are currently vacuous —
so they stay correct if this repo later grows real specs/tests/audits.
"""
from __future__ import annotations

import importlib.util
import io
import os
import subprocess
import sys
import unittest
import unittest.mock
from contextlib import redirect_stdout
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CI = REPO / "scripts" / "ci"
CHECKS = [
    "check_test_ratchet.py",
    "check_spec_ratchet.py",
    "check_no_unwraps.py",
    "check_no_mocks.py",
    "check_audit_immutability.py",
]


def _load_vacuity():
    spec = importlib.util.spec_from_file_location("_vacuity", CI / "_vacuity.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


class VacuityHelper(unittest.TestCase):
    def setUp(self) -> None:
        self.v = _load_vacuity()

    def test_flag_enables_strict(self) -> None:
        self.assertTrue(self.v.require_nonempty(["--require-nonempty"]))
        self.assertFalse(self.v.require_nonempty([]))

    def test_env_enables_strict(self) -> None:
        for truthy in ("1", "true", "yes"):
            with unittest.mock.patch.dict(
                os.environ, {"AGENTILE_REQUIRE_NONEMPTY": truthy}
            ):
                self.assertTrue(self.v.require_nonempty([]))
        for falsy in ("", "0", "false", "off"):
            with unittest.mock.patch.dict(
                os.environ, {"AGENTILE_REQUIRE_NONEMPTY": falsy}
            ):
                self.assertFalse(self.v.require_nonempty([]))

    def test_strict_empty_corpus_is_failure(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = self.v.vacuous_exit("tests", strict=True)
        self.assertEqual(code, 1)
        self.assertIn("VACUOUS", buf.getvalue())

    def test_nonstrict_empty_corpus_is_visible_noop(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = self.v.vacuous_exit("tests", strict=False)
        self.assertEqual(code, 0)
        # A no-op must never be indistinguishable from a real pass.
        self.assertIn("VACUOUS", buf.getvalue())


class ChecksFailClosedWhenGraduated(unittest.TestCase):
    def _run(self, script: str, *args: str, strict: bool):
        env = dict(os.environ)
        env.pop("AGENTILE_REQUIRE_NONEMPTY", None)
        if strict:
            env["AGENTILE_REQUIRE_NONEMPTY"] = "1"
        return subprocess.run(
            [sys.executable, str(CI / script), *args],
            capture_output=True, text=True, env=env, timeout=120,
        )

    def test_each_vacuous_check_can_be_made_to_fail(self) -> None:
        for script in CHECKS:
            plain = self._run(script, strict=False)
            self.assertEqual(plain.returncode, 0, plain.stdout + plain.stderr)
            if "VACUOUS" not in plain.stdout:
                # This check has a real corpus in this repo now; the flip is
                # only asserted for genuinely-vacuous checks.
                continue
            strict = self._run(script, strict=True)
            self.assertEqual(
                strict.returncode, 1,
                f"{script} stayed green under --require-nonempty: "
                f"{strict.stdout}{strict.stderr}",
            )


if __name__ == "__main__":
    unittest.main()
