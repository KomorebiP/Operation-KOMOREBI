from __future__ import annotations

import numpy as np

from priq import (
    averaging_section,
    bayes_commutation_residual,
    bayes_update,
    best_k_residuals,
    block_sum_matrix,
    exact_lift_tensor,
    hidden_exchange_fields,
    hyperedge_energy_statistics,
    integrate_rk4,
    normalization_perturbation_bound,
    posterior_error_certificate,
    quotient_defect,
    recover_coarse_tensor,
    simulate_prediction_update_filter,
    slot_kernel_residual,
    symmetrize_inputs,
    transform_tensor,
)


def test_exact_tensor_lifts_orders_one_to_three() -> None:
    rng = np.random.default_rng(12)
    pi = [0, 0, 1, 1]
    C = block_sum_matrix(pi)
    E = averaging_section(pi)
    for order in (1, 2, 3):
        coarse = rng.normal(size=(2, *([2] * order)))
        hidden = rng.normal(size=(4, *([4] * order)))
        fine = exact_lift_tensor(coarse, C, E, hidden_tensor=hidden)
        assert np.linalg.norm(quotient_defect(fine, coarse, C)) < 1e-11
        assert slot_kernel_residual(fine, C) < 1e-11


def test_coordinate_recovery_and_negative_control() -> None:
    rng = np.random.default_rng(13)
    pi = [0, 0, 1, 1]
    C = block_sum_matrix(pi)
    E = averaging_section(pi)
    coarse = rng.normal(size=(2, 2, 2))
    fine = exact_lift_tensor(coarse, C, E, hidden_tensor=rng.normal(size=(4, 4, 4)))
    recovered = recover_coarse_tensor(fine, pi)
    assert recovered.witness is None
    assert recovered.max_fiber_variation < 1e-11
    assert np.allclose(recovered.coarse_tensor, coarse, atol=1e-11, rtol=1e-11)

    perturbed = fine.copy()
    perturbed[0, 0, 0] += 0.125
    failed = recover_coarse_tensor(perturbed, pi)
    assert failed.witness is not None
    assert failed.max_fiber_variation > 0.1


def test_multilevel_defect_identity() -> None:
    rng = np.random.default_rng(14)
    C21 = np.asarray([[1, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], dtype=float)
    C10 = np.asarray([[1, 1, 0], [0, 0, 1]], dtype=float)
    C20 = C10 @ C21
    order = 2
    A2 = rng.normal(size=(4, 4, 4))
    A1 = rng.normal(size=(3, 3, 3))
    A0 = rng.normal(size=(2, 2, 2))

    def defect(Af: np.ndarray, Ac: np.ndarray, C: np.ndarray) -> np.ndarray:
        m = Af.ndim - 1
        left = transform_tensor(Af, C, [np.eye(Af.shape[1])] * m)
        right = transform_tensor(Ac, np.eye(Ac.shape[0]), [C] * m)
        return left - right

    d21 = defect(A2, A1, C21)
    d10 = defect(A1, A0, C10)
    d20 = defect(A2, A0, C20)
    rhs = transform_tensor(d21, C10, [np.eye(4)] * order) + transform_tensor(
        d10, np.eye(2), [C21] * order
    )
    assert np.allclose(d20, rhs, atol=1e-12, rtol=1e-12)


def test_hidden_exchange_flow_and_mass() -> None:
    fine, coarse, C = hidden_exchange_fields()
    x0 = np.asarray([0.31, 0.19, 0.17, 0.33])
    z0 = C @ x0
    xf = integrate_rk4(fine, x0, 2.0, max_step=1e-3)
    zc = integrate_rk4(coarse, z0, 2.0, max_step=1e-3)
    assert np.linalg.norm(C @ xf - zc, ord=1) < 2e-12
    assert abs(xf.sum() - 1.0) < 2e-12
    assert np.min(xf) >= -1e-12


def test_exact_bayesian_filter_cocycle() -> None:
    fine, coarse, C = hidden_exchange_fields()
    x0 = np.asarray([0.31, 0.19, 0.17, 0.33])
    coarse_likelihoods = [
        np.asarray([1.4, 0.75]),
        np.asarray([0.8, 1.5]),
        np.asarray([1.25, 0.9]),
        np.asarray([0.7, 1.35]),
    ]
    fine_likelihoods = [C.T @ lam for lam in coarse_likelihoods]
    trace = simulate_prediction_update_filter(
        x0,
        C @ x0,
        fine,
        coarse,
        fine_likelihoods,
        coarse_likelihoods,
        [0.4, 0.6, 0.5, 0.7],
        max_step=1e-3,
    )
    pred_res = max(
        np.linalg.norm(C @ xf - xc, ord=1)
        for xf, xc in zip(trace.fine_predictions, trace.coarse_predictions, strict=True)
    )
    post_res = max(
        np.linalg.norm(C @ xf - xc, ord=1)
        for xf, xc in zip(trace.fine_posteriors, trace.coarse_posteriors, strict=True)
    )
    assert pred_res < 3e-12
    assert post_res < 3e-12
    assert np.max(np.abs(trace.fine_evidence - trace.coarse_evidence)) < 3e-12

    mu = np.asarray([0.21, 0.29, 0.18, 0.32])
    lamc = np.asarray([1.6, 0.65])
    lamf = C.T @ lamc
    assert bayes_commutation_residual(mu, lamf, lamc, C) < 1e-14
    assert np.allclose(bayes_update(mu, 3.2 * lamf), bayes_update(mu, lamf))


def test_controlled_perturbation_bounds() -> None:
    epsilon = 0.02
    fine, coarse, C = hidden_exchange_fields(epsilon=epsilon)
    x0 = np.asarray([0.31, 0.19, 0.17, 0.33])
    duration = 0.8
    xf = integrate_rk4(fine, x0, duration, max_step=5e-4)
    zc = integrate_rk4(coarse, C @ x0, duration, max_step=5e-4)
    actual = np.linalg.norm(C @ xf - zc, ord=1)
    assert actual <= 2.0 * epsilon * duration + 1e-10

    eta = 0.03
    lamc = np.asarray([1.3, 0.8])
    lamf = C.T @ lamc + eta * np.asarray([1.0, -1.0, 0.0, 0.0])
    assert np.all(lamf > 0)
    mu = np.asarray([0.28, 0.22, 0.20, 0.30])
    bayes_actual = bayes_commutation_residual(mu, lamf, lamc, C)
    zstar = min(float(lamf.min()), float(lamc.min()))
    assert bayes_actual <= 2.0 * eta / zstar + 1e-12


def test_symmetric_normalization_perturbation_bound() -> None:
    rng = np.random.default_rng(16)
    for _ in range(100):
        u = rng.uniform(0.05, 2.0, size=7)
        v = rng.uniform(0.05, 2.0, size=7)
        actual = np.linalg.norm(u / u.sum() - v / v.sum(), ord=1)
        bound = normalization_perturbation_bound(u, v)
        expected = 2.0 * np.linalg.norm(u - v, ord=1) / max(float(u.sum()), float(v.sum()))
        assert np.isclose(bound, expected)
        assert actual <= bound + 1e-14


def test_pruning_symmetry_and_certificate_recurrence() -> None:
    rng = np.random.default_rng(15)
    tensor = symmetrize_inputs(rng.normal(size=(3, 3, 3, 3)))
    assert np.allclose(tensor, np.swapaxes(tensor, 1, 2))
    assert np.allclose(tensor, np.swapaxes(tensor, 2, 3))

    coefficients = np.geomspace(1.0, 1e-3, 24)
    residuals = best_k_residuals(coefficients)
    assert residuals.shape == (25,)
    assert np.all(np.diff(residuals) <= 1e-14)
    assert residuals[-1] < 1e-12
    probabilities, entropy, effective = hyperedge_energy_statistics(coefficients)
    assert np.isclose(probabilities.sum(), 1.0)
    assert entropy > 0
    assert 1.0 < effective < coefficients.size

    final, minus, plus = posterior_error_certificate(
        0.0,
        flow_lipschitz=[1.0, 1.0, 1.0],
        bayes_lipschitz=[1.2, 1.1, 1.3],
        flow_defects=[0.01, 0.02, 0.01],
        bayes_defects=[0.005, 0.004, 0.006],
    )
    manual = 0.0
    for Lb, dp, db in zip([1.2, 1.1, 1.3], [0.01, 0.02, 0.01], [0.005, 0.004, 0.006]):
        manual = Lb * (manual + dp) + db
    assert np.isclose(final, manual)
    assert minus.size == 3
    assert plus.size == 4
