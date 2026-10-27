#!/usr/bin/env python3
"""Exact finite Taylor controls for continuous approximate intertwining.

No floating-point exponential, sample-based stability claim, or universal
inference is used. Universal statements are proved separately in Lean.
The integral is expanded in monomials independently of the factorial identity.
All imported helpers are from the preserved standard-library-only controls.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as Q
from math import factorial, comb
import json
from pathlib import Path
import random
from check_discrete_memory import Mat
from check_continuous_memory import scale, polynomial_integral_factor

SEED = 20260913
ORDER = 8
MAX_DIMENSION = 3


def norm_inf(a: Mat) -> Q:
    return max((sum((abs(x) for x in row), Q(0)) for row in a.entries), default=Q(0))


def generator_defect(q: Mat, L: Mat, A: Mat) -> Mat:
    if L.rows != L.cols or A.rows != A.cols or (q.rows, q.cols) != (A.rows, L.rows):
        raise ValueError('Incompatible generator/representation dimensions')
    return q @ L - A @ q


def coefficients(q: Mat, L: Mat, A: Mat, order: int) -> list[Mat]:
    if type(order) is not int or not 0 <= order <= 20:
        raise ValueError('Taylor order must be an integer in 0..20')
    generator_defect(q, L, A)
    return [scale(Q(1, factorial(n)), q @ L.power(n) - A.power(n) @ q)
            for n in range(order+1)]


def validate_coefficients(q: Mat, L: Mat, A: Mat, claimed: list[Mat]) -> None:
    """Checks exactly ORDER+1 whole coefficients; incomplete data fail closed."""
    if len(claimed) != ORDER+1:
        raise ValueError('Incomplete coefficient table')
    if claimed != coefficients(q, L, A, ORDER):
        raise ValueError('Incorrect coefficient table')


def run() -> dict:
    rng = random.Random(SEED)
    checks = rejected = systems = 0
    def check(ok: bool, label: str) -> None:
        nonlocal checks
        checks += 1
        if not ok:
            raise AssertionError(f'{checks}: {label}')
    def reject(fn) -> None:
        nonlocal rejected
        try:
            fn()
        except (ValueError, AssertionError):
            rejected += 1
        else:
            raise AssertionError('Invalid input accepted')
    def rand(r: int, c: int) -> Mat:
        return Mat(r, c, tuple(tuple(Q(rng.randint(-2,2),rng.randint(1,3))
                                    for _ in range(c)) for _ in range(r)))
    def series(A: Mat) -> list[Mat]:
        return [scale(Q(1,factorial(n)), A.power(n)) for n in range(ORDER+1)]

    for nx in range(MAX_DIMENSION+1):
        for nz in range(MAX_DIMENSION+1):
            for repetition in range(2):
                systems += 1
                L, A, q = rand(nx,nx), rand(nz,nz), rand(nz,nx)
                delta = generator_defect(q,L,A)
                lc, ac = series(L), series(A)
                E = coefficients(q,L,A,ORDER)
                validate_coefficients(q,L,A,E)
                nw = (nx+nz+repetition) % 4
                p, B = rand(nw,nz), rand(nw,nw)
                E2, EC = coefficients(p,A,B,ORDER), coefficients(p @ q,L,B,ORDER)
                O, V, x, z = rand(2,nx), rand(2,nz), rand(nx,1), rand(nz,1)
                check(generator_defect(p @ q,L,B) ==
                      p @ delta + generator_defect(p,A,B) @ q, 'composed generator')
                check(E[0] == Mat.zero(nz,nx), 'zero initial defect')
                check(E[1] == delta, 'actual first derivative')
                for n in range(ORDER+1):
                    integral = Mat.zero(nz,nx)
                    allowance = Q(0)
                    for k in range(n):
                        j = n-1-k
                        factor = polynomial_integral_factor(k,j)
                        integral += scale(factor, ac[k] @ delta @ lc[j])
                        allowance += factor * norm_inf(ac[k]) * norm_inf(delta) * norm_inf(lc[j])
                    check(E[n] == integral, 'Duhamel coefficient via antiderivative')
                    check(norm_inf(E[n]) <= allowance, 'coefficient norm envelope')
                    check(EC[n] == p @ E[n] + E2[n] @ q, 'multilevel coefficient')
                    output = O @ lc[n] - V @ ac[n] @ q
                    check(output == (O-V @ q) @ lc[n]+V @ E[n], 'readout separation')
                    check(O @ lc[n] @ x - V @ ac[n] @ z ==
                          output @ x + V @ ac[n] @ (q @ x-z), 'initialization separation')
                    if n < ORDER:
                        check(scale(Q(n+1),E[n+1]) == A @ E[n]+delta @ lc[n],
                              'derived defect differential equation')
                for i in range(5):
                    for j in range(5):
                        check(scale(Q(comb(i+j,i)),E[i+j]) == E[i] @ lc[j]+ac[i] @ E[j],
                              'time concatenation coefficient')
                if nx and nz and repetition == 0:
                    changed = list(E)
                    bump = Mat(nz,nx,tuple(tuple(Q(i==0 and j==0) for j in range(nx))
                                             for i in range(nz)))
                    changed[1] += bump
                    reject(lambda: validate_coefficients(q,L,A,changed))

    rates = [Q(-2),Q(-1,2),Q(0),Q(1,2),Q(2)]
    for a in rates:
        for b in rates:
            for n in range(ORDER+1):
                integrated = sum((Q(b**k*a**(n-1-k),factorial(k)*factorial(n-1-k)) *
                                  polynomial_integral_factor(k,n-1-k) for k in range(n)),Q(0))
                expected = (Q(0) if n==0 else Q(a**(n-1),factorial(n-1))) if a==b else \
                           (a**n-b**n)/(factorial(n)*(a-b))
                check(integrated==expected,'distinct and coincident exponential rates')
                check((a-b)*integrated == (a**n-b**n)/factorial(n), 'scalar exact sharpness coefficients')

    I, zero = Mat.eye(1), Mat.zero(1,1)
    for eps in [Q(1,1000),Q(1,7),Q(1)]:
        L=Mat.of([[eps]])
        E=coefficients(I,L,zero,ORDER)
        check(norm_inf(generator_defect(I,L,zero)) == eps,'arbitrarily small generator error')
        check(all(E[n].entries[0][0] == eps**n/factorial(n) for n in range(1,ORDER+1)),
              'unstable exact Taylor coefficients')
        for t in [Q(0),Q(1,2),Q(1),Q(10)]:
            partial=sum((E[n].entries[0][0]*t**n for n in range(ORDER+1)),Q(0))
            check(partial>=eps*t,'finite positive-series lower bound')
    reject(lambda: validate_coefficients(I,I,zero,[]))
    reject(lambda: coefficients(I,I,zero,-1))
    reject(lambda: coefficients(I,I,zero,21))
    reject(lambda: coefficients(I,I,zero,True))
    reject(lambda: generator_defect(Mat.zero(2,1),I,I))
    reject(lambda: generator_defect(I,Mat.zero(1,2),zero))
    return {'passed':True,'seed':SEED,'systems':systems,'state_dimensions':[0,MAX_DIMENSION],
            'taylor_order':ORDER,'mixed_time_degrees':[0,4],
            'scalar_rate_pairs':len(rates)**2,'exact_assertions':checks,
            'negative_controls_rejected':rejected,'arithmetic':'fractions.Fraction only',
            'non_claims':['Finite Taylor coefficients are not whole sampled exponentials.',
                          'No universal theorem follows from these finite controls.',
                          'Flow-growth assumptions are not inferred from sampled matrices.',
                          'The Python implementation is not formally verified.']}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    result=run()
    text=json.dumps(result,indent=2)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(text)
    print(text,end='')
