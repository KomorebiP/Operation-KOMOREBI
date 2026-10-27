from __future__ import annotations

from typing import Sequence

import numpy as np

from .basic import I2, X, basis_state, ketbra, kron_all

Array = np.ndarray


def bit_flip_codewords() -> tuple[Array, Array]:
    return basis_state(3, 0), basis_state(3, 7)


def bit_flip_code_projector() -> Array:
    zero, one = bit_flip_codewords()
    return ketbra(zero) + ketbra(one)


def bit_flip_errors() -> list[Array]:
    return [
        kron_all(I2, I2, I2),
        kron_all(X, I2, I2),
        kron_all(I2, X, I2),
        kron_all(I2, I2, X),
    ]


def syndrome_projectors() -> list[Array]:
    code = bit_flip_code_projector()
    return [e @ code @ e.conj().T for e in bit_flip_errors()]


def knill_laflamme_residual(code_projector: Array, errors: Sequence[Array]) -> tuple[Array, float]:
    p = np.asarray(code_projector, dtype=complex)
    code_rank = int(round(np.trace(p).real))
    coeff = np.zeros((len(errors), len(errors)), dtype=complex)
    residual = 0.0
    for a, ea in enumerate(errors):
        for b, eb in enumerate(errors):
            block = p @ ea.conj().T @ eb @ p
            scalar = np.trace(block) / code_rank
            coeff[a, b] = scalar
            residual = max(residual, float(np.linalg.norm(block - scalar * p)))
    return coeff, residual


def encode_logical_state(alpha: complex, beta: complex) -> Array:
    norm = np.sqrt(abs(alpha) ** 2 + abs(beta) ** 2)
    if norm == 0:
        raise ValueError("logical state must be nonzero")
    zero, one = bit_flip_codewords()
    return (alpha * zero + beta * one) / norm


def bit_flip_channel(density: Array, probabilities: Sequence[float]) -> Array:
    errors = bit_flip_errors()
    if len(probabilities) != 4 or abs(sum(probabilities) - 1) > 1e-12:
        raise ValueError("four probabilities summing to one are required")
    rho = np.asarray(density, dtype=complex)
    return sum(prob * error @ rho @ error.conj().T for prob, error in zip(probabilities, errors, strict=True))


def bit_flip_recovery(density: Array) -> Array:
    rho = np.asarray(density, dtype=complex)
    result = np.zeros_like(rho)
    for error, syndrome in zip(bit_flip_errors(), syndrome_projectors(), strict=True):
        result += error.conj().T @ syndrome @ rho @ syndrome @ error
    return result
