"""RRCT v0.48 distributed sparse J-space.

This module joins the v0.46 Jacobian-discovered sparse workspace with the v0.47
atlas-aligned distributed workspace.  It tests a bounded functional claim:
independently parameterized agents can instantiate local Jacobian workspaces
whose state-dependent sparse contents are aligned into a bidirectionally causal,
pair-provenance-bound shared workspace.

The implementation is a synthetic linear analogue.  It is not an experiment on
Claude or any other production language model, and it makes no claim about
phenomenal consciousness or shared subjective experience.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping, Sequence

import numpy as np

from .distributed_shared_workspace import (
    DistributedWorkspaceConfig,
    JointOutcomeReceipt,
    JointPlanningReceipt,
    JointWorkspaceReceipt,
    PairMessageReceipt,
    SharedWorkspaceAtlas,
    discover_shared_workspace,
    validate_distributed_workspace_chain,
    validate_joint_outcome_receipt,
    validate_joint_planning_receipt,
    validate_joint_workspace_receipt,
    validate_pair_message_receipt,
    validate_shared_atlas_discovery_receipt,
)
from .jspace_self_indexed_workspace import (
    JacobianSparseWorkspace,
    JacobianWorkspaceConfig,
    WorkspaceAccessReceipt,
    validate_jacobian_workspace_discovery_receipt,
    validate_workspace_access_receipt,
)
from .transformational_self_continuity import _digest


def _readonly(value: Any, *, ndim: int | None = None) -> np.ndarray:
    array = np.asarray(value, dtype=np.float64)
    if ndim is not None and array.ndim != ndim:
        raise ValueError(f"expected a {ndim}-dimensional array")
    if not np.all(np.isfinite(array)):
        raise ValueError("array must be finite")
    result = np.array(array, dtype=np.float64, copy=True)
    result.setflags(write=False)
    return result


def _array_digest(value: Any) -> str:
    array = np.asarray(value, dtype=np.float64)
    return _digest(
        {
            "shape": tuple(int(item) for item in array.shape),
            "dtype": "float64",
            "data": array,
        }
    )


def _valid_sha256(value: Any) -> bool:
    return bool(
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _payload(receipt: Any) -> dict[str, Any]:
    value = asdict(receipt)
    value.pop("digest", None)
    return value


def _cosine_rows(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    left_norm = np.maximum(np.linalg.norm(left, axis=1, keepdims=True), 1e-24)
    right_norm = np.maximum(np.linalg.norm(right, axis=1, keepdims=True), 1e-24)
    return (left / left_norm) @ (right / right_norm).T


def _greedy_positive_matching(similarity: np.ndarray) -> tuple[int, ...]:
    if similarity.ndim != 2 or similarity.shape[0] != similarity.shape[1]:
        raise ValueError("concept similarity must be a square matrix")
    count = similarity.shape[0]
    candidates = sorted(
        (
            (float(similarity[i, j]), int(i), int(j))
            for i in range(count)
            for j in range(count)
        ),
        reverse=True,
    )
    mapping = [-1] * count  # local B index -> local A canonical index
    used_a: set[int] = set()
    used_b: set[int] = set()
    for score, index_a, index_b in candidates:
        if index_a in used_a or index_b in used_b:
            continue
        mapping[index_b] = index_a
        used_a.add(index_a)
        used_b.add(index_b)
        if len(used_a) == count:
            break
    if any(index < 0 for index in mapping):
        raise RuntimeError("failed to construct a complete concept matching")
    return tuple(mapping)


@dataclass(frozen=True)
class DistributedJSpaceConfig:
    local_workspace: JacobianWorkspaceConfig = JacobianWorkspaceConfig(
        sparsity=4,
        ambiguity_gap=0.06,
        maximum_workspace_variance_fraction=0.15,
    )
    shared_workspace: DistributedWorkspaceConfig = DistributedWorkspaceConfig(
        minimum_canonical_correlation=0.80,
        ambiguity_gap=0.08,
    )
    support_capacity: int = 4
    minimum_frame_cosine: float = 0.95
    minimum_support_agreement: float = 0.95

    def __post_init__(self) -> None:
        if isinstance(self.support_capacity, bool) or int(self.support_capacity) <= 0:
            raise ValueError("support_capacity must be a positive integer")
        if not 0.0 < float(self.minimum_frame_cosine) <= 1.0:
            raise ValueError("minimum_frame_cosine must lie in (0, 1]")
        if not 0.0 < float(self.minimum_support_agreement) <= 1.0:
            raise ValueError("minimum_support_agreement must lie in (0, 1]")


@dataclass(frozen=True)
class DistributedJSpaceDiscoveryReceipt:
    schema: str
    calibration_samples: int
    residual_dimension_a: int
    residual_dimension_b: int
    local_workspace_rank_a: int
    local_workspace_rank_b: int
    shared_rank: int
    shared_frame_count: int
    support_capacity: int
    minimum_canonical_correlation: float
    cross_agent_alignment_r2: float
    minimum_frame_alignment_cosine: float
    mean_frame_alignment_cosine: float
    support_exact_agreement_rate: float
    dynamic_support_count: int
    local_a_discovery_digest: str
    local_b_discovery_digest: str
    shared_atlas_discovery_digest: str
    shared_frame_digest: str
    concept_map_b_to_a: tuple[int, ...]
    opposite_concept_map: tuple[int, ...]
    packet_certificates_valid: bool
    uses_evaluator_labels: bool
    digest: str


@dataclass(frozen=True)
class DistributedJSpaceAccessReceipt:
    schema: str
    time: int
    episode_id: str
    pair_lineage_digest: str
    local_access_a_digest: str
    local_access_b_digest: str
    joint_workspace_digest: str
    local_support_a: tuple[int, ...]
    local_support_b_mapped: tuple[int, ...]
    shared_support: tuple[int, ...]
    shared_coefficients: tuple[float, ...]
    support_capacity: int
    support_agreement_a: float
    support_agreement_b: float
    reportable_to_a: bool
    reportable_to_b: bool
    bidirectional: bool
    planner_use_authorized: bool
    provenance_status: str
    shared_state_digest: str
    discovery_receipt_digest: str
    uses_evaluator_labels: bool
    digest: str


def validate_distributed_jspace_discovery_receipt(
    receipt: DistributedJSpaceDiscoveryReceipt,
) -> bool:
    if not isinstance(receipt, DistributedJSpaceDiscoveryReceipt):
        return False
    if receipt.schema != "rrct.v048.distributed_jspace_discovery.v1":
        return False
    if receipt.uses_evaluator_labels:
        return False
    integers = (
        receipt.calibration_samples,
        receipt.residual_dimension_a,
        receipt.residual_dimension_b,
        receipt.local_workspace_rank_a,
        receipt.local_workspace_rank_b,
        receipt.shared_rank,
        receipt.shared_frame_count,
        receipt.support_capacity,
        receipt.dynamic_support_count,
    )
    if any(isinstance(value, bool) or int(value) <= 0 for value in integers):
        return False
    if receipt.shared_rank > min(
        receipt.local_workspace_rank_a, receipt.local_workspace_rank_b
    ):
        return False
    if receipt.shared_frame_count != len(receipt.concept_map_b_to_a):
        return False
    if receipt.shared_frame_count != len(receipt.opposite_concept_map):
        return False
    if sorted(receipt.concept_map_b_to_a) != list(range(receipt.shared_frame_count)):
        return False
    if any(
        index < 0 or index >= receipt.shared_frame_count
        for index in receipt.opposite_concept_map
    ):
        return False
    if any(
        receipt.opposite_concept_map[receipt.opposite_concept_map[index]] != index
        for index in range(receipt.shared_frame_count)
    ):
        return False
    numeric = (
        receipt.minimum_canonical_correlation,
        receipt.cross_agent_alignment_r2,
        receipt.minimum_frame_alignment_cosine,
        receipt.mean_frame_alignment_cosine,
        receipt.support_exact_agreement_rate,
    )
    if not all(np.isfinite(value) for value in numeric):
        return False
    if receipt.minimum_canonical_correlation < 0.0:
        return False
    if receipt.cross_agent_alignment_r2 < 0.0:
        return False
    if not 0.0 <= receipt.minimum_frame_alignment_cosine <= 1.0:
        return False
    if not 0.0 <= receipt.mean_frame_alignment_cosine <= 1.0:
        return False
    if not 0.0 <= receipt.support_exact_agreement_rate <= 1.0:
        return False
    if not receipt.packet_certificates_valid:
        return False
    if not all(
        _valid_sha256(value)
        for value in (
            receipt.local_a_discovery_digest,
            receipt.local_b_discovery_digest,
            receipt.shared_atlas_discovery_digest,
            receipt.shared_frame_digest,
            receipt.digest,
        )
    ):
        return False
    return receipt.digest == _digest(_payload(receipt))


def validate_distributed_jspace_access_receipt(
    receipt: DistributedJSpaceAccessReceipt,
) -> bool:
    if not isinstance(receipt, DistributedJSpaceAccessReceipt):
        return False
    if receipt.schema != "rrct.v048.distributed_jspace_access.v1":
        return False
    if receipt.uses_evaluator_labels:
        return False
    if isinstance(receipt.time, bool) or int(receipt.time) < 0:
        return False
    if not receipt.episode_id:
        return False
    if not all(
        _valid_sha256(value)
        for value in (
            receipt.pair_lineage_digest,
            receipt.local_access_a_digest,
            receipt.local_access_b_digest,
            receipt.joint_workspace_digest,
            receipt.shared_state_digest,
            receipt.discovery_receipt_digest,
            receipt.digest,
        )
    ):
        return False
    if isinstance(receipt.support_capacity, bool) or receipt.support_capacity <= 0:
        return False
    if len(receipt.shared_support) > receipt.support_capacity:
        return False
    if len(receipt.shared_support) != len(receipt.shared_coefficients):
        return False
    if tuple(sorted(set(receipt.shared_support))) != tuple(sorted(receipt.shared_support)):
        return False
    if any(value < 0.0 or not np.isfinite(value) for value in receipt.shared_coefficients):
        return False
    if not 0.0 <= receipt.support_agreement_a <= 1.0:
        return False
    if not 0.0 <= receipt.support_agreement_b <= 1.0:
        return False
    return receipt.digest == _digest(_payload(receipt))


class DistributedSparseJSpace:
    """Two local sparse workspaces aligned into one distributed J-space chart."""

    def __init__(
        self,
        *,
        workspace_a: JacobianSparseWorkspace,
        workspace_b: JacobianSparseWorkspace,
        atlas: SharedWorkspaceAtlas,
        concept_map_b_to_a: Sequence[int],
        shared_frame: Any,
        opposite_concept_map: Sequence[int],
        discovery_receipt: DistributedJSpaceDiscoveryReceipt,
        config: DistributedJSpaceConfig,
    ) -> None:
        if not validate_distributed_jspace_discovery_receipt(discovery_receipt):
            raise ValueError("invalid distributed J-space discovery receipt")
        if not validate_jacobian_workspace_discovery_receipt(
            workspace_a.discovery_receipt
        ) or not validate_jacobian_workspace_discovery_receipt(
            workspace_b.discovery_receipt
        ):
            raise ValueError("local workspace receipts must validate")
        if not validate_shared_atlas_discovery_receipt(atlas.discovery_receipt):
            raise ValueError("shared atlas receipt must validate")
        self.workspace_a = workspace_a
        self.workspace_b = workspace_b
        self.atlas = atlas
        self.concept_map_b_to_a = tuple(int(value) for value in concept_map_b_to_a)
        self.shared_frame = _readonly(shared_frame, ndim=2)
        self.opposite_concept_map = tuple(int(value) for value in opposite_concept_map)
        self.discovery_receipt = discovery_receipt
        self.config = config
        if self.shared_frame.shape != (
            discovery_receipt.shared_frame_count,
            discovery_receipt.shared_rank,
        ):
            raise ValueError("shared frame shape mismatch")
        self._frame_pinv = np.linalg.pinv(self.shared_frame.T)

    @property
    def shared_rank(self) -> int:
        return int(self.discovery_receipt.shared_rank)

    @property
    def concept_count(self) -> int:
        return int(self.discovery_receipt.shared_frame_count)

    def map_support_b(self, support: Sequence[int]) -> tuple[int, ...]:
        return tuple(sorted(self.concept_map_b_to_a[int(index)] for index in support))

    def shared_scores(self, state_a: Any, state_b: Any) -> np.ndarray:
        shared = self.atlas.shared_state(state_a, state_b)
        return np.asarray(self.shared_frame @ shared, dtype=np.float64)

    def sparse_content(
        self, state_a: Any, state_b: Any
    ) -> tuple[tuple[int, ...], tuple[float, ...]]:
        scores = self.shared_scores(state_a, state_b)
        order = np.argsort(scores)[::-1]
        support = [int(index) for index in order if scores[index] > 0.0][
            : self.config.support_capacity
        ]
        if not support:
            support = [int(order[0])]
        coefficients = [float(max(scores[index], 0.0)) for index in support]
        order_pairs = sorted(zip(support, coefficients))
        return (
            tuple(index for index, _ in order_pairs),
            tuple(value for _, value in order_pairs),
        )

    def shared_state_from_support(
        self, support: Sequence[int], coefficients: Sequence[float]
    ) -> np.ndarray:
        if len(support) != len(coefficients):
            raise ValueError("support and coefficients must have equal length")
        values = np.zeros(self.concept_count, dtype=np.float64)
        for index, coefficient in zip(support, coefficients):
            index = int(index)
            if not 0 <= index < self.concept_count:
                raise ValueError("support index out of range")
            if not np.isfinite(coefficient) or float(coefficient) < 0.0:
                raise ValueError("coefficients must be finite and nonnegative")
            values[index] += float(coefficient)
        return np.asarray(self.shared_frame.T @ values, dtype=np.float64)

    def swap_shared_concept(
        self,
        state_a: Any,
        state_b: Any,
        source: int,
        target: int,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        source = int(source)
        target = int(target)
        if source == target:
            shared = self.atlas.shared_state(state_a, state_b)
            return (
                np.asarray(state_a, dtype=np.float64).copy(),
                np.asarray(state_b, dtype=np.float64).copy(),
                shared,
            )
        if not 0 <= source < self.concept_count or not 0 <= target < self.concept_count:
            raise ValueError("source and target must be valid concept indices")
        shared = self.atlas.shared_state(state_a, state_b)
        coefficients = np.maximum(self.shared_frame @ shared, 0.0)
        magnitude = float(max(coefficients[source], 0.0))
        if magnitude <= 1e-10:
            magnitude = 1.0
        coefficients[source] = 0.0
        coefficients[target] += magnitude
        patched = np.asarray(self.shared_frame.T @ coefficients, dtype=np.float64)
        return (
            self.atlas.write_a(state_a, patched),
            self.atlas.write_b(state_b, patched),
            patched,
        )

    def ablate(self, state_a: Any, state_b: Any) -> tuple[np.ndarray, np.ndarray]:
        return self.atlas.ablate_a(state_a), self.atlas.ablate_b(state_b)

    @staticmethod
    def _agreement(left: Sequence[int], right: Sequence[int]) -> float:
        a = set(int(value) for value in left)
        b = set(int(value) for value in right)
        if not a and not b:
            return 1.0
        return float(len(a & b) / max(len(a | b), 1))

    def access(
        self,
        *,
        time: int,
        episode_id: str,
        pair_lineage_digest: str,
        state_a: Any,
        state_b: Any,
        local_access_a: WorkspaceAccessReceipt,
        local_access_b: WorkspaceAccessReceipt,
        joint_workspace: JointWorkspaceReceipt,
    ) -> DistributedJSpaceAccessReceipt:
        if not validate_workspace_access_receipt(local_access_a) or not validate_workspace_access_receipt(
            local_access_b
        ):
            raise ValueError("local workspace access receipts must validate")
        if not validate_joint_workspace_receipt(joint_workspace):
            raise ValueError("joint workspace receipt must validate")
        if not _valid_sha256(pair_lineage_digest):
            raise ValueError("pair lineage digest must be SHA-256")
        if pair_lineage_digest != joint_workspace.pair_lineage_digest:
            raise ValueError("joint workspace belongs to another pair")
        support_a = tuple(sorted(int(value) for value in local_access_a.active_support))
        support_b = self.map_support_b(local_access_b.active_support)
        shared_support, coefficients = self.sparse_content(state_a, state_b)
        payload = {
            "schema": "rrct.v048.distributed_jspace_access.v1",
            "time": int(time),
            "episode_id": str(episode_id),
            "pair_lineage_digest": str(pair_lineage_digest),
            "local_access_a_digest": local_access_a.digest,
            "local_access_b_digest": local_access_b.digest,
            "joint_workspace_digest": joint_workspace.digest,
            "local_support_a": support_a,
            "local_support_b_mapped": support_b,
            "shared_support": shared_support,
            "shared_coefficients": coefficients,
            "support_capacity": int(self.config.support_capacity),
            "support_agreement_a": self._agreement(support_a, shared_support),
            "support_agreement_b": self._agreement(support_b, shared_support),
            "reportable_to_a": bool(local_access_a.workspace_enabled),
            "reportable_to_b": bool(local_access_b.workspace_enabled),
            "bidirectional": bool(joint_workspace.bidirectional),
            "planner_use_authorized": bool(joint_workspace.planner_use_authorized),
            "provenance_status": str(joint_workspace.provenance_status),
            "shared_state_digest": _array_digest(self.atlas.shared_state(state_a, state_b)),
            "discovery_receipt_digest": self.discovery_receipt.digest,
            "uses_evaluator_labels": False,
        }
        receipt = DistributedJSpaceAccessReceipt(**payload, digest=_digest(payload))
        if not validate_distributed_jspace_access_receipt(receipt):
            raise RuntimeError("invalid distributed J-space access receipt")
        return receipt


def discover_distributed_jspace(
    *,
    agent_a_states: Any,
    agent_b_states: Any,
    workspace_a: JacobianSparseWorkspace,
    workspace_b: JacobianSparseWorkspace,
    config: DistributedJSpaceConfig | None = None,
) -> DistributedSparseJSpace:
    """Discover a shared sparse frame from two local Jacobian workspaces."""

    cfg = config or DistributedJSpaceConfig()
    states_a = np.asarray(agent_a_states, dtype=np.float64)
    states_b = np.asarray(agent_b_states, dtype=np.float64)
    if states_a.ndim != 2 or states_b.ndim != 2 or states_a.shape[0] != states_b.shape[0]:
        raise ValueError("paired calibration states must have equal row counts")
    atlas = discover_shared_workspace(
        states_a,
        states_b,
        workspace_a,
        workspace_b,
        cfg.shared_workspace,
    )

    frame_a = np.asarray(
        (workspace_a.frame_vectors.T @ atlas.basis_a) / atlas.scale_a,
        dtype=np.float64,
    )
    frame_b = np.asarray(
        ((workspace_b.frame_vectors.T @ atlas.basis_b) / atlas.scale_b) @ atlas.b_to_a,
        dtype=np.float64,
    )
    if frame_a.shape[0] != frame_b.shape[0]:
        raise ValueError("local J-spaces must expose the same number of frame directions")
    similarity = _cosine_rows(frame_a, frame_b)
    concept_map = _greedy_positive_matching(similarity)
    aligned_b = np.empty_like(frame_b)
    match_scores = []
    for local_b, canonical_a in enumerate(concept_map):
        aligned_b[canonical_a] = frame_b[local_b]
        match_scores.append(float(similarity[canonical_a, local_b]))
    shared_frame = frame_a + aligned_b
    norms = np.linalg.norm(shared_frame, axis=1, keepdims=True)
    shared_frame = shared_frame / np.maximum(norms, 1e-24)

    frame_similarity = _cosine_rows(shared_frame, shared_frame)
    np.fill_diagonal(frame_similarity, np.inf)
    opposite = tuple(int(index) for index in np.argmin(frame_similarity, axis=1))
    if any(opposite[opposite[index]] != index for index in range(len(opposite))):
        raise RuntimeError("shared frame does not form reciprocal opposite pairs")

    support_agreements = []
    support_patterns: set[tuple[int, ...]] = set()
    for state_a, state_b in zip(states_a, states_b):
        support_a, _ = workspace_a.sparse_content(state_a)
        support_b_raw, _ = workspace_b.sparse_content(state_b)
        support_b = tuple(sorted(concept_map[index] for index in support_b_raw))
        shared = atlas.shared_state(state_a, state_b)
        scores = shared_frame @ shared
        order = np.argsort(scores)[::-1]
        support_shared = tuple(
            sorted(
                int(index)
                for index in order
                if scores[index] > 0.0
            )[: cfg.support_capacity]
        )
        if not support_shared:
            support_shared = (int(order[0]),)
        set_a = set(support_a)
        set_b = set(support_b)
        set_shared = set(support_shared)
        agreement_a = len(set_a & set_shared) / max(len(set_a | set_shared), 1)
        agreement_b = len(set_b & set_shared) / max(len(set_b | set_shared), 1)
        support_agreements.append(float(min(agreement_a, agreement_b)))
        support_patterns.add(support_shared)

    receipt_payload = {
        "schema": "rrct.v048.distributed_jspace_discovery.v1",
        "calibration_samples": int(states_a.shape[0]),
        "residual_dimension_a": int(states_a.shape[1]),
        "residual_dimension_b": int(states_b.shape[1]),
        "local_workspace_rank_a": int(workspace_a.discovery_receipt.workspace_rank),
        "local_workspace_rank_b": int(workspace_b.discovery_receipt.workspace_rank),
        "shared_rank": int(atlas.shared_rank),
        "shared_frame_count": int(shared_frame.shape[0]),
        "support_capacity": int(cfg.support_capacity),
        "minimum_canonical_correlation": float(
            min(atlas.discovery_receipt.canonical_correlations)
        ),
        "cross_agent_alignment_r2": float(
            atlas.discovery_receipt.cross_agent_alignment_r2
        ),
        "minimum_frame_alignment_cosine": float(min(match_scores)),
        "mean_frame_alignment_cosine": float(np.mean(match_scores)),
        "support_exact_agreement_rate": float(
            np.mean(np.asarray(support_agreements) >= cfg.minimum_support_agreement)
        ),
        "dynamic_support_count": int(len(support_patterns)),
        "local_a_discovery_digest": workspace_a.discovery_receipt.digest,
        "local_b_discovery_digest": workspace_b.discovery_receipt.digest,
        "shared_atlas_discovery_digest": atlas.discovery_receipt.digest,
        "shared_frame_digest": _array_digest(shared_frame),
        "concept_map_b_to_a": tuple(int(value) for value in concept_map),
        "opposite_concept_map": opposite,
        "packet_certificates_valid": bool(
            workspace_a.discovery_receipt.packet_certificate_valid
            and workspace_a.discovery_receipt.hilbert_certificate_valid
            and workspace_a.discovery_receipt.atlas_certificate_valid
            and workspace_b.discovery_receipt.packet_certificate_valid
            and workspace_b.discovery_receipt.hilbert_certificate_valid
            and workspace_b.discovery_receipt.atlas_certificate_valid
            and atlas.discovery_receipt.agent_a_packet_certificate_valid
            and atlas.discovery_receipt.agent_b_packet_certificate_valid
            and atlas.discovery_receipt.agent_a_hilbert_certificate_valid
            and atlas.discovery_receipt.agent_b_hilbert_certificate_valid
            and atlas.discovery_receipt.agent_a_atlas_certificate_valid
            and atlas.discovery_receipt.agent_b_atlas_certificate_valid
        ),
        "uses_evaluator_labels": False,
    }
    receipt = DistributedJSpaceDiscoveryReceipt(
        **receipt_payload,
        digest=_digest(receipt_payload),
    )
    if not validate_distributed_jspace_discovery_receipt(receipt):
        raise RuntimeError("invalid distributed J-space discovery receipt")
    return DistributedSparseJSpace(
        workspace_a=workspace_a,
        workspace_b=workspace_b,
        atlas=atlas,
        concept_map_b_to_a=concept_map,
        shared_frame=shared_frame,
        opposite_concept_map=opposite,
        discovery_receipt=receipt,
        config=cfg,
    )


def validate_distributed_jspace_chain(
    *,
    discovery: DistributedJSpaceDiscoveryReceipt,
    atlas_receipt: Any,
    local_access_a: WorkspaceAccessReceipt,
    local_access_b: WorkspaceAccessReceipt,
    message_a: PairMessageReceipt,
    message_b: PairMessageReceipt,
    joint_workspace: JointWorkspaceReceipt,
    distributed_access: DistributedJSpaceAccessReceipt,
    plan: JointPlanningReceipt,
    outcome: JointOutcomeReceipt,
) -> bool:
    if not validate_distributed_jspace_discovery_receipt(discovery):
        return False
    if not validate_shared_atlas_discovery_receipt(atlas_receipt):
        return False
    if not validate_workspace_access_receipt(local_access_a) or not validate_workspace_access_receipt(
        local_access_b
    ):
        return False
    if not validate_distributed_jspace_access_receipt(distributed_access):
        return False
    if distributed_access.discovery_receipt_digest != discovery.digest:
        return False
    if distributed_access.local_access_a_digest != local_access_a.digest:
        return False
    if distributed_access.local_access_b_digest != local_access_b.digest:
        return False
    if distributed_access.joint_workspace_digest != joint_workspace.digest:
        return False
    if discovery.shared_atlas_discovery_digest != atlas_receipt.digest:
        return False
    if not validate_distributed_workspace_chain(
        atlas=atlas_receipt,
        message_a=message_a,
        message_b=message_b,
        workspace=joint_workspace,
        plan=plan,
        outcome=outcome,
    ):
        return False
    if distributed_access.pair_lineage_digest != joint_workspace.pair_lineage_digest:
        return False
    if distributed_access.episode_id != joint_workspace.episode_id:
        return False
    return True


__all__ = [
    "DistributedJSpaceAccessReceipt",
    "DistributedJSpaceConfig",
    "DistributedJSpaceDiscoveryReceipt",
    "DistributedSparseJSpace",
    "discover_distributed_jspace",
    "validate_distributed_jspace_access_receipt",
    "validate_distributed_jspace_chain",
    "validate_distributed_jspace_discovery_receipt",
]
