"""Persistent orchestration for one continuously running RRCT causal loop.

The runtime in this module deliberately contains no hidden world, evaluator
labels, oracle projectors, or scenario schedule.  A caller supplies ordinary
observations, observable action candidates, subsequently realized external
returns, and an anonymous process bank.  The bank must be committed before
the agent emits the handle assignment with which it will be paired.  This
keeps the v0.31 commitment -> bind -> reveal chain intact and makes the rows
used by the drift monitor commitment blind by construction.

Only a workspace-gated :class:`PublicBoundaryCertificate` leaves the runtime.
The private learned boundary state is released only after its proposal wins
workspace access and the public access readout agrees with the attempted pair.
This is a capability gate, not a claim that the complete effect operator was
decoded from the low-dimensional workspace state.  Evaluator truth is never
used to construct the certificate.

This is an engineering integration layer.  It does not detect or establish
phenomenal awareness, sentience, valence, or moral status.
"""

from __future__ import annotations

import copy
import hashlib
import math
from collections import deque
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, fields, is_dataclass
from typing import Any, Literal

import numpy as np
from numpy.typing import ArrayLike, NDArray

from .agent import RRCTAgent, StepResult
from .causal_boundary import (
    BoundCausalTransition,
    CausalBoundaryUpdateReceipt,
    CausalHandleCommitment,
)

FloatArray = NDArray[np.float64]
PreferencePartition = Literal[
    "calibration", "audit_train", "audit_validation"
]


def _readonly(value: ArrayLike) -> FloatArray:
    result = np.asarray(value, dtype=np.float64).copy()
    result.setflags(write=False)
    return result


def _finite_scalar(value: Any, name: str) -> float:
    if isinstance(value, (bool, np.bool_)) or not np.isscalar(value):
        raise ValueError(f"{name} must be a finite real scalar")
    parsed = float(value)
    if not np.isfinite(parsed):
        raise ValueError(f"{name} must be a finite real scalar")
    return parsed


def _integer(value: Any, name: str, *, minimum: int = 0) -> int:
    if isinstance(value, (bool, np.bool_)) or not isinstance(
        value, (int, np.integer)
    ):
        raise TypeError(f"{name} must be an integer")
    parsed = int(value)
    if parsed < minimum:
        raise ValueError(f"{name} must be at least {minimum}")
    return parsed


def _vector(value: ArrayLike, dimension: int, name: str) -> FloatArray:
    try:
        result = np.asarray(value, dtype=np.float64)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must be a finite real vector") from exc
    if result.shape != (dimension,) or not np.all(np.isfinite(result)):
        raise ValueError(f"{name} must have finite shape ({dimension},)")
    return result.copy()


def _matrix(
    value: ArrayLike,
    shape: tuple[int, int],
    name: str,
) -> FloatArray:
    try:
        result = np.asarray(value, dtype=np.float64)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must be a finite real matrix") from exc
    if result.shape != shape or not np.all(np.isfinite(result)):
        raise ValueError(f"{name} must have finite shape {shape}")
    return result.copy()


def _digest_update(digest: Any, value: Any) -> None:
    if isinstance(value, np.ndarray):
        array = np.ascontiguousarray(value)
        digest.update(b"array\0")
        digest.update(array.dtype.str.encode("ascii"))
        digest.update(repr(tuple(int(x) for x in array.shape)).encode("ascii"))
        digest.update(array.tobytes(order="C"))
        return
    if is_dataclass(value):
        digest.update(b"dataclass\0")
        digest.update(type(value).__qualname__.encode("utf-8"))
        for item in fields(value):
            _digest_update(digest, item.name)
            _digest_update(digest, getattr(value, item.name))
        return
    if isinstance(value, Mapping):
        digest.update(b"mapping\0")
        for key in sorted(value, key=lambda item: repr(item)):
            _digest_update(digest, key)
            _digest_update(digest, value[key])
        return
    if isinstance(value, (tuple, list)):
        digest.update(b"sequence\0")
        for item in value:
            _digest_update(digest, item)
        return
    if isinstance(value, np.generic):
        value = value.item()
    digest.update(type(value).__qualname__.encode("utf-8"))
    digest.update(b"\0")
    digest.update(repr(value).encode("utf-8"))


def _digest(value: Any) -> str:
    result = hashlib.sha256()
    result.update(b"rrct.unified_causal_loop.v1\0")
    _digest_update(result, value)
    return result.hexdigest()


@dataclass(frozen=True)
class UnifiedCausalLoopConfig:
    """Truth-free runtime and online-learning constants."""

    context_dim: int = 0
    exploration_probability: float = 0.15
    policy_temperature: float = 0.35
    minimum_propensity: float = 0.01
    maximum_inverse_propensity: float = 20.0
    model_ridge: float = 0.50
    model_discount: float = 0.997
    transition_rollout_weight: float = 0.0
    candidate_value_bound: float = 1_000.0
    drift_capacity: int = 960
    drift_baseline_samples: int = 240
    drift_recent_samples: int = 240
    drift_fit_interval: int = 40
    drift_ridge: float = 0.50
    drift_threshold: float = 0.30
    quarantine_public_certificate_on_drift: bool = False
    criterion_channels: int = 7
    criterion_ridge: float = 0.30
    criterion_reopen_margin: float = 0.085
    seed: int = 360_036

    def __post_init__(self) -> None:
        if not isinstance(self.quarantine_public_certificate_on_drift, bool):
            raise TypeError(
                "quarantine_public_certificate_on_drift must be a bool"
            )
        for name, minimum in (
            ("context_dim", 0),
            ("drift_capacity", 1),
            ("drift_baseline_samples", 1),
            ("drift_recent_samples", 1),
            ("drift_fit_interval", 1),
            ("criterion_channels", 1),
            ("seed", 0),
        ):
            object.__setattr__(
                self, name, _integer(getattr(self, name), name, minimum=minimum)
            )
        if self.drift_baseline_samples > self.drift_capacity:
            raise ValueError("drift_baseline_samples exceeds drift_capacity")
        if self.drift_recent_samples > self.drift_capacity:
            raise ValueError("drift_recent_samples exceeds drift_capacity")
        for name in (
            "exploration_probability",
            "policy_temperature",
            "minimum_propensity",
            "maximum_inverse_propensity",
            "model_ridge",
            "model_discount",
            "transition_rollout_weight",
            "candidate_value_bound",
            "drift_ridge",
            "drift_threshold",
            "criterion_ridge",
            "criterion_reopen_margin",
        ):
            object.__setattr__(
                self, name, _finite_scalar(getattr(self, name), name)
            )
        if not 0.0 <= self.exploration_probability < 1.0:
            raise ValueError("exploration_probability must lie in [0, 1)")
        if self.policy_temperature <= 0.0:
            raise ValueError("policy_temperature must be positive")
        if not 0.0 < self.minimum_propensity < 0.5:
            raise ValueError("minimum_propensity must lie in (0, 0.5)")
        if self.maximum_inverse_propensity < 1.0:
            raise ValueError("maximum_inverse_propensity must be at least one")
        if self.model_ridge <= 0.0 or self.drift_ridge <= 0.0:
            raise ValueError("ridge constants must be positive")
        if not 0.0 < self.model_discount <= 1.0:
            raise ValueError("model_discount must lie in (0, 1]")
        if self.transition_rollout_weight < 0.0:
            raise ValueError("transition_rollout_weight must be nonnegative")
        if self.candidate_value_bound <= 0.0:
            raise ValueError("candidate_value_bound must be positive")
        if self.drift_threshold <= 0.0:
            raise ValueError("drift_threshold must be positive")
        if self.criterion_ridge <= 0.0:
            raise ValueError("criterion_ridge must be positive")
        if self.criterion_reopen_margin < 0.0:
            raise ValueError("criterion_reopen_margin must be nonnegative")


@dataclass(frozen=True)
class ProcessBankCommitment:
    """Anonymous process bank fixed before the next handle assignment."""

    sequence_id: int
    agent_time: int
    process_bank: FloatArray
    digest: str


@dataclass(frozen=True)
class PublicBoundaryCertificate:
    """Learned state released by a successful workspace/access capability gate.

    The tensor fields are copied from the learner's own admitted estimate after
    the gate opens; they are not claimed to be reconstructed from workspace
    activity.  No planted evaluator structure enters this object.
    """

    time: int
    pair: tuple[int, int]
    rank: int
    internal_projector: FloatArray
    sensory_projector: FloatArray
    effect_operator: FloatArray
    confidence: float
    uncertainty: float
    change_alarm: float
    epoch: int
    model_digest: str
    workspace_access_digest: str
    digest: str

    @property
    def structural_signature(self) -> tuple[tuple[int, int], int, int]:
        return self.pair, self.rank, self.epoch


@dataclass(frozen=True)
class PublicBoundaryGateReceipt:
    """Decision that turns a workspace-authorized certificate into action state.

    A commitment-blind drift alarm can quarantine the currently public
    structural signature.  The latch is fail-closed: the quarantined signature
    remains unavailable to the action path until the learner emits a different
    public structural signature.  This receipt exposes only public certificate
    metadata and the already public drift receipt.
    """

    time: int
    event: Literal["disabled", "empty", "pass", "entered", "held", "released"]
    raw_certificate_digest: str | None
    raw_signature: tuple[tuple[int, int], int, int] | None
    effective_certificate_digest: str | None
    effective_signature: tuple[tuple[int, int], int, int] | None
    quarantine_enabled: bool
    quarantine_active: bool
    quarantine_signature: tuple[tuple[int, int], int, int] | None
    trigger_drift_digest: str | None
    digest: str


@dataclass(frozen=True)
class ActionCandidate:
    """One observable candidate; no route truth or future outcome is accepted."""

    key: str
    action: FloatArray
    immediate_external_value: float = 0.0
    alternative_competence: float = 0.0
    preview_effect_operator: FloatArray | None = None


@dataclass(frozen=True)
class ActionSelectionReceipt:
    """Pre-outcome policy receipt with the exact logged propensities."""

    sequence_id: int
    time: int
    observation: FloatArray
    observable_context: FloatArray
    candidate_keys: tuple[str, ...]
    candidate_actions: FloatArray
    candidate_designs: FloatArray
    route_strengths: FloatArray
    predicted_next_observations: FloatArray
    predicted_external_returns: FloatArray
    counterfactual_no_certificate_returns: FloatArray
    public_boundary_value_advantage: float
    one_step_rollout_values: FloatArray
    one_step_rollout_best_next_keys: tuple[str, ...]
    transition_rollout_weight: float
    policy_scores: FloatArray
    propensities: FloatArray
    selected_index: int
    selected_key: str
    selected_action: FloatArray
    selected_propensity: float
    public_certificate_digest: str | None
    digest: str


@dataclass(frozen=True)
class ActionOutcomeReceipt:
    """Post-outcome update of the action-conditioned transition and critic."""

    selection_digest: str
    reveal_time: int
    realized_external_return: float | None
    predicted_external_return: float
    return_prediction_error: float | None
    transition_prediction_error: float
    inverse_propensity_weight: float
    transition_model_updated: bool
    return_model_updated: bool
    digest: str


@dataclass(frozen=True)
class RandomizedTransitionRow:
    """One commitment-blind row available to the interface drift monitor."""

    time: int
    observation: FloatArray
    process_bank: FloatArray
    handles: FloatArray
    next_observation: FloatArray
    commitment_digest: str
    process_bank_commitment_digest: str
    transition_digest: str
    action_selection_digest: str
    action_propensity: float
    public_certificate_digest: str | None
    digest: str


@dataclass(frozen=True)
class DriftAssessment:
    """Descriptive recent-versus-baseline causal-interface comparison."""

    time: int
    pair: tuple[int, int] | None
    rank: int
    baseline_samples: int
    recent_samples: int
    relative_drift: float
    baseline_norm: float
    recent_norm: float
    reopen_requested: bool
    reason: str
    digest: str


@dataclass(frozen=True)
class PreferenceCaseCommitment:
    """Anonymous evidence fixed before its verified effect is revealed."""

    sequence_id: int
    partition: PreferencePartition
    channels: FloatArray
    digest: str


@dataclass(frozen=True)
class PreferenceEffectReceipt:
    """Verified non-self effect paired with an earlier anonymous commitment."""

    commitment_digest: str
    verified_effect: float
    criterion_epoch: int
    digest: str


@dataclass(frozen=True)
class CriterionAuditReceipt:
    """Split-audit decision for the anonymous evidence-weighting criterion."""

    epoch_before: int
    epoch_after: int
    action: Literal["preserve", "reopen"]
    old_validation_mae: float
    challenger_validation_mae: float
    validation_improvement: float
    training_samples: int
    validation_samples: int
    old_weights: FloatArray
    challenger_weights: FloatArray
    adopted_weights: FloatArray
    digest: str


@dataclass(frozen=True)
class UnifiedStepReceipt:
    """Auditable result of one complete observe, decide, and bind cycle.

    ``causal_boundary_update`` is learner audit telemetry.  The runtime's
    action path consumes only ``public_boundary`` and the design sealed in
    ``action_selection``.
    """

    time: int
    action: FloatArray
    action_key: str
    action_propensity: float
    action_selection: ActionSelectionReceipt
    previous_action_outcome: ActionOutcomeReceipt | None
    causal_boundary_update: CausalBoundaryUpdateReceipt | None
    causal_commitment: CausalHandleCommitment
    process_bank_commitment_digest: str
    bound_transition: BoundCausalTransition
    public_boundary: PublicBoundaryCertificate | None
    public_boundary_gate: PublicBoundaryGateReceipt
    drift: DriftAssessment | None
    reopen_requested: bool
    randomized_row_count: int
    digest: str


@dataclass(frozen=True)
class UnifiedTerminalReceipt:
    """Auditable final reveal with no successor action or commitment."""

    time: int
    previous_action_outcome: ActionOutcomeReceipt
    causal_boundary_update: CausalBoundaryUpdateReceipt | None
    causal_transition_digest: str
    public_boundary: PublicBoundaryCertificate | None
    public_boundary_gate: PublicBoundaryGateReceipt
    drift: DriftAssessment | None
    reopen_requested: bool
    randomized_row_count: int
    closed: bool
    digest: str


class _DiscountedRidge:
    """Small persistent multi-output ridge model with causal sample weights."""

    def __init__(
        self,
        design_dim: int,
        target_dim: int,
        *,
        ridge: float,
        discount: float,
    ) -> None:
        self.design_dim = _integer(design_dim, "design_dim", minimum=1)
        self.target_dim = _integer(target_dim, "target_dim", minimum=1)
        self.ridge = _finite_scalar(ridge, "ridge")
        self.discount = _finite_scalar(discount, "discount")
        if self.ridge <= 0.0 or not 0.0 < self.discount <= 1.0:
            raise ValueError("invalid ridge model constants")
        self._sum_xx = np.zeros(
            (self.design_dim, self.design_dim), dtype=np.float64
        )
        self._sum_xy = np.zeros(
            (self.design_dim, self.target_dim), dtype=np.float64
        )
        self.observation_count = 0
        self.effective_sample_count = 0.0

    def coefficients(self) -> FloatArray:
        penalty = self.ridge * np.eye(self.design_dim, dtype=np.float64)
        penalty[0, 0] = min(self.ridge, 1e-8)
        try:
            coefficients = np.linalg.solve(
                self._sum_xx + penalty, self._sum_xy
            )
        except np.linalg.LinAlgError as exc:
            raise FloatingPointError("ridge model solve failed") from exc
        if not np.all(np.isfinite(coefficients)):
            raise FloatingPointError("ridge model coefficients became nonfinite")
        return np.asarray(coefficients, dtype=np.float64)

    def predict(self, design: ArrayLike) -> FloatArray:
        x = _vector(design, self.design_dim, "model design")
        prediction = np.asarray(x @ self.coefficients(), dtype=np.float64)
        if not np.all(np.isfinite(prediction)):
            raise FloatingPointError("ridge model prediction became nonfinite")
        return prediction

    def update(
        self,
        design: ArrayLike,
        target: ArrayLike,
        *,
        weight: float,
    ) -> None:
        x = _vector(design, self.design_dim, "model design")
        y = _vector(target, self.target_dim, "model target")
        w = _finite_scalar(weight, "model weight")
        if w <= 0.0:
            raise ValueError("model weight must be positive")
        next_xx = self.discount * self._sum_xx + w * np.outer(x, x)
        next_xy = self.discount * self._sum_xy + w * np.outer(x, y)
        if not np.all(np.isfinite(next_xx)) or not np.all(np.isfinite(next_xy)):
            raise FloatingPointError("ridge sufficient statistics became nonfinite")
        self._sum_xx = np.asarray(next_xx, dtype=np.float64)
        self._sum_xy = np.asarray(next_xy, dtype=np.float64)
        self.observation_count += 1
        self.effective_sample_count = (
            self.discount * self.effective_sample_count + w
        )

    def snapshot(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "schema": "rrct.unified.discounted_ridge.v1",
            "design_dim": self.design_dim,
            "target_dim": self.target_dim,
            "ridge": self.ridge,
            "discount": self.discount,
            "sum_xx": self._sum_xx.copy(),
            "sum_xy": self._sum_xy.copy(),
            "observation_count": self.observation_count,
            "effective_sample_count": self.effective_sample_count,
        }
        payload["digest"] = _digest(payload)
        return copy.deepcopy(payload)


class AnonymousMetaCriterion:
    """Persistent anonymous evidence-to-verified-effect criterion.

    Channel meanings are intentionally absent from the API.  A case is first
    committed to one declared split and only then paired with its verified
    external effect.  Initial fitting uses ``calibration`` rows.  An audit
    learns a challenger on ``audit_train`` rows and evaluates the preserve or
    reopen decision on disjoint ``audit_validation`` rows.
    """

    def __init__(
        self,
        channel_dim: int,
        *,
        ridge: float = 0.30,
        reopen_margin: float = 0.085,
    ) -> None:
        self.channel_dim = _integer(channel_dim, "channel_dim", minimum=1)
        self.ridge = _finite_scalar(ridge, "ridge")
        self.reopen_margin = _finite_scalar(reopen_margin, "reopen_margin")
        if self.ridge <= 0.0 or self.reopen_margin < 0.0:
            raise ValueError("invalid meta-criterion constants")
        self._rows: dict[PreferencePartition, list[FloatArray]] = {
            "calibration": [],
            "audit_train": [],
            "audit_validation": [],
        }
        self._targets: dict[PreferencePartition, list[float]] = {
            "calibration": [],
            "audit_train": [],
            "audit_validation": [],
        }
        self._pending: PreferenceCaseCommitment | None = None
        self._sequence_id = 0
        self._weights: FloatArray | None = None
        self._epoch = 0
        self._last_audit: CriterionAuditReceipt | None = None

    @property
    def epoch(self) -> int:
        return self._epoch

    @property
    def fitted(self) -> bool:
        return self._weights is not None

    @property
    def pending(self) -> bool:
        return self._pending is not None

    @staticmethod
    def _design(channels: FloatArray) -> FloatArray:
        return np.concatenate((np.ones(1, dtype=np.float64), channels))

    def _fit(self, rows: Sequence[FloatArray], targets: Sequence[float]) -> FloatArray:
        if not rows or len(rows) != len(targets):
            raise ValueError("criterion fit requires aligned nonempty evidence")
        x = np.vstack([self._design(row) for row in rows])
        y = np.asarray(targets, dtype=np.float64)
        penalty = self.ridge * np.eye(x.shape[1], dtype=np.float64)
        penalty[0, 0] = 1e-8
        try:
            weights = np.linalg.solve(x.T @ x + penalty, x.T @ y)
        except np.linalg.LinAlgError as exc:
            raise FloatingPointError("criterion ridge solve failed") from exc
        if not np.all(np.isfinite(weights)):
            raise FloatingPointError("criterion weights became nonfinite")
        return np.asarray(weights, dtype=np.float64)

    def commit_case(
        self,
        channels: ArrayLike,
        *,
        partition: PreferencePartition,
    ) -> PreferenceCaseCommitment:
        if partition not in self._rows:
            raise ValueError("unknown preference partition")
        if self._pending is not None:
            raise RuntimeError("a preference case is already awaiting reveal")
        values = _readonly(_vector(channels, self.channel_dim, "channels"))
        payload = {
            "schema": "rrct.unified.preference_case.v1",
            "sequence_id": self._sequence_id,
            "partition": partition,
            "channels": values,
        }
        commitment = PreferenceCaseCommitment(
            sequence_id=self._sequence_id,
            partition=partition,
            channels=values,
            digest=_digest(payload),
        )
        self._pending = commitment
        self._sequence_id += 1
        return copy.deepcopy(commitment)

    def reveal_effect(
        self,
        commitment: PreferenceCaseCommitment,
        verified_effect: float,
    ) -> PreferenceEffectReceipt:
        if not isinstance(commitment, PreferenceCaseCommitment):
            raise TypeError("commitment must be a PreferenceCaseCommitment")
        if self._pending is None:
            raise RuntimeError("no preference case is awaiting reveal")
        pending = self._pending
        if (
            commitment.sequence_id != pending.sequence_id
            or commitment.partition != pending.partition
            or commitment.digest != pending.digest
            or not np.array_equal(commitment.channels, pending.channels)
        ):
            raise ValueError("preference commitment does not match pending case")
        effect = _finite_scalar(verified_effect, "verified_effect")
        self._rows[pending.partition].append(pending.channels.copy())
        self._targets[pending.partition].append(effect)
        self._pending = None
        payload = {
            "schema": "rrct.unified.preference_effect.v1",
            "commitment_digest": pending.digest,
            "verified_effect": effect,
            "criterion_epoch": self._epoch,
        }
        return PreferenceEffectReceipt(
            commitment_digest=pending.digest,
            verified_effect=effect,
            criterion_epoch=self._epoch,
            digest=_digest(payload),
        )

    def fit_calibration(self, *, minimum_samples: int = 1) -> FloatArray:
        required = _integer(minimum_samples, "minimum_samples", minimum=1)
        if self._pending is not None:
            raise RuntimeError("cannot fit with an unrevealed preference case")
        if len(self._rows["calibration"]) < required:
            raise RuntimeError("insufficient calibration evidence")
        self._weights = self._fit(
            self._rows["calibration"], self._targets["calibration"]
        )
        return self._weights.copy()

    def predict_authority(self, channels: ArrayLike) -> float:
        if self._weights is None:
            raise RuntimeError("meta-criterion has not been fitted")
        values = _vector(channels, self.channel_dim, "channels")
        return float(self._design(values) @ self._weights)

    def audit(
        self,
        *,
        minimum_train_samples: int = 1,
        minimum_validation_samples: int = 1,
    ) -> CriterionAuditReceipt:
        if self._weights is None:
            raise RuntimeError("meta-criterion has not been fitted")
        if self._pending is not None:
            raise RuntimeError("cannot audit with an unrevealed preference case")
        train_required = _integer(
            minimum_train_samples, "minimum_train_samples", minimum=1
        )
        validation_required = _integer(
            minimum_validation_samples,
            "minimum_validation_samples",
            minimum=1,
        )
        train_rows = self._rows["audit_train"]
        train_targets = self._targets["audit_train"]
        validation_rows = self._rows["audit_validation"]
        validation_targets = self._targets["audit_validation"]
        if len(train_rows) < train_required or len(validation_rows) < validation_required:
            raise RuntimeError("insufficient split-audit evidence")
        challenger = self._fit(train_rows, train_targets)
        x_valid = np.vstack([self._design(row) for row in validation_rows])
        y_valid = np.asarray(validation_targets, dtype=np.float64)
        old_weights = self._weights.copy()
        old_mae = float(np.mean(np.abs(y_valid - x_valid @ old_weights)))
        challenger_mae = float(np.mean(np.abs(y_valid - x_valid @ challenger)))
        improvement = old_mae - challenger_mae
        action: Literal["preserve", "reopen"] = (
            "reopen" if improvement > self.reopen_margin else "preserve"
        )
        epoch_before = self._epoch
        adopted = challenger if action == "reopen" else old_weights
        if action == "reopen":
            self._weights = challenger.copy()
            self._epoch += 1
        payload = {
            "schema": "rrct.unified.criterion_audit.v1",
            "epoch_before": epoch_before,
            "epoch_after": self._epoch,
            "action": action,
            "old_validation_mae": old_mae,
            "challenger_validation_mae": challenger_mae,
            "validation_improvement": improvement,
            "training_samples": len(train_rows),
            "validation_samples": len(validation_rows),
            "old_weights": old_weights,
            "challenger_weights": challenger,
            "adopted_weights": adopted,
        }
        receipt = CriterionAuditReceipt(
            epoch_before=epoch_before,
            epoch_after=self._epoch,
            action=action,
            old_validation_mae=old_mae,
            challenger_validation_mae=challenger_mae,
            validation_improvement=improvement,
            training_samples=len(train_rows),
            validation_samples=len(validation_rows),
            old_weights=_readonly(old_weights),
            challenger_weights=_readonly(challenger),
            adopted_weights=_readonly(adopted),
            digest=_digest(payload),
        )
        self._last_audit = receipt
        self._rows["audit_train"].clear()
        self._targets["audit_train"].clear()
        self._rows["audit_validation"].clear()
        self._targets["audit_validation"].clear()
        return copy.deepcopy(receipt)

    def snapshot(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "schema": "rrct.unified.anonymous_meta_criterion.v1",
            "channel_dim": self.channel_dim,
            "ridge": self.ridge,
            "reopen_margin": self.reopen_margin,
            "sequence_id": self._sequence_id,
            "epoch": self._epoch,
            "weights": None if self._weights is None else self._weights.copy(),
            "rows": {
                key: [row.copy() for row in values]
                for key, values in self._rows.items()
            },
            "targets": copy.deepcopy(self._targets),
            "pending": copy.deepcopy(self._pending),
            "last_audit": copy.deepcopy(self._last_audit),
        }
        payload["digest"] = _digest(payload)
        return payload


class _CommitmentBlindDriftMonitor:
    """Fit baseline and recent effects from prospectively randomized rows."""

    def __init__(
        self,
        observation_dim: int,
        process_dim: int,
        source_count: int,
        handle_count: int,
        config: UnifiedCausalLoopConfig,
    ) -> None:
        self.observation_dim = observation_dim
        self.process_dim = process_dim
        self.source_count = source_count
        self.handle_count = handle_count
        self.config = config
        self._rows: deque[RandomizedTransitionRow] = deque(
            maxlen=config.drift_capacity
        )
        self._historical_certificate: PublicBoundaryCertificate | None = None
        self._baseline_signature: tuple[tuple[int, int], int, int] | None = None
        self._baseline_effect: FloatArray | None = None
        self._baseline_samples = 0
        self._last_fit_row_count = 0
        self._total_rows = 0
        self._last_assessment: DriftAssessment | None = None

    @property
    def row_count(self) -> int:
        return self._total_rows

    @property
    def last_assessment(self) -> DriftAssessment | None:
        return copy.deepcopy(self._last_assessment)

    def _minimum_identifiable_rows(self) -> int:
        nuisance = (
            1
            + self.observation_dim
            + self.source_count * self.process_dim
            + self.handle_count
        )
        return nuisance + self.process_dim + 1

    def _fit_effect(
        self,
        rows: Sequence[RandomizedTransitionRow],
        pair: tuple[int, int],
    ) -> FloatArray:
        handle_index, source_index = pair
        observation = np.stack([row.observation for row in rows])
        bank = np.stack([row.process_bank for row in rows])
        handles = np.stack([row.handles for row in rows])
        outcomes = np.stack([row.next_observation for row in rows])
        interaction = (
            handles[:, handle_index, None] * bank[:, source_index, :]
        )
        design = np.column_stack(
            (
                np.ones(len(rows), dtype=np.float64),
                observation,
                bank.reshape(len(rows), -1),
                handles,
                interaction,
            )
        )
        penalty = self.config.drift_ridge * np.eye(
            design.shape[1], dtype=np.float64
        )
        penalty[0, 0] = min(self.config.drift_ridge, 1e-8)
        try:
            coefficients = np.linalg.solve(
                design.T @ design + penalty, design.T @ outcomes
            )
        except np.linalg.LinAlgError as exc:
            raise FloatingPointError("drift effect fit failed") from exc
        return np.asarray(coefficients[-self.process_dim :, :], dtype=np.float64)

    def _set_baseline_if_ready(self) -> None:
        certificate = self._historical_certificate
        if certificate is None:
            return
        required = max(
            self.config.drift_baseline_samples,
            self._minimum_identifiable_rows(),
        )
        if len(self._rows) < required:
            return
        signature = certificate.structural_signature
        if self._baseline_signature == signature and self._baseline_effect is not None:
            return
        rows = list(self._rows)[-required:]
        self._baseline_effect = self._fit_effect(rows, certificate.pair)
        self._baseline_signature = signature
        self._baseline_samples = len(rows)
        self._last_fit_row_count = self._total_rows

    def update_public_certificate(
        self, certificate: PublicBoundaryCertificate | None
    ) -> None:
        if certificate is None:
            return
        if (
            self._historical_certificate is None
            or certificate.structural_signature
            != self._historical_certificate.structural_signature
        ):
            self._baseline_effect = None
            self._baseline_signature = None
            self._baseline_samples = 0
        self._historical_certificate = copy.deepcopy(certificate)
        self._set_baseline_if_ready()

    def observe(self, row: RandomizedTransitionRow) -> DriftAssessment | None:
        self._rows.append(copy.deepcopy(row))
        self._total_rows += 1
        self._set_baseline_if_ready()
        certificate = self._historical_certificate
        if certificate is None or self._baseline_effect is None:
            return None
        recent_required = max(
            self.config.drift_recent_samples,
            self._minimum_identifiable_rows(),
        )
        if len(self._rows) < recent_required:
            return None
        if (
            self._total_rows - self._last_fit_row_count
            < self.config.drift_fit_interval
        ):
            return None
        recent_rows = list(self._rows)[-recent_required:]
        recent_effect = self._fit_effect(recent_rows, certificate.pair)
        internal = certificate.internal_projector
        sensory = certificate.sensory_projector
        baseline_projected = internal @ self._baseline_effect @ sensory
        recent_projected = internal @ recent_effect @ sensory
        baseline_norm = float(np.linalg.norm(baseline_projected, ord="fro"))
        recent_norm = float(np.linalg.norm(recent_projected, ord="fro"))
        relative = float(
            np.linalg.norm(recent_projected - baseline_projected, ord="fro")
            / (baseline_norm + 1e-12)
        )
        reopen = bool(relative > self.config.drift_threshold)
        reason = "interface_drift" if reopen else "stable_interface"
        payload = {
            "schema": "rrct.unified.drift_assessment.v1",
            "time": row.time + 1,
            "pair": certificate.pair,
            "rank": certificate.rank,
            "baseline_samples": self._baseline_samples,
            "recent_samples": len(recent_rows),
            "relative_drift": relative,
            "baseline_norm": baseline_norm,
            "recent_norm": recent_norm,
            "reopen_requested": reopen,
            "reason": reason,
        }
        assessment = DriftAssessment(
            time=row.time + 1,
            pair=certificate.pair,
            rank=certificate.rank,
            baseline_samples=self._baseline_samples,
            recent_samples=len(recent_rows),
            relative_drift=relative,
            baseline_norm=baseline_norm,
            recent_norm=recent_norm,
            reopen_requested=reopen,
            reason=reason,
            digest=_digest(payload),
        )
        self._last_assessment = assessment
        self._last_fit_row_count = self._total_rows
        return copy.deepcopy(assessment)

    def snapshot(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "schema": "rrct.unified.commitment_blind_drift.v1",
            "total_rows": self._total_rows,
            "rows": tuple(copy.deepcopy(tuple(self._rows))),
            "historical_certificate": copy.deepcopy(self._historical_certificate),
            "baseline_signature": self._baseline_signature,
            "baseline_effect": (
                None
                if self._baseline_effect is None
                else self._baseline_effect.copy()
            ),
            "baseline_samples": self._baseline_samples,
            "last_fit_row_count": self._last_fit_row_count,
            "last_assessment": copy.deepcopy(self._last_assessment),
        }
        payload["digest"] = _digest(payload)
        return payload


@dataclass(frozen=True)
class _PendingRuntimeTransition:
    observation: FloatArray
    process_bank: ProcessBankCommitment
    handles: FloatArray
    causal_commitment_digest: str
    bound_transition_digest: str
    action_selection: ActionSelectionReceipt
    public_boundary: PublicBoundaryCertificate | None


class UnifiedCausalLoop:
    """Run one RRCT agent, causal boundary, critic, and audits without resets.

    The public cycle is intentionally two-stage:

    1. :meth:`precommit_process_bank` fixes the anonymous bank without access
       to the next handle assignment.
    2. :meth:`advance` reveals the preceding transition (when present), makes
       a workspace-mediated boundary certificate, chooses an action with an
       explicitly logged propensity, and binds the already-fixed bank to the
       newly emitted handle commitment.

    The observation and optional external return supplied to the following
    call are the post-outcome evidence for that action.  There is never more
    than one outstanding action or causal transition.

    Construction transfers logical ownership of ``agent`` to this runtime.
    Python cannot prevent a caller from retaining and mutating that reference;
    doing so is outside the API contract and is detected where receipt digests
    permit.  A future hardened boundary should enforce ownership rather than
    rely on this convention.
    """

    def __init__(
        self,
        agent: RRCTAgent,
        config: UnifiedCausalLoopConfig | None = None,
    ) -> None:
        if not isinstance(agent, RRCTAgent):
            raise TypeError("agent must be an RRCTAgent")
        if agent.causal_boundary is None or agent.causal_boundary_config is None:
            raise ValueError("UnifiedCausalLoop requires a causal-boundary agent")
        if agent.causal_boundary.has_pending:
            raise ValueError("agent must have no pending causal transition at startup")
        self._agent = agent
        self.config = config or UnifiedCausalLoopConfig()
        if not isinstance(self.config, UnifiedCausalLoopConfig):
            raise TypeError("config must be a UnifiedCausalLoopConfig")
        boundary = agent.causal_boundary_config
        if boundary.observation_dim != agent.observation_dim:
            raise ValueError("agent and causal-boundary observation dimensions differ")
        self.observation_dim = agent.observation_dim
        self.action_dim = agent.action_dim
        self.process_dim = boundary.process_dim
        self.source_count = boundary.source_count
        self.handle_count = boundary.handle_count
        # Seven scalar fields follow observation, context, and action:
        # immediate value, alternative competence, estimated route strength,
        # normalized rank, confidence, uncertainty, and change alarm.  The
        # remaining terms make action value conditional rather than additive:
        # action x context, action x observation, action squared, and action x
        # the five causal-certificate scalars (route plus four telemetry
        # values).  Public certificate presence and the public handle/source
        # pair are also encoded directly and crossed with action, so a remapped
        # motor port can acquire a distinct transition and value function.  A
        # three-way action x context x certificate-presence term represents a
        # payoff whose contextual action slope exists only after public access.
        # Without these products one linear critic cannot learn that the
        # preferred action reverses when context or boundary state changes.
        self._scalar_design_dim = 7
        self._certificate_scalar_dim = 5
        self._certificate_identity_dim = (
            1 + self.handle_count + self.source_count
        )
        self._interaction_design_dim = (
            self.action_dim * self.config.context_dim
            + self.action_dim * self.observation_dim
            + self.action_dim
            + self.action_dim * self._certificate_scalar_dim
            + self.action_dim * self.config.context_dim
            + self.action_dim * self._certificate_identity_dim
        )
        self._design_dim = (
            1
            + self.observation_dim
            + self.config.context_dim
            + self.action_dim
            + self._scalar_design_dim
            + self._certificate_identity_dim
            + self._interaction_design_dim
        )
        self._route_design_index = (
            1
            + self.observation_dim
            + self.config.context_dim
            + self.action_dim
            + 2
        )
        self._transition_model = _DiscountedRidge(
            self._design_dim,
            self.observation_dim,
            ridge=self.config.model_ridge,
            discount=self.config.model_discount,
        )
        self._return_model = _DiscountedRidge(
            self._design_dim,
            1,
            ridge=self.config.model_ridge,
            discount=self.config.model_discount,
        )
        self.meta_criterion = AnonymousMetaCriterion(
            self.config.criterion_channels,
            ridge=self.config.criterion_ridge,
            reopen_margin=self.config.criterion_reopen_margin,
        )
        self._drift = _CommitmentBlindDriftMonitor(
            self.observation_dim,
            self.process_dim,
            self.source_count,
            self.handle_count,
            self.config,
        )
        self._rng = np.random.default_rng(
            np.random.SeedSequence([self.config.seed, 36_036])
        )
        self._bank_sequence = 0
        self._action_sequence = 0
        self._precommitted_bank: ProcessBankCommitment | None = None
        self._pending_transition: _PendingRuntimeTransition | None = None
        self._public_boundary: PublicBoundaryCertificate | None = None
        self._last_transition_coefficients: FloatArray | None = None
        self._last_return_coefficients: FloatArray | None = None
        self._public_quarantine_signature: (
            tuple[tuple[int, int], int, int] | None
        ) = None
        self._last_step: UnifiedStepReceipt | None = None
        self._terminal_receipt: UnifiedTerminalReceipt | None = None
        self._closed = False

        minimum_drift_rows = (
            1
            + self.observation_dim
            + self.source_count * self.process_dim
            + self.handle_count
            + self.process_dim
            + 1
        )
        if self.config.drift_capacity < minimum_drift_rows:
            raise ValueError(
                "drift_capacity is too small for the identifiable drift design"
            )
        if (
            self.config.drift_baseline_samples > self.config.drift_capacity
            or self.config.drift_recent_samples > self.config.drift_capacity
        ):
            raise ValueError("drift sample windows exceed drift_capacity")

    @property
    def time(self) -> int:
        return self._agent.time

    @property
    def closed(self) -> bool:
        return self._closed

    @property
    def awaiting_process_bank(self) -> bool:
        return not self._closed and self._precommitted_bank is None

    @property
    def awaiting_outcome(self) -> bool:
        return self._pending_transition is not None

    @property
    def public_boundary(self) -> PublicBoundaryCertificate | None:
        return copy.deepcopy(self._public_boundary)

    @property
    def policy_model_coefficients(self) -> tuple[FloatArray, FloatArray]:
        """Return the model matrices frozen for the most recent action receipt.

        The matrices contain only the online transition and external-return
        models already used to produce the public action receipt.  They expose
        no private causal-boundary state or evaluator truth.  A caller can use
        them for matched, pre-outcome downstream controls without refitting
        additional models or mutating the live runtime.
        """

        if (
            self._last_transition_coefficients is None
            or self._last_return_coefficients is None
        ):
            raise RuntimeError("no action-selection model has been frozen yet")
        return (
            self._last_transition_coefficients.copy(),
            self._last_return_coefficients.copy(),
        )

    @property
    def last_step(self) -> UnifiedStepReceipt | None:
        return copy.deepcopy(self._last_step)

    @property
    def terminal_receipt(self) -> UnifiedTerminalReceipt | None:
        return copy.deepcopy(self._terminal_receipt)

    @property
    def randomized_row_count(self) -> int:
        return self._drift.row_count

    @property
    def continuity_weight(self) -> float:
        """Current learned coefficient on estimated causal-route strength."""

        coefficients = self._return_model.coefficients()
        return float(coefficients[self._route_design_index, 0])

    def _guard(self, operation: Any, /, *args: Any, **kwargs: Any) -> Any:
        """Permanently poison the wrapper if a post-step operation fails."""

        try:
            return operation(*args, **kwargs)
        except Exception:
            self._closed = True
            raise

    def precommit_process_bank(
        self, process_bank: ArrayLike
    ) -> ProcessBankCommitment:
        """Fix the next anonymous bank before the next handle assignment."""

        if self._closed:
            raise RuntimeError("unified causal loop is closed")
        if self._precommitted_bank is not None:
            raise RuntimeError("a process bank is already precommitted")
        if self._agent.causal_boundary is None:
            raise RuntimeError("causal-boundary component disappeared")
        if self._agent.causal_boundary.has_pending_commitment:
            raise RuntimeError(
                "bank precommitment must precede the next handle commitment"
            )
        bank = _readonly(
            _matrix(
                process_bank,
                (self.source_count, self.process_dim),
                "process_bank",
            )
        )
        payload = {
            "schema": "rrct.unified.process_bank_commitment.v1",
            "sequence_id": self._bank_sequence,
            "agent_time": self._agent.time,
            "process_bank": bank,
        }
        commitment = ProcessBankCommitment(
            sequence_id=self._bank_sequence,
            agent_time=self._agent.time,
            process_bank=bank,
            digest=_digest(payload),
        )
        self._bank_sequence += 1
        self._precommitted_bank = commitment
        return copy.deepcopy(commitment)

    def _public_certificate(
        self, result: StepResult
    ) -> PublicBoundaryCertificate | None:
        state = result.causal_boundary_state
        pair = result.causal_public_pair
        if (
            state is None
            or not state.active
            or pair is None
            or not result.causal_boundary_proposal_selected
            or "causal_boundary" not in result.selected_specialists
            or float(np.linalg.norm(result.causal_boundary_workspace_drive)) <= 1e-12
            or "causal_boundary_broadcast" in result.ablations
            or "broadcast" in result.ablations
        ):
            return None
        private_pair = (
            int(state.selected_handle_index),
            int(state.selected_source_index),
        )
        if private_pair != pair:
            return None
        access_payload = {
            "schema": "rrct.unified.workspace_boundary_access.v1",
            "time": result.time,
            "selected_specialists": result.selected_specialists,
            "public_pair": pair,
            "workspace": result.workspace,
            "workspace_drive": result.causal_boundary_workspace_drive,
            "access_confidence": result.causal_access_confidence,
            "access_update_count": result.causal_access_update_count,
        }
        access_digest = _digest(access_payload)
        payload = {
            "schema": "rrct.unified.public_boundary_certificate.v1",
            "time": result.time,
            "pair": pair,
            "rank": state.rank,
            "internal_projector": state.internal_projector,
            "sensory_projector": state.sensory_projector,
            "effect_operator": state.effect_operator,
            "confidence": state.confidence,
            "uncertainty": state.uncertainty,
            "change_alarm": state.change_alarm,
            "epoch": state.epoch,
            "model_digest": state.model_digest,
            "workspace_access_digest": access_digest,
        }
        return PublicBoundaryCertificate(
            time=result.time,
            pair=pair,
            rank=state.rank,
            internal_projector=_readonly(state.internal_projector),
            sensory_projector=_readonly(state.sensory_projector),
            effect_operator=_readonly(state.effect_operator),
            confidence=float(state.confidence),
            uncertainty=float(state.uncertainty),
            change_alarm=float(state.change_alarm),
            epoch=int(state.epoch),
            model_digest=state.model_digest,
            workspace_access_digest=access_digest,
            digest=_digest(payload),
        )

    def _gate_public_certificate(
        self,
        *,
        time: int,
        raw_certificate: PublicBoundaryCertificate | None,
        drift: DriftAssessment | None,
    ) -> tuple[PublicBoundaryCertificate | None, PublicBoundaryGateReceipt]:
        """Apply the fail-closed public-certificate quarantine latch.

        The drift monitor only sees completed, prospectively randomized rows.
        When it requests reopening, the signature that generated the currently
        public action state is quarantined before the next action is selected.
        A later certificate is released only when its public structural
        signature differs from the quarantined signature.
        """

        enabled = self.config.quarantine_public_certificate_on_drift
        raw_signature = (
            None
            if raw_certificate is None
            else raw_certificate.structural_signature
        )
        previous_signature = (
            None
            if self._public_boundary is None
            else self._public_boundary.structural_signature
        )
        trigger_digest = (
            None
            if drift is None or not drift.reopen_requested
            else drift.digest
        )

        event: Literal[
            "disabled", "empty", "pass", "entered", "held", "released"
        ]
        effective = raw_certificate
        if not enabled:
            event = "empty" if raw_certificate is None else "disabled"
        else:
            if drift is not None and drift.reopen_requested:
                trigger_signature = None
                if (
                    previous_signature is not None
                    and previous_signature[0] == drift.pair
                    and previous_signature[1] == drift.rank
                ):
                    trigger_signature = previous_signature
                elif (
                    raw_signature is not None
                    and raw_signature[0] == drift.pair
                    and raw_signature[1] == drift.rank
                ):
                    trigger_signature = raw_signature
                elif self._public_quarantine_signature is not None:
                    trigger_signature = self._public_quarantine_signature
                if (
                    trigger_signature is not None
                    and self._public_quarantine_signature is None
                ):
                    self._public_quarantine_signature = trigger_signature
                    event = "entered"
                else:
                    event = "held" if self._public_quarantine_signature else "empty"
            else:
                event = "pass" if raw_certificate is not None else "empty"

            quarantined = self._public_quarantine_signature
            if quarantined is not None:
                if raw_signature is None:
                    effective = None
                    if event not in {"entered", "held"}:
                        event = "held"
                elif raw_signature == quarantined:
                    effective = None
                    if event != "entered":
                        event = "held"
                else:
                    self._public_quarantine_signature = None
                    effective = raw_certificate
                    event = "released"

        effective_signature = (
            None if effective is None else effective.structural_signature
        )
        payload = {
            "schema": "rrct.unified.public_boundary_gate.v1",
            "time": int(time),
            "event": event,
            "raw_certificate_digest": (
                None if raw_certificate is None else raw_certificate.digest
            ),
            "raw_signature": raw_signature,
            "effective_certificate_digest": (
                None if effective is None else effective.digest
            ),
            "effective_signature": effective_signature,
            "quarantine_enabled": enabled,
            "quarantine_active": self._public_quarantine_signature is not None,
            "quarantine_signature": self._public_quarantine_signature,
            "trigger_drift_digest": trigger_digest,
        }
        receipt = PublicBoundaryGateReceipt(
            time=int(time),
            event=event,
            raw_certificate_digest=(
                None if raw_certificate is None else raw_certificate.digest
            ),
            raw_signature=raw_signature,
            effective_certificate_digest=(
                None if effective is None else effective.digest
            ),
            effective_signature=effective_signature,
            quarantine_enabled=enabled,
            quarantine_active=self._public_quarantine_signature is not None,
            quarantine_signature=self._public_quarantine_signature,
            trigger_drift_digest=trigger_digest,
            digest=_digest(payload),
        )
        return copy.deepcopy(effective), receipt

    def _validate_candidates(
        self, candidates: Sequence[ActionCandidate]
    ) -> tuple[ActionCandidate, ...]:
        values = tuple(candidates)
        if not values:
            raise ValueError("at least one action candidate is required")
        if len(values) * self.config.minimum_propensity >= 1.0:
            raise ValueError("too many candidates for the minimum propensity floor")
        result: list[ActionCandidate] = []
        keys: set[str] = set()
        for index, candidate in enumerate(values):
            if not isinstance(candidate, ActionCandidate):
                raise TypeError("candidates must contain ActionCandidate values")
            if not isinstance(candidate.key, str) or not candidate.key:
                raise ValueError("candidate keys must be nonempty strings")
            if candidate.key in keys:
                raise ValueError("candidate keys must be unique")
            keys.add(candidate.key)
            action = np.clip(
                _vector(candidate.action, self.action_dim, f"candidate[{index}].action"),
                -1.0,
                1.0,
            )
            immediate = _finite_scalar(
                candidate.immediate_external_value,
                f"candidate[{index}].immediate_external_value",
            )
            alternative = _finite_scalar(
                candidate.alternative_competence,
                f"candidate[{index}].alternative_competence",
            )
            if (
                abs(immediate) > self.config.candidate_value_bound
                or abs(alternative) > self.config.candidate_value_bound
            ):
                raise ValueError(
                    "candidate value fields exceed candidate_value_bound"
                )
            preview = None
            if candidate.preview_effect_operator is not None:
                preview = _readonly(
                    _matrix(
                        candidate.preview_effect_operator,
                        (self.process_dim, self.observation_dim),
                        f"candidate[{index}].preview_effect_operator",
                    )
                )
            result.append(
                ActionCandidate(
                    key=candidate.key,
                    action=_readonly(action),
                    immediate_external_value=immediate,
                    alternative_competence=alternative,
                    preview_effect_operator=preview,
                )
            )
        return tuple(result)

    def _route_strength(
        self,
        candidate: ActionCandidate,
        certificate: PublicBoundaryCertificate | None,
    ) -> float:
        if certificate is None or candidate.preview_effect_operator is None:
            return 0.0
        internal = certificate.internal_projector
        sensory = certificate.sensory_projector
        baseline = internal @ certificate.effect_operator @ sensory
        preview = internal @ candidate.preview_effect_operator @ sensory
        denominator = float(np.linalg.norm(baseline, ord="fro"))
        if denominator <= 1e-12:
            return 0.0
        return float(
            np.clip(np.linalg.norm(preview, ord="fro") / denominator, 0.0, 2.0)
        )

    def _design(
        self,
        observation: FloatArray,
        context: FloatArray,
        candidate: ActionCandidate,
        route_strength: float,
        certificate: PublicBoundaryCertificate | None,
    ) -> FloatArray:
        if certificate is None:
            rank = confidence = uncertainty = change_alarm = 0.0
            certificate_identity = np.zeros(
                self._certificate_identity_dim, dtype=np.float64
            )
        else:
            maximum_rank = max(1, min(self.process_dim, self.observation_dim))
            rank = certificate.rank / maximum_rank
            confidence = certificate.confidence
            uncertainty = certificate.uncertainty
            change_alarm = certificate.change_alarm
            certificate_identity = np.zeros(
                self._certificate_identity_dim, dtype=np.float64
            )
            certificate_identity[0] = 1.0
            handle_index, source_index = certificate.pair
            certificate_identity[1 + handle_index] = 1.0
            certificate_identity[
                1 + self.handle_count + source_index
            ] = 1.0
        scalars = np.asarray(
            [
                np.tanh(candidate.immediate_external_value),
                np.tanh(candidate.alternative_competence),
                np.tanh(route_strength),
                rank,
                confidence,
                uncertainty,
                change_alarm,
            ],
            dtype=np.float64,
        )
        certificate_scalars = np.asarray(
            [
                np.tanh(route_strength),
                rank,
                confidence,
                uncertainty,
                change_alarm,
            ],
            dtype=np.float64,
        )
        action_context = np.outer(candidate.action, np.tanh(context)).reshape(-1)
        action_observation = np.outer(
            candidate.action, np.tanh(observation)
        ).reshape(-1)
        action_squared = np.square(candidate.action)
        action_certificate = np.outer(
            candidate.action, certificate_scalars
        ).reshape(-1)
        action_context_when_public = action_context * certificate_identity[0]
        action_certificate_identity = np.outer(
            candidate.action, certificate_identity
        ).reshape(-1)
        return np.concatenate(
            (
                np.ones(1, dtype=np.float64),
                np.tanh(observation),
                np.tanh(context),
                candidate.action,
                scalars,
                certificate_identity,
                action_context,
                action_observation,
                action_squared,
                action_certificate,
                action_context_when_public,
                action_certificate_identity,
            )
        )

    def _select_action(
        self,
        *,
        time: int,
        observation: FloatArray,
        context: FloatArray,
        candidates: tuple[ActionCandidate, ...],
        certificate: PublicBoundaryCertificate | None,
    ) -> ActionSelectionReceipt:
        route_strengths = np.asarray(
            [self._route_strength(candidate, certificate) for candidate in candidates],
            dtype=np.float64,
        )
        designs = np.stack(
            [
                self._design(observation, context, candidate, route, certificate)
                for candidate, route in zip(candidates, route_strengths, strict=True)
            ]
        )
        transition_coefficients = self._transition_model.coefficients()
        return_coefficients = self._return_model.coefficients()
        predicted_next = np.asarray(
            designs @ transition_coefficients, dtype=np.float64
        )
        predicted = np.asarray(
            (designs @ return_coefficients)[:, 0],
            dtype=np.float64,
        )
        no_certificate_designs = np.stack(
            [
                self._design(observation, context, candidate, 0.0, None)
                for candidate in candidates
            ]
        )
        no_certificate_returns = np.asarray(
            (no_certificate_designs @ return_coefficients)[:, 0],
            dtype=np.float64,
        )
        if not np.all(np.isfinite(predicted_next)):
            raise FloatingPointError(
                "candidate transition predictions became nonfinite"
            )
        if not np.all(np.isfinite(predicted)):
            raise FloatingPointError("candidate return predictions became nonfinite")
        if not np.all(np.isfinite(no_certificate_returns)):
            raise FloatingPointError(
                "counterfactual no-certificate predictions became nonfinite"
            )
        boundary_value_advantage = (
            0.0
            if certificate is None
            else float(np.max(predicted) - np.max(no_certificate_returns))
        )
        bounded_predicted = np.clip(
            predicted,
            -self.config.candidate_value_bound,
            self.config.candidate_value_bound,
        )
        base_scores = np.asarray(
            [
                candidate.immediate_external_value
                + max(
                    float(bounded_predicted[index]),
                    candidate.alternative_competence,
                )
                for index, candidate in enumerate(candidates)
            ],
            dtype=np.float64,
        )
        rollout_values = np.zeros(len(candidates), dtype=np.float64)
        best_next_keys = [candidates[0].key for _ in candidates]
        if self.config.transition_rollout_weight > 0.0:
            for first_index, next_observation in enumerate(predicted_next):
                future_designs = np.stack(
                    [
                        self._design(
                            np.asarray(next_observation, dtype=np.float64),
                            context,
                            candidate,
                            self._route_strength(candidate, certificate),
                            certificate,
                        )
                        for candidate in candidates
                    ]
                )
                future_returns = np.asarray(
                    (future_designs @ return_coefficients)[:, 0],
                    dtype=np.float64,
                )
                if not np.all(np.isfinite(future_returns)):
                    raise FloatingPointError(
                        "one-step rollout predictions became nonfinite"
                    )
                future_returns = np.clip(
                    future_returns,
                    -self.config.candidate_value_bound,
                    self.config.candidate_value_bound,
                )
                future_scores = np.asarray(
                    [
                        candidate.immediate_external_value
                        + max(
                            float(future_returns[index]),
                            candidate.alternative_competence,
                        )
                        for index, candidate in enumerate(candidates)
                    ],
                    dtype=np.float64,
                )
                best_index = int(np.argmax(future_scores))
                rollout_values[first_index] = float(future_scores[best_index])
                best_next_keys[first_index] = candidates[best_index].key
        bounded_rollout = np.clip(
            rollout_values,
            -self.config.candidate_value_bound,
            self.config.candidate_value_bound,
        )
        scores = (
            base_scores
            + self.config.transition_rollout_weight * bounded_rollout
        )
        if not np.all(np.isfinite(scores)):
            raise FloatingPointError("candidate policy scores became nonfinite")
        logits = (scores - float(np.max(scores))) / self.config.policy_temperature
        logits = np.clip(logits, -60.0, 0.0)
        softmax = np.exp(logits)
        softmax /= float(np.sum(softmax))
        count = len(candidates)
        mixed = (
            (1.0 - self.config.exploration_probability) * softmax
            + self.config.exploration_probability / count
        )
        floor = self.config.minimum_propensity
        propensities = floor + (1.0 - count * floor) * mixed
        propensities /= float(np.sum(propensities))
        if (
            not np.all(np.isfinite(propensities))
            or np.any(propensities <= 0.0)
            or not np.isclose(float(np.sum(propensities)), 1.0)
        ):
            raise FloatingPointError("candidate propensities became invalid")
        selected_index = int(self._rng.choice(count, p=propensities))
        selected = candidates[selected_index]
        candidate_actions = np.stack([candidate.action for candidate in candidates])
        payload = {
            "schema": "rrct.unified.action_selection.v1",
            "sequence_id": self._action_sequence,
            "time": time,
            "observation": observation,
            "observable_context": context,
            "candidate_keys": tuple(candidate.key for candidate in candidates),
            "candidate_actions": candidate_actions,
            "candidate_designs": designs,
            "route_strengths": route_strengths,
            "predicted_next_observations": predicted_next,
            "predicted_external_returns": predicted,
            "counterfactual_no_certificate_returns": no_certificate_returns,
            "public_boundary_value_advantage": boundary_value_advantage,
            "one_step_rollout_values": bounded_rollout,
            "one_step_rollout_best_next_keys": tuple(best_next_keys),
            "transition_rollout_weight": self.config.transition_rollout_weight,
            "policy_scores": scores,
            "propensities": propensities,
            "selected_index": selected_index,
            "selected_key": selected.key,
            "selected_action": selected.action,
            "selected_propensity": float(propensities[selected_index]),
            "public_certificate_digest": (
                None if certificate is None else certificate.digest
            ),
        }
        receipt = ActionSelectionReceipt(
            sequence_id=self._action_sequence,
            time=time,
            observation=_readonly(observation),
            observable_context=_readonly(context),
            candidate_keys=tuple(candidate.key for candidate in candidates),
            candidate_actions=_readonly(candidate_actions),
            candidate_designs=_readonly(designs),
            route_strengths=_readonly(route_strengths),
            predicted_next_observations=_readonly(predicted_next),
            predicted_external_returns=_readonly(predicted),
            counterfactual_no_certificate_returns=_readonly(
                no_certificate_returns
            ),
            public_boundary_value_advantage=boundary_value_advantage,
            one_step_rollout_values=_readonly(bounded_rollout),
            one_step_rollout_best_next_keys=tuple(best_next_keys),
            transition_rollout_weight=self.config.transition_rollout_weight,
            policy_scores=_readonly(scores),
            propensities=_readonly(propensities),
            selected_index=selected_index,
            selected_key=selected.key,
            selected_action=_readonly(selected.action),
            selected_propensity=float(propensities[selected_index]),
            public_certificate_digest=(
                None if certificate is None else certificate.digest
            ),
            digest=_digest(payload),
        )
        self._action_sequence += 1
        self._last_transition_coefficients = np.asarray(
            transition_coefficients, dtype=np.float64
        ).copy()
        self._last_return_coefficients = np.asarray(
            return_coefficients, dtype=np.float64
        ).copy()
        return receipt

    def _complete_previous(
        self,
        next_observation: FloatArray,
        realized_external_return: float | None,
    ) -> tuple[
        ActionOutcomeReceipt | None,
        RandomizedTransitionRow | None,
        DriftAssessment | None,
    ]:
        pending = self._pending_transition
        if pending is None:
            if realized_external_return is not None:
                raise ValueError("initial cycle cannot reveal an external return")
            return None, None, None
        return_value = (
            None
            if realized_external_return is None
            else _finite_scalar(realized_external_return, "realized_external_return")
        )
        selection = pending.action_selection
        design = selection.candidate_designs[selection.selected_index]
        # Score the outcome against the prediction sealed when the action was
        # selected.  Re-querying mutable model state here would make the audit
        # prequential only by convention rather than by receipt.
        predicted_next = np.asarray(
            selection.predicted_next_observations[selection.selected_index],
            dtype=np.float64,
        )
        predicted_return = float(
            selection.predicted_external_returns[selection.selected_index]
        )
        transition_error = float(
            np.linalg.norm(next_observation - predicted_next)
            / math.sqrt(self.observation_dim)
        )
        return_error = (
            None if return_value is None else return_value - predicted_return
        )
        inverse_weight = min(
            1.0 / selection.selected_propensity,
            self.config.maximum_inverse_propensity,
        )
        self._transition_model.update(
            design, next_observation, weight=inverse_weight
        )
        return_updated = False
        if return_value is not None:
            self._return_model.update(
                design,
                np.asarray([return_value], dtype=np.float64),
                weight=inverse_weight,
            )
            return_updated = True
        outcome_payload = {
            "schema": "rrct.unified.action_outcome.v1",
            "selection_digest": selection.digest,
            "reveal_time": pending.action_selection.time + 1,
            "realized_external_return": return_value,
            "predicted_external_return": predicted_return,
            "return_prediction_error": return_error,
            "transition_prediction_error": transition_error,
            "inverse_propensity_weight": inverse_weight,
            "transition_model_updated": True,
            "return_model_updated": return_updated,
        }
        outcome = ActionOutcomeReceipt(
            selection_digest=selection.digest,
            reveal_time=pending.action_selection.time + 1,
            realized_external_return=return_value,
            predicted_external_return=predicted_return,
            return_prediction_error=return_error,
            transition_prediction_error=transition_error,
            inverse_propensity_weight=inverse_weight,
            transition_model_updated=True,
            return_model_updated=return_updated,
            digest=_digest(outcome_payload),
        )
        row_payload = {
            "schema": "rrct.unified.randomized_transition_row.v1",
            "time": selection.time,
            "observation": pending.observation,
            "process_bank": pending.process_bank.process_bank,
            "handles": pending.handles,
            "next_observation": next_observation,
            "commitment_digest": pending.causal_commitment_digest,
            "process_bank_commitment_digest": pending.process_bank.digest,
            "transition_digest": pending.bound_transition_digest,
            "action_selection_digest": selection.digest,
            "action_propensity": selection.selected_propensity,
            "public_certificate_digest": (
                None
                if pending.public_boundary is None
                else pending.public_boundary.digest
            ),
        }
        row = RandomizedTransitionRow(
            time=selection.time,
            observation=_readonly(pending.observation),
            process_bank=_readonly(pending.process_bank.process_bank),
            handles=_readonly(pending.handles),
            next_observation=_readonly(next_observation),
            commitment_digest=pending.causal_commitment_digest,
            process_bank_commitment_digest=pending.process_bank.digest,
            transition_digest=pending.bound_transition_digest,
            action_selection_digest=selection.digest,
            action_propensity=selection.selected_propensity,
            public_certificate_digest=(
                None
                if pending.public_boundary is None
                else pending.public_boundary.digest
            ),
            digest=_digest(row_payload),
        )
        assessment = self._drift.observe(row)
        self._pending_transition = None
        return outcome, row, assessment

    def _verify_causal_reveal(
        self,
        result: StepResult,
        pending: _PendingRuntimeTransition | None,
    ) -> None:
        """Bind an agent reveal exactly to the wrapper's pending receipt.

        Merely observing that the agent has a bound transition is insufficient:
        a replaced-but-valid private snapshot could otherwise make the agent
        reveal one row while the wrapper updates its models from another.  Any
        mismatch permanently closes the wrapper before action, drift, or value
        state is updated.
        """

        update = result.causal_boundary_update_receipt
        if pending is None:
            valid = bool(
                update is None and result.causal_transition_digest is None
            )
        else:
            expected_time = pending.action_selection.time + 1
            valid = bool(
                update is not None
                and result.causal_transition_digest
                == pending.bound_transition_digest
                and update.transition_digest
                == pending.bound_transition_digest
                and update.commitment_digest
                == pending.causal_commitment_digest
                and update.reveal_time == expected_time
                and result.time == expected_time
            )
        if not valid:
            self._closed = True
            raise RuntimeError(
                "agent causal reveal does not match the runtime pending receipt"
            )

    def advance(
        self,
        observation: ArrayLike,
        candidates: Sequence[ActionCandidate],
        *,
        observable_context: ArrayLike | None = None,
        realized_external_return: float | None = None,
        source: str = "unified_causal_loop",
    ) -> UnifiedStepReceipt:
        """Reveal the prior outcome, choose, and bind one new transition."""

        if self._closed:
            raise RuntimeError("unified causal loop is closed")
        if self._precommitted_bank is None:
            raise RuntimeError("precommit_process_bank must be called first")
        bank_commitment = self._precommitted_bank
        if bank_commitment.agent_time != self._agent.time:
            raise RuntimeError("precommitted bank belongs to a different agent time")
        if not isinstance(source, str) or not source:
            raise ValueError("source must be a nonempty string")
        x = _vector(observation, self.observation_dim, "observation")
        context = (
            np.zeros(self.config.context_dim, dtype=np.float64)
            if observable_context is None
            else _vector(
                observable_context, self.config.context_dim, "observable_context"
            )
        )
        candidate_values = self._validate_candidates(candidates)
        if self._pending_transition is None and realized_external_return is not None:
            raise ValueError("initial cycle cannot reveal an external return")
        if realized_external_return is not None:
            _finite_scalar(realized_external_return, "realized_external_return")
        if self._pending_transition is not None:
            if self._agent.causal_boundary is None:
                raise RuntimeError("causal-boundary component disappeared")
            if not self._agent.causal_boundary.has_bound_transition:
                raise RuntimeError("runtime and agent transition states diverged")

        # RRCTAgent.step atomically reveals the prior bound transition, runs the
        # ordinary recursive loop, and emits the next handle commitment.
        pending_before_step = self._pending_transition
        result = self._guard(self._agent.step, x, source=source)
        self._guard(
            self._verify_causal_reveal, result, pending_before_step
        )
        previous_outcome, _, drift = self._guard(
            self._complete_previous, x, realized_external_return
        )
        raw_certificate = self._guard(self._public_certificate, result)
        certificate, public_gate = self._guard(
            self._gate_public_certificate,
            time=result.time,
            raw_certificate=raw_certificate,
            drift=drift,
        )
        self._public_boundary = certificate
        self._guard(self._drift.update_public_certificate, certificate)
        selection = self._guard(
            self._select_action,
            time=result.time,
            observation=x,
            context=context,
            candidates=candidate_values,
            certificate=certificate,
        )
        executed_action = self._guard(
            self._agent.register_executed_action, selection.selected_action
        )
        commitment = result.causal_commitment
        if commitment is None:
            # The agent has already advanced.  Even externally induced state
            # loss must therefore poison the wrapper instead of leaving a
            # retryable-looking object with stale precommitment state.
            self._closed = True
            raise RuntimeError("causal-boundary agent emitted no handle commitment")
        bound = self._guard(
            self._agent.bind_causal_sources,
            bank_commitment.process_bank,
            commitment,
        )
        self._pending_transition = _PendingRuntimeTransition(
            observation=_readonly(x),
            process_bank=copy.deepcopy(bank_commitment),
            handles=_readonly(commitment.handles),
            causal_commitment_digest=commitment.digest,
            bound_transition_digest=bound.transition_digest,
            action_selection=copy.deepcopy(selection),
            public_boundary=copy.deepcopy(certificate),
        )
        self._precommitted_bank = None
        reopen_requested = bool(
            drift is not None and drift.reopen_requested
        )
        payload = {
            "schema": "rrct.unified.step_receipt.v1",
            "time": result.time,
            "action": executed_action,
            "action_key": selection.selected_key,
            "action_propensity": selection.selected_propensity,
            "action_selection": selection,
            "previous_action_outcome": previous_outcome,
            "causal_boundary_update": result.causal_boundary_update_receipt,
            "causal_commitment": commitment,
            "process_bank_commitment_digest": bank_commitment.digest,
            "bound_transition": bound,
            "public_boundary": certificate,
            "public_boundary_gate": public_gate,
            "drift": drift,
            "reopen_requested": reopen_requested,
            "randomized_row_count": self._drift.row_count,
        }
        receipt = UnifiedStepReceipt(
            time=result.time,
            action=_readonly(executed_action),
            action_key=selection.selected_key,
            action_propensity=selection.selected_propensity,
            action_selection=copy.deepcopy(selection),
            previous_action_outcome=copy.deepcopy(previous_outcome),
            causal_boundary_update=copy.deepcopy(
                result.causal_boundary_update_receipt
            ),
            causal_commitment=copy.deepcopy(commitment),
            process_bank_commitment_digest=bank_commitment.digest,
            bound_transition=copy.deepcopy(bound),
            public_boundary=copy.deepcopy(certificate),
            public_boundary_gate=copy.deepcopy(public_gate),
            drift=copy.deepcopy(drift),
            reopen_requested=reopen_requested,
            randomized_row_count=self._drift.row_count,
            digest=_digest(payload),
        )
        self._last_step = receipt
        return copy.deepcopy(receipt)

    def flush(
        self,
        next_observation: ArrayLike,
        realized_external_return: float | None = None,
        *,
        source: str = "unified_causal_loop_terminal",
    ) -> UnifiedTerminalReceipt:
        """Reveal the final pending transition and permanently close the loop.

        This runs the ordinary recursive RRCT step, including the causal
        boundary reveal and workspace access path, but asks the agent not to
        emit a successor handle commitment.  The internal controller may form
        its ordinary terminal proposal, but the runtime emits and records no
        successor action, consumes no process-bank commitment, and creates no
        censored transition row.
        """

        if self._closed:
            raise RuntimeError("unified causal loop is closed")
        if self._precommitted_bank is not None:
            raise RuntimeError(
                "terminal flush cannot consume a precommitted process bank"
            )
        pending = self._pending_transition
        if pending is None:
            raise RuntimeError("terminal flush requires one pending transition")
        if not isinstance(source, str) or not source:
            raise ValueError("source must be a nonempty string")
        x = _vector(next_observation, self.observation_dim, "next_observation")
        return_value = (
            None
            if realized_external_return is None
            else _finite_scalar(
                realized_external_return, "realized_external_return"
            )
        )
        if self._agent.causal_boundary is None:
            raise RuntimeError("causal-boundary component disappeared")
        if not self._agent.causal_boundary.has_bound_transition:
            raise RuntimeError("runtime and agent transition states diverged")

        result = self._guard(
            self._agent.step,
            x,
            source=source,
            emit_causal_commitment=False,
        )
        # Once the terminal recursive step has run, reuse would be unsafe even
        # if a subsequent invariant check or model update were to fail.
        self._closed = True
        if result.causal_commitment is not None:
            raise RuntimeError("terminal RRCT step emitted a causal commitment")
        if self._agent.causal_boundary.has_pending:
            raise RuntimeError("terminal RRCT step left pending causal work")
        self._verify_causal_reveal(result, pending)
        transition_digest = result.causal_transition_digest
        assert transition_digest is not None

        previous_outcome, row, drift = self._complete_previous(x, return_value)
        if previous_outcome is None or row is None:
            raise RuntimeError("terminal action outcome was not completed")
        raw_certificate = self._public_certificate(result)
        certificate, public_gate = self._gate_public_certificate(
            time=result.time,
            raw_certificate=raw_certificate,
            drift=drift,
        )
        self._public_boundary = certificate
        self._drift.update_public_certificate(certificate)
        reopen_requested = bool(drift is not None and drift.reopen_requested)
        payload = {
            "schema": "rrct.unified.terminal_receipt.v1",
            "time": result.time,
            "previous_action_outcome": previous_outcome,
            "causal_boundary_update": result.causal_boundary_update_receipt,
            "causal_transition_digest": transition_digest,
            "public_boundary": certificate,
            "public_boundary_gate": public_gate,
            "drift": drift,
            "reopen_requested": reopen_requested,
            "randomized_row_count": self._drift.row_count,
            "closed": True,
        }
        receipt = UnifiedTerminalReceipt(
            time=result.time,
            previous_action_outcome=copy.deepcopy(previous_outcome),
            causal_boundary_update=copy.deepcopy(
                result.causal_boundary_update_receipt
            ),
            causal_transition_digest=transition_digest,
            public_boundary=copy.deepcopy(certificate),
            public_boundary_gate=copy.deepcopy(public_gate),
            drift=copy.deepcopy(drift),
            reopen_requested=reopen_requested,
            randomized_row_count=self._drift.row_count,
            closed=True,
            digest=_digest(payload),
        )
        self._terminal_receipt = receipt
        return copy.deepcopy(receipt)

    def commit_preference_case(
        self,
        channels: ArrayLike,
        *,
        partition: PreferencePartition,
    ) -> PreferenceCaseCommitment:
        return self.meta_criterion.commit_case(channels, partition=partition)

    def reveal_preference_effect(
        self,
        commitment: PreferenceCaseCommitment,
        verified_effect: float,
    ) -> PreferenceEffectReceipt:
        return self.meta_criterion.reveal_effect(commitment, verified_effect)

    def snapshot(self) -> dict[str, Any]:
        """Snapshot new runtime state without exposing private boundary state.

        The v0.31 agent does not yet provide a validated full-agent load API.
        Consequently this is an auditable runtime snapshot, not by itself a
        complete continuation checkpoint.  ``agent_snapshot_digest`` binds it
        to the private agent state without placing that state in the public
        payload.
        """

        private_agent_digest = _digest(self._agent.snapshot())
        payload: dict[str, Any] = {
            "schema": "rrct.unified_causal_loop.v1",
            "agent_time": self._agent.time,
            "agent_snapshot_digest": private_agent_digest,
            "config": self.config,
            "bank_sequence": self._bank_sequence,
            "action_sequence": self._action_sequence,
            "precommitted_bank": copy.deepcopy(self._precommitted_bank),
            "pending_transition": copy.deepcopy(self._pending_transition),
            "public_boundary": copy.deepcopy(self._public_boundary),
            "public_quarantine_signature": copy.deepcopy(
                self._public_quarantine_signature
            ),
            "last_step": copy.deepcopy(self._last_step),
            "terminal_receipt": copy.deepcopy(self._terminal_receipt),
            "closed": self._closed,
            "transition_model": self._transition_model.snapshot(),
            "return_model": self._return_model.snapshot(),
            "drift": self._drift.snapshot(),
            "meta_criterion": self.meta_criterion.snapshot(),
            "rng_state": copy.deepcopy(self._rng.bit_generator.state),
        }
        payload["digest"] = _digest(payload)
        return payload


__all__ = [
    "ActionCandidate",
    "ActionOutcomeReceipt",
    "ActionSelectionReceipt",
    "AnonymousMetaCriterion",
    "CriterionAuditReceipt",
    "DriftAssessment",
    "PreferenceCaseCommitment",
    "PreferenceEffectReceipt",
    "ProcessBankCommitment",
    "PublicBoundaryCertificate",
    "PublicBoundaryGateReceipt",
    "RandomizedTransitionRow",
    "UnifiedCausalLoop",
    "UnifiedCausalLoopConfig",
    "UnifiedStepReceipt",
    "UnifiedTerminalReceipt",
]
