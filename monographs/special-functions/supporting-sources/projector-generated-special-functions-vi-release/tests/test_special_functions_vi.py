from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

import numpy as np
from scipy.integrate import quad
from scipy.signal import fftconvolve
from scipy.special import ndtr, polygamma

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "pgsf6",
    ROOT / "projector_generated_special_functions_vi.py",
)
assert SPEC is not None and SPEC.loader is not None
M = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = M
SPEC.loader.exec_module(M)


def test_log_gamma_normalization() -> None:
    value = quad(lambda y: float(M.log_gamma_window(1.9, y) ** 2), -30, 10)[0]
    assert abs(value - 1.0) < 2e-11


def test_cross_shape_closed_form() -> None:
    direct = M.cross_gamma_numeric(1.2, 2.8, 0.6, -0.9)
    closed = complex(M.cross_gamma_sech(1.2, 2.8, 0.6, -0.9))
    assert abs(direct - closed) < 4e-10


def test_shape_affinity() -> None:
    assert abs(M.shape_affinity(2.3, 2.3) - 1.0) < 2e-14
    assert 0.0 < M.shape_affinity(0.8, 4.5) < 1.0


def test_beta_logit_normalization() -> None:
    value = quad(lambda h: float(M.beta_logit_density(1.4, 3.2, h)), -30, 30)[0]
    assert abs(value - 1.0) < 3e-10


def test_meixner_normalization_and_variance() -> None:
    shape = 3.2
    norm = quad(lambda x: float(M.meixner_density(shape, x)), -30, 30)[0]
    variance = quad(lambda x: float(x * x * M.meixner_density(shape, x)), -30, 30)[0]
    assert abs(norm - 1.0) < 3e-10
    assert abs(variance - shape / 4.0) < 3e-9


def test_cross_spectrogram_factorization() -> None:
    h = np.linspace(-2.5, 2.5, 31)
    eta = np.linspace(-2.5, 2.5, 31)
    direct = M.cross_spectrogram_density(1.1, 2.4, h, eta)
    factor = M.beta_logit_density(1.1, 2.4, h)[:, None] * M.meixner_density(3.5, eta)[None, :]
    assert np.max(np.abs(direct - factor)) < 3e-13


def test_convolution_semigroup() -> None:
    grid = np.linspace(-14, 14, 5601)
    dx = grid[1] - grid[0]
    conv = fftconvolve(M.meixner_density(0.9, grid), M.meixner_density(1.6, grid), mode="same") * dx
    target = M.meixner_density(2.5, grid)
    mask = np.abs(grid) < 5
    assert np.max(np.abs(conv[mask] - target[mask])) < 4e-5


def test_shape_recurrence() -> None:
    x = np.linspace(-4, 4, 101)
    assert np.max(np.abs(M.meixner_density(4.7, x) - M.density_shape_recurrence(2.7, x))) < 3e-13


def test_levy_symbol() -> None:
    for xi in (0.3, 1.0, 2.2):
        exact = -math.log(math.cosh(xi / 2.0))
        assert abs(M.levy_symbol_numeric(xi) - exact) < 4e-11


def test_bernoulli_cumulants() -> None:
    shape = 3.0
    assert abs(M.bernoulli_even_cumulant(shape, 2) - shape / 4.0) < 1e-12
    assert abs(M.bernoulli_even_cumulant(shape, 4) - shape / 8.0) < 1e-11
    assert abs(M.bernoulli_even_cumulant(shape, 6) - shape / 4.0) < 1e-10
    assert M.bernoulli_even_cumulant(shape, 3) == 0.0


def test_beta_binomial_partition() -> None:
    coefficients = M.beta_binomial_coefficients(15, 1.3, 4.2)
    assert abs(float(np.sum(coefficients**2)) - 1.0) < 4e-13


def test_two_child_addition_theorem() -> None:
    x = np.linspace(-2.0, 2.0, 31)
    y = np.full_like(x, -0.45)
    left = M.mp_orthonormal(4.8, 7, x + y)
    right = M.mp_addition_rhs(1.6, 3.2, 7, x, y)
    assert np.max(np.abs(left - right)) < 8e-12


def test_multinomial_packet_theorem() -> None:
    shapes = (0.8, 1.4, 2.1)
    points = (0.2, -0.7, 1.15)
    left = float(M.mp_orthonormal(sum(shapes), 6, sum(points)))
    right = M.mp_multinomial_rhs(shapes, 6, points)
    assert abs(left - right) < 1e-11


def test_dirichlet_multinomial_energy() -> None:
    shapes = (1.2, 2.0, 2.7, 0.9)
    value = sum(
        M.dirichlet_multinomial_coefficient(comp, shapes) ** 2
        for comp in M.compositions(8, len(shapes))
    )
    assert abs(value - 1.0) < 8e-13


def test_transfer_integral_and_singular_value() -> None:
    shape = 1.7
    increment = 1.2
    degree = 4
    sigma = M.transfer_singular_value(shape, increment, degree)
    for x in (-1.1, 0.0, 1.4):
        direct = M.transfer_integral(shape, increment, degree, x)
        expected = sigma * float(M.mp_orthonormal(shape, degree, x))
        assert abs(direct - expected) < 8e-8


def test_transfer_cocycle() -> None:
    left = M.transfer_singular_value(1.4, 0.7, 6) * M.transfer_singular_value(2.1, 1.3, 6)
    right = M.transfer_singular_value(1.4, 2.0, 6)
    assert abs(left - right) < 4e-14


def test_coherent_overlap() -> None:
    direct = M.coherent_overlap_numeric(1.5, 2.2, -0.4, 0.8, 0.65, -0.35)
    closed = M.coherent_overlap(1.5, 2.2, -0.4, 0.8, 0.65, -0.35)
    assert abs(direct - closed) < 5e-10


def test_berezin_kernel_normalization_and_variance() -> None:
    alpha = 2.1
    pn = quad(lambda h: float(M.berezin_position_density(alpha, h)), -30, 30)[0]
    qn = quad(lambda w: float(M.berezin_frequency_density(alpha, w)), -30, 30)[0]
    pv = quad(lambda h: float(h * h * M.berezin_position_density(alpha, h)), -30, 30)[0]
    qv = quad(lambda w: float(w * w * M.berezin_frequency_density(alpha, w)), -30, 30)[0]
    assert abs(pn - 1.0) < 3e-10
    assert abs(qn - 1.0) < 3e-10
    assert abs(pv - 2.0 * float(polygamma(1, alpha))) < 4e-9
    assert abs(qv - alpha / 2.0) < 4e-9


def test_berezin_multiplier_is_strictly_positive() -> None:
    xi = np.linspace(-7, 7, 61)
    x = np.linspace(-7, 7, 61)
    multiplier = M.berezin_multiplier(1.7, xi, x)
    assert np.all(multiplier > 0)
    assert np.max(multiplier) <= 1.0 + 2e-14


def test_gaussian_scaling() -> None:
    z = np.linspace(-7, 7, 5001)
    dz = z[1] - z[0]
    target = ndtr(z)
    for density in (
        M.rescaled_position_density(100.0, z),
        M.rescaled_frequency_density(100.0, z),
    ):
        cdf = np.cumsum(density) * dz
        cdf /= cdf[-1]
        assert np.max(np.abs(cdf - target)) < 0.02


def test_generated_figures_and_manuscript_references() -> None:
    pdfs = sorted((ROOT / "figures").glob("*.pdf"))
    pngs = sorted((ROOT / "figures").glob("*.png"))
    assert len(pdfs) == len(pngs) == 28
    manuscript = (ROOT / "Projector_Generated_Special_Functions_VI.tex").read_text(encoding="utf-8")
    for pdf in pdfs:
        assert pdf.stem in manuscript
