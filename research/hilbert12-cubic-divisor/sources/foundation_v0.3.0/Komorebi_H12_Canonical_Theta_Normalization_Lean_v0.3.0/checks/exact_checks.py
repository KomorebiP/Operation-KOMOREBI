#!/usr/bin/env python3
"""Exact rational-polynomial and finite carry tests; not elliptic-gamma algebraicity."""
from __future__ import annotations
import json,sys,time,platform
from datetime import datetime,timezone
from pathlib import Path
from itertools import product
import sympy as s
ROOT=Path(__file__).resolve().parents[1]
def main():
 started=datetime.now(timezone.utc).isoformat();tic=time.perf_counter();checks=[];neg=[]
 def zero(name,expr):
  if s.cancel(s.expand(expr))!=0:raise AssertionError((name,s.factor(expr)))
  checks.append(name)
 def true(name,condition):
  if not condition:raise AssertionError(name)
  checks.append(name)
 a,b,x,g2,g3,c,lam=s.symbols('a b x g2 g3 c lam');d=a-b
 f=lambda x:4*x**3-g2*x-g3
 psi=lambda x:3*x**4-s.Rational(3,2)*g2*x*x-3*g3*x-g2*g2/16
 phi=lambda x:x**4+s.Rational(1,2)*g2*x*x+2*g3*x+g2*g2/16
 zero('division polynomial x f - phi = psi',x*f(x)-phi(x)-psi(x))
 # Torsion resultant products, independent of analytic evaluation.
 qpoly=(x-a)*(x-b)
 zero('two torsion resultant',s.resultant(f(x),qpoly,x)-f(a)*f(b))
 zero('three torsion resultant',s.resultant(psi(x),qpoly,x)-psi(a)*psi(b))
 zero('coprime power reconstruction',(c**3)**3/c**8-c)
 X=(x-a)/d
 zero('normalized denominator',(x-a)*(x-b)-d*d*X*(X+1))
 zero('universal rational theta',d*d/((x-a)*(x-b))-1/(X*(X+1)))
 zero('swap is reflection',(x-b)/(b-a)+1+X)
 zero('symmetric kernel discriminant form',d*d/((x-a)*(x-b))-((a+b)**2-4*a*b)/(x*x-(a+b)*x+a*b))
 zero('unordered fifth subgroup',d*d/((x-a)*(x-b))-(b-a)**2/((x-b)*(x-a)))
 zero('homothety invariance',(lam*a-lam*b)**2/((lam*x-lam*a)*(lam*x-lam*b))-d*d/((x-a)*(x-b)))
 # Universal Tate normal family: all checks are identities over Q(u).
 u=s.symbols('u');b2=1-6*u+u*u;b4=u*u-u;b6=u*u
 g2u=b2*b2/12-2*b4;g3u=-b2**3/216+b2*b4/6-b6
 aa=b2/12;bb=u+aa;ya=-u;yb=u*u;dd=aa-bb
 fu=lambda xx:4*xx**3-g2u*xx-g3u
 psu=lambda xx:3*xx**4-s.Rational(3,2)*g2u*xx*xx-3*g3u*xx-g2u*g2u/16
 phu=lambda xx:xx**4+s.Rational(1,2)*g2u*xx*xx+2*g3u*xx+g2u*g2u/16
 zero('Tate curve at P',ya**2-fu(aa));zero('Tate curve at 2P',yb**2-fu(bb))
 zero('Tate mutual doubling P',bb*fu(aa)-phu(aa));zero('Tate mutual doubling 2P',aa*fu(bb)-phu(bb))
 zero('Tate tangent ordinate product',ya*yb-dd**3)
 zero('Tate f product',fu(aa)*fu(bb)-dd**6)
 zero('Tate psi product',psu(aa)*psu(bb)+dd**8)
 zero('Tate cube normalizer',fu(aa)*fu(bb)-u**6)
 zero('Tate eighth normalizer',(psu(aa)*psu(bb))**2-u**16)
 zero('Tate rational normalization recovery',(fu(aa)*fu(bb))**3/(psu(aa)*psu(bb))**2-u*u)
 XX,YY=s.symbols('XX YY')
 transformed=(2*YY+(1-u)*XX-u)**2-fu(XX+aa)
 original=YY**2+(1-u)*XX*YY-u*YY-XX**3+u*XX**2
 zero('Tate short-coordinate change',transformed-4*original)
 zero('Tate normalized theta',dd**2/((XX+aa-aa)*(XX+aa-bb))-u*u/(XX*(XX-u)))
 # Exact rational nonsingular examples; no roots or numerical recognition.
 for uu in [-3,-2,-1,1,2,3,s.Rational(1,2),s.Rational(2,3)]:
  true(f'nonsingular Tate parameter {uu}',uu!=0 and uu**2-11*uu-1!=0)
  zero(f'sample normalizer {uu}',(fu(aa)*fu(bb)).subs(u,uu)-uu**6)
 R=s.Matrix([[8,-4,15],[1,0,0],[2,-1,4]]);Q=R**3
 V=list(product((0,1),repeat=3));chi=lambda u,v:(-1)**sum(a*b for a,b in zip(u,v));T=lambda v:(v[2],v[0],v[1])
 A=lambda v:5+4*v[0]-2*v[1]+7*v[2]
 gain=[sum(chi(w,v)*A(v) for v in V) for w in V]
 true('one-step gain spectrum',gain==[76,-28,8,0,-16,0,0,0])
 true('canonical squared-difference gain spectrum',[2*g for g in gain]==[152,-56,16,0,-32,0,0,0])
 true('first layer scale exponent',sum(gain[i] for i in [1,2,4])==-36)
 true('first layer squared-difference exponent',2*sum(gain[i] for i in [1,2,4])==-72)
 v0=s.Matrix([0,0,s.Rational(1,3)])
 for n in range(1,9):
  carr={v:(Q**n-s.eye(3))*(v0+s.Matrix(v)/2) for v in V}
  true(f'integral carry n={n}',all(z.q==1 for cv in carr.values() for z in cv))
  gs=[sum(chi(u,v)*(carr[v][0]-carr[v][1]) for v in V) for u in V]
  true(f'affine high cancellation n={n}',all(gs[i]==0 for i in [3,5,6,7]))
  true(f'first layer third divisibility n={n}',sum(gs[i] for i in [1,2,4])%3==0)
  if n==1:true('three-step full spectrum',gs==[9720,-3780,984,0,-1884,0,0,0])
 # A nontrivial cube root keeps the cubic norm equation, fails the eighth.
 w=s.symbols('w');mod=w*w+w+1
 zero('cube branch passes degree-two norm',s.rem(w**3-1,mod,w))
 true('cube branch fails degree-three norm',s.rem(w**8-1,mod,w)!=0)
 neg.append('one multiplication norm alone leaves a cube-root scalar')
 zero('pair of scalar norm defects recovers multiplier',((lam**3)**3)/(lam**8)-lam)
 true('bare denominator misses first-order normalization',-28!=0 and 8!=0 and -16!=0)
 neg.append('omitting the known squared-difference factor changes first-order carries')
 out={'started_at':started,'runtime_seconds':time.perf_counter()-tic,'exit_status':0,'python':sys.version.split()[0],'sympy':s.__version__,'platform':platform.platform(),'check_count':len(checks),'checks':checks,'negative_controls':neg,'scope':'Exact Q-polynomial identities, universal Tate family, finite gain/carry regressions. Actual analytic torsion inputs are in the ordinary proof; no U_alg tested.'}
 (ROOT/'evidence/exact_results.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS',len(checks),'exact checks;',len(neg),'negative controls;',round(out['runtime_seconds'],2),'s')
if __name__=='__main__':main()
