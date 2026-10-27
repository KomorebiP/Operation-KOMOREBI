#!/usr/bin/env python3
"""Replay the exact algebraic certificate for one Fermat degree-70 packet.

Requires Python >= 3.10 and SymPy. No network, floating point, or Lean is used.
This verifies finite integer/rational/polynomial assertions, not the complete
Hodge-theoretic proof. The latter is written separately in PROOF.md.
"""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
import math
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import sympy as sp
except ImportError as exc:
    raise SystemExit("SymPy is required: python -m pip install sympy") from exc

A_DATA = [
    [0, 0, 2, 0, 0, 3],
    [0, 0, 1, 2, 7, 0],
    [1, 0, 2, 2, 0, 1],
    [0, 5, 0, 0, 0, 0],
    [0, 0, 0, 2, 0, 3],
    [3, 0, 0, 0, 0, 0],
]
CHARACTER = [1, 20, 24, 42, 61, 62]
WEIGHTS = [10, 6, 3, 3, 3, 8]


def verify() -> dict:
    started = time.perf_counter()
    checks = []

    def check(name: str, condition: bool, detail=None) -> None:
        ok = bool(condition)
        checks.append({"name": name, "pass": ok, "detail": detail})
        if not ok:
            raise AssertionError(f"Certificate check failed: {name}: {detail}")

    A = sp.Matrix(A_DATA)
    a = sp.Matrix(CHARACTER)
    W = sp.Matrix(WEIGHTS)
    one = sp.ones(6, 1)
    M, m, D = 210, 70, 30
    alpha = 3 * a
    units70 = [t for t in range(1, m) if math.gcd(t, m) == 1]
    orbit70 = {tuple(t*x % m for x in CHARACTER) for t in units70}
    units210 = [t for t in range(1, M) if math.gcd(t, M) == 1]
    orbit210 = {tuple(t*int(x) % M for x in alpha) for t in units210}
    check("degree70_full_support", all(0 < x < m for x in CHARACTER))
    check("degree70_orbit_size", len(orbit70) == 24, len(orbit70))
    check("all_degree70_conjugates_middle_balanced", all(sum(b) == 3*m for b in orbit70))
    check("degree210_scaled_orbit", orbit210 == {tuple(3*x for x in b) for b in orbit70})
    check("matrix_determinant", A.det() == -2100, str(A.det()))
    check("positive_normalized_weights", A.inv()*one == W/D and all(x > 0 for x in W))
    check("weighted_homogeneity", A*W == D*one)
    check("positive_adjunction_index", sum(WEIGHTS)-D == 3)
    check("normalized_weight_sum", sum(A.inv()*one) == sp.Rational(11, 10))
    beta = A.T*a/m
    check("packet_integrality", beta == sp.Matrix([3, 3, 1, 3, 2, 3]))
    B = M*A.inv()
    check("integral_laurent_map", all(x.is_Integer for x in B))
    check("monomial_pullback_exponents", A*B == M*sp.eye(6))
    check("projective_weight_compatibility", B*one == 7*W)
    check("packet_pullback_exponents", B.T*beta == alpha)
    u = beta - 3*A[0, :].T
    e0 = sp.Matrix([1, 0, 0, 0, 0, 0])
    check("weight_zero_target_character", (W.T*u)[0] == 0)
    check("deck_character_certificate", B.T*u == alpha-630*e0)
    check("ambient_well_formed", all(math.gcd(*(WEIGHTS[j] for j in range(6) if j != i)) == 1 for i in range(6)))

    # Every singular toric stratum is contained in a coordinate subspace
    # indexed by weights with gcd > 1. Check its intersection dimension bound.
    strata = []
    for length in range(1, 7):
        for support in itertools.combinations(range(6), length):
            divisor = math.gcd(*(WEIGHTS[i] for i in support))
            if divisor <= 1:
                continue
            supported_rows = [r for r in A_DATA if all(r[i] == 0 for i in range(6) if i not in support)]
            # Nonzero restriction gives at least one equation on P(support).
            upper = length-2 if supported_rows else length-1
            strata.append({"support": list(support), "gcd": divisor, "dimension_upper_bound": upper})
    check("ambient_singular_intersection_codimension_at_least_two", all(s["dimension_upper_bound"] <= 2 for s in strata))

    y = sp.symbols('y0:6')
    F = sp.expand(sum(sp.prod(y[j]**row[j] for j in range(6)) for row in A_DATA))
    y0,y1,y2,y3,y4,y5 = y
    expected_F = y0**3+y1**5+y2**2*y5**3+y2*y3**2*y4**7+y0*y2**2*y3**2*y5+y3**2*y5**3
    check("polynomial_matches_matrix", sp.expand(F-expected_F) == 0)
    gradient = [sp.diff(F, x) for x in y]
    check("weighted_euler_identity", sp.expand(sum(W[i]*y[i]*gradient[i] for i in range(6))-D*F) == 0)
    planes = [(0,1,2,3), (0,1,3,5), (0,1,4,5)]
    check("listed_planes_are_singular", all(sp.expand(g.subs({y[i]:0 for i in zeros})) == 0 for zeros in planes for g in gradient))
    # Intersection of the three coordinate prime ideals: minimal hitting sets.
    hitting = []
    for length in range(1, 7):
        for subset in itertools.combinations(range(6), length):
            S = set(subset)
            if all(S.intersection(P) for P in planes) and not any(set(H).issubset(S) for H in hitting):
                hitting.append(subset)
    expected_hitting = [(0,), (1,), (2,5), (3,4), (3,5)]
    check("union_ideal_generators", hitting == expected_hitting, [list(s) for s in hitting])
    G = sp.groebner(gradient, *y, order='grevlex', domain=sp.QQ)
    powers = [3,4,3,13,3]
    membership = []
    for support, power in zip(hitting, powers):
        monomial = sp.prod(y[i] for i in support)
        remainder = G.reduce(monomial**power)[1]
        membership.append({"generator": str(monomial), "power": power, "remainder": str(remainder)})
    check("radical_gradient_ideal_certificate", all(r["remainder"] == "0" for r in membership), membership)
    # Inclusions J subset I(union) and every generator of I(union) in radical(J)
    # prove equality of radicals. No numeric singularity sampling is involved.
    check("cone_singular_dimension", max(6-len(P) for P in planes) == 2)

    return {
        "status": "PASS: exact finite certificate; see PROOF.md for the geometric argument",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(), "sympy": sp.__version__,
        "platform": platform.platform(), "arithmetic": "integers, rationals, QQ polynomial Groebner reduction",
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "command": "python verify_certificate.py --out verification.json",
        "runtime_seconds": time.perf_counter()-started,
        "checks_passed": len(checks), "checks": checks,
        "matrix_A": A_DATA, "matrix_B": [[int(v) for v in row] for row in B.tolist()],
        "weights": WEIGHTS, "degree": D, "beta": [int(x) for x in beta],
        "weight_zero_character_u": [int(x) for x in u],
        "orbit70": [list(o) for o in sorted(orbit70)],
        "singularity_radical": "(y0, y1, y2*y5, y3*y4, y3*y5)",
        "ambient_singular_strata": strata,
        "nonclaims": [
            "No machine verification of mixed Hodge theory or algebraic cycles.",
            "No proof of the general Hodge conjecture or of all Fermat packets.",
            "No explicit equations for a basis of representing surfaces.",
            "No historical novelty claim."
        ]
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=Path(__file__).with_name('verification.json'))
    args = parser.parse_args()
    result = verify()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(result['status'])
    print(f"{result['checks_passed']} checks passed; {result['runtime_seconds']:.3f} seconds")
    print(f"W_a dimension: 24; adjunction index: 3; normalized weight sum: 11/10")
    print(f"Certificate written to {args.out}")


if __name__ == '__main__':
    main()
