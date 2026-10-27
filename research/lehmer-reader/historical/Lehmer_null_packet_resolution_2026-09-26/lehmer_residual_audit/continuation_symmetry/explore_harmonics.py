import sys
from pathlib import Path
from fractions import Fraction
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'continuation_5core'))
from explore_shell import shell,weight
from explore import tau_triangular,sigma_primes

def Q(v):
 p2=sum(x*x for x in v);p3=sum(x**3 for x in v);p4=sum(x**4 for x in v);p5=sum(x**5 for x in v)
 return 6273*p2**4-33750*p2*p2*p4-56800*p2*p3*p3+69600*p3*p5+45000*p4*p4

def feasible(vs,target):
 lo=hi=None; lw=hw=None
 for v in vs:
  w=weight(v);q=Q(v);s=target*(1 if w>0 else -1)
  a=s*q
  if not a:
   if s<0:return False,('zero',v)
   continue
  root=Fraction(-1,q)
  if a>0 and (lo is None or root>lo):lo=root;lw=v
  if a<0 and (hi is None or root<hi):hi=root;hw=v
 if lo is not None and hi is not None and lo>=hi:return False,('interval',lo,hi,lw,hw)
 return True,(lo,hi)
for p in sigma_primes(100)[1]:
 vs=list(shell(p));assert sum(weight(v)*Q(v) for v in vs)==0
 yes=[]
 for s in (1,-1):
  ok,r=feasible(vs,s)
  if ok:yes.append((s,str(r)))
 print(p,yes)
 if p in [7,19,31]:
  print('failure details',[(s,feasible(vs,s)) for s in [1,-1]])
