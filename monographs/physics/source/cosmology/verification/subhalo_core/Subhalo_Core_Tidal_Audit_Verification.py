from __future__ import annotations

import itertools
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "inputs"
DATA = ROOT / "data"
SOURCE = ROOT / "source"
DATA.mkdir(parents=True, exist_ok=True)
SOURCE.mkdir(parents=True, exist_ok=True)

G = 4.30091e-9
RETURN_FRACTION = 0.4
TAGS = ("zoom", "zoomfine")


def _finite(x: pd.Series) -> pd.Series:
    return x.replace([np.inf, -np.inf], np.nan).dropna()


def luminous_probability(v: np.ndarray, v50: float, width: float) -> np.ndarray:
    v = np.maximum(np.asarray(v, dtype=float), 1.0e-9)
    return 1.0 / (1.0 + np.exp(-np.log(v / v50) / width))


def atomic_gate(v: np.ndarray, n_atomic: int) -> np.ndarray:
    v_atomic = 16.727527
    return 1.0 / (1.0 + (v_atomic / np.maximum(v, 1.0e-9)) ** (2 * n_atomic))


def photo_gate(v: np.ndarray, v_photo: float) -> np.ndarray:
    return 1.0 / (1.0 + (v_photo / np.maximum(v, 1.0e-9)) ** 4)


def stellar_efficiency(v: np.ndarray, v_feedback: float, beta: float, v_photo: float, n_atomic: int) -> np.ndarray:
    loading = (v_feedback / np.maximum(v, 1.0e-9)) ** beta
    return atomic_gate(v, n_atomic) * photo_gate(v, v_photo) * (1.0 - RETURN_FRACTION) / (
        1.0 - RETURN_FRACTION + loading
    )


def load_tag(tag: str) -> pd.DataFrame:
    core = pd.read_csv(INPUT / f"selfbound_{tag}.csv")
    peri = pd.read_csv(INPUT / f"subhalo_peri_{tag}.csv")
    key = ["cold_host", "ref_host", "cold_early", "ref_early"]
    peri = peri[key + ["cold_vrel", "ref_vrel", "cold_rperi", "ref_rperi", "cold_rperi_frac", "ref_rperi_frac"]]
    core = core.merge(peri, on=key, how="left", validate="one_to_one")
    for model, prefix in (("cold", "cold"), ("refinement", "ref")):
        cat = pd.read_csv(INPUT / f"halo_catalog_{tag}_{model}_a1.000.csv").set_index("halo_id")
        ids = core[f"{prefix}_host"].astype(int)
        core[f"{prefix}_host_mass"] = ids.map(cat["mass_msun_h"])
        core[f"{prefix}_host_r90"] = ids.map(cat["r90_mpc_h"])
    return core


def self_unbinding_demo(seed: int = 613) -> dict[str, object]:
    rng = np.random.default_rng(seed)
    n = 96
    pos = rng.normal(scale=0.025, size=(n, 3))
    vel = rng.normal(scale=18.0, size=(n, 3))
    vel[-16:] += rng.normal(loc=85.0, scale=8.0, size=(16, 3))
    particle_mass = 2.0e7
    active = np.arange(n, dtype=int)
    sizes = [len(active)]
    for _ in range(n + 1):
        if len(active) < 2:
            break
        p = pos[active]
        v = vel[active]
        center = np.median(p, axis=0)
        rr = np.linalg.norm(p - center, axis=1)
        inner = np.argsort(rr)[: max(4, len(active) // 2)]
        vmean = np.mean(v[inner], axis=0)
        order = np.argsort(rr)
        radius = np.maximum(rr[order], 1.0e-6)
        interior = particle_mass * np.arange(1, len(active) + 1) / radius
        exterior = np.cumsum((particle_mass / radius)[::-1])[::-1] - particle_mass / radius
        phi_sorted = -G * (interior + exterior)
        phi = np.empty(len(active))
        phi[order] = phi_sorted
        energy = 0.5 * np.sum((v - vmean) ** 2, axis=1) + phi
        new_active = active[energy < 0.0]
        sizes.append(len(new_active))
        if len(new_active) == len(active):
            active = new_active
            break
        active = new_active
    return {
        "initial": n,
        "final": int(len(active)),
        "iterations": len(sizes) - 1,
        "sizes": [int(x) for x in sizes],
        "nested": bool(np.all(np.diff(sizes) <= 0)),
        "terminated": bool(len(sizes) - 1 <= n),
    }


def branch_weights(
    df: pd.DataFrame,
    prefix: str,
    disk_fraction: float,
    disk_scale_fraction: float,
    kappa: float,
    shock_amplitude: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    mass = df[f"{prefix}_bound_mass"].to_numpy(float)
    rhalf = df[f"{prefix}_bound_rhalf"].to_numpy(float)
    vmax = df[f"{prefix}_bound_vmax"].to_numpy(float)
    nbound = df[f"{prefix}_bound_n"].to_numpy(float)
    radius = df[f"{prefix}_orbital_R"].to_numpy(float)
    host_enclosed = df[f"{prefix}_host_Menc"].to_numpy(float)
    host_mass = df[f"{prefix}_host_mass"].to_numpy(float)
    host_r90 = df[f"{prefix}_host_r90"].to_numpy(float)
    vrel = df[f"{prefix}_vrel"].to_numpy(float)

    disk_scale = np.maximum(disk_scale_fraction * host_r90, 1.0e-5)
    x = np.maximum(radius / disk_scale, 0.0)
    disk_mass = disk_fraction * host_mass
    disk_enclosed = disk_mass * (1.0 - (1.0 + x) * np.exp(-x))

    valid = (
        (nbound >= 8)
        & np.isfinite(mass)
        & (mass > 0)
        & np.isfinite(rhalf)
        & (rhalf > 0)
        & np.isfinite(radius)
        & (radius > 0)
        & np.isfinite(vrel)
        & (vrel > 0)
        & np.isfinite(vmax)
        & (vmax > 0)
    )

    tidal_radius = radius * (
        np.maximum(mass, 1.0e-30) / np.maximum(kappa * (host_enclosed + disk_enclosed), 1.0e-30)
    ) ** (1.0 / 3.0)
    tidal_weight = 1.0 / (1.0 + (2.0 * rhalf / np.maximum(tidal_radius, 1.0e-9)) ** 4)
    shock_parameter = (
        2.0
        * G
        * disk_enclosed
        * rhalf
        / (np.maximum(radius, 1.0e-6) ** 2 * np.maximum(vrel, 1.0) * np.maximum(vmax, 1.0))
    ) ** 2
    weight = tidal_weight * np.exp(-shock_amplitude * shock_parameter)
    return np.where(valid, weight, 0.0), vmax, mass, tidal_radius, shock_parameter


def build_scans(tag: str, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    gravity_grid = list(
        itertools.product(
            [0.0, 0.01, 0.03, 0.05],
            [0.03, 0.06, 0.10],
            [2.0, 3.0, 5.0],
            [0.0, 0.5, 1.0, 2.0],
        )
    )
    occupation_grid = list(itertools.product([15.0, 20.0, 25.0, 30.0, 40.0], [0.15, 0.25, 0.40, 0.60]))
    feedback_grid = list(itertools.product([40.0, 80.0, 100.0], [1.5, 2.5], [15.0, 25.0], [2, 4, 8]))

    gravity_rows: list[dict[str, float | str | int]] = []
    luminous_rows: list[dict[str, float | str | int]] = []
    stellar_rows: list[dict[str, float | str | int]] = []

    for gravity_id, (f_disk, r_disk, kappa, shock) in enumerate(gravity_grid):
        wc, vc, mc, rtc, xic = branch_weights(df, "cold", f_disk, r_disk, kappa, shock)
        wr, vr, mr, rtr, xir = branch_weights(df, "ref", f_disk, r_disk, kappa, shock)
        cold_sum = float(np.sum(wc))
        ref_sum = float(np.sum(wr))
        gravity_rows.append(
            {
                "tag": tag,
                "gravity_id": gravity_id,
                "fdisk": f_disk,
                "rdfrac": r_disk,
                "kappa": kappa,
                "shock_amplitude": shock,
                "cold_survival_weight": cold_sum,
                "ref_survival_weight": ref_sum,
                "survival_ratio": ref_sum / cold_sum,
                "cold_median_tidal_radius": float(np.nanmedian(rtc)),
                "ref_median_tidal_radius": float(np.nanmedian(rtr)),
                "cold_median_shock_parameter": float(np.nanmedian(xic)),
                "ref_median_shock_parameter": float(np.nanmedian(xir)),
            }
        )
        for occupation_id, (v50, width) in enumerate(occupation_grid):
            cold_count = float(np.sum(wc * luminous_probability(vc, v50, width)))
            ref_count = float(np.sum(wr * luminous_probability(vr, v50, width)))
            luminous_rows.append(
                {
                    "tag": tag,
                    "gravity_id": gravity_id,
                    "occupation_id": occupation_id,
                    "fdisk": f_disk,
                    "rdfrac": r_disk,
                    "kappa": kappa,
                    "shock_amplitude": shock,
                    "V50": v50,
                    "width": width,
                    "cold_luminous_weight": cold_count,
                    "ref_luminous_weight": ref_count,
                    "luminous_ratio": ref_count / cold_count,
                }
            )
        for feedback_id, (v_feedback, beta, v_photo, n_atomic) in enumerate(feedback_grid):
            cold_stellar = float(np.sum(wc * mc * stellar_efficiency(vc, v_feedback, beta, v_photo, n_atomic)))
            ref_stellar = float(np.sum(wr * mr * stellar_efficiency(vr, v_feedback, beta, v_photo, n_atomic)))
            stellar_rows.append(
                {
                    "tag": tag,
                    "gravity_id": gravity_id,
                    "feedback_id": feedback_id,
                    "fdisk": f_disk,
                    "rdfrac": r_disk,
                    "kappa": kappa,
                    "shock_amplitude": shock,
                    "Vfeedback": v_feedback,
                    "beta": beta,
                    "Vphoto": v_photo,
                    "natomic": n_atomic,
                    "cold_stellar_weight": cold_stellar,
                    "ref_stellar_weight": ref_stellar,
                    "stellar_ratio": ref_stellar / cold_stellar,
                }
            )
    return pd.DataFrame(gravity_rows), pd.DataFrame(luminous_rows), pd.DataFrame(stellar_rows)


def ratio_summary(series: pd.Series) -> dict[str, float]:
    x = _finite(series)
    return {
        "minimum": float(x.min()),
        "q16": float(x.quantile(0.16)),
        "median": float(x.median()),
        "q84": float(x.quantile(0.84)),
        "maximum": float(x.max()),
    }


def main() -> None:
    all_thresholds: list[dict[str, float | int | str]] = []
    all_summary: list[dict[str, float | int | str]] = []
    matched_rows: list[pd.DataFrame] = []
    gravity_all: list[pd.DataFrame] = []
    luminous_all: list[pd.DataFrame] = []
    stellar_all: list[pd.DataFrame] = []
    envelope_rows: list[dict[str, float | str]] = []
    proxy_rows: list[dict[str, float | str]] = []
    tag_metrics: dict[str, dict[str, float | int]] = {}

    for tag in TAGS:
        df = load_tag(tag)
        robust = df[(df["cold_bound_n"] >= 20) & (df["ref_bound_n"] >= 20)].copy()
        robust["tag"] = tag
        matched_rows.append(
            robust[
                [
                    "tag",
                    "cold_host",
                    "ref_host",
                    "cold_early",
                    "ref_early",
                    "jaccard_early",
                    "cold_bound_n",
                    "ref_bound_n",
                    "bound_mass_ratio",
                    "bound_rhalf_ratio",
                    "bound_vmax_ratio",
                    "bound_sigma_ratio",
                    "n_initial_ratio",
                    "n_to_host_ratio",
                    "cold_rperi_frac",
                    "ref_rperi_frac",
                ]
            ]
        )

        for threshold in (8, 16, 20, 32, 64, 128):
            for proxy, cold_col, ref_col in (
                ("self_bound", "cold_bound_n", "ref_bound_n"),
                ("hard_current_tidal", "cold_n_tidal", "ref_n_tidal"),
            ):
                cold_count = int(np.sum(df[cold_col] >= threshold))
                ref_count = int(np.sum(df[ref_col] >= threshold))
                all_thresholds.append(
                    {
                        "tag": tag,
                        "proxy": proxy,
                        "particle_threshold": threshold,
                        "cold_count": cold_count,
                        "refinement_count": ref_count,
                        "ratio": ref_count / cold_count if cold_count else np.nan,
                    }
                )

        summary_row: dict[str, float | int | str] = {
            "tag": tag,
            "candidate_pairs": int(len(df)),
            "robust_both_bound20": int(len(robust)),
            "cold_bound20": int(np.sum(df["cold_bound_n"] >= 20)),
            "refinement_bound20": int(np.sum(df["ref_bound_n"] >= 20)),
            "cold_hard_tidal20": int(np.sum(df["cold_n_tidal"] >= 20)),
            "refinement_hard_tidal20": int(np.sum(df["ref_n_tidal"] >= 20)),
            "minimum_jaccard": float(df["jaccard_early"].min()),
            "minimum_cold_descendant_fraction": float(df["cold_desc_fraction"].min()),
            "minimum_refinement_descendant_fraction": float(df["ref_desc_fraction"].min()),
        }
        for field in (
            "bound_mass_ratio",
            "bound_rhalf_ratio",
            "bound_vmax_ratio",
            "bound_sigma_ratio",
            "n_initial_ratio",
            "n_to_host_ratio",
        ):
            stats = ratio_summary(robust[field])
            for key, value in stats.items():
                summary_row[f"{field}_{key}"] = value
            summary_row[f"{field}_fraction_below_one"] = float(np.mean(robust[field] < 1.0))
        mass_ratio = float(summary_row["bound_mass_ratio_median"])
        radius_ratio = float(summary_row["bound_rhalf_ratio_median"])
        summary_row["compactness_compensation_factor"] = radius_ratio / mass_ratio ** (1.0 / 3.0)
        all_summary.append(summary_row)

        gravity, luminous, stellar = build_scans(tag, df)
        gravity_all.append(gravity)
        luminous_all.append(luminous)
        stellar_all.append(stellar)
        for observable, frame, field in (
            ("smooth_survival", gravity, "survival_ratio"),
            ("surviving_luminous_weight", luminous, "luminous_ratio"),
            ("surviving_stellar_weight", stellar, "stellar_ratio"),
        ):
            stats = ratio_summary(frame[field])
            envelope_rows.append({"tag": tag, "observable": observable, **stats})

        self_bound_ratio = summary_row["refinement_bound20"] / summary_row["cold_bound20"]
        hard_ratio = summary_row["refinement_hard_tidal20"] / summary_row["cold_hard_tidal20"]
        smooth_stats = ratio_summary(gravity["survival_ratio"])
        proxy_rows.extend(
            [
                {"tag": tag, "proxy": "self_bound_count_N20", "minimum": self_bound_ratio, "median": self_bound_ratio, "maximum": self_bound_ratio},
                {"tag": tag, "proxy": "hard_current_tidal_count_N20", "minimum": hard_ratio, "median": hard_ratio, "maximum": hard_ratio},
                {"tag": tag, "proxy": "smooth_tide_disk_envelope", "minimum": smooth_stats["minimum"], "median": smooth_stats["median"], "maximum": smooth_stats["maximum"]},
            ]
        )
        tag_metrics[tag] = {
            "candidate_pairs": int(len(df)),
            "robust_pairs": int(len(robust)),
            "bound_count_ratio_N20": float(self_bound_ratio),
            "hard_tidal_count_ratio_N20": float(hard_ratio),
            "mass_ratio_median": float(summary_row["bound_mass_ratio_median"]),
            "rhalf_ratio_median": float(summary_row["bound_rhalf_ratio_median"]),
            "vmax_ratio_median": float(summary_row["bound_vmax_ratio_median"]),
            "sigma_ratio_median": float(summary_row["bound_sigma_ratio_median"]),
            "compactness_factor": float(summary_row["compactness_compensation_factor"]),
            "smooth_survival_min": float(smooth_stats["minimum"]),
            "smooth_survival_median": float(smooth_stats["median"]),
            "smooth_survival_max": float(smooth_stats["maximum"]),
            "luminous_min": float(luminous["luminous_ratio"].min()),
            "luminous_median": float(luminous["luminous_ratio"].median()),
            "luminous_max": float(luminous["luminous_ratio"].max()),
            "stellar_min": float(stellar["stellar_ratio"].min()),
            "stellar_median": float(stellar["stellar_ratio"].median()),
            "stellar_max": float(stellar["stellar_ratio"].max()),
        }

    thresholds = pd.DataFrame(all_thresholds)
    summaries = pd.DataFrame(all_summary)
    matched = pd.concat(matched_rows, ignore_index=True)
    gravity_scan = pd.concat(gravity_all, ignore_index=True)
    luminous_scan = pd.concat(luminous_all, ignore_index=True)
    stellar_scan = pd.concat(stellar_all, ignore_index=True)
    envelopes = pd.DataFrame(envelope_rows)
    proxies = pd.DataFrame(proxy_rows)

    thresholds.to_csv(DATA / "subhalo_core_thresholds.csv", index=False)
    summaries.to_csv(DATA / "subhalo_core_summary.csv", index=False)
    matched.to_csv(DATA / "matched_core_ratios.csv", index=False)
    gravity_scan.to_csv(DATA / "tidal_survival_gravity_scan.csv", index=False)
    luminous_scan.to_csv(DATA / "tidal_survival_luminous_scan.csv", index=False)
    stellar_scan.to_csv(DATA / "tidal_survival_stellar_scan.csv", index=False)
    envelopes.to_csv(DATA / "tidal_survival_envelopes.csv", index=False)
    proxies.to_csv(DATA / "proxy_comparison.csv", index=False)

    demo = self_unbinding_demo()
    z = tag_metrics["zoom"]
    f = tag_metrics["zoomfine"]
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, value: object, criterion: str) -> None:
        checks.append({"check": name, "status": "PASS" if passed else "FAIL", "value": value, "criterion": criterion})

    check("candidate count zoom", z["candidate_pairs"] == 27, z["candidate_pairs"], "equals 27")
    check("candidate count time control", f["candidate_pairs"] == 27, f["candidate_pairs"], "equals 27")
    check("early overlap quality", float(summaries["minimum_jaccard"].min()) >= 0.2, float(summaries["minimum_jaccard"].min()), ">= 0.2")
    check(
        "descendant fraction quality",
        float(summaries[["minimum_cold_descendant_fraction", "minimum_refinement_descendant_fraction"]].min().min()) >= 0.5,
        float(summaries[["minimum_cold_descendant_fraction", "minimum_refinement_descendant_fraction"]].min().min()),
        ">= 0.5",
    )
    check("self-unbinding nested", bool(demo["nested"]), demo["sizes"], "nonincreasing active-set sizes")
    check("self-unbinding finite termination", bool(demo["terminated"]), demo["iterations"], "iterations <= initial particle count")
    check("self-bound N20 ratio zoom", abs(z["bound_count_ratio_N20"] - 23.0 / 24.0) < 1.0e-12, z["bound_count_ratio_N20"], "equals 23/24")
    check("self-bound N20 ratio time control", abs(f["bound_count_ratio_N20"] - 23.0 / 24.0) < 1.0e-12, f["bound_count_ratio_N20"], "equals 23/24")
    check("mass-ratio time stability", abs(z["mass_ratio_median"] - f["mass_ratio_median"]) < 0.01, abs(z["mass_ratio_median"] - f["mass_ratio_median"]), "< 0.01")
    check("radius-ratio time stability", abs(z["rhalf_ratio_median"] - f["rhalf_ratio_median"]) < 0.02, abs(z["rhalf_ratio_median"] - f["rhalf_ratio_median"]), "< 0.02")
    check("median mass below unity", z["mass_ratio_median"] < 1 and f["mass_ratio_median"] < 1, [z["mass_ratio_median"], f["mass_ratio_median"]], "both < 1")
    check("median radius below unity", z["rhalf_ratio_median"] < 1 and f["rhalf_ratio_median"] < 1, [z["rhalf_ratio_median"], f["rhalf_ratio_median"]], "both < 1")
    check("median Vmax close to unity", max(abs(z["vmax_ratio_median"] - 1), abs(f["vmax_ratio_median"] - 1)) < 0.02, [z["vmax_ratio_median"], f["vmax_ratio_median"]], "within 2 percent of unity")
    check("compactness compensation", z["compactness_factor"] < 1 and f["compactness_factor"] < 1, [z["compactness_factor"], f["compactness_factor"]], "both < 1")
    check("hard tidal proxy below unity", z["hard_tidal_count_ratio_N20"] < 1 and f["hard_tidal_count_ratio_N20"] < 1, [z["hard_tidal_count_ratio_N20"], f["hard_tidal_count_ratio_N20"]], "both < 1")
    check("smooth survival envelope above unity", z["smooth_survival_min"] > 1 and f["smooth_survival_min"] > 1, [z["smooth_survival_min"], f["smooth_survival_min"]], "both minima > 1")
    check("smooth survival time stability", abs(z["smooth_survival_median"] - f["smooth_survival_median"]) < 0.01, abs(z["smooth_survival_median"] - f["smooth_survival_median"]), "< 0.01")
    check("luminous envelope finite", bool(np.isfinite(luminous_scan["luminous_ratio"]).all()), [float(luminous_scan["luminous_ratio"].min()), float(luminous_scan["luminous_ratio"].max())], "all finite")
    check("stellar envelope finite", bool(np.isfinite(stellar_scan["stellar_ratio"]).all()), [float(stellar_scan["stellar_ratio"].min()), float(stellar_scan["stellar_ratio"].max())], "all finite")
    check("proxy sign disagreement", z["hard_tidal_count_ratio_N20"] < 1 < z["smooth_survival_min"] and f["hard_tidal_count_ratio_N20"] < 1 < f["smooth_survival_min"], True, "hard and smooth proxies straddle unity")

    checks_df = pd.DataFrame(checks)
    checks_df.to_csv(DATA / "subhalo_core_checks.csv", index=False)
    passed = int(np.sum(checks_df["status"] == "PASS"))
    failed = int(np.sum(checks_df["status"] == "FAIL"))
    result = {
        "title": "Lagrangian Subhalo Cores, Self-Unbinding, and Tidal Survival Audit",
        "tags": tag_metrics,
        "self_unbinding_demo": demo,
        "scan_rows": {
            "gravity": int(len(gravity_scan)),
            "luminous": int(len(luminous_scan)),
            "stellar": int(len(stellar_scan)),
        },
        "checks": checks,
        "pass_count": passed,
        "fail_count": failed,
    }
    (DATA / "Subhalo_Core_Tidal_Audit_Verification.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    def macro(name: str, value: str) -> str:
        return f"\\newcommand{{\\{name}}}{{{value}}}\n"

    lines = [
        macro("SCTPass", str(passed)),
        macro("SCTFail", str(failed)),
        macro("SCTCandidates", str(z["candidate_pairs"])),
        macro("SCTRobust", str(z["robust_pairs"])),
        macro("SCTBoundRatio", f"{z['bound_count_ratio_N20']:.6f}"),
        macro("SCTBoundMassZoom", f"{z['mass_ratio_median']:.6f}"),
        macro("SCTBoundMassFine", f"{f['mass_ratio_median']:.6f}"),
        macro("SCTRhalfZoom", f"{z['rhalf_ratio_median']:.6f}"),
        macro("SCTRhalfFine", f"{f['rhalf_ratio_median']:.6f}"),
        macro("SCTVmaxZoom", f"{z['vmax_ratio_median']:.6f}"),
        macro("SCTVmaxFine", f"{f['vmax_ratio_median']:.6f}"),
        macro("SCTHardZoom", f"{z['hard_tidal_count_ratio_N20']:.6f}"),
        macro("SCTHardFine", f"{f['hard_tidal_count_ratio_N20']:.6f}"),
        macro("SCTSmoothZoomMin", f"{z['smooth_survival_min']:.6f}"),
        macro("SCTSmoothZoomMed", f"{z['smooth_survival_median']:.6f}"),
        macro("SCTSmoothZoomMax", f"{z['smooth_survival_max']:.6f}"),
        macro("SCTSmoothFineMin", f"{f['smooth_survival_min']:.6f}"),
        macro("SCTSmoothFineMed", f"{f['smooth_survival_median']:.6f}"),
        macro("SCTSmoothFineMax", f"{f['smooth_survival_max']:.6f}"),
        macro("SCTLumZoomMin", f"{z['luminous_min']:.6f}"),
        macro("SCTLumZoomMed", f"{z['luminous_median']:.6f}"),
        macro("SCTLumZoomMax", f"{z['luminous_max']:.6f}"),
        macro("SCTLumFineMin", f"{f['luminous_min']:.6f}"),
        macro("SCTLumFineMed", f"{f['luminous_median']:.6f}"),
        macro("SCTLumFineMax", f"{f['luminous_max']:.6f}"),
        macro("SCTStellarZoomMin", f"{z['stellar_min']:.6f}"),
        macro("SCTStellarZoomMed", f"{z['stellar_median']:.6f}"),
        macro("SCTStellarZoomMax", f"{z['stellar_max']:.6f}"),
        macro("SCTStellarFineMin", f"{f['stellar_min']:.6f}"),
        macro("SCTStellarFineMed", f"{f['stellar_median']:.6f}"),
        macro("SCTStellarFineMax", f"{f['stellar_max']:.6f}"),
        macro("SCTCompactZoom", f"{z['compactness_factor']:.6f}"),
        macro("SCTCompactFine", f"{f['compactness_factor']:.6f}"),
    ]
    (SOURCE / "generated_macros.tex").write_text("".join(lines), encoding="utf-8")

    print(json.dumps({"pass": passed, "fail": failed, "tags": tag_metrics}, indent=2))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
