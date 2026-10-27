#!/usr/bin/env python3
"""Delegate the documented publication CLI to the current packaged builder."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

if __name__ == '__main__':
    raise SystemExit(subprocess.run(
        [sys.executable, str(ROOT / 'scripts/build_pdfs.py'), *sys.argv[1:]]
    ).returncode)
