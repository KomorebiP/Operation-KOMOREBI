from __future__ import annotations

from typing import Sequence

import numpy as np

from .basic import I2, X, ketbra

Array = np.ndarray


def apply_channel(density: Array, kraus: Sequence[Array]) -> Array:
    rho = np.asarray(density, dtype=complex)
    return sum(k @ rho @ k.conj().T for k in kraus)


def kraus_completeness_error(kraus: Sequence[Array]) -> float:
    dim = kraus[0].shape[1]
    total = sum(k.conj().T @ k for k in kraus)
    return float(np.linalg.norm(total - np.eye(dim), ord=2))


def measurement_probabilities(density: Array, effects: Sequence[Array]) -> np.ndarray:
    rho = np.asarray(density, dtype=complex)
    return np.array([float(np.real(np.trace(e @ rho))) for e in effects])


def packet_dephase(density: Array, projectors: Sequence[Array]) -> Array:
    rho = np.asarray(density, dtype=complex)
    return sum(p @ rho @ p for p in projectors)


def amplitude_damping_kraus(gamma: float) -> list[Array]:
    if not 0 <= gamma <= 1:
        raise ValueError("gamma must be in [0,1]")
    k0 = np.array([[1, 0], [0, np.sqrt(1 - gamma)]], dtype=complex)
    k1 = np.array([[0, np.sqrt(gamma)], [0, 0]], dtype=complex)
    return [k0, k1]
