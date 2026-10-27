from __future__ import annotations

import argparse
import cmath
import csv
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle
import mpmath as mp
import numpy as np
import sympy as sp
from scipy.special import gamma

mp.mp.dps = 40

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
MUTED = "#5D6D7E"
PAPER = "#FAFAF7"
GRID = "#D5D8DC"
COLORS = [BLUE, TEAL, ORANGE, MAGENTA, RED, YELLOW]

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


def complex_array(values: Iterable[complex]) -> np.ndarray:
    return np.asarray([complex(value) for value in values], dtype=np.complex128)


def mobius_sieve(nmax: int) -> np.ndarray:
    """Linear sieve for the Möbius function on 0..nmax."""
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


# ---------------------------------------------------------------------------
# General polyphase lift
# ---------------------------------------------------------------------------


def carry_matrix_symbolic(m: int, u: sp.Symbol) -> sp.Matrix:
    matrix = sp.zeros(m)
    matrix[0, m - 1] = u
    for row in range(1, m):
        matrix[row, row - 1] = 1
    return matrix


def polyphase_sections_from_coefficients(coeffs: Sequence[sp.Expr], m: int, u: sp.Symbol) -> sp.Matrix:
    sections: list[sp.Expr] = []
    for r in range(m):
        section = sp.Integer(0)
        q = 0
        index = r
        while index < len(coeffs):
            section += coeffs[index] * u**q
            q += 1
            index += m
        sections.append(sp.expand(section))
    return sp.Matrix(sections)


def reconstruct_sections(sections: Sequence[sp.Expr], m: int, z: sp.Symbol) -> sp.Expr:
    u_value = z**m
    return sp.expand(sum(z**r * sections[r].subs({sp.Symbol("u"): u_value}) for r in range(m)))


def theta_apply(section: sp.Expr, r: int, m: int, u: sp.Symbol) -> sp.Expr:
    return sp.expand(m * u * sp.diff(section, u) + r * section)


def theta_vector_apply(vector: sp.Matrix, m: int, u: sp.Symbol) -> sp.Matrix:
    return sp.Matrix([theta_apply(vector[r], r, m, u) for r in range(m)])


def exp_section_hypergeometric(m: int, r: int, u: complex) -> complex:
    params = [mp.mpf(r + j) / m for j in range(1, m + 1)]
    params = [value for value in params if abs(value - 1) > mp.mpf("1e-40")]
    return mp.hyper([], params, u / (m**m)) / mp.factorial(r)


def exp_section_series(m: int, r: int, u: complex, terms: int = 80) -> complex:
    return mp.nsum(lambda q: u**q / mp.factorial(m * q + r), [0, mp.inf]) if terms <= 0 else sum(
        mp.mpf(u) ** q / mp.factorial(m * q + r) for q in range(terms)
    )


# ---------------------------------------------------------------------------
# Bernoulli-Hurwitz packet functions and cyclotomic details
# ---------------------------------------------------------------------------


def bernoulli_interpolation(z: complex, a: complex = 1.0) -> complex:
    if abs(z) < 1e-20:
        return 1.0 + 0.0j
    zz = mp.mpc(z)
    return complex(-zz * mp.zeta(1 - zz, a))


def bernoulli_packet(z: complex, a: complex, m: int, r: int) -> complex:
    if abs(z) < 1e-20:
        return 1.0 / m
    argument = (a + r) / m
    zz = mp.mpc(z)
    return complex(-zz * (m ** (zz - 1)) * mp.zeta(1 - zz, argument))


def cyclotomic_detail(z: complex, a: complex, m: int, r: int, ell: int, j: int) -> complex:
    omega = cmath.exp(2j * math.pi / ell)
    values = [bernoulli_packet(z, a, m * ell, r + child * m) for child in range(ell)]
    return sum((omega ** (-j * child)) * values[child] for child in range(ell)) / math.sqrt(ell)


def cyclotomic_detail_lerch(z: complex, a: complex, m: int, r: int, ell: int, j: int) -> complex:
    omega = mp.e ** (2j * mp.pi / ell)
    argument = (a + r) / m
    return complex(
        -mp.mpc(z)
        / mp.sqrt(ell)
        * (m ** (mp.mpc(z) - 1))
        * mp.lerchphi(omega ** (-j), 1 - mp.mpc(z), argument)
    )


def cyclotomic_egf(t: complex, a: complex, ell: int, j: int) -> complex:
    omega = cmath.exp(2j * math.pi / ell)
    denominator = omega ** (-j) * cmath.exp(t) - 1
    if abs(t) < 1e-14 and j == 0:
        return 1 / math.sqrt(ell)
    return t * cmath.exp(a * t) / (math.sqrt(ell) * denominator)


def bernoulli_euler_channels(n: int, a: sp.Expr) -> tuple[sp.Expr, sp.Expr]:
    low = sp.bernoulli(n, a) / sp.sqrt(2)
    if n == 0:
        high = sp.Integer(0)
    else:
        high = -sp.Rational(n, 2) * sp.euler(n - 1, a) / sp.sqrt(2)
    return sp.simplify(low), sp.simplify(high)


def packet_wronskian_polynomial(n: int, x: sp.Symbol) -> sp.Expr:
    if n < 2:
        raise ValueError("n must be at least 2")
    return sp.expand(
        n * sp.bernoulli(n - 1, x) * sp.euler(n - 1, x)
        - (n - 1) * sp.bernoulli(n, x) * sp.euler(n - 2, x)
    )


# ---------------------------------------------------------------------------
# Möbius-Bernoulli transfer family
# ---------------------------------------------------------------------------


def principal_transfer_values(
    k_values: Sequence[int],
    nmax: int,
    mu: np.ndarray | None = None,
) -> dict[str, np.ndarray]:
    if mu is None:
        mu = mobius_sieve(nmax)
    n = np.arange(2, nmax + 1, dtype=np.float64)
    mu_n = mu[2:].astype(np.float64)
    log_lambda = np.log1p(-1.0 / (n * n))
    base = 1.0 / (n * n)
    squarefree = mu_n * mu_n
    c_values = []
    energy_values = []
    mass_values = []
    for k in k_values:
        weight = base * np.exp(k * log_lambda)
        c_values.append(float(np.dot(mu_n, weight)))
        energy_values.append(float(np.dot(squarefree, weight * weight)))
        mass_values.append(float(np.dot(squarefree, weight)))
    c = np.asarray(c_values)
    energy = np.asarray(energy_values)
    mass = np.asarray(mass_values)
    coherence = np.divide(c * c, energy, out=np.zeros_like(c), where=energy > 0)
    effective_dimension = np.divide(mass * mass, energy, out=np.zeros_like(mass), where=energy > 0)
    return {
        "k": np.asarray(k_values, dtype=int),
        "c": c,
        "energy": energy,
        "mass": mass,
        "coherence": coherence,
        "effective_dimension": effective_dimension,
    }


def generalized_transfer_direct(
    a: float,
    beta: float,
    k: int,
    t: float,
    nmax: int,
    mu: np.ndarray,
    character: np.ndarray | None = None,
) -> complex:
    n = np.arange(2, nmax + 1, dtype=np.float64)
    coefficients = mu[2 : nmax + 1].astype(np.complex128)
    if character is not None:
        coefficients = coefficients * character[2 : nmax + 1]
    damping = np.exp(k * np.log1p(-1.0 / np.power(n, beta)))
    phase = np.exp(-1j * t * np.log(n))
    total = np.sum(coefficients * phase * damping / np.power(n, a))
    if k == 0:
        total += 1.0
    return complex(total)


def long_time_power(
    a: float,
    beta: float,
    k: int,
    nmax: int,
    mu: np.ndarray,
    character: np.ndarray | None = None,
) -> float:
    n = np.arange(2, nmax + 1, dtype=np.float64)
    coefficients = mu[2 : nmax + 1].astype(np.complex128)
    if character is not None:
        coefficients = coefficients * character[2 : nmax + 1]
    damping = np.exp(k * np.log1p(-1.0 / np.power(n, beta)))
    values = coefficients * damping / np.power(n, a)
    total = np.sum(np.abs(values) ** 2)
    if k == 0:
        total += 1.0
    return float(total)


def quadratic_character_mod5(nmax: int) -> np.ndarray:
    values = np.zeros(nmax + 1, dtype=np.int8)
    residue_value = {0: 0, 1: 1, 2: -1, 3: -1, 4: 1}
    for n in range(1, nmax + 1):
        values[n] = residue_value[n % 5]
    return values.astype(np.complex128)


def polyphase_transfer_packets(k: int, modulus: int, nmax: int, mu: np.ndarray) -> np.ndarray:
    n = np.arange(2, nmax + 1, dtype=np.float64)
    weights = mu[2 : nmax + 1].astype(np.float64) / (n * n) * np.exp(k * np.log1p(-1.0 / (n * n)))
    packets = np.zeros(modulus, dtype=np.float64)
    residues = np.arange(2, nmax + 1) % modulus
    for residue in range(modulus):
        packets[residue] = float(np.sum(weights[residues == residue]))
    return packets


# ---------------------------------------------------------------------------
# Exact checks and tables
# ---------------------------------------------------------------------------


@dataclass
class Check:
    name: str
    passed: bool
    detail: str


def run_symbolic_checks() -> list[Check]:
    checks: list[Check] = []
    z, u = sp.symbols("z u")

    coeffs = [sp.Rational((index + 1) * (-1) ** index, index + 2) for index in range(15)]
    for m in (2, 3, 4, 5):
        sections = polyphase_sections_from_coefficients(coeffs, m, u)
        reconstruction = sp.expand(sum(z**r * sections[r].subs(u, z**m) for r in range(m)))
        original = sp.expand(sum(coeffs[index] * z**index for index in range(len(coeffs))))
        checks.append(Check(f"polynomial reconstruction M={m}", sp.simplify(reconstruction - original) == 0, "exact"))

        carry = carry_matrix_symbolic(m, u)
        theta_vector = theta_vector_apply(sections, m, u)
        theta_carry = theta_vector_apply(carry * sections, m, u)
        carry_theta = carry * theta_vector
        commutator = sp.simplify(theta_carry - carry_theta - carry * sections)
        checks.append(Check(f"Weyl commutator M={m}", all(value == 0 for value in commutator), "[Theta,C]=C"))

    for m in (2, 3, 4):
        for r in range(m):
            point = mp.mpf("0.37")
            series_value = exp_section_series(m, r, point, 80)
            hyper_value = exp_section_hypergeometric(m, r, point)
            residual = abs(series_value - hyper_value)
            checks.append(Check(f"exponential hypergeometric M={m} r={r}", residual < mp.mpf("1e-35"), f"{float(residual):.3e}"))

    a = sp.symbols("a")
    for n in range(1, 10):
        child0 = 2 ** (n - 1) * sp.bernoulli(n, a / 2)
        child1 = 2 ** (n - 1) * sp.bernoulli(n, (a + 1) / 2)
        low, high = bernoulli_euler_channels(n, a)
        low_direct = sp.simplify((child0 + child1) / sp.sqrt(2))
        high_direct = sp.simplify((child0 - child1) / sp.sqrt(2))
        checks.append(Check(f"Bernoulli low channel n={n}", sp.simplify(low_direct - low) == 0, "exact"))
        checks.append(Check(f"Euler high channel n={n}", sp.simplify(high_direct - high) == 0, "exact"))

    z0 = 0.37 + 0.41j
    a0 = 0.62
    for m in (2, 3, 4):
        reconstructed = sum(bernoulli_packet(z0, a0, m, r) for r in range(m))
        target = bernoulli_interpolation(z0, a0)
        residual = abs(reconstructed - target)
        checks.append(Check(f"Bernoulli packet reconstruction M={m}", residual < 1e-11, f"{residual:.3e}"))

    for m, ell, r in ((1, 2, 0), (2, 3, 1), (3, 2, 2)):
        parent = bernoulli_packet(z0, a0, m, r)
        children = sum(bernoulli_packet(z0, a0, m * ell, r + child * m) for child in range(ell))
        residual = abs(parent - children)
        checks.append(Check(f"Bernoulli refinement M={m} L={ell} r={r}", residual < 1e-11, f"{residual:.3e}"))

    for m, r, ell, j in ((1, 0, 3, 1), (2, 1, 4, 2), (3, 0, 2, 1)):
        direct = cyclotomic_detail(z0, a0, m, r, ell, j)
        lerch = cyclotomic_detail_lerch(z0, a0, m, r, ell, j)
        residual = abs(direct - lerch)
        checks.append(Check(f"Lerch detail M={m} L={ell} j={j}", residual < 1e-10, f"{residual:.3e}"))

    x = sp.symbols("x")
    for n in range(2, 9):
        polynomial = packet_wronskian_polynomial(n, x)
        low_n, high_n = bernoulli_euler_channels(n, x)
        low_prev, high_prev = bernoulli_euler_channels(n - 1, x)
        direct = sp.expand(4 * (low_n * high_prev - high_n * low_prev))
        checks.append(Check(f"packet Wronskian n={n}", sp.simplify(polynomial - direct) == 0, "exact"))

    return checks


def write_cyclotomic_norm_table() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for n in range(1, 15):
        children = [sp.simplify(3 ** (n - 1) * sp.bernoulli(n, sp.Rational(r, 3))) for r in range(3)]
        # D_1 = child0 + omega^2 child1 + omega child2 = A + B omega, omega^2+omega+1=0
        a_part = sp.simplify(children[0] - children[1])
        b_part = sp.simplify(-children[1] + children[2])
        norm = sp.factor(a_part**2 - a_part * b_part + b_part**2)
        rows.append(
            {
                "n": str(n),
                "child_0": str(children[0]),
                "child_1": str(children[1]),
                "child_2": str(children[2]),
                "A": str(a_part),
                "B": str(b_part),
                "norm": str(norm),
            }
        )
    with (TABLES / "cyclotomic_norms_L3.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return rows


# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------


def figure_01_polyphase_partition() -> None:
    m = 4
    degree = 31
    fig, ax = plt.subplots(figsize=(12.8, 4.8))
    for n in range(degree + 1):
        residue = n % m
        ax.add_patch(Rectangle((n - 0.42, residue - 0.32), 0.84, 0.64, facecolor=COLORS[residue] + "88", edgecolor=INK, lw=0.6))
        ax.text(n, residue, str(n), ha="center", va="center", fontsize=7.5)
    ax.set_xlim(-1, degree + 1)
    ax.set_ylim(-0.8, m - 0.2)
    ax.set_yticks(range(m), [f"packet r={r}" for r in range(m)])
    ax.set_xlabel("Taylor exponent n")
    ax.set_title("Every coefficient exponent has one polyphase address")
    ax.grid(False)
    fig.tight_layout()
    save_figure(fig, "01_polyphase_partition")


def figure_02_carry_shift() -> None:
    m = 5
    fig, ax = plt.subplots(figsize=(12.8, 5.7))
    ax.axis("off")
    y = 0.58
    xs = np.linspace(0.10, 0.90, m)
    for r, xpos in enumerate(xs):
        box = FancyBboxPatch((xpos - 0.065, y - 0.08), 0.13, 0.16, boxstyle="round,pad=.01", facecolor=COLORS[r % len(COLORS)] + "28", edgecolor=COLORS[r % len(COLORS)], lw=2)
        ax.add_patch(box)
        ax.text(xpos, y, rf"$F_{{{r}}}(u)$", ha="center", va="center", fontsize=15)
    for r in range(m - 1):
        arrow = FancyArrowPatch((xs[r] + 0.066, y), (xs[r + 1] - 0.066, y), arrowstyle="-|>", mutation_scale=13, lw=1.8, color=INK)
        ax.add_patch(arrow)
        ax.text((xs[r] + xs[r + 1]) / 2, y + 0.055, r"multiply by $z$", ha="center", fontsize=9)
    arrow = FancyArrowPatch((xs[-1], y - 0.085), (xs[0], y - 0.085), connectionstyle="arc3,rad=-0.47", arrowstyle="-|>", mutation_scale=13, lw=2.2, color=MAGENTA)
    ax.add_patch(arrow)
    ax.text(0.5, 0.15, r"wraparound contributes $uF_{M-1}(u)$ to packet $0$", ha="center", fontsize=13, color=MAGENTA)
    ax.text(0.5, 0.89, r"The carry-shift matrix $C_M(u)$ is multiplication by $z$ in packet coordinates", ha="center", fontsize=18, weight="bold")
    save_figure(fig, "02_carry_shift")


def figure_03_exp_sections() -> None:
    u = np.linspace(0, 8, 350)
    fig, axes = plt.subplots(1, 2, figsize=(13.0, 4.8))
    for m, ax in zip((2, 3), axes, strict=True):
        for r in range(m):
            values = [float(mp.re(exp_section_hypergeometric(m, r, value))) for value in u]
            ax.plot(u, values, lw=2, label=rf"$E_{{{m},{r}}}(u)$")
        ax.set_title(f"Exponential packets for M={m}")
        ax.set_xlabel("u")
        ax.set_ylabel("packet value")
        ax.grid(alpha=0.18)
        ax.legend()
    fig.suptitle("The scalar exponential becomes a vector hypergeometric function", fontsize=17, weight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    save_figure(fig, "03_exponential_sections")


def figure_04_exp_reconstruction() -> None:
    z = np.linspace(-2.5, 2.5, 500)
    fig, ax = plt.subplots(figsize=(12.8, 4.8))
    target = np.exp(z)
    for m, color in zip((2, 3, 4), (BLUE, TEAL, MAGENTA), strict=True):
        reconstruction = np.zeros_like(z)
        for r in range(m):
            reconstruction += z**r * np.asarray([float(mp.re(exp_section_hypergeometric(m, r, value**m))) for value in z])
        ax.plot(z, reconstruction - target, color=color, label=f"M={m}")
    ax.set_yscale("symlog", linthresh=1e-15)
    ax.set_xlabel("z")
    ax.set_ylabel("reconstruction residual")
    ax.set_title(r"Exact synthesis $e^z=\sum_r z^r E_{M,r}(z^M)$")
    ax.grid(alpha=0.2)
    ax.legend()
    fig.tight_layout()
    save_figure(fig, "04_exponential_reconstruction")


def figure_05_operator_lift_map() -> None:
    fig, ax = plt.subplots(figsize=(12.8, 6.0))
    ax.axis("off")
    stages = [
        (0.04, "scalar function", r"$F(z)$", BLUE),
        (0.28, "residue analysis", r"$\mathbf{F}_M(u)$", TEAL),
        (0.53, "operator lift", r"$z\mapsto C_M$\n$\theta\mapsto\Theta_M$", ORANGE),
        (0.78, "matrix system", r"$\mathcal{L}(C_M,\Theta_M)\mathbf{F}_M=0$", MAGENTA),
    ]
    for x0, title, formula, color in stages:
        box = FancyBboxPatch((x0, 0.38), 0.18, 0.25, boxstyle="round,pad=.018", facecolor=color + "24", edgecolor=color, lw=2.2)
        ax.add_patch(box)
        ax.text(x0 + 0.09, 0.57, title, ha="center", va="center", fontsize=12, weight="bold")
        ax.text(x0 + 0.09, 0.46, formula, ha="center", va="center", fontsize=13)
    for left, right in zip(stages[:-1], stages[1:], strict=True):
        ax.add_patch(FancyArrowPatch((left[0] + 0.18, 0.505), (right[0], 0.505), arrowstyle="-|>", mutation_scale=15, lw=2, color=INK))
    ax.text(0.5, 0.83, "Polyphase lifting is a representation of the same Weyl algebra", ha="center", fontsize=19, weight="bold")
    ax.text(0.5, 0.17, r"The commutator is preserved: $[\Theta_M,C_M]=C_M$", ha="center", fontsize=15, color=MUTED)
    save_figure(fig, "05_operator_lift_map")


def figure_06_bessel_sections() -> None:
    z_values = np.linspace(-8, 8, 800)
    m = 3
    # J0 Taylor coefficients up to degree 72
    coeffs = [sp.Integer(0)] * 73
    for q in range(37):
        coeffs[2 * q] = sp.Rational((-1) ** q, 4**q * math.factorial(q) ** 2)
    u_symbol = sp.Symbol("u")
    sections = polyphase_sections_from_coefficients(coeffs, m, u_symbol)
    functions = [sp.lambdify(u_symbol, section, "numpy") for section in sections]
    fig, axes = plt.subplots(m, 1, figsize=(12.8, 7.2), sharex=True)
    for r, ax in enumerate(axes):
        u_values = z_values**m
        values = np.real(functions[r](u_values))
        ax.plot(z_values, values, color=COLORS[r], lw=1.6)
        ax.set_ylabel(rf"$J_{{0;3,{r}}}$")
        ax.grid(alpha=0.16)
    axes[-1].set_xlabel("z, with packet evaluated at u=z^3")
    fig.suptitle("Three packet sections of the Bessel function J0", fontsize=17, weight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    save_figure(fig, "06_bessel_sections")


def figure_07_bernoulli_packet_reconstruction() -> None:
    a = 0.37
    z_values = np.linspace(-1.5, 2.5, 240)
    m = 4
    packets = np.zeros((m, len(z_values)), dtype=np.float64)
    total = np.zeros(len(z_values), dtype=np.float64)
    for index, z in enumerate(z_values):
        for r in range(m):
            packets[r, index] = bernoulli_packet(z, a, m, r).real
        total[index] = bernoulli_interpolation(z, a).real
    fig, axes = plt.subplots(2, 1, figsize=(12.8, 7.0), sharex=True)
    for r in range(m):
        axes[0].plot(z_values, packets[r], lw=1.5, label=f"r={r}")
    axes[0].set_ylabel("packet value")
    axes[0].set_title(r"Bernoulli-Hurwitz packets $\mathcal{B}_{4,r}(z;a)$")
    axes[0].legend(ncol=4)
    axes[0].grid(alpha=0.16)
    axes[1].plot(z_values, total, color=INK, lw=2.4, label="direct interpolation")
    axes[1].plot(z_values, packets.sum(axis=0), color=RED, lw=1.2, ls="--", label="packet sum")
    axes[1].set_xlabel("complex order z restricted to the real axis")
    axes[1].set_ylabel("reconstructed value")
    axes[1].grid(alpha=0.16)
    axes[1].legend()
    fig.suptitle("Exact reconstruction of the Bernoulli interpolation from four packets", fontsize=17, weight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    save_figure(fig, "07_bernoulli_packet_reconstruction")


def figure_08_bernoulli_refinement_tree() -> None:
    fig, ax = plt.subplots(figsize=(12.8, 7.0))
    ax.axis("off")
    levels = [(1, [0]), (2, [0, 1]), (4, list(range(4))), (8, list(range(8)))]
    positions: dict[tuple[int, int], tuple[float, float]] = {}
    for depth, (modulus, residues) in enumerate(levels):
        y = 0.86 - depth * 0.23
        xs = np.linspace(0.08, 0.92, len(residues))
        for residue, xpos in zip(residues, xs, strict=True):
            positions[(modulus, residue)] = (xpos, y)
            color = COLORS[depth % len(COLORS)]
            ax.add_patch(FancyBboxPatch((xpos - 0.045, y - 0.032), 0.09, 0.064, boxstyle="round,pad=.005", facecolor=color + "25", edgecolor=color, lw=1.6))
            ax.text(xpos, y, rf"$({modulus},{residue})$", ha="center", va="center", fontsize=8.5)
    for (parent_m, residues), (child_m, child_residues) in zip(levels[:-1], levels[1:], strict=True):
        factor = child_m // parent_m
        for parent_r in residues:
            px, py = positions[(parent_m, parent_r)]
            for ell in range(factor):
                child_r = parent_r + ell * parent_m
                cx, cy = positions[(child_m, child_r)]
                ax.plot([px, cx], [py - 0.035, cy + 0.035], color=GRID, lw=1)
    ax.text(0.5, 0.96, r"Exact refinement: $\mathcal{B}_{M,r}=\sum_\ell \mathcal{B}_{LM,r+\ell M}$", ha="center", fontsize=19, weight="bold")
    ax.text(0.5, 0.04, "Each parent is reconstructed by all of its residue children", ha="center", fontsize=12.5, color=MUTED)
    save_figure(fig, "08_bernoulli_refinement_tree")


def figure_09_cyclotomic_details() -> None:
    z = 3.4 + 0.6j
    a_values = np.linspace(0.1, 1.8, 120)
    ell = 4
    fig, axes = plt.subplots(2, 1, figsize=(12.8, 7.0), sharex=True)
    for j in range(ell):
        values = np.asarray([cyclotomic_detail(z, a, 1, 0, ell, j) for a in a_values])
        axes[0].plot(a_values, np.abs(values), lw=1.8, label=f"j={j}")
        axes[1].plot(a_values, np.unwrap(np.angle(values)), lw=1.5, label=f"j={j}")
    axes[0].set_ylabel("magnitude")
    axes[0].set_title("Cyclotomic Bernoulli-Lerch channels")
    axes[0].grid(alpha=0.16)
    axes[0].legend(ncol=4)
    axes[1].set_xlabel("translation parameter a")
    axes[1].set_ylabel("unwrapped phase")
    axes[1].grid(alpha=0.16)
    fig.tight_layout()
    save_figure(fig, "09_cyclotomic_details")


def figure_10_cyclotomic_parseval() -> None:
    z = 2.75 + 0.45j
    a = 0.4
    ell = 6
    children = np.asarray([bernoulli_packet(z, a, ell, child) for child in range(ell)])
    transform = np.fft.fft(children) / math.sqrt(ell)
    fig, axes = plt.subplots(1, 2, figsize=(12.8, 4.7))
    axes[0].bar(range(ell), np.abs(children) ** 2, color=COLORS * 2, edgecolor=INK)
    axes[0].set_title("child-packet energies")
    axes[0].set_xlabel("child index")
    axes[0].set_ylabel("squared magnitude")
    axes[1].bar(range(ell), np.abs(transform) ** 2, color=COLORS * 2, edgecolor=INK)
    axes[1].set_title("cyclotomic-channel energies")
    axes[1].set_xlabel("channel index")
    total_child = float(np.sum(np.abs(children) ** 2))
    total_transform = float(np.sum(np.abs(transform) ** 2))
    fig.suptitle(f"Parseval across the special-function filter bank: {total_child:.8f} = {total_transform:.8f}", fontsize=16.5, weight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.90])
    save_figure(fig, "10_cyclotomic_parseval")


def figure_11_bernoulli_euler_channels() -> None:
    x = sp.symbols("x")
    grid = np.linspace(-0.2, 1.2, 600)
    n = 7
    low, high = bernoulli_euler_channels(n, x)
    child0 = 2 ** (n - 1) * sp.bernoulli(n, x / 2)
    child1 = 2 ** (n - 1) * sp.bernoulli(n, (x + 1) / 2)
    functions = [sp.lambdify(x, expression, "numpy") for expression in (child0, child1, low, high)]
    values = [function(grid) for function in functions]
    fig, axes = plt.subplots(1, 2, figsize=(13.0, 4.8))
    axes[0].plot(grid, values[0], color=BLUE, lw=1.8, label="child 0")
    axes[0].plot(grid, values[1], color=ORANGE, lw=1.8, label="child 1")
    axes[0].set_title("two Bernoulli children")
    axes[0].set_xlabel("a")
    axes[0].grid(alpha=0.16)
    axes[0].legend()
    axes[1].plot(grid, values[2], color=TEAL, lw=2, label=r"low: $B_n(a)/\sqrt{2}$")
    axes[1].plot(grid, values[3], color=MAGENTA, lw=2, label=r"high: $-nE_{n-1}(a)/(2\sqrt{2})$")
    axes[1].set_title("unitary low-pass and high-pass channels")
    axes[1].set_xlabel("a")
    axes[1].grid(alpha=0.16)
    axes[1].legend()
    fig.suptitle("Bernoulli and Euler polynomials arise from one exact two-channel refinement", fontsize=16.5, weight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.91])
    save_figure(fig, "11_bernoulli_euler_channels")


def figure_12_packet_wronskians() -> None:
    x = sp.symbols("x")
    grid = np.linspace(-1.2, 2.2, 900)
    fig, axes = plt.subplots(2, 2, figsize=(13.0, 8.0), sharex=True)
    for ax, n, color in zip(axes.ravel(), (3, 4, 5, 6), COLORS[:4], strict=True):
        polynomial = packet_wronskian_polynomial(n, x)
        function = sp.lambdify(x, polynomial, "numpy")
        values = np.asarray(function(grid), dtype=np.float64)
        ax.axhline(0, color=GRID, lw=1)
        ax.plot(grid, values, color=color, lw=1.8)
        roots = [complex(root) for root in sp.nroots(polynomial, maxsteps=200)]
        real_roots = sorted(root.real for root in roots if abs(root.imag) < 1e-9 and -1.2 <= root.real <= 2.2)
        if real_roots:
            ax.scatter(real_roots, np.zeros(len(real_roots)), color=INK, s=24, zorder=4)
        ax.set_title(rf"$\mathcal{{W}}_{{{n}}}(a)$, {len(real_roots)} displayed real roots")
        ax.grid(alpha=0.14)
    for ax in axes[-1]:
        ax.set_xlabel("a")
    fig.suptitle("Packet Wronskians provide a direct zero and interlacing diagnostic", fontsize=17, weight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    save_figure(fig, "12_packet_wronskians")


def figure_13_wronskian_root_counts() -> None:
    x = sp.symbols("x")
    degrees = []
    real_counts = []
    nonreal_counts = []
    ns = list(range(2, 17))
    for n in ns:
        polynomial = packet_wronskian_polynomial(n, x)
        roots = [complex(root) for root in sp.nroots(polynomial, maxsteps=400)]
        real_count = sum(abs(root.imag) < 1e-8 for root in roots)
        degree = sp.degree(polynomial, x)
        degrees.append(degree)
        real_counts.append(real_count)
        nonreal_counts.append(degree - real_count)
    fig, ax = plt.subplots(figsize=(12.8, 4.8))
    ax.bar(ns, real_counts, color=TEAL, label="real roots")
    ax.bar(ns, nonreal_counts, bottom=real_counts, color=ORANGE, label="nonreal roots")
    ax.set_xlabel("order n")
    ax.set_ylabel("root count")
    ax.set_title("A useful negative control: packet Wronskians are not universally real-rooted")
    ax.legend()
    ax.grid(axis="y", alpha=0.18)
    fig.tight_layout()
    save_figure(fig, "13_wronskian_root_counts")


def figure_14_cyclotomic_norms() -> None:
    rows = write_cyclotomic_norm_table()
    ns = np.asarray([int(row["n"]) for row in rows])
    norms = np.asarray([float(sp.Rational(row["norm"])) for row in rows])
    fig, ax = plt.subplots(figsize=(12.8, 4.8))
    ax.semilogy(ns, norms, marker="o", color=BLUE, lw=1.8)
    ax.set_xlabel("integer order n")
    ax.set_ylabel("cyclotomic norm")
    ax.set_title("Exact norm of the first non-DC L=3 Bernoulli detail")
    ax.grid(alpha=0.18)
    fig.tight_layout()
    save_figure(fig, "14_cyclotomic_norms")


def figure_15_mobius_kernel_localization(mu: np.ndarray) -> None:
    n = np.arange(2, 6000, dtype=np.float64)
    fig, ax = plt.subplots(figsize=(12.8, 5.0))
    for k, color in zip((100, 500, 2000, 8000), COLORS[:4], strict=True):
        weight = n ** -2 * np.exp(k * np.log1p(-1.0 / (n * n)))
        normalized = weight / weight.max()
        ax.plot(n / math.sqrt(k), normalized, lw=1.8, color=color, label=f"k={k}")
    ax.set_xlim(0, 5)
    ax.set_xlabel(r"scaled integer address $n/\sqrt{k}$")
    ax.set_ylabel("normalized packet weight")
    ax.set_title(r"The Bernoulli-Möbius transfer localizes at the scale $n\asymp\sqrt{k}$")
    ax.grid(alpha=0.18)
    ax.legend()
    fig.tight_layout()
    save_figure(fig, "15_mobius_kernel_localization")


def figure_16_mertens_wavelet() -> None:
    x = np.linspace(1.001, 180, 2000)
    fig, ax = plt.subplots(figsize=(12.8, 5.0))
    for k, color in zip((100, 500, 2000), (BLUE, TEAL, MAGENTA), strict=True):
        psi = 2 * x ** -5 * np.power(1 - x ** -2, k - 1) * (x * x - k - 1)
        scale = np.max(np.abs(psi))
        ax.plot(x / math.sqrt(k + 1), psi / scale, lw=1.8, color=color, label=f"k={k}")
    ax.axvline(1, color=INK, ls="--", lw=1.2, label=r"sign change $x=\sqrt{k+1}$")
    ax.axhline(0, color=GRID, lw=1)
    ax.set_xlim(0, 3.5)
    ax.set_xlabel(r"scaled coordinate $x/\sqrt{k+1}$")
    ax.set_ylabel("normalized wavelet")
    ax.set_title("The exact finite-difference kernel is a one-sign-change Mertens wavelet")
    ax.legend()
    ax.grid(alpha=0.16)
    fig.tight_layout()
    save_figure(fig, "16_mertens_wavelet")


def figure_17_energy_asymptotic(data: dict[str, np.ndarray]) -> None:
    k = data["k"].astype(float)
    constant = 3 / (2 ** 2.5 * math.pi ** 1.5)
    fig, ax = plt.subplots(figsize=(12.8, 4.9))
    ax.semilogx(k, data["energy"] * k ** 1.5, color=BLUE, lw=2, marker="o", markersize=3, label=r"$k^{3/2}E_k$")
    ax.axhline(constant, color=RED, ls="--", lw=1.8, label=f"limit {constant:.10f}")
    ax.set_xlabel("k")
    ax.set_ylabel("scaled energy")
    ax.set_title("The diagonal Möbius packet energy already has the RH exponent")
    ax.grid(alpha=0.18)
    ax.legend()
    fig.tight_layout()
    save_figure(fig, "17_energy_asymptotic")


def figure_18_mass_and_dimension(data: dict[str, np.ndarray]) -> None:
    k = data["k"].astype(float)
    fig, axes = plt.subplots(1, 2, figsize=(13.0, 4.8))
    axes[0].loglog(k, data["mass"], color=TEAL, lw=2, marker="o", markersize=3, label="squarefree packet mass")
    axes[0].loglog(k, 3 / math.pi ** 1.5 * k ** -0.5, color=INK, ls="--", label=r"$3\pi^{-3/2}k^{-1/2}$")
    axes[0].set_xlabel("k")
    axes[0].set_ylabel("mass")
    axes[0].set_title("active squarefree mass")
    axes[0].grid(alpha=0.18, which="both")
    axes[0].legend()
    axes[1].loglog(k, data["effective_dimension"], color=MAGENTA, lw=2, marker="o", markersize=3)
    axes[1].set_xlabel("k")
    axes[1].set_ylabel(r"$S_k^2/E_k$")
    axes[1].set_title("effective number of active packets")
    axes[1].grid(alpha=0.18, which="both")
    fig.suptitle(r"The packet cloud grows like a constant multiple of $\sqrt{k}$", fontsize=16.5, weight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.91])
    save_figure(fig, "18_mass_and_dimension")


def figure_19_coherence_ratio(data: dict[str, np.ndarray]) -> None:
    k = data["k"].astype(float)
    fig, axes = plt.subplots(1, 2, figsize=(13.0, 4.8))
    axes[0].loglog(k, np.abs(data["c"]), color=BLUE, lw=1.8, marker="o", markersize=3, label=r"$|c_k|$")
    axes[0].loglog(k, np.sqrt(data["energy"]), color=TEAL, lw=1.8, label=r"$\sqrt{E_k}$")
    axes[0].set_xlabel("k")
    axes[0].set_ylabel("amplitude")
    axes[0].set_title("coherent amplitude and diagonal scale")
    axes[0].grid(alpha=0.18, which="both")
    axes[0].legend()
    axes[1].semilogx(k, data["coherence"], color=MAGENTA, lw=1.8, marker="o", markersize=3)
    axes[1].set_xlabel("k")
    axes[1].set_ylabel(r"$\Gamma_k=|c_k|^2/E_k$")
    axes[1].set_title("Möbius packet coherence")
    axes[1].grid(alpha=0.18)
    fig.suptitle("RH is equivalent to subpolynomial growth of the coherence ratio", fontsize=16.5, weight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.91])
    save_figure(fig, "19_coherence_ratio")


def figure_20_log_time_signal(data: dict[str, np.ndarray]) -> None:
    k = data["k"].astype(float)
    y = k ** 0.75 * data["c"]
    fig, ax = plt.subplots(figsize=(12.8, 4.8))
    ax.plot(np.log(k), y, color=BLUE, lw=1.4, marker="o", markersize=3)
    ax.axhline(0, color=GRID, lw=1)
    ax.set_xlabel(r"logarithmic time $u=\log k$")
    ax.set_ylabel(r"$k^{3/4}c_k$")
    ax.set_title("Normalized Bernoulli-difference signal in logarithmic time")
    ax.grid(alpha=0.18)
    fig.tight_layout()
    save_figure(fig, "20_log_time_signal")


def figure_21_long_time_power(mu: np.ndarray) -> None:
    nmax = 60000
    n = np.arange(2, nmax + 1, dtype=np.float64)
    mu_n = mu[2 : nmax + 1].astype(np.float64)
    k = 1200
    coeff = mu_n / (n * n) * np.exp(k * np.log1p(-1.0 / (n * n)))
    t_values = np.linspace(0, 160, 500)
    signal = np.zeros_like(t_values, dtype=np.complex128)
    chunk = 5000
    logs = np.log(n)
    for start in range(0, len(n), chunk):
        stop = min(start + chunk, len(n))
        phase = np.exp(-1j * np.outer(t_values, logs[start:stop]))
        signal += phase @ coeff[start:stop]
    energy = float(np.sum(coeff * coeff))
    running_power = np.cumsum(np.abs(signal) ** 2) / np.arange(1, len(signal) + 1)
    fig, axes = plt.subplots(2, 1, figsize=(12.8, 7.0), sharex=True)
    axes[0].plot(t_values, signal.real, color=BLUE, lw=1.2, label="real")
    axes[0].plot(t_values, signal.imag, color=ORANGE, lw=1.2, label="imaginary")
    axes[0].set_ylabel("F_k(t)")
    axes[0].set_title("Möbius-Bernoulli quantum correlation")
    axes[0].legend()
    axes[0].grid(alpha=0.15)
    axes[1].plot(t_values, running_power, color=TEAL, lw=1.7, label="running mean power")
    axes[1].axhline(energy, color=RED, ls="--", label=f"diagonal energy {energy:.3e}")
    axes[1].set_xlabel("time t")
    axes[1].set_ylabel("mean squared magnitude")
    axes[1].grid(alpha=0.15)
    axes[1].legend()
    fig.tight_layout()
    save_figure(fig, "21_long_time_power")


def figure_22_polyphase_mobius_packets(mu: np.ndarray) -> None:
    modulus = 12
    ks = [200, 1000, 5000]
    fig, axes = plt.subplots(len(ks), 1, figsize=(12.8, 8.3), sharex=True)
    for ax, k in zip(axes, ks, strict=True):
        packets = polyphase_transfer_packets(k, modulus, 180000, mu)
        colors = [TEAL if value >= 0 else ORANGE for value in packets]
        ax.bar(range(modulus), packets, color=colors, edgecolor=INK)
        ax.axhline(0, color=GRID, lw=1)
        ax.set_ylabel(f"k={k}")
        ax.grid(axis="y", alpha=0.15)
    axes[-1].set_xlabel("integer residue modulo 12")
    fig.suptitle("Exact arithmetic polyphase packets of the Möbius transfer signal", fontsize=17, weight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    save_figure(fig, "22_polyphase_mobius_packets")


def figure_23_character_packets(mu: np.ndarray) -> None:
    nmax = 160000
    character = quadratic_character_mod5(nmax)
    k_values = np.unique(np.logspace(1, 4.6, 80).astype(int))
    principal = []
    quadratic = []
    for k in k_values:
        principal.append(generalized_transfer_direct(2, 2, int(k), 0, nmax, mu))
        quadratic.append(generalized_transfer_direct(2, 2, int(k), 0, nmax, mu, character))
    fig, ax = plt.subplots(figsize=(12.8, 4.9))
    ax.loglog(k_values, np.abs(principal), color=BLUE, lw=1.8, label="principal character")
    ax.loglog(k_values, np.abs(quadratic), color=MAGENTA, lw=1.8, label="quadratic character mod 5")
    ax.set_xlabel("k")
    ax.set_ylabel("transfer amplitude")
    ax.set_title("Character packets create a natural GRH-facing atlas")
    ax.grid(alpha=0.18, which="both")
    ax.legend()
    fig.tight_layout()
    save_figure(fig, "23_character_packets")


def figure_24_quantum_operator_pipeline() -> None:
    fig, ax = plt.subplots(figsize=(12.8, 6.1))
    ax.axis("off")
    stages = [
        (0.03, r"$|\phi_a\rangle$", "power-law state", BLUE),
        (0.23, r"$e^{-kK_\beta}$", "scale filter", TEAL),
        (0.43, r"$\mathcal{M}_\chi$", "Möbius-character sign", ORANGE),
        (0.63, r"$e^{-itH}$", "logarithmic evolution", MAGENTA),
        (0.83, r"$\langle\phi_a|$", "coherence readout", RED),
    ]
    for x0, formula, title, color in stages:
        box = FancyBboxPatch((x0, 0.40), 0.14, 0.22, boxstyle="round,pad=.015", facecolor=color + "24", edgecolor=color, lw=2)
        ax.add_patch(box)
        ax.text(x0 + 0.07, 0.55, formula, ha="center", va="center", fontsize=15)
        ax.text(x0 + 0.07, 0.45, title, ha="center", va="center", fontsize=9.5)
    for left, right in zip(stages[:-1], stages[1:], strict=True):
        ax.add_patch(FancyArrowPatch((left[0] + 0.14, 0.51), (right[0], 0.51), arrowstyle="-|>", mutation_scale=14, lw=1.8, color=INK))
    ax.text(0.5, 0.82, r"$\mathcal{C}_{a,\beta,\chi}(k,t)=\langle\phi_a|\mathcal{M}_\chi e^{-kK_\beta}e^{-itH}|\phi_a\rangle$", ha="center", fontsize=18, weight="bold")
    ax.text(0.5, 0.18, r"$H|n\rangle=\log n|n\rangle$ and $K_\beta=-\log(I-e^{-\beta H})$", ha="center", fontsize=14, color=MUTED)
    save_figure(fig, "24_quantum_operator_pipeline")


def figure_25_function_family_map() -> None:
    fig, ax = plt.subplots(figsize=(13.0, 7.0))
    ax.axis("off")
    nodes = {
        "scalar": (0.10, 0.74, "scalar analytic\nfunction", BLUE),
        "lift": (0.38, 0.74, "polyphase\nvector lift", TEAL),
        "matrix": (0.68, 0.74, "matrix differential\nsystem", ORANGE),
        "bern": (0.12, 0.36, "Bernoulli-Hurwitz\npackets", MAGENTA),
        "lerch": (0.40, 0.36, "cyclotomic Lerch\ndetails", RED),
        "wronskian": (0.68, 0.36, "packet Wronskians\nand zero tests", YELLOW),
        "mobius": (0.88, 0.36, "Möbius-Bernoulli\ncoherence", BLUE),
    }
    for key, (x0, y0, label, color) in nodes.items():
        ax.add_patch(FancyBboxPatch((x0 - 0.09, y0 - 0.06), 0.18, 0.12, boxstyle="round,pad=.012", facecolor=color + "22", edgecolor=color, lw=2))
        ax.text(x0, y0, label, ha="center", va="center", fontsize=11, weight="bold")
    edges = [
        ("scalar", "lift"), ("lift", "matrix"), ("scalar", "bern"), ("bern", "lerch"), ("lerch", "wronskian"), ("wronskian", "mobius"), ("matrix", "mobius"),
    ]
    for source, target in edges:
        sx, sy = nodes[source][0], nodes[source][1]
        tx, ty = nodes[target][0], nodes[target][1]
        ax.add_patch(FancyArrowPatch((sx, sy), (tx, ty), arrowstyle="-|>", mutation_scale=12, lw=1.4, color=GRID, connectionstyle="arc3,rad=0.05"))
    ax.text(0.5, 0.93, "A special-function factory generated by exact packet analysis", ha="center", fontsize=20, weight="bold")
    ax.text(0.5, 0.10, "The constructions share reconstruction, refinement, transfer, and certificate laws", ha="center", fontsize=13, color=MUTED)
    save_figure(fig, "25_function_family_map")


def figure_26_status_map() -> None:
    fig, ax = plt.subplots(figsize=(12.8, 5.9))
    ax.axis("off")
    categories = [
        (0.08, 0.65, 0.24, 0.20, "PROVED HERE", ["polyphase lift", "Bernoulli packet refinement", "cyclotomic inverse transform", "energy asymptotic"], TEAL),
        (0.38, 0.65, 0.24, 0.20, "CLASSICAL INPUT", ["Hurwitz zeta", "Raabe multiplication", "Lerch transcendent", "Báez-Duarte criterion"], BLUE),
        (0.68, 0.65, 0.24, 0.20, "COMPUTATIONAL", ["Wronskian root maps", "cyclotomic norms", "coherence plots", "character packets"], ORANGE),
        (0.23, 0.24, 0.24, 0.20, "OPEN", ["Wronskian sign laws", "zero interlacing", "p-adic detail bounds", "character-uniform coherence"], MAGENTA),
        (0.53, 0.24, 0.24, 0.20, "MAJOR CONJECTURE", ["subpolynomial Möbius coherence", "RH and GRH applications", "positive canonical systems"], RED),
    ]
    for x0, y0, w, h, title, entries, color in categories:
        ax.add_patch(FancyBboxPatch((x0, y0), w, h, boxstyle="round,pad=.015", facecolor=color + "20", edgecolor=color, lw=2))
        ax.text(x0 + w / 2, y0 + h - 0.035, title, ha="center", va="center", fontsize=11.5, weight="bold", color=color)
        for index, entry in enumerate(entries):
            ax.text(x0 + 0.025, y0 + h - 0.075 - 0.030 * index, "• " + entry, ha="left", va="center", fontsize=9.4)
    ax.text(0.5, 0.94, "Claim boundary for the generated function theory", ha="center", fontsize=19, weight="bold")
    save_figure(fig, "26_status_map")


def generate_all_figures() -> dict[str, object]:
    checks = run_symbolic_checks()
    if not all(check.passed for check in checks):
        failed = [check for check in checks if not check.passed]
        raise RuntimeError(f"symbolic checks failed: {failed}")

    nmax = 200000
    mu = mobius_sieve(nmax)
    k_values = np.unique(np.logspace(1, 5, 92).astype(int))
    transfer_data = principal_transfer_values(k_values, nmax, mu)

    figure_01_polyphase_partition()
    figure_02_carry_shift()
    figure_03_exp_sections()
    figure_04_exp_reconstruction()
    figure_05_operator_lift_map()
    figure_06_bessel_sections()
    figure_07_bernoulli_packet_reconstruction()
    figure_08_bernoulli_refinement_tree()
    figure_09_cyclotomic_details()
    figure_10_cyclotomic_parseval()
    figure_11_bernoulli_euler_channels()
    figure_12_packet_wronskians()
    figure_13_wronskian_root_counts()
    figure_14_cyclotomic_norms()
    figure_15_mobius_kernel_localization(mu)
    figure_16_mertens_wavelet()
    figure_17_energy_asymptotic(transfer_data)
    figure_18_mass_and_dimension(transfer_data)
    figure_19_coherence_ratio(transfer_data)
    figure_20_log_time_signal(transfer_data)
    figure_21_long_time_power(mu)
    figure_22_polyphase_mobius_packets(mu)
    figure_23_character_packets(mu)
    figure_24_quantum_operator_pipeline()
    figure_25_function_family_map()
    figure_26_status_map()

    # Numerical result ledger
    constant = 3 / (2 ** 2.5 * math.pi ** 1.5)
    large_index = -1
    energy_scaled = float(transfer_data["energy"][large_index] * transfer_data["k"][large_index] ** 1.5)
    mass_scaled = float(transfer_data["mass"][large_index] * math.sqrt(transfer_data["k"][large_index]))

    quantum_k = 1200
    mean_power = long_time_power(2, 2, quantum_k, nmax, mu)
    zero_time = generalized_transfer_direct(2, 2, quantum_k, 0.0, nmax, mu)

    results = {
        "figure_pairs": 26,
        "symbolic_checks": len(checks),
        "symbolic_checks_passed": sum(check.passed for check in checks),
        "mobius_nmax": nmax,
        "largest_k": int(transfer_data["k"][large_index]),
        "energy_scaled_at_largest_k": energy_scaled,
        "energy_asymptotic_constant": constant,
        "energy_relative_error": abs(energy_scaled - constant) / constant,
        "mass_scaled_at_largest_k": mass_scaled,
        "mass_asymptotic_constant": 3 / math.pi ** 1.5,
        "quantum_k": quantum_k,
        "quantum_zero_time_abs": abs(zero_time),
        "quantum_long_time_diagonal_power": mean_power,
        "quantum_coherence_ratio": abs(zero_time) ** 2 / mean_power,
    }

    with (RESULTS / "results.json").open("w", encoding="utf-8") as handle:
        json.dump(results, handle, indent=2, sort_keys=True)

    with (RESULTS / "checks.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["name", "passed", "detail"])
        writer.writeheader()
        writer.writerows([{"name": check.name, "passed": check.passed, "detail": check.detail} for check in checks])

    with (TABLES / "mobius_transfer_samples.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["k", "c_k", "energy", "mass", "coherence", "effective_dimension"])
        for row in zip(
            transfer_data["k"],
            transfer_data["c"],
            transfer_data["energy"],
            transfer_data["mass"],
            transfer_data["coherence"],
            transfer_data["effective_dimension"],
            strict=True,
        ):
            writer.writerow(row)

    return results


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the Projector-Generated Special Functions paper assets")
    parser.add_argument("--base", type=Path, default=ROOT)
    args = parser.parse_args()
    if args.base.resolve() != ROOT.resolve():
        raise SystemExit("This release expects to run from its source directory")
    results = generate_all_figures()
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
