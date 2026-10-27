#!/usr/bin/env python3
"""Exact finite/matrix checks for the literal level-10 arithmetic dictionary.

This script does not construct p-adic representations or prove AI occurrence.
The reduction from the arithmetic objects is in reports/LATTICE113.md.
"""
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import json

class F:
    """Q[t]/(t^2+3t+3), exact, with v_F(t)=1 and v_F(3)=2."""
    def __init__(self, a=0, b=0): self.a, self.b = Q(a), Q(b)
    @staticmethod
    def cast(x): return x if isinstance(x, F) else F(x)
    def __add__(self, y):
        y = F.cast(y); return F(self.a+y.a, self.b+y.b)
    __radd__ = __add__
    def __neg__(self): return F(-self.a, -self.b)
    def __sub__(self, y): return self + -F.cast(y)
    def __mul__(self, y):
        y = F.cast(y)
        return F(self.a*y.a-3*self.b*y.b,
                 self.a*y.b+self.b*y.a-3*self.b*y.b)
    __rmul__ = __mul__
    def inv(self):
        n = self.a*self.a-3*self.a*self.b+3*self.b*self.b
        assert n != 0
        return F((self.a-3*self.b)/n, -self.b/n)
    def __eq__(self, y):
        y=F.cast(y); return (self.a,self.b)==(y.a,y.b)
    def val(self):
        def v3(q):
            if not q: return 10**9
            n,d=q.numerator,q.denominator; v=0
            while n%3==0: n//=3; v+=1
            while d%3==0: d//=3; v-=1
            return v
        return min(2*v3(self.a), 2*v3(self.b)+1)
    def residue(self):
        assert self.val() >= 0
        return self.a.numerator*pow(self.a.denominator,-1,3)%3
    def json(self): return [str(self.a), str(self.b)]

def matmul(a,b):
    return [[sum((a[i][k]*b[k][j] for k in range(3)),F())
             for j in range(3)] for i in range(3)]
def diag(x): return [[F(x[i] if i==j else 0) for j in range(3)] for i in range(3)]
def mpow(a,n):
    out=diag([1,1,1])
    for _ in range(n): out=matmul(out,a)
    return out
def msub(a,b): return [[a[i][j]-b[i][j] for j in range(3)] for i in range(3)]
def tr(a): return sum((a[i][i] for i in range(3)), F())

t=F(0,1)
Pi=[[F(),F(),t],[F(1),F(),F(-3)],[F(),F(1),F(-3)]]
Pi0=[[F(),F(),t],[F(1),F(),F()],[F(),F(1),F()]]
# Pi inverse follows directly by solving Pi*(x0,x1,x2)=(y0,y1,y2).
Pi_inv=[[3*t.inv(),F(1),F()],[3*t.inv(),F(),F(1)],
        [t.inv(),F(),F()]]
assert matmul(Pi,Pi_inv)==diag([1,1,1])
R=msub(Pi,Pi0)
R_grade=min(3*R[i][j].val()+i-j for i in range(3) for j in range(3))
assert R_grade==5
basis=[(1,0,0),(0,1,0),(0,0,1)]
matrices={}
for s in [1,5]:
    beta=mpow(Pi_inv,2*s); pis=mpow(Pi,s)
    values=[]; residues=[]
    for x in basis:
        row=[]; res=[]
        X=matmul(diag(x),pis)
        for y in basis:
            Y=matmul(diag(y),pis)
            z=tr(matmul(beta,msub(matmul(X,Y),matmul(Y,X))))
            expected=sum(x[i]*y[(i-s)%3]-y[i]*x[(i-s)%3] for i in range(3))%3
            assert z.residue()==expected
            row.append(z.json()); res.append(z.residue())
        values.append(row); residues.append(res)
    matrices[str(2*s)]={"exact_trace_coefficients_in_basis_1_t":values,
                         "residue_matrix":residues}

def add(x,y): return ((x%3+y%3)%3)+3*((x//3+y//3)%3)
def neg(x): return (-x%3)+3*(-(x//3)%3)
def mul(x,y):
    a,b=x%3,x//3; c,d=y%3,y//3
    return (a*c-b*d)%3 + 3*((a*d+b*c)%3)
def frob(x): return x%3 +3*(-(x//3)%3)
def trace(x): return 2*(x%3)%3
def b9(x,y):
    z=0
    for i in range(3):
        z=add(z,add(mul(x[i],y[(i+1)%3]),neg(mul(y[i],x[(i+1)%3]))))
    return z
def b3(x,y): return sum(x[i]*y[(i+1)%3]-y[i]*x[(i+1)%3] for i in range(3))%3

field=list(range(9)); triples=list(product(field,repeat=3))
assert all(frob(mul(x,y))==mul(frob(x),frob(y)) for x in field for y in field)
assert all(add(x,frob(x))==trace(x) for x in field)
rad=[]
fbasis=[tuple(v if j==i else 0 for j in range(3)) for i in range(3) for v in [1,3]]
for x in triples:
    assert b9(x,x)==0
    if all(trace(b9(x,y))==0 for y in fbasis): rad.append(x)
assert rad==[(i,i,i) for i in field]
pairchecks=0
for x in triples:
    fx=tuple(map(frob,x))
    for y in triples:
        assert trace(b9(fx,tuple(map(frob,y))))==trace(b9(x,y))
        assert trace(b9(x,y))==(-trace(b9(y,x)))%3
        pairchecks+=1
base=list(product(range(3),repeat=3))
for x in base:
    for y in base:
        assert trace(b9(x,y))==2*b3(x,y)%3
base_rad=[x for x in base if all(b3(x,y)==0 for y in basis)]
assert base_rad==[(i,i,i) for i in range(3)]
# Unique representative (x0-x2,x1-x2,0) proves the fixed quotient count.
quotient=[(a,b,0) for a in field for b in field]
fixed=[x for x in quotient if tuple(map(frob,x))==x]
assert len(fixed)==9
result={
 "status":"PASS",
 "coefficient_domains":["Q[t]/(t^2+3t+3), exact Fractions", "F3", "F9=F3[i]/(i^2+1)"],
 "Pi_minus_Pi0_exact_chain_grade":R_grade,
 "actual_matrix_pairings":matrices,
 "F3_triples":len(base), "F3_pairings_checked":len(base)**2,
 "F3_radical":base_rad, "F3_quotient_order":9,"F3_Heisenberg_degree":3,
 "F9_triples":len(triples),"F9_pairs_checked":pairchecks,
 "F9_radical":rad,"F9_quotient_order":81,"F9_Heisenberg_degree":9,
 "Frobenius_fixed_quotient_order":len(fixed),
 "embedded_pairing_multiplier":2,
 "non_claims":["No automorphic-induction occurrence theorem proved by computation",
               "No identification with original Paper XI packet or kappa",
               "Finite checks validate the displayed arithmetic reduction, not arbitrary strata"]
}
out=Path("evidence/lattice/run113/result.json")
out.write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps({k:result[k] for k in ["status","F9_pairs_checked","F3_quotient_order","F9_quotient_order","embedded_pairing_multiplier"]}))
