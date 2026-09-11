import unittest
from pathlib import Path
from unittest.mock import patch

from rosetta.publication import content_tree, compare_content


class PublicationTests(unittest.TestCase):
    def test_public_content_allowlist_and_latex_rename(self):
        entries = [
            "100644 blob a\tproduct/section.lagda.md",
            "100644 blob b\tbook/hott.tex",
            "100644 blob c\tREADME.md",
            "100644 blob d\tBENCHMARK.md",
            "100644 blob e\tdocs/README.md",
            "100644 blob f\tAGENTS.md",
            "100644 blob g\tdata/project-layout.json",
        ]
        with patch("rosetta.publication.git", side_effect=["commit\n", "\0".join(entries)]):
            content, dev = content_tree(Path("."), "release", "product")
        self.assertEqual(set(content), {"product/section.lagda.md", "latex-book/hott.tex", "README.md", "BENCHMARK.md"})
        self.assertEqual(dev, ["docs/README.md", "AGENTS.md", "data/project-layout.json"])

    def test_differences_and_public_layout_are_reported_without_writes(self):
        with patch("rosetta.publication.git", return_value='{"rosetta_directory":"product"}'), \
             patch("rosetta.publication.content_tree", side_effect=[
                 ({"README.md": ("100644", "new"), "BENCHMARK.md": ("100644", "bench")}, []),
                 ({"README.md": ("100644", "old")}, ["docs/development.md"]),
             ]):
            result = compare_content(Path("."), "main", "release", public=True)
        self.assertEqual(result, ["missing from target: BENCHMARK.md", "different: README.md",
                                  "development-only file in public tree: docs/development.md"])
