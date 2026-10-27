#!/usr/bin/env python3
"""Exact, independent controls for the Strong Artin reader set.

This program imports no producer code. It does not prove global automorphy.
"""
from collections import Counter
from fractions import Fraction as Q
from itertools import combinations_with_replacement, permutations, product
from pathlib import Path
import json


def rank_mod(rows, p):
    a = [[x % p for x in row] for row in rows]
    r = 0
    for j in range(len(a[0])):
        pivot = next((i for i in range(r, len(a)) if a[i][j]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        a[r] = [(x * pow(a[r][j], -1, p)) % p for x in a[r]]
        for i in range(len(a)):
            if i != r:
                b = a[i][j]
                a[i] = [(x-b*y) % p for x, y in zip(a[i], a[r])]
        r += 1
    return r


def cyclic_controls():
    pairs = 0
    singleton = full = empty = 0
    for p in (2, 3, 5):
        vectors = list(product(range(3), repeat=p))
        for v, w in product(vectors, repeat=2):
            if sum(v) != sum(w):
                continue
            shifts = [j for j in range(p) if tuple(v[(a-j) % p] for a in range(p)) == w]
            stab = [j for j in range(p) if tuple(v[(a-j) % p] for a in range(p)) == v]
            assert len(shifts) in (0, 1, p)
            if shifts:
                assert set(shifts) == {(shifts[0]+j) % p for j in stab}
            pairs += 1
            if not shifts:
                empty += 1
            elif len(shifts) == 1:
                singleton += 1
            else:
                full += 1
    exact_families = 0
    for p in (2, 3, 5):
        allowed = [set(range(p))]+[{j} for j in range(p)]
        for family in product(allowed, repeat=4):
            pairwise = all(a & b for a, b in combinations_with_replacement(family, 2))
            common = set.intersection(*family)
            assert bool(pairwise) == bool(common)
            exact_families += 1
    coarse = [{0, 1}, {1, 2}, {0, 2}]
    assert all(a & b for a, b in combinations_with_replacement(coarse, 2))
    assert not set.intersection(*coarse)
    return dict(equal_rank_pairs=pairs, empty=empty, singleton=singleton, full=full,
                four_constraint_families=exact_families,
                coarse_pairwise_counterexample=[sorted(s) for s in coarse],
                coarse_sets_not_exact_prime_cyclic_alignment=True)


def cyclo_add(a, b):
    return tuple(x+y for x, y in zip(a, b))


def cyclo_mul(a, b, p):
    # Z[z]/(1+z+...+z^(p-1)), represented in powers 0,...,p-2.
    c = [0] * p
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            c[(i+j) % p] += x*y
    return tuple(c[i]-c[p-1] for i in range(p-1))


def cyclo_root(a, p):
    a %= p
    return tuple(-1 for _ in range(p-1)) if a == p-1 else tuple(int(i == a) for i in range(p-1))


def elementary(exponents, p):
    zero = (0,)*(p-1)
    values = [(1,)+(0,)*(p-2)] + [zero]*len(exponents)
    for i, a in enumerate(exponents):
        for k in range(i+1, 0, -1):
            values[k] = cyclo_add(values[k], cyclo_mul(values[k-1], cyclo_root(a, p), p))
    return values


def coefficient_controls():
    cases = 0
    blind = separated = 0
    for p in (2, 3, 5):
        for n in range(1, 6):
            for exponents in combinations_with_replacement(range(p), n):
                e = elementary(exponents, p)
                active = [k for k in range(1, n+1) if any(e[k])]
                polynomials = []
                for j in range(p):
                    rotated = elementary([(a+j) % p for a in exponents], p)
                    assert all(rotated[k] == cyclo_mul(e[k], cyclo_root(j*k, p), p) for k in range(n+1))
                    polynomials.append(tuple(rotated))
                separator = any(k % p for k in active)
                assert (len(set(polynomials)) == p) == separator
                cases += 1
                separated += separator
                blind += not separator
    assert elementary((0, 1), 2)[1] == (0,)
    return dict(multisets=cases, separated=separated, blind=blind,
                arithmetic="integral prime cyclotomic quotient, no floating point")


def multiply(a, b):
    return tuple(sum(a[2*i+k]*b[2*k+j] for k in range(2)) for i in range(2) for j in range(2))


def group_trace_controls():
    examples = []
    for p in (5, 7, 11):
        # S3 on span(e1-e3,e2-e3), derived directly from permutation vectors.
        group = []
        for perm in permutations(range(3)):
            columns = []
            for source in (0, 1):
                v = [0, 0, 0]
                v[perm[source]] += 1
                v[perm[2]] -= 1
                columns.append(v[:2])
            group.append(tuple(columns[j][i] % p for i in range(2) for j in range(2)))
        assert len(set(group)) == 6
        assert all(tuple(x % p for x in multiply(a, b)) in group for a, b in product(group, repeat=2))
        trace = lambda a: (a[0]+a[3]) % p
        t = len({trace(a) for a in group})
        basis = []
        for a in group:
            if rank_mod(basis+[list(a)], p) > len(basis):
                basis.append(list(a))
        gram = [[trace(multiply(a, b)) for b in basis] for a in basis]
        signatures = {tuple(trace(multiply(a, b)) for b in basis) for a in group}
        assert rank_mod(gram, p) == len(basis) == 4
        assert len(signatures) == 6 <= t**len(basis) <= t**4
        examples.append(dict(group="S3 standard", p=p, image_order=6, trace_alphabet=t, algebra_dimension=4))
    diagonal = [(pow(2, a, 7), 0, 0, pow(4, a, 7)) for a in range(3)]
    signature = [(a[0]+a[3], (2*a[0]+4*a[3]) % 7) for a in diagonal]
    assert len(set(signature)) == 3
    assert {(a[0]+a[3]) % 7 for a in diagonal} == {2, 6}
    examples.append(dict(group="C3 diagonal", p=7, image_order=3, trace_alphabet=2, algebra_dimension=2))
    # Removing semisimplicity: an order-five unipotent group in GL2(F5).
    unipotent = [(1, a, 0, 1) for a in range(5)]
    assert len({(a[0]+a[3]) % 5 for a in unipotent}) == 1
    # Removing p>n: semisimple scalar C2 in GL3(F3), every trace zero.
    assert all(3*scalar % 3 == 0 for scalar in (1, 2))
    return dict(positive_examples=examples,
                semisimplicity_counterexample=dict(p=5, n=2, image_order=5, trace_alphabet=1),
                large_characteristic_counterexample=dict(p=3, n=3, image_order=2, trace_alphabet=1))


def hensel_controls():
    a = (1, 1, 0, 1)
    # Independent entrywise inverse for X -> AX+XA, not generic inversion code.
    b = [[2, 0, -1, 0], [-1, 2, 1, -1], [0, 0, 2, 0], [0, 0, -1, 2]]
    def action(x):
        return (2*x[0]+x[2], x[0]+2*x[1]+x[3], 2*x[2], x[2]+2*x[3])
    for e in range(4):
        v = tuple(int(i == e) for i in range(4))
        bx = tuple(sum(row[i]*v[i] for i in range(4)) for row in b)
        assert action(bx) == tuple(4*x for x in v)
        dx = action(v)
        assert tuple(sum(row[i]*dx[i] for i in range(4)) for row in b) == tuple(4*x for x in v)
    base = multiply(a, a)
    accepted = set()
    images = set()
    for t in product(range(4), repeat=4):
        u = tuple((x+8*y) % 32 for x, y in zip(base, t))
        delta = tuple(x-y for x, y in zip(u, base))
        if all(sum(row[i]*delta[i] for i in range(4)) % 32 == 0 for row in b):
            accepted.add(u)
        f = tuple(x+8*y for x, y in zip(a, t))
        images.add(tuple(x % 32 for x in multiply(f, f)))
    deeper_images = set()
    for t in product(range(8), repeat=4):
        f = tuple(x+8*y for x, y in zip(a, t))
        deeper_images.add(tuple(x % 32 for x in multiply(f, f)))
    assert accepted == images == deeper_images
    f = (1, 1, 8, 1)
    assert multiply(f, f) == (9, 2, 16, 9)
    assert multiply(f, a) != multiply(a, f)
    negative = (9, 2, 0, 1)
    assert negative not in accepted
    scalar_branch = [x for x in range(27) if x % 9 == 4]
    assert all(pow(x, 3, 27) == 10 for x in scalar_branch)
    assert pow(4, 3, 9) == 1 and all(pow(x, 3, 27) != 1 for x in scalar_branch)
    # Singular square derivative at diag(1,-1) annihilates both off-diagonal units.
    center = (1, 0, 0, -1)
    e12 = (0, 1, 0, 0)
    assert tuple(x+y for x, y in zip(multiply(center, e12), multiply(e12, center))) == (0, 0, 0, 0)
    return dict(p=2, d=2, s=2, m=3, horizon=5, modulus=32,
                horizon_corrections=256, deeper_corrections=4096, accepted_targets=len(accepted),
                scaled_inverse=b, noncommuting_root=list(f), root_square=[9, 2, 16, 9],
                rejected_target=list(negative),
                failed_scalar_branch=dict(prefix=4, initial_modulus=9, next_modulus=27, cubes=[10, 10, 10]),
                singular_derivative_counterexample="diag(1,-1), square degree, E12 killed")


def cohomology_controls():
    # Cyclic group formulas over F3 for Ad(diag(1,-1)).
    p = 3
    action = [1, -1, -1, 1]
    answers = []
    for order in (2, 6):
        norm = [sum(pow(t, i, p) for i in range(order)) % p for t in action]
        coboundary_rank = sum((t-1) % p != 0 for t in action)
        cocycle_dimension = sum(t == 0 for t in norm)
        dim = cocycle_dimension-coboundary_rank
        assert dim == (0 if order == 2 else 2)
        answers.append(dict(group=f"C{order}", coefficient="M2(F3)", action="Ad(diag(1,-1))", H1_dimension=dim))
    return dict(cyclic_H1_examples=answers,
                cyclic_H2_trivial_F3_C3_dimension=1,
                genuine_scalar_obstruction="C3 generator 4 mod 9 has no order-three lift mod 27")


def main():
    results = dict(status="PASS", cyclic_alignment=cyclic_controls(),
                   coefficient_rotation=coefficient_controls(), trace_bound=group_trace_controls(),
                   matrix_hensel=hensel_controls(), cyclic_cohomology=cohomology_controls(),
                   non_claims=["No universal arithmetic obstruction vanishing",
                               "No Galois realization of a finite-Satake automorphic packet",
                               "No new Strong Artin case", "No global automorphy proof",
                               "No independent Lean kernel replay"])
    out = Path("evidence/independent_run/results.json")
    out.write_text(json.dumps(results, indent=2)+"\n")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
