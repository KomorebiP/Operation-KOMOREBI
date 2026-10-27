#!/usr/bin/env python3
"""Exact cutoff cubic and fixed-control actual nonlinear/source-jet checks."""
from pathlib import Path
from fractions import Fraction as F
from math import factorial
import sys,json,time
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'bernoulli_closure/separation/carry_adapted'))
import check_carry_adapted as ca
b=ca.base
P=384;MOD=1<<P

def add(*parts):
 out=[F(0)]*max(map(len,parts))
 for p in parts:
  for i,v in enumerate(p):out[i]+=v
 return out

def scale(a,c):return [c*x for x in a]
def mul(a,b):
 out=[F(0)]*(len(a)+len(b)-1)
 for i,x in enumerate(a):
  for j,y in enumerate(b):out[i+j]+=x*y
 return out

def shift(a,k):return [F(0)]*k+a
def theta(a):return [i*x for i,x in enumerate(a)]
def rec(a):
 z=add(theta(a),scale(a,-1))
 return add(mul(z,z),scale(shift(mul(a,a),1),-1),scale(mul(mul(a,a),a),-1))

def formal_checks(beta):
 assert all(x==0 for x in rec(beta)[:len(beta)])
 count=0
 for r in range(3,13):
  p=beta[:r];B=beta[r:r+17];a=add(theta(p),scale(p,-1))
  W=add(scale(B,r-1),theta(B));cut=rec(p)
  assert all(x==0 for x in cut[:r]);forcing=cut[r:]
  full=add(forcing,scale(mul(a,W),2),scale(mul(add(scale(shift(p,1),2),scale(mul(p,p),3)),B),-1),
           shift(add(mul(W,W),scale(mul(add([F(0),F(1)],scale(p,3)),mul(B,B)),-1)),r),
           scale(shift(mul(mul(B,B),B),2*r),-1))
  assert all(x==0 for x in full[:17]);count+=17
  Ap=scale(a,2);Cp=add(scale(a,2*(r-1)),scale(shift(p,1),-2),scale(mul(p,p),-3))
  assert Ap[:3]==[F(-2),F(0),F(2,15)]
  assert Cp[:3]==[F(-2*r-1),F(0),F(2*r-3,15)]
 return count

def main(output):
 start=time.monotonic();ca.P=P;ca.MOD=MOD
 b.B=b.bernoullis(P);b.twoB=ca.fast_twoB
 beta=[(1-2*n)*F(4**n)*b.B[2*n]/factorial(2*n) for n in range(P//3+1)]
 formal_count=formal_checks(beta[:32]);src=list(b.source(P))
 assert all(b.v2(a,P)>=i for i,a in enumerate(src))
 beta2=mul(beta,beta)
 records=[]
 for T in [0,718787533,22831001499602523078606181325]:
  r=(17659+(1<<18)*T)*(1<<640)-161
  Q=(P+r.bit_count()-156)//3;gamma=b.gamma(r,-154,P,Q)
  assert all(x%2==0 for x in gamma[:1])
  gg=ca.localize(gamma,src);assert all(v%(1<<178)==0 for v in gg)
  K=[v>>178 for v in gg]
  assert all((i*K[i])%2==0 for i in range(1,len(K)))
  half=[i*K[i]//2 for i in range(1,len(K))]
  assert half[1]%2==1 and all(a%2==0 for a in half[2:])
  c=0
  for j in range(P-179):
   if b.ev(half,c,1<<(j+1)):c+=1<<j
  assert c%128==20
  vg=[q*x%MOD for q,x in enumerate(gamma)];vv=ca.localize(vg,src)
  alpha=[0,0];chi=[0,0]
  for j in range(2,len(beta)):
   alpha.append(b.fmod(8**j*2*(j-1)*beta[j],P))
   chi.append(b.fmod(8**j*(2*(r-1)*(j-1)*beta[j]-2*beta[j-1]-3*beta2[j]),P))
  ag=b.mul(alpha,vg,MOD);cg=b.mul(chi,gamma,MOD)
  rg=[((ag[i] if i<len(ag) else 0)+(cg[i] if i<len(cg) else 0))%MOD for i in range(max(len(ag),len(cg)))]
  rr=ca.localize(rg,src)
  # The exact cutoff theorem identifies this residue with sigma*T_F A;
  # the nonlinear terms vanish modulo 2^P because 3r>P.
  assert 3*r>P and r.bit_count()-1-154>0
  ee=[(2*v+(2*r+1)*g-rv)%MOD for v,g,rv in zip(vv,gg,rr)]
  square=ca.localize(b.mul(gamma,gamma,MOD),src)
  def value(poly):return b.ev(poly,c,MOD)
  def dx(poly):return b.ev(b.deriv(poly),c,MOD)>>15
  sv=value(square);sx=dx(square);ev=value(ee);ex=dx(ee)
  assert b.v2(sv,P)==307 and (sv>>307)%8==5
  assert b.v2(sx,P-15)==306
  assert b.v2(ev,P)==155 and (ev>>155)%8==3
  assert b.v2(ex,P-15)==156 and (ex>>156)%4==3
  assert b.v2(value(rr),P)>=159 and b.v2(dx(rr),P-15)>=158
  assert min(b.v2(a,P) for a in square)==307
  assert b.v2(value(vv),P)==154 and (value(vv)>>154)%8==3
  assert b.v2(dx(vv),P-15)==155 and (dx(vv)>>155)%8==7
  phi=b.ev(K,c,1<<(P-178));pv=b.v2(phi,P-178)
  assert pv=={0:0,718787533:30,22831001499602523078606181325:91}[T]
  records.append({'T':str(T),'critical_value_valuation':pv,
   'actual_square_valuation':307,'actual_square_unit_mod8':5,'actual_square_x_derivative_valuation':306,
   'forcing_valuation':155,'forcing_unit_mod8':3,'forcing_x_derivative_valuation':156,
   'forcing_x_derivative_unit_mod4':3,'linear_remainder_value_valuation_or_bound':b.v2(value(rr),P),
   'linear_remainder_x_derivative_valuation_or_bound':b.v2(dx(rr),P-15),
   'packet_cutoff':Q,'critical_center_bits':P-179})
 result={'status':'passed','formal_cutoff_coefficients_checked':formal_count,'formal_beta_identity_through_degree':31,
  'global_bits':P,'controls':records,'seconds':time.monotonic()-start,
  'nonclaims':['No universal critical nonvanishing.','No new multiplier digits or approximation ranks.',
   'Forcing evaluated through the proved exact cutoff identity; not an independent huge-prefix reconstruction.',
   'No source-Newton inverse dictionary or pointwise product substitution is used.']}
 Path(output).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main(sys.argv[1] if len(sys.argv)>1 else 'CHECKS.json')
