#!/usr/bin/env python3
"""Exact integer corroboration of nonresonant 2x2 root towers.
Not a substitute for the uniform Lean proofs; exhaustive scopes and samples
are separately recorded. No floating point or external algebra package.
"""
from __future__ import annotations
from itertools import product
from pathlib import Path
from collections import Counter
import hashlib, json, random

COUNTS=Counter()
I=(1,0,0,1)
def mul(a,b,m):
    return ((a[0]*b[0]+a[1]*b[2])%m,(a[0]*b[1]+a[1]*b[3])%m,
            (a[2]*b[0]+a[3]*b[2])%m,(a[2]*b[1]+a[3]*b[3])%m)
def power(a,d,m):
    COUNTS['matrix_power_evaluations']+=1
    out=I
    for _ in range(d):out=mul(out,a,m)
    return out
def inv(a,m):
    z=pow((a[0]*a[3]-a[1]*a[2])%m,-1,m)
    return tuple(z*t%m for t in (a[3],-a[1],-a[2],a[0]))
def add(a,b,m):return tuple((x+y)%m for x,y in zip(a,b))
def reduce(a,m):return tuple(x%m for x in a)
def norm_matrix(f,d,p):
    cols=[]
    for j in range(4):
        e=tuple(int(i==j) for i in range(4));z=(0,0,0,0);f_j=I
        for _ in range(d):
            z=add(z,mul(mul(f_j,e,p),inv(f_j,p),p),p);f_j=mul(f_j,f,p)
        cols.append(z)
    return [[cols[j][i] for j in range(4)]for i in range(4)]
def solve(a,b,p):
    M=[list(row)+[y%p]for row,y in zip(a,b)]
    for j in range(4):
        pivot=next((i for i in range(j,4)if M[i][j]%p),None)
        if pivot is None:raise ValueError('singular norm')
        M[j],M[pivot]=M[pivot],M[j]
        unit=pow(M[j][j],-1,p);M[j]=[x*unit%p for x in M[j]]
        for i in range(4):
            if i!=j:
                t=M[i][j];M[i]=[(x-t*y)%p for x,y in zip(M[i],M[j])]
    return tuple(row[-1]for row in M)

def step(f,u,p,r,d,N):
    low=p**r;up=low*p;fd=power(f,d,up)
    error=mul(tuple((x-y)%up for x,y in zip(u,fd)),inv(fd,up),up)
    assert all(x%low==0 for x in error)
    x=solve(N,tuple((a//low)%p for a in error),p)
    perturb=tuple((a+low*b)%up for a,b in zip(I,x))
    result=mul(perturb,f,up)
    assert reduce(result,low)==reduce(f,low)
    assert power(result,d,up)==reduce(u,up)
    COUNTS['verified_lifting_steps']+=1
    return result

def main():
    fixtures=[(2,I,3),(2,(1,1,0,1),3),(3,I,2),(3,(1,1,0,1),2),
              (5,(1,1,0,1),2),(5,(1,0,0,2),3)]
    reports=[];rng=random.Random(350034)
    for p,f,d in fixtures:
        N=norm_matrix(f,d,p)
        for j in range(4):solve(N,tuple(int(i==j)for i in range(4)),p)
        q=p*p;base=power(f,d,p);images={}
        for corr in product(range(p),repeat=4):
            x=tuple((a+p*b)%q for a,b in zip(f,corr));u=power(x,d,q)
            assert u not in images,'nonunique root in alleged nonresonant fixture'
            images[u]=x
        targets={tuple((a+p*b)%q for a,b in zip(base,corr))
                 for corr in product(range(p),repeat=4)}
        assert set(images)==targets
        for u,x in images.items():assert step(f,u,p,1,d,N)==x
        COUNTS['exhaustive_first_layer_fibres']+=len(images)
        top=p**7
        for _ in range(32):
            target=tuple((a+p*rng.randrange(top//p))%top for a in base)
            current=f
            for r in range(1,7):
                current=step(current,reduce(target,p**(r+1)),p,r,d,N)
            assert power(current,d,top)==target
            COUNTS['sampled_six_step_towers']+=1
        reports.append({'prime':p,'residual_frobenius':f,'degree':d,
            'all_first_layer_roots_and_targets':p**4,'sampled_targets':32,
            'highest_modulus':top,'steps_per_tower':6})
    roots={r:[x for x in range(3**r)if pow(x,3,3**r)==1]for r in range(1,6)}
    assert roots[2]==[1,4,7]
    assert not any(x%9==4 for x in roots[3])
    assert all(1 in roots[r]for r in roots)
    assert set(x%9 for x in roots[3])=={1}
    COUNTS['exhaustive_scalar_candidates']=sum(3**r for r in range(1,6))
    report={'status':'PASS','arithmetic':'exact Python integers; modular operations',
        'seed':350034,'fixtures':reports,'counts':dict(COUNTS),
        'negative_control':{'target':'cube=1','roots_by_precision':roots,
                            'blocked_partial_root':{'value':4,'modulus':9,'next_modulus':27},
                            'different_full_branch':1},
        'scope':'Exhaustive first layers for the six listed residual matrices; deterministic samples at higher layers. Not all residual matrices or all high-precision targets.',
        'nonclaims':['does not replace Lean general proofs','does not certify infinite precision by finite computation','no arithmetic global or automorphic claim'],
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    path=Path(__file__).with_name('EXACT_CHECKS.json');path.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
