#!/usr/bin/env python3
"""Deterministic and randomized finite-dimensional checks for the structural results.

These checks are regression tests for the displayed identities and examples.
They do not replace the proofs in the manuscript.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Iterable

import numpy as np

SEED = 20260830
TOL = 1e-9
RESULTS_DIR = Path(__file__).with_name("results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
OUT = RESULTS_DIR / "core_geometry.json"


def opnorm(a: np.ndarray) -> float:
    return float(np.linalg.norm(a, ord=2))


def block_diag(*blocks: np.ndarray) -> np.ndarray:
    rows = sum(b.shape[0] for b in blocks)
    cols = sum(b.shape[1] for b in blocks)
    out = np.zeros((rows, cols), dtype=float)
    r = c = 0
    for b in blocks:
        rr, cc = b.shape
        out[r : r + rr, c : c + cc] = b
        r += rr
        c += cc
    return out


def nullspace(a: np.ndarray, tol: float = 1e-10) -> np.ndarray:
    _, s, vh = np.linalg.svd(a, full_matrices=True)
    rank = int(np.sum(s > tol))
    return vh[rank:].T.copy()


def projector_from_basis(basis: np.ndarray) -> np.ndarray:
    if basis.shape[1] == 0:
        return np.zeros((basis.shape[0], basis.shape[0]))
    q, _ = np.linalg.qr(basis)
    return q @ q.T


def build_discrepancy(
    node_dims: list[int], edges: Iterable[tuple[int, int, np.ndarray, float]]
) -> np.ndarray:
    offsets = np.cumsum([0] + node_dims)
    blocks: list[np.ndarray] = []
    total = offsets[-1]
    for source, target, h, weight in edges:
        dt = node_dims[target]
        ds = node_dims[source]
        if h.shape != (dt, ds):
            raise ValueError(f"edge matrix shape {h.shape} != {(dt, ds)}")
        row = np.zeros((dt, total), dtype=float)
        root_w = math.sqrt(weight)
        row[:, offsets[target] : offsets[target + 1]] = root_w * np.eye(dt)
        row[:, offsets[source] : offsets[source + 1]] -= root_w * h
        blocks.append(row)
    return np.vstack(blocks) if blocks else np.zeros((0, total), dtype=float)


def spectral_projector(a: np.ndarray, d: int) -> tuple[np.ndarray, np.ndarray]:
    vals, vecs = np.linalg.eigh(a)
    return vecs[:, :d] @ vecs[:, :d].T, vals


def reflection_and_holonomy_check() -> dict[str, Any]:
    eye = np.eye(2)
    j = np.diag([1.0, -1.0])
    edges = [(0, 1, eye, 1.0), (1, 2, eye, 1.0), (2, 0, j, 1.0)]
    d = build_discrepancy([2, 2, 2], edges)
    ker = nullspace(d)
    fixed = nullspace(j - eye)
    global_expected = np.vstack([fixed, fixed, fixed])
    p_kernel = projector_from_basis(ker)
    p_expected = projector_from_basis(global_expected)
    error = opnorm(p_kernel - p_expected)
    assert ker.shape[1] == 1
    assert fixed.shape[1] == 1
    assert error < TOL

    theta = 0.37
    rot = np.array(
        [[math.cos(theta), -math.sin(theta)], [math.sin(theta), math.cos(theta)]]
    )
    d_rot = build_discrepancy(
        [2, 2, 2], [(0, 1, eye, 1.0), (1, 2, eye, 1.0), (2, 0, rot, 1.0)]
    )
    rot_nullity = nullspace(d_rot).shape[1]
    assert rot_nullity == 0
    return {
        "reflection_cycle_workspace_dimension": int(ker.shape[1]),
        "holonomy_fixed_dimension": int(fixed.shape[1]),
        "global_projector_error": error,
        "rotation_cycle_workspace_dimension": int(rot_nullity),
    }


def laplacian_kernel_check(rng: np.random.Generator) -> dict[str, Any]:
    h01 = rng.normal(size=(2, 2))
    h12 = np.array([[1.0, 0.0], [0.0, 0.0]])
    h20 = rng.normal(size=(2, 2))
    d = build_discrepancy(
        [2, 2, 2], [(0, 1, h01, 0.7), (1, 2, h12, 1.3), (2, 0, h20, 0.9)]
    )
    l = d.T @ d
    null_d = nullspace(d)
    null_l = nullspace(l)
    error = opnorm(projector_from_basis(null_d) - projector_from_basis(null_l))
    energy_error = 0.0
    for _ in range(25):
        x = rng.normal(size=d.shape[1])
        energy_error = max(energy_error, abs(float(x @ l @ x) - float(np.dot(d @ x, d @ x))))
    assert error < 1e-7
    assert energy_error < 1e-8
    return {
        "D_nullity": int(null_d.shape[1]),
        "L_nullity": int(null_l.shape[1]),
        "kernel_projector_error": error,
        "maximum_energy_identity_error": energy_error,
    }


def spectral_stability_check(rng: np.random.Generator) -> dict[str, Any]:
    q, _ = np.linalg.qr(rng.normal(size=(4, 4)))
    eig = np.array([0.4, 0.7, 3.0, 4.5])
    l = q @ np.diag(eig) @ q.T
    e0 = rng.normal(size=(4, 4))
    e0 = 0.5 * (e0 + e0.T)
    eta = 0.2
    e = e0 * (eta / opnorm(e0))
    lt = l + e
    p, vals = spectral_projector(l, 2)
    pt, vals_t = spectral_projector(lt, 2)
    gap = float(vals[2] - vals[1])
    actual = opnorm(p - pt)
    bound = eta / (gap - eta)
    assert eta < gap / 2.0
    assert vals_t[0] >= -1e-10
    assert actual <= bound + 1e-10
    return {
        "gap": gap,
        "perturbation_norm": opnorm(e),
        "projector_distance": actual,
        "theorem_bound": bound,
        "bound_holds": bool(actual <= bound + 1e-10),
    }


def approximate_operation_check(rng: np.random.Generator) -> dict[str, Any]:
    s = np.array([[1.4, 0.2], [0.1, 0.9]])
    sinv = np.linalg.inv(s)
    edges = [(0, 1, s, 1.0), (1, 0, sinv, 1.0)]
    d = build_discrepancy([2, 2], edges)
    l = d.T @ d
    p, vals = spectral_projector(l, 2)
    qproj = np.eye(4) - p

    a = rng.normal(size=(2, 2))
    k = rng.normal(size=(2, 2))
    delta = 0.08
    rho1 = a
    rho2 = s @ a @ sinv + delta * k
    rho_v = block_diag(rho1, rho2)
    rho_e = block_diag(rho2, rho1)

    xi01 = s @ rho1 - rho2 @ s
    xi10 = sinv @ rho2 - rho1 @ sinv
    beta = max(opnorm(xi01), opnorm(xi10))
    epsilon = float(vals[1])
    mu = float(vals[2])
    actual = opnorm(qproj @ rho_v @ p)
    bound = (opnorm(rho_e) * math.sqrt(max(epsilon, 0.0)) + beta) / math.sqrt(mu)
    assert actual <= bound + 1e-8
    return {
        "workspace_dimension": 2,
        "lambda_d": epsilon,
        "lambda_d_plus_1": mu,
        "intertwining_beta": beta,
        "actual_operation_leakage": actual,
        "theorem_bound": bound,
        "bound_holds": bool(actual <= bound + 1e-8),
    }


def residual_duhamel_check(rng: np.random.Generator) -> dict[str, Any]:
    m = 4
    core = 2
    residual = 1
    ts: list[np.ndarray] = []
    hs: list[np.ndarray] = []
    vs: list[np.ndarray] = []
    for _ in range(m):
        h = 0.55 * rng.normal(size=(core, core))
        u = 0.15 * rng.normal(size=(core, residual))
        v = 0.12 * rng.normal(size=(residual, core))
        k = 0.45 * rng.normal(size=(residual, residual))
        t = np.block([[h, u], [v, k]])
        ts.append(t)
        hs.append(h)
        vs.append(v)

    iota_c = np.vstack([np.eye(core), np.zeros((residual, core))])
    select_c = np.hstack([np.eye(core), np.zeros((core, residual))])
    select_r = np.hstack([np.zeros((residual, core)), np.eye(residual)])

    tprod = np.eye(core + residual)
    for t in ts:
        tprod = t @ tprod
    hprod = np.eye(core)
    for h in hs:
        hprod = h @ hprod
    lhs = tprod @ iota_c - iota_c @ hprod

    rhs = np.zeros_like(lhs)
    for r in range(m):
        left = np.eye(core + residual)
        for ell in range(r + 1, m):
            left = ts[ell] @ left
        right = np.eye(core)
        for ell in range(r):
            right = hs[ell] @ right
        iota_r = np.vstack([np.zeros((core, residual)), np.eye(residual)])
        rhs += left @ iota_r @ vs[r] @ right

    identity_error = opnorm(lhs - rhs)
    bound = 0.0
    for r in range(m):
        left_norm = 1.0
        for ell in range(r + 1, m):
            left_norm *= opnorm(ts[ell])
        right_norm = 1.0
        for ell in range(r):
            right_norm *= opnorm(hs[ell])
        bound += left_norm * opnorm(vs[r]) * right_norm

    residual_actual = opnorm(select_r @ tprod @ iota_c)
    core_actual = opnorm(select_c @ tprod @ iota_c - hprod)
    assert identity_error < 1e-9
    assert residual_actual <= bound + 1e-9
    assert core_actual <= bound + 1e-9
    return {
        "path_length": m,
        "duhamel_identity_error": identity_error,
        "terminal_residual_leakage": residual_actual,
        "core_transport_defect": core_actual,
        "pathwise_bound": bound,
    }


def gauge_covariance_check(rng: np.random.Generator) -> dict[str, Any]:
    hs = [rng.normal(size=(2, 2)) for _ in range(3)]
    edge_data = [(0, 1, hs[0], 0.8), (1, 2, hs[1], 1.1), (2, 0, hs[2], 0.9)]
    d = build_discrepancy([2, 2, 2], edge_data)

    gs = []
    for _ in range(3):
        g = rng.normal(size=(2, 2))
        while abs(np.linalg.det(g)) < 0.3:
            g = rng.normal(size=(2, 2))
        gs.append(g)
    hsg = [gs[1] @ hs[0] @ np.linalg.inv(gs[0]),
           gs[2] @ hs[1] @ np.linalg.inv(gs[1]),
           gs[0] @ hs[2] @ np.linalg.inv(gs[2])]
    dg = build_discrepancy(
        [2, 2, 2], [(0, 1, hsg[0], 0.8), (1, 2, hsg[1], 1.1), (2, 0, hsg[2], 0.9)]
    )
    gv = block_diag(*gs)
    ge = block_diag(gs[1], gs[2], gs[0])
    covariance_error = opnorm(dg @ gv - ge @ d)
    assert covariance_error < 1e-9

    us = [np.linalg.qr(rng.normal(size=(2, 2)))[0] for _ in range(3)]
    hsu = [us[1] @ hs[0] @ us[0].T,
           us[2] @ hs[1] @ us[1].T,
           us[0] @ hs[2] @ us[2].T]
    du = build_discrepancy(
        [2, 2, 2], [(0, 1, hsu[0], 0.8), (1, 2, hsu[1], 1.1), (2, 0, hsu[2], 0.9)]
    )
    uv = block_diag(*us)
    l = d.T @ d
    lu = du.T @ du
    laplacian_error = opnorm(lu - uv @ l @ uv.T)
    eig_error = float(np.max(np.abs(np.linalg.eigvalsh(lu) - np.linalg.eigvalsh(l))))
    assert laplacian_error < 1e-8
    assert eig_error < 1e-8
    return {
        "general_gauge_covariance_error": covariance_error,
        "unitary_laplacian_similarity_error": laplacian_error,
        "unitary_spectrum_error": eig_error,
    }


def coarse_graining_check() -> dict[str, Any]:
    d_internal = np.array(
        [[-1.0, 1.0, 0.0, 0.0], [0.0, 0.0, -1.0, 1.0]]
    )
    d_boundary = np.array(
        [[0.0, -1.0, 1.0, 0.0], [1.0, 0.0, 0.0, -1.0]]
    )
    d_full = np.vstack([d_internal, d_boundary])
    inv_sqrt_2 = 1.0 / math.sqrt(2.0)
    j_pi = np.array(
        [[inv_sqrt_2, 0.0], [inv_sqrt_2, 0.0], [0.0, inv_sqrt_2], [0.0, inv_sqrt_2]]
    )
    d_pi = d_boundary @ j_pi
    p_full = projector_from_basis(nullspace(d_full))
    p_coarse = projector_from_basis(j_pi @ nullspace(d_pi))
    proj_error = opnorm(p_full - p_coarse)
    assert proj_error < 1e-9

    p_pi = j_pi @ j_pi.T
    vals_int = np.linalg.eigvalsh(d_internal.T @ d_internal)
    gamma_int = float(vals_int[vals_int > 1e-10].min())
    vals_pi = np.linalg.eigvalsh(d_pi.T @ d_pi)
    gamma_pi = float(vals_pi[vals_pi > 1e-10].min())
    c = np.array([1.7, -0.2, 0.9, 2.4])
    lhs = opnorm((np.eye(4) - p_full) @ c.reshape(-1, 1))
    rhs = float(
        np.linalg.norm(d_internal @ c) / math.sqrt(gamma_int)
        + np.linalg.norm(d_pi @ j_pi.T @ p_pi @ c) / math.sqrt(gamma_pi)
    )
    assert lhs <= rhs + 1e-9
    return {
        "workspace_projector_error": proj_error,
        "two_scale_distance": lhs,
        "two_scale_bound": rhs,
        "bound_holds": bool(lhs <= rhs + 1e-9),
    }


def entropy(probs: np.ndarray) -> float:
    probs = probs[probs > 0]
    return float(-np.sum(probs * np.log2(probs)))


def conditional_entropy(samples: list[tuple[Any, Any]]) -> float:
    grouped: dict[Any, list[Any]] = {}
    for x, y in samples:
        grouped.setdefault(x, []).append(y)
    result = 0.0
    n = len(samples)
    for ys in grouped.values():
        _, counts = np.unique(np.asarray(ys), return_counts=True)
        result += len(ys) / n * entropy(counts / counts.sum())
    return result


def mutual_information(samples: list[tuple[Any, Any]]) -> float:
    xs = [x for x, _ in samples]
    ys = [y for _, y in samples]
    _, cx = np.unique(np.asarray(xs), return_counts=True)
    _, cy = np.unique(np.asarray(ys), return_counts=True)
    pairs: dict[tuple[Any, Any], int] = {}
    for pair in samples:
        pairs[pair] = pairs.get(pair, 0) + 1
    return entropy(cx / cx.sum()) + entropy(cy / cy.sum()) - entropy(
        np.asarray(list(pairs.values()), dtype=float) / len(samples)
    )


def secret_sharing_check(group_size: int = 5) -> dict[str, Any]:
    samples = []
    for z in range(group_size):
        for k in range(group_size):
            samples.append((z, k, (z - k) % group_size))
    i1 = mutual_information([(z, x1) for z, x1, _ in samples])
    i2 = mutual_information([(z, x2) for z, _, x2 in samples])
    hp = conditional_entropy([((x1, x2), z) for z, x1, x2 in samples])
    h1 = conditional_entropy([((x1,), z) for z, x1, _ in samples])
    expected = math.log2(group_size)
    assert abs(i1) < 1e-10 and abs(i2) < 1e-10
    assert abs(hp) < 1e-10 and abs(h1 - expected) < 1e-10
    return {
        "group_size": group_size,
        "I_Z_X1_bits": i1,
        "I_Z_X2_bits": i2,
        "H_Z_given_pair_bits": hp,
        "singleton_log_risk_bits": h1,
        "joint_advantage_bits": expected,
    }


def main() -> None:
    rng = np.random.default_rng(SEED)
    results = {
        "seed": SEED,
        "reflection_and_holonomy": reflection_and_holonomy_check(),
        "laplacian_kernel": laplacian_kernel_check(rng),
        "spectral_stability": spectral_stability_check(rng),
        "approximate_operation_closure": approximate_operation_check(rng),
        "residual_duhamel": residual_duhamel_check(rng),
        "gauge_covariance": gauge_covariance_check(rng),
        "faithful_coarse_graining": coarse_graining_check(),
        "secret_sharing_trivialization": secret_sharing_check(),
        "all_checks_passed": True,
    }
    OUT.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
