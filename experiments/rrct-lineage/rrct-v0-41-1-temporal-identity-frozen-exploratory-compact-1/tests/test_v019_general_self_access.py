import numpy as np
from rrct.general_self_access_experiment import _evaluate_probability, _provenance_route, _model_arbitration, _continuation_route

def test_task_consumers_perfect_identity():
    for truth in (0,1):
        p=float(truth)
        r=_evaluate_probability(p,truth,seed=1,episode=2,step=3)
        assert r['provenance_accuracy'] == 1.0
        assert r['model_arbitration_normalized_error'] < 1e-12
        assert r['model_arbitration_hard_accuracy'] == 1.0
        assert r['continuation_accuracy'] == 1.0

def test_task_consumers_reversed_identity_fail_hard_routes():
    for truth in (0,1):
        p=float(1-truth)
        r=_evaluate_probability(p,truth,seed=4,episode=5,step=6)
        assert r['provenance_accuracy'] == 0.0
        assert np.isclose(r['model_arbitration_normalized_error'],1.0)
        assert r['continuation_accuracy'] == 0.0

def test_probability_half_is_halfway_for_continuous_arbitration():
    for truth in (0,1):
        r=_evaluate_probability(0.5,truth,seed=7,episode=8,step=9)
        assert np.isclose(r['model_arbitration_normalized_error'],0.5)
