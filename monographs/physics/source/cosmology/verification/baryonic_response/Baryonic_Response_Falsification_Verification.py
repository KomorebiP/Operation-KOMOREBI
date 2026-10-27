from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "inputs"
DATA = ROOT / "data"
FIG = ROOT / "figures"
DATA.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)

TAGS = ("zoom", "zoomfine")
BOX = {"zoom": 8.0, "zoomfine": 8.0}
V50_GRID = (15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 50.0)
WIDTH_GRID = (0.15, 0.25, 0.40, 0.60)
VEV_GRID = (15.0, 20.0, 25.0, 30.0, 40.0)
ETA_GRID = (2.0, 3.0, 4.0, 6.0)
VSTAR_GRID = (25.0, 40.0, 60.0, 80.0)
ALPHA_GRID = (1.0, 2.0, 3.0)
MASS_CAPS = (3.0e10, 1.0e11, 3.0e11, 1.0e12, 1.0e13)


def load_tag(tag: str) -> dict[str, pd.DataFrame]:
    return {
        "cold": pd.read_csv(INPUT / f"halo_catalog_{tag}_cold_a1.000.csv"),
        "ref": pd.read_csv(INPUT / f"halo_catalog_{tag}_refinement_a1.000.csv"),
        "match": pd.read_csv(INPUT / f"matched_halos_{tag}.csv"),
        "formation": pd.read_csv(INPUT / f"matched_formation_{tag}.csv"),
        "cumulative": pd.read_csv(INPUT / f"halo_cumulative_{tag}.csv"),
    }


def occupation(v: np.ndarray, v50: float, width: float) -> np.ndarray:
    v = np.maximum(np.asarray(v, dtype=float), 1e-12)
    return 1.0 / (1.0 + np.exp(-np.log(v / v50) / width))


def gas_weight(df: pd.DataFrame, v_evap: float, eta: float) -> np.ndarray:
    v = df["vmax_kms"].to_numpy(float)
    m = df["mass_msun_h"].to_numpy(float)
    return m / (1.0 + (v_evap / np.maximum(v, 1e-12)) ** eta)


def stellar_weight(
    df: pd.DataFrame,
    v_evap: float,
    eta: float,
    v_star: float,
    alpha: float,
) -> np.ndarray:
    v = df["vmax_kms"].to_numpy(float)
    gas = gas_weight(df, v_evap, eta)
    x = (v / v_star) ** alpha
    return gas * x / (1.0 + x)


def robust_matches(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    m = frames["match"].copy()
    m = m[(m["cold_particles"] >= 64) & (m["jaccard"] >= 0.1)].copy()
    f = frames["formation"][["cold_halo_id", "refinement_halo_id", "formation_fraction_ratio"]]
    return m.merge(f, on=["cold_halo_id", "refinement_halo_id"], how="left")


def attach_match_values(frames: dict[str, pd.DataFrame], matches: pd.DataFrame) -> pd.DataFrame:
    c = frames["cold"][["halo_id", "mass_msun_h", "vmax_kms"]].rename(
        columns={"halo_id": "cold_halo_id", "mass_msun_h": "cold_mass_value", "vmax_kms": "cold_vmax_value"}
    )
    r = frames["ref"][["halo_id", "mass_msun_h", "vmax_kms"]].rename(
        columns={"halo_id": "refinement_halo_id", "mass_msun_h": "ref_mass_value", "vmax_kms": "ref_vmax_value"}
    )
    return matches.merge(c, on="cold_halo_id", how="left").merge(r, on="refinement_halo_id", how="left")


def matched_response_ratios(
    matches: pd.DataFrame,
    v_evap: float,
    eta: float,
    v_star: float,
    alpha: float,
) -> np.ndarray:
    mc = matches["cold_mass_value"].to_numpy(float)
    mr = matches["ref_mass_value"].to_numpy(float)
    vc = matches["cold_vmax_value"].to_numpy(float)
    vr = matches["ref_vmax_value"].to_numpy(float)
    def response(m: np.ndarray, v: np.ndarray) -> np.ndarray:
        gas = m / (1.0 + (v_evap / np.maximum(v, 1e-12)) ** eta)
        x = (v / v_star) ** alpha
        return gas * x / (1.0 + x)
    return response(mr, vr) / response(mc, vc)


def periodic_distances(df: pd.DataFrame, host: pd.Series, box: float) -> np.ndarray:
    pos = df[["x_mpc_h", "y_mpc_h", "z_mpc_h"]].to_numpy(float)
    hpos = host[["x_mpc_h", "y_mpc_h", "z_mpc_h"]].to_numpy(float)
    d = np.abs(pos - hpos)
    d = np.minimum(d, box - d)
    return np.sqrt(np.sum(d * d, axis=1))


def build_outputs() -> dict[str, Any]:
    occupation_rows: list[dict[str, Any]] = []
    response_rows: list[dict[str, Any]] = []
    envelope_rows: list[dict[str, Any]] = []
    structural_rows: list[dict[str, Any]] = []
    neighborhood_rows: list[dict[str, Any]] = []
    checks: list[dict[str, Any]] = []

    frames_by_tag = {tag: load_tag(tag) for tag in TAGS}

    for tag, frames in frames_by_tag.items():
        cold = frames["cold"]
        ref = frames["ref"]
        matches = attach_match_values(frames, robust_matches(frames))

        # Occupation scan.
        for v50, width in itertools.product(V50_GRID, WIDTH_GRID):
            nc = float(np.sum(occupation(cold["vmax_kms"].to_numpy(), v50, width)))
            nr = float(np.sum(occupation(ref["vmax_kms"].to_numpy(), v50, width)))
            occupation_rows.append(
                {
                    "tag": tag,
                    "v50_kms": v50,
                    "log_width": width,
                    "expected_luminous_cold": nc,
                    "expected_luminous_refinement": nr,
                    "luminous_count_ratio": nr / nc,
                }
            )

        # Baryonic response scan.
        for v_evap, eta, v_star, alpha in itertools.product(
            VEV_GRID, ETA_GRID, VSTAR_GRID, ALPHA_GRID
        ):
            gc = float(np.sum(gas_weight(cold, v_evap, eta)))
            gr = float(np.sum(gas_weight(ref, v_evap, eta)))
            sc = float(np.sum(stellar_weight(cold, v_evap, eta, v_star, alpha)))
            sr = float(np.sum(stellar_weight(ref, v_evap, eta, v_star, alpha)))
            row: dict[str, Any] = {
                "tag": tag,
                "v_evap_kms": v_evap,
                "eta": eta,
                "v_star_kms": v_star,
                "alpha": alpha,
                "total_gas_ratio": gr / gc,
                "total_stellar_ratio": sr / sc,
            }
            for cap in MASS_CAPS:
                sub = matches[matches["cold_mass_msun_h"] <= cap]
                ratios = matched_response_ratios(sub, v_evap, eta, v_star, alpha)
                row[f"matched_median_stellar_ratio_Mle_{cap:.0e}"] = float(
                    np.median(ratios)
                )
            response_rows.append(row)

        # Matched structural proxies.
        for row in matches.itertuples(index=False):
            structural_rows.append(
                {
                    "tag": tag,
                    "cold_halo_id": int(row.cold_halo_id),
                    "refinement_halo_id": int(row.refinement_halo_id),
                    "cold_mass_msun_h": float(row.cold_mass_msun_h),
                    "mass_ratio": float(row.mass_ratio),
                    "vmax_ratio": float(row.vmax_ratio),
                    "rhalf_ratio": float(row.rhalf_ratio),
                    "sigma1d_ratio": float(row.sigma1d_ratio),
                    "formation_fraction_ratio": float(row.formation_fraction_ratio),
                    "half_mass_surface_density_ratio": float(
                        row.mass_ratio / (row.rhalf_ratio**2)
                    ),
                    "dynamical_surface_density_ratio": float(
                        row.vmax_ratio**2 / row.rhalf_ratio
                    ),
                }
            )

        # Host-neighborhood control: explicitly exploratory and used as a non-convergence test.
        cidx = cold.set_index("halo_id")
        ridx = ref.set_index("halo_id")
        top_hosts = matches.sort_values("cold_mass_msun_h", ascending=False).head(5)
        for radius in (0.5, 1.0, 1.5):
            cold_neighbor_v: list[np.ndarray] = []
            ref_neighbor_v: list[np.ndarray] = []
            for h in top_hosts.itertuples(index=False):
                hc = cidx.loc[int(h.cold_halo_id)]
                hr = ridx.loc[int(h.refinement_halo_id)]
                dc = periodic_distances(cold, hc, BOX[tag])
                dr = periodic_distances(ref, hr, BOX[tag])
                mc = (dc > 1e-10) & (dc <= radius)
                mr = (dr > 1e-10) & (dr <= radius)
                cold_neighbor_v.append(cold.loc[mc, "vmax_kms"].to_numpy(float))
                ref_neighbor_v.append(ref.loc[mr, "vmax_kms"].to_numpy(float))
            cv = np.concatenate(cold_neighbor_v) if cold_neighbor_v else np.empty(0)
            rv = np.concatenate(ref_neighbor_v) if ref_neighbor_v else np.empty(0)
            for v50, width in itertools.product(V50_GRID, WIDTH_GRID):
                nc = float(np.sum(occupation(cv, v50, width)))
                nr = float(np.sum(occupation(rv, v50, width)))
                neighborhood_rows.append(
                    {
                        "tag": tag,
                        "radius_mpc_h": radius,
                        "v50_kms": v50,
                        "log_width": width,
                        "cold_expected_neighbors": nc,
                        "refinement_expected_neighbors": nr,
                        "neighbor_ratio": nr / nc if nc > 0 else np.nan,
                    }
                )

    occ = pd.DataFrame(occupation_rows)
    resp = pd.DataFrame(response_rows)
    struct = pd.DataFrame(structural_rows)
    neigh = pd.DataFrame(neighborhood_rows)

    occ.to_csv(DATA / "luminous_occupation_scan.csv", index=False)
    resp.to_csv(DATA / "baryonic_response_scan.csv", index=False)
    struct.to_csv(DATA / "matched_structural_proxies.csv", index=False)
    neigh.to_csv(DATA / "host_neighborhood_control.csv", index=False)

    # Aggregated response envelopes.
    for tag in TAGS:
        o = occ[occ["tag"] == tag]["luminous_count_ratio"]
        rr = resp[resp["tag"] == tag]
        envelope_rows.extend(
            [
                {
                    "tag": tag,
                    "observable": "global_luminous_count_ratio",
                    "minimum": float(o.min()),
                    "median": float(o.median()),
                    "maximum": float(o.max()),
                },
                {
                    "tag": tag,
                    "observable": "total_gas_ratio",
                    "minimum": float(rr["total_gas_ratio"].min()),
                    "median": float(rr["total_gas_ratio"].median()),
                    "maximum": float(rr["total_gas_ratio"].max()),
                },
                {
                    "tag": tag,
                    "observable": "total_stellar_ratio",
                    "minimum": float(rr["total_stellar_ratio"].min()),
                    "median": float(rr["total_stellar_ratio"].median()),
                    "maximum": float(rr["total_stellar_ratio"].max()),
                },
            ]
        )
        for cap in MASS_CAPS:
            col = f"matched_median_stellar_ratio_Mle_{cap:.0e}"
            envelope_rows.append(
                {
                    "tag": tag,
                    "observable": f"matched_stellar_ratio_Mle_{cap:.0e}",
                    "minimum": float(rr[col].min()),
                    "median": float(rr[col].median()),
                    "maximum": float(rr[col].max()),
                }
            )
        s = struct[struct["tag"] == tag]
        for col in (
            "half_mass_surface_density_ratio",
            "dynamical_surface_density_ratio",
        ):
            envelope_rows.append(
                {
                    "tag": tag,
                    "observable": col,
                    "minimum": float(s[col].quantile(0.10)),
                    "median": float(s[col].median()),
                    "maximum": float(s[col].quantile(0.90)),
                }
            )

    env = pd.DataFrame(envelope_rows)
    env.to_csv(DATA / "baryonic_response_envelopes.csv", index=False)

    # Imported fixed-parameter observables.
    reion = pd.read_csv(INPUT / "reionization_consistency.csv")
    z74 = reion.iloc[(reion["z"] - 7.4).abs().argmin()]
    nlens = pd.read_csv(INPUT / "nonlinear_lensing_ratios.csv")
    glens = nlens[(nlens["source_z"] == 0.5) & (nlens["ell"] == 5000.0)].iloc[0]
    cross = pd.read_csv(INPUT / "lensing_cross_observable_ratios.csv")
    cmb = cross[cross["observable"] == "CMB-kappa-L3000"].iloc[0]

    zoom_occ = env[
        (env["tag"] == "zoom")
        & (env["observable"] == "global_luminous_count_ratio")
    ].iloc[0]
    zf_occ = env[
        (env["tag"] == "zoomfine")
        & (env["observable"] == "global_luminous_count_ratio")
    ].iloc[0]
    zoom_dwarf = env[
        (env["tag"] == "zoom")
        & (env["observable"] == "matched_stellar_ratio_Mle_3e+10")
    ].iloc[0]
    zf_dwarf = env[
        (env["tag"] == "zoomfine")
        & (env["observable"] == "matched_stellar_ratio_Mle_3e+10")
    ].iloc[0]
    zoom_sigma = env[
        (env["tag"] == "zoom")
        & (env["observable"] == "half_mass_surface_density_ratio")
    ].iloc[0]

    signature = pd.DataFrame(
        [
            {
                "observable": "CMB lensing at L=3000",
                "refinement_to_cold_ratio": float(cmb["refinement_to_cold_ratio"]),
                "required_differential_boost_to_unity": float(
                    1.0 / cmb["refinement_to_cold_ratio"] - 1.0
                ),
                "status": "fixed linear projection",
            },
            {
                "observable": "nonlinear galaxy lensing z=0.5 ell=5000",
                "refinement_to_cold_ratio": float(
                    glens["nonlinear_halo_model_ratio"]
                ),
                "required_differential_boost_to_unity": float(
                    1.0 / glens["nonlinear_halo_model_ratio"] - 1.0
                ),
                "status": "controlled halo-model projection",
            },
            {
                "observable": "global luminous-halo count, zoom median",
                "refinement_to_cold_ratio": float(zoom_occ["median"]),
                "required_differential_boost_to_unity": float(
                    1.0 / zoom_occ["median"] - 1.0
                ),
                "status": "baryonic occupation envelope",
            },
            {
                "observable": "global luminous-halo count, time-control median",
                "refinement_to_cold_ratio": float(zf_occ["median"]),
                "required_differential_boost_to_unity": float(
                    1.0 / zf_occ["median"] - 1.0
                ),
                "status": "baryonic occupation envelope",
            },
            {
                "observable": "matched stellar proxy M<=3e10, zoom median",
                "refinement_to_cold_ratio": float(zoom_dwarf["median"]),
                "required_differential_boost_to_unity": float(
                    1.0 / zoom_dwarf["median"] - 1.0
                ),
                "status": "matched baryonic response envelope",
            },
            {
                "observable": "matched stellar proxy M<=3e10, time-control median",
                "refinement_to_cold_ratio": float(zf_dwarf["median"]),
                "required_differential_boost_to_unity": float(
                    1.0 / zf_dwarf["median"] - 1.0
                ),
                "status": "matched baryonic response envelope",
            },
            {
                "observable": "matched half-mass surface-density proxy",
                "refinement_to_cold_ratio": float(zoom_sigma["median"]),
                "required_differential_boost_to_unity": float(
                    1.0 / zoom_sigma["median"] - 1.0
                ),
                "status": "direct matched-halo proxy",
            },
            {
                "observable": "atomic-cooling collapsed fraction z=7.4",
                "refinement_to_cold_ratio": float(
                    z74["refinement_to_cold_fraction"]
                ),
                "required_differential_boost_to_unity": float(
                    z74["required_efficiency_penalty"] - 1.0
                ),
                "status": "controlled reionization consistency",
            },
        ]
    )
    signature.to_csv(DATA / "joint_falsification_signature.csv", index=False)

    # Host-neighborhood convergence summary.
    neigh_summary = (
        neigh.groupby(["tag", "radius_mpc_h"])["neighbor_ratio"]
        .agg(["min", "median", "max"])
        .reset_index()
    )
    neigh_summary.to_csv(DATA / "host_neighborhood_summary.csv", index=False)

    # Checks.
    def add(check_id: str, statement: str, value: float, passed: bool, tolerance: str) -> None:
        checks.append(
            {
                "id": check_id,
                "statement": statement,
                "value": float(value),
                "status": "PASS" if passed else "FAIL",
                "tolerance": tolerance,
            }
        )

    add("BRF01", "All occupation ratios are finite and positive", float(np.nanmin(occ["luminous_count_ratio"])), bool(np.isfinite(occ["luminous_count_ratio"]).all() and (occ["luminous_count_ratio"] > 0).all()), ">0")
    add("BRF02", "All global occupation ratios are below unity", float(np.nanmax(occ["luminous_count_ratio"])), bool((occ["luminous_count_ratio"] < 1).all()), "<1")
    add("BRF03", "Zoom median occupation ratio is suppressed", float(zoom_occ["median"]), bool(zoom_occ["median"] < 0.95), "<0.95")
    add("BRF04", "Time-control median occupation ratio is suppressed", float(zf_occ["median"]), bool(zf_occ["median"] < 0.95), "<0.95")
    add("BRF05", "Occupation median is time-control stable", abs(float(zoom_occ["median"] - zf_occ["median"])), bool(abs(float(zoom_occ["median"] - zf_occ["median"])) < 0.03), "<0.03")
    add("BRF06", "Total stellar response remains near cold", float(resp["total_stellar_ratio"].min()), bool(resp["total_stellar_ratio"].min() > 0.94), ">0.94")
    add("BRF07", "Near-cutoff matched stellar proxy is materially suppressed", float(zoom_dwarf["maximum"]), bool(zoom_dwarf["maximum"] < 0.60), "<0.60")
    add("BRF08", "Near-cutoff matched response is stable under time control", abs(float(zoom_dwarf["median"] - zf_dwarf["median"])), bool(abs(float(zoom_dwarf["median"] - zf_dwarf["median"])) < 0.03), "<0.03")
    zstruct = struct[struct["tag"] == "zoom"]
    add("BRF09", "Median half-mass surface density is suppressed", float(zstruct["half_mass_surface_density_ratio"].median()), bool(zstruct["half_mass_surface_density_ratio"].median() < 1), "<1")
    add("BRF10", "Most matched half-mass surface densities are suppressed", float((zstruct["half_mass_surface_density_ratio"] < 1).mean()), bool((zstruct["half_mass_surface_density_ratio"] < 1).mean() > 0.60), ">0.60")
    add("BRF11", "Median dynamical surface density is suppressed", float(zstruct["dynamical_surface_density_ratio"].median()), bool(zstruct["dynamical_surface_density_ratio"].median() < 1), "<1")
    add("BRF12", "Most robust matches have both mass and Vmax below cold", float(((zstruct["mass_ratio"] < 1) & (zstruct["vmax_ratio"] < 1)).mean()), bool(((zstruct["mass_ratio"] < 1) & (zstruct["vmax_ratio"] < 1)).mean() > 0.75), ">0.75")
    add("BRF13", "CMB lensing remains within one percent of cold", float(cmb["refinement_to_cold_ratio"]), bool(cmb["refinement_to_cold_ratio"] > 0.99), ">0.99")
    add("BRF14", "Nonlinear galaxy lensing remains within two percent of cold", float(glens["nonlinear_halo_model_ratio"]), bool(glens["nonlinear_halo_model_ratio"] > 0.98), ">0.98")
    add("BRF15", "Reionization collapsed fraction remains suppressed", float(z74["refinement_to_cold_fraction"]), bool(z74["refinement_to_cold_fraction"] < 0.50), "<0.50")
    add("BRF16", "Reionization requires greater than twofold efficiency", float(z74["required_efficiency_penalty"]), bool(z74["required_efficiency_penalty"] > 2.0), ">2")
    z1 = neigh_summary[(neigh_summary["tag"] == "zoom") & (neigh_summary["radius_mpc_h"] == 1.0)].iloc[0]
    zf1 = neigh_summary[(neigh_summary["tag"] == "zoomfine") & (neigh_summary["radius_mpc_h"] == 1.0)].iloc[0]
    add("BRF17", "Host-neighborhood envelope crosses or approaches unity", min(abs(float(z1["min"] - 1)), abs(float(zf1["min"] - 1))), bool(z1["min"] < 1.0 or zf1["min"] < 1.0), "boundary control")
    add("BRF18", "Host-neighborhood median is not time-control converged to five percent", abs(float(z1["median"] - zf1["median"])), bool(abs(float(z1["median"] - zf1["median"])) > 0.05), ">0.05 indicates open")
    add("BRF19", "No NaN in response envelopes", float(env.isna().sum().sum()), bool(env.isna().sum().sum() == 0), "0")
    add("BRF20", "All imported and derived signature ratios are finite", float(np.isfinite(signature["refinement_to_cold_ratio"]).mean()), bool(np.isfinite(signature["refinement_to_cold_ratio"]).all()), "1")

    checks_df = pd.DataFrame(checks)
    checks_df.to_csv(DATA / "baryonic_response_checks.csv", index=False)

    # Figures.
    for tag in TAGS:
        d = occ[occ["tag"] == tag]
        fig, ax = plt.subplots(figsize=(7.2, 4.5))
        for width in WIDTH_GRID:
            q = d[d["log_width"] == width]
            ax.plot(q["v50_kms"], q["luminous_count_ratio"], marker="o", label=f"width={width:g}")
        ax.axhline(1.0, linewidth=1.0)
        ax.set_xlabel(r"$V_{50}$ [km s$^{-1}$]")
        ax.set_ylabel("refinement / cold luminous count")
        ax.set_title(f"Luminous occupation envelope: {tag}")
        ax.legend(frameon=False, fontsize=8)
        fig.tight_layout()
        fig.savefig(FIG / f"luminous_occupation_{tag}.pdf")
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.2, 4.5))
    x = np.arange(len(MASS_CAPS), dtype=float)
    labels = [r"$3\times10^{10}$", r"$10^{11}$", r"$3\times10^{11}$", r"$10^{12}$", r"$10^{13}$"]
    for tag, marker in (("zoom", "o"), ("zoomfine", "s")):
        med = []
        lo = []
        hi = []
        for cap in MASS_CAPS:
            row = env[(env["tag"] == tag) & (env["observable"] == f"matched_stellar_ratio_Mle_{cap:.0e}")].iloc[0]
            med.append(row["median"])
            lo.append(row["minimum"])
            hi.append(row["maximum"])
        med = np.asarray(med); lo = np.asarray(lo); hi = np.asarray(hi)
        ax.plot(x, med, marker=marker, label=tag)
        ax.fill_between(x, lo, hi, alpha=0.18)
    ax.axhline(1.0, linewidth=1.0)
    ax.set_xticks(x, labels)
    ax.set_xlabel(r"maximum cold matched-halo mass [$h^{-1}M_\odot$]")
    ax.set_ylabel("median matched stellar-response ratio")
    ax.set_title("Baryonic response amplifies near-cutoff halo differences")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIG / "matched_stellar_response_envelope.pdf")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.2, 4.5))
    zs = struct[struct["tag"] == "zoom"]
    for col, label in (
        ("half_mass_surface_density_ratio", r"$M/r_{1/2}^2$"),
        ("dynamical_surface_density_ratio", r"$V_{\max}^2/r_{1/2}$"),
    ):
        vals = np.sort(zs[col].to_numpy())
        cdf = np.arange(1, len(vals) + 1) / len(vals)
        ax.plot(vals, cdf, label=label)
    ax.axvline(1.0, linewidth=1.0)
    ax.set_xlabel("refinement / cold structural proxy")
    ax.set_ylabel("empirical cumulative fraction")
    ax.set_title("Matched structural and lensing-proxy ratios")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIG / "matched_surface_density_cdf.pdf")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    plot_sig = signature.copy()
    y = np.arange(len(plot_sig))
    ax.barh(y, plot_sig["refinement_to_cold_ratio"])
    ax.axvline(1.0, linewidth=1.0)
    ax.set_yticks(y, [
        "CMB lensing",
        "nonlinear galaxy lensing",
        "luminous count",
        "luminous count control",
        "dwarf stellar proxy",
        "dwarf stellar control",
        "surface density proxy",
        "z=7.4 collapsed fraction",
    ])
    ax.set_xlabel("refinement / cold")
    ax.set_title("Frozen-parameter cross-observable signature")
    ax.invert_yaxis()
    fig.tight_layout()
    fig.savefig(FIG / "joint_falsification_signature.pdf")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.2, 4.5))
    for tag, marker in (("zoom", "o"), ("zoomfine", "s")):
        q = neigh_summary[neigh_summary["tag"] == tag]
        ax.errorbar(
            q["radius_mpc_h"],
            q["median"],
            yerr=[q["median"] - q["min"], q["max"] - q["median"]],
            marker=marker,
            capsize=3,
            label=tag,
        )
    ax.axhline(1.0, linewidth=1.0)
    ax.set_xlabel(r"host-neighborhood radius [$h^{-1}$ Mpc]")
    ax.set_ylabel("occupation-weighted neighbor ratio")
    ax.set_title("Host-centric satellite proxy remains unresolved")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIG / "host_neighborhood_control.pdf")
    plt.close(fig)

    summary = {
        "pass_count": int((checks_df["status"] == "PASS").sum()),
        "fail_count": int((checks_df["status"] == "FAIL").sum()),
        "zoom_luminous_envelope": {
            "min": float(zoom_occ["minimum"]),
            "median": float(zoom_occ["median"]),
            "max": float(zoom_occ["maximum"]),
        },
        "zoomfine_luminous_envelope": {
            "min": float(zf_occ["minimum"]),
            "median": float(zf_occ["median"]),
            "max": float(zf_occ["maximum"]),
        },
        "zoom_dwarf_stellar_envelope": {
            "min": float(zoom_dwarf["minimum"]),
            "median": float(zoom_dwarf["median"]),
            "max": float(zoom_dwarf["maximum"]),
        },
        "zoomfine_dwarf_stellar_envelope": {
            "min": float(zf_dwarf["minimum"]),
            "median": float(zf_dwarf["median"]),
            "max": float(zf_dwarf["maximum"]),
        },
        "zoom_surface_density_median": float(zoom_sigma["median"]),
        "cmb_lensing_ratio_L3000": float(cmb["refinement_to_cold_ratio"]),
        "nonlinear_galaxy_lensing_ratio_z0p5_ell5000": float(glens["nonlinear_halo_model_ratio"]),
        "reionization_collapsed_fraction_ratio_z7p4": float(z74["refinement_to_cold_fraction"]),
        "reionization_efficiency_penalty_z7p4": float(z74["required_efficiency_penalty"]),
        "sha256_inputs": {},
    }
    for path in sorted(INPUT.iterdir()):
        if path.is_file():
            summary["sha256_inputs"][path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    (DATA / "Baryonic_Response_Falsification_Verification.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit-only", action="store_true")
    _ = parser.parse_args()
    summary = build_outputs()
    print(json.dumps(summary, indent=2))
    if summary["fail_count"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
