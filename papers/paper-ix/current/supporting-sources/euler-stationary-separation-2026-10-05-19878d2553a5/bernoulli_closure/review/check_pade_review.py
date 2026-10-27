#!/usr/bin/env python3
"""Independent reset moment construction and exact Fraction Gaussian checks."""
from fractions import Fraction as F
from math import factorial
from pathlib import Path
import json,sys

def v(x):
    x=F(x)
    if not x:return 10**9
    def vi(a):return (abs(a)&-abs(a)).bit_length()-1
    return vi(x.numerator)-vi(x.denominator)

def determinant(A):
    A=[[F(x) for x in row] for row in A];out=F(1)
    for i in range(len(A)):
        j=next(j for j in range(i,len(A)) if A[j][i])
        if i!=j:A[i],A[j]=A[j],A[i];out=-out
        pivot=A[i][i];out*=pivot
        for k in range(i+1,len(A)):
            z=A[k][i]/pivot
            for j in range(i+1,len(A)):A[k][j]-=z*A[i][j]
            A[k][i]=0
    return out

def solve(A,b):
    A=[[F(x) for x in row]+[F(y)] for row,y in zip(A,b)]
    for i in range(len(A)):
        j=next(j for j in range(i,len(A)) if A[j][i])
        A[i],A[j]=A[j],A[i];z=A[i][i];A[i]=[x/z for x in A[i]]
        for k in range(len(A)):
            if k!=i:
                z=A[k][i];A[k]=[x-z*y for x,y in zip(A[k],A[i])]
    return [row[-1] for row in A]

def binary_hankel(n,shift):
    # Bit-packed independent Gaussian elimination over F_2.
    rows=[]
    for i in range(n):
        row=0
        for j in range(n):
            k=i+j+shift+1
            if k&(k-1)==0:row|=1<<j
        rows.append(row)
    for j in range(n):
        pivot=next((i for i in range(j,n) if (rows[i]>>j)&1),None)
        if pivot is None:return 0
        rows[j],rows[pivot]=rows[pivot],rows[j]
        for i in range(j+1,n):
            if (rows[i]>>j)&1:rows[i]^=rows[j]
    return 1

def main(output,source_path=None):
    bh=[binary_hankel(n,0) for n in range(129)]
    ch=[binary_hankel(n,1) for n in range(129)]
    assert all(bh) and all(ch)
    for n in range(1,129):
        k=n//2
        assert bh[n]==(ch[k] if n%2 else bh[k])
        assert ch[n]==bh[k+n%2]*ch[k]
    # h(w)=2sqrt(w)/sinh(2sqrt(w)); no Bernoulli routine is used.
    s=[F(4**q,factorial(2*q+1)) for q in range(21)]
    h=[F(1)]
    for q in range(1,21):h.append(-sum(s[j]*h[q-j] for j in range(1,q+1)))
    assert all(v(h[q])==q.bit_count() for q in range(1,21))
    determinants=[];denominators=[]
    for d in range(1,12):
        D=determinant([[h[i+j] for j in range(d)] for i in range(d)])
        assert v(D)==d-1;determinants.append({'rank':d,'valuation':v(D)})
        if d<=10:
            q=solve([[h[k-j] for j in range(1,d+1)] for k in range(d,2*d)],[-h[k] for k in range(d,2*d)])
            assert all(v(a)>=0 for a in q) and v(q[-1])==1
            error=h[2*d]+sum(q[j-1]*h[2*d-j] for j in range(1,d+1))
            assert v(error)==1
            denominators.append({'rank':d,'coefficient_valuations':[v(a) for a in q],'first_error_valuation':v(error)})
    source=(Path(source_path) if source_path else
            Path(__file__).resolve().parents[1]/'separation/carry_adapted/CARRY_ADAPTED_CHECKS.json')
    results=json.loads(source.read_text());gaps=[]
    expected=[-8,-1,7,14,24,31,39,46,55,62]
    for row in results['records']:
        for model in row['models']:
            d=model['rank'];E=6*d+sum((70+2*d)//(1<<j) for j in range(1,9))-84
            assert E==expected[d-1]==model['error_Gauss_valuation']
            assert model['hankel_determinant_valuation']==d-1
            assert model['denominator_coefficient_valuations_or_bounds']==denominators[d-1]['coefficient_valuations']
            if d>=2:
                assert model['center_difference_valuation_or_bound']==E+7
                assert model['critical_value_difference_valuation']==E
            if (row['T'],d) in [('0',3),('718787533',6)]:
                hval=model['critical_value_valuation'];assert hval<E
                assert row['actual']['critical_value_valuation']==hval
                gaps.append({'T':row['T'],'rank':d,'model_critical_valuation':hval,'error_valuation':E,'strict':True})
    out={'status':'passed','arithmetic':'exact Fraction Gaussian elimination from reciprocal sinh series','binary_hankel_maximum_dimension':128,'reset_moment_maximum_q':20,'hankel_checks':determinants,'denominators':denominators,'strict_transfers':gaps,'scope':'Independent finite orthogonal check; no universal critical-value nonvanishing.'}
    Path(output).write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main(sys.argv[1],sys.argv[2] if len(sys.argv)>2 else None)
