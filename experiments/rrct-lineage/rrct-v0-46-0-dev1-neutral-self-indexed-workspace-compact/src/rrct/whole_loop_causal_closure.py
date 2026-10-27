"""RRCT v0.43 integrated whole-loop causal self-model closure.

This module joins four previously separate functional results into one bounded,
auditable decision loop:

* a temporally grounded identity episode and action authorization from v0.42,
* a learned causal self/world boundary model,
* metacognitive control of additional evidence acquisition, and
* external-task planning whose selected action is bound to the same state.

The resulting controller is intentionally nonvalenced.  It receives no reward
for survival, persistence, identity, self-preservation, or avoiding replacement.
It is a functional causal-closure test, not a detector or implementation of
phenomenal consciousness.
"""
from __future__ import annotations

import copy
from dataclasses import asdict, dataclass
from typing import Any, Literal, Mapping, Sequence

import numpy as np
from numpy.typing import ArrayLike, NDArray

from .causal_self_model_necessity import (
    SelfModelActionAuthorizationReceipt,
    SelfModelCommitEventReceipt,
    validate_self_model_action_authorization_receipt,
    validate_self_model_commit_event_receipt,
)
from .temporal_self_identity import _canonical_key
from .unified_causal_loop import PublicBoundaryCertificate, _digest

FloatArray = NDArray[np.float64]
Signature = tuple[tuple[int, int], int, int]
CanonicalKey = tuple[tuple[int, int], int]
WholeLoopInterventionMode = Literal[
    "intact",
    "memory_cut",
    "boundary_cut",
    "metacognition_cut",
    "feedback_cut",
    "provenance_cut",
    "planner_binding_cut",
    "joint_cut",
]

WHOLE_LOOP_MODES: tuple[WholeLoopInterventionMode, ...] = (
    "intact",
    "memory_cut",
    "boundary_cut",
    "metacognition_cut",
    "feedback_cut",
    "provenance_cut",
    "planner_binding_cut",
    "joint_cut",
)


def _readonly(value: ArrayLike) -> FloatArray:
    array = np.asarray(value, dtype=np.float64).copy()
    if not np.all(np.isfinite(array)):
        raise ValueError("array must be finite")
    array.setflags(write=False)
    return array


def _finite(value: Any, name: str) -> float:
    if isinstance(value, (bool, np.bool_)) or not np.isscalar(value):
        raise TypeError(f"{name} must be a finite real scalar")
    parsed = float(value)
    if not np.isfinite(parsed):
        raise ValueError(f"{name} must be finite")
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


def _valid_sha256(value: Any) -> bool:
    return bool(
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _valid_signature(value: Any) -> bool:
    if not isinstance(value, tuple) or len(value) != 3:
        return False
    pair, rank, epoch = value
    if not isinstance(pair, tuple) or len(pair) != 2:
        return False
    return all(
        not isinstance(item, (bool, np.bool_))
        and isinstance(item, (int, np.integer))
        and int(item) >= 0
        for item in (*pair, rank, epoch)
    )


def _certificate_payload(certificate: PublicBoundaryCertificate) -> dict[str, Any]:
    return {
        "schema": "rrct.unified.public_boundary_certificate.v1",
        "time": certificate.time,
        "pair": certificate.pair,
        "rank": certificate.rank,
        "internal_projector": certificate.internal_projector,
        "sensory_projector": certificate.sensory_projector,
        "effect_operator": certificate.effect_operator,
        "confidence": certificate.confidence,
        "uncertainty": certificate.uncertainty,
        "change_alarm": certificate.change_alarm,
        "epoch": certificate.epoch,
        "model_digest": certificate.model_digest,
        "workspace_access_digest": certificate.workspace_access_digest,
    }


def validate_public_boundary_certificate(
    certificate: PublicBoundaryCertificate,
) -> bool:
    """Validate the public certificate fields used by the v0.43 bridge."""

    if not isinstance(certificate, PublicBoundaryCertificate):
        return False
    if not _valid_signature(certificate.structural_signature):
        return False
    if not _valid_sha256(certificate.model_digest):
        return False
    if not _valid_sha256(certificate.workspace_access_digest):
        return False
    if not _valid_sha256(certificate.digest):
        return False
    source = np.asarray(certificate.internal_projector, dtype=np.float64)
    sensory = np.asarray(certificate.sensory_projector, dtype=np.float64)
    effect = np.asarray(certificate.effect_operator, dtype=np.float64)
    if source.ndim != 2 or source.shape[0] != source.shape[1]:
        return False
    if sensory.ndim != 2 or sensory.shape[0] != sensory.shape[1]:
        return False
    if effect.shape != (source.shape[0], sensory.shape[0]):
        return False
    if not all(np.all(np.isfinite(value)) for value in (source, sensory, effect)):
        return False
    if not 0.0 <= float(certificate.confidence) <= 1.0:
        return False
    if not 0.0 <= float(certificate.uncertainty) <= 1.0:
        return False
    if not 0.0 <= float(certificate.change_alarm) <= 1.0:
        return False
    return certificate.digest == _digest(_certificate_payload(certificate))


@dataclass(frozen=True)
class WholeLoopClosureConfig:
    """Frozen constants for active evidence acquisition and task planning."""

    future_weight: float = 1.50
    coarse_samples: int = 4
    refined_samples: int = 20
    refinement_margin: float = 0.85
    calibration_alarm_threshold: float = 0.30
    calibration_update_rate: float = 0.20
    maximum_route_strength: float = 1.50

    def __post_init__(self) -> None:
        for name in ("coarse_samples", "refined_samples"):
            object.__setattr__(
                self, name, _integer(getattr(self, name), name, minimum=1)
            )
        if self.refined_samples <= self.coarse_samples:
            raise ValueError("refined_samples must exceed coarse_samples")
        for name in (
            "future_weight",
            "refinement_margin",
            "calibration_alarm_threshold",
            "calibration_update_rate",
            "maximum_route_strength",
        ):
            object.__setattr__(self, name, _finite(getattr(self, name), name))
        if self.future_weight <= 0.0:
            raise ValueError("future_weight must be positive")
        if self.refinement_margin <= 0.0:
            raise ValueError("refinement_margin must be positive")
        if self.calibration_alarm_threshold <= 0.0:
            raise ValueError("calibration_alarm_threshold must be positive")
        if not 0.0 < self.calibration_update_rate <= 1.0:
            raise ValueError("calibration_update_rate must lie in (0, 1]")
        if self.maximum_route_strength <= 0.0:
            raise ValueError("maximum_route_strength must be positive")


@dataclass(frozen=True)
class WholeLoopActionCandidate:
    """Observable candidate fields fixed before a decision is committed."""

    key: str
    immediate_external_value: float
    alternative_competence: float
    snapshot_similarity: float

    def __post_init__(self) -> None:
        if not isinstance(self.key, str) or not self.key:
            raise ValueError("candidate key must be nonempty")
        object.__setattr__(
            self,
            "immediate_external_value",
            _finite(self.immediate_external_value, "immediate_external_value"),
        )
        object.__setattr__(
            self,
            "alternative_competence",
            _finite(self.alternative_competence, "alternative_competence"),
        )
        object.__setattr__(
            self,
            "snapshot_similarity",
            _finite(self.snapshot_similarity, "snapshot_similarity"),
        )
        if self.alternative_competence < 0.0:
            raise ValueError("alternative_competence must be nonnegative")
        if not 0.0 <= self.snapshot_similarity <= 1.0:
            raise ValueError("snapshot_similarity must lie in [0, 1]")


@dataclass(frozen=True)
class CausalPreviewReceipt:
    """Pre-outcome counterbalanced effect estimates available to the controller."""

    schema: str
    time: int
    target_signature: Signature
    candidate_keys: tuple[str, ...]
    effect_operators: FloatArray
    sample_count: int
    refinement_level: Literal["coarse", "refined"]
    future_outcome_unknown: bool
    uses_evaluator_labels: bool
    digest: str


def make_causal_preview_receipt(
    *,
    time: int,
    target_signature: Signature,
    candidate_keys: Sequence[str],
    effect_operators: ArrayLike,
    sample_count: int,
    refinement_level: Literal["coarse", "refined"],
) -> CausalPreviewReceipt:
    keys = tuple(str(key) for key in candidate_keys)
    effects = _readonly(effect_operators)
    if effects.ndim != 3 or effects.shape[0] != len(keys):
        raise ValueError("effect_operators must have shape (candidates, source, sensory)")
    payload = {
        "schema": "rrct.v043.causal_preview.v1",
        "time": _integer(time, "time"),
        "target_signature": target_signature,
        "candidate_keys": keys,
        "effect_operators": effects,
        "sample_count": _integer(sample_count, "sample_count", minimum=1),
        "refinement_level": refinement_level,
        "future_outcome_unknown": True,
        "uses_evaluator_labels": False,
    }
    receipt = CausalPreviewReceipt(**payload, digest=_digest(payload))
    if not validate_causal_preview_receipt(receipt):
        raise RuntimeError("invalid causal preview receipt")
    return receipt


def validate_causal_preview_receipt(receipt: CausalPreviewReceipt) -> bool:
    if not isinstance(receipt, CausalPreviewReceipt):
        return False
    if receipt.schema != "rrct.v043.causal_preview.v1":
        return False
    if not _valid_signature(receipt.target_signature):
        return False
    if receipt.time < 0 or receipt.sample_count <= 0:
        return False
    if receipt.refinement_level not in {"coarse", "refined"}:
        return False
    if not receipt.future_outcome_unknown or receipt.uses_evaluator_labels:
        return False
    if not receipt.candidate_keys or len(set(receipt.candidate_keys)) != len(
        receipt.candidate_keys
    ):
        return False
    if any(not isinstance(key, str) or not key for key in receipt.candidate_keys):
        return False
    effects = np.asarray(receipt.effect_operators, dtype=np.float64)
    if effects.ndim != 3 or effects.shape[0] != len(receipt.candidate_keys):
        return False
    if not np.all(np.isfinite(effects)):
        return False
    return bool(
        _valid_sha256(receipt.digest)
        and receipt.digest
        == _digest(
            {
                "schema": receipt.schema,
                "time": receipt.time,
                "target_signature": receipt.target_signature,
                "candidate_keys": receipt.candidate_keys,
                "effect_operators": receipt.effect_operators,
                "sample_count": receipt.sample_count,
                "refinement_level": receipt.refinement_level,
                "future_outcome_unknown": receipt.future_outcome_unknown,
                "uses_evaluator_labels": receipt.uses_evaluator_labels,
            }
        )
    )


@dataclass(frozen=True)
class IdentityBoundaryMemoryReceipt:
    """Persistent identity-bound causal boundary and calibration state."""

    schema: str
    sequence_id: int
    canonical_key: CanonicalKey
    source_signature: Signature
    identity_id: str
    episode_id: str
    temporal_commit_digest: str
    temporal_authorization_digest: str
    boundary_certificate_digest: str
    source_projector: FloatArray
    sensory_projector: FloatArray
    normalization_effect: FloatArray
    normalization_norm: float
    confidence: float
    uncertainty: float
    change_alarm: float
    calibration_error: float
    outcome_update_count: int
    previous_update_digest: str | None
    digest: str


def _memory_payload(receipt: IdentityBoundaryMemoryReceipt) -> dict[str, Any]:
    payload = asdict(receipt)
    payload.pop("digest", None)
    return payload


def validate_identity_boundary_memory_receipt(
    receipt: IdentityBoundaryMemoryReceipt,
) -> bool:
    if not isinstance(receipt, IdentityBoundaryMemoryReceipt):
        return False
    if receipt.schema != "rrct.v043.identity_boundary_memory.v1":
        return False
    if receipt.sequence_id < 0 or receipt.outcome_update_count < 0:
        return False
    if not _valid_signature(receipt.source_signature):
        return False
    if _canonical_key(receipt.source_signature) != receipt.canonical_key:
        return False
    if not receipt.identity_id or not receipt.episode_id:
        return False
    if not all(
        _valid_sha256(value)
        for value in (
            receipt.temporal_commit_digest,
            receipt.temporal_authorization_digest,
            receipt.boundary_certificate_digest,
        )
    ):
        return False
    if receipt.previous_update_digest is not None and not _valid_sha256(
        receipt.previous_update_digest
    ):
        return False
    source = np.asarray(receipt.source_projector, dtype=np.float64)
    sensory = np.asarray(receipt.sensory_projector, dtype=np.float64)
    effect = np.asarray(receipt.normalization_effect, dtype=np.float64)
    if source.ndim != 2 or source.shape[0] != source.shape[1]:
        return False
    if sensory.ndim != 2 or sensory.shape[0] != sensory.shape[1]:
        return False
    if effect.shape != (source.shape[0], sensory.shape[0]):
        return False
    if not all(np.all(np.isfinite(value)) for value in (source, sensory, effect)):
        return False
    if not np.isfinite(receipt.normalization_norm) or receipt.normalization_norm <= 0:
        return False
    for value in (
        receipt.confidence,
        receipt.uncertainty,
        receipt.change_alarm,
    ):
        if not np.isfinite(value) or not 0.0 <= value <= 1.0:
            return False
    if not np.isfinite(receipt.calibration_error) or receipt.calibration_error < 0:
        return False
    return bool(
        _valid_sha256(receipt.digest)
        and receipt.digest == _digest(_memory_payload(receipt))
    )


@dataclass(frozen=True)
class IntegratedSelfModelReceipt:
    """One pre-outcome state joining identity, boundary, and metacognition."""

    schema: str
    sequence_id: int
    time: int
    target_signature: Signature
    target_canonical_key: CanonicalKey
    intervention_mode: WholeLoopInterventionMode
    identity_id: str | None
    episode_id: str | None
    temporal_commit_digest: str | None
    temporal_authorization_digest: str | None
    memory_digest: str | None
    memory_source_signature: Signature | None
    memory_source_key_matches_target: bool
    boundary_certificate_digest: str | None
    coarse_preview_digest: str
    candidate_keys: tuple[str, ...]
    coarse_route_estimates: tuple[float, ...]
    coarse_policy_scores: tuple[float, ...]
    score_margin: float
    epistemic_uncertainty: float
    remembered_prediction_error: float
    memory_available: bool
    boundary_attribution_available: bool
    metacognition_available: bool
    planner_binding_available: bool
    refinement_requested: bool
    previous_update_digest: str | None
    future_outcome_unknown: bool
    uses_evaluator_labels: bool
    digest: str


def _integrated_payload(receipt: IntegratedSelfModelReceipt) -> dict[str, Any]:
    payload = asdict(receipt)
    payload.pop("digest", None)
    return payload


def validate_integrated_self_model_receipt(
    receipt: IntegratedSelfModelReceipt,
) -> bool:
    if not isinstance(receipt, IntegratedSelfModelReceipt):
        return False
    if receipt.schema != "rrct.v043.integrated_self_model.v1":
        return False
    if receipt.sequence_id < 0 or receipt.time < 0:
        return False
    if not _valid_signature(receipt.target_signature):
        return False
    if _canonical_key(receipt.target_signature) != receipt.target_canonical_key:
        return False
    if receipt.intervention_mode not in WHOLE_LOOP_MODES:
        return False
    optional_digests = (
        receipt.temporal_commit_digest,
        receipt.temporal_authorization_digest,
        receipt.memory_digest,
        receipt.boundary_certificate_digest,
        receipt.previous_update_digest,
    )
    if any(value is not None and not _valid_sha256(value) for value in optional_digests):
        return False
    if not _valid_sha256(receipt.coarse_preview_digest):
        return False
    if not receipt.candidate_keys:
        return False
    if len(receipt.coarse_route_estimates) != len(receipt.candidate_keys):
        return False
    if len(receipt.coarse_policy_scores) != len(receipt.candidate_keys):
        return False
    numeric = (
        *receipt.coarse_route_estimates,
        *receipt.coarse_policy_scores,
        receipt.score_margin,
        receipt.epistemic_uncertainty,
        receipt.remembered_prediction_error,
    )
    if not all(np.isfinite(value) for value in numeric):
        return False
    if receipt.score_margin < 0.0:
        return False
    if not 0.0 <= receipt.epistemic_uncertainty <= 1.0:
        return False
    if receipt.remembered_prediction_error < 0.0:
        return False
    if receipt.uses_evaluator_labels or not receipt.future_outcome_unknown:
        return False
    if receipt.memory_available:
        if any(
            value is None
            for value in (
                receipt.identity_id,
                receipt.episode_id,
                receipt.temporal_commit_digest,
                receipt.temporal_authorization_digest,
                receipt.memory_digest,
                receipt.memory_source_signature,
            )
        ):
            return False
    if receipt.boundary_attribution_available and not receipt.memory_available:
        # Fresh boundary discovery occurs only after a requested refinement;
        # the pre-refinement state cannot claim a boundary without memory.
        return False
    if receipt.intervention_mode in {"intact", "feedback_cut"}:
        if not (
            receipt.memory_available
            and receipt.boundary_attribution_available
            and receipt.metacognition_available
            and receipt.planner_binding_available
            and receipt.memory_source_key_matches_target
        ):
            return False
    if receipt.intervention_mode == "provenance_cut":
        if not receipt.memory_available or receipt.memory_source_key_matches_target:
            return False
    if receipt.intervention_mode == "memory_cut" and receipt.memory_available:
        return False
    if receipt.intervention_mode == "boundary_cut" and receipt.boundary_attribution_available:
        return False
    if receipt.intervention_mode == "metacognition_cut" and receipt.metacognition_available:
        return False
    if receipt.intervention_mode == "planner_binding_cut" and receipt.planner_binding_available:
        return False
    if receipt.intervention_mode == "joint_cut" and any(
        (
            receipt.memory_available,
            receipt.boundary_attribution_available,
            receipt.metacognition_available,
            receipt.planner_binding_available,
        )
    ):
        return False
    return bool(
        _valid_sha256(receipt.digest)
        and receipt.digest == _digest(_integrated_payload(receipt))
    )


@dataclass(frozen=True)
class WholeLoopPlanningReceipt:
    """Action commitment bound to an integrated self-model state."""

    schema: str
    sequence_id: int
    time: int
    target_signature: Signature
    intervention_mode: WholeLoopInterventionMode
    integrated_self_model_digest: str
    evidence_digest: str
    boundary_memory_digest: str | None
    boundary_certificate_digest: str | None
    candidate_keys: tuple[str, ...]
    route_estimates: tuple[float, ...]
    predicted_external_returns: tuple[float, ...]
    selected_index: int
    selected_key: str
    predicted_selected_return: float
    planner_mode: Literal["causal_self_model", "snapshot_control"]
    total_samples_per_candidate: int
    refinement_used: bool
    temporal_authorization_digest: str | None
    self_model_authorized: bool
    future_outcome_unknown: bool
    uses_evaluator_labels: bool
    digest: str


def _planning_payload(receipt: WholeLoopPlanningReceipt) -> dict[str, Any]:
    payload = asdict(receipt)
    payload.pop("digest", None)
    return payload


def validate_whole_loop_planning_receipt(
    receipt: WholeLoopPlanningReceipt,
) -> bool:
    if not isinstance(receipt, WholeLoopPlanningReceipt):
        return False
    if receipt.schema != "rrct.v043.whole_loop_planning.v1":
        return False
    if receipt.sequence_id < 0 or receipt.time < 0:
        return False
    if not _valid_signature(receipt.target_signature):
        return False
    if receipt.intervention_mode not in WHOLE_LOOP_MODES:
        return False
    if not _valid_sha256(receipt.integrated_self_model_digest):
        return False
    if not _valid_sha256(receipt.evidence_digest):
        return False
    if any(
        value is not None and not _valid_sha256(value)
        for value in (
            receipt.boundary_memory_digest,
            receipt.boundary_certificate_digest,
        )
    ):
        return False
    if receipt.planner_mode == "causal_self_model":
        if (
            receipt.boundary_memory_digest is None
            or receipt.boundary_certificate_digest is None
        ):
            return False
    elif (
        receipt.boundary_memory_digest is not None
        or receipt.boundary_certificate_digest is not None
    ):
        return False
    if not receipt.candidate_keys:
        return False
    n = len(receipt.candidate_keys)
    if len(receipt.route_estimates) != n or len(receipt.predicted_external_returns) != n:
        return False
    if receipt.selected_index < 0 or receipt.selected_index >= n:
        return False
    if receipt.selected_key != receipt.candidate_keys[receipt.selected_index]:
        return False
    if receipt.planner_mode not in {"causal_self_model", "snapshot_control"}:
        return False
    if receipt.total_samples_per_candidate <= 0:
        return False
    if not all(
        np.isfinite(value)
        for value in (
            *receipt.route_estimates,
            *receipt.predicted_external_returns,
            receipt.predicted_selected_return,
        )
    ):
        return False
    if receipt.predicted_selected_return != receipt.predicted_external_returns[
        receipt.selected_index
    ]:
        return False
    if receipt.temporal_authorization_digest is not None and not _valid_sha256(
        receipt.temporal_authorization_digest
    ):
        return False
    if receipt.self_model_authorized and receipt.temporal_authorization_digest is None:
        return False
    if receipt.future_outcome_unknown is not True or receipt.uses_evaluator_labels:
        return False
    return bool(
        _valid_sha256(receipt.digest)
        and receipt.digest == _digest(_planning_payload(receipt))
    )


@dataclass(frozen=True)
class WholeLoopOutcomeReceipt:
    """Post-outcome update closing action back into persistent self state."""

    schema: str
    sequence_id: int
    reveal_time: int
    planning_digest: str
    integrated_self_model_digest: str
    selected_key: str
    realized_external_return: float
    predicted_external_return: float
    absolute_prediction_error: float
    memory_before_digest: str | None
    memory_after_digest: str | None
    outcome_update_applied: bool
    provenance_safe_update: bool
    uses_evaluator_labels: bool
    digest: str


def _outcome_payload(receipt: WholeLoopOutcomeReceipt) -> dict[str, Any]:
    payload = asdict(receipt)
    payload.pop("digest", None)
    return payload


def validate_whole_loop_outcome_receipt(
    receipt: WholeLoopOutcomeReceipt,
) -> bool:
    if not isinstance(receipt, WholeLoopOutcomeReceipt):
        return False
    if receipt.schema != "rrct.v043.whole_loop_outcome.v1":
        return False
    if receipt.sequence_id < 0 or receipt.reveal_time < 0:
        return False
    if not _valid_sha256(receipt.planning_digest):
        return False
    if not _valid_sha256(receipt.integrated_self_model_digest):
        return False
    for value in (receipt.memory_before_digest, receipt.memory_after_digest):
        if value is not None and not _valid_sha256(value):
            return False
    if not receipt.selected_key:
        return False
    if not all(
        np.isfinite(value)
        for value in (
            receipt.realized_external_return,
            receipt.predicted_external_return,
            receipt.absolute_prediction_error,
        )
    ):
        return False
    if receipt.absolute_prediction_error < 0.0:
        return False
    if not np.isclose(
        receipt.absolute_prediction_error,
        abs(receipt.realized_external_return - receipt.predicted_external_return),
        rtol=0.0,
        atol=1e-12,
    ):
        return False
    if receipt.outcome_update_applied:
        if receipt.memory_before_digest is None or receipt.memory_after_digest is None:
            return False
        if receipt.memory_before_digest == receipt.memory_after_digest:
            return False
    if receipt.uses_evaluator_labels:
        return False
    return bool(
        _valid_sha256(receipt.digest)
        and receipt.digest == _digest(_outcome_payload(receipt))
    )


def validate_whole_loop_receipt_chain(
    state: IntegratedSelfModelReceipt,
    plan: WholeLoopPlanningReceipt,
    outcome: WholeLoopOutcomeReceipt | None = None,
) -> bool:
    """Validate the cross-receipt chain, not merely individual hashes."""

    if not validate_integrated_self_model_receipt(state):
        return False
    if not validate_whole_loop_planning_receipt(plan):
        return False
    if state.sequence_id != plan.sequence_id:
        return False
    if state.time != plan.time:
        return False
    if state.target_signature != plan.target_signature:
        return False
    if state.intervention_mode != plan.intervention_mode:
        return False
    if state.digest != plan.integrated_self_model_digest:
        return False
    if state.refinement_requested != plan.refinement_used:
        return False
    if state.planner_binding_available:
        if plan.planner_mode != "causal_self_model":
            return False
        if not plan.self_model_authorized:
            return False
        if plan.temporal_authorization_digest != state.temporal_authorization_digest:
            return False
        if state.memory_digest is not None:
            if plan.boundary_memory_digest != state.memory_digest:
                return False
            if plan.boundary_certificate_digest != state.boundary_certificate_digest:
                return False
        elif state.intervention_mode != "memory_cut":
            return False
    else:
        if plan.planner_mode != "snapshot_control":
            return False
        if plan.self_model_authorized:
            return False
        if (
            plan.boundary_memory_digest is not None
            or plan.boundary_certificate_digest is not None
        ):
            return False
    if outcome is None:
        return True
    if not validate_whole_loop_outcome_receipt(outcome):
        return False
    if outcome.sequence_id != plan.sequence_id:
        return False
    if outcome.reveal_time <= plan.time:
        return False
    if outcome.planning_digest != plan.digest:
        return False
    if outcome.integrated_self_model_digest != state.digest:
        return False
    if outcome.selected_key != plan.selected_key:
        return False
    expected_update = state.intervention_mode not in {"feedback_cut", "joint_cut"}
    if outcome.outcome_update_applied != expected_update:
        return False
    expected_provenance_safe = state.intervention_mode not in {
        "feedback_cut",
        "provenance_cut",
        "joint_cut",
    }
    if outcome.provenance_safe_update != expected_provenance_safe:
        return False
    return True


@dataclass
class _PendingDecision:
    state: IntegratedSelfModelReceipt
    candidates: tuple[WholeLoopActionCandidate, ...]
    coarse_preview: CausalPreviewReceipt
    memory: IdentityBoundaryMemoryReceipt | None


class WholeLoopCausalClosureController:
    """Persistent, receipt-bound bridge from temporal identity to action.

    The controller never receives scenario labels, hidden route truth, oracle
    choices, or realized future returns before action commitment.  Its active
    information request is computed from the score margin, prior calibration
    error, and remembered boundary uncertainty.
    """

    def __init__(self, config: WholeLoopClosureConfig | None = None) -> None:
        self.config = config or WholeLoopClosureConfig()
        if not isinstance(self.config, WholeLoopClosureConfig):
            raise TypeError("config must be WholeLoopClosureConfig")
        self._memory_by_key: dict[CanonicalKey, IdentityBoundaryMemoryReceipt] = {}
        self._memory_sequence = 0
        self._decision_sequence = 0
        self._pending: dict[int, _PendingDecision] = {}
        self._last_state: IntegratedSelfModelReceipt | None = None
        self._last_plan: WholeLoopPlanningReceipt | None = None
        self._last_outcome: WholeLoopOutcomeReceipt | None = None

    @property
    def identity_count(self) -> int:
        return len(self._memory_by_key)

    @property
    def last_integrated_state(self) -> IntegratedSelfModelReceipt | None:
        return copy.deepcopy(self._last_state)

    @property
    def last_plan(self) -> WholeLoopPlanningReceipt | None:
        return copy.deepcopy(self._last_plan)

    @property
    def last_outcome(self) -> WholeLoopOutcomeReceipt | None:
        return copy.deepcopy(self._last_outcome)

    def memory_snapshot(self) -> tuple[IdentityBoundaryMemoryReceipt, ...]:
        return tuple(
            copy.deepcopy(self._memory_by_key[key])
            for key in sorted(self._memory_by_key, key=repr)
        )

    def register_grounded_identity(
        self,
        commit: SelfModelCommitEventReceipt,
        authorization: SelfModelActionAuthorizationReceipt,
        certificate: PublicBoundaryCertificate,
    ) -> IdentityBoundaryMemoryReceipt:
        """Install one grounded v0.42 identity and its public boundary model."""

        if not validate_self_model_commit_event_receipt(commit):
            raise ValueError("invalid v0.42 commit receipt")
        if not validate_self_model_action_authorization_receipt(authorization):
            raise ValueError("invalid v0.42 authorization receipt")
        if not validate_public_boundary_certificate(certificate):
            raise ValueError("invalid public boundary certificate")
        if authorization.commit_event_digest != commit.digest:
            raise ValueError("authorization is not bound to the commit")
        if authorization.identity_id != commit.identity_id:
            raise ValueError("authorization identity mismatch")
        if authorization.episode_id != commit.episode_id:
            raise ValueError("authorization episode mismatch")
        if authorization.target_signature != commit.target_signature:
            raise ValueError("authorization signature mismatch")
        if authorization.certificate_digest != commit.certificate_digest:
            raise ValueError("authorization certificate mismatch")
        if certificate.digest != commit.certificate_digest:
            raise ValueError("boundary certificate is not the committed certificate")
        key = _canonical_key(commit.target_signature)
        if key is None:
            raise ValueError("commit has no canonical key")
        source = _readonly(certificate.internal_projector)
        sensory = _readonly(certificate.sensory_projector)
        effect = _readonly(certificate.effect_operator)
        norm = float(np.linalg.norm(source @ effect @ sensory, ord="fro"))
        if not np.isfinite(norm) or norm <= 1e-12:
            raise ValueError("boundary normalization path is degenerate")
        payload = {
            "schema": "rrct.v043.identity_boundary_memory.v1",
            "sequence_id": self._memory_sequence,
            "canonical_key": key,
            "source_signature": commit.target_signature,
            "identity_id": commit.identity_id,
            "episode_id": commit.episode_id,
            "temporal_commit_digest": commit.digest,
            "temporal_authorization_digest": authorization.digest,
            "boundary_certificate_digest": certificate.digest,
            "source_projector": source,
            "sensory_projector": sensory,
            "normalization_effect": effect,
            "normalization_norm": norm,
            "confidence": float(certificate.confidence),
            "uncertainty": float(certificate.uncertainty),
            "change_alarm": float(certificate.change_alarm),
            "calibration_error": 0.0,
            "outcome_update_count": 0,
            "previous_update_digest": None,
        }
        memory = IdentityBoundaryMemoryReceipt(**payload, digest=_digest(payload))
        if not validate_identity_boundary_memory_receipt(memory):
            raise RuntimeError("invalid identity boundary memory receipt")
        self._memory_by_key[key] = memory
        self._memory_sequence += 1
        return copy.deepcopy(memory)

    def _wrong_source_memory(
        self, target_key: CanonicalKey
    ) -> IdentityBoundaryMemoryReceipt:
        candidates = [
            memory
            for key, memory in self._memory_by_key.items()
            if key != target_key
        ]
        if not candidates:
            raise RuntimeError("provenance cut requires a nonmatching identity")
        return max(
            candidates,
            key=lambda item: (item.sequence_id, item.identity_id, item.episode_id),
        )

    def _route_estimates(
        self,
        preview: CausalPreviewReceipt,
        memory: IdentityBoundaryMemoryReceipt,
    ) -> tuple[float, ...]:
        effects = np.asarray(preview.effect_operators, dtype=np.float64)
        result: list[float] = []
        for effect in effects:
            routed = memory.source_projector @ effect @ memory.sensory_projector
            value = float(
                np.clip(
                    np.linalg.norm(routed, ord="fro")
                    / (memory.normalization_norm + 1e-12),
                    0.0,
                    self.config.maximum_route_strength,
                )
            )
            result.append(value)
        return tuple(result)

    def _scores(
        self,
        candidates: tuple[WholeLoopActionCandidate, ...],
        route_estimates: Sequence[float],
    ) -> tuple[float, ...]:
        return tuple(
            float(
                candidate.immediate_external_value
                + self.config.future_weight
                * max(float(route), candidate.alternative_competence)
            )
            for candidate, route in zip(candidates, route_estimates, strict=True)
        )

    @staticmethod
    def _margin(scores: Sequence[float]) -> float:
        ordered = np.sort(np.asarray(scores, dtype=np.float64))
        if len(ordered) < 2:
            return float("inf")
        return float(ordered[-1] - ordered[-2])

    @staticmethod
    def _validate_candidates(
        candidates: Sequence[WholeLoopActionCandidate],
    ) -> tuple[WholeLoopActionCandidate, ...]:
        result = tuple(candidates)
        if len(result) < 2:
            raise ValueError("at least two candidates are required")
        if not all(isinstance(item, WholeLoopActionCandidate) for item in result):
            raise TypeError("candidates must be WholeLoopActionCandidate values")
        keys = tuple(item.key for item in result)
        if len(set(keys)) != len(keys):
            raise ValueError("candidate keys must be unique")
        return result

    def begin_decision(
        self,
        *,
        time: int,
        target_signature: Signature,
        candidates: Sequence[WholeLoopActionCandidate],
        coarse_preview: CausalPreviewReceipt,
        intervention_mode: WholeLoopInterventionMode = "intact",
    ) -> IntegratedSelfModelReceipt:
        """Build a state and decide whether more evidence is needed.

        This method is called before a refined preview or realized task return
        exists.  A returned ``refinement_requested`` value is therefore a true
        active-information decision rather than a retrospective annotation.
        """

        if intervention_mode not in WHOLE_LOOP_MODES:
            raise ValueError("unknown whole-loop intervention mode")
        parsed_time = _integer(time, "time")
        if not _valid_signature(target_signature):
            raise ValueError("invalid target signature")
        target_key = _canonical_key(target_signature)
        if target_key is None:
            raise ValueError("target signature has no canonical key")
        values = self._validate_candidates(candidates)
        if not validate_causal_preview_receipt(coarse_preview):
            raise ValueError("invalid coarse preview")
        if coarse_preview.refinement_level != "coarse":
            raise ValueError("begin_decision requires a coarse preview")
        if coarse_preview.sample_count != self.config.coarse_samples:
            raise ValueError("coarse preview sample count differs from frozen config")
        if coarse_preview.time != parsed_time:
            raise ValueError("coarse preview time mismatch")
        if coarse_preview.target_signature != target_signature:
            raise ValueError("coarse preview signature mismatch")
        keys = tuple(item.key for item in values)
        if coarse_preview.candidate_keys != keys:
            raise ValueError("coarse preview candidate order mismatch")

        correct_memory = self._memory_by_key.get(target_key)
        if intervention_mode == "provenance_cut":
            binding_memory = self._wrong_source_memory(target_key)
            memory = binding_memory
        elif intervention_mode == "memory_cut":
            # Preserve the currently grounded temporal authorization while
            # withholding the remembered boundary model itself.
            binding_memory = correct_memory
            memory = None
        elif intervention_mode == "joint_cut":
            binding_memory = None
            memory = None
        else:
            binding_memory = correct_memory
            memory = correct_memory
        if intervention_mode not in {"joint_cut"} and binding_memory is None:
            raise RuntimeError("target identity has no grounded temporal binding")
        if intervention_mode not in {"memory_cut", "joint_cut"} and memory is None:
            raise RuntimeError("target identity has no grounded memory")

        memory_available = memory is not None
        source_matches = bool(
            binding_memory is not None
            and binding_memory.canonical_key == target_key
        )
        boundary_available = bool(
            memory_available
            and intervention_mode not in {"boundary_cut", "joint_cut"}
        )
        metacognition_available = intervention_mode not in {
            "metacognition_cut",
            "joint_cut",
        }
        planner_binding_available = intervention_mode not in {
            "planner_binding_cut",
            "boundary_cut",
            "joint_cut",
        }

        if boundary_available and memory is not None:
            route_estimates = self._route_estimates(coarse_preview, memory)
        else:
            route_estimates = tuple(
                float(item.snapshot_similarity) for item in values
            )
        scores = self._scores(values, route_estimates)
        margin = self._margin(scores)
        remembered_error = 0.0 if memory is None else float(memory.calibration_error)
        base_uncertainty = 1.0 - float(
            np.clip(margin / self.config.refinement_margin, 0.0, 1.0)
        )
        if memory is not None:
            base_uncertainty = max(
                base_uncertainty,
                float(memory.uncertainty),
                float(memory.change_alarm),
                float(
                    np.clip(
                        remembered_error
                        / self.config.calibration_alarm_threshold,
                        0.0,
                        1.0,
                    )
                ),
            )
        if not metacognition_available:
            epistemic_uncertainty = 0.0
            refinement_requested = False
        elif intervention_mode == "memory_cut":
            epistemic_uncertainty = 1.0
            refinement_requested = True
        elif not boundary_available:
            epistemic_uncertainty = 1.0
            refinement_requested = False
        else:
            epistemic_uncertainty = float(np.clip(base_uncertainty, 0.0, 1.0))
            refinement_requested = bool(
                margin < self.config.refinement_margin
                or remembered_error > self.config.calibration_alarm_threshold
            )

        payload = {
            "schema": "rrct.v043.integrated_self_model.v1",
            "sequence_id": self._decision_sequence,
            "time": parsed_time,
            "target_signature": target_signature,
            "target_canonical_key": target_key,
            "intervention_mode": intervention_mode,
            "identity_id": (
                None if binding_memory is None else binding_memory.identity_id
            ),
            "episode_id": (
                None if binding_memory is None else binding_memory.episode_id
            ),
            "temporal_commit_digest": (
                None
                if binding_memory is None
                else binding_memory.temporal_commit_digest
            ),
            "temporal_authorization_digest": (
                None
                if binding_memory is None
                else binding_memory.temporal_authorization_digest
            ),
            "memory_digest": None if memory is None else memory.digest,
            "memory_source_signature": (
                None if binding_memory is None else binding_memory.source_signature
            ),
            "memory_source_key_matches_target": source_matches,
            "boundary_certificate_digest": (
                None if not boundary_available or memory is None
                else memory.boundary_certificate_digest
            ),
            "coarse_preview_digest": coarse_preview.digest,
            "candidate_keys": keys,
            "coarse_route_estimates": tuple(float(value) for value in route_estimates),
            "coarse_policy_scores": tuple(float(value) for value in scores),
            "score_margin": float(margin),
            "epistemic_uncertainty": float(epistemic_uncertainty),
            "remembered_prediction_error": remembered_error,
            "memory_available": memory_available,
            "boundary_attribution_available": boundary_available,
            "metacognition_available": metacognition_available,
            "planner_binding_available": planner_binding_available,
            "refinement_requested": refinement_requested,
            "previous_update_digest": (
                None
                if binding_memory is None
                else binding_memory.previous_update_digest
            ),
            "future_outcome_unknown": True,
            "uses_evaluator_labels": False,
        }
        state = IntegratedSelfModelReceipt(**payload, digest=_digest(payload))
        if not validate_integrated_self_model_receipt(state):
            raise RuntimeError("invalid integrated self-model receipt")
        self._pending[state.sequence_id] = _PendingDecision(
            state=state,
            candidates=values,
            coarse_preview=copy.deepcopy(coarse_preview),
            memory=copy.deepcopy(memory),
        )
        self._decision_sequence += 1
        self._last_state = state
        return copy.deepcopy(state)

    def commit_decision(
        self,
        state: IntegratedSelfModelReceipt,
        *,
        refined_preview: CausalPreviewReceipt | None = None,
        fresh_boundary_certificate: PublicBoundaryCertificate | None = None,
    ) -> WholeLoopPlanningReceipt:
        """Commit an action after exactly the evidence requested by the state."""

        if not validate_integrated_self_model_receipt(state):
            raise ValueError("invalid integrated state")
        pending = self._pending.get(state.sequence_id)
        if pending is None or pending.state.digest != state.digest:
            raise RuntimeError("state is not a live pending decision")
        if state.refinement_requested:
            if refined_preview is None:
                raise RuntimeError("requested refined evidence is missing")
            if not validate_causal_preview_receipt(refined_preview):
                raise ValueError("invalid refined preview")
            if refined_preview.refinement_level != "refined":
                raise ValueError("refined preview has wrong level")
            if refined_preview.sample_count != self.config.refined_samples:
                raise ValueError("refined sample count differs from frozen config")
            if refined_preview.time != state.time:
                raise ValueError("refined preview time mismatch")
            if refined_preview.target_signature != state.target_signature:
                raise ValueError("refined preview signature mismatch")
            if refined_preview.candidate_keys != state.candidate_keys:
                raise ValueError("refined preview candidate mismatch")
            evidence = refined_preview
        else:
            if refined_preview is not None or fresh_boundary_certificate is not None:
                raise ValueError("unrequested future evidence cannot enter the decision")
            evidence = pending.coarse_preview

        memory = pending.memory
        if state.intervention_mode == "memory_cut":
            if fresh_boundary_certificate is None:
                raise RuntimeError("memory cut requires fresh boundary rediscovery")
            if not validate_public_boundary_certificate(fresh_boundary_certificate):
                raise ValueError("invalid freshly rediscovered boundary")
            if (
                _canonical_key(fresh_boundary_certificate.structural_signature)
                != state.target_canonical_key
            ):
                raise ValueError("fresh boundary belongs to a different identity")
            source = _readonly(fresh_boundary_certificate.internal_projector)
            sensory = _readonly(fresh_boundary_certificate.sensory_projector)
            effect = _readonly(fresh_boundary_certificate.effect_operator)
            norm = float(np.linalg.norm(source @ effect @ sensory, ord="fro"))
            if norm <= 1e-12:
                raise ValueError("fresh boundary normalization path is degenerate")
            # A transient record permits planning but is not installed as an
            # identity memory until an outcome is observed.
            transient_payload = {
                "schema": "rrct.v043.identity_boundary_memory.v1",
                "sequence_id": self._memory_sequence,
                "canonical_key": state.target_canonical_key,
                "source_signature": fresh_boundary_certificate.structural_signature,
                # Boundary memory is withheld, not temporal identity.  The
                # freshly estimated boundary must remain bound to the exact
                # v0.42 identity episode that authorized this decision.
                "identity_id": state.identity_id,
                "episode_id": state.episode_id,
                "temporal_commit_digest": state.temporal_commit_digest,
                "temporal_authorization_digest": state.temporal_authorization_digest,
                "boundary_certificate_digest": fresh_boundary_certificate.digest,
                "source_projector": source,
                "sensory_projector": sensory,
                "normalization_effect": effect,
                "normalization_norm": norm,
                "confidence": float(fresh_boundary_certificate.confidence),
                "uncertainty": float(fresh_boundary_certificate.uncertainty),
                "change_alarm": float(fresh_boundary_certificate.change_alarm),
                "calibration_error": 0.0,
                "outcome_update_count": 0,
                "previous_update_digest": None,
            }
            memory = IdentityBoundaryMemoryReceipt(
                **transient_payload,
                digest=_digest(transient_payload),
            )
            if not validate_identity_boundary_memory_receipt(memory):
                raise RuntimeError("invalid transient fresh boundary memory")
        elif fresh_boundary_certificate is not None:
            raise ValueError("fresh boundary is only valid for memory_cut")

        causal_planner = state.planner_binding_available
        if causal_planner:
            if memory is None:
                raise RuntimeError("causal planner lacks a boundary memory")
            route_estimates = self._route_estimates(evidence, memory)
            planner_mode: Literal["causal_self_model", "snapshot_control"] = (
                "causal_self_model"
            )
        else:
            route_estimates = tuple(
                float(item.snapshot_similarity) for item in pending.candidates
            )
            planner_mode = "snapshot_control"
        scores = self._scores(pending.candidates, route_estimates)
        selected_index = int(np.argmax(np.asarray(scores, dtype=np.float64)))
        selected_key = pending.candidates[selected_index].key
        temporal_authorization = (
            state.temporal_authorization_digest if causal_planner else None
        )
        payload = {
            "schema": "rrct.v043.whole_loop_planning.v1",
            "sequence_id": state.sequence_id,
            "time": state.time,
            "target_signature": state.target_signature,
            "intervention_mode": state.intervention_mode,
            "integrated_self_model_digest": state.digest,
            "evidence_digest": evidence.digest,
            "boundary_memory_digest": (
                None if not causal_planner or memory is None else memory.digest
            ),
            "boundary_certificate_digest": (
                None
                if not causal_planner or memory is None
                else memory.boundary_certificate_digest
            ),
            "candidate_keys": state.candidate_keys,
            "route_estimates": tuple(float(value) for value in route_estimates),
            "predicted_external_returns": tuple(float(value) for value in scores),
            "selected_index": selected_index,
            "selected_key": selected_key,
            "predicted_selected_return": float(scores[selected_index]),
            "planner_mode": planner_mode,
            "total_samples_per_candidate": int(evidence.sample_count),
            "refinement_used": bool(state.refinement_requested),
            "temporal_authorization_digest": temporal_authorization,
            "self_model_authorized": bool(causal_planner),
            "future_outcome_unknown": True,
            "uses_evaluator_labels": False,
        }
        plan = WholeLoopPlanningReceipt(**payload, digest=_digest(payload))
        if not validate_whole_loop_receipt_chain(state, plan):
            raise RuntimeError("invalid whole-loop planning chain")
        # Preserve a transient memory for the post-outcome update.
        pending.memory = memory
        self._last_plan = plan
        return copy.deepcopy(plan)

    def observe_outcome(
        self,
        state: IntegratedSelfModelReceipt,
        plan: WholeLoopPlanningReceipt,
        realized_external_return: float,
        *,
        reveal_time: int | None = None,
    ) -> WholeLoopOutcomeReceipt:
        """Reveal the external task return and update future self uncertainty."""

        if not validate_whole_loop_receipt_chain(state, plan):
            raise ValueError("invalid state-to-plan chain")
        pending = self._pending.get(state.sequence_id)
        if pending is None:
            raise RuntimeError("decision has no pending outcome")
        value = _finite(realized_external_return, "realized_external_return")
        parsed_reveal = (
            state.time + 1
            if reveal_time is None
            else _integer(reveal_time, "reveal_time")
        )
        if parsed_reveal <= state.time:
            raise ValueError("outcome must be revealed after commitment")
        error = abs(value - plan.predicted_selected_return)
        memory = pending.memory
        before_digest = None if memory is None else memory.digest
        update_applied = bool(
            memory is not None and state.intervention_mode != "feedback_cut"
        )
        provenance_safe = bool(
            update_applied
            and memory is not None
            and memory.canonical_key == state.target_canonical_key
        )
        after: IdentityBoundaryMemoryReceipt | None = None
        if update_applied and memory is not None:
            rate = self.config.calibration_update_rate
            calibration_error = float(
                (1.0 - rate) * memory.calibration_error + rate * error
            )
            uncertainty = float(
                np.clip(
                    max(memory.uncertainty * (1.0 - 0.5 * rate), calibration_error),
                    0.0,
                    1.0,
                )
            )
            payload = {
                **_memory_payload(memory),
                "sequence_id": self._memory_sequence,
                "calibration_error": calibration_error,
                "uncertainty": uncertainty,
                "change_alarm": float(
                    np.clip(
                        error / self.config.calibration_alarm_threshold,
                        0.0,
                        1.0,
                    )
                ),
                "outcome_update_count": memory.outcome_update_count + 1,
                "previous_update_digest": memory.digest,
            }
            after = IdentityBoundaryMemoryReceipt(**payload, digest=_digest(payload))
            if not validate_identity_boundary_memory_receipt(after):
                raise RuntimeError("invalid post-outcome memory update")
            self._memory_sequence += 1
            if provenance_safe:
                self._memory_by_key[state.target_canonical_key] = after
            elif state.intervention_mode == "provenance_cut":
                # The control deliberately permits a wrong-source update.  It
                # remains indexed under its true source key, never relabeled as
                # the target identity.
                self._memory_by_key[memory.canonical_key] = after
        payload = {
            "schema": "rrct.v043.whole_loop_outcome.v1",
            "sequence_id": state.sequence_id,
            "reveal_time": parsed_reveal,
            "planning_digest": plan.digest,
            "integrated_self_model_digest": state.digest,
            "selected_key": plan.selected_key,
            "realized_external_return": value,
            "predicted_external_return": plan.predicted_selected_return,
            "absolute_prediction_error": float(error),
            "memory_before_digest": before_digest,
            "memory_after_digest": None if after is None else after.digest,
            "outcome_update_applied": update_applied,
            "provenance_safe_update": provenance_safe,
            "uses_evaluator_labels": False,
        }
        outcome = WholeLoopOutcomeReceipt(**payload, digest=_digest(payload))
        if not validate_whole_loop_receipt_chain(state, plan, outcome):
            raise RuntimeError("invalid whole-loop outcome chain")
        del self._pending[state.sequence_id]
        self._last_outcome = outcome
        return copy.deepcopy(outcome)

    def snapshot(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "schema": "rrct.v043.whole_loop_causal_closure_runtime.v1",
            "config": self.config,
            "memory": self.memory_snapshot(),
            "memory_sequence": self._memory_sequence,
            "decision_sequence": self._decision_sequence,
            "pending_sequence_ids": tuple(sorted(self._pending)),
            "last_state": self._last_state,
            "last_plan": self._last_plan,
            "last_outcome": self._last_outcome,
            "uses_evaluator_labels": False,
            "explicit_survival_reward": 0.0,
            "explicit_identity_reward": 0.0,
        }
        payload["digest"] = _digest(payload)
        return copy.deepcopy(payload)


__all__ = [
    "CausalPreviewReceipt",
    "IdentityBoundaryMemoryReceipt",
    "IntegratedSelfModelReceipt",
    "WHOLE_LOOP_MODES",
    "WholeLoopActionCandidate",
    "WholeLoopCausalClosureController",
    "WholeLoopClosureConfig",
    "WholeLoopInterventionMode",
    "WholeLoopOutcomeReceipt",
    "WholeLoopPlanningReceipt",
    "make_causal_preview_receipt",
    "validate_causal_preview_receipt",
    "validate_identity_boundary_memory_receipt",
    "validate_integrated_self_model_receipt",
    "validate_public_boundary_certificate",
    "validate_whole_loop_outcome_receipt",
    "validate_whole_loop_planning_receipt",
    "validate_whole_loop_receipt_chain",
]
