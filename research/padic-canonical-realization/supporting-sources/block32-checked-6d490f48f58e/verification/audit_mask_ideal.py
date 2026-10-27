#!/usr/bin/env python3
"""Exact actual-mask audit using independently routed polynomial transitions.
Finite evidence only, not a proof that this Python code refines compiled Lean.
"""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import sys, json, time, random, platform
sys.path.insert(0,str(Path(__file__).resolve().parent/'reference'))
from audit_support import SupportMachine, Machine, PrunedMachine, DegreePrunedMachine, ProfiledMachine, recurrence_coefficients, digit_word
from ideal_engine import IdealMachine
SEED=29302026

def audit():
 rng=random.Random(SEED);counts=Counter();cases=[];examples=[];strict=0
 def ck(kind,ok,detail=None):
  counts[kind]+=1
  if not ok: raise AssertionError((kind,detail))
 for p in (2,3,5):
  for r in (1,2,3,4):
   for a,b in [([1],[1,-1]),([1],[1,p*p]),([1,1],[1]),([1,1],[1,1]),([1+p**r,1],[1,p*p]),([1,0,1],[1,0,-1])]:
    cases.append((p,r,a,b))
 stress=[(2,4,[1],[1,4]),(2,8,[1],[1,-1]),(2,8,[1],[1,16]),(3,6,[1],[1,81])]
 cases+=stress
 for idx,(p,r,a,b) in enumerate(cases):
  full=Machine(p,r,a,b);old=DegreePrunedMachine(PrunedMachine(full));profile=ProfiledMachine(old);support=SupportMachine(profile)
  model=IdealMachine(p,r,tuple(support.initial_full),tuple(tuple(tuple(row) for row in m) for m in support.matrices))
  c=model.least_profile();ck('closure',model.closed_direct(c));ck('gcd_agreement',model.generators(c)==model.least_gcd_generators())
  ck('refines_support',all(c[i]==0 for i in range(model.n) if i not in support.support))
  ck('digit_budget_comparison',sum(c)<=r*len(support.support));strict+=sum(c)<r*len(support.support)
  # Audit every complete matrix column against direct multiply/section/route.
  for i in range(model.n):
   basis=[0]*model.n;basis[i]=1
   for d in range(p):
    polynomial=support.flatten(profile.step(support.rows(basis),d))
    ck('matrix_columns_vs_polynomials',tuple(polynomial)==model.transition_full(d,basis))
  y=tuple(rng.randrange(p**cap) for cap in c);x=model.embed(c,y)
  ck('cyclic_roundtrip',model.decode(c,x)==y)
  for d in range(p):
   yy=model.transition_cyclic(c,d,y);xx=model.embed(c,yy)
   ck('arbitrary_state_transition',xx==tuple(support.flatten(profile.step(support.rows(x),d))))
   ck('cyclic_output_embedding',profile.output(support.rows(xx))==support.output([xx[i] for i in support.support]))
  oracle=recurrence_coefficients(p,p**r,a,b,32)
  for n,want in enumerate(oracle):
   yy=model.decode(c,model.initial)
   for d in digit_word(p,n): yy=model.transition_cyclic(c,d,yy)
   xx=model.embed(c,yy);got=profile.output(support.rows(xx))
   ck('canonical_coefficients_vs_recurrence',got==want,(idx,p,r,a,b,n))
   ck('coefficients_vs_support_machine',got==support.coefficient(n))
  if idx>=len(cases)-len(stress):
   examples.append({'p':p,'r':r,'A':a,'B':b,'profile_slots':model.n,'support_slots':len(support.support),'support_p_adic_digits':r*len(support.support),'ideal_p_adic_digits':sum(c),'positive_capacity_coordinates':sum(v>0 for v in c),'capacities':list(c),'first16':oracle[:16]})
 return {'status':'PASS','mask_case_executions':len(cases),'distinct_mask_cases':len(set((p,r,tuple(a),tuple(b)) for p,r,a,b in cases)),'strict_p_adic_digit_reductions':strict,'assertions':sum(counts.values()),'counts':dict(counts),'examples':examples,'seed':SEED,'python':platform.python_version(),'failures':[], 'non_claims':['Bounded comparisons are not universal proof','No verified Python-to-Lean executable refinement','No minimal correlated submodule or minimum automaton claim','P-adic digit budgets describe ambient cardinality, not runtime memory usage']}
if __name__=='__main__':
 t=time.monotonic();out=Path(__file__).resolve().parents[1]/'results_current/mask_ideal_audit_result.json'
 result=audit();result['seconds']=time.monotonic()-t;out.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2))
