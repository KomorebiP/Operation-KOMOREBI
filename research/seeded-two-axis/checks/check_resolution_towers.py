#!/usr/bin/env python3
"""Exact finite regression for the arithmetic tower and lattice-gluing block.

No randomized cases, numerical tolerances, p-adic floating point, or claims
that a finite bound verifies a limit theorem. The complete quantified results
have separate written proofs. This checks explicit finite models and CRT
certificates, including negative (collapse and loss-of-morphism) fixtures.
"""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
import math
import platform
import sys
import time
from fractions import Fraction
from pathlib import Path
from typing import Iterable


def require(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


def prime_factors(n: int) -> tuple[int, ...]:
    require(n >= 1, 'positive factor input')
    out, p = [], 2
    while p * p <= n:
        if n % p == 0:
            out.append(p)
            while n % p == 0:
                n //= p
        p += 1
    if n > 1:
        out.append(n)
    return tuple(out)


def valuation_int(n: int, p: int) -> int:
    require(n != 0 and p > 1, 'valuation of a nonzero integer')
    n, v = abs(n), 0
    while n % p == 0:
        n //= p
        v += 1
    return v


def valuation_fraction(q: Fraction, p: int) -> int | float:
    if q == 0:
        return float('inf')
    return valuation_int(q.numerator, p) - valuation_int(q.denominator, p)


def crt(residues: Iterable[int], moduli: Iterable[int]) -> int:
    rs, ms = tuple(residues), tuple(moduli)
    require(len(rs) == len(ms), 'CRT arity')
    require(all(m > 1 for m in ms), 'nontrivial CRT moduli')
    require(all(math.gcd(ms[i], ms[j]) == 1 for i in range(len(ms))
                for j in range(i)), 'coprime CRT moduli')
    n = math.prod(ms)
    x = sum(r * (n // m) * pow(n // m, -1, m)
            for r, m in zip(rs, ms)) % n
    require(all(x % m == r % m for r, m in zip(rs, ms)), 'CRT certificate')
    return x


def local_koszul() -> dict:
    # All coefficient pairs in each listed finite local ring, not a sample.
    prime_powers = ((2,1),(2,2),(2,3),(2,4),(3,1),(3,2),(5,1),(5,2))
    pairs = degree_checks = torsion_checks = nilpotence_checks = 0
    for p, n in prime_powers:
        q = p ** n
        for a, b in itertools.product(range(q), repeat=2):
            pairs += 1
            image = {((-b*t) % q, (a*t) % q) for t in range(q)}
            kernel = {(x,y) for x in range(q) for y in range(q)
                      if (a*x+b*y) % q == 0}
            ker_top = {t for t in range(q) if (a*t) % q == 0 and (b*t) % q == 0}
            image_bottom = {(a*x+b*y) % q for x in range(q) for y in range(q)}
            g = math.gcd(q, a, b)
            require(image <= kernel, f'chain condition {q,a,b}')
            require(len(ker_top) == g, f'H^-2 {q,a,b}')
            require(q // len(image_bottom) == g, f'H^0 {q,a,b}')
            require(len(kernel) // len(image) == g*g, f'H^-1 size {q,a,b}')
            degree_checks += 3
            h = valuation_int(g,p) if g > 1 else 0
            for j in range(h+1):
                killed = sum(((p**j*x) % q, (p**j*y) % q) in image for x,y in kernel)
                require(killed % len(image) == 0, 'whole cohomology cosets')
                require(killed // len(image) == p**(2*min(j,h)),
                        f'H^-1 elementary divisors {q,a,b,j}')
                torsion_checks += 1
            if g > 1:
                exponent = (n+h-1)//h
                require(pow(p**h, exponent, q) == 0, 'nilpotent cone witness')
                nilpotence_checks += 1
    return {'rings': [{'p':p,'n':n,'modulus':p**n} for p,n in prime_powers],
            'all_coefficient_pairs':pairs, 'cohomology_degree_checks':degree_checks,
            'middle_cohomology_torsion_checks':torsion_checks,
            'nilpotence_witnesses':nilpotence_checks}


def transitions() -> dict:
    tuples = elements = 0
    for p in (2,3):
        for a in range(1,6):
            for n in range(a,6):
                for m in range(n,9):
                    tuples += 1
                    for x in range(p**a):
                        actual = (p**(m-a)*x) % (p**n)
                        predicted = (p**(n-a)*(p**(m-n)*x % (p**a))) % (p**n)
                        require(actual == predicted, 'annihilator transition')
                        if m-n >= a:
                            require(actual == 0, 'pro-zero bound')
                        elements += 1
    coherence = lost = 0
    for d in (2,6,30):
        for n in range(1,5):
            for m in range(n,6):
                if m > n:
                    require(d**n % d**m != 0 and d**n % d**n == 0, 'map information loss')
                    lost += 1
                for l in range(m,7):
                    for b in range(1,13):
                        require(pow(b,l-n,d**n) ==
                                (pow(b,m-n,d**n)*pow(b,l-m,d**n)) % d**n,
                                'exchange composition')
                        coherence += 1
    return {'annihilator_transition_tuples':tuples,
            'annihilator_elements_checked':elements,
            'weighted_exchange_coherences':coherence,
            'nonzero_maps_lost_by_coarsening':lost,
            'bounds':{'primes':[2,3], 'a':[1,5], 'n':[1,5], 'm':[1,8],
                      'coherence_D':[2,6,30], 'labels':[1,12]}}


def finite_quotients() -> dict:
    projections = idempotents = compatible = label_pairs = 0
    for d in (2,6,10,30):
        ps = prime_factors(d)
        previous = {}
        for n in range(1,5):
            N = d**n
            es = {p:crt([int(p==q) for q in ps], [q**n for q in ps]) for p in ps}
            require(sum(es.values()) % N == 1 % N, 'CRT unit sum')
            for p in ps:
                require(es[p]**2 % N == es[p], 'CRT idempotency')
                for q in ps:
                    if p != q:
                        require(es[p]*es[q] % N == 0, 'CRT orthogonality')
                idempotents += 1
            for mask in range(1 << len(ps)):
                selected = tuple(p for i,p in enumerate(ps) if mask & (1<<i))
                keep = tuple(p for p in ps if p not in selected)
                modulus_keep = math.prod(p**n for p in keep)
                e_selected = sum(es[p] for p in selected) % N
                require(math.gcd(e_selected,N) == modulus_keep, 'projection kernel generator')
                if keep:
                    require(N % modulus_keep == 0, 'surjective quotient projection')
                else:
                    require(modulus_keep == 1, 'zero quotient convention')
                projections += 1
            if n > 1:
                for p in ps:
                    require(es[p] % (d**(n-1)) == previous[p], 'coherent prime idempotents')
                    compatible += 1
            previous = es
            for a,b in itertools.product(range(1,13),repeat=2):
                S = tuple(p for p in ps if a%p==b%p==0)
                keep_mod = math.prod(p**n for p in ps if p not in S)
                require(math.gcd(keep_mod,a,b) == 1, 'retained interactions vanish')
                for p in S:
                    require(math.gcd(p**n,a,b) > 1, 'selected local interaction nonzero')
                label_pairs += 1
    return {'D':[2,6,10,30], 'levels':[1,4], 'all_subsets_tested':projections,
            'prime_idempotents':idempotents, 'idempotent_transition_checks':compatible,
            'positive_label_pair_instances':label_pairs}


def all_subspaces_2(p: int) -> list[frozenset[tuple[int,int]]]:
    zero = frozenset({(0,0)})
    whole = frozenset(itertools.product(range(p),repeat=2))
    spaces = {zero,whole}
    for v in itertools.product(range(p),repeat=2):
        if v != (0,0):
            spaces.add(frozenset(((t*v[0])%p,(t*v[1])%p) for t in range(p)))
    require(len(spaces) == p+3, 'all subspaces of F_p^2')
    return sorted(spaces,key=lambda s:(len(s),sorted(s)))


def mm2(a,b):
    return [[sum(a[i][k]*b[k][j] for k in range(2)) for j in range(2)] for i in range(2)]


def lattice_gluing() -> dict:
    from sympy import Matrix
    from sympy.matrices.normalforms import hermite_normal_form
    family = []
    op_checks = 0
    for h2,h3 in itertools.product(all_subspaces_2(2),all_subspaces_2(3)):
        H = {(x,y) for x,y in itertools.product(range(6),repeat=2)
             if (x%2,y%2) in h2 and (x%3,y%3) in h3}
        require(len(H)==len(h2)*len(h3),'CRT preimage subgroup size')
        columns = [(6,0),(0,6)] + sorted(H)
        mat = Matrix(2,len(columns),lambda i,j:columns[j][i])
        B = hermite_normal_form(mat)
        require(B.shape==(2,2),'full lattice rank')
        b = [[int(B[i,j]) for j in range(2)] for i in range(2)]
        det = b[0][0]*b[1][1]-b[0][1]*b[1][0]
        require(abs(det)==36//len(H),'lattice index')
        image6 = {(sum(b[0][j]*v[j] for j in range(2))%6,
                   sum(b[1][j]*v[j] for j in range(2))%6)
                  for v in itertools.product(range(6),repeat=2)}
        require(image6==H,'HNF basis generates exact glued lattice residues')
        adj = [[b[1][1],-b[0][1]],[-b[1][0],b[0][0]]]
        for entries in itertools.product(range(3),repeat=4):
            f = [list(entries[:2]),list(entries[2:])]
            local = all(all(((f[0][0]*x+f[0][1]*y)%p,
                              (f[1][0]*x+f[1][1]*y)%p) in h for x,y in h)
                        for p,h in ((2,h2),(3,h3)))
            numerator = mm2(adj,mm2(f,b))
            integral = all(numerator[i][j] % det == 0 for i in range(2) for j in range(2))
            require(local == integral,'local operator stability iff global lattice stability')
            op_checks += 1
        family.append({'h2_size':len(h2),'h3_size':len(h3),'basis':b,'index':abs(det)})
    require(len(family)==30,'complete pair family')
    rank1 = 0
    for t2,t3 in itertools.product(range(-2,3),repeat=2):
        generator = Fraction(2)**t2 * Fraction(3)**t3
        for power in range(4):
            for a in range(-30,31):
                v = Fraction(a,6**power)
                local = valuation_fraction(v,2)>=t2 and valuation_fraction(v,3)>=t3
                global_member = (v/generator).denominator == 1
                require(local==global_member,'rank-one local/generic lattice gluing')
                rank1 += 1
    return {'rank_two_all_F2_F3_subspace_pairs':family,
            'integer_operator_tests':op_checks, 'operator_entries':[0,2],
            'rank_one_fraction_membership_tests':rank1,
            'rank_one_exponents':[-2,2], 'rank_one_numerators':[-30,30],
            'rank_one_denominator_powers':[0,3]}


def fracture_principal_parts() -> dict:
    count=0
    for ps in ((2,3),(2,3,5)):
        d=math.prod(ps)
        for N in (1,2):
            mods=[p**N for p in ps]
            for cs in itertools.product(*(range(m) for m in mods)):
                ys=[Fraction(c,p**N) for c,p in zip(cs,ps)]
                residues=[int(y*d**N) % p**N for y,p in zip(ys,ps)]
                z=crt(residues,mods)
                a=Fraction(z,d**N)
                require(all(valuation_fraction(a-y,p)>=0 for y,p in zip(ys,ps)),
                        'arithmetic fracture CRT witness')
                count+=1
    return {'prime_sets':[[2,3],[2,3,5]], 'denominator_exponents':[1,2],
            'all_principal_part_tuples':count}


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=Path('resolution_results.json'))
    args=parser.parse_args()
    started=time.perf_counter()
    results={}
    for name,fun in [('local_koszul',local_koszul),('transitions',transitions),
                     ('finite_quotients',finite_quotients),('lattice_gluing',lattice_gluing),
                     ('fracture_principal_parts',fracture_principal_parts)]:
        results[name]=fun()
        print(f'{name}: PASS',flush=True)
    import sympy
    script=Path(__file__)
    report={'status':'PASS','evidence':'exact finite regression, not a universal or limit proof',
            'arithmetic':'Python integers, Fraction, exhaustive finite residue sets; integer HNF checked by residues/index',
            'python':platform.python_version(),'sympy':sympy.__version__,
            'platform':platform.platform(),'argv':sys.argv,'deterministic':True,'random_seed':None,
            'skipped_cases_in_stated_families':0,'results':results,
            'elapsed_seconds':time.perf_counter()-started,
            'input_sha256':{script.name:hashlib.sha256(script.read_bytes()).hexdigest()},
            'nonclaims':['No Lean compilation','No independent proof review',
                         'No computational proof about all p-adic numbers or infinite limits',
                         'No unrestricted arithmetic or automorphic globalization',
                         'No historical novelty claim']}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='results'},indent=2))


if __name__=='__main__':
    main()
