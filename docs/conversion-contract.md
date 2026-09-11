# Rosetta maintenance contract

Current policy, 2026-09-11. This supersedes the former regeneration and
separate proposal-solution policies.

## Content and repositories

The Rosetta files are the project content and authoritative maintained source.
There is generally one shared Rosetta. Propagate accepted Markdown and Agda
changes between daniel-carranza/HoTT-Rosetta main (development), its release
branch, and EgbertRijke/HoTT-Rosetta main. Inspect changes from every collaborator
before reconciliation. Keep content changes in focused commits when practical.

The public tree contains only the configured Rosetta directory, latex-book/,
README.md, and BENCHMARK.md. All other files, including everything under docs/,
are development-only. The development fork retains conversion tools, tests,
provenance, reviews, skills, and mathematical records. Do not merge a full
development tree into a public content branch. See repository-layout.md for
synchronization and permission boundaries.

## Generation and direct edits

data/project-layout.json supplies the active Rosetta path; never hard-code it
in tools. data/rosetta-files.json supplies stable filenames.
Generation creates ONLY missing files. It skips existing files before rendering,
and its writer refuses to replace an existing path. This includes chapter
aggregates, exercises, support modules, and library configuration.
Do not maintain a second preview Rosetta.

Edit existing prose, Agda, imports, and chapter aggregation directly and narrowly.
Preserve surrounding content, including uncommitted collaborator work.
Converter and manifest changes affect future missing files; they are not a
reason to regenerate maintained files. Apply recurring editorial corrections
to existing files with focused, inspected edits.

LaTeX inputs come from latex-book/hott-intro.tex in source order. Numbered
sections become chapters, subsections become section files, and exitem entries
become exercises. Preserve prose, mathematics, item order, proofs, references,
and unsupported-input diagnostics. Use latex-book/hott.tex to interpret macros.
Source comparisons are diagnostic, not an equality requirement for maintained
content. Never use archive/legacy-rosetta/ as active material or an include path.

## Formalization and prerequisites

Prioritize section prose and Agda in Chapters 3--22 before remaining exercise
formalizations. Chapters 1--2 are optional. Preserve accepted human contributions,
including exercise work; prioritization is not grounds to remove them.
File presence, compiler success, and review state do not establish completeness.

For new agent-authored additions, copy exact or analogous pinned agda-unimath
code with only necessary local adaptations. Record source commit, file, inclusive
lines, SHA-256, mathematical destination, and adaptation notes. Never invent
proofs or provenance. Report real source gaps.

Place a needed auxiliary result at its natural mathematical home, including an
earlier complete section when appropriate. Preserve dependency order, module
scope, narrative placement, and local imports. Check the changed files and
downstream consumers. Do not leave an artificial hole because a prerequisite
belongs earlier, and do not start a separate proposal solution branch.
The formerly separate proposal solutions were accepted upstream on September 11.

The public BENCHMARK.md records intentionally unsolved benchmark exercises.
Do not confuse these with the retired auxiliary-hole workflow.
Historical training and invisible-mathematics records retain provenance, not
instructions to remove accepted code.

## Checks and review

Ordinary checks validate maintained content and local imports independently of
review decisions or review metadata. Provenance snapshots are evidence, not a
second authoritative code store. Manually edited or unrecorded code must remain
visible and must not be silently replaced by a snapshot.

The compatibility commands typecheck-candidate and typecheck-exercise-candidate
check the actual existing files. Aggregate checks use maintained chapter imports.
Agda interface caches are ignored development artifacts. No compiler option may
turn an incomplete proof into a claimed pass. Legacy explicit exercise deferrals,
if encountered, mean Agda was not run, never that the file passed.

Review never writes Rosetta files or provenance manifests, including during
draft checking and suggested-diff display. Automatic promotion and old
confirmation submissions are disabled. Apply code changes directly in your
editor and check the maintained file afterward. This avoids replacing a file
while an independent editor is saving; tool-only locks cannot protect that case.
Typecheck evidence tracks file contents and transitive local imports.
An edited curated block is overlaid on the maintained file for a disposable
scratchpad check. A passing draft can show a suggested file/provenance diff,
but neither suggestion is applied by review. Metadata writes are restricted to
the review/comment, draft, and check-result stores. Their read-modify-write
transactions are serialized across threads and processes with stable POSIX
sidecar locks and recoverable backups. Unsupported locking fails closed.
Draft saves, discards, and typecheck completions require the expected draft
revision; stale browser tabs cannot overwrite newer draft work. These locks
coordinate project tools, not independent manual JSON editors or helper scripts.
Shared review metadata has one authoritative home: development main in the fork.
It is shared by commits, ordinary merges, and pushes/pulls, never copied into
content-only release or public trees. Archived snapshots are not synchronized.
The UI reports local/remote sharing status and refuses shared review writes on
other branches or detached tags. Fetching status is explicit and does not merge.
Concurrent review-file changes stop at Git's merge boundary; review-sync merges
comments and keeps each decision bound to its evidence. Conflicting decisions
require an explicit choice, with both sides' comments preserved. A comment alone
never refreshes an earlier decision's fingerprint. See review-guide.md for the
workflow and JSON-free conflict-resolution commands.
Unrecorded direct contributions are visible for review and whole-file checks;
edit them directly until provenance is recorded.

Required validation:

```text
python3 -m unittest discover
python3 rosetta.py check
git diff --check
```

Also run typecheck-candidate N M for each changed Agda section,
typecheck-exercise-candidate N K for changed exercise Agda, and typecheck-all
for affected aggregate chapters. Report failures and any deferred checks honestly.
