"""Stable filenames for generated Rosetta documents."""

import json
from pathlib import Path


def load_file_registry(root: Path) -> dict:
    path = root / "data" / "rosetta-files.json"
    value = json.loads(path.read_text())
    files = value.get("files")
    if value.get("format_version") != 1 or not isinstance(files, dict):
        raise ValueError("Rosetta filename data must have format_version 1 and files")
    for key, name in files.items():
        if (
            not isinstance(key, str)
            or not isinstance(name, str)
            or Path(name).name != name
            or not name.endswith(".lagda.md")
        ):
            raise ValueError(f"Invalid Rosetta filename record: {key!r}")
    return files


def registered_filename(root: Path, kind: str, *numbers: int) -> str:
    key = ":".join((kind, *(str(number) for number in numbers)))
    try:
        return load_file_registry(root)[key]
    except KeyError as error:
        raise ValueError(f"No registered Rosetta filename for {key}") from error
