#!/usr/bin/env python3
"""Exact finite audit of the v0.7 dyadic detail formulas.

Only Fraction arithmetic is used. These bounded checks audit an independent
implementation; they do not establish the infinite Lean theorems. No network,
randomness, numerical tolerance, or external matrix library is used.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as Q
from pathlib import Path
import datetime as dt
import hashlib
import json
import platform
import sys
import time

Matrix = tuple[tuple[Q, ...], ...]

def zero(m: int, n: int) -> Matrix:
    return tuple(tuple(Q(0) for _ in range(n)) for _ in range(m))

def eye(n: int) -> Matrix:
    return tuple(tuple(Q(i == j) for j in range(n)) for i in range(n))

def add(a: Matrix, b: Matrix) -> Matrix:
    assert len(a) == len(b) and len(a[0]) == len(b[0])
    return tuple(tuple(x+y for x, y in zip(ar, br)) for ar, br in zip(a, b))

def neg(a: Matrix) -> Matrix:
    return tuple(tuple(-x for x in row) for row in a)

def sub(a: Matrix, b: Matrix) -> Matrix:
    return add(a, neg(b))

def mul(a: Matrix, b: Matrix) -> Matrix:
    assert len(a[0]) == len(b)
    return tuple(tuple(sum((a[i][k]*b[k][j] for k in range(len(b))), Q(0))
        for j in range(len(b[0]))) for i in range(len(a)))

def norm(a: Matrix) -> Q:
    return max(sum(abs(x) for x in row) for row in a)

def fnorm(r: list[Matrix]) -> Q:
    return max(map(norm, r), default=Q(0))

def family(m: int, n: int, level: int, fixture: int) -> Matrix:
    return tuple(tuple(Q(((i+1)*(j+3)+7*level+5*fixture)%13-6,
        1+(i+j+fixture)%3) for j in range(n)) for i in range(m))

def down(m: int, n: int, alpha: Q) -> Matrix:
    return tuple(tuple(alpha*Q(i == j) for j in range(n)) for i in range(m))

def up(m: int, n: int, skew: Q) -> Matrix:
    return tuple(tuple(Q(i == j) if i < m else skew*Q(j == 0)
        for j in range(m)) for i in range(n))

def compose_restrictions(bonds: list[Matrix], i: int, j: int) -> Matrix:
    out = eye(len(bonds[i])) if i < len(bonds) else eye(len(bonds[-1][0]))
    for k in range(i, j):
        out = mul(out, bonds[k])
    return out

def block_sum(x: list[Matrix], y: list[Matrix], r: list[Matrix], i: int, j: int) -> Matrix:
    """Closed transported sum, independent of the pair implementation."""
    out = zero(len(y[i]), len(x[j-1][0]))
    for k in range(i, j):
        out = add(out, mul(mul(compose_restrictions(y, i, k), r[k]),
                           compose_restrictions(x, k+1, j)))
    return out

def coarsen(x: list[Matrix], y: list[Matrix], r: list[Matrix]) -> list[Matrix]:
    return [add(mul(y[k], r[k+1]), mul(r[k], x[k+1])) for k in range(0, len(r), 2)]

def lift(x: list[Matrix], y: list[Matrix], s: list[Matrix], c: list[Matrix]) -> list[Matrix]:
    out = []
    for n, a in enumerate(c):
        k = 2*n
        out += [zero(len(y[k]), len(x[k][0])), mul(s[k], a)]
    return out

def hidden(x: list[Matrix], y: list[Matrix], s: list[Matrix], r: list[Matrix]) -> list[Matrix]:
    j = lift(x, y, s, coarsen(x, y, r))
    return [sub(a,b) for a,b in zip(r,j)]

def channels(x: list[Matrix], y: list[Matrix], s: list[Matrix], r: list[Matrix]):
    c = coarsen(x, y, r)
    a = r[::2]
    nu = [sub(r[k+1], mul(s[k], mul(y[k], r[k+1]))) for k in range(0,len(r),2)]
    return a, nu, c

def synthesize(x: list[Matrix], s: list[Matrix], a, nu, c) -> list[Matrix]:
    out = []
    for n in range(len(c)):
        out += [a[n], add(nu[n], mul(s[2*n], sub(c[n],mul(a[n], x[2*n+1]))))]
    return out

def next_system(x,y,s):
    return ([mul(x[k],x[k+1]) for k in range(0,len(x),2)],
            [mul(y[k],y[k+1]) for k in range(0,len(y),2)],
            [mul(s[k+1],s[k]) for k in range(0,len(s),2)])

def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, default=Path('audit/dyadic_details_exact.json'))
    args=ap.parse_args()
    start=time.monotonic(); started=dt.datetime.now(dt.timezone.utc).isoformat()
    checks=0; pair_cases=0; cascade_cases=0
    def check(p: bool, label: str) -> None:
        nonlocal checks
        if not p: raise AssertionError(label)
        checks+=1
    for edges in (2,4,8,12):
      for alpha in (Q(0),Q(1,2),Q(1)):
       for skew in (Q(-1),Q(0),Q(1)):
        for fixture in range(3):
         for growth in (1,2):
          dims=[n//growth+1 for n in range(edges+1)]
          x=[down(dims[k],dims[k+1],alpha) for k in range(edges)]
          y=[down(dims[k],dims[k+1],Q(1)) for k in range(edges)]
          s=[up(dims[k],dims[k+1],skew) for k in range(edges)]
          r=[family(dims[k],dims[k+1],k,fixture) for k in range(edges)]
          a,nu,c=channels(x,y,s,r)
          h=hidden(x,y,s,r); j=lift(x,y,s,c)
          check(c==[block_sum(x,y,r,k,k+2) for k in range(0,edges,2)],'transported pair identity')
          check(coarsen(x,y,j)==c,'right inverse')
          check(coarsen(x,y,h)==[zero(len(t),len(t[0])) for t in c],'hidden kernel')
          check(hidden(x,y,s,h)==h,'hidden idempotence')
          check([add(b,d) for b,d in zip(h,j)]==r,'kernel reconstruction')
          check(synthesize(x,s,a,nu,c)==r,'triple reconstruction')
          check(fnorm(j)<=fnorm(c),'lift bound S=1')
          check(fnorm(c)<=2*fnorm(r),'coarsen bound')
          check(fnorm(h)<=3*fnorm(r),'hidden bound')
          check(fnorm(r)<=fnorm(h)+fnorm(c),'reverse budget')
          # Independent channel values, not merely those extracted from r.
          ac=[family(dims[k],dims[k+1],k,fixture+4) for k in range(0,edges,2)]
          bc=[family(dims[k+1],dims[k+2],k,fixture+7) for k in range(0,edges,2)]
          vc=[sub(b,mul(s[k],mul(y[k],b))) for k,b in zip(range(0,edges,2),bc)]
          cc=[family(dims[k],dims[k+2],k,fixture+11) for k in range(0,edges,2)]
          made=synthesize(x,s,ac,vc,cc)
          check(channels(x,y,s,made)==(ac,vc,cc),'independent channel inverse')
          check(fnorm(made)<=3*max(fnorm(ac),fnorm(vc))+fnorm(cc),'synthesis bound')
          for n,k in enumerate(range(0,edges,2)):
              check(mul(y[k],nu[n])==zero(dims[k],dims[k+2]),'vertical kernel')
              check(mul(y[k],s[k])==eye(dims[k]),'section law')
          # Check the candidate differential is the same one, via telescoping.
          f=[family(dims[k],dims[k],k,fixture+2) for k in range(edges+1)]
          df=[sub(mul(y[k],f[k+1]),mul(f[k],x[k])) for k in range(edges)]
          cd=coarsen(x,y,df)
          check(cd==[sub(mul(mul(y[k],y[k+1]),f[k+2]),
                   mul(f[k],mul(x[k],x[k+1]))) for k in range(0,edges,2)],'actual differential chain')
          pair_cases+=1
    for depth in range(6):
      for alpha in (Q(1,2),Q(1)):
       for skew in (Q(0),Q(1)):
        edges=2**depth
        dims=[n//4+1 for n in range(edges+1)]
        x=[down(dims[k],dims[k+1],alpha) for k in range(edges)]
        y=[down(dims[k],dims[k+1],Q(1)) for k in range(edges)]
        s=[up(dims[k],dims[k+1],skew) for k in range(edges)]
        original=[family(dims[k],dims[k+1],k,3) for k in range(edges)]
        r=original; systems=[]; details=[]
        for level in range(depth):
            systems.append((x,y,s)); details.append(hidden(x,y,s,r))
            r=coarsen(x,y,r); x,y,s=next_system(x,y,s)
        # Synthesis by reverse lifting, independent of a closed telescope.
        recovered=r
        for level in reversed(range(depth)):
            xx,yy,ss=systems[level]
            recovered=[add(a,b) for a,b in zip(details[level],lift(xx,yy,ss,recovered))]
        check(recovered==original,'finite cascade inverse including N=0')
        def restore_to_fine(value, scale):
            for k in reversed(range(scale)):
                xx,yy,ss=systems[k]; value=lift(xx,yy,ss,value)
            return value
        total=restore_to_fine(r,depth)
        for n in range(depth):
            term=restore_to_fine(details[n],n)
            total=[add(a,b) for a,b in zip(total,term)]
        check(total==original,'finite transported telescope')
        cascade_cases+=1
    # False-claim controls: these are expected rejections, not positive cases.
    one=((Q(1),),); minus=neg(one)
    mutations={}
    coarse=coarsen([one,one],[one,one],[one,minus])
    mutations['coarse_zero_implies_fine_zero_rejected']=(coarse==[zero(1,1)] and [one,minus]!=[zero(1,1),zero(1,1)])
    v=((Q(0),),(Q(1),)); projection=((Q(1),Q(0)),); inclusion=((Q(1),),(Q(0),))
    missing_vertical=mul(inclusion,mul(projection,v))
    mutations['discard_vertical_detail_rejected']=(missing_vertical!=v and mul(projection,v)==zero(1,1))
    half=((Q(1,2),),)
    mutations['untransported_sum_rejected']=(coarsen([one,half],[one,one],[one,one])!=[add(one,one)])
    if not all(mutations.values()): raise AssertionError('a mutation control did not reject its false claim')
    out={'status':'PASS','schema':'komorebi-dyadic-detail-finite-audit-v1',
      'started_at_utc':started,'elapsed_seconds':time.monotonic()-start,
      'argv':sys.argv,'python_version':platform.python_version(),
      'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
      'arithmetic':'fractions.Fraction, exact Q matrices, induced infinity norm',
      'randomness':False,'pair_configurations':pair_cases,'cascade_configurations':cascade_cases,
      'positive_assertions':checks,'false_claim_controls':mutations,
      'bounds':{'pair_edges':[2,4,8,12],'source_factors':['0','1/2','1'],
        'splitting_skew':['-1','0','1'],'fixtures':3,'dimension_growth_divisors':[1,2],
        'cascade_depths':[0,1,2,3,4,5],'cascade_source_factors':['1/2','1'],
        'cascade_splitting_skew':['0','1']},
      'non_claims':['Finite audit is not a universal proof.','No independent Lean kernel validation.',
        'No automatic target splittings, lossless compression, or infinite-depth convergence.']}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
