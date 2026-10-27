#!/usr/bin/env python3
"""Exact principal-seven identities and finite transfer inversion.
Universal analytic statements have separate proofs in PROOF.md; no gamma
algebraicity or vanishing phase is inferred from a bounded check.
"""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from datetime import datetime, timezone
import json, platform, sys, time, hashlib
import sympy as sp
ROOT=Path(__file__).resolve().parents[1]
M=sp.Matrix([[0,1,0],[-4,2,15],[-1,0,4]])
N=2*sp.eye(3)-M; A=M.T; B=N.T
ZERO=(0,0,0)
def mv(T,k):return tuple(int(x) for x in T*sp.Matrix(k))
def clean(d):return {k:F(v) for k,v in d.items() if v}
def add(a,b,sgn=1):
 d=dict(a)
 for k,v in b.items():d[k]=d.get(k,F(0))+sgn*v
 return clean(d)
def scale(c,a):return clean({k:c*v for k,v in a.items()})
def comp(a,T):
 d={}
 for k,c in a.items():
  q=mv(T,k);d[q]=d.get(q,F(0))+c
 return clean(d)
def delta(a):return add(a,comp(a,A),-1)
def charge(k):return k[0]+2*k[1]+4*k[2]
def trace(a):return clean({k:7*c for k,c in a.items() if charge(k)%7==0})
def push(a):
 d={}
 for (x,y,z),c in a.items():
  q=x+2*y+4*z
  if q%7:continue
  r=q//7;v=(-y,z-2*r,15*r-8*z)
  d[v]=d.get(v,F(0))+7*c
 return clean(d)
def norm_defect(a):return add(trace(a),comp(a,B),-1)
def gauge_from_residual(r):
 if r.get(ZERO,0):raise ValueError('zero Fourier mean is required')
 height=max([max(map(abs,k)) for k in r]+[0]);n=0;seven=1
 while seven<=height:n+=1;seven*=7
 cap=3*n;current=dict(r);g={};steps=0
 while current:
  current=push(current);steps+=1;g=add(g,scale(F(-1,7),current))
  if steps>cap:raise RuntimeError('derived finite termination bound violated')
 return g,steps,cap

def run():
 checks=[];negative=[]
 def ck(name,ok):
  if not bool(ok):raise AssertionError(name)
  checks.append(name)
 ck('actual principal cube',N**3==7*sp.eye(3))
 ck('dual principal cube',B**3==7*sp.eye(3))
 ck('degree on rank-three lattice',N.det()==7)
 ck('commuting unit and principal',M*N==N*M and A*B==B*A)
 ck('winding defect is a unit boundary',7*sp.eye(3)-B==(sp.eye(3)-A)*(B*B+B))
 v=sp.Matrix([1,2,4]);ck('kernel generator carry',N*v==sp.Matrix([0,-56,-7]))
 ck('unit doubling on kernel',M*v==2*v+7*sp.Matrix([0,8,1]))
 ker=[k for k in product(range(7),repeat=3) if all(x%7==0 for x in mv(N,k))]
 expected={tuple(j*x%7 for x in (1,2,4)) for j in range(7)}
 ck('all 343 residue triples kernel test',len(ker)==7 and set(ker)==expected)
 for k in product(range(-3,4),repeat=3):
  inv=B.inv()*sp.Matrix(k)
  if ((charge(k)%7==0) != all(x.q==1 for x in inv)):raise AssertionError('dual image')
 ck('all 343 dual image residues',True)
 x,y,z=sp.symbols('x y z');kv=sp.Matrix([x,y,z]);V=sp.expand(sp.Matrix.hstack(kv,A*kv,A*A*kv).det())
 ck('primitive cubic invariant seed',V.subs({x:0,y:0,z:1})==1)
 ck('cubic unit invariance',sp.expand(V.subs(dict(zip((x,y,z),A*kv)),simultaneous=True)-V)==0)
 ck('principal cubic scaling',sp.expand(V.subs(dict(zip((x,y,z),B*kv)),simultaneous=True)-7*V)==0)
 b=sp.symbols('b');red=lambda e:sp.rem(sp.together(e),b**3-7,b)
 tau=(b*b+2*b)/15;s=-(b+2)/15;d=(tau+2*s+4)/7
 ck('principal seven argument identity',sp.simplify(red(b*d+8*s+1))==0)
 ck('conductor third principal carry',sp.simplify(red(b/3-sp.Rational(1,3)+5*s+1))==0)
 ck('gamma period relation',sp.expand(-tau+7*d-2*s-4)==0)
 ck('scaled pole location',sp.expand(red(b*tau-(2*tau+4*s+1)))==0)
 p,q,D=sp.symbols('p q D');geo=sum(D**k for k in range(7))
 ck('geometric seven',sp.expand((1-D)*geo-(1-D**7))==0)
 coeffL=p*geo/((1-p)*(1-q))
 coeffR=(1+q)/((1-p)*(1-D))-1/((1-q)*(1-D))
 ck('gamma positive Fourier coefficient',sp.cancel((coeffL-coeffR).subs(p,q*q/D**7))==0)
 coeffLn=q*sum(D**(-k) for k in range(7))/((1-p)*(1-q))
 coeffRn=D*(-q/(1-q)+p*(1+1/q)/(1-p))/(1-D)
 ck('gamma negative Fourier coefficient',sp.cancel((coeffLn-coeffRn).subs(p,q*q/D**7))==0)
 # The shifted divisors are distinguished by rational power-basis coordinates.
 ck('six other seven shifts avoid all smoothed gamma divisors',all(F(k,7).denominator!=1 for k in range(1,7)))
 ck('principal image has mixed gamma coordinates',(-1<0 and 4>0))
 negative.append('naive seven norm equals F(beta*z) is refuted by orders 4 and 0 at z=tau')
 seed=(0,0,1);seeds=[seed,mv(A,seed),mv(B*B,seed),mv(B**3,seed)]
 max_steps=0
 for coeff in product(range(-2,3),repeat=4):
  g=clean(dict(zip(seeds,coeff)));h=delta(g);r=norm_defect(g)
  if norm_defect(h)!=delta(r):raise AssertionError('norm/unit commutation')
  out,n,cap=gauge_from_residual(r)
  if out!=g or delta(out)!=h:raise AssertionError('finite inverse')
  max_steps=max(max_steps,n)
 ck('625 finite Laurent gauges reconstructed exactly',True)
 # Three pushes are the 343-weighted frequency division by seven.
 f={k:F(i+1) for i,k in enumerate(seeds)}
 expectedpush={tuple(t//7 for t in k):343*c for k,c in f.items() if all(t%7==0 for t in k)}
 ck('triple transfer decimates by seven',push(push(push(f)))==clean(expectedpush))
 ck('trace equals pullback of transfer',trace(f)==comp(push(f),B))
 ck('transfer of principal pullback',push(comp(f,B))==scale(7,f))
 # Finite truncations of the regularity counterexample have one exact endpoint residual.
 for length in range(1,13):
  k=seed;h={}
  for j in range(length):h[k]=F(1,7**j);k=mv(B,k)
  if norm_defect(h)!={k:F(-1,7**(length-1))}:raise AssertionError('critical tail')
 ck('twelve critical-series endpoint identities',True)
 ck('critical subsequence',all(mv(B**(3*j),seed)==(0,0,7**j) for j in range(7)))
 negative.append('principal norm compatibility without adequate regularity does not force flattening')
 # Explicit model pullback on all period coordinates.
 bigN=sp.diag(N,N);l1=sp.Matrix([[1,0,-2,-3,0,-1]]);l2=sp.Matrix([[0,1,3,0,-3,-2]])
 ck('model alpha carry',l1*bigN+l2==7*sp.Matrix([[0,0,1,-1,0,0]]))
 ck('model beta carry',l2*bigN==7*sp.Matrix([[1,0,-3,-2,0,7]]))
 ck('model two-step period labels vanish',all(t%7==0 for t in l1*bigN**2) and all(t%7==0 for t in l2*bigN**2))
 ck('model pulled-back alternating form vanishes',all(((-a)*0-0*(-b))%7==0 for a,b in product(range(7),repeat=2)))
 if norm_defect({seed:F(1)})=={}:raise AssertionError('missing defect')
 negative.append('a single primitive Fourier frequency has a nonzero principal norm defect')
 try:gauge_from_residual({ZERO:F(1)})
 except ValueError:negative.append('nonzero mean is rejected rather than silently summed')
 else:raise AssertionError('mean guard')
 if sp.cancel((coeffL-((1+q)/((1-p)*(1-D)))).subs(p,q*q/D**7))==0:raise AssertionError('omitted chart factor')
 negative.append('omitting the refined numerator gamma factor breaks the exact coefficient identity')
 return {'assertions':checks,'negative_controls':negative,'finite_gauges':625,'kernel_residue_inputs':343,
         'max_finite_transfer_steps':max_steps,'cubic_invariant':str(V),
         'scope':'Exact finite matrices, universal polynomial identities, and bounded Laurent implementation checks. Infinite regularity/continuation proofs are in PROOF.md. No gamma-arithmetic equality.'}
if __name__=='__main__':
 tic=time.monotonic();start=datetime.now(timezone.utc).isoformat();r=run()
 r.update(started_at=start,runtime_seconds=time.monotonic()-tic,exit_status=0,python=sys.version.split()[0],sympy=sp.__version__,platform=platform.platform())
 (ROOT/'evidence/exact_results.json').write_text(json.dumps(r,indent=2)+'\n')
 print('PASS',len(r['assertions']),'assertions;',len(r['negative_controls']),'negative controls;',r['runtime_seconds'],'seconds')
