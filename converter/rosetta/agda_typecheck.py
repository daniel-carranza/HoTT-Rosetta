"""Run and cache Agda checks for reviewable candidate files."""

import hashlib
import json
import re
from pathlib import Path
from typing import Optional, Set

from .agda_manifest import load_manifest
from .generate import candidate_exercise, candidate_section, typecheck_candidate
from .latex import inventory
from .layout import rosetta_directory


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


def candidate_for_destination(root: Path, destination: str) -> tuple[str, str]:
    sections = inventory(root / "book")
    blocks = load_manifest(root / "data" / "agda-blocks.json")
    section_match = re.match(r"section-(\d+)-(\d+)-", destination)
    if section_match:
        chapter, subsection = map(int, section_match.groups())
        return candidate_section(sections[chapter - 1], subsection, blocks)
    exercise_match = re.match(r"exercise-(\d+)-(\d+)-", destination)
    if exercise_match:
        chapter, exercise = map(int, exercise_match.groups())
        return candidate_exercise(root, sections[chapter - 1], exercise, blocks)
    raise ValueError(f"Unsupported Agda destination: {destination}")


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

    blocks = blocks or load_manifest(root / "data" / "agda-blocks.json")
    selected = [block for block in blocks if block.destination == destination]
    value = [destination]
    imports = []
    for block in selected:
        value.extend(
            (block.block_id, block.code, block.conversion_status, *block.imports)
        )
        imports.extend(block.imports)
    for module in sorted(set(imports)):
        path = rosetta_directory(root) / (module + ".lagda.md")
        if path.exists():
            value.extend((module, hashlib.sha256(path.read_bytes()).hexdigest()))
        dependency = module + ".lagda.md"
        if any(block.destination == dependency for block in blocks):
            dependency_blocks = [
                block for block in blocks if block.destination == dependency
            ]
            value.extend(
                item
                for block in dependency_blocks
                for item in (block.block_id, block.code, block.conversion_status)
            )
    return hashlib.sha256("\0".join(value).encode()).hexdigest()


def typecheck_result(root: Path, destination: str) -> dict:
    blocks = load_manifest(root / "data" / "agda-blocks.json")
    digest = typecheck_fingerprint(root, destination, blocks)
    saved = load_typechecks(root)["destinations"].get(destination, {})
    if saved.get("sha256") != digest:
        return {"status": "not-checked", "message": "", "sha256": digest}
    return saved


def run_typecheck(root: Path, destination: str) -> dict:
    filename, document = candidate_for_destination(root, destination)
    blocks = load_manifest(root / "data" / "agda-blocks.json")
    document, _ = prepare_candidate_dependencies(root, document, blocks)
    digest = typecheck_fingerprint(root, destination, blocks)
    returncode, output, staged = typecheck_candidate(root, filename, document)
    result = {
        "status": "passed" if returncode == 0 else "failed",
        "message": output.strip(),
        "sha256": digest,
        "candidate": str(staged.relative_to(root)),
    }
    store = load_typechecks(root)
    store["destinations"][destination] = result
    path = _store_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(store, indent=2, ensure_ascii=False, sort_keys=True) + "\n")
    return result
