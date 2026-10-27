import numpy as np
from scipy.linalg import expm

from projector_transfer_semigroups.packets import (
    coordinate_projectors,
    validate_projectors,
    packet_blocks,
    reconstruct_from_blocks,
    block_composition,
)
from projector_transfer_semigroups.semigroup import (
    feshbach_effective_operator,
    projected_resolvent,
    memory_kernel_laplace,
    numerical_memory_laplace,
)


def test_coordinate_projectors() -> None:
    projectors = coordinate_projectors([[0, 2], [1, 3]], 4)
    assert validate_projectors(projectors)


def test_block_reconstruction() -> None:
    rng = np.random.default_rng(1)
    a = rng.normal(size=(6, 6))
    projectors = coordinate_projectors([[0, 1], [2, 3], [4, 5]], 6)
    blocks = packet_blocks(a, projectors)
    assert np.max(np.abs(reconstruct_from_blocks(blocks) - a)) < 1e-12


def test_semigroup_block_convolution() -> None:
    rng = np.random.default_rng(2)
    a = rng.normal(size=(6, 6))
    generator = -a.T @ a
    projectors = coordinate_projectors([[0, 1], [2, 3], [4, 5]], 6)
    b1 = packet_blocks(expm(0.2 * generator), projectors)
    b2 = packet_blocks(expm(0.35 * generator), projectors)
    product = block_composition(b1, b2)
    target = packet_blocks(expm(0.55 * generator), projectors)
    assert max(np.max(np.abs(product[i][j] - target[i][j])) for i in range(3) for j in range(3)) < 1e-11


def test_reducing_packets_are_block_diagonal() -> None:
    generator = np.diag([-1.0, -2.0, -3.0, -4.0])
    projectors = coordinate_projectors([[0, 1], [2, 3]], 4)
    blocks = packet_blocks(expm(0.7 * generator), projectors)
    assert np.max(np.abs(blocks[0][1])) == 0
    assert np.max(np.abs(blocks[1][0])) == 0


def test_feshbach_resolvent_identity() -> None:
    a = np.array([[-1.2, 0.3, 0.4, 0.0], [0.2, -0.9, 0.0, 0.25], [0.35, 0.0, -1.7, 0.5], [0.0, 0.4, 0.2, -1.4]])
    z = 2.3
    effective = feshbach_effective_operator(a, [0, 1], z)
    assert np.max(np.abs(np.linalg.inv(effective) - projected_resolvent(a, [0, 1], z))) < 1e-12


def test_memory_kernel_laplace_identity() -> None:
    a = np.array([[-1.2, 0.3, 0.4, 0.0], [0.2, -0.9, 0.0, 0.25], [0.35, 0.0, -1.7, 0.5], [0.0, 0.4, 0.2, -1.4]])
    exact = memory_kernel_laplace(a, [0, 1], 2.3)
    numeric = numerical_memory_laplace(a, [0, 1], 2.3, upper=45.0)
    assert np.max(np.abs(exact - numeric)) < 1e-9
