import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from rosetta import cli
from rosetta.agda_edit import apply_agda_block_edit, preview_agda_block_edit
from rosetta.agda_scratchpad import save_scratchpad, run_scratchpad_typecheck, promotion_scratchpad
from rosetta.agda_typecheck import candidate_for_destination, typecheck_fingerprint
from rosetta.generate import write_candidate, write_support_files
from tests import test_agda_edit


class PreservationTests(unittest.TestCase):
    def test_review_server_reads_current_files_without_regeneration(self):
        import threading
        from http.server import ThreadingHTTPServer
        from urllib.request import urlopen
        from rosetta.review_web import make_handler
        from rosetta.layout import rosetta_directory
        root = Path(__file__).resolve().parents[1]
        product = rosetta_directory(root)
        before = {p.name: p.read_bytes() for p in product.iterdir() if p.is_file() and not p.name.endswith(".agdai")}
        with patch("rosetta.generate.candidate_section", side_effect=AssertionError("review regenerated section")), \
             patch("rosetta.generate.candidate_exercise", side_effect=AssertionError("review regenerated exercise")):
            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(root, "test"))
            worker = threading.Thread(target=server.serve_forever, daemon=True)
            worker.start()
            try:
                base = f"http://127.0.0.1:{server.server_port}"
                with urlopen(base + "/read/exercise-2-3-exercise.lagda.md", timeout=30) as response:
                    self.assertEqual(response.status, 200)
                    self.assertIn("const", response.read().decode())
            finally:
                server.shutdown()
                server.server_close()
                worker.join()
        self.assertEqual(before, {p.name: p.read_bytes() for p in product.iterdir() if p.is_file() and not p.name.endswith(".agdai")})

    def test_generators_skip_existing_files_without_rendering(self):
        with tempfile.TemporaryDirectory() as directory:
            root, _ = test_agda_edit.AgdaEditTests()._root(directory)
            registry = {"section:1:1": "section-1-1-example.lagda.md",
                        "exercise:1:1": "exercise-1-1-example.lagda.md",
                        "chapter:1": "chapter-1-example.lagda.md"}
            (root / "data" / "rosetta-files.json").write_text(json.dumps({"format_version": 1, "files": registry}))
            support = root / "data" / "support-files"
            support.mkdir()
            (support / "universe-levels.lagda.md").write_text("old support")
            for name in list(registry.values()) + ["universe-levels.lagda.md"]:
                (root / "product" / name).write_text("Manual prose and Agda: " + name)
            before = {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in (root / "product").iterdir()}
            chapter = SimpleNamespace(number=1, subsections=["Example"], exercise_count=1)
            with patch.object(cli, "ROOT", root), patch.object(cli, "inventory", return_value=[chapter]), \
                 patch.object(cli, "candidate_section", side_effect=AssertionError("rendered existing section")), \
                 patch.object(cli, "candidate_exercise", side_effect=AssertionError("rendered existing exercise")), \
                 patch.object(cli, "candidate_chapter", side_effect=AssertionError("rendered existing chapter")):
                self.assertEqual(cli.command_convert(1, 1), 0)
                self.assertEqual(cli.command_candidate(1, 1), 0)
                self.assertEqual(cli.command_candidate_exercise(1, 1), 0)
                self.assertEqual(cli.command_candidate_chapter(1), 0)
            self.assertEqual(before, {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in (root / "product").iterdir()})
            with self.assertRaises(FileExistsError):
                write_candidate(root, registry["section:1:1"], "replacement")
            write_candidate(root, "new.lagda.md", "new content")
            self.assertEqual((root / "product" / "new.lagda.md").read_text(), "new content")

    def test_confirmation_rejects_intervening_file_edit(self):
        with tempfile.TemporaryDirectory() as directory:
            root, manifest = test_agda_edit.AgdaEditTests()._root(directory)
            edit = preview_agda_block_edit(root, "example-block", "changed", "Local change")
            path = root / "product" / edit.destination
            path.write_text(path.read_text() + "Another collaborator's correction\n")
            before = (path.read_bytes(), manifest.read_bytes())
            with self.assertRaisesRegex(ValueError, "read-only"):
                apply_agda_block_edit(root, "example-block", "changed", "Local change", edit.evidence_digest)
            self.assertEqual(before, (path.read_bytes(), manifest.read_bytes()))

    def test_checks_read_manual_edits_and_hash_transitive_dependencies(self):
        with tempfile.TemporaryDirectory() as directory:
            root, _ = test_agda_edit.AgdaEditTests()._root(directory)
            name = "section-1-1-example.lagda.md"
            path = root / "product" / name
            path.write_text(path.read_text().replace("where\n", "where\nopen import helper\n"))
            helper = root / "product" / "helper.lagda.md"
            helper.write_text("```agda\nmodule helper where\nopen import leaf\n```\n")
            leaf = root / "product" / "leaf.lagda.md"
            leaf.write_text("```agda\nmodule leaf where\n```\n")
            self.assertEqual(candidate_for_destination(root, name)[1], path.read_text())
            before = typecheck_fingerprint(root, name)
            leaf.write_text(leaf.read_text() + "Edited leaf\n")
            self.assertNotEqual(before, typecheck_fingerprint(root, name))

    def test_passing_draft_becomes_stale_after_manual_change(self):
        with tempfile.TemporaryDirectory() as directory:
            root, _ = test_agda_edit.AgdaEditTests()._root(directory)
            save_scratchpad(root, "example-block", "changed", "Local change")
            with patch("rosetta.agda_scratchpad.typecheck_candidate", return_value=(0, "", root / "draft")) as check:
                run_scratchpad_typecheck(root, "example-block")
            document = check.call_args.args[2]
            self.assertIn("Manually improved ending.", document)
            self.assertIn("changed", document)
            path = root / "product" / "section-1-1-example.lagda.md"
            path.write_text(path.read_text() + "Manual correction\n")
            with self.assertRaisesRegex(ValueError, "changed after"):
                promotion_scratchpad(root, "example-block")

    def test_editor_rejects_stale_browser_content(self):
        with tempfile.TemporaryDirectory() as directory:
            root, _ = test_agda_edit.AgdaEditTests()._root(directory)
            with self.assertRaisesRegex(ValueError, "editor was opened"):
                save_scratchpad(root, "example-block", "changed", expected_document_digest="old")

    def test_ordinary_checks_do_not_load_review_metadata(self):
        with patch("rosetta.diagnostics.discover_agda_reviews", side_effect=AssertionError("review loaded")), \
             patch("rosetta.diagnostics.discover_diagram_reviews", side_effect=AssertionError("review loaded")):
            self.assertEqual(cli.command_check(), 0)
