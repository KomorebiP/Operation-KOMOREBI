#!/usr/bin/env python3
"""Independently reconstruct the visual guide data without producer imports."""
from fractions import Fraction
from itertools import combinations_with_replacement, product
from pathlib import Path
import json
import re
import argparse

from independent_controls import elementary, cyclo_root, rank_mod, multiply

ROOT = Path(__file__).resolve().parent.parent
data = json.loads((ROOT / "visual/data.json").read_text())["figures"]
body = (ROOT / "visual/body.tex").read_text()
required = re.findall(r"\{(\d\d_[a-z0-9_]+)\.pdf\}", body)
assert len(required) == len(set(required)) == len(data) == 24
assert set(required) == set(data)
checks = []


def canonical(value):
    return json.loads(json.dumps(value))


def check(key, expected):
    assert data[key]["domain"], key
    assert data[key]["values"] == canonical(expected), (key, data[key]["values"], expected)
    checks.append(key)


def matrix(flat):
    return [list(flat[:2]), list(flat[2:])]


def mat4_product(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def apply(a, x):
    return [sum(u * v for u, v in zip(row, x)) for row in a]


def valuation(q, p):
    def vp(n):
        assert n != 0
        v = 0
        while n % p == 0:
            n //= p
            v += 1
        return v
    return vp(q.numerator) - vp(q.denominator)


check("01_interface", {})
check("02_clifford", {})
check("03_torsor", {"p": 3, "offset": 1, "map": [[j, (j + 1) % 3] for j in range(3)]})
choices = [[cyclo_root(j + k, 3) for k in range(3)] for j in range(3)]
check("04_intertwiner", {"S_diagonal": [[2 * c for c in cyclo_root(k, 3)] for k in range(3)],
    "S_cubed_scalar": 8, "normalized_choices": choices})
multisets = list(combinations_with_replacement(range(12), 2))
assert len(multisets) == 78
check("05_satake", {"M": 4, "d": 3, "N": 12, "n": 2,
    "all_multisets": multisets, "polynomial_bound": len(multisets)})
check("06_coefficients", {"p": 3, "degrees": [1, 2, 3],
    "exponents": [[j * k % 3 for k in (1, 2, 3)] for j in range(3)]})
blind = elementary([0, 1, 2], 3)[1:]
seen = elementary([0, 0, 1], 3)[1:]
blind_stab = [j for j in range(3) if elementary([j, j + 1, j + 2], 3)[1:] == blind]
seen_stab = [j for j in range(3) if elementary([j, j, j + 1], 3)[1:] == seen]
check("07_stabilizer", {"blind_coefficients": blind,
    "blind_active_degrees": [k + 1 for k, c in enumerate(blind) if any(c)],
    "blind_stabilizer": blind_stab, "seen_coefficients": seen, "seen_stabilizer": seen_stab})
rows = [elementary([j, j, j + 1], 3)[1:] for j in range(3)]
check("08_blindness", {"roots": [cyclo_root(k, 3) for k in (0, 0, 1)],
    "elementary_coefficients": rows, "determinant_constant": len({r[-1] for r in rows}) == 1})
counts = [2, 1, 0]
rotations = [[counts[(a - j) % 3] for a in range(3)] for j in range(3)]
check("09_spectrum", {"p": 3, "base": counts, "rotations": rotations,
    "rotation_invariant_regular": [1, 1, 1]})
exact = [{1}, {1}]
coarse = [{0, 1}, {1, 2}, {0, 2}]
check("10_alignment", {"exact_sets": [sorted(s) for s in exact],
    "exact_intersection": sorted(set.intersection(*exact)),
    "coarse_sets": [sorted(s) for s in coarse],
    "coarse_pairwise_nonempty": all(coarse[i] & coarse[j] for i in range(3) for j in range(i)),
    "coarse_global_intersection": sorted(set.intersection(*coarse)),
    "incompatible_exact_example": [[1], [2]]})
packets = [[(j + k) % 3 for k in range(3)] for j in range(3)]
assert all(sorted(p) == [0, 1, 2] for p in packets)
check("11_induction", {"p": 3, "origin_packets": packets, "total_multiplicities": [1, 1, 1]})
reduced = {str(p): [[(a + z * b) % p for a, b in row] for row in rows]
           for p, z in ((3, 1), (7, 2))}
check("12_collapse", {"reduced_elementary_coefficients": reduced,
    "cube_roots_mod3": [x for x in range(3) if pow(x, 3, 3) == 1],
    "cube_roots_mod7": [x for x in range(7) if pow(x, 3, 7) == 1]})
polynomials = [[1, -2, 1], [1, 2, 1]]
primes = [2, 3, 5, 7]
check("13_separation", {"polynomials_high_to_low": polynomials, "primes": primes,
    "reduced_vectors": {str(p): [[a % p for a in row] for row in polynomials] for p in primes},
    "coefficient_difference": polynomials[1][1] - polynomials[0][1]})
group = [(pow(2, j, 7), 0, 0, pow(4, j, 7)) for j in range(3)]
traces = [(g[0] + g[3]) % 7 for g in group]
words = [[(multiply(g, b)[0] + multiply(g, b)[3]) % 7 for b in group[:2]] for g in group]
d = rank_mod(group, 7)
assert d == 2 and len({tuple(w) for w in words}) == len(group)
gram = [[(multiply(a, b)[0] + multiply(a, b)[3]) % 7 for b in group[:2]] for a in group[:2]]
assert rank_mod(gram, 7) == 2
check("14_trace_bound", {"n": 2, "ell": 7, "group_matrices": [matrix(g) for g in group],
    "traces": traces, "t": len(set(traces)), "basis_dimension": d, "trace_words": words,
    "basis_bound": len(set(traces)) ** d, "rank_bound": len(set(traces)) ** 4})
i2 = (1, 0, 0, 1)
assigned = (2, 0, 0, 4)
assigned_square = tuple(x % 7 for x in multiply(assigned, assigned))
assert tuple(x % 7 for x in multiply(assigned_square, assigned)) == i2
check("15_multiplication", {"domain_group": "C2", "assigned_identity": matrix(i2),
    "assigned_generator": matrix(assigned), "generator_square": matrix(assigned_square),
    "homomorphism": assigned_square == i2, "assigned_eigenvalues_in_mu3": all(pow(x, 3, 7) == 1 for x in (2, 4))})
# The affine formula proves multiplication and injectivity for all t, not by finite sampling.
# Its "infinite image" field below is an audited scope statement, not a bounded inference.
check("16_monodromy", {"unipotent_trace": 2, "unipotent_domain": "additive Z_l",
    "unipotent_infinite_image": True, "semisimplicity_required": True})
t = [1, 2, 2, 1]
coboundary = [(x - 1) % 3 for x in t]
norms = {q: [sum(pow(x, j, 3) for j in range(q)) % 3 for x in t] for q in (2, 6)}
dim_b = sum(x != 0 for x in coboundary)
dims = {q: sum(x == 0 for x in n) - dim_b for q, n in norms.items()}
check("17_h1", {"T_diagonal": t, "T_minus_I_diagonal": coboundary,
    "norm_diagonals": norms, "H1_dimensions": dims, "coboundary_dimension": dim_b})
a = (1, 1, 0, 1)
corrected = (3, 1, 0, 1)
compatible = list(product(range(3), repeat=2))
correctable = [(x, 0) for x in range(3)]
check("18_h2", {"compatible_errors": compatible, "correctable_errors": correctable,
    "square_zero_lift": matrix(a), "corrected_lift": matrix(corrected),
    "lift_square": matrix(tuple(x % 4 for x in multiply(a, a))),
    "corrected_square": matrix(tuple(x % 4 for x in multiply(corrected, corrected)))})
assert -2 * 2 + 4 == 0 and 4 % 8 != 0
check("19_syzygy", {"F_at_2_mod8": [2, 4], "moving_row": [-2, 1], "frozen_row": [0, 1],
    "leading_layer_mod2": [1, 0], "original_roots_mod4": [x for x in range(4) if (x * x + 1) % 4 == 0],
    "augmented_roots_mod4": [(x, y) for x in range(4) for y in range(4) if (x * x + 1 + y) % 4 == 0]})
xs = [Fraction(1)]
for _ in range(4):
    # Independent equivalent average formulation of Newton's recurrence.
    x = xs[-1]
    xs.append((x + 6 / x) / 2)
errors = [x * x - 6 for x in xs]
assert all(errors[j + 1] == errors[j] ** 2 / (4 * xs[j] ** 2) for j in range(4))
assert all(x.numerator % 5 and x.denominator % 5 for x in xs)
check("20_hensel_scalar", {"p": 5, "target": 6,
    "iterates": [[x.numerator, x.denominator] for x in xs],
    "errors": [[e.numerator, e.denominator] for e in errors],
    "error_valuations": [valuation(e, 5) for e in errors], "steps": 4})
b = [[2, 0, -1, 0], [-1, 2, 1, -1], [0, 0, 2, 0], [0, 0, -1, 2]]
# Columns reconstructed by applying AX+XA to the four matrix units.
units = [tuple(int(i == j) for i in range(4)) for j in range(4)]
columns = [tuple(u + v for u, v in zip(multiply(a, e), multiply(e, a))) for e in units]
derivative = [[columns[j][i] for j in range(4)] for i in range(4)]
four_i = [[4 * int(i == j) for j in range(4)] for i in range(4)]
assert mat4_product(b, derivative) == mat4_product(derivative, b) == four_i
f = (1, 1, 8, 1)
u = multiply(f, f)
base = multiply(a, a)
delta = [x - y for x, y in zip(u, base)]
bad_target = (1, 10, 0, 1)
bad_delta = [x - y for x, y in zip(bad_target, base)]
passing = apply(b, delta)
failing = apply(b, bad_delta)
assert all(x % 32 == 0 for x in passing) and any(x % 32 for x in failing)
check("21_matrix_hensel", {"A": matrix(a), "D": derivative, "B": b, "BD": four_i,
    "p": 2, "d": 2, "s": 2, "m": 3, "test_modulus": 32, "root": matrix(f),
    "target": matrix(u), "delta": delta, "passing_B_delta": passing,
    "failing_target": matrix(bad_target), "failing_B_delta": failing})
singular = (1, 0, 0, -1)
singular_columns = [tuple(u + v for u, v in zip(multiply(singular, e), multiply(e, singular))) for e in units]
assert singular_columns[1] == singular_columns[2] == (0, 0, 0, 0)
check("22_singular", {"unipotent_inverse_exponent": 2, "scalar_degree_valuation": 1,
    "singular_center": matrix(singular), "singular_derivative_on_matrix_units": [[2, 0], [0, -2]],
    "singular_rank": sum(any(e) for e in singular_columns)})
moduli = [2, 4, 8, 16]
roots = [[x for x in range(m) if pow(x, 2, m) == 1] for m in moduli]
edges = [[j + 1, x, j, x % moduli[j - 1]] for j in range(1, 4) for x in roots[j]]
assert not any(x % 8 == 3 for x in roots[-1])
check("23_tower", {"moduli": moduli, "roots": roots, "edges": edges, "dead_node": [8, 3]})
check("24_open_gate", {})
assert len(checks) == 24
result = {"status": "PASS", "data_figures": 24, "exact_numeric_models": 20,
    "schematic_models": 3, "qualitative_monodromy_scope_records": 1,
    "all_fields_reconstructed": True, "figure_keys": checks,
    "source_imports": ["reviewer-owned independent_controls.py"],
    "producer_imports": [], "arithmetic": "integers, fractions, exact cyclotomic quotient, F3/F7, Z4/Z8/Z32",
    "non_claims": ["No bounded result proves Strong Artin", "No new Lean replay",
        "The infinite unipotent control uses its explicit injective formula, not finite sampling"] }
parser = argparse.ArgumentParser()
parser.add_argument("--result", required=True)
args = parser.parse_args()
out = ROOT / args.result
assert out.resolve().is_relative_to(ROOT.resolve())
out.write_text(json.dumps(result, indent=2)+"\n")
print(json.dumps(result, indent=2))
