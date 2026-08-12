"""Safe edits of curated Agda blocks from the local review program."""

import json
from dataclasses import dataclass
from pathlib import Path

from .agda_manifest import source_digest
from .agda_typecheck import candidate_for_destination
from .editing import EditConflict, EditPreview, apply_edit, preview_edit
from .generate import write_candidate


@dataclass(frozen=True)
class AgdaBlockEdit:
    preview: EditPreview
    destination: str
    provenance_kind: str


def _manifest_values(path: Path, seen=None):
    seen = set() if seen is None else seen
    resolved = path.resolve()
    if resolved in seen:
        raise ValueError(f"Agda manifest include cycle: {path}")
    seen.add(resolved)
    value = json.loads(path.read_text())
    if value.get("format_version") != 1 or not isinstance(value.get("blocks"), list):
        raise ValueError(f"Invalid Agda manifest: {path}")
    yield path, value
    for name in value.get("includes", []):
        yield from _manifest_values(path.parent / name, seen)
    seen.remove(resolved)


def _find_block(root: Path, block_id: str):
    manifest = root / "data" / "agda-blocks.json"
    for path, value in _manifest_values(manifest):
        for block in value["blocks"]:
            if block.get("block_id") == block_id:
                return path, value, block
    raise ValueError(f"Agda block not found: {block_id}")


def _upstream_code(root: Path, block: dict) -> str:
    source = root / "external" / "agda-unimath" / block["source_file"]
    lines = source.read_text().splitlines(keepends=True)
    digest = source_digest(lines, block["source_start_line"], block["source_end_line"])
    if digest != block["source_sha256"]:
        raise ValueError("The pinned upstream source range has changed; refusing to edit")
    return "".join(
        lines[block["source_start_line"] - 1 : block["source_end_line"]]
    ).rstrip("\n")


def preview_agda_block_edit(
    root: Path, block_id: str, code: str, adaptation_note: str = ""
) -> AgdaBlockEdit:
    """Prepare an exact manifest diff for one curated block edit."""

    cleaned_code = code.rstrip("\n")
    if not cleaned_code.strip():
        raise ValueError("Agda code cannot be empty")
    path, value, block = _find_block(root, block_id)
    kind = block["provenance_kind"]
    note = adaptation_note.strip()
    if kind == "handwritten":
        block["code"] = cleaned_code
        block["source_note"] = note or block.get("source_note", "")
        if not block["source_note"].strip():
            raise ValueError("Handwritten code requires a source note")
        new_kind = "handwritten"
    else:
        exact = cleaned_code == _upstream_code(root, block)
        new_kind = "exact" if exact else "adapted"
        if not exact and not note:
            raise ValueError("Edited upstream code requires an adaptation note")
        block["code"] = cleaned_code
        block["provenance_kind"] = new_kind
        if exact:
            block.pop("source_note", None)
        else:
            block["source_note"] = note
    new_text = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    return AgdaBlockEdit(
        preview=preview_edit(path, new_text),
        destination=block["destination"],
        provenance_kind=new_kind,
    )


def apply_agda_block_edit(
    root: Path,
    block_id: str,
    code: str,
    adaptation_note: str,
    expected_manifest_digest: str,
) -> tuple[Path, Path]:
    """Apply a confirmed edit and regenerate its active destination."""

    edit = preview_agda_block_edit(root, block_id, code, adaptation_note)
    if edit.preview.original_digest != expected_manifest_digest:
        raise EditConflict("The Agda manifest changed after preview; reload and try again.")
    backup = apply_edit(edit.preview, root)
    filename, document = candidate_for_destination(root, edit.destination)
    generated = write_candidate(root, filename, document)
    return backup, generated
