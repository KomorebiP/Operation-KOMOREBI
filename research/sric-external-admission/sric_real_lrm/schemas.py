from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence
import json


@dataclass(frozen=True)
class TaskRecord:
    task_id: str
    question: str
    answer: str
    steps: tuple[str, ...]
    proof_depth: int
    proof_signature: tuple[str, ...]
    orbit_id: str
    group_id: str
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, row: Mapping[str, Any], index: int = 0) -> "TaskRecord":
        steps = tuple(str(x) for x in row.get("steps", ()))
        task_id = str(row.get("task_id", row.get("idx", index)))
        proof_signature = row.get("proof_signature")
        if proof_signature is None:
            from .dataset import proof_signature_from_steps
            proof_signature = proof_signature_from_steps(steps)
        proof_depth = int(row.get("proof_depth", len(steps)))
        orbit_id = str(row.get("orbit_id", task_id))
        group_id = str(row.get("group_id", orbit_id))
        return cls(
            task_id=task_id,
            question=str(row["question"]),
            answer=str(row["answer"]),
            steps=steps,
            proof_depth=proof_depth,
            proof_signature=tuple(str(x) for x in proof_signature),
            orbit_id=orbit_id,
            group_id=group_id,
            metadata=dict(row.get("metadata", {})),
        )

    def to_mapping(self) -> dict[str, Any]:
        obj = asdict(self)
        obj["steps"] = list(self.steps)
        obj["proof_signature"] = list(self.proof_signature)
        return obj


@dataclass(frozen=True)
class TraceObservation:
    trace: Any
    answer_loss: float
    answer_logits: Any
    predicted_answer: str | None = None
    generated_text: str | None = None
    generated_correct: bool | None = None
    mode: str = "latent"
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AuditThresholds:
    replay_max_abs: float = 1e-5
    necessity_mean: float = 0.02
    necessity_positive_fraction: float = 0.60
    order_mean: float = 0.01
    structure_mean: float = 0.02
    covariance_structure_mean: float = 0.01
    procedure_mean: float = 0.02
    procedure_positive_fraction: float = 0.65
    twin_abs_mean_max: float = 0.01
    twin_absolute_ceiling: float = 0.05

    @classmethod
    def from_mapping(cls, obj: Mapping[str, Any]) -> "AuditThresholds":
        return cls(**{k: obj[k] for k in cls.__dataclass_fields__ if k in obj})


@dataclass(frozen=True)
class SemanticThresholds:
    minimum_tasks: int = 24
    max_rank: int = 8
    ridge: float = 1e-4
    future_r2: float = 0.20
    procedure_future_r2: float = 0.20
    intervention_r2: float = 0.15
    answer_accuracy: float = 0.70
    twin_drift_max: float = 0.20
    proof_witness_r2: float = 0.15
    patch_recovery_ratio: float = 0.25
    patch_positive_fraction: float = 0.55
    full_state_rank_penalty: int = 1000

    @classmethod
    def from_mapping(cls, obj: Mapping[str, Any]) -> "SemanticThresholds":
        return cls(**{k: obj[k] for k in cls.__dataclass_fields__ if k in obj})


@dataclass(frozen=True)
class AuditConfig:
    schema: str = "sric.real-lrm.audit-config.v3"
    seed: int = 2301
    num_latents: int = 6
    max_tasks: int = 64
    bootstrap_replicates: int = 2000
    truncation: bool = True
    run_norm_noise: bool = True
    run_covariance_noise: bool = True
    run_mode_controls: bool = True
    semantic_escalation: bool = True
    causal_calibration_fraction: float = 0.20
    semantic_discovery_fraction: float = 0.50
    semantic_calibration_fraction: float = 0.25
    cache_captures: bool = True
    specificity_claim: str = "procedure"
    thresholds: AuditThresholds = field(default_factory=AuditThresholds)
    semantic_thresholds: SemanticThresholds = field(default_factory=SemanticThresholds)

    @classmethod
    def from_mapping(cls, obj: Mapping[str, Any]) -> "AuditConfig":
        thresholds = AuditThresholds.from_mapping(obj.get("thresholds", {}))
        semantic_thresholds = SemanticThresholds.from_mapping(obj.get("semantic_thresholds", {}))
        values = {
            k: obj[k]
            for k in cls.__dataclass_fields__
            if k in obj and k not in {"thresholds", "semantic_thresholds"}
        }
        # Backward compatibility with the Pilot 0.1 name.
        if "covariance_noise" in obj and "run_covariance_noise" not in values:
            values["run_covariance_noise"] = bool(obj["covariance_noise"])
        config = cls(**values, thresholds=thresholds, semantic_thresholds=semantic_thresholds)
        config.validate()
        return config

    @classmethod
    def load(cls, path: str | Path) -> "AuditConfig":
        return cls.from_mapping(json.loads(Path(path).read_text(encoding="utf-8")))

    def validate(self) -> None:
        if self.num_latents < 2:
            raise ValueError("num_latents must be at least two")
        if self.max_tasks < 1:
            raise ValueError("max_tasks must be positive")
        if self.bootstrap_replicates < 1:
            raise ValueError("bootstrap_replicates must be positive")
        if not 0.0 < self.causal_calibration_fraction < 0.5:
            raise ValueError("causal_calibration_fraction must lie in (0, 0.5)")
        if not 0.0 < self.semantic_discovery_fraction < 1.0:
            raise ValueError("semantic_discovery_fraction must lie in (0, 1)")
        if not 0.0 < self.semantic_calibration_fraction < 1.0:
            raise ValueError("semantic_calibration_fraction must lie in (0, 1)")
        if self.semantic_discovery_fraction + self.semantic_calibration_fraction >= 1.0:
            raise ValueError("semantic discovery and calibration fractions must leave a final split")
        if self.specificity_claim not in {"content", "procedure"}:
            raise ValueError("specificity_claim must be content or procedure")

    def to_mapping(self) -> dict[str, Any]:
        return asdict(self)


def load_task_records(path: str | Path, max_tasks: int | None = None) -> list[TaskRecord]:
    rows = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(rows, Sequence):
        raise ValueError("Task file must contain a JSON array")
    if max_tasks is not None:
        rows = rows[:max_tasks]
    records = [TaskRecord.from_mapping(row, index=i) for i, row in enumerate(rows)]
    ids = [r.task_id for r in records]
    if len(ids) != len(set(ids)):
        raise ValueError("Task IDs must be unique")
    return records
