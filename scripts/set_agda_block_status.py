#!/usr/bin/env python3
"""Set conversion status for selected manifest blocks."""

import argparse
import json
from pathlib import Path


parser = argparse.ArgumentParser()
parser.add_argument("manifest", type=Path)
parser.add_argument("status", choices=("ready", "blocked"))
parser.add_argument("note")
parser.add_argument("block_ids", nargs="+")
args = parser.parse_args()

manifest = json.loads(args.manifest.read_text())
selected = set(args.block_ids)
found = set()
for block in manifest["blocks"]:
    if block["block_id"] in selected:
        block["conversion_status"] = args.status
        block["conversion_note"] = args.note if args.status == "blocked" else ""
        found.add(block["block_id"])
missing = selected - found
if missing:
    parser.error("unknown block IDs: " + ", ".join(sorted(missing)))
args.manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
