#!/usr/bin/env python3
"""Deterministic checks for the decomposition-robustness examples in SRWT.

The script verifies finite-dimensional instances of:
  1. exact workspace preservation under faithful coarse-graining;
  2. the two-scale coherence bound;
  3. Bayes-risk transport and coalition-count contraction under aggregation;
  4. secret-sharing trivialization of encoding-relative relationality; and
  5. a gatewise decomposition-transport robustness certificate.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np


TOL = 1e-10
RESULTS_DIR = Path(__file__).with_name("results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
OUT = RESULTS_DIR / "decomposition_robustness.json"


def nullspace(a: np.ndarray, tol: float = TOL) -> np.ndarray:
    """Return an orthonormal basis for ker(a)."""
    _, s, vh = np.linalg.svd(a, full_matrices=True)
    rank = int(np.sum(s > tol))
    return vh[rank:].T.copy()


def positive_spectral_gap(a: np.ndarray, tol: float = TOL) -> float:
    vals = np.linalg.eigvalsh(a.T @ a)
    positive = vals[vals > tol]
    if positive.size == 0:
        raise ValueError("operator has no positive eigenvalue")
    return float(positive.min())


def projector(basis: np.ndarray) -> np.ndarray:
    return basis @ basis.T


def entropy_from_probs(probs: np.ndarray, base: float = 2.0) -> float:
    probs = probs[probs > 0]
    return float(-np.sum(probs * np.log(probs) / math.log(base)))


def conditional_entropy(samples: list[tuple[Any, Any]], base: float = 2.0) -> float:
    """Compute H(Y|X) from equally weighted finite samples (x, y)."""
    grouped: dict[Any, list[Any]] = {}
    for x, y in samples:
        grouped.setdefault(x, []).append(y)
    total = len(samples)
    h = 0.0
    for ys in grouped.values():
        values, counts = np.unique(np.asarray(ys), return_counts=True)
        del values
        p_x = len(ys) / total
        h += p_x * entropy_from_probs(counts / counts.sum(), base=base)
    return float(h)


def mutual_information(samples: list[tuple[Any, Any]], base: float = 2.0) -> float:
    """Compute I(A;B) from equally weighted finite samples (a, b)."""
    a_vals = [a for a, _ in samples]
    b_vals = [b for _, b in samples]
    _, a_counts = np.unique(np.asarray(a_vals), return_counts=True)
    _, b_counts = np.unique(np.asarray(b_vals), return_counts=True)
    h_a = entropy_from_probs(a_counts / a_counts.sum(), base=base)
    h_b = entropy_from_probs(b_counts / b_counts.sum(), base=base)
    pair_counts: dict[tuple[Any, Any], int] = {}
    for pair in samples:
        pair_counts[pair] = pair_counts.get(pair, 0) + 1
    h_ab = entropy_from_probs(
        np.asarray(list(pair_counts.values()), dtype=float) / len(samples), base=base
    )
    return float(h_a + h_b - h_ab)


def check_faithful_coarse_graining() -> dict[str, Any]:
    # Four scalar nodes in an identity cycle. Blocks are {0,1} and {2,3}.
    d_internal = np.array(
        [
            [-1.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, -1.0, 1.0],
        ]
    )
    d_boundary = np.array(
        [
            [0.0, -1.0, 1.0, 0.0],
            [1.0, 0.0, 0.0, -1.0],
        ]
    )
    d_full = np.vstack([d_internal, d_boundary])

    inv_sqrt_2 = 1.0 / math.sqrt(2.0)
    j_pi = np.array(
        [
            [inv_sqrt_2, 0.0],
            [inv_sqrt_2, 0.0],
            [0.0, inv_sqrt_2],
            [0.0, inv_sqrt_2],
        ]
    )
    d_pi = d_boundary @ j_pi

    ker_full = nullspace(d_full)
    ker_pi = nullspace(d_pi)
    transported = j_pi @ ker_pi
    p_full = projector(ker_full)
    p_transported = projector(transported)
    projector_error = float(np.linalg.norm(p_full - p_transported, ord=2))

    assert ker_full.shape[1] == 1
    assert ker_pi.shape[1] == 1
    assert projector_error < 1e-9

    # Deterministic vector for the two-scale estimate.
    c = np.array([1.7, -0.2, 0.9, 2.4])
    p_pi = j_pi @ j_pi.T
    gamma_internal = positive_spectral_gap(d_internal)
    gamma_pi = positive_spectral_gap(d_pi)
    lhs = float(np.linalg.norm((np.eye(4) - p_full) @ c))
    rhs = float(
        np.linalg.norm(d_internal @ c) / math.sqrt(gamma_internal)
        + np.linalg.norm(d_pi @ j_pi.T @ p_pi @ c) / math.sqrt(gamma_pi)
    )
    assert lhs <= rhs + 1e-9

    return {
        "full_kernel_dimension": int(ker_full.shape[1]),
        "quotient_kernel_dimension": int(ker_pi.shape[1]),
        "workspace_projector_error": projector_error,
        "gamma_internal": gamma_internal,
        "gamma_quotient": gamma_pi,
        "two_scale_lhs": lhs,
        "two_scale_rhs": rhs,
        "two_scale_bound_holds": bool(lhs <= rhs + 1e-9),
    }


def check_risk_transport() -> dict[str, Any]:
    # Fine decomposition: two independent bit carriers. Target is parity.
    states = [(x1, x2, x1 ^ x2) for x1 in (0, 1) for x2 in (0, 1)]
    h_y_given_x1 = conditional_entropy([((x1,), y) for x1, _, y in states])
    h_y_given_x2 = conditional_entropy([((x2,), y) for _, x2, y in states])
    h_y_given_pair = conditional_entropy([((x1, x2), y) for x1, x2, y in states])

    # Coarse decomposition faithfully merges both carriers into one macro-node.
    h_y_given_coarse_singleton = h_y_given_pair
    assert abs(h_y_given_pair) < TOL
    assert abs(h_y_given_coarse_singleton - h_y_given_pair) < TOL
    assert abs(h_y_given_x1 - 1.0) < TOL
    assert abs(h_y_given_x2 - 1.0) < TOL

    fine_k0 = 2
    coarse_k0 = 1
    primitive_cost_fine = 2.0
    primitive_cost_coarse = 2.0

    return {
        "fine_singleton_risk_bits": [h_y_given_x1, h_y_given_x2],
        "fine_full_risk_bits": h_y_given_pair,
        "coarse_singleton_risk_bits": h_y_given_coarse_singleton,
        "risk_transport_error": abs(h_y_given_coarse_singleton - h_y_given_pair),
        "fine_minimal_coalition_size": fine_k0,
        "coarse_minimal_coalition_size": coarse_k0,
        "coalition_count_contracts": coarse_k0 <= fine_k0,
        "fine_sufficient_support_cost": primitive_cost_fine,
        "coarse_sufficient_support_cost": primitive_cost_coarse,
    }


def check_secret_sharing(group_size: int = 4) -> dict[str, Any]:
    samples = []
    for z in range(group_size):
        for k in range(group_size):
            x1 = k
            x2 = (z - k) % group_size
            samples.append((z, x1, x2))

    i_z_x1 = mutual_information([(z, x1) for z, x1, _ in samples])
    i_z_x2 = mutual_information([(z, x2) for z, _, x2 in samples])
    h_z_given_pair = conditional_entropy([((x1, x2), z) for z, x1, x2 in samples])
    h_z_given_x1 = conditional_entropy([((x1,), z) for z, x1, _ in samples])
    h_z_given_x2 = conditional_entropy([((x2,), z) for z, _, x2 in samples])
    expected = math.log2(group_size)

    assert abs(i_z_x1) < TOL
    assert abs(i_z_x2) < TOL
    assert abs(h_z_given_pair) < TOL
    assert abs(h_z_given_x1 - expected) < TOL
    assert abs(h_z_given_x2 - expected) < TOL

    return {
        "group_size": group_size,
        "I_Z_X1_bits": i_z_x1,
        "I_Z_X2_bits": i_z_x2,
        "H_Z_given_X1_bits": h_z_given_x1,
        "H_Z_given_X2_bits": h_z_given_x2,
        "H_Z_given_pair_bits": h_z_given_pair,
        "declared_minimal_coalition_size": 2,
        "joint_advantage_bits": expected,
    }


def check_margin_robustness() -> dict[str, Any]:
    gate_names = ["structural", "causal", "relational"]
    reference_margins = np.array([0.42, 0.71, 0.28])
    lipschitz = np.array([1.0, 1.6, 0.5])
    decomposition_defects = np.array([0.03, 0.07, 0.11])
    mismatch = np.array(
        [
            [0.010, 0.015, 0.008],
            [0.015, 0.020, 0.010],
            [0.020, 0.025, 0.012],
        ]
    )

    uncertainties = np.vstack(
        [lipschitz * delta + mismatch_row for delta, mismatch_row in zip(decomposition_defects, mismatch)]
    )
    worst_uncertainty = uncertainties.max(axis=0)
    lower_margin_envelope = reference_margins - worst_uncertainty
    robust = bool(np.all(lower_margin_envelope > 0))
    assert robust

    radius = float(np.min(reference_margins / lipschitz))
    assert decomposition_defects.max() < radius

    return {
        "gate_names": gate_names,
        "reference_margins": reference_margins.tolist(),
        "worst_transport_uncertainty": worst_uncertainty.tolist(),
        "lower_margin_envelope": lower_margin_envelope.tolist(),
        "all_required_gates_robust": robust,
        "certificate_radius_without_mismatch": radius,
        "maximum_decomposition_defect": float(decomposition_defects.max()),
    }


def main() -> None:
    results = {
        "status": "PASS",
        "faithful_coarse_graining": check_faithful_coarse_graining(),
        "risk_transport": check_risk_transport(),
        "secret_sharing_trivialization": check_secret_sharing(),
        "decomposition_transport_margins": check_margin_robustness(),
    }
    OUT.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
