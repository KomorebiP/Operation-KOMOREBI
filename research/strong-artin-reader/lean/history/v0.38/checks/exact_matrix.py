#!/usr/bin/env python3
"""Exact rational inverse certificates and exhaustive finite image comparisons."""
import itertools,json
from fractions import Fraction as Q
from pathlib import Path

def mul(A,B):
    return tuple(sum(A[2*i+k]*B[2*k+j] for k in range(2)) for i in range(2) for j in range(2))
def power(A,d):
    R=(1,0,0,1)
    for _ in range(d):R=mul(R,A)
    return R
def derivative(A,d):
    cols=[]
    for k in range(4):
        E=tuple(int(j==k) for j in range(4));col=[0]*4
        for i in range(d):
            W=mul(mul(power(A,i),E),power(A,d-1-i))
            col=[x+y for x,y in zip(col,W)]
        cols.append(col)
    return [[Q(cols[j][i]) for j in range(4)] for i in range(4)]
def inverse(J):
    M=[row[:]+[Q(i==j) for j in range(4)] for i,row in enumerate(J)]
    for k in range(4):
        t=next((i for i in range(k,4) if M[i][k]),None)
        if t is None:raise ValueError('Singular derivative over Q')
        M[k],M[t]=M[t],M[k];a=M[k][k];M[k]=[x/a for x in M[k]]
        for i in range(4):
            if i!=k:
                a=M[i][k];M[i]=[x-a*y for x,y in zip(M[i],M[k])]
    return [row[4:] for row in M]
def vp(n,p):
    s=0
    while n and n%p==0:n//=p;s+=1
    return s

def certificate(A,d,p):
    J=derivative(A,d);V=inverse(J)
    s=max(vp(x.denominator,p) for row in V for x in row)
    B=[[p**s*x for x in row] for row in V]
    for L,R in [(B,J),(J,B)]:
        assert all(sum(L[i][k]*R[k][j] for k in range(4))==p**s*(i==j) for i in range(4) for j in range(4))
    assert all(x.denominator%p for row in B for x in row)
    return J,B,s

def run_case(A,d,p):
    J,B,s=certificate(A,d,p);m=s+1;H=m+s;q=p**H;base=power(A,d)
    BM=[[x.numerator*pow(x.denominator,-1,q)%q for x in row] for row in B]
    targets={};accepted=set();images=set();deeper_images=set();tested=0;deeper=0
    for T in itertools.product(range(p**s),repeat=4):
        U=tuple((a+p**m*t)%q for a,t in zip(base,T));delta=tuple(u-a for u,a in zip(U,base))
        ok=all(sum(b*x for b,x in zip(row,delta))%q==0 for row in BM)
        if ok:accepted.add(U)
        F=tuple(a+p**m*t for a,t in zip(A,T));images.add(tuple(x%q for x in power(F,d)));tested+=1
    for T in itertools.product(range(p**(s+1)),repeat=4):
        F=tuple(a+p**m*t for a,t in zip(A,T));deeper_images.add(tuple(x%q for x in power(F,d)));deeper+=1
    assert images==accepted==deeper_images
    return dict(p=p,d=d,A=A,s=s,m=m,H=H,derivative=[[str(x) for x in row] for row in J],
        scaled_inverse=[[str(x) for x in row] for row in B],
        horizon_candidates=tested,one_level_deeper_candidates=deeper,accepted_targets=len(accepted),comparison='PASS')

def main():
    cases=[run_case((1,1,0,1),2,2),run_case((1,1,0,1),3,3),run_case((1,1,1,2),2,2)]
    A=(1,1,0,1);F=(1,1,8,1)
    assert mul(A,F)!=mul(F,A) and power(F,2)==(9,2,16,9)
    # Singular over Q is intentionally rejected, even though the center is invertible.
    try:certificate((1,0,0,-1),2,3)
    except ValueError:singular_rejected=True
    else:raise AssertionError('Singular derivative accepted')
    result=dict(status='PASS',cases=cases,total_horizon_candidates=sum(c['horizon_candidates'] for c in cases),
        total_deeper_candidates=sum(c['one_level_deeper_candidates'] for c in cases),
        singular_derivative_rejected=singular_rejected,scope='Exhaustive stated finite balls only; universal theorem is Lean proof')
    Path('computations/exact_matrix/results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
