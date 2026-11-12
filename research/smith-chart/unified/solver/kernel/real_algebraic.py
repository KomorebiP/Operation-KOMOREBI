"""Author: Komorebi P. Exact one-real-algebraic-number arithmetic.
Standard library only. A defining squarefree rational polynomial and a rational
interval with exactly one real root are checked by Sturm's theorem. No floating
point evaluation, SymPy, SMT, CAD, or numerical eigensolver is trusted here.

Equality is accepted only when the remainder modulo the defining polynomial is
zero. For completeness of representation use a primitive element's minimal
polynomial. Reducible squarefree polynomials are sound but can be rejected when
an inverse is not a unit in the full quotient ring.
"""
from __future__ import annotations
from fractions import Fraction as F
from exact_polynomials import rational


def trim(p):
    p=list(map(rational,p))
    while len(p)>1 and not p[-1]:p.pop()
    return p or [F(0)]

def iszero(p):return not any(p)

def add(p,q):
    return trim([(p[i] if i<len(p) else F(0))+(q[i] if i<len(q) else F(0)) for i in range(max(len(p),len(q)))])

def neg(p):return [-x for x in p]

def sub(p,q):return add(p,neg(q))

def scale(p,c):return trim([x*c for x in p])

def mul(p,q):
    out=[F(0)]*(len(p)+len(q)-1)
    for i,a in enumerate(p):
        for j,b in enumerate(q):out[i+j]+=a*b
    return trim(out)

def divmod_poly(p,q):
    p=trim(p);q=trim(q)
    if iszero(q):raise ZeroDivisionError('Zero polynomial divisor')
    out=[F(0)]*max(1,len(p)-len(q)+1)
    while not iszero(p) and len(p)>=len(q):
        j=len(p)-len(q);c=p[-1]/q[-1];out[j]+=c
        p=sub(p,[F(0)]*j+scale(q,c))
    return trim(out),p

def gcd(p,q):
    p=trim(p);q=trim(q)
    while not iszero(q):p,q=q,divmod_poly(p,q)[1]
    return scale(p,1/p[-1]) if not iszero(p) else p

def xgcd(p,q):
    p=trim(p);q=trim(q);a,b=[F(1)],[F(0)];c,d=[F(0)],[F(1)]
    while not iszero(q):
        z,r=divmod_poly(p,q);p,q=q,r
        a,b=b,sub(a,mul(z,b));c,d=d,sub(c,mul(z,d))
    if iszero(p):return p,a,c
    t=1/p[-1];return scale(p,t),scale(a,t),scale(c,t)

def derivative(p):return trim([i*p[i] for i in range(1,len(p))])

def evaluate(p,t):
    v=F(0)
    for c in reversed(p):v=v*t+c
    return v

def sturm_sequence(p):
    p=trim(p)
    if len(p)<=1:raise ValueError('Root polynomial must be nonconstant')
    seq=[p,derivative(p)]
    while not iszero(seq[-1]):
        rem=neg(divmod_poly(seq[-2],seq[-1])[1])
        if iszero(rem):break
        # Divide by a positive coefficient magnitude only; preserves Sturm signs.
        rem=scale(rem,1/abs(rem[-1]));seq.append(rem)
    return seq

def variations(seq,x):
    signs=[]
    for p in seq:
        if x=='-inf':z=p[-1]*((-1)**(len(p)-1))
        elif x=='+inf':z=p[-1]
        else:z=evaluate(p,x)
        if z:signs.append(1 if z>0 else -1)
    return sum(a!=b for a,b in zip(signs,signs[1:]))

def root_count(seq,a,b):
    return variations(seq,a)-variations(seq,b)

def interval_eval(p,a,b):
    lo=hi=F(0)
    for c in reversed(p):
        products=[lo*a,lo*b,hi*a,hi*b]
        lo=min(products)+c;hi=max(products)+c
    return lo,hi

class RealField:
    def __init__(self, polynomial, interval):
        self.f=trim(polynomial)
        if len(self.f)<2:raise ValueError('Nonconstant defining polynomial required')
        self.f=scale(self.f,1/self.f[-1])
        if len(gcd(self.f,derivative(self.f)))!=1:raise ValueError('Defining polynomial is not squarefree')
        self.a,self.b=map(rational,interval)
        if self.a>=self.b:raise ValueError('Root interval must have distinct ordered endpoints')
        if evaluate(self.f,self.a)==0 or evaluate(self.f,self.b)==0:raise ValueError('Root interval endpoints cannot be roots')
        self.sturm=sturm_sequence(self.f)
        if root_count(self.sturm,self.a,self.b)!=1:raise ValueError('Interval does not isolate exactly one root')
        self.rational_root=None;self.refinements=0
    def element(self,x):
        if isinstance(x,Element):
            if x.field is not self:raise ValueError('Mismatched algebraic fields')
            return x
        if not isinstance(x,(list,tuple)):x=[rational(x)]
        return Element(self,divmod_poly(trim(x),self.f)[1])
    def refine(self):
        mid=(self.a+self.b)/2;z=evaluate(self.f,mid);self.refinements+=1
        if not z:self.rational_root=mid;return
        if root_count(self.sturm,self.a,mid)==1:self.b=mid
        else:self.a=mid
    def sign(self,p,max_refinements=20000):
        p=divmod_poly(trim(p),self.f)[1]
        if iszero(p):return 0
        common=gcd(self.f,p)
        if len(common)>1 and root_count(sturm_sequence(common),self.a,self.b)==1:return 0
        for _ in range(max_refinements):
            if self.rational_root is not None:
                z=evaluate(p,self.rational_root);return (z>0)-(z<0)
            lo,hi=interval_eval(p,self.a,self.b)
            if lo>0:return 1
            if hi<0:return -1
            self.refine()
        raise ValueError('Exact sign refinement budget exhausted; not a sign decision')

class Element:
    __slots__=('field','p')
    def __init__(self,field,p):self.field=field;self.p=trim(p)
    def __add__(self,o):
        o=self.field.element(o);return self.field.element(add(self.p,o.p))
    __radd__=__add__
    def __neg__(self):return self.field.element(neg(self.p))
    def __sub__(self,o):return self+-self.field.element(o)
    def __rsub__(self,o):return self.field.element(o)+-self
    def __mul__(self,o):
        o=self.field.element(o);return self.field.element(mul(self.p,o.p))
    __rmul__=__mul__
    def inverse(self):
        d,a,_=xgcd(self.p,self.field.f)
        if d!=[F(1)]:raise ValueError('Nonunit inverse; use a minimal polynomial field representation')
        return self.field.element(a)
    def __truediv__(self,o):return self*self.field.element(o).inverse()
    def __rtruediv__(self,o):return self.field.element(o)*self.inverse()
    def __bool__(self):return not iszero(self.p)
    def __eq__(self,o):
        try:o=self.field.element(o)
        except (ValueError,TypeError):return False
        return self.p==o.p
    def __pow__(self,k):
        if k<0:return self.inverse()**(-k)
        z=self.field.element(1);x=self
        while k:
            if k&1:z=z*x
            x=x*x;k//=2
        return z
    def sign(self):return self.field.sign(self.p)
    def serialize(self):return list(map(str,self.p))
    def __repr__(self):return f'Alg({self.serialize()})'


def linear_solve(A,b,field):
    n=len(A)
    if n!=len(b) or any(len(row)!=n for row in A):raise ValueError('Bad linear dimensions')
    M=[[field.element(z) for z in row]+[field.element(c)] for row,c in zip(A,b)]
    for k in range(n):
        pivot=next((j for j in range(k,n) if M[j][k]),None)
        if pivot is None:raise ValueError('Singular algebraic nodal system')
        M[k],M[pivot]=M[pivot],M[k];iv=M[k][k].inverse()
        M[k]=[z*iv for z in M[k]]
        for j in range(n):
            if j==k:continue
            u=M[j][k]
            if u:M[j]=[z-u*w for z,w in zip(M[j],M[k])]
    return [row[-1] for row in M]


def primitive_signed(p):
    """Clear denominators and divide by POSITIVE content, preserving all signs."""
    from math import gcd as igcd, lcm
    p=trim(p);den=1
    for c in p:den=lcm(den,c.denominator)
    ints=[c.numerator*(den//c.denominator) for c in p];g=0
    for c in ints:g=igcd(g,abs(c))
    return [F(c//g) for c in ints] if g else [F(0)]

def integer_sturm(p):
    p=primitive_signed(p);seq=[p,primitive_signed(derivative(p))]
    while not iszero(seq[-1]):
        rem=primitive_signed(neg(divmod_poly(seq[-2],seq[-1])[1]))
        if iszero(rem):break
        seq.append(rem)
    return seq
