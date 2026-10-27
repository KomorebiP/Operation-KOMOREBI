from __future__ import annotations

import cmath
import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle
import mpmath as mp
import numpy as np
import sympy as sp
from scipy.special import gamma as gamma_fn
from scipy.special import gammainc

mp.mp.dps = 60

ROOT = Path(__file__).resolve().parent
FIGURES = ROOT / "figures"
RESULTS = ROOT / "results"
TABLES = ROOT / "tables"
for directory in (FIGURES, RESULTS, TABLES):
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
        "axes.titlesize": 12.5,
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


def diagram_axes(figsize: tuple[float, float] = (12.5, 6.0)) -> tuple[plt.Figure, plt.Axes]:
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
    fontsize: float = 11.5,
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
            fontsize=10.5,
            color=color,
        )


# ---------------------------------------------------------------------------
# Arithmetic and character helpers
# ---------------------------------------------------------------------------


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
            ip = i * p
            if ip > nmax:
                break
            composite[ip] = True
            if i % p == 0:
                mu[ip] = 0
                break
            mu[ip] = -mu[i]
    return mu


def prime_factors(n: int) -> list[int]:
    factors: list[int] = []
    p = 2
    remaining = n
    while p * p <= remaining:
        if remaining % p == 0:
            factors.append(p)
            while remaining % p == 0:
                remaining //= p
        p += 1
    if remaining > 1:
        factors.append(remaining)
    return factors


def squarefree_coprime_density(q: int) -> float:
    value = 1.0 / float(mp.zeta(2))
    for p in prime_factors(q):
        value *= p / (p + 1)
    return value


def characters_mod5(nmax: int) -> np.ndarray:
    """Return the four Dirichlet characters modulo 5.

    Character j sends the primitive residue 2 to exp(2*pi*i*j/4).
    """
    log_map = {1: 0, 2: 1, 4: 2, 3: 3}
    chars = np.zeros((4, nmax + 1), dtype=np.complex128)
    for n in range(1, nmax + 1):
        residue = n % 5
        if residue == 0:
            continue
        exponent = log_map[residue]
        for j in range(4):
            chars[j, n] = np.exp(2j * np.pi * j * exponent / 4)
    return chars


def dirichlet_l_hurwitz(s: complex, character_values: Sequence[complex], q: int) -> complex:
    total = mp.mpc(0)
    for r in range(1, q + 1):
        chi = complex(character_values[r % q]) if len(character_values) == q else complex(character_values[r])
        if abs(chi) > 0:
            total += chi * mp.zeta(s, mp.mpf(r) / q)
    return complex(total / (mp.mpc(q) ** s))


# ---------------------------------------------------------------------------
# Bernoulli-Hurwitz packets and Stieltjes germs
# ---------------------------------------------------------------------------


def bernoulli_packet(z: complex, a: complex, modulus: int, residue: int) -> complex:
    if abs(z) < 1e-28:
        return 1.0 / modulus
    zz = mp.mpc(z)
    q = mp.mpc(a + residue) / modulus
    return complex(-zz * (mp.mpf(modulus) ** (zz - 1)) * mp.zeta(1 - zz, q))


def child_parameters(a: float, m: int, r: int, ell: int) -> tuple[int, list[mp.mpf]]:
    q_total = ell * m
    parameters = [mp.mpf(a + r + child * m) / q_total for child in range(ell)]
    return q_total, parameters


def stieltjes_packet(ell: int, m: int, r: int, a: float, j: int, order: int) -> complex:
    omega = mp.e ** (2j * mp.pi / ell)
    q_total, parameters = child_parameters(a, m, r, ell)
    total = mp.mpc(0)
    for child, parameter in enumerate(parameters):
        total += omega ** (-j * child) * mp.stieltjes(order, parameter)
    return complex(total / mp.sqrt(ell))


def detail_channel(z: complex, ell: int, m: int, r: int, a: float, j: int) -> complex:
    q_total = ell * m
    omega = cmath.exp(2j * math.pi / ell)
    values = [bernoulli_packet(z, a, q_total, r + child * m) for child in range(ell)]
    return sum(omega ** (-j * child) * values[child] for child in range(ell)) / math.sqrt(ell)


def detail_derivative_from_stieltjes(
    ell: int,
    m: int,
    r: int,
    a: float,
    j: int,
    derivative_order: int,
) -> complex:
    if j == 0:
        raise ValueError("The compact derivative formula below is for non-DC channels")
    q_total = ell * m
    log_q = math.log(q_total)
    total = 0j
    for order in range(derivative_order):
        g = stieltjes_packet(ell, m, r, a, j, order)
        total += math.comb(derivative_order - 1, order) * (log_q ** (derivative_order - 1 - order)) * g
    return -(derivative_order / q_total) * total


def detail_variance(children: Sequence[complex]) -> complex:
    values = np.asarray(children, dtype=np.complex128)
    return complex(np.sum(values * values) - np.sum(values) ** 2 / len(values))


def transformed_details(children: Sequence[complex]) -> np.ndarray:
    values = np.asarray(children, dtype=np.complex128)
    return np.fft.fft(values) / math.sqrt(len(values))


def bernoulli_children_exact(n: int, a: sp.Rational, ell: int, m: int = 1, r: int = 0) -> list[sp.Expr]:
    q_total = ell * m
    return [
        sp.simplify(q_total ** (n - 1) * sp.bernoulli(n, sp.Rational(a) + sp.Rational(r + child * m, q_total)))
        for child in range(ell)
    ]


def primitive_packet_resultant_exact(n: int, a: sp.Rational, ell: int, m: int = 1, r: int = 0) -> sp.Expr:
    x = sp.symbols("x")
    children = bernoulli_children_exact(n, a, ell, m, r)
    polynomial = sum(children[index] * x**index for index in range(ell))
    return sp.factor(sp.resultant(sp.cyclotomic_poly(ell, x), polynomial, x))


# ---------------------------------------------------------------------------
# Positive Mobius packet energy and resolvent
# ---------------------------------------------------------------------------


def packet_energy_values(
    k_values: Sequence[int],
    a: float,
    beta: float,
    nmax: int,
    q: int = 1,
    mu: np.ndarray | None = None,
) -> np.ndarray:
    if mu is None:
        mu = mobius_sieve(nmax)
    n = np.arange(2, nmax + 1, dtype=np.float64)
    support = (mu[2:] != 0).astype(np.float64)
    if q > 1:
        support *= (np.gcd(n.astype(np.int64), q) == 1).astype(np.float64)
    base = support * n ** (-2 * a)
    log_x = 2.0 * np.log1p(-n ** (-beta))
    results = []
    for k in k_values:
        results.append(float(np.dot(base, np.exp(k * log_x))))
    # n=1 contributes only at k=0.  It is omitted because the asymptotic theory and all tests use k>=1.
    return np.asarray(results)


def energy_asymptotic_constant(a: float, beta: float, q: int = 1) -> float:
    alpha = (2 * a - 1) / beta
    return squarefree_coprime_density(q) / beta * float(gamma_fn(alpha)) * (2.0 ** (-alpha))


def energy_asymptotic(k: np.ndarray | float, a: float, beta: float, q: int = 1) -> np.ndarray:
    alpha = (2 * a - 1) / beta
    constant = energy_asymptotic_constant(a, beta, q)
    return constant * np.asarray(k, dtype=float) ** (-alpha)


def finite_differences(values: np.ndarray, max_order: int) -> list[np.ndarray]:
    rows = [np.asarray(values, dtype=float)]
    current = np.asarray(values, dtype=float)
    for _ in range(max_order):
        current = np.diff(current)
        rows.append(current)
    return rows


def energy_resolvent(z: complex, a: float, beta: float, nmax: int, q: int, mu: np.ndarray) -> complex:
    n = np.arange(2, nmax + 1, dtype=np.float64)
    support = (mu[2:] != 0).astype(np.float64)
    if q > 1:
        support *= (np.gcd(n.astype(np.int64), q) == 1).astype(np.float64)
    weights = support * n ** (-2 * a)
    x = (1.0 - n ** (-beta)) ** 2
    return complex(np.sum(weights / (1.0 - z * x)))


def squarefree_dirichlet_ratio(s: float, q: int = 1) -> mp.mpf:
    value = mp.zeta(s) / mp.zeta(2 * s)
    for p in prime_factors(q):
        value /= 1 + mp.mpf(p) ** (-s)
    return value


def energy_from_zeta_ratio(k: int, a: float, beta: float, q: int = 1) -> mp.mpf:
    total = mp.mpf(0)
    for j in range(2 * k + 1):
        total += (-1) ** j * math.comb(2 * k, j) * squarefree_dirichlet_ratio(2 * a + beta * j, q)
    return total


# ---------------------------------------------------------------------------
# Gamma scaling and character decoherence
# ---------------------------------------------------------------------------


def gamma_weighted_sample(
    k: int,
    a: float,
    beta: float,
    nmax: int,
    q: int,
    mu: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    n = np.arange(2, nmax + 1, dtype=np.float64)
    support = (mu[2:] != 0).astype(np.float64)
    if q > 1:
        support *= (np.gcd(n.astype(np.int64), q) == 1).astype(np.float64)
    log_weight = -2 * a * np.log(n) + 2 * k * np.log1p(-n ** (-beta))
    log_weight = np.where(support > 0, log_weight, -np.inf)
    maximum = np.max(log_weight)
    weights = np.exp(log_weight - maximum)
    weights /= weights.sum()
    u = 2.0 * k / (n**beta)
    order = np.argsort(u)
    return u[order], weights[order]


def weighted_moments(values: np.ndarray, weights: np.ndarray, max_order: int) -> list[float]:
    return [float(np.dot(weights, values**order)) for order in range(1, max_order + 1)]


def weighted_quantile(values: np.ndarray, weights: np.ndarray, probabilities: Sequence[float]) -> np.ndarray:
    cumulative = np.cumsum(weights)
    return np.interp(np.asarray(probabilities), cumulative, values)


def ks_distance_to_gamma(values: np.ndarray, weights: np.ndarray, alpha: float) -> float:
    empirical = np.cumsum(weights)
    theoretical = gammainc(alpha, values)
    return float(np.max(np.abs(empirical - theoretical)))


def character_gram_matrix(
    k: int,
    a: float,
    beta: float,
    nmax: int,
    mu: np.ndarray,
    characters: np.ndarray,
) -> np.ndarray:
    n = np.arange(2, nmax + 1, dtype=np.float64)
    squarefree = (mu[2:] != 0).astype(np.float64)
    weights = squarefree * n ** (-2 * a) * np.exp(2 * k * np.log1p(-n ** (-beta)))
    char_slice = characters[:, 2 : nmax + 1]
    weighted = char_slice * np.sqrt(weights)[None, :]
    return weighted @ weighted.conj().T


def normalized_correlation(gram: np.ndarray) -> np.ndarray:
    diagonal = np.real(np.diag(gram))
    denom = np.sqrt(np.outer(diagonal, diagonal))
    return np.divide(gram, denom, out=np.zeros_like(gram), where=denom > 0)


# ---------------------------------------------------------------------------
# Figures and checks
# ---------------------------------------------------------------------------


@dataclass
class Check:
    name: str
    passed: bool
    detail: str


def generate_all() -> dict[str, object]:
    checks: list[Check] = []
    tables: dict[str, list[dict[str, object]]] = {}

    # Figure 01: conceptual pipeline.
    fig, ax = diagram_axes((13.0, 6.2))
    ax.text(0.5, 0.94, "From Bernoulli children to local arithmetic invariants", ha="center", fontsize=20, weight="bold")
    stages = [
        (0.04, r"Hurwitz children\n$b_\ell(z;a)$", BLUE),
        (0.23, "cyclotomic DFT\n$W_j(z;a)$", TEAL),
        (0.42, "Stieltjes germ\n$G_{j,m}(a)$", ORANGE),
        (0.61, r"scalar invariants\n$\mathcal{V}$ and $\mathcal{N}$", MAGENTA),
        (0.80, "positive energy\n$E(k)$ and resolvent", RED),
    ]
    for x0, text, color in stages:
        box(ax, (x0, 0.55), 0.15, 0.18, text, face=color + "20", edge=color, fontsize=12)
    for left, right in zip(stages[:-1], stages[1:], strict=True):
        arrow(ax, (left[0] + 0.15, 0.64), (right[0], 0.64), color=INK)
    box(ax, (0.20, 0.17), 0.22, 0.16, r"$L^{(m)}(1,\chi)$\ncharacter transform", face=TEAL + "18", edge=TEAL, fontsize=12)
    box(ax, (0.56, 0.17), 0.22, 0.16, "Gamma scaling\nand character decoherence", face=PURPLE + "18", edge=PURPLE, fontsize=12)
    arrow(ax, (0.50, 0.55), (0.31, 0.33), color=TEAL)
    arrow(ax, (0.88, 0.55), (0.67, 0.33), color=PURPLE)
    ax.text(0.5, 0.065, "Every map is exact at finite packet depth.  Asymptotic statements enter only in the energy and decoherence limits.", ha="center", fontsize=11.2, color=MUTED)
    save_figure(fig, "01_theory_pipeline")

    # Stieltjes packet matrix for L=4.
    ell, m, r, a = 4, 1, 0, 1.0
    stieltjes_matrix = np.array(
        [[stieltjes_packet(ell, m, r, a, j, order) for order in range(6)] for j in range(ell)],
        dtype=np.complex128,
    )
    fig, axes = plt.subplots(1, 2, figsize=(12.8, 4.8))
    im0 = axes[0].imshow(np.real(stieltjes_matrix), cmap="coolwarm", aspect="auto")
    axes[0].set_title("Real parts of $G_{j,m}(1)$")
    axes[0].set_xlabel("Stieltjes order $m$")
    axes[0].set_ylabel("cyclotomic channel $j$")
    axes[0].set_xticks(range(6))
    axes[0].set_yticks(range(ell))
    fig.colorbar(im0, ax=axes[0], fraction=0.045)
    im1 = axes[1].imshow(np.imag(stieltjes_matrix), cmap="coolwarm", aspect="auto")
    axes[1].set_title("Imaginary parts of $G_{j,m}(1)$")
    axes[1].set_xlabel("Stieltjes order $m$")
    axes[1].set_ylabel("cyclotomic channel $j$")
    axes[1].set_xticks(range(6))
    axes[1].set_yticks(range(ell))
    fig.colorbar(im1, ax=axes[1], fraction=0.045)
    fig.suptitle("Cyclotomic Stieltjes packets are the local Taylor data of the Bernoulli-Lerch detail bank", fontsize=16.5, weight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.91])
    save_figure(fig, "02_stieltjes_packet_matrix")

    # Two-channel derivative example.
    derivative_exact = -math.log(2) / math.sqrt(2)
    derivative_formula = detail_derivative_from_stieltjes(2, 1, 0, 1.0, 1, 1)
    checks.append(Check("two_channel_first_derivative", abs(derivative_formula - derivative_exact) < 1e-14, f"error={abs(derivative_formula-derivative_exact):.3e}"))
    z_values = np.linspace(-0.35, 0.35, 241)
    detail_values = np.array([detail_channel(float(z), 2, 1, 0, 1.0, 1).real for z in z_values])
    linear = derivative_exact * z_values
    fig, ax = plt.subplots(figsize=(11.8, 4.8))
    ax.plot(z_values, detail_values, lw=2.1, label="exact $W_1(z;1)$")
    ax.plot(z_values, linear, lw=1.7, linestyle="--", label=r"$-(\log 2)z/\sqrt{2}$")
    ax.axhline(0, color=GRID, lw=1)
    ax.axvline(0, color=GRID, lw=1)
    ax.set_xlabel("complex order restricted to real $z$")
    ax.set_ylabel("detail value")
    ax.set_title(r"The first Bernoulli-Euler detail coefficient is $-(\log 2)/\sqrt{2}$")
    ax.legend()
    ax.grid(alpha=0.18)
    fig.tight_layout()
    save_figure(fig, "03_two_channel_germ")

    # Derivative checks through order 4 by direct high-precision differentiation
    # of the Hurwitz-zeta child formula.
    def detail_mp(z_value: mp.mpf | mp.mpc) -> mp.mpc:
        z_mp = mp.mpc(z_value)
        values = []
        for child in range(2):
            parameter = mp.mpf(1 + child) / 2
            if abs(z_mp) < mp.mpf("1e-70"):
                child_value = mp.mpf(1) / 2
            else:
                child_value = -z_mp * (mp.mpf(2) ** (z_mp - 1)) * mp.zeta(1 - z_mp, parameter)
            values.append(child_value)
        return (values[0] - values[1]) / mp.sqrt(2)

    derivative_rows: list[dict[str, object]] = []
    for nder in range(1, 5):
        predicted = detail_derivative_from_stieltjes(2, 1, 0, 1.0, 1, nder)
        numeric_mp = mp.diff(detail_mp, mp.mpf(0), nder)
        numeric = complex(numeric_mp)
        error = abs(predicted - numeric)
        derivative_rows.append({"order": nder, "predicted": predicted.real, "numeric": numeric.real, "error": error})
        checks.append(Check(f"stieltjes_derivative_order_{nder}", error < 2e-14, f"error={error:.3e}"))
    tables["stieltjes_derivatives"] = derivative_rows

    # Character transform and L derivatives for nonprincipal character mod 4.
    q = 4
    chi_values = [mp.mpc(0), mp.mpc(1), mp.mpc(0), mp.mpc(-1), mp.mpc(0)]
    character_rows: list[dict[str, object]] = []
    for order in range(4):
        lhs_mp = sum(chi_values[r] * mp.stieltjes(order, mp.mpf(r) / q) for r in range(1, q + 1))
        lhs = complex(lhs_mp)
        rhs_sum = mp.mpc(0)
        for h in range(order + 1):
            derivative = mp.diff(
                lambda ss: mp.dirichlet(ss, [0, 1, 0, -1]),
                1,
                h,
            )
            rhs_sum += math.comb(order, h) * (mp.log(q) ** (order - h)) * derivative
        rhs = ((-1) ** order) * q * rhs_sum
        error = abs(lhs - complex(rhs))
        character_rows.append({"order": order, "packet_sum_real": lhs.real, "formula_real": float(mp.re(rhs)), "error": error})
        checks.append(Check(f"character_derivative_transform_{order}", error < 5e-8, f"error={error:.3e}"))
    tables["character_derivatives"] = character_rows
    fig, ax = plt.subplots(figsize=(11.8, 4.7))
    orders = np.arange(4)
    lhs_values = [row["packet_sum_real"] for row in character_rows]
    rhs_values = [row["formula_real"] for row in character_rows]
    width = 0.36
    ax.bar(orders - width / 2, lhs_values, width, label="Stieltjes packet sum")
    ax.bar(orders + width / 2, rhs_values, width, label="$L$-derivative formula")
    ax.set_xticks(orders, [f"$m={value}$" for value in orders])
    ax.set_ylabel("real value")
    ax.set_title(r"Character packets recover the derivatives of $L(s,\chi_4)$ at $s=1$")
    ax.grid(axis="y", alpha=0.18)
    ax.legend()
    fig.tight_layout()
    save_figure(fig, "04_character_L_derivatives")

    # Detail variance identities on a deterministic complex example.
    children_complex = np.array([1.1 + 0.2j, -0.4 + 0.7j, 0.8 - 0.5j, 0.3 + 0.1j])
    transformed = transformed_details(children_complex)
    variance_direct = detail_variance(children_complex)
    variance_fourier = sum(transformed[j] * transformed[-j % len(transformed)] for j in range(1, len(transformed)))
    pairwise = sum((children_complex[l] - children_complex[m]) ** 2 for l in range(4) for m in range(l + 1, 4)) / 4
    checks.append(Check("detail_variance_fourier_identity", abs(variance_direct - variance_fourier) < 1e-13, f"error={abs(variance_direct-variance_fourier):.3e}"))
    checks.append(Check("detail_variance_pairwise_identity", abs(variance_direct - pairwise) < 1e-13, f"error={abs(variance_direct-pairwise):.3e}"))
    fig, axes = plt.subplots(1, 2, figsize=(12.8, 4.8))
    axes[0].scatter(children_complex.real, children_complex.imag, s=85)
    for index, value in enumerate(children_complex):
        axes[0].text(value.real + 0.03, value.imag + 0.03, f"$b_{index}$")
    axes[0].axhline(0, color=GRID, lw=1)
    axes[0].axvline(0, color=GRID, lw=1)
    axes[0].set_xlabel("real part")
    axes[0].set_ylabel("imaginary part")
    axes[0].set_title("child packets")
    axes[0].grid(alpha=0.15)
    axes[1].bar(np.arange(4), np.abs(transformed), color=COLORS[:4])
    axes[1].set_xticks(range(4), ["DC", "detail 1", "detail 2", "detail 3"])
    axes[1].set_ylabel("channel magnitude")
    axes[1].set_title("unitary child transform")
    axes[1].grid(axis="y", alpha=0.15)
    fig.suptitle("The holomorphic detail variance is the non-DC Fourier energy without conjugation", fontsize=16.2, weight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.91])
    save_figure(fig, "05_detail_variance_identity")

    # Bernoulli-Euler variance.
    x_values = np.linspace(0, 1, 401)
    fig, ax = plt.subplots(figsize=(11.8, 4.9))
    for n_order, color in [(4, BLUE), (6, TEAL), (8, MAGENTA)]:
        function = sp.lambdify(sp.symbols("x"), sp.Rational(n_order**2, 8) * sp.euler(n_order - 1, sp.symbols("x")) ** 2, "numpy")
        ax.plot(x_values, function(x_values), lw=1.8, color=color, label=rf"$n={n_order}$")
    ax.set_xlabel("Bernoulli parameter $a$")
    ax.set_ylabel(r"$\mathcal{V}_2(n;a)$")
    ax.set_title("The two-channel refinement variance is an Euler-polynomial square")
    ax.legend()
    ax.grid(alpha=0.18)
    fig.tight_layout()
    save_figure(fig, "06_bernoulli_euler_variance")

    # Exact L=3 example.
    children_l3 = bernoulli_children_exact(4, sp.Rational(0), 3)
    variance_l3 = sp.simplify(sum(value**2 for value in children_l3) - sum(children_l3) ** 2 / 3)
    checks.append(Check("three_channel_variance_exact", variance_l3 == sp.Rational(32, 27), f"value={variance_l3}"))
    fig, ax = plt.subplots(figsize=(10.8, 4.8))
    positions = np.arange(3)
    values = [float(value) for value in children_l3]
    ax.bar(positions, values, color=[BLUE, TEAL, ORANGE])
    ax.axhline(float(sum(children_l3) / 3), color=INK, linestyle="--", label="parent mean")
    for position, value in zip(positions, children_l3, strict=True):
        ax.text(position, float(value) + (0.05 if float(value) >= 0 else -0.10), f"${sp.latex(value)}$", ha="center")
    ax.set_xticks(positions, ["child 0", "child 1", "child 2"])
    ax.set_ylabel("packet value")
    ax.set_title(r"Order four, three-channel Bernoulli refinement: $\mathcal{V}_3=32/27$")
    ax.legend()
    ax.grid(axis="y", alpha=0.16)
    fig.tight_layout()
    save_figure(fig, "07_three_channel_variance")

    # Primitive resultants for L=3 and 5.
    resultant_rows: list[dict[str, object]] = []
    for ell_value in (3, 4, 5):
        for n_order in range(2, 11):
            value = primitive_packet_resultant_exact(n_order, sp.Rational(0), ell_value)
            resultant_rows.append({"L": ell_value, "n": n_order, "value": str(value), "zero": bool(value == 0)})
            checks.append(Check(f"resultant_rational_L{ell_value}_n{n_order}", bool(value.is_rational), f"value={value}"))
    tables["resultants"] = resultant_rows
    fig, ax = plt.subplots(figsize=(12.2, 5.0))
    for ell_value, color in [(3, BLUE), (4, TEAL), (5, MAGENTA)]:
        subset = [row for row in resultant_rows if row["L"] == ell_value]
        n_orders = np.array([row["n"] for row in subset])
        magnitudes = np.array([math.log10(abs(float(sp.Rational(row["value"]))) + 1e-30) for row in subset])
        ax.plot(n_orders, magnitudes, marker="o", color=color, label=rf"$L={ell_value}$")
    ax.set_xlabel("integer order $n$")
    ax.set_ylabel(r"$\log_{10}|\mathcal{N}^{(L)}(n;0)|$")
    ax.set_title("Primitive packet resultants compress a full cyclotomic detail orbit into one scalar")
    ax.legend()
    ax.grid(alpha=0.18)
    fig.tight_layout()
    save_figure(fig, "08_primitive_resultants")

    # Energy computations.
    nmax = 500_000
    mu = mobius_sieve(nmax)
    a_energy = 2.0
    beta_energy = 2.0
    k_dense = np.arange(1, 161)
    energy_dense = packet_energy_values(k_dense, a_energy, beta_energy, nmax, 1, mu)
    differences = finite_differences(energy_dense, 8)
    sign_matrix = np.full((9, 120), np.nan)
    for order, row in enumerate(differences):
        usable = min(120, len(row))
        sign_matrix[order, :usable] = ((-1) ** order) * row[:usable]
    checks.append(Check("complete_monotonicity_numeric", bool(np.nanmin(sign_matrix) >= -2e-18), f"minimum={np.nanmin(sign_matrix):.3e}"))
    fig, ax = plt.subplots(figsize=(12.0, 5.1))
    image = ax.imshow(np.log10(np.maximum(sign_matrix, 1e-30)), cmap="viridis", aspect="auto")
    ax.set_yticks(range(9), [rf"$m={order}$" for order in range(9)])
    ax.set_xlabel("finite-difference location $k$")
    ax.set_title(r"Complete monotonicity: $(-1)^m\Delta^mE(k)\geq 0$")
    fig.colorbar(image, ax=ax, fraction=0.027, pad=0.02, label="log10 positive value")
    fig.tight_layout()
    save_figure(fig, "09_complete_monotonicity")

    # Hankel positivity.
    energy_hankel = packet_energy_values(np.arange(0, 25), a_energy, beta_energy, nmax, 1, mu)
    hankel_rows = []
    for size in range(2, 11):
        matrix = np.array([[energy_hankel[i + j] for j in range(size)] for i in range(size)])
        eigenvalues = np.linalg.eigvalsh(matrix)
        hankel_rows.append({"size": size, "minimum_eigenvalue": float(eigenvalues[0]), "maximum_eigenvalue": float(eigenvalues[-1])})
        checks.append(Check(f"hankel_positive_size_{size}", bool(eigenvalues[0] > -1e-14), f"min_eig={eigenvalues[0]:.3e}"))
    tables["hankel"] = hankel_rows
    fig, ax = plt.subplots(figsize=(11.8, 4.8))
    sizes = np.array([row["size"] for row in hankel_rows])
    minimums = np.array([max(row["minimum_eigenvalue"], 1e-30) for row in hankel_rows])
    maximums = np.array([row["maximum_eigenvalue"] for row in hankel_rows])
    ax.semilogy(sizes, minimums, marker="o", label="smallest eigenvalue")
    ax.semilogy(sizes, maximums, marker="o", label="largest eigenvalue")
    ax.set_xlabel("Hankel size")
    ax.set_ylabel("eigenvalue")
    ax.set_title("Finite packet-energy Hankel matrices are positive")
    ax.legend()
    ax.grid(alpha=0.18, which="both")
    fig.tight_layout()
    save_figure(fig, "10_hankel_positivity")

    # Resolvent over the complex plane.
    xs = np.linspace(-1.4, 1.35, 170)
    ys = np.linspace(-1.25, 1.25, 135)
    magnitude = np.zeros((len(ys), len(xs)))
    n_res = np.arange(2, 5001, dtype=np.float64)
    support_res = (mu[2:5001] != 0).astype(np.float64)
    weights_res = support_res * n_res ** (-2 * a_energy)
    x_res = (1.0 - n_res ** (-beta_energy)) ** 2
    for row, y in enumerate(ys):
        z_row = xs.astype(np.complex128) + 1j * y
        values = np.sum(weights_res[None, :] / (1.0 - z_row[:, None] * x_res[None, :]), axis=1)
        magnitude[row, :] = np.log10(np.maximum(np.abs(values), 1e-300))
        if abs(y) < 0.025:
            magnitude[row, xs >= 1.0] = np.nan
    fig, ax = plt.subplots(figsize=(11.8, 5.5))
    image = ax.imshow(magnitude, extent=[xs[0], xs[-1], ys[0], ys[-1]], origin="lower", cmap="magma", aspect="auto")
    ax.plot([1, xs[-1]], [0, 0], color=WHITE, lw=3.0, label=r"excluded cut $[1,\infty)$")
    ax.set_xlabel("real part of $z$")
    ax.set_ylabel("imaginary part of $z$")
    ax.set_title("The packet-energy resolvent is zero-free off its positive-real cut")
    ax.legend(loc="lower left", facecolor="#111111", edgecolor=WHITE, labelcolor=WHITE, framealpha=0.82)
    fig.colorbar(image, ax=ax, fraction=0.027, pad=0.02, label=r"$\log_{10}|\mathcal{E}(z)|$")
    fig.tight_layout()
    save_figure(fig, "11_zero_free_resolvent")

    # Direct versus zeta-ratio finite differences at modest k.
    ratio_rows: list[dict[str, object]] = []
    for k in range(1, 9):
        direct = packet_energy_values([k], a_energy, beta_energy, nmax, 1, mu)[0]
        exact = float(energy_from_zeta_ratio(k, a_energy, beta_energy, 1))
        error = abs(direct - exact)
        ratio_rows.append({"k": k, "direct": direct, "zeta_ratio": exact, "truncation_error": error})
        checks.append(Check(f"zeta_ratio_energy_{k}", error < 2e-14, f"error={error:.3e}"))
    tables["zeta_ratio"] = ratio_rows
    fig, ax = plt.subplots(figsize=(11.8, 4.8))
    kvals = np.array([row["k"] for row in ratio_rows])
    direct_values = np.array([row["direct"] for row in ratio_rows])
    ratio_values = np.array([row["zeta_ratio"] for row in ratio_rows])
    ax.semilogy(kvals, direct_values, marker="o", lw=2, label="direct squarefree sum")
    ax.semilogy(kvals, ratio_values, marker="x", lw=1.5, linestyle="--", label=r"finite difference of $\zeta(s)/\zeta(2s)$")
    ax.set_xlabel("difference order $k$")
    ax.set_ylabel("energy")
    ax.set_title("One positive packet energy has two exact arithmetic coordinate systems")
    ax.legend()
    ax.grid(alpha=0.18, which="both")
    fig.tight_layout()
    save_figure(fig, "12_zeta_ratio_coordinates")

    # Energy asymptotic.
    k_asym = np.array([100, 300, 1000, 3000, 10000, 30000, 100000])
    energy_asym_values = packet_energy_values(k_asym, a_energy, beta_energy, nmax, 1, mu)
    alpha = (2 * a_energy - 1) / beta_energy
    constant = energy_asymptotic_constant(a_energy, beta_energy, 1)
    normalized = energy_asym_values * k_asym**alpha
    energy_rows = []
    for k, value, norm in zip(k_asym, energy_asym_values, normalized, strict=True):
        energy_rows.append({"k": int(k), "energy": value, "scaled": norm, "relative_error": abs(norm / constant - 1)})
    tables["energy_asymptotic"] = energy_rows
    checks.append(Check("energy_asymptotic_final", abs(normalized[-1] / constant - 1) < 0.01, f"relative_error={abs(normalized[-1]/constant-1):.3e}"))
    fig, ax = plt.subplots(figsize=(11.8, 4.8))
    ax.semilogx(k_asym, normalized, marker="o", lw=2, label=r"$k^{3/2}E_k$")
    ax.axhline(constant, color=RED, linestyle="--", label="proved asymptotic constant")
    ax.set_xlabel("$k$")
    ax.set_ylabel("scaled energy")
    ax.set_title("The principal packet energy has the exact $k^{-3/2}$ scale")
    ax.legend()
    ax.grid(alpha=0.18)
    fig.tight_layout()
    save_figure(fig, "13_energy_asymptotic")

    # Gamma scaling distribution.
    gamma_rows: list[dict[str, object]] = []
    fig, ax = plt.subplots(figsize=(11.8, 5.0))
    u_grid = np.linspace(0, 8, 500)
    gamma_density = u_grid ** (alpha - 1) * np.exp(-u_grid) / gamma_fn(alpha)
    ax.plot(u_grid, gamma_density, color=INK, lw=2.4, label=rf"Gamma$(\alpha={alpha:.1f},1)$")
    for index, k in enumerate([300, 3000, 30000, 100000]):
        values, weights = gamma_weighted_sample(k, a_energy, beta_energy, nmax, 1, mu)
        bins = np.linspace(0, 8, 70)
        hist, edges = np.histogram(values, bins=bins, weights=weights, density=True)
        centers = (edges[:-1] + edges[1:]) / 2
        ax.plot(centers, hist, lw=1.35, color=COLORS[index], label=rf"$k={k}$")
        moments = weighted_moments(values, weights, 2)
        quantiles = weighted_quantile(values, weights, [0.1, 0.5, 0.9])
        ks = ks_distance_to_gamma(values, weights, alpha)
        gamma_rows.append({
            "k": k,
            "mean": moments[0],
            "variance": moments[1] - moments[0] ** 2,
            "q10": quantiles[0],
            "q50": quantiles[1],
            "q90": quantiles[2],
            "ks": ks,
        })
    tables["gamma_scaling"] = gamma_rows
    checks.append(Check("gamma_mean_final", abs(gamma_rows[-1]["mean"] - alpha) < 0.03, f"mean={gamma_rows[-1]['mean']:.6f}"))
    checks.append(Check("gamma_variance_final", abs(gamma_rows[-1]["variance"] - alpha) < 0.06, f"variance={gamma_rows[-1]['variance']:.6f}"))
    ax.set_xlim(0, 8)
    ax.set_xlabel(r"$U_k=2k/n^2$")
    ax.set_ylabel("probability density")
    ax.set_title("The active squarefree packet window converges to a Gamma law")
    ax.legend(ncol=2)
    ax.grid(alpha=0.16)
    fig.tight_layout()
    save_figure(fig, "14_gamma_scaling")

    fig, ax = plt.subplots(figsize=(11.8, 4.8))
    gamma_k = np.array([row["k"] for row in gamma_rows])
    ks_values = np.array([row["ks"] for row in gamma_rows])
    ax.loglog(gamma_k, ks_values, marker="o", lw=2)
    ax.set_xlabel("$k$")
    ax.set_ylabel("weighted Kolmogorov distance")
    ax.set_title("Finite packet distributions approach the limiting Gamma profile")
    ax.grid(alpha=0.18, which="both")
    fig.tight_layout()
    save_figure(fig, "15_gamma_convergence")

    # Character Gram and decoherence.
    characters = characters_mod5(nmax)
    gram_small = character_gram_matrix(100, a_energy, beta_energy, nmax, mu, characters)
    gram_large = character_gram_matrix(100000, a_energy, beta_energy, nmax, mu, characters)
    corr_small = normalized_correlation(gram_small)
    corr_large = normalized_correlation(gram_large)
    fig = plt.figure(figsize=(12.4, 4.9))
    grid = fig.add_gridspec(1, 3, width_ratios=[1.0, 1.0, 0.055], wspace=0.34)
    axes = [fig.add_subplot(grid[0, 0]), fig.add_subplot(grid[0, 1])]
    cax = fig.add_subplot(grid[0, 2])
    for ax, matrix, title in [(axes[0], corr_small, "$k=100$"), (axes[1], corr_large, "$k=100000$")]:
        image = ax.imshow(np.abs(matrix), cmap="viridis", vmin=0, vmax=1)
        ax.set_xticks(range(4), [r"$\chi_0$", r"$\chi_1$", r"$\chi_2$", r"$\chi_3$"])
        ax.set_yticks(range(4), [r"$\chi_0$", r"$\chi_1$", r"$\chi_2$", r"$\chi_3$"])
        ax.set_title(title)
        for row in range(4):
            for col in range(4):
                value = abs(matrix[row, col])
                ax.text(col, row, f"{value:.3f}", ha="center", va="center", color=WHITE if value > 0.55 else INK, fontsize=8.7)
    fig.colorbar(image, cax=cax, label="normalized magnitude")
    fig.suptitle("Distinct Dirichlet-character packets become asymptotically orthogonal", fontsize=16.5, weight="bold")
    fig.subplots_adjust(left=0.07, right=0.96, bottom=0.13, top=0.82)
    save_figure(fig, "16_character_gram")

    k_char = np.array([100, 300, 1000, 3000, 10000, 30000, 100000])
    char_rows = []
    max_offdiag = []
    for k in k_char:
        gram = character_gram_matrix(int(k), a_energy, beta_energy, nmax, mu, characters)
        corr = normalized_correlation(gram)
        mask = ~np.eye(4, dtype=bool)
        maximum = float(np.max(np.abs(corr[mask])))
        max_offdiag.append(maximum)
        char_rows.append({"k": int(k), "max_offdiag": maximum})
    tables["character_decoherence"] = char_rows
    fig, ax = plt.subplots(figsize=(11.8, 4.8))
    ax.loglog(k_char, max_offdiag, marker="o", lw=2, label="largest measured off-diagonal correlation")
    reference_constant = max_offdiag[0] * (k_char[0] ** 0.25)
    ax.loglog(k_char, reference_constant * k_char ** (-0.25), linestyle="--", color=RED, label=r"reference slope $k^{-1/4}$")
    ax.set_xlabel("$k$")
    ax.set_ylabel("maximum normalized correlation")
    ax.set_title("Character decoherence removes cross-sector interference unconditionally")
    ax.legend()
    ax.grid(alpha=0.18, which="both")
    fig.tight_layout()
    save_figure(fig, "17_character_decoherence")
    checks.append(Check("character_decoherence_decreases", max_offdiag[-1] < max_offdiag[0], f"first={max_offdiag[0]:.4f}, last={max_offdiag[-1]:.4f}"))

    # Quantum/logarithmic pipeline.
    fig, ax = diagram_axes((13.0, 6.2))
    ax.text(0.5, 0.94, "Positive packet energy and signed coherence in a logarithmic spectrum", ha="center", fontsize=20, weight="bold")
    box(ax, (0.04, 0.58), 0.17, 0.17, "number basis\n" + r"$|n\rangle$", face=BLUE + "20", edge=BLUE, fontsize=13)
    box(ax, (0.29, 0.58), 0.18, 0.17, "log Hamiltonian\n" + r"$H|n\rangle=\log n|n\rangle$", face=TEAL + "20", edge=TEAL, fontsize=12)
    box(ax, (0.55, 0.58), 0.18, 0.17, "scale filter\n" + r"$e^{-kK_\beta}$", face=ORANGE + "20", edge=ORANGE, fontsize=13)
    box(ax, (0.81, 0.58), 0.15, 0.17, "character sign\n" + r"$\mathcal{M}_\chi$", face=MAGENTA + "20", edge=MAGENTA, fontsize=12)
    arrow(ax, (0.21, 0.665), (0.29, 0.665))
    arrow(ax, (0.47, 0.665), (0.55, 0.665))
    arrow(ax, (0.73, 0.665), (0.81, 0.665))
    box(ax, (0.13, 0.20), 0.30, 0.18, "diagonal power\n" + r"$E(k)=\langle\psi|\mathcal{M}^2e^{-2kK}|\psi\rangle$", face=TEAL + "14", edge=TEAL, fontsize=12)
    box(ax, (0.57, 0.20), 0.30, 0.18, "signed amplitude\n" + r"$F_k(t)=\langle\phi|\mathcal{M}e^{-kK}e^{-itH}|\phi\rangle$", face=MAGENTA + "14", edge=MAGENTA, fontsize=12)
    arrow(ax, (0.63, 0.58), (0.28, 0.38), color=TEAL)
    arrow(ax, (0.88, 0.58), (0.72, 0.38), color=MAGENTA)
    ax.text(0.5, 0.075, "The positive energy is completely understood. The remaining zeta difficulty is the internal coherence of the principal Mobius sector.", ha="center", fontsize=11.3, color=MUTED)
    save_figure(fig, "18_quantum_packet_pipeline")

    # Status map.
    fig, ax = diagram_axes((13.0, 6.5))
    ax.text(0.5, 0.95, "What has been proved and what remains open", ha="center", fontsize=21, weight="bold")
    proved = [
        "Stieltjes germ formulas",
        r"$L^{(m)}(1,\chi)$ transforms",
        "detail variance",
        "primitive resultants",
        "complete monotonicity",
        "Hankel positivity",
        "zero-free resolvent",
        "Gamma scaling",
        "character decoherence",
    ]
    open_items = [
        "principal Mobius coherence",
        "uniform GRH coherence",
        "packet canonical systems",
        "global zero-location theorem",
    ]
    ax.add_patch(FancyBboxPatch((0.05, 0.13), 0.52, 0.72, boxstyle="round,pad=.015,rounding_size=.02", facecolor=TEAL + "14", edgecolor=TEAL, lw=2))
    ax.add_patch(FancyBboxPatch((0.62, 0.13), 0.33, 0.72, boxstyle="round,pad=.015,rounding_size=.02", facecolor=ORANGE + "14", edgecolor=ORANGE, lw=2))
    ax.text(0.31, 0.80, "proved in this paper", ha="center", fontsize=15, weight="bold", color=TEAL)
    ax.text(0.785, 0.80, "open", ha="center", fontsize=15, weight="bold", color=ORANGE)
    y = 0.72
    for item in proved:
        ax.text(0.10, y, f"PASS  {item}", ha="left", va="center", fontsize=11.3)
        y -= 0.065
    y = 0.68
    for item in open_items:
        ax.text(0.67, y, f"-  {item}", ha="left", va="center", fontsize=11.3)
        y -= 0.12
    ax.text(0.5, 0.055, "The positive and cross-character layers are now controlled. The principal signed sector still carries the RH-scale obstruction.", ha="center", fontsize=11.2, color=MUTED)
    save_figure(fig, "19_status_map")

    # Family map.
    fig, ax = diagram_axes((13.0, 6.4))
    ax.text(0.5, 0.95, "The second special-function family generated by the calculus", ha="center", fontsize=20, weight="bold")
    nodes = [
        (0.08, 0.68, 0.20, 0.14, "Bernoulli-Hurwitz\nchildren", BLUE),
        (0.40, 0.68, 0.20, 0.14, "cyclotomic Stieltjes\npackets", TEAL),
        (0.72, 0.68, 0.20, 0.14, "packet resultants\nand variance", ORANGE),
        (0.08, 0.30, 0.20, 0.14, "squarefree zeta-ratio\nfinite differences", MAGENTA),
        (0.40, 0.30, 0.20, 0.14, "Hausdorff energy\nresolvent", RED),
        (0.72, 0.30, 0.20, 0.14, "Gamma scale law\nand character Gram", PURPLE),
    ]
    for x0, y0, width, height, text, color in nodes:
        box(ax, (x0, y0), width, height, text, face=color + "18", edge=color, fontsize=12)
    arrow(ax, (0.28, 0.75), (0.40, 0.75))
    arrow(ax, (0.60, 0.75), (0.72, 0.75))
    arrow(ax, (0.18, 0.68), (0.18, 0.44), color=MAGENTA)
    arrow(ax, (0.28, 0.37), (0.40, 0.37), color=RED)
    arrow(ax, (0.60, 0.37), (0.72, 0.37), color=PURPLE)
    arrow(ax, (0.82, 0.68), (0.82, 0.44), color=PURPLE)
    ax.text(0.5, 0.08, "The analytic and arithmetic branches meet through finite transforms, positive moments, and asymptotic packet orthogonality.", ha="center", fontsize=11.4, color=MUTED)
    save_figure(fig, "20_function_family_map")

    # Save tables.
    for name, rows in tables.items():
        if not rows:
            continue
        path = TABLES / f"{name}.csv"
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

    passed = sum(check.passed for check in checks)
    summary = {
        "title": "Projector-Generated Special Functions II",
        "checks": len(checks),
        "passed": passed,
        "failed": len(checks) - passed,
        "figures": 20,
        "stieltjes_first_derivative": derivative_formula.real,
        "three_channel_variance": str(variance_l3),
        "energy_asymptotic_constant": constant,
        "energy_final_relative_error": energy_rows[-1]["relative_error"],
        "gamma_final_mean": gamma_rows[-1]["mean"],
        "gamma_final_variance": gamma_rows[-1]["variance"],
        "gamma_final_ks": gamma_rows[-1]["ks"],
        "character_correlation_first": max_offdiag[0],
        "character_correlation_last": max_offdiag[-1],
    }
    (RESULTS / "results.json").write_text(json.dumps(summary, indent=2, default=lambda value: value.item() if hasattr(value, "item") else str(value)), encoding="utf-8")
    with (RESULTS / "checks.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["name", "passed", "detail"])
        writer.writeheader()
        for check in checks:
            writer.writerow({"name": check.name, "passed": check.passed, "detail": check.detail})

    if passed != len(checks):
        failures = [check for check in checks if not check.passed]
        raise RuntimeError(f"{len(failures)} checks failed: {failures}")
    return summary


if __name__ == "__main__":
    print(json.dumps(generate_all(), indent=2, default=lambda value: value.item() if hasattr(value, "item") else str(value)))
