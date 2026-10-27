#!/usr/bin/env python3
"""Exact finite tests of Smith proposals, cyclic transport, and intrinsic signatures.
Independent small oracle: enumerate all orbit-generated additive subgroup elements.
Independent large oracle: cardinalities of p^k-images via integer column HNF.
One tested equality (including a vector/matrix equality) counts one assertion.
"""
from __future__ import annotations
from pathlib import Path
from collections import Counter
from itertools import product
from math import prod
import random, json, time, platform, sys
import sympy
from sympy import Matrix, eye, zeros
from sympy.matrices.normalforms import hermite_normal_form
sys.path.insert(0,str(Path(__file__).resolve().parent/'reference'))
from audit_support import SupportMachine, Machine, PrunedMachine, DegreePrunedMachine, ProfiledMachine, recurrence_coefficients, digit_word
from ideal_engine import IdealMachine
from reachable_engine import reachable_module
from audit_reachable import independent_orbit_span
from presentation_engine import CyclicPresentation, certified_smith, validate_smith, integer_matrix
SEED=32092026


def audit():
    rng=random.Random(SEED);counts=Counter();generic=0;mask_count=0;examples=[];all_signatures=[]
    def ck(label, condition, detail=None):
        counts[label]+=1
        if not condition:raise AssertionError((label,detail))
    def rejected(label,fn):
        try:fn()
        except (ValueError,ArithmeticError):ck(label,True);return
        ck(label,False)
    def torsion_from_hnf(P,k):
        model=P.reachable.machine; n=model.n; m=model.modulus
        H=hermite_normal_form(Matrix.hstack(m*eye(n),(model.p**k)*P.reachable.basis)) if n else eye(0)
        image_card=m**n//abs(int(H.det()))
        return P.cardinality//image_card
    def check_signature(P, label, elements=None):
        model=P.reachable.machine;p,r=model.p,model.r
        ell=[]
        for k in range(r+2):
            expected=p**sum(min(k,e) for e in P.exponents)
            actual=torsion_from_hnf(P,k)
            ck(label+'_annihilator_hnf',actual==expected,(p,r,k,P.exponents))
            if elements is not None:
                exhaustive=sum(all((p**k*x)%model.modulus==0 for x in v) for v in elements)
                ck(label+'_annihilator_exhaustive',exhaustive==expected)
            q=actual;length=0
            while q>1 and q%p==0:q//=p;length+=1
            ck(label+'_annihilator_is_power',q==1);ell.append(length)
        for k in range(1,r+1):
            ck(label+'_intrinsic_multiplicity',(ell[k]-ell[k-1])-(ell[k+1]-ell[k])==P.exponents.count(k))
        n=model.n
        # Change the integer generator basis. No reliance on sorted HNF membership here.
        C=eye(n)
        if n>=2:C[0,1]=1;C[:,0],C[:,1]=C[:,1],C[:,0]
        K2=integer_matrix(C.inv()*P.relations) if n else zeros(0,0)
        D2,_,_=certified_smith(K2)
        ck(label+'_signature_basis_independence',tuple(int(D2[i,i]) for i in range(n) if D2[i,i]>1)==P.moduli)
    for p,r in [(2,0),(2,1),(2,2),(2,3),(3,1),(3,2),(5,1)]:
      for n in range(4):
       m=p**r
       if m**n>800:continue
       for alpha in (0,1,2):
        for trial in range(2):
         v=tuple(rng.randrange(m) for _ in range(n))
         mats=tuple(tuple(tuple(rng.randrange(m) for _ in range(n)) for _ in range(n)) for _ in range(alpha))
         model=IdealMachine(p,r,v,mats); reach=reachable_module(model);P=CyclicPresentation.construct(reach);generic+=1
         _,elements=independent_orbit_span(model)
         ck('generic_cardinality_vs_independent_span',P.cardinality==len(elements))
         coords=list(product(*(range(d) for d in P.moduli)))
         ck('generic_exhaustive_decoded_image',{P.decode(y) for y in coords}==elements)
         for x in sorted(elements):ck('generic_vector_roundtrip',P.decode(P.encode(x))==x)
         for y in coords:
            ck('generic_coordinate_roundtrip',P.encode(P.decode(y))==y)
            for d in range(alpha):
                ck('generic_transition_all_states',P.decode(P.transition(d,y))==model.transition_full(d,P.decode(y)))
         for trial2 in range(3):
            x=rng.choice(coords);y=rng.choice(coords);a=rng.randrange(m)
            add=tuple((u+v)%d for u,v,d in zip(x,y,P.moduli))
            ck('generic_decode_additive',P.decode(add)==tuple((u+v)%m for u,v in zip(P.decode(x),P.decode(y))))
            scalar=tuple((a*u)%d for u,d in zip(x,P.moduli))
            ck('generic_scalar_reduction',P.decode(scalar)==tuple(a*u%m for u in P.decode(x)))
         for d,T in enumerate(P.matrices):
          for j,dj in enumerate(P.moduli):
           for i,di in enumerate(P.moduli):ck('generic_mixed_modulus_relation',di*T[j][i]%dj==0)
         check_signature(P,'generic',elements)
         if n:
            broken=P.left.copy();broken[0,0]+=1
            rejected('smith_mutation_rejected',lambda:validate_smith(P.relations,P.diagonal,broken,P.right))
         rejected('bad_coordinate_length_rejected',lambda:P.iterate([], [0]*(len(P.active)+1)))
    masks=[]
    for p in (2,3,5):
      for r in (1,2,3):
       for a,b in [([1],[1,-1]),([1],[1,p*p]),([1,1],[1]),([1,1],[1,1]),([1,0,1],[1,0,-1])]:
        masks.append((p,r,a,b))
    stress=[(2,4,[1],[1,4]),(2,8,[1],[1,-1]),(2,8,[1],[1,16]),(3,6,[1],[1,81])]
    masks+=stress
    for idx,(p,r,a,b) in enumerate(masks):
        full=Machine(p,r,a,b);degree=DegreePrunedMachine(PrunedMachine(full));profile=ProfiledMachine(degree);support=SupportMachine(profile)
        original=IdealMachine(p,r,tuple(support.initial_full),tuple(tuple(tuple(row) for row in t) for t in support.matrices))
        capacities=original.least_profile();active=[i for i,c in enumerate(capacities) if c>0]
        reduced=IdealMachine(p,r,tuple(original.initial[i] for i in active),tuple(tuple(tuple(t[j][i] for i in active) for j in active) for t in original.matrices))
        reach=reachable_module(reduced);P=CyclicPresentation.construct(reach);mask_count+=1
        def expand(x):
            y=[0]*original.n
            for i,z in zip(active,x):y[i]=int(z)%original.modulus
            return tuple(y)
        ck('mask_initial_roundtrip',P.decode(P.encode(reduced.initial))==reduced.initial)
        ck('mask_cardinality_unchanged',prod(P.moduli)==reach.cardinality)
        ck('mask_exponent_sum',sum(P.exponents)==reach.exponent)
        check_signature(P,'mask')
        for i in range(original.n):
          unit=[0]*original.n;unit[i]=1
          for d in range(p):
            ck('mask_columns_vs_polynomial',original.transition_full(d,unit)==tuple(support.flatten(profile.step(support.rows(unit),d))))
        for i in range(len(P.active)):
          y=tuple(int(j==i) for j in range(len(P.active)));x=P.decode(y)
          ck('mask_cyclic_generator_roundtrip',P.encode(x)==y)
          for d in range(p):
            ck('mask_cyclic_generator_transport',expand(P.decode(P.transition(d,y)))==tuple(support.flatten(profile.step(support.rows(expand(x)),d))))
        for trial in range(3):
          y=tuple(rng.randrange(d) for d in P.moduli);x=P.decode(y)
          ck('mask_arbitrary_coordinate_roundtrip',P.encode(x)==y)
          for d in range(p):
            ck('mask_arbitrary_transport',expand(P.decode(P.transition(d,y)))==tuple(support.flatten(profile.step(support.rows(expand(x)),d))))
        for T in P.matrices:
          for j,dj in enumerate(P.moduli):
           for i,di in enumerate(P.moduli):ck('mask_mixed_modulus_relation',di*T[j][i]%dj==0)
        oracle=recurrence_coefficients(p,p**r,a,b,32)
        for n,want in enumerate(oracle):
          y=P.iterate(digit_word(p,n),P.encode(reduced.initial));x=P.decode(y)
          val=profile.output(support.rows(expand(x)))
          ck('mask_coefficient_vs_recurrence',val==want,(p,r,a,b,n))
          ck('mask_coefficient_vs_predecessor',val==support.coefficient(n))
        row={'p':p,'r':r,'A':a,'B':b,'signature':list(P.exponents),'reachable_exponent':reach.exponent}
        all_signatures.append(row)
        if idx>=len(masks)-len(stress):
            examples.append(row|{'ideal_exponent':sum(capacities),'first16':oracle[:16], 'presentation_certificate':P.certificate()})
        print('mask',idx+1,'/',len(masks),'signature',P.exponents,flush=True)
    # Direct independent module-type and mixed-modulus restriction witnesses.
    cyclic4=[(x,) for x in range(4)];elem4=list(product(range(2),repeat=2))
    ck('same_cardinality_distinct_torsion',len(cyclic4)==len(elem4) and sum(2*x[0]%4==0 for x in cyclic4)==2 and sum(all(2*u%2==0 for u in x) for x in elem4)==4)
    ck('invalid_mixed_modulus_entry',2*1%4!=0)
    ck('valid_mixed_modulus_entry',2*2%4==0)
    T=Matrix([[0,1],[0,0]]);S=Matrix([[0,1],[1,0]])
    ck('coordinate_choice_changes_matrix',T[0,1]==1 and (S*T*S)[0,1]==0)
    return {'status':'PASS','seed':SEED,'assertions':sum(counts.values()),'counts':dict(counts),'generic_systems':generic,
      'mask_cases':mask_count,'examples':examples,'all_mask_signatures':all_signatures,'failures':[],
      'python':platform.python_version(),'sympy':sympy.__version__,
      'non_claims':['Finite audits are not the universal Lean theorem.','Smith algorithm is externally proposed and exactly certificate-checked, not a formal Lean executable refinement.','A signature classifies only the module, not the full digit system or sequence.','No state cardinality reduction occurs in this presentation stage.']}

if __name__=='__main__':
    start=time.monotonic();res=audit();res['seconds']=time.monotonic()-start
    target=Path(__file__).resolve().parents[1]/'results/audit_presentation.json'
    target.write_text(json.dumps(res,indent=2)+'\n')
    print(json.dumps({k:v for k,v in res.items() if k not in ['examples','all_mask_signatures']},indent=2))
