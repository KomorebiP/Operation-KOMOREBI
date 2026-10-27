#!/usr/bin/env python3
"""Exact finite Frobenius certificates. Python >= 3.10, standard library only.

The norm-character counting method adapts the frozen Block 47 implementation.
This is NOT the independent implementation; see independent_pointcounts.py.
All equation residues are filtered per pair, not per weighted-orbit representative.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path

PRIMES = (13, 29, 43, 71)

def require(test: bool, message: str) -> None:
    if not test:
        raise AssertionError(message)

def prime(q: int) -> bool:
    return q >= 2 and all(q % d for d in range(2, __import__('math').isqrt(q)+1))

def character(a: int, q: int) -> int:
    t = pow(a % q, (q-1)//2, q)
    return -1 if t == q-1 else t

def valuation7(a: int) -> int:
    if a <= 0:
        raise ValueError('A group order must be positive; zero is not a finite valuation.')
    v = 0
    while a % 7 == 0:
        a //= 7
        v += 1
    return v

def count(A: int, B: int, q: int) -> tuple[int, int, list[int]]:
    d = next(z for z in range(2, q) if character(z, q) == -1)
    coefficients = (1, 0, 0, 10*B, 0, 12*A, 5*B*B)
    Ns = []
    for degree in (1, 2):
        total = 0
        for x in range(q):
            for y in range(q if degree == 2 else 1):
                a = b = 0
                for c in coefficients:
                    a, b = (a*x+d*b*y+c) % q, (a*y+b*x) % q
                total += character(a*a-d*b*b, q) if degree == 2 else character(a, q)
        Ns.append(q**degree + total + 2)  # two rational points at infinity
    s1 = q+1-Ns[0]
    numerator = s1*s1-q*q-1+Ns[1]
    require(numerator % 2 == 0, 'Nonintegral second Frobenius coefficient')
    s2 = numerator//2
    return Ns[0], Ns[1], [q*q, -q*s1, s2, -s1, 1]

def derived(q: int, P: list[int]) -> dict:
    f = 1 if q % 5 in (1, 4) else 2
    Q = q**f
    cm = 1 if Q % 5 == 1 else -1
    nu = cm * character(-3, q)**f
    s1, s2 = -P[3], P[2]
    if f == 2:
        s1, s2 = s1*s1-2*s2, s2*s2-2*q*s1*s1+2*q*q
    twisted = [Q*Q, -nu*Q*s1, s2, -nu*s1, 1]
    target = [Q*Q, -2*Q*(Q+1), (Q+1)**2+2*Q, -2*(Q+1), 1]
    order = sum(twisted)
    return {'f': f, 'Q': Q, 'nu': nu, 'twisted_polynomial': twisted,
            'jacobian_order': order, 'v7_order': valuation7(order),
            'residual_match': all((a-b) % 7 == 0 for a,b in zip(twisted, target))}

def run_prime(q: int) -> dict:
    require(prime(q) and q not in (2,3,5,7), 'Unsupported prime')
    smooth = {(A,B) for A in range(q) for B in range(q) if (A**3+B**5) % q != 0}
    seventh = {pow(c,7,q) for c in range(1,q)}
    expected_pairs = {(A,B) for A,B in smooth if (A**3+B**5) % q in seventh}
    unseen, covered, rows = set(smooth), set(), []
    wrong_coverage = set()
    full_orbits = 0
    while unseen:
        A,B = min(unseen)
        orbit = {(A*pow(u,5,q)%q, B*pow(u,3,q)%q) for u in range(1,q)}
        require(orbit <= unseen, 'Weighted orbits overlap or leave smooth set')
        unseen -= orbit
        full_orbits += 1
        if (A**3+B**5) % q in seventh:
            wrong_coverage |= orbit  # preserved only as a negative control
        admissible = sorted(pair for pair in orbit if pair in expected_pairs)
        if not admissible:
            continue
        n1,n2,P = count(A,B,q)
        info = derived(q,P)
        rows.append({'representative': [A,B], 'orbit_size': len(orbit),
                     'admissible_pairs': [list(x) for x in admissible],
                     'N1': n1, 'N2': n2, 'Pq_ascending': P, **info})
        require(not (covered & set(admissible)), 'Duplicate admissible pair')
        covered.update(admissible)
    require(covered == expected_pairs, 'Incomplete exact equation coverage')
    histogram = Counter()
    matches = []
    for r in rows:
        histogram[r['v7_order']] += len(r['admissible_pairs'])
        if r['residual_match']:
            matches.extend(r['admissible_pairs'])
    matches.sort()
    facts = derived(q, rows[0]['Pq_ascending'])
    if q == 13:
        require(matches == [[0,1],[0,5],[0,8],[0,12]], 'Unexpected good-13 residues')
        for r in rows:
            if r['residual_match']:
                require(r['Pq_ascending'] == [169,0,-26,0,1], 'Good-13 polynomial')
                require(r['jacobian_order'] == 14**4, 'Good-13 twisted order')
    if q in (29,43):
        require(max(histogram) < 4, 'Depth obstruction failed')
    if q == 71:
        require(not matches and max(histogram) == 0, 'Prime-71 exclusion failed')
    if q in (29,43,71):
        require(wrong_coverage != expected_pairs, 'Orbit-filter negative control missed')
    return {'q':q, 'f':facts['f'], 'Q':facts['Q'], 'nu':facts['nu'],
            'smooth_pairs':len(smooth), 'full_orbits': full_orbits,
            'admissible_pairs':len(expected_pairs), 'counted_orbits':len(rows),
            'valuation_histogram_pairs':dict(sorted(histogram.items())),
            'residual_pairs':matches,
            'wrong_representative_filter':{
                'returned_pairs':len(wrong_coverage),
                'false_positives':len(wrong_coverage-expected_pairs),
                'false_negatives':len(expected_pairs-wrong_coverage)},
            'rows':rows}

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    data = {'schema':1, 'method':'quadratic character via norm; weighted orbits with memberwise equation filter',
            'coefficient_order':'ascending, constant coefficient first',
            'primes':[run_prime(q) for q in PRIMES]}
    data['status'] = 'PASS'
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps({'status':'PASS','counted_orbits':sum(p['counted_orbits'] for p in data['primes']),
                      'admissible_pairs':sum(p['admissible_pairs'] for p in data['primes'])}))

if __name__ == '__main__':
    main()
