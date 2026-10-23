"""Workflow hygiene pins that the medlow suite does not cover.

* Every ``${{ }}`` expression inside a ``run:`` body must be one of a small
  allowlist of values that cannot carry shell syntax (event name, SHAs, PR
  number). Inputs, titles, bodies, branch names and step outputs must reach
  the shell through ``env:``.
* Every ``uses:`` line, including the common ``- uses:`` list form, is pinned
  to a full commit SHA (actions) or a fixed version (docker images), and
  never to an abandoned or ``latest`` ref.
* Every claim-grade step that consumes ``$PR_NUMBER`` validates it first.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

WORKFLOWS = Path(__file__).resolve().parents[1] / ".github" / "workflows"

SAFE_EXPR = re.compile(
    r"^\s*(github\.event_name"
    r"|github\.event\.pull_request\.(base|head)\.sha"
    r"|github\.event\.before|github\.sha"
    r"|github\.event\.pull_request\.number)\s*$"
)


def run_bodies(text: str):
    """Yield (lineno, line) for every line inside a run: body."""
    lines = text.splitlines()
    in_run, run_indent = False, 0
    for n, line in enumerate(lines, 1):
        if line.lstrip().startswith("#"):
            continue
        ind = len(line) - len(line.lstrip())
        if in_run:
            if line.strip() and ind <= run_indent:
                in_run = False
            else:
                yield n, line
                continue
        m = re.match(r"^(\s*)(- )?run:\s*(.*)$", line)
        if m:
            rest = m.group(3)
            if rest.startswith(("|", ">")):
                in_run, run_indent = True, len(m.group(1)) + (2 if m.group(2) else 0)
            else:
                yield n, rest


class RunBodyExpressions(unittest.TestCase):
    def test_only_allowlisted_expressions_reach_a_shell(self) -> None:
        bad = []
        for wf in sorted(WORKFLOWS.glob("*.yml")):
            for n, line in run_bodies(wf.read_text(encoding="utf-8")):
                for expr in re.findall(r"\$\{\{(.*?)\}\}", line):
                    if not SAFE_EXPR.match(expr):
                        bad.append(f"{wf.name}:{n}: ${{{{{expr}}}}}")
        self.assertEqual(bad, [], "route these through env: instead")

    def test_detector_sees_a_dispatch_input_in_run(self) -> None:
        sample = (
            "    steps:\n"
            "      - name: x\n"
            "        run: |\n"
            "          ./grade.py --pr \"${{ github.event.inputs.pr }}\"\n"
        )
        exprs = [e for _, l in run_bodies(sample) for e in re.findall(r"\$\{\{(.*?)\}\}", l)]
        self.assertEqual(len(exprs), 1)
        self.assertFalse(SAFE_EXPR.match(exprs[0]))


class ActionRefs(unittest.TestCase):
    def test_every_uses_line_is_pinned(self) -> None:
        bad = []
        for wf in sorted(WORKFLOWS.glob("*.yml")):
            for n, line in enumerate(wf.read_text(encoding="utf-8").splitlines(), 1):
                m = re.match(r"^\s*(?:- )?uses:\s*([^\s#]+)", line)
                if not m:
                    continue
                ref = m.group(1)
                if ref.startswith("./"):
                    continue
                if "returntocorp" in ref or ref.endswith((":latest", "@latest")):
                    bad.append(f"{wf.name}:{n}: {ref}")
                elif ref.startswith("docker://"):
                    if not re.search(r"(:\d+\.\d+\.\d+|@sha256:[0-9a-f]{64})$", ref):
                        bad.append(f"{wf.name}:{n}: {ref}")
                elif not re.search(r"@[0-9a-f]{40}$", ref):
                    bad.append(f"{wf.name}:{n}: {ref}")
        self.assertEqual(bad, [])


class ClaimGradePrNumber(unittest.TestCase):
    def test_every_step_using_pr_number_validates_it_first(self) -> None:
        text = (WORKFLOWS / "claim-grade.yml").read_text(encoding="utf-8")
        guard = '[[ ! "$PR_NUMBER" =~ ^[0-9]+$ ]]'
        users = 0
        for step in re.split(r"\n\s*- name:", text):
            if "run:" not in step:
                continue
            body = step.split("run:", 1)[1]
            if "$PR_NUMBER" not in body:
                continue
            users += 1
            # The first shell use of $PR_NUMBER must be the numeric check.
            self.assertEqual(
                body.find("$PR_NUMBER"), body.find(guard) + len('[[ ! "'),
                f"step '{step.splitlines()[0].strip()}' uses $PR_NUMBER before validating it",
            )
        self.assertGreater(users, 0)


if __name__ == "__main__":
    unittest.main()
