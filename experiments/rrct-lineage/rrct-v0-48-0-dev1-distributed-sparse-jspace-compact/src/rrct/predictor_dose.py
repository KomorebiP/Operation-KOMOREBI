"""Spectrum-preserving predictor-dose validation for RRCT v0.4.

The dose transform rotates paired predictor output coordinates with one shared
orthogonal matrix.  It is a mechanistic organization control, not a claim
about consciousness or universal mediation.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from ._version import __version__
from .experiments import (
    DEFAULT_PREDICTOR_DOSES,
    INTERVENTION_MAGNITUDE,
    V04_BOOTSTRAP_RESAMPLES,
    V04_BOOTSTRAP_SEED,
    V04_VALIDATION_SEEDS,
    _audit_closure_row,
    _episodes,
    _predictor_snapshot_id,
    _prepare_empty_output,
    _train_predictor_snapshot,
    _validate_experiment_counts,
    _validate_sweep_values,
    evaluate_variant,
)


INVARIANT_ATOL = 1e-12
INVARIANT_RTOL = 1e-12
OUTPUT_DIMENSION = 16
_PAIRING_STREAM = 0x50303444


@dataclass(frozen=True)
class PredictorDoseTransform:
    """One auditable shared-output rotation of a predictor snapshot."""

    snapshot: dict[str, Any]
    dose: float
    pairs: tuple[tuple[int, int], ...]
    orthogonal_matrix: np.ndarray
    orthogonal_matrix_sha256: str
    invariants: dict[str, Any]


def _copy_snapshot(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    return {
        str(key): value.copy() if isinstance(value, np.ndarray) else value
        for key, value in snapshot.items()
    }


def _array_sha256(values: np.ndarray) -> str:
    array = np.ascontiguousarray(np.asarray(values, dtype=np.float64))
    digest = hashlib.sha256()
    digest.update(array.dtype.str.encode("ascii"))
    digest.update(np.asarray(array.shape, dtype=np.int64).tobytes())
    digest.update(array.tobytes())
    return digest.hexdigest()


def _seed_fixed_pairs(seed: int, output_dimension: int) -> tuple[tuple[int, int], ...]:
    if int(seed) != seed:
        raise ValueError("seed must be an integer")
    if output_dimension != OUTPUT_DIMENSION:
        raise ValueError("the frozen dose protocol requires exactly 16 output rows")
    rng = np.random.default_rng(
        np.random.SeedSequence([int(seed), _PAIRING_STREAM, output_dimension])
    )
    permutation = rng.permutation(output_dimension)
    return tuple(
        (int(permutation[index]), int(permutation[index + 1]))
        for index in range(0, output_dimension, 2)
    )


def _givens_matrix(
    pairs: Sequence[tuple[int, int]],
    *,
    dose: float,
    output_dimension: int,
) -> np.ndarray:
    if not np.isfinite(dose) or not 0.0 <= dose <= 1.0:
        raise ValueError("dose must be finite and in the closed interval [0, 1]")
    flattened = [int(index) for pair in pairs for index in pair]
    if sorted(flattened) != list(range(output_dimension)):
        raise ValueError("pairs must cover every output coordinate exactly once")
    if dose == 0.0:
        return np.eye(output_dimension, dtype=np.float64)

    matrix = np.zeros((output_dimension, output_dimension), dtype=np.float64)
    if dose == 1.0:
        cosine = 0.0
        sine = 1.0
    else:
        angle = float(dose) * math.pi / 2.0
        cosine = math.cos(angle)
        sine = math.sin(angle)
    for first, second in pairs:
        matrix[first, first] = cosine
        matrix[first, second] = -sine
        matrix[second, first] = sine
        matrix[second, second] = cosine
    return matrix


def verify_predictor_transform(
    base_snapshot: Mapping[str, Any],
    transformed_snapshot: Mapping[str, Any],
    orthogonal_matrix: np.ndarray,
    *,
    atol: float = INVARIANT_ATOL,
    rtol: float = INVARIANT_RTOL,
) -> dict[str, Any]:
    """Return strict, fully retained invariants for a shared left transform."""

    if not np.isfinite(atol) or atol < 0.0 or not np.isfinite(rtol) or rtol < 0.0:
        raise ValueError("invariant tolerances must be finite and nonnegative")
    base_prediction = np.asarray(base_snapshot["prediction_weights"], dtype=np.float64)
    base_skip = np.asarray(base_snapshot["workspace_skip"], dtype=np.float64)
    transformed_prediction = np.asarray(
        transformed_snapshot["prediction_weights"], dtype=np.float64
    )
    transformed_skip = np.asarray(
        transformed_snapshot["workspace_skip"], dtype=np.float64
    )
    matrix = np.asarray(orthogonal_matrix, dtype=np.float64)
    if base_prediction.ndim != 2 or base_skip.ndim != 2:
        raise ValueError("predictor matrices must be two-dimensional")
    if base_prediction.shape[0] != base_skip.shape[0]:
        raise ValueError("predictor matrices must share output rows")
    expected_shape = (base_prediction.shape[0], base_prediction.shape[0])
    if matrix.shape != expected_shape:
        raise ValueError("orthogonal matrix has the wrong shape")
    if transformed_prediction.shape != base_prediction.shape:
        raise ValueError("transformed prediction_weights shape changed")
    if transformed_skip.shape != base_skip.shape:
        raise ValueError("transformed workspace_skip shape changed")

    identity = np.eye(matrix.shape[0], dtype=np.float64)
    left_gram = matrix.T @ matrix
    right_gram = matrix @ matrix.T
    expected_prediction = matrix @ base_prediction
    expected_skip = matrix @ base_skip
    base_prediction_spectrum = np.linalg.svd(base_prediction, compute_uv=False)
    transformed_prediction_spectrum = np.linalg.svd(
        transformed_prediction, compute_uv=False
    )
    base_skip_spectrum = np.linalg.svd(base_skip, compute_uv=False)
    transformed_skip_spectrum = np.linalg.svd(transformed_skip, compute_uv=False)
    base_prediction_frobenius = float(np.linalg.norm(base_prediction, ord="fro"))
    transformed_prediction_frobenius = float(
        np.linalg.norm(transformed_prediction, ord="fro")
    )
    base_skip_frobenius = float(np.linalg.norm(base_skip, ord="fro"))
    transformed_skip_frobenius = float(np.linalg.norm(transformed_skip, ord="fro"))

    checks = {
        "q_left_orthogonal": bool(
            np.allclose(left_gram, identity, atol=atol, rtol=rtol)
        ),
        "q_right_orthogonal": bool(
            np.allclose(right_gram, identity, atol=atol, rtol=rtol)
        ),
        "shared_q_prediction_weights": bool(
            np.allclose(
                transformed_prediction, expected_prediction, atol=atol, rtol=rtol
            )
        ),
        "shared_q_workspace_skip": bool(
            np.allclose(transformed_skip, expected_skip, atol=atol, rtol=rtol)
        ),
        "prediction_singular_spectrum_preserved": bool(
            np.allclose(
                transformed_prediction_spectrum,
                base_prediction_spectrum,
                atol=atol,
                rtol=rtol,
            )
        ),
        "workspace_skip_singular_spectrum_preserved": bool(
            np.allclose(
                transformed_skip_spectrum,
                base_skip_spectrum,
                atol=atol,
                rtol=rtol,
            )
        ),
        "prediction_frobenius_norm_preserved": bool(
            np.isclose(
                transformed_prediction_frobenius,
                base_prediction_frobenius,
                atol=atol,
                rtol=rtol,
            )
        ),
        "workspace_skip_frobenius_norm_preserved": bool(
            np.isclose(
                transformed_skip_frobenius,
                base_skip_frobenius,
                atol=atol,
                rtol=rtol,
            )
        ),
    }
    return {
        "atol": float(atol),
        "rtol": float(rtol),
        "checks": checks,
        "all_passed": bool(all(checks.values())),
        "q_max_abs_left_orthogonality_error": float(
            np.max(np.abs(left_gram - identity))
        ),
        "q_max_abs_right_orthogonality_error": float(
            np.max(np.abs(right_gram - identity))
        ),
        "prediction_shared_q_max_abs_error": float(
            np.max(np.abs(transformed_prediction - expected_prediction))
        ),
        "workspace_skip_shared_q_max_abs_error": float(
            np.max(np.abs(transformed_skip - expected_skip))
        ),
        "prediction_singular_spectrum_base": base_prediction_spectrum.tolist(),
        "prediction_singular_spectrum_transformed": (
            transformed_prediction_spectrum.tolist()
        ),
        "workspace_skip_singular_spectrum_base": base_skip_spectrum.tolist(),
        "workspace_skip_singular_spectrum_transformed": (
            transformed_skip_spectrum.tolist()
        ),
        "prediction_frobenius_norm_base": base_prediction_frobenius,
        "prediction_frobenius_norm_transformed": transformed_prediction_frobenius,
        "workspace_skip_frobenius_norm_base": base_skip_frobenius,
        "workspace_skip_frobenius_norm_transformed": transformed_skip_frobenius,
    }


def transform_predictor_snapshot(
    snapshot: Mapping[str, Any],
    *,
    dose: float,
    seed: int,
) -> PredictorDoseTransform:
    """Apply the frozen seed-paired Givens dose to both predictor output maps."""

    copied = _copy_snapshot(snapshot)
    prediction = np.asarray(copied["prediction_weights"], dtype=np.float64)
    workspace_skip = np.asarray(copied["workspace_skip"], dtype=np.float64)
    if prediction.ndim != 2 or workspace_skip.ndim != 2:
        raise ValueError("predictor snapshot matrices must be two-dimensional")
    if prediction.shape[0] != workspace_skip.shape[0]:
        raise ValueError("predictor snapshot matrices must share output rows")
    if prediction.shape[0] != OUTPUT_DIMENSION:
        raise ValueError("the frozen dose protocol requires 16 predictor outputs")
    if not np.all(np.isfinite(prediction)) or not np.all(np.isfinite(workspace_skip)):
        raise ValueError("predictor snapshot matrices must be finite")

    pairs = _seed_fixed_pairs(seed, prediction.shape[0])
    matrix = _givens_matrix(
        pairs,
        dose=float(dose),
        output_dimension=prediction.shape[0],
    )
    if float(dose) == 0.0:
        copied["prediction_weights"] = prediction.copy()
        copied["workspace_skip"] = workspace_skip.copy()
    elif float(dose) == 1.0:
        transformed_prediction = np.zeros_like(prediction)
        transformed_skip = np.zeros_like(workspace_skip)
        for first, second in pairs:
            transformed_prediction[first] = -prediction[second]
            transformed_prediction[second] = prediction[first]
            transformed_skip[first] = -workspace_skip[second]
            transformed_skip[second] = workspace_skip[first]
        copied["prediction_weights"] = transformed_prediction
        copied["workspace_skip"] = transformed_skip
    else:
        copied["prediction_weights"] = matrix @ prediction
        copied["workspace_skip"] = matrix @ workspace_skip
    invariants = verify_predictor_transform(snapshot, copied, matrix)
    invariants["endpoint_identity_exact"] = (
        bool(
            np.array_equal(matrix, np.eye(OUTPUT_DIMENSION))
            and np.array_equal(copied["prediction_weights"], prediction)
            and np.array_equal(copied["workspace_skip"], workspace_skip)
        )
        if float(dose) == 0.0
        else None
    )
    invariants["endpoint_signed_pair_permutation_exact"] = (
        bool(
            set(np.unique(matrix)).issubset({-1.0, 0.0, 1.0})
            and np.count_nonzero(matrix) == OUTPUT_DIMENSION
            and invariants["checks"]["shared_q_prediction_weights"]
            and invariants["checks"]["shared_q_workspace_skip"]
        )
        if float(dose) == 1.0
        else None
    )
    invariants["all_passed"] = bool(
        invariants["all_passed"]
        and invariants["endpoint_identity_exact"] is not False
        and invariants["endpoint_signed_pair_permutation_exact"] is not False
    )
    copied["prediction_weights"].setflags(write=False)
    copied["workspace_skip"].setflags(write=False)
    matrix.setflags(write=False)
    return PredictorDoseTransform(
        snapshot=copied,
        dose=float(dose),
        pairs=pairs,
        orthogonal_matrix=matrix,
        orthogonal_matrix_sha256=_array_sha256(matrix),
        invariants=invariants,
    )


PREDICTOR_DOSE_ROW_FIELDS = (
    "status",
    "row_status",
    "stop_reason",
    "seed",
    "dose",
    "recurrent_gain",
    "closure_gain",
    "self_feedback_gain",
    "action_feedback_gain",
    "train_episode_count",
    "test_episode_count",
    "train_delay",
    "test_delay",
    "intervention_horizon",
    "adjacency_threshold",
    "closure_normalization",
    "base_snapshot_id",
    "transformed_snapshot_id",
    "input_predictor_snapshot_id",
    "scoring_predictor_snapshot_id",
    "predictor_learning_steps",
    "output_coordinate_order",
    "givens_pairs",
    "givens_block_convention",
    "orthogonal_matrix",
    "orthogonal_matrix_sha256",
    "invariants",
    "self_model_mode_during_scoring",
    "self_learning_updates",
    "self_learning_updates_before_test",
    "self_learning_updates_after_test",
    "self_learning_updates_during_test",
    "heldout_prediction_rmse",
    "self_to_workspace_effect",
    "closure_strength",
    "closure_raw_strength",
    "temporal_persistence",
    "strongly_connected",
    "profile",
    "signature",
    "task_accuracy",
    "factor_accuracy",
    "mean_task_accuracy",
    "projector_residual",
    "resolution_histogram",
    "intervention_magnitude",
    "causal_adjacency",
    "causal_effects",
    "closure_capacity_matrix",
    "closure_bottleneck_pair",
    "closure_cut_certificate",
    "cut_audit",
)


def _json_safe(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_json_safe(item) for item in value]
    return value


def _blank_scoring_payload() -> dict[str, Any]:
    return {
        "input_predictor_snapshot_id": None,
        "scoring_predictor_snapshot_id": None,
        "self_model_mode_during_scoring": None,
        "self_learning_updates": None,
        "self_learning_updates_before_test": None,
        "self_learning_updates_after_test": None,
        "self_learning_updates_during_test": None,
        "heldout_prediction_rmse": None,
        "self_to_workspace_effect": None,
        "closure_strength": None,
        "closure_raw_strength": None,
        "temporal_persistence": None,
        "strongly_connected": None,
        "profile": None,
        "signature": None,
        "task_accuracy": None,
        "factor_accuracy": None,
        "mean_task_accuracy": None,
        "projector_residual": None,
        "resolution_histogram": None,
        "intervention_magnitude": None,
        "causal_adjacency": None,
        "causal_effects": None,
        "closure_capacity_matrix": None,
        "closure_bottleneck_pair": None,
        "closure_cut_certificate": None,
        "cut_audit": None,
    }


def _base_row(
    *,
    seed: int,
    dose: float,
    train_episode_count: int,
    test_episode_count: int,
    train_delay: int,
    test_delay: int,
    intervention_horizon: int,
    recurrent_gain: float,
    closure_gain: float,
    self_feedback_gain: float,
    action_feedback_gain: float,
    base_snapshot: Mapping[str, Any],
    transformed: PredictorDoseTransform,
) -> dict[str, Any]:
    row = {
        "status": "pending",
        "row_status": "pending",
        "stop_reason": [],
        "seed": int(seed),
        "dose": float(dose),
        "recurrent_gain": float(recurrent_gain),
        "closure_gain": float(closure_gain),
        "self_feedback_gain": float(self_feedback_gain),
        "action_feedback_gain": float(action_feedback_gain),
        "train_episode_count": int(train_episode_count),
        "test_episode_count": int(test_episode_count),
        "train_delay": int(train_delay),
        "test_delay": int(test_delay),
        "intervention_horizon": int(intervention_horizon),
        "adjacency_threshold": 7.5e-4,
        "closure_normalization": INTERVENTION_MAGNITUDE,
        "base_snapshot_id": _predictor_snapshot_id(base_snapshot),
        "transformed_snapshot_id": _predictor_snapshot_id(transformed.snapshot),
        "predictor_learning_steps": int(base_snapshot.get("learning_steps", 0)),
        "output_coordinate_order": list(range(OUTPUT_DIMENSION)),
        "givens_pairs": [list(pair) for pair in transformed.pairs],
        "givens_block_convention": (
            "Q[i,i]=c,Q[i,j]=-s,Q[j,i]=s,Q[j,j]=c; "
            "pairs applied in retained order"
        ),
        "orthogonal_matrix": transformed.orthogonal_matrix.tolist(),
        "orthogonal_matrix_sha256": transformed.orthogonal_matrix_sha256,
        "invariants": _json_safe(transformed.invariants),
    }
    row.update(_blank_scoring_payload())
    return row


def _seed_setup_failure_row(
    *,
    seed: int,
    dose: float,
    train_episode_count: int,
    test_episode_count: int,
    train_delay: int,
    test_delay: int,
    intervention_horizon: int,
    recurrent_gain: float,
    closure_gain: float,
    self_feedback_gain: float,
    action_feedback_gain: float,
    reason: str,
) -> dict[str, Any]:
    pairs = _seed_fixed_pairs(seed, OUTPUT_DIMENSION)
    matrix = _givens_matrix(
        pairs,
        dose=float(dose),
        output_dimension=OUTPUT_DIMENSION,
    )
    row: dict[str, Any] = {
        "status": "stopped_seed_setup_exception",
        "row_status": "stopped_seed_setup_exception",
        "stop_reason": [reason],
        "seed": int(seed),
        "dose": float(dose),
        "recurrent_gain": float(recurrent_gain),
        "closure_gain": float(closure_gain),
        "self_feedback_gain": float(self_feedback_gain),
        "action_feedback_gain": float(action_feedback_gain),
        "train_episode_count": int(train_episode_count),
        "test_episode_count": int(test_episode_count),
        "train_delay": int(train_delay),
        "test_delay": int(test_delay),
        "intervention_horizon": int(intervention_horizon),
        "adjacency_threshold": 7.5e-4,
        "closure_normalization": INTERVENTION_MAGNITUDE,
        "base_snapshot_id": None,
        "transformed_snapshot_id": None,
        "predictor_learning_steps": None,
        "output_coordinate_order": list(range(OUTPUT_DIMENSION)),
        "givens_pairs": [list(pair) for pair in pairs],
        "givens_block_convention": (
            "Q[i,i]=c,Q[i,j]=-s,Q[j,i]=s,Q[j,j]=c; "
            "pairs applied in retained order"
        ),
        "orthogonal_matrix": matrix.tolist(),
        "orthogonal_matrix_sha256": _array_sha256(matrix),
        "invariants": {
            "all_passed": None,
            "status": "not_run_after_seed_setup_exception",
            "atol": INVARIANT_ATOL,
            "rtol": INVARIANT_RTOL,
        },
    }
    row.update(_blank_scoring_payload())
    return row


def _score_row(
    row: dict[str, Any],
    result: Mapping[str, Any],
) -> list[str]:
    cut_audit = _audit_closure_row(result)
    row.update(
        {
            "input_predictor_snapshot_id": str(
                result.get("predictor_snapshot_id", "")
            ),
            "scoring_predictor_snapshot_id": str(
                result["loaded_predictor_snapshot_id"]
            ),
            "self_model_mode_during_scoring": str(
                result["self_model_mode_during_scoring"]
            ),
            "self_learning_updates": int(result["self_learning_updates"]),
            "self_learning_updates_before_test": int(
                result["self_learning_updates_before_test"]
            ),
            "self_learning_updates_after_test": int(
                result["self_learning_updates_after_test"]
            ),
            "self_learning_updates_during_test": int(
                result["self_learning_updates_during_test"]
            ),
            "heldout_prediction_rmse": float(result["heldout_prediction_rmse"]),
            "self_to_workspace_effect": float(result["self_to_workspace_effect"]),
            "closure_strength": float(result["closure_strength"]),
            "closure_raw_strength": float(result["closure_raw_strength"]),
            "temporal_persistence": float(
                result["profile"]["temporal_persistence"]
            ),
            "strongly_connected": bool(
                result["profile"]["strongly_connected"]
            ),
            "profile": _json_safe(result["profile"]),
            "signature": _json_safe(result["signature"]),
            "task_accuracy": _json_safe(result["task_accuracy"]),
            "factor_accuracy": _json_safe(result["factor_accuracy"]),
            "mean_task_accuracy": float(result["mean_task_accuracy"]),
            "projector_residual": float(result["projector_residual"]),
            "resolution_histogram": _json_safe(result["resolution_histogram"]),
            "intervention_magnitude": float(result["intervention_magnitude"]),
            "causal_adjacency": _json_safe(result["causal_adjacency"]),
            "causal_effects": _json_safe(result["causal_effects"]),
            "closure_capacity_matrix": _json_safe(
                result["closure_capacity_matrix"]
            ),
            "closure_bottleneck_pair": _json_safe(
                result["closure_bottleneck_pair"]
            ),
            "closure_cut_certificate": _json_safe(
                result["closure_cut_certificate"]
            ),
            "cut_audit": _json_safe(cut_audit),
        }
    )
    reasons: list[str] = []
    expected_updates = int(row["predictor_learning_steps"])
    if row["self_model_mode_during_scoring"] != "frozen":
        reasons.append("self_model_not_frozen_during_scoring")
    if row["self_learning_updates"] != expected_updates:
        reasons.append("predictor_update_count_changed_before_scoring")
    if row["self_learning_updates_before_test"] != expected_updates:
        reasons.append("predictor_update_count_changed_before_test")
    if row["self_learning_updates_after_test"] != expected_updates:
        reasons.append("predictor_update_count_changed_after_test")
    if row["self_learning_updates_during_test"] != 0:
        reasons.append("heldout_predictor_updates_nonzero")
    if row["scoring_predictor_snapshot_id"] != row["transformed_snapshot_id"]:
        reasons.append("scoring_predictor_snapshot_identity_mismatch")
    if row["input_predictor_snapshot_id"] != row["transformed_snapshot_id"]:
        reasons.append("input_predictor_snapshot_identity_mismatch")
    if not cut_audit["passed"]:
        reasons.append("cut_certificate_audit_failed")
    if float(result["intervention_magnitude"]) != float(row["closure_normalization"]):
        reasons.append("closure_normalization_mismatch")
    for field in (
        "recurrent_gain",
        "closure_gain",
        "self_feedback_gain",
        "action_feedback_gain",
    ):
        if float(result[field]) != float(row[field]):
            reasons.append("scoring_gain_not_one")
            break
    return reasons


def _average_ranks(values: Sequence[float]) -> np.ndarray:
    vector = np.asarray(values, dtype=np.float64).reshape(-1)
    if vector.size == 0 or not np.all(np.isfinite(vector)):
        raise ValueError("rank values must be nonempty and finite")
    order = np.argsort(vector, kind="mergesort")
    ranks = np.empty(vector.size, dtype=np.float64)
    start = 0
    while start < vector.size:
        stop = start + 1
        while stop < vector.size and vector[order[stop]] == vector[order[start]]:
            stop += 1
        ranks[order[start:stop]] = 0.5 * (start + stop - 1) + 1.0
        start = stop
    return ranks


def _spearman_average_rank(
    first: Sequence[float], second: Sequence[float]
) -> float:
    first_ranks = _average_ranks(first)
    second_ranks = _average_ranks(second)
    if first_ranks.shape != second_ranks.shape or first_ranks.size < 2:
        raise ValueError("Spearman inputs must have the same length of at least two")
    if np.std(first_ranks) == 0.0 or np.std(second_ranks) == 0.0:
        return 0.0
    return float(np.corrcoef(first_ranks, second_ranks)[0, 1])


def _bootstrap_mean(
    values: Sequence[float],
    *,
    resamples: int,
    rng: np.random.Generator,
) -> dict[str, float]:
    vector = np.asarray(values, dtype=np.float64).reshape(-1)
    if vector.size == 0 or not np.all(np.isfinite(vector)):
        raise ValueError("bootstrap values must be nonempty and finite")
    indices = rng.integers(0, vector.size, size=(int(resamples), vector.size))
    means = np.mean(vector[indices], axis=1)
    lower, upper = np.quantile(means, (0.025, 0.975))
    return {
        "mean": float(np.mean(vector)),
        "population_std": float(np.std(vector, ddof=0)),
        "min": float(np.min(vector)),
        "max": float(np.max(vector)),
        "bootstrap_ci95_lower": float(lower),
        "bootstrap_ci95_upper": float(upper),
    }


def _positive_association_gate(
    values: Sequence[float],
    *,
    seeds: Sequence[int],
    resamples: int,
    rng: np.random.Generator,
    required_sign_agreement: int = 6,
) -> dict[str, Any]:
    vector = np.asarray(values, dtype=np.float64)
    summary: dict[str, Any] = _bootstrap_mean(
        vector, resamples=resamples, rng=rng
    )
    positive_count = int(np.sum(vector > 0.0))
    summary.update(
        {
            "direction_allowed_for_support": "positive_only",
            "strict_positive_count": positive_count,
            "required_strict_positive_count": int(required_sign_agreement),
            "seed_count": int(vector.size),
            "supported": bool(
                positive_count >= required_sign_agreement
                and summary["bootstrap_ci95_lower"] > 0.0
            ),
            "per_seed_values": [
                {"seed": int(seed), "spearman_rho": float(value)}
                for seed, value in zip(seeds, vector)
            ],
        }
    )
    return summary


def _two_sided_association_gate(
    values: Sequence[float],
    *,
    seeds: Sequence[int],
    resamples: int,
    rng: np.random.Generator,
    required_sign_agreement: int = 6,
) -> dict[str, Any]:
    vector = np.asarray(values, dtype=np.float64)
    summary: dict[str, Any] = _bootstrap_mean(
        vector, resamples=resamples, rng=rng
    )
    mean = float(summary["mean"])
    if mean > 0.0:
        direction = "positive"
        agreement = int(np.sum(vector > 0.0))
        excludes_zero = summary["bootstrap_ci95_lower"] > 0.0
    elif mean < 0.0:
        direction = "negative"
        agreement = int(np.sum(vector < 0.0))
        excludes_zero = summary["bootstrap_ci95_upper"] < 0.0
    else:
        direction = "zero"
        agreement = int(np.sum(vector == 0.0))
        excludes_zero = False
    summary.update(
        {
            "aggregate_direction": direction,
            "strict_same_direction_count": agreement,
            "required_strict_same_direction_count": int(required_sign_agreement),
            "seed_count": int(vector.size),
            "ci_excludes_zero_in_aggregate_direction": bool(excludes_zero),
            "supported": bool(
                direction != "zero"
                and agreement >= required_sign_agreement
                and excludes_zero
            ),
            "per_seed_values": [
                {"seed": int(seed), "spearman_rho": float(value)}
                for seed, value in zip(seeds, vector)
            ],
        }
    )
    return summary


def _dose_statistics(
    rows: Sequence[Mapping[str, Any]],
    *,
    seeds: Sequence[int],
    doses: Sequence[float],
    bootstrap_resamples: int,
    bootstrap_seed: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    lookup = {
        (int(row["seed"]), float(row["dose"])): row
        for row in rows
    }
    per_seed: list[dict[str, Any]] = []
    for seed in seeds:
        group = [lookup[(int(seed), float(dose))] for dose in doses]
        per_seed.append(
            {
                "seed": int(seed),
                "dose_vs_heldout_prediction_rmse": _spearman_average_rank(
                    doses,
                    [float(row["heldout_prediction_rmse"]) for row in group],
                ),
                "dose_vs_self_to_workspace_effect": _spearman_average_rank(
                    doses,
                    [float(row["self_to_workspace_effect"]) for row in group],
                ),
                "dose_vs_closure_strength": _spearman_average_rank(
                    doses,
                    [float(row["closure_strength"]) for row in group],
                ),
            }
        )
    rng = np.random.default_rng(int(bootstrap_seed))
    rmse_values = [
        float(item["dose_vs_heldout_prediction_rmse"]) for item in per_seed
    ]
    self_values = [
        float(item["dose_vs_self_to_workspace_effect"]) for item in per_seed
    ]
    closure_values = [
        float(item["dose_vs_closure_strength"]) for item in per_seed
    ]
    gates: dict[str, Any] = {
        "dose_vs_heldout_prediction_rmse": _positive_association_gate(
            rmse_values,
            seeds=seeds,
            resamples=bootstrap_resamples,
            rng=rng,
        ),
        "dose_vs_self_to_workspace_effect": _two_sided_association_gate(
            self_values,
            seeds=seeds,
            resamples=bootstrap_resamples,
            rng=rng,
        ),
        "dose_vs_closure_strength": {
            **_bootstrap_mean(
                closure_values,
                resamples=bootstrap_resamples,
                rng=rng,
            ),
            "inferential_gate": "none_descriptive_only",
            "supported": None,
            "per_seed_values": [
                {"seed": int(seed), "spearman_rho": float(value)}
                for seed, value in zip(seeds, closure_values)
            ],
        },
    }
    return per_seed, gates


def _numeric_summary_with_values(
    rows: Sequence[Mapping[str, Any]], field: str
) -> dict[str, Any]:
    vector = np.asarray([float(row[field]) for row in rows], dtype=np.float64)
    return {
        "mean": float(np.mean(vector)),
        "population_std": float(np.std(vector, ddof=0)),
        "min": float(np.min(vector)),
        "max": float(np.max(vector)),
        "individual_values": [
            {"seed": int(row["seed"]), "value": float(row[field])}
            for row in rows
        ],
    }


def _dose_aggregates(
    rows: Sequence[Mapping[str, Any]], doses: Sequence[float]
) -> list[dict[str, Any]]:
    metrics = (
        "heldout_prediction_rmse",
        "self_to_workspace_effect",
        "closure_strength",
        "temporal_persistence",
        "strongly_connected",
        "mean_task_accuracy",
    )
    aggregates: list[dict[str, Any]] = []
    for dose in doses:
        group = sorted(
            (row for row in rows if float(row["dose"]) == float(dose)),
            key=lambda row: int(row["seed"]),
        )
        aggregates.append(
            {
                "dose": float(dose),
                "seed_count": len(group),
                "seeds_included": [int(row["seed"]) for row in group],
                "metrics": {
                    field: _numeric_summary_with_values(group, field)
                    for field in metrics
                },
            }
        )
    return aggregates


def _write_predictor_dose_csv(
    path: Path, rows: Sequence[Mapping[str, Any]]
) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=PREDICTOR_DOSE_ROW_FIELDS)
        writer.writeheader()
        for source in rows:
            # Every cell is a JSON literal.  This keeps null, bool, number,
            # string, list, and mapping types unambiguous on reconstruction.
            row = {
                field: json.dumps(
                    _json_safe(source[field]),
                    separators=(",", ":"),
                    sort_keys=True,
                    allow_nan=False,
                )
                for field in PREDICTOR_DOSE_ROW_FIELDS
            }
            writer.writerow(row)


def _pyplot() -> Any:
    cache = Path(tempfile.gettempdir()) / "rrct_matplotlib_cache"
    cache.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(cache))
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as exc:  # pragma: no cover - optional dependency boundary
        raise RuntimeError(
            "predictor-dose PNG generation requires the figures dependency"
        ) from exc
    return plt


def _plot_predictor_dose(
    path: Path,
    rows: Sequence[Mapping[str, Any]],
    *,
    protocol_stopped: bool,
) -> None:
    plt = _pyplot()
    figure, axes = plt.subplots(1, 3, figsize=(14, 4.8), constrained_layout=True)
    if protocol_stopped:
        for axis in axes:
            axis.axis("off")
        axes[1].text(
            0.5,
            0.5,
            "Aggregate plot withheld\nprotocol stop retained in JSON/CSV",
            ha="center",
            va="center",
            fontsize=13,
        )
    else:
        seeds = sorted(set(int(row["seed"]) for row in rows))
        doses = sorted(set(float(row["dose"]) for row in rows))
        for axis, field, title in (
            (axes[0], "heldout_prediction_rmse", "Held-out prediction RMSE"),
            (axes[1], "self_to_workspace_effect", "Self to workspace effect"),
            (axes[2], "closure_strength", "Closure strength (descriptive)"),
        ):
            for seed in seeds:
                group = sorted(
                    (row for row in rows if int(row["seed"]) == seed),
                    key=lambda row: float(row["dose"]),
                )
                axis.plot(
                    doses,
                    [float(row[field]) for row in group],
                    color="tab:blue",
                    alpha=0.25,
                    linewidth=1,
                )
            means = [
                float(
                    np.mean(
                        [
                            row[field]
                            for row in rows
                            if float(row["dose"]) == dose
                        ]
                    )
                )
                for dose in doses
            ]
            axis.plot(doses, means, color="black", marker="o", linewidth=2.5)
            axis.set_xlabel("Orthogonal predictor dose")
            axis.set_ylabel(title)
            axis.set_title(title)
    figure.suptitle(
        "Spectrum-preserving predictor organization dose\n"
        "All prespecified seeds retained; closure is descriptive"
    )
    figure.savefig(path, dpi=180)
    plt.close(figure)


def run_predictor_dose(
    output: str | Path,
    *,
    seeds: Sequence[int] = V04_VALIDATION_SEEDS,
    doses: Sequence[float] = DEFAULT_PREDICTOR_DOSES,
    train_episode_count: int = 128,
    test_episode_count: int = 64,
    train_delay: int = 5,
    test_delay: int = 7,
    intervention_horizon: int = 12,
    recurrent_gain: float = 1.0,
    closure_gain: float = 1.0,
    self_feedback_gain: float = 1.0,
    action_feedback_gain: float = 1.0,
    bootstrap_resamples: int = V04_BOOTSTRAP_RESAMPLES,
    bootstrap_seed: int = V04_BOOTSTRAP_SEED,
) -> dict[str, Any]:
    """Run the frozen, spectrum-preserving predictor-dose protocol."""

    seed_values, dose_values = _validate_sweep_values(seeds, doses)
    dose_values = tuple(sorted(dose_values))
    if len(dose_values) < 2:
        raise ValueError("predictor dose requires at least two distinct doses")
    if any(dose < 0.0 or dose > 1.0 for dose in dose_values):
        raise ValueError("predictor doses must lie in [0, 1]")
    _validate_experiment_counts(
        train_episode_count=train_episode_count,
        test_episode_count=test_episode_count,
        intervention_horizon=intervention_horizon,
    )
    for name, value in (("train_delay", train_delay), ("test_delay", test_delay)):
        if int(value) != value or value <= 0:
            raise ValueError(f"{name} must be a positive integer")
    for name, value in (
        ("recurrent_gain", recurrent_gain),
        ("closure_gain", closure_gain),
        ("self_feedback_gain", self_feedback_gain),
        ("action_feedback_gain", action_feedback_gain),
    ):
        if not np.isfinite(value) or float(value) != 1.0:
            raise ValueError(f"{name} is frozen at exactly 1.0")
    if int(bootstrap_resamples) != bootstrap_resamples or bootstrap_resamples <= 0:
        raise ValueError("bootstrap_resamples must be a positive integer")
    destination = _prepare_empty_output(output)

    rows: list[dict[str, Any]] = []
    for seed in seed_values:
        try:
            train = _episodes(train_episode_count, seed=seed + 1, delay=train_delay)
            test = _episodes(test_episode_count, seed=seed + 2, delay=test_delay)
            base_snapshot = _train_predictor_snapshot(train, seed=seed)
            base_snapshot_id = _predictor_snapshot_id(base_snapshot)
        except Exception as exc:
            reason = f"seed_setup_exception:{type(exc).__name__}:{exc}"
            rows.extend(
                _seed_setup_failure_row(
                    seed=seed,
                    dose=dose,
                    train_episode_count=train_episode_count,
                    test_episode_count=test_episode_count,
                    train_delay=train_delay,
                    test_delay=test_delay,
                    intervention_horizon=intervention_horizon,
                    recurrent_gain=recurrent_gain,
                    closure_gain=closure_gain,
                    self_feedback_gain=self_feedback_gain,
                    action_feedback_gain=action_feedback_gain,
                    reason=reason,
                )
                for dose in dose_values
            )
            continue
        for dose in dose_values:
            try:
                transformed = transform_predictor_snapshot(
                    base_snapshot,
                    dose=dose,
                    seed=seed,
                )
            except Exception as exc:
                placeholder = PredictorDoseTransform(
                    snapshot=_copy_snapshot(base_snapshot),
                    dose=float(dose),
                    pairs=(),
                    orthogonal_matrix=np.empty((0, 0), dtype=np.float64),
                    orthogonal_matrix_sha256="",
                    invariants={"all_passed": False, "transform_exception": str(exc)},
                )
                row = _base_row(
                    seed=seed,
                    dose=dose,
                    train_episode_count=train_episode_count,
                    test_episode_count=test_episode_count,
                    train_delay=train_delay,
                    test_delay=test_delay,
                    intervention_horizon=intervention_horizon,
                    recurrent_gain=recurrent_gain,
                    closure_gain=closure_gain,
                    self_feedback_gain=self_feedback_gain,
                    action_feedback_gain=action_feedback_gain,
                    base_snapshot=base_snapshot,
                    transformed=placeholder,
                )
                row["status"] = "stopped_transform_exception"
                row["row_status"] = row["status"]
                row["stop_reason"] = [
                    f"transform_exception:{type(exc).__name__}:{exc}"
                ]
                rows.append(row)
                continue

            row = _base_row(
                seed=seed,
                dose=dose,
                train_episode_count=train_episode_count,
                test_episode_count=test_episode_count,
                train_delay=train_delay,
                test_delay=test_delay,
                intervention_horizon=intervention_horizon,
                recurrent_gain=recurrent_gain,
                closure_gain=closure_gain,
                self_feedback_gain=self_feedback_gain,
                action_feedback_gain=action_feedback_gain,
                base_snapshot=base_snapshot,
                transformed=transformed,
            )
            reasons: list[str] = []
            if not bool(transformed.invariants.get("all_passed", False)):
                reasons.append("predictor_transform_invariant_failure")
            try:
                invariant_recheck = verify_predictor_transform(
                    base_snapshot,
                    transformed.snapshot,
                    transformed.orthogonal_matrix,
                )
            except Exception as exc:
                invariant_recheck = {
                    "all_passed": False,
                    "recheck_exception": f"{type(exc).__name__}:{exc}",
                }
            row["invariants"]["runner_recheck"] = _json_safe(invariant_recheck)
            if not bool(invariant_recheck.get("all_passed", False)):
                reasons.append("runner_predictor_transform_invariant_failure")
            if _array_sha256(transformed.orthogonal_matrix) != (
                transformed.orthogonal_matrix_sha256
            ):
                reasons.append("orthogonal_matrix_sha256_mismatch")
            if _predictor_snapshot_id(base_snapshot) != base_snapshot_id:
                reasons.append("base_predictor_snapshot_identity_changed")
            if reasons:
                row["status"] = "stopped_invariant_failure"
                row["row_status"] = row["status"]
                row["stop_reason"] = reasons
                rows.append(row)
                continue

            try:
                result, _ = evaluate_variant(
                    "predictor_dose",
                    (),
                    train,
                    test,
                    seed=seed,
                    recurrent_gain=recurrent_gain,
                    closure_gain=closure_gain,
                    self_feedback_gain=self_feedback_gain,
                    action_feedback_gain=action_feedback_gain,
                    intervention_horizon=intervention_horizon,
                    self_model_condition="trained_self_model",
                    predictor_snapshot=transformed.snapshot,
                )
                reasons.extend(_score_row(row, result))
            except Exception as exc:
                reasons.append(f"scoring_exception:{type(exc).__name__}:{exc}")
            if _predictor_snapshot_id(base_snapshot) != base_snapshot_id:
                reasons.append("base_predictor_snapshot_identity_changed_after_scoring")
            if _predictor_snapshot_id(transformed.snapshot) != row[
                "transformed_snapshot_id"
            ]:
                reasons.append("transformed_snapshot_identity_changed_after_scoring")
            row["status"] = "protocol_contradiction" if reasons else "completed"
            row["row_status"] = row["status"]
            row["stop_reason"] = reasons
            rows.append(row)

    protocol_stopped = any(row["status"] != "completed" for row in rows)
    if protocol_stopped:
        per_seed_spearman: list[dict[str, Any]] = []
        association_gates: dict[str, Any] = {
            "status": "not_computed_after_protocol_stop"
        }
        per_dose_aggregates: list[dict[str, Any]] = []
    else:
        per_seed_spearman, association_gates = _dose_statistics(
            rows,
            seeds=seed_values,
            doses=dose_values,
            bootstrap_resamples=int(bootstrap_resamples),
            bootstrap_seed=int(bootstrap_seed),
        )
        per_dose_aggregates = _dose_aggregates(rows, dose_values)

    csv_name, json_name, png_name = (
        "predictor_dose.csv",
        "predictor_dose.json",
        "predictor_dose.png",
    )
    _write_predictor_dose_csv(destination / csv_name, rows)
    _plot_predictor_dose(
        destination / png_name,
        rows,
        protocol_stopped=protocol_stopped,
    )
    confirmatory_protocol = bool(
        tuple(seed_values) == tuple(V04_VALIDATION_SEEDS)
        and tuple(dose_values) == tuple(DEFAULT_PREDICTOR_DOSES)
        and int(train_episode_count) == 128
        and int(test_episode_count) == 64
        and int(train_delay) == 5
        and int(test_delay) == 7
        and int(intervention_horizon) == 12
        and int(bootstrap_resamples) == V04_BOOTSTRAP_RESAMPLES
        and int(bootstrap_seed) == V04_BOOTSTRAP_SEED
    )
    summary: dict[str, Any] = {
        "schema": "rrct.predictor_dose.v0.4",
        "experiment": "spectrum_preserving_predictor_organization_dose",
        "version": __version__,
        "status": (
            "stopped_protocol_contradiction"
            if protocol_stopped
            else "completed_without_seed_filtering"
        ),
        "protocol_scope": (
            "frozen_confirmatory_validation"
            if confirmatory_protocol
            else "nonconfirmatory_or_smoke_configuration"
        ),
        "parameters": {
            "seeds": list(seed_values),
            "doses": list(dose_values),
            "train_episode_count": int(train_episode_count),
            "test_episode_count": int(test_episode_count),
            "train_delay": int(train_delay),
            "test_delay": int(test_delay),
            "intervention_horizon": int(intervention_horizon),
            "recurrent_gain": float(recurrent_gain),
            "closure_gain": float(closure_gain),
            "self_feedback_gain": float(self_feedback_gain),
            "action_feedback_gain": float(action_feedback_gain),
        },
        "protocol": {
            "predictor_training": (
                "one label-free predictor snapshot per seed, trained once and "
                "frozen across every dose"
            ),
            "pairing": (
                "one deterministic seed-fixed permutation paired consecutively "
                "to cover all 16 predictor outputs"
            ),
            "transform": (
                "one common Q(d) left-multiplies prediction_weights and "
                "workspace_skip; eight Givens blocks use angle d*pi/2"
            ),
            "endpoint_overrides": {
                "dose_0": "exact identity and bit-identical predictor copies",
                "dose_1": "exact signed pair permutation with entries -1, 0, 1",
            },
            "invariants": (
                "Q orthogonality, both singular spectra, both Frobenius norms, "
                "and shared-Q application at atol=rtol=1e-12"
            ),
            "matched_heldout_stream": True,
            "heldout_updates_required": 0,
            "invariant_failure_policy": (
                "retain failed row, skip its scoring, and withhold every aggregate gate"
            ),
            "causal_effect_normalization": INTERVENTION_MAGNITUDE,
        },
        "association_protocol": {
            "method": "per-seed Spearman correlation using average ranks",
            "rmse_primary_gate": (
                "positive direction only; at least 6/8 strict positive seed "
                "correlations and bootstrap 95% lower bound above zero"
            ),
            "self_to_workspace_primary_gate": (
                "two-sided aggregate direction; at least 6/8 strict same-sign "
                "seed correlations and the bootstrap interval excludes zero"
            ),
            "closure_strength": "descriptive only; no support gate",
        },
        "bootstrap": {
            "method": "deterministic percentile bootstrap of seed-mean correlations",
            "confidence": 0.95,
            "rng_seed": int(bootstrap_seed),
            "resamples": int(bootstrap_resamples),
            "seed_filtering": "none",
        },
        "csv_encoding": (
            "each data cell is a JSON literal for lossless typed reconstruction"
        ),
        "runs": rows,
        "per_seed_spearman": per_seed_spearman,
        "association_gates": association_gates,
        "per_dose_aggregates": per_dose_aggregates,
        "stop_reasons": sorted(
            {
                reason
                for row in rows
                for reason in row["stop_reason"]
            }
        ),
        "artifacts": [json_name, csv_name, png_name],
        "interpretation_boundary": (
            "This arm tests dose-dependent consequences of predictor output "
            "organization in the implemented RRCT architecture. It does not "
            "establish consciousness or a universal mediation principle."
        ),
    }
    (destination / json_name).write_text(
        json.dumps(_json_safe(summary), indent=2, sort_keys=True, allow_nan=False)
        + "\n",
        encoding="utf-8",
    )
    return summary


__all__ = [
    "DEFAULT_PREDICTOR_DOSES",
    "INVARIANT_ATOL",
    "INVARIANT_RTOL",
    "PREDICTOR_DOSE_ROW_FIELDS",
    "PredictorDoseTransform",
    "run_predictor_dose",
    "transform_predictor_snapshot",
    "verify_predictor_transform",
]
