from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import json
import math

import numpy as np
import pandas as pd
from scipy.integrate import cumulative_trapezoid, solve_ivp
from scipy.interpolate import PchipInterpolator, RegularGridInterpolator
from scipy.optimize import brentq
from scipy.special import sici
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
FIG = ROOT / "figures"
PARENT = ROOT / "parent"
DATA.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class Params:
    h0_km_s_mpc: float = 70.0
    omega_b0: float = 0.049
    omega_d0: float = 0.261
    omega_r0: float = 9.0e-5
    n_s: float = 0.965
    sigma8: float = 0.81
    a_star: float = 1.0e-6
    delta_c_eds: float = 1.686
    st_a: float = 0.707
    st_p: float = 0.3
    st_A: float = 0.3222
    formation_fraction: float = 0.04
    concentration_floor: float = 4.0
    atomic_mass_norm_msun: float = 1.0e8
    seed: int = 20260812


P = Params()
H = P.h0_km_s_mpc / 100.0
OMEGA_M = P.omega_b0 + P.omega_d0
OMEGA_V = 1.0 - OMEGA_M - P.omega_r0
C_KM_S = 299792.458
H0_OVER_C_MPC = P.h0_km_s_mpc / C_KM_S
RHO_CRIT = 2.77536627e11 * H**2  # Msun / Mpc^3
RHO_M = OMEGA_M * RHO_CRIT


def e2_a(a: np.ndarray | float) -> np.ndarray:
    aa = np.asarray(a, dtype=float)
    return P.omega_r0 * aa**-4 + OMEGA_M * aa**-3 + OMEGA_V


def e_z(z: np.ndarray | float) -> np.ndarray:
    zz = np.asarray(z, dtype=float)
    return np.sqrt(P.omega_r0 * (1.0 + zz) ** 4 + OMEGA_M * (1.0 + zz) ** 3 + OMEGA_V)


def build_growth() -> tuple[callable, np.ndarray, np.ndarray]:
    n_initial = math.log(1.0e-4)

    def rhs(n: float, y: np.ndarray) -> list[float]:
        a = math.exp(n)
        e2 = float(e2_a(a))
        dln_h = -0.5 * (
            4.0 * P.omega_r0 * a**-4 + 3.0 * OMEGA_M * a**-3
        ) / e2
        omega_m = OMEGA_M * a**-3 / e2
        return [float(y[1]), -(2.0 + dln_h) * float(y[1]) + 1.5 * omega_m * float(y[0])]

    sol = solve_ivp(
        rhs,
        (n_initial, 0.0),
        [1.0e-4, 1.0e-4],
        rtol=1.0e-11,
        atol=1.0e-13,
        max_step=0.02,
        dense_output=True,
    )
    if not sol.success:
        raise RuntimeError(sol.message)
    norm = float(sol.sol(0.0)[0])

    def growth(z: np.ndarray | float) -> np.ndarray:
        zz = np.asarray(z, dtype=float)
        return np.asarray(sol.sol(np.log(1.0 / (1.0 + zz)))[0] / norm, dtype=float)

    z_inv = np.concatenate([[0.0], np.geomspace(1.0e-4, 50.0, 5000)])
    d_inv = growth(z_inv)
    return growth, z_inv, d_inv


GROWTH, Z_INV, D_INV = build_growth()


def z_from_growth(target: np.ndarray | float) -> np.ndarray:
    tt = np.asarray(target, dtype=float)
    return np.interp(np.clip(tt, D_INV[-1], 1.0), D_INV[::-1], Z_INV[::-1])


def spherical_collapse_delta_c(z_c: float, threshold: float = 1.0e7) -> float:
    n_initial = math.log(1.0e-4)
    n_c = math.log(1.0 / (1.0 + z_c))

    def nonlinear_rhs(n: float, y: np.ndarray) -> list[float]:
        a = math.exp(n)
        e2 = float(e2_a(a))
        dln_h = -0.5 * (
            4.0 * P.omega_r0 * a**-4 + 3.0 * OMEGA_M * a**-3
        ) / e2
        omega_m = OMEGA_M * a**-3 / e2
        delta, derivative = float(y[0]), float(y[1])
        return [
            derivative,
            -(2.0 + dln_h) * derivative
            + (4.0 / 3.0) * derivative**2 / (1.0 + delta)
            + 1.5 * omega_m * delta * (1.0 + delta),
        ]

    def collapse_measure(delta_i: float) -> float:
        def event(_: float, y: np.ndarray) -> float:
            return float(y[0] - threshold)

        event.terminal = True
        event.direction = 1
        sol = solve_ivp(
            nonlinear_rhs,
            (n_initial, n_c),
            [delta_i, delta_i],
            events=event,
            rtol=2.0e-9,
            atol=2.0e-12,
            max_step=0.02,
        )
        if len(sol.t_events[0]) > 0:
            return n_c - float(sol.t_events[0][0])
        return -math.log(threshold / max(float(sol.y[0, -1]), 1.0e-30))

    upper = 1.0e-2
    while collapse_measure(upper) <= 0.0:
        upper *= 2.0
    delta_i = brentq(collapse_measure, 1.0e-6, upper, xtol=2.0e-12, rtol=2.0e-10)

    def linear_rhs(n: float, y: np.ndarray) -> list[float]:
        a = math.exp(n)
        e2 = float(e2_a(a))
        dln_h = -0.5 * (
            4.0 * P.omega_r0 * a**-4 + 3.0 * OMEGA_M * a**-3
        ) / e2
        omega_m = OMEGA_M * a**-3 / e2
        return [float(y[1]), -(2.0 + dln_h) * float(y[1]) + 1.5 * omega_m * float(y[0])]

    linear = solve_ivp(
        linear_rhs,
        (n_initial, n_c),
        [delta_i, delta_i],
        rtol=1.0e-11,
        atol=1.0e-13,
    )
    return float(linear.y[0, -1])


COLLAPSE_Z = np.array([0.0, 0.5, 1.0, 2.0, 3.0, 5.0])
COLLAPSE_DC = np.array([spherical_collapse_delta_c(float(z)) for z in COLLAPSE_Z])
DC_INTERP = PchipInterpolator(COLLAPSE_Z, COLLAPSE_DC, extrapolate=True)


def delta_c(z: float) -> float:
    value = float(DC_INTERP(z))
    return min(max(value, 1.65), 1.71)


def top_hat_window(x: np.ndarray) -> np.ndarray:
    xx = np.asarray(x, dtype=float)
    out = np.empty_like(xx)
    small = np.abs(xx) < 1.0e-3
    out[small] = 1.0 - xx[small] ** 2 / 10.0
    xs = xx[~small]
    out[~small] = 3.0 * (np.sin(xs) - xs * np.cos(xs)) / xs**3
    return out


def smooth_transfer(k: np.ndarray) -> np.ndarray:
    q = np.asarray(k, dtype=float) / (OMEGA_M * H * H)
    return (
        np.log1p(2.34 * q)
        / (2.34 * q)
        * (
            1.0
            + 3.89 * q
            + (16.1 * q) ** 2
            + (5.46 * q) ** 3
            + (6.71 * q) ** 4
        )
        ** (-0.25)
    )


class DarkTransfer:
    def __init__(self) -> None:
        tab = pd.read_csv(PARENT / "collisionless_dark_transfer_curve.csv")
        self.k = tab["k_per_Mpc_for_H0_70"].to_numpy(float)
        self.t = np.clip(tab["collisionless_transfer_amplitude_z0"].to_numpy(float), 1.0e-10, 1.0)
        self._interp = PchipInterpolator(np.log(self.k), np.log(self.t), extrapolate=True)
        self._tail_slope = float(np.polyfit(np.log(self.k[-6:]), np.log(self.t[-6:]), 1)[0])

    def __call__(self, k: np.ndarray | float, scale: float = 1.0) -> np.ndarray:
        kk = np.asarray(k, dtype=float) * scale
        out = np.ones_like(kk)
        inside = (kk >= self.k[0]) & (kk <= self.k[-1])
        out[inside] = np.exp(self._interp(np.log(kk[inside])))
        high = kk > self.k[-1]
        out[high] = self.t[-1] * (kk[high] / self.k[-1]) ** self._tail_slope
        return np.clip(out, 1.0e-10, 1.0)


DARK_TRANSFER = DarkTransfer()

K_LINEAR = np.geomspace(1.0e-5, 300.0, 8000)
SHAPE = K_LINEAR**P.n_s * smooth_transfer(K_LINEAR) ** 2
R8 = 8.0 / H
VARIANCE_SHAPE = np.trapezoid(
    K_LINEAR**3 * SHAPE * top_hat_window(K_LINEAR * R8) ** 2 / (2.0 * math.pi**2),
    np.log(K_LINEAR),
)
POWER_AMPLITUDE = P.sigma8**2 / VARIANCE_SHAPE
P_COLD_0 = POWER_AMPLITUDE * SHAPE
P_COLD_INTERP = PchipInterpolator(np.log(K_LINEAR), np.log(P_COLD_0), extrapolate=True)
SIGMA8_CHECK = math.sqrt(
    float(
        np.trapezoid(
            K_LINEAR**3 * P_COLD_0 * top_hat_window(K_LINEAR * R8) ** 2 / (2.0 * math.pi**2),
            np.log(K_LINEAR),
        )
    )
)


def sigma_from_delta(radii: np.ndarray, delta2: np.ndarray) -> np.ndarray:
    results: list[float] = []
    log_k = np.log(K_LINEAR)
    for chunk in np.array_split(np.asarray(radii, dtype=float), 14):
        window = top_hat_window(np.outer(K_LINEAR, chunk))
        values = np.sqrt(np.trapezoid(delta2[:, None] * window**2, log_k, axis=0))
        results.extend(values.tolist())
    return np.asarray(results)


MASS_GRID = np.geomspace(1.0e5, 1.0e16, 700)
RADIUS_GRID = (3.0 * MASS_GRID / (4.0 * math.pi * RHO_M)) ** (1.0 / 3.0)
DELTA2_COLD = K_LINEAR**3 * P_COLD_0 / (2.0 * math.pi**2)
DELTA2_DARK = DELTA2_COLD * DARK_TRANSFER(K_LINEAR) ** 2
SIGMA_COLD_0 = sigma_from_delta(RADIUS_GRID, DELTA2_COLD)
SIGMA_DARK_0 = sigma_from_delta(RADIUS_GRID, DELTA2_DARK)
SIGMA_COLD_INTERP = PchipInterpolator(np.log(MASS_GRID), np.log(SIGMA_COLD_0), extrapolate=True)
SIGMA_DARK_INTERP = PchipInterpolator(np.log(MASS_GRID), np.log(SIGMA_DARK_0), extrapolate=True)


def sigma0_mass(mass: np.ndarray | float, dark: bool) -> np.ndarray:
    interp = SIGMA_DARK_INTERP if dark else SIGMA_COLD_INTERP
    return np.exp(interp(np.log(np.asarray(mass, dtype=float))))


def mass_function(z: float, dark: bool, mass: np.ndarray = MASS_GRID) -> dict[str, np.ndarray | float]:
    sigma0 = sigma0_mass(mass, dark)
    sigma = sigma0 * float(GROWTH(z))
    log_mass = np.log(mass)
    dln_sigma = np.gradient(np.log(sigma), log_mass)
    dc = delta_c(z)
    nu = dc / sigma
    multiplicity = (
        P.st_A
        * math.sqrt(2.0 * P.st_a / math.pi)
        * (1.0 + (P.st_a * nu**2) ** (-P.st_p))
        * nu
        * np.exp(-0.5 * P.st_a * nu**2)
    )
    dn_dlnm = RHO_M / mass * multiplicity * np.abs(-dln_sigma)
    bias = (
        1.0
        + (P.st_a * nu**2 - 1.0) / dc
        + 2.0 * P.st_p / (dc * (1.0 + (P.st_a * nu**2) ** P.st_p))
    )
    return {
        "mass": mass,
        "sigma": sigma,
        "nu": nu,
        "dn_dlnm": dn_dlnm,
        "bias": bias,
        "delta_c": dc,
    }


def formation_concentration(mass: np.ndarray, z: float, dark: bool) -> tuple[np.ndarray, np.ndarray]:
    sigma_f = sigma0_mass(P.formation_fraction * mass, dark)
    target_growth = P.delta_c_eds / sigma_f
    z_formation = np.maximum(z_from_growth(target_growth), z)
    concentration = P.concentration_floor * (1.0 + z_formation) / (1.0 + z)
    return concentration, z_formation


def nfw_fourier(k: np.ndarray, mass: np.ndarray, z: float, dark: bool) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    concentration, z_formation = formation_concentration(mass, z, dark)
    radius_200m = (3.0 * mass / (4.0 * math.pi * 200.0 * RHO_M)) ** (1.0 / 3.0)
    radius_s = radius_200m / concentration
    x = np.asarray(k, dtype=float)[:, None] * radius_s[None, :]
    si_upper, ci_upper = sici((1.0 + concentration)[None, :] * x)
    si_lower, ci_lower = sici(x)
    numerator = (
        np.sin(x) * (si_upper - si_lower)
        + np.cos(x) * (ci_upper - ci_lower)
        - np.sin(concentration[None, :] * x) / ((1.0 + concentration)[None, :] * x)
    )
    denominator = np.log(1.0 + concentration) - concentration / (1.0 + concentration)
    u = numerator / denominator[None, :]
    u = np.where(x < 1.0e-4, 1.0, u)
    return u, concentration, z_formation


def halo_model(z: float, dark: bool, k: np.ndarray, mass: np.ndarray = MASS_GRID) -> dict[str, np.ndarray | float]:
    mf = mass_function(z, dark, mass)
    dn = np.asarray(mf["dn_dlnm"])
    bias = np.asarray(mf["bias"])
    log_mass = np.log(mass)
    u, concentration, z_formation = nfw_fourier(k, mass, z, dark)
    lagrangian_radius = (3.0 * mass / (4.0 * math.pi * RHO_M)) ** (1.0 / 3.0)
    window = top_hat_window(np.outer(k, lagrangian_radius))
    bias_weight = dn * (mass / RHO_M) * bias
    bias_norm = float(np.trapezoid(bias_weight, log_mass))
    i1 = np.trapezoid(u * bias_weight[None, :], log_mass, axis=1) / bias_norm
    one_halo = np.trapezoid(
        (u - window) ** 2 * (dn * (mass / RHO_M) ** 2)[None, :],
        log_mass,
        axis=1,
    )
    linear = np.exp(P_COLD_INTERP(np.log(k))) * float(GROWTH(z)) ** 2
    if dark:
        linear *= DARK_TRANSFER(k) ** 2
    two_halo = i1**2 * linear
    return {
        "k": k,
        "linear": linear,
        "one_halo": one_halo,
        "two_halo": two_halo,
        "nonlinear": one_halo + two_halo,
        "bias_norm": bias_norm,
        "concentration": concentration,
        "z_formation": z_formation,
        "mass_function": mf,
    }


def collapsed_fraction(z: float, dark: bool, minimum_mass: float) -> float:
    mf = mass_function(z, dark)
    mass = np.asarray(mf["mass"])
    dn = np.asarray(mf["dn_dlnm"])
    mask = mass >= minimum_mass
    return float(np.trapezoid(dn[mask] * mass[mask] / RHO_M, np.log(mass[mask])))


def atomic_cooling_mass(z: float) -> float:
    return P.atomic_mass_norm_msun * ((1.0 + z) / 10.0) ** (-1.5)


def sigma_grid_for_scale(scale: float, mass: np.ndarray) -> np.ndarray:
    radii = (3.0 * mass / (4.0 * math.pi * RHO_M)) ** (1.0 / 3.0)
    delta2 = DELTA2_COLD * DARK_TRANSFER(K_LINEAR, scale=scale) ** 2
    return sigma_from_delta(radii, delta2)


def collapsed_fraction_from_sigma(z: float, sigma0: np.ndarray, mass: np.ndarray, minimum_mass: float) -> float:
    sigma = sigma0 * float(GROWTH(z))
    log_mass = np.log(mass)
    dln_sigma = np.gradient(np.log(sigma), log_mass)
    dc = delta_c(z)
    nu = dc / sigma
    multiplicity = (
        P.st_A
        * math.sqrt(2.0 * P.st_a / math.pi)
        * (1.0 + (P.st_a * nu**2) ** (-P.st_p))
        * nu
        * np.exp(-0.5 * P.st_a * nu**2)
    )
    dn = RHO_M / mass * multiplicity * np.abs(-dln_sigma)
    mask = mass >= minimum_mass
    return float(np.trapezoid(dn[mask] * mass[mask] / RHO_M, log_mass[mask]))


def build_distance() -> callable:
    z = np.linspace(0.0, 5.0, 30000)
    chi = np.concatenate([[0.0], cumulative_trapezoid(C_KM_S / P.h0_km_s_mpc / e_z(z), z)])
    return PchipInterpolator(z, chi)


CHI = build_distance()


def nonlinear_power_grid(z_nodes: np.ndarray, k_nodes: np.ndarray, mass: np.ndarray = MASS_GRID) -> tuple[np.ndarray, np.ndarray]:
    cold: list[np.ndarray] = []
    dark: list[np.ndarray] = []
    for z in z_nodes:
        cold.append(np.asarray(halo_model(float(z), False, k_nodes, mass)["nonlinear"]))
        dark.append(np.asarray(halo_model(float(z), True, k_nodes, mass)["nonlinear"]))
    return np.asarray(cold), np.asarray(dark)


def projected_lensing_ratios(
    source_z: float,
    ell: np.ndarray,
    z_nodes: np.ndarray,
    k_nodes: np.ndarray,
    cold_power: np.ndarray,
    dark_power: np.ndarray,
    integration_points: int = 800,
) -> np.ndarray:
    cold_interp = RegularGridInterpolator(
        (z_nodes, np.log(k_nodes)), np.log(cold_power), bounds_error=False, fill_value=None
    )
    dark_interp = RegularGridInterpolator(
        (z_nodes, np.log(k_nodes)), np.log(dark_power), bounds_error=False, fill_value=None
    )
    z = np.linspace(1.0e-4, source_z, integration_points)
    chi = np.asarray(CHI(z), dtype=float)
    chi_source = float(CHI(source_z))
    dchi_dz = C_KM_S / P.h0_km_s_mpc / e_z(z)
    kernel = (
        1.5
        * OMEGA_M
        * H0_OVER_C_MPC**2
        * (1.0 + z)
        * chi
        * (chi_source - chi)
        / chi_source
    )
    ratios: list[float] = []
    for multipole in ell:
        kval = np.clip((float(multipole) + 0.5) / chi, k_nodes[0], k_nodes[-1])
        points = np.column_stack([np.clip(z, z_nodes[0], z_nodes[-1]), np.log(kval)])
        cold = np.exp(cold_interp(points))
        dark = np.exp(dark_interp(points))
        projection = (kernel / chi) ** 2 * dchi_dz
        cold_cl = float(np.trapezoid(projection * cold, z))
        dark_cl = float(np.trapezoid(projection * dark, z))
        ratios.append(dark_cl / cold_cl)
    return np.asarray(ratios)


# ---------------------------------------------------------------------------
# Principal calculations.
# ---------------------------------------------------------------------------
K_HALF_POWER = brentq(lambda kval: float(DARK_TRANSFER(kval) ** 2 - 0.5), 2.0, 20.0)
K_HALF_AMPLITUDE = brentq(lambda kval: float(DARK_TRANSFER(kval) - 0.5), 2.0, 30.0)
M_HALF_POWER = 4.0 * math.pi / 3.0 * RHO_M * (math.pi / K_HALF_POWER) ** 3
M_HALF_AMPLITUDE = 4.0 * math.pi / 3.0 * RHO_M * (math.pi / K_HALF_AMPLITUDE) ** 3

MASS_SAMPLES = np.array([1.0e7, 1.0e8, 1.0e9, 1.0e10, 1.0e11, 1.0e12, 1.0e13])
REDSHIFT_SAMPLES = np.array([0.0, 1.0, 3.0, 6.0, 8.0])
MASS_ROWS: list[dict[str, float]] = []
for z in REDSHIFT_SAMPLES:
    cold_mf = mass_function(float(z), False)
    dark_mf = mass_function(float(z), True)
    cold_interp = PchipInterpolator(
        np.log(np.asarray(cold_mf["mass"])), np.log(np.asarray(cold_mf["dn_dlnm"])), extrapolate=True
    )
    dark_interp = PchipInterpolator(
        np.log(np.asarray(dark_mf["mass"])), np.log(np.asarray(dark_mf["dn_dlnm"])), extrapolate=True
    )
    for mass in MASS_SAMPLES:
        cold_value = float(np.exp(cold_interp(math.log(mass))))
        dark_value = float(np.exp(dark_interp(math.log(mass))))
        MASS_ROWS.append(
            {
                "z": float(z),
                "mass_msun": float(mass),
                "cold_dn_dlnM_Mpc3": cold_value,
                "refinement_dn_dlnM_Mpc3": dark_value,
                "refinement_to_cold_ratio": dark_value / cold_value,
            }
        )
MASS_TABLE = pd.DataFrame(MASS_ROWS)
MASS_TABLE.to_csv(DATA / "halo_mass_function_ratios.csv", index=False)

CONCENTRATION_ROWS: list[dict[str, float]] = []
for mass in MASS_SAMPLES:
    cold_c, cold_zf = formation_concentration(np.array([mass]), 0.0, False)
    dark_c, dark_zf = formation_concentration(np.array([mass]), 0.0, True)
    CONCENTRATION_ROWS.append(
        {
            "mass_msun": float(mass),
            "cold_formation_redshift": float(cold_zf[0]),
            "refinement_formation_redshift": float(dark_zf[0]),
            "cold_concentration": float(cold_c[0]),
            "refinement_concentration": float(dark_c[0]),
            "concentration_ratio": float(dark_c[0] / cold_c[0]),
        }
    )
CONCENTRATION_TABLE = pd.DataFrame(CONCENTRATION_ROWS)
CONCENTRATION_TABLE.to_csv(DATA / "halo_concentration_ratios.csv", index=False)

K_HALO = np.geomspace(1.0e-4, 150.0, 260)
POWER_ROWS: list[dict[str, float]] = []
HALO_RESULTS: dict[float, tuple[dict[str, np.ndarray | float], dict[str, np.ndarray | float]]] = {}
for z in [0.0, 1.0, 2.0]:
    cold = halo_model(z, False, K_HALO)
    dark = halo_model(z, True, K_HALO)
    HALO_RESULTS[z] = (cold, dark)
    for index, kval in enumerate(K_HALO):
        POWER_ROWS.append(
            {
                "z": z,
                "k_per_Mpc": float(kval),
                "cold_linear": float(np.asarray(cold["linear"])[index]),
                "refinement_linear": float(np.asarray(dark["linear"])[index]),
                "cold_one_halo": float(np.asarray(cold["one_halo"])[index]),
                "refinement_one_halo": float(np.asarray(dark["one_halo"])[index]),
                "cold_nonlinear": float(np.asarray(cold["nonlinear"])[index]),
                "refinement_nonlinear": float(np.asarray(dark["nonlinear"])[index]),
                "linear_ratio": float(np.asarray(dark["linear"])[index] / np.asarray(cold["linear"])[index]),
                "nonlinear_ratio": float(np.asarray(dark["nonlinear"])[index] / np.asarray(cold["nonlinear"])[index]),
            }
        )
POWER_TABLE = pd.DataFrame(POWER_ROWS)
POWER_TABLE.to_csv(DATA / "nonlinear_power_ratios.csv", index=False)

REIONIZATION_ROWS: list[dict[str, float]] = []
for z in [6.0, 7.4, 8.0, 10.0]:
    minimum_mass = atomic_cooling_mass(z)
    cold_fraction = collapsed_fraction(z, False, minimum_mass)
    dark_fraction = collapsed_fraction(z, True, minimum_mass)
    REIONIZATION_ROWS.append(
        {
            "z": z,
            "atomic_cooling_mass_msun": minimum_mass,
            "cold_collapsed_fraction": cold_fraction,
            "refinement_collapsed_fraction": dark_fraction,
            "refinement_to_cold_fraction": dark_fraction / cold_fraction,
            "required_efficiency_penalty": cold_fraction / dark_fraction,
        }
    )
REIONIZATION_TABLE = pd.DataFrame(REIONIZATION_ROWS)

MASS_REION = np.geomspace(1.0e5, 1.0e16, 900)
RADIUS_REION = (3.0 * MASS_REION / (4.0 * math.pi * RHO_M)) ** (1.0 / 3.0)
SIGMA_REION_COLD = sigma_from_delta(RADIUS_REION, DELTA2_COLD)
Z_REION = 7.4
M_REION = atomic_cooling_mass(Z_REION)
FCOLL_REION_COLD = collapsed_fraction_from_sigma(Z_REION, SIGMA_REION_COLD, MASS_REION, M_REION)


def efficiency_penalty(scale: float) -> float:
    sigma_scaled = sigma_grid_for_scale(scale, MASS_REION)
    dark_fraction = collapsed_fraction_from_sigma(Z_REION, sigma_scaled, MASS_REION, M_REION)
    return FCOLL_REION_COLD / dark_fraction


SCALE_ROWS: list[dict[str, float]] = []
for target in [1.5, 2.0, 3.0, 5.0]:
    scale = brentq(lambda value: efficiency_penalty(value) - target, 0.1, 3.0)
    SCALE_ROWS.append(
        {
            "maximum_efficiency_penalty": target,
            "maximum_a_star": P.a_star * scale,
            "transfer_scale_ratio": scale,
            "minimum_half_mode_k_per_Mpc": K_HALF_POWER / scale,
        }
    )
SCALE_TABLE = pd.DataFrame(SCALE_ROWS)
SCALE_TABLE.to_csv(DATA / "production_epoch_reionization_bounds.csv", index=False)
REIONIZATION_TABLE.to_csv(DATA / "reionization_consistency.csv", index=False)

Z_NODES = np.linspace(0.0, 2.5, 26)
K_NODES = np.geomspace(1.0e-3, 200.0, 240)
COLD_POWER_GRID, DARK_POWER_GRID = nonlinear_power_grid(Z_NODES, K_NODES)
ELL_VALUES = np.array([1000.0, 3000.0, 5000.0, 10000.0])
LENSING_ROWS: list[dict[str, float]] = []
LINEAR_LENSING = pd.read_csv(PARENT / "linear_lensing_ratios.csv")
for source_z in [0.5, 1.0, 2.0]:
    ratios = projected_lensing_ratios(
        source_z, ELL_VALUES, Z_NODES, K_NODES, COLD_POWER_GRID, DARK_POWER_GRID
    )
    for ell, ratio in zip(ELL_VALUES, ratios):
        linear_match = LINEAR_LENSING[
            (np.isclose(LINEAR_LENSING["z_source"], source_z))
            & (np.isclose(LINEAR_LENSING["ell"], ell))
        ]
        linear_ratio = float(linear_match["linear_lensing_power_ratio"].iloc[0]) if len(linear_match) else math.nan
        LENSING_ROWS.append(
            {
                "source_z": source_z,
                "ell": ell,
                "linear_ratio_from_parent": linear_ratio,
                "nonlinear_halo_model_ratio": float(ratio),
                "nonlinear_minus_linear": float(ratio - linear_ratio) if math.isfinite(linear_ratio) else math.nan,
            }
        )
LENSING_TABLE = pd.DataFrame(LENSING_ROWS)
LENSING_TABLE.to_csv(DATA / "nonlinear_lensing_ratios.csv", index=False)

# ---------------------------------------------------------------------------
# Convergence controls.
# ---------------------------------------------------------------------------
COARSE_MASS = np.geomspace(1.0e5, 1.0e16, 500)
COARSE_K = np.geomspace(1.0e-3, 150.0, 180)
# Build coarse sigma interpolants temporarily by direct integration.
coarse_radius = (3.0 * COARSE_MASS / (4.0 * math.pi * RHO_M)) ** (1.0 / 3.0)
coarse_sigma_cold = sigma_from_delta(coarse_radius, DELTA2_COLD)
coarse_sigma_dark = sigma_from_delta(coarse_radius, DELTA2_DARK)
original_cold_interp = SIGMA_COLD_INTERP
original_dark_interp = SIGMA_DARK_INTERP
# The convergence check uses a local halo-model variant with supplied sigma arrays.
def halo_model_supplied(z: float, dark: bool, kvals: np.ndarray, mass: np.ndarray, sigma0: np.ndarray) -> np.ndarray:
    sigma = sigma0 * float(GROWTH(z))
    log_mass = np.log(mass)
    dln_sigma = np.gradient(np.log(sigma), log_mass)
    dc = delta_c(z)
    nu = dc / sigma
    multiplicity = (
        P.st_A
        * math.sqrt(2.0 * P.st_a / math.pi)
        * (1.0 + (P.st_a * nu**2) ** (-P.st_p))
        * nu
        * np.exp(-0.5 * P.st_a * nu**2)
    )
    dn = RHO_M / mass * multiplicity * np.abs(-dln_sigma)
    bias = 1.0 + (P.st_a * nu**2 - 1.0) / dc + 2.0 * P.st_p / (
        dc * (1.0 + (P.st_a * nu**2) ** P.st_p)
    )
    sigma_interp_local = PchipInterpolator(np.log(mass), np.log(sigma0), extrapolate=True)
    sigma_f = np.exp(sigma_interp_local(np.log(P.formation_fraction * mass)))
    z_formation = np.maximum(z_from_growth(P.delta_c_eds / sigma_f), z)
    concentration = P.concentration_floor * (1.0 + z_formation) / (1.0 + z)
    radius_200m = (3.0 * mass / (4.0 * math.pi * 200.0 * RHO_M)) ** (1.0 / 3.0)
    radius_s = radius_200m / concentration
    x = kvals[:, None] * radius_s[None, :]
    si_upper, ci_upper = sici((1.0 + concentration)[None, :] * x)
    si_lower, ci_lower = sici(x)
    numerator = (
        np.sin(x) * (si_upper - si_lower)
        + np.cos(x) * (ci_upper - ci_lower)
        - np.sin(concentration[None, :] * x) / ((1.0 + concentration)[None, :] * x)
    )
    denominator = np.log(1.0 + concentration) - concentration / (1.0 + concentration)
    u = np.where(x < 1.0e-4, 1.0, numerator / denominator[None, :])
    lagrangian_radius = (3.0 * mass / (4.0 * math.pi * RHO_M)) ** (1.0 / 3.0)
    window = top_hat_window(np.outer(kvals, lagrangian_radius))
    weight = dn * (mass / RHO_M) * bias
    i1 = np.trapezoid(u * weight[None, :], log_mass, axis=1) / np.trapezoid(weight, log_mass)
    one = np.trapezoid((u - window) ** 2 * (dn * (mass / RHO_M) ** 2)[None, :], log_mass, axis=1)
    linear = np.exp(P_COLD_INTERP(np.log(kvals))) * float(GROWTH(z)) ** 2
    if dark:
        linear *= DARK_TRANSFER(kvals) ** 2
    return one + i1**2 * linear

coarse_cold = halo_model_supplied(0.0, False, COARSE_K, COARSE_MASS, coarse_sigma_cold)
coarse_dark = halo_model_supplied(0.0, True, COARSE_K, COARSE_MASS, coarse_sigma_dark)
fine_ratio_interp = PchipInterpolator(
    np.log(K_HALO),
    np.log(np.asarray(HALO_RESULTS[0.0][1]["nonlinear"]) / np.asarray(HALO_RESULTS[0.0][0]["nonlinear"])),
)
coarse_ratio = coarse_dark / coarse_cold
fine_on_coarse = np.exp(fine_ratio_interp(np.log(COARSE_K)))
MASS_GRID_DISCREPANCY = float(np.max(np.abs(coarse_ratio - fine_on_coarse) / fine_on_coarse))

Z_NODES_COARSE = np.linspace(0.0, 2.5, 19)
K_NODES_COARSE = np.geomspace(1.0e-3, 200.0, 180)
COLD_COARSE_GRID, DARK_COARSE_GRID = nonlinear_power_grid(Z_NODES_COARSE, K_NODES_COARSE, COARSE_MASS)
LENSING_FINE = projected_lensing_ratios(0.5, ELL_VALUES, Z_NODES, K_NODES, COLD_POWER_GRID, DARK_POWER_GRID)
LENSING_COARSE = projected_lensing_ratios(
    0.5,
    ELL_VALUES,
    Z_NODES_COARSE,
    K_NODES_COARSE,
    COLD_COARSE_GRID,
    DARK_COARSE_GRID,
    integration_points=600,
)
LENSING_GRID_DISCREPANCY = float(np.max(np.abs(LENSING_COARSE - LENSING_FINE) / LENSING_FINE))

small_k = np.geomspace(1.0e-4, 1.0e-2, 30)
small_halo = halo_model(0.0, False, small_k)
ONE_HALO_SLOPE = float(np.polyfit(np.log(small_k), np.log(np.asarray(small_halo["one_halo"])), 1)[0])

# ---------------------------------------------------------------------------
# Verification ledger.
# ---------------------------------------------------------------------------
CHECKS: list[dict[str, object]] = []


def add_check(identifier: str, statement: str, value: float, tolerance: float, condition: bool) -> None:
    CHECKS.append(
        {
            "id": identifier,
            "statement": statement,
            "value": float(value),
            "tolerance": float(tolerance),
            "status": "PASS" if condition else "FAIL",
        }
    )


add_check("NLH01", "sigma8 normalization", abs(SIGMA8_CHECK - P.sigma8), 1.0e-10, abs(SIGMA8_CHECK - P.sigma8) < 1.0e-10)
add_check("NLH02", "transfer bounded between zero and one", float(np.max(DARK_TRANSFER(K_LINEAR)) - 1.0), 1.0e-12, np.all((DARK_TRANSFER(K_LINEAR) >= 0.0) & (DARK_TRANSFER(K_LINEAR) <= 1.0)))
add_check("NLH03", "half-mode root", abs(float(DARK_TRANSFER(K_HALF_POWER) ** 2) - 0.5), 1.0e-10, abs(float(DARK_TRANSFER(K_HALF_POWER) ** 2) - 0.5) < 1.0e-10)
add_check("NLH04", "variance ordering", float(np.max(SIGMA_DARK_0 - SIGMA_COLD_0)), 1.0e-12, np.all(SIGMA_DARK_0 <= SIGMA_COLD_0 + 1.0e-12))
add_check("NLH05", "z=0 spherical collapse threshold", abs(COLLAPSE_DC[0] - 1.67611397), 2.0e-5, abs(COLLAPSE_DC[0] - 1.67611397) < 2.0e-5)
add_check("NLH06", "mass functions positive", float(min(MASS_TABLE["refinement_dn_dlnM_Mpc3"].min(), MASS_TABLE["cold_dn_dlnM_Mpc3"].min())), 0.0, np.all(MASS_TABLE[["refinement_dn_dlnM_Mpc3", "cold_dn_dlnM_Mpc3"]].to_numpy() > 0.0))
ratio_1e8_z0 = float(MASS_TABLE[(MASS_TABLE.z == 0.0) & (MASS_TABLE.mass_msun == 1.0e8)]["refinement_to_cold_ratio"].iloc[0])
ratio_1e13_z0 = float(MASS_TABLE[(MASS_TABLE.z == 0.0) & (MASS_TABLE.mass_msun == 1.0e13)]["refinement_to_cold_ratio"].iloc[0])
ratio_1e8_z8 = float(MASS_TABLE[(MASS_TABLE.z == 8.0) & (MASS_TABLE.mass_msun == 1.0e8)]["refinement_to_cold_ratio"].iloc[0])
add_check("NLH07", "low-mass halo suppression", ratio_1e8_z0, 0.25, ratio_1e8_z0 < 0.25)
add_check("NLH08", "high-mass recovery", abs(ratio_1e13_z0 - 1.0), 0.01, abs(ratio_1e13_z0 - 1.0) < 0.01)
add_check("NLH09", "suppression strengthens at high redshift", ratio_1e8_z8 - ratio_1e8_z0, 0.0, ratio_1e8_z8 < ratio_1e8_z0)
conc_low = float(CONCENTRATION_TABLE[CONCENTRATION_TABLE.mass_msun == 1.0e8]["concentration_ratio"].iloc[0])
conc_high = float(CONCENTRATION_TABLE[CONCENTRATION_TABLE.mass_msun == 1.0e13]["concentration_ratio"].iloc[0])
add_check("NLH10", "low-mass concentrations suppressed", conc_low, 0.8, conc_low < 0.8)
add_check("NLH11", "high-mass concentrations recover", abs(conc_high - 1.0), 0.03, abs(conc_high - 1.0) < 0.03)
add_check("NLH12", "compensated one-halo term scales as k^4", abs(ONE_HALO_SLOPE - 4.0), 0.03, abs(ONE_HALO_SLOPE - 4.0) < 0.03)
add_check("NLH13", "nonlinear spectra positive", float(POWER_TABLE[["cold_nonlinear", "refinement_nonlinear"]].min().min()), 0.0, np.all(POWER_TABLE[["cold_nonlinear", "refinement_nonlinear"]].to_numpy() > 0.0))
add_check("NLH14", "nonlinear power remains ordered", float((POWER_TABLE.refinement_nonlinear / POWER_TABLE.cold_nonlinear).max() - 1.0), 2.0e-3, np.all(POWER_TABLE.refinement_nonlinear <= POWER_TABLE.cold_nonlinear * 1.002))
ratio_k01 = float(np.interp(math.log(0.1), np.log(K_HALO), np.asarray(HALO_RESULTS[0.0][1]["nonlinear"]) / np.asarray(HALO_RESULTS[0.0][0]["nonlinear"])))
add_check("NLH15", "large-scale nonlinear recovery", abs(ratio_k01 - 1.0), 0.01, abs(ratio_k01 - 1.0) < 0.01)
linear_k10 = float(DARK_TRANSFER(10.0) ** 2)
nonlinear_k10 = float(np.interp(math.log(10.0), np.log(K_HALO), np.asarray(HALO_RESULTS[0.0][1]["nonlinear"]) / np.asarray(HALO_RESULTS[0.0][0]["nonlinear"])))
add_check("NLH16", "halo collapse regenerates power", nonlinear_k10 - linear_k10, 0.0, nonlinear_k10 > linear_k10)
add_check("NLH17", "collapsed fractions ordered", float((REIONIZATION_TABLE.refinement_collapsed_fraction - REIONIZATION_TABLE.cold_collapsed_fraction).max()), 0.0, np.all(REIONIZATION_TABLE.refinement_collapsed_fraction < REIONIZATION_TABLE.cold_collapsed_fraction))
penalty_74 = float(REIONIZATION_TABLE[np.isclose(REIONIZATION_TABLE.z, 7.4)]["required_efficiency_penalty"].iloc[0])
add_check("NLH18", "current benchmark requires roughly threefold ionizing efficiency", abs(penalty_74 - 3.0), 0.2, abs(penalty_74 - 3.0) < 0.2)
add_check("NLH19", "reionization penalty grows with production scale", efficiency_penalty(1.2) - efficiency_penalty(0.8), 0.0, efficiency_penalty(1.2) > efficiency_penalty(0.8))
add_check("NLH20", "nonlinear lensing ratios are ordered", float(LENSING_TABLE.nonlinear_halo_model_ratio.max() - 1.0), 1.0e-8, np.all(LENSING_TABLE.nonlinear_halo_model_ratio <= 1.0 + 1.0e-8))
linear_z05_5000 = float(LENSING_TABLE[(LENSING_TABLE.source_z == 0.5) & (LENSING_TABLE.ell == 5000.0)]["linear_ratio_from_parent"].iloc[0])
nonlinear_z05_5000 = float(LENSING_TABLE[(LENSING_TABLE.source_z == 0.5) & (LENSING_TABLE.ell == 5000.0)]["nonlinear_halo_model_ratio"].iloc[0])
add_check("NLH21", "nonlinear structure weakens the linear lensing suppression", nonlinear_z05_5000 - linear_z05_5000, 0.0, nonlinear_z05_5000 > linear_z05_5000)
add_check("NLH22", "mass-grid convergence", MASS_GRID_DISCREPANCY, 0.03, MASS_GRID_DISCREPANCY < 0.03)
add_check("NLH23", "lensing-grid convergence", LENSING_GRID_DISCREPANCY, 0.02, LENSING_GRID_DISCREPANCY < 0.02)
add_check("NLH24", "all collapse thresholds finite", float(np.max(COLLAPSE_DC)), 1.71, np.all(np.isfinite(COLLAPSE_DC)) and np.all((COLLAPSE_DC > 1.65) & (COLLAPSE_DC < 1.71)))

CHECK_TABLE = pd.DataFrame(CHECKS)
CHECK_TABLE.to_csv(DATA / "nonlinear_structure_checks.csv", index=False)

# ---------------------------------------------------------------------------
# Figures.
# ---------------------------------------------------------------------------
plt.figure(figsize=(7.2, 4.8))
plt.loglog(MASS_GRID, SIGMA_COLD_0, label="cold control")
plt.loglog(MASS_GRID, SIGMA_DARK_0, label="refinement")
plt.axvline(M_HALF_POWER, linestyle="--", linewidth=1.0, label=r"$M_{1/2}$")
plt.xlabel(r"Halo mass $M\ [M_\odot]$")
plt.ylabel(r"Linear variance $\sigma(M,z=0)$")
plt.title("Linear variance and the refinement half-mode mass")
plt.legend()
plt.tight_layout()
plt.savefig(FIG / "variance_half_mode.png", dpi=220)
plt.close()

plt.figure(figsize=(7.2, 4.8))
for z in [0.0, 1.0, 3.0, 6.0, 8.0]:
    subset = MASS_TABLE[MASS_TABLE.z == z]
    plt.semilogx(subset.mass_msun, subset.refinement_to_cold_ratio, marker="o", label=fr"$z={z:g}$")
plt.axvline(M_HALF_POWER, linestyle="--", linewidth=1.0)
plt.xlabel(r"Halo mass $M\ [M_\odot]$")
plt.ylabel("Halo mass-function ratio")
plt.ylim(0.0, 1.05)
plt.title("Low-mass halo suppression strengthens at high redshift")
plt.legend()
plt.tight_layout()
plt.savefig(FIG / "halo_mass_function_ratios.png", dpi=220)
plt.close()

plt.figure(figsize=(7.2, 4.8))
for z in [0.0, 1.0, 2.0]:
    subset = POWER_TABLE[POWER_TABLE.z == z]
    plt.semilogx(subset.k_per_Mpc, subset.nonlinear_ratio, label=fr"nonlinear $z={z:g}$")
plt.semilogx(K_HALO, DARK_TRANSFER(K_HALO) ** 2, linestyle="--", label="linear power ratio")
plt.xlabel(r"Wavenumber $k\ [{\rm Mpc}^{-1}]$")
plt.ylabel("Refinement / cold power")
plt.ylim(0.0, 1.05)
plt.title("Compensated halo model regenerates nonlinear small-scale power")
plt.legend()
plt.tight_layout()
plt.savefig(FIG / "nonlinear_power_ratios.png", dpi=220)
plt.close()

plt.figure(figsize=(7.2, 4.8))
plt.plot(REIONIZATION_TABLE.z, REIONIZATION_TABLE.required_efficiency_penalty, marker="o")
plt.axhline(3.0, linestyle="--", linewidth=1.0, label="threefold efficiency")
plt.xlabel("Redshift")
plt.ylabel(r"Required efficiency ratio $\zeta_D/\zeta_{\rm cold}$")
plt.title("Atomic-cooling halo deficit and reionization efficiency")
plt.legend()
plt.tight_layout()
plt.savefig(FIG / "reionization_efficiency_penalty.png", dpi=220)
plt.close()

plt.figure(figsize=(7.2, 4.8))
z05 = LENSING_TABLE[LENSING_TABLE.source_z == 0.5]
plt.semilogx(z05.ell, z05.linear_ratio_from_parent, marker="o", label="linear projection")
plt.semilogx(z05.ell, z05.nonlinear_halo_model_ratio, marker="o", label="nonlinear halo model")
plt.xlabel(r"Multipole $\ell$")
plt.ylabel("Refinement / cold lensing power")
plt.ylim(0.65, 1.01)
plt.title(r"Nonlinear structure weakens the high-$\ell$ lensing deficit")
plt.legend()
plt.tight_layout()
plt.savefig(FIG / "linear_vs_nonlinear_lensing.png", dpi=220)
plt.close()

# ---------------------------------------------------------------------------
# Summary JSON.
# ---------------------------------------------------------------------------
summary = {
    "parameters": asdict(P),
    "rho_m_msun_mpc3": RHO_M,
    "sigma8_check": SIGMA8_CHECK,
    "collapse_thresholds": [
        {"z": float(z), "delta_c": float(dc)} for z, dc in zip(COLLAPSE_Z, COLLAPSE_DC)
    ],
    "half_mode": {
        "k_power_per_Mpc": K_HALF_POWER,
        "mass_power_msun": M_HALF_POWER,
        "k_amplitude_per_Mpc": K_HALF_AMPLITUDE,
        "mass_amplitude_msun": M_HALF_AMPLITUDE,
    },
    "selected_results": {
        "mass_function_ratio_M1e8_z0": ratio_1e8_z0,
        "mass_function_ratio_M1e8_z8": ratio_1e8_z8,
        "mass_function_ratio_M1e13_z0": ratio_1e13_z0,
        "concentration_ratio_M1e8_z0": conc_low,
        "concentration_ratio_M1e13_z0": conc_high,
        "nonlinear_power_ratio_k10_z0": nonlinear_k10,
        "linear_power_ratio_k10": linear_k10,
        "reionization_efficiency_penalty_z7p4": penalty_74,
        "nonlinear_lensing_ratio_z0p5_ell5000": nonlinear_z05_5000,
        "linear_lensing_ratio_z0p5_ell5000": linear_z05_5000,
        "one_halo_low_k_slope": ONE_HALO_SLOPE,
        "mass_grid_discrepancy": MASS_GRID_DISCREPANCY,
        "lensing_grid_discrepancy": LENSING_GRID_DISCREPANCY,
    },
    "verification": {
        "pass_count": int((CHECK_TABLE.status == "PASS").sum()),
        "fail_count": int((CHECK_TABLE.status == "FAIL").sum()),
    },
}
with open(DATA / "Nonlinear_Structure_Halo_Verification.json", "w", encoding="utf-8") as handle:
    json.dump(summary, handle, indent=2)

# Manifest hashes for scientific outputs.
def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()

manifest_rows = []
for path in sorted(list(DATA.glob("*")) + list(FIG.glob("*"))):
    if path.is_file():
        manifest_rows.append({"path": str(path.relative_to(ROOT)), "sha256": sha256(path), "bytes": path.stat().st_size})
pd.DataFrame(manifest_rows).to_csv(DATA / "scientific_output_manifest.csv", index=False)

print(json.dumps(summary, indent=2))
if summary["verification"]["fail_count"]:
    raise SystemExit(1)
