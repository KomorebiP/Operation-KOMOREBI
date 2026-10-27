#!/usr/bin/env python3
"""Exact Q18 arithmetic, independent SymPy reduction, and norm reconstruction.
No gamma values or decimal recognition are used. Coefficients are rational.
"""
from __future__ import annotations
from fractions import Fraction as Q
from pathlib import Path
from datetime import datetime,timezone
import sympy as sp
import json,time,sys,itertools
ROOT=Path(__file__).resolve().parents[1]
BASIS=list(itertools.product(range(3),range(3),range(2)))
INDEX={e:i for i,e in enumerate(BASIS)}
# Multiplication table independently reduces b^3=7, x^3=2+3w, w^2=-1-w.
def mono(i,j,k):
 scale=7**(i//3);i%=3
 terms={k:scale}
 for _ in range(j//3):
  nt={}
  for e,c in terms.items():nt[e]=nt.get(e,0)+2*c;nt[e+1]=nt.get(e+1,0)+3*c
  terms=nt
 j%=3;out={}
 for e,c in terms.items():
  # w^3=1 follows from w^2+w+1=0.
  e%=3
  for ee,cc in ([(0,c)] if e==0 else [(1,c)] if e==1 else [(0,-c),(1,-c)]):
   idx=INDEX[i,j,ee];out[idx]=out.get(idx,0)+cc
 return {i:c for i,c in out.items() if c}
TABLE={(i,j):mono(*(a+b for a,b in zip(e,f))) for i,e in enumerate(BASIS) for j,f in enumerate(BASIS)}
class Elt:
 def __init__(self,x=0):
  if isinstance(x,Elt):self.c=x.c
  elif isinstance(x,(list,tuple)):self.c=tuple(map(Q,x))
  else:self.c=(Q(x),)+(Q(0),)*17
 def __add__(self,y):y=Elt(y);return Elt([a+b for a,b in zip(self.c,y.c)])
 __radd__=__add__
 def __neg__(self):return Elt([-a for a in self.c])
 def __sub__(self,y):return self+-Elt(y)
 def __rsub__(self,y):return Elt(y)+-self
 def __mul__(self,y):
  y=Elt(y);out=[Q(0)]*18
  for i,a in enumerate(self.c):
   if not a:continue
   for j,b in enumerate(y.c):
    if not b:continue
    for k,c in TABLE[i,j].items():out[k]+=a*b*c
  return Elt(out)
 __rmul__=__mul__
 def __truediv__(self,y):
  if isinstance(y,Elt):raise TypeError('Use independently proved explicit inverse')
  return Elt([a/Q(y) for a in self.c])
 def __pow__(self,n):
  if n<0:raise ValueError('Positive powers only')
  a=self;out=Elt(1)
  while n:
   if n&1:out=out*a
   a=a*a;n//=2
  return out
 def __eq__(self,y):return self.c==Elt(y).c
 def poly(self):return sum(sp.Rational(a.numerator,a.denominator)*BB**i*XX**j*WW**k for a,(i,j,k) in zip(self.c,BASIS))
def gen(e):
 a=[0]*18;a[INDEX[e]]=1;return Elt(a)
b,x,w=gen((1,0,0)),gen((0,1,0)),gen((0,0,1))
def transform(z,bi,xi,wi):
 return sum((c*bi**i*xi**j*wi**k for c,(i,j,k) in zip(z.c,BASIS)),Elt(0))
def data(b,x,w):
 xi=x*x*(-1-3*w)/7
 nu=(x+b*xi-b*b)/3;v=-b*b*nu-2*nu*nu
 Y=(4*b*b+b-14)*v*v+(11*b-23)*v-b*b+3*b-3
 Z=((-2*b*b+7*b-8)*v*v+(-10*b*b+11*b+17)*v)/3+7-b-b*b
 U=(Y-(1+2*w)*Z)/2
 AW=(21*b-42)*v*v+(-15*b*b+30*b)*v-b*b-4*b+11
 BW=3*b*b*v*v+(18*b-42)*v-11*b*b+13*b+7
 W=(AW+w*BW)/3
 aa=[(1+w)*x*x-x+1,-x*x+(1+w)*x+1,-w*x*x-w*x+1]
 return xi,v,U,W,aa
BB,XX,WW=sp.symbols('b x w');gb=sp.groebner([BB**3-7,XX**3-2-3*WW,WW**2+WW+1],BB,XX,WW,domain=sp.QQ)
def red(f):return sp.expand(gb.reduce(sp.expand(f))[1])

def main():
 tic=time.perf_counter();started=datetime.now(timezone.utc).isoformat();checks=[];neg=[]
 def ck(name,cond):
  if not cond:raise AssertionError(name)
  checks.append(name)
 def nc(name,cond):
  if not cond:raise AssertionError('Negative control: '+name)
  neg.append(name)
 ck('base cubic',b**3==7);ck('Kummer cubic',x**3==2+3*w);ck('cyclotomic relation',w*w+w+1==0)
 xi,v,U,W,a=data(b,x,w)
 ck('explicit inverse of X',x*xi==1);ck('integral cubic coordinate',v**3-b*v*v+1==0)
 ck('CM unit product',a[0]*a[1]*a[2]==1)
 for j in range(3):ck(f'CM unit cubic {j}',a[j]**3-3*a[j]**2+6*w*a[j]-1==0)
 eps=[2-b,2-w*b,2-w*w*b];ck('three unit norm',eps[0]*eps[1]*eps[2]==1)
 iota=lambda z:transform(z,b,b*xi,w*w)
 kappa=lambda z:transform(z,w*w*b,w*b*xi,w*w)
 ck('ray involution norm U',U*iota(U)==1);ck('ray involution norm W',W*iota(W)==1)
 for j in range(3):ck(f'actual conjugation index {j}',kappa(a[j])==iota(a[(j+1)%3]))
 ck('actual conjugation epsilon',kappa(eps[0])==eps[2])
 A=a[0]*a[1]**3;invA=(a[1]*a[2])*(a[0]*a[2])**3
 B=a[0]**2*a[1]**4;invB=(a[1]*a[2])**2*(a[0]*a[2])**4
 ck('A inverse',A*invA==1);ck('B inverse',B*invB==1)
 def act(z,i,j):return transform(z,b*w**(i%3),x*w**(j%3),w)
 directions=[(1,0),(0,1),(1,1),(1,2)]
 normsU=[];normsW=[]
 for di,(i,j) in enumerate(directions):
  nu=U*act(U,i,j)*act(U,2*i,2*j);nw=W*act(W,i,j)*act(W,2*i,2*j)
  normsU.append(nu);normsW.append(nw)
  ck(f'U norm fixed on line {i,j}',act(nu,i,j)==nu)
  ck(f'W norm fixed on line {i,j}',act(nw,i,j)==nw)
 expectedU=[w*A,w*eps[0]*eps[2]**2,w*iota(invA),w]
 expectedW=[-B,-eps[0]*eps[2]**2,-iota(invB),Elt(-1)]
 for i in range(4):
  ck(f'U relative norm formula {i}',normsU[i]==expectedU[i]);ck(f'W relative norm formula {i}',normsW[i]==expectedW[i])
 totalU=Elt(1);totalW=Elt(1)
 for i in range(3):
  for j in range(3):totalU*=act(U,i,j);totalW*=act(W,i,j)
 ck('total norm U one',totalU==1);ck('total norm W minus one',totalW==-1)
 prodU=Elt(1);prodW=Elt(1)
 for n in normsU:prodU*=n
 for n in normsW:prodW*=n
 ck('line reconstruction U',prodU==U**3*totalU);ck('line reconstruction W',prodW==W**3*totalW)
 ck('relative-unit cube U',U**3*eps[1]*iota(A)==w*eps[2]*A)
 ck('relative-unit cube W',W**3*eps[1]*iota(B)==-eps[2]*B)
 rhs=(eps[0]*kappa(eps[0]))**2*(a[1]*kappa(a[1]))**3*(a[2]*kappa(a[2]))**2
 ck('polarized positive identity',U**3*eps[0]*a[1]*a[2]**3==w*rhs)
 # Independently construct the original arithmetic candidate over SymPy QQ.
 sx,sv,sU,sW,sa=data(BB,XX,WW)
 for name,z,p in [('X inverse',xi,sx),('v',v,sv),('U',U,sU),('W',W,sW)]+[(f'a{i}',a[i],sa[i]) for i in range(3)]:
  ck('independent Groebner '+name,red(p)==z.poly())
 cert=json.loads((ROOT/'checks/certificate_polynomials.json').read_text())
 ck('Lean U21 normalization',red(sp.sympify(cert['u21'],locals={'b':BB,'x':XX,'w':WW}))==21*U.poly())
 ck('Lean A normalization',red(sp.sympify(cert['A'],locals={'b':BB,'x':XX,'w':WW}))==A.poly())
 ck('Lean IA7 normalization',red(sp.sympify(cert['AI7'],locals={'b':BB,'x':XX,'w':WW}))==7*iota(A).poly())
 ck('A smaller presentation',A==4*(1+w)*x*x-(6*w+4)*x+1)
 # Correction to the tempting, but false, holomorphic lift of the modulus.
 invE=eps[1]*eps[2];inva1=a[0]*a[2];inva2=a[0]*a[1]
 delta=U**3*invE**3*inva2*inva1**5
 explicit=w*(kappa(eps[0])*invE)**2*(kappa(a[1])*inva1)**3*(kappa(a[2])*inva2)**2
 ck('exact phase correction',delta==explicit);ck('phase correction norm one',delta*kappa(delta)==1)
 nc('naive holomorphic CM lift is false',delta!=1)
 nc('phase correction is not in mu6',delta**6!=1)
 nc('omitting omega in target is false',U**3*eps[1]*iota(A)!=eps[2]*A)
 nc('replacing ray involution by complex conjugation is false',U**3*eps[1]*kappa(A)!=w*eps[2]*A)
 nc('reversing unit ratio is false',U**3*eps[2]*iota(A)!=w*eps[1]*A)
 result={'started_at':started,'runtime_seconds':time.perf_counter()-tic,'exit_status':0,'checks':checks,'check_count':len(checks),'negative_controls':neg,'negative_count':len(neg),'domain':'QQ[b,x,w]/(b^3-7,x^3-2-3w,w^2+w+1)','implementations':['18-dimensional fractions.Fraction multiplication table','SymPy Groebner over QQ'],'python':sys.version.split()[0],'sympy':sp.__version__,'relative_norms_U':[str(t.poly()) for t in normsU],'relative_norms_W':[str(t.poly()) for t in normsW],'scope':'Exact arithmetic factorization and phase correction. No gamma equality or phase reality for the analytic value is proved.'}
 (ROOT/'evidence/exact_results.json').write_text(json.dumps(result,indent=2)+'\n')
 print('PASS',len(checks),'exact assertions,',len(neg),'negative controls;',round(result['runtime_seconds'],3),'seconds')
if __name__=='__main__':main()
