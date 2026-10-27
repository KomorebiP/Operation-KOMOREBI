import sympy as sp

from seed_calculus.graphs import cycle_adjacency, endpoint_krylov_determinant_path, path_adjacency, symmetric_graph_seed_rank


def test_path_graphs_are_cyclic() -> None:
    for n in range(2, 13):
        assert symmetric_graph_seed_rank(path_adjacency(n)) == 1
        assert endpoint_krylov_determinant_path(n) != 0


def test_cycle_graphs_need_two_seeds() -> None:
    for n in range(3, 13):
        assert symmetric_graph_seed_rank(cycle_adjacency(n)) == 2


def test_path_and_cycle_are_symmetric() -> None:
    assert path_adjacency(8) == path_adjacency(8).T
    assert cycle_adjacency(8) == cycle_adjacency(8).T
