#!/usr/bin/env python3
"""Bounded discovery of a signed Fermat-packet transfer certificate.

Requires NumPy and SciPy. Solver arithmetic is floating-point; output is accepted
only after an integer incidence check. An optimizer timeout is inconclusive.
The fixed, solver-independent certificate is replayed by ../checks/verify.py.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import platform
import time

ROOT = Path(__file__).resolve().parents[1]
M = 210
SOURCE = (3, 60, 72, 126, 183, 186)
TARGET = (2, 9, 129, 142, 168, 180)


def generators():
    rows = [('pair', tuple(sorted((k, M-k)))) for k in range(1, M//2+1)]
    for p in (2, 3, 5, 7):
        d = M//p
        for k in range(1, d):
            a = [(k+j*d) % M for j in range(p)] + [(-p*k) % M]
            if p == 2:
                a.append(M//2)
            if all(a):
                rows.append((f'standard{p}', tuple(sorted(a))))
    return list(dict.fromkeys(rows))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seconds', type=float, default=15.0)
    parser.add_argument('--coefficient-bound', type=int, default=15)
    parser.add_argument('--out', type=Path, default=ROOT/'discovery/rediscovered_transfer.json')
    args = parser.parse_args()
    if not math.isfinite(args.seconds) or args.seconds <= 0 or args.coefficient_bound <= 0:
        parser.error('time and coefficient bound must be positive and finite')
    try:
        import numpy as np
        import scipy
        from scipy.optimize import Bounds, LinearConstraint, milp
    except ImportError as exc:
        parser.error(f'discovery requires NumPy and SciPy: {exc}')
    start = time.perf_counter()
    packets = generators()
    V = np.zeros((M-1, len(packets)), dtype=np.int64)
    for j, (_, a) in enumerate(packets):
        for x in a:
            V[x-1, j] += 1
    wanted = Counter(TARGET)
    wanted.subtract(Counter(SOURCE))
    rhs = np.array([wanted[r] for r in range(1, M)], dtype=np.int64)
    mat = np.concatenate((V, -V), axis=1).astype(float)
    result = milp(np.ones(mat.shape[1]), integrality=np.ones(mat.shape[1]),
                  bounds=Bounds(0, args.coefficient_bound),
                  constraints=LinearConstraint(mat, rhs, rhs),
                  options={'time_limit': args.seconds, 'mip_rel_gap': 0.0})
    record = {
        'm': M, 'source': SOURCE, 'target': TARGET,
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'python': platform.python_version(), 'numpy': np.__version__, 'scipy': scipy.__version__,
        'runtime_seconds': time.perf_counter()-start,
        'time_limit_seconds': args.seconds, 'coefficient_bound': args.coefficient_bound,
        'generator_count': len(packets), 'solver_status': int(result.status),
        'solver_message': str(result.message), 'verified_exact': False,
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'nonclaims': ['No global minimality among arbitrary geometric constructions.',
                      'No theorem proof from numerical solver status.',
                      'All unused discovered generators need their own geometric justification.']
    }
    if result.x is None:
        record['interpretation'] = 'INCONCLUSIVE: no candidate returned under the stated resource limits'
        exit_code = 2
    else:
        coeffs = [int(round(float(result.x[j]-result.x[j+len(packets)])))
                  for j in range(len(packets))]
        cert = [{'coefficient': c, 'type': packets[j][0], 'packet': packets[j][1]}
                for j, c in enumerate(coeffs) if c]
        observed = Counter()
        for row in cert:
            for residue in row['packet']:
                observed[residue] += row['coefficient']
        exact = all(observed[r] == wanted[r] for r in range(1, M))
        record.update(certificate=cert, verified_exact=exact,
                      solver_objective=float(result.fun), signed_l1=sum(abs(c) for c in coeffs))
        record['interpretation'] = ('EXACT INCIDENCE CERTIFICATE FOUND' if exact else
                                    'REJECTED: rounded numerical candidate failed integer replay')
        exit_code = 0 if exact else 1
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(record, indent=2)+'\n')
    print(record['interpretation'])
    print('Output:', args.out)
    return exit_code


if __name__ == '__main__':
    raise SystemExit(main())
