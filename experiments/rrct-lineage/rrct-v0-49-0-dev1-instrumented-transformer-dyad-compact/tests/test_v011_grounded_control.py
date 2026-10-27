import copy
import numpy as np

from rrct.grounded_control_experiment import (
    GroundedTrackingWorld,
    WeightedRidgeTransfer,
    grounded_world_spec,
)


def test_action_changes_future_world_and_observation():
    spec = grounded_world_spec(17)
    left = GroundedTrackingWorld(spec)
    right = GroundedTrackingWorld(spec)
    before = left.observe(10)
    left.advance(np.asarray([0.7, -0.4]))
    right.advance(np.asarray([-0.7, 0.4]))
    assert not np.allclose(left.position, right.position)
    assert not np.allclose(left.observe(10), right.observe(10))
    assert np.allclose(before, GroundedTrackingWorld(spec).observe(10))


def test_zero_action_coupling_removes_action_effect():
    spec = grounded_world_spec(19)
    left = GroundedTrackingWorld(spec, action_coupling=0.0)
    right = GroundedTrackingWorld(spec, action_coupling=0.0)
    left.advance(np.asarray([1.0, -1.0]))
    right.advance(np.asarray([-1.0, 1.0]))
    assert np.allclose(left.position, right.position)


def test_world_copy_is_counterfactually_replayable():
    world = GroundedTrackingWorld(grounded_world_spec(23))
    clone = copy.deepcopy(world)
    actions = [np.asarray([0.2, -0.1]), np.asarray([-0.4, 0.6])]
    for action in actions:
        world.advance(action)
        clone.advance(action)
    assert np.allclose(world.position, clone.position)
    assert world.tracking_loss() == clone.tracking_loss()


def test_world_spec_is_deterministic_and_digest_stable():
    a = grounded_world_spec(29)
    b = grounded_world_spec(29)
    assert a.digest() == b.digest()
    assert np.array_equal(a.goal, b.goal)
    assert np.array_equal(a.initial_position, b.initial_position)
    assert np.array_equal(a.disturbances, b.disturbances)


def test_weighted_ridge_fit_and_prediction_are_finite():
    x = np.asarray([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
    y = np.asarray([0.0, 1.0, -1.0, 0.5])
    w = np.full(4, 0.25)
    model = WeightedRidgeTransfer(2, 1.0)
    model.fit(x, y, w)
    values = model.predict(x)
    assert values.shape == (4,)
    assert np.all(np.isfinite(values))
