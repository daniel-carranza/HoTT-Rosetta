#!/usr/bin/env python3
"""Friendly command-line entry point when run from converter/."""

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))

from rosetta.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
