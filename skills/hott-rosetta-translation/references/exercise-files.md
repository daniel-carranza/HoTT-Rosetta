# Exercise files

Exercise prose and accepted Agda are maintained content. Preserve the complete
problem, multipart structure, collaborator edits, and solution blocks.

Create an exercise file only if missing. Edit an existing file directly. New
exercise formalization is lower priority than Chapters 3--22 section work unless
requested or required by a section. Do not remove accepted exercise work because
of that priority.

Use pinned-source Agda, recorded provenance, and local imports. Place prerequisite
results where the mathematics belongs; do not create a separate proposal version.
Report actual source gaps without inventing code. BENCHMARK.md lists intentional
public benchmark exercises independently of the retired auxiliary-hole policy.

When exercise Agda changes, run
python3 rosetta.py typecheck-exercise-candidate N K and check affected aggregates.
Propagate accepted content changes between active branches.
