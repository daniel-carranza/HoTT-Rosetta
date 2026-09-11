import io
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch
from urllib.parse import urlencode

from tests import test_agda_review
from tests import test_review
from rosetta.agda_review import update_agda_review, load_agda_review_store, _with_stored_review, _review_digest
from rosetta.editing import EditConflict
from rosetta.review_sync import (
    git, merge_stores, merge_pending, resolve_pending, review_conflicts,
    require_review_branch, sync_status,
)
from rosetta.review_web import STYLE, make_handler, render_review_sharing
from rosetta.review import discover_diagram_reviews, update_diagram_review, load_review_store, _stored_item


def store(state="pending", digest="first", comments=None):
    return {"version": 1, "blocks": {"block": {
        "state": state, "review_sha256": digest, "comments": comments or [],
    }}}


class ReviewSyncTests(unittest.TestCase):
    def _repository(self, directory):
        root = Path(directory)
        git(root, "init", "-b", "main")
        git(root, "config", "user.name", "Test Reviewer")
        git(root, "config", "user.email", "review@example.test")
        git(root, "remote", "add", "fork", "https://github.com/daniel-carranza/HoTT-Rosetta.git")
        (root / "data").mkdir()
        (root / "data/agda-reviews.json").write_text(json.dumps(store()))
        (root / ".gitattributes").write_text("data/agda-reviews.json merge=binary\n")
        git(root, "add", ".")
        git(root, "commit", "-m", "Initial reviews")
        git(root, "update-ref", "refs/remotes/fork/main", "HEAD")
        return root

    def _diverge(self, root, ours, theirs):
        git(root, "switch", "-c", "other-reviewer")
        (root / "data/agda-reviews.json").write_text(json.dumps(theirs))
        git(root, "commit", "-am", "Other reviews")
        git(root, "switch", "main")
        (root / "data/agda-reviews.json").write_text(json.dumps(ours))
        git(root, "commit", "-am", "Our reviews")
        result = git(root, "merge", "--no-edit", "other-reviewer", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(sync_status(root)["unmerged"])

    def test_comment_does_not_reapprove_changed_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            record = test_agda_review.AgdaReviewTests()._record()
            update_agda_review(root, record.block_id, state="approved", current_record=record)
            changed = replace(record, document_sha256="changed")
            update_agda_review(root, record.block_id, comment="Only a comment", current_record=changed)
            saved = load_agda_review_store(root / "data/agda-reviews.json")
            self.assertEqual(_with_stored_review(changed, saved).state, "stale")
            update_agda_review(root, record.block_id, state="approved", current_record=changed)
            self.assertEqual(_with_stored_review(changed, load_agda_review_store(root / "data/agda-reviews.json")).state, "approved")

    def test_diagram_comment_does_not_refresh_approval_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            key = test_review.ReviewTests()._review_repository(root, r"\begin{tikzcd} A \arrow[r] & B \end{tikzcd}")
            update_diagram_review(root, key, state="approved")
            item = discover_diagram_reviews(root)[0].item
            changed = replace(item, source=item.source + " changed")
            with patch("rosetta.review.discover_diagram_reviews", return_value=[SimpleNamespace(item=changed)]):
                update_diagram_review(root, key, comment="Only a comment")
            saved = load_review_store(root / "data/diagram-reviews.json")
            self.assertEqual(_stored_item(changed, saved).state, "stale")

    def test_stale_browser_decision_cannot_approve_unseen_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            original = test_agda_review.AgdaReviewTests()._record()
            changed = replace(original, document_sha256="unseen change")
            with self.assertRaises(EditConflict):
                update_agda_review(root, original.block_id, state="approved", current_record=changed,
                                   expected_review_digest=_review_digest(original))
            self.assertFalse((root / "data/agda-reviews.json").exists())

    def test_both_comments_survive_and_decision_evidence_stays_atomic(self):
        base = store()
        ours = store("approved", "old-evidence", [{"id": "a", "author": "A", "text": "same"}])
        theirs = store("rejected", "new-evidence", [{"id": "b", "author": "B", "text": "same"}])
        merged, conflicts = merge_stores(base, ours, theirs, "blocks")
        record = merged["blocks"]["block"]
        self.assertEqual(conflicts, ["block"])
        self.assertEqual(record["state"], "pending")
        self.assertNotIn("review_sha256", record)
        self.assertEqual(len(record["comments"]), 2)
        self.assertEqual(record["decision_conflict"]["ours"]["review_sha256"], "old-evidence")

    def test_comment_only_change_does_not_conflict_with_new_decision(self):
        base = store("approved")
        ours = store("approved", comments=["new comment"])
        theirs = store("rejected")
        merged, conflicts = merge_stores(base, ours, theirs, "blocks")
        self.assertFalse(conflicts)
        self.assertEqual(merged["blocks"]["block"]["state"], "rejected")
        self.assertEqual(merged["blocks"]["block"]["comments"], ["new comment"])

    def test_new_comment_ids_deduplicate_shared_events_but_not_independent_comments(self):
        common = {"id": "shared", "author": "A", "text": "same"}
        extra = {"id": "independent", "author": "A", "text": "same"}
        merged, _ = merge_stores(store(), store(comments=[common]), store(comments=[common, extra]), "blocks")
        self.assertEqual(len(merged["blocks"]["block"]["comments"]), 2)

    def test_diagram_merge_keeps_both_comments_and_preserves_approval_evidence(self):
        def diagram(state, fingerprint, comments):
            return {"version": 1, "diagrams": {"d": {"state": state, "source_sha256": fingerprint, "comments": comments}}}
        merged, conflicts = merge_stores(diagram("pending", "old", []),
            diagram("approved", "old", ["same"]), diagram("approved", "new", ["same"]), "diagrams")
        self.assertEqual(conflicts, ["d"])
        self.assertEqual(merged["diagrams"]["d"]["comments"], ["same", "same"])

    def test_record_deletion_does_not_drop_comments(self):
        base = store(comments=["Keep this history"])
        merged, _ = merge_stores(base, {"version": 1, "blocks": {}}, base, "blocks")
        self.assertEqual(merged["blocks"]["block"]["comments"], ["Keep this history"])

    def test_real_git_merge_preserves_independent_comments_and_stages_only_reviews(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._repository(directory)
            self._diverge(root, store(comments=["ours"]), store(comments=["theirs"]))
            (root / "unrelated.txt").write_text("Do not stage me")
            self.assertEqual(merge_pending(root, "agda"), [])
            self.assertEqual(git(root, "diff", "--name-only", "--cached").stdout.strip(), "data/agda-reviews.json")
            saved = load_agda_review_store(root / "data/agda-reviews.json")
            self.assertCountEqual(saved["blocks"]["block"]["comments"], ["ours", "theirs"])
            self.assertFalse(sync_status(root)["unmerged"])

    def test_real_git_conflict_is_visible_and_resolvable_without_json_editing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._repository(directory)
            self._diverge(root, store("approved", comments=["ours"]), store("rejected", comments=["theirs"]))
            self.assertEqual(merge_pending(root, "agda"), ["block"])
            self.assertIn("agda:block", review_conflicts(root))
            self.assertTrue(sync_status(root)["unmerged"])
            with self.assertRaises(ValueError):
                require_review_branch(root)
            self.assertEqual(resolve_pending(root, "agda", "block", "theirs"), [])
            saved = load_agda_review_store(root / "data/agda-reviews.json")["blocks"]["block"]
            self.assertEqual(saved["state"], "rejected")
            self.assertCountEqual(saved["comments"], ["ours", "theirs"])
            self.assertFalse(review_conflicts(root))
            self.assertFalse(sync_status(root)["unmerged"])

    def test_merge_refuses_intervening_working_file_change(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._repository(directory)
            self._diverge(root, store(comments=["ours"]), store(comments=["theirs"]))
            path = root / "data/agda-reviews.json"
            manual = store(comments=["ours", "concurrent work"])
            path.write_text(json.dumps(manual))
            with self.assertRaises(EditConflict):
                merge_pending(root, "agda")
            self.assertEqual(json.loads(path.read_text()), manual)

    def test_status_reports_dirty_unpushed_incoming_and_detached(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._repository(directory)
            self.assertTrue(sync_status(root)["writable"])
            path = root / "data/agda-reviews.json"
            path.write_text(json.dumps(store(comments=["local"])))
            self.assertEqual(sync_status(root)["dirty_reviews"], ["data/agda-reviews.json"])
            git(root, "commit", "-am", "Local reviews")
            status = sync_status(root)
            self.assertEqual((status["ahead"], status["behind"], status["unpushed_review_commits"]), (1, 0, 1))
            git(root, "switch", "--detach", "HEAD~1")
            git(root, "update-ref", "refs/remotes/fork/main", "main")
            self.assertEqual(sync_status(root)["behind"], 1)
            with self.assertRaisesRegex(ValueError, "detached tags"):
                require_review_branch(root)

    def test_explicit_fetch_only_updates_remote_reference_not_working_files(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as remote_directory:
            root = self._repository(directory)
            git(root, "clone", "--bare", str(root), remote_directory)
            git(root, "remote", "set-url", "fork", remote_directory)
            path = root / "data/agda-reviews.json"
            path.write_text(json.dumps(store(comments=["Uncommitted work"])))
            before = path.read_bytes()
            with patch("rosetta.review_sync.canonical_remote", return_value="fork"):
                status = sync_status(root, fetch=True)
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(status["dirty_reviews"], ["data/agda-reviews.json"])

    def test_retired_branch_and_detached_metadata_writes_are_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._repository(directory)
            record = test_agda_review.AgdaReviewTests()._record()
            for target in ("archive/example", "proposal/agda-exercise-solutions"):
                git(root, "switch", "-c", target)
                before = (root / "data/agda-reviews.json").read_bytes()
                with self.assertRaisesRegex(ValueError, "development main"):
                    update_agda_review(root, record.block_id, comment="not here", current_record=record)
                self.assertEqual((root / "data/agda-reviews.json").read_bytes(), before)

    def test_http_writer_guard_blocks_detached_or_unversioned_checkout(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch("rosetta.review_web.threading.Thread.start"):
                cls = make_handler(root, "token")
            handler = cls.__new__(cls)
            body = urlencode({"token": "token", "comment": "Keep my text"}).encode()
            handler.path = "/agda/example"
            handler.headers = {"Content-Length": str(len(body))}
            handler.rfile = io.BytesIO(body)
            handler._send = Mock()
            handler.do_POST()
            self.assertEqual(handler._send.call_args.args[0], 400)
            self.assertIn("Keep my text", handler._send.call_args.args[1])

    def test_clean_html_responses_show_only_muted_sharing_tip_without_network(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._repository(directory)
            with patch("rosetta.review_web.threading.Thread.start"):
                cls = make_handler(root, "token")
            handler = cls.__new__(cls)
            handler.send_response = Mock()
            handler.send_header = Mock()
            handler.end_headers = Mock()
            handler.wfile = io.BytesIO()
            with patch("rosetta.review_sync.git", wraps=git) as commands:
                handler._send(200, "<html><main>Page</main></html>")
            self.assertFalse(any("fetch" in call.args for call in commands.call_args_list))
            page = handler.wfile.getvalue().decode()
            self.assertNotIn("review-sharing-status", page)
            self.assertNotIn("Branch:", page)
            self.assertNotIn("Unpushed", page)
            self.assertNotIn("/sync-refresh", page)
            self.assertNotIn("Shared reviews belong to development main", page)
            self.assertIn("class='review-sharing-tip'", page)
            self.assertIn(".review-sharing-tip { color: #6b7075;", STYLE)
            self.assertIn("https://github.com/daniel-carranza/HoTT-Rosetta/blob/main/data/agda-reviews.json", page)
            self.assertIn('on the "main" branch. Remember to pull frequently!', page)
            self.assertIn("saved <em>locally</em> in the file <code>data/agda-reviews.json</code>", page)
            self.assertIn('"main" branch of daniel-carranza/HoTT-Rosetta', page)

    def test_sharing_notice_shows_only_actionable_counts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._repository(directory)
            clean = sync_status(root)
            scenarios = [
                ({"dirty_reviews": ["data/agda-reviews.json"]}, "Uncommitted review files: 1"),
                ({"ahead": 1}, "Unpushed commits: 1"),
                ({"ahead": 2, "unpushed_review_commits": 1}, "Unpushed review commits: 1"),
                ({"behind": 3}, "Incoming commits: 3"),
                ({"ahead": None, "behind": None, "unpushed_review_commits": None}, "Remote status is unknown"),
                ({"writable": False, "branch": "topic", "reason": "Review writes are blocked"}, "Review writes are blocked"),
            ]
            for changes, expected in scenarios:
                with self.subTest(changes=changes):
                    page = render_review_sharing({**clean, **changes}, "token")
                    self.assertIn("review-sharing-status", page)
                    self.assertIn(expected, page)
                    self.assertIn("/sync-refresh", page)
                    self.assertIn("Remote counts reflect the last fetch", page)
                    self.assertNotIn("Unpushed commits: 0", page)
                    self.assertNotIn("Unpushed review commits: 0", page)
                    self.assertNotIn("Uncommitted review files: 0", page)
                    self.assertNotIn("Incoming commits: 0", page)
                    self.assertNotIn("None", page)
                    self.assertNotIn("Shared reviews belong to development main", page)
                    self.assertIn("review-sharing-tip", page)

    def test_sharing_notice_escapes_git_details_and_hides_unavailable_fetch(self):
        with tempfile.TemporaryDirectory() as directory:
            sharing = sync_status(Path(directory))
            sharing.update(branch="<branch>", reason="<problem>")
            page = render_review_sharing(sharing, "token")
            self.assertIn("review-sharing-status", page)
            self.assertIn("&lt;branch&gt;", page)
            self.assertIn("&lt;problem&gt;", page)
            self.assertNotIn("/sync-refresh", page)


if __name__ == "__main__":
    unittest.main()
