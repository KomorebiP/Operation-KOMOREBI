"""Reproducible finite audits; universal statements are the Lean theorems."""
from __future__ import annotations
import hashlib,json,random,sys,time
from collections import Counter
from datetime import datetime,timezone
from itertools import product
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from relational_logic import (Model,evaluate,translate,target_eval,source_rank,target_rank,
 certify_transport,identity_backforth,identity_atomic)
SEED=2026092102;rng=random.Random(SEED);checks=Counter();started=datetime.now(timezone.utc).isoformat();tick=time.monotonic()
inputs=[ROOT/'relational_logic.py',Path(__file__).resolve()]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before={str(p.relative_to(ROOT)):sha(p) for p in inputs}
def ck(k,ok):
 checks[k]+=1
 if not ok:raise AssertionError(k)
def reject(k,fn):
 try:fn()
 except (ValueError,IndexError):checks[k]+=1
 else:raise AssertionError('accepted '+k)

def formula(m,n,budget=3,q=2):
 def st():return (rng.randrange(n),tuple(rng.randrange(len(m.actions)) for _ in range(rng.randrange(3))) if m.actions else ())
 def vt():
  if n and m.observations and (not m.values or rng.randrange(2)):
   s=st();return ('probe',s[0],s[1],rng.randrange(len(m.observations)))
  return ('lit',rng.randrange(m.values))
 options=['false']
 if m.values:options+=['eq','eq']
 if n and m.relations:options+=['rel','rel']
 if budget:options+=['not','and']+(['exists'] if q else [])
 tag=rng.choice(options)
 if tag=='false':return ('false',)
 if tag=='eq':return ('eq',vt(),vt())
 if tag=='rel':return ('rel',rng.randrange(len(m.relations)),st(),st())
 if tag=='not':return ('not',formula(m,n,budget-1,q))
 if tag=='and':return ('and',formula(m,n,budget-1,q),formula(m,n,budget-1,q))
 return ('exists',formula(m,n+1,budget-1,q-1))

def random_model(n):
 return Model(n,3,tuple(tuple(rng.randrange(n) for _ in range(n)) for _ in range(2)),
  (tuple(rng.randrange(3) for _ in range(n)),),
  (tuple(tuple(bool(rng.randrange(2)) for _ in range(n)) for _ in range(n)),))
fixtures=[random_model(rng.randrange(1,6)) for _ in range(24)]
fixtures += [Model(0,0,(),(),()),Model(0,2,((),),((),),((),)),
 Model(3,2,(),(),()),Model(1,1,((0,),),((0,),),(((True,),),))]
for m in fixtures:
 for _ in range(96):
  n=rng.randrange(3) if m.n else 0;f=formula(m,n);g=translate(f,n)
  ck('translation_rank',target_rank(g)==source_rank(f))
  envs=list(product(range(m.n),repeat=n))
  if len(envs)>16:envs=rng.sample(envs,6)
  for env in envs:ck('independent_satisfaction_translation',evaluate(m,f,env)==target_eval(m,g,env))

pullbacks=[]
for _ in range(16):
 base=random_model(rng.randrange(1,4));mult=rng.randrange(2,4);enc=tuple(x//mult for x in range(base.n*mult))
 src=Model(base.n*mult,base.values,
  tuple(tuple(row[x//mult]*mult+rng.randrange(mult) for x in range(base.n*mult)) for row in base.actions),
  tuple(tuple(row[x//mult] for x in range(base.n*mult)) for row in base.observations),
  tuple(tuple(tuple(mat[x//mult][y//mult] for y in range(base.n*mult)) for x in range(base.n*mult)) for mat in base.relations))
 certify_transport(src,base,enc);checks['relational_transport_contract']+=1
 for _ in range(64):
  n=rng.randrange(3);f=formula(src,n,q=2);g=translate(f,n)
  envs=list(product(range(src.n),repeat=n))
  if len(envs)>16:envs=rng.sample(envs,6)
  for env in envs:
   dst=tuple(enc[x] for x in env)
   ck('quantified_relational_transport',evaluate(src,f,env)==evaluate(base,f,dst))
   ck('standard_backend_transport',target_eval(src,g,env)==target_eval(base,g,dst))
 pullbacks.append({'source_states':src.n,'target_states':base.n})

# All 512 directed binary relations on three vertices. Identity dynamics makes
# this finite atomic diagram cover every operation word, not merely a short prefix.
queries=[('exists',('rel',0,(1,()),(0,()))),
 ('exists',('rel',0,(0,()),(1,()))),
 ('not',('exists',('not',('rel',0,(1,()),(0,()))))),
 ('exists',('and',('rel',0,(1,()),(0,())),('not',('rel',0,(0,()),(1,())))))]
for bits in range(512):
 mat=tuple(tuple(bool(bits & (1<<(3*x+y))) for y in range(3)) for x in range(3))
 m=Model(3,1,((0,1,2),),((0,0,0),),(mat,))
 for x,y in product(range(3),repeat=2):
  h=identity_backforth(m,m,1,(x,),(y,))
  # An independent extension-type-set definition of the one-step condition.
  sx={identity_atomic(m,(z,x)) for z in range(3)}
  sy={identity_atomic(m,(z,y)) for z in range(3)}
  ck('backforth_vs_extension_types',h==(identity_atomic(m,(x,))==identity_atomic(m,(y,)) and sx==sy))
  if h:
   for f in queries:ck('rank_one_backforth_preservation',evaluate(m,f,(x,))==evaluate(m,f,(y,)))
 for f in queries:
  for x in range(3):ck('all_graph_standard_translation',evaluate(m,f,(x,))==target_eval(m,translate(f,1),(x,)))
 identity_backforth.cache_clear()

mat=((False,False,True),(False,False,False),(False,False,False))
graph=Model(3,3,((0,1,2),),((0,0,0),),(mat,))
query=queries[0]
ck('same_model_atomic_agreement',identity_atomic(graph,(0,))==identity_atomic(graph,(1,)))
ck('same_model_rank_one_separation',evaluate(graph,query,(0,)) and not evaluate(graph,query,(1,)))
ck('one_step_backforth_failure',not identity_backforth(graph,graph,1,(0,),(1,)))
classes0={identity_atomic(graph,(x,)) for x in range(3)}
classes1={(identity_atomic(graph,(x,)),frozenset(identity_atomic(graph,(z,x)) for z in range(3))) for x in range(3)}
ck('one_class_at_rank_zero',len(classes0)==1);ck('three_classes_at_rank_one',len(classes1)==3)
point=Model(1,3,((0,),),((0,),),(((False,),),))
reject('invalid_quotient_relation',lambda:certify_transport(graph,point,(0,0,0)))

# A nontrivial GOOD quotient with a genuine relational predicate on the quotient.
base=Model(3,1,((0,1,2),),((0,0,0),),(mat,))
fib=Model(6,1,((1,0,3,2,5,4),),((0,0,0,0,0,0),),
 (tuple(tuple(mat[x//2][y//2] for y in range(6)) for x in range(6)),))
certify_transport(fib,base,(0,0,1,1,2,2));checks['explicit_noninjective_relational_quotient']+=1
for f in queries:
 for x in range(6):ck('explicit_relational_quotient_truth',evaluate(fib,f,(x,))==evaluate(base,f,(x//2,)))

# Mutation controls: wrong binder levels and reversed noncommuting words.
labelled=Model(3,3,((0,1,2),),((0,1,2),),(mat,))
nested=('exists',('exists',('and',('rel',0,(1,()),(0,())),('eq',('probe',0,(),0),('lit',2)))))
good=translate(nested,0)
def collapse_bound(t):
 if not isinstance(t,tuple):return t
 if t and t[0]=='bound':return ('bound',0)
 return tuple(collapse_bound(x) for x in t)
ck('nested_binder_control',evaluate(labelled,nested,()) and target_eval(labelled,good,()))
ck('wrong_binder_mutation_detected',not target_eval(labelled,collapse_bound(good),()))
noncommuting=Model(2,2,((1,0),(0,0)),((0,1),),())
a=('eq',('probe',0,(0,1),0),('lit',0));bad=('eq',('probe',0,(1,0),0),('lit',0))
ck('noncommuting_word_translation',evaluate(noncommuting,a,(0,))==target_eval(noncommuting,translate(a,1),(0,)))
ck('reversed_word_mutation_detected',evaluate(noncommuting,a,(0,))!=target_eval(noncommuting,translate(bad,1),(0,)))
reject('state_equality_not_in_source_fragment',lambda:evaluate(graph,('stateeq',(0,()),(1,())),(0,1)))
reject('out_of_scope_variable',lambda:evaluate(graph,('rel',0,(1,()),(0,())),(0,)))
reject('unknown_relation',lambda:evaluate(graph,('rel',1,(0,()),(0,())),(0,)))
reject('unknown_literal',lambda:evaluate(graph,('eq',('lit',3),('lit',0)),(0,)))
reject('malformed_matrix',lambda:Model(2,2,((0,1),),((0,1),),(((True,),),)))
reject('nonsurjective_quantified_map',lambda:certify_transport(point,graph,(1,)))
# Two values and an empty state carrier are separate: existential truth is false,
# universal truth (encoded by not-exists-not) is true.
empty=fixtures[25];f=('exists',('not',('false',)))
ck('empty_existential',not evaluate(empty,f,()) and not target_eval(empty,translate(f,0),()))
ck('empty_universal',evaluate(empty,('not',f),()) and target_eval(empty,translate(('not',f),0),()))
ck('inputs_unchanged',before=={str(p.relative_to(ROOT)):sha(p) for p in inputs})
r={'status':'PASS','seed':SEED,'started_at':started,'runtime_seconds':time.monotonic()-tick,
 'checks':dict(sorted(checks.items())),'total_check_calls':sum(checks.values()),'input_hashes':before,
 'pullbacks':pullbacks,'relational_example':{'rank0_classes':1,'rank1_classes':3,'query_truth':[True,False,False]},
 'bounds':{'random_and_degenerate_models':len(fixtures),'formulas_per_model':96,
  'pullback_pairs':16,'formulas_per_pair':64,'source_quantifier_rank_max':2,'word_length_max':2,
  'assignments_exhaustive_up_to':16,'otherwise_sample':6,'all_three_vertex_graphs':512,
  'graph_queries':len(queries),'graph_backforth_rank':1},
 'non_claims':['Reference interpreter and translator not Lean-extracted',
  'Finite computations are audits, not universal theorems','No performance or historical novelty claim',
  'The finite back-and-forth audit uses identity dynamics']}
(ROOT/'results/PYTHON_AUDIT.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
