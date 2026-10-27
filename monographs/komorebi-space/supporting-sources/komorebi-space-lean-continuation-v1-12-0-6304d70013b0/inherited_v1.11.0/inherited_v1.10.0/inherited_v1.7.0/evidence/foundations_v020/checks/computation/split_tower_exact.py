#!/usr/bin/env python3
"""Exact finite checks for the split-tower formulas (standard library only).

This is supplementary computation, not a proof of an infinite theorem.
Domain: Fraction arithmetic, stages Q^(n+1), target truncation, source c*truncation.
Family: c in {0,1/4,1/2,3/4,7/8}; depths 1..12; six deterministic signed families.
Every case checks cancellation, protected rows, idempotence, reconstruction,
operator-sup-norm bound, and an independently evaluated finite Green sum.
Negative controls corrupt the recurrence sign and erase protected information.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import platform
import sys
import time
from typing import Sequence

Matrix = list[list[F]]
Tower = list[Matrix]


def zero(m: int, n: int) -> Matrix:
    return [[F(0) for _ in range(n)] for _ in range(m)]


def add(a: Matrix, b: Matrix) -> Matrix:
    assert len(a) == len(b) and all(len(x) == len(y) for x,y in zip(a,b))
    return [[x+y for x,y in zip(ar,br)] for ar,br in zip(a,b)]


def sub(a: Matrix, b: Matrix) -> Matrix:
    return [[x-y for x,y in zip(ar,br)] for ar,br in zip(a,b)]


def residual(f: Tower, c: F) -> Tower:
    return [[[f[n+1][i][j] - c*(f[n][i][j] if j<=n else 0)
              for j in range(n+2)] for i in range(n+1)] for n in range(len(f)-1)]


def correction(r: Tower, c: F, *, wrong_sign: bool=False) -> Tower:
    a = [zero(1,1)]
    sign = -1 if wrong_sign else 1
    for n,rn in enumerate(r):
        nxt = [[rn[i][j] + sign*c*(a[n][i][j] if j<=n else 0)
                for j in range(n+2)] for i in range(n+1)]
        a.append(nxt + [[F(0) for _ in range(n+2)]])
    return a


def green_sum(r: Tower, c: F) -> Tower:
    """Independent closed formula, not recursive evaluation."""
    a = [zero(1,1)]
    for n in range(1,len(r)+1):
        a.append([[sum((c**(n-1-k)*r[k][i][j] for k in range(n)
                        if i<=k and j<=k+1), F(0))
                   for j in range(n+1)] for i in range(n+1)])
    return a


def repair(f: Tower, c: F) -> Tower:
    return [sub(x,y) for x,y in zip(f,correction(residual(f,c),c))]


def observe(f: Tower) -> Tower:
    return [f[0]] + [zero(n,n+1)+[list(f[n][-1])] for n in range(1,len(f))]


def opnorm(a: Matrix) -> F:
    return max((sum(map(abs,row),F(0)) for row in a),default=F(0))


def tower_norm(f: Tower) -> F:
    return max(map(opnorm,f),default=F(0))


def candidate(depth: int, family: int) -> Tower:
    return [[[F(((n+1)*17+(i+1)*11+(j+1)*7+family*13)%23-11,
                 (i+j+family)%5+1)
              for j in range(n+1)] for i in range(n+1)] for n in range(depth+1)]


def scalar_text(x: F) -> str:
    return str(x)


def run() -> dict:
    start=time.monotonic()
    cases=checks=0
    cs=[F(0),F(1,4),F(1,2),F(3,4),F(7,8)]
    for c in cs:
        for depth in range(1,13):
            for family in range(6):
                f=candidate(depth,family)
                r=residual(f,c); a=correction(r,c); g=repair(f,c)
                assertions={
                    'right_inverse':residual(a,c)==r,
                    'exact_repair':all(all(x==0 for row in m for x in row) for m in residual(g,c)),
                    'observable_preserved':observe(g)==observe(f),
                    'idempotent':repair(g,c)==g,
                    'coordinate_reconstruction':[add(x,y) for x,y in zip(repair(observe(f),c),a)]==f,
                    'bound':tower_norm(a)<=tower_norm(r)/(1-c),
                    'independent_green_sum':a==green_sum(r,c),
                }
                if not all(assertions.values()):
                    raise AssertionError({'c':str(c),'depth':depth,'family':family,'checks':assertions})
                cases+=1;checks+=len(assertions)
    # Residuals not produced from candidates: check the right inverse on separately defined data.
    for c in cs:
        r=[[[F(((i+2)*7+(j+3)*5+n*11)%19-9,3) for j in range(n+2)]
             for i in range(n+1)] for n in range(12)]
        assert residual(correction(r,c),c)==r
        assert correction(r,c)==green_sum(r,c)
        checks+=2
    # Closed-form identity model at every checked finite level.
    identity=[[[F(i==j) for j in range(n+1)] for i in range(n+1)] for n in range(33)]
    fixed=repair(identity,F(1,2))
    for n,m in enumerate(fixed):
        expected=[[F(1,2)**(n-i) if i==j else F(0) for j in range(n+1)] for i in range(n+1)]
        assert m==expected
        checks+=1
    # Real mutation checks: deliberately corrupted output must be rejected.
    c=F(1,2); f=candidate(4,1);r=residual(f,c)
    mutation_checks={
        'wrong_propagation_sign_rejected':residual(correction(r,c,wrong_sign=True),c)!=r,
        'erased_protected_information_rejected':observe([zero(n+1,n+1) for n in range(5)])!=observe(f),
    }
    assert all(mutation_checks.values())
    # At c=1, finite primitives of persistent unit residuals grow linearly.
    r=[zero(n+1,n+2) for n in range(32)]
    for rn in r:rn[0][0]=F(1)
    a=correction(r,F(1))
    assert [tower_norm(a[:n+1]) for n in range(33)]==[F(n) for n in range(33)]
    script=Path(__file__).read_bytes()
    return {
        'status':'PASS','scope':'exact bounded finite assertion, supplementary to Lean proofs',
        'arithmetic':'fractions.Fraction over Q; no floating-point comparisons',
        'parameters':{'source_contractions':list(map(str,cs)),'depths':[1,12],'families':list(range(6)),
                      'randomness':False,'identity_formula_max_level':32},
        'candidate_cases':cases,'positive_assertions':checks+1,'mutation_controls':mutation_checks,
        'unit_propagation_primitive_norm_at_level_32':str(tower_norm(a)),
        'identity_level_3_diagonal':[str(fixed[3][i][i]) for i in range(4)],
        'python':sys.version,'platform':platform.platform(),
        'script_sha256':hashlib.sha256(script).hexdigest(),'elapsed_seconds':time.monotonic()-start,
        'non_claims':['Finite tests do not prove infinite-dimensional or all-level theorems.',
                      'No proof of a strict propagation gap for arbitrary towers.',
                      'No assertion that a fixed splitting is intrinsically canonical.']}


if __name__=='__main__':
    root=Path(__file__).resolve().parents[2]
    out=root/'audit/computation/SPLIT_TOWER_EXACT.json'
    out.parent.mkdir(parents=True,exist_ok=True)
    try:
        result=run()
    except Exception as exc:
        out.write_text(json.dumps({'status':'FAIL','exception':repr(exc)},indent=2)+'\n')
        raise
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
