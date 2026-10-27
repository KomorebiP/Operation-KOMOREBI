"""Behavioral quotienting for typed LASM programs."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, is_dataclass
from typing import Iterable, Mapping, Sequence

import numpy as np

from .interpreter import Interpreter
from .program import Program


def canonical_runtime_record(value: object) -> object:
    if isinstance(value, np.ndarray):
        array = np.asarray(value)
        return {
            "kind": "ndarray",
            "dtype": str(array.dtype),
            "shape": [int(item) for item in array.shape],
            "data": array.tolist(),
        }
    if isinstance(value, np.generic):
        return value.item()
    if is_dataclass(value):
        return {
            "kind": f"dataclass:{type(value).__module__}.{type(value).__qualname__}",
            "fields": canonical_runtime_record(asdict(value)),
        }
    if isinstance(value, Mapping):
        return {
            str(key): canonical_runtime_record(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, (tuple, list)):
        return [canonical_runtime_record(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise TypeError(f"runtime value is not canonically encodable: {type(value)!r}")


def runtime_hash(value: object) -> str:
    payload = json.dumps(
        canonical_runtime_record(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class BehaviorSignature:
    output_type: str
    input_count: int
    output_hashes: tuple[str, ...]
    behavior_hash: str

    @classmethod
    def from_values(cls, output_type: str, values: Sequence[object]) -> "BehaviorSignature":
        hashes = tuple(runtime_hash(value) for value in values)
        payload = json.dumps(
            {"output_type": output_type, "output_hashes": list(hashes)},
            sort_keys=True,
            separators=(",", ":"),
        )
        return cls(
            output_type=output_type,
            input_count=len(values),
            output_hashes=hashes,
            behavior_hash=hashlib.sha256(payload.encode("utf-8")).hexdigest(),
        )

    def to_record(self) -> dict[str, object]:
        return {
            "output_type": self.output_type,
            "input_count": self.input_count,
            "output_hashes": list(self.output_hashes),
            "behavior_hash": self.behavior_hash,
        }


def program_behavior_signature(
    program: Program,
    examples: Sequence[Mapping[str, object]],
    interpreter: Interpreter,
) -> BehaviorSignature:
    values = [interpreter.execute(program, example).value for example in examples]
    return BehaviorSignature.from_values(program.output_type.value, values)


@dataclass(frozen=True)
class BehaviorClass:
    signature: BehaviorSignature
    representative: Program
    members: tuple[Program, ...]

    def to_record(self) -> dict[str, object]:
        return {
            "signature": self.signature.to_record(),
            "representative_hash": self.representative.content_hash(),
            "member_hashes": [item.content_hash() for item in self.members],
        }


class BehaviorQuotient:
    """Merge syntax trees that execute identically on a declared example set."""

    def __init__(self, examples: Sequence[Mapping[str, object]], interpreter: Interpreter) -> None:
        self.examples = tuple(dict(example) for example in examples)
        self.interpreter = interpreter
        self._classes: dict[str, list[tuple[Program, BehaviorSignature]]] = {}

    def add(self, program: Program) -> BehaviorSignature:
        signature = program_behavior_signature(program, self.examples, self.interpreter)
        self._classes.setdefault(signature.behavior_hash, []).append((program, signature))
        return signature

    @property
    def classes(self) -> tuple[BehaviorClass, ...]:
        output = []
        for behavior_hash in sorted(self._classes):
            pairs = self._classes[behavior_hash]
            programs = sorted(
                (program for program, _ in pairs),
                key=lambda item: (
                    item.metrics.node_count,
                    item.metrics.operator_count,
                    item.content_hash(),
                ),
            )
            output.append(
                BehaviorClass(
                    signature=pairs[0][1],
                    representative=programs[0],
                    members=tuple(programs),
                )
            )
        return tuple(output)

    def representative_programs(self) -> tuple[Program, ...]:
        return tuple(item.representative for item in self.classes)

    def to_record(self) -> dict[str, object]:
        return {
            "schema": "komorebi.lasm_behavior_quotient",
            "schema_version": 1,
            "example_count": len(self.examples),
            "class_count": len(self._classes),
            "classes": [item.to_record() for item in self.classes],
        }


__all__ = [
    "BehaviorClass",
    "BehaviorQuotient",
    "BehaviorSignature",
    "canonical_runtime_record",
    "program_behavior_signature",
    "runtime_hash",
]
