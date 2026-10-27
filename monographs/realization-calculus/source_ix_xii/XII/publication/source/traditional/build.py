#!/usr/bin/env python3
"""Compatibility entry point: rebuild all three synchronized readers."""
import argparse, subprocess, sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--output-dir', '--output', dest='output',type=Path,required=True);a=p.parse_args()
root=Path(__file__).resolve().parents[3]
raise SystemExit(subprocess.call([sys.executable,str(root/'tools/build_readers.py'),'--output',str(a.output)]))
