"""Bounded typed programs for two multi-object role-allocation schemas.

The module deliberately contains no task identifiers, memorized rasters, or
literal coordinates.  It supports two fixed, source-grounded interpreters:

* a filled rectangle with two singleton tokens on one side.  The follower
  token takes the leader's old position and the leader moves to the opposite
  edge's lateral exterior corner, away from the follower;
* four coloured objects around one rectangular background void.  The unique
  largest object gains a three-cell outer cap while the other three objects
  lose their unique inward tips.

Compilation is fail closed.  Every demonstration must replay exactly, at
least three distinct nonidentity source/target groups are required, and each
duplicate-collapsed group must survive leave-one-group-out reinduction.  Test
grids are interpreted independently under hard ARC representation limits.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import itertools
import json
from pathlib import Path
from typing import Dict, Mapping, Optional, Sequence, Tuple

import numpy as np


Array = np.ndarray
Cell = Tuple[int, int]
Box = Tuple[int, int, int, int]

SCHEMA = "komorebi.arc.multi-object-role-allocation-program.v1"
SCHEMA_VERSION = 1
FAMILY = "causal_multi_object_role_allocation"
RECTANGLE_HANDOFF_OPERATOR = "rectangle_opposite_side_singleton_handoff"
CARDINAL_VOID_OPERATOR = (
    "cardinal_void_largest_outer_cap_else_remove_inward_tip"
)
_OPERATORS = {RECTANGLE_HANDOFF_OPERATOR, CARDINAL_VOID_OPERATOR}


class MultiObjectRoleAllocationError(ValueError):
    """Base class for invalid programs and explicit abstentions."""


class MultiObjectRoleAllocationAbstention(MultiObjectRoleAllocationError):
    """Raised when a source has no unique protected interpretation."""


class MultiObjectRoleAllocationLimitError(MultiObjectRoleAllocationError):
    """Raised before a finite representation budget is exceeded."""


@dataclass(frozen=True)
class MultiObjectRoleAllocationLimits:
    """Hard limits for the compiler and both interpreters."""

    maximum_height: int = 30
    maximum_width: int = 30
    maximum_cells: int = 900
    maximum_palette: int = 10
    maximum_components: int = 256
    maximum_component_cells: int = 900
    maximum_void_cells: int = 225
    maximum_examples: int = 10
    maximum_tests: int = 8
    minimum_distinct_nonidentity_groups: int = 3

    def __post_init__(self) -> None:
        for name, value in asdict(self).items():
            if type(value) is not int or value <= 0:
                raise MultiObjectRoleAllocationLimitError(
                    f"{name} must be a positive native integer"
                )

    def to_record(self) -> Dict[str, int]:
        return {name: int(value) for name, value in asdict(self).items()}


DEFAULT_LIMITS = MultiObjectRoleAllocationLimits()


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def multi_object_role_allocation_implementation_fingerprint() -> str:
    """Return a hash of the exact standalone compiler implementation."""

    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def _native_schema_int(value: object, name: str) -> int:
    if type(value) is not int:
        raise MultiObjectRoleAllocationError(f"{name} must be a native integer")
    return value


def _arc_color(value: object, name: str) -> int:
    result = _native_schema_int(value, name)
    if not 0 <= result <= 9:
        raise MultiObjectRoleAllocationError(
            f"{name} must be one ARC palette integer"
        )
    return result


@dataclass(frozen=True)
class MultiObjectRoleAllocationProgram:
    """Canonical role program; only the handoff binds learned colour roles."""

    operator: str
    follower_color: Optional[int] = None
    leader_color: Optional[int] = None
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        if type(self.schema_version) is not int or self.schema_version != SCHEMA_VERSION:
            raise MultiObjectRoleAllocationError(
                f"unsupported schema version {self.schema_version!r}"
            )
        if type(self.operator) is not str or self.operator not in _OPERATORS:
            raise MultiObjectRoleAllocationError(
                f"unknown role-allocation operator {self.operator!r}"
            )
        if self.operator == RECTANGLE_HANDOFF_OPERATOR:
            follower = _arc_color(self.follower_color, "follower_color")
            leader = _arc_color(self.leader_color, "leader_color")
            if follower == leader:
                raise MultiObjectRoleAllocationError(
                    "follower and leader colours must differ"
                )
            object.__setattr__(self, "follower_color", follower)
            object.__setattr__(self, "leader_color", leader)
        elif self.follower_color is not None or self.leader_color is not None:
            raise MultiObjectRoleAllocationError(
                "cardinal-void program cannot carry literal colour roles"
            )

    @classmethod
    def from_record(cls, raw: object) -> "MultiObjectRoleAllocationProgram":
        if not isinstance(raw, Mapping):
            raise MultiObjectRoleAllocationError("program must be a mapping")
        expected = {"schema", "schema_version", "operator", "parameters"}
        present = set(raw)
        if present != expected:
            raise MultiObjectRoleAllocationError(
                "program fields do not match schema; "
                f"missing={sorted(expected - present)}, "
                f"extra={sorted(present - expected)}"
            )
        if raw["schema"] != SCHEMA:
            raise MultiObjectRoleAllocationError(
                f"unknown program schema {raw['schema']!r}"
            )
        schema_version = _native_schema_int(
            raw["schema_version"], "schema_version"
        )
        operator = raw["operator"]
        if type(operator) is not str:
            raise MultiObjectRoleAllocationError("operator must be a string")
        parameters = raw["parameters"]
        if not isinstance(parameters, Mapping):
            raise MultiObjectRoleAllocationError("parameters must be a mapping")
        if operator == RECTANGLE_HANDOFF_OPERATOR:
            if set(parameters) != {"follower_color", "leader_color"}:
                raise MultiObjectRoleAllocationError(
                    "handoff parameters must contain exactly both colour roles"
                )
            return cls(
                operator=operator,
                follower_color=_arc_color(
                    parameters["follower_color"], "follower_color"
                ),
                leader_color=_arc_color(
                    parameters["leader_color"], "leader_color"
                ),
                schema_version=schema_version,
            )
        if operator == CARDINAL_VOID_OPERATOR:
            if parameters:
                raise MultiObjectRoleAllocationError(
                    "cardinal-void parameters must be empty"
                )
            return cls(operator=operator, schema_version=schema_version)
        raise MultiObjectRoleAllocationError(
            f"unknown role-allocation operator {operator!r}"
        )

    def to_record(self) -> Dict[str, object]:
        parameters: Dict[str, object]
        if self.operator == RECTANGLE_HANDOFF_OPERATOR:
            parameters = {
                "follower_color": int(self.follower_color),
                "leader_color": int(self.leader_color),
            }
        else:
            parameters = {}
        record: Dict[str, object] = {
            "schema": SCHEMA,
            "schema_version": int(self.schema_version),
            "operator": str(self.operator),
            "parameters": parameters,
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
        return 29 if self.operator == RECTANGLE_HANDOFF_OPERATOR else 34

    def apply(
        self,
        grid: Array,
        *,
        limits: MultiObjectRoleAllocationLimits = DEFAULT_LIMITS,
    ) -> Array:
        return execute_multi_object_role_allocation_program(
            self, grid, limits=limits
        )


@dataclass(frozen=True)
class _Component:
    color: int
    cells: Tuple[Cell, ...]
    box: Box

    @property
    def size(self) -> int:
        return len(self.cells)


@dataclass(frozen=True)
class _RectangleHandoffScene:
    background: int
    rectangle: _Component
    singleton_positions: Mapping[int, Cell]
    marker_side: str


@dataclass(frozen=True)
class _CardinalVoidScene:
    background: int
    components: Mapping[str, _Component]
    inward_tips: Mapping[str, Cell]
    void_box: Box
    largest_direction: str
    cap_cells: Tuple[Cell, ...]


@dataclass(frozen=True)
class MultiObjectRoleAllocationCandidate:
    """Entry-independent exact candidate with auditable provenance."""

    name: str
    program: MultiObjectRoleAllocationProgram
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
            record["grids"] = [grid.astype(int).tolist() for grid in self.grids]
            record["train_grids"] = [
                grid.astype(int).tolist() for grid in self.train_grids
            ]
        _canonical_json(record)
        return record


def _validated_grid(
    grid: Array, limits: MultiObjectRoleAllocationLimits
) -> Array:
    try:
        raw = np.asarray(grid)
    except (TypeError, ValueError) as error:
        raise MultiObjectRoleAllocationAbstention(
            "grid must be a rectangular numeric matrix"
        ) from error
    if raw.ndim != 2 or raw.size == 0:
        raise MultiObjectRoleAllocationAbstention(
            "grid must be a nonempty matrix"
        )
    if not np.issubdtype(raw.dtype, np.integer) or np.issubdtype(
        raw.dtype, np.bool_
    ):
        raise MultiObjectRoleAllocationAbstention(
            "grid values must be non-boolean integers"
        )
    values = np.asarray(raw, dtype=np.int64)
    height, width = values.shape
    if (
        height > limits.maximum_height
        or width > limits.maximum_width
        or values.size > limits.maximum_cells
    ):
        raise MultiObjectRoleAllocationLimitError(
            "grid exceeds ARC representation limits"
        )
    palette = np.unique(values)
    if len(palette) > limits.maximum_palette:
        raise MultiObjectRoleAllocationLimitError(
            "palette exceeds representation limit"
        )
    if np.any(palette < 0) or np.any(palette > 9):
        raise MultiObjectRoleAllocationAbstention(
            "grid colours must lie in the ARC palette"
        )
    return np.ascontiguousarray(values, dtype=np.int16)


def _background(source: Array) -> int:
    colors, counts = np.unique(source, return_counts=True)
    maximum = int(counts.max())
    winners = colors[counts == maximum]
    if len(winners) != 1:
        raise MultiObjectRoleAllocationAbstention(
            "global background mode is not unique"
        )
    return int(winners[0])


def _components(
    source: Array,
    background: int,
    connectivity: int,
    limits: MultiObjectRoleAllocationLimits,
) -> Tuple[_Component, ...]:
    height, width = source.shape
    if connectivity == 4:
        offsets = ((-1, 0), (0, -1), (0, 1), (1, 0))
    elif connectivity == 8:
        offsets = tuple(
            (delta_row, delta_column)
            for delta_row in (-1, 0, 1)
            for delta_column in (-1, 0, 1)
            if delta_row or delta_column
        )
    else:
        raise MultiObjectRoleAllocationError("unsupported connectivity")
    seen: set[Cell] = set()
    output = []
    for row in range(height):
        for column in range(width):
            if (row, column) in seen or int(source[row, column]) == background:
                continue
            color = int(source[row, column])
            stack = [(row, column)]
            seen.add((row, column))
            cells = []
            while stack:
                current = stack.pop()
                cells.append(current)
                if len(cells) > limits.maximum_component_cells:
                    raise MultiObjectRoleAllocationLimitError(
                        "component size exceeds representation limit"
                    )
                for delta_row, delta_column in offsets:
                    neighbor = (
                        current[0] + delta_row,
                        current[1] + delta_column,
                    )
                    if (
                        0 <= neighbor[0] < height
                        and 0 <= neighbor[1] < width
                        and neighbor not in seen
                        and int(source[neighbor]) == color
                    ):
                        seen.add(neighbor)
                        stack.append(neighbor)
            rows = [cell[0] for cell in cells]
            columns = [cell[1] for cell in cells]
            output.append(
                _Component(
                    color=color,
                    cells=tuple(sorted(cells)),
                    box=(min(rows), min(columns), max(rows), max(columns)),
                )
            )
            if len(output) > limits.maximum_components:
                raise MultiObjectRoleAllocationLimitError(
                    "component count exceeds representation limit"
                )
    return tuple(output)


def _filled_rectangle(component: _Component) -> bool:
    top, left, bottom, right = component.box
    if bottom <= top or right <= left:
        return False
    expected = {
        (row, column)
        for row in range(top, bottom + 1)
        for column in range(left, right + 1)
    }
    return set(component.cells) == expected


def _rectangle_handoff_scene(
    source: Array, limits: MultiObjectRoleAllocationLimits
) -> _RectangleHandoffScene:
    background = _background(source)
    if len(np.unique(source)) != 4:
        raise MultiObjectRoleAllocationAbstention(
            "rectangle handoff requires exactly four source colours"
        )
    components = _components(source, background, 4, limits)
    if len(components) != 3 or len({item.color for item in components}) != 3:
        raise MultiObjectRoleAllocationAbstention(
            "rectangle handoff requires one component per foreground colour"
        )
    rectangles = [item for item in components if _filled_rectangle(item)]
    singletons = [item for item in components if item.size == 1]
    if len(rectangles) != 1 or len(singletons) != 2:
        raise MultiObjectRoleAllocationAbstention(
            "rectangle and singleton roles are not unique"
        )
    rectangle = rectangles[0]
    top, left, bottom, right = rectangle.box
    height, width = source.shape
    positions = {
        item.color: item.cells[0]
        for item in singletons
    }
    marker_cells = tuple(positions.values())
    side_candidates = []
    if (
        top > 0
        and bottom == height - 1
        and all(row == top - 1 and left <= column <= right for row, column in marker_cells)
    ):
        side_candidates.append("north")
    if (
        bottom < height - 1
        and top == 0
        and all(row == bottom + 1 and left <= column <= right for row, column in marker_cells)
    ):
        side_candidates.append("south")
    if (
        left > 0
        and right == width - 1
        and all(column == left - 1 and top <= row <= bottom for row, column in marker_cells)
    ):
        side_candidates.append("west")
    if (
        right < width - 1
        and left == 0
        and all(column == right + 1 and top <= row <= bottom for row, column in marker_cells)
    ):
        side_candidates.append("east")
    if len(side_candidates) != 1 or marker_cells[0] == marker_cells[1]:
        raise MultiObjectRoleAllocationAbstention(
            "singleton marker side is not unique"
        )
    return _RectangleHandoffScene(
        background=background,
        rectangle=rectangle,
        singleton_positions=positions,
        marker_side=side_candidates[0],
    )


def _execute_rectangle_handoff(
    program: MultiObjectRoleAllocationProgram,
    source: Array,
    limits: MultiObjectRoleAllocationLimits,
) -> Tuple[Array, Dict[str, object]]:
    scene = _rectangle_handoff_scene(source, limits)
    follower = int(program.follower_color)
    leader = int(program.leader_color)
    if set(scene.singleton_positions) != {follower, leader}:
        raise MultiObjectRoleAllocationAbstention(
            "learned singleton colour roles do not bind uniquely"
        )
    follower_cell = scene.singleton_positions[follower]
    leader_cell = scene.singleton_positions[leader]
    top, left, bottom, right = scene.rectangle.box
    if scene.marker_side in {"north", "south"}:
        delta = leader_cell[1] - follower_cell[1]
        if delta == 0:
            raise MultiObjectRoleAllocationAbstention(
                "singleton tangent ordering is ambiguous"
            )
        destination = (
            bottom if scene.marker_side == "north" else top,
            right + 1 if delta > 0 else left - 1,
        )
        ordering = "leader_positive_tangent" if delta > 0 else "leader_negative_tangent"
    else:
        delta = leader_cell[0] - follower_cell[0]
        if delta == 0:
            raise MultiObjectRoleAllocationAbstention(
                "singleton tangent ordering is ambiguous"
            )
        destination = (
            bottom + 1 if delta > 0 else top - 1,
            right if scene.marker_side == "west" else left,
        )
        ordering = "leader_positive_tangent" if delta > 0 else "leader_negative_tangent"
    if not (
        0 <= destination[0] < source.shape[0]
        and 0 <= destination[1] < source.shape[1]
    ):
        raise MultiObjectRoleAllocationAbstention(
            "leader destination lies outside the canvas"
        )
    if int(source[destination]) != scene.background:
        raise MultiObjectRoleAllocationAbstention(
            "leader destination is not empty"
        )
    output = source.copy()
    output[follower_cell] = scene.background
    output[leader_cell] = follower
    output[destination] = leader
    if np.array_equal(output, source):
        raise MultiObjectRoleAllocationAbstention(
            "rectangle handoff produced no change"
        )
    rect_top, rect_left, rect_bottom, rect_right = scene.rectangle.box
    trace: Dict[str, object] = {
        "operator": RECTANGLE_HANDOFF_OPERATOR,
        "background_color": int(scene.background),
        "foreground_component_count": 3,
        "rectangle_height": int(rect_bottom - rect_top + 1),
        "rectangle_width": int(rect_right - rect_left + 1),
        "marker_side": scene.marker_side,
        "leader_tangent_order": ordering,
        "changed_cell_count": int(np.count_nonzero(output != source)),
    }
    return np.ascontiguousarray(output), trace


def _unique_extreme(component: _Component, direction: str) -> Optional[Cell]:
    if direction == "north":
        value = max(row for row, _ in component.cells)
        cells = [cell for cell in component.cells if cell[0] == value]
    elif direction == "south":
        value = min(row for row, _ in component.cells)
        cells = [cell for cell in component.cells if cell[0] == value]
    elif direction == "west":
        value = max(column for _, column in component.cells)
        cells = [cell for cell in component.cells if cell[1] == value]
    elif direction == "east":
        value = min(column for _, column in component.cells)
        cells = [cell for cell in component.cells if cell[1] == value]
    else:
        raise MultiObjectRoleAllocationError("unknown cardinal direction")
    return cells[0] if len(cells) == 1 else None


def _outer_cap_cells(component: _Component, direction: str, tip: Cell) -> Tuple[Cell, ...]:
    top, left, bottom, right = component.box
    if direction == "north":
        return tuple((top - 1, tip[1] + offset) for offset in (-1, 0, 1))
    if direction == "south":
        return tuple((bottom + 1, tip[1] + offset) for offset in (-1, 0, 1))
    if direction == "west":
        return tuple((tip[0] + offset, left - 1) for offset in (-1, 0, 1))
    if direction == "east":
        return tuple((tip[0] + offset, right + 1) for offset in (-1, 0, 1))
    raise MultiObjectRoleAllocationError("unknown cardinal direction")


def _cardinal_void_scene(
    source: Array, limits: MultiObjectRoleAllocationLimits
) -> _CardinalVoidScene:
    background = _background(source)
    if len(np.unique(source)) != 5:
        raise MultiObjectRoleAllocationAbstention(
            "cardinal void requires exactly five source colours"
        )
    components = _components(source, background, 8, limits)
    if (
        len(components) != 4
        or len({component.color for component in components}) != 4
        or any(component.size < 2 for component in components)
    ):
        raise MultiObjectRoleAllocationAbstention(
            "cardinal void requires four nontrivial colour components"
        )
    sizes = sorted((component.size for component in components), reverse=True)
    if sizes[0] == sizes[1]:
        raise MultiObjectRoleAllocationAbstention(
            "largest cardinal object is not unique"
        )
    direction_order = ("north", "east", "south", "west")
    interpretations = []
    for permutation in itertools.permutations(components):
        assigned = dict(zip(direction_order, permutation))
        tips = {
            direction: _unique_extreme(assigned[direction], direction)
            for direction in direction_order
        }
        if any(tip is None for tip in tips.values()):
            continue
        north_tip = tips["north"]
        east_tip = tips["east"]
        south_tip = tips["south"]
        west_tip = tips["west"]
        assert north_tip is not None
        assert east_tip is not None
        assert south_tip is not None
        assert west_tip is not None
        top = north_tip[0] + 1
        bottom = south_tip[0] - 1
        left = west_tip[1] + 1
        right = east_tip[1] - 1
        axis_row = west_tip[0]
        axis_column = north_tip[1]
        if (
            top > bottom
            or left > right
            or east_tip[0] != axis_row
            or south_tip[1] != axis_column
            or not top <= axis_row <= bottom
            or not left <= axis_column <= right
        ):
            continue
        void_cells = (bottom - top + 1) * (right - left + 1)
        if void_cells > limits.maximum_void_cells:
            raise MultiObjectRoleAllocationLimitError(
                "central void exceeds representation limit"
            )
        if any(
            int(source[row, column]) != background
            for row in range(top, bottom + 1)
            for column in range(left, right + 1)
        ):
            continue
        if not all(row < top for row, _ in assigned["north"].cells):
            continue
        if not all(row > bottom for row, _ in assigned["south"].cells):
            continue
        if not all(column < left for _, column in assigned["west"].cells):
            continue
        if not all(column > right for _, column in assigned["east"].cells):
            continue
        largest = max(direction_order, key=lambda item: assigned[item].size)
        cap_cells = _outer_cap_cells(assigned[largest], largest, tips[largest])
        if any(
            not (0 <= row < source.shape[0] and 0 <= column < source.shape[1])
            or int(source[row, column]) != background
            for row, column in cap_cells
        ):
            continue
        interpretations.append(
            _CardinalVoidScene(
                background=background,
                components=assigned,
                inward_tips={
                    direction: tips[direction]  # type: ignore[dict-item]
                    for direction in direction_order
                },
                void_box=(top, left, bottom, right),
                largest_direction=largest,
                cap_cells=tuple(sorted(cap_cells)),
            )
        )
    if len(interpretations) != 1:
        raise MultiObjectRoleAllocationAbstention(
            "cardinal void and object roles are not unique"
        )
    return interpretations[0]


def _execute_cardinal_void(
    source: Array, limits: MultiObjectRoleAllocationLimits
) -> Tuple[Array, Dict[str, object]]:
    scene = _cardinal_void_scene(source, limits)
    output = source.copy()
    removed = []
    for direction in ("north", "east", "south", "west"):
        if direction == scene.largest_direction:
            continue
        tip = scene.inward_tips[direction]
        output[tip] = scene.background
        removed.append(direction)
    largest_color = scene.components[scene.largest_direction].color
    for cell in scene.cap_cells:
        output[cell] = largest_color
    if np.array_equal(output, source):
        raise MultiObjectRoleAllocationAbstention(
            "cardinal-void allocation produced no change"
        )
    top, left, bottom, right = scene.void_box
    trace: Dict[str, object] = {
        "operator": CARDINAL_VOID_OPERATOR,
        "background_color": int(scene.background),
        "foreground_component_count": 4,
        "connectivity": 8,
        "void_height": int(bottom - top + 1),
        "void_width": int(right - left + 1),
        "component_sizes_by_direction": {
            direction: int(scene.components[direction].size)
            for direction in ("north", "east", "south", "west")
        },
        "largest_direction": scene.largest_direction,
        "outer_cap_cell_count": len(scene.cap_cells),
        "removed_inward_tip_directions": sorted(removed),
        "changed_cell_count": int(np.count_nonzero(output != source)),
    }
    return np.ascontiguousarray(output), trace


def _execute_with_trace(
    program: MultiObjectRoleAllocationProgram,
    grid: Array,
    limits: MultiObjectRoleAllocationLimits,
) -> Tuple[Array, Dict[str, object]]:
    source = _validated_grid(grid, limits)
    if program.operator == RECTANGLE_HANDOFF_OPERATOR:
        return _execute_rectangle_handoff(program, source, limits)
    if program.operator == CARDINAL_VOID_OPERATOR:
        return _execute_cardinal_void(source, limits)
    raise MultiObjectRoleAllocationError("unknown role-allocation operator")


def execute_multi_object_role_allocation_program(
    program: MultiObjectRoleAllocationProgram | Mapping[str, object],
    grid: Array,
    *,
    limits: MultiObjectRoleAllocationLimits = DEFAULT_LIMITS,
) -> Array:
    """Rebind all source roles and execute one allocation atomically."""

    if not isinstance(program, MultiObjectRoleAllocationProgram):
        program = MultiObjectRoleAllocationProgram.from_record(program)
    output, _ = _execute_with_trace(program, grid, limits)
    return output.copy()


def _example_hash(source: Array, target: Array) -> str:
    digest = hashlib.sha256()
    for grid in (source, target):
        value = np.asarray(grid, dtype=np.int16)
        digest.update(np.asarray(value.shape, dtype=np.int16).tobytes())
        digest.update(value.tobytes(order="C"))
    return digest.hexdigest()


def _program_options_for_example(
    source: Array,
    target: Array,
    limits: MultiObjectRoleAllocationLimits,
) -> Tuple[MultiObjectRoleAllocationProgram, ...]:
    if source.shape != target.shape or np.array_equal(source, target):
        return ()
    options = []
    try:
        scene = _rectangle_handoff_scene(source, limits)
    except MultiObjectRoleAllocationAbstention:
        scene = None
    if scene is not None:
        colors = sorted(scene.singleton_positions)
        for follower, leader in itertools.permutations(colors):
            program = MultiObjectRoleAllocationProgram(
                operator=RECTANGLE_HANDOFF_OPERATOR,
                follower_color=follower,
                leader_color=leader,
            )
            try:
                prediction = program.apply(source, limits=limits)
            except MultiObjectRoleAllocationAbstention:
                continue
            if np.array_equal(prediction, target):
                options.append(program)
    cardinal = MultiObjectRoleAllocationProgram(operator=CARDINAL_VOID_OPERATOR)
    try:
        prediction = cardinal.apply(source, limits=limits)
    except MultiObjectRoleAllocationAbstention:
        prediction = None
    if prediction is not None and np.array_equal(prediction, target):
        options.append(cardinal)
    unique = {program.program_hash(): program for program in options}
    return tuple(unique[key] for key in sorted(unique))


def _infer_exact_program(
    train: Sequence[Tuple[Array, Array]],
    limits: MultiObjectRoleAllocationLimits,
) -> Optional[
    Tuple[
        MultiObjectRoleAllocationProgram,
        Tuple[Array, ...],
        Tuple[Dict[str, object], ...],
    ]
]:
    if not train:
        return None
    options = _program_options_for_example(train[0][0], train[0][1], limits)
    exact_programs = []
    for program in options:
        predictions = []
        traces = []
        valid = True
        for source, target in train:
            if np.array_equal(source, target):
                valid = False
                break
            try:
                prediction, trace = _execute_with_trace(program, source, limits)
            except MultiObjectRoleAllocationAbstention:
                valid = False
                break
            if not np.array_equal(prediction, target):
                valid = False
                break
            predictions.append(prediction)
            traces.append(trace)
        if valid:
            exact_programs.append((program, tuple(predictions), tuple(traces)))
    if len(exact_programs) != 1:
        return None
    return exact_programs[0]


def compile_multi_object_role_allocation_program(
    train: Sequence[Tuple[Array, Array]],
    tests: Sequence[Array],
    *,
    limits: MultiObjectRoleAllocationLimits = DEFAULT_LIMITS,
) -> Tuple[MultiObjectRoleAllocationCandidate, ...]:
    """Compile after exact replay and duplicate-collapsed group LOO."""

    if len(train) < limits.minimum_distinct_nonidentity_groups or not tests:
        return ()
    if len(train) > limits.maximum_examples or len(tests) > limits.maximum_tests:
        raise MultiObjectRoleAllocationLimitError("example budget exceeded")
    try:
        validated = tuple(
            (
                _validated_grid(source, limits),
                _validated_grid(target, limits),
            )
            for source, target in train
        )
        validated_tests = tuple(_validated_grid(test, limits) for test in tests)
    except MultiObjectRoleAllocationAbstention:
        return ()
    if any(np.array_equal(source, target) for source, target in validated):
        return ()

    groups: Dict[str, list[int]] = {}
    for index, (source, target) in enumerate(validated):
        groups.setdefault(_example_hash(source, target), []).append(index)
    if len(groups) < limits.minimum_distinct_nonidentity_groups:
        return ()

    full = _infer_exact_program(validated, limits)
    if full is None:
        return ()
    program, train_predictions, traces = full
    program_hash = program.program_hash()

    group_loo_program_hashes = []
    group_loo_exact_count = 0
    for group_hash in sorted(groups):
        held_indices = groups[group_hash]
        excluded = set(held_indices)
        construction = tuple(
            pair for index, pair in enumerate(validated) if index not in excluded
        )
        fold = _infer_exact_program(construction, limits)
        if fold is None or fold[0].program_hash() != program_hash:
            break
        try:
            exact_group = all(
                np.array_equal(
                    fold[0].apply(validated[index][0], limits=limits),
                    validated[index][1],
                )
                for index in held_indices
            )
        except MultiObjectRoleAllocationAbstention:
            break
        if not exact_group:
            break
        group_loo_program_hashes.append(fold[0].program_hash())
        group_loo_exact_count += 1
    if group_loo_exact_count != len(groups):
        return ()

    try:
        test_predictions = tuple(
            program.apply(test, limits=limits) for test in validated_tests
        )
    except MultiObjectRoleAllocationAbstention:
        return ()

    metadata: Dict[str, object] = {
        "schema": "komorebi.arc.multi-object-role-allocation-candidate.v1",
        "program": program.to_record(),
        "program_hash": program_hash,
        "semantic_key": program.semantic_key,
        "operator": program.operator,
        "domain": "bounded_multi_object_source_role_graph",
        "exact_demonstration_contract": True,
        "test_target_isolation": True,
        "test_input_grounded": True,
        "task_identifier_free": True,
        "raw_grid_free_program": True,
        "literal_coordinate_free_program": True,
        "source_derived_semantic_roles": True,
        "d4_equivariant": True,
        "palette_equivariant": True,
        "translation_equivariant": program.operator == CARDINAL_VOID_OPERATOR,
        "component_color_free_program": program.operator == CARDINAL_VOID_OPERATOR,
        "role_colors_demonstration_inferred": program.operator == RECTANGLE_HANDOFF_OPERATOR,
        "witness_protocol": (
            "full_demonstration_and_duplicate_collapsed_distinct_nonidentity_"
            "group_loo_reinduction"
        ),
        "full_demonstration_count": int(len(validated)),
        "distinct_witness_groups": int(len(groups)),
        "distinct_nonidentity_witness_groups": int(len(groups)),
        "duplicate_example_count": int(len(validated) - len(groups)),
        "loo_exact_count": int(group_loo_exact_count),
        "loo_total_count": int(len(groups)),
        "loo_program_hashes": list(group_loo_program_hashes),
        "distinct_group_loo_exact_count": int(group_loo_exact_count),
        "distinct_group_loo_total_count": int(len(groups)),
        "distinct_group_loo_program_hashes": list(group_loo_program_hashes),
        "witness_reconstructible": True,
        "training_trace_summary": list(traces),
        "ambiguity_policy": "require_unique_program_and_unique_source_role_binding",
        "resource_policy": "hard_bounded_fail_closed",
        "empirical_promotion_eligible": False,
        "external_gain_loss_audit": False,
        "implementation_fingerprint": (
            multi_object_role_allocation_implementation_fingerprint()
        ),
        "limits": limits.to_record(),
    }
    return (
        MultiObjectRoleAllocationCandidate(
            name=f"multi_object_role_allocation:{program.operator}:{program_hash[:12]}",
            program=program,
            grids=test_predictions,
            train_grids=train_predictions,
            complexity=program.complexity,
            metadata=metadata,
        ),
    )


multi_object_role_allocation_candidates = (
    compile_multi_object_role_allocation_program
)


__all__ = [
    "CARDINAL_VOID_OPERATOR",
    "DEFAULT_LIMITS",
    "FAMILY",
    "MultiObjectRoleAllocationAbstention",
    "MultiObjectRoleAllocationCandidate",
    "MultiObjectRoleAllocationError",
    "MultiObjectRoleAllocationLimitError",
    "MultiObjectRoleAllocationLimits",
    "MultiObjectRoleAllocationProgram",
    "RECTANGLE_HANDOFF_OPERATOR",
    "compile_multi_object_role_allocation_program",
    "execute_multi_object_role_allocation_program",
    "multi_object_role_allocation_candidates",
    "multi_object_role_allocation_implementation_fingerprint",
]
