#!/usr/bin/env python3
"""Pure cubic H12 closing audit and exact-rational interval enclosure.

Author: Komorebi P.
Uses only Python's standard library for the interval computation.
It DOES NOT prove the gamma value algebraic or its equality to U_alg.
Integer endpoints, explicit Taylor remainders, and an infinite-series tail
bound distinguish this calculation from floating-point recognition.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from math import factorial, isqrt
from collections import Counter
from pathlib import Path
import argparse
import json
import time

BITS = 224
SCALE = 1 << BITS


def ceildiv(a: int, b: int) -> int:
    if b <= 0:
        raise ValueError('positive divisor required')
    return -((-a) // b)


@dataclass(frozen=True)
class RI:
    """Closed real interval [lo/SCALE, hi/SCALE]."""
    lo: int
    hi: int

    def __post_init__(self):
        if self.lo > self.hi:
            raise ValueError('reversed interval')

    @staticmethod
    def of(x) -> 'RI':
        if isinstance(x, RI):
            return x
        if isinstance(x, float):
            raise TypeError('floats are not permitted')
        q = Fraction(x)
        return RI((q.numerator*SCALE)//q.denominator,
                  ceildiv(q.numerator*SCALE, q.denominator))

    def __add__(self, x):
        x=RI.of(x)
        return RI(self.lo+x.lo, self.hi+x.hi)
    __radd__=__add__

    def __neg__(self):
        return RI(-self.hi, -self.lo)

    def __sub__(self,x):
        return self + (-RI.of(x))

    def __rsub__(self,x):
        return RI.of(x) + (-self)

    def __mul__(self,x):
        x=RI.of(x)
        vals=[self.lo*x.lo,self.lo*x.hi,self.hi*x.lo,self.hi*x.hi]
        return RI(min(vals)//SCALE,ceildiv(max(vals),SCALE))
    __rmul__=__mul__

    def reciprocal(self):
        if self.lo <= 0 <= self.hi:
            raise ZeroDivisionError('interval contains zero')
        if self.hi < 0:
            return -(-self).reciprocal()
        return RI((SCALE*SCALE)//self.hi, ceildiv(SCALE*SCALE,self.lo))

    def __truediv__(self,x):
        return self*RI.of(x).reciprocal()

    def square(self):
        high=max(self.lo*self.lo,self.hi*self.hi)
        low=0 if self.lo<=0<=self.hi else min(self.lo*self.lo,self.hi*self.hi)
        return RI(low//SCALE,ceildiv(high,SCALE))

    def sqrt(self):
        if self.lo < 0:
            raise ValueError('negative lower bound')
        low=isqrt(self.lo*SCALE); high=isqrt(self.hi*SCALE)
        if high*high < self.hi*SCALE:
            high+=1
        return RI(low,high)

    def maxabs(self):
        return max(abs(self.lo),abs(self.hi))

    def contains(self,x):
        x=Fraction(x)
        return self.lo*x.denominator <= x.numerator*SCALE <= self.hi*x.denominator

    def width(self):
        return Fraction(self.hi-self.lo,SCALE)


@dataclass(frozen=True)
class CI:
    re: RI
    im: RI

    @staticmethod
    def of(x) -> 'CI':
        if isinstance(x, CI):
            return x
        return CI(RI.of(x), RI.of(0))

    def __add__(self,x):
        x=CI.of(x)
        return CI(self.re+x.re,self.im+x.im)
    __radd__=__add__

    def __neg__(self):
        return CI(-self.re,-self.im)

    def __sub__(self,x):
        return self+(-CI.of(x))

    def __rsub__(self,x):
        return CI.of(x)+(-self)

    def __mul__(self,x):
        x=CI.of(x)
        return CI(self.re*x.re-self.im*x.im,self.re*x.im+self.im*x.re)
    __rmul__=__mul__

    def conjugate(self):
        return CI(self.re,-self.im)

    def norm2(self):
        return self.re.square()+self.im.square()

    def reciprocal(self):
        d=self.norm2()
        if d.lo <= 0:
            raise ZeroDivisionError('complex box not separated from zero')
        return CI(self.re/d,(-self.im)/d)

    def __truediv__(self,x):
        return self*CI.of(x).reciprocal()

    def __rtruediv__(self,x):
        return CI.of(x)*self.reciprocal()

    def __pow__(self,n:int):
        if n<0:
            return self.reciprocal()**(-n)
        result=CI.of(1);x=self
        while n:
            if n&1:
                result=result*x
            x=x*x;n//=2
        return result

    def exp(self,terms:int=72):
        # Reduce the complex modulus using the l1 upper bound to <= 1/2.
        z=self; squarings=0
        while z.re.maxabs()+z.im.maxabs() > SCALE//2:
            z=z/2;squarings+=1
        term=CI.of(1);total=term
        for n in range(1,terms+1):
            term=term*z/n
            total=total+term
        # |tail| <= exp(1/2)*(1/2)^(N+1)/(N+1)! < 2/(N+1)!
        # The looser final bound is exact and sufficient at BITS=224.
        error=ceildiv(2*SCALE,factorial(terms+1))
        pad=RI(-error,error)
        total=CI(total.re+pad,total.im+pad)
        for _ in range(squarings):
            total=total*total
        return total


def atan_reciprocal(q:int,terms:int=130):
    """Rational enclosure from the alternating arctan series."""
    total=Fraction(0)
    for k in range(terms):
        total += Fraction((-1)**k,(2*k+1)*q**(2*k+1))
    next_term=Fraction((-1)**terms,(2*terms+1)*q**(2*terms+1))
    return min(total,total+next_term),max(total,total+next_term)


def pi_interval():
    a,b=atan_reciprocal(5);c,d=atan_reciprocal(239)
    low=16*a-4*d; high=16*b-4*c
    return RI(RI.of(low).lo,RI.of(high).hi)


def icbrt(n:int):
    lo=0;hi=1 << ((n.bit_length()+2)//3)
    if hi**3 == n:
        return hi
    while hi-lo>1:
        mid=(lo+hi)//2
        if mid**3 <= n:lo=mid
        else:hi=mid
    return lo


def data():
    sq3=RI.of(3).sqrt()
    omega=CI(RI.of(Fraction(-1,2)),sq3/2)
    ai=icbrt(7*SCALE**3)
    alpha=RI(ai,ai+1)
    beta=CI.of(alpha)*omega**2
    pi=pi_interval()
    twopii=CI(RI.of(0),2*pi)
    return omega,beta,twopii


def decimal_out(i:RI,places:int=45):
    """Outward decimal rendering, also without binary floating point."""
    scale=10**places
    low=(i.lo*scale)//SCALE
    high=ceildiv(i.hi*scale,SCALE)
    def fmt(n):
        sign='-' if n<0 else ''
        a=abs(n)
        return f'{sign}{a//scale}.{a%scale:0{places}d}'
    return '['+fmt(low)+', '+fmt(high)+']'


def box_out(z:CI,places=45):
    return {'real':decimal_out(z.re,places),'imag':decimal_out(z.im,places)}


def algebraic_candidate(omega,beta,twopii):
    # This is the retained, independently specified Gauss branch.
    zeta=(twopii*Fraction(3,7)).exp()
    chi=[None,CI.of(1),omega,omega**2,omega**2,omega,CI.of(1)]
    gauss=CI.of(0);power=CI.of(1)
    for a in range(1,7):
        power=power*zeta
        gauss=gauss+chi[a]*power
    xi=gauss/beta
    nu=(xi+beta/xi-beta**2)/3
    v=-beta**2*nu-2*nu**2
    Y=(4*beta**2+beta-14)*v**2+(11*beta-23)*v-beta**2+3*beta-3
    Z=((-2*beta**2+7*beta-8)*v**2+(-10*beta**2+11*beta+17)*v)/3+7-beta-beta**2
    u=(Y-(1+2*omega)*Z)/2
    return u,xi,v


def gamma_value(omega,beta,twopii,terms=3000,evaluation_point=Fraction(1,3)):
    tau=(beta**2+2*beta)/15
    t=-tau;s=-(beta+2)/15
    p=(twopii*t).exp();q=(twopii*s).exp()
    r=Fraction(471,500);small=Fraction(1,2)
    # Exact comparisons of squared absolute values with rational envelopes.
    assert p.norm2().hi*r.denominator**2 < r.numerator**2*SCALE
    assert q.norm2().hi*small.denominator**2 < small.numerator**2*SCALE
    pn=CI.of(1);qn=CI.of(1);summ=CI.of(0)
    if evaluation_point == Fraction(1,3):
        roots=[CI.of(1),omega,omega**2]
    elif evaluation_point == Fraction(1,4):
        ii=CI(RI.of(0),RI.of(1))
        roots=[CI.of(1),ii,CI.of(-1),-ii]
    else:
        raise ValueError('This certificate supports only the two stated rational points')
    period=len(roots)
    for n in range(1,terms+1):
        pn=pn*p;qn=qn*q
        if n%5:
            summ=summ+(pn*roots[n%period]-qn*roots[-n%period])/(n*(1-pn)*(1-qn))
    log_u=-5*summ
    # Rigorous absolute tail for real z=1/3, excluding multiples of five.
    tail=10*r**(terms+1)/((terms+1)*(1-r)**2*(1-small))
    err=ceildiv(tail.numerator*SCALE,tail.denominator)
    pad=RI(-err,err)
    log_u=CI(log_u.re+pad,log_u.im+pad)
    return log_u.exp(),log_u,tail,p,q


def action(x):
    k,l,j=x
    return ((4*k+5*l+j)%7,(4*l+5*j)%7,4*j%7)


def transport_audit():
    pts=[(k,l,j) for k in range(7) for l in range(7) for j in range(7)]
    ix={p:n for n,p in enumerate(pts)}
    perm=[ix[action(p)] for p in pts]
    assert perm[0]==0 and sorted(perm)==list(range(343))
    visited=set();orbits=[]
    for start in range(343):
        if start in visited:continue
        cyc=[];j=start
        while j not in visited:
            visited.add(j);cyc.append(j);j=perm[j]
        assert j==start;orbits.append(cyc)
    counts=Counter(map(len,orbits))
    assert counts=={1:1,3:2,21:16}
    # Check the full 21-step weighted return on every standard basis position.
    # The abstract f_m are exact positive rationals, deliberately non-arithmetic.
    def f(m,j):return Fraction((m+2)*(j+3)+5,m+j+7)
    for j in range(343):
        current=j; coefficient=Fraction(1)
        for m in range(21,0,-1):
            coefficient*=f(m,current)/f(m-1,perm[current])
            current=perm[current]
        assert current==j
        assert coefficient==f(21,j)/f(0,j)
    # Exact action of the fixed-point projector for arbitrary rational weights.
    for j in range(343):
        out_at_zero = (perm[j]==0)
        in_at_zero=(j==0)
        assert out_at_zero==in_at_zero
    # Fourier orthogonality at the fixed coordinate is exact modulo Phi_7.
    for x in pts:
        counts_res=[0]*7
        for a in pts:
            counts_res[sum(ai*xi for ai,xi in zip(a,x))%7]+=1
        if x==(0,0,0):assert counts_res==[343,0,0,0,0,0,0]
        else:assert counts_res==[49]*7
    return {'orbit_lengths':dict(counts),'weighted_21_step_checks':343,
            'fixed_projector_checks':343,'Fourier_orthogonality_checks':343}


def interval_selftest():
    tests=0
    samples=[Fraction(-7,3),Fraction(-1,100),Fraction(0),Fraction(1,7),Fraction(5,2)]
    for a in samples:
        for b in samples:
            ia=RI.of(a);ib=RI.of(b)
            assert (ia+ib).contains(a+b)
            assert (ia*ib).contains(a*b)
            tests+=2
            if b:
                assert (ia/ib).contains(a/b);tests+=1
    # exp(0) must enclose 1 exactly.
    e=CI.of(0).exp(); assert e.re.contains(1) and e.im.contains(0)
    return tests+1


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--terms',type=int,default=3000)
    parser.add_argument('--json',type=Path)
    args=parser.parse_args()
    if args.terms<1000:raise ValueError('Use at least 1000 terms for this closing audit')
    start=time.monotonic()
    result={'status':'analytic_arithmetic_equality_NOT_proved','interval_bits':BITS,
            'selftests':interval_selftest(),'transport':transport_audit()}
    omega,beta,twopii=data()
    ua,xi,v=algebraic_candidate(omega,beta,twopii)
    ug,logu,tail,p,q=gamma_value(omega,beta,twopii,args.terms)
    ratio=ug/ua;cube=ratio**3;diff=ratio-1
    bound=diff.re.maxabs()**2+diff.im.maxabs()**2
    digits=0
    for k in range(1,100):
        if bound*10**(2*k)<SCALE*SCALE:digits=k
        else:break
    assert digits>=40, f'Insufficient ratio enclosure: only {digits} digits'
    assert cube.re.lo > SCALE//2
    assert diff.norm2().hi*4 < SCALE
    # An enclosure containing zero does not certify exact equality.
    assert diff.re.contains(0) and diff.im.contains(0)
    quarter,_,_,_,_=gamma_value(omega,beta,twopii,args.terms,Fraction(1,4))
    quarter_distance=(quarter/ua-1).norm2()
    assert quarter_distance.lo*10000 > SCALE
    result.update({'negative_control_quarter_distance':'> 1/100',
                   'negative_control_quarter_value':box_out(quarter),
                   'terms':args.terms,'U_gamma':box_out(ug),'U_alg':box_out(ua),
                   'ratio':box_out(ratio),'ratio_cubed':box_out(cube),
                   'certified_ratio_distance_upper':f'10^-{digits}',
                   'certified_ratio_cubed_real_lower':'> 1/2',
                   'certified_branch_disk':'|U_gamma/U_alg-1| < 1/2',
                   'tail_exact_factored':f'10*(471/500)^({args.terms+1})/(({args.terms+1})*(29/500)^2*(1/2))',
                   'tail_dyadic_upper_numerator':ceildiv(tail.numerator*SCALE,tail.denominator),
                   'ratio_integer_endpoints':{'real':[ratio.re.lo,ratio.re.hi],
                                              'imag':[ratio.im.lo,ratio.im.hi],
                                              'common_denominator':SCALE},
                   'zero_imaginary_part_proved':False,
                   'elapsed_seconds':round(time.monotonic()-start,3)})
    # Do not print the several-thousand-digit rational tail in the summary.
    report={k:v for k,v in result.items() if not k.startswith('tail_')}
    print(json.dumps(report,indent=2))
    if args.json:
        args.json.write_text(json.dumps(result,indent=2)+'\n')

if __name__=='__main__':
    main()
