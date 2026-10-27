"""Exact partial gauge adapters for task-local PR-LASM programs.

The adapters in this module never replace an ARC raster with a lossy summary.
They are finite, typed changes of coordinates around an authoritative exact
grid.  Every forward map has an explicit inverse on its declared image.  A
map that is not applicable raises :class:`GaugeUndefinedError`; it never
silently clips, fills, guesses a color, or chooses one member of an ambiguous
orbit.

The principal transport contract is::

    physical_output = G_out.inverse(M(G_in.forward(physical_input)))

``G_in`` and ``G_out`` are intentionally separate.  This is required for
shape-changing mechanisms and prevents the common but unsound assumption that
one conjugating gauge can describe both sides of a program.
"""
from __future__ import annotations

import itertools
import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from numbers import Integral
from types import MappingProxyType
from typing import Any, Callable, Iterable, Mapping, Sequence, TypeAlias

from .canonical import (
    Grid,
    canonical_json,
    canonical_value,
    sha256_record,
    validate_grid,
)


Shape: TypeAlias = tuple[int, int]
ColorPair: TypeAlias = tuple[int, int]
Relation: TypeAlias = tuple[str, str, str]
GridMechanism: TypeAlias = Callable[[Grid], object]

SCHEMA_VERSION = 1
MAX_GAUGE_ORBIT = 4096

D4_NAMES = (
    "id",
    "r90",
    "r180",
    "r270",
    "fliplr",
    "flipud",
    "transpose",
    "anti_transpose",
)

_D4_ALIASES = {
    "id": "id",
    "r90": "r90",
    "r180": "r180",
    "r270": "r270",
    "fh": "fliplr",
    "fliplr": "fliplr",
    "fv": "flipud",
    "flipud": "flipud",
    "t": "transpose",
    "transpose": "transpose",
    "at": "anti_transpose",
    "anti_transpose": "anti_transpose",
}


class GaugeError(ValueError):
    """Base class for a rejected gauge operation."""


class GaugeUndefinedError(GaugeError):
    """The exact partial adapter is not defined for the supplied value."""


class AmbiguousGaugeError(GaugeError):
    """An orbit has more than one distinct executable behavior."""


class GaugeOrbitLimitError(GaugeError):
    """Exact ambiguity enumeration would exceed the declared finite budget."""


def _shape(value: Grid) -> Shape:
    return len(value), len(value[0])


def _require_shape(value: object, label: str) -> Shape:
    if (
        not isinstance(value, (tuple, list))
        or len(value) != 2
        or any(isinstance(item, bool) or not isinstance(item, Integral) for item in value)
    ):
        raise TypeError(f"{label} must be a pair of integers")
    height, width = int(value[0]), int(value[1])
    if not 1 <= height <= 30 or not 1 <= width <= 30 or height * width > 900:
        raise ValueError(f"{label} must describe a nonempty ARC canvas")
    return height, width


def _require_color(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise TypeError(f"{label} must be an integer color")
    result = int(value)
    if not 0 <= result <= 9:
        raise ValueError(f"{label} must lie in 0..9")
    return result


def _require_positive_limit(value: object, label: str = "max_orbit") -> int:
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise TypeError(f"{label} must be an integer")
    result = int(value)
    if result <= 0:
        raise ValueError(f"{label} must be positive")
    return result


def _require_name(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{label} must be a string")
    if not value or value != value.strip():
        raise ValueError(f"{label} must be nonempty and trimmed")
    return value


def _strict_record(
    record: object,
    *,
    kind: str,
    fields: frozenset[str],
) -> Mapping[str, object]:
    if not isinstance(record, Mapping):
        raise TypeError(f"{kind} record must be a mapping")
    if set(record) != set(fields):
        missing = sorted(set(fields) - set(record))
        unknown = sorted(set(record) - set(fields))
        raise ValueError(f"invalid {kind} record fields; missing={missing}, unknown={unknown}")
    if record.get("kind") != kind:
        raise ValueError(f"record kind must equal {kind!r}")
    if isinstance(record.get("schema_version"), bool) or record.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"schema_version must equal {SCHEMA_VERSION}")
    return record


def normalize_d4_name(value: object) -> str:
    """Return the public long name of one D4 action."""

    if not isinstance(value, str):
        raise TypeError("D4 transform must be a string")
    try:
        return _D4_ALIASES[value]
    except KeyError as error:
        raise ValueError(f"unknown D4 transform {value!r}") from error


def apply_d4(grid: object, transform: object) -> Grid:
    """Apply one exact D4 action; ``r90`` is counter-clockwise."""

    value = validate_grid(grid)
    name = normalize_d4_name(transform)

    def rotate90(source: Grid) -> Grid:
        height, width = _shape(source)
        return tuple(
            tuple(source[row][width - 1 - column] for row in range(height))
            for column in range(width)
        )

    if name == "id":
        return value
    if name == "r90":
        return rotate90(value)
    if name == "r180":
        return rotate90(rotate90(value))
    if name == "r270":
        return rotate90(rotate90(rotate90(value)))
    if name == "fliplr":
        return tuple(tuple(reversed(row)) for row in value)
    if name == "flipud":
        return tuple(reversed(value))
    if name == "transpose":
        return tuple(
            tuple(value[row][column] for row in range(len(value)))
            for column in range(len(value[0]))
        )
    if name == "anti_transpose":
        return apply_d4(apply_d4(value, "transpose"), "r180")
    raise AssertionError("normalize_d4_name returned an impossible name")


def _derive_d4_tables() -> tuple[dict[tuple[str, str], str], dict[str, str]]:
    # A rectangular grid with all entries distinct is a faithful finite model
    # of the action.  ``compose[(a,b)]`` means apply a, then b.
    witness: Grid = ((0, 1, 2), (3, 4, 5))
    images = {name: apply_d4(witness, name) for name in D4_NAMES}
    compose: dict[tuple[str, str], str] = {}
    for first in D4_NAMES:
        for second in D4_NAMES:
            result = apply_d4(images[first], second)
            matches = [name for name, image in images.items() if image == result]
            if len(matches) != 1:
                raise RuntimeError("D4 reference actions are not faithful")
            compose[(first, second)] = matches[0]
    inverse: dict[str, str] = {}
    for name in D4_NAMES:
        matches = [
            candidate
            for candidate in D4_NAMES
            if compose[(name, candidate)] == "id"
            and compose[(candidate, name)] == "id"
        ]
        if len(matches) != 1:
            raise RuntimeError("D4 inverse is not unique")
        inverse[name] = matches[0]
    return compose, inverse


_D4_COMPOSE_TABLE, _D4_INVERSE_TABLE = _derive_d4_tables()
D4_COMPOSE: Mapping[tuple[str, str], str] = MappingProxyType(_D4_COMPOSE_TABLE)
D4_INVERSE: Mapping[str, str] = MappingProxyType(_D4_INVERSE_TABLE)
del _D4_COMPOSE_TABLE, _D4_INVERSE_TABLE


def compose_d4(first: object, second: object) -> str:
    """Compose actions in execution order: ``second(first(grid))``."""

    return D4_COMPOSE[(normalize_d4_name(first), normalize_d4_name(second))]


def inverse_d4(transform: object) -> str:
    return D4_INVERSE[normalize_d4_name(transform)]


@dataclass(frozen=True, slots=True, order=True)
class BoundingBox:
    """Inclusive bounding box in a physical canvas."""

    top: int
    left: int
    bottom: int
    right: int

    def __post_init__(self) -> None:
        for name in ("top", "left", "bottom", "right"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, Integral):
                raise TypeError(f"{name} must be an integer")
            object.__setattr__(self, name, int(value))
        if self.top < 0 or self.left < 0:
            raise ValueError("bounding-box coordinates must be nonnegative")
        if self.bottom < self.top or self.right < self.left:
            raise ValueError("bounding box must be nonempty")

    @property
    def height(self) -> int:
        return self.bottom - self.top + 1

    @property
    def width(self) -> int:
        return self.right - self.left + 1

    @property
    def shape(self) -> Shape:
        return self.height, self.width

    def fits(self, shape: Shape) -> bool:
        height, width = _require_shape(shape, "shape")
        return self.bottom < height and self.right < width

    def contains(self, row: int, column: int) -> bool:
        return self.top <= row <= self.bottom and self.left <= column <= self.right

    def to_record(self) -> dict[str, int]:
        return {
            "bottom": self.bottom,
            "left": self.left,
            "right": self.right,
            "top": self.top,
        }

    @classmethod
    def from_record(cls, record: object) -> "BoundingBox":
        if not isinstance(record, Mapping):
            raise TypeError("bounding-box record must be a mapping")
        expected = {"bottom", "left", "right", "top"}
        if set(record) != expected:
            raise ValueError("bounding-box record has missing or unknown fields")
        return cls(record["top"], record["left"], record["bottom"], record["right"])


@dataclass(frozen=True, slots=True)
class PaletteGauge:
    """A finite color bijection with a deliberately partial domain.

    Unmapped colors are errors, rather than implicit identity mappings.  This
    is what makes a learned palette role binding safe when a later state
    introduces a previously unseen color.
    """

    mapping: tuple[ColorPair, ...]
    role_bindings: tuple[tuple[str, int], ...] = ()

    def __post_init__(self) -> None:
        if isinstance(self.mapping, (str, bytes)) or not isinstance(self.mapping, Sequence):
            raise TypeError("palette mapping must be a sequence")
        normalized = tuple(
            (_require_color(pair[0], "palette source"), _require_color(pair[1], "palette target"))
            if isinstance(pair, (tuple, list)) and len(pair) == 2
            else (_raise_pair_type())
            for pair in self.mapping
        )
        if not normalized:
            raise ValueError("palette mapping must not be empty")
        sources = tuple(source for source, _ in normalized)
        targets = tuple(target for _, target in normalized)
        if len(set(sources)) != len(sources):
            raise ValueError("palette mapping sources must be unique")
        if len(set(targets)) != len(targets):
            raise ValueError("palette mapping targets must be unique")
        normalized = tuple(sorted(normalized))
        object.__setattr__(self, "mapping", normalized)

        if isinstance(self.role_bindings, (str, bytes)) or not isinstance(
            self.role_bindings, Sequence
        ):
            raise TypeError("role bindings must be a sequence")
        roles: list[tuple[str, int]] = []
        for pair in self.role_bindings:
            if not isinstance(pair, (tuple, list)) or len(pair) != 2:
                raise TypeError("each role binding must be a pair")
            role = _require_name(pair[0], "role name")
            target = _require_color(pair[1], "role target")
            roles.append((role, target))
        if len({name for name, _ in roles}) != len(roles):
            raise ValueError("palette role names must be unique")
        if any(target not in set(targets) for _, target in roles):
            raise ValueError("every role target must lie in the palette codomain")
        object.__setattr__(self, "role_bindings", tuple(sorted(roles)))

    @property
    def domain(self) -> frozenset[int]:
        return frozenset(source for source, _ in self.mapping)

    @property
    def codomain(self) -> frozenset[int]:
        return frozenset(target for _, target in self.mapping)

    @property
    def inverse_mapping(self) -> tuple[ColorPair, ...]:
        return tuple(sorted((target, source) for source, target in self.mapping))

    def forward_color(self, color: object) -> int:
        source = _require_color(color, "source color")
        table = dict(self.mapping)
        if source not in table:
            raise GaugeUndefinedError(f"palette gauge is undefined on source color {source}")
        return table[source]

    def inverse_color(self, color: object) -> int:
        target = _require_color(color, "canonical color")
        table = dict(self.inverse_mapping)
        if target not in table:
            raise GaugeUndefinedError(f"palette inverse is undefined on canonical color {target}")
        return table[target]

    def forward(self, grid: object) -> Grid:
        value = validate_grid(grid)
        table = dict(self.mapping)
        missing = sorted({cell for row in value for cell in row if cell not in table})
        if missing:
            raise GaugeUndefinedError(f"palette gauge is undefined on colors {missing}")
        return validate_grid(tuple(tuple(table[cell] for cell in row) for row in value))

    def inverse(self, grid: object) -> Grid:
        value = validate_grid(grid)
        table = dict(self.inverse_mapping)
        missing = sorted({cell for row in value for cell in row if cell not in table})
        if missing:
            raise GaugeUndefinedError(f"palette inverse is undefined on colors {missing}")
        return validate_grid(tuple(tuple(table[cell] for cell in row) for row in value))

    def to_record(self) -> dict[str, object]:
        return {
            "kind": "palette_role",
            "mapping": [list(pair) for pair in self.mapping],
            "role_bindings": [list(pair) for pair in self.role_bindings],
            "schema_version": SCHEMA_VERSION,
        }

    @classmethod
    def from_record(cls, record: object) -> "PaletteGauge":
        body = _strict_record(
            record,
            kind="palette_role",
            fields=frozenset({"kind", "mapping", "role_bindings", "schema_version"}),
        )
        mapping = body["mapping"]
        roles = body["role_bindings"]
        if isinstance(mapping, (str, bytes)) or not isinstance(mapping, Sequence):
            raise TypeError("palette mapping record must be a sequence")
        if isinstance(roles, (str, bytes)) or not isinstance(roles, Sequence):
            raise TypeError("palette role record must be a sequence")
        return cls(tuple(mapping), tuple(roles))  # type: ignore[arg-type]

    @property
    def content_hash(self) -> str:
        return sha256_record(self.to_record())


def _raise_pair_type() -> tuple[int, int]:
    raise TypeError("each palette mapping entry must be a two-element sequence")


@dataclass(frozen=True, slots=True)
class D4Gauge:
    transform: str
    source_shape: Shape

    def __post_init__(self) -> None:
        object.__setattr__(self, "transform", normalize_d4_name(self.transform))
        object.__setattr__(self, "source_shape", _require_shape(self.source_shape, "source shape"))

    @property
    def target_shape(self) -> Shape:
        height, width = self.source_shape
        if self.transform in {"r90", "r270", "transpose", "anti_transpose"}:
            return width, height
        return height, width

    @property
    def inverse_transform(self) -> str:
        return inverse_d4(self.transform)

    def forward(self, grid: object) -> Grid:
        value = validate_grid(grid)
        if _shape(value) != self.source_shape:
            raise GaugeUndefinedError(
                f"D4 gauge expected source shape {self.source_shape}, got {_shape(value)}"
            )
        return apply_d4(value, self.transform)

    def inverse(self, grid: object) -> Grid:
        value = validate_grid(grid)
        if _shape(value) != self.target_shape:
            raise GaugeUndefinedError(
                f"D4 inverse expected canonical shape {self.target_shape}, got {_shape(value)}"
            )
        result = apply_d4(value, self.inverse_transform)
        if _shape(result) != self.source_shape:
            raise GaugeUndefinedError("D4 inverse did not restore the declared source shape")
        return result

    def to_record(self) -> dict[str, object]:
        return {
            "kind": "d4",
            "schema_version": SCHEMA_VERSION,
            "source_shape": list(self.source_shape),
            "transform": self.transform,
        }

    @classmethod
    def from_record(cls, record: object) -> "D4Gauge":
        body = _strict_record(
            record,
            kind="d4",
            fields=frozenset({"kind", "schema_version", "source_shape", "transform"}),
        )
        return cls(body["transform"], body["source_shape"])  # type: ignore[arg-type]

    @property
    def content_hash(self) -> str:
        return sha256_record(self.to_record())


@dataclass(frozen=True, slots=True)
class SupportTranslationGauge:
    """Translate a foreground bounding box to the origin by exact cropping.

    The inverse is defined only because every discarded cell is required to be
    the declared exterior color.  Thus no ambient raster information is lost.
    """

    source_shape: Shape
    box: BoundingBox
    exterior_color: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "source_shape", _require_shape(self.source_shape, "source shape"))
        if not isinstance(self.box, BoundingBox):
            raise TypeError("box must be a BoundingBox")
        if not self.box.fits(self.source_shape):
            raise ValueError("support box does not fit its source canvas")
        object.__setattr__(
            self, "exterior_color", _require_color(self.exterior_color, "exterior color")
        )

    @property
    def target_shape(self) -> Shape:
        return self.box.shape

    @property
    def offset(self) -> tuple[int, int]:
        return -self.box.top, -self.box.left

    def forward(self, grid: object) -> Grid:
        value = validate_grid(grid)
        if _shape(value) != self.source_shape:
            raise GaugeUndefinedError(
                f"support gauge expected source shape {self.source_shape}, got {_shape(value)}"
            )
        for row, values in enumerate(value):
            for column, color in enumerate(values):
                if not self.box.contains(row, column) and color != self.exterior_color:
                    raise GaugeUndefinedError(
                        "support crop would discard a non-exterior cell"
                    )
        return validate_grid(
            tuple(
                tuple(value[row][self.box.left : self.box.right + 1])
                for row in range(self.box.top, self.box.bottom + 1)
            )
        )

    def inverse(self, grid: object) -> Grid:
        value = validate_grid(grid)
        if _shape(value) != self.target_shape:
            raise GaugeUndefinedError(
                f"support inverse expected canonical shape {self.target_shape}, got {_shape(value)}"
            )
        height, width = self.source_shape
        result = [[self.exterior_color for _ in range(width)] for _ in range(height)]
        for row, values in enumerate(value):
            for column, color in enumerate(values):
                result[self.box.top + row][self.box.left + column] = color
        return validate_grid(result)

    def to_record(self) -> dict[str, object]:
        return {
            "box": self.box.to_record(),
            "exterior_color": self.exterior_color,
            "kind": "support_translation",
            "schema_version": SCHEMA_VERSION,
            "source_shape": list(self.source_shape),
        }

    @classmethod
    def from_record(cls, record: object) -> "SupportTranslationGauge":
        body = _strict_record(
            record,
            kind="support_translation",
            fields=frozenset(
                {"box", "exterior_color", "kind", "schema_version", "source_shape"}
            ),
        )
        return cls(
            body["source_shape"],  # type: ignore[arg-type]
            BoundingBox.from_record(body["box"]),
            body["exterior_color"],  # type: ignore[arg-type]
        )

    @property
    def content_hash(self) -> str:
        return sha256_record(self.to_record())


def infer_support_translation(grid: object, background: object) -> SupportTranslationGauge:
    """Infer the exact foreground support box relative to ``background``."""

    value = validate_grid(grid)
    bg = _require_color(background, "background")
    cells = [
        (row, column)
        for row, values in enumerate(value)
        for column, color in enumerate(values)
        if color != bg
    ]
    if not cells:
        raise GaugeUndefinedError("a uniform grid has no non-background support")
    box = BoundingBox(
        min(row for row, _ in cells),
        min(column for _, column in cells),
        max(row for row, _ in cells),
        max(column for _, column in cells),
    )
    adapter = SupportTranslationGauge(_shape(value), box, bg)
    adapter.forward(value)  # certify the partial-domain precondition now
    return adapter


@dataclass(frozen=True, slots=True)
class ObjectLabelGauge:
    """A bijective renaming of task-local object identifiers."""

    mapping: tuple[tuple[str, str], ...]

    def __post_init__(self) -> None:
        if isinstance(self.mapping, (str, bytes)) or not isinstance(self.mapping, Sequence):
            raise TypeError("object-label mapping must be a sequence")
        normalized: list[tuple[str, str]] = []
        for pair in self.mapping:
            if not isinstance(pair, (tuple, list)) or len(pair) != 2:
                raise TypeError("each object-label mapping entry must be a pair")
            normalized.append(
                (_require_name(pair[0], "source object label"), _require_name(pair[1], "canonical object label"))
            )
        if not normalized:
            raise ValueError("object-label mapping must not be empty")
        if len({source for source, _ in normalized}) != len(normalized):
            raise ValueError("source object labels must be unique")
        if len({target for _, target in normalized}) != len(normalized):
            raise ValueError("canonical object labels must be unique")
        object.__setattr__(self, "mapping", tuple(sorted(normalized)))

    def forward_label(self, label: object) -> str:
        source = _require_name(label, "object label")
        table = dict(self.mapping)
        if source not in table:
            raise GaugeUndefinedError(f"unknown source object label {source!r}")
        return table[source]

    def inverse_label(self, label: object) -> str:
        target = _require_name(label, "canonical object label")
        table = {canonical: source for source, canonical in self.mapping}
        if target not in table:
            raise GaugeUndefinedError(f"unknown canonical object label {target!r}")
        return table[target]

    def forward_object_mapping(self, objects: Mapping[str, object]) -> Mapping[str, object]:
        """Rename keys while leaving authoritative object payloads untouched."""

        if not isinstance(objects, Mapping):
            raise TypeError("objects must be a mapping")
        expected = {source for source, _ in self.mapping}
        if set(objects) != expected:
            raise GaugeUndefinedError("object mapping domain does not equal the supplied object labels")
        return MappingProxyType(
            {self.forward_label(label): objects[label] for label in sorted(objects)}
        )

    def inverse_object_mapping(self, objects: Mapping[str, object]) -> Mapping[str, object]:
        """Invert a renamed mapping without altering its payload values."""

        if not isinstance(objects, Mapping):
            raise TypeError("objects must be a mapping")
        expected = {target for _, target in self.mapping}
        if set(objects) != expected:
            raise GaugeUndefinedError("canonical object domain does not equal the gauge codomain")
        return MappingProxyType(
            {self.inverse_label(label): objects[label] for label in sorted(objects)}
        )

    def forward_objects(self, objects: Mapping[str, object]) -> tuple[tuple[str, object], ...]:
        if not isinstance(objects, Mapping):
            raise TypeError("objects must be a mapping")
        expected = {source for source, _ in self.mapping}
        if set(objects) != expected:
            raise GaugeUndefinedError("object mapping domain does not equal the supplied object labels")
        return tuple(
            sorted(
                (self.forward_label(label), canonical_value(payload))
                for label, payload in objects.items()
            )
        )

    def inverse_objects(self, objects: Mapping[str, object]) -> tuple[tuple[str, object], ...]:
        if not isinstance(objects, Mapping):
            raise TypeError("objects must be a mapping")
        expected = {target for _, target in self.mapping}
        if set(objects) != expected:
            raise GaugeUndefinedError("canonical object domain does not equal the gauge codomain")
        return tuple(
            sorted(
                (self.inverse_label(label), canonical_value(payload))
                for label, payload in objects.items()
            )
        )

    def forward_relations(self, relations: Iterable[Relation]) -> tuple[Relation, ...]:
        result: list[Relation] = []
        for relation in relations:
            source, predicate, target = _validate_relation(relation)
            result.append((self.forward_label(source), predicate, self.forward_label(target)))
        return tuple(sorted(result))

    def inverse_relations(self, relations: Iterable[Relation]) -> tuple[Relation, ...]:
        result: list[Relation] = []
        for relation in relations:
            source, predicate, target = _validate_relation(relation)
            result.append((self.inverse_label(source), predicate, self.inverse_label(target)))
        return tuple(sorted(result))

    def assert_roundtrip(
        self,
        objects: Mapping[str, object],
        relations: Iterable[Relation] = (),
    ) -> None:
        edges = tuple(relations)
        canonical_objects = self.forward_object_mapping(objects)
        restored_objects = self.inverse_object_mapping(canonical_objects)
        if canonical_json(restored_objects) != canonical_json(objects):
            raise GaugeError("object-label gauge failed its exact payload roundtrip")
        canonical_edges = self.forward_relations(edges)
        if self.inverse_relations(canonical_edges) != tuple(sorted(_validate_relation(edge) for edge in edges)):
            raise GaugeError("object-label gauge failed its exact relation roundtrip")

    def to_record(self) -> dict[str, object]:
        return {
            "kind": "object_label",
            "mapping": [list(pair) for pair in self.mapping],
            "schema_version": SCHEMA_VERSION,
        }

    @classmethod
    def from_record(cls, record: object) -> "ObjectLabelGauge":
        body = _strict_record(
            record,
            kind="object_label",
            fields=frozenset({"kind", "mapping", "schema_version"}),
        )
        mapping = body["mapping"]
        if isinstance(mapping, (str, bytes)) or not isinstance(mapping, Sequence):
            raise TypeError("object-label mapping record must be a sequence")
        return cls(tuple(mapping))  # type: ignore[arg-type]

    @property
    def content_hash(self) -> str:
        return sha256_record(self.to_record())


def _validate_relation(value: object) -> Relation:
    if not isinstance(value, (tuple, list)) or len(value) != 3:
        raise TypeError("relations must be source-predicate-target triples")
    return (
        _require_name(value[0], "relation source"),
        _require_name(value[1], "relation predicate"),
        _require_name(value[2], "relation target"),
    )


@dataclass(frozen=True, slots=True)
class ObjectLabelOrbit:
    gauges: tuple[ObjectLabelGauge, ...]
    canonical_record_json: str

    def __post_init__(self) -> None:
        if not self.gauges:
            raise ValueError("object-label orbit must contain at least one gauge")
        if not isinstance(self.canonical_record_json, str) or not self.canonical_record_json:
            raise ValueError("canonical object record must be nonempty JSON text")
        if len({gauge.content_hash for gauge in self.gauges}) != len(self.gauges):
            raise ValueError("object-label orbit gauges must be unique")

    @property
    def ambiguous(self) -> bool:
        return len(self.gauges) > 1

    def to_record(self) -> dict[str, object]:
        return {
            "canonical_record_json": self.canonical_record_json,
            "gauge_ids": [gauge.content_hash for gauge in self.gauges],
            "kind": "object_label_orbit",
            "schema_version": SCHEMA_VERSION,
        }


def canonical_object_label_orbit(
    objects: Mapping[str, object],
    relations: Iterable[Relation] = (),
    *,
    max_orbit: int = MAX_GAUGE_ORBIT,
) -> ObjectLabelOrbit:
    """Canonically label a finite attributed relation graph.

    Payloads are assumed to be label-free.  Exact color refinement is followed
    by bounded exhaustive permutation inside unresolved cells.  All graph
    automorphisms that attain the canonical record are retained.
    """

    if not isinstance(objects, Mapping) or not objects:
        raise ValueError("objects must be a nonempty mapping")
    labels = tuple(sorted(_require_name(label, "object label") for label in objects))
    if len(set(labels)) != len(labels) or set(labels) != set(objects):
        raise ValueError("object labels must be unique strings")
    payload_json = {label: canonical_json(objects[label]) for label in labels}
    edges = tuple(sorted(_validate_relation(relation) for relation in relations))
    if any(source not in objects or target not in objects for source, _, target in edges):
        raise GaugeUndefinedError("relation endpoint is absent from the object mapping")

    colors = {label: payload_json[label] for label in labels}
    for _ in range(len(labels) + 1):
        signatures: dict[str, str] = {}
        for label in labels:
            outgoing = sorted((predicate, colors[target]) for source, predicate, target in edges if source == label)
            incoming = sorted((predicate, colors[source]) for source, predicate, target in edges if target == label)
            signatures[label] = canonical_json(
                {"incoming": incoming, "outgoing": outgoing, "payload": payload_json[label]}
            )
        palette = {signature: f"c{index}" for index, signature in enumerate(sorted(set(signatures.values())))}
        refined = {label: palette[signatures[label]] for label in labels}
        old_partition = sorted(sorted(label for label in labels if colors[label] == color) for color in set(colors.values()))
        new_partition = sorted(sorted(label for label in labels if refined[label] == color) for color in set(refined.values()))
        colors = refined
        if old_partition == new_partition:
            break

    cells = [tuple(sorted(label for label in labels if colors[label] == color)) for color in sorted(set(colors.values()))]
    candidate_count = math.prod(math.factorial(len(cell)) for cell in cells)
    limit = _require_positive_limit(max_orbit)
    if candidate_count > limit:
        raise GaugeOrbitLimitError(
            f"object-label orbit requires {candidate_count} candidates, limit is {limit}"
        )

    slot_cells: list[tuple[str, ...]] = []
    offset = 0
    for cell in cells:
        slot_cells.append(tuple(f"o{index}" for index in range(offset, offset + len(cell))))
        offset += len(cell)

    winners: list[tuple[str, ObjectLabelGauge]] = []
    best: str | None = None
    permutation_spaces = [tuple(itertools.permutations(cell)) for cell in cells]
    for selections in itertools.product(*permutation_spaces):
        pairs: list[tuple[str, str]] = []
        for permutation, slots in zip(selections, slot_cells):
            pairs.extend(zip(permutation, slots))
        gauge = ObjectLabelGauge(tuple(pairs))
        gauge.assert_roundtrip(objects, edges)
        canonical_objects = gauge.forward_objects(objects)
        canonical_relations = gauge.forward_relations(edges)
        record = canonical_json(
            {
                "objects": [[label, payload] for label, payload in canonical_objects],
                "relations": [list(edge) for edge in canonical_relations],
            }
        )
        if best is None or record < best:
            best = record
            winners = [(record, gauge)]
        elif record == best:
            winners.append((record, gauge))
    assert best is not None
    unique = {gauge.content_hash: gauge for _, gauge in winners}
    return ObjectLabelOrbit(tuple(unique[key] for key in sorted(unique)), best)


@dataclass(frozen=True, slots=True)
class GridGauge:
    """A typed composition: support translation, D4 action, palette roles."""

    source_shape: Shape
    spatial: SupportTranslationGauge | None
    orientation: D4Gauge
    palette: PaletteGauge

    def __post_init__(self) -> None:
        source_shape = _require_shape(self.source_shape, "source shape")
        object.__setattr__(self, "source_shape", source_shape)
        if self.spatial is not None:
            if not isinstance(self.spatial, SupportTranslationGauge):
                raise TypeError("spatial must be a SupportTranslationGauge or None")
            if self.spatial.source_shape != source_shape:
                raise ValueError("spatial gauge source shape does not match grid gauge")
            orientation_source = self.spatial.target_shape
        else:
            orientation_source = source_shape
        if not isinstance(self.orientation, D4Gauge):
            raise TypeError("orientation must be a D4Gauge")
        if self.orientation.source_shape != orientation_source:
            raise ValueError("D4 gauge source shape does not match spatial image")
        if not isinstance(self.palette, PaletteGauge):
            raise TypeError("palette must be a PaletteGauge")

    @property
    def canonical_shape(self) -> Shape:
        return self.orientation.target_shape

    def forward(self, grid: object) -> Grid:
        value = validate_grid(grid)
        if _shape(value) != self.source_shape:
            raise GaugeUndefinedError(
                f"grid gauge expected source shape {self.source_shape}, got {_shape(value)}"
            )
        if self.spatial is not None:
            value = self.spatial.forward(value)
        value = self.orientation.forward(value)
        value = self.palette.forward(value)
        if _shape(value) != self.canonical_shape:
            raise GaugeUndefinedError("grid gauge produced an undeclared canonical shape")
        return value

    def inverse(self, grid: object) -> Grid:
        value = validate_grid(grid)
        if _shape(value) != self.canonical_shape:
            raise GaugeUndefinedError(
                f"grid inverse expected canonical shape {self.canonical_shape}, got {_shape(value)}"
            )
        value = self.palette.inverse(value)
        value = self.orientation.inverse(value)
        if self.spatial is not None:
            value = self.spatial.inverse(value)
        if _shape(value) != self.source_shape:
            raise GaugeUndefinedError("grid inverse did not restore its declared source shape")
        return value

    def assert_roundtrip(self, grid: object) -> Grid:
        value = validate_grid(grid)
        restored = self.inverse(self.forward(value))
        if restored != value:
            raise GaugeError("grid gauge failed its exact physical roundtrip")
        return restored

    def to_record(self) -> dict[str, object]:
        return {
            "kind": "grid_gauge",
            "orientation": self.orientation.to_record(),
            "palette": self.palette.to_record(),
            "schema_version": SCHEMA_VERSION,
            "source_shape": list(self.source_shape),
            "spatial": self.spatial.to_record() if self.spatial is not None else None,
        }

    @classmethod
    def from_record(cls, record: object) -> "GridGauge":
        body = _strict_record(
            record,
            kind="grid_gauge",
            fields=frozenset(
                {"kind", "orientation", "palette", "schema_version", "source_shape", "spatial"}
            ),
        )
        spatial_record = body["spatial"]
        spatial = (
            None
            if spatial_record is None
            else SupportTranslationGauge.from_record(spatial_record)
        )
        return cls(
            body["source_shape"],  # type: ignore[arg-type]
            spatial,
            D4Gauge.from_record(body["orientation"]),
            PaletteGauge.from_record(body["palette"]),
        )

    @property
    def content_hash(self) -> str:
        return sha256_record(self.to_record())


@dataclass(frozen=True, slots=True)
class GaugeOrbit:
    """All exact adapters attaining one canonical grid."""

    gauges: tuple[GridGauge, ...]
    canonical_grid: Grid

    def __post_init__(self) -> None:
        object.__setattr__(self, "canonical_grid", validate_grid(self.canonical_grid))
        if not self.gauges:
            raise ValueError("gauge orbit must contain at least one adapter")
        if any(not isinstance(gauge, GridGauge) for gauge in self.gauges):
            raise TypeError("gauge orbit entries must be GridGauge values")
        if any(gauge.canonical_shape != _shape(self.canonical_grid) for gauge in self.gauges):
            raise ValueError("every gauge must have the orbit's canonical shape")
        unique = {gauge.content_hash: gauge for gauge in self.gauges}
        if len(unique) != len(self.gauges):
            raise ValueError("gauge orbit entries must be unique")
        object.__setattr__(self, "gauges", tuple(unique[key] for key in sorted(unique)))

    @property
    def ambiguous(self) -> bool:
        return len(self.gauges) > 1

    def verify(self, source: object) -> Grid:
        value = validate_grid(source)
        for gauge in self.gauges:
            if gauge.forward(value) != self.canonical_grid:
                raise GaugeError("orbit member does not attain the recorded canonical grid")
            gauge.assert_roundtrip(value)
        return self.canonical_grid

    def to_record(self) -> dict[str, object]:
        return {
            "canonical_grid_hash": sha256_record(self.canonical_grid),
            "gauge_ids": [gauge.content_hash for gauge in self.gauges],
            "kind": "grid_gauge_orbit",
            "schema_version": SCHEMA_VERSION,
        }


def _components(mask: set[tuple[int, int]], diagonal: bool = False) -> int:
    directions = ((-1, 0), (1, 0), (0, -1), (0, 1))
    if diagonal:
        directions += ((-1, -1), (-1, 1), (1, -1), (1, 1))
    unseen = set(mask)
    count = 0
    while unseen:
        count += 1
        stack = [unseen.pop()]
        while stack:
            row, column = stack.pop()
            for drow, dcolumn in directions:
                neighbor = row + drow, column + dcolumn
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    stack.append(neighbor)
    return count


def _color_signature(grid: Grid, color: int) -> str:
    cells = {(row, column) for row, values in enumerate(grid) for column, value in enumerate(values) if value == color}
    top = min(row for row, _ in cells)
    left = min(column for _, column in cells)
    bottom = max(row for row, _ in cells)
    right = max(column for _, column in cells)
    binary = tuple(
        tuple(1 if (row, column) in cells else 0 for column in range(left, right + 1))
        for row in range(top, bottom + 1)
    )
    d4_forms = [apply_d4(binary, name) for name in D4_NAMES]
    canonical_support = min(canonical_json(form) for form in d4_forms)
    box_height, box_width = bottom - top + 1, right - left + 1
    return canonical_json(
        {
            "bbox_d4": [min(box_height, box_width), max(box_height, box_width)],
            "components4": _components(cells),
            "components8": _components(cells, diagonal=True),
            "count": len(cells),
            "support": canonical_support,
        }
    )


def _background_candidates(grid: Grid, background: object | None) -> tuple[int, ...]:
    colors = sorted({cell for row in grid for cell in row})
    if background is not None:
        chosen = _require_color(background, "background")
        if chosen not in colors:
            raise GaugeUndefinedError("declared background is absent from the grid")
        return (chosen,)
    counts = Counter(cell for row in grid for cell in row)
    maximum = max(counts.values())
    # A frequency tie is genuine ambiguity; raw color order is not evidence.
    return tuple(color for color in colors if counts[color] == maximum)


def _palette_candidates(
    grid: Grid,
    background: int,
    *,
    max_orbit: int,
) -> tuple[PaletteGauge, ...]:
    colors = sorted({cell for row in grid for cell in row})
    foreground = [color for color in colors if color != background]
    grouped: dict[str, list[int]] = defaultdict(list)
    for color in foreground:
        grouped[_color_signature(grid, color)].append(color)
    groups = [tuple(sorted(grouped[key])) for key in sorted(grouped)]
    count = math.prod(math.factorial(len(group)) for group in groups)
    if count > max_orbit:
        raise GaugeOrbitLimitError(
            f"palette-role ambiguity requires {count} candidates, limit is {max_orbit}"
        )
    slots: list[tuple[int, ...]] = []
    next_slot = 1
    for group in groups:
        slots.append(tuple(range(next_slot, next_slot + len(group))))
        next_slot += len(group)
    spaces = [tuple(itertools.permutations(group)) for group in groups]
    result: list[PaletteGauge] = []
    for selections in itertools.product(*spaces):
        mapping: list[ColorPair] = [(background, 0)]
        roles: list[tuple[str, int]] = [("background", 0)]
        for permutation, targets in zip(selections, slots):
            mapping.extend(zip(permutation, targets))
            roles.extend((f"foreground:{target:02d}", target) for target in targets)
        result.append(PaletteGauge(tuple(mapping), tuple(roles)))
    return tuple(result)


def canonical_gauge_orbit(
    grid: object,
    *,
    background: object | None = None,
    normalize_support: bool = True,
    normalize_palette: bool = True,
    normalize_d4: bool = True,
    max_orbit: int = MAX_GAUGE_ORBIT,
) -> GaugeOrbit:
    """Construct all exact adapters attaining the lexicographic normal form.

    Ambiguity is retained whenever distinct adapters yield the same normal
    form.  Candidate counts are bounded before factorial enumeration.
    """

    value = validate_grid(grid)
    limit = _require_positive_limit(max_orbit)
    backgrounds = _background_candidates(value, background)
    candidates: list[tuple[Grid, GridGauge]] = []
    considered = 0
    for bg in backgrounds:
        spatial: SupportTranslationGauge | None
        if normalize_support and any(cell != bg for row in value for cell in row):
            spatial = infer_support_translation(value, bg)
            spatial_value = spatial.forward(value)
        else:
            spatial = None
            spatial_value = value
        orientations = D4_NAMES if normalize_d4 else ("id",)
        if normalize_palette:
            # Role signatures are D4 invariant by construction, so infer this
            # finite ambiguity set once rather than eight times.
            palettes = _palette_candidates(spatial_value, bg, max_orbit=limit)
        else:
            colors = tuple(sorted({cell for row in spatial_value for cell in row}))
            palettes = (PaletteGauge(tuple((color, color) for color in colors)),)
        for transform in orientations:
            d4_gauge = D4Gauge(transform, _shape(spatial_value))
            oriented = d4_gauge.forward(spatial_value)
            considered += len(palettes)
            if considered > limit:
                raise GaugeOrbitLimitError(
                    f"combined gauge orbit exceeds candidate limit {limit}"
                )
            for palette in palettes:
                adapter = GridGauge(_shape(value), spatial, d4_gauge, palette)
                canonical = adapter.forward(value)
                adapter.assert_roundtrip(value)
                candidates.append((canonical, adapter))
    if not candidates:
        raise GaugeUndefinedError("no exact gauge candidate was constructed")
    best_grid = min(canonical for canonical, _ in candidates)
    winners = {adapter.content_hash: adapter for canonical, adapter in candidates if canonical == best_grid}
    return GaugeOrbit(tuple(winners[key] for key in sorted(winners)), best_grid)


def canonical_d4_orbit(grid: object, *, max_orbit: int = MAX_GAUGE_ORBIT) -> GaugeOrbit:
    """Canonicalize orientation only, retaining stabilizer ambiguity."""

    return canonical_gauge_orbit(
        grid,
        normalize_support=False,
        normalize_palette=False,
        normalize_d4=True,
        max_orbit=max_orbit,
    )


def infer_palette_role_orbit(
    grid: object,
    *,
    background: object | None = None,
    max_orbit: int = MAX_GAUGE_ORBIT,
) -> GaugeOrbit:
    """Canonicalize palette roles only, preserving unresolved role bindings."""

    return canonical_gauge_orbit(
        grid,
        background=background,
        normalize_support=False,
        normalize_palette=True,
        normalize_d4=False,
        max_orbit=max_orbit,
    )


def canonical_grid_signature(grid: object, **orbit_options: object) -> str:
    """Hash one exact canonical representative for routing diagnostics.

    Equality of these signatures is not permission to merge physical output
    rasters.  Such a merge still requires an explicit inverse output gauge and
    unique behavior across its ambiguity orbit.
    """

    orbit = canonical_gauge_orbit(grid, **orbit_options)
    return sha256_record(
        {
            "canonical_grid": orbit.canonical_grid,
            "schema": "komorebi.lasm_action.grid_gauge_signature",
            "schema_version": SCHEMA_VERSION,
        }
    )


def canonical_batch_signature(
    grids: Iterable[object],
    **orbit_options: object,
) -> str:
    """Order-sensitive canonical signature for a demonstration/test batch."""

    values = tuple(grids)
    if not values:
        raise ValueError("canonical batch must contain at least one grid")
    signatures = tuple(
        canonical_grid_signature(grid, **orbit_options) for grid in values
    )
    return sha256_record(
        {
            "grid_signatures": signatures,
            "schema": "komorebi.lasm_action.grid_gauge_batch_signature",
            "schema_version": SCHEMA_VERSION,
        }
    )


@dataclass(frozen=True, slots=True)
class GaugeTransport:
    """A typed ``G_out^-1 ∘ M ∘ G_in`` transport certificate."""

    input_gauge: GridGauge
    output_gauge: GridGauge

    def __post_init__(self) -> None:
        if not isinstance(self.input_gauge, GridGauge) or not isinstance(self.output_gauge, GridGauge):
            raise TypeError("transport endpoints must be GridGauge values")

    def execute(self, source: object, mechanism: GridMechanism) -> Grid:
        if not callable(mechanism):
            raise TypeError("mechanism must be callable")
        physical_input = validate_grid(source)
        canonical_input = self.input_gauge.forward(physical_input)
        canonical_output = validate_grid(mechanism(canonical_input))
        if _shape(canonical_output) != self.output_gauge.canonical_shape:
            raise GaugeUndefinedError(
                "canonical mechanism output shape does not match the output gauge image"
            )
        physical_output = self.output_gauge.inverse(canonical_output)
        # Re-entering the output gauge must recover the exact mechanism result.
        if self.output_gauge.forward(physical_output) != canonical_output:
            raise GaugeError("output gauge failed exact transport roundtrip")
        return physical_output

    def to_record(self) -> dict[str, object]:
        return {
            "input_gauge_id": self.input_gauge.content_hash,
            "kind": "gauge_transport",
            "output_gauge_id": self.output_gauge.content_hash,
            "schema_version": SCHEMA_VERSION,
        }

    @property
    def content_hash(self) -> str:
        return sha256_record(self.to_record())


@dataclass(frozen=True, slots=True)
class OrbitTransportResult:
    outputs: tuple[Grid, ...]
    transport_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        normalized_outputs = tuple(sorted({validate_grid(output) for output in self.outputs}))
        if not normalized_outputs:
            raise ValueError("orbit transport must contain at least one output")
        object.__setattr__(self, "outputs", normalized_outputs)
        if not self.transport_ids or any(not isinstance(item, str) or not item for item in self.transport_ids):
            raise ValueError("orbit transport IDs must be nonempty strings")
        object.__setattr__(self, "transport_ids", tuple(sorted(set(self.transport_ids))))

    @property
    def unambiguous(self) -> bool:
        return len(self.outputs) == 1

    def require_unique(self) -> Grid:
        if not self.unambiguous:
            raise AmbiguousGaugeError(
                f"gauge orbit produced {len(self.outputs)} distinct physical behaviors"
            )
        return self.outputs[0]


def build_transport_orbit(
    input_orbit: GaugeOrbit,
    output_orbit: GaugeOrbit,
    *,
    max_orbit: int = MAX_GAUGE_ORBIT,
) -> tuple[GaugeTransport, ...]:
    """Build a finite transport orbit without resolving symmetry by fiat.

    Every input adapter is paired with every output adapter.  A caller with an
    independently certified correspondence may instead construct an explicit
    tuple of :class:`GaugeTransport` values.
    """

    if not isinstance(input_orbit, GaugeOrbit) or not isinstance(output_orbit, GaugeOrbit):
        raise TypeError("transport orbits require GaugeOrbit endpoints")
    max_orbit = _require_positive_limit(max_orbit)
    count = len(input_orbit.gauges) * len(output_orbit.gauges)
    if count > max_orbit:
        raise GaugeOrbitLimitError(
            f"transport product requires {count} branches, limit is {max_orbit}"
        )
    pairs = itertools.product(input_orbit.gauges, output_orbit.gauges)
    transports = tuple(GaugeTransport(source, target) for source, target in pairs)
    if len(transports) > max_orbit:
        raise GaugeOrbitLimitError("transport orbit exceeds its finite budget")
    unique = {transport.content_hash: transport for transport in transports}
    return tuple(unique[key] for key in sorted(unique))


def execute_transport_orbit(
    source: object,
    mechanism: GridMechanism,
    transports: Iterable[GaugeTransport],
    *,
    max_orbit: int = MAX_GAUGE_ORBIT,
) -> OrbitTransportResult:
    """Execute every ambiguity branch and quotient only exact output equality."""

    values = tuple(transports)
    if not values:
        raise ValueError("transport orbit must not be empty")
    max_orbit = _require_positive_limit(max_orbit)
    if len(values) > max_orbit:
        raise GaugeOrbitLimitError("transport orbit exceeds its finite budget")
    if any(not isinstance(transport, GaugeTransport) for transport in values):
        raise TypeError("transport orbit entries must be GaugeTransport values")
    output_pairs = [(transport.execute(source, mechanism), transport.content_hash) for transport in values]
    return OrbitTransportResult(
        tuple(output for output, _ in output_pairs),
        tuple(identifier for _, identifier in output_pairs),
    )


def transport_mechanism(
    source: object,
    mechanism: GridMechanism,
    input_gauge: GridGauge,
    output_gauge: GridGauge,
) -> Grid:
    """Convenience wrapper for exact, typed input/output gauge transport."""

    return GaugeTransport(input_gauge, output_gauge).execute(source, mechanism)


@dataclass(frozen=True, slots=True)
class MetamorphicCheck:
    name: str
    passed: bool
    evidence_hash: str
    detail: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", _require_name(self.name, "check name"))
        if not isinstance(self.passed, bool):
            raise TypeError("passed must be Boolean")
        if not isinstance(self.evidence_hash, str) or len(self.evidence_hash) != 64:
            raise ValueError("evidence hash must be a SHA-256 hex digest")
        if not isinstance(self.detail, str):
            raise TypeError("detail must be a string")

    def to_record(self) -> dict[str, object]:
        return {
            "detail": self.detail,
            "evidence_hash": self.evidence_hash,
            "name": self.name,
            "passed": self.passed,
        }


@dataclass(frozen=True, slots=True)
class MetamorphicReport:
    checks: tuple[MetamorphicCheck, ...]

    def __post_init__(self) -> None:
        if not self.checks:
            raise ValueError("metamorphic report must contain at least one check")
        if any(not isinstance(check, MetamorphicCheck) for check in self.checks):
            raise TypeError("report entries must be MetamorphicCheck values")

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.checks)

    def require_pass(self) -> "MetamorphicReport":
        failed = [check.name for check in self.checks if not check.passed]
        if failed:
            raise GaugeError(f"metamorphic checks failed: {failed}")
        return self

    def to_record(self) -> dict[str, object]:
        body = {"checks": [check.to_record() for check in self.checks], "passed": self.passed}
        return {**body, "content_hash": sha256_record(body)}


def check_grid_gauge_metamorphisms(
    gauge: GridGauge,
    grids: Iterable[object],
) -> MetamorphicReport:
    """Check both exact roundtrips and deterministic replay on declared inputs."""

    if not isinstance(gauge, GridGauge):
        raise TypeError("gauge must be a GridGauge")
    values = tuple(validate_grid(grid) for grid in grids)
    if not values:
        raise ValueError("metamorphic checks require at least one grid")
    checks: list[MetamorphicCheck] = []
    for index, value in enumerate(values):
        evidence = {"gauge": gauge.content_hash, "grid": sha256_record(value), "index": index}
        digest = sha256_record(evidence)
        try:
            first = gauge.forward(value)
            restored = gauge.inverse(first)
            second = gauge.forward(value)
            physical_ok = restored == value
            deterministic = first == second
            canonical_ok = gauge.forward(gauge.inverse(first)) == first
            checks.extend(
                (
                    MetamorphicCheck(f"physical_roundtrip:{index}", physical_ok, digest),
                    MetamorphicCheck(f"canonical_roundtrip:{index}", canonical_ok, digest),
                    MetamorphicCheck(f"deterministic_replay:{index}", deterministic, digest),
                )
            )
        except Exception as error:  # report the fail-closed rejection, never hide it
            checks.append(
                MetamorphicCheck(
                    f"gauge_applicability:{index}",
                    False,
                    digest,
                    f"{type(error).__name__}: {error}",
                )
            )
    return MetamorphicReport(tuple(checks))


def check_transport_metamorphisms(
    transport: GaugeTransport,
    mechanism: GridMechanism,
    grids: Iterable[object],
) -> MetamorphicReport:
    """Verify the transport square and deterministic replay exactly."""

    if not isinstance(transport, GaugeTransport):
        raise TypeError("transport must be a GaugeTransport")
    if not callable(mechanism):
        raise TypeError("mechanism must be callable")
    values = tuple(validate_grid(grid) for grid in grids)
    if not values:
        raise ValueError("metamorphic checks require at least one grid")
    checks: list[MetamorphicCheck] = []
    for index, value in enumerate(values):
        evidence = {
            "grid": sha256_record(value),
            "index": index,
            "transport": transport.content_hash,
        }
        digest = sha256_record(evidence)
        try:
            canonical_input = transport.input_gauge.forward(value)
            canonical_output = validate_grid(mechanism(canonical_input))
            physical_output = transport.execute(value, mechanism)
            commutes = transport.output_gauge.forward(physical_output) == canonical_output
            deterministic = physical_output == transport.execute(value, mechanism)
            checks.extend(
                (
                    MetamorphicCheck(f"transport_square:{index}", commutes, digest),
                    MetamorphicCheck(f"transport_deterministic:{index}", deterministic, digest),
                )
            )
        except Exception as error:
            checks.append(
                MetamorphicCheck(
                    f"transport_applicability:{index}",
                    False,
                    digest,
                    f"{type(error).__name__}: {error}",
                )
            )
    return MetamorphicReport(tuple(checks))


def check_d4_group_metamorphisms(grids: Iterable[object]) -> MetamorphicReport:
    """Mechanically check the D4 identity, inverse, and composition table."""

    values = tuple(validate_grid(grid) for grid in grids)
    if not values:
        raise ValueError("D4 metamorphic checks require at least one grid")
    checks: list[MetamorphicCheck] = []
    for index, grid in enumerate(values):
        digest = sha256_record({"grid": grid, "index": index})
        identity_ok = apply_d4(grid, "id") == grid
        inverse_ok = all(
            apply_d4(apply_d4(grid, name), inverse_d4(name)) == grid
            for name in D4_NAMES
        )
        composition_ok = all(
            apply_d4(apply_d4(grid, first), second)
            == apply_d4(grid, compose_d4(first, second))
            for first in D4_NAMES
            for second in D4_NAMES
        )
        associativity_ok = all(
            compose_d4(compose_d4(first, second), third)
            == compose_d4(first, compose_d4(second, third))
            for first in D4_NAMES
            for second in D4_NAMES
            for third in D4_NAMES
        )
        checks.extend(
            (
                MetamorphicCheck(f"d4_identity:{index}", identity_ok, digest),
                MetamorphicCheck(f"d4_inverse:{index}", inverse_ok, digest),
                MetamorphicCheck(f"d4_composition:{index}", composition_ok, digest),
                MetamorphicCheck(f"d4_associativity:{index}", associativity_ok, digest),
            )
        )
    return MetamorphicReport(tuple(checks))


__all__ = [
    "AmbiguousGaugeError",
    "BoundingBox",
    "D4_COMPOSE",
    "D4_INVERSE",
    "D4_NAMES",
    "D4Gauge",
    "GaugeError",
    "GaugeOrbit",
    "GaugeOrbitLimitError",
    "GaugeTransport",
    "GaugeUndefinedError",
    "GridGauge",
    "MAX_GAUGE_ORBIT",
    "MetamorphicCheck",
    "MetamorphicReport",
    "ObjectLabelGauge",
    "ObjectLabelOrbit",
    "OrbitTransportResult",
    "PaletteGauge",
    "SupportTranslationGauge",
    "apply_d4",
    "build_transport_orbit",
    "canonical_gauge_orbit",
    "canonical_d4_orbit",
    "canonical_batch_signature",
    "canonical_grid_signature",
    "canonical_object_label_orbit",
    "check_d4_group_metamorphisms",
    "check_grid_gauge_metamorphisms",
    "check_transport_metamorphisms",
    "compose_d4",
    "execute_transport_orbit",
    "infer_support_translation",
    "infer_palette_role_orbit",
    "inverse_d4",
    "normalize_d4_name",
    "transport_mechanism",
]
