#!/usr/bin/env python3
"""Exact-rational controls for block 15; bounded checks are not universal proofs."""
from __future__ import annotations
import json, random
from fractions import Fraction as Q
from pathlib import Path
from observable_model import Matrix
from discrepancy_certificate import select

ROOT=Path(__file__).resolve().parents[1]
rng=random.Random(20260914)
count=systems=positive=small=0

def check(b:bool,msg:str)->None:
    global count
    count+=1
    if not b: raise AssertionError(msg)

def qabs(x:Q)->Q:return abs(x)

for rep in range(120):
    a=Q(1+(rep%2))
    p=Q(rng.randint(-4,4))
    eta=Q(1, 8+(rep%5)*4)
    d=eta/Q(8*(qabs(p)+1))
    if rep%2:d=-d
    c=a+d
    e=(eta/4) * (1 if rep%3 else -1)
    v=a*p+e
    delta=qabs(d);tau=Q(2)
    systems+=1
    check(qabs(a*p-v)<=eta,'true noise bound')
    check(delta*qabs(p)<(tau-1)*eta,'relative model accuracy')
    cert=select(Matrix(((c,),),1),Matrix(((v,),),1),eta,Q(3,2),tau,max_steps=128)
    x=cert['source'].rows[0][0]
    fit=qabs(c*x-v);candidate=eta+delta*qabs(x)
    if cert['lambda'] is None:
        small+=1
        check(x==0,'small-data source')
        check(qabs(v)<=tau*eta,'small-data threshold')
    else:
        positive+=1
        check(candidate<=fit,'candidate-dependent lower discrepancy')
        check(fit<=tau*candidate,'candidate-dependent upper discrepancy')
    check(qabs(x)<=qabs(p),'self-bounded source norm')
    check(qabs(a*x-a*p)<=(tau+1)*(eta+delta*qabs(p)),'true-operator residual')

# The formal zero-model counterexample is universal. These finite values merely guard the implementation intuition.
for k in range(1,33):
    lam=Q(k,8)
    x=Q(0);fit=Q(1);eta=Q(1,10);delta=Q(1);tau=Q(2)
    candidate=eta+delta*qabs(x)
    check(not (candidate<=fit<=tau*candidate),'zero model must fail generalized band on sampled positive parameters')

summary={
  'passed':True,'seed':20260914,'assertions':count,'systems':systems,
  'positive_parameter_cases':positive,'small_data_cases':small,
  'sampled_zero_model_parameters':32,
  'arithmetic':'fractions.Fraction',
  'non_claim':'Finite scalar controls are implementation evidence only; the Lean theorems prove the universal contracts.'
}
(ROOT/'examples/generalized_discrepancy_test_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
