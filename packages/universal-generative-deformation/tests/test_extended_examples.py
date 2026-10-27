from __future__ import annotations

from fractions import Fraction

from generative_deformation import ExplorationConfig, PerturbationForest
from generative_deformation.extended_examples import (
    AffineShapeSystem,
    CongruenceLiftSystem,
    GaussianFamilySystem,
    GraphDeformationSystem,
    MatrixDeformationSystem,
    QubitGateSystem,
    SequenceTransformSystem,
    path_graph,
    triangle_seed,
)


def _direction(system, state, name: str):
    return next(direction for direction in system.directions(state, 0) if direction.name == name)


def _apply(system, state, *names: str):
    result = state
    for name in names:
        result = system.apply(result, _direction(system, result, name))
    return result


def _matmul(left, right):
    return (
        (
            left[0][0] * right[0][0] + left[0][1] * right[1][0],
            left[0][0] * right[0][1] + left[0][1] * right[1][1],
        ),
        (
            left[1][0] * right[0][0] + left[1][1] * right[1][0],
            left[1][0] * right[0][1] + left[1][1] * right[1][1],
        ),
    )


def test_sequence_difference_then_partial_sum_is_identity() -> None:
    system = SequenceTransformSystem(length=8)
    seed = (1, 1, 2, 3, 5, 8, 13, 21)
    assert _apply(system, seed, "difference", "partial_sum") == seed


def test_sequence_partial_sum_then_difference_is_identity() -> None:
    system = SequenceTransformSystem(length=8)
    seed = (2, -1, 4, 0, 3, -2, 5, 1)
    assert _apply(system, seed, "partial_sum", "difference") == seed


def test_sequence_alternating_sign_is_an_involution() -> None:
    system = SequenceTransformSystem(length=6)
    seed = (1, 2, 3, 4, 5, 6)
    assert _apply(system, seed, "alternating_sign", "alternating_sign") == seed


def test_gaussian_standardization_returns_canonical_seed() -> None:
    system = GaussianFamilySystem()
    state = (Fraction(3), Fraction(8))
    assert _apply(system, state, "standardize") == (Fraction(0), Fraction(1))


def test_gaussian_reflection_is_an_involution() -> None:
    system = GaussianFamilySystem()
    state = (Fraction(3, 2), Fraction(5, 3))
    assert _apply(system, state, "reflect", "reflect") == state


def test_gaussian_unit_convolution_adds_one_variance_unit() -> None:
    system = GaussianFamilySystem()
    state = (Fraction(-2), Fraction(7, 3))
    assert _apply(system, state, "convolve_unit") == (Fraction(-2), Fraction(10, 3))


def test_qubit_clifford_projective_orbit_has_six_states() -> None:
    system = QubitGateSystem()
    forest = PerturbationForest(system, [(0, 0, 1)]).explore(
        ExplorationConfig(max_depth=5, max_paths=1800, max_nodes=20, max_edges=200)
    )
    assert len(forest.nodes) == 6


def test_qubit_orbit_preserves_purity_and_validity() -> None:
    system = QubitGateSystem()
    forest = PerturbationForest(system, [(0, 0, 1)]).explore(
        ExplorationConfig(max_depth=4, max_paths=500, max_nodes=20, max_edges=200)
    )
    assert all(system.validate(node.state).valid for node in forest.nodes.values())
    assert all(node.invariants["purity"] == 1.0 for node in forest.nodes.values())


def test_qubit_hadamard_is_an_involution_on_projective_states() -> None:
    system = QubitGateSystem()
    for state in ((0, 0, 1), (0, 0, -1), (1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0)):
        assert _apply(system, state, "H", "H") == state


def test_matrix_transpose_is_an_involution() -> None:
    system = MatrixDeformationSystem()
    seed = ((1, 2), (3, 4))
    assert _apply(system, seed, "transpose", "transpose") == seed


def test_matrix_adjugate_identity() -> None:
    system = MatrixDeformationSystem()
    seed = ((2, 3), (5, 7))
    adjugate = _apply(system, seed, "adjugate")
    determinant = seed[0][0] * seed[1][1] - seed[0][1] * seed[1][0]
    assert _matmul(seed, adjugate) == ((determinant, 0), (0, determinant))


def test_matrix_swap_conjugation_is_an_involution() -> None:
    system = MatrixDeformationSystem()
    seed = ((1, 4), (-2, 3))
    assert _apply(system, seed, "conjugate_swap", "conjugate_swap") == seed


def test_affine_rotation_has_order_four() -> None:
    system = AffineShapeSystem()
    seed = triangle_seed()
    assert system.canonical_key(_apply(system, seed, "rotate_90", "rotate_90", "rotate_90", "rotate_90")) == system.canonical_key(seed)


def test_affine_reflection_is_an_involution() -> None:
    system = AffineShapeSystem()
    seed = triangle_seed()
    assert system.canonical_key(_apply(system, seed, "reflect_x", "reflect_x")) == system.canonical_key(seed)


def test_graph_relabeling_collapses_under_unlabeled_quotient() -> None:
    system = GraphDeformationSystem(node_cap=6)
    seed = path_graph(4)
    assert system.canonical_key(_apply(system, seed, "relabel_reverse")) == system.canonical_key(seed)


def test_graph_complement_is_an_involution() -> None:
    system = GraphDeformationSystem(node_cap=6)
    seed = path_graph(4)
    assert _apply(system, seed, "complement", "complement") == seed


def test_simple_congruence_roots_lift_uniquely() -> None:
    system = CongruenceLiftSystem(3, "square_one", depth_cap=5)
    forest = PerturbationForest(system, system.residual_seeds()).explore(
        ExplorationConfig(max_depth=4, max_paths=100, max_nodes=100, max_edges=200)
    )
    for node in forest.nodes.values():
        if node.state[0] < system.depth_cap:
            assert len(list(system.directions(node.state, node.min_depth))) == 1


def test_singular_congruence_root_has_genuine_branching() -> None:
    system = CongruenceLiftSystem(2, "square_zero", depth_cap=6)
    forest = PerturbationForest(system, system.residual_seeds()).explore(
        ExplorationConfig(max_depth=5, max_paths=300, max_nodes=300, max_edges=1000)
    )
    assert any(
        len(list(system.directions(node.state, node.min_depth))) > 1
        for node in forest.nodes.values()
        if node.state[0] < system.depth_cap
    )
