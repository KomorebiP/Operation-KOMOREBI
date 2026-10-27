from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import json
import math

import numpy as np
import pandas as pd
from scipy.integrate import cumulative_trapezoid, solve_ivp
from scipy.interpolate import CubicSpline, PchipInterpolator
from scipy.ndimage import map_coordinates
from scipy.signal import find_peaks
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
    t_cmb: float = 2.7255
    z_rec: float = 1084.47305577
    chi_rec_h0inv: float = 3.1335298685
    box_deg: float = 20.0
    grid_n: int = 512
    realizations: int = 48
    seed: int = 20260812


P = Params()
OMEGA_M = P.omega_b0 + P.omega_d0
OMEGA_V = 1.0 - P.omega_r0 - OMEGA_M
H0_OVER_C_MPC = P.h0_km_s_mpc / 299792.458
H = P.h0_km_s_mpc / 100.0
TCMB_UK = P.t_cmb * 1.0e6


def e2(a: np.ndarray | float) -> np.ndarray:
    aa = np.asarray(a, dtype=float)
    return P.omega_r0 * aa**-4 + OMEGA_M * aa**-3 + OMEGA_V


def build_background(npts: int = 5000) -> dict[str, np.ndarray | float]:
    n0 = math.log(1.0 / (1.0 + P.z_rec))
    N = np.linspace(n0, 0.0, npts)
    a = np.exp(N)
    E = np.sqrt(e2(a))
    Hc = a * E
    eta = np.concatenate([[0.0], cumulative_trapezoid(1.0 / Hc, N)])
    chi_dim = eta[-1] - eta
    # Match the effective recombination shell used by the parent calculation.
    chi_dim *= P.chi_rec_h0inv / chi_dim[0]
    chi_mpc = chi_dim / H0_OVER_C_MPC

    def rhs(n: float, y: np.ndarray) -> list[float]:
        aa = math.exp(n)
        E2 = float(e2(aa))
        dlnH = -0.5 * (
            4.0 * P.omega_r0 * aa**-4 + 3.0 * OMEGA_M * aa**-3
        ) / E2
        om = OMEGA_M * aa**-3 / E2
        return [float(y[1]), -(2.0 + dlnH) * float(y[1]) + 1.5 * om * float(y[0])]

    ai = math.exp(n0)
    sol = solve_ivp(
        rhs,
        (n0, 0.0),
        [ai, ai],
        t_eval=N,
        rtol=2.0e-11,
        atol=2.0e-13,
    )
    if not sol.success:
        raise RuntimeError(sol.message)
    growth = sol.y[0] / sol.y[0, -1]
    return {
        "N": N,
        "a": a,
        "E": E,
        "chi_mpc": chi_mpc,
        "growth": growth,
        "chi_star_mpc": float(chi_mpc[0]),
    }


def top_hat_window(x: np.ndarray) -> np.ndarray:
    xx = np.asarray(x, dtype=float)
    out = np.empty_like(xx)
    small = np.abs(xx) < 1.0e-3
    out[small] = 1.0 - xx[small] ** 2 / 10.0
    xs = xx[~small]
    out[~small] = 3.0 * (np.sin(xs) - xs * np.cos(xs)) / xs**3
    return out


def smooth_transfer(k: np.ndarray) -> np.ndarray:
    # Declared BBKS-like smooth baseline. It is a controlled shape model,
    # not a precision baryon-wiggle transfer function.
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


def build_matter_power() -> dict[str, np.ndarray | float | PchipInterpolator]:
    k = np.geomspace(1.0e-5, 100.0, 7000)
    shape = k**P.n_s * smooth_transfer(k) ** 2
    radius = 8.0 / H
    window = top_hat_window(k * radius)
    variance_shape = np.trapezoid(
        k**3 * shape * window**2 / (2.0 * math.pi**2), np.log(k)
    )
    amplitude = P.sigma8**2 / variance_shape
    p0 = amplitude * shape
    sigma8_check = math.sqrt(
        float(
            np.trapezoid(
                k**3 * p0 * window**2 / (2.0 * math.pi**2), np.log(k)
            )
        )
    )
    return {
        "k": k,
        "p0": p0,
        "amplitude": amplitude,
        "sigma8_check": sigma8_check,
        "interp": PchipInterpolator(np.log(k), np.log(p0), extrapolate=True),
    }


class DarkTransfer:
    def __init__(self) -> None:
        tab = pd.read_csv(PARENT / "collisionless_dark_transfer_curve.csv")
        self.k = tab["k_per_Mpc_for_H0_70"].to_numpy(float)
        self.t = np.clip(
            tab["collisionless_transfer_amplitude_z0"].to_numpy(float),
            1.0e-8,
            1.0,
        )
        self._interp = PchipInterpolator(
            np.log(self.k), np.log(self.t), extrapolate=True
        )
        tail = slice(-6, None)
        self._tail_slope = float(
            np.polyfit(np.log(self.k[tail]), np.log(self.t[tail]), 1)[0]
        )

    def __call__(self, k: np.ndarray | float) -> np.ndarray:
        kk = np.asarray(k, dtype=float)
        out = np.ones_like(kk)
        inside = (kk >= self.k[0]) & (kk <= self.k[-1])
        out[inside] = np.exp(self._interp(np.log(kk[inside])))
        high = kk > self.k[-1]
        out[high] = self.t[-1] * (kk[high] / self.k[-1]) ** self._tail_slope
        return np.clip(out, 1.0e-8, 1.0)


def lensing_potential(
    background: dict[str, np.ndarray | float],
    matter: dict[str, np.ndarray | float | PchipInterpolator],
    dark_transfer: DarkTransfer,
    n_l: int = 650,
) -> pd.DataFrame:
    ell = np.unique(
        np.concatenate(
            [
                np.arange(2, 101, 2),
                np.arange(105, 1001, 5),
                np.arange(1010, 3001, 10),
                np.arange(3025, 6001, 25),
            ]
        )
    ).astype(float)
    if len(ell) > n_l:
        ids = np.unique(np.round(np.linspace(0, len(ell) - 1, n_l)).astype(int))
        ell = ell[ids]

    chi = np.asarray(background["chi_mpc"], dtype=float)
    a = np.asarray(background["a"], dtype=float)
    growth = np.asarray(background["growth"], dtype=float)
    chi_star = float(background["chi_star_mpc"])
    mask = (chi > 1.0) & (chi < chi_star - 1.0)
    chi = chi[mask][::-1]
    a = a[mask][::-1]
    growth = growth[mask][::-1]
    p_interp = matter["interp"]

    cold = np.empty_like(ell)
    dark = np.empty_like(ell)
    for i, L in enumerate(ell):
        kval = (L + 0.5) / chi
        kclip = np.clip(kval, 1.0e-5, 100.0)
        pz = np.exp(p_interp(np.log(kclip))) * growth**2
        kernel = (
            1.5
            * OMEGA_M
            * H0_OVER_C_MPC**2
            * a**-1
            * chi
            * (chi_star - chi)
            / chi_star
        )
        base = kernel**2 / chi**2 * pz
        cold[i] = np.trapezoid(base, chi)
        dark[i] = np.trapezoid(base * dark_transfer(kval) ** 2, chi)

    cphi = 4.0 * cold / (ell**2 * (ell + 1.0) ** 2)
    cphi_dark = 4.0 * dark / (ell**2 * (ell + 1.0) ** 2)
    out = pd.DataFrame(
        {
            "L": ell.astype(int),
            "C_kappa_kappa_cold": cold,
            "C_kappa_kappa_refinement": dark,
            "C_phi_phi_cold": cphi,
            "C_phi_phi_refinement": cphi_dark,
            "refinement_to_cold_ratio": dark / cold,
        }
    )
    return out


class PrimarySpectra:
    def __init__(self) -> None:
        tab = pd.read_csv(PARENT / "thermal_reionization_los_spectra.csv")
        ell = tab["ell"].to_numpy(float)
        self.ell_max_parent = float(ell[-1])
        self._tt = PchipInterpolator(
            ell, np.log(np.maximum(tab["C_TT"].to_numpy(float), 1.0e-40)), extrapolate=True
        )
        self._ee = PchipInterpolator(
            ell, np.log(np.maximum(tab["C_EE"].to_numpy(float), 1.0e-40)), extrapolate=True
        )
        self._te = CubicSpline(ell, tab["C_TE"].to_numpy(float), bc_type="natural", extrapolate=True)

    def __call__(self, ell: np.ndarray | float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        ll = np.asarray(ell, dtype=float)
        valid = (ll >= 2.0) & (ll <= 3300.0)
        clipped = np.clip(ll, 2.0, self.ell_max_parent)
        tt = np.zeros_like(ll)
        ee = np.zeros_like(ll)
        te = np.zeros_like(ll)
        tt[valid] = np.exp(self._tt(clipped[valid]))
        ee[valid] = np.exp(self._ee(clipped[valid]))
        te[valid] = self._te(clipped[valid])
        high = valid & (ll > self.ell_max_parent)
        if np.any(high):
            damping = np.exp(-(ll[high] - self.ell_max_parent) / 120.0)
            tt[high] *= damping
            ee[high] *= damping
            te[high] *= damping
        bound = np.sqrt(tt * ee)
        te = np.clip(te, -bound, bound)
        return tt, ee, te


class PhiSpectrum:
    def __init__(self, table: pd.DataFrame, column: str) -> None:
        ell = table["L"].to_numpy(float)
        vals = np.maximum(table[column].to_numpy(float), 1.0e-80)
        self._interp = PchipInterpolator(np.log(ell), np.log(vals), extrapolate=True)
        self.lo = float(ell[0])
        self.hi = float(ell[-1])

    def __call__(self, ell: np.ndarray | float) -> np.ndarray:
        ll = np.asarray(ell, dtype=float)
        out = np.zeros_like(ll)
        mask = (ll >= self.lo) & (ll <= self.hi)
        out[mask] = np.exp(self._interp(np.log(ll[mask])))
        return out


def binned_mean(values: np.ndarray, bins: np.ndarray, index: np.ndarray, valid: np.ndarray) -> np.ndarray:
    counts = np.bincount(index[valid], minlength=len(bins) - 1)
    sums = np.bincount(
        index[valid], weights=values.ravel()[valid], minlength=len(bins) - 1
    )
    return sums / np.maximum(counts, 1)


def simulate_remapping(
    primary: PrimarySpectra,
    phi_cold: PhiSpectrum,
    phi_dark: PhiSpectrum,
    *,
    n: int,
    realizations: int,
    seed: int,
    snapshot_at: int | None = None,
) -> dict[str, object]:
    box = math.radians(P.box_deg)
    dx = box / n
    area = box**2
    freq = 2.0 * math.pi * np.fft.fftfreq(n, d=dx)
    lx, ly = np.meshgrid(freq, freq, indexing="ij")
    lm = np.hypot(lx, ly)
    angle = np.arctan2(ly, lx)
    c2 = np.cos(2.0 * angle)
    s2 = np.sin(2.0 * angle)

    ctt, cee, cte = primary(lm)
    corr = np.zeros_like(lm)
    nz = ctt * cee > 0.0
    corr[nz] = cte[nz] / np.sqrt(ctt[nz] * cee[nz])
    corr = np.clip(corr, -1.0, 1.0)
    cpp = phi_cold(lm)
    cpp_dark = phi_dark(lm)

    bins = np.arange(20.0, 2601.0, 25.0)
    centers = 0.5 * (bins[:-1] + bins[1:])
    index = np.digitize(lm.ravel(), bins) - 1
    valid = (index >= 0) & (index < len(centers))
    counts = np.bincount(index[valid], minlength=len(centers))

    theory = {
        "TT": binned_mean(ctt, bins, index, valid),
        "EE": binned_mean(cee, bins, index, valid),
        "TE": binned_mean(cte, bins, index, valid),
    }
    keys = [
        "uTT", "uEE", "uTE",
        "cTT", "cEE", "cTE", "cBB",
        "dTT", "dEE", "dTE", "dBB",
    ]
    accum = {key: np.zeros(len(centers)) for key in keys}
    snapshot: dict[str, np.ndarray] | None = None
    alpha_cold: list[float] = []
    alpha_dark: list[float] = []
    rng = np.random.default_rng(seed)
    coords = np.indices((n, n), dtype=float)
    power_norm = dx**2 / n**2

    def bin_power(array: np.ndarray) -> np.ndarray:
        sums = np.bincount(
            index[valid], weights=array.ravel()[valid], minlength=len(centers)
        )
        return sums / np.maximum(counts, 1)

    def remap_field(
        temp: np.ndarray,
        qmap: np.ndarray,
        umap: np.ndarray,
        ax: np.ndarray,
        ay: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        ci = (coords[0] + ax / dx) % n
        cj = (coords[1] + ay / dx) % n
        tl = map_coordinates(temp, [ci, cj], order=3, mode="wrap", prefilter=True)
        ql = map_coordinates(qmap, [ci, cj], order=3, mode="wrap", prefilter=True)
        ul = map_coordinates(umap, [ci, cj], order=3, mode="wrap", prefilter=True)
        ft = np.fft.fft2(tl)
        fq = np.fft.fft2(ql)
        fu = np.fft.fft2(ul)
        fe = fq * c2 + fu * s2
        fb = -fq * s2 + fu * c2
        return ft, fe, fb

    for realization in range(1, realizations + 1):
        w1 = np.fft.fft2(rng.normal(size=(n, n)))
        w2 = np.fft.fft2(rng.normal(size=(n, n)))
        w3 = np.fft.fft2(rng.normal(size=(n, n)))
        ft = w1 * np.sqrt(ctt) / dx
        fe = (
            corr * w1 + np.sqrt(np.maximum(1.0 - corr**2, 0.0)) * w2
        ) * np.sqrt(cee) / dx
        fq = fe * c2
        fu = fe * s2

        fphi = w3 * np.sqrt(cpp) / dx
        fphi_dark = w3 * np.sqrt(cpp_dark) / dx
        ax = np.fft.ifft2(1j * lx * fphi).real
        ay = np.fft.ifft2(1j * ly * fphi).real
        ax_dark = np.fft.ifft2(1j * lx * fphi_dark).real
        ay_dark = np.fft.ifft2(1j * ly * fphi_dark).real
        alpha_cold.append(float(np.mean(ax * ax + ay * ay)))
        alpha_dark.append(float(np.mean(ax_dark * ax_dark + ay_dark * ay_dark)))

        temp = np.fft.ifft2(ft).real
        qmap = np.fft.ifft2(fq).real
        umap = np.fft.ifft2(fu).real
        ft_c, fe_c, fb_c = remap_field(temp, qmap, umap, ax, ay)
        ft_d, fe_d, fb_d = remap_field(temp, qmap, umap, ax_dark, ay_dark)

        spectra = {
            "uTT": power_norm * np.abs(ft) ** 2,
            "uEE": power_norm * np.abs(fe) ** 2,
            "uTE": power_norm * np.real(ft * np.conj(fe)),
            "cTT": power_norm * np.abs(ft_c) ** 2,
            "cEE": power_norm * np.abs(fe_c) ** 2,
            "cTE": power_norm * np.real(ft_c * np.conj(fe_c)),
            "cBB": power_norm * np.abs(fb_c) ** 2,
            "dTT": power_norm * np.abs(ft_d) ** 2,
            "dEE": power_norm * np.abs(fe_d) ** 2,
            "dTE": power_norm * np.real(ft_d * np.conj(fe_d)),
            "dBB": power_norm * np.abs(fb_d) ** 2,
        }
        for key, value in spectra.items():
            accum[key] += bin_power(value)

        if snapshot_at is not None and realization == snapshot_at:
            snapshot = {key: value.copy() / realization for key, value in accum.items()}

    averaged = {key: value / realizations for key, value in accum.items()}

    # Use paired lensed/unlensed ratios to remove most realization variance.
    corrected = {
        "unlensed_TT": theory["TT"],
        "unlensed_EE": theory["EE"],
        "unlensed_TE": theory["TE"],
        "cold_TT": theory["TT"] * averaged["cTT"] / np.maximum(averaged["uTT"], 1.0e-80),
        "cold_EE": theory["EE"] * averaged["cEE"] / np.maximum(averaged["uEE"], 1.0e-80),
        "cold_TE": theory["TE"] + averaged["cTE"] - averaged["uTE"],
        "cold_BB": averaged["cBB"],
        "dark_TT": theory["TT"] * averaged["dTT"] / np.maximum(averaged["uTT"], 1.0e-80),
        "dark_EE": theory["EE"] * averaged["dEE"] / np.maximum(averaged["uEE"], 1.0e-80),
        "dark_TE": theory["TE"] + averaged["dTE"] - averaged["uTE"],
        "dark_BB": averaged["dBB"],
    }

    snapshot_corrected = None
    if snapshot is not None:
        snapshot_corrected = {
            "cold_TT": theory["TT"] * snapshot["cTT"] / np.maximum(snapshot["uTT"], 1.0e-80),
            "cold_EE": theory["EE"] * snapshot["cEE"] / np.maximum(snapshot["uEE"], 1.0e-80),
            "cold_BB": snapshot["cBB"],
            "dark_TT": theory["TT"] * snapshot["dTT"] / np.maximum(snapshot["uTT"], 1.0e-80),
            "dark_EE": theory["EE"] * snapshot["dEE"] / np.maximum(snapshot["uEE"], 1.0e-80),
            "dark_BB": snapshot["dBB"],
        }

    expected_alpha_cold = float(np.sum(lm**2 * cpp) / area)
    expected_alpha_dark = float(np.sum(lm**2 * cpp_dark) / area)
    return {
        "ell": centers,
        "corrected": corrected,
        "snapshot": snapshot_corrected,
        "alpha_cold": float(np.mean(alpha_cold)),
        "alpha_dark": float(np.mean(alpha_dark)),
        "expected_alpha_cold": expected_alpha_cold,
        "expected_alpha_dark": expected_alpha_dark,
        "n": n,
        "realizations": realizations,
    }


def to_dataframe(result: dict[str, object]) -> pd.DataFrame:
    ell = np.asarray(result["ell"], dtype=float)
    corrected = result["corrected"]
    fac = ell * (ell + 1.0) / (2.0 * math.pi) * TCMB_UK**2
    data: dict[str, np.ndarray] = {"ell": ell}
    for key, value in corrected.items():
        data[f"C_{key}"] = np.asarray(value)
        data[f"D_{key}_uK2"] = fac * np.asarray(value)
    data["dark_to_cold_TT"] = np.asarray(corrected["dark_TT"]) / np.maximum(np.asarray(corrected["cold_TT"]), 1.0e-80)
    data["dark_to_cold_EE"] = np.asarray(corrected["dark_EE"]) / np.maximum(np.asarray(corrected["cold_EE"]), 1.0e-80)
    data["dark_to_cold_BB"] = np.asarray(corrected["dark_BB"]) / np.maximum(np.asarray(corrected["cold_BB"]), 1.0e-80)
    return pd.DataFrame(data)


def nearest(df: pd.DataFrame, ell: float, column: str) -> float:
    i = int(np.argmin(np.abs(df["ell"].to_numpy() - ell)))
    return float(df.iloc[i][column])


def make_figures(lens: pd.DataFrame, spectra: pd.DataFrame, cross: pd.DataFrame) -> None:
    plt.figure(figsize=(7.2, 4.6))
    plt.loglog(lens["L"], lens["L"] ** 4 * lens["C_phi_phi_cold"] / (2.0 * math.pi), label="cold control")
    plt.loglog(lens["L"], lens["L"] ** 4 * lens["C_phi_phi_refinement"] / (2.0 * math.pi), label="refinement")
    plt.xlabel(r"$L$")
    plt.ylabel(r"$L^4 C_L^{\phi\phi}/(2\pi)$")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG / "cmb_lensing_potential.png", dpi=180)
    plt.close()

    plt.figure(figsize=(7.2, 4.6))
    plt.plot(spectra["ell"], spectra["D_unlensed_TT_uK2"], label="unlensed")
    plt.plot(spectra["ell"], spectra["D_cold_TT_uK2"], label="lensed")
    plt.xlim(30, 2200)
    plt.ylim(bottom=0)
    plt.xlabel(r"$\ell$")
    plt.ylabel(r"$D_\ell^{TT}\;[\mu\mathrm{K}^2]$")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG / "lensed_temperature_spectrum.png", dpi=180)
    plt.close()

    plt.figure(figsize=(7.2, 4.6))
    plt.semilogy(spectra["ell"], np.maximum(spectra["D_cold_BB_uK2"], 1.0e-8), label="cold-lensing control")
    plt.semilogy(spectra["ell"], np.maximum(spectra["D_dark_BB_uK2"], 1.0e-8), label="refinement lensing")
    plt.xlim(30, 2400)
    plt.xlabel(r"$\ell$")
    plt.ylabel(r"$D_\ell^{BB,\,\mathrm{lens}}\;[\mu\mathrm{K}^2]$")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG / "lensing_b_modes.png", dpi=180)
    plt.close()

    plt.figure(figsize=(7.2, 4.6))
    plt.semilogx(lens["L"], lens["refinement_to_cold_ratio"])
    plt.ylim(0.98, 1.0005)
    plt.xlabel(r"$L$")
    plt.ylabel("refinement / cold convergence power")
    plt.tight_layout()
    plt.savefig(FIG / "cmb_lensing_ratio.png", dpi=180)
    plt.close()

    plt.figure(figsize=(8.8, 4.8))
    labels = [str(x).replace("galaxy_", "g-").replace("lensing-", "") for x in cross["observable"]]
    xpos = np.arange(len(cross))
    plt.bar(xpos, cross["refinement_to_cold_ratio"])
    plt.ylim(0.65, 1.01)
    plt.xticks(xpos, labels, rotation=38, ha="right", fontsize=8)
    plt.ylabel("refinement / cold power")
    plt.tight_layout()
    plt.savefig(FIG / "cross_observable_scale_separation.png", dpi=180)
    plt.close()


def main() -> None:
    background = build_background()
    matter = build_matter_power()
    transfer = DarkTransfer()
    lens = lensing_potential(background, matter, transfer)
    lens.to_csv(DATA / "cmb_lensing_potential.csv", index=False)

    primary = PrimarySpectra()
    phi_cold = PhiSpectrum(lens, "C_phi_phi_cold")
    phi_dark = PhiSpectrum(lens, "C_phi_phi_refinement")
    main_result = simulate_remapping(
        primary,
        phi_cold,
        phi_dark,
        n=P.grid_n,
        realizations=P.realizations,
        seed=P.seed,
        snapshot_at=P.realizations // 2,
    )
    spectra = to_dataframe(main_result)
    spectra.to_csv(DATA / "lensed_cmb_spectra.csv", index=False)

    # Independent grid control.
    coarse = simulate_remapping(
        primary,
        phi_cold,
        phi_dark,
        n=448,
        realizations=20,
        seed=P.seed + 1,
    )
    coarse_df = to_dataframe(coarse)
    coarse_df.to_csv(DATA / "lensed_cmb_spectra_grid_control.csv", index=False)

    alpha_cont_cold = math.sqrt(
        float(np.trapezoid(lens["L"] ** 3 * lens["C_phi_phi_cold"] / (2.0 * math.pi), lens["L"]))
    )
    alpha_cont_dark = math.sqrt(
        float(np.trapezoid(lens["L"] ** 3 * lens["C_phi_phi_refinement"] / (2.0 * math.pi), lens["L"]))
    )
    arcmin = 180.0 / math.pi * 60.0

    galaxy = pd.read_csv(PARENT / "linear_lensing_ratios.csv")
    cross_rows = []
    for L in [100, 1000, 3000, 5000]:
        i = int(np.argmin(np.abs(lens["L"].to_numpy() - L)))
        cross_rows.append(
            {
                "observable": f"CMB-kappa-L{L}",
                "scale": float(L),
                "refinement_to_cold_ratio": float(lens.iloc[i]["refinement_to_cold_ratio"]),
            }
        )
    for source, ell in [("galaxy_z0p5", 1000), ("galaxy_z0p5", 5000), ("galaxy_z1", 5000)]:
        rows = galaxy[galaxy["source"] == source]
        j = int(np.argmin(np.abs(rows["ell"].to_numpy() - ell)))
        row = rows.iloc[j]
        cross_rows.append(
            {
                "observable": f"{source}-ell{int(row['ell'])}",
                "scale": float(row["ell"]),
                "refinement_to_cold_ratio": float(row["linear_lensing_power_ratio"]),
            }
        )
    for ell in [1000, 2000]:
        cross_rows.append(
            {
                "observable": f"lensing-BB-ell{ell}",
                "scale": float(ell),
                "refinement_to_cold_ratio": nearest(spectra, ell, "dark_to_cold_BB"),
            }
        )
    cross = pd.DataFrame(cross_rows)
    cross.to_csv(DATA / "lensing_cross_observable_ratios.csv", index=False)

    # Acoustic contrast around the second peak.
    d_unl = spectra["D_unlensed_TT_uK2"].to_numpy()
    d_len = spectra["D_cold_TT_uK2"].to_numpy()
    ell_arr = spectra["ell"].to_numpy()
    mask = (ell_arr > 150.0) & (ell_arr < 1200.0)
    peaks, _ = find_peaks(d_unl[mask], distance=8, prominence=np.max(d_unl[mask]) * 0.03)
    troughs, _ = find_peaks(-d_unl[mask], distance=6, prominence=np.max(d_unl[mask]) * 0.01)
    p_rows = np.flatnonzero(mask)[peaks]
    t_rows = np.flatnonzero(mask)[troughs]
    contrast_unl = float("nan")
    contrast_len = float("nan")
    if len(p_rows) >= 2:
        r = p_rows[1]
        left = t_rows[t_rows < r]
        right = t_rows[t_rows > r]
        if len(left) and len(right):
            il = left[-1]
            ir = right[0]
            contrast_unl = float((d_unl[r] - 0.5 * (d_unl[il] + d_unl[ir])) / d_unl[r])
            contrast_len = float((d_len[r] - 0.5 * (d_len[il] + d_len[ir])) / d_len[r])

    snapshot = main_result["snapshot"]
    realization_error = 0.0
    if snapshot is not None:
        selected = [100.0, 500.0, 1000.0, 1500.0, 2000.0]
        vals = []
        for ell in selected:
            i = int(np.argmin(np.abs(np.asarray(main_result["ell"]) - ell)))
            for key in ["cold_TT", "cold_EE", "cold_BB"]:
                full = float(main_result["corrected"][key][i])
                half = float(snapshot[key][i])
                vals.append(abs(full - half) / max(abs(full), 1.0e-30))
        realization_error = float(max(vals))

    grid_error = 0.0
    for ell in [100.0, 500.0, 1000.0, 1500.0, 2000.0]:
        for col in ["D_cold_TT_uK2", "D_cold_EE_uK2", "D_cold_BB_uK2"]:
            fine = nearest(spectra, ell, col)
            low = nearest(coarse_df, ell, col)
            grid_error = max(grid_error, abs(fine - low) / max(abs(fine), 1.0e-12))

    te_cauchy = np.max(
        np.abs(spectra["C_cold_TE"])
        / np.sqrt(np.maximum(spectra["C_cold_TT"] * spectra["C_cold_EE"], 1.0e-80))
    )

    checks: list[dict[str, object]] = []

    def add(cid: str, statement: str, value: float, threshold: float, mode: str = "le") -> None:
        if mode == "le":
            ok = abs(value) <= threshold
        elif mode == "ge":
            ok = value >= threshold
        elif mode == "range":
            ok = 0.0 <= value <= threshold
        else:
            raise ValueError(mode)
        checks.append(
            {
                "id": cid,
                "statement": statement,
                "value": float(value),
                "threshold": float(threshold),
                "status": "PASS" if ok else "FAIL",
            }
        )

    add("LEN01", "sigma8 normalization closes", float(matter["sigma8_check"] - P.sigma8), 2.0e-12)
    add("LEN02", "lensing potential is positive", float(lens[["C_phi_phi_cold", "C_phi_phi_refinement"]].min().min()), 0.0, "ge")
    add("LEN03", "refinement convergence power does not exceed cold control", float(lens["refinement_to_cold_ratio"].max()), 1.0000001, "range")
    add("LEN04", "finite-box cold deflection variance matches Fourier expectation", float(main_result["alpha_cold"] / main_result["expected_alpha_cold"] - 1.0), 0.04)
    add("LEN05", "finite-box refinement deflection variance matches Fourier expectation", float(main_result["alpha_dark"] / main_result["expected_alpha_dark"] - 1.0), 0.04)
    add("LEN06", "refinement deflection variance is no larger than cold control", float(main_result["alpha_dark"] / main_result["alpha_cold"]), 1.0000001, "range")
    add("LEN07", "lensing generated BB is nonnegative", float(spectra["C_cold_BB"].min()), 0.0, "ge")
    add("LEN08", "refinement lensing generated BB is nonnegative", float(spectra["C_dark_BB"].min()), 0.0, "ge")
    add("LEN09", "lensed TE obeys Cauchy bound", float(te_cauchy), 1.01, "range")
    add("LEN10", "realization refinement is controlled", realization_error, 0.10)
    add("LEN11", "grid refinement is controlled", grid_error, 0.12)
    add("LEN12", "second acoustic contrast is reduced by remapping", float(contrast_len / contrast_unl), 1.0, "range")
    add("LEN13", "CMB convergence suppression at L=3000 remains below one percent", abs(1.0 - float(cross[cross.observable == "CMB-kappa-L3000"].iloc[0].refinement_to_cold_ratio)), 0.01)
    add("LEN14", "low-redshift galaxy lensing sees stronger suppression than CMB lensing", float(cross[cross.observable == "galaxy_z0p5-ell5000"].iloc[0].refinement_to_cold_ratio / cross[cross.observable == "CMB-kappa-L3000"].iloc[0].refinement_to_cold_ratio), 1.0, "range")
    add("LEN15", "lensing BB response remains close to cold at ell 1000", abs(1.0 - nearest(spectra, 1000, "dark_to_cold_BB")), 0.01)
    add("LEN16", "continuum cold deflection is finite", alpha_cont_cold, 0.0, "ge")
    add("LEN17", "continuum refinement deflection is finite", alpha_cont_dark, 0.0, "ge")
    add("LEN18", "cold remapped TT is finite", float(np.isfinite(spectra["C_cold_TT"]).all()), 1.0, "ge")
    add("LEN19", "cold remapped EE is finite", float(np.isfinite(spectra["C_cold_EE"]).all()), 1.0, "ge")
    add("LEN20", "dark-to-cold lensing ratios are finite", float(np.isfinite(spectra[["dark_to_cold_TT", "dark_to_cold_EE", "dark_to_cold_BB"]]).all().all()), 1.0, "ge")

    check_df = pd.DataFrame(checks)
    check_df.to_csv(DATA / "cmb_lensing_remapping_checks.csv", index=False)

    summary = {
        "parameters": asdict(P),
        "sigma8_check": float(matter["sigma8_check"]),
        "chi_star_mpc": float(background["chi_star_mpc"]),
        "continuum_deflection_rms_arcmin_cold": alpha_cont_cold * arcmin,
        "continuum_deflection_rms_arcmin_refinement": alpha_cont_dark * arcmin,
        "finite_box_deflection_rms_arcmin_cold": math.sqrt(float(main_result["alpha_cold"])) * arcmin,
        "finite_box_deflection_rms_arcmin_refinement": math.sqrt(float(main_result["alpha_dark"])) * arcmin,
        "cmb_kappa_ratio_L1000": float(cross[cross.observable == "CMB-kappa-L1000"].iloc[0].refinement_to_cold_ratio),
        "cmb_kappa_ratio_L3000": float(cross[cross.observable == "CMB-kappa-L3000"].iloc[0].refinement_to_cold_ratio),
        "cmb_kappa_ratio_L5000": float(cross[cross.observable == "CMB-kappa-L5000"].iloc[0].refinement_to_cold_ratio),
        "galaxy_z0p5_ratio_ell5000": float(cross[cross.observable == "galaxy_z0p5-ell5000"].iloc[0].refinement_to_cold_ratio),
        "lensing_BB_D_ell1000_uK2": nearest(spectra, 1000, "D_cold_BB_uK2"),
        "lensing_BB_D_ell2000_uK2": nearest(spectra, 2000, "D_cold_BB_uK2"),
        "refinement_to_cold_BB_ell1000": nearest(spectra, 1000, "dark_to_cold_BB"),
        "refinement_to_cold_BB_ell2000": nearest(spectra, 2000, "dark_to_cold_BB"),
        "second_peak_contrast_unlensed": contrast_unl,
        "second_peak_contrast_lensed": contrast_len,
        "realization_refinement_max": realization_error,
        "grid_refinement_max": grid_error,
        "te_cauchy_max": float(te_cauchy),
        "pass_count": int((check_df.status == "PASS").sum()),
        "fail_count": int((check_df.status == "FAIL").sum()),
        "claim_boundary": [
            "linear matter power normalized to the declared sigma8 benchmark",
            "smooth BBKS-like baseline transfer rather than a precision baryon-wiggle spectrum",
            "Born flat-sky Gaussian remapping on a finite periodic patch",
            "no post-Born corrections, nonlinear matter power, foregrounds, or delensing",
            "primary TT/TE/EE inputs remain controlled templates rather than likelihood spectra",
        ],
    }
    (DATA / "CMB_Lensing_Remapping_Verification.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )

    make_figures(lens, spectra, cross)
    if summary["fail_count"]:
        raise RuntimeError(f"{summary['fail_count']} lensing checks failed")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
