from __future__ import annotations

import numpy as np

from projector_transfer_semigroups.bayes import (
    bayes_update,
    bayesian_coarsening_defect,
    bayesian_sufficient_partition,
    canonical_bayesian_partition,
    coarsen_probability,
)


def test_blockwise_constant_likelihood_commutes_with_coarsening() -> None:
    prior = np.array([0.10, 0.25, 0.20, 0.45])
    groups = ((0, 1), (2, 3))
    likelihood = np.array([0.4, 0.4, 1.7, 1.7])
    sufficient, coarse_likelihood = bayesian_sufficient_partition(likelihood, groups)
    assert sufficient
    left = coarsen_probability(bayes_update(prior, likelihood), groups)
    right = bayes_update(coarsen_probability(prior, groups), coarse_likelihood)
    assert np.max(np.abs(left - right)) < 1e-15


def test_nonconstant_likelihood_exposes_hidden_within_packet_shape() -> None:
    groups = ((0, 1), (2, 3))
    likelihood = np.array([0.2, 1.1, 0.7, 0.7])
    p = np.array([0.25, 0.05, 0.35, 0.35])
    q = np.array([0.05, 0.25, 0.35, 0.35])
    assert np.max(np.abs(coarsen_probability(p, groups) - coarsen_probability(q, groups))) == 0.0
    left = coarsen_probability(bayes_update(p, likelihood), groups)
    right = coarsen_probability(bayes_update(q, likelihood), groups)
    assert np.max(np.abs(left - right)) > 1e-2


def test_exact_information_loss_factorization() -> None:
    prior = np.array([0.10, 0.25, 0.20, 0.45])
    groups = ((0, 1), (2, 3))
    likelihood = np.array([0.2, 0.9, 1.4, 0.8])
    coarse_likelihood = np.array([0.55, 1.10])
    record = bayesian_coarsening_defect(prior, likelihood, groups, coarse_likelihood)
    assert np.max(np.abs(record["defect"] - record["factored_defect"])) < 2e-15
    assert np.linalg.norm(record["defect"], 1) <= record["l1_bound"] + 1e-15


def test_global_likelihood_scaling_is_invisible() -> None:
    prior = np.array([0.10, 0.25, 0.20, 0.45])
    groups = ((0, 1), (2, 3))
    coarse = np.array([0.4, 1.7])
    fine = 3.2 * np.array([0.4, 0.4, 1.7, 1.7])
    record = bayesian_coarsening_defect(prior, fine, groups, coarse)
    assert np.max(np.abs(record["defect"])) < 2e-15


def test_canonical_partition_is_coarsest_joint_level_set_partition() -> None:
    family = [
        np.array([0.2, 0.2, 0.7, 0.7, 1.1]),
        np.array([0.8, 0.8, 0.1, 0.1, 0.5]),
    ]
    groups = canonical_bayesian_partition(family)
    assert groups == ((0, 1), (2, 3), (4,))
    for likelihood in family:
        sufficient, _ = bayesian_sufficient_partition(likelihood, groups)
        assert sufficient


def test_nested_sufficient_tower_commutes() -> None:
    prior = np.array([0.05, 0.15, 0.30, 0.10, 0.25, 0.15])
    fine_groups = ((0, 1), (2, 3), (4, 5))
    coarse_groups = ((0, 1), (2,))
    likelihood = np.array([0.4, 0.4, 1.2, 1.2, 2.0, 2.0])
    _, middle_likelihood = bayesian_sufficient_partition(likelihood, fine_groups)
    assert np.allclose(middle_likelihood, [0.4, 1.2, 2.0])
    middle_prior = coarsen_probability(prior, fine_groups)
    fine_posterior = coarsen_probability(bayes_update(prior, likelihood), fine_groups)
    middle_posterior = bayes_update(middle_prior, middle_likelihood)
    assert np.max(np.abs(fine_posterior - middle_posterior)) < 1e-15

    # The first two middle states are not sufficient for a further merge.
    sufficient, _ = bayesian_sufficient_partition(middle_likelihood, coarse_groups)
    assert not sufficient
