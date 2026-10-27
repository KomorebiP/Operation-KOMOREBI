import numpy as np
import pytest
from rrct.metacognitive_closure_experiment import MetacognitiveAccessReadout, _same_norm_other_efference


def test_readout_features_have_expected_shape():
    x = MetacognitiveAccessReadout.features(np.zeros(16), np.zeros(12))
    assert x.shape == (29,)
    assert x[0] == 1.0


def test_readout_roundtrip_simple_linear_signal():
    rng = np.random.default_rng(4)
    x = rng.normal(size=(200, 29)); x[:, 0] = 1.0
    y = x[:, 1:4].copy()
    model = MetacognitiveAccessReadout(precision=1e-6)
    model.fit(x, y)
    assert model.beta is not None
    pred = x @ model.beta
    assert np.sqrt(np.mean((pred-y)**2)) < 1e-4


def test_same_norm_other_efference_preserves_norm_but_not_fixed_transform():
    rng = np.random.default_rng(12)
    command = np.asarray([0.4, -0.7])
    values = np.stack([_same_norm_other_efference(command, rng) for _ in range(20)])
    np.testing.assert_allclose(np.linalg.norm(values, axis=1), np.linalg.norm(command), atol=1e-12)
    assert np.std(values[:, 0]) > 0.1


def test_readout_validates_shapes():
    with pytest.raises(ValueError):
        MetacognitiveAccessReadout.features(np.zeros(15), np.zeros(12))
