"""Deterministic reference audit; does not substitute finite checks for Lean proofs."""
from __future__ import annotations
import sys,json,random
from pathlib import Path
from itertools import product
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from observational_logic import (FiniteSystem, fo_sat, fo_quantifier_rank, source_sat,
    behavioral_quotient, code_formula, check_finite_code, words_through)
from standard_logic import *
SEED=2026092102
rng=random.Random(SEED); counts=Counter()
def check(k,c):
    counts[k]+=1
    if not c: raise AssertionError(k)

def formula(depth,n,na,no):
    if depth==0:
        if n==0 or no==0:return ('true',)
        def term():return (rng.randrange(n),tuple(rng.randrange(na) for _ in range(rng.randrange(4))) if na else ())
        if rng.randrange(2):return ('test',term(),rng.randrange(no),rng.randrange(3))
        return ('compare',term(),rng.randrange(no),term(),rng.randrange(no))
    k=rng.randrange(5)
    if k==0:return formula(0,n,na,no)
    if k==1:return ('not',formula(depth-1,n,na,no))
    if k==2:return ('and',formula(depth-1,n,na,no),formula(depth-1,n,na,no))
    return ('exists',formula(depth-1,n+1,na,no))

def raw(depth,na,no):
    if depth==0:return ('test',rng.randrange(no),rng.randrange(3)) if no else ('true',)
    k=rng.randrange(5 if na else 4)
    if k<=1:return raw(0,na,no)
    if k==2:return ('not',raw(depth-1,na,no))
    if k==3:return ('and',raw(depth-1,na,no),raw(depth-1,na,no))
    return ('after',rng.randrange(na),raw(depth-1,na,no))

def pair_equal(s,x,y):
    todo=[(x,y)];seen=set()
    while todo:
        a,b=todo.pop()
        if (a,b) in seen:continue
        seen.add((a,b))
        if any(o[a]!=o[b] for o in s.observations):return False
        todo += [(a0[a],a0[b]) for a0 in s.transitions]
    return True

maps=list(product(range(2),repeat=2))
systems=[FiniteSystem((a,b),(o,),2) for a,b,o in product(maps,maps,maps)]
for n in range(1,7):
    for k in range(6):
        na=no=k%3
        systems.append(FiniteSystem(tuple(tuple(rng.randrange(n) for _ in range(n)) for _ in range(na)),
            tuple(tuple(rng.randrange(3) for _ in range(n)) for _ in range(no)),n))

for s in systems:
    model=TaggedModel.from_system(s,(0,1,2))
    q,enc,h=behavioral_quotient(s); qm=TaggedModel.from_system(q,(0,1,2))
    for n in (0,1,2):
        for _ in range(24):
            f=formula(4,n,len(s.transitions),len(s.observations));t=translate(f,n)
            check('syntactic_quantifier_rank',target_rank(t)==fo_quantifier_rank(f))
            for e in product(range(s.size),repeat=n):
                et=tuple(('state',x) for x in e)
                actual=eval_formula(model,t,et)
                check('standard_satisfaction_translation',actual==fo_sat(s,f,e))
                check('standard_quotient_transport',actual==eval_formula(qm,t,tuple(('state',enc[x]) for x in e)))
    for _ in range(32):
        f=raw(5,len(s.transitions),len(s.observations));t=compile_source(f)
        check('path_compiler_qf',target_rank(t)==0)
        for x in range(s.size):
            check('path_compiler_truth',eval_formula(model,t,(('state',x),))==source_sat(s,f,x))
    tests=[(w,j) for w in words_through(len(s.transitions),h) for j in range(len(s.observations))]
    check('local_code_certificate',check_finite_code(s,tests))
    phi=guarded_code(tests)
    check('code_formula_qf',target_rank(phi)==0)
    for x,y in product(model.universe(),repeat=2):
        expected=x[0]=='state' and y[0]=='state' and pair_equal(s,x[1],y[1])
        check('guarded_definition_all_tags',eval_formula(model,phi,(x,y))==expected)

# Reify the exact counterexamples from the Lean boundary module.
s=FiniteSystem(((0,),),((0,),),1);m=TaggedModel.from_system(s,(0,1))
f=('exists',('test',(0,()),0,1))
wrong=exists(('eq',('observe',0,('bound',0)),('constant',1)))
check('unguarded_spurious_value_witness',eval_formula(m,wrong,()) and not eval_formula(m,translate(f,0),()))
t=FiniteSystem(((0,1),),((0,1),),2);tm=TaggedModel.from_system(t,(0,1))
check('nonsurjective_reflection_fails',not eval_formula(m,translate(f,0),()) and eval_formula(tm,translate(f,0),()))
nested=('exists',('and',('test',(0,()),0,0),('exists',('and',('test',(0,()),0,1),('test',(1,()),0,0)))))
check('nested_binders_correct',eval_formula(tm,translate(nested,0),()))
def clobber(t):
    if isinstance(t,tuple):
        if len(t)==2 and t[0]=='bound':return ('bound',0)
        return tuple(clobber(x) for x in t)
    return t
check('binder_mutation_rejected',not eval_formula(tm,clobber(translate(nested,0)),()))
s=FiniteSystem(((1,1,2),(0,2,2)),((0,0,1),),3);m=TaggedModel.from_system(s,(0,1))
f=('test',(0,(0,1)),0,1);bad=('test',(0,(1,0)),0,1)
check('word_reversal_rejected',eval_formula(m,translate(f,1),(('state',0),)) and not eval_formula(m,translate(bad,1),(('state',0),)))
s=FiniteSystem(((0,0),),((0,0),),2);m=TaggedModel.from_system(s,(0,))
fixed=('eq',('action',0,('free',0)),('free',0))
check('full_state_equality_failure',pair_equal(s,0,1) and eval_formula(m,fixed,(('state',0),)) and not eval_formula(m,fixed,(('state',1),)))
empty=TaggedModel(((),),((),),0,(0,1))
check('empty_state_sort_guarded',not eval_formula(empty,translate(('exists',('true',)),0),()))
check('empty_state_sort_unguarded',eval_formula(empty,exists(TOP),()))
check('existential_retained_not_QE',target_rank(translate(('exists',('true',)),0))==1)
check('state_value_tags_disjoint',('state',0)!=('value',0))

for bad,n in [(('state_equal',0,1),2),(('test',(2,()),0,0),2),(('exists',('test',(1,()),0,0)),0),(('true',),-1)]:
    try: translate(bad,n)
    except ValueError: check('invalid_source_rejected',True)
    else: raise AssertionError('Invalid source accepted')
for bad in [('free',9),('bound',0),('constant',7),('action',8,('free',0)),('observe',9,('free',0))]:
    try:eval_term(m,bad,(('state',0),),())
    except ValueError:check('invalid_target_or_signature_rejected',True)
    else:raise AssertionError('Invalid target accepted')
result={'status':'PASS','seed':SEED,'systems':len(systems),'exhaustive_two_state_systems':64,
    'additional_seeded_systems':36,'counts':dict(sorted(counts.items())),'total_checks':sum(counts.values()),
    'bounds':{'free_variables':[0,1,2],'fo_formulas_per_arity':24,'fo_sample_depth':4,'path_formulas_per_system':32,
      'path_sample_depth':5,'value_sort':[0,1,2],'random_state_sizes':[1,2,3,4,5,6]},
    'scope':'Exact finite reference audit, distinct from the universal Lean compiler proof; source formulas sampled.',
    'non_claims':['Python is not verified or extracted from Lean.','Not full first-order elementarity or quantifier elimination.','Not a discovery benchmark.']}
(ROOT/'results/TRANSLATION_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
