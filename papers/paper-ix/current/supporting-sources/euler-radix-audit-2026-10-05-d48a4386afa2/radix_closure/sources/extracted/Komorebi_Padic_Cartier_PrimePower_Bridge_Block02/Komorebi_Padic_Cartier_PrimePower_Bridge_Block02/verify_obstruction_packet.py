from __future__ import annotations
from random import Random
import json
from pathlib import Path

from prime_power_cartier_compiler import frobenius_defect, vp_poly, vp_int, trim, is_prime

SEED=2026091703
PRIMES=(2,3,5,7,11)
SAMPLES=40
MAX_R=7


def one_layer_holds(B,p,r):
    # Literal one-layer denominator stabilization is equivalent to B^p == B(z^p) mod p^r,
    # i.e. p*E_B == 0 mod p^r.
    E=frobenius_defect(B,p)
    mod=p**r
    return all((p*x) % mod == 0 for x in E)


def run():
    rng=Random(SEED)
    cases=checks=0
    finite_depths=[]
    for p in PRIMES:
        assert is_prime(p)
        masks=[[1],[1,-1],[1,p],[1,p*p],[1,p*p, p**3]]
        for _ in range(SAMPLES):
            d=rng.randint(0,4)
            b0=rng.choice([x for x in range(1,p*2+1) if x%p])
            B=[b0]+[rng.randint(-p**3,p**3) for _ in range(d)]
            masks.append(trim(B))
        for B in masks:
            E=frobenius_defect(B,p)
            h=vp_poly(E,p)
            depth=None if h>10**8 else 1+h
            if depth is not None: finite_depths.append(depth)
            for r in range(1,MAX_R+1):
                criterion = True if depth is None else r <= depth
                actual=one_layer_holds(B,p,r)
                if actual != criterion:
                    raise AssertionError(("depth criterion mismatch",B,p,r,E,h,actual,criterion))
                checks+=1
            # If finite, the obstruction packet at the last successful precision is nonzero mod p.
            if depth is not None:
                div=p**(depth-1)
                if any(x%div for x in E):
                    raise AssertionError("defect not divisible at claimed depth")
                packet=[(x//div)%p for x in E]
                if not any(packet):
                    raise AssertionError(("terminal obstruction packet vanished",B,p,depth,E,packet))
            cases+=1
    return {
        "schema":"komorebi-one-layer-obstruction-packet-verification-v1",
        "seed":SEED,"primes":list(PRIMES),"samples_per_prime":SAMPLES,
        "max_precision_exponent_checked":MAX_R,"mask_cases":cases,
        "precision_checks":checks,"failures":0,
        "max_finite_stabilization_depth_observed":max(finite_depths) if finite_depths else None,
        "claim_boundary":"This checks the valuation criterion for the literal one-layer normal form on finite masks/precisions. The necessary-and-sufficient theorem is algebraic: the all-digit identity is equivalent to p E_B = 0 mod p^r because Cartier sections jointly reconstruct a series and all remaining factors are units."
    }

if __name__=='__main__':
    result=run()
    Path(__file__).with_name('obstruction_verification_results.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,indent=2,sort_keys=True))
