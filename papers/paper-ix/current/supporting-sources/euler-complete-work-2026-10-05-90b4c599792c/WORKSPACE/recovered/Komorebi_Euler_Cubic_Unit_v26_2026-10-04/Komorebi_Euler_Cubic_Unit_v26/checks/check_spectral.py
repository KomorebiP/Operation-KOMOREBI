#!/usr/bin/env python3
"""Exact audit for the spectral continuation. No floating p-adic approximation.
This checks finite identities, an analytic negative-control polynomial, and
finite integer evaluations. Universal infinite-series statements are in Lean.
"""
from __future__ import annotations
from collections import Counter
from fractions import Fraction as Q
from itertools import combinations
from math import comb, factorial
from pathlib import Path
import hashlib, json, platform, time, sys

COUNTS=Counter()
def check(group, condition, detail=None):
    COUNTS[group]+=1
    if not condition: raise AssertionError((group,detail))
def v2(x):
    x=Q(x)
    if not x: return None
    def vi(n):
        n=abs(n); return (n & -n).bit_length()-1
    return vi(x.numerator)-vi(x.denominator)
B=[Q(1)]
def bernoulli(n):
    while len(B)<=n:
        m=len(B)
        B.append(-sum((Q(comb(m+1,j))*B[j] for j in range(m)),Q(0))/Q(m+1))
    return B[n]
def beta(n):
    return Q(1) if n==0 else -Q(2**(2*n)*(2*n-1),factorial(2*n))*bernoulli(2*n)
def dbeta(n):
    return Q(1) if n==0 else (1-Q(2**(2*n-1)))*beta(n)
def weight(e,z):
    return (1-e)/(1-e*z)
def source(n):
    assert n>=0
    return Q(9**(n+1)-1,8*(n+1)*(2*n+1))
def packet(r,q,n,depleted=False):
    assert n>=q>=0
    b=dbeta if depleted else beta
    P=1
    for i in range(q): P*=(n-i)*(2*n-2*i-1)
    return Q(8**q)*b(r+q)/b(r)*P*source(n-q)
def det(A):
    A=[[Q(x) for x in row] for row in A]
    ans=Q(1);n=len(A)
    for i in range(n):
        p=next((j for j in range(i,n) if A[j][i]),None)
        if p is None:return Q(0)
        if p!=i:A[i],A[p]=A[p],A[i];ans=-ans
        pivot=A[i][i];ans*=pivot
        for j in range(i+1,n):
            c=A[j][i]/pivot
            for k in range(i+1,n):A[j][k]-=c*A[i][k]
    return ans

def run():
    start=time.monotonic()
    expected=[Q(1),Q(-1,2),Q(1,6),Q(0),Q(-1,30),Q(0),Q(1,42)]
    for n,b in enumerate(expected):check('Bernoulli benchmarks',bernoulli(n)==b,n)
    for r in range(1,33):
        e=Q(2**(2*r-1))
        check('beta valuation',v2(beta(r))==r.bit_count()-1,r)
        for q in range(9):
            z=Q(4**q)
            check('actual beta undepletion',beta(r+q)/beta(r)==dbeta(r+q)/dbeta(r)*weight(e,z),(r,q))
            for M in range(5):
                pref=1+sum((e**(m+1)*z**m*(z-1) for m in range(M)),Q(0))
                rem=e**(M+1)*z**M*(z-1)/(1-e*z)
                check('exact correction expansion',weight(e,z)==pref+rem,(r,q,M))
                if q:
                    check('exact remainder valuation',v2(rem)==(M+1)*(2*r-1)+2*M*q,(r,q,M))
    rows=[*range(1,25),31,47,63,95,127]
    for r in rows:
        m=max(0,(r.bit_count()-2)//2)
        for n in range(13):
            terms=[packet(r,q,n,True) for q in range(n+1)]
            S=sum((4**(m*q)*terms[q] for q in range(n+1)),Q(0))
            check('actual finite integer escape values',v2(S)==0,(r,n,m))
            e=Q(2**(2*r-1))
            actual=sum((packet(r,q,n) for q in range(n+1)),Q(0))
            via=sum((weight(e,Q(4**q))*terms[q] for q in range(n+1)),Q(0))
            check('integer residual undepletion',actual==via,(r,n))
    sets=[(1,2),(1,129),(2,5,9),(1,3,7,10)]
    sets += list(combinations(range(1,9),3))
    for qs in sets:
        M=[[4**(m*q)-4**((m-1)*q) for q in qs] for m in range(1,len(qs)+1)]
        value=det(M)
        product=1
        for q in qs: product*=4**q-1
        for i,j in combinations(range(len(qs)),2): product*=4**qs[j]-4**qs[i]
        cost=2*sum(q*(len(qs)-1-i) for i,q in enumerate(qs))
        check('Vandermonde determinant identity',value==product,qs)
        check('Vandermonde exact valuation',v2(value)==cost,qs)
        # One unit entry forces at least one moment with valuation no greater
        # than the determinant valuation (integral adjugate argument).
        a=[1]+[(-1)**i*2**i for i in range(1,len(qs))]
        obs=[sum(Q(M[i][j])*a[j] for j in range(len(qs))) for i in range(len(qs))]
        check('finite observation budget',min(v2(t) for t in obs if t)!=None and
              min(v2(t) for t in obs if t)<=cost,qs)
    # Fixed-parameter counterexample using precisely the proposed rational weights.
    p1=[Q(31031,84),Q(-3937,42),Q(155,28)]
    p2=[Q(-31115,84),Q(3937,42),Q(-127,28)]
    def family(e):
        return [Q(i==0)+weight(e,Q(4))*p1[i]+weight(e,Q(16))*p2[i] for i in range(3)]
    check('counterexample depleted double root',family(Q(0))==[Q(0),Q(0),Q(1)])
    check('counterexample actual double root',family(Q(8))==[Q(64),Q(-16),Q(1)])
    for p in (p1,p2):check('individual packet is squarefree',p[1]**2-4*p[0]*p[2]!=0)
    d1=[3*p1[i]+15*p2[i] for i in range(3)]
    check('nonzero first value defect',d1[0]==-4448)
    check('moved critical derivative',family(Q(8))[1]+2*family(Q(8))[2]*8==0)
    check('moved critical value',sum(family(Q(8))[i]*Q(8)**i for i in range(3))==0)
    # An even simpler fixed-center construction, valid at arbitrarily small
    # target dyadic epsilon; packets depend on that chosen target.
    for N in range(1,21):
        e=Q(2**N)
        A=5*(1-4*e)/(4*(1-e)); C=1-A
        check('same-center negative control',A+C==1 and weight(e,Q(4))*A+weight(e,Q(16))*C==1,N)
        check('same-center first defect nonzero',-(3*A+15*C)==45*e/(e-1)!=0,N)
    # Exact second-order drift coefficient; comparisons are polynomial algebra.
    for a in [Q(1),Q(2),Q(3,2)]:
        for b in [Q(-3),Q(0),Q(2)]:
            for c in [Q(0),Q(1),Q(4)]:
                for d in [Q(-1),Q(1)]:
                    for e in [Q(2),Q(8),Q(32)]:
                        y=-e*b/(2*a)
                        f=a*y*y+e*(b*y+c)+e*e*d
                        check('critical derivative model',2*a*y+e*b==0)
                        check('critical value model',f==e*c+e*e*(d-b*b/(4*a)))
    report={
      'status':'passed','arithmetic':'exact fractions and integers; no floating p-adic tolerance',
      'elapsed_seconds':round(time.monotonic()-start,6),'python':sys.version.split()[0],
      'platform':platform.platform(),'counts':dict(COUNTS),'total':sum(COUNTS.values()),
      'scope':{'r_undepletion':[1,32],'q_undepletion':[0,8],'expansion_order':[0,4],
               'integer_rows_r':rows,'integer_offsets':[0,12],
               'negative_control':'synthetic; NOT an Euler repeated root'},
      'not_claimed':['universal Euler simplicity','critical scalar nonvanishing for remaining families',
                     'a proof based on bounded experiments','reproduction of old quick-test counts'],
      'input_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
      'counterexample':{'epsilon':8,'p1':[str(v) for v in p1],'p2':[str(v) for v in p2],
                        'depleted':'x^2','undepleted_at_8':'(x-8)^2','first_defect_at_0':-4448}}
    out=Path(__file__).resolve().parents[1]/'evidence/spectral_exact_checks.json'
    out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':run()
