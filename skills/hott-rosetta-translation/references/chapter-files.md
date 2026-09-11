# Chapter files

A chapter file corresponds to a numbered LaTeX section. It contains the chapter
introduction and imports its section and exercise modules in numerical order.

Generation creates only a missing chapter file. Existing chapter introductions
and imports are maintained directly. When filenames or the section/exercise
inventory change, edit the affected imports narrowly and typecheck the aggregate.
Never regenerate the chapter to update its import list, and never infer section
completeness from a successful aggregate check.
