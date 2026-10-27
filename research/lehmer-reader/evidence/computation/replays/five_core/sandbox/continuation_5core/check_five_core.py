#!/usr/bin/env python3
"""Exact finite audit of the Han/Macdonald five-core packet continuation.

Universal claim dependencies: Han's t-core Vandermonde identity and the
classical five-core divisor formula. Finite execution does not prove Lehmer.
Run from any directory: python3 check_five_core.py
No randomness, numerical floating-point arithmetic, or external packages.
"""
from __future__ import annotations
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from math import comb, isqrt, prod
from pathlib import Path
import datetime, json, platform, sys, time

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from explore import tau_triangular, product_tau, sigma_primes
from explore_shell import shell, weight, polynomial, val, chi5, PAIRS


def evaluate_mod(coeff: list[int], u: int, modulus: int) -> int:
    answer=0
    for c in reversed(coeff): answer=(answer*u+c)%modulus
    return answer


def derivative_mod(coeff: list[int], u: int, modulus: int) -> int:
    return sum(j*c*pow(u,j-1,modulus) for j,c in enumerate(coeff) if j)%modulus


def lift_simple(coeff: list[int], residue: int, digits: int) -> tuple[int,list[int]]:
    if evaluate_mod(coeff,residue,5) or derivative_mod(coeff,residue,5)==0:
        raise ValueError('Not a simple residual root.')
    u=residue; history=[u]
    for k in range(1,digits):
        step=5**k; modulus=5*step
        candidates=[u+d*step for d in range(5) if evaluate_mod(coeff,u+d*step,modulus)==0]
        if len(candidates)!=1: raise ArithmeticError(('Hensel uniqueness failed',k,candidates))
        u=candidates[0]; history.append(u)
    return u,history


def partitions(n: int, largest: int | None=None):
    if n==0:
        yield (); return
    if largest is None: largest=n
    for first in range(min(n,largest),0,-1):
        for rest in partitions(n-first,first): yield (first,)+rest


def hook_lengths(lam: tuple[int,...]) -> list[int]:
    return [lam[i]-j+sum(row>j for row in lam[i+1:]) for i in range(len(lam)) for j in range(lam[i])]


def core_count_formula(n: int) -> int:
    return sum(chi5(d)*(n//d) for d in range(1,n+1) if n%d==0)


def main() -> None:
    started=datetime.datetime.now(datetime.timezone.utc).isoformat(); t0=time.perf_counter()
    source_paths=[Path(__file__),HERE/'explore_shell.py',HERE.parent/'explore.py']
    before={str(p.relative_to(HERE.parent)):sha256(p.read_bytes()).hexdigest() for p in source_paths}
    selected=[2411,2999,4999,16249,18749]
    limit=2000; maxn=max(selected)
    tau=tau_triangular(maxn)
    assert tau[:129]==product_tau(128)
    assert tau[1:8]==[1,-24,252,-1472,4830,-6048,-16744]
    _,primes=sigma_primes(limit)
    prime_set=set(primes)|set(selected)
    # Independent deterministic primality checks for all selected indices.
    assert all(p>1 and all(p%d for d in range(2,isqrt(p)+1)) for p in prime_set)
    all_indices=sorted(set(range(1,129))|prime_set)
    records=[]; stats=Counter(); saved={}; sample_weights={}
    for n in all_indices:
        vectors=list(shell(n)); assert len(set(vectors))==len(vectors)
        expected_count=core_count_formula(n)
        assert len(vectors)==expected_count
        ws=[]; B=[0]*11
        for v in vectors:
            assert sum(v)==0 and sum(z*z for z in v)==10*n
            assert all(v[i]%5==i for i in range(5))
            w=weight(v); ws.append(w)
            assert w!=0 and w%5==1
            P=polynomial(v)
            assert P[0]==288
            # A second algebraic evaluation, away from the physical value 5.
            c=[(v[i]-i)//5 for i in range(5)]
            assert sum(P[j]*2**j for j in range(11))==prod((i+2*c[i])-(j+2*c[j]) for i,j in PAIRS)
            for j,b in enumerate(P): B[j]+=b
            if n in prime_set and n>20:
                assert w%n!=0
                assert all(0<abs(v[i]-v[j])<n for i,j in PAIRS)
                stats['index_prime_unit_packets']+=1
            stats['packet_polynomial_checks']+=1
        total=sum(ws)
        assert total==tau[n]
        assert sum(b*5**j for j,b in enumerate(B))==288*total
        stats['shell_sum_checks']+=1
        if n in prime_set:
            assert len(vectors)==n+chi5(n)
            stats['prime_shell_count_checks']+=1
            assert (total-n-chi5(n))%5==0
        layers=[j+val(b,5) if b else None for j,b in enumerate(B)]
        mu=min(z for z in layers if z is not None)
        assert all((b*5**j)%(5**mu)==0 for j,b in enumerate(B))
        C=[b*5**j//5**mu for j,b in enumerate(B)]
        assert total!=0  # BOUNDED experimental assertion, not used in the universal lemmas.
        assert val(total,5)==mu+val(sum(C),5)
        if n in [7,19,499,1249,2411,2999,4999,16249,18749]:
            row={'n':n,'shell_count':len(ws),'positive_packets':sum(w>0 for w in ws),
                 'negative_packets':sum(w<0 for w in ws),'tau':total,'v5_tau':val(total,5),
                 'index_prime_valuation':val(total,n) if n in prime_set else None,
                 'B':B,'layer_valuations':layers,'mu':mu,'G_mod5':[z%5 for z in C],
                 'G_at_1_mod25':evaluate_mod(C,1,25),'derivative_at_1_mod5':derivative_mod(C,1,5)}
            if n==499:
                row['simple_roots']={str(e):{'root':lift_simple(C,e,12)[0],
                                           'history':lift_simple(C,e,12)[1]}
                                     for e in range(5) if evaluate_mod(C,e,5)==0 and derivative_mod(C,e,5)!=0}
                assert row['G_mod5']==[2,0,3]+[0]*8 and row['G_at_1_mod25']==10
                assert row['simple_roots']['1']['root']%25==16
            if n==1249:
                assert row['G_mod5']==[0,0,4]+[0]*8 and row['G_at_1_mod25']%5==4
            if n==16249:
                assert row['G_mod5']==[3,0,1,1]+[0]*7
                assert row['G_at_1_mod25']==15 and row['derivative_at_1_mod5']==0
                # Entire-branch proof is in the note. This checks all residues modulo 5^5 in that branch.
                for y in range(5**4):
                    assert evaluate_mod(C,1+5*y,25)==15
                    stats['double_root_branch_checks']+=1
            records.append(row);saved[n]=B
            if n==19:sample_weights[n]=ws
    # Hook formula independent of the lattice encoding at small indices.
    hook_records=[]
    for m in range(25):
        total=Fraction(0); core_count=0
        for lam in partitions(m):
            hooks=hook_lengths(lam)
            if 5 in hooks:
                stats['annihilated_partitions']+=1; continue
            assert all(h%5 for h in hooks)
            w=prod((Fraction(h*h-25,h*h) for h in hooks),start=Fraction(1))
            assert w.denominator==1 and w.numerator%5==1
            total+=w;core_count+=1;stats['surviving_hook_packets']+=1
        assert total==tau[m+1]
        assert core_count==core_count_formula(m+1)
        stats['hook_sum_checks']+=1
        hook_records.append({'partition_size':m,'surviving_cores':core_count,'weighted_sum':int(total)})
    elapsed=time.perf_counter()-t0
    result={'status':'PASS','prime_bound':limit,'selected_primes_beyond_bound':selected,
            'full_small_index_bound':128,'max_index_used':maxn,'counts':dict(stats),'selected':records,
            'p19_weights':sample_weights[19],'hook_checks':hook_records,'runtime_seconds':elapsed,
            'non_claims':['Not a proof of Lehmer nonvanishing for all primes.',
                          'The prime-indexed family is not assumed 5-adically analytic in its index.',
                          'A fixed polynomial degree does not bound the valuation of its value at 1.',
                          'No Lean compilation or historical-priority claim.']}
    (HERE/'RESULTS.json').write_text(json.dumps(result,indent=2)+'\n')
    after={str(p.relative_to(HERE.parent)):sha256(p.read_bytes()).hexdigest() for p in source_paths}
    assert before==after
    manifest={'schema_version':1,'claim_id':'LEHMER-5CORE-EXACT-PACKETS',
              'repository':{'commit':'not a git repository; input hashes recorded','dirty':True},
              'command':'python3 continuation_5core/check_five_core.py',
              'environment':{'software':[sys.version,platform.python_implementation()],
                             'hardware':platform.platform()},
              'mathematics':{'assertion_tested':'Exact shell sums, five-adic packet polynomials, and two root-branch certificates.',
                             'coefficient_domain':'integers and rational Fractions, finite rings Z/5^kZ',
                             'conventions':'vi=i mod 5, sum vi=0, squared norm=10*n, Vandermonde/288=tau packet',
                             'inputs':list(before.keys()),'bounds':{'all_primes_through':limit,'all_indices_through':128,
                                    'selected_primes':selected,'hook_partition_size_max':24,'root_digits':12},
                             'non_claims':result['non_claims']},
              'randomness':{'used':False,'generator':'none','seed':None},
              'run':{'started_at':started,'runtime_seconds':elapsed,'exit_status':0},
              'input_hashes_before':before,'input_hashes_after':after,
              'outputs':[{'path':'continuation_5core/RESULTS.json','sha256':sha256((HERE/'RESULTS.json').read_bytes()).hexdigest()}],
              'checks':dict(stats),'result':'PASS for the stated finite assertions',
              'residual_risks':['External classical identities are dependencies, not established by bounded tests.',
                                'Scripts share the Python integer runtime; the independent formulas differ mathematically.',
                                'The manifest validator was not run in this environment.']}
    (HERE/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'counts':dict(stats),'runtime_seconds':elapsed,
                      'selected_summary':[{k:r[k] for k in ['n','shell_count','v5_tau','mu','G_at_1_mod25']}
                                          for r in records]},indent=2))

if __name__=='__main__': main()
