"""Small, dependency-free data structures shared by the converter."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass(frozen=True)
class MathematicalItem:
    """A numbered theorem-like environment found in a subsection."""

    kind: str
    number: str
    label: Optional[str]
    source_line: int

    @property
    def stable_id(self) -> str:
        return f"{self.kind.lower()}-{self.number}"


@dataclass
class SectionSource:
    """A globally numbered LaTeX section and its discovered contents."""

    number: int
    title: str
    path: Path
    subsections: List[str] = field(default_factory=list)
    exercise_count: int = 0
