#!/usr/bin/env python3
"""Fresh bounded rational regression; does not certify universal identities."""
from fractions import Fraction as F
from math import factorial as fac, comb
from pathlib import Path
from collections import Counter
import hashlib, json, sys, time

M = 6
counts=Counter()
def check(x,y,kind):
    assert x==y, (kind,x,y)
    counts[kind]+=1

def conv(a,b):
    return [sum((a[k]*b[n-k] for k in range(n+1)),F(0)) for n in range(M+1)]

def pow_unit(a,r):
    # Direct generalized binomial expansion of (1+(a-1))^r.
    b=a[:]; b[0]=0
    term=[F(1)]+[F(0)]*M
    out=term[:]; c=F(1)
    for k in range(1,M+1):
        term=conv(term,b)
        c*=F(r-k+1,k)
        out=[x+c*y for x,y in zip(out,term)]
    return out

def kappas(a):
    # -log(1+b) by direct finite log series, independent of Newton recurrence.
    b=a[:];b[0]=0
    term=[F(1)]+[F(0)]*M;out=[F(0)]*(M+1)
    for k in range(1,M+1):
        term=conv(term,b)
        out=[x+F((-1)**k,k)*y for x,y in zip(out,term)]
    return [m*out[m] for m in range(M+1)]

def det(a):
    n=len(a)
    if n==0:return F(1)
    return sum(((-1)**j*a[0][j]*det([row[:j]+row[j+1:] for row in a[1:]]) for j in range(n)),F(0))

for N in range(1,6):
    a=[F((-1)**n,fac(N*n)) for n in range(M+1)]
    kap=kappas(a)
    for r in [F(-2),F(0),F(1,2),F(3)]:
        b=pow_unit(a,-r); P=[b[n]*fac(N*n) for n in range(M+1)]
        for n in range(1,M+1):
            rhs=-sum(((-1)**k*comb(N*n-1,N*k)*P[n-k] for k in range(1,n)),F(0))-r*sum(((-1)**k*comb(N*n-1,N*k-1)*P[n-k] for k in range(1,n+1)),F(0))
            check(P[n],rhs,'parameter_recurrence')
            check(n*b[n],r*sum((kap[k]*b[n-k] for k in range(1,n+1)),F(0)),'logarithmic_newton')
            bell=[F(1)]
            for j in range(1,n+1):
                bell.append(sum((comb(j-1,k-1)*r*fac(k-1)*kap[k]*bell[j-k] for k in range(1,j+1)),F(0)))
            check(P[n],F(fac(N*n),fac(n))*bell[n],'bell_polynomial')
            if n<=4:
                mat=[[r*kap[i-j+1] if i>=j else F(-(i+1)) if j==i+1 else F(0) for j in range(n)] for i in range(n)]
                check(b[n],det(mat)/fac(n),'newton_determinant')
        s=F(-1,3)
        check(conv(b,pow_unit(a,-s)),pow_unit(a,-r-s),'reciprocal_parameter_addition')
    # Tangent via direct product inverse then independent displayed recurrence.
    inv=pow_unit(a,-1)
    T=[N*fac(N*n+N-1)*kap[n+1] for n in range(M)]
    check(T[0],F(1),'tangent_initial')
    for n in range(1,M):
        check(T[n],(-1)**n-sum(((-1)**k*comb(N*n+N-1,N*k)*T[n-k] for k in range(1,n+1)),F(0)),'tangent_recurrence')
    for j in range(N):
        phi=[F(fac(j),fac(N*n+j)) for n in range(M+1)]
        C=[v*fac(N*n) for n,v in enumerate(pow_unit(phi,-1))]
        for n in range(M+1):
            check(sum((comb(N*n+j,N*q)*C[q] for q in range(n+1)),F(0)),F(n==0),'triangular_inverse')
        r=F(1,2);s=F(-2);x=F(2,3);y=F(-1,4)
        cr=pow_unit(phi,-r);cs=pow_unit(phi,-s);crs=pow_unit(phi,-r-s)
        def appell(m,c,x):
            return sum((F(fac(m),fac(m-N*n))*c[n]*x**(m-N*n) for n in range(m//N+1)),F(0))
        for m in range(0,7):
            check(appell(m,crs,x+y),sum((comb(m,q)*appell(q,cr,x)*appell(m-q,cs,y) for q in range(m+1)),F(0)),'appell_joint_convolution')
    H=[abs(v) for v in a]
    for u in [F(-1),F(0),F(1,2),F(2)]:
        hs=[H[n]*u**(N*n) for n in range(M+1)]
        theta=conv(pow_unit(hs,-1),pow_unit(H,-u))
        P1=[v*fac(N*n) for n,v in enumerate(pow_unit(a,-1))]
        Pu=[v*fac(N*n) for n,v in enumerate(pow_unit(a,-u))]
        for n in range(M+1):
            check(theta[n]*fac(N*n),(-1)**n*sum((comb(N*n,N*q)*P1[q]*u**(N*q)*Pu[n-q] for q in range(n+1)),F(0)),'theta_reconstruction')
            if n:
                check(n*theta[n],sum(((-1)**m*kap[m]*(u**(N*m)+u)*theta[n-m] for m in range(1,n+1)),F(0)),'theta_newton')
                if u==0 or (u==-1 and N%2==0):check(theta[n],F(0),'theta_trivial_factors')
        if N==1:check(theta,[(-2*u)**n/F(fac(n)) for n in range(M+1)],'N1_theta_boundary')
    if N==1:
        check(kap,[F(0),F(1)]+[F(0)]*(M-1),'N1_log_boundary')
        check(T,[F(1)]+[F(0)]*(M-1),'N1_tangent_boundary')

print(json.dumps({'status':'PASS','total_assertions':sum(counts.values()),'assertions_by_group':dict(counts),'arithmetic':'fractions.Fraction, exact rational','bounds':{'N':[1,5],'block_index':[0,6],'r':['-2','0','1/2','3'],'u':['-1','0','1/2','2'],'Appell_m':[0,6],'Newton_determinant_n':[1,4]},'non_claim':'Finite regression only; universal conclusions require the separate algebraic derivation.'},indent=2))
