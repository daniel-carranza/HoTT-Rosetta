import unittest
import json

from rosetta.audit import (
    _substantive_agda_blocks,
    audit_agda_sources,
    audit_verbatim_sources,
    extract_existing_agda_blocks,
)


class AuditTests(unittest.TestCase):
    def _active_directory(self, root, files):
        (root / "data").mkdir(exist_ok=True)
        (root / "data" / "project-layout.json").write_text(
            json.dumps(
                {"format_version": 1, "rosetta_directory": "work/rosetta"}
            )
        )
        registry = {}
        for name in files:
            parts = name.split("-")
            registry[f"{parts[0]}:{int(parts[1])}:{int(parts[2])}"] = name
        (root / "data" / "rosetta-files.json").write_text(
            json.dumps({"format_version": 1, "files": registry})
        )
        active = root / "work" / "rosetta"
        active.mkdir(parents=True)
        return active

    def test_module_and_import_block_is_not_substantive(self):
        markdown = """```agda
module example where

open import dependency
```
"""
        self.assertEqual(_substantive_agda_blocks(markdown), 0)

    def test_definition_block_is_substantive(self):
        markdown = """```agda
module example where
```

```agda
answer : ℕ
answer = 42
```
"""
        self.assertEqual(_substantive_agda_blocks(markdown), 1)

    def test_existing_block_is_associated_with_preceding_item(self):
        import tempfile
        from pathlib import Path

        markdown = """## Definition 3.2.1

Text.

```agda
answer = 42
```
"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "section.lagda.md"
            path.write_text(markdown)
            blocks = extract_existing_agda_blocks(path)
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0].item_id, "definition-3.2.1")
        self.assertEqual(blocks[0].start_line, 6)

    def test_source_audit_includes_sections_and_exercises(self):
        import tempfile
        from pathlib import Path

        markdown = """```agda
module example where
```

```agda
answer = 42
```
"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "external" / "agda-unimath" / "src" / "source.lagda.md"
            source.parent.mkdir(parents=True)
            source.write_text("```agda\nanswer = 42\n```\n")
            active = self._active_directory(
                root,
                ["section-3-1-example.lagda.md", "exercise-3-1-example.lagda.md"],
            )
            (active / "section-3-1-example.lagda.md").write_text(markdown)
            (active / "exercise-3-1-example.lagda.md").write_text(markdown)

            blocks, matches = audit_verbatim_sources(root, 3, 3)

        self.assertEqual(
            [block.destination for block in blocks],
            ["exercise-3-1-example.lagda.md", "section-3-1-example.lagda.md"],
        )
        self.assertTrue(all(matches[(block.destination, block.start_line)] for block in blocks))

    def test_source_audit_finds_combined_exact_excerpts(self):
        import tempfile
        from pathlib import Path

        upstream = """first-definition : Type
first-definition = Type

unused-definition = Type

second-definition : Type
second-definition = Type
"""
        combined = """```agda
first-definition : Type
first-definition = Type

second-definition : Type
second-definition = Type
```
"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "external" / "agda-unimath" / "src" / "source.lagda.md"
            source.parent.mkdir(parents=True)
            source.write_text(upstream)
            active = self._active_directory(
                root, ["section-3-1-example.lagda.md"]
            )
            destination = active / "section-3-1-example.lagda.md"
            destination.write_text(combined)

            blocks, evidence = audit_agda_sources(root, 3, 3)

        key = (blocks[0].destination, blocks[0].start_line)
        self.assertEqual(evidence[key].category, "exact-excerpts")
        self.assertEqual(evidence[key].sources, ["src/source.lagda.md"])


if __name__ == "__main__":
    unittest.main()
