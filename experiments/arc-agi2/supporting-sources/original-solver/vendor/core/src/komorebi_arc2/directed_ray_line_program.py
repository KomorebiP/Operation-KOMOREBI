"""Bounded typed programs for directed ARC rays and line recurrences.

The compiler exposes three task-identifier-free schemas:

* recolor a pivot-adjacent cardinal arm and copy it through a learned
  clockwise or counter-clockwise quarter turn;
* erase a straight 8-connected segment and draw its length-plus-one
  successor immediately beyond a learned forward endpoint; and
* upscale payload cells to two-by-two blocks and emit source-relative
  bidirectional diagonal paint rays through those blocks.

All learned fields are scalar role bindings or relative directions.  Programs
contain no raster, absolute coordinate, task identifier, or test-derived
value.  Compilation requires exact demonstration replay, conservative support
witnesses, unanimous exact-program test behavior, and leave-one-distinct-
nonidentity-group-out reinduction of the identical canonical program.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
from typing import Dict, Mapping, Optional, Sequence, Tuple

import numpy as np


Array = np.ndarray
Cell = Tuple[int, int]
Vector = Tuple[int, int]

SCHEMA = "komorebi.arc.directed-ray-line-program.v1"
SCHEMA_VERSION = 1
FAMILY = "causal_directed_ray_line"

PIVOTED_CARDINAL_ARM_QUARTER_TURN_RECOLOR = (
    "pivoted_cardinal_arm_quarter_turn_recolor"
)
SUCCESSOR_SEGMENT_ADVANCE = "successor_segment_advance"
UPSCALE2_BLOCKS_DIAGONAL_RAYS = (
    "upscale2_blocks_bidirectional_diagonal_rays"
)

_OPERATORS = (
    PIVOTED_CARDINAL_ARM_QUARTER_TURN_RECOLOR,
    SUCCESSOR_SEGMENT_ADVANCE,
    UPSCALE2_BLOCKS_DIAGONAL_RAYS,
)
_COMPLEXITIES = {
    PIVOTED_CARDINAL_ARM_QUARTER_TURN_RECOLOR: 24,
    SUCCESSOR_SEGMENT_ADVANCE: 20,
    UPSCALE2_BLOCKS_DIAGONAL_RAYS: 22,
}
_CARDINAL_VECTORS: Dict[str, Vector] = {
    "north": (-1, 0),
    "east": (0, 1),
    "south": (1, 0),
    "west": (0, -1),
}
_UNIT_VECTORS: Dict[str, Vector] = {
    "north": (-1, 0),
    "north_east": (-1, 1),
    "east": (0, 1),
    "south_east": (1, 1),
    "south": (1, 0),
    "south_west": (1, -1),
    "west": (0, -1),
    "north_west": (-1, -1),
}
_HANDEDNESSES = ("clockwise", "counter_clockwise")
_MAIN_DIAGONAL = "north_west_south_east"
_ANTI_DIAGONAL = "north_east_south_west"
_UPSCALE_DIAGONALS = (_MAIN_DIAGONAL, _ANTI_DIAGONAL)


class DirectedRayLineError(ValueError):
    """Base class for invalid programs and bounded execution failures."""


class DirectedRayLineAbstention(DirectedRayLineError):
    """Raised when a source does not have one protected interpretation."""


class DirectedRayLineAmbiguityError(DirectedRayLineAbstention):
    """Raised when exact schemas predict divergent held-out behavior."""


class DirectedRayLineLimitError(DirectedRayLineError):
    """Raised before a configured finite resource budget is exceeded."""


@dataclass(frozen=True)
class DirectedRayLineLimits:
    """Hard raster, grammar, and execution limits."""

    maximum_height: int = 30
    maximum_width: int = 30
    maximum_cells: int = 900
    maximum_palette: int = 10
    maximum_examples: int = 10
    maximum_tests: int = 8
    maximum_programs: int = 512
    maximum_exact_programs: int = 32
    maximum_test_behaviors: int = 16
    maximum_payload_cells: int = 225
    maximum_ray_cells: int = 900

    def __post_init__(self) -> None:
        for name, value in asdict(self).items():
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, np.integer))
                or int(value) <= 0
            ):
                raise DirectedRayLineLimitError(
                    f"{name} must be a positive integer"
                )

    def to_record(self) -> Dict[str, int]:
        return {name: int(value) for name, value in asdict(self).items()}


DEFAULT_LIMITS = DirectedRayLineLimits()


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def directed_ray_line_implementation_fingerprint() -> str:
    """Hash the exact standalone interpreter and compiler source."""

    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def _validated_optional_color(name: str, value: object) -> Optional[int]:
    if value is None:
        return None
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, np.integer))
        or not 0 <= int(value) <= 9
    ):
        raise DirectedRayLineError(
            f"{name} must be null or one ARC palette integer"
        )
    return int(value)


@dataclass(frozen=True)
class DirectedRayLineProgram:
    """Canonical operator plus bounded demonstration-inferred role fields."""

    operator: str
    anchor_color: Optional[int] = None
    payload_color: Optional[int] = None
    paint_color: Optional[int] = None
    orientation: Optional[str] = None
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        if (
            isinstance(self.schema_version, bool)
            or not isinstance(self.schema_version, (int, np.integer))
            or int(self.schema_version) != SCHEMA_VERSION
        ):
            raise DirectedRayLineError(
                f"unsupported schema version {self.schema_version!r}; "
                f"expected {SCHEMA_VERSION}"
            )
        if self.operator not in _OPERATORS:
            raise DirectedRayLineError(
                f"unknown directed-ray operator {self.operator!r}"
            )
        anchor = _validated_optional_color("anchor_color", self.anchor_color)
        payload = _validated_optional_color(
            "payload_color", self.payload_color
        )
        paint = _validated_optional_color("paint_color", self.paint_color)
        orientation = self.orientation
        if orientation is not None and not isinstance(orientation, str):
            raise DirectedRayLineError("orientation must be null or a string")

        if self.operator == PIVOTED_CARDINAL_ARM_QUARTER_TURN_RECOLOR:
            if anchor is None or payload is None or paint is None:
                raise DirectedRayLineError(
                    "pivoted-arm programs require three learned color roles"
                )
            if len({anchor, payload, paint}) != 3:
                raise DirectedRayLineError(
                    "pivot, payload, and trail colors must be distinct"
                )
            if orientation not in _HANDEDNESSES:
                raise DirectedRayLineError(
                    "pivoted-arm orientation must be a quarter-turn handedness"
                )
        elif self.operator == SUCCESSOR_SEGMENT_ADVANCE:
            if any(value is not None for value in (anchor, payload, paint)):
                raise DirectedRayLineError(
                    "successor-segment programs bind colors from each source"
                )
            if orientation not in _UNIT_VECTORS:
                raise DirectedRayLineError(
                    "successor-segment orientation must be one unit direction"
                )
        else:
            if anchor is not None or payload is not None or paint is None:
                raise DirectedRayLineError(
                    "upscale-ray programs store only the learned paint color"
                )
            if orientation not in _UPSCALE_DIAGONALS:
                raise DirectedRayLineError(
                    "upscale-ray orientation must be one diagonal axis"
                )

        object.__setattr__(self, "schema_version", SCHEMA_VERSION)
        object.__setattr__(self, "anchor_color", anchor)
        object.__setattr__(self, "payload_color", payload)
        object.__setattr__(self, "paint_color", paint)
        object.__setattr__(self, "orientation", orientation)

    @classmethod
    def pivoted_arm_quarter_turn(
        cls,
        *,
        anchor_color: int,
        payload_color: int,
        paint_color: int,
        handedness: str,
    ) -> "DirectedRayLineProgram":
        return cls(
            operator=PIVOTED_CARDINAL_ARM_QUARTER_TURN_RECOLOR,
            anchor_color=anchor_color,
            payload_color=payload_color,
            paint_color=paint_color,
            orientation=handedness,
        )

    @classmethod
    def successor_segment(cls, direction: str) -> "DirectedRayLineProgram":
        return cls(
            operator=SUCCESSOR_SEGMENT_ADVANCE,
            orientation=direction,
        )

    @classmethod
    def upscale_blocks_diagonal_rays(
        cls,
        paint_color: int,
        orientation: str = _MAIN_DIAGONAL,
    ) -> "DirectedRayLineProgram":
        return cls(
            operator=UPSCALE2_BLOCKS_DIAGONAL_RAYS,
            paint_color=paint_color,
            orientation=orientation,
        )

    @classmethod
    def from_record(cls, raw: object) -> "DirectedRayLineProgram":
        if not isinstance(raw, Mapping):
            raise DirectedRayLineError(
                "directed-ray-line program must be a mapping"
            )
        expected = {
            "schema",
            "schema_version",
            "operator",
            "anchor_color",
            "payload_color",
            "paint_color",
            "orientation",
        }
        present = set(raw)
        if present != expected:
            raise DirectedRayLineError(
                "directed-ray-line program fields do not match schema; "
                f"missing={sorted(expected - present)}, "
                f"extra={sorted(present - expected)}"
            )
        if raw["schema"] != SCHEMA:
            raise DirectedRayLineError(
                f"unknown directed-ray-line schema {raw['schema']!r}"
            )
        return cls(
            operator=str(raw["operator"]),
            anchor_color=raw["anchor_color"],
            payload_color=raw["payload_color"],
            paint_color=raw["paint_color"],
            orientation=raw["orientation"],
            schema_version=raw["schema_version"],
        )

    def to_record(self) -> Dict[str, object]:
        record: Dict[str, object] = {
            "schema": SCHEMA,
            "schema_version": int(self.schema_version),
            "operator": str(self.operator),
            "anchor_color": self.anchor_color,
            "payload_color": self.payload_color,
            "paint_color": self.paint_color,
            "orientation": self.orientation,
        }
        _canonical_json(record)
        return record

    @property
    def semantic_key(self) -> str:
        return _canonical_json(self.to_record())

    def program_hash(self) -> str:
        return hashlib.sha256(self.semantic_key.encode("ascii")).hexdigest()

    def content_hash(self) -> str:
        return self.program_hash()

    @property
    def complexity(self) -> int:
        return int(_COMPLEXITIES[self.operator])

    def apply(
        self,
        grid: Array,
        *,
        limits: "DirectedRayLineLimits" = DEFAULT_LIMITS,
    ) -> Array:
        return execute_directed_ray_line_program(self, grid, limits=limits)


@dataclass(frozen=True)
class DirectedRayLineTrace:
    """Coordinate-free runtime evidence for one rebound source scene."""

    operator: str
    background_color: int
    source_shape: Tuple[int, int]
    output_shape: Tuple[int, int]
    direction: str
    source_length: int = 0
    target_length: int = 0
    payload_cell_count: int = 0
    payload_component_count: int = 0
    block_cell_count: int = 0
    ray_cell_count: int = 0
    bidirectional_payload_count: int = 0
    changed_cell_count: int = 0
    anchor_color: Optional[int] = None
    payload_color: Optional[int] = None
    paint_color: Optional[int] = None

    def to_record(self) -> Dict[str, object]:
        return {
            "operator": str(self.operator),
            "background_color": int(self.background_color),
            "source_shape": [int(value) for value in self.source_shape],
            "output_shape": [int(value) for value in self.output_shape],
            "direction": str(self.direction),
            "source_length": int(self.source_length),
            "target_length": int(self.target_length),
            "payload_cell_count": int(self.payload_cell_count),
            "payload_component_count": int(self.payload_component_count),
            "block_cell_count": int(self.block_cell_count),
            "ray_cell_count": int(self.ray_cell_count),
            "bidirectional_payload_count": int(
                self.bidirectional_payload_count
            ),
            "changed_cell_count": int(self.changed_cell_count),
            "anchor_color": self.anchor_color,
            "payload_color": self.payload_color,
            "paint_color": self.paint_color,
        }


@dataclass(frozen=True)
class DirectedRayLineCandidate:
    """Entry-independent exact candidate with canonical provenance."""

    name: str
    program: DirectedRayLineProgram
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
            "metadata": dict(self.metadata),
        }
        if include_grids:
            record["grids"] = [
                grid.astype(int).tolist() for grid in self.grids
            ]
            record["train_grids"] = [
                grid.astype(int).tolist() for grid in self.train_grids
            ]
        _canonical_json(record)
        return record


def _validated_grid(grid: Array, limits: DirectedRayLineLimits) -> Array:
    try:
        raw = np.asarray(grid)
    except (TypeError, ValueError) as error:
        raise DirectedRayLineAbstention(
            "grid must be a rectangular numeric raster"
        ) from error
    if raw.ndim != 2 or raw.size == 0:
        raise DirectedRayLineAbstention("grid must be a nonempty matrix")
    if np.issubdtype(raw.dtype, np.bool_) or not np.issubdtype(
        raw.dtype, np.integer
    ):
        raise DirectedRayLineAbstention("grid values must be integers")
    height, width = raw.shape
    if (
        height > limits.maximum_height
        or width > limits.maximum_width
        or raw.size > limits.maximum_cells
    ):
        raise DirectedRayLineLimitError(
            "grid exceeds ARC representation limits"
        )
    values = np.asarray(raw, dtype=np.int64)
    palette = np.unique(values)
    if len(palette) > limits.maximum_palette:
        raise DirectedRayLineLimitError(
            "palette exceeds representation limit"
        )
    if np.any(palette < 0) or np.any(palette > 9):
        raise DirectedRayLineAbstention(
            "grid colors must lie in the ARC palette"
        )
    return np.ascontiguousarray(values, dtype=np.int16)


def _background(source: Array) -> int:
    colors, counts = np.unique(source, return_counts=True)
    maximum = int(counts.max())
    winners = colors[counts == maximum]
    if len(winners) != 1:
        raise DirectedRayLineAmbiguityError(
            "global background mode is not unique"
        )
    return int(winners[0])


def _vector_name(vector: Vector, table: Mapping[str, Vector]) -> str:
    names = [name for name, value in table.items() if value == vector]
    if len(names) != 1:
        raise DirectedRayLineError(f"unknown direction vector {vector!r}")
    return names[0]


def _turned(vector: Vector, handedness: str) -> Vector:
    row, column = vector
    if handedness == "clockwise":
        return column, -row
    if handedness == "counter_clockwise":
        return -column, row
    raise DirectedRayLineError(f"unknown handedness {handedness!r}")


def _pivoted_arm_trace(
    program: DirectedRayLineProgram,
    source: Array,
) -> Tuple[Array, DirectedRayLineTrace]:
    background = _background(source)
    anchor = int(program.anchor_color)  # validated by the program
    payload = int(program.payload_color)
    paint = int(program.paint_color)
    if background in {anchor, payload, paint}:
        raise DirectedRayLineAbstention(
            "learned role colors collide with the rebound background"
        )
    if set(int(value) for value in np.unique(source)) != {
        background,
        anchor,
        payload,
    }:
        raise DirectedRayLineAbstention(
            "pivoted-arm source must contain exactly its three source roles"
        )
    if bool(np.any(source == paint)):
        raise DirectedRayLineAbstention(
            "trail color must be absent from the source"
        )
    anchors = np.argwhere(source == anchor)
    if len(anchors) != 1:
        raise DirectedRayLineAbstention(
            "pivot role must be represented by one singleton"
        )
    pivot = tuple(int(value) for value in anchors[0])
    payload_cells = {
        (int(row), int(column))
        for row, column in np.argwhere(source == payload)
    }
    if not payload_cells:
        raise DirectedRayLineAbstention("payload arm is empty")
    directions = []
    length = len(payload_cells)
    for name, (delta_row, delta_column) in _CARDINAL_VECTORS.items():
        expected = {
            (
                pivot[0] + distance * delta_row,
                pivot[1] + distance * delta_column,
            )
            for distance in range(1, length + 1)
        }
        if expected == payload_cells:
            directions.append(name)
    if len(directions) != 1:
        raise DirectedRayLineAmbiguityError(
            "payload must be one gapless pivot-adjacent cardinal arm"
        )
    source_direction = directions[0]
    target_vector = _turned(
        _CARDINAL_VECTORS[source_direction],
        str(program.orientation),
    )
    target_direction = _vector_name(target_vector, _CARDINAL_VECTORS)
    height, width = source.shape
    targets = {
        (
            pivot[0] + distance * target_vector[0],
            pivot[1] + distance * target_vector[1],
        )
        for distance in range(1, length + 1)
    }
    if any(
        not (0 <= row < height and 0 <= column < width)
        for row, column in targets
    ):
        raise DirectedRayLineAbstention(
            "turned arm exceeds the output workspace"
        )
    if any(int(source[cell]) != background for cell in targets):
        raise DirectedRayLineAbstention(
            "turned arm collides with a nonbackground cell"
        )
    output = source.copy()
    for cell in payload_cells:
        output[cell] = paint
    for cell in targets:
        output[cell] = payload
    return (
        np.ascontiguousarray(output),
        DirectedRayLineTrace(
            operator=program.operator,
            background_color=background,
            source_shape=tuple(int(value) for value in source.shape),
            output_shape=tuple(int(value) for value in output.shape),
            direction=f"{source_direction}_to_{target_direction}",
            source_length=length,
            target_length=length,
            payload_cell_count=length,
            changed_cell_count=2 * length,
            anchor_color=anchor,
            payload_color=payload,
            paint_color=paint,
        ),
    )


def _successor_segment_trace(
    program: DirectedRayLineProgram,
    source: Array,
) -> Tuple[Array, DirectedRayLineTrace]:
    background = _background(source)
    colors = [
        int(value) for value in np.unique(source) if int(value) != background
    ]
    if len(colors) != 1:
        raise DirectedRayLineAbstention(
            "successor source must contain one foreground color"
        )
    foreground = colors[0]
    cells = {
        (int(row), int(column))
        for row, column in np.argwhere(source == foreground)
    }
    if not cells:
        raise DirectedRayLineAbstention("successor segment is empty")
    direction = str(program.orientation)
    delta_row, delta_column = _UNIT_VECTORS[direction]
    endpoints = [
        cell
        for cell in cells
        if (
            cell[0] + delta_row,
            cell[1] + delta_column,
        )
        not in cells
    ]
    if len(endpoints) != 1:
        raise DirectedRayLineAmbiguityError(
            "segment has no unique forward endpoint"
        )
    forward = endpoints[0]
    length = len(cells)
    expected = {
        (
            forward[0] - distance * delta_row,
            forward[1] - distance * delta_column,
        )
        for distance in range(length)
    }
    if expected != cells:
        raise DirectedRayLineAbstention(
            "foreground is not one gapless straight unit-step segment"
        )
    targets = {
        (
            forward[0] + distance * delta_row,
            forward[1] + distance * delta_column,
        )
        for distance in range(1, length + 2)
    }
    height, width = source.shape
    if any(
        not (0 <= row < height and 0 <= column < width)
        for row, column in targets
    ):
        raise DirectedRayLineAbstention(
            "successor segment exceeds the output workspace"
        )
    if cells.intersection(targets):
        raise DirectedRayLineAbstention(
            "successor segment must advance without overlap"
        )
    if any(int(source[cell]) != background for cell in targets):
        raise DirectedRayLineAbstention(
            "successor segment collides with a nonbackground cell"
        )
    output = np.full(source.shape, background, dtype=np.int16)
    for cell in targets:
        output[cell] = foreground
    return (
        np.ascontiguousarray(output),
        DirectedRayLineTrace(
            operator=program.operator,
            background_color=background,
            source_shape=tuple(int(value) for value in source.shape),
            output_shape=tuple(int(value) for value in output.shape),
            direction=direction,
            source_length=length,
            target_length=length + 1,
            payload_cell_count=length,
            changed_cell_count=2 * length + 1,
            payload_color=foreground,
        ),
    )


def _upscale_diagonal_rays_trace(
    program: DirectedRayLineProgram,
    source: Array,
    limits: DirectedRayLineLimits,
) -> Tuple[Array, DirectedRayLineTrace]:
    background = _background(source)
    colors = [
        int(value) for value in np.unique(source) if int(value) != background
    ]
    if len(colors) != 1:
        raise DirectedRayLineAbstention(
            "upscale-ray source must contain one payload color"
        )
    payload = colors[0]
    paint = int(program.paint_color)
    if paint in {background, payload} or bool(np.any(source == paint)):
        raise DirectedRayLineAbstention(
            "ray paint must be novel relative to the source roles"
        )
    payload_cells = [
        (int(row), int(column))
        for row, column in np.argwhere(source == payload)
    ]
    if not payload_cells:
        raise DirectedRayLineAbstention("upscale payload is empty")
    if len(payload_cells) > limits.maximum_payload_cells:
        raise DirectedRayLineLimitError(
            "payload count exceeds execution limit"
        )
    remaining = set(payload_cells)
    payload_component_count = 0
    while remaining:
        payload_component_count += 1
        stack = [remaining.pop()]
        while stack:
            current_row, current_column = stack.pop()
            for delta_row in (-1, 0, 1):
                for delta_column in (-1, 0, 1):
                    if delta_row == 0 and delta_column == 0:
                        continue
                    neighbor = (
                        current_row + delta_row,
                        current_column + delta_column,
                    )
                    if neighbor in remaining:
                        remaining.remove(neighbor)
                        stack.append(neighbor)
    height, width = source.shape
    output_height = 2 * height
    output_width = 2 * width
    if (
        output_height > limits.maximum_height
        or output_width > limits.maximum_width
        or output_height * output_width > limits.maximum_cells
    ):
        raise DirectedRayLineLimitError(
            "two-times upscale output exceeds representation limits"
        )
    output = np.full(
        (output_height, output_width),
        background,
        dtype=np.int16,
    )
    for row, column in payload_cells:
        output[
            2 * row : 2 * row + 2,
            2 * column : 2 * column + 2,
        ] = payload
    ray_cells: set[Cell] = set()
    for row, column in payload_cells:
        for output_row in range(output_height):
            if program.orientation == _MAIN_DIAGONAL:
                diagonal_offset = 2 * (row - column)
                output_column = output_row - diagonal_offset
            else:
                diagonal_sum = 2 * (row + column) + 1
                output_column = diagonal_sum - output_row
            if (
                0 <= output_column < output_width
                and int(output[output_row, output_column]) == background
            ):
                ray_cells.add((output_row, output_column))
                if len(ray_cells) > limits.maximum_ray_cells:
                    raise DirectedRayLineLimitError(
                        "diagonal ray cell count exceeds execution limit"
                    )
    if not ray_cells:
        raise DirectedRayLineAbstention(
            "upscale blocks leave no observable diagonal ray"
        )
    bidirectional_payload_count = 0
    for row, column in payload_cells:
        if program.orientation == _MAIN_DIAGONAL:
            own_ray = {
                cell
                for cell in ray_cells
                if cell[0] - cell[1] == 2 * (row - column)
            }
        else:
            own_ray = {
                cell
                for cell in ray_cells
                if cell[0] + cell[1] == 2 * (row + column) + 1
            }
        if any(cell[0] < 2 * row for cell in own_ray) and any(
            cell[0] > 2 * row + 1 for cell in own_ray
        ):
            bidirectional_payload_count += 1
    for cell in ray_cells:
        output[cell] = paint
    return (
        np.ascontiguousarray(output),
        DirectedRayLineTrace(
            operator=program.operator,
            background_color=background,
            source_shape=tuple(int(value) for value in source.shape),
            output_shape=tuple(int(value) for value in output.shape),
            direction=str(program.orientation),
            payload_cell_count=len(payload_cells),
            payload_component_count=payload_component_count,
            block_cell_count=4 * len(payload_cells),
            ray_cell_count=len(ray_cells),
            bidirectional_payload_count=bidirectional_payload_count,
            changed_cell_count=4 * len(payload_cells) + len(ray_cells),
            payload_color=payload,
            paint_color=paint,
        ),
    )


def _execute_with_trace(
    program: DirectedRayLineProgram,
    grid: Array,
    limits: DirectedRayLineLimits,
) -> Tuple[Array, DirectedRayLineTrace]:
    source = _validated_grid(grid, limits)
    if program.operator == PIVOTED_CARDINAL_ARM_QUARTER_TURN_RECOLOR:
        output, trace = _pivoted_arm_trace(program, source)
    elif program.operator == SUCCESSOR_SEGMENT_ADVANCE:
        output, trace = _successor_segment_trace(program, source)
    elif program.operator == UPSCALE2_BLOCKS_DIAGONAL_RAYS:
        output, trace = _upscale_diagonal_rays_trace(
            program,
            source,
            limits,
        )
    else:
        raise DirectedRayLineError(
            f"unknown directed-ray operator {program.operator!r}"
        )
    output = _validated_grid(output, limits)
    if output.shape == source.shape and np.array_equal(output, source):
        raise DirectedRayLineAbstention("program produced no change")
    return output, trace


def execute_directed_ray_line_program(
    program: DirectedRayLineProgram | Mapping[str, object],
    grid: Array,
    *,
    limits: DirectedRayLineLimits = DEFAULT_LIMITS,
) -> Array:
    """Rebind source roles and execute one typed line program atomically."""

    if not isinstance(program, DirectedRayLineProgram):
        program = DirectedRayLineProgram.from_record(program)
    output, _ = _execute_with_trace(program, grid, limits)
    return output.copy()


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
    train: Sequence[Tuple[Array, Array]],
    limits: DirectedRayLineLimits,
) -> Tuple[Tuple[Array, Array], ...]:
    return tuple(
        (
            _validated_grid(source, limits),
            _validated_grid(target, limits),
        )
        for source, target in train
    )


def _program_grammar(
    train: Sequence[Tuple[Array, Array]],
    limits: DirectedRayLineLimits,
) -> Tuple[DirectedRayLineProgram, ...]:
    if not train:
        return ()
    source_palettes = [
        set(int(value) for value in np.unique(source))
        for source, _ in train
    ]
    target_palettes = [
        set(int(value) for value in np.unique(target))
        for _, target in train
    ]
    common_source = set.intersection(*source_palettes)
    common_target = set.intersection(*target_palettes)
    source_union = set.union(*source_palettes)
    novel_common_target = sorted(common_target - source_union)
    programs: Dict[str, DirectedRayLineProgram] = {}

    for anchor in sorted(common_source):
        for payload in sorted(common_source - {anchor}):
            for paint in novel_common_target:
                for handedness in _HANDEDNESSES:
                    program = DirectedRayLineProgram.pivoted_arm_quarter_turn(
                        anchor_color=anchor,
                        payload_color=payload,
                        paint_color=paint,
                        handedness=handedness,
                    )
                    programs[program.program_hash()] = program
    for direction in _UNIT_VECTORS:
        program = DirectedRayLineProgram.successor_segment(direction)
        programs[program.program_hash()] = program
    for paint in novel_common_target:
        for orientation in _UPSCALE_DIAGONALS:
            program = DirectedRayLineProgram.upscale_blocks_diagonal_rays(
                paint,
                orientation,
            )
            programs[program.program_hash()] = program

    ordered = tuple(
        sorted(
            programs.values(),
            key=lambda program: (program.complexity, program.semantic_key),
        )
    )
    if len(ordered) > limits.maximum_programs:
        raise DirectedRayLineLimitError(
            f"program grammar has {len(ordered)} entries; "
            f"limit is {limits.maximum_programs}"
        )
    return ordered


def _exact_program_predictions(
    train: Sequence[Tuple[Array, Array]],
    programs: Sequence[DirectedRayLineProgram],
    limits: DirectedRayLineLimits,
) -> Dict[str, Tuple[DirectedRayLineProgram, Tuple[Array, ...]]]:
    exact: Dict[
        str,
        Tuple[DirectedRayLineProgram, Tuple[Array, ...]],
    ] = {}
    for program in programs:
        predictions = []
        try:
            for source, target in train:
                prediction = program.apply(source, limits=limits)
                if not np.array_equal(prediction, target):
                    break
                predictions.append(prediction)
            else:
                exact[program.program_hash()] = (
                    program,
                    tuple(predictions),
                )
                if len(exact) > limits.maximum_exact_programs:
                    raise DirectedRayLineLimitError(
                        "exact-program count exceeds grammar limit"
                    )
        except DirectedRayLineError:
            continue
    return exact


def _discover_unique_exact_program(
    train: Sequence[Tuple[Array, Array]],
    limits: DirectedRayLineLimits,
) -> Optional[Tuple[DirectedRayLineProgram, Tuple[Array, ...]]]:
    programs = _program_grammar(train, limits)
    exact = _exact_program_predictions(train, programs, limits)
    if len(exact) != 1:
        return None
    return next(iter(exact.values()))


def _support_record(
    program: DirectedRayLineProgram,
    train: Sequence[Tuple[Array, Array]],
    limits: DirectedRayLineLimits,
) -> Optional[Tuple[Dict[str, object], Tuple[DirectedRayLineTrace, ...]]]:
    traces = []
    try:
        for source, _ in train:
            _, trace = _execute_with_trace(program, source, limits)
            traces.append(trace)
    except DirectedRayLineError:
        return None
    if program.operator == PIVOTED_CARDINAL_ARM_QUARTER_TURN_RECOLOR:
        incoming = {
            trace.direction.split("_to_", 1)[0] for trace in traces
        }
        lengths = {trace.source_length for trace in traces}
        if incoming != set(_CARDINAL_VECTORS) or len(lengths) < 2:
            return None
        return (
            {
                "all_four_cardinal_source_directions_witnessed": True,
                "source_direction_count": int(len(incoming)),
                "ray_length_variation": int(len(lengths)),
                "singleton_ray_witnessed": bool(1 in lengths),
                "nonsingleton_ray_witnessed": bool(
                    any(length > 1 for length in lengths)
                ),
                "handedness": str(program.orientation),
            },
            tuple(traces),
        )
    if program.operator == SUCCESSOR_SEGMENT_ADVANCE:
        lengths = sorted({trace.source_length for trace in traces})
        if (
            len(lengths) < 3
            or lengths[0] != 1
            or lengths != list(range(lengths[0], lengths[-1] + 1))
        ):
            return None
        return (
            {
                "source_length_variation": int(len(lengths)),
                "consecutive_lengths_from_one_witnessed": True,
                "length_increment": 1,
                "erase_source_segment": True,
                "forward_direction": str(program.orientation),
            },
            tuple(traces),
        )
    payload_colors = {trace.payload_color for trace in traces}
    source_shapes = {trace.source_shape for trace in traces}
    total_payload = sum(trace.payload_cell_count for trace in traces)
    bidirectional = any(
        trace.bidirectional_payload_count > 0 for trace in traces
    )
    disconnected_payload = any(
        trace.payload_component_count >= 2 for trace in traces
    )
    if (
        len(payload_colors) < 3
        or len(source_shapes) < 3
        or total_payload < 6
        or not all(trace.ray_cell_count > 0 for trace in traces)
        or not bidirectional
        or not disconnected_payload
    ):
        return None
    return (
        {
            "payload_color_variation": int(len(payload_colors)),
            "source_shape_variation": int(len(source_shapes)),
            "total_payload_instances": int(total_payload),
            "observable_ray_in_every_demonstration": True,
            "bidirectional_ray_witnessed": True,
            "disconnected_payload_components_witnessed": True,
            "payload_connectivity": 8,
            "scale_factor": 2,
            "ray_orientation": str(program.orientation),
        },
        tuple(traces),
    )


def _minimum_groups(operator: str) -> int:
    if operator == PIVOTED_CARDINAL_ARM_QUARTER_TURN_RECOLOR:
        return 4
    return 3


def compile_directed_ray_line_programs(
    train: Sequence[Tuple[Array, Array]],
    tests: Sequence[Array],
    *,
    limits: DirectedRayLineLimits = DEFAULT_LIMITS,
) -> Tuple[DirectedRayLineCandidate, ...]:
    """Compile one exact, supported, LOO-stable typed line program."""

    if len(train) < 3 or not tests:
        return ()
    if len(train) > limits.maximum_examples or len(tests) > limits.maximum_tests:
        raise DirectedRayLineLimitError("example budget exceeded")
    try:
        validated = _validated_train(train, limits)
        validated_tests = tuple(
            _validated_grid(test, limits) for test in tests
        )
    except DirectedRayLineAbstention:
        return ()

    groups: Dict[str, list[int]] = {}
    for index, (source, target) in enumerate(validated):
        if np.array_equal(source, target):
            continue
        groups.setdefault(_example_hash(source, target), []).append(index)
    if len(groups) < 3:
        return ()

    programs = _program_grammar(validated, limits)
    full_exact = _exact_program_predictions(validated, programs, limits)
    supported: Dict[
        str,
        Tuple[
            DirectedRayLineProgram,
            Tuple[Array, ...],
            Dict[str, object],
            Tuple[DirectedRayLineTrace, ...],
        ],
    ] = {}
    for program_hash, (program, predictions) in full_exact.items():
        if len(groups) < _minimum_groups(program.operator):
            continue
        support_result = _support_record(program, validated, limits)
        if support_result is None:
            continue
        support, traces = support_result
        supported[program_hash] = (
            program,
            predictions,
            support,
            traces,
        )
    if not supported:
        return ()

    exact_test_behaviors: Dict[str, list[str]] = {}
    predictions_by_hash: Dict[str, Tuple[Array, ...]] = {}
    for program_hash, (program, _, _, _) in sorted(supported.items()):
        try:
            predictions = tuple(
                program.apply(test, limits=limits)
                for test in validated_tests
            )
        except DirectedRayLineError:
            return ()
        behavior = _behavior_hash(predictions)
        exact_test_behaviors.setdefault(behavior, []).append(program_hash)
        predictions_by_hash[program_hash] = predictions
    if len(exact_test_behaviors) > limits.maximum_test_behaviors:
        raise DirectedRayLineLimitError(
            "exact test behavior-class count exceeds limit"
        )
    if len(exact_test_behaviors) != 1:
        raise DirectedRayLineAmbiguityError(
            "full-data-exact directed-ray programs predict divergent tests"
        )
    program_hash, selected = min(
        supported.items(),
        key=lambda item: (item[1][0].complexity, item[1][0].semantic_key),
    )
    program, train_predictions, support, traces = selected

    loo_program_hashes = []
    loo_exact_count = 0
    for group_hash in sorted(groups):
        indices = groups[group_hash]
        excluded = set(indices)
        construction = tuple(
            pair
            for index, pair in enumerate(validated)
            if index not in excluded
        )
        rediscovered = _discover_unique_exact_program(construction, limits)
        if rediscovered is None:
            break
        fold_program = rediscovered[0]
        fold_hash = fold_program.program_hash()
        loo_program_hashes.append(fold_hash)
        if fold_hash != program_hash:
            break
        try:
            exact_group = all(
                np.array_equal(
                    fold_program.apply(validated[index][0], limits=limits),
                    validated[index][1],
                )
                for index in indices
            )
        except DirectedRayLineError:
            break
        if not exact_group:
            break
        loo_exact_count += 1
    if loo_exact_count != len(groups):
        return ()

    output_shape_contracts = {
        PIVOTED_CARDINAL_ARM_QUARTER_TURN_RECOLOR: "same_as_input",
        SUCCESSOR_SEGMENT_ADVANCE: "same_as_input",
        UPSCALE2_BLOCKS_DIAGONAL_RAYS: "two_times_input_each_axis",
    }
    literal_color_free = program.operator == SUCCESSOR_SEGMENT_ADVANCE
    metadata: Dict[str, object] = {
        "schema": "komorebi.arc.directed-ray-line-candidate.v1",
        "program": program.to_record(),
        "program_hash": program_hash,
        "semantic_key": program.semantic_key,
        "operator": program.operator,
        "background_binding": "unique_global_mode",
        "output_shape_contract": output_shape_contracts[program.operator],
        "exact_demonstration_contract": True,
        "test_target_isolation": True,
        "test_input_grounded": True,
        "task_identifier_free": True,
        "raw_grid_free_program": True,
        "literal_coordinate_free_program": True,
        "literal_color_free_program": bool(literal_color_free),
        "learned_color_roles_are_demonstration_inferred": bool(
            not literal_color_free
        ),
        "whole_task_palette_equivariant_compiler": True,
        "atomic_collision_abstention": True,
        "unique_source_interpretation": True,
        "d4_equivariant_program": False,
        "witness_protocol": (
            "leave_one_distinct_nonidentity_group_out_reinduction"
        ),
        "discovery_protocol": (
            "canonical_minimum_description_exact_typed_program"
        ),
        "distinct_witness_groups": int(len(groups)),
        "distinct_nonidentity_witness_groups": int(len(groups)),
        "loo_exact_count": int(loo_exact_count),
        "loo_total_count": int(len(groups)),
        "loo_program_hashes": list(loo_program_hashes),
        "full_exact_program_count": int(len(full_exact)),
        "supported_exact_program_count": int(len(supported)),
        "exact_test_behavior_count": int(len(exact_test_behaviors)),
        "support": support,
        "training_trace_summary": [trace.to_record() for trace in traces],
        "witness_reconstructible": True,
        "empirical_promotion_eligible": False,
        "external_gain_loss_audit": False,
        "implementation_fingerprint": (
            directed_ray_line_implementation_fingerprint()
        ),
        "bounded_program_count": int(len(programs)),
        "limits": limits.to_record(),
    }
    return (
        DirectedRayLineCandidate(
            name=(
                f"directed_ray_line:{program.operator}:"
                f"{program_hash[:12]}"
            ),
            program=program,
            grids=tuple(
                np.ascontiguousarray(grid)
                for grid in predictions_by_hash[program_hash]
            ),
            train_grids=tuple(
                np.ascontiguousarray(grid) for grid in train_predictions
            ),
            complexity=program.complexity,
            metadata=metadata,
        ),
    )


directed_ray_line_candidates = compile_directed_ray_line_programs


__all__ = [
    "DEFAULT_LIMITS",
    "FAMILY",
    "PIVOTED_CARDINAL_ARM_QUARTER_TURN_RECOLOR",
    "SCHEMA",
    "SUCCESSOR_SEGMENT_ADVANCE",
    "UPSCALE2_BLOCKS_DIAGONAL_RAYS",
    "DirectedRayLineAbstention",
    "DirectedRayLineAmbiguityError",
    "DirectedRayLineCandidate",
    "DirectedRayLineError",
    "DirectedRayLineLimitError",
    "DirectedRayLineLimits",
    "DirectedRayLineProgram",
    "DirectedRayLineTrace",
    "compile_directed_ray_line_programs",
    "directed_ray_line_candidates",
    "directed_ray_line_implementation_fingerprint",
    "execute_directed_ray_line_program",
]
