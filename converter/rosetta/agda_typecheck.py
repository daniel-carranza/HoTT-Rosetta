"""Run and cache Agda checks for reviewable candidate files."""

import hashlib
import json
import re
from pathlib import Path
from typing import Optional, Set

from .agda_manifest import load_manifest
from .generate import typecheck_candidate
from .layout import rosetta_directory
from .maintained import destination_path, dependency_digest, replace_block
from .editing import update_json_store


def _store_path(root: Path) -> Path:
    return root / "_build" / "rosetta-review" / "agda-typechecks.json"


def load_typechecks(root: Path) -> dict:
    path = _store_path(root)
    if not path.exists():
        return {"version": 1, "destinations": {}}
    value = json.loads(path.read_text())
    if value.get("version") != 1 or not isinstance(value.get("destinations"), dict):
        raise ValueError(f"Invalid Agda typecheck data: {path}")
    return value


def deferred_exercises(blocks, destination: str, document: str = "") -> list:
    """Return unfinished exercises contained in or imported by a candidate."""

    by_destination = {}
    for block in blocks:
        by_destination.setdefault(block.destination, []).append(block)
    pending = {}
    visiting = set()

    def visit(current: str):
        if current in visiting:
            return
        visiting.add(current)
        for block in by_destination.get(current, []):
            if block.conversion_status == "exercise":
                pending[block.block_id] = block
            if block.conversion_status == "ready":
                for module in block.imports:
                    visit(module + ".lagda.md")

    visit(destination)
    for module in re.findall(r"^open import ([A-Za-z0-9-]+)", document, re.MULTILINE):
        visit(module + ".lagda.md")
    return sorted(pending.values(), key=lambda block: (block.destination, block.item_id))


def deferred_message(blocks) -> str:
    items = ", ".join(dict.fromkeys(block.item_id for block in blocks))
    return (
        "Agda was not run. This file contains or depends on "
        f"recorded unfinished mathematics: {items}."
    )


def candidate_for_destination(
    root: Path, destination: str, blocks=None
) -> tuple[str, str]:
    """Read maintained content; optional blocks are explicit draft overlays."""
    document = destination_path(root, destination).read_text()
    if blocks is not None:
        originals = {b.block_id: b for b in load_manifest(root / "data" / "agda-blocks.json")}
        for block in blocks:
            if block.destination == destination and block != originals.get(block.block_id):
                document = replace_block(document, block.block_id, block.code)
    return destination, document


def prepare_candidate_dependencies(
    root: Path, document: str, blocks, visiting: Optional[Set[str]] = None
) -> tuple[str, str]:
    """Fingerprint generated imports used by a review candidate."""

    visiting = set() if visiting is None else visiting
    combined = []
    for module in re.findall(r"^open import ([A-Za-z0-9-]+)", document, re.MULTILINE):
        destination = module + ".lagda.md"
        dependency_path = rosetta_directory(root) / destination
        if not dependency_path.is_file() or module in visiting:
            continue
        combined.extend(
            (destination, hashlib.sha256(dependency_path.read_bytes()).hexdigest())
        )
    digest = hashlib.sha256((document + "\0" + "\0".join(combined)).encode()).hexdigest()
    return document, digest


def typecheck_fingerprint(root: Path, destination: str, blocks=None) -> str:
    """Fingerprint the Agda content without rendering any candidates."""

    return dependency_digest(root, destination)


def typecheck_result(root: Path, destination: str) -> dict:
    blocks = load_manifest(root / "data" / "agda-blocks.json")
    digest = typecheck_fingerprint(root, destination, blocks)
    pending = deferred_exercises(blocks, destination)
    if pending:
        return {
            "status": "deferred",
            "message": deferred_message(pending),
            "sha256": digest,
            "candidate": "",
        }
    saved = load_typechecks(root)["destinations"].get(destination, {})
    if saved.get("sha256") != digest:
        return {"status": "not-checked", "message": "", "sha256": digest}
    return saved


def run_typecheck(root: Path, destination: str, force: bool = False) -> dict:
    filename, document = candidate_for_destination(root, destination)
    blocks = load_manifest(root / "data" / "agda-blocks.json")
    document, _ = prepare_candidate_dependencies(root, document, blocks)
    digest = typecheck_fingerprint(root, destination, blocks)
    pending = deferred_exercises(blocks, destination, document)
    if pending and not force:
        return {
            "status": "deferred",
            "message": deferred_message(pending),
            "sha256": digest,
            "candidate": "",
        }
    returncode, output, staged = typecheck_candidate(root, filename, document)
    result = {
        "status": "passed" if returncode == 0 else "failed",
        "message": output.strip(),
        "sha256": digest,
        "candidate": str(staged.relative_to(root)),
    }
    def update(store):
        store["destinations"][destination] = result

    update_json_store(_store_path(root), root, "destinations", update)
    return result
