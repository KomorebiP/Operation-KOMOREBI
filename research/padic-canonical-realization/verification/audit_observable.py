#!/usr/bin/env python3
"""Finite exact audits: integer-lattice observer versus exhaustive behavior partitions.
Vector/matrix equalities count as one assertion. No floating-point decisions.
"""
from pathlib import Path
import sys, json, random, platform, time
from itertools import product
from math import prod
from collections import Counter
import sympy
from sympy import Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent/'reference'))
from observable_engine import ObservablePresentation, exponent
from ideal_engine import IdealMachine
from reachable_engine import reachable_module
from presentation_engine import CyclicPresentation
from audit_support import SupportMachine, Machine, PrunedMachine, DegreePrunedMachine, ProfiledMachine, recurrence_coefficients, digit_word
SEED=33092026


def transition(T,x,ds):
    return tuple(sum(int(T[j][i])*x[i] for i in range(len(ds)))%ds[j] for j in range(len(ds)))


def behavior_partition(moduli, matrices, output, m):
    """Independent finite-state refinement, using no HNF, Smith, ranks or divisions."""
    states=list(product(*(range(d) for d in moduli)))
    color={x:0 for x in states}; counts=[1]
    for _ in range(len(states)+1):
        labels={}; new={}
        for x in states:
            key=(color[x],sum(a*b for a,b in zip(output,x))%m,
                 tuple(color[transition(T,x,moduli)] for T in matrices))
            if key not in labels: labels[key]=len(labels)
            new[x]=labels[key]
        if new==color: return states,color,counts
        color=new;counts.append(len(labels))
    raise AssertionError('Finite refinement did not terminate.')


def audit():
    rng=random.Random(SEED);counts=Counter();generic=0;mask_count=0;examples=[];cases=[]
    def ck(label,ok,detail=None):
        counts[label]+=1
        if not ok: raise AssertionError((label,detail))
    def reject(label,f):
        try:f()
        except (ValueError,ArithmeticError):ck(label,True);return
        ck(label,False)
    for p,r in [(2,0),(2,1),(2,2),(2,3),(3,1),(3,2),(5,1)]:
      m=p**r
      for n in range(4):
       for alpha in (0,1,2):
        for trial in range(3):
          es=[rng.randrange(r+1) for _ in range(n)]; ds=tuple(p**e for e in es)
          if prod(ds)>625:continue
          mats=tuple(tuple(tuple((ds[j]//__import__('math').gcd(ds[j],ds[i]))*rng.randrange(__import__('math').gcd(ds[j],ds[i]))
                     for i in range(n)) for j in range(n)) for _ in range(alpha))
          lam=tuple((m//di)*rng.randrange(di) for di in ds)
          P=ObservablePresentation.construct(p,r,ds,mats,lam);generic+=1
          states,color,trajectory=behavior_partition(ds,mats,lam,m)
          ck('generic_quotient_cardinality',len(set(color.values()))==P.cardinality)
          zero=tuple(0 for _ in ds); silent={x for x in states if color[x]==color[zero]}
          ck('generic_kernel_cardinality',len(silent)==P.kernel_cardinality)
          ck('generic_finite_horizon',len(trajectory)-1<=sum(es))
          ck('generic_exact_rounds',len(trajectory)-1==P.growth_rounds)
          ck('generic_round_cardinalities',trajectory==[p**e for e in P.quotient_exponents_by_round])
          codes={};inverse={}
          for x in states:
            code=P.encode(x)
            ck('generic_exact_kernel_membership',P.in_kernel(x)==(x in silent))
            ck('generic_output_preserved',P.output(code)==sum(a*b for a,b in zip(lam,x))%m)
            if color[x] in codes:ck('generic_behavior_to_quotient',codes[color[x]]==code)
            else:codes[color[x]]=code
            if code in inverse:ck('generic_quotient_to_behavior',inverse[code]==color[x])
            else:inverse[code]=color[x]
            for d,T in enumerate(mats):
              ck('generic_transition_preserved',P.transition(d,code)==P.encode(transition(T,x,ds)))
          for y in product(*(range(d) for d in P.quotient_moduli)):
            ck('generic_quotient_roundtrip',P.encode(P.representative(y))==y)
          for _ in range(3):
            x=rng.choice(states);y=rng.choice(states);a=rng.randrange(m)
            encx=P.encode(x);ency=P.encode(y)
            ck('generic_projection_additive',P.encode(tuple((u+v)%di for u,v,di in zip(x,y,ds)))==tuple((u+v)%di for u,v,di in zip(encx,ency,P.quotient_moduli)))
            ck('generic_projection_scalar',P.encode(tuple(a*u%di for u,di in zip(x,ds)))==tuple(a*u%di for u,di in zip(encx,P.quotient_moduli)))
          reject('generic_wrong_source_dimension',lambda:P.encode([0]*(n+1)))
          reject('generic_wrong_quotient_dimension',lambda:P.representative([0]*(len(P.quotient_moduli)+1)))
    masks=[]
    for p in (2,3,5):
      for r in (1,2,3):
        for a,b in [([1],[1,-1]),([1],[1,p*p]),([1,1],[1]),([1,1],[1,1]),([1,0,1],[1,0,-1])]:masks.append((p,r,a,b))
    stress=[(2,4,[1],[1,4]),(2,8,[1],[1,-1]),(2,8,[1],[1,16]),(3,6,[1],[1,81])]
    masks+=stress
    for idx,(p,r,a,b) in enumerate(masks):
        full=Machine(p,r,a,b); degree=DegreePrunedMachine(PrunedMachine(full));profile=ProfiledMachine(degree);support=SupportMachine(profile)
        original=IdealMachine(p,r,tuple(support.initial_full),tuple(tuple(tuple(row) for row in t) for t in support.matrices))
        caps=original.least_profile();active=[i for i,c in enumerate(caps) if c>0]
        reduced=IdealMachine(p,r,tuple(original.initial[i] for i in active),tuple(tuple(tuple(t[j][i] for i in active) for j in active) for t in original.matrices))
        reach=reachable_module(reduced); C=CyclicPresentation.construct(reach); mask_count+=1
        def expand(x):
            y=[0]*original.n
            for i,z in zip(active,x):y[i]=int(z)%original.modulus
            return tuple(y)
        def actual_output(y):return profile.output(support.rows(expand(C.decode(y))))
        lam=[]
        for i in range(len(C.moduli)):
            e=tuple(int(i==j) for j in range(len(C.moduli)));lam.append(actual_output(e))
        P=ObservablePresentation.construct(p,r,C.moduli,C.matrices,lam)
        ck('mask_cardinality_identity',P.cardinality*P.kernel_cardinality==reach.cardinality)
        ck('mask_normalized_output_lower_bound',P.cardinality%(p**r)==0)
        for i in range(original.n):
          e=[0]*original.n;e[i]=1
          for d in range(p):
            ck('mask_original_columns_vs_polynomial',original.transition_full(d,e)==tuple(support.flatten(profile.step(support.rows(e),d))))
        for i in range(len(C.moduli)):
          e=tuple(int(i==j) for j in range(len(C.moduli)));encoded=P.encode(e)
          ck('mask_generator_output',P.output(encoded)==actual_output(e))
          for d in range(p):
            ck('mask_quotient_generator_transition',P.transition(d,encoded)==P.encode(C.transition(d,e)))
        for _ in range(4):
          x=tuple(rng.randrange(di) for di in C.moduli)
          ck('mask_arbitrary_output',P.output(P.encode(x))==actual_output(x))
          for d in range(p):ck('mask_arbitrary_transition',P.transition(d,P.encode(x))==P.encode(C.transition(d,x)))
        init=C.encode(reduced.initial);qinit=P.encode(init)
        oracle=recurrence_coefficients(p,p**r,a,b,32)
        for n,want in enumerate(oracle):
            y=P.iterate(digit_word(p,n),qinit);val=P.output(y)
            ck('mask_coefficient_vs_direct_recurrence',val==want,(p,r,a,b,n))
            ck('mask_coefficient_vs_predecessor',val==actual_output(C.iterate(digit_word(p,n),init)))
        row={'p':p,'r':r,'A':a,'B':b,'reachable_signature':C.exponents,'observable_signature':P.signature,
             'reachable_exponent':reach.exponent,'observable_exponent':exponent(p,P.cardinality),
             'unobservable_exponent':exponent(p,P.kernel_cardinality),'closure_rounds':P.growth_rounds}
        cases.append(row)
        if idx>=len(masks)-len(stress):examples.append(row|{'certificate':P.certificate(),'first16':oracle[:16]})
        print('mask',idx+1,'/',len(masks),'reachable',reach.exponent,'observable',row['observable_exponent'],'signature',P.signature,flush=True)
    P=ObservablePresentation.construct(2,2,[4],[[[1]]],[2])
    ck('nonfield_observable_quotient',P.cardinality==2 and P.kernel_cardinality==2 and P.signature==(1,))
    P=ObservablePresentation.construct(5,1,[5,5],[[[0,1],[1,0]]],[1,0])
    ck('immediate_kernel_not_invariant',P.kernel_cardinality==1 and P.cardinality==25 and P.growth_rounds==2)
    reject('reject_invalid_source_relation',lambda:ObservablePresentation.construct(2,2,[2,4],[[[0,0],[1,0]]],[0,0]))
    reject('reject_invalid_output_relation',lambda:ObservablePresentation.construct(2,2,[2],[[[1]]],[1]))
    return {'status':'PASS','seed':SEED,'assertions':sum(counts.values()),'counts':dict(counts),
       'generic_systems':generic,'mask_cases':mask_count,'strict_mask_reductions':sum(x['observable_exponent']<x['reachable_exponent'] for x in cases),
       'cases':cases,'examples':examples,'python':platform.python_version(),'sympy':sympy.__version__,
       'non_claims':['Finite audits do not prove the universal theorem.','No Python-to-Lean executable refinement.','No minimum DFA or cross-realization comparison theorem.'], 'failures':[]}

if __name__=='__main__':
    t=time.monotonic();result=audit();result['seconds']=time.monotonic()-t
    out=Path(__file__).resolve().parents[1]/'results/audit_observable.json'
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('examples','cases')},indent=2))
