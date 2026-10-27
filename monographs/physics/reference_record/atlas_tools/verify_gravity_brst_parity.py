#!/usr/bin/env python3
"""Exact Lorentz BRST dual-spinor parity negative control.

This is a bounded exterior-algebra witness, not a kernel check of the parent BV
theory. Ghosts are odd, all four dual-spinor components are odd, and s is a left
odd derivation. It compares the archived right-ghost minus sign with the plus
sign forced by the dual action when the spinor is odd.
"""
from __future__ import annotations

import json
from pathlib import Path
import sympy as sp

NAMES = ("theta1", "theta2", "theta3", "eta0", "eta1", "eta2", "eta3")
NG = len(NAMES)


def canon(a):
    return {m: sp.simplify(c) for m, c in a.items() if sp.simplify(c) != 0}


def add(*terms):
    out = {}
    for a in terms:
        for m, c in a.items():
            out[m] = out.get(m, 0) + c
    return canon(out)


def scale(c, a):
    return canon({m: c * x for m, x in a.items()})


def monomial_product(a, b):
    if a & b:
        return None, 0
    crossings = sum((b & ((1 << i) - 1)).bit_count() for i in range(NG) if a & (1 << i))
    return a | b, (-1) ** crossings


def mul(a, b):
    out = {}
    for ma, ca in a.items():
        for mb, cb in b.items():
            m, sign = monomial_product(ma, mb)
            if sign:
                out[m] = out.get(m, 0) + sign * ca * cb
    return canon(out)


UNIT = {0: sp.Integer(1)}
GEN = [{1 << i: sp.Integer(1)} for i in range(NG)]


def differential(a, generator_images):
    out = {}
    for mask, coefficient in a.items():
        idx = [i for i in range(NG) if mask & (1 << i)]
        for j, i in enumerate(idx):
            prefix = {sum(1 << k for k in idx[:j]): sp.Integer(1)}
            suffix = {sum(1 << k for k in idx[j + 1:]): sp.Integer(1)}
            out = add(out, scale(coefficient * (-1) ** j,
                                 mul(mul(prefix, generator_images[i]), suffix)))
    return out


def serialize(a):
    return {"*".join(NAMES[i] for i in range(NG) if mask & (1 << i)) or "1": str(c)
            for mask, c in sorted(canon(a).items())}


def main():
    # Mostly-plus Clifford representation: gamma^I=i Gamma^I, where Gamma are
    # the usual mostly-minus Dirac matrices. Coefficients are exact Q(i).
    I2, O2 = sp.eye(2), sp.zeros(2)
    sig = [sp.Matrix([[0, 1], [1, 0]]), sp.Matrix([[0, -sp.I], [sp.I, 0]]),
           sp.Matrix([[1, 0], [0, -1]])]
    beta = sp.diag(1, 1, -1, -1)
    gamma = [sp.I * beta] + [sp.I * sp.BlockMatrix([[O2, x], [-x, O2]]).as_explicit() for x in sig]
    metric = (-1, 1, 1, 1)
    clifford = all(gamma[i] * gamma[j] + gamma[j] * gamma[i]
                   == 2 * metric[i] * sp.eye(4) * int(i == j)
                   for i in range(4) for j in range(4))
    T = [gamma[2] * gamma[3] / 2, gamma[3] * gamma[1] / 2, gamma[1] * gamma[2] / 2]
    lie = T[0] * T[1] - T[1] * T[0] == -T[2] and \
          T[1] * T[2] - T[2] * T[1] == -T[0] and \
          T[2] * T[0] - T[0] * T[2] == -T[1]
    # Orthogonal implementation check: sort the concatenated generator lists
    # by adjacent swaps, independently of the bit-count crossing formula.
    exterior = True
    for a in range(1 << NG):
        for b in range(1 << NG):
            m, sign = monomial_product(a, b)
            seq = [i for i in range(NG) if a & (1 << i)] + [i for i in range(NG) if b & (1 << i)]
            if len(set(seq)) != len(seq):
                exterior = exterior and sign == 0
                continue
            swaps = 0
            for j in range(1, len(seq)):
                k = j
                while k and seq[k - 1] > seq[k]:
                    seq[k - 1], seq[k] = seq[k], seq[k - 1]
                    swaps += 1
                    k -= 1
            exterior = exterior and m == sum(1 << i for i in seq) and sign == (-1) ** swaps
    chi = [[add(*(scale(T[a][i, j], GEN[a]) for a in range(3))) for j in range(4)] for i in range(4)]
    chi2 = [[add(*(mul(chi[i][k], chi[k][j]) for k in range(4))) for j in range(4)] for i in range(4)]
    # chi^2=-theta2 theta3 T1+theta1 theta3 T2-theta1 theta2 T3.
    sc = [scale(-1, mul(GEN[1], GEN[2])), mul(GEN[0], GEN[2]), scale(-1, mul(GEN[0], GEN[1]))]
    ghost_ce = all(differential(chi[i][j], sc + [{}] * 4) == chi2[i][j]
                   for i in range(4) for j in range(4))
    bar = GEN[3:]
    bar_chi = [add(*(mul(bar[j], chi[j][i]) for j in range(4))) for i in range(4)]
    results = {}
    for name, sign in [("archived_right_minus", -1), ("corrected_right_plus", 1)]:
        images = sc + [scale(sign, x) for x in bar_chi]
        squares = [differential(images[i], images) for i in range(NG)]
        derivation = True
        for i in range(NG):
            for j in range(NG):
                derivation = derivation and differential(mul(GEN[i], GEN[j]), images) == \
                    add(mul(images[i], GEN[j]), scale(-1, mul(GEN[i], images[j])))
        expected_bar_square = [scale(2, add(*(mul(bar[j], chi2[j][i]) for j in range(4))))
                               if sign == -1 else {} for i in range(4)]
        results[name] = {"ghost_square_zero": all(not x for x in squares[:3]),
                         "dual_spinor_square_zero": all(not x for x in squares[3:]),
                         "left_odd_leibniz_on_generators": derivation,
                         "derived_formula_matches": squares[3:] == expected_bar_square,
                         "squared_dual_components": [serialize(x) for x in squares[3:]]}
    checks = {"mostly_plus_clifford_relations": clifford,
              "actual_spin_lorentz_rotation_commutators": lie,
              "exterior_product_all_128_by_128_basis_pairs": exterior,
              "ghost_CE_matrix_rule": ghost_ce,
              "archived_sign_is_nonzero_negative_control": not results["archived_right_minus"]["dual_spinor_square_zero"],
              "corrected_sign_nilpotent_on_all_seven_generators": results["corrected_right_plus"]["ghost_square_zero"] and results["corrected_right_plus"]["dual_spinor_square_zero"],
              "both_formulas_match_left_odd_Leibniz": all(r["derived_formula_matches"] and r["left_odd_leibniz_on_generators"] for r in results.values())}
    report = {"coefficient_domain": "exact Q(i), SymPy rational/integer coefficients",
              "convention": "left odd derivation; three odd Lorentz rotation ghosts and four odd dual-spinor generators",
              "checks": checks, "results": results,
              "interpretation": "The archived right-ghost minus sign fails fermionic dual-spinor nilpotency in the actual four-dimensional spin representation. Corrected plus sign is nilpotent in this pure Lorentz sector.",
              "non_claims": ["No fresh Lean kernel check", "No complete gravity BV antibracket computation", "No diffeomorphism or U(1) sector tested", "No quantum master equation or anomaly result"]}
    out = Path(__file__).resolve().parents[1] / "evidence/gravity/brst_parity_results.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n")
    assert all(checks.values()), checks
    print(json.dumps({"checks": len(checks), "all_pass": True, "output": str(out)}))


if __name__ == "__main__":
    main()
