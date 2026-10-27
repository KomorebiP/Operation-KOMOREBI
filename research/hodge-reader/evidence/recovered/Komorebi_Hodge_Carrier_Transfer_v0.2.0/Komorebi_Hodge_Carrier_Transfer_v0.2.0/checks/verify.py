#!/usr/bin/env python3
"""Exact finite replay of the Carrier/Transfer v0.2.0 certificates.

Python >=3.10 standard library only. No floating point, network or optimizer.
This proves the finite assertions and the finite premise of the stated global
integer inequality. It is NOT a proof-assistant check of the Hodge arguments.
Run from any directory: python checks/verify.py --out results/verification.json
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction as Q
from functools import reduce
import hashlib, heapq, itertools, json, math, platform, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
M = 210
SOURCE = (3,60,72,126,183,186)
TARGET = (2,9,129,142,168,180)
DUAL_NUM = (31,87,57,101,84,60)
DUAL_DEN = 420


def compositions(total: int, length: int):
    if length == 1:
        yield (total,)
        return
    for first in range(total+1):
        for tail in compositions(total-first,length-1):
            yield (first,)+tail


def orbit(m: int, a: tuple[int, ...]):
    return sorted({tuple(t*x % m for x in a)
                   for t in range(1,m) if math.gcd(t,m)==1})


def balanced(m: int, a: tuple[int, ...]) -> bool:
    return (len(a)%2==0 and all(0<x<m for x in a)
            and all(sum(b)==len(a)*m//2 for b in orbit(m,a)))


def shortest_positive_return(m: int, a: tuple[int, ...], costs: tuple[int, ...]):
    """Dijkstra on residue states, excluding the empty walk.

Every zero-sum nonnegative integer vector is the incidence vector of a
nonempty return walk. Costs are positive, so a shortest return exists.
"""
    inf=10**100
    dist=[inf]*m
    dist[0]=0
    pq=[(0,0)]
    while pq:
        cost,r=heapq.heappop(pq)
        if cost!=dist[r]:continue
        for ai,ci in zip(a,costs):
            s=(r+ai)%m
            nc=cost+ci
            if nc<dist[s]:
                dist[s]=nc
                heapq.heappush(pq,(nc,s))
    best=min(costs[i]+dist[(-a[i])%m] for i in range(len(a)))
    return best,dist


def run():
    t0=time.perf_counter()
    checks=[]
    def check(name, condition, detail=None):
        entry={'name':name,'pass':bool(condition),'detail':detail}
        checks.append(entry)
        if not condition:raise AssertionError(entry)
    data=json.loads((ROOT/'results/transfer210.json').read_text())
    cert=data['certificate']
    check('source_matches_frozen_predecessor',tuple(data['source'])==SOURCE)
    check('target_matches_frozen_witness',tuple(data['target'])==TARGET)
    check('source_is_three_times_degree70_packet', SOURCE==tuple(3*x for x in (1,20,24,42,61,62)))
    check('target_full_conductor_210', math.gcd(M,*TARGET)==1)
    check('source_conductor_70', M//math.gcd(M,*SOURCE)==70)
    os,ot=orbit(M,SOURCE),orbit(M,TARGET)
    check('source_orbit_dimension_24',len(os)==24)
    check('target_orbit_dimension_48',len(ot)==48)
    check('source_all_middle_balanced',balanced(M,SOURCE))
    check('target_all_middle_balanced',balanced(M,TARGET))
    check('source_and_target_orbits_disjoint',not(set(os)&set(ot)))
    check('fourteen_signed_generators',len(cert)==14 and all(abs(r['coefficient'])==1 for r in cert))
    signed=Counter()
    left=list(TARGET)
    right=list(SOURCE)
    negative=[]
    for row in cert:
        packet=tuple(row['packet']); coeff=row['coefficient']
        for x in packet:signed[x]+=coeff
        check('balanced_'+row['type']+'_'+str(packet),balanced(M,packet))
        if coeff<0:
            left.extend(packet);negative.extend(packet)
        else:right.extend(packet)
    diff=Counter(TARGET)
    diff.subtract(Counter(SOURCE))
    check('exact_signed_incidence_identity',all(signed[r]==diff[r] for r in range(1,M)))
    check('thirty_entry_positive_multiset_identity',len(left)==len(right)==30 and Counter(left)==Counter(right))
    check('negative_auxiliary_length_24',len(negative)==24)
    neg_complement=[M-x for x in negative]
    check('complementary_stabilization_54_entries', len(left+neg_complement)==54 and Counter(left+neg_complement)==Counter(right+neg_complement))
    pair_stack=[v for x in negative for v in (x,M-x)]
    check('stabilized_left_is_target_plus_24_tate_pairs',Counter(left+neg_complement)==Counter(list(TARGET)+pair_stack))
    # The four-entry factors use only the Lefschetz (1,1) theorem.
    # The length-six and length-eight factors are deflated Aoki standard cycles.
    s5=next(tuple(r['packet'])for r in cert if r['type']=='standard5')
    s7=next(tuple(r['packet'])for r in cert if r['type']=='standard7')
    check('standard5_deflates_by_six',tuple(x//6 for x in s5)==(5,10,12,19,26,33) and all(x%6==0 for x in s5))
    check('standard7_deflates_by_six',tuple(x//6 for x in s7)==(2,7,12,17,21,22,27,32) and all(x%6==0 for x in s7))
    sigma5=tuple(sorted([5+j*7 for j in range(5)]+[35-5*5]))
    sigma7=tuple(sorted([2+j*5 for j in range(7)]+[35-7*2]))
    check('standard5_exact_sigma_and_admissibility',sigma5==tuple(x//6 for x in s5) and math.gcd(5,7)==1)
    check('standard7_exact_sigma_and_admissibility',sigma7==tuple(x//6 for x in s7) and math.gcd(2,5)==1)

    check('dual_positive_with_sum_one',min(DUAL_NUM)>0 and sum(DUAL_NUM)==DUAL_DEN)
    enumerated=0; invariant=0; minimum=10**20
    # For length >=14, cost >=14*31>420. It remains to enumerate length <=13.
    for degree in range(1,14):
        for v in compositions(degree,6):
            enumerated+=1
            if sum(x*y for x,y in zip(TARGET,v))%M==0:
                invariant+=1
                value=sum(x*y for x,y in zip(DUAL_NUM,v))
                minimum=min(minimum,value)
                if value<DUAL_DEN:raise AssertionError(('dual counterexample',v,value))
    check('all_invariant_columns_length_at_most_13',minimum>=DUAL_DEN,{'all_vectors':enumerated,'invariant_vectors':invariant,'minimum_numerator':minimum})
    check('all_longer_columns_automatically_excluded',14*min(DUAL_NUM)>DUAL_DEN)
    minimum_path, distances=shortest_positive_return(M,TARGET,DUAL_NUM)
    check('independent_shortest_cycle_dual_check',minimum_path==DUAL_DEN,minimum_path)
    check('matching_primal_column_of_ones',sum(TARGET)%M==0 and sum(DUAL_NUM)==DUAL_DEN)

    witnesses=[]
    for m,a,k in [
        (110,(1,24,62,71,81,91),11),
        (110,(1,31,55,71,81,91),11),
        (114,(1,13,43,72,103,110),27),
        (114,(1,13,43,80,102,103),9),
        (114,(1,7,78,79,86,91),3),
        (220,(1,62,111,142,162,182),11),
    ]:
        b=tuple(k*x%m for x in a)
        check('hodge_packet_and_age_one_power_'+str(m)+'_'+str(a),balanced(m,a) and all(0<x<m for x in b) and sum(b)==m and math.gcd(k,m)>1)
        witnesses.append({'m':m,'a':list(a),'multiplier':k,'age_one_character':list(b),'dual_weights':[str(Q(x,m))for x in b]})

    # Finite benchmarks ONLY. The arbitrary-q proof is in PROOF.md.
    ks=[]
    for q in range(6,81):
        a=tuple([1+j*q for j in range(5)]+[5*q-5])
        if not balanced(5*q,a):raise AssertionError(('K5 balance',q))
        eta=[Q(1,q)]*5+[Q(q-5,q)]
        if not(min(eta)>0 and sum(eta)==1):raise AssertionError(('K5 dual',q))
        ks.append(q)
    check('K5_finite_benchmarks_q6_through80',len(ks)==75)
    return {
        'status':'PASS: exact finite certificates; manuscript proof and external dependencies remain separate',
        'created_utc':datetime.now(timezone.utc).isoformat(),
        'python':platform.python_version(),'platform':platform.platform(),
        'arithmetic':'integers and fractions.Fraction; no floating point',
        'runtime_seconds':time.perf_counter()-t0,
        'checks_passed':len(checks),'checks':checks,
        'target_orbit':[list(x)for x in ot],
        'source_orbit':[list(x)for x in os],
        'positive_identity':{'left':left,'right':right},
        'global_dual':{'numerators':DUAL_NUM,'denominator':DUAL_DEN,
                       'enumerated_through_length':13,'minimum_nonzero_cycle_cost':minimum_path,
                       'shortest_residue_costs':distances},
        'age_one_obstructions':witnesses,
        'K5_finite_benchmark_range':{'q_min':6,'q_max':80,'count':75},
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'input_sha256':hashlib.sha256((ROOT/'results/transfer210.json').read_bytes()).hexdigest(),
        'nonclaims':['No Lean verification.','No new equations for representing surfaces.',
                     'No proof of general Hodge conjecture or universal carrier coverage.',
                     'No claim that the auxiliary searches or external censuses are complete.',
                     'No claim of historical novelty.']
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=ROOT/'results/verification.json')
    args=parser.parse_args()
    r=run();args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(r,indent=2)+'\n')
    print(r['status']);print(f"{r['checks_passed']} checks passed in {r['runtime_seconds']:.3f}s")
    print('New full-conductor packet: dimension 48 at degree 210.')
    print('Global direct-matrix obstruction: exact dual optimum 1.')
    print('Output:',args.out)

if __name__=='__main__':main()
