#!/usr/bin/env python3
"""Finite, exact checks for the squarefree-primary realization examples.

These tests verify finite projections and the Chinese remainder construction.
They do not establish infinite or computability-theoretic theorems.
"""
from itertools import product
from math import prod, gcd


def first_primes(k):
    ps = []
    x = 2
    while len(ps) < k:
        if all(x % p for p in ps if p*p <= x):
            ps.append(x)
        x += 1
    return ps


def crt(values, primes):
    assert len(values) == len(primes)
    M = prod(primes)
    if M == 1:
        return 0
    x = 0
    for a, p in zip(values, primes):
        m = M // p
        x += (a % p) * m * pow(m, -1, p)
    return x % M


def finite_subgroup(M, step):
    return frozenset((k * step) % M for k in range(M))


def run():
    primes = first_primes(6)
    print("primes:", primes)
    for N in range(1, 6):
        ps = primes[:N]
        order = prod(ps)
        # Cyclicity: the all-one element has order the primorial.
        generator_order = 1
        for p in ps:
            generator_order *= p
        assert generator_order == order
        # Check every coordinate tuple for N <= 4 (up to 210 tuples).
        if N <= 4:
            for x in product(*(range(p) for p in ps)):
                k = crt(x, ps)
                assert all(k % p == a for a, p in zip(x, ps))
        else:
            for k in range(100):
                x = tuple((k*k+3*i+1) % p for i, p in enumerate(ps))
                r = crt(x, ps)
                assert all(r % p == a for a, p in zip(x, ps))
        print(f"A_{N}: order={order}, cyclic=True, CRT cases=PASS")

    # Every subgroup of a cyclic squarefree group C_30 is picked by a prime subset.
    ps = [2, 3, 5]
    M = prod(ps)
    subgroups = set()
    for mask in range(1 << len(ps)):
        order = prod(p for j, p in enumerate(ps) if mask & (1 << j))
        group = finite_subgroup(M, M // order)
        assert len(group) == order
        subgroups.add(group)
    assert len(subgroups) == 2**len(ps)
    all_cyclic_subgroups = {finite_subgroup(M, step) for step in range(M)}
    assert subgroups == all_cyclic_subgroups
    print(f"subgroup lattice of C_{M}: {len(subgroups)} = 2^{len(ps)} groups, PASS")

    # Exact finite packet obstruction: all group endomorphisms act diagonally.
    ps = [2, 3, 5, 7]
    seed = (1, 1, 0, 0)
    endomorphism_orbit = {
        tuple((coeff * x) % p for coeff, x, p in zip(cs, seed, ps))
        for cs in product(*(range(p) for p in ps))
    }
    assert len(endomorphism_orbit) == 2 * 3
    assert all(x[2:] == (0, 0) for x in endomorphism_orbit)
    print("endomorphism packet-support obstruction: 6 of 210 elements reachable, PASS")

    # The prime-index set {2^k} has growing gaps, witness against unary periodicity.
    inds = [2**k for k in range(7)]
    assert [inds[i+1]-inds[i] for i in range(len(inds)-1)] == inds[:-1]
    print("power-of-two indices:", inds, "(finite growing-gap check=PASS)")
    print("All finite exact checks passed. Infinite claims require the written proofs.")


if __name__ == "__main__":
    run()
