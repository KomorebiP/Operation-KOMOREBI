#!/usr/bin/env python3
"""Exact finite checks for the bad-seven torus calculation; no Galois oracle."""
import itertools
import json
from pathlib import Path

P = 7
ZERO, ONE, R = (0, 0), (1, 0), (0, 1)


def add(a, b):
    return tuple((x + y) % P for x, y in zip(a, b))


def mul(a, b):
    # F_49 = F_7[r]/(r^2+r-1).
    x, y = a
    z, w = b
    return ((x*z+y*w) % P, (x*w+y*z-y*w) % P)


def power(a, n):
    out = ONE
    while n:
        if n & 1:
            out = mul(out, a)
        a = mul(a, a)
        n //= 2
    return out


def poly_mul(a, b):
    out = [0] * (len(a)+len(b)-1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i+j] += x*y
    return out


def main():
    field = list(itertools.product(range(P), repeat=2))
    assert all(power(a, 48) == ONE for a in field if a != ZERO)
    roots = [a for a in field if add(add(mul(a, a), a), (-1, 0)) == ZERO]
    assert roots == [(0, 1), (6, 6)]
    squares = {mul(a, a) for a in field}
    node_data = []
    for r in roots:
        h = add((6, 0), mul((-3, 0), r))
        assert power(r, 49) == r
        assert power(h, 8) == (3, 0)
        assert power(h, 24) == (6, 0)
        assert h not in squares
        node_data.append({"r": r, "h(r)": h, "norm": power(h, 8),
                          "euler_test": power(h, 24), "is_square": False})
    polynomial = poly_mul(poly_mul([-1, 1, 1], [-1, 1, 1]), [5, -2, 1])
    assert polynomial == [5, -12, 0, 10, 0, 0, 1]
    pairs = []
    for A, B in itertools.product(range(1, 7), repeat=2):
        if (A**3+B**5) % 7:
            continue
        u = A*A*pow(B, -3, 7) % 7
        assert pow(u, 3, 7) == B
        assert pow(u, 5, 7) == -A % 7
        assert A**3*B % 7 == 6
        scaled = [5*B*B, 12*A*u, 0, 10*B*u**3, 0, 0, u**6]
        assert [x % 7 for x in scaled] == [u**6*x % 7 for x in polynomial]
        pairs.append([A, B, u])
    assert len(pairs) == 6
    # The unit-Kummer group law uses carry(a,b)=(a+b-(a+b mod 7))/7.
    carry = lambda a, b: (a+b)//7
    for a, b, c in itertools.product(range(7), repeat=3):
        assert carry(a,b)+carry((a+b)%7,c) == carry(b,c)+carry(a,(b+c)%7)
    result = {"verdict": "PASS_EXACT_FINITE_ASSERTIONS", "field": "F7[r]/(r^2+r-1)",
              "nodes": node_data, "normalized_polynomial": polynomial,
              "admissible_nonzero_residue_triples_A_B_u": pairs,
              "carry_cocycle_triples_checked": 343,
              "scope": "Algebra and branch nonsplitting only; uniformization, monodromy, finite-flat descent, and global irreducibility are not computationally proved."}
    out = Path("work48/verification/bad7_run/result.json")
    out.write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
