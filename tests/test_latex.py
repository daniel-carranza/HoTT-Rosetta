import unittest
from pathlib import Path

from rosetta.latex import (
    book_section_paths,
    command_arguments,
    inventory,
    numbered_items,
    uncommented_lines,
)


ROOT = Path(__file__).resolve().parent.parent


class LatexStructureTests(unittest.TestCase):
    def test_escaped_percent_is_not_a_comment(self):
        lines = list(uncommented_lines(r"kept \% sign % removed"))
        self.assertEqual(lines, [(1, r"kept \% sign ")])

    def test_book_input_order(self):
        paths = book_section_paths(ROOT / "book")
        self.assertEqual(len(paths), 22)
        self.assertEqual(paths[0].name, "dtt.tex")
        self.assertEqual(paths[8].name, "equivalences.tex")
        self.assertEqual(paths[-1].name, "circle-universal-cover.tex")

    def test_shared_numbering_counter(self):
        source = r"""
\begin{defn}\label{def:a} A. \end{defn}
\begin{rmk} B. \end{rmk}
\begin{prp}\label{prop:c} C. \end{prp}
"""
        items = numbered_items(source, 3, 2)
        self.assertEqual(
            [(item.kind, item.number) for item in items],
            [
                ("Definition", "3.2.1"),
                ("Remark", "3.2.2"),
                ("Proposition", "3.2.3"),
            ],
        )
        self.assertEqual(items[0].label, "def:a")

    def test_balanced_heading_argument(self):
        source = r"\subsection{Laws on \texorpdfstring{$\N$}{ℕ}} Body"
        self.assertEqual(
            command_arguments(source, "subsection")[0][0],
            r"Laws on \texorpdfstring{$\N$}{ℕ}",
        )

    def test_nested_book_title_is_not_truncated(self):
        sections = inventory(ROOT / "book")
        self.assertEqual(
            sections[4].subsections[5],
            r"The laws of addition on \texorpdfstring{$\N$}{ℕ}",
        )


if __name__ == "__main__":
    unittest.main()
