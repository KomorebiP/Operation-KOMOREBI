#!/usr/bin/env python3
"""Run exact identities and rational interval certificates, not a Lean build."""
from __future__ import annotations
import json,sys,hashlib
from pathlib import Path
from fractions import Fraction as Q
from math import factorial,comb
import sympy as sp
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'source'))
import models as M
z,w,x,r,s,u=M.z,M.w,M.x,M.r,M.s,M.u
records=[]
def ck(name,ok,kind='exact algebra'):
    if not bool(ok):raise AssertionError(name)
    records.append({'name':name,'status':'PASS','kind':kind})
def eq(a,b):return sp.expand(a-b)==0
# Root filters: direct selector and actual complex orbit formula for N=4.
f=sum((j+1)*z**j for j in range(13));omega=sp.I
for j in range(4):
    averaged=sp.expand(sum(omega**(-j*l)*f.subs(z,omega**l*z) for l in range(4))/4)
    ck(f'Root-of-unity average selects residue {j}',eq(averaged,M.project(f,4,j)))
    ck(f'Selector {j} is idempotent',eq(M.project(M.project(f,4,j),4,j),M.project(f,4,j)))
ck('Four selectors reconstruct the polynomial',eq(sum(M.project(f,4,j) for j in range(4)),f))
f=1+2*z+3*z**2+z**3;g=2+z+z**2
for k in range(3):
    rhs=sum(M.project(f,3,i)*M.project(g,3,j) for i in range(3) for j in range(3) if (i+j)%3==k)
    ck(f'Cyclic product residue {k}',eq(rhs,M.project(f*g,3,k)))
for N in [1,2,3,4,5]:
    J=M.signed_shift(N)
    ck(f'J_{N}^N = -I',J**N==-sp.eye(N))
    ck(f'J_{N} characteristic polynomial',eq(J.charpoly(x).as_expr(),x**N+1))
    # Finite exponential jet entry formula, including signed wrapping.
    A=sum((J**n*z**n/sp.factorial(n) for n in range(15)),sp.zeros(N))
    B=sp.Matrix(N,N,lambda p,q:(1 if p>=q else -1)*M.section(N,(p-q)%N,z,14,True))
    ck(f'All signed fundamental matrix entries, N={N}, through degree 14',A==B)
for N in [2,3,4]:
    for k in range(N):
        lhs=M.section(N,k,z+w,10,True)
        rhs=sum((-1)**((i+j)//N)*M.section(N,i,z,10,True)*M.section(N,j,w,10,True)
                for i in range(N) for j in range(N) if (i+j)%N==k)
        ck(f'Signed addition N={N}, packet={k}, total degree <=10',eq(lhs,M.trunc_total(rhs,(z,w),10)))
for N,j in [(3,0),(3,1),(3,2),(4,1),(4,3)]:
    params=[sp.Rational(j+m,N) for m in range(1,N+1) if j+m!=N]
    ck(f'Hypergeometric factorial normalization N={N}, j={j}, n<=7',all(
       sp.factorial(N*n+j)==sp.factorial(j)*N**(N*n)*sp.factorial(n)*sp.prod(sp.rf(a,n) for a in params) for n in range(8)))
# Reciprocal polynomials: independent binomial, derivative and Newton routes.
for N in range(1,6):
    pp=M.reciprocal(N,6);rr=M.parameter_recurrence(N,6)
    bb=M.generalized_power(M.denominator(N,6),-r,6)
    ck(f'Parameter and Newton recurrences agree, N={N}, n<=6',all(eq(a,b) for a,b in zip(pp,rr)))
    ck(f'Independent binomial expansion agrees, N={N}, n<=6',all(eq(pp[n],bb[n]*factorial(N*n)) for n in range(7)))
    ck(f'Leading r coefficients, N={N}, n=1..6',all(sp.Poly(pp[n],r).LC()==sp.Rational(factorial(N*n),factorial(n)*factorial(N)**n) for n in range(1,7)))
    ck(f'Parameter-addition law, N={N}, n<=5',all(eq(pp[n].subs(r,r+s),sum(comb(N*n,N*q)*pp[q]*pp[n-q].subs(r,s) for q in range(n+1))) for n in range(6)))
    ck(f'Newton determinant, N={N}, n=1..4',all(eq(M.newton_matrix(N,n).det()/factorial(n),pp[n]/factorial(N*n)) for n in range(1,5)))
ck('Printed secant polynomials',all(eq(a,b) for a,b in zip(M.reciprocal(2,3),[1,r,r*(3*r+2),r*(15*r*r+30*r+16)])))
ck('Secant order addition: 61+75+75+61=272',M.reciprocal(2,3)[3].subs(r,2)==272)
ck('Order-one exception P_{1,n}=r^n',all(eq(M.reciprocal(1,6)[n],r**n) for n in range(7)))
ck('Three distinct reciprocal coefficient rows',
    [int(M.reciprocal(2,3)[n].subs(r,1)) for n in range(4)]==[1,1,5,61] and
    [M.normalized_inverse(2,0,3)[n]*factorial(2*n) for n in range(4)]==[1,-1,5,-61] and
    [M.normalized_inverse(2,1,3)[n]*factorial(2*n) for n in range(4)]==[1,-sp.Rational(1,3),sp.Rational(7,15),-sp.Rational(31,21)])
for N in [1,2,3,4]:
    K=M.kappa(N,7);T=[N*factorial(N*n+N-1)*K[n+1] for n in range(7)]
    out=[sp.S.One]
    for n in range(1,7):out.append((-1)**n-sum((-1)**k*comb(N*n+N-1,N*k)*out[n-k] for k in range(1,n+1)))
    ck(f'Tangent recurrence and logarithmic coefficients N={N}',T==out)
# Differential Bell polynomial on the exact N=2 tangent and the cubic expression.
ck('N=2 Riccati equation',sp.trigsimp(sp.diff(sp.tan(z),z)-1-sp.tan(z)**2)==0)
D3=(sp.exp(-z)+2*sp.exp(z/2)*sp.cos(sp.sqrt(3)*z/2))/3
ck('Exact cubic denominator satisfies D3 triple derivative = -D3',sp.simplify(sp.diff(D3,z,3)+D3)==0)
# Multiplying higher Riccati by D^3 yields -D'''-D =0 without branch ambiguity.
D=sp.Function('D')(z);T=-sp.diff(D,z)/D
ck('Cubic Riccati polynomial reduces to original ODE',sp.simplify((-sp.diff(T,z,2)+3*T*sp.diff(T,z)-T**3)*D-sp.diff(D,z,3))==0)
for N,j in [(2,0),(2,1),(3,1),(4,2)]:
    polys=[M.appell(N,j,m) for m in range(9)]
    ck(f'Appell lowering N={N},j={j}, m<=8',all(eq(sp.diff(polys[m],x),m*polys[m-1]) for m in range(1,9)))
    ck(f'Appell translation N={N},j={j}, m=6',eq(polys[6].subs(x,x+u),sum(comb(6,k)*polys[k]*u**(6-k) for k in range(7))))
    phi=[sp.Rational(factorial(j),factorial(N*k+j)) for k in range(9//N+1)]
    ck(f'Finite inverse operator N={N},j={j}, m<=8',all(eq(sum(phi[k]*sp.diff(polys[m],x,N*k) for k in range(m//N+1)),x**m) for m in range(9)))
ck('Printed Appell quartic',eq(M.appell(2,0,4),x**4-6*x*x+5))
for N in [2,3,4]:
    th=M.theta(N,4);pp=M.reciprocal(N,4)
    ck(f'Theta convolution agrees with Newton, N={N}, n<=4',all(eq(th[n],(-1)**n*sum(comb(N*n,N*q)*pp[q].subs(r,1)*u**(N*q)*pp[n-q].subs(r,u) for q in range(n+1))) for n in range(5)))
    ck(f'Theta zero at u=0, N={N}',all(t.subs(u,0)==0 for t in th[1:]))
    if N%2==0:ck(f'Even theta zero at u=-1, N={N}',all(t.subs(u,-1)==0 for t in th[1:]))
ck('Odd order does not force u+1 factor',M.theta(3,1)[1].subs(u,-1)==2)
ck('Printed theta quadratic-index polynomial',eq(M.theta(2,2)[2],u*(u+1)*(5*u*u+u+2)))
# Exact N=4 identity and rotational orbit multiplicity.
D4=sp.cos(z/sp.sqrt(2))*sp.cosh(z/sp.sqrt(2))
ck('D4 factorization Taylor coefficients through z^20',eq(sp.series(D4,z,0,21).removeO(),M.section(4,0,z,20,True)))
ck('D4 differential equation',sp.simplify(sp.diff(D4,z,4)+D4)==0)
ck('Four normalized roots give one fourth power',all((sp.I**k*sp.Rational(3,2))**4==sp.Rational(81,16) for k in range(4)))
ck('Closed-disk zero counts retain endpoints',all(sum(1 for m in range(30) if sp.Rational(2*m+1,2)<=R)==sp.floor(R+sp.Rational(1,2)) for R in [sp.Rational(j,4) for j in range(41)]))
for N in [2,3,4,5]:
    aa=M.denominator(N,6);kk=M.kappa(N,6)
    # Independent logarithm expansion -log(1+v).
    v=list(aa);v[0]=0;power=[sp.S.One]+[0]*6;log=[sp.S.Zero]*7
    for k in range(1,7):
        power=M.conv(power,v,6);log=[sp.expand(a+sp.Rational((-1)**k,k)*b) for a,b in zip(log,power)]
    ck(f'Zero moment Newton coefficients versus formal log, N={N}',all(eq(kk[j],j*log[j]) for j in range(1,7)))
ck('Printed moments of cosine',[M.kappa(2,4)[j] for j in range(1,5)]==[sp.Rational(1,2),sp.Rational(1,6),sp.Rational(1,15),sp.Rational(17,630)])
ck('N4 full worked coefficient 69',M.reciprocal(4,2)[2].subs(r,1)==69)
ck('N4 full worked moment 17/10080',M.kappa(4,2)[2]==sp.Rational(17,10080))
ck('N4 tangent coefficient 34',4*factorial(7)*M.kappa(4,2)[2]==34)
# Moment closed forms at even integer arguments, checked against factorial recurrence.
for N in [2,4]:
    for q in range(1,4):
        A=sp.pi if N==2 else sp.sqrt(2)*sp.pi
        closed=(2**(N*q)-1)*sp.zeta(N*q)/A**(N*q)
        ck(f'Exact lattice zeta moment N={N}, q={q}',sp.simplify(closed-M.kappa(N,q)[q])==0)
# A finite Fredholm/product identity, not an infinite-dimensional proof.
K=sp.diag(sp.Rational(1,2),sp.Rational(1,5),sp.Rational(1,5))
ck('Multiplicity-sensitive finite determinant',eq((sp.eye(3)-w*K).det(),(1-w/2)*(1-w/5)**2))
ck('Multiplicity-sensitive finite traces',[sp.trace(K**j) for j in range(1,4)]==[sp.Rational(9,10),sp.Rational(33,100),sp.Rational(141,1000)])
# Machin identity tangent is exactly 1; branch follows from positive real/imag parts.
v=(1+sp.I/5)**4/(1+sp.I/239)
ck('Machin angle identity rational complex arithmetic',sp.simplify(sp.re(v)-sp.im(v))==0 and sp.re(v)>0)
pilo,pihi=M.pi_bounds();ck('Rational pi interval has width below 10^-70',pihi-pilo<Q(1,10**70),'rational enclosure')
ck('Pi interval lies strictly between 3 and 22/7',Q(3)<pilo<pihi<Q(22,7),'rational enclosure')
ratio_records=[]
for n in range(1,9):
    lo,hi=M.secant_ratio_interval(n)
    ck(f'Secant leading-term ratio n={n} enclosed below 1',Q(0)<lo<hi<Q(1),'rational enclosure')
    ck(f'Secant finite error n={n} below 3^(-2n-1)',1-lo<Q(1,3**(2*n+1)),'rational enclosure')
    ratio_records.append({'n':n,'lower':M.fraction_record(lo),'upper':M.fraction_record(hi)})
certs=M.certify_cubic_roots()
for c in certs:
    ck(f'Cubic root {c["model_index"]}: opposite endpoint signs',c['opposite_endpoint_signs'],'rational Taylor enclosure')
    ck(f'Cubic root {c["model_index"]}: derivative excludes zero throughout bracket',c['unique_in_bracket'],'rational Taylor enclosure')
# Deliberately false claims must fail, using exact scalar or matrix equality.
controls=[('Drop signed carry',M.signed_shift(3)**3==sp.eye(3)),
          ('Use ordinary instead of block binomial weights',eq(M.reciprocal(2,2)[2].subs(r,2),2*5+2*1)),
          ('Impose even theta factor at odd N',M.theta(3,1)[1].subs(u,-1)==0),
          ('Deduplicate a repeated eigenvalue',eq((sp.eye(3)-w*K).det(),(1-w/2)*(1-w/5))),
          ('Treat N=1 empty product as exp(-w)',eq(sp.series(sp.exp(-w),w,0,3).removeO(),1))]
for name,value in controls:
    if bool(value):raise AssertionError('Invalid control was accepted: '+name)
report={'status':'PASS','scope':'Exact finite identities, symbolic calculations and certified rational brackets. Not new Lean proofs.',
        'checks_passed':len(records),'checks':records,'invalid_controls_rejected':[name for name,_ in controls],
        'cubic_brackets':certs,'secant_ratio_enclosures':ratio_records,
        'pi_enclosure':{'lower':M.fraction_record(pilo),'upper':M.fraction_record(pihi)},
        'plotting_limit':'Smooth curves and asymptotic displacement values are sampled numerical visualizations, not global proof certificates.',
        'new_lean_verification':False}
(ROOT/'checks/EXACT_CHECKS.json').write_text(json.dumps(report,indent=2)+'\n')
print(f'PASS: {len(records)} exact/certified checks; {len(controls)} invalid controls rejected; {len(certs)} isolated cubic zero brackets.')
