import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from rosetta.agda_review import (
    AgdaReviewRecord,
    ReviewComment,
    _review_digest,
    _exercise_statement,
    _with_stored_review,
    discover_agda_reviews,
    load_agda_review_store,
    update_agda_review,
)
from rosetta.review_web import (
    render_agda_editor,
    render_agda_code_diff,
    render_agda_edit_preview,
    render_index,
    render_loading,
    render_record,
    run_block_typecheck,
)


class AgdaReviewTests(unittest.TestCase):
    def _record(self):
        return AgdaReviewRecord(
            block_id="definition-1.1.1-example",
            item_id="definition-1.1.1",
            destination="section-1-1-example.lagda.md",
            provenance_kind="exact",
            statement="## Definition 1.1.1\n\nA type.",
            project_code="A : Type",
            source_code="A : Type",
            source_location="src/example.lagda.md:10-10",
            source_commit="abc123",
            exact_match=True,
            document_sha256="document-digest",
            conversion_status="ready",
            conversion_note="",
            state="pending",
            comments=[],
        )

    def test_repository_manifest_blocks_are_reviewable(self):
        root = Path(__file__).resolve().parent.parent
        records = discover_agda_reviews(root)
        curated = [record for record in records if record.provenance_kind != "missing"]
        missing = [record for record in records if record.provenance_kind == "missing"]
        self.assertEqual(len(curated), 406)
        self.assertEqual(sum(record.exact_match for record in curated), 172)
        self.assertEqual(sum(record.provenance_kind == "adapted" for record in curated), 176)
        self.assertEqual(sum(record.provenance_kind == "handwritten" for record in curated), 58)
        self.assertTrue(missing)
        self.assertTrue(all(not record.project_code for record in missing))
        self.assertTrue(all(record.typecheck_status == "not-applicable" for record in missing))
        daniel_comments = [
            comment
            for record in records
            for comment in record.comments
            if comment.author == "Daniel C"
        ]
        self.assertGreaterEqual(len(daniel_comments), 11)
        self.assertEqual(sum(record.conversion_status == "blocked" for record in records), 29)
        self.assertTrue(all(record.statement for record in records))
        self.assertTrue(all(record.document_sha256 for record in records))

    def test_exercise_review_uses_problem_statement_not_solution(self):
        document = """# Exercise 8.1

## Problem statement

Show that the proposition is decidable.

## Solution

```agda
answer : Type
```
"""
        statement = _exercise_statement(document, document.index("```agda"))
        self.assertEqual(
            statement,
            "## Problem statement\n\nShow that the proposition is decidable.",
        )
        self.assertNotIn("Solution", statement)

    def test_approval_and_comment_use_protected_store(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "data").mkdir()
            (root / "data" / "agda-reviews.json").write_text(
                '{\n  "version": 1,\n  "blocks": {}\n}\n'
            )
            record = self._record()
            with patch(
                "rosetta.agda_review.discover_agda_reviews", return_value=[record]
            ):
                update_agda_review(
                    root, record.block_id, state="approved", comment="Checked.",
                    comment_author="Daniel C",
                )
            store = load_agda_review_store(root / "data" / "agda-reviews.json")
            saved = store["blocks"][record.block_id]
            self.assertEqual(saved["state"], "approved")
            self.assertEqual(
                saved["comments"], [{"author": "Daniel C", "text": "Checked."}]
            )
            self.assertTrue(any((root / ".rosetta-backups").rglob("*")))

    def test_cached_record_avoids_rediscovering_all_reviews(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "data").mkdir()
            (root / "data" / "agda-reviews.json").write_text(
                '{\n  "version": 1,\n  "blocks": {}\n}\n'
            )
            record = self._record()
            with patch("rosetta.agda_review.discover_agda_reviews") as discover:
                update_agda_review(
                    root,
                    record.block_id,
                    state="approved",
                    current_record=record,
                )
            discover.assert_not_called()
            saved = load_agda_review_store(root / "data" / "agda-reviews.json")
            self.assertEqual(saved["blocks"][record.block_id]["state"], "approved")

    def test_browser_pages_show_three_review_columns_and_escape_code(self):
        record = self._record()
        detail = render_record(record)
        index = render_index([record])
        self.assertIn("Book statement or proof", detail)
        self.assertIn("<h2", detail)
        self.assertIn("Rosetta Agda code", detail)
        self.assertIn("Recorded source code", detail)
        self.assertIn("Show highlighted Agda diff", detail)
        self.assertIn("identical to the recorded source", detail)
        self.assertIn("Approve", detail)
        self.assertIn("Run Agda check", detail)
        self.assertIn("Edit Agda code", detail)
        self.assertIn("Open scratchpad editor", detail)
        self.assertNotIn("<textarea name='code'", detail)
        self.assertIn("Agda: not-checked", detail)
        self.assertEqual(detail.count("All blocks"), 2)
        self.assertIn("class='comment-box'", detail)
        self.assertLess(detail.index("Existing comments"), detail.index("Add a shared comment"))
        commented = AgdaReviewRecord(
            **{**record.to_dict(), "comments": [ReviewComment("Daniel C", "Check this.")]}
        )
        self.assertIn("Daniel C", render_record(commented))
        self.assertIn("definition-1.1.1", index)
        self.assertIn("Find an item", index)
        self.assertIn("agda-search", index)
        self.assertIn("Only items with comments", index)
        self.assertIn("data-has-comments='false'", index)
        unsafe = AgdaReviewRecord(**{**record.to_dict(), "project_code": "x < y"})
        self.assertIn("x &lt; y", render_record(unsafe))

        changed = AgdaReviewRecord(
            **{
                **record.to_dict(),
                "project_code": "A : Set\nlocal = A",
                "source_code": "A : Type\nupstream = A",
                "exact_match": False,
            }
        )
        code_diff = render_agda_code_diff(changed)
        self.assertIn("class='diff-delete'>− A : Type", code_diff)
        self.assertIn("class='diff-add'>+ A : Set", code_diff)
        self.assertIn("− agda-unimath", code_diff)
        self.assertIn("+ Rosetta", code_diff)

        editor = render_agda_editor(record, "token")
        self.assertIn("Agda scratchpad", editor)
        self.assertIn("Save scratchpad draft", editor)
        self.assertIn("A : Type", editor)
        self.assertIn("← Return to review", editor)

        edit_preview = render_agda_edit_preview(
            record,
            "A : Type\nA = Type",
            "Local adjustment.",
            "-A : Type\n+A : Set",
            "digest",
            "adapted",
            "token",
        )
        self.assertIn("Confirm and save Agda edit", edit_preview)
        self.assertIn("-A : Type", edit_preview)
        self.assertIn("adapted", edit_preview)

        commented_index = render_index([commented])
        self.assertIn("data-has-comments='true'", commented_index)

    def test_loading_page_reports_progress_and_polls_until_ready(self):
        page = render_loading()
        self.assertIn("Preparing the review workspace", page)
        self.assertIn("generated book, Agda blocks, provenance", page)
        self.assertIn("fetch('/status'", page)
        self.assertIn("location.reload()", page)
        self.assertIn("status.message", page)

    def test_successful_agda_check_hides_progress_output(self):
        record = self._record()
        progress = "Checking candidate-example\n Checking imported-module"
        passed = AgdaReviewRecord(
            **{
                **record.to_dict(),
                "typecheck_status": "passed",
                "typecheck_message": progress,
            }
        )
        detail = render_record(passed)
        self.assertIn("Agda accepted the complete candidate file.", detail)
        self.assertNotIn("Checking imported-module", detail)

        failed = AgdaReviewRecord(
            **{
                **record.to_dict(),
                "typecheck_status": "failed",
                "typecheck_message": "proof does not have the required type",
            }
        )
        self.assertIn("proof does not have the required type", render_record(failed))

    def test_missing_code_uses_the_same_review_page_for_comments(self):
        record = AgdaReviewRecord(
            **{
                **self._record().to_dict(),
                "block_id": "missing-agda-section-8-1-example-definition-8.1.1",
                "provenance_kind": "missing",
                "project_code": "",
                "source_code": "",
                "source_commit": "",
                "conversion_status": "missing",
                "typecheck_status": "not-applicable",
            }
        )
        detail = render_record(record)
        index = render_index([record], missing_count=1)
        self.assertIn("Agda code missing", detail)
        self.assertIn("No candidate Agda code.", detail)
        self.assertIn("Add a shared comment", detail)
        self.assertNotIn("Run Agda check", detail)
        self.assertNotIn("Edit Rosetta Agda code", detail)
        self.assertNotIn(">Approve<", detail)
        self.assertIn(record.block_id, index)

        with tempfile.TemporaryDirectory() as directory, patch(
            "rosetta.agda_review.discover_agda_reviews", return_value=[record]
        ):
            root = Path(directory)
            (root / "data").mkdir()
            (root / "data" / "agda-reviews.json").write_text(
                '{\n  "version": 1,\n  "blocks": {}\n}\n'
            )
            update_agda_review(
                root, record.block_id, comment="No applicable match found.",
                comment_author="codex",
            )
            with self.assertRaisesRegex(ValueError, "cannot be approved"):
                update_agda_review(root, record.block_id, state="approved")

        with self.assertRaisesRegex(ValueError, "no candidate Agda code"):
            run_block_typecheck(Path("."), record.block_id, [record])

    def test_typecheck_button_action_runs_check(self):
        record = self._record()
        with tempfile.TemporaryDirectory() as directory, patch(
            "rosetta.review_web.run_typecheck", return_value={"status": "passed"}
        ) as run:
            result = run_block_typecheck(Path(directory), record.block_id, [record])
        self.assertEqual(result["status"], "passed")
        run.assert_called_once_with(Path(directory), record.destination)

    def test_changing_generated_file_makes_approval_stale(self):
        approved = self._record()
        store = {
            "version": 1,
            "blocks": {
                approved.block_id: {
                    "state": "approved",
                    "comments": [],
                    "review_sha256": _review_digest(approved),
                }
            },
        }
        changed = AgdaReviewRecord(
            **{**approved.to_dict(), "document_sha256": "changed-file-digest"}
        )
        self.assertEqual(_with_stored_review(changed, store).state, "stale")


if __name__ == "__main__":
    unittest.main()
