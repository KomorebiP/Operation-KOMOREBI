"""Finite task-local semantic tool synthesis for PR-LASM Block 10.

This module is deliberately split into two phases:

``propose_tool_programs``
    may inspect labelled *training* demonstrations and returns immutable,
    target-free executable programs;

``execute_tool``
    receives only one such program and one input grid.  It cannot inspect a
    demonstration target, a test label, a task identifier, or a corpus row.

The language is a small selector x relation x geometry x effect x closure
product.  Not every syntactic product is meaningful, so the validator exposes
only a finite compatibility table.  The proposer binds holes from conservative
properties of demonstrated deltas, exactly replays every demonstration, and
then behavior-quotients the surviving syntax before any test input is run.

Exact grids remain authoritative.  Objects and ambient faces are temporary
semantic views used to construct an edit mask; the result is always rendered
back to a validated ARC grid.
"""
from __future__ import annotations

from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from functools import lru_cache
from numbers import Integral
from types import MappingProxyType
from typing import Any, Iterable, Iterator, Mapping, Sequence

import numpy as np

from komorebi_lasm_composition.model import (
    Grid,
    LeafInvocation,
    canonical_parameters,
    canonical_value,
    decode_canonical_parameters,
    sha256_record,
    validate_grid,
)
from komorebi_lasm_composition.task import TrainingTask, sanitize_training_task


SCHEMA_VERSION = 1
ARC_COLORS = tuple(range(10))
ORTHOGONAL = ((-1, 0), (0, -1), (0, 1), (1, 0))
DIAGONAL = ((-1, -1), (-1, 1), (1, -1), (1, 1))
ALL_DIRECTIONS = ORTHOGONAL + DIAGONAL

SELECTORS = (
    "all_components",
    "singleton_components",
    "non_singleton_components",
    "smallest_components",
    "largest_components",
    "with_holes",
    "without_holes",
    "border_touching",
    "interior_components",
    "unique_shape_components",
    "repeated_shape_components",
    "shape_matched_components",
    "color_components",
    "all_foreground_cells",
)
RELATIONS = (
    "none",
    "aligned_pairs",
    "same_color_aligned_pairs",
    "same_shape_aligned_pairs",
    "diagonal_pairs",
    "same_shape_diagonal_pairs",
)
GEOMETRIES = (
    "selected_support",
    "ambient_holes",
    "bounding_box_fill",
    "bounding_box_outline",
    "between_extents",
    "diagonal_between_extents",
    "pair_midpoint_stamp",
    "rays_to_border",
    "outward_diagonal_rays",
    "missing_corner_diagonal_rays",
    "translate",
    "translation_orbit",
    "local_stamp",
    "checkerboard_from_rows",
    "control_directed_copy",
    "marker_quadrant_render",
    "project_to_container_boundary",
    "shape_color_transfer",
    "corner_legend_pair_swap",
)
EFFECTS = (
    "paint_constant",
    "paint_source_color",
    "recolor_selected",
    "erase_selected",
)
CLOSURES = ("once", "until_stable")

_VALID_SELECTOR = frozenset(SELECTORS)
_VALID_RELATION = frozenset(RELATIONS)
_VALID_GEOMETRY = frozenset(GEOMETRIES)
_VALID_EFFECT = frozenset(EFFECTS)
_VALID_CLOSURE = frozenset(CLOSURES)


def _integer(value: object, name: str, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise TypeError(f"{name} must be an integer")
    result = int(value)
    if not minimum <= result <= maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}")
    return result


def _boolean(value: object, name: str) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"{name} must be Boolean")
    return value


def _choice(value: object, name: str, choices: Iterable[str]) -> str:
    allowed = tuple(choices)
    if not isinstance(value, str) or value not in allowed:
        raise ValueError(f"{name} must be one of {allowed!r}")
    return value


def _exact_keys(parameters: Mapping[str, Any], required: Iterable[str]) -> None:
    if not isinstance(parameters, Mapping):
        raise TypeError("tool parameters must be a mapping")
    expected = frozenset(required)
    actual = frozenset(parameters)
    if actual != expected:
        raise ValueError(
            "tool parameter keys differ from schema; "
            f"missing={sorted(expected - actual)}, extra={sorted(actual - expected)}"
        )


def _deep_freeze(value: Any) -> Any:
    if isinstance(value, dict):
        return MappingProxyType({key: _deep_freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_deep_freeze(item) for item in value)
    return value


def _validate_role(value: object, name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a color-role string")
    if value in {
        "background",
        "zero",
        "corner",
        "rarest_foreground",
        "most_foreground",
        "unique_foreground",
        "source",
    }:
        return value
    if value.startswith("literal:"):
        suffix = value.split(":", 1)[1]
        if suffix.isdigit() and 0 <= int(suffix) <= 9:
            return value
    raise ValueError(f"unsupported {name} {value!r}")


def _validate_offset(value: object, name: str) -> tuple[int, int]:
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise TypeError(f"{name} must be a two-element sequence")
    return (
        _integer(value[0], f"{name}[0]", -29, 29),
        _integer(value[1], f"{name}[1]", -29, 29),
    )


def _validate_parameters(
    selector: str,
    relation: str,
    geometry: str,
    effect: str,
    closure: str,
    parameters: Mapping[str, Any],
) -> None:
    if selector not in _VALID_SELECTOR:
        raise ValueError(f"unknown selector {selector!r}")
    if relation not in _VALID_RELATION:
        raise ValueError(f"unknown relation {relation!r}")
    if geometry not in _VALID_GEOMETRY:
        raise ValueError(f"unknown geometry {geometry!r}")
    if effect not in _VALID_EFFECT:
        raise ValueError(f"unknown effect {effect!r}")
    if closure not in _VALID_CLOSURE:
        raise ValueError(f"unknown closure {closure!r}")

    required = {
        "background_role",
        "connectivity",
        "monochrome_components",
        "selector_color_role",
        "paint_role",
        "background_only",
        "include_sources",
        "directions",
        "offset",
        "stamp_offsets",
        "max_steps",
        "shape_mode",
    }
    _exact_keys(parameters, required)
    _validate_role(parameters["background_role"], "background_role")
    connectivity = _integer(parameters["connectivity"], "connectivity", 4, 8)
    if connectivity not in {4, 8}:
        raise ValueError("connectivity must be 4 or 8")
    _boolean(parameters["monochrome_components"], "monochrome_components")
    _validate_role(parameters["selector_color_role"], "selector_color_role")
    _validate_role(parameters["paint_role"], "paint_role")
    _boolean(parameters["background_only"], "background_only")
    _boolean(parameters["include_sources"], "include_sources")
    directions = parameters["directions"]
    if not isinstance(directions, (list, tuple)) or len(directions) > 8:
        raise TypeError("directions must be a sequence of at most eight offsets")
    normalized_directions = tuple(_validate_offset(item, "direction") for item in directions)
    if any(offset not in ALL_DIRECTIONS for offset in normalized_directions):
        raise ValueError("directions must use unit compass offsets")
    if len(set(normalized_directions)) != len(normalized_directions):
        raise ValueError("directions must be unique")
    _validate_offset(parameters["offset"], "offset")
    stamp_offsets = parameters["stamp_offsets"]
    if not isinstance(stamp_offsets, (list, tuple)) or len(stamp_offsets) > 25:
        raise TypeError("stamp_offsets must be a sequence of at most 25 offsets")
    normalized_stamp = tuple(_validate_offset(item, "stamp offset") for item in stamp_offsets)
    if any(abs(dy) > 3 or abs(dx) > 3 for dy, dx in normalized_stamp):
        raise ValueError("stamp offsets must remain in the radius-three window")
    if len(set(normalized_stamp)) != len(normalized_stamp):
        raise ValueError("stamp offsets must be unique")
    _integer(parameters["max_steps"], "max_steps", 1, 30)
    _choice(parameters["shape_mode"], "shape_mode", ("exact", "d4"))

    # Compatibility is part of the typed language, not a proposal heuristic.
    pair_geometry = geometry in {
        "between_extents", "diagonal_between_extents", "pair_midpoint_stamp"
    }
    if pair_geometry != (relation != "none"):
        raise ValueError("between-extents geometry requires exactly one pair relation")
    if geometry in {
        "ambient_holes", "bounding_box_fill", "bounding_box_outline",
        "checkerboard_from_rows", "control_directed_copy",
        "marker_quadrant_render", "project_to_container_boundary",
        "outward_diagonal_rays", "missing_corner_diagonal_rays",
        "corner_legend_pair_swap",
    } and relation != "none":
        raise ValueError(f"{geometry} does not accept pair relations")
    if geometry in {"rays_to_border", "translate", "translation_orbit", "local_stamp"} and relation != "none":
        raise ValueError(f"{geometry} does not accept pair relations")
    if geometry == "ambient_holes" and selector not in {
        "all_components", "with_holes", "color_components"
    }:
        raise ValueError("ambient-hole geometry needs an object-bearing selector")
    if geometry == "rays_to_border" and not normalized_directions:
        raise ValueError("ray geometry needs at least one direction")
    if geometry in {"translate", "translation_orbit"} and parameters["offset"] == [0, 0]:
        raise ValueError("translation offset must be nonzero")
    if geometry in {"local_stamp", "pair_midpoint_stamp"} and not normalized_stamp:
        raise ValueError("local stamp needs at least one offset")
    if closure == "until_stable" and geometry not in {
        "translation_orbit", "rays_to_border", "bounding_box_fill", "ambient_holes"
    }:
        raise ValueError("this geometry has no finite fixed-point semantics")
    if effect in {"recolor_selected", "erase_selected"} and geometry != "selected_support":
        raise ValueError(f"{effect} requires selected-support geometry")
    if geometry in {
        "checkerboard_from_rows", "control_directed_copy",
        "marker_quadrant_render", "project_to_container_boundary",
        "shape_color_transfer", "corner_legend_pair_swap",
    } and effect != "paint_source_color":
        raise ValueError(f"{geometry} has typed direct-color output semantics")
    if effect == "paint_source_color" and geometry == "rays_to_border" and selector == "all_foreground_cells":
        # Each selected cell has a well-defined source color, so this is valid.
        pass


@dataclass(frozen=True, slots=True)
class ToolProgram:
    """One immutable executable task-local semantic tool."""

    selector: str
    relation: str
    geometry: str
    effect: str
    closure: str
    parameters_json: str
    cost: int = 5
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        if isinstance(self.cost, bool) or not isinstance(self.cost, Integral) or not 1 <= int(self.cost) <= 64:
            raise ValueError("cost must be an integer from 1 through 64")
        if self.schema_version != SCHEMA_VERSION or isinstance(self.schema_version, bool):
            raise ValueError(f"schema_version must equal {SCHEMA_VERSION}")
        parameters = decode_canonical_parameters(self.parameters_json)
        _validate_parameters(
            self.selector,
            self.relation,
            self.geometry,
            self.effect,
            self.closure,
            parameters,
        )

    @classmethod
    def from_parameters(
        cls,
        *,
        selector: str,
        relation: str,
        geometry: str,
        effect: str,
        closure: str,
        parameters: Mapping[str, Any],
        cost: int = 5,
    ) -> "ToolProgram":
        return cls(
            selector=selector,
            relation=relation,
            geometry=geometry,
            effect=effect,
            closure=closure,
            parameters_json=canonical_parameters(parameters),
            cost=cost,
        )

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "ToolProgram":
        if not isinstance(record, Mapping):
            raise TypeError("tool record must be a mapping")
        required = {"selector", "relation", "geometry", "effect", "closure", "cost"}
        if not required.issubset(record):
            raise ValueError(f"tool record is missing {sorted(required - set(record))}")
        raw_parameters = record.get("parameters")
        raw_json = record.get("parameters_json")
        if raw_parameters is None and raw_json is None:
            raise ValueError("tool record needs parameters or parameters_json")
        if raw_parameters is not None and not isinstance(raw_parameters, Mapping):
            raise TypeError("tool record parameters must be a mapping")
        if raw_json is None:
            parameters_json = canonical_parameters(raw_parameters)  # type: ignore[arg-type]
        elif not isinstance(raw_json, str):
            raise TypeError("parameters_json must be a string")
        else:
            parameters_json = raw_json
        if raw_parameters is not None and canonical_parameters(raw_parameters) != parameters_json:
            raise ValueError("parameters and parameters_json disagree")
        value = cls(
            selector=str(record["selector"]),
            relation=str(record["relation"]),
            geometry=str(record["geometry"]),
            effect=str(record["effect"]),
            closure=str(record["closure"]),
            parameters_json=parameters_json,
            cost=int(record["cost"]),
            schema_version=int(record.get("schema_version", SCHEMA_VERSION)),
        )
        claimed = record.get("tool_id")
        if claimed is not None and claimed != value.tool_id:
            raise ValueError("tool_id does not match tool semantics")
        return value

    @property
    def parameters(self) -> Mapping[str, Any]:
        value = decode_canonical_parameters(self.parameters_json)
        return _deep_freeze(value)

    @property
    def semantic_record(self) -> dict[str, Any]:
        return {
            "schema": "komorebi.lasm_action.tool_semantics",
            "schema_version": self.schema_version,
            "input_type": "grid",
            "output_type": "grid",
            "selector": self.selector,
            "relation": self.relation,
            "geometry": self.geometry,
            "effect": self.effect,
            "closure": self.closure,
            "parameters": decode_canonical_parameters(self.parameters_json),
        }

    @property
    def tool_id(self) -> str:
        return sha256_record(self.semantic_record)

    @property
    def grammar_word(self) -> tuple[str, str, str, str, str]:
        return self.selector, self.relation, self.geometry, self.effect, self.closure

    def to_record(self) -> dict[str, Any]:
        record = {
            **self.semantic_record,
            "parameters_json": self.parameters_json,
            "cost": int(self.cost),
            "tool_id": self.tool_id,
            "origin": "training_demonstration_synthesis",
        }
        record["content_hash"] = sha256_record(record)
        return record


@dataclass(frozen=True, slots=True)
class ToolSynthesisLimits:
    max_programs: int = 4_096
    max_executions: int = 16_384
    max_candidates: int = 64
    max_objects: int = 128
    max_cells: int = 900
    max_stamp_offsets: int = 16
    max_translation_vectors: int = 64
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        for name in (
            "max_programs",
            "max_executions",
            "max_candidates",
            "max_objects",
            "max_cells",
            "max_stamp_offsets",
            "max_translation_vectors",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, Integral) or int(value) <= 0:
                raise ValueError(f"{name} must be a positive integer")
        if self.max_cells > 900:
            raise ValueError("max_cells cannot exceed the ARC grid limit")
        if self.max_objects > 900:
            raise ValueError("max_objects cannot exceed the ARC cell limit")
        if self.max_stamp_offsets > 25:
            raise ValueError("max_stamp_offsets cannot exceed the language limit")
        if self.schema_version != SCHEMA_VERSION or isinstance(self.schema_version, bool):
            raise ValueError(f"schema_version must equal {SCHEMA_VERSION}")

    def to_record(self) -> dict[str, Any]:
        return {
            "schema": "komorebi.lasm_action.tool_synthesis_limits",
            "schema_version": self.schema_version,
            "max_programs": int(self.max_programs),
            "max_executions": int(self.max_executions),
            "max_candidates": int(self.max_candidates),
            "max_objects": int(self.max_objects),
            "max_cells": int(self.max_cells),
            "max_stamp_offsets": int(self.max_stamp_offsets),
            "max_translation_vectors": int(self.max_translation_vectors),
        }


@dataclass(frozen=True, slots=True)
class ToolCandidate:
    program: ToolProgram
    training_outputs: tuple[Grid, ...]
    test_outputs: tuple[Grid, ...]
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self.program, ToolProgram):
            raise TypeError("program must be a ToolProgram")
        object.__setattr__(self, "training_outputs", tuple(validate_grid(grid) for grid in self.training_outputs))
        object.__setattr__(self, "test_outputs", tuple(validate_grid(grid) for grid in self.test_outputs))
        if not self.training_outputs:
            raise ValueError("candidate needs demonstration outputs")
        if not self.test_outputs:
            raise ValueError("candidate needs at least one sanitized test behavior")
        if self.schema_version != SCHEMA_VERSION or isinstance(self.schema_version, bool):
            raise ValueError(f"schema_version must equal {SCHEMA_VERSION}")

    @property
    def behavior_hash(self) -> str:
        return sha256_record({
            "training_outputs": self.training_outputs,
            "test_outputs": self.test_outputs,
        })

    def to_record(self) -> dict[str, Any]:
        record = {
            "schema": "komorebi.lasm_action.tool_candidate",
            "schema_version": self.schema_version,
            "program": self.program.to_record(),
            "training_outputs": canonical_value(self.training_outputs),
            "test_outputs": canonical_value(self.test_outputs),
            "behavior_hash": self.behavior_hash,
        }
        record["content_hash"] = sha256_record(record)
        return record


@dataclass(frozen=True, slots=True)
class ToolSynthesisResult:
    candidates: tuple[ToolCandidate, ...]
    programs_considered: int
    executions_performed: int
    exact_programs: int
    behavior_classes: int
    limit_reached: str = ""
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(self, "candidates", tuple(self.candidates))
        if not all(isinstance(item, ToolCandidate) for item in self.candidates):
            raise TypeError("candidates must contain ToolCandidate records")
        for name in ("programs_considered", "executions_performed", "exact_programs", "behavior_classes"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, Integral) or int(value) < 0:
                raise ValueError(f"{name} must be a nonnegative integer")
        if self.behavior_classes != len(self.candidates):
            raise ValueError("behavior_classes must equal the quotient candidate count")
        if self.schema_version != SCHEMA_VERSION or isinstance(self.schema_version, bool):
            raise ValueError(f"schema_version must equal {SCHEMA_VERSION}")

    @property
    def unique_test_behavior(self) -> bool:
        # An apparently unique prefix of a truncated search is not evidence of
        # semantic uniqueness.  Every finite enumeration boundary fails closed.
        return (
            not self.limit_reached
            and bool(self.candidates)
            and len({sha256_record(item.test_outputs) for item in self.candidates}) == 1
        )

    @property
    def selected_candidate(self) -> ToolCandidate | None:
        if not self.unique_test_behavior:
            return None
        return min(
            self.candidates,
            key=lambda item: (item.program.cost, item.program.tool_id),
        )

    def to_record(self) -> dict[str, Any]:
        record = {
            "schema": "komorebi.lasm_action.tool_synthesis_result",
            "schema_version": self.schema_version,
            "candidates": [item.to_record() for item in self.candidates],
            "programs_considered": int(self.programs_considered),
            "executions_performed": int(self.executions_performed),
            "exact_programs": int(self.exact_programs),
            "behavior_classes": int(self.behavior_classes),
            "unique_test_behavior": self.unique_test_behavior,
            "selected_tool_id": self.selected_candidate.program.tool_id if self.selected_candidate else "",
            "limit_reached": self.limit_reached,
        }
        record["content_hash"] = sha256_record(record)
        return record


@dataclass(frozen=True, slots=True)
class RouteCompletionCertificate:
    """Reproducible integrity record for one untruncated finite subgrammar.

    The hashes detect accidental drift; they are neither authentication nor an
    independent mathematical proof of completeness.
    """

    route: str
    program_space_hash: str
    grammar_contract_hash: str
    training_hashes: tuple[str, ...]
    programs_enumerated: int
    complete: bool = True
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.route != "scene_native_relational":
            raise ValueError("unknown complete tool route")
        for name in ("program_space_hash", "grammar_contract_hash"):
            digest = getattr(self, name)
            if (
                not isinstance(digest, str)
                or len(digest) != 64
                or digest != digest.lower()
                or any(character not in "0123456789abcdef" for character in digest)
            ):
                raise ValueError(f"{name} must be a lowercase SHA-256 digest")
        object.__setattr__(self, "training_hashes", tuple(self.training_hashes))
        if not self.training_hashes:
            raise ValueError("training_hashes cannot be empty")
        if any(
            not isinstance(digest, str)
            or len(digest) != 64
            or digest != digest.lower()
            or any(character not in "0123456789abcdef" for character in digest)
            for digest in self.training_hashes
        ):
            raise ValueError("training_hashes must contain lowercase SHA-256 digests")
        if isinstance(self.programs_enumerated, bool) or not isinstance(self.programs_enumerated, Integral) or self.programs_enumerated < 0:
            raise ValueError("programs_enumerated must be nonnegative")
        if self.complete is not True:
            raise ValueError("a completion certificate must be complete")
        if self.schema_version != SCHEMA_VERSION or isinstance(self.schema_version, bool):
            raise ValueError(f"schema_version must equal {SCHEMA_VERSION}")

    def to_record(self) -> dict[str, Any]:
        record = {
            "schema": "komorebi.lasm_action.route_completion_certificate",
            "schema_version": self.schema_version,
            "route": self.route,
            "program_space_hash": self.program_space_hash,
            "grammar_contract_hash": self.grammar_contract_hash,
            "training_hashes": list(self.training_hashes),
            "programs_enumerated": int(self.programs_enumerated),
            "complete": True,
        }
        record["certificate_hash"] = sha256_record(record)
        return record


@dataclass(frozen=True, slots=True)
class CompleteToolRouteResult:
    certificate: RouteCompletionCertificate
    candidates: tuple[ToolCandidate, ...]
    executions_performed: int
    exact_programs: int
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self.certificate, RouteCompletionCertificate):
            raise TypeError("certificate must be a RouteCompletionCertificate")
        object.__setattr__(self, "candidates", tuple(self.candidates))
        if not all(isinstance(item, ToolCandidate) for item in self.candidates):
            raise TypeError("candidates must contain ToolCandidate records")
        for name in ("executions_performed", "exact_programs"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, Integral) or value < 0:
                raise ValueError(f"{name} must be nonnegative")
        if self.schema_version != SCHEMA_VERSION or isinstance(self.schema_version, bool):
            raise ValueError(f"schema_version must equal {SCHEMA_VERSION}")

    @property
    def complete(self) -> bool:
        return self.certificate.complete

    @property
    def behavior_classes(self) -> int:
        return len(self.candidates)

    @property
    def unique_test_behavior(self) -> bool:
        return bool(self.candidates) and len({sha256_record(item.test_outputs) for item in self.candidates}) == 1

    @property
    def selected_candidate(self) -> ToolCandidate | None:
        if not self.unique_test_behavior:
            return None
        return min(self.candidates, key=lambda item: (item.program.cost, item.program.tool_id))

    def to_record(self) -> dict[str, Any]:
        record = {
            "schema": "komorebi.lasm_action.complete_tool_route_result",
            "schema_version": self.schema_version,
            "certificate": self.certificate.to_record(),
            "candidates": [item.to_record() for item in self.candidates],
            "executions_performed": int(self.executions_performed),
            "exact_programs": int(self.exact_programs),
            "behavior_classes": self.behavior_classes,
            "unique_test_behavior": self.unique_test_behavior,
            "selected_tool_id": self.selected_candidate.program.tool_id if self.selected_candidate else "",
            "complete": True,
        }
        record["content_hash"] = sha256_record(record)
        return record


@dataclass(frozen=True, slots=True)
class _Object:
    color: int
    cells: frozenset[tuple[int, int]]
    top: int
    left: int
    bottom: int
    right: int
    holes: frozenset[tuple[int, int]]

    @property
    def size(self) -> int:
        return len(self.cells)

    @property
    def height(self) -> int:
        return self.bottom - self.top + 1

    @property
    def width(self) -> int:
        return self.right - self.left + 1

    @property
    def center(self) -> tuple[int, int]:
        # Integer center is deliberately restricted to the bounding-box cell
        # nearest the upper-left.  Pair geometries use extents, not this value.
        return ((self.top + self.bottom) // 2, (self.left + self.right) // 2)

    @property
    def shape_signature(self) -> tuple[tuple[int, int], ...]:
        return tuple(sorted((row - self.top, column - self.left) for row, column in self.cells))

    @property
    def touches_border(self) -> bool:
        # The final grid shape is supplied by the selector helper.
        raise AttributeError("border membership requires the scene dimensions")


def _as_grid(value: Any) -> Grid:
    return validate_grid(value)


def _array(value: Grid) -> np.ndarray:
    return np.asarray(value, dtype=np.int16)


def _resolve_role(array: np.ndarray, role: str, *, background: int | None = None, source: int | None = None) -> int:
    _validate_role(role, "color role")
    if role.startswith("literal:"):
        return int(role.split(":", 1)[1])
    if role == "source":
        if source is None:
            raise ValueError("source color role is unavailable")
        return int(source)
    if role == "zero":
        return 0
    counts = Counter(int(item) for item in array.ravel())
    if role == "corner":
        corners = Counter((int(array[0, 0]), int(array[0, -1]), int(array[-1, 0]), int(array[-1, -1])))
        maximum = max(corners.values())
        winners = sorted(color for color, count in corners.items() if count == maximum)
        if len(winners) != 1:
            raise ValueError("corner color is ambiguous")
        return winners[0]
    if role == "background":
        if background is not None:
            return int(background)
        maximum = max(counts.values())
        winners = sorted(color for color, count in counts.items() if count == maximum)
        if len(winners) != 1:
            raise ValueError("background color is ambiguous")
        return winners[0]
    resolved_background = int(background) if background is not None else _resolve_role(array, "background")
    foreground = {color: count for color, count in counts.items() if color != resolved_background}
    if not foreground:
        raise ValueError("foreground role is unavailable")
    if role == "unique_foreground":
        if len(foreground) != 1:
            raise ValueError("unique foreground color is ambiguous")
        return next(iter(foreground))
    wanted = min(foreground.values()) if role == "rarest_foreground" else max(foreground.values())
    winners = sorted(color for color, count in foreground.items() if count == wanted)
    if len(winners) != 1:
        raise ValueError(f"{role} color is ambiguous")
    return winners[0]


def _directions(connectivity: int) -> tuple[tuple[int, int], ...]:
    return ORTHOGONAL if connectivity == 4 else ALL_DIRECTIONS


def _components(mask: np.ndarray, connectivity: int) -> tuple[frozenset[tuple[int, int]], ...]:
    height, width = mask.shape
    seen = np.zeros(mask.shape, dtype=bool)
    answer: list[frozenset[tuple[int, int]]] = []
    for row in range(height):
        for column in range(width):
            if seen[row, column] or not bool(mask[row, column]):
                continue
            queue: deque[tuple[int, int]] = deque(((row, column),))
            seen[row, column] = True
            cells: set[tuple[int, int]] = set()
            while queue:
                y, x = queue.popleft()
                cells.add((y, x))
                for dy, dx in _directions(connectivity):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < height and 0 <= nx < width and bool(mask[ny, nx]) and not seen[ny, nx]:
                        seen[ny, nx] = True
                        queue.append((ny, nx))
            answer.append(frozenset(cells))
    return tuple(answer)


def _enclosed_cells(cells: frozenset[tuple[int, int]]) -> frozenset[tuple[int, int]]:
    if not cells:
        return frozenset()
    top = min(row for row, _ in cells)
    bottom = max(row for row, _ in cells)
    left = min(column for _, column in cells)
    right = max(column for _, column in cells)
    if bottom - top < 2 or right - left < 2:
        return frozenset()
    local = np.zeros((bottom - top + 1, right - left + 1), dtype=bool)
    for row, column in cells:
        local[row - top, column - left] = True
    empty = ~local
    exterior: set[tuple[int, int]] = set()
    queue: deque[tuple[int, int]] = deque()
    height, width = local.shape
    for row in range(height):
        for column in (0, width - 1):
            if empty[row, column] and (row, column) not in exterior:
                exterior.add((row, column)); queue.append((row, column))
    for column in range(width):
        for row in (0, height - 1):
            if empty[row, column] and (row, column) not in exterior:
                exterior.add((row, column)); queue.append((row, column))
    while queue:
        row, column = queue.popleft()
        for dy, dx in ORTHOGONAL:
            ny, nx = row + dy, column + dx
            if 0 <= ny < height and 0 <= nx < width and empty[ny, nx] and (ny, nx) not in exterior:
                exterior.add((ny, nx)); queue.append((ny, nx))
    return frozenset(
        (row + top, column + left)
        for row in range(height)
        for column in range(width)
        if empty[row, column] and (row, column) not in exterior
    )


def _objects(array: np.ndarray, background: int, connectivity: int, monochrome: bool, *, max_objects: int = 128) -> tuple[_Object, ...]:
    groups: list[tuple[int, frozenset[tuple[int, int]]]] = []
    if monochrome:
        for color in sorted(set(int(item) for item in array.ravel()) - {background}):
            for cells in _components(array == color, connectivity):
                groups.append((color, cells))
    else:
        for cells in _components(array != background, connectivity):
            colors = Counter(int(array[row, column]) for row, column in cells)
            maximum = max(colors.values())
            winners = [candidate for candidate, count in colors.items() if count == maximum]
            if len(winners) != 1:
                raise ValueError("mixed-color component has no unique dominant color")
            color = winners[0]
            groups.append((color, cells))
    if len(groups) > max_objects:
        raise ValueError("scene exceeds the finite object budget")
    answer: list[_Object] = []
    for color, cells in groups:
        rows = [row for row, _ in cells]
        columns = [column for _, column in cells]
        answer.append(_Object(
            color=color,
            cells=cells,
            top=min(rows), left=min(columns), bottom=max(rows), right=max(columns),
            holes=_enclosed_cells(cells),
        ))
    return tuple(sorted(answer, key=lambda item: (item.top, item.left, item.bottom, item.right, item.color, item.shape_signature)))


@lru_cache(maxsize=4_096)
def _objects_cached(
    grid: Grid,
    background: int,
    connectivity: int,
    monochrome: bool,
    max_objects: int = 128,
) -> tuple[_Object, ...]:
    """Memoize immutable scene decompositions during bounded synthesis."""
    return _objects(
        _array(grid), background, connectivity, monochrome,
        max_objects=max_objects,
    )


def _shape_key(item: _Object, mode: str) -> tuple[tuple[int, int], ...]:
    """Return an exact or D4-canonical object support signature."""
    if mode == "exact":
        return item.shape_signature
    if mode != "d4":
        raise ValueError(f"unknown shape mode {mode!r}")
    points = item.shape_signature
    variants: list[tuple[tuple[int, int], ...]] = []
    for swap in (False, True):
        for sign_row in (-1, 1):
            for sign_column in (-1, 1):
                transformed = []
                for row, column in points:
                    y, x = (column, row) if swap else (row, column)
                    transformed.append((sign_row * y, sign_column * x))
                minimum_row = min(row for row, _ in transformed)
                minimum_column = min(column for _, column in transformed)
                variants.append(tuple(sorted(
                    (row - minimum_row, column - minimum_column)
                    for row, column in transformed
                )))
    return min(variants)


def _select(
    objects: Sequence[_Object],
    selector: str,
    array: np.ndarray,
    background: int,
    selector_color_role: str,
    shape_mode: str,
) -> tuple[_Object, ...]:
    if selector in {"all_components", "all_foreground_cells"}:
        return tuple(objects)
    if selector == "singleton_components":
        return tuple(item for item in objects if item.size == 1)
    if selector == "non_singleton_components":
        return tuple(item for item in objects if item.size > 1)
    if selector == "smallest_components":
        size = min((item.size for item in objects), default=-1)
        return tuple(item for item in objects if item.size == size)
    if selector == "largest_components":
        size = max((item.size for item in objects), default=-1)
        return tuple(item for item in objects if item.size == size)
    if selector == "with_holes":
        return tuple(item for item in objects if item.holes)
    if selector == "without_holes":
        return tuple(item for item in objects if not item.holes)
    height, width = array.shape
    if selector == "border_touching":
        return tuple(item for item in objects if item.top == 0 or item.left == 0 or item.bottom == height - 1 or item.right == width - 1)
    if selector == "interior_components":
        return tuple(item for item in objects if item.top > 0 and item.left > 0 and item.bottom < height - 1 and item.right < width - 1)
    if selector in {"unique_shape_components", "repeated_shape_components"}:
        counts = Counter(_shape_key(item, shape_mode) for item in objects)
        unique = selector == "unique_shape_components"
        return tuple(item for item in objects if (counts[_shape_key(item, shape_mode)] == 1) == unique)
    if selector == "shape_matched_components":
        color = _resolve_role(array, selector_color_role, background=background)
        reference_shapes = {
            _shape_key(item, shape_mode) for item in objects if item.color != color
        }
        return tuple(
            item for item in objects
            if item.color == color and _shape_key(item, shape_mode) in reference_shapes
        )
    if selector == "color_components":
        color = _resolve_role(array, selector_color_role, background=background)
        return tuple(item for item in objects if item.color == color)
    raise ValueError(f"unsupported selector {selector!r}")


def _relation_pairs(selected: Sequence[_Object], relation: str) -> tuple[tuple[_Object, _Object], ...]:
    if relation == "none":
        return ()
    pairs: list[tuple[_Object, _Object]] = []
    for index, first in enumerate(selected):
        for second in selected[index + 1:]:
            horizontal = first.top <= second.bottom and second.top <= first.bottom
            vertical = first.left <= second.right and second.left <= first.right
            first_center = first.center
            second_center = second.center
            diagonal = (
                abs(first_center[0] - second_center[0])
                == abs(first_center[1] - second_center[1])
                and first_center != second_center
            )
            if relation in {"diagonal_pairs", "same_shape_diagonal_pairs"}:
                if not diagonal:
                    continue
            elif not (horizontal or vertical):
                continue
            if relation == "same_color_aligned_pairs" and first.color != second.color:
                continue
            if relation in {"same_shape_aligned_pairs", "same_shape_diagonal_pairs"} and first.shape_signature != second.shape_signature:
                continue
            pairs.append((first, second))
    return tuple(pairs)


def _between_extents(first: _Object, second: _Object) -> frozenset[tuple[int, int]]:
    cells: set[tuple[int, int]] = set()
    # Connect overlapping row spans through the columns strictly between boxes.
    row_lo = max(first.top, second.top)
    row_hi = min(first.bottom, second.bottom)
    if row_lo <= row_hi:
        if first.right < second.left:
            for row in range(row_lo, row_hi + 1):
                cells.update((row, column) for column in range(first.right + 1, second.left))
        elif second.right < first.left:
            for row in range(row_lo, row_hi + 1):
                cells.update((row, column) for column in range(second.right + 1, first.left))
    # Connect overlapping column spans through the rows strictly between boxes.
    column_lo = max(first.left, second.left)
    column_hi = min(first.right, second.right)
    if column_lo <= column_hi:
        if first.bottom < second.top:
            for column in range(column_lo, column_hi + 1):
                cells.update((row, column) for row in range(first.bottom + 1, second.top))
        elif second.bottom < first.top:
            for column in range(column_lo, column_hi + 1):
                cells.update((row, column) for row in range(second.bottom + 1, first.top))
    return frozenset(cells)


def _geometry_edits(
    array: np.ndarray,
    selected: Sequence[_Object],
    pairs: Sequence[tuple[_Object, _Object]],
    geometry: str,
    parameters: Mapping[str, Any],
) -> tuple[tuple[int, int, int], ...]:
    height, width = array.shape
    edits: list[tuple[int, int, int]] = []
    if geometry == "selected_support":
        for item in selected:
            edits.extend((row, column, item.color) for row, column in sorted(item.cells))
    elif geometry == "ambient_holes":
        for item in selected:
            edits.extend((row, column, item.color) for row, column in sorted(item.holes))
    elif geometry in {"bounding_box_fill", "bounding_box_outline"}:
        for item in selected:
            for row in range(item.top, item.bottom + 1):
                for column in range(item.left, item.right + 1):
                    if geometry == "bounding_box_outline" and row not in {item.top, item.bottom} and column not in {item.left, item.right}:
                        continue
                    edits.append((row, column, item.color))
    elif geometry == "between_extents":
        for first, second in pairs:
            if first.color != second.color:
                raise ValueError("pair source color is ambiguous")
            source = first.color
            edits.extend((row, column, source) for row, column in sorted(_between_extents(first, second)))
    elif geometry == "diagonal_between_extents":
        for first, second in pairs:
            row, column = first.center
            target_row, target_column = second.center
            dy = 1 if target_row > row else -1
            dx = 1 if target_column > column else -1
            if first.color != second.color:
                raise ValueError("pair source color is ambiguous")
            source = first.color
            row += dy; column += dx
            while (row, column) != (target_row, target_column):
                edits.append((row, column, source))
                row += dy; column += dx
    elif geometry == "pair_midpoint_stamp":
        offsets = tuple(tuple(item) for item in parameters["stamp_offsets"])
        seen_centers: set[tuple[int, int]] = set()
        for first, second in pairs:
            first_row, first_column = first.center
            second_row, second_column = second.center
            if (first_row + second_row) % 2 or (first_column + second_column) % 2:
                continue
            center = ((first_row + second_row) // 2, (first_column + second_column) // 2)
            if center in seen_centers:
                continue
            seen_centers.add(center)
            if first.color != second.color:
                raise ValueError("pair source color is ambiguous")
            source = first.color
            for dy, dx in offsets:
                row, column = center[0] + dy, center[1] + dx
                if 0 <= row < height and 0 <= column < width:
                    edits.append((row, column, source))
    elif geometry == "rays_to_border":
        directions = tuple(tuple(item) for item in parameters["directions"])
        for item in selected:
            origins = item.cells if item.size == 1 else (item.center,)
            for origin_row, origin_column in origins:
                for dy, dx in directions:
                    row, column = origin_row + dy, origin_column + dx
                    while 0 <= row < height and 0 <= column < width:
                        edits.append((row, column, item.color))
                        row += dy; column += dx
    elif geometry == "outward_diagonal_rays":
        for item in selected:
            side_counts: list[tuple[str, int]] = []
            if item.top == 0:
                side_counts.append(("top", sum(row == 0 for row, _ in item.cells)))
            if item.bottom == height - 1:
                side_counts.append(("bottom", sum(row == height - 1 for row, _ in item.cells)))
            if item.left == 0:
                side_counts.append(("left", sum(column == 0 for _, column in item.cells)))
            if item.right == width - 1:
                side_counts.append(("right", sum(column == width - 1 for _, column in item.cells)))
            if not side_counts:
                continue
            maximum = max(count for _, count in side_counts)
            sides = [side for side, count in side_counts if count == maximum]
            if len(sides) != 1:
                continue
            side = sides[0]
            if side == "bottom":
                extreme = [(row, column) for row, column in item.cells if row == item.top]
                origins = (min(extreme, key=lambda cell: cell[1]), max(extreme, key=lambda cell: cell[1]))
                rays = ((origins[0], (-1, -1)), (origins[1], (-1, 1)))
            elif side == "top":
                extreme = [(row, column) for row, column in item.cells if row == item.bottom]
                origins = (min(extreme, key=lambda cell: cell[1]), max(extreme, key=lambda cell: cell[1]))
                rays = ((origins[0], (1, -1)), (origins[1], (1, 1)))
            elif side == "left":
                extreme = [(row, column) for row, column in item.cells if column == item.right]
                origins = (min(extreme, key=lambda cell: cell[0]), max(extreme, key=lambda cell: cell[0]))
                rays = ((origins[0], (-1, 1)), (origins[1], (1, 1)))
            else:
                extreme = [(row, column) for row, column in item.cells if column == item.left]
                origins = (min(extreme, key=lambda cell: cell[0]), max(extreme, key=lambda cell: cell[0]))
                rays = ((origins[0], (-1, -1)), (origins[1], (1, -1)))
            for (origin_row, origin_column), (dy, dx) in rays:
                row, column = origin_row + dy, origin_column + dx
                while 0 <= row < height and 0 <= column < width:
                    edits.append((row, column, item.color))
                    row += dy; column += dx
    elif geometry == "missing_corner_diagonal_rays":
        for item in selected:
            if item.height != 2 or item.width != 2 or item.size != 3:
                continue
            corners = {
                (item.top, item.left), (item.top, item.right),
                (item.bottom, item.left), (item.bottom, item.right),
            }
            missing = tuple(corners - set(item.cells))
            if len(missing) != 1:
                continue
            origin_row, origin_column = missing[0]
            dy = -1 if origin_row == item.top else 1
            dx = -1 if origin_column == item.left else 1
            row, column = origin_row + dy, origin_column + dx
            while 0 <= row < height and 0 <= column < width:
                edits.append((row, column, item.color))
                row += dy; column += dx
    elif geometry in {"translate", "translation_orbit"}:
        dy, dx = tuple(parameters["offset"])
        max_steps = int(parameters["max_steps"]) if geometry == "translation_orbit" else 1
        for item in selected:
            for step in range(1, max_steps + 1):
                shifted = tuple((row + step * dy, column + step * dx) for row, column in item.cells)
                if not all(0 <= row < height and 0 <= column < width for row, column in shifted):
                    break
                edits.extend((row, column, item.color) for row, column in shifted)
    elif geometry == "local_stamp":
        offsets = tuple(tuple(item) for item in parameters["stamp_offsets"])
        for item in selected:
            origins = item.cells if item.size == 1 else (item.center,)
            for origin_row, origin_column in origins:
                for dy, dx in offsets:
                    row, column = origin_row + dy, origin_column + dx
                    if 0 <= row < height and 0 <= column < width:
                        edits.append((row, column, item.color))
    elif geometry == "checkerboard_from_rows":
        if height != 2:
            raise ValueError("row-derived checkerboard requires exactly two rows")
        first = set(int(item) for item in array[0])
        second = set(int(item) for item in array[1])
        if len(first) != 1 or len(second) != 1 or first == second:
            raise ValueError("checkerboard source rows must be uniform and distinct")
        palette = (next(iter(first)), next(iter(second)))
        for row in range(height):
            for column in range(width):
                edits.append((row, column, palette[(row + column) % 2]))
    elif geometry == "control_directed_copy":
        # The control and payload are separated colored components.  A 3-wide
        # control has one full row and one singleton in the adjacent row; that
        # singleton chooses the horizontal direction.  The other component is
        # copied by exactly one payload width.
        candidates: list[tuple[_Object, int]] = []
        for item in selected:
            if item.width != 3 or item.height < 2:
                continue
            row_counts = Counter(row for row, _ in item.cells)
            full_rows = [row for row, count in row_counts.items() if count == 3]
            singleton_rows = [row for row, count in row_counts.items() if count == 1]
            if not full_rows or not singleton_rows:
                continue
            direction_cell = min(
                (cell for cell in item.cells if row_counts[cell[0]] == 1),
                key=lambda cell: (cell[0], cell[1]),
            )
            if direction_cell[1] == item.left:
                candidates.append((item, -1))
            elif direction_cell[1] == item.right:
                candidates.append((item, 1))
        if len(candidates) != 1:
            raise ValueError("scene lacks one unambiguous directional control")
        control, direction = candidates[0]
        payloads = [item for item in selected if item is not control and item.color != control.color]
        if len(payloads) != 1:
            raise ValueError("scene lacks one unambiguous payload")
        payload = payloads[0]
        destination_left = payload.right + 1 if direction > 0 else payload.left - payload.width
        for row, column in payload.cells:
            local_column = column - payload.left
            mirrored_column = payload.width - 1 - local_column
            target_column = destination_left + mirrored_column
            if not 0 <= target_column < width:
                raise ValueError("directed copy leaves the canvas")
            edits.append((row, target_column, payload.color))
    elif geometry == "marker_quadrant_render":
        markers = [item for item in selected if item.size == 1]
        if len(markers) != 1 or height % 2 or width % 2:
            raise ValueError("quadrant render needs one singleton marker and even dimensions")
        marker = markers[0]
        split_row, split_column = height // 2, width // 2
        row_start = 0 if marker.top < split_row else split_row
        row_stop = split_row if marker.top < split_row else height
        column_start = 0 if marker.left < split_column else split_column
        column_stop = split_column if marker.left < split_column else width
        background = _resolve_role(array, str(parameters["background_role"]))
        for row in range(height):
            for column in range(width):
                color = marker.color if row_start <= row < row_stop and column_start <= column < column_stop else background
                edits.append((row, column, color))
    elif geometry == "project_to_container_boundary":
        rectangles = [item for item in selected if item.size == item.height * item.width and item.height >= 2 and item.width >= 2]
        if not rectangles:
            raise ValueError("scene lacks a solid container")
        maximum = max(item.size for item in rectangles)
        containers = [item for item in rectangles if item.size == maximum]
        if len(containers) != 1:
            raise ValueError("solid container is ambiguous")
        container = containers[0]
        markers = [item for item in selected if item is not container and item.size == 1]
        if not markers:
            raise ValueError("scene lacks exterior marker objects")
        changed = 0
        for marker in markers:
            row, column = next(iter(marker.cells))
            destinations: list[tuple[int, tuple[int, int]]] = []
            if container.top <= row <= container.bottom:
                destinations.extend((abs(column - edge), (row, edge)) for edge in (container.left, container.right))
            if container.left <= column <= container.right:
                destinations.extend((abs(row - edge), (edge, column)) for edge in (container.top, container.bottom))
            if not destinations:
                continue
            distance = min(item[0] for item in destinations)
            nearest = sorted(cell for candidate_distance, cell in destinations if candidate_distance == distance)
            if len(nearest) != 1:
                continue
            edits.append((nearest[0][0], nearest[0][1], marker.color))
            changed += 1
        if not changed:
            raise ValueError("no exterior marker aligns with the container")
    elif geometry == "shape_color_transfer":
        background = _resolve_role(array, str(parameters["background_role"]))
        all_objects = _objects_cached(
            validate_grid(array),
            background,
            int(parameters["connectivity"]),
            bool(parameters["monochrome_components"]),
        )
        mode = str(parameters["shape_mode"])
        changed = 0
        for item in selected:
            reference_colors = sorted({
                other.color for other in all_objects
                if other.color != item.color and _shape_key(other, mode) == _shape_key(item, mode)
            })
            if len(reference_colors) != 1:
                continue
            edits.extend((row, column, reference_colors[0]) for row, column in sorted(item.cells))
            changed += 1
        if not changed:
            raise ValueError("no selected object has a unique cross-color shape match")
    elif geometry == "corner_legend_pair_swap":
        # A 2x2 corner legend stores two unordered palette transpositions, one
        # pair per row.  The legend is read-only; the mapping applies elsewhere.
        background = _resolve_role(array, str(parameters["background_role"]))
        placements = (
            (0, 0),
            (0, width - 2),
            (height - 2, 0),
            (height - 2, width - 2),
        )
        legends: list[tuple[int, int, dict[int, int]]] = []
        for top, left in placements:
            block = array[top:top + 2, left:left + 2]
            if block.shape != (2, 2) or np.any(block == background):
                continue
            mapping = {
                int(block[0, 0]): int(block[0, 1]),
                int(block[0, 1]): int(block[0, 0]),
                int(block[1, 0]): int(block[1, 1]),
                int(block[1, 1]): int(block[1, 0]),
            }
            if len(mapping) != 4:
                continue
            legends.append((top, left, mapping))
        if len(legends) != 1:
            raise ValueError("scene lacks one unambiguous 2x2 corner legend")
        top, left, mapping = legends[0]
        for row in range(height):
            for column in range(width):
                if top <= row < top + 2 and left <= column < left + 2:
                    continue
                color = int(array[row, column])
                if color in mapping:
                    edits.append((row, column, mapping[color]))
        if not edits:
            raise ValueError("corner legend has no payload occurrences")
    else:
        raise ValueError(f"unsupported geometry {geometry!r}")
    return tuple(edits)


def _execute_once(
    program: ToolProgram, grid: Grid, *, max_objects: int = 128,
) -> Grid:
    parameters = decode_canonical_parameters(program.parameters_json)
    source = _array(grid)
    if source.size > 900:
        raise ValueError("grid exceeds the ARC cell limit")
    background = _resolve_role(source, str(parameters["background_role"]))
    objects = _objects_cached(
        grid,
        background,
        int(parameters["connectivity"]),
        bool(parameters["monochrome_components"]),
        max_objects,
    )
    selected = _select(
        objects,
        program.selector,
        source,
        background,
        str(parameters["selector_color_role"]),
        str(parameters["shape_mode"]),
    )
    if not selected:
        raise ValueError("selector has no members")
    pairs = _relation_pairs(selected, program.relation)
    if program.relation != "none" and not pairs:
        raise ValueError("relation has no instances")
    edits = _geometry_edits(source, selected, pairs, program.geometry, parameters)
    if not edits:
        raise ValueError("geometry produced no edits")

    result = source.copy()
    if program.geometry in {"translate", "translation_orbit"} and not bool(parameters["include_sources"]):
        for item in selected:
            for row, column in item.cells:
                result[row, column] = background

    writes: dict[tuple[int, int], set[int]] = defaultdict(set)
    for row, column, source_color in edits:
        if bool(parameters["background_only"]) and int(result[row, column]) != background:
            continue
        if program.effect == "erase_selected":
            color = background
        elif program.effect == "paint_source_color":
            color = source_color
        else:
            color = _resolve_role(source, str(parameters["paint_role"]), background=background, source=source_color)
        writes[(row, column)].add(int(color))
    conflicting = sorted(position for position, colors in writes.items() if len(colors) != 1)
    if conflicting:
        raise ValueError("tool proposes conflicting colors for one cell")
    for (row, column), colors in sorted(writes.items()):
        result[row, column] = next(iter(colors))
    rendered = validate_grid(result)
    if rendered == grid:
        raise ValueError("tool execution is a no-op")
    return rendered


def execute_tool(
    program: ToolProgram, grid: Any, *, max_objects: int = 128,
) -> Grid:
    """Execute a frozen tool without target, task, or corpus access."""

    if not isinstance(program, ToolProgram):
        raise TypeError("program must be a ToolProgram")
    max_objects = _integer(max_objects, "max_objects", 1, 900)
    current = _as_grid(grid)
    maximum = int(program.parameters["max_steps"]) if program.closure == "until_stable" else 1
    for _ in range(maximum):
        try:
            following = _execute_once(program, current, max_objects=max_objects)
        except ValueError as error:
            if program.closure == "until_stable" and "no-op" in str(error):
                return current
            raise
        if following == current:
            return current
        current = following
        if program.closure == "once":
            break
    return validate_grid(current)


def tool_applicable(program: ToolProgram, grid: Any) -> bool:
    try:
        execute_tool(program, grid)
    except (AssertionError, KeyError, TypeError, ValueError, OverflowError):
        return False
    return True


def _base_parameters(
    *,
    background_role: str,
    connectivity: int = 4,
    monochrome_components: bool = True,
    selector_color_role: str = "unique_foreground",
    paint_role: str = "literal:1",
    background_only: bool = True,
    include_sources: bool = True,
    directions: Sequence[tuple[int, int]] = (),
    offset: tuple[int, int] = (0, 0),
    stamp_offsets: Sequence[tuple[int, int]] = (),
    max_steps: int = 30,
    shape_mode: str = "exact",
) -> dict[str, Any]:
    return {
        "background_role": background_role,
        "connectivity": connectivity,
        "monochrome_components": monochrome_components,
        "selector_color_role": selector_color_role,
        "paint_role": paint_role,
        "background_only": background_only,
        "include_sources": include_sources,
        "directions": [list(item) for item in directions],
        "offset": list(offset),
        "stamp_offsets": [list(item) for item in stamp_offsets],
        "max_steps": max_steps,
        "shape_mode": shape_mode,
    }


def _background_roles(inputs: Sequence[Grid]) -> tuple[str, ...]:
    roles: list[str] = []
    for role in ("background", "corner", "zero"):
        try:
            [_resolve_role(_array(grid), role) for grid in inputs]
        except ValueError:
            continue
        roles.append(role)
    common = set(value for row in inputs[0] for value in row)
    for grid in inputs[1:]:
        common &= {value for row in grid for value in row}
    roles.extend(f"literal:{color}" for color in sorted(common))
    return tuple(dict.fromkeys(roles))


def _paint_roles(inputs: Sequence[Grid], targets: Sequence[Grid]) -> tuple[str, ...]:
    changed_target_colors: set[int] | None = None
    for source_grid, target_grid in zip(inputs, targets):
        source = _array(source_grid); target = _array(target_grid)
        if source.shape != target.shape:
            return ()
        colors = {int(value) for value in target[source != target]}
        changed_target_colors = colors if changed_target_colors is None else changed_target_colors & colors
    roles: list[str] = [f"literal:{color}" for color in sorted(changed_target_colors or ())]
    for role in ("unique_foreground", "rarest_foreground", "most_foreground", "background", "zero"):
        try:
            [_resolve_role(_array(grid), role) for grid in inputs]
        except ValueError:
            continue
        roles.append(role)
    roles.append("source")
    return tuple(dict.fromkeys(roles))


def _selector_color_roles(inputs: Sequence[Grid]) -> tuple[str, ...]:
    roles: list[str] = []
    for role in ("unique_foreground", "rarest_foreground", "most_foreground"):
        try:
            [_resolve_role(_array(grid), role) for grid in inputs]
        except ValueError:
            continue
        roles.append(role)
    common = set(value for row in inputs[0] for value in row)
    for grid in inputs[1:]:
        common &= {value for row in grid for value in row}
    roles.extend(f"literal:{color}" for color in sorted(common))
    return tuple(dict.fromkeys(roles)) or ("unique_foreground",)


def _translation_vectors(inputs: Sequence[Grid], targets: Sequence[Grid], limit: int) -> tuple[tuple[int, int], ...]:
    candidates: Counter[tuple[int, int]] = Counter()
    for source_grid, target_grid in zip(inputs, targets):
        source = _array(source_grid); target = _array(target_grid)
        if source.shape != target.shape:
            continue
        for color in sorted((set(int(item) for item in source.ravel()) & set(int(item) for item in target.ravel()))):
            before = tuple(zip(*np.nonzero(source == color)))
            after = tuple(zip(*np.nonzero(target == color)))
            if len(before) * len(after) > 4_096:
                continue
            for sy, sx in before:
                for ty, tx in after:
                    offset = (int(ty - sy), int(tx - sx))
                    if offset != (0, 0):
                        candidates[offset] += 1
    return tuple(
        offset for offset, _ in sorted(
            candidates.items(), key=lambda item: (-item[1], abs(item[0][0]) + abs(item[0][1]), item[0])
        )[:limit]
    )


def _stamp_patterns(inputs: Sequence[Grid], targets: Sequence[Grid], limit: int) -> tuple[tuple[tuple[int, int], ...], ...]:
    """Infer only translation-invariant local additions around singleton seeds."""
    per_demo: list[set[tuple[tuple[int, int], ...]]] = []
    for source_grid, target_grid in zip(inputs, targets):
        source = _array(source_grid); target = _array(target_grid)
        if source.shape != target.shape:
            return ()
        backgrounds = Counter(int(item) for item in source.ravel())
        background = min((-count, color) for color, count in backgrounds.items())[1]
        singleton_cells: list[tuple[int, int]] = []
        for color in sorted(set(int(item) for item in source.ravel()) - {background}):
            for cells in _components(source == color, 4):
                if len(cells) == 1:
                    singleton_cells.append(next(iter(cells)))
        added = set(zip(*np.nonzero(source != target)))
        patterns: set[tuple[tuple[int, int], ...]] = set()
        for origin_row, origin_column in singleton_cells:
            offsets = tuple(sorted(
                (int(row - origin_row), int(column - origin_column))
                for row, column in added
                if max(abs(int(row - origin_row)), abs(int(column - origin_column))) <= 3
                and (row, column) != (origin_row, origin_column)
            ))
            if 0 < len(offsets) <= limit:
                patterns.add(offsets)
        per_demo.append(patterns)
    if not per_demo:
        return ()
    common = set(per_demo[0])
    for patterns in per_demo[1:]:
        common &= patterns
    standard = {
        ((-1, 0), (0, -1), (0, 1), (1, 0)),
        tuple(sorted(ALL_DIRECTIONS)),
        ((-1, -1), (-1, 1), (1, -1), (1, 1)),
    }
    return tuple(sorted(common | standard, key=lambda item: (len(item), item)))


def _ray_direction_sets() -> tuple[tuple[tuple[int, int], ...], ...]:
    return (
        ((-1, 0),), ((1, 0),), ((0, -1),), ((0, 1),),
        ((-1, 0), (1, 0)), ((0, -1), (0, 1)), tuple(ORTHOGONAL),
        tuple(DIAGONAL), tuple(ALL_DIRECTIONS),
    )


def _program(
    selector: str,
    relation: str,
    geometry: str,
    effect: str,
    closure: str,
    parameters: Mapping[str, Any],
) -> ToolProgram | None:
    costs = {
        "selected_support": 3,
        "ambient_holes": 5,
        "bounding_box_fill": 5,
        "bounding_box_outline": 5,
        "between_extents": 6,
        "diagonal_between_extents": 7,
        "pair_midpoint_stamp": 7,
        "rays_to_border": 6,
        "outward_diagonal_rays": 7,
        "missing_corner_diagonal_rays": 7,
        "translate": 7,
        "translation_orbit": 8,
        "local_stamp": 7,
        "checkerboard_from_rows": 5,
        "control_directed_copy": 8,
        "marker_quadrant_render": 7,
        "project_to_container_boundary": 8,
        "shape_color_transfer": 7,
        "corner_legend_pair_swap": 6,
    }
    try:
        return ToolProgram.from_parameters(
            selector=selector, relation=relation, geometry=geometry,
            effect=effect, closure=closure, parameters=parameters,
            cost=costs[geometry] + (2 if closure == "until_stable" else 0),
        )
    except (KeyError, TypeError, ValueError, OverflowError):
        return None


def _complete_scene_native_programs(
    inputs: tuple[Grid, ...],
    targets: tuple[Grid, ...],
) -> tuple[ToolProgram, ...]:
    """Enumerate the complete, deliberately small scene-native subgrammar."""
    if any((len(source), len(source[0])) != (len(target), len(target[0])) for source, target in zip(inputs, targets)):
        return ()
    backgrounds = _background_roles(inputs)
    paints = _paint_roles(inputs, targets)
    selector_roles = _selector_color_roles(inputs)
    programs: dict[str, ToolProgram] = {}

    def add(candidate: ToolProgram | None) -> None:
        if candidate is not None:
            programs[candidate.tool_id] = candidate

    pair_stamps = (
        ((0, 0), (-1, 0), (0, -1), (0, 1), (1, 0)),
        ((0, 0),) + tuple(ALL_DIRECTIONS),
        ((0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)),
    )
    for background_role in backgrounds:
        add(_program(
            "all_components", "none", "checkerboard_from_rows",
            "paint_source_color", "once",
            _base_parameters(background_role=background_role, paint_role="source", background_only=False),
        ))
        add(_program(
            "all_components", "none", "missing_corner_diagonal_rays",
            "paint_source_color", "once",
            _base_parameters(background_role=background_role, paint_role="source", background_only=True),
        ))
        for connectivity in (4, 8):
            for selector_role in selector_roles:
                direct = _base_parameters(
                    background_role=background_role,
                    connectivity=connectivity,
                    selector_color_role=selector_role,
                    paint_role="source",
                    background_only=False,
                )
                for selector, geometry in (
                    ("all_components", "control_directed_copy"),
                    ("color_components", "marker_quadrant_render"),
                    ("all_components", "project_to_container_boundary"),
                    ("all_components", "corner_legend_pair_swap"),
                ):
                    add(_program(selector, "none", geometry, "paint_source_color", "once", direct))
                for shape_mode in ("exact", "d4"):
                    transfer = dict(direct)
                    transfer["shape_mode"] = shape_mode
                    add(_program(
                        "color_components", "none", "shape_color_transfer",
                        "paint_source_color", "once", transfer,
                    ))
                    for paint_role in paints:
                        matched = dict(transfer)
                        matched["paint_role"] = paint_role
                        add(_program(
                            "shape_matched_components", "none", "selected_support",
                            "recolor_selected", "once", matched,
                        ))
            for paint_role in paints:
                add(_program(
                    "largest_components", "none", "outward_diagonal_rays",
                    "paint_constant", "once",
                    _base_parameters(
                        background_role=background_role, connectivity=connectivity,
                        paint_role=paint_role, background_only=True,
                    ),
                ))
        for paint_role in paints:
            pair_parameters = _base_parameters(
                background_role=background_role,
                paint_role=paint_role,
                background_only=True,
            )
            for relation in ("diagonal_pairs", "same_shape_diagonal_pairs"):
                add(_program(
                    "all_components", relation, "diagonal_between_extents",
                    "paint_constant", "once", pair_parameters,
                ))
            for selector in ("singleton_components", "color_components", "all_components"):
                roles = selector_roles if selector == "color_components" else ("unique_foreground",)
                for selector_role in roles:
                    for relation in ("aligned_pairs", "same_color_aligned_pairs", "same_shape_aligned_pairs"):
                        for offsets in pair_stamps:
                            parameters = _base_parameters(
                                background_role=background_role,
                                selector_color_role=selector_role,
                                paint_role=paint_role,
                                background_only=True,
                                stamp_offsets=offsets,
                            )
                            add(_program(
                                selector, relation, "pair_midpoint_stamp",
                                "paint_constant", "once", parameters,
                            ))
    return tuple(sorted(programs.values(), key=lambda value: (value.cost, value.tool_id)))


def _parameterized_programs(
    inputs: tuple[Grid, ...],
    targets: tuple[Grid, ...],
    limits: ToolSynthesisLimits,
) -> Iterator[ToolProgram]:
    if any((len(source), len(source[0])) != (len(target), len(target[0])) for source, target in zip(inputs, targets)):
        return
    background_roles = _background_roles(inputs)
    paint_roles = _paint_roles(inputs, targets)
    selector_color_roles = _selector_color_roles(inputs)
    if not background_roles or not paint_roles:
        return

    # A compact role/dimension-derived motif constructor.  It is deliberately
    # placed before the larger object cross-product so finite caps cannot hide
    # the smallest task-local algebra.
    for background_role in background_roles:
        params = _base_parameters(
            background_role=background_role,
            paint_role="source",
            background_only=False,
        )
        candidate = _program(
            "all_components", "none", "checkerboard_from_rows",
            "paint_source_color", "once", params,
        )
        if candidate is not None:
            yield candidate

    # Scene-native relational constructors.  All location and payload choices
    # are recovered again from each runtime input; only palette-role predicates
    # and connectivity remain in the compiled program.
    for background_role in background_roles:
        for selector_role in selector_color_roles:
            for connectivity in (4, 8):
                params = _base_parameters(
                    background_role=background_role,
                    connectivity=connectivity,
                    selector_color_role=selector_role,
                    paint_role="source",
                    background_only=False,
                )
                for selector, geometry in (
                    ("all_components", "control_directed_copy"),
                    ("color_components", "marker_quadrant_render"),
                    ("all_components", "project_to_container_boundary"),
                    ("all_components", "corner_legend_pair_swap"),
                ):
                    candidate = _program(
                        selector, "none", geometry, "paint_source_color", "once", params,
                    )
                    if candidate is not None:
                        yield candidate
                for shape_mode in ("exact", "d4"):
                    shape_params = _base_parameters(
                        background_role=background_role,
                        connectivity=connectivity,
                        selector_color_role=selector_role,
                        paint_role="source",
                        background_only=False,
                        shape_mode=shape_mode,
                    )
                    transfer = _program(
                        "color_components", "none", "shape_color_transfer",
                        "paint_source_color", "once", shape_params,
                    )
                    if transfer is not None:
                        yield transfer
                    for paint_role in paint_roles:
                        matched_params = dict(shape_params)
                        matched_params["paint_role"] = paint_role
                        matched = _program(
                            "shape_matched_components", "none", "selected_support",
                            "recolor_selected", "once", matched_params,
                        )
                        if matched is not None:
                            yield matched

        for paint_role in paint_roles:
            for connectivity in (4, 8):
                params = _base_parameters(
                    background_role=background_role,
                    connectivity=connectivity,
                    paint_role=paint_role,
                    background_only=True,
                )
                candidate = _program(
                    "largest_components", "none", "outward_diagonal_rays",
                    "paint_constant", "once", params,
                )
                if candidate is not None:
                    yield candidate

        params = _base_parameters(
            background_role=background_role,
            paint_role="source",
            background_only=True,
        )
        candidate = _program(
            "all_components", "none", "missing_corner_diagonal_rays",
            "paint_source_color", "once", params,
        )
        if candidate is not None:
            yield candidate

        for paint_role in paint_roles:
            params = _base_parameters(
                background_role=background_role,
                paint_role=paint_role,
                background_only=True,
            )
            for relation in ("diagonal_pairs", "same_shape_diagonal_pairs"):
                candidate = _program(
                    "all_components", relation, "diagonal_between_extents",
                    "paint_constant", "once", params,
                )
                if candidate is not None:
                    yield candidate

    # Pair-relative stamps cover constructions whose location is defined by a
    # relation rather than by either endpoint alone (for example a plus at the
    # midpoint of two aligned markers).
    pair_stamps = (
        ((0, 0), (-1, 0), (0, -1), (0, 1), (1, 0)),
        ((0, 0),) + tuple(ALL_DIRECTIONS),
        ((0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)),
    )
    for background_role in background_roles:
        for selector in ("singleton_components", "color_components", "all_components"):
            selector_roles = selector_color_roles if selector == "color_components" else ("unique_foreground",)
            for selector_role in selector_roles:
                for relation in ("aligned_pairs", "same_color_aligned_pairs", "same_shape_aligned_pairs"):
                    for offsets in pair_stamps:
                        for paint_role in paint_roles:
                            params = _base_parameters(
                                background_role=background_role,
                                selector_color_role=selector_role,
                                paint_role=paint_role,
                                background_only=True,
                                stamp_offsets=offsets,
                            )
                            candidate = _program(
                                selector, relation, "pair_midpoint_stamp",
                                "paint_constant", "once", params,
                            )
                            if candidate is not None:
                                yield candidate

    selectors = SELECTORS
    # Local recoloring and topology-conditioned selection.
    for background_role in background_roles:
        for connectivity in (4, 8):
            for monochrome in (True, False):
                for selector in selectors:
                    selector_roles = selector_color_roles if selector == "color_components" else ("unique_foreground",)
                    for selector_role in selector_roles:
                        for paint_role in paint_roles:
                            for effect in ("recolor_selected", "erase_selected"):
                                params = _base_parameters(
                                    background_role=background_role,
                                    connectivity=connectivity,
                                    monochrome_components=monochrome,
                                    selector_color_role=selector_role,
                                    paint_role=paint_role,
                                    background_only=False,
                                )
                                candidate = _program(selector, "none", "selected_support", effect, "once", params)
                                if candidate is not None:
                                    yield candidate

                        # Ambient/object geometry.  The source-color effect is
                        # essential for palette-variable tasks.
                        for geometry in ("ambient_holes", "bounding_box_fill", "bounding_box_outline"):
                            for effect in ("paint_constant", "paint_source_color"):
                                roles = paint_roles if effect == "paint_constant" else ("source",)
                                for paint_role in roles:
                                    for background_only in (True, False):
                                        params = _base_parameters(
                                            background_role=background_role,
                                            connectivity=connectivity,
                                            monochrome_components=monochrome,
                                            selector_color_role=selector_role,
                                            paint_role=paint_role,
                                            background_only=background_only,
                                        )
                                        candidate = _program(selector, "none", geometry, effect, "once", params)
                                        if candidate is not None:
                                            yield candidate

    # Aligned object/cell connectors.
    for background_role in background_roles:
        for selector in ("all_components", "singleton_components", "color_components"):
            selector_roles = selector_color_roles if selector == "color_components" else ("unique_foreground",)
            for selector_role in selector_roles:
                for relation in ("aligned_pairs", "same_color_aligned_pairs", "same_shape_aligned_pairs"):
                    for effect in ("paint_constant", "paint_source_color"):
                        roles = paint_roles if effect == "paint_constant" else ("source",)
                        for paint_role in roles:
                            params = _base_parameters(
                                background_role=background_role,
                                selector_color_role=selector_role,
                                paint_role=paint_role,
                                background_only=True,
                            )
                            candidate = _program(selector, relation, "between_extents", effect, "once", params)
                            if candidate is not None:
                                yield candidate

    # Directional rays.
    for background_role in background_roles:
        for selector in ("singleton_components", "color_components", "all_components"):
            selector_roles = selector_color_roles if selector == "color_components" else ("unique_foreground",)
            for selector_role in selector_roles:
                for directions in _ray_direction_sets():
                    for effect in ("paint_constant", "paint_source_color"):
                        roles = paint_roles if effect == "paint_constant" else ("source",)
                        for paint_role in roles:
                            params = _base_parameters(
                                background_role=background_role,
                                selector_color_role=selector_role,
                                paint_role=paint_role,
                                background_only=True,
                                directions=directions,
                            )
                            candidate = _program(selector, "none", "rays_to_border", effect, "once", params)
                            if candidate is not None:
                                yield candidate

    # Copy/move and periodic motif extension.  Vectors are target-bound during
    # synthesis but fixed in the executable record.
    translations = _translation_vectors(inputs, targets, limits.max_translation_vectors)
    for background_role in background_roles:
        for selector in (
            "all_components", "singleton_components", "smallest_components",
            "largest_components", "unique_shape_components", "color_components",
        ):
            selector_roles = selector_color_roles if selector == "color_components" else ("unique_foreground",)
            for selector_role in selector_roles:
                for offset in translations:
                    for include_sources in (True, False):
                        for geometry in ("translate", "translation_orbit"):
                            params = _base_parameters(
                                background_role=background_role,
                                selector_color_role=selector_role,
                                paint_role="source",
                                background_only=True,
                                include_sources=include_sources,
                                offset=offset,
                                max_steps=30,
                            )
                            candidate = _program(selector, "none", geometry, "paint_source_color", "once", params)
                            if candidate is not None:
                                yield candidate

    # Small translation-invariant stamps around marker objects.
    stamp_patterns = _stamp_patterns(inputs, targets, limits.max_stamp_offsets)
    for background_role in background_roles:
        for selector in ("singleton_components", "color_components"):
            selector_roles = selector_color_roles if selector == "color_components" else ("unique_foreground",)
            for selector_role in selector_roles:
                for offsets in stamp_patterns:
                    for effect in ("paint_constant", "paint_source_color"):
                        roles = paint_roles if effect == "paint_constant" else ("source",)
                        for paint_role in roles:
                            params = _base_parameters(
                                background_role=background_role,
                                selector_color_role=selector_role,
                                paint_role=paint_role,
                                background_only=True,
                                stamp_offsets=offsets,
                            )
                            candidate = _program(selector, "none", "local_stamp", effect, "once", params)
                            if candidate is not None:
                                yield candidate


def _compile_exact_programs(
    training_inputs: Sequence[Any],
    training_outputs: Sequence[Any],
    limits: ToolSynthesisLimits | None = None,
) -> tuple[tuple[ToolProgram, ...], int, int, str]:
    """Internal exact compiler with explicit proposal/execution accounting."""

    limits = limits or ToolSynthesisLimits()
    inputs = tuple(_as_grid(grid) for grid in training_inputs)
    targets = tuple(_as_grid(grid) for grid in training_outputs)
    if not inputs or len(inputs) != len(targets):
        raise ValueError("training inputs and outputs must have equal positive length")
    if any(len(grid) * len(grid[0]) > limits.max_cells for grid in inputs + targets):
        raise ValueError("demonstration exceeds the configured cell budget")

    syntax: dict[str, ToolProgram] = {}
    syntax_limit_reached = False
    for candidate in _parameterized_programs(inputs, targets, limits):
        syntax.setdefault(candidate.tool_id, candidate)
        if len(syntax) >= limits.max_programs:
            syntax_limit_reached = True
            break
    exact: list[ToolProgram] = []
    executions = 0
    execution_limit_reached = False
    exact_limit_reached = False
    considered = 0
    for candidate in sorted(syntax.values(), key=lambda item: (item.cost, item.tool_id)):
        if executions + len(inputs) > limits.max_executions:
            execution_limit_reached = True
            break
        considered += 1
        outputs_list: list[Grid] = []
        try:
            for grid in inputs:
                outputs_list.append(
                    execute_tool(candidate, grid, max_objects=limits.max_objects)
                )
                executions += 1
        except (AssertionError, KeyError, TypeError, ValueError, OverflowError):
            continue
        outputs = tuple(outputs_list)
        if outputs == targets:
            exact.append(candidate)
            if len(exact) >= limits.max_candidates:
                exact_limit_reached = True
                break
    limit_reached = (
        "exact_candidate_cap" if exact_limit_reached
        else "execution_cap" if execution_limit_reached
        else "program_cap" if syntax_limit_reached
        else ""
    )
    return tuple(exact), considered, executions, limit_reached


def propose_tool_programs(
    training_inputs: Sequence[Any],
    training_outputs: Sequence[Any],
    limits: ToolSynthesisLimits | None = None,
) -> tuple[ToolProgram, ...]:
    """Compile finite target-aware syntax and return demo-exact programs only."""

    return _compile_exact_programs(training_inputs, training_outputs, limits)[0]


def synthesize_tools(
    task: TrainingTask | Mapping[str, Any],
    limits: ToolSynthesisLimits | None = None,
) -> ToolSynthesisResult:
    """Synthesize, exact-replay, freeze, then run on sanitized test inputs."""

    limits = limits or ToolSynthesisLimits()
    sanitized = sanitize_training_task(task)

    # This call is the only target-aware phase.  Returned programs no longer
    # retain targets or target-derived coordinate sets.
    programs, programs_considered, compile_executions, limit_reached = _compile_exact_programs(
        sanitized.training_inputs,
        sanitized.training_outputs,
        limits,
    )
    behavior_classes: dict[str, ToolCandidate] = {}
    exact_programs = 0
    test_executions = 0
    for program in programs:
        try:
            training_outputs = tuple(
                execute_tool(program, grid, max_objects=limits.max_objects)
                for grid in sanitized.training_inputs
            )
            if training_outputs != sanitized.training_outputs:
                continue
            exact_programs += 1
            test_outputs = tuple(
                execute_tool(program, grid, max_objects=limits.max_objects)
                for grid in sanitized.test_inputs
            )
            test_executions += len(sanitized.test_inputs)
        except (AssertionError, KeyError, TypeError, ValueError, OverflowError):
            continue
        candidate = ToolCandidate(program=program, training_outputs=training_outputs, test_outputs=test_outputs)
        prior = behavior_classes.get(candidate.behavior_hash)
        if prior is None or (program.cost, program.tool_id) < (prior.program.cost, prior.program.tool_id):
            behavior_classes[candidate.behavior_hash] = candidate
    ordered = tuple(sorted(
        behavior_classes.values(),
        key=lambda item: (item.program.cost, item.behavior_hash, item.program.tool_id),
    )[:limits.max_candidates])
    return ToolSynthesisResult(
        candidates=ordered,
        programs_considered=programs_considered,
        executions_performed=compile_executions + len(programs) * len(sanitized.training_inputs) + test_executions,
        exact_programs=exact_programs,
        behavior_classes=len(ordered),
        limit_reached=limit_reached,
    )


def synthesize_complete_scene_native_tools(
    task: TrainingTask | Mapping[str, Any],
) -> CompleteToolRouteResult:
    """Exhaustively synthesize the finite scene-native relational subgrammar.

    Unlike :func:`synthesize_tools`, this route has no prefix cap.  Its grammar
    has only role values extracted from the demonstrations, two connectivity
    choices, two shape gauges, three fixed local stamps, and the declared
    finite enum axes above.  Every constructed syntax is executed on every
    demonstration before the completion certificate is created.
    """

    sanitized = sanitize_training_task(task)
    programs = _complete_scene_native_programs(
        sanitized.training_inputs,
        sanitized.training_outputs,
    )
    program_space_hash = sha256_record([program.tool_id for program in programs])
    executions = 0
    exact: list[tuple[ToolProgram, tuple[Grid, ...]]] = []
    for program in programs:
        outputs: list[Grid] = []
        failed = False
        for grid in sanitized.training_inputs:
            try:
                outputs.append(execute_tool(program, grid))
                executions += 1
            except (AssertionError, KeyError, TypeError, ValueError, OverflowError):
                executions += 1
                failed = True
                break
        if not failed and tuple(outputs) == sanitized.training_outputs:
            exact.append((program, tuple(outputs)))

    quotient: dict[str, ToolCandidate] = {}
    exact_programs = 0
    for program, training_outputs in exact:
        test_outputs: list[Grid] = []
        failed = False
        for grid in sanitized.test_inputs:
            try:
                test_outputs.append(execute_tool(program, grid))
                executions += 1
            except (AssertionError, KeyError, TypeError, ValueError, OverflowError):
                executions += 1
                failed = True
                break
        if failed:
            continue
        exact_programs += 1
        candidate = ToolCandidate(
            program=program,
            training_outputs=training_outputs,
            test_outputs=tuple(test_outputs),
        )
        prior = quotient.get(candidate.behavior_hash)
        if prior is None or (program.cost, program.tool_id) < (prior.program.cost, prior.program.tool_id):
            quotient[candidate.behavior_hash] = candidate
    candidates = tuple(sorted(
        quotient.values(),
        key=lambda item: (item.program.cost, item.behavior_hash, item.program.tool_id),
    ))
    certificate = RouteCompletionCertificate(
        route="scene_native_relational",
        program_space_hash=program_space_hash,
        grammar_contract_hash=TOOL_LANGUAGE_HASH,
        training_hashes=sanitized.training_hashes,
        programs_enumerated=len(programs),
        complete=True,
    )
    return CompleteToolRouteResult(
        certificate=certificate,
        candidates=candidates,
        executions_performed=executions,
        exact_programs=exact_programs,
    )


def lower_to_block9_leaf(program: ToolProgram) -> LeafInvocation | None:
    """Return a Block 9 leaf only when exact semantic parity is proven.

    No current tool meets that contract.  In particular, this language's
    object-local ambient-hole semantics are not equivalent to Block 9's
    canvas-global ``fill_holes`` leaf for every connectivity and component
    policy.  Failing closed avoids attaching an unsound parity certificate.
    """

    if not isinstance(program, ToolProgram):
        raise TypeError("program must be a ToolProgram")
    return None


TOOL_LANGUAGE_MANIFEST = MappingProxyType({
    "schema": "komorebi.lasm_action.tool_language_manifest",
    "schema_version": SCHEMA_VERSION,
    "selectors": SELECTORS,
    "relations": RELATIONS,
    "geometries": GEOMETRIES,
    "effects": EFFECTS,
    "closures": CLOSURES,
})
TOOL_LANGUAGE_HASH = sha256_record(TOOL_LANGUAGE_MANIFEST)


__all__ = [
    "CLOSURES",
    "CompleteToolRouteResult",
    "EFFECTS",
    "GEOMETRIES",
    "RELATIONS",
    "SELECTORS",
    "TOOL_LANGUAGE_HASH",
    "TOOL_LANGUAGE_MANIFEST",
    "ToolCandidate",
    "ToolProgram",
    "ToolSynthesisLimits",
    "ToolSynthesisResult",
    "RouteCompletionCertificate",
    "execute_tool",
    "lower_to_block9_leaf",
    "propose_tool_programs",
    "synthesize_tools",
    "synthesize_complete_scene_native_tools",
    "tool_applicable",
]
