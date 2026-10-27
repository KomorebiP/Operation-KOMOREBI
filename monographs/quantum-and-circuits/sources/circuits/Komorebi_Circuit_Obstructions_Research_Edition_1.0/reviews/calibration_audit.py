"""Bounded adversarial C03/C04 audit; source helpers and constructors are reused."""
from pathlib import Path
import argparse
import hashlib
import json
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--source', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
args = parser.parse_args()
sys.dont_write_bytecode = True
sys.path.insert(0, str(args.source / 'checks'))
from truth_tables import profile, affine_masks
from reversible import degree, validate
from verify_completeness import optimal_small

results = []
for n in (4, 5, 6):
    f = sum(int(bool(x & 1 and x & 2) or (x >> 2) == (1 << (n - 2)) - 1) << x
            for x in range(1 << n))
    values = [profile(f ^ ell, n) for ell in affine_masks(n)]
    maximum = max(a for a, b in values), max(b for a, b in values)
    assert maximum == (3, n - 1)
    results.append({'n': n, 'affine_masks': len(values),
                    'max_alpha': maximum[0], 'max_beta': maximum[1]})

counts = {0: 0, 1: 0, 3: 0}
cases = 0
for n in (1, 2, 3):
    for f in range(1 << (1 << n)):
        ops, width, y, t = optimal_small(f, n)
        validate(ops, width)
        assert sum(g[0] == 'T' for g in ops) == t
        for x in range(1 << n):
            for y0 in (0, 1):
                state = [(x >> i) & 1 for i in range(n)] + [0] * (width - n)
                state[y] = y0
                expected = state[:]
                # Fresh scalar gate interpreter, separate from source bit-sliced trace.
                for gate in ops:
                    if gate[0] == 'N':
                        state[gate[1]] ^= 1
                    elif gate[0] == 'C':
                        state[gate[2]] ^= state[gate[1]]
                    else:
                        state[gate[3]] ^= state[gate[1]] & state[gate[2]]
                expected[y] ^= (f >> x) & 1
                assert state == expected
                cases += 1
        counts[t] += 1
        bstar = max(profile(f ^ ell, n)[1] for ell in affine_masks(n))
        assert t == max(0, degree(f, n) - 1, 2 * bstar - 3)

names = ('docs/THEORY.md', 'docs/FOUNDATIONS.md', 'checks/truth_tables.py',
         'checks/reversible.py', 'checks/verify_completeness.py')
output = {'status': 'PASS', 'C03_all_affine_masks': results,
          'C04_functions': sum(counts.values()), 'C04_distribution': counts,
          'C04_scalar_boundary_cases': cases,
          'arithmetic': 'exact F2 / integer bit operations',
          'command': sys.argv,
          'input_sha256': {name: hashlib.sha256((args.source / name).read_bytes()).hexdigest()
                           for name in names},
          'scope': 'Fresh scalar gate interpreter; circuit constructors/profile helper reused; original source not rewritten.'}
args.out.write_text(json.dumps(output, indent=2) + '\n')
print(json.dumps(output, indent=2))
