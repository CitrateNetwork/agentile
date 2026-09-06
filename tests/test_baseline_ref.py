#!/usr/bin/env python3
"""Tripwire: ratchets must read the baseline from the merge-base commit."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "ci"))
import _baseline  # noqa: E402


class BaselineRefTests(unittest.TestCase):
    def test_explicit_ref_is_not_read_from_the_pr_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            baseline_path = root / ".agentile" / "coverage" / "baseline.json"
            baseline_path.parent.mkdir(parents=True)
            baseline_path.write_text(
                json.dumps({"tests": {"count": 7, "command": ""}}),
                encoding="utf-8",
            )

            def git(*args: str) -> None:
                subprocess.run(
                    ["git", *args],
                    cwd=root,
                    check=True,
                    capture_output=True,
                    text=True,
                )

            git("init", "-q")
            git("config", "user.email", "agentile-test@example.invalid")
            git("config", "user.name", "Agentile test")
            git("add", ".agentile/coverage/baseline.json")
            git("commit", "-qm", "baseline")
            ref = subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=root, text=True
            ).strip()

            # Simulate a PR that lowers the checked-out baseline after the
            # merge-base commit was created.
            baseline_path.write_text(
                json.dumps({"tests": {"count": 0, "command": ""}}),
                encoding="utf-8",
            )

            with patch.object(_baseline, "PROJECT_ROOT", root), patch.object(
                _baseline, "BASELINE_PATH", baseline_path
            ):
                loaded = _baseline.load_baseline(ref=ref)

            self.assertEqual(loaded["tests"]["count"], 7)


if __name__ == "__main__":
    unittest.main()
