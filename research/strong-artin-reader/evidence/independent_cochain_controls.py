#!/usr/bin/env python3
"""Direct normalized C3 cochain calculation and exact dual-syzygy examples."""
from itertools import product
from pathlib import Path
import json


def rank(rows, p):
    a = [[x % p for x in row] for row in rows]
    r = 0
    for j in range(len(a[0])):
        pivot = next((i for i in range(r, len(a)) if a[i][j]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        scale = pow(a[r][j], -1, p)
        a[r] = [x*scale % p for x in a[r]]
        for i in range(len(a)):
            if i != r:
                scale = a[i][j]
                a[i] = [(x-scale*y) % p for x, y in zip(a[i], a[r])]
        r += 1
    return r


def main():
    pairs = list(product((1, 2), repeat=2))
    triples = list(product(range(3), repeat=3))
    def one(b, g):
        return 0 if not g else b[g-1]
    def two(c, g, h):
        return 0 if not g or not h else c[pairs.index((g, h))]
    def d1(b):
        return tuple((one(b, h)-one(b, (g+h) % 3)+one(b, g)) % 3 for g, h in pairs)
    def d2(c):
        return tuple((two(c, h, k)-two(c, (g+h) % 3, k)+two(c, g, (h+k) % 3)-two(c, g, h)) % 3 for g, h, k in triples)
    boundaries = {d1(b) for b in product(range(3), repeat=2)}
    cocycles = {c for c in product(range(3), repeat=4) if not any(d2(c))}
    assert len(boundaries) == 3 and len(cocycles) == 9
    assert boundaries <= cocycles
    carry = tuple(int(g+h >= 3) for g, h in pairs)
    assert carry in cocycles and carry not in boundaries
    delta1 = [d1(tuple(int(i == j) for i in range(2))) for j in range(2)]
    delta2 = [d2(tuple(int(i == j) for i in range(4))) for j in range(4)]
    assert rank(delta1, 3) == 1 and rank(delta2, 3) == 2
    # Actual scalar section in Z/27, with kernel coordinates x -> x/9 mod3.
    lifts = [1, 4, 16]
    actual = tuple(((lifts[g]*lifts[h]*pow(lifts[(g+h) % 3], -1, 27)-1) % 27)//9 for g, h in pairs)
    assert actual == carry
    syzygies = []
    for p in (2, 3, 5):
        image = {(u, v, (u+v) % p) for u, v in product(range(p), repeat=2)}
        compatible = {w for w in product(range(p), repeat=3) if (w[2]-w[0]-w[1]) % p == 0}
        assert image == compatible
        assert (0, 0, 1) not in image
        augmented = {(u, v, (u+v+t) % p) for u, v, t in product(range(p), repeat=3)}
        assert len(augmented) == p**3
        syzygies.append(dict(p=p, image_size=len(image), augmented_image_size=len(augmented), rejected_error=[0, 0, 1]))
    result = dict(status="PASS", cyclic_C3_F3=dict(normalized_one_cochains=9, normalized_two_cochains=81,
                    cocycles=len(cocycles), coboundaries=len(boundaries), H2_dimension=1,
                    delta1_rank=1, delta2_rank=2, carry_cocycle=list(carry), actual_scalar_defect=list(actual)),
                  syzygy_controls=syzygies,
                  non_claims=["No vanishing in an arithmetic deformation complex", "No global Galois realization"])
    Path("evidence/independent_cochain_run/results.json").write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
