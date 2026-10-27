#!/usr/bin/env python3
"""Exact rational cross-checks for change of splitting on dimension-growing towers.

Finite implementation audit only. Infinite and all-level claims are in Lean.
No random draws, floating point, network calls, or external algebra library.
"""
from __future__ import annotations
from fractions import Fraction as Q
from pathlib import Path
import argparse, hashlib, json, platform, sys, time

Matrix = tuple[tuple[Q, ...], ...]
assertions = 0

def check(p: bool, msg: str) -> None:
    global assertions
    assertions += 1
    if not p:
        raise AssertionError(msg)

def zeros(m: int, n: int) -> Matrix:
    return tuple(tuple(Q(0) for _ in range(n)) for _ in range(m))

def eye(n: int) -> Matrix:
    return tuple(tuple(Q(i == j) for j in range(n)) for i in range(n))

def add(a: Matrix, b: Matrix) -> Matrix:
    assert len(a) == len(b) and len(a[0]) == len(b[0])
    return tuple(tuple(x+y for x,y in zip(ar,br)) for ar,br in zip(a,b))

def scale(c: Q, a: Matrix) -> Matrix:
    return tuple(tuple(c*x for x in row) for row in a)

def sub(a: Matrix, b: Matrix) -> Matrix:
    return add(a,scale(Q(-1),b))

def mul(a: Matrix, b: Matrix) -> Matrix:
    assert len(a[0]) == len(b)
    return tuple(tuple(sum((a[i][k]*b[k][j] for k in range(len(b))), Q(0))
                       for j in range(len(b[0]))) for i in range(len(a)))

def norm(a: Matrix) -> Q:
    return max(sum(map(abs,row),Q(0)) for row in a)

def supnorm(xs: list[Matrix]) -> Q:
    return max(map(norm,xs),default=Q(0))

def drop(n: int) -> Matrix:
    return tuple(tuple(Q(i == j) for j in range(n+2)) for i in range(n+1))

def section(n: int, a: Q) -> Matrix:
    return eye(n+1) + (tuple(a if j == 0 else Q(0) for j in range(n+1)),)

def defect(f: list[Matrix], beta: Q) -> list[Matrix]:
    return [sub(mul(drop(n),f[n+1]),mul(f[n],scale(beta,drop(n))))
            for n in range(len(f)-1)]

def correction(r: list[Matrix], beta: Q, a: Q) -> list[Matrix]:
    x = [zeros(1,1)]
    for n,rn in enumerate(r):
        x.append(mul(section(n,a),add(rn,mul(x[-1],scale(beta,drop(n))))))
    return x

def green_correction(r: list[Matrix], beta: Q, a: Q) -> list[Matrix]:
    out = [zeros(1,1)]
    for n in range(1,len(r)+1):
        total=zeros(n+1,n+1)
        for k in range(n):
            term=mul(section(k,a),r[k])
            for j in range(k+1,n):
                term=mul(mul(section(j,a),term),scale(beta,drop(j)))
            total=add(total,term)
        out.append(total)
    return out

def minus(xs: list[Matrix], ys: list[Matrix]) -> list[Matrix]:
    return [sub(x,y) for x,y in zip(xs,ys)]

def plus(xs: list[Matrix], ys: list[Matrix]) -> list[Matrix]:
    return [add(x,y) for x,y in zip(xs,ys)]

def repair(f: list[Matrix], beta: Q, a: Q) -> list[Matrix]:
    return minus(f,correction(defect(f,beta),beta,a))

def observable(f: list[Matrix], a: Q) -> list[Matrix]:
    return [f[0]] + [sub(f[n+1],mul(mul(section(n,a),drop(n)),f[n+1]))
                     for n in range(len(f)-1)]

def candidate(depth: int, family: int) -> list[Matrix]:
    return [tuple(tuple(Q(((i+1)*(j+2)*(family+1)+3*n+family)%11-5,
                               1+(i+j+n+family)%4) for j in range(n+1))
                  for i in range(n+1)) for n in range(depth+1)]

def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=Path('audit/splitting_change_exact.json'))
    args=parser.parse_args(); start=time.monotonic(); cases=0
    betas=[Q(0),Q(1,4),Q(1,2),Q(3,4)]
    pairs=[(Q(0),Q(1)),(Q(-1),Q(1)),(Q(1,3),Q(-1,2))]
    for beta in betas:
      for a,b in pairs:
       for depth in [1,2,4,7]:
        for family in range(3):
          f=candidate(depth,family);r=defect(f,beta)
          aa=correction(r,beta,a);ab=correction(r,beta,b)
          pa=repair(f,beta,a);pb=repair(f,beta,b)
          check(aa==green_correction(r,beta,a),'independent Green sum')
          check(defect(aa,beta)==r,'right inverse A')
          check(defect(ab,beta)==r,'right inverse B')
          check(supnorm(defect(minus(aa,ab),beta))==0,'difference lands in exact core')
          check(minus(pb,pa)==minus(aa,ab),'repair change sign')
          check(repair(pb,beta,a)==pb and repair(pa,beta,b)==pa,'cross retractions')
          check(observable(observable(f,b),a)==observable(f,b),'profile subspace independence')
          check(observable(pa,a)==observable(f,a),'protected profile A')
          check(observable(pb,b)==observable(f,b),'protected profile B')
          check(supnorm(minus(aa,ab))<=abs(a-b)/(1-beta)**2*supnorm(r),'two-gap perturbation')
          c=Q(-1,4);ac=correction(r,beta,c)
          check(plus(minus(aa,ab),minus(ab,ac))==minus(aa,ac),'transition cocycle')
          check(plus(pa,aa)==f and plus(pb,ab)==f,'chart reconstruction')
          # Independent residual family, not just defects of the candidate.
          raw=[tuple(tuple(Q((i+2*j+family+3*n)%7-3,1+(i+j)%3)
                               for j in range(n+2)) for i in range(n+1)) for n in range(depth)]
          check(defect(correction(raw,beta,a),beta)==raw,'all finite residuals lift')
          cases+=1
    f=[eye(n+1) for n in range(3)];beta=Q(1,2)
    pa=repair(f,beta,Q(0));pb=repair(f,beta,Q(1))
    check(pa[1]==((Q(1,2),Q(0)),(Q(0),Q(1))),'zero-section matrix')
    check(pb[1]==((Q(1,2),Q(0)),(Q(-1,2),Q(1))),'skew-section matrix')
    check(pa != pb,'splitting-independent repair is false')
    check(repair(pb,beta,Q(0)) != repair(pa,beta,Q(1)),'commutativity is false')
    # Mutants must be detected independently of positive-case counting.
    negatives={}
    try:
        assert minus(pb,pa)==minus(correction(defect(f,beta),beta,Q(1)),
                                  correction(defect(f,beta),beta,Q(0)))
    except AssertionError: negatives['reversed_transition_sign_rejected']=True
    try:
        assert pa==pb
    except AssertionError: negatives['false_splitting_independence_rejected']=True
    if len(negatives)!=2:raise AssertionError('negative controls failed')
    result={'status':'PASS','cases':cases,'positive_assertions':assertions,
      'negative_controls':negatives,'arithmetic':'fractions.Fraction exact rational',
      'python':sys.version,'platform':platform.platform(),'elapsed_seconds':time.monotonic()-start,
      'bounds':{'beta':list(map(str,betas)),'section_pairs':[[str(a),str(b)] for a,b in pairs],
                'depths':[1,2,4,7],'families':3},
      'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
      'nonclaims':['Not a universal proof','No floating-point tolerance','No empirical claim of novelty']}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
