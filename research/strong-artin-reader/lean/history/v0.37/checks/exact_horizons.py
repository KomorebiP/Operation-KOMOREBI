#!/usr/bin/env python3
"""Exhaustive finite corroboration, not an infinite proof or independent review."""
import json
from pathlib import Path
from scalar_survival import certificate,valuation,lift_root

families={2:([1,2,3,4,6,8,12],range(1,5)),
          3:([1,2,3,6,9],range(1,4)),
          5:([1,2,5,10],range(1,3))}
records=[]
totals=dict(families=0,finite_candidates=0,target_prefix_comparisons=0,
            certificate_comparisons=0,digit_steps=0)
for p,(degrees,depths) in families.items():
    for d in degrees:
        s=valuation(p,d)
        for m in depths:
            H=max(m,s+1)+s
            mod_m,mod_h,mod_deep=p**m,p**H,p**(H+2)
            shallow={}
            deep={}
            for b in range(mod_h):
                if b%p:
                    shallow.setdefault(pow(b,d,mod_h),set()).add(b%mod_m)
                    totals['finite_candidates']+=1
            for b in range(mod_deep):
                if b%p:
                    deep.setdefault(pow(b,d,mod_deep),set()).add(b%mod_m)
                    totals['finite_candidates']+=1
            # Check every unit target at the deeper modulus, including those
            # for which no root exists. Compare whole prefix sets.
            target_count=0
            for u in range(mod_deep):
                if not u%p:continue
                assert shallow.get(u%mod_h,set())==deep.get(u,set()),(p,d,m,u)
                totals['target_prefix_comparisons']+=len(range(1,mod_m))-len(range(p,mod_m,p))
                target_count+=1
            # Check the optimized finite certificate against a separately
            # enumerated full horizon (all b modulo p^H).
            for u in range(mod_h):
                for a in range(mod_m):
                    if not a%p:continue
                    c=certificate(p,d,m,a,u)
                    assert c['survives']==(a in shallow.get(u,set())),(p,d,m,a,u)
                    totals['certificate_comparisons']+=1
            # Deterministic integer targets generated from known exact roots.
            # This tests the digit constructor, not just the image comparison.
            for b in range(1,min(p**(m+1),40)):
                if not b%p:continue
                target=b**d
                lifted=lift_root(p,d,m,b%mod_m,target,max(m+6,H+2))
                x,L=lifted['root'],lifted['precision']
                assert x%mod_m==b%mod_m and pow(x,d,p**L)==target%(p**L)
                totals['digit_steps']+=len(lifted['steps'])
            records.append(dict(p=p,d=d,m=m,horizon=H,comparison_depth=H+2,
                unit_targets_checked=target_count,unit_prefixes=(p-1)*p**(m-1)))
            totals['families']+=1

assert not certificate(3,3,2,4,1)['survives']
assert certificate(3,3,2,4,10)['survives']
assert not certificate(2,2,4,9,1)['survives']
assert pow(10,3,27)==1 and not certificate(3,3,3,10,1)['survives']
positive=lift_root(3,3,2,4,10,12)
out=dict(status='PASS',totals=totals,exhaustive_ranges=records,
         positive_cube_ten=positive,
         nonclaims=['Finite comparisons do not prove infinite solvability.',
                    'No arbitrary matrix or nonunit-prefix assertion is tested.',
                    'Digit lifts beyond declared exhaustive ranges are deterministic examples.'])
dest=Path('computations/exact_horizons/results.json')
dest.parent.mkdir(parents=True,exist_ok=True)
dest.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(totals))
