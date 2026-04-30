# `scripts/index/` — Agentile indexer scripts

> Read-only and write-mode tools for the `.agentile/` chronological
> index, frontmatter coverage, and sprint-folder renaming. Ported
> from the source project that incubated this skeleton; sanitized
> for project-agnostic use.

## When to run each script

| Script | Mode | When to run |
|--------|------|-------------|
| `build_agentile_index.py` | read-only | Anytime you want a fresh index. After every sprint close, before publishing the project's MEMORY/INDEX summary, before any rename operation. Always safe to re-run. |
| `backfill_frontmatter.py` | **write** | Once per project, after adopting the skeleton, to give pre-Rule-12 documents a `created` timestamp from git history. Rerunning is idempotent — files that already have frontmatter are skipped. |
| `build_rename_plan.py` | read-only | When journals/essays/case studies in `docs/` have inconsistent filename prefixes and the project owner wants to migrate them to the `YYYY-MM-DDTHHMM_<slug>.md` convention. |
| `apply_rename_plan.py` | **write** | After reviewing `RENAME_PLAN.md` and confirming the migration is correct. Executes `git mv` for each row. |
| `build_sprint_rename_plan.py` | read-only | When sprint folders under `sprints/{active,completed,...}/` lack the `YYYY-MM-DD-` chronological prefix and need migration. Reports the cross-reference blast radius before any change. |
| `apply_sprint_rename_plan.py` | **write** | After reviewing `SPRINT_RENAME_PLAN.md`. Executes `git mv` on the sprint folders. |
| `rewrite_sprint_xrefs.py` | **write** | Run AFTER `apply_sprint_rename_plan.py` to update slug references inside `.md` files. Idempotent: a negative-lookbehind guards against double-rewriting. |

Each script auto-discovers the project root by walking upward
from its own location until it finds a `.agentile/` directory.
That means you can invoke them from anywhere in the project tree:
`./scripts/index/build_agentile_index.py` from the repo root,
`../scripts/index/build_agentile_index.py` from a subdir, both
work.

## Output location

All write-output goes to `.agentile/INDEX/`:

```
.agentile/INDEX/
├── INDEX_CHRONOLOGICAL.md       # everything, sorted by best_timestamp
├── INDEX_BY_CATEGORY.md         # grouped by category
├── INDEX_RAW.tsv                # machine-readable
├── NAMING_INCONSISTENCIES.md    # files missing frontmatter, sprint patterns, etc.
├── RENAME_PLAN.md / .tsv        # produced by build_rename_plan
└── SPRINT_RENAME_PLAN.md / .tsv # produced by build_sprint_rename_plan
```

`INDEX/` is **auto-generated**. It's typically `.gitignore`'d (or
kept under a `.gitkeep` placeholder so the directory survives).
Never edit files in `INDEX/` by hand — they will be overwritten.

## Sequencing the rename operations

The two write-mode rename flows MUST run in order. Skipping a
step or reordering them will produce broken cross-references or
ambiguous slugs.

### Journal/essay/case-study rename

```bash
# 1. Plan
./scripts/index/build_rename_plan.py
# 2. Review .agentile/INDEX/RENAME_PLAN.md — verify timestamps, slugs
# 3. Apply
./scripts/index/apply_rename_plan.py
# 4. Re-index to confirm
./scripts/index/build_agentile_index.py
```

No xref-rewrite step is needed for journals/essays/case-studies
because their filenames typically aren't referenced by slug
elsewhere in `.agentile/`.

### Sprint folder rename

```bash
# 1. Plan — reports xref blast radius
./scripts/index/build_sprint_rename_plan.py
# 2. Review .agentile/INDEX/SPRINT_RENAME_PLAN.md
# 3. Move folders
./scripts/index/apply_sprint_rename_plan.py
# 4. Rewrite slug references in .md files
./scripts/index/rewrite_sprint_xrefs.py
# 5. Re-index
./scripts/index/build_agentile_index.py
# 6. Sanity check — git status should show no orphan references
git grep -l "<old-sprint-slug>"
```

The xref rewrite step is what turns a fast `git mv` into a
correct rename. If you skip it, links throughout `.agentile/`
will point at folders that no longer exist.

## Empty `.agentile/` behavior

All scripts must handle an empty (or near-empty) `.agentile/`
gracefully:

- `build_agentile_index.py` produces empty index files with
  "no documents" placeholder text.
- `backfill_frontmatter.py` reports "Files without frontmatter:
  0" and exits 0.
- The rename planners produce empty plans with "no docs found"
  placeholder text.
- The rename appliers exit 1 with a clear error if the plan TSV
  doesn't exist (the error names the build script to run first).

This matters for the skeleton's adoption flow: a freshly-bootstrapped
project should be able to run the full pipeline against its
near-empty `.agentile/` and get sensible (empty) outputs without
errors.

## Running outside git

The scripts that read git history (`build_agentile_index`,
`backfill_frontmatter`, `build_rename_plan`, `build_sprint_rename_plan`)
gracefully handle the case where:

- Files are untracked (uses filesystem mtime as fallback)
- The directory has no git history at all (returns empty data)

The scripts that *write* via git (`apply_rename_plan`,
`apply_sprint_rename_plan`) require a git repository — they use
`git mv` so history follows the rename.

## See also

- `.agentile/rules/CORE_RULES.md` Rule 12 — the frontmatter
  requirement these scripts enforce
- `.agentile/coverage/GATES.md` ratchet 4 — frontmatter coverage
  is one of the four ratchets
- `scripts/sprint.sh` — agent-agnostic sprint CLI that invokes
  these scripts at the appropriate lifecycle moments
