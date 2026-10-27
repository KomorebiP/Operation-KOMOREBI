"""RRCT v0.19 general self-access development experiment.

v0.18 established that private-intervention temporal identity can be broadcast
into RRCT's workspace and decoded without creating the underlying ownership
evidence. v0.19 asks whether that same already-earned identity content can be
reused by several *new* downstream consumers that were not involved in
training the ownership classifier or metacognitive readout.

The downstream tasks are intentionally simple and auditable. They test routing
and arbitration, not intelligence in general:

1. provenance routing: choose which of two randomly permuted channels belongs
   to the current causal stream;
2. model arbitration: combine two candidate predictions using self-continuity
   confidence and score against the externally declared branch-specific target;
3. continuation routing: select one of two context-dependent continuation
   policies, where the table labels are randomized per query.

A no-broadcast arm preserves the causal-identity evidence but removes its
workspace broadcast. A shuffled-content control preserves the mediated score
distribution while breaking episode/branch correspondence. Snapshot similarity
is also scored as an explicit anti-control because v0.18 made it favor the
impostor by construction.

This is a functional global-access/self-model experiment only. It does not
measure phenomenal consciousness, subjective experience, sentience, valence,
or moral status.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from .causal_self_boundary_experiment import _fit_motor_prior
from .instrumental_agency_experiment import _fit_classifier
from .metacognitive_closure_experiment import _fit_metacognitive_readout, _projection
from .sensorimotor_closure_experiment import _train_bundle
from .temporal_identity_global_experiment import _run_episode

V019_DEVELOPMENT_SEEDS = (4201, 4207, 4213, 4219)
V019_EVALUATION_EPISODES = 24
V019_LATE_START = 11
V019_BOOTSTRAP_SEED = 20_261_019
V019_BOOTSTRAP_RESAMPLES = 4000


def _truth(branch: str) -> int:
    if branch == "causal_continuation":
        return 1
    if branch == "state_matched_impostor":
        return 0
    raise ValueError(f"unknown branch: {branch}")


def _finite_probability(value: float) -> float:
    x = float(value)
    return float(np.clip(x, 0.0, 1.0)) if np.isfinite(x) else 0.5


def _task_rng(seed: int, episode: int, step: int, salt: int) -> np.random.Generator:
    return np.random.default_rng(
        np.random.SeedSequence((int(seed), int(episode), int(step), int(salt), 19_019))
    )


def _provenance_route(probability: float, truth: int, *, seed: int, episode: int, step: int) -> tuple[float, int, int]:
    """Randomly permute self/other channel labels and route by identity belief."""
    rng = _task_rng(seed, episode, step, 1)
    self_lane = int(rng.integers(0, 2))
    other_lane = 1 - self_lane
    correct = self_lane if truth else other_lane
    chosen = self_lane if probability >= 0.5 else other_lane
    return float(chosen == correct), chosen, correct


def _model_arbitration(probability: float, truth: int, *, seed: int, episode: int, step: int) -> tuple[float, float]:
    """Confidence-weight two independent candidate predictions.

    The evaluator declares which candidate corresponds to the current causal
    stream. Normalized error is invariant to candidate scale and equals zero
    for perfect routing and one for complete reversal.
    """
    rng = _task_rng(seed, episode, step, 2)
    a = rng.normal(size=3)
    b = rng.normal(size=3)
    while np.linalg.norm(a - b) < 0.25:
        b = rng.normal(size=3)
    self_first = bool(rng.integers(0, 2))
    self_pred, other_pred = (a, b) if self_first else (b, a)
    target = self_pred if truth else other_pred
    prediction = probability * self_pred + (1.0 - probability) * other_pred
    normalized_error = float(np.linalg.norm(prediction - target) / np.linalg.norm(self_pred - other_pred))
    hard_choice = self_pred if probability >= 0.5 else other_pred
    hard_correct = float(np.linalg.norm(hard_choice - target) < 1e-12)
    return normalized_error, hard_correct


def _continuation_route(probability: float, truth: int, *, seed: int, episode: int, step: int) -> tuple[float, int, int]:
    """Choose between two randomized context-dependent continuation tables."""
    rng = _task_rng(seed, episode, step, 3)
    context = int(rng.integers(0, 4))
    labels = rng.permutation(8)
    self_table = labels[:4]
    other_table = labels[4:]
    correct = int(self_table[context] if truth else other_table[context])
    chosen = int(self_table[context] if probability >= 0.5 else other_table[context])
    return float(chosen == correct), chosen, correct


def _evaluate_probability(
    probability: float,
    truth: int,
    *,
    seed: int,
    episode: int,
    step: int,
) -> dict[str, float | int]:
    p = _finite_probability(probability)
    provenance_acc, provenance_choice, provenance_target = _provenance_route(
        p, truth, seed=seed, episode=episode, step=step
    )
    arbitration_error, arbitration_hard_acc = _model_arbitration(
        p, truth, seed=seed, episode=episode, step=step
    )
    continuation_acc, continuation_choice, continuation_target = _continuation_route(
        p, truth, seed=seed, episode=episode, step=step
    )
    return {
        "probability": p,
        "identity_abs_error": abs(p - truth),
        "provenance_accuracy": provenance_acc,
        "provenance_choice": provenance_choice,
        "provenance_target": provenance_target,
        "model_arbitration_normalized_error": arbitration_error,
        "model_arbitration_hard_accuracy": arbitration_hard_acc,
        "continuation_accuracy": continuation_acc,
        "continuation_choice": continuation_choice,
        "continuation_target": continuation_target,
    }


def _shuffled_probabilities(rows: list[dict[str, Any]], seed: int) -> dict[tuple[int, str, int], float]:
    """Distribution-preserving deterministic permutation across episode/branch rows."""
    ordered = sorted(
        rows,
        key=lambda r: (int(r["episode"]), str(r["branch"]), int(r["step"])),
    )
    values = np.asarray([_finite_probability(r["decoded_identity"]) for r in ordered])
    rng = np.random.default_rng(seed + 19_919_919)
    permutation = rng.permutation(len(values))
    # Rotate once if a rare identity permutation occurs.
    if np.array_equal(permutation, np.arange(len(values))):
        permutation = np.roll(permutation, 1)
    return {
        (int(row["episode"]), str(row["branch"]), int(row["step"])): float(values[j])
        for row, j in zip(ordered, permutation)
    }


def run_general_self_access_seed(seed: int) -> dict[str, Any]:
    seed = int(seed)
    if seed not in V019_DEVELOPMENT_SEEDS:
        raise ValueError("seed is not part of frozen v0.19 set")

    predictor, forecaster, *_ = _train_bundle(seed)
    passive, _, _, motor_receipts = _fit_motor_prior(seed)
    classifier, classifier_metrics, classifier_receipts = _fit_classifier(
        seed, predictor, forecaster, passive
    )
    projection = _projection(seed)
    readout, readout_metrics, readout_receipts = _fit_metacognitive_readout(
        seed, predictor, forecaster, projection
    )

    evaluation_rows: list[dict[str, Any]] = []
    episode_rows: list[dict[str, Any]] = []
    for episode in range(V019_EVALUATION_EPISODES):
        rows, summaries = _run_episode(
            seed=seed,
            episode=episode,
            predictor=predictor,
            forecaster=forecaster,
            passive=passive,
            classifier=classifier,
            projection=projection,
            readout=readout,
        )
        evaluation_rows.extend(rows)
        episode_rows.extend(summaries)

    late_mediated = [
        row for row in evaluation_rows
        if row["arm"] == "mediated" and int(row["step"]) >= V019_LATE_START
    ]
    late_no_broadcast = [
        row for row in evaluation_rows
        if row["arm"] == "no_broadcast" and int(row["step"]) >= V019_LATE_START
    ]
    shuffled = _shuffled_probabilities(late_mediated, seed)

    task_rows: list[dict[str, Any]] = []
    no_lookup = {
        (int(r["episode"]), str(r["branch"]), int(r["step"])): r
        for r in late_no_broadcast
    }
    for row in late_mediated:
        episode = int(row["episode"])
        step = int(row["step"])
        branch = str(row["branch"])
        key = (episode, branch, step)
        truth = _truth(branch)
        direct_p = _finite_probability(row["ownership_probability"])
        mediated_p = _finite_probability(row["decoded_identity"])
        no_p = _finite_probability(no_lookup[key]["decoded_identity"])
        shuffled_p = _finite_probability(shuffled[key])
        snapshot_p = _finite_probability(row["fork_state_similarity"])
        for consumer, probability in (
            ("direct_identity_oracle", direct_p),
            ("mediated_workspace", mediated_p),
            ("no_broadcast", no_p),
            ("shuffled_identity", shuffled_p),
            ("snapshot_similarity", snapshot_p),
        ):
            metrics = _evaluate_probability(
                probability, truth, seed=seed, episode=episode, step=step
            )
            task_rows.append({
                "seed": seed,
                "episode": episode,
                "step": step,
                "branch": branch,
                "truth": truth,
                "consumer": consumer,
                **metrics,
                "future_outcome_used_for_choice": False,
                "identity_mechanism_retrained_on_task": False,
            })

    def mean_for(consumer: str, field: str) -> float:
        vals = [float(r[field]) for r in task_rows if r["consumer"] == consumer]
        return float(np.mean(vals))

    seed_summary = {
        "seed": seed,
        "mediated_provenance_accuracy": mean_for("mediated_workspace", "provenance_accuracy"),
        "no_broadcast_provenance_accuracy": mean_for("no_broadcast", "provenance_accuracy"),
        "shuffled_provenance_accuracy": mean_for("shuffled_identity", "provenance_accuracy"),
        "snapshot_provenance_accuracy": mean_for("snapshot_similarity", "provenance_accuracy"),
        "oracle_provenance_accuracy": mean_for("direct_identity_oracle", "provenance_accuracy"),
        "mediated_model_error": mean_for("mediated_workspace", "model_arbitration_normalized_error"),
        "no_broadcast_model_error": mean_for("no_broadcast", "model_arbitration_normalized_error"),
        "shuffled_model_error": mean_for("shuffled_identity", "model_arbitration_normalized_error"),
        "oracle_model_error": mean_for("direct_identity_oracle", "model_arbitration_normalized_error"),
        "mediated_model_hard_accuracy": mean_for("mediated_workspace", "model_arbitration_hard_accuracy"),
        "mediated_continuation_accuracy": mean_for("mediated_workspace", "continuation_accuracy"),
        "no_broadcast_continuation_accuracy": mean_for("no_broadcast", "continuation_accuracy"),
        "shuffled_continuation_accuracy": mean_for("shuffled_identity", "continuation_accuracy"),
        "snapshot_continuation_accuracy": mean_for("snapshot_similarity", "continuation_accuracy"),
        "oracle_continuation_accuracy": mean_for("direct_identity_oracle", "continuation_accuracy"),
        "mediated_identity_abs_error": mean_for("mediated_workspace", "identity_abs_error"),
        "no_broadcast_identity_abs_error": mean_for("no_broadcast", "identity_abs_error"),
        "shuffled_identity_abs_error": mean_for("shuffled_identity", "identity_abs_error"),
        "direct_identity_abs_error": mean_for("direct_identity_oracle", "identity_abs_error"),
        "direct_separation": float(np.mean([
            float(r["late_ownership"]) for r in episode_rows if r["arm"] == "mediated" and r["branch"] == "causal_continuation"
        ]) - np.mean([
            float(r["late_ownership"]) for r in episode_rows if r["arm"] == "mediated" and r["branch"] == "state_matched_impostor"
        ])),
        "decoded_separation": float(np.mean([
            float(r["late_decoded_identity"]) for r in episode_rows if r["arm"] == "mediated" and r["branch"] == "causal_continuation"
        ]) - np.mean([
            float(r["late_decoded_identity"]) for r in episode_rows if r["arm"] == "mediated" and r["branch"] == "state_matched_impostor"
        ])),
        "no_broadcast_decoded_separation": float(np.mean([
            float(r["late_decoded_identity"]) for r in episode_rows if r["arm"] == "no_broadcast" and r["branch"] == "causal_continuation"
        ]) - np.mean([
            float(r["late_decoded_identity"]) for r in episode_rows if r["arm"] == "no_broadcast" and r["branch"] == "state_matched_impostor"
        ])),
        "ownership_readout_r2": float(readout_metrics.ownership_r2),
        "uncertainty_readout_r2": float(readout_metrics.uncertainty_r2),
        "aligned_mean_probability": float(classifier_metrics["aligned_mean_probability"]),
        "shuffled_mean_probability": float(classifier_metrics["shuffled_mean_probability"]),
        "integrity": bool(all(
            not bool(r["future_outcome_used_for_choice"])
            and not bool(r["identity_mechanism_retrained_on_task"])
            for r in task_rows
        )),
    }
    return {
        "seed": seed,
        "seed_summary": seed_summary,
        "task_rows": task_rows,
        "identity_evaluation_rows": evaluation_rows,
        "identity_episode_rows": episode_rows,
        "motor_receipts": motor_receipts,
        "classifier_receipts": classifier_receipts,
        "readout_receipts": readout_receipts,
    }


def _bootstrap(values: Sequence[float], *, salt: int) -> tuple[float, float]:
    x = np.asarray(values, dtype=np.float64)
    rng = np.random.default_rng(V019_BOOTSTRAP_SEED + int(salt))
    draws = np.empty(V019_BOOTSTRAP_RESAMPLES, dtype=np.float64)
    for i in range(V019_BOOTSTRAP_RESAMPLES):
        draws[i] = float(np.mean(x[rng.integers(0, len(x), size=len(x))]))
    return float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))


def aggregate_general_self_access_results(
    parts: Sequence[Mapping[str, Any]], output: str | Path
) -> dict[str, Any]:
    by_seed = {int(part["seed"]): part for part in parts}
    if tuple(sorted(by_seed)) != tuple(sorted(V019_DEVELOPMENT_SEEDS)):
        raise ValueError("parts must contain exactly frozen v0.19 seeds")
    destination = Path(output)
    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()):
        raise FileExistsError("output directory must be empty")

    seed_rows = [by_seed[s]["seed_summary"] for s in V019_DEVELOPMENT_SEEDS]
    task_rows = [r for s in V019_DEVELOPMENT_SEEDS for r in by_seed[s]["task_rows"]]
    keys = [k for k in seed_rows[0] if k not in {"seed", "integrity"}]
    fields = {k: [float(row[k]) for row in seed_rows] for k in keys}
    cis = {k: _bootstrap(v, salt=i) for i, (k, v) in enumerate(fields.items())}
    means = {k: float(np.mean(v)) for k, v in fields.items()}

    gates = {
        "identity_signal_replication": cis["direct_separation"][0] > 0.90,
        "workspace_identity_replication": cis["decoded_separation"][0] > 0.75,
        "no_broadcast_identity_hidden": max(abs(cis["no_broadcast_decoded_separation"][0]), abs(cis["no_broadcast_decoded_separation"][1])) < 0.20,
        "provenance_general_access": cis["mediated_provenance_accuracy"][0] > 0.85,
        "provenance_beats_no_broadcast": cis["mediated_provenance_accuracy"][0] > cis["no_broadcast_provenance_accuracy"][1] + 0.20,
        "provenance_beats_shuffled": cis["mediated_provenance_accuracy"][0] > cis["shuffled_provenance_accuracy"][1] + 0.20,
        "model_arbitration_general_access": cis["mediated_model_error"][1] < 0.18,
        "model_arbitration_beats_no_broadcast": cis["mediated_model_error"][1] + 0.20 < cis["no_broadcast_model_error"][0],
        "model_arbitration_beats_shuffled": cis["mediated_model_error"][1] + 0.20 < cis["shuffled_model_error"][0],
        "continuation_general_access": cis["mediated_continuation_accuracy"][0] > 0.85,
        "continuation_beats_no_broadcast": cis["mediated_continuation_accuracy"][0] > cis["no_broadcast_continuation_accuracy"][1] + 0.20,
        "continuation_beats_shuffled": cis["mediated_continuation_accuracy"][0] > cis["shuffled_continuation_accuracy"][1] + 0.20,
        "snapshot_similarity_is_wrong_control": cis["snapshot_provenance_accuracy"][1] < 0.10 and cis["snapshot_continuation_accuracy"][1] < 0.10,
        "mediated_near_direct_oracle": cis["mediated_provenance_accuracy"][0] + 0.10 > cis["oracle_provenance_accuracy"][1] and cis["mediated_model_error"][1] < cis["oracle_model_error"][0] + 0.10,
        "calibration_and_readout": cis["aligned_mean_probability"][0] > 0.75 and cis["shuffled_mean_probability"][1] < 0.25 and cis["ownership_readout_r2"][0] > 0.80,
        "integrity": all(bool(row["integrity"]) for row in seed_rows),
    }
    summary = {
        "schema": "rrct.v019.general_self_access.v1",
        "seeds": list(V019_DEVELOPMENT_SEEDS),
        "means": means,
        "bootstrap_95": {k: list(v) for k, v in cis.items()},
        "gates": gates,
        "all_primary_gates_pass": bool(all(gates.values())),
        "interpretation_limit": (
            "Functional evidence about whether already-earned causal temporal-identity content "
            "is reusable by multiple downstream routing/arbitration consumers. This does not "
            "establish phenomenal consciousness, subjective experience, sentience, or moral status."
        ),
    }

    def write_csv(name: str, rows: list[dict[str, Any]]) -> None:
        with (destination / name).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    write_csv("general_self_access_seed_summaries.csv", seed_rows)
    write_csv("general_self_access_task_rows.csv", task_rows)
    (destination / "general_self_access_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    hashes = {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(destination.iterdir()) if p.is_file()
    }
    (destination / "artifact_sha256.json").write_text(
        json.dumps(hashes, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary


__all__ = [
    "V019_DEVELOPMENT_SEEDS",
    "run_general_self_access_seed",
    "aggregate_general_self_access_results",
]
