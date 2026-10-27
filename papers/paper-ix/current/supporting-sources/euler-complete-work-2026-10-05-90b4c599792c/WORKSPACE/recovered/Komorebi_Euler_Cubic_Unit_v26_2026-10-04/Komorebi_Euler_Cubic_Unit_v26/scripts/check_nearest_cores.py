#!/usr/bin/env python3
"""Independent integer audits for the nearest-neighbor collision block.

Python 3.10+, standard library only. These finite checks corroborate the Lean
proofs; they do not establish a universal Euler-family classification.
Outputs are never overwritten. All polynomial arithmetic is exact.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from math import comb, factorial
from pathlib import Path
import random
import time


def v2(n: int) -> int:
    if n == 0:
        raise ValueError('v2(0) has no finite value in this audit')
    n = abs(n)
    return (n & -n).bit_length() - 1


def trim(p: list[int]) -> list[int]:
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    return p


def mul(p: list[int], q: list[int]) -> list[int]:
    out = [0] * (len(p) + len(q) - 1)
    for i, a in enumerate(p):
        for j, b in enumerate(q):
            out[i+j] += a*b
    return trim(out)


def add(p: list[int], q: list[int]) -> list[int]:
    out = [0] * max(len(p), len(q))
    for i, a in enumerate(p): out[i] += a
    for i, a in enumerate(q): out[i] += a
    return trim(out)


def evaluate(p: list[int], x: int) -> int:
    out = 0
    for c in reversed(p): out = out*x+c
    return out


def derivative(p: list[int], d: int) -> list[int]:
    return [factorial(n)//factorial(n-d)*p[n]
            for n in range(d, len(p))] or [0]


def coeff(p: list[int], n: int) -> int:
    return p[n] if n < len(p) else 0


def last_odd(p: list[int]) -> int | None:
    inds = [n for n, a in enumerate(p) if a % 2]
    return max(inds) if inds else None


def packet(j: int) -> list[int]:
    out = [1]
    for ell in range(j):
        out = mul(out, mul([-ell, 1], [-2*ell-1, 2]))
    return out


def affine_coefficients(p: list[int], a: int, s: int, last: int) -> list[int]:
    """Direct binomial coefficient substitution, not factorwise localization."""
    return [s**n * sum(p[m]*comb(m,n)*a**(m-n)
                      for m in range(n,len(p)))
            for n in range(last+1)]


def audit(max_j: int, trials: int) -> dict:
    counts: Counter[str] = Counter()
    start = time.monotonic()
    def check(label: str, ok: bool) -> None:
        if not ok:
            raise AssertionError(f'{label}: check {counts[label]+1} failed')
        counts[label] += 1

    # All geometric balls in a moderate complete range; no huge-value sampling.
    for j in range(4,max_j+1):
        for i in range(j):
            k = max(i,j-1-i).bit_length()
            b = 1 << (k-1)
            near = [ell for ell in range(j) if ell != i and v2(i-ell) == k-1]
            expected = [ell for ell in (i-b,i+b) if 0 <= ell < j]
            check('nearest_geometry', k >= 2 and near == expected and 1 <= len(near) <= 2)
            check('far_distance_bound', all(v2(i-ell) <= k-2
                  for ell in range(j) if ell != i and ell not in near))

    # Compute P_j in the ORIGINAL variable, then translate by direct binomial
    # expansion. This is independent of the normalized-factor construction.
    requests: dict[int,list[int]] = {j:list(range(j)) for j in range(4,33)}
    requests.update({65:[0,20,32,64], 97:[6,38,48,96],
                     113:[9,41,56,105],129:[0,64,104,128],
                     145:[0,51,72,144],161:[0,26,80,90,154,160],
                     258:[0,1,128,256,257],514:[0,230,257,435,513]})
    local_records=[]
    for j, centers in requests.items():
        p=packet(j)
        for i in centers:
            k=max(i,j-1-i).bit_length(); h=1 << (k-1)
            d=v2(factorial(i))+v2(factorial(j-1-i))
            t=k+d
            nmax=2*j-1 if j<=32 else 10
            local=affine_coefficients(p,i,1<<k,nmax+1)
            check('exact_center_zero', local[0] == 0)
            check('whole_local_content', all(x % (1<<t)==0 for x in local))
            q=[local[n+1]//(1<<t) for n in range(nmax+1)]
            check('skeleton_constant_unit', q[0]%2==1)
            left=i>=h; right=i+h<j
            nearest=[1,-2] if right and not left else [1,2]
            if left and right: nearest=[1,0,-4]
            # Divide the known translated coefficient vector by its short nearest
            # factor. Its constant is 1, so this uses no rational denominators.
            rem=[]
            for n in range(nmax+1):
                rem.append(q[n]-sum(nearest[a]*rem[n-a]
                           for a in range(1,min(n,len(nearest)-1)+1)))
                check('four_scaled_remainder', rem[n] % (4**n) == 0)
                check('factor_reassembly', q[n] == sum(nearest[a]*rem[n-a]
                      for a in range(min(n,len(nearest)-1)+1)))
            local_records.append({'j':j,'i':i,'k':k,'t':t,'nearest':nearest,
                                  'coefficients_checked':nmax+1})

    rng=random.Random(20261004)
    outcome=Counter()
    for _ in range(trials):
        degree=rng.randrange(0,10)
        e=[rng.randrange(-20,21) for _ in range(degree+1)]
        tail=[rng.randrange(-20,21) for _ in range(degree+1)]
        e[0]=2*rng.randrange(-20,21)+1
        tail[0]=2*rng.randrange(-20,21)+1
        w=2*rng.randrange(-20,21)
        es=[a*4**n for n,a in enumerate(e)]
        ts=[a*4**n for n,a in enumerate(tail)]
        for typ, nearest, sign in [('left',[1,2],1),('right',[1,-2],-1),('both',[1,0,-4],0)]:
            a=mul(nearest,es)
            numerator=add([w], [0]+add(a,ts))
            check('whole_core_even', all(c%2==0 for c in numerator))
            f=[c//2 for c in numerator]
            if typ!='both':
                check('one_neighbor_last_odd',last_odd(f)==2)
                for n in range(degree+3):
                    expected=4**n*(2*(coeff(e,n+1)+coeff(tail,n+1))+sign*coeff(e,n))
                    check('one_neighbor_coefficient_identity',coeff(f,n+2)==expected)
                normal=f; d=2; outcome['quadratic']+=1
            else:
                check('two_neighbor_second_identity', coeff(f,2)==2*(coeff(e,1)+coeff(tail,1)))
                for n in range(degree+3):
                    expected=2*4**n*(4*(coeff(e,n+2)+coeff(tail,n+2))-coeff(e,n))
                    check('two_neighbor_coefficient_identity',coeff(f,n+3)==expected)
                d=last_odd(f)
                if d is None:
                    check('two_neighbor_content_exactly_one',all(c%2==0 for c in f) and coeff(f,3)%4==2)
                    normal=[c//2 for c in f];d=3
                    check('divided_cubic_last_odd',last_odd(normal)==3)
                    outcome['cubic']+=1
                else:
                    check('two_neighbor_trichotomy',d in (0,1))
                    normal=f;outcome['constant' if d==0 else 'affine']+=1
            for x in (0,1,-1,2,3,8,17):
                value=evaluate(derivative(normal,d),x)
                check('top_jet_exact_valuation', value!=0 and v2(value)==v2(factorial(d)))

    # Honest negative controls: the analytic hypotheses allow double/triple zeros.
    f2=[0,0,1]; f3=[0,0,0,-2]
    check('permitted_double', all(evaluate(derivative(f2,d),0)==0 for d in (0,1))
                              and evaluate(derivative(f2,2),0)!=0)
    check('permitted_triple', all(evaluate(derivative(f3,d),0)==0 for d in (0,1,2))
                              and evaluate(derivative(f3,3),0)!=0)
    check('double_direct_identity', add([0], [0]+add([1,2],[-1])) == [2*c for c in f2])
    check('triple_direct_identity', add([0], [0]+add([1,0,-4],[-1])) == [2*c for c in f3])

    # Original integer example. Independent digit and valuation recurrences agree.
    r=(1<<64)-17; bound=(r.bit_count()-1)//3
    costs=[3*q+(r+q).bit_count()-r.bit_count() for q in range(bound+1)]
    mu=min(costs);j=max(q for q,c in enumerate(costs) if c==mu)
    ecosts=[3*q+(j-1).bit_count()-(j-q-1).bit_count() for q in range(j)]
    origin=3*j+1+(j-1).bit_count()-min(ecosts)
    delta=v2(r+j)-origin
    check('actual_resonant_descriptor', (bound,j,mu,origin,delta)==(20,17,-11,53,11))
    accum=0
    for q in range(1,1025):
        accum+=4-v2(r+q)
        check('actual_increment_identity', accum==3*q+(r+q).bit_count()-r.bit_count())
    candidates=[]
    for i in range(17):
        k=max(i,16-i).bit_length()
        slope=v2(factorial(i))+v2(factorial(16-i))
        both=i>=1<<(k-1) and i+(1<<(k-1))<17
        if slope==11: candidates.append(i)
        check('terminal17_resonant_one_neighbor', slope!=11 or not both)
    return {'status':'PASS','checked_utc':datetime.now(timezone.utc).isoformat(),
            'seconds':round(time.monotonic()-start,6),'registered_checks':sum(counts.values()),
            'check_counts':dict(counts),'geometry_max_j':max_j,'random_seed':20261004,
            'finite_seed_trials':trials,'finite_core_outcomes':dict(outcome),
            'localized_packets':len(local_records),'localization_records':local_records,
            'actual_example':{'r':str(r),'terminal':j,'mu':mu,'delta':delta,
                              'candidate_slope_centers':candidates},
            'boundary':'Finite integer/synthetic checks. Universal claims come from Lean. No new Euler-family atlas.'}


def main() -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--max-j',type=int,default=192)
    p.add_argument('--trials',type=int,default=256)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    if not 4<=args.max_j<=4096 or args.trials<1:
        raise ValueError('Require 4<=max-j<=4096 and trials>=1')
    if args.output.exists():raise FileExistsError(args.output)
    data=audit(args.max_j,args.trials)
    data['script_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps({k:v for k,v in data.items() if k not in ('localization_records',)},indent=2))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
