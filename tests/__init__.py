"""Tests for the conversion tools."""
"""Test package bootstrap for the converter source tree."""

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "converter"))
