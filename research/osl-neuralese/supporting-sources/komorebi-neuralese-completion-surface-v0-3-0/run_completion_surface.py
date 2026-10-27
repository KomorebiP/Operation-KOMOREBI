#!/usr/bin/env python3
"""Exact two-index hard causal-completion audit for frozen Neuralese checkpoints.

The scientific runner works one episode at a time.  Signature identifiers are
therefore meaningful only inside one ``HardSignatureTable``; callers must never
compare bare integer identifiers produced for different episodes or horizons.
"""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import os
import platform
import sys
import time
from pathlib import Path
from typing import Any, Iterable, Literal, Sequence

import numpy as np

from checkpoint_io import LinearOperatorWeights, file_sha256, load_checkpoint
from core import N_STATES, canonical_maps, encode_tables, sample_batch
from soft_surface import compute_soft_completion_surface


ROOT = Path(__file__).resolve().parent
PREREGISTRATION = ROOT / "PREREGISTRATION.json"
EXECUTION_FREEZE = ROOT / "EXECUTION_FREEZE.json"
LINEAGE_REGRESSION = ROOT / "results" / "LINEAGE_REGRESSION.json"
RESULTS_DIR = ROOT / "results"
MINIMUM_NORM = 1e-12
REQUIRED_FROZEN_FILES = frozenset(
    {
        "PREREGISTRATION.json",
        "RESEARCH_SPEC.md",
        "checkpoint_io.py",
        "checkpoints/projective_terminal_seed0.pt",
        "checkpoints/projective_terminal_seed1.pt",
        "core.py",
        "relator_witness.py",
        "results/LINEAGE_REGRESSION.json",
        "run_completion_surface.py",
        "run_lineage_regression.py",
        "soft_surface.py",
        "test_completion_surface.py",
    }
)

HistoryMode = Literal["cumulative", "exact"]
FutureMode = Literal["cumulative", "exact"]


@dataclasses.dataclass(frozen=True)
class EpisodeTree:
    episode_id: str
    scope_token: object
    max_depth: int
    hidden_by_depth: tuple[np.ndarray, ...]
    logits_by_depth: tuple[np.ndarray, ...]
    probabilities_by_depth: tuple[np.ndarray, ...]
    predictions_by_depth: tuple[np.ndarray, ...]
    semantic_by_depth: tuple[np.ndarray, ...]
    margins_by_depth: tuple[np.ndarray, ...]
    codes: np.ndarray
    slot_maps: np.ndarray
    canonical_to_slot: np.ndarray


@dataclasses.dataclass(frozen=True)
class HardSignatureTable:
    episode_id: str
    scope_token: object
    max_horizon: int
    # ``ids_by_horizon[h][d]`` contains IDs for nodes at exact history depth d.
    ids_by_horizon: tuple[tuple[np.ndarray, ...], ...]
    class_counts: tuple[int, ...]

    def ids(self, horizon: int, history_depth: int) -> np.ndarray:
        if not 0 <= horizon <= self.max_horizon:
            raise IndexError("signature horizon out of range")
        rows = self.ids_by_horizon[horizon]
        if not 0 <= history_depth < len(rows):
            raise IndexError("history depth is incompatible with signature horizon")
        return rows[history_depth]

    def assert_compatible(self, other: "HardSignatureTable", horizon: int) -> None:
        if self.scope_token is not other.scope_token or horizon > min(
            self.max_horizon, other.max_horizon
        ):
            raise ValueError("signature IDs from different episode/horizon scopes cannot be compared")


@dataclasses.dataclass(frozen=True)
class FutureAggregates:
    episode_id: str
    scope_token: object
    max_horizon: int
    correct_counts: tuple[tuple[np.ndarray, ...], ...]
    all_correct: tuple[tuple[np.ndarray, ...], ...]
    minimum_margin: tuple[tuple[np.ndarray, ...], ...]

    def assert_compatible(self, tree: EpisodeTree) -> None:
        if self.scope_token is not tree.scope_token:
            raise ValueError("future aggregates belong to a different episode")


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def validate_execution_freeze(
    freeze_path: Path = EXECUTION_FREEZE,
    lineage_path: Path = LINEAGE_REGRESSION,
) -> dict[str, Any]:
    """Verify frozen scientific sources and the required inherited regression."""

    freeze = json.loads(Path(freeze_path).read_text(encoding="utf-8"))
    if freeze.get("schema") != "komorebi.neuralese.completion_surface.execution_freeze.v1":
        raise ValueError("unexpected execution-freeze schema")
    frozen_files = freeze.get("files")
    if not isinstance(frozen_files, dict) or not frozen_files:
        raise ValueError("execution freeze has no source digests")
    if set(frozen_files) != REQUIRED_FROZEN_FILES:
        missing = sorted(REQUIRED_FROZEN_FILES - set(frozen_files))
        extra = sorted(set(frozen_files) - REQUIRED_FROZEN_FILES)
        raise ValueError(
            f"execution freeze file set mismatch; missing={missing}, extra={extra}"
        )
    for relative, expected in frozen_files.items():
        path = ROOT / relative
        if not path.is_file():
            raise ValueError(f"frozen source is missing: {relative}")
        observed = file_sha256(path)
        if observed != expected:
            raise ValueError(
                f"frozen source digest mismatch for {relative}: {observed} != {expected}"
            )
    structural = freeze.get("structural_validation", {})
    if structural.get("status") != "PASS" or int(structural.get("test_count", -1)) < 17:
        raise ValueError("structural validation is not frozen as passing")
    lineage = json.loads(Path(lineage_path).read_text(encoding="utf-8"))
    if not bool(lineage.get("passed")):
        raise ValueError("inherited v0.2.1 lineage regression did not pass")
    for seed in ("0", "1"):
        record = lineage.get("seeds", {}).get(seed, {})
        if (
            int(record.get("decision_count", -1)) != 61_440
            or float(record.get("semantic_continuation_accuracy", -1.0)) != 1.0
            or int(record.get("maximum_split_multiplicity", -1)) != 1
            or not bool(record.get("passed"))
        ):
            raise ValueError(f"lineage regression mismatch for checkpoint seed {seed}")
    return {
        "freeze_file": str(Path(freeze_path).resolve()),
        "freeze_sha256": file_sha256(Path(freeze_path)),
        "validated_file_count": len(frozen_files),
        "structural_test_count": int(structural["test_count"]),
        "lineage_regression_file": str(Path(lineage_path).resolve()),
        "lineage_regression_sha256": file_sha256(Path(lineage_path)),
        "passed": True,
    }


def normalize_fail_closed(states: np.ndarray, epsilon: float = MINIMUM_NORM) -> np.ndarray:
    """Normalize rows, rejecting zero, tiny, or nonfinite projective states."""

    array = np.asarray(states, dtype=np.float64)
    if array.ndim < 1 or array.shape[-1] != N_STATES:
        raise ValueError("states must have final dimension eight")
    if not np.isfinite(array).all():
        raise ArithmeticError("nonfinite projective state")
    norms = np.linalg.norm(array, axis=-1, keepdims=True)
    if not np.isfinite(norms).all() or np.any(norms <= float(epsilon)):
        raise ArithmeticError("projective recurrence reached a zero or tiny ray")
    normalized = array / norms
    if not np.isfinite(normalized).all():
        raise ArithmeticError("normalization produced a nonfinite state")
    return normalized


def softmax_fail_closed(logits: np.ndarray) -> np.ndarray:
    values = np.asarray(logits, dtype=np.float64)
    if not np.isfinite(values).all():
        raise ArithmeticError("nonfinite decoder logit")
    shifted = values - np.max(values, axis=-1, keepdims=True)
    exponential = np.exp(shifted)
    denominator = np.sum(exponential, axis=-1, keepdims=True)
    if (
        not np.isfinite(exponential).all()
        or not np.isfinite(denominator).all()
        or np.any(denominator <= 0.0)
    ):
        raise ArithmeticError("invalid softmax probability")
    probabilities = exponential / denominator
    if not np.isfinite(probabilities).all():
        raise ArithmeticError("nonfinite softmax probability")
    return probabilities


def canonical_word_to_slots(
    canonical_to_slot: np.ndarray, word: Sequence[int]
) -> np.ndarray:
    raw_mapping = np.asarray(canonical_to_slot)
    raw_symbols = np.asarray(tuple(word))
    if not np.issubdtype(raw_mapping.dtype, np.integer):
        raise ValueError("canonical_to_slot must have an integer dtype")
    if raw_symbols.size and not np.issubdtype(raw_symbols.dtype, np.integer):
        raise ValueError("canonical words must have an integer dtype")
    mapping = raw_mapping.astype(np.int64, copy=False)
    symbols = raw_symbols.astype(np.int64, copy=False)
    if mapping.shape != (2,) or set(mapping.tolist()) != {0, 1}:
        raise ValueError("canonical_to_slot must be a permutation of [0, 1]")
    if symbols.size and (np.any(symbols < 0) or np.any(symbols > 1)):
        raise ValueError("canonical words must contain only 0 and 1")
    return mapping[symbols] if symbols.size else np.empty(0, dtype=np.int64)


def _target_margins(logits: np.ndarray, target: np.ndarray) -> np.ndarray:
    rows = np.arange(logits.shape[0])
    selected = logits[rows, target]
    alternatives = logits.copy()
    alternatives[rows, target] = -np.inf
    margins = selected - np.max(alternatives, axis=1)
    if not np.isfinite(margins).all():
        raise ArithmeticError("nonfinite target margin")
    return margins


def build_episode_tree(
    weights: LinearOperatorWeights,
    episode_tables: np.ndarray,
    episode_maps: np.ndarray,
    canonical_to_slot: np.ndarray,
    max_depth: int,
    episode_id: str = "episode",
) -> EpisodeTree:
    """Enumerate all starts and all canonical binary words through ``max_depth``."""

    if max_depth < 0:
        raise ValueError("max_depth must be nonnegative")
    weights.validate()
    tables = np.asarray(episode_tables)
    raw_maps = np.asarray(episode_maps)
    if not np.issubdtype(raw_maps.dtype, np.integer):
        raise ValueError("episode maps must have an integer dtype")
    maps = raw_maps.astype(np.int64, copy=False)
    if tables.shape != (2, N_STATES, N_STATES) or maps.shape != (2, N_STATES):
        raise ValueError("one episode must contain two 8-state operator tables/maps")
    if not np.isfinite(tables).all():
        raise ArithmeticError("nonfinite episode table")
    if any(not np.array_equal(np.sort(row), np.arange(N_STATES)) for row in maps):
        raise ValueError("each episode map must be an eight-state permutation")
    if not np.array_equal(tables, np.eye(N_STATES, dtype=tables.dtype)[maps]):
        raise ValueError("episode tables do not encode the declared integer maps")
    mapping = np.asarray(canonical_to_slot, dtype=np.int64)
    canonical_word_to_slots(mapping, ())
    codes = encode_tables(weights, tables[None, ...], np.float64)[0]
    if not np.isfinite(codes).all():
        raise ArithmeticError("nonfinite encoded operator")
    canonical_codes = codes[mapping]
    canonical_slot_maps = maps[mapping]
    initial = weights.state_embedding.astype(np.float64)
    # The registered recurrence normalizes after each generator application;
    # the depth-zero embedding is validated but deliberately left at its stored scale.
    normalize_fail_closed(initial)
    hidden = initial.copy()
    semantic = np.arange(N_STATES, dtype=np.int64)
    decoder = weights.decoder.astype(np.float64)

    hidden_rows: list[np.ndarray] = []
    logits_rows: list[np.ndarray] = []
    probability_rows: list[np.ndarray] = []
    prediction_rows: list[np.ndarray] = []
    semantic_rows: list[np.ndarray] = []
    margin_rows: list[np.ndarray] = []
    for depth in range(max_depth + 1):
        logits = hidden @ decoder.T
        probabilities = softmax_fail_closed(logits)
        predictions = np.argmax(logits, axis=1).astype(np.int64)
        margins = _target_margins(logits, semantic)
        hidden_rows.append(hidden)
        logits_rows.append(logits)
        probability_rows.append(probabilities)
        prediction_rows.append(predictions)
        semantic_rows.append(semantic)
        margin_rows.append(margins)
        if depth == max_depth:
            break
        unnormalized = np.einsum("oij,nj->noi", canonical_codes, hidden).reshape(-1, N_STATES)
        hidden = normalize_fail_closed(unnormalized)
        semantic = np.stack(
            [canonical_slot_maps[operator, semantic] for operator in range(2)], axis=1
        ).reshape(-1)

    return EpisodeTree(
        episode_id=str(episode_id),
        scope_token=object(),
        max_depth=max_depth,
        hidden_by_depth=tuple(hidden_rows),
        logits_by_depth=tuple(logits_rows),
        probabilities_by_depth=tuple(probability_rows),
        predictions_by_depth=tuple(prediction_rows),
        semantic_by_depth=tuple(semantic_rows),
        margins_by_depth=tuple(margin_rows),
        codes=codes,
        slot_maps=maps,
        canonical_to_slot=mapping.copy(),
    )


def intern_hard_signatures(
    predictions_by_depth: Sequence[np.ndarray],
    max_horizon: int,
    episode_id: str = "episode",
    episode_scope: object | None = None,
) -> HardSignatureTable:
    """Intern exact recursive tuples; no digest is used as an identity surrogate."""

    raw_predictions = tuple(np.asarray(row) for row in predictions_by_depth)
    if any(not np.issubdtype(row.dtype, np.integer) for row in raw_predictions):
        raise ValueError("hard predictions must have an integer dtype")
    predictions = tuple(row.astype(np.int64, copy=False) for row in raw_predictions)
    if not predictions or max_horizon < 0 or max_horizon >= len(predictions):
        raise ValueError("signature horizon is incompatible with trajectory depth")
    for depth, row in enumerate(predictions):
        expected = N_STATES * (2**depth)
        if row.shape != (expected,):
            raise ValueError(f"prediction shell {depth} has shape {row.shape}, expected {(expected,)}")
        if np.any(row < 0) or np.any(row >= N_STATES):
            raise ValueError("hard prediction outside the eight-class domain")

    horizons: list[tuple[np.ndarray, ...]] = []
    base = tuple(row.copy() for row in predictions)
    horizons.append(base)
    class_counts = [len(set(np.concatenate(base).tolist()))]
    for horizon in range(1, max_horizon + 1):
        previous = horizons[horizon - 1]
        intern: dict[tuple[int, int, int], int] = {}
        rows: list[np.ndarray] = []
        for depth in range(len(predictions) - horizon):
            children = previous[depth + 1].reshape(-1, 2)
            current = predictions[depth]
            identifiers = np.empty(current.shape[0], dtype=np.int64)
            for index, (prediction, pair) in enumerate(zip(current, children)):
                key = (int(prediction), int(pair[0]), int(pair[1]))
                identifier = intern.get(key)
                if identifier is None:
                    identifier = len(intern)
                    intern[key] = identifier
                identifiers[index] = identifier
            rows.append(identifiers)
        horizons.append(tuple(rows))
        class_counts.append(len(intern))
    return HardSignatureTable(
        episode_id=str(episode_id),
        scope_token=object() if episode_scope is None else episode_scope,
        max_horizon=max_horizon,
        ids_by_horizon=tuple(horizons),
        class_counts=tuple(class_counts),
    )


def explicit_prediction_signature(
    predictions_by_depth: Sequence[np.ndarray],
    history_depth: int,
    history_index: int,
    horizon: int,
) -> tuple[int, ...]:
    """Breadth-first suffix predictions, used as an independent audit oracle."""

    if min(history_depth, history_index, horizon) < 0:
        raise ValueError("depth, index, and horizon must be nonnegative")
    if history_depth + horizon >= len(predictions_by_depth):
        raise ValueError("requested signature exceeds trajectory tree")
    base_size = len(np.asarray(predictions_by_depth[history_depth]))
    if history_index >= base_size:
        raise IndexError("history index out of range")
    output: list[int] = []
    for suffix_depth in range(horizon + 1):
        width = 2**suffix_depth
        start = history_index * width
        row = np.asarray(predictions_by_depth[history_depth + suffix_depth])
        output.extend(map(int, row[start : start + width]))
    return tuple(output)


def recursive_future_aggregates(tree: EpisodeTree, max_horizon: int) -> FutureAggregates:
    if max_horizon < 0 or max_horizon > tree.max_depth:
        raise ValueError("future horizon exceeds trajectory tree")
    current_correct = tuple(
        prediction == semantic
        for prediction, semantic in zip(tree.predictions_by_depth, tree.semantic_by_depth)
    )
    correct_tables: list[tuple[np.ndarray, ...]] = [
        tuple(row.astype(np.int64) for row in current_correct)
    ]
    all_tables: list[tuple[np.ndarray, ...]] = [current_correct]
    margin_tables: list[tuple[np.ndarray, ...]] = [tree.margins_by_depth]
    for horizon in range(1, max_horizon + 1):
        previous_count = correct_tables[horizon - 1]
        previous_all = all_tables[horizon - 1]
        previous_margin = margin_tables[horizon - 1]
        counts: list[np.ndarray] = []
        all_correct: list[np.ndarray] = []
        minima: list[np.ndarray] = []
        for depth in range(tree.max_depth - horizon + 1):
            child_counts = previous_count[depth + 1].reshape(-1, 2)
            child_all = previous_all[depth + 1].reshape(-1, 2)
            child_margin = previous_margin[depth + 1].reshape(-1, 2)
            counts.append(current_correct[depth].astype(np.int64) + child_counts.sum(axis=1))
            all_correct.append(current_correct[depth] & np.all(child_all, axis=1))
            minima.append(np.minimum(tree.margins_by_depth[depth], child_margin.min(axis=1)))
        correct_tables.append(tuple(counts))
        all_tables.append(tuple(all_correct))
        margin_tables.append(tuple(minima))
    return FutureAggregates(
        episode_id=tree.episode_id,
        scope_token=tree.scope_token,
        max_horizon=max_horizon,
        correct_counts=tuple(correct_tables),
        all_correct=tuple(all_tables),
        minimum_margin=tuple(margin_tables),
    )


def compare_scoped_signature_ids(
    left: HardSignatureTable,
    right: HardSignatureTable,
    horizon: int,
    history_depth: int,
) -> np.ndarray:
    """Compare IDs only after proving their episode/horizon scope is shared."""

    left.assert_compatible(right, horizon)
    left_ids = left.ids(horizon, history_depth)
    right_ids = right.ids(horizon, history_depth)
    if left_ids.shape != right_ids.shape:
        raise ValueError("signature vectors have different shapes")
    return left_ids == right_ids


def select_history_depths(L: int, mode: HistoryMode = "cumulative") -> tuple[int, ...]:
    if L < 0:
        raise ValueError("L must be nonnegative")
    if mode == "cumulative":
        return tuple(range(L + 1))
    if mode == "exact":
        return (L,)
    raise ValueError(f"unknown history mode: {mode}")


def select_future_depths(H: int, mode: FutureMode = "cumulative") -> tuple[int, ...]:
    if H < 0:
        raise ValueError("H must be nonnegative")
    if mode == "cumulative":
        return tuple(range(H + 1))
    if mode == "exact":
        return (H,)
    raise ValueError(f"unknown future mode: {mode}")


def expected_history_count(L: int, mode: HistoryMode = "cumulative") -> int:
    return int(sum(N_STATES * 2**depth for depth in select_history_depths(L, mode)))


def expected_suffix_count(H: int, mode: FutureMode = "cumulative") -> int:
    return int(sum(2**depth for depth in select_future_depths(H, mode)))


def hard_partition_metrics(
    semantic: np.ndarray,
    signature_ids: np.ndarray,
    all_correct: np.ndarray | None = None,
) -> dict[str, Any]:
    """Classify exact hard signatures without conflating partition and correctness."""

    labels = np.asarray(semantic, dtype=np.int64)
    signatures = np.asarray(signature_ids, dtype=np.int64)
    if labels.ndim != 1 or signatures.shape != labels.shape or labels.size == 0:
        raise ValueError("semantic labels and signatures must be nonempty equal vectors")
    if np.any(labels < 0) or np.any(labels >= N_STATES):
        raise ValueError("semantic label outside the eight-state domain")
    correct = (
        np.ones(labels.shape, dtype=bool)
        if all_correct is None
        else np.asarray(all_correct, dtype=bool)
    )
    if correct.shape != labels.shape:
        raise ValueError("all_correct must match semantic labels")

    signatures_by_label: dict[int, set[int]] = {
        label: set(map(int, signatures[labels == label])) for label in range(N_STATES)
    }
    labels_by_signature: dict[int, set[int]] = {}
    for label, signature in zip(labels, signatures):
        labels_by_signature.setdefault(int(signature), set()).add(int(label))
    maximum_split = max(map(len, signatures_by_label.values()))
    maximum_merge = max(map(len, labels_by_signature.values()))
    label_records: dict[str, Any] = {}
    completed = 0
    for label in range(N_STATES):
        member_mask = labels == label
        label_signatures = signatures_by_label[label]
        present = bool(np.any(member_mask))
        unsplit = len(label_signatures) == 1
        unmerged = unsplit and len(labels_by_signature[next(iter(label_signatures))]) == 1
        label_correct = present and bool(np.all(correct[member_mask]))
        complete = present and label_correct and unsplit and unmerged
        completed += int(complete)
        label_records[str(label)] = {
            "present": present,
            "all_declared_decisions_correct": label_correct,
            "signature_count": len(label_signatures),
            "unsplit": unsplit,
            "unmerged": unmerged,
            "complete": complete,
        }
    return {
        "signature_class_count": len(labels_by_signature),
        "maximum_split_multiplicity": maximum_split,
        "maximum_merge_multiplicity": maximum_merge,
        "completed_semantic_labels": completed,
        "semantic_label_completion_fraction": completed / N_STATES,
        "label_records": label_records,
    }


def _decision_vectors(
    tree: EpisodeTree,
    history_depths: Sequence[int],
    future_depths: Sequence[int],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    predictions: list[np.ndarray] = []
    semantics: list[np.ndarray] = []
    margins: list[np.ndarray] = []
    for history_depth in history_depths:
        for future_depth in future_depths:
            absolute_depth = history_depth + future_depth
            if absolute_depth > tree.max_depth:
                raise ValueError("cell exceeds the shared trajectory tree")
            predictions.append(tree.predictions_by_depth[absolute_depth])
            semantics.append(tree.semantic_by_depth[absolute_depth])
            margins.append(tree.margins_by_depth[absolute_depth])
    return np.concatenate(predictions), np.concatenate(semantics), np.concatenate(margins)


def summarize_cell(
    tree: EpisodeTree,
    hard_signatures: HardSignatureTable,
    future_aggregates: FutureAggregates,
    L: int,
    H: int,
    history_mode: HistoryMode = "cumulative",
    future_mode: FutureMode = "cumulative",
) -> dict[str, Any]:
    """Summarize one exact Cartesian history/future cell.

    The hard partition always uses the cumulative signature through H, including
    in shell views; shell selection affects decision, accuracy, and margin rows.
    """

    if L + H > tree.max_depth:
        raise ValueError("requested cell exceeds the trajectory tree")
    if H > hard_signatures.max_horizon or H > future_aggregates.max_horizon:
        raise ValueError("requested H exceeds precomputed tables")
    if hard_signatures.scope_token is not tree.scope_token:
        raise ValueError("hard signatures belong to a different episode")
    future_aggregates.assert_compatible(tree)
    history_depths = select_history_depths(L, history_mode)
    future_depths = select_future_depths(H, future_mode)

    history_semantic = np.concatenate([tree.semantic_by_depth[d] for d in history_depths])
    history_signature = np.concatenate([hard_signatures.ids(H, d) for d in history_depths])
    if future_mode == "cumulative":
        history_correct = np.concatenate(
            [future_aggregates.all_correct[H][d] for d in history_depths]
        )
    else:
        history_correct = np.concatenate(
            [
                (
                    tree.predictions_by_depth[d + H]
                    == tree.semantic_by_depth[d + H]
                ).reshape(tree.semantic_by_depth[d].size, 2**H).all(axis=1)
                for d in history_depths
            ]
        )
    partition = hard_partition_metrics(history_semantic, history_signature, history_correct)
    predictions, semantics, margins = _decision_vectors(tree, history_depths, future_depths)
    finite = np.isfinite(margins)
    correct = predictions == semantics
    history_count = expected_history_count(L, history_mode)
    suffix_count = expected_suffix_count(H, future_mode)
    decision_count = history_count * suffix_count
    if predictions.size != decision_count or history_semantic.size != history_count:
        raise ArithmeticError("enumerated cell count disagrees with registered formula")
    if not np.all(finite):
        raise ArithmeticError("nonfinite statistic reached cell summarization")
    minimum_margin = float(np.min(margins))
    all_decisions_correct = bool(np.all(correct))
    hard_pass = bool(
        all_decisions_correct
        and minimum_margin > 0.0
        and partition["signature_class_count"] == N_STATES
        and partition["maximum_split_multiplicity"] == 1
        and partition["maximum_merge_multiplicity"] == 1
        and partition["semantic_label_completion_fraction"] == 1.0
    )
    return {
        "L": int(L),
        "H": int(H),
        "history_mode": history_mode,
        "future_mode": future_mode,
        "history_count": history_count,
        "suffix_count": suffix_count,
        "decision_count": decision_count,
        "semantic_continuation_accuracy": float(np.mean(correct)),
        "correct_decision_count": int(np.sum(correct)),
        "all_decisions_correct": all_decisions_correct,
        **partition,
        "minimum_target_margin": minimum_margin,
        "p01_target_margin": float(np.quantile(margins, 0.01, method="linear")),
        "median_target_margin": float(np.median(margins)),
        "zero_norm_count": 0,
        "nonfinite_count": 0,
        "hard_completion_pass": hard_pass,
    }


def downset_violations(pass_mask: np.ndarray) -> list[dict[str, list[int]]]:
    mask = np.asarray(pass_mask)
    if mask.ndim != 2 or mask.size == 0:
        raise ValueError("pass mask must be a nonempty two-dimensional array")
    if mask.dtype != np.bool_:
        if not np.all(np.isin(mask, [0, 1])):
            raise ValueError("pass mask must contain only booleans")
        mask = mask.astype(bool)
    violations: list[dict[str, list[int]]] = []
    for L, H in np.argwhere(mask):
        missing = np.argwhere(~mask[: L + 1, : H + 1])
        for lower_L, lower_H in missing:
            violations.append(
                {
                    "passing_cell": [int(L), int(H)],
                    "missing_predecessor": [int(lower_L), int(lower_H)],
                }
            )
    return violations


def validate_downset(pass_mask: np.ndarray) -> bool:
    violations = downset_violations(pass_mask)
    if violations:
        raise ValueError(f"cumulative pass mask is not a down-set: {violations[0]}")
    return True


def diagonal_action_audit(
    tree: EpisodeTree,
    signatures: HardSignatureTable,
    Lmax: int,
    Hmax: int,
) -> dict[str, Any]:
    if signatures.scope_token is not tree.scope_token:
        raise ValueError("hard signatures belong to a different episode")
    if Lmax + Hmax > tree.max_depth or Hmax > signatures.max_horizon:
        raise ValueError("diagonal audit exceeds precomputed tree/signatures")
    cells: list[dict[str, Any]] = []
    for L in range(Lmax):
        for H in range(Hmax):
            source_depths = range(L + 1)
            target_domain_ids = np.concatenate(
                [signatures.ids(H, depth) for depth in range(L + 2)]
            )
            target_domain_semantics = np.concatenate(
                [tree.semantic_by_depth[depth] for depth in range(L + 2)]
            )
            target_labels_by_signature: dict[int, set[int]] = {}
            for signature, label in zip(target_domain_ids, target_domain_semantics):
                target_labels_by_signature.setdefault(int(signature), set()).add(int(label))
            for generator in range(2):
                source_ids: list[np.ndarray] = []
                source_semantics: list[np.ndarray] = []
                endpoint_ids: list[np.ndarray] = []
                endpoint_semantics: list[np.ndarray] = []
                for depth in source_depths:
                    size = tree.semantic_by_depth[depth].size
                    child_indices = 2 * np.arange(size) + generator
                    source_ids.append(signatures.ids(H + 1, depth))
                    source_semantics.append(tree.semantic_by_depth[depth])
                    endpoint_ids.append(signatures.ids(H, depth + 1)[child_indices])
                    endpoint_semantics.append(tree.semantic_by_depth[depth + 1][child_indices])
                source_id = np.concatenate(source_ids)
                source_semantic = np.concatenate(source_semantics)
                endpoint_id = np.concatenate(endpoint_ids)
                endpoint_semantic = np.concatenate(endpoint_semantics)
                slot = int(tree.canonical_to_slot[generator])
                expected_semantic = tree.slot_maps[slot, source_semantic]
                bad_classes: list[dict[str, Any]] = []
                for class_id in np.unique(source_id):
                    members = source_id == class_id
                    source_labels = set(map(int, source_semantic[members]))
                    target_ids = set(map(int, endpoint_id[members]))
                    target_labels = set(map(int, endpoint_semantic[members]))
                    expected_labels = set(map(int, expected_semantic[members]))
                    target_signature_labels = set()
                    for target_id in target_ids:
                        target_signature_labels.update(target_labels_by_signature[target_id])
                    good = bool(
                        len(source_labels) == 1
                        and len(target_ids) == 1
                        and len(target_labels) == 1
                        and target_labels == expected_labels
                        and target_signature_labels == expected_labels
                    )
                    if not good:
                        bad_classes.append(
                            {
                                "source_signature_id": int(class_id),
                                "source_semantic_labels": sorted(source_labels),
                                "target_signature_ids": sorted(target_ids),
                                "target_semantic_labels": sorted(target_labels),
                                "expected_semantic_labels": sorted(expected_labels),
                                "target_signature_semantic_labels": sorted(target_signature_labels),
                            }
                        )
                cells.append(
                    {
                        "L": L,
                        "H": H,
                        "generator": generator,
                        "source_class_count": int(np.unique(source_id).size),
                        "bad_class_count": len(bad_classes),
                        "bad_classes": bad_classes,
                        "exact_environment_action": bool(
                            np.array_equal(endpoint_semantic, expected_semantic)
                        ),
                        "passed": len(bad_classes) == 0,
                    }
                )
    return {
        "mathematical_map": "F_a: Q_(L,H+1) -> Q_(L+1,H)",
        "cells": cells,
        "passed": bool(all(cell["passed"] for cell in cells)),
        "same_space_closure_claimed": False,
    }


def analyze_completion_surface(
    tree: EpisodeTree,
    Lmax: int,
    Hmax: int,
    include_soft: bool = True,
) -> dict[str, Any]:
    if min(Lmax, Hmax) < 0 or Lmax + Hmax > tree.max_depth:
        raise ValueError("surface rectangle is incompatible with trajectory tree")
    signatures = intern_hard_signatures(
        tree.predictions_by_depth,
        Hmax,
        episode_id=tree.episode_id,
        episode_scope=tree.scope_token,
    )
    aggregates = recursive_future_aggregates(tree, Hmax)
    cumulative: list[dict[str, Any]] = []
    exact_history: list[dict[str, Any]] = []
    exact_future: list[dict[str, Any]] = []
    exact_both: list[dict[str, Any]] = []
    pass_mask = np.zeros((Lmax + 1, Hmax + 1), dtype=bool)
    for L in range(Lmax + 1):
        for H in range(Hmax + 1):
            main = summarize_cell(tree, signatures, aggregates, L, H)
            cumulative.append(main)
            pass_mask[L, H] = main["hard_completion_pass"]
            exact_history.append(
                summarize_cell(tree, signatures, aggregates, L, H, history_mode="exact")
            )
            exact_future.append(
                summarize_cell(tree, signatures, aggregates, L, H, future_mode="exact")
            )
            exact_both.append(
                summarize_cell(
                    tree,
                    signatures,
                    aggregates,
                    L,
                    H,
                    history_mode="exact",
                    future_mode="exact",
                )
            )
    violations = downset_violations(pass_mask)
    diagonal = diagonal_action_audit(tree, signatures, Lmax, Hmax)
    output = {
        "episode_id": tree.episode_id,
        "Lmax": Lmax,
        "Hmax": Hmax,
        "cumulative_cells": cumulative,
        "exact_history_cumulative_future_cells": exact_history,
        "cumulative_history_exact_future_cells": exact_future,
        "exact_history_exact_future_cells": exact_both,
        "cumulative_pass_mask": pass_mask.tolist(),
        "downset_violations": violations,
        "downset_passed": len(violations) == 0,
        "hard_rectangle_passed": bool(np.all(pass_mask)),
        "diagonal_action": diagonal,
    }
    if include_soft:
        centered_logits = tuple(
            logits - np.mean(logits, axis=1, keepdims=True)
            for logits in tree.logits_by_depth
        )
        output["soft_interfaces"] = compute_soft_completion_surface(
            tree.probabilities_by_depth,
            centered_logits,
            tree.semantic_by_depth,
            max_history_depth=Lmax,
            max_future_horizon=Hmax,
            label_count=N_STATES,
        )
    return output


def insert_word_at_cut(
    base_word: Sequence[int], insertion: Sequence[int], cut: int
) -> tuple[int, ...]:
    base = tuple(map(int, base_word))
    inserted = tuple(map(int, insertion))
    if not 0 <= cut <= len(base):
        raise ValueError("cut must lie between base-word symbols")
    if any(symbol not in (0, 1) for symbol in base + inserted):
        raise ValueError("words must contain only binary canonical generators")
    return base[:cut] + inserted + base[cut:]


def make_fresh_d4_episodes(checkpoint_seed: int, count: int = 8):
    if checkpoint_seed not in (0, 1) or count < 1:
        raise ValueError("registered checkpoint seed is 0 or 1 and count must be positive")
    rng = np.random.default_rng(930_000 + 1_000 * checkpoint_seed)
    return sample_batch(rng, count, 0, family="d4")


def _checkpoint_path(seed: int) -> Path:
    return ROOT / "checkpoints" / f"projective_terminal_seed{seed}.pt"


def run_registered_audit(
    preregistration: dict[str, Any],
    *,
    Lmax: int = 8,
    Hmax: int = 8,
    checkpoint_seeds: Sequence[int] = (0, 1),
    include_soft: bool = True,
    include_relator: bool = True,
    retain_relator_case_arrays: bool = False,
    execution_integrity: bool = False,
) -> dict[str, Any]:
    """Execute the frozen audit.  This is intentionally not called on import."""

    if min(Lmax, Hmax) < 0:
        raise ValueError("surface limits must be nonnegative")
    records: dict[str, Any] = {}
    checkpoint_digests: dict[str, str] = {}
    hard_gate = True
    downset_gate = True
    soft_gate = True
    diagonal_gate = True
    relator_hard_gate = True
    relator_soft_gate = True
    control_gate = True
    for seed_value in checkpoint_seeds:
        seed = int(seed_value)
        filename = f"projective_terminal_seed{seed}.pt"
        expected_digest = preregistration["checkpoints"][filename]
        checkpoint = load_checkpoint(_checkpoint_path(seed), expected_digest)
        checkpoint_digests[filename] = checkpoint.sha256
        if checkpoint.metadata.get("schema") != "komorebi.neuralese.projective_checkpoint.v1":
            raise ValueError(f"projective checkpoint schema mismatch for {filename}")
        if int(checkpoint.metadata["config"].get("seed", -1)) != seed:
            raise ValueError(f"checkpoint metadata seed mismatch for {filename}")
        batch = make_fresh_d4_episodes(seed, 8)
        episode_records: list[dict[str, Any]] = []
        for episode in range(8):
            episode_id = f"checkpoint_seed{seed}:episode{episode}"
            tree = build_episode_tree(
                checkpoint.weights,
                batch.tables[episode],
                batch.maps[episode],
                batch.canonical_to_slot[episode],
                Lmax + Hmax,
                episode_id=episode_id,
            )
            episode_record = analyze_completion_surface(
                tree, Lmax, Hmax, include_soft=include_soft
            )
            episode_record["episode_index"] = episode
            episode_record["canonical_to_slot"] = batch.canonical_to_slot[episode].tolist()
            episode_records.append(episode_record)
            hard_gate &= bool(episode_record["hard_rectangle_passed"])
            downset_gate &= bool(episode_record["downset_passed"])
            diagonal_gate &= bool(episode_record["diagonal_action"]["passed"])
            if include_soft:
                soft_gate &= bool(
                    episode_record["soft_interfaces"][
                        "both_interfaces_exact_on_cumulative_rectangle"
                    ]
                )
            del tree
        seed_record: dict[str, Any] = {
            "checkpoint_seed": seed,
            "checkpoint": filename,
            "checkpoint_sha256": checkpoint.sha256,
            "episode_seed": 930_000 + 1_000 * seed,
            "episodes": episode_records,
        }
        if include_relator:
            from relator_witness import run_relator_witness

            witness = run_relator_witness(
                checkpoint.weights,
                batch,
                seed,
                retain_case_arrays=retain_relator_case_arrays,
            )
            seed_record["relator_witness"] = witness
            relator_hard_gate &= bool(witness["gates"]["W0_relator_hard_closure"])
            relator_soft_gate &= bool(witness["gates"]["W1_relator_soft_flatness"])
            control_gate &= bool(witness["gates"]["C0_nonidentity_control"])
        records[str(seed)] = seed_record

    gates: dict[str, Any] = {
        "E0_execution_integrity": bool(execution_integrity),
        "H0_hard_rectangle": bool(hard_gate),
        "H1_downset": bool(downset_gate),
        "D0_diagonal_action": bool(diagonal_gate),
    }
    gates["S0_soft_exact_collapse"] = bool(soft_gate) if include_soft else None
    gates["W0_relator_hard_closure"] = bool(relator_hard_gate) if include_relator else None
    gates["W1_relator_soft_flatness"] = bool(relator_soft_gate) if include_relator else None
    gates["C0_nonidentity_control"] = bool(control_gate) if include_relator else None
    return {
        "schema": "komorebi.neuralese.completion_surface.results.v1",
        "version": "0.3.0",
        "status": "adaptive_developmental_followup",
        "registered_rectangle": {"Lmax": Lmax, "Hmax": Hmax},
        "checkpoint_seeds": list(map(int, checkpoint_seeds)),
        "checkpoint_digests": checkpoint_digests,
        "include_soft_interfaces": include_soft,
        "include_relator_witness": include_relator,
        "records": records,
        "gates": gates,
        "aggregation": "worst_case_conjunction_without_cross_episode_pooling",
        "claim_boundary": (
            "Hard results concern only the exact registered finite rectangle; soft "
            "interfaces and the non-exhaustive repeated-relator witness family are "
            "reported separately. No same-space stabilized quotient is claimed."
        ),
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preregistration", type=Path, default=PREREGISTRATION)
    parser.add_argument("--execution-freeze", type=Path, default=EXECUTION_FREEZE)
    parser.add_argument("--lineage-regression", type=Path, default=LINEAGE_REGRESSION)
    parser.add_argument("--output", type=Path, default=RESULTS_DIR / "COMPLETION_SURFACE_RESULTS.json")
    parser.add_argument("--Lmax", type=int, default=8)
    parser.add_argument("--Hmax", type=int, default=8)
    parser.add_argument("--checkpoint-seeds", type=int, nargs="+", default=[0, 1])
    parser.add_argument("--skip-soft", action="store_true")
    parser.add_argument("--skip-relator", action="store_true")
    parser.add_argument("--retain-relator-case-arrays", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    started = time.time()
    registered_profile = bool(
        args.preregistration.resolve() == PREREGISTRATION.resolve()
        and args.execution_freeze.resolve() == EXECUTION_FREEZE.resolve()
        and args.lineage_regression.resolve() == LINEAGE_REGRESSION.resolve()
        and args.Lmax == 8
        and args.Hmax == 8
        and list(args.checkpoint_seeds) == [0, 1]
        and not args.skip_soft
        and not args.skip_relator
        and not args.retain_relator_case_arrays
    )
    freeze_record: dict[str, Any] | None = None
    try:
        if args.output.exists():
            raise FileExistsError(f"refusing to overwrite existing output: {args.output}")
        preregistration = json.loads(args.preregistration.read_text(encoding="utf-8"))
        if registered_profile:
            # This validation precedes checkpoint loading and therefore precedes
            # every new v0.3.0 learned endpoint.
            freeze_record = validate_execution_freeze(
                args.execution_freeze, args.lineage_regression
            )
        result = run_registered_audit(
            preregistration,
            Lmax=args.Lmax,
            Hmax=args.Hmax,
            checkpoint_seeds=args.checkpoint_seeds,
            include_soft=not args.skip_soft,
            include_relator=not args.skip_relator,
            retain_relator_case_arrays=args.retain_relator_case_arrays,
            execution_integrity=registered_profile and freeze_record is not None,
        )
    except Exception as exc:
        invalid = {
            "schema": "komorebi.neuralese.completion_surface.invalid_run.v1",
            "version": "0.3.0",
            "status": "INVALID_EXECUTION_ABORTED",
            "registered_execution_profile": registered_profile,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "gates": {"E0_execution_integrity": False},
            "elapsed_seconds": time.time() - started,
            "runner_sha256": file_sha256(Path(__file__).resolve()),
            "preregistration_sha256": file_sha256(args.preregistration),
        }
        invalid_output = (
            args.output
            if not args.output.exists()
            else args.output.with_name(
                f"{args.output.stem}.INVALID_ATTEMPT_{time.time_ns()}{args.output.suffix}"
            )
        )
        atomic_json(invalid_output, invalid)
        print(
            json.dumps(
                {"output": str(invalid_output), "status": invalid["status"]},
                sort_keys=True,
            )
        )
        return 2
    result["registered_execution_profile"] = registered_profile
    result["execution_freeze"] = freeze_record
    if not registered_profile:
        result["status"] = "unregistered_developmental_profile"
        result["gates"]["E0_execution_integrity"] = False
    result["execution"] = {
        "elapsed_seconds": time.time() - started,
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "runner_sha256": file_sha256(Path(__file__).resolve()),
        "test_sha256": (
            file_sha256(ROOT / "test_completion_surface.py")
            if (ROOT / "test_completion_surface.py").exists()
            else None
        ),
        "preregistration_sha256": file_sha256(args.preregistration),
    }
    atomic_json(args.output, result)
    print(json.dumps({"output": str(args.output), "gates": result["gates"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
