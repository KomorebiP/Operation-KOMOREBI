"""Causal components for the Recursive Resolution Closure prototype.

These components are deliberately small, deterministic, and NumPy-only.  They
are research scaffolding rather than a claim that a particular numerical
threshold establishes consciousness.  In particular, the self-model and
controller contain no reward, pleasure, pain, or valence variable: control is
based only on prediction, novelty, fidelity, and computational cost.
"""

from __future__ import annotations

import hashlib
import math
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy.typing import ArrayLike, NDArray

from .projectors import NestedOrthogonalProjectors


FloatArray = NDArray[np.float64]


def _vector(values: ArrayLike, length: int, name: str) -> FloatArray:
    """Coerce a finite one-dimensional vector and validate its length."""

    vector = np.asarray(values, dtype=np.float64)
    if vector.shape != (length,):
        raise ValueError(f"{name} must have shape ({length},), got {vector.shape}")
    if not np.all(np.isfinite(vector)):
        raise ValueError(f"{name} must contain only finite values")
    return vector


def balanced_matrix(
    rng_or_seed: np.random.Generator
    | np.random.SeedSequence
    | int
    | None,
    rows: int,
    columns: int,
    *,
    gain: float = 1.0,
) -> FloatArray:
    """Return a balanced rectangular matrix with equal nonzero singular values.

    The result has rank ``min(rows, columns)`` and every nonzero singular value
    equals ``gain`` up to floating-point roundoff.  Square results are scaled
    orthogonal matrices.  Rectangular results are scaled semi-orthogonal maps,
    avoiding the arbitrary direction amplification introduced by a normalized
    Gaussian matrix.

    Parameters
    ----------
    rng_or_seed:
        Existing NumPy generator or any seed accepted by
        :func:`numpy.random.default_rng`.
    rows, columns:
        Positive matrix dimensions.
    gain:
        Finite nonnegative common singular value.
    """

    if int(rows) != rows or rows <= 0 or int(columns) != columns or columns <= 0:
        raise ValueError("rows and columns must be positive integers")
    if not np.isfinite(gain) or gain < 0.0:
        raise ValueError("gain must be finite and nonnegative")
    rng = (
        rng_or_seed
        if isinstance(rng_or_seed, np.random.Generator)
        else np.random.default_rng(rng_or_seed)
    )
    rows = int(rows)
    columns = int(columns)
    rank = min(rows, columns)

    left_raw = rng.normal(size=(rows, rank))
    left, left_r = np.linalg.qr(left_raw, mode="reduced")
    left_signs = np.sign(np.diag(left_r))
    left_signs[left_signs == 0.0] = 1.0
    left = left * left_signs

    right_raw = rng.normal(size=(columns, rank))
    right, right_r = np.linalg.qr(right_raw, mode="reduced")
    right_signs = np.sign(np.diag(right_r))
    right_signs[right_signs == 0.0] = 1.0
    right = right * right_signs
    return np.asarray(float(gain) * (left @ right.T), dtype=np.float64)


def _normalized_random_matrix(
    rng: np.random.Generator,
    rows: int,
    columns: int,
    *,
    gain: float = 1.0,
) -> FloatArray:
    """Compatibility wrapper for the public balanced initializer."""

    return balanced_matrix(rng, rows, columns, gain=gain)


def _effective_gain(recurrence: bool, recurrent_gain: float) -> float:
    """Validate and apply a boolean recurrence gate to a continuous gain."""

    if not np.isfinite(recurrent_gain) or recurrent_gain < 0.0:
        raise ValueError("recurrent_gain must be finite and nonnegative")
    return float(recurrent_gain) if recurrence else 0.0


def _leaky_recurrent_state(
    previous: FloatArray,
    candidate: FloatArray,
    *,
    leak: float,
    recurrent_gain: float,
) -> FloatArray:
    """Blend bounded recurrent carry continuously from zero through gain one."""

    # This saturation is continuous at zero, preserves the historical blend
    # at gain=1, and keeps carry below one for the declared leaks (> 0.5).
    carry = (1.0 - leak) * 2.0 * recurrent_gain / (1.0 + recurrent_gain)
    return np.asarray(
        carry * previous + (1.0 - carry) * candidate,
        dtype=np.float64,
    )


@dataclass(frozen=True)
class SpecialistOutput:
    """A specialist's workspace proposal and local evidence."""

    name: str
    level: int
    state: FloatArray
    salience: float
    confidence: float
    reconstruction_error: float


class SpecialistModule:
    """A local recurrent processor assigned to one resolution detail band."""

    def __init__(
        self,
        input_dim: int,
        output_dim: int,
        *,
        level: int,
        broadcast_dim: int,
        name: str | None = None,
        leak: float = 0.55,
        seed: int | np.random.SeedSequence | None = 0,
    ) -> None:
        if min(input_dim, output_dim, broadcast_dim) <= 0:
            raise ValueError("specialist dimensions must be positive")
        if level < 0:
            raise ValueError("level must be nonnegative")
        if not 0.0 < leak <= 1.0:
            raise ValueError("leak must lie in (0, 1]")
        self.input_dim = int(input_dim)
        self.output_dim = int(output_dim)
        self.broadcast_dim = int(broadcast_dim)
        self.level = int(level)
        self.name = name or f"specialist_{level}"
        self.leak = float(leak)

        rng = np.random.default_rng(seed)
        self._input_weights = _normalized_random_matrix(
            rng, self.output_dim, self.input_dim, gain=1.15
        )
        self._recurrent_weights = _normalized_random_matrix(
            rng, self.output_dim, self.output_dim, gain=0.72
        )
        self._broadcast_weights = _normalized_random_matrix(
            rng, self.output_dim, self.broadcast_dim, gain=0.45
        )
        self._decoder = np.linalg.pinv(self._input_weights)
        self.state = np.zeros(self.output_dim, dtype=np.float64)

    def reset(self) -> None:
        """Clear local recurrent state without changing parameters."""

        self.state.fill(0.0)

    def process(
        self,
        signal: ArrayLike,
        *,
        broadcast: ArrayLike | None = None,
        recurrence: bool = True,
        recurrent_gain: float = 1.0,
    ) -> SpecialistOutput:
        """Process a detail-band signal and propose a workspace state."""

        x = _vector(signal, self.input_dim, "signal")
        if broadcast is None:
            feedback = np.zeros(self.broadcast_dim, dtype=np.float64)
        else:
            feedback = _vector(broadcast, self.broadcast_dim, "broadcast")

        effective_gain = _effective_gain(recurrence, recurrent_gain)
        drive = self._input_weights @ x + self._broadcast_weights @ feedback
        if effective_gain:
            drive = drive + effective_gain * (self._recurrent_weights @ self.state)
        candidate = np.tanh(drive)
        self.state = _leaky_recurrent_state(
            self.state,
            candidate,
            leak=self.leak,
            recurrent_gain=effective_gain,
        )

        decoded = self._decoder @ self.state
        scale = 1.0 + float(np.linalg.norm(x))
        reconstruction_error = float(np.linalg.norm(decoded - x) / scale)
        confidence = float(1.0 / (1.0 + reconstruction_error))
        salience = float(confidence * np.linalg.norm(self.state))
        return SpecialistOutput(
            name=self.name,
            level=self.level,
            state=self.state.copy(),
            salience=salience,
            confidence=confidence,
            reconstruction_error=reconstruction_error,
        )


@dataclass(frozen=True)
class WorkspaceBroadcast:
    """Result of capacity-limited global competition."""

    state: FloatArray
    selected: tuple[str, ...]
    weights: FloatArray
    proposal_states: FloatArray


class GlobalWorkspace:
    """A recurrent, capacity-limited workspace with competitive broadcast."""

    def __init__(
        self,
        proposal_dim: int,
        workspace_dim: int,
        *,
        capacity: int = 3,
        leak: float = 0.65,
        seed: int | np.random.SeedSequence | None = 0,
    ) -> None:
        if min(proposal_dim, workspace_dim, capacity) <= 0:
            raise ValueError("workspace dimensions and capacity must be positive")
        if not 0.0 < leak <= 1.0:
            raise ValueError("leak must lie in (0, 1]")
        self.proposal_dim = int(proposal_dim)
        self.workspace_dim = int(workspace_dim)
        self.capacity = int(capacity)
        self.leak = float(leak)

        rng = np.random.default_rng(seed)
        self._proposal_weights = _normalized_random_matrix(
            rng, self.workspace_dim, self.proposal_dim, gain=1.0
        )
        self._recurrent_weights = _normalized_random_matrix(
            rng, self.workspace_dim, self.workspace_dim, gain=0.70
        )
        self.state = np.zeros(self.workspace_dim, dtype=np.float64)

    def reset(self) -> None:
        """Clear workspace recurrence."""

        self.state.fill(0.0)

    def step(
        self,
        proposals: tuple[SpecialistOutput, ...] | list[SpecialistOutput],
        *,
        recurrence: bool = True,
        recurrent_gain: float = 1.0,
        enabled: bool = True,
        perturbation: ArrayLike | None = None,
    ) -> WorkspaceBroadcast:
        """Select salient proposals and create a global broadcast.

        ``perturbation`` is an additive causal intervention applied after
        recurrent integration.  It is intentionally explicit so experiments
        can compare unperturbed and counterfactual trajectories.
        """

        if not enabled or not proposals:
            self.state.fill(0.0)
            return WorkspaceBroadcast(
                state=self.state.copy(),
                selected=(),
                weights=np.zeros(0, dtype=np.float64),
                proposal_states=np.zeros((0, self.proposal_dim), dtype=np.float64),
            )

        for proposal in proposals:
            _vector(proposal.state, self.proposal_dim, f"{proposal.name}.state")
        count = min(self.capacity, len(proposals))
        # Stable sorting makes equal-salience outcomes deterministic.
        order = sorted(
            range(len(proposals)),
            key=lambda index: (-proposals[index].salience, proposals[index].name),
        )[:count]
        selected = tuple(proposals[index] for index in order)
        logits = np.asarray([proposal.salience for proposal in selected], dtype=np.float64)
        logits -= float(np.max(logits))
        weights = np.exp(logits)
        weights /= float(np.sum(weights))
        states = np.stack([proposal.state for proposal in selected], axis=0)
        pooled = np.sum(weights[:, None] * states, axis=0)

        effective_gain = _effective_gain(recurrence, recurrent_gain)
        drive = self._proposal_weights @ pooled
        if effective_gain:
            drive = drive + effective_gain * (self._recurrent_weights @ self.state)
        candidate = np.tanh(drive)
        candidate = _leaky_recurrent_state(
            self.state,
            candidate,
            leak=self.leak,
            recurrent_gain=effective_gain,
        )
        if perturbation is not None:
            candidate = candidate + _vector(
                perturbation, self.workspace_dim, "perturb_workspace"
            )
        self.state = np.asarray(np.tanh(candidate), dtype=np.float64)

        return WorkspaceBroadcast(
            state=self.state.copy(),
            selected=tuple(proposal.name for proposal in selected),
            weights=np.asarray(weights, dtype=np.float64),
            proposal_states=np.asarray(states, dtype=np.float64),
        )


class NonValencedSelfModel:
    """A causal self-state and one-step workspace predictor.

    The model tracks prediction error and internally available state.  It has
    no reward head, preference ordering, affect variable, or suffering proxy.
    """

    def __init__(
        self,
        workspace_dim: int,
        self_dim: int,
        *,
        leak: float = 0.55,
        learning_rate: float = 0.08,
        normalized_lms_epsilon: float = 1e-8,
        training: bool = False,
        seed: int | np.random.SeedSequence | None = 0,
    ) -> None:
        if min(workspace_dim, self_dim) <= 0:
            raise ValueError("self-model dimensions must be positive")
        if not 0.0 < leak <= 1.0:
            raise ValueError("leak must lie in (0, 1]")
        if (
            not np.isfinite(learning_rate)
            or learning_rate < 0.0
            or learning_rate > 2.0
        ):
            raise ValueError("learning_rate must be finite and lie in [0, 2]")
        if not np.isfinite(normalized_lms_epsilon) or normalized_lms_epsilon <= 0.0:
            raise ValueError("normalized_lms_epsilon must be finite and positive")
        self.workspace_dim = int(workspace_dim)
        self.self_dim = int(self_dim)
        self.leak = float(leak)
        self.learning_rate = float(learning_rate)
        self.normalized_lms_epsilon = float(normalized_lms_epsilon)
        self._training = bool(training)

        rng = np.random.default_rng(seed)
        input_dim = 3 * self.workspace_dim
        self._input_weights = _normalized_random_matrix(
            rng, self.self_dim, input_dim, gain=1.1
        )
        self._recurrent_weights = _normalized_random_matrix(
            rng, self.self_dim, self.self_dim, gain=0.68
        )
        self._prediction_weights = _normalized_random_matrix(
            rng, self.workspace_dim, self.self_dim, gain=0.10
        )
        self._workspace_skip = (
            0.72 * np.eye(self.workspace_dim, dtype=np.float64)
            + _normalized_random_matrix(
                rng, self.workspace_dim, self.workspace_dim, gain=0.06
            )
        )
        self.state = np.zeros(self.self_dim, dtype=np.float64)
        self._last_workspace = np.zeros(self.workspace_dim, dtype=np.float64)
        self._prediction_features = np.zeros(
            self.self_dim + self.workspace_dim, dtype=np.float64
        )
        self._last_prediction = np.zeros(self.workspace_dim, dtype=np.float64)
        self._learning_steps = 0

    def reset(self) -> None:
        """Clear the self-state and its temporal predictor."""

        self.state.fill(0.0)
        self._last_workspace.fill(0.0)
        self._prediction_features.fill(0.0)
        self._last_prediction.fill(0.0)

    @property
    def training(self) -> bool:
        """Whether normalized-LMS predictor updates are enabled."""

        return self._training

    @property
    def learning_steps(self) -> int:
        """Number of enabled predictor-learning calls since initialization."""

        return self._learning_steps

    def train(self) -> None:
        """Enable online self-prediction learning."""

        self._training = True

    def freeze(self) -> None:
        """Disable learning while retaining the learned predictor exactly."""

        self._training = False

    def predict_workspace(self) -> FloatArray:
        """Predict the next workspace from the current self-state."""

        self._prediction_features = np.concatenate(
            (self.state, self._last_workspace), axis=0
        )
        prediction = np.asarray(
            np.tanh(
                self._prediction_weights @ self.state
                + self._workspace_skip @ self._last_workspace
            ),
            dtype=np.float64,
        )
        self._last_prediction = prediction.copy()
        return prediction

    def learn_workspace(
        self,
        target_workspace: ArrayLike,
        *,
        enabled: bool = True,
    ) -> bool:
        """Apply one deterministic normalized-LMS predictor update.

        The feature vector cached by the preceding :meth:`predict_workspace`
        call is paired with the now observed workspace target.  ``enabled`` is
        an explicit causal gate used by the agent's self-model ablation.
        Returns whether a training step was performed.
        """

        target = _vector(
            target_workspace, self.workspace_dim, "target_workspace"
        )
        if not enabled or not self._training:
            return False
        error = target - self._last_prediction
        # The tanh derivative converts output error to a local linearized LMS
        # residual.  Normalization makes the deterministic step insensitive to
        # the feature-vector scale and keeps rates in the standard [0, 2] band.
        delta = error * (1.0 - np.square(self._last_prediction))
        denominator = self.normalized_lms_epsilon + float(
            self._prediction_features @ self._prediction_features
        )
        correction = (
            self.learning_rate
            * np.outer(delta, self._prediction_features)
            / denominator
        )
        self._prediction_weights += correction[:, : self.self_dim]
        self._workspace_skip += correction[:, self.self_dim :]
        self._learning_steps += 1
        return True

    def predictor_snapshot(self) -> dict[str, Any]:
        """Return an independent copy of learned predictor parameters."""

        return {
            "prediction_weights": self._prediction_weights.copy(),
            "workspace_skip": self._workspace_skip.copy(),
            "learning_steps": self._learning_steps,
            "learning_rate": self.learning_rate,
            "normalized_lms_epsilon": self.normalized_lms_epsilon,
        }

    def load_predictor_snapshot(
        self,
        snapshot: Mapping[str, Any],
        *,
        freeze: bool = True,
    ) -> None:
        """Load exact learned parameters for matched causal comparisons."""

        prediction_weights = np.asarray(
            snapshot["prediction_weights"], dtype=np.float64
        )
        workspace_skip = np.asarray(snapshot["workspace_skip"], dtype=np.float64)
        if prediction_weights.shape != (self.workspace_dim, self.self_dim):
            raise ValueError(
                "prediction_weights must have shape "
                f"({self.workspace_dim}, {self.self_dim})"
            )
        if workspace_skip.shape != (self.workspace_dim, self.workspace_dim):
            raise ValueError(
                "workspace_skip must have shape "
                f"({self.workspace_dim}, {self.workspace_dim})"
            )
        if not np.all(np.isfinite(prediction_weights)) or not np.all(
            np.isfinite(workspace_skip)
        ):
            raise ValueError("predictor parameters must contain only finite values")
        learning_steps = int(snapshot.get("learning_steps", 0))
        if learning_steps < 0:
            raise ValueError("learning_steps must be nonnegative")
        self._prediction_weights = prediction_weights.copy()
        self._workspace_skip = workspace_skip.copy()
        self._learning_steps = learning_steps
        if freeze:
            self.freeze()

    def update(
        self,
        workspace: ArrayLike,
        memory: ArrayLike,
        prediction_error: ArrayLike,
        *,
        recurrence: bool = True,
        recurrent_gain: float = 1.0,
        enabled: bool = True,
    ) -> FloatArray:
        """Update the causally active self-model."""

        workspace_vector = _vector(workspace, self.workspace_dim, "workspace")
        memory_vector = _vector(memory, self.workspace_dim, "memory")
        error_vector = _vector(
            prediction_error, self.workspace_dim, "prediction_error"
        )
        if not enabled:
            self.reset()
            return self.state.copy()

        features = np.concatenate(
            (workspace_vector, memory_vector, error_vector), axis=0
        )
        effective_gain = _effective_gain(recurrence, recurrent_gain)
        drive = self._input_weights @ features
        if effective_gain:
            drive = drive + effective_gain * (self._recurrent_weights @ self.state)
        candidate = np.tanh(drive)
        self.state = _leaky_recurrent_state(
            self.state,
            candidate,
            leak=self.leak,
            recurrent_gain=effective_gain,
        )
        self._last_workspace = workspace_vector.copy()
        return self.state.copy()


@dataclass(frozen=True)
class MemoryRead:
    """Similarity-weighted episodic retrieval."""

    vector: FloatArray
    indices: tuple[int, ...]
    similarities: FloatArray
    weights: FloatArray


class NonValencedObservationForecaster:
    """Small label-free autoregressive forecaster for internal planning only."""

    SNAPSHOT_SCHEMA = "rrct.nonvalenced_observation_forecaster.v1"
    MODEL_ORDER = 1
    ACTIVATION = "tanh"
    UPDATE_RULE = "normalized_lms_tanh_v1"
    NORMALIZED_LMS_EPSILON = 1e-8
    SNAPSHOT_DTYPE = "float64"

    @staticmethod
    def _finite_real_scalar(value: Any, name: str) -> float:
        """Parse one finite real scalar without accepting bools or strings."""

        if isinstance(value, (bool, np.bool_)) or not np.isscalar(value):
            raise ValueError(f"{name} must be a finite real scalar")
        array = np.asarray(value)
        if array.dtype.kind not in "iuf":
            raise ValueError(f"{name} must be a finite real scalar")
        parsed = float(value)
        if not np.isfinite(parsed):
            raise ValueError(f"{name} must be a finite real scalar")
        return parsed

    @classmethod
    def _integer_scalar(
        cls,
        value: Any,
        name: str,
        *,
        minimum: int,
    ) -> int:
        """Parse an exactly integral finite scalar with a fixed lower bound."""

        parsed = cls._finite_real_scalar(value, name)
        if not parsed.is_integer() or parsed < minimum:
            qualifier = "positive" if minimum == 1 else "nonnegative"
            raise ValueError(f"{name} must be a {qualifier} integer")
        return int(parsed)

    def __init__(
        self,
        dimension: int,
        *,
        learning_rate: float = 0.08,
        training: bool = False,
    ) -> None:
        parsed_dimension = self._integer_scalar(
            dimension,
            "dimension",
            minimum=1,
        )
        parsed_learning_rate = self._finite_real_scalar(
            learning_rate,
            "learning_rate",
        )
        if not 0.0 < parsed_learning_rate <= 2.0:
            raise ValueError("learning_rate must lie in (0, 2]")
        if not isinstance(training, (bool, np.bool_)):
            raise ValueError("training must be boolean")
        self.dimension = parsed_dimension
        self.learning_rate = parsed_learning_rate
        self.weights = 0.8 * np.eye(self.dimension, dtype=np.float64)
        self.bias = np.zeros(self.dimension, dtype=np.float64)
        self.training = bool(training)
        self.learning_steps = 0
        self.observed_count = 0
        self.last_observation = np.zeros(self.dimension, dtype=np.float64)
        self.last_prediction = np.zeros(self.dimension, dtype=np.float64)
        self.last_error = np.zeros(self.dimension, dtype=np.float64)

    def train(self) -> None:
        self.training = True

    def freeze(self) -> None:
        self.training = False

    def reset(self) -> None:
        self.observed_count = 0
        self.last_observation.fill(0.0)
        self.last_prediction.fill(0.0)
        self.last_error.fill(0.0)

    def observe(self, observation: ArrayLike) -> FloatArray:
        value = _vector(observation, self.dimension, "observation")
        if self.observed_count == 0:
            prediction = np.zeros(self.dimension, dtype=np.float64)
            error = value.copy()
        else:
            with np.errstate(over="ignore", invalid="ignore"):
                linear = self.weights @ self.last_observation + self.bias
            if not np.all(np.isfinite(linear)):
                raise FloatingPointError(
                    "observation-forecaster linear prediction became nonfinite"
                )
            prediction = np.tanh(linear)
            error = value - prediction
            if self.training:
                with np.errstate(over="ignore", invalid="ignore"):
                    derivative_error = error * (1.0 - np.square(prediction))
                    denominator = self.NORMALIZED_LMS_EPSILON + float(
                        self.last_observation @ self.last_observation
                    ) + 1.0
                    weight_correction = self.learning_rate * np.outer(
                        derivative_error, self.last_observation
                    ) / denominator
                    bias_correction = (
                        self.learning_rate * derivative_error / denominator
                    )
                    next_weights = self.weights + weight_correction
                    next_bias = self.bias + bias_correction
                if (
                    not np.isfinite(denominator)
                    or not np.all(np.isfinite(next_weights))
                    or not np.all(np.isfinite(next_bias))
                ):
                    raise FloatingPointError(
                        "observation-forecaster update became nonfinite"
                    )
                self.weights = next_weights
                self.bias = next_bias
                self.learning_steps += 1
        self.last_observation = value.copy()
        self.last_prediction = prediction.copy()
        self.last_error = error.copy()
        self.observed_count += 1
        return prediction.copy()

    def forecast(self, horizon: int) -> FloatArray:
        parsed_horizon = self._integer_scalar(horizon, "horizon", minimum=1)
        if self.observed_count == 0:
            raise RuntimeError("forecast requires at least one observation")
        current = self.last_observation.copy()
        values = []
        for _ in range(parsed_horizon):
            with np.errstate(over="ignore", invalid="ignore"):
                linear = self.weights @ current + self.bias
            if not np.all(np.isfinite(linear)):
                raise FloatingPointError(
                    "observation-forecaster forecast became nonfinite"
                )
            current = np.tanh(linear)
            values.append(current.copy())
        return np.stack(values)

    def snapshot(self) -> dict[str, Any]:
        return {
            "schema": self.SNAPSHOT_SCHEMA,
            "dimension": self.dimension,
            "model_order": self.MODEL_ORDER,
            "activation": self.ACTIVATION,
            "update_rule": self.UPDATE_RULE,
            "normalized_lms_epsilon": self.NORMALIZED_LMS_EPSILON,
            "dtype": self.SNAPSHOT_DTYPE,
            "weights": self.weights.copy(),
            "bias": self.bias.copy(),
            "learning_steps": int(self.learning_steps),
            "learning_rate": self.learning_rate,
        }

    def load_snapshot(
        self,
        snapshot: Mapping[str, Any],
        *,
        freeze: bool = True,
    ) -> None:
        if not isinstance(snapshot, Mapping):
            raise TypeError("observation-forecaster snapshot must be a mapping")
        if not isinstance(freeze, (bool, np.bool_)):
            raise ValueError("freeze must be boolean")
        required = {
            "schema",
            "dimension",
            "model_order",
            "activation",
            "update_rule",
            "normalized_lms_epsilon",
            "dtype",
            "weights",
            "bias",
            "learning_steps",
            "learning_rate",
        }
        missing = sorted(required.difference(snapshot))
        if missing:
            raise ValueError(
                "observation-forecaster snapshot is missing required fields: "
                + ", ".join(missing)
            )
        if snapshot["schema"] != self.SNAPSHOT_SCHEMA:
            raise ValueError("unsupported observation-forecaster snapshot schema")
        snapshot_dimension = self._integer_scalar(
            snapshot["dimension"],
            "snapshot dimension",
            minimum=1,
        )
        if snapshot_dimension != self.dimension:
            raise ValueError("observation-forecaster snapshot dimension mismatch")
        model_order = self._integer_scalar(
            snapshot["model_order"],
            "snapshot model_order",
            minimum=1,
        )
        if model_order != self.MODEL_ORDER:
            raise ValueError("unsupported observation-forecaster model order")
        if snapshot["activation"] != self.ACTIVATION:
            raise ValueError("unsupported observation-forecaster activation")
        if snapshot["update_rule"] != self.UPDATE_RULE:
            raise ValueError("unsupported observation-forecaster update rule")
        epsilon = self._finite_real_scalar(
            snapshot["normalized_lms_epsilon"],
            "snapshot normalized_lms_epsilon",
        )
        if epsilon != self.NORMALIZED_LMS_EPSILON:
            raise ValueError("observation-forecaster epsilon mismatch")
        if snapshot["dtype"] != self.SNAPSHOT_DTYPE:
            raise ValueError("unsupported observation-forecaster snapshot dtype")
        learning_rate = self._finite_real_scalar(
            snapshot["learning_rate"],
            "snapshot learning_rate",
        )
        if not 0.0 < learning_rate <= 2.0:
            raise ValueError("snapshot learning_rate must lie in (0, 2]")
        learning_steps = self._integer_scalar(
            snapshot["learning_steps"],
            "snapshot learning_steps",
            minimum=0,
        )
        try:
            weights = np.asarray(snapshot["weights"], dtype=np.float64)
            bias = np.asarray(snapshot["bias"], dtype=np.float64)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError(
                "invalid observation-forecaster snapshot arrays"
            ) from exc
        if (
            weights.shape != (self.dimension, self.dimension)
            or bias.shape != (self.dimension,)
        ):
            raise ValueError("invalid observation-forecaster snapshot shape")
        if not np.all(np.isfinite(weights)) or not np.all(np.isfinite(bias)):
            raise ValueError("observation-forecaster snapshot must be finite")

        # Mutate only after the complete snapshot has passed validation.
        self.weights = weights.copy()
        self.bias = bias.copy()
        self.learning_steps = learning_steps
        self.learning_rate = learning_rate
        self.reset()
        self.training = not bool(freeze)


def _regularized_incomplete_beta(a: float, b: float, x: float) -> float:
    """Evaluate the regularized incomplete beta without a SciPy dependency."""

    if not a > 0.0 or not b > 0.0 or not 0.0 <= x <= 1.0:
        raise ValueError("invalid regularized incomplete beta arguments")
    if x == 0.0:
        return 0.0
    if x == 1.0:
        return 1.0

    def continued_fraction(left: float, right: float, value: float) -> float:
        maximum_iterations = 256
        epsilon = 3e-14
        floor = 1e-300
        qab = left + right
        qap = left + 1.0
        qam = left - 1.0
        c = 1.0
        d = 1.0 - qab * value / qap
        if abs(d) < floor:
            d = floor
        d = 1.0 / d
        result = d
        for iteration in range(1, maximum_iterations + 1):
            doubled = 2 * iteration
            coefficient = (
                iteration
                * (right - iteration)
                * value
                / ((qam + doubled) * (left + doubled))
            )
            d = 1.0 + coefficient * d
            if abs(d) < floor:
                d = floor
            c = 1.0 + coefficient / c
            if abs(c) < floor:
                c = floor
            d = 1.0 / d
            result *= d * c
            coefficient = -(
                (left + iteration)
                * (qab + iteration)
                * value
                / ((left + doubled) * (qap + doubled))
            )
            d = 1.0 + coefficient * d
            if abs(d) < floor:
                d = floor
            c = 1.0 + coefficient / c
            if abs(c) < floor:
                c = floor
            d = 1.0 / d
            multiplier = d * c
            result *= multiplier
            if abs(multiplier - 1.0) <= epsilon:
                return result
        raise ArithmeticError("incomplete-beta continued fraction did not converge")

    log_factor = (
        math.lgamma(a + b)
        - math.lgamma(a)
        - math.lgamma(b)
        + a * math.log(x)
        + b * math.log1p(-x)
    )
    factor = math.exp(log_factor)
    if x < (a + 1.0) / (a + b + 2.0):
        value = factor * continued_fraction(a, b, x) / a
    else:
        value = 1.0 - factor * continued_fraction(b, a, 1.0 - x) / b
    return float(min(1.0, max(0.0, value)))


@dataclass(frozen=True)
class BayesianTransferPrediction:
    """Posterior-predictive Student-t summary for one transfer query."""

    mean: float
    scale_squared: float
    variance: float
    aleatoric_variance: float
    epistemic_variance: float
    degrees_of_freedom: float

    def cdf(self, value: float) -> float:
        """Return the predictive Student-t CDF at ``value``."""

        if isinstance(value, (bool, np.bool_)) or not np.isscalar(value):
            raise ValueError("CDF value must be a finite real scalar")
        parsed = float(value)
        if not np.isfinite(parsed):
            raise ValueError("CDF value must be a finite real scalar")
        standardized = (parsed - self.mean) / math.sqrt(self.scale_squared)
        if standardized == 0.0:
            return 0.5
        ratio = self.degrees_of_freedom / (
            self.degrees_of_freedom + standardized * standardized
        )
        tail = 0.5 * _regularized_incomplete_beta(
            0.5 * self.degrees_of_freedom,
            0.5,
            ratio,
        )
        return float(tail if standardized < 0.0 else 1.0 - tail)

    def probability_above(self, value: float = 0.0) -> float:
        """Return posterior-predictive probability strictly above ``value``."""

        return float(1.0 - self.cdf(value))

    def quantile(self, probability: float) -> float:
        """Invert the predictive CDF deterministically by bracketed bisection."""

        if (
            isinstance(probability, (bool, np.bool_))
            or not np.isscalar(probability)
            or not np.isfinite(probability)
            or not 0.0 < float(probability) < 1.0
        ):
            raise ValueError("probability must lie strictly between zero and one")
        target = float(probability)
        scale = math.sqrt(self.scale_squared)
        radius = scale
        lower = self.mean - radius
        upper = self.mean + radius
        for _ in range(64):
            if self.cdf(lower) <= target <= self.cdf(upper):
                break
            radius *= 2.0
            lower = self.mean - radius
            upper = self.mean + radius
        else:
            raise ArithmeticError("failed to bracket Student-t quantile")
        for _ in range(96):
            midpoint = 0.5 * (lower + upper)
            if self.cdf(midpoint) < target:
                lower = midpoint
            else:
                upper = midpoint
        return float(0.5 * (lower + upper))

    def lower_bound(self, confidence: float) -> float:
        """Return a one-sided posterior-predictive lower credible bound."""

        if (
            isinstance(confidence, (bool, np.bool_))
            or not np.isscalar(confidence)
            or not np.isfinite(confidence)
            or not 0.5 < float(confidence) < 1.0
        ):
            raise ValueError("confidence must lie strictly between 0.5 and 1")
        return self.quantile(1.0 - float(confidence))


class BayesianCausalTransferModel:
    """Exact Normal-Inverse-Gamma regression over paired causal outcomes.

    This is Bayesian conditional prediction, not causal identification by
    itself.  Transfer semantics require targets from paired or randomized
    interventions.  Fractional weights form a declared generalized-Bayes
    likelihood, so candidates sharing one revealed future may sum to one
    effective evidence unit.
    """

    SNAPSHOT_SCHEMA = "rrct.bayesian_causal_transfer.v1"
    IMPLEMENTATION_VERSION = 1
    LIKELIHOOD = "gaussian_power_likelihood"
    PRIOR = "normal_inverse_gamma"
    SNAPSHOT_DTYPE = "float64"
    LOAD_TOLERANCE = 1e-10

    @staticmethod
    def _finite_real_scalar(value: Any, name: str) -> float:
        if isinstance(value, (bool, np.bool_)) or not np.isscalar(value):
            raise ValueError(f"{name} must be a finite real scalar")
        array = np.asarray(value)
        if array.dtype.kind not in "iuf":
            raise ValueError(f"{name} must be a finite real scalar")
        parsed = float(value)
        if not np.isfinite(parsed):
            raise ValueError(f"{name} must be a finite real scalar")
        return parsed

    @classmethod
    def _integer_scalar(cls, value: Any, name: str, *, minimum: int) -> int:
        parsed = cls._finite_real_scalar(value, name)
        if not parsed.is_integer() or parsed < minimum:
            raise ValueError(f"{name} must be an integer no smaller than {minimum}")
        return int(parsed)

    @staticmethod
    def _array_digest(array: FloatArray) -> str:
        contiguous = np.ascontiguousarray(array, dtype=np.float64)
        prefix = repr((str(contiguous.dtype), tuple(contiguous.shape))).encode()
        return hashlib.sha256(prefix + contiguous.tobytes(order="C")).hexdigest()

    def __init__(
        self,
        feature_dim: int,
        *,
        include_intercept: bool = False,
        feature_bound: float = 1.0,
        target_bound: float = 1.0,
        prior_precision: float = 1.0,
        prior_shape: float = 2.0,
        prior_scale: float = 1.0,
        coordinate_names: tuple[str, ...] | None = None,
        training: bool = False,
    ) -> None:
        self.feature_dim = self._integer_scalar(feature_dim, "feature_dim", minimum=1)
        if not isinstance(include_intercept, (bool, np.bool_)):
            raise ValueError("include_intercept must be boolean")
        if not isinstance(training, (bool, np.bool_)):
            raise ValueError("training must be boolean")
        self.include_intercept = bool(include_intercept)
        self.design_dim = self.feature_dim + int(self.include_intercept)
        self.feature_bound = self._finite_real_scalar(feature_bound, "feature_bound")
        self.target_bound = self._finite_real_scalar(target_bound, "target_bound")
        self.prior_precision = self._finite_real_scalar(prior_precision, "prior_precision")
        self.prior_shape = self._finite_real_scalar(prior_shape, "prior_shape")
        self.prior_scale = self._finite_real_scalar(prior_scale, "prior_scale")
        if self.feature_bound <= 0.0 or self.target_bound <= 0.0:
            raise ValueError("feature and target bounds must be positive")
        if self.prior_precision <= 0.0:
            raise ValueError("prior_precision must be positive")
        if self.prior_shape <= 1.0:
            raise ValueError("prior_shape must exceed one")
        if self.prior_scale <= 0.0:
            raise ValueError("prior_scale must be positive")
        if coordinate_names is None:
            coordinate_names = tuple(
                f"feature_{index:02d}" for index in range(self.feature_dim)
            )
        if (
            not isinstance(coordinate_names, tuple)
            or len(coordinate_names) != self.feature_dim
            or any(not isinstance(name, str) or not name for name in coordinate_names)
            or len(set(coordinate_names)) != len(coordinate_names)
        ):
            raise ValueError("coordinate_names must be unique nonempty names")
        self.coordinate_names = tuple(coordinate_names)
        self.prior_mean = np.zeros(self.design_dim, dtype=np.float64)
        self.prior_precision_matrix = self.prior_precision * np.eye(
            self.design_dim, dtype=np.float64
        )
        self.sum_xx = np.zeros((self.design_dim, self.design_dim), dtype=np.float64)
        self.sum_xy = np.zeros(self.design_dim, dtype=np.float64)
        self.sum_yy = 0.0
        self.observation_count = 0
        self.effective_sample_count = 0.0
        self.training = bool(training)

    def train(self) -> None:
        self.training = True

    def freeze(self) -> None:
        self.training = False

    def reset(self) -> None:
        self.sum_xx.fill(0.0)
        self.sum_xy.fill(0.0)
        self.sum_yy = 0.0
        self.observation_count = 0
        self.effective_sample_count = 0.0

    def _features(self, values: ArrayLike) -> FloatArray:
        try:
            features = np.asarray(values, dtype=np.float64)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError("features must be a finite real vector") from exc
        if features.shape != (self.feature_dim,):
            raise ValueError(
                f"features must have shape ({self.feature_dim},), got {features.shape}"
            )
        if not np.all(np.isfinite(features)):
            raise ValueError("features must contain only finite values")
        if np.any(np.abs(features) > self.feature_bound):
            raise ValueError("features exceed the declared bound")
        if self.include_intercept:
            return np.concatenate((np.ones(1, dtype=np.float64), features))
        return features.copy()

    def _posterior(
        self,
        *,
        sum_xx: FloatArray | None = None,
        sum_xy: FloatArray | None = None,
        sum_yy: float | None = None,
        effective_sample_count: float | None = None,
    ) -> tuple[FloatArray, FloatArray, float, float]:
        xx = self.sum_xx if sum_xx is None else sum_xx
        xy = self.sum_xy if sum_xy is None else sum_xy
        yy = self.sum_yy if sum_yy is None else float(sum_yy)
        effective = (
            self.effective_sample_count
            if effective_sample_count is None
            else float(effective_sample_count)
        )
        precision = self.prior_precision_matrix + xx
        try:
            np.linalg.cholesky(precision)
            mean = np.linalg.solve(
                precision,
                self.prior_precision_matrix @ self.prior_mean + xy,
            )
        except np.linalg.LinAlgError as exc:
            raise FloatingPointError("posterior precision is not positive definite") from exc
        shape = self.prior_shape + 0.5 * effective
        scale = self.prior_scale + 0.5 * (
            yy
            + float(self.prior_mean @ self.prior_precision_matrix @ self.prior_mean)
            - float(mean @ precision @ mean)
        )
        if (
            not np.all(np.isfinite(precision))
            or not np.all(np.isfinite(mean))
            or not np.isfinite(shape)
            or not np.isfinite(scale)
            or shape <= 1.0
            or scale <= 0.0
        ):
            raise FloatingPointError("Bayesian posterior became invalid")
        return precision, mean, float(shape), float(scale)

    def observe(
        self,
        features: ArrayLike,
        target: float,
        *,
        weight: float = 1.0,
    ) -> bool:
        """Condition on one revealed outcome, or do nothing while frozen."""

        design = self._features(features)
        value = self._finite_real_scalar(target, "target")
        parsed_weight = self._finite_real_scalar(weight, "weight")
        if abs(value) > self.target_bound:
            raise ValueError("target exceeds the declared bound")
        if not 0.0 < parsed_weight <= 1.0:
            raise ValueError("weight must lie in (0, 1]")
        if not self.training:
            return False
        next_xx = self.sum_xx + parsed_weight * np.outer(design, design)
        next_xy = self.sum_xy + parsed_weight * design * value
        next_yy = self.sum_yy + parsed_weight * value * value
        next_effective = self.effective_sample_count + parsed_weight
        self._posterior(
            sum_xx=next_xx,
            sum_xy=next_xy,
            sum_yy=next_yy,
            effective_sample_count=next_effective,
        )
        self.sum_xx = next_xx
        self.sum_xy = next_xy
        self.sum_yy = float(next_yy)
        self.observation_count += 1
        self.effective_sample_count = float(next_effective)
        return True

    def observe_batch(
        self,
        features: ArrayLike,
        targets: ArrayLike,
        *,
        weights: ArrayLike | None = None,
    ) -> int:
        """Transactionally condition on a batch of bounded observations."""

        try:
            feature_rows = np.asarray(features, dtype=np.float64)
            target_values = np.asarray(targets, dtype=np.float64)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError("batch values must be finite real arrays") from exc
        if feature_rows.ndim != 2 or feature_rows.shape[1:] != (self.feature_dim,):
            raise ValueError(f"features must have shape (n, {self.feature_dim})")
        if target_values.shape != (feature_rows.shape[0],):
            raise ValueError("targets must have shape (n,)")
        if feature_rows.shape[0] == 0:
            raise ValueError("batch must contain at least one observation")
        if weights is None:
            weight_values = np.ones(feature_rows.shape[0], dtype=np.float64)
        else:
            try:
                weight_values = np.asarray(weights, dtype=np.float64)
            except (TypeError, ValueError, OverflowError) as exc:
                raise ValueError("weights must be a finite real vector") from exc
        if weight_values.shape != (feature_rows.shape[0],):
            raise ValueError("weights must have shape (n,)")
        designs = np.stack([self._features(row) for row in feature_rows])
        if (
            not np.all(np.isfinite(target_values))
            or np.any(np.abs(target_values) > self.target_bound)
            or not np.all(np.isfinite(weight_values))
            or np.any(weight_values <= 0.0)
            or np.any(weight_values > 1.0)
        ):
            raise ValueError("batch targets or weights violate declared bounds")
        if not self.training:
            return 0
        weighted_designs = designs * weight_values[:, None]
        next_xx = self.sum_xx + designs.T @ weighted_designs
        next_xy = self.sum_xy + designs.T @ (weight_values * target_values)
        next_yy = self.sum_yy + float(np.sum(weight_values * np.square(target_values)))
        next_effective = self.effective_sample_count + float(np.sum(weight_values))
        self._posterior(
            sum_xx=next_xx,
            sum_xy=next_xy,
            sum_yy=next_yy,
            effective_sample_count=next_effective,
        )
        self.sum_xx = np.asarray(next_xx, dtype=np.float64)
        self.sum_xy = np.asarray(next_xy, dtype=np.float64)
        self.sum_yy = float(next_yy)
        self.observation_count += int(feature_rows.shape[0])
        self.effective_sample_count = float(next_effective)
        return int(feature_rows.shape[0])

    def predict(self, features: ArrayLike) -> BayesianTransferPrediction:
        design = self._features(features)
        precision, mean, shape, scale = self._posterior()
        try:
            solved = np.linalg.solve(precision, design)
        except np.linalg.LinAlgError as exc:
            raise FloatingPointError("posterior precision solve failed") from exc
        leverage = float(design @ solved)
        if leverage < -1e-12:
            raise FloatingPointError("posterior leverage became negative")
        leverage = max(0.0, leverage)
        noise_variance = scale / (shape - 1.0)
        epistemic_variance = noise_variance * leverage
        variance = noise_variance + epistemic_variance
        scale_squared = scale / shape * (1.0 + leverage)
        values = (
            float(design @ mean),
            scale_squared,
            variance,
            noise_variance,
            epistemic_variance,
            2.0 * shape,
        )
        if not np.all(np.isfinite(values)) or min(values[1:]) < 0.0:
            raise FloatingPointError("posterior prediction became invalid")
        return BayesianTransferPrediction(
            mean=values[0],
            scale_squared=values[1],
            variance=values[2],
            aleatoric_variance=values[3],
            epistemic_variance=values[4],
            degrees_of_freedom=values[5],
        )

    def posterior_digest(self) -> str:
        return str(self.snapshot()["posterior_digest"])

    def snapshot(self) -> dict[str, Any]:
        precision, mean, shape, scale = self._posterior()
        arrays = {
            "prior_mean": self.prior_mean.copy(),
            "prior_precision_matrix": self.prior_precision_matrix.copy(),
            "sum_xx": self.sum_xx.copy(),
            "sum_xy": self.sum_xy.copy(),
            "posterior_precision": precision.copy(),
            "posterior_mean": mean.copy(),
        }
        snapshot: dict[str, Any] = {
            "schema": self.SNAPSHOT_SCHEMA,
            "implementation_version": self.IMPLEMENTATION_VERSION,
            "likelihood": self.LIKELIHOOD,
            "prior": self.PRIOR,
            "dtype": self.SNAPSHOT_DTYPE,
            "feature_dim": self.feature_dim,
            "design_dim": self.design_dim,
            "include_intercept": self.include_intercept,
            "coordinate_names": self.coordinate_names,
            "feature_bound": self.feature_bound,
            "target_bound": self.target_bound,
            "prior_precision": self.prior_precision,
            "prior_shape": self.prior_shape,
            "prior_scale": self.prior_scale,
            "sum_yy": self.sum_yy,
            "observation_count": self.observation_count,
            "effective_sample_count": self.effective_sample_count,
            "posterior_shape": shape,
            "posterior_scale": scale,
            "training": self.training,
            **arrays,
            "array_hashes": {
                name: self._array_digest(value) for name, value in arrays.items()
            },
        }
        payload = tuple(
            (name, snapshot[name])
            for name in sorted(snapshot)
            if name not in {"training", "posterior_digest"}
        )
        snapshot["posterior_digest"] = hashlib.sha256(repr(payload).encode()).hexdigest()
        return snapshot

    def load_snapshot(
        self,
        snapshot: Mapping[str, Any],
        *,
        freeze: bool = True,
    ) -> None:
        """Load a fully checked posterior without partially mutating on error."""

        if not isinstance(snapshot, Mapping):
            raise TypeError("Bayesian transfer snapshot must be a mapping")
        if not isinstance(freeze, (bool, np.bool_)):
            raise ValueError("freeze must be boolean")
        required = {
            "schema", "implementation_version", "likelihood", "prior", "dtype",
            "feature_dim", "design_dim", "include_intercept", "coordinate_names",
            "feature_bound", "target_bound", "prior_precision", "prior_shape",
            "prior_scale", "prior_mean", "prior_precision_matrix", "sum_xx",
            "sum_xy", "sum_yy", "observation_count", "effective_sample_count",
            "posterior_precision", "posterior_mean", "posterior_shape",
            "posterior_scale", "training", "array_hashes", "posterior_digest",
        }
        missing = sorted(required.difference(snapshot))
        if missing:
            raise ValueError(
                "Bayesian transfer snapshot is missing required fields: "
                + ", ".join(missing)
            )
        unexpected = sorted(set(snapshot).difference(required))
        if unexpected:
            raise ValueError(
                "Bayesian transfer snapshot has unknown fields: "
                + ", ".join(unexpected)
            )
        for name in ("schema", "likelihood", "prior", "dtype", "posterior_digest"):
            if not isinstance(snapshot[name], str):
                raise ValueError(f"Bayesian transfer snapshot {name} must be a string")
        for name in ("implementation_version", "feature_dim", "design_dim"):
            if isinstance(snapshot[name], (bool, np.bool_)) or not isinstance(
                snapshot[name], (int, np.integer)
            ):
                raise ValueError(f"Bayesian transfer snapshot {name} must be an integer")
        if not isinstance(snapshot["include_intercept"], (bool, np.bool_)):
            raise ValueError(
                "Bayesian transfer snapshot include_intercept must be boolean"
            )
        if not isinstance(snapshot["coordinate_names"], tuple):
            raise ValueError(
                "Bayesian transfer snapshot coordinate_names must be a tuple"
            )
        if not isinstance(snapshot["training"], (bool, np.bool_)):
            raise ValueError("Bayesian transfer snapshot training must be boolean")
        fixed = {
            "schema": self.SNAPSHOT_SCHEMA,
            "implementation_version": self.IMPLEMENTATION_VERSION,
            "likelihood": self.LIKELIHOOD,
            "prior": self.PRIOR,
            "dtype": self.SNAPSHOT_DTYPE,
            "feature_dim": self.feature_dim,
            "design_dim": self.design_dim,
            "include_intercept": self.include_intercept,
            "coordinate_names": self.coordinate_names,
        }
        for name, expected in fixed.items():
            if snapshot[name] != expected:
                raise ValueError(f"Bayesian transfer snapshot {name} mismatch")
        scalar_expected = {
            "feature_bound": self.feature_bound,
            "target_bound": self.target_bound,
            "prior_precision": self.prior_precision,
            "prior_shape": self.prior_shape,
            "prior_scale": self.prior_scale,
        }
        for name, expected in scalar_expected.items():
            if self._finite_real_scalar(snapshot[name], f"snapshot {name}") != expected:
                raise ValueError(f"Bayesian transfer snapshot {name} mismatch")
        if isinstance(snapshot["observation_count"], (bool, np.bool_)) or not isinstance(
            snapshot["observation_count"], (int, np.integer)
        ):
            raise ValueError("snapshot observation_count must be a nonnegative integer")
        observation_count = int(snapshot["observation_count"])
        if observation_count < 0:
            raise ValueError("snapshot observation_count must be a nonnegative integer")
        effective = self._finite_real_scalar(
            snapshot["effective_sample_count"], "snapshot effective_sample_count"
        )
        if effective < 0.0 or effective > observation_count + self.LOAD_TOLERANCE:
            raise ValueError("invalid effective sample count")
        if observation_count == 0 and effective != 0.0:
            raise ValueError("empty snapshot must have zero effective sample count")
        array_shapes = {
            "prior_mean": (self.design_dim,),
            "prior_precision_matrix": (self.design_dim, self.design_dim),
            "sum_xx": (self.design_dim, self.design_dim),
            "sum_xy": (self.design_dim,),
            "posterior_precision": (self.design_dim, self.design_dim),
            "posterior_mean": (self.design_dim,),
        }
        arrays: dict[str, FloatArray] = {}
        for name, shape_spec in array_shapes.items():
            try:
                value = np.asarray(snapshot[name], dtype=np.float64)
            except (TypeError, ValueError, OverflowError) as exc:
                raise ValueError(f"invalid snapshot array: {name}") from exc
            if value.shape != shape_spec or not np.all(np.isfinite(value)):
                raise ValueError(f"invalid snapshot array: {name}")
            arrays[name] = value.copy()
        hashes = snapshot["array_hashes"]
        if not isinstance(hashes, Mapping) or set(hashes) != set(arrays):
            raise ValueError("invalid Bayesian transfer array hashes")
        for name, value in arrays.items():
            if hashes[name] != self._array_digest(value):
                raise ValueError(f"Bayesian transfer snapshot hash mismatch: {name}")
        if not np.array_equal(arrays["prior_mean"], self.prior_mean) or not np.array_equal(
            arrays["prior_precision_matrix"], self.prior_precision_matrix
        ):
            raise ValueError("Bayesian transfer prior arrays mismatch")
        tolerance = self.LOAD_TOLERANCE
        if not np.allclose(arrays["sum_xx"], arrays["sum_xx"].T, atol=tolerance, rtol=0.0):
            raise ValueError("sum_xx must be symmetric")
        try:
            np.linalg.cholesky(arrays["prior_precision_matrix"])
            np.linalg.cholesky(arrays["posterior_precision"])
        except np.linalg.LinAlgError as exc:
            raise ValueError("snapshot precision must be positive definite") from exc
        if float(np.min(np.linalg.eigvalsh(arrays["sum_xx"]))) < -tolerance:
            raise ValueError("sum_xx must be positive semidefinite")
        sum_yy = self._finite_real_scalar(snapshot["sum_yy"], "snapshot sum_yy")
        if sum_yy < 0.0:
            raise ValueError("sum_yy must be nonnegative")
        augmented = np.block(
            [
                [arrays["sum_xx"], arrays["sum_xy"][:, None]],
                [arrays["sum_xy"][None, :], np.asarray([[sum_yy]])],
            ]
        )
        if float(np.min(np.linalg.eigvalsh(augmented))) < -tolerance:
            raise ValueError("snapshot moments are not jointly feasible")
        component_bound = np.full(self.design_dim, self.feature_bound)
        if self.include_intercept:
            component_bound[0] = 1.0
        if (
            np.any(
                np.diag(arrays["sum_xx"])
                > effective * np.square(component_bound) + tolerance
            )
            or np.any(
                np.abs(arrays["sum_xy"])
                > effective * component_bound * self.target_bound + tolerance
            )
            or sum_yy > effective * self.target_bound**2 + tolerance
        ):
            raise ValueError("snapshot moments exceed declared bounds")
        candidate = BayesianCausalTransferModel(
            self.feature_dim,
            include_intercept=self.include_intercept,
            feature_bound=self.feature_bound,
            target_bound=self.target_bound,
            prior_precision=self.prior_precision,
            prior_shape=self.prior_shape,
            prior_scale=self.prior_scale,
            coordinate_names=self.coordinate_names,
            training=False,
        )
        candidate.sum_xx = arrays["sum_xx"].copy()
        candidate.sum_xy = arrays["sum_xy"].copy()
        candidate.sum_yy = sum_yy
        candidate.observation_count = observation_count
        candidate.effective_sample_count = effective
        precision, mean, shape, scale = candidate._posterior()
        stored_shape = self._finite_real_scalar(
            snapshot["posterior_shape"], "snapshot posterior_shape"
        )
        stored_scale = self._finite_real_scalar(
            snapshot["posterior_scale"], "snapshot posterior_scale"
        )
        if (
            not np.allclose(precision, arrays["posterior_precision"], atol=tolerance, rtol=tolerance)
            or not np.allclose(mean, arrays["posterior_mean"], atol=tolerance, rtol=tolerance)
            or not np.isclose(shape, stored_shape, atol=tolerance, rtol=tolerance)
            or not np.isclose(scale, stored_scale, atol=tolerance, rtol=tolerance)
        ):
            raise ValueError("stored Bayesian posterior does not match moments")
        candidate_snapshot = candidate.snapshot()
        if snapshot["posterior_digest"] != candidate_snapshot["posterior_digest"]:
            raise ValueError("Bayesian transfer posterior digest mismatch")
        self.sum_xx = candidate.sum_xx.copy()
        self.sum_xy = candidate.sum_xy.copy()
        self.sum_yy = candidate.sum_yy
        self.observation_count = candidate.observation_count
        self.effective_sample_count = candidate.effective_sample_count
        self.training = not bool(freeze)


class EpisodicMemory:
    """A bounded temporal store with deterministic cosine retrieval."""

    def __init__(
        self,
        dimension: int,
        *,
        capacity: int = 64,
        top_k: int = 3,
        novelty_threshold: float = 0.02,
        temporal_decay: float = 0.9,
    ) -> None:
        if min(dimension, capacity, top_k) <= 0:
            raise ValueError("memory dimension, capacity, and top_k must be positive")
        if novelty_threshold < 0.0:
            raise ValueError("novelty_threshold must be nonnegative")
        if not 0.0 <= temporal_decay < 1.0:
            raise ValueError("temporal_decay must lie in [0, 1)")
        self.dimension = int(dimension)
        self.capacity = int(capacity)
        self.top_k = min(int(top_k), self.capacity)
        self.novelty_threshold = float(novelty_threshold)
        self.temporal_decay = float(temporal_decay)
        self._items = np.zeros((self.capacity, self.dimension), dtype=np.float64)
        self._times = np.full(self.capacity, -1, dtype=np.int64)
        self._sources: list[str | None] = [None] * self.capacity
        self._size = 0
        self._cursor = 0
        self._temporal_trace = np.zeros(self.dimension, dtype=np.float64)
        self._temporal_weight = 0.0

    def __len__(self) -> int:
        return self._size

    @property
    def size(self) -> int:
        """Number of occupied episodic slots."""

        return self._size

    def reset(self) -> None:
        """Remove all episodes."""

        self._items.fill(0.0)
        self._times.fill(-1)
        self._sources = [None] * self.capacity
        self._size = 0
        self._cursor = 0
        self._temporal_trace.fill(0.0)
        self._temporal_weight = 0.0

    def _active_indices(self) -> FloatArray:
        # The internal type is integer; a separate helper keeps the ring logic
        # out of retrieval and snapshot code.
        return np.flatnonzero(self._times >= 0)

    def retrieve(self, query: ArrayLike) -> MemoryRead:
        """Retrieve up to ``top_k`` similar episodes."""

        query_vector = _vector(query, self.dimension, "memory query")
        active = np.flatnonzero(self._times >= 0)
        if active.size == 0:
            return MemoryRead(
                vector=np.zeros(self.dimension, dtype=np.float64),
                indices=(),
                similarities=np.zeros(0, dtype=np.float64),
                weights=np.zeros(0, dtype=np.float64),
            )

        items = self._items[active]
        query_norm = max(float(np.linalg.norm(query_vector)), np.finfo(float).eps)
        item_norms = np.maximum(
            np.linalg.norm(items, axis=1), np.finfo(np.float64).eps
        )
        similarities = (items @ query_vector) / (item_norms * query_norm)
        order = np.lexsort((active, -similarities))[: self.top_k]
        chosen_indices = active[order]
        chosen_similarities = similarities[order]
        logits = chosen_similarities - float(np.max(chosen_similarities))
        weights = np.exp(logits)
        weights /= float(np.sum(weights))
        semantic_vector = np.sum(
            weights[:, None] * self._items[chosen_indices], axis=0
        )
        if self._temporal_weight:
            temporal_vector = self._temporal_trace / self._temporal_weight
            vector = 0.65 * semantic_vector + 0.35 * temporal_vector
        else:
            vector = semantic_vector
        return MemoryRead(
            vector=np.asarray(vector, dtype=np.float64),
            indices=tuple(int(index) for index in chosen_indices),
            similarities=np.asarray(chosen_similarities, dtype=np.float64),
            weights=np.asarray(weights, dtype=np.float64),
        )

    def novelty(self, item: ArrayLike) -> float:
        """Return one minus maximum cosine similarity to stored episodes."""

        vector = _vector(item, self.dimension, "memory item")
        if self._size == 0:
            return 1.0
        active = np.flatnonzero(self._times >= 0)
        items = self._items[active]
        norm = max(float(np.linalg.norm(vector)), np.finfo(np.float64).eps)
        item_norms = np.maximum(
            np.linalg.norm(items, axis=1), np.finfo(np.float64).eps
        )
        maximum = float(np.max((items @ vector) / (item_norms * norm)))
        return float(np.clip(1.0 - maximum, 0.0, 2.0))

    def write(self, item: ArrayLike, *, time: int, source: str = "external") -> bool:
        """Write a novel episode, returning whether storage occurred."""

        vector = _vector(item, self.dimension, "memory item")
        if float(np.linalg.norm(vector)) <= np.finfo(np.float64).eps:
            return False
        if self._size and self.novelty(vector) < self.novelty_threshold:
            return False
        index = self._cursor
        self._items[index] = vector
        self._times[index] = int(time)
        self._sources[index] = str(source)
        self._temporal_trace = (
            self.temporal_decay * self._temporal_trace + vector
        )
        self._temporal_weight = self.temporal_decay * self._temporal_weight + 1.0
        self._cursor = (self._cursor + 1) % self.capacity
        self._size = min(self._size + 1, self.capacity)
        return True

    def snapshot(self) -> dict[str, Any]:
        """Return copies of occupied storage and metadata."""

        active = np.flatnonzero(self._times >= 0)
        temporal_order = active[np.argsort(self._times[active], kind="stable")]
        return {
            "items": self._items[temporal_order].copy(),
            "times": self._times[temporal_order].copy(),
            "sources": tuple(self._sources[index] for index in temporal_order),
            "size": self._size,
            "capacity": self.capacity,
            "temporal_trace": (
                self._temporal_trace / self._temporal_weight
                if self._temporal_weight
                else np.zeros(self.dimension, dtype=np.float64)
            ).copy(),
        }


@dataclass(frozen=True)
class ControlDecision:
    """Counterfactual action and next-resolution selection."""

    action: FloatArray
    resolution_level: int
    action_scores: FloatArray
    resolution_scores: FloatArray


class CounterfactualController:
    """Select actions and resolution by simulating deterministic candidates.

    Candidate scores estimate prediction-error correction, information
    fidelity, and compute cost.  They are epistemic control scores, not rewards
    or subjective preference signals.
    """

    def __init__(
        self,
        observation_dim: int,
        workspace_dim: int,
        self_dim: int,
        action_dim: int,
        *,
        n_action_candidates: int = 7,
        seed: int | np.random.SeedSequence | None = 0,
    ) -> None:
        if min(observation_dim, workspace_dim, self_dim, action_dim) <= 0:
            raise ValueError("controller dimensions must be positive")
        if n_action_candidates < 3:
            raise ValueError("n_action_candidates must be at least three")
        self.observation_dim = int(observation_dim)
        self.workspace_dim = int(workspace_dim)
        self.self_dim = int(self_dim)
        self.action_dim = int(action_dim)
        self.n_action_candidates = int(n_action_candidates)

        rng = np.random.default_rng(seed)
        context_dim = 2 * self.workspace_dim + self.self_dim
        self._action_weights = _normalized_random_matrix(
            rng, self.action_dim, context_dim, gain=1.0
        )
        self._action_effect = _normalized_random_matrix(
            rng, self.workspace_dim, self.action_dim, gain=0.45
        )
        self._observation_model = _normalized_random_matrix(
            rng, self.workspace_dim, self.observation_dim, gain=0.9
        )
        self._self_model = _normalized_random_matrix(
            rng, self.workspace_dim, self.self_dim, gain=0.35
        )
        prototypes = rng.normal(size=(self.n_action_candidates - 3, self.action_dim))
        norms = np.maximum(np.linalg.norm(prototypes, axis=1, keepdims=True), 1e-12)
        self._action_prototypes = np.asarray(0.75 * prototypes / norms, dtype=np.float64)

    def choose(
        self,
        observation: ArrayLike,
        projectors: NestedOrthogonalProjectors,
        *,
        current_level: int,
        workspace: ArrayLike,
        self_state: ArrayLike,
        memory: ArrayLike,
        prediction_error: ArrayLike,
        resolution_enabled: bool = True,
    ) -> ControlDecision:
        """Evaluate action and resolution counterfactuals and choose maxima."""

        x = _vector(observation, self.observation_dim, "observation")
        workspace_vector = _vector(workspace, self.workspace_dim, "workspace")
        self_vector = _vector(self_state, self.self_dim, "self_state")
        memory_vector = _vector(memory, self.workspace_dim, "memory")
        error_vector = _vector(
            prediction_error, self.workspace_dim, "prediction_error"
        )

        context = np.concatenate((workspace_vector, self_vector, memory_vector))
        base_action = np.tanh(self._action_weights @ context)
        candidates = np.concatenate(
            (
                np.zeros((1, self.action_dim), dtype=np.float64),
                base_action[None, :],
                -base_action[None, :],
                self._action_prototypes,
            ),
            axis=0,
        )
        candidates = candidates[: self.n_action_candidates]
        corrected = error_vector[None, :] + candidates @ self._action_effect.T
        action_scores = -np.linalg.norm(corrected, axis=1)
        action_scores -= 0.05 * np.linalg.norm(candidates, axis=1)
        action_index = int(np.argmax(action_scores))
        action = np.asarray(candidates[action_index], dtype=np.float64)

        scale = max(float(np.linalg.norm(x)), np.finfo(np.float64).eps)
        # Relative prediction error drives a target information budget.  A
        # predictable trajectory may be processed coarsely, while surprise
        # recruits more detail.  The small floor prevents an almost-zero
        # workspace from turning harmless roundoff into maximal surprise.
        surprise = float(
            np.clip(
                np.linalg.norm(error_vector)
                / (np.linalg.norm(workspace_vector) + 0.25),
                0.0,
                2.0,
            )
        )
        target_cost = float(
            np.clip(0.12 + 0.80 * surprise / (surprise + 0.25), 0.08, 1.0)
        )
        resolution_scores = np.empty(len(projectors), dtype=np.float64)
        for level, rank in enumerate(projectors.ranks):
            projected = projectors.project(x, level)
            modeled_workspace = np.tanh(
                self._observation_model @ projected + self._self_model @ self_vector
            )
            model_disagreement = float(
                np.linalg.norm(modeled_workspace - workspace_vector)
                / np.sqrt(self.workspace_dim)
            )
            residual = float(np.linalg.norm(x - projected) / scale)
            fidelity = 1.0 - min(residual, 1.0)
            cost = rank / projectors.dimension
            transition = abs(level - current_level) / max(len(projectors) - 1, 1)
            resolution_scores[level] = (
                -abs(cost - target_cost)
                - (0.16 + 0.05 * surprise) * residual
                - 0.06 * model_disagreement
                + 0.03 * fidelity
                - 0.035 * transition
            )

        if resolution_enabled:
            resolution_level = int(np.argmax(resolution_scores))
        else:
            resolution_level = len(projectors) - 1
        return ControlDecision(
            action=action.copy(),
            resolution_level=resolution_level,
            action_scores=np.asarray(action_scores, dtype=np.float64),
            resolution_scores=resolution_scores.copy(),
        )


__all__ = [
    "BayesianCausalTransferModel",
    "BayesianTransferPrediction",
    "ControlDecision",
    "CounterfactualController",
    "EpisodicMemory",
    "FloatArray",
    "GlobalWorkspace",
    "MemoryRead",
    "NonValencedObservationForecaster",
    "NonValencedSelfModel",
    "SpecialistModule",
    "SpecialistOutput",
    "WorkspaceBroadcast",
    "balanced_matrix",
]
