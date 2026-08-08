"""Safe discovery of active generated Rosetta files."""

from pathlib import Path
from typing import List

from .layout import rosetta_directory
from .file_registry import load_file_registry


def active_files(root: Path) -> List[Path]:
    directory = rosetta_directory(root)
    return sorted(
        (
            directory / name
            for name in set(load_file_registry(root).values())
            if (directory / name).is_file()
        ),
        key=lambda path: path.name,
    )


def active_file(root: Path, name: str) -> Path:
    if not name or Path(name).name != name or not name.endswith(".lagda.md"):
        raise ValueError("Invalid generated filename")
    path = rosetta_directory(root) / name
    if not path.is_file():
        raise ValueError(f"Generated Rosetta file not found: {name}")
    return path
