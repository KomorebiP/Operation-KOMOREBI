"""Canonical records for obstruction-guided PR-LASM macro synthesis.

Runtime records deliberately contain no ARC task identifiers, expected test grids, or
source-answer hashes. Those belong to the separate audit ledger.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping

from komorebi_lasm_compiler.model import canonical_value, sha256_record


class MacroStatus(str, Enum):
    CANDIDATE = "candidate"
    PROVISIONAL = "provisional"
    STABLE = "stable"
    RETIRED = "retired"


class ObstructionKind(str, Enum):
    IDENTITY = "identity"
    RECOLOR = "recolor"
    SUPPORT_ADD = "support_add"
    SUPPORT_REMOVE = "support_remove"
    SUPPORT_MIXED = "support_mixed"
    SHAPE_CHANGE = "shape_change"
    MIXED = "mixed"


@dataclass(frozen=True)
class HoleSpec:
    """One finite typed search coordinate in a macro sketch."""

    name: str
    value_type: str
    domain: tuple[Any, ...]
    source: str

    def __post_init__(self) -> None:
        if not self.name or self.name.strip() != self.name:
            raise ValueError("hole name must be nonempty and trimmed")
        if not self.domain:
            raise ValueError("hole domain must be nonempty")

    def to_record(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "value_type": self.value_type,
            "domain": canonical_value(self.domain),
            "source": self.source,
        }


@dataclass(frozen=True)
class ObstructionPacket:
    """Training-only diagnosis used to route finite sketch search."""

    shape_relation: str
    obstruction_kinds: tuple[str, ...]
    added_cells: tuple[int, ...]
    removed_cells: tuple[int, ...]
    recolored_cells: tuple[int, ...]
    input_color_counts: tuple[int, ...]
    output_color_counts: tuple[int, ...]
    training_pair_hashes: tuple[str, ...]
    scene_complexity: int
    route_lanes: tuple[str, ...]
    schema_version: int = 1

    @property
    def identity_record(self) -> dict[str, Any]:
        return {
            "schema": "komorebi.lasm_obstruction_packet",
            "schema_version": self.schema_version,
            "shape_relation": self.shape_relation,
            "obstruction_kinds": list(self.obstruction_kinds),
            "added_cells": list(self.added_cells),
            "removed_cells": list(self.removed_cells),
            "recolored_cells": list(self.recolored_cells),
            "input_color_counts": list(self.input_color_counts),
            "output_color_counts": list(self.output_color_counts),
            "training_pair_hashes": list(self.training_pair_hashes),
            "scene_complexity": int(self.scene_complexity),
            "route_lanes": list(self.route_lanes),
        }

    @property
    def packet_id(self) -> str:
        return sha256_record(self.identity_record)

    def to_record(self) -> dict[str, Any]:
        record = {**self.identity_record, "packet_id": self.packet_id}
        record["content_hash"] = sha256_record(record)
        return record


@dataclass(frozen=True)
class MacroSketch:
    """Typed finite program sketch whose holes are filled from demonstrations."""

    name: str
    schema: str
    family: str
    holes: tuple[HoleSpec, ...]
    obstruction_kinds: tuple[str, ...]
    cost: int
    description: str
    schema_version: int = 1

    def __post_init__(self) -> None:
        if not self.name or not self.schema or not self.family:
            raise ValueError("sketch name, schema, and family are required")
        if self.cost <= 0:
            raise ValueError("sketch cost must be positive")
        names = [hole.name for hole in self.holes]
        if len(names) != len(set(names)):
            raise ValueError("sketch hole names must be unique")

    @property
    def identity_record(self) -> dict[str, Any]:
        return {
            "schema": "komorebi.lasm_macro_sketch",
            "schema_version": self.schema_version,
            "name": self.name,
            "macro_schema": self.schema,
            "family": self.family,
            "holes": [hole.to_record() for hole in self.holes],
            "obstruction_kinds": list(self.obstruction_kinds),
            "cost": int(self.cost),
        }

    @property
    def sketch_id(self) -> str:
        return sha256_record(self.identity_record)

    def to_record(self) -> dict[str, Any]:
        record = {**self.identity_record, "sketch_id": self.sketch_id, "description": self.description}
        record["content_hash"] = sha256_record(record)
        return record


@dataclass(frozen=True)
class SynthesizedProgram:
    """One demonstration-exact instantiation of a macro sketch."""

    family: str
    macro_schema: str
    sketch_id: str
    parameters: Mapping[str, Any]
    cost: int
    training_hashes: tuple[str, ...]
    origin: str = "obstruction_guided_hole_fill"
    description: str = ""

    @property
    def signature_record(self) -> dict[str, Any]:
        return {
            "family": self.family,
            "macro_schema": self.macro_schema,
            "parameters": canonical_value(self.parameters),
        }

    @property
    def signature(self) -> str:
        return f"{self.family}:{sha256_record(self.signature_record)[:24]}"

    @property
    def signature_hash(self) -> str:
        return sha256_record(self.signature_record)

    def to_record(self) -> dict[str, Any]:
        record = {
            "schema": "komorebi.lasm_synthesized_macro_program",
            "schema_version": 1,
            "family": self.family,
            "macro_schema": self.macro_schema,
            "sketch_id": self.sketch_id,
            "parameters": canonical_value(self.parameters),
            "cost": int(self.cost),
            "training_hashes": list(self.training_hashes),
            "origin": self.origin,
            "description": self.description,
            "signature": self.signature,
            "signature_hash": self.signature_hash,
        }
        record["content_hash"] = sha256_record(record)
        return record


@dataclass(frozen=True)
class CandidateExecution:
    program: SynthesizedProgram
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
class SynthesisTrace:
    obstruction_packet_id: str
    lanes_attempted: list[str] = field(default_factory=list)
    sketches_considered: int = 0
    hole_assignments_considered: int = 0
    exact_training_programs: int = 0
    behavior_classes: int = 0
    runtime_rejections: int = 0
    elapsed_seconds: float = 0.0

    def to_record(self) -> dict[str, Any]:
        return {
            "obstruction_packet_id": self.obstruction_packet_id,
            "lanes_attempted": list(self.lanes_attempted),
            "sketches_considered": int(self.sketches_considered),
            "hole_assignments_considered": int(self.hole_assignments_considered),
            "exact_training_programs": int(self.exact_training_programs),
            "behavior_classes": int(self.behavior_classes),
            "runtime_rejections": int(self.runtime_rejections),
            "elapsed_seconds": float(self.elapsed_seconds),
        }


@dataclass(frozen=True)
class MacroSchemaEvidence:
    schema: str
    families: tuple[str, ...]
    activation_count: int
    exact_count: int
    wrong_count: int
    exact_source_tasks: int
    status: MacroStatus
    minimum_support: int
    evidence_digest: str

    def to_runtime_record(self) -> dict[str, Any]:
        record = {
            "schema": "komorebi.lasm_macro_schema",
            "schema_version": 1,
            "macro_schema": self.schema,
            "families": list(self.families),
            "status": self.status.value,
            "minimum_support": int(self.minimum_support),
            "exact_source_tasks": int(self.exact_source_tasks),
            "activation_count": int(self.activation_count),
            "wrong_count": int(self.wrong_count),
            "evidence_digest": self.evidence_digest,
        }
        record["macro_id"] = sha256_record({
            key: value for key, value in record.items()
            if key not in {"exact_source_tasks", "activation_count", "wrong_count", "evidence_digest"}
        })
        record["content_hash"] = sha256_record(record)
        return record


__all__ = [
    "CandidateExecution", "HoleSpec", "MacroSchemaEvidence", "MacroSketch",
    "MacroStatus", "ObstructionKind", "ObstructionPacket", "SynthesizedProgram",
    "SynthesisTrace",
]
