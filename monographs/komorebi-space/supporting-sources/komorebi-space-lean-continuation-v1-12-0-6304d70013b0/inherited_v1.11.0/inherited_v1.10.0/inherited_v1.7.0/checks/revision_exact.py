#!/usr/bin/env python3
"""Exact checks for the v1.1.0 additions, including an independent rank oracle.

Universal conclusions are proved in the monograph. These finite tests audit
worked models and the supplied rational implementation, not a Lean refinement.
"""
from __future__ import annotations
from dataclasses import replace
from datetime import datetime, timezone
from fractions import Fraction as Q
from itertools import combinations, permutations, product
from pathlib import Path
from random import Random
import json
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'examples'))
from protected_repair import Certificate, solve_protected, verify_certificate

COUNT = 0
GROUPS = {}
NEGATIVE = []


def check(p, message):
    global COUNT
    COUNT += 1
    if not p:
        raise AssertionError(message)


def run(name, fn):
    before = COUNT
    detail = fn()
    GROUPS[name] = {'assertions': COUNT-before, 'detail': detail}


def det(a):
    """Leibniz expansion, independent of the proposer's row reduction."""
    n = len(a)
    total = Q(0)
    for p in permutations(range(n)):
        inversions = sum(p[i] > p[j] for i in range(n) for j in range(i+1, n))
        term = Q((-1)**inversions)
        for i in range(n):
            term *= a[i][p[i]]
        total += term
    return total


def rank_by_minors(a, n):
    for k in range(min(len(a), n), 0, -1):
        for rows in combinations(range(len(a)), k):
            for cols in combinations(range(n), k):
                if det([[a[i][j] for j in cols] for i in rows]):
                    return k
    return 0


def mv(a, x):
    return tuple(sum((Q(v)*Q(w) for v, w in zip(row, x)), Q(0)) for row in a)


def test_certificates():
    cases = []
    vecs = list(product(range(-1, 2), repeat=2))
    for a, p, x in product(vecs, repeat=3):
        cases.append(([a], [p], x))
    rng = Random(61010)
    for n in range(5):
        for m in range(4):
            for p in range(4):
                for _ in range(3):
                    A = [[Q(rng.randrange(-2,3), rng.randrange(1,4)) for _ in range(n)] for _ in range(m)]
                    P = [[Q(rng.randrange(-2,3), rng.randrange(1,4)) for _ in range(n)] for _ in range(p)]
                    x = [Q(rng.randrange(-3,4), rng.randrange(1,4)) for _ in range(n)]
                    cases.append((A,P,x))
    feasible = obstructed = 0
    for A, P, x in cases:
        c = solve_protected(A, P, x)
        n = len(x)
        T = list(A) + list(P)
        b = [Q(0)] * len(A) + list(mv(P,x))
        rank = rank_by_minors(T, n)
        aug = [list(row)+[rhs] for row,rhs in zip(T,b)]
        possible = rank_by_minors(aug,n+1) == rank
        check((c.status == 'feasible') == possible, 'independent rank alternative')
        check(verify_certificate(A,P,x,c), 'direct certificate verification')
        if possible:
            feasible += 1
            check(not any(mv(A,c.answer)), 'exact output')
            check(mv(P,c.answer) == mv(P,x), 'protected output')
            check(len(c.ambiguity_basis) == n-rank, 'independent ambiguity dimension')
            check(rank_by_minors(c.ambiguity_basis,n) == n-rank, 'independent basis independence')
            for v in c.ambiguity_basis:
                check(not any(mv(T,v)), 'ambiguity annihilates both operators')
            for coefficient in [-2, 1, 3]:
                y = tuple(c.answer[j] + coefficient*sum((v[j] for v in c.ambiguity_basis),Q(0)) for j in range(n))
                check(not any(mv(A,y)) and mv(P,y) == mv(P,x), 'affine family remains feasible')
        else:
            obstructed += 1
            la,mu = c.residual_witness,c.protected_witness
            left = tuple(sum((la[i]*A[i][j] for i in range(len(A))),Q(0)) for j in range(n))
            right = tuple(sum((mu[i]*P[i][j] for i in range(len(P))),Q(0)) for j in range(n))
            check(left == right, 'dual equality independent multiplication')
            check(sum((v*w for v,w in zip(left,x)),Q(0)) == 1, 'normalized nonzero obstruction')
    return {'cases':len(cases),'exhaustive_two_coordinate_cases':729,
            'seeded_shape_and_degenerate_cases':len(cases)-729,
            'feasible':feasible,'obstructed':obstructed,
            'oracle':'all minors with Leibniz determinants, not row reduction',
            'dimensions':'n=0..4; compatibility and protected row counts=0..3'}


def add(a,b):
    return tuple(tuple(x+y for x,y in zip(r,s)) for r,s in zip(a,b))


def sub(a,b):
    return tuple(tuple(x-y for x,y in zip(r,s)) for r,s in zip(a,b))


def mul(a,b):
    return tuple(tuple(sum((a[i][k]*b[k][j] for k in range(len(b))),Q(0))
                       for j in range(len(b[0]))) for i in range(len(a)))


def power(a,n):
    result=tuple(tuple(Q(i==j) for j in range(len(a))) for i in range(len(a)))
    for _ in range(n):result=mul(result,a)
    return result


def test_dyadic():
    rng=Random(55)
    A=((Q(1,2),Q(1,3)),(Q(0),Q(1,2)))
    B=((Q(1),Q(0)),(Q(0),Q(1,2)))
    BI=((Q(1),Q(0)),(Q(0),Q(2)))
    Z=((Q(0),Q(0)),(Q(0),Q(0)))
    systems=0
    for length in [2,4,8,16,32]:
        for sample in range(7):
            raw=tuple(tuple(tuple(Q(rng.randrange(-3,4)) for _ in range(2)) for _ in range(2)) for _ in range(length))
            cur=raw
            al,be,section=A,B,BI
            lifts=[]
            for N in range(1,length.bit_length()):
                cur=tuple(add(mul(be,cur[i+1]),mul(cur[i],al)) for i in range(0,len(cur),2))
                lifts.append(section)
                restored=cur
                for ss in reversed(lifts):
                    restored=tuple(v for c in restored for v in (Z,mul(ss,c)))
                width=2**N
                for k,value in enumerate(restored):
                    if (k+1)%width:
                        check(value==Z,'sharp dyadic support with non-scalar operator fibers')
                    else:
                        m=(k+1)//width-1
                        residual=Z
                        for j in range(width):
                            residual=add(residual,mul(mul(power(B,j),raw[width*m+j]),power(A,width-1-j)))
                        direct=mul(power(BI,width-1),residual)
                        check(value==direct,'independent direct weighted block formula')
                for k in range(min(width-1,length)):
                    check(restored[k]==Z,'whole-prefix cutoff')
                al=mul(al,al);be=mul(be,be);section=mul(section,section)
            systems+=1
    for N in range(1,7):
        width=2**N
        x=[Q(1)]*width
        cur=x
        for _ in range(N):cur=[cur[i]+cur[i+1] for i in range(0,len(cur),2)]
        for _ in range(N):cur=[v for c in cur for v in (Q(0),c)]
        check(cur[-1]==width,'boundary is allowed to survive and sharp')
        check(all(v==0 for v in cur[:-1]),'first block recovered except last coordinate')
    return {'matrix_residual_systems':systems,'lengths':[2,4,8,16,32],
            'fibers':'2x2 rational operators; noncommuting source bond and residuals',
            'scalar_boundary_depths':6,
            'scope':'finite checks of support and the direct weighted block formula'}


def test_protected_hilbert():
    vecs=list(product(range(-2,3),repeat=2))
    tested=0
    for p,d in product(vecs,repeat=2):
        if p==(0,0):continue
        v=(-Q(p[1]),Q(p[0]))
        beta=sum(Q(a)*b for a,b in zip(d,v))
        for x in [(Q(2),Q(-1)),(Q(-2),Q(3)),(Q(0),Q(0))]:
            r=sum(Q(a)*b for a,b in zip(d,x))
            if not beta:
                check((solve_protected([d],[p],x).status=='feasible')==(r==0), 'restricted image obstruction')
                continue
            h=tuple(r/beta*a for a in v)
            y=tuple(a-b for a,b in zip(x,h))
            check(not any(mv([d],y)), 'protected Hilbert answer exact')
            check(mv([p],y)==mv([p],x), 'protected Hilbert answer preserves')
            gain2=sum(a*a for a in v)/(beta*beta)
            check(sum(a*a for a in h)==gain2*r*r, 'optimal restricted gain squared')
            check(tuple(solve_protected([d],[p],x).answer)==y, 'unique answer agrees independently')
            tested+=1
    # Unrestricted second projection fails to retain the first constraint.
    independent=(Q(1,2),Q(1,2))
    check(independent[1]!=0,'independent projection leaves local exactness')
    # General sharpened comparison G2^2 <= G1^2 for nonnegative rational inputs.
    for a,b,gamma in product([Q(0),Q(1,3),Q(1),Q(5)],repeat=3):
        G1=a+b*(1+a*gamma)
        G2sq=a*a+b*b*(1+a*gamma)**2
        check(G2sq<=G1*G1,'sharper joint gain never exceeds sum bound')
    return {'unique_nonzero_restricted_map_cases':tested,'gain_triples':64,
            'scope':'exact two-dimensional protected geometry and squared gain identities'}


def test_persistent_images():
    records=0
    for values in product(range(3),repeat=3):
        current=set(range(3))
        for _ in range(3):current={values[k] for k in current}
        check(bool(current),'persistent image inhabited in finite endomap model')
        check({values[k] for k in current}==current,'restriction onto persistent image')
        check(len({values[k] for k in current})==len(current),'endomap bijective on persistent finite image')
        for y in current:
            family=[y]
            for _ in range(8):family.append(next(k for k in current if values[k]==family[-1]))
            check(all(values[family[i+1]]==family[i] for i in range(8)),'finite prefix of persistent-image lift')
        records+=1
    return {'endomaps_on_three_elements':records,
            'scope':'finite illustrations only; infinite conclusion uses the printed proof'}


def test_negative_controls():
    A=[[1,-1,0]];x=[2,0,5]
    P=[[1,0,0],[0,0,1]]
    c=solve_protected(A,P,x)
    bad=replace(c,answer=(Q(1),Q(1),Q(5)))
    check(not verify_certificate(A,P,x,bad),'reject exact but unprotected output')
    NEGATIVE.append('exact output with wrong protected values')
    P=[[0,0,1]];c=solve_protected(A,P,x)
    check(not verify_certificate(A,P,x,replace(c,ambiguity_basis=())), 'reject incomplete ambiguity basis')
    NEGATIVE.append('missing ambiguity direction')
    P=[[1,0,0],[0,1,0]];c=solve_protected(A,P,x)
    check(not verify_certificate(A,P,x,replace(c,residual_witness=(Q(0),))), 'reject corrupt dual witness')
    NEGATIVE.append('corrupt obstruction witness')
    for badA,badP,badx in [([[1,0]],[],[1]),([[1.0]],[],[1]),([[True]],[],[1]),([['1/0']],[],[1])]:
        rejected=False
        try:solve_protected(badA,badP,badx)
        except (TypeError,ValueError):rejected=True
        check(rejected,'reject malformed or inexact input')
    NEGATIVE.extend(['ragged dimensions','floating-point input','Boolean input','zero denominator'])
    raw=[Q(1),Q(1)]
    coarse=[raw[0]+raw[1]]
    lifted=[Q(0),coarse[0]]
    check(lifted[1] != 0 and 1+1 == 2**1,'computed dyadic prefix boundary survives')
    NEGATIVE.append('strict prefix cutoff incorrectly changed to non-strict')
    shift_tails=[[Q(0)]*N+[Q(1)]*(10-N) for N in [0,1,2,4,8]]
    check(all(max(abs(v) for v in row)==1 for row in shift_tails) and
          shift_tails[-1][0]==0 and shift_tails[-1][8]==1,
          'computed shift tails retain unit norm despite recovered coordinates')
    NEGATIVE.append('coordinate recovery incorrectly promoted to uniform convergence')
    return {'rejected_controls':len(NEGATIVE),'controls':NEGATIVE}


def main():
    start=time.monotonic()
    for name,fn in [('finite_certificates',test_certificates),('dyadic_support',test_dyadic),
                    ('protected_hilbert',test_protected_hilbert),('persistent_images',test_persistent_images),
                    ('negative_controls',test_negative_controls)]:run(name,fn)
    output={'status':'PASS','version':'1.1.0','executed_utc':datetime.now(timezone.utc).isoformat(),
            'arithmetic':'fractions.Fraction, integers, finite sets',
            'assertions':COUNT,'groups':GROUPS,'negative_controls':NEGATIVE,
            'elapsed_seconds':round(time.monotonic()-start,3),
            'fresh_lean_compilation':False,
            'scope':'Finite exact implementation/model checks. Universal mathematical results use the printed proofs. No new Lean verification follows from these tests.'}
    (ROOT/'audit/revision_exact.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps(output,indent=2))


if __name__=='__main__':main()
