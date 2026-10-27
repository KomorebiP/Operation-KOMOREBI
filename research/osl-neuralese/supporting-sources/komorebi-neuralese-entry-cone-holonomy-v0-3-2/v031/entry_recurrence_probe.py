#!/usr/bin/env python3
"""Entry/recurrent computations used by the registered Neuralese v0.3.1 runner.

This module is intentionally import-only.  Learned checkpoint access is owned
exclusively by ``run_v031.py``; the former standalone CLI and ``run_probe``
entry point are fail-closed.  For each semantic state q and canonical generator g,
it constructs the same-semantic incoming recurrent representative

    z[q,g] = normalize(M_g a[g^{-1} q]).

It then exhausts every binary suffix through a declared horizon for native
anchors, R-incoming representatives, and F-incoming representatives.
"""

from __future__ import annotations

import hashlib
import importlib
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

# Fail before NumPy or any scientific module is imported when somebody tries
# to revive the retired standalone learned-endpoint CLI.
if __name__ == "__main__":
    raise SystemExit(
        "standalone entry-probe execution is disabled; use the one frozen "
        "v031/run_v031.py registered runner"
    )

import numpy as np


N_STATES = 8
N_OPERATORS = 2
DEFAULT_HORIZON = 8
DEFAULT_EPISODES = 8
EPISODE_SEED_BASE = 940_000
SCHEME_NAMES = ("native_anchor", "incoming_R", "incoming_F")
EXPECTED_SOURCE_DIGESTS = {
    "checkpoint_io.py": "202b246a5c93239fa35db69067f7496bac8b2a05d580fe6fedfb7f99c77c6647",
    "core.py": "d06daf0a9f050391221bb328f0e749c3fe5e12bfb91262849c3ddfff84b7b8ad",
    "checkpoints/projective_terminal_seed0.pt": "b2d16d640dddc4f2f2ed69a4211f0d9948c71c3655901484238fa8ae11c1f702",
    "checkpoints/projective_terminal_seed1.pt": "a52dd3def596553c2880dfd00516bd1bb7492d1cbfab1634b570f27c1737d2d7",
}
EXPECTED_LOCAL_FROZEN_FILES = frozenset(
    {
        "PREREGISTRATION.json",
        "RESEARCH_SPEC.md",
        "entry_recurrence_probe.py",
        "test_entry_recurrence_probe.py",
    }
)


@dataclass(frozen=True)
class SuffixTree:
    """Exact suffix trees, with axes scheme, semantic start, suffix, feature."""

    hidden: tuple[np.ndarray, ...]
    logits: tuple[np.ndarray, ...]
    probabilities: tuple[np.ndarray, ...]
    centered_logits: tuple[np.ndarray, ...]
    predictions: tuple[np.ndarray, ...]
    semantics: tuple[np.ndarray, ...]
    margins: tuple[np.ndarray, ...]


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_source_package(
    source_root: Path, *, include_checkpoint_bytes: bool = True
) -> dict[str, Any]:
    root = Path(source_root).resolve()
    observed: dict[str, str] = {}
    for relative, expected in EXPECTED_SOURCE_DIGESTS.items():
        if not include_checkpoint_bytes and relative.startswith("checkpoints/"):
            continue
        path = root / relative
        if not path.is_file():
            raise FileNotFoundError(f"required frozen source is missing: {path}")
        digest = file_sha256(path)
        if digest != expected:
            raise ValueError(
                f"frozen-source digest mismatch for {relative}: {digest} != {expected}"
            )
        observed[relative] = digest
    return {
        "source_root": str(root),
        "validated_file_count": len(observed),
        "checkpoint_bytes_included": include_checkpoint_bytes,
        "digests": observed,
        "passed": True,
    }


def validate_execution_freeze(freeze_path: Path | None = None) -> dict[str, Any]:
    """Refuse learned endpoint execution unless this exact source was frozen."""

    root = Path(__file__).resolve().parent
    if freeze_path is None:
        # The integrated release has one global scientific freeze.  Keep the
        # legacy explicit-path branch below only for the component's synthetic
        # missing/tamper tests.
        import freeze_v031

        return freeze_v031.validate_execution_freeze(
            root / "V031_EXECUTION_FREEZE.json", root.parent
        )
    path = Path(freeze_path).resolve()
    if not path.is_file():
        raise FileNotFoundError(
            "EXECUTION_FREEZE.json is absent; freeze preregistration and sources before endpoint execution"
        )
    freeze = json.loads(path.read_text(encoding="utf-8"))
    if freeze.get("schema") != "komorebi.neuralese.entry_recurrence_probe.execution_freeze.v1":
        raise ValueError("unexpected entry-probe execution-freeze schema")
    if freeze.get("status") != "FROZEN_BEFORE_LEARNED_ENDPOINT_INSPECTION":
        raise ValueError("execution freeze does not certify the pre-endpoint boundary")
    local_files = freeze.get("local_files")
    if not isinstance(local_files, dict) or set(local_files) != EXPECTED_LOCAL_FROZEN_FILES:
        raise ValueError("execution-freeze local file set does not match the scientific source set")
    for relative, expected in local_files.items():
        observed = file_sha256(root / relative)
        if observed != expected:
            raise ValueError(f"local frozen-source mismatch for {relative}: {observed} != {expected}")
    profile = freeze.get("registered_profile", {})
    if (
        profile.get("checkpoint_seeds") != [0, 1]
        or int(profile.get("episodes_per_checkpoint", -1)) != DEFAULT_EPISODES
        or int(profile.get("max_suffix_horizon", -1)) != DEFAULT_HORIZON
        or profile.get("episode_seeds") != {"0": EPISODE_SEED_BASE, "1": EPISODE_SEED_BASE + 1000}
    ):
        raise ValueError("execution-freeze profile does not match the registered defaults")
    structural = freeze.get("structural_validation", {})
    if structural.get("status") != "PASS" or int(structural.get("test_count", -1)) < 7:
        raise ValueError("synthetic structural validation was not frozen as passing")
    return {
        "execution_freeze": str(path),
        "execution_freeze_sha256": file_sha256(path),
        "local_file_count": len(local_files),
        "structural_test_count": int(structural["test_count"]),
        "passed": True,
    }


def load_upstream(source_root: Path):
    """Load only the hash-validated v0.3.0 checkpoint and task helpers."""

    validation = validate_source_package(source_root)
    root = Path(source_root).resolve()
    sys.path.insert(0, str(root))
    try:
        checkpoint_io = importlib.import_module("checkpoint_io")
        core = importlib.import_module("core")
    finally:
        if sys.path and sys.path[0] == str(root):
            sys.path.pop(0)
    for module in (checkpoint_io, core):
        if Path(module.__file__).resolve().parent != root:
            raise ImportError(f"module collision: {module.__name__} was not loaded from {root}")
    return checkpoint_io, core, validation


def normalize_fail_closed(states: np.ndarray, epsilon: float = 1e-12) -> np.ndarray:
    array = np.asarray(states, dtype=np.float64)
    if array.shape[-1] != N_STATES or not np.isfinite(array).all():
        raise ArithmeticError("invalid recurrent state")
    norms = np.linalg.norm(array, axis=-1, keepdims=True)
    if not np.isfinite(norms).all() or np.any(norms <= epsilon):
        raise ArithmeticError("zero, tiny, or nonfinite recurrent ray")
    output = array / norms
    if not np.isfinite(output).all():
        raise ArithmeticError("normalization produced a nonfinite state")
    return output


def softmax_fail_closed(logits: np.ndarray) -> np.ndarray:
    values = np.asarray(logits, dtype=np.float64)
    if not np.isfinite(values).all():
        raise ArithmeticError("nonfinite logits")
    shifted = values - np.max(values, axis=-1, keepdims=True)
    exponential = np.exp(shifted)
    denominator = np.sum(exponential, axis=-1, keepdims=True)
    if np.any(denominator <= 0.0) or not np.isfinite(denominator).all():
        raise ArithmeticError("invalid softmax denominator")
    return exponential / denominator


def target_margins(logits: np.ndarray, semantics: np.ndarray) -> np.ndarray:
    values = np.asarray(logits, dtype=np.float64)
    labels = np.broadcast_to(np.asarray(semantics, dtype=np.int64)[None, ...], values.shape[:-1])
    selected = np.take_along_axis(values, labels[..., None], axis=-1)[..., 0]
    alternatives = values.copy()
    np.put_along_axis(alternatives, labels[..., None], -np.inf, axis=-1)
    margins = selected - np.max(alternatives, axis=-1)
    if not np.isfinite(margins).all():
        raise ArithmeticError("nonfinite target margin")
    return margins


def positive_ray_angle(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    left_unit = normalize_fail_closed(left)
    right_unit = normalize_fail_closed(right)
    cosine = np.sum(left_unit * right_unit, axis=-1)
    return np.arccos(np.clip(cosine, -1.0, 1.0))


def incoming_representatives(
    weights: Any,
    tables: np.ndarray,
    maps: np.ndarray,
    canonical_to_slot: np.ndarray,
    core: Any,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return native anchors, two incoming tables, canonical codes and maps."""

    mapping = np.asarray(canonical_to_slot, dtype=np.int64)
    if mapping.shape != (2,) or set(mapping.tolist()) != {0, 1}:
        raise ValueError("canonical_to_slot must be a permutation of [0, 1]")
    codes = core.encode_tables(weights, np.asarray(tables)[None, ...], np.float64)[0]
    canonical_codes = codes[mapping]
    canonical_maps = np.asarray(maps, dtype=np.int64)[mapping]
    native = weights.state_embedding.astype(np.float64, copy=True)
    normalize_fail_closed(native)
    incoming = np.empty((N_OPERATORS, N_STATES, N_STATES), dtype=np.float64)
    labels = np.arange(N_STATES, dtype=np.int64)
    for generator in range(N_OPERATORS):
        inverse_sources = np.argsort(canonical_maps[generator])
        if not np.array_equal(canonical_maps[generator, inverse_sources], labels):
            raise ArithmeticError("incoming route does not preserve declared semantic endpoint")
        unnormalized = np.einsum(
            "ij,qj->qi", canonical_codes[generator], native[inverse_sources]
        )
        incoming[generator] = normalize_fail_closed(unnormalized)
    return native, incoming, canonical_codes, canonical_maps


def enumerate_suffix_tree(
    initial_states: np.ndarray,
    canonical_codes: np.ndarray,
    canonical_maps: np.ndarray,
    decoder: np.ndarray,
    max_horizon: int,
) -> SuffixTree:
    if max_horizon < 0:
        raise ValueError("max_horizon must be nonnegative")
    initial = np.asarray(initial_states, dtype=np.float64)
    if initial.ndim != 3 or initial.shape[1:] != (N_STATES, N_STATES):
        raise ValueError("initial_states must have shape (schemes, 8, 8)")
    codes = np.asarray(canonical_codes, dtype=np.float64)
    maps = np.asarray(canonical_maps, dtype=np.int64)
    readout = np.asarray(decoder, dtype=np.float64)
    if codes.shape != (2, 8, 8) or maps.shape != (2, 8) or readout.shape != (8, 8):
        raise ValueError("invalid code, map, or decoder shape")
    if not np.isfinite(initial).all() or not np.isfinite(codes).all() or not np.isfinite(readout).all():
        raise ArithmeticError("nonfinite tree input")

    hidden = initial[:, :, None, :].copy()
    semantics = np.arange(N_STATES, dtype=np.int64)[:, None]
    hidden_rows: list[np.ndarray] = []
    logit_rows: list[np.ndarray] = []
    probability_rows: list[np.ndarray] = []
    centered_rows: list[np.ndarray] = []
    prediction_rows: list[np.ndarray] = []
    semantic_rows: list[np.ndarray] = []
    margin_rows: list[np.ndarray] = []
    for depth in range(max_horizon + 1):
        logits = np.einsum("sqnd,kd->sqnk", hidden, readout)
        centered = logits - np.mean(logits, axis=-1, keepdims=True)
        predictions = np.argmax(logits, axis=-1).astype(np.int64)
        probabilities = softmax_fail_closed(logits)
        margins = target_margins(logits, semantics)
        hidden_rows.append(hidden)
        logit_rows.append(logits)
        probability_rows.append(probabilities)
        centered_rows.append(centered)
        prediction_rows.append(predictions)
        semantic_rows.append(semantics.copy())
        margin_rows.append(margins)
        if depth == max_horizon:
            break
        expanded = np.einsum("aij,sqnj->sqnai", codes, hidden)
        hidden = normalize_fail_closed(expanded.reshape(initial.shape[0], N_STATES, -1, N_STATES))
        semantics = np.stack([maps[a, semantics] for a in range(N_OPERATORS)], axis=-1)
        semantics = semantics.reshape(N_STATES, -1)
    return SuffixTree(
        hidden=tuple(hidden_rows),
        logits=tuple(logit_rows),
        probabilities=tuple(probability_rows),
        centered_logits=tuple(centered_rows),
        predictions=tuple(prediction_rows),
        semantics=tuple(semantic_rows),
        margins=tuple(margin_rows),
    )


def _depth_selection(max_horizon: int, positive_only: bool = False) -> range:
    return range(1 if positive_only else 0, max_horizon + 1)


def _flatten_scheme(
    rows: Sequence[np.ndarray], scheme: int, max_horizon: int, state: int | None = None,
    positive_only: bool = False,
) -> np.ndarray:
    depths = _depth_selection(max_horizon, positive_only)
    pieces = []
    for depth in depths:
        current = rows[depth][scheme]
        pieces.append(current.reshape(-1, *current.shape[2:]) if state is None else current[state])
    if not pieces:
        example = rows[0][scheme]
        trailing = example.shape[2:]
        return np.empty((0, *trailing), dtype=example.dtype)
    return np.concatenate(pieces, axis=0)


def _flatten_semantics(
    rows: Sequence[np.ndarray], max_horizon: int, state: int | None = None,
    positive_only: bool = False,
) -> np.ndarray:
    pieces = []
    for depth in _depth_selection(max_horizon, positive_only):
        current = rows[depth]
        pieces.append(current.reshape(-1) if state is None else current[state])
    return np.concatenate(pieces) if pieces else np.empty(0, dtype=np.int64)


def scheme_summary(tree: SuffixTree, scheme: int, max_horizon: int) -> dict[str, Any]:
    predictions = _flatten_scheme(tree.predictions, scheme, max_horizon)
    semantics = _flatten_semantics(tree.semantics, max_horizon)
    margins = _flatten_scheme(tree.margins, scheme, max_horizon)
    correct = predictions == semantics
    shell_errors = []
    shell_minimum_margins = []
    for depth in range(max_horizon + 1):
        shell_prediction = tree.predictions[depth][scheme].reshape(-1)
        shell_semantic = tree.semantics[depth].reshape(-1)
        shell_errors.append(int(np.sum(shell_prediction != shell_semantic)))
        shell_minimum_margins.append(float(np.min(tree.margins[depth][scheme])))
    minimum_margin = float(np.min(margins))
    all_argmax_correct = bool(np.all(correct))
    return {
        "scheme": SCHEME_NAMES[scheme],
        "decision_count": int(predictions.size),
        "correct_decision_count": int(np.sum(correct)),
        "error_count": int(np.sum(~correct)),
        "accuracy": float(np.mean(correct)),
        "all_argmax_correct": all_argmax_correct,
        "minimum_target_margin": minimum_margin,
        "strict_hard_pass": bool(all_argmax_correct and minimum_margin > 0.0),
        "errors_by_exact_suffix_depth": shell_errors,
        "minimum_target_margin_by_exact_suffix_depth": shell_minimum_margins,
        "errors_by_semantic_start": [
            int(
                np.sum(
                    _flatten_scheme(tree.predictions, scheme, max_horizon, state)
                    != _flatten_semantics(tree.semantics, max_horizon, state)
                )
            )
            for state in range(N_STATES)
        ],
        "depth_zero_predictions": tree.predictions[0][scheme, :, 0].tolist(),
        "depth_zero_target_margins": tree.margins[0][scheme, :, 0].tolist(),
        "positive_depth_decision_count": int(sum(N_STATES * 2**d for d in range(1, max_horizon + 1))),
        "positive_depth_error_count": int(sum(shell_errors[1:])),
    }


def compare_schemes(
    tree: SuffixTree,
    left: int,
    right: int,
    max_horizon: int,
) -> dict[str, Any]:
    horizon_records: list[dict[str, Any]] = []
    state_records: list[dict[str, Any]] = []
    first_disagreement: int | None = None
    first_soft_difference: int | None = None
    for horizon in range(max_horizon + 1):
        left_prediction = _flatten_scheme(tree.predictions, left, horizon)
        right_prediction = _flatten_scheme(tree.predictions, right, horizon)
        semantics = _flatten_semantics(tree.semantics, horizon)
        left_probability = _flatten_scheme(tree.probabilities, left, horizon)
        right_probability = _flatten_scheme(tree.probabilities, right, horizon)
        left_centered = _flatten_scheme(tree.centered_logits, left, horizon)
        right_centered = _flatten_scheme(tree.centered_logits, right, horizon)
        left_hidden = _flatten_scheme(tree.hidden, left, horizon)
        right_hidden = _flatten_scheme(tree.hidden, right, horizon)
        probability_difference = left_probability - right_probability
        centered_difference = left_centered - right_centered
        angles = positive_ray_angle(left_hidden, right_hidden)
        hard_different = left_prediction != right_prediction
        left_correct = left_prediction == semantics
        right_correct = right_prediction == semantics
        if first_disagreement is None and np.any(
            tree.predictions[horizon][left] != tree.predictions[horizon][right]
        ):
            first_disagreement = horizon
        if first_soft_difference is None and (
            np.any(tree.probabilities[horizon][left] != tree.probabilities[horizon][right])
            or np.any(tree.centered_logits[horizon][left] != tree.centered_logits[horizon][right])
        ):
            first_soft_difference = horizon
        horizon_records.append(
            {
                "H": horizon,
                "cumulative_decision_count": int(left_prediction.size),
                "hard_signature_equal": bool(np.array_equal(left_prediction, right_prediction)),
                "hard_difference_count": int(np.sum(hard_different)),
                "left_error_count": int(np.sum(~left_correct)),
                "right_error_count": int(np.sum(~right_correct)),
                "repaired_error_count": int(np.sum((~left_correct) & right_correct)),
                "introduced_error_count": int(np.sum(left_correct & (~right_correct))),
                "probability_max_abs_difference": float(np.max(np.abs(probability_difference))),
                "probability_rms_difference": float(np.sqrt(np.mean(probability_difference**2))),
                "centered_logit_max_abs_difference": float(np.max(np.abs(centered_difference))),
                "centered_logit_rms_difference": float(np.sqrt(np.mean(centered_difference**2))),
                "positive_ray_angle_max_radians": float(np.max(angles)),
                "positive_ray_angle_mean_radians": float(np.mean(angles)),
            }
        )
    for state in range(N_STATES):
        left_prediction = _flatten_scheme(tree.predictions, left, max_horizon, state)
        right_prediction = _flatten_scheme(tree.predictions, right, max_horizon, state)
        semantics = _flatten_semantics(tree.semantics, max_horizon, state)
        left_probability = _flatten_scheme(tree.probabilities, left, max_horizon, state)
        right_probability = _flatten_scheme(tree.probabilities, right, max_horizon, state)
        left_centered = _flatten_scheme(tree.centered_logits, left, max_horizon, state)
        right_centered = _flatten_scheme(tree.centered_logits, right, max_horizon, state)
        angles = positive_ray_angle(
            _flatten_scheme(tree.hidden, left, max_horizon, state),
            _flatten_scheme(tree.hidden, right, max_horizon, state),
        )
        left_correct = left_prediction == semantics
        right_correct = right_prediction == semantics
        state_records.append(
            {
                "semantic_state": state,
                "decision_count": int(left_prediction.size),
                "hard_signature_equal": bool(np.array_equal(left_prediction, right_prediction)),
                "hard_difference_count": int(np.sum(left_prediction != right_prediction)),
                "left_error_count": int(np.sum(~left_correct)),
                "right_error_count": int(np.sum(~right_correct)),
                "repaired_error_count": int(np.sum((~left_correct) & right_correct)),
                "introduced_error_count": int(np.sum(left_correct & (~right_correct))),
                "probability_max_abs_difference": float(np.max(np.abs(left_probability - right_probability))),
                "centered_logit_max_abs_difference": float(np.max(np.abs(left_centered - right_centered))),
                "positive_ray_angle_max_radians": float(np.max(angles)),
            }
        )
    terminal = horizon_records[-1]
    positive_depth: dict[str, Any] | None = None
    if max_horizon >= 1:
        left_prediction = _flatten_scheme(
            tree.predictions, left, max_horizon, positive_only=True
        )
        right_prediction = _flatten_scheme(
            tree.predictions, right, max_horizon, positive_only=True
        )
        semantics = _flatten_semantics(tree.semantics, max_horizon, positive_only=True)
        probability_difference = _flatten_scheme(
            tree.probabilities, left, max_horizon, positive_only=True
        ) - _flatten_scheme(tree.probabilities, right, max_horizon, positive_only=True)
        centered_difference = _flatten_scheme(
            tree.centered_logits, left, max_horizon, positive_only=True
        ) - _flatten_scheme(tree.centered_logits, right, max_horizon, positive_only=True)
        angles = positive_ray_angle(
            _flatten_scheme(tree.hidden, left, max_horizon, positive_only=True),
            _flatten_scheme(tree.hidden, right, max_horizon, positive_only=True),
        )
        left_correct = left_prediction == semantics
        right_correct = right_prediction == semantics
        positive_depth = {
            "decision_count": int(left_prediction.size),
            "hard_difference_count": int(np.sum(left_prediction != right_prediction)),
            "repaired_error_count": int(np.sum((~left_correct) & right_correct)),
            "introduced_error_count": int(np.sum(left_correct & (~right_correct))),
            "probability_max_abs_difference": float(np.max(np.abs(probability_difference))),
            "probability_rms_difference": float(np.sqrt(np.mean(probability_difference**2))),
            "centered_logit_max_abs_difference": float(np.max(np.abs(centered_difference))),
            "centered_logit_rms_difference": float(np.sqrt(np.mean(centered_difference**2))),
            "positive_ray_angle_max_radians": float(np.max(angles)),
            "positive_ray_angle_mean_radians": float(np.mean(angles)),
        }
    return {
        "left": SCHEME_NAMES[left],
        "right": SCHEME_NAMES[right],
        "first_exact_suffix_depth_with_hard_disagreement": first_disagreement,
        "first_exact_suffix_depth_with_bitwise_soft_difference": first_soft_difference,
        "through_H": max_horizon,
        "hard_signature_equal": terminal["hard_signature_equal"],
        "hard_difference_count": terminal["hard_difference_count"],
        "repaired_error_count": terminal["repaired_error_count"],
        "introduced_error_count": terminal["introduced_error_count"],
        "positive_suffix_depths_only": positive_depth,
        "horizons": horizon_records,
        "states": state_records,
    }


def evaluate_episode(weights: Any, batch: Any, episode: int, core: Any, max_horizon: int) -> dict[str, Any]:
    native, incoming, codes, maps = incoming_representatives(
        weights,
        batch.tables[episode],
        batch.maps[episode],
        batch.canonical_to_slot[episode],
        core,
    )
    initials = np.stack((native, incoming[0], incoming[1]), axis=0)
    tree = enumerate_suffix_tree(initials, codes, maps, weights.decoder, max_horizon)
    summaries = [scheme_summary(tree, scheme, max_horizon) for scheme in range(3)]
    comparisons = [
        compare_schemes(tree, 0, 1, max_horizon),
        compare_schemes(tree, 0, 2, max_horizon),
        compare_schemes(tree, 1, 2, max_horizon),
    ]
    native_errors = summaries[0]["error_count"]
    route_records = []
    for route_scheme, comparison in zip((1, 2), comparisons[:2]):
        route_records.append(
            {
                "scheme": SCHEME_NAMES[route_scheme],
                "strict_hard_pass": summaries[route_scheme]["strict_hard_pass"],
                "native_error_count": native_errors,
                "reanchored_error_count": summaries[route_scheme]["error_count"],
                "repaired_error_count": comparison["repaired_error_count"],
                "introduced_error_count": comparison["introduced_error_count"],
                "repair_without_hard_regression": bool(
                    summaries[route_scheme]["strict_hard_pass"]
                    and comparison["repaired_error_count"] == native_errors
                    and comparison["introduced_error_count"] == 0
                ),
            }
        )
    return {
        "episode_index": episode,
        "canonical_to_slot": np.asarray(batch.canonical_to_slot[episode], dtype=int).tolist(),
        "anchor_norms": np.linalg.norm(native, axis=1).tolist(),
        "incoming_R_norms": np.linalg.norm(incoming[0], axis=1).tolist(),
        "incoming_F_norms": np.linalg.norm(incoming[1], axis=1).tolist(),
        "schemes": summaries,
        "comparisons": comparisons,
        "uniform_reanchoring": route_records,
    }


def aggregate_results(seed_records: dict[str, Any], max_horizon: int) -> dict[str, Any]:
    episodes = [episode for seed in seed_records.values() for episode in seed["episodes"]]
    scheme_totals: dict[str, Any] = {}
    for scheme_index, name in enumerate(SCHEME_NAMES):
        records = [episode["schemes"][scheme_index] for episode in episodes]
        decisions = sum(record["decision_count"] for record in records)
        errors = sum(record["error_count"] for record in records)
        shell_errors = [
            sum(record["errors_by_exact_suffix_depth"][depth] for record in records)
            for depth in range(max_horizon + 1)
        ]
        scheme_totals[name] = {
            "decision_count": decisions,
            "error_count": errors,
            "accuracy": (decisions - errors) / decisions,
            "all_argmax_correct": errors == 0,
            "minimum_target_margin": min(record["minimum_target_margin"] for record in records),
            "strict_hard_pass": bool(
                errors == 0 and min(record["minimum_target_margin"] for record in records) > 0.0
            ),
            "errors_by_exact_suffix_depth": shell_errors,
        }
    comparison_totals: dict[str, Any] = {}
    for comparison_index in range(3):
        records = [episode["comparisons"][comparison_index] for episode in episodes]
        key = f"{records[0]['left']}__vs__{records[0]['right']}"
        comparison_totals[key] = {
            "hard_signature_equal_in_every_episode": all(record["hard_signature_equal"] for record in records),
            "hard_difference_count": sum(record["hard_difference_count"] for record in records),
            "repaired_error_count": sum(record["repaired_error_count"] for record in records),
            "introduced_error_count": sum(record["introduced_error_count"] for record in records),
            "maximum_probability_abs_difference": max(
                record["horizons"][-1]["probability_max_abs_difference"] for record in records
            ),
            "maximum_centered_logit_abs_difference": max(
                record["horizons"][-1]["centered_logit_max_abs_difference"] for record in records
            ),
            "maximum_positive_ray_angle_radians": max(
                record["horizons"][-1]["positive_ray_angle_max_radians"] for record in records
            ),
            "positive_suffix_depths_only": {
                "maximum_probability_abs_difference": max(
                    record["positive_suffix_depths_only"]["probability_max_abs_difference"]
                    for record in records
                ),
                "maximum_centered_logit_abs_difference": max(
                    record["positive_suffix_depths_only"]["centered_logit_max_abs_difference"]
                    for record in records
                ),
                "maximum_positive_ray_angle_radians": max(
                    record["positive_suffix_depths_only"]["positive_ray_angle_max_radians"]
                    for record in records
                ),
            },
        }
    native_errors = scheme_totals["native_anchor"]["error_count"]
    reanchor_gates = {}
    for route in ("incoming_R", "incoming_F"):
        comparison = comparison_totals[f"native_anchor__vs__{route}"]
        reanchor_gates[route] = bool(
            scheme_totals[route]["strict_hard_pass"]
            and comparison["repaired_error_count"] == native_errors
            and comparison["introduced_error_count"] == 0
        )
    expected_seed0_predictions = list(range(N_STATES))
    expected_seed0_predictions[2] = 6
    native_entry_pattern = bool(
        all(
            episode["schemes"][0]["errors_by_exact_suffix_depth"]
            == [1] + [0] * max_horizon
            and all(
                margin > 0.0
                for margin in episode["schemes"][0]["minimum_target_margin_by_exact_suffix_depth"][1:]
            )
            and episode["schemes"][0]["errors_by_semantic_start"]
            == [0, 0, 1, 0, 0, 0, 0, 0]
            and episode["schemes"][0]["depth_zero_predictions"]
            == expected_seed0_predictions
            and episode["schemes"][0]["depth_zero_target_margins"][2] < 0.0
            and all(
                margin > 0.0
                for state, margin in enumerate(
                    episode["schemes"][0]["depth_zero_target_margins"]
                )
                if state != 2
            )
            for episode in seed_records["0"]["episodes"]
        )
        and all(
            episode["schemes"][0]["errors_by_exact_suffix_depth"]
            == [0] * (max_horizon + 1)
            and all(
                margin > 0.0
                for margin in episode["schemes"][0]["minimum_target_margin_by_exact_suffix_depth"]
            )
            and episode["schemes"][0]["depth_zero_predictions"] == list(range(N_STATES))
            for episode in seed_records["1"]["episodes"]
        )
    )
    return {
        "episode_count": len(episodes),
        "schemes": scheme_totals,
        "comparisons": comparison_totals,
        "gates": {
            "E0_source_and_numeric_integrity": True,
            "A0_native_anchors_hard_correct_through_H": scheme_totals["native_anchor"]["strict_hard_pass"],
            "I0_known_seed0_defect_confined_to_empty_suffix": native_entry_pattern,
            "R0_uniform_R_reanchor_repairs_without_hard_regression": reanchor_gates["incoming_R"],
            "F0_uniform_F_reanchor_repairs_without_hard_regression": reanchor_gates["incoming_F"],
            "P0_incoming_routes_have_identical_hard_signatures": comparison_totals[
                "incoming_R__vs__incoming_F"
            ]["hard_signature_equal_in_every_episode"],
        },
    }


def atomic_json(path: Path, value: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(target.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, target)


def run_probe(source_root: Path, max_horizon: int = 8, episode_count: int = 8) -> dict[str, Any]:
    del source_root, max_horizon, episode_count
    raise RuntimeError(
        "run_probe is disabled: learned endpoints may only be accessed by "
        "the one frozen v031/run_v031.py registered runner"
    )


def main() -> int:
    raise SystemExit(
        "standalone entry-probe execution is disabled; use the one frozen "
        "v031/run_v031.py registered runner"
    )


if __name__ == "__main__":
    raise SystemExit(main())
