#!/usr/bin/env python3
"""Bounded exact checks for proposed affine Mahler kernel formulas.

This is a research checkpoint, not a Lean proof or a universal proof by testing.
Run: python3 check_kernel_formulas.py
"""

from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import platform
import time


def theta(radix, address, row, depth):
    """Alternating-binomial definition, with out-of-range binomials zero."""
    return sum(
        (-1) ** (depth - i)
        * comb(depth, i)
        * (comb(radix * i + address, row) if row <= radix * i + address else 0)
        for i in range(depth + 1)
    )


def v2(nonzero_integer):
    if nonzero_integer == 0:
        raise ValueError("This bounded check calls v2 only on nonzero integers.")
    value = abs(nonzero_integer)
    valuation = 0
    while value % 2 == 0:
        valuation += 1
        value //= 2
    return valuation


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    start = time.perf_counter()
    started_at = datetime.now(timezone.utc).isoformat()
    formula_checks = 0
    edge_checks = 0
    for depth in range(41):
        for j in range(depth + 1):
            actual = theta(2, 1, depth + j, depth)
            proposed = (
                2 ** (depth - j)
                * Fraction(depth + j + 1, depth + 1)
                * comb(depth + 1, j)
            )
            require(actual == proposed, f"Binary digit identity failed: k={depth}, j={j}")
            formula_checks += 1
        require(theta(2, 1, 2 * depth + 1, depth) == 1, f"Top edge failed: k={depth}")
        edge_checks += 1

    require(formula_checks == 861, "Unexpected formula case count")
    require(edge_checks == 41, "Unexpected edge case count")
    base_terms = [4, 4]
    base_total = theta(2, 1, 3, 2)
    require(sum(base_terms) == base_total == 8, "Hand-computable benchmark failed")
    cancellations = [{
        "kind": "coefficient_expansion",
        "parameters": {"M": 2, "s": 1, "r": 3, "k": 2},
        "terms": base_terms,
        "sum": base_total,
        "minimum_term_v2": 2,
        "sum_v2": 3,
    }]
    for exponent in (2, 3, 4):
        half_radix = 2 ** (exponent - 1)
        all_paths = [
            (i, theta(2, 1, 3, i) * theta(half_radix, 0, i, 2))
            for i in range(2, 2 * half_radix + 1)
        ]
        nonzero_paths = [(i, term) for i, term in all_paths if term != 0]
        expected_paths = [
            (2, 8 * half_radix ** 2),
            (3, 8 * half_radix ** 2 * (half_radix - 1)),
        ]
        require(nonzero_paths == expected_paths, f"Composition paths failed: a={exponent}")
        total = sum(term for _, term in nonzero_paths)
        actual = theta(2 ** exponent, 1, 3, 2)
        require(total == actual == 2 ** (3 * exponent), f"Composition total failed: a={exponent}")
        minimum = min(v2(term) for _, term in nonzero_paths)
        require(minimum == 2 * exponent + 1, f"Minimum valuation failed: a={exponent}")
        require(v2(total) == 3 * exponent, f"Total valuation failed: a={exponent}")
        cancellations.append({
            "kind": "binary_composition",
            "parameters": {"a": exponent, "M": 2 ** exponent, "s": 1, "r": 3, "k": 2},
            "paths": [{"intermediate_index": i, "term": term} for i, term in nonzero_paths],
            "sum": total,
            "minimum_term_v2": minimum,
            "sum_v2": v2(total),
            "additional_digits": v2(total) - minimum,
        })

    root = Path(__file__).resolve().parent
    result_path = root / "kernel_check_results.json"
    results = {
        "status": "PASS",
        "scope": "Bounded exact checks; no new Lean proof.",
        "binary_address_formula": {
            "formula": "Theta_(2,1)(k+j,k) = 2^(k-j) * (k+j+1)/(k+1) * binom(k+1,j)",
            "depth_range": [0, 40],
            "j_range": "0 <= j <= k",
            "checked_cases": formula_checks,
            "arithmetic": "Python exact integers and fractions.Fraction",
        },
        "top_edge": {"formula": "Theta_(2,1)(2k+1,k) = 1", "checked_cases": edge_checks},
        "cancellation_examples": cancellations,
        "separate_uniform_algebraic_observation": {
            "status": "Direct coefficient derivation, not inferred from tests; not Lean checked.",
            "identity": "Theta_(M,1)(3,2) = M^2(M-1) + M^2 = M^3",
            "composition": "For M=2N and N=2^(a-1), a>=2, the only nonzero paths are 8N^2 and 8N^2(N-1).",
            "consequence": "For all a>=2, path-minimum valuation is 2a+1 while total valuation is 3a; extra cancellation is a-1 digits.",
        },
        "non_claims": [
            "Finite checks do not prove the universal binary formula.",
            "No general exact affine kernel valuation formula is established.",
            "No universal fixed finite-state carry algorithm is established.",
            "No Lean proof was added or checked by this script.",
        ],
    }
    result_path.write_text(json.dumps(results, indent=2) + "\n")
    script_path = Path(__file__).resolve()
    outputs = [
        {"path": path.name, "sha256": sha256(path.read_bytes()).hexdigest()}
        for path in (script_path, result_path)
    ]
    manifest = {
        "schema_version": 1,
        "claim_id": "affine_mahler_binary_digit_and_cancellation_brainstorm",
        "repository": {"commit": "not a git checkout", "dirty": False},
        "command": "python3 check_kernel_formulas.py",
        "environment": {
            "software": ["Python " + platform.python_version(), "Python standard library only"],
            "hardware": platform.machine(),
        },
        "mathematics": {
            "assertion_tested": "Binary s=1 closed formula on 861 inputs, 41 top edges, and four concrete cancellation examples.",
            "coefficient_domain": "Z; exact rational expressions compared using fractions.Fraction",
            "conventions": "Theta is the alternating-binomial coefficient formula. Binomial(n,r)=0 if r>n. v2 is used only for nonzero integers.",
            "inputs": ["M=2,s=1,k=0..40,j=0..k", "Top edge k=0..40", "Cancellation (M,s,r,k)=(2,1,3,2)", "Composition a in {2,3,4}, s=1,r=3,k=2"],
            "bounds": {"maximum_binary_depth": 40, "composition_exponents": [2, 3, 4], "random_inputs": 0},
            "non_claims": results["non_claims"],
        },
        "randomness": {"used": False, "generator": "none", "seed": None},
        "run": {"started_at": started_at, "runtime_seconds": time.perf_counter() - start, "exit_status": 0},
        "outputs": outputs,
        "checks": [
            "Alternating-binomial definition independently compared to binary closed formula.",
            "All 41 upper edges checked.",
            "Hand-computable example 4+4=8 checked.",
            "Entire finite composition index range checked for the three selected prime-power examples.",
            "Exact term valuations and total valuations checked.",
        ],
        "result": "implementation and finite assertion verified in the stated range",
        "residual_risks": ["These checks are ordinary Python execution, not kernel-verified Lean proofs.", "A universal result requires the separate algebraic proof or formalization."],
    }
    (root / "kernel_check_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"status": "PASS", "binary_formula_checks": formula_checks, "top_edge_checks": edge_checks, "cancellation_examples": len(cancellations)}))


if __name__ == "__main__":
    main()
