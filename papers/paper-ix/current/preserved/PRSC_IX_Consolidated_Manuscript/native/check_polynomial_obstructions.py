#!/usr/bin/env python3
"""Exact finite checks for the explicitly stated polynomial lifting criterion.
Not a proof of either untyped native conjecture. Uses only Python integers.
"""
from __future__ import annotations
from itertools import product
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import platform
import time

ROOT = Path(__file__).resolve().parent

def evaluate(coefficients, x):
    # Horner evaluation, independent of the derivative calculation below.
    value = 0
    for c in reversed(coefficients):
        value = value * x + c
    return value

def derivative(coefficients, x):
    return sum(k * c * x ** (k - 1) for k, c in enumerate(coefficients) if k)

def one_case(coefficients, p, L, x):
    q = p ** L
    value = evaluate(coefficients, x)
    assert value % q == 0
    residual = (value // q) % p
    jacobian = derivative(coefficients, x) % p
    expected = [t for t in range(p) if (residual + jacobian * t) % p == 0]
    actual = [t for t in range(p) if evaluate(coefficients, x + q * t) % (q * p) == 0]
    assert expected == actual
    for t in range(p):
        shifted = x + q * t
        assert evaluate(coefficients, shifted) % q == 0
        assert derivative(coefficients, shifted) % p == jacobian
        assert (evaluate(coefficients, shifted) // q) % p == (residual + jacobian * t) % p
    # In one variable rank is 0 or 1. Nonempty solution sets have p^(1-rank) members.
    rank = int(jacobian != 0)
    assert not actual or len(actual) == p ** (1 - rank)
    return {"coefficients_ascending": list(coefficients), "prime": p, "L": L,
            "representative": x, "residual_mod_p": residual,
            "jacobian_mod_p": jacobian, "correction_digits": actual,
            "lift_residues": [x + q * t for t in actual]}

def main():
    started = datetime.now(timezone.utc).isoformat()
    start = time.perf_counter()
    counts = {"polynomial_vectors": 0, "residues_scanned": 0,
              "solution_points_checked": 0, "liftable_points": 0,
              "obstructed_points": 0, "singular_solution_points": 0}
    for coeff in product(range(-2, 3), repeat=4):
        counts["polynomial_vectors"] += 1
        for p in (2, 3, 5):
            for L in (1, 2, 3):
                q = p ** L
                for x in range(q):
                    counts["residues_scanned"] += 1
                    if evaluate(coeff, x) % q:
                        continue
                    row = one_case(coeff, p, L, x)
                    counts["solution_points_checked"] += 1
                    counts["singular_solution_points"] += row["jacobian_mod_p"] == 0
                    counts["liftable_points" if row["correction_digits"] else "obstructed_points"] += 1
    benchmarks = [one_case((-3, 0, 1), 3, 1, 0),
                  one_case((-1, 0, 1), 3, 1, 1),
                  one_case((-1, 0, 1), 3, 1, 4),
                  one_case((-5, 0, 1), 2, 1, 1),
                  one_case((-5, 0, 1), 2, 2, 1),
                  one_case((-5, 0, 1), 2, 2, 3)]
    assert benchmarks[0]["lift_residues"] == []
    assert benchmarks[1]["lift_residues"] == [1]
    assert benchmarks[2]["lift_residues"] == [10]
    assert benchmarks[3]["lift_residues"] == [1, 3]
    assert benchmarks[4]["lift_residues"] == benchmarks[5]["lift_residues"] == []
    output = ROOT / "polynomial_obstruction_checks.json"
    output.write_text(json.dumps({"status": "PASS", "counts": counts,
                                  "benchmarks": benchmarks}, indent=2) + "\n")
    duration = time.perf_counter() - start
    manifest = {"schema_version": 1, "claim_id": "PaperIX.Native13.2.PolynomialSpecialization",
        "repository": {"commit": "standalone child work, no git repository", "dirty": True},
        "command": "python3 native_work/check_polynomial_obstructions.py",
        "environment": {"software": ["Python " + platform.python_version()], "hardware": platform.machine()},
        "mathematics": {"assertion_tested": "For each listed solution modulo p^L, residual-plus-Jacobian corrections equal directly enumerated lifts modulo p^(L+1); representative change and lift counts agree.",
            "coefficient_domain": "exact integer polynomials, reduced modulo prime powers",
            "conventions": "coefficient vectors in ascending powers, L>=1, canonical x representatives in exhaustive run",
            "inputs": ["all 625 length-four vectors in {-2,-1,0,1,2}^4", "six exact boundary benchmarks"],
            "bounds": {"primes": [2, 3, 5], "L": [1, 2, 3], "max_degree": 3},
            "non_claims": ["Not a proof of the universal polynomial theorem.", "Not a proof of native Conjecture 13.2 or 13.3.", "No multivariable exhaustive range."]},
        "randomness": {"used": False, "generator": "", "seed": None},
        "run": {"started_at": started, "runtime_seconds": duration, "exit_status": 0},
        "outputs": [{"path": output.name, "sha256": hashlib.sha256(output.read_bytes()).hexdigest()},
                    {"path": Path(__file__).name, "sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}],
        "checks": ["Direct Horner polynomial evaluation versus derivative-based correction equation", "All correction digits tested", "Representative changes preserve obstruction coset", "Nonempty lift count p^(1-rank)", "Six hand-computable benchmarks"],
        "result": "implementation and finite assertion verified in the stated range",
        "residual_risks": ["Universal argument resides in the accompanying proof note, separately from the computation."]}
    (ROOT / "polynomial_obstruction_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"status": "PASS", "counts": counts, "runtime_seconds": duration}, indent=2))

if __name__ == "__main__":
    main()
