"""Read and patch maintained literate Agda without reconstructing documents."""

import hashlib
import re
from pathlib import Path

from .layout import rosetta_directory

AGDA_FENCE = re.compile(r"^([ \t]*)```agda[ \t]*\n(.*?)^\1```[ \t]*$", re.M | re.S)


def destination_path(root: Path, filename: str) -> Path:
    if Path(filename).name != filename or not filename.endswith(".lagda.md"):
        raise ValueError(f"Invalid Rosetta filename: {filename}")
    return rosetta_directory(root) / filename


def block_match(document: str, block_id: str):
    marker = f"<!-- rosetta-agda-block: {block_id} -->"
    if document.count(marker) != 1:
        raise ValueError(f"Expected one maintained block marker: {block_id}")
    position = document.index(marker) + len(marker)
    match = AGDA_FENCE.search(document, position)
    if match is None or document[position:match.start()].strip():
        raise ValueError(f"No Agda fence immediately follows {block_id}")
    return match


def replace_block(document: str, block_id: str, code: str) -> str:
    if re.search(r"^[ \t]*```", code, re.M):
        raise ValueError("Agda edits cannot contain Markdown fences")
    match = block_match(document, block_id)
    return document[:match.start(2)] + code.rstrip("\n") + "\n" + document[match.end(2):]


def dependency_digest(root: Path, filename: str) -> str:
    """Hash actual file bytes and transitive local imports."""
    digest = hashlib.sha256()
    visited = set()

    def visit(name):
        if name in visited:
            return
        visited.add(name)
        path = destination_path(root, name)
        digest.update(name.encode())
        if not path.is_file():
            digest.update(b"missing")
            return
        content = path.read_bytes()
        digest.update(content)
        for fence in AGDA_FENCE.finditer(content.decode()):
            for module in re.findall(r"^\s*(?:open\s+)?import\s+([\w.-]+)", fence.group(2), re.M):
                if not module.startswith("Agda."):
                    visit(module + ".lagda.md")

    visit(filename)
    return digest.hexdigest()
