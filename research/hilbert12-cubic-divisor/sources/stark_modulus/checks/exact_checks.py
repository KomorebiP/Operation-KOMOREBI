#!/usr/bin/env python3
"""Exact certificates for the beta^3=7 Stark/modulus comparison.

Two implementations check the six new norm identities:
  * a standalone 18-dimensional rational quotient algebra;
  * SymPy Groebner reduction over QQ (not floating arithmetic).
This script does not by itself prove the analytic theorems in PROOF.md.
"""
from __future__ import annotations
from fractions import Fraction as Q
from itertools import product, permutations
from collections import Counter
from pathlib import Path
import json, platform, time
import sympy as sp

MONS = tuple(product(range(3), range(3), range(2)))
INDEX = {m:i for i,m in enumerate(MONS)}

class E:
    """Q[b,x,w]/(b^3-7,x^3-2-3w,w^2+w+1)."""
    def __init__(self, value=0):
        if isinstance(value, E): self.c = value.c
        elif isinstance(value, tuple):
            if len(value) != 18: raise ValueError('Expected 18 coefficients')
            self.c = tuple(Q(z) for z in value)
        else:
            c = [Q(0)]*18; c[0] = Q(value); self.c = tuple(c)
    @classmethod
    def mon(cls, i, j, k):
        c=[Q(0)]*18; c[INDEX[(i,j,k)]]=Q(1); return cls(tuple(c))
    def __add__(self, other):
        o=E(other); return E(tuple(a+b for a,b in zip(self.c,o.c)))
    __radd__=__add__
    def __neg__(self): return E(tuple(-a for a in self.c))
    def __sub__(self, other): return self+-E(other)
    def __rsub__(self, other): return E(other)+-self
    def __truediv__(self, other):
        if isinstance(other,E): raise TypeError('Only rational division implemented')
        return E(tuple(a/Q(other) for a in self.c))
    def __mul__(self, other):
        o=E(other); out=[Q(0)]*18
        wred=((1,0),(0,1),(-1,-1))
        for ia,ca in enumerate(self.c):
            if not ca: continue
            i,j,k=MONS[ia]
            for ib,cb in enumerate(o.c):
                if not cb: continue
                ii,jj,kk=MONS[ib]
                bb,xx,ww=i+ii,j+jj,k+kk
                coeff=ca*cb*(7 if bb>=3 else 1)
                # x^3 = 2+3w. Every product has x exponent at most four.
                terms=((ww,1),) if xx<3 else ((ww,2),(ww+1,3))
                for we,mult in terms:
                    wr=wred[we%3]
                    for wk,fc in enumerate(wr):
                        if fc: out[INDEX[(bb%3,xx%3,wk)]]+=coeff*mult*fc
        return E(tuple(out))
    __rmul__=__mul__
    def __pow__(self, n):
        if not isinstance(n,int) or n<0: raise ValueError('Nonnegative integer power required')
        out=E(1); p=self
        while n:
            if n&1: out=out*p
            n//=2
            if n: p=p*p
        return out
    def __eq__(self, other): return self.c==E(other).c
    def image(self, images):
        powers=[[E(1),z,z*z] for z in images]
        out=E(0)
        for coeff,(i,j,k) in zip(self.c,MONS):
            if coeff: out+=coeff*powers[0][i]*powers[1][j]*powers[2][k]
        return out
    def sympy(self, bs, xs, ws):
        return sp.expand(sum(sp.Rational(c.numerator,c.denominator)*bs**i*xs**j*ws**k
                             for c,(i,j,k) in zip(self.c,MONS) if c))
    def record(self):
        return [{'monomial':list(m),'coefficient':str(c)} for c,m in zip(self.c,MONS) if c]

checks=[]
def check(name, condition):
    if not condition: raise AssertionError(name)
    checks.append(name)

def build(b,x,w):
    xi=x*x*(-1-3*w)/7
    nu=(x+b*xi-b*b)/3;v=-b*b*nu-2*nu*nu
    Y=(4*b*b+b-14)*v*v+(11*b-23)*v-b*b+3*b-3
    Z=((-2*b*b+7*b-8)*v*v+(-10*b*b+11*b+17)*v)/3+7-b-b*b
    U=(Y-(1+2*w)*Z)/2; Ui=(Y+(1+2*w)*Z)/2
    AW=(21*b-42)*v*v+(-15*b*b+30*b)*v-b*b-4*b+11
    BW=3*b*b*v*v+(18*b-42)*v-11*b*b+13*b+7
    W=(AW+w*BW)/3
    aa=[(1+w)*x*x-x+1,-x*x+(1+w)*x+1,-w*x*x-w*x+1]
    return xi,nu,v,Y,Z,U,Ui,W,aa

start=time.perf_counter()
b,x,w=E.mon(1,0,0),E.mon(0,1,0),E.mon(0,0,1)
xi,nu,v,Y,Z,U,Ui,W,aa=build(b,x,w)
eps=2-b
sig=lambda p:p.image((b,w*b*xi,w*w))
kappa=lambda p:p.image((w*w*b,w*b*xi,w*w))
def iterate(fn,p,n):
    for _ in range(n):p=fn(p)
    return p
N=lambda p:p*kappa(p)
for name,diff in [('b cubed',b**3-7),('X cubed',x**3-2-3*w),('omega',w*w+w+1),
                  ('X inverse',x*xi-1),('epsilon inverse',eps*(b*b+2*b+4)-1),
                  ('v polynomial',v**3-b*v*v+1),('Y Z lift',Y*Y+3*Z*Z-4),
                  ('U inverse',U*Ui-1),('W inversion',W*iterate(sig,W,3)-1),
                  ('norm-five smoothing',W**5-sig(W)*U**6),
                  ('radical lift relation',W**21-(-w*w)*U**25*sig(U)**5*iterate(sig,U,2))]:
    check(name,diff==0)
for gname,g in [('b',b),('x',x),('w',w)]:
    check('sigma order6 '+gname,iterate(sig,g,6)==g)
    check('conjugation involution '+gname,kappa(kappa(g))==g)
check('sigma cubed fixes v',iterate(sig,v,3)==v)
check('sigma nontrivial cubic',iterate(sig,v,2)!=v)
check('sigma omega conjugation',sig(w)==w*w)
check('A trace',sum(aa)==3)
check('A second elementary coefficient',aa[0]*aa[1]+aa[0]*aa[2]+aa[1]*aa[2]==6*w)
check('A norm',aa[0]*aa[1]*aa[2]==1)
for k,a in enumerate(aa):check(f'A{k} monic unit equation',a**3-3*a*a+6*w*a-1==0)
for k,num in enumerate((w*w+w*x,1+w*x,w+w*x)):
    check(f'A{k} CM rational expression',num**3-(3+3*w)*aa[k]==0)
Wh=W
for h in range(6):
    Nh=N(eps*aa[(h+1)%3]**2)
    check(f'new Stark norm identity h={h}',N(Wh)==Nh if h%2==0 else N(Wh)*Nh==1)
    Wh=sig(Wh)
check('modulus cubed certificate',N(eps**3*aa[2]*aa[1]**5)*N(Ui)**3==1)
# Monic reciprocal polynomial establishes W and W^{-1} integral over O_K.
pco=[E(1),5*b*b+14*b-43,-b*b-133*b+260,-894*b*b+1470*b+461,
     -b*b-133*b+260,5*b*b+14*b-43,E(1)]
r0=E(0)
for c in pco:r0=r0*W+c
check('W monic reciprocal polynomial',r0==0)
# Exact finite residue data supporting the inherited radical degree claim.
check('181 base residue',pow(32,3,181)==7)
check('181 v residue',(99**3-32*99**2+1)%181==0)
check('181 omega residue',(48**2+48+1)%181==0)
Aval=(21*32-42)*99**2+(-15*32**2+30*32)*99-32**2-4*32+11
Bval=3*32**2*99**2+(18*32-42)*99-11*32**2+13*32+7
check('181 W residue',(Aval+48*Bval)*pow(3,-1,181)%181==23)
check('181 nonsquare',pow(23,90,181)==180)
check('181 noncube',pow(23,60,181)==132)
z=sp.symbols('z')
check('181 binomial irreducible',sp.Poly(z**6-23,z,modulus=181).is_irreducible)
# Dirichlet L(0) character sums over exact rationals and Q(omega).
chi7=[0,0,1,2,2,1,0]  # exponent table for nonzero residues, index 1..6
for j in (0,1,2):
    f=3 if j==0 else 21;val=E(0)
    for a in range(1,f+1):
        if a%3==0 or (j and a%7==0):continue
        sign=1 if a%3==1 else -1
        ev=E(1) if j==0 else w**((chi7[a%7]*j)%3)
        val+=Q(-a,f)*sign*ev
    check('Dirichlet L0 j='+str(j),val==([E(Q(1,3)),-2*w,-2*w*w][j]))
# All odd induced-character decompositions, on all 18 group elements.
# S3 represented by permutations; its standard character is fixed_points-1.
for perm in permutations(range(3)):
    inv=sum(perm[i]>perm[j] for i in range(3) for j in range(i+1,3))
    sign=(-1)**inv;fix=sum(perm[i]==i for i in range(3));std=fix-1
    # Ind_{C2}^{S3}(sgn) has values 3 at identity, -1 at a transposition, 0 at 3-cycles.
    ind=3 if fix==3 else (-1 if sign==-1 else 0)
    for k in range(3):
        for j in range(3):
            ch=w**((j*k)%3)
            check(f'Artin character {perm},{k},{j}',ind*ch==(sign+std)*ch)
# Ray representatives and exact cubic residue labels.
reps=[1,4,10,13,16,19];exp4={1:0,4:1,2:2};pairgroups=[[],[],[]]
for a in reps:
    check(f'primary ray representative {a}',a%3==1 and a%7!=0)
    k=2*exp4[a*a%7]%3;pairgroups[k].append(a)
check('cubic ray classes',pairgroups==[[1,13],[4,10],[16,19]])
# Rational differences are in 3J O iff they are divisible by21.
check('six different ray classes',len({a%21 for a in reps})==6)
check('ray class number 3J',(63*(1-Q(1,3))*(1-Q(1,7)))/6==6)
check('ray class number lambdaJ',(21*(1-Q(1,3))*(1-Q(1,7)))/6==2)
check('ray class number 3',(9*(1-Q(1,3)))/6==1)
for m,k in enumerate([2,1,3]):
    exactpair={(7-3*k)%21,(7+3*k)%21}
    check(f'torsion pair m={m}',exactpair==set(pairgroups[m]))
# Unit grid calculations are correct, but their products are not fixed by ratios.
M=sp.Matrix([[0,1,0],[-4,2,15],[-1,0,4]])
grid_orbits={}
for n,a,d in [(10,1,3),(23,5,-2)]:
    A=sp.Matrix([[1,0,0],[0,1,0],[a,d,n]])
    M1=A.inv()*M*A
    check(f'unit conjugation integral {n}',all(t.q==1 for t in M1))
    check(f'unit determinant {n}',M1.det()==1)
    T=((0,-1),(4-15*a,2+15*d))
    def move(pt):return ((T[0][0]*pt[0]+T[0][1]*pt[1])%n,
                         (T[1][0]*pt[0]+T[1][1]*pt[1])%n)
    left=set(product(range(n),repeat=2));sizes=[]
    while left:
        first=min(left);cur=first;seq=[]
        while cur not in seq:
            seq.append(cur);left.remove(cur);cur=move(cur)
        check(f'closed grid orbit {n}:{len(sizes)}',cur==first)
        sizes.append(len(seq))
    grid_orbits[str(n)]=dict(sorted(Counter(sizes).items()))
check('23 orbit decomposition',grid_orbits['23']=={1:1,528:1})
check('10 orbit decomposition',grid_orbits['10']=={1:1,3:1,12:8})
# Independent SymPy polynomial reduction: rebuilt from original coordinate formulas.
bb,xx,ww=sp.symbols('b x w')
GB=sp.groebner([bb**3-7,xx**3-2-3*ww,ww**2+ww+1],bb,xx,ww,domain=sp.QQ)
def red(p):return sp.expand(GB.reduce(sp.expand(p))[1])
xii=red(xx*xx*(-1-3*ww)/7)
nuu=red((xx+bb*xii-bb*bb)/3);vv=red(-bb*bb*nuu-2*nuu*nuu)
aw=red((21*bb-42)*vv*vv+(-15*bb*bb+30*bb)*vv-bb*bb-4*bb+11)
bw=red(3*bb*bb*vv*vv+(18*bb-42)*vv-11*bb*bb+13*bb+7)
WW=red((aw+ww*bw)/3)
AS=[(1+ww)*xx**2-xx+1,-xx**2+(1+ww)*xx+1,-ww*xx**2-ww*xx+1]
sg=lambda p:red(p.subs({xx:ww*bb*xii,ww:ww*ww},simultaneous=True))
cc=lambda p:red(p.subs({bb:ww*ww*bb,xx:ww*bb*xii,ww:ww*ww},simultaneous=True))
check('independent W formula',red(WW-W.sympy(bb,xx,ww))==0)
WW0=WW
for h in range(6):
    BB=red((2-bb)*AS[(h+1)%3]**2)
    nw=red(WW*cc(WW));nb=red(BB*cc(BB))
    residue=red(nw-nb) if h%2==0 else red(nw*nb-1)
    check(f'independent Stark norm identity h={h}',residue==0)
    WW=sg(WW)

out={'status':'PASS','checks':len(checks),'names':checks,
     'domain':'exact rational quotient of dimension 18; independent SymPy QQ Groebner reduction',
     'finite_grid_orbits':grid_orbits,'new_norm_identities_reproduced_independently':6,
     'a_units':[a.record() for a in aa], 'W_normal_form':W.record(),
     'python':platform.python_version(),'sympy':sp.__version__,
     'runtime_seconds':time.perf_counter()-start,
     'non_claims':['No numerical recognition','No Lean verification','The script does not prove the complex gamma phase equality']}
path=Path(__file__).resolve().parent.parent/'evidence'/'exact_results.json'
path.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ('names','a_units','W_normal_form')},indent=2))
