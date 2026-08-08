# Conversion contract

This document records decisions that the converter can enforce. It exists
because the older translation instructions and existing files are not wholly
consistent.

## Sources and order

- Follow active `\input{...}` commands from `book/hott-intro.tex`, through the
  three `chapter-*.tex` files, in source order.
- A globally numbered LaTeX `\section` becomes a Rosetta chapter.
- A LaTeX `\subsection` becomes a Rosetta section.
- An `\exitem` becomes a Rosetta exercise.

## Implementation priority

- Chapters 3--22 are the required compatibility range. Inability to reproduce
  the existing translations from Chapter 3 onward with high accuracy is a
  failure of the converter, even though some editorial differences and manual
  intervention are expected.
- Chapters 3--6 are the trusted examples of complete prose conversion with
  Agda blocks in place, subject to confirmation by the automated audit.
- Chapters 7--17 contain useful examples but are not presumed complete merely
  because files exist. They may be used as partial fixtures only after their
  relevant prose or Agda content has been audited.
- Section files are the main content. Prioritize their faithful prose,
  mathematics, numbering, and Agda before exercise formalizations.
- Exercise prose remains required conversion output. Finding missing exercise
  Agda is lower priority and occurs only when requested or required by a
  section dependency.
- Chapters 1--2 are an optional compatibility goal.
- Accuracy is measured structurally and by reviewed golden comparisons, not by
  requiring byte-for-byte identity with manually edited files. Required
  comparisons include complete prose coverage, item order and numbering,
  headings, mathematics, references, module/file structure, and Agda insertion
  points. Differences must be classified and reported rather than ignored.

## Completion status

- File existence means only that a path exists. It does not mean that the
  source range was fully translated, that required Agda blocks were inserted,
  that provenance was recorded, or that the file typechecks.
- Inventory and status reports track at least these dimensions separately:
  prose coverage, numbered-item coverage, Agda-block coverage, provenance,
  review state, and Agda typechecking.
- Review state is reported but remains optional; it is never part of the basic
  definition of whether conversion ran successfully.
- Status documents generated from filenames alone must use terms such as
  `present` and `missing`, not `complete` and `incomplete`.

## Numbering

- The environments `thm`, `cor`, `lem`, `prp`, `defn`, `quasidefn`, `rmk`,
  `eg`, `axiom`, and `postulate` share one counter.
- That counter resets for each subsection, matching `book/hott-intro.tex`.
- The converter computes these numbers; it does not infer them from labels or
  from existing Markdown.

## Unresolved presentation differences

Generated sections use `# Section N.M Title`; numbered mathematical items use
stable level-two headings and item markers.

Existing translations also contain editorial cross-reference wording and
hand-rendered proof trees. The prototype must report these differences rather
than silently treating Pandoc output as final.

TikZ-CD diagrams are converted from their matrix of entries into ASCII-style
drafts. Each draft includes a short shape description, a visible matrix, and an
explicit list of parsed arrows so diagonal or long-range connections are not
lost. Generated diagrams carry a stable `rosetta-diagram` marker and pending
review state. They are valid conversion output, but remain reviewable and
editable because diagram layout involves aesthetic judgment.

Pandoc discards the contents of the project macro `\define{...}` when it is
unknown. The pre-Pandoc normalization therefore converts this macro to
`\textbf{...}`, which Pandoc renders as Markdown bold text. Every additional
content-bearing macro needs an equally explicit rule and regression test.

Pandoc discards the contents of `prooftree` environments, so preprocessing
parses the bussproofs commands and renders premises, inference rules, labels,
and conclusions as plain-text derivations. Generated trees carry stable
pending-review markers because final spacing remains an aesthetic decision.

Mathematical notation is normalized by an explicit project table rather than
by executing arbitrary TeX definitions. Confirmed commands such as `\N`,
`\succN`, `\addN`, `\jdeq`, and `\to` become the Unicode/plain-text notation
used by existing Rosetta fixtures. Unsupported commands remain visible and
will become diagnostics; they are not silently removed.

Most cross-references are derived automatically from LaTeX labels. A small,
fixture-backed alias table is allowed for editorial cases without a useful
stable number. For example, the local Curry--Howard table reference is rendered
as “the following table” rather than assigning an unverified table number.

## Safety and reproducibility

- Preview commands write only to standard output.
- `data/project-layout.json` defines the single active Rosetta directory.
  Runtime code must never hard-code that directory or silently fall back to a
  second document tree.
- `archive/legacy-rosetta/` (formerly `src/`) is a historical backup. No active script, program, check, test, review
  workflow, or Agda invocation may use it.
- Conversion writes the active generated files. Durable changes belong in the
  converter or its versioned curated data, not in hand-edits to generated files.
- `typecheck-candidate N M` stages the same content with a temporary
  `candidate-...` module name while checking imports and Agda code solely from
  the configured active directory.
- Unknown macros and unsupported environments must produce diagnostics. They
  must never disappear silently.
- Agda blocks and their provenance are curated data, separate from mechanical
  LaTeX conversion.
- Missing exercise Agda does not block section work, ordinary conversion, or
  ordinary checks.

## Review program

- The review program is entirely optional. Conversion and ordinary validation
  must work without opening it and without any review records.
- The review program displays active generated files read-only and records
  review status and comments separately.
- Numbered mathematical items without a curated Agda block appear in the same
  Agda review list with empty code and a clear missing-code label. They accept
  comments but cannot be approved, rejected, or typechecked until code exists.
  Partial exercises and other gaps that cannot be inferred automatically are
  recorded in `data/agda-gaps.json`.
- Generated numbered items carry unobtrusive HTML comments such as
  `<!-- rosetta-item: definition-3.2.1 -->`. Markdown readers ignore these,
  while the converter and review program use them as stable editing anchors.
- Generated diagrams similarly carry stable comments such as
  `<!-- rosetta-diagram: ...; review: pending -->`. The review interface must
  show the source diagram, generated ASCII draft, and shape description, and
  allow collaborators to approve or edit the draft.
- Every save must be atomic and must preserve a recoverable previous version.
- The interface must show the exact pending diff before the user confirms a
  file edit.
- Review metadata records which source-file revision was reviewed. Editing a
  reviewed mathematical item makes its previous verification stale rather
  than silently carrying verification forward.
- Missing, stale, or disputed review records are informational in ordinary
  operation. They become failures only in an explicitly requested strict or
  release check.
- Shared diagram decisions are stored in `data/diagram-reviews.json`. Each
  approval records the digest of the exact TikZ source; a changed source makes
  the approval stale. Comments remain visible regardless of approval state.

## User-facing simplicity

- `convert` performs conversion and does not require review setup.
- `check` reports conversion problems with concise repair instructions. It does
  not fail merely because review is incomplete.
- `review` is a convenient optional interface for collaborators who want it.
- Advanced provenance and release requirements belong behind an explicit
  `check --strict` or equivalent command and must not clutter the ordinary
  workflow.

## Agda provenance

- `data/agda-blocks.json` is versioned, human-readable project data.
- Every block must identify one mathematical item and one destination file.
- Every block must record an upstream commit, file, inclusive line range, and
  SHA-256 digest of that exact range.
- The copied code is stored explicitly so conversion never depends on network
  access or on whichever upstream revision happens to be checked out.
- A block may be described as verbatim only when the complete stored block
  equals its pinned upstream line range byte-for-byte. Locally adapted or
  handwritten legacy blocks require a different, explicit provenance category;
  they must not be entered as exact blocks merely because related upstream code
  exists.
