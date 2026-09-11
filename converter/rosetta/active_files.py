"""Safe discovery of maintained Rosetta files, including direct contributions."""

from pathlib import Path
from typing import List

from .layout import rosetta_directory


def active_files(root: Path) -> List[Path]:
    directory = rosetta_directory(root)
    return sorted(path for path in directory.glob("*.lagda.md") if path.is_file())


def active_file(root: Path, name: str) -> Path:
    if not name or Path(name).name != name or not name.endswith(".lagda.md"):
        raise ValueError("Invalid generated filename")
    path = rosetta_directory(root) / name
    if not path.is_file():
        raise ValueError(f"Generated Rosetta file not found: {name}")
    return path
