"""bootstrap.sh must commit only the files it generates.

Runs the real ``bootstrap.sh --non-interactive`` inside a throwaway copy of
the skeleton (its own git repo, HOME and git config isolated) with unrelated
files planted in the adopter's tree, then inspects what was committed and
what is staged. Nothing outside the temp dir is touched.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _git(cwd: Path, *args: str, env: dict) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, env=env, check=True, capture_output=True, text=True
    ).stdout


class BootstrapStagesOnlyGeneratedFiles(unittest.TestCase):
    PLANTED = ("local-notes.txt", "private/creds.json")

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="ag-boot-"))
        self.proj = self.tmp / "proj"
        home = self.tmp / "home"
        home.mkdir()
        self.env = {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "HOME": str(home),
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_AUTHOR_NAME": "t",
            "GIT_AUTHOR_EMAIL": "t@example.invalid",
            "GIT_COMMITTER_NAME": "t",
            "GIT_COMMITTER_EMAIL": "t@example.invalid",
            "LC_ALL": "C",
        }
        tracked = subprocess.run(
            ["git", "ls-files", "-z"], cwd=REPO, check=True, capture_output=True
        ).stdout.decode().split("\0")
        for rel in filter(None, tracked):
            src = REPO / rel
            if not src.is_file():
                continue
            dst = self.proj / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        _git(self.proj, "init", "-q", "-b", "main", env=self.env)
        _git(self.proj, "add", "-A", env=self.env)
        _git(self.proj, "commit", "-q", "-m", "skeleton", env=self.env)
        for rel in self.PLANTED:
            p = self.proj / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("not part of the bootstrap\n")

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def _run_bootstrap(self) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["bash", str(self.proj / "bootstrap.sh"), "--non-interactive",
             "--project-name=demo", "--no-hooks"],
            cwd=self.proj, env=self.env, capture_output=True, text=True,
        )

    def test_planted_files_are_neither_committed_nor_staged(self) -> None:
        r = self._run_bootstrap()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        committed = set(_git(self.proj, "ls-tree", "-r", "--name-only", "HEAD",
                             env=self.env).split())
        staged = set(_git(self.proj, "diff", "--cached", "--name-only",
                          env=self.env).split())
        for rel in self.PLANTED:
            self.assertFalse(rel in committed, f"{rel} was committed by bootstrap")
            self.assertFalse(rel in staged, f"{rel} was staged by bootstrap")
            self.assertTrue((self.proj / rel).is_file(), f"{rel} was removed")

    def test_generated_files_are_still_committed(self) -> None:
        r = self._run_bootstrap()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        changed = set(_git(self.proj, "show", "--name-only", "--format=", "HEAD",
                           env=self.env).split())
        for rel in (".agentile/CONFIG.md", "CLAUDE.md",
                    ".agentile/coverage/baseline.json"):
            self.assertIn(rel, changed)
        self.assertTrue(any(p.startswith(".agentile/sprints/active/") and
                            "YYYY-XX-XX" not in p for p in changed), changed)


if __name__ == "__main__":
    unittest.main()
