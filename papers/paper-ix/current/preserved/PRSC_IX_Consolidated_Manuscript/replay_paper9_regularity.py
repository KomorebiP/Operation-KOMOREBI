#!/usr/bin/env python3
"""Replay the fresh analytic regularity gate with the separately supplied pinned kit."""
import argparse
from pathlib import Path
import subprocess
import sys
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--kit', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
script = Path(__file__).resolve().parent / 'polynomial_regularity/scripts/verify_polynomial_regularity.py'
raise SystemExit(subprocess.run([sys.executable, str(script), '--kit', str(args.kit.resolve()),
    '--output', str(args.output.resolve())]).returncode)
