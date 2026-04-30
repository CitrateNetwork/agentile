#!/usr/bin/env python3
"""Grade a single claim string against the claim-grader prompt.

Reads claim text from stdin, returns a JSON object with score,
verdict, reasons, and (optionally) a suggested rewrite. The prompt
template lives at `scripts/ai/prompts/claim_grader.md` and is
versioned via its frontmatter `prompt_version` field.

Provider selection:
  - Default: Anthropic (env: ANTHROPIC_API_KEY)
  - Fallback: OpenAI (env: OPENAI_API_KEY)
  - If neither is set: returns a NO-OP grade with score=null and
    verdict="grader-unavailable", which CI treats as informational.

Skeleton-friendly: the no-op path means the script works without
configuration (useful in early sprints before the project owner has
chosen an LLM provider).

Usage:
  echo "WP-3 complete" | scripts/ai/grade_claim.py
  scripts/ai/grade_claim.py --file commit_message.txt
  scripts/ai/grade_claim.py --provider openai

Exit codes:
  0 — graded successfully (or no-op grade returned)
  2 — usage error
  3 — provider error (e.g. API timeout) — output JSON includes the error
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "index"))
from _common import find_project_root  # type: ignore  # noqa: E402

PROJECT_ROOT = find_project_root()
PROMPT_PATH = PROJECT_ROOT / "scripts" / "ai" / "prompts" / "claim_grader.md"

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_MODEL = "claude-haiku-4-5-20251001"
OPENAI_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_MODEL = "gpt-4o-mini"


def load_prompt() -> tuple[str, int]:
    """Return (prompt_body, version). The body has the frontmatter and
    HTML comment block stripped — everything that's metadata, not
    grader instructions."""
    text = PROMPT_PATH.read_text(encoding="utf-8")
    version = 1
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            for line in text[3:end].splitlines():
                if line.strip().startswith("prompt_version:"):
                    try:
                        version = int(line.split(":", 1)[1].strip())
                    except ValueError:
                        pass
            text = text[end + 4:]
    # Strip the leading HTML comment block that explains the prompt.
    if text.lstrip().startswith("<!--"):
        close = text.find("-->")
        if close != -1:
            text = text[close + 3:]
    return text.strip(), version


def grade_anthropic(prompt: str, claim: str, api_key: str) -> dict:
    body = {
        "model": ANTHROPIC_MODEL,
        "max_tokens": 1024,
        "messages": [
            {"role": "user", "content": prompt + "\n" + claim}
        ],
    }
    req = urllib.request.Request(
        ANTHROPIC_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    # Response shape: {"content": [{"type":"text","text":"..."}], ...}
    content = data.get("content", [])
    text = next((c.get("text", "") for c in content if c.get("type") == "text"), "")
    return parse_grade_json(text)


def grade_openai(prompt: str, claim: str, api_key: str) -> dict:
    body = {
        "model": OPENAI_MODEL,
        "messages": [
            {"role": "user", "content": prompt + "\n" + claim}
        ],
        "response_format": {"type": "json_object"},
        "max_tokens": 1024,
    }
    req = urllib.request.Request(
        OPENAI_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    text = data["choices"][0]["message"]["content"]
    return parse_grade_json(text)


def parse_grade_json(text: str) -> dict:
    """The grader is instructed to output JSON only. In practice some
    providers wrap it in markdown fences; strip them defensively."""
    text = text.strip()
    if text.startswith("```"):
        # Drop opening fence (with or without language tag) and closing fence.
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)
    return json.loads(text)


def noop_grade(reason: str, version: int) -> dict:
    return {
        "score": None,
        "verdict": "grader-unavailable",
        "reasons": [reason],
        "highlighted_phrases": [],
        "suggested_rewrite": None,
        "prompt_version": version,
    }


def main() -> int:
    args = sys.argv[1:]
    if args and args[0] in ("-h", "--help"):
        print(__doc__)
        return 0

    provider = "auto"
    file_path: str | None = None
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--provider":
            provider = args[i + 1]
            i += 2
            continue
        if a == "--file":
            file_path = args[i + 1]
            i += 2
            continue
        i += 1

    if file_path:
        claim = Path(file_path).read_text(encoding="utf-8")
    else:
        claim = sys.stdin.read()

    prompt, version = load_prompt()

    if not claim.strip():
        result = noop_grade("empty claim text on stdin/file", version)
        print(json.dumps(result, indent=2))
        return 0

    anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    openai_key = os.environ.get("OPENAI_API_KEY", "").strip()

    chosen = provider
    if chosen == "auto":
        if anthropic_key:
            chosen = "anthropic"
        elif openai_key:
            chosen = "openai"
        else:
            chosen = "none"

    if chosen == "none" or (chosen == "anthropic" and not anthropic_key) or (chosen == "openai" and not openai_key):
        result = noop_grade(
            "no API key in env (set ANTHROPIC_API_KEY or OPENAI_API_KEY); "
            "grader returns informational no-op until configured",
            version,
        )
        print(json.dumps(result, indent=2))
        return 0

    try:
        if chosen == "anthropic":
            result = grade_anthropic(prompt, claim, anthropic_key)
        elif chosen == "openai":
            result = grade_openai(prompt, claim, openai_key)
        else:
            print(f"ERROR: unknown provider '{chosen}'", file=sys.stderr)
            return 2
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, json.JSONDecodeError) as e:
        result = noop_grade(f"{chosen} provider error: {e}", version)
        result["verdict"] = "provider-error"
        print(json.dumps(result, indent=2))
        return 3

    # Ensure the prompt version is stamped even if the model omits it.
    result.setdefault("prompt_version", version)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
