#!/usr/bin/env python3
"""Exact independent normalization checks; universal claims use the proof."""
import argparse, json
from math import comb
from pathlib import Path

def mul(a,b):
    c=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b): c[i+j]+=x*y
    return c

def add(a,b):
    return [(a[i] if i<len(a) else 0)+(b[i] if i<len(b) else 0) for i in range(max(len(a),len(b)))]

def trim(a):
    while a and not a[-1]: a.pop()
    return a

def v2(x):
    assert x
    x=abs(x)
    return (x&-x).bit_length()-1

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);args=p.parse_args()
    den=[1,0,-1,0,1];num=[0,2,0,2]
    # 2y/(1+y²)+6y³/(1+y⁶)=num/den.
    lhs=mul(add(mul([0,2],[1,0,0,0,0,0,1]),mul([0,0,0,6],[1,0,1])),den)
    rhs=mul(num,mul([1,0,1],[1,0,0,0,0,0,1]))
    assert trim(lhs)==trim(rhs)
    masses=[0]*16
    for i,z in ((1,2),(3,2),(7,-2),(9,-2),(13,2),(15,2)): masses[i]=z
    prod=mul(den,masses);reduced=[0]*16
    for i,z in enumerate(prod):reduced[i%16]+=z
    assert reduced==num+[0]*12
    assert all(masses[i]==masses[-i%16] for i in range(16))
    oddmass=sum(masses[i] for i in range(1,16,2) if ((i*i-1)//8)%2)
    assert sum(masses)==4 and oddmass==4
    nmax=24;e=[1]
    for n in range(1,nmax+1):e.append(-sum(comb(2*n,2*j)*e[j] for j in range(n)))
    assert e[:6]==[1,-1,5,-61,1385,-50521]
    b=[(1+3*9**n)*e[n] for n in range(nmax+1)]
    records=[]
    for s in range(5):
        for k in range(21):
            d=sum((-1)**(k-j)*comb(k,j)*b[s+j] for j in range(k+1))
            assert v2(d)==3*k+2
            records.append({'s':s,'k':k,'valuation':v2(d),'unit_mod32':(d//2**(3*k+2))%32})
    out={'rational_transform_identity':True,'mod16_group_ring_identity':True,
         'masses_mod16':masses,'pushforward_rho_mass_even':0,'pushforward_rho_mass_odd':1,
         'difference_checks':records,'scope':'Exact finite checks only; uniform proof is in EXACT_REGULARIZED_MOMENTS.md.'}
    Path(args.output).write_text(json.dumps(out,indent=2)+'\n')
    print('PASS: rational transform, residue masses, and 105 exact difference valuations.')
if __name__=='__main__':main()
