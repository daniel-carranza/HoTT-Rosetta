import tempfile
import unittest
from pathlib import Path

from rosetta.compare import (
    comparison_issues,
    candidate_raw_tex_commands,
    compare_section,
    pending_diagram_count,
    raw_tex_commands_outside_fences,
)


class CompareTests(unittest.TestCase):
    def test_agda_code_does_not_reduce_prose_similarity(self):
        generated = "# Section 3.1 Example\n\nThe same prose.\n"
        expected = generated + "\n```agda\nanswer = 42\n```\n"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "fixture.lagda.md"
            path.write_text(expected)
            result = compare_section(generated, path, root)
        self.assertEqual(result.prose_similarity, 1.0)

    def test_inline_math_and_maintainer_notes_do_not_reduce_prose_similarity(self):
        generated = """# Section 1.1 Example

The source prose uses `generated-notation`.
    This indented continuation is source prose too.
"""
        expected = """# Section 1.1 Example

The source prose uses `document-notation`.
    This indented continuation is source prose too.
TODO: This is a maintainer review note.

## Agda-unimath sources

- A manually recorded provenance note.
"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture = root / "fixture.lagda.md"
            fixture.write_text(expected)
            result = compare_section(generated, fixture, root)
        self.assertEqual(result.prose_similarity, 1.0)

    def test_automatic_diagram_caption_does_not_count_as_source_prose(self):
        generated = """# Section 1.1 Example

Source prose.

<!-- rosetta-diagram: abc123; review: pending -->

*Square-shaped diagram (automatic draft).*

```text
[A] ----> [B]
```
"""
        expected = "# Section 1.1 Example\n\nSource prose.\n"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture = root / "fixture.lagda.md"
            fixture.write_text(expected)
            result = compare_section(generated, fixture, root)
        self.assertEqual(result.prose_similarity, 1.0)

    def test_raw_tex_outside_code_is_reported(self):
        generated = "Text with \\mystery here.\n"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "fixture.lagda.md"
            path.write_text("Text here.\n")
            result = compare_section(generated, path, root)
        self.assertEqual(result.raw_tex_commands, [r"\mystery"])
        self.assertIn("raw TeX remains", comparison_issues(result))

    def test_pending_diagram_is_not_unfinished_notation(self):
        generated = """<!-- rosetta-diagram: abc123; review: pending -->
```text
[A] ----> [B]
```
"""
        self.assertEqual(raw_tex_commands_outside_fences(generated), [])
        self.assertEqual(pending_diagram_count(generated), 1)
        self.assertEqual(candidate_raw_tex_commands(generated), [])

    def test_candidate_checks_unfinished_notation_in_ordinary_display(self):
        generated = """```text
\\unfinished(A)
```
"""
        self.assertEqual(candidate_raw_tex_commands(generated), [r"\unfinished"])

    def test_fixture_heading_presentation_is_normalized(self):
        generated = """# Section 8.3 The well-ordering principle of ℕ

### Proof
"""
        expected = """# Section 8.3 The well-ordering principle of natural numbers

## Proof of Theorem 8.3.1

## Agda-unimath sources
"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture = root / "fixture.lagda.md"
            fixture.write_text(expected)
            result = compare_section(generated, fixture, root)
        self.assertEqual(result.matching_headings, result.expected_headings)

    def test_classified_display_layout_does_not_fail_fidelity(self):
        generated = "# Section 7.1 Example\n\n```text\na\n```\n"
        expected = "# Section 7.1 Example\n"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture = root / "section-7-1-example.lagda.md"
            fixture.write_text(expected)
            result = compare_section(generated, fixture, root)
        self.assertTrue(result.display_difference_classification)
        self.assertNotIn("display math differs", comparison_issues(result))


if __name__ == "__main__":
    unittest.main()
