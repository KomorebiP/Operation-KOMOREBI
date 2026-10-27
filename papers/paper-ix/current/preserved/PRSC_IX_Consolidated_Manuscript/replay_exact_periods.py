#!/usr/bin/env python3
"""Reproduce the complete prior release, native continuation, and dyadic sharpening."""
import argparse
from pathlib import Path
import subprocess
import sys

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--kit', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True, help='New directory')
    a = p.parse_args()
    root = Path(__file__).resolve().parent
    output = a.output.resolve()
    kit = a.kit.resolve()
    result = subprocess.run([sys.executable, str(root/'review/replay_review.py'),
                             '--kit', str(kit), '--output', str(output)])
    if result.returncode: return result.returncode
    baseline = output/'PRSC_IX_v0.11.0_Nishibuchi_Completion'
    builds = sorted((baseline/'verification/runs').glob('*/build'))
    if not builds: raise RuntimeError('No fresh baseline build found')
    return subprocess.run([sys.executable, str(root/'strengthening/scripts/verify_strengthening.py'),
         '--kit', str(kit), '--baseline-root', str(baseline), '--baseline-build', str(builds[-1]),
         '--output', str(output/'dyadic_continuation')]).returncode

if __name__ == '__main__':
    raise SystemExit(main())
