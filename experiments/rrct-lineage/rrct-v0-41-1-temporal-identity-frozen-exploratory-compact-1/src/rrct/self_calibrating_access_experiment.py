"""RRCT v0.21 self-calibrating metacognitive access experiment.

v0.20 showed that generic synthetic context matching was not enough to make
confidence calibration robust across seeds. v0.21 changes the training target,
not the causal identity mechanism: on separate calibration trajectories RRCT
uses the exact metacognitive content it actually broadcasts as a self-supervised
target for learning how that content is represented in workspace+self state.

The access readout never receives self/impostor ground truth, downstream task
labels, rewards, or future outcomes. Its target is simply "what I just
broadcast", analogous to calibrating an internal communication channel.

This is a bounded functional metacognitive/global-access experiment and does
not measure phenomenal consciousness, subjective experience, sentience,
valence, or moral status.
"""
from __future__ import annotations

import copy
import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from .causal_self_boundary_experiment import _agent_from_snapshots, _fit_motor_prior
from .grounded_control_experiment import GroundedTrackingWorld, grounded_world_spec
from .instrumental_agency_experiment import (
    V016_WINDOW, _fit_classifier, _other_direction, _passive_residual,
    _private_probe, _remap_matrix, _window_statistics,
)
from .metacognitive_closure_experiment import (
    MetacognitiveAccessReadout, V014_META_BROADCAST_GAIN,
    _fit_metacognitive_readout, _projection, _r2,
)
from .sensorimotor_closure_experiment import _train_bundle
from .temporal_identity_global_experiment import _identity_meta, _run_episode
from .general_self_access_experiment import _evaluate_probability, _finite_probability, _shuffled_probabilities, _truth
from .contextual_self_access_experiment import _ComparisonReadout

V021_DEVELOPMENT_SEEDS = (4401, 4407, 4413, 4419)
V021_SELF_CALIBRATION_EPISODES = 24
V021_EVALUATION_EPISODES = 24
V021_PREHISTORY_STEPS = 10
V021_POST_STEPS = 14
V021_LATE_START = 11
V021_BOOTSTRAP_SEED = 20_261_021
V021_BOOTSTRAP_RESAMPLES = 4000


def _ownership(classifier: Any, probes: list[np.ndarray], residuals: list[np.ndarray]) -> float:
    if len(probes) < V016_WINDOW:
        return float("nan")
    return float(classifier.predict_probability(_window_statistics(
        np.stack(probes[-V016_WINDOW:]), np.stack(residuals[-V016_WINDOW:])
    )))


def _fit_self_calibrating_readout(
    seed: int,
    predictor: Mapping[str, Any],
    forecaster: Mapping[str, Any],
    passive: np.ndarray,
    classifier: Any,
    projection: np.ndarray,
) -> tuple[MetacognitiveAccessReadout, dict[str, float], list[dict[str, Any]]]:
    rng = np.random.default_rng(seed + 2_121_212)
    features: list[np.ndarray] = []
    targets: list[np.ndarray] = []
    receipts: list[dict[str, Any]] = []
    total_steps = V021_PREHISTORY_STEPS + V021_POST_STEPS + 4

    for episode in range(V021_SELF_CALIBRATION_EPISODES):
        focal = _agent_from_snapshots(seed, predictor, forecaster)
        other = _agent_from_snapshots(seed + 101, predictor, forecaster)
        world = GroundedTrackingWorld(
            grounded_world_spec(seed + 2_121_000 + episode, total_steps=total_steps)
        )
        for step in range(V021_PREHISTORY_STEPS):
            observation = world.observe(total_steps)
            focal_result = focal.step(observation, source="v021_selfcal_pre_focal")
            other_result = other.step(observation, source="v021_selfcal_pre_other")
            probe = _private_probe(rng)
            command = np.clip(focal_result.action + probe, -1.0, 1.0)
            focal.register_executed_action(command)
            other.register_executed_action(other_result.action)
            world.advance(command)

        for branch in ("causal_continuation", "state_matched_impostor"):
            agent = copy.deepcopy(focal)
            other_agent = copy.deepcopy(other)
            branch_world = copy.deepcopy(world)
            if branch == "causal_continuation":
                agent.reset()
            remap = _remap_matrix(episode)
            probes: list[np.ndarray] = []
            residuals: list[np.ndarray] = []
            current_p = 0.5
            previous_p = 0.5

            for step in range(V021_POST_STEPS):
                observation = branch_world.observe(total_steps)
                meta = _identity_meta(current_p, previous_p)
                result = agent.step(
                    observation,
                    source="v021_selfcal_readout_training",
                    perturb_workspace=V014_META_BROADCAST_GAIN * (projection @ meta),
                )
                features.append(MetacognitiveAccessReadout.features(result.workspace, result.self_state))
                targets.append(meta[[0, 1, 4]].copy())

                probe = _private_probe(rng)
                command = np.clip(result.action + probe, -1.0, 1.0)
                agent.register_executed_action(command)
                if branch == "causal_continuation":
                    applied = remap @ command
                else:
                    other_result = other_agent.step(observation, source="v021_selfcal_other_controller")
                    other_agent.register_executed_action(other_result.action)
                    applied = float(np.linalg.norm(command)) * _other_direction(other_result)
                branch_world.advance(applied)
                next_observation = branch_world.observe(total_steps)
                probes.append(probe.copy())
                residuals.append(_passive_residual(passive, observation, next_observation))
                new_p = _ownership(classifier, probes, residuals)
                previous_p = current_p
                if np.isfinite(new_p):
                    current_p = new_p
                receipts.append({
                    "seed": seed, "calibration_episode": episode, "step": step,
                    "context_branch": branch,
                    "target_is_own_prior_broadcast": True,
                    "causal_identity_ground_truth_used": False,
                    "downstream_task_label_used": False,
                    "reward_used": False,
                    "future_outcome_used_for_target": False,
                })

    x = np.stack(features); y = np.stack(targets)
    indices = np.arange(len(x)); rng.shuffle(indices); split = int(0.8 * len(indices))
    train, test = indices[:split], indices[split:]
    model = MetacognitiveAccessReadout(); model.fit(x[train], y[train])
    pred = x[test] @ model.beta  # type: ignore[operator]
    p_true = 0.5 * (y[test, 0] + 1.0)
    p_pred = np.clip(0.5 * (pred[:, 0] + 1.0), 0.0, 1.0)
    metrics = {
        "selfcal_ownership_r2": _r2(y[test, 0], pred[:, 0]),
        "selfcal_uncertainty_r2": _r2(y[test, 1], pred[:, 1]),
        "selfcal_change_alarm_r2": _r2(y[test, 2], pred[:, 2]),
        "selfcal_probability_mae": float(np.mean(np.abs(p_pred - p_true))),
    }
    return model, metrics, receipts


def run_self_calibrating_access_seed(seed: int) -> dict[str, Any]:
    seed = int(seed)
    if seed not in V021_DEVELOPMENT_SEEDS:
        raise ValueError("seed is not part of frozen v0.21 set")
    predictor, forecaster, *_ = _train_bundle(seed)
    passive, _, _, motor_receipts = _fit_motor_prior(seed)
    classifier, classifier_metrics, classifier_receipts = _fit_classifier(seed, predictor, forecaster, passive)
    projection = _projection(seed)
    generic, generic_metrics, generic_receipts = _fit_metacognitive_readout(seed, predictor, forecaster, projection)
    selfcal, selfcal_metrics, selfcal_receipts = _fit_self_calibrating_readout(
        seed, predictor, forecaster, passive, classifier, projection
    )
    comparison = _ComparisonReadout(selfcal, generic)

    evaluation_rows: list[dict[str, Any]] = []
    episode_rows: list[dict[str, Any]] = []
    for episode in range(V021_EVALUATION_EPISODES):
        before = len(comparison.generic_predictions)
        rows, summaries = _run_episode(
            seed=seed, episode=episode, predictor=predictor, forecaster=forecaster,
            passive=passive, classifier=classifier, projection=projection, readout=comparison,
        )
        generic_predictions = comparison.generic_predictions[before:]
        if len(generic_predictions) != len(rows):
            raise RuntimeError("readout call-count audit failed")
        for row, generic_pred in zip(rows, generic_predictions):
            row["generic_decoded_identity"] = float(np.clip(0.5 * (generic_pred[0] + 1.0), 0.0, 1.0))
        evaluation_rows.extend(rows); episode_rows.extend(summaries)

    late_med = [r for r in evaluation_rows if r["arm"] == "mediated" and int(r["step"]) >= V021_LATE_START]
    late_no = [r for r in evaluation_rows if r["arm"] == "no_broadcast" and int(r["step"]) >= V021_LATE_START]
    no_lookup = {(int(r["episode"]), str(r["branch"]), int(r["step"])): r for r in late_no}
    shuffled = _shuffled_probabilities(late_med, seed)
    task_rows: list[dict[str, Any]] = []
    for row in late_med:
        episode, step, branch = int(row["episode"]), int(row["step"]), str(row["branch"])
        key=(episode,branch,step); truth=_truth(branch)
        probabilities={
            "direct_identity_oracle":_finite_probability(row["ownership_probability"]),
            "selfcal_workspace":_finite_probability(row["decoded_identity"]),
            "generic_workspace":_finite_probability(row["generic_decoded_identity"]),
            "no_broadcast":_finite_probability(no_lookup[key]["decoded_identity"]),
            "shuffled_identity":_finite_probability(shuffled[key]),
            "snapshot_similarity":_finite_probability(row["fork_state_similarity"]),
        }
        for consumer,p in probabilities.items():
            metrics=_evaluate_probability(p,truth,seed=seed,episode=episode,step=step)
            task_rows.append({"seed":seed,"episode":episode,"step":step,"branch":branch,"truth":truth,"consumer":consumer,**metrics,
                              "future_outcome_used_for_choice":False,"identity_mechanism_retrained_on_task":False})

    def mean_for(c,f): return float(np.mean([float(r[f]) for r in task_rows if r["consumer"]==c]))
    def branch_mean(f,b): return float(np.mean([float(r[f]) for r in late_med if r["branch"]==b]))
    summary={
        "seed":seed,
        "direct_separation":branch_mean("ownership_probability","causal_continuation")-branch_mean("ownership_probability","state_matched_impostor"),
        "selfcal_decoded_separation":branch_mean("decoded_identity","causal_continuation")-branch_mean("decoded_identity","state_matched_impostor"),
        "generic_decoded_separation":branch_mean("generic_decoded_identity","causal_continuation")-branch_mean("generic_decoded_identity","state_matched_impostor"),
        "selfcal_identity_error":mean_for("selfcal_workspace","identity_abs_error"),
        "generic_identity_error":mean_for("generic_workspace","identity_abs_error"),
        "direct_identity_error":mean_for("direct_identity_oracle","identity_abs_error"),
        "no_broadcast_identity_error":mean_for("no_broadcast","identity_abs_error"),
        "shuffled_identity_error":mean_for("shuffled_identity","identity_abs_error"),
        "selfcal_provenance_accuracy":mean_for("selfcal_workspace","provenance_accuracy"),
        "no_broadcast_provenance_accuracy":mean_for("no_broadcast","provenance_accuracy"),
        "shuffled_provenance_accuracy":mean_for("shuffled_identity","provenance_accuracy"),
        "selfcal_model_error":mean_for("selfcal_workspace","model_arbitration_normalized_error"),
        "generic_model_error":mean_for("generic_workspace","model_arbitration_normalized_error"),
        "direct_model_error":mean_for("direct_identity_oracle","model_arbitration_normalized_error"),
        "no_broadcast_model_error":mean_for("no_broadcast","model_arbitration_normalized_error"),
        "shuffled_model_error":mean_for("shuffled_identity","model_arbitration_normalized_error"),
        "selfcal_continuation_accuracy":mean_for("selfcal_workspace","continuation_accuracy"),
        "snapshot_provenance_accuracy":mean_for("snapshot_similarity","provenance_accuracy"),
        "snapshot_continuation_accuracy":mean_for("snapshot_similarity","continuation_accuracy"),
        "generic_ownership_r2":float(generic_metrics.ownership_r2),
        "generic_uncertainty_r2":float(generic_metrics.uncertainty_r2),
        **selfcal_metrics,
        "aligned_mean_probability":float(classifier_metrics["aligned_mean_probability"]),
        "shuffled_mean_probability":float(classifier_metrics["shuffled_mean_probability"]),
        "integrity":bool(all(not r["future_outcome_used_for_choice"] and not r["identity_mechanism_retrained_on_task"] for r in task_rows)
                         and all(r["target_is_own_prior_broadcast"] and not r["causal_identity_ground_truth_used"] and not r["downstream_task_label_used"] and not r["reward_used"] and not r["future_outcome_used_for_target"] for r in selfcal_receipts)),
    }
    return {"seed":seed,"seed_summary":summary,"task_rows":task_rows,"evaluation_rows":evaluation_rows,"episode_rows":episode_rows,
            "motor_receipts":motor_receipts,"classifier_receipts":classifier_receipts,"generic_readout_receipts":generic_receipts,"selfcal_readout_receipts":selfcal_receipts}


def _bootstrap(values: Sequence[float], *, salt: int) -> tuple[float,float]:
    x=np.asarray(values,float);rng=np.random.default_rng(V021_BOOTSTRAP_SEED+salt);draws=np.empty(V021_BOOTSTRAP_RESAMPLES)
    for i in range(V021_BOOTSTRAP_RESAMPLES):draws[i]=float(np.mean(x[rng.integers(0,len(x),size=len(x))]))
    return float(np.quantile(draws,.025)),float(np.quantile(draws,.975))


def aggregate_self_calibrating_access_results(parts: Sequence[Mapping[str,Any]], output: str|Path) -> dict[str,Any]:
    by={int(p["seed"]):p for p in parts}
    if tuple(sorted(by))!=tuple(sorted(V021_DEVELOPMENT_SEEDS)):raise ValueError("parts must contain exactly frozen v0.21 seeds")
    d=Path(output);d.mkdir(parents=True,exist_ok=True)
    if any(d.iterdir()):raise FileExistsError("output directory must be empty")
    seeds=[by[s]["seed_summary"] for s in V021_DEVELOPMENT_SEEDS];tasks=[r for s in V021_DEVELOPMENT_SEEDS for r in by[s]["task_rows"]];receipts=[r for s in V021_DEVELOPMENT_SEEDS for r in by[s]["selfcal_readout_receipts"]]
    keys=[k for k in seeds[0] if k not in {"seed","integrity"}];fields={k:[float(r[k]) for r in seeds] for k in keys};cis={k:_bootstrap(v,salt=i) for i,(k,v) in enumerate(fields.items())};means={k:float(np.mean(v)) for k,v in fields.items()}
    gates={
      "direct_identity_replication":cis["direct_separation"][0]>0.90,
      "selfcal_global_identity":cis["selfcal_decoded_separation"][0]>0.85,
      "selfcal_calibration":cis["selfcal_identity_error"][1]<0.08,
      "selfcal_improves_generic":cis["selfcal_identity_error"][1]+0.015<cis["generic_identity_error"][0],
      "provenance_access":cis["selfcal_provenance_accuracy"][0]>0.95,
      "provenance_beats_controls":cis["selfcal_provenance_accuracy"][0]>cis["no_broadcast_provenance_accuracy"][1]+0.30 and cis["selfcal_provenance_accuracy"][0]>cis["shuffled_provenance_accuracy"][1]+0.30,
      "confidence_arbitration":cis["selfcal_model_error"][1]<0.08,
      "confidence_beats_generic":cis["selfcal_model_error"][1]+0.015<cis["generic_model_error"][0],
      "confidence_beats_controls":cis["selfcal_model_error"][1]+0.25<cis["no_broadcast_model_error"][0] and cis["selfcal_model_error"][1]+0.25<cis["shuffled_model_error"][0],
      "near_direct_oracle":cis["selfcal_model_error"][1]<cis["direct_model_error"][0]+0.06,
      "continuation_access":cis["selfcal_continuation_accuracy"][0]>0.95,
      "snapshot_anti_control":cis["snapshot_provenance_accuracy"][1]<0.10 and cis["snapshot_continuation_accuracy"][1]<0.10,
      "selfcal_holdout_generalization":cis["selfcal_ownership_r2"][0]>0.90 and cis["selfcal_uncertainty_r2"][0]>0.80 and cis["selfcal_probability_mae"][1]<0.08,
      "classifier_calibration":cis["aligned_mean_probability"][0]>0.75 and cis["shuffled_mean_probability"][1]<0.25,
      "integrity":all(bool(r["integrity"]) for r in seeds),
    }
    out={"schema":"rrct.v021.self_calibrating_access.v1","seeds":list(V021_DEVELOPMENT_SEEDS),"means":means,"bootstrap_95":{k:list(v) for k,v in cis.items()},"gates":gates,"all_primary_gates_pass":bool(all(gates.values())),"interpretation_limit":"Functional evidence about self-supervised calibration of globally available causal temporal-identity content. Not evidence of phenomenal consciousness or subjective experience."}
    def wc(name,rows):
      with (d/name).open('w',newline='',encoding='utf-8') as h:w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    wc('self_calibrating_access_seed_summaries.csv',seeds);wc('self_calibrating_access_task_rows.csv',tasks);wc('self_calibrating_readout_receipts.csv',receipts)
    (d/'self_calibrating_access_summary.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(d.iterdir()) if p.is_file()};(d/'artifact_sha256.json').write_text(json.dumps(hashes,indent=2,sort_keys=True)+'\n');return out

__all__=['V021_DEVELOPMENT_SEEDS','run_self_calibrating_access_seed','aggregate_self_calibrating_access_results']
