from __future__ import annotations

import math
from pathlib import Path

import mpmath as mp
import numpy as np
import sympy as sp

import projector_generated_special_functions_ii as sf


ROOT = Path(__file__).resolve().parents[1]


def test_stieltjes_first_detail_derivative() -> None:
    value = sf.detail_derivative_from_stieltjes(2, 1, 0, 1.0, 1, 1)
    assert abs(value + math.log(2) / math.sqrt(2)) < 1e-14


def test_character_stieltjes_order_zero() -> None:
    lhs = mp.stieltjes(0, mp.mpf(1) / 4) - mp.stieltjes(0, mp.mpf(3) / 4)
    rhs = 4 * mp.dirichlet(1, [0, 1, 0, -1])
    assert abs(lhs - rhs) < mp.mpf("1e-45")


def test_detail_variance_fourier_identity() -> None:
    children = np.array([1.2 + 0.3j, -0.7 + 0.1j, 0.4 - 0.9j, 1.1 + 0.2j])
    details = sf.transformed_details(children)
    direct = sf.detail_variance(children)
    transformed = sum(details[j] * details[-j % 4] for j in range(1, 4))
    assert abs(direct - transformed) < 1e-12


def test_detail_variance_pairwise_identity() -> None:
    children = np.array([1.2 + 0.3j, -0.7 + 0.1j, 0.4 - 0.9j])
    direct = sf.detail_variance(children)
    pairwise = sum((children[i] - children[j]) ** 2 for i in range(3) for j in range(i + 1, 3)) / 3
    assert abs(direct - pairwise) < 1e-12


def test_bernoulli_euler_two_channel_identity() -> None:
    x = sp.symbols("x")
    for n in range(2, 9):
        children = sf.bernoulli_children_exact(n, sp.Rational(0), 2)
        high = sp.simplify((children[0] - children[1]) / sp.sqrt(2))
        expected = -sp.Rational(n, 2) * sp.euler(n - 1, 0) / sp.sqrt(2)
        assert sp.simplify(high - expected) == 0


def test_three_channel_variance() -> None:
    children = sf.bernoulli_children_exact(4, sp.Rational(0), 3)
    variance = sp.simplify(sum(value**2 for value in children) - sum(children) ** 2 / 3)
    assert variance == sp.Rational(32, 27)


def test_primitive_resultants_are_rational() -> None:
    for ell in (3, 4, 5):
        for n in range(2, 8):
            value = sf.primitive_packet_resultant_exact(n, sp.Rational(0), ell)
            assert value.is_rational


def test_energy_complete_monotonicity() -> None:
    mu = sf.mobius_sieve(100_000)
    values = sf.packet_energy_values(np.arange(1, 80), 2.0, 2.0, 100_000, 1, mu)
    rows = sf.finite_differences(values, 6)
    for order, row in enumerate(rows):
        assert np.min(((-1) ** order) * row) >= -1e-16


def test_hankel_positive_semidefinite() -> None:
    mu = sf.mobius_sieve(100_000)
    values = sf.packet_energy_values(np.arange(0, 18), 2.0, 2.0, 100_000, 1, mu)
    matrix = np.array([[values[i + j] for j in range(8)] for i in range(8)])
    assert np.linalg.eigvalsh(matrix)[0] > -1e-13


def test_resolvent_has_pick_sign() -> None:
    mu = sf.mobius_sieve(50_000)
    value_upper = sf.energy_resolvent(0.4 + 0.7j, 2.0, 2.0, 50_000, 1, mu)
    value_lower = sf.energy_resolvent(0.4 - 0.7j, 2.0, 2.0, 50_000, 1, mu)
    assert value_upper.imag > 0
    assert value_lower.imag < 0
    assert abs(value_upper) > 0
    assert abs(value_lower) > 0


def test_zeta_ratio_coordinate_identity() -> None:
    mu = sf.mobius_sieve(400_000)
    for k in range(1, 6):
        direct = sf.packet_energy_values([k], 2.0, 2.0, 400_000, 1, mu)[0]
        exact = float(sf.energy_from_zeta_ratio(k, 2.0, 2.0, 1))
        assert abs(direct - exact) < 3e-14


def test_energy_asymptotic_constant() -> None:
    constant = sf.energy_asymptotic_constant(2.0, 2.0, 1)
    expected = 3 / (2 ** 2.5 * math.pi ** 1.5)
    assert abs(constant - expected) < 1e-15


def test_gamma_moment_prediction() -> None:
    alpha = 1.5
    assert abs(float(mp.gamma(alpha + 1) / mp.gamma(alpha)) - alpha) < 1e-15
    assert abs(float(mp.gamma(alpha + 2) / mp.gamma(alpha)) - alpha * (alpha + 1)) < 1e-15


def test_empirical_gamma_scaling() -> None:
    mu = sf.mobius_sieve(300_000)
    values, weights = sf.gamma_weighted_sample(50_000, 2.0, 2.0, 300_000, 1, mu)
    mean, second = sf.weighted_moments(values, weights, 2)
    variance = second - mean**2
    assert abs(mean - 1.5) < 0.05
    assert abs(variance - 1.5) < 0.10


def test_character_gram_is_hermitian_positive() -> None:
    nmax = 100_000
    mu = sf.mobius_sieve(nmax)
    chars = sf.characters_mod5(nmax)
    gram = sf.character_gram_matrix(1000, 2.0, 2.0, nmax, mu, chars)
    assert np.max(np.abs(gram - gram.conj().T)) < 1e-13
    assert np.linalg.eigvalsh(gram)[0] > -1e-13


def test_character_decoherence_improves() -> None:
    nmax = 200_000
    mu = sf.mobius_sieve(nmax)
    chars = sf.characters_mod5(nmax)
    small = sf.normalized_correlation(sf.character_gram_matrix(100, 2.0, 2.0, nmax, mu, chars))
    large = sf.normalized_correlation(sf.character_gram_matrix(100_000, 2.0, 2.0, nmax, mu, chars))
    mask = ~np.eye(4, dtype=bool)
    assert np.max(np.abs(large[mask])) < np.max(np.abs(small[mask]))


def test_all_figures_present() -> None:
    pdfs = sorted((ROOT / "figures").glob("*.pdf"))
    pngs = sorted((ROOT / "figures").glob("*.png"))
    assert len(pdfs) == len(pngs) == 20


def test_result_ledger_passed() -> None:
    import json

    data = json.loads((ROOT / "results" / "results.json").read_text())
    assert data["checks"] == data["passed"] == 61
