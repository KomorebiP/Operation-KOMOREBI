#!/usr/bin/env python3
"""Replay polynomial lifting; with --all, replay all preserved active proof blocks first."""
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
if output.exists(): parser.error('--output must not exist')
output.mkdir(parents=True)
if args.all:
    subprocess.run([sys.executable,str(root/'replay_shared_correction.py'),'--all',
        '--kit',str(args.kit.resolve()),'--output',str(output/'preserved')],check=True)
subprocess.run([sys.executable,str(root/'polynomial_lifting/scripts/verify_polynomial.py'),
    '--kit',str(args.kit.resolve()),'--output',str(output/'polynomial')],check=True)
