#!/usr/bin/env python3
"""Bounded, deterministic exact audit, with an exhaustive independent small oracle."""
from __future__ import annotations
from pathlib import Path
from collections import Counter
from itertools import product
from math import prod
from datetime import datetime, timezone
import random,json,time,sys,platform
import sympy
sys.path.insert(0,str(Path(__file__).resolve().parent/'reference'))
from audit_support import SupportMachine, Machine, PrunedMachine, DegreePrunedMachine, ProfiledMachine, recurrence_coefficients, digit_word
from ideal_engine import IdealMachine
from reachable_engine import reachable_module,lattice_step
SEED=31092026

def in_box(model,capacities,x):
    return all(int(z) % g == 0 for z,g in zip(x,model.generators(capacities)))


def independent_orbit_span(model):
    m,n=model.modulus,model.n
    orbit={model.initial}; frontier=[model.initial]
    while frontier:
        x=frontier.pop()
        for d in range(len(model.matrices)):
            y=model.transition_full(d,x)
            if y not in orbit:orbit.add(y);frontier.append(y)
    module={(0,)*n}
    # Exhaustive additive spans; this uses no HNF, divisibility test, or valuations.
    for v in sorted(orbit):
        module={tuple((x[i]+a*v[i])%m for i in range(n)) for x in module for a in range(m)}
    return orbit,module


def audit():
    rng=random.Random(SEED);counts=Counter();examples=[];generic=0;strict=0
    def ck(name,condition,info=None):
        counts[name]+=1
        if not condition:raise AssertionError((name,info))
    for p,r in [(2,0),(2,1),(2,2),(2,3),(3,1),(3,2),(5,1)]:
      for n in range(4):
       if (p**r)**n>800:continue
       for alpha in [0,1,2]:
        for _ in range(3):
         m=p**r
         v=tuple(rng.randrange(m) for _ in range(n))
         mats=tuple(tuple(tuple(rng.randrange(m) for _ in range(n)) for _ in range(n)) for _ in range(alpha))
         model=IdealMachine(p,r,v,mats); result=reachable_module(model); generic+=1
         orbit,module=independent_orbit_span(model)
         got={x for x in product(range(m),repeat=n) if result.contains(x)}
         ck('generic_exact_module_vs_orbit_span',got==module)
         ck('generic_exact_cardinality',result.cardinality==len(module))
         ck('generic_initial_inclusion',v in got)
         ck('generic_orbit_inclusion',orbit<=got)
         ck('generic_invariant_all_states',all(model.transition_full(d,x) in got for d in range(alpha) for x in got))
         ck('generic_fixed_lattice',lattice_step(model,result.basis)==result.basis)
         ck('generic_round_bound',result.growth_rounds<=sum(model.least_profile()))
         ck('generic_ideal_containment',all(in_box(model,model.least_profile(),x) for x in got))
         # Each early iterate uses exactly words shorter than its round index.
         from sympy import eye
         lattice=m*eye(n); finite={(0,)*n}
         for k in range(result.growth_rounds+1):
            from reachable_engine import ReachableModule
            snap=ReachableModule(model,lattice,k,[],result.capacity_bound)
            ck('generic_iterate_matches_independent_linear_closure',
               {x for x in product(range(m),repeat=n) if snap.contains(x)}==finite)
            generators=[v]+[model.transition_full(d,x) for x in finite for d in range(alpha)]
            new=finite
            for x in generators:
               if x not in new:
                  new={tuple((y[i]+a*x[i])%m for i in range(n)) for y in new for a in range(m)}
            finite=new;lattice=lattice_step(model,lattice)
    # Restriction witnesses, evaluated independently as finite sets.
    witnesses=[IdealMachine(5,1,(1,1,0),(((0,0,0),(0,0,0),(1,-1,0)),)),
               IdealMachine(2,2,(2,0),(((0,0),(2,0)),)),
               IdealMachine(5,1,(1,),(((1,),),))]
    witness_rows=[]
    for idx,model in enumerate(witnesses):
        res=reachable_module(model);orbit,span=independent_orbit_span(model)
        ck('witness_exact_cardinality',res.cardinality==[5,2,5][idx])
        ck('witness_orbit_span',len(span)==res.cardinality)
        if idx==0:ck('witness_exact_diagonal',span=={(a,a,0) for a in range(5)})
        if idx==2:ck('witness_span_not_orbit',orbit=={(1,)} and span!=orbit)
        witness_rows.append({'case':idx,'ideal_exponent':sum(model.least_profile()),'reachable_exponent':res.exponent,'orbit_size':len(orbit),'span_size':res.cardinality})
    # Actual p-adic mask matrices, then exact integer-lattice reachability.
    masks=[]
    for p in (2,3,5):
      for r in (1,2,3):
       for a,b in [([1],[1,-1]),([1],[1,p*p]),([1,1],[1]),([1,1],[1,1]),([1,0,1],[1,0,-1])]:
        masks.append((p,r,a,b))
    stress=[(2,4,[1],[1,4]),(2,8,[1],[1,-1]),(2,8,[1],[1,16]),(3,6,[1],[1,81])]
    masks+=stress
    for idx,(p,r,a,b) in enumerate(masks):
        full=Machine(p,r,a,b);old=DegreePrunedMachine(PrunedMachine(full));profile=ProfiledMachine(old);support=SupportMachine(profile)
        original=IdealMachine(p,r,tuple(support.initial_full),tuple(tuple(tuple(row) for row in t) for t in support.matrices))
        capacities=original.least_profile(); active=[i for i,c in enumerate(capacities) if c>0]
        reduced=IdealMachine(p,r,tuple(original.initial[i] for i in active),
                 tuple(tuple(tuple(t[j][i] for i in active) for j in active) for t in original.matrices))
        res=reachable_module(reduced)
        ck('mask_round_bound',res.growth_rounds<=sum(capacities))
        ck('mask_cardinality_ideal_bound',res.exponent<=sum(capacities));strict+=res.exponent<sum(capacities)
        def expand(x):
            y=[0]*original.n
            for i,z in zip(active,x):y[i]=int(z)%original.modulus
            return tuple(y)
        # Check every original profiled column, not merely the reduced submatrix.
        for i in range(original.n):
          basis=[0]*original.n;basis[i]=1
          for d in range(p):
            ck('mask_matrix_columns_vs_polynomial_routing',original.transition_full(d,basis)==tuple(support.flatten(profile.step(support.rows(basis),d))))
        # A second actual-mask closure route enumerates short digit words using
        # direct polynomial transitions, never HNF basis images or matrix powers.
        from sympy import Matrix, eye
        from sympy.matrices.normalforms import hermite_normal_form
        frontier=[tuple(support.initial_full)]; word_vectors=[]
        for depth in range(res.growth_rounds):
            next_frontier=[]
            for x in frontier:
                word_vectors.append(tuple(x[i] for i in active))
                ck('mask_short_word_omitted_coordinates_zero',all(x[i]==0 for i in range(original.n) if i not in active))
                for d in range(p):
                    next_frontier.append(tuple(support.flatten(profile.step(support.rows(x),d))))
            frontier=next_frontier
        if reduced.n:
            columns=[reduced.modulus*eye(reduced.n)]+[Matrix(reduced.n,1,list(v)) for v in word_vectors]
            direct_word_lattice=hermite_normal_form(Matrix.hstack(*columns))
        else:
            direct_word_lattice=res.basis
        ck('mask_reachable_vs_direct_polynomial_word_span',direct_word_lattice==res.basis)
        # All HNF generators stay within the old ideal box and are transition invariant.
        for j in range(reduced.n):
          x=res.generator(j); xx=expand(x)
          ck('mask_generators_ideal_containment',in_box(original,capacities,xx))
          for d in range(p):
            y=res.transition(d,x)
            ck('mask_generator_transition_full_embedding',expand(y)==original.transition_full(d,xx))
        for _ in range(3):
          coeff=[rng.randrange(reduced.modulus) for _ in range(reduced.n)]
          x=tuple(sum(int(res.basis[i,j])*coeff[j] for j in range(reduced.n))%reduced.modulus for i in range(reduced.n))
          ck('mask_arbitrary_reachable_membership',res.contains(x))
          for d in range(p):
            ck('mask_arbitrary_transition_embedding',expand(res.transition(d,x))==tuple(support.flatten(profile.step(support.rows(expand(x)),d))))
        oracle=recurrence_coefficients(p,p**r,a,b,32)
        for n,want in enumerate(oracle):
          x=reduced.initial
          for d in digit_word(p,n):x=res.transition(d,x)
          val=profile.output(support.rows(expand(x)))
          ck('mask_coefficient_vs_direct_recurrence',val==want,(p,r,a,b,n))
          ck('mask_coefficient_vs_support_machine',val==support.coefficient(n))
        if idx>=len(masks)-len(stress):
          examples.append({'p':p,'r':r,'A':a,'B':b,'profile_positions':original.n,'positive_ideal_coordinates':len(active),
            'ideal_exponent':sum(capacities),'reachable_exponent':res.exponent,'growth_rounds':res.growth_rounds,
            'round_exponents':res.round_exponents,'first16':oracle[:16],
            'hnf_basis_rows':[[int(res.basis[i,j]) for j in range(reduced.n)] for i in range(reduced.n)]})
        print('mask',idx+1,'/',len(masks),'ideal',sum(capacities),'reachable',res.exponent,'rounds',res.growth_rounds,flush=True)
    return {'status':'PASS','seed':SEED,'generic_systems':generic,'mask_cases':len(masks),'mask_strict_reductions':strict,
      'assertions':sum(counts.values()),'counts':dict(counts),'examples':examples,'witnesses':witness_rows,
      'python':platform.python_version(),'sympy':sympy.__version__,'failures':[],
      'non_claims':['Bounded computations are not the universal proof.','Hermite normal form engine is not formally refined to Lean.','No canonical operator-basis or observable quotient theorem.','No runtime or memory saving follows from state cardinality.']}

if __name__=='__main__':
    start=time.monotonic();result=audit();result['seconds']=time.monotonic()-start
    dest=Path(__file__).resolve().parents[1]/'results/audit_reachable.json';dest.parent.mkdir(exist_ok=True)
    dest.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='examples'},indent=2))
