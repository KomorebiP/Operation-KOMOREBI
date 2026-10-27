#!/usr/bin/env python3
"""Independent guard regression against preserved arbitrary-precision code.

No archived code is changed. Brute force is the finite oracle.
"""
from pathlib import Path
from itertools import product
import importlib.util, json, math, sys

source=Path(sys.argv[1]).resolve()
output=Path(sys.argv[2])
spec=importlib.util.spec_from_file_location('archived_moving_search',source)
module=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=module
spec.loader.exec_module(module)
sector=module.Sector.build('test',10)
profile=module.LocalMovingProfile.build(sector,-1)
H=1
intervals=[(module.ceil_div(-H-x,p),(H-x)//p) for p,x in zip(sector.primes,profile.residues)]
aggregate_only=sum(lo for lo,hi in intervals)<=profile.q0<=sum(hi for lo,hi in intervals)
guarded=all(lo<=hi for lo,hi in intervals) and aggregate_only
brute=[x for x in product(range(-H,H+1),repeat=2) if sum((10//p)*v for p,v in zip(sector.primes,x))==-1]
assert profile.residues==(-1,2) and profile.q0==0
assert aggregate_only and not guarded and not brute
assert profile.n_interval(H)==(1,0)
height,lift=profile.gauge(0)
assert height==2 and max(map(abs,lift.values()))==2
cases=0
radicals=(2,3,5,6,10,14,15,21,30,42,70,105)
for r in radicals:
    s=module.Sector.build('oracle',r)
    weights=[r//p for p in s.primes]
    for H in range(4):
        possible={sum(w*v for w,v in zip(weights,coords)) for coords in product(range(-H,H+1),repeat=len(weights))}
        for t in range(-30,31):
            profile=module.LocalMovingProfile.build(s,t)
            lo,hi=profile.n_interval(H)
            assert (lo<=0<=hi)==(t in possible),(r,H,t,profile.residues,(lo,hi))
            if lo<=0<=hi:
                vector=profile.construct(0,H)
                assert max(map(abs,vector.values()),default=0)<=H
                assert sum(weights[i]*vector[p] for i,p in enumerate(s.primes))==t
            cases+=1
report={'status':'PASS','source':str(source),'counterexample':{'radical':10,'primes':[2,5],'target':-1,'height':1,'residues':[-1,2],'q0':0,'intervals':intervals,'aggregate_only_accepts':aggregate_only,'individual_guards_accept':guarded,'brute_solutions':brute,'preserved_n_interval':profile.n_interval(H) if False else [1,0],'minimum_height':height,'minimum_lift':lift},'finite_oracle_cases':cases,'bounds':{'radicals':radicals,'target':'-30..30','height':'0..3'},'interpretation':'The new manuscript criterion required individual nonempty interval guards. The preserved feasibility method already has these guards. Direct construct assumes feasibility and has final assertions. No archived code was edited.','non_claims':['Finite regression is not a proof of the all-input CRT theorem','No abc implication is established']}
output.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':'PASS','finite_oracle_cases':cases,'counterexample':report['counterexample']},indent=2))
