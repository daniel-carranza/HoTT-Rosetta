import tempfile
import unittest
import json
from pathlib import Path
from unittest.mock import patch

from rosetta.agda_manifest import AgdaBlock, load_manifest
from rosetta.generate import (
    agda_typecheck_options, candidate_chapter, candidate_exercise, candidate_section,
    section_module_name, slugify, write_candidate,
)
from rosetta.latex import inventory


class GenerateTests(unittest.TestCase):
    @patch("rosetta.generate.subprocess.run")
    def test_agda_interface_option_is_used_when_supported(self, run):
        run.return_value.stdout = "  --no-write-interfaces"
        run.return_value.stderr = ""
        self.assertEqual(
            agda_typecheck_options("agda"),
            ["--no-libraries", "--no-write-interfaces"],
        )

    @patch("rosetta.generate.subprocess.run")
    def test_agda_interface_option_is_omitted_when_unsupported(self, run):
        run.return_value.stdout = "Agda 2.8 help"
        run.return_value.stderr = ""
        self.assertEqual(agda_typecheck_options("agda"), ["--no-libraries"])

    def test_candidate_section_rejects_curated_destination_name_mismatch(self):
        root = Path(__file__).resolve().parent.parent
        section = inventory(root / "book")[2]
        block = AgdaBlock(
            block_id="registered-name",
            provenance_kind="handwritten",
            item_id="section-3.1",
            destination="section-3-1-registered-name.lagda.md",
            source_file="", source_commit="", source_start_line=0,
            source_end_line=0, source_sha256="", code="example = 1",
            order=1, imports=[], source_note="Local test.",
        )
        with self.assertRaisesRegex(ValueError, "registered filename"):
            candidate_section(section, 1, [block])

    def test_slug_and_module_name(self):
        self.assertEqual(slugify("Peano's seventh and eighth axioms"), "peanos-seventh-and-eighth-axioms")
        self.assertEqual(
            section_module_name(6, 4, "Peano's seventh and eighth axioms"),
            "section-6-4-peanos-seventh-and-eighth-axioms",
        )
        self.assertEqual(
            slugify(r"The laws of addition on \texorpdfstring{$\N$}{ℕ}"),
            "the-laws-of-addition-on-natural-numbers",
        )

    def test_candidate_is_written_only_under_build_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "data").mkdir()
            (root / "data" / "project-layout.json").write_text(
                json.dumps(
                    {"format_version": 1, "rosetta_directory": "product"}
                )
            )
            destination = write_candidate(root, "section-18-1-example.lagda.md", "text")
            self.assertEqual(
                destination,
                root / "product" / "section-18-1-example.lagda.md",
            )
            self.assertEqual(destination.read_text(), "text")

    def test_block_imports_are_added_to_module_header(self):
        root = Path(__file__).resolve().parent.parent
        section = inventory(root / "book")[2]
        block = AgdaBlock(
            block_id="example",
            provenance_kind="exact",
            item_id="definition-3.2.1",
            destination="section-3-2-addition-on-the-natural-numbers.lagda.md",
            source_file="example",
            source_commit="abc",
            source_start_line=1,
            source_end_line=1,
            source_sha256="abc",
            code="example = 1",
            order=1,
            imports=["section-3-1-the-formal-specification-of-the-type-of-natural-numbers"],
        )
        _, document = candidate_section(section, 2, [block])
        self.assertIn(
            "open import section-3-1-the-formal-specification-of-the-type-of-natural-numbers",
            document,
        )

    def test_section_level_anchor_supports_unnumbered_code(self):
        root = Path(__file__).resolve().parent.parent
        section = inventory(root / "book")[2]
        block = AgdaBlock(
            block_id="section-level-example",
            provenance_kind="handwritten",
            item_id="section-3.3",
            destination="section-3-3-pattern-matching.lagda.md",
            source_file="",
            source_commit="",
            source_start_line=0,
            source_end_line=0,
            source_sha256="",
            source_note="Local example.",
            code="example = 1",
            order=1,
            imports=[],
        )
        _, document = candidate_section(section, 3, [block])
        self.assertIn("<!-- rosetta-item: section-3.3 -->", document)
        self.assertIn("example = 1", document)

    def test_chapter_three_foundational_blocks_are_generated(self):
        root = Path(__file__).resolve().parent.parent
        section = inventory(root / "book")[2]
        blocks = load_manifest(root / "data" / "agda-blocks.json")
        _, document = candidate_section(section, 1, blocks)
        self.assertIn(
            "<!-- rosetta-item: "
            "subheading-3.1-the-introduction-rules-of-natural-numbers -->",
            document,
        )
        self.assertIn("data ℕ : Type lzero where", document)
        self.assertIn("ind-ℕ :", document)
        self.assertIn("rec-ℕ = ind-ℕ", document)
        self.assertIn("open import universe-levels", document)

    def test_exercise_and_chapter_candidates_are_self_contained(self):
        root = Path(__file__).resolve().parent.parent
        section = inventory(root / "book")[2]
        exercise_name, exercise = candidate_exercise(root, section, 1)
        self.assertIn(f"module {exercise_name.removesuffix('.lagda.md')} where", exercise)
        self.assertIn("## Problem statement", exercise)
        chapter_name, chapter = candidate_chapter(root, section)
        self.assertIn(f"module {chapter_name.removesuffix('.lagda.md')} where", chapter)
        self.assertIn("open import section-3-1-", chapter)

    def test_exercise_manifest_blocks_are_inserted_at_solution_anchor(self):
        root = Path(__file__).resolve().parent.parent
        section = inventory(root / "book")[2]
        blocks = load_manifest(root / "data" / "agda-blocks.json")
        _, exercise = candidate_exercise(root, section, 2, blocks)
        self.assertIn("<!-- rosetta-item: exercise-3-2 -->", exercise)
        self.assertIn("<!-- rosetta-agda-block: exercise-3-2-min-and-max-block-1 -->", exercise)
        self.assertIn("min-ℕ : ℕ → (ℕ → ℕ)", exercise)
        self.assertNotIn("No formalization has been curated yet", exercise)

    def test_chapter_four_boolean_exercise_is_fully_curated(self):
        root = Path(__file__).resolve().parent.parent
        section = inventory(root / "book")[3]
        blocks = load_manifest(root / "data" / "agda-blocks.json")
        _, exercise = candidate_exercise(root, section, 2, blocks)
        self.assertIn("data bool : Type lzero where", exercise)
        self.assertIn("ind-bool :", exercise)
        self.assertIn("neg-bool :", exercise)
        self.assertIn("and-bool :", exercise)
        self.assertIn("or-bool :", exercise)

    def test_chapter_four_negation_exercise_blocks_are_curated(self):
        root = Path(__file__).resolve().parent.parent
        section = inventory(root / "book")[3]
        blocks = load_manifest(root / "data" / "agda-blocks.json")
        _, exercise = candidate_exercise(root, section, 3, blocks)
        self.assertIn("law-of-non-contradiction :", exercise)
        self.assertIn("double-negation-kleisli-map :", exercise)
        self.assertIn("not-not-lem :", exercise)

    def test_chapter_four_list_exercise_blocks_are_curated(self):
        root = Path(__file__).resolve().parent.parent
        section = inventory(root / "book")[3]
        blocks = load_manifest(root / "data" / "agda-blocks.json")
        _, exercise = candidate_exercise(root, section, 4, blocks)
        self.assertIn("data list", exercise)
        self.assertIn("fold-list :", exercise)
        self.assertIn("flatten-list :", exercise)
        self.assertIn("reverse-list :", exercise)

    def test_chapter_five_exercise_blocks_are_all_curated(self):
        root = Path(__file__).resolve().parent.parent
        section = inventory(root / "book")[4]
        blocks = load_manifest(root / "data" / "agda-blocks.json")
        for number in range(1, 9):
            filename, exercise = candidate_exercise(root, section, number, blocks)
            selected = [block for block in blocks if block.destination == filename]
            self.assertTrue(selected, filename)
            self.assertNotIn("No formalization has been curated yet", exercise)

    def test_chapter_six_exercise_blocks_are_all_curated(self):
        root = Path(__file__).resolve().parent.parent
        section = inventory(root / "book")[5]
        blocks = load_manifest(root / "data" / "agda-blocks.json")
        for number in range(1, 7):
            filename, exercise = candidate_exercise(root, section, number, blocks)
            selected = [block for block in blocks if block.destination == filename]
            self.assertTrue(selected, filename)
            self.assertNotIn("No formalization has been curated yet", exercise)

    def test_blocked_exercise_block_is_reviewable_but_not_generated(self):
        root = Path(__file__).resolve().parent.parent
        section = inventory(root / "book")[2]
        blocks = load_manifest(root / "data" / "agda-blocks.json")
        _, exercise = candidate_exercise(root, section, 6, blocks)
        blocked = [
            block for block in blocks
            if block.conversion_status == "blocked"
            and block.destination == "exercise-3-6-division-by-two.lagda.md"
        ]
        self.assertEqual(len(blocked), 1)
        self.assertNotIn(blocked[0].block_id, exercise)
        self.assertNotIn("{!", exercise)


if __name__ == "__main__":
    unittest.main()
