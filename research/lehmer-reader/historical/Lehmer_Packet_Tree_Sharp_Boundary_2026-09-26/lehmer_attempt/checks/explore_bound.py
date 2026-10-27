from itertools import combinations,product
from fractions import Fraction as F
from math import prod
def det(a):
 if len(a)==1:return a[0][0]
 return sum((-1)**j*a[0][j]*det([[a[r][c] for c in range(len(a)) if c!=j] for r in range(1,len(a))]) for j in range(len(a)))
def inverse(a):
 d=det(a)
 return [[F((-1)**(i+j)*det([[a[r][c] for c in range(3) if c!=i] for r in range(3) if r!=j]),d) for j in range(3)] for i in range(3)]

def weight(v): return prod(v[i]-v[j] for i,j in combinations(range(5),2))//288
T=[]
for e in range(5):
 rest=[i for i in range(5) if i!=e]
 for plus in combinations(rest,2):
  d=tuple(0 if i==e else (1 if i in plus else -1) for i in range(5))
  if sum(i*d[i] for i in range(5))%5:continue
  for i,j in combinations(range(5),2):
   delta=d[i]-d[j]
   if abs(delta)!=1 or (i-j)%5 not in (1,4):continue
   sg=1 if (i-j)%5==1 else -1
   l=[int(z==i)-int(z==j) for z in range(5)]
   A=[[1]*5,d,l]
   piv=next(c for c in combinations(range(5),3) if det([[row[z] for z in c] for row in A]))
   free=[z for z in range(5) if z not in piv]
   inv=inverse([[row[z] for z in piv] for row in A])
   Tf=[[-sum(inv[r][j]*A[j][z] for j in range(3)) for z in free] for r in range(3)]
   Tb=[row[2]*sg for row in inv]
   T.append((d,delta,l,piv,free,Tf,Tb,sg))

def minimum(k):
 M=2**k;a=5*M//2;out=[]
 for d,delta,l,piv,free,Tf,Tb,sg in T:
  star=[F(sg*(a+1)*(4*l[z]-delta*d[z]),7) for z in range(5)]
  ranges=[]
  for z in free:
   near=(star[z].numerator//star[z].denominator-z)//5
   ranges.append([z+5*h for h in range(near-2,near+4)])
  for u in product(*ranges):
   m=[0]*5
   for z,c in zip(free,u):m[z]=c
   ok=True
   for r,z in enumerate(piv):
    val=sum(F(Tf[r][c])*u[c] for c in range(2))+F(Tb[r])*(a+1)
    if val.denominator!=1 or int(val)%5!=z:ok=False;break
    m[z]=int(val)
   if not ok:continue
   v=tuple(m[i]-a*d[i] for i in range(5));w=tuple(m[i]+a*d[i] for i in range(5))
   if weight(v)*weight(w)>=0:continue
   n=sum(z*z for z in v)//10
   out.append((n,v,w,d,tuple(m)))
 return min(out)
if __name__=='__main__':
 for k in range(1,10):
  M=2**k;lo=(100*M*M+10*M+36)//35;b=minimum(k)
  print(k,lo,b,flush=True)
