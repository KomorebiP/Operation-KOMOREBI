#!/usr/bin/env python3
"""Exact/modular corroboration of the Lean v20 skeleton atlas.

The universally quantified claims are Lean theorems, not consequences of these
finite checks. This script uses only Python's standard library. It tests exact
finite polynomial normalizations modulo declared powers of two, partitions,
synthetic nonconstant pointwise-unit lower factors, and small actual carry data.
It deliberately does not call the synthetic functions actual Euler residuals.
"""
from __future__ import annotations
import argparse
from collections import Counter
from math import factorial
from pathlib import Path
import hashlib
import json
import time


def v2(n: int) -> int:
    if not n:
        raise ValueError('Zero has no finite integer valuation')
    n = abs(n)
    return (n & -n).bit_length()-1


def mul(a: list[int], b: list[int], modulus: int) -> list[int]:
    out = [0]*(len(a)+len(b)-1)
    for i, x in enumerate(a):
        for k, y in enumerate(b):
            out[i+k] = (out[i+k]+x*y) % modulus
    return out


def add(a: list[int], b: list[int], modulus: int) -> list[int]:
    return [((a[i] if i<len(a) else 0)+(b[i] if i<len(b) else 0)) % modulus
            for i in range(max(len(a),len(b)))]


def affine(a: list[int], center: int, scale: int, modulus: int) -> list[int]:
    # Horner polynomial composition, distinct from factor-by-factor skeleton assembly.
    out = [0]
    for x in reversed(a):
        out = mul(out,[center,scale],modulus)
        out[0] = (out[0]+x) % modulus
    return out[:-1] if out[-1]==0 and len(out)>len(a) else out


def trim(a: list[int]) -> list[int]:
    while len(a)>1 and not a[-1]:
        a.pop()
    return a


def skeleton(j: int, modulus: int) -> list[int]:
    out=[1]
    for i in range(j):
        out=mul(out,[-i,1],modulus)
        out=mul(out,[-2*i-1,2],modulus)
    return out


def data(j: int, i: int) -> tuple[int,int,int]:
    k=max(i,j-1-i).bit_length()
    d=v2(factorial(i))+v2(factorial(j-1-i))
    return k,d,k+d


def local_unit(j: int, i: int, k: int, modulus: int) -> list[int]:
    out=[1]
    for n in range(1,i+1):
        v=v2(n)
        out=mul(out,[n>>v,1<<(k-v)],modulus)
    for n in range(1,j-i):
        v=v2(n)
        out=mul(out,[-(n>>v),1<<(k-v)],modulus)
    for l in range(j):
        out=mul(out,[2*i-2*l-1,1<<(k+1)],modulus)
    return out


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--precision',type=int,default=32)
    args=parser.parse_args()
    if args.precision<8 or args.precision>128:
        parser.error('precision must be between 8 and 128')
    if args.output.exists():
        raise FileExistsError(f'Refusing to overwrite {args.output}')
    started=time.monotonic()
    counts: Counter[str]=Counter()
    examples=[]
    def check(label: str, condition: bool, item: object) -> None:
        if not condition:
            raise AssertionError(f'{label}: {item!r}')
        counts[label]+=1
    P=args.precision
    small=[(j,i) for j in range(2,33) for i in range(j)]
    large=[(j,i) for j in (65,129,193,258,514)
           for i in sorted({0,1,j//3,j//2,j-2,j-1})]
    for j,i in small+large:
        k,d,t=data(j,i)
        modulus=1<<(P+t)
        full=affine(skeleton(j,modulus),i,1<<k,modulus)
        check('whole_polynomial_content', all(c%(1<<t)==0 for c in full),(j,i))
        reduced=[(c>>t)%(1<<P) for c in full]
        expected=[0]+local_unit(j,i,k,1<<P)
        check('all_coefficient_factorization',trim(reduced)==trim(expected),(j,i))
        q=local_unit(j,i,k,1<<P)
        check('local_unit_complete_binary_reduction',q[0]%2==1 and all(c%2==0 for c in q[1:]),(j,i))
        check('isolated_derivative_valuation',v2(full[1])==k+d,(j,i))
        # Direct derivative product at i, avoiding Taylor coefficient extraction.
        direct=(-1)**(j-1-i)*factorial(i)*factorial(j-1-i)
        for l in range(j):
            direct*=2*i-2*l-1
        check('direct_derivative_order',v2(direct)==d,(j,i))
        if j>=65:
            examples.append({'j':j,'i':i,'k':k,'d':d,'t':t})
    for j in range(2,513):
        m=(j-1).bit_length()
        cover=[0]*(1<<m)
        for i in range(j):
            k,_,_=data(j,i)
            for x in range(i%(1<<k),1<<m,1<<k):
                cover[x]+=1
        check('complete_disjoint_partition',all(n==1 for n in cover),j)
    # V=1+X+X^2+2X^3 is pointwise odd but NOT a constant binary polynomial.
    U=[1,2,0,4]
    V=[1,1,1,2]
    for j in range(2,25):
        for i in range(j):
            k,d,t=data(j,i)
            for delta in (t-1,t,t+1):
                content=min(delta,t)
                modulus=1<<(P+content)
                g=add(mul(skeleton(j,modulus),affine(U,-j,1,modulus),modulus),
                      [(1<<delta)*c%modulus for c in V],modulus)
                loc=affine(g,i,1<<k,modulus)
                check('synthetic_whole_content',all(c%(1<<content)==0 for c in loc),(j,i,delta))
                red=trim([(c>>content)%2 for c in loc])
                want=[1] if delta<t else ([1,1] if delta==t else [0,1])
                check('synthetic_constant_or_affine_certificate',red==want,(j,i,delta))
    for r,want in ((254,(2,0,0)),(510,(2,-1,1)),(1022,(2,-2,2))):
        bound=(r.bit_count()-1)//3
        lam=[3*q+(r+q).bit_count()-r.bit_count() for q in range(bound+1)]
        mu=min(lam);j=max(q for q,c in enumerate(lam) if c==mu)
        L=v2(r+j);delta=L-8
        check('actual_terminal_two_carry',(j,mu,delta)==want,r)
        roots=sum(data(2,i)[2]<=delta for i in range(2))
        check('terminal_two_threshold_count',roots==(0 if delta==0 else 2),r)
    # Why global theorem excludes j=1: an odd-valued V can yield a double root.
    p1=[0,-1,2]
    badV=[1,3,-1]
    check('j_one_negative_control',add(p1,badV,16)==[1,2,1],None)
    check('negative_control_lower_is_pointwise_odd',all(sum(c*x**i for i,c in enumerate(badV))%2==1 for x in range(16)),None)
    output={'status':'PASS','precision_bits':P,'counts':dict(counts),
            'registered_checks':sum(counts.values()),'seconds':time.monotonic()-started,
            'large_skeleton_examples':examples,
            'scope':'Finite corroboration only. Synthetic U,V are not Euler residuals. Universal conclusions are Lean theorems.',
            'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({k:output[k] for k in ('status','registered_checks','seconds','counts')},indent=2))

if __name__=='__main__':
    main()
