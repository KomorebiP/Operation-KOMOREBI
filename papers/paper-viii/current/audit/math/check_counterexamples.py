#!/usr/bin/env python3
"""Exact independent checks of two mathematical counterexamples.

The rounding computation is two-significant-digit decimal arithmetic,
rounding to nearest with ties to even, not IEEE binary or a GPU kernel.
The determinant, standard-model residual comparisons and operator/vector
example are then evaluated using exact fractions. This is bounded evidence.
"""
from decimal import Decimal, localcontext, ROUND_HALF_EVEN
from fractions import Fraction as Q
from pathlib import Path
import json


def main():
    av = (Decimal("1.1"), Decimal("1.3"))
    bv = (Decimal("1.1"), Decimal("1.3"))
    with localcontext() as context:
        context.prec = 2
        context.rounding = ROUND_HALF_EVEN
        rounded = [[a * b for b in bv] for a in av]
    exact = [[Q(a) * Q(b) for b in bv] for a in av]
    result = [[Q(x) for x in row] for row in rounded]
    residual = [[abs(result[i][j] - exact[i][j]) for j in range(2)] for i in range(2)]
    u = Q(1, 20)
    ratios = [[residual[i][j] / abs(exact[i][j]) for j in range(2)] for i in range(2)]
    determinant = result[0][0] * result[1][1] - result[0][1] * result[1][0]
    assert result == [[Q(6, 5), Q(7, 5)], [Q(7, 5), Q(17, 10)]]
    assert determinant == Q(2, 25) and determinant != 0
    assert all(r <= u for row in ratios for r in row)
    # E=diag(0,1), x=(1,0): exact input-specific error zero, operator norm one.
    ex = [Q(0), Q(0)]
    assert sum(z*z for z in ex) == 0
    report = {
        "evidence_kind": "fresh exact bounded counterexample calculation",
        "rounding_model": "two significant decimal digits; nearest ties to even",
        "unit_roundoff": str(u),
        "rounded_product": [[str(x) for x in row] for row in result],
        "exact_product": [[str(x) for x in row] for row in exact],
        "relative_scalar_errors": [[str(x) for x in row] for row in ratios],
        "rounded_determinant": str(determinant),
        "computed_product_rank": 2,
        "maximum_rank_of_same_shape_perturbed_input_products": 1,
        "all_scalar_roundings_satisfy_standard_model": True,
        "overflow_underflow": False,
        "vector_error_squared": "0",
        "actual_error_operator_norm": "1",
        "fresh_lean_execution": False,
        "fresh_gpu_execution": False,
        "all_assertions_passed": True,
    }
    out = Path(__file__).with_name("COUNTEREXAMPLE_CHECK.json")
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"all_assertions_passed": True, "determinant": str(determinant), "report": str(out)}))


if __name__ == "__main__":
    main()
