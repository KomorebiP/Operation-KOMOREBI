from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pytest

import projector_generated_special_functions_vii as sf


ROOT = Path(sf.__file__).resolve().parent


def test_composition_count() -> None:
    for total in range(8):
        for factors in range(2, 6):
            assert len(sf.compositions(total, factors)) == sf.excitation_dimension(total, factors)


def test_multiplicity_dimension_from_nullspace() -> None:
    kappas = (0.6, 0.9, 1.2, 1.4)
    for total in range(6):
        frame = sf.multiplicity_frame(total, kappas)
        assert frame.shape[1] == sf.multiplicity_dimension(total, len(kappas))
        if total > 0:
            assert np.max(np.abs(sf.lowering_matrix(total, kappas) @ frame)) < 2e-10


def test_pair_casimir_spectrum_multiple_shapes() -> None:
    for kappas in ((0.5, 0.5, 0.5), (0.7, 1.1, 0.9), (1.3, 0.8, 1.6)):
        for total in (1, 2, 5):
            data = sf.three_body_recoupling(total, kappas)
            assert np.allclose(data.left_eigenvalues, sf.theoretical_pair_spectrum(total, kappas[0], kappas[1]), atol=2e-10)
            assert np.allclose(data.right_eigenvalues, sf.theoretical_pair_spectrum(total, kappas[1], kappas[2]), atol=2e-10)


def test_recoupling_is_orthogonal() -> None:
    data = sf.three_body_recoupling(9, (0.65, 1.05, 1.25))
    assert np.allclose(data.overlap.T @ data.overlap, np.eye(10), atol=2e-10)
    assert np.allclose(data.overlap @ data.overlap.T, np.eye(10), atol=2e-10)


def test_one_excitation_formula() -> None:
    for kappas in ((0.5, 0.5, 0.5), (0.7, 1.1, 0.9), (2.0, 0.75, 1.25)):
        observed = sf.three_body_recoupling(1, kappas).overlap
        expected = sf.one_excitation_closed_form(kappas)
        assert np.allclose(observed, expected, atol=2e-10)
        assert np.allclose(expected.T @ expected, np.eye(2), atol=2e-12)


def test_equal_shape_two_excitation_formula() -> None:
    observed = sf.three_body_recoupling(2, (0.5, 0.5, 0.5)).overlap
    expected = sf.equal_shape_two_excitation_matrix()
    assert np.allclose(observed, expected, atol=2e-10)
    assert np.allclose(expected.T @ expected, np.eye(3), atol=2e-12)


def test_leonard_tridiagonal_selection_rule() -> None:
    for total in range(2, 10):
        data = sf.three_body_recoupling(total, (0.7, 1.1, 0.9))
        assert sf.tridiagonal_residual(data.right_in_left) < 2e-10


def test_probability_kernel_is_doubly_stochastic() -> None:
    data = sf.three_body_recoupling(11, (0.7, 1.1, 0.9))
    probability = data.overlap**2
    assert sf.doubly_stochastic_residual(probability) < 2e-10


def test_uniform_distribution_is_stationary() -> None:
    data = sf.three_body_recoupling(8, (0.7, 1.1, 0.9))
    probability = data.overlap**2
    uniform = np.full(9, 1.0 / 9.0)
    assert np.allclose(uniform @ probability, uniform, atol=2e-12)


def test_entropy_does_not_decrease_under_bistochastic_channel() -> None:
    rng = np.random.default_rng(71)
    data = sf.three_body_recoupling(8, (0.7, 1.1, 0.9))
    probability = data.overlap**2
    for _ in range(100):
        p = rng.dirichlet(np.ones(9))
        q = p @ probability
        hp = -np.sum(p * np.log(p))
        hq = -np.sum(q * np.log(q))
        assert hq + 2e-12 >= hp


def test_equal_shape_probability_matrix_is_symmetric() -> None:
    data = sf.three_body_recoupling(10, (0.5, 0.5, 0.5))
    probability = data.overlap**2
    assert np.max(np.abs(probability - probability.T)) < 2e-10


def test_four_body_tree_casimirs_commute() -> None:
    trees = sf.four_body_tree_bases(4, (0.55, 0.8, 1.05, 1.3))
    assert max(tree.commutator_residual for tree in trees) < 1e-9


def test_four_body_tree_basis_is_orthonormal() -> None:
    trees = sf.four_body_tree_bases(4, (0.55, 0.8, 1.05, 1.3))
    dimension = sf.multiplicity_dimension(4, 4)
    for tree in trees:
        assert tree.basis.shape[1] == dimension
        assert np.allclose(tree.basis.T @ tree.basis, np.eye(dimension), atol=2e-10)
        assert tree.diagonalization_residual < 2e-9


def test_pentagon_product_closes() -> None:
    for total in range(1, 6):
        trees = sf.four_body_tree_bases(total, (0.55, 0.8, 1.05, 1.3))
        product, edges = sf.pentagon_product(trees)
        assert len(edges) == 5
        assert np.allclose(product, np.eye(product.shape[0]), atol=2e-10)


def test_each_pentagon_edge_is_orthogonal() -> None:
    trees = sf.four_body_tree_bases(3, (0.55, 0.8, 1.05, 1.3))
    _, edges = sf.pentagon_product(trees)
    for edge in edges:
        assert np.allclose(edge.T @ edge, np.eye(edge.shape[0]), atol=2e-10)


def test_givens_compilation_exact() -> None:
    matrix = sf.three_body_recoupling(9, (0.7, 1.1, 0.9)).overlap
    rotations, diagonal = sf.givens_decompose(matrix)
    reconstructed = sf.givens_reconstruct(rotations, diagonal)
    assert np.allclose(reconstructed, matrix, atol=2e-10)
    assert len(rotations) <= matrix.shape[0] * (matrix.shape[0] - 1) // 2


def test_givens_diagonal_is_sign_matrix() -> None:
    matrix = sf.three_body_recoupling(7, (0.7, 1.1, 0.9)).overlap
    _, diagonal = sf.givens_decompose(matrix)
    values = np.diag(diagonal)
    assert np.allclose(np.abs(values), np.ones_like(values), atol=2e-10)


def test_figures_exist_in_both_formats() -> None:
    pdfs = sorted((ROOT / "figures").glob("*.pdf"))
    pngs = sorted((ROOT / "figures").glob("*.png"))
    assert len(pdfs) == len(pngs) == 30
    assert [path.stem for path in pdfs] == [path.stem for path in pngs]


def test_built_in_checks_pass() -> None:
    checks = sf.run_checks()
    assert len(checks) == 13
    assert all(bool(record["passed"]) for record in checks.values())


def test_generated_tables_exist() -> None:
    assert (ROOT / "tables" / "three_body_metrics.csv").is_file()
    assert (ROOT / "tables" / "pentagon_metrics.csv").is_file()
    assert (ROOT / "generated_tables" / "equal_shape_N2_matrix.tex").is_file()
