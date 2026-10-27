"""Canonical records for the Block 6 bidirectional compiler."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence


def canonical_value(value: Any) -> Any:
    """Return a JSON-stable representation without NumPy or tuple ambiguity."""
    try:
        import numpy as np
        if isinstance(value, np.ndarray):
            return canonical_value(value.tolist())
        if isinstance(value, np.generic):
            return value.item()
    except Exception:
        pass
    if isinstance(value, Mapping):
        return {str(k): canonical_value(v) for k, v in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, (tuple, list)):
        return [canonical_value(v) for v in value]
    if isinstance(value, set):
        return sorted(canonical_value(v) for v in value)
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(canonical_value(value), sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


def sha256_record(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class RouteSignature:
    shape_relation: str
    support_relation: str
    edit_kinds: tuple[tuple[str, int], ...] = ()
    delta_pattern_hash: str = ""
    enabled_lanes: tuple[str, ...] = ()

    def to_record(self) -> dict[str, Any]:
        return {
            "shape_relation": self.shape_relation,
            "support_relation": self.support_relation,
            "edit_kinds": dict(self.edit_kinds),
            "delta_pattern_hash": self.delta_pattern_hash,
            "enabled_lanes": list(self.enabled_lanes),
        }


@dataclass(frozen=True)
class CompiledProgram:
    family: str
    parameters: Mapping[str, Any]
    cost: int
    origin: str
    route: RouteSignature | None = None
    training_hashes: tuple[str, ...] = ()
    description: str = ""

    def __post_init__(self) -> None:
        if not self.family or self.family.strip() != self.family:
            raise ValueError("family must be a nonempty trimmed string")
        if int(self.cost) <= 0:
            raise ValueError("cost must be positive")

    @property
    def signature_record(self) -> dict[str, Any]:
        return {
            "family": self.family,
            "parameters": canonical_value(self.parameters),
        }

    @property
    def signature(self) -> str:
        return f"{self.family}:{canonical_json(self.parameters)}"

    @property
    def signature_hash(self) -> str:
        return sha256_record(self.signature_record)

    def to_record(self) -> dict[str, Any]:
        record = {
            "schema": "komorebi.lasm_compiled_relational_program",
            "schema_version": 1,
            "family": self.family,
            "parameters": canonical_value(self.parameters),
            "cost": int(self.cost),
            "origin": self.origin,
            "training_hashes": list(self.training_hashes),
            "description": self.description,
            "signature": self.signature,
            "signature_hash": self.signature_hash,
        }
        if self.route is not None:
            record["route"] = self.route.to_record()
        record["content_hash"] = sha256_record({k: v for k, v in record.items() if k != "content_hash"})
        return record


@dataclass(frozen=True)
class CandidateExecution:
    program: CompiledProgram
    outputs: tuple[tuple[tuple[int, ...], ...], ...]
    ir_program_hash: str
    direct_execution_hash: str

    @property
    def output_hash(self) -> str:
        return sha256_record(self.outputs)

    def to_record(self) -> dict[str, Any]:
        return {
            "program": self.program.to_record(),
            "outputs": canonical_value(self.outputs),
            "output_hash": self.output_hash,
            "ir_program_hash": self.ir_program_hash,
            "direct_execution_hash": self.direct_execution_hash,
        }


@dataclass
class CompilationTrace:
    route: RouteSignature
    lanes_attempted: list[str] = field(default_factory=list)
    raw_programs: int = 0
    exact_training_programs: int = 0
    behavior_classes: int = 0
    rejected_runtime: int = 0
    elapsed_seconds: float = 0.0

    def to_record(self) -> dict[str, Any]:
        return {
            "route": self.route.to_record(),
            "lanes_attempted": list(self.lanes_attempted),
            "raw_programs": int(self.raw_programs),
            "exact_training_programs": int(self.exact_training_programs),
            "behavior_classes": int(self.behavior_classes),
            "rejected_runtime": int(self.rejected_runtime),
            "elapsed_seconds": float(self.elapsed_seconds),
        }
