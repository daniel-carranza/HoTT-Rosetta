# HoTT Rosetta agent instructions

Before changing the repository, read docs/implementation-handoff.md,
docs/conversion-contract.md, skills/hott-rosetta-translation/SKILL.md, and
its task-specific references. Consult docs/agda-training-exercises.md and
docs/invisible-math.md for historical dependency and provenance evidence.

## Current policy

- The maintained Rosetta files are authoritative project content. Preserve
  collaborator edits, including uncommitted work. Generation creates only
  missing files; never regenerate existing files or create a parallel preview
  Rosetta. Apply focused changes directly to existing files.
- Keep one shared Rosetta across the development fork, its release branch,
  and the public repository. Inspect and propagate accepted content changes.
  Keep public content to the configured Rosetta directory, latex-book/,
  README.md, and BENCHMARK.md. Everything else is development-only.
- Read the active Rosetta path from data/project-layout.json.
- Never use archive/legacy-rosetta/ in active code, tests, comparisons,
  imports, or Agda include paths.
- Prioritize section prose and Agda for Chapters 3--22 before remaining
  exercise Agda, adding exercise results when needed by sections.
  Chapters 1--2 are optional. Preserve already accepted human contributions.
- Never invent Agda. Copy exact or analogous pinned agda-unimath code,
  make only necessary local adaptations, and record commit/file/line/hash
  provenance. Report actual gaps when no source applies.
- Add needed auxiliary results where they naturally belong, including earlier
  complete files. Maintain narrative and dependency order. Do not create
  artificial holes or separate proposal solutions for these dependencies.
- Use repository-local Agda imports, never external/agda-unimath imports.
- File presence, typechecking, and review state do not establish completeness.
  Review is optional and must not control ordinary checks or generation.
- Typecheck maintained files. A deferred result is not a pass.
- Preserve public history and all human changes. Inspect the worktree, stage
  only intended files, and use focused commits. Never reset, clean, force-push,
  or overwrite collaborator work.
- Respect remote permissions. If one or two simple attempts do not resolve a
  permission issue, stop workarounds, explain the intended action and required
  permission, and ask the user. Fork access does not imply access to publish
  into EgbertRijke/HoTT-Rosetta.

## Validation

```text
python3 -m unittest discover
python3 rosetta.py check
git diff --check
```

Run python3 rosetta.py typecheck-candidate N M for every changed section
containing Agda, typecheck-exercise-candidate N K for changed exercise Agda,
and typecheck-all for affected aggregate chapters. These commands check
maintained files, despite the historical candidate names.

Historical documents and explicitly historical sections are evidence, not
current instructions. The maintenance contract is the current policy authority.
