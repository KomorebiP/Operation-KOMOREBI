#!/usr/bin/env python3
"""Exact tests for the general finite recurrence reconstruction obstruction."""
from fractions import Fraction as F
from itertools import product
from math import comb
from pathlib import Path
import random,json
ROOT=Path(__file__).resolve().parents[1]

def conv(a,b):
 c=[0]*(len(a)+len(b)-1)
 for i,x in enumerate(a):
  for j,y in enumerate(b):c[i+j]+=x*y
 return c

def evaluate(a,x):return sum(c*x**i for i,c in enumerate(a))

def period_poly(s):return [-1]+[0]*(s-1)+[1]

def shifted_poly(r,d):
 a=[1]
 for _ in range(d):a=conv(a,[-r,1])
 return a

def gen_recur(poly,initial,length):
 assert poly[-1]==1
 d=len(poly)-1
 a=list(map(F,initial))
 assert len(a)==d
 for _ in range(length-d):
  a.append(-sum(poly[j]*a[-d+j] for j in range(d)))
 return a

def run():
 rng=random.Random(27361)
 options=[]
 for p,q in [(2,3),(3,5),(5,7)]:
  for s in [1,2,3,4,6]: options.append((p,q,period_poly(s),'periodic'))
  for d in [1,2,3,4,7]: options.append((p,q,shifted_poly(1,d),'polynomial_depth'))
  for s in [2,3,4]:
   for d in [1,2,3]:options.append((p,q,conv(period_poly(s),shifted_poly(1,d)),'polyphase'))
  for d in [1,2,3]:options.append((p,q,conv(shifted_poly(-1,d),shifted_poly(1,d)),'parity_polynomial'))
 passed=0;examples=[]
 for p,q,poly,label in options:
  assert poly[-1]==1
  l=len(poly)-1
  filt=conv(poly,[-p,1])
  assert len(filt)==l+2
  assert evaluate(filt,p)==0
  assert evaluate(filt,q)==(q-p)*evaluate(poly,q)
  for trial in range(7):
   ini=[rng.randint(-7,7) for _ in range(l)]
   seq=gen_recur(poly,ini,30+l)
   lam=F(rng.randint(-10,10),rng.randint(1,9))
   for k in [0,1,3,5,10,17]:
    assert sum(poly[j]*seq[k+j] for j in range(l+1))==0
    assert sum(filt[j]*seq[k+j] for j in range(l+2))==0
    err=[F(q**(k+j))-lam*p**(k+j)-seq[k+j] for j in range(l+2)]
    annih=sum(filt[j]*err[j] for j in range(l+2))
    assert annih==q**k*(q-p)*evaluate(poly,q)
    max_error=max(abs(z) for z in err)
    norm=sum(abs(x) for x in filt)
    assert norm*max_error>=abs(annih)
    assert max_error>=F(q**k*abs(q-p)*abs(evaluate(poly,q)),norm)
    passed+=1
  if len(examples)<7:
   examples.append({"p":p,"q":q,"P":poly,"family":label,"filter":filt,
     "Pq":evaluate(poly,q),"bound_at_k3":str(F(q**3*abs(q-p)*abs(evaluate(poly,q)),sum(abs(x) for x in filt)))})
 # Negative control: a grammar containing q^j can reconstruct q^j exactly.
 for p,q in [(2,3),(3,5),(5,7)]:
  poly=[-q,1]
  filt=conv(poly,[-p,1])
  assert evaluate(poly,q)==0
  for k in range(1,12):
   seq=[q**j for j in range(k+5)]
   assert sum(filt[j]*seq[k+j] for j in range(3))==0
  # It makes a perfect reconstruction even with lambda=0.
  assert all(q**k - (0*p**k+q**k)==0 for k in range(1,20))
 output={"recurrence_families":len(options),"exact_checks":passed,"examples":examples,
  "negative_control":"P(z)=z-q contains q^k; exact correction exists with lambda=0",
  "proof_boundary":"No novel abc height estimate; the required q^k mode imports the transferred height."}
 (ROOT/'evidence/recurrence_results.json').write_text(json.dumps(output,indent=2)+'\n')
 print(json.dumps({"families":len(options),"exact_checks":passed,"neg_controls":3,"sample":examples[:2]},indent=2))
 print('PASS')
if __name__=='__main__':run()
