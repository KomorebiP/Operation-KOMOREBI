#!/usr/bin/env python3
"""Exact polynomial and integration identities; finite tests are not universal proofs."""
from pathlib import Path
from datetime import datetime, timezone
import json, time, sys, math
import sympy as s
ROOT=Path(__file__).resolve().parents[1]
def main():
 start=datetime.now(timezone.utc).isoformat();tic=time.perf_counter();checks=[];neg=[]
 def zero(name,expr):
  assert s.cancel(s.expand(expr))==0,(name,expr);checks.append(name)
 def true(name,cond):
  assert cond,name;checks.append(name)
 def nonzero(name,expr):
  assert s.cancel(s.expand(expr))!=0,name;neg.append(name)
 x,c,k=s.symbols('x c k');f0,f1,fc,dc=s.symbols('f0 f1 fc dc')
 c3=s.Rational(1,3)
 # Independent exact integration on a polynomial basis.
 for n in range(15):
  f=x**n;g=s.diff(f,x,2)
  lhs=-2*s.integrate(x*g,(x,0,c3))+s.integrate((x-1)*g,(x,c3,1))
  zero(f'Green identity monomial degree {n}',lhs-(3*f.subs(x,c3)-2*f.subs(x,0)-f.subs(x,1)))
 # Integration by parts endpoint algebra, valid for general twice differentiable f.
 left=c3*dc-fc+f0;right=-(c3-1)*dc+fc-f1
 zero('general endpoint algebra',-2*left+right-(3*fc-2*f0-f1))
 zero('kernel total signed mass',-2*s.integrate(x,(x,0,c3))+s.integrate(x-1,(x,c3,1))+s.Rational(1,3))
 zero('kernel absolute mass',2*s.integrate(x,(x,0,c3))+s.integrate(1-x,(x,c3,1))-s.Rational(1,3))
 # Fourier antiderivatives checked by differentiation, not numeric quadrature.
 A=s.exp(k*x)*(x/k-1/k**2);B=s.exp(k*x)*((x-1)/k-1/k**2)
 zero('Fourier first primitive',s.diff(A,x)-x*s.exp(k*x))
 zero('Fourier second primitive',s.diff(B,x)-(x-1)*s.exp(k*x))
 moment=-2*(A.subs(x,c3)-A.subs(x,0))+B.subs(x,1)-B.subs(x,c3)
 zero('Fourier Green multiplier',moment-(3*s.exp(k/3)-2-s.exp(k))/k**2)
 w=s.symbols('w')
 zero('conductor three taps zeroth moment',-2+3-1)
 zero('conductor three taps first moment',3*c3-1)
 for n in range(1,31):
  if n%3==0:zero(f'mode {n} annihilated at cubic residue',s.rem(w**n-1,w*w+w+1,w))
 true('active modes through 2500',sum(math.gcd(n,15)==1 for n in range(1,2501))==1333)
 # Actual cubic chart: degree and rational inverse.
 b,t=s.symbols('b t');tb=-(b*b+2*b)/15
 zero('actual chart cubic',s.rem(225*tb**3-42*tb+7,b**3-7,b))
 zero('actual chart inverse',s.rem((2-b)*(4-15*tb)-1,b**3-7,b))
 true('primitive chart polynomial irreducible',s.Poly(225*t**3-42*t+7,t).is_irreducible)
 # A fractional-linear image of a quadratic point satisfies a quadratic.
 a,b0,c0,d0,z=s.symbols('a b c d z');W=s.symbols('W')
 Q=(c0*c0-c0*d0+d0*d0)*z*z+(-2*b0*d0+b0*c0+a*d0-2*a*c0)*z+(a*a-a*b0+b0*b0)
 zero('Mobius quadratic elimination',s.rem(s.together(Q.subs(z,(a*W+b0)/(c0*W+d0))*(c0*W+d0)**2).cancel(),W*W+W+1,W))
 zero('positive quadratic coefficient',2*(c0*c0-c0*d0+d0*d0)-(c0*c0+d0*d0+(c0-d0)**2))
 zero('rank-three norm Bezout',15*7-4*26-1)
 zero('cube branch distance identity',s.rem((z-1)**2+3*z,z*z+z+1,z))
 nonzero('dropping endpoint f(1) changes the Green identity',(3*fc-3*f0)-(3*fc-2*f0-f1))
 nonzero('wrong junction does not kill slope',-2*c+(1-c))
 nonzero('one scalar norm is insufficient',s.rem(z-1,s.cyclotomic_poly(7,z),z))
 nonzero('linear phase changes the value at one third',s.rem(w-1,w*w+w+1,w))
 rec={'started_at':start,'runtime_seconds':time.perf_counter()-tic,'exit_status':0,'check_count':len(checks),'checks':checks,'negative_controls':neg,'sympy':s.__version__,'python':sys.version.split()[0],'scope':'Exact rational polynomial/symbolic identities and declared finite regressions. Universal Green theorem is separately compiled in Lean.'}
 (ROOT/'evidence/exact_results.json').write_text(json.dumps(rec,indent=2)+'\n')
 print('PASS',len(checks),'exact checks;',len(neg),'negative controls')
if __name__=='__main__':main()
