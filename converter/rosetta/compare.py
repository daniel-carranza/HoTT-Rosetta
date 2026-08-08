"""Measured comparison between regenerated previews and active files."""

import difflib
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List

from .render import render_section


FENCE_RE = re.compile(r"^```([^\n]*)\n.*?^```\s*$", re.MULTILINE | re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.MULTILINE)
WORD_RE = re.compile(r"[\wÀ-žℕℤ]+(?:[-'][\wÀ-žℕℤ]+)*", re.UNICODE)
RAW_COMMAND_RE = re.compile(r"\\[A-Za-z@]+")
DIAGRAM_DRAFT_RE = re.compile(
    r"<!-- rosetta-diagram: [^;]+; review: pending -->\s*"
    r"\*.*?\(automatic draft\)\.\*\s*```text\n.*?^```\s*",
    re.MULTILINE | re.DOTALL,
)
MIN_PROSE_SIMILARITY = 0.90
DISPLAY_DIFFERENCE_CLASSIFICATIONS = {
    "section-7-1-": "generated output preserves source displays split around prose and diagrams",
    "section-7-3-": "active reference manually splits one source display",
    "section-7-4-": "generated output preserves source diagrams omitted from the fixture",
    "section-9-1-": "generated output preserves a source diagram omitted from the fixture",
    "section-10-4-": "generated output preserves source diagrams omitted from the fixture",
    "section-14-2-": "generated output preserves a source diagram omitted from the fixture",
    "section-14-4-": "active reference manually splits one source display",
    "section-16-3-": "active reference manually splits one source display",
    "section-17-3-": "active reference manually splits one source display",
    "section-17-5-": "generated output preserves source displays merged or omitted in the fixture",
}
DIAGRAM_CAPTION_RE = re.compile(
    r"^\*.*? diagram(?:.*?)? \(automatic draft\)\.\*\s*$", re.MULTILINE
)


@dataclass(frozen=True)
class Comparison:
    destination: str
    prose_similarity: float
    expected_headings: int
    matching_headings: int
    generated_text_fences: int
    expected_text_fences: int
    unresolved_references: int
    raw_tex_commands: List[str]
    display_difference_classification: str = ""

    def to_dict(self):
        return asdict(self)


def comparison_issues(result: Comparison) -> List[str]:
    """Return reasons a comparison is not yet a high-fidelity match."""

    issues = []
    if result.prose_similarity < MIN_PROSE_SIMILARITY:
        issues.append("prose below 90%")
    if result.matching_headings != result.expected_headings:
        issues.append("headings differ")
    if (result.generated_text_fences != result.expected_text_fences
            and not result.display_difference_classification):
        issues.append("display math differs")
    if result.unresolved_references:
        issues.append("unresolved references")
    if result.raw_tex_commands:
        issues.append("raw TeX remains")
    return issues


def _without_code(markdown: str) -> str:
    value = FENCE_RE.sub("", markdown)
    value = DIAGRAM_CAPTION_RE.sub("", value)
    value = "\n".join(
        line for line in value.splitlines() if not line.startswith("    ")
    )
    value = re.sub(r"<!--.*?-->", "", value, flags=re.DOTALL)
    return value


def raw_tex_commands_outside_fences(markdown: str) -> List[str]:
    """Return unfinished TeX commands, excluding deliberately preserved code."""

    return sorted(set(RAW_COMMAND_RE.findall(_without_code(markdown))))


def candidate_raw_tex_commands(markdown: str) -> List[str]:
    """Check prose and ordinary displays, excluding Agda and diagram drafts."""

    value = DIAGRAM_DRAFT_RE.sub("", markdown)

    def fence_body(match):
        language = match.group(1).strip()
        if language == "agda":
            return ""
        return match.group(0).removeprefix(f"```{match.group(1)}\n").removesuffix(
            "```"
        )

    value = FENCE_RE.sub(fence_body, value)
    return sorted(set(RAW_COMMAND_RE.findall(value)))


def pending_diagram_count(markdown: str) -> int:
    """Count automatic diagram drafts carrying pending review markers."""

    return len(
        re.findall(r"<!-- rosetta-diagram: [^;]+; review: pending -->", markdown)
    )


def _prose_only(markdown: str) -> str:
    value = FENCE_RE.sub("", markdown)
    value = DIAGRAM_CAPTION_RE.sub("", value)
    value = re.sub(r"<!--.*?-->", "", value, flags=re.DOTALL)
    value = INLINE_CODE_RE.sub("", value)
    # These active-file additions describe review or provenance rather
    # than prose translated from the book source.
    value = re.sub(
        r"^## Agda-unimath sources\s*$.*",
        "",
        value,
        flags=re.MULTILINE | re.DOTALL,
    )
    value = "\n".join(
        line for line in value.splitlines() if not line.startswith("TODO:")
    )
    return value


def _tokens(markdown: str) -> List[str]:
    return [token.lower() for token in WORD_RE.findall(_without_code(markdown))]


def _prose_tokens(markdown: str) -> List[str]:
    return [token.lower() for token in WORD_RE.findall(_prose_only(markdown))]


def _fence_count(markdown: str, language: str) -> int:
    return sum(
        1 for match in FENCE_RE.finditer(markdown) if match.group(1).strip() == language
    )


def _structural_headings(markdown: str) -> set:
    """Return headings after fixture-backed presentation normalization."""

    headings = set()
    for heading in HEADING_RE.findall(markdown):
        if heading == "Agda-unimath sources" or heading.startswith(
            ("Prelude to ", "Unnumbered Remark")
        ):
            continue
        if heading.startswith("Proof of "):
            heading = "Proof"
        heading = re.sub(r"^Section\s+", "", heading)
        heading = re.sub(r"^\d+\.\d+\s+", "", heading)
        heading = heading.replace("`", "")
        heading = heading.replace("ℕ", "natural numbers")
        heading = heading.replace("the natural numbers", "natural numbers")
        heading = heading.replace("Π", "Pi").replace("Σ", "Sigma")
        heading = re.sub(r"\s*\+\s*", " + ", heading)
        headings.add(heading)
    return headings


def compare_section(generated: str, expected_path: Path, root: Path) -> Comparison:
    expected = expected_path.read_text()
    generated_headings = _structural_headings(generated)
    expected_headings = _structural_headings(expected)
    commands = raw_tex_commands_outside_fences(generated)
    classification = next(
        (reason for prefix, reason in DISPLAY_DIFFERENCE_CLASSIFICATIONS.items()
         if expected_path.name.startswith(prefix)),
        "",
    )
    return Comparison(
        destination=str(expected_path.relative_to(root)),
        prose_similarity=round(
            max(
                difflib.SequenceMatcher(
                    None, _tokens(expected), _tokens(generated)
                ).ratio(),
                difflib.SequenceMatcher(
                    None, _prose_tokens(expected), _prose_tokens(generated)
                ).ratio(),
            ),
            4,
        ),
        expected_headings=len(expected_headings),
        matching_headings=len(expected_headings & generated_headings),
        generated_text_fences=_fence_count(generated, "text"),
        expected_text_fences=_fence_count(expected, "text"),
        unresolved_references=generated.count("[unresolved reference:"),
        raw_tex_commands=commands,
        display_difference_classification=(
            classification
            if _fence_count(generated, "text") != _fence_count(expected, "text")
            else ""
        ),
    )
