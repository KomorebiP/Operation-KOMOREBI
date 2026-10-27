#!/usr/bin/env python3
"""Independent exact checks; writes only beside this file, never route outputs."""
from fractions import Fraction
from hashlib import sha256
from itertools import product
from pathlib import Path
import json
import runpy

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MULTI = ROOT / "routes/multichannel"


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def vp(value, prime):
    value = Fraction(value)
    if value == 0:
        return float("inf")
    ans = 0
    a, b = abs(value.numerator), value.denominator
    while a % prime == 0:
        a //= prime
        ans += 1
    while b % prime == 0:
        b //= prime
        ans -= 1
    return ans


def nu(vector, prime):
    return min(vp(a, prime) for a in vector)


def action(matrix, vector):
    return [sum(a * b for a, b in zip(row, vector)) for row in matrix]


def main():
    before = {name: digest(MULTI / name) for name in ["PROOF.md", "verify.py", "results.json"]}
    checks = 0
    positive_det_depth = 0
    # Rational vectors, including zeros and negative input content; several
    # primes so positive determinant depth occurs in the exhaustive range.
    for entries in product(range(-2, 3), repeat=4):
        a, b, c, d = entries
        delta = a * d - b * c
        if delta == 0:
            continue
        matrix = [[a, b], [c, d]]
        inverse = [[Fraction(d, delta), Fraction(-b, delta)],
                   [Fraction(-c, delta), Fraction(a, delta)]]
        for prime in [2, 3, 5, 7]:
            for pair in product(range(-2, 3), repeat=2):
                if pair == (0, 0):
                    continue
                for scale in [Fraction(1), Fraction(1, prime**2)]:
                    vector = [scale * u for u in pair]
                    result = action(matrix, vector)
                    original_depth, image_depth = nu(vector, prime), nu(result, prime)
                    assert original_depth <= image_depth <= original_depth + vp(delta, prime)
                    assert original_depth + min(vp(e, prime) for e in entries) <= image_depth
                    assert image_depth <= original_depth - min(vp(e, prime) for row in inverse for e in row)
                    for q in [1, prime, prime**2]:
                        image_rational = [e / q for e in result]
                        assert original_depth - vp(q, prime) <= nu(image_rational, prime)
                        assert nu(image_rational, prime) <= original_depth + vp(delta, prime) - vp(q, prime)
                    assert action(inverse, result) == vector
                    checks += 1
                    positive_det_depth += (vp(delta, prime) > 0)
    # Small explicit examples independently reconstructed from displayed maps.
    for prime in [3, 5, 7]:
        for depth in [1, 2, 5]:
            X = prime**depth - 1
            vector = [X, 1]
            hidden = action([[1, 0], [-1, 1]], vector)
            assert nu(hidden, prime) == 0 and all(vp(e, prime) == 0 for e in hidden)
            assert vp(2 * hidden[0] + hidden[1], prime) == depth
            concentrated = action([[1, X], [-1, 1]], [1, 1])
            assert concentrated == [prime**depth, 0]
            assert nu(concentrated, prime) == depth
            normalized = action([[Fraction(1, prime**depth), Fraction(1, prime**depth)], [0, 1]], vector)
            assert normalized == [1, 1]
    # Rerun the author's own verifier while redirecting all emitted files into
    # the review tree. Its mathematical implementation is not used above.
    ns = runpy.run_path(str(MULTI / "verify.py"))
    ns["main"].__globals__["OUT"] = HERE / "multichannel"
    ns["main"]()
    after = {name: digest(MULTI / name) for name in before}
    assert before == after
    result = {
        "status": "passed",
        "independent_matrix_vector_checks": checks,
        "checks_with_positive_determinant_depth": positive_det_depth,
        "scope": "2x2 nonsingular matrices entries -2..2; primes 2,3,5,7; 24 nonzero vectors entries -2..2; scales 1 and p^-2; rational denominators 1,p,p^2",
        "nonclaims": ["Universal validity follows from proof audit, not finite testing", "No ABC proof or impossibility theorem"],
        "route_sha256_before": before,
        "route_sha256_after": after,
        "script_sha256": digest(Path(__file__)),
    }
    (HERE / "independent_results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
