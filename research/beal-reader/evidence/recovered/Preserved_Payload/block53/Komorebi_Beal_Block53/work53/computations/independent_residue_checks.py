#!/usr/bin/env python3
"""Independent exhaustive finite-ring checks in the sqrt(5) basis.

No imports from the primary verifier. These finite assertions test algebraic
lemmas and boundary controls, not global Galois representations or geometry.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ArithmeticError(message)


def mul(a: tuple[int, int], b: tuple[int, int], modulus: int) -> tuple[int, int]:
    return ((a[0]*b[0]+5*a[1]*b[1]) % modulus,
            (a[0]*b[1]+a[1]*b[0]) % modulus)


def inv(a: tuple[int, int], modulus: int) -> tuple[int, int]:
    norm = (a[0]*a[0]-5*a[1]*a[1]) % modulus
    if norm % 7 == 0:
        raise ValueError("nonunit")
    ni = pow(norm, -1, modulus)
    return (a[0]*ni % modulus, -a[1]*ni % modulus)


def main() -> dict:
    # Complete O/7^3 enumeration, not a generated grid.
    modulus = 343
    square_zero = 0
    for x in range(modulus):
        for y in range(modulus):
            square = ((x*x+5*y*y) % modulus, (2*x*y) % modulus)
            actual = square == (0, 0)
            expected = x % 49 == 0 and y % 49 == 0
            require(actual == expected, f"nilpotent mismatch {(x, y)}")
            square_zero += actual
    require(square_zero == 49, "square-zero element count")

    modulus = 49
    unit_count = inverse_count = lambda_count = tested = correct = 0
    for x in range(modulus):
        for y in range(modulus):
            lam = (x, y)
            if x % 7 == 0 and y % 7 == 0:
                continue
            unit_count += 1
            require(mul(lam, inv(lam, modulus), modulus) == (1, 0), "inverse")
            inverse_count += 1
            if (x % 7, y % 7) == (1, 0):
                continue  # residual lambda=1 violates the separation hypothesis
            lambda_count += 1
            for i in range(7):
                for j in range(7):
                    a = ((x+7*i) % modulus, (y+7*j) % modulus)
                    d = mul(lam, inv(a, modulus), modulus)
                    tested += 1
                    trace = ((a[0]+d[0]) % modulus, (a[1]+d[1]) % modulus)
                    if trace == ((x+1) % modulus, y):
                        require(a == lam and d == (1, 0), "character root mismatch")
                        correct += 1
    require((unit_count, lambda_count, tested, correct) == (2352, 2303, 112847, 2303),
            "enumeration counts")

    # Independent finite-field Kummer functional check.
    elems = [(x, y) for x in range(7) for y in range(7)]
    zero = (0, 0)
    both71 = both29 = zero43 = good13_29 = good13_43 = good13_71 = 0
    cases = 0
    for u in elems:
        for r in elems:
            if r == zero:
                continue
            cases += 1
            f71a = ((2*u[0]+r[0]) % 7, (2*u[1]+r[1]) % 7)
            f71b = ((5*u[0]+r[0]) % 7, (5*u[1]+r[1]) % 7)
            f29a = ((4*u[0]+r[0]+5) % 7, (4*u[1]+r[1]) % 7)
            f29b = ((3*u[0]+r[0]+5) % 7, (3*u[1]+r[1]) % 7)
            f43 = ((r[0]+2) % 7, r[1])
            z71 = f71a == zero and f71b == zero
            z29 = f29a == zero and f29b == zero
            require(not z71, "both places over71 cannot vanish")
            require(z29 == (u == zero and r == (2, 0)), "both29 zero locus")
            require((f43 == zero) == (r == (5, 0)), "43 zero locus")
            both71 += z71
            both29 += z29
            zero43 += f43 == zero
            if u == zero:
                require(f71a != zero and f71b != zero, "good13/71 nonvanishing")
                good13_71 += f71a == zero or f71b == zero
                good13_29 += z29
                good13_43 += f43 == zero
    require((cases,both71,both29,zero43,good13_29,good13_43,good13_71) ==
            (2352,0,1,49,1,1,0), "Kummer counts")
    try:
        inv((7, 0), 49)
    except ValueError:
        nonunit = "REJECTED"
    else:
        raise ArithmeticError("nonunit silently inverted")
    return {
        "schema": "komorebi.beal.block53.independent_residue_checks.v1",
        "status": "PASS",
        "domain": "(Z/7^j)[s]/(s^2-5), independent sqrt5 basis",
        "nilpotent_enumeration": {"modulus":343, "all_elements":343**2,
             "square_zero_elements":square_zero,
             "equivalence":"u^2=0 mod343 iff u is divisible49"},
        "character_root_enumeration": {"modulus":49, "all_units":unit_count,
             "inverse_checks":inverse_count, "separated_lambdas":lambda_count,
             "same_residue_candidates":tested, "correct_roots":correct},
        "kummer_functionals": {"normalized_vectors":cases,
             "simultaneous71_zeros":both71, "simultaneous29_zeros":both29,
             "43_zeros":zero43, "good13_29_zeros":good13_29,
             "good13_43_zeros":good13_43, "good13_71_zeros":good13_71},
        "negative_controls": {"nonunit_inverse":nonunit},
        "non_claims": ["No arithmetic conjugation comparison map is asserted",
            "No exhaustion of global representations",
            "Finite ring verification does not prove class field theory or geometric input"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = main()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
