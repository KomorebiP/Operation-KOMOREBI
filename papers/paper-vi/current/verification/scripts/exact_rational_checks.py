#!/usr/bin/env python3
"""Independent exact rational witnesses for Paper VI. Finite examples, no universal proof."""
from fractions import Fraction as F
from itertools import product
import json

def matrix(rows): return [[F(x) for x in row] for row in rows]
def zeros(n,m=None):return [[F(0) for _ in range(n if m is None else m)] for _ in range(n)]
def eye(n):return matrix([[int(i==j) for j in range(n)] for i in range(n)])
def transpose(a):return [list(r) for r in zip(*a)]
def add(a,b):return [[x+y for x,y in zip(r,s)] for r,s in zip(a,b)]
def neg(a):return scale(a,-1)
def sub(a,b):return add(a,neg(b))
def scale(a,s):return [[s*x for x in r] for r in a]
def mul(a,b):return [[sum(x*y for x,y in zip(r,c)) for c in zip(*b)] for r in a]
def power(a,n):
 r=eye(len(a))
 for _ in range(n):r=mul(r,a)
 return r

def diag(v):return [[x if i==j else F(0) for j in range(len(v))] for i,x in enumerate(v)]
def col(v):return [[F(x)] for x in v]
def norm1(a):return max(sum(abs(x) for x in c) for c in zip(*a))
def inverse(a):
 n=len(a);a=[r+s for r,s in zip(a,eye(n))]
 for k in range(n):
  p=next(i for i in range(k,n) if a[i][k]);a[k],a[p]=a[p],a[k]
  q=a[k][k];a[k]=[x/q for x in a[k]]
  for i in range(n):
   if i!=k:
    q=a[i][k];a[i]=[x-q*y for x,y in zip(a[i],a[k])]
 return [r[n:] for r in a]

def run():
 checks=[];controls=[]
 def check(name,condition):
  if not condition:raise RuntimeError('Exact assertion failed: '+name)
  checks.append({'name':name,'status':'PASS'})
 def eq(name,a,b):check(name,a==b)
 def reject(name,condition,reason):
  if condition:raise RuntimeError('False control accepted: '+name)
  controls.append({'name':name,'status':'REJECTED','reason':reason})
 Q=matrix([[-3,1,2,0],[1,-3,0,2],[2,0,-3,1],[0,2,1,-3]])
 K=add(eye(4),scale(Q,F(1,8)));C=matrix([[1,1,0,0],[0,0,1,1]])
 Kc=matrix([[F(3,4),F(1,4)],[F(1,4),F(3,4)]])
 H=scale(matrix([[1,1,1,1],[1,-1,1,-1],[1,1,-1,-1],[1,-1,-1,1]]),F(1,2))
 Ps=[mul(col([H[i][j] for i in range(4)]),[list(zip(*H))[j]]) for j in range(4)]
 bad=[r[:] for r in K];bad[0][0]-=F(1,16);bad[2][0]+=F(1,16)
 eq('column_generator',mul([[F(1)]*4],Q),zeros(1,4))
 eq('walsh_orthogonality',mul(transpose(H),H),eye(4))
 eq('spectral_generator',mul(mul(transpose(H),Q),H),diag([0,-2,-4,-6]))
 for i,j in product(range(4),repeat=2):eq(f'projector_{i}_{j}',mul(Ps[i],Ps[j]),Ps[i] if i==j else zeros(4))
 eq('projector_resolution',sum_matrix(Ps),eye(4))
 def transfer(q):return sum_matrix([scale(P,q**j) for j,P in enumerate(Ps)])
 for q,r in product([F(0),F(1,4),F(1,2),F(1)],repeat=2):eq(f'transfer_composition_{q}_{r}',mul(transfer(q),transfer(r)),transfer(q*r))
 for n in range(7):eq(f'lumping_{n}',mul(C,power(K,n)),mul(power(Kc,n),C))
 D=sub(mul(C,bad),mul(Kc,C))
 eq('defect_norm',norm1(D),F(1,8))
 for n in range(9):
  lhs=sub(mul(C,power(bad,n)),mul(power(Kc,n),C))
  rhs=sum_matrix([mul(mul(power(Kc,n-1-j),D),power(bad,j)) for j in range(n)],2,4)
  eq(f'telescoping_{n}',lhs,rhs);check(f'linear_bound_{n}',norm1(lhs)<=n*norm1(D))
 reject('arbitrary_partition_commutes',mul(C,bad)==mul(Kc,C),'A changed aggregate transition probability gives D != 0.')
 E=matrix([[F(1,3),F(2,3),0,0],[F(1,3),F(2,3),0,0],[0,0,F(3,7),F(4,7)],[0,0,F(3,7),F(4,7)]])
 w=[F(1,10),F(2,10),F(3,10),F(4,10)];W=diag(w);E0=[w[:] for _ in range(4)]
 Ds=[E0,sub(E,E0),sub(eye(4),E)]
 eq('weighted_adjoint',mul(W,E),mul(transpose(E),W));eq('conditional_idempotent',mul(E,E),E)
 eq('coarse_after_fine',mul(E0,E),E0);eq('fine_after_coarse',mul(E,E0),E0)
 for i,j in product(range(3),repeat=2):eq(f'martingale_{i}_{j}',mul(Ds[i],Ds[j]),Ds[i] if i==j else zeros(4))
 f=col([0,3,2,5]);energies=[mul(mul(transpose(mul(D,f)),W),mul(D,f))[0][0] for D in Ds]
 eq('energy_pythagoras',sum(energies),F(13));reject('euclidean_self_adjoint',E==transpose(E),'The adjoint uses the weighted inner product.')
 def bayes(p,l):
  weighted=[x*y for x,y in zip(p,l)];z=sum(weighted)
  if z<=0:raise ValueError('Evidence must be positive')
  return [x/z for x in weighted],z
 def coarse(p):return [sum(p[:2]),sum(p[2:])]
 grid=[[F(a,4),F(b,4),F(c,4),F(4-a-b-c,4)] for a in range(5) for b in range(5-a) for c in range(5-a-b)]
 eq('simplex_grid_size',len(grid),35)
 ell=[F(4),F(1),F(1),F(1)]
 for j,p in enumerate(grid):
  P=coarse(p);eff=[sum(p[i]*ell[i] for i in I)/P[k] if P[k] else F(0) for k,I in enumerate(((0,1),(2,3)))]
  eq(f'bayes_effective_{j}',coarse(bayes(p,ell)[0]),bayes(P,eff)[0])
  eq(f'bayes_constant_{j}',coarse(bayes(p,[3,3,1,1])[0]),bayes(P,[3,1])[0])
 p=[F(1,4)]*4;post,z=bayes(p,ell);eq('posterior',post,[F(4,7),F(1,7),F(1,7),F(1,7)])
 eq('evidence',z,F(7,4))
 reject('coarse_prior_suffices',coarse(bayes([F(1,2),0,F(1,2),0],ell)[0])==coarse(bayes([0,F(1,2),F(1,2),0],ell)[0]),'Within-packet likelihood information is lost.')
 for n in [1,3,7,15]:
  h=F(1,n+1);xs=[h*(i+1) for i in range(n)]
  L=matrix([[2 if i==j else -1 if abs(i-j)==1 else 0 for j in range(n)] for i in range(n)])
  L=scale(L,1/h**2);G=[[min(x,y)-x*y for y in xs] for x in xs]
  eq(f'green_inverse_{n}',mul(L,scale(G,h)),eye(n))
  u=col([x-x**4 for x in xs]);forcing=col([12*x*x for x in xs])
  eq(f'quartic_residual_{n}',sub(mul(L,u),forcing),col([2*h*h]*n))
  err=col([-h*h*x*(1-x) for x in xs]);eq(f'quartic_solution_error_{n}',sub(mul(scale(G,h),forcing),u),err)
  eq(f'quartic_sup_error_{n}',max(abs(r[0]) for r in err),h*h/4)
 Kf=Kc;wf=[F(1),F(1,2)];terminal=col([2,1]);paths=[]
 for tail in product(range(2),repeat=3):
  path=(0,)+tail;prob=F(1);weight=F(1)
  for i,j in zip(path,path[1:]):prob*=Kf[j][i];weight*=wf[i]
  paths.append((prob,prob*weight*terminal[path[-1]][0]))
 eq('feynman_kac_mass',sum(x for x,_ in paths),F(1));eq('feynman_kac_value',sum(x for _,x in paths),mul(power(mul(diag(wf),transpose(Kf)),3),terminal)[0][0])
 eq('feynman_kac_paths',len(paths),8)
 N=matrix([[0,1],[0,0]]);J=add(scale(eye(2),-2),N)
 eq('jordan_nilpotent',mul(N,N),zeros(2))
 for zz in [F(1,2),F(1),F(3),F(7)]:
  inv=inverse(sub(scale(eye(2),zz),J));eq(f'jordan_resolvent_{zz}',inv,add(scale(eye(2),1/(zz+2)),scale(N,1/(zz+2)**2)))
 Af=matrix([[2,1,0],[0,2,0],[0,0,9]]);Ac=matrix([[2,1],[0,2]]);Cr=matrix([[1,0,0],[0,1,0]])
 eq('rectangular_intertwining',mul(Cr,Af),mul(Ac,Cr))
 for k in range(7):eq(f'rectangular_power_{k}',mul(Cr,power(Af,k)),mul(power(Ac,k),Cr))
 eq('rectangular_rational',mul(Cr,inverse(add(eye(3),Af))),mul(inverse(add(eye(2),Ac)),Cr))
 reject('values_only_calculus',inverse(add(eye(2),Ac))==scale(eye(2),F(1,3)),'The nonzero Jordan direction needs the derivative term.')
 return {'status':'PASS','arithmetic':'Exact fractions.Fraction rational arithmetic','checks_passed':len(checks),'checks':checks,'false_controls_rejected':len(controls),'controls':controls,'bounded_families':{'simplex_denominator':4,'simplex_priors':35,'lumping_horizons':[0,6],'defect_horizons':[0,8],'transfer_parameter_grid':['0','1/4','1/2','1'],'green_interior_sizes':[1,3,7,15],'feynman_kac_horizon':3,'feynman_kac_paths':8,'jordan_resolvent_parameters':['1/2','1','3','7'],'rectangular_powers':[0,6]},'non_claims':['Not a rerun of the 204 original SymPy checks.','No symbolic improper integrals, continuous parameter identities, Lean kernel proof, or universal theorem follows from these finite checks.'],'weighted_energies':[str(x) for x in energies]}

def sum_matrix(ms,n=None,m=None):
 if not ms:return zeros(n,m)
 r=zeros(len(ms[0]),len(ms[0][0]))
 for a in ms:r=add(r,a)
 return r
if __name__=='__main__':print(json.dumps(run(),indent=2))
