"""Independent finite scope checks. Universal claims are in the Lean sources."""
from __future__ import annotations
import hashlib, json, random, sys, time
from collections import Counter
from datetime import datetime, timezone
from itertools import product
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from observation_logic import (System, Term, Formula, evaluate, check_transport,
    behavioral_quotient, distinguishing_word, discover_defining_formula, holds)

SEED = 2026092101
rng = random.Random(SEED)
checks: Counter[str] = Counter()
start = time.monotonic()
started = datetime.now(timezone.utc).isoformat()
inputs = [ROOT / 'observation_logic.py', Path(__file__).resolve()]
def hashes(): return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
before = hashes()
def check(name: str, condition: bool):
    checks[name] += 1
    if not condition: raise AssertionError(name)
def reject(name: str, thunk):
    try: thunk()
    except ValueError: checks[name] += 1
    else: raise AssertionError('accepted invalid input: ' + name)

def formula(system: System, arity: int, budget: int, horizon: int, qleft: int) -> Formula:
    def term():
        if not arity or not system.observations or rng.randrange(3)==0:
            return Term.literal(rng.randrange(system.values))
        length = rng.randrange(horizon+1) if system.steps else 0
        return Term.probe(rng.randrange(arity),
                          (rng.randrange(len(system.steps)) for _ in range(length)),
                          rng.randrange(len(system.observations)))
    choice = rng.randrange(10) if budget else 0
    if choice < 4: return Formula.equal(term(),term())
    if choice < 6: return Formula.neg(formula(system,arity,budget-1,horizon,qleft))
    if choice < 8: return Formula.conj(formula(system,arity,budget-1,horizon,qleft),
                                      formula(system,arity,budget-1,horizon,qleft))
    if qleft: return Formula.exists(formula(system,arity+1,budget-1,horizon,qleft-1))
    return Formula.equal(term(),term())

def signature(system, state, horizon):
    return tuple(system.behavior(state,w,j)
                 for length in range(horizon+1)
                 for w in product(range(len(system.steps)),repeat=length)
                 for j in range(len(system.observations)))

fixtures=[]
for k in range(12):
    n=rng.randrange(1,7); a=rng.randrange(1,3); o=rng.randrange(1,3)
    fixtures.append(System(n,3,tuple(tuple(rng.randrange(n) for _ in range(n)) for _ in range(a)),
                           tuple(tuple(rng.randrange(3) for _ in range(n)) for _ in range(o)),f'random{k}'))
for k in range(12):
    n=rng.randrange(1,5); mult=rng.randrange(2,4); a=rng.randrange(1,3)
    base=tuple(tuple(rng.randrange(n) for _ in range(n)) for _ in range(a))
    obs=tuple(rng.randrange(3) for _ in range(n))
    fixtures.append(System(n*mult,3,
        tuple(tuple(base[d][x//mult]*mult+rng.randrange(mult) for x in range(n*mult)) for d in range(a)),
        (tuple(obs[x//mult] for x in range(n*mult)),),f'fibers{k}'))
fixtures += [
    System(8,2,(tuple(((s%2+s//2%2)%2)+2*(s//2%2)+4*(s//4) for s in range(8)),),
           (tuple(s%2 for s in range(8)),),'small_lean'),
    System(64,4,(tuple((s%4+s//4%4)%4+4*(s//4%4)+16*(s//16) for s in range(64)),),
           (tuple(s%4 for s in range(64)),),'large_64'),
    System(0,2,((),),((),),'empty'),
    System(3,2,(),(),'no_operations_or_observations')]
fixture_results=[]
for source in fixtures:
    target, enc=behavioral_quotient(source)
    check_transport(source,target,enc,onto=True)
    checks['quotient_local_certificate']+=1
    defining, tests=discover_defining_formula(source)
    check('compiled_formula_quantifier_free',defining.qrank==0)
    for x in range(source.n):
        for y in range(source.n):
            witness=distinguishing_word(source,x,y)
            check('bfs_vs_partition', (witness is None)==(enc[x]==enc[y]))
            check('compiled_defining_formula', evaluate(source,defining,(x,y))==(enc[x]==enc[y]))
            if witness is not None:
                w,j=witness
                f=Formula.equal(Term.probe(0,w,j),Term.literal(source.behavior(x,w,j)))
                check('distinguishing_formula_positive',evaluate(source,f,(x,)))
                check('distinguishing_formula_negative',not evaluate(source,f,(y,)))
                check('distinguishing_formula_rank_zero',f.qrank==0)
    maxq=0
    for trial in range(64):
        arity=rng.randrange(3) if source.n else 0
        horizon=rng.randrange(4)
        f=formula(source,arity,4,horizon,1 if source.n>16 else 3)
        maxq=max(maxq,f.qrank)
        f.validate(source,arity)
        if source.n**arity<=16:
            envs=list(product(range(source.n),repeat=arity))
        else:
            envs=[tuple(rng.randrange(source.n) for _ in range(arity)) for _ in range(6)]
        sigs=[signature(source,x,horizon) for x in range(source.n)]
        for env in envs:
            got=evaluate(source,f,env)
            check('quantified_quotient_preservation',got==evaluate(target,f,tuple(enc[x] for x in env)))
            tau=tuple(rng.choice([x for x in range(source.n) if sigs[x]==sigs[y]]) for y in env)
            check('bounded_depth_quantifier_congruence',got==evaluate(source,f,tau))
    fixture_results.append({'name':source.name,'states':source.n,'quotient_states':target.n,
                            'defining_tests':len(tests),'max_tested_quantifier_rank':maxq})
    holds.cache_clear()

point=System(1,2,((0,),),((0,),),'point')
visible=System(2,2,((0,1),),((0,1),),'visible')
query=Formula.exists(Formula.equal(Term.probe(0,(),0),Term.literal(1)))
check_transport(point,visible,(0,),onto=False)
reject('nonsurjective_quantifier_transport_rejected',lambda:check_transport(point,visible,(0,),onto=True))
check('existential_counterexample_source',not evaluate(point,query,(0,)))
check('existential_counterexample_target',evaluate(visible,query,(0,)))
constant=System(2,2,((0,0),),((0,0),),'constant')
check('full_equality_boundary',distinguishing_word(constant,0,1) is None and
      constant.steps[0][0]==0 and constant.steps[0][1]!=1)
for h in range(24):
    sink=h+2
    chain=System(h+3,2,(tuple(sink if x in (0,sink) else x-1 for x in range(h+3)),),
                 (tuple(1 if x==0 else 0 for x in range(h+3)),),f'delay{h}')
    check('arbitrary_delay_same_prefix',signature(chain,sink,h)==signature(chain,h+1,h))
    witness=distinguishing_word(chain,sink,h+1)
    check('arbitrary_delay_next_word',witness is not None and len(witness[0])==h+1)
reject('invalid_transition_rejected',lambda:System(1,2,((1,),),((0,),)))
reject('out_of_scope_variable_rejected',lambda:evaluate(point,Formula.equal(Term.probe(1,(),0),Term.literal(0)),(0,)))
reject('state_equality_not_in_fragment',lambda:evaluate(point,Formula('state_equal',(0,0)),(0,)))
reject('malformed_formula_rejected',lambda:evaluate(point,Formula('equal',()),(0,)))
reject('unknown_value_rejected',lambda:evaluate(point,Formula.equal(Term.literal(2),Term.literal(0)),(0,)))
reject('bad_observation_transport',lambda:check_transport(constant,visible,(0,1),onto=True))
check('input_hashes_unchanged',before==hashes())
result={'status':'PASS','seed':SEED,'started_at':started,'runtime_seconds':time.monotonic()-start,
        'fixtures':fixture_results,'checks':dict(sorted(checks.items())),
        'total_check_calls':sum(checks.values()),'inputs_sha256':before,
        'bounds':{'synthetic_fixtures':len(fixtures),'random_formulas_per_fixture':64,
                  'maximum_operation_depth':3,'maximum_quantifier_rank':3,
                  'all_pairs_checked':True,'large_fixture_quantifier_rank_cap':1,
                  'delayed_observation_horizons':'0..23'},
        'non_claims':['Not a verified Python implementation','Not a general model-theory solver',
                      'No state-space-free complexity claim','Not held-out AI discovery',
                      'Finite tests do not replace universal Lean proofs']}
(ROOT/'results').mkdir(exist_ok=True)
(ROOT/'results'/'PYTHON_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':result['status'],'fixtures':len(fixtures),'checks':result['checks'],
                  'total':result['total_check_calls'],'runtime_seconds':result['runtime_seconds']},indent=2))
