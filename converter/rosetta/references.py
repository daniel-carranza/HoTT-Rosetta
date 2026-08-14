"""Resolve LaTeX labels to readable Rosetta cross-references."""

import html
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from .latex import (
    EXERCISE_RE,
    LABEL_RE,
    SECTION_RE,
    SUBSECTION_RE,
    command_arguments,
    inventory,
    numbered_items,
    subsection_body,
    uncommented_text,
)


@dataclass(frozen=True)
class Reference:
    kind: str
    number: str

    @property
    def wording(self) -> str:
        if not self.kind:
            return self.number
        return f"{self.kind} {self.number}"


# Confirmed editorial wording for references that do not have a stable useful
# number in the source inventory. Keep this small and fixture-backed.
REFERENCE_ALIASES = {
    "table:Curry-Howard": "the following table",
    "eq:translation-invariant-congN": "(*)",
    "eq:well-ordering": "(*)",
    "eq:multiples-of-gcd": "(*)",
    "eq:common-divisors": "(**)",
    "item:f-up-trunc-Prop": "(i)",
    "item:f-up-trunc-Prop'": "(ii)",
    "item:equiv-Prop": "(iii)",
    "eq:is-prop-minimal-element": "(*)",
    "prp-item:surjective": "(i)",
    "prp-item:is-equiv-precomp-surjective": "(ii)",
    "prp-item:is-trunc-map-precomp-surjective": "(iii)",
    "item:count-coprod": "(1)",
    "item:count-Sigma": "(2)",
    "item:count-Sigma-count-base": "condition (2a)",
    "item:count-Sigma-count-fibers": "condition (2b)",
    "item:product-finite-types": "(2)",
    "item:Sigma-finite-types": "(3)",
}

REFERENCE_GROUP_ALIASES = {
    ("eq:multiples-of-gcd", "eq:common-divisors"): "the two displayed types",
}

ENUMERATE_TOKEN_RE = re.compile(
    r"\\begin\{enumerate\}|\\end\{enumerate\}|"
    r"\\item(?:\[[^\]]*\])?\s*(?:\\label\{([^}]+)\})?"
)


def _index_numbered_list_items(
    text: str, references: Dict[str, Reference]
) -> None:
    """Index labels attached to numbered list items in source order."""

    counters: List[int] = []
    for match in ENUMERATE_TOKEN_RE.finditer(text):
        token = match.group(0)
        if token.startswith(r"\begin"):
            counters.append(0)
        elif token.startswith(r"\end"):
            if counters:
                counters.pop()
        elif counters:
            counters[-1] += 1
            label = match.group(1)
            if label and label not in references:
                references[label] = Reference("", f"({counters[-1]})")


def _nearby_label(text: str, start: int, limit: int = 300) -> Optional[str]:
    match = LABEL_RE.search(text, start, start + limit)
    return match.group(1) if match else None


def build_reference_index(book_dir: Path) -> Dict[str, Reference]:
    references: Dict[str, Reference] = {
        label: Reference("", wording)
        for label, wording in REFERENCE_ALIASES.items()
    }
    roman = ["I", "II", "III"]
    master_inputs = [
        "chapter-type-theory",
        "chapter-univalent-foundations",
        "chapter-circle",
    ]
    for chapter_number, name in enumerate(master_inputs):
        chapter_text = uncommented_text(book_dir / f"{name}.tex")
        chapter_heading = re.search(r"\\chapter\{[^}]+\}", chapter_text)
        if chapter_heading:
            label = _nearby_label(chapter_text, chapter_heading.end())
            if label:
                references[label] = Reference("Chapter", roman[chapter_number])
    for section in inventory(book_dir):
        text = uncommented_text(section.path)
        _index_numbered_list_items(text, references)
        section_heading = SECTION_RE.search(text)
        if section_heading:
            label = _nearby_label(text, section_heading.end())
            if label:
                references[label] = Reference("Chapter", str(section.number))
        subsection_matches = command_arguments(text, "subsection")
        for subsection, match in enumerate(subsection_matches, start=1):
            label = _nearby_label(text, match[2])
            if label:
                references[label] = Reference(
                    "Section", f"{section.number}.{subsection}"
                )
            _, body = subsection_body(section.path, subsection)
            for item in numbered_items(body, section.number, subsection):
                if item.label:
                    references[item.label] = Reference(item.kind, item.number)
        exercises_start = re.search(r"\\begin\{exercises\}", text)
        if exercises_start:
            exercise_text = text[exercises_start.end() :]
            matches = list(EXERCISE_RE.finditer(exercise_text))
            for exercise, match in enumerate(matches, start=1):
                end = matches[exercise].start() if exercise < len(matches) else len(exercise_text)
                for label in LABEL_RE.findall(exercise_text[match.end() : end]):
                    references[label] = Reference(
                        "Exercise", f"{section.number}.{exercise}"
                    )
    return references


def _plural(kind: str) -> str:
    if kind.endswith("y"):
        return kind[:-1] + "ies"
    return kind + "s"


def reference_wording(labels: List[str], index: Dict[str, Reference]) -> str:
    group_alias = REFERENCE_GROUP_ALIASES.get(tuple(labels))
    if group_alias:
        return group_alias
    found = [index.get(label) for label in labels]
    if any(reference is None for reference in found):
        missing = ", ".join(
            label for label, reference in zip(labels, found) if reference is None
        )
        return f"**[unresolved reference: {missing}]**"
    references = [reference for reference in found if reference is not None]
    if len(references) == 1:
        return references[0].wording
    if all(not reference.kind for reference in references):
        return " and ".join(reference.wording for reference in references)
    kinds = {reference.kind for reference in references}
    if len(kinds) == 1:
        numbers = [reference.number for reference in references]
        joined = ", ".join(numbers[:-1]) + " and " + numbers[-1]
        return f"{_plural(references[0].kind)} {joined}"
    return ", ".join(reference.wording for reference in references[:-1]) + (
        " and " + references[-1].wording
    )


PANDOC_REFERENCE_RE = re.compile(
    r'<a\s+href="[^"]*"[^>]*data-reference="([^"]+)"[^>]*>.*?</a>'
)


def resolve_markdown_references(
    markdown: str, index: Dict[str, Reference]
) -> str:
    def replacement(match: re.Match) -> str:
        wording = reference_wording(
            html.unescape(match.group(1)).split(","), index
        )
        if wording.startswith("**[unresolved reference:"):
            return wording
        prefix = markdown[: match.start()]
        at_sentence_start = (
            not prefix.strip()
            or re.search(r"\n\s*\n\s*$", prefix) is not None
            or re.search(r"[.!?][\"')\]]*\s*$", prefix) is not None
        )
        if at_sentence_start and wording[:1].islower():
            wording = wording[:1].upper() + wording[1:]
        # Reference wording is inserted into Markdown prose, so literal stars
        # must not participate in emphasis delimiters across the paragraph.
        return wording.replace("*", r"\*")

    return PANDOC_REFERENCE_RE.sub(replacement, markdown)
