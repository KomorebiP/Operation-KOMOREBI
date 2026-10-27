from __future__ import annotations

from typing import Sequence

import numpy as np
from scipy.linalg import expm

Array = np.ndarray


def commutator(a: Array, b: Array) -> Array:
    return np.asarray(a) @ np.asarray(b) - np.asarray(b) @ np.asarray(a)


def unitary_evolution(hamiltonian: Array, time: float) -> Array:
    h = np.asarray(hamiltonian, dtype=complex)
    return np.asarray(expm(-1j * time * h), dtype=complex)


def leakage_amplitude(hamiltonian: Array, projector: Array, time: float) -> float:
    h = np.asarray(hamiltonian, dtype=complex)
    p = np.asarray(projector, dtype=complex)
    q = np.eye(h.shape[0], dtype=complex) - p
    return float(np.linalg.norm(q @ unitary_evolution(h, time) @ p, ord=2))


def leakage_bound(hamiltonian: Array, projector: Array, time: float) -> float:
    h = np.asarray(hamiltonian, dtype=complex)
    p = np.asarray(projector, dtype=complex)
    return abs(time) * float(np.linalg.norm(commutator(h, p), ord=2))


def feshbach_effective(hamiltonian: Array, projector: Array, z: complex) -> Array:
    h = np.asarray(hamiltonian, dtype=complex)
    p = np.asarray(projector, dtype=complex)
    q = np.eye(h.shape[0], dtype=complex) - p
    q_basis = np.linalg.eigh(q)[1][:, np.linalg.eigvalsh(q) > 0.5]
    p_basis = np.linalg.eigh(p)[1][:, np.linalg.eigvalsh(p) > 0.5]
    hpp = p_basis.conj().T @ h @ p_basis
    hpq = p_basis.conj().T @ h @ q_basis
    hqp = q_basis.conj().T @ h @ p_basis
    hqq = q_basis.conj().T @ h @ q_basis
    return hpp + hpq @ np.linalg.inv(z * np.eye(hqq.shape[0]) - hqq) @ hqp


def projected_resolvent(hamiltonian: Array, projector: Array, z: complex) -> Array:
    h = np.asarray(hamiltonian, dtype=complex)
    p = np.asarray(projector, dtype=complex)
    p_basis = np.linalg.eigh(p)[1][:, np.linalg.eigvalsh(p) > 0.5]
    full = np.linalg.inv(z * np.eye(h.shape[0]) - h)
    return p_basis.conj().T @ full @ p_basis


def moving_frame_generator(hamiltonian: Array, unitary: Array, unitary_derivative: Array) -> Array:
    """Hamiltonian in y=U^* psi coordinates for i psi_dot=H psi."""
    h = np.asarray(hamiltonian, dtype=complex)
    u = np.asarray(unitary, dtype=complex)
    du = np.asarray(unitary_derivative, dtype=complex)
    return u.conj().T @ h @ u - 1j * u.conj().T @ du


def canonical_projector_connection(projectors: Sequence[Array], derivatives: Sequence[Array]) -> Array:
    """Minimal skew-Hermitian connection C=1/2 sum [Pdot,P]."""
    if len(projectors) != len(derivatives):
        raise ValueError("projector and derivative lists must match")
    out = np.zeros_like(projectors[0], dtype=complex)
    for p, dp in zip(projectors, derivatives, strict=True):
        out += commutator(dp, p)
    return 0.5 * out


def bloch_projector(theta: float, phi: float) -> Array:
    sx = np.array([[0, 1], [1, 0]], dtype=complex)
    sy = np.array([[0, -1j], [1j, 0]], dtype=complex)
    sz = np.array([[1, 0], [0, -1]], dtype=complex)
    n = np.array([
        np.sin(theta) * np.cos(phi),
        np.sin(theta) * np.sin(phi),
        np.cos(theta),
    ])
    return 0.5 * (np.eye(2) + n[0] * sx + n[1] * sy + n[2] * sz)


def bloch_curvature(theta: float, phi: float, step: float = 1e-5) -> float:
    p = bloch_projector(theta, phi)
    dt = (bloch_projector(theta + step, phi) - bloch_projector(theta - step, phi)) / (2 * step)
    dp = (bloch_projector(theta, phi + step) - bloch_projector(theta, phi - step)) / (2 * step)
    value = -1j * np.trace(p @ commutator(dt, dp))
    return float(np.real(value))
