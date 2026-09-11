---
name: hott-rosetta-translation
description: Maintain HoTT Rosetta prose and source-backed Agda, create missing book files, and support content-preserving review.
---

# HoTT Rosetta maintenance

Read AGENTS.md, docs/implementation-handoff.md, and
docs/conversion-contract.md before work. Read only relevant references:

- Section work: references/section-files.md and references/latex-to-markdown.md.
- Placement and auxiliaries: references/agda-block-placement.md.
- Chapter aggregation: references/chapter-files.md.
- Exercises: references/exercise-files.md.
- Branch synchronization: docs/repository-layout.md.
- Review tooling: docs/review-guide.md.

The maintained Rosetta is authoritative. Generation creates only missing files.
Edit existing files directly and narrowly; never regenerate them or create a
parallel preview tree. Obtain the content path from data/project-layout.json.
Use latex-book/ for LaTeX and never use archive/legacy-rosetta/ as active input.

For new formalization, search pinned agda-unimath for exact code, then analogues.
Record source commit, file, inclusive lines, digest, destination, and adaptations.
Never invent Agda. Place prerequisites at their natural mathematical homes,
including earlier sections, and check affected consumers. Do not leave artificial
holes or use the retired proposal branch workflow. Consult the historical
training/invisible-mathematics records only for useful source and placement evidence.

Prioritize section content in Chapters 3--22; exercise code is added when requested
or needed by sections. Preserve all accepted human edits. Completeness requires
mathematical coverage evidence and cannot be inferred from files or review state.

Use repository-local imports. Typecheck actual maintained files with
typecheck-candidate N M, typecheck-exercise-candidate N K when exercise code
changes, and typecheck-all for affected aggregates. Also run the unit suite,
rosetta.py check, and git diff --check. Report deferred checks as not run.

Keep generally one shared Rosetta across active development and public branches.
Public content is only the configured Rosetta directory, latex-book/, README.md,
and BENCHMARK.md. Other files stay in the development fork. Preserve human work
and public Git history. Respect permissions and report publication that needs
access beyond the available token.
