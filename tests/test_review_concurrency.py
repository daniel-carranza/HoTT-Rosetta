"""Regression coverage for lost updates, without requiring loopback access."""

import hashlib
import io
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch
from urllib.parse import urlencode

from tests import test_agda_edit, test_agda_review
from rosetta import editing
from rosetta.agda_review import update_agda_review, load_agda_review_store
from rosetta.agda_scratchpad import (
    discard_scratchpad, draft_revision, load_scratchpad,
    run_scratchpad_typecheck, save_scratchpad,
)
from rosetta.review import update_diagram_review, load_review_store
from rosetta.review_web import make_handler, render_agda_editor


class ReviewConcurrencyTests(unittest.TestCase):
    def test_review_writer_refuses_rosetta_even_with_a_current_preview(self):
        with tempfile.TemporaryDirectory() as directory:
            root, _ = test_agda_edit.AgdaEditTests()._root(directory)
            path = root / "product/section-1-1-example.lagda.md"
            original = path.read_bytes()
            preview = editing.preview_edit(path, "erase all collaborator work")
            with patch("rosetta.editing.os.replace") as replace_file:
                with self.assertRaisesRegex(ValueError, "restricted to review metadata"):
                    editing.apply_edit(preview, root)
            replace_file.assert_not_called()
            self.assertEqual(path.read_bytes(), original)

    def test_review_writer_refuses_metadata_alias_into_rosetta(self):
        with tempfile.TemporaryDirectory() as directory:
            root, _ = test_agda_edit.AgdaEditTests()._root(directory)
            target = root / "product/section-1-1-example.lagda.md"
            alias = root / "data/agda-reviews.json"
            alias.symlink_to(target)
            original = target.read_bytes()
            with self.assertRaises(ValueError):
                editing.apply_edit(editing.preview_edit(alias, "lost"), root)
            self.assertEqual(target.read_bytes(), original)

    def test_simultaneous_agda_comments_preserve_every_comment_and_decision(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            record = test_agda_review.AgdaReviewTests()._record()
            update_agda_review(root, record.block_id, state="approved", current_record=record)

            def comment(number):
                update_agda_review(root, record.block_id, comment=str(number), current_record=record)

            with ThreadPoolExecutor(max_workers=8) as workers:
                list(workers.map(comment, range(32)))
            saved = load_agda_review_store(root / "data/agda-reviews.json")["blocks"][record.block_id]
            self.assertEqual(saved["state"], "approved")
            self.assertCountEqual([c["text"] for c in saved["comments"]], map(str, range(32)))

    def test_simultaneous_diagram_comments_preserve_every_comment(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            record = SimpleNamespace(item=SimpleNamespace(stable_id="diagram", source="source", state="pending"))
            with patch("rosetta.review.discover_diagram_reviews", return_value=[record]):
                with ThreadPoolExecutor(max_workers=8) as workers:
                    list(workers.map(lambda n: update_diagram_review(root, "diagram", comment=str(n)), range(24)))
            saved = load_review_store(root / "data/diagram-reviews.json")["diagrams"]["diagram"]
            self.assertCountEqual(saved["comments"], map(str, range(24)))

    def test_separate_processes_share_transaction_lock_including_first_creation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            script = """
import sys
from pathlib import Path
import tests
from rosetta.editing import update_json_store
root = Path(sys.argv[1])
for n in range(12):
    def update(store):
        store['blocks'][sys.argv[2] + '-' + str(n)] = n
    update_json_store(root / 'data/agda-reviews.json', root, 'blocks', update)
"""
            processes = [subprocess.Popen([sys.executable, "-c", script, directory, str(n)],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         cwd=Path(__file__).resolve().parents[1]) for n in range(4)]
            try:
                for process in processes:
                    _, errors = process.communicate(timeout=20)
                    self.assertEqual(process.returncode, 0, errors.decode())
            finally:
                for process in processes:
                    if process.poll() is None:
                        process.kill()
                        process.wait()
            self.assertEqual(len(load_agda_review_store(root / "data/agda-reviews.json")["blocks"]), 48)

    def test_intervening_external_metadata_change_is_not_used_as_new_base(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "data/agda-reviews.json"
            editing.update_json_store(path, root, "blocks", lambda store: None)
            original_apply = editing._apply_edit_locked
            collaborator = '{"version": 1, "blocks": {"collaborator": {}}}'

            def interleaved(preview, repository):
                path.write_text(collaborator)
                return original_apply(preview, repository)

            with patch.object(editing, "_apply_edit_locked", side_effect=interleaved):
                with self.assertRaises(editing.EditConflict):
                    editing.update_json_store(path, root, "blocks", lambda store: store["blocks"].update(ours={}))
            self.assertEqual(path.read_text(), collaborator)

    def test_stale_tabs_cannot_save_or_discard_newer_draft(self):
        with tempfile.TemporaryDirectory() as directory:
            root, _ = test_agda_edit.AgdaEditTests()._root(directory)
            first = save_scratchpad(root, "example-block", "first")
            second = save_scratchpad(root, "example-block", "second", expected_draft_revision=draft_revision(first))
            with self.assertRaises(editing.EditConflict):
                save_scratchpad(root, "example-block", "stale", expected_draft_revision=draft_revision(first))
            with self.assertRaises(editing.EditConflict):
                discard_scratchpad(root, "example-block", draft_revision(first))
            self.assertEqual(load_scratchpad(root, "example-block"), second)

    def test_finishing_typecheck_cannot_restore_a_superseded_or_discarded_draft(self):
        for discard in (False, True):
            with self.subTest(discard=discard), tempfile.TemporaryDirectory() as directory:
                root, _ = test_agda_edit.AgdaEditTests()._root(directory)
                first = save_scratchpad(root, "example-block", "first")

                def while_checking(*args):
                    if discard:
                        discard_scratchpad(root, "example-block", draft_revision(first))
                    else:
                        save_scratchpad(root, "example-block", "second", expected_draft_revision=draft_revision(first))
                    return 0, "", root / "temporary"

                with patch("rosetta.agda_scratchpad.typecheck_candidate", side_effect=while_checking):
                    with self.assertRaises(editing.EditConflict):
                        run_scratchpad_typecheck(root, "example-block", draft_revision(first))
                saved = load_scratchpad(root, "example-block")
                if discard:
                    self.assertIsNone(saved)
                else:
                    self.assertEqual(saved.code, "second")
                    self.assertEqual(saved.status, "not-checked")

    def _post(self, root, action, form):
        # Exercise the real handler without opening a socket in the sandbox.
        with patch("rosetta.review_web.threading.Thread.start"):
            handler_class = make_handler(root, "test-token")
        handler = handler_class.__new__(handler_class)
        body = urlencode({"token": "test-token", **form}).encode()
        handler.path = "/agda/example-block/" + action
        handler.headers = {"Content-Length": str(len(body))}
        handler.rfile = io.BytesIO(body)
        handler._send = Mock()
        handler._redirect = Mock()
        with patch("rosetta.review_web.require_review_branch"):
            handler.do_POST()
        return handler

    def test_old_confirmation_post_cannot_write_any_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root, _ = test_agda_edit.AgdaEditTests()._root(directory)
            before = {str(p): p.read_bytes() for p in root.rglob("*") if p.is_file()}
            handler = self._post(root, "edit-confirm", {"code": "overwrite"})
            self.assertEqual(handler._send.call_args.args[0], 410)
            self.assertEqual(before, {str(p): p.read_bytes() for p in root.rglob("*") if p.is_file()})

    def test_stale_draft_post_returns_conflict_and_retains_submitted_text(self):
        with tempfile.TemporaryDirectory() as directory:
            root, _ = test_agda_edit.AgdaEditTests()._root(directory)
            document = root / "product/section-1-1-example.lagda.md"
            first = save_scratchpad(root, "example-block", "newer draft")
            handler = self._post(root, "scratch-save", {
                "code": "keep my <draft>", "draft_revision": "missing",
                "document_digest": hashlib.sha256(document.read_bytes()).hexdigest(),
            })
            status, body = handler._send.call_args.args
            self.assertEqual(status, 409)
            self.assertIn("keep my &lt;draft&gt;", body)
            self.assertEqual(load_scratchpad(root, "example-block"), first)

    def test_all_draft_action_forms_carry_the_revision(self):
        with tempfile.TemporaryDirectory() as directory:
            root, _ = test_agda_edit.AgdaEditTests()._root(directory)
            draft = save_scratchpad(root, "example-block", "code")
            record = test_agda_review.AgdaReviewTests()._record()
            page = render_agda_editor(record, "token", draft)
            self.assertEqual(page.count("name='draft_revision'"), 4)
            self.assertEqual(page.count(draft_revision(draft)), 4)

    def test_old_draft_forms_fail_closed_and_preserve_submitted_note(self):
        with tempfile.TemporaryDirectory() as directory:
            root, _ = test_agda_edit.AgdaEditTests()._root(directory)
            handler = self._post(root, "scratch-save", {"code": "draft", "adaptation_note": "important note"})
            status, body = handler._send.call_args.args
            self.assertEqual(status, 409)
            self.assertIn("important note", body)
            self.assertIsNone(load_scratchpad(root, "example-block"))


if __name__ == "__main__":
    unittest.main()
