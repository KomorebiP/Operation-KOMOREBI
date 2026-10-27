from __future__ import annotations
import hashlib, itertools, json, math, platform, random, time, traceback
from collections import Counter
from pathlib import Path
from ideal_engine import IdealMachine

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results_current'/'generic_ideal_audit_result.json'
SEED=20260921
counts=Counter()

def check(name, pred, data=None):
    counts[name]+=1
    if not pred:
        raise AssertionError((name,data))

def check_system(M, rng):
    c=M.least_profile();g=M.generators(c)
    check('fixed_point',M.step_profile(c)==c)
    check('independent_gcd_closure',g==M.least_gcd_generators())
    check('generator_invariance',M.closed_direct(c))
    check('support_refinement',all(c[i]==0 for i in range(M.n) if i not in M.support()))
    check('cardinality_comparison',M.state_count(c)<=M.modulus**len(M.support()))
    if M.n<=3 and M.r<=3:
        for w in itertools.product(range(M.r+1), repeat=M.n):
            closed=M.closed_direct(w)
            check('closure_characterization',closed==(M.step_profile(w)==w))
            if closed:
                check('exhaustive_leastness',all(a<=b for a,b in zip(c,w)))
    if M.state_count(c)<=128:
        ys=list(itertools.product(*(range(M.p**a) for a in c)))
        check('enumerated_cardinality',len({M.embed(c,y) for y in ys})==M.state_count(c))
    else:
        ys=[tuple(rng.randrange(M.p**a) for a in c) for _ in range(12)]
    for y in ys:
        x=M.embed(c,y)
        check('encode_decode',M.decode(c,x)==y)
        for d in range(len(M.matrices)):
            z=M.transition_cyclic(c,d,y)
            check('transition_conjugacy',M.embed(c,z)==M.transition_full(d,x))
            a=rng.randrange(M.modulus)
            ay=tuple(a*v%(M.p**cap) for v,cap in zip(y,c))
            az=tuple(a*v%(M.p**cap) for v,cap in zip(z,c))
            check('transition_scalar_compatibility',M.transition_cyclic(c,d,ay)==az)
    x=M.initial;y=M.decode(c,x)
    for _ in range(12):
        check('word_simulation',M.embed(c,y)==x)
        if not M.matrices:break
        d=rng.randrange(len(M.matrices));x=M.transition_full(d,x);y=M.transition_cyclic(c,d,y)
    return c

def main():
    rng=random.Random(SEED);systems=0
    for p in (2,3,5):
        for r in range(4):
            for n in range(4):
                for digits in (0,1,2):
                    for _ in range(3):
                        m=p**r
                        M=IdealMachine(p,r,tuple(rng.randrange(m) for _ in range(n)),
                            tuple(tuple(tuple(rng.randrange(m) for _ in range(n)) for _ in range(n)) for _ in range(digits)))
                        check_system(M,rng);systems+=1
    for p in (2,3,5):
        for r in range(4):
            m=p**r;M=IdealMachine(p,r,(),())
            for x in range(m):
                for a in range(r+3):
                    check('capped_multiplication',M.order((p**a*x)%m)==min(r,a+M.order(x)))
                for c in range(r+1):
                    gen=p**(r-c)
                    check('membership_characterization',(x%gen==0)==(r-M.order(x)<=c))
            for c in range(r+1):
                gen=p**(r-c);small=p**c
                images=[gen*y%m for y in range(small)]
                check('cyclic_bijection',len(set(images))==small and set(images)=={x for x in range(m) if x%gen==0})
                for y in range(small):
                    check('cyclic_roundtrip',images[y]//gen==y)
                    for scalar in range(m):
                        check('cyclic_scalar_law',(gen*(scalar*y%small))%m==(scalar*images[y])%m)
    nil=IdealMachine(2,2,(2,0),(((0,0),(2,0)),))
    nc=check_system(nil,rng)
    check('nilpotent_profile',nc==(1,0))
    check('nilpotent_cardinality',nil.state_count(nc)==2 and nil.modulus**len(nil.support())==16)
    corr=IdealMachine(5,1,(1,1,0),(((0,0,0),(0,0,0),(1,-1,0)),))
    cc=check_system(corr,rng)
    check('correlation_not_removed',cc==(1,1,1) and corr.transition_full(0,corr.initial)==(0,0,0))
    return {'systems':systems,'nilpotent':{'capacities':nc,'old_cardinality':16,'new_cardinality':2},
            'correlated':{'capacities':cc,'initial_image':corr.transition_full(0,corr.initial)},
            'nonclaims':['No direct actual-mask integration audit in this suite.','No Python-to-Lean executable refinement theorem.',
              'Products of coordinate ideals need not be minimal correlated submodules or automata.']}

if __name__=='__main__':
    started=time.time();inputs={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),Path(__file__).with_name('ideal_engine.py'))}
    try:
        result=main();result.update(status='PASS',errors=[]);exitcode=0
    except Exception as e:
        result={'status':'FAIL','errors':[repr(e)],'traceback':traceback.format_exc()};exitcode=1
    result.update(assertions=sum(counts.values()),checks=dict(counts),seed=SEED,seconds=time.time()-started,
      python=platform.python_version(),inputs_before=inputs,
      inputs_after={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),Path(__file__).with_name('ideal_engine.py'))})
    OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
    raise SystemExit(exitcode)
