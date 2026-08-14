import unittest
from pathlib import Path

from rosetta.references import (
    Reference,
    build_reference_index,
    reference_wording,
    resolve_markdown_references,
)
from rosetta.pandoc import markdown_to_safe_html


ROOT = Path(__file__).resolve().parent.parent


class ReferenceTests(unittest.TestCase):
    def test_book_reference_index(self):
        index = build_reference_index(ROOT / "book")
        self.assertEqual(index["sec:identity"], Reference("Chapter", "5"))
        self.assertEqual(
            index["prp:unit-laws-add-N"], Reference("Proposition", "5.6.1")
        )
        self.assertEqual(
            index["ex:semi-ring-laws-N"], Reference("Exercise", "5.5")
        )
        self.assertEqual(
            index["ex:distributive-mul-addN"], Reference("Exercise", "5.5")
        )
        self.assertEqual(index["chap:uf"], Reference("Chapter", "II"))
        self.assertEqual(index["table:Curry-Howard"].wording, "the following table")
        self.assertEqual(index["eq:well-ordering"].wording, "(*)")
        self.assertEqual(index["item:count-Sigma"].wording, "(2)")
        self.assertEqual(index["item:thm-quotient-up"].wording, "(1)")
        self.assertEqual(index["item:thm-quotient-effective"].wording, "(2)")
        self.assertEqual(index["item:thm-quotient-up-image"].wording, "(3)")
        self.assertEqual(index["item:dup-set-truncation"].wording, "(2)")

    def test_multiple_references_use_plural_wording(self):
        index = {
            "a": Reference("Proposition", "5.6.1"),
            "b": Reference("Proposition", "5.6.2"),
        }
        self.assertEqual(
            reference_wording(["a", "b"], index),
            "Propositions 5.6.1 and 5.6.2",
        )

    def test_unknown_reference_stays_visible(self):
        html = (
            '<a href="#missing" data-reference-type="ref" '
            'data-reference="missing">[missing]</a>'
        )
        self.assertEqual(
            resolve_markdown_references(html, {}),
            "**[unresolved reference: missing]**",
        )

    def test_fixture_backed_list_and_equation_aliases(self):
        index = build_reference_index(ROOT / "book")
        self.assertEqual(
            reference_wording(
                ["eq:multiples-of-gcd", "eq:common-divisors"], index
            ),
            "the two displayed types",
        )
        encoded = (
            '<a href="#item" data-reference-type="ref" '
            'data-reference="item:f-up-trunc-Prop&#39;">[item]</a>'
        )
        self.assertEqual(resolve_markdown_references(encoded, index), "(ii)")

    def test_equation_aliases_are_markdown_safe_and_sentence_capitalized(self):
        index = build_reference_index(ROOT / "book")
        group = (
            '<a href="#group" data-reference-type="ref" '
            'data-reference="eq:multiples-of-gcd,eq:common-divisors">[group]</a>'
        )
        single = (
            '<a href="#single" data-reference-type="ref" '
            'data-reference="eq:common-divisors">[single]</a>'
        )
        markdown = resolve_markdown_references(
            f"Previous paragraph.\n\n{group} are useful. The type in {single} "
            "is least *nonzero* and *bounded*.",
            index,
        )
        self.assertIn("The two displayed types", markdown)
        self.assertIn(r"(\*\*)", markdown)
        rendered = markdown_to_safe_html(markdown)
        self.assertIn("The two displayed types", rendered)
        self.assertIn("(**)", rendered)
        self.assertEqual(rendered.count("<em>"), 2)
        self.assertEqual(rendered.count("</em>"), 2)


if __name__ == "__main__":
    unittest.main()
