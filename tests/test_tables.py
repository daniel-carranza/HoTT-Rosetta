import unittest

from rosetta.tables import normalize_html_tables


class TableTests(unittest.TestCase):
    def test_html_table_becomes_pipe_table(self):
        source = """<table>
<tr><th>Logic</th><th>Type theory</th></tr>
<tr><td><span class="math inline"><em>P</em> ∨ <em>Q</em></span></td><td>A + B</td></tr>
</table>"""
        self.assertEqual(
            normalize_html_tables(source),
            "| Logic | Type theory |\n"
            "| --- | --- |\n"
            "| `P ∨ Q` | A + B |",
        )

    def test_math_subscript_is_preserved(self):
        source = (
            '<table><tr><td><span class="math inline">'
            '∃<sub><em>x</em></sub>P(x)</span></td></tr></table>'
        )
        self.assertIn("`∃_xP(x)`", normalize_html_tables(source))

    def test_spanning_title_row_is_not_used_as_header(self):
        source = (
            "<table><tr><td>Title</td></tr>"
            "<tr><td>Left</td><td>Right</td></tr>"
            "<tr><td>A</td><td>B</td></tr></table>"
        )
        self.assertEqual(
            normalize_html_tables(source),
            "| Left | Right |\n| --- | --- |\n| A | B |",
        )

    def test_curry_howard_title_gets_semantic_headers(self):
        source = (
            "<table><tr><td>The Curry-Howard interpretation</td></tr>"
            "<tr><td>Propositions</td><td>Types</td></tr></table>"
        )
        self.assertEqual(
            normalize_html_tables(source),
            "| Logic | Type theory |\n"
            "| --- | --- |\n"
            "| Propositions | Types |",
        )


if __name__ == "__main__":
    unittest.main()
