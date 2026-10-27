#!/usr/bin/env python3
"""Exact finite contract in PROOF.md. No ABC conjecture is tested."""
from pathlib import Path
from fractions import Fraction
from math import gcd
import hashlib,json,platform,time

ROOT=Path(__file__).resolve().parent

def rank(matrix):
    a=[[Fraction(x) for x in row] for row in matrix]
    m,n=len(a),len(a[0])
    r=0
    for col in range(n):
        row=next((i for i in range(r,m) if a[i][col]),None)
        if row is None:continue
        a[r],a[row]=a[row],a[r]
        x=a[r][col]
        a[r]=[v/x for v in a[r]]
        for i in range(m):
            if i!=r:
                x=a[i][col]
                a[i]=[u-x*v for u,v in zip(a[i],a[r])]
        r+=1
        if r==m:break
    return r

def main():
    start=time.monotonic()
    tracked=[ROOT/'verify.py',ROOT/'PROOF.md']
    before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in tracked}
    for M in range(1,101):
        H=(M+2)//3
        assert abs(M-2*H)<=H
        assert (M-2*H)+2*H==M
        for u in range(-H+1,H):
            for v in range(-H+1,H):
                E=u+2*v
                assert not(E and E%M==0),(M,u,v,E)
    basis_cases=0
    for A in range(2,11):
        for B in range(1,A):
            if gcd(A,B)!=1:continue
            for D in range(1,7):
                coeff=[A**j*B**(D-j) for j in range(D+1)]
                rows=[]
                for j in range(D):
                    row=[0]*(D+1)
                    row[j],row[j+1]=-A,B
                    assert sum(u*v for u,v in zip(row,coeff))==0
                    rows.append(row)
                assert rank(rows)==D
                basis_cases+=1
    assert (1093**2+2)//3==398217
    after={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in tracked}
    assert before==after
    out={'status':'completed','assertion_tested':'Exact D1 minimum height in complete smaller cubes for M1to100, and ranks/zero evaluations of displayed rational-relation vectors in the stated domain.','bounds':{'M':[1,100],'A':[2,10],'B':'1<=B<A,gcd(A,B)=1','D':[1,6]},'minimum_height_cases':100,'independent_zero_vector_cases':basis_cases,'python':platform.python_version(),'runtime_seconds':time.monotonic()-start,'input_sha256_before':before,'input_sha256_after':after,'non_claims':['No proof or disproof of ABC.','No claim ruling out auxiliary polynomials with a proved nonvanishing estimate.']}
    (ROOT/'results.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ('status','minimum_height_cases','independent_zero_vector_cases')}))

if __name__=='__main__':main()
