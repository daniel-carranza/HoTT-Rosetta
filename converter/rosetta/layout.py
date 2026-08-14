"""Central project layout used by every active Rosetta workflow."""

import json
from pathlib import Path


def rosetta_directory(root: Path) -> Path:
    """Return the configured active Rosetta directory."""

    path = root / "data" / "project-layout.json"
    value = json.loads(path.read_text())
    if value.get("format_version") != 1:
        raise ValueError("Project layout must have format_version 1")
    configured = value.get("rosetta_directory")
    if not isinstance(configured, str) or not configured.strip():
        raise ValueError("Project layout needs a nonempty rosetta_directory")
    relative = Path(configured)
    if relative.is_absolute() or ".." in relative.parts or relative == Path("."):
        raise ValueError("rosetta_directory must be a safe repository-relative path")
    return root / relative
