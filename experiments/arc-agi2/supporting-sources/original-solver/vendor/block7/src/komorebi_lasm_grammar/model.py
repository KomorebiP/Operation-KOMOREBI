"""Canonical records for persistent PR-LASM grammar promotion.

The runtime records in this module deliberately exclude source task identifiers and
output grids.  Source provenance belongs to the separate audit ledger.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Sequence

from komorebi_lasm_compiler.model import canonical_value, sha256_record


class MacroScope(str, Enum):
    """The semantic breadth at which an operator abstraction is promoted."""

    FAMILY = "family"
    CONTROL = "control"
    SCHEMA = "schema"
    EXACT = "exact"


class MacroStatus(str, Enum):
    """Lifecycle state of a grammar abstraction."""

    CANDIDATE = "candidate"
    PROVISIONAL = "provisional"
    STABLE = "stable"
    RETIRED = "retired"


@dataclass(frozen=True)
class HoleSpec:
    """One typed parameter hole in an anti-unified macro template."""

    name: str
    path: tuple[str, ...]
    value_type: str
    optional: bool = False

    def to_record(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "path": list(self.path),
            "value_type": self.value_type,
            "optional": bool(self.optional),
        }


@dataclass(frozen=True)
class CompressionCertificate:
    """Finite description-length proxy for a promoted abstraction."""

    raw_bytes: int
    macro_bytes: int
    instantiation_bytes: int
    compression_gain_bytes: int
    source_program_count: int

    def to_record(self) -> dict[str, int]:
        return {
            "raw_bytes": int(self.raw_bytes),
            "macro_bytes": int(self.macro_bytes),
            "instantiation_bytes": int(self.instantiation_bytes),
            "compression_gain_bytes": int(self.compression_gain_bytes),
            "source_program_count": int(self.source_program_count),
        }


@dataclass(frozen=True)
class MacroTemplate:
    """Task-ID-free, role-bound executable grammar abstraction.

    ``parameter_template`` may contain records of the form
    ``{"$hole": "h0", "type": "color_role"}``.  The bank never stores the
    values observed at individual source tasks.
    """

    family: str
    scope: MacroScope
    controls: Mapping[str, Any]
    parameter_template: Any
    holes: tuple[HoleSpec, ...]
    status: MacroStatus
    exact_source_tasks: int
    activation_count: int
    wrong_activation_count: int
    minimum_support: int
    compression: CompressionCertificate
    evidence_digest: str
    description: str = ""
    schema_version: int = 1

    def __post_init__(self) -> None:
        if not self.family or self.family.strip() != self.family:
            raise ValueError("macro family must be a nonempty trimmed string")
        if self.minimum_support < 1:
            raise ValueError("minimum_support must be positive")
        if self.exact_source_tasks < 0 or self.activation_count < 0 or self.wrong_activation_count < 0:
            raise ValueError("macro evidence counts cannot be negative")
        if self.status is MacroStatus.STABLE:
            if self.exact_source_tasks < self.minimum_support:
                raise ValueError("stable macro lacks minimum source support")
            if self.wrong_activation_count:
                raise ValueError("stable macro has wrong activations")

    @property
    def identity_record(self) -> dict[str, Any]:
        return {
            "schema": "komorebi.lasm_macro_template",
            "schema_version": int(self.schema_version),
            "family": self.family,
            "scope": self.scope.value,
            "controls": canonical_value(self.controls),
            "parameter_template": canonical_value(self.parameter_template),
            "holes": [hole.to_record() for hole in self.holes],
        }

    @property
    def macro_id(self) -> str:
        return sha256_record(self.identity_record)

    def matches(self, family: str, parameters: Mapping[str, Any]) -> bool:
        if family != self.family:
            return False
        return all(canonical_value(parameters.get(key)) == canonical_value(value) for key, value in self.controls.items())

    def to_record(self) -> dict[str, Any]:
        record = {
            **self.identity_record,
            "macro_id": self.macro_id,
            "status": self.status.value,
            "exact_source_tasks": int(self.exact_source_tasks),
            "activation_count": int(self.activation_count),
            "wrong_activation_count": int(self.wrong_activation_count),
            "minimum_support": int(self.minimum_support),
            "compression": self.compression.to_record(),
            "evidence_digest": self.evidence_digest,
            "description": self.description,
        }
        record["content_hash"] = sha256_record({key: value for key, value in record.items() if key != "content_hash"})
        return record


@dataclass
class MacroEvidence:
    """Audit-only source evidence for one abstraction key."""

    key: str
    scope: MacroScope
    family: str
    controls: dict[str, Any]
    activation_count: int = 0
    exact_count: int = 0
    wrong_count: int = 0
    exact_task_ids: set[str] = field(default_factory=set)
    wrong_task_ids: set[str] = field(default_factory=set)
    source_signatures: set[str] = field(default_factory=set)
    parameter_records: list[dict[str, Any]] = field(default_factory=list)

    @property
    def exact_source_tasks(self) -> int:
        return len(self.exact_task_ids)

    def observe(
        self,
        *,
        task_id: str,
        signature: str,
        parameters: Mapping[str, Any],
        correct: bool,
    ) -> None:
        self.activation_count += 1
        self.source_signatures.add(str(signature))
        self.parameter_records.append(dict(canonical_value(parameters)))
        if correct:
            self.exact_count += 1
            self.exact_task_ids.add(str(task_id))
        else:
            self.wrong_count += 1
            self.wrong_task_ids.add(str(task_id))

    def to_audit_record(self) -> dict[str, Any]:
        record = {
            "key": self.key,
            "scope": self.scope.value,
            "family": self.family,
            "controls": canonical_value(self.controls),
            "activation_count": int(self.activation_count),
            "exact_count": int(self.exact_count),
            "wrong_count": int(self.wrong_count),
            "exact_source_tasks": int(self.exact_source_tasks),
            "exact_task_ids": sorted(self.exact_task_ids),
            "wrong_task_ids": sorted(self.wrong_task_ids),
            "source_signatures": sorted(self.source_signatures),
        }
        record["content_hash"] = sha256_record(record)
        return record


@dataclass(frozen=True)
class MacroBank:
    """Immutable task-ID-free bank of promoted grammar abstractions."""

    macros: tuple[MacroTemplate, ...]
    minimum_support: int = 2
    schema_version: int = 1

    def __post_init__(self) -> None:
        ids = [macro.macro_id for macro in self.macros]
        if len(ids) != len(set(ids)):
            raise ValueError("macro IDs must be unique")
        if any(macro.status is not MacroStatus.STABLE for macro in self.macros):
            raise ValueError("runtime bank may contain only stable macros")

    def matching(self, family: str, parameters: Mapping[str, Any]) -> tuple[MacroTemplate, ...]:
        return tuple(macro for macro in self.macros if macro.matches(family, parameters))

    def permits(self, family: str, parameters: Mapping[str, Any]) -> bool:
        return bool(self.matching(family, parameters))

    @property
    def bank_id(self) -> str:
        return sha256_record({
            "schema": "komorebi.lasm_macro_bank",
            "schema_version": int(self.schema_version),
            "minimum_support": int(self.minimum_support),
            "macro_ids": [macro.macro_id for macro in self.macros],
        })

    def to_runtime_record(self) -> dict[str, Any]:
        record = {
            "schema": "komorebi.lasm_macro_bank",
            "schema_version": int(self.schema_version),
            "minimum_support": int(self.minimum_support),
            "bank_id": self.bank_id,
            "macros": [macro.to_record() for macro in self.macros],
        }
        record["content_hash"] = sha256_record({key: value for key, value in record.items() if key != "content_hash"})
        return record

    @classmethod
    def from_runtime_record(cls, record: Mapping[str, Any]) -> "MacroBank":
        if record.get("schema") != "komorebi.lasm_macro_bank":
            raise ValueError("not a macro bank record")
        macros = []
        for item in record.get("macros", []):
            holes = tuple(
                HoleSpec(
                    name=str(hole["name"]),
                    path=tuple(str(part) for part in hole.get("path", [])),
                    value_type=str(hole["value_type"]),
                    optional=bool(hole.get("optional", False)),
                )
                for hole in item.get("holes", [])
            )
            compression = CompressionCertificate(**{key: int(value) for key, value in item["compression"].items()})
            macro = MacroTemplate(
                family=str(item["family"]),
                scope=MacroScope(str(item["scope"])),
                controls=dict(item.get("controls", {})),
                parameter_template=item.get("parameter_template"),
                holes=holes,
                status=MacroStatus(str(item["status"])),
                exact_source_tasks=int(item["exact_source_tasks"]),
                activation_count=int(item["activation_count"]),
                wrong_activation_count=int(item["wrong_activation_count"]),
                minimum_support=int(item["minimum_support"]),
                compression=compression,
                evidence_digest=str(item["evidence_digest"]),
                description=str(item.get("description", "")),
                schema_version=int(item.get("schema_version", 1)),
            )
            if item.get("macro_id") and item["macro_id"] != macro.macro_id:
                raise ValueError("macro ID mismatch")
            macros.append(macro)
        bank = cls(tuple(sorted(macros, key=lambda macro: macro.macro_id)), int(record.get("minimum_support", 2)), int(record.get("schema_version", 1)))
        if record.get("bank_id") and record["bank_id"] != bank.bank_id:
            raise ValueError("macro bank ID mismatch")
        expected = sha256_record({key: value for key, value in record.items() if key != "content_hash"})
        if record.get("content_hash") and record["content_hash"] != expected:
            raise ValueError("macro bank content hash mismatch")
        return bank


__all__ = [
    "CompressionCertificate",
    "HoleSpec",
    "MacroBank",
    "MacroEvidence",
    "MacroScope",
    "MacroStatus",
    "MacroTemplate",
]
