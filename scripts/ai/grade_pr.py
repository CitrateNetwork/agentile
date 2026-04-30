#!/usr/bin/env python3
"""Grade a whole PR's claim surface (title + description + commit
messages in the range) against the claim grader prompt.

Pulls the text via `gh` CLI when available, otherwise reads from
files passed on the command line.

Outputs a JSON object with:
  - per_claim:   list of {kind, identifier, grade}
  - aggregate:   {min_score, mean_score, worst_offenders}
  - summary_md:  a markdown comment ready to post on the PR

Usage:
  scripts/ai/grade_pr.py --pr 123                   # via gh
  scripts/ai/grade_pr.py --base origin/main         # walks commits in the range
  scripts/ai/grade_pr.py --title "..." --body "..." # explicit inputs

Shadow mode behavior: the script always exits 0 unless invoked with
`--strict`, in which case it exits 1 if any single claim's score is
below `--threshold` (default 5). Shadow mode produces a comment;
strict mode produces a comment AND blocks the merge. See
`.github/workflows/claim-grade.yml` for the wiring.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "index"))
from _common import find_project_root  # type: ignore  # noqa: E402

PROJECT_ROOT = find_project_root()
GRADER = PROJECT_ROOT / "scripts" / "ai" / "grade_claim.py"


def grade_one(text: str) -> dict[str, Any]:
    if not text.strip():
        return {
            "score": None, "verdict": "empty",
            "reasons": ["empty claim"], "highlighted_phrases": [],
            "suggested_rewrite": None,
        }
    proc = subprocess.run(
        ["python3", str(GRADER)],
        input=text,
        capture_output=True,
        text=True,
        timeout=60,
    )
    if proc.returncode not in (0, 3):
        return {
            "score": None,
            "verdict": "grader-error",
            "reasons": [f"grade_claim.py exit {proc.returncode}: {proc.stderr.strip()[:200]}"],
            "highlighted_phrases": [],
            "suggested_rewrite": None,
        }
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        return {
            "score": None,
            "verdict": "parse-error",
            "reasons": [f"could not parse grader output: {e}"],
            "highlighted_phrases": [],
            "suggested_rewrite": None,
        }


def gh_pr_view(pr: int) -> dict[str, Any]:
    proc = subprocess.run(
        ["gh", "pr", "view", str(pr), "--json", "title,body,commits"],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        raise SystemExit(f"gh pr view failed: {proc.stderr.strip()}")
    return json.loads(proc.stdout)


def commits_in_range(base: str, head: str = "HEAD") -> list[dict[str, str]]:
    proc = subprocess.run(
        ["git", "-C", str(PROJECT_ROOT),
         "log", "--format=%H%x09%s%x09%b%x1e",
         f"{base}..{head}"],
        capture_output=True, text=True, check=False,
    )
    if proc.returncode != 0:
        return []
    out: list[dict[str, str]] = []
    # Records separated by 0x1e (record separator).
    for record in proc.stdout.split("\x1e"):
        record = record.strip()
        if not record:
            continue
        parts = record.split("\t", 2)
        sha = parts[0] if len(parts) > 0 else ""
        subject = parts[1] if len(parts) > 1 else ""
        body = parts[2] if len(parts) > 2 else ""
        out.append({"sha": sha, "subject": subject, "body": body})
    return out


def claims_from_inputs(args: argparse.Namespace) -> list[dict[str, str]]:
    claims: list[dict[str, str]] = []
    if args.pr:
        data = gh_pr_view(args.pr)
        claims.append({"kind": "pr_title", "identifier": f"PR #{args.pr}", "text": data.get("title", "")})
        if data.get("body"):
            claims.append({"kind": "pr_body", "identifier": f"PR #{args.pr}", "text": data["body"]})
        for c in data.get("commits", []):
            claims.append({
                "kind": "commit",
                "identifier": c.get("oid", "")[:8],
                "text": (c.get("messageHeadline", "") + "\n\n" + c.get("messageBody", "")).strip(),
            })
    if args.title:
        claims.append({"kind": "pr_title", "identifier": "(inline)", "text": args.title})
    if args.body:
        claims.append({"kind": "pr_body", "identifier": "(inline)", "text": args.body})
    if args.base:
        for c in commits_in_range(args.base):
            claims.append({
                "kind": "commit",
                "identifier": c["sha"][:8],
                "text": (c["subject"] + "\n\n" + c["body"]).strip(),
            })
    return claims


def render_markdown(per_claim: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    lines.append("## Claim grader (shadow mode)")
    lines.append("")
    lines.append("Each commit / PR-text element scored against the claim-compression "
                 "rubric. Shadow mode: this comment is informational; merge is not "
                 "blocked.")
    lines.append("")
    lines.append("| Kind | Id | Score | Verdict | Reasons |")
    lines.append("|------|----|-------|---------|---------|")
    for entry in per_claim:
        g = entry["grade"]
        score = "—" if g.get("score") is None else str(g["score"])
        verdict = g.get("verdict", "—")
        reasons = "; ".join(g.get("reasons", []))[:200]
        lines.append(f"| {entry['kind']} | `{entry['identifier']}` | {score} | {verdict} | {reasons} |")
    lines.append("")
    suggestions = [
        e for e in per_claim
        if e["grade"].get("suggested_rewrite") and e["grade"].get("score", 10) < 7
    ]
    if suggestions:
        lines.append("### Suggested rewrites")
        lines.append("")
        for e in suggestions:
            lines.append(f"**{e['kind']} `{e['identifier']}`:**")
            lines.append("")
            lines.append("> " + e["grade"]["suggested_rewrite"].replace("\n", "\n> "))
            lines.append("")
    return "\n".join(lines)


def aggregate(per_claim: list[dict[str, Any]]) -> dict[str, Any]:
    scores = [e["grade"]["score"] for e in per_claim if e["grade"].get("score") is not None]
    if not scores:
        return {"min_score": None, "mean_score": None, "worst_offenders": []}
    sorted_with_idx = sorted(
        ((e["grade"]["score"], i) for i, e in enumerate(per_claim) if e["grade"].get("score") is not None),
        key=lambda t: t[0],
    )
    worst = [
        {
            "kind": per_claim[i]["kind"],
            "identifier": per_claim[i]["identifier"],
            "score": s,
            "verdict": per_claim[i]["grade"].get("verdict"),
        }
        for s, i in sorted_with_idx[:3]
    ]
    return {
        "min_score": min(scores),
        "mean_score": sum(scores) / len(scores),
        "worst_offenders": worst,
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--pr", type=int, help="GitHub PR number (uses `gh`)")
    p.add_argument("--base", help="Git base ref; grades commits in base..HEAD")
    p.add_argument("--title", help="PR title (inline)")
    p.add_argument("--body", help="PR body (inline)")
    p.add_argument("--strict", action="store_true",
                   help="Exit 1 if any score < threshold (default: shadow mode, exit 0)")
    p.add_argument("--threshold", type=int, default=5,
                   help="Score below this triggers strict-mode failure (default: 5)")
    p.add_argument("--out-json", help="Also write the JSON report to this path")
    args = p.parse_args()

    claims = claims_from_inputs(args)
    if not claims:
        print(json.dumps({"per_claim": [], "aggregate": aggregate([]),
                          "summary_md": "_No claim text to grade._"}))
        return 0

    per_claim = []
    for c in claims:
        per_claim.append({
            "kind": c["kind"],
            "identifier": c["identifier"],
            "grade": grade_one(c["text"]),
        })

    report = {
        "per_claim": per_claim,
        "aggregate": aggregate(per_claim),
        "summary_md": render_markdown(per_claim),
    }
    print(json.dumps(report, indent=2))

    if args.out_json:
        Path(args.out_json).write_text(json.dumps(report, indent=2), encoding="utf-8")

    if args.strict:
        bad = [
            e for e in per_claim
            if e["grade"].get("score") is not None and e["grade"]["score"] < args.threshold
        ]
        if bad:
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
