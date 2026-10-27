#!/usr/bin/env python3
"""Exact audit of the Hilbert 12 contracting seven-packet theta transport.

Author: Komorebi P.
This is a finite algebraic audit plus optional numerical diagnostics.
No algebraicity theorem, normalized CM comparison, or Hilbert 12 solution is claimed.

Use:
  python h12_contracting_seven_packet_verify.py
  python h12_contracting_seven_packet_verify.py --numeric
"""
from __future__ import annotations
import argparse
import sympy as sp

b=sp.symbols('b')
fb=b**3-7
M=sp.Matrix([[0,1,0],[-4,2,15],[-1,0,4]])
R=M.inv()
epsilon=2-b
rho=b*b+2*b+4
tau=(b*b+2*b)/15
sigma=-(b+2)/15
delta=(tau+2*sigma+4)/7
z0=sp.Rational(1,3)

def red(expr):
    e=sp.cancel(expr)
    numerator,denominator=sp.fraction(e)
    if denominator!=1:
        # The exact relations in this program have rational number denominators.
        numerator=sp.rem(sp.expand(numerator),fb,b)
        denominator=sp.rem(sp.expand(denominator),fb,b)
        return sp.cancel(numerator/denominator)
    return sp.rem(sp.expand(e),fb,b)

def check_zero(expr,label):
    val=red(expr)
    assert val==0, f'{label}: {val}'
    print('PASS',label)


def exact_audit():
    check_zero(epsilon*rho-1,'epsilon times rho equals one')
    assert R*M==sp.eye(3) and M*R==sp.eye(3)
    print('PASS integer lattice inverse')
    assert M.det()==R.det()==1
    print('PASS unit lattice determinants')
    check_zero(rho*z0-(z0+5*tau+1),'contracting fixed label carry')
    check_zero(rho*delta-(4*delta+8*tau-sigma),'seven-torsion inverse unit carry')
    check_zero(epsilon*delta-(2*delta+8*sigma+1),'forward unit carry')

    # Check that both arithmetic units preserve the actual fifth-divisor lattice.
    check_zero(epsilon*tau-(-4*sigma-1),'epsilon tau on lattice')
    check_zero(epsilon*sigma-(tau+2*sigma),'epsilon sigma on lattice')
    check_zero(epsilon/5-(3*sigma+sp.Rational(4,5)),'epsilon one fifth on lattice')
    check_zero(rho*tau-(8*tau+sigma+2),'rho tau on lattice')
    check_zero(rho*sigma-(-4*tau-1),'rho sigma on lattice')
    check_zero(rho/5-(3*tau+sp.Rational(4,5)),'rho one fifth on lattice')

    carries=[]
    for k in range(7):
        q, kp=divmod(4*k,7)
        a=5+8*k+q
        s=-k+2*q
        c=1+4*q
        carries.append((k,kp,a,s,c))
        check_zero(rho*(z0+k*delta)-(z0+kp*delta+a*tau+s*sigma+c),f'carry k={k}')
        assert a>=0 and s in (-1,0)
        if k>0:
            assert sp.Rational(k,7).q!=1 # No z_k belongs to the fifth-divisor lattice.
    assert (sp.Rational(1,3)*5).q!=1
    print('PASS conductor points outside fifth-divisor lattice (rational coordinates)')
    assert [k for k in range(7) if 4*k%7==k]==[0]
    assert all(4**3*k%7==k for k in range(7))
    print('PASS two primitive three-cycles and fixed conductor label')

    perm=sp.zeros(7)
    for k in range(7): perm[k,4*k%7]=1
    X=sp.symbols('X')
    assert sp.factor(perm.charpoly(X).as_expr())==(X-1)**3*(X**2+X+1)**2
    print('PASS seven-label permutation spectrum: 1^3, omega^2, omega-bar^2')
    N=M-2*sp.eye(3)
    assert all(int(v)%7==0 for v in N**3)
    assert any(int(v)%7!=0 for v in N**2)
    assert all(int(v)%7==0 for v in R**7-4*sp.eye(3))
    assert all(int(v)%7==0 for v in R**21-sp.eye(3))
    assert any(int(v)%7!=0 for v in R**3-sp.eye(3))
    assert all(int(v)%7==0 for v in R**3-sp.eye(3)-2*N-5*N**2)
    print('PASS ambient mod-seven unit has order 21, semisimple torsion slice has order 3')

    F=sp.symbols('F0:7'); C=sp.symbols('C0:7')
    gm=[C[k]*F[4*k%7] for k in range(7)]
    for label,(i,j,k) in [('plus',(1,4,2)),('minus',(3,5,6))]:
        x=F[i]/F[j]; y=F[k]/F[j]
        alpha=C[i]/C[j]; gamma=C[k]/C[j]
        check_zero(gm[i]/gm[j]-alpha/y,f'{label} primitive ratio X')
        check_zero(gm[k]/gm[j]-gamma*x/y,f'{label} primitive ratio Y')
        check_zero(gm[i]*gm[j]*gm[k]-(C[i]*C[j]*C[k])*F[i]*F[j]*F[k],f'{label} cycle norm')
        check_zero((F[j]**3)-(F[i]*F[j]*F[k])/(x*y),f'{label} cubic reconstruction')
    T=sp.Matrix([[0,-1],[1,-1]])
    assert T**3==sp.eye(2) and T**2+T+sp.eye(2)==sp.zeros(2)
    print('PASS two-dimensional monomial action of exact order three')

    # Finite-N telescope for a free family of abstract (nonzero) f values.
    # For each m: C_{j,m}=f_{m,j}/f_{m-1,4j}; choose j=2**m k (mod 7).
    for k in range(7):
        assert all((4*(2**m*k%7))%7==(2**(m-1)*k)%7 for m in range(1,11))
    print('PASS contraction telescope index: pi^{-m}(k)=2^m k modulo seven')
    print('Carry data:')
    for row in carries: print(' ',row)
    print('Exact audit passed. The algebraic-to-analytic special-value equality is not proved.')


def numerical_audit(precision=55,terms=3400):
    import mpmath as mp
    mp.mp.dps=precision
    omega=mp.exp(2j*mp.pi/3)
    beta=mp.root(7,3)*omega**2
    rt=beta**2+2*beta+4
    tt=-(beta**2+2*beta)/15
    ss=-(beta+2)/15
    tau_n=-tt
    dd=(tau_n+2*ss+4)/7
    base=mp.mpf(1)/3
    twopi=2j*mp.pi

    def gammalog(z):
        p=mp.exp(twopi*tt);q=mp.exp(twopi*ss);e=mp.exp(twopi*z)
        P=Q=E=Ei=mp.mpc(1); summ=mp.mpc(0)
        for n in range(1,terms+1):
            P*=p;Q*=q;E*=e;Ei/=e
            if n%5:summ+=(P*E-Q*Ei)/(n*(1-P)*(1-Q))
        return -5*summ

    def theta(z,period):
        q=mp.exp(twopi*period);e=mp.exp(twopi*z)
        return mp.qp(e,q)*mp.qp(q/e,q)

    def qq(z,period):
        return theta(z,period)**5/theta(5*z,5*period)

    def gammaF(z):
        shift=int(mp.floor((mp.im(z)+mp.im(tt))/mp.im(ss)))
        zr=z-shift*ss
        f=mp.exp(gammalog(zr))
        if shift>=0:
            for j in range(shift): f/=qq(zr+j*ss,tt)
        else:
            for j in range(shift,0):f*=qq(zr+j*ss,tt)
        return f

    def theta_carry(w,a,s):
        v=mp.mpc(1)
        if s>=0:
            for j in range(s):v/=qq(w+j*ss,tt)
        else:
            for j in range(s,0):v*=qq(w+j*ss,tt)
        w=w+s*ss
        if a>=0:
            for j in range(a):v*=qq(w+j*tau_n,ss)
        else:
            for j in range(a,0):v/=qq(w+j*tau_n,ss)
        return v

    f0=[gammaF(base+k*dd) for k in range(7)]
    f1=[gammaF(rt*(base+k*dd)) for k in range(7)]
    c=[]
    for k in range(7):
        q,j=divmod(4*k,7)
        a=5+8*k+q;s=-k+2*q
        c.append(theta_carry(base+j*dd,a,s))
    errs=[abs(f1[k]/(c[k]*f0[4*k%7])-1) for k in range(7)]
    print('NUMERIC |rho|=',mp.nstr(abs(rt),16))
    print('NUMERIC anchor relative error |F(0)/epsilon^2-1|=',
          mp.nstr(abs(gammaF(0)/(2-beta)**2-1),12))
    print('NUMERIC max relative theta-carry error across 7 labels=',mp.nstr(max(errs),12))
    for name,(i,j,k) in [('plus',(1,4,2)),('minus',(3,5,6))]:
        X0=f0[i]/f0[j];Y0=f0[k]/f0[j]
        X1=f1[i]/f1[j];Y1=f1[k]/f1[j]
        aa=c[i]/c[j]; gg=c[k]/c[j]
        E1=abs(X1/(aa/Y0)-1)
        E2=abs(Y1/(gg*X0/Y0)-1)
        print('NUMERIC',name,'X0=',mp.nstr(X0,18),'Y0=',mp.nstr(Y0,18))
        print('NUMERIC',name,'primitive errors=',mp.nstr(E1,12),mp.nstr(E2,12))
    print('These are floating-point diagnostics, not directed interval certificates.')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--numeric',action='store_true')
    parser.add_argument('--precision',type=int,default=55)
    parser.add_argument('--terms',type=int,default=3400)
    args=parser.parse_args()
    exact_audit()
    if args.numeric:numerical_audit(args.precision,args.terms)
