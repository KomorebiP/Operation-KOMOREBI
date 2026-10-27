import numpy as np

from projector_seed_residuals.cohomology import (
    cohomology_dimensions,
    packet_cohomology_dimensions,
    rank_mod_p,
)


def test_rank_mod_p() -> None:
    matrix = np.array([[1, 2, 3], [2, 4, 1], [0, 1, 1]], dtype=int)
    assert rank_mod_p(matrix, 5) == 2


def test_packet_cohomology_reconstructs_total() -> None:
    p = 5
    d0_a = np.array([[1], [0]], dtype=int)
    d1_a = np.array([[0, 1]], dtype=int)
    d0_b = np.zeros((2, 1), dtype=int)
    d1_b = np.zeros((1, 2), dtype=int)
    packet_h = packet_cohomology_dimensions(
        [[d0_a, d1_a], [d0_b, d1_b]],
        [[1, 2, 1], [1, 2, 1]],
        p,
    )
    assert packet_h == [[0, 0, 0], [1, 2, 1]]

    d0 = np.block([[d0_a, np.zeros((2, 1), dtype=int)], [np.zeros((2, 1), dtype=int), d0_b]])
    d1 = np.block([[d1_a, np.zeros((1, 2), dtype=int)], [np.zeros((1, 2), dtype=int), d1_b]])
    total_h = cohomology_dimensions([d0, d1], [2, 4, 2], p)
    assert total_h == [1, 2, 1]
    assert [sum(packet_h[j][i] for j in range(2)) for i in range(3)] == total_h


def test_invalid_complex_rejected() -> None:
    d0 = np.array([[1], [0]], dtype=int)
    d1 = np.array([[1, 0]], dtype=int)
    try:
        cohomology_dimensions([d0, d1], [1, 2, 1], 5)
    except ValueError as exc:
        assert "do not form a complex" in str(exc)
    else:
        raise AssertionError("invalid complex should be rejected")
