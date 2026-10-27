#!/usr/bin/env python3
"""Independent point counts for the two trace-zero implications.

Uses F_(q^2) quadratic characters via the norm to F_q, rather than
enumerating squares in the extension field. Counts every smooth pair at
both primes, rather than orbit representatives at 19.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def char(a, q):
    t = pow(a % q, (q-1)//2, q)
    return -1 if t == q-1 else t


def count_poly(A, B, q):
    d = next(t for t in range(2, q) if char(t, q) == -1)
    coeffs = (1, 0, 0, 10*B, 0, 12*A, 5*B*B)
    sums = []
    for degree in (1, 2):
        total = 0
        for x in range(q):
            for y in range(q if degree == 2 else 1):
                a = b = 0
                for c in coeffs:
                    a, b = (a*x + d*b*y + c) % q, (a*y + b*x) % q
                total += char(a*a-d*b*b, q) if degree == 2 else char(a, q)
        sums.append(q**degree + total + 2)
    n1, n2 = sums
    t1 = q+1-n1
    numerator = t1*t1-q*q-1+n2
    assert numerator % 2 == 0
    t2 = numerator//2
    return [q*q, -q*t1, t2, -t1, 1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT/'verification/modular_independent_pointcounts.json')
    args = parser.parse_args()
    input_path = ROOT/'verification/modular_correlations.json'
    imported = json.loads(input_path.read_text())
    expected11 = {(r['A'], r['B']): r['jacobian_frobenius_polynomial']
                  for r in imported['q11_complete_smooth_Beal_point_counts']}
    expected19 = {}
    for r in imported['q19_weighted_orbit_point_counts']['orbits']:
        for u in range(1, 19):
            pair = (r['A']*pow(u, 5, 19) % 19, r['B']*pow(u, 3, 19) % 19)
            expected19[pair] = r['jacobian_frobenius_polynomial']
    out = {'status': 'independent_complete_point_counts_agree',
           'input_sha256': hashlib.sha256(input_path.read_bytes()).hexdigest(),
           'method': 'extension-field quadratic character through its norm to F_q',
           'checks': []}
    for q, expected in ((11, expected11), (19, expected19)):
        pairs = [(A, B) for A in range(q) for B in range(q) if (A**3+B**5) % q]
        matches = []
        for A, B in pairs:
            poly = count_poly(A, B, q)
            assert poly == expected[A, B], (q, A, B, poly, expected[A, B])
            if [c % 7 for c in poly] == [q*q % 7, 0, 2*q % 7, 0, 1]:
                matches.append([A, B])
        predicted = [[A, B] for A, B in pairs if (A == 0 if q == 11 else B == 0)]
        assert matches == predicted
        rvalues = [r for r in range(q) if (r*r+r-1) % q == 0]
        branch_signs = [char(6-3*r, q) for r in rvalues]
        assert len(rvalues) == 2 and branch_signs[0] == branch_signs[1] != 0
        out['checks'].append({'q': q, 'all_smooth_pairs': len(pairs),
                              'full_polynomial_matches': matches,
                              'multiplicative_node_roots': rvalues,
                              'multiplicative_branch_characters': branch_signs,
                              'q_plus_one_mod7': (q+1) % 7})
    dest = args.output
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2)+'\n')
    print(json.dumps({'status':out['status'], 'checked_pairs':sum(r['all_smooth_pairs'] for r in out['checks'])}))


if __name__ == '__main__':
    main()
