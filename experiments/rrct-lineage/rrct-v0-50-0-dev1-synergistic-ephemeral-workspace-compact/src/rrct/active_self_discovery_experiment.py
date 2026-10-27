"""RRCT v0.29 active metacognitive self-discovery.

v0.28 could discover which unlabeled internal fluctuation sources mediate through
an actuator into later sensation, but an external schedule still supplied every
meta-intervention. v0.29 gives the learner a finite perturbation budget and
makes probe selection and stopping endogenous.

The active policy chooses the source-space direction with maximal posterior
regression uncertainty. It stops only when its *own* discovered provenance rank
and projector are stable across successive checkpoints, the causal-intersection
eigen-gap is clean, and causal-map uncertainty is sufficiently small. Hidden
source/projector/rank truth is never consulted by the policy or stopping rule.

Two unknown evidence regimes are used: low and high causal observation noise.
The hypothesis is that the same controller should stop early in clean evidence,
continue self-investigation under noisy evidence, and still recover/functionally
use the action-provenance interface. Random probing and externally structured
round-robin probing are matched controls.
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
    V028_SOURCE_DIM,
    _probe_explained_fraction,
    _subspace_precision,
    _subspace_recall,
    discover_action_provenance,
)

V029_DEVELOPMENT_SEEDS = (5601, 5607, 5613, 5619)
V029_INTERNAL_DIM = 8
V029_SENSORY_DIM = 12
V029_LOW_NOISE = 0.08
V029_HIGH_NOISE = 0.30
V029_MAX_PROBES = 480
V029_MIN_PROBES = 120
V029_CHECK_INTERVAL = 30
V029_STABLE_CHECKS = 2
V029_PROJECTOR_DRIFT_MAX = 0.05
V029_SELECTED_EIGEN_MIN = 0.97
V029_REJECTED_EIGEN_MAX = 0.55
V029_MAP_UNCERTAINTY_MAX = 0.05
V029_FIXED_LOW_BUDGET = 150
V029_EVALUATION_ROWS = 240
V029_BOOTSTRAP_SEED = 20_261_029
V029_BOOTSTRAP_RESAMPLES = 4000


def _orthogonal(rng: np.random.Generator, n: int) -> np.ndarray:
    q, _ = np.linalg.qr(rng.normal(size=(n, n)))
    return q


@dataclass(frozen=True)
class HiddenInterface:
    source_projector: np.ndarray
    internal_projector: np.ndarray
    sensory_projector: np.ndarray
    command_effect: np.ndarray
    sensory_effect: np.ndarray
    sensory_takeover_effect: np.ndarray
    sensory_remap_effect: np.ndarray


def _hidden_interface(seed: int) -> HiddenInterface:
    rng = np.random.default_rng(int(seed) + 29_001)
    qs = _orthogonal(rng, V028_SOURCE_DIM)
    qi = _orthogonal(rng, V029_INTERNAL_DIM)
    qo = _orthogonal(rng, V029_SENSORY_DIM)
    action_source, command_decoy, sensory_decoy = qs[:, :2], qs[:, 2:4], qs[:, 4:6]
    actuator, command_other = qi[:, :2], qi[:, 2:4]
    sensory_self, sensory_other = qo[:, :2], qo[:, 2:4]

    true_command = action_source @ np.diag([0.85, 0.72]) @ actuator.T
    decoy_command = command_decoy @ np.diag([1.20, 1.05]) @ command_other.T
    true_sensory = action_source @ np.diag([0.68, 0.58]) @ sensory_self.T
    decoy_sensory = sensory_decoy @ np.diag([1.30, 1.10]) @ sensory_other.T
    angle = 0.65
    remap = np.asarray([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]], dtype=np.float64)
    remapped_true = action_source @ (np.diag([0.68, 0.58]) @ remap) @ sensory_self.T
    return HiddenInterface(
        source_projector=action_source @ action_source.T,
        internal_projector=actuator @ actuator.T,
        sensory_projector=sensory_self @ sensory_self.T,
        command_effect=true_command + decoy_command,
        sensory_effect=true_sensory + decoy_sensory,
        sensory_takeover_effect=decoy_sensory,
        sensory_remap_effect=remapped_true + decoy_sensory,
    )


def _response(
    rng: np.random.Generator,
    z: np.ndarray,
    interface: HiddenInterface,
    noise: float,
    *,
    sensory_effect: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    current = rng.normal(0.0, 1.0, size=V029_SENSORY_DIM)
    command = z @ interface.command_effect + rng.normal(0.0, noise, size=V029_INTERNAL_DIM)
    effect = interface.sensory_effect if sensory_effect is None else np.asarray(sensory_effect, dtype=np.float64)
    nxt = 0.67 * current + z @ effect + rng.normal(0.0, noise, size=V029_SENSORY_DIM)
    return command, current, nxt


def _design_uncertainty(meta: np.ndarray, commands: np.ndarray, sensor: np.ndarray, next_sensor: np.ndarray) -> float:
    z = np.asarray(meta, dtype=np.float64)
    c = np.asarray(commands, dtype=np.float64)
    y = np.asarray(sensor, dtype=np.float64)
    nxt = np.asarray(next_sensor, dtype=np.float64)
    a = z.T @ z + V028_REGRESSION_RIDGE * np.eye(V028_SOURCE_DIM)
    inv = np.linalg.inv(a)
    bc = np.linalg.solve(a, z.T @ c)
    innovation = nxt - 0.67 * y
    bs = np.linalg.solve(a, z.T @ innovation)
    rc = c - z @ bc
    rs = innovation - z @ bs
    sigma = float(np.sqrt(0.5 * (np.mean(np.square(rc)) + np.mean(np.square(rs)))))
    return float(sigma * np.sqrt(np.max(np.linalg.eigvalsh(inv))))


def _active_probe(meta: list[np.ndarray], rng: np.random.Generator) -> np.ndarray:
    if not meta:
        inv = np.eye(V028_SOURCE_DIM) / V028_REGRESSION_RIDGE
    else:
        z = np.asarray(meta, dtype=np.float64)
        inv = np.linalg.inv(z.T @ z + V028_REGRESSION_RIDGE * np.eye(V028_SOURCE_DIM))
    values, vectors = np.linalg.eigh(inv)
    probe = vectors[:, int(np.argmax(values))]
    if rng.random() < 0.5:
        probe = -probe
    return np.asarray(probe, dtype=np.float64)


def _random_probe(rng: np.random.Generator) -> np.ndarray:
    z = rng.normal(size=V028_SOURCE_DIM)
    return z / (np.linalg.norm(z) + 1e-12)


def _round_robin_probe(step: int) -> np.ndarray:
    z = np.zeros(V028_SOURCE_DIM, dtype=np.float64)
    z[int(step) % V028_SOURCE_DIM] = 1.0 if ((int(step) // V028_SOURCE_DIM) % 2 == 0) else -1.0
    return z


@dataclass(frozen=True)
class SequentialDiscovery:
    policy: str
    noise: float
    probes: int
    stopped_by_confidence: bool
    discovery: Any
    meta: np.ndarray
    commands: np.ndarray
    sensor: np.ndarray
    next_sensor: np.ndarray
    final_uncertainty: float
    final_projector_drift: float


def run_sequential_discovery(seed: int, noise: float, policy: str) -> SequentialDiscovery:
    if policy not in {"active", "random", "round_robin"}:
        raise ValueError("unknown probe policy")
    interface = _hidden_interface(seed)
    rng = np.random.default_rng(int(seed) + 29_100 + {"active": 0, "random": 101, "round_robin": 211}[policy] + int(round(noise * 1000)))
    meta: list[np.ndarray] = []
    commands: list[np.ndarray] = []
    sensor: list[np.ndarray] = []
    next_sensor: list[np.ndarray] = []
    previous_projector: np.ndarray | None = None
    previous_rank: int | None = None
    stable = 0
    final_drift = float("inf")
    stopped = False

    for step in range(V029_MAX_PROBES):
        if policy == "active":
            z = _active_probe(meta, rng)
        elif policy == "random":
            z = _random_probe(rng)
        else:
            z = _round_robin_probe(step)
        c, y, nxt = _response(rng, z, interface, float(noise))
        meta.append(z); commands.append(c); sensor.append(y); next_sensor.append(nxt)

        n = len(meta)
        if n < V029_MIN_PROBES or n % V029_CHECK_INTERVAL:
            continue
        zz = np.asarray(meta); cc = np.asarray(commands); yy = np.asarray(sensor); nn = np.asarray(next_sensor)
        found = discover_action_provenance(zz, cc, yy, nn, seed=int(seed) + 29_500 + n)
        uncertainty = _design_uncertainty(zz, cc, yy, nn)
        rank = int(found.rank)
        if previous_projector is None or previous_rank is None or rank != previous_rank:
            final_drift = float("inf")
        else:
            denom = np.sqrt(max(1, rank))
            final_drift = float(np.linalg.norm(found.source_projector - previous_projector, ord="fro") / denom)
        values = np.asarray(found.intersection_eigenvalues, dtype=np.float64)
        selected_clean = rank > 0 and float(values[rank - 1]) > V029_SELECTED_EIGEN_MIN
        rejected_clean = rank >= len(values) or float(values[rank]) < V029_REJECTED_EIGEN_MAX
        confidence = (
            previous_rank == rank
            and selected_clean
            and rejected_clean
            and final_drift < V029_PROJECTOR_DRIFT_MAX
            and uncertainty < V029_MAP_UNCERTAINTY_MAX
        )
        stable = stable + 1 if confidence else 0
        previous_projector = found.source_projector.copy()
        previous_rank = rank
        if stable >= V029_STABLE_CHECKS:
            stopped = True
            break

    zz = np.asarray(meta); cc = np.asarray(commands); yy = np.asarray(sensor); nn = np.asarray(next_sensor)
    found = discover_action_provenance(zz, cc, yy, nn, seed=int(seed) + 29_900)
    uncertainty = _design_uncertainty(zz, cc, yy, nn)
    return SequentialDiscovery(policy, float(noise), len(meta), stopped, found, zz, cc, yy, nn, uncertainty, final_drift)


def _fixed_budget_discovery(seed: int, noise: float, budget: int) -> Any:
    interface = _hidden_interface(seed)
    rng = np.random.default_rng(int(seed) + 29_700 + int(round(noise * 1000)))
    zrows=[]; crows=[]; yrows=[]; nrows=[]
    for step in range(int(budget)):
        z = _round_robin_probe(step)
        c, y, nxt = _response(rng, z, interface, float(noise))
        zrows.append(z); crows.append(c); yrows.append(y); nrows.append(nxt)
    return discover_action_provenance(np.asarray(zrows), np.asarray(crows), np.asarray(yrows), np.asarray(nrows), seed=int(seed)+29_777)


def _matched_count_uncertainty(seed: int, noise: float, policy: str, count: int) -> float:
    interface = _hidden_interface(seed)
    rng = np.random.default_rng(int(seed) + 29_800 + {"random": 17, "round_robin": 29}[policy] + int(round(noise * 1000)))
    zrows=[]; crows=[]; yrows=[]; nrows=[]
    for step in range(int(count)):
        z = _random_probe(rng) if policy == "random" else _round_robin_probe(step)
        c, y, nxt = _response(rng, z, interface, float(noise))
        zrows.append(z); crows.append(c); yrows.append(y); nrows.append(nxt)
    return _design_uncertainty(np.asarray(zrows), np.asarray(crows), np.asarray(yrows), np.asarray(nrows))


def _functional_scores(seed: int, found: Any, noise: float) -> tuple[float, float]:
    interface = _hidden_interface(seed)
    out=[]
    for offset, effect in ((0, interface.sensory_remap_effect), (1, interface.sensory_takeover_effect)):
        rng=np.random.default_rng(int(seed)+30_100+offset+int(round(noise*1000)))
        z=[]; y=[]; nxt=[]
        for _ in range(V029_EVALUATION_ROWS):
            probe=_random_probe(rng)
            _, cur, n=_response(rng, probe, interface, float(noise), sensory_effect=effect)
            z.append(probe); y.append(cur); nxt.append(n)
        out.append(_probe_explained_fraction(np.asarray(y),np.asarray(z),np.asarray(nxt),found.source_projector,found.sensory_projector))
    return float(out[0]), float(out[1])


def run_active_self_discovery_seed(seed: int) -> dict[str, Any]:
    seed=int(seed)
    if seed not in V029_DEVELOPMENT_SEEDS:
        raise ValueError("seed is not part of frozen v0.29 set")
    interface=_hidden_interface(seed)
    records={}
    for regime,noise in (("low",V029_LOW_NOISE),("high",V029_HIGH_NOISE)):
        for policy in ("active","random","round_robin"):
            seq=run_sequential_discovery(seed,noise,policy)
            remap,take=_functional_scores(seed,seq.discovery,noise)
            records[(regime,policy)]={
                "probes":seq.probes,
                "stopped":seq.stopped_by_confidence,
                "rank":int(seq.discovery.rank),
                "source_recall":_subspace_recall(seq.discovery.source_projector,interface.source_projector),
                "source_precision":_subspace_precision(seq.discovery.source_projector,interface.source_projector),
                "internal_overlap":_subspace_recall(seq.discovery.internal_projector,interface.internal_projector),
                "sensory_overlap":_subspace_recall(seq.discovery.sensory_projector,interface.sensory_projector),
                "uncertainty":seq.final_uncertainty,
                "remap":remap,
                "takeover":take,
                "separation":remap-take,
            }
    fixed=_fixed_budget_discovery(seed,V029_HIGH_NOISE,V029_FIXED_LOW_BUDGET)
    low=records[("low","active")]; high=records[("high","active")]
    summary={
        "seed":seed,
        "active_low_probes":float(low["probes"]),
        "active_high_probes":float(high["probes"]),
        "noise_adaptive_probe_increase":float(high["probes"]-low["probes"]),
        "active_low_rank":int(low["rank"]),
        "active_high_rank":int(high["rank"]),
        "active_low_source_recall":float(low["source_recall"]),
        "active_high_source_recall":float(high["source_recall"]),
        "active_high_source_precision":float(high["source_precision"]),
        "active_high_internal_overlap":float(high["internal_overlap"]),
        "active_high_sensory_overlap":float(high["sensory_overlap"]),
        "active_high_separation":float(high["separation"]),
        "active_high_takeover":float(high["takeover"]),
        "random_high_probes":float(records[("high","random")]["probes"]),
        "round_high_probes":float(records[("high","round_robin")]["probes"]),
        "active_vs_random_high_probe_saving":float(records[("high","random")]["probes"]-high["probes"]),
        "active_vs_random_low_probe_saving":float(records[("low","random")]["probes"]-low["probes"]),
        "active_high_uncertainty":float(high["uncertainty"]),
        "random_high_uncertainty":float(records[("high","random")]["uncertainty"]),
        "uncertainty_advantage_vs_random":float(records[("high","random")]["uncertainty"]-high["uncertainty"]),
        "matched_random_high_uncertainty":float(_matched_count_uncertainty(seed,V029_HIGH_NOISE,"random",int(high["probes"]))),
        "matched_round_high_uncertainty":float(_matched_count_uncertainty(seed,V029_HIGH_NOISE,"round_robin",int(high["probes"]))),
        "matched_random_uncertainty_advantage":float(_matched_count_uncertainty(seed,V029_HIGH_NOISE,"random",int(high["probes"]))-high["uncertainty"]),
        "active_round_uncertainty_gap":float(high["uncertainty"]-_matched_count_uncertainty(seed,V029_HIGH_NOISE,"round_robin",int(high["probes"]))),
        "fixed_high_rank":int(fixed.rank),
        "fixed_high_source_recall":float(_subspace_recall(fixed.source_projector,interface.source_projector)),
        "active_high_recall_advantage_vs_fixed":float(high["source_recall"]-_subspace_recall(fixed.source_projector,interface.source_projector)),
        "integrity":bool(low["stopped"] and high["stopped"]),
    }
    return {
        "seed":seed,
        "seed_summary":summary,
        "records":{f"{k[0]}_{k[1]}":v for k,v in records.items()},
        "discovery_receipt":{
            "seed":seed,
            "hidden_rank_used_by_policy":False,
            "hidden_source_projector_used_by_policy":False,
            "hidden_internal_projector_used_by_policy":False,
            "hidden_sensory_projector_used_by_policy":False,
            "noise_regime_label_used_by_policy":False,
            "self_or_other_labels_used_by_policy":False,
            "probe_direction_rule":"largest posterior source-space regression uncertainty",
            "stop_rule":"stable discovered rank/projector + causal-intersection eigengap + posterior map uncertainty",
        },
    }


def _boot(values: Sequence[float], salt: int) -> tuple[float,float]:
    x=np.asarray(values,dtype=np.float64);rng=np.random.default_rng(V029_BOOTSTRAP_SEED+int(salt));draw=np.empty(V029_BOOTSTRAP_RESAMPLES)
    for i in range(len(draw)): draw[i]=float(np.mean(x[rng.integers(0,len(x),size=len(x))]))
    return float(np.quantile(draw,.025)),float(np.quantile(draw,.975))


def aggregate_active_self_discovery_results(parts: Sequence[Mapping[str,Any]], output: str|Path) -> dict[str,Any]:
    by={int(p["seed"]):p for p in parts}
    if tuple(sorted(by))!=tuple(sorted(V029_DEVELOPMENT_SEEDS)): raise ValueError("parts must contain exactly frozen v0.29 seeds")
    d=Path(output);d.mkdir(parents=True,exist_ok=True)
    if any(d.iterdir()): raise FileExistsError("output directory must be empty")
    rows=[by[s]["seed_summary"] for s in V029_DEVELOPMENT_SEEDS]
    numeric=[k for k,v in rows[0].items() if k not in {"seed","integrity","active_low_rank","active_high_rank","fixed_high_rank"} and isinstance(v,(int,float,np.floating))]
    vals={k:[float(r[k]) for r in rows] for k in numeric}; means={k:float(np.mean(v)) for k,v in vals.items()}; cis={k:_boot(v,i) for i,(k,v) in enumerate(vals.items())}
    gates={
      "active_self_certifies_before_cap":all(bool(r["integrity"]) for r in rows),
      "rank_discovery_stays_correct":all(int(r["active_low_rank"])==2 and int(r["active_high_rank"])==2 for r in rows),
      "clean_evidence_recovers_source":cis["active_low_source_recall"][0]>.98,
      "noisy_evidence_recovers_source":cis["active_high_source_recall"][0]>.97,
      "noisy_source_precision":cis["active_high_source_precision"][0]>.97,
      "noisy_internal_interface":cis["active_high_internal_overlap"][0]>.93,
      "noisy_sensory_interface":cis["active_high_sensory_overlap"][0]>.92,
      "self_other_use_survives_noise":cis["active_high_separation"][0]>.28,
      "takeover_rejected_under_noise":cis["active_high_takeover"][1]<.05,
      "probing_duration_adapts_to_noise":cis["noise_adaptive_probe_increase"][0]>120.0,
      "active_is_no_worse_than_structured_schedule":means["active_high_probes"]<=means["round_high_probes"]+45.0,
      "active_reduces_worst_direction_uncertainty_vs_random":cis["matched_random_uncertainty_advantage"][0]>0.0,
      "active_matches_structured_design_uncertainty":cis["active_round_uncertainty_gap"][1]<0.01,
      "fixed_clean_budget_is_inadequate_when_noisy":means["fixed_high_source_recall"]<.90,
      "active_repairs_fixed_budget_failure":cis["active_high_recall_advantage_vs_fixed"][0]>.08,
      "policy_uses_no_identity_or_noise_truth":all(not any([p["discovery_receipt"]["hidden_rank_used_by_policy"],p["discovery_receipt"]["hidden_source_projector_used_by_policy"],p["discovery_receipt"]["hidden_internal_projector_used_by_policy"],p["discovery_receipt"]["hidden_sensory_projector_used_by_policy"],p["discovery_receipt"]["noise_regime_label_used_by_policy"],p["discovery_receipt"]["self_or_other_labels_used_by_policy"]]) for p in parts),
    }
    result={"schema":"rrct.v029.active_self_discovery.v1","seeds":list(V029_DEVELOPMENT_SEEDS),"means":means,"bootstrap_95":{k:list(v) for k,v in cis.items()},"gates":gates,"all_primary_gates_pass":bool(all(gates.values())),"interpretation_boundary":"Endogenous selection and stopping of bounded self-directed causal probes for action-provenance discovery in a synthetic interface. This is functional metacognitive self-investigation, not evidence of phenomenal consciousness or subjective experience."}
    with (d/"active_self_discovery_seed_summaries.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys()));w.writeheader();w.writerows(rows)
    (d/"active_self_discovery_summary.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    hashes={q.name:hashlib.sha256(q.read_bytes()).hexdigest() for q in sorted(d.iterdir()) if q.is_file()}
    (d/"artifact_sha256.json").write_text(json.dumps(hashes,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return result

__all__=["V029_DEVELOPMENT_SEEDS","run_sequential_discovery","run_active_self_discovery_seed","aggregate_active_self_discovery_results"]
