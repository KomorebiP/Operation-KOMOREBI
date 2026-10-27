#!/usr/bin/env python3
"""Replay exact polynomial lift counts, optionally after all preserved active blocks."""
import argparse
from pathlib import Path
import subprocess
import sys
root=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--kit',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
parser.add_argument('--all',action='store_true')
args=parser.parse_args()
output=args.output.resolve()
if output.exists():parser.error('--output must not exist')
output.mkdir(parents=True)
if args.all:
    subprocess.run([sys.executable,str(root/'replay_paper9.py'),'--all',
      '--kit',str(args.kit.resolve()),'--output',str(output/'preserved')],check=True)
subprocess.run([sys.executable,str(root/'polynomial_counts/scripts/verify_polynomial_counts.py'),
  '--kit',str(args.kit.resolve()),'--output',str(output/'counts')],check=True)
