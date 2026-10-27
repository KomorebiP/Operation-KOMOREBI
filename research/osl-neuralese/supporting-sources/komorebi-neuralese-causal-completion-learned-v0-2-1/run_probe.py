#!/usr/bin/env python3
"""Run the frozen learned-checkpoint causal-completion probe without PyTorch."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import platform
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

from checkpoint_io import LoadedCheckpoint, file_sha256, load_checkpoint
from core import (
    D4_RELATIONS,
    D4_REPRESENTATIVE_WORDS,
    N_STATES,
    all_start_cases,
    apply_canonical_word_cases,
    apply_slots,
    d4_cayley_reduction,
    encode_tables,
    future_equivalence_curve,
    normalize_rows,
    positive_ray_angle,
    predict,
    projective_word_tangent,
    reachable_all_start_cases,
    run_batch,
    sample_batch,
    slots_for_word,
    tangent_observability_tower,
    target_margin,
)


ROOT = Path(__file__).resolve().parent
PREREGISTRATION = ROOT / "PREREGISTRATION.json"
UPSTREAM_RESULTS = ROOT / "upstream" / "PROJECTIVE_RESULTS.json"
RESULTS_DIR = ROOT / "results"

ARM_FILES = {
    "raw_terminal": "raw_terminal_seed{seed}.pt",
    "relation_pressure": "relation_pressure_seed{seed}.pt",
    "projective_terminal": "projective_terminal_seed{seed}.pt",
}

REFERENCE_DEPTHS = (1, 2, 3, 4, 8, 12, 32, 64, 128, 256)


def atomic_text(path: Path, text: str) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    os.replace(temporary, path)


def atomic_json(path: Path, value: Any) -> None:
    atomic_text(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


def percentile(values: np.ndarray, q: float) -> float:
    return float(np.quantile(np.asarray(values, dtype=np.float64), q))


def summary(values: np.ndarray) -> dict[str, float]:
    array = np.asarray(values, dtype=np.float64)
    return {
        "mean": float(np.mean(array)),
        "median": float(np.median(array)),
        "p05": percentile(array, 0.05),
        "p95": percentile(array, 0.95),
        "min": float(np.min(array)),
        "max": float(np.max(array)),
    }


def load_inputs(preregistration: dict[str, Any]) -> dict[str, dict[int, LoadedCheckpoint]]:
    output: dict[str, dict[int, LoadedCheckpoint]] = {}
    expected = preregistration["checkpoints"]
    for arm, template in ARM_FILES.items():
        output[arm] = {}
        for seed in preregistration["new_audit"]["checkpoint_seeds"]:
            filename = template.format(seed=seed)
            checkpoint = load_checkpoint(ROOT / "checkpoints" / filename, expected[filename])
            config = checkpoint.metadata["config"]
            if int(config.get("seed", -1)) != seed:
                raise ValueError(f"seed mismatch in {filename}")
            if arm == "projective_terminal":
                if checkpoint.metadata.get("schema") != "komorebi.neuralese.projective_checkpoint.v1":
                    raise ValueError(f"schema mismatch in {filename}")
            elif checkpoint.metadata.get("arm") not in {"linear_terminal", "linear_relation"}:
                raise ValueError(f"legacy arm mismatch in {filename}")
            output[arm][seed] = checkpoint
    return output


def replay_upstream(
    checkpoints: dict[str, dict[int, LoadedCheckpoint]],
    upstream: dict[str, Any],
    preregistration: dict[str, Any],
) -> dict[str, Any]:
    examples = int(preregistration["replay_validation"]["examples_per_depth"])
    short_depths = set(map(int, preregistration["replay_validation"]["short_depths"]))
    short_tolerance = float(preregistration["replay_validation"]["short_depth_tolerance"])
    long_tolerance = float(preregistration["replay_validation"]["long_depth_backend_tolerance"])
    records: dict[str, Any] = {}
    short_comparisons: list[float] = []
    long_comparisons: list[float] = []
    for seed in preregistration["new_audit"]["checkpoint_seeds"]:
        seed_record: dict[str, Any] = {}
        for arm in ("raw_terminal", "projective_terminal"):
            rng = np.random.default_rng(220_000 + seed * 1000)
            arm_record: dict[str, Any] = {}
            checkpoint = checkpoints[arm][seed]
            normalize = arm == "projective_terminal"
            for depth in REFERENCE_DEPTHS:
                batch = sample_batch(rng, examples, depth, family="d4")
                with np.errstate(over="ignore", invalid="ignore"):
                    hidden, logits = run_batch(
                        checkpoint.weights,
                        batch,
                        normalize_each_step=normalize,
                        dtype=np.float32,
                    )
                finite = np.isfinite(hidden).all(axis=1) & np.isfinite(logits).all(axis=1)
                prediction = np.argmax(logits, axis=1)
                observed_accuracy = float(np.mean((prediction == batch.target) & finite))
                observed_finite = float(np.mean(finite))
                if arm == "projective_terminal":
                    reference = upstream["records"][str(seed)]["projective"]["deep"]["d4"][str(depth)]
                else:
                    reference = upstream["records"][str(seed)]["raw_parent"]["deep"]["d4"][str(depth)]
                accuracy_delta = abs(observed_accuracy - float(reference["accuracy"]))
                finite_delta = abs(observed_finite - float(reference["finite_fraction"]))
                compare_this = arm == "projective_terminal" or depth < 256
                if compare_this:
                    target = short_comparisons if depth in short_depths else long_comparisons
                    target.extend((accuracy_delta, finite_delta))
                arm_record[str(depth)] = {
                    "observed_accuracy": observed_accuracy,
                    "reference_accuracy": float(reference["accuracy"]),
                    "accuracy_absolute_delta": accuracy_delta,
                    "observed_finite_fraction": observed_finite,
                    "reference_finite_fraction": float(reference["finite_fraction"]),
                    "finite_absolute_delta": finite_delta,
                    "included_in_gate": compare_this,
                }
            seed_record[arm] = arm_record
        records[str(seed)] = seed_record
    maximum_short = max(short_comparisons)
    maximum_long = max(long_comparisons)
    return {
        "records": records,
        "maximum_short_depth_absolute_discrepancy": maximum_short,
        "maximum_long_depth_absolute_discrepancy": maximum_long,
        "criterion": f"short <= {short_tolerance}; long <= {long_tolerance}",
        "passed": bool(maximum_short <= short_tolerance and maximum_long <= long_tolerance),
        "raw_depth256_excluded_reason": "float32 overflow timing is backend-sensitive",
        "revision_note": "A failed v0.2.0 smoke showed deep recurrent predictions are BLAS-sensitive; the preserved failure motivated this two-band engineering validation without changing scientific gates.",
    }


def relation_case_tangent_gains(
    hidden: np.ndarray,
    codes: np.ndarray,
    canonical_to_slot: np.ndarray,
    word: tuple[int, ...],
    repeats: int,
) -> tuple[np.ndarray, np.ndarray]:
    episode_count = canonical_to_slot.shape[0]
    multiplicity = hidden.shape[0] // episode_count
    episode_slots = slots_for_word(canonical_to_slot, word * repeats)
    case_slots = np.repeat(episode_slots, multiplicity, axis=0)
    top = np.empty(hidden.shape[0], dtype=np.float64)
    bottom = np.empty(hidden.shape[0], dtype=np.float64)
    for case in range(hidden.shape[0]):
        matrices = [codes[case, slot] for slot in case_slots[case]]
        _, singular, _ = projective_word_tangent(hidden[case], matrices)
        top[case] = singular[0]
        bottom[case] = singular[-1]
    return top, bottom


def relation_audit(
    checkpoint: LoadedCheckpoint,
    batch: Any,
    repeats_list: list[int],
    suffix_horizon: int,
    prefix_depth: int,
    prefix_seed: int,
) -> tuple[dict[str, Any], dict[str, dict[int, dict[str, np.ndarray]]]]:
    weights = checkpoint.weights
    episode_codes = encode_tables(weights, batch.tables, np.float64)
    prefix_rng = np.random.default_rng(prefix_seed)
    prefix_slots = prefix_rng.integers(
        0, 2, size=(batch.tables.shape[0], prefix_depth), dtype=np.int64
    )
    initial, codes, semantic = reachable_all_start_cases(
        weights, batch, episode_codes, prefix_slots
    )
    output: dict[str, Any] = {}
    raw_arrays: dict[str, dict[int, dict[str, np.ndarray]]] = {}
    for relation_name, word in D4_RELATIONS.items():
        relation_record: dict[str, Any] = {}
        raw_arrays[relation_name] = {}
        control_word = word[:-1] + (1 - word[-1],)
        control_state = apply_canonical_word_cases(
            initial, codes, batch.canonical_to_slot, control_word, repeats=1
        )
        control_prediction = predict(weights, control_state)
        control_separation = control_prediction != predict(weights, initial)
        for repeats in repeats_list:
            returned = apply_canonical_word_cases(
                initial, codes, batch.canonical_to_slot, word, repeats=repeats
            )
            prediction = predict(weights, returned)
            accuracy = prediction == semantic
            angles = positive_ray_angle(initial, returned)
            margins = target_margin(weights, returned, semantic)
            curve = future_equivalence_curve(
                weights, initial, returned, codes, horizon=suffix_horizon
            )
            first_reveal = np.asarray(curve.pop("first_reveal_depth"), dtype=np.int64)
            top_gain, bottom_gain = relation_case_tangent_gains(
                initial, codes, batch.canonical_to_slot, word, repeats
            )
            episode_shape = (batch.tables.shape[0], N_STATES)
            by_start = []
            for start in range(N_STATES):
                selection = np.arange(start, initial.shape[0], N_STATES)
                by_start.append(
                    {
                        "start": start,
                        "accuracy": float(np.mean(accuracy[selection])),
                        "median_positive_ray_angle": float(np.median(angles[selection])),
                        "equivalent_through_horizon_fraction": float(
                            np.mean(first_reveal[selection] > suffix_horizon)
                        ),
                        "median_top_tangent_gain": float(np.median(top_gain[selection])),
                    }
                )
            relation_record[str(repeats)] = {
                "accuracy": float(np.mean(accuracy)),
                "positive_ray_angle": summary(angles),
                "target_margin": summary(margins),
                "top_tangent_gain": summary(top_gain),
                "bottom_tangent_gain": summary(bottom_gain),
                "contracting_top_gain_fraction": float(np.mean(top_gain < 1.0)),
                "behavioral_refinement": curve,
                "by_start": by_start,
                "matched_nonidentity_current_separation": float(np.mean(control_separation)),
            }
            raw_arrays[relation_name][repeats] = {
                "angle": angles.reshape(episode_shape),
                "survival": (first_reveal > suffix_horizon).reshape(episode_shape),
                "top_gain": top_gain.reshape(episode_shape),
            }
        output[relation_name] = relation_record
    return output, raw_arrays


def apply_group_representatives(
    weights: Any,
    initial: np.ndarray,
    codes: np.ndarray,
    canonical_to_slot: np.ndarray,
) -> list[np.ndarray]:
    return [
        apply_canonical_word_cases(initial, codes, canonical_to_slot, word, repeats=1)
        for word in D4_REPRESENTATIVE_WORDS
    ]


def cayley_and_faithfulness_audit(
    checkpoint: LoadedCheckpoint,
    batch: Any,
    suffix_horizon: int,
    prefix_depth: int,
    prefix_seed: int,
) -> dict[str, Any]:
    weights = checkpoint.weights
    episode_codes = encode_tables(weights, batch.tables, np.float64)
    prefix_rng = np.random.default_rng(prefix_seed)
    prefix_slots = prefix_rng.integers(
        0, 2, size=(batch.tables.shape[0], prefix_depth), dtype=np.int64
    )
    initial, codes, starts = reachable_all_start_cases(
        weights, batch, episode_codes, prefix_slots
    )
    representatives = apply_group_representatives(
        weights, initial, codes, batch.canonical_to_slot
    )
    representative_predictions = [predict(weights, state) for state in representatives]
    element_accuracy: list[float] = []
    for element, word in enumerate(D4_REPRESENTATIVE_WORDS):
        slots = slots_for_word(batch.canonical_to_slot, word)
        exact = starts.copy()
        maps = np.repeat(batch.maps, N_STATES, axis=0)
        rows = np.arange(exact.shape[0])
        case_slots = np.repeat(slots, N_STATES, axis=0)
        for step in range(case_slots.shape[1]):
            selected = maps[rows, case_slots[:, step]]
            exact = selected[rows, exact]
        element_accuracy.append(float(np.mean(representative_predictions[element] == exact)))

    pair_records: dict[str, Any] = {}
    episode_count = batch.tables.shape[0]
    pair_separation = []
    for left in range(8):
        for right in range(left + 1, 8):
            disagreement = (
                representative_predictions[left] != representative_predictions[right]
            ).reshape(episode_count, N_STATES)
            witness = np.any(disagreement, axis=1)
            pair_records[f"{left}-{right}"] = {
                "episode_separation_fraction": float(np.mean(witness)),
                "all_start_disagreement_fraction": float(np.mean(disagreement)),
            }
            pair_separation.append(float(np.mean(witness)))

    reduction = d4_cayley_reduction()
    cayley_rows: dict[str, Any] = {}
    current_agreements: list[float] = []
    survival_values: list[float] = []
    angle_medians: list[float] = []
    for left in range(8):
        for right in range(8):
            concatenated = apply_canonical_word_cases(
                initial,
                codes,
                batch.canonical_to_slot,
                D4_REPRESENTATIVE_WORDS[left] + D4_REPRESENTATIVE_WORDS[right],
            )
            reduced_index = reduction[(left, right)]
            reduced = representatives[reduced_index]
            current_agreement = float(
                np.mean(predict(weights, concatenated) == predict(weights, reduced))
            )
            angles = positive_ray_angle(concatenated, reduced)
            curve = future_equivalence_curve(
                weights, concatenated, reduced, codes, horizon=suffix_horizon
            )
            curve.pop("first_reveal_depth")
            survival = float(curve["equivalent_through_horizon_fraction"][-1])
            key = f"{left},{right}->{reduced_index}"
            cayley_rows[key] = {
                "left": left,
                "right": right,
                "reduced": reduced_index,
                "current_behavioral_agreement": current_agreement,
                "median_positive_ray_angle": float(np.median(angles)),
                "max_positive_ray_angle": float(np.max(angles)),
                "equivalent_through_horizon_fraction": survival,
            }
            current_agreements.append(current_agreement)
            survival_values.append(survival)
            angle_medians.append(float(np.median(angles)))
    return {
        "element_endpoint_accuracy": element_accuracy,
        "faithfulness": {
            "pair_records": pair_records,
            "minimum_episode_separation_fraction": min(pair_separation),
            "mean_episode_separation_fraction": float(np.mean(pair_separation)),
        },
        "cayley": {
            "entries": cayley_rows,
            "minimum_current_behavioral_agreement": min(current_agreements),
            "minimum_equivalent_through_horizon_fraction": min(survival_values),
            "worst_median_positive_ray_angle": max(angle_medians),
            "suffix_horizon": suffix_horizon,
        },
    }


def scale_gauge_audit(
    checkpoint: LoadedCheckpoint,
    batch: Any,
    scale_factors: list[float],
    suffix_horizon: int,
    seed: int,
) -> dict[str, Any]:
    weights = checkpoint.weights
    episode_codes = encode_tables(weights, batch.tables, np.float64)
    initial, codes, _ = all_start_cases(weights, episode_codes)
    rng = np.random.default_rng(seed)
    prefix = rng.integers(0, 2, size=(batch.tables.shape[0], 4), dtype=np.int64)
    prefix_cases = np.repeat(prefix, N_STATES, axis=0)
    reached = apply_slots(initial.copy(), codes, prefix_cases, normalize_each_step=True)
    output: dict[str, Any] = {}
    for scale in scale_factors:
        curve = future_equivalence_curve(
            weights, reached, float(scale) * reached, codes, horizon=suffix_horizon
        )
        curve.pop("first_reveal_depth")
        output[str(scale)] = {
            "equivalent_through_horizon_fraction": float(
                curve["equivalent_through_horizon_fraction"][-1]
            ),
            "curve": curve,
        }
    return output


def observability_audit(
    checkpoint: LoadedCheckpoint,
    batch: Any,
    episode_count: int,
    horizon: int,
    relative_tolerance: float,
    prefix_depth: int,
    prefix_seed: int,
) -> dict[str, Any]:
    weights = checkpoint.weights
    episode_codes = encode_tables(weights, batch.tables[:episode_count], np.float64)
    prefix_rng = np.random.default_rng(prefix_seed)
    prefix_slots = prefix_rng.integers(
        0, 2, size=(episode_count, prefix_depth), dtype=np.int64
    )
    reached, codes, _ = reachable_all_start_cases(
        weights,
        type(batch)(
            tables=batch.tables[:episode_count],
            maps=batch.maps[:episode_count],
            op_slots=batch.op_slots[:episode_count],
            canonical_ops=batch.canonical_ops[:episode_count],
            start=batch.start[:episode_count],
            target=batch.target[:episode_count],
            canonical_to_slot=batch.canonical_to_slot[:episode_count],
            phi=batch.phi[:episode_count],
            family=batch.family,
        ),
        episode_codes,
        prefix_slots,
    )
    records: list[list[dict[str, Any]]] = []
    for episode in range(episode_count):
        for start in range(N_STATES):
            records.append(
                tangent_observability_tower(
                    weights,
                    reached[episode * N_STATES + start],
                    codes[episode * N_STATES + start],
                    horizon=horizon,
                    relative_tolerance=relative_tolerance,
                )
            )
    by_depth: list[dict[str, Any]] = []
    for depth in range(horizon + 1):
        ranks = np.asarray([record[depth]["rank"] for record in records])
        effective = np.asarray([record[depth]["effective_rank"] for record in records])
        conditions = np.asarray(
            [record[depth]["condition_number_on_rank"] for record in records], dtype=np.float64
        )
        packet_trace = np.asarray([record[depth]["exact_depth_trace"] for record in records])
        by_depth.append(
            {
                "depth": depth,
                "rank_min": int(np.min(ranks)),
                "rank_median": float(np.median(ranks)),
                "rank_max": int(np.max(ranks)),
                "effective_rank": summary(effective),
                "condition_number_on_rank": summary(conditions),
                "exact_depth_packet_trace": summary(packet_trace),
            }
        )
    return {
        "kind": "local_centered_logit_projective_tangent_proxy",
        "case_count": len(records),
        "relative_tolerance": relative_tolerance,
        "by_depth": by_depth,
        "warning": "This local logit Gramian is not an exact nonlinear behavioral quotient.",
    }


def _softmax_rows(logits: np.ndarray) -> np.ndarray:
    shifted = logits - np.max(logits, axis=-1, keepdims=True)
    exponential = np.exp(shifted)
    return exponential / np.sum(exponential, axis=-1, keepdims=True)


def behavioral_fiber_audit(
    checkpoint: LoadedCheckpoint,
    batch: Any,
    episode_count: int,
    prefix_depth: int,
    continuation_depth: int,
    pair_samples_per_episode: int,
    seed: int,
) -> dict[str, Any]:
    """Build finite behavioral fibers from every registered prefix history."""

    weights = checkpoint.weights
    episode_count = min(episode_count, batch.tables.shape[0])
    episode_codes = encode_tables(weights, batch.tables[:episode_count], np.float64)
    prefix_words = list(itertools.product(range(2), repeat=prefix_depth))
    continuation_words = [
        word
        for depth in range(continuation_depth + 1)
        for word in itertools.product(range(2), repeat=depth)
    ]
    rng = np.random.default_rng(seed)
    exact_predictions: list[float] = []
    unique_patterns: list[float] = []
    continuous_rms: list[float] = []
    continuous_max: list[float] = []
    hidden_angles: list[float] = []
    centroid_decode: list[float] = []
    centroid_closure: list[float] = []
    centroid_separation: list[float] = []
    centroid_relation: dict[str, list[float]] = {name: [] for name in D4_RELATIONS}
    anchor_angles: list[float] = []
    anchor_decode: list[float] = []
    anchor_relation: dict[str, list[float]] = {name: [] for name in D4_RELATIONS}
    pair_dynamics: dict[int, dict[str, list[float]]] = {
        depth: {"initial": [], "final": [], "ratio": []} for depth in (1, 2, 4, 8)
    }

    for episode in range(episode_count):
        operators = episode_codes[episode]
        maps = batch.maps[episode]
        states_by_label: dict[int, list[np.ndarray]] = {state: [] for state in range(8)}
        for start in range(8):
            for word in prefix_words:
                hidden = normalize_rows(weights.state_embedding[start][None, :].astype(np.float64))[0]
                semantic = start
                for operator in word:
                    hidden = normalize_rows((operators[operator] @ hidden)[None, :])[0]
                    semantic = int(maps[operator, semantic])
                states_by_label[semantic].append(hidden)

        centroids: dict[int, np.ndarray] = {}
        for semantic, state_list in states_by_label.items():
            states = np.stack(state_list)
            centroid = normalize_rows(np.mean(states, axis=0, keepdims=True))[0]
            centroids[semantic] = centroid
            patterns: list[tuple[int, ...]] = []
            signatures: list[np.ndarray] = []
            for state in states:
                predictions: list[int] = []
                expected: list[int] = []
                probabilities: list[np.ndarray] = []
                for word in continuation_words:
                    current = state.copy()
                    target = semantic
                    for operator in word:
                        current = normalize_rows((operators[operator] @ current)[None, :])[0]
                        target = int(maps[operator, target])
                    logits = weights.decoder.astype(np.float64) @ current
                    predictions.append(int(np.argmax(logits)))
                    expected.append(target)
                    probabilities.append(_softmax_rows(logits[None, :])[0])
                exact_predictions.extend(
                    float(prediction == target)
                    for prediction, target in zip(predictions, expected)
                )
                patterns.append(tuple(predictions))
                signatures.append(np.concatenate(probabilities))
            unique_patterns.append(float(len(set(patterns))))
            signature_array = np.stack(signatures)
            signature_centroid = np.mean(signature_array, axis=0)
            distances = np.linalg.norm(signature_array - signature_centroid, axis=1)
            continuous_rms.append(float(np.sqrt(np.mean(distances**2))))
            continuous_max.append(float(np.max(distances)))
            hidden_angles.extend(positive_ray_angle(states, np.broadcast_to(centroid, states.shape)).tolist())

        centroid_matrix = np.stack([centroids[state] for state in range(8)])
        anchors = normalize_rows(weights.state_embedding.astype(np.float64))
        for left in range(8):
            for right in range(left + 1, 8):
                centroid_separation.append(
                    float(positive_ray_angle(centroid_matrix[left][None, :], centroid_matrix[right][None, :])[0])
                )
        for semantic, centroid in centroids.items():
            centroid_decode.append(float(predict(weights, centroid[None, :])[0] == semantic))
            anchor = anchors[semantic]
            anchor_angles.append(
                float(positive_ray_angle(anchor[None, :], centroid[None, :])[0])
            )
            anchor_decode.append(float(predict(weights, anchor[None, :])[0] == semantic))
            for operator in range(2):
                endpoint = normalize_rows((operators[operator] @ centroid)[None, :])[0]
                target = int(maps[operator, semantic])
                centroid_closure.append(
                    float(positive_ray_angle(endpoint[None, :], centroids[target][None, :])[0])
                )
            for relation_name, canonical_word in D4_RELATIONS.items():
                endpoint = centroid.copy()
                visible_word = batch.canonical_to_slot[episode, np.asarray(canonical_word)]
                for operator in visible_word:
                    endpoint = normalize_rows((operators[int(operator)] @ endpoint)[None, :])[0]
                centroid_relation[relation_name].append(
                    float(positive_ray_angle(endpoint[None, :], centroid[None, :])[0])
                )
                anchor_endpoint = anchor.copy()
                for operator in visible_word:
                    anchor_endpoint = normalize_rows(
                        (operators[int(operator)] @ anchor_endpoint)[None, :]
                    )[0]
                anchor_relation[relation_name].append(
                    float(
                        positive_ray_angle(
                            anchor_endpoint[None, :], anchor[None, :]
                        )[0]
                    )
                )

        for depth, values in pair_dynamics.items():
            for _ in range(pair_samples_per_episode):
                semantic = int(rng.integers(0, 8))
                candidates = states_by_label[semantic]
                left_index, right_index = rng.choice(len(candidates), size=2, replace=False)
                left = candidates[int(left_index)].copy()
                right = candidates[int(right_index)].copy()
                initial_angle = float(positive_ray_angle(left[None, :], right[None, :])[0])
                continuation = rng.integers(0, 2, size=depth)
                for operator in continuation:
                    left = normalize_rows((operators[int(operator)] @ left)[None, :])[0]
                    right = normalize_rows((operators[int(operator)] @ right)[None, :])[0]
                final_angle = float(positive_ray_angle(left[None, :], right[None, :])[0])
                values["initial"].append(initial_angle)
                values["final"].append(final_angle)
                if initial_angle > 1e-10:
                    values["ratio"].append(final_angle / initial_angle)

    return {
        "kind": "finite_behavioral_refinement_tower",
        "episode_count": episode_count,
        "prefix_depth": prefix_depth,
        "prefix_words_per_start": len(prefix_words),
        "continuation_depth": continuation_depth,
        "continuation_words": len(continuation_words),
        "continuation_decisions": len(exact_predictions),
        "discrete_continuation_accuracy": float(np.mean(exact_predictions)),
        "unique_prediction_signatures_per_semantic_state": summary(np.asarray(unique_patterns)),
        "continuous_probability_signature_rms_within_fiber": summary(np.asarray(continuous_rms)),
        "continuous_probability_signature_max_within_fiber": summary(np.asarray(continuous_max)),
        "hidden_angle_to_fiber_centroid": summary(np.asarray(hidden_angles)),
        "posthoc_centroid_codebook": {
            "status": "post_hoc_diagnostic_not_a_frozen_model_component",
            "decode_accuracy": float(np.mean(centroid_decode)),
            "one_step_closure_angle": summary(np.asarray(centroid_closure)),
            "pairwise_separation_angle": summary(np.asarray(centroid_separation)),
            "relation_cycle_angle": {
                name: summary(np.asarray(values)) for name, values in centroid_relation.items()
            },
        },
        "raw_embedding_anchor": {
            "status": "pre_recurrence_reference_not_used_for_registered_loop_gates",
            "decode_accuracy": float(np.mean(anchor_decode)),
            "angle_to_matching_fiber_centroid": summary(np.asarray(anchor_angles)),
            "relation_cycle_angle": {
                name: summary(np.asarray(values)) for name, values in anchor_relation.items()
            },
        },
        "common_continuation_pair_dynamics": {
            str(depth): {
                "initial_angle": summary(np.asarray(values["initial"])),
                "final_angle": summary(np.asarray(values["final"])),
                "final_to_initial_angle_ratio": summary(np.asarray(values["ratio"])),
                "contracting_fraction": float(np.mean(np.asarray(values["ratio"]) < 1.0)),
                "pairs": len(values["ratio"]),
            }
            for depth, values in pair_dynamics.items()
        },
        "warning": "This supports only the registered finite history and continuation set.",
    }


def radial_gauge_lift_audit(
    checkpoint: LoadedCheckpoint,
    seed: int,
    examples: int = 512,
    depth: int = 256,
) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    batch = sample_batch(rng, examples, depth, family="d4")
    raw_hidden, raw_logits = run_batch(
        checkpoint.weights, batch, normalize_each_step=False, dtype=np.float64
    )
    normalized_hidden, normalized_logits = run_batch(
        checkpoint.weights, batch, normalize_each_step=True, dtype=np.float64
    )
    raw_prediction = np.argmax(raw_logits, axis=1)
    normalized_prediction = np.argmax(normalized_logits, axis=1)
    finite = np.isfinite(raw_hidden).all(axis=1)
    angles = positive_ray_angle(raw_hidden[finite], normalized_hidden[finite])
    return {
        "depth": depth,
        "examples": examples,
        "raw_finite_fraction": float(np.mean(finite)),
        "prediction_agreement": float(np.mean(raw_prediction[finite] == normalized_prediction[finite])),
        "positive_ray_angle": summary(angles),
        "raw_log10_norm": summary(np.log10(np.linalg.norm(raw_hidden[finite], axis=1))),
        "numeric_semantics": "idealized float64 diagnostic; the upstream replay separately preserves float32 execution behavior",
    }


def cluster_bootstrap(
    projective: np.ndarray,
    raw: np.ndarray,
    seed: int,
    replicates: int,
) -> dict[str, Any]:
    projective = np.asarray(projective, dtype=np.float64)
    raw = np.asarray(raw, dtype=np.float64)
    if projective.shape != raw.shape:
        raise ValueError("paired bootstrap arrays must have equal shapes")
    rng = np.random.default_rng(seed)
    differences = np.empty(replicates, dtype=np.float64)
    for index in range(replicates):
        selection = rng.integers(0, projective.size, size=projective.size)
        differences[index] = float(np.mean(projective[selection] - raw[selection]))
    return {
        "paired_mean_difference": float(np.mean(projective - raw)),
        "percentile_95_interval": [percentile(differences, 0.025), percentile(differences, 0.975)],
        "replicates": replicates,
        "cluster_count": int(projective.size),
    }


def build_gates(result: dict[str, Any], preregistration: dict[str, Any]) -> dict[str, Any]:
    gate: dict[str, Any] = {}

    def add(name: str, observed: Any, criterion: str, passed: bool) -> None:
        gate[name] = {
            "observed": observed,
            "criterion": criterion,
            "status": "PASS" if passed else "FAIL",
        }

    add(
        "execution_checkpoint_digests",
        result["input_validation"]["all_checkpoint_digests_match"],
        "all exact",
        result["input_validation"]["all_checkpoint_digests_match"],
    )
    replay = result["upstream_replay"]
    add(
        "execution_numpy_replay",
        {
            "maximum_short_depth_absolute_discrepancy": replay[
                "maximum_short_depth_absolute_discrepancy"
            ],
            "maximum_long_depth_absolute_discrepancy": replay[
                "maximum_long_depth_absolute_discrepancy"
            ],
        },
        replay["criterion"],
        replay["passed"],
    )

    scale_floor = min(
        record["equivalent_through_horizon_fraction"]
        for arm_record in result["audits"].values()
        for seed_record in arm_record.values()
        for record in seed_record["scale_gauge"].values()
    )

    projective_records = result["audits"]["projective_terminal"]
    fiber_accuracy = min(
        seed_record["behavioral_fibers"]["discrete_continuation_accuracy"]
        for seed_record in projective_records.values()
    )
    fiber_signature_max = max(
        seed_record["behavioral_fibers"]["unique_prediction_signatures_per_semantic_state"]["max"]
        for seed_record in projective_records.values()
    )
    add(
        "Q0_finite_behavioral_quotient",
        {"minimum_continuation_accuracy": fiber_accuracy, "maximum_signatures_per_semantic_state": fiber_signature_max},
        "accuracy >= 0.99 and exactly one discrete signature per semantic state",
        fiber_accuracy >= 0.99 and fiber_signature_max == 1.0,
    )
    add("P1_positive_scale_gauge", scale_floor, "== 1.0", scale_floor == 1.0)

    repeat_key = "16"
    p2_angles = []
    p2_survival = []
    n1_p95 = []
    for seed_record in projective_records.values():
        for relation in D4_RELATIONS:
            row = seed_record["relations"][relation][repeat_key]
            p2_angles.append(row["positive_ray_angle"]["median"])
            p2_survival.append(
                row["behavioral_refinement"]["equivalent_through_horizon_fraction"][-1]
            )
            n1_p95.append(seed_record["relations"][relation]["1"]["top_tangent_gain"]["p95"])
    p2_observed = {
        "worst_median_angle": max(p2_angles),
        "minimum_H8_survival": min(p2_survival),
    }
    add(
        "P2_projective_path_flatness",
        p2_observed,
        "angle <= 0.01 and H8 survival >= 0.999",
        max(p2_angles) <= 0.01 and min(p2_survival) >= 0.999,
    )

    cayley_current = []
    cayley_survival = []
    separation = []
    for seed_record in projective_records.values():
        cayley_current.append(seed_record["cayley_and_faithfulness"]["cayley"]["minimum_current_behavioral_agreement"])
        cayley_survival.append(seed_record["cayley_and_faithfulness"]["cayley"]["minimum_equivalent_through_horizon_fraction"])
        separation.append(seed_record["cayley_and_faithfulness"]["faithfulness"]["minimum_episode_separation_fraction"])
    add(
        "A1_finite_D4_cayley",
        {"minimum_current": min(cayley_current), "minimum_H4_survival": min(cayley_survival)},
        "current >= 0.999 and H4 survival >= 0.99",
        min(cayley_current) >= 0.999 and min(cayley_survival) >= 0.99,
    )
    add(
        "A2_action_separation",
        min(separation),
        ">= 0.99",
        min(separation) >= 0.99,
    )
    add(
        "N1_normal_attraction",
        max(n1_p95),
        "all relation p95 one-loop top tangent gains < 1.0",
        max(n1_p95) < 1.0,
    )

    comparison = result["comparisons"]["projective_vs_raw_repeat16"]
    comparative_pass = (
        comparison["survival"]["paired_mean_difference"] > 0
        and comparison["angle_advantage_raw_minus_projective"]["paired_mean_difference"] > 0
    )
    add(
        "comparative_completion",
        comparison,
        "projective has higher H8 survival and lower angle",
        comparative_pass,
    )
    scientific = {name: value for name, value in gate.items() if not name.startswith("execution_")}
    return {
        "execution_passed": all(
            value["status"] == "PASS" for name, value in gate.items() if name.startswith("execution_")
        ),
        "scientific_all_passed": all(value["status"] == "PASS" for value in scientific.values()),
        "gates": gate,
    }


def render_report(result: dict[str, Any]) -> str:
    gates = result["gates"]
    lines = [
        "# Neuralese Causal Completion — learned-checkpoint result",
        "",
        "Author: Komorebi P.  ",
        "Version: 0.2.1  ",
        f"Execution: `{'PASS' if gates['execution_passed'] else 'FAIL'}`  ",
        f"All scientific gates: `{'PASS' if gates['scientific_all_passed'] else 'NOT PASSED'}`",
        "",
        "## Bottom line",
        "",
    ]
    gate_rows = gates["gates"]
    if gate_rows["P2_projective_path_flatness"]["status"] == "PASS":
        lines.append("The projective checkpoint passed the registered finite path-flatness test.")
    else:
        lines.append(
            "The projective checkpoint remains behaviorally strong but is not path-flat: identity-word histories can be distinguished by registered future continuations."
        )
    if gate_rows["N1_normal_attraction"]["status"] == "PASS":
        lines.append("Its sampled identity-loop tangent dynamics also passed the local attraction gate.")
    else:
        lines.append(
            "It did not obtain a normally attracting certificate under the registered tangent assay."
        )
    lines += [
        "",
        "This adaptive developmental run tests loop defects through exhaustive future suffixes and state-dependent projective tangent Jacobians on the saved learned checkpoints. It performs no retraining. The failed v0.2.0 smoke is preserved in `results/development_v0.2.0/`.",
        "",
        "## Registered gates",
        "",
        "| Gate | Status | Observed | Criterion |",
        "|---|---|---|---|",
    ]
    for name, row in gate_rows.items():
        observed = json.dumps(row["observed"], sort_keys=True)
        lines.append(f"| `{name}` | {row['status']} | `{observed}` | {row['criterion']} |")

    lines += [
        "",
        "## Repeat-16 identity-loop audit",
        "",
        "| Arm | Min endpoint accuracy | Mean H8 survival | Worst median angle | Worst p95 one-loop tangent gain |",
        "|---|---:|---:|---:|---:|",
    ]
    for arm, seed_records in result["audits"].items():
        accuracies = []
        survivals = []
        angles = []
        tangent = []
        for seed_record in seed_records.values():
            for relation in D4_RELATIONS:
                row16 = seed_record["relations"][relation]["16"]
                accuracies.append(row16["accuracy"])
                survivals.append(row16["behavioral_refinement"]["equivalent_through_horizon_fraction"][-1])
                angles.append(row16["positive_ray_angle"]["median"])
                tangent.append(seed_record["relations"][relation]["1"]["top_tangent_gain"]["p95"])
        lines.append(
            f"| {arm} | {min(accuracies):.4f} | {np.mean(survivals):.4f} | {max(angles):.4f} | {max(tangent):.4f} |"
        )

    comparison = result["comparisons"]["projective_vs_raw_repeat16"]
    lines += [
        "",
        "## Paired checkpoint comparison",
        "",
        f"Projective-minus-raw H8 survival: `{comparison['survival']['paired_mean_difference']:.6f}` "
        f"(cluster-bootstrap 95% interval `{comparison['survival']['percentile_95_interval']}`).",
        "",
        f"Raw-minus-projective identity-loop angle: `{comparison['angle_advantage_raw_minus_projective']['paired_mean_difference']:.6f}` "
        f"(95% interval `{comparison['angle_advantage_raw_minus_projective']['percentile_95_interval']}`).",
        "",
        "## Interpretation",
        "",
        "The positive-scale gate tests the radial gauge separately from path flatness. The Cayley gate checks all 64 D4 products, while the action-separation gate prevents a collapsed representation from receiving credit merely for satisfying identity relations. The tangent gate uses the implemented normalized map",
        "",
        "\\[",
        "DF_M(h)=\\frac{(I-uu^{\\mathsf T})M}{\\lVert Mh\\rVert},\\qquad u=\\frac{Mh}{\\lVert Mh\\rVert},",
        "\\]",
        "",
        "rather than treating the raw matrix spectrum as the spectrum of the projective dynamics.",
        "",
        "No same-space quotient spectrum or invariant-metric certificate is claimed. The local observability tower has not been promoted to a closed quotient because finite-horizon null directions would first need a generator-invariance certificate.",
        "",
        "## Claim boundary",
        "",
        "These results concern six fixed checkpoints, 64 fresh D4 coordinate randomizations per seed, all eight starting states, and suffixes through the registered finite horizons. They do not establish spontaneous or universal Neuralese, architecture-independent emergence, unbounded recurrence, or any claim about frontier language models or awareness.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true", help="use 8 episodes and shorter suffix horizons")
    args = parser.parse_args()
    started = time.perf_counter()
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    if file_sha256(UPSTREAM_RESULTS) != preregistration["upstream_reference"]["sha256"]:
        raise ValueError("upstream reference digest mismatch")
    upstream = json.loads(UPSTREAM_RESULTS.read_text(encoding="utf-8"))
    checkpoints = load_inputs(preregistration)
    audit_config = dict(preregistration["new_audit"])
    if args.quick:
        audit_config["episodes_per_checkpoint"] = 8
        audit_config["behavioral_suffix_horizon"] = 4
        audit_config["full_cayley_suffix_horizon"] = 2
        audit_config["observability_episode_count"] = 2
        audit_config["observability_horizon"] = 3
        audit_config["behavioral_fiber_episode_count"] = 2
        audit_config["behavioral_fiber_pair_samples"] = 8
        audit_config["cluster_bootstrap_replicates"] = 100

    result: dict[str, Any] = {
        "schema": "komorebi.neuralese.causal_completion.result.v1",
        "version": "0.2.1",
        "author": "Komorebi P.",
        "profile": "quick" if args.quick else "registered",
        "preregistration_sha256": file_sha256(PREREGISTRATION),
        "input_validation": {
            "upstream_sha256": file_sha256(UPSTREAM_RESULTS),
            "checkpoint_sha256": {
                arm: {str(seed): checkpoint.sha256 for seed, checkpoint in by_seed.items()}
                for arm, by_seed in checkpoints.items()
            },
            "all_checkpoint_digests_match": True,
            "restricted_loader": True,
        },
        "environment": {
            "python": sys.version,
            "numpy": np.__version__,
            "platform": platform.platform(),
            "torch_required": False,
        },
    }
    result["upstream_replay"] = replay_upstream(checkpoints, upstream, preregistration)
    audits: dict[str, Any] = {}
    raw_arrays: dict[str, dict[int, Any]] = {}
    for arm, by_seed in checkpoints.items():
        audits[arm] = {}
        raw_arrays[arm] = {}
        for seed, checkpoint in by_seed.items():
            rng = np.random.default_rng(910_000 + 1000 * seed)
            batch = sample_batch(
                rng, int(audit_config["episodes_per_checkpoint"]), 0, family="d4"
            )
            relations, arrays = relation_audit(
                checkpoint,
                batch,
                list(map(int, audit_config["relation_repeats"])),
                int(audit_config["behavioral_suffix_horizon"]),
                int(audit_config["registered_prefix_depth"]),
                920_000 + seed,
            )
            raw_arrays[arm][seed] = arrays
            audits[arm][str(seed)] = {
                "checkpoint_sha256": checkpoint.sha256,
                "relations": relations,
                "cayley_and_faithfulness": cayley_and_faithfulness_audit(
                    checkpoint,
                    batch,
                    int(audit_config["full_cayley_suffix_horizon"]),
                    int(audit_config["registered_prefix_depth"]),
                    920_000 + seed,
                ),
                "scale_gauge": scale_gauge_audit(
                    checkpoint,
                    batch,
                    list(map(float, audit_config["scale_factors"])),
                    int(audit_config["scale_suffix_horizon"]),
                    seed=930_000 + seed,
                ),
                "tangent_observability": observability_audit(
                    checkpoint,
                    batch,
                    int(audit_config["observability_episode_count"]),
                    int(audit_config["observability_horizon"]),
                    float(audit_config["observability_relative_tolerance"]),
                    int(audit_config["registered_prefix_depth"]),
                    920_000 + seed,
                ),
                "behavioral_fibers": behavioral_fiber_audit(
                    checkpoint,
                    batch,
                    int(audit_config["behavioral_fiber_episode_count"]),
                    int(audit_config["behavioral_fiber_prefix_depth"]),
                    int(audit_config["behavioral_fiber_continuation_depth"]),
                    int(audit_config["behavioral_fiber_pair_samples"]),
                    seed=950_000 + seed,
                ),
            }
            if arm in {"raw_terminal", "relation_pressure"}:
                audits[arm][str(seed)]["raw_vs_gauge_fixed_lift"] = radial_gauge_lift_audit(
                    checkpoint, seed=940_000 + seed
                )
    result["audits"] = audits

    projective_survival: list[float] = []
    raw_survival: list[float] = []
    projective_angle: list[float] = []
    raw_angle: list[float] = []
    for seed in audit_config["checkpoint_seeds"]:
        p_seed_survival = []
        r_seed_survival = []
        p_seed_angle = []
        r_seed_angle = []
        for relation in D4_RELATIONS:
            p = raw_arrays["projective_terminal"][seed][relation][16]
            r = raw_arrays["raw_terminal"][seed][relation][16]
            p_seed_survival.append(np.mean(p["survival"], axis=1))
            r_seed_survival.append(np.mean(r["survival"], axis=1))
            p_seed_angle.append(np.median(p["angle"], axis=1))
            r_seed_angle.append(np.median(r["angle"], axis=1))
        projective_survival.extend(np.mean(np.stack(p_seed_survival), axis=0).tolist())
        raw_survival.extend(np.mean(np.stack(r_seed_survival), axis=0).tolist())
        projective_angle.extend(np.mean(np.stack(p_seed_angle), axis=0).tolist())
        raw_angle.extend(np.mean(np.stack(r_seed_angle), axis=0).tolist())
    bootstrap_seed = int(audit_config["cluster_bootstrap_seed"])
    bootstrap_replicates = int(audit_config["cluster_bootstrap_replicates"])
    result["comparisons"] = {
        "projective_vs_raw_repeat16": {
            "survival": cluster_bootstrap(
                np.asarray(projective_survival),
                np.asarray(raw_survival),
                bootstrap_seed,
                bootstrap_replicates,
            ),
            "angle_advantage_raw_minus_projective": cluster_bootstrap(
                np.asarray(raw_angle),
                np.asarray(projective_angle),
                bootstrap_seed + 1,
                bootstrap_replicates,
            ),
        }
    }
    result["gates"] = build_gates(result, preregistration)
    result["elapsed_seconds"] = time.perf_counter() - started
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    result_path = RESULTS_DIR / ("QUICK_RESULTS.json" if args.quick else "RESULTS.json")
    report_path = RESULTS_DIR / ("QUICK_REPORT.md" if args.quick else "REPORT.md")
    atomic_json(result_path, result)
    atomic_text(report_path, render_report(result))
    completion = {
        "schema": "komorebi.neuralese.causal_completion.completion.v1",
        "profile": result["profile"],
        "execution_passed": result["gates"]["execution_passed"],
        "scientific_all_passed": result["gates"]["scientific_all_passed"],
        "results_file": result_path.name,
        "results_sha256": file_sha256(result_path),
        "report_file": report_path.name,
        "report_sha256": file_sha256(report_path),
        "elapsed_seconds": result["elapsed_seconds"],
    }
    completion_path = RESULTS_DIR / (
        "QUICK_RUN_COMPLETE.json" if args.quick else "RUN_COMPLETE.json"
    )
    atomic_json(completion_path, completion)
    print(json.dumps(completion, sort_keys=True))
    return 0 if completion["execution_passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
