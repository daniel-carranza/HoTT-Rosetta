"""Recoverable, conflict-aware edits for shared review data."""

import difflib
import hashlib
import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from contextlib import contextmanager
from typing import Optional

from .layout import rosetta_directory


class EditConflict(RuntimeError):
    """The file changed after an editor loaded it."""


def text_digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class EditPreview:
    path: Path
    original_digest: Optional[str]
    new_text: str
    diff: str


def preview_edit(path: Path, new_text: str, *, original: str = None) -> EditPreview:
    original = path.read_text() if original is None else original
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


def _metadata_path(path: Path, root: Path) -> Path:
    relative = _within(path, root)
    allowed = {
        Path("data/agda-reviews.json"),
        Path("data/diagram-reviews.json"),
        Path("_build/rosetta-review/agda-scratchpads.json"),
        Path("_build/rosetta-review/agda-typechecks.json"),
    }
    if relative not in allowed:
        raise ValueError("Review writes are restricted to review metadata; edit Rosetta files in your editor")
    if (root / "data/project-layout.json").exists():
        product = rosetta_directory(root).resolve()
        if product == path.resolve() or product in path.resolve().parents:
            raise ValueError("Review cannot write inside the maintained Rosetta")
    return relative


@contextmanager
def _metadata_lock(path: Path, root: Path):
    """Serialize whole transactions across threads and review/CLI processes.

    A stable sidecar is locked, never the inode replaced by the transaction.
    Independent text editors do not participate; this is for metadata only.
    """
    _metadata_path(path, root)
    try:
        import fcntl
    except ImportError as error:
        raise RuntimeError("Review metadata writes require POSIX file locking") from error
    directory = root / "_build/rosetta-review/locks"
    directory.mkdir(parents=True, exist_ok=True)
    name = text_digest(str(path.resolve()))
    with (directory / (name + ".lock")).open("a+b") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _read_optional(path: Path):
    try:
        return path.read_text()
    except FileNotFoundError:
        return None


def update_json_store(path: Path, root: Path, collection: str, update):
    """Read, modify, and atomically save one metadata snapshot under one lock."""
    with _metadata_lock(path, root):
        original = _read_optional(path)
        store = json.loads(original) if original is not None else {"version": 1, collection: {}}
        if store.get("version") != 1 or not isinstance(store.get(collection), dict):
            raise ValueError(f"Invalid review data: {path}")
        update(store)
        new_text = json.dumps(store, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
        if new_text != original:
            preview = EditPreview(path, text_digest(original) if original is not None else None, new_text, "")
            _apply_edit_locked(preview, root)
        return store


def apply_edit(preview: EditPreview, repository_root: Path) -> Path:
    """Apply an existing metadata preview under the shared transaction lock."""
    with _metadata_lock(preview.path, repository_root):
        return _apply_edit_locked(preview, repository_root)


def _apply_edit_locked(preview: EditPreview, repository_root: Path):
    """Apply a preview if it is current, returning the backup path.

    The caller is responsible for presenting ``preview.diff`` and receiving
    confirmation. This function enforces containment, conflict detection,
    backup creation, and atomic replacement.
    """

    relative = _metadata_path(preview.path, repository_root)
    current = _read_optional(preview.path)
    if (text_digest(current) if current is not None else None) != preview.original_digest:
        raise EditConflict(
            f"{preview.path} changed after the edit was prepared; reload it and try again."
        )

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    backup = repository_root / ".rosetta-backups" / relative.parent
    backup.mkdir(parents=True, exist_ok=True)
    backup_path = None
    if current is not None:
        backup_path = backup / f"{relative.name}.{timestamp}.{preview.original_digest[:12]}"
        shutil.copy2(preview.path, backup_path)

    preview.path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{preview.path.name}.", dir=str(preview.path.parent)
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            handle.write(preview.new_text)
            handle.flush()
            os.fsync(handle.fileno())
        latest = _read_optional(preview.path)
        if (text_digest(latest) if latest is not None else None) != preview.original_digest:
            raise EditConflict(f"{preview.path} changed while the edit was being saved")
        if preview.original_digest is None:
            # Publish a complete first snapshot without clobbering a new file.
            os.link(temporary_name, preview.path)
            os.unlink(temporary_name)
        else:
            os.chmod(temporary_name, preview.path.stat().st_mode & 0o777)
            os.replace(temporary_name, preview.path)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise
    return backup_path
