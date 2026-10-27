import numpy as np
from rrct.yoked_indexical_agency_experiment import _remap_matrix


def test_yoked_experiment_remaps_remain_orthogonal():
    for i in range(3):
        m = _remap_matrix(i)
        np.testing.assert_allclose(m.T @ m, np.eye(2), atol=1e-12)
