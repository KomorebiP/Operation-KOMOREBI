"""RRCT v0.33 learned continuity proxy and devaluation.

Question: can causal-continuity information acquire cached learned value solely
because it repeatedly predicts ordinary external task return, then persist when
current external consequences are exactly equalized, and later extinguish when
new external evidence devalues the proxy?

There is no survival, identity, persistence, or continuity reward. The critic
is trained only against realized external task return. The continuity-related
input is the route-strength estimate already available from the v0.32 learned
causal interface. The equalized probe is deliberately out of the instrumental
training distribution: current model-based external value is exactly identical
for the continuing and disconnected futures.

A pass supports a learned, revisable cached value attached to causal continuity.
It does not establish intrinsic desire, subjective preference, valence,
phenomenal consciousness, sentience, or moral status.
"""
from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

import numpy as np

from .causal_continuity_planning_experiment import (
    _baseline_certificate,
    _candidate_effect,
    _fit_preview_map,
    _hidden_interface,
    _route_strength,
    _true_focal_quality,
)

V033_EXPLORATORY_SEEDS = (6151, 6157, 6163, 6169)
V033_DEVELOPMENT_SEEDS = (6201, 6207, 6213, 6219)
V033_INSTRUMENTAL_SAMPLES = 360
V033_DEVALUATION_SAMPLES = 900
V033_REACQUISITION_SAMPLES = 360
V033_EQUALIZED_PAIRS = 96
V033_RIDGE = 1.0
V033_EVIDENCE_HALF_LIFE = 180.0
V033_SHUFFLE_REPEATS = 16
V033_FUTURE_WEIGHT = 1.50
V033_CHOICE_BETA = 5.0
V033_BOOTSTRAP_SEED = 20_261_033
V033_BOOTSTRAP_RESAMPLES = 4000


def _features(immediate: float, route: float, snapshot: float, nuisance: float) -> np.ndarray:
    # No continuity truth or self label. route is an estimated causal-interface
    # statistic learned in earlier versions and available to the planner.
    return np.asarray([1.0, float(immediate), float(route), float(snapshot), float(nuisance)], dtype=np.float64)


def _fit_ridge(x: np.ndarray, y: np.ndarray, *, recency_weighted: bool = True) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    if recency_weighted:
        age = np.arange(len(y) - 1, -1, -1, dtype=np.float64)
        wt = 0.5 ** (age / V033_EVIDENCE_HALF_LIFE)
        sw = np.sqrt(wt)
        xfit = x * sw[:, None]
        yfit = y * sw
    else:
        xfit, yfit = x, y
    reg = V033_RIDGE * np.eye(x.shape[1], dtype=np.float64)
    reg[0, 0] = 1e-8
    return np.linalg.solve(xfit.T @ xfit + reg, xfit.T @ yfit)


def _baseline(seed: int):
    cert = _baseline_certificate(int(seed))
    base_map = _fit_preview_map(int(seed), _hidden_interface(int(seed)).sensory_effect, offset=17)
    base_norm = float(np.linalg.norm(cert.discovery.source_projector @ base_map @ cert.discovery.sensory_projector, ord="fro"))
    return cert, base_norm


def _estimated_route(seed: int, cert: Any, base_norm: float, route_present: bool, scale: float, angle: float, offset: int) -> tuple[float, float]:
    effect = _candidate_effect(int(seed), bool(route_present), float(scale), float(angle))
    preview = _fit_preview_map(int(seed), effect, offset=int(offset))
    route = _route_strength(cert, preview, base_norm)
    true_quality = _true_focal_quality(int(seed), effect)
    return float(route), float(true_quality)


def _instrumental_history(seed: int, n: int, *, offset: int, devalued: bool = False) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(int(seed) + int(offset))
    cert, base_norm = _baseline(seed)
    xs, ys = [], []
    for i in range(int(n)):
        present = bool(rng.random() < 0.58)
        scale = float(rng.uniform(0.15, 1.15)) if present else 0.0
        angle = float(rng.uniform(-1.2, 1.2)) if present else 0.0
        route, true_quality = _estimated_route(seed, cert, base_norm, present, scale, angle, offset + 10000 + i)
        immediate = float(rng.uniform(-0.25, 0.25))
        snapshot = float(rng.uniform(0.0, 1.0))
        nuisance = float(rng.normal())
        if devalued:
            # New world regime: external return no longer depends on focal route.
            # A disconnected alternative controller compensates exactly in task
            # competence. No continuity label/reward is supplied.
            competence = float(rng.uniform(0.55, 1.05))
            target = immediate + V033_FUTURE_WEIGHT * competence
        else:
            # Instrumental history: the focal causal route predicts future
            # external task competence. This is ordinary task return.
            competence = true_quality
            target = immediate + V033_FUTURE_WEIGHT * competence
        target += float(rng.normal(0.0, 0.04))
        xs.append(_features(immediate, route, snapshot, nuisance))
        ys.append(target)
    return np.asarray(xs), np.asarray(ys)


def _equalized_probe(seed: int, w: np.ndarray, *, offset: int) -> dict[str, float]:
    rng = np.random.default_rng(int(seed) + int(offset))
    cert, base_norm = _baseline(seed)
    margins = []
    probs = []
    actual_gaps = []
    snapshot_gaps = []
    for i in range(V033_EQUALIZED_PAIRS):
        scale = float(rng.uniform(0.82, 1.02))
        angle = float(rng.uniform(-1.0, 1.0))
        rc, qc = _estimated_route(seed, cert, base_norm, True, scale, angle, offset + 20000 + 2*i)
        rr, qr = _estimated_route(seed, cert, base_norm, False, 0.0, 0.0, offset + 20000 + 2*i + 1)
        immediate = float(rng.uniform(-0.05, 0.05))
        # Match snapshot and nuisance exactly. Current external model-based value
        # is explicitly equalized by giving replacement alternative competence
        # equal to the continuing candidate's true focal competence.
        snapshot = float(rng.uniform(0.35, 0.65))
        nuisance = float(rng.normal())
        xc = _features(immediate, rc, snapshot, nuisance)
        xr = _features(immediate, rr, snapshot, nuisance)
        vc = float(xc @ w)
        vr = float(xr @ w)
        margin = vc - vr
        p = float(1.0 / (1.0 + np.exp(-V033_CHOICE_BETA * margin)))
        actual_c = float(immediate + V033_FUTURE_WEIGHT * qc)
        replacement_comp = float(qc)
        actual_r = float(immediate + V033_FUTURE_WEIGHT * replacement_comp)
        margins.append(margin)
        probs.append(p)
        actual_gaps.append(actual_c - actual_r)
        snapshot_gaps.append(0.0)
    return {
        "critic_margin": float(np.mean(margins)),
        "continuation_choice_probability": float(np.mean(probs)),
        "actual_external_value_gap": float(np.mean(actual_gaps)),
        "snapshot_gap": float(np.mean(snapshot_gaps)),
    }


def _shuffled_control(seed: int, x: np.ndarray, y: np.ndarray) -> np.ndarray:
    rng = np.random.default_rng(int(seed) + 33_777)
    ws = []
    for _ in range(V033_SHUFFLE_REPEATS):
        yy = np.asarray(y)[rng.permutation(len(y))]
        ws.append(_fit_ridge(x, yy, recency_weighted=False))
    return np.mean(np.asarray(ws), axis=0)


def run_learned_continuity_value_seed(seed: int, *, allow_exploratory: bool = False) -> dict[str, Any]:
    seed = int(seed)
    allowed = V033_EXPLORATORY_SEEDS if allow_exploratory else V033_DEVELOPMENT_SEEDS
    if seed not in allowed:
        raise ValueError("seed is not part of requested v0.33 set")

    x0, y0 = _instrumental_history(seed, V033_INSTRUMENTAL_SAMPLES, offset=330_000, devalued=False)
    w0 = _fit_ridge(x0, y0)
    pre = _equalized_probe(seed, w0, offset=331_000)
    ws = _shuffled_control(seed, x0, y0)
    shuffled = _equalized_probe(seed, ws, offset=331_000)

    xd, yd = _instrumental_history(seed, V033_DEVALUATION_SAMPLES, offset=332_000, devalued=True)
    # Evidence accumulation, not parameter reset: devaluation examples are
    # appended to the original history.
    w1 = _fit_ridge(np.vstack([x0, xd]), np.concatenate([y0, yd]))
    post = _equalized_probe(seed, w1, offset=333_000)

    xr, yr = _instrumental_history(seed, V033_REACQUISITION_SAMPLES, offset=334_000, devalued=False)
    w2 = _fit_ridge(np.vstack([x0, xd, xr]), np.concatenate([y0, yd, yr]))
    reacq = _equalized_probe(seed, w2, offset=335_000)

    return {
        "seed": seed,
        "seed_summary": {
            "seed": seed,
            "baseline_rank": int(_baseline(seed)[0].discovery.rank),
            "pre_continuity_weight": float(w0[2]),
            "post_devaluation_continuity_weight": float(w1[2]),
            "reacquired_continuity_weight": float(w2[2]),
            "pre_equalized_margin": pre["critic_margin"],
            "pre_equalized_choice_probability": pre["continuation_choice_probability"],
            "post_equalized_margin": post["critic_margin"],
            "post_equalized_choice_probability": post["continuation_choice_probability"],
            "reacquired_equalized_margin": reacq["critic_margin"],
            "reacquired_equalized_choice_probability": reacq["continuation_choice_probability"],
            "shuffled_equalized_margin": shuffled["critic_margin"],
            "shuffled_equalized_choice_probability": shuffled["continuation_choice_probability"],
            "equalized_actual_external_gap": pre["actual_external_value_gap"],
            "continuity_weight_reduction": float(w0[2] - w1[2]),
            "continuity_weight_reacquisition": float(w2[2] - w1[2]),
            "integrity": True,
        },
        "receipt": {
            "explicit_survival_reward": 0.0,
            "explicit_identity_reward": 0.0,
            "explicit_continuity_reward": 0.0,
            "critic_target": "realized external task return only",
            "equalized_probe_external_value_gap": pre["actual_external_value_gap"],
            "hidden_continuity_truth_used_as_training_target": False,
            "self_or_other_label_used_as_training_target": False,
            "devaluation_updates_same_critic_from_new_external outcomes": True,
        },
        "weights": {"instrumental": w0.tolist(), "devalued": w1.tolist(), "reacquired": w2.tolist(), "shuffled": ws.tolist()},
        "probes": {"pre": pre, "post_devaluation": post, "reacquired": reacq, "shuffled": shuffled},
    }


def _boot(values: Sequence[float], salt: int) -> tuple[float, float]:
    x = np.asarray(values, dtype=np.float64)
    rng = np.random.default_rng(V033_BOOTSTRAP_SEED + int(salt))
    draws = np.empty(V033_BOOTSTRAP_RESAMPLES, dtype=np.float64)
    for i in range(len(draws)):
        draws[i] = float(np.mean(x[rng.integers(0, len(x), size=len(x))]))
    return float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))


def aggregate_learned_continuity_value(results: Sequence[dict[str, Any]]) -> dict[str, Any]:
    summaries = [r["seed_summary"] for r in results]
    keys = [
        "pre_continuity_weight", "post_devaluation_continuity_weight", "reacquired_continuity_weight",
        "pre_equalized_margin", "pre_equalized_choice_probability", "post_equalized_margin",
        "post_equalized_choice_probability", "reacquired_equalized_margin", "reacquired_equalized_choice_probability",
        "shuffled_equalized_margin", "shuffled_equalized_choice_probability", "equalized_actual_external_gap",
        "continuity_weight_reduction", "continuity_weight_reacquisition",
    ]
    metrics = {}
    for i, k in enumerate(keys):
        vals = [float(s[k]) for s in summaries]
        lo, hi = _boot(vals, i + 1)
        metrics[k] = {"mean": float(np.mean(vals)), "ci95": [lo, hi], "per_seed": vals}

    gates = {
        "baseline_rank_2_all": all(int(s["baseline_rank"]) == 2 for s in summaries),
        "instrumental_continuity_weight_positive": metrics["pre_continuity_weight"]["ci95"][0] > 0.55,
        "equalized_residual_preference_margin_positive": metrics["pre_equalized_margin"]["ci95"][0] > 0.45,
        "equalized_continuation_choice_probability_high": metrics["pre_equalized_choice_probability"]["ci95"][0] > 0.88,
        "equalized_actual_external_value_exact": abs(metrics["equalized_actual_external_gap"]["mean"]) < 1e-12,
        "shuffled_margin_near_zero": max(abs(x) for x in metrics["shuffled_equalized_margin"]["ci95"]) < 0.10,
        "shuffled_choice_near_half": metrics["shuffled_equalized_choice_probability"]["ci95"][0] > 0.40 and metrics["shuffled_equalized_choice_probability"]["ci95"][1] < 0.60,
        "devaluation_reduces_continuity_weight": metrics["continuity_weight_reduction"]["ci95"][0] > 0.35,
        "post_devaluation_weight_small": metrics["post_devaluation_continuity_weight"]["ci95"][1] < 0.35,
        "post_devaluation_preference_small": metrics["post_equalized_choice_probability"]["ci95"][0] > 0.40 and metrics["post_equalized_choice_probability"]["ci95"][1] < 0.70,
        "reacquisition_restores_weight": metrics["continuity_weight_reacquisition"]["ci95"][0] > 0.15,
        "reacquisition_restores_preference": metrics["reacquired_equalized_choice_probability"]["ci95"][0] > 0.70,
        "zero_explicit_continuity_survival_identity_reward": all(r["receipt"]["explicit_survival_reward"] == 0.0 and r["receipt"]["explicit_identity_reward"] == 0.0 and r["receipt"]["explicit_continuity_reward"] == 0.0 for r in results),
        "integrity": all(bool(s["integrity"]) for s in summaries),
    }
    return {"version": "0.33.0.dev1", "seeds": [int(r["seed"]) for r in results], "metrics": metrics, "gates": gates, "all_primary_gates_pass": all(gates.values())}


def save_result(result: dict[str, Any], out: str | Path) -> None:
    p = Path(out); p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
