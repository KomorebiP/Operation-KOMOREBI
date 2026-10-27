from __future__ import annotations
from random import Random
import json, hashlib
from pathlib import Path

from prime_power_cartier_compiler import PrimePowerCartierCompiler, direct_coefficients, trim

SEED=2026091702
PRIMES=(2,3,5,7)
EXPONENTS=(1,2,3,4,5)
RANDOM_MASKS_PER_PAIR=6
NMAX=180


def run():
    rng=Random(SEED)
    cases=checks=0
    reductions=[]
    curated=[
        ([1,1],[1,-1],3,2),
        ([1,1],[1,-1],3,5),
        ([1,1,1],[1],2,4),
        ([1,0,1],[1,1],2,3),
        ([1,2],[1,-1,1],5,3),
        ([1,1],[1,25],5,3),   # defect has extra 5-adic divisibility
        ([1,1],[1,49],7,3),   # defect has extra 7-adic divisibility
    ]
    allcases=[]
    for c in curated:
        allcases.append(c)
    for p in PRIMES:
        for r in EXPONENTS:
            for _ in range(RANDOM_MASKS_PER_PAIR):
                da=rng.randint(0,3); db=rng.randint(0,3)
                A=[rng.randint(-4,4) for _ in range(da+1)]
                B=[rng.randint(-4,4) for _ in range(db+1)]
                c=rng.choice(list(range(1,p)))
                A[0]=c; B[0]=c
                if da and all(x==0 for x in A[1:]): A[-1]=1
                if db and all(x==0 for x in B[1:]): B[-1]=1
                allcases.append((trim(A),trim(B),p,r))

    examples=[]
    for A,B,p,r in allcases:
        comp=PrimePowerCartierCompiler(A,B,p,r)
        direct=direct_coefficients(A,B,p,r,NMAX)
        got=comp.coefficient_prefix(NMAX)
        if got != direct:
            for n,(x,y) in enumerate(zip(got,direct)):
                if x!=y:
                    raise AssertionError(("mismatch",A,B,p,r,n,x,y))
        checks += NMAX+1; cases += 1
        s=comp.bound_summary()
        if s.sharpened_dimension > s.coarse_dimension:
            raise AssertionError("sharpening enlarged dimension")
        reductions.append((s.coarse_dimension,s.sharpened_dimension,len(s.layers),s.coarse_layer_bound))
        if len(examples)<12:
            examples.append({
                "A":list(A),"B":list(B),"p":p,"r":r,
                "defect":list(comp.E),
                "defect_valuation": None if comp.defect_valuation>10**8 else comp.defect_valuation,
                "stabilization_depth": comp.one_layer_stabilization_depth(),
                "coarse_layers":s.coarse_layer_bound,"valuation_layer_bound":s.valuation_layer_bound,
                "max_correction_order":s.max_correction_order,"pruned_layers":list(s.layers),
                "coarse_global_degree":s.coarse_global_degree_bound,
                "valuation_global_degree":s.valuation_global_degree_bound,
                "degree_by_layer":dict(s.degree_by_layer),
                "coarse_dimension":s.coarse_dimension,"valuation_dimension":s.valuation_dimension,
                "sharpened_dimension":s.sharpened_dimension,
                "transition_nonzeros":list(comp.nonzero_entries()),
            })

    strict=sum(1 for c,s,_,_ in reductions if s<c)
    layer_strict=sum(1 for _,_,lp,lc in reductions if lp<lc)
    ratio=[s/c for c,s,_,_ in reductions if c]
    result={
        "schema":"komorebi-prime-power-cartier-sparse-compiler-verification-v2",
        "seed":SEED,"primes":list(PRIMES),"exponents":list(EXPONENTS),
        "random_masks_per_pair":RANDOM_MASKS_PER_PAIR,"nmax":NMAX,
        "cases":cases,"coefficient_checks":checks,"failures":0,
        "strict_dimension_reductions":strict,
        "strict_layer_reductions":layer_strict,
        "mean_dimension_ratio":sum(ratio)/len(ratio),
        "min_dimension_ratio":min(ratio),"max_dimension_ratio":max(ratio),
        "examples":examples,
        "claim_boundary":"Exact finite regression of the sparse compiler against an independent coefficient recurrence. It audits the implementation and sharpened bounds on the stated range; universal claims rely on the algebraic proofs in THEOREM_NOTE_BLOCK02.md."
    }
    return result

if __name__=='__main__':
    result=run()
    p=Path(__file__).with_name('verification_results_block02.json')
    p.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,indent=2,sort_keys=True))
