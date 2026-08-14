#!/usr/bin/env python3
"""Append one provenance-pinned upstream range to an Agda block manifest."""

import argparse
import hashlib
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("source_root", type=Path)
    parser.add_argument("source_file")
    parser.add_argument("start", type=int)
    parser.add_argument("end", type=int)
    parser.add_argument("block_id")
    parser.add_argument("item_id")
    parser.add_argument("destination")
    parser.add_argument("--commit", required=True)
    parser.add_argument("--order", type=int, default=0)
    parser.add_argument("--imports", nargs="*", default=[])
    parser.add_argument("--replace", action="append", default=[])
    args = parser.parse_args()

    source = args.source_root / args.source_file
    lines = source.read_text().splitlines(keepends=True)
    selected = "".join(lines[args.start - 1 : args.end])
    code = selected.rstrip("\n")
    for replacement in args.replace:
        old, separator, new = replacement.partition("=")
        if not separator:
            parser.error("--replace values must have the form OLD=NEW")
        code = code.replace(old, new)

    manifest = json.loads(args.manifest.read_text())
    if any(block["block_id"] == args.block_id for block in manifest["blocks"]):
        parser.error(f"duplicate block ID: {args.block_id}")
    exact = code == selected.rstrip("\n")
    block = {
        "block_id": args.block_id,
        "provenance_kind": "exact" if exact else "adapted",
        "item_id": args.item_id,
        "destination": args.destination,
        "source_file": args.source_file,
        "source_commit": args.commit,
        "source_start_line": args.start,
        "source_end_line": args.end,
        "source_sha256": hashlib.sha256(selected.encode()).hexdigest(),
        "order": args.order,
        "imports": args.imports,
        "code": code,
    }
    if not exact:
        block["source_note"] = (
            "Copied from the pinned source with only the requested local substitutions."
        )
    manifest["blocks"].append(block)
    args.manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
