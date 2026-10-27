#!/usr/bin/env python3
"""Exact certificates for Fermat packet capacity and explicit five-phase cycles.

Python >=3.10, SymPy. No network, optimization, floating arithmetic, or random
sampling. The geometric theorem is a manuscript proof, not machine formalized.
Run from the bundle root: python checks/verify_all.py
"""
from __future__ import annotations
import argparse
from fractions import Fraction
import hashlib
import heapq
import itertools
import json
import math
import platform
from pathlib import Path
import sys
import time
from datetime import datetime, timezone
import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR_SHA256 = '72807b5827d21a85bfc1aa8b62ab11a3371de5e6529be751c0943e07bf5e9a77'


def dual_certificate(m: int, a: list[int], dual: list[Fraction]) -> dict:
    """Certify all nonempty invariant exponent vectors, not a degree cutoff.

    Integer potentials d satisfy d[r+a_i] <= d[r]+cost_i and d[0]=0.
    Therefore every path to residue r has cost >= d[r]. A zero-sum word,
    split before its last edge, costs >= d[-a_i]+cost_i.
    """
    if not 2 <= m <= 10000 or len(a) != 6 or len(dual) != 6:
        raise ValueError('Expected six coordinates and 2 <= modulus <= 10000')
    if not all(0 < x < m for x in a) or math.gcd(m, *a) != 1:
        raise ValueError('Use a primitive full-support character')
    if not all(x > 0 for x in dual):
        raise ValueError('This verifier requires strictly positive dual costs')
    L = math.lcm(*(v.denominator for v in dual))
    costs = [int(L * v) for v in dual]
    dist: list[int | None] = [None] * m
    dist[0] = 0
    heap = [(0, 0)]
    while heap:
        d, r = heapq.heappop(heap)
        if d != dist[r]:
            continue
        for ai, ci in zip(a, costs):
            nxt, nd = (r + ai) % m, d + ci
            if dist[nxt] is None or nd < dist[nxt]:
                dist[nxt] = nd
                heapq.heappush(heap, (nd, nxt))
    if any(x is None for x in dist):
        raise AssertionError('Residue graph was not connected')
    d = [int(x) for x in dist]
    triangles = all(d[(r + ai) % m] <= d[r] + ci
                    for r in range(m) for ai, ci in zip(a, costs))
    returns = [d[-ai % m] + ci for ai, ci in zip(a, costs)]
    if not triangles or d[0] != 0 or min(returns) < L:
        raise AssertionError('The proposed dual is not globally certified')
    return {'denominator': L, 'integer_costs': costs, 'potentials': d,
            'all_bellman_inequalities': triangles,
            'bellman_inequality_count': 6 * m,
            'last_edge_lower_bounds': returns,
            'minimum_nonempty_cycle_cost': str(Fraction(min(returns), L)),
            'dual_objective': str(sum(dual, Fraction(0))),
            'scope': 'all nonzero invariant nonnegative integer exponent vectors'}


def elementary(vars_, k):
    return sum(sp.prod(c) for c in itertools.combinations(vars_, k))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=ROOT/'results/verification.json')
    args = parser.parse_args()
    start = time.perf_counter()
    records = []

    def check(label, condition, detail=None):
        ok = bool(condition)
        records.append({'name': label, 'pass': ok, 'detail': detail})
        if not ok:
            raise AssertionError(f'{label}: {detail}')

    pred = ROOT/'predecessor/Komorebi_Hodge_Carrier70_v0.1.0.zip'
    check('predecessor_bytes_preserved', hashlib.sha256(pred.read_bytes()).hexdigest() == PREDECESSOR_SHA256)
    capacity_results = []
    for data in json.loads((ROOT/'checks/capacity_inputs.json').read_text()):
        m, a = data['modulus'], data['character']
        units = [t for t in range(1, m) if math.gcd(t, m) == 1]
        check(f'capacity_{m}_input_is_balanced', all(sum(t*x % m for x in a) == 3*m for t in units))
        A = sp.Matrix(data['matrix'])
        w = sp.Matrix([sp.Rational(v) for v in data['weights']])
        y = [Fraction(v) for v in data['candidate_dual']]
        check(f'capacity_{m}_primal', A*w == sp.ones(6, 1) and all(v > 0 for v in w))
        check(f'capacity_{m}_invariant_columns', all(int(v) % m == 0 for v in A.T*sp.Matrix(a)))
        check(f'capacity_{m}_matching_objectives', sum(w) == sp.Rational(data['weight_sum']) == sp.Rational(sum(y)))
        cert = dual_certificate(m, a, y)
        check(f'capacity_{m}_global_dual', cert['all_bellman_inequalities'])
        capacity_results.append({**data, 'global_dual_certificate': cert})

    # Symbolic no-go congruence. Positivity and divisibility implication for all
    # q>5, gcd(b,q)=1 is proved in PROOF.md, not inferred from sampled q.
    q, b = sp.symbols('q b', integer=True)
    v = sp.symbols('v0:6', integer=True)
    aa = [b + i*q for i in range(5)] + [5*(q-b)]
    cc = [1]*5 + [q-5]
    check('uniform_no_go_congruence_identity', sp.expand(
        sum(aa[i]*v[i] for i in range(6)) - b*sum(cc[i]*v[i] for i in range(6))
        - q*(sum(i*v[i] for i in range(5)) + (5-b)*v[5])) == 0)
    check('uniform_no_go_dual_sum', sp.cancel(sum(cc)/q) == 1)
    check('uniform_no_go_primal_unit_column', sp.expand(sum(aa)-15*q) == 0)

    t = sp.symbols('t0:5')
    e = [elementary(t, i) for i in range(1, 6)]
    g1 = e[0]**4-5*e[0]**2*e[1]+5*e[0]*e[2]+5*e[1]**2-5*e[3]
    check('newton_identity_p5', sp.expand(sum(x**5 for x in t) - (e[0]*g1-5*e[1]*e[2]+5*e[4])) == 0)
    delta = sp.prod(t[i]-t[j] for i in range(5) for j in range(i+1, 5))
    EJ = sp.Matrix([[sp.diff(f, x) for x in t] for f in e])
    check('elementary_jacobian_vandermonde', sp.expand(EJ.det(method='domain-ge')-delta) == 0)

    E1,E2,E3,E4,P,z,kappa = sp.symbols('E1 E2 E3 E4 P z kappa')
    G1 = E1**4-5*E1**2*E2+5*E1*E3+5*E2**2-5*E4
    coords = [E1,E2,E3,E4,P,z]
    determinant_q_values = [2,3,4,5,7,11,17]
    for qi in determinant_q_values:
        f3 = P-kappa*z**5
        G3 = 5*sum(P**(qi-1-j)*kappa**j*z**(5*j) for j in range(qi))
        check(f'factorization_geometric_sum_q{qi}', sp.expand(f3*G3-5*(P**qi-kappa**qi*z**(5*qi))) == 0)
        H = [E1,G1,E2,-5*E3,f3,G3]
        HJ = sp.Matrix([[sp.diff(h, x) for x in coords] for h in H])
        target = 625*qi*sum(kappa**j*P**(qi-1-j)*z**(5*j-1) for j in range(1,qi))
        check(f'exact_intermediate_determinant_q{qi}', sp.expand(HJ.det(method='domain-ge')-target) == 0)
    # The uniform combinatorial coefficient is j+(q-j)=q.
    j = sp.symbols('j', integer=True)
    check('uniform_wedge_coefficient', sp.expand(j+(q-j)-q) == 0)
    check('period_normalization', sp.cancel(625*q**5/(2*(5*q)**6)-1/(50*q)) == 0)

    permutations = list(itertools.permutations(range(5)))
    total_support_terms = 0
    total_balanced_unit_tests = 0
    for qi in range(2, 65):
        m = 5*qi
        units = [t for t in range(1,m) if math.gcd(t,m)==1]
        seen = set()
        valid = True
        for bi in range(1,qi):
            char = [bi+i*qi for i in range(5)] + [5*(qi-bi)]
            for ti in units:
                transformed = [ti*x % m for x in char]
                valid &= all(0 < x < m for x in transformed) and sum(transformed) == 3*m
                # Reordered first five entries are the same family at b'=tb mod q.
                bp = ti*bi % qi
                valid &= sorted(transformed[:5]) == [bp+i*qi for i in range(5)]
                valid &= transformed[5] == 5*(qi-bp)
                total_balanced_unit_tests += 1
            for perm in permutations:
                exponent = tuple(bi-1+qi*i for i in perm)+(5*(qi-bi)-1,)
                valid &= all(0 <= x <= m-2 for x in exponent)
                valid &= sum(exponent) == 3*m-6
                seen.add(exponent)
        valid &= len(seen) == 120*(qi-1)
        total_support_terms += len(seen)
        check(f'family_support_and_balance_q{qi}', valid, {'terms':len(seen)})

    # Independent socle-pairing check using SymPy's expanded Vandermonde,
    # rather than the permutation construction used for the support census.
    delta_terms = sp.Poly(delta, *t).terms()
    for qi in (2, 7, 11):
        m = 5*qi
        for bi in range(1, qi):
            char = [bi+i*qi for i in range(5)] + [5*(qi-bi)]
            dual_exp = tuple(m-ai-1 for ai in char)
            survivors = []
            for bj in range(1, qi):
                for powers, coefficient in delta_terms:
                    exp = tuple(qi*power+bj-1 for power in powers) + (5*(qi-bj)-1,)
                    product_exp = tuple(x+y for x,y in zip(exp, dual_exp))
                    if all(x <= m-2 for x in product_exp):
                        survivors.append((product_exp, int(coefficient), qi-bj))
            check(f'exact_socle_pairing_q{qi}_b{bi}',
                  survivors == [((m-2,)*6, 1, qi-bi)],
                  {'surviving_terms': len(survivors), 'coefficient_factor': 625*qi**5})

    examples=[]
    for qi,bi in [(5,1),(7,1),(11,1),(14,1)]:
        m=5*qi
        char=[bi+i*qi for i in range(5)]+[5*(qi-bi)]
        units=[t for t in range(1,m) if math.gcd(t,m)==1]
        orbit=sorted({tuple(t*x % m for x in char) for t in units})
        examples.append({'q':qi,'b':bi,'degree':m,'character':char,
                         'rational_packet_dimension':len(orbit),
                         'cycle_degree':10*qi*qi,
                         'determinant_coefficient_integer_factor':625*qi**5,
                         'kappa_exponent':qi-bi,
                         'period_factor_after_(2pii)^2':f'kappa^{qi-bi}/{50*qi}',
                         'jacobian_dual_test_monomial_exponents':[m-x-1 for x in char],
                         'total_first_five_permutation_sector_dimension':120*(qi-1)})
    (ROOT/'results/capacity_certificates.json').write_text(json.dumps(capacity_results,indent=2)+'\n')
    (ROOT/'results/cycle_examples.json').write_text(json.dumps(examples,indent=2)+'\n')
    result={
        'status':'PASS: exact computational assertions; geometric proof remains manuscript-level',
        'created_utc':datetime.now(timezone.utc).isoformat(),
        'python':platform.python_version(),'sympy':sp.__version__,'platform':platform.platform(),
        'command':[sys.executable,'checks/verify_all.py'],
        'runtime_seconds':time.perf_counter()-start,
        'checks_passed':len(records),'checks':records,
        'arithmetic':'integer and rational arithmetic, exact symbolic polynomial identities',
        'randomness':'none','network':'none','optimization':'none in certificate replay',
        'tested_family_q_range':[2,64],
        'symbolic_intermediate_determinant_q_values':determinant_q_values,
        'support_monomials_checked':total_support_terms,
        'balanced_unit_instances_checked':total_balanced_unit_tests,
        'universal_conclusions':'See PROOF.md for mathematical arguments separate from finite replay',
        'nonclaims':['No proof of the general Hodge conjecture',
                     'No Lean verification of the geometric proof',
                     'No claim that standard-cycle algebraicity is new',
                     'No claim that the capacity criterion is sufficient for a normal geometric carrier']}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+'\n')
    print(result['status'])
    print(f"{len(records)} grouped checks passed in {result['runtime_seconds']:.3f} s")
    print(f"{total_support_terms} distinct support monomials; {total_balanced_unit_tests} balance/conjugacy instances")
    print('Capacity values:',{d['modulus']:d['weight_sum'] for d in capacity_results})

if __name__ == '__main__':
    main()
