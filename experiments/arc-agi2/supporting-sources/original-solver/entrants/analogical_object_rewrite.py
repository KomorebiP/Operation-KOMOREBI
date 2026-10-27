"""Task-local analogical object rewriting for PR-LASM Block 14.

This lane parses root scenes into objects, induces normalized before/after
templates from demonstrations, and reapplies them through relational object
roles.  Its finite grammar contains completion, repair, replication, deletion,
and recoloring programs.  Two richer templates transport internal object
roles: marker count -> frame thickness, and incomplete outline -> filled frame
plus gap continuation.

Programs store structural roles and normalized templates, never task IDs or
resolved coordinates.  Compilation uses demonstrations and test inputs only;
attached test labels are ignored.  Admission requires exact replay, genuine
leave-one-demo-out re-induction, a unique minimum-description full-test
behavior, D4/palette covariance, and non-exhausted hard limits.

Author: Komorebi P.
"""
from __future__ import annotations

import argparse
from collections import Counter, deque
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any


Grid = tuple[tuple[int, ...], ...]
Cell = tuple[int, int]
Pair = tuple[Grid, Grid]
SCHEMA = "komorebi.pr_lasm.block14.analogical_object_rewrite.program.v1"
SCAN_SCHEMA = "komorebi.pr_lasm.block14.analogical_object_rewrite.scan_freeze.v1"
AUTHOR = "Komorebi P."
ORTHOGONAL: tuple[Cell, ...] = ((-1, 0), (0, -1), (0, 1), (1, 0))
EIGHT: tuple[Cell, ...] = tuple(
    (dr, dc)
    for dr in (-1, 0, 1)
    for dc in (-1, 0, 1)
    if (dr, dc) != (0, 0)
)


class Undefined(ValueError):
    """An object role is absent, tied, colliding, or outside a hard cap."""


@dataclass(frozen=True, slots=True)
class Limits:
    max_grid_cells: int = 900
    max_examples: int = 10
    max_components: int = 192
    max_frame_thickness: int = 8
    max_programs: int = 4_096
    max_executor_calls: int = 100_000
    max_gauge_checks: int = 1_024
    max_candidates: int = 1
    mdl_slack: int = 0

    @classmethod
    def from_value(cls, value: Mapping[str, Any] | None) -> "Limits":
        if value is None:
            return cls()
        if not isinstance(value, Mapping):
            raise Undefined("limits must be a mapping")
        defaults = cls()
        ceilings = {
            "max_grid_cells": 3_600,
            "max_examples": 20,
            "max_components": 512,
            "max_frame_thickness": 15,
            "max_programs": 20_000,
            "max_executor_calls": 1_000_000,
            "max_gauge_checks": 4_096,
            "max_candidates": 1,
            "mdl_slack": 3,
        }
        result: dict[str, int] = {}
        for name in cls.__dataclass_fields__:
            fallback = value.get("candidate_cap", getattr(defaults, name)) if name == "max_candidates" else getattr(defaults, name)
            raw = value.get(name, fallback)
            if isinstance(raw, bool) or not isinstance(raw, int):
                raise Undefined(f"limits.{name} must be an integer")
            minimum = 0 if name == "mdl_slack" else 1
            if raw < minimum:
                raise Undefined(f"limits.{name} is below {minimum}")
            result[name] = min(raw, ceilings[name])
        return cls(**result)


@dataclass(frozen=True, slots=True)
class Component:
    cells: frozenset[Cell]
    bbox: tuple[int, int, int, int]
    color_counts: tuple[tuple[int, int], ...]
    partition: str
    canvas_shape: tuple[int, int]

    @property
    def area(self) -> int:
        return len(self.cells)

    @property
    def height(self) -> int:
        return self.bbox[1] - self.bbox[0] + 1

    @property
    def width(self) -> int:
        return self.bbox[3] - self.bbox[2] + 1

    @property
    def bbox_area(self) -> int:
        return self.height * self.width

    @property
    def colors(self) -> tuple[int, ...]:
        return tuple(color for color, _ in self.color_counts)

    @property
    def monochrome(self) -> bool:
        return len(self.color_counts) == 1

    @property
    def color(self) -> int:
        if not self.monochrome:
            raise Undefined("multicolor object has no scalar color")
        return self.color_counts[0][0]

    @property
    def solid(self) -> bool:
        return self.area == self.bbox_area

    @property
    def line(self) -> bool:
        return self.height == 1 or self.width == 1

    @property
    def square(self) -> bool:
        return self.height == self.width

    @property
    def touches_border(self) -> bool:
        height, width = self.canvas_shape
        return self.bbox[0] == 0 or self.bbox[1] == height - 1 or self.bbox[2] == 0 or self.bbox[3] == width - 1

    @property
    def normalized_shape(self) -> tuple[Cell, ...]:
        top, _, left, _ = self.bbox
        return tuple(sorted((row - top, column - left) for row, column in self.cells))

    @property
    def d4_shape(self) -> tuple[tuple[int, int], tuple[Cell, ...]]:
        mask = tuple(
            tuple(1 if (row, column) in self.normalized_shape else 0 for column in range(self.width))
            for row in range(self.height)
        )
        variants = _d4_matrices(mask)
        return min((_shape(value), tuple((r, c) for r, row in enumerate(value) for c, item in enumerate(row) if item)) for value in variants)


@dataclass(slots=True)
class Scene:
    grid: Grid
    background_role: str
    background: int
    mono4: tuple[Component, ...]
    mono8: tuple[Component, ...]
    multi4: tuple[Component, ...]
    color_counts: Counter[int]


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _plain(grid: Grid) -> list[list[int]]:
    return [list(row) for row in grid]


def _shape(grid: Sequence[Sequence[Any]]) -> tuple[int, int]:
    return len(grid), len(grid[0])


def _grid(value: Any, limits: Limits) -> Grid:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or not value:
        raise Undefined("grid must be a nonempty sequence")
    rows: list[tuple[int, ...]] = []
    width: int | None = None
    for raw_row in value:
        if not isinstance(raw_row, Sequence) or isinstance(raw_row, (str, bytes)) or not raw_row:
            raise Undefined("grid row must be nonempty")
        row: list[int] = []
        for raw_cell in raw_row:
            if isinstance(raw_cell, bool) or not isinstance(raw_cell, int) or not 0 <= raw_cell <= 9:
                raise Undefined("ARC color is invalid")
            row.append(int(raw_cell))
        if width is None:
            width = len(row)
        elif len(row) != width:
            raise Undefined("grid is ragged")
        rows.append(tuple(row))
    if len(rows) * int(width or 0) > limits.max_grid_cells:
        raise Undefined("grid exceeds the cell cap")
    return tuple(rows)


def _sanitize(task: Any, limits: Limits) -> tuple[tuple[Pair, ...], tuple[Grid, ...]]:
    if not isinstance(task, Mapping):
        raise Undefined("task must be a mapping")
    train, test = task.get("train"), task.get("test")
    if (
        not isinstance(train, Sequence)
        or isinstance(train, (str, bytes))
        or len(train) < 2
        or not isinstance(test, Sequence)
        or isinstance(test, (str, bytes))
        or not test
        or len(train) + len(test) > limits.max_examples
    ):
        raise Undefined("task arity is invalid")
    demonstrations: list[Pair] = []
    for example in train:
        if not isinstance(example, Mapping):
            raise Undefined("demonstration is invalid")
        source = _grid(example.get("input"), limits)
        target = _grid(example.get("output"), limits)
        if _shape(source) != _shape(target) or source == target:
            raise Undefined("object rewriting requires nonidentity same-shape pairs")
        demonstrations.append((source, target))
    tests: list[Grid] = []
    for example in test:
        if not isinstance(example, Mapping):
            raise Undefined("test example is invalid")
        tests.append(_grid(example.get("input"), limits))
    return tuple(demonstrations), tuple(tests)


def _unique_mode(values: Iterable[int]) -> int:
    counts = Counter(values)
    maximum = max(counts.values())
    winners = sorted(color for color, count in counts.items() if count == maximum)
    if len(winners) != 1:
        raise Undefined("mode role is tied")
    return winners[0]


def _background(grid: Grid, role: str) -> int:
    height, width = _shape(grid)
    if role == "mode":
        return _unique_mode(cell for row in grid for cell in row)
    if role == "border_mode":
        return _unique_mode(
            grid[row][column]
            for row in range(height)
            for column in range(width)
            if row in {0, height - 1} or column in {0, width - 1}
        )
    if role == "corners":
        corners = (grid[0][0], grid[0][-1], grid[-1][0], grid[-1][-1])
        if len(set(corners)) != 1:
            raise Undefined("corner role is tied")
        return corners[0]
    raise Undefined("unknown background role")


def _bbox(cells: Iterable[Cell]) -> tuple[int, int, int, int]:
    points = tuple(cells)
    if not points:
        raise Undefined("empty object")
    return (
        min(row for row, _ in points),
        max(row for row, _ in points),
        min(column for _, column in points),
        max(column for _, column in points),
    )


def _components(grid: Grid, background: int, partition: str, limits: Limits) -> tuple[Component, ...]:
    if partition not in {"mono4", "mono8", "multi4"}:
        raise Undefined("unknown object partition")
    connectivity = 8 if partition == "mono8" else 4
    monochrome = partition.startswith("mono")
    directions = EIGHT if connectivity == 8 else ORTHOGONAL
    height, width = _shape(grid)
    remaining = {
        (row, column)
        for row in range(height)
        for column in range(width)
        if grid[row][column] != background
    }
    answer: list[Component] = []
    while remaining:
        seed = min(remaining)
        remaining.remove(seed)
        cells = {seed}
        queue = deque([seed])
        while queue:
            row, column = queue.popleft()
            for dr, dc in directions:
                point = row + dr, column + dc
                if point not in remaining:
                    continue
                if monochrome and grid[point[0]][point[1]] != grid[row][column]:
                    continue
                remaining.remove(point)
                cells.add(point)
                queue.append(point)
        frozen = frozenset(cells)
        answer.append(
            Component(
                frozen,
                _bbox(frozen),
                tuple(sorted(Counter(grid[row][column] for row, column in frozen).items())),
                partition,
                (height, width),
            )
        )
        if len(answer) > limits.max_components:
            raise Undefined("object count cap exhausted")
    return tuple(sorted(answer, key=lambda item: (item.bbox, item.color_counts)))


def _scene(grid: Grid, background_role: str, limits: Limits) -> Scene:
    background = _background(grid, background_role)
    return Scene(
        grid,
        background_role,
        background,
        _components(grid, background, "mono4", limits),
        _components(grid, background, "mono8", limits),
        _components(grid, background, "multi4", limits),
        Counter(cell for row in grid for cell in row),
    )


def _d4_matrices(matrix: Sequence[Sequence[Any]]) -> tuple[tuple[tuple[Any, ...], ...], ...]:
    frozen = tuple(tuple(row) for row in matrix)
    values: dict[str, tuple[tuple[Any, ...], ...]] = {}
    current = frozen
    for _ in range(4):
        values.setdefault(_canonical(current), current)
        reflected = tuple(tuple(reversed(row)) for row in current)
        values.setdefault(_canonical(reflected), reflected)
        current = tuple(tuple(row) for row in zip(*reversed(current)))
    return tuple(values[key] for key in sorted(values))


def _partition(scene: Scene, name: str) -> tuple[Component, ...]:
    if name == "mono4":
        return scene.mono4
    if name == "mono8":
        return scene.mono8
    if name == "multi4":
        return scene.multi4
    raise Undefined("unknown object partition")


def _resolve_color_role(role: Mapping[str, Any], scene: Scene, component: Component) -> int:
    kind = role.get("kind")
    if kind == "literal":
        color = role.get("color")
        if isinstance(color, bool) or not isinstance(color, int) or not 0 <= color <= 9:
            raise Undefined("literal color is invalid")
        return color
    if kind == "background":
        return scene.background
    if kind == "object_color":
        return component.color
    foreground = {color: count for color, count in scene.color_counts.items() if color != scene.background}
    if kind in {"rarest_foreground", "most_foreground"}:
        if not foreground:
            raise Undefined("foreground color role is absent")
        wanted = min(foreground.values()) if kind == "rarest_foreground" else max(foreground.values())
        winners = sorted(color for color, count in foreground.items() if count == wanted)
        if len(winners) != 1:
            raise Undefined("foreground color role is tied")
        return winners[0]
    raise Undefined("unknown color role")


def _select_components(scene: Scene, program: Mapping[str, Any]) -> tuple[Component, ...]:
    partition = str(program.get("partition"))
    components = _partition(scene, partition)
    selector = program.get("selector")
    if not isinstance(selector, Mapping):
        raise Undefined("object selector is invalid")
    kind = selector.get("kind")
    if kind == "all":
        selected = list(components)
    elif kind in {"unique_min_area", "unique_max_area", "unique_min_bbox", "unique_max_bbox"}:
        if not components:
            raise Undefined("object population is empty")
        attr = "area" if kind.endswith("area") else "bbox_area"
        values = [getattr(component, attr) for component in components]
        wanted = min(values) if "min" in str(kind) else max(values)
        selected = [component for component in components if getattr(component, attr) == wanted]
        if len(selected) != 1:
            raise Undefined("object extreme is tied")
    elif kind in {"line", "solid_rectangle", "non_solid", "square", "touches_border", "interior"}:
        selected = []
        for component in components:
            value = {
                "line": component.line,
                "solid_rectangle": component.solid,
                "non_solid": not component.solid,
                "square": component.square,
                "touches_border": component.touches_border,
                "interior": not component.touches_border,
            }[str(kind)]
            if value:
                selected.append(component)
    elif kind in {"unique_shape", "repeated_shape"}:
        counts = Counter(component.d4_shape for component in components)
        wanted = 1 if kind == "unique_shape" else None
        selected = [
            component
            for component in components
            if (counts[component.d4_shape] == 1 if wanted == 1 else counts[component.d4_shape] > 1)
        ]
    elif kind in {"unique_rarest_color", "unique_most_color"}:
        mono = [component for component in components if component.monochrome]
        totals = Counter(component.color for component in mono)
        if not totals:
            raise Undefined("monochrome color population is empty")
        wanted = min(totals.values()) if kind == "unique_rarest_color" else max(totals.values())
        colors = [color for color, count in totals.items() if count == wanted]
        if len(colors) != 1:
            raise Undefined("object color-frequency role is tied")
        selected = [component for component in mono if component.color == colors[0]]
    else:
        raise Undefined("unknown object selector")
    if not selected:
        raise Undefined("object selector is empty")
    return tuple(selected)


def _execute_marker_count_frame(program: Mapping[str, Any], scene: Scene, limits: Limits) -> tuple[Grid, dict[str, Any]]:
    objects = scene.multi4
    if not objects:
        raise Undefined("marker-frame object population is empty")
    output = [list(row) for row in scene.grid]
    claims: dict[Cell, int] = {}
    records: list[dict[str, Any]] = []
    for component in objects:
        if not component.solid or len(component.color_counts) != 2:
            raise Undefined("object is not a filled two-role rectangle")
        ordered = sorted(component.color_counts, key=lambda item: (-item[1], item[0]))
        if ordered[0][1] == ordered[1][1]:
            raise Undefined("base/marker identity is tied")
        base, marker = ordered[0][0], ordered[1][0]
        thickness = ordered[1][1]
        if not 1 <= thickness <= limits.max_frame_thickness:
            raise Undefined("marker-count thickness is outside its cap")
        top, bottom, left, right = component.bbox
        expanded = top - thickness, bottom + thickness, left - thickness, right + thickness
        if expanded[0] < 0 or expanded[2] < 0 or expanded[1] >= len(scene.grid) or expanded[3] >= len(scene.grid[0]):
            raise Undefined("replicated frame leaves the canvas")
        painted = 0
        for row in range(expanded[0], expanded[1] + 1):
            for column in range(expanded[2], expanded[3] + 1):
                if top <= row <= bottom and left <= column <= right:
                    continue
                point = row, column
                if scene.grid[row][column] != scene.background:
                    raise Undefined("replicated frame collides with source support")
                previous = claims.get(point)
                if previous is not None and previous != marker:
                    raise Undefined("replicated frames disagree on overlap")
                claims[point] = marker
                painted += 1
        records.append(
            {
                "before_template": "filled_rectangle_with_intrinsic_markers",
                "shape": [component.height, component.width],
                "base_role": base,
                "marker_role": marker,
                "marker_count": thickness,
                "replicated_frame_cells": painted,
            }
        )
    for (row, column), color in claims.items():
        output[row][column] = color
    return tuple(tuple(row) for row in output), {
        "macro": "marker_count_frame",
        "object_count": len(objects),
        "objects": records,
    }


def _outline_descriptor(component: Component) -> tuple[set[Cell], set[Cell]]:
    if not component.monochrome or component.height < 3 or component.width < 3:
        raise Undefined("outline object is too small or multicolor")
    top, bottom, left, right = component.bbox
    perimeter = {
        (row, column)
        for row in range(top, bottom + 1)
        for column in range(left, right + 1)
        if row in {top, bottom} or column in {left, right}
    }
    if not component.cells <= perimeter:
        raise Undefined("outline object has occupied interior")
    missing = perimeter - component.cells
    if len(missing) > 1:
        raise Undefined("outline has more than one gap")
    if missing:
        row, column = next(iter(missing))
        if row in {top, bottom} and column in {left, right}:
            raise Undefined("corner gap has two outward gauges")
    return perimeter, missing


def _frame_paint_cells(scene: Scene, component: Component) -> set[Cell]:
    _, missing = _outline_descriptor(component)
    top, bottom, left, right = component.bbox
    cells = {
        (row, column)
        for row in range(top + 1, bottom)
        for column in range(left + 1, right)
    }
    if missing:
        row, column = next(iter(missing))
        if row == top:
            dr, dc = -1, 0
        elif row == bottom:
            dr, dc = 1, 0
        elif column == left:
            dr, dc = 0, -1
        else:
            dr, dc = 0, 1
        while 0 <= row < len(scene.grid) and 0 <= column < len(scene.grid[0]):
            cells.add((row, column))
            row += dr
            column += dc
    if any(scene.grid[row][column] != scene.background for row, column in cells):
        raise Undefined("frame fill/continuation collides with source support")
    return cells


def _execute_frame_fill_escape(program: Mapping[str, Any], scene: Scene, limits: Limits) -> tuple[Grid, dict[str, Any]]:
    if len(scene.mono4) < 2:
        raise Undefined("frame repair requires an object cohort")
    emission = program.get("emission")
    if not isinstance(emission, Mapping):
        raise Undefined("frame emission is invalid")
    output = [list(row) for row in scene.grid]
    claims: set[Cell] = set()
    records: list[dict[str, Any]] = []
    for component in scene.mono4:
        cells = _frame_paint_cells(scene, component)
        color = _resolve_color_role(emission, scene, component)
        for row, column in cells:
            output[row][column] = color
        claims.update(cells)
        _, missing = _outline_descriptor(component)
        records.append(
            {
                "before_template": "rectangular_outline",
                "shape": [component.height, component.width],
                "gap_count": len(missing),
                "filled_or_continued_cells": len(cells),
                "emission": color,
            }
        )
    return tuple(tuple(row) for row in output), {
        "macro": "frame_fill_escape",
        "object_count": len(scene.mono4),
        "edit_count": len(claims),
        "objects": records,
    }


def _execute_role_action(program: Mapping[str, Any], scene: Scene, limits: Limits) -> tuple[Grid, dict[str, Any]]:
    selected = _select_components(scene, program)
    action = program.get("action")
    if not isinstance(action, Mapping):
        raise Undefined("object action is invalid")
    kind = action.get("kind")
    output = [list(row) for row in scene.grid]
    colors: Counter[int] = Counter()
    for component in selected:
        if kind == "delete":
            color = scene.background
        elif kind == "recolor":
            role = action.get("color")
            if not isinstance(role, Mapping):
                raise Undefined("recolor role is invalid")
            color = _resolve_color_role(role, scene, component)
        else:
            raise Undefined("unknown object action")
        for row, column in component.cells:
            output[row][column] = color
        colors[color] += component.area
    return tuple(tuple(row) for row in output), {
        "macro": "relational_object_action",
        "partition": program.get("partition"),
        "selector": program.get("selector"),
        "selected_count": len(selected),
        "paint_histogram": {str(color): count for color, count in sorted(colors.items())},
    }


def _execute_on_scene(program: Mapping[str, Any], scene: Scene, limits: Limits) -> tuple[Grid, Scene, dict[str, Any]]:
    macro = program.get("macro")
    if macro == "marker_count_frame":
        output, record = _execute_marker_count_frame(program, scene, limits)
    elif macro == "frame_fill_escape":
        output, record = _execute_frame_fill_escape(program, scene, limits)
    elif macro == "relational_object_action":
        output, record = _execute_role_action(program, scene, limits)
    else:
        raise Undefined("unknown analogical rewrite macro")
    if output == scene.grid:
        raise Undefined("object rewrite is an identity")
    return output, scene, record


def _execute_internal(program: Mapping[str, Any], grid: Grid, limits: Limits) -> tuple[Grid, Scene, dict[str, Any]]:
    if not isinstance(program, Mapping) or program.get("schema") != SCHEMA:
        raise Undefined("invalid analogical rewrite program")
    background_role = program.get("background")
    if background_role not in {"mode", "border_mode", "corners"}:
        raise Undefined("invalid root identity role")
    scene = _scene(grid, str(background_role), limits)
    return _execute_on_scene(program, scene, limits)


def execute_program(program: Mapping[str, Any], value: Any) -> list[list[int]]:
    """Execute one serialized object rewrite program."""

    limits = Limits()
    grid = _grid(value, limits)
    return _plain(_execute_internal(program, grid, limits)[0])


def replay_program(program: Mapping[str, Any], value: Any) -> dict[str, Any]:
    """Tournament replay hook with root-identity and object-rewrite stages."""

    limits = Limits()
    grid = _grid(value, limits)
    output, scene, rewrite = _execute_internal(program, grid, limits)
    parsed = {
        "kind": "root_object_scene",
        "shape": list(_shape(grid)),
        "background_role": scene.background_role,
        "background": scene.background,
        "mono4_objects": len(scene.mono4),
        "mono8_objects": len(scene.mono8),
        "multi4_objects": len(scene.multi4),
    }
    return {
        "output": _plain(output),
        "stages": [
            {"name": "transport-root-identity", "input": _plain(grid), "output": parsed},
            {"name": "resolve-object-correspondence", "input": parsed, "output": rewrite},
            {"name": "execute-normalized-rewrite", "input": rewrite, "output": _plain(output)},
        ],
    }


def _base_program(macro: str, background: str, complexity: int, **fields: Any) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "macro": macro,
        "background": background,
        "description_length": complexity + (0 if background == "mode" else 1),
        **fields,
    }


def _color_action_specs(demonstrations: Sequence[Pair]) -> tuple[dict[str, Any], ...]:
    changed_targets = sorted(
        {
            target[row][column]
            for source, target in demonstrations
            for row in range(len(source))
            for column in range(len(source[0]))
            if source[row][column] != target[row][column]
        }
    )
    roles: list[dict[str, Any]] = [
        {"kind": "background"},
        {"kind": "object_color"},
        {"kind": "rarest_foreground"},
        {"kind": "most_foreground"},
    ]
    roles.extend({"kind": "literal", "color": color} for color in changed_targets)
    return tuple(roles)


def _program_pool(demonstrations: Sequence[Pair], limits: Limits, *, family: str | None = None) -> tuple[dict[str, Any], ...]:
    programs: list[dict[str, Any]] = []
    backgrounds = ("mode", "border_mode", "corners")
    if family in {None, "marker_count_frame"}:
        for background in backgrounds:
            programs.append(
                _base_program(
                    "marker_count_frame",
                    background,
                    8,
                    partition="multi4",
                    before_template={"kind": "solid_two_role_rectangle"},
                    correspondence={"marker_count": "frame_thickness", "marker_color": "frame_color"},
                    after_template={"kind": "preserve_object_and_add_rectangular_frame"},
                )
            )
    if family in {None, "frame_fill_escape"}:
        for background in backgrounds:
            for role in _color_action_specs(demonstrations):
                programs.append(
                    _base_program(
                        "frame_fill_escape",
                        background,
                        10 + (1 if role["kind"] == "literal" else 0),
                        partition="mono4",
                        before_template={"kind": "rectangular_outline", "maximum_gaps": 1},
                        correspondence={"interior": "fill", "gap": "continue_outward_to_boundary"},
                        after_template={"kind": "filled_frame_with_optional_escape_ray"},
                        emission=role,
                    )
                )
    role_action_possible = family == "relational_object_action"
    if family is None:
        # A delete/recolor action never paints a root-background cell.  This
        # challenge-only support test removes most additive tasks before the
        # larger role grammar is enumerated.
        for background in backgrounds:
            try:
                if all(
                    all(
                        source[row][column] != _background(source, background)
                        for row in range(len(source))
                        for column in range(len(source[0]))
                        if source[row][column] != target[row][column]
                    )
                    for source, target in demonstrations
                ):
                    role_action_possible = True
                    break
            except Undefined:
                continue
    if role_action_possible:
        selectors = (
            "all",
            "unique_min_area",
            "unique_max_area",
            "unique_min_bbox",
            "unique_max_bbox",
            "line",
            "solid_rectangle",
            "non_solid",
            "square",
            "touches_border",
            "interior",
            "unique_shape",
            "repeated_shape",
            "unique_rarest_color",
            "unique_most_color",
        )
        for background in backgrounds:
            for partition in ("mono4", "mono8", "multi4"):
                for selector in selectors:
                    programs.append(
                        _base_program(
                            "relational_object_action",
                            background,
                            7,
                            partition=partition,
                            selector={"kind": selector},
                            before_template={"kind": "selected_normalized_object_support"},
                            after_template={"kind": "delete"},
                            action={"kind": "delete"},
                        )
                    )
                    for role in _color_action_specs(demonstrations):
                        programs.append(
                            _base_program(
                                "relational_object_action",
                                background,
                                8 + (1 if role["kind"] == "literal" else 0),
                                partition=partition,
                                selector={"kind": selector},
                                before_template={"kind": "selected_normalized_object_support"},
                                after_template={"kind": "recolor_support"},
                                action={"kind": "recolor", "color": role},
                            )
                        )
    unique = {_canonical(program): program for program in programs}
    if len(unique) > limits.max_programs:
        raise Undefined("program grammar cap exhausted")
    return tuple(unique[key] for key in sorted(unique))


def _exact_programs(
    demonstrations: Sequence[Pair],
    tests: Sequence[Grid],
    limits: Limits,
    *,
    family: str | None = None,
) -> tuple[tuple[dict[str, Any], ...], int]:
    exact: list[dict[str, Any]] = []
    calls = 0
    scene_cache: dict[tuple[Grid, str], Scene | None] = {}

    def cached_scene(grid: Grid, background: str) -> Scene:
        key = grid, background
        if key not in scene_cache:
            try:
                scene_cache[key] = _scene(grid, background, limits)
            except Undefined:
                scene_cache[key] = None
        scene = scene_cache[key]
        if scene is None:
            raise Undefined("cached root identity is undefined")
        return scene

    for program in _program_pool(demonstrations, limits, family=family):
        try:
            train_outputs = []
            for source, _ in demonstrations:
                scene = cached_scene(source, str(program["background"]))
                train_outputs.append(_execute_on_scene(program, scene, limits)[0])
                calls += 1
            for source in tests:
                scene = cached_scene(source, str(program["background"]))
                _execute_on_scene(program, scene, limits)
                calls += 1
            if calls > limits.max_executor_calls:
                raise Undefined("executor-call cap exhausted")
        except Undefined:
            continue
        if tuple(train_outputs) == tuple(target for _, target in demonstrations):
            exact.append(program)
    if not exact:
        return (), calls
    best = min(int(program["description_length"]) for program in exact)
    near = tuple(
        sorted(
            (program for program in exact if int(program["description_length"]) <= best + limits.mdl_slack),
            key=lambda item: (int(item["description_length"]), _canonical(item)),
        )
    )
    return near, calls


def _behavior(program: Mapping[str, Any], grids: Sequence[Grid], limits: Limits) -> tuple[Grid, ...]:
    return tuple(_execute_internal(program, grid, limits)[0] for grid in grids)


def _loo_guard(program: Mapping[str, Any], demonstrations: Sequence[Pair], limits: Limits) -> tuple[bool, int, int]:
    family = str(program.get("macro"))
    checks = 0
    classes_seen = 0
    for held_out, (source, target) in enumerate(demonstrations):
        training = tuple(pair for index, pair in enumerate(demonstrations) if index != held_out)
        programs, _ = _exact_programs(training, (source,), limits, family=family)
        if not programs:
            return False, checks, classes_seen
        behaviors: dict[str, tuple[Grid, ...]] = {}
        for candidate in programs:
            try:
                outputs = _behavior(candidate, (source,), limits)
            except Undefined:
                continue
            behaviors[_digest([_plain(grid) for grid in outputs])] = outputs
            checks += 1
        classes_seen += len(behaviors)
        if len(behaviors) != 1 or next(iter(behaviors.values())) != (target,):
            return False, checks, classes_seen
    return True, checks, classes_seen


def _rotate90(grid: Grid) -> Grid:
    return tuple(tuple(row) for row in zip(*reversed(grid)))


def _swap_grid(grid: Grid, left: int, right: int) -> Grid:
    return tuple(tuple(right if value == left else left if value == right else value for value in row) for row in grid)


def _swap_program(program: Mapping[str, Any], left: int, right: int) -> dict[str, Any]:
    result = json.loads(_canonical(program))

    def swap_role(role: Any) -> None:
        if isinstance(role, dict):
            if role.get("kind") == "literal":
                value = role.get("color")
                role["color"] = right if value == left else left if value == right else value
            for value in role.values():
                swap_role(value)
        elif isinstance(role, list):
            for value in role:
                swap_role(value)

    swap_role(result)
    return result


def _gauge_guard(program: Mapping[str, Any], demonstrations: Sequence[Pair], limits: Limits) -> tuple[bool, int, int]:
    d4_checks = 0
    palette_checks = 0
    for source, target in demonstrations:
        paired: dict[str, tuple[Grid, Grid]] = {}
        transformed_source, transformed_target = source, target
        for _ in range(4):
            paired.setdefault(_canonical(_plain(transformed_source)), (transformed_source, transformed_target))
            reflected_source = tuple(tuple(reversed(row)) for row in transformed_source)
            reflected_target = tuple(tuple(reversed(row)) for row in transformed_target)
            paired.setdefault(_canonical(_plain(reflected_source)), (reflected_source, reflected_target))
            transformed_source, transformed_target = _rotate90(transformed_source), _rotate90(transformed_target)
        for source_variant, target_variant in paired.values():
            d4_checks += 1
            if d4_checks + palette_checks > limits.max_gauge_checks:
                return False, d4_checks, palette_checks
            try:
                prediction = _execute_internal(program, source_variant, limits)[0]
            except Undefined:
                return False, d4_checks, palette_checks
            if prediction != target_variant:
                return False, d4_checks, palette_checks
        colors = sorted({cell for row in source for cell in row} | {cell for row in target for cell in row})
        absent = next((color for color in range(10) if color not in colors), None)
        swaps = list(itertools.combinations(colors, 2))
        if absent is not None:
            swaps.extend((color, absent) for color in colors)
        for left, right in swaps:
            palette_checks += 1
            if d4_checks + palette_checks > limits.max_gauge_checks:
                return False, d4_checks, palette_checks
            try:
                prediction = _execute_internal(_swap_program(program, left, right), _swap_grid(source, left, right), limits)[0]
            except Undefined:
                return False, d4_checks, palette_checks
            if prediction != _swap_grid(target, left, right):
                return False, d4_checks, palette_checks
    return True, d4_checks, palette_checks


def compile_task(task: Any, limits: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    """Induce at most one behaviorally unique normalized object rewrite."""

    try:
        bounds = Limits.from_value(limits)
        demonstrations, tests = _sanitize(task, bounds)
        programs, calls = _exact_programs(demonstrations, tests, bounds)
    except (Undefined, TypeError, ValueError):
        return []
    if not programs:
        return []
    behaviors: dict[str, list[tuple[dict[str, Any], tuple[Grid, ...]]]] = {}
    for program in programs:
        try:
            outputs = _behavior(program, tests, bounds)
        except Undefined:
            continue
        behaviors.setdefault(_digest([_plain(grid) for grid in outputs]), []).append((program, outputs))
    if len(behaviors) != 1:
        return []
    behavior_hash, equivalent = next(iter(sorted(behaviors.items())))
    equivalent.sort(key=lambda item: (int(item[0]["description_length"]), _canonical(item[0])))
    representative: dict[str, Any] | None = None
    representative_outputs: tuple[Grid, ...] = ()
    loo_counts = (0, 0)
    gauge_counts = (0, 0)
    for program, outputs in equivalent:
        loo_ok, loo_checks, loo_classes = _loo_guard(program, demonstrations, bounds)
        if not loo_ok:
            continue
        gauge_ok, d4_checks, palette_checks = _gauge_guard(program, demonstrations, bounds)
        if not gauge_ok:
            continue
        representative = program
        representative_outputs = outputs
        loo_counts = loo_checks, loo_classes
        gauge_counts = d4_checks, palette_checks
        break
    if representative is None:
        return []
    try:
        train_outputs = _behavior(representative, tuple(source for source, _ in demonstrations), bounds)
    except Undefined:
        return []
    if train_outputs != tuple(target for _, target in demonstrations):
        return []
    candidate = {
        "family": "analogical_object_rewrite",
        "program": json.loads(_canonical(representative)),
        "train_outputs": [_plain(grid) for grid in train_outputs],
        "test_outputs": [_plain(grid) for grid in representative_outputs],
        "complexity": int(representative["description_length"]),
        "evidence": {
            "all_demos_exact": True,
            "exact_replay": True,
            "root_identity_transported": True,
            "normalized_object_templates": True,
            "leave_one_demo_out_reinduction": True,
            "leave_one_out_program_checks": loo_counts[0],
            "leave_one_out_behavior_classes": loo_counts[1],
            "enumeration_complete": True,
            "programs_enumerated": len(_program_pool(demonstrations, bounds)),
            "executor_calls": calls,
            "hard_caps_exhausted": False,
            "near_mdl_programs": len(programs),
            "full_test_behavior_classes": len(behaviors),
            "full_test_behavior_hash": behavior_hash,
            "equivalent_programs": len(equivalent),
            "d4_covariance_checks": gauge_counts[0],
            "palette_covariance_checks": gauge_counts[1],
            "serialized_resolved_coordinates": False,
            "task_identity_observed": False,
            "test_labels_observed": False,
            "solution_store_observed": False,
        },
    }
    candidate["evidence"]["candidate_semantic_hash"] = _digest(candidate)
    return [candidate][: bounds.max_candidates]


def _safe_task(task: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(task, Mapping) or not isinstance(task.get("train"), list) or not isinstance(task.get("test"), list):
        raise Undefined("task splits are invalid")
    return {
        "train": [{"input": example["input"], "output": example["output"]} for example in task["train"]],
        "test": [{"input": example["input"]} for example in task["test"]],
    }


def freeze_scan(
    challenges: Mapping[str, Mapping[str, Any]],
    *,
    limits: Mapping[str, Any] | None = None,
    source_hash: str | None = None,
    entrant_source_hash: str | None = None,
    run_name: str = "analogical-object-rewrite-scan",
) -> dict[str, Any]:
    """Freeze a deterministic challenge-only object-rewrite scan."""

    records: dict[str, Any] = {}
    activated = 0
    for raw_task_id, task in sorted(challenges.items(), key=lambda item: str(item[0])):
        safe = _safe_task(task)
        candidates = compile_task(safe, limits=limits)
        if len(candidates) > 1:
            raise AssertionError("compile_task violated its one-candidate contract")
        if candidates:
            activated += 1
        record = {
            "task_semantic_hash": _digest(safe),
            "status": "candidate" if candidates else "abstention",
            "candidates": candidates,
        }
        record["content_hash"] = _digest(record)
        records[str(raw_task_id)] = record
    body = {
        "schema": SCAN_SCHEMA,
        "schema_version": 1,
        "author": AUTHOR,
        "phase": "prediction_freeze_before_solution_open",
        "label_access": "none",
        "run_name": run_name,
        "source_hash": source_hash,
        "entrant_source_hash": entrant_source_hash,
        "source_task_count": len(challenges),
        "activation_count": activated,
        "records": records,
        "claim_boundary": (
            "Challenge-only deterministic scan. The entrant receives demonstrations and "
            "test inputs; no solution, score, result, baseline, or submission is opened."
        ),
    }
    body["semantic_hash"] = _digest(body)
    body["content_hash"] = _digest(body)
    return body


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".partial")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8", newline="\n")
    temporary.replace(path)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--challenges", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--run-name", default="analogical-object-rewrite-scan")
    args = parser.parse_args(argv)
    raw = args.challenges.read_bytes()
    challenges = json.loads(raw.decode("utf-8-sig"))
    if not isinstance(challenges, Mapping):
        raise ValueError("challenges JSON must contain an object")
    frozen = freeze_scan(
        challenges,
        source_hash=hashlib.sha256(raw).hexdigest(),
        entrant_source_hash=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        run_name=args.run_name,
    )
    _write_json(args.output, frozen)
    print(_canonical({"activation_count": frozen["activation_count"], "content_hash": frozen["content_hash"], "source_task_count": frozen["source_task_count"]}))
    return 0


__all__ = [
    "AUTHOR",
    "Limits",
    "SCHEMA",
    "Undefined",
    "compile_task",
    "execute_program",
    "freeze_scan",
    "replay_program",
]


if __name__ == "__main__":
    raise SystemExit(main())
