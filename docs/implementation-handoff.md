# Implementation handoff

Updated 2026-08-07.

## Immediate handoff: publish the major rewrite safely

The user has authorized preparation of a large release on the fork
`https://github.com/daniel-carranza/HoTT-Rosetta.git`. GitHub authentication is
working through `GH_TOKEN`; `gh repo view` reports `ADMIN` access. Keep remotes
as follows:

- `origin`: `EgbertRijke/HoTT-Rosetta`, the upstream repository;
- `fork`: `daniel-carranza/HoTT-Rosetta`, the writable release target.

The upstream baseline is commit `43471ee`. Branch `archive/pre-converter` and
annotated tag `pre-converter-2026-08-07` both point to it and are published on
the fork. The fork also has a “Pre-converter archive” GitHub Release from that
tag.
The fork's `main` is currently `be5decb`; its two additional authentication-test
commits add and then remove `test-file.txt`, so its final tree matches the
baseline. Do not rewrite this history without the user asking.

These preservation steps are complete:

1. Push `archive/pre-converter` to `fork`.
2. Push `pre-converter-2026-08-07` to `fork`.
3. Create a GitHub Release on the fork from that tag, titled “Pre-converter
   archive,” explaining that it preserves the repository before the converter,
   review program, generated book, and structural rewrite.
4. Create a feature branch from the current local/fork `main`. Do not commit
   the dirty working tree directly to `main`.

Then perform the release work in this order:

1. Inventory every path as product, source, tool, curated data, documentation,
   cache, or archive.
2. Agree on and implement a clear hierarchy with history-preserving moves.
   The intended starting design is:

   ```text
   book/                    original LaTeX
   rosetta-book/            tracked literate Agda product
   converter/               Python converter and review program
   data/                    manifests, provenance, reviews, configuration
   tests/                   automated tests
   scripts/                 maintenance utilities
   docs/                    onboarding and technical documentation
   skills/                  agent workflow
   external/agda-unimath/   pinned submodule
   archive/legacy-rosetta/  former src/ backup
   ```

   Refine names if the inventory reveals a clearer arrangement. Use `git mv`
   for tracked files where possible. Never lose or overwrite the dirty worktree.
3. Move the active Rosetta product out of ignored `_build/` into a tracked,
   plainly named directory. Update `data/project-layout.json`; all runtime code
   must continue to obtain the location from that setting.
4. Update imports, tests, scripts, documentation, ignore rules, and CI paths.
5. Replace the incomplete README with a newcomer guide. Add setup, cloning with
   submodules, conversion, review-program use, reading the book, contributing,
   troubleshooting, dependency versions, and current limitations. Add a root
   license or an explicit licensing statement after confirming the intended
   license with the user.
6. Add GitHub Actions for unit tests, ordinary checks, diff checks,
   reproducible generation, and Agda typechecking. Do not enable branch
   protection; the user explicitly declined it.
7. Audit the staged content for credentials, machine-specific paths, caches,
   generated Agda interfaces, and accidental omissions.
8. Validate from a fresh clone, including submodule initialization, generation,
   review startup, and aggregate Chapter 1--22 typechecking.
9. Commit the migration in understandable commits, push the feature branch to
   `fork`, and open a pull request against the fork's `main`.

Do not place a token in files, command arguments, remotes, logs, or chat. Use
the existing `GH_TOKEN` environment authentication. If permissions fail once
and one or two ordinary remedies also fail, stop and tell the user exactly
which permission and operation are blocked.

## Current goal and priority

Maintain a reproducible Python converter from `book/*.tex` to self-contained
literate Agda Markdown. Required compatibility is Chapters 3--22; Chapters
1--2 remain useful supporting material.

Prioritize work in this order:

1. Faithful prose, numbering, mathematics, and Markdown in section files.
2. Applicable, provenance-backed Agda blocks for section definitions, results,
   constructions, and proofs.
3. Aggregate chapter files and converter-wide correctness.
4. Exercise prose and structure.
5. Exercise Agda blocks only when explicitly requested or needed by a section.
6. Optional review and diagram presentation improvements.

Do not spend routine work filling missing exercise Agda blocks while section
files still need conversion or formalization.

## Active document model

- `data/project-layout.json` defines the only active Rosetta directory,
  currently `rosetta-book/`.
- `data/rosetta-files.json` records stable chapter, section, exercise, and
  support filenames.
- `archive/legacy-rosetta/` (formerly `src/`) is a historical backup. Active scripts, tests, review tools, Agda
  invocations, and agent workflows must never use or compare against it.
- Generated files are outputs. Put durable corrections in the converter or
  versioned data, then regenerate.
- A future move requires changing the layout setting, regenerating everything,
  and running the complete validation suite.

## Agda rules

- Never invent Agda. Search the pinned `external/agda-unimath` checkout for
  exact and analogous material.
- Copy the closest applicable source and make only necessary compatibility
  changes, such as local universe or established name substitutions.
- Record commit, source file, inclusive lines, source hash, stored code, and
  whether the block is exact or adapted.
- Exact means byte-for-byte identical to the pinned source range.
- Use only repository-local imports in generated documents.
- If no applicable source exists, leave the item without code and record the
  gap. Do not block unrelated section work.
- Typecheck each changed section candidate. Typecheck its aggregate chapter
  when dependencies or shared support code change.

The manifest currently contains 344 blocks: 159 exact, 127 adapted, and 58
historical handwritten/local blocks. Do not add new handwritten blocks.
Chapter 7 and Chapter 8 aggregate candidates typecheck. Exercise 7.9(b) remains
an intentional missing-code item with a review comment describing near matches.

## Review program

The review program is optional and reads active generated documents only. It
shows rendered Markdown, candidate Agda, provenance, typecheck state, and
missing-code items. Review state never controls ordinary conversion or checks.

When supplying candidate Agda, add a concise `codex` comment only if it helps a
reviewer resolve a likely mathematical, logical, or source question. A useful
search-gap comment may name close upstream results and explain why they do not
apply. Do not add routine search logs, summaries of obvious code, or comments
that merely say a block typechecks.

## Implementation map

- `converter/rosetta/render.py`: LaTeX-to-Markdown structure and stable item markers.
- `converter/rosetta/generate.py`: generation and candidate typechecking.
- `converter/rosetta/agda_manifest.py`: curated blocks, provenance, and insertion.
- `converter/rosetta/agda_review.py`, `converter/rosetta/review_web.py`: optional review records
  and read-only browser.
- `converter/rosetta/layout.py`, `converter/rosetta/file_registry.py`: active location and names.
- `data/agda-blocks*.json`: curated Agda and provenance.
- `data/agda-gaps.json`: explicit gaps not inferred automatically.

Everyday commands:

```text
python3 rosetta.py convert
python3 rosetta.py check
python3 rosetta.py review --web
```

## Current verified state

- All 336 registered documents regenerate in the configured directory.
- Aggregate Chapters 1--22 typecheck there with no legacy archive include path.
- The active checks reject runtime references to the backup tree.
- The review UI includes read-only rendered Markdown, links from document items
  to Agda review pages, missing-code pages, comments filtering, and cached
  navigation/actions.

## Required validation

Before handing work back:

```text
python3 -m unittest discover
python3 rosetta.py check
git diff --check
```

Also run `python3 rosetta.py typecheck-candidate N M` for every changed section
containing Agda. Exercise typechecking is required only when exercise Agda is
changed. Preserve the uncommitted worktree; never reset or clean it.
