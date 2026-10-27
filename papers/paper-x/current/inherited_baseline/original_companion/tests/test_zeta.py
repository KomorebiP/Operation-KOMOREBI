from fractions import Fraction

import sympy as sp

from projector_seed_residuals.zeta import (
    estimated_seed_dimension,
    exact_singular_dimension,
    singular_power_count,
    singular_square_zeta_expression,
    smooth_count,
    weighted_count,
    weighted_zeta_expression,
)


def test_smooth_counts() -> None:
    assert [smooth_count(3, 2, depth) for depth in range(1, 5)] == [1, 9, 81, 729]


def test_weighted_counts() -> None:
    weights = [1, 2, 4]
    assert [weighted_count(2, weights, depth) for depth in range(1, 7)] == [1, 2, 8, 32, 256, 2048]


def test_weighted_zeta_coefficients() -> None:
    T = sp.Symbol("T")
    expression = weighted_zeta_expression(2, [1, 2, 4])
    series = sp.series(expression, T, 0, 10).removeO().expand()
    for depth in range(1, 9):
        assert int(series.coeff(T, depth)) == weighted_count(2, [1, 2, 4], depth)


def test_singular_square_counts() -> None:
    assert [singular_power_count(3, 2, depth) for depth in range(1, 7)] == [1, 3, 3, 9, 9, 27]


def test_singular_square_zeta_coefficients() -> None:
    T = sp.Symbol("T")
    expression = singular_square_zeta_expression(3)
    series = sp.series(expression, T, 0, 12).removeO().expand()
    for depth in range(1, 11):
        assert int(series.coeff(T, depth)) == singular_power_count(3, 2, depth)


def test_exact_singular_dimension() -> None:
    assert exact_singular_dimension(2) == Fraction(1, 2)
    assert exact_singular_dimension(3) == Fraction(2, 3)
    assert exact_singular_dimension(5) == Fraction(4, 5)


def test_estimated_dimension_converges() -> None:
    counts = [singular_power_count(3, 2, depth) for depth in range(5, 41)]
    estimate = estimated_seed_dimension(counts, 3, list(range(5, 41)))
    assert abs(estimate - 0.5) < 0.01
