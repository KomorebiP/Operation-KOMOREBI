from __future__ import annotations

from dataclasses import dataclass
from math import log

import numpy as np
from numpy.typing import NDArray
from scipy.special import gammaln, logsumexp
from ._validation import real_array

FloatArray = NDArray[np.float64]


def _positive_logdet(matrix: FloatArray) -> float:
    sign, value = np.linalg.slogdet(matrix)
    if sign <= 0:
        raise np.linalg.LinAlgError("matrix is not positive definite")
    return float(value)


@dataclass(frozen=True)
class FittedBayesianRegression:
    coefficient_mean: FloatArray
    coefficient_covariance: FloatArray
    posterior_shape: float
    posterior_scale: FloatArray
    log_evidence: float

    def predict(self, features: FloatArray) -> tuple[FloatArray, FloatArray]:
        raw = np.asarray(features)
        if raw.ndim == 1:
            raw = raw[None, :]
        x = real_array(raw, "prediction features", ndim=2, empty=True)
        if x.shape[1] != self.coefficient_mean.shape[1]:
            raise ValueError("prediction feature count differs from fitted design")
        mean = x @ self.coefficient_mean.T
        leverage = 1.0 + np.einsum("nf,fg,ng->n", x, self.coefficient_covariance, x)
        variance = leverage[:, None] * (
            self.posterior_scale[None, :] / max(self.posterior_shape - 1.0, 1e-9)
        )
        return mean, np.maximum(variance, 1e-12)

    def predictive_log_likelihood(
        self, features: FloatArray, targets: FloatArray,
        *, output_indices: list[int] | None = None,
    ) -> float:
        raw = np.asarray(features)
        if raw.ndim == 1:
            raw = raw[None, :]
        x = real_array(raw, "prediction features", ndim=2, empty=True)
        y = real_array(targets, "prediction targets", ndim=2, empty=True)
        mean, _ = self.predict(x)
        if y.shape != mean.shape:
            raise ValueError("prediction targets must match predicted rows and outputs")
        indices = list(range(y.shape[1])) if output_indices is None else list(output_indices)
        if not indices or len(indices) != len(set(indices)) or any(i < 0 or i >= y.shape[1] for i in indices):
            raise ValueError("output_indices must be a nonempty set of valid output columns")
        leverage = 1.0 + np.einsum("nf,fg,ng->n", x, self.coefficient_covariance, x)
        degrees = 2.0 * self.posterior_shape
        total = 0.0
        for output in indices:
            scale_squared = np.maximum((self.posterior_scale[output] / self.posterior_shape) * leverage, 1e-12)
            residual_squared = (y[:, output] - mean[:, output]) ** 2
            total += float(np.sum(
                gammaln(0.5 * (degrees + 1.0)) - gammaln(0.5 * degrees)
                - 0.5 * (np.log(degrees * np.pi) + np.log(scale_squared))
                - 0.5 * (degrees + 1.0) * np.log1p(residual_squared / (degrees * scale_squared))
            ))
        if not np.isfinite(total):
            raise FloatingPointError("predictive log likelihood is not finite")
        return total


@dataclass(frozen=True)
class BayesianRegression:
    prior_precision: float = 1.0
    shape: float = 2.0
    scale: float = 0.04

    def __post_init__(self) -> None:
        if not np.isfinite(self.prior_precision) or self.prior_precision <= 0:
            raise ValueError("prior_precision must be finite and positive")
        if not np.isfinite(self.shape) or self.shape <= 1:
            raise ValueError("shape must be finite and > 1 for finite predictive variance")
        if not np.isfinite(self.scale) or self.scale <= 0:
            raise ValueError("scale must be finite and positive")

    def fit(self, design: FloatArray, targets: FloatArray) -> FittedBayesianRegression:
        x = real_array(design, "design", ndim=2)
        y = real_array(targets, "targets", ndim=2)
        if x.ndim != 2 or y.ndim != 2 or x.shape[0] != y.shape[0]:
            raise ValueError("design and targets must be two-dimensional with matching rows")
        n, features = x.shape
        outputs = y.shape[1]
        prior = self.prior_precision * np.eye(features, dtype=np.float64)
        posterior_precision = prior + x.T @ x
        try:
            chol = np.linalg.cholesky(posterior_precision)
            covariance = np.linalg.solve(chol.T, np.linalg.solve(chol, np.eye(features)))
        except np.linalg.LinAlgError:
            covariance = np.linalg.pinv(posterior_precision, rcond=1e-10)
        coefficient_mean = (covariance @ x.T @ y).T
        posterior_shape = self.shape + 0.5 * n
        posterior_scale = np.empty(outputs, dtype=np.float64)
        log_evidence = 0.0
        logdet_prior = features * log(self.prior_precision)
        logdet_posterior = _positive_logdet(posterior_precision)
        for output in range(outputs):
            target = y[:, output]
            mean = coefficient_mean[output]
            residual = target - x @ mean
            # Equivalent to y'y - m'Lambda m, without catastrophic cancellation.
            quadratic = float(residual @ residual + self.prior_precision * (mean @ mean))
            scale = max(self.scale + 0.5 * quadratic, 1e-12)
            posterior_scale[output] = scale
            log_evidence += (
                gammaln(posterior_shape)
                - gammaln(self.shape)
                + self.shape * log(self.scale)
                - posterior_shape * log(scale)
                + 0.5 * (logdet_prior - logdet_posterior)
                - 0.5 * n * log(2.0 * np.pi)
            )
        if not np.isfinite(coefficient_mean).all() or not np.isfinite(posterior_scale).all() or not np.isfinite(log_evidence):
            raise FloatingPointError("regression fit produced nonfinite values")
        return FittedBayesianRegression(
            coefficient_mean=coefficient_mean,
            coefficient_covariance=covariance,
            posterior_shape=float(posterior_shape),
            posterior_scale=posterior_scale,
            log_evidence=float(log_evidence),
        )


def normalized_probabilities(log_weights: FloatArray) -> FloatArray:
    values = np.asarray(log_weights)
    if values.ndim != 1 or values.dtype.kind not in "biuf":
        raise ValueError("log weights must be a one-dimensional real numeric array")
    values = values.astype(np.float64)
    if np.isnan(values).any():
        raise ValueError("NaN log weights cannot define probabilities")
    if values.size == 0:
        return values
    positive_infinity = np.isposinf(values)
    if positive_infinity.any():
        return positive_infinity.astype(np.float64) / positive_infinity.sum()
    if not np.isfinite(values).any():
        raise ValueError("all candidates have zero mass (-infinite log weight)")
    probabilities = np.exp(values - logsumexp(values))
    return probabilities / probabilities.sum()
