import tempfile
import unittest
import json
from pathlib import Path

from rosetta.math_text import normalize_markdown_math
from rosetta.review import (
    diagram_review_items,
    discover_diagram_reviews,
    load_review_store,
    source_diagrams,
    update_diagram_review,
)


class ReviewTests(unittest.TestCase):
    def _configure(self, root: Path):
        data = root / "data"
        data.mkdir(exist_ok=True)
        (data / "project-layout.json").write_text(json.dumps({"format_version": 1, "rosetta_directory": "work/rosetta"}))
        (data / "rosetta-files.json").write_text(json.dumps({"format_version": 1, "files": {"section:1:1": "section-1-1-example.lagda.md"}}))

    def _review_repository(self, root: Path, source: str) -> str:
        markdown = normalize_markdown_math(f"``` math\n{source}\n```")
        (root / "book").mkdir()
        (root / "book" / "sample.tex").write_text(source)
        self._configure(root)
        candidates = root / "work" / "rosetta"
        candidates.mkdir(parents=True)
        (candidates / "section-1-1-example.lagda.md").write_text(markdown)
        data = root / "data"
        (data / "diagram-reviews.json").write_text(
            '{\n  "version": 1,\n  "diagrams": {}\n}\n'
        )
        return discover_diagram_reviews(root)[0].item.stable_id

    def test_diagram_draft_is_paired_with_original_source(self):
        source = r"""\begin{tikzcd}
A \arrow[r,"f"] & B
\end{tikzcd}"""
        markdown = normalize_markdown_math(f"``` math\n{source}\n```")
        with tempfile.TemporaryDirectory() as directory:
            book = Path(directory)
            (book / "sample.tex").write_text(source)
            items = diagram_review_items(markdown, source_diagrams(book))
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].state, "pending")
        self.assertEqual(items[0].description, "Linear diagram")
        self.assertIn("[A]", items[0].ascii_art)
        self.assertEqual(items[0].source, source)

    def test_repository_review_discovery_records_destination(self):
        source = r"""\begin{tikzcd}
A \arrow[r] & B
\end{tikzcd}"""
        markdown = normalize_markdown_math(f"``` math\n{source}\n```")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "book").mkdir()
            (root / "book" / "sample.tex").write_text(source)
            self._configure(root)
            candidates = root / "work" / "rosetta"
            candidates.mkdir(parents=True)
            candidate = candidates / "section-1-1-example.lagda.md"
            candidate.write_text(markdown)
            records = discover_diagram_reviews(root)
        self.assertEqual(len(records), 1)
        self.assertEqual(
            records[0].destination,
            "work/rosetta/section-1-1-example.lagda.md",
        )

    def test_approval_and_comment_are_shared_and_source_bound(self):
        source = r"""\begin{tikzcd}
A \arrow[r] & B
\end{tikzcd}"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            stable_id = self._review_repository(root, source)
            update_diagram_review(root, stable_id, state="approved")
            update_diagram_review(root, stable_id, comment="Looks clear.")
            item = discover_diagram_reviews(root)[0].item
            store = load_review_store(root / "data" / "diagram-reviews.json")
            has_backup = any(
                path.is_file() for path in (root / ".rosetta-backups").rglob("*")
            )
        self.assertEqual(item.state, "approved")
        self.assertEqual(item.comments, ["Looks clear."])
        self.assertIn(stable_id, store["diagrams"])
        self.assertTrue(has_backup)


if __name__ == "__main__":
    unittest.main()
