# LaTeX to Markdown

Preserve content and expose unsupported input rather than silently dropping it.
Implement recurring rules in the converter with regression tests.

- Remove indexing commands and retain stable label information in item markers.
- Render emphasis and definitions as Markdown emphasis/bold.
- Render inline mathematics as code spans where readable and displays as
  fenced `text` blocks.
- Resolve cross-references from LaTeX labels; use a tested alias only for a
  genuine editorial exception.
- Convert word-like macros, including words joined by `\usc`, to readable
  kebab-case text.
- Preserve prose following code or display blocks as ordinary paragraphs.
- Convert proof trees and TikZ-CD diagrams to faithful reviewable drafts with
  stable markers.
- Keep unknown macros and unsupported environments visible as diagnostics.

Use the explicit project notation tables and macro definitions in
`book/hott.tex` as evidence. Do not execute arbitrary TeX definitions.
