#!/usr/bin/env python3
"""Exact continuation audit for the dyadic Euler carry-Newton reduction.

This script is finite evidence for the formulas in CONTINUATION_02.md.
It does not replace the proofs there.
"""
from __future__ import annotations
from collections import Counter
from fractions import Fraction as F
from math import comb, factorial, inf, ceil
from pathlib import Path
import importlib.util, json, time

BASE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("baseaudit", BASE / "check_dyadic_tail.py")
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

MAX_N = 512
ROOT_BITS = 64


def lam(r: int, j: int) -> int:
    return 3*j + (r+j).bit_count() - r.bit_count()


def carry_count(r: int, j: int) -> int:
    return r.bit_count() + j.bit_count() - (r+j).bit_count()


def lam_carry(r: int, j: int) -> int:
    return 3*j + j.bit_count() - carry_count(r, j)


def candidate_bound(r: int) -> int:
    return max(0, (r.bit_count()-1)//3)


def min_data(r: int):
    B = candidate_bound(r)
    vals = [lam(r,j) for j in range(B+1)]
    mu = min(vals)
    J = tuple(j for j,v in enumerate(vals) if v == mu)
    return mu, J, B


def root_type(J: tuple[int,...]):
    s = set(J)
    g0 = int(0 in s)
    g1 = int(0 in s) ^ int(1 in s)
    roots = []
    if g0 == 0:
        der0 = (int(1 in s) + int(2 in s)) % 2
        roots.append((0, "simple" if der0 else "multiple"))
    if g1 == 0:
        der1 = sum(int(j in s) for j in (1,2,3)) % 2
        roots.append((1, "simple" if der1 else "multiple"))
    return tuple(roots)


def generalized_G_mod(r: int, x: int, bits: int, beta: list[F]) -> int:
    mu, J, B = min_data(r)
    modulus = 1 << bits
    answer = 0
    P = 1
    # lambda_r(j)-mu >= 3j+1-s2(r)-mu; beyond this cutoff every term vanishes mod 2^bits.
    last = max(B+5, ceil((bits + r.bit_count() + mu - 1)/3)+2)
    if r + last >= len(beta):
        raise ValueError("insufficient inverse coefficients")
    scale = F(1 << (-mu), 1) if mu <= 0 else F(1, 1 << mu)
    for j in range(last+1):
        if j:
            P = P * (x-j+1) * (2*x-(2*j-1)) % modulus
        coeff = scale * F(8**j) * beta[r+j] / beta[r]
        assert base.v2(coeff) >= 0
        if base.v2(coeff) < bits:
            answer = (answer + base.mod_fraction(coeff,bits)*P*base.source_mod(x-j,bits)) % modulus
    return answer


def lift_simple_root(r: int, parity: int, bits: int, beta: list[F]) -> int:
    x = parity
    assert generalized_G_mod(r,x,1,beta) == 0
    for b in range(2,bits+1):
        if generalized_G_mod(r,x,b,beta) != 0:
            x += 1 << (b-1)
        assert generalized_G_mod(r,x,b,beta) == 0
        alt = x ^ (1 << (b-1))
        assert generalized_G_mod(r,alt,b,beta) != 0
    return x


def edge_data(j: int):
    vals = []
    for k in range(j):
        if k == 0:
            e = 0
        else:
            e = 3*k + (j-1).bit_count() - (j-k-1).bit_count()
        vals.append(e)
    E = min(vals)
    K = tuple(k for k,v in enumerate(vals) if v == E)
    A = 3*j + 1 + (j-1).bit_count()
    L = A - E
    return E,K,A,L


def main():
    t0=time.perf_counter()
    kappa=base.inverse_coefficients(700)
    beta=[kappa[m]/(4**m*factorial(2*m)) for m in range(701)]
    sources=[base.source(n) for n in range(MAX_N+1)]
    euler=base.euler_even(MAX_N)

    # Carry formula and finite-candidate reduction.
    carry_checks=0
    finite_bound_checks=0
    for r in range(1,100000):
        B=candidate_bound(r)
        for j in range(B+6):
            assert lam(r,j) == lam_carry(r,j)
            carry_checks += 1
        mu,J,_=min_data(r)
        # The next five indices beyond the proved cutoff must be positive, hence cannot minimize.
        for j in range(B+1,B+6):
            assert lam(r,j) > 0 >= mu
            finite_bound_checks += 1

    # Wall-crossing theorem on j<=200, checking one level before/at/after the wall.
    wall_checks=0
    wall_table=[]
    for j in range(1,201):
        E,K,A,Lstar=edge_data(j)
        for L in (max(1,Lstar-1),Lstar,Lstar+1):
            r=(1<<L)-j
            mu,J,B=min_data(r)
            if L < Lstar:
                assert set(J).issubset(set(K))
                assert j not in J
            elif L == Lstar:
                assert set(J) == set(K) | {j}
            else:
                assert J == (j,)
            wall_checks += 1
        if j <= 20:
            wall_table.append(dict(j=j,E=E,earlier_minima=K,A=A,Lstar=Lstar,
                                   boundary=(1<<Lstar)-j))

    # Exact-tail validation on all nonempty tails through N=512.
    roots={}
    class_counts=Counter()
    for r in range(1,MAX_N+1):
        mu,J,B=min_data(r)
        typ=root_type(J)
        class_counts[str((J,typ))]+=1
        roots[r]={}
        for parity,status in typ:
            if status == 'simple':
                roots[r][parity]=lift_simple_root(r,parity,16,beta)

    tail_checks=0
    no_root_checks=0
    simple_root_checks=0
    unresolved_multiple=0
    for N in range(1,MAX_N+1):
        terms=[kappa[m]*comb(2*N,2*m)*sources[N-m] for m in range(N+1)]
        assert sum(terms,F(0)) == euler[N]
        acc=F(0)
        for r in range(N,0,-1):
            acc += terms[r]
            actual=base.v2(acc)
            mu,J,B=min_data(r)
            typ=root_type(J)
            base_weight=4*r-1+base.v2_int(comb(N,r))+mu
            if not typ:
                predicted=base_weight
                no_root_checks += 1
            elif all(status=='simple' for _,status in typ):
                x=N-r
                parity=x&1
                if parity in roots[r]:
                    d=(x-roots[r][parity]) % (1<<16)
                    if d == 0:
                        # Root precision insufficient to resolve this integer. Skip rather than guess.
                        continue
                    predicted=base_weight+base.v2_int(d)
                else:
                    predicted=base_weight
                simple_root_checks += 1
            else:
                unresolved_multiple += 1
                continue
            assert actual == predicted, (N,r,actual,predicted,mu,J,typ)
            tail_checks += 1

    # First two-root case r=510, independently against the original unfactored modular tail.
    r=510
    mu,J,B=min_data(r)
    assert mu == -1 and J == (2,)
    assert root_type(J) == ((0,'simple'),(1,'simple'))
    roots510={p: lift_simple_root(r,p,ROOT_BITS,beta) for p in (0,1)}
    checks510=[]
    for x in (0,1,2,3,4,5,7,8,15,16,31,32,63,64,95):
        N=r+x
        residue=base.original_tail_mod(N,r-1,2100,kappa)
        actual=base.v2_int(residue)
        dist=base.v2_int((x-roots510[x&1])%(1<<ROOT_BITS))
        predicted=4*r-1+base.v2_int(comb(N,r))+mu+dist
        assert actual == predicted
        checks510.append(dict(x=x,N=N,binomial_v2=int(base.v2_int(comb(N,r))),
                              root_distance=int(dist),tail_v2=int(actual)))

    result={
        'status':'PASS',
        'carry_identity_checks':carry_checks,
        'finite_candidate_bound_checks':finite_bound_checks,
        'wall_crossing_checks':wall_checks,
        'all_tail_prediction_checks':tail_checks,
        'no_root_tail_checks':no_root_checks,
        'simple_root_tail_checks':simple_root_checks,
        'unresolved_multiple_root_tails_in_N_le_512':unresolved_multiple,
        'classification_counts_r_le_512':dict(class_counts),
        'first_two_root_case':{
            'r':510,'M':509,'mu':mu,'J':J,
            'roots_mod_2_to_64':{str(k):v for k,v in roots510.items()},
            'checks':checks510,
        },
        'wall_table_j_1_to_20':wall_table,
        'runtime_seconds':time.perf_counter()-t0,
        'non_claims':[
            'The finite checks do not prove the general theorems in CONTINUATION_02.md.',
            'Multiple residual-root branches beginning at higher dominant indices are not fully resolved here.',
            'No Lean compilation or historical-priority review was performed.'
        ]
    }
    (BASE/'RESULTS_CARRY_NEWTON.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    main()
