"""Exact finite audits for a task-indexed representation calculus.

No theorem prover is called. Complete finite transition tables certify their
all-word quotient property by stable partition refinement. Other experiments
audit the stated bounded instances, not a universal learned discovery system.
Run from the project root: python checks/audit_core.py
"""
from __future__ import annotations
from collections import Counter, deque
from itertools import product
from math import comb, isqrt
from pathlib import Path
import json
import random

ROOT = Path(__file__).resolve().parents[1]
COUNTS: Counter[str] = Counter()


def check(condition: bool, label: str) -> None:
    COUNTS[label] += 1
    if not condition:
        raise AssertionError(label)


def quotient(states: tuple[tuple[int, ...], ...], transitions, observe):
    """Coarsest output-respecting congruence of a complete finite system."""
    def relabel(signatures):
        labels = {}
        return {s: labels.setdefault(signatures[s], len(labels)) for s in states}
    blocks = relabel({s: observe(s) for s in states})
    sizes = [len(set(blocks.values()))]
    while True:
        new = relabel({s: (blocks[s], tuple(blocks[t(s)] for t in transitions))
                       for s in states})
        # This update refines the preceding partition. Equal cardinality means
        # equality as a partition, even if labels were assigned differently.
        count = len(set(new.values()))
        if count == sizes[-1]:
            blocks = new
            break
        check(count > sizes[-1], 'quotient_strict_refinement')
        sizes.append(count)
        blocks = new
    for s in states:
        for t in states:
            if blocks[s] == blocks[t]:
                check(observe(s) == observe(t), 'quotient_output_certificate')
                for action in transitions:
                    check(blocks[action(s)] == blocks[action(t)],
                          'quotient_transition_certificate')
    return blocks, sizes


def first_witness(left, right, transitions, observe):
    """Breadth-first distinguishing word, or None if the pair is equivalent."""
    queue = deque([(left, right, ())])
    seen = {(left, right)}
    while queue:
        a, b, word = queue.popleft()
        if observe(a) != observe(b):
            return list(word)
        for d, action in enumerate(transitions):
            pair = action(a), action(b)
            if pair not in seen:
                seen.add(pair)
                queue.append((*pair, word + (d,)))
    return None


def audit_observations():
    states = tuple(product(range(4), repeat=3))
    step = lambda s: ((s[0] + s[1]) % 4, s[1], s[2])
    swap = lambda s: (s[2], s[1], s[0])
    observe = lambda s: s[0]
    before, sizes0 = quotient(states, (step,), observe)
    after, sizes1 = quotient(states, (step, swap), observe)
    for a in states:
        for b in states:
            check((before[a] == before[b]) == (a[:2] == b[:2]),
                  'original_profile_pair_equivalence')
            check((after[a] == after[b]) == (a == b),
                  'enlarged_profile_pair_equivalence')
    w1 = first_witness((0, 0, 0), (0, 1, 0), (step,), observe)
    w2 = first_witness((0, 0, 0), (0, 0, 1), (step, swap), observe)
    check(w1 == [0] and w2 == [1], 'shortest_distinguishing_examples')
    return {'admissible_state_count': len(states),
            'original_partition_history': sizes0,
            'expanded_partition_history': sizes1,
            'current_output_only_not_sufficient_witness': w1,
            'new_operation_invalidates_old_quotient_witness': w2,
            'scope': 'All 64 admissible states, not only an orbit of one fixed initial state.'}


def mm(a, b, mod):
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(len(b))) % mod
                       for j in range(len(b[0]))) for i in range(len(a)))


def add(a, b, mod):
    return tuple(tuple((x+y) % mod for x,y in zip(ar,br)) for ar,br in zip(a,b))


def sub(a, b, mod):
    return tuple(tuple((x-y) % mod for x,y in zip(ar,br)) for ar,br in zip(a,b))


def audit_composition():
    rng = random.Random(20260920)
    for mod in (4, 8, 9, 25):
        for _ in range(100):
            mats = [tuple(tuple(rng.randrange(mod) for _ in range(2)) for _ in range(2))
                    for _ in range(5)]
            a, b, c, q, v = mats
            delta_q = sub(mm(q,a,mod), mm(b,q,mod), mod)
            delta_v = sub(mm(v,b,mod), mm(c,v,mod), mod)
            lhs = sub(mm(mm(v,q,mod),a,mod),mm(c,mm(v,q,mod),mod),mod)
            rhs = add(mm(v,delta_q,mod),mm(delta_v,q,mod),mod)
            check(lhs == rhs, 'transport_residual_composition')
    return {'moduli':[4,8,9,25], 'matrix_shape':[2,2], 'trials_per_modulus':100}


def polynomial_value(coefficients, x):
    return sum(c*x**j for j,c in enumerate(coefficients))


def audit_lifting():
    root_cases = 0
    for p in (2,3,5):
        for r in (1,2,3):
            lower, upper = p**r, p**(r+1)
            for coeffs in product(range(-2,3), repeat=3):
                for x in range(lower):
                    value = polynomial_value(coeffs,x)
                    if value % lower:
                        continue
                    root_cases += 1
                    residual = (value//lower) % p
                    jac = (coeffs[1]+2*coeffs[2]*x) % p
                    predicted = [d for d in range(p) if (residual+jac*d) % p == 0]
                    actual = [d for d in range(p)
                              if polynomial_value(coeffs,x+lower*d) % upper == 0]
                    check(predicted == actual, 'jacobian_lift_fiber_equality')
                    obstruction = residual if jac == 0 else 0
                    check((obstruction == 0) == bool(actual), 'cokernel_zero_iff_lift')
                    for eta in range(p):
                        changed = polynomial_value(coeffs,x+lower*eta)//lower % p
                        check((changed-residual-jac*eta) % p == 0,
                              'lift_representative_residual_change')
                        changed_obstruction = changed if jac == 0 else 0
                        check(changed_obstruction == obstruction,
                              'lift_obstruction_representative_invariance')
    return {'primes':[2,3,5], 'precisions':[1,2,3],
            'polynomials':'Every c0+c1*x+c2*x^2 with cj in {-2,-1,0,1,2}.',
            'lower_roots_checked':root_cases,
            'example_nonliftable':{'polynomial':[1,0,1],'p':2,'r':1,'x':1,
                                   'residual':1,'jacobian':0,'lifts':[]}}


def raw_binary_action(n, digit):
    """Independent closed binomial expansion of Lambda_d(G*x^n)/G, G=F_2^3."""
    N = n+3
    out = [0]*(N+1)
    for a in range((N-digit)//2+1):
        for t in range(a+1):
            out[N-a+t] += comb(N,2*a+digit)*comb(a,t)*(-1)**(a-t)
    return out


def audit_relation_discovery():
    degrees = (0,2,3,4,5,6)
    weights = (0,0,0,1,4,5)
    moduli = [2**(6-w) for w in weights]
    mats=[]
    for d in (0,1):
        matrix=[[0]*6 for _ in degrees]
        for k,(n,w) in enumerate(zip(degrees,weights)):
            raw = raw_binary_action(n,d)
            full = [2**w*c for c in raw]
            check(all(c%64 == 0 for j,c in enumerate(full) if j not in degrees),
                  'binary_envelope_tail_vanishes')
            psi = 16*(full[4] if len(full)>4 else 0)+(full[6] if len(full)>6 else 0)
            check(psi%64 == 0, 'binary_envelope_image_obstruction')
            for i,(j,wi) in enumerate(zip(degrees,weights)):
                value=full[j] if j<len(full) else 0
                check(value % 2**wi == 0, 'binary_normalization_integral')
                matrix[i][k] = (value//2**wi) % moduli[i]
                check(matrix[i][k]*moduli[k] % moduli[i] == 0,
                      'binary_mixed_precision_relation_preserved')
        mats.append(matrix)
    annihilators=[]
    # Search all finite F2 linear predicates; the desired relation is NOT an
    # input to the search. Require it to kill the seed and every digit image.
    for lam in product(range(2),repeat=6):
        valid=lam[0] == 0 and all(
            sum(lam[i]*T[i][j] for i in range(6))%2 == 0
            for T in mats for j in range(6))
        if valid:
            annihilators.append(list(lam))
    known = [0,0,0,1,0,1]
    check(known in annihilators, 'known_relation_rediscovered_without_search_hint')
    check((16*0+32)%64 != 0, 'missing_atom_counterexample')
    # Relation-preserving coupled direction vs its forbidden separate component.
    check((16*2+32)%64 == 0, 'coupled_atom_passes')
    return {'precision':6, 'degrees':degrees, 'weights':weights,
            'mixed_moduli':moduli, 'digit_matrices':mats,
            'exhaustive_predicate_candidates':64,
            'all_seed_and_image_annihilators':annihilators,
            'recovered_relation':'a4+a6=0 mod 2; equivalently 16*c4+c6=0 mod 64',
            'claim_boundary':'Recovers a known Block15 invariant. Does not prove all-precision exact orbit classification.'}


def binary_spectrum(r):
    exponents=[0,0]
    for k in range(1,isqrt(r)+2):
        exponents.extend((k*k-1,k*k+k+1))
    return sorted(s for s in exponents if s<r)


def audit_precision_information():
    previous=0
    rows=[]
    for r in range(1,1025):
        spec=binary_spectrum(r)
        length=sum(r-s for s in spec)
        check(length-previous == len(spec),'module_length_increment_equals_generator_count')
        previous=length
        if r in (4,8,16,64,128,512,1024):
            rows.append({'precision':r,'minimum_free_coordinates':len(spec),
                         'bits_for_arbitrary_module_element':length,
                         'bits_in_full_free_coordinate_array':r*len(spec)})
    return {'rows':rows,'range':'r=1..1024',
            'boundary':'Not minimal DFA memory, not a lower bound for arbitrary algorithms.'}


def main():
    result={'status':'PASS', 'evidence':'exact finite execution; universal arguments in FORMAL_NOTE.md; no new Lean build',
            'observations':audit_observations(),
            'transport':audit_composition(),
            'polynomial_lifting':audit_lifting(),
            'relation_discovery':audit_relation_discovery(),
            'precision_information':audit_precision_information()}
    result['check_counts']=dict(sorted(COUNTS.items()))
    (ROOT/'results').mkdir(exist_ok=True)
    (ROOT/'results/AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':'PASS','checks':sum(COUNTS.values()),
                      'quotient_histories':[result['observations']['original_partition_history'],
                                           result['observations']['expanded_partition_history']],
                      'recovered_relations':result['relation_discovery']['all_seed_and_image_annihilators'],
                      'lower_roots':result['polynomial_lifting']['lower_roots_checked']},indent=2))

if __name__=='__main__':
    main()
