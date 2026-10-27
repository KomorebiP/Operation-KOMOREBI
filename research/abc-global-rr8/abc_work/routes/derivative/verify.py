"""Exact bounded audit of arithmetic-derivative lattice candidates.

Run: python3 abc_work/routes/derivative/verify.py
Bounded assertions do not establish an asymptotic ABC bound.
"""
from pathlib import Path
from math import gcd,lcm
from functools import reduce
import hashlib,json,platform,time

ROOT=Path(__file__).resolve().parent
INPUT=Path('abc_work/base/ABC_Square_Kernel_Reverse_Realization_2026-10-25/abc_square_kernel_bridge_20261025/PROOF_NOTE.md')
def factor(n):
 out={};p=2
 while p*p<=n:
  while n%p==0:out[p]=out.get(p,0)+1;n//=p
  p+=1
 if n>1:out[n]=out.get(n,0)+1
 return out

def g(n):return reduce(gcd,(e*(n//p) for p,e in factor(n).items()))

def audit(b,c,cap):
 # Cases have b supported on two primes and c a power of one prime.
 fb,fc=factor(b),factor(c)
 assert c==b+1 and len(fb)==2 and len(fc)==1
 ps=list(fb);q=next(iter(fc))
 A=[fb[p]*(b//p) for p in ps];C=fc[q]*(c//q)
 best_all=None;best_nondeg=None;w_all=None;w_nondeg=None;tested=0
 for x in range(-cap,cap+1):
  for y in range(-cap,cap+1):
   t=A[0]*x+A[1]*y
   if t%C:continue
   z=t//C
   if abs(z)>cap or (x,y,z)==(0,0,0):continue
   tested+=1
   h=max(abs(x),abs(y),abs(z))
   if best_all is None or h<best_all:best_all=h;w_all=[x,y,z]
   if t and (best_nondeg is None or h<best_nondeg):best_nondeg=h;w_nondeg=[x,y,z]
 # All smaller cubes are included: any found minimum <=cap is exact.
 assert best_nondeg is not None
 L=lcm(g(b),g(c));R=reduce(lambda a,p:a*p,set(fb)|set(fc),1)
 assert L%(b*c//R)==0
 assert A[0]*w_nondeg[0]+A[1]*w_nondeg[1]==C*w_nondeg[2]
 return {'b':b,'c':c,'primes':ps+[q],'coefficients':A+[-C],
 'cap':cap,'nonzero_solutions_in_cube':tested,'shortest_nonzero_height':best_all,
 'shortest_nonzero_witness':w_all,'minimum_nondegenerate_height':best_nondeg,
 'nondegenerate_witness':w_nondeg,'G_b':g(b),'G_c':g(c),'minimum_absolute_W':L,
 'R':R,'minimum_height_exceeds_sqrt_c':best_nondeg**2>c}

start=time.time();before=hashlib.sha256(INPUT.read_bytes()).hexdigest()
cases=[audit(36,37,12),audit(48,49,8),audit(80,81,10),audit(108,109,108)]
assert [(x['shortest_nonzero_height'],x['minimum_nondegenerate_height']) for x in cases]==[(3,12),(6,8),(4,4),(1,108)]
assert before==hashlib.sha256(INPUT.read_bytes()).hexdigest()
out={'assertion_tested':'For four named primitive triples, exact minimum l-infinity norms of nonzero additive arithmetic derivations and of derivations with nonzero Wronskian; full integer cubes up to indicated caps, all smaller cubes included.','non_claims':['No universal ABC inequality.','No counterexample to the full ABC conjecture or to eventual small-derivative conjectures.','No numerical tolerance.'], 'command':'python3 abc_work/routes/derivative/verify.py','python':platform.python_version(),'input_sha256':before,'elapsed_seconds':time.time()-start,'cases':cases}
(ROOT/'results.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
