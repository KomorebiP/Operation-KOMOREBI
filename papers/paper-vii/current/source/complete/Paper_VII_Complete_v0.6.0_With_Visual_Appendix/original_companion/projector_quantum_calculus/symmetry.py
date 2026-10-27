from __future__ import annotations

from itertools import product
from typing import Sequence

import numpy as np

from .basic import I2, Z, kron_all

Array = np.ndarray


def cyclic_projectors(symmetry: Array, order: int) -> list[Array]:
    """Character projectors for a unitary S with S**order=I."""
    s = np.asarray(symmetry, dtype=complex)
    if s.shape[0] != s.shape[1]:
        raise ValueError("symmetry must be square")
    omega = np.exp(2j * np.pi / order)
    projectors: list[Array] = []
    powers = [np.linalg.matrix_power(s, r) for r in range(order)]
    for j in range(order):
        p = sum(omega ** (-j * r) * powers[r] for r in range(order)) / order
        projectors.append(np.asarray(p, dtype=complex))
    return projectors


def parity_operator(n_qubits: int) -> Array:
    return kron_all(*([Z] * n_qubits))


def parity_projectors(n_qubits: int) -> tuple[Array, Array]:
    s = parity_operator(n_qubits)
    identity = np.eye(2**n_qubits, dtype=complex)
    return (0.5 * (identity + s), 0.5 * (identity - s))


def tensor_packet_projectors(local_projectors: Sequence[Sequence[Array]]) -> list[tuple[tuple[int, ...], Array]]:
    """Fine tensor packets indexed by one local packet label per factor."""
    indexed: list[tuple[tuple[int, ...], Array]] = []
    for address in product(*[range(len(ps)) for ps in local_projectors]):
        indexed.append((tuple(address), kron_all(*[local_projectors[k][j] for k, j in enumerate(address)])))
    return indexed


def coarse_mod_projectors(local_projectors: Sequence[Sequence[Array]], modulus: int) -> list[Array]:
    fine = tensor_packet_projectors(local_projectors)
    dimension = fine[0][1].shape[0]
    coarse = [np.zeros((dimension, dimension), dtype=complex) for _ in range(modulus)]
    for address, p in fine:
        coarse[sum(address) % modulus] += p
    return coarse


def sector_populations(state_or_density: Array, projectors: Sequence[Array]) -> np.ndarray:
    x = np.asarray(state_or_density, dtype=complex)
    if x.ndim == 1:
        return np.array([float(np.real(np.vdot(x, p @ x))) for p in projectors])
    return np.array([float(np.real(np.trace(p @ x))) for p in projectors])


def off_block_norm(operator: Array, projectors: Sequence[Array], ord: int | str | None = 2) -> float:
    a = np.asarray(operator, dtype=complex)
    off = np.zeros_like(a)
    for i, pi in enumerate(projectors):
        for j, pj in enumerate(projectors):
            if i != j:
                off += pi @ a @ pj
    return float(np.linalg.norm(off, ord=ord))
