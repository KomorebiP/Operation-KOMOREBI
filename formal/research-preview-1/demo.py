#!/usr/bin/env python3
"""Finite reference demo, not a proof and not the minimal-realization compiler."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import platform
import time
from pathlib import Path

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--count', type=int, default=32, help='coefficients per mask, 1..256')
    parser.add_argument('--output', type=Path, help='optional new JSON receipt')
    args = parser.parse_args()
    if not 1 <= args.count <= 256:
        parser.error('--count must be between 1 and 256')
    root = Path(__file__).resolve().parent
    ref = root / 'padic/verification/reference/audit_finite_cartier.py'
    spec = importlib.util.spec_from_file_location('cartier_reference', ref)
    if spec is None or spec.loader is None:
        raise RuntimeError('Cannot load included reference module')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    started = time.monotonic()
    rows = []
    for p, r, a, b in [(2, 2, [1], [1, -1]), (2, 4, [1], [1, 4]), (3, 3, [1], [1, 9])]:
        machine = module.Machine(p, r, a, b)
        expected = module.recurrence_coefficients(p, p**r, a, b, args.count)
        actual = [machine.coefficient(n) for n in range(args.count)]
        for n, (x, y) in enumerate(zip(actual, expected, strict=True)):
            if x != y:
                raise AssertionError(f'Mismatch at p={p}, r={r}, index={n}: {x} != {y}')
        rows.append({'p': p, 'r': r, 'A_ascending': a, 'B_ascending': b,
                     'modulus': p**r, 'sufficient_layers': machine.L,
                     'sufficient_numerator_degree': machine.D,
                     'coefficients': actual})
    result = {
        'status': 'PASS', 'scope': 'Finite integer/modular reference comparison only.',
        'scalar_coefficient_comparisons': len(rows) * args.count,
        'input_cases': rows, 'python': platform.python_version(),
        'reference_sha256': hashlib.sha256(ref.read_bytes()).hexdigest(),
        'seconds': time.monotonic() - started,
        'non_claims': ['No universal proof from this run.', 'No minimal-state compiler is exercised.',
                      'No formal Python-to-Lean executable refinement.', 'No runtime speed claim.'],
    }
    text = json.dumps(result, indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding='utf-8')
    print(text, end='')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
