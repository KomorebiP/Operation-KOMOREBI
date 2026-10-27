#!/usr/bin/env python3
"""Run the deterministic numerical replay from the package root."""
from pathlib import Path
import subprocess, sys
ROOT=Path(__file__).resolve().parent
if __name__=='__main__':
    raise SystemExit(subprocess.call([sys.executable,str(ROOT/'verification/numerical/replay.py'),*sys.argv[1:]],cwd=ROOT))
