import unittest

from rosetta.proof_trees import render_proof_tree, render_proof_tree_markdown


class ProofTreeTests(unittest.TestCase):
    def test_binary_tree_preserves_premises_and_conclusion(self):
        draft = render_proof_tree(
            r"\AxiomC{$a:A$}\AxiomC{$f:A\to B$}\BinaryInfC{$f(a):B$}"
        )
        self.assertIn("a:A", draft.art)
        self.assertIn("f:A→ B", draft.art)
        self.assertIn("f(a):B", draft.art)
        self.assertIn("─", draft.art)

    def test_review_marker_is_stable(self):
        rendered = render_proof_tree_markdown(r"\AxiomC{$A$}\UnaryInfC{$B$}")
        self.assertIn("rosetta-proof-tree:", rendered)
        self.assertIn("review: pending", rendered)


if __name__ == "__main__":
    unittest.main()
