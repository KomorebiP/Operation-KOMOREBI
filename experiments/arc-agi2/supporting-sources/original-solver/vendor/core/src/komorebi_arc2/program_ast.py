"""Executable, canonical typed programs for ARC candidate migration.

The v1.4 solver's legacy sequence grammar already represents executable
programs internally as tuples of ``Op`` objects, but ``RuleCandidate`` keeps
only their materialized train and test grids.  This module provides the
smallest additive substrate needed to preserve those programs as data:

* a typed identity, primitive call, and sequence tree
* a registry-backed interpreter
* canonical JSON serialization and content hashing
* a replay-checked binding to an existing materialized candidate

The legacy ``program`` family and ordinary ``conditional-dag-1`` composition
candidates can be reconstructed from their existing records.  Other candidate
families must begin emitting an AST at their own compile boundary before they
can honestly use this adapter.  A replay check prevents a materialized
candidate from being paired with an inequivalent AST.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Callable, Iterable, Mapping, Optional, Protocol, Sequence

import numpy as np


AST_SCHEMA = "komorebi.typed_program_ast"
AST_SCHEMA_VERSION = 1


class ValueType(str, Enum):
    """Runtime value types admitted by the first executable substrate."""

    GRID = "grid"
    MASK = "mask"


@dataclass(frozen=True)
class IdentityNode:
    """The typed identity program."""

    value_type: ValueType = ValueType.GRID

    @property
    def input_type(self) -> ValueType:
        return self.value_type

    @property
    def output_type(self) -> ValueType:
        return self.value_type


@dataclass(frozen=True)
class CallNode:
    """A symbolic reference to one registered typed primitive."""

    primitive: str
    input_type: ValueType = ValueType.GRID
    output_type: ValueType = ValueType.GRID

    def __post_init__(self) -> None:
        if not self.primitive or self.primitive.strip() != self.primitive:
            raise ValueError("primitive names must be nonempty and trimmed")


@dataclass(frozen=True)
class SequenceNode:
    """Ordered composition with statically checked adjacent types."""

    steps: tuple["ProgramNode", ...]

    def __post_init__(self) -> None:
        if not self.steps:
            raise ValueError("an empty sequence must be represented by IdentityNode")
        for left, right in zip(self.steps, self.steps[1:]):
            if left.output_type != right.input_type:
                raise TypeError(
                    "sequence type mismatch: "
                    f"{left.output_type.value} cannot feed {right.input_type.value}"
                )

    @property
    def input_type(self) -> ValueType:
        return self.steps[0].input_type

    @property
    def output_type(self) -> ValueType:
        return self.steps[-1].output_type


ProgramNode = IdentityNode | CallNode | SequenceNode


def _node_record(node: ProgramNode) -> dict[str, object]:
    if isinstance(node, IdentityNode):
        return {"kind": "identity", "value_type": node.value_type.value}
    if isinstance(node, CallNode):
        return {
            "kind": "call",
            "primitive": node.primitive,
            "input_type": node.input_type.value,
            "output_type": node.output_type.value,
        }
    if isinstance(node, SequenceNode):
        return {
            "kind": "sequence",
            "steps": [_node_record(step) for step in node.steps],
        }
    raise TypeError(f"unsupported program node {type(node)!r}")


def _require_mapping(value: object, context: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{context} must be a mapping")
    return value


def _node_from_record(raw: object) -> ProgramNode:
    record = _require_mapping(raw, "program node")
    kind = record.get("kind")
    if kind == "identity":
        return IdentityNode(ValueType(str(record.get("value_type"))))
    if kind == "call":
        return CallNode(
            primitive=str(record.get("primitive", "")),
            input_type=ValueType(str(record.get("input_type"))),
            output_type=ValueType(str(record.get("output_type"))),
        )
    if kind == "sequence":
        raw_steps = record.get("steps")
        if not isinstance(raw_steps, list):
            raise TypeError("sequence steps must be a list")
        return SequenceNode(tuple(_node_from_record(step) for step in raw_steps))
    raise ValueError(f"unknown program node kind {kind!r}")


@dataclass(frozen=True)
class TypedProgramAST:
    """Versioned executable syntax tree with canonical serialization."""

    root: ProgramNode
    schema_version: int = AST_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.schema_version != AST_SCHEMA_VERSION:
            raise ValueError(
                f"unsupported AST schema version {self.schema_version}; "
                f"expected {AST_SCHEMA_VERSION}"
            )

    @property
    def input_type(self) -> ValueType:
        return self.root.input_type

    @property
    def output_type(self) -> ValueType:
        return self.root.output_type

    def to_record(self) -> dict[str, object]:
        return {
            "schema": AST_SCHEMA,
            "schema_version": self.schema_version,
            "input_type": self.input_type.value,
            "output_type": self.output_type.value,
            "root": _node_record(self.root),
        }

    def to_json(self) -> str:
        return json.dumps(
            self.to_record(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )

    def content_hash(self) -> str:
        return hashlib.sha256(self.to_json().encode("utf-8")).hexdigest()

    @classmethod
    def from_record(cls, raw: object) -> "TypedProgramAST":
        record = _require_mapping(raw, "typed program")
        if record.get("schema") != AST_SCHEMA:
            raise ValueError(f"unknown AST schema {record.get('schema')!r}")
        version = int(record.get("schema_version", -1))
        ast = cls(root=_node_from_record(record.get("root")), schema_version=version)
        declared_input = ValueType(str(record.get("input_type")))
        declared_output = ValueType(str(record.get("output_type")))
        if declared_input != ast.input_type or declared_output != ast.output_type:
            raise TypeError("serialized root types do not match declared program types")
        return ast

    @classmethod
    def from_json(cls, payload: str) -> "TypedProgramAST":
        return cls.from_record(json.loads(payload))


@dataclass(frozen=True)
class PrimitiveDefinition:
    """Runtime implementation and signature for a symbolic primitive name."""

    name: str
    function: Callable[[object], object]
    input_type: ValueType = ValueType.GRID
    output_type: ValueType = ValueType.GRID

    def __post_init__(self) -> None:
        if not self.name or self.name.strip() != self.name:
            raise ValueError("primitive names must be nonempty and trimmed")
        if not callable(self.function):
            raise TypeError(f"primitive {self.name!r} is not callable")


class PrimitiveRegistry:
    """Immutable name-to-implementation map used by the interpreter."""

    def __init__(self, primitives: Iterable[PrimitiveDefinition]) -> None:
        definitions: dict[str, PrimitiveDefinition] = {}
        for primitive in primitives:
            if primitive.name in definitions:
                raise ValueError(f"duplicate primitive name {primitive.name!r}")
            definitions[primitive.name] = primitive
        self._definitions = MappingProxyType(definitions)

    def resolve(self, name: str) -> PrimitiveDefinition:
        try:
            return self._definitions[name]
        except KeyError as error:
            raise KeyError(f"unregistered primitive {name!r}") from error

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._definitions))


class TypedProgramInterpreter:
    """Execute a typed tree against an explicit primitive registry."""

    def __init__(
        self,
        registry: PrimitiveRegistry,
        *,
        normalizers: Optional[Mapping[ValueType, Callable[[object], object]]] = None,
    ) -> None:
        self.registry = registry
        self._normalizers = MappingProxyType(dict(normalizers or {}))

    def _normalize(self, value: object, value_type: ValueType) -> object:
        normalizer = self._normalizers.get(value_type)
        return normalizer(value) if normalizer is not None else value

    def _execute_node(self, node: ProgramNode, value: object) -> object:
        normalized = self._normalize(value, node.input_type)
        if isinstance(node, IdentityNode):
            return self._normalize(normalized, node.output_type)
        if isinstance(node, CallNode):
            primitive = self.registry.resolve(node.primitive)
            if primitive.input_type != node.input_type:
                raise TypeError(
                    f"primitive {node.primitive!r} input type is "
                    f"{primitive.input_type.value}, not {node.input_type.value}"
                )
            if primitive.output_type != node.output_type:
                raise TypeError(
                    f"primitive {node.primitive!r} output type is "
                    f"{primitive.output_type.value}, not {node.output_type.value}"
                )
            output = primitive.function(normalized)
            return self._normalize(output, node.output_type)
        if isinstance(node, SequenceNode):
            output = normalized
            for step in node.steps:
                output = self._execute_node(step, output)
            return self._normalize(output, node.output_type)
        raise TypeError(f"unsupported program node {type(node)!r}")

    def execute(self, program: TypedProgramAST, value: object) -> object:
        return self._execute_node(program.root, value)


def ast_from_primitive_names(primitive_names: Sequence[str]) -> TypedProgramAST:
    """Construct a grid-to-grid tree from an ordered primitive-name record."""

    names = tuple(str(name).strip() for name in primitive_names)
    calls = tuple(CallNode(name) for name in names)
    if not calls:
        return TypedProgramAST(IdentityNode())
    root: ProgramNode = calls[0] if len(calls) == 1 else SequenceNode(calls)
    return TypedProgramAST(root)


def ast_from_legacy_program_text(program_text: str) -> TypedProgramAST:
    """Parse v1.4's canonical ``program`` metadata into a typed tree."""

    text = str(program_text).strip()
    if text.startswith("program:"):
        text = text[len("program:") :]
    if text == "identity":
        return ast_from_primitive_names(())
    names = tuple(part.strip() for part in text.split(";"))
    if not names or any(not name for name in names):
        raise ValueError(f"invalid legacy program text {program_text!r}")
    return ast_from_primitive_names(names)


def ast_from_composition_metadata(metadata: Mapping[str, object]) -> TypedProgramAST:
    """Parse a reconstructible ``conditional-dag-1`` candidate record."""

    if metadata.get("program_version") != "conditional-dag-1":
        raise ValueError(
            f"unsupported composition version {metadata.get('program_version')!r}"
        )
    raw_steps = metadata.get("steps")
    if not isinstance(raw_steps, list) or not raw_steps:
        raise ValueError("composition metadata must contain at least one step")
    names = []
    for raw_step in raw_steps:
        step = _require_mapping(raw_step, "composition step")
        name = step.get("name")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("composition step is missing a primitive name")
        names.append(name)
    return ast_from_primitive_names(names)


def interpreter_from_legacy_ops(
    operations: Iterable[object],
    *,
    grid_normalizer: Callable[[object], object],
) -> TypedProgramInterpreter:
    """Build an interpreter over existing callable ``Op`` objects.

    The adapter intentionally uses only the public ``name`` and callable
    contracts of each legacy operation.  The existing ``Op.__call__`` remains
    the source of runtime semantics during the migration.
    """

    primitives = []
    for operation in operations:
        name = str(getattr(operation, "name", ""))
        if not callable(operation):
            raise TypeError(f"legacy operation {name!r} is not callable")
        primitives.append(PrimitiveDefinition(name=name, function=operation))
    return TypedProgramInterpreter(
        PrimitiveRegistry(primitives),
        normalizers={ValueType.GRID: grid_normalizer},
    )


def interpreter_from_composition_primitives(
    primitives: Iterable[object],
    *,
    grid_normalizer: Callable[[object], object],
) -> TypedProgramInterpreter:
    """Build an interpreter over v1.4's strict ``CompositionPrimitive`` API."""

    definitions = []
    for primitive in primitives:
        name = str(getattr(primitive, "name", ""))
        apply = getattr(primitive, "apply", None)
        if not callable(apply):
            raise TypeError(f"composition primitive {name!r} has no callable apply method")
        definitions.append(PrimitiveDefinition(name=name, function=apply))
    return TypedProgramInterpreter(
        PrimitiveRegistry(definitions),
        normalizers={ValueType.GRID: grid_normalizer},
    )


class MaterializedCandidate(Protocol):
    """Structural interface needed to bind a v1.4 candidate."""

    name: str
    family: str
    grids: Sequence[object]
    train_grids: Sequence[object]
    metadata: Optional[Mapping[str, object]]


@dataclass(frozen=True)
class ReplayVerification:
    """Exact comparison between AST executions and stored predictions."""

    expected_train_count: int
    replayed_train_count: int
    expected_test_count: int
    replayed_test_count: int
    train_mismatches: tuple[int, ...]
    test_mismatches: tuple[int, ...]

    @property
    def exact(self) -> bool:
        return (
            self.expected_train_count == self.replayed_train_count
            and self.expected_test_count == self.replayed_test_count
            and not self.train_mismatches
            and not self.test_mismatches
        )

    def to_record(self) -> dict[str, object]:
        return {
            "exact": self.exact,
            "expected_train_count": self.expected_train_count,
            "replayed_train_count": self.replayed_train_count,
            "expected_test_count": self.expected_test_count,
            "replayed_test_count": self.replayed_test_count,
            "train_mismatches": list(self.train_mismatches),
            "test_mismatches": list(self.test_mismatches),
        }


@dataclass(frozen=True)
class CandidateProgramBinding:
    """Non-mutating executable view of one materialized candidate."""

    candidate: MaterializedCandidate
    program: TypedProgramAST
    verification: ReplayVerification

    def execute(self, value: object, interpreter: TypedProgramInterpreter) -> object:
        return interpreter.execute(self.program, value)


class CandidateReplayMismatch(ValueError):
    """Raised when an AST does not reproduce a candidate's stored grids."""

    def __init__(self, verification: ReplayVerification) -> None:
        super().__init__(f"candidate AST replay mismatch: {verification.to_record()}")
        self.verification = verification


def _mismatch_indices(expected: Sequence[object], actual: Sequence[object]) -> tuple[int, ...]:
    shared = min(len(expected), len(actual))
    mismatches = [
        index
        for index in range(shared)
        if not bool(np.array_equal(np.asarray(expected[index]), np.asarray(actual[index])))
    ]
    mismatches.extend(range(shared, max(len(expected), len(actual))))
    return tuple(mismatches)


def verify_candidate_replay(
    candidate: MaterializedCandidate,
    program: TypedProgramAST,
    interpreter: TypedProgramInterpreter,
    *,
    train_inputs: Sequence[object],
    test_inputs: Sequence[object],
) -> ReplayVerification:
    replayed_train = tuple(interpreter.execute(program, value) for value in train_inputs)
    replayed_test = tuple(interpreter.execute(program, value) for value in test_inputs)
    expected_train = tuple(candidate.train_grids)
    expected_test = tuple(candidate.grids)
    return ReplayVerification(
        expected_train_count=len(expected_train),
        replayed_train_count=len(replayed_train),
        expected_test_count=len(expected_test),
        replayed_test_count=len(replayed_test),
        train_mismatches=_mismatch_indices(expected_train, replayed_train),
        test_mismatches=_mismatch_indices(expected_test, replayed_test),
    )


def bind_legacy_program_candidate(
    candidate: MaterializedCandidate,
    interpreter: TypedProgramInterpreter,
    *,
    train_inputs: Sequence[object],
    test_inputs: Sequence[object],
) -> CandidateProgramBinding:
    """Replay-check and bind an existing v1.4 ``program`` candidate.

    No candidate field is changed.  The function rejects non-program families
    because their materialized outputs do not contain enough information to
    reconstruct an executable transformation honestly.
    """

    if candidate.family != "program":
        raise ValueError(
            f"candidate family {candidate.family!r} does not expose a reconstructible AST"
        )
    metadata = candidate.metadata or {}
    program_text = metadata.get("program")
    if not isinstance(program_text, str):
        program_text = candidate.name
    program = ast_from_legacy_program_text(program_text)
    verification = verify_candidate_replay(
        candidate,
        program,
        interpreter,
        train_inputs=train_inputs,
        test_inputs=test_inputs,
    )
    if not verification.exact:
        raise CandidateReplayMismatch(verification)
    return CandidateProgramBinding(candidate, program, verification)


def bind_composition_candidate(
    candidate: MaterializedCandidate,
    interpreter: TypedProgramInterpreter,
    *,
    train_inputs: Sequence[object],
    test_inputs: Sequence[object],
) -> CandidateProgramBinding:
    """Replay-check a reconstructible typed-composition candidate.

    Candidates whose final result exists only as a materialized terminal rule
    will fail primitive resolution or replay.  This is intentional.  Such a
    record is not yet an executable program, even though it was emitted by the
    composition lane.
    """

    metadata = candidate.metadata or {}
    if metadata.get("composition_block") != "typed_conditional_program":
        raise ValueError("candidate does not expose typed composition metadata")
    program = ast_from_composition_metadata(metadata)
    verification = verify_candidate_replay(
        candidate,
        program,
        interpreter,
        train_inputs=train_inputs,
        test_inputs=test_inputs,
    )
    if not verification.exact:
        raise CandidateReplayMismatch(verification)
    return CandidateProgramBinding(candidate, program, verification)


__all__ = [
    "AST_SCHEMA",
    "AST_SCHEMA_VERSION",
    "CallNode",
    "CandidateProgramBinding",
    "CandidateReplayMismatch",
    "IdentityNode",
    "PrimitiveDefinition",
    "PrimitiveRegistry",
    "ReplayVerification",
    "SequenceNode",
    "TypedProgramAST",
    "TypedProgramInterpreter",
    "ValueType",
    "ast_from_composition_metadata",
    "ast_from_legacy_program_text",
    "ast_from_primitive_names",
    "bind_composition_candidate",
    "bind_legacy_program_candidate",
    "interpreter_from_composition_primitives",
    "interpreter_from_legacy_ops",
    "verify_candidate_replay",
]
