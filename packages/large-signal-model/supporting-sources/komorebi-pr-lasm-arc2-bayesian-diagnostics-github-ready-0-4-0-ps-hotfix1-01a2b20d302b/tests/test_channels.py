from __future__ import annotations
import numpy as np
from komorebi_arc2 import entry


def test_kronecker_self_mask():
    g = np.array([[1, 0], [0, 1]], dtype=np.int16)
    out = entry.kronecker_self_mask_exact(g)
    assert out.shape == (4, 4)
    assert np.array_equal(out[:2, :2], g)
    assert np.array_equal(out[2:, 2:], g)


def test_cell_gravity_down():
    g = np.array([[2, 0], [0, 0], [0, 3]], dtype=np.int16)
    out = entry.cell_gravity(g, "down")
    assert np.array_equal(out, np.array([[0, 0], [0, 0], [2, 3]], dtype=np.int16))


def test_repeated_shape_selector():
    g = np.zeros((7, 10), dtype=np.int16)
    g[0, 0:2] = 2
    g[3, 0:2] = 3
    g[5:7, 7:9] = 4
    out = entry.select_most_repeated_shape_exact(g)
    assert out.shape == (1, 2)
    assert np.count_nonzero(out) == 2


def test_connect_markers_row():
    g = np.zeros((5, 7), dtype=np.int16)
    g[2, 1] = 6
    g[2, 5] = 6
    out = entry.connect_markers_exact(g, "h", True, 6)
    assert np.all(out[2, 1:6] == 6)
