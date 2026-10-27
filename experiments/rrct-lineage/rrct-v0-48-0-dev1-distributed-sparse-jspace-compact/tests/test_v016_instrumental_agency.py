import numpy as np
import pytest
from rrct.instrumental_agency_experiment import InstrumentalOwnershipClassifier, V016_WINDOW, _window_statistics


def test_window_statistics_detects_linear_probe_effect():
    rng = np.random.default_rng(4)
    z = rng.normal(size=(V016_WINDOW, 2))
    b = np.asarray([[0.3, 0.0], [0.0, -0.2]])
    r = z @ b
    stat = _window_statistics(z, r)
    assert stat[0] > 0.2
    assert stat[1] > 0.0


def test_temporal_roll_reduces_probe_specific_gain():
    rng = np.random.default_rng(8)
    z = rng.normal(size=(V016_WINDOW, 2))
    r = z @ np.asarray([[0.4, 0.0], [0.0, 0.25]])
    aligned = _window_statistics(z, r)
    shuffled = _window_statistics(np.roll(z, 1, axis=0), r)
    assert aligned[1] > shuffled[1]


def test_classifier_learns_separable_examples():
    x = np.asarray([[0.4, .02],[0.35,.018],[0.1,.001],[0.12,.002]], dtype=float)
    y = np.asarray([1,1,0,0], dtype=float)
    m = InstrumentalOwnershipClassifier(precision=.1);m.fit(x,y)
    assert m.predict_probability(x[0]) > m.predict_probability(x[-1])


def test_window_shape_validation():
    with pytest.raises(ValueError):
        _window_statistics(np.zeros((7,2)), np.zeros((7,2)))
