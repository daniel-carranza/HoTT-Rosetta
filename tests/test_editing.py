import tempfile
import unittest
from pathlib import Path

from rosetta.editing import EditConflict, apply_edit, preview_edit


class EditingTests(unittest.TestCase):
    def test_edit_is_atomic_and_backed_up(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "data" / "example.lagda.md"
            path.parent.mkdir()
            path.write_text("old\n")
            preview = preview_edit(path, "new\n")
            self.assertIn("-old", preview.diff)
            self.assertIn("+new", preview.diff)
            backup = apply_edit(preview, root)
            self.assertEqual(path.read_text(), "new\n")
            self.assertEqual(backup.read_text(), "old\n")

    def test_concurrent_change_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "example.lagda.md"
            path.write_text("first\n")
            preview = preview_edit(path, "proposed\n")
            path.write_text("another reviewer changed this\n")
            with self.assertRaises(EditConflict):
                apply_edit(preview, root)
            self.assertEqual(path.read_text(), "another reviewer changed this\n")

    def test_cannot_edit_outside_repository(self):
        with tempfile.TemporaryDirectory() as repository_directory:
            with tempfile.TemporaryDirectory() as outside_directory:
                root = Path(repository_directory)
                path = Path(outside_directory) / "outside.md"
                path.write_text("old\n")
                preview = preview_edit(path, "new\n")
                with self.assertRaisesRegex(ValueError, "outside"):
                    apply_edit(preview, root)


if __name__ == "__main__":
    unittest.main()
