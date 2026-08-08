# HoTT Rosetta agent instructions

Before changing this repository, read these current instructions completely:

1. `docs/implementation-handoff.md`
2. `docs/conversion-contract.md`
3. `skills/hott-rosetta-translation/SKILL.md`
4. Every reference selected by that skill for the task

Read `docs/initial-prompt.txt` and `docs/audit-baseline.md` only when historical
project intent or baseline evidence is relevant; they are not current workflow
instructions.

## Non-negotiable requirements

- Required conversion compatibility is Chapters 3--22. Chapters 1--2 are
  optional.
- Prioritize faithful section prose and section Agda. Exercise prose remains in
  scope, but finding missing exercise Agda is lower priority and should happen
  only when requested or required by section work.
- High-fidelity reproduction from Chapter 3 onward is a success criterion.
- File existence never means complete conversion.
- The review UI is entirely optional. Conversion and ordinary checks must not
  depend on review state.
- The active Rosetta directory is configured in `data/project-layout.json`.
  Every script and program must use that setting rather than hard-coding a
  location.
- `archive/legacy-rosetta/` (formerly `src/`) is a historical backup only. Active scripts, programs, tests, and
  agent workflows must not read from it, write to it, compare against it, or
  put it on Agda's include path.
- Agda claimed as copied from agda-unimath must be verbatim and have exact
  commit/file/line/hash provenance. Do not describe adapted legacy blocks as
  exact.
- Never write a new Agda block by hand. Search agda-unimath for exact and
  analogous material, copy the closest applicable code, and make only locally
  necessary adaptations. If no applicable source exists, stop and report the
  gap.
- Generated Rosetta files must remain self-contained: use repository-local
  imports, never imports from `external/agda-unimath`.

## Working-tree warning

The current converter implementation is uncommitted. Preserve all untracked
files under `converter/`, `rosetta-book/`, `tests/`, `data/`, and `docs/`, plus `rosetta.py`
and `AGENTS.md`. Preserve the `.gitignore` modification.
Do not reset, clean, or replace this work.

## Required validation

Run before handing work back:

```text
python3 -m unittest discover
python3 rosetta.py check
git diff --check
```

Use `python3 rosetta.py typecheck-candidate N M` whenever a changed section
contains Agda. Typecheck exercises only when their Agda changes.
