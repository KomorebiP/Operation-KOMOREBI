import numpy as np

from rrct.selective_self_reopening_experiment import (
    V031_INTERFACE_DRIFT_THRESHOLD,
    _baseline_certificate,
    _monitor,
    _new_self_sensory_projector,
    _rediscover,
)
from rrct.action_provenance_experiment import _subspace_recall


def test_world_surprise_does_not_imply_interface_drift():
    seed = 5901
    b = _baseline_certificate(seed)
    world = _monitor(seed, "world_only", b)
    remap = _monitor(seed, "interface_remap", b)
    assert world["world_surprise"] > remap["world_surprise"]
    assert world["interface_drift"] < V031_INTERFACE_DRIFT_THRESHOLD
    assert remap["interface_drift"] > V031_INTERFACE_DRIFT_THRESHOLD


def test_reopening_can_relearn_or_revoke_interface():
    seed = 5907
    remap = _rediscover(seed, "interface_remap")
    takeover = _rediscover(seed, "takeover")
    assert remap.rank == 2
    assert _subspace_recall(remap.sensory_projector, _new_self_sensory_projector(seed)) > 0.95
    assert takeover.rank == 0
