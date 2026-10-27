from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
from scipy.integrate import quad
from scipy.special import polygamma

import projector_generated_special_functions_v as sf


def test_log_gamma_window_is_normalized() -> None:
    value = quad(lambda y: float(sf.log_gamma_density(1.5, y)), -40, 12, epsabs=1e-12)[0]
    assert abs(value - 1.0) < 1e-10


def test_log_gamma_moments() -> None:
    mean = quad(lambda y: y * float(sf.log_gamma_density(1.5, y)), -40, 12, epsabs=1e-11)[0]
    second = quad(lambda y: y * y * float(sf.log_gamma_density(1.5, y)), -40, 12, epsabs=1e-11)[0]
    assert abs(mean - sf.digamma(1.5)) < 1e-9
    assert abs(second - mean * mean - polygamma(1, 1.5)) < 1e-8


def test_ambiguity_closed_form() -> None:
    numeric = sf.centered_ambiguity_numeric(1.5, 1.1, -0.7)
    exact = complex(sf.gamma_sech_kernel(1.5, 1.1, -0.7))
    assert abs(numeric - exact) < 1e-10


def test_ambiguity_shift_law() -> None:
    h, eta, alpha = 0.8, 0.6, 1.5
    left = complex(sf.gamma_sech_kernel(alpha + 1.0, h, eta))
    right = ((alpha + 1j * eta) / alpha) / math.cosh(h / 2.0) * complex(sf.gamma_sech_kernel(alpha, h, eta))
    assert abs(left - right) < 1e-12


def test_phase_space_nonvanishing() -> None:
    values = sf.gamma_sech_kernel(1.5, np.linspace(-5, 5, 31)[:, None], np.linspace(-6, 6, 41)[None, :])
    assert np.min(np.abs(values)) > 0.0


def test_meixner_density_normalization() -> None:
    value = quad(lambda w: float(sf.meixner_density(1.5, w)), -24, 24, epsabs=1e-11)[0]
    assert abs(value - 1.0) < 1e-10


def test_meixner_characteristic_function() -> None:
    h = 0.9
    real = quad(lambda w: float(sf.meixner_density(1.5, w) * np.cos(w * h)), -24, 24, epsabs=1e-10)[0]
    assert abs(real - math.cosh(h / 2.0) ** (-1.5)) < 2e-9


def test_laguerre_meixner_fourier_pair() -> None:
    numeric = sf.laguerre_packet_fourier_numeric(1.5, 3, 0.65)
    exact = complex(sf.laguerre_packet_fourier(1.5, 3, 0.65))
    assert abs(numeric - exact) < 1e-9


def test_laguerre_orthogonality() -> None:
    y = np.linspace(-18, 8, 70001)
    f0 = sf.laguerre_packet(1.5, 0, y)
    f3 = sf.laguerre_packet(1.5, 3, y)
    assert abs(np.trapezoid(f0 * f3, y)) < 1e-8
    assert abs(np.trapezoid(f3 * f3, y) - 1.0) < 1e-8


def test_meixner_orthogonality() -> None:
    w = np.linspace(-20, 20, 50001)
    rho = sf.meixner_density(1.5, w)
    p1 = sf.meixner_pollaczek_orthonormal(1.5, 1, w)
    p4 = sf.meixner_pollaczek_orthonormal(1.5, 4, w)
    assert abs(np.trapezoid(rho * p1 * p4, w)) < 1e-8
    assert abs(np.trapezoid(rho * p4 * p4, w) - 1.0) < 1e-8


def test_su11_commutators() -> None:
    k0, kp, km = sf.su11_matrices(1.5, 16)
    interior = slice(0, 13)
    assert np.max(np.abs((k0 @ kp - kp @ k0 - kp)[interior, interior])) < 1e-12
    assert np.max(np.abs((km @ kp - kp @ km - 2 * k0)[interior, interior])) < 1e-12


def test_su11_casimir() -> None:
    alpha = 1.5
    k0, kp, km = sf.su11_matrices(alpha, 16)
    casimir = k0 @ k0 - 0.5 * (kp @ km + km @ kp)
    target = alpha / 2.0 * (alpha / 2.0 - 1.0)
    assert np.max(np.abs(casimir[:13, :13] - target * np.eye(13))) < 1e-12


def test_jacobi_relation() -> None:
    k0, kp, km = sf.su11_matrices(1.5, 12)
    assert np.allclose(sf.laguerre_jacobi(1.5, 12), 2 * k0 - kp - km)
    assert np.allclose(sf.meixner_jacobi(1.5, 12), 0.5 * (kp + km))


def test_uncertainty_identity() -> None:
    data = sf.uncertainty_data(1.5)
    assert abs(data["var_p"] - 1.5 / 4.0) < 1e-15
    assert abs(data["var_y"] - polygamma(1, 1.5)) < 1e-15
    assert data["product"] > 0.5


def test_fractional_depth_binomial_identity() -> None:
    direct = sf.fractional_mobius_transfer(2.5, nmax=3_000_000)
    series = float(sf.fractional_binomial_transfer(2.5, terms=5000))
    assert abs(direct - series) < 2e-8


def test_arithmetic_kernel_is_hermitian() -> None:
    kernel = sf.build_arithmetic_kernel(nmax=180_000)
    left = kernel.kernel(300.0, 900.0, 1.7)
    right = kernel.kernel(900.0, 300.0, -1.7)
    assert abs(left - np.conj(right)) < 1e-14


def test_arithmetic_kernel_converges_to_universal_limit() -> None:
    kernel = sf.build_arithmetic_kernel(nmax=600_000)
    value = kernel.normalized_centered(12000.0, 48000.0, 2.4)
    limit = sf.universal_arithmetic_limit(kernel.alpha, kernel.beta, 12000.0, 48000.0, 2.4)
    assert abs(value - limit) < 4e-3


def test_result_ledger() -> None:
    data = json.loads((ROOT / "results" / "results.json").read_text())
    assert data["built_in_checks"]["passed"] == data["built_in_checks"]["total"] == 19
    assert data["figure_pairs"] == 26


def test_every_figure_has_both_formats() -> None:
    pdfs = sorted((ROOT / "figures").glob("*.pdf"))
    pngs = sorted((ROOT / "figures").glob("*.png"))
    assert len(pdfs) == len(pngs) == 26
    assert [p.stem for p in pdfs] == [p.stem for p in pngs]
