#!/usr/bin/env python3
"""Deterministic one-zone cooling, feedback, and ionizing-source audit.

This program imports the frozen paired halo catalogues and the previously
computed halo mass functions. It applies one common baryonic gas-regulator
model to the cold and refinement branches without retuning the dark-sector
parameters.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, asdict
from itertools import product
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "inputs"
DATA = ROOT / "data"
FIG = ROOT / "figures"
SOURCE = ROOT / "source"
DATA.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)
SOURCE.mkdir(exist_ok=True)

# Declared background and baryon parameters inherited from the cosmology block.
OMEGA_M = 0.31
OMEGA_L = 0.69
OMEGA_B = 0.049
OMEGA_D = 0.261
F_B = OMEGA_B / (OMEGA_B + OMEGA_D)
RETURN_FRACTION = 0.40
A_REION = 1.0 / (1.0 + 7.41246511)
DYN_FACTOR = 0.10
T_ATOMIC = 1.0e4  # kelvin
MU = 0.59
M_PROTON = 1.67262192369e-27
K_BOLTZ = 1.380649e-23
T_PER_V2 = MU * M_PROTON * 1.0e6 / (2.0 * K_BOLTZ)  # K / (km/s)^2
V_ATOMIC = math.sqrt(T_ATOMIC / T_PER_V2)
H0_KMS_MPC = 70.0
G_MPC_KMS2_MSUN = 4.30091e-9

EPS_GRID = (0.005, 0.01, 0.02)
VFB_GRID = (40.0, 60.0, 80.0, 100.0)
BETA_GRID = (1.5, 2.0, 3.0)
VPHOTO_GRID = (15.0, 20.0, 25.0, 30.0)
NATOM_GRID = (2.0, 4.0, 8.0)
PARAM_GRID = tuple(product(EPS_GRID, VFB_GRID, BETA_GRID, VPHOTO_GRID, NATOM_GRID))
HMF_TABLE = pd.read_csv(INPUT / "halo_mass_function_ratios.csv")
REPRESENTATIVE = (0.01, 80.0, 2.0, 20.0, 4.0)
MASS_CUTS = (3.0e10, 1.0e11, 3.0e11, 1.0e12)  # Msun/h
A0 = 0.02
NSTEPS = 360


@dataclass(frozen=True)
class Params:
    eps_ff: float
    v_feedback: float
    beta: float
    v_photo: float
    n_atomic: float


def expansion(a: np.ndarray | float) -> np.ndarray | float:
    return np.sqrt(OMEGA_M / np.asarray(a) ** 3 + OMEGA_L)


def virial_temperature(v_kms: np.ndarray | float) -> np.ndarray | float:
    return T_PER_V2 * np.asarray(v_kms) ** 2


def atomic_cooling_gate(v_kms: np.ndarray, n_atomic: float) -> np.ndarray:
    temperature = virial_temperature(v_kms)
    return 1.0 / (1.0 + (T_ATOMIC / np.maximum(temperature, 1.0e-30)) ** n_atomic)


def photoheating_gate(v_kms: np.ndarray, a: float, v_photo: float) -> np.ndarray:
    if a < A_REION:
        return np.ones_like(v_kms)
    return 1.0 / (1.0 + (v_photo / np.maximum(v_kms, 1.0e-30)) ** 4)


def mass_loading(v_kms: np.ndarray, v_feedback: float, beta: float) -> np.ndarray:
    return (v_feedback / np.maximum(v_kms, 1.0e-30)) ** beta


def load_matched(tag: str) -> pd.DataFrame:
    matched = pd.read_csv(INPUT / f"matched_halos_{tag}.csv")
    formation = pd.read_csv(INPUT / f"matched_formation_{tag}.csv")
    cold = pd.read_csv(INPUT / f"halo_catalog_{tag}_cold_a1.000.csv").set_index("halo_id")
    refinement = pd.read_csv(INPUT / f"halo_catalog_{tag}_refinement_a1.000.csv").set_index("halo_id")

    data = matched.merge(
        formation[
            [
                "cold_halo_id",
                "refinement_halo_id",
                "cold_assembled_fraction_a0p5",
                "refinement_assembled_fraction_a0p5",
            ]
        ],
        on=["cold_halo_id", "refinement_halo_id"],
    )
    data = data[
        (data["cold_particles"] >= 64)
        & (data["jaccard"] >= 0.1)
        & (data["cold_assembled_fraction_a0p5"] > 0.0)
        & (data["refinement_assembled_fraction_a0p5"] > 0.0)
    ].copy()

    cold_ids = data["cold_halo_id"].astype(int).to_numpy()
    ref_ids = data["refinement_halo_id"].astype(int).to_numpy()
    data["cold_mass_msun_h"] = cold.loc[cold_ids, "mass_msun_h"].to_numpy()
    data["cold_vmax_kms"] = cold.loc[cold_ids, "vmax_kms"].to_numpy()
    data["refinement_mass_msun_h"] = refinement.loc[ref_ids, "mass_msun_h"].to_numpy()
    data["refinement_vmax_kms"] = refinement.loc[ref_ids, "vmax_kms"].to_numpy()
    return data.reset_index(drop=True)


def growth_history(m1: np.ndarray, v1: np.ndarray, f05: np.ndarray, a: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    exponent = np.log(f05) / np.log(0.5)
    mass = m1[:, None] * a[None, :] ** exponent[:, None]
    velocity = v1[:, None] * (mass / m1[:, None]) ** (1.0 / 3.0) * expansion(a)[None, :] ** (1.0 / 3.0)
    derivative = exponent[:, None] * mass / a[None, :]
    return mass, velocity, derivative


def evolve_regulator(
    m1: np.ndarray,
    v1: np.ndarray,
    f05: np.ndarray,
    params: Params,
    *,
    retain_history: bool = False,
) -> dict[str, np.ndarray | float]:
    m1 = np.asarray(m1, dtype=float)
    v1 = np.asarray(v1, dtype=float)
    f05 = np.asarray(f05, dtype=float)
    a = np.exp(np.linspace(np.log(A0), 0.0, NSTEPS + 1))
    mass, velocity, _ = growth_history(m1, v1, f05, a)

    gas = F_B * mass[:, 0].copy()
    stars = np.zeros_like(gas)
    outflow = np.zeros_like(gas)
    sfr = np.zeros_like(gas)
    max_budget_residual = 0.0

    histories: list[tuple[float, float, float, float, float, float]] = []
    for index in range(NSTEPS):
        amid = math.sqrt(a[index] * a[index + 1])
        da = a[index + 1] - a[index]
        exponent = np.log(f05) / np.log(0.5)
        midpoint_mass = m1 * amid**exponent
        midpoint_velocity = v1 * (midpoint_mass / m1) ** (1.0 / 3.0) * expansion(amid) ** (1.0 / 3.0)

        cooling = atomic_cooling_gate(midpoint_velocity, params.n_atomic)
        cooling *= photoheating_gate(midpoint_velocity, amid, params.v_photo)
        eta = mass_loading(midpoint_velocity, params.v_feedback, params.beta)
        activity = params.eps_ff * cooling / (DYN_FACTOR * amid)
        loss = activity * (1.0 - RETURN_FRACTION + eta)

        delta_mass = mass[:, index + 1] - mass[:, index]
        source = F_B * delta_mass / da
        kd = loss * da
        exponential = np.exp(-kd)
        gas_new = np.where(
            kd < 1.0e-8,
            gas + (source - loss * gas) * da,
            gas * exponential + source * (1.0 - exponential) / np.maximum(loss, 1.0e-30),
        )
        removed = np.maximum(gas + F_B * delta_mass - gas_new, 0.0)
        denominator = 1.0 - RETURN_FRACTION + eta
        stars += removed * (1.0 - RETURN_FRACTION) / denominator
        outflow += removed * eta / denominator
        gas = gas_new
        sfr = params.eps_ff * cooling * gas / DYN_FACTOR

        expected = F_B * mass[:, index + 1]
        budget = gas + stars + outflow
        max_budget_residual = max(
            max_budget_residual,
            float(np.max(np.abs(budget - expected) / np.maximum(F_B * m1, 1.0e-30))),
        )
        if retain_history:
            histories.append(
                (
                    a[index + 1],
                    float(np.sum(mass[:, index + 1])),
                    float(np.sum(gas)),
                    float(np.sum(stars)),
                    float(np.sum(outflow)),
                    float(np.sum(sfr)),
                )
            )

    result: dict[str, np.ndarray | float] = {
        "gas": gas,
        "stars": stars,
        "outflow": outflow,
        "sfr": sfr,
        "max_budget_residual": max_budget_residual,
    }
    if retain_history:
        result["history"] = np.asarray(histories)
    return result


def scan_catalogue(tag: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, float, pd.DataFrame, float, int]:
    pairs = load_matched(tag)
    ordered_table = ordered_history_table(tag, pairs)
    ordered_mask = ordered_table["ordered_mass_source_velocity_history"].to_numpy(dtype=bool)
    max_ordered_stellar_ratio = 0.0
    ordered_violations = 0
    rows: list[dict[str, float | str]] = []
    max_budget = 0.0
    cold_args = (
        pairs["cold_mass_msun_h"].to_numpy(),
        pairs["cold_vmax_kms"].to_numpy(),
        pairs["cold_assembled_fraction_a0p5"].to_numpy(),
    )
    ref_args = (
        pairs["refinement_mass_msun_h"].to_numpy(),
        pairs["refinement_vmax_kms"].to_numpy(),
        pairs["refinement_assembled_fraction_a0p5"].to_numpy(),
    )

    for values in PARAM_GRID:
        params = Params(*map(float, values))
        cold = evolve_regulator(*cold_args, params)
        refinement = evolve_regulator(*ref_args, params)
        max_budget = max(max_budget, float(cold["max_budget_residual"]), float(refinement["max_budget_residual"]))
        ordered_ratios = refinement["stars"][ordered_mask] / cold["stars"][ordered_mask]
        max_ordered_stellar_ratio = max(max_ordered_stellar_ratio, float(np.max(ordered_ratios)))
        ordered_violations += int(np.sum(ordered_ratios > 1.0 + 1.0e-10))

        row: dict[str, float | str] = {"tag": tag, **asdict(params)}
        row["matched_total_stellar_ratio"] = float(np.sum(refinement["stars"]) / np.sum(cold["stars"]))
        row["matched_total_gas_ratio"] = float(np.sum(refinement["gas"]) / np.sum(cold["gas"]))
        row["matched_total_sfr_ratio"] = float(np.sum(refinement["sfr"]) / np.sum(cold["sfr"]))
        for cut in MASS_CUTS:
            mask = pairs["cold_mass_msun_h"].to_numpy() <= cut
            suffix = f"{cut:.0e}"
            row[f"median_stellar_ratio_Mle_{suffix}"] = float(np.median(refinement["stars"][mask] / cold["stars"][mask]))
            row[f"median_gas_ratio_Mle_{suffix}"] = float(np.median(refinement["gas"][mask] / cold["gas"][mask]))
            row[f"median_sfr_ratio_Mle_{suffix}"] = float(np.median(refinement["sfr"][mask] / cold["sfr"][mask]))
            row[f"pairs_Mle_{suffix}"] = int(np.sum(mask))
        rows.append(row)

    scan = pd.DataFrame(rows)
    envelope_rows: list[dict[str, float | str]] = []
    observable_columns = [
        column
        for column in scan.columns
        if "_ratio" in column and not column.startswith("pairs_")
    ]
    for column in observable_columns:
        values = scan[column].to_numpy(dtype=float)
        envelope_rows.append(
            {
                "tag": tag,
                "observable": column,
                "minimum": float(np.min(values)),
                "median": float(np.median(values)),
                "maximum": float(np.max(values)),
            }
        )
    envelopes = pd.DataFrame(envelope_rows)

    representative = Params(*REPRESENTATIVE)
    cold_rep = evolve_regulator(*cold_args, representative, retain_history=True)
    ref_rep = evolve_regulator(*ref_args, representative, retain_history=True)
    cold_history = np.asarray(cold_rep["history"])
    ref_history = np.asarray(ref_rep["history"])
    history = pd.DataFrame(
        {
            "tag": tag,
            "a": cold_history[:, 0],
            "cold_halo_mass": cold_history[:, 1],
            "refinement_halo_mass": ref_history[:, 1],
            "cold_gas": cold_history[:, 2],
            "refinement_gas": ref_history[:, 2],
            "cold_stars": cold_history[:, 3],
            "refinement_stars": ref_history[:, 3],
            "cold_outflow": cold_history[:, 4],
            "refinement_outflow": ref_history[:, 4],
            "cold_sfr_proxy": cold_history[:, 5],
            "refinement_sfr_proxy": ref_history[:, 5],
        }
    )
    history["halo_mass_ratio"] = history["refinement_halo_mass"] / history["cold_halo_mass"]
    history["gas_ratio"] = history["refinement_gas"] / history["cold_gas"]
    history["stellar_ratio"] = history["refinement_stars"] / history["cold_stars"]
    history["sfr_ratio"] = history["refinement_sfr_proxy"] / history["cold_sfr_proxy"]
    return pairs, scan, envelopes, max_budget, history, ordered_table, max_ordered_stellar_ratio, ordered_violations


def ordered_history_table(tag: str, pairs: pd.DataFrame) -> pd.DataFrame:
    a = np.exp(np.linspace(np.log(A0), 0.0, 500))
    cold_mass, cold_velocity, cold_derivative = growth_history(
        pairs["cold_mass_msun_h"].to_numpy(),
        pairs["cold_vmax_kms"].to_numpy(),
        pairs["cold_assembled_fraction_a0p5"].to_numpy(),
        a,
    )
    ref_mass, ref_velocity, ref_derivative = growth_history(
        pairs["refinement_mass_msun_h"].to_numpy(),
        pairs["refinement_vmax_kms"].to_numpy(),
        pairs["refinement_assembled_fraction_a0p5"].to_numpy(),
        a,
    )
    ordered = (
        np.all(ref_mass <= cold_mass * (1.0 + 1.0e-12), axis=1)
        & np.all(ref_derivative <= cold_derivative * (1.0 + 1.0e-12), axis=1)
        & np.all(ref_velocity <= cold_velocity * (1.0 + 1.0e-12), axis=1)
    )
    table = pairs[
        [
            "cold_halo_id",
            "refinement_halo_id",
            "cold_mass_msun_h",
            "refinement_mass_msun_h",
            "mass_ratio",
            "vmax_ratio",
            "cold_assembled_fraction_a0p5",
            "refinement_assembled_fraction_a0p5",
        ]
    ].copy()
    table.insert(0, "tag", tag)
    table["ordered_mass_source_velocity_history"] = ordered
    return table


def hubble_z(z: float) -> float:
    return H0_KMS_MPC * math.sqrt(OMEGA_M * (1.0 + z) ** 3 + OMEGA_L)


def v200(mass_msun: np.ndarray, z: float) -> np.ndarray:
    h = hubble_z(z)
    rho_critical = 3.0 * h * h / (8.0 * math.pi * G_MPC_KMS2_MSUN)
    radius = (3.0 * mass_msun / (4.0 * math.pi * 200.0 * rho_critical)) ** (1.0 / 3.0)
    return np.sqrt(G_MPC_KMS2_MSUN * mass_msun / radius)


def load_hmf_at(redshift: float, branch: str, mass: np.ndarray) -> np.ndarray:
    hmf = HMF_TABLE
    column = "cold_dn_dlnM_Mpc3" if branch == "cold" else "refinement_dn_dlnM_Mpc3"
    redshifts = np.sort(hmf["z"].unique())
    if np.any(np.isclose(redshifts, redshift)):
        frame = hmf[np.isclose(hmf["z"], redshift)]
        return np.exp(
            np.interp(
                np.log(mass),
                np.log(frame["mass_msun"].to_numpy()),
                np.log(frame[column].to_numpy()),
            )
        )
    lower = float(redshifts[redshifts < redshift].max())
    upper = float(redshifts[redshifts > redshift].min())
    weight = (redshift - lower) / (upper - lower)
    low = hmf[np.isclose(hmf["z"], lower)]
    high = hmf[np.isclose(hmf["z"], upper)]
    low_log = np.interp(np.log(mass), np.log(low["mass_msun"]), np.log(low[column]))
    high_log = np.interp(np.log(mass), np.log(high["mass_msun"]), np.log(high[column]))
    return np.exp((1.0 - weight) * low_log + weight * high_log)


def ionizing_source_ratio(redshift: float, params: Params, include_photoheating: bool) -> float:
    atomic_mass = 1.0e8 * ((1.0 + redshift) / 10.0) ** (-1.5)
    mass = np.logspace(np.log10(atomic_mass), 13.0, 1000)
    velocity = v200(mass, redshift)
    cooling = atomic_cooling_gate(velocity, params.n_atomic)
    if include_photoheating:
        cooling *= 1.0 / (1.0 + (params.v_photo / velocity) ** 4)
    eta = mass_loading(velocity, params.v_feedback, params.beta)
    equilibrium_efficiency = cooling * (1.0 - RETURN_FRACTION) / (1.0 - RETURN_FRACTION + eta)
    cold = load_hmf_at(redshift, "cold", mass)
    refinement = load_hmf_at(redshift, "refinement", mass)
    cold_source = np.trapezoid(mass * equilibrium_efficiency * cold, x=np.log(mass))
    refinement_source = np.trapezoid(mass * equilibrium_efficiency * refinement, x=np.log(mass))
    return float(refinement_source / cold_source)


def ionizing_envelope() -> pd.DataFrame:
    rows: list[dict[str, float | bool]] = []
    for redshift in (6.0, 7.4, 8.0):
        for photoheating in (False, True):
            ratios = np.asarray(
                [ionizing_source_ratio(redshift, Params(*map(float, values)), photoheating) for values in PARAM_GRID]
            )
            boosts = 1.0 / ratios
            rows.append(
                {
                    "z": redshift,
                    "photoheating": photoheating,
                    "minimum_ratio": float(np.min(ratios)),
                    "q05_ratio": float(np.quantile(ratios, 0.05)),
                    "q25_ratio": float(np.quantile(ratios, 0.25)),
                    "median_ratio": float(np.median(ratios)),
                    "q75_ratio": float(np.quantile(ratios, 0.75)),
                    "q95_ratio": float(np.quantile(ratios, 0.95)),
                    "maximum_ratio": float(np.max(ratios)),
                    "minimum_required_boost": float(np.min(boosts)),
                    "median_required_boost": float(np.median(boosts)),
                    "maximum_required_boost": float(np.max(boosts)),
                    "fraction_requiring_boost_gt_2": float(np.mean(boosts > 2.0)),
                    "fraction_requiring_boost_gt_3": float(np.mean(boosts > 3.0)),
                }
            )
    return pd.DataFrame(rows)


def make_figures(envelopes: pd.DataFrame, histories: pd.DataFrame, ionizing: pd.DataFrame) -> None:
    # 1. Representative aggregate histories.
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    for tag, frame in histories.groupby("tag"):
        suffix = "260-step" if tag == "zoom" else "360-step"
        ax.plot(frame["a"], frame["stellar_ratio"], label=f"stellar, {suffix}")
        ax.plot(frame["a"], frame["sfr_ratio"], linestyle="--", label=f"SFR, {suffix}")
    ax.axvline(A_REION, linewidth=0.8, linestyle=":")
    ax.set_xscale("log")
    ax.set_xlabel("scale factor a")
    ax.set_ylabel("refinement / cold")
    ax.set_ylim(0.85, 1.01)
    ax.legend(ncol=2, fontsize=8)
    ax.set_title("Representative mass-conserving gas-regulator history")
    fig.tight_layout()
    fig.savefig(FIG / "01_regulator_history.pdf")
    plt.close(fig)

    # 2. Dwarf stellar and SFR envelopes.
    selected = []
    for tag in ("zoom", "zoomfine"):
        for cut in (3.0e10, 1.0e11, 3.0e11, 1.0e12):
            for kind in ("stellar", "sfr"):
                obs = f"median_{kind}_ratio_Mle_{cut:.0e}"
                row = envelopes[(envelopes["tag"] == tag) & (envelopes["observable"] == obs)].iloc[0]
                selected.append((tag, cut, kind, row["minimum"], row["median"], row["maximum"]))
    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    cuts = np.arange(4)
    width = 0.18
    offsets = {("zoom", "stellar"): -1.5 * width, ("zoom", "sfr"): -0.5 * width,
               ("zoomfine", "stellar"): 0.5 * width, ("zoomfine", "sfr"): 1.5 * width}
    labels_used = set()
    for tag, cut, kind, low, med, high in selected:
        x = list((3.0e10, 1.0e11, 3.0e11, 1.0e12)).index(cut) + offsets[(tag, kind)]
        label = f"{tag}, {kind}"
        ax.errorbar(x, med, yerr=[[med - low], [high - med]], fmt="o", capsize=3,
                    label=label if label not in labels_used else None)
        labels_used.add(label)
    ax.axhline(1.0, linewidth=0.8)
    ax.set_xticks(cuts, [r"$3\times10^{10}$", r"$10^{11}$", r"$3\times10^{11}$", r"$10^{12}$"])
    ax.set_xlabel(r"maximum cold halo mass [$M_\odot/h$]")
    ax.set_ylabel("median refinement / cold")
    ax.set_ylim(0.35, 1.02)
    ax.legend(fontsize=8, ncol=2)
    ax.set_title("Cooling and feedback amplify the near-cutoff difference")
    fig.tight_layout()
    fig.savefig(FIG / "02_dwarf_response_envelopes.pdf")
    plt.close(fig)

    # 3. Ionizing emissivity envelope.
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    for photo, frame in ionizing.groupby("photoheating"):
        frame = frame.sort_values("z")
        label = "post-ionization photoheating" if photo else "no photoheating"
        ax.plot(frame["z"], frame["median_ratio"], marker="o", label=label)
        ax.fill_between(frame["z"], frame["minimum_ratio"], frame["maximum_ratio"], alpha=0.2)
    prior = pd.read_csv(INPUT / "reionization_consistency.csv")
    ax.plot(prior["z"], prior["refinement_to_cold_fraction"], marker="s", linestyle=":", label="unweighted collapsed fraction")
    ax.set_xlabel("redshift z")
    ax.set_ylabel("refinement / cold source ratio")
    ax.set_ylim(0.1, 0.8)
    ax.legend(fontsize=8)
    ax.set_title("Feedback-weighted ionizing emissivity remains suppressed")
    fig.tight_layout()
    fig.savefig(FIG / "03_ionizing_emissivity.pdf")
    plt.close(fig)

    # 4. Equilibrium efficiency curves.
    velocity = np.logspace(np.log10(8.0), np.log10(250.0), 500)
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    for vfb in (40.0, 60.0, 80.0, 100.0):
        params = Params(0.01, vfb, 2.0, 20.0, 4.0)
        cooling = atomic_cooling_gate(velocity, params.n_atomic)
        photo = 1.0 / (1.0 + (params.v_photo / velocity) ** 4)
        eta = mass_loading(velocity, params.v_feedback, params.beta)
        efficiency = cooling * photo * (1.0 - RETURN_FRACTION) / (1.0 - RETURN_FRACTION + eta)
        ax.plot(velocity, efficiency, label=fr"$V_{{\rm fb}}={vfb:.0f}$ km/s")
    ax.axvline(V_ATOMIC, linewidth=0.8, linestyle=":", label="atomic threshold")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel(r"halo speed $V$ [km/s]")
    ax.set_ylabel("equilibrium retained-star fraction")
    ax.set_ylim(1.0e-5, 1.1)
    ax.legend(fontsize=8)
    ax.set_title("Atomic cooling and energy-driven feedback")
    fig.tight_layout()
    fig.savefig(FIG / "04_feedback_efficiency.pdf")
    plt.close(fig)


def envelope_lookup(envelopes: pd.DataFrame, tag: str, observable: str) -> dict[str, float]:
    row = envelopes[(envelopes["tag"] == tag) & (envelopes["observable"] == observable)].iloc[0]
    return {key: float(row[key]) for key in ("minimum", "median", "maximum")}


def main() -> None:
    all_scans: list[pd.DataFrame] = []
    all_envelopes: list[pd.DataFrame] = []
    all_histories: list[pd.DataFrame] = []
    ordered_tables: list[pd.DataFrame] = []
    pair_counts: dict[str, int] = {}
    max_budget = 0.0
    ordered_maxima: list[float] = []
    ordered_bad_total = 0

    for tag in ("zoom", "zoomfine"):
        pairs, scan, envelopes, budget, history, ordered_table, ordered_max, ordered_bad = scan_catalogue(tag)
        all_scans.append(scan)
        all_envelopes.append(envelopes)
        all_histories.append(history)
        ordered_tables.append(ordered_table)
        pair_counts[tag] = len(pairs)
        max_budget = max(max_budget, budget)
        ordered_maxima.append(ordered_max)
        ordered_bad_total += ordered_bad

    scan = pd.concat(all_scans, ignore_index=True)
    envelopes = pd.concat(all_envelopes, ignore_index=True)
    histories = pd.concat(all_histories, ignore_index=True)
    ordered = pd.concat(ordered_tables, ignore_index=True)
    ionizing = ionizing_envelope()

    scan.to_csv(DATA / "gas_regulator_parameter_scan.csv", index=False)
    envelopes.to_csv(DATA / "gas_regulator_envelopes.csv", index=False)
    histories.to_csv(DATA / "representative_regulator_history.csv", index=False)
    ordered.to_csv(DATA / "ordered_history_pairs.csv", index=False)
    ionizing.to_csv(DATA / "ionizing_emissivity_envelope.csv", index=False)
    make_figures(envelopes, histories, ionizing)

    # Numerical theorem audit accumulated during the parameter scans.
    max_ordered_stellar_ratio = max(ordered_maxima)
    ordered_violations = ordered_bad_total

    zoom_total_stars = envelope_lookup(envelopes, "zoom", "matched_total_stellar_ratio")
    control_total_stars = envelope_lookup(envelopes, "zoomfine", "matched_total_stellar_ratio")
    zoom_dwarf_stars = envelope_lookup(envelopes, "zoom", "median_stellar_ratio_Mle_3e+10")
    control_dwarf_stars = envelope_lookup(envelopes, "zoomfine", "median_stellar_ratio_Mle_3e+10")
    zoom_dwarf_sfr = envelope_lookup(envelopes, "zoom", "median_sfr_ratio_Mle_3e+10")
    control_dwarf_sfr = envelope_lookup(envelopes, "zoomfine", "median_sfr_ratio_Mle_3e+10")
    reion_row = ionizing[(ionizing["z"] == 7.4) & (ionizing["photoheating"] == True)].iloc[0]
    prior = pd.read_csv(INPUT / "reionization_consistency.csv")
    prior_penalty = float(prior[np.isclose(prior["z"], 7.4)]["required_efficiency_penalty"].iloc[0])

    checks: list[dict[str, object]] = []
    def record(identifier: str, statement: str, passed: bool, value: float | int | str) -> None:
        checks.append({"id": identifier, "statement": statement, "status": "PASS" if passed else "FAIL", "value": value})

    record("CFR01", "atomic cooling speed is finite and near 17 km/s", 16.0 < V_ATOMIC < 18.0, V_ATOMIC)
    record("CFR02", "complete parameter grid contains 432 points", len(PARAM_GRID) == 432, len(PARAM_GRID))
    record("CFR03", "zoom matched sample is nonempty", pair_counts["zoom"] > 40, pair_counts["zoom"])
    record("CFR04", "time-control matched sample is nonempty", pair_counts["zoomfine"] > 40, pair_counts["zoomfine"])
    record("CFR05", "gas regulator preserves baryonic mass", max_budget < 5.0e-12, max_budget)
    record("CFR06", "all regulator outputs are finite", bool(np.isfinite(scan.select_dtypes(include=[np.number]).to_numpy()).all()), 0)
    record("CFR07", "matched total stellar budget is suppressed across zoom scan", zoom_total_stars["maximum"] < 1.0, zoom_total_stars["maximum"])
    record("CFR08", "matched total stellar budget is suppressed across time-control scan", control_total_stars["maximum"] < 1.0, control_total_stars["maximum"])
    record("CFR09", "near-cutoff stellar median is below 0.70 across zoom scan", zoom_dwarf_stars["maximum"] < 0.70, zoom_dwarf_stars["maximum"])
    record("CFR10", "near-cutoff stellar median is below 0.70 across time-control scan", control_dwarf_stars["maximum"] < 0.70, control_dwarf_stars["maximum"])
    record("CFR11", "near-cutoff current SFR median is below 0.65 across zoom scan", zoom_dwarf_sfr["maximum"] < 0.65, zoom_dwarf_sfr["maximum"])
    record("CFR12", "near-cutoff current SFR median is below 0.65 across time-control scan", control_dwarf_sfr["maximum"] < 0.65, control_dwarf_sfr["maximum"])
    record("CFR13", "source-ordered pairs exist in both catalogues", int(ordered.groupby("tag")["ordered_mass_source_velocity_history"].sum().min()) >= 15, int(ordered.groupby("tag")["ordered_mass_source_velocity_history"].sum().min()))
    record("CFR14", "source-ordered pairs have no integrated stellar-ordering violation", ordered_violations == 0, ordered_violations)
    record("CFR15", "maximum ordered stellar ratio remains below unity", max_ordered_stellar_ratio <= 1.0 + 1.0e-10, max_ordered_stellar_ratio)
    record("CFR16", "z=7.4 ionizing source remains suppressed over complete scan", float(reion_row["maximum_ratio"]) < 1.0, float(reion_row["maximum_ratio"]))
    record("CFR17", "feedback-weighted median reionization burden is below collapsed-fraction penalty", float(reion_row["median_required_boost"]) < prior_penalty, float(reion_row["median_required_boost"]))
    record("CFR18", "z=7.4 required boost remains below three across scan", float(reion_row["maximum_required_boost"]) < 3.0, float(reion_row["maximum_required_boost"]))
    record("CFR19", "representative histories retain positive gas and stars", bool((histories[["cold_gas", "refinement_gas", "cold_stars", "refinement_stars"]].to_numpy() >= 0.0).all()), 0)
    record("CFR20", "time-control dwarf-SFR median agrees within 0.03", abs(control_dwarf_sfr["median"] - zoom_dwarf_sfr["median"]) < 0.03, abs(control_dwarf_sfr["median"] - zoom_dwarf_sfr["median"]))

    checks_frame = pd.DataFrame(checks)
    checks_frame.to_csv(DATA / "cooling_feedback_reionization_checks.csv", index=False)
    passed = int((checks_frame["status"] == "PASS").sum())
    failed = int((checks_frame["status"] == "FAIL").sum())

    summary = {
        "model": {
            "baryon_fraction": F_B,
            "return_fraction": RETURN_FRACTION,
            "reionization_scale_factor": A_REION,
            "atomic_temperature_K": T_ATOMIC,
            "atomic_velocity_kms": V_ATOMIC,
            "parameter_grid_size": len(PARAM_GRID),
            "representative_parameters": asdict(Params(*REPRESENTATIVE)),
        },
        "samples": pair_counts,
        "mass_conservation_max_relative_residual": max_budget,
        "ordered_history_pairs": {
            tag: int(group["ordered_mass_source_velocity_history"].sum())
            for tag, group in ordered.groupby("tag")
        },
        "max_ordered_integrated_stellar_ratio": max_ordered_stellar_ratio,
        "zoom": {
            "matched_total_stellar": zoom_total_stars,
            "matched_dwarf_stellar_Mle_3e10": zoom_dwarf_stars,
            "matched_dwarf_sfr_Mle_3e10": zoom_dwarf_sfr,
        },
        "zoomfine": {
            "matched_total_stellar": control_total_stars,
            "matched_dwarf_stellar_Mle_3e10": control_dwarf_stars,
            "matched_dwarf_sfr_Mle_3e10": control_dwarf_sfr,
        },
        "ionizing_source_z7p4_with_photoheating": {
            key: float(reion_row[key])
            for key in (
                "minimum_ratio",
                "median_ratio",
                "maximum_ratio",
                "minimum_required_boost",
                "median_required_boost",
                "maximum_required_boost",
                "fraction_requiring_boost_gt_2",
            )
        },
        "unweighted_collapsed_fraction_penalty_z7p4": prior_penalty,
        "checks": {"pass": passed, "fail": failed, "records": checks},
    }
    with open(DATA / "Cooling_Feedback_Reionization_Verification.json", "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)

    # LaTeX macros generated from the deterministic record.
    macros = rf"""% Generated by Cooling_Feedback_Reionization_Verification.py
\newcommand{{\CFRAtomicVelocity}}{{{V_ATOMIC:.6f}}}
\newcommand{{\CFRPairZoom}}{{{pair_counts['zoom']}}}
\newcommand{{\CFRPairControl}}{{{pair_counts['zoomfine']}}}
\newcommand{{\CFRMassResidual}}{{{max_budget:.3e}}}
\newcommand{{\CFRZoomTotalStarMin}}{{{zoom_total_stars['minimum']:.6f}}}
\newcommand{{\CFRZoomTotalStarMedian}}{{{zoom_total_stars['median']:.6f}}}
\newcommand{{\CFRZoomTotalStarMax}}{{{zoom_total_stars['maximum']:.6f}}}
\newcommand{{\CFRControlTotalStarMin}}{{{control_total_stars['minimum']:.6f}}}
\newcommand{{\CFRControlTotalStarMedian}}{{{control_total_stars['median']:.6f}}}
\newcommand{{\CFRControlTotalStarMax}}{{{control_total_stars['maximum']:.6f}}}
\newcommand{{\CFRZoomDwarfStarMin}}{{{zoom_dwarf_stars['minimum']:.6f}}}
\newcommand{{\CFRZoomDwarfStarMedian}}{{{zoom_dwarf_stars['median']:.6f}}}
\newcommand{{\CFRZoomDwarfStarMax}}{{{zoom_dwarf_stars['maximum']:.6f}}}
\newcommand{{\CFRControlDwarfStarMin}}{{{control_dwarf_stars['minimum']:.6f}}}
\newcommand{{\CFRControlDwarfStarMedian}}{{{control_dwarf_stars['median']:.6f}}}
\newcommand{{\CFRControlDwarfStarMax}}{{{control_dwarf_stars['maximum']:.6f}}}
\newcommand{{\CFRZoomDwarfSFRMin}}{{{zoom_dwarf_sfr['minimum']:.6f}}}
\newcommand{{\CFRZoomDwarfSFRMedian}}{{{zoom_dwarf_sfr['median']:.6f}}}
\newcommand{{\CFRZoomDwarfSFRMax}}{{{zoom_dwarf_sfr['maximum']:.6f}}}
\newcommand{{\CFRControlDwarfSFRMin}}{{{control_dwarf_sfr['minimum']:.6f}}}
\newcommand{{\CFRControlDwarfSFRMedian}}{{{control_dwarf_sfr['median']:.6f}}}
\newcommand{{\CFRControlDwarfSFRMax}}{{{control_dwarf_sfr['maximum']:.6f}}}
\newcommand{{\CFRIonMin}}{{{float(reion_row['minimum_ratio']):.6f}}}
\newcommand{{\CFRIonMedian}}{{{float(reion_row['median_ratio']):.6f}}}
\newcommand{{\CFRIonMax}}{{{float(reion_row['maximum_ratio']):.6f}}}
\newcommand{{\CFRBoostMin}}{{{float(reion_row['minimum_required_boost']):.6f}}}
\newcommand{{\CFRBoostMedian}}{{{float(reion_row['median_required_boost']):.6f}}}
\newcommand{{\CFRBoostMax}}{{{float(reion_row['maximum_required_boost']):.6f}}}
\newcommand{{\CFRPriorPenalty}}{{{prior_penalty:.6f}}}
\newcommand{{\CFROrderedZoom}}{{{int(ordered[ordered['tag']=='zoom']['ordered_mass_source_velocity_history'].sum())}}}
\newcommand{{\CFROrderedControl}}{{{int(ordered[ordered['tag']=='zoomfine']['ordered_mass_source_velocity_history'].sum())}}}
\newcommand{{\CFRMaxOrderedStar}}{{{max_ordered_stellar_ratio:.6f}}}
\newcommand{{\CFRPass}}{{{passed}}}
\newcommand{{\CFRFail}}{{{failed}}}
"""
    (SOURCE / "generated_values.tex").write_text(macros, encoding="utf-8")

    print(json.dumps({"pass": passed, "fail": failed, "max_budget": max_budget}, indent=2))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
