#!/usr/bin/env python3
"""Exact finite prime-field reduct/alien-addition checks (standard Python only).

Not an IUT theta-link implementation.  See notes/BRIDGE_NOTE.md for scope.
"""
import json
from itertools import permutations, product
from math import gcd
from pathlib import Path

PRIMES = (5, 7, 11, 13, 17, 19)


def field_ops(p, k):
    """Power-coordinate transport of addition through x -> x^k."""
    invk = pow(k, -1, p - 1)
    def f(x): return pow(x, k, p)
    def g(x): return pow(x, invk, p)
    def add(x, y): return g((f(x) + f(y)) % p)
    return f, g, add


def check(p):
    units = [k for k in range(1, p) if gcd(k, p-1) == 1]
    distinct_tables = set()
    for k in units:
        f, g, add = field_ops(p, k)
        assert all(g(f(x)) == x and f(g(x)) == x for x in range(p))
        assert all(f(x*y % p) == f(x)*f(y) % p for x,y in product(range(p), repeat=2))
        assert add(0,0) == 0 and f(1) == 1
        assert all(add(x,y) == add(y,x) for x,y in product(range(p), repeat=2))
        assert all(add(0,x) == x and add(x,0) == x for x in range(p))
        assert all(any(add(x,y) == 0 for y in range(p)) for x in range(p))
        assert all(add(add(x,y),z) == add(x,add(y,z))
                   for x,y,z in product(range(p), repeat=3))
        assert all(x*add(y,z) % p == add(x*y % p, x*z % p)
                   for x,y,z in product(range(p), repeat=3))
        assert all(add(x,y)*z % p == add(x*z % p, y*z % p)
                   for x,y,z in product(range(p), repeat=3))
        distinct_tables.add(tuple(add(x,y) for x,y in product(range(p), repeat=2)))
    assert len(distinct_tables) == len(units), (p, len(distinct_tables), len(units))
    f, g, add = field_ops(p, p-2)
    assert f(2) == pow(2,p-2,p)  # Inversion on F_p^*.
    assert f(2) != (f(1)+f(1)) % p
    assert add(1,1) != 2
    return {"prime": p, "multiplicative_monoid_automorphisms": len(units),
            "distinct_pulled_back_additions": len(distinct_tables),
            "ordinary_one_plus_one": 2,
            "inversion_transport_one_plus_one": add(1,1),
            "checked_associativity_and_distributivity": True}


def full_F5_monoid_automorphism_count():
    # All permutations fixing 0,1. Verify multiplicativity (no power-map assumption).
    count = 0
    for perm in permutations((2,3,4)):
        table = [0,1,*perm]
        if all(table[(x*y)%5] == (table[x]*table[y])%5
               for x,y in product(range(5), repeat=2)):
            count += 1
    assert count == 2
    return count


if __name__ == "__main__":
    records = [check(p) for p in PRIMES]
    assert full_F5_monoid_automorphism_count() == 2
    output = {
        "status": "PASS", "scope": "finite arithmetic reduct models, not IUT",
        "primes": records,
        "all_F5_multiplicative_automorphisms": 2,
        "mathematical_lemma": "F_p inverse-map transport is nonadditive for p >= 5",
        "iut_source_instantation": False,
        "iut_iii_corollary_3_12_established": False,
    }
    target = Path(__file__).with_name("finite_results.json")
    target.write_text(json.dumps(output,indent=2,sort_keys=True) + "\n")
    print(json.dumps(output,indent=2))
