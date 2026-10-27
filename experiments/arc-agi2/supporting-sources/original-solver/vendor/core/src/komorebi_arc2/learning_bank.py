"""Leakage-resistant persistent macro learning for typed ARC programs.

The solver cannot honestly claim to learn across tasks if a revealed test label
can influence the prediction receipt for that same task.  This module makes
that boundary explicit.  A query is first opened and cryptographically sealed,
then (and only then) may its label be revealed and used to update an immutable
macro bank.  Newly admitted macros are therefore eligible starting at the next
sequence position.

Macro records deliberately contain only a versioned :class:`TypedProgramAST`.
Source identifiers, grids, filesystem paths, and labels are never stored in a
macro.  The surrounding evidence ledger keeps content hashes and evaluator
attestations needed to audit admission without retaining task payloads.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Mapping, Optional, Sequence

from .program_ast import (
    CallNode,
    IdentityNode,
    PrimitiveRegistry,
    SequenceNode,
    TypedProgramAST,
    ValueType,
)


LEARNING_BANK_SCHEMA = "komorebi.prequential_macro_bank"
LEARNING_BANK_SCHEMA_VERSION = 2
MACRO_SCHEMA = "komorebi.typed_macro"
QUERY_RECEIPT_SCHEMA = "komorebi.pre_reveal_query"
OBSERVATION_SCHEMA = "komorebi.sealed_reveal"
LEDGER_EVENT_SCHEMA = "komorebi.learning_ledger_event"


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def content_hash_text(value: str) -> str:
    """Return the canonical SHA-256 spelling used throughout the bank API."""

    if not isinstance(value, str):
        raise TypeError("content to hash must be text")
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _record_hash(record: Mapping[str, object]) -> str:
    return content_hash_text(_canonical_json(record))


def _require_hash(value: object, field: str) -> str:
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise ValueError(f"{field} must be a lowercase SHA-256 digest")
    return value


def _require_mapping(value: object, context: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{context} must be a mapping")
    return value


def _require_list(value: object, context: str) -> list[object]:
    if not isinstance(value, list):
        raise TypeError(f"{context} must be a list")
    return value


def _exact_keys(record: Mapping[str, object], expected: set[str], context: str) -> None:
    extra = set(record) - expected
    missing = expected - set(record)
    if extra or missing:
        raise ValueError(
            f"{context} fields do not match schema; "
            f"missing={sorted(missing)}, extra={sorted(extra)}"
        )


@dataclass(frozen=True)
class MacroRecord:
    """A canonical macro containing typed executable data and nothing else."""

    program: TypedProgramAST
    schema_version: int = LEARNING_BANK_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self.program, TypedProgramAST):
            raise TypeError("macro program must be a TypedProgramAST")
        if self.schema_version != LEARNING_BANK_SCHEMA_VERSION:
            raise ValueError(f"unsupported macro schema version {self.schema_version}")

    @property
    def program_hash(self) -> str:
        return self.program.content_hash()

    @property
    def description_bits(self) -> int:
        return len(self.to_json().encode("utf-8")) * 8

    def to_record(self) -> dict[str, object]:
        return {
            "schema": MACRO_SCHEMA,
            "schema_version": self.schema_version,
            "program": self.program.to_record(),
        }

    def to_json(self) -> str:
        return _canonical_json(self.to_record())

    def content_hash(self) -> str:
        return content_hash_text(self.to_json())

    @classmethod
    def from_record(cls, raw: object) -> "MacroRecord":
        record = _require_mapping(raw, "macro")
        _exact_keys(record, {"schema", "schema_version", "program"}, "macro")
        if record["schema"] != MACRO_SCHEMA:
            raise ValueError(f"unknown macro schema {record['schema']!r}")
        return cls(
            program=TypedProgramAST.from_record(record["program"]),
            schema_version=int(record["schema_version"]),
        )

    @classmethod
    def from_json(cls, payload: str) -> "MacroRecord":
        return cls.from_record(json.loads(payload))


def _program_calls(program: TypedProgramAST) -> tuple[CallNode, ...]:
    calls: list[CallNode] = []

    def visit(node: IdentityNode | CallNode | SequenceNode) -> None:
        if isinstance(node, IdentityNode):
            return
        if isinstance(node, CallNode):
            calls.append(node)
            return
        if isinstance(node, SequenceNode):
            for step in node.steps:
                visit(step)
            return
        raise TypeError(f"unsupported program node {type(node)!r}")

    visit(program.root)
    return tuple(calls)


def registry_contract_hash(registry: PrimitiveRegistry) -> str:
    """Hash the registry's unique symbolic names and declared signatures."""

    definitions = []
    for name in registry.names:
        primitive = registry.resolve(name)
        definitions.append(
            {
                "name": name,
                "input_type": primitive.input_type.value,
                "output_type": primitive.output_type.value,
            }
        )
    return _record_hash(
        {
            "schema": "komorebi.primitive_registry_contract",
            "schema_version": 1,
            "definitions": definitions,
        }
    )


def _resolution_failure(
    program: TypedProgramAST, registry: PrimitiveRegistry
) -> Optional[str]:
    if program.input_type != ValueType.GRID or program.output_type != ValueType.GRID:
        return "macro_not_grid_to_grid"
    for call in _program_calls(program):
        try:
            primitive = registry.resolve(call.primitive)
        except KeyError:
            return f"unresolved_primitive:{call.primitive}"
        if primitive.input_type != call.input_type:
            return f"primitive_input_type_mismatch:{call.primitive}"
        if primitive.output_type != call.output_type:
            return f"primitive_output_type_mismatch:{call.primitive}"
    return None


_LITERAL_COLOR_PATTERNS = (
    re.compile(r"(?:^|[_.:/-])literal_colou?r(?:[_.:/=-]*\d+)?(?:$|[_.:/-])"),
    re.compile(r"^recolou?r[_.:/-]*\d+[_.:/-]+to[_.:/-]+\d+$"),
    re.compile(r"^recolou?r[_.:/-]+.+[_.:/-]+to[_.:/=-]*\d+$"),
    re.compile(r"^(?:set|paint|fill)[_.:/-]*colou?r[_.:/=-]*\d+$"),
    re.compile(r"^replace[_.:/-]*colou?r[_.:/=-]*\d+[_.:/-]+(?:with|to)[_.:/=-]*\d+$"),
)


def _excluded_step(program: TypedProgramAST) -> Optional[str]:
    for call in _program_calls(program):
        lowered = call.primitive.casefold()
        if "terminal_exact_rule" in lowered:
            return f"excluded_terminal_exact_rule:{call.primitive}"
        if lowered.startswith("recursive_growth_"):
            return f"excluded_recursive_growth_step:{call.primitive}"
        if any(pattern.search(lowered) is not None for pattern in _LITERAL_COLOR_PATTERNS):
            return f"excluded_literal_color_step:{call.primitive}"
    return None


class BankMode(str, Enum):
    LEARNING = "learning"
    RESTART_CONTROL = "restart_control"


@dataclass(frozen=True)
class ResolutionAbstention:
    subject_kind: str
    subject_hash: str
    reason: str

    def __post_init__(self) -> None:
        if self.subject_kind not in {"bank_macro", "pre_reveal_program"}:
            raise ValueError(f"unknown abstention subject {self.subject_kind!r}")
        _require_hash(self.subject_hash, "abstention subject hash")
        if not self.reason:
            raise ValueError("abstention reason must be nonempty")

    def to_record(self) -> dict[str, object]:
        return {
            "subject_kind": self.subject_kind,
            "subject_hash": self.subject_hash,
            "reason": self.reason,
        }

    @classmethod
    def from_record(cls, raw: object) -> "ResolutionAbstention":
        record = _require_mapping(raw, "resolution abstention")
        _exact_keys(record, {"subject_kind", "subject_hash", "reason"}, "abstention")
        return cls(
            subject_kind=str(record["subject_kind"]),
            subject_hash=str(record["subject_hash"]),
            reason=str(record["reason"]),
        )


@dataclass(frozen=True)
class ProgramDiscoveryCertificate:
    """Pre-reveal evidence that a committed program survived demo folds."""

    program_hash: str
    source_content_hash: str
    interpreter_contract: str
    miner_contract: str
    distinct_nonidentity_group_hashes: tuple[str, ...]
    fold_selected_program_hashes: tuple[str, ...]
    full_demo_exact: bool
    demo_loo_exact: bool
    schema_version: int = LEARNING_BANK_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.schema_version != LEARNING_BANK_SCHEMA_VERSION:
            raise ValueError(
                f"unsupported discovery certificate version {self.schema_version}"
            )
        for value, field in (
            (self.program_hash, "discovery program hash"),
            (self.source_content_hash, "discovery source content hash"),
            (self.interpreter_contract, "discovery interpreter contract"),
            (self.miner_contract, "discovery miner contract"),
        ):
            _require_hash(value, field)
        groups = self.distinct_nonidentity_group_hashes
        if tuple(sorted(set(groups))) != groups:
            raise ValueError(
                "distinct nonidentity group hashes must be unique and sorted"
            )
        for value in groups:
            _require_hash(value, "nonidentity group hash")
        if len(self.fold_selected_program_hashes) != len(groups):
            raise ValueError(
                "fold selections must align with distinct nonidentity groups"
            )
        for value in self.fold_selected_program_hashes:
            _require_hash(value, "fold selected program hash")
        if not isinstance(self.full_demo_exact, bool):
            raise TypeError("full_demo_exact must be a boolean")
        if not isinstance(self.demo_loo_exact, bool):
            raise TypeError("demo_loo_exact must be a boolean")
        if self.demo_loo_exact and (
            not self.full_demo_exact or len(groups) < 2
        ):
            raise ValueError(
                "demo LOO exactness requires full exactness and two distinct "
                "nonidentity groups"
            )
        if self.demo_loo_exact and any(
            selected != self.program_hash
            for selected in self.fold_selected_program_hashes
        ):
            raise ValueError(
                "demo LOO exactness requires the same program to be selected "
                "in every held-out fold"
            )

    def to_record(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "program_hash": self.program_hash,
            "source_content_hash": self.source_content_hash,
            "interpreter_contract": self.interpreter_contract,
            "miner_contract": self.miner_contract,
            "distinct_nonidentity_group_hashes": list(
                self.distinct_nonidentity_group_hashes
            ),
            "fold_selected_program_hashes": list(
                self.fold_selected_program_hashes
            ),
            "full_demo_exact": self.full_demo_exact,
            "demo_loo_exact": self.demo_loo_exact,
        }

    def content_hash(self) -> str:
        return _record_hash(self.to_record())

    @classmethod
    def from_record(cls, raw: object) -> "ProgramDiscoveryCertificate":
        record = _require_mapping(raw, "program discovery certificate")
        _exact_keys(
            record,
            {
                "schema_version",
                "program_hash",
                "source_content_hash",
                "interpreter_contract",
                "miner_contract",
                "distinct_nonidentity_group_hashes",
                "fold_selected_program_hashes",
                "full_demo_exact",
                "demo_loo_exact",
            },
            "program discovery certificate",
        )
        raw_full = record["full_demo_exact"]
        raw_loo = record["demo_loo_exact"]
        if not isinstance(raw_full, bool) or not isinstance(raw_loo, bool):
            raise TypeError("discovery exactness fields must be booleans")
        return cls(
            program_hash=str(record["program_hash"]),
            source_content_hash=str(record["source_content_hash"]),
            interpreter_contract=str(record["interpreter_contract"]),
            miner_contract=str(record["miner_contract"]),
            distinct_nonidentity_group_hashes=tuple(
                str(value)
                for value in _require_list(
                    record["distinct_nonidentity_group_hashes"],
                    "distinct nonidentity group hashes",
                )
            ),
            fold_selected_program_hashes=tuple(
                str(value)
                for value in _require_list(
                    record["fold_selected_program_hashes"],
                    "fold selected program hashes",
                )
            ),
            full_demo_exact=raw_full,
            demo_loo_exact=raw_loo,
            schema_version=int(record["schema_version"]),
        )


@dataclass(frozen=True)
class QueryReceipt:
    """A prediction-time commitment created before the test label is visible."""

    sequence_index: int
    source_content_hash: str
    bank_head_before: str
    registry_contract: str
    interpreter_contract: str
    mode: BankMode
    active_macro_hashes: tuple[str, ...]
    committed_program_hashes: tuple[str, ...]
    abstentions: tuple[ResolutionAbstention, ...]
    discovery_certificates: tuple[ProgramDiscoveryCertificate, ...] = ()
    schema_version: int = LEARNING_BANK_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.schema_version != LEARNING_BANK_SCHEMA_VERSION:
            raise ValueError(f"unsupported query receipt version {self.schema_version}")
        if self.sequence_index < 0:
            raise ValueError("query sequence index must be nonnegative")
        _require_hash(self.source_content_hash, "source content hash")
        _require_hash(self.bank_head_before, "bank head")
        _require_hash(self.registry_contract, "registry contract")
        _require_hash(self.interpreter_contract, "interpreter contract")
        for field, values in (
            ("active macro hashes", self.active_macro_hashes),
            ("committed program hashes", self.committed_program_hashes),
        ):
            if tuple(sorted(set(values))) != values:
                raise ValueError(f"{field} must be unique and sorted")
            for value in values:
                _require_hash(value, field)
        sorted_abstentions = tuple(
            sorted(
                self.abstentions,
                key=lambda item: (item.subject_kind, item.subject_hash, item.reason),
            )
        )
        if sorted_abstentions != self.abstentions:
            raise ValueError("abstentions must be deterministically sorted")
        ordered_certificates = tuple(
            sorted(
                self.discovery_certificates,
                key=lambda item: item.program_hash,
            )
        )
        if ordered_certificates != self.discovery_certificates:
            raise ValueError(
                "discovery certificates must be sorted by program hash"
            )
        certificate_hashes = tuple(
            certificate.program_hash for certificate in self.discovery_certificates
        )
        if len(set(certificate_hashes)) != len(certificate_hashes):
            raise ValueError("discovery certificate program hashes must be unique")
        committed = set(self.committed_program_hashes)
        for certificate in self.discovery_certificates:
            if certificate.program_hash not in committed:
                raise ValueError(
                    "a discovery certificate must refer to a committed program"
                )
            if certificate.source_content_hash != self.source_content_hash:
                raise ValueError(
                    "discovery certificate source differs from query receipt"
                )
            if certificate.interpreter_contract != self.interpreter_contract:
                raise ValueError(
                    "discovery certificate interpreter differs from query receipt"
                )

    def to_record(self) -> dict[str, object]:
        return {
            "schema": QUERY_RECEIPT_SCHEMA,
            "schema_version": self.schema_version,
            "sequence_index": self.sequence_index,
            "source_content_hash": self.source_content_hash,
            "bank_head_before": self.bank_head_before,
            "registry_contract": self.registry_contract,
            "interpreter_contract": self.interpreter_contract,
            "mode": self.mode.value,
            "active_macro_hashes": list(self.active_macro_hashes),
            "committed_program_hashes": list(self.committed_program_hashes),
            "abstentions": [item.to_record() for item in self.abstentions],
            "discovery_certificates": [
                item.to_record() for item in self.discovery_certificates
            ],
        }

    def to_json(self) -> str:
        return _canonical_json(self.to_record())

    def content_hash(self) -> str:
        return content_hash_text(self.to_json())

    @classmethod
    def from_record(cls, raw: object) -> "QueryReceipt":
        record = _require_mapping(raw, "query receipt")
        _exact_keys(
            record,
            {
                "schema",
                "schema_version",
                "sequence_index",
                "source_content_hash",
                "bank_head_before",
                "registry_contract",
                "interpreter_contract",
                "mode",
                "active_macro_hashes",
                "committed_program_hashes",
                "abstentions",
                "discovery_certificates",
            },
            "query receipt",
        )
        if record["schema"] != QUERY_RECEIPT_SCHEMA:
            raise ValueError(f"unknown query receipt schema {record['schema']!r}")
        return cls(
            sequence_index=int(record["sequence_index"]),
            source_content_hash=str(record["source_content_hash"]),
            bank_head_before=str(record["bank_head_before"]),
            registry_contract=str(record["registry_contract"]),
            interpreter_contract=str(record["interpreter_contract"]),
            mode=BankMode(str(record["mode"])),
            active_macro_hashes=tuple(
                str(value)
                for value in _require_list(
                    record["active_macro_hashes"], "active macro hashes"
                )
            ),
            committed_program_hashes=tuple(
                str(value)
                for value in _require_list(
                    record["committed_program_hashes"], "committed program hashes"
                )
            ),
            abstentions=tuple(
                ResolutionAbstention.from_record(value)
                for value in _require_list(record["abstentions"], "abstentions")
            ),
            discovery_certificates=tuple(
                ProgramDiscoveryCertificate.from_record(value)
                for value in _require_list(
                    record["discovery_certificates"],
                    "discovery certificates",
                )
            ),
            schema_version=int(record["schema_version"]),
        )


@dataclass(frozen=True)
class SealedObservation:
    """Post-reveal evaluator attestations tied to one pre-reveal receipt."""

    receipt: QueryReceipt
    label_content_hash: str
    exact_program_hashes: tuple[str, ...]
    schema_version: int = LEARNING_BANK_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.schema_version != LEARNING_BANK_SCHEMA_VERSION:
            raise ValueError(f"unsupported observation version {self.schema_version}")
        _require_hash(self.label_content_hash, "label content hash")
        if tuple(sorted(set(self.exact_program_hashes))) != self.exact_program_hashes:
            raise ValueError("exact program hashes must be unique and sorted")
        committed = set(self.receipt.committed_program_hashes)
        for program_hash in self.exact_program_hashes:
            _require_hash(program_hash, "exact program hash")
            if program_hash not in committed:
                raise ValueError(
                    "a program cannot be marked exact unless it was committed "
                    "in the pre-reveal receipt"
                )

    @property
    def receipt_hash(self) -> str:
        return self.receipt.content_hash()

    def to_record(self) -> dict[str, object]:
        return {
            "schema": OBSERVATION_SCHEMA,
            "schema_version": self.schema_version,
            "receipt": self.receipt.to_record(),
            "label_content_hash": self.label_content_hash,
            "exact_program_hashes": list(self.exact_program_hashes),
        }

    def content_hash(self) -> str:
        return _record_hash(self.to_record())

    @classmethod
    def from_record(cls, raw: object) -> "SealedObservation":
        record = _require_mapping(raw, "sealed observation")
        _exact_keys(
            record,
            {
                "schema",
                "schema_version",
                "receipt",
                "label_content_hash",
                "exact_program_hashes",
            },
            "sealed observation",
        )
        if record["schema"] != OBSERVATION_SCHEMA:
            raise ValueError(f"unknown observation schema {record['schema']!r}")
        return cls(
            receipt=QueryReceipt.from_record(record["receipt"]),
            label_content_hash=str(record["label_content_hash"]),
            exact_program_hashes=tuple(
                str(value)
                for value in _require_list(
                    record["exact_program_hashes"], "exact program hashes"
                )
            ),
            schema_version=int(record["schema_version"]),
        )


@dataclass(frozen=True)
class AdmissionEvidence:
    """Minimum support and compression evidence for one proposed macro."""

    source_receipt_hashes: tuple[str, ...]
    demo_loo_exact: bool
    uncompressed_description_bits: int

    def __post_init__(self) -> None:
        normalized = tuple(sorted(set(self.source_receipt_hashes)))
        object.__setattr__(self, "source_receipt_hashes", normalized)
        for receipt_hash in normalized:
            _require_hash(receipt_hash, "source receipt hash")
        if not isinstance(self.demo_loo_exact, bool):
            raise TypeError("demo_loo_exact must be a boolean")
        if self.uncompressed_description_bits < 0:
            raise ValueError("uncompressed description length must be nonnegative")

    def to_record(self) -> dict[str, object]:
        return {
            "source_receipt_hashes": list(self.source_receipt_hashes),
            "demo_loo_exact": self.demo_loo_exact,
            "uncompressed_description_bits": self.uncompressed_description_bits,
        }

    @classmethod
    def from_record(cls, raw: object) -> "AdmissionEvidence":
        record = _require_mapping(raw, "admission evidence")
        _exact_keys(
            record,
            {
                "source_receipt_hashes",
                "demo_loo_exact",
                "uncompressed_description_bits",
            },
            "admission evidence",
        )
        raw_loo = record["demo_loo_exact"]
        if not isinstance(raw_loo, bool):
            raise TypeError("demo_loo_exact must be a boolean")
        return cls(
            source_receipt_hashes=tuple(
                str(value)
                for value in _require_list(
                    record["source_receipt_hashes"], "source receipt hashes"
                )
            ),
            demo_loo_exact=raw_loo,
            uncompressed_description_bits=int(record["uncompressed_description_bits"]),
        )


@dataclass(frozen=True)
class AdmissionProposal:
    program: TypedProgramAST
    evidence: AdmissionEvidence

    @property
    def macro(self) -> MacroRecord:
        return MacroRecord(self.program)


def _evidence_failure(
    macro: MacroRecord,
    evidence: AdmissionEvidence,
    observations: Sequence[SealedObservation],
) -> Optional[str]:
    """Evaluate the portable admission gates against sealed prior evidence."""

    program_hash = macro.program_hash
    if macro.program.input_type != ValueType.GRID or macro.program.output_type != ValueType.GRID:
        return "macro_not_grid_to_grid"
    excluded = _excluded_step(macro.program)
    if excluded is not None:
        return excluded
    if not evidence.demo_loo_exact:
        return "demo_leave_one_out_not_exact"
    if evidence.uncompressed_description_bits <= macro.description_bits:
        return "nonpositive_description_compression"
    if len(evidence.source_receipt_hashes) < 2:
        return "insufficient_distinct_source_receipts"

    observation_by_receipt = {item.receipt_hash: item for item in observations}
    sources: list[SealedObservation] = []
    for receipt_hash in evidence.source_receipt_hashes:
        observation = observation_by_receipt.get(receipt_hash)
        if observation is None:
            return f"unknown_or_unrevealed_source_receipt:{receipt_hash}"
        if program_hash not in observation.receipt.committed_program_hashes:
            return f"program_not_pre_reveal_committed:{receipt_hash}"
        if program_hash not in observation.exact_program_hashes:
            return f"source_program_not_exact:{receipt_hash}"
        certificate = next(
            (
                item
                for item in observation.receipt.discovery_certificates
                if item.program_hash == program_hash
            ),
            None,
        )
        if certificate is None:
            return f"source_discovery_certificate_missing:{receipt_hash}"
        if certificate.source_content_hash != observation.receipt.source_content_hash:
            return f"source_discovery_certificate_source_mismatch:{receipt_hash}"
        if certificate.interpreter_contract != observation.receipt.interpreter_contract:
            return f"source_discovery_certificate_runtime_mismatch:{receipt_hash}"
        if not certificate.full_demo_exact:
            return f"source_discovery_not_full_exact:{receipt_hash}"
        if not certificate.demo_loo_exact:
            return f"source_discovery_loo_failed:{receipt_hash}"
        sources.append(observation)
    if len({item.receipt.source_content_hash for item in sources}) < 2:
        return "insufficient_distinct_source_content"
    if len({item.receipt.registry_contract for item in sources}) != 1:
        return "source_registry_contract_mismatch"
    if len({item.receipt.interpreter_contract for item in sources}) != 1:
        return "source_interpreter_contract_mismatch"
    return None


def _evidence_interpreter_contract(
    evidence: AdmissionEvidence,
    observations: Sequence[SealedObservation],
) -> str:
    """Return the unique runtime contract after successful evidence validation."""

    observation_by_receipt = {item.receipt_hash: item for item in observations}
    contracts = {
        observation_by_receipt[receipt_hash].receipt.interpreter_contract
        for receipt_hash in evidence.source_receipt_hashes
    }
    if len(contracts) != 1:
        raise RuntimeError("admission evidence has no unique interpreter contract")
    return next(iter(contracts))


@dataclass(frozen=True)
class LedgerEvent:
    event_number: int
    kind: str
    previous_head: str
    payload_json: str
    event_hash: str
    schema_version: int = LEARNING_BANK_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.schema_version != LEARNING_BANK_SCHEMA_VERSION:
            raise ValueError(f"unsupported ledger event version {self.schema_version}")
        if self.event_number < 0:
            raise ValueError("ledger event number must be nonnegative")
        if not self.kind:
            raise ValueError("ledger event kind must be nonempty")
        _require_hash(self.previous_head, "previous ledger head")
        _require_hash(self.event_hash, "ledger event hash")
        try:
            payload = json.loads(self.payload_json)
        except json.JSONDecodeError as error:
            raise ValueError("ledger payload must be valid JSON") from error
        if self.payload_json != _canonical_json(payload):
            raise ValueError("ledger payload JSON must be canonical")
        if self.event_hash != _record_hash(self._body_record()):
            raise ValueError("ledger event hash does not match its content")

    def _body_record(self) -> dict[str, object]:
        return {
            "schema": LEDGER_EVENT_SCHEMA,
            "schema_version": self.schema_version,
            "event_number": self.event_number,
            "kind": self.kind,
            "previous_head": self.previous_head,
            "payload": json.loads(self.payload_json),
        }

    @property
    def payload(self) -> object:
        return json.loads(self.payload_json)

    def to_record(self) -> dict[str, object]:
        return {**self._body_record(), "event_hash": self.event_hash}

    @classmethod
    def create(
        cls,
        *,
        event_number: int,
        kind: str,
        previous_head: str,
        payload: object,
    ) -> "LedgerEvent":
        payload_json = _canonical_json(payload)
        body = {
            "schema": LEDGER_EVENT_SCHEMA,
            "schema_version": LEARNING_BANK_SCHEMA_VERSION,
            "event_number": event_number,
            "kind": kind,
            "previous_head": previous_head,
            "payload": json.loads(payload_json),
        }
        return cls(
            event_number=event_number,
            kind=kind,
            previous_head=previous_head,
            payload_json=payload_json,
            event_hash=_record_hash(body),
        )

    @classmethod
    def from_record(cls, raw: object) -> "LedgerEvent":
        record = _require_mapping(raw, "ledger event")
        _exact_keys(
            record,
            {
                "schema",
                "schema_version",
                "event_number",
                "kind",
                "previous_head",
                "payload",
                "event_hash",
            },
            "ledger event",
        )
        if record["schema"] != LEDGER_EVENT_SCHEMA:
            raise ValueError(f"unknown ledger schema {record['schema']!r}")
        return cls(
            event_number=int(record["event_number"]),
            kind=str(record["kind"]),
            previous_head=str(record["previous_head"]),
            payload_json=_canonical_json(record["payload"]),
            event_hash=str(record["event_hash"]),
            schema_version=int(record["schema_version"]),
        )


GENESIS_LEDGER_HEAD = _record_hash(
    {
        "schema": LEARNING_BANK_SCHEMA,
        "schema_version": LEARNING_BANK_SCHEMA_VERSION,
        "genesis": True,
    }
)


@dataclass(frozen=True)
class BankEntry:
    macro: MacroRecord
    admitted_after_sequence: int
    interpreter_contract: str
    admission_event_hash: str

    def __post_init__(self) -> None:
        if self.admitted_after_sequence < 0:
            raise ValueError("macro admission sequence must be nonnegative")
        _require_hash(self.interpreter_contract, "admitted interpreter contract")
        _require_hash(self.admission_event_hash, "admission event hash")

    def to_record(self) -> dict[str, object]:
        return {
            "macro": self.macro.to_record(),
            "admitted_after_sequence": self.admitted_after_sequence,
            "interpreter_contract": self.interpreter_contract,
            "admission_event_hash": self.admission_event_hash,
        }

    @classmethod
    def from_record(cls, raw: object) -> "BankEntry":
        record = _require_mapping(raw, "bank entry")
        _exact_keys(
            record,
            {
                "macro",
                "admitted_after_sequence",
                "interpreter_contract",
                "admission_event_hash",
            },
            "bank entry",
        )
        return cls(
            macro=MacroRecord.from_record(record["macro"]),
            admitted_after_sequence=int(record["admitted_after_sequence"]),
            interpreter_contract=str(record["interpreter_contract"]),
            admission_event_hash=str(record["admission_event_hash"]),
        )


@dataclass(frozen=True)
class QueryOpening:
    receipt: QueryReceipt
    active_macros: tuple[MacroRecord, ...]

    @property
    def abstentions(self) -> tuple[ResolutionAbstention, ...]:
        return self.receipt.abstentions


def resolve_active_bank_entries(
    entries: Sequence[BankEntry],
    *,
    sequence_index: int,
    registry: PrimitiveRegistry,
    interpreter_contract: str,
) -> tuple[tuple[MacroRecord, ...], tuple[ResolutionAbstention, ...]]:
    """Resolve the exact bank view available at one pre-reveal query.

    Keeping this policy in one function lets both query creation and the
    prediction-time snapshot verifier recompute the active-macro commitment.
    """

    _require_hash(interpreter_contract, "interpreter contract")
    active: list[MacroRecord] = []
    abstentions: list[ResolutionAbstention] = []
    for entry in entries:
        macro_hash = entry.macro.content_hash()
        if entry.admitted_after_sequence >= sequence_index:
            abstentions.append(
                ResolutionAbstention(
                    "bank_macro", macro_hash, "not_strictly_later_than_admission"
                )
            )
            continue
        if entry.interpreter_contract != interpreter_contract:
            abstentions.append(
                ResolutionAbstention(
                    "bank_macro", macro_hash, "interpreter_contract_mismatch"
                )
            )
            continue
        failure = _resolution_failure(entry.macro.program, registry)
        if failure is None:
            active.append(entry.macro)
        else:
            abstentions.append(
                ResolutionAbstention("bank_macro", macro_hash, failure)
            )
    active.sort(key=lambda macro: macro.content_hash())
    abstentions.sort(
        key=lambda item: (item.subject_kind, item.subject_hash, item.reason)
    )
    return tuple(active), tuple(abstentions)


@dataclass(frozen=True)
class AdmissionDecision:
    macro_hash: str
    accepted: bool
    reason: str
    admission_event_hash: Optional[str] = None


@dataclass(frozen=True)
class UpdateResult:
    observation: SealedObservation
    decisions: tuple[AdmissionDecision, ...]


@dataclass(frozen=True)
class MacroBank:
    """Immutable state of a strictly ordered prequential learning stream."""

    mode: BankMode = BankMode.LEARNING
    next_sequence_index: int = 0
    entries: tuple[BankEntry, ...] = ()
    observations: tuple[SealedObservation, ...] = ()
    ledger: tuple[LedgerEvent, ...] = ()
    pending: Optional[QueryReceipt] = None
    schema_version: int = LEARNING_BANK_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.schema_version != LEARNING_BANK_SCHEMA_VERSION:
            raise ValueError(f"unsupported macro bank version {self.schema_version}")
        if self.next_sequence_index < 0:
            raise ValueError("next sequence index must be nonnegative")
        if self.mode == BankMode.RESTART_CONTROL and self.entries:
            raise ValueError("restart-control banks must remain empty")
        macro_hashes = tuple(entry.macro.content_hash() for entry in self.entries)
        if tuple(sorted(set(macro_hashes))) != macro_hashes:
            raise ValueError("bank entries must have unique, sorted macro hashes")
        for entry in self.entries:
            if entry.admitted_after_sequence >= self.next_sequence_index:
                raise ValueError("a macro cannot be admitted at a future sequence")
        receipt_hashes = tuple(item.receipt_hash for item in self.observations)
        if len(set(receipt_hashes)) != len(receipt_hashes):
            raise ValueError("a query receipt cannot be revealed more than once")
        observation_indices = tuple(
            item.receipt.sequence_index for item in self.observations
        )
        if tuple(sorted(observation_indices)) != observation_indices:
            raise ValueError("sealed observations must be in sequence order")
        if any(
            item.receipt.sequence_index >= self.next_sequence_index
            for item in self.observations
        ):
            raise ValueError("sealed observations must precede the next query")
        previous = GENESIS_LEDGER_HEAD
        for number, event in enumerate(self.ledger):
            if event.event_number != number:
                raise ValueError("ledger event numbers must be contiguous")
            if event.previous_head != previous:
                raise ValueError("ledger event chain is broken")
            previous = event.event_hash
        event_hashes = {event.event_hash for event in self.ledger}
        if any(entry.admission_event_hash not in event_hashes for entry in self.entries):
            raise ValueError("bank entry is missing its admission ledger event")

        query_events: dict[str, tuple[QueryReceipt, LedgerEvent]] = {}
        reveal_events: dict[str, tuple[SealedObservation, LedgerEvent]] = {}
        admission_events: dict[
            str, tuple[MacroRecord, AdmissionEvidence, int, str, LedgerEvent]
        ] = {}
        for event in self.ledger:
            if event.kind == "query_opened":
                receipt = QueryReceipt.from_record(event.payload)
                receipt_hash = receipt.content_hash()
                if receipt_hash in query_events:
                    raise ValueError("duplicate query receipt ledger event")
                if receipt.bank_head_before != event.previous_head:
                    raise ValueError("query receipt does not commit its prior ledger head")
                if receipt.mode != self.mode:
                    raise ValueError("query receipt mode does not match its bank")
                query_events[receipt_hash] = (receipt, event)
            elif event.kind == "label_revealed":
                observation = SealedObservation.from_record(event.payload)
                receipt_hash = observation.receipt_hash
                if receipt_hash in reveal_events:
                    raise ValueError("duplicate reveal ledger event")
                reveal_events[receipt_hash] = (observation, event)
            elif event.kind == "macro_admitted":
                payload = _require_mapping(event.payload, "macro admission payload")
                _exact_keys(
                    payload,
                    {
                        "macro",
                        "macro_hash",
                        "admitted_after_sequence",
                        "interpreter_contract",
                        "evidence",
                    },
                    "macro admission payload",
                )
                macro = MacroRecord.from_record(payload["macro"])
                macro_hash = _require_hash(payload["macro_hash"], "macro hash")
                if macro.content_hash() != macro_hash:
                    raise ValueError("admission macro hash does not match its record")
                if event.event_hash in admission_events:
                    raise ValueError("duplicate admission ledger event")
                evidence = AdmissionEvidence.from_record(payload["evidence"])
                interpreter_contract = _require_hash(
                    payload["interpreter_contract"], "admitted interpreter contract"
                )
                admission_events[event.event_hash] = (
                    macro,
                    evidence,
                    int(payload["admitted_after_sequence"]),
                    interpreter_contract,
                    event,
                )
            else:
                raise ValueError(f"unknown learning ledger event kind {event.kind!r}")

        query_indices = tuple(
            receipt.sequence_index
            for receipt, _ in sorted(
                query_events.values(), key=lambda pair: pair[1].event_number
            )
        )
        if query_indices:
            expected_indices = tuple(
                range(query_indices[0], query_indices[0] + len(query_indices))
            )
            if query_indices != expected_indices:
                raise ValueError("query ledger sequence indices must be contiguous")
        if set(reveal_events) - set(query_events):
            raise ValueError("reveal ledger event has no pre-reveal query event")
        serialized_observations = {
            item.receipt_hash: item.to_record() for item in self.observations
        }
        ledger_observations = {
            receipt_hash: item.to_record()
            for receipt_hash, (item, _) in reveal_events.items()
        }
        if serialized_observations != ledger_observations:
            raise ValueError("serialized observations do not match reveal ledger events")
        for receipt_hash, (observation, reveal_event) in reveal_events.items():
            query_receipt, query_event = query_events[receipt_hash]
            if observation.receipt != query_receipt:
                raise ValueError("reveal embeds a different pre-reveal receipt")
            if reveal_event.event_number != query_event.event_number + 1:
                raise ValueError("a reveal must immediately follow its query receipt")

        entry_by_event = {entry.admission_event_hash: entry for entry in self.entries}
        if set(entry_by_event) != set(admission_events):
            raise ValueError("bank entries do not match admission ledger events")
        for event_hash, entry in entry_by_event.items():
            (
                macro,
                evidence,
                admitted_after,
                interpreter_contract,
                event,
            ) = admission_events[event_hash]
            if (
                entry.macro != macro
                or entry.admitted_after_sequence != admitted_after
                or entry.interpreter_contract != interpreter_contract
            ):
                raise ValueError("bank entry differs from its admission ledger event")
            source_observations = tuple(
                observation
                for observation, reveal_event in reveal_events.values()
                if reveal_event.event_number < event.event_number
            )
            if not any(
                reveal_event.event_number < event.event_number
                and observation.receipt.sequence_index == admitted_after
                for observation, reveal_event in reveal_events.values()
            ):
                raise ValueError("macro admission has no preceding same-sequence reveal")
            policy_failure = _evidence_failure(macro, evidence, source_observations)
            if policy_failure is not None:
                raise ValueError(
                    "admission ledger evidence violates policy: " + policy_failure
                )
            evidence_contract = _evidence_interpreter_contract(
                evidence, source_observations
            )
            if interpreter_contract != evidence_contract:
                raise ValueError(
                    "bank entry interpreter contract differs from its source evidence"
                )

        unmatched_queries = set(query_events) - set(reveal_events)
        if self.pending is not None:
            if self.pending.sequence_index != self.next_sequence_index:
                raise ValueError("pending query must occupy the next sequence index")
            if unmatched_queries != {self.pending.content_hash()}:
                raise ValueError("pending query does not match the unrevealed ledger query")
            if self.pending.content_hash() not in query_events:
                raise ValueError("pending query has no ledger event")
            pending_event = query_events[self.pending.content_hash()][1]
            if not self.ledger or pending_event != self.ledger[-1]:
                raise ValueError("pending query must be the final ledger event")
        elif unmatched_queries:
            raise ValueError("ledger contains an unrevealed query without pending state")

    @classmethod
    def empty(
        cls,
        *,
        mode: BankMode = BankMode.LEARNING,
        next_sequence_index: int = 0,
    ) -> "MacroBank":
        return cls(mode=mode, next_sequence_index=next_sequence_index)

    @property
    def ledger_head(self) -> str:
        return self.ledger[-1].event_hash if self.ledger else GENESIS_LEDGER_HEAD

    def content_hash(self) -> str:
        return _record_hash(self.to_record())

    def _append_event(self, kind: str, payload: object) -> tuple[LedgerEvent, ...]:
        event = LedgerEvent.create(
            event_number=len(self.ledger),
            kind=kind,
            previous_head=self.ledger_head,
            payload=payload,
        )
        return self.ledger + (event,)

    def begin_query(
        self,
        *,
        source_content_hash: str,
        registry: PrimitiveRegistry,
        interpreter_contract: str,
        pre_reveal_programs: Iterable[TypedProgramAST] = (),
        discovery_certificates: Iterable[ProgramDiscoveryCertificate] = (),
    ) -> tuple["MacroBank", QueryOpening]:
        """Seal all prediction-time information before any label is accepted.

        ``interpreter_contract`` is a required caller-maintained digest of the
        executable runtime semantics, build, and primitive implementations.
        It is intentionally separate from the automatically derived symbolic
        registry contract, which covers only names and type signatures.
        """

        if self.pending is not None:
            raise RuntimeError("the pending query must be revealed before opening another")
        _require_hash(source_content_hash, "source content hash")
        _require_hash(interpreter_contract, "interpreter contract")
        registry_hash = registry_contract_hash(registry)
        active, bank_abstentions = resolve_active_bank_entries(
            self.entries,
            sequence_index=self.next_sequence_index,
            registry=registry,
            interpreter_contract=interpreter_contract,
        )
        abstentions: list[ResolutionAbstention] = list(bank_abstentions)

        proposals_by_hash: dict[str, TypedProgramAST] = {}
        for program in pre_reveal_programs:
            if not isinstance(program, TypedProgramAST):
                raise TypeError("pre-reveal programs must be TypedProgramAST values")
            proposals_by_hash[program.content_hash()] = program
        committed = {macro.program_hash for macro in active}
        for program_hash, program in sorted(proposals_by_hash.items()):
            failure = _resolution_failure(program, registry)
            if failure is None:
                committed.add(program_hash)
            else:
                abstentions.append(
                    ResolutionAbstention("pre_reveal_program", program_hash, failure)
                )

        certificates_by_program: dict[str, ProgramDiscoveryCertificate] = {}
        for certificate in discovery_certificates:
            if not isinstance(certificate, ProgramDiscoveryCertificate):
                raise TypeError(
                    "discovery certificates must be ProgramDiscoveryCertificate values"
                )
            program_hash = certificate.program_hash
            if program_hash not in proposals_by_hash:
                raise ValueError(
                    "a discovery certificate must refer to a supplied pre-reveal program"
                )
            if program_hash not in committed:
                raise ValueError(
                    "a discovery certificate cannot authorize an unresolved program"
                )
            if certificate.source_content_hash != source_content_hash:
                raise ValueError(
                    "discovery certificate source differs from the opened query"
                )
            if certificate.interpreter_contract != interpreter_contract:
                raise ValueError(
                    "discovery certificate interpreter differs from the opened query"
                )
            if program_hash in certificates_by_program:
                raise ValueError(
                    f"duplicate discovery certificate for program {program_hash}"
                )
            certificates_by_program[program_hash] = certificate

        abstentions.sort(
            key=lambda item: (item.subject_kind, item.subject_hash, item.reason)
        )
        receipt = QueryReceipt(
            sequence_index=self.next_sequence_index,
            source_content_hash=source_content_hash,
            bank_head_before=self.ledger_head,
            registry_contract=registry_hash,
            interpreter_contract=interpreter_contract,
            mode=self.mode,
            active_macro_hashes=tuple(macro.content_hash() for macro in active),
            committed_program_hashes=tuple(sorted(committed)),
            abstentions=tuple(abstentions),
            discovery_certificates=tuple(
                certificates_by_program[key]
                for key in sorted(certificates_by_program)
            ),
        )
        ledger = self._append_event("query_opened", receipt.to_record())
        opened = MacroBank(
            mode=self.mode,
            next_sequence_index=self.next_sequence_index,
            entries=self.entries,
            observations=self.observations,
            ledger=ledger,
            pending=receipt,
        )
        return opened, QueryOpening(receipt=receipt, active_macros=active)

    def _admission_failure(
        self,
        proposal: AdmissionProposal,
        observations: Sequence[SealedObservation],
        existing_macro_hashes: set[str],
    ) -> Optional[str]:
        macro = proposal.macro
        macro_hash = macro.content_hash()
        if self.mode == BankMode.RESTART_CONTROL:
            return "restart_control_never_admits"
        if macro_hash in existing_macro_hashes:
            return "duplicate_macro"
        return _evidence_failure(macro, proposal.evidence, observations)

    def reveal_and_update(
        self,
        *,
        receipt_hash: str,
        label_content_hash: str,
        exact_program_hashes: Iterable[str],
        proposals: Iterable[AdmissionProposal] = (),
    ) -> tuple["MacroBank", UpdateResult]:
        """Seal a label, then consider macros for use on strictly later tasks."""

        if self.pending is None:
            raise RuntimeError("no pending pre-reveal query exists")
        _require_hash(receipt_hash, "receipt hash")
        if receipt_hash != self.pending.content_hash():
            raise ValueError("receipt hash does not match the pending query")
        _require_hash(label_content_hash, "label content hash")
        normalized_exact = tuple(sorted(set(exact_program_hashes)))
        for program_hash in normalized_exact:
            _require_hash(program_hash, "exact program hash")
        observation = SealedObservation(
            receipt=self.pending,
            label_content_hash=label_content_hash,
            exact_program_hashes=normalized_exact,
        )
        observations = self.observations + (observation,)
        ledger = self._append_event("label_revealed", observation.to_record())

        proposals_by_macro: dict[str, AdmissionProposal] = {}
        for proposal in proposals:
            if not isinstance(proposal, AdmissionProposal):
                raise TypeError("admission proposals must be AdmissionProposal values")
            macro_hash = proposal.macro.content_hash()
            if macro_hash in proposals_by_macro:
                raise ValueError(f"duplicate admission proposal {macro_hash}")
            proposals_by_macro[macro_hash] = proposal

        entries = list(self.entries)
        existing_hashes = {entry.macro.content_hash() for entry in entries}
        decisions: list[AdmissionDecision] = []
        for macro_hash, proposal in sorted(proposals_by_macro.items()):
            failure = self._admission_failure(
                proposal, observations, existing_hashes
            )
            if failure is not None:
                decisions.append(AdmissionDecision(macro_hash, False, failure))
                continue
            interpreter_contract = _evidence_interpreter_contract(
                proposal.evidence, observations
            )
            event = LedgerEvent.create(
                event_number=len(ledger),
                kind="macro_admitted",
                previous_head=ledger[-1].event_hash if ledger else GENESIS_LEDGER_HEAD,
                payload={
                    "macro": proposal.macro.to_record(),
                    "macro_hash": macro_hash,
                    "admitted_after_sequence": self.pending.sequence_index,
                    "interpreter_contract": interpreter_contract,
                    "evidence": proposal.evidence.to_record(),
                },
            )
            ledger = ledger + (event,)
            entries.append(
                BankEntry(
                    macro=proposal.macro,
                    admitted_after_sequence=self.pending.sequence_index,
                    interpreter_contract=interpreter_contract,
                    admission_event_hash=event.event_hash,
                )
            )
            existing_hashes.add(macro_hash)
            decisions.append(
                AdmissionDecision(
                    macro_hash,
                    True,
                    "admitted_for_strictly_later_queries",
                    event.event_hash,
                )
            )
        entries.sort(key=lambda entry: entry.macro.content_hash())
        updated = MacroBank(
            mode=self.mode,
            next_sequence_index=self.next_sequence_index + 1,
            entries=tuple(entries),
            observations=observations,
            ledger=ledger,
            pending=None,
        )
        return updated, UpdateResult(observation, tuple(decisions))

    def restart_empty(
        self, *, mode: BankMode = BankMode.RESTART_CONTROL
    ) -> "MacroBank":
        """Drop all learned state while preserving the stream position.

        ``RESTART_CONTROL`` is the negative-control default.  Such a bank still
        produces query and reveal receipts but rejects every admission, so it
        remains empty for the rest of the stream.
        """

        if self.pending is not None:
            raise RuntimeError("cannot restart while a query is pending")
        return MacroBank.empty(mode=mode, next_sequence_index=self.next_sequence_index)

    def to_record(self) -> dict[str, object]:
        return {
            "schema": LEARNING_BANK_SCHEMA,
            "schema_version": self.schema_version,
            "mode": self.mode.value,
            "next_sequence_index": self.next_sequence_index,
            "entries": [entry.to_record() for entry in self.entries],
            "observations": [item.to_record() for item in self.observations],
            "ledger": [event.to_record() for event in self.ledger],
            "pending": self.pending.to_record() if self.pending is not None else None,
        }

    def to_json(self) -> str:
        return _canonical_json(self.to_record())

    @classmethod
    def from_record(cls, raw: object) -> "MacroBank":
        record = _require_mapping(raw, "macro bank")
        _exact_keys(
            record,
            {
                "schema",
                "schema_version",
                "mode",
                "next_sequence_index",
                "entries",
                "observations",
                "ledger",
                "pending",
            },
            "macro bank",
        )
        if record["schema"] != LEARNING_BANK_SCHEMA:
            raise ValueError(f"unknown macro bank schema {record['schema']!r}")
        pending_raw = record["pending"]
        return cls(
            mode=BankMode(str(record["mode"])),
            next_sequence_index=int(record["next_sequence_index"]),
            entries=tuple(
                BankEntry.from_record(value)
                for value in _require_list(record["entries"], "bank entries")
            ),
            observations=tuple(
                SealedObservation.from_record(value)
                for value in _require_list(record["observations"], "observations")
            ),
            ledger=tuple(
                LedgerEvent.from_record(value)
                for value in _require_list(record["ledger"], "ledger")
            ),
            pending=(
                None if pending_raw is None else QueryReceipt.from_record(pending_raw)
            ),
            schema_version=int(record["schema_version"]),
        )

    @classmethod
    def from_json(cls, payload: str) -> "MacroBank":
        return cls.from_record(json.loads(payload))


__all__ = [
    "AdmissionDecision",
    "AdmissionEvidence",
    "AdmissionProposal",
    "BankEntry",
    "BankMode",
    "GENESIS_LEDGER_HEAD",
    "LEARNING_BANK_SCHEMA",
    "LEARNING_BANK_SCHEMA_VERSION",
    "LedgerEvent",
    "MacroBank",
    "MacroRecord",
    "ProgramDiscoveryCertificate",
    "QueryOpening",
    "QueryReceipt",
    "ResolutionAbstention",
    "SealedObservation",
    "UpdateResult",
    "content_hash_text",
    "registry_contract_hash",
    "resolve_active_bank_entries",
]
