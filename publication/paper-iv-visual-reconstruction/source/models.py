"""Exact finite models and rational enclosures for Paper IV's visual appendix.

Series arrays store ordinary coefficients in w, not block-EGF coefficients.
SymPy rational arithmetic supplies the algebra. Fraction supplies all certification
bounds. mpmath is used only to suggest root brackets and display coordinates;
the bracket acceptance test does not trust its root finder.
"""
from __future__ import annotations
from fractions import Fraction as Q
from functools import lru_cache
from math import factorial, comb
import sympy as sp

w,z,x,r,s,u=sp.symbols('w z x r s u')

def conv(a,b,n):
    return [sp.expand(sum(a[k]*b[j-k] for k in range(j+1) if k<len(a) and j-k<len(b))) for j in range(n+1)]

def inverse(a,n):
    if a[0]!=1: raise ValueError('The examples require a unit series normalized to 1.')
    out=[sp.S.One]
    for j in range(1,n+1):out.append(sp.expand(-sum(a[k]*out[j-k] for k in range(1,min(j,len(a)-1)+1))))
    return out

@lru_cache(None)
def denominator(N,n):
    if N<1 or n<0:raise ValueError('N >= 1 and n >= 0 required')
    return tuple(sp.Rational((-1)**j,factorial(N*j)) for j in range(n+1))

@lru_cache(None)
def kappa(N,n):
    a=denominator(N,n);out=[sp.S.Zero]
    for j in range(1,n+1):out.append(sp.expand(-j*a[j]-sum(a[k]*out[j-k] for k in range(1,j))))
    return tuple(out)

@lru_cache(None)
def reciprocal(N,n):
    k=kappa(N,n);b=[sp.S.One]
    for j in range(1,n+1):b.append(sp.expand(r*sum(k[t]*b[j-t] for t in range(1,j+1))/j))
    return tuple(sp.expand(b[j]*factorial(N*j)) for j in range(n+1))

def parameter_recurrence(N,n):
    p=[sp.S.One]
    for j in range(1,n+1):
        p.append(sp.expand(-sum((-1)**k*comb(N*j-1,N*k)*p[j-k] for k in range(1,j))
                           -r*sum((-1)**k*comb(N*j-1,N*k-1)*p[j-k] for k in range(1,j+1))))
    return p

def generalized_power(a,exponent,n):
    # Independent binomial expansion (1+v)^alpha, truncated by degree.
    v=list(a);v[0]=0;power=[sp.S.One]+[sp.S.Zero]*n;out=power.copy();coeff=sp.S.One
    for k in range(1,n+1):
        power=conv(power,v,n);coeff=sp.expand(coeff*(exponent-k+1)/k)
        out=[sp.expand(A+coeff*B) for A,B in zip(out,power)]
    return out

def newton_matrix(N,n,param=r):
    k=kappa(N,n)
    return sp.Matrix(n,n,lambda i,j: param*k[i-j+1] if j<=i else -(i+1) if j==i+1 else 0)

def signed_shift(N):
    if N<1:raise ValueError('N >= 1 required')
    A=sp.zeros(N)
    for j in range(N-1):A[j+1,j]=1
    A[0,N-1]=-1
    return A

def section(N,j,t=z,degree=12,signed=False):
    return sp.expand(sum(sp.Rational((-1)**q if signed else 1,factorial(N*q+j))*t**(N*q+j)
                         for q in range((degree-j)//N+1)))

def trunc_total(expr,vars,degree):
    return sp.Add(*(c*sp.prod(v**e for v,e in zip(vars,p))
                    for p,c in sp.Poly(sp.expand(expr),*vars).terms() if sum(p)<=degree))

def project(expr,N,j,var=z):
    return sp.Add(*(c*var**p[0] for p,c in sp.Poly(sp.expand(expr),var).terms() if p[0]%N==j))

def normalized_inverse(N,j,n):
    a=[sp.Rational(factorial(j),factorial(N*k+j)) for k in range(n+1)]
    return tuple(inverse(a,n))

def appell(N,j,m,param=sp.S.One):
    n=m//N;a=[sp.Rational(factorial(j),factorial(N*k+j)) for k in range(n+1)]
    c=generalized_power(a,-param,n)
    return sp.expand(sum(sp.Rational(factorial(m),factorial(m-N*k))*c[k]*x**(m-N*k) for k in range(n+1)))

def theta(N,n):
    k=kappa(N,n);t=[sp.S.One]
    for j in range(1,n+1):t.append(sp.expand(sum((-1)**m*k[m]*(u**(N*m)+u)*t[j-m] for m in range(1,j+1))/j))
    return tuple(sp.expand(t[j]*factorial(N*j)) for j in range(n+1))

def atan_bounds(inv,k=60):
    q=Q(1,inv);v=sum(((-1)**j*q**(2*j+1)/Q(2*j+1) for j in range(k+1)),Q(0))
    term=(-1)**(k+1)*q**(2*k+3)/Q(2*k+3)
    return min(v,v+term),max(v,v+term)

@lru_cache(None)
def pi_bounds():
    a,b=atan_bounds(5,60);c,d=atan_bounds(239,18)
    return 16*a-4*d,16*b-4*c

def decimal_string(q:Q,digits=22):
    # Decimal output is rounded outward by the caller for bounds.
    sign='-' if q<0 else '';q=abs(q);scale=10**digits;n=q.numerator*scale//q.denominator
    return f'{sign}{n//scale}.{n%scale:0{digits}d}'

def fraction_record(q):return {'numerator':str(q.numerator),'denominator':str(q.denominator)}

def rounded_outward(pair,digits=70):
    scale=10**digits;lo,hi=pair
    return Q((lo.numerator*scale)//lo.denominator,scale),Q(-((-hi.numerator*scale)//hi.denominator),scale)


def D3_bounds(a:Q,terms=90,derivative=0):
    """Alternating Taylor enclosure at a >= 0; exact rational endpoints."""
    if a<0:raise ValueError('This certificate uses nonnegative real arguments')
    start=(derivative+2)//3
    total=sum(((-1)**j*a**(3*j-derivative)/factorial(3*j-derivative) for j in range(start,terms+1)),Q(0))
    n=terms+1;tail=(-1)**n*a**(3*n-derivative)/factorial(3*n-derivative)
    ratio=a**3/Q((3*n+1-derivative)*(3*n+2-derivative)*(3*n+3-derivative))
    if ratio>=1:raise ValueError('Tail monotonicity was not established')
    return min(total,total+tail),max(total,total+tail)

def D3_derivative_interval(a:Q,b:Q,terms=90):
    """Outward interval evaluation of D3' on [a,b], with Taylor tail."""
    if not 0<a<b:raise ValueError('Require 0 < a < b')
    low=Q(0);high=Q(0)
    for j in range(1,terms+1):
        p=3*j-1;aa=a**p/factorial(p);bb=b**p/factorial(p)
        if j%2:low-=bb;high-=aa
        else:low+=aa;high+=bb
    n=terms+1;tail=b**(3*n-1)/factorial(3*n-1)
    ratio=b**3/Q(3*n*(3*n+1)*(3*n+2))
    if ratio>=1:raise ValueError('Derivative tail is not decreasing')
    return low-tail,high+tail

def certify_cubic_roots(count=4,digits=20):
    import mpmath as mp
    out=[]
    with mp.workdps(90):
        for m in range(count):
            model=2*mp.pi/mp.sqrt(3)*(m+mp.mpf('0.5'))
            f=lambda t:mp.cos(mp.sqrt(3)*t/2)+mp.exp(-3*t/2)/2
            guess=mp.findroot(f,(model-mp.mpf('.08'),model+mp.mpf('.08')))
            scale=10**digits;k=int(mp.floor(guess*scale));a=Q(k,scale);b=Q(k+1,scale)
            alo,ahi=rounded_outward(D3_bounds(a));blo,bhi=rounded_outward(D3_bounds(b));dl,dh=rounded_outward(D3_derivative_interval(a,b))
            opposite=(ahi<0<blo) or (bhi<0<alo);monotone=dh<0 or dl>0
            if not(opposite and monotone):raise AssertionError(f'Bracket {m} failed exact verification')
            delta=guess-model;leading=(-1)**m/mp.sqrt(3)*mp.exp(-3*model/2)
            out.append({'model_index':m,'lower':fraction_record(a),'upper':fraction_record(b),
                'lower_decimal':decimal_string(a,digits),'upper_decimal':decimal_string(b,digits),
                'D3_lower_endpoint_interval':[fraction_record(alo),fraction_record(ahi)],
                'D3_upper_endpoint_interval':[fraction_record(blo),fraction_record(bhi)],
                'D3_derivative_interval':[fraction_record(dl),fraction_record(dh)],
                'opposite_endpoint_signs':True,'unique_in_bracket':True,'taylor_terms':90,
                'display_only':{'model':mp.nstr(model,20),'delta':mp.nstr(delta,15),'leading_delta':mp.nstr(leading,15),
                                'relative_displacement_error':mp.nstr(delta/leading-1,12)}})
    return out

def secant_ratio_interval(n):
    P=reciprocal(2,n)[n].subs(r,1);P=int(P)
    c=Q(P,2*factorial(2*n)*2**(2*n+1));a,b=pi_bounds()
    return c*a**(2*n+1),c*b**(2*n+1)
