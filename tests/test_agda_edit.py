import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from rosetta.agda_edit import apply_agda_block_edit, preview_agda_block_edit


class AgdaEditTests(unittest.TestCase):
    def _root(self, directory: str) -> tuple[Path, Path]:
        root = Path(directory)
        (root / "data").mkdir()
        (root / "data" / "project-layout.json").write_text(json.dumps({
            "format_version": 1, "rosetta_directory": "product",
        }))
        (root / "product").mkdir()
        (root / "product" / "section-1-1-example.lagda.md").write_text(
            "# Collaborator prose\n\n"
            "```agda\nmodule section-1-1-example where\n```\n\n"
            "<!-- rosetta-agda-block: example-block -->\n\n"
            "```agda\noriginal : Set\noriginal = Set\n```\n\n"
            "Manually improved ending.\n"
        )
        source = root / "external" / "agda-unimath" / "src" / "example.lagda.md"
        source.parent.mkdir(parents=True)
        source.write_text("original : Set\noriginal = Set\n")
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        shard = root / "data" / "agda-blocks-example.json"
        shard.write_text(json.dumps({
            "format_version": 1,
            "blocks": [{
                "block_id": "example-block",
                "provenance_kind": "exact",
                "item_id": "definition-1.1.1",
                "destination": "section-1-1-example.lagda.md",
                "source_file": "src/example.lagda.md",
                "source_commit": "abc",
                "source_start_line": 1,
                "source_end_line": 2,
                "source_sha256": digest,
                "order": 0,
                "imports": [],
                "code": "original : Set\noriginal = Set",
            }],
        }, indent=2) + "\n")
        (root / "data" / "agda-blocks.json").write_text(json.dumps({
            "format_version": 1,
            "includes": [shard.name],
            "blocks": [],
        }, indent=2) + "\n")
        return root, shard

    def test_edit_requires_note_and_changes_exact_block_to_adapted(self):
        with tempfile.TemporaryDirectory() as directory:
            root, _ = self._root(directory)
            with self.assertRaisesRegex(ValueError, "adaptation note"):
                preview_agda_block_edit(root, "example-block", "changed")
            edit = preview_agda_block_edit(
                root, "example-block", "changed", "Adjusted for local names."
            )
            self.assertEqual(edit.provenance_kind, "adapted")
            self.assertIn('"provenance_kind": "adapted"', edit.preview.diff)
            self.assertIn("Adjusted for local names.", edit.preview.diff)

    def test_legacy_apply_is_disabled_and_cannot_write_content_or_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            root, shard = self._root(directory)
            edit = preview_agda_block_edit(
                root, "example-block", "changed", "Adjusted for local names."
            )
            generated = root / "product" / "section-1-1-example.lagda.md"
            original = generated.read_text()
            manifest = shard.read_bytes()
            with self.assertRaisesRegex(ValueError, "read-only"):
                apply_agda_block_edit(
                    root, "example-block", "changed", "Adjusted for local names.",
                    edit.evidence_digest,
                )
            self.assertEqual(generated.read_text(), original)
            self.assertEqual(shard.read_bytes(), manifest)
            self.assertFalse((root / ".rosetta-backups").exists())
            self.assertIn("+changed", edit.document_preview.diff)
            self.assertEqual(edit.document_preview.new_text, original.replace("original : Set\noriginal = Set", "changed"))

    def test_confirmation_rejects_manifest_changed_after_preview(self):
        with tempfile.TemporaryDirectory() as directory:
            root, shard = self._root(directory)
            edit = preview_agda_block_edit(
                root, "example-block", "changed", "Adjusted for local names."
            )
            shard.write_text(shard.read_text() + "\n")
            with self.assertRaisesRegex(ValueError, "read-only"):
                apply_agda_block_edit(
                    root,
                    "example-block",
                    "changed",
                    "Adjusted for local names.",
                    edit.evidence_digest,
                )


if __name__ == "__main__":
    unittest.main()
