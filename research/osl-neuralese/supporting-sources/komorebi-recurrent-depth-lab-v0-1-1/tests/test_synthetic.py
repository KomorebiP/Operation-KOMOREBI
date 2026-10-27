from __future__ import annotations

import numpy as np
from numpy.testing import assert_allclose

from krd_lab.analysis import (
    affine_dmd,
    block_transport_certificate,
    contraction_certificate,
    coordinate_projectors,
    detect_slider,
    last_write_selector,
    linear_operator_fit,
    modulo_cache_profile,
    path_independence,
    pca_reduce,
)
from krd_lab.synthetic import (
    contraction_system,
    generate_trajectories,
    rotation_system,
    slider_system,
)


ATOL = 1e-10


def _unordered_eigenvalue_error(actual: np.ndarray, expected: np.ndarray) -> float:
    left = np.asarray(actual, dtype=complex).reshape(-1)
    right = np.asarray(expected, dtype=complex).reshape(-1)
    if left.size != right.size:
        return float("inf")
    forward = max(float(np.min(np.abs(value - right))) for value in left)
    reverse = max(float(np.min(np.abs(value - left))) for value in right)
    return max(forward, reverse)


def _relative_residual(operator: np.ndarray, source: np.ndarray, target: np.ndarray) -> float:
    denominator = max(float(np.linalg.norm(target)), np.finfo(float).eps)
    return float(np.linalg.norm(target - operator @ source) / denominator)


def _rotation(theta: float) -> np.ndarray:
    return np.array(
        [
            [np.cos(theta), -np.sin(theta)],
            [np.sin(theta), np.cos(theta)],
        ]
    )


def test_known_contraction_reaches_its_fixed_point_with_a_valid_certificate() -> None:
    system, fixed_point = contraction_system()
    initial = np.array([4.0, -3.0])
    states = system.trajectory(initial, steps=30)
    errors = np.linalg.norm(states - fixed_point, axis=1)
    kappa = float(np.linalg.norm(system.operator, ord=2))

    assert_allclose(system.step(fixed_point), fixed_point, atol=1e-12)
    assert np.all(errors[1:] <= kappa * errors[:-1] + 1e-12)
    assert errors[-1] <= kappa**30 * errors[0] + 1e-12

    certificate = contraction_certificate(
        states,
        operator=system.operator,
        fixed_point=fixed_point,
    )
    assert certificate.status == "conditional_on_supplied_linear_operator"
    assert certificate.fixed_point_error_bound is not None
    assert certificate.observed_final_error is not None
    assert certificate.bound_holds is True
    assert certificate.observed_final_error <= certificate.fixed_point_error_bound + 1e-12


def test_q7_rotation_is_an_exact_orbit_and_affine_dmd_recovers_it() -> None:
    q = 7
    theta = 2.0 * np.pi / q
    system = rotation_system(theta=theta)
    initial = np.array([1.0, 0.2])
    states = system.trajectory(initial, steps=q)

    assert_allclose(states[q], initial, atol=1e-12)
    assert_allclose(
        np.linalg.norm(states, axis=1),
        np.full(q + 1, np.linalg.norm(initial)),
        atol=1e-12,
    )
    assert min(np.linalg.norm(states[index] - initial) for index in range(1, q)) > 1e-3

    fit = affine_dmd(states)
    expected_eigenvalues = np.exp(np.array([1j * theta, -1j * theta]))
    assert_allclose(fit.operator, system.operator, atol=ATOL, rtol=ATOL)
    assert_allclose(fit.offset, np.zeros(2), atol=ATOL)
    assert fit.one_step_residual < ATOL
    assert _unordered_eigenvalue_error(fit.eigenvalues, expected_eigenvalues) < ATOL
    assert_allclose(np.abs(fit.eigenvalues), np.ones(2), atol=ATOL)


def test_slider_has_constant_drift_and_a_nontrivial_jordan_chain() -> None:
    system = slider_system()
    states = system.trajectory(np.array([0.0, 1.0]), steps=10)
    expected = np.column_stack([np.arange(11, dtype=float), np.ones(11)])

    assert_allclose(states, expected, atol=1e-12)
    assert_allclose(np.diff(states, n=2, axis=0), 0.0, atol=1e-12)

    result = detect_slider(states)
    assert result.detected
    assert result.acceleration_ratio < 1e-12
    assert result.direction_stability > 1.0 - 1e-12

    nilpotent = system.operator - np.eye(2)
    assert np.linalg.norm(nilpotent) > 0.5
    assert_allclose(nilpotent @ nilpotent, np.zeros((2, 2)), atol=1e-12)
    assert np.linalg.matrix_rank(nilpotent, tol=1e-12) == 1

    rng = np.random.default_rng(1103)
    source = rng.normal(size=(2, 32))
    target = system.operator @ source
    fit = linear_operator_fit(source, target)
    assert fit.fully_excited
    assert fit.effective_rank == 2
    assert fit.relative_residual < ATOL
    assert_allclose(fit.operator, system.operator, atol=ATOL, rtol=ATOL)


def test_mixed_blocks_reconstruct_all_paths_and_c_to_o_to_s_transport() -> None:
    contraction = np.array([[0.55]])
    orbit = _rotation(0.41)
    slider = np.array([[1.0, 0.30], [0.0, 1.0]])
    c_to_o = np.array([[0.20], [-0.10]])
    o_to_s = np.array([[0.10, -0.05], [0.02, 0.04]])

    operator = np.zeros((5, 5))
    operator[0:1, 0:1] = contraction
    operator[1:3, 1:3] = orbit
    operator[3:5, 3:5] = slider
    operator[1:3, 0:1] = c_to_o
    operator[3:5, 1:3] = o_to_s

    p_c, p_o, p_s = coordinate_projectors(5, ((0,), (1, 2), (3, 4)))
    certificate = block_transport_certificate(
        operator,
        (p_c, p_o, p_s),
        exponent=3,
        tolerance=1e-11,
    )
    assert certificate.valid
    assert certificate.one_step_reconstruction_residual < 1e-11
    assert certificate.path_power_residual < 1e-11

    direct_c_to_s = p_s @ operator @ p_c
    two_step_c_to_s = p_s @ np.linalg.matrix_power(operator, 2) @ p_c
    through_orbit = (p_s @ operator @ p_o) @ (p_o @ operator @ p_c)

    assert_allclose(direct_c_to_s, np.zeros((5, 5)), atol=1e-12)
    assert np.linalg.norm(through_orbit) > 1e-6
    assert_allclose(two_step_c_to_s, through_orbit, atol=1e-12)
    assert_allclose(two_step_c_to_s[3:5, 0:1], o_to_s @ c_to_o, atol=1e-12)


def test_polynomial_koopman_feature_space_closes_exactly_out_of_sample() -> None:
    coefficient = 0.60
    offset = -0.20

    def feature(values: np.ndarray) -> np.ndarray:
        values = np.asarray(values, dtype=float)
        return np.vstack([np.ones_like(values), values, values**2])

    train = np.linspace(-1.0, 1.0, 257)
    source = feature(train)
    target = feature(coefficient * train + offset)
    fit = linear_operator_fit(source, target)
    expected = np.array(
        [
            [1.0, 0.0, 0.0],
            [offset, coefficient, 0.0],
            [offset**2, 2.0 * coefficient * offset, coefficient**2],
        ]
    )

    held_out = np.random.default_rng(2025).uniform(-1.25, 1.25, size=129)
    held_source = feature(held_out)
    held_target = feature(coefficient * held_out + offset)

    assert fit.fully_excited
    assert fit.effective_rank == 3
    assert fit.relative_residual < ATOL
    assert_allclose(fit.operator, expected, atol=ATOL, rtol=ATOL)
    assert _relative_residual(fit.operator, held_source, held_target) < ATOL
    assert _unordered_eigenvalue_error(
        np.linalg.eigvals(fit.operator),
        np.array([1.0, coefficient, coefficient**2]),
    ) < ATOL


def test_incomplete_koopman_features_report_held_out_leakage() -> None:
    def feature(values: np.ndarray) -> np.ndarray:
        values = np.asarray(values, dtype=float)
        return np.vstack([np.ones_like(values), values])

    def step(values: np.ndarray) -> np.ndarray:
        return 0.50 * values + 0.20 * values**2

    train = np.linspace(-1.0, 1.0, 101)
    fit = linear_operator_fit(feature(train), feature(step(train)))
    held_out = np.linspace(-0.985, 0.995, 113)
    leakage = _relative_residual(
        fit.operator,
        feature(held_out),
        feature(step(held_out)),
    )

    assert fit.fully_excited
    assert fit.effective_rank == 2
    assert leakage > 1e-2


def test_linear_fit_flags_an_unexcited_lane() -> None:
    operator = np.diag([0.40, 0.80])
    amplitudes = 0.40 ** np.arange(8, dtype=float)
    source = np.vstack([amplitudes, np.zeros_like(amplitudes)])
    target = operator @ source
    fit = linear_operator_fit(source, target)

    unseen = np.array([0.0, 1.0])
    unseen_error = float(np.linalg.norm(fit.operator @ unseen - operator @ unseen))
    assert fit.effective_rank == 1
    assert not fit.fully_excited
    assert fit.relative_residual < ATOL
    assert unseen_error > 0.5


def test_last_write_selector_exposes_modulo_cache_collisions() -> None:
    step_count = 10
    modulus = 3
    selector = last_write_selector(step_count, modulus)
    expected = np.zeros((modulus, step_count))
    expected[0, 9] = 1.0
    expected[1, 7] = 1.0
    expected[2, 8] = 1.0

    assert_allclose(selector, expected, atol=0.0)
    assert np.linalg.matrix_rank(selector) == modulus
    assert step_count - np.linalg.matrix_rank(selector) == 7

    values = np.arange(step_count * 2, dtype=float).reshape(step_count, 2)
    final_cache = selector @ values
    overwritten_change = values.copy()
    overwritten_change[0] += np.array([1000.0, -1000.0])
    retained_change = values.copy()
    retained_change[9] += np.array([1000.0, -1000.0])

    assert_allclose(selector @ overwritten_change, final_cache, atol=0.0)
    assert not np.allclose(selector @ retained_change, final_cache)

    profile = modulo_cache_profile(step_count, modulus)
    assert profile["retained_last_step"] == {"0": 9, "1": 7, "2": 8}
    assert profile["collision_count"] == 7
    assert not profile["lossless"]

    lossless_selector = last_write_selector(2, 3)
    assert_allclose(lossless_selector.T @ lossless_selector, np.eye(2), atol=0.0)


def test_random_initializations_collapse_to_the_same_endpoint() -> None:
    system, fixed_point = contraction_system()
    rng = np.random.default_rng(271828)
    initials = [value for value in rng.normal(size=(64, 2))]
    steps = 100
    trajectories = generate_trajectories(system, initials, steps=steps)
    kappa = float(np.linalg.norm(system.operator, ord=2))

    for initial, trajectory in zip(initials, trajectories, strict=True):
        initial_error = float(np.linalg.norm(initial - fixed_point))
        final_error = float(np.linalg.norm(trajectory[-1] - fixed_point))
        assert final_error <= kappa**steps * initial_error + 2e-12

    result = path_independence(trajectories, tail=8)
    assert result.seeds == 64
    assert result.final_pairwise_max < 1e-10
    assert result.normalized_final_dispersion < 1e-10


def test_small_successive_change_does_not_imply_small_remaining_error() -> None:
    states = np.array([[1.0], [0.99]])
    naive_delta = float(np.linalg.norm(states[-1] - states[-2]))
    certificate = contraction_certificate(
        states,
        kappa=0.99,
        fixed_point=np.array([0.0]),
    )

    assert naive_delta < 0.02
    assert certificate.fixed_point_error_bound is not None
    assert certificate.fixed_point_error_bound > 0.90
    assert_allclose(certificate.fixed_point_error_bound, 0.99, atol=1e-12)
    assert certificate.bound_holds is True


def test_noncontractive_and_nonnormal_cases_do_not_receive_certificates() -> None:
    translation = np.array([[0.0], [1e-12], [2e-12]])
    translation_result = contraction_certificate(
        translation,
        kappa=1.0,
        fixed_point=np.array([0.0]),
    )
    assert translation_result.fixed_point_error_bound is None
    assert translation_result.bound_holds is None

    operator = np.array([[0.50, 10.0], [0.0, 0.50]])
    assert_allclose(np.max(np.abs(np.linalg.eigvals(operator))), 0.50, atol=1e-12)
    assert np.linalg.norm(operator, ord=2) > 1.0
    initial = np.array([20.0, 1.0])
    states = np.vstack([initial, operator @ initial])
    nonnormal_result = contraction_certificate(
        states,
        operator=operator,
        fixed_point=np.zeros(2),
    )
    assert nonnormal_result.kappa > 1.0
    assert nonnormal_result.fixed_point_error_bound is None
    assert nonnormal_result.bound_holds is None


def test_empirical_tail_ratios_are_diagnostic_not_certificates() -> None:
    states = np.array([[1.0], [0.5], [0.25], [0.125]])
    result = contraction_certificate(states, fixed_point=np.array([0.0]))
    assert result.status == "empirical_only"
    assert result.kappa < 1.0
    assert result.fixed_point_error_bound is None
    assert result.bound_holds is None


def test_constant_pca_chart_reports_zero_numerical_rank() -> None:
    states = np.full((12, 4), 1000.0)
    result = pca_reduce(states, rank=3)
    assert result.effective_rank == 0
    assert result.reconstruction_residual == 0.0
    assert_allclose(result.explained_variance_ratio, 0.0, atol=0.0)
