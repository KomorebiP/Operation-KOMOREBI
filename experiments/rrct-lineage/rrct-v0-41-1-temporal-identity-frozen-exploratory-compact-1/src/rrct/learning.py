"""Small deterministic readouts used by the prototype experiments."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


def interaction_features(x: np.ndarray, degree: int = 3) -> np.ndarray:
    """Expand rows with bounded polynomial interactions.

    The implementation intentionally includes interactions but not powers of a
    single coordinate.  This is enough to probe compositional reuse while
    keeping the feature matrix compact and deterministic.
    """

    array = np.asarray(x, dtype=np.float64)
    was_vector = array.ndim == 1
    if was_vector:
        array = array[None, :]
    if array.ndim != 2:
        raise ValueError("x must be one- or two-dimensional")
    if degree not in (1, 2, 3):
        raise ValueError("degree must be 1, 2, or 3")

    columns = [np.ones((array.shape[0], 1)), array]
    if degree >= 2:
        pairwise = [
            (array[:, i] * array[:, j])[:, None]
            for i in range(array.shape[1])
            for j in range(i + 1, array.shape[1])
        ]
        if pairwise:
            columns.append(np.concatenate(pairwise, axis=1))
    if degree >= 3:
        triples = [
            (array[:, i] * array[:, j] * array[:, k])[:, None]
            for i in range(array.shape[1])
            for j in range(i + 1, array.shape[1])
            for k in range(j + 1, array.shape[1])
        ]
        if triples:
            columns.append(np.concatenate(triples, axis=1))
    result = np.concatenate(columns, axis=1)
    return result[0] if was_vector else result


@dataclass
class RidgeBinaryReadout:
    """Closed-form ridge classifier with calibrated logistic scores."""

    alpha: float = 1e-3
    degree: int = 2
    weights: np.ndarray | None = None

    def fit(self, x: np.ndarray, y: np.ndarray) -> "RidgeBinaryReadout":
        features = interaction_features(x, self.degree)
        targets = 2.0 * np.asarray(y, dtype=np.float64).reshape(-1) - 1.0
        if features.shape[0] != targets.shape[0]:
            raise ValueError("x and y must have the same number of rows")
        gram = features.T @ features
        regularizer = self.alpha * np.eye(gram.shape[0])
        regularizer[0, 0] = 0.0
        self.weights = np.linalg.solve(gram + regularizer, features.T @ targets)
        return self

    def decision_function(self, x: np.ndarray) -> np.ndarray:
        if self.weights is None:
            raise RuntimeError("readout has not been fitted")
        return np.asarray(interaction_features(x, self.degree) @ self.weights)

    def predict_proba(self, x: np.ndarray) -> np.ndarray:
        scores = np.clip(self.decision_function(x), -30.0, 30.0)
        return 1.0 / (1.0 + np.exp(-scores))

    def predict(self, x: np.ndarray) -> np.ndarray:
        return (self.predict_proba(x) >= 0.5).astype(int)

    def score(self, x: np.ndarray, y: np.ndarray) -> float:
        truth = np.asarray(y, dtype=int).reshape(-1)
        return float(np.mean(self.predict(x).reshape(-1) == truth))


@dataclass
class LatentFactorProbe:
    """Decode three independent latent factors for compositional reuse tests.

    The probe is intentionally external to the agent.  It measures whether the
    final internal state contains context, object, and actuator information.
    New task labels are then computed from the same three decoded factors
    without refitting a task-specific classifier.
    """

    alpha: float = 1e-2
    mean_: np.ndarray | None = None
    scale_: np.ndarray | None = None
    models_: tuple[RidgeBinaryReadout, ...] | None = None

    def fit(self, x: np.ndarray, signed_factors: np.ndarray) -> "LatentFactorProbe":
        features = np.asarray(x, dtype=np.float64)
        factors = np.asarray(signed_factors, dtype=np.float64)
        if features.ndim != 2 or factors.ndim != 2 or factors.shape[1] != 3:
            raise ValueError("x must be 2D and signed_factors must have shape (n, 3)")
        if features.shape[0] != factors.shape[0]:
            raise ValueError("x and signed_factors must have the same number of rows")
        self.mean_ = features.mean(axis=0)
        self.scale_ = features.std(axis=0)
        self.scale_[self.scale_ < 1e-8] = 1.0
        standardized = (features - self.mean_) / self.scale_
        self.models_ = tuple(
            RidgeBinaryReadout(alpha=self.alpha, degree=1).fit(
                standardized, (factors[:, index] > 0).astype(int)
            )
            for index in range(3)
        )
        return self

    def _standardize(self, x: np.ndarray) -> np.ndarray:
        if self.mean_ is None or self.scale_ is None or self.models_ is None:
            raise RuntimeError("latent probe has not been fitted")
        features = np.asarray(x, dtype=np.float64)
        return (features - self.mean_) / self.scale_

    def predict_proba(self, x: np.ndarray) -> np.ndarray:
        standardized = self._standardize(x)
        assert self.models_ is not None
        return np.column_stack(
            [model.predict_proba(standardized) for model in self.models_]
        )

    def predict_signed(self, x: np.ndarray) -> np.ndarray:
        return np.where(self.predict_proba(x) >= 0.5, 1, -1).astype(int)

    def binding_accuracy(self, x: np.ndarray, signed_factors: np.ndarray) -> float:
        expected = np.asarray(signed_factors, dtype=int)
        return float(np.mean(np.all(self.predict_signed(x) == expected, axis=1)))
