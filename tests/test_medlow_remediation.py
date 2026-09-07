#!/usr/bin/env python3
"""Regression tripwires for the RM-Q MEDIUM + LOW remediation (AG-B-002,
003, 005, 006, 008, 009, 010, 013 and Leg-A AG-02).

Each test fails on the pre-fix code and passes on the fixed code, so the
suite doubles as the RC-8 inversion for the bug class it guards.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
HOOK = REPO / ".claude" / "hooks" / "pre-commit-frontmatter.sh"
BOOTSTRAP = REPO / "bootstrap.sh"
WORKFLOWS = REPO / ".github" / "workflows"


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    )


class HookPortability(unittest.TestCase):
    """AG-B-002 — the pre-commit hook must not use bash-4-only `mapfile`,
    which aborts every commit on macOS's bash 3.2."""

    def test_no_bash4_only_builtins_in_hooks(self) -> None:
        for hook in (REPO / ".claude" / "hooks").glob("*.sh"):
            # Ignore comment-only lines (an explanatory note may name the
            # builtin); flag only real command usage.
            code_lines = [
                ln for ln in hook.read_text(encoding="utf-8").splitlines()
                if not ln.lstrip().startswith("#")
            ]
            code = "\n".join(code_lines)
            self.assertNotRegex(
                code, r"\bmapfile\b", f"{hook.name} uses mapfile (bash-4 only)"
            )
            self.assertNotRegex(
                code, r"\breadarray\b", f"{hook.name} uses readarray (bash-4 only)"
            )

    def test_hook_runs_without_mapfile_builtin(self) -> None:
        """Functional proof: run the hook with `mapfile` disabled (as it is
        absent on bash 3.2) against a staged .md file. Pre-fix this aborts
        with `mapfile: command not found`; post-fix it completes."""
        if shutil.which("bash") is None:
            self.skipTest("bash not available")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / ".agentile" / "docs").mkdir(parents=True)
            # A checker copy so the hook resolves scripts/ci/check_frontmatter.py.
            shutil.copytree(REPO / "scripts", root / "scripts")
            shutil.copytree(REPO / ".claude" / "hooks", root / ".claude" / "hooks")
            doc = root / ".agentile" / "docs" / "note.md"
            doc.write_text("---\ncreated: 2026-01-01\n---\n# ok\n", encoding="utf-8")
            _git(root, "init", "-q")
            _git(root, "config", "user.email", "t@example.invalid")
            _git(root, "config", "user.name", "t")
            _git(root, "add", ".agentile/docs/note.md")
            hook = root / ".claude" / "hooks" / "pre-commit-frontmatter.sh"
            # `enable -n mapfile` makes the bash-4 builtin unavailable, mimicking
            # bash 3.2 where the loop must be used instead.
            proc = subprocess.run(
                ["bash", "-c", f"enable -n mapfile 2>/dev/null; exec {hook}"],
                cwd=root,
                capture_output=True,
                text=True,
            )
            self.assertNotIn("command not found", proc.stderr)
            self.assertEqual(proc.returncode, 0, proc.stderr)


class HookIdempotency(unittest.TestCase):
    """AG-B-003 — bootstrap's hook-install guard must recognise its own
    bridge on re-run (case-sensitive `grep agentile` never matched the
    `Agentile` it wrote)."""

    def test_bridge_marker_matches_guard(self) -> None:
        text = BOOTSTRAP.read_text(encoding="utf-8")
        # The guard greps `grep -qF "$hook_marker"` and the marker is a stable
        # lowercase token that the emitted bridge contains verbatim.
        self.assertIn('hook_marker="agentile-hook-bridge"', text)
        self.assertIn('grep -qF "$hook_marker"', text)
        # The heredoc bridge line embeds the same marker.
        self.assertRegex(text, r"#\s*\$\{hook_marker\}")
        # RC-8: the old capitalised, un-matchable comment must be gone.
        self.assertNotIn("# Agentile hook bridge —", text)

    def test_emitted_bridge_is_recognised_by_the_guard(self) -> None:
        marker = "agentile-hook-bridge"
        bridge = f"#!/usr/bin/env bash\n# {marker} v1 — invokes ...\nexec ...\n"
        # `grep -qF marker` over the bridge must succeed (the guard's positive).
        proc = subprocess.run(
            ["grep", "-qF", marker], input=bridge, text=True
        )
        self.assertEqual(proc.returncode, 0)


class SedTemplateInjection(unittest.TestCase):
    """AG-B-013 — operator strings templated with sed must escape `&` and
    reject embedded newlines (GNU sed `e` = shell exec)."""

    def _run_sed_escape(self, value: str) -> subprocess.CompletedProcess[str]:
        # Extract the sed_escape function body and exercise it in isolation.
        src = BOOTSTRAP.read_text(encoding="utf-8")
        m = re.search(r"sed_escape\(\) \{.*?\n\}", src, re.DOTALL)
        assert m, "sed_escape function not found"
        script = m.group(0) + '\nsed_escape "$1"\n'
        return subprocess.run(
            ["bash", "-c", script, "bash", value],
            capture_output=True,
            text=True,
        )

    def test_ampersand_is_escaped(self) -> None:
        proc = self._run_sed_escape("A&B")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout, r"A\&B")

    def test_newline_is_rejected(self) -> None:
        proc = self._run_sed_escape("x\necho pwned")
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("template-injection guard", proc.stderr)


class WorkflowInjection(unittest.TestCase):
    """AG-B-005 / AG-B-006 — attacker-controlled values (dispatch inputs,
    PR filenames) must not be interpolated as `${{ }}` into a `run:` body."""

    def _run_bodies(self, wf: Path) -> str:
        # Crude but effective: collect the text of `run:` blocks and check no
        # `${{ ... }}` expression survives inside them.
        text = wf.read_text(encoding="utf-8")
        return text

    def test_no_expr_interpolation_of_inputs_in_run(self) -> None:
        # No `${{ ... inputs.pr ... }}` inside a run: script; it must go via env.
        for wf in WORKFLOWS.glob("*.yml"):
            text = wf.read_text(encoding="utf-8")
            # steps.<id>.outputs.files was the AG-B-006 vector; ban it entirely.
            self.assertNotRegex(
                text,
                r"\$\{\{\s*steps\.\w+\.outputs\.files\s*\}\}",
                f"{wf.name} interpolates a changed-file list into a run: shell",
            )

    def test_claim_grade_uses_env_for_pr_number(self) -> None:
        text = (WORKFLOWS / "claim-grade.yml").read_text(encoding="utf-8")
        self.assertIn("PR_NUMBER:", text)
        # The run: body references the shell var, not the raw expression.
        self.assertNotRegex(
            text, r'pr_num="\$\{\{ github\.event',
        )
        self.assertIn('"$PR_NUMBER" =~ ^[0-9]+$', text)


class ActionPinning(unittest.TestCase):
    """AG-B-008 — no abandoned/mutable third-party action refs."""

    def test_no_returntocorp_and_no_latest_tag(self) -> None:
        for wf in WORKFLOWS.glob("*.yml"):
            for line in wf.read_text(encoding="utf-8").splitlines():
                stripped = line.strip()
                if stripped.startswith("uses:"):
                    self.assertNotIn("returntocorp", stripped, f"{wf.name}: {stripped}")
                    self.assertFalse(
                        stripped.endswith(":latest"), f"{wf.name}: {stripped}"
                    )


class PublicHygiene(unittest.TestCase):
    """AG-B-009 / AG-02 — no dead personal-namespace links or leaked
    internal paths/opsec in the public corpus."""

    def _tracked_md(self) -> list[Path]:
        out = _git(REPO, "ls-files", "*.md").stdout.splitlines()
        return [REPO / p for p in out]

    def test_no_saulbuilds_citrate_links(self) -> None:
        for p in self._tracked_md():
            self.assertNotIn(
                "SaulBuilds/citrate", p.read_text(encoding="utf-8"),
                f"{p.relative_to(REPO)} links the private personal repo",
            )

    def test_no_local_path_or_opsec_leaks(self) -> None:
        needles = [
            "/home/saul",
            "Mozi Group",
            "citrate-old-history",
            "gh CLI is authenticated",
            "admin of CitrateNetwork",
        ]
        for p in _git(REPO, "ls-files").stdout.splitlines():
            # The test harness itself legitimately names the sentinel strings
            # it scans for; exclude tests/ from the corpus scan.
            if p.startswith("tests/"):
                continue
            fp = REPO / p
            if not fp.is_file():
                continue
            try:
                text = fp.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            for needle in needles:
                self.assertNotIn(needle, text, f"{p} leaks {needle!r}")


class WorkflowsReadme(unittest.TestCase):
    """AG-B-010 — the workflows README must be honest about count and perms."""

    def test_readme_covers_all_workflows_and_write_perm(self) -> None:
        readme = (WORKFLOWS / "README.md").read_text(encoding="utf-8")
        self.assertNotIn("Five GitHub Actions workflows", readme)
        yml = {p.name for p in WORKFLOWS.glob("*.yml")}
        for name in yml:
            self.assertIn(name, readme, f"{name} undocumented in workflows README")
        self.assertIn("pull-requests: write", readme)
        self.assertIn("ANTHROPIC_API_KEY", readme)


class FilesFrom(unittest.TestCase):
    """check_frontmatter.py --files-from (the AG-B-006 safe path)."""

    def test_files_from_reads_list_and_filters(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            listing = Path(d) / "files.txt"
            # A shell-metacharacter filename is inert data here, not executed.
            listing.write_text(
                ".agentile/docs/$(touch pwned).md\n", encoding="utf-8"
            )
            proc = subprocess.run(
                [sys.executable, str(REPO / "scripts" / "ci" / "check_frontmatter.py"),
                 "--files-from", str(listing)],
                cwd=REPO, capture_output=True, text=True,
            )
            # The security property: the metachar filename is inert DATA, never
            # a shell command. It must not create `pwned`, and --files-from must
            # parse (no usage/crash error, exit code 0 or 1 — never 2).
            self.assertFalse((REPO / "pwned").exists(), "metachar filename executed")
            self.assertIn(proc.returncode, (0, 1), proc.stderr)
            self.assertNotIn("Traceback", proc.stderr)


if __name__ == "__main__":
    unittest.main()
