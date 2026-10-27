import numpy as np
import pytest

from rrct.agent import RRCTAgent
from rrct.causal_self_boundary_experiment import CausalSelfBoundaryModel, _meta_projection


def test_register_executed_action_is_bounded_and_returned():
    agent = RRCTAgent(12, seed=3)
    value = agent.register_executed_action(np.asarray([2.0, -3.0]))
    np.testing.assert_allclose(value, [1.0, -1.0])
    np.testing.assert_allclose(agent.choose_action(), [1.0, -1.0])


def test_register_executed_action_validates_shape():
    agent = RRCTAgent(12, seed=3)
    with pytest.raises(ValueError):
        agent.register_executed_action(np.zeros(3))


def test_boundary_update_is_prequential_and_adapts_to_inversion():
    passive = np.zeros((7, 2), dtype=np.float64)
    prior = 0.2 * np.eye(2)
    model = CausalSelfBoundaryModel(passive, prior, 1e-3)
    obs = np.zeros(12)
    for _ in range(30):
        action = np.asarray([0.8, -0.6])
        nxt = np.zeros(12)
        nxt[:2] = action @ (-0.2 * np.eye(2))
        model.update(obs, action, nxt)
    assert np.all(np.isfinite(model.action_effect))
    assert model.action_effect[0, 0] < 0.0
    assert model.action_effect[1, 1] < 0.0


def test_meta_projection_is_deterministic_and_orthonormal():
    a = _meta_projection(11, 16)
    b = _meta_projection(11, 16)
    np.testing.assert_allclose(a, b)
    np.testing.assert_allclose(a.T @ a, np.eye(4), atol=1e-12)
