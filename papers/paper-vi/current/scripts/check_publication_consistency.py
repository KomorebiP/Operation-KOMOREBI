#!/usr/bin/env python3
"""Delegate current release consistency to the read-only release verifier.

The dated October9 implementation and its evidence remain in provenance.
"""
from pathlib import Path
import subprocess
import sys

if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    raise SystemExit(subprocess.call([sys.executable, '-B', str(root / 'scripts/verify_release.py'), *sys.argv[1:]]))
