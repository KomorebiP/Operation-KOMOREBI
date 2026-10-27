#!/usr/bin/env python3
"""Deterministic rational controls for inexact discrepancy certificates.

Known Euclidean matrices, dimensions 0..4, with exact residual and norm-square
comparisons. Finite controls do not prove convergence or verify Python itself.
"""
from __future__ import annotations
import copy
import json
import math
import random
from fractions import Fraction as Q
from pathlib import Path
from observable_model import Matrix
from hilbert_certificate import add, scale, transpose, norm_sq, inverse
from tikhonov_certificate import construct
from discrepancy_certificate import select
from inexact_discrepancy_certificate import validate, run_document

ROOT=Path(__file__).resolve().parents[1]
COUNT=0; REJECTED=0; SYSTEMS=0; POSITIVE=0; SMALL=0; COMPARES=0
rng=random.Random(20260914)


def check(condition: bool, message: str) -> None:
    global COUNT
    COUNT+=1
    if not condition: raise AssertionError(message)


def reject(thunk, message: str) -> None:
    global REJECTED
    try: thunk()
    except (ValueError, TypeError, KeyError, ArithmeticError): REJECTED+=1
    else: raise AssertionError('Accepted invalid control: '+message)


def sqrt_enclosure(q: Q, tol: Q) -> tuple[Q,Q]:
    """Exact dyadic enclosure. Used to simulate measured residual inputs."""
    assert q>=0 and tol>0
    s=1
    for _ in range(128):
        k=math.isqrt(q.numerator*s*s//q.denominator)
        lo=Q(k,s); hi=lo if lo*lo==q else Q(k+1,s)
        if hi-lo<=tol: return lo,hi
        s*=2
    raise RuntimeError('Test square-root enclosure resource limit.')


def mat(n:int,d:int)->Matrix:
    return Matrix(tuple(tuple(Q(rng.randint(-3,3)) for _ in range(d)) for _ in range(n)),d)


def vec(d:int, lo:int=-3, hi:int=3)->Matrix:
    return Matrix(tuple((Q(rng.randint(lo,hi)),) for _ in range(d)),1)


def l1(x:Matrix)->Q:
    return sum((abs(r[0]) for r in x.rows),Q(0))


for n in range(5):
  for d in range(5):
    for rep in range(3):
      a=mat(n,d);g=vec(d);eta=Q(1,rep+2);tau=Q(4)
      e=Matrix(tuple(((eta/4 if j==0 else Q(0)),) for j in range(n)),1)
      v=add(a@g,e);kappa=eta/16;xi=eta/16;omega=eta/16
      check(norm_sq(e)<=eta**2,'valid external noise test')
      selected=select(a,v,eta,Q(2),Q(5,2),max_steps=128)
      SYSTEMS+=1
      if selected['branch']=='small_data':
        SMALL+=1
        x=Matrix(tuple((kappa/(d+1),) for _ in range(d)),1)
        low,high=sqrt_enclosure(norm_sq(v),omega)
        measured=(low+high)/2
        out=validate(a,v,x,eta,tau,kappa,measured,omega)
        check(out['branch']=='small_data','small branch')
        check(norm_sq(x)<=kappa**2,'small output source error')
        check(norm_sq(v)<=(tau*eta)**2,'true small norm')
        if d:
          wrong=Matrix(tuple((Q(1),) for _ in range(d)),1)
          reject(lambda:validate(a,v,wrong,eta,tau,kappa,measured,omega),'bad approximate zero')
        reject(lambda:validate(a,v,x,eta,tau,kappa,measured+10,omega),'false small measurement')
        continue
      POSITIVE+=1
      lam=selected['lambda'];star=selected['source']
      normal=add(transpose(a)@a,scale(Matrix.eye(d),lam))
      direction=vec(d)
      if direction==Matrix.zero(d,1): direction=Matrix(tuple((Q(1),) for _ in range(d)),1)
      t=Q(1)
      for _ in range(128):
        perturb=scale(direction,t);x=add(star,perturb)
        r=add(normal@x,transpose(a)@v,Q(-1));rho=l1(r)
        if rho**2<=(lam*kappa)**2 and rho**2<=4*lam*xi**2:break
        t/=2
      else:raise RuntimeError('Test perturbation resource limit.')
      d2=norm_sq(add(a@x,v,Q(-1)));low,high=sqrt_enclosure(d2,omega)
      measured=(low+high)/2
      out=validate(a,v,x,eta,tau,kappa,measured,omega,lam=lam,rho=rho,xi=xi)
      check(out['branch']=='positive_parameter','positive branch')
      check(norm_sq(r)>0,'genuinely inexact source')
      check(norm_sq(add(x,star,Q(-1)))<=kappa**2,'actual source correction')
      check(norm_sq(a@add(x,star,Q(-1)))<=xi**2,'actual image correction')
      check(norm_sq(add(x,star,Q(-1)))<=norm_sq(r)/lam**2,'scaled source correction')
      check(norm_sq(a@add(x,star,Q(-1)))<=norm_sq(r)/(4*lam),'sharp image correction')
      check(eta**2<=norm_sq(add(a@star,v,Q(-1)))<=(tau*eta)**2,'exact solution band')
      check(normal@add(x,star,Q(-1))==r,'normal correction identity')
      c=construct(a,lam)
      check(c['recovery']@v==star,'exact comparison regularizer')
      check(c['inverse']@r==add(x,star,Q(-1)),'inverse correction identity')
      # Measured normal residual is zero with a certified enclosure of the true residual.
      nm={'vector':[0]*d,'error_bound':str(rho),'norm_bound':'0'}
      valid2=validate(a,v,x,eta,tau,kappa,measured,omega,lam=lam,rho=rho,xi=xi,normal_measurement=nm)
      check(valid2['normal_residual_squared']==norm_sq(r),'uncertain normal envelope')
      for field in ('rho','xi','kappa'):
        kw={'lam':lam,'rho':rho,'xi':xi}
        kp=kappa
        if field=='kappa':kp=Q(0)
        else:kw[field]=Q(0)
        reject(lambda kp=kp,kw=kw:validate(a,v,x,eta,tau,kp,measured,omega,**kw),'zero '+field)
      reject(lambda:validate(a,v,x,eta,tau,kappa,measured+10,omega,lam=lam,rho=rho,xi=xi),'measurement lies')
      bad_nm={'vector':[0]*d,'error_bound':'0','norm_bound':'0'}
      reject(lambda:validate(a,v,x,eta,tau,kappa,measured,omega,lam=lam,rho=rho,xi=xi,normal_measurement=bad_nm),'false normal measurement')
      if COMPARES<12 and n and d:
        import sympy as sp
        aa=sp.Matrix([[sp.Rational(q.numerator,q.denominator) for q in row] for row in a.rows])
        vv=sp.Matrix([sp.Rational(row[0].numerator,row[0].denominator) for row in v.rows])
        zz=(aa.T*aa+sp.Rational(lam.numerator,lam.denominator)*sp.eye(d)).inv()*aa.T*vv
        check(all(Q(int(zz[j].p),int(zz[j].q))==star.rows[j][0] for j in range(d)),'SymPy inverse cross-check')
        COMPARES+=1

# Scalar sharpness, including nullspace directions: no floating square roots.
for lam in (Q(1,16),Q(1,4),Q(1),Q(4)):
  for x0 in (Q(-2),Q(0),Q(3,2)):
    a=Matrix(((Q(0),),),1);x=Matrix(((x0,),),1);r=scale(x,lam)
    check(norm_sq(x)==norm_sq(r)/lam**2,'sharp source zero operator')
for v0 in (Q(-2),Q(0),Q(4)):
  for x0 in (Q(-1),Q(0),Q(201,100)):
    z= x0-v0/2;r=2*x0-v0
    check(z*z==r*r/4,'sharp image identity operator')

# The squared enclosure agrees with the direct scalar absolute-value test.
ENCLOSURES=0
for d0 in (Q(0),Q(1,3),Q(1),Q(3)):
 for m0 in (Q(0),Q(1,4),Q(1),Q(4)):
  for w0 in (Q(0),Q(1,10),Q(1),Q(5)):
   direct=abs(m0-d0)<=w0
   squared=max(Q(0),m0-w0)**2<=d0*d0<=(m0+w0)**2
   check(direct==squared,'squared measurement enclosure');ENCLOSURES+=1

# Counterexamples: raw normal residuals and apparent fitting bands alone are inadequate.
for k in (2,4,8,16,32):
 s=Q(1,k);a=Matrix(((Q(0),),),1);v=Matrix(((s,),),1);x=Matrix(((Q(1),),),1)
 check(norm_sq(scale(x,s))==s*s,'small raw residual')
 check(norm_sq(add(a@x,v,Q(-1)))==s*s,'apparent discrepancy band')
 check(norm_sq(x)==1,'persistent source error')
 reject(lambda:validate(a,v,x,s,Q(2),s,s,Q(0),lam=s,rho=s,xi=s),'unscaled source tolerance')

# Complete CLI contract and deliberate malformed/understated inputs.
doc=json.loads((ROOT/'examples/inexact_discrepancy_input.json').read_text())
out=run_document(doc)
check(out['certificate']['normal_residual_squared']=='1/2500','example normal norm')
check(out['certificate']['sharp_image_bound_squared']=='1/10000','example image bound')
check(json.loads(json.dumps(out))==out,'recursive rational JSON roundtrip')
mutations={
 'lambda':[0,-1,0.1,True,'1/0'],
 'noise_allowance':[0,-1,0.1,True],
 'upper_multiplier':[1,0,-1],
 'source_tolerance':[0,-1],
 'normal_envelope':[0,-1],
 'image_tolerance':[0,-1],
 'measurement_error':[-1,0],
 'measured_residual':[-1,0,100],
 'schema_version':[True,2],
 'coefficient_domain':['R'],
 'candidate_source':[[1],[True],[]],
 'global_dimension':[-1,17,True],
 'local_dimension':[-1,17,True],
}
for key,values in mutations.items():
 for value in values:
  bad=copy.deepcopy(doc);bad[key]=value
  reject(lambda bad=bad:run_document(bad),'malformed '+key)
bad=copy.deepcopy(doc);bad['unknown']=1
reject(lambda:run_document(bad),'unknown field')
bad=copy.deepcopy(doc);bad['normal_measurement']['error_bound']='0'
reject(lambda:run_document(bad),'incorrect normal error envelope')

report={'passed':True,'seed':20260914,'assertions':COUNT,'systems':SYSTEMS,
 'positive_parameter_cases':POSITIVE,'small_data_cases':SMALL,'rejected_controls':REJECTED,
 'sympy_exact_inverse_comparisons':COMPARES,'squared_enclosure_cases':ENCLOSURES,
 'dimensions':'source/target 0..4','noise_allowances':['1/2','1/3','1/4'],
 'parameter_source':'inherited exact discrepancy selector, not true source',
 'trust_boundary':'Finite rational tests, not universal limit proofs or formally verified Python. Exact comparisons reuse matrix helpers; SymPy comparisons use a separate exact inverse.'}
print(json.dumps(report,indent=2))
(ROOT/'examples/inexact_discrepancy_test_summary.json').write_text(json.dumps(report,indent=2)+'\n')
