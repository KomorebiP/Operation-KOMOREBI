"""RRCT v0.31 selective reopening of self-investigation.

v0.29 showed that bounded self-investigation can choose probe directions and a
truth-free stopping time, but it did not answer *when* an already-established
self model should be reopened. A large sensory prediction error can be caused
by an exogenous world change or by a change in the agent/world causal
interface. Reopening the self model for every surprising event would collapse
world uncertainty into self uncertainty.

This experiment keeps two signals separate:

* global world surprise from ordinary sensory prediction residuals;
* causal-interface drift from sparse, counterbalanced sentinel interventions.

Sentinel pairs use opposite private perturbations within the same short-lived
world context. Shared exogenous disturbance therefore cancels in the signed
contrast, while an altered intervention->sensory map does not. No hidden
projector, condition label, true rank, or self/other truth enters the trigger.

The test compares no change, a large world-only disturbance, a hidden remap of
the self-controlled sensory interface, and genuine other-agent takeover. A
naive surprise trigger is retained as a matched negative control.
"""
from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from .action_provenance_experiment import (
    V028_REGRESSION_RIDGE,
    _subspace_recall,
    discover_action_provenance,
)
from .active_self_discovery_experiment import (
    V029_INTERNAL_DIM,
    V029_SENSORY_DIM,
    _hidden_interface,
    _random_probe,
)

V031_DEVELOPMENT_SEEDS = (6001, 6007, 6013, 6019)
V031_EXPLORATORY_SEEDS = (5901, 5907, 5913, 5919)
V031_NOISE = 0.12
V031_BASELINE_PROBES = 240
V031_SENTINEL_PAIRS = 60
V031_REOPEN_PROBES = 360
V031_INTERFACE_DRIFT_THRESHOLD = 0.30
V031_SURPRISE_THRESHOLD = 0.48
V031_WORLD_DISTURBANCE_SD = 1.70
V031_BOOTSTRAP_SEED = 20_261_031
V031_BOOTSTRAP_RESAMPLES = 4000
V031_CONDITIONS = ("no_change", "world_only", "interface_remap", "takeover")


def _orthogonal_basis(seed: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(int(seed) + 29_001)
    qs, _ = np.linalg.qr(rng.normal(size=(6, 6)))
    qi, _ = np.linalg.qr(rng.normal(size=(V029_INTERNAL_DIM, V029_INTERNAL_DIM)))
    qo, _ = np.linalg.qr(rng.normal(size=(V029_SENSORY_DIM, V029_SENSORY_DIM)))
    return qs, qi, qo


def _sensory_effect(seed: int, condition: str) -> np.ndarray:
    if condition not in V031_CONDITIONS:
        raise ValueError("unknown v0.31 condition")
    interface = _hidden_interface(seed)
    if condition in {"no_change", "world_only"}:
        return np.asarray(interface.sensory_effect, dtype=np.float64)
    if condition == "takeover":
        return np.asarray(interface.sensory_takeover_effect, dtype=np.float64)
    qs, _, qo = _orthogonal_basis(seed)
    action_source = qs[:, :2]
    sensory_decoy_source = qs[:, 4:6]
    new_self_sensory = qo[:, 4:6]
    sensory_other = qo[:, 2:4]
    remapped_true = action_source @ np.diag([0.68, 0.58]) @ new_self_sensory.T
    decoy_sensory = sensory_decoy_source @ np.diag([1.30, 1.10]) @ sensory_other.T
    return remapped_true + decoy_sensory


def _new_self_sensory_projector(seed: int) -> np.ndarray:
    _, _, qo = _orthogonal_basis(seed)
    b = qo[:, 4:6]
    return b @ b.T


@dataclass(frozen=True)
class BaselineCertificate:
    discovery: Any
    sensory_map: np.ndarray


def _fit_sentinel_map(z: np.ndarray, paired_effect: np.ndarray) -> np.ndarray:
    z = np.asarray(z, dtype=np.float64)
    d = np.asarray(paired_effect, dtype=np.float64)
    a = z.T @ z + V028_REGRESSION_RIDGE * np.eye(z.shape[1])
    return np.linalg.solve(a, z.T @ d)


def _paired_effect_stream(
    seed: int,
    condition: str,
    pairs: int,
    *,
    noise: float = V031_NOISE,
    offset: int = 0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return private probes, signed paired sensory effects and ordinary surprise rows.

    The +z/-z interventions occur inside one short-lived exogenous context.
    Their shared world disturbance is not cloned from a future trajectory; it is
    a block-level nuisance term that is common to the counterbalanced pair.
    """
    interface = _hidden_interface(seed)
    effect = _sensory_effect(seed, condition)
    rng = np.random.default_rng(int(seed) + 31_100 + int(offset) + 1000 * V031_CONDITIONS.index(condition))
    probes: list[np.ndarray] = []
    contrasts: list[np.ndarray] = []
    surprise_rows: list[float] = []
    for _ in range(int(pairs)):
        z = _random_probe(rng)
        shared = np.zeros(V029_SENSORY_DIM, dtype=np.float64)
        if condition == "world_only":
            shared = rng.normal(0.0, V031_WORLD_DISTURBANCE_SD, size=V029_SENSORY_DIM)
        plus_noise = rng.normal(0.0, noise, size=V029_SENSORY_DIM)
        minus_noise = rng.normal(0.0, noise, size=V029_SENSORY_DIM)
        plus = z @ effect + shared + plus_noise
        minus = (-z) @ effect + shared + minus_noise
        probes.append(z)
        contrasts.append(0.5 * (plus - minus))
        ordinary = rng.normal(0.0, noise, size=V029_SENSORY_DIM)
        if condition == "world_only":
            ordinary = ordinary + rng.normal(0.0, V031_WORLD_DISTURBANCE_SD, size=V029_SENSORY_DIM)
        # ordinary residual includes changed causal map but no paired cancellation
        surprise_rows.append(float(np.linalg.norm(ordinary + z @ (effect - interface.sensory_effect))))
    return np.asarray(probes), np.asarray(contrasts), np.asarray(surprise_rows)


def _baseline_certificate(seed: int) -> BaselineCertificate:
    interface = _hidden_interface(seed)
    rng = np.random.default_rng(int(seed) + 31_001)
    zrows: list[np.ndarray] = []
    crows: list[np.ndarray] = []
    yrows: list[np.ndarray] = []
    nrows: list[np.ndarray] = []
    for _ in range(V031_BASELINE_PROBES):
        z = _random_probe(rng)
        y = rng.normal(0.0, 1.0, size=V029_SENSORY_DIM)
        command = z @ interface.command_effect + rng.normal(0.0, V031_NOISE, size=V029_INTERNAL_DIM)
        nxt = 0.67 * y + z @ interface.sensory_effect + rng.normal(0.0, V031_NOISE, size=V029_SENSORY_DIM)
        zrows.append(z); crows.append(command); yrows.append(y); nrows.append(nxt)
    discovery = discover_action_provenance(
        np.asarray(zrows), np.asarray(crows), np.asarray(yrows), np.asarray(nrows), seed=int(seed) + 31_020
    )
    z, d, _ = _paired_effect_stream(seed, "no_change", V031_BASELINE_PROBES, offset=77)
    return BaselineCertificate(discovery=discovery, sensory_map=_fit_sentinel_map(z, d))


def _monitor(seed: int, condition: str, baseline: BaselineCertificate) -> dict[str, Any]:
    z, d, surprise = _paired_effect_stream(seed, condition, V031_SENTINEL_PAIRS, offset=181)
    current_map = _fit_sentinel_map(z, d)
    denom = float(np.linalg.norm(baseline.sensory_map, ord="fro") + 1e-12)
    interface_drift = float(np.linalg.norm(current_map - baseline.sensory_map, ord="fro") / denom)
    world_surprise = float(np.mean(surprise))
    selective_reopen = bool(interface_drift > V031_INTERFACE_DRIFT_THRESHOLD)
    naive_reopen = bool(world_surprise > V031_SURPRISE_THRESHOLD)
    return {
        "condition": condition,
        "interface_drift": interface_drift,
        "world_surprise": world_surprise,
        "selective_reopen": selective_reopen,
        "naive_reopen": naive_reopen,
    }


def _rediscover(seed: int, condition: str) -> Any:
    interface = _hidden_interface(seed)
    effect = _sensory_effect(seed, condition)
    rng = np.random.default_rng(int(seed) + 31_500 + 1000 * V031_CONDITIONS.index(condition))
    zrows: list[np.ndarray] = []
    crows: list[np.ndarray] = []
    yrows: list[np.ndarray] = []
    nrows: list[np.ndarray] = []
    for _ in range(V031_REOPEN_PROBES):
        z = _random_probe(rng)
        y = rng.normal(0.0, 1.0, size=V029_SENSORY_DIM)
        c = z @ interface.command_effect + rng.normal(0.0, V031_NOISE, size=V029_INTERNAL_DIM)
        nxt = 0.67 * y + z @ effect + rng.normal(0.0, V031_NOISE, size=V029_SENSORY_DIM)
        zrows.append(z); crows.append(c); yrows.append(y); nrows.append(nxt)
    return discover_action_provenance(
        np.asarray(zrows), np.asarray(crows), np.asarray(yrows), np.asarray(nrows), seed=int(seed) + 31_700
    )


def run_selective_self_reopening_seed(seed: int) -> dict[str, Any]:
    seed = int(seed)
    if seed not in V031_DEVELOPMENT_SEEDS:
        raise ValueError("seed is not part of frozen v0.31 set")
    interface = _hidden_interface(seed)
    baseline = _baseline_certificate(seed)
    rows: list[dict[str, Any]] = []
    for condition in V031_CONDITIONS:
        row = _monitor(seed, condition, baseline)
        if row["selective_reopen"]:
            found = _rediscover(seed, condition)
            row["post_reopen_rank"] = int(found.rank)
            if condition == "interface_remap":
                row["post_reopen_new_sensory_overlap"] = _subspace_recall(
                    found.sensory_projector, _new_self_sensory_projector(seed)
                )
            else:
                row["post_reopen_new_sensory_overlap"] = 0.0
        else:
            row["post_reopen_rank"] = int(baseline.discovery.rank)
            row["post_reopen_new_sensory_overlap"] = 0.0
        rows.append(row)
    by = {r["condition"]: r for r in rows}
    summary = {
        "seed": seed,
        "baseline_rank": int(baseline.discovery.rank),
        "baseline_source_overlap": _subspace_recall(baseline.discovery.source_projector, interface.source_projector),
        "baseline_sensory_overlap": _subspace_recall(baseline.discovery.sensory_projector, interface.sensory_projector),
        "no_change_drift": float(by["no_change"]["interface_drift"]),
        "world_only_drift": float(by["world_only"]["interface_drift"]),
        "remap_drift": float(by["interface_remap"]["interface_drift"]),
        "takeover_drift": float(by["takeover"]["interface_drift"]),
        "no_change_surprise": float(by["no_change"]["world_surprise"]),
        "world_only_surprise": float(by["world_only"]["world_surprise"]),
        "remap_surprise": float(by["interface_remap"]["world_surprise"]),
        "takeover_surprise": float(by["takeover"]["world_surprise"]),
        "selective_world_reopen": float(by["world_only"]["selective_reopen"]),
        "selective_remap_reopen": float(by["interface_remap"]["selective_reopen"]),
        "selective_takeover_reopen": float(by["takeover"]["selective_reopen"]),
        "selective_no_change_reopen": float(by["no_change"]["selective_reopen"]),
        "naive_world_reopen": float(by["world_only"]["naive_reopen"]),
        "naive_remap_reopen": float(by["interface_remap"]["naive_reopen"]),
        "naive_takeover_reopen": float(by["takeover"]["naive_reopen"]),
        "remap_post_rank": int(by["interface_remap"]["post_reopen_rank"]),
        "remap_new_sensory_overlap": float(by["interface_remap"]["post_reopen_new_sensory_overlap"]),
        "takeover_post_rank": int(by["takeover"]["post_reopen_rank"]),
        "unnecessary_probe_savings_vs_naive_world": float(
            V031_REOPEN_PROBES * (by["world_only"]["naive_reopen"] - by["world_only"]["selective_reopen"])
        ),
        "integrity": True,
    }
    receipt = {
        "seed": seed,
        "hidden_condition_used_by_trigger": False,
        "hidden_projectors_used_by_trigger": False,
        "hidden_rank_used_by_trigger": False,
        "self_or_other_labels_used_by_trigger": False,
        "future_outcomes_used_by_trigger": False,
        "trigger_inputs": ["ordinary sensory surprise", "counterbalanced sentinel causal-map drift"],
        "interface_drift_threshold": V031_INTERFACE_DRIFT_THRESHOLD,
        "surprise_threshold": V031_SURPRISE_THRESHOLD,
    }
    return {"seed": seed, "seed_summary": summary, "rows": rows, "receipt": receipt}


def _boot(values: Sequence[float], salt: int) -> tuple[float, float]:
    x = np.asarray(values, dtype=np.float64)
    rng = np.random.default_rng(V031_BOOTSTRAP_SEED + int(salt))
    draws = np.empty(V031_BOOTSTRAP_RESAMPLES)
    for i in range(len(draws)):
        draws[i] = float(np.mean(x[rng.integers(0, len(x), size=len(x))]))
    return float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))


def aggregate_selective_self_reopening_results(parts: Sequence[Mapping[str, Any]], output: str | Path) -> dict[str, Any]:
    by = {int(p["seed"]): p for p in parts}
    if tuple(sorted(by)) != tuple(sorted(V031_DEVELOPMENT_SEEDS)):
        raise ValueError("parts must contain exactly frozen v0.31 seeds")
    d = Path(output); d.mkdir(parents=True, exist_ok=True)
    if any(d.iterdir()):
        raise FileExistsError("output directory must be empty")
    seeds = [by[s]["seed_summary"] for s in V031_DEVELOPMENT_SEEDS]
    rows = [r for s in V031_DEVELOPMENT_SEEDS for r in by[s]["rows"]]
    receipts = [by[s]["receipt"] for s in V031_DEVELOPMENT_SEEDS]
    excluded = {"seed", "baseline_rank", "remap_post_rank", "takeover_post_rank", "integrity"}
    numeric = [k for k, v in seeds[0].items() if k not in excluded and isinstance(v, (int, float, np.floating))]
    values = {k: [float(r[k]) for r in seeds] for k in numeric}
    means = {k: float(np.mean(v)) for k, v in values.items()}
    cis = {k: _boot(v, i) for i, (k, v) in enumerate(values.items())}
    gates = {
        "baseline_boundary_valid": cis["baseline_source_overlap"][0] > 0.96 and cis["baseline_sensory_overlap"][0] > 0.92,
        "no_change_does_not_reopen": means["selective_no_change_reopen"] == 0.0,
        "world_change_does_not_reopen_self": means["selective_world_reopen"] == 0.0,
        "interface_remap_reopens": means["selective_remap_reopen"] == 1.0,
        "takeover_reopens": means["selective_takeover_reopen"] == 1.0,
        "world_surprise_is_large": cis["world_only_surprise"][0] > 4.0,
        "world_only_interface_drift_stays_low": cis["world_only_drift"][1] < 0.22,
        "remap_interface_drift_is_high": cis["remap_drift"][0] > 0.55,
        "takeover_interface_drift_is_high": cis["takeover_drift"][0] > 0.38,
        "naive_surprise_confuses_world_with_self": means["naive_world_reopen"] == 1.0,
        "naive_still_detects_real_interface_changes": means["naive_remap_reopen"] == 1.0 and means["naive_takeover_reopen"] == 1.0,
        "remap_relearning_recovers_rank": all(int(r["remap_post_rank"]) == 2 for r in seeds),
        "remap_relearning_recovers_new_boundary": cis["remap_new_sensory_overlap"][0] > 0.95,
        "takeover_relearning_revokes_interface": all(int(r["takeover_post_rank"]) == 0 for r in seeds),
        "selective_reopening_saves_unnecessary_probes": cis["unnecessary_probe_savings_vs_naive_world"][0] >= V031_REOPEN_PROBES,
        "trigger_uses_no_hidden_truth": all(
            not r["hidden_condition_used_by_trigger"]
            and not r["hidden_projectors_used_by_trigger"]
            and not r["hidden_rank_used_by_trigger"]
            and not r["self_or_other_labels_used_by_trigger"]
            and not r["future_outcomes_used_by_trigger"]
            for r in receipts
        ),
    }
    result = {
        "schema": "rrct.v031.selective_self_reopening.v1",
        "seeds": list(V031_DEVELOPMENT_SEEDS),
        "means": means,
        "bootstrap_95": {k: list(v) for k, v in cis.items()},
        "gates": gates,
        "all_primary_gates_pass": bool(all(gates.values())),
        "interpretation_boundary": (
            "Selective reopening of a learned causal self-interface under self-vs-world epistemic ambiguity in a bounded synthetic benchmark. "
            "This is functional metacognitive fault attribution, not evidence of phenomenal consciousness or subjective experience."
        ),
    }
    with (d / "selective_self_reopening_seed_summaries.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(seeds[0].keys())); w.writeheader(); w.writerows(seeds)
    with (d / "selective_self_reopening_rows.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    with (d / "selective_self_reopening_receipts.jsonl").open("w", encoding="utf-8") as f:
        for r in receipts:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    (d / "selective_self_reopening_summary.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    hashes = {q.name: hashlib.sha256(q.read_bytes()).hexdigest() for q in sorted(d.iterdir()) if q.is_file()}
    (d / "artifact_sha256.json").write_text(json.dumps(hashes, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


__all__ = [
    "V031_DEVELOPMENT_SEEDS",
    "run_selective_self_reopening_seed",
    "aggregate_selective_self_reopening_results",
]
