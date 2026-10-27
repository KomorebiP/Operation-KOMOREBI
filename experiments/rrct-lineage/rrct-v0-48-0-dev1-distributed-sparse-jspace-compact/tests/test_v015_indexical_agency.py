import numpy as np
from rrct.indexical_agency_experiment import _remap_matrix


def test_remap_matrices_are_orthogonal():
    for episode in range(3):
        m = _remap_matrix(episode)
        np.testing.assert_allclose(m.T @ m, np.eye(2), atol=1e-12)


def test_remap_cycles_three_distinct_maps():
    mats = [_remap_matrix(i) for i in range(3)]
    assert not np.allclose(mats[0], mats[1])
    assert not np.allclose(mats[1], mats[2])
    assert not np.allclose(mats[0], mats[2])
