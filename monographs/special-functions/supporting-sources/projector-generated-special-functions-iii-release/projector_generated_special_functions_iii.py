from __future__ import annotations

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
from scipy.special import eval_genlaguerre, gamma as gamma_fn, roots_genlaguerre

mp.mp.dps = 80

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
    fontsize: float = 11.0,
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
            fontsize=10.0,
            color=color,
        )


# ---------------------------------------------------------------------------
# Arithmetic helpers and squarefree packet measure
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
            value = i * p
            if value > nmax:
                break
            composite[value] = True
            if i % p == 0:
                mu[value] = 0
                break
            mu[value] = -mu[i]
    return mu


def prime_factors(n: int) -> list[int]:
    factors: list[int] = []
    remaining = n
    p = 2
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


@dataclass(frozen=True)
class PacketParameters:
    a: float = 2.0
    beta: float = 2.0
    conductor: int = 1

    @property
    def alpha(self) -> float:
        return (2.0 * self.a - 1.0) / self.beta

    @property
    def density(self) -> float:
        return squarefree_coprime_density(self.conductor)

    @property
    def energy_constant(self) -> float:
        return self.density / self.beta * float(gamma_fn(self.alpha)) * 2.0 ** (-self.alpha)


@dataclass
class PacketMeasure:
    params: PacketParameters
    n: np.ndarray
    x: np.ndarray
    w: np.ndarray

    def energy(self, k: int) -> float:
        if k == 0:
            return float(np.sum(self.w))
        logx = np.log(self.x, where=self.x > 0, out=np.full_like(self.x, -np.inf))
        return float(np.sum(self.w * np.exp(k * logx)))

    def energies(self, ks: Sequence[int]) -> np.ndarray:
        logx = np.log(self.x, where=self.x > 0, out=np.full_like(self.x, -np.inf))
        values = []
        for k in ks:
            if k == 0:
                values.append(float(np.sum(self.w)))
            else:
                values.append(float(np.sum(self.w * np.exp(k * logx))))
        return np.array(values, dtype=float)

    def tilted_probabilities(self, k: int) -> np.ndarray:
        logx = np.log(self.x, where=self.x > 0, out=np.full_like(self.x, -np.inf))
        raw = self.w * np.exp(k * logx)
        return raw / np.sum(raw)

    def scaled_u(self, k: int) -> np.ndarray:
        return k * (1.0 - self.x)


def build_measure(params: PacketParameters, nmax: int = 1_500_000) -> PacketMeasure:
    mu = mobius_sieve(nmax)
    n = np.arange(1, nmax + 1, dtype=np.float64)
    mask = mu[1:] != 0
    if params.conductor > 1:
        mask &= np.gcd(np.arange(1, nmax + 1), params.conductor) == 1
    n = n[mask]
    x = (1.0 - n ** (-params.beta)) ** 2
    w = n ** (-2.0 * params.a)
    return PacketMeasure(params=params, n=n, x=x, w=w)


def exact_energy_zeta_ratio(k: int, a: int = 2, beta: int = 2, dps: int = 100) -> mp.mpf:
    mp.mp.dps = dps
    total = mp.mpf("0")
    for j in range(2 * k + 1):
        s = 2 * a + beta * j
        d = mp.zeta(s) / mp.zeta(2 * s)
        total += (-1) ** j * mp.binomial(2 * k, j) * d
    return total


# ---------------------------------------------------------------------------
# Lanczos and orthogonal packet polynomials
# ---------------------------------------------------------------------------


@dataclass
class LanczosResult:
    diagonal: np.ndarray
    off_diagonal: np.ndarray
    vectors: np.ndarray | None = None

    def jacobi(self) -> np.ndarray:
        size = self.diagonal.size
        matrix = np.diag(self.diagonal.copy())
        if size > 1:
            matrix += np.diag(self.off_diagonal, 1)
            matrix += np.diag(self.off_diagonal, -1)
        return matrix


def lanczos_diagonal(
    nodes: np.ndarray,
    seed: np.ndarray,
    steps: int,
    keep_vectors: bool = False,
    reorthogonalize: bool = True,
) -> LanczosResult:
    norm = float(np.linalg.norm(seed))
    if norm == 0:
        raise ValueError("seed must be nonzero")
    q = seed.astype(float) / norm
    q_previous = np.zeros_like(q)
    beta_previous = 0.0
    diagonals: list[float] = []
    off_diagonals: list[float] = []
    vectors: list[np.ndarray] = []
    for index in range(steps):
        if keep_vectors or reorthogonalize:
            vectors.append(q.copy())
        residual = nodes * q - beta_previous * q_previous
        alpha = float(np.dot(q, residual))
        residual = residual - alpha * q
        if reorthogonalize:
            for old in vectors:
                residual -= float(np.dot(old, residual)) * old
        diagonals.append(alpha)
        if index == steps - 1:
            break
        beta = float(np.linalg.norm(residual))
        if beta < 1e-15:
            break
        off_diagonals.append(beta)
        q_previous = q
        q = residual / beta
        beta_previous = beta
    vector_array = np.vstack(vectors) if keep_vectors else None
    return LanczosResult(np.array(diagonals), np.array(off_diagonals), vector_array)


def global_lanczos(measure: PacketMeasure, steps: int) -> LanczosResult:
    return lanczos_diagonal(measure.x, np.sqrt(measure.w), steps)


def tilted_lanczos(measure: PacketMeasure, k: int, steps: int) -> LanczosResult:
    probabilities = measure.tilted_probabilities(k)
    nodes = measure.scaled_u(k)
    return lanczos_diagonal(nodes, np.sqrt(probabilities), steps)


def monic_polynomials_from_jacobi(result: LanczosResult, degree: int) -> list[np.ndarray]:
    polynomials: list[np.ndarray] = [np.array([1.0])]
    if degree == 0:
        return polynomials
    polynomials.append(np.array([-result.diagonal[0], 1.0]))
    for m in range(1, degree):
        current = polynomials[m]
        previous = polynomials[m - 1]
        shifted = np.pad(current, (1, 0))
        alpha_term = result.diagonal[m] * np.pad(current, (0, 1))
        beta_sq = result.off_diagonal[m - 1] ** 2
        previous_term = beta_sq * np.pad(previous, (0, 2))
        polynomials.append(shifted - alpha_term - previous_term)
    return polynomials


def monic_laguerre_coefficients(degree: int, alpha: float) -> np.ndarray:
    # (-1)^m m! L_m^{(alpha-1)}(u), returned in ascending powers.
    grid = np.arange(degree + 1, dtype=float)
    values = (-1.0) ** degree * math.factorial(degree) * eval_genlaguerre(degree, alpha - 1.0, grid)
    vandermonde = np.vander(grid, N=degree + 1, increasing=True)
    return np.linalg.solve(vandermonde, values)


def polynomial_values(coefficients: np.ndarray, x: np.ndarray) -> np.ndarray:
    return np.polynomial.polynomial.polyval(x, coefficients)


def gamma_laguerre_norm(degree: int, alpha: float) -> float:
    return math.factorial(degree) * float(mp.rf(alpha, degree))


def laguerre_jacobi(alpha: float, steps: int) -> np.ndarray:
    diagonal = np.array([2.0 * m + alpha for m in range(steps)], dtype=float)
    off = np.array([math.sqrt((m + 1.0) * (m + alpha)) for m in range(steps - 1)], dtype=float)
    matrix = np.diag(diagonal)
    if steps > 1:
        matrix += np.diag(off, 1) + np.diag(off, -1)
    return matrix


# ---------------------------------------------------------------------------
# Determinants, quadrature, and resolvent approximants
# ---------------------------------------------------------------------------


def gamma_moment(order: int, alpha: float) -> float:
    return float(mp.rf(alpha, order))


def tilted_moments(measure: PacketMeasure, k: int, max_order: int) -> np.ndarray:
    p = measure.tilted_probabilities(k)
    u = measure.scaled_u(k)
    return np.array([float(np.sum(p * u ** r)) for r in range(max_order + 1)])


def hankel_matrix(moments: Sequence[float], degree: int) -> np.ndarray:
    return np.array([[moments[i + j] for j in range(degree + 1)] for i in range(degree + 1)], dtype=float)


def gamma_hankel_constant(degree: int, alpha: float) -> float:
    value = 1.0
    for j in range(degree + 1):
        value *= math.factorial(j) * float(mp.rf(alpha, j))
    return value


def hankel_asymptotic_ratio(measure: PacketMeasure, k: int, degree: int) -> float:
    moments = tilted_moments(measure, k, 2 * degree)
    determinant = float(np.linalg.det(hankel_matrix(moments, degree)))
    return determinant / gamma_hankel_constant(degree, measure.params.alpha)


def gauss_quadrature(result: LanczosResult) -> tuple[np.ndarray, np.ndarray]:
    matrix = result.jacobi()
    eigenvalues, eigenvectors = np.linalg.eigh(matrix)
    # Tiny negative nodes can arise from roundoff when the exact measure has
    # support at zero.  Treat only numerical negatives as the endpoint zero.
    eigenvalues = np.where((eigenvalues < 0.0) & (eigenvalues > -1e-12), 0.0, eigenvalues)
    weights = eigenvectors[0, :] ** 2
    order = np.argsort(eigenvalues)
    return eigenvalues[order], weights[order]


def exact_resolvent(measure: PacketMeasure, z: complex) -> complex:
    return complex(np.sum(measure.w / (1.0 - z * measure.x)))


def reduced_resolvent(measure: PacketMeasure, result: LanczosResult, z: complex) -> complex:
    nodes, weights = gauss_quadrature(result)
    return complex(np.sum(measure.energy(0) * weights / (1.0 - z * nodes)))


def moment_matching_error(measure: PacketMeasure, result: LanczosResult, max_degree: int) -> np.ndarray:
    nodes, weights = gauss_quadrature(result)
    e0 = measure.energy(0)
    errors = []
    for degree in range(max_degree + 1):
        exact = measure.energy(degree)
        reduced = e0 * float(np.sum(weights * nodes ** degree))
        errors.append(abs(exact - reduced))
    return np.array(errors)


def christoffel_darboux_kernel(
    result: LanczosResult,
    u: np.ndarray,
    degree: int,
) -> np.ndarray:
    polynomials = monic_polynomials_from_jacobi(result, degree)
    norms = [1.0]
    for m in range(1, degree + 1):
        norms.append(norms[-1] * result.off_diagonal[m - 1] ** 2)
    values = [polynomial_values(poly, u) for poly in polynomials]
    kernel = np.zeros((u.size, u.size), dtype=float)
    for m in range(degree + 1):
        kernel += np.outer(values[m], values[m]) / norms[m]
    return kernel


def gamma_christoffel_kernel(alpha: float, u: np.ndarray, degree: int) -> np.ndarray:
    values = []
    norms = []
    for m in range(degree + 1):
        coeff = monic_laguerre_coefficients(m, alpha)
        values.append(polynomial_values(coeff, u))
        norms.append(gamma_laguerre_norm(m, alpha))
    kernel = np.zeros((u.size, u.size), dtype=float)
    for values_m, norm_m in zip(values, norms, strict=True):
        kernel += np.outer(values_m, values_m) / norm_m
    return kernel


# ---------------------------------------------------------------------------
# High-precision determinant and total-positivity checks
# ---------------------------------------------------------------------------


def mp_energy(k: int, dps: int = 100) -> mp.mpf:
    return exact_energy_zeta_ratio(k, dps=dps)


def generalized_hankel_minor(rows: Sequence[int], cols: Sequence[int], dps: int = 100) -> mp.mpf:
    mp.mp.dps = dps
    matrix = mp.matrix(len(rows), len(cols))
    for i, row in enumerate(rows):
        for j, col in enumerate(cols):
            matrix[i, j] = mp_energy(row + col, dps=dps)
    return mp.det(matrix)


# ---------------------------------------------------------------------------
# Figure generation
# ---------------------------------------------------------------------------


def figure_01_pipeline() -> None:
    fig, ax = diagram_axes((13.0, 6.2))
    ax.text(0.5, 0.94, "Squarefree packet measure to moment-exact reduced model", ha="center", fontsize=20, weight="bold")
    stages = [
        (0.03, "squarefree\npacket measure", BLUE),
        (0.20, "positive\ncontraction", TEAL),
        (0.37, "moments and\nHankel minors", ORANGE),
        (0.54, "Jacobi and\ncontinued fraction", MAGENTA),
        (0.71, "Gamma tilt and\nLaguerre limit", PURPLE),
        (0.87, "moment-exact\npacket reduction", RED),
    ]
    for x0, label, color in stages:
        box(ax, (x0, 0.58), 0.13, 0.17, label, face=color + "20", edge=color, fontsize=11)
    for left, right in zip(stages[:-1], stages[1:], strict=True):
        arrow(ax, (left[0] + 0.13, 0.665), (right[0], 0.665), color=INK)
    box(ax, (0.18, 0.20), 0.25, 0.16, r"$E_k=\langle v,T^k v\rangle$", face=WHITE, edge=TEAL, fontsize=15)
    box(ax, (0.57, 0.20), 0.25, 0.16, r"$J_k\longrightarrow J_{\alpha}^{\mathrm{Lag}}$", face=WHITE, edge=PURPLE, fontsize=15)
    arrow(ax, (0.305, 0.58), (0.305, 0.36), color=TEAL)
    arrow(ax, (0.695, 0.58), (0.695, 0.36), color=PURPLE)
    ax.text(0.5, 0.07, "The positive packet energy becomes a canonical spectral problem rather than a list of unrelated coefficients.", ha="center", color=MUTED, fontsize=11.5)
    save_figure(fig, "01_theory_pipeline")


def figure_02_measure(measure: PacketMeasure) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(13.0, 4.8))
    count = min(180, measure.n.size)
    axes[0].scatter(measure.x[:count], measure.w[:count], s=20, color=BLUE, alpha=0.8)
    axes[0].set_yscale("log")
    axes[0].set_xlabel(r"packet node $x_n=(1-n^{-\beta})^2$")
    axes[0].set_ylabel(r"weight $n^{-2a}$")
    axes[0].set_title("Discrete squarefree packet measure")
    axes[0].grid(alpha=0.18)
    axes[1].plot(measure.n[:count], 1.0 - measure.x[:count], color=TEAL, lw=2)
    axes[1].set_xscale("log")
    axes[1].set_yscale("log")
    axes[1].set_xlabel("squarefree integer $n$")
    axes[1].set_ylabel(r"distance $1-x_n$")
    axes[1].set_title("Nodes accumulate at the spectral edge")
    axes[1].grid(alpha=0.18, which="both")
    fig.suptitle("One compactly supported measure generates the complete positive packet theory", fontsize=17, weight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.91])
    save_figure(fig, "02_squarefree_packet_measure")


def figure_03_contraction() -> None:
    fig, ax = diagram_axes((13.0, 6.0))
    ax.text(0.5, 0.93, "Positive contraction and cyclic seed", ha="center", fontsize=21, weight="bold")
    box(ax, (0.05, 0.56), 0.19, 0.18, "number basis\n" + r"$\{|n\rangle\}$", face=BLUE + "18", edge=BLUE, fontsize=14)
    box(ax, (0.32, 0.56), 0.22, 0.18, r"$T|n\rangle=x_n|n\rangle$" + "\n" + r"$0\leq T<I$", face=TEAL + "18", edge=TEAL, fontsize=14)
    box(ax, (0.62, 0.56), 0.24, 0.18, r"$|v\rangle=\sum_n\sqrt{w_n}|n\rangle$", face=ORANGE + "18", edge=ORANGE, fontsize=13)
    arrow(ax, (0.24, 0.65), (0.32, 0.65), color=INK)
    arrow(ax, (0.54, 0.65), (0.62, 0.65), color=INK)
    box(ax, (0.14, 0.20), 0.27, 0.17, "moments\n" + r"$E_k=\langle v,T^kv\rangle$", face=WHITE, edge=MAGENTA, fontsize=14)
    box(ax, (0.58, 0.20), 0.27, 0.17, "Lanczos basis\n" + r"$T\sim J$", face=WHITE, edge=PURPLE, fontsize=14)
    arrow(ax, (0.43, 0.56), (0.285, 0.37), color=MAGENTA)
    arrow(ax, (0.72, 0.56), (0.715, 0.37), color=PURPLE)
    arrow(ax, (0.41, 0.285), (0.58, 0.285), color=INK, text="same cyclic model", text_offset=(0, 0.035))
    ax.text(0.5, 0.07, "The Jacobi matrix is the packet-normal form of the diagonal contraction on its cyclic subspace.", ha="center", fontsize=11.5, color=MUTED)
    save_figure(fig, "03_positive_contraction")


def figure_04_energy_decay(measure: PacketMeasure) -> None:
    ks = np.unique(np.round(np.logspace(0, 5, 90)).astype(int))
    values = measure.energies(ks)
    alpha = measure.params.alpha
    constant = measure.params.energy_constant
    asymptotic = constant * ks.astype(float) ** (-alpha)
    ratio = values / asymptotic
    fig, axes = plt.subplots(1, 2, figsize=(13.0, 4.8))
    axes[0].loglog(ks, values, color=BLUE, lw=2.2, label="computed energy")
    axes[0].loglog(ks, asymptotic, color=ORANGE, ls="--", lw=2, label=r"$A k^{-\alpha}$")
    axes[0].set_xlabel("packet depth $k$")
    axes[0].set_ylabel(r"$E_k$")
    axes[0].set_title("Packet-energy decay")
    axes[0].legend()
    axes[0].grid(alpha=0.18, which="both")
    axes[1].semilogx(ks, ratio, color=TEAL, lw=2.2)
    axes[1].axhline(1.0, color=INK, ls="--", lw=1)
    axes[1].set_xlabel("packet depth $k$")
    axes[1].set_ylabel("computed / asymptotic")
    axes[1].set_title("Approach to the exact leading constant")
    axes[1].grid(alpha=0.18)
    fig.suptitle("The positive energy supplies the scale law before any Mobius coherence estimate", fontsize=17, weight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.91])
    save_figure(fig, "04_energy_decay")


def figure_05_total_positivity() -> None:
    row_sets = [(0, 1), (0, 2), (1, 3), (0, 1, 2), (0, 2, 4), (1, 3, 5)]
    col_sets = [(0, 1), (0, 2), (1, 4), (0, 1, 2), (0, 2, 3), (1, 3, 5)]
    matrix = np.full((len(row_sets), len(col_sets)), np.nan)
    for i, rows in enumerate(row_sets):
        for j, cols in enumerate(col_sets):
            if len(rows) == len(cols):
                value = generalized_hankel_minor(rows, cols, dps=90)
                matrix[i, j] = math.log10(float(abs(value)))
    fig, ax = plt.subplots(figsize=(10.8, 5.8))
    masked = np.ma.masked_invalid(matrix)
    image = ax.imshow(masked, cmap="viridis", aspect="auto")
    ax.set_xticks(range(len(col_sets)), [str(value) for value in col_sets], rotation=25, ha="right")
    ax.set_yticks(range(len(row_sets)), [str(value) for value in row_sets])
    ax.set_xlabel("column exponents")
    ax.set_ylabel("row exponents")
    ax.set_title("Logarithms of selected strictly positive Hankel minors", weight="bold", fontsize=15)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            if np.isfinite(matrix[i, j]):
                ax.text(j, i, f"{matrix[i,j]:.2f}", ha="center", va="center", color=WHITE if matrix[i,j] < -2 else INK, fontsize=9)
    fig.colorbar(image, ax=ax, fraction=0.035, pad=0.02, label=r"$\log_{10}$ minor")
    fig.tight_layout()
    save_figure(fig, "05_total_positivity")


def figure_06_edge_cusp(measure: PacketMeasure) -> None:
    zs = 1.0 - np.logspace(-6, -1, 80)
    at_one = exact_resolvent(measure, 1.0)
    values = np.array([exact_resolvent(measure, float(z)).real for z in zs])
    scaled = (at_one.real - values) / np.sqrt(1.0 - zs)
    expected = 3.0 / (2.0 ** 1.5 * math.pi)
    fig, axes = plt.subplots(1, 2, figsize=(13.0, 4.8))
    axes[0].plot(zs, values, color=BLUE, lw=2.2)
    axes[0].axhline(at_one.real, color=INK, ls="--", lw=1, label=r"$\mathcal{E}(1)$")
    axes[0].set_xlabel("real $z<1$")
    axes[0].set_ylabel(r"$\mathcal{E}(z)$")
    axes[0].set_title("Finite limit at the spectral edge")
    axes[0].legend()
    axes[0].grid(alpha=0.18)
    axes[1].semilogx(1.0 - zs, scaled, color=TEAL, lw=2.2)
    axes[1].axhline(expected, color=ORANGE, ls="--", lw=2, label="predicted cusp constant")
    axes[1].invert_xaxis()
    axes[1].set_xlabel(r"$1-z$")
    axes[1].set_ylabel(r"$[\mathcal{E}(1)-\mathcal{E}(z)]/\sqrt{1-z}$")
    axes[1].set_title("Square-root edge law")
    axes[1].legend()
    axes[1].grid(alpha=0.18)
    fig.suptitle("The principal energy resolvent has a computable square-root cusp at its cut endpoint", fontsize=17, weight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.91])
    save_figure(fig, "06_edge_cusp")


def figure_07_global_jacobi(measure: PacketMeasure) -> None:
    result = global_lanczos(measure, 12)
    index = np.arange(result.diagonal.size)
    fig, axes = plt.subplots(1, 2, figsize=(13.0, 4.8))
    axes[0].plot(index, result.diagonal, marker="o", color=BLUE, lw=2, label="diagonal")
    axes[0].plot(index[1:], result.off_diagonal, marker="s", color=ORANGE, lw=2, label="off-diagonal")
    axes[0].set_xlabel("Jacobi index")
    axes[0].set_ylabel("coefficient")
    axes[0].set_title("Packet Jacobi coefficients")
    axes[0].legend()
    axes[0].grid(alpha=0.18)
    image = axes[1].imshow(result.jacobi(), cmap="coolwarm", aspect="auto")
    axes[1].set_title("Tridiagonal packet-normal operator")
    axes[1].set_xlabel("basis index")
    axes[1].set_ylabel("basis index")
    fig.colorbar(image, ax=axes[1], fraction=0.045, pad=0.03)
    fig.suptitle("Lanczos converts the diagonal number-basis contraction into one canonical Jacobi matrix", fontsize=17, weight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.91])
    save_figure(fig, "07_global_jacobi")


def figure_08_continued_fraction() -> None:
    fig, ax = diagram_axes((13.0, 5.8))
    ax.text(0.5, 0.93, "Jacobi continued fraction for the packet resolvent", ha="center", fontsize=21, weight="bold")
    labels = [r"$a_0$", r"$b_1^2$", r"$a_1$", r"$b_2^2$", r"$a_2$", r"$\cdots$"]
    xs = np.linspace(0.08, 0.86, len(labels))
    colors = [BLUE, ORANGE, TEAL, MAGENTA, PURPLE, MUTED]
    for x0, label, color in zip(xs, labels, colors, strict=True):
        box(ax, (x0, 0.48), 0.10, 0.14, label, face=color + "18", edge=color, fontsize=15)
    for x0, x1 in zip(xs[:-1], xs[1:], strict=True):
        arrow(ax, (x0 + 0.10, 0.55), (x1, 0.55), color=INK)
    ax.text(0.5, 0.30, r"$S(w)=\dfrac{1}{w-a_0-\dfrac{b_1^2}{w-a_1-\dfrac{b_2^2}{w-a_2-\cdots}}}$", ha="center", fontsize=18)
    ax.text(0.5, 0.10, "Every truncation is a positive finite packet model with real nodes and positive weights.", ha="center", fontsize=11.5, color=MUTED)
    save_figure(fig, "08_continued_fraction")


def figure_09_pade(measure: PacketMeasure) -> None:
    z = np.linspace(-4.0, 0.95, 500)
    exact = np.array([exact_resolvent(measure, complex(value)).real for value in z])
    fig, axes = plt.subplots(1, 2, figsize=(13.0, 4.8))
    axes[0].plot(z, exact, color=INK, lw=2.5, label="exact")
    errors = []
    for steps, color in zip([2, 4, 6, 8], [BLUE, TEAL, ORANGE, MAGENTA], strict=True):
        result = global_lanczos(measure, steps)
        approx = np.array([reduced_resolvent(measure, result, complex(value)).real for value in z])
        axes[0].plot(z, approx, color=color, lw=1.3, label=f"{steps}-node")
        errors.append(np.max(np.abs(approx - exact)))
    axes[0].set_xlabel("real $z<1$")
    axes[0].set_ylabel(r"$\mathcal{E}(z)$")
    axes[0].set_title("Positive rational packet approximants")
    axes[0].legend(ncol=2)
    axes[0].grid(alpha=0.18)
    axes[1].semilogy([2, 4, 6, 8], errors, marker="o", color=RED, lw=2)
    axes[1].set_xlabel("quadrature nodes")
    axes[1].set_ylabel("maximum error on plotted interval")
    axes[1].set_title("Uniform improvement with model order")
    axes[1].grid(alpha=0.18)
    fig.suptitle("The Jacobi truncations give Pade-type resolvent models without losing positivity", fontsize=17, weight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.91])
    save_figure(fig, "09_pade_approximants")


def figure_10_poles_weights(measure: PacketMeasure) -> None:
    result = global_lanczos(measure, 10)
    nodes, weights = gauss_quadrature(result)
    positive = nodes > 1e-14
    poles = 1.0 / nodes[positive]
    pole_weights = weights[positive]
    fig, axes = plt.subplots(1, 2, figsize=(13.0, 4.6))
    axes[0].scatter(poles, np.zeros_like(poles), s=80 * (pole_weights / pole_weights.max()) + 20, c=pole_weights, cmap="viridis", edgecolor=INK)
    axes[0].axvline(1.0, color=RED, ls="--", lw=1.5)
    axes[0].set_xlabel("resolvent pole $1/x_j$")
    axes[0].set_yticks([])
    axes[0].set_title(r"All finite-model poles lie on $(1,\infty)$")
    axes[0].grid(alpha=0.15, axis="x")
    axes[1].bar(np.arange(nodes.size), weights, color=TEAL, edgecolor=INK)
    axes[1].set_xlabel("quadrature packet")
    axes[1].set_ylabel("positive weight")
    axes[1].set_title("Positive spectral weights")
    axes[1].grid(alpha=0.15, axis="y")
    fig.suptitle("Pole location and weight positivity are inherited from the packet measure", fontsize=17, weight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.91])
    save_figure(fig, "10_poles_and_weights")


def figure_11_moment_matching(measure: PacketMeasure) -> None:
    fig, ax = plt.subplots(figsize=(11.5, 5.4))
    for steps, color in zip([2, 4, 6, 8], [BLUE, TEAL, ORANGE, MAGENTA], strict=True):
        result = global_lanczos(measure, steps)
        errors = moment_matching_error(measure, result, 2 * steps + 3)
        ax.semilogy(np.arange(errors.size), np.maximum(errors, 1e-18), marker="o", ms=3.5, color=color, lw=1.5, label=f"{steps}-node model")
        ax.axvline(2 * steps - 1, color=color, alpha=0.25, lw=1)
    ax.set_xlabel("moment degree")
    ax.set_ylabel("absolute moment error")
    ax.set_title("Each $m$-node packet reduction matches the first $2m$ moments", weight="bold", fontsize=15)
    ax.legend(ncol=2)
    ax.grid(alpha=0.18, which="both")
    fig.tight_layout()
    save_figure(fig, "11_moment_matching")


def figure_12_gamma_tilt(measure: PacketMeasure) -> None:
    alpha = measure.params.alpha
    k_values = [100, 10000, 1000000, 10000000]
    grid = np.linspace(0, 7.0, 300)
    gamma_density = grid ** (alpha - 1.0) * np.exp(-grid) / float(gamma_fn(alpha))
    fig, axes = plt.subplots(2, 2, figsize=(13.0, 7.0), sharex=True, sharey=True)
    for ax, k, color in zip(axes.ravel(), k_values, [BLUE, TEAL, ORANGE, MAGENTA], strict=True):
        p = measure.tilted_probabilities(k)
        u = measure.scaled_u(k)
        bins = np.linspace(0, 7.0, 65)
        histogram, edges = np.histogram(u, bins=bins, weights=p, density=True)
        centers = 0.5 * (edges[:-1] + edges[1:])
        ax.step(centers, histogram, where="mid", color=color, lw=1.8, label="packet law")
        ax.plot(grid, gamma_density, color=INK, ls="--", lw=1.7, label="Gamma limit")
        ax.set_title(f"k = {k}")
        ax.grid(alpha=0.15)
    axes[0, 0].legend()
    for ax in axes[-1, :]:
        ax.set_xlabel(r"$u=k(1-x_n)$")
    for ax in axes[:, 0]:
        ax.set_ylabel("density")
    fig.suptitle(rf"Tilted packet measures converge to $\mathrm{{Gamma}}(\alpha,1)$ with $\alpha={alpha:.1f}$", fontsize=17, weight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    save_figure(fig, "12_gamma_tilt")


def figure_13_laguerre_polynomials(measure: PacketMeasure) -> None:
    k_values = [100, 10000, 1000000]
    degrees = [1, 2, 3, 4]
    u = np.linspace(0, 8.0, 500)
    fig, axes = plt.subplots(2, 2, figsize=(13.0, 7.2))
    for ax, degree in zip(axes.ravel(), degrees, strict=True):
        limit_coeff = monic_laguerre_coefficients(degree, measure.params.alpha)
        ax.plot(u, polynomial_values(limit_coeff, u), color=INK, ls="--", lw=2.2, label="Laguerre limit")
        for k, color in zip(k_values, [BLUE, TEAL, MAGENTA], strict=True):
            result = tilted_lanczos(measure, k, degree + 1)
            coeff = monic_polynomials_from_jacobi(result, degree)[degree]
            ax.plot(u, polynomial_values(coeff, u), color=color, lw=1.2, label=f"k={k}")
        ax.set_title(f"degree {degree}")
        ax.grid(alpha=0.15)
        ax.set_ylim(-30, 55 if degree >= 3 else 20)
    axes[0, 0].legend(ncol=2, fontsize=8.5)
    for ax in axes[-1, :]:
        ax.set_xlabel("scaled packet coordinate $u$")
    fig.suptitle("Fixed-degree packet polynomials converge to monic generalized Laguerre polynomials", fontsize=17, weight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    save_figure(fig, "13_laguerre_polynomial_limit")


def figure_14_recurrence(measure: PacketMeasure) -> None:
    ks = np.unique(np.round(np.logspace(1.5, 7, 48)).astype(int))
    steps = 5
    alpha_limit = np.array([2.0 * m + measure.params.alpha for m in range(steps)])
    beta_limit = np.array([math.sqrt((m + 1.0) * (m + measure.params.alpha)) for m in range(steps - 1)])
    diagonal_errors = []
    off_errors = []
    for k in ks:
        result = tilted_lanczos(measure, int(k), steps)
        diagonal_errors.append(np.max(np.abs(result.diagonal - alpha_limit)))
        off_errors.append(np.max(np.abs(result.off_diagonal - beta_limit)))
    fig, axes = plt.subplots(1, 2, figsize=(13.0, 4.8))
    axes[0].loglog(ks, diagonal_errors, color=BLUE, lw=2, marker="o", ms=3, label="diagonal")
    axes[0].loglog(ks, off_errors, color=ORANGE, lw=2, marker="s", ms=3, label="off-diagonal")
    axes[0].set_xlabel("tilt depth $k$")
    axes[0].set_ylabel("maximum coefficient error")
    axes[0].set_title("Convergence to the Laguerre Jacobi matrix")
    axes[0].legend()
    axes[0].grid(alpha=0.18, which="both")
    result = tilted_lanczos(measure, int(ks[-1]), steps)
    x_index = np.arange(steps)
    axes[1].plot(x_index, result.diagonal, marker="o", color=BLUE, lw=2, label="packet diagonal")
    axes[1].plot(x_index, alpha_limit, marker="x", color=INK, ls="--", lw=1.5, label="Laguerre diagonal")
    axes[1].plot(x_index[:-1] + 0.5, result.off_diagonal, marker="s", color=ORANGE, lw=2, label="packet off-diagonal")
    axes[1].plot(x_index[:-1] + 0.5, beta_limit, marker="x", color=RED, ls="--", lw=1.5, label="Laguerre off-diagonal")
    axes[1].set_xlabel("Jacobi index")
    axes[1].set_ylabel("coefficient")
    axes[1].set_title(f"Coefficients at k={ks[-1]}")
    axes[1].legend(fontsize=8.5)
    axes[1].grid(alpha=0.18)
    fig.suptitle("The Gamma-Laguerre Jacobi operator is the universal local fixed point", fontsize=17, weight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.91])
    save_figure(fig, "14_recurrence_coefficients")


def figure_15_hankel_asymptotic(measure: PacketMeasure) -> None:
    ks = np.unique(np.round(np.logspace(1.8, 7, 44)).astype(int))
    fig, ax = plt.subplots(figsize=(11.5, 5.4))
    for degree, color in zip([1, 2, 3, 4], [BLUE, TEAL, ORANGE, MAGENTA], strict=True):
        ratios = [hankel_asymptotic_ratio(measure, int(k), degree) for k in ks]
        ax.semilogx(ks, ratios, color=color, lw=2, label=f"degree {degree}")
    ax.axhline(1.0, color=INK, ls="--", lw=1.2)
    ax.set_xlabel("tilt depth $k$")
    ax.set_ylabel("determinant / Gamma limit")
    ax.set_title("Scaled Hankel determinants converge to the Laguerre moment determinant", weight="bold", fontsize=15)
    ax.legend(ncol=2)
    ax.grid(alpha=0.18)
    fig.tight_layout()
    save_figure(fig, "15_hankel_determinants")


def figure_16_christoffel(measure: PacketMeasure) -> None:
    u = np.linspace(0.0, 7.0, 130)
    degree = 4
    k = 1000000
    result = tilted_lanczos(measure, k, degree + 1)
    packet = christoffel_darboux_kernel(result, u, degree)
    gamma_kernel = gamma_christoffel_kernel(measure.params.alpha, u, degree)
    diff = packet - gamma_kernel
    fig, axes = plt.subplots(1, 3, figsize=(13.0, 4.2))
    vmax = max(float(np.max(np.abs(packet))), float(np.max(np.abs(gamma_kernel))))
    im0 = axes[0].imshow(packet, cmap="viridis", origin="lower", extent=[0, 7, 0, 7], vmin=0, vmax=vmax, aspect="auto")
    axes[0].set_title("packet kernel")
    im1 = axes[1].imshow(gamma_kernel, cmap="viridis", origin="lower", extent=[0, 7, 0, 7], vmin=0, vmax=vmax, aspect="auto")
    axes[1].set_title("Laguerre kernel")
    lim = float(np.max(np.abs(diff)))
    im2 = axes[2].imshow(diff, cmap="coolwarm", origin="lower", extent=[0, 7, 0, 7], vmin=-lim, vmax=lim, aspect="auto")
    axes[2].set_title("difference")
    for ax in axes:
        ax.set_xlabel("u")
        ax.set_ylabel("v")
    fig.colorbar(im1, ax=axes[:2], fraction=0.022, pad=0.02, label="kernel value")
    fig.colorbar(im2, ax=axes[2], fraction=0.045, pad=0.03, label="difference")
    fig.suptitle(f"Christoffel-Darboux kernel convergence at k={k}", fontsize=17, weight="bold")
    fig.subplots_adjust(left=0.06, right=0.94, bottom=0.16, top=0.84, wspace=0.30)
    save_figure(fig, "16_christoffel_darboux")


def figure_17_gauss_nodes(measure: PacketMeasure) -> None:
    degree = 6
    alpha = measure.params.alpha
    laguerre_nodes, laguerre_weights = roots_genlaguerre(degree, alpha - 1.0)
    laguerre_weights = laguerre_weights / gamma_fn(alpha)
    ks = [100, 10000, 1000000, 10000000]
    fig, axes = plt.subplots(1, 2, figsize=(13.0, 4.8))
    for k, color in zip(ks, [BLUE, TEAL, ORANGE, MAGENTA], strict=True):
        result = tilted_lanczos(measure, k, degree)
        nodes, weights = gauss_quadrature(result)
        axes[0].plot(laguerre_nodes, nodes - laguerre_nodes, marker="o", color=color, lw=1.5, label=f"k={k}")
        axes[1].plot(laguerre_weights, weights - laguerre_weights, marker="s", color=color, lw=1.5, label=f"k={k}")
    axes[0].axhline(0, color=INK, ls="--", lw=1)
    axes[0].set_xlabel("Laguerre node")
    axes[0].set_ylabel("packet node minus limit")
    axes[0].set_title("Quadrature-node convergence")
    axes[0].grid(alpha=0.18)
    axes[1].axhline(0, color=INK, ls="--", lw=1)
    axes[1].set_xlabel("Laguerre weight")
    axes[1].set_ylabel("packet weight minus limit")
    axes[1].set_title("Quadrature-weight convergence")
    axes[1].grid(alpha=0.18)
    axes[0].legend(fontsize=8.5)
    fig.suptitle("Packet Gauss quadrature converges to normalized Gauss-Laguerre quadrature", fontsize=17, weight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.91])
    save_figure(fig, "17_gauss_laguerre_limit")


def figure_18_reduction() -> None:
    fig, ax = diagram_axes((13.0, 6.2))
    ax.text(0.5, 0.94, "Moment-exact packet reduction", ha="center", fontsize=21, weight="bold")
    box(ax, (0.05, 0.57), 0.22, 0.18, "infinite diagonal\npacket operator T", face=BLUE + "18", edge=BLUE, fontsize=13)
    box(ax, (0.38, 0.57), 0.22, 0.18, "m-step Lanczos\npacket basis", face=TEAL + "18", edge=TEAL, fontsize=13)
    box(ax, (0.71, 0.57), 0.22, 0.18, r"$m\times m$ Jacobi" + "\n" + r"model $J_m$", face=ORANGE + "18", edge=ORANGE, fontsize=13)
    arrow(ax, (0.27, 0.66), (0.38, 0.66), color=INK)
    arrow(ax, (0.60, 0.66), (0.71, 0.66), color=INK)
    box(ax, (0.12, 0.22), 0.31, 0.16, "exact moments\n" + r"$\langle v,T^rv\rangle$", face=WHITE, edge=MAGENTA, fontsize=14)
    box(ax, (0.57, 0.22), 0.31, 0.16, "reduced moments\n" + r"$E_0 e_1^T J_m^r e_1$", face=WHITE, edge=PURPLE, fontsize=14)
    arrow(ax, (0.27, 0.57), (0.275, 0.38), color=MAGENTA)
    arrow(ax, (0.82, 0.57), (0.725, 0.38), color=PURPLE)
    arrow(ax, (0.43, 0.30), (0.57, 0.30), color=INK, text=r"equal for $0\leq r\leq 2m-1$", text_offset=(0, 0.045))
    ax.text(0.5, 0.08, "The reduction preserves the declared moment contract without materializing the full diagonal operator.", ha="center", color=MUTED, fontsize=11.5)
    save_figure(fig, "18_moment_exact_reduction")


def figure_19_parameter_map() -> None:
    a_values = np.linspace(0.55, 3.5, 160)
    beta_values = np.linspace(0.4, 4.0, 170)
    aa, bb = np.meshgrid(a_values, beta_values)
    alpha = (2.0 * aa - 1.0) / bb
    fig, ax = plt.subplots(figsize=(11.0, 5.8))
    image = ax.imshow(alpha, origin="lower", extent=[a_values.min(), a_values.max(), beta_values.min(), beta_values.max()], aspect="auto", cmap="viridis", vmin=0, vmax=4)
    contours = ax.contour(aa, bb, alpha, levels=[0.5, 1.0, 1.5, 2.0, 3.0], colors=WHITE, linewidths=0.9)
    ax.clabel(contours, inline=True, fontsize=8, fmt=r"$\alpha=%.1f$")
    ax.scatter([2.0], [2.0], color=RED, s=70, edgecolor=INK, label="principal RH parameters")
    ax.set_xlabel("power parameter $a$")
    ax.set_ylabel(r"filter parameter $\beta$")
    ax.set_title(r"Universality class $\alpha=(2a-1)/\beta$", weight="bold", fontsize=15)
    ax.legend(loc="upper right")
    fig.colorbar(image, ax=ax, fraction=0.035, pad=0.02, label=r"Gamma shape $\alpha$")
    fig.tight_layout()
    save_figure(fig, "19_parameter_universality")


def figure_20_dependency() -> None:
    fig, ax = diagram_axes((13.0, 6.2))
    ax.text(0.5, 0.94, "Dependency map of the proved theory", ha="center", fontsize=21, weight="bold")
    nodes = [
        (0.08, 0.70, "positive packet\nmeasure", BLUE),
        (0.34, 0.70, "strict total\npositivity", TEAL),
        (0.60, 0.70, "Jacobi and\ncontinued fraction", ORANGE),
        (0.82, 0.70, "positive Pade\nmodels", MAGENTA),
        (0.20, 0.31, "Gamma tilting", PURPLE),
        (0.48, 0.31, "Laguerre\nuniversality", RED),
        (0.76, 0.31, "moment-exact\nreduction", YELLOW),
    ]
    for x0, y0, label, color in nodes:
        box(ax, (x0, y0), 0.16, 0.13, label, face=color + "18", edge=color, fontsize=11)
    links = [(0, 1), (1, 2), (2, 3), (0, 4), (4, 5), (2, 6), (5, 6)]
    centers = [(x + 0.08, y + 0.065) for x, y, _, _ in nodes]
    for source, target in links:
        arrow(ax, centers[source], centers[target], color=INK)
    ax.text(0.5, 0.08, "The principal Mobius coherence problem enters only after this positive structure has been completed.", ha="center", fontsize=11.5, color=MUTED)
    save_figure(fig, "20_dependency_map")


def figure_21_boundary() -> None:
    fig, ax = diagram_axes((13.0, 5.9))
    ax.text(0.5, 0.93, "Status boundary", ha="center", fontsize=21, weight="bold")
    box(ax, (0.06, 0.47), 0.39, 0.28, "proved\n\npositive measure\ntotal positivity\nJacobi model\nLaguerre fixed point\npositive quadrature", face=TEAL + "20", edge=TEAL, fontsize=12)
    box(ax, (0.55, 0.47), 0.39, 0.28, "open\n\nprincipal Mobius coherence\nsubpolynomial signed synthesis\nRH and GRH consequences", face=ORANGE + "20", edge=ORANGE, fontsize=12)
    arrow(ax, (0.45, 0.61), (0.55, 0.61), color=INK, text="does not follow automatically", text_offset=(0, 0.05))
    ax.text(0.5, 0.19, r"$E_k$ controls the diagonal packet energy.  RH requires a new estimate for the signed off-diagonal coherence.", ha="center", fontsize=13)
    ax.text(0.5, 0.07, "The positive theory narrows the problem but does not prove the missing arithmetic cancellation.", ha="center", fontsize=11.5, color=MUTED)
    save_figure(fig, "21_status_boundary")


def figure_22_family_map() -> None:
    fig, ax = diagram_axes((13.0, 6.4))
    ax.text(0.5, 0.95, "Projector-generated function family III", ha="center", fontsize=21, weight="bold")
    center = (0.5, 0.54)
    ax.add_patch(Circle(center, 0.105, facecolor=BLUE + "25", edgecolor=BLUE, lw=2))
    ax.text(center[0], center[1], "squarefree\npacket measure", ha="center", va="center", fontsize=13, weight="bold")
    leaves = [
        (0.15, 0.77, "Stieltjes\nresolvent", TEAL),
        (0.50, 0.82, "Jacobi\nfunction", ORANGE),
        (0.84, 0.77, "Pade packet\nmodels", MAGENTA),
        (0.16, 0.28, "Hankel\ndeterminants", RED),
        (0.50, 0.18, "Laguerre\nfixed point", PURPLE),
        (0.84, 0.28, "Gauss packet\nquadrature", YELLOW),
    ]
    for x0, y0, label, color in leaves:
        ax.add_patch(Circle((x0, y0), 0.085, facecolor=color + "22", edgecolor=color, lw=1.7))
        ax.text(x0, y0, label, ha="center", va="center", fontsize=10.5)
        arrow(ax, center, (x0, y0), color=color)
    ax.text(0.5, 0.04, "All six objects are generated from one moment seed and linked by exact transforms.", ha="center", fontsize=11.5, color=MUTED)
    save_figure(fig, "22_function_family_map")


# ---------------------------------------------------------------------------
# Tables and checks
# ---------------------------------------------------------------------------


def write_csv(path: Path, rows: Iterable[dict[str, object]], fieldnames: Sequence[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def run_checks(measure: PacketMeasure) -> list[dict[str, object]]:
    checks: list[dict[str, object]] = []

    def record(name: str, passed: bool, value: object) -> None:
        checks.append({"check": name, "passed": bool(passed), "value": value})

    # Low-order agreement with the exact zeta-ratio formula.
    for k in range(6):
        direct = measure.energy(k)
        exact = float(exact_energy_zeta_ratio(k, dps=100))
        record(f"energy_zeta_ratio_{k}", abs(direct - exact) < 2e-11, abs(direct - exact))

    # Complete monotonicity for a finite rectangle of orders.
    energies = measure.energies(range(40))
    current = energies.copy()
    minimum_signed = float("inf")
    for order in range(8):
        if order > 0:
            current = np.diff(current)
        signed = ((-1) ** order) * current
        minimum_signed = min(minimum_signed, float(np.min(signed)))
    record("complete_monotonicity", minimum_signed > -2e-14, minimum_signed)

    # Selected total-positive minors.
    minor_specs = [
        ((0, 1), (0, 1)),
        ((0, 2), (1, 3)),
        ((0, 1, 2), (0, 1, 2)),
        ((0, 2, 4), (1, 3, 5)),
    ]
    for index, (rows, cols) in enumerate(minor_specs):
        value = generalized_hankel_minor(rows, cols, dps=100)
        record(f"total_positive_minor_{index}", value > 0, mp.nstr(value, 12))

    # Global Jacobi spectrum and positive quadrature.
    global_result = global_lanczos(measure, 10)
    nodes, weights = gauss_quadrature(global_result)
    record("global_jacobi_nodes", bool(np.all((nodes > -1e-12) & (nodes < 1.0 + 1e-12))), [float(nodes.min()), float(nodes.max())])
    record("positive_quadrature_weights", bool(np.all(weights > 0)), float(weights.min()))

    errors = moment_matching_error(measure, global_result, 19)
    record("moment_exact_reduction", float(np.max(errors[:20])) < 3e-11, float(np.max(errors[:20])))

    # Resolvent approximation and pole location.
    approx_error = abs(exact_resolvent(measure, -1.0) - reduced_resolvent(measure, global_result, -1.0))
    record("resolvent_reduction", approx_error < 5e-11, approx_error)
    positive_nodes = nodes[nodes > 1e-14]
    record(
        "poles_outside_unit_cut",
        bool(np.all(positive_nodes < 1.0) and np.all(nodes >= -1e-12)),
        float(np.min(1.0 / positive_nodes)),
    )

    # Gamma moments and Laguerre recurrence.
    gamma_tolerances = {1000: 0.10, 10000: 0.10, 100000: 0.03, 1000000: 0.02, 10000000: 0.01}
    for k, tolerance in gamma_tolerances.items():
        moments = tilted_moments(measure, k, 6)
        target = np.array([gamma_moment(r, measure.params.alpha) for r in range(7)])
        relative = np.max(np.abs(moments - target) / np.maximum(1.0, target))
        record(f"gamma_moments_{k}", relative < tolerance, float(relative))

    tilted = tilted_lanczos(measure, 10000000, 6)
    diag_target = np.array([2.0 * m + measure.params.alpha for m in range(6)])
    off_target = np.array([math.sqrt((m + 1.0) * (m + measure.params.alpha)) for m in range(5)])
    record("laguerre_diagonal", float(np.max(np.abs(tilted.diagonal - diag_target))) < 0.05, float(np.max(np.abs(tilted.diagonal - diag_target))))
    record("laguerre_off_diagonal", float(np.max(np.abs(tilted.off_diagonal - off_target))) < 0.03, float(np.max(np.abs(tilted.off_diagonal - off_target))))

    for degree in [1, 2, 3, 4]:
        ratio = hankel_asymptotic_ratio(measure, 1000000, degree)
        record(f"hankel_limit_{degree}", abs(ratio - 1.0) < 0.08, ratio)

    # Edge cusp constant.
    expected = 3.0 / (2.0 ** 1.5 * math.pi)
    z = 1.0 - 1e-5
    cusp = (exact_resolvent(measure, 1.0).real - exact_resolvent(measure, z).real) / math.sqrt(1.0 - z)
    record("edge_cusp", abs(cusp / expected - 1.0) < 0.03, cusp)

    # Christoffel-Darboux and Gauss-Laguerre convergence.
    degree = 5
    k = 10000000
    packet_result = tilted_lanczos(measure, k, degree)
    packet_nodes, packet_weights = gauss_quadrature(packet_result)
    limit_nodes, limit_weights = roots_genlaguerre(degree, measure.params.alpha - 1.0)
    limit_weights = limit_weights / gamma_fn(measure.params.alpha)
    record("gauss_nodes_limit", float(np.max(np.abs(packet_nodes - limit_nodes))) < 0.04, float(np.max(np.abs(packet_nodes - limit_nodes))))
    record("gauss_weights_limit", float(np.max(np.abs(packet_weights - limit_weights))) < 0.02, float(np.max(np.abs(packet_weights - limit_weights))))

    # Direct operator identity for selected k values.
    seed = np.sqrt(measure.w)
    for k in [0, 1, 4, 10]:
        operator_value = float(np.dot(seed, (measure.x ** k) * seed))
        record(f"operator_moment_{k}", abs(operator_value - measure.energy(k)) < 5e-14, abs(operator_value - measure.energy(k)))

    return checks


def generate_tables(measure: PacketMeasure, checks: list[dict[str, object]]) -> dict[str, object]:
    energy_rows = []
    for k in [0, 1, 2, 4, 8, 16, 100, 1000, 10000, 100000]:
        value = measure.energy(k)
        asymptotic = measure.params.energy_constant * max(k, 1) ** (-measure.params.alpha)
        energy_rows.append(
            {
                "k": k,
                "energy": f"{value:.16e}",
                "asymptotic": f"{asymptotic:.16e}",
                "ratio": f"{value / asymptotic:.10f}" if k > 0 else "-",
            }
        )
    write_csv(TABLES / "energy.csv", energy_rows, ["k", "energy", "asymptotic", "ratio"])

    global_result = global_lanczos(measure, 10)
    jacobi_rows = []
    for index, diagonal in enumerate(global_result.diagonal):
        jacobi_rows.append(
            {
                "index": index,
                "diagonal": f"{diagonal:.14f}",
                "off_diagonal": f"{global_result.off_diagonal[index]:.14f}" if index < global_result.off_diagonal.size else "-",
            }
        )
    write_csv(TABLES / "jacobi.csv", jacobi_rows, ["index", "diagonal", "off_diagonal"])

    recurrence_rows = []
    for k in [100, 10000, 1000000, 10000000]:
        result = tilted_lanczos(measure, k, 5)
        for index, diagonal in enumerate(result.diagonal):
            recurrence_rows.append(
                {
                    "k": k,
                    "index": index,
                    "diagonal": f"{diagonal:.12f}",
                    "diagonal_limit": f"{2 * index + measure.params.alpha:.12f}",
                    "off_diagonal": f"{result.off_diagonal[index]:.12f}" if index < result.off_diagonal.size else "-",
                    "off_limit": f"{math.sqrt((index + 1) * (index + measure.params.alpha)):.12f}" if index < result.off_diagonal.size else "-",
                }
            )
    write_csv(TABLES / "recurrence.csv", recurrence_rows, ["k", "index", "diagonal", "diagonal_limit", "off_diagonal", "off_limit"])

    determinant_rows = []
    for k in [100, 1000, 10000, 100000]:
        for degree in [1, 2, 3, 4]:
            determinant_rows.append(
                {
                    "k": k,
                    "degree": degree,
                    "scaled_ratio": f"{hankel_asymptotic_ratio(measure, k, degree):.12f}",
                }
            )
    write_csv(TABLES / "hankel_asymptotic.csv", determinant_rows, ["k", "degree", "scaled_ratio"])

    quadrature_rows = []
    degree = 6
    limit_nodes, limit_weights = roots_genlaguerre(degree, measure.params.alpha - 1.0)
    limit_weights = limit_weights / gamma_fn(measure.params.alpha)
    result = tilted_lanczos(measure, 10000000, degree)
    nodes, weights = gauss_quadrature(result)
    for index in range(degree):
        quadrature_rows.append(
            {
                "index": index + 1,
                "packet_node": f"{nodes[index]:.12f}",
                "laguerre_node": f"{limit_nodes[index]:.12f}",
                "packet_weight": f"{weights[index]:.12f}",
                "laguerre_weight": f"{limit_weights[index]:.12f}",
            }
        )
    write_csv(TABLES / "quadrature.csv", quadrature_rows, ["index", "packet_node", "laguerre_node", "packet_weight", "laguerre_weight"])

    pade_rows = []
    test_points = [-4.0, -1.0, -0.25, 0.5, 0.9]
    for steps in [2, 4, 6, 8, 10]:
        result = global_lanczos(measure, steps)
        for z in test_points:
            exact = exact_resolvent(measure, z)
            approximate = reduced_resolvent(measure, result, z)
            pade_rows.append(
                {
                    "nodes": steps,
                    "z": z,
                    "exact": f"{exact.real:.14f}",
                    "approximate": f"{approximate.real:.14f}",
                    "absolute_error": f"{abs(exact - approximate):.4e}",
                }
            )
    write_csv(TABLES / "pade.csv", pade_rows, ["nodes", "z", "exact", "approximate", "absolute_error"])

    write_csv(RESULTS / "checks.csv", checks, ["check", "passed", "value"])

    summary = {
        "title": "Projector-Generated Special Functions III",
        "author": "Komorebi P.",
        "parameters": {
            "a": measure.params.a,
            "beta": measure.params.beta,
            "conductor": measure.params.conductor,
            "alpha": measure.params.alpha,
            "energy_constant": measure.params.energy_constant,
        },
        "checks": len(checks),
        "passed": sum(bool(row["passed"]) for row in checks),
        "figure_pairs": 22,
        "nmax": int(measure.n[-1]),
        "edge_cusp_constant": 3.0 / (2.0 ** 1.5 * math.pi),
    }
    (RESULTS / "results.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def generate_all() -> dict[str, object]:
    params = PacketParameters(a=2.0, beta=2.0, conductor=1)
    measure = build_measure(params, nmax=1_500_000)

    figure_01_pipeline()
    figure_02_measure(measure)
    figure_03_contraction()
    figure_04_energy_decay(measure)
    figure_05_total_positivity()
    figure_06_edge_cusp(measure)
    figure_07_global_jacobi(measure)
    figure_08_continued_fraction()
    figure_09_pade(measure)
    figure_10_poles_weights(measure)
    figure_11_moment_matching(measure)
    figure_12_gamma_tilt(measure)
    figure_13_laguerre_polynomials(measure)
    figure_14_recurrence(measure)
    figure_15_hankel_asymptotic(measure)
    figure_16_christoffel(measure)
    figure_17_gauss_nodes(measure)
    figure_18_reduction()
    figure_19_parameter_map()
    figure_20_dependency()
    figure_21_boundary()
    figure_22_family_map()

    checks = run_checks(measure)
    summary = generate_tables(measure, checks)
    if summary["passed"] != summary["checks"]:
        failed = [row for row in checks if not row["passed"]]
        raise RuntimeError(f"failed checks: {failed}")
    return summary


if __name__ == "__main__":
    print(json.dumps(generate_all(), indent=2))
