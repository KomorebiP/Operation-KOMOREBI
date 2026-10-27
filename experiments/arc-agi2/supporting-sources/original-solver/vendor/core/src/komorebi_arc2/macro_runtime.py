"""Read-only runtime snapshots for leakage-resistant persistent ARC macros.

This module is the bridge between :mod:`learning_bank` and the frozen solver.
A prequential controller opens and seals a bank query before a held-out output is
revealed.  The resulting :class:`LearnerSnapshot` can then be supplied to
``solve_task``.  The solver may execute only the macros committed by that
snapshot and never mutates learning state during inference.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Mapping, Sequence

import numpy as np

from .learning_bank import (
    BankEntry,
    MacroBank,
    MacroRecord,
    QueryOpening,
    QueryReceipt,
    registry_contract_hash,
    resolve_active_bank_entries,
)
from .program_ast import PrimitiveRegistry, TypedProgramInterpreter

SNAPSHOT_SCHEMA = "komorebi.arc2.learner_snapshot"
SNAPSHOT_SCHEMA_VERSION = 2


class MacroCandidateLimitError(RuntimeError):
    """Raised when exact active macro behaviors exceed the audited cap."""


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _content_hash(value: object) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _require_hash(value: object, field: str) -> str:
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise ValueError(f"{field} must be a lowercase SHA-256 digest")
    return value


def _grid_record(value: object) -> list[list[int]]:
    array = np.asarray(value)
    if array.ndim != 2 or array.size == 0:
        raise ValueError("ARC grids must be nonempty and two dimensional")
    return [[int(cell) for cell in row] for row in array.tolist()]


def task_source_record(task: Mapping[str, object]) -> dict[str, object]:
    """Return the prediction-time portion of one ARC task.

    Training outputs are available to an ARC solver and therefore belong in the
    source record.  Test outputs are deliberately discarded even when a local
    debugging task contains them.
    """

    raw_train = task.get("train", [])
    raw_test = task.get("test", [])
    if not isinstance(raw_train, list) or not isinstance(raw_test, list):
        raise TypeError("ARC task train and test fields must be lists")
    train: list[dict[str, object]] = []
    for index, raw in enumerate(raw_train):
        if not isinstance(raw, Mapping) or "input" not in raw or "output" not in raw:
            raise ValueError(f"training record {index} lacks input or output")
        train.append(
            {
                "input": _grid_record(raw["input"]),
                "output": _grid_record(raw["output"]),
            }
        )
    tests: list[dict[str, object]] = []
    for index, raw in enumerate(raw_test):
        if not isinstance(raw, Mapping) or "input" not in raw:
            raise ValueError(f"test record {index} lacks input")
        tests.append({"input": _grid_record(raw["input"])})
    return {"train": train, "test": tests}


def task_source_content_hash(task: Mapping[str, object]) -> str:
    return _content_hash(task_source_record(task))


@dataclass(frozen=True)
class SnapshotMacro:
    """One admitted macro together with its proof-carrying lineage edge."""

    macro: MacroRecord
    admitted_after_sequence: int
    interpreter_contract: str
    admission_event_hash: str

    def __post_init__(self) -> None:
        if not isinstance(self.macro, MacroRecord):
            raise TypeError("snapshot macro must contain a MacroRecord")
        if self.admitted_after_sequence < 0:
            raise ValueError("admission sequence must be nonnegative")
        _require_hash(self.interpreter_contract, "interpreter contract")
        _require_hash(self.admission_event_hash, "admission event hash")

    @classmethod
    def from_entry(cls, entry: BankEntry) -> "SnapshotMacro":
        return cls(
            macro=entry.macro,
            admitted_after_sequence=entry.admitted_after_sequence,
            interpreter_contract=entry.interpreter_contract,
            admission_event_hash=entry.admission_event_hash,
        )

    def to_record(self) -> dict[str, object]:
        return {
            "macro": self.macro.to_record(),
            "admitted_after_sequence": self.admitted_after_sequence,
            "interpreter_contract": self.interpreter_contract,
            "admission_event_hash": self.admission_event_hash,
        }

    @classmethod
    def from_record(cls, raw: object) -> "SnapshotMacro":
        if not isinstance(raw, Mapping):
            raise TypeError("snapshot macro must be a mapping")
        expected = {
            "macro",
            "admitted_after_sequence",
            "interpreter_contract",
            "admission_event_hash",
        }
        if set(raw) != expected:
            raise ValueError("snapshot macro fields do not match the schema")
        return cls(
            macro=MacroRecord.from_record(raw["macro"]),
            admitted_after_sequence=int(raw["admitted_after_sequence"]),
            interpreter_contract=str(raw["interpreter_contract"]),
            admission_event_hash=str(raw["admission_event_hash"]),
        )


@dataclass(frozen=True)
class LearnerSnapshot:
    """Immutable prediction-time view of one opened prequential bank query."""

    receipt: QueryReceipt
    macros: tuple[SnapshotMacro, ...]
    bank_proof: MacroBank
    schema_version: int = SNAPSHOT_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.schema_version != SNAPSHOT_SCHEMA_VERSION:
            raise ValueError(f"unsupported learner snapshot version {self.schema_version}")
        if not isinstance(self.receipt, QueryReceipt):
            raise TypeError("snapshot receipt must be a QueryReceipt")
        if not isinstance(self.bank_proof, MacroBank):
            raise TypeError("snapshot bank proof must be a MacroBank")
        if self.bank_proof.pending != self.receipt:
            raise ValueError("snapshot bank proof does not contain its pending receipt")
        if self.bank_proof.next_sequence_index != self.receipt.sequence_index:
            raise ValueError("snapshot bank proof sequence differs from its receipt")
        ordered = tuple(sorted(self.macros, key=lambda item: item.macro.content_hash()))
        if ordered != self.macros:
            raise ValueError("snapshot macros must be sorted by macro hash")
        hashes = tuple(item.macro.content_hash() for item in self.macros)
        if len(set(hashes)) != len(hashes):
            raise ValueError("snapshot macro hashes must be unique")
        if hashes != self.receipt.active_macro_hashes:
            raise ValueError("snapshot macros do not match the receipt active-macro commitment")
        for item in self.macros:
            if item.admitted_after_sequence >= self.receipt.sequence_index:
                raise ValueError("snapshot contains a macro not admitted strictly earlier")
            if item.interpreter_contract != self.receipt.interpreter_contract:
                raise ValueError("snapshot macro interpreter contract differs from query receipt")
        entries_by_hash = {
            entry.macro.content_hash(): entry for entry in self.bank_proof.entries
        }
        for item in self.macros:
            entry = entries_by_hash.get(item.macro.content_hash())
            if entry is None or item != SnapshotMacro.from_entry(entry):
                raise ValueError(
                    "snapshot macro is not backed by its validated bank admission ledger"
                )

    @property
    def sequence_index(self) -> int:
        return self.receipt.sequence_index

    @property
    def source_content_hash(self) -> str:
        return self.receipt.source_content_hash

    def to_record(self) -> dict[str, object]:
        return {
            "schema": SNAPSHOT_SCHEMA,
            "schema_version": self.schema_version,
            "receipt": self.receipt.to_record(),
            "macros": [item.to_record() for item in self.macros],
            "bank_proof": self.bank_proof.to_record(),
        }

    def to_json(self) -> str:
        return _canonical_json(self.to_record())

    def content_hash(self) -> str:
        return hashlib.sha256(self.to_json().encode("utf-8")).hexdigest()

    @classmethod
    def from_record(cls, raw: object) -> "LearnerSnapshot":
        if not isinstance(raw, Mapping):
            raise TypeError("learner snapshot must be a mapping")
        expected = {"schema", "schema_version", "receipt", "macros", "bank_proof"}
        if set(raw) != expected:
            raise ValueError("learner snapshot fields do not match the schema")
        if raw["schema"] != SNAPSHOT_SCHEMA:
            raise ValueError(f"unknown learner snapshot schema {raw['schema']!r}")
        raw_macros = raw["macros"]
        if not isinstance(raw_macros, list):
            raise TypeError("learner snapshot macros must be a list")
        return cls(
            receipt=QueryReceipt.from_record(raw["receipt"]),
            macros=tuple(SnapshotMacro.from_record(item) for item in raw_macros),
            bank_proof=MacroBank.from_record(raw["bank_proof"]),
            schema_version=int(raw["schema_version"]),
        )

    @classmethod
    def from_json(cls, payload: str) -> "LearnerSnapshot":
        return cls.from_record(json.loads(payload))

    @classmethod
    def from_opened_bank(
        cls,
        opened_bank: MacroBank,
        opening: QueryOpening,
    ) -> "LearnerSnapshot":
        if opened_bank.pending != opening.receipt:
            raise ValueError("opened bank and query opening do not share a pending receipt")
        active = set(opening.receipt.active_macro_hashes)
        entries = {
            entry.macro.content_hash(): entry
            for entry in opened_bank.entries
            if entry.macro.content_hash() in active
        }
        if set(entries) != active:
            raise ValueError("opened bank does not contain every active committed macro")
        macros = tuple(
            SnapshotMacro.from_entry(entries[macro_hash])
            for macro_hash in opening.receipt.active_macro_hashes
        )
        return cls(
            receipt=opening.receipt,
            macros=macros,
            bank_proof=opened_bank,
        )

    def validate_runtime(
        self,
        *,
        source_content_hash: str,
        registry: PrimitiveRegistry,
        interpreter_contract: str,
    ) -> None:
        _require_hash(source_content_hash, "source content hash")
        _require_hash(interpreter_contract, "interpreter contract")
        if source_content_hash != self.receipt.source_content_hash:
            raise ValueError("learner snapshot belongs to a different ARC task source")
        if interpreter_contract != self.receipt.interpreter_contract:
            raise ValueError("learner snapshot interpreter contract mismatch")
        if registry_contract_hash(registry) != self.receipt.registry_contract:
            raise ValueError("learner snapshot primitive registry contract mismatch")
        active, bank_abstentions = resolve_active_bank_entries(
            self.bank_proof.entries,
            sequence_index=self.receipt.sequence_index,
            registry=registry,
            interpreter_contract=interpreter_contract,
        )
        expected_active_hashes = tuple(macro.content_hash() for macro in active)
        if expected_active_hashes != self.receipt.active_macro_hashes:
            raise ValueError(
                "learner snapshot active-macro commitment is not the resolved bank view"
            )
        receipt_bank_abstentions = tuple(
            item
            for item in self.receipt.abstentions
            if item.subject_kind == "bank_macro"
        )
        if bank_abstentions != receipt_bank_abstentions:
            raise ValueError(
                "learner snapshot bank abstentions are not the resolved bank view"
            )
        entry_by_hash = {
            item.macro.content_hash(): item for item in self.bank_proof.entries
        }
        expected_macros = tuple(
            SnapshotMacro.from_entry(entry_by_hash[macro_hash])
            for macro_hash in expected_active_hashes
        )
        if self.macros != expected_macros:
            raise ValueError(
                "learner snapshot macros are not the complete resolved bank view"
            )


@dataclass(frozen=True)
class MaterializedMacroCandidate:
    """One active macro that exactly replays every current demonstration."""

    macro_hash: str
    program_hash: str
    name: str
    description_bits: int
    train_grids: tuple[np.ndarray, ...]
    test_grids: tuple[np.ndarray, ...]
    metadata: Mapping[str, object]


def materialize_snapshot_macros(
    snapshot: LearnerSnapshot,
    interpreter: TypedProgramInterpreter,
    train: Sequence[tuple[np.ndarray, np.ndarray]],
    tests: Sequence[np.ndarray],
    *,
    maximum: int = 8,
) -> tuple[MaterializedMacroCandidate, ...]:
    """Execute active macros and retain only exact current-demo candidates."""

    if maximum < 0:
        raise ValueError("maximum macro candidates must be nonnegative")
    materialized: list[MaterializedMacroCandidate] = []
    for item in snapshot.macros:
        program = item.macro.program
        try:
            train_predictions = tuple(
                np.asarray(interpreter.execute(program, source), dtype=np.int16)
                for source, _ in train
            )
            if not all(
                np.array_equal(prediction, np.asarray(target, dtype=np.int16))
                for prediction, (_, target) in zip(train_predictions, train)
            ):
                continue
            if train and all(
                np.array_equal(prediction, np.asarray(source, dtype=np.int16))
                for prediction, (source, _) in zip(train_predictions, train)
            ):
                continue
            test_predictions = tuple(
                np.asarray(interpreter.execute(program, source), dtype=np.int16)
                for source in tests
            )
        except (KeyError, TypeError, ValueError):
            continue
        macro_hash = item.macro.content_hash()
        materialized.append(
            MaterializedMacroCandidate(
                macro_hash=macro_hash,
                program_hash=item.macro.program_hash,
                name=f"learned_macro:{item.macro.program_hash[:16]}",
                description_bits=item.macro.description_bits,
                train_grids=train_predictions,
                test_grids=test_predictions,
                metadata={
                    "source": "prequential_macro_bank",
                    "snapshot_hash": snapshot.content_hash(),
                    "query_receipt_hash": snapshot.receipt.content_hash(),
                    "sequence_index": snapshot.sequence_index,
                    "macro_hash": macro_hash,
                    "program_hash": item.macro.program_hash,
                    "admitted_after_sequence": item.admitted_after_sequence,
                    "admission_event_hash": item.admission_event_hash,
                    "exact_current_demonstrations": True,
                    "read_only_inference": True,
                },
            )
        )
    materialized.sort(
        key=lambda candidate: (
            candidate.description_bits,
            candidate.program_hash,
            candidate.macro_hash,
        )
    )
    deduplicated: list[MaterializedMacroCandidate] = []
    seen: set[tuple[tuple[int, int, bytes], ...]] = set()
    for candidate in materialized:
        signature = tuple(
            (int(grid.shape[0]), int(grid.shape[1]), grid.tobytes())
            for grid in candidate.test_grids
        )
        if signature in seen:
            continue
        seen.add(signature)
        deduplicated.append(candidate)
    if len(deduplicated) > maximum:
        raise MacroCandidateLimitError(
            "exact active macro behaviors exceed the configured cap: "
            f"{len(deduplicated)} > {maximum}"
        )
    return tuple(deduplicated)


__all__ = [
    "LearnerSnapshot",
    "MacroCandidateLimitError",
    "MaterializedMacroCandidate",
    "SNAPSHOT_SCHEMA",
    "SNAPSHOT_SCHEMA_VERSION",
    "SnapshotMacro",
    "materialize_snapshot_macros",
    "task_source_content_hash",
    "task_source_record",
]
