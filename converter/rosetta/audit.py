"""Evidence-based audit of existing translations.

The audit intentionally distinguishes facts we can establish mechanically from
facts that still require a stronger comparison or human judgment.
"""

import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional

from .latex import inventory, numbered_items, subsection_body
from .file_registry import load_file_registry, registered_filename
from .layout import rosetta_directory


HEADING_NUMBER_RE = re.compile(
    r"^#{2,6}\s+(?:Theorem|Corollary|Lemma|Proposition|Definition|"
    r"Quasi-definition|Remark|Example|Axiom|Postulate)\s+(\d+\.\d+\.\d+)\b",
    re.MULTILINE,
)
AGDA_FENCE_RE = re.compile(r"^```agda\s*\n(.*?)^```\s*$", re.MULTILINE | re.DOTALL)
NUMBERED_HEADING_RE = re.compile(
    r"^#{2,6}\s+([A-Za-z-]+)\s+(\d+\.\d+\.\d+)\b", re.MULTILINE
)


@dataclass(frozen=True)
class SectionAudit:
    chapter: int
    subsection: int
    source: str
    destination: Optional[str]
    file_present: bool
    expected_numbered_items: int
    found_numbered_items: int
    missing_item_numbers: List[str]
    substantive_agda_blocks: int
    prose_coverage: str
    agda_coverage: str
    provenance: str
    typechecking: str
    review: str

    def to_dict(self):
        return asdict(self)


def _section_file(src_dir: Path, chapter: int, subsection: int) -> Optional[Path]:
    matches = sorted(src_dir.glob(f"section-{chapter}-{subsection}-*.lagda.md"))
    if len(matches) > 1:
        names = ", ".join(str(path) for path in matches)
        raise ValueError(f"Multiple destination files match section {chapter}.{subsection}: {names}")
    return matches[0] if matches else None


def _substantive_agda_blocks(markdown: str) -> int:
    count = 0
    for block in AGDA_FENCE_RE.findall(markdown):
        meaningful = []
        for line in block.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("--"):
                continue
            if stripped.startswith("module ") or stripped.startswith("open import "):
                continue
            meaningful.append(stripped)
        if meaningful:
            count += 1
    return count


@dataclass(frozen=True)
class ExistingAgdaBlock:
    destination: str
    item_id: Optional[str]
    start_line: int
    code: str


@dataclass(frozen=True)
class AgdaSourceEvidence:
    category: str
    sources: List[str]


def extract_existing_agda_blocks(path: Path) -> List[ExistingAgdaBlock]:
    markdown = path.read_text()
    headings = list(NUMBERED_HEADING_RE.finditer(markdown))
    result = []
    for match in AGDA_FENCE_RE.finditer(markdown):
        code = match.group(1).rstrip("\n")
        if _substantive_agda_blocks(f"```agda\n{code}\n```\n") == 0:
            continue
        preceding = [heading for heading in headings if heading.start() < match.start()]
        item_id = None
        if preceding:
            heading = preceding[-1]
            item_id = f"{heading.group(1).lower()}-{heading.group(2)}"
        result.append(
            ExistingAgdaBlock(
                destination=path.name,
                item_id=item_id,
                start_line=markdown.count("\n", 0, match.start()) + 2,
                code=code,
            )
        )
    return result


def _code_chunks(code: str) -> List[str]:
    """Return substantial blank-line-separated pieces of an Agda block."""

    return [chunk.strip() for chunk in re.split(r"\n\s*\n", code) if len(chunk.strip()) >= 20]


def _contains_chunks_in_order(text: str, chunks: List[str]) -> bool:
    position = 0
    for chunk in chunks:
        position = text.find(chunk, position)
        if position < 0:
            return False
        position += len(chunk)
    return True


def _adaptation_normal_form(code: str) -> str:
    """Normalize only established legacy compatibility edits for evidence."""

    value = code.replace("UU", "Type")
    value = re.sub(r"--[^\n]*", "", value)
    return re.sub(r"\s+", "", value)


def audit_agda_sources(
    root: Path, first: int, last: int
) -> tuple[List[ExistingAgdaBlock], Dict[tuple[str, int], AgdaSourceEvidence]]:
    """Find exact full blocks and exact combined excerpts in agda-unimath."""

    upstream_files = sorted((root / "external" / "agda-unimath" / "src").rglob("*.lagda.md"))
    upstream = [(path, path.read_text()) for path in upstream_files]
    normalized_upstream = [
        (path, _adaptation_normal_form(text)) for path, text in upstream
    ]
    blocks = []
    evidence: Dict[tuple[str, int], AgdaSourceEvidence] = {}
    registry = load_file_registry(root)
    for chapter in range(first, last + 1):
        paths = [
            rosetta_directory(root) / name
            for key, name in registry.items()
            if key.startswith(f"section:{chapter}:")
            or key.startswith(f"exercise:{chapter}:")
        ]
        for path in sorted(paths):
            if path.is_file():
                blocks.extend(extract_existing_agda_blocks(path))
    for block in blocks:
        key = (block.destination, block.start_line)
        full_sources = [
            str(path.relative_to(root / "external" / "agda-unimath"))
            for path, text in upstream
            if block.code in text
        ]
        if full_sources:
            evidence[key] = AgdaSourceEvidence("exact-full", full_sources)
            continue
        chunks = _code_chunks(block.code)
        excerpt_sources = [
            str(path.relative_to(root / "external" / "agda-unimath"))
            for path, text in upstream
            if len(chunks) >= 2 and _contains_chunks_in_order(text, chunks)
        ]
        if excerpt_sources:
            evidence[key] = AgdaSourceEvidence("exact-excerpts", excerpt_sources)
            continue
        normalized = _adaptation_normal_form(block.code)
        adapted_sources = [
            str(path.relative_to(root / "external" / "agda-unimath"))
            for path, text in normalized_upstream
            if normalized and normalized in text
        ]
        evidence[key] = AgdaSourceEvidence(
            "adapted-normalized" if adapted_sources else "handwritten-local",
            adapted_sources,
        )
    return blocks, evidence


def audit_verbatim_sources(
    root: Path, first: int, last: int
) -> tuple[List[ExistingAgdaBlock], Dict[tuple[str, int], List[str]]]:
    """Compatibility wrapper returning only exact full-block matches."""

    blocks, evidence = audit_agda_sources(root, first, last)
    matches = {
        key: item.sources if item.category == "exact-full" else []
        for key, item in evidence.items()
    }
    return blocks, matches


def audit_sections(root: Path, first: int, last: int) -> List[SectionAudit]:
    sections = inventory(root / "book")
    if first < 1 or last > len(sections) or first > last:
        raise ValueError(f"Chapter range must lie between 1 and {len(sections)}")

    results: List[SectionAudit] = []
    for section in sections[first - 1 : last]:
        for subsection, _ in enumerate(section.subsections, start=1):
            _, body = subsection_body(section.path, subsection)
            expected = numbered_items(body, section.number, subsection)
            expected_numbers = {item.number for item in expected}
            candidate = rosetta_directory(root) / registered_filename(
                root, "section", section.number, subsection
            )
            destination = candidate if candidate.is_file() else None
            if destination is None:
                found_numbers = set()
                substantive_blocks = 0
            else:
                markdown = destination.read_text()
                found_numbers = set(HEADING_NUMBER_RE.findall(markdown))
                substantive_blocks = _substantive_agda_blocks(markdown)
            missing = sorted(expected_numbers - found_numbers)
            results.append(
                SectionAudit(
                    chapter=section.number,
                    subsection=subsection,
                    source=str(section.path.relative_to(root)),
                    destination=(
                        str(destination.relative_to(root)) if destination else None
                    ),
                    file_present=destination is not None,
                    expected_numbered_items=len(expected_numbers),
                    found_numbered_items=len(expected_numbers & found_numbers),
                    missing_item_numbers=missing,
                    substantive_agda_blocks=substantive_blocks,
                    # Presence and heading counts cannot establish these facts.
                    prose_coverage="unknown" if destination else "missing",
                    agda_coverage="unknown" if destination else "missing",
                    provenance="unknown" if destination else "missing",
                    typechecking="not-run" if destination else "missing",
                    review="optional-not-checked",
                )
            )
    return results
