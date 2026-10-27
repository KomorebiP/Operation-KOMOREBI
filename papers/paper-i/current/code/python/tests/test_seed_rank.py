import numpy as np
import sympy as sp

from seed_calculus.core import cyclic_span_dimension, matrix_units, semisimple_seed_rank, single_operator_seed_rank
from seed_calculus.examples import companion_matrix, full_matrix_orbit_dimension, repeated_jordan_operator


def test_companion_is_cyclic() -> None:
    c = companion_matrix([0, 0, 0, 0, 0])
    assert single_operator_seed_rank(c) == 1
    seed = np.zeros(5); seed[0] = 1
    assert cyclic_span_dimension([np.array(c, dtype=float)], [seed]) == 5


def test_repeated_jordan_requires_two_seeds() -> None:
    j = repeated_jordan_operator([3, 2], eigenvalue=4)
    assert single_operator_seed_rank(j) == 2


def test_semisimple_multiplicity_formula() -> None:
    assert semisimple_seed_rank([3], [7]) == 3
    assert semisimple_seed_rank([2, 4], [5, 9]) == 3
    assert semisimple_seed_rank([1, 1, 1], [2, 5, 3]) == 5


def test_full_matrix_algebra_representative_nonzero_vectors_are_cyclic() -> None:
    assert full_matrix_orbit_dimension(np.array([1, 0, 0, 0], dtype=float)) == 4
    assert full_matrix_orbit_dimension(np.array([1, -2, 3, 5], dtype=float)) == 4


def test_matrix_units_generate() -> None:
    units = matrix_units(3)
    seed = np.array([0, 1, 0], dtype=float)
    assert cyclic_span_dimension(units, [seed]) == 3
