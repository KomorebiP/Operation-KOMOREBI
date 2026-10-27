#!/usr/bin/env python3
"""Bounded checks only; uniform claims have separate written proofs."""
from collections import Counter
from math import comb, isqrt
from pathlib import Path
import json
import sys


def tau_triangular(N):
    ts = []
    m = 1
    while m*(m+1)//2 < N:
        ts.append((m*(m+1)//2, (-1)**m*(2*m+1)))
        m += 1
    f = [1]+[0]*(N-1)
    for n in range(1, N):
        total = sum(a*(9*t-n)*f[n-t] for t, a in ts if t <= n)
        f[n], rem = divmod(total, n)
        assert rem == 0
    return [0]+f


def tau_product(N):
    a = [1]+[0]*(N-1)
    for k in range(1, N):
        b = a.copy()
        for j in range(1, min(24, (N-1)//k)+1):
            c = (-1)**j*comb(24, j)
            for i in range(j*k, N):
                b[i] += c*a[i-j*k]
        a = b
    return [0]+a


def primes(N):
    ok = [True]*(N+1)
    ok[:2] = [False,False]
    for p in range(2,isqrt(N)+1):
        if ok[p]:
            for j in range(p*p,N+1,p):
                ok[j] = False
    return [p for p in range(2,N+1) if ok[p]]


def local_sequence(p,a,N):
    T = [1,a]
    for _ in range(2,N+1):
        T.append(a*T[-1]-p**11*T[-2])
    chi = 0 if p%5 == 0 else (1 if p%5 in (1,4) else -1)
    R = T[:2]+[T[r]-chi*p**10*T[r-2] for r in range(2,N+1)]
    return T,R


def main(out):
    stats = Counter()
    tau = tau_triangular(10000)
    assert tau[:129] == tau_product(128)
    stats['independent_product_coefficients'] = 128
    ps = primes(10000)
    selected = [1,2,3,4,5,7,8,9,11,13,16,17,19,23,25,27,30,32,49,60,64,120,128,210]
    examples = []
    for M in selected:
        matches = [p for p in ps if (p+1)%(5*M) == 0 and tau[p]%M == 0]
        rec = {'modulus':M,'count_through_10000':len(matches),'first_prime':None}
        if matches:
            p = matches[0]
            T,R = local_sequence(p,tau[p],32)
            assert R[0] == 1 and all(x%M == 0 for x in R[1:])
            assert all(T[r]%M == (1 if r%2 == 0 else 0)%M for r in range(33))
            stats['actual_local_congruences'] += 32
            rec.update(first_prime=p,tau_prime=tau[p],tau_quotient=tau[p]//M,
                       primitive_square=R[2])
        examples.append(rec)
    # Deliberately synthetic integer p,a: this checks the polynomial mechanism,
    # not primality or density, and includes M=1 and even moduli.
    for M in range(1,257):
        p = 5*M-1
        for a in (-2*M,0,3*M):
            T,R = local_sequence(p,a,32)
            assert all(x%M == 0 for x in R[1:])
            stats['synthetic_local_congruences'] += 32
    # Trace-zero filtered Frobenius matrices: phi=[[0,-p^11],[1,0]].
    # The nonexistence of invariant Q_p-lines follows universally from odd
    # determinant valuation and is proved in NOTE.md, not tested here.
    for p in ps:
        phi = ((0,-p**11),(1,0))
        square = tuple(tuple(sum(phi[i][k]*phi[k][j] for k in range(2))
                             for j in range(2)) for i in range(2))
        assert square == ((-p**11,0),(0,-p**11))
        assert phi[0][0]+phi[1][1] == 0
        assert phi[0][0]*phi[1][1]-phi[0][1]*phi[1][0] == p**11
        stats['frobenius_matrix_checks'] += 1
    result = {'status':'passed','bounds':{'tau_max':10000,'actual_exponent_max':32,
              'synthetic_moduli':[1,256],'synthetic_a_multipliers':[-2,0,3]},
              'counts':dict(stats),'examples':examples,
              'non_claims':['No proof of Chebotarev or positive density by computation',
              'No proof of Lehmer; no tau zero found or asserted',
              'Synthetic p parameters need not be prime']}
    Path(out).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result['counts'],sort_keys=True))


if __name__ == '__main__':
    main(sys.argv[1])
