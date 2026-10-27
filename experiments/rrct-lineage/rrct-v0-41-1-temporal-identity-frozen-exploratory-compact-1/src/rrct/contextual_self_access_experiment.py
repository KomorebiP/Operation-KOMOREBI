"""RRCT v0.20 contextual metacognitive calibration experiment.

v0.19 showed that globally broadcast temporal identity is highly useful for
new downstream routing tasks, but its workspace readout remained slightly too
compressed for a strict confidence-sensitive oracle-closeness gate.

v0.20 tests a mechanistic repair: train the metacognitive access readout on
*synthetic identity/uncertainty broadcasts inside fork/remap contexts* rather
than only generic tracking contexts. Synthetic targets are sampled independently
of branch identity; the readout never receives causal-continuation labels,
downstream task labels, rewards, or future outcomes.

The causal ownership classifier, private instrument, broadcast projection, and
fork remain unchanged. Thus this version tests calibration of internal access,
not a stronger self detector.

This is a functional metacognitive/global-access experiment only and is not a
measure of phenomenal consciousness, subjective experience, sentience,
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
from .instrumental_agency_experiment import _fit_classifier, _other_direction, _private_probe, _remap_matrix
from .metacognitive_closure_experiment import (
    MetacognitiveAccessReadout,
    V014_META_BROADCAST_GAIN,
    _fit_metacognitive_readout,
    _projection,
    _r2,
)
from .sensorimotor_closure_experiment import _train_bundle
from .temporal_identity_global_experiment import _run_episode
from .general_self_access_experiment import _evaluate_probability, _finite_probability, _shuffled_probabilities, _truth

V020_DEVELOPMENT_SEEDS = (4301, 4307, 4313, 4319)
V020_CONTEXT_CALIBRATION_EPISODES = 32
V020_EVALUATION_EPISODES = 24
V020_PREHISTORY_STEPS = 10
V020_POST_STEPS = 14
V020_LATE_START = 11
V020_BOOTSTRAP_SEED = 20_261_020
V020_BOOTSTRAP_RESAMPLES = 4000


class _ComparisonReadout:
    """Return contextual prediction while recording the generic control."""
    def __init__(self, contextual: MetacognitiveAccessReadout, generic: MetacognitiveAccessReadout) -> None:
        self.contextual = contextual
        self.generic = generic
        self.generic_predictions: list[np.ndarray] = []

    def predict(self, workspace: np.ndarray, self_state: np.ndarray) -> np.ndarray:
        self.generic_predictions.append(self.generic.predict(workspace, self_state))
        return self.contextual.predict(workspace, self_state)


def _fit_contextual_readout(
    seed: int,
    predictor: Mapping[str, Any],
    forecaster: Mapping[str, Any],
    projection: np.ndarray,
) -> tuple[MetacognitiveAccessReadout, dict[str, float], list[dict[str, Any]]]:
    rng = np.random.default_rng(seed + 2_020_020)
    features: list[np.ndarray] = []
    targets: list[np.ndarray] = []
    receipts: list[dict[str, Any]] = []
    total_steps = V020_PREHISTORY_STEPS + V020_POST_STEPS + 4

    for episode in range(V020_CONTEXT_CALIBRATION_EPISODES):
        focal = _agent_from_snapshots(seed, predictor, forecaster)
        other = _agent_from_snapshots(seed + 101, predictor, forecaster)
        world = GroundedTrackingWorld(
            grounded_world_spec(seed + 2_020_000 + episode, total_steps=total_steps)
        )
        for step in range(V020_PREHISTORY_STEPS):
            observation = world.observe(total_steps)
            focal_result = focal.step(observation, source="v020_context_calibration_pre_focal")
            other_result = other.step(observation, source="v020_context_calibration_pre_other")
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
            for step in range(V020_POST_STEPS):
                observation = branch_world.observe(total_steps)
                meta = np.asarray(
                    [
                        rng.uniform(-1.0, 1.0),
                        rng.uniform(0.0, 1.0),
                        0.0,
                        0.0,
                        rng.uniform(0.0, 1.0),
                    ],
                    dtype=np.float64,
                )
                result = agent.step(
                    observation,
                    source="v020_contextual_readout_training",
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
                    other_result = other_agent.step(
                        observation, source="v020_contextual_readout_other_controller"
                    )
                    other_agent.register_executed_action(other_result.action)
                    applied = float(np.linalg.norm(command)) * _other_direction(other_result)
                branch_world.advance(applied)
                receipts.append(
                    {
                        "seed": seed,
                        "calibration_episode": episode,
                        "step": step,
                        "context_branch": branch,
                        "synthetic_meta_only": True,
                        "synthetic_target_independent_of_branch": True,
                        "causal_identity_label_used": False,
                        "downstream_task_label_used": False,
                        "future_outcome_used": False,
                    }
                )

    x = np.stack(features)
    y = np.stack(targets)
    indices = np.arange(len(x))
    rng.shuffle(indices)
    split = int(0.8 * len(indices))
    train, test = indices[:split], indices[split:]
    model = MetacognitiveAccessReadout()
    model.fit(x[train], y[train])
    pred = x[test] @ model.beta  # type: ignore[operator]
    metrics = {
        "context_ownership_r2": _r2(y[test, 0], pred[:, 0]),
        "context_uncertainty_r2": _r2(y[test, 1], pred[:, 1]),
        "context_change_alarm_r2": _r2(y[test, 2], pred[:, 2]),
    }
    return model, metrics, receipts


def run_contextual_self_access_seed(seed: int) -> dict[str, Any]:
    seed = int(seed)
    if seed not in V020_DEVELOPMENT_SEEDS:
        raise ValueError("seed is not part of frozen v0.20 set")
    predictor, forecaster, *_ = _train_bundle(seed)
    passive, _, _, motor_receipts = _fit_motor_prior(seed)
    classifier, classifier_metrics, classifier_receipts = _fit_classifier(seed, predictor, forecaster, passive)
    projection = _projection(seed)
    generic, generic_metrics, generic_receipts = _fit_metacognitive_readout(seed, predictor, forecaster, projection)
    contextual, contextual_metrics, contextual_receipts = _fit_contextual_readout(seed, predictor, forecaster, projection)
    comparison = _ComparisonReadout(contextual, generic)

    evaluation_rows: list[dict[str, Any]] = []
    episode_rows: list[dict[str, Any]] = []
    for episode in range(V020_EVALUATION_EPISODES):
        before = len(comparison.generic_predictions)
        rows, summaries = _run_episode(
            seed=seed, episode=episode, predictor=predictor, forecaster=forecaster,
            passive=passive, classifier=classifier, projection=projection, readout=comparison,
        )
        new_generic = comparison.generic_predictions[before:]
        if len(new_generic) != len(rows):
            raise RuntimeError("generic/contextual readout call audit failed")
        for row, generic_pred in zip(rows, new_generic):
            row["generic_decoded_identity"] = float(np.clip(0.5 * (generic_pred[0] + 1.0), 0.0, 1.0))
            row["generic_decoded_uncertainty"] = float(generic_pred[1])
        evaluation_rows.extend(rows)
        episode_rows.extend(summaries)

    late_mediated = [r for r in evaluation_rows if r["arm"] == "mediated" and int(r["step"]) >= V020_LATE_START]
    late_no = [r for r in evaluation_rows if r["arm"] == "no_broadcast" and int(r["step"]) >= V020_LATE_START]
    no_lookup = {(int(r["episode"]), str(r["branch"]), int(r["step"])): r for r in late_no}
    shuffled = _shuffled_probabilities(late_mediated, seed)

    task_rows: list[dict[str, Any]] = []
    for row in late_mediated:
        episode, step, branch = int(row["episode"]), int(row["step"]), str(row["branch"])
        key = (episode, branch, step)
        truth = _truth(branch)
        probs = {
            "direct_identity_oracle": _finite_probability(row["ownership_probability"]),
            "contextual_workspace": _finite_probability(row["decoded_identity"]),
            "generic_workspace": _finite_probability(row["generic_decoded_identity"]),
            "no_broadcast": _finite_probability(no_lookup[key]["decoded_identity"]),
            "shuffled_identity": _finite_probability(shuffled[key]),
            "snapshot_similarity": _finite_probability(row["fork_state_similarity"]),
        }
        for consumer, probability in probs.items():
            metrics = _evaluate_probability(probability, truth, seed=seed, episode=episode, step=step)
            task_rows.append({
                "seed": seed, "episode": episode, "step": step, "branch": branch,
                "truth": truth, "consumer": consumer, **metrics,
                "future_outcome_used_for_choice": False,
                "identity_mechanism_retrained_on_task": False,
            })

    def mean_for(consumer: str, field: str) -> float:
        return float(np.mean([float(r[field]) for r in task_rows if r["consumer"] == consumer]))

    def branch_mean(field: str, branch: str) -> float:
        vals = [float(r[field]) for r in late_mediated if r["branch"] == branch]
        return float(np.mean(vals))

    seed_summary = {
        "seed": seed,
        "direct_separation": branch_mean("ownership_probability", "causal_continuation") - branch_mean("ownership_probability", "state_matched_impostor"),
        "contextual_decoded_separation": branch_mean("decoded_identity", "causal_continuation") - branch_mean("decoded_identity", "state_matched_impostor"),
        "generic_decoded_separation": branch_mean("generic_decoded_identity", "causal_continuation") - branch_mean("generic_decoded_identity", "state_matched_impostor"),
        "contextual_identity_error": mean_for("contextual_workspace", "identity_abs_error"),
        "generic_identity_error": mean_for("generic_workspace", "identity_abs_error"),
        "direct_identity_error": mean_for("direct_identity_oracle", "identity_abs_error"),
        "no_broadcast_identity_error": mean_for("no_broadcast", "identity_abs_error"),
        "shuffled_identity_error": mean_for("shuffled_identity", "identity_abs_error"),
        "contextual_provenance_accuracy": mean_for("contextual_workspace", "provenance_accuracy"),
        "generic_provenance_accuracy": mean_for("generic_workspace", "provenance_accuracy"),
        "no_broadcast_provenance_accuracy": mean_for("no_broadcast", "provenance_accuracy"),
        "shuffled_provenance_accuracy": mean_for("shuffled_identity", "provenance_accuracy"),
        "contextual_model_error": mean_for("contextual_workspace", "model_arbitration_normalized_error"),
        "generic_model_error": mean_for("generic_workspace", "model_arbitration_normalized_error"),
        "direct_model_error": mean_for("direct_identity_oracle", "model_arbitration_normalized_error"),
        "no_broadcast_model_error": mean_for("no_broadcast", "model_arbitration_normalized_error"),
        "shuffled_model_error": mean_for("shuffled_identity", "model_arbitration_normalized_error"),
        "contextual_continuation_accuracy": mean_for("contextual_workspace", "continuation_accuracy"),
        "generic_continuation_accuracy": mean_for("generic_workspace", "continuation_accuracy"),
        "no_broadcast_continuation_accuracy": mean_for("no_broadcast", "continuation_accuracy"),
        "shuffled_continuation_accuracy": mean_for("shuffled_identity", "continuation_accuracy"),
        "snapshot_provenance_accuracy": mean_for("snapshot_similarity", "provenance_accuracy"),
        "snapshot_continuation_accuracy": mean_for("snapshot_similarity", "continuation_accuracy"),
        "generic_ownership_r2": float(generic_metrics.ownership_r2),
        "generic_uncertainty_r2": float(generic_metrics.uncertainty_r2),
        **contextual_metrics,
        "aligned_mean_probability": float(classifier_metrics["aligned_mean_probability"]),
        "shuffled_mean_probability": float(classifier_metrics["shuffled_mean_probability"]),
        "integrity": bool(all(
            not bool(r["future_outcome_used_for_choice"]) and not bool(r["identity_mechanism_retrained_on_task"])
            for r in task_rows
        ) and all(
            bool(r["synthetic_meta_only"]) and bool(r["synthetic_target_independent_of_branch"])
            and not bool(r["causal_identity_label_used"]) and not bool(r["downstream_task_label_used"])
            and not bool(r["future_outcome_used"])
            for r in contextual_receipts
        )),
    }
    return {
        "seed": seed, "seed_summary": seed_summary, "task_rows": task_rows,
        "evaluation_rows": evaluation_rows, "episode_rows": episode_rows,
        "motor_receipts": motor_receipts, "classifier_receipts": classifier_receipts,
        "generic_readout_receipts": generic_receipts,
        "contextual_readout_receipts": contextual_receipts,
    }


def _bootstrap(values: Sequence[float], *, salt: int) -> tuple[float, float]:
    x = np.asarray(values, dtype=np.float64)
    rng = np.random.default_rng(V020_BOOTSTRAP_SEED + int(salt))
    draws = np.empty(V020_BOOTSTRAP_RESAMPLES)
    for i in range(V020_BOOTSTRAP_RESAMPLES):
        draws[i] = float(np.mean(x[rng.integers(0, len(x), size=len(x))]))
    return float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))


def aggregate_contextual_self_access_results(parts: Sequence[Mapping[str, Any]], output: str | Path) -> dict[str, Any]:
    by_seed = {int(p["seed"]): p for p in parts}
    if tuple(sorted(by_seed)) != tuple(sorted(V020_DEVELOPMENT_SEEDS)):
        raise ValueError("parts must contain exactly frozen v0.20 seeds")
    destination = Path(output); destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()): raise FileExistsError("output directory must be empty")
    seed_rows = [by_seed[s]["seed_summary"] for s in V020_DEVELOPMENT_SEEDS]
    task_rows = [r for s in V020_DEVELOPMENT_SEEDS for r in by_seed[s]["task_rows"]]
    contextual_receipts = [r for s in V020_DEVELOPMENT_SEEDS for r in by_seed[s]["contextual_readout_receipts"]]
    keys = [k for k in seed_rows[0] if k not in {"seed", "integrity"}]
    fields = {k:[float(r[k]) for r in seed_rows] for k in keys}
    cis = {k:_bootstrap(v,salt=i) for i,(k,v) in enumerate(fields.items())}
    means = {k:float(np.mean(v)) for k,v in fields.items()}
    gates = {
        "direct_identity_replication": cis["direct_separation"][0] > 0.90,
        "contextual_global_identity": cis["contextual_decoded_separation"][0] > 0.85,
        "contextual_calibration": cis["contextual_identity_error"][1] < 0.08,
        "contextual_improves_generic_calibration": cis["contextual_identity_error"][1] + 0.02 < cis["generic_identity_error"][0],
        "provenance_access": cis["contextual_provenance_accuracy"][0] > 0.95,
        "provenance_beats_controls": cis["contextual_provenance_accuracy"][0] > cis["no_broadcast_provenance_accuracy"][1] + 0.30 and cis["contextual_provenance_accuracy"][0] > cis["shuffled_provenance_accuracy"][1] + 0.30,
        "confidence_arbitration": cis["contextual_model_error"][1] < 0.08,
        "confidence_arbitration_beats_generic": cis["contextual_model_error"][1] + 0.02 < cis["generic_model_error"][0],
        "confidence_arbitration_beats_controls": cis["contextual_model_error"][1] + 0.25 < cis["no_broadcast_model_error"][0] and cis["contextual_model_error"][1] + 0.25 < cis["shuffled_model_error"][0],
        "near_direct_oracle": cis["contextual_model_error"][1] < cis["direct_model_error"][0] + 0.06,
        "continuation_access": cis["contextual_continuation_accuracy"][0] > 0.95,
        "snapshot_anti_control": cis["snapshot_provenance_accuracy"][1] < 0.10 and cis["snapshot_continuation_accuracy"][1] < 0.10,
        "contextual_readout_generalizes": cis["context_ownership_r2"][0] > 0.90 and cis["context_uncertainty_r2"][0] > 0.60,
        "classifier_calibration": cis["aligned_mean_probability"][0] > 0.75 and cis["shuffled_mean_probability"][1] < 0.25,
        "integrity": all(bool(r["integrity"]) for r in seed_rows),
    }
    summary = {
        "schema":"rrct.v020.contextual_self_access.v1", "seeds":list(V020_DEVELOPMENT_SEEDS),
        "means":means, "bootstrap_95":{k:list(v) for k,v in cis.items()}, "gates":gates,
        "all_primary_gates_pass":bool(all(gates.values())),
        "interpretation_limit":"Functional evidence about context-calibrated global access to causal temporal-identity content. Not evidence of phenomenal consciousness or subjective experience.",
    }
    def write_csv(name,rows):
        with (destination/name).open('w',newline='',encoding='utf-8') as h:
            w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    write_csv('contextual_self_access_seed_summaries.csv',seed_rows)
    write_csv('contextual_self_access_task_rows.csv',task_rows)
    write_csv('contextual_readout_receipts.csv',contextual_receipts)
    (destination/'contextual_self_access_summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(destination.iterdir()) if p.is_file()}
    (destination/'artifact_sha256.json').write_text(json.dumps(hashes,indent=2,sort_keys=True)+'\n')
    return summary

__all__=['V020_DEVELOPMENT_SEEDS','run_contextual_self_access_seed','aggregate_contextual_self_access_results']
