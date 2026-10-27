from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import json
import math
from typing import Iterable

import numpy as np
import pandas as pd
import sympy as sp
from scipy.integrate import cumulative_trapezoid, solve_ivp
from scipy.interpolate import RegularGridInterpolator
from scipy.special import roots_genlaguerre, spherical_jn
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
FIG = ROOT / "figures"
DATA.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class Parameters:
    omega_r0: float = 9.0e-5
    omega_b0: float = 0.049
    omega_d0: float = 0.261
    h0_km_s_mpc: float = 70.0
    production_scale: float = 1.0e-6
    prime: int = 2
    sigma: float = 1.0
    lambda_over_A: float = 1.0e-4
    n_s: float = 0.965

    @property
    def omega_v0(self) -> float:
        return 1.0 - self.omega_r0 - self.omega_b0 - self.omega_d0

    @property
    def omega_m0(self) -> float:
        return self.omega_b0 + self.omega_d0

    @property
    def h0_over_c_per_mpc(self) -> float:
        return self.h0_km_s_mpc / 299792.458


P = Parameters()


# ---------------------------------------------------------------------------
# Phase-space quadrature for the scale-covariant dyadic production spectrum.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class PhaseGrid:
    levels: pd.DataFrame
    mass: np.ndarray
    q: np.ndarray
    base: np.ndarray
    dlnf_dlnq: np.ndarray

    @property
    def size(self) -> int:
        return int(self.mass.size)


def build_phase_grid(
    *,
    nq: int,
    production_scale: float,
    min_rest_fraction: float = 1.0e-6,
    max_level: int = 28,
) -> PhaseGrid:
    # First determine which levels carry non-negligible present rest density.
    x_ref, w_ref = roots_genlaguerre(96, 0.5)
    prefactor = 1.0 / (2.0 * math.pi ** 1.5)
    level_rows: list[dict[str, float]] = []
    for h in range(1, max_level + 1):
        mass = P.lambda_over_A * P.prime ** (P.sigma * h)
        degeneracy = (P.prime - 1) * P.prime ** (h - 1)
        suppression = math.exp(-math.pi * mass)
        q_scale = production_scale * math.sqrt(mass)
        rest = (
            degeneracy
            * suppression
            * q_scale**3
            * mass
            * prefactor
            * float(np.sum(w_ref))
        )
        level_rows.append(
            {
                "level": float(h),
                "mass_over_A": mass,
                "degeneracy": float(degeneracy),
                "suppression": suppression,
                "q_scale_over_A": q_scale,
                "present_rest_weight": rest,
            }
        )
    total_rest = sum(row["present_rest_weight"] for row in level_rows)
    retained = [
        row
        for row in level_rows
        if row["present_rest_weight"] / total_rest >= min_rest_fraction
    ]
    retained_total = sum(row["present_rest_weight"] for row in retained)
    for row in retained:
        row["retained_rest_fraction"] = row["present_rest_weight"] / retained_total

    lag_x, lag_w = roots_genlaguerre(nq, 0.5)
    x = np.sqrt(lag_x / math.pi)
    q_weight = prefactor * lag_w

    mass_values: list[float] = []
    q_values: list[float] = []
    base_values: list[float] = []
    derivatives: list[float] = []
    for row in retained:
        m = float(row["mass_over_A"])
        d = float(row["degeneracy"])
        suppression = float(row["suppression"])
        q_scale = float(row["q_scale_over_A"])
        for node, weight, laguerre_node in zip(x, q_weight, lag_x):
            mass_values.append(m)
            q_values.append(q_scale * float(node))
            base_values.append(d * suppression * q_scale**3 * float(weight))
            # f_0(q) is Gaussian in x=q/q_scale: d ln f_0 / d ln q=-2*pi*x^2=-2*y.
            derivatives.append(-2.0 * float(laguerre_node))

    return PhaseGrid(
        levels=pd.DataFrame(retained),
        mass=np.asarray(mass_values),
        q=np.asarray(q_values),
        base=np.asarray(base_values),
        dlnf_dlnq=np.asarray(derivatives),
    )


# ---------------------------------------------------------------------------
# Collisionless hierarchy and self-consistent post-recombination Poisson source.
# ---------------------------------------------------------------------------
class CollisionlessTowerSolver:
    def __init__(
        self,
        k_over_h0: Iterable[float],
        *,
        nq: int = 10,
        ell_max: int = 10,
        d_log_a: float = 0.004,
        production_scale: float = P.production_scale,
        a_initial: float = 1.0e-3,
    ) -> None:
        self.k = np.asarray(list(k_over_h0), dtype=float)
        if np.any(self.k <= 0.0):
            raise ValueError("all k/H0 values must be positive")
        self.nk = int(self.k.size)
        self.ell_max = int(ell_max)
        self.production_scale = float(production_scale)
        self.grid = build_phase_grid(
            nq=nq,
            production_scale=production_scale,
        )
        self.nphase = self.grid.size
        self.mass = self.grid.mass
        self.q = self.grid.q
        self.base = self.grid.base
        self.dlnf = self.grid.dlnf_dlnq
        self.n_initial = math.log(a_initial)
        self.n_final = 0.0
        count = int(math.ceil((self.n_final - self.n_initial) / d_log_a))
        self.step = (self.n_final - self.n_initial) / count
        self.count = count
        _, rho_today_bar, _ = self.background_phase(1.0)
        self.rho_today_bar = rho_today_bar
        self._build_streaming_table()

    def background_phase(self, a: float) -> tuple[np.ndarray, float, float]:
        eps = np.sqrt(self.q**2 + (a * self.mass) ** 2)
        rho_bar = float(np.sum(self.base * eps))
        pressure_bar = float(np.sum(self.base * self.q**2 / (3.0 * eps)))
        return eps, rho_bar, pressure_bar

    def background(self, log_a: float) -> dict[str, float | np.ndarray]:
        a = math.exp(log_a)
        eps, rho_bar, pressure_bar = self.background_phase(a)
        rho_ratio = a**-4 * rho_bar / self.rho_today_bar
        w_dark = pressure_bar / rho_bar
        e2 = (
            P.omega_r0 * a**-4
            + P.omega_b0 * a**-3
            + P.omega_d0 * rho_ratio
            + P.omega_v0
        )
        dlnh = -0.5 * (
            4.0 * P.omega_r0 * a**-4
            + 3.0 * P.omega_b0 * a**-3
            + 3.0 * P.omega_d0 * rho_ratio * (1.0 + w_dark)
        ) / e2
        return {
            "a": a,
            "eps": eps,
            "rho_bar": rho_bar,
            "pressure_bar": pressure_bar,
            "rho_ratio": rho_ratio,
            "w_dark": w_dark,
            "e2": e2,
            "dlnh": dlnh,
        }

    def _build_streaming_table(self) -> None:
        grid_count = max(2501, self.count + 1)
        self.stream_log_a = np.linspace(self.n_initial, self.n_final, grid_count)
        integrand = np.empty((grid_count, self.nphase), dtype=float)
        for i, value in enumerate(self.stream_log_a):
            bg = self.background(float(value))
            a = float(bg["a"])
            eps = np.asarray(bg["eps"])
            e = math.sqrt(float(bg["e2"]))
            integrand[i] = (self.q / eps) / (a * e)
        delta = np.diff(self.stream_log_a)
        stream = np.zeros_like(integrand)
        stream[1:] = np.cumsum(
            0.5 * (integrand[1:] + integrand[:-1]) * delta[:, None],
            axis=0,
        )
        self.stream_distance = stream

    def stream_at(self, log_a: float) -> np.ndarray:
        if log_a <= self.stream_log_a[0]:
            return self.stream_distance[0]
        if log_a >= self.stream_log_a[-1]:
            return self.stream_distance[-1]
        coordinate = (
            (log_a - self.stream_log_a[0])
            / (self.stream_log_a[-1] - self.stream_log_a[0])
            * (len(self.stream_log_a) - 1)
        )
        index = int(coordinate)
        fraction = coordinate - index
        return (
            (1.0 - fraction) * self.stream_distance[index]
            + fraction * self.stream_distance[index + 1]
        )

    def initial_state(self) -> np.ndarray:
        bg = self.background(self.n_initial)
        a = float(bg["a"])
        eps = np.asarray(bg["eps"])
        h_conformal = a * math.sqrt(float(bg["e2"]))
        k_conformal = self.k / h_conformal
        delta_initial = a

        state = np.zeros(
            (self.nk, 2 + self.nphase * (self.ell_max + 1)),
            dtype=float,
        )
        # Baryon variables: delta_b and u_b=theta_b/H_conformal.
        state[:, 0] = delta_initial
        state[:, 1] = -delta_initial

        hierarchy = state[:, 2:].reshape(
            self.nk,
            self.nphase,
            self.ell_max + 1,
        )
        hierarchy[:, :, 0] = delta_initial
        velocity = self.q / eps
        boost_shape = -self.dlnf / (3.0 * velocity)
        hierarchy[:, :, 1] = (
            -delta_initial / k_conformal[:, None]
        ) * boost_shape[None, :]
        return state

    def moments(
        self,
        log_a: float,
        state: np.ndarray,
    ) -> dict[str, np.ndarray | float]:
        bg = self.background(log_a)
        eps = np.asarray(bg["eps"])
        rho_bar = float(bg["rho_bar"])
        pressure_bar = float(bg["pressure_bar"])
        hierarchy = state[:, 2:].reshape(
            self.nk,
            self.nphase,
            self.ell_max + 1,
        )
        energy_weight = self.base * eps
        pressure_weight = self.base * self.q**2 / (3.0 * eps)
        delta_dark = np.sum(
            hierarchy[:, :, 0] * energy_weight[None, :],
            axis=1,
        ) / rho_bar
        delta_pressure_over_rho = np.sum(
            hierarchy[:, :, 0] * pressure_weight[None, :],
            axis=1,
        ) / rho_bar
        if self.ell_max >= 2:
            anisotropic = (
                (2.0 / 3.0)
                * np.sum(
                    hierarchy[:, :, 2]
                    * (self.base * self.q**2 / eps)[None, :],
                    axis=1,
                )
                / (rho_bar + pressure_bar)
            )
        else:
            anisotropic = np.zeros(self.nk)
        return {
            **bg,
            "delta_dark": delta_dark,
            "delta_pressure_over_rho": delta_pressure_over_rho,
            "sigma_dark": anisotropic,
        }

    def rhs(self, log_a: float, state: np.ndarray) -> np.ndarray:
        moments = self.moments(log_a, state)
        a = float(moments["a"])
        eps = np.asarray(moments["eps"])
        rho_ratio = float(moments["rho_ratio"])
        e2 = float(moments["e2"])
        dlnh = float(moments["dlnh"])
        delta_dark = np.asarray(moments["delta_dark"])

        h_conformal = a * math.sqrt(e2)
        k_conformal = self.k / h_conformal
        delta_b = state[:, 0]
        u_b = state[:, 1]

        gravitational_source = (
            P.omega_b0 * a**-1 * delta_b
            + P.omega_d0 * a**2 * rho_ratio * delta_dark
        )
        potential = -1.5 * gravitational_source / self.k**2

        derivative = np.zeros_like(state)
        derivative[:, 0] = -u_b
        dln_hconformal = 1.0 + dlnh
        derivative[:, 1] = (
            -(1.0 + dln_hconformal) * u_b
            + self.k**2 * potential / (a**2 * e2)
        )

        hierarchy = state[:, 2:].reshape(
            self.nk,
            self.nphase,
            self.ell_max + 1,
        )
        d_hierarchy = derivative[:, 2:].reshape(
            self.nk,
            self.nphase,
            self.ell_max + 1,
        )
        velocity = self.q / eps
        streaming = k_conformal[:, None] * velocity[None, :]

        d_hierarchy[:, :, 0] = -streaming * hierarchy[:, :, 1]
        d_hierarchy[:, :, 1] = k_conformal[:, None] * (
            velocity[None, :]
            * (hierarchy[:, :, 0] - 2.0 * hierarchy[:, :, 2])
            / 3.0
            - potential[:, None]
            * self.dlnf[None, :]
            / (3.0 * velocity[None, :])
        )
        for ell in range(2, self.ell_max):
            d_hierarchy[:, :, ell] = streaming * (
                ell * hierarchy[:, :, ell - 1]
                - (ell + 1) * hierarchy[:, :, ell + 1]
            ) / (2 * ell + 1)

        x_stream = self.k[:, None] * self.stream_at(log_a)[None, :]
        next_multipole = np.zeros((self.nk, self.nphase), dtype=float)
        mask = x_stream > self.ell_max + 1.0
        next_multipole[mask] = (
            (2 * self.ell_max + 1)
            * hierarchy[:, :, self.ell_max][mask]
            / x_stream[mask]
            - hierarchy[:, :, self.ell_max - 1][mask]
        )
        d_hierarchy[:, :, self.ell_max] = streaming * (
            self.ell_max * hierarchy[:, :, self.ell_max - 1]
            - (self.ell_max + 1) * next_multipole
        ) / (2 * self.ell_max + 1)
        return derivative

    def run(
        self,
        snapshot_a: np.ndarray,
    ) -> tuple[np.ndarray, pd.DataFrame, dict[str, np.ndarray]]:
        targets = np.asarray(snapshot_a, dtype=float)
        if targets[0] < math.exp(self.n_initial) - 1.0e-15 or targets[-1] > 1.0:
            raise ValueError("snapshot range must lie inside the integration interval")
        target_n = np.log(targets)
        state = self.initial_state()
        n_value = self.n_initial
        next_target = 0

        records: list[dict[str, float]] = []
        history = {
            "delta_b": np.empty((len(targets), self.nk)),
            "delta_dark": np.empty((len(targets), self.nk)),
            "matter_contrast": np.empty((len(targets), self.nk)),
            "weyl_source": np.empty((len(targets), self.nk)),
            "sigma_dark": np.empty((len(targets), self.nk)),
        }

        def record(index: int, n_at: float, state_at: np.ndarray) -> None:
            mom = self.moments(n_at, state_at)
            a = float(mom["a"])
            delta_b = state_at[:, 0]
            delta_dark = np.asarray(mom["delta_dark"])
            rho_ratio = float(mom["rho_ratio"])
            matter_denominator = P.omega_b0 * a**-3 + P.omega_d0 * rho_ratio
            matter_contrast = (
                P.omega_b0 * a**-3 * delta_b
                + P.omega_d0 * rho_ratio * delta_dark
            ) / matter_denominator
            sigma_dark = np.asarray(mom["sigma_dark"])
            # In conformal Newtonian gauge, the subhorizon Weyl source includes
            # the collisionless gravitational-slip correction:
            # k^2(Phi+Psi) = -3 H0^2 [S_delta - 3 S_sigma/2].
            source = (
                P.omega_b0 * a**-1 * delta_b
                + P.omega_d0 * a**2 * rho_ratio * delta_dark
                - 1.5
                * P.omega_d0
                * a**2
                * rho_ratio
                * (1.0 + float(mom["w_dark"]))
                * sigma_dark
            )
            history["delta_b"][index] = delta_b
            history["delta_dark"][index] = delta_dark
            history["matter_contrast"][index] = matter_contrast
            history["weyl_source"][index] = source
            history["sigma_dark"][index] = sigma_dark
            records.append(
                {
                    "a": a,
                    "z": 1.0 / a - 1.0,
                    "rho_D_over_rho_D0": rho_ratio,
                    "w_D": float(mom["w_dark"]),
                }
            )

        # Record the exact first snapshot.
        while next_target < len(targets) and target_n[next_target] <= n_value + 1.0e-14:
            record(next_target, float(target_n[next_target]), state)
            next_target += 1

        for _ in range(self.count):
            previous_n = n_value
            previous_state = state.copy()
            h = self.step
            k1 = self.rhs(n_value, state)
            k2 = self.rhs(n_value + 0.5 * h, state + 0.5 * h * k1)
            k3 = self.rhs(n_value + 0.5 * h, state + 0.5 * h * k2)
            k4 = self.rhs(n_value + h, state + h * k3)
            state = state + h * (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0
            n_value += h
            while next_target < len(targets) and target_n[next_target] <= n_value + 1.0e-14:
                fraction = (target_n[next_target] - previous_n) / (n_value - previous_n)
                interpolated = previous_state + fraction * (state - previous_state)
                record(next_target, float(target_n[next_target]), interpolated)
                next_target += 1
        while next_target < len(targets):
            record(next_target, float(target_n[next_target]), state)
            next_target += 1

        return state, pd.DataFrame(records), history


# ---------------------------------------------------------------------------
# Cold two-fluid reference and the previous adiabatic-fluid closure.
# ---------------------------------------------------------------------------
def cold_reference(
    k_values: np.ndarray,
    snapshot_a: np.ndarray,
    *,
    d_log_a: float = 0.004,
) -> dict[str, np.ndarray]:
    k = np.asarray(k_values, dtype=float)
    n_initial = math.log(float(snapshot_a[0]))
    count = int(math.ceil(-n_initial / d_log_a))
    step = -n_initial / count
    state = np.tile(
        np.array([snapshot_a[0], -snapshot_a[0], snapshot_a[0], -snapshot_a[0]]),
        (len(k), 1),
    )
    target_n = np.log(snapshot_a)
    next_target = 0
    n_value = n_initial
    history = {
        "delta_b": np.empty((len(snapshot_a), len(k))),
        "delta_dark": np.empty((len(snapshot_a), len(k))),
        "matter_contrast": np.empty((len(snapshot_a), len(k))),
        "weyl_source": np.empty((len(snapshot_a), len(k))),
    }

    def background(n: float) -> tuple[float, float, float]:
        a = math.exp(n)
        e2 = (
            P.omega_r0 * a**-4
            + P.omega_m0 * a**-3
            + P.omega_v0
        )
        dlnh = -0.5 * (
            4.0 * P.omega_r0 * a**-4
            + 3.0 * P.omega_m0 * a**-3
        ) / e2
        return a, e2, dlnh

    def rhs(n: float, y: np.ndarray) -> np.ndarray:
        a, e2, dlnh = background(n)
        delta_b, u_b, delta_d, u_d = y.T
        source = P.omega_b0 * a**-1 * delta_b + P.omega_d0 * a**-1 * delta_d
        potential = -1.5 * source / k**2
        dln_hc = 1.0 + dlnh
        result = np.empty_like(y)
        result[:, 0] = -u_b
        result[:, 2] = -u_d
        result[:, 1] = -(1.0 + dln_hc) * u_b + k**2 * potential / (a**2 * e2)
        result[:, 3] = -(1.0 + dln_hc) * u_d + k**2 * potential / (a**2 * e2)
        return result

    def record(index: int, n: float, y: np.ndarray) -> None:
        a, _, _ = background(n)
        delta_b, _, delta_d, _ = y.T
        history["delta_b"][index] = delta_b
        history["delta_dark"][index] = delta_d
        history["matter_contrast"][index] = (
            P.omega_b0 * delta_b + P.omega_d0 * delta_d
        ) / P.omega_m0
        history["weyl_source"][index] = a**-1 * (
            P.omega_b0 * delta_b + P.omega_d0 * delta_d
        )

    while next_target < len(snapshot_a) and target_n[next_target] <= n_value + 1.0e-14:
        record(next_target, float(target_n[next_target]), state)
        next_target += 1
    for _ in range(count):
        old_n = n_value
        old_state = state.copy()
        h = step
        k1 = rhs(n_value, state)
        k2 = rhs(n_value + 0.5 * h, state + 0.5 * h * k1)
        k3 = rhs(n_value + 0.5 * h, state + 0.5 * h * k2)
        k4 = rhs(n_value + h, state + h * k3)
        state = state + h * (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0
        n_value += h
        while next_target < len(snapshot_a) and target_n[next_target] <= n_value + 1.0e-14:
            fraction = (target_n[next_target] - old_n) / (n_value - old_n)
            interpolated = old_state + fraction * (state - old_state)
            record(next_target, float(target_n[next_target]), interpolated)
            next_target += 1
    while next_target < len(snapshot_a):
        record(next_target, float(target_n[next_target]), state)
        next_target += 1
    return history


def fluid_closure_final(
    k_values: np.ndarray,
    *,
    production_scale: float,
    d_log_a: float = 0.004,
) -> np.ndarray:
    k = np.asarray(k_values, dtype=float)
    n_initial = math.log(1.0e-3)
    count = int(math.ceil(-n_initial / d_log_a))
    step = -n_initial / count
    initial = math.exp(n_initial)
    state = np.tile(np.array([initial, -initial, initial, -initial]), (len(k), 1))
    n_value = n_initial

    def rhs(n: float, y: np.ndarray) -> np.ndarray:
        a = math.exp(n)
        e2 = P.omega_r0 * a**-4 + P.omega_m0 * a**-3 + P.omega_v0
        dlnh = -0.5 * (
            4.0 * P.omega_r0 * a**-4 + 3.0 * P.omega_m0 * a**-3
        ) / e2
        delta_b, u_b, delta_d, u_d = y.T
        source = P.omega_b0 * a**-1 * delta_b + P.omega_d0 * a**-1 * delta_d
        potential = -1.5 * source / k**2
        pressure = production_scale**2 * k**2 / (3.0 * a**4 * e2)
        dln_hc = 1.0 + dlnh
        result = np.empty_like(y)
        result[:, 0] = -u_b
        result[:, 2] = -u_d
        result[:, 1] = -(1.0 + dln_hc) * u_b + k**2 * potential / (a**2 * e2)
        result[:, 3] = (
            -(1.0 + dln_hc) * u_d
            + k**2 * potential / (a**2 * e2)
            + pressure * delta_d
        )
        return result

    for _ in range(count):
        h = step
        k1 = rhs(n_value, state)
        k2 = rhs(n_value + 0.5 * h, state + 0.5 * h * k1)
        k3 = rhs(n_value + 0.5 * h, state + 0.5 * h * k2)
        k4 = rhs(n_value + h, state + h * k3)
        state += h * (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0
        n_value += h
    return state


# ---------------------------------------------------------------------------
# Free-streaming hierarchy benchmark.
# ---------------------------------------------------------------------------
def free_streaming_rhs(x: float, state: np.ndarray, ell_max: int) -> np.ndarray:
    derivative = np.zeros_like(state)
    derivative[0] = -state[1]
    for ell in range(1, ell_max):
        derivative[ell] = (
            ell * state[ell - 1] - (ell + 1) * state[ell + 1]
        ) / (2 * ell + 1)
    if x > ell_max + 1.0:
        next_value = (2 * ell_max + 1) * state[ell_max] / x - state[ell_max - 1]
    else:
        next_value = 0.0
    derivative[ell_max] = (
        ell_max * state[ell_max - 1] - (ell_max + 1) * next_value
    ) / (2 * ell_max + 1)
    return derivative


def free_streaming_test(ell_max: int, x_final: float) -> float:
    initial = np.zeros(ell_max + 1)
    initial[0] = 1.0
    result = solve_ivp(
        lambda x, y: free_streaming_rhs(x, y, ell_max),
        (1.0e-8, x_final),
        initial,
        rtol=2.0e-11,
        atol=2.0e-13,
        max_step=0.02,
    ).y[:, -1]
    exact = np.asarray([spherical_jn(ell, x_final) for ell in range(ell_max + 1)])
    return float(np.max(np.abs(result[: min(8, ell_max)] - exact[: min(8, ell_max)])))


# ---------------------------------------------------------------------------
# Main hierarchy run.
# ---------------------------------------------------------------------------
K_GRID = np.geomspace(30.0, 3.0e5, 48)
A_SNAPSHOTS = np.geomspace(1.0e-3, 1.0, 54)
MAIN_SOLVER = CollisionlessTowerSolver(
    K_GRID,
    nq=8,
    ell_max=8,
    d_log_a=0.005,
)
FINAL_STATE, BACKGROUND_RECORDS, MODEL_HISTORY = MAIN_SOLVER.run(A_SNAPSHOTS)
COLD_HISTORY = cold_reference(K_GRID, A_SNAPSHOTS, d_log_a=0.005)

MATTER_TRANSFER = MODEL_HISTORY["matter_contrast"] / COLD_HISTORY["matter_contrast"]
WEYL_TRANSFER = MODEL_HISTORY["weyl_source"] / COLD_HISTORY["weyl_source"]
POWER_RATIO = MATTER_TRANSFER**2

# Growth rate and f*sigma8 ratios are obtained on the common log-a grid.
LOG_A = np.log(A_SNAPSHOTS)
F_MODEL = np.gradient(
    np.log(np.abs(MODEL_HISTORY["matter_contrast"])),
    LOG_A,
    axis=0,
    edge_order=2,
)
F_COLD = np.gradient(
    np.log(np.abs(COLD_HISTORY["matter_contrast"])),
    LOG_A,
    axis=0,
    edge_order=2,
)
FSIGMA8_RATIO = (
    F_MODEL * MODEL_HISTORY["matter_contrast"]
) / (
    F_COLD * COLD_HISTORY["matter_contrast"]
)

# Present transfer and half-mode scales.
T0 = MATTER_TRANSFER[-1]
P0 = T0**2


def crossing_scale(values: np.ndarray, target: float) -> float:
    indices = np.where(values <= target)[0]
    if len(indices) == 0:
        return float("nan")
    index = int(indices[0])
    if index == 0:
        return float(K_GRID[0])
    x0, x1 = np.log(K_GRID[index - 1]), np.log(K_GRID[index])
    y0, y1 = values[index - 1], values[index]
    fraction = (target - y0) / (y1 - y0)
    return float(math.exp(x0 + fraction * (x1 - x0)))


K_HALF_AMPLITUDE = crossing_scale(T0, 0.5)
K_HALF_POWER = crossing_scale(P0, 0.5)
K_HALF_AMPLITUDE_MPC = K_HALF_AMPLITUDE * P.h0_over_c_per_mpc
K_HALF_POWER_MPC = K_HALF_POWER * P.h0_over_c_per_mpc

# Previous fluid closure, evaluated on the same k grid.
FLUID_FINAL = fluid_closure_final(K_GRID, production_scale=P.production_scale)
COLD_FINAL = np.column_stack(
    [
        COLD_HISTORY["delta_b"][-1],
        np.zeros(len(K_GRID)),
        COLD_HISTORY["delta_dark"][-1],
        np.zeros(len(K_GRID)),
    ]
)
FLUID_SOURCE = P.omega_b0 * FLUID_FINAL[:, 0] + P.omega_d0 * FLUID_FINAL[:, 2]
COLD_SOURCE_FINAL = (
    P.omega_b0 * COLD_HISTORY["delta_b"][-1]
    + P.omega_d0 * COLD_HISTORY["delta_dark"][-1]
)
FLUID_TRANSFER = FLUID_SOURCE / COLD_SOURCE_FINAL

# ---------------------------------------------------------------------------
# Convergence and limiting tests.
# ---------------------------------------------------------------------------
TEST_K = np.asarray([300.0, 30000.0, 100000.0])
TEST_A = np.asarray([1.0e-3, 1.0])


def final_transfer(
    *,
    nq: int,
    ell_max: int,
    d_log_a: float,
    production_scale: float = P.production_scale,
) -> np.ndarray:
    solver = CollisionlessTowerSolver(
        TEST_K,
        nq=nq,
        ell_max=ell_max,
        d_log_a=d_log_a,
        production_scale=production_scale,
    )
    _, _, history = solver.run(TEST_A)
    cold = cold_reference(TEST_K, TEST_A, d_log_a=d_log_a)
    return history["matter_contrast"][-1] / cold["matter_contrast"][-1]


Q6 = final_transfer(nq=6, ell_max=8, d_log_a=0.005)
Q8 = final_transfer(nq=8, ell_max=8, d_log_a=0.005)
Q10 = final_transfer(nq=10, ell_max=8, d_log_a=0.005)
L6 = final_transfer(nq=8, ell_max=6, d_log_a=0.005)
L8 = final_transfer(nq=8, ell_max=8, d_log_a=0.005)
D10 = final_transfer(nq=8, ell_max=8, d_log_a=0.010)
D5 = final_transfer(nq=8, ell_max=8, d_log_a=0.005)
D25 = final_transfer(nq=8, ell_max=8, d_log_a=0.0025)
COLD_LIMIT = final_transfer(
    nq=8,
    ell_max=8,
    d_log_a=0.005,
    production_scale=1.0e-8,
)

quadrature_residual = float(np.max(np.abs(Q10 - Q8)))
hierarchy_residual = float(np.max(np.abs(L8 - L6)))
time_residual = float(np.max(np.abs(D25 - D5)))
time_coarse_residual = float(np.max(np.abs(D5 - D10)))
if time_residual > 0.0 and time_coarse_residual > 0.0:
    time_order = math.log(time_coarse_residual / time_residual, 2.0)
else:
    time_order = float("nan")
cold_limit_residual = float(np.max(np.abs(COLD_LIMIT - 1.0)))

# Gaussian boost integration-by-parts identity.
y_symbol = sp.symbols("y", positive=True)
boost_average = sp.simplify(
    sp.integrate(
        y_symbol ** sp.Rational(1, 2)
        * sp.exp(-y_symbol)
        * (2 * y_symbol / 3),
        (y_symbol, 0, sp.oo),
    )
    / sp.integrate(
        y_symbol ** sp.Rational(1, 2) * sp.exp(-y_symbol),
        (y_symbol, 0, sp.oo),
    )
)
boost_identity_residual = float(abs(sp.N(boost_average - 1)))

# Free-streaming hierarchy test.
free_streaming_residual = free_streaming_test(ell_max=18, x_final=15.0)

# ---------------------------------------------------------------------------
# Late-time observable templates.
# ---------------------------------------------------------------------------
log_k_grid = np.log(K_GRID)
log_a_grid = np.log(A_SNAPSHOTS)
transfer_interpolator = RegularGridInterpolator(
    (log_a_grid, log_k_grid),
    MATTER_TRANSFER,
    bounds_error=False,
    fill_value=None,
)
weyl_interpolator = RegularGridInterpolator(
    (log_a_grid, log_k_grid),
    WEYL_TRANSFER,
    bounds_error=False,
    fill_value=None,
)

# Background distance in H0^{-1} units.
A_DISTANCE = np.geomspace(1.0e-3, 1.0, 5000)
# Use the exact tower background from the main phase grid.
def e_background(a: float) -> float:
    _, rho_bar, _ = MAIN_SOLVER.background_phase(a)
    rho_ratio = a**-4 * rho_bar / MAIN_SOLVER.rho_today_bar
    return math.sqrt(
        P.omega_r0 * a**-4
        + P.omega_b0 * a**-3
        + P.omega_d0 * rho_ratio
        + P.omega_v0
    )

E_DISTANCE = np.asarray([e_background(float(a)) for a in A_DISTANCE])
integrand_distance = 1.0 / (A_DISTANCE**2 * E_DISTANCE)
# chi(a)=integral_a^1 da/(a^2 E).
reverse_integral = cumulative_trapezoid(
    integrand_distance[::-1],
    A_DISTANCE[::-1],
    initial=0.0,
)
CHI_DISTANCE = -reverse_integral[::-1]


def chi_of_a(a: np.ndarray | float) -> np.ndarray:
    return np.interp(np.asarray(a), A_DISTANCE, CHI_DISTANCE)


def cold_growth_of_a(a: np.ndarray | float) -> np.ndarray:
    # All cold k modes are identical; use the first one and normalize today.
    values = np.interp(
        np.log(np.asarray(a)),
        log_a_grid,
        COLD_HISTORY["matter_contrast"][:, 0],
    )
    return values / COLD_HISTORY["matter_contrast"][-1, 0]


K_EQUALITY = P.omega_m0 * math.sqrt(2.0 / P.omega_r0)


def reference_transfer(k: np.ndarray) -> np.ndarray:
    # Controlled analytic equality filter used only as a positive lensing weight.
    return 1.0 / (1.0 + (k / K_EQUALITY) ** 2)


def interpolate_transfer(
    interpolator: RegularGridInterpolator,
    a: np.ndarray,
    k: np.ndarray,
) -> np.ndarray:
    a_clipped = np.clip(a, A_SNAPSHOTS[0], A_SNAPSHOTS[-1])
    k_clipped = np.clip(k, K_GRID[0], K_GRID[-1])
    points = np.column_stack([np.log(a_clipped), np.log(k_clipped)])
    return np.asarray(interpolator(points), dtype=float)


def lensing_ratio(z_source: float, ell: float) -> float:
    a_source = max(1.0 / (1.0 + z_source), A_SNAPSHOTS[0])
    a = np.geomspace(a_source * (1.0 + 1.0e-6), 0.9999, 900)
    chi = chi_of_a(a)
    chi_source = float(chi_of_a(a_source))
    separation = np.maximum(chi_source - chi, 0.0)
    k = (ell + 0.5) / np.maximum(chi, 1.0e-8)
    growth = cold_growth_of_a(a)
    p_reference = (
        np.maximum(k, 1.0e-12) ** P.n_s
        * reference_transfer(k) ** 2
        * growth**2
    )
    common = (
        1.0 / (a**2 * np.asarray([e_background(float(x)) for x in a]))
        * (separation / (chi_source * a)) ** 2
        * p_reference
    )
    model_t = interpolate_transfer(weyl_interpolator, a, k)
    numerator = float(np.trapezoid(common * model_t**2, a))
    denominator = float(np.trapezoid(common, a))
    return numerator / denominator


lensing_rows: list[dict[str, float | str]] = []
for source_label, source_z, multipoles in [
    ("galaxy_z0p5", 0.5, [100, 500, 1000, 3000, 5000]),
    ("galaxy_z1", 1.0, [100, 500, 1000, 3000, 5000]),
    ("galaxy_z2", 2.0, [100, 500, 1000, 3000, 5000]),
    ("cmb_lensing_z999", 999.0, [40, 100, 400, 1000, 2000, 3000]),
]:
    for ell in multipoles:
        lensing_rows.append(
            {
                "source": source_label,
                "z_source": source_z,
                "ell": float(ell),
                "linear_lensing_power_ratio": lensing_ratio(source_z, float(ell)),
            }
        )
LENSING = pd.DataFrame(lensing_rows)

# Snapshot observables at selected redshifts and k values.
selected_z = [0.0, 0.5, 1.0, 2.0, 5.0]
selected_k = [300.0, 3000.0, 30000.0, 100000.0]
observable_rows: list[dict[str, float]] = []
for redshift in selected_z:
    a_value = 1.0 / (1.0 + redshift)
    ai = int(np.argmin(np.abs(A_SNAPSHOTS - a_value)))
    for kval in selected_k:
        ki = int(np.argmin(np.abs(K_GRID - kval)))
        observable_rows.append(
            {
                "z": redshift,
                "a_sample": float(A_SNAPSHOTS[ai]),
                "k_over_H0": float(K_GRID[ki]),
                "matter_transfer_amplitude": float(MATTER_TRANSFER[ai, ki]),
                "matter_power_ratio": float(POWER_RATIO[ai, ki]),
                "weyl_source_transfer": float(WEYL_TRANSFER[ai, ki]),
                "f_sigma8_ratio": float(FSIGMA8_RATIO[ai, ki]),
                "dark_anisotropic_stress": float(MODEL_HISTORY["sigma_dark"][ai, ki]),
            }
        )
OBSERVABLES = pd.DataFrame(observable_rows)

# A primary-CMB-scale diagnostic: this post-recombination hierarchy is initialized
# at a=1e-3, so it computes late lensing only.  The k range corresponding to
# ell<=3000 at last scattering lies well below the present half-mode.
chi_last_scattering = float(chi_of_a(1.0e-3))
K_PRIMARY_MAX = 3000.5 / chi_last_scattering
PRIMARY_SCALE_FRACTION_OF_POWER_HALF = K_PRIMARY_MAX / K_HALF_POWER

# ---------------------------------------------------------------------------
# Output tables.
# ---------------------------------------------------------------------------
transfer_rows: list[dict[str, float]] = []
for index, kval in enumerate(K_GRID):
    transfer_rows.append(
        {
            "k_over_H0": float(kval),
            "k_per_Mpc_for_H0_70": float(kval * P.h0_over_c_per_mpc),
            "collisionless_transfer_amplitude_z0": float(T0[index]),
            "collisionless_power_ratio_z0": float(P0[index]),
            "fluid_transfer_amplitude_z0": float(FLUID_TRANSFER[index]),
            "weyl_source_transfer_z0": float(WEYL_TRANSFER[-1, index]),
            "dark_anisotropic_stress_z0": float(MODEL_HISTORY["sigma_dark"][-1, index]),
        }
    )
TRANSFER_TABLE = pd.DataFrame(transfer_rows)

history_rows: list[dict[str, float]] = []
for ai, a_value in enumerate(A_SNAPSHOTS):
    for ki, kval in enumerate(K_GRID):
        history_rows.append(
            {
                "a": float(a_value),
                "z": float(1.0 / a_value - 1.0),
                "k_over_H0": float(kval),
                "matter_transfer_amplitude": float(MATTER_TRANSFER[ai, ki]),
                "weyl_source_transfer": float(WEYL_TRANSFER[ai, ki]),
                "f_sigma8_ratio": float(FSIGMA8_RATIO[ai, ki]),
            }
        )
HISTORY_TABLE = pd.DataFrame(history_rows)

convergence_rows = [
    {"test": "quadrature", "coarse": float(np.max(np.abs(Q8 - Q6))), "fine": quadrature_residual, "observed_order": np.nan},
    {"test": "hierarchy_truncation", "coarse": hierarchy_residual, "fine": hierarchy_residual, "observed_order": np.nan},
    {"test": "time_step", "coarse": time_coarse_residual, "fine": time_residual, "observed_order": time_order},
    {"test": "cold_limit", "coarse": np.nan, "fine": cold_limit_residual, "observed_order": np.nan},
]
CONVERGENCE = pd.DataFrame(convergence_rows)

TRANSFER_TABLE.to_csv(DATA / "collisionless_dark_transfer_curve.csv", index=False)
HISTORY_TABLE.to_csv(DATA / "collisionless_transfer_history.csv", index=False)
OBSERVABLES.to_csv(DATA / "linear_observable_ratios.csv", index=False)
LENSING.to_csv(DATA / "linear_lensing_ratios.csv", index=False)
CONVERGENCE.to_csv(DATA / "collisionless_hierarchy_convergence.csv", index=False)
MAIN_SOLVER.grid.levels.to_csv(DATA / "collisionless_retained_levels.csv", index=False)

# ---------------------------------------------------------------------------
# Figures.
# ---------------------------------------------------------------------------
plt.figure(figsize=(7.6, 4.9))
plt.semilogx(K_GRID, T0, label="collisionless hierarchy")
plt.semilogx(K_GRID, FLUID_TRANSFER, linestyle="--", label="adiabatic fluid closure")
plt.axhline(1.0, linewidth=0.9)
plt.axhline(0.5, linestyle=":", linewidth=0.9)
plt.xlabel(r"$k/H_0$")
plt.ylabel("Present matter-transfer amplitude")
plt.title("The collisionless tower resolves the cutoff beyond the fluid closure")
plt.legend(fontsize=8)
plt.tight_layout()
plt.savefig(FIG / "collisionless_vs_fluid_transfer.png", dpi=220)
plt.close()

plt.figure(figsize=(7.6, 4.9))
for redshift in [0.0, 0.5, 1.0, 2.0, 5.0]:
    ai = int(np.argmin(np.abs(A_SNAPSHOTS - 1.0 / (1.0 + redshift))))
    plt.semilogx(K_GRID, POWER_RATIO[ai], label=fr"$z={redshift:g}$")
plt.axhline(1.0, linewidth=0.9)
plt.axhline(0.5, linestyle=":", linewidth=0.9)
plt.xlabel(r"$k/H_0$")
plt.ylabel(r"$P_m/P_{m,\mathrm{cold}}$")
plt.title("The same distribution fixes the redshift-dependent linear power cutoff")
plt.legend(fontsize=8)
plt.tight_layout()
plt.savefig(FIG / "matter_power_ratio_history.png", dpi=220)
plt.close()

plt.figure(figsize=(7.6, 4.9))
for source in LENSING["source"].unique():
    subset = LENSING[LENSING["source"] == source]
    plt.semilogx(subset["ell"], subset["linear_lensing_power_ratio"], marker="o", label=source)
plt.axhline(1.0, linewidth=0.9)
plt.xlabel(r"Multipole $\ell$")
plt.ylabel("Linear lensing-power ratio")
plt.title("Late-time weak and CMB-lensing templates use the same dark transfer")
plt.legend(fontsize=7)
plt.tight_layout()
plt.savefig(FIG / "lensing_power_ratios.png", dpi=220)
plt.close()

plt.figure(figsize=(7.6, 4.9))
for kval in [300.0, 3000.0, 30000.0, 100000.0]:
    ki = int(np.argmin(np.abs(K_GRID - kval)))
    plt.semilogx(A_SNAPSHOTS, MATTER_TRANSFER[:, ki], label=fr"$k/H_0\approx{K_GRID[ki]:.0f}$")
plt.axhline(1.0, linewidth=0.9)
plt.xlabel("Scale factor")
plt.ylabel("Matter-transfer amplitude")
plt.title("Free streaming accumulates only below the scale-covariant cutoff")
plt.legend(fontsize=8)
plt.tight_layout()
plt.savefig(FIG / "transfer_growth_history.png", dpi=220)
plt.close()

# ---------------------------------------------------------------------------
# Verification ledger.
# ---------------------------------------------------------------------------
checks: list[dict[str, object]] = []


def add_check(
    check_id: str,
    statement: str,
    value: float,
    tolerance: float,
    *,
    status: str | None = None,
) -> None:
    if status is None:
        status = "PASS" if abs(value) <= tolerance else "FAIL"
    checks.append(
        {
            "id": check_id,
            "statement": statement,
            "value": float(value),
            "tolerance": float(tolerance),
            "status": status,
        }
    )


add_check("CB01", "Gaussian boost moment reproduces the growing-mode continuity normalization", boost_identity_residual, 1.0e-14)
add_check("CB02", "free-streaming hierarchy reproduces spherical Bessel multipoles", free_streaming_residual, 2.0e-8)
add_check("CB03", "momentum quadrature is converged on the declared transfer sample", quadrature_residual, 2.0e-3)
add_check("CB04", "multipole truncation is converged on the declared transfer sample", hierarchy_residual, 2.0e-3)
add_check("CB05", "time-step refinement is converged on the declared transfer sample", time_residual, 2.0e-6)
add_check("CB06", "cold-production limit recovers the pressureless reference", cold_limit_residual, 6.0e-4)
add_check("CB07", "large-scale collisionless transfer recovers unity", abs(float(T0[0]) - 1.0), 2.0e-6)
add_check("CB08", "collisionless transfer has a finite amplitude half-mode", 0.0 if math.isfinite(K_HALF_AMPLITUDE) else 1.0, 0.0)
add_check("CB09", "collisionless transfer has a finite power half-mode", 0.0 if math.isfinite(K_HALF_POWER) else 1.0, 0.0)
add_check("CB10", "power half-mode lies below the amplitude half-mode", max(K_HALF_POWER - K_HALF_AMPLITUDE, 0.0), 0.0)
add_check("CB11", "dark anisotropic stress remains finite in the late hierarchy", 0.0 if np.all(np.isfinite(MODEL_HISTORY["sigma_dark"])) else 1.0, 0.0)
add_check("CB12", "matter transfer remains positive over the declared grid", max(-float(np.min(MATTER_TRANSFER)), 0.0), 0.0)
add_check("CB13", "Weyl-source transfer remains positive over the declared grid", max(-float(np.min(WEYL_TRANSFER)), 0.0), 0.0)
add_check("CB14", "galaxy and CMB lensing templates remain finite and positive", 0.0 if np.all(np.isfinite(LENSING["linear_lensing_power_ratio"])) and np.all(LENSING["linear_lensing_power_ratio"] > 0) else 1.0, 0.0)
add_check("CB15", "primary acoustic k range is below the late-time power half-mode", max(PRIMARY_SCALE_FRACTION_OF_POWER_HALF - 1.0, 0.0), 0.0)
add_check("CB16", "retained level weights sum to unity", abs(float(MAIN_SOLVER.grid.levels["retained_rest_fraction"].sum()) - 1.0), 1.0e-14)
add_check("CB17", "fluid and hierarchy closures agree on large scales", abs(float(T0[8] - FLUID_TRANSFER[8])), 3.0e-3)
add_check("CB18", "the hierarchy produces stronger-than-one-percent small-scale departure from the fluid closure", max(0.01 - float(np.max(np.abs(T0 - FLUID_TRANSFER))), 0.0), 0.0)
add_check("CB19", "linear power ratio decreases below one at the highest resolved k", max(float(P0[-1]) - 1.0, 0.0), 0.0)
add_check("CB20", "all reported observable ratios are finite", 0.0 if np.all(np.isfinite(OBSERVABLES.select_dtypes(include=[float, int]).to_numpy())) else 1.0, 0.0)

CHECKS = pd.DataFrame(checks)
CHECKS.to_csv(DATA / "collisionless_boltzmann_checks.csv", index=False)

summary = {
    "parameters": asdict(P),
    "numerical_configuration": {
        "k_count": int(len(K_GRID)),
        "snapshot_count": int(len(A_SNAPSHOTS)),
        "retained_levels": int(len(MAIN_SOLVER.grid.levels)),
        "phase_nodes": int(MAIN_SOLVER.nphase),
        "ell_max": int(MAIN_SOLVER.ell_max),
        "d_log_a": float(MAIN_SOLVER.step),
    },
    "hierarchy": {
        "free_streaming_residual": free_streaming_residual,
        "quadrature_residual": quadrature_residual,
        "multipole_residual": hierarchy_residual,
        "time_step_residual": time_residual,
        "observed_time_order": time_order,
        "cold_limit_residual": cold_limit_residual,
    },
    "cutoff": {
        "amplitude_half_mode_k_over_H0": K_HALF_AMPLITUDE,
        "amplitude_half_mode_per_Mpc_H0_70": K_HALF_AMPLITUDE_MPC,
        "power_half_mode_k_over_H0": K_HALF_POWER,
        "power_half_mode_per_Mpc_H0_70": K_HALF_POWER_MPC,
        "primary_ell3000_k_over_H0": K_PRIMARY_MAX,
        "primary_scale_over_power_half_mode": PRIMARY_SCALE_FRACTION_OF_POWER_HALF,
    },
    "lensing": LENSING.to_dict(orient="records"),
    "counts": {
        "pass": int((CHECKS["status"] == "PASS").sum()),
        "fail": int((CHECKS["status"] == "FAIL").sum()),
    },
}
(DATA / "Scale_Covariant_Collisionless_Boltzmann_Verification.json").write_text(
    json.dumps(summary, indent=2),
    encoding="utf-8",
)

hashes: dict[str, str] = {}
for file_name in [
    "collisionless_dark_transfer_curve.csv",
    "collisionless_transfer_history.csv",
    "linear_observable_ratios.csv",
    "linear_lensing_ratios.csv",
    "collisionless_hierarchy_convergence.csv",
    "collisionless_retained_levels.csv",
    "collisionless_boltzmann_checks.csv",
    "Scale_Covariant_Collisionless_Boltzmann_Verification.json",
]:
    path = DATA / file_name
    hashes[file_name] = hashlib.sha256(path.read_bytes()).hexdigest()
(DATA / "data_sha256.json").write_text(json.dumps(hashes, indent=2), encoding="utf-8")

if summary["counts"]["fail"]:
    print(CHECKS.to_string(index=False))
    raise SystemExit(json.dumps(summary, indent=2))

print(json.dumps(summary, indent=2))
