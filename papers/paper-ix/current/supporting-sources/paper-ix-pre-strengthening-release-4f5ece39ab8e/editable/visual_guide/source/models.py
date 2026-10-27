#!/usr/bin/env python3
"""Exact finite models for Paper IX's reader appendix.

Integer and Fraction calculations only, except coordinates handed to the drawing
backend. A bounded check of these models is not a proof of a universal theorem.
"""
from __future__ import annotations
from fractions import Fraction as Q
from functools import lru_cache
from itertools import product
from math import comb, factorial, gcd
from typing import Callable, Iterable


def choose(n: int, k: int) -> int:
    return comb(n, k) if n >= 0 and 0 <= k <= n else 0


def val(x: Q | int, p: int) -> int | None:
    """Exact rational valuation; None denotes mathematical infinity at zero."""
    if p < 2:
        raise ValueError('p must be at least two (the caller supplies primality).')
    x = Q(x)
    if not x:
        return None
    a, b, v = abs(x.numerator), x.denominator, 0
    while a % p == 0:
        a //= p; v += 1
    while b % p == 0:
        b //= p; v -= 1
    return v


def at_least(x: Q | int, p: int, depth: int) -> bool:
    v = val(x, p)
    return v is None or v >= depth


def residue(x: Q | int, p: int, depth: int) -> int:
    if depth < 0:
        raise ValueError('Residue precision must be nonnegative.')
    x = Q(x); modulus = p ** depth
    if gcd(x.denominator, p) != 1:
        raise ValueError('Rational is not integral at this prime.')
    return (x.numerator * pow(x.denominator, -1, modulus)) % modulus


def difference(a: Iterable[Q | int], n: int, order: int, step: int = 1) -> Q:
    a = tuple(a)
    if min(n, order, step) < 0 or n + order * step >= len(a):
        raise ValueError('Difference stencil exceeds the available exact data.')
    return sum((Q((-1)**(order-k) * comb(order,k)) * a[n+k*step]
                for k in range(order+1)), Q(0))


def difference_table(a: Iterable[Q | int]) -> list[list[Q]]:
    table = [[Q(x) for x in a]]
    while len(table[-1]) > 1:
        row = table[-1]
        table.append([b-a for a,b in zip(row,row[1:])])
    return table


@lru_cache(maxsize=256)
def euler_packet(N: int, j: int, end: int) -> tuple[Q,...]:
    if N < 1 or not 0 <= j < N or end < 0:
        raise ValueError('Invalid packet width, address, or terminal row.')
    c = [Q(1)]
    for n in range(1,end+1):
        c.append(-sum((comb(N*n+j,N*q)*c[q] for q in range(n)), Q(0)) /
                 comb(N*n+j,N*n))
    return tuple(c)


def inverse_ordinary(a: Iterable[Q | int]) -> tuple[Q,...]:
    a = tuple(map(Q,a))
    if not a or not a[0]:
        raise ValueError('A reciprocal requires a nonzero constant coefficient.')
    b = [1/a[0]]
    for n in range(1,len(a)):
        b.append(-sum((a[k]*b[n-k] for k in range(1,n+1)), Q(0))/a[0])
    return tuple(b)


def packet_from_ordinary_inverse(N: int, j: int, end: int) -> tuple[Q,...]:
    # Independent ordinary-series route, not the cleared-binomial recurrence.
    src = [Q(factorial(j), factorial(N*n+j)) for n in range(end+1)]
    inv = inverse_ordinary(src)
    return tuple(factorial(N*n)*inv[n] for n in range(end+1))


def clearing_product(N: int, j: int, n: int) -> int:
    z=1
    for k in range(1,n+1): z *= comb(N*k+j,N*k)
    return z


def hurwitz(a: Iterable[Q | int], b: Iterable[Q | int], end: int) -> tuple[Q,...]:
    a,b=tuple(a),tuple(b)
    return tuple(sum((comb(n,k)*Q(a[k])*Q(b[n-k])
                      for k in range(n+1) if k<len(a) and n-k<len(b)),Q(0))
                 for n in range(end+1))


def theta(M: int, s: int, r: int, k: int) -> int:
    return sum((-1)**(k-a)*comb(k,a)*choose(M*a+s,r) for a in range(k+1))


@lru_cache(maxsize=32)
def classical_euler(end: int) -> tuple[int,...]:
    e=[1]
    for n in range(1,end+1): e.append(-sum(comb(2*n,2*k)*e[k] for k in range(n)))
    return tuple(e)


@lru_cache(maxsize=32)
def gamma(end: int) -> tuple[int,...]:
    e=classical_euler(end)
    return tuple(sum(comb(2*m,2*k)*e[k]*e[m-k] for k in range(m+1))
                 for m in range(end+1))


def odd_source(p: int, degree: int) -> int:
    if p <= 0 or p % 2 == 0:
        raise ValueError('The alternating source length must be positive and odd.')
    return sum((-1)**a*(2*a+1)**degree for a in range(p))


def odd_terms(p: int, n: int) -> tuple[int,...]:
    g=gamma(n)
    return tuple(comb(2*n,2*m)*g[m]*p**(2*m)*odd_source(p,2*(n-m))
                 for m in range(n+1))


@lru_cache(maxsize=32)
def beta(end: int) -> tuple[Q,...]:
    # Ordinary kernel coefficients, not factorial-scaled coefficients.
    return inverse_ordinary(Q(2**(2*m+1),factorial(2*m+2)) for m in range(end+1))


def kappa(m: int) -> Q:
    return beta(m)[m]*2**(2*m)*factorial(2*m)


def dyadic_source(n: int) -> Q:
    return Q(3**(2*n+2)-1,4*(2*n+1)*(2*n+2))


def dyadic_terms(n: int) -> tuple[Q,...]:
    b=beta(n)
    return tuple(b[m]*2**(2*m)*Q(factorial(2*n),factorial(2*n-2*m))*dyadic_source(n-m)
                 for m in range(n+1))


def dyadic_truncation(n: int, M: int) -> Q:
    return sum(dyadic_terms(n)[:M+1],Q(0))


def packet_offsets() -> tuple[tuple[int,...],tuple[int,...]]:
    return (1,1,4,2),(1,1,5,3)


def scaled_packet_map(j: int, depth: int) -> tuple[int,...]:
    _,ds=packet_offsets();N=2**depth;c=euler_packet(4,j,N-1)
    return tuple(residue((factorial(j)*v-factorial(j))/2**ds[j],2,depth) for v in c)


def rank_mod(rows: Iterable[Iterable[int]], p: int, ncols: int|None=None) -> int:
    a=[list(x) for x in rows]
    if not a: return 0
    n=len(a[0]) if ncols is None else ncols
    if any(len(r)!=n for r in a):raise ValueError('Ragged matrix.')
    a=[[x%p for x in r] for r in a]; r=0
    for j in range(n):
        k=next((k for k in range(r,len(a)) if a[k][j]),None)
        if k is None: continue
        a[r],a[k]=a[k],a[r]
        a[r]=[(x*pow(a[r][j],-1,p))%p for x in a[r]]
        for k in range(len(a)):
            if k!=r:
                c=a[k][j];a[k]=[(x-c*y)%p for x,y in zip(a[k],a[r])]
        r+=1
        if r==len(a):break
    return r


def matvec(a: list[list[int]], x: tuple[int,...], q: int) -> tuple[int,...]:
    return tuple(sum(c*y for c,y in zip(row,x))%q for row in a)


def correction_fiber(J: list[list[int]], residual: tuple[int,...], q: int,
                     ncols: int|None=None) -> list[tuple[int,...]]:
    d=len(J[0]) if J else (ncols or 0)
    return [t for t in product(range(q),repeat=d)
            if all((a+b)%q==0 for a,b in zip(residual,matvec(J,t,q)))]


def lift_univariate(coeff: tuple[int,...], p: int, x0: int, L: int, steps: int) -> list[dict]:
    def ev(x): return sum(c*x**i for i,c in enumerate(coeff))
    def der(x): return sum(i*c*x**(i-1) for i,c in enumerate(coeff) if i)
    out=[];x=x0
    for ell in range(L,L+steps):
        mod=p**ell
        if ev(x)%mod:raise ValueError('Start is not a root at its declared depth.')
        r=(ev(x)//mod)%p;j=der(x)%p
        digits=[t for t in range(p) if (r+j*t)%p==0]
        if len(digits)!=1:raise ValueError('Expected a unique nonsingular correction.')
        t=digits[0];z=x+mod*t
        out.append(dict(depth=ell,modulus=mod,x=x,residual=r,jacobian=j,digit=t,next=z))
        x=z
    return out


def roots_mod(coeff: tuple[int,...], q: int) -> list[int]:
    return [x for x in range(q) if sum(c*x**i for i,c in enumerate(coeff))%q==0]


def graph_roots(q: int, sign: int=1) -> tuple[tuple[int,int],...]:
    """Even branch of y+y^2+sign*t=0 modulo an even q."""
    out=[]
    for t in range(0,q,2):
        rr=[y for y in range(0,q,2) if (y+y*y+sign*t)%q==0]
        if len(rr)!=1:raise ValueError('Not a unique even root.')
        out.append((t,rr[0]))
    return tuple(out)


def crt_pair(a: int, m: int, b: int, n: int) -> int:
    if m<1 or n<1 or gcd(m,n)!=1:raise ValueError('Coprime positive moduli required.')
    return (a+m*((b-a)*pow(m,-1,n)%n))%(m*n)


def synthesis() -> dict:
    n,M,L=4,1,8;e=classical_euler(n)[n];approx=dyadic_truncation(n,M)
    target=(2*e)%2**L;approx_target=residue(2*approx,2,L)
    roots=[y for y in range(0,2**L,2) if (y*y+y-target)%2**L==0]
    return dict(n=n,M=M,depth=L,E=e,truncation=approx,coefficient_error=e-approx,
                target=target,approx_target=approx_target,even_roots=roots)
