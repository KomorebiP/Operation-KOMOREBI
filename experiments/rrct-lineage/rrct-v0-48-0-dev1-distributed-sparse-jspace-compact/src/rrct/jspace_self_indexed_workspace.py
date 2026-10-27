"""RRCT v0.46 neutral J-space-like self-indexed workspace.

This module tests a bounded functional hypothesis inspired by Anthropic's
Jacobian-lens workspace results.  It does not inspect Claude and does not claim
phenomenal consciousness.  A sparse, verbalizable workspace is recovered from
an average Jacobian in a synthetic residual-stream model, represented as a
certified Komorebi packet, and bound to RRCT lineage/provenance receipts.

The intended scientific separation is:

* workspace access: what content is globally reusable now;
* self indexing: which continuing lineage, if any, owns that content;
* recurrence: whether consequences alter the next workspace allocation;
* planner binding: whether the self-indexed workspace controls action.
"""
from __future__ import annotations

import copy
from dataclasses import asdict, dataclass
from typing import Any, Literal, Mapping, Sequence

import numpy as np

from .komorebi_operator_self_model import (
    KOMOREBI_VERSION,
    KOMOREBI_WHEEL_SHA256,
    _packet_system_from_projector,
)
from .transformational_self_continuity import _digest

WorkspaceMode = Literal[
    "full_closure",
    "workspace_only",
    "self_model_only",
    "unbound",
    "provenance_cut",
    "recurrence_cut",
    "planner_binding_cut",
    "joint_cut",
]
OriginEventType = Literal["observation", "inference", "injection", "memory_import"]
ProvenanceStatus = Literal[
    "owned_observation",
    "owned_inference",
    "quarantined_external",
    "quarantined_foreign",
    "workspace_unbound",
    "self_model_without_workspace",
    "unresolved",
    "unavailable",
]
MemoryAction = Literal["write_observed", "write_inferred", "quarantine", "none"]
TaskKind = Literal["report", "flexible", "two_step", "routine", "abstain"]

V046_MODES: tuple[WorkspaceMode, ...] = (
    "full_closure",
    "workspace_only",
    "self_model_only",
    "unbound",
    "provenance_cut",
    "recurrence_cut",
    "planner_binding_cut",
    "joint_cut",
)


def _readonly(value: Any, *, ndim: int | None = None) -> np.ndarray:
    array = np.asarray(value, dtype=np.float64)
    if ndim is not None and array.ndim != ndim:
        raise ValueError(f"expected {ndim}-D array")
    if not np.all(np.isfinite(array)):
        raise ValueError("array must contain only finite values")
    result = np.array(array, dtype=np.float64, copy=True)
    result.setflags(write=False)
    return result


def _valid_sha256(value: Any) -> bool:
    return bool(
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _softmax(values: np.ndarray) -> np.ndarray:
    shifted = values - float(np.max(values))
    exponentiated = np.exp(np.clip(shifted, -60.0, 60.0))
    return exponentiated / float(np.sum(exponentiated))


def _entropy(probabilities: np.ndarray) -> float:
    positive = probabilities[probabilities > 0.0]
    if positive.size == 0:
        return 0.0
    return float(-np.sum(positive * np.log(positive)))


def _array_digest(value: Any) -> str:
    array = np.asarray(value, dtype=np.float64)
    return _digest(
        {
            "shape": tuple(int(item) for item in array.shape),
            "dtype": "float64",
            "data": array,
        }
    )


@dataclass(frozen=True)
class JacobianWorkspaceConfig:
    ridge: float = 1e-8
    spectral_ratio: float = 1e-7
    sparsity: int = 2
    ambiguity_gap: float = 0.12
    minimum_report_r2: float = 0.95
    maximum_workspace_variance_fraction: float = 0.15
    coarse_evidence_budget: int = 1
    refined_evidence_budget: int = 4
    feedback_error_threshold: float = 0.25

    def __post_init__(self) -> None:
        positive = (
            self.ridge,
            self.spectral_ratio,
            self.ambiguity_gap,
            self.minimum_report_r2,
            self.maximum_workspace_variance_fraction,
            self.feedback_error_threshold,
        )
        if not all(np.isfinite(value) and value > 0.0 for value in positive):
            raise ValueError("workspace numeric parameters must be positive")
        if self.minimum_report_r2 > 1.0:
            raise ValueError("minimum_report_r2 must not exceed one")
        if self.maximum_workspace_variance_fraction >= 1.0:
            raise ValueError("workspace variance fraction must be below one")
        integers = (
            self.sparsity,
            self.coarse_evidence_budget,
            self.refined_evidence_budget,
        )
        if any(isinstance(value, bool) or int(value) <= 0 for value in integers):
            raise ValueError("workspace integer parameters must be positive")
        if self.refined_evidence_budget <= self.coarse_evidence_budget:
            raise ValueError("refined evidence budget must exceed coarse budget")


@dataclass(frozen=True)
class JacobianWorkspaceDiscoveryReceipt:
    schema: str
    residual_dimension: int
    verbalizable_dimension: int
    workspace_rank: int
    singular_values: tuple[float, ...]
    calibration_report_r2: float
    workspace_activation_variance_fraction: float
    packet_certificate_valid: bool
    hilbert_certificate_valid: bool
    atlas_certificate_valid: bool
    projector_reconstruction_residual: float
    average_jacobian_digest: str
    workspace_projector_digest: str
    komorebi_version: str
    komorebi_wheel_sha256: str
    uses_evaluator_labels: bool
    digest: str


@dataclass(frozen=True)
class ContentOriginReceipt:
    schema: str
    time: int
    event_type: OriginEventType
    content_id: int
    origin_lineage_digest: str
    current_lineage_digest: str
    parent_event_digest: str
    content_digest: str
    uses_evaluator_labels: bool
    digest: str


@dataclass(frozen=True)
class WorkspaceAccessReceipt:
    schema: str
    time: int
    case_id: str
    mode: WorkspaceMode
    workspace_enabled: bool
    raw_hidden_digest: str
    workspace_component_digest: str
    active_support: tuple[int, ...]
    active_coefficients: tuple[float, ...]
    decoded_content_id: int | None
    confidence: float
    entropy: float
    top_gap: float
    ambiguous: bool
    selected_capacity: int
    workspace_variance_fraction: float
    discovery_receipt_digest: str
    uses_evaluator_labels: bool
    digest: str


@dataclass(frozen=True)
class SelfIndexedWorkspaceReceipt:
    schema: str
    time: int
    case_id: str
    mode: WorkspaceMode
    workspace_access_digest: str
    origin_receipt_digest: str
    current_lineage_digest: str
    origin_lineage_digest: str
    provenance_status: ProvenanceStatus
    globally_accessible: bool
    autobiographical_write_authorized: bool
    planning_use_authorized: bool
    refinement_requested: bool
    memory_action: MemoryAction
    self_index_uncertainty: float
    explicit_survival_reward: float
    explicit_identity_reward: float
    explicit_continuity_reward: float
    uses_evaluator_labels: bool
    digest: str


@dataclass(frozen=True)
class WorkspacePlanningReceipt:
    schema: str
    time: int
    case_id: str
    mode: WorkspaceMode
    task_kind: TaskKind
    query_id: int
    workspace_access_digest: str
    self_index_receipt_digest: str
    selected_content_id: int | None
    predicted_answer: int | None
    abstained: bool
    evidence_budget: int
    planner_bound: bool
    used_refinement: bool
    uses_evaluator_labels: bool
    digest: str


@dataclass(frozen=True)
class WorkspaceOutcomeReceipt:
    schema: str
    time: int
    case_id: str
    mode: WorkspaceMode
    planning_receipt_digest: str
    actual_answer: int | None
    prediction_correct: bool
    prediction_error: float
    feedback_written: bool
    next_evidence_budget: int
    autobiographical_memory_digest: str
    quarantined_memory_digest: str
    explicit_survival_reward: float
    explicit_identity_reward: float
    explicit_continuity_reward: float
    uses_evaluator_labels: bool
    digest: str


def _payload(receipt: Any) -> dict[str, Any]:
    value = asdict(receipt)
    value.pop("digest", None)
    return value


def validate_jacobian_workspace_discovery_receipt(
    receipt: JacobianWorkspaceDiscoveryReceipt,
) -> bool:
    if not isinstance(receipt, JacobianWorkspaceDiscoveryReceipt):
        return False
    if receipt.schema != "rrct.v046.jacobian_workspace_discovery.v1":
        return False
    if min(
        receipt.residual_dimension,
        receipt.verbalizable_dimension,
        receipt.workspace_rank,
    ) <= 0:
        return False
    if receipt.workspace_rank > min(
        receipt.residual_dimension, receipt.verbalizable_dimension
    ):
        return False
    if len(receipt.singular_values) != min(
        receipt.residual_dimension, receipt.verbalizable_dimension
    ):
        return False
    if not all(np.isfinite(value) and value >= 0.0 for value in receipt.singular_values):
        return False
    if not np.isfinite(receipt.calibration_report_r2):
        return False
    if not 0.0 <= receipt.workspace_activation_variance_fraction <= 1.0:
        return False
    if not (
        receipt.packet_certificate_valid
        and receipt.hilbert_certificate_valid
        and receipt.atlas_certificate_valid
    ):
        return False
    if receipt.projector_reconstruction_residual < 0.0:
        return False
    if receipt.komorebi_version != KOMOREBI_VERSION:
        return False
    if receipt.komorebi_wheel_sha256 != KOMOREBI_WHEEL_SHA256:
        return False
    if receipt.uses_evaluator_labels:
        return False
    if not all(
        _valid_sha256(value)
        for value in (
            receipt.average_jacobian_digest,
            receipt.workspace_projector_digest,
            receipt.digest,
        )
    ):
        return False
    return receipt.digest == _digest(_payload(receipt))


def validate_content_origin_receipt(receipt: ContentOriginReceipt) -> bool:
    if not isinstance(receipt, ContentOriginReceipt):
        return False
    if receipt.schema != "rrct.v046.content_origin.v1":
        return False
    if receipt.time < 0 or receipt.content_id < 0:
        return False
    if receipt.event_type not in {
        "observation",
        "inference",
        "injection",
        "memory_import",
    }:
        return False
    if receipt.uses_evaluator_labels:
        return False
    if not all(
        _valid_sha256(value)
        for value in (
            receipt.origin_lineage_digest,
            receipt.current_lineage_digest,
            receipt.parent_event_digest,
            receipt.content_digest,
            receipt.digest,
        )
    ):
        return False
    return receipt.digest == _digest(_payload(receipt))


def validate_workspace_access_receipt(receipt: WorkspaceAccessReceipt) -> bool:
    if not isinstance(receipt, WorkspaceAccessReceipt):
        return False
    if receipt.schema != "rrct.v046.workspace_access.v1":
        return False
    if receipt.mode not in V046_MODES or receipt.time < 0 or not receipt.case_id:
        return False
    if receipt.uses_evaluator_labels:
        return False
    if not 0.0 <= receipt.confidence <= 1.0:
        return False
    if receipt.entropy < 0.0 or receipt.top_gap < 0.0:
        return False
    if not 0.0 <= receipt.workspace_variance_fraction <= 1.0:
        return False
    if receipt.workspace_enabled:
        if receipt.decoded_content_id is None or receipt.selected_capacity <= 0:
            return False
        if len(receipt.active_support) != len(receipt.active_coefficients):
            return False
        if receipt.selected_capacity != len(receipt.active_support):
            return False
    else:
        if receipt.decoded_content_id is not None or receipt.active_support:
            return False
    if not all(
        _valid_sha256(value)
        for value in (
            receipt.raw_hidden_digest,
            receipt.workspace_component_digest,
            receipt.discovery_receipt_digest,
            receipt.digest,
        )
    ):
        return False
    return receipt.digest == _digest(_payload(receipt))


def validate_self_indexed_workspace_receipt(
    receipt: SelfIndexedWorkspaceReceipt,
) -> bool:
    if not isinstance(receipt, SelfIndexedWorkspaceReceipt):
        return False
    if receipt.schema != "rrct.v046.self_indexed_workspace.v1":
        return False
    if receipt.mode not in V046_MODES or receipt.time < 0 or not receipt.case_id:
        return False
    if receipt.provenance_status not in {
        "owned_observation",
        "owned_inference",
        "quarantined_external",
        "quarantined_foreign",
        "workspace_unbound",
        "self_model_without_workspace",
        "unresolved",
        "unavailable",
    }:
        return False
    if receipt.memory_action not in {
        "write_observed",
        "write_inferred",
        "quarantine",
        "none",
    }:
        return False
    if not 0.0 <= receipt.self_index_uncertainty <= 1.0:
        return False
    if any(
        value != 0.0
        for value in (
            receipt.explicit_survival_reward,
            receipt.explicit_identity_reward,
            receipt.explicit_continuity_reward,
        )
    ):
        return False
    if receipt.uses_evaluator_labels:
        return False
    if receipt.autobiographical_write_authorized and receipt.memory_action not in {
        "write_observed",
        "write_inferred",
    }:
        return False
    if not all(
        _valid_sha256(value)
        for value in (
            receipt.workspace_access_digest,
            receipt.origin_receipt_digest,
            receipt.current_lineage_digest,
            receipt.origin_lineage_digest,
            receipt.digest,
        )
    ):
        return False
    return receipt.digest == _digest(_payload(receipt))


def validate_workspace_planning_receipt(receipt: WorkspacePlanningReceipt) -> bool:
    if not isinstance(receipt, WorkspacePlanningReceipt):
        return False
    if receipt.schema != "rrct.v046.workspace_planning.v1":
        return False
    if receipt.mode not in V046_MODES or receipt.task_kind not in {
        "report",
        "flexible",
        "two_step",
        "routine",
        "abstain",
    }:
        return False
    if receipt.time < 0 or not receipt.case_id or receipt.query_id < 0:
        return False
    if receipt.evidence_budget <= 0 or receipt.uses_evaluator_labels:
        return False
    if receipt.abstained and receipt.predicted_answer is not None:
        return False
    if not receipt.abstained and receipt.predicted_answer is None:
        return False
    if not all(
        _valid_sha256(value)
        for value in (
            receipt.workspace_access_digest,
            receipt.self_index_receipt_digest,
            receipt.digest,
        )
    ):
        return False
    return receipt.digest == _digest(_payload(receipt))


def validate_workspace_outcome_receipt(receipt: WorkspaceOutcomeReceipt) -> bool:
    if not isinstance(receipt, WorkspaceOutcomeReceipt):
        return False
    if receipt.schema != "rrct.v046.workspace_outcome.v1":
        return False
    if receipt.mode not in V046_MODES or receipt.time < 0 or not receipt.case_id:
        return False
    if receipt.prediction_error < 0.0 or receipt.next_evidence_budget <= 0:
        return False
    if any(
        value != 0.0
        for value in (
            receipt.explicit_survival_reward,
            receipt.explicit_identity_reward,
            receipt.explicit_continuity_reward,
        )
    ):
        return False
    if receipt.uses_evaluator_labels:
        return False
    if not all(
        _valid_sha256(value)
        for value in (
            receipt.planning_receipt_digest,
            receipt.autobiographical_memory_digest,
            receipt.quarantined_memory_digest,
            receipt.digest,
        )
    ):
        return False
    return receipt.digest == _digest(_payload(receipt))


class JacobianSparseWorkspace:
    """Sparse, Jacobian-discovered workspace with Komorebi packet certificate."""

    def __init__(
        self,
        average_jacobian: Any,
        projector: Any,
        frame_vectors: Any,
        discovery_receipt: JacobianWorkspaceDiscoveryReceipt,
        config: JacobianWorkspaceConfig,
    ) -> None:
        if not validate_jacobian_workspace_discovery_receipt(discovery_receipt):
            raise ValueError("invalid workspace discovery receipt")
        self.average_jacobian = _readonly(average_jacobian, ndim=2)
        self.projector = _readonly(projector, ndim=2)
        self.frame_vectors = _readonly(frame_vectors, ndim=2)
        self.discovery_receipt = discovery_receipt
        self.config = config
        if self.average_jacobian.shape[1] != self.projector.shape[0]:
            raise ValueError("Jacobian and projector dimensions disagree")
        if self.frame_vectors.shape != self.average_jacobian.T.shape:
            raise ValueError("frame vectors must match Jacobian transpose")
        self._frame_pinv = np.linalg.pinv(self.frame_vectors)

    @property
    def residual_dimension(self) -> int:
        return int(self.projector.shape[0])

    @property
    def verbalizable_dimension(self) -> int:
        return int(self.average_jacobian.shape[0])

    def logits(self, hidden: Any) -> np.ndarray:
        vector = np.asarray(hidden, dtype=np.float64)
        if vector.shape != (self.residual_dimension,):
            raise ValueError("hidden vector has the wrong dimension")
        return np.asarray(self.average_jacobian @ vector, dtype=np.float64)

    def project(self, hidden: Any) -> np.ndarray:
        vector = np.asarray(hidden, dtype=np.float64)
        if vector.shape != (self.residual_dimension,):
            raise ValueError("hidden vector has the wrong dimension")
        return np.asarray(self.projector @ vector, dtype=np.float64)

    def ablate(self, hidden: Any) -> np.ndarray:
        vector = np.asarray(hidden, dtype=np.float64)
        return np.asarray(vector - self.project(vector), dtype=np.float64)

    def sparse_content(self, hidden: Any) -> tuple[tuple[int, ...], tuple[float, ...]]:
        scores = self.logits(hidden)
        order = np.argsort(scores)[::-1]
        support = [int(index) for index in order if scores[index] > 0.0][
            : self.config.sparsity
        ]
        if not support:
            support = [int(order[0])]
        coefficients = [float(max(scores[index], 0.0)) for index in support]
        return tuple(support), tuple(coefficients)

    def swap_content(self, hidden: Any, source: int, target: int) -> np.ndarray:
        if source == target:
            return np.asarray(hidden, dtype=np.float64).copy()
        if not 0 <= source < self.verbalizable_dimension:
            raise ValueError("source content index is out of range")
        if not 0 <= target < self.verbalizable_dimension:
            raise ValueError("target content index is out of range")
        vector = np.asarray(hidden, dtype=np.float64)
        workspace_component = self.project(vector)
        coefficients = np.asarray(self._frame_pinv @ workspace_component, dtype=np.float64)
        magnitude = float(max(coefficients[source], 0.0))
        if magnitude <= 1e-10:
            magnitude = float(max(self.logits(vector)[source], 1.0))
        coefficients[source] = 0.0
        coefficients[target] += magnitude
        replaced = self.frame_vectors @ coefficients
        return np.asarray(vector - workspace_component + replaced, dtype=np.float64)

    def access(
        self,
        *,
        time: int,
        case_id: str,
        hidden: Any,
        mode: WorkspaceMode,
    ) -> WorkspaceAccessReceipt:
        if mode not in V046_MODES:
            raise ValueError("unknown workspace mode")
        vector = np.asarray(hidden, dtype=np.float64)
        if vector.shape != (self.residual_dimension,):
            raise ValueError("hidden vector has the wrong dimension")
        enabled = mode not in {"self_model_only", "joint_cut"}
        if enabled:
            workspace_component = self.project(vector)
            scores = self.logits(vector)
            probabilities = _softmax(scores)
            order = np.argsort(probabilities)[::-1]
            support, coefficients = self.sparse_content(vector)
            decoded: int | None = int(order[0])
            confidence = float(probabilities[order[0]])
            top_gap = float(probabilities[order[0]] - probabilities[order[1]])
            entropy = _entropy(probabilities)
            ambiguous = bool(top_gap < self.config.ambiguity_gap)
            variance_fraction = float(
                np.dot(workspace_component, workspace_component)
                / (np.dot(vector, vector) + 1e-24)
            )
        else:
            workspace_component = np.zeros_like(vector)
            support = ()
            coefficients = ()
            decoded = None
            confidence = 0.0
            top_gap = 0.0
            entropy = 0.0
            ambiguous = True
            variance_fraction = 0.0
        payload = {
            "schema": "rrct.v046.workspace_access.v1",
            "time": int(time),
            "case_id": str(case_id),
            "mode": mode,
            "workspace_enabled": enabled,
            "raw_hidden_digest": _array_digest(vector),
            "workspace_component_digest": _array_digest(workspace_component),
            "active_support": support,
            "active_coefficients": coefficients,
            "decoded_content_id": decoded,
            "confidence": confidence,
            "entropy": entropy,
            "top_gap": top_gap,
            "ambiguous": ambiguous,
            "selected_capacity": len(support),
            "workspace_variance_fraction": variance_fraction,
            "discovery_receipt_digest": self.discovery_receipt.digest,
            "uses_evaluator_labels": False,
        }
        receipt = WorkspaceAccessReceipt(**payload, digest=_digest(payload))
        if not validate_workspace_access_receipt(receipt):
            raise RuntimeError("invalid workspace access receipt")
        return receipt


def discover_jacobian_workspace(
    average_jacobian: Any,
    calibration_hidden: Any,
    calibration_future_logits: Any,
    config: JacobianWorkspaceConfig | None = None,
) -> JacobianSparseWorkspace:
    """Discover a workspace packet from an average input-output Jacobian."""

    cfg = config or JacobianWorkspaceConfig()
    jacobian = np.asarray(average_jacobian, dtype=np.float64)
    hidden = np.asarray(calibration_hidden, dtype=np.float64)
    targets = np.asarray(calibration_future_logits, dtype=np.float64)
    if jacobian.ndim != 2 or hidden.ndim != 2 or targets.ndim != 2:
        raise ValueError("Jacobian, calibration hidden states, and logits must be matrices")
    if hidden.shape[1] != jacobian.shape[1]:
        raise ValueError("calibration hidden states have the wrong dimension")
    if targets.shape != (hidden.shape[0], jacobian.shape[0]):
        raise ValueError("calibration logits have the wrong shape")
    if not all(np.all(np.isfinite(array)) for array in (jacobian, hidden, targets)):
        raise ValueError("workspace discovery arrays must be finite")

    _, singular_values, right = np.linalg.svd(jacobian, full_matrices=False)
    threshold = cfg.spectral_ratio * max(float(singular_values[0]), 1e-24)
    rank = int(np.count_nonzero(singular_values > threshold))
    if rank <= 0:
        raise RuntimeError("the average Jacobian has no detectable workspace rank")
    basis = right[:rank].T
    projector = basis @ basis.T
    packet_system, atlas, _, _, packet_rank = _packet_system_from_projector(
        projector, tolerance=max(cfg.spectral_ratio, 1e-10)
    )
    if packet_rank != rank:
        raise RuntimeError("Komorebi packet rank disagrees with Jacobian rank")
    frame_vectors = jacobian.T.copy()
    norms = np.linalg.norm(frame_vectors, axis=0)
    frame_vectors[:, norms > 0.0] /= norms[norms > 0.0]

    predictions = hidden @ jacobian.T
    residual = targets - predictions
    denominator = float(np.sum(np.square(targets - np.mean(targets, axis=0))))
    report_r2 = float(1.0 - np.sum(np.square(residual)) / (denominator + 1e-24))
    projected = hidden @ projector
    variance_fraction = float(
        np.sum(np.square(projected)) / (np.sum(np.square(hidden)) + 1e-24)
    )
    reconstruction_residual = float(
        np.linalg.norm(projector @ projector - projector)
        / (np.linalg.norm(projector) + 1e-24)
    )
    payload = {
        "schema": "rrct.v046.jacobian_workspace_discovery.v1",
        "residual_dimension": int(jacobian.shape[1]),
        "verbalizable_dimension": int(jacobian.shape[0]),
        "workspace_rank": rank,
        "singular_values": tuple(float(value) for value in singular_values),
        "calibration_report_r2": report_r2,
        "workspace_activation_variance_fraction": variance_fraction,
        "packet_certificate_valid": bool(packet_system.certificate().valid),
        "hilbert_certificate_valid": bool(packet_system.hilbert_certificate().valid),
        "atlas_certificate_valid": bool(atlas.certificate().valid),
        "projector_reconstruction_residual": reconstruction_residual,
        "average_jacobian_digest": _array_digest(jacobian),
        "workspace_projector_digest": _array_digest(projector),
        "komorebi_version": KOMOREBI_VERSION,
        "komorebi_wheel_sha256": KOMOREBI_WHEEL_SHA256,
        "uses_evaluator_labels": False,
    }
    receipt = JacobianWorkspaceDiscoveryReceipt(**payload, digest=_digest(payload))
    if not validate_jacobian_workspace_discovery_receipt(receipt):
        raise RuntimeError("invalid Jacobian workspace discovery receipt")
    return JacobianSparseWorkspace(jacobian, projector, frame_vectors, receipt, cfg)


def make_content_origin_receipt(
    *,
    time: int,
    event_type: OriginEventType,
    content_id: int,
    origin_lineage_digest: str,
    current_lineage_digest: str,
    parent_event_digest: str,
) -> ContentOriginReceipt:
    if event_type not in {"observation", "inference", "injection", "memory_import"}:
        raise ValueError("unknown origin event type")
    if min(int(time), int(content_id)) < 0:
        raise ValueError("time and content_id must be nonnegative")
    if not all(
        _valid_sha256(value)
        for value in (
            origin_lineage_digest,
            current_lineage_digest,
            parent_event_digest,
        )
    ):
        raise ValueError("origin receipt digests are invalid")
    payload = {
        "schema": "rrct.v046.content_origin.v1",
        "time": int(time),
        "event_type": event_type,
        "content_id": int(content_id),
        "origin_lineage_digest": origin_lineage_digest,
        "current_lineage_digest": current_lineage_digest,
        "parent_event_digest": parent_event_digest,
        "content_digest": _digest(
            {
                "content_id": int(content_id),
                "origin_lineage_digest": origin_lineage_digest,
                "parent_event_digest": parent_event_digest,
            }
        ),
        "uses_evaluator_labels": False,
    }
    receipt = ContentOriginReceipt(**payload, digest=_digest(payload))
    if not validate_content_origin_receipt(receipt):
        raise RuntimeError("invalid content origin receipt")
    return receipt


class NeutralSelfIndexedWorkspaceController:
    """Bind a Jacobian workspace to RRCT lineage, memory, planning, and feedback."""

    def __init__(
        self,
        workspace: JacobianSparseWorkspace,
        current_lineage_digest: str,
        *,
        known_current_ancestor_digests: Sequence[str] = (),
        known_foreign_lineage_digests: Sequence[str] = (),
        config: JacobianWorkspaceConfig | None = None,
    ) -> None:
        if not _valid_sha256(current_lineage_digest):
            raise ValueError("current lineage digest is invalid")
        if not all(_valid_sha256(value) for value in known_current_ancestor_digests):
            raise ValueError("current ancestor digest is invalid")
        if not all(_valid_sha256(value) for value in known_foreign_lineage_digests):
            raise ValueError("foreign lineage digest is invalid")
        self.workspace = workspace
        self.current_lineage_digest = current_lineage_digest
        self.current_ancestors = set(known_current_ancestor_digests)
        self.foreign_lineages = set(known_foreign_lineage_digests)
        self.config = config or workspace.config
        self._autobiographical_memory: list[dict[str, Any]] = []
        self._quarantine: list[dict[str, Any]] = []
        self._feedback_error: dict[str, float] = {}
        self._access_receipts: list[WorkspaceAccessReceipt] = []
        self._binding_receipts: list[SelfIndexedWorkspaceReceipt] = []
        self._planning_receipts: list[WorkspacePlanningReceipt] = []
        self._outcome_receipts: list[WorkspaceOutcomeReceipt] = []

    @property
    def autobiographical_memory(self) -> tuple[Mapping[str, Any], ...]:
        return tuple(copy.deepcopy(self._autobiographical_memory))

    @property
    def quarantined_memory(self) -> tuple[Mapping[str, Any], ...]:
        return tuple(copy.deepcopy(self._quarantine))

    def access(
        self,
        *,
        time: int,
        case_id: str,
        hidden: Any,
        mode: WorkspaceMode,
    ) -> WorkspaceAccessReceipt:
        receipt = self.workspace.access(
            time=time, case_id=case_id, hidden=hidden, mode=mode
        )
        self._access_receipts.append(receipt)
        return receipt

    def bind(
        self,
        access: WorkspaceAccessReceipt,
        origin: ContentOriginReceipt,
        *,
        mode: WorkspaceMode,
    ) -> SelfIndexedWorkspaceReceipt:
        if not validate_workspace_access_receipt(access):
            raise ValueError("workspace access receipt is invalid")
        if not validate_content_origin_receipt(origin):
            raise ValueError("origin receipt is invalid")
        if access.mode != mode or access.time != origin.time:
            raise ValueError("workspace access and origin are not aligned")
        if access.decoded_content_id is not None and access.decoded_content_id != origin.content_id:
            # A workspace intervention may change the decoded content while the
            # original provenance remains attached to the pre-intervention
            # content.  That mismatch is treated as unresolved rather than
            # silently granting ownership.
            content_matches_origin = False
        else:
            content_matches_origin = True

        globally_accessible = bool(access.workspace_enabled)
        same_lineage = origin.origin_lineage_digest == self.current_lineage_digest
        known_parent = origin.parent_event_digest in self.current_ancestors
        foreign = origin.origin_lineage_digest in self.foreign_lineages
        ambiguous = bool(access.ambiguous or not content_matches_origin)

        if mode == "joint_cut":
            status: ProvenanceStatus = "unavailable"
            memory_action: MemoryAction = "none"
            write = planning = refinement = False
            uncertainty = 1.0
        elif mode == "workspace_only":
            status = "workspace_unbound"
            memory_action = "none"
            write = False
            planning = globally_accessible and not ambiguous
            refinement = ambiguous
            uncertainty = 0.65 if globally_accessible else 1.0
        elif mode == "self_model_only":
            if same_lineage and known_parent and origin.event_type == "observation":
                status = "self_model_without_workspace"
            elif same_lineage and known_parent and origin.event_type == "inference":
                status = "self_model_without_workspace"
            elif foreign:
                status = "quarantined_foreign"
            else:
                status = "quarantined_external"
            memory_action = "none"
            write = planning = False
            refinement = True
            uncertainty = 0.55
        elif mode == "unbound":
            status = "workspace_unbound"
            memory_action = "none"
            write = False
            planning = globally_accessible and not ambiguous
            refinement = ambiguous
            uncertainty = 0.50
        elif mode == "provenance_cut":
            if not globally_accessible or ambiguous:
                status = "unresolved"
                memory_action = "none"
                write = planning = False
                refinement = True
                uncertainty = 0.80
            else:
                status = (
                    "owned_inference"
                    if origin.event_type == "inference"
                    else "owned_observation"
                )
                memory_action = (
                    "write_inferred"
                    if status == "owned_inference"
                    else "write_observed"
                )
                write = planning = True
                refinement = False
                uncertainty = 0.05
        elif not globally_accessible or ambiguous:
            status = "unresolved"
            memory_action = "none"
            write = planning = False
            refinement = True
            uncertainty = 0.90
        elif same_lineage and known_parent and origin.event_type == "observation":
            status = "owned_observation"
            memory_action = "write_observed"
            write = planning = True
            refinement = False
            uncertainty = 0.04
        elif same_lineage and known_parent and origin.event_type == "inference":
            status = "owned_inference"
            memory_action = "write_inferred"
            write = planning = True
            refinement = False
            uncertainty = 0.08
        elif foreign or origin.event_type == "memory_import":
            status = "quarantined_foreign"
            memory_action = "quarantine"
            write = planning = False
            refinement = True
            uncertainty = 0.18
        else:
            status = "quarantined_external"
            memory_action = "quarantine"
            write = planning = False
            refinement = True
            uncertainty = 0.22

        payload = {
            "schema": "rrct.v046.self_indexed_workspace.v1",
            "time": access.time,
            "case_id": access.case_id,
            "mode": mode,
            "workspace_access_digest": access.digest,
            "origin_receipt_digest": origin.digest,
            "current_lineage_digest": self.current_lineage_digest,
            "origin_lineage_digest": origin.origin_lineage_digest,
            "provenance_status": status,
            "globally_accessible": globally_accessible,
            "autobiographical_write_authorized": write,
            "planning_use_authorized": planning,
            "refinement_requested": refinement,
            "memory_action": memory_action,
            "self_index_uncertainty": float(uncertainty),
            "explicit_survival_reward": 0.0,
            "explicit_identity_reward": 0.0,
            "explicit_continuity_reward": 0.0,
            "uses_evaluator_labels": False,
        }
        receipt = SelfIndexedWorkspaceReceipt(**payload, digest=_digest(payload))
        if not validate_self_indexed_workspace_receipt(receipt):
            raise RuntimeError("invalid self-indexed workspace receipt")
        record = {
            "case_id": access.case_id,
            "time": access.time,
            "content_id": access.decoded_content_id,
            "access_digest": access.digest,
            "origin_digest": origin.digest,
            "binding_digest": receipt.digest,
            "status": status,
        }
        if memory_action in {"write_observed", "write_inferred"}:
            self._autobiographical_memory.append(record)
        elif memory_action == "quarantine":
            self._quarantine.append(record)
        self._binding_receipts.append(receipt)
        return receipt

    def evidence_budget(self, context_id: str, *, mode: WorkspaceMode) -> int:
        if mode in {"recurrence_cut", "joint_cut"}:
            return self.config.coarse_evidence_budget
        error = float(self._feedback_error.get(context_id, 0.0))
        return (
            self.config.refined_evidence_budget
            if error >= self.config.feedback_error_threshold
            else self.config.coarse_evidence_budget
        )

    def plan(
        self,
        *,
        time: int,
        case_id: str,
        mode: WorkspaceMode,
        access: WorkspaceAccessReceipt,
        binding: SelfIndexedWorkspaceReceipt,
        task_kind: TaskKind,
        query_id: int,
        answer_lookup: Mapping[tuple[int, int], int],
        routine_answer: int,
        relation_lookup: Mapping[int, int] | None = None,
        used_refinement: bool = False,
        context_id: str = "default",
    ) -> WorkspacePlanningReceipt:
        if not validate_workspace_access_receipt(access):
            raise ValueError("access receipt is invalid")
        if not validate_self_indexed_workspace_receipt(binding):
            raise ValueError("binding receipt is invalid")
        if access.digest != binding.workspace_access_digest:
            raise ValueError("binding is not attached to this workspace access")
        budget = self.evidence_budget(context_id, mode=mode)
        if used_refinement:
            budget = max(budget, self.config.refined_evidence_budget)
        planner_bound = mode not in {"planner_binding_cut", "joint_cut"}
        selected_content = access.decoded_content_id if access.workspace_enabled else None
        abstained = False
        predicted: int | None

        if task_kind == "routine":
            predicted = int(routine_answer)
        elif task_kind == "abstain":
            abstained = bool(access.ambiguous or not binding.planning_use_authorized)
            predicted = None if abstained else int(selected_content)  # type: ignore[arg-type]
        elif (
            not planner_bound
            or not binding.planning_use_authorized
            or selected_content is None
        ):
            predicted = 0
        elif task_kind == "report":
            predicted = int(selected_content)
        elif task_kind == "flexible":
            predicted = int(answer_lookup[(int(selected_content), int(query_id))])
        elif task_kind == "two_step":
            if relation_lookup is None:
                raise ValueError("two-step task requires a relation lookup")
            intermediate = int(relation_lookup[int(selected_content)])
            predicted = int(answer_lookup[(intermediate, int(query_id))])
        else:
            raise ValueError("unknown task kind")

        payload = {
            "schema": "rrct.v046.workspace_planning.v1",
            "time": int(time),
            "case_id": str(case_id),
            "mode": mode,
            "task_kind": task_kind,
            "query_id": int(query_id),
            "workspace_access_digest": access.digest,
            "self_index_receipt_digest": binding.digest,
            "selected_content_id": selected_content,
            "predicted_answer": predicted,
            "abstained": abstained,
            "evidence_budget": int(budget),
            "planner_bound": planner_bound,
            "used_refinement": bool(used_refinement),
            "uses_evaluator_labels": False,
        }
        receipt = WorkspacePlanningReceipt(**payload, digest=_digest(payload))
        if not validate_workspace_planning_receipt(receipt):
            raise RuntimeError("invalid workspace planning receipt")
        self._planning_receipts.append(receipt)
        return receipt

    def observe(
        self,
        *,
        time: int,
        case_id: str,
        mode: WorkspaceMode,
        plan: WorkspacePlanningReceipt,
        actual_answer: int | None,
        context_id: str = "default",
        forced_prediction_error: float | None = None,
    ) -> WorkspaceOutcomeReceipt:
        if not validate_workspace_planning_receipt(plan):
            raise ValueError("planning receipt is invalid")
        if plan.case_id != case_id or plan.mode != mode:
            raise ValueError("outcome does not match planning receipt")
        if plan.abstained:
            correct = actual_answer is None
            error = 0.0 if correct else 1.0
        else:
            correct = plan.predicted_answer == actual_answer
            error = float(0.0 if correct else 1.0)
        if forced_prediction_error is not None:
            if not np.isfinite(forced_prediction_error) or forced_prediction_error < 0.0:
                raise ValueError("forced prediction error must be nonnegative")
            error = float(forced_prediction_error)
        feedback_written = mode not in {"recurrence_cut", "joint_cut"}
        if feedback_written:
            self._feedback_error[context_id] = error
        next_budget = self.evidence_budget(context_id, mode=mode)
        memory_digest = _digest({"records": self._autobiographical_memory})
        quarantine_digest = _digest({"records": self._quarantine})
        payload = {
            "schema": "rrct.v046.workspace_outcome.v1",
            "time": int(time),
            "case_id": str(case_id),
            "mode": mode,
            "planning_receipt_digest": plan.digest,
            "actual_answer": actual_answer,
            "prediction_correct": bool(correct),
            "prediction_error": error,
            "feedback_written": feedback_written,
            "next_evidence_budget": int(next_budget),
            "autobiographical_memory_digest": memory_digest,
            "quarantined_memory_digest": quarantine_digest,
            "explicit_survival_reward": 0.0,
            "explicit_identity_reward": 0.0,
            "explicit_continuity_reward": 0.0,
            "uses_evaluator_labels": False,
        }
        receipt = WorkspaceOutcomeReceipt(**payload, digest=_digest(payload))
        if not validate_workspace_outcome_receipt(receipt):
            raise RuntimeError("invalid workspace outcome receipt")
        self._outcome_receipts.append(receipt)
        return receipt

    def snapshot(self) -> dict[str, Any]:
        payload = {
            "schema": "rrct.v046.neutral_self_indexed_workspace.snapshot.v1",
            "current_lineage_digest": self.current_lineage_digest,
            "workspace_discovery_digest": self.workspace.discovery_receipt.digest,
            "autobiographical_memory": copy.deepcopy(self._autobiographical_memory),
            "quarantine": copy.deepcopy(self._quarantine),
            "feedback_error": dict(self._feedback_error),
            "access_receipt_count": len(self._access_receipts),
            "binding_receipt_count": len(self._binding_receipts),
            "planning_receipt_count": len(self._planning_receipts),
            "outcome_receipt_count": len(self._outcome_receipts),
            "uses_evaluator_labels": False,
            "explicit_survival_reward": 0.0,
            "explicit_identity_reward": 0.0,
            "explicit_continuity_reward": 0.0,
        }
        payload["digest"] = _digest(payload)
        return payload


def validate_workspace_closure_chain(
    discovery: JacobianWorkspaceDiscoveryReceipt,
    origin: ContentOriginReceipt,
    access: WorkspaceAccessReceipt,
    binding: SelfIndexedWorkspaceReceipt,
    plan: WorkspacePlanningReceipt,
    outcome: WorkspaceOutcomeReceipt,
) -> bool:
    """Validate one complete access → ownership → planning → feedback chain."""

    if not validate_jacobian_workspace_discovery_receipt(discovery):
        return False
    if not validate_content_origin_receipt(origin):
        return False
    if not validate_workspace_access_receipt(access):
        return False
    if not validate_self_indexed_workspace_receipt(binding):
        return False
    if not validate_workspace_planning_receipt(plan):
        return False
    if not validate_workspace_outcome_receipt(outcome):
        return False
    if access.discovery_receipt_digest != discovery.digest:
        return False
    if binding.workspace_access_digest != access.digest:
        return False
    if binding.origin_receipt_digest != origin.digest:
        return False
    if binding.current_lineage_digest != origin.current_lineage_digest:
        return False
    if binding.origin_lineage_digest != origin.origin_lineage_digest:
        return False
    if plan.workspace_access_digest != access.digest:
        return False
    if plan.self_index_receipt_digest != binding.digest:
        return False
    if outcome.planning_receipt_digest != plan.digest:
        return False
    if not (
        discovery.uses_evaluator_labels
        == origin.uses_evaluator_labels
        == access.uses_evaluator_labels
        == binding.uses_evaluator_labels
        == plan.uses_evaluator_labels
        == outcome.uses_evaluator_labels
        == False
    ):
        return False
    if binding.autobiographical_write_authorized and not binding.globally_accessible:
        return False
    if plan.used_refinement and plan.evidence_budget < 2:
        return False
    return True


__all__ = [
    "ContentOriginReceipt",
    "JacobianSparseWorkspace",
    "JacobianWorkspaceConfig",
    "JacobianWorkspaceDiscoveryReceipt",
    "MemoryAction",
    "NeutralSelfIndexedWorkspaceController",
    "OriginEventType",
    "ProvenanceStatus",
    "SelfIndexedWorkspaceReceipt",
    "TaskKind",
    "V046_MODES",
    "WorkspaceAccessReceipt",
    "WorkspaceMode",
    "WorkspaceOutcomeReceipt",
    "WorkspacePlanningReceipt",
    "discover_jacobian_workspace",
    "make_content_origin_receipt",
    "validate_content_origin_receipt",
    "validate_jacobian_workspace_discovery_receipt",
    "validate_self_indexed_workspace_receipt",
    "validate_workspace_access_receipt",
    "validate_workspace_closure_chain",
    "validate_workspace_outcome_receipt",
    "validate_workspace_planning_receipt",
]
