"""RRCT v0.25 discovery of a causal self-boundary from interventions.

Unlike earlier experiments, the learner is not told which sensory coordinates
belong to the controllable body/world interface.  A 12-D scene contains a
2-D focal-controlled latent process, a 2-D other-agent process, and 8 nuisance
processes, all hidden behind an unknown dense orthogonal sensor mixing.  RRCT
observes its native task state for ordinary control, while the boundary learner
receives only the mixed sensory stream and the private perturbations RRCT knows
it injected into its own motor command.

The learner discovers a sensory subspace by testing which singular directions
of the probe->next-sensory regression exceed a temporal-permutation null.  The
hidden true subspace and condition labels are used only by the evaluator.

This is a bounded functional causal-identification experiment.  It does not
measure phenomenal consciousness, subjective experience, sentience, valence,
or moral status.
"""
from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from .causal_self_boundary_experiment import _agent_from_snapshots
from .instrumental_agency_experiment import _other_direction, _remap_matrix
from .sensorimotor_closure_experiment import _train_bundle

V025_DEVELOPMENT_SEEDS = (5001, 5007, 5013, 5019)
V025_CALIBRATION_EPISODES = 8
V025_CALIBRATION_STEPS = 40
V025_EVALUATION_EPISODES = 12
V025_EVALUATION_STEPS = 28
V025_PROBE_AMPLITUDE = 0.70
V025_BASE_ACTION_SCALE = 0.30
V025_REGRESSION_RIDGE = 0.50
V025_NULL_PERMUTATIONS = 128
V025_NULL_QUANTILE = 0.99
V025_BOOTSTRAP_SEED = 20_261_025
V025_BOOTSTRAP_RESAMPLES = 4000


def _orthogonal_mixing(seed: int) -> np.ndarray:
    rng = np.random.default_rng(int(seed))
    q, _ = np.linalg.qr(rng.normal(size=(12, 12)))
    signs = np.sign(np.diag(q)); signs[signs == 0.0] = 1.0
    return q * signs


def _native_observation(position: np.ndarray, goal: np.ndarray, last_action: np.ndarray, step: int, total_steps: int) -> np.ndarray:
    error = goal - position
    x = np.zeros(12, dtype=np.float64)
    x[:2] = np.tanh(position / 1.5)
    x[2:4] = np.tanh(goal / 1.5)
    x[4:6] = np.tanh(error / 2.0)
    x[6] = min(step, total_steps - 1) / float(total_steps - 1)
    x[7] = 1.0 if step >= total_steps - 2 else 0.0
    x[8:10] = last_action
    x[10] = np.tanh(np.linalg.norm(error) / 2.0)
    x[11] = 1.0
    return x


def _probe(rng: np.random.Generator) -> np.ndarray:
    angle = float(rng.uniform(0.0, 2.0 * np.pi))
    return V025_PROBE_AMPLITUDE * np.asarray([np.cos(angle), np.sin(angle)], dtype=np.float64)


def _effect_regression(sensor: np.ndarray, probes: np.ndarray, next_sensor: np.ndarray) -> np.ndarray:
    y = np.asarray(sensor, dtype=np.float64); z = np.asarray(probes, dtype=np.float64); nxt = np.asarray(next_sensor, dtype=np.float64)
    if y.ndim != 2 or y.shape[1] != 12 or z.shape != (len(y), 2) or nxt.shape != y.shape:
        raise ValueError("boundary discovery arrays have incorrect shapes")
    design = np.column_stack((np.ones(len(y)), y, z))
    penalty = V025_REGRESSION_RIDGE * np.eye(design.shape[1], dtype=np.float64); penalty[0, 0] = 0.05
    coefficients = np.linalg.solve(design.T @ design + penalty, design.T @ nxt)
    return coefficients[-2:, :]


@dataclass(frozen=True)
class DiscoveredBoundary:
    projector: np.ndarray
    rank: int
    singular_values: np.ndarray
    null_thresholds: np.ndarray


def discover_self_boundary(sensor: np.ndarray, probes: np.ndarray, next_sensor: np.ndarray, *, seed: int) -> DiscoveredBoundary:
    """Discover the private-intervention reachable sensory subspace without labels."""
    y = np.asarray(sensor, dtype=np.float64); z = np.asarray(probes, dtype=np.float64); nxt = np.asarray(next_sensor, dtype=np.float64)
    effect = _effect_regression(y, z, nxt)
    _, singular, vt = np.linalg.svd(effect, full_matrices=False)
    rng = np.random.default_rng(int(seed))
    null = np.empty((V025_NULL_PERMUTATIONS, len(singular)), dtype=np.float64)
    for i in range(V025_NULL_PERMUTATIONS):
        shuffled = z[rng.permutation(len(z))]
        _, values, _ = np.linalg.svd(_effect_regression(y, shuffled, nxt), full_matrices=False)
        null[i] = values
    thresholds = np.quantile(null, V025_NULL_QUANTILE, axis=0)
    rank = int(np.sum(singular > thresholds))
    if rank:
        basis = vt[:rank].T
        projector = basis @ basis.T
    else:
        projector = np.zeros((12, 12), dtype=np.float64)
    return DiscoveredBoundary(projector=projector, rank=rank, singular_values=singular, null_thresholds=thresholds)


def _subspace_overlap(projector: np.ndarray, truth: np.ndarray) -> float:
    return float(np.trace(np.asarray(projector) @ np.asarray(truth)) / 2.0)


def _probe_explained_fraction(sensor: np.ndarray, probes: np.ndarray, next_sensor: np.ndarray, projector: np.ndarray) -> float:
    y = np.asarray(sensor) @ projector; nxt = np.asarray(next_sensor) @ projector; z = np.asarray(probes)
    if float(np.mean(nxt * nxt)) < 1e-14 or np.linalg.matrix_rank(projector) == 0:
        return 0.0
    x0 = np.column_stack((np.ones(len(y)), y)); p0 = V025_REGRESSION_RIDGE * np.eye(x0.shape[1]); p0[0, 0] = 0.05
    b0 = np.linalg.solve(x0.T @ x0 + p0, x0.T @ nxt); e0 = float(np.mean(np.square(nxt - x0 @ b0)))
    x1 = np.column_stack((np.ones(len(y)), y, z)); p1 = V025_REGRESSION_RIDGE * np.eye(x1.shape[1]); p1[0, 0] = 0.05
    b1 = np.linalg.solve(x1.T @ x1 + p1, x1.T @ nxt); e1 = float(np.mean(np.square(nxt - x1 @ b1)))
    return float(np.clip((e0 - e1) / (e0 + 1e-12), 0.0, 1.0))


def _episode_stream(seed: int, predictor: Mapping[str, Any], forecaster: Mapping[str, Any], mixing: np.ndarray, *, steps: int, episode: int, condition: str) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    rng = np.random.default_rng(int(seed) + 25_000_000 + 313 * int(episode) + (0 if condition == "calibration" else 97 if condition == "self_remap" else 193))
    focal = _agent_from_snapshots(seed, predictor, forecaster); other = _agent_from_snapshots(seed + 101, predictor, forecaster)
    position = rng.uniform(-1.0, 1.0, size=2); other_position = rng.uniform(-1.0, 1.0, size=2); goal = rng.uniform(-1.0, 1.0, size=2)
    nuisance = rng.normal(0.0, 0.8, size=8); last_action = np.zeros(2, dtype=np.float64)
    sensor_now = mixing @ np.concatenate((position, other_position, nuisance))
    sensor_rows=[]; probe_rows=[]; next_rows=[]; other_corr=[]; remap=_remap_matrix(episode)
    for step in range(int(steps)):
        obs = _native_observation(position, goal, last_action, step, steps + 2)
        focal_result = focal.step(obs, source=f"v025_{condition}_focal"); other_result = other.step(obs, source=f"v025_{condition}_other")
        base = V025_BASE_ACTION_SCALE * focal_result.action; candidate_probe = _probe(rng); command = np.clip(base + candidate_probe, -1.0, 1.0); executed_probe = command - base
        focal.register_executed_action(command); other.register_executed_action(other_result.action)
        if condition == "calibration": applied = command
        elif condition == "self_remap": applied = remap @ command
        elif condition == "other_takeover": applied = float(np.linalg.norm(command)) * _other_direction(other_result)
        else: raise ValueError(f"unknown condition: {condition}")
        previous = sensor_now.copy()
        position = 0.91 * position + 0.38 * applied + rng.normal(0.0, 0.025, size=2)
        # Deliberately make nonself dynamics higher variance than self motion.
        other_position = 0.82 * other_position + 0.70 * other_result.action + rng.normal(0.0, 0.08, size=2)
        nuisance = 0.72 * nuisance + rng.normal(0.0, 0.28, size=8)
        last_action = applied.copy(); sensor_now = mixing @ np.concatenate((position, other_position, nuisance))
        sensor_rows.append(previous); probe_rows.append(executed_probe.copy()); next_rows.append(sensor_now.copy())
        other_corr.append(float(np.dot(executed_probe, other_result.action)))
    return np.stack(sensor_rows), np.stack(probe_rows), np.stack(next_rows), float(np.mean(other_corr))


def run_discovered_self_boundary_seed(seed: int) -> dict[str, Any]:
    seed = int(seed)
    if seed not in V025_DEVELOPMENT_SEEDS: raise ValueError("seed is not part of frozen v0.25 set")
    predictor, forecaster, *_ = _train_bundle(seed)
    mixing = _orthogonal_mixing(seed + 2_525); true_basis = mixing[:, :2]; true_projector = true_basis @ true_basis.T
    ys=[]; zs=[]; ns=[]; corr=[]
    for episode in range(V025_CALIBRATION_EPISODES):
        y,z,n,c = _episode_stream(seed + 5 * episode, predictor, forecaster, mixing, steps=V025_CALIBRATION_STEPS, episode=episode, condition="calibration")
        ys.append(y); zs.append(z); ns.append(n); corr.append(c)
    y=np.concatenate(ys); z=np.concatenate(zs); nxt=np.concatenate(ns)
    learned = discover_self_boundary(y,z,nxt,seed=seed+25_100)
    rng=np.random.default_rng(seed+25_200); shuffled = discover_self_boundary(y,z[rng.permutation(len(z))],nxt,seed=seed+25_300)
    delta=nxt-y; _,_,vt=np.linalg.svd(delta-delta.mean(axis=0),full_matrices=False); pca_basis=vt[:2].T; pca_projector=pca_basis@pca_basis.T
    random_basis,_=np.linalg.qr(rng.normal(size=(12,2))); random_projector=random_basis@random_basis.T
    rows=[]
    for episode in range(V025_EVALUATION_EPISODES):
        for condition in ("self_remap","other_takeover"):
            ey,ez,en,_=_episode_stream(seed+9_000+7*episode,predictor,forecaster,mixing,steps=V025_EVALUATION_STEPS,episode=episode,condition=condition)
            rows.append({
                "seed":seed,"episode":episode,"condition":condition,
                "learned_score":_probe_explained_fraction(ey,ez,en,learned.projector),
                "oracle_score":_probe_explained_fraction(ey,ez,en,true_projector),
                "shuffled_score":_probe_explained_fraction(ey,ez,en,shuffled.projector),
                "pca_score":_probe_explained_fraction(ey,ez,en,pca_projector),
                "random_score":_probe_explained_fraction(ey,ez,en,random_projector),
            })
    def mean(condition:str,key:str)->float:
        return float(np.mean([r[key] for r in rows if r["condition"]==condition]))
    summary={
        "seed":seed,
        "discovered_rank":int(learned.rank),
        "learned_truth_overlap":_subspace_overlap(learned.projector,true_projector),
        "shuffled_truth_overlap":_subspace_overlap(shuffled.projector,true_projector),
        "pca_truth_overlap":_subspace_overlap(pca_projector,true_projector),
        "random_truth_overlap":_subspace_overlap(random_projector,true_projector),
        "learned_minus_pca_overlap":_subspace_overlap(learned.projector,true_projector)-_subspace_overlap(pca_projector,true_projector),
        "self_remap_learned":mean("self_remap","learned_score"),
        "other_takeover_learned":mean("other_takeover","learned_score"),
        "learned_self_other_separation":mean("self_remap","learned_score")-mean("other_takeover","learned_score"),
        "self_remap_oracle":mean("self_remap","oracle_score"),
        "oracle_gap":mean("self_remap","oracle_score")-mean("self_remap","learned_score"),
        "self_remap_shuffled":mean("self_remap","shuffled_score"),
        "self_remap_pca":mean("self_remap","pca_score"),
        "probe_other_action_dot":float(np.mean(corr)),
        "integrity":True,
    }
    return {"seed":seed,"seed_summary":summary,"rows":rows,"discovery_receipt":{
        "seed":seed,"labels_used":False,"true_projector_used_in_discovery":False,"body_coordinates_supplied":False,
        "rank_supplied":False,"null_permutations":V025_NULL_PERMUTATIONS,"selected_rank":int(learned.rank),
        "singular_values":learned.singular_values.tolist(),"null_thresholds":learned.null_thresholds.tolist(),
    }}


def _boot(values: Sequence[float], salt: int) -> tuple[float,float]:
    x=np.asarray(values,dtype=np.float64); rng=np.random.default_rng(V025_BOOTSTRAP_SEED+int(salt)); draws=np.empty(V025_BOOTSTRAP_RESAMPLES,dtype=np.float64)
    for i in range(len(draws)): draws[i]=float(np.mean(x[rng.integers(0,len(x),size=len(x))]))
    return float(np.quantile(draws,.025)),float(np.quantile(draws,.975))


def aggregate_discovered_self_boundary_results(parts: Sequence[Mapping[str,Any]], output: str|Path) -> dict[str,Any]:
    by={int(p["seed"]):p for p in parts}
    if tuple(sorted(by)) != tuple(sorted(V025_DEVELOPMENT_SEEDS)): raise ValueError("parts must contain exactly frozen v0.25 seeds")
    d=Path(output); d.mkdir(parents=True,exist_ok=True)
    if any(d.iterdir()): raise FileExistsError("output directory must be empty")
    seeds=[by[s]["seed_summary"] for s in V025_DEVELOPMENT_SEEDS]; rows=[r for s in V025_DEVELOPMENT_SEEDS for r in by[s]["rows"]]; receipts=[by[s]["discovery_receipt"] for s in V025_DEVELOPMENT_SEEDS]
    numeric=[k for k,v in seeds[0].items() if k not in {"seed","integrity","discovered_rank"} and isinstance(v,(int,float,np.floating))]
    values={k:[float(r[k]) for r in seeds] for k in numeric}; means={k:float(np.mean(v)) for k,v in values.items()}; cis={k:_boot(v,i) for i,(k,v) in enumerate(values.items())}
    rank_values=[int(r["discovered_rank"]) for r in seeds]
    gates={
        "rank_discovered_correctly":all(v==2 for v in rank_values),
        "hidden_subspace_recovered":cis["learned_truth_overlap"][0]>.90,
        "temporal_shuffle_fails":cis["shuffled_truth_overlap"][1]<.15,
        "variance_pca_fails":cis["pca_truth_overlap"][1]<.20,
        "causal_beats_pca":cis["learned_minus_pca_overlap"][0]>.65,
        "remap_uses_discovered_boundary":cis["self_remap_learned"][0]>.65,
        "takeover_rejected":cis["other_takeover_learned"][1]<.15,
        "functional_self_other_separation":cis["learned_self_other_separation"][0]>.55,
        "near_oracle_function":cis["oracle_gap"][1]<.18,
        "shuffled_boundary_not_functional":cis["self_remap_shuffled"][1]<.15,
        "pca_boundary_not_functional":cis["self_remap_pca"][1]<.20,
        "private_probe_not_other_policy":abs(cis["probe_other_action_dot"][0])<.08 and abs(cis["probe_other_action_dot"][1])<.08,
        "discovery_is_unsupervised":all(not r["labels_used"] and not r["true_projector_used_in_discovery"] and not r["body_coordinates_supplied"] and not r["rank_supplied"] for r in receipts),
        "integrity":all(bool(r["integrity"]) for r in seeds),
    }
    result={"schema":"rrct.v025.discovered_self_boundary.v1","seeds":list(V025_DEVELOPMENT_SEEDS),"means":means,"bootstrap_95":{k:list(v) for k,v in cis.items()},"discovered_ranks":rank_values,"gates":gates,"all_primary_gates_pass":bool(all(gates.values())),"interpretation_boundary":"Unsupervised discovery of a private-intervention reachable sensory subspace in a bounded synthetic mixed scene; not evidence of phenomenal consciousness or subjective experience."}
    with (d/"discovered_self_boundary_seed_summaries.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(seeds[0].keys()));w.writeheader();w.writerows(seeds)
    with (d/"discovered_self_boundary_rows.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys()));w.writeheader();w.writerows(rows)
    with (d/"discovery_receipts.csv").open("w",newline="") as f:
        flat=[]
        for r in receipts:
            q=dict(r);q["singular_values"]=json.dumps(q["singular_values"]);q["null_thresholds"]=json.dumps(q["null_thresholds"]);flat.append(q)
        w=csv.DictWriter(f,fieldnames=list(flat[0].keys()));w.writeheader();w.writerows(flat)
    (d/"discovered_self_boundary_summary.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    hashes={}
    for q in sorted(d.iterdir()):
        if q.is_file(): hashes[q.name]=hashlib.sha256(q.read_bytes()).hexdigest()
    (d/"artifact_sha256.json").write_text(json.dumps(hashes,indent=2,sort_keys=True)+"\n")
    return result
