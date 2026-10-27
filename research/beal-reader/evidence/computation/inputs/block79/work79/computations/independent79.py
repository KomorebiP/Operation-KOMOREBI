#!/usr/bin/env python3
"""Separate implementation: coefficient phi basis; residue sqrt(5) basis;
explicit matrices for nilpotence and conjugation. Imports no primary code."""
import json,itertools
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SSETS={
'A':[307,337,547,673,743,797,883,1483,1933],
'B':[197,307,337,547,673,797,883,1483,1933],
'C':[197,307,337,547,673,743,883,1483,1933],
'D':[197,307,337,547,743,797,883,1483,1933]}
class Ring:
 def __init__(self,m,two=False):self.m=m;self.two=two
 def add(self,x,y):return ((x[0]+y[0])%self.m,(x[1]+y[1])%self.m)
 def neg(self,x):return (-x[0]%self.m,-x[1]%self.m)
 def sub(self,x,y):return self.add(x,self.neg(y))
 def mul(self,x,y):
  a,b=x;c,d=y
  if self.two:return ((a*c+5*b*d)%self.m,(a*d+b*c)%self.m)
  return ((a*c+b*d)%self.m,(a*d+b*c+b*d)%self.m)
 def num(self,v):return (v%self.m,0)
 def sc(self,v,x):return self.mul(self.num(v),x)
 def power(self,x,n):
  # Left-to-right binary product, not the primary right-to-left loop.
  r=(1,0)
  for bit in bin(n)[2:]:
   r=self.mul(r,r)
   if bit=='1':r=self.mul(r,x)
  return r
 def inv(self,x):
  a,b=x
  n=(a*a-5*b*b) if self.two else (a*a+a*b-b*b)
  inv=pow(n%self.m,-1,self.m)
  return ((a if self.two else a+b)*inv%self.m,-b*inv%self.m)
 def from_w(self,x):return ((x[0]-x[1])%self.m,2*x[1]%self.m)
 def to_w(self,x):
  b=x[1]*pow(2,-1,self.m)%self.m
  return ((x[0]+b)%self.m,b)
def matmul(R,A,B):
 out=[]
 for i in range(2):
  for j in range(2):
   s=(0,0)
   for k in range(2):s=R.add(s,R.mul(A[i*2+k],B[k*2+j]))
   out.append(s)
 return tuple(out)
def mscale(R,v,A):return tuple(R.sc(v,a) for a in A)
def canon(R,x):
 a,b=R.to_w(x);return a+7*b

def nilpotence_support():
 R=Ring(7);E=[(a,b) for a in range(7) for b in range(7)];Z=(0,0)
 nil=lo=0
 for p,z,c in itertools.product(E,repeat=3):
  M=(p,z,c,R.neg(p))
  if matmul(R,M,M)==(Z,)*4:
   nil+=1
   if c==Z:assert p==Z;lo+=1
 count=bad=total=0
 for h in range(7):
  for c in E:
   if c==Z:continue
   for b in E:
    for theta in E:
     # Build rank-one nilpotent and Frobenius projector, then extract entries.
     pt=R.mul(c,theta)
     M=(pt,R.neg(R.mul(pt,theta)),c,R.neg(pt))
     A=(R.mul(theta,b),R.mul(theta,R.sub(R.num(h),R.mul(theta,b))),b,R.sub(R.num(h),R.mul(theta,b)))
     pf=R.sub(A[0],R.num(h));qt=M[1];qf=A[1]
     assert matmul(R,M,M)==(Z,)*4
     assert R.mul(c,qt)==R.neg(R.mul(M[0],M[0]))
     assert R.mul(c,qf)==R.neg(R.mul(M[0],pf))
     assert R.sub(R.mul(c,pf),R.mul(b,M[0]))==R.sc(-h,c)
     bad+=R.mul(c,qt)!=R.mul(pt,pt)
     fq=R.add(qf,R.sc(3,qt));fp=R.add(pf,R.sc(3,pt))
     assert R.add(R.mul(c,fq),R.mul(pt,fp))==Z
     total=(total+canon(R,pt)+49*canon(R,pf)+2401*canon(R,qt)+117649*canon(R,qf))%(2**64)
     count+=1
 return {'traceless_matrices':49**3,'nilpotent_matrices':nil,'nilpotents_with_lower_zero':lo,
 'support_packets':count,'quadratic_wrong_sign_rejected':bad,'packet_aggregate':total}

def aux():
 R=Ring(343);one=(1,0);zero=(0,0);Qlist=[169,29,31,9409,38809,779689,26697889]
 V=[(a,b) for b in range(7) for a in range(7)];cnt=good=agg=0
 for Q in Qlist:
  for yy,rr,uu in itertools.product(V,V,[(1,0),(0,1)]):
   y,r,u=map(R.from_w,(yy,rr,uu))
   P=(one,zero,R.sc(7,y),one);Pinv=(one,zero,R.sc(-7,y),one)
   N=matmul(R,matmul(R,P,(zero,R.sc(7,u),zero,zero)),Pinv)
   F=matmul(R,matmul(R,P,(R.num(Q),r,zero,one)),Pinv)
   assert matmul(R,N,N)==(zero,)*4
   assert matmul(R,F,N)==mscale(R,Q,N) and matmul(R,N,F)==N
   assert R.sub(R.mul(F[0],F[3]),R.mul(F[1],F[2]))==R.num(Q)
   nw=[R.to_w(x) for x in N];fw=[R.to_w(x) for x in F]
   assert nw[2]==zero and all(a%49==0 for i in [0,3] for a in nw[i])
   beta=tuple((v//7)*pow(Q,-1,7)%7 for v in fw[2])
   assert beta==tuple(v*(Q-1)*pow(Q,-1,7)%7 for v in yy)
   if Q%7==1:assert beta==zero;good+=1
   agg=(agg+sum((i+1)*(x[0]+343*x[1]) for i,x in enumerate(fw)))%(2**64);cnt+=1
 return {'cases':cnt,'norms':Qlist,'norm_one_mod7_beta_zero_cases':good,'frobenius_aggregate':agg,
         'nonzero_upper_inertia_allowed':True,'all_candidates_excluded':False}

def row_reduce(mat):
 a=[list(map(lambda v:v%7,r)) for r in mat];used=[];line=0
 for column in range(len(a[0])):
  candidates=[i for i in range(line,len(a)) if a[i][column]]
  if not candidates:continue
  i=candidates[-1];a[line],a[i]=a[i],a[line]
  a[line]=[(v*pow(a[line][column],5,7))%7 for v in a[line]]
  for k in list(range(line))+list(range(line+1,len(a))):
   fac=a[k][column];a[k]=[(a[k][j]-fac*a[line][j])%7 for j in range(len(a[0]))]
  used.append(column);line+=1
  if line==len(a):break
 return a,used

def ker(mat):
 rr,piv=row_reduce(mat);ans=[]
 for j in range(len(mat[0])):
  if j in piv:continue
  v=[0]*len(mat[0]);v[j]=1
  for i,c in enumerate(piv):v[c]=(-rr[i][j])%7
  assert all(sum(x*y for x,y in zip(row,v))%7==0 for row in mat)
  ans.append(v)
 return ans

def det_int(A):
 if len(A)==0:return 1
 # Exact permutation expansion is different from row reduction.
 total=0
 for perm in itertools.permutations(range(len(A))):
  inv=sum(perm[i]>perm[j] for i in range(len(A)) for j in range(i+1,len(A)))
  term=(-1)**inv
  for i,j in enumerate(perm):term*=A[i][j]
  total+=term
 return total

def cert_rank(M,rank):
 if not rank:return 0
 _,cols=row_reduce(M)
 # Pick independent original rows through the transpose.
 _,rows=row_reduce([list(r) for r in zip(*M)])
 D=det_int([[M[i][j] for j in cols[:rank]] for i in rows[:rank]])
 assert D%7
 assert len(ker(M))==len(M[0])-rank
 return D

def res(q,integers):
 assert all(q%d for d in range(2,__import__('math').isqrt(q)+1))
 R=Ring(q,True);inv2=pow(2,-1,q);phi=(inv2,inv2);e=(q*q-1)//7
 for a in range(q):
  root=R.power(R.add(R.num(a),phi),e)
  if root!=(1,0):break
 def ell(x):
  s=R.power(x,e);v=(1,0)
  for i in range(7):
   if v==s:return i
   v=R.mul(v,root)
  raise AssertionError('not seventh root')
 units=[phi,R.num(2),R.num(3),(0,1),R.num(7)]
 logs=[ell(u) for u in units]
 # Convert root back to a+b phi: omega=2phi-1.
 zphi=[(root[0]-root[1])%q,2*root[1]%q]
 return {'q':q,'generator_offset':a,'zeta':zphi,'unit_logs':logs,
 'rational_logs':{str(n):ell(R.num(n)) for n in integers if n%q}}

def ray_check():
 primes=sorted(set(sum(SSETS.values(),[])));minus=[q for q in primes if q%7==6]
 ds={q:res(q,minus) for q in primes};out={}
 for label,S in SSETS.items():
  M=[[ds[q]['unit_logs'][i] for q in S] for i in range(5)]
  R=M+[[(0 if q==ell else ds[q]['rational_logs'][str(ell)]) for q in S] for ell in S if ell%7==6]
  rank=len(row_reduce(R)[1]);cert_rank(M,3);cert_rank(R,rank)
  plus=[i for i,q in enumerate(S) if q%7==1];nm=sum(q%7==6 for q in S)
  np=len(plus)-len(row_reduce([[v[i] for i in plus] for v in R])[1]);basis=ker(R)
  out[label]={'support':S,'fixed_rows':M,'extra_frobenius_primes':[q for q in S if q%7==6],
   'augmented_rows':R,'fixed_rank':3,'augmented_rank':rank,'kernel_basis':basis,
   'plus_dimension':np,'minus_dimension':nm,'semilinear_difference_dimension_bound':len(basis),
   'affine_count_bound_over_k_if_nonempty':49**len(basis),
   'common_semilinear_frame_count_bound_if_nonempty':7**len(basis)}
 assert [out[x]['augmented_rank'] for x in 'ABCD']==[6,6,5,6]
 return {'residue_data':[ds[q] for q in primes],'patterns':out,
         'common_fixed_split_difference_dimension_over_k':6,
         'not_an_absolute_affine_solution':True,'patterns_eliminated':0}

def control():
 p=5167;A=pow(75,-1,p);R=Ring(p,True);iv2=pow(2,-1,p);phi=(iv2,iv2)
 for x in [phi,R.num(3),R.num(5),R.num(75*A)]:assert R.power(x,(p*p-1)//7)==(1,0)
 b=pow(-pow(A,3,p)%p,pow(5,-1,p-1),p);x=b;precision=1
 while precision<8:
  precision=min(2*precision,8);mod=p**precision
  x=(x-(pow(x,5,mod)+A**3-p**7)*pow(5*pow(x,4,mod),-1,mod))%mod
 assert (pow(x,5,p**8)+A**3-p**7)% (p**8)==0
 return {'prime':p,'A':A,'C':p,'B_mod_q':b,'B_mod_q8':str(x),'modulus_power':8,
         'node_thickness':7,'monodromy_content':1,'local_frey_only':True,
         'ordinary_integer_B_not_claimed':True}

def main():
 result={'version':'7.9.0','status':'PASS','nilpotence_and_support':nilpotence_support(),
 'auxiliary_toric':aux(),'restricted_p_tangent':ray_check(),'local_positive_control':control()}
 p=ROOT/'work79/verification/independent79.json';p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print(json.dumps(result,sort_keys=True))
if __name__=='__main__':main()
