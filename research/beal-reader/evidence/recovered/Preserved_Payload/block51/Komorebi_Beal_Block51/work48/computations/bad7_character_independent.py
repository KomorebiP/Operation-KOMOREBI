#!/usr/bin/env python3
"""Fresh exhaustive q=11,19 recount using square multiplicities, no orbit reduction."""
import itertools
import json
from collections import Counter
from pathlib import Path


def mul(z, w, p):
    return ((z[0]*w[0]-z[1]*w[1]) % p,
            (z[0]*w[1]+z[1]*w[0]) % p)


def count(A, B, p, degree):
    field = [(a, b) for a in range(p)
             for b in (range(p) if degree == 2 else [0])]
    squares = Counter(mul(z, z, p) for z in field)
    n = 2  # two rational points at infinity, leading coefficient one
    for z in field:
        z3 = mul(mul(z, z, p), z, p)
        z6 = mul(z3, z3, p)
        value = ((z6[0]+10*B*z3[0]+12*A*z[0]+5*B*B) % p,
                 (z6[1]+10*B*z3[1]+12*A*z[1]) % p)
        n += squares[value]
    return n


def main():
    # Quotient map of the ambient ray group onto C4 x C2.
    ambient = list(itertools.product(range(8), range(4), range(2), range(2)))
    quotient = lambda z: ((-z[0]+z[1]+2*z[2]) % 4,
                         (-z[0]+z[2]+z[3]) % 2)
    unit_image = {((4*e+k) % 8, (2*e+k) % 4, e % 2, (e+k) % 2)
                  for e in range(2) for k in range(8)}
    kernel = {z for z in ambient if quotient(z) == (0, 0)}
    assert kernel == unit_image and len(kernel) == 16
    assert len({quotient(z) for z in ambient}) == 8
    assert quotient((4, 3, 0, 0)) == (3, 0)

    prior = json.loads(Path('work48/verification/character_sieve_run/result.json').read_text())
    results = []
    for p, value in ((11, 1), (19, -1)):
        assert p % 4 == 3  # i^2=-1 defines F_(p^2).
        entry = next(row for row in prior['prime_checks'] if row['q'] == p)
        expected = {}
        for row in entry['orbits']:
            for u in range(1, p):
                pair = (row['A']*pow(u, 5, p) % p, row['B']*pow(u, 3, p) % p)
                expected[pair] = row['Pq']
        pairs = []
        for A, B in itertools.product(range(p), repeat=2):
            if (A**3+B**5) % p == 0:
                continue
            n1, n2 = count(A, B, p, 1), count(A, B, p, 2)
            t = p+1-n1
            c2numer = t*t-(p*p+1-n2)
            assert c2numer % 2 == 0
            poly = [p*p, -p*t, c2numer//2, -t, 1]
            assert poly == expected[(A, B)], (p, A, B)
            evaluation = sum(a*value**i for i, a in enumerate(poly)) % 7
            assert evaluation != 0, (p, A, B)
            pairs.append({'A': A, 'B': B, 'N1': n1, 'N2': n2,
                          'Pq': poly, 'Pq_at_character_mod7': evaluation})
        assert len(pairs) == p*p-p
        node_roots = [r for r in range(p) if (r*r+r-1) % p == 0]
        branch_values = [(6-3*r) % p for r in node_roots]
        prime_squares = {a*a % p for a in range(p)}
        assert len(node_roots) == 2 and all(h not in prime_squares for h in branch_values)
        results.append({'q': p, 'character_value': value, 'pairs': pairs,
                        'node_roots': node_roots, 'branch_values': branch_values})
    result = {'status': 'PASS_INDEPENDENT_EXHAUSTIVE_452_RECOUNT',
              'method': 'Direct square-multiplicity enumeration in Fq and Fq[i]/(i^2+1), every smooth pair; expanded sextic, no Horner or weighted-orbit count reuse.',
              'ray_quotient_order': 8, 'unit_kernel_order': 16, 'rows': results,
              'scope': 'Verifies finite counts, root exclusions, and finite ray quotient only. The global character contract and geometric Frobenius interpretation require the written proofs.'}
    Path('work48/verification/bad7_character_audit_run/result.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({'status': result['status'], 'smooth_pairs': sum(len(r['pairs']) for r in results)}))


if __name__ == '__main__':
    main()
