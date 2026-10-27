"""RRCT v0.47 distributed shared workspace.

This module tests a narrow computational claim: two individually complete,
self-indexed workspaces can form a hidden, causally distributed coordination
manifold through interaction.  The shared manifold is discovered from paired
workspace trajectories, not from evaluator factor labels.  It is then required
to pass stronger tests than communication success alone: bidirectional causal
write access, joint sufficiency, provenance-aware persistence, planner binding,
and consequence-driven recurrence.

The implementation is synthetic and deterministic under fixed seeds.  It does
not claim a shared subjective mind, phenomenal consciousness, valence, desire,
or moral status.
"""
from __future__ import annotations

import copy
import hashlib
from dataclasses import asdict, dataclass
from typing import Any, Literal, Mapping, Sequence

import numpy as np

from .jspace_self_indexed_workspace import (
    JacobianSparseWorkspace,
    _array_digest,
    _entropy,
    _softmax,
    _valid_sha256,
    validate_jacobian_workspace_discovery_receipt,
)
from .komorebi_operator_self_model import (
    KOMOREBI_VERSION,
    KOMOREBI_WHEEL_SHA256,
    _packet_system_from_projector,
)
from .transformational_self_continuity import _digest

SharedMode = Literal[
    "full_shared",
    "message_only",
    "workspace_cut",
    "message_shuffle",
    "one_way",
    "provenance_cut",
    "planner_binding_cut",
    "recurrence_cut",
    "joint_cut",
]

V047_MODES: tuple[SharedMode, ...] = (
    "full_shared",
    "message_only",
    "workspace_cut",
    "message_shuffle",
    "one_way",
    "provenance_cut",
    "planner_binding_cut",
    "recurrence_cut",
    "joint_cut",
)

ProvenanceStatus = Literal[
    "compatible_pair",
    "quarantined_foreign_pair",
    "unbound",
]
MemoryAction = Literal["write_joint", "quarantine", "none"]


def _readonly(value: Any, *, ndim: int | None = None) -> np.ndarray:
    array = np.asarray(value, dtype=np.float64)
    if ndim is not None and array.ndim != ndim:
        raise ValueError(f"expected {ndim}-D array")
    if not np.all(np.isfinite(array)):
        raise ValueError("array must be finite")
    result = np.array(array, dtype=np.float64, copy=True)
    result.setflags(write=False)
    return result


def _valid_nonnegative_int(value: Any) -> bool:
    return bool(
        not isinstance(value, (bool, np.bool_))
        and isinstance(value, (int, np.integer))
        and int(value) >= 0
    )


def _payload(receipt: Any) -> dict[str, Any]:
    payload = asdict(receipt)
    payload.pop("digest", None)
    return payload


def _ridge_fit(features: Any, targets: Any, ridge: float) -> np.ndarray:
    x = np.asarray(features, dtype=np.float64)
    y = np.asarray(targets, dtype=np.float64)
    if x.ndim != 2 or y.ndim != 2 or x.shape[0] != y.shape[0]:
        raise ValueError("ridge arrays have incompatible shapes")
    design = np.concatenate([x, np.ones((x.shape[0], 1))], axis=1)
    penalty = float(ridge) * np.eye(design.shape[1])
    penalty[-1, -1] = 0.0
    return np.linalg.solve(design.T @ design + penalty, design.T @ y)


def _ridge_predict(features: Any, weights: Any) -> np.ndarray:
    x = np.asarray(features, dtype=np.float64)
    w = np.asarray(weights, dtype=np.float64)
    one = x.ndim == 1
    if one:
        x = x[None, :]
    design = np.concatenate([x, np.ones((x.shape[0], 1))], axis=1)
    result = design @ w
    return result[0] if one else result


def _inverse_sqrt(matrix: np.ndarray, ridge: float) -> np.ndarray:
    symmetric = 0.5 * (matrix + matrix.T)
    values, vectors = np.linalg.eigh(symmetric)
    values = np.maximum(values, float(ridge))
    return np.asarray(vectors @ np.diag(values ** -0.5) @ vectors.T)


def _r2(actual: Any, predicted: Any) -> float:
    y = np.asarray(actual, dtype=np.float64)
    p = np.asarray(predicted, dtype=np.float64)
    if y.shape != p.shape:
        return float("-inf")
    residual = float(np.sum(np.square(y - p)))
    centered = y - np.mean(y, axis=0, keepdims=True)
    denominator = float(np.sum(np.square(centered)))
    return float(1.0 - residual / (denominator + 1e-24))


@dataclass(frozen=True)
class DistributedWorkspaceConfig:
    ridge: float = 1e-6
    spectral_ratio: float = 1e-3
    minimum_canonical_correlation: float = 0.80
    coarse_rounds: int = 1
    refined_rounds: int = 3
    feedback_error_threshold: float = 0.25
    ambiguity_gap: float = 0.12

    def __post_init__(self) -> None:
        numeric = (
            self.ridge,
            self.spectral_ratio,
            self.minimum_canonical_correlation,
            self.feedback_error_threshold,
            self.ambiguity_gap,
        )
        if not all(np.isfinite(value) and value > 0.0 for value in numeric):
            raise ValueError("distributed workspace numeric parameters must be positive")
        if self.minimum_canonical_correlation >= 1.0:
            raise ValueError("minimum canonical correlation must be below one")
        integers = (self.coarse_rounds, self.refined_rounds)
        if any(isinstance(value, bool) or int(value) <= 0 for value in integers):
            raise ValueError("evidence rounds must be positive integers")
        if self.refined_rounds <= self.coarse_rounds:
            raise ValueError("refined rounds must exceed coarse rounds")


@dataclass(frozen=True)
class SharedAtlasDiscoveryReceipt:
    schema: str
    calibration_samples: int
    agent_a_dimension: int
    agent_b_dimension: int
    shared_rank: int
    canonical_correlations: tuple[float, ...]
    cross_agent_alignment_r2: float
    agent_a_shared_variance_fraction: float
    agent_b_shared_variance_fraction: float
    agent_a_packet_certificate_valid: bool
    agent_b_packet_certificate_valid: bool
    agent_a_hilbert_certificate_valid: bool
    agent_b_hilbert_certificate_valid: bool
    agent_a_atlas_certificate_valid: bool
    agent_b_atlas_certificate_valid: bool
    agent_a_local_workspace_digest: str
    agent_b_local_workspace_digest: str
    agent_a_projector_digest: str
    agent_b_projector_digest: str
    komorebi_version: str
    komorebi_wheel_sha256: str
    uses_evaluator_labels: bool
    digest: str


@dataclass(frozen=True)
class PairMessageReceipt:
    schema: str
    time: int
    episode_id: str
    round_index: int
    sender_lineage_digest: str
    receiver_lineage_digest: str
    pair_lineage_digest: str
    message_dimension: int
    message_digest: str
    communication_enabled: bool
    shuffled: bool
    uses_evaluator_labels: bool
    digest: str


@dataclass(frozen=True)
class JointWorkspaceReceipt:
    schema: str
    time: int
    episode_id: str
    mode: SharedMode
    pair_lineage_digest: str
    origin_pair_lineage_digest: str
    atlas_discovery_digest: str
    agent_a_message_digest: str
    agent_b_message_digest: str
    agent_a_state_digest: str
    agent_b_state_digest: str
    shared_state_digest: str
    shared_enabled: bool
    bidirectional: bool
    aligned_private_only: bool
    decoded_action: int | None
    confidence: float
    entropy: float
    top_gap: float
    ambiguous: bool
    evidence_rounds: int
    provenance_status: ProvenanceStatus
    memory_action: MemoryAction
    autobiographical_write_authorized: bool
    planner_use_authorized: bool
    explicit_survival_reward: float
    explicit_identity_reward: float
    explicit_continuity_reward: float
    uses_evaluator_labels: bool
    digest: str


@dataclass(frozen=True)
class JointPlanningReceipt:
    schema: str
    time: int
    episode_id: str
    mode: SharedMode
    joint_workspace_digest: str
    selected_action: int | None
    predicted_action: int | None
    abstained: bool
    planner_bound: bool
    evidence_rounds: int
    uses_shared_workspace: bool
    uses_message_only_route: bool
    uses_evaluator_labels: bool
    digest: str


@dataclass(frozen=True)
class JointOutcomeReceipt:
    schema: str
    time: int
    episode_id: str
    mode: SharedMode
    planning_receipt_digest: str
    actual_action: int
    prediction_correct: bool
    prediction_error: float
    feedback_written: bool
    next_evidence_rounds: int
    joint_memory_digest: str
    quarantined_memory_digest: str
    explicit_survival_reward: float
    explicit_identity_reward: float
    explicit_continuity_reward: float
    uses_evaluator_labels: bool
    digest: str


def validate_shared_atlas_discovery_receipt(
    receipt: SharedAtlasDiscoveryReceipt,
) -> bool:
    if not isinstance(receipt, SharedAtlasDiscoveryReceipt):
        return False
    if receipt.schema != "rrct.v047.shared_atlas_discovery.v1":
        return False
    if receipt.uses_evaluator_labels:
        return False
    if not all(
        _valid_nonnegative_int(value)
        for value in (
            receipt.calibration_samples,
            receipt.agent_a_dimension,
            receipt.agent_b_dimension,
            receipt.shared_rank,
        )
    ):
        return False
    if min(
        receipt.calibration_samples,
        receipt.agent_a_dimension,
        receipt.agent_b_dimension,
        receipt.shared_rank,
    ) <= 0:
        return False
    if len(receipt.canonical_correlations) != receipt.shared_rank:
        return False
    if not all(0.0 <= value <= 1.0 + 1e-9 for value in receipt.canonical_correlations):
        return False
    if not np.isfinite(receipt.cross_agent_alignment_r2):
        return False
    if not 0.0 <= receipt.agent_a_shared_variance_fraction <= 1.0 + 1e-9:
        return False
    if not 0.0 <= receipt.agent_b_shared_variance_fraction <= 1.0 + 1e-9:
        return False
    if not all(
        (
            receipt.agent_a_packet_certificate_valid,
            receipt.agent_b_packet_certificate_valid,
            receipt.agent_a_hilbert_certificate_valid,
            receipt.agent_b_hilbert_certificate_valid,
            receipt.agent_a_atlas_certificate_valid,
            receipt.agent_b_atlas_certificate_valid,
        )
    ):
        return False
    digests = (
        receipt.agent_a_local_workspace_digest,
        receipt.agent_b_local_workspace_digest,
        receipt.agent_a_projector_digest,
        receipt.agent_b_projector_digest,
        receipt.komorebi_wheel_sha256,
        receipt.digest,
    )
    if not all(_valid_sha256(value) for value in digests):
        return False
    if receipt.komorebi_version != KOMOREBI_VERSION:
        return False
    if receipt.komorebi_wheel_sha256 != KOMOREBI_WHEEL_SHA256:
        return False
    return receipt.digest == _digest(_payload(receipt))


def validate_pair_message_receipt(receipt: PairMessageReceipt) -> bool:
    if not isinstance(receipt, PairMessageReceipt):
        return False
    if receipt.schema != "rrct.v047.pair_message.v1":
        return False
    if receipt.uses_evaluator_labels:
        return False
    if not all(
        _valid_nonnegative_int(value)
        for value in (receipt.time, receipt.round_index, receipt.message_dimension)
    ):
        return False
    if receipt.message_dimension <= 0 or not receipt.episode_id:
        return False
    digests = (
        receipt.sender_lineage_digest,
        receipt.receiver_lineage_digest,
        receipt.pair_lineage_digest,
        receipt.message_digest,
        receipt.digest,
    )
    if not all(_valid_sha256(value) for value in digests):
        return False
    return receipt.digest == _digest(_payload(receipt))


def validate_joint_workspace_receipt(receipt: JointWorkspaceReceipt) -> bool:
    if not isinstance(receipt, JointWorkspaceReceipt):
        return False
    if receipt.schema != "rrct.v047.joint_workspace.v1":
        return False
    if receipt.mode not in V047_MODES or receipt.uses_evaluator_labels:
        return False
    if not _valid_nonnegative_int(receipt.time) or not _valid_nonnegative_int(
        receipt.evidence_rounds
    ):
        return False
    if receipt.evidence_rounds <= 0 or not receipt.episode_id:
        return False
    required = (
        receipt.pair_lineage_digest,
        receipt.origin_pair_lineage_digest,
        receipt.atlas_discovery_digest,
        receipt.agent_a_message_digest,
        receipt.agent_b_message_digest,
        receipt.agent_a_state_digest,
        receipt.agent_b_state_digest,
        receipt.shared_state_digest,
        receipt.digest,
    )
    if not all(_valid_sha256(value) for value in required):
        return False
    if receipt.decoded_action is not None and not _valid_nonnegative_int(
        receipt.decoded_action
    ):
        return False
    if not 0.0 <= receipt.confidence <= 1.0 + 1e-9:
        return False
    if receipt.entropy < 0.0 or receipt.top_gap < 0.0:
        return False
    if receipt.provenance_status not in {
        "compatible_pair",
        "quarantined_foreign_pair",
        "unbound",
    }:
        return False
    if receipt.memory_action not in {"write_joint", "quarantine", "none"}:
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
    if receipt.provenance_status == "quarantined_foreign_pair":
        if receipt.autobiographical_write_authorized:
            return False
        if receipt.memory_action != "quarantine":
            return False
    if receipt.memory_action == "write_joint" and not receipt.autobiographical_write_authorized:
        return False
    if receipt.planner_use_authorized and not (
        receipt.shared_enabled or receipt.mode == "message_only"
    ):
        return False
    return receipt.digest == _digest(_payload(receipt))


def validate_joint_planning_receipt(receipt: JointPlanningReceipt) -> bool:
    if not isinstance(receipt, JointPlanningReceipt):
        return False
    if receipt.schema != "rrct.v047.joint_planning.v1":
        return False
    if receipt.mode not in V047_MODES or receipt.uses_evaluator_labels:
        return False
    if not _valid_nonnegative_int(receipt.time) or not _valid_nonnegative_int(
        receipt.evidence_rounds
    ):
        return False
    if not receipt.episode_id or not _valid_sha256(receipt.joint_workspace_digest):
        return False
    for value in (receipt.selected_action, receipt.predicted_action):
        if value is not None and not _valid_nonnegative_int(value):
            return False
    if receipt.planner_bound and receipt.abstained:
        return False
    if receipt.uses_shared_workspace and receipt.uses_message_only_route:
        return False
    if not _valid_sha256(receipt.digest):
        return False
    return receipt.digest == _digest(_payload(receipt))


def validate_joint_outcome_receipt(receipt: JointOutcomeReceipt) -> bool:
    if not isinstance(receipt, JointOutcomeReceipt):
        return False
    if receipt.schema != "rrct.v047.joint_outcome.v1":
        return False
    if receipt.mode not in V047_MODES or receipt.uses_evaluator_labels:
        return False
    if not _valid_nonnegative_int(receipt.time) or not _valid_nonnegative_int(
        receipt.actual_action
    ):
        return False
    if not _valid_nonnegative_int(receipt.next_evidence_rounds):
        return False
    if receipt.prediction_error < 0.0 or not np.isfinite(receipt.prediction_error):
        return False
    required = (
        receipt.planning_receipt_digest,
        receipt.joint_memory_digest,
        receipt.quarantined_memory_digest,
        receipt.digest,
    )
    if not all(_valid_sha256(value) for value in required):
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
    return receipt.digest == _digest(_payload(receipt))


class SharedWorkspaceAtlas:
    """A paired shared/private factorization discovered without evaluator labels."""

    def __init__(
        self,
        *,
        mean_a: Any,
        mean_b: Any,
        basis_a: Any,
        basis_b: Any,
        scale_a: Any,
        scale_b: Any,
        b_to_a: Any,
        discovery_receipt: SharedAtlasDiscoveryReceipt,
        config: DistributedWorkspaceConfig,
    ) -> None:
        if not validate_shared_atlas_discovery_receipt(discovery_receipt):
            raise ValueError("invalid shared atlas discovery receipt")
        self.mean_a = _readonly(mean_a, ndim=1)
        self.mean_b = _readonly(mean_b, ndim=1)
        self.basis_a = _readonly(basis_a, ndim=2)
        self.basis_b = _readonly(basis_b, ndim=2)
        self.scale_a = _readonly(scale_a, ndim=1)
        self.scale_b = _readonly(scale_b, ndim=1)
        self.b_to_a = _readonly(b_to_a, ndim=2)
        self.discovery_receipt = discovery_receipt
        self.config = config
        rank = discovery_receipt.shared_rank
        if self.basis_a.shape != (self.mean_a.size, rank):
            raise ValueError("agent A shared basis shape mismatch")
        if self.basis_b.shape != (self.mean_b.size, rank):
            raise ValueError("agent B shared basis shape mismatch")
        if self.scale_a.shape != (rank,) or self.scale_b.shape != (rank,):
            raise ValueError("shared scale shape mismatch")
        if self.b_to_a.shape != (rank, rank):
            raise ValueError("shared alignment shape mismatch")
        self.projector_a = _readonly(self.basis_a @ self.basis_a.T, ndim=2)
        self.projector_b = _readonly(self.basis_b @ self.basis_b.T, ndim=2)

    @property
    def shared_rank(self) -> int:
        return int(self.discovery_receipt.shared_rank)

    def encode_a(self, state: Any) -> np.ndarray:
        vector = np.asarray(state, dtype=np.float64)
        if vector.shape != self.mean_a.shape:
            raise ValueError("agent A state has the wrong dimension")
        return np.asarray(((vector - self.mean_a) @ self.basis_a) / self.scale_a)

    def encode_b(self, state: Any) -> np.ndarray:
        vector = np.asarray(state, dtype=np.float64)
        if vector.shape != self.mean_b.shape:
            raise ValueError("agent B state has the wrong dimension")
        local = ((vector - self.mean_b) @ self.basis_b) / self.scale_b
        return np.asarray(local @ self.b_to_a)

    def shared_state(self, state_a: Any, state_b: Any) -> np.ndarray:
        return np.asarray(0.5 * (self.encode_a(state_a) + self.encode_b(state_b)))

    def write_a(self, state: Any, shared: Any) -> np.ndarray:
        vector = np.asarray(state, dtype=np.float64)
        target = np.asarray(shared, dtype=np.float64)
        if target.shape != (self.shared_rank,):
            raise ValueError("shared state has the wrong rank")
        centered = vector - self.mean_a
        private = centered - self.projector_a @ centered
        component = self.basis_a @ (target * self.scale_a)
        return np.asarray(self.mean_a + private + component)

    def write_b(self, state: Any, shared: Any) -> np.ndarray:
        vector = np.asarray(state, dtype=np.float64)
        target = np.asarray(shared, dtype=np.float64)
        if target.shape != (self.shared_rank,):
            raise ValueError("shared state has the wrong rank")
        centered = vector - self.mean_b
        private = centered - self.projector_b @ centered
        local_standard = target @ self.b_to_a.T
        component = self.basis_b @ (local_standard * self.scale_b)
        return np.asarray(self.mean_b + private + component)

    def ablate_a(self, state: Any) -> np.ndarray:
        vector = np.asarray(state, dtype=np.float64)
        centered = vector - self.mean_a
        return np.asarray(self.mean_a + centered - self.projector_a @ centered)

    def ablate_b(self, state: Any) -> np.ndarray:
        vector = np.asarray(state, dtype=np.float64)
        centered = vector - self.mean_b
        return np.asarray(self.mean_b + centered - self.projector_b @ centered)


def discover_shared_workspace(
    agent_a_states: Any,
    agent_b_states: Any,
    agent_a_local_workspace: JacobianSparseWorkspace,
    agent_b_local_workspace: JacobianSparseWorkspace,
    config: DistributedWorkspaceConfig | None = None,
) -> SharedWorkspaceAtlas:
    """Discover a paired shared manifold using only synchronized trajectories."""

    cfg = config or DistributedWorkspaceConfig()
    x = np.asarray(agent_a_states, dtype=np.float64)
    y = np.asarray(agent_b_states, dtype=np.float64)
    if x.ndim != 2 or y.ndim != 2 or x.shape[0] != y.shape[0]:
        raise ValueError("paired agent states must be two matrices with equal rows")
    if x.shape[0] < 4:
        raise ValueError("shared workspace discovery requires at least four samples")
    if x.shape[1] != agent_a_local_workspace.residual_dimension:
        raise ValueError("agent A calibration dimension mismatch")
    if y.shape[1] != agent_b_local_workspace.residual_dimension:
        raise ValueError("agent B calibration dimension mismatch")
    if not validate_jacobian_workspace_discovery_receipt(
        agent_a_local_workspace.discovery_receipt
    ) or not validate_jacobian_workspace_discovery_receipt(
        agent_b_local_workspace.discovery_receipt
    ):
        raise ValueError("local workspace discovery receipts must validate")

    # Restrict factorization to content that each local workspace makes globally
    # available.  Private and automatic activity may remain in the full states.
    x_projected = x @ agent_a_local_workspace.projector
    y_projected = y @ agent_b_local_workspace.projector
    mean_a = np.mean(x_projected, axis=0)
    mean_b = np.mean(y_projected, axis=0)
    xc = x_projected - mean_a
    yc = y_projected - mean_b
    denominator = max(x.shape[0] - 1, 1)
    cxx = xc.T @ xc / denominator + cfg.ridge * np.eye(x.shape[1])
    cyy = yc.T @ yc / denominator + cfg.ridge * np.eye(y.shape[1])
    cxy = xc.T @ yc / denominator
    whitened = _inverse_sqrt(cxx, cfg.ridge) @ cxy @ _inverse_sqrt(cyy, cfg.ridge)
    _, correlations, _ = np.linalg.svd(whitened, full_matrices=False)
    rank = int(np.count_nonzero(correlations >= cfg.minimum_canonical_correlation))
    if rank <= 0:
        raise RuntimeError("no shared canonical workspace was detected")

    # Raw cross-covariance singular vectors give orthonormal local packet bases.
    left, singular_values, right_t = np.linalg.svd(cxy, full_matrices=False)
    spectral_threshold = cfg.spectral_ratio * max(float(singular_values[0]), 1e-24)
    spectral_rank = int(np.count_nonzero(singular_values > spectral_threshold))
    rank = min(rank, spectral_rank)
    if rank <= 0:
        raise RuntimeError("shared workspace rank vanished under spectral threshold")
    basis_a = left[:, :rank]
    basis_b = right_t.T[:, :rank]
    raw_a = xc @ basis_a
    raw_b = yc @ basis_b
    scale_a = np.std(raw_a, axis=0, ddof=1)
    scale_b = np.std(raw_b, axis=0, ddof=1)
    scale_a = np.maximum(scale_a, cfg.ridge)
    scale_b = np.maximum(scale_b, cfg.ridge)
    standard_a = raw_a / scale_a
    standard_b = raw_b / scale_b
    u, _, vt = np.linalg.svd(standard_b.T @ standard_a, full_matrices=False)
    b_to_a = u @ vt
    aligned_b = standard_b @ b_to_a
    alignment_r2 = _r2(standard_a, aligned_b)
    projector_a = basis_a @ basis_a.T
    projector_b = basis_b @ basis_b.T
    packet_a, atlas_a, _, _, packet_rank_a = _packet_system_from_projector(
        projector_a, tolerance=max(cfg.spectral_ratio, 1e-10)
    )
    packet_b, atlas_b, _, _, packet_rank_b = _packet_system_from_projector(
        projector_b, tolerance=max(cfg.spectral_ratio, 1e-10)
    )
    if packet_rank_a != rank or packet_rank_b != rank:
        raise RuntimeError("Komorebi packet rank disagrees with shared rank")
    variance_a = float(
        np.sum(np.square(xc @ projector_a)) / (np.sum(np.square(x - np.mean(x, axis=0))) + 1e-24)
    )
    variance_b = float(
        np.sum(np.square(yc @ projector_b)) / (np.sum(np.square(y - np.mean(y, axis=0))) + 1e-24)
    )
    payload = {
        "schema": "rrct.v047.shared_atlas_discovery.v1",
        "calibration_samples": int(x.shape[0]),
        "agent_a_dimension": int(x.shape[1]),
        "agent_b_dimension": int(y.shape[1]),
        "shared_rank": int(rank),
        "canonical_correlations": tuple(float(value) for value in correlations[:rank]),
        "cross_agent_alignment_r2": float(alignment_r2),
        "agent_a_shared_variance_fraction": variance_a,
        "agent_b_shared_variance_fraction": variance_b,
        "agent_a_packet_certificate_valid": bool(packet_a.certificate().valid),
        "agent_b_packet_certificate_valid": bool(packet_b.certificate().valid),
        "agent_a_hilbert_certificate_valid": bool(packet_a.hilbert_certificate().valid),
        "agent_b_hilbert_certificate_valid": bool(packet_b.hilbert_certificate().valid),
        "agent_a_atlas_certificate_valid": bool(atlas_a.certificate().valid),
        "agent_b_atlas_certificate_valid": bool(atlas_b.certificate().valid),
        "agent_a_local_workspace_digest": agent_a_local_workspace.discovery_receipt.digest,
        "agent_b_local_workspace_digest": agent_b_local_workspace.discovery_receipt.digest,
        "agent_a_projector_digest": _array_digest(projector_a),
        "agent_b_projector_digest": _array_digest(projector_b),
        "komorebi_version": KOMOREBI_VERSION,
        "komorebi_wheel_sha256": KOMOREBI_WHEEL_SHA256,
        "uses_evaluator_labels": False,
    }
    receipt = SharedAtlasDiscoveryReceipt(**payload, digest=_digest(payload))
    if not validate_shared_atlas_discovery_receipt(receipt):
        raise RuntimeError("invalid shared atlas discovery receipt")
    return SharedWorkspaceAtlas(
        mean_a=mean_a,
        mean_b=mean_b,
        basis_a=basis_a,
        basis_b=basis_b,
        scale_a=scale_a,
        scale_b=scale_b,
        b_to_a=b_to_a,
        discovery_receipt=receipt,
        config=cfg,
    )


def make_pair_message_receipt(
    *,
    time: int,
    episode_id: str,
    round_index: int,
    sender_lineage_digest: str,
    receiver_lineage_digest: str,
    pair_lineage_digest: str,
    message: Any,
    communication_enabled: bool,
    shuffled: bool,
) -> PairMessageReceipt:
    vector = np.asarray(message, dtype=np.float64)
    if vector.ndim != 1 or vector.size <= 0 or not np.all(np.isfinite(vector)):
        raise ValueError("message must be a finite nonempty vector")
    payload = {
        "schema": "rrct.v047.pair_message.v1",
        "time": int(time),
        "episode_id": str(episode_id),
        "round_index": int(round_index),
        "sender_lineage_digest": str(sender_lineage_digest),
        "receiver_lineage_digest": str(receiver_lineage_digest),
        "pair_lineage_digest": str(pair_lineage_digest),
        "message_dimension": int(vector.size),
        "message_digest": _array_digest(vector),
        "communication_enabled": bool(communication_enabled),
        "shuffled": bool(shuffled),
        "uses_evaluator_labels": False,
    }
    receipt = PairMessageReceipt(**payload, digest=_digest(payload))
    if not validate_pair_message_receipt(receipt):
        raise RuntimeError("invalid pair message receipt")
    return receipt


class DistributedSharedWorkspaceController:
    """Bind a discovered shared manifold to pair provenance, planning, and feedback."""

    def __init__(
        self,
        atlas: SharedWorkspaceAtlas,
        *,
        agent_a_lineage_digest: str,
        agent_b_lineage_digest: str,
        joint_action_decoder: Any,
        message_action_decoder: Any,
        action_count: int,
        config: DistributedWorkspaceConfig | None = None,
    ) -> None:
        if not _valid_sha256(agent_a_lineage_digest) or not _valid_sha256(
            agent_b_lineage_digest
        ):
            raise ValueError("agent lineage digests must be SHA-256 values")
        if isinstance(action_count, bool) or int(action_count) <= 1:
            raise ValueError("action_count must exceed one")
        self.atlas = atlas
        self.config = config or atlas.config
        self.agent_a_lineage_digest = str(agent_a_lineage_digest)
        self.agent_b_lineage_digest = str(agent_b_lineage_digest)
        self.pair_lineage_digest = _digest(
            {
                "schema": "rrct.v047.pair_lineage.v1",
                "agent_a": self.agent_a_lineage_digest,
                "agent_b": self.agent_b_lineage_digest,
                "atlas": atlas.discovery_receipt.digest,
            }
        )
        self.joint_action_decoder = _readonly(joint_action_decoder, ndim=2)
        self.message_action_decoder = _readonly(message_action_decoder, ndim=2)
        self.action_count = int(action_count)
        if self.joint_action_decoder.shape != (atlas.shared_rank + 1, action_count):
            raise ValueError("joint action decoder shape mismatch")
        if self.message_action_decoder.shape[1] != action_count:
            raise ValueError("message action decoder shape mismatch")
        self._joint_memory: list[dict[str, Any]] = []
        self._quarantined_memory: list[dict[str, Any]] = []
        self._next_rounds = self.config.coarse_rounds

    @property
    def next_evidence_rounds(self) -> int:
        return int(self._next_rounds)

    @property
    def joint_memory_digest(self) -> str:
        return _digest({"schema": "rrct.v047.joint_memory.v1", "rows": self._joint_memory})

    @property
    def quarantined_memory_digest(self) -> str:
        return _digest(
            {"schema": "rrct.v047.quarantined_joint_memory.v1", "rows": self._quarantined_memory}
        )

    def integrate(
        self,
        *,
        time: int,
        episode_id: str,
        mode: SharedMode,
        state_a: Any,
        state_b: Any,
        message_a: Any,
        message_b: Any,
        message_a_receipt: PairMessageReceipt,
        message_b_receipt: PairMessageReceipt,
        origin_pair_lineage_digest: str,
        evidence_rounds: int | None = None,
    ) -> tuple[JointWorkspaceReceipt, np.ndarray, np.ndarray, np.ndarray]:
        if mode not in V047_MODES:
            raise ValueError("unknown distributed workspace mode")
        if not validate_pair_message_receipt(message_a_receipt) or not validate_pair_message_receipt(
            message_b_receipt
        ):
            raise ValueError("message receipts must validate")
        if message_a_receipt.pair_lineage_digest != self.pair_lineage_digest:
            raise ValueError("agent A message is bound to another pair")
        if message_b_receipt.pair_lineage_digest != self.pair_lineage_digest:
            raise ValueError("agent B message is bound to another pair")
        vector_a = np.asarray(state_a, dtype=np.float64)
        vector_b = np.asarray(state_b, dtype=np.float64)
        msg_a = np.asarray(message_a, dtype=np.float64)
        msg_b = np.asarray(message_b, dtype=np.float64)
        rounds = self._next_rounds if evidence_rounds is None else int(evidence_rounds)
        if rounds <= 0:
            raise ValueError("evidence rounds must be positive")

        shared_enabled = mode not in {"message_only", "workspace_cut", "joint_cut"}
        bidirectional = mode not in {"message_only", "one_way", "joint_cut"}
        aligned_private_only = mode == "message_only"
        if shared_enabled:
            if mode == "one_way":
                # Agent A obtains the complete interaction state, while B retains
                # only its local state.  The composite state is therefore not a
                # bidirectionally writable workspace.
                shared = self.atlas.encode_a(vector_a)
            else:
                shared = self.atlas.shared_state(vector_a, vector_b)
            written_a = self.atlas.write_a(vector_a, shared)
            written_b = (
                self.atlas.write_b(vector_b, shared) if bidirectional else vector_b.copy()
            )
        else:
            shared = np.zeros(self.atlas.shared_rank, dtype=np.float64)
            written_a = self.atlas.ablate_a(vector_a) if mode in {"workspace_cut", "joint_cut"} else vector_a.copy()
            written_b = self.atlas.ablate_b(vector_b) if mode in {"workspace_cut", "joint_cut"} else vector_b.copy()

        if origin_pair_lineage_digest == self.pair_lineage_digest:
            provenance: ProvenanceStatus = "compatible_pair"
        elif mode == "provenance_cut":
            provenance = "compatible_pair"
        else:
            provenance = "quarantined_foreign_pair"

        if mode == "message_only":
            message_features = np.concatenate([msg_a, msg_b])
            logits = _ridge_predict(message_features, self.message_action_decoder)
        elif shared_enabled:
            logits = _ridge_predict(shared, self.joint_action_decoder)
        else:
            logits = np.zeros(self.action_count, dtype=np.float64)
        probabilities = _softmax(logits)
        order = np.argsort(probabilities)[::-1]
        decoded = int(order[0]) if (shared_enabled or mode == "message_only") else None
        confidence = float(probabilities[order[0]]) if decoded is not None else 0.0
        gap = float(probabilities[order[0]] - probabilities[order[1]]) if decoded is not None else 0.0
        entropy = _entropy(probabilities) if decoded is not None else 0.0
        ambiguous = bool(decoded is None or gap < self.config.ambiguity_gap)
        write_authorized = bool(
            provenance == "compatible_pair"
            and mode not in {"message_only", "workspace_cut", "joint_cut"}
        )
        planner_authorized = bool(
            provenance == "compatible_pair"
            and mode not in {"workspace_cut", "planner_binding_cut", "joint_cut"}
            and (shared_enabled or mode == "message_only")
        )
        if write_authorized:
            memory_action: MemoryAction = "write_joint"
        elif provenance == "quarantined_foreign_pair":
            memory_action = "quarantine"
        else:
            memory_action = "none"
        payload = {
            "schema": "rrct.v047.joint_workspace.v1",
            "time": int(time),
            "episode_id": str(episode_id),
            "mode": mode,
            "pair_lineage_digest": self.pair_lineage_digest,
            "origin_pair_lineage_digest": str(origin_pair_lineage_digest),
            "atlas_discovery_digest": self.atlas.discovery_receipt.digest,
            "agent_a_message_digest": message_a_receipt.digest,
            "agent_b_message_digest": message_b_receipt.digest,
            "agent_a_state_digest": _array_digest(written_a),
            "agent_b_state_digest": _array_digest(written_b),
            "shared_state_digest": _array_digest(shared),
            "shared_enabled": bool(shared_enabled),
            "bidirectional": bool(bidirectional),
            "aligned_private_only": bool(aligned_private_only),
            "decoded_action": decoded,
            "confidence": confidence,
            "entropy": entropy,
            "top_gap": gap,
            "ambiguous": ambiguous,
            "evidence_rounds": int(rounds),
            "provenance_status": provenance,
            "memory_action": memory_action,
            "autobiographical_write_authorized": write_authorized,
            "planner_use_authorized": planner_authorized,
            "explicit_survival_reward": 0.0,
            "explicit_identity_reward": 0.0,
            "explicit_continuity_reward": 0.0,
            "uses_evaluator_labels": False,
        }
        receipt = JointWorkspaceReceipt(**payload, digest=_digest(payload))
        if not validate_joint_workspace_receipt(receipt):
            raise RuntimeError("invalid joint workspace receipt")
        if memory_action == "write_joint":
            self._joint_memory.append(
                {
                    "episode_id": str(episode_id),
                    "shared_state_digest": receipt.shared_state_digest,
                    "workspace_digest": receipt.digest,
                    "origin_pair_lineage_digest": str(origin_pair_lineage_digest),
                }
            )
        elif memory_action == "quarantine":
            self._quarantined_memory.append(
                {
                    "episode_id": str(episode_id),
                    "shared_state_digest": receipt.shared_state_digest,
                    "workspace_digest": receipt.digest,
                    "origin_pair_lineage_digest": str(origin_pair_lineage_digest),
                }
            )
        return receipt, shared, written_a, written_b

    def plan(
        self,
        *,
        time: int,
        workspace: JointWorkspaceReceipt,
    ) -> JointPlanningReceipt:
        if not validate_joint_workspace_receipt(workspace):
            raise ValueError("joint workspace receipt must validate")
        if workspace.pair_lineage_digest != self.pair_lineage_digest:
            raise ValueError("joint workspace is bound to another pair")
        planner_bound = bool(workspace.planner_use_authorized)
        selected = workspace.decoded_action if planner_bound else None
        payload = {
            "schema": "rrct.v047.joint_planning.v1",
            "time": int(time),
            "episode_id": workspace.episode_id,
            "mode": workspace.mode,
            "joint_workspace_digest": workspace.digest,
            "selected_action": selected,
            "predicted_action": selected,
            "abstained": bool(selected is None),
            "planner_bound": planner_bound,
            "evidence_rounds": int(workspace.evidence_rounds),
            "uses_shared_workspace": bool(planner_bound and workspace.shared_enabled),
            "uses_message_only_route": bool(planner_bound and workspace.mode == "message_only"),
            "uses_evaluator_labels": False,
        }
        receipt = JointPlanningReceipt(**payload, digest=_digest(payload))
        if not validate_joint_planning_receipt(receipt):
            raise RuntimeError("invalid joint planning receipt")
        return receipt

    def observe(
        self,
        *,
        time: int,
        plan: JointPlanningReceipt,
        actual_action: int,
    ) -> JointOutcomeReceipt:
        if not validate_joint_planning_receipt(plan):
            raise ValueError("joint plan must validate")
        if not _valid_nonnegative_int(actual_action) or int(actual_action) >= self.action_count:
            raise ValueError("actual action is out of range")
        correct = bool(plan.selected_action == int(actual_action))
        error = 0.0 if correct else 1.0
        feedback_written = bool(plan.mode != "recurrence_cut")
        if feedback_written and error >= self.config.feedback_error_threshold:
            self._next_rounds = self.config.refined_rounds
        elif feedback_written:
            self._next_rounds = self.config.coarse_rounds
        payload = {
            "schema": "rrct.v047.joint_outcome.v1",
            "time": int(time),
            "episode_id": plan.episode_id,
            "mode": plan.mode,
            "planning_receipt_digest": plan.digest,
            "actual_action": int(actual_action),
            "prediction_correct": correct,
            "prediction_error": float(error),
            "feedback_written": feedback_written,
            "next_evidence_rounds": int(self._next_rounds),
            "joint_memory_digest": self.joint_memory_digest,
            "quarantined_memory_digest": self.quarantined_memory_digest,
            "explicit_survival_reward": 0.0,
            "explicit_identity_reward": 0.0,
            "explicit_continuity_reward": 0.0,
            "uses_evaluator_labels": False,
        }
        receipt = JointOutcomeReceipt(**payload, digest=_digest(payload))
        if not validate_joint_outcome_receipt(receipt):
            raise RuntimeError("invalid joint outcome receipt")
        return receipt

    def snapshot(self) -> dict[str, Any]:
        payload = {
            "schema": "rrct.v047.distributed_shared_workspace_controller.v1",
            "pair_lineage_digest": self.pair_lineage_digest,
            "agent_a_lineage_digest": self.agent_a_lineage_digest,
            "agent_b_lineage_digest": self.agent_b_lineage_digest,
            "atlas_discovery_digest": self.atlas.discovery_receipt.digest,
            "next_evidence_rounds": int(self._next_rounds),
            "joint_memory": copy.deepcopy(self._joint_memory),
            "quarantined_memory": copy.deepcopy(self._quarantined_memory),
            "explicit_survival_reward": 0.0,
            "explicit_identity_reward": 0.0,
            "explicit_continuity_reward": 0.0,
            "uses_evaluator_labels": False,
        }
        payload["digest"] = _digest(payload)
        return payload


def validate_distributed_workspace_chain(
    atlas: SharedAtlasDiscoveryReceipt,
    message_a: PairMessageReceipt,
    message_b: PairMessageReceipt,
    workspace: JointWorkspaceReceipt,
    plan: JointPlanningReceipt,
    outcome: JointOutcomeReceipt,
) -> bool:
    if not validate_shared_atlas_discovery_receipt(atlas):
        return False
    if not validate_pair_message_receipt(message_a) or not validate_pair_message_receipt(
        message_b
    ):
        return False
    if not validate_joint_workspace_receipt(workspace):
        return False
    if not validate_joint_planning_receipt(plan):
        return False
    if not validate_joint_outcome_receipt(outcome):
        return False
    if workspace.atlas_discovery_digest != atlas.digest:
        return False
    if workspace.agent_a_message_digest != message_a.digest:
        return False
    if workspace.agent_b_message_digest != message_b.digest:
        return False
    if not (
        message_a.pair_lineage_digest
        == message_b.pair_lineage_digest
        == workspace.pair_lineage_digest
    ):
        return False
    if not (
        message_a.episode_id
        == message_b.episode_id
        == workspace.episode_id
        == plan.episode_id
        == outcome.episode_id
    ):
        return False
    if plan.joint_workspace_digest != workspace.digest:
        return False
    if outcome.planning_receipt_digest != plan.digest:
        return False
    if min(message_a.time, message_b.time) > workspace.time:
        return False
    if workspace.time > plan.time or plan.time > outcome.time:
        return False
    if plan.mode != workspace.mode or outcome.mode != plan.mode:
        return False
    if plan.planner_bound != workspace.planner_use_authorized:
        return False
    if workspace.provenance_status == "quarantined_foreign_pair" and plan.planner_bound:
        return False
    return True


__all__ = [
    "DistributedSharedWorkspaceController",
    "DistributedWorkspaceConfig",
    "JointOutcomeReceipt",
    "JointPlanningReceipt",
    "JointWorkspaceReceipt",
    "PairMessageReceipt",
    "SharedAtlasDiscoveryReceipt",
    "SharedMode",
    "SharedWorkspaceAtlas",
    "V047_MODES",
    "discover_shared_workspace",
    "make_pair_message_receipt",
    "validate_distributed_workspace_chain",
    "validate_joint_outcome_receipt",
    "validate_joint_planning_receipt",
    "validate_joint_workspace_receipt",
    "validate_pair_message_receipt",
    "validate_shared_atlas_discovery_receipt",
]
