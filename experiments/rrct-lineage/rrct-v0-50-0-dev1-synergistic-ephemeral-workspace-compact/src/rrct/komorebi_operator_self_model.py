"""RRCT v0.45 Komorebi operator self-model integration.

This module uses the public finite APIs of ``komorebi-math==1.0.0b4`` to make
RRCT's transformational self-model explicit in projector, transfer-block,
residual-packet, multiresolution, Bayesian, and proof-path form.

The integration is deliberately bounded.  It does not claim that Komorebi
operators are necessary for every self-model or that the synthetic benchmark
establishes consciousness.  It provides an executable comparison against the
v0.44 bespoke transport controller.
"""
from __future__ import annotations

import copy
import hashlib
import importlib
import json
import sys
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any, Literal, Mapping, Sequence

import numpy as np

from .transformational_self_continuity import (
    ContinuityAssessmentReceipt,
    LineageAnchorReceipt,
    SuccessorEvidenceReceipt,
    TransformInterventionMode,
    TransformationalAdjudicationReceipt,
    TransformationalOutcomeReceipt,
    TransformationalPlanningReceipt,
    TransformationalSelfContinuityController,
    SuccessorTaskReceipt,
    TransformationalTransitionReceipt,
    _assessment_payload,
    _digest,
    _memory_transport,
    _orthogonal_transport,
    validate_continuity_assessment_receipt,
    validate_successor_evidence_receipt,
    validate_transformational_receipt_chain,
)

KOMOREBI_VERSION = "1.0.0b4"
KOMOREBI_WHEEL = "komorebi_math-1.0.0b4-py3-none-any.whl"
KOMOREBI_WHEEL_SHA256 = "7d51e3040aea84f6d540936c2427376205ef8660d44b6841c2848c542e628adb"

Relation = Literal["continuation", "replacement", "unresolved"]
ChangeClass = Literal["self_change", "world_change", "mixed_change", "no_change"]


def _ensure_komorebi() -> Any:
    """Load the exact vendored Komorebi wheel and verify its identity."""

    try:
        module = importlib.import_module("komorebi_math")
    except ModuleNotFoundError:
        wheel = Path(__file__).resolve().parent / "_vendor" / KOMOREBI_WHEEL
        if not wheel.is_file():
            raise RuntimeError("the vendored Komorebi Math wheel is missing")
        actual = hashlib.sha256(wheel.read_bytes()).hexdigest()
        if actual != KOMOREBI_WHEEL_SHA256:
            raise RuntimeError("the vendored Komorebi Math wheel failed SHA-256 verification")
        sys.path.insert(0, str(wheel))
        module = importlib.import_module("komorebi_math")
    version = str(getattr(module, "__version__", ""))
    if version != KOMOREBI_VERSION:
        raise RuntimeError(
            f"RRCT v0.45 requires komorebi-math {KOMOREBI_VERSION}, found {version!r}"
        )
    return module


_ensure_komorebi()
from komorebi_math.algorithms.low_rank import recompress_core  # noqa: E402
from komorebi_math.coordinates.analysis_synthesis import (  # noqa: E402
    AnalysisSynthesisSystem,
)
from komorebi_math.core.packets import PacketSystem  # noqa: E402
from komorebi_math.dynamics.bayes import BayesianUpdate  # noqa: E402


def _readonly(value: Any, *, ndim: int | None = None) -> np.ndarray:
    array = np.asarray(value, dtype=np.float64)
    if ndim is not None and array.ndim != ndim:
        raise ValueError(f"expected {ndim}-D array")
    if not np.all(np.isfinite(array)):
        raise ValueError("array must be finite")
    result = np.array(array, dtype=np.float64, copy=True)
    result.setflags(write=False)
    return result


def _valid_sha256(value: Any) -> bool:
    return bool(
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _relative_residual(actual: Any, expected: Any) -> float:
    left = np.asarray(actual)
    right = np.asarray(expected)
    if left.shape != right.shape:
        return 1.0
    return float(np.linalg.norm(left - right) / (np.linalg.norm(right) + 1e-12))


def _quality(residual: float, scale: float) -> float:
    if residual < 0.0 or not np.isfinite(residual):
        return 0.0
    return float(np.exp(-residual / max(float(scale), 1e-12)))


def _projector_rank(projector: np.ndarray, tolerance: float) -> int:
    eigenvalues = np.linalg.eigvalsh(0.5 * (projector + projector.T))
    return int(np.count_nonzero(eigenvalues > max(0.5, tolerance)))


def _projector_basis(projector: Any, tolerance: float) -> tuple[np.ndarray, int]:
    """Return an orthogonal basis whose first columns span ``projector``."""

    matrix = np.asarray(projector, dtype=np.float64)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("projector must be square")
    symmetric = 0.5 * (matrix + matrix.T)
    values, vectors = np.linalg.eigh(symmetric)
    order = np.argsort(values)[::-1]
    values = values[order]
    vectors = vectors[:, order]
    rank = int(np.count_nonzero(values > max(0.5, tolerance)))
    if rank <= 0 or rank >= matrix.shape[0]:
        raise ValueError("self projector must define a nontrivial proper subspace")
    return np.asarray(vectors, dtype=np.float64), rank


def _packet_system_from_projector(
    projector: Any,
    *,
    tolerance: float,
) -> tuple[PacketSystem, AnalysisSynthesisSystem, np.ndarray, np.ndarray, int]:
    """Create certified ``self`` and ``world`` packets from one projector."""

    basis, rank = _projector_basis(projector, tolerance)
    atlas = AnalysisSynthesisSystem.from_invertible(
        basis.T,
        source="rrct-state",
        coordinates="komorebi-self-world",
        tolerance=tolerance,
        theorem="RRCT-KM-01",
    )
    groups = (tuple(range(rank)), tuple(range(rank, basis.shape[0])))
    self_component, world_component = atlas.components(groups)
    packet_system = PacketSystem(
        [self_component, world_component],
        names=("self", "world"),
        tolerance=tolerance,
    )
    packet_system.certificate().require()
    packet_system.hilbert_certificate().require()
    return packet_system, atlas, self_component, world_component, rank


def _effect_packet_energies(
    residual: np.ndarray,
    source_self: np.ndarray,
    source_world: np.ndarray,
    sensory_self: np.ndarray,
    sensory_world: np.ndarray,
) -> dict[str, float]:
    blocks = {
        "self_from_self": source_self @ residual @ sensory_self,
        "self_from_world": source_self @ residual @ sensory_world,
        "world_from_self": source_world @ residual @ sensory_self,
        "world_from_world": source_world @ residual @ sensory_world,
    }
    squared = {name: float(np.linalg.norm(value) ** 2) for name, value in blocks.items()}
    total = float(sum(squared.values()))
    denominator = total + 1e-24
    return {
        **{f"{name}_energy": value for name, value in squared.items()},
        "total_energy": total,
        "self_packet_fraction": float(
            (squared["self_from_self"] + squared["self_from_world"]) / denominator
        ),
        "world_packet_fraction": float(
            (squared["world_from_self"] + squared["world_from_world"]) / denominator
        ),
        "off_block_fraction": float(
            (squared["self_from_world"] + squared["world_from_self"]) / denominator
        ),
    }


@dataclass(frozen=True)
class KomorebiOperatorConfig:
    tolerance: float = 1e-9
    projector_residual_scale: float = 0.18
    effect_residual_scale: float = 0.18
    memory_residual_scale: float = 0.22
    off_block_scale: float = 0.35
    memory_rank_budget: int = 4
    fusion_weight: float = 0.50
    accept_threshold: float = 0.45
    reject_threshold: float = 0.06
    refinement_low: float = 0.06
    refinement_high: float = 0.90

    def __post_init__(self) -> None:
        numeric = (
            self.tolerance,
            self.projector_residual_scale,
            self.effect_residual_scale,
            self.memory_residual_scale,
            self.off_block_scale,
        )
        if not all(np.isfinite(value) and value > 0.0 for value in numeric):
            raise ValueError("Komorebi residual scales and tolerance must be positive")
        if isinstance(self.memory_rank_budget, bool) or self.memory_rank_budget <= 0:
            raise ValueError("memory_rank_budget must be positive")
        if not 0.0 <= self.fusion_weight <= 1.0:
            raise ValueError("fusion_weight must lie in [0, 1]")
        if not 0.0 < self.reject_threshold < self.accept_threshold < 1.0:
            raise ValueError("operator thresholds must satisfy 0 < reject < accept < 1")
        if not 0.0 <= self.refinement_low < self.refinement_high <= 1.0:
            raise ValueError("operator refinement interval is invalid")


@dataclass(frozen=True)
class KomorebiProjectorDiscoveryReceipt:
    schema: str
    dimension: int
    controllable_rank: int
    controllability_singular_values: tuple[float, ...]
    packet_certificate_valid: bool
    hilbert_certificate_valid: bool
    atlas_certificate_valid: bool
    projector_reconstruction_residual: float
    uses_evaluator_labels: bool
    digest: str


@dataclass(frozen=True)
class KomorebiOperatorAssessmentReceipt:
    schema: str
    sequence_id: int
    time: int
    candidate_id: str
    intervention_mode: TransformInterventionMode
    predecessor_lineage_digest: str
    evidence_digest: str
    base_assessment_digest: str
    integrated_assessment_digest: str
    komorebi_version: str
    komorebi_wheel_sha256: str
    source_packet_certificate_valid: bool
    sensory_packet_certificate_valid: bool
    source_atlas_certificate_valid: bool
    sensory_atlas_certificate_valid: bool
    source_packet_transport_residual: float
    sensory_packet_transport_residual: float
    effect_transport_residual: float
    effect_off_block_fraction: float
    self_packet_residual_fraction: float
    world_packet_residual_fraction: float
    memory_recompression_rank: int
    memory_recompression_certificate_valid: bool
    memory_recompression_spectral_error: float
    memory_recompression_frobenius_error: float
    memory_full_transport_residual: float
    memory_reconstruction_residual: float
    causal_packet_quality: float
    memory_packet_quality: float
    operator_continuity_score: float
    base_continuity_score: float
    fused_continuity_score: float
    posterior_labels: tuple[Relation, ...]
    posterior: tuple[float, ...]
    inferred_change_class: ChangeClass
    evidence_sufficient: bool
    refinement_requested: bool
    provisional_relation: Literal["accept", "reject", "unresolved"]
    future_outcome_unknown: bool
    uses_evaluator_labels: bool
    digest: str


def _payload(receipt: Any) -> dict[str, Any]:
    value = asdict(receipt)
    value.pop("digest", None)
    return value


def validate_komorebi_projector_discovery_receipt(
    receipt: KomorebiProjectorDiscoveryReceipt,
) -> bool:
    if not isinstance(receipt, KomorebiProjectorDiscoveryReceipt):
        return False
    if receipt.schema != "rrct.v045.komorebi_projector_discovery.v1":
        return False
    if receipt.dimension <= 1 or not 0 < receipt.controllable_rank < receipt.dimension:
        return False
    if len(receipt.controllability_singular_values) != receipt.dimension:
        return False
    if not all(np.isfinite(value) and value >= 0.0 for value in receipt.controllability_singular_values):
        return False
    if not (
        receipt.packet_certificate_valid
        and receipt.hilbert_certificate_valid
        and receipt.atlas_certificate_valid
    ):
        return False
    if receipt.projector_reconstruction_residual < 0.0 or not np.isfinite(
        receipt.projector_reconstruction_residual
    ):
        return False
    if receipt.uses_evaluator_labels:
        return False
    return bool(_valid_sha256(receipt.digest) and receipt.digest == _digest(_payload(receipt)))


def validate_komorebi_operator_assessment_receipt(
    receipt: KomorebiOperatorAssessmentReceipt,
) -> bool:
    if not isinstance(receipt, KomorebiOperatorAssessmentReceipt):
        return False
    if receipt.schema != "rrct.v045.komorebi_operator_assessment.v1":
        return False
    if receipt.sequence_id < 0 or receipt.time < 0 or not receipt.candidate_id:
        return False
    if not all(
        _valid_sha256(value)
        for value in (
            receipt.predecessor_lineage_digest,
            receipt.evidence_digest,
            receipt.base_assessment_digest,
            receipt.integrated_assessment_digest,
            receipt.komorebi_wheel_sha256,
            receipt.digest,
        )
    ):
        return False
    if receipt.komorebi_version != KOMOREBI_VERSION:
        return False
    if receipt.komorebi_wheel_sha256 != KOMOREBI_WHEEL_SHA256:
        return False
    if not all(
        (
            receipt.source_packet_certificate_valid,
            receipt.sensory_packet_certificate_valid,
            receipt.source_atlas_certificate_valid,
            receipt.sensory_atlas_certificate_valid,
            receipt.memory_recompression_certificate_valid,
        )
    ):
        return False
    numeric = (
        receipt.source_packet_transport_residual,
        receipt.sensory_packet_transport_residual,
        receipt.effect_transport_residual,
        receipt.effect_off_block_fraction,
        receipt.self_packet_residual_fraction,
        receipt.world_packet_residual_fraction,
        receipt.memory_recompression_spectral_error,
        receipt.memory_recompression_frobenius_error,
        receipt.memory_full_transport_residual,
        receipt.memory_reconstruction_residual,
        receipt.causal_packet_quality,
        receipt.memory_packet_quality,
        receipt.operator_continuity_score,
        receipt.base_continuity_score,
        receipt.fused_continuity_score,
    )
    if not all(np.isfinite(value) and value >= 0.0 for value in numeric):
        return False
    if any(
        not 0.0 <= value <= 1.0
        for value in (
            receipt.effect_off_block_fraction,
            receipt.self_packet_residual_fraction,
            receipt.world_packet_residual_fraction,
            receipt.causal_packet_quality,
            receipt.memory_packet_quality,
            receipt.operator_continuity_score,
            receipt.base_continuity_score,
            receipt.fused_continuity_score,
        )
    ):
        return False
    if receipt.memory_recompression_rank < 0:
        return False
    if receipt.posterior_labels != ("continuation", "replacement", "unresolved"):
        return False
    if len(receipt.posterior) != 3 or not np.isclose(sum(receipt.posterior), 1.0, atol=1e-10):
        return False
    if any(not np.isfinite(value) or value < 0.0 for value in receipt.posterior):
        return False
    if receipt.inferred_change_class not in {
        "self_change",
        "world_change",
        "mixed_change",
        "no_change",
    }:
        return False
    if receipt.provisional_relation not in {"accept", "reject", "unresolved"}:
        return False
    if not receipt.future_outcome_unknown or receipt.uses_evaluator_labels:
        return False
    return receipt.digest == _digest(_payload(receipt))


def discover_controllable_packets(
    dynamics: Any,
    actuation: Any,
    *,
    tolerance: float = 1e-9,
) -> tuple[np.ndarray, np.ndarray, KomorebiProjectorDiscoveryReceipt]:
    """Discover a causal self packet from controllability, without identity labels.

    The self packet is the numerical range of ``[B, AB, ..., A^(n-1)B]``.
    This is a causal-control definition, not an evaluator-provided variable mask.
    """

    a = np.asarray(dynamics, dtype=np.float64)
    b = np.asarray(actuation, dtype=np.float64)
    if a.ndim != 2 or a.shape[0] != a.shape[1]:
        raise ValueError("dynamics must be square")
    if b.ndim == 1:
        b = b[:, None]
    if b.ndim != 2 or b.shape[0] != a.shape[0]:
        raise ValueError("actuation has incompatible shape")
    blocks = []
    current = np.array(b, copy=True)
    for _ in range(a.shape[0]):
        blocks.append(current)
        current = a @ current
    controllability = np.concatenate(blocks, axis=1)
    u, singular_values, _ = np.linalg.svd(controllability, full_matrices=True)
    padded = np.zeros(a.shape[0], dtype=np.float64)
    padded[: singular_values.size] = singular_values
    cutoff = max(float(tolerance), float(padded[0]) * float(tolerance))
    rank = int(np.count_nonzero(padded > cutoff))
    if rank <= 0 or rank >= a.shape[0]:
        raise ValueError("controllability must reveal a nontrivial proper self subspace")
    self_projector = u[:, :rank] @ u[:, :rank].T
    world_projector = np.eye(a.shape[0]) - self_projector
    packets, atlas, reconstructed_self, _, _ = _packet_system_from_projector(
        self_projector, tolerance=tolerance
    )
    payload = {
        "schema": "rrct.v045.komorebi_projector_discovery.v1",
        "dimension": int(a.shape[0]),
        "controllable_rank": rank,
        "controllability_singular_values": tuple(float(value) for value in padded),
        "packet_certificate_valid": bool(packets.certificate().valid),
        "hilbert_certificate_valid": bool(packets.hilbert_certificate().valid),
        "atlas_certificate_valid": bool(atlas.certificate().valid),
        "projector_reconstruction_residual": _relative_residual(
            reconstructed_self, self_projector
        ),
        "uses_evaluator_labels": False,
    }
    receipt = KomorebiProjectorDiscoveryReceipt(**payload, digest=_digest(payload))
    if not validate_komorebi_projector_discovery_receipt(receipt):
        raise RuntimeError("invalid Komorebi projector-discovery receipt")
    return _readonly(self_projector, ndim=2), _readonly(world_projector, ndim=2), receipt


class KomorebiOperatorBridge:
    """Build a certified operator assessment for one RRCT successor candidate."""

    def __init__(self, config: KomorebiOperatorConfig | None = None) -> None:
        self.config = config or KomorebiOperatorConfig()
        if not isinstance(self.config, KomorebiOperatorConfig):
            raise TypeError("config must be KomorebiOperatorConfig")

    def _metrics(
        self,
        root: LineageAnchorReceipt,
        evidence: SuccessorEvidenceReceipt,
        base: ContinuityAssessmentReceipt,
    ) -> dict[str, Any]:
        if not validate_successor_evidence_receipt(evidence):
            raise ValueError("successor evidence is invalid")
        source_packets, source_atlas, source_self, source_world, _ = (
            _packet_system_from_projector(
                root.source_projector, tolerance=self.config.tolerance
            )
        )
        sensory_packets, sensory_atlas, sensory_self, sensory_world, _ = (
            _packet_system_from_projector(
                root.sensory_projector, tolerance=self.config.tolerance
            )
        )
        source_transport, _, _ = _orthogonal_transport(
            evidence.source_anchor_before, evidence.source_anchor_after
        )
        sensory_transport, _, _ = _orthogonal_transport(
            evidence.sensory_anchor_before, evidence.sensory_anchor_after
        )
        transported_source = source_packets.transport(source_transport.T)
        transported_sensory = sensory_packets.transport(sensory_transport.T)
        candidate_source, _, candidate_source_self, candidate_source_world, _ = (
            _packet_system_from_projector(
                evidence.candidate_source_projector,
                tolerance=self.config.tolerance,
            )
        )
        candidate_sensory, _, candidate_sensory_self, candidate_sensory_world, _ = (
            _packet_system_from_projector(
                evidence.candidate_sensory_projector,
                tolerance=self.config.tolerance,
            )
        )
        source_packet_residual = float(
            np.mean(
                [
                    _relative_residual(left, right)
                    for left, right in zip(
                        transported_source.projectors,
                        candidate_source.projectors,
                        strict=True,
                    )
                ]
            )
        )
        sensory_packet_residual = float(
            np.mean(
                [
                    _relative_residual(left, right)
                    for left, right in zip(
                        transported_sensory.projectors,
                        candidate_sensory.projectors,
                        strict=True,
                    )
                ]
            )
        )
        expected_effect = (
            source_transport.T
            @ np.asarray(root.effect_operator)
            @ sensory_transport
        )
        effect_residual_matrix = (
            np.asarray(evidence.candidate_effect_operator) - expected_effect
        )
        effect_residual = _relative_residual(
            evidence.candidate_effect_operator, expected_effect
        )
        energies = _effect_packet_energies(
            effect_residual_matrix,
            candidate_source_self,
            candidate_source_world,
            candidate_sensory_self,
            candidate_sensory_world,
        )

        memory_transport, full_memory_residual, _, _ = _memory_transport(
            evidence.memory_anchor_before, evidence.memory_anchor_after
        )
        rank_budget = min(
            int(self.config.memory_rank_budget),
            memory_transport.shape[0],
            memory_transport.shape[1],
        )
        recompressed = recompress_core(
            np.eye(memory_transport.shape[0]),
            memory_transport,
            np.eye(memory_transport.shape[1]),
            rank_budget,
            tolerance=self.config.tolerance,
        )
        recompressed.certificate.require()
        compressed_transport = np.asarray(recompressed.materialize(), dtype=np.float64)
        memory_reconstruction = (
            np.asarray(evidence.memory_anchor_before) @ compressed_transport
        )
        memory_residual = _relative_residual(
            memory_reconstruction, evidence.memory_anchor_after
        )

        causal_residual = float(
            np.mean(
                [source_packet_residual, sensory_packet_residual, effect_residual]
            )
        )
        weighted_off_block = float(
            energies["off_block_fraction"] * min(1.0, effect_residual)
        )
        causal_quality = float(
            np.sqrt(
                _quality(causal_residual, self.config.effect_residual_scale)
                * _quality(weighted_off_block, self.config.off_block_scale)
            )
        )
        # The certified low-rank model measures resolution loss.  Continuity
        # itself is scored from the full held-out memory transport so that an
        # intentionally small compression budget is not confused with identity
        # failure.
        memory_quality = _quality(
            full_memory_residual, self.config.memory_residual_scale
        )
        operator_score = float(
            np.sqrt(max(causal_quality, 0.0) * max(memory_quality, 0.0))
            * (0.85 + 0.15 * float(base.commitment_quality))
        )
        operator_score = float(np.clip(operator_score, 0.0, 1.0))
        weight = float(self.config.fusion_weight)
        fused = float(
            np.exp(
                (1.0 - weight) * np.log(max(float(base.continuity_score), 1e-12))
                + weight * np.log(max(operator_score, 1e-12))
            )
        )
        fused = float(np.clip(fused, 0.0, 1.0))

        continuation_like = max(fused, 1e-9)
        replacement_like = max(1.0 - fused, 1e-9)
        unresolved_like = max(
            np.exp(-abs(fused - 0.25) / 0.20)
            * (1.0 if base.evidence_sufficient else 2.0),
            1e-9,
        )
        posterior = BayesianUpdate(
            [0.45, 0.45, 0.10],
            [continuation_like, replacement_like, unresolved_like],
        ).posterior

        self_fraction = float(energies["self_packet_fraction"])
        world_fraction = float(energies["world_packet_fraction"])
        magnitude = float(effect_residual)
        if magnitude <= max(0.05, 10.0 * self.config.tolerance):
            change_class: ChangeClass = "no_change"
        elif self_fraction >= 0.70:
            change_class = "self_change"
        elif world_fraction >= 0.70:
            change_class = "world_change"
        else:
            change_class = "mixed_change"

        evidence_sufficient = bool(
            base.evidence_sufficient
            and source_packets.certificate().valid
            and sensory_packets.certificate().valid
            and source_atlas.certificate().valid
            and sensory_atlas.certificate().valid
            and recompressed.certificate.valid
        )
        return {
            "source_packet_certificate_valid": bool(source_packets.certificate().valid),
            "sensory_packet_certificate_valid": bool(sensory_packets.certificate().valid),
            "source_atlas_certificate_valid": bool(source_atlas.certificate().valid),
            "sensory_atlas_certificate_valid": bool(sensory_atlas.certificate().valid),
            "source_packet_transport_residual": source_packet_residual,
            "sensory_packet_transport_residual": sensory_packet_residual,
            "effect_transport_residual": effect_residual,
            "effect_off_block_fraction": float(energies["off_block_fraction"]),
            "self_packet_residual_fraction": self_fraction,
            "world_packet_residual_fraction": world_fraction,
            "memory_recompression_rank": int(recompressed.retained_rank),
            "memory_recompression_certificate_valid": bool(recompressed.certificate.valid),
            "memory_recompression_spectral_error": float(recompressed.spectral_error),
            "memory_recompression_frobenius_error": float(recompressed.frobenius_error),
            "memory_full_transport_residual": float(full_memory_residual),
            "memory_reconstruction_residual": memory_residual,
            "causal_packet_quality": float(np.clip(causal_quality, 0.0, 1.0)),
            "memory_packet_quality": float(np.clip(memory_quality, 0.0, 1.0)),
            "operator_continuity_score": operator_score,
            "base_continuity_score": float(base.continuity_score),
            "fused_continuity_score": fused,
            "posterior_labels": ("continuation", "replacement", "unresolved"),
            "posterior": tuple(float(value) for value in posterior),
            "inferred_change_class": change_class,
            "evidence_sufficient": evidence_sufficient,
        }

    def assess(
        self,
        root: LineageAnchorReceipt,
        evidence: SuccessorEvidenceReceipt,
        base: ContinuityAssessmentReceipt,
        *,
        integrated: ContinuityAssessmentReceipt,
    ) -> KomorebiOperatorAssessmentReceipt:
        metrics = self._metrics(root, evidence, base)
        payload = {
            "schema": "rrct.v045.komorebi_operator_assessment.v1",
            "sequence_id": int(base.sequence_id),
            "time": int(base.time),
            "candidate_id": base.candidate_id,
            "intervention_mode": base.intervention_mode,
            "predecessor_lineage_digest": root.digest,
            "evidence_digest": evidence.digest,
            "base_assessment_digest": base.digest,
            "integrated_assessment_digest": integrated.digest,
            "komorebi_version": KOMOREBI_VERSION,
            "komorebi_wheel_sha256": KOMOREBI_WHEEL_SHA256,
            **metrics,
            "refinement_requested": bool(integrated.refinement_requested),
            "provisional_relation": integrated.provisional_relation,
            "future_outcome_unknown": True,
            "uses_evaluator_labels": False,
        }
        receipt = KomorebiOperatorAssessmentReceipt(
            **payload, digest=_digest(payload)
        )
        if not validate_komorebi_operator_assessment_receipt(receipt):
            raise RuntimeError("invalid Komorebi operator assessment receipt")
        return receipt


class KomorebiTransformationalSelfContinuityController(
    TransformationalSelfContinuityController
):
    """v0.44 controller whose continuity score is fused with Komorebi packets."""

    def __init__(
        self,
        root: LineageAnchorReceipt,
        config: Any | None = None,
        *,
        operator_config: KomorebiOperatorConfig | None = None,
    ) -> None:
        super().__init__(root, config)
        self.operator_bridge = KomorebiOperatorBridge(operator_config)
        self._komorebi_receipts: dict[str, KomorebiOperatorAssessmentReceipt] = {}

    @property
    def komorebi_operator_receipts(
        self,
    ) -> tuple[KomorebiOperatorAssessmentReceipt, ...]:
        return tuple(
            copy.deepcopy(self._komorebi_receipts[key])
            for key in sorted(self._komorebi_receipts)
        )

    def operator_receipt_for_assessment(
        self, assessment_digest: str
    ) -> KomorebiOperatorAssessmentReceipt | None:
        value = self._komorebi_receipts.get(assessment_digest)
        return None if value is None else copy.deepcopy(value)

    def _assess(
        self,
        root: LineageAnchorReceipt,
        evidence: SuccessorEvidenceReceipt,
        *,
        sequence_id: int,
        intervention_mode: TransformInterventionMode,
        permit_refinement: bool,
    ) -> ContinuityAssessmentReceipt:
        base = super()._assess(
            root,
            evidence,
            sequence_id=sequence_id,
            intervention_mode=intervention_mode,
            permit_refinement=permit_refinement,
        )
        metrics = self.operator_bridge._metrics(root, evidence, base)

        if intervention_mode in {"snapshot_only", "causal_only", "memory_only", "joint_cut"}:
            fused_score = float(base.continuity_score)
            sufficient = bool(base.evidence_sufficient)
        else:
            fused_score = float(metrics["fused_continuity_score"])
            sufficient = bool(metrics["evidence_sufficient"])

        if sufficient and fused_score >= self.operator_bridge.config.accept_threshold:
            provisional: Literal["accept", "reject", "unresolved"] = "accept"
        elif sufficient and fused_score <= self.operator_bridge.config.reject_threshold:
            provisional = "reject"
        else:
            provisional = "unresolved"
        refinement = bool(
            permit_refinement
            and evidence.evidence_level == "coarse"
            and intervention_mode not in {"metacognition_cut", "joint_cut"}
            and (
                not sufficient
                or self.operator_bridge.config.refinement_low
                <= fused_score
                <= self.operator_bridge.config.refinement_high
                or not evidence.evidence_complete
            )
        )
        integrated = replace(
            base,
            continuity_score=float(np.clip(fused_score, 0.0, 1.0)),
            evidence_sufficient=sufficient,
            refinement_requested=refinement,
            provisional_relation=provisional,
            digest="",
        )
        integrated = replace(
            integrated, digest=_digest(_assessment_payload(integrated))
        )
        if not validate_continuity_assessment_receipt(integrated):
            raise RuntimeError("invalid integrated continuity assessment")
        operator = self.operator_bridge.assess(
            root, evidence, base, integrated=integrated
        )
        self._komorebi_receipts[integrated.digest] = operator
        return integrated

    def snapshot(self) -> dict[str, Any]:
        payload = super().snapshot()
        inherited_digest = payload.pop("digest", None)
        payload.update(
            {
                "schema": "rrct.v045.komorebi_operator_self_model_runtime.v1",
                "komorebi_version": KOMOREBI_VERSION,
                "komorebi_wheel_sha256": KOMOREBI_WHEEL_SHA256,
                "komorebi_operator_config": asdict(self.operator_bridge.config),
                "komorebi_operator_receipts": self.komorebi_operator_receipts,
                "komorebi_operator_receipt_count": len(self._komorebi_receipts),
                "inherited_runtime_digest": inherited_digest,
                "uses_evaluator_labels": False,
            }
        )
        payload["digest"] = _digest(payload)
        return copy.deepcopy(payload)


def validate_komorebi_assessment_chain(
    assessment: ContinuityAssessmentReceipt,
    operator: KomorebiOperatorAssessmentReceipt,
) -> bool:
    if not validate_continuity_assessment_receipt(assessment):
        return False
    if not validate_komorebi_operator_assessment_receipt(operator):
        return False
    if operator.integrated_assessment_digest != assessment.digest:
        return False
    if operator.evidence_digest != assessment.evidence_digest:
        return False
    if operator.predecessor_lineage_digest != assessment.predecessor_lineage_digest:
        return False
    if operator.sequence_id != assessment.sequence_id:
        return False
    if operator.time != assessment.time or operator.candidate_id != assessment.candidate_id:
        return False
    if operator.intervention_mode != assessment.intervention_mode:
        return False
    expected_score = (
        operator.base_continuity_score
        if operator.intervention_mode
        in {"snapshot_only", "causal_only", "memory_only", "joint_cut"}
        else operator.fused_continuity_score
    )
    if not np.isclose(assessment.continuity_score, expected_score, atol=1e-12):
        return False
    if assessment.evidence_sufficient != operator.evidence_sufficient and operator.intervention_mode not in {
        "snapshot_only",
        "causal_only",
        "memory_only",
        "joint_cut",
    }:
        return False
    if assessment.refinement_requested != operator.refinement_requested:
        return False
    if assessment.provisional_relation != operator.provisional_relation:
        return False
    return True


def validate_komorebi_transformational_receipt_chain(
    *,
    transition: TransformationalTransitionReceipt,
    adjudication: TransformationalAdjudicationReceipt,
    plan: TransformationalPlanningReceipt,
    task: SuccessorTaskReceipt,
    outcome: TransformationalOutcomeReceipt,
    operator_receipts: Sequence[KomorebiOperatorAssessmentReceipt],
) -> bool:
    if not validate_transformational_receipt_chain(
        transition=transition,
        adjudication=adjudication,
        plan=plan,
        task=task,
        outcome=outcome,
    ):
        return False
    by_integrated = {
        receipt.integrated_assessment_digest: receipt
        for receipt in operator_receipts
        if validate_komorebi_operator_assessment_receipt(receipt)
    }
    required = set(transition.coarse_assessment_digests) | set(
        adjudication.final_assessment_digests
    )
    return bool(required and required.issubset(by_integrated))


__all__ = [
    "ChangeClass",
    "KOMOREBI_VERSION",
    "KOMOREBI_WHEEL_SHA256",
    "KomorebiOperatorAssessmentReceipt",
    "KomorebiOperatorBridge",
    "KomorebiOperatorConfig",
    "KomorebiProjectorDiscoveryReceipt",
    "KomorebiTransformationalSelfContinuityController",
    "discover_controllable_packets",
    "validate_komorebi_assessment_chain",
    "validate_komorebi_operator_assessment_receipt",
    "validate_komorebi_projector_discovery_receipt",
    "validate_komorebi_transformational_receipt_chain",
]
