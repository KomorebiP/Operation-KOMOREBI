#!/usr/bin/env python3
"""Audit delivered arrays without rerunning the expensive ODE study.

Exit 0 means reproducibility checks agree with the recorded results.
It does NOT mean the physical model passes. --require-physics returns 3
when the recorded depth-independence test remains failed.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--require-physics', action='store_true')
    args = ap.parse_args()
    data = ROOT / 'results/final'
    rows = json.loads((data / 'dynamics.json').read_text())
    verification = json.loads((data / 'verification.json').read_text())
    if len(rows) != 17:
        raise AssertionError(f'Expected 17 configurations, found {len(rows)}')
    original_hash = hashlib.sha256((ROOT/'inputs/frozen_benchmark.json').read_bytes()).hexdigest()
    if original_hash != verification['source_sha256']:
        raise AssertionError('Frozen input differs from verified input')
    discrepancies = []
    for i, row in enumerate(rows):
        with np.load(data/f'run_{i:02d}.npz', allow_pickle=False) as a:
            t, q, v, modes, kinetic = [a[k] for k in ('t', 'q', 'velocity', 'modes', 'kinetic')]
            if not np.all(np.isfinite(q)) or not np.all(np.diff(t)>0):
                raise AssertionError(f'Invalid sampled path in run {i}')
            if not np.allclose(kinetic, v*v, rtol=1e-13, atol=1e-14):
                raise AssertionError(f'Inconsistent kinetic energy in run {i}')
            values = {
                'energy_residual': float(np.max(np.abs(kinetic+modes-1))),
                'maximum_mode_energy_fraction': float(modes.max()),
                'final_mode_energy_fraction': float(modes[-1]),
                'final_q': float(q[-1]),
                'final_velocity': float(v[-1]),
            }
            for key, actual in values.items():
                if not np.isclose(actual, row[key], rtol=1e-11, atol=1e-13):
                    discrepancies.append({'run': i, 'field': key, 'actual': actual, 'recorded': row[key]})
    if discrepancies:
        raise AssertionError(json.dumps(discrepancies, indent=2))
    failed = [g['name'] for g in verification['gates'] if not g['pass_']]
    result = {'saved_array_audit': 'PASS', 'runs_checked': len(rows),
              'study_gates_passed': sum(g['pass_'] for g in verification['gates']),
              'study_gates_failed': failed,
              'physical_resolution_established': False}
    print(json.dumps(result, indent=2))
    if args.require_physics and failed:
        raise SystemExit(3)

if __name__ == '__main__':
    main()
