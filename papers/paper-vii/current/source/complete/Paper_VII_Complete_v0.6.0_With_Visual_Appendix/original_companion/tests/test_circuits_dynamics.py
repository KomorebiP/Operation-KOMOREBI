import numpy as np
from scipy.linalg import expm

from projector_quantum_calculus.basic import I2, X, Z, basis_state
from projector_quantum_calculus.circuits import bell_circuit, circuit_unitary, packet_path_reconstruction
from projector_quantum_calculus.dynamics import (
    canonical_projector_connection, commutator, feshbach_effective,
    leakage_amplitude, leakage_bound, moving_frame_generator, projected_resolvent,
)
from projector_quantum_calculus.symmetry import parity_projectors


def test_bell_circuit() -> None:
    _, _, bell = bell_circuit()
    target = (basis_state(2, 0) + basis_state(2, 3)) / np.sqrt(2)
    assert np.linalg.norm(bell - target) < 1e-12


def test_packet_path_reconstruction() -> None:
    _, gates, _ = bell_circuit()
    ps = parity_projectors(2)
    assert np.linalg.norm(packet_path_reconstruction(gates, ps) - circuit_unitary(gates)) < 1e-12


def test_parity_block_dynamics() -> None:
    h = 0.8 * np.kron(X, X) + 0.35 * (np.kron(Z, I2) + np.kron(I2, Z))
    pe, _ = parity_projectors(2)
    assert max(leakage_amplitude(h, pe, t) for t in np.linspace(0, 3, 11)) < 1e-11


def test_leakage_bound() -> None:
    h = 0.8 * np.kron(X, X) + 0.35 * (np.kron(Z, I2) + np.kron(I2, Z)) + 0.2 * np.kron(X, I2)
    pe, _ = parity_projectors(2)
    for t in np.linspace(0, 2, 21):
        assert leakage_amplitude(h, pe, t) <= leakage_bound(h, pe, t) + 1e-10


def test_feshbach_resolvent() -> None:
    rng = np.random.default_rng(2)
    a = rng.standard_normal((6, 6)) + 1j * rng.standard_normal((6, 6))
    h = (a + a.conj().T) / 2
    p = np.diag([1, 1, 1, 0, 0, 0]).astype(complex)
    z = 8 + 0.3j
    got = np.linalg.inv(z * np.eye(3) - feshbach_effective(h, p, z))
    ref = projected_resolvent(h, p, z)
    assert np.linalg.norm(got - ref) < 1e-10


def test_moving_frame_formula() -> None:
    k = np.array([[0, -0.6], [0.6, 0]], dtype=complex)
    t = 0.3
    u = expm(t * k)
    du = k @ u
    h = np.array([[1, 0.2j], [-0.2j, -0.4]], dtype=complex)
    heff = moving_frame_generator(h, u, du)
    assert np.linalg.norm(heff - heff.conj().T) < 1e-12


def test_canonical_projector_connection() -> None:
    k = np.array([[0, -0.7], [0.7, 0]], dtype=complex)
    u = expm(0.4 * k)
    fixed = [np.diag([1, 0]).astype(complex), np.diag([0, 1]).astype(complex)]
    ps = [u @ p @ u.conj().T for p in fixed]
    dps = [commutator(k, p) for p in ps]
    c = canonical_projector_connection(ps, dps)
    assert max(np.linalg.norm(commutator(c, p) - dp) for p, dp in zip(ps, dps, strict=True)) < 1e-10
