#!/usr/bin/env python3
"""Shared exact suffix and decoder-facet engine for Neuralese v0.3.1.

Author: Komorebi P.

The module is checkpoint agnostic.  It accepts explicit NumPy arrays, executes
the declared per-generator projective recurrence, and returns compact summaries
plus optional in-memory decision matrices for registered contrasts.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from itertools import product
from typing import Any, Iterable, Sequence

import numpy as np

from holonomy_spectroscopy import (
    DEFAULT_MINIMUM_NORM,
    NumericalRayError,
    normalize_positive_ray,
    positive_rescaled_word_product,
    semantic_word_action,
)


N_STATES = 8
N_OPERATORS = 2
DEFAULT_HORIZON = 8
MINIMUM_FACET_NORM = 1e-14


def _permutation_rows(maps: np.ndarray) -> bool:
    return bool(
        maps.shape == (N_OPERATORS, N_STATES)
        and all(np.array_equal(np.sort(row), np.arange(N_STATES)) for row in maps)
    )


def cumulative_suffix_count(horizon: int) -> int:
    if isinstance(horizon, bool) or not isinstance(horizon, (int, np.integer)):
        raise ValueError("horizon must be an integer")
    if int(horizon) < 0:
        raise ValueError("horizon must be nonnegative")
    return 2 ** (int(horizon) + 1) - 1


def word_from_index(length: int, index: int) -> tuple[int, ...]:
    if length < 0 or index < 0 or index >= 2**length:
        raise ValueError("word index is outside the binary shell")
    return tuple((index >> shift) & 1 for shift in range(length - 1, -1, -1))


@dataclass(frozen=True)
class SuffixFacetBank:
    maximum_horizon: int
    words: tuple[tuple[int, ...], ...]
    depths: np.ndarray
    indices_within_depth: np.ndarray
    products: np.ndarray
    semantic_actions: np.ndarray
    competitor_labels: np.ndarray
    unit_pulled_back_facets: np.ndarray
    minimum_pulled_back_facet_norm: float


@dataclass(frozen=True)
class AuditResult:
    summary: dict[str, Any]
    predictions: np.ndarray
    targets: np.ndarray
    strict: np.ndarray
    target_margins: np.ndarray
    angular_clearances: np.ndarray
    angular_competitors: np.ndarray
    margin_competitors: np.ndarray
    reveals: np.ndarray | None


def build_suffix_facet_bank(
    codes: np.ndarray,
    semantic_maps: np.ndarray,
    decoder: np.ndarray,
    maximum_horizon: int = DEFAULT_HORIZON,
) -> SuffixFacetBank:
    operators = np.asarray(codes, dtype=np.float64)
    maps_raw = np.asarray(semantic_maps)
    readout = np.asarray(decoder, dtype=np.float64)
    if operators.shape != (N_OPERATORS, N_STATES, N_STATES):
        raise ValueError("codes must have shape (2,8,8)")
    if not np.issubdtype(maps_raw.dtype, np.integer):
        raise ValueError("semantic maps must have an integer dtype")
    maps = maps_raw.astype(np.int64, copy=False)
    if not _permutation_rows(maps):
        raise ValueError("each semantic map must be an eight-state permutation")
    if readout.shape != (N_STATES, N_STATES):
        raise ValueError("decoder must have shape (8,8)")
    if not np.isfinite(operators).all() or not np.isfinite(readout).all():
        raise NumericalRayError("suffix-bank input is nonfinite")
    if (
        isinstance(maximum_horizon, bool)
        or not isinstance(maximum_horizon, (int, np.integer))
        or int(maximum_horizon) < 0
    ):
        raise ValueError("maximum_horizon must be a nonnegative integer")
    maximum_horizon = int(maximum_horizon)

    words: list[tuple[int, ...]] = []
    depths: list[int] = []
    indices: list[int] = []
    products: list[np.ndarray] = []
    actions: list[np.ndarray] = []
    for depth in range(maximum_horizon + 1):
        for index, word in enumerate(product(range(N_OPERATORS), repeat=depth)):
            canonical_word = tuple(map(int, word))
            words.append(canonical_word)
            depths.append(depth)
            indices.append(index)
            products.append(positive_rescaled_word_product(operators, canonical_word))
            actions.append(
                semantic_word_action(
                    maps, np.arange(N_STATES, dtype=np.int64), canonical_word
                )
            )

    product_array = np.stack(products)
    action_array = np.stack(actions).astype(np.int64, copy=False)
    competitors = np.empty((len(words), N_STATES, N_STATES - 1), dtype=np.int64)
    unit_facets = np.empty(
        (len(words), N_STATES, N_STATES - 1, N_STATES), dtype=np.float64
    )
    minimum_facet_norm = float("inf")
    for suffix_index, matrix in enumerate(product_array):
        for initial_semantic in range(N_STATES):
            target = int(action_array[suffix_index, initial_semantic])
            other = np.asarray(
                [label for label in range(N_STATES) if label != target],
                dtype=np.int64,
            )
            facets = readout[target][None, :] - readout[other]
            pulled_back = np.einsum("ji,kj->ki", matrix, facets)
            norms = np.linalg.norm(pulled_back, axis=1)
            if (
                not np.isfinite(norms).all()
                or np.any(norms <= MINIMUM_FACET_NORM)
            ):
                raise NumericalRayError(
                    "a pulled-back decoder facet vanished or became nonfinite"
                )
            competitors[suffix_index, initial_semantic] = other
            unit_facets[suffix_index, initial_semantic] = pulled_back / norms[:, None]
            minimum_facet_norm = min(minimum_facet_norm, float(np.min(norms)))

    return SuffixFacetBank(
        maximum_horizon=maximum_horizon,
        words=tuple(words),
        depths=np.asarray(depths, dtype=np.int64),
        indices_within_depth=np.asarray(indices, dtype=np.int64),
        products=product_array,
        semantic_actions=action_array,
        competitor_labels=competitors,
        unit_pulled_back_facets=unit_facets,
        minimum_pulled_back_facet_norm=minimum_facet_norm,
    )


def _trajectory_decisions(
    codes: np.ndarray,
    semantic_maps: np.ndarray,
    decoder: np.ndarray,
    states: np.ndarray,
    semantic: np.ndarray,
    maximum_horizon: int,
    minimum_norm: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    operators = np.asarray(codes, dtype=np.float64)
    maps = np.asarray(semantic_maps, dtype=np.int64)
    readout = np.asarray(decoder, dtype=np.float64)
    initial = normalize_positive_ray(states, minimum_norm)
    if initial.ndim == 1:
        initial = initial[None, :]
    labels = np.asarray(semantic)
    if not np.issubdtype(labels.dtype, np.integer):
        raise ValueError("semantic labels must have an integer dtype")
    labels = labels.astype(np.int64, copy=False)
    if labels.ndim != 1 or initial.shape != (labels.size, N_STATES):
        raise ValueError("states and semantic labels have incompatible shapes")
    if np.any(labels < 0) or np.any(labels >= N_STATES):
        raise ValueError("semantic label is outside the eight-state domain")

    count = cumulative_suffix_count(maximum_horizon)
    predictions = np.empty((labels.size, count), dtype=np.uint8)
    targets = np.empty((labels.size, count), dtype=np.uint8)
    margins = np.empty((labels.size, count), dtype=np.float64)
    margin_competitors = np.empty((labels.size, count), dtype=np.uint8)
    current = initial[:, None, :]
    current_labels = labels[:, None]
    offset = 0
    for depth in range(maximum_horizon + 1):
        width = 2**depth
        logits = np.einsum("nwd,kd->nwk", current, readout)
        prediction = np.argmax(logits, axis=-1).astype(np.uint8)
        selected = np.take_along_axis(logits, current_labels[..., None], axis=-1)[..., 0]
        masked = logits.copy()
        np.put_along_axis(masked, current_labels[..., None], -np.inf, axis=-1)
        competitor = np.argmax(masked, axis=-1).astype(np.uint8)
        margin = selected - np.max(masked, axis=-1)
        if not np.isfinite(margin).all():
            raise NumericalRayError("decoder produced a nonfinite target margin")
        section = slice(offset, offset + width)
        predictions[:, section] = prediction
        targets[:, section] = current_labels.astype(np.uint8)
        margins[:, section] = margin
        margin_competitors[:, section] = competitor
        offset += width
        if depth == maximum_horizon:
            break
        expanded = np.einsum("oij,nwj->nwoi", operators, current)
        current = normalize_positive_ray(
            expanded.reshape(labels.size, width * N_OPERATORS, N_STATES),
            minimum_norm,
        )
        current_labels = np.stack(
            [maps[operator, current_labels] for operator in range(N_OPERATORS)],
            axis=2,
        ).reshape(labels.size, width * N_OPERATORS)
    if offset != count:
        raise ArithmeticError("suffix trajectory count mismatch")
    return predictions, targets, margins, margin_competitors


def _angular_clearance_matrices(
    bank: SuffixFacetBank,
    states: np.ndarray,
    semantic: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    initial = normalize_positive_ray(states)
    if initial.ndim == 1:
        initial = initial[None, :]
    labels = np.asarray(semantic, dtype=np.int64)
    count = len(bank.words)
    clearances = np.empty((labels.size, count), dtype=np.float64)
    active_competitors = np.empty((labels.size, count), dtype=np.uint8)
    case_chunk = 256
    for depth in range(bank.maximum_horizon + 1):
        start = cumulative_suffix_count(depth - 1) if depth else 0
        width = 2**depth
        stop = start + width
        suffix_indices = np.arange(start, stop)[:, None]
        for case_start in range(0, labels.size, case_chunk):
            case_stop = min(labels.size, case_start + case_chunk)
            label_chunk = labels[case_start:case_stop]
            state_chunk = initial[case_start:case_stop]
            selected_facets = bank.unit_pulled_back_facets[
                suffix_indices, label_chunk[None, :], :, :
            ]
            values = np.einsum("wnkd,nd->wnk", selected_facets, state_chunk)
            minima_index = np.argmin(values, axis=2)
            minimum_values = np.take_along_axis(
                values, minima_index[..., None], axis=2
            )[..., 0]
            selected_competitors = bank.competitor_labels[
                suffix_indices, label_chunk[None, :], :
            ]
            competitor = np.take_along_axis(
                selected_competitors, minima_index[..., None], axis=2
            )[..., 0]
            clearances[case_start:case_stop, start:stop] = minimum_values.T
            active_competitors[case_start:case_stop, start:stop] = (
                competitor.T.astype(np.uint8)
            )
    if not np.isfinite(clearances).all():
        raise NumericalRayError("angular clearance became nonfinite")
    return clearances, active_competitors


def recursive_suffix_consistency(
    direct_full_word_hard_membership: np.ndarray,
    codes: np.ndarray,
    semantic_maps: np.ndarray,
    decoder: np.ndarray,
    states: np.ndarray,
    semantic: np.ndarray,
    maximum_horizon: int,
    minimum_norm: float = DEFAULT_MINIMUM_NORM,
) -> dict[str, Any]:
    """Check the finite-cone recursion by an independent one-step traversal.

    ``direct_full_word_hard_membership`` is the direct audit: one Boolean for
    every complete suffix word, obtained from the pulled-back decoder facets.
    The recursive side is deliberately rebuilt here without those facets or
    the frozen word products.  It advances every state by exactly one learned
    generator, tests the decoder cone at each descendant, and folds the binary
    suffix tree from its leaves back to the root via

    ``safe(node, H) = hard(node) and safe(node R, H-1) and safe(node F, H-1)``.

    Agreement is required both word by word and for the recursively folded
    root membership.  The wordwise check prevents coincident root failures
    from hiding an ordering or propagation mismatch.
    """
    direct = np.asarray(direct_full_word_hard_membership)
    if direct.dtype != np.bool_:
        raise ValueError("direct hard-membership matrix must have Boolean dtype")
    if (
        isinstance(maximum_horizon, bool)
        or not isinstance(maximum_horizon, (int, np.integer))
        or int(maximum_horizon) < 0
    ):
        raise ValueError("maximum_horizon must be a nonnegative integer")
    maximum_horizon = int(maximum_horizon)
    expected = cumulative_suffix_count(maximum_horizon)
    if direct.ndim != 2 or direct.shape[1] != expected:
        raise ValueError("direct hard-membership matrix has incompatible shape")

    operators = np.asarray(codes, dtype=np.float64)
    maps_raw = np.asarray(semantic_maps)
    readout = np.asarray(decoder, dtype=np.float64)
    if operators.shape != (N_OPERATORS, N_STATES, N_STATES):
        raise ValueError("codes must have shape (2,8,8)")
    if not np.issubdtype(maps_raw.dtype, np.integer):
        raise ValueError("semantic maps must have an integer dtype")
    maps = maps_raw.astype(np.int64, copy=False)
    if not _permutation_rows(maps):
        raise ValueError("each semantic map must be an eight-state permutation")
    if readout.shape != (N_STATES, N_STATES):
        raise ValueError("decoder must have shape (8,8)")
    if not np.isfinite(operators).all() or not np.isfinite(readout).all():
        raise NumericalRayError("recursive suffix input is nonfinite")

    current = normalize_positive_ray(states, minimum_norm)
    if current.ndim == 1:
        current = current[None, :]
    labels_raw = np.asarray(semantic)
    if not np.issubdtype(labels_raw.dtype, np.integer):
        raise ValueError("semantic labels must have an integer dtype")
    current_labels = labels_raw.astype(np.int64, copy=False)
    if current_labels.ndim != 1 or current.shape != (
        current_labels.size,
        N_STATES,
    ):
        raise ValueError("states and semantic labels have incompatible shapes")
    if current_labels.size != direct.shape[0]:
        raise ValueError("direct hard membership and state counts disagree")
    if np.any(current_labels < 0) or np.any(current_labels >= N_STATES):
        raise ValueError("semantic label is outside the eight-state domain")
    current = current[:, None, :]
    current_labels = current_labels[:, None]

    # Rebuild local hard membership through an independent one-generator tree
    # traversal.  This path intentionally does not read the suffix bank,
    # pulled-back facets, or precomputed full-word products.
    local_shells: list[np.ndarray] = []
    for depth in range(maximum_horizon + 1):
        logits = np.einsum("nwd,kd->nwk", current, readout)
        selected = np.take_along_axis(
            logits, current_labels[..., None], axis=-1
        )[..., 0]
        masked = logits.copy()
        np.put_along_axis(masked, current_labels[..., None], -np.inf, axis=-1)
        margins = selected - np.max(masked, axis=-1)
        if not np.isfinite(margins).all():
            raise NumericalRayError("decoder produced a nonfinite target margin")
        predictions = np.argmax(logits, axis=-1)
        shell_hard = (predictions == current_labels) & (margins > 0.0)
        expected_width = 2**depth
        if shell_hard.shape != (direct.shape[0], expected_width):
            raise ArithmeticError("recursive suffix shell width changed")
        local_shells.append(shell_hard)
        if depth == maximum_horizon:
            break
        expanded = np.einsum("oij,nwj->nwoi", operators, current)
        current = normalize_positive_ray(
            expanded.reshape(
                direct.shape[0], expected_width * N_OPERATORS, N_STATES
            ),
            minimum_norm,
        )
        current_labels = np.stack(
            [maps[operator, current_labels] for operator in range(N_OPERATORS)],
            axis=2,
        ).reshape(direct.shape[0], expected_width * N_OPERATORS)

    one_step_word_membership = np.concatenate(local_shells, axis=1)
    if one_step_word_membership.shape != direct.shape:
        raise ArithmeticError("recursive suffix tree count changed")

    records: list[dict[str, Any]] = []
    all_equal = True
    total_word_mismatches = 0
    total_root_mismatches = 0
    for horizon in range(maximum_horizon + 1):
        count = cumulative_suffix_count(horizon)
        direct_words = direct[:, :count]
        one_step_words = one_step_word_membership[:, :count]
        word_mismatch_count = int(np.sum(direct_words != one_step_words))
        word_equal = bool(word_mismatch_count == 0)
        direct_safe = np.all(direct_words, axis=1)

        recursive_safe = local_shells[horizon].copy()
        for depth in range(horizon - 1, -1, -1):
            recursive_safe = local_shells[depth] & recursive_safe.reshape(
                direct.shape[0], -1, N_OPERATORS
            ).all(axis=2)
        recursive_safe = recursive_safe[:, 0]
        root_mismatch_count = int(np.sum(direct_safe != recursive_safe))
        safe_equal = bool(root_mismatch_count == 0)
        all_equal = all_equal and word_equal and safe_equal
        total_word_mismatches += word_mismatch_count
        total_root_mismatches += root_mismatch_count
        records.append(
            {
                "H": horizon,
                "direct_full_word_and_one_step_membership_equal": word_equal,
                "word_membership_comparison_count": int(direct_words.size),
                "word_membership_mismatch_count": word_mismatch_count,
                "direct_and_recursive_safe_equal": safe_equal,
                "root_safe_comparison_count": int(direct.shape[0]),
                "root_safe_mismatch_count": root_mismatch_count,
                "direct_safe_case_count": int(np.sum(direct_safe)),
                "recursive_safe_case_count": int(np.sum(recursive_safe)),
            }
        )
    return {
        "passed": bool(all_equal),
        "method": (
            "direct pulled-back full-word hard membership versus fresh "
            "one-generator descendant traversal and bottom-up Boolean recursion"
        ),
        "total_word_membership_mismatch_count_across_horizons": int(
            total_word_mismatches
        ),
        "total_root_safe_mismatch_count_across_horizons": int(
            total_root_mismatches
        ),
        "horizons": records,
    }


def _event_histogram(mask: np.ndarray, depths: np.ndarray) -> tuple[dict[str, int], np.ndarray]:
    first = np.full(mask.shape[0], -1, dtype=np.int64)
    for case in range(mask.shape[0]):
        locations = np.flatnonzero(mask[case])
        if locations.size:
            first[case] = int(locations[0])
    histogram = {
        str(depth): int(np.sum((first >= 0) & (depths[first.clip(min=0)] == depth)))
        for depth in range(int(np.max(depths)) + 1)
    }
    histogram["none"] = int(np.sum(first < 0))
    return histogram, first


def _locator(case_locators: Sequence[dict[str, Any]] | None, case: int) -> dict[str, Any]:
    if case_locators is None:
        return {"case_index": int(case)}
    if len(case_locators) <= case:
        raise ValueError("case locator count is smaller than state count")
    return {"case_index": int(case), **dict(case_locators[case])}


def _decision_witness(
    bank: SuffixFacetBank,
    matrix: np.ndarray,
    result: "AuditResult | None",
    case_locators: Sequence[dict[str, Any]] | None,
    kind: str,
    *,
    predictions: np.ndarray,
    targets: np.ndarray,
    margins: np.ndarray,
    clearances: np.ndarray,
    angular_competitors: np.ndarray,
    margin_competitors: np.ndarray,
) -> dict[str, Any]:
    del result
    case, suffix = np.unravel_index(int(np.argmin(matrix)), matrix.shape)
    record = {
        **_locator(case_locators, int(case)),
        "suffix_global_index": int(suffix),
        "suffix_depth": int(bank.depths[suffix]),
        "suffix_index_within_depth": int(bank.indices_within_depth[suffix]),
        "suffix": list(bank.words[suffix]),
        "prediction": int(predictions[case, suffix]),
        "target": int(targets[case, suffix]),
        "target_margin": float(margins[case, suffix]),
        "minimum_angular_clearance": float(clearances[case, suffix]),
        "margin_active_competitor": int(margin_competitors[case, suffix]),
        "minimum_angular_competitor": int(angular_competitors[case, suffix]),
    }
    record["witness_kind"] = kind
    if kind == "angular_clearance":
        record["signed_spherical_boundary_distance_radians"] = float(
            np.arcsin(np.clip(clearances[case, suffix], -1.0, 1.0))
        )
    return record


def audit_states(
    bank: SuffixFacetBank,
    codes: np.ndarray,
    semantic_maps: np.ndarray,
    decoder: np.ndarray,
    states: np.ndarray,
    semantic: np.ndarray,
    *,
    baseline_states: np.ndarray | None = None,
    case_locators: Sequence[dict[str, Any]] | None = None,
    minimum_norm: float = DEFAULT_MINIMUM_NORM,
) -> AuditResult:
    initial = normalize_positive_ray(states, minimum_norm)
    if initial.ndim == 1:
        initial = initial[None, :]
    labels_raw = np.asarray(semantic)
    if not np.issubdtype(labels_raw.dtype, np.integer):
        raise ValueError("semantic labels must have an integer dtype")
    labels = labels_raw.astype(np.int64, copy=False)
    if labels.ndim != 1 or initial.shape != (labels.size, N_STATES):
        raise ValueError("states and semantic labels have incompatible shapes")
    if case_locators is not None and len(case_locators) != labels.size:
        raise ValueError("case locator count does not match the state count")

    if baseline_states is None:
        combined = initial
        combined_labels = labels
    else:
        baseline = normalize_positive_ray(baseline_states, minimum_norm)
        if baseline.shape != initial.shape:
            raise ValueError("baseline states must match analyzed states")
        combined = np.concatenate((initial, baseline), axis=0)
        combined_labels = np.concatenate((labels, labels), axis=0)

    prediction_all, target_all, margin_all, margin_competitor_all = _trajectory_decisions(
        codes,
        semantic_maps,
        decoder,
        combined,
        combined_labels,
        bank.maximum_horizon,
        minimum_norm,
    )
    case_count = labels.size
    predictions = prediction_all[:case_count]
    targets = target_all[:case_count]
    margins = margin_all[:case_count]
    margin_competitors = margin_competitor_all[:case_count]
    expected_targets = bank.semantic_actions[:, labels].T.astype(np.uint8)
    if not np.array_equal(targets, expected_targets):
        raise ArithmeticError("stepwise and frozen suffix semantics disagree")
    clearances, angular_competitors = _angular_clearance_matrices(bank, initial, labels)
    strict = (predictions == targets) & (margins > 0.0) & (clearances > 0.0)
    if not np.array_equal(margins > 0.0, clearances > 0.0):
        raise ArithmeticError("target-margin and pulled-back-facet signs disagree")

    reveals = None
    if baseline_states is not None:
        baseline_predictions = prediction_all[case_count:]
        baseline_targets = target_all[case_count:]
        if not np.array_equal(baseline_targets, targets):
            raise ArithmeticError("baseline and analyzed suffix semantics disagree")
        reveals = predictions != baseline_predictions

    failure_histogram, first_failure = _event_histogram(~strict, bank.depths)
    if reveals is None:
        reveal_histogram = None
        first_reveal = np.full(case_count, -1, dtype=np.int64)
    else:
        reveal_histogram, first_reveal = _event_histogram(reveals, bank.depths)
    recursion = recursive_suffix_consistency(
        clearances > 0.0,
        codes,
        semantic_maps,
        decoder,
        initial,
        labels,
        bank.maximum_horizon,
        minimum_norm,
    )

    shell_records: list[dict[str, Any]] = []
    cumulative_records: list[dict[str, Any]] = []
    for horizon in range(bank.maximum_horizon + 1):
        shell_start = cumulative_suffix_count(horizon - 1) if horizon else 0
        shell_stop = shell_start + 2**horizon
        cumulative_stop = cumulative_suffix_count(horizon)
        shell_records.append(
            {
                "H": horizon,
                "suffix_count": 2**horizon,
                "decision_count": int(case_count * 2**horizon),
                "strict_correct_count": int(np.sum(strict[:, shell_start:shell_stop])),
                "minimum_target_margin": float(np.min(margins[:, shell_start:shell_stop])),
                "minimum_angular_clearance": float(
                    np.min(clearances[:, shell_start:shell_stop])
                ),
            }
        )
        cumulative_strict = strict[:, :cumulative_stop]
        cumulative_clearance = clearances[:, :cumulative_stop]
        cumulative_records.append(
            {
                "H": horizon,
                "suffix_count": cumulative_stop,
                "decision_count": int(case_count * cumulative_stop),
                "strict_correct_count": int(np.sum(cumulative_strict)),
                "safe_case_count": int(np.sum(np.all(cumulative_strict, axis=1))),
                "minimum_target_margin": float(np.min(margins[:, :cumulative_stop])),
                "minimum_angular_clearance": float(np.min(cumulative_clearance)),
                "p01_case_minimum_angular_clearance": float(
                    np.quantile(np.min(cumulative_clearance, axis=1), 0.01)
                ),
                "median_case_minimum_angular_clearance": float(
                    np.median(np.min(cumulative_clearance, axis=1))
                ),
            }
        )

    angular_witness = _decision_witness(
        bank,
        clearances,
        None,
        case_locators,
        "angular_clearance",
        predictions=predictions,
        targets=targets,
        margins=margins,
        clearances=clearances,
        angular_competitors=angular_competitors,
        margin_competitors=margin_competitors,
    )
    margin_witness = _decision_witness(
        bank,
        margins,
        None,
        case_locators,
        "target_margin",
        predictions=predictions,
        targets=targets,
        margins=margins,
        clearances=clearances,
        angular_competitors=angular_competitors,
        margin_competitors=margin_competitors,
    )
    summary = {
        "case_count": int(case_count),
        "maximum_suffix_horizon": bank.maximum_horizon,
        "suffix_count_per_case": len(bank.words),
        "decision_count": int(strict.size),
        "strict_correct_count": int(np.sum(strict)),
        "strict_error_count": int(np.sum(~strict)),
        "all_cases_survive": bool(np.all(strict)),
        "failure_case_count": int(np.sum(first_failure >= 0)),
        "first_failure_histogram": failure_histogram,
        "reveal_case_count": (
            None if reveals is None else int(np.sum(first_reveal >= 0))
        ),
        "first_reveal_histogram": reveal_histogram,
        "minimum_target_margin": float(np.min(margins)),
        "minimum_angular_clearance": float(np.min(clearances)),
        "robust_clearance_above_1e_minus_10": bool(np.min(clearances) > 1e-10),
        "minimum_target_margin_witness": margin_witness,
        "minimum_angular_clearance_witness": angular_witness,
        "prediction_sha256": hashlib.sha256(predictions.tobytes(order="C")).hexdigest(),
        "strict_mask_sha256": hashlib.sha256(strict.tobytes(order="C")).hexdigest(),
        "recursive_suffix_consistency": recursion,
        "shells": shell_records,
        "cumulative_horizons": cumulative_records,
    }
    return AuditResult(
        summary=summary,
        predictions=predictions,
        targets=targets,
        strict=strict,
        target_margins=margins,
        angular_clearances=clearances,
        angular_competitors=angular_competitors,
        margin_competitors=margin_competitors,
        reveals=reveals,
    )


def summarize_audit_horizon(
    audit: AuditResult,
    bank: SuffixFacetBank,
    horizon: int,
    case_locators: Sequence[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    if horizon < 0 or horizon > bank.maximum_horizon:
        raise ValueError("requested horizon is outside the suffix bank")
    stop = cumulative_suffix_count(horizon)
    strict = audit.strict[:, :stop]
    margin = audit.target_margins[:, :stop]
    clearance = audit.angular_clearances[:, :stop]
    prediction = audit.predictions[:, :stop]
    target = audit.targets[:, :stop]
    angular_competitor = audit.angular_competitors[:, :stop]
    margin_competitor = audit.margin_competitors[:, :stop]
    angular_witness = _decision_witness(
        bank,
        clearance,
        None,
        case_locators,
        "angular_clearance",
        predictions=prediction,
        targets=target,
        margins=margin,
        clearances=clearance,
        angular_competitors=angular_competitor,
        margin_competitors=margin_competitor,
    )
    return {
        "H": int(horizon),
        "case_count": int(strict.shape[0]),
        "suffix_count_per_case": int(stop),
        "decision_count": int(strict.size),
        "strict_correct_count": int(np.sum(strict)),
        "safe_case_count": int(np.sum(np.all(strict, axis=1))),
        "minimum_target_margin": float(np.min(margin)),
        "minimum_angular_clearance": float(np.min(clearance)),
        "p01_case_minimum_angular_clearance": float(
            np.quantile(np.min(clearance, axis=1), 0.01)
        ),
        "p05_case_minimum_angular_clearance": float(
            np.quantile(np.min(clearance, axis=1), 0.05)
        ),
        "median_case_minimum_angular_clearance": float(
            np.median(np.min(clearance, axis=1))
        ),
        "p95_case_minimum_angular_clearance": float(
            np.quantile(np.min(clearance, axis=1), 0.95)
        ),
        "minimum_angular_clearance_witness": angular_witness,
    }


def build_history_levels(
    codes: np.ndarray,
    semantic_maps: np.ndarray,
    anchors: np.ndarray,
    maximum_depth: int,
    minimum_norm: float = DEFAULT_MINIMUM_NORM,
) -> tuple[tuple[np.ndarray, ...], tuple[np.ndarray, ...]]:
    operators = np.asarray(codes, dtype=np.float64)
    maps = np.asarray(semantic_maps, dtype=np.int64)
    current = np.asarray(anchors, dtype=np.float64)
    if current.shape != (N_STATES, N_STATES):
        raise ValueError("anchors must have shape (8,8)")
    normalize_positive_ray(current, minimum_norm)
    labels = np.arange(N_STATES, dtype=np.int64)
    state_levels = [current.copy()]
    semantic_levels = [labels.copy()]
    for depth in range(1, maximum_depth + 1):
        expanded = np.einsum("oij,nj->noi", operators, current)
        current = normalize_positive_ray(
            expanded.reshape(-1, N_STATES), minimum_norm
        )
        labels = np.stack(
            [maps[operator, labels] for operator in range(N_OPERATORS)], axis=1
        ).reshape(-1)
        expected = N_STATES * 2**depth
        if current.shape != (expected, N_STATES) or labels.shape != (expected,):
            raise ArithmeticError("history level count mismatch")
        state_levels.append(current)
        semantic_levels.append(labels)
    return tuple(state_levels), tuple(semantic_levels)


def history_case_locators(depth: int) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for start in range(N_STATES):
        for word_index in range(2**depth):
            records.append(
                {
                    "start": start,
                    "history_depth": depth,
                    "history_index": word_index,
                    "history": list(word_from_index(depth, word_index)),
                }
            )
    return records


__all__ = [
    "AuditResult",
    "DEFAULT_HORIZON",
    "MINIMUM_FACET_NORM",
    "SuffixFacetBank",
    "audit_states",
    "build_history_levels",
    "build_suffix_facet_bank",
    "cumulative_suffix_count",
    "history_case_locators",
    "recursive_suffix_consistency",
    "summarize_audit_horizon",
    "word_from_index",
]
