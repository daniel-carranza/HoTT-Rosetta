# Repository layout and shared content

The primary content is the maintained Rosetta, whose directory is configured in
data/project-layout.json (currently rosetta-book/). Both Markdown and Agda are
edited directly.

daniel-carranza/HoTT-Rosetta main is the development home. Its release branch
prepares the public tree for EgbertRijke/HoTT-Rosetta main.

The public tree contains exactly these content roots:

- The configured Rosetta directory, including its local support modules and
  HoTT-Rosetta.agda-lib.
- latex-book/, the LaTeX sources and accompanying book assets.
- README.md.
- BENCHMARK.md.

Everything else is development-only, including docs/, converter/, data/, tests/,
skills/, scripts/, AGENTS.md, CI configuration, pinned external sources, and
editor/cache configuration. No docs/ file is exported to the public repository.

## Development setup

```sh
git clone --recurse-submodules https://github.com/daniel-carranza/HoTT-Rosetta.git
cd HoTT-Rosetta
```

An existing clone can initialize provenance with
git submodule update --init external/agda-unimath.
Install Python 3.9 or newer, Pandoc, and Agda. CI uses Python 3.10 and Agda 2.8.0.
The source library is pinned for provenance; the Rosetta never imports it.

## Synchronizing accepted content

There is generally one shared Rosetta, not separate development mathematics or
proposal solutions. Fetch the active branches and inspect both histories and
worktrees before editing. Preserve accepted changes from either repository;
reconcile concurrent edits individually rather than replacing an entire tree.

Keep content changes separate from backend changes in focused commits when
practical. Carry those content commits to the other active branches, resolving
conflicts with the current maintained files. Never merge the whole development
tree into release or the public repository. Retired proposal and archival
branches are historical evidence, not additional maintained versions.

After committing, compare the shared content:

```text
python3 rosetta.py content-diff fork/release --public
python3 rosetta.py content-diff origin/main --public
```

These commands compare committed Git content, not working-tree changes. They
report missing or differing content and, with --public, development files that
must be excluded. The old book/ path is normalized for migration comparisons.
They make no changes and do not regenerate files. An exact result checks bytes
and file modes; it does not establish mathematical completeness.

The initial transition preserves release's README and latex-book/ rename and
incorporates the newer public content. The reconciled release also records the
accepted public ancestry without importing development files. Inspect the final
public tree and verify that the latest public main is an ancestor of release
before publishing. Use ordinary fast-forward pushes; never rewrite public
history or overwrite new remote work. See implementation-handoff.md for the
validated commits and publication status.

The token in the current environment permits publishing to the fork only.
Prepare and validate the fork release first. A maintainer with access to the
original repository must publish that content there; do not repeatedly attempt
unauthorized pushes or treat an unpublished public update as completed.

Build caches, disposable draft checks, and recoverable review backups are
development artifacts, not a second maintained Rosetta.

## Shared reviews and historical snapshots

Review decisions and comments are tracked development data, authoritative on
the fork's main branch. Developers exchange them through ordinary Git commits
and merges. They are intentionally absent from the content-only release and
original repository; content-diff therefore does not compare them. Use
review-sync status and the workflow in review-guide.md for review synchronization.

The proposal tip 2cc8b8ddbc6f93b7a1aa9ed1513e72d581b082cc is preserved by the
annotated tag archive/proposal-agda-exercise-solutions-2026-09-11. Do not update
that historical tag to match current content or reviews. It is a recovery point,
not an active branch. Check implementation-handoff.md for protection/deletion
status before taking further retirement actions.
