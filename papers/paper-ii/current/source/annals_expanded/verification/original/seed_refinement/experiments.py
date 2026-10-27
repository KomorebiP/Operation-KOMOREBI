from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import sympy as sp

from .dyadic import delayed_separation_example, odd_prime_sign_projectors, resultant_weight, smith_diagonal_solve
from .projectors import (
    analyze_residues,
    residue_projectors,
    root_of_unity_projectors,
    synthesize_residues,
    verify_crt_factorization,
    verify_refinement,
)
from .smith_chart import gamma_from_impedance, phase_transform, polyphase_orbit, smith_weight
from .stability import (
    compatible_replication_tower,
    defect_norm_bound,
    power_defect,
    power_defect_expansion,
    resolvent_defect,
)
from .weighted import Edge, direct_inverse_mod, neumann_inverse_mod, path_counts, path_zeta, zeta_coefficients


def _graph() -> list[Edge]:
    return [
        Edge(0, 0, 2),
        Edge(0, 1, 1),
        Edge(1, 1, 3),
        Edge(1, 2, 2),
        Edge(2, 0, 1),
        Edge(2, 2, 4),
    ]


def run_experiments(output: str | Path | None = None) -> dict[str, object]:
    rng = np.random.default_rng(20260726)
    x = rng.normal(size=97)

    packet_residuals: dict[str, float] = {}
    for modulus in (2, 3, 4, 6, 8, 12):
        packets = analyze_residues(x, modulus)
        packet_residuals[str(modulus)] = float(np.linalg.norm(synthesize_residues(packets) - x))

    refinement_residuals = {
        f"{coarse}_to_{fine}": verify_refinement(128, coarse, fine)
        for coarse, fine in [(2, 4), (2, 8), (3, 6), (3, 12), (4, 8), (4, 12), (6, 12)]
    }

    root_projector_residuals: dict[str, float] = {}
    for order in (2, 3, 4, 5, 8, 12):
        ps = root_of_unity_projectors(order)
        identity = np.eye(order)
        residual = float(np.linalg.norm(sum(ps) - identity))
        residual = max(residual, *(float(np.linalg.norm(p @ p - p)) for p in ps))
        root_projector_residuals[str(order)] = residual

    crt_residuals = {
        "4x3": verify_crt_factorization(145, 4, 3),
        "8x3": verify_crt_factorization(193, 8, 3),
        "4x5": verify_crt_factorization(241, 4, 5),
        "8x5": verify_crt_factorization(321, 8, 5),
    }

    t = sp.Symbol("t")
    zeta = sp.cancel(path_zeta(3, _graph(), [0], [2], t))
    enumerated = path_counts(3, _graph(), [0], [2], 30)
    expanded = zeta_coefficients(zeta, t, 30)

    inverse_records: dict[str, object] = {}
    for prime, depth in [(2, 10), (3, 8), (5, 7)]:
        D = np.diag([1, 1 + prime, 1 + 2 * prime]).astype(object)
        K = np.array(
            [
                [0, prime, prime**3],
                [prime**2, 0, prime],
                [prime**3, prime**2, 0],
            ],
            dtype=object,
        )
        modulus = prime**depth
        direct = direct_inverse_mod(D, K, prime, depth)
        filtered = neumann_inverse_mod(D, K, prime, depth)
        residual = ((D + K) @ filtered - np.eye(3, dtype=object)) % modulus
        inverse_records[str(prime)] = {
            "depth": depth,
            "modulus": modulus,
            "max_residual": int(max(abs(int(v)) for v in residual.flat)),
            "difference_from_direct": int(max(abs(int(v)) for v in ((filtered - direct) % modulus).flat)),
        }

    delayed = delayed_separation_example()
    xvar = sp.Symbol("x")
    f = sp.Poly(xvar - 1, xvar)
    g = sp.Poly(xvar + 1, xvar)
    odd_plus, odd_minus = odd_prime_sign_projectors(np.array([[1, 1], [0, -1]], dtype=int), 5)
    smith_good = smith_diagonal_solve([0, 1, 3], [1, 2, 8], 2, 6)
    smith_bad = smith_diagonal_solve([0, 1, 3], [1, 2, 4], 2, 6)

    E, C, Tf, Tc = compatible_replication_tower(np.array([0.4, 0.8, 1.3]), 4)
    exact_defect = float(np.linalg.norm(power_defect(C, Tf, Tc)))
    Tf_perturbed = Tf.copy()
    Tf_perturbed[0, 0] += 0.09
    defect_power_records = []
    for n in range(1, 10):
        lhs = C @ np.linalg.matrix_power(Tf_perturbed, n) - np.linalg.matrix_power(Tc, n) @ C
        rhs = power_defect_expansion(C, Tf_perturbed, Tc, n)
        actual, bound = defect_norm_bound(C, Tf_perturbed, Tc, n)
        defect_power_records.append(
            {
                "power": n,
                "identity_residual": float(np.linalg.norm(lhs - rhs)),
                "actual": actual,
                "bound": bound,
            }
        )
    lhs, rhs = resolvent_defect(C, Tf_perturbed, Tc, 3.1 + 0.7j)

    z = 2.0 + 1.0j
    smith_phase = phase_transform(z, 2, 1)
    orbit = polyphase_orbit(0.73, 16)
    orbit_radius_residual = float(max(abs(abs(gamma_from_impedance(value)) - 0.73) for value in orbit))

    results: dict[str, object] = {
        "author": "Komorebi P.",
        "paper": "Projector-Resolved Seed Calculus II",
        "packet_reconstruction_residuals": packet_residuals,
        "refinement_residuals": refinement_residuals,
        "root_projector_residuals": root_projector_residuals,
        "crt_factorization_residuals": crt_residuals,
        "path_zeta": {
            "expression": str(zeta),
            "enumerated_counts": enumerated,
            "series_counts": expanded,
            "match": enumerated == expanded,
        },
        "weighted_inverse": inverse_records,
        "dyadic": {
            "plus_projector": [[str(v) for v in row] for row in delayed["plus"].tolist()],
            "minus_projector": [[str(v) for v in row] for row in delayed["minus"].tolist()],
            "plus_idempotent": bool(delayed["plus_idempotent"]),
            "minus_idempotent": bool(delayed["minus_idempotent"]),
            "orthogonal": bool(delayed["orthogonal"]),
            "resultant_weight_at_2": list(resultant_weight(f, g, 2)),
            "resultant_weight_at_3": list(resultant_weight(f, g, 3)),
            "odd_prime_plus_projector_mod_5": odd_plus.tolist(),
            "odd_prime_minus_projector_mod_5": odd_minus.tolist(),
            "smith_good": {
                "solvable": smith_good.solvable,
                "solution_count": smith_good.solution_count,
                "coordinate_counts": list(smith_good.coordinate_counts),
            },
            "smith_bad_solvable": smith_bad.solvable,
        },
        "refinement_stability": {
            "exact_defect": exact_defect,
            "power_records": defect_power_records,
            "resolvent_identity_residual": float(np.linalg.norm(lhs - rhs)),
        },
        "smith_chart": {
            "two_phase_value": [float(smith_phase.real), float(smith_phase.imag)],
            "expected_admittance": [float((1 / z).real), float((1 / z).imag)],
            "orbit_radius_residual": orbit_radius_residual,
            "symmetric_weight_residual": float(abs(smith_weight(0.2 + 0.4j) - smith_weight(-0.2 - 0.4j))),
        },
    }

    if output is not None:
        path = Path(output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(results, indent=2, sort_keys=True), encoding="utf-8")
    return results
