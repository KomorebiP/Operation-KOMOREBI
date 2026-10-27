from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Tuple

import sympy as sp


@dataclass(frozen=True)
class FoundationCertificate:
    dimension: int
    seed: sp.Matrix
    shift: sp.Matrix
    orbit_matrix: sp.Matrix
    orbit_rank: int
    relation_residual: sp.Matrix
    signal: sp.Matrix
    signal_polynomial_coefficients: tuple[sp.Integer, ...]
    spatial_projectors: tuple[sp.Matrix, ...]
    spatial_packets: tuple[sp.Matrix, ...]
    spatial_reconstruction_residual: sp.Matrix
    parity_projectors: tuple[sp.Matrix, sp.Matrix]
    mod4_projectors: tuple[sp.Matrix, ...]
    parity_refinement_residuals: tuple[sp.Matrix, sp.Matrix]
    mod4_to_spatial_residuals: tuple[sp.Matrix, ...]
    operator: sp.Matrix
    operator_output: sp.Matrix
    transfer_blocks: tuple[tuple[sp.Matrix, ...], ...]
    transfer_reconstruction_residual: sp.Matrix
    transfer_support: tuple[tuple[int, int], ...]
    second_operator: sp.Matrix
    product_path_residual: sp.Matrix
    fourier_matrix: sp.Matrix
    fourier_projectors: tuple[sp.Matrix, ...]
    fourier_completeness_residual: sp.Matrix
    fourier_idempotence_residuals: tuple[sp.Matrix, ...]
    fourier_annihilation_residuals: tuple[sp.Matrix, ...]
    fourier_diagonal_operator: sp.Matrix
    haar_matrix: sp.Matrix
    multi_atlas_reconstruction_residual: sp.Matrix
    nonlinear_output: sp.Matrix
    nonlinear_packet_residual: sp.Matrix
    bilinear_interaction_residual: sp.Matrix
    obstruction_projector: sp.Matrix
    solvable_obstruction: sp.Matrix
    blocked_obstruction: sp.Matrix
    dense_extension_residual: sp.Matrix


def cyclic_shift(n: int) -> sp.Matrix:
    U = sp.zeros(n)
    for j in range(n):
        U[(j + 1) % n, j] = 1
    return U


def coordinate_projectors(n: int) -> tuple[sp.Matrix, ...]:
    out = []
    for j in range(n):
        P = sp.zeros(n)
        P[j, j] = 1
        out.append(P)
    return tuple(out)


def unitary_dft(n: int) -> sp.Matrix:
    omega = sp.exp(-2 * sp.pi * sp.I / n)
    return sp.Matrix(n, n, lambda k, j: omega ** (k * j) / sp.sqrt(n))


def haar_matrix(n: int) -> sp.Matrix:
    if n < 2 or n & (n - 1):
        raise ValueError("n must be a power of two")
    if n == 2:
        return sp.Matrix([[1, 1], [1, -1]]) / sp.sqrt(2)
    Hh = haar_matrix(n // 2)
    # Standard orthonormal multilevel Haar transform: coarse transform of pair averages,
    # followed by the finest detail coefficients.
    pair = sp.zeros(n)
    for q in range(n // 2):
        pair[q, 2 * q] = 1 / sp.sqrt(2)
        pair[q, 2 * q + 1] = 1 / sp.sqrt(2)
        pair[n // 2 + q, 2 * q] = 1 / sp.sqrt(2)
        pair[n // 2 + q, 2 * q + 1] = -1 / sp.sqrt(2)
    upper = sp.diag(Hh, sp.eye(n // 2))
    return sp.simplify(upper * pair)


def matrix_zero(M: sp.Matrix) -> bool:
    return all(sp.simplify(v) == 0 for v in M)


@lru_cache(maxsize=1)
def build_certificate() -> FoundationCertificate:
    n = 8
    U = cyclic_shift(n)
    seed = sp.eye(n)[:, 0]
    orbit = sp.Matrix.hstack(*[(U ** k) * seed for k in range(n)])
    relation_residual = sp.simplify(U ** n - sp.eye(n))

    coeffs = tuple(sp.Integer(v) for v in (2, -1, 3, 0, 1, 4, -2, 5))
    x = sum((coeffs[k] * (U ** k) * seed for k in range(n)), sp.zeros(n, 1))

    E = coordinate_projectors(n)
    packets = tuple(P * x for P in E)
    spatial_residual = sp.simplify(sum(packets, sp.zeros(n, 1)) - x)

    P_even = sum((E[j] for j in range(0, n, 2)), sp.zeros(n))
    P_odd = sum((E[j] for j in range(1, n, 2)), sp.zeros(n))
    R = tuple(E[r] + E[r + 4] for r in range(4))
    parity_refinement = (
        sp.simplify(P_even - R[0] - R[2]),
        sp.simplify(P_odd - R[1] - R[3]),
    )
    mod4_refinement = tuple(sp.simplify(R[r] - E[r] - E[r + 4]) for r in range(4))

    T = 2 * sp.eye(n) - U + 3 * (U ** 2)
    Tx = sp.simplify(T * x)
    blocks = tuple(tuple(sp.simplify(E[b] * T * E[a]) for a in range(n)) for b in range(n))
    Trec = sum((blocks[b][a] for b in range(n) for a in range(n)), sp.zeros(n))
    transfer_residual = sp.simplify(Trec - T)
    support = tuple((b, a) for b in range(n) for a in range(n) if not matrix_zero(blocks[b][a]))

    S = sp.eye(n) + U ** 3
    path_sum = sp.zeros(n)
    for b in range(n):
        for g in range(n):
            for a in range(n):
                path_sum += E[b] * S * E[g] * T * E[a]
    product_residual = sp.simplify(path_sum - S * T)

    F = unitary_dft(n)
    Q = []
    for k in range(n):
        Ek = sp.zeros(n)
        Ek[k, k] = 1
        Q.append(sp.simplify(F.conjugate().T * Ek * F))
    Q = tuple(Q)
    Qsum = sp.simplify(sum(Q, sp.zeros(n)) - sp.eye(n))
    Qidem = tuple(sp.simplify(Qk * Qk - Qk) for Qk in Q)
    Qann = tuple(sp.simplify(Q[i] * Q[j]) for i in range(n) for j in range(n) if i != j)
    Tfourier = sp.simplify(F * T * F.conjugate().T)

    H = haar_matrix(n)
    assert matrix_zero(sp.simplify(H.T * H - sp.eye(n)))
    weights = (sp.Integer(1), sp.Integer(2), sp.Integer(3))
    c0 = weights[0] * x
    c1 = weights[1] * F * x
    c2 = weights[2] * H * x
    xhat = sp.simplify((weights[0] * c0 + weights[1] * F.conjugate().T * c1 + weights[2] * H.T * c2) / sum(w * w for w in weights))
    multi_residual = sp.simplify(xhat - x)

    # Nonlinear realization: N(x)=x + (Ux) \odot (U^3 x).
    ux = U * x
    u3x = (U ** 3) * x
    nonlinear = sp.simplify(x + ux.multiply_elementwise(u3x))
    nonlinear_packet_sum = sum((E[b] * nonlinear for b in range(n)), sp.zeros(n, 1))
    nonlinear_packet_residual = sp.simplify(nonlinear_packet_sum - nonlinear)

    # Resolve the bilinear term into all packet-pair interactions.
    interaction = sp.zeros(n, 1)
    for a in range(n):
        for c in range(n):
            left = U * E[a] * x
            right = (U ** 3) * E[c] * x
            interaction += left.multiply_elementwise(right)
    bilinear_residual = sp.simplify(interaction - ux.multiply_elementwise(u3x))

    # Finite obstruction packet for L h = d.
    L = sp.Matrix([[1, 0], [0, 1], [1, 1]])
    Pi = sp.simplify(sp.eye(3) - L * (L.T * L).inv() * L.T)
    d_good = sp.Matrix([1, 2, 3])
    d_bad = sp.Matrix([1, 2, 4])
    obs_good = sp.simplify(Pi * d_good)
    obs_bad = sp.simplify(Pi * d_bad)

    # Dense-extension check: an identity proved on the basis orbit extends linearly to x.
    basis_check = sp.Matrix.hstack(*[(sum(E, sp.zeros(n)) - sp.eye(n)) * orbit[:, j] for j in range(n)])
    dense_extension_residual = sp.simplify(basis_check)

    # Exact checks.
    assert orbit.rank() == n
    assert matrix_zero(relation_residual)
    assert matrix_zero(spatial_residual)
    assert all(matrix_zero(r) for r in parity_refinement)
    assert all(matrix_zero(r) for r in mod4_refinement)
    assert matrix_zero(transfer_residual)
    assert matrix_zero(product_residual)
    assert matrix_zero(Qsum)
    assert all(matrix_zero(r) for r in Qidem)
    assert all(matrix_zero(r) for r in Qann)
    assert matrix_zero(multi_residual)
    assert matrix_zero(nonlinear_packet_residual)
    assert matrix_zero(bilinear_residual)
    assert matrix_zero(obs_good)
    assert not matrix_zero(obs_bad)
    assert matrix_zero(dense_extension_residual)

    return FoundationCertificate(
        dimension=n,
        seed=seed,
        shift=U,
        orbit_matrix=orbit,
        orbit_rank=orbit.rank(),
        relation_residual=relation_residual,
        signal=x,
        signal_polynomial_coefficients=coeffs,
        spatial_projectors=E,
        spatial_packets=packets,
        spatial_reconstruction_residual=spatial_residual,
        parity_projectors=(P_even, P_odd),
        mod4_projectors=R,
        parity_refinement_residuals=parity_refinement,
        mod4_to_spatial_residuals=mod4_refinement,
        operator=T,
        operator_output=Tx,
        transfer_blocks=blocks,
        transfer_reconstruction_residual=transfer_residual,
        transfer_support=support,
        second_operator=S,
        product_path_residual=product_residual,
        fourier_matrix=F,
        fourier_projectors=Q,
        fourier_completeness_residual=Qsum,
        fourier_idempotence_residuals=Qidem,
        fourier_annihilation_residuals=Qann,
        fourier_diagonal_operator=Tfourier,
        haar_matrix=H,
        multi_atlas_reconstruction_residual=multi_residual,
        nonlinear_output=nonlinear,
        nonlinear_packet_residual=nonlinear_packet_residual,
        bilinear_interaction_residual=bilinear_residual,
        obstruction_projector=Pi,
        solvable_obstruction=obs_good,
        blocked_obstruction=obs_bad,
        dense_extension_residual=dense_extension_residual,
    )
