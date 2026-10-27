from fractions import Fraction
from math import factorial

import mpmath as mp
import numpy as np
import sympy as sp

from special_functions import (
    D_root_average,
    D_value,
    amice_transform_coefficients,
    block_appell_polynomials,
    block_product,
    congruential_euler_coefficients,
    congruential_euler_value,
    congruential_power_coefficients,
    reciprocal_block_coefficients,
    root_filter_average,
    root_filter_value,
    secant_coefficients,
    secant_parameter_polynomial,
    spectral_zeta_N2_partial,
    spectral_zeta_N2_positive,
    theta_polynomials,
    transfer_exponential,
    transfer_exponential_hypergeom,
    transfer_tangent_coefficients,
    transfer_tangent_value,
    secant_value,
    registry_entries,
)


def test_root_filter_identity() -> None:
    coeff = [complex((m + 1) ** 2) for m in range(18)]
    f = lambda z: sum(coeff[m] * z**m / factorial(m) for m in range(len(coeff)))
    for N in (2, 3, 4, 5):
        for j in range(N):
            lhs = root_filter_value(coeff, N, j, 0.37 + 0.19j)
            rhs = root_filter_average(f, N, j, 0.37 + 0.19j)
            assert abs(lhs - rhs) < 1e-10


def test_transfer_exponential_reconstruction() -> None:
    for N in (2, 3, 4, 5):
        z = 0.44 - 0.23j
        total = sum(transfer_exponential(N, j, z, terms=45) for j in range(N))
        assert abs(total - np.exp(z)) < 1e-12


def test_hypergeometric_form() -> None:
    mp.mp.dps = 60
    for N in (2, 3, 4, 5):
        for j in range(N):
            lhs = transfer_exponential(N, j, mp.mpf("0.31"), terms=60)
            rhs = transfer_exponential_hypergeom(N, j, mp.mpf("0.31"))
            assert abs(lhs - rhs) < mp.mpf("1e-45")


def test_D_root_average_and_ode() -> None:
    for N in (2, 3, 4, 5, 6):
        z = 0.7 + 0.2j
        assert abs(D_value(N, z, 60) - D_root_average(N, z)) < 1e-11
        # Sympy checks the defining ODE through a finite series.
        x = sp.Symbol("x")
        series = sum(sp.Rational((-1) ** n, sp.factorial(N * n)) * x ** (N * n) for n in range(8))
        residual = sp.diff(series, x, N) + series
        assert sp.series(residual, x, 0, N * 6).removeO() == 0


def test_secant_inverse_and_power_law() -> None:
    for N in (2, 3, 4, 5):
        den = [Fraction((-1) ** n) for n in range(9)]
        inv = reciprocal_block_coefficients(den, N, 8)
        product = block_product(den, inv, N, 8)
        assert product == [Fraction(1)] + [Fraction(0)] * 8
        a2 = secant_coefficients(N, 2, 8)
        assert a2 == block_product(inv, inv, N, 8)


def test_tangent_recurrence() -> None:
    for N in (2, 3, 4, 5):
        T = transfer_tangent_coefficients(N, 8)
        for m in range(9):
            lhs = sum(Fraction((-1) ** k * sp.binomial(N * m + N - 1, N * k)) * T[m - k] for k in range(m + 1))
            assert lhs == Fraction((-1) ** m)
    assert transfer_tangent_coefficients(2, 5)[:4] == [1, 2, 16, 272]


def test_congruential_inverse() -> None:
    for N in (2, 3, 4, 5, 6):
        for j in range(N):
            E = congruential_euler_coefficients(N, j, 7)
            for n in range(8):
                lhs = sum(Fraction(sp.binomial(N * n + j, N * q)) * E[q] for q in range(n + 1))
                assert lhs == (1 if n == 0 else 0)


def test_block_appell_derivative() -> None:
    x = sp.Symbol("x")
    polys = block_appell_polynomials(3, 1, 2, 9)
    for m in range(1, len(polys)):
        assert sp.expand(sp.diff(polys[m], x) - m * polys[m - 1]) == 0


def test_parameter_polynomials_match_integer_order() -> None:
    r = sp.Symbol("r")
    for N in (2, 3, 4):
        for n in range(6):
            poly = secant_parameter_polynomial(N, n)
            for order in (1, 2, 3):
                coeff = secant_coefficients(N, order, n)[n]
                assert sp.Rational(coeff.numerator, coeff.denominator) == sp.expand(poly).subs(r, order)


def test_theta_first_polynomials() -> None:
    x = sp.Symbol("x")
    theta = theta_polynomials(3)
    assert theta[0] == 1
    assert sp.expand(theta[1] + x * (x + 1)) == 0
    assert sp.expand(theta[2] - x * (x + 1) * (5 * x**2 + x + 2)) == 0


def test_D4_factorization() -> None:
    z = sp.Symbol("z")
    lhs = sum(sp.Rational((-1) ** n, sp.factorial(4 * n)) * z ** (4 * n) for n in range(8))
    rhs = sp.cos(z / sp.sqrt(2)) * sp.cosh(z / sp.sqrt(2))
    assert sp.series(lhs - rhs, z, 0, 28).removeO().expand() == 0


def test_spectral_zeta_N2() -> None:
    mp.mp.dps = 50
    s = mp.mpf("3.5")
    exact = spectral_zeta_N2_positive(s)
    partial = spectral_zeta_N2_partial(s, 200000)
    assert abs(exact - partial) < mp.mpf("3e-14")
    assert abs(exact - mp.pi ** (-s) * (2**s - 1) * mp.zeta(s)) < mp.mpf("1e-45")


def test_amice_transform_basic() -> None:
    # A(t)=e^{2t}; A(log(1+T))=(1+T)^2.
    coeff = [Fraction(2**n) for n in range(7)]
    result = amice_transform_coefficients(coeff, 6)
    assert result[:3] == [Fraction(1), Fraction(2), Fraction(1)]
    assert result[3:] == [Fraction(0)] * 4



def test_transfer_exponential_addition_law() -> None:
    for N in (2, 3, 4, 5):
        x = 0.27
        y = -0.18
        for residue in range(N):
            lhs = transfer_exponential(N, residue, x + y, terms=55)
            rhs = sum(
                transfer_exponential(N, a, x, terms=55)
                * transfer_exponential(N, b, y, terms=55)
                for a in range(N)
                for b in range(N)
                if (a + b) % N == residue
            )
            assert abs(lhs - rhs) < 1e-12


def test_secant_differential_law() -> None:
    mp.mp.dps = 50
    for N in (2, 3, 4, 5):
        for order in (1, 2, 3):
            z = mp.mpf("0.19")
            derivative = mp.diff(lambda w: secant_value(N, order, w, terms=70), z)
            rhs = order * transfer_tangent_value(N, z, terms=70) * secant_value(N, order, z, terms=70)
            assert abs(derivative - rhs) < mp.mpf("1e-35")


def test_congruential_analytic_series() -> None:
    mp.mp.dps = 50
    for N in (2, 3, 4, 5):
        for j in range(N):
            z = mp.mpf("0.11")
            coeff = congruential_euler_coefficients(N, j, 20)
            series = sum(
                mp.mpf(value.numerator) / value.denominator * z ** (N * n) / mp.factorial(N * n)
                for n, value in enumerate(coeff)
            )
            exact = congruential_euler_value(N, j, z, terms=70)
            assert abs(series - exact) < mp.mpf("1e-40")


def test_congruential_power_law() -> None:
    for N in (2, 3, 4):
        for j in range(N):
            first = congruential_power_coefficients(N, j, 1, 7)
            second = congruential_power_coefficients(N, j, 2, 7)
            assert second == block_product(first, first, N, 7)


def test_secancy_polynomial_binomial_law() -> None:
    r, s = sp.symbols("r s")
    for N in (2, 3, 4):
        for n in range(6):
            lhs = secant_parameter_polynomial(N, n).subs({sp.Symbol("r"): r + s})
            rhs = sum(
                sp.binomial(N * n, N * q)
                * secant_parameter_polynomial(N, q).subs({sp.Symbol("r"): r})
                * secant_parameter_polynomial(N, n - q).subs({sp.Symbol("r"): s})
                for q in range(n + 1)
            )
            assert sp.expand(lhs - rhs) == 0


def test_theta_integrality() -> None:
    x = sp.Symbol("x")
    for poly in theta_polynomials(7):
        assert sp.Poly(poly, x).domain == sp.ZZ


def test_registry_is_complete_and_unique() -> None:
    entries = registry_entries()
    assert len(entries) == 15
    assert len({entry.family for entry in entries}) == len(entries)
