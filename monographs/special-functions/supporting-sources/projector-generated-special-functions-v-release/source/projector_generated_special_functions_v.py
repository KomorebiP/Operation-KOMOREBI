from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterable

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle
import mpmath as mp
import numpy as np
from scipy.integrate import quad
from scipy.special import digamma, eval_genlaguerre, gamma, gammaln, loggamma, polygamma

mp.mp.dps = 80

ROOT = Path(__file__).resolve().parent
FIGURES = ROOT / "figures"
RESULTS = ROOT / "results"
TABLES = ROOT / "tables"
GENERATED = ROOT / "generated_tables"
for directory in (FIGURES, RESULTS, TABLES, GENERATED):
    directory.mkdir(parents=True, exist_ok=True)

INK = "#17202A"
BLUE = "#2E86AB"
TEAL = "#2A9D8F"
ORANGE = "#F4A261"
MAGENTA = "#A23E8C"
RED = "#E76F51"
YELLOW = "#E9C46A"
PURPLE = "#6C5CE7"
MUTED = "#5D6D7E"
PAPER = "#FAFAF7"
GRID = "#D5D8DC"
WHITE = "#FFFFFF"
COLORS = [BLUE, TEAL, ORANGE, MAGENTA, RED, YELLOW, PURPLE]

plt.rcParams.update(
    {
        "figure.facecolor": PAPER,
        "axes.facecolor": PAPER,
        "axes.edgecolor": INK,
        "axes.labelcolor": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "text.color": INK,
        "font.size": 10.5,
        "axes.titlesize": 12.2,
        "axes.titleweight": "bold",
        "legend.frameon": False,
        "savefig.bbox": "tight",
        "savefig.facecolor": PAPER,
    }
)


def save_figure(fig: plt.Figure, stem: str) -> None:
    fig.savefig(FIGURES / f"{stem}.pdf")
    fig.savefig(FIGURES / f"{stem}.png", dpi=220)
    plt.close(fig)


def diagram_axes(figsize: tuple[float, float] = (12.6, 6.1)) -> tuple[plt.Figure, plt.Axes]:
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    return fig, ax


def box(
    ax: plt.Axes,
    xy: tuple[float, float],
    width: float,
    height: float,
    text: str,
    face: str = WHITE,
    edge: str = INK,
    fontsize: float = 10.8,
) -> None:
    patch = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle="round,pad=.012,rounding_size=.018",
        facecolor=face,
        edgecolor=edge,
        linewidth=1.7,
    )
    ax.add_patch(patch)
    ax.text(xy[0] + width / 2, xy[1] + height / 2, text, ha="center", va="center", fontsize=fontsize)


def arrow(
    ax: plt.Axes,
    start: tuple[float, float],
    end: tuple[float, float],
    color: str = INK,
    text: str | None = None,
    text_offset: tuple[float, float] = (0.0, 0.03),
) -> None:
    patch = FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=13, linewidth=1.6, color=color)
    ax.add_patch(patch)
    if text:
        ax.text(
            (start[0] + end[0]) / 2 + text_offset[0],
            (start[1] + end[1]) / 2 + text_offset[1],
            text,
            ha="center",
            va="center",
            fontsize=9.8,
            color=color,
        )


# ---------------------------------------------------------------------------
# Log-Gamma packet window and generated special functions
# ---------------------------------------------------------------------------


def log_gamma_window(alpha: float, y: np.ndarray | float) -> np.ndarray:
    values = np.asarray(y, dtype=float)
    return np.exp(0.5 * alpha * values - 0.5 * np.exp(values) - 0.5 * gammaln(alpha))


def log_gamma_density(alpha: float, y: np.ndarray | float) -> np.ndarray:
    values = np.asarray(y, dtype=float)
    return np.exp(alpha * values - np.exp(values) - gammaln(alpha))


def log_gamma_fourier(alpha: float, omega: np.ndarray | float) -> np.ndarray:
    values = np.asarray(omega, dtype=float)
    z = alpha / 2.0 - 1j * values
    log_value = (alpha / 2.0 - 1j * values) * math.log(2.0) + loggamma(z)
    log_value -= 0.5 * (math.log(2.0 * math.pi) + gammaln(alpha))
    return np.exp(log_value)


def meixner_density(alpha: float, omega: np.ndarray | float) -> np.ndarray:
    values = np.asarray(omega, dtype=float)
    return np.abs(log_gamma_fourier(alpha, values)) ** 2


def gamma_sech_kernel(alpha: float, h: np.ndarray | float, eta: np.ndarray | float) -> np.ndarray:
    h_values, eta_values = np.broadcast_arrays(np.asarray(h, dtype=float), np.asarray(eta, dtype=float))
    z = alpha + 1j * eta_values
    log_sech = -np.log(np.cosh(h_values / 2.0))
    return np.exp(loggamma(z) - gammaln(alpha) + z * log_sech)


def centered_ambiguity_numeric(alpha: float, h: float, eta: float) -> complex:
    integrand = lambda y: (
        log_gamma_window(alpha, y + h / 2)
        * log_gamma_window(alpha, y - h / 2)
        * np.exp(1j * eta * y)
    )
    real = quad(lambda yy: float(np.real(integrand(yy))), -20, 8, epsabs=2e-12, limit=300)[0]
    imag = quad(lambda yy: float(np.imag(integrand(yy))), -20, 8, epsabs=2e-12, limit=300)[0]
    return complex(real, imag)


def wigner_log_gamma(alpha: float, y: np.ndarray, omega: np.ndarray) -> np.ndarray:
    yy, ww = np.meshgrid(np.asarray(y, dtype=float), np.asarray(omega, dtype=float), indexing="ij")
    out = np.empty_like(yy)
    prefactor = 2.0 / (math.pi * float(mp.gamma(alpha)))
    for i in range(yy.shape[0]):
        x = float(np.exp(yy[i, 0]))
        for j in range(yy.shape[1]):
            out[i, j] = prefactor * math.exp(alpha * yy[i, j]) * float(mp.re(mp.besselk(2j * ww[i, j], x)))
    return out


def uncertainty_data(alpha: float) -> dict[str, float]:
    var_y = float(polygamma(1, alpha))
    var_p = alpha / 4.0
    return {
        "mean_y": float(digamma(alpha)),
        "var_y": var_y,
        "var_p": var_p,
        "product": math.sqrt(var_y * var_p),
        "qfi_u": alpha,
        "qfi_eta": 4.0 * var_y,
        "berry_curvature": 1.0,
    }


def meixner_pollaczek_orthonormal(alpha: float, degree: int, omega: np.ndarray | float) -> np.ndarray:
    x = np.asarray(omega, dtype=float)
    if degree == 0:
        return np.ones_like(x)
    p_prev = np.ones_like(x)
    p_curr = 2.0 * x / math.sqrt(alpha)
    if degree == 1:
        return p_curr
    for n in range(1, degree):
        b_np1 = 0.5 * math.sqrt((n + 1) * (n + alpha))
        b_n = 0.5 * math.sqrt(n * (n + alpha - 1))
        p_next = (x * p_curr - b_n * p_prev) / b_np1
        p_prev, p_curr = p_curr, p_next
    return p_curr


def laguerre_packet(alpha: float, degree: int, y: np.ndarray | float) -> np.ndarray:
    values = np.asarray(y, dtype=float)
    normalization = math.exp(0.5 * (gammaln(degree + 1) - gammaln(degree + alpha)))
    return (
        normalization
        * np.exp(0.5 * alpha * values - 0.5 * np.exp(values))
        * eval_genlaguerre(degree, alpha - 1.0, np.exp(values))
    )


def laguerre_packet_fourier(alpha: float, degree: int, omega: np.ndarray | float) -> np.ndarray:
    values = np.asarray(omega, dtype=float)
    return (
        (1j ** degree)
        * log_gamma_fourier(alpha, values)
        * meixner_pollaczek_orthonormal(alpha, degree, values)
    )


def laguerre_packet_fourier_numeric(alpha: float, degree: int, omega: float) -> complex:
    integrand = lambda y: laguerre_packet(alpha, degree, y) * np.exp(-1j * omega * y) / math.sqrt(2 * math.pi)
    real = quad(lambda yy: float(np.real(integrand(yy))), -35, 10, epsabs=2e-12, limit=450)[0]
    imag = quad(lambda yy: float(np.imag(integrand(yy))), -35, 10, epsabs=2e-12, limit=450)[0]
    return complex(real, imag)


# ---------------------------------------------------------------------------
# Ladder operators and exact matrix systems
# ---------------------------------------------------------------------------


def su11_matrices(alpha: float, dimension: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    k0 = np.diag(np.arange(dimension, dtype=float) + alpha / 2.0)
    kp = np.zeros((dimension, dimension), dtype=float)
    for n in range(dimension - 1):
        kp[n + 1, n] = math.sqrt((n + 1) * (n + alpha))
    km = kp.T
    return k0, kp, km


def laguerre_jacobi(alpha: float, dimension: int) -> np.ndarray:
    k0, kp, km = su11_matrices(alpha, dimension)
    return 2.0 * k0 - kp - km


def meixner_jacobi(alpha: float, dimension: int) -> np.ndarray:
    _, kp, km = su11_matrices(alpha, dimension)
    return 0.5 * (kp + km)


# ---------------------------------------------------------------------------
# Arithmetic kernel and fractional-depth extension
# ---------------------------------------------------------------------------


@lru_cache(maxsize=12)
def mobius_sieve(nmax: int) -> np.ndarray:
    mu = np.zeros(nmax + 1, dtype=np.int8)
    mu[1] = 1
    primes: list[int] = []
    composite = np.zeros(nmax + 1, dtype=bool)
    for i in range(2, nmax + 1):
        if not composite[i]:
            primes.append(i)
            mu[i] = -1
        for p in primes:
            value = i * p
            if value > nmax:
                break
            composite[value] = True
            if i % p == 0:
                mu[value] = 0
                break
            mu[value] = -mu[i]
    return mu


@dataclass
class ArithmeticKernel:
    a: float
    beta: float
    n: np.ndarray
    weight: np.ndarray
    log_y: np.ndarray

    @property
    def alpha(self) -> float:
        return (2 * self.a - 1) / self.beta

    def kernel(self, k: float, ell: float, tau: float = 0.0) -> complex:
        depth = k + ell
        factor = np.exp(depth * self.log_y)
        phase = np.exp(-1j * tau * np.log(self.n))
        return complex(np.sum(self.weight * factor * phase))

    def normalized_centered(self, k: float, ell: float, tau: float) -> complex:
        eta = tau / self.beta
        numerator = self.kernel(k, ell, tau)
        denominator = math.sqrt(self.kernel(k, k, 0.0).real * self.kernel(ell, ell, 0.0).real)
        carrier = np.exp(1j * eta * math.log(2.0 * math.sqrt(k * ell)))
        return complex(carrier * numerator / denominator)


def build_arithmetic_kernel(a: float = 2.0, beta: float = 2.0, nmax: int = 600_000) -> ArithmeticKernel:
    mu = mobius_sieve(nmax)
    integers = np.arange(1, nmax + 1, dtype=np.int64)
    mask = mu[1:] != 0
    n = integers[mask].astype(float)
    y = 1.0 - n ** (-beta)
    log_y = np.full_like(y, -np.inf)
    positive = y > 0
    log_y[positive] = np.log(y[positive])
    weight = n ** (-2 * a)
    return ArithmeticKernel(a=a, beta=beta, n=n, weight=weight, log_y=log_y)


def universal_arithmetic_limit(alpha: float, beta: float, k: float, ell: float, tau: float) -> complex:
    h = math.log(k / ell)
    eta = tau / beta
    return complex(gamma_sech_kernel(alpha, h, eta))


def fractional_mobius_transfer(r: float, a: float = 2.0, beta: float = 2.0, nmax: int = 500_000) -> float:
    mu = mobius_sieve(nmax)
    integers = np.arange(2, nmax + 1, dtype=float)
    muv = mu[2:].astype(float)
    return float(np.sum(muv * integers ** (-a) * (1.0 - integers ** (-beta)) ** r))


def fractional_binomial_transfer(r: float, a: float = 2.0, beta: float = 2.0, terms: int = 120) -> mp.mpf:
    mp.mp.dps = 60
    total = mp.mpf("0")
    for j in range(terms):
        total += (-1) ** j * mp.binomial(r, j) / mp.zeta(a + beta * j)
    return total


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------


def perform_checks() -> tuple[list[dict[str, object]], dict[str, object]]:
    checks: list[dict[str, object]] = []

    def record(name: str, passed: bool, detail: str) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    # Normalization and moment identities
    for alpha in (0.75, 1.5, 3.0, 8.0):
        integral = quad(lambda y: float(log_gamma_density(alpha, y)), -40, 12, epsabs=2e-12, limit=400)[0]
        record(f"window normalization alpha={alpha}", abs(integral - 1.0) < 2e-10, f"integral={integral:.13g}")

    # Exact ambiguity formula
    ambiguity_errors = []
    for h, eta in ((0.0, 0.7), (0.8, 0.5), (1.4, -1.1), (-0.6, 1.7)):
        numeric = centered_ambiguity_numeric(1.5, h, eta)
        exact = complex(gamma_sech_kernel(1.5, h, eta))
        ambiguity_errors.append(abs(numeric - exact))
    record("Gamma-sech ambiguity", max(ambiguity_errors) < 3e-9, f"max_error={max(ambiguity_errors):.3e}")

    # Fourier transform formula
    fourier_errors = []
    for degree in range(5):
        for omega in (-1.2, -0.3, 0.8):
            numeric = laguerre_packet_fourier_numeric(1.5, degree, omega)
            exact = complex(laguerre_packet_fourier(1.5, degree, omega))
            fourier_errors.append(abs(numeric - exact))
    record("Laguerre-Meixner Fourier duality", max(fourier_errors) < 2e-8, f"max_error={max(fourier_errors):.3e}")

    # Spectral density normalization and moments
    spectral_integral = quad(lambda w: float(meixner_density(1.5, w)), -20, 20, epsabs=1e-10, limit=300)[0]
    record("Meixner spectral density normalization", abs(spectral_integral - 1.0) < 2e-9, f"integral={spectral_integral:.13g}")

    # Uncertainty formulas
    for alpha in (0.75, 1.5, 3.0, 10.0):
        data = uncertainty_data(alpha)
        record(
            f"strict uncertainty alpha={alpha}",
            data["product"] > 0.5 and data["product"] < 0.8,
            f"product={data['product']:.12g}",
        )

    # Meixner-Pollaczek orthogonality
    nodes = np.linspace(-18, 18, 40001)
    rho = meixner_density(1.5, nodes)
    polys = np.vstack([meixner_pollaczek_orthonormal(1.5, n, nodes) for n in range(5)])
    gram = np.array([[np.trapezoid(rho * polys[i] * polys[j], nodes) for j in range(5)] for i in range(5)])
    mp_error = float(np.max(np.abs(gram - np.eye(5))))
    record("Meixner-Pollaczek orthogonality", mp_error < 2e-7, f"max_error={mp_error:.3e}")

    # Laguerre packet orthogonality
    y_grid = np.linspace(-15, 7, 60001)
    packets = np.vstack([laguerre_packet(1.5, n, y_grid) for n in range(5)])
    lag_gram = np.array([[np.trapezoid(packets[i] * packets[j], y_grid) for j in range(5)] for i in range(5)])
    lag_error = float(np.max(np.abs(lag_gram - np.eye(5))))
    record("Laguerre packet orthogonality", lag_error < 2e-7, f"max_error={lag_error:.3e}")

    # SU(1,1) commutators on the non-boundary block
    alpha = 1.5
    dim = 18
    k0, kp, km = su11_matrices(alpha, dim)
    interior = slice(0, dim - 2)
    c1 = (k0 @ kp - kp @ k0 - kp)[interior, interior]
    c2 = (k0 @ km - km @ k0 + km)[interior, interior]
    c3 = (km @ kp - kp @ km - 2 * k0)[interior, interior]
    comm_error = max(float(np.max(np.abs(c1))), float(np.max(np.abs(c2))), float(np.max(np.abs(c3))))
    record("su(1,1) commutators", comm_error < 2e-12, f"max_error={comm_error:.3e}")

    casimir = k0 @ k0 - 0.5 * (kp @ km + km @ kp)
    target = alpha / 2 * (alpha / 2 - 1)
    cas_error = float(np.max(np.abs(casimir[: dim - 2, : dim - 2] - target * np.eye(dim - 2))))
    record("su(1,1) Casimir", cas_error < 2e-12, f"max_error={cas_error:.3e}")

    # Poschl-Teller ODE
    h = np.linspace(-4, 4, 20001)
    eta = 0.7
    nu = 1.5 + 1j * eta
    f = gamma_sech_kernel(1.5, h, eta)
    dh = h[1] - h[0]
    fpp = (f[:-2] - 2 * f[1:-1] + f[2:]) / dh**2
    residual = -4 * fpp - nu * (nu + 1) / np.cosh(h[1:-1] / 2) ** 2 * f[1:-1] + nu**2 * f[1:-1]
    pt_error = float(np.max(np.abs(residual[10:-10])))
    record("Poschl-Teller equation", pt_error < 2e-6, f"max_error={pt_error:.3e}")

    # Arithmetic convergence to the universal kernel
    arithmetic = build_arithmetic_kernel(nmax=600_000)
    convergence_rows = []
    max_large_error = 0.0
    for scale in (400, 1200, 4000, 12000):
        k = float(scale)
        ell = float(4 * scale)
        tau = 2.4
        discrete = arithmetic.normalized_centered(k, ell, tau)
        universal = universal_arithmetic_limit(arithmetic.alpha, arithmetic.beta, k, ell, tau)
        error = abs(discrete - universal)
        max_large_error = error if scale == 12000 else max_large_error
        convergence_rows.append({"scale": scale, "error": error, "discrete_real": discrete.real, "discrete_imag": discrete.imag})
    record("arithmetic joint-kernel convergence", max_large_error < 7e-3, f"error_at_12000={max_large_error:.3e}")

    # Fractional-depth binomial formula
    frac_direct = fractional_mobius_transfer(2.5, nmax=5_000_000)
    frac_series = float(fractional_binomial_transfer(2.5, terms=5000))
    frac_error = abs(frac_direct - frac_series)
    record("fractional-depth binomial orbit", frac_error < 8e-9, f"error={frac_error:.3e}")

    # Zero-free real phase-space sample
    h_grid = np.linspace(-6, 6, 121)
    eta_grid = np.linspace(-8, 8, 121)
    hh, ee = np.meshgrid(h_grid, eta_grid, indexing="ij")
    values = gamma_sech_kernel(1.5, hh, ee)
    minimum = float(np.min(np.abs(values)))
    record("real phase-space nonvanishing sample", minimum > 0.0, f"minimum={minimum:.3e}")

    passed = sum(1 for check in checks if check["passed"])
    summary: dict[str, object] = {
        "built_in_checks": {"passed": passed, "total": len(checks)},
        "ambiguity_max_error": max(ambiguity_errors),
        "fourier_duality_max_error": max(fourier_errors),
        "meixner_gram_error": mp_error,
        "laguerre_gram_error": lag_error,
        "su11_commutator_error": comm_error,
        "su11_casimir_error": cas_error,
        "poschl_teller_error": pt_error,
        "fractional_depth_error": frac_error,
        "phase_space_minimum_sample": minimum,
        "arithmetic_convergence": convergence_rows,
        "uncertainty_alpha_1_5": uncertainty_data(1.5),
    }
    return checks, summary


# ---------------------------------------------------------------------------
# Figure generation
# ---------------------------------------------------------------------------


def generate_figures(summary: dict[str, object]) -> None:
    # 01 pipeline
    fig, ax = diagram_axes()
    ax.text(0.5, 0.94, "From arithmetic depth packets to a universal phase-space function", ha="center", fontsize=19, weight="bold")
    items = [
        (0.03, "squarefree\ndepth-time kernel", BLUE),
        (0.22, "large-depth\nGamma scaling", TEAL),
        (0.41, "log-Gamma\npacket window", ORANGE),
        (0.60, "Gamma-sech\nambiguity kernel", MAGENTA),
        (0.79, "Laguerre and\nMeixner duality", PURPLE),
    ]
    for x0, text, color in items:
        box(ax, (x0, 0.56), 0.16, 0.18, text, face=color + "20", edge=color, fontsize=12)
    for left, right in zip(items[:-1], items[1:]):
        arrow(ax, (left[0] + 0.16, 0.65), (right[0], 0.65), color=INK)
    box(ax, (0.18, 0.18), 0.25, 0.15, "exact ambiguity\nPoschl-Teller equation", face=WHITE, edge=TEAL, fontsize=11.5)
    box(ax, (0.57, 0.18), 0.25, 0.15, "SU(1,1) ladder\nand quantum geometry", face=WHITE, edge=PURPLE, fontsize=11.5)
    arrow(ax, (0.49, 0.56), (0.305, 0.33), color=TEAL)
    arrow(ax, (0.68, 0.56), (0.695, 0.33), color=PURPLE)
    ax.text(0.5, 0.07, "The limiting packet is a concrete Gabor window rather than an abstract asymptotic profile.", ha="center", color=MUTED, fontsize=11.5)
    save_figure(fig, "01_theory_pipeline")

    # 02 window family
    y = np.linspace(-7, 4, 1800)
    fig, ax = plt.subplots(figsize=(12.6, 5.3))
    for alpha, color in zip((0.75, 1.5, 3.0, 8.0), COLORS):
        ax.plot(y, log_gamma_window(alpha, y), lw=2.1, color=color, label=rf"$\alpha={alpha}$")
    ax.set_xlabel("log coordinate $y$")
    ax.set_ylabel(r"$g_\alpha(y)$")
    ax.set_title("Normalized log-Gamma packet windows")
    ax.grid(alpha=0.18)
    ax.legend(ncol=4)
    save_figure(fig, "02_log_gamma_windows")

    # 03 position density
    fig, ax = plt.subplots(figsize=(12.6, 5.3))
    for alpha, color in zip((0.75, 1.5, 3.0, 8.0), COLORS):
        ax.plot(y, log_gamma_density(alpha, y), lw=2.1, color=color, label=rf"$\alpha={alpha}$")
    ax.set_xlabel(r"$y=\log u$")
    ax.set_ylabel("probability density")
    ax.set_title("The packet position law is log-Gamma")
    ax.grid(alpha=0.18)
    ax.legend(ncol=4)
    save_figure(fig, "03_log_gamma_density")

    # 04 spectral density
    omega = np.linspace(-8, 8, 2000)
    fig, ax = plt.subplots(figsize=(12.6, 5.3))
    for alpha, color in zip((0.75, 1.5, 3.0, 8.0), COLORS):
        ax.plot(omega, meixner_density(alpha, omega), lw=2.1, color=color, label=rf"$\alpha={alpha}$")
    ax.set_xlabel(r"Mellin frequency $\omega$")
    ax.set_ylabel(r"$|\widehat g_\alpha(\omega)|^2$")
    ax.set_title("The dual packet law is the symmetric Meixner density")
    ax.grid(alpha=0.18)
    ax.legend(ncol=4)
    save_figure(fig, "04_meixner_density")

    # 05 autocorrelation
    h = np.linspace(-7, 7, 1600)
    fig, ax = plt.subplots(figsize=(12.6, 5.2))
    for alpha, color in zip((0.75, 1.5, 3.0, 8.0), COLORS):
        ax.plot(h, 1 / np.cosh(h / 2) ** alpha, lw=2.1, color=color, label=rf"$\alpha={alpha}$")
    ax.set_xlabel("log-depth difference $h$")
    ax.set_ylabel("normalized overlap")
    ax.set_title(r"Exact depth overlap $\operatorname{sech}^{\alpha}(h/2)$")
    ax.grid(alpha=0.18)
    ax.legend(ncol=4)
    save_figure(fig, "05_depth_autocorrelation")

    # 06 ambiguity magnitude
    h_grid = np.linspace(-5, 5, 181)
    eta_grid = np.linspace(-7, 7, 181)
    hh, ee = np.meshgrid(h_grid, eta_grid, indexing="xy")
    amb = gamma_sech_kernel(1.5, hh, ee)
    fig, ax = plt.subplots(figsize=(11.7, 6.2))
    image = ax.imshow(np.abs(amb), extent=[h_grid.min(), h_grid.max(), eta_grid.min(), eta_grid.max()], origin="lower", aspect="auto", cmap="viridis")
    ax.set_xlabel("log-depth shift $h$")
    ax.set_ylabel(r"Mellin-frequency shift $\eta$")
    ax.set_title(r"Magnitude of the Gamma-sech ambiguity function, $\alpha=3/2$")
    fig.colorbar(image, ax=ax, fraction=0.035, pad=0.025, label="magnitude")
    save_figure(fig, "06_ambiguity_magnitude")

    # 07 ambiguity phase
    fig, ax = plt.subplots(figsize=(11.7, 6.2))
    image = ax.imshow(np.angle(amb), extent=[h_grid.min(), h_grid.max(), eta_grid.min(), eta_grid.max()], origin="lower", aspect="auto", cmap="twilight", vmin=-np.pi, vmax=np.pi)
    ax.set_xlabel("log-depth shift $h$")
    ax.set_ylabel(r"Mellin-frequency shift $\eta$")
    ax.set_title("Phase of the zero-free Gamma-sech ambiguity function")
    fig.colorbar(image, ax=ax, fraction=0.035, pad=0.025, label="phase")
    save_figure(fig, "07_ambiguity_phase")

    # 08 slices
    fig, axes = plt.subplots(1, 2, figsize=(12.8, 4.8))
    for eta, color in zip((0.0, 0.75, 1.5, 2.5), COLORS):
        axes[0].plot(h, np.abs(gamma_sech_kernel(1.5, h, eta)), lw=2, color=color, label=rf"$\eta={eta}$")
    axes[0].set_xlabel("$h$")
    axes[0].set_ylabel("magnitude")
    axes[0].set_title("Depth slices")
    axes[0].grid(alpha=0.18)
    axes[0].legend()
    eta_line = np.linspace(-8, 8, 1000)
    for hh0, color in zip((0.0, 0.8, 1.6, 2.4), COLORS):
        axes[1].plot(eta_line, np.abs(gamma_sech_kernel(1.5, hh0, eta_line)), lw=2, color=color, label=rf"$h={hh0}$")
    axes[1].set_xlabel(r"$\eta$")
    axes[1].set_ylabel("magnitude")
    axes[1].set_title("Frequency slices")
    axes[1].grid(alpha=0.18)
    axes[1].legend()
    fig.suptitle("The ambiguity magnitude factorizes into depth and frequency envelopes", fontsize=16, weight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.91])
    save_figure(fig, "08_ambiguity_slices")

    # 09 Poschl-Teller residual and potential
    h2 = np.linspace(-7, 7, 1600)
    eta0 = 0.8
    nu = 1.5 + 1j * eta0
    potential = -nu * (nu + 1) / np.cosh(h2 / 2) ** 2
    fig, axes = plt.subplots(1, 2, figsize=(12.8, 4.8))
    axes[0].plot(h2, potential.real, color=BLUE, lw=2, label="real")
    axes[0].plot(h2, potential.imag, color=MAGENTA, lw=2, label="imaginary")
    axes[0].set_title("Complex Poschl-Teller potential")
    axes[0].set_xlabel("$h$")
    axes[0].grid(alpha=0.18)
    axes[0].legend()
    f = gamma_sech_kernel(1.5, h2, eta0)
    axes[1].plot(h2, f.real, color=TEAL, lw=2, label="real")
    axes[1].plot(h2, f.imag, color=ORANGE, lw=2, label="imaginary")
    axes[1].set_title("Exact Gamma-sech eigenfunction")
    axes[1].set_xlabel("$h$")
    axes[1].grid(alpha=0.18)
    axes[1].legend()
    fig.suptitle("The generated ambiguity function solves a shape-invariant Schrodinger equation", fontsize=15.5, weight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.90])
    save_figure(fig, "09_poschl_teller")

    # 10 Wigner function
    y_w = np.linspace(-4.5, 3.0, 85)
    o_w = np.linspace(-5.5, 5.5, 95)
    wigner = wigner_log_gamma(1.5, y_w, o_w)
    fig, ax = plt.subplots(figsize=(11.7, 6.2))
    vmax = float(np.percentile(np.abs(wigner), 99.0))
    image = ax.imshow(wigner.T, extent=[y_w.min(), y_w.max(), o_w.min(), o_w.max()], origin="lower", aspect="auto", cmap="coolwarm", vmin=-vmax, vmax=vmax)
    ax.set_xlabel("log coordinate $y$")
    ax.set_ylabel(r"Mellin frequency $\omega$")
    ax.set_title(r"Wigner-Kontorovich-Lebedev packet, $\alpha=3/2$")
    fig.colorbar(image, ax=ax, fraction=0.035, pad=0.025, label="Wigner density")
    save_figure(fig, "10_wigner_kl")

    # 11 Wigner marginals
    fig, axes = plt.subplots(1, 2, figsize=(12.8, 4.8))
    axes[0].plot(y_w, np.trapezoid(wigner, o_w, axis=1), color=BLUE, lw=2.2, label="Wigner marginal")
    axes[0].plot(y_w, log_gamma_density(1.5, y_w), color=ORANGE, lw=1.5, ls="--", label="exact position law")
    axes[0].set_xlabel("$y$")
    axes[0].set_title("Position marginal")
    axes[0].grid(alpha=0.18)
    axes[0].legend()
    axes[1].plot(o_w, np.trapezoid(wigner, y_w, axis=0), color=TEAL, lw=2.2, label="Wigner marginal")
    axes[1].plot(o_w, meixner_density(1.5, o_w), color=MAGENTA, lw=1.5, ls="--", label="exact spectral law")
    axes[1].set_xlabel(r"$\omega$")
    axes[1].set_title("Frequency marginal")
    axes[1].grid(alpha=0.18)
    axes[1].legend()
    fig.suptitle("The Wigner packet recovers both exact probability marginals", fontsize=15.5, weight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.90])
    save_figure(fig, "11_wigner_marginals")

    # 12 uncertainty product
    alphas = np.logspace(-1, 2, 500)
    product = np.array([uncertainty_data(float(a))["product"] for a in alphas])
    fig, ax = plt.subplots(figsize=(12.6, 5.2))
    ax.semilogx(alphas, product, color=BLUE, lw=2.2)
    ax.axhline(0.5, color=RED, ls="--", lw=1.6, label="Heisenberg limit")
    ax.set_xlabel(r"shape parameter $\alpha$")
    ax.set_ylabel(r"$\Delta Y\,\Delta P$")
    ax.set_title(r"The log-Gamma packet approaches minimum uncertainty as $\alpha$ grows")
    ax.grid(alpha=0.18, which="both")
    ax.legend()
    save_figure(fig, "12_uncertainty_product")

    # 13 QFI geometry
    fig, ax = diagram_axes((12.6, 6.0))
    ax.text(0.5, 0.92, "Constant quantum geometry of the packet orbit", ha="center", fontsize=19, weight="bold")
    box(ax, (0.08, 0.58), 0.24, 0.18, "translation metric\n" + r"$g_{uu}=\alpha/4$", face=BLUE + "20", edge=BLUE, fontsize=13)
    box(ax, (0.38, 0.58), 0.24, 0.18, "modulation metric\n" + r"$g_{\eta\eta}=\psi_1(\alpha)$", face=TEAL + "20", edge=TEAL, fontsize=13)
    box(ax, (0.68, 0.58), 0.24, 0.18, "Berry curvature\n" + r"$\mathcal{F}_{u\eta}=1$", face=MAGENTA + "20", edge=MAGENTA, fontsize=13)
    box(ax, (0.22, 0.20), 0.23, 0.14, "QFI\n" + r"$\operatorname{diag}(\alpha,4\psi_1)$", face=WHITE, edge=PURPLE, fontsize=12)
    box(ax, (0.55, 0.20), 0.23, 0.14, "uncertainty\n" + r"$\alpha\psi_1(\alpha)>1$", face=WHITE, edge=ORANGE, fontsize=12)
    arrow(ax, (0.20, 0.58), (0.33, 0.34), color=PURPLE)
    arrow(ax, (0.50, 0.58), (0.33, 0.34), color=PURPLE)
    arrow(ax, (0.80, 0.58), (0.67, 0.34), color=ORANGE)
    ax.text(0.5, 0.08, "The metric is flat in packet coordinates while the symplectic curvature remains nonzero.", ha="center", fontsize=11.5, color=MUTED)
    save_figure(fig, "13_quantum_geometry")

    # 14 Laguerre packets
    y_l = np.linspace(-7, 4, 1800)
    fig, ax = plt.subplots(figsize=(12.6, 5.4))
    for ndeg, color in zip(range(6), COLORS):
        ax.plot(y_l, laguerre_packet(1.5, ndeg, y_l), lw=1.8, color=color, label=rf"$n={ndeg}$")
    ax.set_xlabel("log coordinate $y$")
    ax.set_ylabel(r"$\Lambda_{n,\alpha}(y)$")
    ax.set_title("Laguerre packet basis on logarithmic scale")
    ax.grid(alpha=0.18)
    ax.legend(ncol=6)
    save_figure(fig, "14_laguerre_packets")

    # 15 Meixner polynomials
    omega_m = np.linspace(-5.5, 5.5, 1600)
    rho_m = meixner_density(1.5, omega_m)
    fig, ax = plt.subplots(figsize=(12.6, 5.4))
    scale = np.sqrt(rho_m)
    for ndeg, color in zip(range(6), COLORS):
        ax.plot(omega_m, meixner_pollaczek_orthonormal(1.5, ndeg, omega_m) * scale, lw=1.8, color=color, label=rf"$n={ndeg}$")
    ax.set_xlabel(r"Mellin frequency $\omega$")
    ax.set_ylabel(r"$p_n(\omega)\sqrt{\rho_\alpha(\omega)}$")
    ax.set_title("Meixner-Pollaczek packet basis in frequency coordinates")
    ax.grid(alpha=0.18)
    ax.legend(ncol=6)
    save_figure(fig, "15_meixner_packets")

    # 16 Fourier duality
    fig, axes = plt.subplots(2, 2, figsize=(12.8, 7.2), sharex=True)
    omega_d = np.linspace(-5, 5, 500)
    for ax, ndeg in zip(axes.ravel(), range(4)):
        exact = laguerre_packet_fourier(1.5, ndeg, omega_d)
        ax.plot(omega_d, exact.real, color=BLUE, lw=2, label="real")
        ax.plot(omega_d, exact.imag, color=MAGENTA, lw=2, label="imaginary")
        ax.set_title(rf"degree $n={ndeg}$")
        ax.grid(alpha=0.16)
    axes[0, 0].legend(ncol=2)
    for ax in axes[-1]:
        ax.set_xlabel(r"$\omega$")
    fig.suptitle("Fourier transform of Laguerre packets equals the Gamma envelope times Meixner-Pollaczek packets", fontsize=15.5, weight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    save_figure(fig, "16_fourier_duality")

    # 17 Laguerre Jacobi matrix
    jl = laguerre_jacobi(1.5, 12)
    fig, ax = plt.subplots(figsize=(8.4, 6.5))
    image = ax.imshow(jl, cmap="coolwarm", aspect="equal")
    ax.set_title("Laguerre multiplication operator")
    ax.set_xlabel("basis index")
    ax.set_ylabel("basis index")
    for i in range(12):
        for j in range(12):
            if abs(jl[i, j]) > 1e-12:
                ax.text(j, i, f"{jl[i,j]:.1f}", ha="center", va="center", fontsize=7, color=WHITE if abs(jl[i,j]) > 4 else INK)
    fig.colorbar(image, ax=ax, fraction=0.045, pad=0.03)
    save_figure(fig, "17_laguerre_jacobi")

    # 18 Meixner Jacobi matrix
    jm = meixner_jacobi(1.5, 12)
    fig, ax = plt.subplots(figsize=(8.4, 6.5))
    image = ax.imshow(jm, cmap="coolwarm", aspect="equal")
    ax.set_title("Meixner-Pollaczek frequency operator")
    ax.set_xlabel("basis index")
    ax.set_ylabel("basis index")
    for i in range(12):
        for j in range(12):
            if abs(jm[i, j]) > 1e-12:
                ax.text(j, i, f"{jm[i,j]:.1f}", ha="center", va="center", fontsize=7, color=WHITE if abs(jm[i,j]) > 2.5 else INK)
    fig.colorbar(image, ax=ax, fraction=0.045, pad=0.03)
    save_figure(fig, "18_meixner_jacobi")

    # 19 SU(1,1) ladder
    fig, ax = diagram_axes((12.6, 6.2))
    ax.text(0.5, 0.93, r"One $\mathfrak{su}(1,1)$ ladder, two orthogonal coordinate systems", ha="center", fontsize=19, weight="bold")
    xs = np.linspace(0.08, 0.92, 7)
    for ndeg, xpos in enumerate(xs):
        box(ax, (xpos - 0.045, 0.58), 0.09, 0.11, rf"$|{ndeg}\rangle$", face=BLUE + "18", edge=BLUE, fontsize=12)
        if ndeg < len(xs) - 1:
            arrow(ax, (xpos + 0.045, 0.635), (xs[ndeg + 1] - 0.045, 0.635), color=TEAL, text=rf"$\sqrt{{({ndeg+1})({ndeg}+\alpha)}}$", text_offset=(0, 0.055))
    box(ax, (0.15, 0.20), 0.27, 0.15, "Laguerre coordinate\n" + r"$J_L=2K_0-K_+-K_-$", face=WHITE, edge=ORANGE, fontsize=12)
    box(ax, (0.58, 0.20), 0.27, 0.15, "Meixner coordinate\n" + r"$J_M=(K_++K_-)/2$", face=WHITE, edge=MAGENTA, fontsize=12)
    arrow(ax, (0.38, 0.58), (0.285, 0.35), color=ORANGE)
    arrow(ax, (0.62, 0.58), (0.715, 0.35), color=MAGENTA)
    ax.text(0.5, 0.08, r"The Casimir is $\frac{\alpha}{2}(\frac{\alpha}{2}-1)I$ in both atlases.", ha="center", fontsize=12, color=MUTED)
    save_figure(fig, "19_su11_duality")

    # 20 arithmetic convergence
    rows = summary["arithmetic_convergence"]
    scales = np.array([row["scale"] for row in rows], dtype=float)
    errors = np.array([row["error"] for row in rows], dtype=float)
    fig, ax = plt.subplots(figsize=(12.6, 5.2))
    ax.loglog(scales, errors, marker="o", color=BLUE, lw=2.2, label="measured kernel error")
    reference = errors[0] * (scales / scales[0]) ** (-0.25)
    ax.loglog(scales, reference, color=ORANGE, ls="--", lw=1.8, label=r"reference slope $m^{-1/4}$")
    ax.set_xlabel("base depth")
    ax.set_ylabel("complex kernel error")
    ax.set_title("Squarefree arithmetic packets converge to the Gamma-sech phase-space kernel")
    ax.grid(alpha=0.18, which="both")
    ax.legend()
    save_figure(fig, "20_arithmetic_convergence")

    # 21 complex trajectory comparison
    arithmetic = build_arithmetic_kernel(nmax=600_000)
    taus = np.linspace(-5, 5, 320)
    k0, l0 = 5000.0, 20000.0
    discrete = np.array([arithmetic.normalized_centered(k0, l0, float(t)) for t in taus])
    universal = np.array([universal_arithmetic_limit(arithmetic.alpha, arithmetic.beta, k0, l0, float(t)) for t in taus])
    fig, ax = plt.subplots(figsize=(7.2, 6.4))
    ax.plot(universal.real, universal.imag, color=ORANGE, lw=2.4, label="universal")
    ax.plot(discrete.real, discrete.imag, color=BLUE, lw=1.5, ls="--", label="squarefree arithmetic")
    ax.scatter([discrete[0].real, discrete[-1].real], [discrete[0].imag, discrete[-1].imag], color=[TEAL, MAGENTA], s=35)
    ax.set_xlabel("real part")
    ax.set_ylabel("imaginary part")
    ax.set_title("Centered depth-time trajectory")
    ax.grid(alpha=0.18)
    ax.legend()
    ax.set_aspect("equal", adjustable="box")
    save_figure(fig, "21_arithmetic_trajectory")

    # 22 fractional depth flow
    r_values = np.linspace(0.1, 8, 160)
    direct = np.array([fractional_mobius_transfer(float(r), nmax=120_000) for r in r_values])
    fig, ax = plt.subplots(figsize=(12.6, 5.2))
    ax.plot(r_values, direct, color=BLUE, lw=2.2)
    for integer in range(1, 9):
        ax.scatter([integer], [fractional_mobius_transfer(float(integer), nmax=120_000)], color=ORANGE, s=28)
    ax.set_xlabel("continuous depth $r$")
    ax.set_ylabel(r"$C_{2,2}(r,0)$")
    ax.set_title("The weighted finite-difference orbit extends to continuous depth")
    ax.grid(alpha=0.18)
    save_figure(fig, "22_fractional_depth")

    # 23 fractional binomial convergence
    terms = np.arange(4, 121, 4)
    target = float(fractional_binomial_transfer(2.5, terms=5000))
    approximations = []
    for count in terms:
        approximations.append(float(fractional_binomial_transfer(2.5, terms=int(count))))
    errors_frac = np.abs(np.array(approximations) - target)
    fig, ax = plt.subplots(figsize=(12.6, 5.2))
    ax.semilogy(terms, errors_frac, marker="o", color=TEAL, lw=2)
    ax.set_xlabel("binomial-series terms")
    ax.set_ylabel("absolute error")
    ax.set_title("Fractional-depth binomial reconstruction")
    ax.grid(alpha=0.18)
    save_figure(fig, "23_fractional_binomial")

    # 24 coherent-state lattice
    fig, ax = plt.subplots(figsize=(11.7, 6.1))
    uvals = np.linspace(-2.5, 2.5, 9)
    etavals = np.linspace(-4, 4, 9)
    for u in uvals:
        for eta in etavals:
            size = 30 + 220 * abs(complex(gamma_sech_kernel(1.5, u, eta)))
            ax.scatter(u, eta, s=size, facecolor=BLUE, edgecolor=INK, alpha=0.45)
    ax.set_xlabel("log-depth displacement $h$")
    ax.set_ylabel(r"Mellin-frequency displacement $\eta$")
    ax.set_title("A packet lattice weighted by the exact coherent-state overlap")
    ax.grid(alpha=0.15)
    save_figure(fig, "24_coherent_state_lattice")

    # 25 quantum architecture
    fig, ax = diagram_axes((12.6, 6.5))
    ax.text(0.5, 0.94, "Quantum and signal realization of the universal packet", ha="center", fontsize=19, weight="bold")
    box(ax, (0.04, 0.57), 0.18, 0.17, "number basis\n" + r"$|n\rangle$", face=BLUE + "20", edge=BLUE, fontsize=13)
    box(ax, (0.29, 0.57), 0.18, 0.17, "depth filter\n" + r"$e^{-kK_\beta}$", face=TEAL + "20", edge=TEAL, fontsize=13)
    box(ax, (0.54, 0.57), 0.18, 0.17, "logarithmic phase\n" + r"$e^{-itH}$", face=ORANGE + "20", edge=ORANGE, fontsize=13)
    box(ax, (0.79, 0.57), 0.17, 0.17, "packet overlap\n" + r"$\mathfrak{A}_\alpha$", face=MAGENTA + "20", edge=MAGENTA, fontsize=13)
    for start, end in [((0.22, 0.655), (0.29, 0.655)), ((0.47, 0.655), (0.54, 0.655)), ((0.72, 0.655), (0.79, 0.655))]:
        arrow(ax, start, end)
    box(ax, (0.18, 0.20), 0.25, 0.15, "log-coordinate Gabor packet\ntranslation + modulation", face=WHITE, edge=PURPLE, fontsize=11.5)
    box(ax, (0.57, 0.20), 0.25, 0.15, "dual polynomial packets\nLaguerre + Meixner", face=WHITE, edge=RED, fontsize=11.5)
    arrow(ax, (0.38, 0.57), (0.305, 0.35), color=PURPLE)
    arrow(ax, (0.68, 0.57), (0.695, 0.35), color=RED)
    ax.text(0.5, 0.08, "The logarithmic Hamiltonian supplies the time coordinate. The calculus supplies the depth filter and packet geometry.", ha="center", fontsize=11.2, color=MUTED)
    save_figure(fig, "25_quantum_packet_realization")

    # 26 family map
    fig, ax = diagram_axes((12.8, 6.7))
    ax.text(0.5, 0.95, "Special Functions V: generated function family", ha="center", fontsize=20, weight="bold")
    nodes = [
        (0.06, 0.68, "Gamma-sech\nambiguity", BLUE),
        (0.30, 0.68, "log-Gamma\nwindow", TEAL),
        (0.54, 0.68, "Meixner\nspectral law", ORANGE),
        (0.78, 0.68, "Wigner-KL\nfunction", MAGENTA),
        (0.18, 0.28, "Laguerre-Meixner\nFourier pair", PURPLE),
        (0.46, 0.28, r"$\mathfrak{su}(1,1)$" + "\noperator pair", RED),
        (0.74, 0.28, "fractional-depth\ntransfer", YELLOW),
    ]
    for x0, y0, text, color in nodes:
        box(ax, (x0, y0), 0.17, 0.13, text, face=color + "18", edge=color, fontsize=11.2)
    for start, end in [
        ((0.23, 0.745), (0.30, 0.745)),
        ((0.47, 0.745), (0.54, 0.745)),
        ((0.71, 0.745), (0.78, 0.745)),
        ((0.385, 0.68), (0.265, 0.41)),
        ((0.625, 0.68), (0.545, 0.41)),
        ((0.865, 0.68), (0.825, 0.41)),
    ]:
        arrow(ax, start, end, color=INK)
    ax.text(0.5, 0.10, "All seven objects arise from one universal large-depth packet and its exact coordinate transforms.", ha="center", fontsize=11.5, color=MUTED)
    save_figure(fig, "26_function_family_map")


# ---------------------------------------------------------------------------
# Tables and output ledger
# ---------------------------------------------------------------------------


def write_tables(summary: dict[str, object], checks: list[dict[str, object]]) -> None:
    uncertainty_rows = []
    for alpha in (0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0, 10.0):
        row = {"alpha": alpha, **uncertainty_data(alpha)}
        uncertainty_rows.append(row)
    with (TABLES / "uncertainty.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(uncertainty_rows[0].keys()))
        writer.writeheader()
        writer.writerows(uncertainty_rows)

    with (TABLES / "arithmetic_convergence.csv").open("w", newline="") as handle:
        rows = summary["arithmetic_convergence"]
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    with (RESULTS / "checks.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["check", "passed", "detail"])
        writer.writeheader()
        writer.writerows(checks)

    headline = rf"""
\begin{{center}}
\begin{{tabular}}{{L{{0.39\textwidth}}L{{0.47\textwidth}}}}
\toprule
Certificate & Value\\
\midrule
Built-in checks & {summary['built_in_checks']['passed']} of {summary['built_in_checks']['total']} passed\\
Ambiguity formula error & ${summary['ambiguity_max_error']:.3e}$\\
Laguerre--Meixner Fourier error & ${summary['fourier_duality_max_error']:.3e}$\\
Meixner Gram error & ${summary['meixner_gram_error']:.3e}$\\
Laguerre Gram error & ${summary['laguerre_gram_error']:.3e}$\\
$\mathfrak{{su}}(1,1)$ commutator error & ${summary['su11_commutator_error']:.3e}$\\
Poschl--Teller residual & ${summary['poschl_teller_error']:.3e}$\\
Fractional-depth error & ${summary['fractional_depth_error']:.3e}$\\
\bottomrule
\end{{tabular}}
\end{{center}}
"""
    (GENERATED / "headline.tex").write_text(headline)

    lines = [
        r"\begin{longtable}{L{0.42\textwidth}L{0.12\textwidth}L{0.37\textwidth}}",
        r"\caption{Built-in verification ledger.}\label{tab:checks}\\",
        r"\toprule Check & Result & Detail\\\midrule",
        r"\endfirsthead",
        r"\toprule Check & Result & Detail\\\midrule",
        r"\endhead",
    ]
    for check in checks:
        name = str(check["check"]).replace("_", r"\_")
        detail = str(check["detail"]).replace("_", r"\_")
        result = "pass" if check["passed"] else "fail"
        lines.append(f"{name} & {result} & {detail}\\\\")
    lines += [r"\bottomrule", r"\end{longtable}"]
    (GENERATED / "checks.tex").write_text("\n".join(lines))

    uncertainty_tex = [
        r"\begin{center}",
        r"\begin{tabular}{rrrrr}",
        r"\toprule $\alpha$ & $\operatorname{Var}Y$ & $\operatorname{Var}P$ & $\Delta Y\Delta P$ & $\mathcal I_{\eta\eta}$\\\midrule",
    ]
    for row in uncertainty_rows:
        uncertainty_tex.append(
            f"{row['alpha']:.2f} & {row['var_y']:.6f} & {row['var_p']:.6f} & {row['product']:.6f} & {row['qfi_eta']:.6f}\\\\"
        )
    uncertainty_tex += [r"\bottomrule", r"\end{tabular}", r"\end{center}"]
    (GENERATED / "uncertainty.tex").write_text("\n".join(uncertainty_tex))

    convergence_tex = [
        r"\begin{center}",
        r"\begin{tabular}{rrrr}",
        r"\toprule base depth & kernel error & real part & imaginary part\\\midrule",
    ]
    for row in summary["arithmetic_convergence"]:
        convergence_tex.append(
            f"{row['scale']} & {row['error']:.6e} & {row['discrete_real']:.8f} & {row['discrete_imag']:.8f}\\\\"
        )
    convergence_tex += [r"\bottomrule", r"\end{tabular}", r"\end{center}"]
    (GENERATED / "arithmetic_convergence.tex").write_text("\n".join(convergence_tex))


def main() -> None:
    checks, summary = perform_checks()
    generate_figures(summary)
    write_tables(summary, checks)
    summary["figure_pairs"] = len(list(FIGURES.glob("*.pdf")))
    (RESULTS / "results.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary["built_in_checks"], indent=2))


if __name__ == "__main__":
    main()
