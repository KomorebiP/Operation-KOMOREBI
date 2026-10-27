import numpy as np

from projector_quantum_calculus.basic import basis_state, ketbra
from projector_quantum_calculus.channels import (
    amplitude_damping_kraus, apply_channel, kraus_completeness_error,
    measurement_probabilities, packet_dephase,
)
from projector_quantum_calculus.geometry import (
    causal_volume_hamiltonian, cycle_eigenvalues, euclidean_transfer,
    low_mode_error_bound, torus_eigenvalues,
)
from projector_quantum_calculus.symmetry import parity_projectors


def test_amplitude_damping_channel() -> None:
    ks = amplitude_damping_kraus(0.3)
    assert kraus_completeness_error(ks) < 1e-12
    rho = ketbra(basis_state(1, 1))
    out = apply_channel(rho, ks)
    assert abs(np.trace(out) - 1) < 1e-12
    assert np.linalg.eigvalsh(out).min() > -1e-12


def test_block_diagonal_measurement_ignores_cross_sector_coherence() -> None:
    pe, po = parity_projectors(2)
    state = (basis_state(2, 0) + basis_state(2, 1)) / np.sqrt(2)
    rho = ketbra(state)
    effects = [pe, po]
    assert np.linalg.norm(measurement_probabilities(rho, effects) - measurement_probabilities(packet_dephase(rho, [pe, po]), effects)) < 1e-12


def test_cycle_spectrum() -> None:
    values = cycle_eigenvalues(32)
    assert abs(values[0]) < 1e-12
    assert np.all(values >= -1e-12)
    assert abs(values[1] - values[-1]) < 1e-12


def test_low_mode_bound() -> None:
    for n in [16, 32, 64, 128]:
        h = 2 * np.pi / n
        error, bound = low_mode_error_bound(1, h)
        assert 0 <= error <= bound + 1e-12


def test_torus_dimension() -> None:
    assert torus_eigenvalues(8, 1).size == 8
    assert torus_eigenvalues(8, 2).size == 64
    assert torus_eigenvalues(8, 3).size == 512


def test_euclidean_transfer() -> None:
    h = causal_volume_hamiltonian(20)
    t1 = euclidean_transfer(h, 0.2)
    t2 = euclidean_transfer(h, 0.4)
    assert np.linalg.eigvalsh(t1).min() > 0
    assert np.linalg.norm(t1 @ t1 - t2) < 1e-10
