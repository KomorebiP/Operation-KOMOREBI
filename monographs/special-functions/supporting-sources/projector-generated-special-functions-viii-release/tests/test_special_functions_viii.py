from __future__ import annotations

import math
import numpy as np

import projector_generated_special_functions_viii as sf


def test_symmetric_q_number_classical_limit() -> None:
    assert abs(sf.q_number(3.25, 1.0) - 3.25) < 1e-15
    assert abs(sf.q_number(-2.0, 0.7) + sf.q_number(2.0, 0.7)) < 1e-14


def test_q_algebra_on_untruncated_rows() -> None:
    q = 0.73
    k0, kp, km = sf.q_local_matrices(15, 0.8, q)
    commutator = km @ kp - kp @ km
    target = np.diag([sf.q_number(2 * (n + 0.8), q) for n in range(15)])
    assert np.max(np.abs(commutator[:-1, :-1] - target[:-1, :-1])) < 1e-9


def test_q_casimir_is_scalar() -> None:
    q = 0.71
    kappa = 0.9
    casimir = sf.q_casimir_matrix(8, (kappa,), q, (0,))
    scalar = sf.q_number(kappa, q) * sf.q_number(kappa - 1, q)
    assert np.max(np.abs(casimir - scalar * np.eye(casimir.shape[0]))) < 1e-10


def test_two_body_q_hahn_vector_is_lowest_weight() -> None:
    q = 0.68
    vector = sf.q_two_body_lowest_coefficients(9, 0.65, 1.2, q)
    lowering = sf.q_lowering_matrix(9, (0.65, 1.2), q)
    np.testing.assert_allclose(np.linalg.norm(vector), 1.0, atol=1e-13)
    assert np.max(np.abs(lowering @ vector)) < 1e-10


def test_multiplicity_dimension() -> None:
    for total in range(7):
        frame3 = sf.q_multiplicity_frame(total, (0.6, 0.9, 1.1), 0.72)
        frame4 = sf.q_multiplicity_frame(total, (0.6, 0.9, 1.1, 1.3), 0.72)
        assert frame3.shape[1] == sf.multiplicity_dimension(total, 3)
        assert frame4.shape[1] == sf.multiplicity_dimension(total, 4)


def test_three_body_q_racah_is_orthogonal() -> None:
    data = sf.q_three_body_recoupling(7, (0.7, 1.1, 0.9), 0.74)
    assert np.max(np.abs(data.overlap.T @ data.overlap - np.eye(8))) < 1e-10


def test_pair_casimir_spectrum_matches_closed_form() -> None:
    total = 7
    q = 0.74
    data = sf.q_three_body_recoupling(total, (0.7, 1.1, 0.9), q)
    expected = sf.q_pair_spectrum(total, 0.7, 1.1, q)
    assert np.max(np.abs(data.left_eigenvalues - expected)) < 1e-9


def test_opposing_q_casimir_is_tridiagonal() -> None:
    data = sf.q_three_body_recoupling(10, (0.7, 1.1, 0.9), 0.72)
    assert sf.tridiagonal_residual(data.right_in_left) < 1e-8


def test_equal_shape_one_excitation_closed_form() -> None:
    for q in (0.2, 0.5, 0.8, 1.0):
        exact = sf.equal_shape_one_excitation_matrix(q)
        computed = sf.q_three_body_recoupling(1, (0.5, 0.5, 0.5), q).overlap
        assert np.max(np.abs(exact - computed)) < 1e-10


def test_squared_q_racah_kernel_is_bistochastic() -> None:
    matrix = sf.q_three_body_recoupling(8, (0.7, 1.1, 0.9), 0.73).overlap
    assert sf.doubly_stochastic_residual(matrix**2) < 1e-10


def test_one_excitation_entropy_monotone() -> None:
    q_grid = np.linspace(0.05, 1.0, 150)
    entropy = [sf.row_entropies(sf.equal_shape_one_excitation_matrix(float(q)) ** 2)[0] for q in q_grid]
    assert np.min(np.diff(entropy)) > -1e-10


def test_higher_excitation_entropy_is_not_universally_monotone() -> None:
    q_grid = np.linspace(0.12, 1.0, 120)
    entropy = [sf.row_entropies(sf.q_three_body_recoupling(3, (0.5, 0.5, 0.5), float(q)).overlap**2)[1] for q in q_grid]
    assert np.min(np.diff(entropy)) < -1e-5


def test_q_to_one_limits() -> None:
    classical = sf.q_three_body_recoupling(6, (0.7, 1.1, 0.9), 1.0).overlap
    near = sf.q_three_body_recoupling(6, (0.7, 1.1, 0.9), 0.99999).overlap
    near = sf.align_signed_matrix(classical, near)
    assert np.max(np.abs(classical - near)) < 1e-5


def test_q_to_zero_equal_shape_routes() -> None:
    matrix = sf.equal_shape_one_excitation_matrix(1e-7)
    target = np.array([[0.0, 1.0], [1.0, 0.0]])
    assert np.max(np.abs(matrix - target)) < 2e-7


def test_deformation_generator_is_skew() -> None:
    data = sf.deformation_generator(6, (0.7, 1.1, 0.9), theta=0.35)
    generator = np.asarray(data["generator"])
    assert np.max(np.abs(generator + generator.T)) < 1e-12
    assert float(data["tangent_residual"]) < 2e-7


def test_four_body_q_pentagon_closes() -> None:
    trees = sf.q_four_body_tree_bases(4, (0.55, 0.8, 1.05, 1.3), 0.78)
    product, _ = sf.q_pentagon_product(trees)
    assert np.max(np.abs(product - np.eye(product.shape[0]))) < 1e-9


def test_givens_compiler_reconstructs_q_racah_matrix() -> None:
    matrix = sf.q_three_body_recoupling(8, (0.7, 1.1, 0.9), 0.73).overlap
    rotations, diagonal = sf.givens_decompose(matrix)
    reconstructed = sf.givens_reconstruct(rotations, diagonal)
    assert len(rotations) <= matrix.shape[0] * (matrix.shape[0] - 1) // 2
    assert np.max(np.abs(reconstructed - matrix)) < 1e-10


def test_q_racah_duality() -> None:
    q = 0.73
    N = 6
    A, B, G, D = 0.6, 0.8, -N - 1.0, 0.4
    alpha, beta, gamma, delta = q**A, q**B, q**G, q**D
    for n in range(N + 1):
        for y in range(N + 1):
            left = sf.q_racah_polynomial(n, y, alpha, beta, gamma, delta, q)
            right = sf.q_racah_polynomial(y, n, gamma, delta, alpha, beta, q)
            assert abs(left - right) < 1e-10


def test_q_racah_classical_limit() -> None:
    q = 0.999
    N = 6
    A, B, G, D = 0.6, 0.8, -N - 1.0, 0.4
    alpha, beta, gamma, delta = q**A, q**B, q**G, q**D
    error = 0.0
    for n in range(4):
        for y in range(N + 1):
            q_value = sf.q_racah_polynomial(n, y, alpha, beta, gamma, delta, q).real
            classical = sf.classical_racah_polynomial(n, y, A, B, G, D)
            error = max(error, abs(q_value - classical))
    assert error < 2e-4


def test_askey_wilson_difference_equation() -> None:
    q = 0.7
    parameters = (0.2, 0.3, -0.25, 0.4)
    for n in range(5):
        for theta in np.linspace(0.4, 2.6, 6):
            z = np.exp(1j * theta)
            function = lambda value, degree=n: sf.askey_wilson_r(degree, value, *parameters, q)
            left = sf.askey_wilson_operator(function, z, *parameters, q)
            eigenvalue = q ** (-n) + np.prod(parameters) * q ** (n - 1)
            assert abs(left - eigenvalue * function(z)) < 1e-9
