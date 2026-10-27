"""Deterministic values, hashes, and finite ARC grids for Block 10.

Block 10 records cross a persistence boundary.  This module consequently keeps
their canonical representation deliberately smaller than Python's object
model: JSON scalars, string-keyed mappings, and finite sequences only.  Caller
owned containers are copied before they are frozen, so a record's content hash
cannot change after construction.
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
import math
import re
from enum import Enum
from numbers import Integral
from types import MappingProxyType
from typing import Any, Mapping, TypeAlias

from komorebi_lasm_composition.model import (
    MAX_GRID_CELLS,
    MAX_GRID_HEIGHT,
    MAX_GRID_WIDTH,
    Grid,
    validate_grid as _block9_validate_grid,
)


SCHEMA_VERSION = 1
SNAPSHOT_FORMAT = "komorebi.lasm_action.snapshot.v1"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
FrozenValue: TypeAlias = (
    None | bool | int | float | str | tuple["FrozenValue", ...] |
    Mapping[str, "FrozenValue"]
)


def require_trimmed(value: object, label: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{label} must be a string")
    if value != value.strip() or (not allow_empty and not value):
        qualifier = "trimmed" if allow_empty else "nonempty and trimmed"
        raise ValueError(f"{label} must be {qualifier}")
    if any(ord(character) < 32 for character in value):
        raise ValueError(f"{label} cannot contain control characters")
    return value


def require_sha256(value: object, label: str, *, allow_empty: bool = False) -> str:
    text = require_trimmed(value, label, allow_empty=allow_empty)
    if text == "" and allow_empty:
        return text
    if SHA256_RE.fullmatch(text) is None:
        raise ValueError(f"{label} must be a lowercase SHA-256 digest")
    return text


def require_nonnegative_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise TypeError(f"{label} must be an integer")
    result = int(value)
    if result < 0:
        raise ValueError(f"{label} must be nonnegative")
    return result


def require_positive_int(value: object, label: str) -> int:
    result = require_nonnegative_int(value, label)
    if result == 0:
        raise ValueError(f"{label} must be positive")
    return result


def validate_grid(value: object) -> Grid:
    """Use Block 9's pre-coercion validation and return an immutable grid."""

    return _block9_validate_grid(value)


freeze_grid = validate_grid


def _canonical_value(value: Any, *, path: str, depth: int) -> Any:
    if depth > 64:
        raise ValueError("canonical value exceeds maximum nesting depth")
    if value is None or isinstance(value, (str, bool)):
        return value
    if isinstance(value, Enum):
        return _canonical_value(value.value, path=path, depth=depth + 1)
    if isinstance(value, Integral):
        return int(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"non-finite number at {path}")
        # JSON has two spellings for signed zero in common encoders.  The sign
        # is not semantically useful in these records, so normalize it.
        return 0.0 if value == 0.0 else value
    if dataclasses.is_dataclass(value):
        if hasattr(value, "to_record") and callable(value.to_record):
            return _canonical_value(value.to_record(), path=path, depth=depth + 1)
        return _canonical_value(
            {field.name: getattr(value, field.name) for field in dataclasses.fields(value)},
            path=path,
            depth=depth + 1,
        )

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
                raise ValueError(f"duplicate canonical key {key!r} at {path}")
            result[key] = _canonical_value(
                item, path=f"{path}.{key}", depth=depth + 1
            )
        return {key: result[key] for key in sorted(result)}
    if isinstance(value, (tuple, list)):
        return [
            _canonical_value(item, path=f"{path}[{index}]", depth=depth + 1)
            for index, item in enumerate(value)
        ]
    if isinstance(value, (set, frozenset)):
        items = [
            _canonical_value(item, path=f"{path}[*]", depth=depth + 1)
            for item in value
        ]
        return sorted(items, key=canonical_json)
    if hasattr(value, "to_record") and callable(value.to_record):
        return _canonical_value(value.to_record(), path=path, depth=depth + 1)
    raise TypeError(f"unsupported canonical value {type(value).__name__} at {path}")


def canonical_value(value: Any) -> Any:
    """Return a detached, JSON-compatible canonical copy of ``value``."""

    return _canonical_value(value, path="$", depth=0)


def canonical_json(value: Any) -> str:
    return json.dumps(
        canonical_value(value),
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def canonical_bytes(value: Any) -> bytes:
    return canonical_json(value).encode("utf-8")


def content_hash(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


sha256_record = content_hash


def deep_freeze(value: Any) -> FrozenValue:
    """Detach and recursively freeze one supported canonical value."""

    def freeze(item: Any) -> FrozenValue:
        if isinstance(item, dict):
            return MappingProxyType({key: freeze(child) for key, child in item.items()})
        if isinstance(item, list):
            return tuple(freeze(child) for child in item)
        return item

    return freeze(canonical_value(value))


def deep_thaw(value: Any) -> Any:
    """Return a fresh mutable canonical copy of a frozen value."""

    return canonical_value(value)


def _reject_json_constant(token: str) -> None:
    raise ValueError(f"non-finite JSON number {token!r} is forbidden")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key {key!r}")
        result[key] = value
    return result


def decode_json_bytes(payload: bytes | bytearray | str) -> Any:
    """Strictly decode UTF-8 JSON, rejecting duplicate keys and NaN values."""

    if isinstance(payload, (bytes, bytearray)):
        try:
            text = bytes(payload).decode("utf-8", errors="strict")
        except UnicodeDecodeError as error:
            raise ValueError("payload must be valid UTF-8") from error
    elif isinstance(payload, str):
        text = payload
    else:
        raise TypeError("payload must be bytes or text")
    try:
        return json.loads(
            text,
            object_pairs_hook=_unique_object,
            parse_constant=_reject_json_constant,
        )
    except json.JSONDecodeError as error:
        raise ValueError("payload must contain valid JSON") from error


def canonical_parameters(value: Mapping[str, Any]) -> str:
    """Encode one immutable operator-parameter object canonically."""

    if not isinstance(value, Mapping):
        raise TypeError("parameters must be a mapping")
    return canonical_json(value)


def decode_canonical_parameters(parameters_json: str) -> dict[str, Any]:
    """Decode a parameter object and reject any noncanonical spelling."""

    require_trimmed(parameters_json, "parameters_json")
    value = decode_json_bytes(parameters_json)
    if not isinstance(value, dict):
        raise TypeError("parameters_json must encode a JSON object")
    expected = canonical_json(value)
    if parameters_json != expected:
        raise ValueError(
            "parameters_json must use canonical sorted compact JSON; "
            f"expected {expected!r}"
        )
    return value


__all__ = [
    "Grid",
    "FrozenValue",
    "MAX_GRID_HEIGHT",
    "MAX_GRID_WIDTH",
    "MAX_GRID_CELLS",
    "SCHEMA_VERSION",
    "SNAPSHOT_FORMAT",
    "SHA256_RE",
    "canonical_value",
    "canonical_json",
    "canonical_bytes",
    "content_hash",
    "sha256_record",
    "deep_freeze",
    "deep_thaw",
    "decode_json_bytes",
    "canonical_parameters",
    "decode_canonical_parameters",
    "validate_grid",
    "freeze_grid",
    "require_trimmed",
    "require_sha256",
    "require_nonnegative_int",
    "require_positive_int",
]
