"""Regression witnesses for reviewed boundaries, not universal proofs."""
import numpy as np
import pytest
from projector_transfer_semigroups.bayes import (
    bayes_update, packet_bayes_update, coarsen_probability,
    effective_coarse_likelihood, bayesian_coarsening_defect,
    canonical_bayesian_partition,
)

@pytest.mark.parametrize('prior', [[-1, 2], [np.nan, 1], [np.inf, 1], [[1, 2]]])
def test_invalid_prior_rejected(prior):
    with pytest.raises(ValueError):
        bayes_update(np.array(prior), np.ones(2))

@pytest.mark.parametrize('likelihood', [[np.nan, 1], [np.inf, 1]])
def test_nonfinite_likelihood_rejected(likelihood):
    with pytest.raises(ValueError):
        bayes_update(np.array([.4, .6]), np.array(likelihood))

@pytest.mark.parametrize('groups', [[[0], [0, 1]], [[0]], [[0.2], [1]], [[], [0, 1]]])
def test_invalid_packet_partition_rejected(groups):
    with pytest.raises(ValueError):
        packet_bayes_update(np.array([.4, .6]), np.ones(2), groups)

def test_zero_evidence_packet_contributes_zero():
    r = packet_bayes_update(np.array([.25, .25, .5]), np.array([0, 0, 2]), [[0, 1], [2]])
    np.testing.assert_array_equal(r['conditional_shapes'][0], [0, 0])
    np.testing.assert_array_equal(r['packet_masses'], [0, 1])
    np.testing.assert_array_equal(r['reconstructed'], r['posterior'])

def test_zero_prior_packet_effective_factorization():
    p, l, groups = np.array([0., 0., 1.]), np.array([3., 8., 2.]), [[0, 1], [2]]
    r = effective_coarse_likelihood(p, l, groups)
    np.testing.assert_array_equal(r, [0, 2])
    np.testing.assert_allclose(coarsen_probability(bayes_update(p, l), groups),
                               bayes_update(coarsen_probability(p, groups), r))
    d = bayesian_coarsening_defect(p, l, groups, np.array([1., 3.]))
    np.testing.assert_allclose(d['defect'], d['factored_defect'], atol=1e-15)

def test_individual_evidences_do_not_ensure_sequential_evidence():
    p, l, k = np.array([.5, .5]), np.array([1., 0.]), np.array([0., 1.])
    assert l @ p > 0 and k @ p > 0
    with pytest.raises(ValueError):
        bayes_update(bayes_update(p, l), k)

def test_one_packet_closure_is_uninformative():
    p, l = np.array([.5, .5]), np.array([1., 3.])
    assert canonical_bayesian_partition([l]) == ((0,), (1,))
    np.testing.assert_array_equal(coarsen_probability(bayes_update(p, l), [[0, 1]]), [1])
    np.testing.assert_array_equal(bayes_update(coarsen_probability(p, [[0, 1]]), np.array([7.])), [1])

def test_tolerance_proximity_is_not_an_equivalence_relation():
    l = np.array([0., .75, 1.5])
    assert abs(l[0]-l[1]) <= 1 and abs(l[1]-l[2]) <= 1 and abs(l[0]-l[2]) > 1
    assert canonical_bayesian_partition([l], atol=1) == ((0, 1), (2,))
    assert canonical_bayesian_partition([l[[1, 0, 2]]], atol=1) == ((0, 1, 2),)

def test_hidden_inverse_does_not_imply_full_resolvent_exists():
    a = np.diag([0., 1.])
    np.testing.assert_array_equal(np.linalg.inv(-a[1:, 1:]), [[-1.]])
    with pytest.raises(np.linalg.LinAlgError):
        np.linalg.inv(-a)

def test_subgenerator_may_have_defective_exit_density():
    a = np.zeros((2, 2))
    assert np.all(a.sum(axis=0) <= 0)
    p = np.array([.5, .5])
    assert -np.ones(2) @ a @ p == 0
    assert np.ones(2) @ p == 1
