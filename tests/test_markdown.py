import unittest

from rosetta.markdown import clean_markdown


class MarkdownTests(unittest.TestCase):
    def test_prose_sentences_start_on_new_lines(self):
        self.assertEqual(
            clean_markdown("First sentence. Second sentence.\n"),
            "First sentence.\nSecond sentence.\n",
        )

    def test_preserved_proof_tree_is_a_visible_display_fallback(self):
        source = "    \\AxiomC{$P$}\n    \\UnaryInfC{$Q$}\n"
        self.assertEqual(
            clean_markdown(source),
            "```text\n\\AxiomC{$P$}\n\\UnaryInfC{$Q$}\n```\n",
        )

    def test_code_fence_is_not_split(self):
        source = "```text\nFirst. Second.\n```\n"
        self.assertEqual(clean_markdown(source), source)

    def test_sentence_indented_by_pandoc_list_display_becomes_prose(self):
        source = (
            "1. An item.\n\n"
            "```text\nzero-Fin_0 := star.\n```\n\n"
            "    Since this is ordinary explanatory prose, it should not be code.\n"
        )
        self.assertIn(
            "\nSince this is ordinary explanatory prose, it should not be code.\n",
            clean_markdown(source),
        )

        self.assertIn(
            "\nIn order to construct the map, first choose a value\n",
            clean_markdown(
                "1. An item.\n\n"
                "    In order to construct the map, first choose a value\n"
            ),
        )

    def test_indented_formula_is_preserved(self):
        self.assertEqual(
            clean_markdown("Before.\n\n    H(m, q) if x = q\n"),
            "Before.\n\n    H(m, q) if x = q\n",
        )

    def test_construction_argument_becomes_heading(self):
        source = "### Proof\n\n*Construction..* We construct it.\n"
        self.assertEqual(
            clean_markdown(source), "### Construction\n\nWe construct it.\n"
        )


if __name__ == "__main__":
    unittest.main()
