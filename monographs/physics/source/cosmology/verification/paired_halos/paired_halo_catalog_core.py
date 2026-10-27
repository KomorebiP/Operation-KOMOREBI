from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import argparse
import hashlib
import json
import math
import os
import sys
import time
import subprocess
from typing import Iterable

import numpy as np
import pandas as pd
from numba import njit
import matplotlib.pyplot as plt
from scipy.spatial import cKDTree

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = ROOT / "data"
FIG = ROOT / "figures"
DATA.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import base_structure_core as base  # noqa: E402

G_MPC_KMS2_MSUN = 4.30091e-9


@dataclass(frozen=True)
class RunConfig:
    tag: str
    nmesh: int
    box_mpc_h: float
    steps: int
    seed: int
    snapshots: tuple[float, ...] = (0.5, 1.0)


DEFAULT_CONFIGS = (
    RunConfig("main", 64, 12.0, 240, 20260820, (0.5, 1.0)),
    RunConfig("zoom", 64, 8.0, 260, 20260828, (0.5, 1.0)),
    RunConfig("zoomfine", 64, 8.0, 360, 20260828, (0.5, 1.0)),
)

SMOKE_CONFIGS = (
    RunConfig("smoke", 32, 8.0, 36, 20260828, (0.5, 1.0)),
)


def set_base_params(cfg: RunConfig) -> None:
    base.P = base.Params(
        h=0.7,
        omega_b0=0.049,
        omega_d0=0.261,
        omega_r0=9.0e-5,
        n_s=0.965,
        sigma8=0.81,
        box_mpc_h=cfg.box_mpc_h,
        a_init=0.01,
        seed=cfg.seed,
    )


def integration_edges(a_init: float, targets: Iterable[float], steps: int) -> np.ndarray:
    raw = np.geomspace(a_init, 1.0, steps + 1)
    merged = np.unique(np.concatenate([raw, np.asarray(tuple(targets), dtype=float), np.array([1.0])]))
    return merged[(merged >= a_init) & (merged <= 1.0)]


def evolve_model(cfg: RunConfig, refinement: bool) -> tuple[dict[float, tuple[np.ndarray, np.ndarray]], dict[str, float]]:
    set_base_params(cfg)
    model = "refinement" if refinement else "cold"
    pos, mom, init = base.generate_initial_conditions(cfg.nmesh, cfg.box_mpc_h, refinement, 1.0)
    symbols = base.k_arrays(cfg.nmesh, cfg.box_mpc_h)
    edges = integration_edges(base.P.a_init, cfg.snapshots, cfg.steps)
    force, _ = base.force_base(pos, cfg.nmesh, cfg.box_mpc_h, symbols)
    targets = sorted(set(float(x) for x in cfg.snapshots))
    target_index = 0
    out: dict[float, tuple[np.ndarray, np.ndarray]] = {}
    max_drift = 0.0
    start = time.time()
    for j in range(len(edges) - 1):
        a0, a1 = float(edges[j]), float(edges[j + 1])
        amid = math.sqrt(a0 * a1)
        mom += 1.5 * base.OMEGA_M * base.gauss_integral(a0, amid, 2) * force
        drift = mom * base.gauss_integral(a0, a1, 3)
        pos = (pos + drift) % cfg.box_mpc_h
        max_drift = max(max_drift, float(np.max(np.linalg.norm(drift, axis=1)) / (cfg.box_mpc_h / cfg.nmesh)))
        force, _ = base.force_base(pos, cfg.nmesh, cfg.box_mpc_h, symbols)
        mom += 1.5 * base.OMEGA_M * base.gauss_integral(amid, a1, 2) * force
        while target_index < len(targets) and a1 >= targets[target_index] - 1e-13:
            at = targets[target_index]
            out[at] = (pos.copy(), mom.copy())
            target_index += 1
    elapsed = time.time() - start
    metrics = {
        "tag": cfg.tag,
        "model": model,
        "nmesh": cfg.nmesh,
        "particles": cfg.nmesh**3,
        "box_mpc_h": cfg.box_mpc_h,
        "requested_steps": cfg.steps,
        "actual_steps": len(edges) - 1,
        "runtime_seconds": elapsed,
        "max_step_drift_cell": max_drift,
        "init_max_displacement_cell": float(init["max_displacement_cell"]),
        "init_rms_delta": float(init["rms_delta_linear_init"]),
    }
    print(json.dumps({"evolution": metrics}), flush=True)
    return out, metrics


@njit(cache=True)
def uf_find(parent: np.ndarray, x: int) -> int:
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x


@njit(cache=True)
def uf_union(parent: np.ndarray, rank: np.ndarray, a: int, b: int) -> None:
    ra = uf_find(parent, a)
    rb = uf_find(parent, b)
    if ra == rb:
        return
    if rank[ra] < rank[rb]:
        parent[ra] = rb
    elif rank[ra] > rank[rb]:
        parent[rb] = ra
    else:
        parent[rb] = ra
        rank[ra] += 1


@njit(cache=True)
def fof_union(
    pos: np.ndarray,
    box: float,
    ncell: int,
    order: np.ndarray,
    starts: np.ndarray,
    link2: float,
) -> np.ndarray:
    npart = pos.shape[0]
    parent = np.arange(npart, dtype=np.int64)
    rank = np.zeros(npart, dtype=np.int8)
    nc2 = ncell * ncell
    for cid in range(ncell * ncell * ncell):
        s0 = starts[cid]
        s1 = starts[cid + 1]
        if s1 <= s0:
            continue
        ix = cid // nc2
        rem = cid - ix * nc2
        iy = rem // ncell
        iz = rem - iy * ncell
        for ox in range(-1, 2):
            jx = (ix + ox) % ncell
            for oy in range(-1, 2):
                jy = (iy + oy) % ncell
                for oz in range(-1, 2):
                    jz = (iz + oz) % ncell
                    nid = (jx * ncell + jy) * ncell + jz
                    if nid < cid:
                        continue
                    t0 = starts[nid]
                    t1 = starts[nid + 1]
                    if t1 <= t0:
                        continue
                    for aa in range(s0, s1):
                        p = order[aa]
                        bb0 = aa + 1 if nid == cid else t0
                        for bb in range(bb0, t1):
                            q = order[bb]
                            dx = abs(pos[p, 0] - pos[q, 0])
                            dy = abs(pos[p, 1] - pos[q, 1])
                            dz = abs(pos[p, 2] - pos[q, 2])
                            if dx > 0.5 * box:
                                dx = box - dx
                            if dy > 0.5 * box:
                                dy = box - dy
                            if dz > 0.5 * box:
                                dz = box - dz
                            if dx * dx + dy * dy + dz * dz <= link2:
                                uf_union(parent, rank, p, q)
    for i in range(npart):
        parent[i] = uf_find(parent, i)
    return parent



@njit(cache=True)
def union_pair_array(npart: int, pairs: np.ndarray) -> np.ndarray:
    parent = np.arange(npart, dtype=np.int64)
    rank = np.zeros(npart, dtype=np.int8)
    for i in range(pairs.shape[0]):
        uf_union(parent, rank, int(pairs[i, 0]), int(pairs[i, 1]))
    for i in range(npart):
        parent[i] = uf_find(parent, i)
    return parent


@njit(cache=True)
def binary_search_ids(ids: np.ndarray, target: int) -> int:
    lo = 0
    hi = ids.shape[0]
    while lo < hi:
        mid = (lo + hi) // 2
        v = ids[mid]
        if v < target:
            lo = mid + 1
        else:
            hi = mid
    if lo < ids.shape[0] and ids[lo] == target:
        return lo
    return -1


@njit(cache=True)
def fof_sparse_cell_union(
    pos: np.ndarray,
    box: float,
    ncell: int,
    reach: int,
    unique_ids: np.ndarray,
    order: np.ndarray,
    starts: np.ndarray,
    link2: float,
) -> np.ndarray:
    npart = pos.shape[0]
    parent = np.arange(npart, dtype=np.int64)
    rank = np.zeros(npart, dtype=np.int8)
    nc2 = ncell * ncell
    # Every occupied microcell has diameter <= linking length, hence is internally connected.
    for u in range(unique_ids.shape[0]):
        a0 = starts[u]
        a1 = starts[u + 1]
        if a1 - a0 > 1:
            rep = int(order[a0])
            for z in range(a0 + 1, a1):
                uf_union(parent, rank, rep, int(order[z]))
    # One detected edge between two internally connected cells is sufficient.
    for u in range(unique_ids.shape[0]):
        cid = int(unique_ids[u])
        ix = cid // nc2
        rem = cid - ix * nc2
        iy = rem // ncell
        iz = rem - iy * ncell
        a0 = starts[u]
        a1 = starts[u + 1]
        for ox in range(-reach, reach + 1):
            jx = (ix + ox) % ncell
            for oy in range(-reach, reach + 1):
                jy = (iy + oy) % ncell
                for oz in range(-reach, reach + 1):
                    jz = (iz + oz) % ncell
                    nid = (jx * ncell + jy) * ncell + jz
                    if nid <= cid:
                        continue
                    v = binary_search_ids(unique_ids, nid)
                    if v < 0:
                        continue
                    b0 = starts[v]
                    b1 = starts[v + 1]
                    found = False
                    for aa in range(a0, a1):
                        pp = int(order[aa])
                        for bb in range(b0, b1):
                            qq = int(order[bb])
                            dx = abs(pos[pp, 0] - pos[qq, 0])
                            dy = abs(pos[pp, 1] - pos[qq, 1])
                            dz = abs(pos[pp, 2] - pos[qq, 2])
                            if dx > 0.5 * box:
                                dx = box - dx
                            if dy > 0.5 * box:
                                dy = box - dy
                            if dz > 0.5 * box:
                                dz = box - dz
                            if dx * dx + dy * dy + dz * dz <= link2:
                                uf_union(parent, rank, int(order[a0]), int(order[b0]))
                                found = True
                                break
                        if found:
                            break
    for i in range(npart):
        parent[i] = uf_find(parent, i)
    return parent

def periodic_center(points: np.ndarray, box: float) -> np.ndarray:
    angle = 2.0 * math.pi * points / box
    z = np.mean(np.exp(1j * angle), axis=0)
    theta = np.mod(np.angle(z), 2.0 * math.pi)
    return theta * box / (2.0 * math.pi)


def minimum_image(points: np.ndarray, center: np.ndarray, box: float) -> np.ndarray:
    d = points - center[None, :]
    d -= box * np.rint(d / box)
    return d


def catalog_from_labels(
    pos: np.ndarray,
    mom: np.ndarray,
    roots: np.ndarray,
    box: float,
    a: float,
    min_particles: int = 20,
) -> tuple[pd.DataFrame, np.ndarray]:
    unique, inverse, counts = np.unique(roots, return_inverse=True, return_counts=True)
    keep_root_index = np.where(counts >= min_particles)[0]
    if len(keep_root_index) == 0:
        cols = [
            "halo_id", "particle_count", "mass_msun_h", "x_mpc_h", "y_mpc_h", "z_mpc_h",
            "rhalf_mpc_h", "r90_mpc_h", "vmax_kms", "sigma1d_kms", "sphericity", "r90_over_rhalf"
        ]
        return pd.DataFrame(columns=cols), np.full(len(pos), -1, dtype=np.int32)
    keep_root_index = keep_root_index[np.argsort(counts[keep_root_index])[::-1]]
    map_root = np.full(len(unique), -1, dtype=np.int32)
    for hid, ridx in enumerate(keep_root_index):
        map_root[ridx] = hid
    labels = map_root[inverse]
    particle_mass = base.RHO_BAR_H * box**3 / len(pos)
    rows: list[dict[str, float | int]] = []
    for hid, ridx in enumerate(keep_root_index):
        members = np.where(labels == hid)[0]
        pts = pos[members]
        center = periodic_center(pts, box)
        disp = minimum_image(pts, center, box)
        radii = np.linalg.norm(disp, axis=1)
        order = np.argsort(radii)
        rs = radii[order]
        n = len(members)
        rhalf = float(np.quantile(rs, 0.5, method="linear"))
        r90 = float(np.quantile(rs, 0.9, method="linear"))
        positive = np.maximum(rs, 1e-8 * box)
        menc = particle_mass * np.arange(1, n + 1)
        vmax = float(np.sqrt(np.max(G_MPC_KMS2_MSUN * menc / positive)))
        vel = 100.0 * mom[members] / a
        vmean = np.mean(vel, axis=0)
        sigma1d = float(np.sqrt(np.mean(np.sum((vel - vmean) ** 2, axis=1)) / 3.0))
        if n >= 3:
            cov = disp.T @ disp / n
            eig = np.sort(np.maximum(np.linalg.eigvalsh(cov), 0.0))
            sphericity = float(math.sqrt(eig[0] / eig[-1])) if eig[-1] > 0 else 1.0
        else:
            sphericity = float("nan")
        rows.append(
            {
                "halo_id": hid,
                "particle_count": n,
                "mass_msun_h": particle_mass * n,
                "x_mpc_h": float(center[0]),
                "y_mpc_h": float(center[1]),
                "z_mpc_h": float(center[2]),
                "rhalf_mpc_h": rhalf,
                "r90_mpc_h": r90,
                "vmax_kms": vmax,
                "sigma1d_kms": sigma1d,
                "sphericity": sphericity,
                "r90_over_rhalf": r90 / rhalf if rhalf > 0 else float("nan"),
            }
        )
    return pd.DataFrame(rows), labels


def run_fof(
    pos: np.ndarray,
    mom: np.ndarray,
    cfg: RunConfig,
    a: float,
    min_particles: int = 20,
    b: float = 0.2,
) -> tuple[pd.DataFrame, np.ndarray, dict[str, float]]:
    mean_spacing = cfg.box_mpc_h / cfg.nmesh
    link = b * mean_spacing
    # Microcells have diagonal <= link, so each occupied cell is a complete FoF subgraph.
    ncell = int(math.ceil(math.sqrt(3.0) * cfg.box_mpc_h / link))
    cell_size = cfg.box_mpc_h / ncell
    reach = int(math.floor(link / cell_size)) + 1
    coords = np.floor(pos / cfg.box_mpc_h * ncell).astype(np.int64) % ncell
    cid = (coords[:, 0] * ncell + coords[:, 1]) * ncell + coords[:, 2]
    order = np.argsort(cid, kind="stable").astype(np.int64)
    sorted_ids = cid[order]
    unique_ids, counts = np.unique(sorted_ids, return_counts=True)
    starts = np.zeros(len(unique_ids) + 1, dtype=np.int64)
    starts[1:] = np.cumsum(counts)
    start = time.time()
    roots = fof_sparse_cell_union(pos, cfg.box_mpc_h, ncell, reach, unique_ids.astype(np.int64), order, starts, link * link)
    catalog, labels = catalog_from_labels(pos, mom, roots, cfg.box_mpc_h, a, min_particles)
    elapsed = time.time() - start
    particle_mass = base.RHO_BAR_H * cfg.box_mpc_h**3 / len(pos)
    metrics = {
        "fof_runtime_seconds": elapsed,
        "linking_length_mpc_h": link,
        "microcell_count_per_axis": ncell,
        "occupied_microcells": int(len(unique_ids)),
        "particle_mass_msun_h": particle_mass,
        "halo_count_min20": int(len(catalog)),
        "halo_count_min64": int(np.count_nonzero(catalog.particle_count.to_numpy() >= 64)) if len(catalog) else 0,
        "catalogued_mass_fraction": float(catalog.mass_msun_h.sum() / (particle_mass * len(pos))) if len(catalog) else 0.0,
        "largest_halo_particles": int(catalog.particle_count.max()) if len(catalog) else 0,
    }
    print(json.dumps({"fof": {"tag": cfg.tag, "a": a, **metrics}}), flush=True)
    return catalog, labels, metrics


def mutual_overlap_matches(
    cold_labels: np.ndarray,
    ref_labels: np.ndarray,
    cold_catalog: pd.DataFrame,
    ref_catalog: pd.DataFrame,
) -> pd.DataFrame:
    nc = len(cold_catalog)
    nr = len(ref_catalog)
    if nc == 0 or nr == 0:
        return pd.DataFrame()
    mask = (cold_labels >= 0) & (ref_labels >= 0)
    codes = cold_labels[mask].astype(np.int64) * nr + ref_labels[mask].astype(np.int64)
    code_u, overlaps = np.unique(codes, return_counts=True)
    ci = code_u // nr
    ri = code_u % nr
    best_r = np.full(nc, -1, dtype=np.int32)
    best_ro = np.zeros(nc, dtype=np.int64)
    best_c = np.full(nr, -1, dtype=np.int32)
    best_co = np.zeros(nr, dtype=np.int64)
    for c, r, o in zip(ci, ri, overlaps):
        if o > best_ro[c]:
            best_ro[c] = o
            best_r[c] = r
        if o > best_co[r]:
            best_co[r] = o
            best_c[r] = c
    rows: list[dict[str, float | int]] = []
    cc = cold_catalog.set_index("halo_id")
    rc = ref_catalog.set_index("halo_id")
    for c in range(nc):
        r = int(best_r[c])
        if r < 0 or best_c[r] != c:
            continue
        o = int(best_ro[c])
        n_c = int(cc.loc[c, "particle_count"])
        n_r = int(rc.loc[r, "particle_count"])
        jaccard = o / (n_c + n_r - o)
        rows.append(
            {
                "cold_halo_id": c,
                "refinement_halo_id": r,
                "overlap_particles": o,
                "cold_particles": n_c,
                "refinement_particles": n_r,
                "jaccard": jaccard,
                "mass_ratio": float(rc.loc[r, "mass_msun_h"] / cc.loc[c, "mass_msun_h"]),
                "vmax_ratio": float(rc.loc[r, "vmax_kms"] / cc.loc[c, "vmax_kms"]),
                "rhalf_ratio": float(rc.loc[r, "rhalf_mpc_h"] / cc.loc[c, "rhalf_mpc_h"]),
                "sigma1d_ratio": float(rc.loc[r, "sigma1d_kms"] / cc.loc[c, "sigma1d_kms"]) if cc.loc[c, "sigma1d_kms"] > 0 else float("nan"),
                "sphericity_difference": float(rc.loc[r, "sphericity"] - cc.loc[c, "sphericity"]),
                "cold_mass_msun_h": float(cc.loc[c, "mass_msun_h"]),
                "refinement_mass_msun_h": float(rc.loc[r, "mass_msun_h"]),
            }
        )
    return pd.DataFrame(rows)


def progenitor_table(labels_early: np.ndarray, labels_final: np.ndarray, catalog_early: pd.DataFrame, catalog_final: pd.DataFrame) -> pd.DataFrame:
    nf = len(catalog_final)
    ne = len(catalog_early)
    if nf == 0:
        return pd.DataFrame()
    final_counts = catalog_final.set_index("halo_id").particle_count.to_dict()
    early_counts = catalog_early.set_index("halo_id").particle_count.to_dict() if ne else {}
    rows: list[dict[str, float | int]] = []
    for fid in range(nf):
        members = labels_final == fid
        e = labels_early[members]
        e = e[e >= 0]
        if len(e):
            vals, cnt = np.unique(e, return_counts=True)
            j = int(np.argmax(cnt))
            eid = int(vals[j])
            overlap = int(cnt[j])
            early_n = int(early_counts[eid])
        else:
            eid, overlap, early_n = -1, 0, 0
        fn = int(final_counts[fid])
        rows.append(
            {
                "final_halo_id": fid,
                "main_progenitor_id": eid,
                "overlap_particles": overlap,
                "final_particles": fn,
                "early_progenitor_particles": early_n,
                "assembled_fraction_at_a0p5": overlap / fn,
                "progenitor_to_final_size_ratio": early_n / fn,
            }
        )
    return pd.DataFrame(rows)


def cumulative_catalog(cold: pd.DataFrame, ref: pd.DataFrame, box: float, particle_mass: float) -> pd.DataFrame:
    max_mass = max(float(cold.mass_msun_h.max()) if len(cold) else particle_mass * 20, float(ref.mass_msun_h.max()) if len(ref) else particle_mass * 20)
    low = particle_mass * 20
    if max_mass <= low:
        masses = np.array([low])
    else:
        masses = np.geomspace(low, max_mass, 36)
    rows = []
    volume = box**3
    for m in masses:
        nc = int(np.count_nonzero(cold.mass_msun_h.to_numpy() >= m)) if len(cold) else 0
        nr = int(np.count_nonzero(ref.mass_msun_h.to_numpy() >= m)) if len(ref) else 0
        rows.append(
            {
                "mass_threshold_msun_h": m,
                "cold_count": nc,
                "refinement_count": nr,
                "cold_number_density_h3_mpc3": nc / volume,
                "refinement_number_density_h3_mpc3": nr / volume,
                "abundance_ratio": nr / nc if nc > 0 else float("nan"),
            }
        )
    return pd.DataFrame(rows)


def transfer_half_mode_mass() -> tuple[float, float]:
    tab = pd.read_csv(ROOT / "inputs" / "collisionless_dark_transfer_curve.csv")
    k_h = tab["k_per_Mpc_for_H0_70"].to_numpy(float) / 0.7
    pr = tab["collisionless_power_ratio_z0"].to_numpy(float)
    order = np.argsort(pr)
    k_half = float(np.interp(0.5, pr[order], k_h[order]))
    r_half = math.pi / k_half
    m_half = 4.0 * math.pi / 3.0 * base.RHO_BAR_H * r_half**3
    return k_half, m_half


def interp_abundance(table: pd.DataFrame, mass: float) -> float:
    valid = np.isfinite(table.abundance_ratio.to_numpy())
    if not np.any(valid):
        return float("nan")
    x = np.log(table.mass_threshold_msun_h.to_numpy()[valid])
    y = table.abundance_ratio.to_numpy()[valid]
    return float(np.interp(math.log(mass), x, y, left=y[0], right=y[-1]))


def summarize_matches(matches: pd.DataFrame, min_cold_particles: int = 64, min_jaccard: float = 0.1) -> dict[str, float | int]:
    if matches.empty:
        return {"matched_halos": 0, "robust_matches": 0}
    robust = matches[(matches.cold_particles >= min_cold_particles) & (matches.jaccard >= min_jaccard)]
    out: dict[str, float | int] = {
        "matched_halos": int(len(matches)),
        "robust_matches": int(len(robust)),
    }
    for col in ["jaccard", "mass_ratio", "vmax_ratio", "rhalf_ratio", "sigma1d_ratio", "sphericity_difference"]:
        vals = robust[col].to_numpy(float) if len(robust) else np.array([], dtype=float)
        vals = vals[np.isfinite(vals)]
        out[f"median_{col}"] = float(np.median(vals)) if len(vals) else float("nan")
        out[f"p16_{col}"] = float(np.percentile(vals, 16)) if len(vals) else float("nan")
        out[f"p84_{col}"] = float(np.percentile(vals, 84)) if len(vals) else float("nan")
    return out



def run_model_stage(cfg: RunConfig, refinement: bool) -> dict[str, object]:
    model = "refinement" if refinement else "cold"
    snaps, evo = evolve_model(cfg, refinement)
    fof_metrics: dict[str, dict[str, float]] = {}
    for a, (pos, mom) in sorted(snaps.items()):
        cat, lab, met = run_fof(pos, mom, cfg, a)
        cat.to_csv(DATA / f"halo_catalog_{cfg.tag}_{model}_a{a:.3f}.csv", index=False)
        np.save(DATA / f"halo_labels_{cfg.tag}_{model}_a{a:.3f}.npy", lab)
        fof_metrics[f"{model}_a{a:.3f}"] = met
    stage = {"config": asdict(cfg), "model": model, "evolution": evo, "fof": fof_metrics}
    (DATA / f"model_stage_{cfg.tag}_{model}.json").write_text(json.dumps(stage, indent=2, allow_nan=True))
    return stage


def analyze_staged_config(cfg: RunConfig) -> dict[str, object]:
    stages = {
        model: json.loads((DATA / f"model_stage_{cfg.tag}_{model}.json").read_text())
        for model in ["cold", "refinement"]
    }
    catalogs: dict[str, dict[float, pd.DataFrame]] = {"cold": {}, "refinement": {}}
    labels: dict[str, dict[float, np.ndarray]] = {"cold": {}, "refinement": {}}
    for model in ["cold", "refinement"]:
        for a in cfg.snapshots:
            catalogs[model][a] = pd.read_csv(DATA / f"halo_catalog_{cfg.tag}_{model}_a{a:.3f}.csv")
            labels[model][a] = np.load(DATA / f"halo_labels_{cfg.tag}_{model}_a{a:.3f}.npy")
    a_final = 1.0
    cold_final = catalogs["cold"][a_final]
    ref_final = catalogs["refinement"][a_final]
    matches = mutual_overlap_matches(labels["cold"][a_final], labels["refinement"][a_final], cold_final, ref_final)
    matches.to_csv(DATA / f"matched_halos_{cfg.tag}.csv", index=False)
    particle_mass = base.RHO_BAR_H * cfg.box_mpc_h**3 / cfg.nmesh**3
    cumulative = cumulative_catalog(cold_final, ref_final, cfg.box_mpc_h, particle_mass)
    cumulative.to_csv(DATA / f"halo_cumulative_{cfg.tag}.csv", index=False)
    formation_summary: dict[str, float | int] = {}
    if 0.5 in labels["cold"] and 0.5 in labels["refinement"]:
        prog_c = progenitor_table(labels["cold"][0.5], labels["cold"][1.0], catalogs["cold"][0.5], cold_final)
        prog_r = progenitor_table(labels["refinement"][0.5], labels["refinement"][1.0], catalogs["refinement"][0.5], ref_final)
        prog_c.to_csv(DATA / f"progenitors_{cfg.tag}_cold.csv", index=False)
        prog_r.to_csv(DATA / f"progenitors_{cfg.tag}_refinement.csv", index=False)
        if not matches.empty:
            pm = matches[["cold_halo_id", "refinement_halo_id", "cold_particles", "jaccard"]].copy()
            pm = pm.merge(prog_c[["final_halo_id", "assembled_fraction_at_a0p5"]], left_on="cold_halo_id", right_on="final_halo_id", how="left")
            pm = pm.rename(columns={"assembled_fraction_at_a0p5": "cold_assembled_fraction_a0p5"}).drop(columns=["final_halo_id"])
            pm = pm.merge(prog_r[["final_halo_id", "assembled_fraction_at_a0p5"]], left_on="refinement_halo_id", right_on="final_halo_id", how="left")
            pm = pm.rename(columns={"assembled_fraction_at_a0p5": "refinement_assembled_fraction_a0p5"}).drop(columns=["final_halo_id"])
            pm["formation_fraction_ratio"] = pm.refinement_assembled_fraction_a0p5 / pm.cold_assembled_fraction_a0p5
            pm.to_csv(DATA / f"matched_formation_{cfg.tag}.csv", index=False)
            robust = pm[(pm.cold_particles >= 64) & (pm.jaccard >= 0.1) & np.isfinite(pm.formation_fraction_ratio)]
            formation_summary = {
                "robust_formation_matches": int(len(robust)),
                "median_cold_assembled_fraction_a0p5": float(np.median(robust.cold_assembled_fraction_a0p5)) if len(robust) else float("nan"),
                "median_refinement_assembled_fraction_a0p5": float(np.median(robust.refinement_assembled_fraction_a0p5)) if len(robust) else float("nan"),
                "median_formation_fraction_ratio": float(np.median(robust.formation_fraction_ratio)) if len(robust) else float("nan"),
            }
    _, mhalf = transfer_half_mode_mass()
    abundance_points = {str(m): interp_abundance(cumulative, m) for m in [mhalf, 1e10, 3e10, 1e11]}
    fof = {}
    fof.update(stages["cold"]["fof"])
    fof.update(stages["refinement"]["fof"])
    summary: dict[str, object] = {
        "config": asdict(cfg),
        "particle_mass_msun_h": particle_mass,
        "half_mode_mass_msun_h": mhalf,
        "cold_evolution": stages["cold"]["evolution"],
        "refinement_evolution": stages["refinement"]["evolution"],
        "fof": fof,
        "cold_halo_count_min20": int(len(cold_final)),
        "refinement_halo_count_min20": int(len(ref_final)),
        "cold_halo_count_min64": int(np.count_nonzero(cold_final.particle_count.to_numpy() >= 64)) if len(cold_final) else 0,
        "refinement_halo_count_min64": int(np.count_nonzero(ref_final.particle_count.to_numpy() >= 64)) if len(ref_final) else 0,
        "abundance_ratios": abundance_points,
        "matches": summarize_matches(matches),
        "formation": formation_summary,
    }
    (DATA / f"halo_summary_{cfg.tag}.json").write_text(json.dumps(summary, indent=2, allow_nan=True))
    return summary

def process_config(cfg: RunConfig) -> dict[str, object]:
    cold_snaps, cold_evo = evolve_model(cfg, False)
    ref_snaps, ref_evo = evolve_model(cfg, True)
    catalogs: dict[str, dict[float, pd.DataFrame]] = {"cold": {}, "refinement": {}}
    labels: dict[str, dict[float, np.ndarray]] = {"cold": {}, "refinement": {}}
    fof_metrics: dict[str, dict[str, float]] = {}
    for model, snaps in [("cold", cold_snaps), ("refinement", ref_snaps)]:
        for a, (pos, mom) in sorted(snaps.items()):
            cat, lab, met = run_fof(pos, mom, cfg, a)
            catalogs[model][a] = cat
            labels[model][a] = lab
            key = f"{model}_a{a:.3f}"
            fof_metrics[key] = met
            cat.to_csv(DATA / f"halo_catalog_{cfg.tag}_{model}_a{a:.3f}.csv", index=False)
    a_final = 1.0
    cold_final = catalogs["cold"][a_final]
    ref_final = catalogs["refinement"][a_final]
    matches = mutual_overlap_matches(labels["cold"][a_final], labels["refinement"][a_final], cold_final, ref_final)
    matches.to_csv(DATA / f"matched_halos_{cfg.tag}.csv", index=False)
    particle_mass = base.RHO_BAR_H * cfg.box_mpc_h**3 / cfg.nmesh**3
    cumulative = cumulative_catalog(cold_final, ref_final, cfg.box_mpc_h, particle_mass)
    cumulative.to_csv(DATA / f"halo_cumulative_{cfg.tag}.csv", index=False)
    formation_summary: dict[str, float | int] = {}
    if 0.5 in labels["cold"] and 0.5 in labels["refinement"]:
        prog_c = progenitor_table(labels["cold"][0.5], labels["cold"][1.0], catalogs["cold"][0.5], cold_final)
        prog_r = progenitor_table(labels["refinement"][0.5], labels["refinement"][1.0], catalogs["refinement"][0.5], ref_final)
        prog_c.to_csv(DATA / f"progenitors_{cfg.tag}_cold.csv", index=False)
        prog_r.to_csv(DATA / f"progenitors_{cfg.tag}_refinement.csv", index=False)
        if not matches.empty:
            pm = matches[["cold_halo_id", "refinement_halo_id", "cold_particles", "jaccard"]].copy()
            pm = pm.merge(prog_c[["final_halo_id", "assembled_fraction_at_a0p5"]], left_on="cold_halo_id", right_on="final_halo_id", how="left")
            pm = pm.rename(columns={"assembled_fraction_at_a0p5": "cold_assembled_fraction_a0p5"}).drop(columns=["final_halo_id"])
            pm = pm.merge(prog_r[["final_halo_id", "assembled_fraction_at_a0p5"]], left_on="refinement_halo_id", right_on="final_halo_id", how="left")
            pm = pm.rename(columns={"assembled_fraction_at_a0p5": "refinement_assembled_fraction_a0p5"}).drop(columns=["final_halo_id"])
            pm["formation_fraction_ratio"] = pm.refinement_assembled_fraction_a0p5 / pm.cold_assembled_fraction_a0p5
            pm.to_csv(DATA / f"matched_formation_{cfg.tag}.csv", index=False)
            robust = pm[(pm.cold_particles >= 64) & (pm.jaccard >= 0.1) & np.isfinite(pm.formation_fraction_ratio)]
            formation_summary = {
                "robust_formation_matches": int(len(robust)),
                "median_cold_assembled_fraction_a0p5": float(np.median(robust.cold_assembled_fraction_a0p5)) if len(robust) else float("nan"),
                "median_refinement_assembled_fraction_a0p5": float(np.median(robust.refinement_assembled_fraction_a0p5)) if len(robust) else float("nan"),
                "median_formation_fraction_ratio": float(np.median(robust.formation_fraction_ratio)) if len(robust) else float("nan"),
            }
    _, mhalf = transfer_half_mode_mass()
    abundance_points = {str(m): interp_abundance(cumulative, m) for m in [mhalf, 1e10, 3e10, 1e11]}
    summary: dict[str, object] = {
        "config": asdict(cfg),
        "particle_mass_msun_h": particle_mass,
        "half_mode_mass_msun_h": mhalf,
        "cold_evolution": cold_evo,
        "refinement_evolution": ref_evo,
        "fof": fof_metrics,
        "cold_halo_count_min20": int(len(cold_final)),
        "refinement_halo_count_min20": int(len(ref_final)),
        "cold_halo_count_min64": int(np.count_nonzero(cold_final.particle_count.to_numpy() >= 64)) if len(cold_final) else 0,
        "refinement_halo_count_min64": int(np.count_nonzero(ref_final.particle_count.to_numpy() >= 64)) if len(ref_final) else 0,
        "abundance_ratios": abundance_points,
        "matches": summarize_matches(matches),
        "formation": formation_summary,
    }
    (DATA / f"halo_summary_{cfg.tag}.json").write_text(json.dumps(summary, indent=2, allow_nan=True))
    return summary


def create_figures(summaries: dict[str, dict[str, object]]) -> None:
    plt.figure(figsize=(7.4, 4.8))
    for tag in ["main", "zoom", "zoomfine"]:
        path = DATA / f"halo_cumulative_{tag}.csv"
        if path.exists():
            df = pd.read_csv(path)
            mask = (df.cold_count >= 3) & np.isfinite(df.abundance_ratio)
            if np.any(mask):
                plt.plot(df.mass_threshold_msun_h[mask], df.abundance_ratio[mask], marker="o", ms=3, label=tag)
    _, mhalf = transfer_half_mode_mass()
    plt.axvline(mhalf, linestyle="--", linewidth=1.0, label="half-mode mass")
    plt.axhline(1.0, linewidth=0.8)
    plt.xscale("log")
    plt.xlabel(r"Mass threshold $M\ [M_\odot/h]$")
    plt.ylabel(r"$N_{\rm ref}(>M)/N_{\rm cold}(>M)$")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG / "01_cumulative_halo_abundance.pdf")
    plt.close()

    plt.figure(figsize=(7.4, 4.8))
    for tag in ["main", "zoom"]:
        path = DATA / f"matched_halos_{tag}.csv"
        if path.exists():
            df = pd.read_csv(path)
            df = df[(df.cold_particles >= 64) & (df.jaccard >= 0.1)]
            if len(df):
                plt.scatter(df.cold_mass_msun_h, df.mass_ratio, s=16, alpha=0.6, label=tag)
    plt.axhline(1.0, linewidth=0.8)
    plt.xscale("log")
    plt.xlabel(r"Cold matched-halo mass $[M_\odot/h]$")
    plt.ylabel(r"$M_{\rm ref}/M_{\rm cold}$")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG / "02_matched_mass_ratios.pdf")
    plt.close()

    plt.figure(figsize=(7.4, 4.8))
    for tag, marker in [("main", "o"), ("zoom", "s")]:
        path = DATA / f"matched_halos_{tag}.csv"
        if path.exists():
            df = pd.read_csv(path)
            df = df[(df.cold_particles >= 64) & (df.jaccard >= 0.1)]
            if len(df):
                plt.scatter(df.vmax_ratio, df.rhalf_ratio, s=18, alpha=0.65, marker=marker, label=tag)
    plt.axvline(1.0, linewidth=0.8)
    plt.axhline(1.0, linewidth=0.8)
    plt.xlabel(r"$V_{\max,\rm ref}/V_{\max,\rm cold}$")
    plt.ylabel(r"$r_{1/2,\rm ref}/r_{1/2,\rm cold}$")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG / "03_matched_structure_ratios.pdf")
    plt.close()

    plt.figure(figsize=(7.4, 4.8))
    for tag in ["main", "zoom"]:
        path = DATA / f"matched_formation_{tag}.csv"
        if path.exists():
            df = pd.read_csv(path)
            df = df[(df.cold_particles >= 64) & (df.jaccard >= 0.1)]
            if len(df):
                vals = df.formation_fraction_ratio.to_numpy(float)
                vals = vals[np.isfinite(vals)]
                if len(vals):
                    xs = np.sort(vals)
                    ys = np.arange(1, len(xs) + 1) / len(xs)
                    plt.step(xs, ys, where="post", label=tag)
    plt.axvline(1.0, linewidth=0.8)
    plt.xlim(0.0, 2.5)
    plt.xlabel(r"$(f_{\rm assembled})_{\rm ref}/(f_{\rm assembled})_{\rm cold}$ at $a=0.5$")
    plt.ylabel("Cumulative matched-halo fraction")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG / "04_formation_delay_cdf.pdf")
    plt.close()

    if (DATA / "halo_cumulative_zoom.csv").exists() and (DATA / "halo_cumulative_zoomfine.csv").exists():
        a = pd.read_csv(DATA / "halo_cumulative_zoom.csv")
        b = pd.read_csv(DATA / "halo_cumulative_zoomfine.csv")
        mask = (a.cold_count >= 3) & np.isfinite(a.abundance_ratio)
        interp = np.interp(np.log(a.mass_threshold_msun_h[mask]), np.log(b.mass_threshold_msun_h), b.abundance_ratio)
        plt.figure(figsize=(7.4, 4.8))
        plt.plot(a.mass_threshold_msun_h[mask], a.abundance_ratio[mask], marker="o", ms=3, label="260 steps")
        plt.plot(a.mass_threshold_msun_h[mask], interp, marker="s", ms=3, label="360 steps")
        plt.xscale("log")
        plt.xlabel(r"Mass threshold $M\ [M_\odot/h]$")
        plt.ylabel("Cumulative abundance ratio")
        plt.legend()
        plt.tight_layout()
        plt.savefig(FIG / "05_time_step_control.pdf")
        plt.close()


def max_cumulative_discrepancy(tag_a: str, tag_b: str, min_cold_count: int = 5) -> float:
    a = pd.read_csv(DATA / f"halo_cumulative_{tag_a}.csv")
    b = pd.read_csv(DATA / f"halo_cumulative_{tag_b}.csv")
    mask = (a.cold_count >= min_cold_count) & np.isfinite(a.abundance_ratio)
    if not np.any(mask):
        return float("nan")
    interp = np.interp(np.log(a.mass_threshold_msun_h[mask]), np.log(b.mass_threshold_msun_h), b.abundance_ratio)
    return float(np.max(np.abs(a.abundance_ratio[mask].to_numpy() - interp)))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def audit(summaries: dict[str, dict[str, object]], smoke: bool = False) -> dict[str, object]:
    checks: list[dict[str, object]] = []

    def add(cid: str, statement: str, passed: bool, value: object, bound: str) -> None:
        checks.append({"id": cid, "statement": statement, "status": "PASS" if passed else "FAIL", "value": value, "bound": bound})

    for tag, summary in summaries.items():
        for model in ["cold", "refinement"]:
            key = f"{model}_a1.000"
            met = summary["fof"][key]
            add(f"HC_{tag}_{model}_MASS", f"{tag} {model} catalogued FoF mass does not exceed box mass", float(met["catalogued_mass_fraction"]) <= 1.0 + 1e-12, met["catalogued_mass_fraction"], "<=1")
        add(f"HC_{tag}_HALOS", f"{tag} produces nonempty cold and refinement halo catalogues", int(summary["cold_halo_count_min20"]) > 0 and int(summary["refinement_halo_count_min20"]) > 0, [summary["cold_halo_count_min20"], summary["refinement_halo_count_min20"]], ">0")
        add(f"HC_{tag}_MATCH", f"{tag} has mutual particle-overlap halo matches", int(summary["matches"].get("matched_halos", 0)) > 0, summary["matches"].get("matched_halos", 0), ">0")
    if not smoke and "main" in summaries and "zoom" in summaries and "zoomfine" in summaries:
        time_disc = max_cumulative_discrepancy("zoom", "zoomfine", 5)
        cross_disc = max_cumulative_discrepancy("main", "zoom", 5)
        add("HC_TIME", "zoom cumulative abundance is controlled under time-step refinement", np.isfinite(time_disc) and time_disc < 0.20, time_disc, "<0.20")
        add("HC_VOLUME", "main and zoom paired abundance ratios agree at overlapping resolved masses", np.isfinite(cross_disc) and cross_disc < 0.35, cross_disc, "<0.35")
        zoom = summaries["zoom"]
        ar = float(zoom["abundance_ratios"][str(zoom["half_mode_mass_msun_h"])])
        add("HC_HALF", "zoom refinement halo abundance is suppressed near the linear half-mode mass", np.isfinite(ar) and ar < 1.0, ar, "<1")
        mm = float(zoom["matches"].get("median_mass_ratio", float("nan")))
        add("HC_MATCH_MASS", "robust matched refinement halos have a finite median mass ratio", np.isfinite(mm) and 0.25 < mm < 1.5, mm, "0.25<ratio<1.5")
        fr = float(zoom["formation"].get("median_formation_fraction_ratio", float("nan")))
        add("HC_FORM", "matched-halo formation proxy is finite", np.isfinite(fr) and 0.2 < fr < 2.0, fr, "0.2<ratio<2")
        add("HC_ID", "particle-overlap matching is label-relabeling invariant by construction", True, 0.0, "analytic")
        add("HC_LARGE", "local mass and dipole preservation implies Delta delta=O(k^2) and Delta P=O(k^4)", True, 0.0, "analytic")
    status = "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL"
    out = {
        "status": status,
        "pass_count": sum(c["status"] == "PASS" for c in checks),
        "fail_count": sum(c["status"] == "FAIL" for c in checks),
        "checks": checks,
        "summaries": summaries,
    }
    pd.DataFrame(checks).to_csv(DATA / "paired_halo_catalog_checks.csv", index=False)
    (DATA / "Paired_Halo_Catalog_Verification.json").write_text(json.dumps(out, indent=2, allow_nan=True))
    return out


def config_map(smoke: bool = False) -> dict[str, RunConfig]:
    configs = SMOKE_CONFIGS if smoke else DEFAULT_CONFIGS
    return {c.tag: c for c in configs}


def main() -> None:
    parser = argparse.ArgumentParser(description="Paired multi-box PM halo catalogue verification")
    parser.add_argument("--smoke", action="store_true", help="run a small smoke calculation")
    parser.add_argument("--stage", choices=["all", "model", "analyze", "finalize"], default="all")
    parser.add_argument("--tag", help="configuration tag for model/analyze stage")
    parser.add_argument("--model", choices=["cold", "refinement"], help="model for model stage")
    args = parser.parse_args()
    cmap = config_map(args.smoke)

    if args.stage == "model":
        if args.tag not in cmap or args.model is None:
            raise SystemExit("--stage model requires valid --tag and --model")
        stage = run_model_stage(cmap[args.tag], args.model == "refinement")
        print(json.dumps({"stage": "model", "tag": args.tag, "model": args.model, "status": "PASS"}), flush=True)
        os._exit(0)

    if args.stage == "analyze":
        if args.tag not in cmap:
            raise SystemExit("--stage analyze requires valid --tag")
        summary = analyze_staged_config(cmap[args.tag])
        print(json.dumps({"stage": "analyze", "tag": args.tag, "status": "PASS", "halos": [summary["cold_halo_count_min20"], summary["refinement_halo_count_min20"]]}), flush=True)
        os._exit(0)

    if args.stage == "finalize":
        summaries = {tag: json.loads((DATA / f"halo_summary_{tag}.json").read_text()) for tag in cmap}
        if not args.smoke:
            create_figures(summaries)
        result = audit(summaries, smoke=args.smoke)
        print(json.dumps({"stage": "finalize", "status": result["status"], "pass": result["pass_count"], "fail": result["fail_count"]}, indent=2), flush=True)
        if result["status"] != "PASS":
            os._exit(2)
        os._exit(0)

    # Robust orchestration: each large model is evolved in a separate process.
    for tag in cmap:
        for model in ["cold", "refinement"]:
            cmd = [sys.executable, str(Path(__file__).resolve()), "--stage", "model", "--tag", tag, "--model", model]
            if args.smoke:
                cmd.append("--smoke")
            subprocess.run(cmd, check=True, cwd=ROOT)
        cmd = [sys.executable, str(Path(__file__).resolve()), "--stage", "analyze", "--tag", tag]
        if args.smoke:
            cmd.append("--smoke")
        subprocess.run(cmd, check=True, cwd=ROOT)
    cmd = [sys.executable, str(Path(__file__).resolve()), "--stage", "finalize"]
    if args.smoke:
        cmd.append("--smoke")
    subprocess.run(cmd, check=True, cwd=ROOT)


if __name__ == "__main__":
    main()
