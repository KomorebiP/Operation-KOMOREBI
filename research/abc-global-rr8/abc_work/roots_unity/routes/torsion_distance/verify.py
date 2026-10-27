"""Exact Hensel checks for the bounded-exponent coefficient-uniformity obstruction.
Run: python3 abc_work/roots_unity/routes/torsion_distance/verify.py
No factorization of A**n+1 beyond the named p is claimed.
"""
from pathlib import Path
import hashlib,json,platform
ROOT=Path(__file__).resolve().parent
INPUT=Path('abc_work/routes/global/PROOF_NOTE.md')
def vp(n,p):
 assert n
 e=0
 while n%p==0:e+=1;n//=p
 return e

def lift_family(p,M):
 assert p%4==1
 r=next(a for a in range(1,p) if (a*a+1)%p==0)
 modulus=p;out=[]
 for m in range(1,M+1):
  assert 1<=r<modulus and (r*r+1)%modulus==0
  assert pow(r,2,p)==p-1 and pow(r,4,p)==1
  e=vp(r*r+1,p)
  # d_p=4; A^2-1 is a p-adic unit, so e_p equals the sum valuation.
  assert vp(r**4-1,p)==e and e>=m
  out.append({'m':m,'A':r,'p':p,'n':2,'B':1,'order':4,'e_p':e,
              'named_prime_lower_bound_on_W':p**(e-1),
              'c':r*r+1,'height_bound_A_less_than_p_power_m':r<modulus})
  # Unique Hensel digit from f(r+t*p^m)/p^m = f(r)/p^m+2*r*t mod p.
  t=(-((r*r+1)//modulus)*pow(2*r,-1,p))%p
  r+=t*modulus;modulus*=p
 return out
out={'assertion_tested':'Hensel root family A_m^2+1 divisible by p^m, primitive order4, and exact equality e_p=v_p(A_m^2+1) for p=5,101, m=1..20. This tests a coefficient-uniformity obstruction for bounded n, not a large-n conjecture.',
'non_claims':['No full factorization of outputs or computation of total W_n.','No counterexample to ABC.','No counterexample to a bound only as n tends to infinity.'],
'command':'python3 abc_work/roots_unity/routes/torsion_distance/verify.py','python':platform.python_version(),
'input_sha256':hashlib.sha256(INPUT.read_bytes()).hexdigest(),
'cases':lift_family(5,20)+lift_family(101,20)}
(ROOT/'results.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='cases'},indent=2))
print('Verified',len(out['cases']),'exact named-prime cases')
