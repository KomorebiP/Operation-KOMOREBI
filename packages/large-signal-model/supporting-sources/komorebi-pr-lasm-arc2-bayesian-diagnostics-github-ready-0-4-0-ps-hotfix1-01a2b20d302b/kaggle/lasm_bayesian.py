from __future__ import annotations

"""Bayesian Projector-Resolved Large Signal Model for static ARC tasks.

The deterministic ARC DSL supplies typed candidate programs.  This module keeps
those candidates separate from their evidence, constructs an exact multi-atlas
record for every demonstration, and forms a posterior over program, family,
atlas, resolution, and predicted output.  The posterior combines demonstration
likelihood, hierarchical family reliability, residual-route compatibility,
Bayesian ridge calibration, complexity, and prediction diversity.
"""

from dataclasses import dataclass, field
from math import exp, lgamma, log, pi, sqrt
from pathlib import Path
from typing import Any, Mapping, Protocol, Sequence
import json
import os

import numpy as np

try:
    from .atlas import (
        ARCAtlasAnalyzer,
        ATLAS_NAMES,
        RESOLUTION_NAMES,
        ROUTE_NAMES,
        TaskSignalState,
        analyze_task_signal,
        sanitize_grid,
    )
except ImportError:  # standalone Kaggle runtime
    from atlas import (
        ARCAtlasAnalyzer,
        ATLAS_NAMES,
        RESOLUTION_NAMES,
        ROUTE_NAMES,
        TaskSignalState,
        analyze_task_signal,
        sanitize_grid,
    )

Array = np.ndarray
FloatArray = np.ndarray


class CandidateLike(Protocol):
    name: str
    grids: Sequence[Array]
    train_grids: Sequence[Array]
    train_error: int
    complexity: int
    family: str


def canonical_grid(grid: Array) -> str:
    array = sanitize_grid(grid)
    return json.dumps(array.astype(int).tolist(), separators=(",", ":"))


def _logsumexp(values: FloatArray) -> float:
    values = np.asarray(values, dtype=np.float64)
    if values.size == 0:
        return float("-inf")
    maximum = float(np.max(values))
    return maximum + log(float(np.exp(values - maximum).sum()))


def normalized_probabilities(log_weights: Sequence[float]) -> FloatArray:
    values = np.asarray(log_weights, dtype=np.float64)
    if values.size == 0:
        return values
    return np.exp(values - _logsumexp(values))


def _log_beta(alpha: float, beta: float) -> float:
    return lgamma(alpha) + lgamma(beta) - lgamma(alpha + beta)


def beta_binomial_log_marginal(successes: int, failures: int, alpha: float, beta: float) -> float:
    successes = max(0, int(successes))
    failures = max(0, int(failures))
    total = successes + failures
    combinatorial = lgamma(total + 1.0) - lgamma(successes + 1.0) - lgamma(failures + 1.0)
    return combinatorial + _log_beta(alpha + successes, beta + failures) - _log_beta(alpha, beta)


def logistic_normal_mean(mean: float, variance: float) -> float:
    denominator = sqrt(max(1e-12, 1.0 + pi * max(0.0, variance) / 8.0))
    value = mean / denominator
    if value >= 0:
        return 1.0 / (1.0 + exp(-min(value, 60.0)))
    return exp(max(value, -60.0)) / (1.0 + exp(max(value, -60.0)))


@dataclass(frozen=True)
class FittedBayesianRidge:
    coefficient_mean: FloatArray
    coefficient_covariance: FloatArray
    posterior_shape: float
    posterior_scale: float
    feature_mean: FloatArray
    feature_scale: FloatArray
    feature_names: tuple[str, ...]

    def transform(self, features: FloatArray) -> FloatArray:
        values = np.asarray(features, dtype=np.float64)
        if values.ndim == 1:
            values = values[None, :]
        return (values - self.feature_mean[None, :]) / self.feature_scale[None, :]

    def predict(self, features: FloatArray) -> tuple[FloatArray, FloatArray]:
        x = self.transform(features)
        mean = x @ self.coefficient_mean
        leverage = 1.0 + np.einsum("nf,fg,ng->n", x, self.coefficient_covariance, x)
        variance = leverage * self.posterior_scale / max(self.posterior_shape - 1.0, 1e-9)
        return mean, np.maximum(variance, 1e-12)

    def to_json(self) -> dict[str, Any]:
        return {
            "coefficient_mean": self.coefficient_mean.tolist(),
            "coefficient_covariance": self.coefficient_covariance.tolist(),
            "posterior_shape": self.posterior_shape,
            "posterior_scale": self.posterior_scale,
            "feature_mean": self.feature_mean.tolist(),
            "feature_scale": self.feature_scale.tolist(),
            "feature_names": list(self.feature_names),
        }

    @classmethod
    def from_json(cls, data: Mapping[str, Any]) -> "FittedBayesianRidge":
        return cls(
            coefficient_mean=np.asarray(data["coefficient_mean"], dtype=np.float64),
            coefficient_covariance=np.asarray(data["coefficient_covariance"], dtype=np.float64),
            posterior_shape=float(data["posterior_shape"]),
            posterior_scale=float(data["posterior_scale"]),
            feature_mean=np.asarray(data["feature_mean"], dtype=np.float64),
            feature_scale=np.asarray(data["feature_scale"], dtype=np.float64),
            feature_names=tuple(str(value) for value in data["feature_names"]),
        )


@dataclass(frozen=True)
class BayesianRidge:
    prior_precision: float = 2.0
    shape: float = 2.5
    scale: float = 0.08

    def fit(self, design: FloatArray, targets: FloatArray, feature_names: Sequence[str]) -> FittedBayesianRidge:
        x = np.asarray(design, dtype=np.float64)
        y = np.asarray(targets, dtype=np.float64).ravel()
        if x.ndim != 2 or y.ndim != 1 or x.shape[0] != y.shape[0]:
            raise ValueError("design and targets must have matching rows")
        feature_mean = np.mean(x, axis=0)
        feature_scale = np.std(x, axis=0)
        feature_scale = np.where(feature_scale > 1e-10, feature_scale, 1.0)
        # Keep the explicit bias column uncentered. Centering a constant column
        # would turn it into zero and remove the posterior intercept entirely.
        if feature_names and str(feature_names[0]) == "bias":
            feature_mean = feature_mean.copy()
            feature_scale = feature_scale.copy()
            feature_mean[0] = 0.0
            feature_scale[0] = 1.0
        z = (x - feature_mean[None, :]) / feature_scale[None, :]
        prior = self.prior_precision * np.eye(z.shape[1], dtype=np.float64)
        precision = prior + z.T @ z
        try:
            chol = np.linalg.cholesky(precision)
            covariance = np.linalg.solve(chol.T, np.linalg.solve(chol, np.eye(precision.shape[0])))
        except np.linalg.LinAlgError:
            covariance = np.linalg.pinv(precision, rcond=1e-10)
        coefficient_mean = covariance @ z.T @ y
        posterior_shape = self.shape + 0.5 * z.shape[0]
        quadratic = float(y @ y - coefficient_mean @ precision @ coefficient_mean)
        posterior_scale = max(self.scale + 0.5 * quadratic, 1e-12)
        return FittedBayesianRidge(
            coefficient_mean=coefficient_mean,
            coefficient_covariance=covariance,
            posterior_shape=float(posterior_shape),
            posterior_scale=float(posterior_scale),
            feature_mean=feature_mean,
            feature_scale=feature_scale,
            feature_names=tuple(feature_names),
        )


@dataclass(frozen=True)
class BetaPrior:
    alpha: float = 1.0
    beta: float = 1.0

    @property
    def mean(self) -> float:
        return self.alpha / max(1e-12, self.alpha + self.beta)

    @property
    def variance(self) -> float:
        total = self.alpha + self.beta
        return self.alpha * self.beta / max(1e-12, total * total * (total + 1.0))

    def to_json(self) -> dict[str, float]:
        return {"alpha": self.alpha, "beta": self.beta}

    @classmethod
    def from_json(cls, value: Mapping[str, Any] | None) -> "BetaPrior":
        if not value:
            return cls()
        return cls(float(value.get("alpha", 1.0)), float(value.get("beta", 1.0)))


@dataclass(frozen=True)
class LASMCalibration:
    model_version: str
    families: tuple[str, ...]
    family_priors: Mapping[str, BetaPrior]
    route_family_priors: Mapping[str, Mapping[str, BetaPrior]]
    regression: FittedBayesianRidge | None = None
    training_metadata: Mapping[str, Any] = field(default_factory=dict)

    def family_prior(self, family: str) -> BetaPrior:
        return self.family_priors.get(family, self.family_priors.get("__unknown__", BetaPrior(1.0, 4.0)))

    def route_prior(self, route: str, family: str) -> BetaPrior:
        route_map = self.route_family_priors.get(route, {})
        return route_map.get(family, route_map.get("__unknown__", self.family_prior(family)))

    def to_json(self) -> dict[str, Any]:
        return {
            "model_version": self.model_version,
            "families": list(self.families),
            "family_priors": {key: value.to_json() for key, value in self.family_priors.items()},
            "route_family_priors": {
                route: {key: value.to_json() for key, value in priors.items()}
                for route, priors in self.route_family_priors.items()
            },
            "regression": None if self.regression is None else self.regression.to_json(),
            "training_metadata": dict(self.training_metadata),
        }

    @classmethod
    def from_json(cls, data: Mapping[str, Any]) -> "LASMCalibration":
        return cls(
            model_version=str(data.get("model_version", "unversioned")),
            families=tuple(str(value) for value in data.get("families", [])),
            family_priors={
                str(key): BetaPrior.from_json(value)
                for key, value in dict(data.get("family_priors", {})).items()
            },
            route_family_priors={
                str(route): {
                    str(key): BetaPrior.from_json(value)
                    for key, value in dict(priors).items()
                }
                for route, priors in dict(data.get("route_family_priors", {})).items()
            },
            regression=(
                None
                if data.get("regression") is None
                else FittedBayesianRidge.from_json(data["regression"])
            ),
            training_metadata=dict(data.get("training_metadata", {})),
        )

    @classmethod
    def neutral(cls) -> "LASMCalibration":
        return cls(
            model_version="neutral-1",
            families=(),
            family_priors={"__unknown__": BetaPrior(1.0, 3.0)},
            route_family_priors={},
            regression=None,
            training_metadata={"source": "neutral runtime fallback"},
        )


def load_calibration(path: str | Path | None = None) -> LASMCalibration:
    candidates: list[Path] = []
    if path is not None:
        candidates.append(Path(path))
    environment_path = os.environ.get("PR_LASM_ARC2_CALIBRATION")
    if environment_path:
        candidates.append(Path(environment_path))
    candidates.append(Path(__file__).resolve().parent / "data" / "bayesian_lasm_calibration.json")
    candidates.append(Path(__file__).resolve().parent / "bayesian_lasm_calibration.json")
    candidates.append(Path.cwd() / "bayesian_lasm_calibration.json")
    for candidate in candidates:
        if candidate.exists():
            try:
                return LASMCalibration.from_json(json.loads(candidate.read_text(encoding="utf-8")))
            except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
                continue
    return LASMCalibration.neutral()


def infer_family_atlas(family: str) -> str:
    value = family.lower()
    if "color" in value or "recolor" in value:
        return "color"
    if "polyphase" in value or "phase" in value:
        return "polyphase2"
    if "period" in value or "tile" in value:
        return "polyphase3"
    if "fourier" in value:
        return "fourier"
    if "sym" in value or "mirror" in value or "geometry" in value or "transform" in value:
        return "haar"
    if any(token in value for token in ("object", "gravity", "line", "bbox", "count", "frequency", "rank", "translation")):
        return "object"
    if "panel" in value or "block" in value:
        return "spatial"
    return "spatial"


def infer_family_resolution(family: str) -> str:
    value = family.lower()
    if any(token in value for token in ("object", "line", "bbox", "count", "relation", "translation")):
        return "micro"
    if any(token in value for token in ("panel", "polyphase", "phase", "mirror", "sym", "geometry", "block")):
        return "meso"
    return "macro"


def infer_candidate_channel(family: str) -> str:
    value = family.lower()
    if value in {
        "learned_transform",
        "color_map",
        "scale",
        "scale_color",
        "fallback",
        "program",
        "color_replace",
        "recolor_all",
    } or value.startswith("program"):
        return "base"
    return "structural"


@dataclass(frozen=True)
class CandidateMetrics:
    exact_rate: float
    shape_match_rate: float
    cell_match_rate: float
    error_per_cell: float
    group_residuals: Mapping[str, float]
    total_cells: int
    correct_cells: int
    incorrect_cells: int
    shape_matches: int
    shape_failures: int


def candidate_metrics(
    candidate: CandidateLike,
    train: Sequence[tuple[Array, Array]],
    analyzer: ARCAtlasAnalyzer,
) -> CandidateMetrics:
    predicted = list(getattr(candidate, "train_grids", ()) or ())
    if len(predicted) != len(train):
        predicted = [x.copy() for x, _ in train]
    exact_count = 0
    shape_matches = 0
    correct_cells = 0
    incorrect_cells = 0
    total_cells = 0
    group_residuals = {name: 0.0 for name in ATLAS_NAMES}
    for prediction, (_, target) in zip(predicted, train, strict=True):
        prediction = sanitize_grid(prediction)
        target = sanitize_grid(target)
        if prediction.shape == target.shape:
            shape_matches += 1
            matches = int(np.count_nonzero(prediction == target))
            correct_cells += matches
            incorrect_cells += int(target.size - matches)
            total_cells += int(target.size)
            exact_count += int(matches == target.size)
        else:
            total_cells += int(target.size)
            incorrect_cells += int(target.size)
        predicted_groups = analyzer.feature_groups(prediction)
        target_groups = analyzer.feature_groups(target)
        for name in ATLAS_NAMES:
            left = predicted_groups[name]
            right = target_groups[name]
            group_residuals[name] += float(np.linalg.norm(left - right) / max(1.0, sqrt(left.size)))
    count = max(1, len(train))
    group_residuals = {name: value / count for name, value in group_residuals.items()}
    return CandidateMetrics(
        exact_rate=exact_count / count,
        shape_match_rate=shape_matches / count,
        cell_match_rate=correct_cells / max(1, total_cells),
        error_per_cell=incorrect_cells / max(1, total_cells),
        group_residuals=group_residuals,
        total_cells=total_cells,
        correct_cells=correct_cells,
        incorrect_cells=incorrect_cells,
        shape_matches=shape_matches,
        shape_failures=count - shape_matches,
    )


def feature_schema(families: Sequence[str]) -> tuple[str, ...]:
    scalar = (
        "bias",
        "exact_rate",
        "shape_match_rate",
        "cell_match_rate",
        "neg_error_per_cell",
        "log_complexity",
        "family_prior_mean",
        "route_prior_mean",
        "atlas_compatibility",
        "resolution_compatibility",
        "train_error_log",
        "is_exact_fit",
    )
    residual = tuple(f"candidate_residual:{name}" for name in ATLAS_NAMES)
    task_route = tuple(f"task_route:{name}" for name in ROUTE_NAMES)
    task_atlas = tuple(f"task_atlas:{name}" for name in ATLAS_NAMES)
    task_resolution = tuple(f"task_resolution:{name}" for name in RESOLUTION_NAMES)
    task_summary = tuple(f"task_summary:{index}" for index in range(32))
    family = tuple(f"family:{name}" for name in families) + ("family:__unknown__",)
    return scalar + residual + task_route + task_atlas + task_resolution + task_summary + family


def candidate_feature_vector(
    candidate: CandidateLike,
    metrics: CandidateMetrics,
    task_state: TaskSignalState,
    calibration: LASMCalibration,
    schema_families: Sequence[str] | None = None,
) -> FloatArray:
    families = tuple(schema_families if schema_families is not None else calibration.families)
    family_prior = calibration.family_prior(candidate.family)
    route_prior = calibration.route_prior(task_state.primary_route, candidate.family)
    atlas = infer_family_atlas(candidate.family)
    resolution = infer_family_resolution(candidate.family)
    values: list[float] = [
        1.0,
        metrics.exact_rate,
        metrics.shape_match_rate,
        metrics.cell_match_rate,
        -metrics.error_per_cell,
        log1p_safe(candidate.complexity),
        family_prior.mean,
        route_prior.mean,
        float(task_state.atlas_probabilities.get(atlas, 0.0)),
        float(task_state.resolution_probabilities.get(resolution, 0.0)),
        log1p_safe(candidate.train_error),
        float(candidate.train_error == 0),
    ]
    values.extend(-float(metrics.group_residuals[name]) for name in ATLAS_NAMES)
    values.extend(float(task_state.route_probabilities[name]) for name in ROUTE_NAMES)
    values.extend(float(task_state.atlas_probabilities[name]) for name in ATLAS_NAMES)
    values.extend(float(task_state.resolution_probabilities[name]) for name in RESOLUTION_NAMES)
    values.extend(np.asarray(task_state.summary_vector[:32], dtype=np.float64).tolist())
    family_index = {name: index for index, name in enumerate(families)}
    one_hot = np.zeros(len(families) + 1, dtype=np.float64)
    one_hot[family_index.get(candidate.family, len(families))] = 1.0
    values.extend(one_hot.tolist())
    return np.asarray(values, dtype=np.float64)


def log1p_safe(value: float | int) -> float:
    return log(1.0 + max(0.0, float(value)))


@dataclass(frozen=True)
class CandidatePosterior:
    candidate_index: int
    name: str
    family: str
    atlas: str
    resolution: str
    probability: float
    log_weight: float
    demonstration_log_likelihood: float
    family_log_prior: float
    route_log_prior: float
    calibration_probability: float
    calibration_variance: float
    complexity_log_prior: float
    metrics: CandidateMetrics


@dataclass(frozen=True)
class OutputPosterior:
    grid: Array
    probability: float
    candidate_indices: tuple[int, ...]
    families: tuple[str, ...]
    names: tuple[str, ...]
    channel_probabilities: Mapping[str, float]
    exact_fit_probability: float
    exact_fit_candidate_count: int
    best_candidate_probability: float


@dataclass(frozen=True)
class LASMTaskPosterior:
    task_state: TaskSignalState
    candidate_posteriors: tuple[CandidatePosterior, ...]
    output_posteriors: tuple[tuple[OutputPosterior, ...], ...]
    family_probabilities: Mapping[str, float]
    atlas_probabilities: Mapping[str, float]
    resolution_probabilities: Mapping[str, float]
    posterior_entropy: float
    model_disagreement: float

    def diagnostics(self, top: int = 20) -> dict[str, Any]:
        candidates = sorted(self.candidate_posteriors, key=lambda item: item.probability, reverse=True)[:top]
        return {
            "primary_route": self.task_state.primary_route,
            "route_probabilities": dict(self.task_state.route_probabilities),
            "task_atlas_probabilities": dict(self.task_state.atlas_probabilities),
            "task_resolution_probabilities": dict(self.task_state.resolution_probabilities),
            "posterior_family_probabilities": dict(self.family_probabilities),
            "posterior_atlas_probabilities": dict(self.atlas_probabilities),
            "posterior_resolution_probabilities": dict(self.resolution_probabilities),
            "posterior_entropy": self.posterior_entropy,
            "model_disagreement": self.model_disagreement,
            "top_candidates": [
                {
                    "name": item.name,
                    "family": item.family,
                    "atlas": item.atlas,
                    "resolution": item.resolution,
                    "probability": item.probability,
                    "log_weight": item.log_weight,
                    "demonstration_log_likelihood": item.demonstration_log_likelihood,
                    "family_log_prior": item.family_log_prior,
                    "route_log_prior": item.route_log_prior,
                    "calibration_probability": item.calibration_probability,
                    "calibration_variance": item.calibration_variance,
                    "complexity_log_prior": item.complexity_log_prior,
                    "exact_rate": item.metrics.exact_rate,
                    "shape_match_rate": item.metrics.shape_match_rate,
                    "cell_match_rate": item.metrics.cell_match_rate,
                }
                for item in candidates
            ],
            "output_posteriors": [
                [
                    {
                        "probability": output.probability,
                        "families": list(output.families),
                        "names": list(output.names),
                        "channel_probabilities": dict(output.channel_probabilities),
                        "exact_fit_probability": output.exact_fit_probability,
                        "exact_fit_candidate_count": output.exact_fit_candidate_count,
                        "best_candidate_probability": output.best_candidate_probability,
                        "shape": list(output.grid.shape),
                    }
                    for output in outputs[:top]
                ]
                for outputs in self.output_posteriors
            ],
        }


@dataclass
class BayesianProjectorResolvedLargeSignalModel:
    calibration: LASMCalibration = field(default_factory=load_calibration)
    analyzer: ARCAtlasAnalyzer = field(default_factory=ARCAtlasAnalyzer)
    complexity_penalty: float = 0.045
    calibration_weight: float = 2.2
    family_weight: float = 1.2
    route_weight: float = 1.0
    atlas_weight: float = 0.8
    resolution_weight: float = 0.4
    diversity_weight: float = 0.55

    def _candidate_log_weight(
        self,
        candidate: CandidateLike,
        metrics: CandidateMetrics,
        task_state: TaskSignalState,
    ) -> tuple[float, dict[str, float]]:
        shape_log = beta_binomial_log_marginal(
            metrics.shape_matches,
            metrics.shape_failures,
            19.0,
            1.0,
        ) / max(1, metrics.shape_matches + metrics.shape_failures)
        cell_log = beta_binomial_log_marginal(
            metrics.correct_cells,
            metrics.incorrect_cells,
            49.0,
            1.0,
        ) / max(1, metrics.total_cells)
        exact_log = beta_binomial_log_marginal(
            int(round(metrics.exact_rate * max(1, len(candidate.train_grids)))),
            max(1, len(candidate.train_grids)) - int(round(metrics.exact_rate * max(1, len(candidate.train_grids)))),
            9.0,
            1.0,
        ) / max(1, len(candidate.train_grids))
        demonstration_log_likelihood = 9.0 * shape_log + 32.0 * cell_log + 5.0 * exact_log

        family_prior = self.calibration.family_prior(candidate.family)
        route_prior = self.calibration.route_prior(task_state.primary_route, candidate.family)
        family_log_prior = log(max(1e-9, family_prior.mean))
        route_log_prior = log(max(1e-9, route_prior.mean))
        atlas = infer_family_atlas(candidate.family)
        resolution = infer_family_resolution(candidate.family)
        atlas_log_prior = log(max(1e-9, task_state.atlas_probabilities.get(atlas, 1e-9)))
        resolution_log_prior = log(max(1e-9, task_state.resolution_probabilities.get(resolution, 1e-9)))
        complexity_log_prior = -self.complexity_penalty * log1p_safe(candidate.complexity)

        calibration_probability = 0.5
        calibration_variance = 1.0
        calibration_log = log(0.5)
        if self.calibration.regression is not None:
            features = candidate_feature_vector(candidate, metrics, task_state, self.calibration)
            if features.size == self.calibration.regression.coefficient_mean.size:
                mean, variance = self.calibration.regression.predict(features)
                calibration_probability = logistic_normal_mean(float(mean[0]), float(variance[0]))
                calibration_variance = float(variance[0])
                calibration_log = log(max(1e-9, calibration_probability))

        log_weight = (
            demonstration_log_likelihood
            + self.family_weight * family_log_prior
            + self.route_weight * route_log_prior
            + self.atlas_weight * atlas_log_prior
            + self.resolution_weight * resolution_log_prior
            + self.calibration_weight * calibration_log
            + complexity_log_prior
        )
        return log_weight, {
            "demonstration_log_likelihood": demonstration_log_likelihood,
            "family_log_prior": family_log_prior,
            "route_log_prior": route_log_prior,
            "calibration_probability": calibration_probability,
            "calibration_variance": calibration_variance,
            "complexity_log_prior": complexity_log_prior,
        }

    def fit_posterior(
        self,
        candidates: Sequence[CandidateLike],
        train: Sequence[tuple[Array, Array]],
        tests: Sequence[Array],
    ) -> LASMTaskPosterior:
        task_state = analyze_task_signal(train, self.analyzer)
        provisional: list[tuple[int, CandidateLike, CandidateMetrics, float, dict[str, float]]] = []
        for index, candidate in enumerate(candidates):
            if not candidate.grids:
                continue
            metrics = candidate_metrics(candidate, train, self.analyzer)
            log_weight, parts = self._candidate_log_weight(candidate, metrics, task_state)
            provisional.append((index, candidate, metrics, log_weight, parts))
        if not provisional:
            return LASMTaskPosterior(task_state, (), tuple(() for _ in tests), {}, {}, {}, 0.0, 1.0)
        probabilities = normalized_probabilities([row[3] for row in provisional])
        posterior_items: list[CandidatePosterior] = []
        family_probabilities: dict[str, float] = {}
        atlas_probabilities: dict[str, float] = {}
        resolution_probabilities: dict[str, float] = {}
        for row, probability in zip(provisional, probabilities, strict=True):
            index, candidate, metrics, log_weight, parts = row
            atlas = infer_family_atlas(candidate.family)
            resolution = infer_family_resolution(candidate.family)
            posterior = CandidatePosterior(
                candidate_index=index,
                name=candidate.name,
                family=candidate.family,
                atlas=atlas,
                resolution=resolution,
                probability=float(probability),
                log_weight=float(log_weight),
                demonstration_log_likelihood=float(parts["demonstration_log_likelihood"]),
                family_log_prior=float(parts["family_log_prior"]),
                route_log_prior=float(parts["route_log_prior"]),
                calibration_probability=float(parts["calibration_probability"]),
                calibration_variance=float(parts["calibration_variance"]),
                complexity_log_prior=float(parts["complexity_log_prior"]),
                metrics=metrics,
            )
            posterior_items.append(posterior)
            family_probabilities[candidate.family] = family_probabilities.get(candidate.family, 0.0) + float(probability)
            atlas_probabilities[atlas] = atlas_probabilities.get(atlas, 0.0) + float(probability)
            resolution_probabilities[resolution] = resolution_probabilities.get(resolution, 0.0) + float(probability)

        output_posteriors: list[tuple[OutputPosterior, ...]] = []
        for test_index in range(len(tests)):
            records: dict[str, dict[str, Any]] = {}
            for posterior in posterior_items:
                candidate = candidates[posterior.candidate_index]
                if test_index >= len(candidate.grids):
                    continue
                grid = sanitize_grid(candidate.grids[test_index])
                key = canonical_grid(grid)
                record = records.setdefault(
                    key,
                    {
                        "grid": grid,
                        "probability": 0.0,
                        "indices": [],
                        "families": set(),
                        "names": [],
                        "channels": {"base": 0.0, "structural": 0.0},
                        "exact_fit_probability": 0.0,
                        "exact_fit_candidate_count": 0,
                        "best_candidate_probability": 0.0,
                    },
                )
                record["probability"] += posterior.probability
                record["indices"].append(posterior.candidate_index)
                record["families"].add(posterior.family)
                record["names"].append(posterior.name)
                record["best_candidate_probability"] = max(float(record["best_candidate_probability"]), posterior.probability)
                if posterior.metrics.exact_rate >= 1.0 - 1e-12:
                    record["exact_fit_probability"] += posterior.probability
                    record["exact_fit_candidate_count"] = int(record["exact_fit_candidate_count"]) + 1
                channel = infer_candidate_channel(posterior.family)
                record["channels"][channel] = float(record["channels"].get(channel, 0.0)) + posterior.probability
            outputs = [
                OutputPosterior(
                    grid=record["grid"],
                    probability=float(record["probability"]),
                    candidate_indices=tuple(record["indices"]),
                    families=tuple(sorted(record["families"])),
                    names=tuple(record["names"]),
                    channel_probabilities={key: float(value) for key, value in record["channels"].items()},
                    exact_fit_probability=float(record["exact_fit_probability"]),
                    exact_fit_candidate_count=int(record["exact_fit_candidate_count"]),
                    best_candidate_probability=float(record["best_candidate_probability"]),
                )
                for record in records.values()
            ]
            outputs.sort(
                key=lambda item: (
                    -float(item.exact_fit_probability > 0.0),
                    -item.exact_fit_probability,
                    -item.probability,
                    item.grid.size,
                    canonical_grid(item.grid),
                )
            )
            output_posteriors.append(tuple(outputs))
        entropy = -sum(item.probability * log(max(item.probability, 1e-15)) for item in posterior_items)
        disagreement = 1.0 - sum(item.probability**2 for item in posterior_items)
        return LASMTaskPosterior(
            task_state=task_state,
            candidate_posteriors=tuple(sorted(posterior_items, key=lambda item: item.probability, reverse=True)),
            output_posteriors=tuple(output_posteriors),
            family_probabilities=family_probabilities,
            atlas_probabilities=atlas_probabilities,
            resolution_probabilities=resolution_probabilities,
            posterior_entropy=float(entropy),
            model_disagreement=float(disagreement),
        )

    @staticmethod
    def _grid_diversity(left: Array, right: Array) -> float:
        left = sanitize_grid(left)
        right = sanitize_grid(right)
        if left.shape != right.shape:
            area_ratio = min(left.size, right.size) / max(1, max(left.size, right.size))
            return min(1.0, 0.65 + 0.35 * (1.0 - area_ratio))
        return float(np.mean(left != right))

    def select_output_posteriors(self, posterior: LASMTaskPosterior, test_index: int, k: int = 2) -> list[OutputPosterior]:
        if test_index >= len(posterior.output_posteriors) or not posterior.output_posteriors[test_index]:
            return []
        outputs = list(posterior.output_posteriors[test_index])
        exact_outputs = [output for output in outputs if output.exact_fit_probability > 0.0]
        primary_pool = exact_outputs or outputs
        first = max(
            primary_pool,
            key=lambda output: (
                output.exact_fit_probability,
                output.probability,
                output.best_candidate_probability,
                -output.grid.size,
                canonical_grid(output.grid),
            ),
        )
        selected: list[OutputPosterior] = [first]
        if k <= 1:
            return selected

        remaining_exact = [output for output in exact_outputs if canonical_grid(output.grid) != canonical_grid(first.grid)]
        if remaining_exact:
            second = max(
                remaining_exact,
                key=lambda output: (
                    log(max(output.exact_fit_probability, 1e-15))
                    + self.diversity_weight * self._grid_diversity(first.grid, output.grid),
                    output.probability,
                    output.best_candidate_probability,
                ),
            )
            selected.append(second)
        else:
            remaining = [output for output in outputs if canonical_grid(output.grid) != canonical_grid(first.grid)]
            if remaining:
                first_channels = first.channel_probabilities
                second = max(
                    remaining,
                    key=lambda output: (
                        log(max(output.probability, 1e-15))
                        + self.diversity_weight * self._grid_diversity(first.grid, output.grid)
                        + 0.20
                        * float(
                            (first_channels.get("base", 0.0) > first_channels.get("structural", 0.0))
                            != (output.channel_probabilities.get("base", 0.0) > output.channel_probabilities.get("structural", 0.0))
                        ),
                        output.best_candidate_probability,
                    ),
                )
                selected.append(second)
        return selected[:k]

    def select_attempts(self, posterior: LASMTaskPosterior, test_index: int, k: int = 2) -> list[Array]:
        selected_outputs = self.select_output_posteriors(posterior, test_index, k=k)
        selected = [output.grid for output in selected_outputs]
        if not selected:
            selected = [np.zeros((1, 1), dtype=np.int16)]
        while len(selected) < k:
            selected.append(selected[0].copy())
        return [sanitize_grid(grid) for grid in selected[:k]]



@dataclass
class CalibrationAccumulator:
    family_success: dict[str, list[float]] = field(default_factory=dict)
    route_family_success: dict[str, dict[str, list[float]]] = field(default_factory=dict)
    design_rows: list[FloatArray] = field(default_factory=list)
    targets: list[float] = field(default_factory=list)

    def add(
        self,
        candidate: CandidateLike,
        metrics: CandidateMetrics,
        task_state: TaskSignalState,
        success_fraction: float,
        families: Sequence[str],
        calibration: LASMCalibration,
    ) -> None:
        self.family_success.setdefault(candidate.family, []).append(float(success_fraction))
        self.route_family_success.setdefault(task_state.primary_route, {}).setdefault(candidate.family, []).append(float(success_fraction))
        self.design_rows.append(candidate_feature_vector(candidate, metrics, task_state, calibration, families))
        self.targets.append(float(success_fraction))

    def finalize(
        self,
        families: Sequence[str],
        metadata: Mapping[str, Any],
        prior_strength: float = 2.0,
    ) -> LASMCalibration:
        family_priors: dict[str, BetaPrior] = {}
        for family in families:
            values = self.family_success.get(family, [])
            successes = float(sum(values))
            failures = float(len(values) - successes)
            family_priors[family] = BetaPrior(1.0 + prior_strength * successes, 1.0 + prior_strength * failures)
        family_priors["__unknown__"] = BetaPrior(1.0, 4.0)
        route_priors: dict[str, dict[str, BetaPrior]] = {}
        for route in ROUTE_NAMES:
            route_priors[route] = {}
            for family in families:
                values = self.route_family_success.get(route, {}).get(family, [])
                if values:
                    successes = float(sum(values))
                    failures = float(len(values) - successes)
                    route_priors[route][family] = BetaPrior(1.0 + prior_strength * successes, 1.0 + prior_strength * failures)
            route_priors[route]["__unknown__"] = BetaPrior(1.0, 4.0)
        regression = None
        if self.design_rows:
            design = np.vstack(self.design_rows)
            probabilities = np.clip(np.asarray(self.targets, dtype=np.float64), 0.0, 1.0)
            # The predictive layer is interpreted as latent log odds. Use a
            # small symmetric pseudo-count so exact failures and successes
            # remain finite while retaining a useful separation.
            smoothed = (probabilities + 0.05) / 1.10
            targets = np.log(smoothed / (1.0 - smoothed))
            regression = BayesianRidge().fit(design, targets, feature_schema(families))
        return LASMCalibration(
            model_version="pr-lasm-arc2-bayesian-0.4.0",
            families=tuple(families),
            family_priors=family_priors,
            route_family_priors=route_priors,
            regression=regression,
            training_metadata=dict(metadata),
        )


__all__ = [
    "BayesianProjectorResolvedLargeSignalModel",
    "BayesianRidge",
    "BetaPrior",
    "CalibrationAccumulator",
    "CandidateMetrics",
    "CandidatePosterior",
    "FittedBayesianRidge",
    "LASMCalibration",
    "LASMTaskPosterior",
    "OutputPosterior",
    "beta_binomial_log_marginal",
    "candidate_feature_vector",
    "candidate_metrics",
    "feature_schema",
    "infer_candidate_channel",
    "infer_family_atlas",
    "infer_family_resolution",
    "load_calibration",
    "normalized_probabilities",
]
