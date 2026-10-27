#!/usr/bin/env python3
"""Build the current monograph and both companions from their authored sources."""
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
raise SystemExit(subprocess.call([sys.executable,str(ROOT/'scripts/build_pdfs.py'),*sys.argv[1:]],cwd=ROOT))
