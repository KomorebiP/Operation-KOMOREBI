#!/usr/bin/env python3
"""Finite exact-rational controls for block 16; not a proof of the Lean theorems."""
from __future__ import annotations
import copy,json,random
from fractions import Fraction as Q
from pathlib import Path
from observable_model import Matrix
from calibration_certificate import add,scale,l1,run_document
ROOT=Path(__file__).resolve().parents[1];rng=random.Random(20260914)
checks=rejects=systems=approx=redundant=0

def check(b:bool,msg:str)->None:
 global checks
 checks+=1
 if not b: raise AssertionError(msg)
def reject(f,msg:str)->None:
 global rejects
 try:f()
 except (ValueError,TypeError,KeyError,ArithmeticError):rejects+=1
 else:raise AssertionError('accepted invalid '+msg)
def mat(m,n,den=8):
 return Matrix(tuple(tuple(Q(rng.randint(-3,3),den) for _ in range(n)) for _ in range(m)),n)
def hcat(a,b):
 if a.nrows!=b.nrows:raise ValueError
 return Matrix(tuple(tuple(ra)+tuple(rb) for ra,rb in zip(a.rows,b.rows)),a.ncols+b.ncols)
def vcat(a,b):
 if a.ncols!=b.ncols:raise ValueError
 return Matrix(tuple(a.rows)+tuple(b.rows),a.ncols)

for g in range(1,4):
 for extra in range(3):
  k=g+extra;m=1+(g+extra)%3
  for rep in range(8):
   B=mat(g,extra) if extra else Matrix.zero(g,0)
   U=hcat(Matrix.eye(g),B)
   R=vcat(Matrix.eye(g),Matrix.zero(extra,g))
   if rep%2:
    q=Q(4*g-1,4*g)
    R=scale(R,q);approx+=1
   else: redundant+=int(extra>0)
   A=mat(m,g);C=add(A,mat(m,g,64))
   E=mat(m,k,128);Y=add(A@U,E);eta=l1(E)
   doc={'schema_version':1,'coefficient_domain':'Q','source_dimension':g,'calibration_dimension':k,'data_dimension':m,
        'synthesis':U.json(),'analysis':R.json(),'measured_outputs':Y.json(),'model_operator':C.json(),
        'calibration_truth_allowance':str(eta)}
   out=run_document(doc);systems+=1
   delta=Q(out['generated_operator_error_allowance'])
   # Entrywise-l1 analogue of the Lean operator-norm theorem.
   check(l1(add(A,C,Q(-1)))<=delta,'generated calibration allowance')
   check(Q(out['reconstruction_defect_l1_bound'])<1,'defect threshold')
   check(Q(out['model_calibration_fit_l1_bound'])==l1(add(Y,C@U,Q(-1))),'fit recomputation')
   check(Q(out['analysis_l1_bound'])==l1(R),'analysis bound recomputation')

# Proper-subspace failure: calibration sees only first coordinate, model error is arbitrary in second.
U=Matrix(((Q(1),),(Q(0),)),1);R=Matrix(((Q(1),Q(0)),),2);Y=Matrix(((Q(0),),),1);C=Matrix(((Q(0),Q(100)),),2)
bad={'schema_version':1,'coefficient_domain':'Q','source_dimension':2,'calibration_dimension':1,'data_dimension':1,
     'synthesis':U.json(),'analysis':R.json(),'measured_outputs':Y.json(),'model_operator':C.json(),'calibration_truth_allowance':'0'}
reject(lambda:run_document(bad),'nonspanning calibration')
# Parser and premise controls.
good={'schema_version':1,'coefficient_domain':'Q','source_dimension':1,'calibration_dimension':1,'data_dimension':1,
      'synthesis':[['1']],'analysis':[['1']],'measured_outputs':[['1']],'model_operator':[['1']],
      'calibration_truth_allowance':'0'}
res=run_document(good);check(res['generated_operator_error_allowance']=='0','exact scalar calibration')
for key,val in [('calibration_truth_allowance','-1'),('source_dimension',17),('schema_version',2),('synthesis',[])]:
 d=copy.deepcopy(good);d[key]=val;reject(lambda d=d:run_document(d),key)
d=copy.deepcopy(good);d['true_operator']=[['1']];reject(lambda:run_document(d),'unknown true operator field')
summary={'passed':True,'seed':20260914,'assertions':checks,'systems':systems,'approximate_frame_cases':approx,
         'redundant_exact_frame_cases':redundant,'rejected_controls':rejects,
         'dimensions':'source 1..3, calibration source..source+2, data 1..3',
         'trust_boundary':'Finite exact entrywise-l1 matrix checks. The generic Lean theorem uses native operator norm; Python and parser are not formally verified.'}
(ROOT/'examples/calibration_test_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
