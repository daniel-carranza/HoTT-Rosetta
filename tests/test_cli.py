import unittest
from unittest.mock import patch

from rosetta.cli import command_typecheck_all


class AggregateTypecheckTests(unittest.TestCase):
    def test_typecheck_all_checks_registered_chapters_in_order(self):
        with patch("rosetta.cli.shutil.which", return_value="/usr/bin/agda"), patch(
            "rosetta.cli.agda_typecheck_options", return_value=["--no-libraries"]
        ), patch(
            "rosetta.cli.subprocess.run"
        ) as run:
            run.return_value.returncode = 0
            self.assertEqual(command_typecheck_all(1, 2), 0)
        self.assertEqual(run.call_count, 2)
        self.assertIn("chapter-1-", str(run.call_args_list[0].args[0][-1]))
        self.assertIn("chapter-2-", str(run.call_args_list[1].args[0][-1]))

    def test_typecheck_all_rejects_invalid_range(self):
        self.assertEqual(command_typecheck_all(0, 2), 2)


if __name__ == "__main__":
    unittest.main()
