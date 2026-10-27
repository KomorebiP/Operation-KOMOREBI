"""Bounded, palette-equivariant programs over structural object roles.

The legacy stencil learner stores literal colours, shapes, and offsets.  This
module is a deliberately small alternative representation: programs bind
roles again on every input and their persistent records cannot contain a
resolved colour, coordinate, task identifier, or raster.

The generic language has a 4-connected monochrome-component domain.  It
supports strict ``THE`` extrema, strict nearest/farthest Manhattan relations,
and ``FOR_EACH``.  Effects are evaluated against an immutable source and are
committed atomically.  Three additional fixed structural operators use the
same role/effect record schema:

* retain the unique largest maximal filled monochrome subrectangle;
* complete an occluded horizontal, vertical, diagonal, or filled-rectangle
  primitive through one non-background blocker colour; and
* erase the first non-background ray hit beyond a singleton marker and a
  contiguous straight guide.

Compilation is finite and deterministic.  Exact demonstration replay is
necessary but is followed by leave-one-*distinct-example-group*-out
rediscovery of the identical canonical program hash.  Duplicate examples
therefore cannot manufacture independent support.  Test targets are not an
argument to this module and test inputs are used only after certification.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Dict, Iterable, Mapping, Optional, Sequence, Tuple

import numpy as np


Array = np.ndarray
Cell = Tuple[int, int]
Box = Tuple[int, int, int, int]

SCHEMA = "komorebi.arc.role-bound-object-program.v1"
SCHEMA_VERSION = 1
FAMILY = "causal_role_bound_object_rewrite"

_COMPONENT_OPERATOR = "component_effect"
_RECTANGLE_OPERATOR = "retain_unique_maximal_filled_rectangle"
_OCCLUSION_OPERATOR = "complete_occluded_regular_primitive"
_RAY_OPERATOR = "erase_marker_guide_ray_boundary"

_FIXED_OPERATORS = frozenset(
    (_RECTANGLE_OPERATOR, _OCCLUSION_OPERATOR, _RAY_OPERATOR)
)
_OPERATORS = frozenset((_COMPONENT_OPERATOR, *_FIXED_OPERATORS))
_QUANTIFIERS = frozenset(("THE", "FOR_EACH"))
_EXTREME_METRICS = frozenset(
    ("area", "bbox_area", "height", "width", "perimeter", "density")
)
_EXTREME_ORDERS = frozenset(("minimum", "maximum"))
_RELATION_ORDERS = frozenset(("nearest", "farthest"))
_EFFECT_KINDS = frozenset(("paint", "erase", "retain", "fill_bbox"))
_TARGET_KINDS = frozenset(("cells", "exterior_band_1", "bbox"))
_GENERIC_ROLE_SEQUENCES = frozenset(
    (("subject",), ("reference", "subject"))
)


class RoleBindingError(ValueError):
    """Base class for invalid role programs and source rasters."""


class RoleBindingAbstention(RoleBindingError):
    """Raised when an input has no unique admissible role interpretation."""


class RoleBindingAmbiguityError(RoleBindingAbstention):
    """Raised when exact training explanations predict divergent test grids."""


class RoleBindingLimitError(RoleBindingError):
    """Raised before a configured finite representation budget is exceeded."""


@dataclass(frozen=True)
class RoleBoundObjectLimits:
    """Hard representation and enumeration budgets."""

    maximum_height: int = 30
    maximum_width: int = 30
    maximum_cells: int = 900
    maximum_palette: int = 10
    maximum_components: int = 128
    maximum_examples: int = 8
    maximum_tests: int = 8
    maximum_programs: int = 96
    maximum_candidates: int = 24
    maximum_writes: int = 900
    maximum_rectangle_checks: int = 300_000
    maximum_primitive_hypotheses: int = 128

    def __post_init__(self) -> None:
        for name, value in asdict(self).items():
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, np.integer))
                or int(value) <= 0
            ):
                raise RoleBindingLimitError(f"{name} must be a positive integer")

    def to_record(self) -> Dict[str, int]:
        return {name: int(value) for name, value in asdict(self).items()}


DEFAULT_LIMITS = RoleBoundObjectLimits()


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def role_bound_implementation_fingerprint() -> str:
    """Hash the executable interpreter/compiler source used by an audit.

    Program hashes intentionally identify declarative semantics only.  The
    promotion receipt separately binds those programs to these implementation
    bytes, so an interpreter edit invalidates the empirical gate until the
    full gains/losses audit is rerun.
    """

    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def _mapping(value: object, context: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise RoleBindingError(f"{context} must be a mapping")
    return value


def _exact_keys(
    record: Mapping[str, object], expected: Iterable[str], context: str
) -> None:
    wanted = set(expected)
    present = set(record)
    if present != wanted:
        raise RoleBindingError(
            f"{context} fields do not match schema; "
            f"missing={sorted(wanted - present)}, extra={sorted(present - wanted)}"
        )


def _plain(value: object) -> object:
    """Return a detached, recursively JSON-safe value."""

    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Mapping):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_plain(item) for item in value]
    raise RoleBindingError(f"noncanonical value of type {type(value).__name__}")


def _component_binding(
    role: str, selector: Mapping[str, object]
) -> Dict[str, object]:
    return {"role": str(role), "selector": dict(selector)}


def _fixed_program_parts(
    operator: str,
) -> Tuple[str, str, Tuple[Dict[str, object], ...], Dict[str, object]]:
    if operator == _RECTANGLE_OPERATOR:
        return (
            "filled_monochrome_subrectangles",
            "THE",
            (
                _component_binding(
                    "subject",
                    {
                        "kind": "unique_structural",
                        "predicate": "maximal_filled_subrectangle",
                        "order": "maximum_area",
                    },
                ),
            ),
            {"kind": "retain", "role": "subject", "target": "cells"},
        )
    if operator == _OCCLUSION_OPERATOR:
        return (
            "regular_primitives_by_symbolic_colour",
            "FOR_EACH",
            (
                _component_binding(
                    "subject",
                    {
                        "kind": "all",
                        "predicate": "uniquely_occluded_regular_primitive",
                    },
                ),
                _component_binding(
                    "blocker",
                    {
                        "kind": "structural_relation",
                        "relation": "occupies_missing_support",
                        "relative_to": "subject",
                    },
                ),
            ),
            {
                "kind": "paint",
                "role": "subject",
                "target": "missing_regular_support",
                "color_role": "subject",
            },
        )
    if operator == _RAY_OPERATOR:
        return (
            "symbolic_colour_lines_and_singletons",
            "THE",
            (
                _component_binding(
                    "marker", {"kind": "unique_structural", "predicate": "singleton"}
                ),
                _component_binding(
                    "guide",
                    {
                        "kind": "structural_relation",
                        "relation": "contiguous_line_endpoint_precedes_marker",
                        "relative_to": "marker",
                    },
                ),
                _component_binding(
                    "boundary",
                    {
                        "kind": "structural_relation",
                        "relation": "first_nonbackground_outward_ray_hit",
                        "relative_to": "marker",
                    },
                ),
            ),
            {"kind": "erase", "role": "boundary", "target": "cells"},
        )
    raise RoleBindingError(f"unknown fixed operator {operator!r}")


@dataclass(frozen=True)
class RoleBoundObjectProgram:
    """Canonical executable program whose bindings contain no literals."""

    operator: str
    bindings: Tuple[Mapping[str, object], ...]
    effect: Mapping[str, object]
    quantifier: str = "THE"
    domain: str = "monochrome_components_4"
    background_policy: str = "unique_global_mode"
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.schema_version != SCHEMA_VERSION:
            raise RoleBindingError(
                f"unsupported schema version {self.schema_version}; "
                f"expected {SCHEMA_VERSION}"
            )
        if self.operator not in _OPERATORS:
            raise RoleBindingError(f"unknown role-bound operator {self.operator!r}")
        if self.quantifier not in _QUANTIFIERS:
            raise RoleBindingError(f"unknown quantifier {self.quantifier!r}")
        if self.background_policy != "unique_global_mode":
            raise RoleBindingError(
                "the palette-equivariant v1 language requires unique_global_mode"
            )
        raw_bindings = self.bindings
        if not isinstance(raw_bindings, (tuple, list)) or not raw_bindings:
            raise RoleBindingError("bindings must be a nonempty sequence")
        bindings = tuple(
            _normalize_binding(binding, index)
            for index, binding in enumerate(raw_bindings)
        )
        effect = _normalize_effect(self.effect, self.operator)
        object.__setattr__(self, "bindings", bindings)
        object.__setattr__(self, "effect", effect)

        if self.operator in _FIXED_OPERATORS:
            domain, quantifier, expected_bindings, expected_effect = (
                _fixed_program_parts(self.operator)
            )
            if (
                self.domain != domain
                or self.quantifier != quantifier
                or list(bindings) != list(expected_bindings)
                or dict(effect) != expected_effect
            ):
                raise RoleBindingError(
                    "fixed structural operator must use its canonical role schema"
                )
        else:
            if self.domain != "monochrome_components_4":
                raise RoleBindingError("component programs require the 4-connected domain")
            _validate_component_program(bindings, effect, self.quantifier)

    @classmethod
    def from_record(cls, raw: object) -> "RoleBoundObjectProgram":
        record = _mapping(raw, "role-bound program")
        _exact_keys(
            record,
            {
                "schema",
                "schema_version",
                "operator",
                "domain",
                "background_policy",
                "quantifier",
                "bindings",
                "effect",
            },
            "role-bound program",
        )
        if record["schema"] != SCHEMA:
            raise RoleBindingError(f"unknown program schema {record['schema']!r}")
        bindings = record["bindings"]
        if not isinstance(bindings, list):
            raise RoleBindingError("serialized bindings must be a list")
        return cls(
            operator=str(record["operator"]),
            domain=str(record["domain"]),
            quantifier=str(record["quantifier"]),
            bindings=tuple(_mapping(item, "binding") for item in bindings),
            effect=_mapping(record["effect"], "effect"),
            background_policy=str(record["background_policy"]),
            schema_version=int(record["schema_version"]),
        )

    @classmethod
    def unique_maximal_filled_rectangle_retention(
        cls,
    ) -> "RoleBoundObjectProgram":
        domain, quantifier, bindings, effect = _fixed_program_parts(
            _RECTANGLE_OPERATOR
        )
        return cls(_RECTANGLE_OPERATOR, bindings, effect, quantifier, domain)

    @classmethod
    def occluded_regular_primitive_completion(cls) -> "RoleBoundObjectProgram":
        domain, quantifier, bindings, effect = _fixed_program_parts(
            _OCCLUSION_OPERATOR
        )
        return cls(_OCCLUSION_OPERATOR, bindings, effect, quantifier, domain)

    @classmethod
    def marker_guide_ray_boundary_erasure(cls) -> "RoleBoundObjectProgram":
        domain, quantifier, bindings, effect = _fixed_program_parts(_RAY_OPERATOR)
        return cls(_RAY_OPERATOR, bindings, effect, quantifier, domain)

    def to_record(self) -> Dict[str, object]:
        """Return the detached canonical artifact, never runtime bindings."""

        record: Dict[str, object] = {
            "schema": SCHEMA,
            "schema_version": int(self.schema_version),
            "operator": str(self.operator),
            "domain": str(self.domain),
            "background_policy": str(self.background_policy),
            "quantifier": str(self.quantifier),
            "bindings": _plain(self.bindings),
            "effect": _plain(self.effect),
        }
        # Serialization itself is part of validation: no custom encoder may
        # smuggle arrays, coordinates, or non-finite scalars into the record.
        _canonical_json(record)
        return record

    @property
    def semantic_key(self) -> str:
        return _canonical_json(
            {
                "operator": self.operator,
                "domain": self.domain,
                "background_policy": self.background_policy,
                "quantifier": self.quantifier,
                "bindings": _plain(self.bindings),
                "effect": _plain(self.effect),
            }
        )

    def program_hash(self) -> str:
        return hashlib.sha256(_canonical_json(self.to_record()).encode("ascii")).hexdigest()

    def content_hash(self) -> str:
        """Compatibility alias for content-addressed program stores."""

        return self.program_hash()

    @property
    def complexity(self) -> int:
        fixed = {
            _RECTANGLE_OPERATOR: 18,
            _OCCLUSION_OPERATOR: 24,
            _RAY_OPERATOR: 22,
        }
        if self.operator in fixed:
            return fixed[self.operator]
        effect_cost = {"paint": 3, "erase": 2, "retain": 4, "fill_bbox": 4}
        return 5 + 4 * len(self.bindings) + effect_cost[str(self.effect["kind"])]

    def apply(
        self,
        grid: Array,
        *,
        limits: RoleBoundObjectLimits = DEFAULT_LIMITS,
    ) -> Array:
        return execute_role_bound_object_program(self, grid, limits=limits)


def _normalize_binding(raw: object, index: int) -> Dict[str, object]:
    binding = _mapping(raw, f"binding {index}")
    _exact_keys(binding, {"role", "selector"}, f"binding {index}")
    role = binding["role"]
    if not isinstance(role, str) or not role or role.strip() != role:
        raise RoleBindingError("role names must be nonempty and trimmed")
    selector = _mapping(binding["selector"], f"selector for {role}")
    if not all(isinstance(key, str) for key in selector):
        raise RoleBindingError("selector keys must be strings")
    return {"role": role, "selector": dict(_plain(selector))}


def _normalize_effect(raw: object, operator: str) -> Dict[str, object]:
    effect = _mapping(raw, "effect")
    if not all(isinstance(key, str) for key in effect):
        raise RoleBindingError("effect keys must be strings")
    normalized = dict(_plain(effect))
    if operator in _FIXED_OPERATORS:
        return normalized
    kind = normalized.get("kind")
    if kind not in _EFFECT_KINDS:
        raise RoleBindingError(f"unknown component effect {kind!r}")
    expected = {"kind", "role", "target"}
    if kind in ("paint", "fill_bbox"):
        expected.add("color_role")
    _exact_keys(normalized, expected, "component effect")
    if normalized["target"] not in _TARGET_KINDS:
        raise RoleBindingError(f"unknown effect target {normalized['target']!r}")
    if kind == "fill_bbox" and normalized["target"] != "bbox":
        raise RoleBindingError("fill_bbox must target bbox")
    if kind != "fill_bbox" and normalized["target"] == "bbox":
        raise RoleBindingError("bbox target is reserved for fill_bbox")
    return normalized


def _validate_component_program(
    bindings: Sequence[Mapping[str, object]],
    effect: Mapping[str, object],
    quantifier: str,
) -> None:
    roles = tuple(str(binding["role"]) for binding in bindings)
    if roles not in _GENERIC_ROLE_SEQUENCES:
        raise RoleBindingError(
            "component roles must use the finite canonical vocabulary and order"
        )
    known: set[str] = set()
    quantified: set[str] = set()
    all_count = 0
    for binding in bindings:
        role = str(binding["role"])
        if role in known or role == "background":
            raise RoleBindingError(f"duplicate or reserved role {role!r}")
        selector = _mapping(binding["selector"], f"selector for {role}")
        kind = selector.get("kind")
        if kind == "all":
            _exact_keys(selector, {"kind"}, f"selector for {role}")
            all_count += 1
            quantified.add(role)
        elif kind == "unique_extreme":
            _exact_keys(
                selector, {"kind", "metric", "order"}, f"selector for {role}"
            )
            if selector["metric"] not in _EXTREME_METRICS:
                raise RoleBindingError(f"unknown extreme metric {selector['metric']!r}")
            if selector["order"] not in _EXTREME_ORDERS:
                raise RoleBindingError(f"unknown extreme order {selector['order']!r}")
        elif kind == "relation_extreme":
            _exact_keys(
                selector,
                {"kind", "relation", "order", "relative_to"},
                f"selector for {role}",
            )
            if selector["relation"] != "manhattan":
                raise RoleBindingError("only cell-set Manhattan relation is supported")
            if selector["order"] not in _RELATION_ORDERS:
                raise RoleBindingError(f"unknown relation order {selector['order']!r}")
            relative = selector["relative_to"]
            if relative not in known or relative in quantified:
                raise RoleBindingError(
                    "relation_extreme must reference an earlier unique binding"
                )
        else:
            raise RoleBindingError(f"unknown selector kind {kind!r}")
        known.add(role)
    if quantifier == "THE" and all_count:
        raise RoleBindingError("THE cannot contain an all selector")
    if quantifier == "FOR_EACH" and all_count != 1:
        raise RoleBindingError("FOR_EACH requires exactly one all selector")
    role = effect.get("role")
    if role not in known:
        raise RoleBindingError(f"effect references unbound role {role!r}")
    color_role = effect.get("color_role")
    if color_role is not None and color_role != "background" and color_role not in known:
        raise RoleBindingError(f"effect references unbound colour role {color_role!r}")


@dataclass(frozen=True)
class _Component:
    color: int
    cells: Tuple[Cell, ...]
    box: Box

    @property
    def area(self) -> int:
        return len(self.cells)

    @property
    def height(self) -> int:
        return self.box[2] - self.box[0] + 1

    @property
    def width(self) -> int:
        return self.box[3] - self.box[1] + 1

    @property
    def bbox_area(self) -> int:
        return self.height * self.width

    @property
    def density(self) -> Fraction:
        return Fraction(self.area, self.bbox_area)

    @property
    def perimeter(self) -> int:
        occupied = set(self.cells)
        return sum(
            (row + dr, column + dc) not in occupied
            for row, column in self.cells
            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1))
        )


def _validated_grid(grid: Array, limits: RoleBoundObjectLimits) -> Array:
    try:
        raw = np.asarray(grid)
    except (TypeError, ValueError) as error:
        raise RoleBindingError("grid must be a rectangular numeric raster") from error
    if raw.ndim != 2 or raw.size == 0:
        raise RoleBindingError("role binding requires a nonempty 2D grid")
    height, width = raw.shape
    if height > limits.maximum_height or width > limits.maximum_width:
        raise RoleBindingLimitError(
            f"grid shape {raw.shape} exceeds "
            f"{limits.maximum_height}x{limits.maximum_width}"
        )
    if raw.size > limits.maximum_cells:
        raise RoleBindingLimitError("cell budget exceeded")
    if np.issubdtype(raw.dtype, np.bool_):
        raise RoleBindingError("Boolean rasters are not ARC colour grids")
    if not np.issubdtype(raw.dtype, np.integer):
        try:
            integral = np.equal(raw, np.floor(raw))
        except (TypeError, ValueError) as error:
            raise RoleBindingError("grid values must be integers") from error
        if not bool(np.all(integral)):
            raise RoleBindingError("grid values must be integers")
    try:
        minimum = int(np.min(raw))
        maximum = int(np.max(raw))
    except (TypeError, ValueError, OverflowError) as error:
        raise RoleBindingError("grid values must be finite integers") from error
    if minimum < 0 or maximum > 9:
        raise RoleBindingError("ARC colours must lie in [0, 9]")
    value = np.asarray(raw, dtype=np.int16)
    palette = np.unique(value)
    if len(palette) > limits.maximum_palette:
        raise RoleBindingLimitError("palette budget exceeded")
    return np.ascontiguousarray(value)


def _background(grid: Array) -> int:
    colors, counts = np.unique(grid, return_counts=True)
    maximum = int(counts.max())
    winners = colors[counts == maximum]
    if len(winners) != 1:
        raise RoleBindingAbstention("global-mode background is not unique")
    return int(winners[0])


def _components(
    grid: Array, background: int, limits: RoleBoundObjectLimits
) -> Tuple[_Component, ...]:
    height, width = grid.shape
    seen: set[Cell] = set()
    found: list[_Component] = []
    for row in range(height):
        for column in range(width):
            if (row, column) in seen or int(grid[row, column]) == background:
                continue
            color = int(grid[row, column])
            stack = [(row, column)]
            seen.add((row, column))
            cells: list[Cell] = []
            while stack:
                current = stack.pop()
                cells.append(current)
                cr, cc = current
                for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nxt = cr + dr, cc + dc
                    if (
                        0 <= nxt[0] < height
                        and 0 <= nxt[1] < width
                        and nxt not in seen
                        and int(grid[nxt]) == color
                    ):
                        seen.add(nxt)
                        stack.append(nxt)
            ordered = tuple(sorted(cells))
            rows = [cell[0] for cell in ordered]
            columns = [cell[1] for cell in ordered]
            found.append(
                _Component(
                    color=color,
                    cells=ordered,
                    box=(min(rows), min(columns), max(rows), max(columns)),
                )
            )
            if len(found) > limits.maximum_components:
                raise RoleBindingLimitError("component budget exceeded")
    if not found:
        raise RoleBindingAbstention("source contains no foreground components")
    return tuple(found)


def _metric(component: _Component, metric: str) -> int | Fraction:
    return getattr(component, metric)


def _cell_manhattan(left: _Component, right: _Component) -> int:
    return min(
        abs(lr - rr) + abs(lc - rc)
        for lr, lc in left.cells
        for rr, rc in right.cells
    )


def _strict_extreme(
    candidates: Sequence[_Component], values: Sequence[object], order: str
) -> _Component:
    if not candidates:
        raise RoleBindingAbstention("selector has no candidates")
    extreme = min(values) if order in ("minimum", "nearest") else max(values)
    winners = [item for item, value in zip(candidates, values) if value == extreme]
    if len(winners) != 1:
        raise RoleBindingAbstention("selector extreme is tied")
    return winners[0]


def _bind_components(
    program: RoleBoundObjectProgram,
    components: Sequence[_Component],
    *,
    support: Optional[Dict[str, int]] = None,
) -> Tuple[Dict[str, _Component], ...]:
    contexts: list[Dict[str, _Component]] = [{}]
    for binding in program.bindings:
        role = str(binding["role"])
        selector = _mapping(binding["selector"], "selector")
        expanded: list[Dict[str, _Component]] = []
        for context in contexts:
            used = set(context.values())
            candidates = [item for item in components if item not in used]
            kind = selector["kind"]
            if kind == "all":
                if not candidates:
                    raise RoleBindingAbstention("FOR_EACH selector is empty")
                if support is not None:
                    support["foreach_cardinality"] = max(
                        support.get("foreach_cardinality", 0), len(candidates)
                    )
                for candidate in candidates:
                    expanded.append({**context, role: candidate})
                continue
            if kind == "unique_extreme":
                metric = str(selector["metric"])
                chosen = _strict_extreme(
                    candidates,
                    [_metric(item, metric) for item in candidates],
                    str(selector["order"]),
                )
            elif kind == "relation_extreme":
                reference = context[str(selector["relative_to"])]
                if support is not None:
                    support["relation_candidate_count"] = max(
                        support.get("relation_candidate_count", 0), len(candidates)
                    )
                chosen = _strict_extreme(
                    candidates,
                    [_cell_manhattan(item, reference) for item in candidates],
                    str(selector["order"]),
                )
            else:  # validated programs cannot reach structural selectors here
                raise RoleBindingError(f"unsupported runtime selector {kind!r}")
            expanded.append({**context, role: chosen})
        contexts = expanded
    if not contexts:
        raise RoleBindingAbstention("role binding produced no contexts")
    return tuple(contexts)


def _component_program_support(
    program: RoleBoundObjectProgram,
    source: Array,
    limits: RoleBoundObjectLimits,
) -> Dict[str, int]:
    """Measure witnessed selector alternatives without consulting a target."""

    support: Dict[str, int] = {
        "scene_component_count": 0,
        "relation_candidate_count": 0,
        "foreach_cardinality": 0,
    }
    background = _background(source)
    components = _components(source, background, limits)
    support["scene_component_count"] = len(components)
    _bind_components(program, components, support=support)
    return support


def _box_cells(box: Box) -> Tuple[Cell, ...]:
    top, left, bottom, right = box
    return tuple(
        (row, column)
        for row in range(top, bottom + 1)
        for column in range(left, right + 1)
    )


def _exterior_band(box: Box, shape: Tuple[int, int]) -> Tuple[Cell, ...]:
    top, left, bottom, right = box
    height, width = shape
    cells = []
    for row in range(max(0, top - 1), min(height - 1, bottom + 1) + 1):
        for column in range(max(0, left - 1), min(width - 1, right + 1) + 1):
            if not (top <= row <= bottom and left <= column <= right):
                cells.append((row, column))
    return tuple(cells)


def _commit_writes(
    source: Array,
    writes: Iterable[Tuple[Cell, int]],
    limits: RoleBoundObjectLimits,
    *,
    base: Optional[Array] = None,
) -> Array:
    height, width = source.shape
    requested: Dict[Cell, int] = {}
    for cell, raw_color in writes:
        row, column = cell
        color = int(raw_color)
        if not (0 <= row < height and 0 <= column < width):
            raise RoleBindingAbstention("effect requested an out-of-bounds write")
        previous = requested.get(cell)
        if previous is not None and previous != color:
            raise RoleBindingAbstention("atomic effects request conflicting colours")
        requested[cell] = color
        if len(requested) > limits.maximum_writes:
            raise RoleBindingLimitError("write budget exceeded")
    if not requested:
        raise RoleBindingAbstention("effect has an empty target")
    output = source.copy() if base is None else np.asarray(base, dtype=np.int16).copy()
    for (row, column), color in requested.items():
        output[row, column] = color
    return np.ascontiguousarray(output)


def _execute_component_program(
    program: RoleBoundObjectProgram,
    source: Array,
    background: int,
    limits: RoleBoundObjectLimits,
) -> Array:
    components = _components(source, background, limits)
    contexts = _bind_components(program, components)
    effect = program.effect
    kind = str(effect["kind"])
    role = str(effect["role"])
    target = str(effect["target"])
    writes: list[Tuple[Cell, int]] = []
    retain_base: Optional[Array] = None
    if kind == "retain":
        retain_base = np.full(source.shape, background, dtype=np.int16)
    for context in contexts:
        subject = context[role]
        if target == "cells":
            cells = subject.cells
        elif target == "exterior_band_1":
            cells = _exterior_band(subject.box, source.shape)
        elif target == "bbox":
            cells = _box_cells(subject.box)
        else:
            raise RoleBindingError(f"unsupported target {target!r}")
        if kind == "erase":
            color = background
            writes.extend((cell, color) for cell in cells)
        elif kind == "retain":
            writes.extend((cell, int(source[cell])) for cell in cells)
        else:
            color_role = str(effect["color_role"])
            color = background if color_role == "background" else context[color_role].color
            if kind == "fill_bbox":
                # Filling is source-preserving: foreground distractors inside the
                # selected box are evidence, not writable background.  Filtering
                # against the immutable source also keeps FOR_EACH execution
                # independent of context traversal order.
                cells = tuple(cell for cell in cells if int(source[cell]) == background)
            writes.extend((cell, color) for cell in cells)
    return _commit_writes(source, writes, limits, base=retain_base)


def _filled_subrectangles(
    source: Array, background: int, limits: RoleBoundObjectLimits
) -> Tuple[Tuple[int, Box], ...]:
    height, width = source.shape
    raw: set[Tuple[int, Box]] = set()
    checks = 0
    for raw_color in np.unique(source):
        color = int(raw_color)
        if color == background:
            continue
        mask = source == color
        for top in range(height - 1):
            common = np.ones(width, dtype=bool)
            for bottom in range(top, height):
                common &= mask[bottom, :]
                checks += width
                if checks > limits.maximum_rectangle_checks:
                    raise RoleBindingLimitError("filled-subrectangle check budget exceeded")
                if bottom == top:
                    continue
                start: Optional[int] = None
                for index, value in enumerate(common.tolist() + [False]):
                    if value and start is None:
                        start = index
                    elif not value and start is not None:
                        if index - start >= 2:
                            raw.add((color, (top, start, bottom, index - 1)))
                        start = None
    maximal = []
    for color, box in raw:
        top, left, bottom, right = box
        contained = any(
            other_color == color
            and other_box != box
            and other_box[0] <= top
            and other_box[1] <= left
            and other_box[2] >= bottom
            and other_box[3] >= right
            for other_color, other_box in raw
        )
        if not contained:
            maximal.append((color, box))
    return tuple(sorted(maximal, key=lambda item: (item[1], item[0])))


def _execute_rectangle_retention(
    source: Array, background: int, limits: RoleBoundObjectLimits
) -> Array:
    rectangles = _filled_subrectangles(source, background, limits)
    if not rectangles:
        raise RoleBindingAbstention("no filled foreground subrectangle")
    areas = [
        (box[2] - box[0] + 1) * (box[3] - box[1] + 1)
        for _, box in rectangles
    ]
    maximum = max(areas)
    winners = [item for item, area in zip(rectangles, areas) if area == maximum]
    if len(winners) != 1:
        raise RoleBindingAbstention("largest filled subrectangle is tied")
    color, box = winners[0]
    base = np.full(source.shape, background, dtype=np.int16)
    return _commit_writes(
        source,
        ((cell, color) for cell in _box_cells(box)),
        limits,
        base=base,
    )


def _line_support(cells: Sequence[Cell]) -> Optional[Tuple[Cell, ...]]:
    if len(cells) < 3:
        return None
    points = set(cells)
    rows = [cell[0] for cell in cells]
    columns = [cell[1] for cell in cells]
    if len(set(rows)) == 1:
        row = rows[0]
        return tuple((row, column) for column in range(min(columns), max(columns) + 1))
    if len(set(columns)) == 1:
        column = columns[0]
        return tuple((row, column) for row in range(min(rows), max(rows) + 1))
    if len({row - column for row, column in cells}) == 1:
        start, end = min(points), max(points)
        return tuple(
            (start[0] + offset, start[1] + offset)
            for offset in range(end[0] - start[0] + 1)
        )
    if len({row + column for row, column in cells}) == 1:
        start = min(points)
        end = max(points)
        return tuple(
            (start[0] + offset, start[1] - offset)
            for offset in range(end[0] - start[0] + 1)
        )
    return None


def _primitive_hypotheses(
    source: Array, background: int, limits: RoleBoundObjectLimits
) -> Tuple[Tuple[int, Tuple[Cell, ...], int, str], ...]:
    hypotheses: list[Tuple[int, Tuple[Cell, ...], int, str]] = []
    for raw_color in np.unique(source):
        color = int(raw_color)
        if color == background:
            continue
        own = tuple(map(tuple, np.argwhere(source == color).tolist()))
        own_set = set(own)

        support = _line_support(own)
        if support is not None:
            missing = tuple(cell for cell in support if cell not in own_set)
            if missing and 2 * len(own) > len(support):
                blockers = {int(source[cell]) for cell in missing}
                if len(blockers) == 1 and background not in blockers and color not in blockers:
                    blocker = next(iter(blockers))
                    if int(np.sum(source == blocker)) > sum(
                        int(source[cell]) == blocker for cell in support
                    ):
                        hypotheses.append((color, missing, blocker, "line"))

        rows = [cell[0] for cell in own]
        columns = [cell[1] for cell in own]
        box = (min(rows), min(columns), max(rows), max(columns))
        if box[2] > box[0] and box[3] > box[1]:
            rectangle = _box_cells(box)
            missing = tuple(cell for cell in rectangle if cell not in own_set)
            if missing and 2 * len(own) > len(rectangle):
                blockers = {int(source[cell]) for cell in missing}
                if len(blockers) == 1 and background not in blockers and color not in blockers:
                    blocker = next(iter(blockers))
                    if int(np.sum(source == blocker)) > sum(
                        int(source[cell]) == blocker for cell in rectangle
                    ):
                        hypotheses.append(
                            (color, missing, blocker, "filled_rectangle")
                        )
        if len(hypotheses) > limits.maximum_primitive_hypotheses:
            raise RoleBindingLimitError("primitive hypothesis budget exceeded")
    return tuple(hypotheses)


def _execute_occlusion_completion(
    source: Array, background: int, limits: RoleBoundObjectLimits
) -> Array:
    hypotheses = _primitive_hypotheses(source, background, limits)
    if not hypotheses:
        raise RoleBindingAbstention("no uniquely occluded regular primitive")
    by_color: Dict[int, set[Tuple[str, Tuple[Cell, ...]]]] = {}
    for color, missing, _, kind in hypotheses:
        by_color.setdefault(color, set()).add((kind, tuple(sorted(missing))))
    if any(len(variants) != 1 for variants in by_color.values()):
        raise RoleBindingAbstention("one symbolic colour has multiple completions")
    writes = [
        (cell, color)
        for color, variants in by_color.items()
        for cell in next(iter(variants))[1]
    ]
    return _commit_writes(source, writes, limits)


def _contiguous_line(cells: Sequence[Cell]) -> Optional[Tuple[Cell, Cell, Cell]]:
    """Return ordered endpoints and positive unit step for a complete line."""

    if len(cells) < 3:
        return None
    points = set(cells)
    rows = [cell[0] for cell in cells]
    columns = [cell[1] for cell in cells]
    if len(set(rows)) == 1:
        ordered = sorted(points)
        step = (0, 1)
    elif len(set(columns)) == 1:
        ordered = sorted(points)
        step = (1, 0)
    elif len({row - column for row, column in cells}) == 1:
        ordered = sorted(points)
        step = (1, 1)
    elif len({row + column for row, column in cells}) == 1:
        ordered = sorted(points)
        step = (1, -1)
    else:
        return None
    start, end = ordered[0], ordered[-1]
    length = max(abs(end[0] - start[0]), abs(end[1] - start[1])) + 1
    expected = {
        (start[0] + offset * step[0], start[1] + offset * step[1])
        for offset in range(length)
    }
    if expected != points:
        return None
    return start, end, step


def _execute_marker_guide_ray(
    source: Array, background: int, limits: RoleBoundObjectLimits
) -> Array:
    height, width = source.shape
    colors = [int(color) for color in np.unique(source) if int(color) != background]
    singleton_colors = [color for color in colors if int(np.sum(source == color)) == 1]
    if len(singleton_colors) != 1:
        raise RoleBindingAbstention("singleton marker role is not unique")
    marker_color = singleton_colors[0]
    marker = tuple(map(int, np.argwhere(source == marker_color)[0]))
    interpretations: list[Tuple[int, Cell]] = []
    for guide_color in colors:
        if guide_color == marker_color:
            continue
        guide_cells = tuple(map(tuple, np.argwhere(source == guide_color).tolist()))
        line = _contiguous_line(guide_cells)
        if line is None:
            continue
        start, end, step = line
        endpoint_options = (
            (start, (-step[0], -step[1])),
            (end, step),
        )
        for endpoint, direction in endpoint_options:
            expected_marker = endpoint[0] + direction[0], endpoint[1] + direction[1]
            if marker != expected_marker:
                continue
            row, column = marker[0] + direction[0], marker[1] + direction[1]
            background_span = 0
            while 0 <= row < height and 0 <= column < width:
                if int(source[row, column]) != background:
                    if background_span:
                        interpretations.append((guide_color, (row, column)))
                    break
                background_span += 1
                row += direction[0]
                column += direction[1]
    unique = set(interpretations)
    if len(unique) != 1:
        raise RoleBindingAbstention("marker-guide ray interpretation is not unique")
    _, target = next(iter(unique))
    return _commit_writes(source, ((target, background),), limits)


def execute_role_bound_object_program(
    program: RoleBoundObjectProgram | Mapping[str, object],
    grid: Array,
    *,
    limits: RoleBoundObjectLimits = DEFAULT_LIMITS,
) -> Array:
    """Rebind and transactionally execute one canonical role program."""

    if not isinstance(program, RoleBoundObjectProgram):
        program = RoleBoundObjectProgram.from_record(program)
    source = _validated_grid(grid, limits)
    background = _background(source)
    if program.operator == _COMPONENT_OPERATOR:
        output = _execute_component_program(program, source, background, limits)
    elif program.operator == _RECTANGLE_OPERATOR:
        output = _execute_rectangle_retention(source, background, limits)
    elif program.operator == _OCCLUSION_OPERATOR:
        output = _execute_occlusion_completion(source, background, limits)
    elif program.operator == _RAY_OPERATOR:
        output = _execute_marker_guide_ray(source, background, limits)
    else:  # constructor validation makes this unreachable
        raise RoleBindingError(f"unknown operator {program.operator!r}")
    if output.shape != source.shape:
        raise RoleBindingError("role effect changed the raster shape")
    return np.asarray(output, dtype=np.int64).copy()


@dataclass(frozen=True)
class RoleBoundObjectCandidate:
    """Entry-independent exact candidate with an executable program record."""

    name: str
    program: RoleBoundObjectProgram
    grids: Tuple[Array, ...]
    train_grids: Tuple[Array, ...]
    complexity: int
    metadata: Mapping[str, object]
    family: str = FAMILY
    train_error: int = 0

    def to_record(self, *, include_grids: bool = True) -> Dict[str, object]:
        record: Dict[str, object] = {
            "name": str(self.name),
            "family": str(self.family),
            "train_error": int(self.train_error),
            "complexity": int(self.complexity),
            "program": self.program.to_record(),
            "metadata": _plain(self.metadata),
        }
        if include_grids:
            record["grids"] = [
                np.asarray(grid, dtype=np.int64).tolist() for grid in self.grids
            ]
            record["train_grids"] = [
                np.asarray(grid, dtype=np.int64).tolist()
                for grid in self.train_grids
            ]
        _canonical_json(record)
        return record


def _program(
    bindings: Sequence[Mapping[str, object]],
    effect: Mapping[str, object],
    *,
    quantifier: str = "THE",
) -> RoleBoundObjectProgram:
    return RoleBoundObjectProgram(
        operator=_COMPONENT_OPERATOR,
        bindings=tuple(bindings),
        effect=effect,
        quantifier=quantifier,
    )


def _enumerate_programs(limits: RoleBoundObjectLimits) -> Tuple[RoleBoundObjectProgram, ...]:
    programs: Dict[str, RoleBoundObjectProgram] = {}

    def add(program: RoleBoundObjectProgram) -> None:
        programs.setdefault(program.program_hash(), program)

    add(RoleBoundObjectProgram.unique_maximal_filled_rectangle_retention())
    add(RoleBoundObjectProgram.occluded_regular_primitive_completion())
    add(RoleBoundObjectProgram.marker_guide_ray_boundary_erasure())

    # This bounded grammar deliberately contains the reference pattern that
    # motivated it: unique minimum-area reference, unique nearest subject,
    # paint the subject with the dynamically rebound reference colour.
    # Only D4-invariant metrics are compiled.  The interpreter admits height
    # and width for explicit programs, but compiling them would make the
    # candidate-level D4 claim false under quarter turns.
    for metric in ("area", "bbox_area", "perimeter", "density"):
        for extreme in ("minimum", "maximum"):
            for relation in ("nearest", "farthest"):
                bindings = (
                    _component_binding(
                        "reference",
                        {"kind": "unique_extreme", "metric": metric, "order": extreme},
                    ),
                    _component_binding(
                        "subject",
                        {
                            "kind": "relation_extreme",
                            "relation": "manhattan",
                            "order": relation,
                            "relative_to": "reference",
                        },
                    ),
                )
                effects = (
                    {
                        "kind": "paint",
                        "role": "subject",
                        "target": "cells",
                        "color_role": "reference",
                    },
                    {
                        "kind": "paint",
                        "role": "subject",
                        "target": "exterior_band_1",
                        "color_role": "reference",
                    },
                    {"kind": "erase", "role": "subject", "target": "cells"},
                    {"kind": "retain", "role": "subject", "target": "cells"},
                    {
                        "kind": "fill_bbox",
                        "role": "subject",
                        "target": "bbox",
                        "color_role": "reference",
                    },
                )
                for effect in effects:
                    add(_program(bindings, effect))

    # Quantified forms exercise simultaneous, traversal-independent effects.
    all_binding = (_component_binding("subject", {"kind": "all"}),)
    for effect in (
        {"kind": "erase", "role": "subject", "target": "cells"},
        {"kind": "retain", "role": "subject", "target": "cells"},
        {
            "kind": "paint",
            "role": "subject",
            "target": "exterior_band_1",
            "color_role": "subject",
        },
        {
            "kind": "fill_bbox",
            "role": "subject",
            "target": "bbox",
            "color_role": "subject",
        },
    ):
        add(_program(all_binding, effect, quantifier="FOR_EACH"))

    ordered = tuple(
        sorted(programs.values(), key=lambda item: (item.complexity, item.semantic_key))
    )
    if len(ordered) > limits.maximum_programs:
        raise RoleBindingLimitError(
            f"program grammar has {len(ordered)} entries; "
            f"limit is {limits.maximum_programs}"
        )
    return ordered


def _example_hash(source: Array, target: Array) -> str:
    digest = hashlib.sha256()
    for grid in (source, target):
        value = np.asarray(grid, dtype=np.int16)
        digest.update(np.asarray(value.shape, dtype=np.int16).tobytes())
        digest.update(value.tobytes(order="C"))
    return digest.hexdigest()


def _behavior_hash(grids: Sequence[Array]) -> str:
    digest = hashlib.sha256()
    for grid in grids:
        value = np.asarray(grid, dtype=np.int16)
        digest.update(np.asarray(value.shape, dtype=np.int16).tobytes())
        digest.update(value.tobytes(order="C"))
    return digest.hexdigest()


def _validated_train(
    train: Sequence[Tuple[Array, Array]], limits: RoleBoundObjectLimits
) -> Tuple[Tuple[Array, Array], ...]:
    validated = []
    for source, target in train:
        source_grid = _validated_grid(source, limits)
        target_grid = _validated_grid(target, limits)
        if source_grid.shape != target_grid.shape:
            raise RoleBindingAbstention("role-bound effects preserve grid shape")
        validated.append((source_grid, target_grid))
    return tuple(validated)


def _exact_program_predictions(
    train: Sequence[Tuple[Array, Array]],
    programs: Sequence[RoleBoundObjectProgram],
    limits: RoleBoundObjectLimits,
) -> Dict[str, Tuple[RoleBoundObjectProgram, Tuple[Array, ...]]]:
    exact: Dict[str, Tuple[RoleBoundObjectProgram, Tuple[Array, ...]]] = {}
    for program in programs:
        predictions = []
        try:
            for source, target in train:
                prediction = program.apply(source, limits=limits)
                if not np.array_equal(prediction, target):
                    break
                predictions.append(prediction)
            else:
                exact[program.program_hash()] = (program, tuple(predictions))
        except RoleBindingError:
            continue
    return exact


def _discover_exact_program(
    train: Sequence[Tuple[Array, Array]],
    programs: Sequence[RoleBoundObjectProgram],
    limits: RoleBoundObjectLimits,
) -> Optional[Tuple[RoleBoundObjectProgram, Tuple[Array, ...]]]:
    """Select one canonical minimum-description exact program from a fold.

    The selection is run independently on each construction fold.  Requiring
    that fold-first result to match the full-data result makes LOO a genuine
    model-selection check: a simpler fold-only explanation can now reject a
    candidate instead of every full-data-exact program passing tautologically.
    """

    exact = _exact_program_predictions(train, programs, limits)
    if not exact:
        return None
    return min(
        exact.values(),
        key=lambda item: (item[0].complexity, item[0].semantic_key),
    )


def compile_role_bound_object_rewrites(
    train: Sequence[Tuple[Array, Array]],
    tests: Sequence[Array],
    *,
    limits: RoleBoundObjectLimits = DEFAULT_LIMITS,
) -> Tuple[RoleBoundObjectCandidate, ...]:
    """Compile only exact programs with genuine distinct-group LOO support."""

    if len(train) < 2:
        return ()
    if len(train) > limits.maximum_examples or len(tests) > limits.maximum_tests:
        raise RoleBindingLimitError("example budget exceeded")
    try:
        validated = _validated_train(train, limits)
        validated_tests = tuple(_validated_grid(test, limits) for test in tests)
    except RoleBindingAbstention:
        return ()

    groups: Dict[str, list[int]] = {}
    for index, (source, target) in enumerate(validated):
        if np.array_equal(source, target):
            continue
        groups.setdefault(_example_hash(source, target), []).append(index)
    if len(groups) < 2:
        return ()

    programs = _enumerate_programs(limits)
    full_exact = _exact_program_predictions(validated, programs, limits)
    discovered = (
        min(
            full_exact.values(),
            key=lambda item: (item[0].complexity, item[0].semantic_key),
        )
        if full_exact
        else None
    )
    if discovered is None:
        return ()
    program, train_predictions = discovered
    program_hash = program.program_hash()

    # Canonical fold-first selection prevents a simpler construction-only
    # explanation from passing LOO, but it must not hide a different exact
    # full-data explanation.  Execute every exact program independently on the
    # tests and require all concrete predictions to agree before any candidate
    # is exposed to the promotion lane.
    exact_test_behaviors: Dict[str, list[str]] = {}
    selected_test_predictions: Optional[Tuple[Array, ...]] = None
    for exact_hash, (exact_program, _) in sorted(full_exact.items()):
        try:
            predictions = tuple(
                exact_program.apply(test, limits=limits)
                for test in validated_tests
            )
        except RoleBindingError:
            continue
        behavior = _behavior_hash(predictions)
        exact_test_behaviors.setdefault(behavior, []).append(exact_hash)
        if exact_hash == program_hash:
            selected_test_predictions = predictions
    if len(exact_test_behaviors) > limits.maximum_candidates:
        raise RoleBindingLimitError(
            "exact test behavior-class budget exceeded; compiler abstains"
        )
    if len(exact_test_behaviors) > 1:
        raise RoleBindingAmbiguityError(
            "full-data-exact role programs predict divergent test behaviors"
        )
    if selected_test_predictions is None:
        return ()
    accepted: list[RoleBoundObjectCandidate] = []
    seen_behaviors: set[str] = set()
    for program_hash, program, train_predictions in (
        (program_hash, program, train_predictions),
    ):
        fixed = program.operator in _FIXED_OPERATORS
        relation_candidate_count = 0
        foreach_cardinality = 0
        minimum_selector_support = 0
        if not fixed:
            support_records: list[Dict[str, int]] = []
            try:
                for indices in groups.values():
                    support_records.append(
                        _component_program_support(
                            program, validated[indices[0]][0], limits
                        )
                    )
            except RoleBindingError:
                continue
            relation_candidate_count = max(
                record["relation_candidate_count"] for record in support_records
            )
            foreach_cardinality = max(
                record["foreach_cardinality"] for record in support_records
            )
            minimum_selector_support = min(
                record["scene_component_count"] for record in support_records
            )
            has_relation = any(
                binding["selector"].get("kind") == "relation_extreme"
                for binding in program.bindings
            )
            if has_relation and relation_candidate_count < 2:
                continue
            if program.quantifier == "FOR_EACH" and foreach_cardinality < 2:
                continue
        loo_exact = 0
        loo_program_hashes: list[str] = []
        for indices in groups.values():
            excluded = set(indices)
            construction = tuple(
                pair for index, pair in enumerate(validated) if index not in excluded
            )
            if not construction:
                break
            # Fold-first discovery selects a canonical program without the
            # held group's targets or the full-data program/hash as input.
            rediscovered = _discover_exact_program(construction, programs, limits)
            if rediscovered is None:
                break
            fold_program = rediscovered[0]
            fold_hash = fold_program.program_hash()
            loo_program_hashes.append(fold_hash)
            if fold_hash != program_hash:
                break
            try:
                if not all(
                    np.array_equal(fold_program.apply(validated[index][0], limits=limits),
                                   validated[index][1])
                    for index in indices
                ):
                    break
            except RoleBindingError:
                break
            loo_exact += 1
        if loo_exact != len(groups):
            continue
        test_predictions = selected_test_predictions
        behavior_hash = _behavior_hash((*train_predictions, *test_predictions))
        if behavior_hash in seen_behaviors:
            continue
        seen_behaviors.add(behavior_hash)
        metadata: Dict[str, object] = {
            "schema": "komorebi.arc.role-bound-object-candidate.v1",
            "program": program.to_record(),
            "program_hash": program_hash,
            "semantic_key": program.semantic_key,
            "role_binding": "input_local_strict_rebinding",
            "background_binding": program.background_policy,
            "component_domain": "4_connected_monochrome",
            "exact_demonstration_contract": True,
            "test_target_isolation": True,
            "test_input_grounded": True,
            "task_identifier_free": True,
            "literal_color_free_program": True,
            "literal_coordinate_free_program": True,
            "raw_grid_free_program": True,
            "palette_equivariant": True,
            "d4_equivariant": True,
            "atomic_collision_abstention": True,
            "witness_protocol": "leave_one_distinct_nonidentity_group_out_rediscovery",
            "discovery_protocol": "canonical_minimum_description_exact_program",
            "full_discovery_program_hash": program_hash,
            "full_exact_program_count": int(len(full_exact)),
            "agreeing_exact_program_hashes": sorted(
                next(iter(exact_test_behaviors.values()))
            ),
            "exact_test_behavior_count": int(len(exact_test_behaviors)),
            "distinct_witness_groups": int(len(groups)),
            "loo_exact_count": int(loo_exact),
            "loo_total_count": int(len(groups)),
            "loo_program_hashes": list(loo_program_hashes),
            "negative_counterfactual_support": bool(
                not fixed
                and (
                    relation_candidate_count >= 2
                    or foreach_cardinality >= 2
                )
            ),
            "negative_counterfactual_scope": "generic_component_programs",
            "maximum_relation_candidate_count": int(relation_candidate_count),
            "maximum_foreach_cardinality": int(foreach_cardinality),
            "minimum_selector_support": int(minimum_selector_support),
            "promotion_evidence": (
                "exact_distinct_demo_replay+LOO_rediscovery+strict_test_binding"
            ),
            "empirical_promotion_eligible": bool(fixed),
            "external_gain_loss_audit": False,
            "implementation_fingerprint": role_bound_implementation_fingerprint(),
            "bounded_program_count": int(len(programs)),
            "limits": limits.to_record(),
        }
        accepted.append(
            RoleBoundObjectCandidate(
                name=f"role_bound:{program.operator}:{program_hash[:12]}",
                program=program,
                grids=test_predictions,
                train_grids=train_predictions,
                complexity=program.complexity,
                metadata=metadata,
            )
        )
        if len(accepted) > limits.maximum_candidates:
            raise RoleBindingLimitError(
                "accepted exact behavior-class budget exceeded; "
                "compiler resource-abstains instead of truncating disagreement"
            )
    return tuple(accepted)


role_bound_object_rewrite_candidates = compile_role_bound_object_rewrites


__all__ = [
    "DEFAULT_LIMITS",
    "FAMILY",
    "RoleBindingAbstention",
    "RoleBindingAmbiguityError",
    "RoleBindingError",
    "RoleBindingLimitError",
    "RoleBoundObjectCandidate",
    "RoleBoundObjectLimits",
    "RoleBoundObjectProgram",
    "compile_role_bound_object_rewrites",
    "execute_role_bound_object_program",
    "role_bound_object_rewrite_candidates",
    "role_bound_implementation_fingerprint",
]
