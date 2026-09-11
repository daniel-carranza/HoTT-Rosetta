# Section files

Each maintained section corresponds to one LaTeX subsection. Preserve complete
prose, mathematics, proofs, item numbering, and declaration order. Use the
registry for filenames and the configured Rosetta directory.

Create a section through the converter only when its file is missing. Existing
files receive focused edits directly; converter changes do not authorize their
regeneration. Keep item and block markers where practical to support review,
but manual contributions remain authoritative without manifest entries.

New agent-authored Agda must follow exact or analogous pinned agda-unimath code
with source commit, file, lines, hash, and adaptation notes. Use local imports.
For placement and auxiliaries, read agda-block-placement.md.

Add a needed prerequisite at its natural mathematical home, including an earlier
complete file. Preserve scope and dependency order, avoid cycles, and check every
affected consumer. Do not create artificial holes or proposal-only solutions.

Run python3 rosetta.py typecheck-candidate N M on changed section Agda,
check affected aggregate chapters, and run the validation in AGENTS.md.
These checks use the actual maintained files. Propagate accepted changes to
other active branches as described in docs/repository-layout.md.
