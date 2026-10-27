#!/usr/bin/env python3
"""Finite exact-rational checks; not proofs of strong or infinite-dimensional limits."""
from __future__ import annotations
import copy,json,math,random
from fractions import Fraction as Q
from pathlib import Path
from observable_model import Matrix
from hilbert_certificate import add,scale,transpose,norm_sq,positive_semidefinite
from reconstruction_certificate import construct as pseudoinverse
from tikhonov_certificate import construct as tikhonov
from discrepancy_certificate import select,json_value
from inexact_discrepancy_certificate import validate
from uncertain_operator_certificate import run_document
ROOT=Path(__file__).resolve().parents[1]
rng=random.Random(20260914)
count=rejects=systems=positive=small=compares=rank_changes=0

def check(b:bool,s:str)->None:
    global count
    count+=1
    if not b:raise AssertionError(s)

def reject(f,s:str)->None:
    global rejects
    try:f()
    except (ValueError,TypeError,KeyError,ArithmeticError):rejects+=1
    else:raise AssertionError('Accepted invalid control: '+s)

def mat(n:int,d:int)->Matrix:
    return Matrix(tuple(tuple(Q(rng.randint(-2,2)) for _ in range(d)) for _ in range(n)),d)

def vec(d:int)->Matrix:
    return Matrix(tuple((Q(rng.randint(-3,3)),) for _ in range(d)),1)

def l1(a:Matrix)->Q:
    return sum((abs(z) for r in a.rows for z in r),Q(0))

def enclosure(q:Q,tol:Q)->tuple[Q,Q]:
    if q<0 or tol<=0:raise ValueError('Invalid enclosure input')
    den=1
    for _ in range(128):
        k=math.isqrt(q.numerator*den*den//q.denominator)
        lo=Q(k,den);hi=lo if lo*lo==q else Q(k+1,den)
        if hi-lo<=tol:return lo,hi
        den*=2
    raise RuntimeError('Finite enclosure cap exhausted')

for n in range(5):
 for d in range(5):
  for rep in range(3):
   A=mat(n,d) if rep else Matrix.zero(n,d)
   D=scale(mat(n,d),Q(1,256));C=add(A,D)
   delta=l1(D);g=vec(d);p=pseudoinverse(A)['identifiable_projector']@g
   M=l1(p);eta=Q(1,16*(rep+1));eps=eta+delta*M;tau=Q(4)
   e=Matrix(tuple(((eta/4 if j==0 else Q(0)),) for j in range(n)),1)
   v=add(A@g,e);kappa=eps/16;xi=eps/16;omega=eps/16
   systems+=1
   rank_changes+=pseudoinverse(A)['rank']!=pseudoinverse(C)['rank']
   check(positive_semidefinite(add(scale(Matrix.eye(d),delta**2),transpose(D)@D,Q(-1))), 'whole operator allowance')
   check(norm_sq(p)<=M*M,'identifiable source bound')
   check(norm_sq(add(C@p,v,Q(-1)))<=eps*eps,'effective data noise')
   chosen=select(C,v,eps,Q(2),Q(5,2),max_steps=128)
   y=chosen['source'];lam=chosen['lambda']
   check(norm_sq(y)<=norm_sq(p),'fixed-source norm domination')
   check(norm_sq(add(A@y,A@p,Q(-1)))<=((tau+1)*eps)**2,'true operator residual')
   if lam is None:
    small+=1;x=Matrix(tuple((kappa/(d+1),) for _ in range(d)),1)
    lo,hi=enclosure(norm_sq(v),omega);m=(lo+hi)/2
    c=validate(C,v,x,eps,tau,kappa,m,omega)
   else:
    positive+=1;normal=add(transpose(C)@C,scale(Matrix.eye(d),lam))
    direction=vec(d)
    if direction==Matrix.zero(d,1):direction=Matrix(tuple((Q(1),) for _ in range(d)),1)
    step=Q(1)
    for _ in range(128):
     x=add(y,scale(direction,step));r=add(normal@x,transpose(C)@v,Q(-1));rho=l1(r)
     if rho*rho<=(lam*kappa)**2 and rho*rho<=4*lam*xi*xi:break
     step/=2
    else:raise RuntimeError('Perturbation cap exhausted')
    lo,hi=enclosure(norm_sq(add(C@x,v,Q(-1))),omega);m=(lo+hi)/2
    c=validate(C,v,x,eps,tau,kappa,m,omega,lam=lam,rho=rho,xi=xi)
    check(norm_sq(r)>0,'nonexact candidate')
    if compares<8 and n and d:
     import sympy as sp
     cc=sp.Matrix([[sp.Rational(z.numerator,z.denominator) for z in row] for row in C.rows])
     vv=sp.Matrix([sp.Rational(row[0].numerator,row[0].denominator) for row in v.rows])
     yy=(cc.T*cc+sp.Rational(lam.numerator,lam.denominator)*sp.eye(d)).inv()*cc.T*vv
     check(all(Q(int(yy[j].p),int(yy[j].q))==y.rows[j][0] for j in range(d)),'separate SymPy solve')
     compares+=1
    for bad in ('rho','xi','kappa'):
     kw={'lam':lam,'rho':rho,'xi':xi};kp=kappa
     if bad=='kappa':kp=Q(0)
     else:kw[bad]=Q(0)
     reject(lambda kw=kw,kp=kp:validate(C,v,x,eps,tau,kp,m,omega,**kw),'missing '+bad)
   check(norm_sq(add(x,y,Q(-1)))<=kappa*kappa,'companion source correction')
   check(norm_sq(x)<=(M+kappa)**2,'conditional source-norm budget')
   check(norm_sq(add(A@x,A@p,Q(-1)))<=(l1(A)*kappa+(tau+1)*eps)**2,'computed true residual')
   # Independent expansion of the true/model normal-residual difference.
   lam2=lam if lam is not None else Q(1)
   nrA=add(add(transpose(A)@A,scale(Matrix.eye(d),lam2))@x,transpose(A)@v,Q(-1))
   nrC=add(add(transpose(C)@C,scale(Matrix.eye(d),lam2))@x,transpose(C)@v,Q(-1))
   rhs=add(transpose(add(A,C,Q(-1)))@add(C@x,v,Q(-1)),transpose(A)@(add(A,C,Q(-1))@x))
   check(add(nrA,nrC,Q(-1))==rhs,'normal residual transport identity')
   check(norm_sq(add(nrA,nrC,Q(-1)))<=(delta*(l1(add(C@x,v,Q(-1)))+(l1(C)+delta)*l1(x)))**2,'available residual transport bound')
   doc={'schema_version':1,'coefficient_domain':'Q','global_dimension':d,'local_dimension':n,
     'model_operator':C.json(),'local_vector':[str(r[0]) for r in v.rows],
     'candidate_source':[str(r[0]) for r in x.rows], 'data_noise_allowance':str(eta),
     'operator_error_allowance':str(delta),'source_norm_bound':str(M),
     'upper_multiplier':str(tau),'source_tolerance':str(kappa),'branch':c['branch'],
     'measured_residual':str(m),'measurement_error':str(omega)}
   if lam is not None:doc.update({'lambda':str(lam),'normal_envelope':str(rho),'image_tolerance':str(xi)})
   out=run_document(doc)
   check(out['effective_noise_allowance']==str(eps),'wrapper effective noise')
   check(bool(out['externally_required_not_checked']),'no fabricated external validation')
   for key in ('operator_error_allowance','source_norm_bound','data_noise_allowance'):
    wrong=copy.deepcopy(doc);wrong[key]='-1'
    reject(lambda wrong=wrong:run_document(wrong),'negative uncertainty input')

# Actual Lean scalar certificate and nonzero operator error.
doc=json.loads((ROOT/'examples/uncertain_operator_input.json').read_text());result=run_document(doc)
check(result['effective_noise_allowance']=='1/2','supplied effective allowance')
check(result['computed_model_certificate']['normal_residual_squared']=='1/5625','supplied normal residual')
check(json.loads(json.dumps(result))==result,'JSON roundtrip')
mutations={'operator_error_allowance':[-1,True,0.1,'1/0'],'source_norm_bound':[-1,True,0.1],
 'data_noise_allowance':[-1,True,0.1], 'source_tolerance':[0,-1], 'image_tolerance':[0,-1],
 'normal_envelope':[0,-1], 'lambda':[0,-1], 'upper_multiplier':[1,0],
 'schema_version':[True,2], 'global_dimension':[True,-1,17], 'model_operator':[[[True]],[]]}
for key,vals in mutations.items():
 for val in vals:
  bad=copy.deepcopy(doc);bad[key]=val
  reject(lambda bad=bad:run_document(bad),'malformed '+key)
bad=copy.deepcopy(doc);bad['A']=[[1]];reject(lambda:run_document(bad),'unrecognized true-operator field')
bad=copy.deepcopy(doc);bad['operator_error_allowance']='0';bad['data_noise_allowance']='0'
reject(lambda:run_document(bad),'zero effective allowance')

# Persistent model bias: exact accepted solutions can approach the wrong source.
for k in (2,4,8,16,32):
 s=Q(1,k);lam=4*s/(1-s);C=Matrix(((Q(2),),),1);v=Matrix(((Q(1),),),1)
 y=tikhonov(C,lam)['recovery']@v
 check(y.rows[0][0]==(1-s)/2,'biased model source formula')
 check(norm_sq(add(C@y,v,Q(-1)))==s*s,'biased discrepancy exact')
 check(norm_sq(add(y,v,Q(-1)))>=Q(1,4),'true-source error persists')

summary={'passed':True,'seed':20260914,'assertions':count,'systems':systems,
 'positive_parameter_cases':positive,'small_data_cases':small,'rank_change_cases':rank_changes,
 'rejected_controls':rejects,'sympy_comparisons':compares,'dimensions':'0..4 source and target',
 'bounds':'75 finite model/noise cases, exact rational arithmetic, whole matrix PSD checks; finite controls do not prove infinite convergence.',
 'trust_boundary':'Shared rational matrix helpers plus eight separate SymPy solves. Python is tested, not formally verified. The checker never receives the unknown true operator.'}
(ROOT/'examples/operator_uncertainty_test_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
