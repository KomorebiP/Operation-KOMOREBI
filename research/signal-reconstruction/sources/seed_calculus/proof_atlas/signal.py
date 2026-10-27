from __future__ import annotations

from functools import lru_cache

from dataclasses import dataclass

import sympy as sp


@dataclass(frozen=True)
class SignalCertificate:
    signal: sp.Matrix
    phase2: tuple[sp.Matrix, ...]
    phase4: tuple[sp.Matrix, ...]
    polyphase_residual: sp.Matrix
    refinement_residuals: tuple[sp.Matrix, ...]
    haar_coefficients: sp.Matrix
    haar_residual: sp.Matrix
    fourier_coefficients: sp.Matrix
    fourier_residual: sp.Matrix
    fourier_projector_residual: sp.Matrix
    fourier_idempotence_residuals: tuple[sp.Matrix, ...]


def residue_projector(n: int, order: int, phase: int) -> sp.Matrix:
    P = sp.zeros(n)
    for i in range(n):
        if i % order == phase % order:
            P[i, i] = 1
    return P


def polyphase_analyze(x: sp.Matrix, order: int) -> tuple[sp.Matrix, ...]:
    return tuple(sp.Matrix([x[i] for i in range(r, x.rows, order)]) for r in range(order))


def polyphase_synthesize(channels: tuple[sp.Matrix, ...], length: int) -> sp.Matrix:
    order = len(channels)
    out = sp.zeros(length, 1)
    for r, channel in enumerate(channels):
        for q, value in enumerate(channel):
            index = order * q + r
            if index < length:
                out[index] = value
    return out


def haar_one_level_matrix(n: int) -> sp.Matrix:
    if n <= 0 or n % 2:
        raise ValueError("n must be positive and even")
    H2 = sp.Matrix([[1, 1], [1, -1]]) / sp.sqrt(2)
    H = sp.zeros(n)
    for k in range(n // 2):
        H[2 * k : 2 * k + 2, 2 * k : 2 * k + 2] = H2
    return H


def dft8_matrix() -> sp.Matrix:
    s2 = sp.sqrt(2)
    roots = [
        1,
        (1 - sp.I) / s2,
        -sp.I,
        -(1 + sp.I) / s2,
        -1,
        -(1 - sp.I) / s2,
        sp.I,
        (1 + sp.I) / s2,
    ]
    return sp.Matrix(8, 8, lambda j, k: roots[(j * k) % 8] / sp.sqrt(8))


def transform_projectors(U: sp.Matrix, groups: tuple[tuple[int, ...], ...]) -> tuple[sp.Matrix, ...]:
    n = U.rows
    out: list[sp.Matrix] = []
    Uinv = sp.simplify(U.inv())
    for group in groups:
        E = sp.zeros(n)
        for i in group:
            E[i, i] = 1
        out.append(sp.simplify(Uinv * E * U))
    return tuple(out)


def matrix_simplify(M: sp.Matrix) -> sp.Matrix:
    return M.applyfunc(lambda z: sp.simplify(sp.expand_complex(z)))


def matrix_is_zero(M: sp.Matrix) -> bool:
    return all(sp.simplify(sp.expand_complex(v)) == 0 for v in M)


@lru_cache(maxsize=None)
def build_certificate() -> SignalCertificate:
    x = sp.Matrix([3, 1, 4, 1, 5, 9, 2, 6])

    phase2 = polyphase_analyze(x, 2)
    phase4 = polyphase_analyze(x, 4)
    polyphase_residual = polyphase_synthesize(phase4, 8) - x

    P2 = tuple(residue_projector(8, 2, r) for r in range(2))
    P4 = tuple(residue_projector(8, 4, r) for r in range(4))
    refinement_residuals = (
        P2[0] - P4[0] - P4[2],
        P2[1] - P4[1] - P4[3],
    )

    H = haar_one_level_matrix(8)
    hc = sp.simplify(H * x)
    haar_residual = matrix_simplify(H.T * hc - x)

    F = dft8_matrix()
    fc = matrix_simplify(F * x)
    fourier_residual = matrix_simplify(F.conjugate().T * fc - x)

    groups = ((0,), (1, 7), (2, 6), (3, 5), (4,))
    Q = transform_projectors(F, groups)
    fourier_projector_residual = matrix_simplify(sum(Q, sp.zeros(8)) - sp.eye(8))
    fourier_idempotence_residuals = tuple(matrix_simplify(Qi * Qi - Qi) for Qi in Q)

    assert matrix_is_zero(polyphase_residual)
    assert all(matrix_is_zero(R) for R in refinement_residuals)
    assert matrix_is_zero(haar_residual)
    assert matrix_is_zero(fourier_residual)
    assert matrix_is_zero(fourier_projector_residual)
    assert all(matrix_is_zero(R) for R in fourier_idempotence_residuals)
    assert matrix_is_zero(matrix_simplify(H.T * H - sp.eye(8)))
    assert matrix_is_zero(matrix_simplify(F.conjugate().T * F - sp.eye(8)))

    return SignalCertificate(
        signal=x,
        phase2=phase2,
        phase4=phase4,
        polyphase_residual=polyphase_residual,
        refinement_residuals=refinement_residuals,
        haar_coefficients=hc,
        haar_residual=haar_residual,
        fourier_coefficients=fc,
        fourier_residual=fourier_residual,
        fourier_projector_residual=fourier_projector_residual,
        fourier_idempotence_residuals=fourier_idempotence_residuals,
    )
