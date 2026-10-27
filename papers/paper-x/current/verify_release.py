#!/usr/bin/env python3
"""Strict frozen-release membership and SHA-256 verification; no proof replay."""
from pathlib import Path
import runpy
if __name__ == '__main__':
    runpy.run_path(str(Path(__file__).resolve().parent/'scripts/verify_integrity.py'),run_name='__main__')
