"""Exact polynomial controls for the written one-kind quartic root theorem.
Author: Komorebi P. Sturm counts here test finite graphs, not all graphs.
"""
from fractions import Fraction as F


def trim(p):
    p=list(map(F,p))
    while p and not p[-1]:p.pop()
    return p


def derivative(p):return trim([j*a for j,a in enumerate(p)][1:])


def divrem(a,b):
    a=trim(a);b=trim(b)
    if not b:raise ZeroDivisionError('Zero polynomial')
    q=[F(0)]*max(0,len(a)-len(b)+1)
    while a and len(a)>=len(b):
        j=len(a)-len(b);v=a[-1]/b[-1];q[j]=v
        for k,x in enumerate(b):a[j+k]-=v*x
        a=trim(a)
    return trim(q),a


def gcd(a,b):
    a=trim(a);b=trim(b)
    while b:a,b=b,divrem(a,b)[1]
    return [v/a[-1] for v in a] if a else []


def variations(signs):return sum(a!=b for a,b in zip(signs,signs[1:]))


def real_roots_with_multiplicity(p):
    p=trim(p)
    if not p:raise ValueError('Zero polynomial has no finite root count')
    if len(p)==1:return 0
    g=gcd(p,derivative(p));squarefree,rem=divrem(p,g);assert not rem
    chain=[squarefree,derivative(squarefree)]
    while chain[-1]:
        rem=divrem(chain[-2],chain[-1])[1]
        if not rem:break
        chain.append([-v for v in rem])
    plus=[1 if row[-1]>0 else -1 for row in chain]
    minus=[s*(-1)**(len(row)-1) for s,row in zip(plus,chain)]
    distinct=variations(minus)-variations(plus)
    return distinct+(real_roots_with_multiplicity(g) if len(g)>1 else 0)
