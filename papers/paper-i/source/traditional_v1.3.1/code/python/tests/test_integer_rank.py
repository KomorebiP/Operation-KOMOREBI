import numpy as np
import pytest
from seed_calculus.core import semisimple_seed_rank


def test_no_float_rounding_beyond_53_bits():
    m = 2**53 + 1
    assert semisimple_seed_rank([1], [m]) == m


def test_unbounded_integer_ceiling():
    m = 10**400 + 1
    d = 3
    assert semisimple_seed_rank([d], [m]) == (m + d - 1) // d


def test_numpy_integer_counts():
    assert semisimple_seed_rank([np.int64(3)], [np.int64(7)]) == 3


def test_zero_multiplicity():
    assert semisimple_seed_rank([3, 7], [0, 0]) == 0


@pytest.mark.parametrize("ds,ms", [([1.5], [3]), ([2], [3.5]), ([True], [3]), ([2], [False]), ([0], [1]), ([2], [-1]), ([1, 2], [1]), ([], [])])
def test_invalid_counts_are_rejected(ds, ms):
    with pytest.raises(ValueError):
        semisimple_seed_rank(ds, ms)


def test_complex_symmetric_shortcut_is_rejected():
    import sympy as sp
    from seed_calculus.graphs import symmetric_graph_seed_rank
    from seed_calculus.core import single_operator_seed_rank
    a = sp.Matrix([[sp.I, 1], [1, -sp.I]])
    assert a == a.T and a**2 == sp.zeros(2)
    assert single_operator_seed_rank(a) == 1
    with pytest.raises(ValueError):
        symmetric_graph_seed_rank(a)


def test_unknown_realness_is_rejected():
    import sympy as sp
    from seed_calculus.graphs import symmetric_graph_seed_rank
    with pytest.raises(ValueError):
        symmetric_graph_seed_rank(sp.Matrix([[sp.Symbol("z")]]))


def test_real_symmetric_matrix_still_works():
    import sympy as sp
    from seed_calculus.graphs import symmetric_graph_seed_rank
    assert symmetric_graph_seed_rank(sp.Matrix([[0, 1], [1, 0]])) == 1
