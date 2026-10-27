#!/usr/bin/env python3
"""Delegate current read-only release validation to the complete evidence checker."""
from pathlib import Path
import subprocess,sys
if __name__=='__main__':
    root=Path(__file__).resolve().parent
    raise SystemExit(subprocess.call([sys.executable,'-B',str(root/'scripts/check_release_evidence.py'),*sys.argv[1:]]))
