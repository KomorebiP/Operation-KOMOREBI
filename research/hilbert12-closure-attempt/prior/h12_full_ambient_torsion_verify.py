#!/usr/bin/env python3
"""Full 343-point ambient cubic torsion and triptic distribution audit.
Author: Komorebi P.
Exact integer/rational identities, optional numerical checks of a classical
multiplication formula. Does NOT prove elliptic gamma algebraicity or Hilbert 12.
"""
import argparse
from collections import Counter
import sympy as sp

b=sp.symbols('b')
poly=b**3-7
rho=b*b+2*b+4
epsilon=2-b
tau=(b*b+2*b)/15
s=-(b+2)/15
delta=(tau+2*s+4)/7
eta=(s+2)/7
xi=sp.Rational(1,7)
z0=sp.Rational(1,3)
R=sp.Matrix([[8,-4,15],[1,0,0],[2,-1,4]])
M=R.inv()
u=sp.Matrix([1,2,4]);v=sp.Matrix([0,1,2]);w=sp.Matrix([0,0,1])
V=sp.Matrix.hstack(u,v,w)
H=sp.Matrix([[4,-4,15],[-4,1,0],[15,0,0]])

def rem(e):
    return sp.rem(sp.expand(sp.together(e)),poly,b)

def assert_zero(e,label):
    out=rem(e)
    assert out==0,(label,out)

def action(k,l,j):
    return ((4*k+5*l+j)%7,(4*l+5*j)%7,(4*j)%7)

def carry(k,l,j):
    U=4*k+5*l+j;V_=4*l+5*j;W=4*j
    qu,kp=divmod(U,7);qv,lp=divmod(V_,7);qw,jp=divmod(W,7)
    A=5+8*k+3*l+2*j+qu
    B=-k-2*l-j+2*qu+qv
    C=1-3*l-2*j+4*qu+2*qv+qw
    return (kp,lp,jp,A,B,C)

def exact_audit():
    assert V.det()==1
    assert all(int(a)%7==0 for a in R**21-sp.eye(3))
    assert any(int(a)%7!=0 for a in R**3-sp.eye(3))
    assert all(int(a)%7==0 for a in R**7-4*sp.eye(3))
    print('PASS complete lattice basis and order 21 mod seven')
    Nr=M-2*sp.eye(3)
    assert all(int(a)%7==0 for a in Nr*u)
    assert all(int(a)%7==0 for a in Nr*v-u)
    assert all(int(a)%7==0 for a in Nr*w-v)
    assert int((u.T*H*w)[0])%7==1
    assert int((u.T*H*v)[0])%7==0
    print('PASS full length-three eigenchain and nonzero socle-to-top pairing')
    assert_zero(rho*eta-(5*delta+4*eta+3*tau-2*s-3),'rho eta')
    assert_zero(rho*xi-(delta+5*eta+4*xi+2*tau-s-2),'rho one seventh')
    assert_zero(rho*delta-(4*delta+8*tau-s),'rho delta')
    print('PASS exact images of three generators')

    points=[(k,l,j) for k in range(7) for l in range(7) for j in range(7)]
    assert len({action(*p) for p in points})==343
    for p in points:
        k,l,j=p
        kp,lp,jp,A,B,C=carry(*p)
        assert (kp,lp,jp)==action(*p)
        lhs=rho*(z0+k*delta+l*eta+j*xi)
        rhs=z0+kp*delta+lp*eta+jp*xi+A*tau+B*s+C
        assert_zero(lhs-rhs,f'343 carry {p}')
    print('PASS 343 exact arithmetic unit carries')

    known=set();sizes=[];representatives=[]
    for p in points:
        if p in known:continue
        x=p;orbit=[]
        while x not in known:
            known.add(x);orbit.append(x);x=action(*x)
        assert x==p
        sizes.append(len(orbit));representatives.append((p,len(orbit)))
    assert Counter(sizes)==Counter({1:1,3:2,21:16})
    print('PASS full 343-point orbit decomposition', dict(Counter(sizes)))
    assert Counter(length for p,length in representatives if p[2]==0 and p[1]==0)==Counter({1:1,3:2})
    print('PASS embedded seven-point socle packet')

    # Characteristic 7 reduction: R is 4I+5N+N^2 with N=(M-2I).
    assert all(int(q)%7==0 for q in R-4*sp.eye(3)-5*Nr-Nr**2)
    assert all(int(q)%7==0 for q in R**3-sp.eye(3)-2*Nr-5*Nr**2)
    print('PASS semisimple order three and nontrivial order-seven shear')
    TT=sp.Matrix([[4,5,1],[0,4,5],[0,0,4]])
    dual=TT.inv_mod(7).T
    a=sp.Matrix([1,0,0]); seen=[]
    for m in range(1,22):
        a=(dual*a).applyfunc(lambda y:int(y)%7)
        seen.append(tuple(a))
    assert len(set(seen))==21 and seen[-1]==(1,0,0)
    print('PASS complementary dual character has a full 21-step orbit')

    # All points avoid the zero/pole lattice Lambda5: integer tau, sigma
    # coefficients force k=l=0, and then (1/3+j/7) is not an integer fifth.
    for k,l,j in points:
        if k==0 and l==0:
            assert (5*(sp.Rational(1,3)+sp.Rational(j,7))).q != 1
    print('PASS lattice-avoidance arithmetic for conductor-three packet')
    print('Exact audit passed, with no Gamma algebraicity claim.')


def gamma_log(z,t,s,N,mp):
    twopi=2j*mp.pi
    P=mp.exp(twopi*t);Q=mp.exp(twopi*s);E=mp.exp(twopi*z)
    pn=qn=en=ei=mp.mpc(1);acc=mp.mpc(0)
    for n in range(1,N+1):
        pn*=P;qn*=Q;en*=E;ei/=E
        if n%5:acc+=(pn*en-qn*ei)/(n*(1-pn)*(1-qn))
    return -5*acc


def numeric_distribution():
    import mpmath as mp
    mp.mp.dps=38
    t=mp.mpc('0.19','0.52');s=mp.mpc('-0.13','0.66');z=mp.mpf(1)/3
    N=210
    for n in (2,3,5,7):
        val=mp.mpc(0)
        for u in range(1-n,1):
            for v in range(n):
                zz=z+(u*t+v*s)/n
                for j in range(n):
                    val+=gamma_log(zz+mp.mpf(j)/n,t,s,N,mp)
        target=gamma_log(n*z,t,s,N,mp) if n%5 else mp.mpc(0)
        err=abs(val-target)
        print('NUMERIC distribution n=',n,'n^3=',n**3,
              'log residual',mp.nstr(err,12),'expected', 'F(nz)' if n%5 else '1')
    print('Numerics are not an interval certificate; the proof is geometric-series Fourier filtering.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--numeric',action='store_true')
    a=p.parse_args()
    exact_audit()
    if a.numeric:numeric_distribution()
