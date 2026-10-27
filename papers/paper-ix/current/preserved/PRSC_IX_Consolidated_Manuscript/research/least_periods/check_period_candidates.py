#!/usr/bin/env python3
"""Exact finite checks for the candidate N=4 period classification.

These calculations are NOT Lean proofs and finite tests are NOT a universal
proof. The accompanying Newton-dominance argument is a separate mathematical
derivation whose formalization remains outstanding.

C_{N,j}(0)=1 and, for n>0,
C_{N,j}(n)=-sum_{q<n} binom(N*n+j,N*q)*C_{N,j}(q)/binom(N*n+j,N*n).
All arithmetic below uses fractions.Fraction and integer binomial coefficients.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from math import comb, factorial
from pathlib import Path


def coefficients(N: int, j: int, end: int) -> list[Fraction]:
    if N < 1 or not 0 <= j < N or end < 0:
        raise ValueError("invalid coefficient parameters")
    result = [Fraction(1)]
    for n in range(1, end + 1):
        result.append(-sum(
            (Fraction(comb(N*n+j, N*q))*result[q] for q in range(n)),
            Fraction(0),
        ) / comb(N*n+j, N*n))
    return result


def valuation_two(value: Fraction) -> int | None:
    """Return None at zero, otherwise the exact rational 2-adic valuation."""
    if value == 0:
        return None
    numerator, denominator = abs(value.numerator), value.denominator
    result = 0
    while numerator % 2 == 0:
        numerator //= 2
        result += 1
    while denominator % 2 == 0:
        denominator //= 2
        result -= 1
    return result


def mahler_coefficient(values: list[Fraction], k: int) -> Fraction:
    return sum(
        (Fraction((-1)**(k-i)*comb(k, i))*values[i] for i in range(k+1)),
        Fraction(0),
    )


def run() -> dict:
    offsets = [1, 1, 4, 2]
    prefix_ends = [2, 2, 6, 4]
    families = []
    checked = 0
    for j in range(4):
        values = coefficients(4, j, 32)
        prefix = []
        for k in range(1, prefix_ends[j]+1):
            value = mahler_coefficient(values, k)
            prefix.append({"k": k, "exact_fraction": str(value),
                           "v2": valuation_two(value)})
        cases = []
        for n in range(17):
            for T in range(1, 17):
                actual = valuation_two(values[n+T]-values[n])
                expected = valuation_two(Fraction(T)) + offsets[j]
                if actual != expected:
                    raise AssertionError((j, n, T, actual, expected))
                cases.append({"n": n, "T": T, "actual_v2": actual,
                              "candidate_v2": expected})
                checked += 1
        families.append({"j": j, "normalized_offset": offsets[j],
                         "original_offset": offsets[j] + valuation_two(Fraction(factorial(j))),
                         "exact_mahler_prefix": prefix, "cases": cases})
    return {
        "status": "FINITE_CHECKS_PASS",
        "scope": "Exact rational computation; not a Lean verification or a universal proof.",
        "universal_candidate_status": "Derived separately by the Newton-dominance argument; not Lean formalized in this checkpoint.",
        "normalization": "U_{4,j}(n)=j!*C_{4,j}(n)",
        "recurrence": "C(N,j,0)=1; C(N,j,n)=-sum(q=0..n-1,binom(N*n+j,N*q)*C(N,j,q))/binom(N*n+j,N*n)",
        "candidate_formula": "v2(C(4,j,n+T)-C(4,j,n))=v2(T)+c[j], c=[1,1,4,2]",
        "tested_range": {"j_inclusive": [0, 3], "n_inclusive": [0, 16],
                         "T_inclusive": [1, 16], "coefficients_n_inclusive": [0, 32],
                         "mahler_prefix_max_k_by_j": prefix_ends},
        "direct_difference_cases": checked,
        "families": families,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=Path(__file__).with_name("period_candidates_results.json"))
    args = parser.parse_args()
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    result = run()
    output.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    source = Path(__file__).resolve()
    manifest = {
        "status": result["status"],
        "scope": result["scope"],
        "reproduction": "python3 check_period_candidates.py",
        "dependencies": "Python standard library only",
        "files": [{"name": p.name, "bytes": p.stat().st_size,
                   "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                  for p in [source, output]],
    }
    manifest_path = output.with_name("period_candidates_manifest.json")
    manifest_path.write_text(json.dumps(manifest, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"status": result["status"],
                      "direct_difference_cases": result["direct_difference_cases"],
                      "results": str(output), "manifest": str(manifest_path)}, indent=2))


if __name__ == "__main__":
    main()
