#!/usr/bin/env python3
"""Exact controls for actual mixed-characteristic layers and residue Frobenius."""
from itertools import combinations_with_replacement, product
from pathlib import Path
import json


I = (1, 0, 0, 1)


def mul(a, b, q):
    return tuple(sum(a[2*i+k]*b[2*k+j] for k in range(2)) % q for i in range(2) for j in range(2))


def inv(a, q):
    z = pow((a[0]*a[3]-a[1]*a[2]) % q, -1, q)
    return tuple(x*z % q for x in (a[3], -a[1], -a[2], a[0]))


def power(a, d, q):
    b = I
    for _ in range(d):
        b = mul(b, a, q)
    return b


def layers():
    cases = 0
    target_tests = 0
    summaries = []
    for p in (2, 3):
        q = p*p
        corrections = list(product(range(p), repeat=4))
        centers = [a for a in corrections if (a[0]*a[3]-a[1]*a[2]) % p]
        for f in centers:
            fi = inv(f, p)
            for d in range(1, 6):
                base = power(f, d, q)
                bi = inv(base, q)
                def norm(x):
                    y = (0, 0, 0, 0)
                    for _ in range(d):
                        y = tuple((a+b) % p for a, b in zip(y, x))
                        x = mul(mul(f, x, p), fi, p)
                    return y
                expected = {norm(x) for x in corrections}
                image = {power(tuple(a+p*x for a, x in zip(f, v)), d, q) for v in corrections}
                accepted = set()
                for v in corrections:
                    u = tuple((a+p*x) % q for a, x in zip(base, v))
                    normalized = mul(u, bi, q)
                    assert all((a-b) % p == 0 for a, b in zip(normalized, I))
                    e = tuple((a-b)//p % p for a, b in zip(normalized, I))
                    if e in expected:
                        accepted.add(u)
                assert image == accepted
                cases += 1
                target_tests += len(corrections)
        summaries.append(dict(p=p, layer=f"Z/{q} to Z/{p}", centers=len(centers), degrees=[1, 2, 3, 4, 5]))
    return dict(cases=cases, target_tests=target_tests, families=summaries,
                assertion="Normalized actual coefficient mismatch lies in norm image iff original power equation has a root in the prescribed residue fibre")


def frobenius():
    summaries = []
    total = 0
    for p, c, ell in ((2, 1, 1), (3, 1, 0), (5, 2, 0)):
        # Field Fp[z]/(z²+ell*z+c).
        elements = list(product(range(p), repeat=2))
        zero = (0, 0)
        one = (1, 0)
        def add(x, y):
            return ((x[0]+y[0]) % p, (x[1]+y[1]) % p)
        def neg(x):
            return (-x[0] % p, -x[1] % p)
        def times(x, y):
            a, b = x
            d, e = y
            return ((a*d-c*b*e) % p, (a*e+b*d-ell*b*e) % p)
        def exp(x, d):
            y = one
            for _ in range(d):
                y = times(y, x)
            return y
        def polynomial(roots):
            out = [one]
            for root in roots:
                new = [zero]*(len(out)+1)
                for i, a in enumerate(out):
                    new[i] = add(new[i], times(neg(root), a))
                    new[i+1] = add(new[i+1], a)
                out = new
            return out
        assert len({exp(x, p) for x in elements}) == p*p
        assert all(any(times(x, y) == one for y in elements) for x in elements if x != zero)
        count = 0
        for n in range(1, 4):
            for roots in combinations_with_replacement(elements, n):
                actual = polynomial([exp(x, p) for x in roots])
                expected = [exp(a, p) for a in polynomial(roots)]
                assert actual == expected
                count += 1
        summaries.append(dict(p=p, extension_degree=2, modulus=[c, ell, 1], root_multisets=count))
        total += count
    return dict(root_multisets=total, families=summaries,
                assertion="p-power root transform equals coefficientwise Frobenius over nonprime finite residue fields; Frobenius is injective")


def main():
    result = dict(status="PASS", actual_mixed_characteristic_layers=layers(), residue_Frobenius=frobenius(),
                  non_claims=["No arithmetic obstruction vanishing", "No global Galois realization", "No infinite-tower or Strong Artin theorem follows from these finite tests"])
    Path("evidence/independent_layer_run/results.json").write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
