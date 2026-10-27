#!/usr/bin/env python3
"""Finite exact regressions linking the new Lean formulas to the existing EGF laboratory.
These rational tests are not substitutes for the Lean universal proofs.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as Q
from itertools import product
import json
from math import factorial
from pathlib import Path
import sys
import time
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'research'))
import coupled_lab  # preserved original EGF implementation

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    start = time.monotonic()
    counts: dict[str, int] = {}
    def check(label: str, condition: bool) -> None:
        if not condition:
            raise AssertionError(label)
        counts[label] = counts.get(label, 0) + 1
    def dense(scales: tuple[Q, ...], last: int) -> tuple[list[Q], list[Q]]:
        q, r, a, b = scales
        u, v = [Q(0)], [Q(0)]
        for degree in range(2*last+1):
            du = Q(degree == 0) + sum((q**i * r**(degree-i) * u[i] * v[degree-i]
                                      for i in range(degree+1)), Q(0))
            dv = Q(degree == 0) + sum((a**i * b**(degree-i) * u[i] * v[degree-i]
                                      for i in range(degree+1)), Q(0))
            u.append(du / (degree+1))
            v.append(dv / (degree+1))
        return u, v
    grid = tuple(Q(i, 5) for i in range(1, 5))
    seen: dict[tuple[Q, ...], tuple[Q, ...]] = {}
    regular = 0
    cases = list(product(grid, repeat=4))
    for case, scales in enumerate(cases):
        q, r, a, b = scales
        p, k = q*r, a*b
        u, v = dense(scales, 6)
        A, B = coupled_lab.coupled_odd_derivatives(*scales, last=6)
        for row, derivatives in ((u, A), (v, B)):
            for n in range(7):
                check('ordinary_vs_EGF', row[2*n+1] == derivatives[n]/factorial(2*n+1))
                check('strict_positivity', row[2*n+1] > 0)
                check('geometric_majorant', row[2*n+1] <= Q(1,2)**n)
                check('even_coefficients_zero', row[2*n] == 0)
        U1, V1 = p/3, k/3
        U2, V2 = p*(p*q*q+k*r*r)/15, k*(p*a*a+k*b*b)/15
        U3 = p*(q**4*U2+p*p*U1*V1+r**4*V2)/7
        V3 = k*(a**4*U2+k*k*U1*V1+b**4*V2)/7
        jets = (U1, V1, U2, V2, U3, V3)
        check('six_jet_formula', jets == (u[3],v[3],u[5],v[5],u[7],v[7]))
        defect = k*k*U2-p*p*V2
        check('defect_factorization', defect == p*k*a*r*(q*q-b*b)*(q*b-a*r)/15)
        check('zero_locus', (defect == 0) == (q == b or q*b == a*r))
        if defect:
            regular += 1
            check('regular_jet_collision', jets not in seen or seen[jets] == scales)
            seen[jets] = scales
        if case < 8:
            for z in (Q(1,2), Q(1), Q(4,3)):
                ratio = z*z/2
                for N in range(8):
                    upper = z*ratio**N/(1-ratio)
                    for row in (u, v):
                        finite_tail = sum((row[2*n+1]*z**(2*n+1) for n in range(N,7)),Q(0))
                        check('tail_bound_indexing', 0 <= finite_tail <= upper)
    sl, sr = (Q(1,4),Q(1,2),Q(1,4),Q(1,2)), (Q(1,2),Q(1,4),Q(1,2),Q(1,4))
    check('boundary_parameters_distinct', sl != sr)
    check('boundary_jet_collision', dense(sl,3) == dense(sr,3))
    worked = (Q(1,5),Q(2,5),Q(3,5),Q(7,10))
    u, v = dense(worked,3)
    p, k = worked[0]*worked[1], worked[2]*worked[3]
    d = k*k*u[5]-p*p*v[5]
    check('worked_defect', d == Q(189,7812500))
    check('reject_draft_numeric_typo', d != Q(189,3125000))
    report = {'passed':True, 'parameter_grid_cases':len(cases), 'regular_grid_cases':regular,
              'last_odd_index':6, 'exact_assertions':sum(counts.values()), 'counts':counts,
              'seconds':round(time.monotonic()-start,6),
              'scope':'Finite rational regressions; distinct from kernel proof of the universal statements.'}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    return 0

if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, OSError, AssertionError) as exc:
        print('FAILED: '+str(exc),file=sys.stderr)
        raise SystemExit(1)
