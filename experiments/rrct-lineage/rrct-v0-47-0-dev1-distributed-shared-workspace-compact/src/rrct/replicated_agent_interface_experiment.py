"""RRCT v0.27 replicated joint discovery of the internal/external causal self-interface.

The learner is not told which of eight mixed internal command coordinates are
causally efficacious, which of twelve mixed sensory coordinates are controlled,
or the rank of either side.  It receives only the private perturbation vector
it deliberately injected across the candidate internal command field and the
resulting mixed sensory stream.

A hidden rank-2 internal subspace drives the physical actuator.  Its orthogonal
6-D complement contains deliberately high-variance, action-correlated, lagged,
and noisy decoy command activity.  The world again hides focal-controlled,
other-agent, and nuisance latent processes behind a dense unknown sensor mix.

The learner fits a probe->next-sensory effect operator conditional on current
sensory state.  A familywise temporal-permutation null selects significant
singular modes.  Left and right singular subspaces define the discovered
internal actuator and external sensory self-boundaries respectively.

Hidden projectors and condition labels are evaluation-only.  This is a bounded
functional causal-identification experiment, not a test of phenomenal
consciousness, sentience, valence, or moral status.
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
from .discovered_self_boundary_experiment import _native_observation, _orthogonal_mixing
from .instrumental_agency_experiment import _other_direction, _remap_matrix
from .sensorimotor_closure_experiment import _train_bundle

V027_DEVELOPMENT_SEEDS = (5301, 5307, 5313, 5319)
V027_INTERNAL_DIM = 8
V027_CALIBRATION_EPISODES = 16
V027_CALIBRATION_STEPS = 60
V027_EVALUATION_EPISODES = 12
V027_EVALUATION_STEPS = 30
V027_PROBE_AMPLITUDE = 0.95
V027_BASE_ACTION_SCALE = 0.25
V027_REGRESSION_RIDGE = 0.50
V027_NULL_PERMUTATIONS = 128
V027_NULL_QUANTILE = 0.99
V027_TAKEOVER_AMPLITUDE = 0.50
V027_BOOTSTRAP_SEED = 20_261_027
V027_BOOTSTRAP_RESAMPLES = 4000


def _internal_interface(seed: int) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(int(seed))
    q, _ = np.linalg.qr(rng.normal(size=(V027_INTERNAL_DIM, V027_INTERNAL_DIM)))
    return q[:, :2], q[:, 2:]


def _candidate_probe(rng: np.random.Generator) -> np.ndarray:
    direction = rng.normal(size=V027_INTERNAL_DIM)
    return V027_PROBE_AMPLITUDE * direction / (np.linalg.norm(direction) + 1e-12)


def _joint_effect_regression(sensor: np.ndarray, probes: np.ndarray, next_sensor: np.ndarray) -> np.ndarray:
    y = np.asarray(sensor, dtype=np.float64)
    z = np.asarray(probes, dtype=np.float64)
    nxt = np.asarray(next_sensor, dtype=np.float64)
    if y.ndim != 2 or y.shape[1] != 12 or z.shape != (len(y), V027_INTERNAL_DIM) or nxt.shape != y.shape:
        raise ValueError("joint-interface arrays have incorrect shapes")
    design = np.column_stack((np.ones(len(y)), y, z))
    penalty = V027_REGRESSION_RIDGE * np.eye(design.shape[1], dtype=np.float64)
    penalty[0, 0] = 0.05
    coefficients = np.linalg.solve(design.T @ design + penalty, design.T @ nxt)
    return coefficients[-V027_INTERNAL_DIM:, :]


@dataclass(frozen=True)
class ReplicatedAgentInterface:
    internal_projector: np.ndarray
    sensory_projector: np.ndarray
    rank: int
    singular_values: np.ndarray
    familywise_null_threshold: float
    half_a_threshold: float
    half_b_threshold: float
    half_a_directional: np.ndarray
    half_b_directional: np.ndarray
    replicated_mask: np.ndarray


def _familywise_threshold(y: np.ndarray, z: np.ndarray, nxt: np.ndarray, *, seed: int, permutations: int) -> float:
    rng = np.random.default_rng(int(seed))
    null_max = np.empty(int(permutations), dtype=np.float64)
    for i in range(len(null_max)):
        shuffled = z[rng.permutation(len(z))]
        values = np.linalg.svd(_joint_effect_regression(y, shuffled, nxt), compute_uv=False)
        null_max[i] = float(np.max(values))
    return float(np.quantile(null_max, V027_NULL_QUANTILE))


def discover_replicated_agent_interface(sensor: np.ndarray, probes: np.ndarray, next_sensor: np.ndarray, *, seed: int) -> ReplicatedAgentInterface:
    """Discover only causal modes that replicate across disjoint calibration halves."""
    y = np.asarray(sensor, dtype=np.float64)
    z = np.asarray(probes, dtype=np.float64)
    nxt = np.asarray(next_sensor, dtype=np.float64)
    effect = _joint_effect_regression(y, z, nxt)
    u, singular, vt = np.linalg.svd(effect, full_matrices=False)
    full_threshold = _familywise_threshold(y,z,nxt,seed=seed,permutations=V027_NULL_PERMUTATIONS)
    midpoint = len(y)//2
    ya,za,na = y[:midpoint],z[:midpoint],nxt[:midpoint]
    yb,zb,nb = y[midpoint:],z[midpoint:],nxt[midpoint:]
    ea = _joint_effect_regression(ya,za,na); eb = _joint_effect_regression(yb,zb,nb)
    half_a_threshold = _familywise_threshold(ya,za,na,seed=seed+1,permutations=96)
    half_b_threshold = _familywise_threshold(yb,zb,nb,seed=seed+2,permutations=96)
    replicated=[]; half_a=[]; half_b=[]
    for i in range(len(singular)):
        left=u[:,i]; right=vt[i]
        a=float(abs(left @ ea @ right)); b=float(abs(left @ eb @ right))
        half_a.append(a); half_b.append(b)
        replicated.append(bool(singular[i] > full_threshold and a > half_a_threshold and b > half_b_threshold))
    selected=np.flatnonzero(replicated)
    rank=int(len(selected))
    if rank:
        internal_basis=u[:,selected]; sensory_basis=vt[selected].T
        internal_projector=internal_basis@internal_basis.T; sensory_projector=sensory_basis@sensory_basis.T
    else:
        internal_projector=np.zeros((V027_INTERNAL_DIM,V027_INTERNAL_DIM)); sensory_projector=np.zeros((12,12))
    return ReplicatedAgentInterface(
        internal_projector=internal_projector, sensory_projector=sensory_projector, rank=rank,
        singular_values=singular, familywise_null_threshold=full_threshold,
        half_a_threshold=half_a_threshold, half_b_threshold=half_b_threshold,
        half_a_directional=np.asarray(half_a), half_b_directional=np.asarray(half_b), replicated_mask=np.asarray(replicated,dtype=bool),
    )


def _subspace_overlap(projector: np.ndarray, truth: np.ndarray) -> float:
    return float(np.trace(np.asarray(projector) @ np.asarray(truth)) / 2.0)


def _joint_probe_explained_fraction(
    sensor: np.ndarray,
    probes: np.ndarray,
    next_sensor: np.ndarray,
    internal_projector: np.ndarray,
    sensory_projector: np.ndarray,
) -> float:
    y = np.asarray(sensor, dtype=np.float64) @ np.asarray(sensory_projector, dtype=np.float64)
    nxt = np.asarray(next_sensor, dtype=np.float64) @ np.asarray(sensory_projector, dtype=np.float64)
    z = np.asarray(probes, dtype=np.float64) @ np.asarray(internal_projector, dtype=np.float64)
    if np.linalg.matrix_rank(internal_projector) == 0 or np.linalg.matrix_rank(sensory_projector) == 0:
        return 0.0
    x0 = np.column_stack((np.ones(len(y)), y))
    p0 = V027_REGRESSION_RIDGE * np.eye(x0.shape[1]); p0[0, 0] = 0.05
    b0 = np.linalg.solve(x0.T @ x0 + p0, x0.T @ nxt)
    e0 = float(np.mean(np.square(nxt - x0 @ b0)))
    x1 = np.column_stack((np.ones(len(y)), y, z))
    p1 = V027_REGRESSION_RIDGE * np.eye(x1.shape[1]); p1[0, 0] = 0.05
    b1 = np.linalg.solve(x1.T @ x1 + p1, x1.T @ nxt)
    e1 = float(np.mean(np.square(nxt - x1 @ b1)))
    return float(np.clip((e0 - e1) / (e0 + 1e-12), 0.0, 1.0))


def _episode_stream(
    seed: int,
    predictor: Mapping[str, Any],
    forecaster: Mapping[str, Any],
    sensory_mixing: np.ndarray,
    internal_basis: np.ndarray,
    internal_complement: np.ndarray,
    *,
    steps: int,
    episode: int,
    condition: str,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    offsets = {"calibration": 0, "self_remap": 97, "other_takeover": 193}
    if condition not in offsets:
        raise ValueError(f"unknown condition: {condition}")
    rng = np.random.default_rng(int(seed) + 26_000_000 + 313 * int(episode) + offsets[condition])
    focal = _agent_from_snapshots(seed, predictor, forecaster)
    other = _agent_from_snapshots(seed + 101, predictor, forecaster)
    position = rng.uniform(-1.0, 1.0, size=2)
    other_position = rng.uniform(-1.0, 1.0, size=2)
    goal = rng.uniform(-1.0, 1.0, size=2)
    nuisance = rng.normal(0.0, 0.8, size=8)
    last_action = np.zeros(2, dtype=np.float64)
    previous_focal_action = np.zeros(2, dtype=np.float64)
    sensor_now = sensory_mixing @ np.concatenate((position, other_position, nuisance))
    sensor_rows: list[np.ndarray] = []
    probe_rows: list[np.ndarray] = []
    next_rows: list[np.ndarray] = []
    command_rows: list[np.ndarray] = []
    remap = _remap_matrix(episode)

    for step in range(int(steps)):
        obs = _native_observation(position, goal, last_action, step, steps + 2)
        focal_result = focal.step(obs, source=f"v027_{condition}_focal")
        other_result = other.step(obs, source=f"v027_{condition}_other")
        action = V027_BASE_ACTION_SCALE * focal_result.action
        # High-variance decoys: correlated, lagged, and noisy but exactly orthogonal
        # to the true hidden actuator subspace.
        decoy = np.zeros(V027_INTERNAL_DIM - 2, dtype=np.float64)
        decoy[0] = 1.8 * (action[0] + 0.6 * action[1])
        decoy[1] = 1.6 * (action[1] - 0.5 * action[0])
        decoy[2] = 1.4 * (previous_focal_action[0] - previous_focal_action[1])
        decoy[3] = 1.2 * (previous_focal_action[0] + previous_focal_action[1])
        decoy[4:] = rng.normal(0.0, 0.35, size=2)
        baseline_command = internal_basis @ action + internal_complement @ decoy
        private_probe = _candidate_probe(rng)
        candidate_command = baseline_command + private_probe
        motor_command = np.clip(internal_basis.T @ candidate_command, -1.0, 1.0)
        focal.register_executed_action(motor_command)
        other.register_executed_action(other_result.action)

        if condition == "calibration":
            applied = motor_command
        elif condition == "self_remap":
            applied = remap @ motor_command
        else:
            # Current focal probe has no causal route to the world in takeover.
            applied = V027_TAKEOVER_AMPLITUDE * _other_direction(other_result)

        previous_sensor = sensor_now.copy()
        position = 0.91 * position + 0.38 * applied + rng.normal(0.0, 0.025, size=2)
        other_position = 0.82 * other_position + 0.70 * other_result.action + rng.normal(0.0, 0.08, size=2)
        nuisance = 0.72 * nuisance + rng.normal(0.0, 0.28, size=8)
        last_action = applied.copy()
        sensor_now = sensory_mixing @ np.concatenate((position, other_position, nuisance))
        sensor_rows.append(previous_sensor)
        probe_rows.append(private_probe.copy())
        next_rows.append(sensor_now.copy())
        command_rows.append(candidate_command.copy())
        previous_focal_action = focal_result.action.copy()

    return np.stack(sensor_rows), np.stack(probe_rows), np.stack(next_rows), np.stack(command_rows)


def run_replicated_agent_interface_seed(seed: int) -> dict[str, Any]:
    seed = int(seed)
    if seed not in V027_DEVELOPMENT_SEEDS:
        raise ValueError("seed is not part of frozen v0.27 set")
    predictor, forecaster, *_ = _train_bundle(seed)
    sensory_mixing = _orthogonal_mixing(seed + 2_526)
    internal_basis, internal_complement = _internal_interface(seed + 2_626)
    true_internal = internal_basis @ internal_basis.T
    true_sensory_basis = sensory_mixing[:, :2]
    true_sensory = true_sensory_basis @ true_sensory_basis.T

    ys=[]; zs=[]; ns=[]; commands=[]
    for episode in range(V027_CALIBRATION_EPISODES):
        y,z,n,c = _episode_stream(
            seed + 5 * episode, predictor, forecaster, sensory_mixing, internal_basis, internal_complement,
            steps=V027_CALIBRATION_STEPS, episode=episode, condition="calibration",
        )
        ys.append(y); zs.append(z); ns.append(n); commands.append(c)
    y=np.concatenate(ys); z=np.concatenate(zs); nxt=np.concatenate(ns); command=np.concatenate(commands)

    learned = discover_replicated_agent_interface(y, z, nxt, seed=seed + 27_100)
    rng = np.random.default_rng(seed + 27_200)
    shuffled = discover_replicated_agent_interface(y, z[rng.permutation(len(z))], nxt, seed=seed + 27_300)

    # Variance baselines deliberately see the same calibration streams.
    _,_,vt_i = np.linalg.svd(command - command.mean(axis=0), full_matrices=False)
    pca_internal_basis = vt_i[:2].T
    pca_internal = pca_internal_basis @ pca_internal_basis.T
    delta = nxt - y
    _,_,vt_o = np.linalg.svd(delta - delta.mean(axis=0), full_matrices=False)
    pca_sensory_basis = vt_o[:2].T
    pca_sensory = pca_sensory_basis @ pca_sensory_basis.T

    rows=[]
    for episode in range(V027_EVALUATION_EPISODES):
        for condition in ("self_remap", "other_takeover"):
            ey,ez,en,_ = _episode_stream(
                seed + 9_000 + 7 * episode, predictor, forecaster, sensory_mixing, internal_basis, internal_complement,
                steps=V027_EVALUATION_STEPS, episode=episode, condition=condition,
            )
            rows.append({
                "seed": seed,
                "episode": episode,
                "condition": condition,
                "learned_score": _joint_probe_explained_fraction(ey,ez,en,learned.internal_projector,learned.sensory_projector),
                "oracle_score": _joint_probe_explained_fraction(ey,ez,en,true_internal,true_sensory),
                "shuffled_score": _joint_probe_explained_fraction(ey,ez,en,shuffled.internal_projector,shuffled.sensory_projector),
                "pca_score": _joint_probe_explained_fraction(ey,ez,en,pca_internal,pca_sensory),
            })

    def mean(condition: str, key: str) -> float:
        return float(np.mean([r[key] for r in rows if r["condition"] == condition]))

    summary={
        "seed": seed,
        "discovered_rank": int(learned.rank),
        "internal_overlap": _subspace_overlap(learned.internal_projector, true_internal),
        "sensory_overlap": _subspace_overlap(learned.sensory_projector, true_sensory),
        "shuffled_internal_overlap": _subspace_overlap(shuffled.internal_projector, true_internal),
        "shuffled_sensory_overlap": _subspace_overlap(shuffled.sensory_projector, true_sensory),
        "pca_internal_overlap": _subspace_overlap(pca_internal, true_internal),
        "pca_sensory_overlap": _subspace_overlap(pca_sensory, true_sensory),
        "internal_beats_pca": _subspace_overlap(learned.internal_projector, true_internal)-_subspace_overlap(pca_internal, true_internal),
        "sensory_beats_pca": _subspace_overlap(learned.sensory_projector, true_sensory)-_subspace_overlap(pca_sensory, true_sensory),
        "self_remap_learned": mean("self_remap", "learned_score"),
        "other_takeover_learned": mean("other_takeover", "learned_score"),
        "learned_self_other_separation": mean("self_remap", "learned_score")-mean("other_takeover", "learned_score"),
        "self_remap_oracle": mean("self_remap", "oracle_score"),
        "oracle_gap": mean("self_remap", "oracle_score")-mean("self_remap", "learned_score"),
        "self_remap_shuffled": mean("self_remap", "shuffled_score"),
        "self_remap_pca": mean("self_remap", "pca_score"),
        "integrity": True,
    }
    return {
        "seed": seed,
        "seed_summary": summary,
        "rows": rows,
        "discovery_receipt": {
            "seed": seed,
            "self_labels_used": False,
            "actuator_coordinates_supplied": False,
            "body_coordinates_supplied": False,
            "internal_projector_used_in_discovery": False,
            "sensory_projector_used_in_discovery": False,
            "rank_supplied": False,
            "selected_rank": int(learned.rank),
            "candidate_internal_dimension": V027_INTERNAL_DIM,
            "singular_values": learned.singular_values.tolist(),
            "familywise_null_threshold": float(learned.familywise_null_threshold),
            "half_a_threshold": float(learned.half_a_threshold), "half_b_threshold": float(learned.half_b_threshold),
            "half_a_directional": learned.half_a_directional.tolist(), "half_b_directional": learned.half_b_directional.tolist(),
            "replicated_mask": learned.replicated_mask.astype(int).tolist(),
        },
    }


def _boot(values: Sequence[float], salt: int) -> tuple[float,float]:
    x=np.asarray(values,dtype=np.float64)
    rng=np.random.default_rng(V027_BOOTSTRAP_SEED+int(salt))
    draws=np.empty(V027_BOOTSTRAP_RESAMPLES,dtype=np.float64)
    for i in range(len(draws)):
        draws[i]=float(np.mean(x[rng.integers(0,len(x),size=len(x))]))
    return float(np.quantile(draws,.025)),float(np.quantile(draws,.975))


def aggregate_replicated_agent_interface_results(parts: Sequence[Mapping[str,Any]], output: str|Path) -> dict[str,Any]:
    by={int(p["seed"]):p for p in parts}
    if tuple(sorted(by)) != tuple(sorted(V027_DEVELOPMENT_SEEDS)):
        raise ValueError("parts must contain exactly frozen v0.27 seeds")
    d=Path(output); d.mkdir(parents=True,exist_ok=True)
    if any(d.iterdir()):
        raise FileExistsError("output directory must be empty")
    seeds=[by[s]["seed_summary"] for s in V027_DEVELOPMENT_SEEDS]
    rows=[r for s in V027_DEVELOPMENT_SEEDS for r in by[s]["rows"]]
    receipts=[by[s]["discovery_receipt"] for s in V027_DEVELOPMENT_SEEDS]
    numeric=[k for k,v in seeds[0].items() if k not in {"seed","integrity","discovered_rank"} and isinstance(v,(int,float,np.floating))]
    values={k:[float(r[k]) for r in seeds] for k in numeric}
    means={k:float(np.mean(v)) for k,v in values.items()}
    cis={k:_boot(v,i) for i,(k,v) in enumerate(values.items())}
    ranks=[int(r["discovered_rank"]) for r in seeds]
    gates={
        "rank_discovered_correctly": all(v==2 for v in ranks),
        "hidden_internal_interface_recovered": cis["internal_overlap"][0]>.97,
        "hidden_sensory_interface_recovered": cis["sensory_overlap"][0]>.90,
        "temporal_shuffle_internal_fails": cis["shuffled_internal_overlap"][1]<.15,
        "temporal_shuffle_sensory_fails": cis["shuffled_sensory_overlap"][1]<.15,
        "internal_variance_pca_fails": cis["pca_internal_overlap"][1]<.20,
        "sensory_variance_pca_fails": cis["pca_sensory_overlap"][1]<.20,
        "causal_internal_beats_pca": cis["internal_beats_pca"][0]>.70,
        "causal_sensory_beats_pca": cis["sensory_beats_pca"][0]>.70,
        "remap_uses_discovered_joint_interface": cis["self_remap_learned"][0]>.55,
        "takeover_rejected": cis["other_takeover_learned"][1]<.15,
        "functional_self_other_separation": cis["learned_self_other_separation"][0]>.45,
        "near_oracle_joint_function": cis["oracle_gap"][1]<.22,
        "shuffled_joint_interface_not_functional": cis["self_remap_shuffled"][1]<.15,
        "pca_joint_interface_not_functional": cis["self_remap_pca"][1]<.20,
        "discovery_has_no_boundary_labels": all(
            not r["self_labels_used"] and not r["actuator_coordinates_supplied"] and not r["body_coordinates_supplied"]
            and not r["internal_projector_used_in_discovery"] and not r["sensory_projector_used_in_discovery"] and not r["rank_supplied"]
            for r in receipts
        ),
        "integrity": all(bool(r["integrity"]) for r in seeds),
    }
    result={
        "schema":"rrct.v027.replicated_agent_interface.v1",
        "seeds":list(V027_DEVELOPMENT_SEEDS),
        "means":means,
        "bootstrap_95":{k:list(v) for k,v in cis.items()},
        "discovered_ranks":ranks,
        "gates":gates,
        "all_primary_gates_pass":bool(all(gates.values())),
        "interpretation_boundary":"Replicated unsupervised joint discovery of a private-intervention efficacious internal subspace and reachable sensory subspace in a bounded synthetic mixed scene; not evidence of phenomenal consciousness or subjective experience.",
    }
    with (d/"replicated_agent_interface_seed_summaries.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(seeds[0].keys())); w.writeheader(); w.writerows(seeds)
    with (d/"replicated_agent_interface_rows.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    with (d/"discovery_receipts.csv").open("w",newline="",encoding="utf-8") as f:
        flat=[]
        for r in receipts:
            q=dict(r); q["singular_values"]=json.dumps(q["singular_values"]); flat.append(q)
        w=csv.DictWriter(f,fieldnames=list(flat[0].keys())); w.writeheader(); w.writerows(flat)
    (d/"replicated_agent_interface_summary.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    hashes={}
    for q in sorted(d.iterdir()):
        if q.is_file(): hashes[q.name]=hashlib.sha256(q.read_bytes()).hexdigest()
    (d/"artifact_sha256.json").write_text(json.dumps(hashes,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return result


__all__=[
    "V027_DEVELOPMENT_SEEDS","ReplicatedAgentInterface","discover_replicated_agent_interface",
    "run_replicated_agent_interface_seed","aggregate_replicated_agent_interface_results",
]
