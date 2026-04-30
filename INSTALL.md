# Installing Agentile

> Detailed setup walkthrough. For the 30-second version, see
> [`README.md`](README.md). This file is for project owners who
> want to understand each step.

---

## Prerequisites

| Tool | Required | Version | Used for |
|------|----------|---------|----------|
| `git` | Yes | any recent | Source control, hooks |
| `bash` | Yes | 4+ | bootstrap.sh, sprint.sh, hooks |
| `python3` | Yes | 3.10+ | All `scripts/ci/`, `scripts/index/`, `scripts/ai/` |
| `semgrep` | Optional | latest | AST-grade tripwires (`scripts/semgrep/`) |
| `actionlint` | Optional | latest | `lint-workflows.yml` runs it via Docker |
| `gh` (GitHub CLI) | Optional | latest | `claim-grade.yml` posts PR comments via it |
| TLA+ Toolbox / `tla2tools.jar` | Optional | latest | If you intend to write TLA+ specs |

`semgrep`, `actionlint`, `gh`, and TLA+ are only required at the
moment you want the corresponding feature. The skeleton bootstraps
without them and CI gracefully no-ops the workflows that reference
them when the tools aren't present.

---

## Step 1: Get the skeleton into your repo

You have three options.

### Option A: Clone fresh

If you're starting a brand-new project:

```bash
git clone https://github.com/CitrateNetwork/agentile.git my-project
cd my-project
git remote remove origin   # disconnect from the skeleton remote
# Now point at your own repo:
git remote add origin git@github.com:<org>/<repo>.git
```

### Option B: Copy into an existing repo

If you already have a project and want to adopt Agentile:

```bash
cd my-existing-project
# Copy the skeleton's framework directories in:
cp -R /path/to/agentile-clone/.agentile .
cp -R /path/to/agentile-clone/.claude   .
cp -R /path/to/agentile-clone/scripts   .
cp -R /path/to/agentile-clone/.github   .   # only the workflow files; merge if you have existing workflows
cp /path/to/agentile-clone/bootstrap.sh .
cp /path/to/agentile-clone/.gitignore   ./.gitignore.agentile   # don't clobber yours; merge by hand
```

### Option C: git subtree

For projects that want to track upstream skeleton updates:

```bash
git subtree add --prefix=skeleton https://github.com/CitrateNetwork/agentile.git main --squash
# Then symlink or copy the parts you want into place.
```

Most projects pick Option A or B; subtree is for the unusual case
where you want to merge upstream skeleton changes mechanically.

---

## Step 2: Run `bootstrap.sh`

```bash
./bootstrap.sh
```

The script asks for:

- **Project name** — auto-defaults to the parent directory name
- **One-line description** — used in CONFIG.md and CLAUDE.md
- **Primary languages** — comma-separated (e.g. "rust,typescript")
- **License** — defaults to "MIT"

It then:

1. Fills in `.agentile/CONFIG.md` from the template
2. Fills in `.agentile/PRODUCT_SPEC.md` from the template
3. Generates `CLAUDE.md` from `.claude/CLAUDE.md.template`
4. Seeds `.claude/settings.json` from its template (gitignored)
5. Renames the Sprint 0 placeholder folder to today's date and
   flips its frontmatter `status: template` → `status: active`
6. Seeds `.agentile/coverage/BASELINE.md` and
   `.agentile/coverage/baseline.json`
7. Asks whether to install git hooks (default: yes)
8. Runs the indexer to populate `.agentile/INDEX/`
9. Stages and (with confirmation) commits everything as
   `chore: bootstrap from agentile-skeleton vX.Y.Z`

For non-interactive automation:

```bash
./bootstrap.sh --non-interactive \
  --project-name="my-project" \
  --description="One-line description" \
  --languages="rust" \
  --license="MIT"
```

Re-running `bootstrap.sh` is safe: it detects already-bootstrapped
state and asks per-section whether to update.

---

## Step 3: Read the framework entry point

Before you write code, read these files in order. They take ~15
minutes total.

1. **`.agentile/AGENT_ENTRY.md`** — the universal entry point. Tells
   you which other files to read and in what order.
2. **`.agentile/CONFIG.md`** — the canonical-constants doc you just
   filled in. Make sure every value is correct.
3. **`.agentile/rules/CORE_RULES.md`** — the 13 rules that bind all
   work. Pay particular attention to Rule 12 (frontmatter) and
   Rule 11 (data source tracing).
4. **`.agentile/coverage/GATES.md`** — the four ratchets your CI
   will enforce.

Optional but useful:

- `.agentile/docs/methodology/METHODOLOGY.md` — the synthesis
- `.agentile/docs/methodology/04_FAILURE_MODES.md` — the catalog of
  named anti-patterns
- `.agentile/workflows/SPRINT_LIFECYCLE.md` — the shape every
  sprint follows

---

## Step 4: Set the canonical test count command

The skeleton can't know what your project's test runner is.
Edit `.agentile/coverage/baseline.json` to set the `tests.command`
field. The command must:

- Print a single integer to stdout (the script extracts the last
  numeric token)
- Exit 0 on success
- Be deterministic (same input = same output count)

Common shapes:

```json
{
  "tests": {
    "count": 0,
    "command": "cargo test --workspace 2>&1 | grep 'test result:' | awk '{s+=$4}END{print s}'"
  }
}
```

```json
{
  "tests": {
    "count": 0,
    "command": "npx vitest run --reporter=json 2>/dev/null | jq '.numTotalTests'"
  }
}
```

Then run:

```bash
./scripts/ci/check_test_ratchet.py
```

The first run reports a count and notes the baseline is 0; subsequent
runs enforce it.

---

## Step 5: Walk through Sprint 0

Open the seeded sprint:

```
.agentile/sprints/active/<today>-sprint-0-bootstrap/SPRINT.md
```

It has six WPs (0.1 through 0.6) covering:

- WP-0.1 — read foundation tier
- WP-0.2 — fill in CONFIG.md
- WP-0.3 — fill in PRODUCT_SPEC.md
- WP-0.4 — capture BASELINE.md numbers
- WP-0.5 — write the project's first journal
- WP-0.6 — kick off Sprint 1

Each WP is mechanical and short. The total time to close Sprint 0
is typically one work session.

---

## Step 6: Kick off Sprint 1

Sprint 1's goal is project-specific — the first real piece of work
your project wants to deliver. Possible shapes:

- A feature sprint (`workflows/FEATURE.md`)
- A retrofit sprint if you adopted Agentile mid-project
- A remediation sprint if you have a day-zero audit

To start:

```bash
./scripts/sprint.sh kickoff S-1 <slug>
# e.g.: ./scripts/sprint.sh kickoff S-1 first-feature
```

That seeds `.agentile/sprints/active/<today>-sprint-s-1-<slug>/SPRINT.md`.
Edit it to fill in the goal and Work Packages.

---

## Step 7 (optional): Configure CI

The workflows under `.github/workflows/` work out of the box for
GitHub Actions. To enable them:

1. Push to a GitHub repo (the workflows fire on `pull_request` and
   `push: branches: [main]`).
2. Set repo secrets if you want the AI grader to run:
   - `ANTHROPIC_API_KEY` (preferred), or
   - `OPENAI_API_KEY` (fallback)
3. Adjust `ratchet-check.yml`'s `test-ratchet` job to install your
   project's toolchain (Rust, Node, Python, etc.) before the script
   runs. Look for the comment block in the job — there's a TODO
   pointing where toolchain setup goes.

For non-GitHub CI, port the workflow YAML to your provider. The
underlying scripts in `scripts/ci/` are the contract; the workflow
files are just glue.

---

## Step 8 (optional): Configure Claude Code

If you use Claude Code:

1. The bootstrap already seeded `.claude/settings.json` from the
   template. Edit if you want different permissions or hook events.
2. The slash commands under `.claude/commands/` are picked up
   automatically when you open the project in Claude Code.
3. The subagents under `.claude/agents/` are similarly auto-loaded.

Slash commands available:

- `/sprint kickoff <id> <slug>` — start a new sprint
- `/sprint daily` — append today's daily log entry
- `/sprint close` — seed RETRO.md
- `/sprint status` — show active sprints
- `/journal` — start a journal entry with proper frontmatter
- `/essay` — start an essay
- `/case-study` — start a case study
- `/claim-grade` — grade a piece of text for honesty
- `/ratchet-check` — run all four ratchets locally
- `/audit-drive` — walk through the audit-driven workflow

Subagents (invoked via the `Agent` tool):

- `methodology-guide` — answers "how does the framework want me to
  do X?"
- `tripwire-author` — drafts a new Semgrep rule or check_*.py from
  an audit finding
- `claim-grader` — interprets the AI grader's output
- `journal-coach` — coaches journal entries at sprint boundaries

---

## Step 9 (optional): Hard-mode opt-in for soft gates

The AI grader, data-source check, and benchmark regression check
all default to **shadow mode** — they post comments but never block
merges. After your project's calibration period (typically 2 weeks
of watching the comments to confirm the false-positive rate is
acceptable), opt into hard mode:

1. **Claim grader** — edit
   `.github/workflows/claim-grade.yml`:
   - Remove `continue-on-error: true`
   - Add `--strict --threshold 5` to the `grade_pr.py` invocation

2. **Data-source check** — edit
   `.github/workflows/data-source-check.yml`:
   - Remove `continue-on-error: true`
   - Add `--strict` to the `data_source_check.py` invocation

3. **Benchmark regression** — edit
   `.github/workflows/benchmark-nightly.yml`:
   - Add `--strict` to the `check_regression.py` invocation
   - Add the regression-check job as a required check in branch
     protection rules

Make these one at a time and watch the merge friction. If false
positives spike, revert and tune the prompt or adjust the
thresholds.

---

## Troubleshooting

### "no .agentile/ directory found above this script"

Every script in `scripts/` walks upward from its own location to
find a `.agentile/` directory. If you see this error, you're
either:

- Running the script from outside the project tree (cd into the
  project first), or
- Inside an agentile-equipped project that's missing `.agentile/`
  (re-run `bootstrap.sh`)

### "test command timed out after 600s"

`check_test_ratchet.py` enforces a 10-minute timeout. If your test
suite legitimately takes longer:

- Split into a fast-suite + a slow-suite and run only the
  fast-suite in the ratchet
- Increase the timeout in the script (look for `timeout=600` and
  change it)
- Or run the ratchet only nightly rather than per-PR

### Frontmatter checker fails on legitimate non-doc files

The `check_frontmatter.py` script only walks `.agentile/`. If you
add a non-doc file under `.agentile/` (e.g. a binary blob), exclude
it via the script's `INDEX/` skip pattern or via `.gitignore`.

### Ratchets all return "WARN: no … set in baseline.json"

You haven't set the canonical commands yet. Edit
`.agentile/coverage/baseline.json` and re-run.

---

## Where to ask for help

- **Methodology questions** — the `methodology-guide` subagent in
  Claude Code, or read the relevant file in `.agentile/`.
- **Bug reports / feature requests** — open an issue against the
  skeleton repo at https://github.com/CitrateNetwork/agentile.
- **Improvements / forks** — PRs welcome. If you fork for a
  different domain (data engineering, ML training, infra), link
  back so others can find your variant.

---

## Updating the skeleton in your project

When the upstream skeleton releases a new version:

1. Fetch from the skeleton repo (manual diff approach):
   ```bash
   git remote add agentile https://github.com/CitrateNetwork/agentile.git
   git fetch agentile main
   git diff agentile/main -- .agentile/rules/ scripts/ .claude/
   ```
   Cherry-pick the changes you want.

2. Or if you used `git subtree` (Option C above):
   ```bash
   git subtree pull --prefix=skeleton agentile main --squash
   ```

The skeleton's CHANGELOG.md notes which files moved or changed
shape between versions; check it before updating.
