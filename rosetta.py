#!/usr/bin/env python3
"""Repository-root compatibility entry point for the converter."""

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "converter"))

from rosetta.cli import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
