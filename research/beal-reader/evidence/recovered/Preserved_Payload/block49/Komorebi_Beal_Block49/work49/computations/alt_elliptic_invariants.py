"""Exact identities and bounded residues; no Diophantine search."""
import json
from fractions import Fraction
from pathlib import Path

def add(*polys):
    result = {}
    for poly in polys:
        for monomial, coefficient in poly.items():
            result[monomial] = result.get(monomial, 0) + coefficient
    return {m: c for m, c in result.items() if c}

def scale(poly, n):
    return {m: n * c for m, c in poly.items() if n * c}

def mul(left, right):
    result = {}
    for (i, j), a in left.items():
        for (k, l), b in right.items():
            m = i + k, j + l
            result[m] = result.get(m, 0) + a * b
    return {m: c for m, c in result.items() if c}

def power(poly, n):
    result = {(0, 0): 1}
    for _ in range(n):
        result = mul(result, poly)
    return result

def valuation(n, p):
    assert n
    result = 0
    while n % p == 0:
        result += 1
        n //= p
    return result

A, V = {(1, 0): 1}, {(0, 1): 1}
a1, a3 = scale(A, 3), scale(V, -1)
b2, b4, b6 = power(a1, 2), mul(a1, a3), power(a3, 2)
c4 = add(power(b2, 2), scale(b4, -24))
c6 = add(scale(power(b2, 3), -1), scale(mul(b2, b4), 36), scale(b6, -216))
delta = add(scale(power(b4, 3), -8), scale(power(b6, 2), -27),
            scale(mul(mul(b2, b4), b6), 9))
assert c4 == {(4, 0): 81, (1, 1): 72}
assert c6 == {(6, 0): -729, (3, 1): -972, (0, 2): -216}
assert delta == {(3, 3): -27, (0, 4): -27}
assert add(power(c4, 3), scale(power(c6, 2), -1)) == scale(delta, 1728)
residues = []
for q in (5, 7, 11, 19, 29, 41):
    at_C = []
    at_B = []
    for a in range(1, q):
        assert 81 * a**4 % q != 0
        at_B.append(a)
        for b in range(1, q):
            if (a**3 + b**5) % q == 0:
                value = 9 * a * (9 * a**3 + 8 * b**5) % q
                assert value == 9 * a**4 % q != 0
                at_C.append([a, b, value])
    residues.append({"q": q, "B_divisible_checks": len(at_B),
                     "C_divisible_unit_pairs": at_C})
j21 = [Fraction(-3**2 * 5**6, 2**3), Fraction(3**3 * 5**3, 2),
       Fraction(-3**2 * 5**3 * 101**3, 2**21),
       Fraction(-3**3 * 5**3 * 383**3, 2**7)]
v5 = [valuation(j.numerator, 5) - valuation(j.denominator, 5) for j in j21]
assert v5 == [6, 3, 3, 3]
result = {
    "status": "passed",
    "polynomial_domain": "Z[A,V] with V=B^5",
    "symbolic_checks": [
        "c4=9A(9A^3+8V)", "c6=-27(27A^6+36A^3V+8V^2)",
        "Delta=-27V^3(A^3+V)", "c4^3-c6^2=1728Delta"],
    "non_CM_rational_21_isogeny_j": [str(j) for j in j21],
    "j21_5_adic_valuations": v5,
    "bounded_residue_checks": residues,
    "non_claims": [
        "No search for or exclusion of integer Beal solutions.",
        "No computational proof of rational-isogeny classification.",
        "Residual conductor uses the written Tate-curve argument.",
        "No irreducibility transfer to the genus-two RM representation."
    ]
}
Path("work49/verification/alt_elliptic_run/result.json").write_text(
    json.dumps(result, indent=2) + "\n")
print(json.dumps({"status": result["status"],
                  "exact_polynomial_identities": len(result["symbolic_checks"]),
                  "residue_primes": [row["q"] for row in residues], "j21_v5": v5}))
