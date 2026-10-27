"""Canonical immutable records for recursive PR-LASM composition.

The records in this module are deliberately small and dependency free.  In
particular, executable leaf parameters are stored as canonical JSON text rather
than as a mutable mapping.  Semantic identity is kept separate from derivation
evidence so that training provenance can never change the identity of a program.
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from enum import Enum
from numbers import Integral
from types import MappingProxyType
from typing import Any, Literal, Mapping, Sequence, TypeAlias


Grid: TypeAlias = tuple[tuple[int, ...], ...]
Measure: TypeAlias = tuple[int, int, int, int]
ProgressMode: TypeAlias = Literal[
    "residual_subset", "strict_descent", "shape_correction"
]
LeafNamespace: TypeAlias = Literal["atomic", "block6", "block8"]

MAX_GRID_HEIGHT = 30
MAX_GRID_WIDTH = 30
MAX_GRID_CELLS = 900
SCHEMA_VERSION = 1

_LEAF_NAMESPACES = frozenset({"atomic", "block6", "block8"})
_LEAF_STATUSES = frozenset(
    {"primitive", "candidate", "provisional", "stable", "retired"}
)
_PROGRESS_MODES = frozenset(
    {"residual_subset", "strict_descent", "shape_correction"}
)


def _require_trimmed(value: object, label: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{label} must be a string")
    if value != value.strip() or (not allow_empty and not value):
        qualifier = "trimmed" if allow_empty else "nonempty and trimmed"
        raise ValueError(f"{label} must be {qualifier}")
    return value


def _require_positive_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise TypeError(f"{label} must be an integer")
    normalized = int(value)
    if normalized <= 0:
        raise ValueError(f"{label} must be positive")
    return normalized


def _require_nonnegative_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise TypeError(f"{label} must be an integer")
    normalized = int(value)
    if normalized < 0:
        raise ValueError(f"{label} must be nonnegative")
    return normalized


def _rows_without_coercion(value: object) -> list[object]:
    """Expose grid rows without first asking NumPy to coerce their dtype.

    Calling ``np.asarray(value, dtype=int)`` before validation accepts booleans,
    truncates floats, and historically made some ragged inputs version dependent.
    This helper intentionally performs structural inspection first.
    """

    if isinstance(value, (str, bytes, bytearray, Mapping)):
        raise TypeError("grid must be a two-dimensional row sequence")
    ndim = getattr(value, "ndim", None)
    if ndim is not None and ndim != 2:
        raise ValueError("grid must be two-dimensional")
    try:
        row_count = len(value)  # type: ignore[arg-type]
    except (TypeError, AttributeError) as error:
        raise TypeError("grid must be a finite two-dimensional row sequence") from error
    if row_count > MAX_GRID_HEIGHT:
        raise ValueError(f"grid height must not exceed {MAX_GRID_HEIGHT}")
    try:
        return [value[index] for index in range(row_count)]  # type: ignore[index]
    except (TypeError, KeyError, IndexError) as error:
        raise TypeError("grid rows must support deterministic integer indexing") from error


def _cells_without_coercion(row: object, row_index: int) -> list[object]:
    if isinstance(row, (str, bytes, bytearray, Mapping)):
        raise TypeError(f"grid row {row_index} must be a cell sequence")
    ndim = getattr(row, "ndim", None)
    if ndim is not None and ndim != 1:
        raise ValueError(f"grid row {row_index} must be one-dimensional")
    try:
        cell_count = len(row)  # type: ignore[arg-type]
    except (TypeError, AttributeError) as error:
        raise TypeError(f"grid row {row_index} must be a finite cell sequence") from error
    if cell_count > MAX_GRID_WIDTH:
        raise ValueError(f"grid width must not exceed {MAX_GRID_WIDTH}")
    try:
        return [row[index] for index in range(cell_count)]  # type: ignore[index]
    except (TypeError, KeyError, IndexError) as error:
        raise TypeError(
            f"grid row {row_index} must support deterministic integer indexing"
        ) from error


def validate_grid(value: object) -> Grid:
    """Validate an ARC grid *before* coercion and return its frozen form.

    A valid grid is rectangular, nonempty, at most 30 by 30 (and 900 cells),
    and contains only genuine integer colors in the inclusive range 0..9.
    Booleans and integral-looking floating-point values are rejected.
    """

    rows = _rows_without_coercion(value)
    height = len(rows)
    if height == 0:
        raise ValueError("grid must contain at least one row")
    if height > MAX_GRID_HEIGHT:
        raise ValueError(f"grid height must not exceed {MAX_GRID_HEIGHT}")

    inspected: list[list[object]] = []
    width: int | None = None
    for row_index, row in enumerate(rows):
        cells = _cells_without_coercion(row, row_index)
        if width is None:
            width = len(cells)
            if width == 0:
                raise ValueError("grid rows must contain at least one cell")
            if width > MAX_GRID_WIDTH:
                raise ValueError(f"grid width must not exceed {MAX_GRID_WIDTH}")
        elif len(cells) != width:
            raise ValueError("grid must be rectangular")
        inspected.append(cells)

    assert width is not None
    if height * width > MAX_GRID_CELLS:
        raise ValueError(f"grid must not exceed {MAX_GRID_CELLS} cells")

    # Validation intentionally precedes the calls to int below.
    for row_index, cells in enumerate(inspected):
        for column_index, cell in enumerate(cells):
            if isinstance(cell, bool) or not isinstance(cell, Integral):
                raise TypeError(
                    f"grid cell ({row_index}, {column_index}) must be an integer"
                )
            if not 0 <= int(cell) <= 9:
                raise ValueError(
                    f"grid cell ({row_index}, {column_index}) must be in 0..9"
                )

    return tuple(tuple(int(cell) for cell in cells) for cells in inspected)


freeze_grid = validate_grid


def _canonical_value(value: Any, *, path: str = "$", depth: int = 0) -> Any:
    if depth > 64:
        raise ValueError("canonical value exceeds maximum nesting depth")
    if value is None or isinstance(value, (str, bool)):
        return value
    if isinstance(value, Integral):
        return int(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"non-finite number at {path}")
        return value
    if isinstance(value, Enum):
        return _canonical_value(value.value, path=path, depth=depth + 1)

    # NumPy scalar and array support is intentionally lossless.  Grid validation
    # itself does not use this path and therefore never benefits from coercion.
    module_name = type(value).__module__.split(".", 1)[0]
    if module_name == "numpy":
        if hasattr(value, "ndim") and int(value.ndim) > 0:
            return _canonical_value(value.tolist(), path=path, depth=depth + 1)
        if hasattr(value, "item"):
            return _canonical_value(value.item(), path=path, depth=depth + 1)

    if isinstance(value, Mapping):
        result: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError(f"canonical mapping key at {path} must be a string")
            if key in result:
                raise ValueError(f"duplicate canonical mapping key {key!r} at {path}")
            result[key] = _canonical_value(
                item, path=f"{path}.{key}", depth=depth + 1
            )
        return {key: result[key] for key in sorted(result)}
    if isinstance(value, (tuple, list)):
        return [
            _canonical_value(item, path=f"{path}[{index}]", depth=depth + 1)
            for index, item in enumerate(value)
        ]
    if hasattr(value, "to_record") and callable(value.to_record):
        return _canonical_value(value.to_record(), path=path, depth=depth + 1)
    raise TypeError(f"unsupported canonical value {type(value).__name__} at {path}")


def canonical_value(value: Any) -> Any:
    """Return a JSON-safe, recursively canonical copy of ``value``."""

    return _canonical_value(value)


def canonical_json(value: Any) -> str:
    """Encode ``value`` with the package's unique JSON representation."""

    return json.dumps(
        canonical_value(value),
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def sha256_record(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _reject_json_constant(token: str) -> None:
    raise ValueError(f"non-finite JSON number {token!r} is forbidden")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key {key!r}")
        result[key] = value
    return result


def decode_canonical_parameters(parameters_json: str) -> dict[str, Any]:
    """Decode and verify a canonical parameter object."""

    _require_trimmed(parameters_json, "parameters_json")
    try:
        value = json.loads(
            parameters_json,
            object_pairs_hook=_unique_object,
            parse_constant=_reject_json_constant,
        )
    except (json.JSONDecodeError, TypeError) as error:
        raise ValueError("parameters_json must contain valid JSON") from error
    if not isinstance(value, dict):
        raise TypeError("parameters_json must encode a JSON object")
    expected = canonical_json(value)
    if parameters_json != expected:
        raise ValueError(
            "parameters_json must use canonical sorted compact JSON; "
            f"expected {expected!r}"
        )
    return value


def canonical_parameters(value: Mapping[str, Any]) -> str:
    """Create canonical parameter JSON from a mapping."""

    if not isinstance(value, Mapping):
        raise TypeError("leaf parameters must be a mapping")
    return canonical_json(value)


def _deep_immutable(value: Any) -> Any:
    if isinstance(value, dict):
        return MappingProxyType({key: _deep_immutable(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_deep_immutable(item) for item in value)
    return value


def _validate_digestish(value: object, label: str, *, allow_empty: bool = True) -> str:
    text = _require_trimmed(value, label, allow_empty=allow_empty)
    if any(ord(character) < 33 or ord(character) > 126 for character in text):
        raise ValueError(f"{label} must contain printable non-whitespace ASCII")
    return text


def _normalize_measure(value: Sequence[object], label: str) -> Measure:
    if len(value) != 4:
        raise ValueError(f"{label} must contain exactly four coordinates")
    return tuple(
        _require_nonnegative_int(coordinate, f"{label}[{index}]")
        for index, coordinate in enumerate(value)
    )  # type: ignore[return-value]


@dataclass(frozen=True, slots=True)
class LeafInvocation:
    """One typed ``grid -> grid`` primitive in an expanded composition."""

    namespace: LeafNamespace
    family: str
    macro_schema: str
    parameters_json: str
    source_macro_id: str
    cost: int
    status: str = "primitive"
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.namespace not in _LEAF_NAMESPACES:
            raise ValueError(
                "namespace must be one of 'atomic', 'block6', or 'block8'"
            )
        _require_trimmed(self.family, "family")
        _require_trimmed(self.macro_schema, "macro_schema")
        decode_canonical_parameters(self.parameters_json)
        _validate_digestish(self.source_macro_id, "source_macro_id")
        _require_positive_int(self.cost, "cost")
        if self.status not in _LEAF_STATUSES:
            raise ValueError(
                "status must be primitive, candidate, provisional, stable, or retired"
            )
        if isinstance(self.schema_version, bool) or self.schema_version != SCHEMA_VERSION:
            raise ValueError(f"schema_version must equal {SCHEMA_VERSION}")

    @classmethod
    def from_parameters(
        cls,
        namespace: LeafNamespace,
        family: str,
        macro_schema: str,
        parameters: Mapping[str, Any],
        source_macro_id: str,
        cost: int,
        status: str = "primitive",
    ) -> "LeafInvocation":
        return cls(
            namespace=namespace,
            family=family,
            macro_schema=macro_schema,
            parameters_json=canonical_parameters(parameters),
            source_macro_id=source_macro_id,
            cost=cost,
            status=status,
        )

    @property
    def parameters(self) -> Mapping[str, Any]:
        """A recursively immutable decoded view of the parameter object."""

        return _deep_immutable(decode_canonical_parameters(self.parameters_json))

    @property
    def parameters_record(self) -> dict[str, Any]:
        """A fresh mutable copy for calls into inherited executors."""

        return decode_canonical_parameters(self.parameters_json)

    @property
    def semantic_record(self) -> dict[str, Any]:
        return {
            "schema": "komorebi.lasm_composition.leaf_semantics",
            "schema_version": self.schema_version,
            "namespace": self.namespace,
            "family": self.family,
            "macro_schema": self.macro_schema,
            "parameters": self.parameters_record,
            "input_type": "grid",
            "output_type": "grid",
        }

    @property
    def semantic_hash(self) -> str:
        return sha256_record(self.semantic_record)

    @property
    def syntax_record(self) -> dict[str, Any]:
        return {
            **self.semantic_record,
            "source_macro_id": self.source_macro_id,
            "status": self.status,
        }

    @property
    def syntax_hash(self) -> str:
        return sha256_record(self.syntax_record)

    def to_record(self) -> dict[str, Any]:
        record = {
            "schema": "komorebi.lasm_composition.leaf_invocation",
            "schema_version": self.schema_version,
            "namespace": self.namespace,
            "family": self.family,
            "macro_schema": self.macro_schema,
            "parameters": self.parameters_record,
            "parameters_json": self.parameters_json,
            "source_macro_id": self.source_macro_id,
            "cost": int(self.cost),
            "status": self.status,
            "input_type": "grid",
            "output_type": "grid",
            "semantic_hash": self.semantic_hash,
            "syntax_hash": self.syntax_hash,
        }
        record["content_hash"] = sha256_record(record)
        return record


@dataclass(frozen=True, slots=True)
class ExampleResidual:
    """Background-independent mismatch summary for one demonstration."""

    current_hash: str
    target_hash: str
    current_shape: tuple[int, int]
    target_shape: tuple[int, int]
    measure: Measure
    mismatch_count: int
    mismatch_components: int
    obstruction_kinds: tuple[str, ...]
    packet_id: str = ""
    background_color: int = 0
    added_cells: int = 0
    removed_cells: int = 0
    recolored_cells: int = 0
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(self, "current_shape", tuple(self.current_shape))
        object.__setattr__(self, "target_shape", tuple(self.target_shape))
        object.__setattr__(self, "measure", tuple(self.measure))
        object.__setattr__(self, "obstruction_kinds", tuple(self.obstruction_kinds))
        _validate_digestish(self.current_hash, "current_hash", allow_empty=False)
        _validate_digestish(self.target_hash, "target_hash", allow_empty=False)
        for label, shape in (
            ("current_shape", self.current_shape),
            ("target_shape", self.target_shape),
        ):
            if len(shape) != 2:
                raise ValueError(f"{label} must contain height and width")
            for index, coordinate in enumerate(shape):
                _require_positive_int(coordinate, f"{label}[{index}]")
        normalized_measure = _normalize_measure(self.measure, "measure")
        if tuple(self.measure) != normalized_measure:
            object.__setattr__(self, "measure", normalized_measure)
        for label, value in (
            ("mismatch_count", self.mismatch_count),
            ("mismatch_components", self.mismatch_components),
            ("added_cells", self.added_cells),
            ("removed_cells", self.removed_cells),
            ("recolored_cells", self.recolored_cells),
        ):
            _require_nonnegative_int(value, label)
        if (
            isinstance(self.background_color, bool)
            or not isinstance(self.background_color, Integral)
            or not 0 <= int(self.background_color) <= 9
        ):
            raise ValueError("background_color must be an integer in 0..9")
        if not self.obstruction_kinds:
            raise ValueError("obstruction_kinds must be nonempty")
        if tuple(sorted(set(self.obstruction_kinds))) != self.obstruction_kinds:
            raise ValueError("obstruction_kinds must be unique and sorted")
        for kind in self.obstruction_kinds:
            _require_trimmed(kind, "obstruction kind")
        if isinstance(self.schema_version, bool) or self.schema_version != SCHEMA_VERSION:
            raise ValueError(f"schema_version must equal {SCHEMA_VERSION}")
        expected = sha256_record(self.identity_record)
        if self.packet_id:
            if self.packet_id != expected:
                raise ValueError("packet_id does not match residual contents")
        else:
            object.__setattr__(self, "packet_id", expected)

    @property
    def exact(self) -> bool:
        return self.measure == (0, 0, 0, 0)

    @property
    def identity_record(self) -> dict[str, Any]:
        return {
            "schema": "komorebi.lasm_composition.example_residual",
            "schema_version": self.schema_version,
            "current_hash": self.current_hash,
            "target_hash": self.target_hash,
            "current_shape": list(self.current_shape),
            "target_shape": list(self.target_shape),
            "measure": list(self.measure),
            "mismatch_count": int(self.mismatch_count),
            "mismatch_components": int(self.mismatch_components),
            "obstruction_kinds": list(self.obstruction_kinds),
            "background_color": int(self.background_color),
            "added_cells": int(self.added_cells),
            "removed_cells": int(self.removed_cells),
            "recolored_cells": int(self.recolored_cells),
        }

    def to_record(self) -> dict[str, Any]:
        record = {**self.identity_record, "packet_id": self.packet_id}
        record["content_hash"] = sha256_record(record)
        return record


@dataclass(frozen=True, slots=True)
class ResidualBatch:
    examples: tuple[ExampleResidual, ...]
    aggregate_packet_id: str = ""
    common_kinds: tuple[str, ...] = ()
    union_kinds: tuple[str, ...] = ()
    route_lanes: tuple[str, ...] = ()
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(self, "examples", tuple(self.examples))
        object.__setattr__(self, "common_kinds", tuple(self.common_kinds))
        object.__setattr__(self, "union_kinds", tuple(self.union_kinds))
        object.__setattr__(self, "route_lanes", tuple(self.route_lanes))
        if not self.examples:
            raise ValueError("a residual batch needs at least one example")
        if not all(isinstance(example, ExampleResidual) for example in self.examples):
            raise TypeError("residual batch examples must be ExampleResidual records")
        union = tuple(
            sorted({kind for example in self.examples for kind in example.obstruction_kinds})
        )
        common_set = set(self.examples[0].obstruction_kinds)
        for example in self.examples[1:]:
            common_set.intersection_update(example.obstruction_kinds)
        common = tuple(sorted(common_set))
        if self.union_kinds and self.union_kinds != union:
            raise ValueError("union_kinds does not match example residuals")
        if self.common_kinds and self.common_kinds != common:
            raise ValueError("common_kinds does not match example residuals")
        if not self.union_kinds:
            object.__setattr__(self, "union_kinds", union)
        if not self.common_kinds:
            object.__setattr__(self, "common_kinds", common)
        if tuple(dict.fromkeys(self.route_lanes)) != self.route_lanes:
            raise ValueError("route_lanes must be unique and ordered")
        for lane in self.route_lanes:
            _require_trimmed(lane, "route lane")
        if isinstance(self.schema_version, bool) or self.schema_version != SCHEMA_VERSION:
            raise ValueError(f"schema_version must equal {SCHEMA_VERSION}")
        expected = sha256_record(self.identity_record)
        if self.aggregate_packet_id:
            if self.aggregate_packet_id != expected:
                raise ValueError("aggregate_packet_id does not match residual batch")
        else:
            object.__setattr__(self, "aggregate_packet_id", expected)

    @property
    def exact(self) -> bool:
        return all(example.exact for example in self.examples)

    @property
    def measures(self) -> tuple[Measure, ...]:
        return tuple(example.measure for example in self.examples)

    @property
    def identity_record(self) -> dict[str, Any]:
        return {
            "schema": "komorebi.lasm_composition.residual_batch",
            "schema_version": self.schema_version,
            "examples": [example.packet_id for example in self.examples],
            "common_kinds": list(self.common_kinds),
            "union_kinds": list(self.union_kinds),
            "route_lanes": list(self.route_lanes),
        }

    def to_record(self) -> dict[str, Any]:
        record = {
            **self.identity_record,
            "aggregate_packet_id": self.aggregate_packet_id,
            "example_records": [example.to_record() for example in self.examples],
        }
        record["content_hash"] = sha256_record(record)
        return record


@dataclass(frozen=True, slots=True)
class ProgressCertificate:
    """Proof object for one monotone transition across all demonstrations."""

    before_packet_id: str
    after_packet_id: str
    before_measures: tuple[Measure, ...]
    after_measures: tuple[Measure, ...]
    corrected_cells: tuple[int, ...]
    introduced_errors: tuple[int, ...]
    mode: ProgressMode
    before_state_hash: str = ""
    after_state_hash: str = ""
    strict_demo_indices: tuple[int, ...] = ()
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "before_measures", tuple(tuple(value) for value in self.before_measures)
        )
        object.__setattr__(
            self, "after_measures", tuple(tuple(value) for value in self.after_measures)
        )
        object.__setattr__(self, "corrected_cells", tuple(self.corrected_cells))
        object.__setattr__(self, "introduced_errors", tuple(self.introduced_errors))
        object.__setattr__(self, "strict_demo_indices", tuple(self.strict_demo_indices))
        _validate_digestish(self.before_packet_id, "before_packet_id", allow_empty=False)
        _validate_digestish(self.after_packet_id, "after_packet_id", allow_empty=False)
        if self.before_packet_id == self.after_packet_id:
            raise ValueError("a progress certificate cannot certify a no-op packet")
        count = len(self.before_measures)
        if count == 0 or len(self.after_measures) != count:
            raise ValueError("before and after measures must have equal nonzero length")
        if len(self.corrected_cells) != count or len(self.introduced_errors) != count:
            raise ValueError("cell-count vectors must match the demonstration count")
        normalized_before = tuple(
            _normalize_measure(measure, f"before_measures[{index}]")
            for index, measure in enumerate(self.before_measures)
        )
        normalized_after = tuple(
            _normalize_measure(measure, f"after_measures[{index}]")
            for index, measure in enumerate(self.after_measures)
        )
        if normalized_before != self.before_measures:
            object.__setattr__(self, "before_measures", normalized_before)
        if normalized_after != self.after_measures:
            object.__setattr__(self, "after_measures", normalized_after)
        for index, (before, after) in enumerate(zip(normalized_before, normalized_after)):
            if after > before:
                raise ValueError(f"demonstration {index} worsens under the residual measure")
            if before == (0, 0, 0, 0) and after != before:
                raise ValueError(f"exact demonstration {index} was broken")
        strict = tuple(
            index
            for index, (before, after) in enumerate(zip(normalized_before, normalized_after))
            if after < before
        )
        if not strict:
            raise ValueError("at least one demonstration must strictly decrease")
        if self.strict_demo_indices and self.strict_demo_indices != strict:
            raise ValueError("strict_demo_indices does not match the measures")
        if not self.strict_demo_indices:
            object.__setattr__(self, "strict_demo_indices", strict)
        for label, values in (
            ("corrected_cells", self.corrected_cells),
            ("introduced_errors", self.introduced_errors),
        ):
            for index, value in enumerate(values):
                _require_nonnegative_int(value, f"{label}[{index}]")
        for index, (before, after, corrected, introduced) in enumerate(
            zip(
                normalized_before,
                normalized_after,
                self.corrected_cells,
                self.introduced_errors,
            )
        ):
            # For finite mismatch sets B and A,
            # |B| - |A| = |B \\ A| - |A \\ B|.  This does not reconstruct the
            # cell sets, but it prevents forged count vectors from contradicting
            # the certified residual measures.
            if corrected > before[2] or introduced > after[2]:
                raise ValueError(
                    f"cell-transition counts exceed mismatch totals for demonstration {index}"
                )
            if corrected - introduced != before[2] - after[2]:
                raise ValueError(
                    f"cell-transition counts contradict mismatch descent for demonstration {index}"
                )
        if self.mode not in _PROGRESS_MODES:
            raise ValueError("invalid progress-certificate mode")
        if self.mode == "residual_subset" and any(self.introduced_errors):
            raise ValueError("residual_subset certificates cannot introduce errors")
        if self.mode == "shape_correction" and not any(
            after[:2] < before[:2]
            for before, after in zip(normalized_before, normalized_after)
        ):
            raise ValueError("shape_correction must strictly improve a shape coordinate")
        if self.before_state_hash:
            _validate_digestish(self.before_state_hash, "before_state_hash")
        if self.after_state_hash:
            _validate_digestish(self.after_state_hash, "after_state_hash")
        if self.before_state_hash and self.before_state_hash == self.after_state_hash:
            raise ValueError("a progress certificate cannot return to the same state")
        if isinstance(self.schema_version, bool) or self.schema_version != SCHEMA_VERSION:
            raise ValueError(f"schema_version must equal {SCHEMA_VERSION}")

    @property
    def certificate_hash(self) -> str:
        return sha256_record(self.identity_record)

    @property
    def identity_record(self) -> dict[str, Any]:
        return {
            "schema": "komorebi.lasm_composition.progress_certificate",
            "schema_version": self.schema_version,
            "before_packet_id": self.before_packet_id,
            "after_packet_id": self.after_packet_id,
            "before_measures": [list(value) for value in self.before_measures],
            "after_measures": [list(value) for value in self.after_measures],
            "corrected_cells": list(self.corrected_cells),
            "introduced_errors": list(self.introduced_errors),
            "mode": self.mode,
            "before_state_hash": self.before_state_hash,
            "after_state_hash": self.after_state_hash,
            "strict_demo_indices": list(self.strict_demo_indices),
        }

    def to_record(self) -> dict[str, Any]:
        record = {**self.identity_record, "certificate_hash": self.certificate_hash}
        record["content_hash"] = sha256_record(record)
        return record


@dataclass(frozen=True, slots=True)
class CompositeProgram:
    """An ordered expanded leaf program with separately hashed derivation evidence."""

    leaves: tuple[LeafInvocation, ...]
    certificates: tuple[ProgressCertificate, ...]
    training_hashes: tuple[str, ...]
    bank_id: str
    registry_hash: str
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(self, "leaves", tuple(self.leaves))
        object.__setattr__(self, "certificates", tuple(self.certificates))
        object.__setattr__(self, "training_hashes", tuple(self.training_hashes))
        if not self.leaves:
            raise ValueError("a composite program needs at least one leaf")
        if not all(isinstance(leaf, LeafInvocation) for leaf in self.leaves):
            raise TypeError("composite leaves must be LeafInvocation records")
        if len(self.certificates) != len(self.leaves):
            raise ValueError("every expanded leaf must have one progress certificate")
        if not all(
            isinstance(certificate, ProgressCertificate)
            for certificate in self.certificates
        ):
            raise TypeError("certificates must be ProgressCertificate records")
        if not self.training_hashes:
            raise ValueError("training_hashes must be nonempty")
        for index, digest in enumerate(self.training_hashes):
            _validate_digestish(digest, f"training_hashes[{index}]", allow_empty=False)
        _validate_digestish(self.bank_id, "bank_id")
        _validate_digestish(self.registry_hash, "registry_hash")
        if isinstance(self.schema_version, bool) or self.schema_version != SCHEMA_VERSION:
            raise ValueError(f"schema_version must equal {SCHEMA_VERSION}")
        for index in range(1, len(self.certificates)):
            previous = self.certificates[index - 1]
            current = self.certificates[index]
            if previous.after_packet_id != current.before_packet_id:
                raise ValueError("progress certificates must form a packet chain")
            if (
                previous.after_state_hash
                and current.before_state_hash
                and previous.after_state_hash != current.before_state_hash
            ):
                raise ValueError("progress certificates must form a state chain")

    @property
    def leaf_count(self) -> int:
        return len(self.leaves)

    @property
    def total_cost(self) -> int:
        return sum(int(leaf.cost) for leaf in self.leaves)

    @property
    def semantic_record(self) -> dict[str, Any]:
        # No training hashes, certificates, bank identity, cost, or provenance.
        return {
            "schema": "komorebi.lasm_composition.composite_semantics",
            "schema_version": self.schema_version,
            "expanded_leaves": [leaf.semantic_record for leaf in self.leaves],
        }

    @property
    def semantic_hash(self) -> str:
        return sha256_record(self.semantic_record)

    @property
    def syntax_record(self) -> dict[str, Any]:
        return {
            "schema": "komorebi.lasm_composition.composite_syntax",
            "schema_version": self.schema_version,
            "leaves": [leaf.syntax_record for leaf in self.leaves],
        }

    @property
    def syntax_hash(self) -> str:
        return sha256_record(self.syntax_record)

    @property
    def derivation_record(self) -> dict[str, Any]:
        return {
            "schema": "komorebi.lasm_composition.composite_derivation",
            "schema_version": self.schema_version,
            "semantic_hash": self.semantic_hash,
            "syntax_hash": self.syntax_hash,
            "training_hashes": list(self.training_hashes),
            "certificates": [
                certificate.to_record() for certificate in self.certificates
            ],
            "bank_id": self.bank_id,
            "registry_hash": self.registry_hash,
        }

    @property
    def derivation_hash(self) -> str:
        return sha256_record(self.derivation_record)

    def to_record(self) -> dict[str, Any]:
        record = {
            "schema": "komorebi.lasm_composition.composite_program",
            "schema_version": self.schema_version,
            "leaves": [leaf.to_record() for leaf in self.leaves],
            "certificates": [
                certificate.to_record() for certificate in self.certificates
            ],
            "training_hashes": list(self.training_hashes),
            "bank_id": self.bank_id,
            "registry_hash": self.registry_hash,
            "leaf_count": self.leaf_count,
            "total_cost": self.total_cost,
            "semantic_hash": self.semantic_hash,
            "syntax_hash": self.syntax_hash,
            "derivation_hash": self.derivation_hash,
        }
        record["content_hash"] = sha256_record(record)
        return record


@dataclass(frozen=True, slots=True)
class CompositionLimits:
    """Deterministic count budgets for recursive search."""

    max_depth: int = 3
    max_frontier: int = 256
    max_proposals_per_state: int = 512
    max_expansions: int = 50_000
    max_total_cost: int = 64
    progress_mode: ProgressMode = "residual_subset"
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        for label, value in (
            ("max_depth", self.max_depth),
            ("max_frontier", self.max_frontier),
            ("max_proposals_per_state", self.max_proposals_per_state),
            ("max_expansions", self.max_expansions),
            ("max_total_cost", self.max_total_cost),
        ):
            _require_positive_int(value, label)
        if self.progress_mode not in _PROGRESS_MODES:
            raise ValueError("invalid progress_mode")
        if isinstance(self.schema_version, bool) or self.schema_version != SCHEMA_VERSION:
            raise ValueError(f"schema_version must equal {SCHEMA_VERSION}")

    # Compatibility aliases make the limit meaning explicit at call sites.
    @property
    def primitive_leaf_depth(self) -> int:
        return self.max_depth

    @property
    def frontier_limit(self) -> int:
        return self.max_frontier

    @property
    def proposal_limit_per_state(self) -> int:
        return self.max_proposals_per_state

    @property
    def expansion_limit(self) -> int:
        return self.max_expansions

    def to_record(self) -> dict[str, Any]:
        record = {
            "schema": "komorebi.lasm_composition.limits",
            "schema_version": self.schema_version,
            "max_depth": int(self.max_depth),
            "max_frontier": int(self.max_frontier),
            "max_proposals_per_state": int(self.max_proposals_per_state),
            "max_expansions": int(self.max_expansions),
            "max_total_cost": int(self.max_total_cost),
            "progress_mode": self.progress_mode,
        }
        record["content_hash"] = sha256_record(record)
        return record


@dataclass(frozen=True, slots=True)
class CompositionTrace:
    """Immutable deterministic search-accounting record."""

    root_packet_id: str
    lanes_attempted: tuple[str, ...] = ()
    states_expanded: int = 0
    proposals_considered: int = 0
    transitions_accepted: int = 0
    exact_programs: int = 0
    behavior_classes: int = 0
    max_depth_reached: int = 0
    rejection_counts: tuple[tuple[str, int], ...] = ()
    limit_reached: str = ""
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(self, "lanes_attempted", tuple(self.lanes_attempted))
        object.__setattr__(
            self,
            "rejection_counts",
            tuple((name, count) for name, count in self.rejection_counts),
        )
        _validate_digestish(self.root_packet_id, "root_packet_id", allow_empty=False)
        if tuple(dict.fromkeys(self.lanes_attempted)) != self.lanes_attempted:
            raise ValueError("lanes_attempted must be unique and ordered")
        for lane in self.lanes_attempted:
            _require_trimmed(lane, "attempted lane")
        for label, value in (
            ("states_expanded", self.states_expanded),
            ("proposals_considered", self.proposals_considered),
            ("transitions_accepted", self.transitions_accepted),
            ("exact_programs", self.exact_programs),
            ("behavior_classes", self.behavior_classes),
            ("max_depth_reached", self.max_depth_reached),
        ):
            _require_nonnegative_int(value, label)
        names = tuple(name for name, _ in self.rejection_counts)
        if names != tuple(sorted(set(names))):
            raise ValueError("rejection_counts must have unique sorted names")
        for name, count in self.rejection_counts:
            _require_trimmed(name, "rejection category")
            _require_nonnegative_int(count, f"rejection count {name!r}")
        _require_trimmed(self.limit_reached, "limit_reached", allow_empty=True)
        if isinstance(self.schema_version, bool) or self.schema_version != SCHEMA_VERSION:
            raise ValueError(f"schema_version must equal {SCHEMA_VERSION}")

    @property
    def trace_hash(self) -> str:
        return sha256_record(self.identity_record)

    @property
    def identity_record(self) -> dict[str, Any]:
        return {
            "schema": "komorebi.lasm_composition.trace",
            "schema_version": self.schema_version,
            "root_packet_id": self.root_packet_id,
            "lanes_attempted": list(self.lanes_attempted),
            "states_expanded": int(self.states_expanded),
            "proposals_considered": int(self.proposals_considered),
            "transitions_accepted": int(self.transitions_accepted),
            "exact_programs": int(self.exact_programs),
            "behavior_classes": int(self.behavior_classes),
            "max_depth_reached": int(self.max_depth_reached),
            "rejection_counts": dict(self.rejection_counts),
            "limit_reached": self.limit_reached,
        }

    def to_record(self) -> dict[str, Any]:
        record = {**self.identity_record, "trace_hash": self.trace_hash}
        record["content_hash"] = sha256_record(record)
        return record


@dataclass(frozen=True, slots=True)
class CompositionCandidate:
    """One exact composed candidate and its complete behavior identity."""

    program: CompositeProgram
    training_outputs: tuple[Grid, ...]
    test_outputs: tuple[Grid, ...]
    native_execution_hash: str
    ir_program_hash: str
    prefix_behavior_hashes: tuple[str, ...] = ()
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self.program, CompositeProgram):
            raise TypeError("program must be a CompositeProgram")
        object.__setattr__(
            self,
            "training_outputs",
            tuple(validate_grid(grid) for grid in self.training_outputs),
        )
        object.__setattr__(
            self, "test_outputs", tuple(validate_grid(grid) for grid in self.test_outputs)
        )
        object.__setattr__(
            self, "prefix_behavior_hashes", tuple(self.prefix_behavior_hashes)
        )
        _validate_digestish(
            self.native_execution_hash, "native_execution_hash", allow_empty=False
        )
        _validate_digestish(self.ir_program_hash, "ir_program_hash", allow_empty=False)
        for index, digest in enumerate(self.prefix_behavior_hashes):
            _validate_digestish(
                digest, f"prefix_behavior_hashes[{index}]", allow_empty=False
            )
        if self.prefix_behavior_hashes and len(self.prefix_behavior_hashes) != len(
            self.program.leaves
        ):
            raise ValueError("prefix hashes must correspond one-to-one with leaves")
        if isinstance(self.schema_version, bool) or self.schema_version != SCHEMA_VERSION:
            raise ValueError(f"schema_version must equal {SCHEMA_VERSION}")

    @property
    def behavior_record(self) -> dict[str, Any]:
        # The quotient covers both demonstration and sanitized test-input behavior.
        return {
            "training_outputs": canonical_value(self.training_outputs),
            "test_outputs": canonical_value(self.test_outputs),
        }

    @property
    def behavior_hash(self) -> str:
        return sha256_record(self.behavior_record)

    @property
    def candidate_hash(self) -> str:
        return sha256_record(
            {
                "program": self.program.derivation_hash,
                "behavior": self.behavior_hash,
                "native_execution_hash": self.native_execution_hash,
                "ir_program_hash": self.ir_program_hash,
                "prefix_behavior_hashes": list(self.prefix_behavior_hashes),
            }
        )

    def to_record(self) -> dict[str, Any]:
        record = {
            "schema": "komorebi.lasm_composition.candidate",
            "schema_version": self.schema_version,
            "program": self.program.to_record(),
            "training_outputs": canonical_value(self.training_outputs),
            "test_outputs": canonical_value(self.test_outputs),
            "behavior_hash": self.behavior_hash,
            "native_execution_hash": self.native_execution_hash,
            "ir_program_hash": self.ir_program_hash,
            "prefix_behavior_hashes": list(self.prefix_behavior_hashes),
            "candidate_hash": self.candidate_hash,
        }
        record["content_hash"] = sha256_record(record)
        return record


CandidateExecution = CompositionCandidate
CompositionCandidateExecution = CompositionCandidate


__all__ = [
    "CandidateExecution",
    "CompositionCandidate",
    "CompositionCandidateExecution",
    "CompositionLimits",
    "CompositionTrace",
    "CompositeProgram",
    "ExampleResidual",
    "Grid",
    "LeafInvocation",
    "LeafNamespace",
    "MAX_GRID_CELLS",
    "MAX_GRID_HEIGHT",
    "MAX_GRID_WIDTH",
    "Measure",
    "ProgressCertificate",
    "ProgressMode",
    "ResidualBatch",
    "SCHEMA_VERSION",
    "canonical_json",
    "canonical_parameters",
    "canonical_value",
    "decode_canonical_parameters",
    "freeze_grid",
    "sha256_record",
    "validate_grid",
]
