"""Final, conservative Markdown cleanup for repository conventions."""

import re
import textwrap
from typing import List


SPAN_LABEL_RE = re.compile(r'<span id="[^"]+" data-label="[^"]+"></span>\s*')
SENTENCE_BOUNDARY_RE = re.compile(r"(?<=[.!?]) (?=[A-Z“‘*`])")
INDENTED_BLOCK_RE = re.compile(r"(?m)(?:^(?: {4}|\t).*(?:\n|$))+")
PROOF_TREE_COMMAND_RE = re.compile(
    r"\\(?:Axiom|UnaryInf|BinaryInf|TrinaryInf|RightLabel|DisplayProof|noLine)"
)


def _split_prose_line(line: str) -> List[str]:
    if not line or line.startswith(("#", "```", "    ", "<!--", "- ", "> ")):
        return [line]
    return SENTENCE_BOUNDARY_RE.split(line)


def _indented_prose(line: str) -> bool:
    """Recognize prose Pandoc indented only because it follows a list display."""

    if not line.startswith("    "):
        return False
    value = line[4:].strip()
    return bool(
        value
        and re.match(r"[A-Z][a-z]+\s", value)
    )


def clean_markdown(markdown: str) -> str:
    markdown = SPAN_LABEL_RE.sub("", markdown)
    markdown = INDENTED_BLOCK_RE.sub(
        lambda match: (
            "```text\n" + textwrap.dedent(match.group(0)).strip() + "\n```\n"
            if PROOF_TREE_COMMAND_RE.search(match.group(0))
            else match.group(0)
        ),
        markdown,
    )
    # Pandoc renders proof optional arguments as emphasized opening text.
    markdown = re.sub(
        r"### Proof\n(?:\s*\n)+\*Construction\.\.\*\s*",
        "### Construction\n\n",
        markdown,
    )
    lines: List[str] = []
    in_fence = False
    for line in markdown.splitlines():
        if line.startswith("```"):
            in_fence = not in_fence
            lines.append(line)
        elif in_fence:
            lines.append(line)
        else:
            if _indented_prose(line):
                line = line[4:]
            lines.extend(_split_prose_line(line))
    value = "\n".join(lines)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip() + "\n"
