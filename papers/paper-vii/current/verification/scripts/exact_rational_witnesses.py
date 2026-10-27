#!/usr/bin/env python3
"""Small exact rational witnesses for Paper VII; no theorem or Lean certification.

Run: python3 exact_rational_witnesses.py --out exact_rational_witnesses.json
Only Python's standard library is used. Matrix arithmetic uses Fraction.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as F
from itertools import combinations
import json
from pathlib import Path
import platform
import sys


def mat(rows):
    return [[F(x) for x in row] for row in rows]


def zeros(n, m):
    return [[F(0) for _ in range(m)] for _ in range(n)]


def eye(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def transpose(a):
    return [list(row) for row in zip(*a)]


def add(a, b):
    return [[x + y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def scale(c, a):
    return [[F(c) * x for x in row] for row in a]


def sub(a, b):
    return add(a, scale(-1, b))


def mul(a, b):
    if len(a[0]) != len(b):
        raise ValueError("matrix product dimensions disagree")
    return [[sum((x * y for x, y in zip(row, col)), F(0))
             for col in zip(*b)] for row in a]


def trace(a):
    return sum((a[i][i] for i in range(len(a))), F(0))


def block(a, b, c, d):
    return [x + y for x, y in zip(a, b)] + [x + y for x, y in zip(c, d)]


def kron(a, b):
    return [[x * y for x in ar for y in br] for ar in a for br in b]


def rref(a):
    out = [row[:] for row in a]
    pivot_cols = []
    row = 0
    for col in range(len(out[0])):
        pivot = next((i for i in range(row, len(out)) if out[i][col]), None)
        if pivot is None:
            continue
        out[row], out[pivot] = out[pivot], out[row]
        out[row] = [x / out[row][col] for x in out[row]]
        for i in range(len(out)):
            if i != row and out[i][col]:
                out[i] = [x - out[i][col] * y for x, y in zip(out[i], out[row])]
        pivot_cols.append(col)
        row += 1
        if row == len(out):
            break
    return out, pivot_cols


def rank(a):
    return len(rref(a)[1])


def inverse(a):
    n = len(a)
    reduced, pivots = rref([row + identity for row, identity in zip(a, eye(n))])
    if pivots[:n] != list(range(n)):
        raise ValueError("singular matrix")
    return [row[n:] for row in reduced]


def nullspace(a):
    reduced, pivots = rref(a)
    free = [j for j in range(len(a[0])) if j not in pivots]
    vectors = []
    for j in free:
        vector = [F(0) for _ in a[0]]
        vector[j] = F(1)
        for row, pivot in enumerate(pivots):
            vector[pivot] = -reduced[row][j]
        vectors.append(vector)
    return vectors


def det(a):
    """Cofactor determinant, independent of the elimination rank/inverse code."""
    n = len(a)
    if n == 1:
        return a[0][0]
    return sum(((-1) ** j * a[0][j] *
                det([row[:j] + row[j + 1:] for row in a[1:]])
                for j in range(n)), F(0))


def vec(a):
    return [x for row in a for x in row]


def outer(v):
    return [[x * y for y in v] for x in v]


def column(v):
    return [[x] for x in v]


def encode(x):
    if isinstance(x, F):
        return str(x)
    if isinstance(x, dict):
        return {key: encode(value) for key, value in x.items()}
    if isinstance(x, (list, tuple)):
        return [encode(y) for y in x]
    return x


class Audit:
    def __init__(self):
        self.assertions = []
        self.records = {}

    def check(self, name, condition):
        self.assertions.append({"name": name, "passed": bool(condition)})
        if not condition:
            raise AssertionError(name)


def arithmetic_benchmarks(audit):
    audit.check("arithmetic.rank_dependent_rows", rank(mat([[1, 2], [2, 4]])) == 1)
    test = mat([[2, 1], [1, 1]])
    audit.check("arithmetic.hand_inverse", inverse(test) == mat([[1, -1], [-1, 2]]))
    audit.check("arithmetic.det_independent", det(test) == 1)
    ns = nullspace(mat([[1, 2], [2, 4]]))
    audit.check("arithmetic.hand_nullspace", ns == [[F(-2), F(1)]])
    try:
        inverse(mat([[1, 2], [2, 4]]))
    except ValueError:
        rejected = True
    else:
        rejected = False
    audit.check("arithmetic.reject_singular_inverse", rejected)


def projector_and_involution(audit):
    u, w = [F(3, 5), F(4, 5)], [F(-4, 5), F(3, 5)]
    p, q, h = outer(u), outer(w), mat([[1, 0], [0, -1]])
    b = mul(mul(q, h), p)
    compressed = mul(mul(p, h), p)
    commutator = sub(mul(h, p), mul(p, h))
    audit.check("projector.complete_orthogonal", add(p, q) == eye(2) and mul(p, q) == zeros(2, 2))
    audit.check("projector.symmetric_idempotent", transpose(p) == p and mul(p, p) == p and mul(q, q) == q)
    audit.check("projector.rank_one", rank(p) == rank(q) == 1)
    audit.check("involution.selfadjoint_square", transpose(h) == h and mul(h, h) == eye(2))
    audit.check("compression.scalar", compressed == scale(F(-7, 25), p))
    audit.check("compression.norm_squared_certificate", mul(transpose(compressed), compressed) == scale(F(49, 625), p))
    audit.check("compression.contractive", F(49, 625) <= 1)
    audit.check("off_block.norm_squared_certificate", mul(transpose(b), b) == scale(F(576, 625), p))
    audit.check("commutator.norm_squared_certificate", mul(transpose(commutator), commutator) == scale(F(576, 625), eye(2)))
    audit.check("compression.pythagorean", F(49, 625) + F(576, 625) == 1)
    points = [(F(1), F(0)), (F(0), F(1)), (F(3, 5), F(4, 5)),
              (F(5, 13), F(12, 13)), (F(3, 5), F(-4, 5))]
    cases = []
    for i, (c, s) in enumerate(points):
        # U = R + i I_imag, where R=c I and I_imag=-s H.
        # Unitarity is certified by its two rational real/imaginary identities.
        real, imaginary = scale(c, eye(2)), scale(-s, h)
        audit.check(f"propagator.{i}.unit_circle", c * c + s * s == 1)
        audit.check(f"propagator.{i}.unitary_real", add(mul(transpose(real), real), mul(transpose(imaginary), imaginary)) == eye(2))
        audit.check(f"propagator.{i}.unitary_imaginary", sub(mul(transpose(real), imaginary), mul(transpose(imaginary), real)) == zeros(2, 2))
        real_leak = mul(mul(q, real), p)
        imag_leak = mul(mul(q, imaginary), p)
        audit.check(f"propagator.{i}.leakage_certificate", real_leak == zeros(2, 2) and mul(transpose(imag_leak), imag_leak) == scale(s * s * F(576, 625), p))
        cases.append({"cosine": c, "sine": s, "leakage_norm_squared": s * s * F(576, 625)})
    bad = [row[:] for row in p]
    bad[0][0] += F(1, 25)
    audit.check("negative_control.projector_perturbation_rejected", mul(bad, bad) != bad)
    audit.records["projector_involution"] = {
        "P": p, "Q": q, "H": h, "compression_norm_squared": F(49, 625),
        "off_block_norm_squared": F(576, 625), "rational_circle_points": cases,
        "interpretation": "Closed involution propagator algebra only; no time inequality is evaluated."}


def unit_matrix(d, i, j):
    out = zeros(d, d)
    out[i][j] = F(1)
    return out


def seed_matrices(d, m, k):
    seeds = []
    for j in range(k):
        seed = zeros(d, m)
        for row in range(d):
            multiplicity = j * d + row
            if multiplicity < m:
                seed[row][multiplicity] = F(1)
        seeds.append(seed)
    return seeds


def orbit_rows(seeds, d):
    return [vec(mul(unit_matrix(d, i, j), seed))
            for seed in seeds for i in range(d) for j in range(d)]


def seed_witnesses(audit):
    cases = []
    for d in range(1, 5):
        for m in range(1, 5):
            k = (m + d - 1) // d
            seeds = seed_matrices(d, m, k)
            prefix = f"seed.d{d}.m{m}"
            audit.check(prefix + ".stacked_multiplicity_rank", rank([row for seed in seeds for row in seed]) == m)
            audit.check(prefix + ".explicit_full_orbit", rank(orbit_rows(seeds, d)) == d * m)
            # This is the numeric capacity obstruction for k-1 seeds. The
            # universal row-space argument itself remains a mathematical proof.
            audit.check(prefix + ".lower_capacity", (k - 1) * d < m <= k * d)
            individual_ranks = []
            for i, seed in enumerate(seeds):
                cr, orbit_rank = rank(seed), rank(orbit_rows([seed], d))
                audit.check(prefix + f".one_seed_{i}_orbit_rank", orbit_rank == d * cr)
                individual_ranks.append({"coefficient_rank": cr, "orbit_dimension": orbit_rank})
            cases.append({"d": d, "m": m, "constructed_seed_count": k,
                          "full_dimension": d * m, "individual_seeds": individual_ranks})
    # Nontrivial direct sum: central summand projections permit independent
    # algebra matrices on each of (M_2 tensor I_3) and (M_1 tensor I_2).
    summands, k = [(2, 3), (1, 2)], 2
    dimension = sum(d * m for d, m in summands)
    rows = []
    offset = 0
    for d, m in summands:
        for row in orbit_rows(seed_matrices(d, m, k), d):
            rows.append([F(0)] * offset + row + [F(0)] * (dimension - offset - d * m))
        offset += d * m
    audit.check("seed.direct_sum.explicit_full_orbit", rank(rows) == dimension)
    audit.check("seed.direct_sum.capacity", all((k - 1) * d < m for d, m in summands))
    audit.records["seed_rank"] = {
        "basis_order": "row-major (representation index, multiplicity index); direct sums in listed order",
        "single_summand_cases": cases, "direct_sum": {"summands": summands, "seeds": k, "hull_dimension": rank(rows)}}


def channel(kraus, x):
    result = zeros(len(kraus[0]), len(kraus[0]))
    for k in kraus:
        result = add(result, mul(mul(k, x), transpose(k)))
    return result


def choi_from_channel(kraus):
    n, out = 2, zeros(4, 4)
    for i in range(n):
        for j in range(n):
            out = add(out, kron(channel(kraus, unit_matrix(n, i, j)), unit_matrix(n, i, j)))
    return out


def partial_trace_output(j):
    return [[sum((j[2 * a + i][2 * a + k] for a in range(2)), F(0))
             for k in range(2)] for i in range(2)]


def channel_witnesses(audit):
    parameters = [(F(1), F(0)), (F(0), F(1)), (F(4, 5), F(3, 5)),
                  (F(3, 5), F(4, 5)), (F(5, 13), F(12, 13))]
    u = mat([[1, 0], [0, -1]])
    rho = mat([[F(3, 5), F(1, 5)], [F(1, 5), F(2, 5)]])
    cases = []
    for case, (retained, damped) in enumerate(parameters):
        prefix = f"channel.{case}"
        kraus = [mat([[1, 0], [0, retained]]), mat([[0, damped], [0, 0]])]
        audit.check(prefix + ".circle", retained * retained + damped * damped == 1)
        completeness = add(mul(transpose(kraus[0]), kraus[0]), mul(transpose(kraus[1]), kraus[1]))
        audit.check(prefix + ".kraus_trace_preserving", completeness == eye(2))
        j = choi_from_channel(kraus)
        gram = add(outer(vec(kraus[0])), outer(vec(kraus[1])))
        audit.check(prefix + ".independent_choi_gram", j == gram)
        audit.check(prefix + ".choi_symmetric", transpose(j) == j)
        minors = []
        for size in range(1, 5):
            for indices in combinations(range(4), size):
                minor = det([[j[i][k] for k in indices] for i in indices])
                minors.append({"indices": list(indices), "determinant": minor})
        audit.check(prefix + ".all_15_principal_minors_nonnegative", all(x["determinant"] >= 0 for x in minors))
        audit.check(prefix + ".choi_partial_trace", partial_trace_output(j) == eye(2))
        audit.check(prefix + ".choi_rank", rank(j) == (1 if damped == 0 else 2))
        sym = kron(u, u)
        audit.check(prefix + ".choi_involution_symmetry", mul(mul(sym, j), transpose(sym)) == j)
        for i in range(2):
            for k in range(2):
                x = unit_matrix(2, i, k)
                audit.check(prefix + f".basis_trace_{i}{k}", trace(channel(kraus, x)) == F(i == k))
                audit.check(prefix + f".basis_covariance_{i}{k}", channel(kraus, mul(mul(u, x), u)) == mul(mul(u, channel(kraus, x)), u))
        out_rho = channel(kraus, rho)
        audit.check(prefix + ".density_example", trace(out_rho) == 1 and out_rho[0][0] >= 0 and out_rho[1][1] >= 0 and det(out_rho) >= 0)
        audit.check(prefix + ".unital_iff_zero_damping", (channel(kraus, eye(2)) == eye(2)) == (damped == 0))
        cases.append({"retained_amplitude": retained, "damping_amplitude": damped,
                      "damping_probability": damped * damped, "kraus": kraus,
                      "choi": j, "principal_minors": minors, "density_output": out_rho})
    broken_kraus = [mat([[1, 0], [0, F(4, 5)]]), mat([[0, F(4, 5)], [0, 0]])]
    audit.check("negative_control.non_tp_kraus_rejected", add(mul(transpose(broken_kraus[0]), broken_kraus[0]), mul(transpose(broken_kraus[1]), broken_kraus[1])) != eye(2))
    audit.records["amplitude_damping"] = {"choi_basis": "output tensor input; vec(K) is row-major",
                                           "covariance": "U=diag(1,-1)", "cases": cases}


def feshbach_witnesses(audit):
    families = [
        {"name": "rank_one_2x2", "A": mat([[1]]), "B": mat([[2]]), "D": mat([[4]]),
         "zs": [-1, 0, 1, 2, 3, 5, 6], "eigenvalues": [0, 5]},
        {"name": "rank_one_3x3", "A": mat([[1, 2], [2, 4]]), "B": mat([[3], [6]]), "D": mat([[9]]),
         "zs": [-1, 0, 1, 2, 5, 10, 14], "eigenvalues": [0, 14]},
    ]
    results = []
    for family in families:
        a, b, d = family["A"], family["B"], family["D"]
        p, q = len(a), len(d)
        h = block(a, b, transpose(b), d)
        prefix, cases = "feshbach." + family["name"], []
        audit.check(prefix + ".selfadjoint", transpose(h) == h)
        for z in map(F, family["zs"]):
            zp = sub(scale(z, eye(p)), a)
            zq = sub(scale(z, eye(q)), d)
            zq_inv = inverse(zq)
            sigma = mul(mul(b, zq_inv), transpose(b))
            f = sub(zp, sigma)
            full = sub(scale(z, eye(p + q)), h)
            left = block(eye(p), mul(b, zq_inv), zeros(q, p), eye(q))
            right = block(eye(p), zeros(p, q), mul(zq_inv, transpose(b)), eye(q))
            diag = block(f, zeros(p, q), zeros(q, p), zq)
            audit.check(prefix + f".z{z}.block_elimination", mul(mul(left, full), right) == diag)
            audit.check(prefix + f".z{z}.det_factorization", det(full) == det(zq) * det(f))
            entry = {"z": z, "F": f, "self_energy": sigma,
                     "full_determinant": det(full), "F_determinant": det(f)}
            if z in family["eigenvalues"]:
                f_basis = nullspace(f)
                full_basis = nullspace(full)
                lifted = []
                for x in f_basis:
                    y = mul(mul(zq_inv, transpose(b)), column(x))
                    lifted.append(x + [row[0] for row in y])
                audit.check(prefix + f".z{z}.kernel_dimensions", len(f_basis) == len(full_basis) and len(f_basis) > 0)
                audit.check(prefix + f".z{z}.lifted_vectors", all(mul(full, column(v)) == zeros(p + q, 1) for v in lifted))
                audit.check(prefix + f".z{z}.lift_is_basis", rank(lifted) == len(full_basis))
                audit.check(prefix + f".z{z}.projection_inverse", [v[:p] for v in lifted] == f_basis)
                entry.update({"kernel_dimension": len(f_basis), "F_kernel_basis": f_basis,
                              "lifted_full_kernel_basis": lifted})
            else:
                full_inv, f_inv = inverse(full), inverse(f)
                retained_inv = [row[:p] for row in full_inv[:p]]
                audit.check(prefix + f".z{z}.projected_resolvent", retained_inv == f_inv)
                audit.check(prefix + f".z{z}.two_sided_inverse", mul(full, full_inv) == eye(p + q) and mul(full_inv, full) == eye(p + q))
                entry["retained_resolvent"] = retained_inv
            cases.append(entry)
        results.append({"name": family["name"], "H": h, "retained_dimension": p,
                        "hidden_dimension": q, "cases": cases})
    # The 2x2 witness at z=0 has true lift (1,-1/2); opposite sign must fail.
    full = scale(-1, mat([[1, 2], [2, 4]]))
    audit.check("negative_control.opposite_feshbach_lift_sign_rejected", mul(full, column([F(1), F(1, 2)])) != zeros(2, 1))
    audit.records["feshbach"] = results


def run():
    audit = Audit()
    arithmetic_benchmarks(audit)
    projector_and_involution(audit)
    seed_witnesses(audit)
    channel_witnesses(audit)
    feshbach_witnesses(audit)
    payload = {
        "schema": "paper-vii-exact-rational-witnesses-v1",
        "status": "finite_assertions_verified",
        "arithmetic_domain": "fractions.Fraction over Q; rational real/imaginary parts for involution propagators",
        "python": sys.version.split()[0], "implementation": platform.python_implementation(),
        "deterministic": True, "randomness": "none", "tolerance": "none",
        "bounds": {"projector_cases": 1, "rational_circle_points": 5,
                   "single_summand_seed_types": 16, "seed_d_range": [1, 4], "seed_m_range": [1, 4],
                   "direct_sum_seed_types": 1, "amplitude_damping_channels": 5,
                   "choi_principal_minors_per_channel": 15, "feshbach_families": 2,
                   "feshbach_parameter_values": 14, "feshbach_eigenvalue_parameters": 4,
                   "feshbach_resolvent_parameters": 10,
                   "maximum_square_operator_matrix_dimension": 4,
                   "largest_seed_hilbert_space_dimension": 16,
                   "maximum_rank_array_rows": 18, "maximum_rank_array_columns": 16},
        "assertion_count": len(audit.assertions),
        "passed_assertion_count": sum(x["passed"] for x in audit.assertions),
        "assertions": audit.assertions, "records": audit.records,
        "nonclaims": [
            "No Lean proof checking or formal theorem certification is performed.",
            "These are finitely many constructed examples, not exhaustive rational or complex matrix testing.",
            "The seed capacity inequality does not independently prove the uniform row-space argument.",
            "No exponential approximation, transcendental time value, or universal leakage inequality is tested.",
            "No upper-half-plane self-energy, memory-kernel, continuum, or unbounded-operator theorem is tested.",
            "No claim is made that source manuscripts or recovered outputs have been authenticated by these examples."]}
    return encode(payload)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path, help="JSON output path")
    args = parser.parse_args()
    payload = run()
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    # Serialization contract: exact rationals remain rational strings, and all
    # logical data survive a JSON round trip. Output is written only after pass.
    if json.loads(text) != payload:
        raise AssertionError("JSON round-trip mismatch")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"PASS: {payload['passed_assertion_count']}/{payload['assertion_count']} exact finite assertions; {args.out}")


if __name__ == "__main__":
    main()
