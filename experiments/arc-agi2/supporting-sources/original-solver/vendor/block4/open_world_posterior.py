from __future__ import annotations

"""Open-world posterior calibration and diversity-aware attempt ordering.

The module is deliberately independent of scikit-learn.  It fits finite
L2/Gaussian-prior logistic models by damped Newton iteration, stores a Laplace
covariance certificate, and applies an explicit uncovered-mechanism mass:

    p_unknown = 1 - p_coverage.

The currently validated ARC integration preserves the exact two-attempt set and
changes only presentation order.  A generic selector is also provided for future
candidate pools larger than two.
"""

from collections import Counter
from dataclasses import asdict, dataclass
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np

from halfturn_completion import exact, freeze

ROUTES = (
    "identity_like", "recolor", "geometry", "crop_extract", "expand", "compress",
    "draw_add", "erase_remove", "translate", "panel", "periodic",
    "object_relational", "mixed",
)
ATLASES = ("spatial", "color", "fourier", "haar", "polyphase2", "polyphase3", "polyphase4", "object")
RESOLUTIONS = ("macro", "meso", "micro")
FAMILY_GROUPS = (
    "block2", "halfturn", "fallback", "program", "signal", "struct", "causal",
    "graph", "residual", "learned", "other",
)
LAMBDA_GRID = (0.03, 0.1, 0.3, 1.0, 3.0, 10.0, 30.0)
SWAP_THRESHOLD = 0.85
COVERAGE_CAP_NO_EXACT_FIT = 0.20


def _json_float(value: Any, default: float = 0.0) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return float(default)
    return result if math.isfinite(result) else float(default)


def _entropy(mapping: Mapping[str, Any] | None) -> float:
    values = np.asarray([max(0.0, _json_float(v)) for v in (mapping or {}).values()], dtype=np.float64)
    total = float(values.sum())
    if total <= 0.0:
        return 0.0
    values /= total
    return float(-(values * np.log(np.clip(values, 1e-15, 1.0))).sum())


def _family_group(family: str | None) -> str:
    value = str(family or "").lower()
    if value.startswith("discrete_"):
        return "block2"
    if value.startswith("masked_half_turn") or value.startswith("halfturn_"):
        return "halfturn"
    for group in FAMILY_GROUPS:
        if group in {"block2", "halfturn", "other"}:
            continue
        if value == group or value.startswith(group + "_"):
            return group
    return "other"


def _modal_output_shape(task: Mapping[str, Any]) -> tuple[tuple[int, int], float]:
    shapes = [tuple(int(v) for v in np.asarray(pair["output"]).shape) for pair in task["train"]]
    modal, count = Counter(shapes).most_common(1)[0]
    return modal, count / len(shapes)


def _pair_diversity(left: Any, right: Any) -> tuple[float, float, float]:
    a, b = np.asarray(left), np.asarray(right)
    if a.shape != b.shape:
        ratio = min(a.size, b.size) / max(1, max(a.size, b.size))
        return min(1.0, 0.65 + 0.35 * (1.0 - ratio)), 1.0, 0.0
    hamming = float(np.mean(a != b))
    return hamming, 0.0, hamming


def _group_fold(task_id: str, *, salt: str, folds: int) -> int:
    digest = hashlib.sha256(f"{salt}|{task_id}".encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % folds


@dataclass(frozen=True)
class AttemptRecord:
    task_id: str
    test_index: int
    task_features: dict[str, float]
    attempt_features: tuple[dict[str, float], dict[str, float]]
    attempts: tuple[Any, Any]
    correct: tuple[bool, bool]
    coverage: bool
    diversity: float
    shape_difference: float
    hamming_difference: float
    no_exact_fit_or_promotion: bool


@dataclass
class MatrixBundle:
    records: list[AttemptRecord]
    attempt_X: np.ndarray
    attempt_y: np.ndarray
    attempt_task_ids: np.ndarray
    attempt_feature_names: list[str]
    attempt_keep: np.ndarray
    coverage_X: np.ndarray
    coverage_y: np.ndarray
    coverage_task_ids: np.ndarray
    coverage_feature_names: list[str]
    coverage_keep: np.ndarray
    pair_X: np.ndarray
    pair_y: np.ndarray
    pair_feature_names: list[str]
    pair_keep: np.ndarray
    attempt1_y: np.ndarray
    attempt2_y: np.ndarray


class FeatureFactory:
    def __init__(
        self,
        challenges: Mapping[str, Any],
        diagnostics: Mapping[str, Any],
        block2_promotions: Sequence[Mapping[str, Any]],
        halfturn_ledger: Sequence[Mapping[str, Any]],
    ) -> None:
        self.challenges = challenges
        self.diagnostics = diagnostics.get("tasks", diagnostics)
        self.block2_promotions = {
            (str(row["task_id"]), int(row["test_index"])): dict(row)
            for row in block2_promotions
            if row.get("promoted")
        }
        self.halfturn_promotions: dict[tuple[str, int], dict[str, Any]] = {}
        for row in halfturn_ledger:
            task_id = str(row["task_id"])
            for output in row.get("outputs", []):
                if output.get("candidate_exact") or output.get("promoted"):
                    self.halfturn_promotions[(task_id, int(output["test_index"]))] = dict(row)

    def _selected_meta(self, task_id: str, test_index: int, attempt_index: int) -> dict[str, Any]:
        task_diag = self.diagnostics.get(task_id, {})
        selected = task_diag.get("selected_attempts", task_diag.get("baseline_selected_attempts", [])) or []
        metadata: dict[str, Any] = {}
        if test_index < len(selected) and isinstance(selected[test_index], list) and attempt_index < len(selected[test_index]):
            candidate = selected[test_index][attempt_index]
            if isinstance(candidate, Mapping):
                metadata = dict(candidate)

        key = (task_id, test_index)
        if attempt_index == 1 and key in self.block2_promotions:
            promotion = self.block2_promotions[key]
            family = str(promotion.get("family", "discrete_unknown"))
            metadata = {
                "probability": 0.0,
                "best_candidate_probability": 1.0,
                "exact_fit_probability": 1.0,
                "exact_fit_candidate_count": 1,
                "families": [family],
                "names": [family],
                "channel_probabilities": {"base": 0.0, "structural": 1.0},
                "selection_lane": "block2_certified",
            }
        if attempt_index == 1 and key in self.halfturn_promotions:
            metadata = {
                "probability": 0.0,
                "best_candidate_probability": 1.0,
                "exact_fit_probability": 1.0,
                "exact_fit_candidate_count": 1,
                "families": ["masked_half_turn_completion"],
                "names": ["foreground_bbox_rot180_fill_background_preserve_original"],
                "channel_probabilities": {"base": 0.0, "structural": 1.0},
                "selection_lane": "halfturn_certified",
            }
        return metadata

    def task_features(self, task_id: str, test_index: int) -> tuple[dict[str, float], tuple[int, int], set[int]]:
        task = self.challenges[task_id]
        task_diag = self.diagnostics.get(task_id, {})
        test_input = np.asarray(task["test"][test_index]["input"])
        modal_shape, shape_consistency = _modal_output_shape(task)
        same_shape: list[float] = []
        changes: list[float] = []
        input_colors: list[int] = []
        output_colors: list[int] = []
        output_palette: set[int] = set()
        for pair in task["train"]:
            source, target = np.asarray(pair["input"]), np.asarray(pair["output"])
            same_shape.append(float(source.shape == target.shape))
            if source.shape == target.shape:
                changes.append(float(np.mean(source != target)))
            input_colors.append(len(set(map(int, source.ravel()))))
            output_colors.append(len(set(map(int, target.ravel()))))
            output_palette.update(map(int, target.ravel()))

        route_probabilities = task_diag.get("route_probabilities", {}) or {}
        atlas_probabilities = task_diag.get("task_atlas_probabilities", {}) or {}
        resolution_probabilities = task_diag.get("task_resolution_probabilities", {}) or {}
        values: dict[str, float] = {
            "bias": 1.0,
            "log_train_count": math.log1p(len(task["train"])),
            "log_input_area": math.log1p(test_input.size),
            "log_modal_output_area": math.log1p(modal_shape[0] * modal_shape[1]),
            "shape_consistency": shape_consistency,
            "same_shape_rate": float(np.mean(same_shape)),
            "mean_change_rate": float(np.mean(changes)) if changes else 1.0,
            "mean_input_colors": float(np.mean(input_colors)),
            "mean_output_colors": float(np.mean(output_colors)),
            "log_candidate_count": math.log1p(_json_float(task_diag.get("candidate_count", 0))),
            "log_task_exact_fit_count": math.log1p(_json_float(task_diag.get("exact_fit_candidate_count", 0))),
            "posterior_entropy_log": math.log1p(max(0.0, _json_float(task_diag.get("posterior_entropy", 0)))),
            "model_disagreement": _json_float(task_diag.get("model_disagreement", 0)),
            "route_max": max([_json_float(v) for v in route_probabilities.values()] or [0.0]),
            "route_entropy": _entropy(route_probabilities),
            "atlas_max": max([_json_float(v) for v in atlas_probabilities.values()] or [0.0]),
            "atlas_entropy": _entropy(atlas_probabilities),
            "resolution_max": max([_json_float(v) for v in resolution_probabilities.values()] or [0.0]),
            "resolution_entropy": _entropy(resolution_probabilities),
            "identity_fast_path": float(task_diag.get("mode") == "identity_fast_path"),
            "block2_promoted": float((task_id, test_index) in self.block2_promotions),
            "halfturn_promoted": float((task_id, test_index) in self.halfturn_promotions),
        }
        for name in ROUTES:
            values[f"route_{name}"] = _json_float(route_probabilities.get(name, 0))
        for name in ATLASES:
            values[f"atlas_{name}"] = _json_float(atlas_probabilities.get(name, 0))
        for name in RESOLUTIONS:
            values[f"resolution_{name}"] = _json_float(resolution_probabilities.get(name, 0))
        return values, modal_shape, output_palette

    def attempt_features(
        self,
        task_id: str,
        test_index: int,
        attempt_index: int,
        grid: Any,
        modal_shape: tuple[int, int],
        output_palette: set[int],
    ) -> dict[str, float]:
        metadata = self._selected_meta(task_id, test_index, attempt_index)
        value = np.asarray(grid)
        test_input = np.asarray(self.challenges[task_id]["test"][test_index]["input"])
        colors = set(map(int, value.ravel()))
        union = colors | output_palette
        channel = metadata.get("channel_probabilities", {}) or {}
        families = {_family_group(name) for name in (metadata.get("families", []) or [])}
        result: dict[str, float] = {
            "probability": _json_float(metadata.get("probability", 0)),
            "best_candidate_probability": _json_float(metadata.get("best_candidate_probability", 0)),
            "exact_fit_probability": _json_float(metadata.get("exact_fit_probability", 0)),
            "exact_fit_candidate_count": _json_float(metadata.get("exact_fit_candidate_count", 0)),
            "log_probability": math.log(max(_json_float(metadata.get("probability", 0)), 1e-300)),
            "log_exact_fit_probability": math.log(max(_json_float(metadata.get("exact_fit_probability", 0)), 1e-300)),
            "structural_mass": _json_float(channel.get("structural", 0)),
            "base_mass": _json_float(channel.get("base", 0)),
            "shape_modal": float(tuple(value.shape) == tuple(modal_shape)),
            "shape_input": float(value.shape == test_input.shape),
            "log_area": math.log1p(value.size),
            "log_area_ratio_input": math.log((value.size + 1) / (test_input.size + 1)),
            "color_count": float(len(colors)),
            "constant_grid": float(len(colors) == 1),
            "identity_grid": float(exact(value, test_input)),
            "palette_jaccard": len(colors & output_palette) / len(union) if union else 1.0,
            "palette_subset": float(colors <= output_palette),
        }
        for group in FAMILY_GROUPS:
            result[f"family_{group}"] = float(group in families)
        return result

    def records(
        self,
        submission: Mapping[str, Any],
        solutions: Mapping[str, Any] | None = None,
    ) -> list[AttemptRecord]:
        result: list[AttemptRecord] = []
        for task_id in sorted(submission):
            for test_index, row in enumerate(submission[task_id]):
                task_values, modal_shape, output_palette = self.task_features(task_id, test_index)
                attempts = (row["attempt_1"], row["attempt_2"])
                attempt_values = tuple(
                    self.attempt_features(task_id, test_index, index, attempts[index], modal_shape, output_palette)
                    for index in (0, 1)
                )
                if solutions is None:
                    correct = (False, False)
                else:
                    truth = solutions[task_id][test_index]
                    correct = (exact(attempts[0], truth), exact(attempts[1], truth))
                diversity, shape_difference, hamming = _pair_diversity(*attempts)
                max_exact_fit = max(v["exact_fit_probability"] for v in attempt_values)
                promoted = bool(task_values["block2_promoted"] or task_values["halfturn_promoted"])
                result.append(
                    AttemptRecord(
                        task_id=task_id,
                        test_index=test_index,
                        task_features=task_values,
                        attempt_features=(attempt_values[0], attempt_values[1]),
                        attempts=attempts,
                        correct=correct,
                        coverage=bool(correct[0] or correct[1]),
                        diversity=diversity,
                        shape_difference=shape_difference,
                        hamming_difference=hamming,
                        no_exact_fit_or_promotion=bool(max_exact_fit <= 1e-12 and not promoted),
                    )
                )
        return result


def _dict_matrix(rows: Sequence[dict[str, float]], names: Sequence[str]) -> np.ndarray:
    return np.asarray([[float(row.get(name, 0.0)) for name in names] for row in rows], dtype=np.float64)


def build_matrices(records: Sequence[AttemptRecord]) -> MatrixBundle:
    if not records:
        raise ValueError("records must not be empty")
    task_names = sorted(records[0].task_features)
    attempt_names = sorted(records[0].attempt_features[0])

    attempt_rows: list[dict[str, float]] = []
    attempt_y: list[int] = []
    attempt_task_ids: list[str] = []
    coverage_rows: list[dict[str, float]] = []
    pair_rows: list[dict[str, float]] = []
    coverage_y: list[int] = []
    pair_y: list[int] = []
    attempt1_y: list[int] = []
    attempt2_y: list[int] = []

    for record in records:
        for index in (0, 1):
            row = {f"task:{name}": record.task_features[name] for name in task_names}
            row.update({f"attempt:{name}": record.attempt_features[index][name] for name in attempt_names})
            row["rank1"] = float(index == 0)
            attempt_rows.append(row)
            attempt_y.append(int(record.correct[index]))
            attempt_task_ids.append(record.task_id)

        first, second = record.attempt_features
        coverage = {f"task:{name}": record.task_features[name] for name in task_names}
        coverage.update({f"a1:{name}": first[name] for name in attempt_names})
        coverage.update({f"a2:{name}": second[name] for name in attempt_names})
        coverage["pair:diversity"] = record.diversity
        coverage["pair:shape_difference"] = record.shape_difference
        coverage_rows.append(coverage)

        pair = {f"task:{name}": record.task_features[name] for name in task_names}
        pair.update({f"delta:{name}": second[name] - first[name] for name in attempt_names})
        pair.update({f"sum:{name}": second[name] + first[name] for name in attempt_names})
        pair["pair:diversity"] = record.diversity
        pair["pair:shape_difference"] = record.shape_difference
        pair_rows.append(pair)

        coverage_y.append(int(record.coverage))
        pair_y.append(int(record.correct[1] and not record.correct[0]))
        attempt1_y.append(int(record.correct[0]))
        attempt2_y.append(int(record.correct[1]))

    attempt_feature_names = sorted(attempt_rows[0])
    coverage_feature_names = sorted(coverage_rows[0])
    pair_feature_names = sorted(pair_rows[0])

    attempt_keep = np.asarray(
        [
            name not in {
                "task:block2_promoted", "task:halfturn_promoted",
                "attempt:family_block2", "attempt:family_halfturn",
            }
            for name in attempt_feature_names
        ],
        dtype=bool,
    )
    coverage_keep = np.asarray(
        [name not in {"task:block2_promoted", "task:halfturn_promoted"} for name in coverage_feature_names],
        dtype=bool,
    )
    pair_keep = np.asarray(
        [
            name not in {
                "task:block2_promoted", "task:halfturn_promoted",
                "delta:family_block2", "delta:family_halfturn",
                "sum:family_block2", "sum:family_halfturn",
            }
            for name in pair_feature_names
        ],
        dtype=bool,
    )

    return MatrixBundle(
        records=list(records),
        attempt_X=_dict_matrix(attempt_rows, attempt_feature_names),
        attempt_y=np.asarray(attempt_y, dtype=np.int8),
        attempt_task_ids=np.asarray(attempt_task_ids, dtype=object),
        attempt_feature_names=attempt_feature_names,
        attempt_keep=attempt_keep,
        coverage_X=_dict_matrix(coverage_rows, coverage_feature_names),
        coverage_y=np.asarray(coverage_y, dtype=np.int8),
        coverage_task_ids=np.asarray([record.task_id for record in records], dtype=object),
        coverage_feature_names=coverage_feature_names,
        coverage_keep=coverage_keep,
        pair_X=_dict_matrix(pair_rows, pair_feature_names),
        pair_y=np.asarray(pair_y, dtype=np.int8),
        pair_feature_names=pair_feature_names,
        pair_keep=pair_keep,
        attempt1_y=np.asarray(attempt1_y, dtype=np.int8),
        attempt2_y=np.asarray(attempt2_y, dtype=np.int8),
    )


def _sigmoid(values: np.ndarray) -> np.ndarray:
    clipped = np.clip(values, -35.0, 35.0)
    return 1.0 / (1.0 + np.exp(-clipped))


@dataclass
class LogisticPosterior:
    schema: str
    feature_names: list[str]
    prior_precision: float
    mean: list[float]
    scale: list[float]
    coefficients: list[float]
    covariance: list[list[float]]
    iterations: int
    converged: bool

    @classmethod
    def fit(
        cls,
        X: np.ndarray,
        y: np.ndarray,
        feature_names: Sequence[str],
        *,
        prior_precision: float,
        max_iterations: int = 100,
        tolerance: float = 1e-7,
    ) -> "LogisticPosterior":
        matrix = np.asarray(X, dtype=np.float64)
        target = np.asarray(y, dtype=np.float64)
        if matrix.ndim != 2 or len(target) != matrix.shape[0]:
            raise ValueError("incompatible design matrix and target")
        if len(np.unique(target)) < 2:
            raise ValueError("logistic target must contain both classes")
        mean = matrix.mean(axis=0)
        scale = matrix.std(axis=0)
        scale[scale < 1e-8] = 1.0
        bias_indices = np.asarray(
            [index for index, name in enumerate(feature_names) if name in {"bias", "task:bias"}],
            dtype=int,
        )
        if len(bias_indices):
            mean[bias_indices] = 0.0
            scale[bias_indices] = 1.0
        Z = (matrix - mean) / scale
        coefficients = np.zeros(Z.shape[1], dtype=np.float64)
        penalty = np.ones_like(coefficients)
        if len(bias_indices):
            penalty[bias_indices] = 0.0
        converged = False
        iterations = 0
        for iteration in range(max_iterations):
            iterations = iteration + 1
            probability = _sigmoid(Z @ coefficients)
            weight = np.maximum(probability * (1.0 - probability), 1e-8)
            gradient = Z.T @ (target - probability) - prior_precision * penalty * coefficients
            hessian = Z.T @ (Z * weight[:, None]) + prior_precision * np.diag(penalty) + 1e-8 * np.eye(Z.shape[1])
            step = np.linalg.solve(hessian, gradient)
            old_objective = float(
                np.sum(target * np.log(np.clip(probability, 1e-15, 1.0)) + (1.0 - target) * np.log(np.clip(1.0 - probability, 1e-15, 1.0)))
                - 0.5 * prior_precision * np.sum(penalty * coefficients * coefficients)
            )
            factor = 1.0
            candidate = coefficients + step
            while factor > 1e-5:
                candidate = coefficients + factor * step
                candidate_probability = _sigmoid(Z @ candidate)
                new_objective = float(
                    np.sum(target * np.log(np.clip(candidate_probability, 1e-15, 1.0)) + (1.0 - target) * np.log(np.clip(1.0 - candidate_probability, 1e-15, 1.0)))
                    - 0.5 * prior_precision * np.sum(penalty * candidate * candidate)
                )
                if new_objective >= old_objective - 1e-10:
                    break
                factor *= 0.5
            coefficients = candidate
            if float(np.max(np.abs(factor * step))) < tolerance:
                converged = True
                break
        probability = _sigmoid(Z @ coefficients)
        weight = np.maximum(probability * (1.0 - probability), 1e-8)
        hessian = Z.T @ (Z * weight[:, None]) + prior_precision * np.diag(penalty) + 1e-8 * np.eye(Z.shape[1])
        covariance = np.linalg.inv(hessian)
        return cls(
            schema="komorebi.arc.logistic-laplace-posterior.v1",
            feature_names=list(feature_names),
            prior_precision=float(prior_precision),
            mean=mean.tolist(),
            scale=scale.tolist(),
            coefficients=coefficients.tolist(),
            covariance=covariance.tolist(),
            iterations=iterations,
            converged=converged,
        )

    def predict(self, X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        matrix = np.asarray(X, dtype=np.float64)
        mean = np.asarray(self.mean)
        scale = np.asarray(self.scale)
        coefficients = np.asarray(self.coefficients)
        covariance = np.asarray(self.covariance)
        Z = (matrix - mean) / scale
        latent = Z @ coefficients
        variance = np.einsum("ij,jk,ik->i", Z, covariance, Z)
        return _sigmoid(latent), np.maximum(variance, 0.0)

    def to_json(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_json(cls, value: Mapping[str, Any]) -> "LogisticPosterior":
        return cls(**dict(value))


def _log_loss(y: np.ndarray, probability: np.ndarray) -> float:
    p = np.clip(np.asarray(probability, dtype=np.float64), 1e-8, 1.0 - 1e-8)
    target = np.asarray(y, dtype=np.float64)
    return float(-np.mean(target * np.log(p) + (1.0 - target) * np.log(1.0 - p)))


def _ece(y: np.ndarray, probability: np.ndarray, bins: int = 10) -> float:
    target = np.asarray(y, dtype=np.float64)
    p = np.asarray(probability, dtype=np.float64)
    result = 0.0
    for index in range(bins):
        low, high = index / bins, (index + 1) / bins
        mask = (p >= low) & (p < (high if index < bins - 1 else high + 1e-12))
        if np.any(mask):
            result += float(mask.mean()) * abs(float(target[mask].mean() - p[mask].mean()))
    return result


def _auroc(y: np.ndarray, probability: np.ndarray) -> float:
    target = np.asarray(y, dtype=np.int8)
    scores = np.asarray(probability, dtype=np.float64)
    positive = int(target.sum())
    negative = len(target) - positive
    if positive == 0 or negative == 0:
        return float("nan")
    order = np.argsort(scores, kind="mergesort")
    ranks = np.empty(len(scores), dtype=np.float64)
    position = 0
    while position < len(order):
        end = position + 1
        while end < len(order) and scores[order[end]] == scores[order[position]]:
            end += 1
        average_rank = (position + 1 + end) / 2.0
        ranks[order[position:end]] = average_rank
        position = end
    rank_sum = float(ranks[target == 1].sum())
    return (rank_sum - positive * (positive + 1) / 2.0) / (positive * negative)


def probability_metrics(y: np.ndarray, probability: np.ndarray) -> dict[str, float]:
    target = np.asarray(y, dtype=np.float64)
    p = np.asarray(probability, dtype=np.float64)
    return {
        "brier": float(np.mean((p - target) ** 2)),
        "log_loss": _log_loss(target, p),
        "ece_10": _ece(target, p, 10),
        "auroc": _auroc(target, p),
        "mean_probability": float(p.mean()),
        "overconfident_wrong_rate_at_0_9": float(np.mean((p > 0.9) & (target == 0))),
    }


def _selected_names(names: Sequence[str], keep: np.ndarray) -> list[str]:
    return [name for name, retain in zip(names, keep) if retain]


def _fit_for_lambda(X: np.ndarray, y: np.ndarray, names: Sequence[str], prior_precision: float) -> LogisticPosterior:
    return LogisticPosterior.fit(X, y, names, prior_precision=prior_precision)


def _choose_probability_lambda(
    X: np.ndarray,
    y: np.ndarray,
    task_ids: np.ndarray,
    names: Sequence[str],
    *,
    outer_fold: int,
    eligible: np.ndarray | None = None,
) -> tuple[float, list[dict[str, float]]]:
    if eligible is None:
        eligible = np.ones(len(y), dtype=bool)
    scores: list[dict[str, float]] = []
    for prior_precision in LAMBDA_GRID:
        predictions: list[np.ndarray] = []
        targets: list[np.ndarray] = []
        for inner_fold in range(4):
            train = np.asarray(
                [
                    _group_fold(str(task_id), salt="block4-open-world-v2", folds=5) != outer_fold
                    and _group_fold(str(task_id), salt=f"block4-open-world-v2-inner-{outer_fold}", folds=4) != inner_fold
                    and bool(eligible[index])
                    for index, task_id in enumerate(task_ids)
                ],
                dtype=bool,
            )
            validate = np.asarray(
                [
                    _group_fold(str(task_id), salt="block4-open-world-v2", folds=5) != outer_fold
                    and _group_fold(str(task_id), salt=f"block4-open-world-v2-inner-{outer_fold}", folds=4) == inner_fold
                    and bool(eligible[index])
                    for index, task_id in enumerate(task_ids)
                ],
                dtype=bool,
            )
            model = _fit_for_lambda(X[train], y[train], names, prior_precision)
            probability, _ = model.predict(X[validate])
            predictions.append(probability)
            targets.append(y[validate])
        probability = np.concatenate(predictions)
        target = np.concatenate(targets)
        scores.append({"prior_precision": prior_precision, "log_loss": _log_loss(target, probability)})
    best = min(scores, key=lambda row: (row["log_loss"], row["prior_precision"]))
    return float(best["prior_precision"]), scores


def _choose_pair_lambda(bundle: MatrixBundle, outer_fold: int) -> tuple[float, list[dict[str, float]]]:
    X = bundle.pair_X[:, bundle.pair_keep]
    names = _selected_names(bundle.pair_feature_names, bundle.pair_keep)
    task_ids = bundle.coverage_task_ids
    scores: list[dict[str, float]] = []
    for prior_precision in LAMBDA_GRID:
        top1 = 0
        swaps = 0
        wins = 0
        losses = 0
        for inner_fold in range(4):
            train = np.asarray(
                [
                    _group_fold(str(task_id), salt="block4-open-world-v2", folds=5) != outer_fold
                    and _group_fold(str(task_id), salt=f"block4-open-world-v2-inner-{outer_fold}", folds=4) != inner_fold
                    and bool(bundle.coverage_y[index])
                    for index, task_id in enumerate(task_ids)
                ],
                dtype=bool,
            )
            validate = np.asarray(
                [
                    _group_fold(str(task_id), salt="block4-open-world-v2", folds=5) != outer_fold
                    and _group_fold(str(task_id), salt=f"block4-open-world-v2-inner-{outer_fold}", folds=4) == inner_fold
                    for task_id in task_ids
                ],
                dtype=bool,
            )
            model = _fit_for_lambda(X[train], bundle.pair_y[train], names, prior_precision)
            probability, _ = model.predict(X[validate])
            # Hyperparameter selection evaluates the model's natural 0.5 decision
            # boundary.  The deployed policy applies the stricter 0.75 threshold.
            choose_second = probability > 0.5
            first = bundle.attempt1_y[validate]
            second = bundle.attempt2_y[validate]
            top1 += int(np.sum(np.where(choose_second, second, first)))
            swaps += int(choose_second.sum())
            wins += int(np.sum(choose_second & (second > first)))
            losses += int(np.sum(choose_second & (first > second)))
        scores.append(
            {
                "prior_precision": prior_precision,
                "top1_exact": top1,
                "swaps": swaps,
                "wins": wins,
                "losses": losses,
            }
        )
    best = min(scores, key=lambda row: (-row["top1_exact"], row["losses"], row["prior_precision"]))
    return float(best["prior_precision"]), scores


@dataclass
class NestedAudit:
    attempt_probability: np.ndarray
    attempt_variance: np.ndarray
    coverage_probability: np.ndarray
    coverage_variance: np.ndarray
    pair_probability: np.ndarray
    pair_variance: np.ndarray
    fold_choices: list[dict[str, Any]]


def nested_grouped_audit(bundle: MatrixBundle) -> NestedAudit:
    attempt_probability = np.zeros(len(bundle.attempt_y), dtype=np.float64)
    attempt_variance = np.zeros(len(bundle.attempt_y), dtype=np.float64)
    coverage_probability = np.zeros(len(bundle.coverage_y), dtype=np.float64)
    coverage_variance = np.zeros(len(bundle.coverage_y), dtype=np.float64)
    pair_probability = np.zeros(len(bundle.pair_y), dtype=np.float64)
    pair_variance = np.zeros(len(bundle.pair_y), dtype=np.float64)
    choices: list[dict[str, Any]] = []

    AX = bundle.attempt_X[:, bundle.attempt_keep]
    CX = bundle.coverage_X[:, bundle.coverage_keep]
    PX = bundle.pair_X[:, bundle.pair_keep]
    attempt_names = _selected_names(bundle.attempt_feature_names, bundle.attempt_keep)
    coverage_names = _selected_names(bundle.coverage_feature_names, bundle.coverage_keep)
    pair_names = _selected_names(bundle.pair_feature_names, bundle.pair_keep)

    for outer_fold in range(5):
        attempt_test = np.asarray(
            [_group_fold(str(task_id), salt="block4-open-world-v2", folds=5) == outer_fold for task_id in bundle.attempt_task_ids],
            dtype=bool,
        )
        coverage_test = np.asarray(
            [_group_fold(str(task_id), salt="block4-open-world-v2", folds=5) == outer_fold for task_id in bundle.coverage_task_ids],
            dtype=bool,
        )
        attempt_train = ~attempt_test
        coverage_train = ~coverage_test

        attempt_lambda, attempt_grid = _choose_probability_lambda(
            AX, bundle.attempt_y, bundle.attempt_task_ids, attempt_names, outer_fold=outer_fold
        )
        coverage_lambda, coverage_grid = _choose_probability_lambda(
            CX, bundle.coverage_y, bundle.coverage_task_ids, coverage_names, outer_fold=outer_fold
        )
        pair_lambda, pair_grid = _choose_pair_lambda(bundle, outer_fold)

        attempt_model = _fit_for_lambda(AX[attempt_train], bundle.attempt_y[attempt_train], attempt_names, attempt_lambda)
        coverage_model = _fit_for_lambda(CX[coverage_train], bundle.coverage_y[coverage_train], coverage_names, coverage_lambda)
        pair_train = coverage_train & (bundle.coverage_y == 1)
        pair_model = _fit_for_lambda(PX[pair_train], bundle.pair_y[pair_train], pair_names, pair_lambda)

        attempt_probability[attempt_test], attempt_variance[attempt_test] = attempt_model.predict(AX[attempt_test])
        coverage_probability[coverage_test], coverage_variance[coverage_test] = coverage_model.predict(CX[coverage_test])
        pair_probability[coverage_test], pair_variance[coverage_test] = pair_model.predict(PX[coverage_test])
        choices.append(
            {
                "outer_fold": outer_fold,
                "attempt_prior_precision": attempt_lambda,
                "coverage_prior_precision": coverage_lambda,
                "pair_prior_precision": pair_lambda,
                "attempt_inner_grid": attempt_grid,
                "coverage_inner_grid": coverage_grid,
                "pair_inner_grid": pair_grid,
            }
        )

    no_exact = np.asarray([record.no_exact_fit_or_promotion for record in bundle.records], dtype=bool)
    coverage_probability[no_exact] = np.minimum(coverage_probability[no_exact], COVERAGE_CAP_NO_EXACT_FIT)
    return NestedAudit(
        attempt_probability=attempt_probability,
        attempt_variance=attempt_variance,
        coverage_probability=coverage_probability,
        coverage_variance=coverage_variance,
        pair_probability=pair_probability,
        pair_variance=pair_variance,
        fold_choices=choices,
    )


def _mode_with_numeric_tie(values: Sequence[float]) -> float:
    counts = Counter(float(value) for value in values)
    return min(counts, key=lambda value: (-counts[value], value))


def fit_final_models(bundle: MatrixBundle, audit: NestedAudit) -> dict[str, Any]:
    attempt_lambda = _mode_with_numeric_tie([row["attempt_prior_precision"] for row in audit.fold_choices])
    coverage_lambda = _mode_with_numeric_tie([row["coverage_prior_precision"] for row in audit.fold_choices])
    # Pair choices are more variable. The median supplies a deterministic robust aggregate.
    pair_values = sorted(float(row["pair_prior_precision"]) for row in audit.fold_choices)
    pair_lambda = pair_values[len(pair_values) // 2]

    AX = bundle.attempt_X[:, bundle.attempt_keep]
    CX = bundle.coverage_X[:, bundle.coverage_keep]
    PX = bundle.pair_X[:, bundle.pair_keep]
    attempt_names = _selected_names(bundle.attempt_feature_names, bundle.attempt_keep)
    coverage_names = _selected_names(bundle.coverage_feature_names, bundle.coverage_keep)
    pair_names = _selected_names(bundle.pair_feature_names, bundle.pair_keep)

    attempt_model = _fit_for_lambda(AX, bundle.attempt_y, attempt_names, attempt_lambda)
    coverage_model = _fit_for_lambda(CX, bundle.coverage_y, coverage_names, coverage_lambda)
    pair_model = _fit_for_lambda(PX[bundle.coverage_y == 1], bundle.pair_y[bundle.coverage_y == 1], pair_names, pair_lambda)
    return {
        "schema": "komorebi.arc.open-world-model-bundle.v1",
        "attempt_model": attempt_model.to_json(),
        "coverage_model": coverage_model.to_json(),
        "pair_model": pair_model.to_json(),
        "swap_threshold": SWAP_THRESHOLD,
        "coverage_cap_no_exact_fit": COVERAGE_CAP_NO_EXACT_FIT,
        "lambda_selection": {
            "attempt": {"rule": "mode of nested-fold choices; numeric ties favor stronger shrinkage order minimum", "value": attempt_lambda},
            "coverage": {"rule": "mode of nested-fold choices; numeric ties favor minimum", "value": coverage_lambda},
            "pair": {"rule": "median of nested-fold choices", "value": pair_lambda},
        },
        "feature_masks": {
            "attempt_all": bundle.attempt_feature_names,
            "attempt_selected": attempt_names,
            "coverage_all": bundle.coverage_feature_names,
            "coverage_selected": coverage_names,
            "pair_all": bundle.pair_feature_names,
            "pair_selected": pair_names,
        },
        "claim_boundary": "Fitted on the bundled public-training corpus; cross-fitted and locked-holdout evidence is reported separately.",
    }


def _raw_closed_world_confidence(record: AttemptRecord) -> float:
    return min(
        0.999999,
        max(
            record.attempt_features[0]["probability"],
            record.attempt_features[1]["probability"],
            record.attempt_features[0]["exact_fit_probability"],
            record.attempt_features[1]["exact_fit_probability"],
        ),
    )


def reorder_submission(
    submission: Mapping[str, Any],
    records: Sequence[AttemptRecord],
    pair_probability: np.ndarray,
    *,
    threshold: float = SWAP_THRESHOLD,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    import copy

    output = copy.deepcopy(submission)
    ledger: list[dict[str, Any]] = []
    for record, probability in zip(records, pair_probability):
        row = output[record.task_id][record.test_index]
        before_1, before_2 = freeze(row["attempt_1"]), freeze(row["attempt_2"])
        swap = bool(probability > threshold)
        if swap:
            row["attempt_1"], row["attempt_2"] = row["attempt_2"], row["attempt_1"]
        after_1, after_2 = freeze(row["attempt_1"]), freeze(row["attempt_2"])
        ledger.append(
            {
                "task_id": record.task_id,
                "test_index": record.test_index,
                "p_attempt_2_should_lead": float(probability),
                "threshold": threshold,
                "swapped": swap,
                "attempt_set_preserved": {before_1, before_2} == {after_1, after_2},
            }
        )
    return output, ledger


def select_diverse_top_two(
    candidates: Sequence[Mapping[str, Any]],
    *,
    unknown_mass: float,
    diversity_weight: float = 0.25,
) -> tuple[int, int]:
    """Select two candidate indices while penalizing semantic duplicates.

    Each candidate must contain ``probability`` and ``grid``.  The first attempt
    maximizes calibrated correctness probability.  The second maximizes its own
    probability plus a diversity bonus that grows with unknown-mechanism mass.
    """

    if len(candidates) < 2:
        raise ValueError("at least two candidates are required")
    probabilities = [_json_float(candidate.get("probability", 0.0)) for candidate in candidates]
    first = max(range(len(candidates)), key=lambda index: (probabilities[index], -index))
    first_grid = candidates[first]["grid"]
    scores: list[tuple[float, int]] = []
    for index, candidate in enumerate(candidates):
        if index == first:
            continue
        diversity, _, _ = _pair_diversity(first_grid, candidate["grid"])
        duplicate_penalty = 1.0 if freeze(first_grid) == freeze(candidate["grid"]) else 0.0
        score = probabilities[index] + diversity_weight * max(0.0, min(1.0, unknown_mass)) * diversity - duplicate_penalty
        scores.append((score, index))
    second = max(scores, key=lambda pair: (pair[0], -pair[1]))[1]
    return first, second


def audit_summary(bundle: MatrixBundle, audit: NestedAudit) -> dict[str, Any]:
    coverage_probability = audit.coverage_probability
    unknown_mass = 1.0 - coverage_probability
    choose_second = audit.pair_probability > SWAP_THRESHOLD
    top1 = np.where(choose_second, bundle.attempt2_y, bundle.attempt1_y)
    wins = int(np.sum(choose_second & (bundle.attempt2_y > bundle.attempt1_y)))
    losses = int(np.sum(choose_second & (bundle.attempt1_y > bundle.attempt2_y)))
    raw_coverage = np.asarray([_raw_closed_world_confidence(record) for record in bundle.records])
    uncovered = bundle.coverage_y == 0
    covered = bundle.coverage_y == 1
    return {
        "schema": "komorebi.arc.open-world-posterior-audit.v1",
        "records": len(bundle.records),
        "attempt_records": len(bundle.attempt_y),
        "coverage_positive": int(bundle.coverage_y.sum()),
        "attempt1_exact_before_reordering": int(bundle.attempt1_y.sum()),
        "attempt2_exact": int(bundle.attempt2_y.sum()),
        "cross_fitted_attempt1_exact_after_reordering": int(top1.sum()),
        "cross_fitted_attempt1_gain": int(top1.sum() - bundle.attempt1_y.sum()),
        "cross_fitted_swaps": int(choose_second.sum()),
        "cross_fitted_winning_swaps": wins,
        "cross_fitted_losing_swaps": losses,
        "cross_fitted_rank_accuracy_on_solved_outputs": float(np.mean((choose_second == bundle.pair_y.astype(bool))[covered])),
        "attempt_probability_metrics": probability_metrics(bundle.attempt_y, audit.attempt_probability),
        "coverage_probability_metrics": probability_metrics(bundle.coverage_y, coverage_probability),
        "raw_closed_world_coverage_metrics": probability_metrics(bundle.coverage_y, raw_coverage),
        "mean_unknown_mass_uncovered": float(unknown_mass[uncovered].mean()),
        "mean_unknown_mass_covered": float(unknown_mass[covered].mean()),
        "coverage_cap": {
            "threshold": COVERAGE_CAP_NO_EXACT_FIT,
            "affected_outputs": int(sum(record.no_exact_fit_or_promotion for record in bundle.records)),
            "covered_outputs_in_affected_group": int(
                sum(record.no_exact_fit_or_promotion and record.coverage for record in bundle.records)
            ),
        },
        "fold_choices": audit.fold_choices,
        "pass": bool(
            int(bundle.coverage_y.sum()) == 273
            and int(top1.sum()) >= 260
            and losses == 0
            and probability_metrics(bundle.coverage_y, coverage_probability)["brier"] < 0.06
            and probability_metrics(bundle.coverage_y, coverage_probability)["brier"]
            < probability_metrics(bundle.coverage_y, raw_coverage)["brier"]
            and float(unknown_mass[uncovered].mean()) > float(unknown_mass[covered].mean())
        ),
        "claim_boundary": "Grouped nested cross-fitting on public-training tasks; not a hidden-evaluation estimate.",
    }



def _select_matrix_columns(
    matrix: np.ndarray,
    all_names: Sequence[str],
    selected_names: Sequence[str],
) -> np.ndarray:
    positions = {name: index for index, name in enumerate(all_names)}
    missing = [name for name in selected_names if name not in positions]
    if missing:
        raise ValueError(f"runtime feature mismatch; missing {missing[:8]}")
    return matrix[:, [positions[name] for name in selected_names]]


def calibrate_runtime_submission(
    challenges: Mapping[str, Any],
    diagnostics: Mapping[str, Any],
    submission: Mapping[str, Any],
    model_bundle: Mapping[str, Any],
    *,
    block2_promotions: Sequence[Mapping[str, Any]] = (),
    halfturn_ledger: Sequence[Mapping[str, Any]] = (),
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Calibrate and reorder a live submission without access to solutions.

    The function accepts the base solver diagnostics and any source-blind outer-lane
    promotion records.  It emits the same two grids in a potentially different
    order together with coverage, unknown-mass, attempt, and ranking diagnostics.
    """

    factory = FeatureFactory(challenges, diagnostics, block2_promotions, halfturn_ledger)
    records = factory.records(submission, solutions=None)
    matrices = build_matrices(records)
    attempt_model = LogisticPosterior.from_json(model_bundle["attempt_model"])
    coverage_model = LogisticPosterior.from_json(model_bundle["coverage_model"])
    pair_model = LogisticPosterior.from_json(model_bundle["pair_model"])

    attempt_X = _select_matrix_columns(
        matrices.attempt_X, matrices.attempt_feature_names, attempt_model.feature_names
    )
    coverage_X = _select_matrix_columns(
        matrices.coverage_X, matrices.coverage_feature_names, coverage_model.feature_names
    )
    pair_X = _select_matrix_columns(
        matrices.pair_X, matrices.pair_feature_names, pair_model.feature_names
    )
    attempt_probability, attempt_variance = attempt_model.predict(attempt_X)
    coverage_probability, coverage_variance = coverage_model.predict(coverage_X)
    pair_probability, pair_variance = pair_model.predict(pair_X)
    no_exact = np.asarray([record.no_exact_fit_or_promotion for record in records], dtype=bool)
    coverage_probability[no_exact] = np.minimum(
        coverage_probability[no_exact],
        float(model_bundle.get("coverage_cap_no_exact_fit", COVERAGE_CAP_NO_EXACT_FIT)),
    )
    threshold = float(model_bundle.get("swap_threshold", SWAP_THRESHOLD))
    reordered, order_ledger = reorder_submission(
        submission, records, pair_probability, threshold=threshold
    )
    ledger: list[dict[str, Any]] = []
    for index, (record, order) in enumerate(zip(records, order_ledger)):
        ledger.append(
            {
                **order,
                "p_coverage": float(coverage_probability[index]),
                "p_unknown": float(1.0 - coverage_probability[index]),
                "coverage_latent_variance": float(coverage_variance[index]),
                "p_original_attempt_1_correct": float(attempt_probability[2 * index]),
                "p_original_attempt_2_correct": float(attempt_probability[2 * index + 1]),
                "original_attempt_1_latent_variance": float(attempt_variance[2 * index]),
                "original_attempt_2_latent_variance": float(attempt_variance[2 * index + 1]),
                "pair_latent_variance": float(pair_variance[index]),
                "no_exact_fit_or_promotion": record.no_exact_fit_or_promotion,
                "pair_diversity": record.diversity,
            }
        )
    return reordered, ledger

def model_from_bundle(bundle: Mapping[str, Any], key: str) -> LogisticPosterior:
    return LogisticPosterior.from_json(bundle[key])


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
