import numpy as np
import sympy as sp

from seed_refinement.weighted import (
    Edge,
    direct_inverse_mod,
    neumann_inverse_mod,
    path_counts,
    path_zeta,
    zeta_coefficients,
)


def graph() -> list[Edge]:
    return [
        Edge(0, 0, 2), Edge(0, 1, 1), Edge(1, 1, 3),
        Edge(1, 2, 2), Edge(2, 0, 1), Edge(2, 2, 4),
    ]


def test_path_zeta_matches_enumeration() -> None:
    t = sp.Symbol("t")
    zeta = path_zeta(3, graph(), [0], [2], t)
    assert path_counts(3, graph(), [0], [2], 30) == zeta_coefficients(zeta, t, 30)


def test_zeta_is_rational() -> None:
    t = sp.Symbol("t")
    zeta = sp.cancel(path_zeta(3, graph(), [0], [2], t))
    numerator, denominator = sp.fraction(zeta)
    assert numerator.is_polynomial(t)
    assert denominator.is_polynomial(t)


def test_filtered_inverse_exact_mod_powers() -> None:
    D = np.array([[3, 0, 0], [0, 5, 0], [0, 0, 7]], dtype=object)
    K = np.array([[0, 2, 0], [0, 0, 4], [8, 0, 0]], dtype=object)
    for depth in range(1, 11):
        modulus = 2**depth
        direct = direct_inverse_mod(D, K, 2, depth)
        filtered = neumann_inverse_mod(D, K, 2, depth)
        assert not np.any((direct - filtered) % modulus)


def test_filtered_inverse_odd_prime() -> None:
    D = np.array([[2, 0], [0, 4]], dtype=object)
    K = np.array([[0, 3], [9, 0]], dtype=object)
    for depth in range(1, 8):
        modulus = 3**depth
        assert not np.any((direct_inverse_mod(D, K, 3, depth) - neumann_inverse_mod(D, K, 3, depth)) % modulus)
