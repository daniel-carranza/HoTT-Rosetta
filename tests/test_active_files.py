import json
import tempfile
import unittest
from pathlib import Path

from rosetta.active_files import active_file, active_files
from rosetta.agda_review import AgdaReviewRecord
from rosetta.review_web import render_file_index, render_file_reader


class ActiveFileTests(unittest.TestCase):
    def _root(self, directory):
        root = Path(directory)
        (root / "data").mkdir()
        (root / "data" / "project-layout.json").write_text(
            json.dumps(
                {"format_version": 1, "rosetta_directory": "work/rosetta"}
            )
        )
        (root / "data" / "rosetta-files.json").write_text(
            json.dumps(
                {
                    "format_version": 1,
                    "files": {
                        "section:1:1": "section-1-1-example.lagda.md",
                        "section:1:2": "section-1-2-example.lagda.md",
                    },
                }
            )
        )
        (root / "work" / "rosetta").mkdir(parents=True)
        return root

    def _record(self, **changes):
        values = dict(
            block_id="definition-1.2.3-example",
            item_id="definition-1.2.3",
            destination="section-1-2-example.lagda.md",
            provenance_kind="exact",
            statement="## Definition 1.2.3\n\nA definition.",
            project_code="A : Type",
            source_code="A : Type",
            source_location="example:1-1",
            source_commit="abc",
            exact_match=True,
            document_sha256="digest",
            conversion_status="ready",
            conversion_note="",
            state="pending",
            comments=[],
        )
        values.update(changes)
        return AgdaReviewRecord(**values)

    def test_configured_generated_files_are_the_only_files_listed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._root(directory)
            wanted = root / "work" / "rosetta" / "section-1-1-example.lagda.md"
            wanted.write_text("generated\n")
            (root / "work" / "rosetta" / "notes.md").write_text("notes\n")
            self.assertEqual(active_files(root), [wanted])
            self.assertEqual(active_file(root, wanted.name), wanted)
            with self.assertRaisesRegex(ValueError, "Invalid"):
                active_file(root, "../outside.lagda.md")

    def test_read_only_index_and_markdown_preview(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._root(directory)
            path = root / "work" / "rosetta" / "section-1-2-example.lagda.md"
            path.write_text("## Definition 1.2.3\n\nold <text>\n")
            index = render_file_index([path])
            reader = render_file_reader(path.name, path.read_text())
            self.assertIn("Generated Rosetta files", index)
            self.assertIn(path.name, index)
            self.assertIn("<h2 id=\"item-1.2.3\"", reader)
            self.assertIn("old &lt;text&gt;", reader)
            self.assertNotIn("Edit", reader)

    def test_reader_links_item_and_proof_to_review(self):
        record = self._record()
        reader = render_file_reader(
            record.destination,
            "## Definition 1.2.3\n\nA definition.\n\n## Proof\n\nDone.\n",
            [record],
        )
        self.assertEqual(reader.count("/agda/" + record.block_id), 2)

    def test_reader_links_exercise_to_missing_code_review(self):
        record = self._record(
            block_id="missing-agda-exercise-1-2-example-exercise-1-2",
            item_id="exercise-1-2",
            destination="exercise-1-2-example.lagda.md",
            provenance_kind="missing",
            statement="The exercise prompt.",
            project_code="",
            source_code="",
            conversion_status="missing",
        )
        reader = render_file_reader(
            record.destination,
            "## Problem statement\n\nA task.\n\n## Solution\n",
            [record],
        )
        self.assertEqual(reader.count("/agda/" + record.block_id), 2)


if __name__ == "__main__":
    unittest.main()
