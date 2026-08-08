"""Recoverable, conflict-aware edits for shared review data."""

import difflib
import hashlib
import os
import shutil
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


class EditConflict(RuntimeError):
    """The file changed after an editor loaded it."""


def text_digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class EditPreview:
    path: Path
    original_digest: str
    new_text: str
    diff: str


def preview_edit(path: Path, new_text: str) -> EditPreview:
    original = path.read_text()
    diff = "".join(
        difflib.unified_diff(
            original.splitlines(keepends=True),
            new_text.splitlines(keepends=True),
            fromfile=str(path),
            tofile=str(path),
        )
    )
    return EditPreview(path, text_digest(original), new_text, diff)


def _within(path: Path, root: Path) -> Path:
    resolved_root = root.resolve()
    resolved = path.resolve()
    try:
        return resolved.relative_to(resolved_root)
    except ValueError as error:
        raise ValueError(f"Refusing to edit a file outside {resolved_root}") from error


def apply_edit(preview: EditPreview, repository_root: Path) -> Path:
    """Apply a preview if it is current, returning the backup path.

    The caller is responsible for presenting ``preview.diff`` and receiving
    confirmation. This function enforces containment, conflict detection,
    backup creation, and atomic replacement.
    """

    relative = _within(preview.path, repository_root)
    current = preview.path.read_text()
    if text_digest(current) != preview.original_digest:
        raise EditConflict(
            f"{preview.path} changed after the edit was prepared; reload it and try again."
        )

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    backup = repository_root / ".rosetta-backups" / relative.parent
    backup.mkdir(parents=True, exist_ok=True)
    backup_path = backup / f"{relative.name}.{timestamp}.{preview.original_digest[:12]}"
    shutil.copy2(preview.path, backup_path)

    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{preview.path.name}.", dir=str(preview.path.parent)
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            handle.write(preview.new_text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, preview.path)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise
    return backup_path
