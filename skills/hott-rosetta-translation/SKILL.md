---
name: hott-rosetta-translation
description: Convert HoTT book LaTeX into generated literate Agda Markdown, improve section prose or formalization, curate provenance-backed agda-unimath blocks, and maintain the optional review workflow in the HoTT-Rosetta repository.
---

# HoTT-Rosetta Translation

## Core workflow

1. Read `AGENTS.md`, `docs/implementation-handoff.md`, and
   `docs/conversion-contract.md` completely.
2. Read only the references relevant to the task:
   - section work: `references/section-files.md` and
     `references/latex-to-markdown.md`;
   - chapter aggregation: `references/chapter-files.md`;
   - explicitly requested exercise work: `references/exercise-files.md`.
3. Inspect the LaTeX source, converter code, curated data, and active generated
   output needed for the task.
4. Change the converter or versioned data, regenerate, and validate. Do not
   repair generated documents by hand unless the user explicitly requests it.

The active output directory comes only from `data/project-layout.json`.
Stable names come from `data/rosetta-files.json`. Never consult
`archive/legacy-rosetta/`; it is the historical former `src/` backup.

## Priorities

Prioritize section files: first faithful natural-language mathematics, then
applicable Agda for their definitions, results, constructions, and proofs.
After sections, maintain aggregate chapters and converter correctness.

Exercise prose and structure remain conversion outputs, but finding Agda for
exercise solutions is lower priority. Do not proactively fill missing exercise
Agda blocks unless the user requests it or a section depends on that code.

## Structure and naming

A globally numbered LaTeX `\section` becomes a Rosetta chapter. A LaTeX
`\subsection` becomes a Rosetta section. An `\exitem` becomes an exercise.

- `chapter-N-title-slug.lagda.md`
- `section-N-M-title-slug.lagda.md`
- `exercise-N-K-topic-slug.lagda.md`

Each file begins with a level-one heading and an Agda module whose name exactly
matches the basename. Put Agda blocks near the mathematical item they formalize.
Use stable `rosetta-item` and `rosetta-agda-block` markers through the converter,
not manual output edits.

## Agda sourcing

Before adding a block, search the pinned repository submodule at
`external/agda-unimath` for exact and analogous code.

- Never write a new block by hand or recreate upstream-looking code.
- Copy the closest applicable source. Preserve its names, structure, line
  breaks, and indentation where possible.
- Make only changes required by established local names, universes, imports, or
  dependencies. Mark any changed block as adapted, never exact.
- Record the upstream commit, file, inclusive line range, SHA-256 hash, stored
  code, and a concise adaptation note in `data/agda-blocks*.json`.
- Generated documents may import only repository-local modules, never
  `external/agda-unimath` modules.
- If no applicable source exists, record a missing-code gap and continue with
  other in-scope section work. Do not invent a replacement.

Typecheck every changed section containing Agda with:

```text
python3 rosetta.py typecheck-candidate N M
```

When shared dependencies change, also typecheck the aggregate chapter.

## Review comments

While supplying candidate blocks, add a `codex` comment only when it helps a
reviewer answer a likely mathematical, logical, or source question. For a
useful search gap, name the closest relevant upstream definitions and briefly
say why they are insufficient. Clearly distinguish exact, adapted, and merely
related sources.

Keep comments short and plain. Do not add routine search histories, speculative
lists, code summaries, or comments that only report successful typechecking.
Missing-code items use the same review interface with empty candidate code.

## Validation

Confirm source coverage, numbering, file/module agreement, local imports, and
Agda placement. Before handoff run:

```text
python3 -m unittest discover
python3 rosetta.py check
git diff --check
```

Preserve unrelated and uncommitted work. Do not pull, commit, push, reset, or
clean unless the user explicitly requests it.
