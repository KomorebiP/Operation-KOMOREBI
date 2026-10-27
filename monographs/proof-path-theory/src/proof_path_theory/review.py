from __future__ import annotations

import numpy as np


def equicorrelated_covariance(
    reviewers: int,
    variance: float = 1.0,
    correlation: float = 0.0,
) -> np.ndarray:
    if reviewers <= 0:
        raise ValueError("reviewers must be positive")
    if not np.isfinite(float(variance)) or variance <= 0:
        raise ValueError("variance must be finite and positive")
    if not np.isfinite(float(correlation)):
        raise ValueError("correlation must be finite")
    lower = -1.0 / (reviewers - 1) if reviewers > 1 else -1.0
    if not lower <= correlation <= 1.0:
        raise ValueError("correlation is outside the valid equicorrelation range")
    covariance = np.full((reviewers, reviewers), correlation * variance, dtype=float)
    np.fill_diagonal(covariance, variance)
    return covariance


def weighted_estimator_variance(weights: np.ndarray, covariance: np.ndarray) -> float:
    weights = np.asarray(weights, dtype=float)
    covariance = np.asarray(covariance, dtype=float)
    if covariance.ndim != 2 or covariance.shape[0] != covariance.shape[1]:
        raise ValueError("covariance must be square")
    if not np.all(np.isfinite(covariance)) or not np.all(np.isfinite(weights)):
        raise ValueError("weights and covariance must be finite")
    if not np.allclose(covariance, covariance.T, atol=1e-12):
        raise ValueError("covariance must be symmetric")
    if np.min(np.linalg.eigvalsh(covariance)) < -1e-12:
        raise ValueError("covariance must be positive semidefinite")
    if weights.shape != (covariance.shape[0],):
        raise ValueError("weights do not match covariance dimension")
    return float(weights @ covariance @ weights)


def equal_weight_variance(covariance: np.ndarray) -> float:
    covariance = np.asarray(covariance, dtype=float)
    if covariance.ndim != 2 or covariance.shape[0] != covariance.shape[1]:
        raise ValueError("covariance must be square")
    if covariance.shape[0] == 0:
        raise ValueError("covariance must be nonempty")
    weights = np.ones(covariance.shape[0], dtype=float) / covariance.shape[0]
    return weighted_estimator_variance(weights, covariance)


def equicorrelated_effective_count(reviewers: int, correlation: float) -> float:
    if reviewers <= 0:
        raise ValueError("reviewers must be positive")
    if not np.isfinite(float(correlation)):
        raise ValueError("correlation must be finite")
    lower = -1.0 / (reviewers - 1) if reviewers > 1 else -1.0
    if not lower < correlation <= 1.0:
        raise ValueError("correlation is outside the nonsingular range")
    denominator = 1.0 + (reviewers - 1) * correlation
    if denominator <= 0:
        raise ValueError("effective-count denominator must be positive")
    return float(reviewers / denominator)


def effective_reviewer_count(
    covariance: np.ndarray,
    *,
    reference_variance: float | None = None,
) -> float:
    covariance = np.asarray(covariance, dtype=float)
    if covariance.ndim != 2 or covariance.shape[0] != covariance.shape[1]:
        raise ValueError("covariance must be square")
    if covariance.shape[0] == 0:
        raise ValueError("covariance must be nonempty")
    if not np.all(np.isfinite(covariance)):
        raise ValueError("covariance must be finite")
    if not np.allclose(covariance, covariance.T, atol=1e-12):
        raise ValueError("covariance must be symmetric")
    if np.min(np.linalg.eigvalsh(covariance)) < -1e-12:
        raise ValueError("covariance must be positive semidefinite")
    if reference_variance is None:
        diagonal = np.diag(covariance)
        if np.any(diagonal <= 0):
            raise ValueError("covariance diagonal must be positive")
        reference_variance = float(np.mean(diagonal))
    if reference_variance <= 0:
        raise ValueError("reference_variance must be positive")
    variance = equal_weight_variance(covariance)
    if variance <= 0:
        raise ValueError("aggregate variance must be positive")
    return float(reference_variance / variance)


def generalized_least_squares_weights(covariance: np.ndarray) -> np.ndarray:
    covariance = np.asarray(covariance, dtype=float)
    if covariance.ndim != 2 or covariance.shape[0] != covariance.shape[1]:
        raise ValueError("covariance must be square")
    if covariance.shape[0] == 0:
        raise ValueError("covariance must be nonempty")
    if not np.all(np.isfinite(covariance)):
        raise ValueError("covariance must be finite")
    if not np.allclose(covariance, covariance.T, atol=1e-12):
        raise ValueError("covariance must be symmetric")
    eigenvalues = np.linalg.eigvalsh(covariance)
    if np.min(eigenvalues) <= 0:
        raise ValueError("covariance must be positive definite")
    ones = np.ones(covariance.shape[0], dtype=float)
    solved = np.linalg.solve(covariance, ones)
    denominator = float(ones @ solved)
    if denominator <= 0:
        raise ValueError("invalid covariance normalization")
    return solved / denominator


def shared_bias_mse(
    reviewers: int | np.ndarray,
    *,
    individual_variance: float,
    shared_bias: float,
    pairwise_correlation: float = 0.0,
    lens_variance: float = 0.0,
) -> np.ndarray:
    count = np.asarray(reviewers, dtype=float)
    scalar_inputs = np.asarray(
        [individual_variance, shared_bias, pairwise_correlation, lens_variance],
        dtype=float,
    )
    if not np.all(np.isfinite(count)) or not np.all(np.isfinite(scalar_inputs)):
        raise ValueError("review model inputs must be finite")
    if np.any(count <= 0):
        raise ValueError("reviewer counts must be positive")
    if individual_variance < 0 or lens_variance < 0:
        raise ValueError("variance parameters must be nonnegative")
    if not 0.0 <= pairwise_correlation <= 1.0:
        raise ValueError("pairwise correlation must lie in [0, 1]")
    variance = individual_variance * (
        pairwise_correlation + (1.0 - pairwise_correlation) / count
    )
    return variance + shared_bias**2 + lens_variance
