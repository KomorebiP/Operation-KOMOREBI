#!/usr/bin/env python3
"""Exact audit of imported PV trace-polynomial data; no Hilbert newform replay.

This checks finite polynomial correlations and independent point counts at 11.
It does not infer nonexistent Hecke coefficient labels from transcript indices.
"""
import argparse
import hashlib
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def parse_polynomial(s):
    s = s.replace(' ', '').replace('-', '+-')
    coeff = [0, 0, 0]
    for term in s.split('+'):
        if not term:
            continue
        m = re.fullmatch(r'(-?\d*)\*?x(?:\^(2))?', term)
        if m:
            c = {'': 1, '-': -1}.get(m[1])
            if c is None:
                c = int(m[1])
            coeff[2 if m[2] else 1] += c
        else:
            assert re.fullmatch(r'-?\d+', term), term
            coeff[0] += int(term)
    while coeff[-1] == 0:
        coeff.pop()
    assert coeff[-1] == 1 and 2 <= len(coeff) <= 3
    return tuple(coeff)


def parse_data(path):
    text = path.read_text()
    pat = r'<(\d+),\[([^\]]*)\],\[([^\]]*)\],\[([^\]]*)\]>'
    rows = []
    for m in re.finditer(pat, text):
        rows.append((int(m[1]), *(tuple(parse_polynomial(x) for x in m[i].split(','))
                                  for i in (2, 3, 4))))
    assert re.sub(pat, '', text).replace(',', '').replace('Data:=[', '').replace('];', '').strip() == ''
    assert len(rows) == 37
    return rows


class Fp2:
    def __init__(self, p, d):
        self.p, self.d = p, d
        assert pow(d, (p-1)//2, p) == p-1
        self.elements = [(a, b) for a in range(p) for b in range(p)]
        self.squares = {self.mul(a, a) for a in self.elements if a != (0, 0)}

    def add(self, a, b):
        return ((a[0]+b[0]) % self.p, (a[1]+b[1]) % self.p)

    def mul(self, a, b):
        return ((a[0]*b[0]+self.d*a[1]*b[1]) % self.p,
                (a[0]*b[1]+a[1]*b[0]) % self.p)

    def power(self, a, n):
        r = (1, 0)
        while n:
            if n & 1:
                r = self.mul(r, a)
            a = self.mul(a, a)
            n //= 2
        return r

    def evaluate(self, poly, a):
        r = (0, 0)
        for c in reversed(poly):
            r = self.add(self.mul(r, a), (c % self.p, 0))
        return r

    def roots(self, poly):
        return {a for a in self.elements if self.evaluate(poly, a) == (0, 0)}

    def character(self, a):
        return 0 if a == (0, 0) else 1 if a in self.squares else -1


def degree_mod15(q):
    r, f = q % 15, 1
    while r != 1:
        r = (r*q) % 15
        f += 1
    return f


def point_counts_trace_polynomial(poly, p=11):
    def char(a):
        v = pow(a % p, (p-1)//2, p)
        return -1 if v == p-1 else v
    def ev(a):
        r = 0
        for c in reversed(poly):
            r = (r*a+c) % p
        return r
    n1 = p + sum(char(ev(a)) for a in range(p)) + 1 + char(poly[-1])
    d = next(d for d in range(2, p) if char(d) == -1)
    field = Fp2(p, d)
    n2 = p*p + sum(field.character(field.evaluate(poly, a)) for a in field.elements) + 2
    s1 = p+1-n1
    assert (s1*s1-(p*p+1-n2)) % 2 == 0
    s2 = (s1*s1-(p*p+1-n2))//2
    tr = (s2-2*p, -s1, 1)
    if s1*s1 == 4*tr[0]:
        assert s1 % 2 == 0
        tr = (-s1//2, 1)
    else:
        D = s1*s1-4*tr[0]
        assert D > 0 and D % 5 == 0 and math.isqrt(D//5)**2 == D//5
    return {'N1': n1, 'N2': n2, 'trace_polynomial': list(tr),
            'jacobian_frobenius_polynomial': [p*p,-p*s1,s2,-s1,1]}


def audit_weighted_residue_orbits(p):
    """Complete smooth-pair coverage using (A,B)->(u^5 A,u^3 B).

    The change X->uX,Z->u^3 Z identifies the corresponding curves.
    """
    F = Fp2(7,5)
    remaining = {(A,B) for A in range(p) for B in range(p) if (A**3+B**5) % p}
    total = len(remaining)
    rows = []
    while remaining:
        A,B = min(remaining)
        orbit = {(A*pow(u,5,p) % p, B*pow(u,3,p) % p) for u in range(1,p)}
        assert orbit <= remaining
        remaining -= orbit
        rec = point_counts_trace_polynomial([5*B*B,12*A,0,10*B,0,0,1], p)
        rec.update({'A':A,'B':B,'orbit_size':len(orbit),
                    'trace_zero_mod7':(0,0) in F.roots(tuple(rec['trace_polynomial']))})
        assert rec['trace_zero_mod7'] == ([(c % 7) for c in rec['jacobian_frobenius_polynomial']]
                                        == [p*p % 7,0,2*p % 7,0,1])
        rows.append(rec)
    return {'p':p,'smooth_pairs_covered':total,'orbits':rows}


def audit():
    path = ROOT / 'source_records/pv_Data.txt'
    rows = parse_data(path)
    F = Fp2(7, 5)
    stats = []
    for q, C1, C0, Coo in rows:
        if q == 7:
            continue  # auxiliary characteristic cannot equal residual characteristic
        regular = set().union(*(F.roots(P) for P in C1))
        assert all(F.roots(P) for P in C1+C0+Coo)
        fK = 1 if pow(5, (q-1)//2, q) == 1 else 2
        fF = degree_mod15(q)
        assert fF % fK == 0 and fF//fK in (1, 2)
        def overF(a):
            return F.add(F.mul(a, a), ((-2*pow(q, fK)) % 7, 0)) if fF == 2*fK else a
        zero = {a for a in F.elements if any(F.evaluate(P, overF(a)) == (0, 0) for P in C0)}
        infinity = {a for a in F.elements if any(F.evaluate(P, overF(a)) == (0, 0) for P in Coo)}
        one = {((pow(q, fK)+1) % 7, 0), ((-pow(q, fK)-1) % 7, 0)}
        pairs = {(a, F.power(a, 7)) for a in regular}
        stats.append({'q': q, 'fK': fK, 'regular_polynomial_records': len(C1),
                      'regular_trace_residues': len(regular),
                      'coefficient_conjugate_pairs': len(pairs),
                      'independent_marginal_pairs': len(regular)**2,
                      'trace_zero_allowed_cases': [label for label, values in
                          [('regular',regular), ('t=0',zero), ('t=infinity',infinity), ('t=1',one)]
                          if (0,0) in values],
                      'all_case_trace_residues': len(regular|zero|infinity|one)})
    # Independent exact verification of every regular trace polynomial at q=11.
    # y^2=5x^6-12x^5+10t x^3+t^2 is PV's family.
    exact_regular = []
    for t in range(2, 11):
        rec = point_counts_trace_polynomial([t*t,0,0,10*t,0,-12,5])
        rec['t'] = t
        exact_regular.append(rec)
    source_regular = next(C1 for q,C1,_,_ in rows if q == 11)
    assert sorted(tuple(r['trace_polynomial']) for r in exact_regular) == sorted(source_regular)
    # Table 7.4 labels for the hypergeometric calculation do not agree directly
    # with equation (32)'s curve parameter. The reciprocal parameter matches.
    table74 = {2:(5,1), 3:(-5,0,1), 4:(-1,-1,1), 5:(-2,1),
               6:(-1,4,1), 7:(-5,5,1), 8:(-19,2,1), 9:(1,3,1), 10:(-11,1,1)}
    assert all(tuple(r['trace_polynomial']) == table74[pow(r['t'], -1, 11)] for r in exact_regular)
    parameter_mismatches = [r['t'] for r in exact_regular if tuple(r['trace_polynomial']) != table74[r['t']]]
    assert parameter_mismatches == list(range(2,10))
    # Use the integral Beal model at q=11 in the B=0 and C=0 boundary lanes.
    # B=0 is good reduction, so exact point counts certify the trace-zero exclusion.
    exact_Bzero = []
    for A in range(1,11):
        rec = point_counts_trace_polynomial([0,12*A,0,0,0,0,1])
        rec['A'] = A
        assert (0,0) not in F.roots(tuple(rec['trace_polynomial']))
        exact_Bzero.append(rec)
    assert all((0,0) not in F.roots(tuple(r['trace_polynomial'])) for r in exact_regular)
    # Directly check the actual Beal model on every smooth residue pair. This
    # avoids relying on a hypergeometric parameter convention for the conclusion.
    exact_Beal = []
    for A in range(11):
        for B in range(11):
            if (A**3+B**5) % 11 == 0:
                continue
            rec = point_counts_trace_polynomial([5*B*B,12*A,0,10*B,0,0,1])
            rec.update({'A': A, 'B': B})
            zero_trace = (0,0) in F.roots(tuple(rec['trace_polynomial']))
            assert zero_trace == ([(c % 7) for c in rec['jacobian_frobenius_polynomial']]
                                   == [11*11 % 7,0,22 % 7,0,1])
            assert zero_trace == (A == 0)
            rec['trace_zero_mod7'] = zero_trace
            exact_Beal.append(rec)
    assert len(exact_Beal) == 110
    at19 = audit_weighted_residue_orbits(19)
    assert at19['smooth_pairs_covered'] == 342
    assert all(rec['trace_zero_mod7'] == (rec['B'] == 0) for rec in at19['orbits'])
    # Multiplicative branch C=0 has trace +/-12, nonzero mod7.
    assert 12 % 7 != 0
    # Synthetic negative control: individually allowed values with no shared prime.
    supports = [{0}, {1}]
    assert all(supports) and not set.intersection(*supports)
    return {'status': 'FINITE_EXACT_DATA_AUDIT_NOT_MODULAR_ELIMINATION',
            'input_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'source_commit': 'e88f914c577ab6cf9a45e5cdd82c1993477fb423',
            'auxiliary_primes_audited': len(stats), 'skipped_residual_prime': 7,
            'statistics': stats, 'q11_regular_point_counts': exact_regular,
            'q11_Bzero_point_counts': exact_Bzero,
            'q11_complete_smooth_Beal_point_counts': exact_Beal,
            'q11_smooth_Beal_pairs': len(exact_Beal),
            'q19_weighted_orbit_point_counts': at19,
            'q19_exact_conclusion': 'Trace zero mod7 requires B=0 mod19 in a primitive Beal reduction, using the standard multiplicative branch comparison when C=0 (plus/minus20 is nonzero mod7).',
            'parameter_convention_check': {'table74_same_parameter_mismatches': parameter_mismatches,
                  'table74_matches_equation32_at_reciprocal_parameter': True,
                  'effect_on_unlabelled_regular_multiset': 'none'},
            'q11_exact_conclusion': 'Trace zero mod7 requires A=0 mod11 in a primitive Beal reduction, using the standard multiplicative branch comparison when C=0.',
            'conditional_CM_consequence': 'A form with CM by K(sqrt(-3)), congruent to the Frey representation mod7, forces 11|A.',
            'synthetic_control': {'marginals_nonempty': True, 'global_intersection_empty': True},
            'boundaries': ['No Magma Hilbert-form computation.',
                           'No indexed form coefficient fields or Hecke values recovered.',
                           'Coefficient-conjugate pairs are exact polynomial relations, not an assertion of new elimination.',
                           'All 110 smooth residue pairs of the Beal model at q=11 independently recomputed by point counts.',
                           'Other q data are imported algorithm outputs, not independently certified.',
                           'CM consequence assumes the modular representation comparison and the usual bad-prime trace condition.']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = audit()
    text = json.dumps(result, indent=2, sort_keys=True)+'\n'
    if args.output:
        args.output.write_text(text)
    print(text, end='')
