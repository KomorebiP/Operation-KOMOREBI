from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import os
import json
import math
import time

import numpy as np
import pandas as pd
from numba import njit
from scipy.integrate import cumulative_trapezoid, solve_ivp
from scipy.interpolate import CubicSpline, PchipInterpolator
from scipy.optimize import brentq
from scipy.special import erfc

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
FIG = ROOT / "figures"
PARENT = Path(os.environ.get("COLLISIONLESS_TRANSFER_DIR", str(ROOT / "inputs")))
DATA.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class Params:
    h: float = 0.7
    omega_b0: float = 0.049
    omega_d0: float = 0.261
    omega_r0: float = 9.0e-5
    n_s: float = 0.965
    sigma8: float = 0.81
    box_mpc_h: float = 10.0
    a_init: float = 0.01
    seed: int = 20260812


P = Params()
OMEGA_M = P.omega_b0 + P.omega_d0
OMEGA_V = 1.0 - P.omega_r0 - OMEGA_M
RHO_BAR_H = 2.77536627e11 * OMEGA_M  # (Msun/h)/(Mpc/h)^3


def e2(a: np.ndarray | float) -> np.ndarray:
    aa = np.asarray(a, dtype=float)
    return P.omega_r0 * aa**-4 + OMEGA_M * aa**-3 + OMEGA_V


def dlnH_dN(a: float) -> float:
    E2 = float(e2(a))
    return -0.5 * (4.0 * P.omega_r0 * a**-4 + 3.0 * OMEGA_M * a**-3) / E2


def omega_m_a(a: float) -> float:
    return OMEGA_M * a**-3 / float(e2(a))


def build_growth(a_min: float = 1.0e-4, n: int = 5000) -> dict[str, object]:
    N = np.linspace(math.log(a_min), 0.0, n)
    ai = math.exp(N[0])

    def rhs(nn: float, y: np.ndarray) -> list[float]:
        a = math.exp(nn)
        return [
            float(y[1]),
            -(2.0 + dlnH_dN(a)) * float(y[1]) + 1.5 * omega_m_a(a) * float(y[0]),
        ]

    sol = solve_ivp(rhs, (N[0], 0.0), [ai, ai], t_eval=N, rtol=2e-11, atol=2e-13)
    if not sol.success:
        raise RuntimeError(sol.message)
    norm = float(sol.y[0, -1])
    D = sol.y[0] / norm
    DN = sol.y[1] / norm
    return {
        "N": N,
        "a": np.exp(N),
        "D": D,
        "DN": DN,
        "D_spline": CubicSpline(N, D),
        "DN_spline": CubicSpline(N, DN),
    }


def top_hat_window(x: np.ndarray) -> np.ndarray:
    xx = np.asarray(x, dtype=float)
    out = np.empty_like(xx)
    small = np.abs(xx) < 1e-3
    out[small] = 1.0 - xx[small] ** 2 / 10.0 + xx[small] ** 4 / 280.0
    z = xx[~small]
    out[~small] = 3.0 * (np.sin(z) - z * np.cos(z)) / z**3
    return out


def smooth_transfer_phys(k_mpc: np.ndarray) -> np.ndarray:
    q = np.asarray(k_mpc, dtype=float) / (OMEGA_M * P.h * P.h)
    return (
        np.log1p(2.34 * q)
        / (2.34 * q)
        * (1.0 + 3.89 * q + (16.1 * q) ** 2 + (5.46 * q) ** 3 + (6.71 * q) ** 4) ** (-0.25)
    )


def build_power_h() -> dict[str, object]:
    k_phys = np.geomspace(1e-6, 3000.0, 20000)
    shape = k_phys**P.n_s * smooth_transfer_phys(k_phys) ** 2
    radius = 8.0 / P.h
    W = top_hat_window(k_phys * radius)
    var_shape = np.trapezoid(k_phys**3 * shape * W**2 / (2 * math.pi**2), np.log(k_phys))
    amp = P.sigma8**2 / var_shape
    p_phys = amp * shape
    k_h = k_phys / P.h
    p_h = P.h**3 * p_phys
    Wh = top_hat_window(k_h * 8.0)
    sigma8_check = math.sqrt(float(np.trapezoid(k_h**3 * p_h * Wh**2 / (2 * math.pi**2), np.log(k_h))))
    return {
        "k_h": k_h,
        "p_h": p_h,
        "sigma8_check": sigma8_check,
        "log_interp": PchipInterpolator(np.log(k_h), np.log(p_h), extrapolate=True),
    }


class DarkTransfer:
    def __init__(self) -> None:
        tab = pd.read_csv(PARENT / "collisionless_dark_transfer_curve.csv")
        self.k_h = tab["k_per_Mpc_for_H0_70"].to_numpy(float) / P.h
        self.t = np.clip(tab["collisionless_transfer_amplitude_z0"].to_numpy(float), 1e-10, 1.0)
        self._interp = PchipInterpolator(np.log(self.k_h), np.log(self.t), extrapolate=True)
        self.tail_slope = float(np.polyfit(np.log(self.k_h[-6:]), np.log(self.t[-6:]), 1)[0])

    def __call__(self, k_h: np.ndarray | float) -> np.ndarray:
        kk = np.asarray(k_h, dtype=float)
        out = np.ones_like(kk)
        mid = (kk >= self.k_h[0]) & (kk <= self.k_h[-1])
        out[mid] = np.exp(self._interp(np.log(kk[mid])))
        high = kk > self.k_h[-1]
        out[high] = self.t[-1] * (kk[high] / self.k_h[-1]) ** self.tail_slope
        return np.clip(out, 1e-10, 1.0)


def spherical_collapse(a_coll: float = 1.0) -> dict[str, float]:
    ai = 1e-4
    Ni = math.log(ai)
    Nf = math.log(a_coll)

    def nonlinear_end(delta_i: float) -> tuple[float, float]:
        y0 = 1.0 - delta_i / 3.0
        yp0 = -delta_i / 3.0

        def rhs(N: float, yv: np.ndarray) -> list[float]:
            a = math.exp(N)
            y, yp = float(yv[0]), float(yv[1])
            source = 0.5 * omega_m_a(a) * (y**-3 - 1.0) * y
            return [yp, -(2.0 + dlnH_dN(a)) * yp - source]

        def event(N: float, yv: np.ndarray) -> float:
            return float(yv[0]) - 1e-3

        event.terminal = True  # type: ignore[attr-defined]
        event.direction = -1  # type: ignore[attr-defined]
        sol = solve_ivp(rhs, (Ni, Nf), [y0, yp0], events=event, rtol=2e-10, atol=2e-12, max_step=0.01)
        if len(sol.t_events[0]):
            return float(sol.t_events[0][0]), 1e-3
        return Nf, float(sol.y[0, -1])

    def collapse_time(delta_i: float) -> float:
        Nend, yend = nonlinear_end(delta_i)
        return Nend if yend <= 1.0001e-3 else Nf + yend - 1e-3

    lo, hi = 1e-5, 5e-3
    while collapse_time(lo) < Nf:
        lo *= 0.5
    while collapse_time(hi) > Nf:
        hi *= 2.0
        if hi > 0.1:
            raise RuntimeError("Could not bracket collapse")
    delta_i = brentq(lambda d: collapse_time(d) - Nf, lo, hi, xtol=1e-13, rtol=1e-11)

    def rhs_lin(N: float, y: np.ndarray) -> list[float]:
        a = math.exp(N)
        return [
            float(y[1]),
            -(2.0 + dlnH_dN(a)) * float(y[1]) + 1.5 * omega_m_a(a) * float(y[0]),
        ]

    lin = solve_ivp(rhs_lin, (Ni, Nf), [delta_i, delta_i], t_eval=[Nf], rtol=2e-11, atol=2e-13)
    return {"a_init": ai, "delta_init": delta_i, "delta_c": float(lin.y[0, -1])}


def _press_schechter(masses: np.ndarray, sigma: np.ndarray, delta_c: float) -> tuple[np.ndarray, np.ndarray]:
    lnM = np.log(masses)
    dlnsigma = np.gradient(np.log(sigma), lnM)
    nu = delta_c / sigma
    pref = math.sqrt(2.0 / math.pi) * RHO_BAR_H / masses
    hmf = pref * np.abs(dlnsigma) * nu * np.exp(-0.5 * nu**2)
    collapsed = erfc(nu / math.sqrt(2.0))
    return hmf, collapsed


def compute_excursion_set(power: dict[str, object], dark: DarkTransfer, delta_c: float) -> tuple[pd.DataFrame, dict[str, float]]:
    k = np.geomspace(1e-5, 3e4, 16000)
    p_cold = np.exp(power["log_interp"](np.log(k)))
    p_ref = p_cold * dark(k) ** 2
    lnk = np.log(k)
    masses = np.geomspace(1e5, 1e16, 480)
    radii = (3 * masses / (4 * math.pi * RHO_BAR_H)) ** (1 / 3)

    # Real-space top-hat variance.
    sig_tc = np.empty_like(masses)
    sig_tr = np.empty_like(masses)
    for i, R in enumerate(radii):
        W = top_hat_window(k * R)
        sig_tc[i] = math.sqrt(float(np.trapezoid(k**3 * p_cold * W**2 / (2 * math.pi**2), lnk)))
        sig_tr[i] = math.sqrt(float(np.trapezoid(k**3 * p_ref * W**2 / (2 * math.pi**2), lnk)))
    hmf_tc, fc_tc = _press_schechter(masses, sig_tc, delta_c)
    hmf_tr, fc_tr = _press_schechter(masses, sig_tr, delta_c)

    # Pi-sharp filter: k_c=pi/R. This uses the same radius convention as the half-mode mass.
    Ic = np.concatenate([[0.0], cumulative_trapezoid(k**3 * p_cold / (2 * math.pi**2), lnk)])
    Ir = np.concatenate([[0.0], cumulative_trapezoid(k**3 * p_ref / (2 * math.pi**2), lnk)])
    kc = math.pi / radii
    sig_sc = np.sqrt(np.interp(np.log(kc), lnk, Ic))
    sig_sr = np.sqrt(np.interp(np.log(kc), lnk, Ir))
    hmf_sc, fc_sc = _press_schechter(masses, sig_sc, delta_c)
    hmf_sr, fc_sr = _press_schechter(masses, sig_sr, delta_c)

    ratio_t = np.divide(hmf_tr, hmf_tc, out=np.zeros_like(hmf_tr), where=hmf_tc > 0)
    ratio_s = np.divide(hmf_sr, hmf_sc, out=np.zeros_like(hmf_sr), where=hmf_sc > 0)

    tab = pd.read_csv(PARENT / "collisionless_dark_transfer_curve.csv")
    kh = tab["k_per_Mpc_for_H0_70"].to_numpy(float) / P.h
    pr = tab["collisionless_power_ratio_z0"].to_numpy(float)
    order = np.argsort(pr)
    k_half = float(np.interp(0.5, pr[order], kh[order]))
    R_half = math.pi / k_half
    M_half = 4 * math.pi / 3 * RHO_BAR_H * R_half**3

    def crossing(ratio: np.ndarray, target: float) -> float:
        idx = np.where(ratio >= target)[0]
        if len(idx) == 0:
            return float("nan")
        j = int(idx[0])
        if j == 0:
            return float(masses[0])
        return float(math.exp(np.interp(target, ratio[j - 1 : j + 1], np.log(masses[j - 1 : j + 1]))))

    def at_mass(arr: np.ndarray, mass: float) -> float:
        return float(np.interp(math.log(mass), np.log(masses), arr))

    out = pd.DataFrame(
        {
            "mass_msun_h": masses,
            "radius_mpc_h": radii,
            "sigma_tophat_cold": sig_tc,
            "sigma_tophat_refinement": sig_tr,
            "sigma_pisharp_cold": sig_sc,
            "sigma_pisharp_refinement": sig_sr,
            "collapsed_tophat_cold": fc_tc,
            "collapsed_tophat_refinement": fc_tr,
            "collapsed_pisharp_cold": fc_sc,
            "collapsed_pisharp_refinement": fc_sr,
            "dn_dlnM_tophat_cold": hmf_tc,
            "dn_dlnM_tophat_refinement": hmf_tr,
            "dn_dlnM_pisharp_cold": hmf_sc,
            "dn_dlnM_pisharp_refinement": hmf_sr,
            "halo_ratio_tophat": ratio_t,
            "halo_ratio_pisharp": ratio_s,
        }
    )
    summary = {
        "k_half_power_h_mpc": k_half,
        "half_mode_mass_msun_h": M_half,
        "tophat_ratio_half_mass": at_mass(ratio_t, M_half),
        "pisharp_ratio_half_mass": at_mass(ratio_s, M_half),
        "tophat_half_abundance_mass_msun_h": crossing(ratio_t, 0.5),
        "pisharp_half_abundance_mass_msun_h": crossing(ratio_s, 0.5),
        "tophat_tenth_abundance_mass_msun_h": crossing(ratio_t, 0.1),
        "pisharp_tenth_abundance_mass_msun_h": crossing(ratio_s, 0.1),
        "pisharp_ratio_1e8": at_mass(ratio_s, 1e8),
        "pisharp_ratio_1e10": at_mass(ratio_s, 1e10),
        "pisharp_ratio_1e11": at_mass(ratio_s, 1e11),
    }
    return out, summary


def phase_space_bound(eta: float = 1.0, lambda_over_A: float = 1e-4) -> dict[str, float]:
    coeff = 24.0 / ((2 * math.pi) ** 1.5 * math.pi**5)
    q_A4 = coeff * eta / lambda_over_A
    mpeak_A = 5.0 / (2 * math.pi)
    q_m4 = q_A4 / mpeak_A**4
    # Conversion: 1 eV^4 / c^3 = 1.2722722677e-13 [Msun pc^-3 (km/s)^-3].
    q_astro_1kev = q_m4 * (1e3**4) * 1.2722722677338836e-13
    G_pc = 4.30091e-3  # pc (km/s)^2 / Msun
    rc_pc_1kev_10 = math.sqrt(9.0 / (4 * math.pi * G_pc * q_astro_1kev * 10.0))
    return {
        "Qmax_over_A4": q_A4,
        "Qmax_over_mpeak4": q_m4,
        "mpeak_over_A": mpeak_A,
        "Qmax_astro_for_mpeak_1keV": q_astro_1kev,
        "minimum_isothermal_core_pc_for_1keV_sigma10": rc_pc_1kev_10,
    }


@njit(cache=True)
def cic_deposit(pos: np.ndarray, n: int, box: float) -> np.ndarray:
    grid = np.zeros(n * n * n, dtype=np.float64)
    scale = n / box
    for p in range(pos.shape[0]):
        ux, uy, uz = pos[p, 0] * scale, pos[p, 1] * scale, pos[p, 2] * scale
        bx, by, bz = math.floor(ux), math.floor(uy), math.floor(uz)
        ix, iy, iz = int(bx) % n, int(by) % n, int(bz) % n
        fx, fy, fz = ux - bx, uy - by, uz - bz
        for dx in range(2):
            wx = fx if dx else 1.0 - fx
            jx = (ix + dx) % n
            for dy in range(2):
                wy = fy if dy else 1.0 - fy
                jy = (iy + dy) % n
                for dz in range(2):
                    wz = fz if dz else 1.0 - fz
                    jz = (iz + dz) % n
                    grid[(jx * n + jy) * n + jz] += wx * wy * wz
    return grid.reshape((n, n, n))


@njit(cache=True)
def cic_interpolate(pos: np.ndarray, fields: np.ndarray, box: float) -> np.ndarray:
    n = fields.shape[1]
    out = np.zeros((pos.shape[0], fields.shape[0]), dtype=np.float64)
    scale = n / box
    for p in range(pos.shape[0]):
        ux, uy, uz = pos[p, 0] * scale, pos[p, 1] * scale, pos[p, 2] * scale
        bx, by, bz = math.floor(ux), math.floor(uy), math.floor(uz)
        ix, iy, iz = int(bx) % n, int(by) % n, int(bz) % n
        fx, fy, fz = ux - bx, uy - by, uz - bz
        for dx in range(2):
            wx = fx if dx else 1.0 - fx
            jx = (ix + dx) % n
            for dy in range(2):
                wy = fy if dy else 1.0 - fy
                jy = (iy + dy) % n
                for dz in range(2):
                    wz = fz if dz else 1.0 - fz
                    jz = (iz + dz) % n
                    w = wx * wy * wz
                    for c in range(fields.shape[0]):
                        out[p, c] += w * fields[c, jx, jy, jz]
    return out


def k_arrays(n: int, box: float) -> tuple[np.ndarray, ...]:
    dx = box / n
    kv = 2 * math.pi * np.fft.fftfreq(n, d=dx)
    kx, ky, kz = np.meshgrid(kv, kv, kv, indexing="ij")
    kmag = np.sqrt(kx * kx + ky * ky + kz * kz)
    lap = (2 * np.sin(0.5 * kx * dx) / dx) ** 2 + (2 * np.sin(0.5 * ky * dx) / dx) ** 2 + (2 * np.sin(0.5 * kz * dx) / dx) ** 2
    return kmag, lap, np.sin(kx * dx) / dx, np.sin(ky * dx) / dx, np.sin(kz * dx) / dx


def force_base(pos: np.ndarray, n: int, box: float, symbols: tuple[np.ndarray, ...]) -> tuple[np.ndarray, np.ndarray]:
    counts = cic_deposit(pos, n, box)
    delta = counts / (pos.shape[0] / n**3) - 1.0
    dk = np.fft.fftn(delta)
    _, lap, gx, gy, gz = symbols
    inv = np.zeros_like(lap)
    inv[lap > 0] = 1.0 / lap[lap > 0]
    fields = np.stack(
        [
            np.fft.ifftn(1j * gx * inv * dk).real,
            np.fft.ifftn(1j * gy * inv * dk).real,
            np.fft.ifftn(1j * gz * inv * dk).real,
        ]
    )
    return cic_interpolate(pos, fields, box), delta


def gauss_integral(a0: float, a1: float, power_a: int) -> float:
    x, w = np.polynomial.legendre.leggauss(10)
    a = 0.5 * (a1 - a0) * x + 0.5 * (a1 + a0)
    return float(0.5 * (a1 - a0) * np.sum(w / (a**power_a * np.sqrt(e2(a)))))


def generate_initial_conditions(n: int, box: float, refinement: bool, sign: float) -> tuple[np.ndarray, np.ndarray, dict[str, float]]:
    growth = build_growth()
    power = build_power_h()
    dark = DarkTransfer()
    rng = np.random.default_rng(P.seed)
    white = rng.normal(size=(n, n, n))
    wk = np.fft.fftn(white)
    phase = np.divide(wk, np.abs(wk), out=np.zeros_like(wk), where=np.abs(wk) > 0)
    kmag, _, _, _, _ = k_arrays(n, box)
    kclip = np.maximum(kmag, 1e-8)
    pk = np.exp(power["log_interp"](np.log(kclip)))
    if refinement:
        pk *= dark(kclip) ** 2
    amp = np.sqrt(n**6 * pk / box**3)
    delta0 = sign * phase * amp
    delta0[0, 0, 0] = 0.0
    kv = 2 * math.pi * np.fft.fftfreq(n, d=box / n)
    kx, ky, kz = np.meshgrid(kv, kv, kv, indexing="ij")
    k2 = kx * kx + ky * ky + kz * kz
    invk2 = np.zeros_like(k2)
    invk2[k2 > 0] = 1.0 / k2[k2 > 0]
    s = np.stack(
        [
            np.fft.ifftn(1j * kx * invk2 * delta0).real,
            np.fft.ifftn(1j * ky * invk2 * delta0).real,
            np.fft.ifftn(1j * kz * invk2 * delta0).real,
        ],
        axis=-1,
    ).reshape((-1, 3))
    dx = box / n
    coords = (np.arange(n) + 0.5) * dx
    qx, qy, qz = np.meshgrid(coords, coords, coords, indexing="ij")
    q = np.stack([qx, qy, qz], axis=-1).reshape((-1, 3))
    N = math.log(P.a_init)
    D = float(growth["D_spline"](N))
    DN = float(growth["DN_spline"](N))
    E = math.sqrt(float(e2(P.a_init)))
    pos = (q + D * s) % box
    mom = P.a_init**2 * E * DN * s
    return pos, mom, {
        "D_init": D,
        "DN_init": DN,
        "max_displacement_cell": float(np.max(np.linalg.norm(D * s, axis=1)) / dx),
        "rms_delta_linear_init": float(np.std(np.fft.ifftn(D * delta0).real)),
    }


def power_spectrum_full(pos: np.ndarray, n: int, box: float, nbins: int = 28) -> pd.DataFrame:
    counts = cic_deposit(pos, n, box)
    delta = counts / (pos.shape[0] / n**3) - 1.0
    dk = np.fft.fftn(delta)
    raw = (dk * np.conj(dk)).real * box**3 / n**6
    kmag, _, _, _, _ = k_arrays(n, box)
    dx = box / n
    kv = 2 * math.pi * np.fft.fftfreq(n, d=dx)
    kx, ky, kz = np.meshgrid(kv, kv, kv, indexing="ij")

    def sinc(x: np.ndarray) -> np.ndarray:
        return np.sinc(x / math.pi)

    W = (sinc(0.5 * kx * dx) * sinc(0.5 * ky * dx) * sinc(0.5 * kz * dx)) ** 2
    raw = np.divide(raw, W**2, out=np.zeros_like(raw), where=W > 0.05)
    valid = (kmag > 0) & (kmag < 0.72 * math.pi / dx) & (W > 0.05)
    edges = np.geomspace(2 * math.pi / box, 0.7 * math.pi / dx, nbins + 1)
    ids = np.digitize(kmag.ravel(), edges) - 1
    rows: list[tuple[float, float, float, int]] = []
    for i in range(nbins):
        mask = valid.ravel() & (ids == i)
        if np.count_nonzero(mask) < 8:
            continue
        kval = kmag.ravel()[mask]
        pval = raw.ravel()[mask]
        k = float(np.exp(np.mean(np.log(kval))))
        p = float(np.mean(pval))
        rows.append((k, p, k**3 * p / (2 * math.pi**2), int(np.count_nonzero(mask))))
    return pd.DataFrame(rows, columns=["k_h_mpc", "P_full_mpc_h3", "Delta2", "modes"])


def density_pdf(delta: np.ndarray) -> dict[str, float]:
    rho = np.maximum(1 + delta, 1e-8)
    return {
        "rho_p50": float(np.percentile(rho, 50)),
        "rho_p90": float(np.percentile(rho, 90)),
        "rho_p99": float(np.percentile(rho, 99)),
        "rho_p999": float(np.percentile(rho, 99.9)),
        "volume_fraction_rho_gt_10": float(np.mean(rho > 10)),
        "volume_fraction_rho_gt_50": float(np.mean(rho > 50)),
    }


def run_pm_case(case: str, nmesh: int, steps: int, tag: str) -> dict[str, object]:
    refinement = case.startswith("refinement")
    sign = 1.0 if case.endswith("plus") else -1.0
    pos, mom, init = generate_initial_conditions(nmesh, P.box_mpc_h, refinement, sign)
    symbols = k_arrays(nmesh, P.box_mpc_h)
    a_edges = np.geomspace(P.a_init, 1.0, steps + 1)
    force, delta = force_base(pos, nmesh, P.box_mpc_h, symbols)
    outputs: dict[str, pd.DataFrame] = {str(P.a_init): power_spectrum_full(pos, nmesh, P.box_mpc_h)}
    targets = [0.1, 0.3, 0.5, 1.0]
    ti = 0
    max_drift = 0.0
    start = time.time()
    for j in range(steps):
        a0, a1 = float(a_edges[j]), float(a_edges[j + 1])
        amid = math.sqrt(a0 * a1)
        mom += 1.5 * OMEGA_M * gauss_integral(a0, amid, 2) * force
        drift = mom * gauss_integral(a0, a1, 3)
        pos = (pos + drift) % P.box_mpc_h
        max_drift = max(max_drift, float(np.max(np.linalg.norm(drift, axis=1)) / (P.box_mpc_h / nmesh)))
        force, delta = force_base(pos, nmesh, P.box_mpc_h, symbols)
        mom += 1.5 * OMEGA_M * gauss_integral(amid, a1, 2) * force
        while ti < len(targets) and a1 >= targets[ti] - 1e-12:
            outputs[str(targets[ti])] = power_spectrum_full(pos, nmesh, P.box_mpc_h)
            ti += 1
    suffix = f"_{tag}" if tag else ""
    table = pd.concat([df.assign(a=float(a)) for a, df in outputs.items()], ignore_index=True)
    table.to_csv(DATA / f"pm_case_{case}{suffix}.csv", index=False)
    metrics = {
        "case": case,
        "nmesh": nmesh,
        "steps": steps,
        "runtime_seconds": time.time() - start,
        "max_step_drift_cell": max_drift,
        "init": init,
        "pdf": density_pdf(delta),
    }
    (DATA / f"pm_case_{case}{suffix}.json").write_text(json.dumps(metrics, indent=2))
    return metrics


def aggregate_pm(tag: str) -> dict[str, object]:
    suffix = f"_{tag}" if tag else ""
    cases = ["cold_plus", "cold_minus", "refinement_plus", "refinement_minus"]
    tabs = {c: pd.read_csv(DATA / f"pm_case_{c}{suffix}.csv") for c in cases}
    rows: list[tuple[float, float, float, float, float]] = []
    for a in [P.a_init, 0.1, 0.3, 0.5, 1.0]:
        cp, cm, rp, rm = [tabs[c][tabs[c].a == a].reset_index(drop=True) for c in cases]
        n = min(len(cp), len(cm), len(rp), len(rm))
        cp, cm, rp, rm = cp.iloc[:n], cm.iloc[:n], rp.iloc[:n], rm.iloc[:n]
        cold = 0.5 * (cp.P_full_mpc_h3.to_numpy() + cm.P_full_mpc_h3.to_numpy())
        ref = 0.5 * (rp.P_full_mpc_h3.to_numpy() + rm.P_full_mpc_h3.to_numpy())
        for k, pc, pr in zip(cp.k_h_mpc, cold, ref):
            rows.append((a, k, pc, pr, pr / pc if pc > 0 else np.nan))
    out = pd.DataFrame(rows, columns=["a", "k_h_mpc", "P_cold", "P_refinement", "nonlinear_power_ratio"])
    out.to_csv(DATA / f"paired_pm_power{suffix}.csv", index=False)

    metrics = [json.loads((DATA / f"pm_case_{c}{suffix}.json").read_text()) for c in cases]
    pdfrows = []
    for model in ["cold", "refinement"]:
        vals = [json.loads((DATA / f"pm_case_{model}_{s}{suffix}.json").read_text()) for s in ["plus", "minus"]]
        row: dict[str, float | str] = {"model": model}
        for k in vals[0]["pdf"]:
            row[k] = 0.5 * (vals[0]["pdf"][k] + vals[1]["pdf"][k])
        pdfrows.append(row)
    pd.DataFrame(pdfrows).to_csv(DATA / f"paired_pm_density_pdf{suffix}.csv", index=False)
    summary = {
        "tag": tag,
        "nmesh": int(metrics[0]["nmesh"]),
        "particles": int(metrics[0]["nmesh"]) ** 3,
        "box_mpc_h": P.box_mpc_h,
        "steps": int(metrics[0]["steps"]),
        "runtime_seconds_total": sum(float(x["runtime_seconds"]) for x in metrics),
        "max_step_drift_cell": max(float(x["max_step_drift_cell"]) for x in metrics),
        "init_max_displacement_cell": max(float(x["init"]["max_displacement_cell"]) for x in metrics),
        "init_rms_delta": max(float(x["init"]["rms_delta_linear_init"]) for x in metrics),
    }
    (DATA / f"paired_pm_summary{suffix}.json").write_text(json.dumps(summary, indent=2))
    return summary


def interpolate_ratio(df: pd.DataFrame, a: float, k: float) -> float:
    z = df[df.a == a]
    return float(np.interp(k, z.k_h_mpc, z.nonlinear_power_ratio))


def audit() -> dict[str, object]:
    power = build_power_h()
    dark = DarkTransfer()
    collapse = spherical_collapse()
    excursion, ex = compute_excursion_set(power, dark, collapse["delta_c"])
    excursion.to_csv(DATA / "nonlinear_excursion_set_halos.csv", index=False)
    phase = phase_space_bound()

    main = pd.read_csv(DATA / "paired_pm_power_main.csv")
    n48 = pd.read_csv(DATA / "paired_pm_power_n48.csv")
    t100 = pd.read_csv(DATA / "paired_pm_power_n48t100.csv")
    main_summary = json.loads((DATA / "paired_pm_summary_main.json").read_text())
    pdf = pd.read_csv(DATA / "paired_pm_density_pdf_main.csv")

    k_half = ex["k_half_power_h_mpc"]
    r_init = interpolate_ratio(main, P.a_init, k_half)
    r_01 = interpolate_ratio(main, 0.1, k_half)
    r_03 = interpolate_ratio(main, 0.3, k_half)
    r_1 = interpolate_ratio(main, 1.0, k_half)
    refill = 1.0 - (1.0 - r_1) / (1.0 - r_init)

    # Spatial and temporal convergence in the resolved band 1<=k<=8 h/Mpc.
    def discrepancy(A: pd.DataFrame, B: pd.DataFrame) -> float:
        vals = []
        for a in [0.1, 0.3, 0.5, 1.0]:
            x = A[A.a == a]
            y = B[B.a == a]
            mask = (x.k_h_mpc >= 1.0) & (x.k_h_mpc <= 8.0)
            interp = np.interp(x.k_h_mpc[mask], y.k_h_mpc, y.nonlinear_power_ratio)
            vals.extend(np.abs(x.nonlinear_power_ratio[mask].to_numpy() - interp))
        return float(np.nanmax(vals))

    spatial = discrepancy(main, n48)
    temporal = discrepancy(n48, t100)

    # Paired linear-growth check from a_i to 0.1 on modes below 2 h/Mpc.
    cp = pd.read_csv(DATA / "pm_case_cold_plus_main.csv")
    cm = pd.read_csv(DATA / "pm_case_cold_minus_main.csv")
    p0 = 0.5 * (cp[cp.a == P.a_init].P_full_mpc_h3.to_numpy() + cm[cm.a == P.a_init].P_full_mpc_h3.to_numpy())
    p1 = 0.5 * (cp[cp.a == 0.1].P_full_mpc_h3.to_numpy() + cm[cm.a == 0.1].P_full_mpc_h3.to_numpy())
    k = cp[cp.a == 0.1].k_h_mpc.to_numpy()
    growth = build_growth()
    linear = (float(growth["D_spline"](math.log(0.1))) / float(growth["D_spline"](math.log(P.a_init)))) ** 2
    m = k < 2.0
    growth_mean_error = abs(float(np.mean(p1[m] / p0[m])) / linear - 1.0)

    cold_pdf = pdf[pdf.model == "cold"].iloc[0]
    ref_pdf = pdf[pdf.model == "refinement"].iloc[0]
    dense10_ratio = float(ref_pdf.volume_fraction_rho_gt_10 / cold_pdf.volume_fraction_rho_gt_10)
    dense50_ratio = float(ref_pdf.volume_fraction_rho_gt_50 / cold_pdf.volume_fraction_rho_gt_50)

    checks: list[dict[str, object]] = []

    def ck(cid: str, statement: str, value: float, tolerance: float, kind: str = "abs") -> None:
        if kind == "abs":
            passed = abs(value) <= tolerance
        elif kind == "max":
            passed = value <= tolerance
        else:
            passed = value >= tolerance
        checks.append({"id": cid, "statement": statement, "value": value, "tolerance": tolerance, "kind": kind, "status": "PASS" if passed else "FAIL"})

    ck("NLS01", "sigma8 normalization", float(power["sigma8_check"]) - P.sigma8, 2e-8)
    ck("NLS02", "spherical-collapse threshold", collapse["delta_c"] - 1.675, 0.02)
    ck("NLS03", "variance ordering, top-hat", float(np.max(excursion.sigma_tophat_refinement - excursion.sigma_tophat_cold)), 1e-10, "max")
    ck("NLS04", "variance ordering, pi-sharp", float(np.max(excursion.sigma_pisharp_refinement - excursion.sigma_pisharp_cold)), 1e-10, "max")
    ck("NLS05", "collapsed-fraction ordering, top-hat", float(np.max(excursion.collapsed_tophat_refinement - excursion.collapsed_tophat_cold)), 1e-10, "max")
    ck("NLS06", "collapsed-fraction ordering, pi-sharp", float(np.max(excursion.collapsed_pisharp_refinement - excursion.collapsed_pisharp_cold)), 1e-10, "max")
    ck("NLS07", "finite half-mode mass", ex["half_mode_mass_msun_h"], 1e8, "min")
    ck("NLS08", "positive phase-space coefficient", phase["Qmax_over_A4"], 1e-6, "min")
    ck("NLS09", "initial Zel'dovich displacement below 0.6 cell", 0.6 - main_summary["init_max_displacement_cell"], 0.0, "min")
    ck("NLS10", "maximum main step drift below 1.75 cell", 1.75 - main_summary["max_step_drift_cell"], 0.0, "min")
    ck("NLS11", "paired early linear growth mean", growth_mean_error, 0.04)
    ck("NLS12", "spatial-control discrepancy", spatial, 0.035)
    ck("NLS13", "time-step-control discrepancy", temporal, 0.002)
    ck("NLS14", "initial half-mode ratio agrees with one-half", r_init - 0.5, 0.04)
    ck("NLS15", "nonlinear half-mode remains below cold", r_1 - 1.0, 0.02, "max")
    ck("NLS16", "nonlinear mode coupling refills at least 90 percent", refill, 0.9, "min")
    ck("NLS17", "dense-volume ratio above 10 is bounded", dense10_ratio - 1.05, 0.0, "max")
    ck("NLS18", "dense-volume ratio above 50 is bounded", dense50_ratio - 1.05, 0.0, "max")
    check_df = pd.DataFrame(checks)
    check_df.to_csv(DATA / "nonlinear_structure_checks.csv", index=False)

    result = {
        "parameters": asdict(P),
        "omega_m0": OMEGA_M,
        "omega_v0": OMEGA_V,
        "sigma8_check": float(power["sigma8_check"]),
        "spherical_collapse": collapse,
        "excursion_summary": ex,
        "phase_space": phase,
        "pm_main": main_summary,
        "pm_spatial_max_discrepancy": spatial,
        "pm_timestep_max_discrepancy": temporal,
        "pm_growth_mean_relative_error": growth_mean_error,
        "pm_half_mode_ratios": {"a_init": r_init, "a_0p1": r_01, "a_0p3": r_03, "a_1": r_1, "suppression_refilled_fraction": refill},
        "density_pdf_ratios": {"rho_gt_10": dense10_ratio, "rho_gt_50": dense50_ratio},
        "pass_count": int((check_df.status == "PASS").sum()),
        "fail_count": int((check_df.status == "FAIL").sum()),
        "dark_transfer_tail_slope": dark.tail_slope,
    }
    (DATA / "Nonlinear_Refinement_Structure_Verification.json").write_text(json.dumps(result, indent=2))
    return result
