from __future__ import annotations
import sys,json,random,time
from pathlib import Path
from itertools import product
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from observational_logic import *

SEED=2026092101
rng=random.Random(SEED)
counts=Counter()
def check(key: str, condition: bool) -> None:
    counts[key]+=1
    if not condition: raise AssertionError(key)

def raw_formula(depth: int, actions: int, observations: int) -> Formula:
    if depth==0:
        return ('test',rng.randrange(observations),rng.randrange(3)) if observations else ('true',)
    choice=rng.randrange(5 if actions else 4)
    if choice==0:return ('true',)
    if choice==1:return raw_formula(0,actions,observations)
    if choice==2:return ('not',raw_formula(depth-1,actions,observations))
    if choice==3:return ('and',raw_formula(depth-1,actions,observations),raw_formula(depth-1,actions,observations))
    return ('after',rng.randrange(actions),raw_formula(depth-1,actions,observations))

def first_order(depth: int, variables: int, actions: int, observations: int) -> Formula:
    if depth==0:
        if not variables or not observations:return ('true',)
        def term():
            return (rng.randrange(variables),tuple(rng.randrange(actions) for _ in range(rng.randrange(4))) if actions else ())
        if rng.randrange(2): return ('test',term(),rng.randrange(observations),rng.randrange(3))
        return ('compare',term(),rng.randrange(observations),term(),rng.randrange(observations))
    c=rng.randrange(5)
    if c<=1:return first_order(0,variables,actions,observations)
    if c==2:return ('not',first_order(depth-1,variables,actions,observations))
    if c==3:return ('and',first_order(depth-1,variables,actions,observations),first_order(depth-1,variables,actions,observations))
    return ('exists',first_order(depth-1,variables+1,actions,observations))

def independent_behavior_equal(s: FiniteSystem, x:int, y:int) -> bool:
    # Pair search is deliberately independent of the partition-refinement reference.
    todo=[(x,y)];seen=set()
    while todo:
        a,b=todo.pop()
        if (a,b) in seen:continue
        seen.add((a,b))
        if any(row[a]!=row[b] for row in s.observations):return False
        todo.extend((row[a],row[b]) for row in s.transitions)
    return True

systems=[]
# Exhaust every two-state system with TWO labelled actions and ONE binary observation.
maps=list(product(range(2),repeat=2))
for a,b,o in product(maps,maps,maps):
    systems.append(FiniteSystem((a,b),(o,),2))
# Additional deterministic-seeded finite systems, including null operation/observation signatures.
for n in range(1,7):
    for k in range(6):
        na=k%3;no=k%3
        systems.append(FiniteSystem(tuple(tuple(rng.randrange(n) for _ in range(n)) for _ in range(na)),
          tuple(tuple(rng.randrange(3) for _ in range(n)) for _ in range(no)),n))

for s in systems:
    q,enc,h=behavioral_quotient(s)
    check('surjectivity',set(enc)==set(range(q.size)))
    forms=[raw_formula(5,len(s.transitions),len(s.observations)) for _ in range(64)]
    for f in forms:
        nf=normalize(f)
        check('normalization_retraction',normalize(embed(nf))==nf)
        for x in range(s.size):
            check('normalization_truth',source_sat(s,f,x)==path_sat(s,nf,x))
            check('path_transport',path_sat(s,nf,x)==path_sat(q,nf,enc[x]))
    tests=[(w,j) for w in words_through(len(s.transitions),h) for j in range(len(s.observations))]
    check('finite_code_local_certificate',check_finite_code(s,tests))
    cf=code_formula(tests)
    check('finite_code_quantifier_rank',fo_quantifier_rank(cf)==0)
    for x,y in product(range(s.size),repeat=2):
        eq=independent_behavior_equal(s,x,y)
        check('quotient_vs_independent_pair_search',eq==(enc[x]==enc[y]))
        check('finite_code_formula_exact',fo_sat(s,cf,(x,y))==eq)
    for variables in (0,1,2):
        for _ in range(32):
            f=first_order(4,variables,len(s.transitions),len(s.observations))
            for env in product(range(s.size),repeat=variables):
                check('quantified_surjective_transport',fo_sat(s,f,env)==fo_sat(q,f,tuple(enc[x] for x in env)))

# Correct order of noncommuting actions: reversed paths must fail.
s=FiniteSystem(((1,1,2),(0,2,2)),((0,0,1),),3)
f=('after',0,('after',1,('test',0,1)))
check('word_order_negative_control',source_sat(s,f,0) and not path_sat(s,('atom',(1,0),0,1),0))
# Full state equality does not descend.
s=FiniteSystem(((0,0),),((0,0),),2);q,enc,_=behavioral_quotient(s)
check('state_equality_boundary',enc[0]==enc[1] and s.transitions[0][0]==0 and s.transitions[0][1]!=1)
check('full_inequality_sentence_boundary',s.size>1 and q.size==1)
# Surjectivity is necessary for quantified source-target reflection.
s=FiniteSystem(((0,),),((0,),),1);t=FiniteSystem(((0,1),),((0,1),),2)
f=('exists',('test',(0,()),0,1))
check('nonsurjective_quantifier_boundary',not fo_sat(s,f,()) and fo_sat(t,f,()))
# Quantifier rank alone does not bound operation depth.
for h in range(65):
    f=('test',(0,(0,)*h),0,1)
    check('separate_rank_and_horizon',fo_quantifier_rank(f)==0 and fo_term_horizon(f)==h)
    delayed=FiniteSystem((tuple(list(range(1,h+2))+[h+1,h+2]),),
                         (tuple([0]*(h+1)+[1,0]),),h+3)
    check('delayed_observation_prefix',all(delayed.observe(0,(0,)*n,0)==
        delayed.observe(h+2,(0,)*n,0) for n in range(h+1)))
    check('delayed_observation_next_step',delayed.observe(0,(0,)*(h+1),0)!=
        delayed.observe(h+2,(0,)*(h+1),0))
# A finite horizon cannot be used as a stable code without checking transitions.
s=FiniteSystem(((1,2,2),),((0,0,1),),3)
check('premature_code_rejected',not check_finite_code(s,[((),0)]))
# Rich observation tests are a real assumption: a constant output predicate distinguishes nothing.
separating=FiniteSystem(((0,1),),((0,1),),2)
nonseparating=FiniteSystem(((0,1),),((0,0),),2)
check('nonseparating_predicate_boundary',behavioral_quotient(separating)[0].size==2
      and behavioral_quotient(nonseparating)[0].size==1)
invalid=0
for bad in [('state_equal',0,1),('forall',('true',)),('after',0),('atom',(),0,1)]:
    try: normalize(bad)
    except ValueError:invalid+=1
check('invalid_syntax_rejection',invalid==4)
try: words_through(2,30,cap=1000)
except RuntimeError:check('resource_cap_inconclusive',True)
else:raise AssertionError('resource cap silently ignored')
result={'status':'PASS','seed':SEED,'systems':len(systems),'exhaustive_two_state_systems':64,
        'random_or_boundary_systems':36,'counts':dict(sorted(counts.items())),
        'total_checks':sum(counts.values()),'scope':'Finite executable audit, separate from universal Lean proofs.',
        'not_claimed':['general first-order equality preservation','quantifier elimination','historical novelty','verified Python extraction']}
(ROOT/'results/AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
