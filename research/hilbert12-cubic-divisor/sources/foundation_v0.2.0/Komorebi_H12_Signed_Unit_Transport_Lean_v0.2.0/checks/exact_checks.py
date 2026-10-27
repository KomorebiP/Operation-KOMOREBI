#!/usr/bin/env python3
"""Exact finite/symbolic regression for signed unit transport; not an analytic proof."""
from pathlib import Path
from itertools import product
from datetime import datetime,timezone
import json,time,sys,platform,hashlib
import sympy as sp
from sympy.matrices.normalforms import smith_normal_form
ROOT=Path(__file__).resolve().parents[1]
def main():
 tic=time.perf_counter();start=datetime.now(timezone.utc).isoformat();checks=[]
 def check(name,claim):
  if not claim:raise AssertionError(name)
  checks.append(name)
 V=list(product((0,1),repeat=3));T=lambda v:(v[2],v[0],v[1]);I={v:i for i,v in enumerate(V)}
 chi=lambda u,v:(-1)**sum(a*b for a,b in zip(u,v))
 W=sp.Matrix([[chi(u,v) for v in V] for u in V])
 check('Walsh orthogonality W squared equals 8I',W*W==8*sp.eye(8))
 check('Walsh Smith factors',list(smith_normal_form(W,domain=sp.ZZ).diagonal())==[1,-2,-2,2,-4,4,4,-8] or sorted(abs(x) for x in smith_normal_form(W,domain=sp.ZZ).diagonal())==[1,2,2,2,4,4,4,8])
 for u in V:
  check(f'character order three {u}',T(T(T(u)))==u)
  for v in V:check(f'contragredient character pairing {u} {v}',chi(T(u),T(v))==chi(u,v))
 A=sp.Matrix([5+4*b-2*c+7*a for b,c,a in V]);gain=W*A
 check('all one-step eta gains',gain==sp.Matrix([76,-28,8,0,-16,0,0,0]))
 u0,db,dc,da=sp.symbols('u0 db dc da');av=[u0+b*db+c*dc+a*da for b,c,a in V]
 for u in V:
  d=sum(u)
  for k in range(d):check(f'Walsh jet vanishing {u} degree {k}',sp.expand(sum(chi(u,v)*x**k for v,x in zip(V,av)))==0)
  if d:
   val=(-1)**d*sp.factorial(d)*2**(3-d)*sp.prod(step for bit,step in zip(u,[db,dc,da]) if bit)
   check(f'leading Walsh moment {u}',sp.expand(sum(chi(u,v)*x**d for v,x in zip(V,av))-val)==0)
 R=sp.Matrix([[8,-4,15],[1,0,0],[2,-1,4]])
 Q=sp.Matrix([[1033,-540,2070],[90,-47,180],[264,-138,529]])
 check('third power unit matrix',R**3==Q)
 b,c,a=sp.symbols('b c a');p=sp.Matrix([b/2,c/2,sp.Rational(1,3)+a/2])
 carry=sp.Matrix([690+516*b-270*c+1035*a,60+45*b-24*c+90*a,176+132*b-69*c+264*a])
 check('uniform three-step carries',sp.simplify(Q*p-p-carry)==sp.zeros(3,1))
 check('third power fixes mod two',all(int(x)%2==0 for x in Q-sp.eye(3)))
 check('all first-step lengths positive',min(A)==3 and max(A)==16)
 for n in range(1,7):
  carr=[Q**n*sp.Matrix([sp.Rational(v[0],2),sp.Rational(v[1],2),sp.Rational(1,3)+sp.Rational(v[2],2)])-sp.Matrix([sp.Rational(v[0],2),sp.Rational(v[1],2),sp.Rational(1,3)+sp.Rational(v[2],2)]) for v in V]
  check(f'carry integrality n={n}',all(x.q==1 for row in carr for x in row))
  lengths=sp.Matrix([row[0]-row[1] for row in carr]);g=W*lengths
  check(f'high-channel constant cancellation n={n}',all(g[I[u]]==0 for u in V if sum(u)>=2))
 # These exponent identities prove multiplicative formulas for arbitrary nonzero packets.
 agg=[sp.Matrix([sum(chi(u,v) for u in V if sum(u)==k) for v in V]) for k in [1,2,3]]
 e0=sp.Matrix([1,0,0,0,0,0,0,0]);ones=sp.ones(8,1)
 check('aggregate reconstruction exponent identity',sum(agg,sp.zeros(8,1))+ones==8*e0)
 h=sp.Matrix([3*sum(v)-4 for v in V]);hg=W*h
 check('undetected affine gauge',hg==sp.Matrix([4,-12,-12,0,-12,0,0,0]))
 check('gauge preserves conductor norm equation',sum(h)+h[0]==0)
 check('gauge is unit permutation invariant',all(h[I[T(v)]]==h[I[v]] for v in V))
 check('first-weight aggregate detects gauge',sum(hg[I[u]] for u in V if sum(u)==1)==-36)
 # Lower-dimensional half-period plane c=0 is not invariant under T.
 check('negative: elliptic half-period plane not unit stable',T((1,0,0))[1]==1)
 # Explicit finite theta carries: membership and eta-exponent counts.
 signed_support={}
 for u in V:
  stencil={}
  for v,n in zip(V,A):
   for j in range(int(n)):
    key=(T(T(v)),j);stencil[key]=stencil.get(key,0)+chi(u,v)
  check(f'signed carry exponent sum {u}',sum(stencil.values())==gain[I[u]])
  signed_support[''.join(map(str,u))]={'support_size':len(stencil),'exponent_sum':int(sum(stencil.values()))}
 out={'started_at':start,'runtime_seconds':time.perf_counter()-tic,'python':sys.version.split()[0],'sympy':sp.__version__,'platform':platform.platform(),'check_count':len(checks),'checks':checks,'eta_gain_order_000_to_111':list(map(int,gain)),'third_step_carry_gain':list(map(int,W*sp.Matrix([630+471*v[0]-246*v[1]+945*v[2] for v in V]))),'signed_support':signed_support,'bounds':{'carry_regression_n':list(range(1,7)),'vertices':8,'character_pairings':64},'scope':'Exact finite and symbolic checks. Universal algebraic proofs are in Lean/PROOF.md. No gamma arithmetic comparison.'}
 (ROOT/'evidence/exact_results.json').write_text(json.dumps(out,indent=2)+'\n')
 print('PASS:',len(checks),'exact checks')
if __name__=='__main__':main()
