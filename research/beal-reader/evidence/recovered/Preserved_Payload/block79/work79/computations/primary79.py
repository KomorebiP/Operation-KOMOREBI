#!/usr/bin/env python3
"""Exact finite assertions for Block79. Standard-library only. No proof by sampling."""
import json,hashlib,itertools
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SUPPORTS={
 'A':[307,337,547,673,743,797,883,1483,1933],
 'B':[197,307,337,547,673,797,883,1483,1933],
 'C':[197,307,337,547,673,743,883,1483,1933],
 'D':[197,307,337,547,743,797,883,1483,1933]}
class Quadratic:
 def __init__(self,m,a,b):self.m,self.a,self.b=m,a,b # t^2=a+b*t
 def add(self,x,y):return ((x[0]+y[0])%self.m,(x[1]+y[1])%self.m)
 def neg(self,x):return (-x[0]%self.m,-x[1]%self.m)
 def sub(self,x,y):return self.add(x,self.neg(y))
 def mul(self,x,y):
  a,b=x;c,d=y;m=self.m
  return ((a*c+self.a*b*d)%m,(a*d+b*c+self.b*b*d)%m)
 def scale(self,n,x):return (n*x[0]%self.m,n*x[1]%self.m)
 def power(self,x,n):
  v=(1,0)
  while n:
   if n&1:v=self.mul(v,x)
   x=self.mul(x,x);n//=2
  return v
 def inv(self,x):
  m=self.m;a,b=x;N=(a*a+self.b*a*b-self.a*b*b)%m;d=pow(N,-1,m)
  return ((a+self.b*b)*d%m,-b*d%m)
def code(x):return x[0]+7*x[1]
def mm(F,A,B):
 return tuple(F.add(F.mul(A[2*i],B[j]),F.mul(A[2*i+1],B[2+j])) for i in range(2) for j in range(2))
def ma(F,A,B):return tuple(F.add(x,y) for x,y in zip(A,B))
def ms(F,A,B):return tuple(F.sub(x,y) for x,y in zip(A,B))
def sm(F,n,A):return tuple(F.scale(n,x) for x in A)
def rref(M):
 A=[r[:] for r in M];piv=[];i=0
 for j in range(len(A[0])):
  k=next((k for k in range(i,len(A)) if A[k][j]%7),None)
  if k is None:continue
  A[i],A[k]=A[k],A[i];v=pow(A[i][j]%7,-1,7);A[i]=[x*v%7 for x in A[i]]
  for k in range(len(A)):
   if k!=i:
    v=A[k][j];A[k]=[(x-v*y)%7 for x,y in zip(A[k],A[i])]
  piv.append(j);i+=1
  if i==len(A):break
 return A,piv
def kernel(M):
 A,P=rref(M);basis=[]
 for j in range(len(A[0])):
  if j not in P:
   v=[0]*len(A[0]);v[j]=1
   for i,p in enumerate(P):v[p]=-A[i][j]%7
   basis.append(v)
 return basis

def algebra():
 F=Quadratic(7,5,0);K=[(a,b) for b in range(7) for a in range(7)];zero=(0,0)
 nil=lowerzero=0
 for p,z,c in itertools.product(K,repeat=3):
  if F.add(F.mul(p,p),F.mul(z,c))==zero:
   nil+=1
   if c==zero:
    assert p==zero;lowerzero+=1
 assert nil==2401 and lowerzero==49
 count=wrong=0;agg=0
 for h in range(7):
  for c in K[1:]:
   for b in K:
    for theta in K:
     pt=F.mul(theta,c);pf=F.sub(F.mul(theta,b),(h,0))
     qt=F.neg(F.mul(F.mul(theta,theta),c))
     qf=F.sub(F.scale(h,theta),F.mul(F.mul(theta,theta),b))
     assert F.add(F.mul(c,qt),F.mul(pt,pt))==zero
     assert F.add(F.mul(c,qf),F.mul(pt,pf))==zero
     assert F.sub(F.mul(c,pf),F.mul(b,pt))==F.scale(-h,c)
     assert F.mul(c,qt)==F.neg(F.mul(pt,pt))
     wrong+=F.mul(c,qt)!=F.mul(pt,pt)
     m=3
     assert F.add(F.mul(c,F.add(qf,F.scale(m,qt))),F.mul(pt,F.add(pf,F.scale(m,pt))))==zero
     agg=(agg+code(pt)+49*code(pf)+2401*code(qt)+117649*code(qf))%(2**64)
     count+=1
 # Rational toric nilpotence (not just trace) is essential.
 assert mm(F,((1,0),zero,zero,(6,0)),((1,0),zero,zero,(6,0)))!= (zero,)*4
 return {'traceless_matrices':49**3,'nilpotent_matrices':nil,'nilpotents_with_lower_zero':lowerzero,
         'support_packets':count,'quadratic_wrong_sign_rejected':wrong,'packet_aggregate':agg}

def auxiliary():
 R=Quadratic(343,5,0);o=(1,0);z=(0,0);I=(o,z,z,o)
 Qs=[13**2,29,31,97**2,197**2,883**2,5167**2]
 vals=[(a,b) for b in range(7) for a in range(7)];ct=bc=0;ag=0
 for Q in Qs:
  iq=pow(Q,-1,7)
  for y,r,u in itertools.product(vals,vals,[(1,0),(0,1)]):
   yr=R.mul(y,r);y2=R.mul(y,y)
   N=(R.scale(-49,R.mul(u,y)),R.scale(7,u),R.scale(-343,R.mul(u,y2)),R.scale(49,R.mul(u,y)))
   P=R.sub(((Q-1)%343,0),R.scale(7,yr))
   F=(R.add(o,P),r,R.scale(7,R.mul(y,P)),R.add(o,R.scale(7,yr)))
   assert mm(R,N,N)==(z,)*4
   assert mm(R,F,N)==sm(R,Q,N) and mm(R,N,F)==N
   assert R.sub(R.mul(F[0],F[3]),R.mul(F[1],F[2]))==(Q%343,0)
   assert all(t%49==0 for x in (N[0],N[3]) for t in x)
   assert N[2]==z
   beta=tuple(((v//7)*iq)%7 for v in F[2])
   expected=tuple(v*(Q-1)*iq%7 for v in y)
   assert beta==expected
   if Q%7==1:
    assert beta==(0,0);bc+=1
   ag=(ag+sum((i+1)*(x[0]+343*x[1]) for i,x in enumerate(F)))%(2**64);ct+=1
 return {'cases':ct,'norms':Qs,'norm_one_mod7_beta_zero_cases':bc,'frobenius_aggregate':ag,
         'nonzero_upper_inertia_allowed':True,'all_candidates_excluded':False}

def prime(q):return q>=2 and all(q%d for d in range(2,int(q**.5)+1))
def residue_data(q,integers):
 assert prime(q) and pow(5,(q-1)//2,q)==q-1
 F=Quadratic(q,1,1);e=(q*q-1)//7
 for a in range(q):
  z=F.power((a,1),e)
  if z!=(1,0):break
 lookup={F.power(z,i):i for i in range(7)}
 def ell(v):return lookup[F.power(v,e)]
 row=[ell(v) for v in [(0,1),(2,0),(3,0),(q-1,2),(7,0)]]
 logs={str(n):ell((n%q,0)) for n in integers if n%q}
 return {'q':q,'generator_offset':a,'zeta':list(z),'unit_logs':row,'rational_logs':logs}

def ray():
 primes=sorted(set(sum(SUPPORTS.values(),[])));neg=[q for q in primes if q%7==6]
 data={q:residue_data(q,neg) for q in primes};out={}
 for label,S in SUPPORTS.items():
  M=[[data[q]['unit_logs'][i] for q in S] for i in range(5)]
  assert M[0]==[0]*9 and M[2]==M[3]
  R=M+[[(0 if q==ell else data[q]['rational_logs'][str(ell)]) for q in S] for ell in S if ell%7==6]
  kp=kernel(M);kr=kernel(R);rank=len(rref(R)[1])
  minus=[i for i,q in enumerate(S) if q%7==6];plus=[i for i,q in enumerate(S) if q%7==1]
  assert len(rref(M)[1])==3
  assert all(row[i]==0 for row in R for i in minus)
  nplus=len(plus)-len(rref([[row[i] for i in plus] for row in R])[1]);nminus=len(minus)
  assert nplus+nminus==len(kr)
  out[label]={'support':S,'fixed_rows':M,'extra_frobenius_primes':[q for q in S if q%7==6],
              'augmented_rows':R,'fixed_rank':3,'augmented_rank':rank,'kernel_basis':kr,
              'plus_dimension':nplus,'minus_dimension':nminus,'semilinear_difference_dimension_bound':len(kr),
              'affine_count_bound_over_k_if_nonempty':49**len(kr),
              'common_semilinear_frame_count_bound_if_nonempty':7**len(kr)}
 assert [out[x]['augmented_rank'] for x in 'ABCD']==[6,6,5,6]
 return {'residue_data':[data[q] for q in primes],'patterns':out,
         'common_fixed_split_difference_dimension_over_k':6,
         'not_an_absolute_affine_solution':True,'patterns_eliminated':0}

def local_control():
 q=5167;A=pow(75,-1,q);C=q
 assert prime(q) and q%5 in (2,3) and q%7==1
 F=Quadratic(q,1,1);e=(q*q-1)//7
 assert all(F.power(x,e)==(1,0) for x in [(0,1),(3,0),(5,0),(75*A%q,0)])
 B=pow((-A**3)%q,pow(5,-1,q-1),q);res=B
 # digit lifting; independent uses Newton below
 mod=q
 for _ in range(7):
  d=(-(res**5+A**3-C**7)//mod)*pow(5*pow(res,4,q),-1,q)%q
  res+=mod*d;mod*=q
 assert (res**5+A**3-C**7)%mod==0
 return {'prime':q,'A':A,'C':C,'B_mod_q':B,'B_mod_q8':str(res),
         'modulus_power':8,'node_thickness':7,'monodromy_content':1,
         'local_frey_only':True,'ordinary_integer_B_not_claimed':True}

def main():
 result={'version':'7.9.0','status':'PASS','nilpotence_and_support':algebra(),
         'auxiliary_toric':auxiliary(),'restricted_p_tangent':ray(),'local_positive_control':local_control()}
 target=ROOT/'work79/verification/primary79.json';target.parent.mkdir(parents=True,exist_ok=True)
 target.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
 print(json.dumps(result,sort_keys=True))
if __name__=='__main__':main()
