import numpy as np

from seed_calculus.core import packet_reachability, packet_transfer_graph, transfer_blocks
from seed_calculus.examples import bilateral_shift_matrix, residue_projectors


def test_shift_cycles_residue_packets() -> None:
    shift = bilateral_shift_matrix(12)
    projectors = residue_projectors(12, 4)
    blocks = transfer_blocks(shift, projectors)
    pattern = np.array([[int(np.linalg.norm(block) > 1e-12) for block in row] for row in blocks])
    expected = np.zeros((4, 4), dtype=int)
    for alpha in range(4):
        expected[(alpha + 1) % 4, alpha] = 1
    assert np.array_equal(pattern, expected)


def test_transfer_graph_reachability() -> None:
    shift = bilateral_shift_matrix(15)
    projectors = residue_projectors(15, 5)
    adjacency = packet_transfer_graph([shift], projectors)
    assert packet_reachability(adjacency, [0]) == set(range(5))
