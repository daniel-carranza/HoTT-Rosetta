"""Conservative inspection of this repository's LaTeX sources.

This module deliberately does not pretend to be a general TeX parser. It only
recognizes structural commands after comments have been removed. Pandoc will
be responsible for parsing prose and mathematics in the rendering stage.
"""

import re
from pathlib import Path
from typing import Iterator, List, Tuple

from .model import MathematicalItem, SectionSource


INPUT_RE = re.compile(r"\\input\{([^}]+)\}")
SECTION_RE = re.compile(r"\\section\{([^}]+)\}")
SUBSECTION_RE = re.compile(r"\\subsection\{([^}]+)\}")
BEGIN_RE = re.compile(
    r"\\begin\{(thm|cor|lem|prp|defn|quasidefn|rmk|eg|axiom|postulate)\}"
)
LABEL_RE = re.compile(r"\\label\{([^}]+)\}")
EXERCISE_RE = re.compile(r"\\exitem\b")

ITEM_NAMES = {
    "thm": "Theorem",
    "cor": "Corollary",
    "lem": "Lemma",
    "prp": "Proposition",
    "defn": "Definition",
    "quasidefn": "Quasi-definition",
    "rmk": "Remark",
    "eg": "Example",
    "axiom": "Axiom",
    "postulate": "Postulate",
}


def uncommented_lines(text: str) -> Iterator[Tuple[int, str]]:
    """Yield line numbers and content with unescaped LaTeX comments removed."""

    for number, line in enumerate(text.splitlines(), start=1):
        index = 0
        while True:
            index = line.find("%", index)
            if index < 0:
                break
            backslashes = 0
            cursor = index - 1
            while cursor >= 0 and line[cursor] == "\\":
                backslashes += 1
                cursor -= 1
            if backslashes % 2 == 0:
                line = line[:index]
                break
            index += 1
        yield number, line


def uncommented_text(path: Path) -> str:
    return "\n".join(line for _, line in uncommented_lines(path.read_text()))


def input_names(path: Path) -> List[str]:
    """Return active input targets in source order."""

    return INPUT_RE.findall(uncommented_text(path))


def command_arguments(text: str, command: str) -> List[Tuple[str, int, int]]:
    """Return balanced braced arguments as (value, command start, end)."""

    marker = "\\" + command + "{"
    results = []
    search_from = 0
    while True:
        start = text.find(marker, search_from)
        if start < 0:
            return results
        argument_start = start + len(marker)
        depth = 1
        position = argument_start
        while position < len(text) and depth:
            if text[position] == "{" and (
                position == 0 or text[position - 1] != "\\"
            ):
                depth += 1
            elif text[position] == "}" and (
                position == 0 or text[position - 1] != "\\"
            ):
                depth -= 1
            position += 1
        if depth:
            raise ValueError(f"Unclosed argument for {marker} at character {start}")
        results.append((text[argument_start : position - 1], start, position))
        search_from = position


def book_section_paths(book_dir: Path) -> List[Path]:
    """Follow the book's nested input chain and return mathematical sections."""

    master = book_dir / "hott-intro.tex"
    chapter_names = [
        name for name in input_names(master) if name.startswith("chapter-")
    ]
    result: List[Path] = []
    for chapter_name in chapter_names:
        chapter = book_dir / f"{chapter_name}.tex"
        for name in input_names(chapter):
            candidate = book_dir / f"{name}.tex"
            if candidate.exists():
                result.append(candidate)
    return result


def inventory(book_dir: Path) -> List[SectionSource]:
    result: List[SectionSource] = []
    for number, path in enumerate(book_section_paths(book_dir), start=1):
        text = uncommented_text(path)
        section_arguments = command_arguments(text, "section")
        if not section_arguments:
            raise ValueError(f"No section heading found in {path}")
        subsection_arguments = command_arguments(text, "subsection")
        result.append(
            SectionSource(
                number=number,
                title=section_arguments[0][0],
                path=path,
                subsections=[argument[0] for argument in subsection_arguments],
                exercise_count=len(EXERCISE_RE.findall(text)),
            )
        )
    return result


def numbered_items(text: str, section: int, subsection: int) -> List[MathematicalItem]:
    """Apply the shared theorem counter used by book/hott-intro.tex."""

    items: List[MathematicalItem] = []
    counter = 0
    lines = list(uncommented_lines(text))
    for position, (line_number, line) in enumerate(lines):
        match = BEGIN_RE.search(line)
        if match is None:
            continue
        counter += 1
        nearby = line + " " + " ".join(value for _, value in lines[position + 1 : position + 3])
        label_match = LABEL_RE.search(nearby)
        items.append(
            MathematicalItem(
                kind=ITEM_NAMES[match.group(1)],
                number=f"{section}.{subsection}.{counter}",
                label=label_match.group(1) if label_match else None,
                source_line=line_number,
            )
        )
    return items


def subsection_body(path: Path, subsection_number: int) -> Tuple[str, str]:
    """Return a subsection title and body, stopping before exercises."""

    text = uncommented_text(path)
    matches = command_arguments(text, "subsection")
    if subsection_number < 1 or subsection_number > len(matches):
        raise IndexError(f"{path} has no subsection {subsection_number}")
    current = matches[subsection_number - 1]
    start = current[2]
    candidates = [len(text)]
    if subsection_number < len(matches):
        candidates.append(matches[subsection_number][1])
    exercises = re.search(r"\\begin\{exercises\}", text[start:])
    if exercises:
        candidates.append(start + exercises.start())
    return current[0], text[start : min(candidates)].strip()


def section_introduction(path: Path) -> str:
    """Return text after the section heading and before its first subsection."""

    text = uncommented_text(path)
    sections = command_arguments(text, "section")
    if not sections:
        raise ValueError(f"No section heading found in {path}")
    start = sections[0][2]
    subsections = command_arguments(text, "subsection")
    end = subsections[0][1] if subsections else len(text)
    exercises = re.search(r"\\begin\{exercises\}", text[start:end])
    if exercises:
        end = start + exercises.start()
    return text[start:end].strip()


def exercise_bodies(path: Path) -> List[str]:
    """Split the active exercises environment at each ``\\exitem`` marker."""

    text = uncommented_text(path)
    environment = re.search(
        r"\\begin\{exercises\}(.*?)\\end\{exercises\}", text, re.DOTALL
    )
    if not environment:
        return []
    body = environment.group(1)
    markers = list(EXERCISE_RE.finditer(body))
    return [
        body[marker.end() : markers[index + 1].start() if index + 1 < len(markers) else len(body)].strip()
        for index, marker in enumerate(markers)
    ]
