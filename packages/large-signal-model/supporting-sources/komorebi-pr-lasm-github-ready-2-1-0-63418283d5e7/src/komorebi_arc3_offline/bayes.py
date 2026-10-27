from __future__ import annotations

from dataclasses import dataclass
from math import log

import numpy as np
from numpy.typing import NDArray
from scipy.special import gammaln, logsumexp

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
        x = np.asarray(features, dtype=np.float64)
        if x.ndim == 1:
            x = x[None, :]
        mean = x @ self.coefficient_mean.T
        leverage = 1.0 + np.einsum("nf,fg,ng->n", x, self.coefficient_covariance, x)
        variance = leverage[:, None] * (
            self.posterior_scale[None, :] / max(self.posterior_shape - 1.0, 1e-9)
        )
        return mean, np.maximum(variance, 1e-12)

    def predictive_log_likelihood(self, features: FloatArray, targets: FloatArray) -> float:
        x = np.asarray(features, dtype=np.float64)
        y = np.asarray(targets, dtype=np.float64)
        mean, _ = self.predict(x)
        leverage = 1.0 + np.einsum("nf,fg,ng->n", x, self.coefficient_covariance, x)
        degrees = 2.0 * self.posterior_shape
        total = 0.0
        for output in range(y.shape[1]):
            scale_squared = (self.posterior_scale[output] / self.posterior_shape) * leverage
            scale_squared = np.maximum(scale_squared, 1e-12)
            residual_squared = (y[:, output] - mean[:, output]) ** 2
            total += float(
                np.sum(
                    gammaln(0.5 * (degrees + 1.0))
                    - gammaln(0.5 * degrees)
                    - 0.5 * (np.log(degrees * np.pi) + np.log(scale_squared))
                    - 0.5
                    * (degrees + 1.0)
                    * np.log1p(residual_squared / (degrees * scale_squared))
                )
            )
        return total


@dataclass(frozen=True)
class BayesianRegression:
    prior_precision: float = 1.0
    shape: float = 2.0
    scale: float = 0.04

    def fit(self, design: FloatArray, targets: FloatArray) -> FittedBayesianRegression:
        x = np.asarray(design, dtype=np.float64)
        y = np.asarray(targets, dtype=np.float64)
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
            quadratic = float(target @ target - mean @ posterior_precision @ mean)
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
        return FittedBayesianRegression(
            coefficient_mean=coefficient_mean,
            coefficient_covariance=covariance,
            posterior_shape=float(posterior_shape),
            posterior_scale=posterior_scale,
            log_evidence=float(log_evidence),
        )


def normalized_probabilities(log_weights: FloatArray) -> FloatArray:
    values = np.asarray(log_weights, dtype=np.float64)
    if values.size == 0:
        return values
    return np.exp(values - logsumexp(values))
