import numpy as np

from projector_transfer_semigroups.markov import (
    symmetric_random_walk,
    exact_lumped_chain,
    evolve_markov,
    lumping_defect,
    finite_horizon_lumping_error,
    survival_curve,
)
from projector_transfer_semigroups.bayes import (
    bayes_update,
    packet_bayes_update,
    beta_binomial_posterior,
    bayesian_flow,
    bayesian_flow_generator,
    hmm_filter,
)


def test_random_walk_mass_parity_and_variance() -> None:
    positions, p = symmetric_random_walk(18)
    assert abs(p.sum() - 1.0) < 1e-15
    assert all((positions - 18) % 2 == 0)
    assert abs(positions @ p) < 1e-15
    assert abs((positions**2) @ p - 18.0) < 1e-12


def test_exact_markov_lumping() -> None:
    k, c, kbar = exact_lumped_chain()
    assert np.max(np.abs(lumping_defect(k, c, kbar))) < 1e-15
    for n in range(16):
        assert np.max(np.abs(finite_horizon_lumping_error(k, c, kbar, n))) < 2e-14


def test_lumping_error_linear_bound() -> None:
    k, c, kbar = exact_lumped_chain()
    kp = k.copy()
    kp[:, 0] += np.array([0.01, 0.0, -0.01, 0.0])
    eps = np.linalg.norm(lumping_defect(kp, c, kbar), 1)
    for n in range(1, 15):
        actual = np.linalg.norm(finite_horizon_lumping_error(kp, c, kbar, n), 1)
        assert actual <= n * eps + 1e-12


def test_bayes_composition() -> None:
    p = np.array([0.1, 0.2, 0.3, 0.4])
    l1 = np.array([0.2, 0.8, 0.6, 0.3])
    l2 = np.array([0.9, 0.4, 0.7, 0.5])
    assert np.max(np.abs(bayes_update(bayes_update(p, l1), l2) - bayes_update(p, l1 * l2))) < 1e-15


def test_packet_bayes_reconstruction() -> None:
    p = np.array([0.1, 0.2, 0.3, 0.4])
    l = np.array([0.2, 0.8, 0.6, 0.3])
    result = packet_bayes_update(p, l, [[0, 1], [2, 3]])
    assert np.max(np.abs(result["posterior"] - result["reconstructed"])) < 1e-15
    assert abs(result["packet_masses"].sum() - 1.0) < 1e-15


def test_beta_binomial_update() -> None:
    result = beta_binomial_posterior(2.0, 3.0, 7, 10)
    assert result["a"] == 9.0
    assert result["b"] == 6.0
    assert abs(result["mean"] - 0.6) < 1e-15


def test_bayesian_flow_semigroup_and_generator() -> None:
    p = np.array([0.12, 0.18, 0.30, 0.40])
    g = np.array([-0.4, 0.1, 0.8, 1.2])
    assert np.max(np.abs(bayesian_flow(bayesian_flow(p, g, 0.4), g, 0.7) - bayesian_flow(p, g, 1.1))) < 1e-14
    t = 0.73
    h = 1e-6
    derivative = (bayesian_flow(p, g, t + h) - bayesian_flow(p, g, t - h)) / (2 * h)
    expected = bayesian_flow_generator(bayesian_flow(p, g, t), g)
    assert np.max(np.abs(derivative - expected)) < 2e-10


def test_hmm_filter_normalizes() -> None:
    k = np.array([[0.75, 0.25], [0.25, 0.75]])
    likelihoods = [np.array([0.85, 0.25]), np.array([0.35, 0.8]), np.array([0.9, 0.2])]
    states = hmm_filter(k, np.array([0.6, 0.4]), likelihoods)
    assert len(states) == 4
    assert all(abs(p.sum() - 1.0) < 1e-15 for p in states)
    assert all(np.all(p >= 0) for p in states)


def test_survival_monotone_and_hazard_nonnegative() -> None:
    a = np.array([[-0.45, 0.12, 0.0], [0.30, -0.52, 0.18], [0.0, 0.28, -0.60]])
    curves = survival_curve(a, np.array([1.0, 0.0, 0.0]), np.linspace(0, 10, 101))
    assert np.max(np.diff(curves["survival"])) <= 1e-12
    assert np.min(curves["hazard"]) >= -1e-12
