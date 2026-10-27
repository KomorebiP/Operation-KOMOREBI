"""Exact bounded audit of the separate, written orbit-interpolation theorem."""
from collections import defaultdict
from fractions import Fraction as F
from pathlib import Path
from math import prod
import json, sys
from packet_core import shell, involution, weight, tau_from_product

def inv(v):
    s2,s3,s4,s5=[sum(x**k for x in v) for k in range(2,6)]
    return (F(s4,s2**2),F(s3*s3,s2**3),F(s3*s5,s2**4),F(s5*s5,s2**5))

def s2(v):return sum(x*x for x in v)
def E(v,t):
    a,b,c,d=[sum(x**k for x in v) for k in range(2,6)]
    return c*a**3+t*b*b*a*a+t*t*b*d*a+t**3*d*d

def interpolant(reps,target,t):
    C=s2(reps[0]); es=[E(v,t) for v in reps]
    assert len(set(es))==len(es)
    def L(i,v):
        rho=F(s2(v),C)**5
        return prod(F(E(v,t)-es[j]*rho,es[i]-es[j])
                    for j in range(len(es)) if j!=i)
    def Q(v):return sum(a*L(i,v) for i,a in enumerate(target))
    return Q,L

out={'status':'PASS','invariant_separation_shells':128,
     'packet_count':0,'orbit_count':0,'cases':[]}
tau=tau_from_product(128)
for n in range(1,129):
    pts=list(shell(n)); groups=defaultdict(list)
    for v in pts:groups[min(v,involution(v))].append(v)
    reps=sorted(groups)
    assert len({inv(v) for v in reps})==len(reps)
    assert all(inv(v)==inv(involution(v)) for v in pts)
    assert sum(map(weight,pts))==tau[n]
    out['packet_count']+=len(pts);out['orbit_count']+=len(reps)
    if n not in (7,31):continue
    t=next(t for t in range(3*len(reps)*(len(reps)-1)//2+1)
           if len({E(v,t) for v in reps})==len(reps))
    masses=[sum(map(weight,groups[r])) for r in reps]
    target=[F(-1) for r in reps]
    target[0]=F(tau[n],masses[0])-1
    Q,L=interpolant(reps,target,t)
    # Orthogonal checks: Kronecker evaluation, individual packet values,
    # independent q-product survivor, and failure of universal nullness.
    assert all(L(i,v)==int(i==j) for i in range(len(reps))
               for j,v in enumerate(reps))
    corrected=[sum(weight(v)*(1+Q(v)) for v in groups[r]) for r in reps]
    assert corrected==[tau[n]]+[0]*(len(reps)-1)
    null_at_target=sum(weight(v)*Q(v) for v in pts)
    assert null_at_target==0
    shell_one=sum(weight(v)*Q(v) for v in shell(1))
    assert shell_one!=0
    out['cases'].append({'n':n,'orbits':len(reps),'degree':10*(len(reps)-1),
       'separating_integer_t':t,'original_masses':masses,
       'corrected_masses':[str(x) for x in corrected],
       'shell_one_failure':str(shell_one),'target_null_sum':str(null_at_target)})
Path(sys.argv[1]).write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='cases'}))
