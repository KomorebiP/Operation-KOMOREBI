from __future__ import annotations

import numpy as np

from proof_path_theory import (
    AuditRegime,
    audit_priority,
    constant_rate_regime,
    effective_reviewer_count,
    equal_weight_variance,
    equicorrelated_covariance,
    equicorrelated_effective_count,
    generalized_least_squares_weights,
    optimal_depth,
    refinement_decision,
    shared_bias_mse,
    simulate_audit_queue,
    stopping_depth,
    weighted_estimator_variance,
)


def test_equicorrelated_effective_count_formula() -> None:
    assert equicorrelated_effective_count(10, 0.0) == 10.0
    assert np.isclose(equicorrelated_effective_count(10, 0.2), 10 / 2.8)


def test_covariance_effective_count_matches_formula() -> None:
    covariance = equicorrelated_covariance(10, 1.0, 0.2)
    assert np.isclose(effective_reviewer_count(covariance), 10 / 2.8)


def test_gls_is_minimum_variance_against_equal_weights() -> None:
    covariance = np.array([[1.0, 0.3, 0.1], [0.3, 2.0, 0.2], [0.1, 0.2, 0.7]])
    gls = generalized_least_squares_weights(covariance)
    equal = np.ones(3) / 3
    assert np.isclose(gls.sum(), 1.0)
    assert weighted_estimator_variance(gls, covariance) <= equal_weight_variance(covariance) + 1e-12


def test_shared_bias_creates_mse_floor() -> None:
    mse = shared_bias_mse(
        np.array([1, 10, 100000]),
        individual_variance=1.0,
        shared_bias=0.3,
        lens_variance=0.04,
    )
    assert mse[0] > mse[1] > mse[2]
    assert np.isclose(mse[-1], 0.13, atol=2e-5)


def test_audit_regimes() -> None:
    assert constant_rate_regime(2, 3) is AuditRegime.STABLE
    assert constant_rate_regime(3, 3) is AuditRegime.CRITICAL
    assert constant_rate_regime(4, 3) is AuditRegime.UNSTABLE


def test_audit_queue_constant_rates() -> None:
    stable = simulate_audit_queue([2.0] * 20, [3.0] * 20, initial_backlog=5.0)
    critical = simulate_audit_queue([3.0] * 20, [3.0] * 20, initial_backlog=5.0)
    unstable = simulate_audit_queue([4.0] * 20, [3.0] * 20)
    assert stable.final_backlog == 0.0
    assert critical.final_backlog == 5.0
    assert unstable.final_backlog == 20.0


def test_audit_priority_handles_zero_cost() -> None:
    assert audit_priority(error_probability=0.2, consequence=5, dependency_reach=2, audit_cost=0) == float("inf")


def test_refinement_decision_and_bridge_override() -> None:
    rejected = refinement_decision(
        {"verification": 0.1, "bridge": 0.2},
        cost_increase=1.0,
        goal_weights={"verification": 1.0, "bridge": 0.1},
    )
    retained = refinement_decision(
        {"verification": 0.1, "bridge": 0.9},
        cost_increase=1.0,
        goal_weights={"verification": 1.0, "bridge": 0.1},
        bridge_override=0.8,
    )
    assert not rejected.keep
    assert retained.keep
    assert retained.reason == "bridge-retention override"


def test_goal_weights_select_different_depths() -> None:
    residuals = [1.0, 0.4, 0.15, 0.08]
    costs = [0.0, 1.0, 3.0, 8.0]
    shallow = optimal_depth(residuals, costs, residual_weight=1.0, cost_weight=0.5)
    deep = optimal_depth(residuals, costs, residual_weight=10.0, cost_weight=0.1)
    assert shallow < deep


def test_stopping_depth() -> None:
    assert stopping_depth(
        [1.0, 0.4, 0.15, 0.08, 0.06],
        [1, 2, 4, 8, 16],
        residual_tolerance=0.1,
        marginal_gain_floor=0.01,
    ) == 3
