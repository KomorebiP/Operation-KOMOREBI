import sys,json,time,math
from pathlib import Path
from fractions import Fraction
import sympy as s
import numpy as np
from scipy.optimize import linprog
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE.parent/'continuation_5core'))
from explore_shell import shell,weight
from explore import sigma_primes
p2,p3,p4,p5=s.symbols('p2 p3 p4 p5');vs=(p2,p3,p4,p5)
ps={0:s.Integer(5),1:s.Integer(0),2:p2,3:p3,4:p4,5:p5};ee={1:0,2:-p2/2,3:p3/3,4:p2**2/8-p4/4,5:p5/5-p2*p3/6}
for k in range(6,9):ps[k]=s.expand(sum((-1)**(j-1)*ee[j]*ps[k-j] for j in range(1,6)))
def L(f):
 z=0
 for m,P in enumerate(vs,2):
  a=m*sum(ps[i]*ps[m-2-i] for i in range(m-1))-s.Rational(m*(m-1),5)*ps[m-2]
  z+=s.diff(f,P)*a
  for n,Q in enumerate(vs,2):z+=s.diff(f,P,Q)*m*n*(ps[m+n-2]-ps[m-1]*ps[n-1]/5)
 return s.Poly(s.expand(z),*vs)
def exponents(d):
 for a in range(d//2+1):
  for b in range(d//3+1):
   for c in range(d//4+1):
    for e in range(d//5+1):
     if 2*a+3*b+4*c+5*e==d:yield (a,b,c,e)
def vals(v):return tuple(sum(x**k for x in v) for k in range(2,6))
def ev(poly,v):
 z=vals(v)
 return sum(c*math.prod(x**e for x,e in zip(z,es)) for es,c in poly)
def canonical(expr):
 po=s.Poly(expr,*vs);den=s.ilcm(*[c.q for c in po.coeffs()]);cs=[int(c*den) for c in po.coeffs()];g=math.gcd(*cs)
 if cs[0]<0:g=-g
 return [(tuple(es),int(c*den)//g) for es,c in po.terms()]

def build(d):
 es=list(exponents(d));basis=[math.prod(x**k for x,k in zip(vs,a)) for a in es];LP=[L(b) for b in basis]
 mon=sorted(set(e for p in LP for e in p.monoms()))
 mat=[[p.coeff_monomial(m) for p in LP] for m in mon]
 # Harmonic alternating theta has weight 12+d, level one. Kill its Sturm coefficients.
 for n in range(1,(12+d)//12+1):
  pts=list(shell(n));mat.append([sum(weight(v)*b.subs(dict(zip(vs,vals(v)))) for v in pts) for b in basis])
 ns=s.Matrix(mat).nullspace();out=[]
 for vec in ns:
  f=s.expand(sum(b*c for b,c in zip(basis,vec)));assert L(f).is_zero
  out.append({'degree':d,'terms':canonical(f)})
 return out

def try_sign(vectors,K,sign):
 ww=[weight(v) for v in vectors];QQ=[[ev(k['terms'],v) for k in K] for v in vectors];sc=[max(1,max(abs(q[j]) for q in QQ)) for j in range(len(K))]
 sg=[sign*(1 if w>0 else -1) for w in ww]
 A=[[-sg[i]*float(Fraction(q[j],sc[j])) for j in range(len(K))]+[1] for i,q in enumerate(QQ)]
 c=[0]*len(K)+[-1];res=linprog(c,A_ub=A,b_ub=sg,bounds=[(None,None)]*len(K)+[(0,1)],method='highs')
 if not res.success or res.x[-1]<1e-8:return {'certified':False,'proposal_status':res.message,'proposal_margin':float(res.x[-1]) if res.success else None}
 coeff=[Fraction(float(a)).limit_denominator(10**8)/sc[j] for j,a in enumerate(res.x[:-1])]
 margins=[sg[i]*(1+sum(c*qj for c,qj in zip(coeff,q))) for i,q in enumerate(QQ)]
 if min(margins)<=0:return {'certified':False,'proposal_status':'rationalized proposal failed exact margin'}
 assert all(sum(w*q[j] for w,q in zip(ww,QQ))==0 for j in range(len(K)))
 return {'certified':True,'sign':sign,'coefficients':[[c.numerator,c.denominator] for c in coeff], 'margin':[min(margins).numerator,min(margins).denominator], 'tau_check':sum(ww)}

if __name__=='__main__':
    t=time.perf_counter();K=[]
    for d in range(8,17,2):
     x=build(d);K.extend(x);print('degree',d,'kernels',len(x),flush=True)
    (HERE/'KERNELS.json').write_text(json.dumps(K,indent=2))
    rows=[]
    for p in sigma_primes(100)[1]:
     pts=list(shell(p));row={'p':p,'shell_count':len(pts),'attempts':[]}
     for degree in [8,10,12,14,16]:
      kk=[k for k in K if k['degree']<=degree]
      for sign in [1,-1]:
       r=try_sign(pts,kk,sign);row['attempts'].append({'max_degree':degree,'sign':sign,**r})
       if r['certified']:break
      if r['certified']:break
     print(p,'cert',r['certified'],'d',degree,flush=True);rows.append(row)
    (HERE/'POSITIVITY_RESULTS.json').write_text(json.dumps({'rows':rows,'runtime':time.perf_counter()-t},indent=2))
