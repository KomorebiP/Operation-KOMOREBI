import copy
import numpy as np
from rrct.agent import RRCTAgent
from rrct.temporal_identity_global_experiment import _deep_structural_equal, _identity_meta


def test_structural_audit_accepts_deepcopy_and_rejects_reset():
    agent = RRCTAgent(12, seed=18)
    for k in range(3):
        agent.step(np.linspace(-0.3, 0.4, 12) + 0.01*k)
    clone = copy.deepcopy(agent)
    assert _deep_structural_equal(agent, clone)
    clone.reset()
    assert not _deep_structural_equal(agent, clone)


def test_identity_meta_has_bounded_uncertainty_and_signed_identity():
    low = _identity_meta(0.0, 0.0)
    mid = _identity_meta(0.5, 0.5)
    high = _identity_meta(1.0, 1.0)
    assert low[0] == -1.0 and high[0] == 1.0
    assert mid[1] == 1.0
    assert low[1] == 0.0 and high[1] == 0.0
