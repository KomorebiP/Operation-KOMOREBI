import sys, itertools, json, math, time
from pathlib import Path
sys.dont_write_bytecode=True
C=Path('/mnt/data/beal65_session/frozen64/Komorebi_Beal_Block64/work64/computations');sys.path.insert(0,str(C))
import conductor64 as cs

def mul(a,b):
 c=[0]*11
 for i,x in enumerate(a):
  for j,y in enumerate(b):c[i+j]+=x*y
 for i in range(10,5,-1):
  t=c[i]
  for j in range(7):c[i-6+j]-=t
 return c[:6]
def det(A):
 a=[r[:] for r in A];prev=1;sgn=1
 for k in range(len(a)-1):
  piv=next((i for i in range(k,len(a)) if a[i][k]),None)
  if piv is None:return 0
  if piv!=k:a[k],a[piv]=a[piv],a[k];sgn=-sgn
  p=a[k][k]
  for i in range(k+1,len(a)):
   for j in range(k+1,len(a)):a[i][j]=(a[i][j]*p-a[i][k]*a[k][j])//prev
   a[i][k]=0
  prev=p
 return sgn*a[-1][-1]
def norm(a):
 cols=[mul(a,[int(i==j) for i in range(6)]) for j in range(6)]
 return det([list(x) for x in zip(*cols)])
primes=[379,421,449,631,659,701,911, 743]
found={}
t=time.monotonic()
for bound in (1,2,3):
 for a in itertools.product(range(-bound,bound+1),repeat=6):
  if bound>1 and max(map(abs,a))!=bound:continue
  n=norm(a)
  if n in primes and n not in found:
   found[n]=a; print('found',n,a,flush=True)
  if len(found)==len(primes):break
 if len(found)==len(primes):break
print('search seconds',time.monotonic()-t,flush=True)
out=[]
for q,a in found.items():
 if q==743:continue
 z=next(x for x in range(2,q) if pow(x,7,q)==1 and cs.ev(a,x,q)==0)
 def kl(v):return next(j for j in range(7) if pow(z,j,q)==pow(v%q,(q-1)//7,q))
 ph=[x for x in range(q) if (x*x-x-1)%q==0]
 K=[[kl(x),kl(3),kl(2*x-1)] for x in ph]
 beta=0;R=[]
 for ell,s in [(547,5),(743,1)]:
  g=cs.primitive(ell);r=pow(g,(ell-1)//7,ell);log={pow(g,j,ell):j%7 for j in range(ell-1)}
  v=-sum(b*log[cs.ev(a,pow(r,b,ell),ell)] for b in range(1,7))%7
  R.append(v);beta=(beta+s*v)%7
 products=[cs.MUL[cs.dot(k,[7,6,1])][beta] for k in K]
 row=dict(q=q,pi=a,root=z,phi_roots=ph,K=K,row=R,beta=beta,products=products)
 out.append(row);print(row,flush=True)
Path('/mnt/data/beal65_session/exploration/prime_candidates.json').write_text(json.dumps(out,indent=2))
