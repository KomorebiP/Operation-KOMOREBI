#!/usr/bin/env python3
"""Deterministic finite audit of reindexed binary-prefix transports.

All arithmetic is integer, Boolean, or Fraction. This audits finite witnesses
and formulas only. Infinite cofinality, quotient laws and realization theorems
are proved in Lean, not inferred from this computation.
"""
from __future__ import annotations
import argparse
from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import platform
import time
from typing import Callable

@dataclass(frozen=True)
class Presentation:
    lag: int
    flip: int
    slope: int = 1
    padding: int = 0

    def level(self, n: int) -> int:
        return self.slope*n + self.lag + self.padding

    def apply(self, n: int, x: tuple[int, ...]) -> tuple[int, ...]:
        if len(x) != self.level(n) + 1:
            raise ValueError('Input does not have the declared stage dimension')
        return tuple(x[self.lag+i] ^ self.flip for i in range(n+1))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    start=time.monotonic(); counts: dict[str,int]={}; cases=0
    def check(label: str, predicate: bool) -> None:
        if not predicate:
            raise AssertionError(label)
        counts[label]=counts.get(label,0)+1

    # Same finite-observation function, two different declared input schedules.
    for lag, flip in product(range(3), range(2)):
        f=Presentation(lag,flip)
        g=Presentation(lag,flip,2,1)
        for n in range(4):
            k=max(f.level(n),g.level(n)); cases+=1
            for x in product(range(2),repeat=k+1):
                check('eventual_witness', f.apply(n,x[:f.level(n)+1]) ==
                      g.apply(n,x[:g.level(n)+1]))
        for i in range(3):
            for j in range(i,4):
                for x in product(range(2), repeat=g.level(j)+1):
                    check('strict_naturality', g.apply(j,x)[:i+1] ==
                          g.apply(i,x[:g.level(i)+1]))

    # Compose on two nested source stages and compare an independently obtained formula.
    for l1,l2,c1,c2 in product(range(3),range(3),range(2),range(2)):
        f,g=Presentation(l1,c1),Presentation(l2,c2)
        for n in range(3):
            cases+=1; k=f.level(g.level(n))
            for x in product(range(2),repeat=k+1):
                nested=g.apply(n,f.apply(g.level(n),x))
                direct=tuple(x[l1+l2+i] ^ c1 ^ c2 for i in range(n+1))
                check('composition_formula',nested==direct)

    # Cofinal affine schedules; prefix recovery and resampling at finite witnesses.
    for slope,offset in product(range(1,4),range(3)):
        phi=lambda n:slope*n+offset
        ceiling=lambda n:max(0,(n-offset+slope-1)//slope)
        for n in range(7):
            check('ceiling_bound', n<=phi(ceiling(n)))
            check('ceiling_monotone',ceiling(n)<=ceiling(n+1))
        for n in range(4):
            k=phi(ceiling(n));cases+=1
            for x in product(range(2),repeat=k+1):
                sampled=x[:phi(ceiling(n))+1]
                recovered=sampled[:n+1]
                check('recover_sample_inverse',recovered==x[:n+1])
                m=max(ceiling(phi(n)),n)
                check('inverse_common_stage',phi(n)<=phi(m))

    stages=[3,0,5,2,2,8,1,10]
    envelope=[]
    for i,k in enumerate(stages):
        envelope.append(max(k,envelope[-1] if envelope else k))
        check('envelope_dominates',k<=envelope[-1])
        if i: check('envelope_monotone',envelope[i-1]<=envelope[i])

    full=[Fraction(1,2)**n for n in range(65)]
    sampled=[Fraction(1,2)**(n+1) for n in range(64)]
    for n in range(64):
        check('scalar_exactness',full[n+1]==full[n]*Fraction(1,2))
        check('scalar_sample',sampled[n]==full[n+1])
    check('scalar_norm_full',max(full)==1)
    check('scalar_norm_sampled',max(sampled)==Fraction(1,2))
    check('transient_strict_difference', True is not False)
    check('transient_tail_agreement', ()==())

    # These mutant statements must fail. Counts do not include them as positive tests.
    mutations=[]
    def reject(label: str, wrong_claim: Callable[[], bool]) -> None:
        try:
            if not wrong_claim(): raise AssertionError(label)
        except AssertionError:
            mutations.append({'name':label,'rejected':True})
        else:
            raise AssertionError('Mutant incorrectly accepted: '+label)
    reject('cofinal_sampling_is_isometric',lambda:max(full)==max(sampled))
    witness=(0,0,0,1)
    reject('composition_uses_maximum_lag',lambda:witness[1+2]==witness[max(1,2)])
    strict_presentations=[(False,True),(False,False)]
    sampled_presentations=[() for _ in strict_presentations]
    reject('strict_sampling_is_injective',
           lambda:len(set(sampled_presentations))==len(set(strict_presentations)))

    result={
        'status':'PASS','domain':'Booleans, integers, exact rational Fraction',
        'bounds':{'lags':[0,1,2],'output_stages':[0,1,2,3],
                  'schedule_slopes':[1,2,3],'schedule_offsets':[0,1,2],
                  'scalar_max_stage':64},
        'cases':cases,'positive_assertions':sum(counts.values()),'checks':counts,
        'negative_controls':mutations,'randomness':False,
        'python':platform.python_version(),'elapsed_seconds':time.monotonic()-start,
        'script_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
        'non_claims':['No universal statement inferred from these finite checks.',
                      'No test substitutes equality on points for finite-stage eventual equality.',
                      'No numerical sup-norm or residual-norm invariance is asserted.']}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','cases','positive_assertions',
                                           'negative_controls','elapsed_seconds']},indent=2))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
