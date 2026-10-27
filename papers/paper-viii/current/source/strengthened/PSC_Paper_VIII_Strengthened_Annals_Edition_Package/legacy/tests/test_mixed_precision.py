import numpy as np

from packet_gpu.mixed_precision import (
    actual_block_diagonal_error,
    optimal_precision_tolerances,
    packet_error_bound,
    quantize_by_packet,
)


def test_error_bound_holds() -> None:
    rng = np.random.default_rng(8)
    blocks = [rng.normal(size=(5, 5)), rng.normal(size=(4, 4)), rng.normal(size=(3, 3))]
    approx = quantize_by_packet(blocks, [16, 32, 64])
    xs = [rng.normal(size=(5, 2)), rng.normal(size=(4, 2)), rng.normal(size=(3, 2))]
    actual = actual_block_diagonal_error(blocks, approx, xs)
    norms = [np.linalg.norm(b, 2) for b in blocks]
    rel = [np.linalg.norm(q - b, 2) / np.linalg.norm(b, 2) for b, q in zip(blocks, approx, strict=True)]
    inputs = [np.linalg.norm(x) for x in xs]
    bound = packet_error_bound(norms, rel, inputs)
    assert actual <= bound + 1e-12


def test_optimal_tolerance_constraint() -> None:
    s = np.array([1.0, 2.0, 5.0])
    c = np.array([1.0, 3.0, 2.0])
    tau = 1e-3
    eps = optimal_precision_tolerances(s, c, tau)
    assert np.isclose(np.dot(s, eps), tau)
    # KKT condition s_i eps_i / c_i is constant.
    ratios = s * eps / c
    assert np.allclose(ratios, ratios[0])


def test_quantization_packet_dtypes() -> None:
    blocks = [np.array([[1.123456789]]), np.array([[2.123456789]]), np.array([[3.123456789]])]
    q = quantize_by_packet(blocks, [16, 32, 64])
    assert abs(q[2][0, 0] - blocks[2][0, 0]) == 0
    assert abs(q[0][0, 0] - blocks[0][0, 0]) >= abs(q[1][0, 0] - blocks[1][0, 0]) * 0.1
