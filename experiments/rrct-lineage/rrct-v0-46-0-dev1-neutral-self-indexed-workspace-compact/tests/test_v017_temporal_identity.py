import copy
import numpy as np
import pytest

from rrct.agent import RRCTAgent
from rrct.temporal_identity_experiment import _cosine, _dynamic_state_vector


def test_dynamic_state_vector_reset_breaks_snapshot_similarity():
    agent = RRCTAgent(12, seed=17)
    for k in range(4):
        agent.step(np.linspace(-0.4, 0.6, agent.observation_dim) + 0.01 * k)
    before = _dynamic_state_vector(agent)
    copied = copy.deepcopy(agent)
    assert _cosine(before, _dynamic_state_vector(copied)) > 0.999999
    copied.reset()
    assert _cosine(before, _dynamic_state_vector(copied)) < 0.1


def test_cosine_zero_vector_is_defined_as_zero():
    z = np.zeros(4)
    assert _cosine(z, z) == 0.0


def test_cosine_shape_mismatch_raises_numpy_error():
    with pytest.raises(ValueError):
        _cosine(np.zeros(3), np.zeros(4))
