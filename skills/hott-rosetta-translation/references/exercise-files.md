# Exercise files

Exercise files remain part of complete prose conversion, but their Agda
solutions are lower priority than section content.

Translate each full `\exitem` into an exercise file with a descriptive title,
`## Problem statement`, and `## Solution`. The review program links exercises
to their problem statements. Preserve multipart structure clearly.

Do not proactively search for or add missing exercise Agda unless the user
requests it or a section requires the code. When exercise Agda is in scope,
follow the same pinned-source, provenance, no-handwritten-code, local-import,
and review-comment rules as section work. If no applicable upstream source
exists, leave the candidate empty and record a useful gap comment only when it
would help reviewers.

Regenerate through the converter. If Agda changed, run
`python3 rosetta.py typecheck-exercise-candidate N K` and typecheck the
aggregate chapter when appropriate.
