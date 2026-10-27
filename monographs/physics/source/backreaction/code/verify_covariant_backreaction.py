#!/usr/bin/env python3
"""Verification suite for the covariant refinement-fiber bridge.

The program uses only NumPy, SciPy, and Matplotlib. It separates exact
identities, controlled quadrature, and diagnostic model calculations.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq
from scipy.special import beta as beta_fn
from scipy.special import gamma as gamma_fn
from scipy.special import roots_genlaguerre


PI = math.pi
GL_X, GL_W = roots_genlaguerre(128, 0.5)
GL96_X, GL96_W = roots_genlaguerre(96, 0.5)
GL_PREF = 1.0 / (2.0 * PI**1.5)


@dataclass(frozen=True)
class ContinuumConstants:
    sigma: float
    alpha: float
    c_number: float
    c_rest: float
    c_energy: float
    c_pressure: float
    w: float
    rest_fraction: float
    mean_mass_over_a: float
    rest_peak_over_a: float


def continuum_constants(sigma: float) -> ContinuumConstants:
    alpha = 1.0 / sigma
    c_number = gamma_fn(alpha + 1.5) / (
        8.0 * sigma * PI ** (alpha + 4.5)
    )
    c_rest = gamma_fn(alpha + 2.5) / (
        8.0 * sigma * PI ** (alpha + 5.5)
    )
    c_energy = (
        gamma_fn(alpha + 4.0)
        * beta_fn(1.5, alpha + 2.0)
        / (4.0 * sigma * PI ** (alpha + 6.0))
    )
    w = 1.0 / (2.0 * alpha + 7.0)
    c_pressure = c_energy * w
    rest_fraction = c_rest / c_energy
    mean_mass = (alpha + 1.5) / PI
    return ContinuumConstants(
        sigma=sigma,
        alpha=alpha,
        c_number=c_number,
        c_rest=c_rest,
        c_energy=c_energy,
        c_pressure=c_pressure,
        w=w,
        rest_fraction=rest_fraction,
        mean_mass_over_a=mean_mass,
        rest_peak_over_a=mean_mass,
    )


def energy_per_state_dimensionless(
    y: float,
    laguerre_x: np.ndarray = GL_X,
    laguerre_w: np.ndarray = GL_W,
) -> float:
    """Energy per internal state divided by A^4 for m/A=y."""
    if y <= 0.0:
        return 0.0
    root = np.sqrt(y + laguerre_x / PI)
    integral = GL_PREF * float(np.dot(laguerre_w, root))
    return float(y**2 * math.exp(-PI * y) * integral / (2.0 * PI**2))


def pressure_per_state_dimensionless(
    y: float,
    laguerre_x: np.ndarray = GL_X,
    laguerre_w: np.ndarray = GL_W,
) -> float:
    """Pressure per internal state divided by A^4 for m/A=y."""
    if y <= 0.0:
        return 0.0
    root = np.sqrt(y + laguerre_x / PI)
    integral = (GL_PREF / PI) * float(
        np.dot(laguerre_w, laguerre_x / root)
    )
    return float(y**2 * math.exp(-PI * y) * integral / (6.0 * PI**2))


def number_per_state_dimensionless(y: float) -> float:
    return y ** 1.5 * math.exp(-PI * y) / (8.0 * PI**3)


def rest_per_state_dimensionless(y: float) -> float:
    return y ** 2.5 * math.exp(-PI * y) / (8.0 * PI**3)


def discrete_tower_moments(
    lambda_over_a: float,
    prime: int,
    sigma: float,
    cutoff_y: float = 35.0,
    laguerre_x: np.ndarray = GL_X,
    laguerre_w: np.ndarray = GL_W,
) -> dict[str, float]:
    total_n = 0.0
    total_r = 0.0
    total_e = 0.0
    total_p = 0.0
    level_count = 0
    h = 1
    while h < 1000:
        y = lambda_over_a * prime ** (sigma * h)
        if y > cutoff_y:
            break
        degeneracy = (prime - 1) * prime ** (h - 1)
        total_n += degeneracy * number_per_state_dimensionless(y)
        total_r += degeneracy * rest_per_state_dimensionless(y)
        total_e += degeneracy * energy_per_state_dimensionless(
            y, laguerre_x, laguerre_w
        )
        total_p += degeneracy * pressure_per_state_dimensionless(
            y, laguerre_x, laguerre_w
        )
        level_count += 1
        h += 1
    if total_e <= 0.0 or total_n <= 0.0:
        return {
            "levels": level_count,
            "number": total_n,
            "rest": total_r,
            "energy": total_e,
            "pressure": total_p,
            "w": math.nan,
            "rest_fraction": math.nan,
            "mean_mass_over_a": math.nan,
        }
    return {
        "levels": level_count,
        "number": total_n,
        "rest": total_r,
        "energy": total_e,
        "pressure": total_p,
        "w": total_p / total_e,
        "rest_fraction": total_r / total_e,
        "mean_mass_over_a": total_r / total_n,
    }


def bandlimited(rng: np.random.Generator, n: int, kmax: int) -> np.ndarray:
    x = 2.0 * PI * np.arange(n) / n
    out = rng.normal()
    for k in range(1, kmax + 1):
        out += rng.normal() * np.cos(k * x) + rng.normal() * np.sin(k * x)
    return out / math.sqrt(1.0 + 2.0 * kmax)


def spectral_derivative(values: np.ndarray) -> np.ndarray:
    n = len(values)
    modes = np.fft.fftfreq(n, d=1.0 / n)
    return np.fft.ifft(1j * modes * np.fft.fft(values)).real


def centered_derivative(values: np.ndarray) -> np.ndarray:
    dx = 2.0 * PI / len(values)
    return (np.roll(values, -1) - np.roll(values, 1)) / (2.0 * dx)


def matter_constraint_residual(
    rng: np.random.Generator,
    n: int,
    kmax: int,
    derivative,
    omit_exchange: bool = False,
    omit_chi_gradient: bool = False,
    trials: int = 20,
) -> float:
    worst = 0.0
    lam_phi = 0.4
    v = 1.2
    gamma = 0.7
    fiber_eigenvalue = 1.3
    base_mass2 = 0.6
    for _ in range(trials):
        phi, pi_phi, chi, pi_chi, lapse_n, lapse_m = [
            bandlimited(rng, n, kmax) for _ in range(6)
        ]
        dphi = derivative(phi)
        dchi = derivative(chi)
        dn = derivative(lapse_n)
        dm = derivative(lapse_m)
        uprime = lam_phi * phi * (phi**2 - v**2)
        a = 1.0 + gamma * phi**2 / v**2
        interaction_phi = gamma * phi * fiber_eigenvalue * chi**2 / v**2
        vphi = uprime if omit_exchange else uprime + interaction_phi
        vchi = (base_mass2 + a * fiber_eigenvalue) * chi

        def gradients(lapse: np.ndarray):
            q_phi = -derivative(lapse * dphi) + lapse * vphi
            p_phi = lapse * pi_phi
            q_chi = lapse * vchi
            if not omit_chi_gradient:
                q_chi = q_chi - derivative(lapse * dchi)
            p_chi = lapse * pi_chi
            return q_phi, p_phi, q_chi, p_chi

        qn, pn, qcn, pcn = gradients(lapse_n)
        qm, pm, qcm, pcm = gradients(lapse_m)
        bracket = np.mean(qn * pm - pn * qm + qcn * pcm - pcn * qcm)
        shift = lapse_n * dm - lapse_m * dn
        expected = np.mean(shift * (pi_phi * dphi + pi_chi * dchi))
        scale = max(1.0e-14, abs(bracket), abs(expected))
        worst = max(worst, abs(bracket - expected) / scale)
    return worst


def commutant_nullities(dims: list[int], prime: int, sigma: float) -> tuple[int, int]:
    n = sum(dims)
    constraints: list[np.ndarray] = []
    offset = 0
    identity = np.eye(n, dtype=complex)
    for dim in dims:
        for a in range(dim):
            for b in range(dim):
                generator = np.zeros((n, n), dtype=complex)
                generator[offset + a, offset + b] = 1.0
                constraints.append(
                    np.kron(generator.T, identity) - np.kron(identity, generator)
                )
        offset += dim
    system = np.vstack(constraints)
    singular = np.linalg.svd(system, compute_uv=False)
    tol = singular[0] * max(system.shape) * np.finfo(float).eps
    invariant_nullity = n * n - int(np.count_nonzero(singular > tol))
    scale_matrix = np.zeros((len(dims) - 1, len(dims)))
    factor = prime ** (2.0 * sigma)
    for row in range(len(dims) - 1):
        scale_matrix[row, row] = -factor
        scale_matrix[row, row + 1] = 1.0
    scale_rank = np.linalg.matrix_rank(scale_matrix)
    scale_nullity = len(dims) - scale_rank
    return invariant_nullity, scale_nullity


def ward_identity_residual(seed: int = 20260819) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    h = 0.17
    phi = rng.normal()
    phi_dot = rng.normal()
    chi = rng.normal(size=7)
    chi_dot = rng.normal(size=7)
    eigenvalues = np.geomspace(0.4, 30.0, len(chi))
    lam_phi = 0.8
    v = 1.1
    gamma = 0.6
    base_mass2 = 0.3
    uprime = lam_phi * phi * (phi**2 - v**2)
    aprime = 2.0 * gamma * phi / v**2
    a = 1.0 + gamma * phi**2 / v**2
    y_d = float(np.sum(eigenvalues * chi**2))
    mass2 = base_mass2 + a * eigenvalues
    phi_ddot = -3.0 * h * phi_dot - uprime - 0.5 * aprime * y_d
    chi_ddot = -3.0 * h * chi_dot - mass2 * chi
    q = 0.5 * aprime * phi_dot * y_d
    rho_phi_dot = phi_dot * phi_ddot + uprime * phi_dot
    rho_chi_dot = float(
        np.sum(chi_dot * chi_ddot + mass2 * chi * chi_dot)
        + 0.5 * aprime * phi_dot * y_d
    )
    average_residual = rho_phi_dot + 3.0 * h * phi_dot**2 + q
    detail_residual = rho_chi_dot + 3.0 * h * float(np.sum(chi_dot**2)) - q
    omitted_exchange_residual = q
    return {
        "average": abs(average_residual),
        "detail": abs(detail_residual),
        "total": abs(average_residual + detail_residual),
        "omitted_exchange": abs(omitted_exchange_residual),
    }


def saturation_diagnostic(parent: dict) -> dict[str, float]:
    pars = parent["parameters"]
    calibrated = parent["calibrated_benchmark"]
    gamma = float(pars["gamma"])
    lam_phi = float(pars["lam"])
    sigma = float(pars["sigma"])
    prime = int(pars["prime"])
    alpha = 1.0 / sigma
    eta = float(calibrated["capture_normalization"])
    a_in = float(calibrated["A_over_mu"])
    lambda_in = float(calibrated["Lambda_over_mu"])
    v_over_mu = 1.0 / math.sqrt(lam_phi)
    continuum_energy_ratio = (
        2.0
        * gamma
        * continuum_constants(sigma).c_energy
        * a_in ** (alpha + 2.0)
        / (v_over_mu**2 * lambda_in**alpha)
    )
    continuum_factor = continuum_energy_ratio ** (-1.0 / (alpha + 2.0))
    continuum_a = a_in * continuum_factor
    continuum_x = lambda_in / continuum_a
    continuum_lowest_exponent = PI * continuum_x * prime**sigma

    def log_overdraw(x: float) -> float:
        moments = discrete_tower_moments(x, prime, sigma)
        a_over_mu = lambda_in / x
        ratio = (
            2.0
            * gamma
            * a_over_mu**2
            * moments["energy"]
            / v_over_mu**2
        )
        return math.log(max(ratio, 1.0e-300))

    x_lo = float(pars["lambda_over_A"])
    x_hi = 1.0
    while log_overdraw(x_hi) > 0.0 and x_hi < 100.0:
        x_hi *= 1.5
    x_sat = brentq(log_overdraw, x_lo, x_hi, xtol=1.0e-12, rtol=1.0e-12)
    sat = discrete_tower_moments(x_sat, prime, sigma)
    a_sat = lambda_in / x_sat
    lowest_mass = lambda_in * prime**sigma
    lowest_coupling = gamma * lowest_mass**2 / v_over_mu**2
    peak_coupling = (
        gamma
        * lam_phi
        * float(calibrated["mass_peak_over_mu_discrete"]) ** 2
    )
    energy_lambda_bound = lam_phi * eta
    return {
        "eta": eta,
        "unprojected_energy_over_available": 1.0 / eta,
        "continuum_energy_over_available_at_input": continuum_energy_ratio,
        "continuum_slowing_factor": continuum_factor,
        "continuum_energy_saturation_A_over_mu": continuum_a,
        "continuum_energy_saturation_Lambda_over_A": continuum_x,
        "continuum_lowest_level_suppression_exponent": continuum_lowest_exponent,
        "discrete_energy_saturation_A_over_mu": a_sat,
        "discrete_energy_saturation_Lambda_over_A": x_sat,
        "discrete_saturation_level_count": sat["levels"],
        "discrete_saturation_w": sat["w"],
        "discrete_saturation_rest_fraction": sat["rest_fraction"],
        "discrete_saturation_mean_mass_over_A": sat["mean_mass_over_a"],
        "benchmark_peak_quartic_coupling": peak_coupling,
        "saturation_lowest_level_quartic_coupling": lowest_coupling,
        "perturbative_lambda_upper_bound_at_benchmark_peak": 1.0
        / (gamma * float(calibrated["mass_peak_over_mu_discrete"]) ** 2),
        "energy_control_lambda_upper_bound": energy_lambda_bound,
        "peak_coupling_at_energy_control_bound": peak_coupling
        * energy_lambda_bound
        / lam_phi,
        "lowest_coupling_at_energy_control_bound": lowest_coupling
        * energy_lambda_bound
        / lam_phi,
    }


def saturation_curve(parent: dict, points: int = 120) -> list[dict[str, float]]:
    pars = parent["parameters"]
    calibrated = parent["calibrated_benchmark"]
    gamma = float(pars["gamma"])
    lam_phi = float(pars["lam"])
    sigma = float(pars["sigma"])
    prime = int(pars["prime"])
    lambda_over_mu = float(calibrated["Lambda_over_mu"])
    v_over_mu = 1.0 / math.sqrt(lam_phi)
    rows = []
    for x in np.geomspace(float(pars["lambda_over_A"]), 12.0, points):
        moments = discrete_tower_moments(float(x), prime, sigma)
        a_over_mu = lambda_over_mu / x
        ratio = (
            2.0
            * gamma
            * a_over_mu**2
            * moments["energy"]
            / v_over_mu**2
        )
        rows.append(
            {
                "lambda_over_a": float(x),
                "a_over_mu": float(a_over_mu),
                "energy_over_available": float(ratio),
                "w": float(moments["w"]),
                "rest_fraction": float(moments["rest_fraction"]),
                "levels": int(moments["levels"]),
            }
        )
    return rows


def radiative_scaling(prime: int, sigmas: list[float]) -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    for sigma in sigmas:
        values = []
        for depth in range(1, 25):
            tower = sum(
                (prime - 1)
                * prime ** (h - 1)
                * prime ** (4.0 * sigma * h)
                for h in range(1, depth + 1)
            )
            muv = prime ** (sigma * depth)
            values.append((depth, muv, tower))
        fit = np.polyfit(
            np.log([v[1] for v in values[-9:]]),
            np.log([v[2] for v in values[-9:]]),
            1,
        )[0]
        expected = 4.0 + 1.0 / sigma
        for depth, muv, tower in values:
            rows.append(
                {
                    "sigma": sigma,
                    "depth": depth,
                    "m_uv_over_lambda": muv,
                    "weighted_m4_sum": tower,
                    "fitted_exponent": fit,
                    "expected_exponent": expected,
                }
            )
    return rows


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def relative_error(value: float, reference: float) -> float:
    return abs(value / reference - 1.0)


def continuum_outer_quadrature_residual(sigma: float) -> float:
    """Independently integrate the per-state kernels over continuum mass."""
    constants = continuum_constants(sigma)
    alpha = constants.alpha
    kernels = (
        (number_per_state_dimensionless, constants.c_number),
        (rest_per_state_dimensionless, constants.c_rest),
        (energy_per_state_dimensionless, constants.c_energy),
        (pressure_per_state_dimensionless, constants.c_pressure),
    )
    residual = 0.0
    for kernel, reference in kernels:
        value = quad(
            lambda y: y ** (alpha - 1.0) * kernel(y) / sigma,
            0.0,
            np.inf,
            epsabs=2.0e-14,
            epsrel=2.0e-11,
            limit=400,
        )[0]
        residual = max(residual, relative_error(value, reference))
    return residual


def build_figures(
    figure_dir: Path,
    continuum_rows: list[dict],
    convergence_rows: list[dict],
    radiative_rows: list[dict],
    saturation_rows: list[dict],
    checks: list[dict],
    diagnostic: dict,
) -> None:
    figure_dir.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.size": 10.5,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "figure.dpi": 130,
            "savefig.dpi": 240,
        }
    )
    blue = "#254f73"
    rust = "#a44a3f"
    green = "#3f7652"
    gold = "#b1842f"

    sig = np.array([r["sigma"] for r in continuum_rows])
    w = np.array([r["w"] for r in continuum_rows])
    rest = np.array([r["rest_fraction"] for r in continuum_rows])
    peak = np.array([r["rest_peak_over_a"] for r in continuum_rows])
    fig, axes = plt.subplots(1, 3, figsize=(11.0, 3.35))
    axes[0].plot(sig, w, color=blue, lw=2.2)
    axes[0].set(xlabel=r"refinement order $\sigma$", ylabel=r"$w_\star$")
    axes[1].plot(sig, rest, color=green, lw=2.2)
    axes[1].set(xlabel=r"refinement order $\sigma$", ylabel="captured rest fraction")
    axes[2].plot(sig, peak, color=rust, lw=2.2)
    axes[2].set(xlabel=r"refinement order $\sigma$", ylabel=r"$m_{\rm peak}/A$")
    for ax in axes:
        ax.grid(alpha=0.22)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(figure_dir / f"general_sigma_universality.{ext}", bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.8, 4.2))
    for prime, color in zip((2, 3, 5), (blue, rust, green)):
        subset = [r for r in convergence_rows if r["prime"] == prime]
        ax.loglog(
            [r["lambda_over_a"] for r in subset],
            [r["relative_energy_error"] for r in subset],
            marker="o",
            lw=1.8,
            color=color,
            label=f"p={prime}",
        )
    ax.set_xlabel(r"$\Lambda/A$")
    ax.set_ylabel("relative interpolation-energy discrepancy")
    ax.grid(alpha=0.22, which="both")
    ax.legend(frameon=False)
    ax.invert_xaxis()
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(figure_dir / f"fixed_prime_log_sampling.{ext}", bbox_inches="tight")
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.05))
    xvals = np.array([r["lambda_over_a"] for r in saturation_rows])
    ratios = np.array([r["energy_over_available"] for r in saturation_rows])
    axes[0].loglog(xvals, ratios, color=rust, lw=2.2)
    axes[0].axhline(1.0, color=gold, lw=1.5, linestyle="--", label="energy limit")
    axes[0].axvline(diagnostic["discrete_energy_saturation_Lambda_over_A"], color=blue, lw=1.4, linestyle=":", label="discrete saturation")
    axes[0].set(xlabel=r"$\Lambda/A$", ylabel="unprojected energy / available energy")
    axes[0].grid(alpha=0.22, which="both")
    axes[0].legend(frameon=False, fontsize=9)
    axes[1].semilogx(xvals, [r["rest_fraction"] for r in saturation_rows], color=green, lw=2.2, label="rest fraction")
    axes[1].semilogx(xvals, [r["w"] for r in saturation_rows], color=blue, lw=2.2, label=r"$w_\star$")
    axes[1].axvline(diagnostic["discrete_energy_saturation_Lambda_over_A"], color=rust, lw=1.4, linestyle=":")
    axes[1].set(xlabel=r"$\Lambda/A$", ylabel="production ratio")
    axes[1].grid(alpha=0.22, which="both")
    axes[1].legend(frameon=False, fontsize=9)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(figure_dir / f"backreaction_obstruction.{ext}", bbox_inches="tight")
    plt.close(fig)

    constraint_checks = [r for r in checks if r["family"] == "constraint"]
    fig, ax = plt.subplots(figsize=(7.4, 4.15))
    labels = [r["short_label"] for r in constraint_checks]
    vals = [max(float(r["residual"]), 1.0e-18) for r in constraint_checks]
    colors = [blue if r["expected"] == "pass" else rust for r in constraint_checks]
    ax.bar(labels, vals, color=colors)
    ax.set_yscale("log")
    ax.set_ylabel("relative bracket residual")
    ax.tick_params(axis="x", rotation=17)
    ax.grid(axis="y", alpha=0.22, which="both")
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(figure_dir / f"constraint_negative_controls.{ext}", bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.8, 4.2))
    for sigma, color in zip((0.5, 1.0, 2.0), (rust, blue, green)):
        subset = [r for r in radiative_rows if r["sigma"] == sigma]
        ax.loglog(
            [r["m_uv_over_lambda"] for r in subset],
            [r["weighted_m4_sum"] for r in subset],
            lw=2.0,
            color=color,
            label=rf"$\sigma={sigma:g}$",
        )
    ax.set_xlabel(r"$M_{\rm UV}/\Lambda$")
    ax.set_ylabel(r"$\sum_h d_h\lambda_h^2/\Lambda^4$")
    ax.grid(alpha=0.22, which="both")
    ax.legend(frameon=False)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(figure_dir / f"radiative_uv_growth.{ext}", bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parent-json", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--figures", required=True, type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    parent = json.loads(args.parent_json.read_text(encoding="utf-8"))

    sigma_grid = np.linspace(0.4, 3.0, 90)
    continuum_rows = []
    for sigma in sigma_grid:
        c = continuum_constants(float(sigma))
        continuum_rows.append(
            {
                "sigma": c.sigma,
                "alpha": c.alpha,
                "c_number": c.c_number,
                "c_rest": c.c_rest,
                "c_energy": c.c_energy,
                "c_pressure": c.c_pressure,
                "w": c.w,
                "rest_fraction": c.rest_fraction,
                "mean_mass_over_a": c.mean_mass_over_a,
                "rest_peak_over_a": c.rest_peak_over_a,
            }
        )
    write_csv(args.output / "continuum_universality.csv", continuum_rows)

    convergence_rows = []
    c1 = continuum_constants(1.0)
    for prime in (2, 3, 5):
        for x in np.geomspace(1.0e-1, 1.0e-5, 13):
            disc = discrete_tower_moments(float(x), prime, 1.0)
            expected_energy = c1.c_energy / x
            expected_rest = c1.c_rest / x
            convergence_rows.append(
                {
                    "prime": prime,
                    "sigma": 1.0,
                    "lambda_over_a": float(x),
                    "levels": disc["levels"],
                    "energy": disc["energy"],
                    "expected_energy": expected_energy,
                    "relative_energy_error": abs(disc["energy"] / expected_energy - 1.0),
                    "rest": disc["rest"],
                    "expected_rest": expected_rest,
                    "relative_rest_error": abs(disc["rest"] / expected_rest - 1.0),
                    "w": disc["w"],
                    "rest_fraction": disc["rest_fraction"],
                }
            )
    write_csv(args.output / "discrete_convergence.csv", convergence_rows)

    rng = np.random.default_rng(20260819)
    spectral = matter_constraint_residual(rng, 128, 3, spectral_derivative)
    aliased = matter_constraint_residual(rng, 64, 18, spectral_derivative)
    finite_difference = matter_constraint_residual(rng, 128, 3, centered_derivative)
    omitted_gradient = matter_constraint_residual(
        rng, 128, 3, spectral_derivative, omit_chi_gradient=True
    )
    ward = ward_identity_residual()
    invariant_nullity, scale_nullity = commutant_nullities([1, 2, 4], 2, 1.0)
    diagnostic = saturation_diagnostic(parent)

    sigma1_references = (
        3.0 / (32.0 * PI**5),
        15.0 / (64.0 * PI**6),
        32.0 / (35.0 * PI**7),
        32.0 / (315.0 * PI**7),
    )
    sigma1_values = (c1.c_number, c1.c_rest, c1.c_energy, c1.c_pressure)
    sigma1_residual = max(
        relative_error(value, reference)
        for value, reference in zip(sigma1_values, sigma1_references)
    )
    outer_residuals = {
        sigma: continuum_outer_quadrature_residual(sigma)
        for sigma in (0.5, 1.0, 2.0)
    }

    pars = parent["parameters"]
    calibrated = parent["calibrated_benchmark"]
    gamma = float(pars["gamma"])
    lam_phi = float(pars["lam"])
    sigma = float(pars["sigma"])
    prime = int(pars["prime"])
    alpha = 1.0 / sigma
    x_in = float(pars["lambda_over_A"])
    a_in = float(calibrated["A_over_mu"])
    lambda_in = float(calibrated["Lambda_over_mu"])
    eta = float(calibrated["capture_normalization"])
    v_over_mu = 1.0 / math.sqrt(lam_phi)

    benchmark_128 = discrete_tower_moments(x_in, prime, sigma)
    benchmark_96 = discrete_tower_moments(
        x_in,
        prime,
        sigma,
        laguerre_x=GL96_X,
        laguerre_w=GL96_W,
    )
    quadrature_residual = max(
        relative_error(benchmark_96[key], benchmark_128[key])
        for key in ("energy", "pressure")
    )
    reconstructed_overdraw = (
        2.0
        * gamma
        * a_in**2
        * benchmark_128["energy"]
        / v_over_mu**2
    )
    parent_overdraw_residual = abs(reconstructed_overdraw * eta - 1.0)

    threshold_x = diagnostic["discrete_energy_saturation_Lambda_over_A"]
    threshold_a = lambda_in / threshold_x
    threshold_moments = discrete_tower_moments(threshold_x, prime, sigma)
    threshold_ratio = (
        2.0
        * gamma
        * threshold_a**2
        * threshold_moments["energy"]
        / v_over_mu**2
    )
    threshold_residual = abs(threshold_ratio - 1.0)

    continuum_ratio = (
        2.0
        * gamma
        * continuum_constants(sigma).c_energy
        * a_in ** (alpha + 2.0)
        / (v_over_mu**2 * lambda_in**alpha)
    )
    continuum_factor = diagnostic["continuum_slowing_factor"]
    continuum_residual = max(
        relative_error(
            diagnostic["continuum_energy_over_available_at_input"],
            continuum_ratio,
        ),
        abs(continuum_ratio * continuum_factor ** (alpha + 2.0) - 1.0),
        relative_error(
            diagnostic["continuum_energy_saturation_A_over_mu"],
            a_in * continuum_factor,
        ),
    )

    peak_coupling = diagnostic["benchmark_peak_quartic_coupling"]
    lowest_coupling = diagnostic["saturation_lowest_level_quartic_coupling"]
    perturbative_lambda_bound = diagnostic[
        "perturbative_lambda_upper_bound_at_benchmark_peak"
    ]
    perturbative_bound_residual = abs(
        peak_coupling * perturbative_lambda_bound / lam_phi - 1.0
    )
    energy_lambda_bound = lam_phi / reconstructed_overdraw
    peak_at_energy_bound = peak_coupling * energy_lambda_bound / lam_phi
    lowest_at_energy_bound = lowest_coupling * energy_lambda_bound / lam_phi
    energy_bound_residual = max(
        relative_error(
            diagnostic["energy_control_lambda_upper_bound"],
            energy_lambda_bound,
        ),
        abs(reconstructed_overdraw * energy_lambda_bound / lam_phi - 1.0),
        max(0.0, peak_at_energy_bound - 1.0),
        max(0.0, lowest_at_energy_bound - 1.0),
    )

    saturation_rows = saturation_curve(parent)
    write_csv(args.output / "energy_saturation_curve.csv", saturation_rows)
    radiative_rows = radiative_scaling(2, [0.5, 1.0, 2.0])
    write_csv(args.output / "radiative_scaling.csv", radiative_rows)

    checks = [
        {
            "id": "COV01",
            "family": "symmetry",
            "short_label": "level orthogonal",
            "statement": "Level-orthogonal invariance leaves one scalar coefficient per level",
            "status": "PASS" if invariant_nullity == 3 else "FAIL",
            "residual": abs(invariant_nullity - 3),
            "tolerance": 0,
            "expected": "pass",
            "note": f"computed nullity={invariant_nullity}",
        },
        {
            "id": "COV02",
            "family": "symmetry",
            "short_label": "branch covariance",
            "statement": "Branch-homogeneous covariance leaves one operator coefficient",
            "status": "PASS" if scale_nullity == 1 else "FAIL",
            "residual": abs(scale_nullity - 1),
            "tolerance": 0,
            "expected": "pass",
            "note": f"computed nullity={scale_nullity}",
        },
        {
            "id": "COV03",
            "family": "ward",
            "short_label": "total Ward",
            "statement": "Average and detail energy exchange cancels on shell",
            "status": "PASS" if ward["total"] < 1.0e-12 else "FAIL",
            "residual": ward["total"],
            "tolerance": 1.0e-12,
            "expected": "pass",
            "note": "finite-depth random state",
        },
        {
            "id": "COV04",
            "family": "ward",
            "short_label": "omitted exchange",
            "statement": "Omitting the average-mode exchange produces a nonzero continuity defect",
            "status": "PASS" if ward["omitted_exchange"] > 1.0e-8 else "FAIL",
            "residual": ward["omitted_exchange"],
            "tolerance": 1.0e-8,
            "expected": "fail",
            "note": "negative control",
        },
        {
            "id": "ADM01",
            "family": "constraint",
            "short_label": "spectral headroom",
            "statement": "Matter Hamiltonian brackets close on the momentum constraint",
            "status": "PASS" if spectral < 1.0e-10 else "FAIL",
            "residual": spectral,
            "tolerance": 1.0e-10,
            "expected": "pass",
            "note": "N=128, band=3",
        },
        {
            "id": "ADM02",
            "family": "constraint",
            "short_label": "aliasing",
            "statement": "Violating spectral headroom creates a bracket defect",
            "status": "PASS" if aliased > 1.0e-8 else "FAIL",
            "residual": aliased,
            "tolerance": 1.0e-8,
            "expected": "fail",
            "note": "negative control, N=64, band=18",
        },
        {
            "id": "ADM03",
            "family": "constraint",
            "short_label": "finite difference",
            "statement": "Centered differences fail exact nonlinear closure",
            "status": "PASS" if finite_difference > 1.0e-8 else "FAIL",
            "residual": finite_difference,
            "tolerance": 1.0e-8,
            "expected": "fail",
            "note": "negative control",
        },
        {
            "id": "ADM04",
            "family": "constraint",
            "short_label": "missing gradient",
            "statement": "Dropping the detail gradient breaks the bracket identity",
            "status": "PASS" if omitted_gradient > 1.0e-8 else "FAIL",
            "residual": omitted_gradient,
            "tolerance": 1.0e-8,
            "expected": "fail",
            "note": "negative control for an incomplete scalar constraint",
        },
        {
            "id": "UNI01",
            "family": "universality",
            "short_label": "sigma-one constants",
            "statement": "General-sigma constants reduce to the sigma=1 closed forms",
            "status": "PASS" if sigma1_residual < 1.0e-12 else "FAIL",
            "residual": sigma1_residual,
            "tolerance": 1.0e-12,
            "expected": "pass",
            "note": "maximum relative error over C_N, C_R, C_E, and C_P",
        },
        {
            "id": "UNI02",
            "family": "universality",
            "short_label": "outer quad s=.5",
            "statement": "Independent continuum-mass quadrature reproduces sigma=0.5 constants",
            "status": "PASS" if outer_residuals[0.5] < 1.0e-8 else "FAIL",
            "residual": outer_residuals[0.5],
            "tolerance": 1.0e-8,
            "expected": "pass",
            "note": "maximum relative error over all four moments",
        },
        {
            "id": "UNI03",
            "family": "universality",
            "short_label": "outer quad s=1",
            "statement": "Independent continuum-mass quadrature reproduces sigma=1 constants",
            "status": "PASS" if outer_residuals[1.0] < 1.0e-8 else "FAIL",
            "residual": outer_residuals[1.0],
            "tolerance": 1.0e-8,
            "expected": "pass",
            "note": "maximum relative error over all four moments",
        },
        {
            "id": "UNI04",
            "family": "universality",
            "short_label": "outer quad s=2",
            "statement": "Independent continuum-mass quadrature reproduces sigma=2 constants",
            "status": "PASS" if outer_residuals[2.0] < 1.0e-8 else "FAIL",
            "residual": outer_residuals[2.0],
            "tolerance": 1.0e-8,
            "expected": "pass",
            "note": "maximum relative error over all four moments",
        },
        {
            "id": "QUA01",
            "family": "quadrature",
            "short_label": "Laguerre 96/128",
            "statement": "Benchmark energy and pressure converge between 96 and 128 nodes",
            "status": "PASS" if quadrature_residual < 1.0e-9 else "FAIL",
            "residual": quadrature_residual,
            "tolerance": 1.0e-9,
            "expected": "pass",
            "note": "generalized Laguerre alpha=1/2; maximum relative change",
        },
        {
            "id": "BKR01",
            "family": "backreaction",
            "short_label": "energy overdraw",
            "statement": "The frozen benchmark prescribed spectrum exceeds the available energy",
            "status": "PASS"
            if diagnostic["unprojected_energy_over_available"] > 1.0e20
            else "FAIL",
            "residual": diagnostic["unprojected_energy_over_available"],
            "tolerance": 1.0e20,
            "expected": "fail",
            "note": "diagnostic negative result",
        },
        {
            "id": "BKR02",
            "family": "backreaction",
            "short_label": "parent reconstruction",
            "statement": "Discrete quadrature reconstructs the frozen parent overdraw",
            "status": "PASS" if parent_overdraw_residual < 1.0e-10 else "FAIL",
            "residual": parent_overdraw_residual,
            "tolerance": 1.0e-10,
            "expected": "pass",
            "note": f"reconstructed ratio={reconstructed_overdraw:.12e}",
        },
        {
            "id": "BKR03",
            "family": "backreaction",
            "short_label": "threshold root",
            "statement": "The reported discrete threshold solves R_disc=1",
            "status": "PASS" if threshold_residual < 1.0e-10 else "FAIL",
            "residual": threshold_residual,
            "tolerance": 1.0e-10,
            "expected": "pass",
            "note": f"R_disc={threshold_ratio:.16g}",
        },
        {
            "id": "BKR04",
            "family": "backreaction",
            "short_label": "continuum identity",
            "statement": "Raw-continuum slowing uses its own absolute energy coefficient",
            "status": "PASS" if continuum_residual < 1.0e-12 else "FAIL",
            "residual": continuum_residual,
            "tolerance": 1.0e-12,
            "expected": "pass",
            "note": f"raw input ratio={continuum_ratio:.12e}",
        },
        {
            "id": "CPL01",
            "family": "coupling",
            "short_label": "nominal coupling",
            "statement": "The printed perturbative lambda bound sets g_peak=1",
            "status": "PASS" if perturbative_bound_residual < 1.0e-12 else "FAIL",
            "residual": perturbative_bound_residual,
            "tolerance": 1.0e-12,
            "expected": "pass",
            "note": f"lambda_bound={perturbative_lambda_bound:.12e}",
        },
        {
            "id": "CPL02",
            "family": "coupling",
            "short_label": "energy-control lambda",
            "statement": "The no-overdraw lambda bound also leaves benchmark couplings below one",
            "status": "PASS" if energy_bound_residual < 1.0e-10 else "FAIL",
            "residual": energy_bound_residual,
            "tolerance": 1.0e-10,
            "expected": "pass",
            "note": (
                f"lambda={energy_lambda_bound:.12e}, "
                f"g_peak={peak_at_energy_bound:.6g}, "
                f"g_1={lowest_at_energy_bound:.6g}"
            ),
        },
    ]
    write_csv(args.output / "verification_checks.csv", checks)
    (args.output / "backreaction_audit.json").write_text(
        json.dumps(diagnostic, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    summary = {
        "checks": len(checks),
        "pass": sum(r["status"] == "PASS" for r in checks),
        "fail": sum(r["status"] == "FAIL" for r in checks),
        "negative_controls": sum(r["expected"] == "fail" for r in checks),
        "parent_capture_normalization": diagnostic["eta"],
        "unprojected_energy_over_available": diagnostic[
            "unprojected_energy_over_available"
        ],
        "claim_boundary": "Internal analytic and numerical audit, not external reproduction or empirical confirmation",
    }
    (args.output / "verification_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    build_figures(
        args.figures,
        continuum_rows,
        convergence_rows,
        radiative_rows,
        saturation_rows,
        checks,
        diagnostic,
    )
    if summary["fail"]:
        raise SystemExit(f"verification failures: {summary['fail']}")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
