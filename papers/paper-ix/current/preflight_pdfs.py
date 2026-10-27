#!/usr/bin/env python3
"""Run the current publication's metadata, navigation, and bounds checker."""
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parent
if __name__=='__main__':
    raise SystemExit(subprocess.call([sys.executable,str(ROOT/'tools/check_publication.py')]+sys.argv[1:]))
