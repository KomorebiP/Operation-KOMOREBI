#!/usr/bin/env python3
"""Exact finite corroboration only; it does not decide an infinite tower."""
from __future__ import annotations
from pathlib import Path
from itertools import product
from math import gcd
from collections import Counter
import json, time, hashlib, sys

Mat = tuple[int, int, int, int]
ONE: Mat = (1, 0, 0, 1)

def mul(x: Mat, y: Mat, m: int) -> Mat:
    a,b,c,d=x; e,f,g,h=y
    return ((a*e+b*g)%m,(a*f+b*h)%m,(c*e+d*g)%m,(c*f+d*h)%m)

def power(x: Mat, d: int, m: int) -> Mat:
    out=ONE
    while d:
        if d & 1: out=mul(out,x,m)
        x=mul(x,x,m); d//=2
    return out

def red(x: Mat,m: int)->Mat:
    return tuple(v % m for v in x)  # type: ignore[return-value]

def inv(x: Mat,m: int)->Mat:
    a,b,c,d=x; z=pow((a*d-b*c)%m,-1,m)
    return ((d*z)%m,(-b*z)%m,(-c*z)%m,(a*z)%m)

def require(ok: bool, message: str) -> None:
    if not ok: raise RuntimeError(message)

def main()->None:
    t=time.monotonic(); counts=Counter(); scalar=[]
    for p,d,maxlevel in [(2,2,10),(3,3,7)]:
        levels={}
        for k in range(1,maxlevel+1):
            m=p**k
            roots={x for x in range(m) if pow(x,d,m)==1}
            counts['scalar_candidates']+=m
            levels[k]=roots
            if k>1:
                projected={x%(p**(k-1)) for x in roots}
                require(projected<=levels[k-1],'root reduction lost an equation')
                scalar.append({'p':p,'degree':d,'prefix_exponent':k-1,
                    'roots_at_prefix':sorted(levels[k-1]),'prefixes_reached_from_next':sorted(projected),
                    'dead_at_next':sorted(levels[k-1]-projected)})
        if p==2:
            require(levels[4]=={1,7,9,15},'mod-16 control')
            require({x%16 for x in levels[5]}=={1,15},'mod-32 survival control')
        else:
            require(4 in levels[2] and 4 not in {x%9 for x in levels[3]},'cube control')
    matrix=[]; levels={}
    for k in range(1,5):
        m=2**k; roots=set(); units=0
        for x in product(range(m),repeat=4):
            counts['matrix_candidates']+=1
            if gcd(x[0]*x[3]-x[1]*x[2],m)!=1: continue
            units+=1; counts['matrix_unit_square_evaluations']+=1
            if mul(x,x,m)==ONE: roots.add(x)
        require(units==6*2**(4*(k-1)),'GL2 cardinality mismatch')
        levels[k]=roots
        item={'modulus':m,'all_units':units,'square_roots_of_identity':len(roots)}
        if k>1:
            reached={red(x,2**(k-1)) for x in roots}
            require(reached<=levels[k-1],'matrix root reduction failure')
            item.update({'reached_preceding_prefixes':len(reached),
                'preceding_prefixes_without_successor':len(levels[k-1]-reached)})
        matrix.append(item)
    # Exact finite local-gauge obstruction: individually attainable degree 1 and 2
    # targets, not simultaneously conjugate to powers of a shared lift.
    m=4; Fbar=(1,1,0,1); target1=Fbar; target2=ONE
    lifts=[x for x in product(range(m),repeat=4) if red(x,2)==Fbar]
    gauges=[x for x in product(range(m),repeat=4) if red(x,2)==ONE]
    attainable=0
    individual1=False; individual2=False
    for f,z0,z1 in product(lifts,gauges,gauges):
        counts['finite_gauge_tuples']+=1
        a=mul(mul(z0,f,m),inv(z0,m),m)
        b=mul(mul(z1,power(f,2,m),m),inv(z1,m),m)
        individual1 |= a==target1
        individual2 |= b==target2
        attainable += (a==target1 and b==target2)
        # Reducing the entire tuple preserves both target equations.
        require(red(a,2)==mul(mul(red(z0,2),red(f,2),2),inv(red(z0,2),2),2),'gauge reduction')
        require(red(b,2)==ONE,'square reduction')
    require(individual1 and individual2 and attainable==0,'shared correction negative control')
    result={'status':'PASS','kind':'exact finite corroboration, not an infinite-tower proof',
      'python':sys.version,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
      'seconds':time.monotonic()-t,'counts':dict(counts),'scalar_layers':scalar,'matrix_layers':matrix,
      'gauge_control':{'modulus':4,'Frobenius_residue':Fbar,'degree1_target':target1,
          'degree2_target':target2,'individual_prescriptions_attainable':True,
          'simultaneous_matching_tuples':attainable},
      'coverage':'Exhaustive scalar residues in the listed ranges; all GL2 matrices modulo 2,4,8,16; all 4096 listed finite gauge tuples. No random sampling.',
      'nonclaims':['No experimental decision of all-depth solvability','No effective universal survival bound','No arithmetic/global automorphy conclusion']}
    out=Path(__file__).with_name('EXACT_CHECKS.json');out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'counts':result['counts'],'seconds':result['seconds'],'matrix_layers':matrix},indent=2))

if __name__=='__main__': main()
