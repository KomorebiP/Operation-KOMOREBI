#!/usr/bin/env python3
"""Bounded exact controls for the carry criterion and surviving depleted poles.
The general conclusions are proved in CARRY_AND_POLE_ATTEMPT.md.
"""
from fractions import Fraction as F
from math import comb,factorial,prod
from pathlib import Path
import hashlib,json,sys,time

P=64; MOD=1<<P

def v2(n):
 if not n:return P
 n=abs(n);return (n&-n).bit_length()-1

def mf(q):
 q=F(q);assert q.denominator%2
 return q.numerator*pow(q.denominator,-1,MOD)%MOD

def bernoulli(n):
 out=[F(1)]
 for m in range(1,n+1):out.append(-sum((comb(m+1,k)*out[k] for k in range(m)),F(0))/(m+1))
 return out

BER=bernoulli(P)

def choose(n,k):
 z=prod(n-i for i in range(k))
 assert z%factorial(k)==0
 return z//factorial(k)

def D(z):
 return sum(choose(2*z,k)*mf((1<<k)*BER[k]) for k in range(P+1))%MOD

def source(n):return F(9**(n+1)-1,8*(n+1)*(2*n+1))

def skeleton(q,x):return prod((x-i)*(2*x-2*i-1) for i in range(q))

def carry_exact(B,M):
 # d greater than this bound cannot fail by s2(B+d)>=1.
 cutoff=max(1,(B.bit_count()-1)//M+1)
 return all(M*d+(B+d).bit_count()-B.bit_count()>0 for d in range(1,cutoff+1))

def carry_bits(B,M):
 for t in range(B.bit_length()+1):
  if (B>>t)&1:continue
  b=B% (1<<t)
  if b.bit_count()>M*((1<<t)-b):return False
 return True

def scaled_value(m,h):
 r=(1<<h)-m;out=0;Dr=D(r)
 for q in range(m+1):
  scale=F((1<<(h+5*q))*(2*r+2*q-1),(2*r-1)*prod(2*r+i for i in range(1,2*q+1)))
  unit=D(r+q)*pow(Dr,-1,MOD)%MOD
  out=(out+mf(scale*source(m-q))*unit*skeleton(q,m))%MOD
 return out

def residue_value(m):
 denominator=2*prod(-2*m+i for i in range(1,2*m+1) if i!=2*m)
 scale=F((1<<(5*m))*(-1),(-2*m-1)*denominator)
 return mf(scale)*pow(D(-m),-1,MOD)*skeleton(m,m)%MOD

def run():
 start=time.monotonic();count=0;heredity=0;forbidden=0
 for M in (1,2,3,6,12):
  for B in range(1,2048,2):
   ok=carry_exact(B,M);assert ok==carry_bits(B,M)
   count+=1
   if ok:
    for h in range(1,B.bit_length()+1):
     assert carry_exact(B%(1<<h),M);heredity+=1
  for d in range(1,16,2):
   h=M*d+(d-1).bit_count()+1
   for Q in (0,1,2,7):
    B=(Q+1)*(1<<h)-d
    assert M*d+(B+d).bit_count()-B.bit_count()<=0
    forbidden+=1
 controls=[]
 for m in range(1,5):
  R=residue_value(m)
  assert v2(R)==4*m+v2(m)
  values=[]
  for h in (8,12,16,20,28,36):
   z=scaled_value(m,h);distance=v2((z-R)%MOD)
   assert distance>=h
   values.append({'h':h,'scaled_value_mod2_64':str(z),'distance_to_residue_valuation':distance})
  controls.append({'m':m,'residue_mod2_64':str(R),'residue_valuation':v2(R),'sequence':values})
 return {'status':'PASS','coefficient_domain':'Exact integers and fractions; pole controls modulo2^64',
 'carry_bounds':{'M':[1,2,3,6,12],'odd_B':'1..2047','forbidden_d':'odd1..15','extension_Q':[0,1,2,7]},
 'carry_checks':count,'hereditary_prefix_checks':heredity,'forbidden_neighborhood_checks':forbidden,
 'pole_controls':controls,
 'nonclaims':['No actual Euler nonintersection proved.','No singular-parameter digits added.','Finite controls do not replace general proof.'],
 'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'elapsed_seconds':time.monotonic()-start}

if __name__=='__main__':
 result=run();out=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).with_name('CARRY_POLE_CONTROLS.json')
 out.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ['status','carry_checks','hereditary_prefix_checks','forbidden_neighborhood_checks','elapsed_seconds']},indent=2))
