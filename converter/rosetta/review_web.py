"""Small dependency-free browser interface for Agda review."""

import html
import json
import re
import secrets
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Optional
from urllib.parse import parse_qs, quote, unquote, urlparse

from .agda_review import (
    AgdaReviewRecord,
    _with_stored_review,
    discover_agda_reviews,
    load_agda_review_store,
    missing_agda_block_id,
    update_agda_review,
)
from .active_files import active_file, active_files
from .layout import rosetta_directory
from .missing_agda import MissingAgdaItem, discover_missing_agda
from .agda_typecheck import run_typecheck
from .pandoc import markdown_fragments_to_safe_html, markdown_to_safe_html


STYLE = """
body { font-family: system-ui, sans-serif; margin: 0; color: #202124; }
header { background: #23395d; color: white; padding: 1rem 1.5rem; }
main { max-width: 1500px; margin: auto; padding: 1.25rem; }
a { color: #174ea6; }
.summary, .controls { display: flex; gap: .75rem; flex-wrap: wrap; align-items: center; }
.badge { border-radius: 1rem; padding: .25rem .65rem; background: #e8eaed; }
.approved { background: #ceead6; } .rejected, .stale { background: #f8d7da; }
.pending { background: #feefc3; }
.passed { background: #ceead6; } .failed { background: #f8d7da; }
.not-checked, .not-applicable, .missing { background: #e8eaed; }
.columns { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.statement { grid-column: 1 / -1; }
.panel { border: 1px solid #dadce0; border-radius: .5rem; padding: 1rem; min-width: 0; }
pre { white-space: pre-wrap; overflow-wrap: anywhere; background: #f6f8fa; padding: 1rem; }
textarea { width: 95%; min-height: 30rem; font-family: ui-monospace, monospace; }
.comment-box { min-height: 5rem; max-width: 50rem; }
.review-comments { margin-top: 1.25rem; font-size: 1.1rem; line-height: 1.55; }
.review-comments li { margin: .65rem 0; }
.lower-navigation { margin: 1.25rem 0; padding: .75rem 0; border-bottom: 1px solid #dadce0; }
.reader-preview { font-size: 1rem; line-height: 1.55; }
.reader-preview pre { white-space: pre; overflow-x: auto; overflow-wrap: normal; }
.reader-preview a[href^='/agda/'] { display: inline-block; margin: .15rem .35rem .65rem 0; padding: .2rem .5rem; border: 1px solid #174ea6; border-radius: .3rem; background: white; font-size: .85rem; text-decoration: none; }
.missing-item { margin: 1rem 0; }
button { padding: .55rem .9rem; cursor: pointer; }
table { width: 100%; border-collapse: collapse; } th, td { padding: .55rem; border-bottom: 1px solid #ddd; text-align: left; }
.warning { border-left: .3rem solid #d93025; padding-left: .8rem; }
@media (max-width: 850px) { .columns { grid-template-columns: 1fr; } .statement { grid-column: auto; } }
"""


def _layout(title: str, body: str) -> str:
    return (
        "<!doctype html><html><head><meta charset='utf-8'>"
        f"<meta name='viewport' content='width=device-width'><title>{html.escape(title)}</title>"
        f"<style>{STYLE}</style></head><body><header><h1>{html.escape(title)}</h1>"
        "</header><main>" + body + "</main></body></html>"
    )


def render_index(
    records: list[AgdaReviewRecord], file_count: int = 0, missing_count: int = 0
) -> str:
    counts = {state: sum(item.state == state for item in records) for state in (
        "pending", "approved", "rejected", "stale"
    )}
    rows = []
    for record in records:
        url = "/agda/" + quote(record.block_id)
        has_comments = "true" if record.comments else "false"
        rows.append(
            f"<tr class='agda-item' data-has-comments='{has_comments}'>"
            f"<td><a href='{url}'>{html.escape(record.item_id)}</a></td>"
            f"<td>{html.escape(record.destination)}</td>"
            f"<td>{html.escape(record.provenance_kind)}</td>"
            f"<td><span class='badge {record.state}'>{html.escape(record.state)}</span></td>"
            f"<td><span class='badge {record.typecheck_status}'>{html.escape(record.typecheck_status)}</span></td>"
            "</tr>"
        )
    summary = "".join(
        f"<span class='badge {state}'>{count} {state}</span>"
        for state, count in counts.items()
    )
    body = (
        "<p>Review the book text, Rosetta Agda code, and recorded source side by side.</p>"
        f"<p><a href='/read'>Read {file_count} generated .lagda.md files</a> · "
        f"<a href='/missing-agda'>View {missing_count} mathematical items missing Agda</a></p>"
        f"<div class='summary'>{summary}</div><h2>Agda review items</h2>"
        "<p><label>Find an item: <input id='agda-search' type='search' "
        "placeholder='For example: 7.9'></label> &nbsp; "
        "<label><input id='comments-only' type='checkbox'> "
        "Only items with comments</label></p>"
        "<table><thead><tr><th>Book item</th><th>File</th><th>Source kind</th>"
        "<th>Review</th><th>Agda check</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table>"
        "<script>const search=document.getElementById('agda-search');"
        "const commentsOnly=document.getElementById('comments-only');"
        "function filterItems(){const q=search.value.toLowerCase();"
        "document.querySelectorAll('.agda-item').forEach(function(x){"
        "const matchesText=x.textContent.toLowerCase().includes(q);"
        "const matchesComments=!commentsOnly.checked||x.dataset.hasComments==='true';"
        "x.hidden=!(matchesText&&matchesComments);});}"
        "search.addEventListener('input',filterItems);"
        "commentsOnly.addEventListener('change',filterItems);</script>"
    )
    return _layout("HoTT Rosetta review", body)


def render_file_index(paths: list[Path]) -> str:
    rows = "".join(
        f"<li class='file'><a href='/read/{quote(path.name)}'>"
        f"{html.escape(path.name)}</a></li>"
        for path in paths
    )
    return _layout(
        "Generated Rosetta files",
        "<p><a href='/'>← Review home</a></p>"
        + "<p>These are the active generated Rosetta files. They combine the "
        "converted book text with curated Agda blocks and are read-only here.</p>"
        +
        "<p><label>Find a file: <input id='file-search' type='search'></label></p>"
        "<ul>" + rows + "</ul>"
        "<script>document.getElementById('file-search').addEventListener('input',function(){"
        "const q=this.value.toLowerCase();document.querySelectorAll('.file').forEach(function(x){"
        "x.hidden=!x.textContent.toLowerCase().includes(q);});});</script>",
    )


def _reader_review_links(records: list[AgdaReviewRecord]) -> str:
    links = []
    for index, record in enumerate(records, 1):
        label = "Review missing Agda" if record.provenance_kind == "missing" else "Review Agda"
        if len(records) > 1:
            label += f" {index}"
        links.append(f"[{label}](/agda/{quote(record.block_id)})")
    return " ".join(links)


def render_file_reader(
    name: str,
    content: str,
    records: Optional[list[AgdaReviewRecord]] = None,
) -> str:
    records = records or []
    by_number = {}
    for record in records:
        number_match = re.search(r"(\d+\.\d+(?:\.\d+)?)", record.statement)
        if not number_match:
            number_match = re.search(
                r"(\d+)-(\d+)(?:-(\d+))?", record.item_id
            )
            if number_match:
                number = ".".join(value for value in number_match.groups() if value)
            else:
                continue
        else:
            number = number_match.group(1)
        by_number.setdefault(number, []).append(record)

    lines = []
    heading = re.compile(r"^#{1,6}\s+.*?\b(\d+\.\d+(?:\.\d+)?)\b")
    proof_heading = re.compile(r"^#{2,6}\s+(?:Proof|Construction)\s*$", re.IGNORECASE)
    exercise_heading = re.compile(r"^##\s+(?:Problem statement|Solution)\s*$", re.IGNORECASE)
    current_records = []
    exercise_records = [record for record in records if record.item_id.startswith("exercise-")]
    in_fence = False
    for line in content.splitlines(keepends=True):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        match = None if in_fence else heading.match(line)
        links = ""
        if match:
            number = match.group(1)
            current_records = by_number.get(number, [])
            newline = "\n" if line.endswith("\n") else ""
            line = line.rstrip("\r\n") + f" {{#item-{number}}}" + newline
            links = _reader_review_links(current_records)
        elif not in_fence and proof_heading.match(line):
            links = _reader_review_links(current_records)
        elif not in_fence and exercise_heading.match(line):
            links = _reader_review_links(exercise_records)
        lines.append(line)
        if links:
            lines.append("\n" + links + "\n")
    preview = markdown_to_safe_html("".join(lines))
    return _layout(
        name,
        "<nav class='controls'><a href='/read'>← All generated files</a></nav>"
        f"<article class='reader-preview'>{preview}</article>",
    )


def render_missing_agda(items: list[MissingAgdaItem]) -> str:
    rows = []
    previews = markdown_fragments_to_safe_html(
        [item.statement or "Statement unavailable in generated file." for item in items]
    )
    for item, preview in zip(items, previews):
        rows.append(
            "<details class='panel missing-item'><summary>"
            f"<strong>{html.escape(item.kind)} {html.escape(item.number)}</strong> — "
            f"<a href='/agda/{quote(missing_agda_block_id(item.destination, item.item_id))}'>"
            "Open the review page</a> · "
            f"<a href='/read/{quote(item.destination)}#item-{quote(item.number)}'>"
            f"{html.escape(item.destination)}</a></summary>"
            f"<div class='reader-preview'>{preview}</div>"
            "</details>"
        )
    return _layout(
        "Mathematical items missing Agda",
        "<p><a href='/'>← Review home</a></p>"
        "<p>These numbered definitions, results, remarks, and similar items occur in "
        "generated files but have no associated substantive Agda block. Expand an "
        "item to read its statement and proof, or open its complete file.</p>"
        f"<p><strong>{len(items)} items</strong></p>"
        "<p><label>Find a missing item: <input id='missing-search' type='search' "
        "placeholder='For example: 7.9'></label></p>"
        f"{''.join(rows) or '<p>No items are missing Agda.</p>'}"
        "<script>document.getElementById('missing-search').addEventListener('input',function(){"
        "const q=this.value.toLowerCase();document.querySelectorAll('.missing-item').forEach(function(x){"
        "x.hidden=!x.textContent.toLowerCase().includes(q);});});</script>",
    )


def render_record(
    record: AgdaReviewRecord, previous_id: str = "", next_id: str = "", token: str = ""
) -> str:
    navigation = ["<a href='/'>All blocks</a>"]
    if previous_id:
        navigation.append(f"<a href='/agda/{quote(previous_id)}'>← Previous</a>")
    if next_id:
        navigation.append(f"<a href='/agda/{quote(next_id)}'>Next →</a>")
    navigation_html = " &nbsp; ".join(navigation)
    is_missing = record.provenance_kind == "missing"
    source_note = (
        "No Agda code or applicable upstream source has been recorded yet."
        if is_missing
        else
        "This is an exact copy of the recorded source."
        if record.exact_match
        else (
            "This is handwritten project code. No upstream source is claimed."
            if record.provenance_kind == "handwritten"
            else "This block is adapted. Compare the differences before approving it."
        )
    )
    warning_class = "" if record.exact_match else " class='warning'"
    comments = "".join(
        f"<li><strong>{html.escape(value.author)}</strong>"
        f"{': ' if value.author else ''}{html.escape(value.text)}</li>"
        for value in record.comments
    )
    check_message = (
        f"<pre>{html.escape(record.typecheck_message)}</pre>"
        if record.typecheck_message else ""
    )
    body = (
        f"<nav class='controls'>{navigation_html}</nav>"
        f"<h2>{html.escape(record.item_id)}</h2>"
        f"<p><span class='badge {record.state}'>{html.escape(record.state)}</span> "
        f"<span class='badge'>{html.escape(record.provenance_kind)}</span> "
        f"<span class='badge'>{html.escape(record.conversion_status)}</span> "
        f"<span class='badge {record.typecheck_status}'>Agda: {html.escape(record.typecheck_status)}</span></p>"
        + (
            f"<p class='warning'><strong>Not inserted by conversion:</strong> "
            f"{html.escape(record.conversion_note)}</p>"
            if record.conversion_status == "blocked" else ""
        )
        +
        f"<p><a href='/read/{quote(record.destination)}'>Read the generated file</a></p>"
        + (
            "<section class='panel warning'><h3>Agda code missing</h3>"
            "<p>This item has no candidate Agda block. Use the shared comments to "
            "record helpful search results or relevant upstream material.</p></section>"
            if is_missing else
            f"<section class='panel'><h3>Agda check</h3>"
            f"<p>This checks the complete candidate file containing this block.</p>{check_message}"
            f"<form method='post' action='/agda/{quote(record.block_id)}/typecheck'>"
            f"<input type='hidden' name='token' value='{html.escape(token)}'>"
            "<button type='submit'>Run Agda check</button></form></section>"
        )
        +
        "<div class='columns'>"
        f"<section class='panel statement'><h3>Book statement or proof</h3>"
        f"<div class='reader-preview'>{markdown_to_safe_html(record.statement)}</div></section>"
        f"<section class='panel'><h3>Rosetta Agda code</h3><pre>{html.escape(record.project_code) if record.project_code else 'No candidate Agda code.'}</pre></section>"
        f"<section class='panel'><h3>Recorded source code</h3><p{warning_class}>{html.escape(source_note)}</p>"
        f"<p><strong>Location:</strong> {html.escape(record.source_location)}<br>"
        f"<strong>Commit:</strong> <code>{html.escape(record.source_commit)}</code></p>"
        f"<pre>{html.escape(record.source_code)}</pre></section></div>"
        f"<nav class='controls lower-navigation'>{navigation_html}</nav>"
        f"<section class='panel review-comments'><h3>Existing comments</h3>"
        f"<ul>{comments or '<li>No comments yet.</li>'}</ul></section>"
        f"<form method='post' action='/agda/{quote(record.block_id)}'>"
        f"<input type='hidden' name='token' value='{html.escape(token)}'>"
        "<h3>Review decision</h3>"
        + (
            "<p>Missing code cannot be approved or rejected.</p>"
            if is_missing else
            "<div class='controls'><button name='state' value='approved'>Approve</button>"
            "<button name='state' value='rejected'>Reject</button>"
            "<button name='state' value='pending'>Clear decision</button></div>"
        )
        +
        "<p><label>Your name <input name='comment_author' value='Reviewer'></label></p>"
        "<p><label>Add a shared comment<br>"
        "<textarea class='comment-box' name='comment'></textarea></label></p>"
        "<button type='submit'>Save review</button></form>"
    )
    return _layout(f"Review {record.item_id}", body)


def run_block_typecheck(root: Path, block_id: str, records: list[AgdaReviewRecord]):
    matches = [record for record in records if record.block_id == block_id]
    if not matches:
        raise ValueError(f"Agda block not found: {block_id}")
    if matches[0].provenance_kind == "missing":
        raise ValueError("There is no candidate Agda code to check")
    return run_typecheck(root, matches[0].destination)


def make_handler(root: Path, token: str = ""):
    record_cache = {"stamp": None, "records": None}

    def input_stamp():
        paths = [
            root / "data" / "project-layout.json",
            root / "data" / "rosetta-files.json",
            root / "data" / "agda-blocks.json",
            root / "data" / "agda-coverage.json",
            root / "data" / "agda-gaps.json",
            root / "data" / "agda-reviews.json",
        ]
        paths.extend(active_files(root))
        return tuple(
            (str(path), path.stat().st_mtime_ns, path.stat().st_size)
            for path in paths if path.exists()
        )

    def review_records():
        stamp = input_stamp()
        if record_cache["records"] is None or record_cache["stamp"] != stamp:
            record_cache["records"] = discover_agda_reviews(root)
            record_cache["stamp"] = stamp
        return record_cache["records"]

    def invalidate_records():
        record_cache["records"] = None

    class ReviewHandler(BaseHTTPRequestHandler):
        def _send(self, status: int, content: str, content_type: str = "text/html; charset=utf-8"):
            encoded = content.encode()
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(encoded)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(encoded)

        def do_GET(self):
            try:
                records = review_records()
                path = urlparse(self.path).path
                if path == "/":
                    files = active_files(root)
                    self._send(200, render_index(
                        records, len(files),
                        sum(record.provenance_kind == "missing" for record in records),
                    ))
                    return
                if path == "/missing-agda":
                    self._send(200, render_missing_agda(discover_missing_agda(root)))
                    return
                if path == "/read":
                    self._send(200, render_file_index(active_files(root)))
                    return
                if path.startswith("/read/"):
                    name = unquote(path.removeprefix("/read/"))
                    file_path = active_file(root, name)
                    file_records = [
                        record for record in records if record.destination == name
                    ]
                    self._send(
                        200,
                        render_file_reader(
                            name,
                            file_path.read_text(),
                            file_records,
                        ),
                    )
                    return
                if path.startswith("/agda/"):
                    block_id = unquote(path.removeprefix("/agda/"))
                    ids = [record.block_id for record in records]
                    if block_id not in ids:
                        self._send(404, _layout("Not found", "<p>Agda block not found.</p>"))
                        return
                    index = ids.index(block_id)
                    self._send(200, render_record(
                        records[index], ids[index - 1] if index else "",
                        ids[index + 1] if index + 1 < len(ids) else "", token,
                    ))
                    return
                self._send(404, _layout("Not found", "<p>Page not found.</p>"))
            except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as error:
                self._send(500, _layout("Review error", f"<p>{html.escape(str(error))}</p>"))

        def do_POST(self):
            path = urlparse(self.path).path
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length > 5_000_000:
                    raise ValueError("Review form is too large")
                form = parse_qs(self.rfile.read(length).decode(), keep_blank_values=True)
                if form.get("token", [""])[0] != token:
                    raise ValueError("This review page has expired; reload it and try again")
                if path.startswith("/agda/") and path.endswith("/typecheck"):
                    block_id = unquote(
                        path.removeprefix("/agda/").removesuffix("/typecheck")
                    )
                    records = review_records()
                    run_block_typecheck(root, block_id, records)
                    invalidate_records()
                    self._redirect("/agda/" + quote(block_id))
                    return
                if path.startswith("/agda/"):
                    block_id = unquote(path.removeprefix("/agda/"))
                    records = review_records()
                    matches = [
                        record for record in records if record.block_id == block_id
                    ]
                    if not matches:
                        raise ValueError(f"Agda block not found: {block_id}")
                    state = form.get("state", [None])[0]
                    comment = form.get("comment", [""])[0].strip() or None
                    comment_author = form.get("comment_author", ["Reviewer"])[0]
                    if state is None and comment is None:
                        raise ValueError("Choose a decision or enter a comment")
                    update_agda_review(
                        root, block_id, state=state, comment=comment,
                        comment_author=comment_author,
                        current_record=matches[0],
                    )
                    store = load_agda_review_store(
                        root / "data" / "agda-reviews.json"
                    )
                    record_cache["records"] = [
                        _with_stored_review(record, store)
                        if record.block_id == block_id
                        else record
                        for record in records
                    ]
                    record_cache["stamp"] = input_stamp()
                    self._redirect("/agda/" + quote(block_id))
                    return
                self._send(404, _layout("Not found", "<p>Page not found.</p>"))
            except (OSError, ValueError, RuntimeError) as error:
                self._send(400, _layout("Could not save review", f"<p>{html.escape(str(error))}</p>"))

        def _redirect(self, location: str):
            self.send_response(303)
            self.send_header("Location", location)
            self.end_headers()

        def log_message(self, format, *args):
            return

    return ReviewHandler


def serve_review(root: Path, host: str = "127.0.0.1", port: int = 8765) -> None:
    if host not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("The review interface may only listen on this computer")
    server = ThreadingHTTPServer((host, port), make_handler(root, secrets.token_urlsafe(24)))
    print(f"Review interface: http://{host}:{server.server_port}/")
    print("Press Ctrl-C to stop it.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
