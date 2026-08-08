"""Diagram review discovery and shared approval/comment records."""

import hashlib
import json
import re
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Dict, List, Optional

from .diagrams import TIKZCD_RE, diagram_stable_id
from .editing import apply_edit, preview_edit
from .active_files import active_files


DIAGRAM_REVIEW_RE = re.compile(
    r"<!-- rosetta-diagram: ([0-9a-f]+); review: (pending|approved) -->\s*"
    r"\*([^\n]+?) \(automatic draft\)\.\*\s*"
    r"```text\n(.*?)^```",
    re.MULTILINE | re.DOTALL,
)


@dataclass(frozen=True)
class DiagramReviewItem:
    stable_id: str
    state: str
    description: str
    ascii_art: str
    source: str
    comments: List[str]

    def to_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class DiagramReviewRecord:
    destination: str
    item: DiagramReviewItem

    def to_dict(self):
        return {"destination": self.destination, **self.item.to_dict()}


def source_diagrams(book_dir: Path) -> Dict[str, str]:
    """Index original tikz-cd environments by the generated stable ID."""

    sources: Dict[str, str] = {}
    for path in sorted(book_dir.glob("*.tex")):
        for match in TIKZCD_RE.finditer(path.read_text()):
            source = match.group(0)
            stable_id = diagram_stable_id(source)
            sources[stable_id] = source
    return sources


def diagram_review_items(markdown: str, sources: Dict[str, str]) -> List[DiagramReviewItem]:
    """Return diagram drafts in document order with their original source."""

    return [
        DiagramReviewItem(
            stable_id=match.group(1),
            state=match.group(2),
            description=match.group(3),
            ascii_art=match.group(4).rstrip(),
            source=sources.get(match.group(1), ""),
            comments=[],
        )
        for match in DIAGRAM_REVIEW_RE.finditer(markdown)
    ]


def _empty_store() -> dict:
    return {"version": 1, "diagrams": {}}


def load_review_store(path: Path) -> dict:
    """Load the optional shared review file with strict basic validation."""

    if not path.exists():
        return _empty_store()
    store = json.loads(path.read_text())
    if store.get("version") != 1 or not isinstance(store.get("diagrams"), dict):
        raise ValueError(f"Invalid diagram review data: {path}")
    return store


def _source_digest(source: str) -> str:
    return hashlib.sha256(source.encode()).hexdigest()


def _stored_item(item: DiagramReviewItem, store: dict) -> DiagramReviewItem:
    record = store["diagrams"].get(item.stable_id)
    if not record:
        return item
    current_digest = _source_digest(item.source) if item.source else ""
    state = record.get("state", "pending")
    if record.get("source_sha256") != current_digest:
        state = "stale"
    comments = record.get("comments", [])
    if not isinstance(comments, list) or any(not isinstance(value, str) for value in comments):
        raise ValueError(f"Invalid comments for diagram {item.stable_id}")
    return replace(item, state=state, comments=comments)


def discover_diagram_reviews(root: Path) -> List[DiagramReviewRecord]:
    """Find generated diagram drafts and pair them with book sources."""

    sources = source_diagrams(root / "book")
    store = load_review_store(root / "data" / "diagram-reviews.json")
    records: List[DiagramReviewRecord] = []
    for path in (path for path in active_files(root) if path.name.startswith("section-")):
        for discovered in diagram_review_items(path.read_text(), sources):
            item = _stored_item(discovered, store)
            records.append(
                DiagramReviewRecord(
                    str(path.relative_to(root)),
                    item,
                )
            )
    return records


def update_diagram_review(
    root: Path,
    stable_id: str,
    *,
    state: Optional[str] = None,
    comment: Optional[str] = None,
) -> Path:
    """Persist one approval or comment using the protected edit boundary."""

    records = discover_diagram_reviews(root)
    matches = [record.item for record in records if record.item.stable_id == stable_id]
    if not matches:
        raise ValueError(f"Generated diagram not found: {stable_id}")
    item = matches[0]
    if not item.source:
        raise ValueError(f"Diagram {stable_id} has no paired source")
    path = root / "data" / "diagram-reviews.json"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(_empty_store(), indent=2) + "\n")
    store = load_review_store(path)
    record = store["diagrams"].setdefault(stable_id, {})
    record["source_sha256"] = _source_digest(item.source)
    if state is not None:
        if state not in {"pending", "approved"}:
            raise ValueError(f"Unsupported review state: {state}")
        record["state"] = state
    else:
        record.setdefault("state", item.state if item.state != "stale" else "pending")
    comments = record.setdefault("comments", [])
    if comment is not None:
        cleaned = comment.strip()
        if not cleaned:
            raise ValueError("Review comments cannot be empty")
        comments.append(cleaned)
    new_text = json.dumps(store, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    preview = preview_edit(path, new_text)
    apply_edit(preview, root)
    return path
