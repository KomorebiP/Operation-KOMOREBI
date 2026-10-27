#!/usr/bin/env python3
"""Exact local squareclass lanes for a^3*u^6+b^5*v^10=c^7*w^14.

All residue computations are exhaustive over the declared finite rings.
The p-adic saturation theorem is a separate written proof, not a computation.
"""
from itertools import product
from pathlib import Path
import argparse
import json

EXPONENTS = (3, 5, 7)
PHASES = ("all_units", "A_nonunit", "B_nonunit", "C_nonunit")


def prime(n):
    return n >= 2 and all(n % d for d in range(2, int(n ** 0.5) + 1))


def residue_witness(coeff, p, modulus, phase):
    nonunit = None if phase == "all_units" else PHASES.index(phase) - 1
    tables = []
    for i, (a, exponent) in enumerate(zip(coeff, EXPONENTS)):
        table = {}
        for u in range(modulus):
            base = (a * u * u) % modulus
            if (base % p == 0) != (i == nonunit):
                continue
            value = pow(base, exponent, modulus)
            table.setdefault(value, u)
        tables.append(table)
    for x, u in tables[0].items():
        for y, v in tables[1].items():
            z = (x + y) % modulus
            if z in tables[2]:
                return (u, v, tables[2][z])
    return None


def direct_witness(coeff, p, modulus, phase):
    nonunit = None if phase == "all_units" else PHASES.index(phase) - 1
    for roots in product(range(modulus), repeat=3):
        bases = tuple(a * u * u % modulus for a, u in zip(coeff, roots))
        if any((base % p == 0) != (i == nonunit) for i, base in enumerate(bases)):
            continue
        if (pow(bases[0], 3, modulus) + pow(bases[1], 5, modulus)
                - pow(bases[2], 7, modulus)) % modulus == 0:
            return roots
    return None


def dyadic_expected(coeff, phase):
    a, b, c = coeff
    if phase == "all_units":
        return False
    i = PHASES.index(phase) - 1
    if any(x % 2 == 0 for j, x in enumerate(coeff) if j != i):
        return False
    return ((b - c) % 8 == 0 if i == 0 else
            (a - c) % 8 == 0 if i == 1 else (a + b) % 8 == 0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = {
        "conventions": {
            "coefficient_labels": {"0": "p divides squarefree coefficient", "S": "unit square", "N": "unit nonsquare"},
            "primitivity": "At most one of the three bases is divisible by p.",
            "scope": "Local necessary conditions only; p-adic lifting is established separately in notes/stratification.md.",
        },
        "odd_primes": [],
        "checks": {},
    }

    comparison_count = 0
    for p in (3, 5, 7):
        for coeff in product(range(p), repeat=3):
            if sum(a == 0 for a in coeff) > 1:
                continue
            for phase in PHASES:
                fast = residue_witness(coeff, p, p, phase)
                slow = direct_witness(coeff, p, p, phase)
                assert (fast is None) == (slow is None), (p, coeff, phase)
                comparison_count += 1
    result["checks"]["independent_direct_comparisons"] = comparison_count

    # Unit coefficients differing by a square give exactly the same image sets.
    squareclass_checks = 0
    for p in range(3, 102, 2):
        if not prime(p):
            continue
        squares = {x * x % p for x in range(1, p)}
        ns = min(x for x in range(1, p) if x not in squares)
        representatives = {"0": 0, "S": 1, "N": ns}
        for a in range(1, p):
            rep = 1 if a in squares else ns
            for e in EXPONENTS:
                assert {pow(a * x * x, e, p) for x in range(1, p)} == {
                    pow(rep * x * x, e, p) for x in range(1, p)}
                squareclass_checks += 1
        rows = []
        for labels in product(("0", "S", "N"), repeat=3):
            if labels.count("0") > 1:
                continue
            coeff = tuple(representatives[s] for s in labels)
            phases = {}
            for phase in PHASES:
                witness = residue_witness(coeff, p, p, phase)
                if witness is not None:
                    phases[phase] = witness
            rows.append({"labels": "".join(labels), "allowed_phases": phases})
        result["odd_primes"].append({"p": p, "nonsquare_representative": ns,
                                     "rows": rows,
                                     "excluded_coefficient_classes": [r["labels"] for r in rows if not r["allowed_phases"]]})
    result["checks"]["unit_squareclass_image_checks"] = squareclass_checks

    # Both coefficient units and ramified squarefree coefficients are exhaustive.
    dyadic = []
    dyadic_comparisons = 0
    for modulus in (8, 16):
        coefficients = [a for a in range(modulus) if a % 4 != 0]
        surviving, excluded, phase_count = 0, 0, 0
        for coeff in product(coefficients, repeat=3):
            if sum(a % 2 == 0 for a in coeff) > 1:
                continue
            allowed = []
            for phase in PHASES:
                observed = residue_witness(coeff, 2, modulus, phase) is not None
                expected = dyadic_expected(coeff, phase)
                assert observed == expected, (modulus, coeff, phase)
                dyadic_comparisons += 1
                if observed:
                    allowed.append(phase)
            surviving += bool(allowed)
            excluded += not allowed
            phase_count += len(allowed)
            if modulus == 8:
                dyadic.append({"coefficients_mod8": coeff, "allowed_phases": allowed})
        result[f"dyadic_mod{modulus}"] = {"surviving_coefficient_residue_triples": surviving,
                                           "excluded_coefficient_residue_triples": excluded,
                                           "allowed_phase_count": phase_count}
    result["dyadic_mod8_rows"] = dyadic
    result["checks"]["dyadic_mod8_mod16_comparisons"] = dyadic_comparisons

    # Direct finite correlation example: coefficient phases mod 8.
    allowed_odd = {tuple(r["coefficients_mod8"]) for r in dyadic
                   if all(x % 2 for x in r["coefficients_mod8"]) and r["allowed_phases"]}
    marginals = [sorted({row[i] for row in allowed_odd}) for i in range(3)]
    cartesian = set(product(*marginals))
    false_positives = sorted(cartesian - allowed_odd)
    assert false_positives
    result["correlation_loss"] = {"joint_allowed_count": len(allowed_odd),
                                   "separate_marginal_product_count": len(cartesian),
                                   "marginals": marginals,
                                   "false_positives": false_positives,
                                   "interpretation": "Keeping only separate coefficient marginals loses certified mod-8 exclusions."}

    # Known coefficient family (a,b,c)=(1,2,3) is impossible modulo 8.
    assert all(residue_witness((1, 2, 3), 2, 8, phase) is None for phase in PHASES)
    # Negative control: omit the minus in the C-nonunit phase and observe a mismatch.
    assert dyadic_expected((1, 7, 2), "C_nonunit")
    assert (1 - 7) % 8 != 0
    result["checks"]["benchmark_1_2_3_excluded"] = True
    result["checks"]["wrong_sign_negative_control_rejected"] = True
    result["status"] = "all_declared_finite_checks_passed"
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "checks": result["checks"],
                      "dyadic": {k: v for k, v in result.items() if k in ("dyadic_mod8", "dyadic_mod16")},
                      "odd_exclusions": {r["p"]: r["excluded_coefficient_classes"] for r in result["odd_primes"]},
                      "correlation": {k: v for k, v in result["correlation_loss"].items() if k != "false_positives"}}, indent=2))


if __name__ == "__main__":
    main()
