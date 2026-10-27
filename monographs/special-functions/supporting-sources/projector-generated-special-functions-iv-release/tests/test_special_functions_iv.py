from __future__ import annotations

import json
import math
from pathlib import Path

import mpmath as mp
import numpy as np

import projector_generated_special_functions_iv as sf

ROOT = Path(__file__).resolve().parents[1]


def small_data(a: float = 2.0, beta: float = 2.0, nmax: int = 250_000) -> sf.NumberPacketData:
    return sf.build_number_packet_data(sf.KernelParameters(a=a, beta=beta, conductor=1), nmax=nmax)


def test_signed_moments_match_finite_difference() -> None:
    data = small_data(nmax=350_000)
    for k in range(6):
        observed = data.signed_transfer(k, 0.0).real
        expected = float(sf.exact_signed_moment(k, dps=90))
        assert abs(observed - expected) < 2e-6


def test_positive_kernel_matches_zeta_ratio_difference() -> None:
    data = small_data(nmax=350_000)
    for depth in range(8):
        observed = data.positive_kernel(depth, 0.6)
        expected = sf.exact_positive_kernel(depth, 0.6, dps=90)
        assert abs(observed - expected) < 2e-9


def test_depth_time_kernel_is_positive_semidefinite() -> None:
    data = small_data(nmax=200_000)
    points = [(100, 0.0), (300, 0.8), (1000, -1.2), (4000, 2.0)]
    gram = np.empty((len(points), len(points)), dtype=np.complex128)
    for i, (k, t) in enumerate(points):
        for j, (ell, s) in enumerate(points):
            gram[i, j] = data.positive_kernel(k + ell, t - s)
    assert np.max(np.abs(gram - gram.conjugate().T)) < 1e-12
    assert np.min(np.linalg.eigvalsh(gram)) > -1e-11


def test_gamma_dephasing_value_at_zero() -> None:
    value = sf.gamma_dephasing(1.5, 2.0, np.array([0.0]))[0]
    assert abs(value - 1) < 1e-15


def test_principal_modulus_identity() -> None:
    tau = np.linspace(-8, 8, 81)
    observed = np.abs(sf.gamma_dephasing(1.5, 2.0, tau)) ** 2
    expected = sf.principal_modulus_squared(tau)
    assert np.max(np.abs(observed - expected)) < 2e-13


def test_gamma_dephasing_asymptotic() -> None:
    data = small_data(nmax=350_000)
    depth = 40_000
    for tau in (0.5, 1.0, 2.0):
        observed = depth ** (1j * tau / 2) * data.positive_kernel(depth, tau) / data.positive_kernel(depth, 0)
        expected = complex(mp.gamma(mp.mpf('1.5') + 0.5j * tau) / mp.gamma(mp.mpf('1.5')))
        assert abs(observed - expected) < 0.01


def test_depth_overlap_limit_formula() -> None:
    alpha = 1.5
    observed = sf.depth_overlap_limit(alpha, 4.0, 1.0)
    expected = 0.8**alpha
    assert abs(observed - expected) < 1e-15


def test_depth_overlap_convergence() -> None:
    data = small_data(nmax=350_000)
    k = 40_000
    ell = 10_000
    observed = data.positive_kernel(k + ell, 0).real / math.sqrt(
        data.positive_kernel(2 * k, 0).real * data.positive_kernel(2 * ell, 0).real
    )
    expected = sf.depth_overlap_limit(1.5, k, ell)
    assert abs(observed - expected) < 0.02


def test_log_frequency_cumulants() -> None:
    values = sf.log_frequency_cumulants(1.5, 2.0, 3)
    assert abs(values[0] + float(mp.digamma(mp.mpf('1.5'))) / 2) < 1e-13
    assert values[1] > 0


def test_signed_resolvent_functional_equation() -> None:
    data = small_data(a=2.0, beta=2.0, nmax=350_000)
    shifted = small_data(a=4.0, beta=2.0, nmax=350_000)
    for z in (-0.7 + 0.2j, 0.2 + 0.3j, 0.6 - 0.2j):
        residual = sf.signed_resolvent_functional_residual(data, shifted, z)
        assert abs(residual) < 2e-9


def test_pade_exact_moment_contract() -> None:
    moments = np.array([complex(sf.exact_signed_moment(k)) for k in range(12)])
    numerator, denominator = sf.pade_from_moments(moments, 4)
    reconstructed = sf.pade_series_coefficients(numerator, denominator, 8)
    assert np.max(np.abs(reconstructed - moments[:8])) < 2e-11


def test_signed_one_node_is_outside_positive_support() -> None:
    c0 = complex(sf.exact_signed_moment(0))
    c1 = complex(sf.exact_signed_moment(1))
    node = c1 / c0
    assert node.real < 0
    assert abs(node.imag) < 1e-14


def test_positive_pade_nodes_lie_in_unit_interval() -> None:
    data = small_data(nmax=350_000)
    moments = np.array([data.positive_companion_moment(k) for k in range(12)], dtype=np.complex128)
    nodes, weights = sf.pade_packet_nodes_weights(moments, 4)
    assert np.max(np.abs(nodes.imag)) < 1e-7
    assert np.all(nodes.real >= -1e-8)
    assert np.all(nodes.real < 1 + 1e-8)
    assert np.max(np.abs(weights.imag)) < 1e-6


def test_borel_riesz_bridge() -> None:
    data = small_data(nmax=150_000)
    for x in (0.5, 2.0, 7.0):
        left = sf.borel_transfer(data, x)
        right = math.exp(x) * sf.riesz_companion(data, x) / x
        assert abs(left - right) < 2e-10


def test_character_packet_matrix() -> None:
    data = small_data(nmax=250_000)
    chars = sf.characters_mod_five(data.n.astype(np.int64))
    depth_small = 100
    depth_large = 10000
    values = []
    for depth in (depth_small, depth_large):
        numerator = sf.character_cross_kernel(data, chars[0], chars[1], depth)
        diagonal0 = sf.character_cross_kernel(data, chars[0], chars[0], depth)
        diagonal1 = sf.character_cross_kernel(data, chars[1], chars[1], depth)
        values.append(abs(numerator) / math.sqrt(abs(diagonal0 * diagonal1)))
    assert values[1] < values[0]


def test_hankel_determinant_contrast() -> None:
    signed = [complex(sf.exact_signed_moment(k)) for k in range(8)]
    assert sf.hankel_determinant(signed, 1).real > 0
    assert sf.hankel_determinant(signed, 2).real < 0


def test_result_ledger() -> None:
    result = json.loads((ROOT / "results" / "results.json").read_text())
    assert result["passed"] == result["checks"] == 18
    assert result["figure_pairs"] == 28


def test_required_figure_pairs_exist() -> None:
    pdfs = sorted((ROOT / "figures").glob("*.pdf"))
    pngs = sorted((ROOT / "figures").glob("*.png"))
    assert len(pdfs) == len(pngs) == 28
    assert {p.stem for p in pdfs} == {p.stem for p in pngs}
