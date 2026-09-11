"""Compare shared content in Git revisions without touching any files."""

import json
import subprocess
from pathlib import Path


def git(root: Path, *arguments: str) -> str:
    return subprocess.run(["git", *arguments], cwd=root, check=True, text=True,
                          capture_output=True).stdout


def content_tree(root: Path, revision: str, directory: str) -> tuple[dict, list]:
    commit = git(root, "rev-parse", "--verify", revision + "^{commit}").strip()
    files = git(root, "ls-tree", "-r", "-z", commit).split("\0")
    content, development = {}, []
    for entry in files:
        if not entry:
            continue
        metadata, path = entry.split("\t", 1)
        mode, kind, digest = metadata.split()
        if path.startswith(directory + "/") or path.startswith("latex-book/") or path in {"README.md", "BENCHMARK.md"}:
            content[path] = (mode, digest)
        elif path.startswith("book/"):
            content["latex-book/" + path.removeprefix("book/")] = (mode, digest)
        else:
            development.append(path)
    return content, development


def compare_content(root: Path, source: str, target: str, public: bool = False) -> list[str]:
    layout = json.loads(git(root, "show", source + ":data/project-layout.json"))
    directory = layout["rosetta_directory"]
    left, _ = content_tree(root, source, directory)
    right, development = content_tree(root, target, directory)
    differences = []
    for name in sorted(left.keys() | right.keys()):
        if left.get(name) != right.get(name):
            state = "missing from target" if name not in right else "only in target" if name not in left else "different"
            differences.append(f"{state}: {name}")
    if public:
        differences.extend(f"development-only file in public tree: {name}" for name in development)
    return differences
