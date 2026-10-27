from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import json
import math
import time
from typing import Callable, Iterable

import numpy as np
import pandas as pd
from numpy.polynomial.legendre import leggauss
from scipy.integrate import solve_ivp
from scipy.interpolate import PchipInterpolator
from scipy.ndimage import maximum_filter
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
FIG = ROOT / "figures"
PARENT = ROOT / "parent"
LOGS = ROOT / "logs"
for directory in (DATA, FIG, PARENT, LOGS):
    directory.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class Parameters:
    h: float = 0.7
    omega_b0: float = 0.049
    omega_d0: float = 0.261
    omega_r0: float = 9.0e-5
    n_s: float = 0.965
    sigma8: float = 0.81
    box_mpc: float = 100.0 / 7.0
    a_initial: float = 0.02
    main_grid: int = 64
    control_grid: int = 48
    main_steps: int = 80
    control_steps: int = 64
    time_control_steps: int = 96
    seed: int = 20260813
    deconvolution_k_fraction: float = 0.65
    initial_k_fraction: float = 0.70


P = Parameters()
OMEGA_M = P.omega_b0 + P.omega_d0
OMEGA_V = 1.0 - OMEGA_M - P.omega_r0
RHO_CRIT = 2.77536627e11 * P.h**2  # Msun / Mpc^3
RHO_M = OMEGA_M * RHO_CRIT
SNAPSHOTS = np.array(
    [
        0.02,
        0.04,
        0.05,
        0.07,
        0.10,
        0.14,
        0.20,
        0.25,
        1.0 / 3.0,
        0.45,
        0.50,
        2.0 / 3.0,
        0.80,
        1.00,
    ],
    dtype=float,
)
DENSITY_THRESHOLDS = np.array([5.0, 10.0, 20.0, 50.0, 100.0])


def expansion(a: np.ndarray | float) -> np.ndarray:
    aa = np.asarray(a, dtype=float)
    return np.sqrt(P.omega_r0 * aa**-4 + OMEGA_M * aa**-3 + OMEGA_V)


def build_growth() -> tuple[Callable[[np.ndarray | float], np.ndarray], Callable[[np.ndarray | float], np.ndarray]]:
    n_initial = math.log(1.0e-4)

    def rhs(n: float, y: np.ndarray) -> list[float]:
        a = math.exp(n)
        e2 = P.omega_r0 * a**-4 + OMEGA_M * a**-3 + OMEGA_V
        dln_h = -0.5 * (4.0 * P.omega_r0 * a**-4 + 3.0 * OMEGA_M * a**-3) / e2
        omega_m = OMEGA_M * a**-3 / e2
        return [float(y[1]), -(2.0 + dln_h) * float(y[1]) + 1.5 * omega_m * float(y[0])]

    solution = solve_ivp(
        rhs,
        (n_initial, 0.0),
        [1.0e-4, 1.0e-4],
        rtol=1.0e-11,
        atol=1.0e-13,
        max_step=0.02,
        dense_output=True,
    )
    if not solution.success:
        raise RuntimeError(solution.message)
    normalization = float(solution.sol(0.0)[0])

    def growth(a: np.ndarray | float) -> np.ndarray:
        aa = np.asarray(a, dtype=float)
        return np.asarray(solution.sol(np.log(aa))[0] / normalization, dtype=float)

    def growth_log_derivative(a: np.ndarray | float) -> np.ndarray:
        aa = np.asarray(a, dtype=float)
        return np.asarray(solution.sol(np.log(aa))[1] / normalization, dtype=float)

    return growth, growth_log_derivative


GROWTH, GROWTH_N = build_growth()


def bbks_transfer(k: np.ndarray | float) -> np.ndarray:
    kk = np.asarray(k, dtype=float)
    q = kk / (OMEGA_M * P.h**2)
    out = np.ones_like(q)
    mask = q > 0.0
    qm = q[mask]
    out[mask] = (
        np.log1p(2.34 * qm)
        / (2.34 * qm)
        * (1.0 + 3.89 * qm + (16.1 * qm) ** 2 + (5.46 * qm) ** 3 + (6.71 * qm) ** 4) ** (-0.25)
    )
    return out


def top_hat_window(x: np.ndarray | float) -> np.ndarray:
    xx = np.asarray(x, dtype=float)
    out = np.empty_like(xx)
    small = np.abs(xx) < 1.0e-3
    out[small] = 1.0 - xx[small] ** 2 / 10.0
    xs = xx[~small]
    out[~small] = 3.0 * (np.sin(xs) - xs * np.cos(xs)) / xs**3
    return out


K_NORMALIZATION = np.geomspace(1.0e-5, 300.0, 8000)
SHAPE = K_NORMALIZATION**P.n_s * bbks_transfer(K_NORMALIZATION) ** 2
R8 = 8.0 / P.h
VARIANCE_SHAPE = np.trapezoid(
    K_NORMALIZATION**3 * SHAPE * top_hat_window(K_NORMALIZATION * R8) ** 2 / (2.0 * math.pi**2),
    np.log(K_NORMALIZATION),
)
POWER_AMPLITUDE = P.sigma8**2 / VARIANCE_SHAPE


def cold_linear_power(k: np.ndarray | float) -> np.ndarray:
    kk = np.asarray(k, dtype=float)
    return POWER_AMPLITUDE * kk**P.n_s * bbks_transfer(kk) ** 2


class RefinementTransfer:
    def __init__(self, path: Path) -> None:
        table = pd.read_csv(path)
        self.k = table["k_per_Mpc_for_H0_70"].to_numpy(float)
        self.t = np.clip(table["collisionless_transfer_amplitude_z0"].to_numpy(float), 1.0e-10, 1.0)
        self.interpolator = PchipInterpolator(np.log(self.k), np.log(self.t), extrapolate=True)
        self.tail_slope = float(np.polyfit(np.log(self.k[-6:]), np.log(self.t[-6:]), 1)[0])

    def __call__(self, k: np.ndarray | float) -> np.ndarray:
        kk = np.asarray(k, dtype=float)
        out = np.ones_like(kk)
        inside = (kk >= self.k[0]) & (kk <= self.k[-1])
        out[inside] = np.exp(self.interpolator(np.log(kk[inside])))
        high = kk > self.k[-1]
        out[high] = self.t[-1] * (kk[high] / self.k[-1]) ** self.tail_slope
        return np.clip(out, 1.0e-10, 1.0)


REFINEMENT_TRANSFER = RefinementTransfer(PARENT / "collisionless_dark_transfer_curve.csv")

_GL_X, _GL_W = leggauss(8)


def gauss_legendre_integral(function: Callable[[np.ndarray], np.ndarray], a: float, b: float) -> float:
    points = 0.5 * (b - a) * _GL_X + 0.5 * (a + b)
    return float(0.5 * (b - a) * np.sum(_GL_W * function(points)))


def drift_factor(a: float, b: float) -> float:
    return gauss_legendre_integral(lambda x: 1.0 / (x**3 * expansion(x)), a, b)


def kick_factor(a: float, b: float) -> float:
    return 1.5 * OMEGA_M * gauss_legendre_integral(lambda x: 1.0 / (x**2 * expansion(x)), a, b)


def mesh_wavevectors(grid: int, box: float) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    dx = box / grid
    kx = 2.0 * math.pi * np.fft.fftfreq(grid, d=dx)[:, None, None]
    ky = 2.0 * math.pi * np.fft.fftfreq(grid, d=dx)[None, :, None]
    kz = 2.0 * math.pi * np.fft.rfftfreq(grid, d=dx)[None, None, :]
    kmag = np.sqrt(kx * kx + ky * ky + kz * kz)
    return kx, ky, kz, kmag


def cic_indices(position: np.ndarray, grid: int, box: float) -> tuple[np.ndarray, np.ndarray]:
    dx = box / grid
    coordinate = position / dx
    base = np.floor(coordinate).astype(np.int64)
    fraction = coordinate - base
    return base % grid, fraction


def cic_deposit(position: np.ndarray, grid: int, box: float) -> np.ndarray:
    base, fraction = cic_indices(position, grid, box)
    cells = grid**3
    density = np.zeros(cells, dtype=float)
    for ox in (0, 1):
        wx = 1.0 - fraction[:, 0] if ox == 0 else fraction[:, 0]
        ix = (base[:, 0] + ox) % grid
        for oy in (0, 1):
            wy = 1.0 - fraction[:, 1] if oy == 0 else fraction[:, 1]
            iy = (base[:, 1] + oy) % grid
            for oz in (0, 1):
                wz = 1.0 - fraction[:, 2] if oz == 0 else fraction[:, 2]
                iz = (base[:, 2] + oz) % grid
                index = (ix * grid + iy) * grid + iz
                density += np.bincount(index, weights=wx * wy * wz, minlength=cells)
    mean_count = len(position) / cells
    return density.reshape(grid, grid, grid) / mean_count - 1.0


def cic_interpolate(position: np.ndarray, fields: Iterable[np.ndarray], grid: int, box: float) -> np.ndarray:
    base, fraction = cic_indices(position, grid, box)
    flat_fields = [field.ravel() for field in fields]
    result = np.zeros((len(position), len(flat_fields)), dtype=float)
    for ox in (0, 1):
        wx = 1.0 - fraction[:, 0] if ox == 0 else fraction[:, 0]
        ix = (base[:, 0] + ox) % grid
        for oy in (0, 1):
            wy = 1.0 - fraction[:, 1] if oy == 0 else fraction[:, 1]
            iy = (base[:, 1] + oy) % grid
            for oz in (0, 1):
                wz = 1.0 - fraction[:, 2] if oz == 0 else fraction[:, 2]
                iz = (base[:, 2] + oz) % grid
                index = (ix * grid + iy) * grid + iz
                weight = wx * wy * wz
                for component, field in enumerate(flat_fields):
                    result[:, component] += weight * field[index]
    return result


def particle_force(position: np.ndarray, grid: int, box: float) -> tuple[np.ndarray, np.ndarray, float]:
    delta = cic_deposit(position, grid, box)
    spectrum = np.fft.rfftn(delta)
    kx, ky, kz, kmag = mesh_wavevectors(grid, box)
    inverse = np.zeros_like(kmag)
    nonzero = kmag > 0.0
    inverse[nonzero] = 1.0 / kmag[nonzero] ** 2
    shape = (grid, grid, grid)
    force_x = np.fft.irfftn(1j * kx * inverse * spectrum, s=shape, axes=(0, 1, 2)).real
    force_y = np.fft.irfftn(1j * ky * inverse * spectrum, s=shape, axes=(0, 1, 2)).real
    force_z = np.fft.irfftn(1j * kz * inverse * spectrum, s=shape, axes=(0, 1, 2)).real
    force = cic_interpolate(position, (force_x, force_y, force_z), grid, box)
    net_force = float(np.linalg.norm(np.sum(force, axis=0)) / max(len(force), 1))
    return force, delta, net_force


def generate_initial_state(
    grid: int,
    box: float,
    a_initial: float,
    seed: int,
    refinement: bool,
    amplitude_scale: float = 1.0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    white_noise = rng.normal(size=(grid, grid, grid))
    white_spectrum = np.fft.rfftn(white_noise)
    kx, ky, kz, kmag = mesh_wavevectors(grid, box)
    volume = box**3
    amplitude = np.sqrt(grid**3 * cold_linear_power(kmag) / volume)
    amplitude[0, 0, 0] = 0.0
    nyquist = math.pi * grid / box
    amplitude[kmag > P.initial_k_fraction * nyquist] = 0.0
    if refinement:
        amplitude *= REFINEMENT_TRANSFER(kmag)
    delta_spectrum = amplitude_scale * white_spectrum * amplitude
    inverse = np.zeros_like(kmag)
    nonzero = kmag > 0.0
    inverse[nonzero] = 1.0 / kmag[nonzero] ** 2
    shape = (grid, grid, grid)
    displacement = np.stack(
        [
            np.fft.irfftn(1j * kx * inverse * delta_spectrum, s=shape, axes=(0, 1, 2)).real,
            np.fft.irfftn(1j * ky * inverse * delta_spectrum, s=shape, axes=(0, 1, 2)).real,
            np.fft.irfftn(1j * kz * inverse * delta_spectrum, s=shape, axes=(0, 1, 2)).real,
        ],
        axis=-1,
    ).reshape(-1, 3)
    dx = box / grid
    lagrangian = (np.indices((grid, grid, grid)).transpose(1, 2, 3, 0) + 0.5) * dx
    lagrangian = lagrangian.reshape(-1, 3)
    position = (lagrangian + float(GROWTH(a_initial)) * displacement) % box
    momentum = (a_initial**2 * float(expansion(a_initial)) * float(GROWTH_N(a_initial))) * displacement
    return position, momentum, delta_spectrum


@dataclass
class SimulationOutput:
    grid: int
    steps: int
    seed: int
    refinement: bool
    densities: dict[float, np.ndarray]
    final_position: np.ndarray
    final_momentum: np.ndarray
    maximum_net_force: float
    initial_delta_spectrum: np.ndarray
    wall_seconds: float


def run_simulation(
    grid: int,
    steps: int,
    seed: int,
    refinement: bool,
    snapshots: np.ndarray = SNAPSHOTS,
    amplitude_scale: float = 1.0,
) -> SimulationOutput:
    start = time.perf_counter()
    position, momentum, initial_delta_spectrum = generate_initial_state(
        grid,
        P.box_mpc,
        P.a_initial,
        seed,
        refinement,
        amplitude_scale=amplitude_scale,
    )
    scale_edges = np.geomspace(P.a_initial, 1.0, steps + 1)
    force, density, net_force = particle_force(position, grid, P.box_mpc)
    maximum_net_force = net_force
    output: dict[float, np.ndarray] = {}
    target_index = 0
    while target_index < len(snapshots) and snapshots[target_index] <= P.a_initial + 1.0e-14:
        output[float(snapshots[target_index])] = density.copy()
        target_index += 1
    for a_left, a_right in zip(scale_edges[:-1], scale_edges[1:]):
        a_mid = math.sqrt(a_left * a_right)
        momentum += kick_factor(a_left, a_mid) * force
        position = (position + drift_factor(a_left, a_right) * momentum) % P.box_mpc
        force, density, net_force = particle_force(position, grid, P.box_mpc)
        maximum_net_force = max(maximum_net_force, net_force)
        momentum += kick_factor(a_mid, a_right) * force
        while target_index < len(snapshots) and snapshots[target_index] <= a_right + 1.0e-14:
            output[float(snapshots[target_index])] = density.copy()
            target_index += 1
    return SimulationOutput(
        grid=grid,
        steps=steps,
        seed=seed,
        refinement=refinement,
        densities=output,
        final_position=position,
        final_momentum=momentum,
        maximum_net_force=maximum_net_force,
        initial_delta_spectrum=initial_delta_spectrum,
        wall_seconds=time.perf_counter() - start,
    )


def rfft_mode_weights(grid: int) -> np.ndarray:
    weights = np.ones(grid // 2 + 1, dtype=float)
    if grid % 2 == 0:
        if len(weights) > 2:
            weights[1:-1] = 2.0
    elif len(weights) > 1:
        weights[1:] = 2.0
    return weights[None, None, :]


def cic_window(grid: int, box: float) -> tuple[np.ndarray, np.ndarray]:
    dx = box / grid
    kx, ky, kz, kmag = mesh_wavevectors(grid, box)
    window = (
        np.sinc(kx * dx / (2.0 * math.pi)) ** 2
        * np.sinc(ky * dx / (2.0 * math.pi)) ** 2
        * np.sinc(kz * dx / (2.0 * math.pi)) ** 2
    )
    return window, kmag


def binned_power_and_cross(
    cold: np.ndarray,
    refinement: np.ndarray,
    grid: int,
    box: float,
    bins: int = 24,
) -> pd.DataFrame:
    cold_spectrum = np.fft.rfftn(cold)
    refinement_spectrum = np.fft.rfftn(refinement)
    window, kmag = cic_window(grid, box)
    nyquist = math.pi * grid / box
    mask = (kmag > 0.0) & (kmag < P.deconvolution_k_fraction * nyquist) & (window > 0.2)
    corrected_cold = cold_spectrum / np.where(window > 0.2, window, 1.0)
    corrected_refinement = refinement_spectrum / np.where(window > 0.2, window, 1.0)
    prefactor = box**3 / grid**6
    cold_power = prefactor * np.abs(corrected_cold) ** 2
    refinement_power = prefactor * np.abs(corrected_refinement) ** 2
    cross_power = prefactor * np.real(corrected_cold * np.conj(corrected_refinement))
    weights = np.broadcast_to(rfft_mode_weights(grid), kmag.shape)
    edges = np.geomspace(2.0 * math.pi / box, P.deconvolution_k_fraction * nyquist, bins + 1)
    assignment = np.digitize(kmag[mask], edges) - 1
    records: list[dict[str, float]] = []
    for index in range(bins):
        selected = assignment == index
        if not np.any(selected):
            continue
        w = weights[mask][selected]
        k_selected = kmag[mask][selected]
        pc = cold_power[mask][selected]
        pdark = refinement_power[mask][selected]
        pcross = cross_power[mask][selected]
        weight_sum = float(np.sum(w))
        mean_pc = float(np.sum(w * pc) / weight_sum)
        mean_pdark = float(np.sum(w * pdark) / weight_sum)
        mean_cross = float(np.sum(w * pcross) / weight_sum)
        records.append(
            {
                "k_per_Mpc": float(np.exp(np.sum(w * np.log(k_selected)) / weight_sum)),
                "cold_power_Mpc3": mean_pc,
                "refinement_power_Mpc3": mean_pdark,
                "power_ratio": mean_pdark / mean_pc,
                "cross_correlation": mean_cross / math.sqrt(mean_pc * mean_pdark),
                "mode_weight": weight_sum,
            }
        )
    return pd.DataFrame.from_records(records)


def density_statistics(density: np.ndarray, scale_factor: float, branch: str) -> list[dict[str, float | str]]:
    rho = 1.0 + density
    standard_deviation = float(np.std(rho))
    centered = rho - float(np.mean(rho))
    skewness = float(np.mean(centered**3) / standard_deviation**3) if standard_deviation > 0.0 else 0.0
    local_maximum = rho == maximum_filter(rho, size=3, mode="wrap")
    records: list[dict[str, float | str]] = []
    for threshold in DENSITY_THRESHOLDS:
        selected = rho > threshold
        records.append(
            {
                "scale_factor": scale_factor,
                "redshift": 1.0 / scale_factor - 1.0,
                "branch": branch,
                "density_threshold": threshold,
                "volume_fraction": float(np.mean(selected)),
                "mass_fraction": float(np.sum(rho[selected]) / np.sum(rho)),
                "peak_count": float(np.sum(local_maximum & selected)),
                "density_standard_deviation": standard_deviation,
                "density_skewness": skewness,
                "maximum_density": float(np.max(rho)),
            }
        )
    return records


def interpolate_at(table: pd.DataFrame, x: float, column: str) -> float:
    return float(np.interp(x, table["k_per_Mpc"].to_numpy(float), table[column].to_numpy(float)))


def first_crossing(scale: np.ndarray, value: np.ndarray, target: float) -> float | None:
    valid = np.where(value >= target)[0]
    if len(valid) == 0:
        return None
    index = int(valid[0])
    if index == 0:
        return float(scale[0])
    x0, x1 = float(scale[index - 1]), float(scale[index])
    y0, y1 = float(value[index - 1]), float(value[index])
    if y1 == y0:
        return x1
    return x0 + (target - y0) * (x1 - x0) / (y1 - y0)


def linear_growth_control() -> dict[str, float]:
    grid = 32
    box = P.box_mpc
    a_initial = P.a_initial
    a_final = 0.20
    amplitude = 1.0e-3
    dx = box / grid
    lagrangian = (np.indices((grid, grid, grid)).transpose(1, 2, 3, 0) + 0.5) * dx
    q = lagrangian.reshape(-1, 3)
    wave_number = 2.0 * math.pi / box
    displacement = np.zeros_like(q)
    displacement[:, 0] = -(amplitude / wave_number) * np.sin(wave_number * q[:, 0])
    position = (q + float(GROWTH(a_initial)) * displacement) % box
    momentum = (a_initial**2 * float(expansion(a_initial)) * float(GROWTH_N(a_initial))) * displacement

    def mode_amplitude(delta: np.ndarray) -> float:
        spectrum = np.fft.rfftn(delta)
        return float(2.0 * abs(spectrum[1, 0, 0]) / grid**3)

    _, initial_density, _ = particle_force(position, grid, box)
    initial_mode = mode_amplitude(initial_density)
    edges = np.geomspace(a_initial, a_final, 72 + 1)
    force, _, _ = particle_force(position, grid, box)
    for a_left, a_right in zip(edges[:-1], edges[1:]):
        a_mid = math.sqrt(a_left * a_right)
        momentum += kick_factor(a_left, a_mid) * force
        position = (position + drift_factor(a_left, a_right) * momentum) % box
        force, final_density, _ = particle_force(position, grid, box)
        momentum += kick_factor(a_mid, a_right) * force
    final_mode = mode_amplitude(final_density)
    measured_growth = final_mode / initial_mode
    expected_growth = float(GROWTH(a_final) / GROWTH(a_initial))
    return {
        "linear_measured_growth": measured_growth,
        "linear_expected_growth": expected_growth,
        "linear_relative_growth_error": abs(measured_growth / expected_growth - 1.0),
    }


def plot_outputs(
    power_history: pd.DataFrame,
    density_table: pd.DataFrame,
    final_cold: np.ndarray,
    final_refinement: np.ndarray,
    halo_comparison: pd.DataFrame,
) -> None:
    plt.figure(figsize=(8.2, 5.4))
    selected_scales = [0.05, 0.10, 0.25, 0.50, 1.00]
    for a in selected_scales:
        subset = power_history[np.isclose(power_history["scale_factor"], a)]
        plt.plot(subset["k_per_Mpc"], subset["power_ratio"], label=f"a={a:g}")
    k_plot = np.geomspace(power_history["k_per_Mpc"].min(), power_history["k_per_Mpc"].max(), 300)
    plt.plot(k_plot, REFINEMENT_TRANSFER(k_plot) ** 2, linestyle="--", label="input linear ratio")
    plt.plot(halo_comparison["k_per_Mpc"], halo_comparison["halo_model_nonlinear_ratio"], linestyle=":", label="halo-model z=0")
    plt.xscale("log")
    plt.ylim(0.35, 1.03)
    plt.xlabel(r"$k\ [{\rm Mpc}^{-1}]$")
    plt.ylabel("refinement / cold power")
    plt.title("Nonlinear regeneration of suppressed refinement power")
    plt.legend(ncol=2, fontsize=8)
    plt.tight_layout()
    plt.savefig(FIG / "01_power_regeneration.png", dpi=180)
    plt.close()

    plt.figure(figsize=(8.2, 5.4))
    for threshold in [10.0, 20.0, 50.0, 100.0]:
        cold = density_table[(density_table.branch == "cold") & (density_table.density_threshold == threshold)]
        refinement = density_table[(density_table.branch == "refinement") & (density_table.density_threshold == threshold)]
        cold_mass = cold["mass_fraction"].to_numpy(float)
        refinement_mass = refinement["mass_fraction"].to_numpy(float)
        ratio = np.full_like(cold_mass, np.nan)
        valid = cold_mass > 1.0e-4
        ratio[valid] = refinement_mass[valid] / cold_mass[valid]
        plt.plot(cold["scale_factor"], ratio, label=rf"$\rho/\bar\rho>{threshold:g}$")
    plt.axhline(1.0, linewidth=0.8, linestyle="--")
    plt.xscale("log")
    plt.ylim(0.55, 1.03)
    plt.xlabel("scale factor")
    plt.ylabel("refinement / cold collapsed mass fraction")
    plt.title("Delayed high-density collapse survives power regeneration")
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(FIG / "02_collapsed_mass_fraction.png", dpi=180)
    plt.close()

    plt.figure(figsize=(8.2, 5.4))
    for a in [0.05, 0.10, 0.25, 0.50, 1.00]:
        subset = power_history[np.isclose(power_history["scale_factor"], a)]
        plt.plot(subset["k_per_Mpc"], subset["cross_correlation"], label=f"a={a:g}")
    plt.xscale("log")
    plt.ylim(0.97, 1.0005)
    plt.xlabel(r"$k\ [{\rm Mpc}^{-1}]$")
    plt.ylabel("paired cross-correlation")
    plt.title("The paired cosmic web remains highly phase-correlated")
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(FIG / "03_cross_correlation.png", dpi=180)
    plt.close()

    center = final_cold.shape[2] // 2
    slab = np.arange(center - 2, center + 2) % final_cold.shape[2]
    cold_slice = np.log10(np.maximum(np.mean(1.0 + final_cold[:, :, slab], axis=2), 1.0e-3))
    refinement_slice = np.log10(np.maximum(np.mean(1.0 + final_refinement[:, :, slab], axis=2), 1.0e-3))
    common_min = min(float(cold_slice.min()), float(refinement_slice.min()))
    common_max = max(float(cold_slice.max()), float(refinement_slice.max()))
    figure, axes = plt.subplots(1, 3, figsize=(12.0, 4.0))
    first = axes[0].imshow(cold_slice.T, origin="lower", vmin=common_min, vmax=common_max)
    axes[0].set_title("cold control")
    axes[1].imshow(refinement_slice.T, origin="lower", vmin=common_min, vmax=common_max)
    axes[1].set_title("refinement")
    difference = axes[2].imshow((refinement_slice - cold_slice).T, origin="lower")
    axes[2].set_title("log-density difference")
    for axis in axes:
        axis.set_xticks([])
        axis.set_yticks([])
    figure.colorbar(first, ax=axes[:2], fraction=0.025, pad=0.02, label=r"$\log_{10}(\rho/\bar\rho)$")
    figure.colorbar(difference, ax=axes[2], fraction=0.05, pad=0.04)
    figure.suptitle("Paired nonlinear density fields at a=1")
    figure.subplots_adjust(left=0.02, right=0.95, bottom=0.04, top=0.88, wspace=0.08)
    figure.savefig(FIG / "04_density_slices.png", dpi=180)
    plt.close(figure)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    start = time.perf_counter()
    main_cold = run_simulation(P.main_grid, P.main_steps, P.seed, False)
    main_refinement = run_simulation(P.main_grid, P.main_steps, P.seed, True)

    power_records: list[pd.DataFrame] = []
    density_records: list[dict[str, float | str]] = []
    for a in SNAPSHOTS:
        cold_density = main_cold.densities[float(a)]
        refinement_density = main_refinement.densities[float(a)]
        power = binned_power_and_cross(cold_density, refinement_density, P.main_grid, P.box_mpc)
        power.insert(0, "redshift", 1.0 / a - 1.0)
        power.insert(0, "scale_factor", a)
        power["linear_input_ratio"] = REFINEMENT_TRANSFER(power["k_per_Mpc"].to_numpy(float)) ** 2
        power_records.append(power)
        density_records.extend(density_statistics(cold_density, float(a), "cold"))
        density_records.extend(density_statistics(refinement_density, float(a), "refinement"))
    power_history = pd.concat(power_records, ignore_index=True)
    density_table = pd.DataFrame.from_records(density_records)

    # Grid and time-step controls.
    control_cold = run_simulation(P.control_grid, P.control_steps, P.seed, False, snapshots=np.array([1.0]))
    control_refinement = run_simulation(P.control_grid, P.control_steps, P.seed, True, snapshots=np.array([1.0]))
    time_cold = run_simulation(P.control_grid, P.time_control_steps, P.seed, False, snapshots=np.array([1.0]))
    time_refinement = run_simulation(P.control_grid, P.time_control_steps, P.seed, True, snapshots=np.array([1.0]))
    control_power = binned_power_and_cross(
        control_cold.densities[1.0], control_refinement.densities[1.0], P.control_grid, P.box_mpc
    )
    time_power = binned_power_and_cross(
        time_cold.densities[1.0], time_refinement.densities[1.0], P.control_grid, P.box_mpc
    )
    main_final_power = power_history[np.isclose(power_history.scale_factor, 1.0)].copy()

    selected_k = np.array([3.0, 4.0, 5.0, 6.0, 7.0])
    convergence_records: list[dict[str, float]] = []
    for k in selected_k:
        main_ratio = interpolate_at(main_final_power, k, "power_ratio")
        grid_ratio = interpolate_at(control_power, k, "power_ratio")
        time_ratio = interpolate_at(time_power, k, "power_ratio")
        convergence_records.append(
            {
                "k_per_Mpc": k,
                "main_ratio": main_ratio,
                "grid_control_ratio": grid_ratio,
                "time_control_ratio": time_ratio,
                "grid_relative_difference": abs(grid_ratio / main_ratio - 1.0),
                "time_relative_difference": abs(time_ratio / grid_ratio - 1.0),
            }
        )
    convergence = pd.DataFrame.from_records(convergence_records)

    # Independent paired-phase robustness controls on the smaller grid.
    phase_records: list[dict[str, float]] = []
    for seed in [P.seed + 101, P.seed + 202]:
        phase_cold = run_simulation(32, 48, seed, False, snapshots=np.array([1.0]))
        phase_refinement = run_simulation(32, 48, seed, True, snapshots=np.array([1.0]))
        phase_power = binned_power_and_cross(
            phase_cold.densities[1.0], phase_refinement.densities[1.0], 32, P.box_mpc
        )
        for k in [4.0, 6.0, 7.0]:
            phase_records.append(
                {
                    "seed": float(seed),
                    "k_per_Mpc": k,
                    "power_ratio": interpolate_at(phase_power, k, "power_ratio"),
                }
            )
    phase_table = pd.DataFrame.from_records(phase_records)

    linear_control = linear_growth_control()

    halo_table = pd.read_csv(PARENT / "nonlinear_power_ratios.csv")
    halo_z0 = halo_table[np.isclose(halo_table["z"], 0.0)].copy()
    halo_comparison = pd.DataFrame(
        {
            "k_per_Mpc": main_final_power["k_per_Mpc"].to_numpy(float),
            "particle_mesh_ratio": main_final_power["power_ratio"].to_numpy(float),
            "halo_model_nonlinear_ratio": np.interp(
                main_final_power["k_per_Mpc"].to_numpy(float),
                halo_z0["k_per_Mpc"].to_numpy(float),
                halo_z0["nonlinear_ratio"].to_numpy(float),
            ),
            "linear_input_ratio": main_final_power["linear_input_ratio"].to_numpy(float),
        }
    )
    halo_comparison["pm_minus_halo_model"] = (
        halo_comparison["particle_mesh_ratio"] - halo_comparison["halo_model_nonlinear_ratio"]
    )

    # Collapse-time diagnostics from mesh mass fractions.
    formation_records: list[dict[str, float | str | None]] = []
    for threshold, target in [(10.0, 0.25), (20.0, 0.10), (50.0, 0.10), (100.0, 0.05)]:
        cold = density_table[(density_table.branch == "cold") & (density_table.density_threshold == threshold)]
        refinement = density_table[
            (density_table.branch == "refinement") & (density_table.density_threshold == threshold)
        ]
        a_cold = first_crossing(cold["scale_factor"].to_numpy(float), cold["mass_fraction"].to_numpy(float), target)
        a_refinement = first_crossing(
            refinement["scale_factor"].to_numpy(float), refinement["mass_fraction"].to_numpy(float), target
        )
        formation_records.append(
            {
                "density_threshold": threshold,
                "target_mass_fraction": target,
                "cold_crossing_scale_factor": a_cold,
                "refinement_crossing_scale_factor": a_refinement,
                "relative_scale_factor_delay": None
                if a_cold is None or a_refinement is None
                else a_refinement / a_cold - 1.0,
            }
        )
    formation = pd.DataFrame.from_records(formation_records)

    # Selected physical summary values.
    summary_k = [4.0, 6.0, 7.35, 8.0, 9.0]
    selected_power: list[dict[str, float]] = []
    for k in summary_k:
        row: dict[str, float] = {"k_per_Mpc": k, "linear_input_ratio": float(REFINEMENT_TRANSFER(k) ** 2)}
        for a in [0.05, 0.10, 0.25, 0.50, 1.00]:
            table = power_history[np.isclose(power_history.scale_factor, a)]
            row[f"power_ratio_a_{a:g}"] = interpolate_at(table, k, "power_ratio")
            row[f"cross_correlation_a_{a:g}"] = interpolate_at(table, k, "cross_correlation")
        selected_power.append(row)
    selected_power_table = pd.DataFrame.from_records(selected_power)

    # Save machine-readable data.
    power_history.to_csv(DATA / "paired_pm_power_history.csv", index=False)
    density_table.to_csv(DATA / "paired_pm_density_statistics.csv", index=False)
    convergence.to_csv(DATA / "paired_pm_convergence.csv", index=False)
    phase_table.to_csv(DATA / "paired_pm_phase_robustness.csv", index=False)
    halo_comparison.to_csv(DATA / "paired_pm_halo_model_comparison.csv", index=False)
    formation.to_csv(DATA / "paired_pm_formation_delays.csv", index=False)
    selected_power_table.to_csv(DATA / "paired_pm_selected_power.csv", index=False)

    plot_outputs(
        power_history,
        density_table,
        main_cold.densities[1.0],
        main_refinement.densities[1.0],
        halo_comparison,
    )

    particle_mass = RHO_M * P.box_mpc**3 / P.main_grid**3
    final_momentum_residual_cold = float(
        np.linalg.norm(np.sum(main_cold.final_momentum, axis=0))
        / max(np.sum(np.linalg.norm(main_cold.final_momentum, axis=1)), 1.0e-30)
    )
    final_momentum_residual_refinement = float(
        np.linalg.norm(np.sum(main_refinement.final_momentum, axis=0))
        / max(np.sum(np.linalg.norm(main_refinement.final_momentum, axis=1)), 1.0e-30)
    )
    main_halo_rms = float(
        np.sqrt(np.mean(halo_comparison["pm_minus_halo_model"].to_numpy(float) ** 2))
    )
    phase_group = phase_table.groupby("k_per_Mpc")["power_ratio"]
    phase_fractional_scatter = float(
        np.max(phase_group.std(ddof=1).to_numpy(float) / phase_group.mean().to_numpy(float))
    )

    checks: list[dict[str, str | float]] = []

    def add_check(identifier: str, statement: str, value: float, tolerance: float, mode: str = "max") -> None:
        passed = value <= tolerance if mode == "max" else value >= tolerance
        checks.append(
            {
                "id": identifier,
                "statement": statement,
                "value": value,
                "tolerance": tolerance,
                "status": "PASS" if passed else "FAIL",
            }
        )

    add_check("PM01", "CIC mass conservation in every main snapshot", float(max(abs(main_cold.densities[a].mean()) for a in main_cold.densities)), 5.0e-14)
    add_check("PM02", "Refinement CIC mass conservation in every main snapshot", float(max(abs(main_refinement.densities[a].mean()) for a in main_refinement.densities)), 5.0e-14)
    add_check("PM03", "Cold net PM force remains negligible", main_cold.maximum_net_force, 2.0e-14)
    add_check("PM04", "Refinement net PM force remains negligible", main_refinement.maximum_net_force, 2.0e-14)
    add_check("PM05", "Cold total canonical momentum remains negligible", final_momentum_residual_cold, 2.0e-14)
    add_check("PM06", "Refinement total canonical momentum remains negligible", final_momentum_residual_refinement, 2.0e-14)
    add_check("PM07", "Low-amplitude PM evolution recovers linear growth", linear_control["linear_relative_growth_error"], 1.5e-2)
    add_check("PM08", "Grid control keeps paired power ratios stable", float(convergence.grid_relative_difference.max()), 2.0e-2)
    add_check("PM09", "Time-step control keeps paired power ratios stable", float(convergence.time_relative_difference.max()), 6.0e-3)
    add_check("PM10", "Paired-phase ratio scatter remains small", phase_fractional_scatter, 1.5e-2)
    add_check("PM11", "The z=0 PM result agrees with the independent halo-model trend", main_halo_rms, 2.0e-2)
    add_check("PM12", "Paired density fields remain strongly cross-correlated at z=0", float(main_final_power.cross_correlation.min()), 0.99, mode="min")
    add_check("PM13", "Early high-k power retains a visible refinement suppression", 1.0 - interpolate_at(power_history[np.isclose(power_history.scale_factor, 0.05)], 8.0, "power_ratio"), 0.35, mode="min")
    add_check("PM14", "Nonlinear evolution regenerates most z=0 high-k power", interpolate_at(main_final_power, 8.0, "power_ratio"), 0.95, mode="min")
    add_check("PM15", "Refinement high-density mass fraction remains below cold at z=3", float(
        density_table[(density_table.branch == "refinement") & np.isclose(density_table.scale_factor, 0.25) & np.isclose(density_table.density_threshold, 20.0)].mass_fraction.iloc[0]
        / density_table[(density_table.branch == "cold") & np.isclose(density_table.scale_factor, 0.25) & np.isclose(density_table.density_threshold, 20.0)].mass_fraction.iloc[0]
    ), 0.98)
    add_check("PM16", "Refinement peak count remains below cold at z=3", float(
        density_table[(density_table.branch == "refinement") & np.isclose(density_table.scale_factor, 0.25) & np.isclose(density_table.density_threshold, 20.0)].peak_count.iloc[0]
        / density_table[(density_table.branch == "cold") & np.isclose(density_table.scale_factor, 0.25) & np.isclose(density_table.density_threshold, 20.0)].peak_count.iloc[0]
    ), 0.95)
    add_check("PM17", "Main simulation reaches the refinement half-mode scale", P.deconvolution_k_fraction * math.pi * P.main_grid / P.box_mpc, 8.0, mode="min")
    add_check("PM18", "Power ratios stay nonnegative", float(power_history.power_ratio.min()), 0.0, mode="min")
    add_check("PM19", "Cross-correlations obey the Cauchy bound", float(power_history.cross_correlation.max()), 1.0000001)
    add_check("PM20", "No paired cross-correlation becomes negative", float(power_history.cross_correlation.min()), 0.0, mode="min")

    check_table = pd.DataFrame.from_records(checks)
    check_table.to_csv(DATA / "paired_pm_checks.csv", index=False)

    selected = selected_power_table.set_index("k_per_Mpc")
    summary = {
        "parameters": asdict(P),
        "omega_m0": OMEGA_M,
        "omega_v0": OMEGA_V,
        "box_mpc": P.box_mpc,
        "main_particle_count": P.main_grid**3,
        "main_particle_mass_msun": particle_mass,
        "main_cell_mpc": P.box_mpc / P.main_grid,
        "main_usable_k_max_per_Mpc": P.deconvolution_k_fraction * math.pi * P.main_grid / P.box_mpc,
        "input_half_mode_k_per_Mpc": float(
            np.interp(0.5, (REFINEMENT_TRANSFER(np.geomspace(0.1, 30.0, 10000)) ** 2)[::-1], np.geomspace(0.1, 30.0, 10000)[::-1])
        ),
        "selected_power": selected_power,
        "z0_ratio_k8": float(selected.loc[8.0, "power_ratio_a_1"]),
        "a005_ratio_k8": float(selected.loc[8.0, "power_ratio_a_0.05"]),
        "z0_cross_k8": float(selected.loc[8.0, "cross_correlation_a_1"]),
        "halo_model_rms_difference": main_halo_rms,
        "phase_fractional_scatter_max": phase_fractional_scatter,
        "cold_maximum_net_force": main_cold.maximum_net_force,
        "refinement_maximum_net_force": main_refinement.maximum_net_force,
        "cold_final_momentum_residual": final_momentum_residual_cold,
        "refinement_final_momentum_residual": final_momentum_residual_refinement,
        "linear_control": linear_control,
        "main_wall_seconds_cold": main_cold.wall_seconds,
        "main_wall_seconds_refinement": main_refinement.wall_seconds,
        "total_wall_seconds": time.perf_counter() - start,
        "checks_pass": int((check_table.status == "PASS").sum()),
        "checks_fail": int((check_table.status == "FAIL").sum()),
    }
    (DATA / "Paired_Refinement_Particle_Mesh_Verification.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    output_files = [
        DATA / "paired_pm_power_history.csv",
        DATA / "paired_pm_density_statistics.csv",
        DATA / "paired_pm_convergence.csv",
        DATA / "paired_pm_phase_robustness.csv",
        DATA / "paired_pm_halo_model_comparison.csv",
        DATA / "paired_pm_formation_delays.csv",
        DATA / "paired_pm_selected_power.csv",
        DATA / "paired_pm_checks.csv",
        DATA / "Paired_Refinement_Particle_Mesh_Verification.json",
    ]
    manifest = {path.name: sha256(path) for path in output_files}
    (DATA / "data_sha256.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2, sort_keys=True))
    print(check_table.to_string(index=False))
    if summary["checks_fail"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
