"""Immutable formal records for action-congruent PR-LASM capsules.

The records deliberately separate three things that were easy to conflate in
earlier prototypes:

* an exact runtime state, whose identity never contains a target;
* a training-only readout used to learn/audit a finite quotient; and
* target-free coordinates and contracts that may cross the runtime boundary.

All nested caller values are detached and frozen during construction.  Every
record has a canonical content hash and a strict ``from_record`` decoder.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from numbers import Integral
from types import MappingProxyType
from typing import Any, ClassVar, Iterable, Mapping, Sequence

from .canonical import (
    Grid,
    SCHEMA_VERSION,
    canonical_value,
    content_hash,
    deep_freeze,
    require_nonnegative_int,
    require_sha256,
    require_trimmed,
    validate_grid,
)


_LEAKAGE_KINDS = frozenset(
    {
        "readout",
        "applicability",
        "successor",
        "missing_receipt",
        "missing_successor",
        "nondeterminism",
        "unresolved_feature",
    }
)
_FORBIDDEN_RUNTIME_TOKENS = frozenset(
    {
        "answer",
        "expected",
        "gold",
        "label",
        "output",
        "solution",
        "target",
        "test_output",
        "training_output",
    }
)


def _empty_mapping() -> Mapping[str, Any]:
    return {}


def _tuple_strings(
    values: Iterable[object],
    label: str,
    *,
    sorted_unique: bool = False,
    allow_empty_items: bool = False,
) -> tuple[str, ...]:
    result = tuple(
        require_trimmed(value, f"{label}[{index}]", allow_empty=allow_empty_items)
        for index, value in enumerate(values)
    )
    if sorted_unique and tuple(sorted(set(result))) != result:
        raise ValueError(f"{label} must be unique and sorted")
    return result


def _digest_tuple(values: Iterable[object], label: str) -> tuple[str, ...]:
    result = tuple(
        require_sha256(value, f"{label}[{index}]")
        for index, value in enumerate(values)
    )
    if tuple(sorted(set(result))) != result:
        raise ValueError(f"{label} must be unique and sorted")
    return result


def _check_schema_version(value: object) -> None:
    if (
        isinstance(value, bool)
        or not isinstance(value, Integral)
        or int(value) != SCHEMA_VERSION
    ):
        raise ValueError(f"schema_version must equal {SCHEMA_VERSION}")


def _body_with_hash(body: Mapping[str, Any]) -> dict[str, Any]:
    record = dict(canonical_value(body))
    record["content_hash"] = content_hash(record)
    return record


def _strip_and_verify_record(
    record: Mapping[str, Any], *, schema: str, allowed: set[str]
) -> dict[str, Any]:
    if not isinstance(record, Mapping):
        raise TypeError("record must be a mapping")
    unknown = set(record) - allowed - {"content_hash"}
    if unknown:
        raise ValueError(f"unknown {schema} fields: {sorted(unknown)}")
    body = {key: value for key, value in record.items() if key != "content_hash"}
    if body.get("schema") != schema:
        raise ValueError(f"record schema must equal {schema!r}")
    if "content_hash" in record:
        digest = require_sha256(record["content_hash"], "content_hash")
        if digest != content_hash(body):
            raise ValueError("record content_hash does not match its contents")
    return body


def _feature_key_tokens(key: str) -> tuple[str, ...]:
    normalized = key.lower().replace("-", "_").replace(".", "_")
    return tuple(token for token in normalized.split("_") if token)


def _assert_target_free(value: Any, *, path: str = "$") -> None:
    """Reject explicit target/answer coordinates at the runtime boundary."""

    if isinstance(value, Mapping):
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError(f"runtime coordinate key at {path} must be a string")
            tokens = _feature_key_tokens(key)
            if key.lower() in _FORBIDDEN_RUNTIME_TOKENS or any(
                token in _FORBIDDEN_RUNTIME_TOKENS for token in tokens
            ):
                raise ValueError(f"target-aware coordinate {key!r} is forbidden at runtime")
            _assert_target_free(item, path=f"{path}.{key}")
    elif isinstance(value, (tuple, list)):
        for index, item in enumerate(value):
            _assert_target_free(item, path=f"{path}[{index}]")


@dataclass(frozen=True, slots=True)
class AmbientPacket:
    """Finite target-free state features available to capsule refinement."""

    features: Mapping[str, Any] = field(default_factory=_empty_mapping)
    packet_kind: str = "static"
    provenance: tuple[str, ...] = ()
    schema_version: int = SCHEMA_VERSION

    SCHEMA: ClassVar[str] = "komorebi.lasm_action.ambient_packet"

    def __post_init__(self) -> None:
        require_trimmed(self.packet_kind, "packet_kind")
        provenance = _tuple_strings(self.provenance, "provenance", sorted_unique=True)
        frozen = deep_freeze(self.features)
        if not isinstance(frozen, Mapping):
            raise TypeError("features must be a mapping")
        _assert_target_free(frozen)
        object.__setattr__(self, "features", frozen)
        object.__setattr__(self, "provenance", provenance)
        _check_schema_version(self.schema_version)

    @property
    def feature_names(self) -> tuple[str, ...]:
        return tuple(self.features)

    @property
    def identity_record(self) -> dict[str, Any]:
        return {
            "schema": self.SCHEMA,
            "schema_version": self.schema_version,
            "packet_kind": self.packet_kind,
            "features": canonical_value(self.features),
            "provenance": list(self.provenance),
        }

    @property
    def packet_hash(self) -> str:
        return content_hash(self.identity_record)

    @property
    def content_hash(self) -> str:
        return self.packet_hash

    @property
    def packet_id(self) -> str:
        return self.packet_hash

    def to_record(self) -> dict[str, Any]:
        return _body_with_hash(self.identity_record)

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "AmbientPacket":
        body = _strip_and_verify_record(
            record,
            schema=cls.SCHEMA,
            allowed={"schema", "schema_version", "packet_kind", "features", "provenance"},
        )
        return cls(
            features=body.get("features", {}),
            packet_kind=body.get("packet_kind", "static"),
            provenance=tuple(body.get("provenance", ())),
            schema_version=body.get("schema_version", SCHEMA_VERSION),
        )


@dataclass(frozen=True, slots=True)
class RuntimeCoordinates:
    """Coordinates safe to persist and use after training labels are removed."""

    state_hash: str
    values: Mapping[str, Any] = field(default_factory=_empty_mapping)
    capsule_hash: str = ""
    gauge_id: str = "identity"
    schema_version: int = SCHEMA_VERSION

    SCHEMA: ClassVar[str] = "komorebi.lasm_action.runtime_coordinates"

    def __post_init__(self) -> None:
        require_sha256(self.state_hash, "state_hash")
        require_sha256(self.capsule_hash, "capsule_hash", allow_empty=True)
        require_trimmed(self.gauge_id, "gauge_id")
        frozen = deep_freeze(self.values)
        if not isinstance(frozen, Mapping):
            raise TypeError("runtime coordinate values must be a mapping")
        _assert_target_free(frozen)
        object.__setattr__(self, "values", frozen)
        _check_schema_version(self.schema_version)

    @property
    def identity_record(self) -> dict[str, Any]:
        return {
            "schema": self.SCHEMA,
            "schema_version": self.schema_version,
            "state_hash": self.state_hash,
            "capsule_hash": self.capsule_hash,
            "gauge_id": self.gauge_id,
            "values": canonical_value(self.values),
        }

    @property
    def coordinate_hash(self) -> str:
        return content_hash(self.identity_record)

    @property
    def content_hash(self) -> str:
        return self.coordinate_hash

    def to_record(self) -> dict[str, Any]:
        return _body_with_hash(self.identity_record)

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "RuntimeCoordinates":
        body = _strip_and_verify_record(
            record,
            schema=cls.SCHEMA,
            allowed={"schema", "schema_version", "state_hash", "capsule_hash", "gauge_id", "values"},
        )
        return cls(
            state_hash=body["state_hash"],
            capsule_hash=body.get("capsule_hash", ""),
            gauge_id=body.get("gauge_id", "identity"),
            values=body.get("values", {}),
            schema_version=body.get("schema_version", SCHEMA_VERSION),
        )


@dataclass(frozen=True, slots=True)
class TargetAwareSynthesisContext:
    """Training-only coordinates that may inspect one demonstrated target.

    There is intentionally no implicit conversion to :class:`RuntimeCoordinates`.
    There is also no method on this target-aware object that can mint a runtime
    record.  Callers must leave this scope and independently construct target-
    free coordinates from the source/runtime path.  Python values do not carry
    information-flow taint, so lexical field rejection alone is not presented
    as a noninterference proof.
    """

    source_grid: Grid
    target_grid: Grid
    candidate_values: Mapping[str, Any] = field(default_factory=_empty_mapping)
    schema_version: int = SCHEMA_VERSION

    SCHEMA: ClassVar[str] = "komorebi.lasm_action.target_aware_synthesis_context"

    def __post_init__(self) -> None:
        object.__setattr__(self, "source_grid", validate_grid(self.source_grid))
        object.__setattr__(self, "target_grid", validate_grid(self.target_grid))
        frozen = deep_freeze(self.candidate_values)
        if not isinstance(frozen, Mapping):
            raise TypeError("candidate_values must be a mapping")
        object.__setattr__(self, "candidate_values", frozen)
        _check_schema_version(self.schema_version)

    @property
    def source_hash(self) -> str:
        return content_hash({"grid": self.source_grid})

    @property
    def target_hash(self) -> str:
        return content_hash({"grid": self.target_grid})

    @property
    def context_hash(self) -> str:
        return content_hash(self.identity_record)

    @property
    def content_hash(self) -> str:
        return self.context_hash

    @property
    def identity_record(self) -> dict[str, Any]:
        return {
            "schema": self.SCHEMA,
            "schema_version": self.schema_version,
            "source_grid": canonical_value(self.source_grid),
            "target_grid": canonical_value(self.target_grid),
            "candidate_values": canonical_value(self.candidate_values),
        }

    def to_record(self) -> dict[str, Any]:
        return _body_with_hash(self.identity_record)

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "TargetAwareSynthesisContext":
        body = _strip_and_verify_record(
            record,
            schema=cls.SCHEMA,
            allowed={"schema", "schema_version", "source_grid", "target_grid", "candidate_values"},
        )
        return cls(
            source_grid=body["source_grid"],
            target_grid=body["target_grid"],
            candidate_values=body.get("candidate_values", {}),
            schema_version=body.get("schema_version", SCHEMA_VERSION),
        )


# The longer spelling is useful in specifications; both names denote exactly
# the same deliberately training-only type.
TargetAwareSynthesisCoordinates = TargetAwareSynthesisContext


@dataclass(frozen=True, slots=True)
class StaticTransitionState:
    """One exact finite state plus a training-only observable readout."""

    grid: Grid
    readout: Any = None
    ambient: AmbientPacket = field(default_factory=AmbientPacket)
    runtime_values: Mapping[str, Any] = field(default_factory=_empty_mapping)
    history: tuple[str, ...] = ()
    state_name: str = ""
    schema_version: int = SCHEMA_VERSION

    SCHEMA: ClassVar[str] = "komorebi.lasm_action.static_transition_state"

    def __post_init__(self) -> None:
        object.__setattr__(self, "grid", validate_grid(self.grid))
        if not isinstance(self.ambient, AmbientPacket):
            if isinstance(self.ambient, Mapping):
                object.__setattr__(self, "ambient", AmbientPacket(features=self.ambient))
            else:
                raise TypeError("ambient must be an AmbientPacket or feature mapping")
        frozen_readout = deep_freeze(self.readout)
        frozen_runtime = deep_freeze(self.runtime_values)
        if not isinstance(frozen_runtime, Mapping):
            raise TypeError("runtime_values must be a mapping")
        _assert_target_free(frozen_runtime)
        object.__setattr__(self, "readout", frozen_readout)
        object.__setattr__(self, "runtime_values", frozen_runtime)
        object.__setattr__(self, "history", _tuple_strings(self.history, "history"))
        require_trimmed(self.state_name, "state_name", allow_empty=True)
        _check_schema_version(self.schema_version)

    @property
    def identity_record(self) -> dict[str, Any]:
        """Target-free identity; ``readout`` is intentionally absent."""

        return {
            "schema": "komorebi.lasm_action.static_transition_state_identity",
            "schema_version": self.schema_version,
            "grid": canonical_value(self.grid),
            "ambient_packet_hash": self.ambient.packet_hash,
            "runtime_values": canonical_value(self.runtime_values),
            "history": list(self.history),
            "state_name": self.state_name,
        }

    @property
    def state_hash(self) -> str:
        return content_hash(self.identity_record)

    @property
    def exact_grid(self) -> Grid:
        return self.grid

    @property
    def semantic_record(self) -> dict[str, Any]:
        return {
            "schema": self.SCHEMA,
            "schema_version": self.schema_version,
            "state_hash": self.state_hash,
            "grid": canonical_value(self.grid),
            "readout": canonical_value(self.readout),
            "ambient": self.ambient.to_record(),
            "runtime_values": canonical_value(self.runtime_values),
            "history": list(self.history),
            "state_name": self.state_name,
        }

    @property
    def content_hash(self) -> str:
        return content_hash(self.semantic_record)

    def runtime_coordinates(
        self, *, capsule_hash: str = "", gauge_id: str = "identity"
    ) -> RuntimeCoordinates:
        values = {
            **canonical_value(self.runtime_values),
            "ambient": canonical_value(self.ambient.features),
        }
        return RuntimeCoordinates(
            state_hash=self.state_hash,
            capsule_hash=capsule_hash,
            gauge_id=gauge_id,
            values=values,
        )

    def to_record(self) -> dict[str, Any]:
        return _body_with_hash(self.semantic_record)

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "StaticTransitionState":
        body = _strip_and_verify_record(
            record,
            schema=cls.SCHEMA,
            allowed={
                "schema", "schema_version", "state_hash", "grid", "readout",
                "ambient", "runtime_values", "history", "state_name",
            },
        )
        ambient_record = body.get("ambient", AmbientPacket().to_record())
        ambient = AmbientPacket.from_record(ambient_record)
        result = cls(
            grid=body["grid"],
            readout=body.get("readout"),
            ambient=ambient,
            runtime_values=body.get("runtime_values", {}),
            history=tuple(body.get("history", ())),
            state_name=body.get("state_name", ""),
            schema_version=body.get("schema_version", SCHEMA_VERSION),
        )
        if "state_hash" in body and body["state_hash"] != result.state_hash:
            raise ValueError("state_hash does not match state contents")
        return result


ExactStaticTransitionState = StaticTransitionState


@dataclass(frozen=True, slots=True)
class ActionReceipt:
    """One deterministic action observation at one exact source state."""

    source_state_hash: str
    action: str
    applicable: bool
    successor_state_hash: str = ""
    parameters: Mapping[str, Any] = field(default_factory=_empty_mapping)
    evidence_kind: str = "observed"
    schema_version: int = SCHEMA_VERSION

    SCHEMA: ClassVar[str] = "komorebi.lasm_action.action_receipt"

    def __post_init__(self) -> None:
        require_sha256(self.source_state_hash, "source_state_hash")
        require_trimmed(self.action, "action")
        if not isinstance(self.applicable, bool):
            raise TypeError("applicable must be Boolean")
        require_sha256(
            self.successor_state_hash,
            "successor_state_hash",
            # A bounded counterfactual audit can establish applicability before
            # it has room to materialize the exact successor.  Such a receipt
            # is valid evidence but incomplete and can never certify successor
            # congruence.
            allow_empty=True,
        )
        if not self.applicable and self.successor_state_hash:
            raise ValueError("an inapplicable action cannot have a successor")
        frozen = deep_freeze(self.parameters)
        if not isinstance(frozen, Mapping):
            raise TypeError("parameters must be a mapping")
        object.__setattr__(self, "parameters", frozen)
        require_trimmed(self.evidence_kind, "evidence_kind")
        _check_schema_version(self.schema_version)

    @property
    def action_id(self) -> str:
        return self.action

    @property
    def successor_known(self) -> bool:
        return bool(self.successor_state_hash) if self.applicable else True

    @property
    def identity_record(self) -> dict[str, Any]:
        return {
            "schema": self.SCHEMA,
            "schema_version": self.schema_version,
            "source_state_hash": self.source_state_hash,
            "action": self.action,
            "applicable": self.applicable,
            "successor_state_hash": self.successor_state_hash,
            "parameters": canonical_value(self.parameters),
            "evidence_kind": self.evidence_kind,
        }

    @property
    def receipt_hash(self) -> str:
        return content_hash(self.identity_record)

    @property
    def content_hash(self) -> str:
        return self.receipt_hash

    def to_record(self) -> dict[str, Any]:
        return _body_with_hash(self.identity_record)

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "ActionReceipt":
        body = _strip_and_verify_record(
            record,
            schema=cls.SCHEMA,
            allowed={
                "schema", "schema_version", "source_state_hash", "action",
                "applicable", "successor_state_hash", "parameters", "evidence_kind",
            },
        )
        return cls(
            source_state_hash=body["source_state_hash"],
            action=body["action"],
            applicable=body["applicable"],
            successor_state_hash=body.get("successor_state_hash", ""),
            parameters=body.get("parameters", {}),
            evidence_kind=body.get("evidence_kind", "observed"),
            schema_version=body.get("schema_version", SCHEMA_VERSION),
        )


@dataclass(frozen=True, slots=True)
class PredictiveCapsule:
    """A finite partition over exact target-free state identities."""

    blocks: tuple[tuple[str, ...], ...]
    feature_names: tuple[str, ...] = ()
    origin: str = "oracle"
    complete: bool = True
    schema_version: int = SCHEMA_VERSION

    SCHEMA: ClassVar[str] = "komorebi.lasm_action.predictive_capsule"

    def __post_init__(self) -> None:
        normalized_blocks: list[tuple[str, ...]] = []
        seen: set[str] = set()
        for block_index, block in enumerate(self.blocks):
            normalized = tuple(sorted(
                require_sha256(value, f"blocks[{block_index}][{index}]")
                for index, value in enumerate(block)
            ))
            if not normalized:
                raise ValueError("capsule blocks must be nonempty")
            if len(set(normalized)) != len(normalized):
                raise ValueError("a capsule block cannot repeat a state")
            overlap = seen.intersection(normalized)
            if overlap:
                raise ValueError("capsule blocks must be disjoint")
            seen.update(normalized)
            normalized_blocks.append(normalized)
        if not normalized_blocks:
            raise ValueError("a predictive capsule needs at least one block")
        normalized_blocks.sort()
        object.__setattr__(self, "blocks", tuple(normalized_blocks))
        features = _tuple_strings(self.feature_names, "feature_names", sorted_unique=True)
        _assert_target_free({name: None for name in features})
        object.__setattr__(self, "feature_names", features)
        require_trimmed(self.origin, "origin")
        if not isinstance(self.complete, bool):
            raise TypeError("complete must be Boolean")
        _check_schema_version(self.schema_version)

    @property
    def state_hashes(self) -> tuple[str, ...]:
        return tuple(sorted(state for block in self.blocks for state in block))

    def block_index(self, state_hash: str) -> int:
        require_sha256(state_hash, "state_hash")
        for index, block in enumerate(self.blocks):
            if state_hash in block:
                return index
        raise KeyError(state_hash)

    def class_of(self, state_hash: str) -> int:
        return self.block_index(state_hash)

    def block_key(self, state_hash: str) -> str:
        index = self.block_index(state_hash)
        return content_hash({"capsule": self.capsule_hash, "block": self.blocks[index]})

    @property
    def identity_record(self) -> dict[str, Any]:
        return {
            "schema": self.SCHEMA,
            "schema_version": self.schema_version,
            "blocks": [list(block) for block in self.blocks],
            "feature_names": list(self.feature_names),
            "origin": self.origin,
            "complete": self.complete,
        }

    @property
    def capsule_hash(self) -> str:
        return content_hash(self.identity_record)

    @property
    def capsule_id(self) -> str:
        return self.capsule_hash

    @property
    def content_hash(self) -> str:
        return self.capsule_hash

    def to_record(self) -> dict[str, Any]:
        record = {**self.identity_record, "capsule_hash": self.capsule_hash}
        return _body_with_hash(record)

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "PredictiveCapsule":
        body = _strip_and_verify_record(
            record,
            schema=cls.SCHEMA,
            allowed={
                "schema", "schema_version", "blocks", "feature_names", "origin",
                "complete", "capsule_hash",
            },
        )
        result = cls(
            blocks=tuple(tuple(block) for block in body["blocks"]),
            feature_names=tuple(body.get("feature_names", ())),
            origin=body.get("origin", "oracle"),
            complete=body.get("complete", True),
            schema_version=body.get("schema_version", SCHEMA_VERSION),
        )
        if "capsule_hash" in body and body["capsule_hash"] != result.capsule_hash:
            raise ValueError("capsule_hash does not match capsule contents")
        return result


@dataclass(frozen=True, slots=True)
class LeakageWitness:
    """A finite counterexample to one required capsule congruence."""

    kind: str
    capsule_hash: str
    left_state_hash: str
    right_state_hash: str
    action: str = ""
    left_observation: Any = None
    right_observation: Any = None
    block_index: int = 0
    details: Mapping[str, Any] = field(default_factory=_empty_mapping)
    schema_version: int = SCHEMA_VERSION

    SCHEMA: ClassVar[str] = "komorebi.lasm_action.leakage_witness"

    def __post_init__(self) -> None:
        if self.kind not in _LEAKAGE_KINDS:
            raise ValueError(f"unknown leakage kind {self.kind!r}")
        require_sha256(self.capsule_hash, "capsule_hash")
        require_sha256(self.left_state_hash, "left_state_hash")
        require_sha256(self.right_state_hash, "right_state_hash")
        if (
            self.left_state_hash == self.right_state_hash
            and self.kind not in {
                "missing_receipt", "missing_successor", "nondeterminism",
                "unresolved_feature",
            }
        ):
            raise ValueError("a binary congruence witness needs two distinct states")
        require_trimmed(self.action, "action", allow_empty=True)
        block_index = require_nonnegative_int(self.block_index, "block_index")
        object.__setattr__(self, "block_index", block_index)
        left = deep_freeze(self.left_observation)
        right = deep_freeze(self.right_observation)
        details = deep_freeze(self.details)
        if not isinstance(details, Mapping):
            raise TypeError("details must be a mapping")
        # Canonicalize pair orientation together with its observations.
        if self.right_state_hash < self.left_state_hash:
            old_left = self.left_state_hash
            old_right = self.right_state_hash
            object.__setattr__(self, "left_state_hash", old_right)
            object.__setattr__(self, "right_state_hash", old_left)
            left, right = right, left
        object.__setattr__(self, "left_observation", left)
        object.__setattr__(self, "right_observation", right)
        object.__setattr__(self, "details", details)
        _check_schema_version(self.schema_version)

    @property
    def identity_record(self) -> dict[str, Any]:
        return {
            "schema": self.SCHEMA,
            "schema_version": self.schema_version,
            "kind": self.kind,
            "capsule_hash": self.capsule_hash,
            "left_state_hash": self.left_state_hash,
            "right_state_hash": self.right_state_hash,
            "action": self.action,
            "left_observation": canonical_value(self.left_observation),
            "right_observation": canonical_value(self.right_observation),
            "block_index": self.block_index,
            "details": canonical_value(self.details),
        }

    @property
    def witness_hash(self) -> str:
        return content_hash(self.identity_record)

    @property
    def witness_kind(self) -> str:
        return self.kind

    @property
    def content_hash(self) -> str:
        return self.witness_hash

    def to_record(self) -> dict[str, Any]:
        return _body_with_hash(self.identity_record)

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "LeakageWitness":
        body = _strip_and_verify_record(
            record,
            schema=cls.SCHEMA,
            allowed={
                "schema", "schema_version", "kind", "capsule_hash",
                "left_state_hash", "right_state_hash", "action",
                "left_observation", "right_observation", "block_index", "details",
            },
        )
        return cls(
            kind=body["kind"],
            capsule_hash=body["capsule_hash"],
            left_state_hash=body["left_state_hash"],
            right_state_hash=body["right_state_hash"],
            action=body.get("action", ""),
            left_observation=body.get("left_observation"),
            right_observation=body.get("right_observation"),
            block_index=body.get("block_index", 0),
            details=body.get("details", {}),
            schema_version=body.get("schema_version", SCHEMA_VERSION),
        )


@dataclass(frozen=True, slots=True)
class RefinementProposal:
    """Collision-driven finite refinement of an existing capsule partition."""

    base_capsule_hash: str
    witness_hashes: tuple[str, ...]
    added_features: tuple[str, ...]
    refined_blocks: tuple[tuple[str, ...], ...]
    unresolved_witness_hashes: tuple[str, ...] = ()
    method: str = "greedy_collision_split"
    schema_version: int = SCHEMA_VERSION

    SCHEMA: ClassVar[str] = "komorebi.lasm_action.refinement_proposal"

    def __post_init__(self) -> None:
        require_sha256(self.base_capsule_hash, "base_capsule_hash")
        witnesses = _digest_tuple(self.witness_hashes, "witness_hashes")
        unresolved = _digest_tuple(
            self.unresolved_witness_hashes, "unresolved_witness_hashes"
        )
        if not set(unresolved).issubset(witnesses):
            raise ValueError("unresolved witnesses must be a subset of all witnesses")
        features = _tuple_strings(
            self.added_features, "added_features", sorted_unique=True
        )
        _assert_target_free({name: None for name in features})
        # Reuse capsule validation for disjointness, digest checks and sorting.
        normalized = PredictiveCapsule(
            blocks=self.refined_blocks,
            feature_names=features,
            origin="refinement_validation",
            complete=not unresolved,
        ).blocks
        object.__setattr__(self, "witness_hashes", witnesses)
        object.__setattr__(self, "unresolved_witness_hashes", unresolved)
        object.__setattr__(self, "added_features", features)
        object.__setattr__(self, "refined_blocks", normalized)
        require_trimmed(self.method, "method")
        _check_schema_version(self.schema_version)

    @property
    def resolves_all(self) -> bool:
        return not self.unresolved_witness_hashes

    @property
    def refined_capsule_hash(self) -> str:
        return content_hash(
            {
                "base_capsule_hash": self.base_capsule_hash,
                "blocks": self.refined_blocks,
                "added_features": self.added_features,
                "complete": self.resolves_all,
            }
        )

    def as_capsule(self, base: PredictiveCapsule) -> PredictiveCapsule:
        if base.capsule_hash != self.base_capsule_hash:
            raise ValueError("refinement proposal does not belong to base capsule")
        base_states = set(base.state_hashes)
        refined_states = {
            state_hash
            for block in self.refined_blocks
            for state_hash in block
        }
        if refined_states != base_states:
            raise ValueError(
                "refinement proposal must preserve the base capsule state universe"
            )
        base_class = {
            state_hash: block_index
            for block_index, block in enumerate(base.blocks)
            for state_hash in block
        }
        if any(
            len({base_class[state_hash] for state_hash in block}) != 1
            for block in self.refined_blocks
        ):
            raise ValueError(
                "refinement proposal may split base blocks but cannot merge them"
            )
        return PredictiveCapsule(
            blocks=self.refined_blocks,
            feature_names=tuple(sorted(set(base.feature_names + self.added_features))),
            origin=f"refined:{base.capsule_hash}",
            complete=self.resolves_all,
        )

    @property
    def identity_record(self) -> dict[str, Any]:
        return {
            "schema": self.SCHEMA,
            "schema_version": self.schema_version,
            "base_capsule_hash": self.base_capsule_hash,
            "witness_hashes": list(self.witness_hashes),
            "added_features": list(self.added_features),
            "refined_blocks": [list(block) for block in self.refined_blocks],
            "unresolved_witness_hashes": list(self.unresolved_witness_hashes),
            "method": self.method,
        }

    @property
    def proposal_hash(self) -> str:
        return content_hash(self.identity_record)

    @property
    def content_hash(self) -> str:
        return self.proposal_hash

    def to_record(self) -> dict[str, Any]:
        return _body_with_hash(self.identity_record)

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "RefinementProposal":
        body = _strip_and_verify_record(
            record,
            schema=cls.SCHEMA,
            allowed={
                "schema", "schema_version", "base_capsule_hash", "witness_hashes",
                "added_features", "refined_blocks", "unresolved_witness_hashes", "method",
            },
        )
        return cls(
            base_capsule_hash=body["base_capsule_hash"],
            witness_hashes=tuple(body.get("witness_hashes", ())),
            added_features=tuple(body.get("added_features", ())),
            refined_blocks=tuple(tuple(block) for block in body["refined_blocks"]),
            unresolved_witness_hashes=tuple(body.get("unresolved_witness_hashes", ())),
            method=body.get("method", "greedy_collision_split"),
            schema_version=body.get("schema_version", SCHEMA_VERSION),
        )


@dataclass(frozen=True, slots=True)
class ActionContract:
    """Target-free certificate that one action respects one capsule."""

    action: str
    capsule_hash: str
    covered_state_hashes: tuple[str, ...]
    readout_congruent: bool
    applicability_congruent: bool
    successor_congruent: bool
    witness_hashes: tuple[str, ...] = ()
    complete: bool = True
    schema_version: int = SCHEMA_VERSION

    SCHEMA: ClassVar[str] = "komorebi.lasm_action.action_contract"

    def __post_init__(self) -> None:
        require_trimmed(self.action, "action")
        require_sha256(self.capsule_hash, "capsule_hash")
        states = _digest_tuple(self.covered_state_hashes, "covered_state_hashes")
        witnesses = _digest_tuple(self.witness_hashes, "witness_hashes")
        object.__setattr__(self, "covered_state_hashes", states)
        object.__setattr__(self, "witness_hashes", witnesses)
        for name in (
            "readout_congruent", "applicability_congruent",
            "successor_congruent", "complete",
        ):
            if not isinstance(getattr(self, name), bool):
                raise TypeError(f"{name} must be Boolean")
        if self.certified and witnesses:
            raise ValueError("a certified contract cannot contain leakage witnesses")
        _check_schema_version(self.schema_version)

    @property
    def action_id(self) -> str:
        return self.action

    @property
    def certified(self) -> bool:
        return (
            self.complete
            and self.readout_congruent
            and self.applicability_congruent
            and self.successor_congruent
            and not self.witness_hashes
        )

    @property
    def authorized(self) -> bool:
        return self.certified

    @property
    def valid(self) -> bool:
        return self.certified

    @property
    def identity_record(self) -> dict[str, Any]:
        return {
            "schema": self.SCHEMA,
            "schema_version": self.schema_version,
            "action": self.action,
            "capsule_hash": self.capsule_hash,
            "covered_state_hashes": list(self.covered_state_hashes),
            "readout_congruent": self.readout_congruent,
            "applicability_congruent": self.applicability_congruent,
            "successor_congruent": self.successor_congruent,
            "witness_hashes": list(self.witness_hashes),
            "complete": self.complete,
        }

    @property
    def contract_hash(self) -> str:
        return content_hash(self.identity_record)

    @property
    def content_hash(self) -> str:
        return self.contract_hash

    def to_record(self) -> dict[str, Any]:
        return _body_with_hash(self.identity_record)

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "ActionContract":
        body = _strip_and_verify_record(
            record,
            schema=cls.SCHEMA,
            allowed={
                "schema", "schema_version", "action", "capsule_hash",
                "covered_state_hashes", "readout_congruent",
                "applicability_congruent", "successor_congruent",
                "witness_hashes", "complete",
            },
        )
        return cls(
            action=body["action"],
            capsule_hash=body["capsule_hash"],
            covered_state_hashes=tuple(body.get("covered_state_hashes", ())),
            readout_congruent=body["readout_congruent"],
            applicability_congruent=body["applicability_congruent"],
            successor_congruent=body["successor_congruent"],
            witness_hashes=tuple(body.get("witness_hashes", ())),
            complete=body.get("complete", True),
            schema_version=body.get("schema_version", SCHEMA_VERSION),
        )


@dataclass(frozen=True, slots=True)
class CongruenceAudit:
    """Complete finite audit result for a capsule and action alphabet."""

    capsule_hash: str
    contracts: tuple[ActionContract, ...]
    witnesses: tuple[LeakageWitness, ...]
    covered_state_hashes: tuple[str, ...]
    action_alphabet: tuple[str, ...]
    schema_version: int = SCHEMA_VERSION

    SCHEMA: ClassVar[str] = "komorebi.lasm_action.congruence_audit"

    def __post_init__(self) -> None:
        require_sha256(self.capsule_hash, "capsule_hash")
        contracts = tuple(self.contracts)
        witnesses = tuple(self.witnesses)
        if not all(isinstance(item, ActionContract) for item in contracts):
            raise TypeError("contracts must contain ActionContract records")
        if not all(isinstance(item, LeakageWitness) for item in witnesses):
            raise TypeError("witnesses must contain LeakageWitness records")
        if any(item.capsule_hash != self.capsule_hash for item in contracts + witnesses):
            raise ValueError("all audit records must reference the audited capsule")
        contract_actions = tuple(item.action for item in contracts)
        if tuple(sorted(contract_actions)) != contract_actions:
            raise ValueError("contracts must be sorted by action")
        if len(set(contract_actions)) != len(contract_actions):
            raise ValueError("an audit cannot repeat an action contract")
        covered_states = _digest_tuple(
            self.covered_state_hashes, "covered_state_hashes"
        )
        action_alphabet = _tuple_strings(
            self.action_alphabet, "action_alphabet", sorted_unique=True
        )
        if contract_actions != action_alphabet:
            raise ValueError(
                "audit contracts must cover the complete action alphabet exactly"
            )
        if any(item.covered_state_hashes != covered_states for item in contracts):
            raise ValueError(
                "every action contract must cover the audit state set exactly"
            )
        covered_set = set(covered_states)
        if any(
            item.left_state_hash not in covered_set
            or item.right_state_hash not in covered_set
            for item in witnesses
        ):
            raise ValueError("audit witnesses must reference covered states")
        if any(item.action and item.action not in action_alphabet for item in witnesses):
            raise ValueError("audit witness references an action outside the alphabet")
        witness_ids = {item.witness_hash for item in witnesses}
        referenced_witness_ids = {
            witness_hash
            for contract in contracts
            for witness_hash in contract.witness_hashes
        }
        if referenced_witness_ids - witness_ids:
            raise ValueError("action contract references an absent audit witness")
        if contracts and witness_ids != referenced_witness_ids:
            raise ValueError("every audit witness must be referenced by a contract")
        object.__setattr__(self, "contracts", contracts)
        object.__setattr__(self, "witnesses", tuple(sorted(
            witnesses, key=lambda item: item.witness_hash
        )))
        object.__setattr__(self, "covered_state_hashes", covered_states)
        object.__setattr__(self, "action_alphabet", action_alphabet)
        _check_schema_version(self.schema_version)

    @property
    def congruent(self) -> bool:
        return not self.witnesses and all(contract.certified for contract in self.contracts)

    @property
    def content_hash(self) -> str:
        return content_hash(self.identity_record)

    @property
    def identity_record(self) -> dict[str, Any]:
        return {
            "schema": self.SCHEMA,
            "schema_version": self.schema_version,
            "capsule_hash": self.capsule_hash,
            "contracts": [contract.to_record() for contract in self.contracts],
            "witnesses": [witness.to_record() for witness in self.witnesses],
            "covered_state_hashes": list(self.covered_state_hashes),
            "action_alphabet": list(self.action_alphabet),
            "congruent": self.congruent,
        }

    def to_record(self) -> dict[str, Any]:
        return _body_with_hash(self.identity_record)

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "CongruenceAudit":
        body = _strip_and_verify_record(
            record,
            schema=cls.SCHEMA,
            allowed={
                "schema", "schema_version", "capsule_hash", "contracts", "witnesses",
                "covered_state_hashes", "action_alphabet", "congruent",
            },
        )
        result = cls(
            capsule_hash=body["capsule_hash"],
            contracts=tuple(ActionContract.from_record(item) for item in body.get("contracts", ())),
            witnesses=tuple(LeakageWitness.from_record(item) for item in body.get("witnesses", ())),
            covered_state_hashes=tuple(body.get("covered_state_hashes", ())),
            action_alphabet=tuple(body.get("action_alphabet", ())),
            schema_version=body.get("schema_version", SCHEMA_VERSION),
        )
        if "congruent" in body and body["congruent"] != result.congruent:
            raise ValueError("stored congruent flag does not match audit records")
        return result


@dataclass(frozen=True, slots=True)
class CapsuleSnapshot:
    """Target-free executable capsule bundle suitable for fresh-process replay."""

    capsule: PredictiveCapsule
    contracts: tuple[ActionContract, ...] = ()
    ambient_packets: tuple[AmbientPacket, ...] = ()
    runtime_coordinates: tuple[RuntimeCoordinates, ...] = ()
    receipts: tuple[ActionReceipt, ...] = ()
    registry_hash: str = ""
    metadata: Mapping[str, Any] = field(default_factory=_empty_mapping)
    schema_version: int = SCHEMA_VERSION

    SCHEMA: ClassVar[str] = "komorebi.lasm_action.capsule_snapshot"

    def __post_init__(self) -> None:
        if not isinstance(self.capsule, PredictiveCapsule):
            raise TypeError("capsule must be a PredictiveCapsule")
        contracts = tuple(self.contracts)
        packets = tuple(self.ambient_packets)
        coordinates = tuple(self.runtime_coordinates)
        receipts = tuple(self.receipts)
        if not all(isinstance(item, ActionContract) for item in contracts):
            raise TypeError("contracts must contain ActionContract records")
        if not all(isinstance(item, AmbientPacket) for item in packets):
            raise TypeError("ambient_packets must contain AmbientPacket records")
        if not all(isinstance(item, RuntimeCoordinates) for item in coordinates):
            raise TypeError("runtime_coordinates must contain RuntimeCoordinates records")
        if not all(isinstance(item, ActionReceipt) for item in receipts):
            raise TypeError("receipts must contain ActionReceipt records")
        for item in receipts:
            _assert_target_free(item.parameters)
        if any(item.capsule_hash != self.capsule.capsule_hash for item in contracts):
            raise ValueError("snapshot contracts must reference its capsule")
        if any(
            item.capsule_hash not in ("", self.capsule.capsule_hash)
            for item in coordinates
        ):
            raise ValueError("runtime coordinates reference another capsule")
        if len({item.action for item in contracts}) != len(contracts):
            raise ValueError("snapshot cannot repeat an action contract")
        object.__setattr__(self, "contracts", tuple(sorted(contracts, key=lambda item: item.action)))
        object.__setattr__(self, "ambient_packets", tuple(sorted(packets, key=lambda item: item.packet_hash)))
        object.__setattr__(self, "runtime_coordinates", tuple(sorted(coordinates, key=lambda item: item.coordinate_hash)))
        object.__setattr__(self, "receipts", tuple(sorted(receipts, key=lambda item: item.receipt_hash)))
        require_sha256(self.registry_hash, "registry_hash", allow_empty=True)
        metadata = deep_freeze(self.metadata)
        if not isinstance(metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        _assert_target_free(metadata)
        object.__setattr__(self, "metadata", metadata)
        _check_schema_version(self.schema_version)

    @property
    def identity_record(self) -> dict[str, Any]:
        return {
            "schema": self.SCHEMA,
            "schema_version": self.schema_version,
            "capsule": self.capsule.to_record(),
            "contracts": [item.to_record() for item in self.contracts],
            "ambient_packets": [item.to_record() for item in self.ambient_packets],
            "runtime_coordinates": [item.to_record() for item in self.runtime_coordinates],
            "receipts": [item.to_record() for item in self.receipts],
            "registry_hash": self.registry_hash,
            "metadata": canonical_value(self.metadata),
            "target_free": True,
        }

    @property
    def snapshot_hash(self) -> str:
        return content_hash(self.identity_record)

    @property
    def content_hash(self) -> str:
        return self.snapshot_hash

    def to_record(self) -> dict[str, Any]:
        record = {**self.identity_record, "snapshot_hash": self.snapshot_hash}
        return _body_with_hash(record)

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "CapsuleSnapshot":
        body = _strip_and_verify_record(
            record,
            schema=cls.SCHEMA,
            allowed={
                "schema", "schema_version", "capsule", "contracts",
                "ambient_packets", "runtime_coordinates", "receipts",
                "registry_hash", "metadata", "target_free", "snapshot_hash",
            },
        )
        if body.get("target_free") is not True:
            raise ValueError("capsule snapshots must declare target_free=true")
        result = cls(
            capsule=PredictiveCapsule.from_record(body["capsule"]),
            contracts=tuple(ActionContract.from_record(item) for item in body.get("contracts", ())),
            ambient_packets=tuple(AmbientPacket.from_record(item) for item in body.get("ambient_packets", ())),
            runtime_coordinates=tuple(RuntimeCoordinates.from_record(item) for item in body.get("runtime_coordinates", ())),
            receipts=tuple(ActionReceipt.from_record(item) for item in body.get("receipts", ())),
            registry_hash=body.get("registry_hash", ""),
            metadata=body.get("metadata", {}),
            schema_version=body.get("schema_version", SCHEMA_VERSION),
        )
        if "snapshot_hash" in body and body["snapshot_hash"] != result.snapshot_hash:
            raise ValueError("snapshot_hash does not match snapshot contents")
        return result


__all__ = [
    "Grid",
    "AmbientPacket",
    "RuntimeCoordinates",
    "TargetAwareSynthesisContext",
    "TargetAwareSynthesisCoordinates",
    "StaticTransitionState",
    "ExactStaticTransitionState",
    "ActionReceipt",
    "PredictiveCapsule",
    "LeakageWitness",
    "RefinementProposal",
    "ActionContract",
    "CongruenceAudit",
    "CapsuleSnapshot",
]
