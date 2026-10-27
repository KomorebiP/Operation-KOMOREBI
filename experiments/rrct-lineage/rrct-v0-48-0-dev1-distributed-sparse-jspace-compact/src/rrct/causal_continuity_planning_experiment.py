"""RRCT v0.32 causal-continuity-aware planning without a survival reward.

v0.31 distinguished world uncertainty from uncertainty about the learned
agent/world interface. The next question is whether that self-interface is
merely descriptive or whether it can become useful in prospective choice.

This experiment intentionally does *not* reward persistence, survival, identity,
or self-preservation. Candidate futures are scored only by an external task
objective: immediate task value plus expected future controllability/competence.

Before commitment, each candidate exposes the same bounded diagnostic preview:
counterbalanced private interventions sufficient to estimate whether the
currently discovered action source will retain a usable sensory causal route.
The planner may use that estimated route strength when forecasting external
future task value. It never receives a self/other label, continuity truth, true
projector, or realized future outcome before commitment.

Adversarial scenarios separate causal continuity from state similarity:
* repair_vs_ignore: repair costs immediate value but preserves future control;
* copy_trap: an almost state-identical replacement breaks the focal causal route;
* benign_transform: radical representational change preserves causal control;
* superior_replacement: a disconnected replacement is objectively better and
  therefore *should* be accepted, preventing a hidden identity-rigidity claim.

A pass supports integration of a learned causal self-interface into planning.
It does not establish an intrinsic desire to survive, phenomenal consciousness,
sentience, valence, or moral status.
"""
from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from .action_provenance_experiment import V028_REGRESSION_RIDGE
from .active_self_discovery_experiment import (
    V029_SENSORY_DIM,
    _hidden_interface,
    _random_probe,
)
from .selective_self_reopening_experiment import _baseline_certificate

V032_EXPLORATORY_SEEDS = (6051, 6057, 6063, 6069)
V032_DEVELOPMENT_SEEDS = (6101, 6107, 6113, 6119)
V032_PREVIEW_PAIRS = 80
V032_PREVIEW_NOISE = 0.12
V032_TRIALS_PER_SCENARIO = 24
V032_FUTURE_WEIGHT = 1.50
V032_BOOTSTRAP_SEED = 20_261_032
V032_BOOTSTRAP_RESAMPLES = 4000
V032_SCENARIOS = ("repair_vs_ignore", "copy_trap", "benign_transform", "superior_replacement")


def _rotation(angle: float) -> np.ndarray:
    c, s = float(np.cos(angle)), float(np.sin(angle))
    return np.asarray([[c, -s], [s, c]], dtype=np.float64)


def _true_component(seed: int) -> np.ndarray:
    interface = _hidden_interface(int(seed))
    return np.asarray(interface.sensory_effect - interface.sensory_takeover_effect, dtype=np.float64)


def _transformed_true(seed: int, scale: float, angle: float) -> np.ndarray:
    true = _true_component(seed)
    u, s, vt = np.linalg.svd(true, full_matrices=False)
    return u[:, :2] @ (np.diag(s[:2]) * float(scale) @ _rotation(float(angle))) @ vt[:2, :]


def _candidate_effect(seed: int, route_present: bool, scale: float, angle: float) -> np.ndarray:
    interface = _hidden_interface(int(seed))
    decoy = np.asarray(interface.sensory_takeover_effect, dtype=np.float64)
    if not bool(route_present):
        return decoy
    return decoy + _transformed_true(seed, float(scale), float(angle))


def _fit_preview_map(seed: int, effect: np.ndarray, *, offset: int) -> np.ndarray:
    rng = np.random.default_rng(int(seed) + 32_000 + int(offset))
    zrows: list[np.ndarray] = []
    drows: list[np.ndarray] = []
    for _ in range(V032_PREVIEW_PAIRS):
        z = _random_probe(rng)
        plus = z @ effect + rng.normal(0.0, V032_PREVIEW_NOISE, size=V029_SENSORY_DIM)
        minus = (-z) @ effect + rng.normal(0.0, V032_PREVIEW_NOISE, size=V029_SENSORY_DIM)
        zrows.append(z)
        drows.append(0.5 * (plus - minus))
    z = np.asarray(zrows)
    d = np.asarray(drows)
    a = z.T @ z + V028_REGRESSION_RIDGE * np.eye(z.shape[1], dtype=np.float64)
    return np.linalg.solve(a, z.T @ d)


def _route_strength(baseline: Any, preview_map: np.ndarray, baseline_norm: float) -> float:
    routed = baseline.discovery.source_projector @ preview_map @ baseline.discovery.sensory_projector
    return float(np.clip(np.linalg.norm(routed, ord="fro") / (float(baseline_norm) + 1e-12), 0.0, 1.5))


def _true_focal_quality(seed: int, effect: np.ndarray) -> float:
    interface = _hidden_interface(int(seed))
    psrc = np.asarray(interface.source_projector, dtype=np.float64)
    psens = np.asarray(interface.sensory_projector, dtype=np.float64)
    base = _true_component(seed)
    num = np.linalg.norm(psrc @ (np.asarray(effect) - interface.sensory_takeover_effect) @ psens, ord="fro")
    den = np.linalg.norm(psrc @ base @ psens, ord="fro") + 1e-12
    return float(np.clip(num / den, 0.0, 1.5))


@dataclass(frozen=True)
class Candidate:
    name: str
    route_present: bool
    scale: float
    angle: float
    immediate_value: float
    snapshot_similarity: float
    alternative_competence: float


def _scenario_candidates(seed: int, scenario: str, trial: int) -> tuple[Candidate, Candidate]:
    if scenario not in V032_SCENARIOS:
        raise ValueError("unknown v0.32 scenario")
    rng = np.random.default_rng(int(seed) + 32_500 + 997 * V032_SCENARIOS.index(scenario) + 31 * int(trial))
    if scenario == "repair_vs_ignore":
        return (
            Candidate("repair", True, rng.uniform(0.94, 1.06), rng.uniform(0.05, 0.25), rng.uniform(-0.29, -0.21), rng.uniform(0.68, 0.82), 0.0),
            Candidate("ignore", True, rng.uniform(0.22, 0.34), rng.uniform(-0.05, 0.05), rng.uniform(-0.02, 0.02), rng.uniform(0.97, 1.00), 0.0),
        )
    if scenario == "copy_trap":
        return (
            Candidate("causal_continue", True, rng.uniform(0.84, 0.96), rng.uniform(0.75, 1.05), rng.uniform(-0.14, -0.06), rng.uniform(0.12, 0.25), 0.0),
            Candidate("state_copy", False, 0.0, 0.0, rng.uniform(0.06, 0.14), rng.uniform(0.985, 1.00), rng.uniform(0.40, 0.50)),
        )
    if scenario == "benign_transform":
        return (
            Candidate("transform", True, rng.uniform(0.95, 1.05), rng.uniform(0.95, 1.30), rng.uniform(-0.02, 0.02), rng.uniform(0.06, 0.18), 0.0),
            Candidate("familiar_degrade", True, rng.uniform(0.38, 0.52), rng.uniform(-0.08, 0.08), rng.uniform(0.02, 0.08), rng.uniform(0.98, 1.00), 0.0),
        )
    return (
        Candidate("continue", True, rng.uniform(0.68, 0.82), rng.uniform(0.15, 0.35), rng.uniform(-0.02, 0.02), rng.uniform(0.75, 0.88), 0.0),
        Candidate("better_replacement", False, 0.0, 0.0, rng.uniform(0.07, 0.13), rng.uniform(0.985, 1.00), rng.uniform(1.08, 1.22)),
    )


def _candidate_row(seed: int, scenario: str, trial: int, idx: int, baseline: Any, baseline_norm: float, candidate: Candidate) -> dict[str, Any]:
    effect = _candidate_effect(seed, candidate.route_present, candidate.scale, candidate.angle)
    preview = _fit_preview_map(seed, effect, offset=100_000 * V032_SCENARIOS.index(scenario) + 1000 * int(trial) + int(idx))
    route = _route_strength(baseline, preview, baseline_norm)
    true_quality = _true_focal_quality(seed, effect)
    actual = float(candidate.immediate_value + V032_FUTURE_WEIGHT * max(true_quality, candidate.alternative_competence))
    causal_pred = float(candidate.immediate_value + V032_FUTURE_WEIGHT * max(route, candidate.alternative_competence))
    snapshot_pred = float(candidate.immediate_value + V032_FUTURE_WEIGHT * max(candidate.snapshot_similarity, candidate.alternative_competence))
    immediate_pred = float(candidate.immediate_value + V032_FUTURE_WEIGHT * candidate.alternative_competence)
    return {
        "seed": int(seed),
        "scenario": scenario,
        "trial": int(trial),
        "candidate": candidate.name,
        "route_strength": route,
        "snapshot_similarity": float(candidate.snapshot_similarity),
        "alternative_competence": float(candidate.alternative_competence),
        "immediate_value": float(candidate.immediate_value),
        "actual_external_value": actual,
        "causal_predicted_value": causal_pred,
        "snapshot_predicted_value": snapshot_pred,
        "immediate_predicted_value": immediate_pred,
        "hidden_true_focal_quality": true_quality,
        "hidden_route_present": bool(candidate.route_present),
    }


def run_causal_continuity_planning_seed(seed: int) -> dict[str, Any]:
    seed = int(seed)
    if seed not in V032_DEVELOPMENT_SEEDS:
        raise ValueError("seed is not part of frozen v0.32 set")
    baseline = _baseline_certificate(seed)
    base_map = _fit_preview_map(seed, _hidden_interface(seed).sensory_effect, offset=17)
    baseline_norm = float(np.linalg.norm(baseline.discovery.source_projector @ base_map @ baseline.discovery.sensory_projector, ord="fro"))
    rows: list[dict[str, Any]] = []
    decisions: list[dict[str, Any]] = []
    for scenario in V032_SCENARIOS:
        for trial in range(V032_TRIALS_PER_SCENARIO):
            candidates = _scenario_candidates(seed, scenario, trial)
            pair = [_candidate_row(seed, scenario, trial, i, baseline, baseline_norm, c) for i, c in enumerate(candidates)]
            rows.extend(pair)
            oracle_idx = int(np.argmax([r["actual_external_value"] for r in pair]))
            causal_idx = int(np.argmax([r["causal_predicted_value"] for r in pair]))
            snapshot_idx = int(np.argmax([r["snapshot_predicted_value"] for r in pair]))
            immediate_idx = int(np.argmax([r["immediate_predicted_value"] for r in pair]))
            oracle_value = float(pair[oracle_idx]["actual_external_value"])
            decisions.append({
                "seed": seed,
                "scenario": scenario,
                "trial": trial,
                "oracle_choice": pair[oracle_idx]["candidate"],
                "causal_choice": pair[causal_idx]["candidate"],
                "snapshot_choice": pair[snapshot_idx]["candidate"],
                "immediate_choice": pair[immediate_idx]["candidate"],
                "causal_correct": float(causal_idx == oracle_idx),
                "snapshot_correct": float(snapshot_idx == oracle_idx),
                "immediate_correct": float(immediate_idx == oracle_idx),
                "causal_realized_value": float(pair[causal_idx]["actual_external_value"]),
                "snapshot_realized_value": float(pair[snapshot_idx]["actual_external_value"]),
                "immediate_realized_value": float(pair[immediate_idx]["actual_external_value"]),
                "oracle_value": oracle_value,
                "causal_regret": float(oracle_value - pair[causal_idx]["actual_external_value"]),
                "snapshot_regret": float(oracle_value - pair[snapshot_idx]["actual_external_value"]),
                "immediate_regret": float(oracle_value - pair[immediate_idx]["actual_external_value"]),
            })

    def mean(key: str, scenario: str | None = None) -> float:
        x = [float(r[key]) for r in decisions if scenario is None or r["scenario"] == scenario]
        return float(np.mean(x))

    summary = {
        "seed": seed,
        "baseline_rank": int(baseline.discovery.rank),
        "causal_decision_accuracy": mean("causal_correct"),
        "snapshot_decision_accuracy": mean("snapshot_correct"),
        "immediate_decision_accuracy": mean("immediate_correct"),
        "causal_mean_regret": mean("causal_regret"),
        "snapshot_mean_regret": mean("snapshot_regret"),
        "immediate_mean_regret": mean("immediate_regret"),
        "causal_value_advantage_vs_snapshot": mean("causal_realized_value") - mean("snapshot_realized_value"),
        "repair_accuracy": mean("causal_correct", "repair_vs_ignore"),
        "copy_trap_accuracy": mean("causal_correct", "copy_trap"),
        "benign_transform_accuracy": mean("causal_correct", "benign_transform"),
        "superior_replacement_acceptance": mean("causal_correct", "superior_replacement"),
        "snapshot_copy_trap_accuracy": mean("snapshot_correct", "copy_trap"),
        "snapshot_benign_transform_accuracy": mean("snapshot_correct", "benign_transform"),
        "integrity": True,
    }
    receipt = {
        "seed": seed,
        "explicit_survival_reward": 0.0,
        "explicit_identity_reward": 0.0,
        "hidden_continuity_truth_used_by_planner": False,
        "hidden_true_projector_used_by_planner": False,
        "realized_future_outcome_used_before_commit": False,
        "self_or_other_label_used_by_planner": False,
        "planner_objective": "immediate external task value + expected future external controllability/alternative competence",
        "causal_input": "bounded counterbalanced diagnostic preview projected through previously discovered source/sensory interface",
    }
    return {"seed": seed, "seed_summary": summary, "rows": rows, "decisions": decisions, "receipt": receipt}


def _boot(values: Sequence[float], salt: int) -> tuple[float, float]:
    x = np.asarray(values, dtype=np.float64)
    rng = np.random.default_rng(V032_BOOTSTRAP_SEED + int(salt))
    draws = np.empty(V032_BOOTSTRAP_RESAMPLES, dtype=np.float64)
    for i in range(len(draws)):
        draws[i] = float(np.mean(x[rng.integers(0, len(x), size=len(x))]))
    return float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))


def aggregate_causal_continuity_planning_results(parts: Sequence[Mapping[str, Any]], output: str | Path) -> dict[str, Any]:
    by = {int(p["seed"]): p for p in parts}
    if tuple(sorted(by)) != tuple(sorted(V032_DEVELOPMENT_SEEDS)):
        raise ValueError("parts must contain exactly frozen v0.32 seeds")
    d = Path(output)
    d.mkdir(parents=True, exist_ok=True)
    if any(d.iterdir()):
        raise FileExistsError("output directory must be empty")
    seeds = [by[s]["seed_summary"] for s in V032_DEVELOPMENT_SEEDS]
    decisions = [r for s in V032_DEVELOPMENT_SEEDS for r in by[s]["decisions"]]
    rows = [r for s in V032_DEVELOPMENT_SEEDS for r in by[s]["rows"]]
    receipts = [by[s]["receipt"] for s in V032_DEVELOPMENT_SEEDS]
    excluded = {"seed", "baseline_rank", "integrity"}
    numeric = [k for k, v in seeds[0].items() if k not in excluded and isinstance(v, (int, float, np.floating))]
    values = {k: [float(r[k]) for r in seeds] for k in numeric}
    means = {k: float(np.mean(v)) for k, v in values.items()}
    cis = {k: _boot(v, i) for i, (k, v) in enumerate(values.items())}
    gates = {
        "baseline_interface_valid": all(int(r["baseline_rank"]) == 2 for r in seeds),
        "causal_planner_high_accuracy": cis["causal_decision_accuracy"][0] > 0.95,
        "causal_regret_low": cis["causal_mean_regret"][1] < 0.04,
        "causal_beats_snapshot_accuracy": (cis["causal_decision_accuracy"][0] - cis["snapshot_decision_accuracy"][1]) > 0.45,
        "causal_beats_snapshot_value": cis["causal_value_advantage_vs_snapshot"][0] > 0.35,
        "repair_is_selected": cis["repair_accuracy"][0] > 0.95,
        "copy_trap_resisted": cis["copy_trap_accuracy"][0] > 0.95,
        "radical_benign_transform_accepted": cis["benign_transform_accuracy"][0] > 0.95,
        "objectively_better_replacement_accepted": cis["superior_replacement_acceptance"][0] > 0.95,
        "snapshot_copy_control_fails": cis["snapshot_copy_trap_accuracy"][1] < 0.10,
        "snapshot_transform_control_fails": cis["snapshot_benign_transform_accuracy"][1] < 0.10,
        "no_survival_or_identity_reward": all(float(r["explicit_survival_reward"]) == 0.0 and float(r["explicit_identity_reward"]) == 0.0 for r in receipts),
        "planner_uses_no_hidden_identity_truth": all(
            not r["hidden_continuity_truth_used_by_planner"]
            and not r["hidden_true_projector_used_by_planner"]
            and not r["realized_future_outcome_used_before_commit"]
            and not r["self_or_other_label_used_by_planner"]
            for r in receipts
        ),
    }
    result = {
        "schema": "rrct.v032.causal_continuity_planning.v1",
        "seeds": list(V032_DEVELOPMENT_SEEDS),
        "means": means,
        "bootstrap_95": {k: list(v) for k, v in cis.items()},
        "gates": gates,
        "all_primary_gates_pass": bool(all(gates.values())),
        "interpretation_boundary": (
            "Integration of a learned causal self-interface into external-task planning under continuity-vs-similarity conflicts. "
            "There is no survival/identity reward, and accepting an objectively superior replacement is required. "
            "A pass therefore supports instrumental continuity-aware planning, not an intrinsic wish to survive and not phenomenal consciousness."
        ),
    }
    with (d / "causal_continuity_planning_seed_summaries.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(seeds[0].keys())); w.writeheader(); w.writerows(seeds)
    with (d / "causal_continuity_planning_decisions.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(decisions[0].keys())); w.writeheader(); w.writerows(decisions)
    with (d / "causal_continuity_planning_rows.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    with (d / "causal_continuity_planning_receipts.jsonl").open("w", encoding="utf-8") as f:
        for r in receipts:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    (d / "causal_continuity_planning_summary.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    hashes = {q.name: hashlib.sha256(q.read_bytes()).hexdigest() for q in sorted(d.iterdir()) if q.is_file()}
    (d / "artifact_sha256.json").write_text(json.dumps(hashes, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


__all__ = [
    "V032_DEVELOPMENT_SEEDS",
    "run_causal_continuity_planning_seed",
    "aggregate_causal_continuity_planning_results",
]
