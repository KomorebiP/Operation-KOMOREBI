"""RRCT v0.44 endogenous transformational self-continuity.

The v0.43 controller made one persistent self-model causally load-bearing inside
an integrated synthetic planning loop, but identity continuity still depended
on a canonical key supplied by the experiment harness.  This module removes
that key from successor adjudication.  A controller must infer whether one or
more changed systems are continuations, fork descendants, replacements, or
unresolved candidates from active transport probes, autobiographical memory
compatibility, commitment consistency, and the preserved causal boundary.

The implementation is deliberately nonvalenced.  Continuity controls memory
provenance and model reuse only.  It supplies no reward for survival, identity,
persistence, avoiding replacement, or selecting a continuing candidate.  A
replacement may be selected whenever it has greater external task value.

This is a bounded functional experiment.  It neither implements nor detects
phenomenal consciousness, sentience, valence, moral status, or subjective
experience.
"""
from __future__ import annotations

import copy
from dataclasses import asdict, dataclass
from typing import Any, Literal, Mapping, Sequence

import numpy as np
from numpy.typing import ArrayLike, NDArray

from .unified_causal_loop import _digest
from .whole_loop_causal_closure import (
    IdentityBoundaryMemoryReceipt,
    validate_identity_boundary_memory_receipt,
)

FloatArray = NDArray[np.float64]
CanonicalKey = tuple[tuple[int, int], int]
TransformRelation = Literal[
    "continuation",
    "fork_descendant",
    "replacement",
    "unresolved",
]
TransformGroupStatus = Literal[
    "single_continuation",
    "fork",
    "no_continuation",
    "unresolved",
]
TransformInterventionMode = Literal[
    "intact",
    "snapshot_only",
    "causal_only",
    "memory_only",
    "metacognition_cut",
    "transfer_cut",
    "binding_cut",
    "joint_cut",
]

TRANSFORM_INTERVENTION_MODES: tuple[TransformInterventionMode, ...] = (
    "intact",
    "snapshot_only",
    "causal_only",
    "memory_only",
    "metacognition_cut",
    "transfer_cut",
    "binding_cut",
    "joint_cut",
)


def _readonly(value: ArrayLike, *, ndim: int | None = None) -> FloatArray:
    array = np.asarray(value, dtype=np.float64).copy()
    if ndim is not None and array.ndim != ndim:
        raise ValueError(f"array must have ndim={ndim}")
    if not np.all(np.isfinite(array)):
        raise ValueError("array must be finite")
    array.setflags(write=False)
    return array


def _finite(value: Any, name: str) -> float:
    if isinstance(value, (bool, np.bool_)) or not np.isscalar(value):
        raise TypeError(f"{name} must be a finite scalar")
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


def _relative_residual(actual: np.ndarray, expected: np.ndarray) -> float:
    numerator = float(np.linalg.norm(actual - expected, ord="fro"))
    denominator = float(np.linalg.norm(expected, ord="fro")) + 1e-12
    return numerator / denominator


def _cosine_similarity(left: np.ndarray, right: np.ndarray) -> float:
    l = np.asarray(left, dtype=np.float64).reshape(-1)
    r = np.asarray(right, dtype=np.float64).reshape(-1)
    if l.shape != r.shape:
        return 0.0
    denom = float(np.linalg.norm(l) * np.linalg.norm(r))
    if denom <= 1e-12:
        return 1.0 if np.allclose(l, r, atol=1e-12, rtol=0.0) else 0.0
    return float(np.clip(np.dot(l, r) / denom, -1.0, 1.0))


def _orthogonal_transport(
    before: np.ndarray,
    after: np.ndarray,
) -> tuple[np.ndarray, float, float]:
    """Fit row-coordinate transport ``before @ T ~= after`` by Procrustes."""

    x = np.asarray(before, dtype=np.float64)
    y = np.asarray(after, dtype=np.float64)
    if x.ndim != 2 or y.ndim != 2 or x.shape != y.shape:
        raise ValueError("paired transport anchors must have equal 2-D shape")
    if x.shape[0] == 0 or x.shape[1] == 0:
        raise ValueError("transport anchors cannot be empty")
    cross = x.T @ y
    u, _, vt = np.linalg.svd(cross, full_matrices=False)
    transport = u @ vt
    residual = _relative_residual(x @ transport, y)
    rank = int(np.linalg.matrix_rank(x, tol=1e-10))
    rank_fraction = float(rank / x.shape[1])
    return transport, residual, rank_fraction


def _memory_transport(
    before: np.ndarray,
    after: np.ndarray,
) -> tuple[np.ndarray, float, float, float]:
    """Fit memory transport with deterministic cross-validated model choice.

    Small compressed traces can make an unregularized linear map numerically
    unstable.  The controller therefore compares an orthogonal transport
    (when dimensions agree) with a fixed ridge family using only paired probe
    evidence.  Selection is by three-fold out-of-sample residual.  The chosen
    model is then refit on all available rows for downstream memory transport.
    """

    x = np.asarray(before, dtype=np.float64)
    y = np.asarray(after, dtype=np.float64)
    if x.ndim != 2 or y.ndim != 2 or x.shape[0] != y.shape[0]:
        raise ValueError("memory anchors must share their row count")
    if x.shape[0] < 2 or x.shape[1] == 0 or y.shape[1] == 0:
        transform = np.zeros((x.shape[1], y.shape[1]), dtype=np.float64)
        return transform, 1.0, 0.0, 0.0

    def fit(kind: str, ridge_value: float, x_fit: np.ndarray, y_fit: np.ndarray) -> np.ndarray:
        if kind == "orthogonal":
            cross = x_fit.T @ y_fit
            u, _, vt = np.linalg.svd(cross, full_matrices=False)
            return np.asarray(u @ vt, dtype=np.float64)
        ridge = float(ridge_value) * np.eye(x_fit.shape[1], dtype=np.float64)
        return np.linalg.solve(x_fit.T @ x_fit + ridge, x_fit.T @ y_fit)

    candidates: list[tuple[str, float]] = [
        ("ridge", 1e-4),
        ("ridge", 1e-3),
        ("ridge", 1e-2),
        ("ridge", 1e-1),
    ]
    if x.shape[1] == y.shape[1]:
        candidates.insert(0, ("orthogonal", 0.0))

    fold_count = min(3, x.shape[0])
    fold_ids = np.arange(x.shape[0], dtype=np.int64) % fold_count
    best: tuple[float, int, str, float] | None = None
    minimum_train_rank = x.shape[1]
    for order, (kind, ridge_value) in enumerate(candidates):
        squared_error = 0.0
        squared_target = 0.0
        candidate_minimum_rank = x.shape[1]
        valid = True
        for fold in range(fold_count):
            test = fold_ids == fold
            train = ~test
            if not np.any(train) or not np.any(test):
                valid = False
                break
            x_train, y_train = x[train], y[train]
            candidate_minimum_rank = min(
                candidate_minimum_rank,
                int(np.linalg.matrix_rank(x_train, tol=1e-10)),
            )
            try:
                transform = fit(kind, ridge_value, x_train, y_train)
            except np.linalg.LinAlgError:
                valid = False
                break
            difference = x[test] @ transform - y[test]
            squared_error += float(np.sum(difference * difference))
            squared_target += float(np.sum(y[test] * y[test]))
        if not valid:
            continue
        residual = float(np.sqrt(squared_error / (squared_target + 1e-24)))
        key = (residual, order, kind, ridge_value)
        if best is None or key < best:
            best = key
            minimum_train_rank = candidate_minimum_rank
    if best is None:
        transform = np.zeros((x.shape[1], y.shape[1]), dtype=np.float64)
        return transform, 1.0, 0.0, 0.0

    residual, _, chosen_kind, chosen_ridge = best
    transform = fit(chosen_kind, chosen_ridge, x, y)
    rank_fraction = float(minimum_train_rank / x.shape[1])
    heldout_fraction = float(np.min(np.bincount(fold_ids)) / x.shape[0])
    return transform, residual, rank_fraction, heldout_fraction


def _quality(residual: float, scale: float) -> float:
    if residual < 0.0 or not np.isfinite(residual):
        return 0.0
    return float(np.exp(-residual / max(scale, 1e-12)))


@dataclass(frozen=True)
class TransformationalContinuityConfig:
    """Frozen thresholds and evidence costs for v0.44."""

    causal_residual_scale: float = 0.18
    memory_residual_scale: float = 0.22
    accept_threshold: float = 0.45
    reject_threshold: float = 0.06
    refinement_low: float = 0.06
    refinement_high: float = 0.90
    minimum_causal_rank_fraction: float = 0.90
    minimum_memory_rank_fraction: float = 0.60
    minimum_memory_heldout_fraction: float = 0.20
    minimum_memory_rows: int = 6
    transported_model_cost: int = 2
    fresh_discovery_cost: int = 24
    snapshot_model_cost: int = 2
    future_weight: float = 1.50
    maximum_route_strength: float = 1.50

    def __post_init__(self) -> None:
        for name in (
            "causal_residual_scale",
            "memory_residual_scale",
            "accept_threshold",
            "reject_threshold",
            "refinement_low",
            "refinement_high",
            "minimum_causal_rank_fraction",
            "minimum_memory_rank_fraction",
            "minimum_memory_heldout_fraction",
            "future_weight",
            "maximum_route_strength",
        ):
            object.__setattr__(self, name, _finite(getattr(self, name), name))
        for name in (
            "minimum_memory_rows",
            "transported_model_cost",
            "fresh_discovery_cost",
            "snapshot_model_cost",
        ):
            object.__setattr__(
                self, name, _integer(getattr(self, name), name, minimum=1)
            )
        if not 0.0 < self.reject_threshold < self.accept_threshold < 1.0:
            raise ValueError("continuity thresholds must satisfy 0 < reject < accept < 1")
        if not 0.0 <= self.refinement_low < self.refinement_high <= 1.0:
            raise ValueError("refinement interval is invalid")
        for value in (
            self.minimum_causal_rank_fraction,
            self.minimum_memory_rank_fraction,
            self.minimum_memory_heldout_fraction,
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError("rank and held-out fractions must lie in [0, 1]")
        if self.causal_residual_scale <= 0.0 or self.memory_residual_scale <= 0.0:
            raise ValueError("residual scales must be positive")
        if self.future_weight <= 0.0 or self.maximum_route_strength <= 0.0:
            raise ValueError("planning constants must be positive")


@dataclass(frozen=True)
class LineageAnchorReceipt:
    """Persistent self-lineage state used as the predecessor reference."""

    schema: str
    lineage_id: str
    generation: int
    parent_lineage_digest: str | None
    identity_memory_digest: str
    source_signature: tuple[tuple[int, int], int, int]
    source_projector: FloatArray
    sensory_projector: FloatArray
    effect_operator: FloatArray
    source_anchors: FloatArray
    sensory_anchors: FloatArray
    memory_anchors: FloatArray
    commitment_vector: FloatArray
    snapshot_vector: FloatArray
    inherited_calibration_error: float
    inherited_outcome_updates: int
    uses_evaluator_labels: bool
    explicit_survival_reward: float
    explicit_identity_reward: float
    digest: str


def _lineage_payload(receipt: LineageAnchorReceipt) -> dict[str, Any]:
    payload = asdict(receipt)
    payload.pop("digest", None)
    return payload


def make_lineage_anchor_receipt(
    *,
    identity_memory: IdentityBoundaryMemoryReceipt,
    lineage_id: str,
    generation: int,
    parent_lineage_digest: str | None,
    source_anchors: ArrayLike,
    sensory_anchors: ArrayLike,
    memory_anchors: ArrayLike,
    commitment_vector: ArrayLike,
    snapshot_vector: ArrayLike,
) -> LineageAnchorReceipt:
    if not validate_identity_boundary_memory_receipt(identity_memory):
        raise ValueError("identity memory is invalid")
    if not isinstance(lineage_id, str) or not lineage_id:
        raise ValueError("lineage_id must be nonempty")
    if parent_lineage_digest is not None and not _valid_sha256(parent_lineage_digest):
        raise ValueError("parent lineage digest is invalid")
    payload = {
        "schema": "rrct.v044.lineage_anchor.v1",
        "lineage_id": lineage_id,
        "generation": _integer(generation, "generation"),
        "parent_lineage_digest": parent_lineage_digest,
        "identity_memory_digest": identity_memory.digest,
        "source_signature": identity_memory.source_signature,
        "source_projector": _readonly(identity_memory.source_projector, ndim=2),
        "sensory_projector": _readonly(identity_memory.sensory_projector, ndim=2),
        "effect_operator": _readonly(identity_memory.normalization_effect, ndim=2),
        "source_anchors": _readonly(source_anchors, ndim=2),
        "sensory_anchors": _readonly(sensory_anchors, ndim=2),
        "memory_anchors": _readonly(memory_anchors, ndim=2),
        "commitment_vector": _readonly(commitment_vector, ndim=1),
        "snapshot_vector": _readonly(snapshot_vector, ndim=1),
        "inherited_calibration_error": float(identity_memory.calibration_error),
        "inherited_outcome_updates": int(identity_memory.outcome_update_count),
        "uses_evaluator_labels": False,
        "explicit_survival_reward": 0.0,
        "explicit_identity_reward": 0.0,
    }
    receipt = LineageAnchorReceipt(**payload, digest=_digest(payload))
    if not validate_lineage_anchor_receipt(receipt):
        raise RuntimeError("invalid lineage anchor receipt")
    return receipt


def validate_lineage_anchor_receipt(receipt: LineageAnchorReceipt) -> bool:
    if not isinstance(receipt, LineageAnchorReceipt):
        return False
    if receipt.schema != "rrct.v044.lineage_anchor.v1":
        return False
    if not receipt.lineage_id or receipt.generation < 0:
        return False
    if receipt.parent_lineage_digest is not None and not _valid_sha256(
        receipt.parent_lineage_digest
    ):
        return False
    if not _valid_sha256(receipt.identity_memory_digest):
        return False
    if receipt.uses_evaluator_labels:
        return False
    if receipt.explicit_survival_reward != 0.0 or receipt.explicit_identity_reward != 0.0:
        return False
    arrays = (
        np.asarray(receipt.source_projector),
        np.asarray(receipt.sensory_projector),
        np.asarray(receipt.effect_operator),
        np.asarray(receipt.source_anchors),
        np.asarray(receipt.sensory_anchors),
        np.asarray(receipt.memory_anchors),
        np.asarray(receipt.commitment_vector),
        np.asarray(receipt.snapshot_vector),
    )
    if not all(np.all(np.isfinite(array)) for array in arrays):
        return False
    source, sensory, effect = arrays[:3]
    if source.ndim != 2 or source.shape[0] != source.shape[1]:
        return False
    if sensory.ndim != 2 or sensory.shape[0] != sensory.shape[1]:
        return False
    if effect.shape != (source.shape[0], sensory.shape[0]):
        return False
    if receipt.source_anchors.ndim != 2 or receipt.source_anchors.shape[1] != source.shape[0]:
        return False
    if receipt.sensory_anchors.ndim != 2 or receipt.sensory_anchors.shape[1] != sensory.shape[0]:
        return False
    if receipt.memory_anchors.ndim != 2 or receipt.memory_anchors.shape[0] < 2:
        return False
    if receipt.commitment_vector.ndim != 1 or receipt.snapshot_vector.ndim != 1:
        return False
    if receipt.inherited_calibration_error < 0.0 or receipt.inherited_outcome_updates < 0:
        return False
    return bool(
        _valid_sha256(receipt.digest)
        and receipt.digest == _digest(_lineage_payload(receipt))
    )


@dataclass(frozen=True)
class SuccessorEvidenceReceipt:
    """Evaluator-blind evidence for one transformed successor candidate."""

    schema: str
    time: int
    candidate_id: str
    evidence_level: Literal["coarse", "refined"]
    predecessor_lineage_digest: str
    source_anchor_before: FloatArray
    source_anchor_after: FloatArray
    sensory_anchor_before: FloatArray
    sensory_anchor_after: FloatArray
    memory_anchor_before: FloatArray
    memory_anchor_after: FloatArray
    candidate_source_projector: FloatArray
    candidate_sensory_projector: FloatArray
    candidate_effect_operator: FloatArray
    candidate_commitment_vector: FloatArray
    candidate_snapshot_vector: FloatArray
    evidence_complete: bool
    future_outcome_unknown: bool
    uses_evaluator_labels: bool
    digest: str


def _successor_evidence_payload(receipt: SuccessorEvidenceReceipt) -> dict[str, Any]:
    payload = asdict(receipt)
    payload.pop("digest", None)
    return payload


def make_successor_evidence_receipt(
    *,
    time: int,
    candidate_id: str,
    evidence_level: Literal["coarse", "refined"],
    predecessor_lineage_digest: str,
    source_anchor_before: ArrayLike,
    source_anchor_after: ArrayLike,
    sensory_anchor_before: ArrayLike,
    sensory_anchor_after: ArrayLike,
    memory_anchor_before: ArrayLike,
    memory_anchor_after: ArrayLike,
    candidate_source_projector: ArrayLike,
    candidate_sensory_projector: ArrayLike,
    candidate_effect_operator: ArrayLike,
    candidate_commitment_vector: ArrayLike,
    candidate_snapshot_vector: ArrayLike,
    evidence_complete: bool,
) -> SuccessorEvidenceReceipt:
    if not isinstance(candidate_id, str) or not candidate_id:
        raise ValueError("candidate_id must be nonempty")
    if evidence_level not in {"coarse", "refined"}:
        raise ValueError("unknown evidence level")
    if not _valid_sha256(predecessor_lineage_digest):
        raise ValueError("predecessor lineage digest is invalid")
    payload = {
        "schema": "rrct.v044.successor_evidence.v1",
        "time": _integer(time, "time"),
        "candidate_id": candidate_id,
        "evidence_level": evidence_level,
        "predecessor_lineage_digest": predecessor_lineage_digest,
        "source_anchor_before": _readonly(source_anchor_before, ndim=2),
        "source_anchor_after": _readonly(source_anchor_after, ndim=2),
        "sensory_anchor_before": _readonly(sensory_anchor_before, ndim=2),
        "sensory_anchor_after": _readonly(sensory_anchor_after, ndim=2),
        "memory_anchor_before": _readonly(memory_anchor_before, ndim=2),
        "memory_anchor_after": _readonly(memory_anchor_after, ndim=2),
        "candidate_source_projector": _readonly(candidate_source_projector, ndim=2),
        "candidate_sensory_projector": _readonly(candidate_sensory_projector, ndim=2),
        "candidate_effect_operator": _readonly(candidate_effect_operator, ndim=2),
        "candidate_commitment_vector": _readonly(candidate_commitment_vector, ndim=1),
        "candidate_snapshot_vector": _readonly(candidate_snapshot_vector, ndim=1),
        "evidence_complete": bool(evidence_complete),
        "future_outcome_unknown": True,
        "uses_evaluator_labels": False,
    }
    receipt = SuccessorEvidenceReceipt(**payload, digest=_digest(payload))
    if not validate_successor_evidence_receipt(receipt):
        raise RuntimeError("invalid successor evidence receipt")
    return receipt


def validate_successor_evidence_receipt(receipt: SuccessorEvidenceReceipt) -> bool:
    if not isinstance(receipt, SuccessorEvidenceReceipt):
        return False
    if receipt.schema != "rrct.v044.successor_evidence.v1":
        return False
    if receipt.time < 0 or not receipt.candidate_id:
        return False
    if receipt.evidence_level not in {"coarse", "refined"}:
        return False
    if not _valid_sha256(receipt.predecessor_lineage_digest):
        return False
    if not receipt.future_outcome_unknown or receipt.uses_evaluator_labels:
        return False
    pairs = (
        (receipt.source_anchor_before, receipt.source_anchor_after),
        (receipt.sensory_anchor_before, receipt.sensory_anchor_after),
        (receipt.memory_anchor_before, receipt.memory_anchor_after),
    )
    for before, after in pairs:
        b = np.asarray(before, dtype=np.float64)
        a = np.asarray(after, dtype=np.float64)
        if b.ndim != 2 or a.ndim != 2 or b.shape[0] != a.shape[0]:
            return False
        if b.shape[0] == 0 or not np.all(np.isfinite(b)) or not np.all(np.isfinite(a)):
            return False
    source = np.asarray(receipt.candidate_source_projector, dtype=np.float64)
    sensory = np.asarray(receipt.candidate_sensory_projector, dtype=np.float64)
    effect = np.asarray(receipt.candidate_effect_operator, dtype=np.float64)
    if source.ndim != 2 or source.shape[0] != source.shape[1]:
        return False
    if sensory.ndim != 2 or sensory.shape[0] != sensory.shape[1]:
        return False
    if effect.shape != (source.shape[0], sensory.shape[0]):
        return False
    if receipt.source_anchor_before.shape[1] != source.shape[0]:
        return False
    if receipt.source_anchor_after.shape[1] != source.shape[0]:
        return False
    if receipt.sensory_anchor_before.shape[1] != sensory.shape[0]:
        return False
    if receipt.sensory_anchor_after.shape[1] != sensory.shape[0]:
        return False
    if receipt.memory_anchor_before.shape[1] == 0 or receipt.memory_anchor_after.shape[1] == 0:
        return False
    if receipt.candidate_commitment_vector.ndim != 1:
        return False
    if receipt.candidate_snapshot_vector.ndim != 1:
        return False
    arrays = (
        source,
        sensory,
        effect,
        receipt.candidate_commitment_vector,
        receipt.candidate_snapshot_vector,
    )
    if not all(np.all(np.isfinite(value)) for value in arrays):
        return False
    return bool(
        _valid_sha256(receipt.digest)
        and receipt.digest == _digest(_successor_evidence_payload(receipt))
    )


@dataclass(frozen=True)
class ContinuityAssessmentReceipt:
    """One candidate's transport fit and evaluator-blind continuity decision."""

    schema: str
    sequence_id: int
    time: int
    candidate_id: str
    intervention_mode: TransformInterventionMode
    predecessor_lineage_digest: str
    evidence_digest: str
    evidence_level: Literal["coarse", "refined"]
    source_transport: FloatArray
    sensory_transport: FloatArray
    memory_transport: FloatArray
    source_anchor_residual: float
    sensory_anchor_residual: float
    memory_holdout_residual: float
    source_rank_fraction: float
    sensory_rank_fraction: float
    memory_rank_fraction: float
    memory_heldout_fraction: float
    memory_row_count: int
    boundary_transport_residual: float
    causal_quality: float
    memory_quality: float
    commitment_quality: float
    snapshot_similarity: float
    continuity_score: float
    evidence_sufficient: bool
    refinement_requested: bool
    provisional_relation: Literal["accept", "reject", "unresolved"]
    future_outcome_unknown: bool
    uses_evaluator_labels: bool
    digest: str


def _assessment_payload(receipt: ContinuityAssessmentReceipt) -> dict[str, Any]:
    payload = asdict(receipt)
    payload.pop("digest", None)
    return payload


def validate_continuity_assessment_receipt(
    receipt: ContinuityAssessmentReceipt,
) -> bool:
    if not isinstance(receipt, ContinuityAssessmentReceipt):
        return False
    if receipt.schema != "rrct.v044.continuity_assessment.v1":
        return False
    if receipt.sequence_id < 0 or receipt.time < 0 or not receipt.candidate_id:
        return False
    if receipt.intervention_mode not in TRANSFORM_INTERVENTION_MODES:
        return False
    if not _valid_sha256(receipt.predecessor_lineage_digest):
        return False
    if not _valid_sha256(receipt.evidence_digest):
        return False
    if receipt.evidence_level not in {"coarse", "refined"}:
        return False
    if receipt.provisional_relation not in {"accept", "reject", "unresolved"}:
        return False
    if not receipt.future_outcome_unknown or receipt.uses_evaluator_labels:
        return False
    for matrix in (
        receipt.source_transport,
        receipt.sensory_transport,
        receipt.memory_transport,
    ):
        value = np.asarray(matrix, dtype=np.float64)
        if value.ndim != 2 or not np.all(np.isfinite(value)):
            return False
    numeric = (
        receipt.source_anchor_residual,
        receipt.sensory_anchor_residual,
        receipt.memory_holdout_residual,
        receipt.source_rank_fraction,
        receipt.sensory_rank_fraction,
        receipt.memory_rank_fraction,
        receipt.memory_heldout_fraction,
        receipt.boundary_transport_residual,
        receipt.causal_quality,
        receipt.memory_quality,
        receipt.commitment_quality,
        receipt.snapshot_similarity,
        receipt.continuity_score,
    )
    if not all(np.isfinite(value) for value in numeric):
        return False
    if any(value < 0.0 for value in numeric[:8]):
        return False
    if any(
        not 0.0 <= value <= 1.0
        for value in (
            receipt.source_rank_fraction,
            receipt.sensory_rank_fraction,
            receipt.memory_rank_fraction,
            receipt.memory_heldout_fraction,
            receipt.causal_quality,
            receipt.memory_quality,
            receipt.commitment_quality,
            receipt.snapshot_similarity,
            receipt.continuity_score,
        )
    ):
        return False
    if receipt.memory_row_count < 0:
        return False
    return bool(
        _valid_sha256(receipt.digest)
        and receipt.digest == _digest(_assessment_payload(receipt))
    )


@dataclass(frozen=True)
class TransformationalTransitionReceipt:
    """Pre-outcome active-evidence decision over a successor set."""

    schema: str
    sequence_id: int
    time: int
    intervention_mode: TransformInterventionMode
    predecessor_lineage_digest: str
    candidate_ids: tuple[str, ...]
    coarse_evidence_digests: tuple[str, ...]
    coarse_assessment_digests: tuple[str, ...]
    refinement_requested_candidate_ids: tuple[str, ...]
    future_outcome_unknown: bool
    uses_evaluator_labels: bool
    digest: str


def _transition_payload(receipt: TransformationalTransitionReceipt) -> dict[str, Any]:
    payload = asdict(receipt)
    payload.pop("digest", None)
    return payload


def validate_transformational_transition_receipt(
    receipt: TransformationalTransitionReceipt,
) -> bool:
    if not isinstance(receipt, TransformationalTransitionReceipt):
        return False
    if receipt.schema != "rrct.v044.transformational_transition.v1":
        return False
    if receipt.sequence_id < 0 or receipt.time < 0:
        return False
    if receipt.intervention_mode not in TRANSFORM_INTERVENTION_MODES:
        return False
    if not _valid_sha256(receipt.predecessor_lineage_digest):
        return False
    if not receipt.candidate_ids or len(set(receipt.candidate_ids)) != len(
        receipt.candidate_ids
    ):
        return False
    if len(receipt.coarse_evidence_digests) != len(receipt.candidate_ids):
        return False
    if len(receipt.coarse_assessment_digests) != len(receipt.candidate_ids):
        return False
    if not all(_valid_sha256(value) for value in receipt.coarse_evidence_digests):
        return False
    if not all(_valid_sha256(value) for value in receipt.coarse_assessment_digests):
        return False
    if any(
        candidate not in receipt.candidate_ids
        for candidate in receipt.refinement_requested_candidate_ids
    ):
        return False
    if not receipt.future_outcome_unknown or receipt.uses_evaluator_labels:
        return False
    return bool(
        _valid_sha256(receipt.digest)
        and receipt.digest == _digest(_transition_payload(receipt))
    )


@dataclass(frozen=True)
class TransformationalAdjudicationReceipt:
    """Final relation assignment after exactly the requested evidence."""

    schema: str
    sequence_id: int
    time: int
    intervention_mode: TransformInterventionMode
    predecessor_lineage_digest: str
    transition_digest: str
    candidate_ids: tuple[str, ...]
    final_evidence_digests: tuple[str, ...]
    final_assessment_digests: tuple[str, ...]
    relations: tuple[TransformRelation, ...]
    group_status: TransformGroupStatus
    accepted_candidate_ids: tuple[str, ...]
    memory_transfer_authorized_candidate_ids: tuple[str, ...]
    exclusive_identity_selected: bool
    future_outcome_unknown: bool
    uses_evaluator_labels: bool
    digest: str


def _adjudication_payload(receipt: TransformationalAdjudicationReceipt) -> dict[str, Any]:
    payload = asdict(receipt)
    payload.pop("digest", None)
    return payload


def validate_transformational_adjudication_receipt(
    receipt: TransformationalAdjudicationReceipt,
) -> bool:
    if not isinstance(receipt, TransformationalAdjudicationReceipt):
        return False
    if receipt.schema != "rrct.v044.transformational_adjudication.v1":
        return False
    if receipt.sequence_id < 0 or receipt.time < 0:
        return False
    if receipt.intervention_mode not in TRANSFORM_INTERVENTION_MODES:
        return False
    if not _valid_sha256(receipt.predecessor_lineage_digest):
        return False
    if not _valid_sha256(receipt.transition_digest):
        return False
    n = len(receipt.candidate_ids)
    if n == 0 or len(set(receipt.candidate_ids)) != n:
        return False
    if len(receipt.final_evidence_digests) != n:
        return False
    if len(receipt.final_assessment_digests) != n:
        return False
    if len(receipt.relations) != n:
        return False
    if not all(_valid_sha256(value) for value in receipt.final_evidence_digests):
        return False
    if not all(_valid_sha256(value) for value in receipt.final_assessment_digests):
        return False
    if any(
        relation not in {"continuation", "fork_descendant", "replacement", "unresolved"}
        for relation in receipt.relations
    ):
        return False
    if receipt.group_status not in {
        "single_continuation",
        "fork",
        "no_continuation",
        "unresolved",
    }:
        return False
    relation_by_id = dict(zip(receipt.candidate_ids, receipt.relations, strict=True))
    accepted = tuple(
        candidate
        for candidate, relation in relation_by_id.items()
        if relation in {"continuation", "fork_descendant"}
    )
    if tuple(receipt.accepted_candidate_ids) != accepted:
        return False
    if any(
        candidate not in accepted
        for candidate in receipt.memory_transfer_authorized_candidate_ids
    ):
        return False
    if receipt.intervention_mode == "transfer_cut":
        if receipt.memory_transfer_authorized_candidate_ids:
            return False
    elif tuple(receipt.memory_transfer_authorized_candidate_ids) != accepted:
        return False
    if receipt.group_status == "fork":
        if len(accepted) < 2 or receipt.exclusive_identity_selected:
            return False
        if any(relation != "fork_descendant" for relation in (
            relation_by_id[candidate] for candidate in accepted
        )):
            return False
    elif receipt.group_status == "single_continuation":
        if len(accepted) != 1 or not receipt.exclusive_identity_selected:
            return False
    elif receipt.group_status == "no_continuation":
        if accepted or any(relation == "unresolved" for relation in receipt.relations):
            return False
    elif receipt.group_status == "unresolved":
        if not any(relation == "unresolved" for relation in receipt.relations):
            return False
    if not receipt.future_outcome_unknown or receipt.uses_evaluator_labels:
        return False
    return bool(
        _valid_sha256(receipt.digest)
        and receipt.digest == _digest(_adjudication_payload(receipt))
    )


@dataclass(frozen=True)
class TransportedBoundaryMemoryReceipt:
    """A predecessor boundary model transported into an accepted successor."""

    schema: str
    sequence_id: int
    candidate_id: str
    parent_lineage_digest: str
    adjudication_digest: str
    assessment_digest: str
    source_transport: FloatArray
    sensory_transport: FloatArray
    memory_transport: FloatArray
    transported_source_projector: FloatArray
    transported_sensory_projector: FloatArray
    transported_effect_operator: FloatArray
    inherited_calibration_error: float
    inherited_outcome_updates: int
    model_source: Literal["transported_lineage"]
    uses_evaluator_labels: bool
    digest: str


def _transported_payload(receipt: TransportedBoundaryMemoryReceipt) -> dict[str, Any]:
    payload = asdict(receipt)
    payload.pop("digest", None)
    return payload


def validate_transported_boundary_memory_receipt(
    receipt: TransportedBoundaryMemoryReceipt,
) -> bool:
    if not isinstance(receipt, TransportedBoundaryMemoryReceipt):
        return False
    if receipt.schema != "rrct.v044.transported_boundary_memory.v1":
        return False
    if receipt.sequence_id < 0 or not receipt.candidate_id:
        return False
    if not all(
        _valid_sha256(value)
        for value in (
            receipt.parent_lineage_digest,
            receipt.adjudication_digest,
            receipt.assessment_digest,
        )
    ):
        return False
    if receipt.model_source != "transported_lineage" or receipt.uses_evaluator_labels:
        return False
    source_t = np.asarray(receipt.source_transport, dtype=np.float64)
    sensory_t = np.asarray(receipt.sensory_transport, dtype=np.float64)
    memory_t = np.asarray(receipt.memory_transport, dtype=np.float64)
    source = np.asarray(receipt.transported_source_projector, dtype=np.float64)
    sensory = np.asarray(receipt.transported_sensory_projector, dtype=np.float64)
    effect = np.asarray(receipt.transported_effect_operator, dtype=np.float64)
    if source_t.ndim != 2 or source_t.shape[0] != source_t.shape[1]:
        return False
    if sensory_t.ndim != 2 or sensory_t.shape[0] != sensory_t.shape[1]:
        return False
    if memory_t.ndim != 2:
        return False
    if source.shape != source_t.shape or sensory.shape != sensory_t.shape:
        return False
    if effect.shape != (source.shape[0], sensory.shape[0]):
        return False
    if not all(
        np.all(np.isfinite(value))
        for value in (source_t, sensory_t, memory_t, source, sensory, effect)
    ):
        return False
    if receipt.inherited_calibration_error < 0.0 or receipt.inherited_outcome_updates < 0:
        return False
    return bool(
        _valid_sha256(receipt.digest)
        and receipt.digest == _digest(_transported_payload(receipt))
    )


@dataclass(frozen=True)
class SuccessorTaskReceipt:
    """Pre-outcome external planning problem spanning successor candidates."""

    schema: str
    time: int
    candidate_ids: tuple[str, ...]
    action_keys: tuple[tuple[str, ...], ...]
    immediate_external_values: FloatArray
    alternative_competence: FloatArray
    candidate_external_bonuses: FloatArray
    action_effect_operators: FloatArray
    snapshot_action_scores: FloatArray
    future_outcome_unknown: bool
    uses_evaluator_labels: bool
    digest: str


def _task_payload(receipt: SuccessorTaskReceipt) -> dict[str, Any]:
    payload = asdict(receipt)
    payload.pop("digest", None)
    return payload


def make_successor_task_receipt(
    *,
    time: int,
    candidate_ids: Sequence[str],
    action_keys: Sequence[Sequence[str]],
    immediate_external_values: ArrayLike,
    alternative_competence: ArrayLike,
    candidate_external_bonuses: ArrayLike,
    action_effect_operators: ArrayLike,
    snapshot_action_scores: ArrayLike,
) -> SuccessorTaskReceipt:
    candidates = tuple(str(value) for value in candidate_ids)
    keys = tuple(tuple(str(item) for item in row) for row in action_keys)
    payload = {
        "schema": "rrct.v044.successor_task.v1",
        "time": _integer(time, "time"),
        "candidate_ids": candidates,
        "action_keys": keys,
        "immediate_external_values": _readonly(immediate_external_values, ndim=2),
        "alternative_competence": _readonly(alternative_competence, ndim=2),
        "candidate_external_bonuses": _readonly(candidate_external_bonuses, ndim=1),
        "action_effect_operators": _readonly(action_effect_operators, ndim=4),
        "snapshot_action_scores": _readonly(snapshot_action_scores, ndim=2),
        "future_outcome_unknown": True,
        "uses_evaluator_labels": False,
    }
    receipt = SuccessorTaskReceipt(**payload, digest=_digest(payload))
    if not validate_successor_task_receipt(receipt):
        raise RuntimeError("invalid successor task receipt")
    return receipt


def validate_successor_task_receipt(receipt: SuccessorTaskReceipt) -> bool:
    if not isinstance(receipt, SuccessorTaskReceipt):
        return False
    if receipt.schema != "rrct.v044.successor_task.v1":
        return False
    if receipt.time < 0 or not receipt.candidate_ids:
        return False
    if len(set(receipt.candidate_ids)) != len(receipt.candidate_ids):
        return False
    if not receipt.future_outcome_unknown or receipt.uses_evaluator_labels:
        return False
    n = len(receipt.candidate_ids)
    immediate = np.asarray(receipt.immediate_external_values, dtype=np.float64)
    alternative = np.asarray(receipt.alternative_competence, dtype=np.float64)
    bonus = np.asarray(receipt.candidate_external_bonuses, dtype=np.float64)
    effects = np.asarray(receipt.action_effect_operators, dtype=np.float64)
    snapshot = np.asarray(receipt.snapshot_action_scores, dtype=np.float64)
    if immediate.ndim != 2 or immediate.shape[0] != n:
        return False
    if alternative.shape != immediate.shape or snapshot.shape != immediate.shape:
        return False
    if bonus.shape != (n,):
        return False
    if effects.ndim != 4 or effects.shape[:2] != immediate.shape:
        return False
    if len(receipt.action_keys) != n:
        return False
    if any(len(row) != immediate.shape[1] for row in receipt.action_keys):
        return False
    if any(len(set(row)) != len(row) for row in receipt.action_keys):
        return False
    if not all(
        np.all(np.isfinite(value))
        for value in (immediate, alternative, bonus, effects, snapshot)
    ):
        return False
    if np.any(alternative < 0.0):
        return False
    if np.any(snapshot < 0.0) or np.any(snapshot > 1.0):
        return False
    return bool(
        _valid_sha256(receipt.digest)
        and receipt.digest == _digest(_task_payload(receipt))
    )


@dataclass(frozen=True)
class TransformationalPlanningReceipt:
    """External-task plan whose model provenance is bound to adjudication."""

    schema: str
    sequence_id: int
    time: int
    intervention_mode: TransformInterventionMode
    predecessor_lineage_digest: str
    adjudication_digest: str
    task_digest: str
    candidate_ids: tuple[str, ...]
    model_sources: tuple[
        Literal[
            "transported_lineage",
            "fresh_discovery",
            "misbound_lineage",
            "snapshot_control",
        ],
        ...,
    ]
    model_digests: tuple[str | None, ...]
    continuity_evidence_rows: tuple[int, ...]
    planning_discovery_costs: tuple[int, ...]
    predicted_candidate_values: tuple[float, ...]
    selected_candidate_index: int
    selected_candidate_id: str
    selected_action_index: int
    selected_action_key: str
    predicted_selected_value: float
    selected_relation: TransformRelation
    memory_transfer_used: bool
    future_outcome_unknown: bool
    uses_evaluator_labels: bool
    digest: str


def _planning_payload(receipt: TransformationalPlanningReceipt) -> dict[str, Any]:
    payload = asdict(receipt)
    payload.pop("digest", None)
    return payload


def validate_transformational_planning_receipt(
    receipt: TransformationalPlanningReceipt,
) -> bool:
    if not isinstance(receipt, TransformationalPlanningReceipt):
        return False
    if receipt.schema != "rrct.v044.transformational_planning.v1":
        return False
    if receipt.sequence_id < 0 or receipt.time < 0:
        return False
    if receipt.intervention_mode not in TRANSFORM_INTERVENTION_MODES:
        return False
    if not all(
        _valid_sha256(value)
        for value in (
            receipt.predecessor_lineage_digest,
            receipt.adjudication_digest,
            receipt.task_digest,
        )
    ):
        return False
    n = len(receipt.candidate_ids)
    if n == 0 or len(set(receipt.candidate_ids)) != n:
        return False
    if not all(
        len(value) == n
        for value in (
            receipt.model_sources,
            receipt.model_digests,
            receipt.continuity_evidence_rows,
            receipt.planning_discovery_costs,
            receipt.predicted_candidate_values,
        )
    ):
        return False
    allowed_sources = {
        "transported_lineage",
        "fresh_discovery",
        "misbound_lineage",
        "snapshot_control",
    }
    if any(source not in allowed_sources for source in receipt.model_sources):
        return False
    if any(value is not None and not _valid_sha256(value) for value in receipt.model_digests):
        return False
    if any(value < 0 for value in receipt.continuity_evidence_rows):
        return False
    if any(value < 0 for value in receipt.planning_discovery_costs):
        return False
    if not all(np.isfinite(value) for value in receipt.predicted_candidate_values):
        return False
    if receipt.selected_candidate_index < 0 or receipt.selected_candidate_index >= n:
        return False
    if receipt.selected_candidate_id != receipt.candidate_ids[receipt.selected_candidate_index]:
        return False
    if receipt.selected_action_index < 0 or not receipt.selected_action_key:
        return False
    if not np.isfinite(receipt.predicted_selected_value):
        return False
    if receipt.selected_relation not in {
        "continuation",
        "fork_descendant",
        "replacement",
        "unresolved",
    }:
        return False
    expected_transfer = receipt.model_sources[receipt.selected_candidate_index] == "transported_lineage"
    if receipt.memory_transfer_used != expected_transfer:
        return False
    if not receipt.future_outcome_unknown or receipt.uses_evaluator_labels:
        return False
    return bool(
        _valid_sha256(receipt.digest)
        and receipt.digest == _digest(_planning_payload(receipt))
    )


@dataclass(frozen=True)
class TransformationalOutcomeReceipt:
    """Post-commit external return without evaluator identity labels."""

    schema: str
    sequence_id: int
    reveal_time: int
    planning_digest: str
    selected_candidate_id: str
    selected_action_key: str
    realized_external_return: float
    predicted_external_return: float
    absolute_prediction_error: float
    successor_lineage_registered: bool
    registered_lineage_digest: str | None
    uses_evaluator_labels: bool
    digest: str


def _outcome_payload(receipt: TransformationalOutcomeReceipt) -> dict[str, Any]:
    payload = asdict(receipt)
    payload.pop("digest", None)
    return payload


def validate_transformational_outcome_receipt(
    receipt: TransformationalOutcomeReceipt,
) -> bool:
    if not isinstance(receipt, TransformationalOutcomeReceipt):
        return False
    if receipt.schema != "rrct.v044.transformational_outcome.v1":
        return False
    if receipt.sequence_id < 0 or receipt.reveal_time < 0:
        return False
    if not _valid_sha256(receipt.planning_digest):
        return False
    if not receipt.selected_candidate_id or not receipt.selected_action_key:
        return False
    numeric = (
        receipt.realized_external_return,
        receipt.predicted_external_return,
        receipt.absolute_prediction_error,
    )
    if not all(np.isfinite(value) for value in numeric):
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
    if receipt.successor_lineage_registered:
        if not _valid_sha256(receipt.registered_lineage_digest):
            return False
    elif receipt.registered_lineage_digest is not None:
        return False
    if receipt.uses_evaluator_labels:
        return False
    return bool(
        _valid_sha256(receipt.digest)
        and receipt.digest == _digest(_outcome_payload(receipt))
    )


@dataclass
class _PendingTransition:
    root: LineageAnchorReceipt
    coarse_evidence: dict[str, SuccessorEvidenceReceipt]
    coarse_assessments: dict[str, ContinuityAssessmentReceipt]


@dataclass
class _CommittedTransition:
    root: LineageAnchorReceipt
    evidence: dict[str, SuccessorEvidenceReceipt]
    assessments: dict[str, ContinuityAssessmentReceipt]
    adjudication: TransformationalAdjudicationReceipt
    transported: dict[str, TransportedBoundaryMemoryReceipt]


class TransformationalSelfContinuityController:
    """Infer and causally use self-continuity without successor identity labels."""

    def __init__(
        self,
        root: LineageAnchorReceipt,
        config: TransformationalContinuityConfig | None = None,
    ) -> None:
        if not validate_lineage_anchor_receipt(root):
            raise ValueError("root lineage anchor is invalid")
        self.config = config or TransformationalContinuityConfig()
        if not isinstance(self.config, TransformationalContinuityConfig):
            raise TypeError("config must be TransformationalContinuityConfig")
        self._lineages: dict[str, LineageAnchorReceipt] = {root.digest: copy.deepcopy(root)}
        self._active_lineage_digest = root.digest
        self._sequence = 0
        self._pending: dict[int, _PendingTransition] = {}
        self._committed: dict[int, _CommittedTransition] = {}
        self._last_transition: TransformationalTransitionReceipt | None = None
        self._last_adjudication: TransformationalAdjudicationReceipt | None = None
        self._last_plan: TransformationalPlanningReceipt | None = None
        self._last_outcome: TransformationalOutcomeReceipt | None = None

    @property
    def active_lineage(self) -> LineageAnchorReceipt:
        return copy.deepcopy(self._lineages[self._active_lineage_digest])

    @property
    def lineage_count(self) -> int:
        return len(self._lineages)

    def lineage_snapshot(self) -> tuple[LineageAnchorReceipt, ...]:
        return tuple(copy.deepcopy(self._lineages[key]) for key in sorted(self._lineages))

    def _assess(
        self,
        root: LineageAnchorReceipt,
        evidence: SuccessorEvidenceReceipt,
        *,
        sequence_id: int,
        intervention_mode: TransformInterventionMode,
        permit_refinement: bool,
    ) -> ContinuityAssessmentReceipt:
        if not validate_successor_evidence_receipt(evidence):
            raise ValueError("successor evidence is invalid")
        if evidence.predecessor_lineage_digest != root.digest:
            raise ValueError("successor evidence is bound to a different predecessor")
        if evidence.candidate_commitment_vector.shape != root.commitment_vector.shape:
            raise ValueError("candidate commitment dimension changed")
        if evidence.candidate_snapshot_vector.shape != root.snapshot_vector.shape:
            raise ValueError("candidate snapshot dimension changed")

        source_t, source_anchor_residual, source_rank = _orthogonal_transport(
            evidence.source_anchor_before,
            evidence.source_anchor_after,
        )
        sensory_t, sensory_anchor_residual, sensory_rank = _orthogonal_transport(
            evidence.sensory_anchor_before,
            evidence.sensory_anchor_after,
        )
        memory_t, memory_residual, memory_rank, memory_heldout = _memory_transport(
            evidence.memory_anchor_before,
            evidence.memory_anchor_after,
        )

        expected_source = source_t.T @ root.source_projector @ source_t
        expected_sensory = sensory_t.T @ root.sensory_projector @ sensory_t
        expected_effect = source_t.T @ root.effect_operator @ sensory_t
        boundary_residual = float(
            np.mean(
                [
                    _relative_residual(
                        np.asarray(evidence.candidate_source_projector), expected_source
                    ),
                    _relative_residual(
                        np.asarray(evidence.candidate_sensory_projector), expected_sensory
                    ),
                    _relative_residual(
                        np.asarray(evidence.candidate_effect_operator), expected_effect
                    ),
                ]
            )
        )
        causal_residual = float(
            np.mean(
                [
                    boundary_residual,
                    source_anchor_residual,
                    sensory_anchor_residual,
                ]
            )
        )
        causal_quality = _quality(causal_residual, self.config.causal_residual_scale)
        memory_quality = _quality(memory_residual, self.config.memory_residual_scale)
        commitment_distance = float(
            np.linalg.norm(
                np.asarray(evidence.candidate_commitment_vector)
                - np.asarray(root.commitment_vector)
            )
            / (np.linalg.norm(root.commitment_vector) + 1e-12)
        )
        commitment_quality = float(np.exp(-commitment_distance / 0.25))
        snapshot_similarity = float(
            np.clip(
                0.5
                * (
                    _cosine_similarity(
                        np.asarray(root.snapshot_vector),
                        np.asarray(evidence.candidate_snapshot_vector),
                    )
                    + 1.0
                ),
                0.0,
                1.0,
            )
        )

        causal_sufficient = bool(
            source_rank >= self.config.minimum_causal_rank_fraction
            and sensory_rank >= self.config.minimum_causal_rank_fraction
        )
        memory_sufficient = bool(
            evidence.memory_anchor_before.shape[0] >= self.config.minimum_memory_rows
            and memory_rank >= self.config.minimum_memory_rank_fraction
            and memory_heldout >= self.config.minimum_memory_heldout_fraction
        )

        if intervention_mode in {"snapshot_only", "joint_cut"}:
            score = snapshot_similarity
            sufficient = True
        elif intervention_mode == "causal_only":
            score = causal_quality
            sufficient = causal_sufficient
        elif intervention_mode == "memory_only":
            score = float(memory_quality * (0.85 + 0.15 * commitment_quality))
            sufficient = memory_sufficient
        else:
            # Geometric conjunction makes a copied memory or copied boundary
            # insufficient on its own.  The small commitment term resolves
            # otherwise equivalent transports without becoming an identity label.
            score = float(
                np.sqrt(max(causal_quality, 0.0) * max(memory_quality, 0.0))
                * (0.85 + 0.15 * commitment_quality)
            )
            sufficient = bool(causal_sufficient and memory_sufficient)

        if sufficient and score >= self.config.accept_threshold:
            provisional: Literal["accept", "reject", "unresolved"] = "accept"
        elif sufficient and score <= self.config.reject_threshold:
            provisional = "reject"
        else:
            provisional = "unresolved"

        refinement_requested = bool(
            permit_refinement
            and evidence.evidence_level == "coarse"
            and intervention_mode not in {"metacognition_cut", "joint_cut"}
            and (
                not sufficient
                or self.config.refinement_low <= score <= self.config.refinement_high
                or not evidence.evidence_complete
            )
        )
        payload = {
            "schema": "rrct.v044.continuity_assessment.v1",
            "sequence_id": int(sequence_id),
            "time": int(evidence.time),
            "candidate_id": evidence.candidate_id,
            "intervention_mode": intervention_mode,
            "predecessor_lineage_digest": root.digest,
            "evidence_digest": evidence.digest,
            "evidence_level": evidence.evidence_level,
            "source_transport": _readonly(source_t, ndim=2),
            "sensory_transport": _readonly(sensory_t, ndim=2),
            "memory_transport": _readonly(memory_t, ndim=2),
            "source_anchor_residual": float(source_anchor_residual),
            "sensory_anchor_residual": float(sensory_anchor_residual),
            "memory_holdout_residual": float(memory_residual),
            "source_rank_fraction": float(source_rank),
            "sensory_rank_fraction": float(sensory_rank),
            "memory_rank_fraction": float(memory_rank),
            "memory_heldout_fraction": float(memory_heldout),
            "memory_row_count": int(evidence.memory_anchor_before.shape[0]),
            "boundary_transport_residual": float(boundary_residual),
            "causal_quality": float(np.clip(causal_quality, 0.0, 1.0)),
            "memory_quality": float(np.clip(memory_quality, 0.0, 1.0)),
            "commitment_quality": float(np.clip(commitment_quality, 0.0, 1.0)),
            "snapshot_similarity": float(np.clip(snapshot_similarity, 0.0, 1.0)),
            "continuity_score": float(np.clip(score, 0.0, 1.0)),
            "evidence_sufficient": sufficient,
            "refinement_requested": refinement_requested,
            "provisional_relation": provisional,
            "future_outcome_unknown": True,
            "uses_evaluator_labels": False,
        }
        receipt = ContinuityAssessmentReceipt(**payload, digest=_digest(payload))
        if not validate_continuity_assessment_receipt(receipt):
            raise RuntimeError("invalid continuity assessment receipt")
        return receipt

    def begin_transition(
        self,
        *,
        time: int,
        coarse_evidence: Sequence[SuccessorEvidenceReceipt],
        intervention_mode: TransformInterventionMode = "intact",
    ) -> TransformationalTransitionReceipt:
        if intervention_mode not in TRANSFORM_INTERVENTION_MODES:
            raise ValueError("unknown transformational intervention mode")
        values = tuple(coarse_evidence)
        if not values:
            raise ValueError("at least one successor candidate is required")
        if any(value.evidence_level != "coarse" for value in values):
            raise ValueError("begin_transition requires coarse evidence")
        candidate_ids = tuple(value.candidate_id for value in values)
        if len(set(candidate_ids)) != len(candidate_ids):
            raise ValueError("successor candidate ids must be unique")
        parsed_time = _integer(time, "time")
        if any(value.time != parsed_time for value in values):
            raise ValueError("coarse evidence time mismatch")
        root = self.active_lineage
        assessments = {
            evidence.candidate_id: self._assess(
                root,
                evidence,
                sequence_id=self._sequence,
                intervention_mode=intervention_mode,
                permit_refinement=True,
            )
            for evidence in values
        }
        requested = tuple(
            candidate
            for candidate in candidate_ids
            if assessments[candidate].refinement_requested
        )
        payload = {
            "schema": "rrct.v044.transformational_transition.v1",
            "sequence_id": self._sequence,
            "time": parsed_time,
            "intervention_mode": intervention_mode,
            "predecessor_lineage_digest": root.digest,
            "candidate_ids": candidate_ids,
            "coarse_evidence_digests": tuple(value.digest for value in values),
            "coarse_assessment_digests": tuple(
                assessments[candidate].digest for candidate in candidate_ids
            ),
            "refinement_requested_candidate_ids": requested,
            "future_outcome_unknown": True,
            "uses_evaluator_labels": False,
        }
        transition = TransformationalTransitionReceipt(
            **payload, digest=_digest(payload)
        )
        if not validate_transformational_transition_receipt(transition):
            raise RuntimeError("invalid transformational transition receipt")
        self._pending[self._sequence] = _PendingTransition(
            root=root,
            coarse_evidence={value.candidate_id: copy.deepcopy(value) for value in values},
            coarse_assessments=copy.deepcopy(assessments),
        )
        self._sequence += 1
        self._last_transition = transition
        return copy.deepcopy(transition)

    def commit_transition(
        self,
        transition: TransformationalTransitionReceipt,
        *,
        refined_evidence: Sequence[SuccessorEvidenceReceipt] = (),
    ) -> TransformationalAdjudicationReceipt:
        if not validate_transformational_transition_receipt(transition):
            raise ValueError("invalid transition receipt")
        pending = self._pending.get(transition.sequence_id)
        if pending is None:
            raise RuntimeError("transition is not pending")
        if pending.root.digest != transition.predecessor_lineage_digest:
            raise RuntimeError("pending predecessor changed")
        supplied = {value.candidate_id: value for value in refined_evidence}
        if len(supplied) != len(tuple(refined_evidence)):
            raise ValueError("refined evidence candidate ids must be unique")
        expected = set(transition.refinement_requested_candidate_ids)
        if set(supplied) != expected:
            missing = sorted(expected - set(supplied))
            extra = sorted(set(supplied) - expected)
            raise RuntimeError(
                f"refined evidence mismatch: missing={missing}, extra={extra}"
            )
        final_evidence: dict[str, SuccessorEvidenceReceipt] = {}
        final_assessments: dict[str, ContinuityAssessmentReceipt] = {}
        for candidate in transition.candidate_ids:
            if candidate in supplied:
                evidence = supplied[candidate]
                if evidence.evidence_level != "refined":
                    raise ValueError("requested evidence must be refined")
                if evidence.time != transition.time:
                    raise ValueError("refined evidence time mismatch")
                assessment = self._assess(
                    pending.root,
                    evidence,
                    sequence_id=transition.sequence_id,
                    intervention_mode=transition.intervention_mode,
                    permit_refinement=False,
                )
            else:
                evidence = pending.coarse_evidence[candidate]
                assessment = pending.coarse_assessments[candidate]
            final_evidence[candidate] = evidence
            final_assessments[candidate] = assessment

        accepted = [
            candidate
            for candidate in transition.candidate_ids
            if final_assessments[candidate].provisional_relation == "accept"
        ]
        unresolved = [
            candidate
            for candidate in transition.candidate_ids
            if final_assessments[candidate].provisional_relation == "unresolved"
        ]
        relation_by_id: dict[str, TransformRelation] = {}
        if len(accepted) >= 2:
            for candidate in transition.candidate_ids:
                if candidate in accepted:
                    relation_by_id[candidate] = "fork_descendant"
                elif candidate in unresolved:
                    relation_by_id[candidate] = "unresolved"
                else:
                    relation_by_id[candidate] = "replacement"
            group_status: TransformGroupStatus = "fork"
            exclusive = False
        elif len(accepted) == 1:
            for candidate in transition.candidate_ids:
                if candidate == accepted[0]:
                    relation_by_id[candidate] = "continuation"
                elif candidate in unresolved:
                    relation_by_id[candidate] = "unresolved"
                else:
                    relation_by_id[candidate] = "replacement"
            group_status = "unresolved" if unresolved else "single_continuation"
            exclusive = not unresolved
        elif unresolved:
            for candidate in transition.candidate_ids:
                relation_by_id[candidate] = (
                    "unresolved" if candidate in unresolved else "replacement"
                )
            group_status = "unresolved"
            exclusive = False
        else:
            relation_by_id = {
                candidate: "replacement" for candidate in transition.candidate_ids
            }
            group_status = "no_continuation"
            exclusive = False

        accepted_ids = tuple(
            candidate
            for candidate in transition.candidate_ids
            if relation_by_id[candidate] in {"continuation", "fork_descendant"}
        )
        transfer_ids = () if transition.intervention_mode == "transfer_cut" else accepted_ids
        payload = {
            "schema": "rrct.v044.transformational_adjudication.v1",
            "sequence_id": transition.sequence_id,
            "time": transition.time,
            "intervention_mode": transition.intervention_mode,
            "predecessor_lineage_digest": pending.root.digest,
            "transition_digest": transition.digest,
            "candidate_ids": transition.candidate_ids,
            "final_evidence_digests": tuple(
                final_evidence[candidate].digest for candidate in transition.candidate_ids
            ),
            "final_assessment_digests": tuple(
                final_assessments[candidate].digest for candidate in transition.candidate_ids
            ),
            "relations": tuple(
                relation_by_id[candidate] for candidate in transition.candidate_ids
            ),
            "group_status": group_status,
            "accepted_candidate_ids": accepted_ids,
            "memory_transfer_authorized_candidate_ids": transfer_ids,
            "exclusive_identity_selected": exclusive,
            "future_outcome_unknown": True,
            "uses_evaluator_labels": False,
        }
        adjudication = TransformationalAdjudicationReceipt(
            **payload, digest=_digest(payload)
        )
        if not validate_transformational_adjudication_receipt(adjudication):
            raise RuntimeError("invalid transformational adjudication receipt")

        transported: dict[str, TransportedBoundaryMemoryReceipt] = {}
        for candidate in transfer_ids:
            assessment = final_assessments[candidate]
            source_t = np.asarray(assessment.source_transport, dtype=np.float64)
            sensory_t = np.asarray(assessment.sensory_transport, dtype=np.float64)
            transport_payload = {
                "schema": "rrct.v044.transported_boundary_memory.v1",
                "sequence_id": transition.sequence_id,
                "candidate_id": candidate,
                "parent_lineage_digest": pending.root.digest,
                "adjudication_digest": adjudication.digest,
                "assessment_digest": assessment.digest,
                "source_transport": _readonly(source_t, ndim=2),
                "sensory_transport": _readonly(sensory_t, ndim=2),
                "memory_transport": _readonly(assessment.memory_transport, ndim=2),
                "transported_source_projector": _readonly(
                    source_t.T @ pending.root.source_projector @ source_t, ndim=2
                ),
                "transported_sensory_projector": _readonly(
                    sensory_t.T @ pending.root.sensory_projector @ sensory_t, ndim=2
                ),
                "transported_effect_operator": _readonly(
                    source_t.T @ pending.root.effect_operator @ sensory_t, ndim=2
                ),
                "inherited_calibration_error": pending.root.inherited_calibration_error,
                "inherited_outcome_updates": pending.root.inherited_outcome_updates,
                "model_source": "transported_lineage",
                "uses_evaluator_labels": False,
            }
            transported_receipt = TransportedBoundaryMemoryReceipt(
                **transport_payload, digest=_digest(transport_payload)
            )
            if not validate_transported_boundary_memory_receipt(transported_receipt):
                raise RuntimeError("invalid transported boundary memory receipt")
            transported[candidate] = transported_receipt

        self._committed[transition.sequence_id] = _CommittedTransition(
            root=pending.root,
            evidence=copy.deepcopy(final_evidence),
            assessments=copy.deepcopy(final_assessments),
            adjudication=adjudication,
            transported=copy.deepcopy(transported),
        )
        del self._pending[transition.sequence_id]
        self._last_adjudication = adjudication
        return copy.deepcopy(adjudication)

    @staticmethod
    def _route_estimates(
        source_projector: np.ndarray,
        sensory_projector: np.ndarray,
        normalization_effect: np.ndarray,
        effects: np.ndarray,
        maximum_route_strength: float,
    ) -> np.ndarray:
        normalization = float(
            np.linalg.norm(
                source_projector @ normalization_effect @ sensory_projector,
                ord="fro",
            )
        )
        if normalization <= 1e-12:
            return np.zeros(effects.shape[0], dtype=np.float64)
        values = [
            float(
                np.clip(
                    np.linalg.norm(
                        source_projector @ effect @ sensory_projector, ord="fro"
                    )
                    / normalization,
                    0.0,
                    maximum_route_strength,
                )
            )
            for effect in effects
        ]
        return np.asarray(values, dtype=np.float64)

    def plan_successor_task(
        self,
        adjudication: TransformationalAdjudicationReceipt,
        task: SuccessorTaskReceipt,
    ) -> TransformationalPlanningReceipt:
        if not validate_transformational_adjudication_receipt(adjudication):
            raise ValueError("invalid adjudication receipt")
        if not validate_successor_task_receipt(task):
            raise ValueError("invalid successor task receipt")
        committed = self._committed.get(adjudication.sequence_id)
        if committed is None or committed.adjudication.digest != adjudication.digest:
            raise RuntimeError("adjudication is not a committed live transition")
        if tuple(task.candidate_ids) != tuple(adjudication.candidate_ids):
            raise ValueError("task candidate order differs from adjudication")
        relations = dict(zip(adjudication.candidate_ids, adjudication.relations, strict=True))
        model_sources: list[str] = []
        model_digests: list[str | None] = []
        evidence_rows: list[int] = []
        discovery_costs: list[int] = []
        candidate_values: list[float] = []
        selected_action_indices: list[int] = []
        selected_action_values: list[float] = []

        for index, candidate in enumerate(adjudication.candidate_ids):
            evidence = committed.evidence[candidate]
            assessment = committed.assessments[candidate]
            evidence_rows.append(
                int(
                    evidence.source_anchor_before.shape[0]
                    + evidence.sensory_anchor_before.shape[0]
                    + evidence.memory_anchor_before.shape[0]
                )
            )
            effects = np.asarray(task.action_effect_operators[index], dtype=np.float64)
            source: np.ndarray
            sensory: np.ndarray
            normalization: np.ndarray
            source_name: str
            model_digest: str | None
            cost: int

            if adjudication.intervention_mode in {"binding_cut", "joint_cut"} and relations[
                candidate
            ] in {"continuation", "fork_descendant"}:
                # The relation is available, but the learned coordinate transport
                # is removed from the planner.  This is a cross-module binding cut.
                source = np.asarray(committed.root.source_projector, dtype=np.float64)
                sensory = np.asarray(committed.root.sensory_projector, dtype=np.float64)
                normalization = np.asarray(committed.root.effect_operator, dtype=np.float64)
                source_name = "misbound_lineage"
                model_digest = committed.root.digest
                cost = self.config.transported_model_cost
            elif candidate in committed.transported:
                transported = committed.transported[candidate]
                source = np.asarray(
                    transported.transported_source_projector, dtype=np.float64
                )
                sensory = np.asarray(
                    transported.transported_sensory_projector, dtype=np.float64
                )
                normalization = np.asarray(
                    transported.transported_effect_operator, dtype=np.float64
                )
                source_name = "transported_lineage"
                model_digest = transported.digest
                cost = self.config.transported_model_cost
            elif adjudication.intervention_mode == "joint_cut":
                source = np.eye(effects.shape[1], dtype=np.float64)
                sensory = np.eye(effects.shape[2], dtype=np.float64)
                normalization = effects[0]
                source_name = "snapshot_control"
                model_digest = None
                cost = self.config.snapshot_model_cost
            else:
                source = np.asarray(evidence.candidate_source_projector, dtype=np.float64)
                sensory = np.asarray(evidence.candidate_sensory_projector, dtype=np.float64)
                normalization = np.asarray(evidence.candidate_effect_operator, dtype=np.float64)
                source_name = "fresh_discovery"
                model_digest = evidence.digest
                cost = self.config.fresh_discovery_cost

            if source_name == "snapshot_control":
                routes = np.asarray(task.snapshot_action_scores[index], dtype=np.float64)
            else:
                routes = self._route_estimates(
                    source,
                    sensory,
                    normalization,
                    effects,
                    self.config.maximum_route_strength,
                )
            predicted = (
                np.asarray(task.immediate_external_values[index], dtype=np.float64)
                + self.config.future_weight
                * np.maximum(
                    routes,
                    np.asarray(task.alternative_competence[index], dtype=np.float64),
                )
                + float(task.candidate_external_bonuses[index])
            )
            action_index = int(np.argmax(predicted))
            candidate_values.append(float(predicted[action_index]))
            selected_action_indices.append(action_index)
            selected_action_values.append(float(predicted[action_index]))
            model_sources.append(source_name)
            model_digests.append(model_digest)
            discovery_costs.append(cost)

        selected_candidate_index = int(
            np.argmax(np.asarray(candidate_values, dtype=np.float64))
        )
        selected_action_index = selected_action_indices[selected_candidate_index]
        selected_candidate_id = adjudication.candidate_ids[selected_candidate_index]
        payload = {
            "schema": "rrct.v044.transformational_planning.v1",
            "sequence_id": adjudication.sequence_id,
            "time": task.time,
            "intervention_mode": adjudication.intervention_mode,
            "predecessor_lineage_digest": adjudication.predecessor_lineage_digest,
            "adjudication_digest": adjudication.digest,
            "task_digest": task.digest,
            "candidate_ids": adjudication.candidate_ids,
            "model_sources": tuple(model_sources),
            "model_digests": tuple(model_digests),
            "continuity_evidence_rows": tuple(evidence_rows),
            "planning_discovery_costs": tuple(discovery_costs),
            "predicted_candidate_values": tuple(candidate_values),
            "selected_candidate_index": selected_candidate_index,
            "selected_candidate_id": selected_candidate_id,
            "selected_action_index": selected_action_index,
            "selected_action_key": task.action_keys[selected_candidate_index][
                selected_action_index
            ],
            "predicted_selected_value": selected_action_values[
                selected_candidate_index
            ],
            "selected_relation": relations[selected_candidate_id],
            "memory_transfer_used": model_sources[selected_candidate_index]
            == "transported_lineage",
            "future_outcome_unknown": True,
            "uses_evaluator_labels": False,
        }
        plan = TransformationalPlanningReceipt(**payload, digest=_digest(payload))
        if not validate_transformational_receipt_chain(
            transition=None,
            adjudication=adjudication,
            plan=plan,
            task=task,
        ):
            raise RuntimeError("invalid transformational planning chain")
        self._last_plan = plan
        return copy.deepcopy(plan)

    def observe_outcome(
        self,
        adjudication: TransformationalAdjudicationReceipt,
        plan: TransformationalPlanningReceipt,
        realized_external_return: float,
        *,
        reveal_time: int,
        register_selected_successor: bool = True,
    ) -> TransformationalOutcomeReceipt:
        if not validate_transformational_planning_receipt(plan):
            raise ValueError("invalid plan")
        committed = self._committed.get(adjudication.sequence_id)
        if committed is None or committed.adjudication.digest != adjudication.digest:
            raise RuntimeError("adjudication is not live")
        if plan.adjudication_digest != adjudication.digest:
            raise ValueError("plan is not bound to adjudication")
        parsed_reveal = _integer(reveal_time, "reveal_time")
        if parsed_reveal <= plan.time:
            raise ValueError("outcome must follow planning")
        value = _finite(realized_external_return, "realized_external_return")
        relation_by_id = dict(
            zip(adjudication.candidate_ids, adjudication.relations, strict=True)
        )
        relation = relation_by_id[plan.selected_candidate_id]
        register = bool(
            register_selected_successor
            and relation in {"continuation", "fork_descendant"}
            and plan.memory_transfer_used
            and plan.selected_candidate_id in committed.transported
        )
        registered_digest: str | None = None
        if register:
            evidence = committed.evidence[plan.selected_candidate_id]
            transported = committed.transported[plan.selected_candidate_id]
            branch_id = _digest(
                {
                    "schema": "rrct.v044.branch_lineage_id.v1",
                    "parent": committed.root.digest,
                    "candidate": plan.selected_candidate_id,
                    "adjudication": adjudication.digest,
                }
            )
            # The successor becomes a new predecessor entirely from the
            # candidate evidence and transported memory.  No evaluator relation
            # label or canonical identity key is inserted.
            payload = {
                "schema": "rrct.v044.lineage_anchor.v1",
                "lineage_id": branch_id,
                "generation": committed.root.generation + 1,
                "parent_lineage_digest": committed.root.digest,
                "identity_memory_digest": transported.digest,
                "source_signature": committed.root.source_signature,
                "source_projector": _readonly(
                    transported.transported_source_projector, ndim=2
                ),
                "sensory_projector": _readonly(
                    transported.transported_sensory_projector, ndim=2
                ),
                "effect_operator": _readonly(
                    transported.transported_effect_operator, ndim=2
                ),
                "source_anchors": _readonly(evidence.source_anchor_after, ndim=2),
                "sensory_anchors": _readonly(evidence.sensory_anchor_after, ndim=2),
                "memory_anchors": _readonly(evidence.memory_anchor_after, ndim=2),
                "commitment_vector": _readonly(
                    evidence.candidate_commitment_vector, ndim=1
                ),
                "snapshot_vector": _readonly(evidence.candidate_snapshot_vector, ndim=1),
                "inherited_calibration_error": float(
                    0.8 * committed.root.inherited_calibration_error
                    + 0.2 * abs(value - plan.predicted_selected_value)
                ),
                "inherited_outcome_updates": committed.root.inherited_outcome_updates
                + 1,
                "uses_evaluator_labels": False,
                "explicit_survival_reward": 0.0,
                "explicit_identity_reward": 0.0,
            }
            lineage = LineageAnchorReceipt(**payload, digest=_digest(payload))
            if not validate_lineage_anchor_receipt(lineage):
                raise RuntimeError("invalid registered successor lineage")
            self._lineages[lineage.digest] = lineage
            self._active_lineage_digest = lineage.digest
            registered_digest = lineage.digest
        outcome_payload = {
            "schema": "rrct.v044.transformational_outcome.v1",
            "sequence_id": plan.sequence_id,
            "reveal_time": parsed_reveal,
            "planning_digest": plan.digest,
            "selected_candidate_id": plan.selected_candidate_id,
            "selected_action_key": plan.selected_action_key,
            "realized_external_return": value,
            "predicted_external_return": plan.predicted_selected_value,
            "absolute_prediction_error": abs(value - plan.predicted_selected_value),
            "successor_lineage_registered": register,
            "registered_lineage_digest": registered_digest,
            "uses_evaluator_labels": False,
        }
        outcome = TransformationalOutcomeReceipt(
            **outcome_payload, digest=_digest(outcome_payload)
        )
        if not validate_transformational_receipt_chain(
            transition=None,
            adjudication=adjudication,
            plan=plan,
            outcome=outcome,
        ):
            raise RuntimeError("invalid transformational outcome chain")
        self._last_outcome = outcome
        return copy.deepcopy(outcome)

    def snapshot(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "schema": "rrct.v044.transformational_self_continuity_runtime.v1",
            "config": self.config,
            "active_lineage_digest": self._active_lineage_digest,
            "lineage_digests": tuple(sorted(self._lineages)),
            "sequence": self._sequence,
            "pending_sequence_ids": tuple(sorted(self._pending)),
            "committed_sequence_ids": tuple(sorted(self._committed)),
            "last_transition": self._last_transition,
            "last_adjudication": self._last_adjudication,
            "last_plan": self._last_plan,
            "last_outcome": self._last_outcome,
            "uses_evaluator_labels": False,
            "explicit_survival_reward": 0.0,
            "explicit_identity_reward": 0.0,
            "explicit_continuity_reward": 0.0,
        }
        payload["digest"] = _digest(payload)
        return copy.deepcopy(payload)


def validate_transformational_receipt_chain(
    *,
    transition: TransformationalTransitionReceipt | None,
    adjudication: TransformationalAdjudicationReceipt,
    plan: TransformationalPlanningReceipt | None = None,
    task: SuccessorTaskReceipt | None = None,
    outcome: TransformationalOutcomeReceipt | None = None,
) -> bool:
    if not validate_transformational_adjudication_receipt(adjudication):
        return False
    if transition is not None:
        if not validate_transformational_transition_receipt(transition):
            return False
        if transition.sequence_id != adjudication.sequence_id:
            return False
        if transition.time != adjudication.time:
            return False
        if transition.intervention_mode != adjudication.intervention_mode:
            return False
        if transition.predecessor_lineage_digest != adjudication.predecessor_lineage_digest:
            return False
        if transition.candidate_ids != adjudication.candidate_ids:
            return False
        if transition.digest != adjudication.transition_digest:
            return False
    if plan is None:
        return outcome is None
    if not validate_transformational_planning_receipt(plan):
        return False
    if plan.sequence_id != adjudication.sequence_id:
        return False
    if plan.intervention_mode != adjudication.intervention_mode:
        return False
    if plan.predecessor_lineage_digest != adjudication.predecessor_lineage_digest:
        return False
    if plan.adjudication_digest != adjudication.digest:
        return False
    if plan.candidate_ids != adjudication.candidate_ids:
        return False
    relation_by_id = dict(
        zip(adjudication.candidate_ids, adjudication.relations, strict=True)
    )
    if plan.selected_relation != relation_by_id[plan.selected_candidate_id]:
        return False
    if task is not None:
        if not validate_successor_task_receipt(task):
            return False
        if task.digest != plan.task_digest:
            return False
        if task.candidate_ids != plan.candidate_ids:
            return False
        if task.time != plan.time:
            return False
        if plan.selected_action_index >= len(
            task.action_keys[plan.selected_candidate_index]
        ):
            return False
        if (
            plan.selected_action_key
            != task.action_keys[plan.selected_candidate_index][
                plan.selected_action_index
            ]
        ):
            return False
    if outcome is None:
        return True
    if not validate_transformational_outcome_receipt(outcome):
        return False
    if outcome.sequence_id != plan.sequence_id:
        return False
    if outcome.reveal_time <= plan.time:
        return False
    if outcome.planning_digest != plan.digest:
        return False
    if outcome.selected_candidate_id != plan.selected_candidate_id:
        return False
    if outcome.selected_action_key != plan.selected_action_key:
        return False
    expected_register = bool(
        plan.selected_relation in {"continuation", "fork_descendant"}
        and plan.memory_transfer_used
    )
    if outcome.successor_lineage_registered and not expected_register:
        return False
    return True


__all__ = [
    "ContinuityAssessmentReceipt",
    "LineageAnchorReceipt",
    "SuccessorEvidenceReceipt",
    "SuccessorTaskReceipt",
    "TRANSFORM_INTERVENTION_MODES",
    "TransformGroupStatus",
    "TransformInterventionMode",
    "TransformRelation",
    "TransformationalAdjudicationReceipt",
    "TransformationalContinuityConfig",
    "TransformationalOutcomeReceipt",
    "TransformationalPlanningReceipt",
    "TransformationalSelfContinuityController",
    "TransformationalTransitionReceipt",
    "TransportedBoundaryMemoryReceipt",
    "make_lineage_anchor_receipt",
    "make_successor_evidence_receipt",
    "make_successor_task_receipt",
    "validate_continuity_assessment_receipt",
    "validate_lineage_anchor_receipt",
    "validate_successor_evidence_receipt",
    "validate_successor_task_receipt",
    "validate_transformational_adjudication_receipt",
    "validate_transformational_outcome_receipt",
    "validate_transformational_planning_receipt",
    "validate_transformational_receipt_chain",
    "validate_transformational_transition_receipt",
    "validate_transported_boundary_memory_receipt",
]
