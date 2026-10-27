from math import isqrt, prod
from collections import Counter
from fractions import Fraction
import sys, time
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent.parent))
from explore import tau_triangular, sigma_primes

PAIRS=[(i,j) for i in range(5) for j in range(i+1,5)]

def shell(n):
    if n<1: raise ValueError(n)
    R=isqrt(10*n)
    lanes=[range(-R + (i+R)%5,R+1,5) for i in range(3)]
    for a in lanes[0]:
      aa=a*a
      for b in lanes[1]:
        aabb=aa+b*b
        if aabb>10*n: continue
        for c in lanes[2]:
          rem=10*n-aabb-c*c
          if rem<0: continue
          s=-a-b-c
          D=2*rem-s*s
          if D<0: continue
          d=isqrt(D)
          if d*d!=D: continue
          for z in ((d,-d) if d else (0,)):
            if (s+z)%2: continue
            v3=(s+z)//2;v4=s-v3
            if v3%5==3 and v4%5==4:
              yield (a,b,c,v3,v4)

def weight(v):
    z=prod(v[i]-v[j] for i,j in PAIRS)
    w,rem=divmod(z,288)
    assert rem==0
    return w

def polynomial(v):
    c=[(v[i]-i)//5 for i in range(5)]
    P=[1]
    for i,j in PAIRS:
      a=i-j;b=c[i]-c[j]
      Q=[0]*(len(P)+1)
      for k,z in enumerate(P):Q[k]+=a*z;Q[k+1]+=b*z
      P=Q
    assert sum(P[k]*5**k for k in range(11))==288*weight(v)
    return P

def val(n,p):
    if not n:return None
    k=0
    while n%p==0:k+=1;n//=p
    return k

def chi5(n):return 0 if n%5==0 else 1 if n%5 in (1,4) else -1

if __name__=='__main__':
 t=time.perf_counter()
 ns=[1,2,3,5,7,11,19,29,59,79,101,149,499,2411]
 tau=tau_triangular(max(ns))
 for n in ns:
  vs=list(shell(n));ws=list(map(weight,vs));B=[0]*11
  for v in vs:
   pp=polynomial(v)
   for k,b in enumerate(pp):B[k]+=b
  assert sum(ws)==tau[n]
  if n>1:assert len(vs)==n+chi5(n)
  print(n,'count',len(vs),'sum',sum(ws),'positive',sum(w>0 for w in ws),'negative',sum(w<0 for w in ws),'v5',val(sum(ws),5),'v_n',val(sum(ws),n) if n>1 else None,flush=True)
  if n in (19,29,2411):
   print('B',B,flush=True)
   if n==19:print('weights',ws,flush=True)
 print('seconds',time.perf_counter()-t)
