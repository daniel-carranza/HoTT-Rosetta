import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from rosetta.agda_typecheck import run_typecheck, typecheck_result


class AgdaTypecheckTests(unittest.TestCase):
    def test_result_is_cached_and_becomes_unchecked_after_change(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            staged = root / "_build" / "rosetta-typecheck" / "candidate-example.lagda.md"
            with patch(
                "rosetta.agda_typecheck.candidate_for_destination",
                return_value=("example.lagda.md", "first candidate"),
            ), patch(
                "rosetta.agda_typecheck.load_manifest", return_value=[]
            ), patch(
                "rosetta.agda_typecheck.typecheck_fingerprint", return_value="first"
            ), patch(
                "rosetta.agda_typecheck.typecheck_candidate",
                return_value=(0, "", staged),
            ):
                checked = run_typecheck(root, "section-1-1-example.lagda.md")
                self.assertEqual(checked["status"], "passed")
                self.assertEqual(
                    typecheck_result(root, "section-1-1-example.lagda.md")["status"],
                    "passed",
                )

            with patch(
                "rosetta.agda_typecheck.candidate_for_destination",
                return_value=("example.lagda.md", "changed candidate"),
            ), patch(
                "rosetta.agda_typecheck.load_manifest", return_value=[]
            ), patch(
                "rosetta.agda_typecheck.typecheck_fingerprint", return_value="changed"
            ):
                self.assertEqual(
                    typecheck_result(root, "section-1-1-example.lagda.md")["status"],
                    "not-checked",
                )

    def test_failure_message_is_saved(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            staged = root / "_build" / "rosetta-typecheck" / "candidate-example.lagda.md"
            with patch(
                "rosetta.agda_typecheck.candidate_for_destination",
                return_value=("example.lagda.md", "candidate"),
            ), patch(
                "rosetta.agda_typecheck.load_manifest", return_value=[]
            ), patch(
                "rosetta.agda_typecheck.typecheck_fingerprint", return_value="candidate"
            ), patch(
                "rosetta.agda_typecheck.typecheck_candidate",
                return_value=(1, "proof does not have the required type", staged),
            ):
                result = run_typecheck(root, "section-1-1-example.lagda.md")
            self.assertEqual(result["status"], "failed")
            self.assertIn("required type", result["message"])
