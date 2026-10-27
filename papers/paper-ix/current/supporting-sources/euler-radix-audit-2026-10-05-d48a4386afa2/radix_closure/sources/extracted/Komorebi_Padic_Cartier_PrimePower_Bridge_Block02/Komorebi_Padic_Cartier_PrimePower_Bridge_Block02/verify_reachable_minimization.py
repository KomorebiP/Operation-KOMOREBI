from __future__ import annotations
import json
from pathlib import Path
from prime_power_cartier_compiler import PrimePowerCartierCompiler, direct_coefficients

CASES=[
    ([1,1],[1,-1],3,2,20000),
    ([1,1],[1,-1],2,2,20000),
    ([1,1,1],[1],2,4,20000),
    ([1,1],[1,25],5,3,20000),
    ([1,1],[1,49],7,3,20000),
]
NMAX=500

def run():
    rows=[]; checks=0
    for A,B,p,r,cap in CASES:
        C=PrimePowerCartierCompiler(A,B,p,r)
        states,T,out=C.reachable_automaton(cap)
        blocks,mT,mout,block_of=C.minimize_output_automaton(T,out)
        # initial reachable state is state 0; trace both automata on base-p digits for 0..NMAX.
        direct=direct_coefficients(A,B,p,r,NMAX)
        for n in range(NMAX+1):
            s=0; ms=block_of[0]; x=n
            while x:
                d=x%p; x//=p
                s=T[s][d]; ms=mT[ms][d]
            if out[s] != direct[n] or mout[ms] != direct[n]:
                raise AssertionError((A,B,p,r,n,out[s],mout[ms],direct[n]))
            checks+=1
        rows.append({
            'A':A,'B':B,'p':p,'r':r,'linear_dimension':C.dimension,
            'reachable_states':len(states),'minimal_output_states':len(blocks),
            'reduction_ratio':len(blocks)/len(states),
        })
    return {'schema':'komorebi-prime-power-cartier-reachable-minimization-v1',
            'cases':len(CASES),'nmax':NMAX,'coefficient_checks':checks,'failures':0,'rows':rows,
            'claim_boundary':'Reachable enumeration and Moore minimization are exact for these explicitly enumerated finite automata. The state cap is a resource guard; exceeding it would be inconclusive, not a theorem failure.'}

if __name__=='__main__':
    r=run(); Path(__file__).with_name('reachable_minimization_results.json').write_text(json.dumps(r,indent=2,sort_keys=True)+'\n'); print(json.dumps(r,indent=2,sort_keys=True))
