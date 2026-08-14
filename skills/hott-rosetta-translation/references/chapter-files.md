# Chapter files

A chapter file corresponds to a globally numbered LaTeX `\section`. It contains
the introductory prose before the first `\subsection`, followed by generated
imports for every registered section and exercise in numerical order.

Chapter files aggregate generated modules; do not maintain their import lists
by hand. When a section, exercise, filename, or dependency changes, regenerate
the chapter and typecheck the aggregate if Agda is involved.
