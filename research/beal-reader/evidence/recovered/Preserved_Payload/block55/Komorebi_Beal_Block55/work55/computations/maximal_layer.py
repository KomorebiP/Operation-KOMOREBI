#!/usr/bin/env python3
"""Exact maximal-order Kummer/reciprocity test, Beal Block55.
A pass excludes the actual diagonal correction only under the written
geometric and support hypotheses. A surviving vector is NOT a Frey solution.
Python 3.10+, standard library. No prime-size bound on the mathematical lemma.
"""
from __future__ import annotations
import argparse
import itertools
import json
from pathlib import Path
from inherited_reciprocity_checks import build, kernel, rref, require

UNIVERSE = [97,197,293,491,587,883,1373,1471,1567,1667]
FIVE_PRIME_CLASS = [197,491,883,1471,1667]

def restricted(matrix, indices):
    return [[row[i] % 7 for i in indices] for row in matrix]

def rank(matrix):
    return len(rref(matrix)[1])

def directions():
    return [(u,r,1) for u in range(7) for r in range(1,7)]

def zero_set(kummer, alpha):
    return tuple(i for i,row in enumerate(kummer)
                 if sum(a*b for a,b in zip(row,alpha)) % 7 == 0)

def residue_data(qs):
    rows, places, ineligible, _ = build(qs)
    high = [p for p in places if p['h'] >= 2]
    M = [[p['logs'][name] % 7 for p in high] for name in rows]
    K = [[p['logs'][name] % 7 for name in ('phi','3','sqrt5')] for p in high]
    return rows, high, ineligible, M, K

def test_support(qs):
    rows, ps, excluded, M, K = residue_data(qs)
    tests=[]
    for a in directions():
        z=zero_set(K,a); B=restricted(M,z); basis=kernel(B)
        tests.append({'alpha':list(a),'zero_indices':list(z),'rank':rank(B),
                      'nullity':len(basis),'kernel_basis':basis})
    return {'prime_support_input':sorted(qs),'rows':rows,'high_places':ps,
            'matrix_mod7':M,'kummer_rows_mod7':K,
            'all_42_tests_injective':all(t['nullity']==0 for t in tests),
            'directions_tested':42,'tests':tests,
            'interpretation':'Necessary top-layer compatibility only; a surviving vector is not a Frey representation'}

def signed_determinant(a):
    n=len(a)
    out=0
    for sigma in itertools.permutations(range(n)):
        inversions=sum(sigma[i]>sigma[j] for i in range(n) for j in range(i+1,n))
        term=(-1)**inversions
        for i,j in enumerate(sigma):term*=a[i][j]
        out+=term
    return out

def minor_certificate(data):
    masks={tuple(t['zero_indices']) for t in data['tests']}
    maximal=sorted(z for z in masks if not any(set(z)<set(w) for w in masks))
    out=[];M=data['matrix_mod7']
    for cols in maximal:
        found=False
        for rr in itertools.combinations(range(5),len(cols)):
            d=signed_determinant([[M[i][j] for j in cols] for i in rr])
            if d%7:
                out.append({'columns':list(cols),'rows':list(rr),'determinant_integer':d,'determinant_mod7':d%7})
                found=True;break
        require(found,'no certificate minor for maximal zero set')
    return out

def fixtures():
    rows,ps,excluded,M,K=residue_data(UNIVERSE)
    tests=[(a,zero_set(K,a)) for a in directions()]
    circuits=[]; total_candidates=0; matroid_circuits=0
    # A compatible column circuit has at most five members, as proved in notes.
    for size in range(1,6):
        for c in itertools.combinations(range(len(ps)),size):
            total_candidates+=1
            bas=kernel(restricted(M,c))
            if len(bas)!=1 or not all(bas[0]):continue
            matroid_circuits+=1
            admissible=[list(a) for a,z in tests if set(c)<=set(z)]
            if admissible:
                circuits.append({'indices':list(c),'q_support':sorted({ps[i]['q'] for i in c}),
                                 'kernel_vector':bas[0],'kummer_rank':rank([K[i] for i in c]),
                                 'admissible_F7_alphas':admissible})
    minbad=sorted({tuple(c['q_support']) for c in circuits
                    if not any(set(d['q_support'])<set(c['q_support']) for d in circuits)},key=lambda s:(len(s),s))
    good=[]; classified=[]
    for mask in range(1<<len(UNIVERSE)):
        qs=[q for i,q in enumerate(UNIVERSE) if mask>>i&1]
        ix={i for i,p in enumerate(ps) if p['q'] in qs}
        failures=[]
        for a,z in tests:
            selected=sorted(ix.intersection(z));B=restricted(M,selected)
            if rank(B)<len(selected):failures.append(list(a))
        passed=not failures
        by_circuit=not any(set(c)<=set(qs) for c in minbad)
        require(passed==by_circuit,'rank test and circuit characterization disagree')
        if passed:good.append(qs)
        classified.append({'mask':mask,'prime_support':qs,'criterion_passed':passed,
                           'surviving_F7_directions':failures})
    maximal_good=[s for s in good if not any(set(s)<set(t) for t in good)]
    primary_class=test_support(FIVE_PRIME_CLASS)
    require(primary_class['all_42_tests_injective'],'five-prime class failed')
    primary_class['maximal_zero_set_minor_certificates']=minor_certificate(primary_class)
    original=test_support([491,1471])
    require(original['all_42_tests_injective'],'predecessor support must pass new all-depth criterion')
    survivor=test_support([97,293])
    require(not survivor['all_42_tests_injective'],'negative control was incorrectly excluded')
    retained=next(t for t in survivor['tests'] if t['alpha']==[0,1,1])
    require(retained['kernel_basis']==[[6,1]],'surviving two-place line changed')
    # Complete F49 normalization. alpha=(u,r,1); write u,r in basis(1,phi).
    # Compare only zero masks, an exact test of the descent-free reduction.
    extensions=0; non_F7=0; zero_masks={}
    for u0,u1,r0,r1 in itertools.product(range(7),repeat=4):
        if (r0,r1)==(0,0):continue
        z=tuple(i for i,l in enumerate(K)
            if (l[0]*u0+l[1]*r0+l[2])%7==0 and (l[0]*u1+l[1]*r1)%7==0)
        c=0 if r0 else 1
        a=((u0+c*u1)%7,(r0+c*r1)%7,1)
        require(a[1]!=0 and set(z)<=set(zero_set(K,a)), 'F49-to-F7 monotonic reduction failed')
        # An independent basis extension test: rank over F49 equals rank over F7
        # because all minors lie in the prime subfield. It is the zero set
        # reduction, not a claim that the ACTUAL coefficients lie in F7.
        extensions+=1;non_F7+=int(u1!=0 or r1!=0)
        zero_masks[z]=zero_masks.get(z,0)+1
    require(extensions==2352 and non_F7==2310,'normalization coverage')
    # High h cannot be discarded. This fixture contains the inert h=3 prime1373.
    require(next(p['h'] for p in ps if p['q']==1373)==3,'missing h3 regime')
    result={'status':'PASS','contract':'Exact finite criterion, conditional arithmetic applications; no global prime bound',
      'arithmetic':'F7 linear algebra and exact phi-basis residue fields',
      'universe':UNIVERSE,'rows':rows,'places':ps,'matrix_mod7':M,'kummer_rows_mod7':K,
      'candidate_subsets_of_ideals_size_at_most_5':total_candidates,
      'matroid_circuits_size_at_most_5':matroid_circuits,
      'compatible_circuits':circuits,'minimal_surviving_rational_supports':[list(s) for s in minbad],
      'maximal_criterion_pass_supports':maximal_good,
      'classified_prime_subsets':len(classified),'criterion_pass_count':len(good),
      'criterion_survivor_count':len(classified)-len(good),'classification':classified,
      'complete_F49_directions':extensions,'nonprimefield_normalized_directions':non_F7,
      'distinct_F49_zero_masks':len(zero_masks),
      'five_prime_class':primary_class,'block54_four_place_class':original,
      'two_inert_place_survivor':survivor,
      'nonclaims':['No F7 descent of the actual Kummer class','No automatic beta vanishing',
                  'No Frey realization of a surviving line','No bounded prime support for arbitrary C']}
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',required=True,type=Path)
    p.add_argument('--primes',type=int,nargs='+',help='Optional explicit rational support to test instead of release fixtures')
    a=p.parse_args()
    result=test_support(a.primes) if a.primes is not None else fixtures()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    if a.primes is None:
        print(json.dumps({k:result[k] for k in ('status','classified_prime_subsets','criterion_pass_count','criterion_survivor_count','maximal_criterion_pass_supports','minimal_surviving_rational_supports','complete_F49_directions')},indent=2))
    else: print(json.dumps({'all_42_tests_injective':result['all_42_tests_injective'],'high_places':len(result['high_places']),'directions_tested':42}))

if __name__=='__main__':main()
