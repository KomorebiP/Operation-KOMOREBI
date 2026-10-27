"""Task-local relational delta-algebra induction for PR-LASM Block 14.

The compiler treats every same-shape demonstration as an edit relation.  It
builds a fresh relational vocabulary for the task, anti-unifies changed cells
into small conjunctions, and searches compact decision lists whose actions are
resolved from scene roles.  The resulting program contains neither task IDs
nor resolved coordinates and can be replayed independently.

Compilation is challenge-only: demonstrations and test inputs are accepted,
attached test outputs are ignored, and no score/baseline/solution artifact is
read.  Admission requires exact demonstration replay, genuine leave-one-demo-
out re-induction, a single full-test behavior quotient at minimum description
length, D4 covariance, palette covariance, and non-exhausted hard budgets.

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
SCHEMA = "komorebi.pr_lasm.block14.delta_algebra.program.v1"
SCAN_SCHEMA = "komorebi.pr_lasm.block14.delta_algebra.scan_freeze.v1"
AUTHOR = "Komorebi P."
ORTHOGONAL: tuple[Cell, ...] = ((-1, 0), (0, -1), (0, 1), (1, 0))
DIAGONAL: tuple[Cell, ...] = ((-1, -1), (-1, 1), (1, -1), (1, 1))
EIGHT: tuple[Cell, ...] = ORTHOGONAL + DIAGONAL


class Undefined(ValueError):
    """A scene role or a bounded induction step is undefined."""


@dataclass(frozen=True, slots=True)
class Limits:
    max_grid_cells: int = 900
    max_examples: int = 10
    max_components: int = 160
    max_features: int = 72
    max_atoms: int = 192
    max_conjunction: int = 2
    max_selectors: int = 768
    max_rule_candidates: int = 512
    max_programs: int = 4_096
    max_executor_calls: int = 120_000
    max_rules: int = 3
    max_mdl: int = 40
    mdl_slack: int = 0
    max_candidates: int = 1
    min_rule_demo_witnesses: int = 2
    max_gauge_checks: int = 1_024

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
            "max_features": 128,
            "max_atoms": 512,
            "max_conjunction": 3,
            "max_selectors": 4_096,
            "max_rule_candidates": 2_048,
            "max_programs": 20_000,
            "max_executor_calls": 1_000_000,
            "max_rules": 4,
            "max_mdl": 128,
            "mdl_slack": 3,
            "max_candidates": 1,
            "min_rule_demo_witnesses": 10,
            "max_gauge_checks": 4_096,
        }
        aliases = {"candidate_cap": "max_candidates"}
        fields: dict[str, int] = {}
        for name in cls.__dataclass_fields__:
            raw = value.get(name, value.get(next((key for key, item in aliases.items() if item == name), ""), getattr(defaults, name)))
            if isinstance(raw, bool) or not isinstance(raw, int):
                raise Undefined(f"limits.{name} must be an integer")
            minimum = 0 if name == "mdl_slack" else 1
            if raw < minimum:
                raise Undefined(f"limits.{name} is below {minimum}")
            fields[name] = min(raw, ceilings[name])
        return cls(**fields)


@dataclass(frozen=True, slots=True)
class Component:
    color: int
    cells: frozenset[Cell]
    bbox: tuple[int, int, int, int]
    shape: tuple[Cell, ...]

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
    def solid(self) -> bool:
        return self.area == self.height * self.width


@dataclass(slots=True)
class Scene:
    grid: Grid
    background_role: str
    background: int
    foreground: frozenset[Cell]
    color_counts: Counter[int]
    foreground_color_counts: Counter[int]
    components: tuple[Component, ...]
    cell_component: dict[Cell, int]
    foreground_bbox: tuple[int, int, int, int] | None
    features: tuple[tuple[Mapping[str, Any], ...], ...]


@dataclass(frozen=True, slots=True)
class Atom:
    feature: str
    op: str
    value: Any

    def record(self) -> dict[str, Any]:
        return {"feature": self.feature, "op": self.op, "value": self.value}


@dataclass(frozen=True, slots=True)
class SelectorCandidate:
    atoms: tuple[Atom, ...]
    selected_mask: int
    changed_mask: int
    complexity: int


@dataclass(frozen=True, slots=True)
class RuleCandidate:
    action: Mapping[str, Any]
    selector: SelectorCandidate
    complexity: int


@dataclass(slots=True)
class SearchStats:
    atoms_considered: int = 0
    selectors_considered: int = 0
    rules_considered: int = 0
    programs_considered: int = 0
    executor_calls: int = 0
    exhausted: bool = False


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _plain(grid: Grid) -> list[list[int]]:
    return [list(row) for row in grid]


def _grid(value: Any, limits: Limits) -> Grid:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or not value:
        raise Undefined("grid must be a nonempty sequence")
    rows: list[tuple[int, ...]] = []
    width: int | None = None
    for raw_row in value:
        if not isinstance(raw_row, Sequence) or isinstance(raw_row, (str, bytes)) or not raw_row:
            raise Undefined("grid row must be a nonempty sequence")
        row: list[int] = []
        for raw_cell in raw_row:
            if isinstance(raw_cell, bool) or not isinstance(raw_cell, int) or not 0 <= raw_cell <= 9:
                raise Undefined("ARC colors must be integer values in [0, 9]")
            row.append(int(raw_cell))
        if width is None:
            width = len(row)
        elif len(row) != width:
            raise Undefined("grid is ragged")
        rows.append(tuple(row))
    if len(rows) * int(width or 0) > limits.max_grid_cells:
        raise Undefined("grid exceeds the finite cell budget")
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
        raise Undefined("task arity is outside the finite grammar")
    demonstrations: list[Pair] = []
    for example in train:
        if not isinstance(example, Mapping):
            raise Undefined("invalid demonstration")
        source = _grid(example.get("input"), limits)
        target = _grid(example.get("output"), limits)
        if _shape(source) != _shape(target) or source == target:
            raise Undefined("delta algebra requires nonidentity same-shape pairs")
        demonstrations.append((source, target))
    tests: list[Grid] = []
    for example in test:
        if not isinstance(example, Mapping):
            raise Undefined("invalid test example")
        # Attached labels are intentionally ignored.
        tests.append(_grid(example.get("input"), limits))
    return tuple(demonstrations), tuple(tests)


def _shape(grid: Grid) -> tuple[int, int]:
    return len(grid), len(grid[0])


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
        values = (grid[0][0], grid[0][-1], grid[-1][0], grid[-1][-1])
        if len(set(values)) != 1:
            raise Undefined("corner role is tied")
        return values[0]
    raise Undefined("unknown background role")


def _bbox(cells: Iterable[Cell]) -> tuple[int, int, int, int]:
    points = tuple(cells)
    if not points:
        raise Undefined("empty bounding box")
    return (
        min(row for row, _ in points),
        max(row for row, _ in points),
        min(column for _, column in points),
        max(column for _, column in points),
    )


def _normalize(cells: Iterable[Cell]) -> tuple[Cell, ...]:
    points = tuple(cells)
    top, _, left, _ = _bbox(points)
    return tuple(sorted((row - top, column - left) for row, column in points))


def _components(grid: Grid, background: int, limits: Limits) -> tuple[tuple[Component, ...], dict[Cell, int]]:
    height, width = _shape(grid)
    remaining = {
        (row, column)
        for row in range(height)
        for column in range(width)
        if grid[row][column] != background
    }
    components: list[Component] = []
    while remaining:
        seed = min(remaining)
        color = grid[seed[0]][seed[1]]
        remaining.remove(seed)
        cells = {seed}
        queue = deque([seed])
        while queue:
            row, column = queue.popleft()
            for dr, dc in ORTHOGONAL:
                point = row + dr, column + dc
                if point in remaining and grid[point[0]][point[1]] == color:
                    remaining.remove(point)
                    cells.add(point)
                    queue.append(point)
        box = _bbox(cells)
        components.append(Component(color, frozenset(cells), box, _normalize(cells)))
        if len(components) > limits.max_components:
            raise Undefined("component budget exhausted")
    components.sort(key=lambda item: (item.bbox, item.color, item.shape))
    mapping = {
        cell: index
        for index, component in enumerate(components)
        for cell in component.cells
    }
    return tuple(components), mapping


def _rank_role(value: int, population: Sequence[int]) -> str:
    if not population:
        return "none"
    minimum, maximum = min(population), max(population)
    min_unique = population.count(minimum) == 1
    max_unique = population.count(maximum) == 1
    if len(population) == 1:
        return "only"
    if value == minimum and min_unique:
        return "unique_min"
    if value == maximum and max_unique:
        return "unique_max"
    if value == minimum:
        return "tied_min"
    if value == maximum:
        return "tied_max"
    return "middle"


def _inside_zone(cell: Cell, box: tuple[int, int, int, int] | None) -> str:
    if box is None:
        return "none"
    row, column = cell
    top, bottom, left, right = box
    if not (top <= row <= bottom and left <= column <= right):
        return "outside"
    if row in {top, bottom} or column in {left, right}:
        return "border"
    return "interior"


def _axis_between(
    grid: Grid,
    cell: Cell,
    background: int,
    directions: Sequence[Cell],
    *,
    require_same: bool,
) -> bool:
    height, width = _shape(grid)
    row, column = cell
    if tuple(directions) == ORTHOGONAL:
        pairs = (((-1, 0), (1, 0)), ((0, -1), (0, 1)))
    elif tuple(directions) == DIAGONAL:
        pairs = (((-1, -1), (1, 1)), ((-1, 1), (1, -1)))
    else:
        raise Undefined("between relation has unknown directions")
    for first, second in pairs:
        seen: list[int] = []
        for dr, dc in (first, second):
            rr, cc = row + dr, column + dc
            found: int | None = None
            while 0 <= rr < height and 0 <= cc < width:
                if grid[rr][cc] != background:
                    found = grid[rr][cc]
                    break
                rr += dr
                cc += dc
            if found is None:
                break
            seen.append(found)
        if len(seen) == 2 and (not require_same or seen[0] == seen[1]):
            return True
    return False


def _orbit_count(grid: Grid, cell: Cell, cells: frozenset[Cell], box: tuple[int, int, int, int]) -> int:
    row, column = cell
    top, bottom, left, right = box
    points = {
        (row, column),
        (top + bottom - row, column),
        (row, left + right - column),
        (top + bottom - row, left + right - column),
    }
    if bottom - top == right - left:
        rr, cc = row - top, column - left
        size = bottom - top
        points.update(
            {
                (top + cc, left + rr),
                (top + cc, left + size - rr),
                (top + size - cc, left + rr),
                (top + size - cc, left + size - rr),
            }
        )
    return sum(point in cells for point in points)


def _visible_colors(grid: Grid, cell: Cell, background: int, directions: Sequence[Cell]) -> tuple[int, ...]:
    height, width = _shape(grid)
    answer: list[int] = []
    for dr, dc in directions:
        row, column = cell[0] + dr, cell[1] + dc
        while 0 <= row < height and 0 <= column < width:
            value = grid[row][column]
            if value != background:
                answer.append(value)
                break
            row += dr
            column += dc
    return tuple(answer)


def _nearest_colors(grid: Grid, cell: Cell, foreground: frozenset[Cell], metric: str) -> tuple[int, tuple[int, ...]]:
    if not foreground:
        raise Undefined("nearest foreground role is absent")
    row, column = cell
    if metric == "manhattan":
        distances = {point: abs(point[0] - row) + abs(point[1] - column) for point in foreground}
    elif metric == "chebyshev":
        distances = {point: max(abs(point[0] - row), abs(point[1] - column)) for point in foreground}
    else:
        raise Undefined("unknown distance metric")
    distance = min(distances.values())
    colors = tuple(sorted({grid[rr][cc] for (rr, cc), value in distances.items() if value == distance}))
    return distance, colors


def _feature_table(
    grid: Grid,
    background_role: str,
    background: int,
    foreground: frozenset[Cell],
    counts: Counter[int],
    foreground_counts: Counter[int],
    components: tuple[Component, ...],
    cell_component: Mapping[Cell, int],
    foreground_bbox: tuple[int, int, int, int] | None,
) -> tuple[tuple[Mapping[str, Any], ...], ...]:
    height, width = _shape(grid)
    component_areas = [component.area for component in components]
    shape_counts = Counter(component.shape for component in components)
    rows_fg = [sum((row, column) in foreground for column in range(width)) for row in range(height)]
    cols_fg = [sum((row, column) in foreground for row in range(height)) for column in range(width)]
    result: list[tuple[Mapping[str, Any], ...]] = []
    for row in range(height):
        feature_row: list[Mapping[str, Any]] = []
        for column in range(width):
            cell = (row, column)
            value = grid[row][column]
            is_fg = cell in foreground
            neighbors4 = [
                (row + dr, column + dc)
                for dr, dc in ORTHOGONAL
                if 0 <= row + dr < height and 0 <= column + dc < width
            ]
            neighbors8 = [
                (row + dr, column + dc)
                for dr, dc in EIGHT
                if 0 <= row + dr < height and 0 <= column + dc < width
            ]
            row_same = sum(grid[row][cc] == value for cc in range(width))
            col_same = sum(grid[rr][column] == value for rr in range(height))
            manhattan, near_manhattan = _nearest_colors(grid, cell, foreground, "manhattan") if foreground else (-1, ())
            chebyshev, near_chebyshev = _nearest_colors(grid, cell, foreground, "chebyshev") if foreground else (-1, ())
            box_zone = _inside_zone(cell, foreground_bbox)
            containing = [
                index
                for index, component in enumerate(components)
                if component.bbox[0] <= row <= component.bbox[1]
                and component.bbox[2] <= column <= component.bbox[3]
            ]
            bbox_borders = [
                index
                for index in containing
                if row in {components[index].bbox[0], components[index].bbox[1]}
                or column in {components[index].bbox[2], components[index].bbox[3]}
            ]
            index = cell_component.get(cell)
            component = components[index] if index is not None else None
            color_population = list(foreground_counts.values())
            color_role = "background" if value == background else _rank_role(foreground_counts[value], color_population)
            visible4 = _visible_colors(grid, cell, background, ORTHOGONAL)
            visible8 = _visible_colors(grid, cell, background, EIGHT)
            pair_fg = sorted((rows_fg[row], cols_fg[column]))
            pair_same = sorted((row_same, col_same))
            features: dict[str, Any] = {
                "source_is_background": value == background,
                "source_is_foreground": is_fg,
                "source_color_role": color_role,
                "source_color_count": counts[value],
                "source_color_is_singleton": counts[value] == 1,
                "cell_is_border": row in {0, height - 1} or column in {0, width - 1},
                "cell_is_corner": row in {0, height - 1} and column in {0, width - 1},
                "cell_border_distance": min(row, height - 1 - row, column, width - 1 - column),
                "cell_center_or_axis": (2 * row == height - 1) or (2 * column == width - 1),
                "cell_checker_parity": (row + column) % 2,
                "n4_foreground": sum(point in foreground for point in neighbors4),
                "n8_foreground": sum(point in foreground for point in neighbors8),
                "n4_same": sum(grid[rr][cc] == value for rr, cc in neighbors4),
                "n8_same": sum(grid[rr][cc] == value for rr, cc in neighbors8),
                "row_col_foreground_counts": f"{pair_fg[0]}:{pair_fg[1]}",
                "row_col_same_counts": f"{pair_same[0]}:{pair_same[1]}",
                "row_or_col_has_foreground": rows_fg[row] > 0 or cols_fg[column] > 0,
                "row_and_col_have_foreground": rows_fg[row] > 0 and cols_fg[column] > 0,
                "between_axis_foreground": _axis_between(grid, cell, background, ORTHOGONAL, require_same=False),
                "between_axis_same_color": _axis_between(grid, cell, background, ORTHOGONAL, require_same=True),
                "between_diagonal_foreground": _axis_between(grid, cell, background, DIAGONAL, require_same=False),
                "between_diagonal_same_color": _axis_between(grid, cell, background, DIAGONAL, require_same=True),
                "visible_axis_count": len(visible4),
                "visible_d8_count": len(visible8),
                "visible_axis_one_color": bool(visible4) and len(set(visible4)) == 1,
                "visible_d8_one_color": bool(visible8) and len(set(visible8)) == 1,
                "nearest_manhattan_distance": manhattan,
                "nearest_chebyshev_distance": chebyshev,
                "nearest_manhattan_one_color": len(near_manhattan) == 1,
                "nearest_chebyshev_one_color": len(near_chebyshev) == 1,
                "foreground_bbox_zone": box_zone,
                "inside_any_component_bbox_count": len(containing),
                "on_any_component_bbox_border_count": len(bbox_borders),
                "inside_unique_component_bbox": len(containing) == 1,
                "component_member": component is not None,
                "component_area": component.area if component else -1,
                "component_area_role": _rank_role(component.area, component_areas) if component else "none",
                "component_shape_frequency": shape_counts[component.shape] if component else 0,
                "component_solid": component.solid if component else False,
                "component_line": (component.height == 1 or component.width == 1) if component else False,
                "component_square": (component.height == component.width) if component else False,
                "component_touches_border": (
                    component.bbox[0] == 0
                    or component.bbox[1] == height - 1
                    or component.bbox[2] == 0
                    or component.bbox[3] == width - 1
                ) if component else False,
                "component_local_edge_distance": (
                    min(
                        row - component.bbox[0],
                        component.bbox[1] - row,
                        column - component.bbox[2],
                        component.bbox[3] - column,
                    ) if component else -1
                ),
                "foreground_bbox_orbit_count": (
                    _orbit_count(grid, cell, foreground, foreground_bbox) if foreground_bbox else 0
                ),
            }
            feature_row.append(features)
        result.append(tuple(feature_row))
    return tuple(result)


def _scene(grid: Grid, background_role: str, limits: Limits) -> Scene:
    background = _background(grid, background_role)
    counts = Counter(cell for row in grid for cell in row)
    foreground = frozenset(
        (row, column)
        for row, values in enumerate(grid)
        for column, value in enumerate(values)
        if value != background
    )
    if not foreground:
        raise Undefined("foreground is empty")
    foreground_counts = Counter(grid[row][column] for row, column in foreground)
    components, cell_component = _components(grid, background, limits)
    box = _bbox(foreground)
    features = _feature_table(
        grid,
        background_role,
        background,
        foreground,
        counts,
        foreground_counts,
        components,
        cell_component,
        box,
    )
    if len(features[0][0]) > limits.max_features:
        raise Undefined("feature grammar exceeds its hard cap")
    return Scene(
        grid,
        background_role,
        background,
        foreground,
        counts,
        foreground_counts,
        components,
        cell_component,
        box,
        features,
    )


def _unique_color_by_count(scene: Scene, order: str) -> int:
    if not scene.foreground_color_counts:
        raise Undefined("foreground color population is empty")
    wanted = (
        min(scene.foreground_color_counts.values())
        if order == "min"
        else max(scene.foreground_color_counts.values())
    )
    winners = sorted(color for color, count in scene.foreground_color_counts.items() if count == wanted)
    if len(winners) != 1:
        raise Undefined("foreground color role is tied")
    return winners[0]


def _action_color(action: Mapping[str, Any], scene: Scene, cell: Cell) -> int:
    kind = action.get("kind")
    if kind == "literal":
        color = action.get("color")
        if isinstance(color, bool) or not isinstance(color, int) or not 0 <= color <= 9:
            raise Undefined("literal action color is invalid")
        return color
    if kind == "background":
        return scene.background
    if kind == "only_foreground":
        colors = sorted(scene.foreground_color_counts)
        if len(colors) != 1:
            raise Undefined("only-foreground role is tied")
        return colors[0]
    if kind == "rarest_foreground":
        return _unique_color_by_count(scene, "min")
    if kind == "most_foreground":
        return _unique_color_by_count(scene, "max")
    if kind in {"nearest_manhattan", "nearest_chebyshev"}:
        metric = "manhattan" if kind.endswith("manhattan") else "chebyshev"
        _, colors = _nearest_colors(scene.grid, cell, scene.foreground, metric)
        if len(colors) != 1:
            raise Undefined("nearest-color action is tied")
        return colors[0]
    if kind in {"visible_axis", "visible_d8"}:
        directions = ORTHOGONAL if kind == "visible_axis" else EIGHT
        colors = set(_visible_colors(scene.grid, cell, scene.background, directions))
        if len(colors) != 1:
            raise Undefined("visible-ray color action is tied")
        return next(iter(colors))
    if kind == "enclosing_component":
        row, column = cell
        colors = {
            component.color
            for component in scene.components
            if component.bbox[0] <= row <= component.bbox[1]
            and component.bbox[2] <= column <= component.bbox[3]
        }
        if len(colors) != 1:
            raise Undefined("enclosing-component color action is tied")
        return next(iter(colors))
    raise Undefined("unknown delta action")


def _action_specs(demonstrations: Sequence[Pair]) -> tuple[dict[str, Any], ...]:
    changed_colors = sorted(
        {
            target[row][column]
            for source, target in demonstrations
            for row in range(len(source))
            for column in range(len(source[0]))
            if source[row][column] != target[row][column]
        }
    )
    actions: list[dict[str, Any]] = [
        {"kind": "background"},
        {"kind": "only_foreground"},
        {"kind": "rarest_foreground"},
        {"kind": "most_foreground"},
        {"kind": "nearest_manhattan"},
        {"kind": "nearest_chebyshev"},
        {"kind": "visible_axis"},
        {"kind": "visible_d8"},
        {"kind": "enclosing_component"},
    ]
    actions.extend({"kind": "literal", "color": color} for color in changed_colors)
    return tuple(actions)


def _atom_holds(atom: Atom, value: Any) -> bool:
    if atom.op == "eq":
        return value == atom.value
    if isinstance(value, bool) or not isinstance(value, int):
        return False
    if atom.op == "le":
        return value <= atom.value
    if atom.op == "ge":
        return value >= atom.value
    raise Undefined("unknown selector relation")


def _selector_holds(selector: Mapping[str, Any], features: Mapping[str, Any]) -> bool:
    atoms = selector.get("all")
    if not isinstance(atoms, Sequence) or isinstance(atoms, (str, bytes)) or not atoms:
        raise Undefined("selector conjunction is invalid")
    for raw in atoms:
        if not isinstance(raw, Mapping):
            raise Undefined("selector atom is invalid")
        name, op, value = raw.get("feature"), raw.get("op"), raw.get("value")
        if not isinstance(name, str) or name not in features or op not in {"eq", "le", "ge"}:
            raise Undefined("selector atom lies outside the grammar")
        if not _atom_holds(Atom(name, str(op), value), features[name]):
            return False
    return True


def _execute_internal(program: Mapping[str, Any], grid: Grid, limits: Limits) -> tuple[Grid, Scene, tuple[dict[str, Any], ...]]:
    if not isinstance(program, Mapping) or program.get("schema") != SCHEMA or program.get("operator") != "delta_decision_list":
        raise Undefined("invalid delta-algebra program")
    background_role = program.get("background")
    if background_role not in {"mode", "border_mode", "corners"}:
        raise Undefined("invalid background role")
    rules = program.get("rules")
    if not isinstance(rules, Sequence) or isinstance(rules, (str, bytes)) or not 1 <= len(rules) <= limits.max_rules:
        raise Undefined("invalid decision list")
    scene = _scene(grid, str(background_role), limits)
    output = [list(row) for row in grid]
    applied: list[dict[str, Any]] = []
    for index, raw_rule in enumerate(rules):
        if not isinstance(raw_rule, Mapping):
            raise Undefined("rule is invalid")
        selector, action = raw_rule.get("selector"), raw_rule.get("action")
        if not isinstance(selector, Mapping) or not isinstance(action, Mapping):
            raise Undefined("rule fields are invalid")
        selected: list[Cell] = []
        paint_counts: Counter[int] = Counter()
        for row in range(len(grid)):
            for column in range(len(grid[0])):
                if _selector_holds(selector, scene.features[row][column]):
                    color = _action_color(action, scene, (row, column))
                    output[row][column] = color
                    selected.append((row, column))
                    paint_counts[color] += 1
        applied.append(
            {
                "rule_index": index,
                "selected_count": len(selected),
                "selected_cells": [[row, column] for row, column in selected],
                "paint_histogram": {str(color): count for color, count in sorted(paint_counts.items())},
            }
        )
    result = tuple(tuple(row) for row in output)
    return result, scene, tuple(applied)


def execute_program(program: Mapping[str, Any], value: Any) -> list[list[int]]:
    """Execute one serialized task-local delta program."""

    limits = Limits()
    grid = _grid(value, limits)
    output, _, _ = _execute_internal(program, grid, limits)
    return _plain(output)


def replay_program(program: Mapping[str, Any], value: Any) -> dict[str, Any]:
    """Tournament replay hook with parse, select, and render stages."""

    limits = Limits()
    grid = _grid(value, limits)
    output, scene, applied = _execute_internal(program, grid, limits)
    scene_record = {
        "kind": "delta_scene",
        "shape": list(_shape(grid)),
        "background_role": scene.background_role,
        "background": scene.background,
        "foreground_count": len(scene.foreground),
        "component_count": len(scene.components),
        "feature_vocabulary": sorted(scene.features[0][0]),
    }
    edit_record = {
        "kind": "relational_edit_set",
        "rules": list(applied),
        "edit_count": sum(
            output[row][column] != grid[row][column]
            for row in range(len(grid))
            for column in range(len(grid[0]))
        ),
    }
    return {
        "output": _plain(output),
        "stages": [
            {"name": "parse-relational-scene", "input": _plain(grid), "output": scene_record},
            {"name": "resolve-task-local-edit-set", "input": scene_record, "output": edit_record},
            {"name": "render-delta", "input": edit_record, "output": _plain(output)},
        ],
    }


def _atom_complexity(atom: Atom) -> int:
    directional = atom.feature in {
        "between_axis_foreground",
        "between_axis_same_color",
        "between_diagonal_foreground",
        "between_diagonal_same_color",
        "visible_axis_count",
        "visible_d8_count",
        "visible_axis_one_color",
        "visible_d8_one_color",
        "foreground_bbox_orbit_count",
    }
    threshold = atom.op != "eq"
    absolute_cardinality = atom.feature in {
        "source_color_count",
        "cell_border_distance",
        "n4_foreground",
        "n8_foreground",
        "n4_same",
        "n8_same",
        "visible_axis_count",
        "visible_d8_count",
        "nearest_manhattan_distance",
        "nearest_chebyshev_distance",
        "inside_any_component_bbox_count",
        "on_any_component_bbox_border_count",
        "component_area",
        "component_shape_frequency",
        "component_local_edge_distance",
        "foreground_bbox_orbit_count",
    }
    return 1 + int(directional) + int(threshold) + int(absolute_cardinality)


def _action_complexity(action: Mapping[str, Any]) -> int:
    kind = action.get("kind")
    if kind in {"background", "only_foreground", "rarest_foreground", "most_foreground"}:
        return 1
    if kind == "literal":
        return 2
    return 3


def _make_atom_masks(
    scenes: Sequence[Scene],
    targets: Sequence[Grid],
    changed_mask: int,
    limits: Limits,
    stats: SearchStats,
) -> tuple[list[Atom], list[int], list[int]]:
    all_features = sorted(scenes[0].features[0][0])
    offsets: list[int] = []
    cursor = 0
    for scene in scenes:
        offsets.append(cursor)
        cursor += len(scene.grid) * len(scene.grid[0])
    positive_values: dict[str, set[Any]] = {name: set() for name in all_features}
    for demo, scene in enumerate(scenes):
        width = len(scene.grid[0])
        for row in range(len(scene.grid)):
            for column in range(width):
                bit = 1 << (offsets[demo] + row * width + column)
                if changed_mask & bit:
                    for name, value in scene.features[row][column].items():
                        positive_values[name].add(value)
    atoms: list[Atom] = []
    for name in all_features:
        for value in sorted(positive_values[name], key=_canonical):
            atoms.append(Atom(name, "eq", value))
            if isinstance(value, int) and not isinstance(value, bool) and -1 <= value <= 32:
                atoms.append(Atom(name, "le", value))
                atoms.append(Atom(name, "ge", value))
    masks_by_record: dict[str, tuple[Atom, int]] = {}
    for atom in atoms:
        mask = 0
        for demo, scene in enumerate(scenes):
            width = len(scene.grid[0])
            for row in range(len(scene.grid)):
                for column in range(width):
                    if _atom_holds(atom, scene.features[row][column][atom.feature]):
                        mask |= 1 << (offsets[demo] + row * width + column)
        if mask & changed_mask:
            key = str(mask)
            previous = masks_by_record.get(key)
            if previous is None or (_atom_complexity(atom), _canonical(atom.record())) < (
                _atom_complexity(previous[0]),
                _canonical(previous[0].record()),
            ):
                masks_by_record[key] = (atom, mask)
    reduced = sorted(masks_by_record.values(), key=lambda item: (_atom_complexity(item[0]), _canonical(item[0].record())))
    stats.atoms_considered += len(reduced)
    if len(reduced) > limits.max_atoms:
        stats.exhausted = True
        return [], [], offsets
    return [item[0] for item in reduced], [item[1] for item in reduced], offsets


def _mine_selectors(
    scenes: Sequence[Scene],
    targets: Sequence[Grid],
    action: Mapping[str, Any],
    all_changed_mask: int,
    limits: Limits,
    stats: SearchStats,
) -> tuple[SelectorCandidate, ...]:
    total_cells = sum(len(scene.grid) * len(scene.grid[0]) for scene in scenes)
    offsets: list[int] = []
    cursor = 0
    good_mask = 0
    bad_mask = 0
    changed_good_mask = 0
    demo_masks: list[int] = []
    for demo, (scene, target) in enumerate(zip(scenes, targets)):
        offsets.append(cursor)
        demo_mask = 0
        width = len(scene.grid[0])
        for row in range(len(scene.grid)):
            for column in range(width):
                bit = 1 << cursor
                demo_mask |= bit
                try:
                    color = _action_color(action, scene, (row, column))
                except Undefined:
                    bad_mask |= bit
                else:
                    if target[row][column] == color:
                        good_mask |= bit
                        if scene.grid[row][column] != target[row][column]:
                            changed_good_mask |= bit
                    else:
                        bad_mask |= bit
                cursor += 1
        demo_masks.append(demo_mask)
    if changed_good_mask == 0:
        return ()
    required_witnesses = min(limits.min_rule_demo_witnesses, len(scenes))
    if sum(bool(changed_good_mask & mask) for mask in demo_masks) < required_witnesses:
        return ()
    atoms, atom_masks, _ = _make_atom_masks(scenes, targets, changed_good_mask, limits, stats)
    if stats.exhausted:
        return ()
    selectors: dict[str, SelectorCandidate] = {}
    all_mask = (1 << total_cells) - 1
    for depth in range(1, limits.max_conjunction + 1):
        for indices in itertools.combinations(range(len(atoms)), depth):
            selected = all_mask
            for index in indices:
                selected &= atom_masks[index]
            if not selected or selected & bad_mask:
                continue
            coverage = selected & changed_good_mask
            if not coverage:
                continue
            if sum(bool(coverage & mask) for mask in demo_masks) < required_witnesses:
                continue
            chosen = tuple(atoms[index] for index in indices)
            complexity = sum(_atom_complexity(atom) for atom in chosen)
            candidate = SelectorCandidate(chosen, selected, coverage, complexity)
            key = str(coverage)
            previous = selectors.get(key)
            if previous is None or (complexity, _canonical([atom.record() for atom in chosen])) < (
                previous.complexity,
                _canonical([atom.record() for atom in previous.atoms]),
            ):
                selectors[key] = candidate
            stats.selectors_considered += 1
            if stats.selectors_considered > limits.max_selectors * max(1, len(_action_specs(tuple((scene.grid, target) for scene, target in zip(scenes, targets))))):
                stats.exhausted = True
                return ()
    ordered = sorted(
        selectors.values(),
        key=lambda item: (item.complexity, -item.changed_mask.bit_count(), _canonical([atom.record() for atom in item.atoms])),
    )
    if len(ordered) > limits.max_selectors:
        stats.exhausted = True
        return ()
    return tuple(ordered)


def _program_record(background: str, rules: Sequence[RuleCandidate]) -> dict[str, Any]:
    records = [
        {
            "selector": {"all": [atom.record() for atom in rule.selector.atoms]},
            "action": dict(rule.action),
        }
        for rule in rules
    ]
    records.sort(key=_canonical)
    complexity = 1 + (0 if background == "mode" else 1) + sum(rule.complexity + 1 for rule in rules)
    return {
        "schema": SCHEMA,
        "operator": "delta_decision_list",
        "background": background,
        "rules": records,
        "default": "identity",
        "description_length": complexity,
    }


def _enumerate_programs_for_background(
    demonstrations: Sequence[Pair],
    tests: Sequence[Grid],
    background: str,
    limits: Limits,
    stats: SearchStats,
) -> tuple[dict[str, Any], ...]:
    try:
        scenes = tuple(_scene(source, background, limits) for source, _ in demonstrations)
        test_scenes = tuple(_scene(source, background, limits) for source in tests)
    except Undefined:
        return ()
    targets = tuple(target for _, target in demonstrations)
    changed_all = 0
    cursor = 0
    for source, target in demonstrations:
        for row in range(len(source)):
            for column in range(len(source[0])):
                if source[row][column] != target[row][column]:
                    changed_all |= 1 << cursor
                cursor += 1
    rules: list[RuleCandidate] = []
    seen_action_behavior: dict[str, Mapping[str, Any]] = {}
    for action in _action_specs(demonstrations):
        # Equivalent role actions on every observed source cell share one grammar branch.
        behavior: list[Any] = []
        valid = True
        for scene in (*scenes, *test_scenes):
            colors: list[int | None] = []
            for row in range(len(scene.grid)):
                for column in range(len(scene.grid[0])):
                    try:
                        colors.append(_action_color(action, scene, (row, column)))
                    except Undefined:
                        colors.append(None)
            behavior.append(colors)
        behavior_key = _digest(behavior)
        previous = seen_action_behavior.get(behavior_key)
        if previous is not None and (_action_complexity(previous), _canonical(previous)) <= (
            _action_complexity(action),
            _canonical(action),
        ):
            continue
        seen_action_behavior[behavior_key] = action
        selectors = _mine_selectors(scenes, targets, action, changed_all, limits, stats)
        if stats.exhausted:
            return ()
        for selector in selectors:
            rules.append(RuleCandidate(action, selector, _action_complexity(action) + selector.complexity))
    # Deduplicate identical changed coverage/action behavior while retaining the shortest rule.
    deduplicated: dict[str, RuleCandidate] = {}
    for rule in rules:
        key = f"{rule.selector.changed_mask}:{_digest(rule.action)}"
        previous = deduplicated.get(key)
        if previous is None or (rule.complexity, _canonical(rule.action)) < (previous.complexity, _canonical(previous.action)):
            deduplicated[key] = rule
    ordered_rules = sorted(
        deduplicated.values(),
        key=lambda item: (item.complexity, -item.selector.changed_mask.bit_count(), _canonical(item.action), _canonical([atom.record() for atom in item.selector.atoms])),
    )
    stats.rules_considered += len(ordered_rules)
    if len(ordered_rules) > limits.max_rule_candidates:
        stats.exhausted = True
        return ()
    by_bit: dict[int, list[int]] = {}
    for index, rule in enumerate(ordered_rules):
        mask = rule.selector.changed_mask & changed_all
        pending = mask
        while pending:
            low = pending & -pending
            bit = low.bit_length() - 1
            by_bit.setdefault(bit, []).append(index)
            pending ^= low
    programs: dict[str, dict[str, Any]] = {}
    best_complexity: int | None = None
    minimum_rule_increment = min((rule.complexity + 1 for rule in ordered_rules), default=10**9)

    def visit(covered: int, chosen: tuple[int, ...]) -> None:
        nonlocal best_complexity
        if stats.exhausted:
            return
        if covered & changed_all == changed_all:
            selected_rules = tuple(ordered_rules[index] for index in chosen)
            program = _program_record(background, selected_rules)
            complexity = int(program["description_length"])
            if complexity <= limits.max_mdl and (
                best_complexity is None or complexity <= best_complexity + limits.mdl_slack
            ):
                if best_complexity is None or complexity < best_complexity:
                    best_complexity = complexity
                    programs.clear()
                key = _canonical(program)
                if key not in programs:
                    programs[key] = program
                    stats.programs_considered += 1
                    if stats.programs_considered > limits.max_programs:
                        stats.exhausted = True
            return
        if len(chosen) >= limits.max_rules:
            return
        if best_complexity is not None:
            partial_rules = tuple(ordered_rules[index] for index in chosen)
            partial_complexity = int(_program_record(background, partial_rules)["description_length"]) if partial_rules else 1 + (0 if background == "mode" else 1)
            if partial_complexity + minimum_rule_increment > best_complexity + limits.mdl_slack:
                return
        uncovered = changed_all & ~covered
        first_bit = (uncovered & -uncovered).bit_length() - 1
        for index in by_bit.get(first_bit, ()):
            if index in chosen:
                continue
            rule = ordered_rules[index]
            new_covered = covered | rule.selector.changed_mask
            if new_covered == covered:
                continue
            visit(new_covered, chosen + (index,))

    visit(0, ())
    if stats.exhausted:
        return ()
    exact: list[dict[str, Any]] = []
    for program in programs.values():
        try:
            outputs = []
            for source, _ in demonstrations:
                result, _, _ = _execute_internal(program, source, limits)
                outputs.append(result)
                stats.executor_calls += 1
            for source in tests:
                _execute_internal(program, source, limits)
                stats.executor_calls += 1
            if stats.executor_calls > limits.max_executor_calls:
                stats.exhausted = True
                return ()
        except Undefined:
            continue
        if tuple(outputs) == targets:
            exact.append(program)
    return tuple(sorted(exact, key=lambda item: (int(item["description_length"]), _canonical(item))))


def _synthesize(
    demonstrations: Sequence[Pair],
    tests: Sequence[Grid],
    limits: Limits,
) -> tuple[tuple[dict[str, Any], ...], dict[str, Any]]:
    stats = SearchStats()
    exact: list[dict[str, Any]] = []
    for background in ("mode", "border_mode", "corners"):
        exact.extend(_enumerate_programs_for_background(demonstrations, tests, background, limits, stats))
        if stats.exhausted:
            return (), {"exhausted": True}
    if not exact:
        return (), {
            "exhausted": False,
            "atoms_considered": stats.atoms_considered,
            "selectors_considered": stats.selectors_considered,
            "rules_considered": stats.rules_considered,
            "programs_considered": stats.programs_considered,
            "executor_calls": stats.executor_calls,
        }
    best = min(int(program["description_length"]) for program in exact)
    near = [program for program in exact if int(program["description_length"]) <= best + limits.mdl_slack]
    return tuple(near), {
        "exhausted": False,
        "atoms_considered": stats.atoms_considered,
        "selectors_considered": stats.selectors_considered,
        "rules_considered": stats.rules_considered,
        "programs_considered": stats.programs_considered,
        "executor_calls": stats.executor_calls,
        "exact_programs": len(exact),
        "near_mdl_programs": len(near),
        "best_description_length": best,
    }


def _behavior(program: Mapping[str, Any], grids: Sequence[Grid], limits: Limits) -> tuple[Grid, ...]:
    return tuple(_execute_internal(program, grid, limits)[0] for grid in grids)


def _loo_guard(demonstrations: Sequence[Pair], limits: Limits) -> tuple[bool, int, int]:
    checks = 0
    classes = 0
    for held_out in range(len(demonstrations)):
        training = tuple(pair for index, pair in enumerate(demonstrations) if index != held_out)
        if not training:
            return False, checks, classes
        source, expected = demonstrations[held_out]
        # One remaining example is permitted only inside the LOO compiler; the
        # public compiler still requires at least two demonstrations.
        local_limits = Limits(**{
            name: (1 if name == "min_rule_demo_witnesses" else getattr(limits, name))
            for name in limits.__dataclass_fields__
        })
        programs, evidence = _synthesize(training, (source,), local_limits)
        if evidence.get("exhausted") or not programs:
            return False, checks, classes
        behaviors: dict[str, tuple[Grid, ...]] = {}
        for program in programs:
            try:
                output = _behavior(program, (source,), local_limits)
            except Undefined:
                continue
            behaviors[_digest([_plain(grid) for grid in output])] = output
            checks += 1
        classes += len(behaviors)
        if len(behaviors) != 1 or next(iter(behaviors.values())) != (expected,):
            return False, checks, classes
    return True, checks, classes


def _rotate90(grid: Grid) -> Grid:
    return tuple(tuple(row) for row in zip(*reversed(grid)))


def _d4_variants(grid: Grid) -> tuple[Grid, ...]:
    values: dict[str, Grid] = {}
    current = grid
    for _ in range(4):
        values.setdefault(_canonical(_plain(current)), current)
        reflected = tuple(tuple(reversed(row)) for row in current)
        values.setdefault(_canonical(_plain(reflected)), reflected)
        current = _rotate90(current)
    return tuple(values[key] for key in sorted(values))


def _swap_grid(grid: Grid, left: int, right: int) -> Grid:
    return tuple(
        tuple(right if value == left else left if value == right else value for value in row)
        for row in grid
    )


def _swap_program(program: Mapping[str, Any], left: int, right: int) -> dict[str, Any]:
    result = json.loads(_canonical(program))
    for rule in result["rules"]:
        action = rule["action"]
        if action.get("kind") == "literal":
            value = action["color"]
            action["color"] = right if value == left else left if value == right else value
    return result


def _gauge_guard(program: Mapping[str, Any], demonstrations: Sequence[Pair], limits: Limits) -> tuple[bool, int, int]:
    d4_checks = 0
    palette_checks = 0
    for source, target in demonstrations:
        source_variants = _d4_variants(source)
        target_variants = _d4_variants(target)
        # Canonical-key matching avoids relying on enumeration order when a
        # raster itself has symmetry.
        paired: dict[str, tuple[Grid, Grid]] = {}
        source_current, target_current = source, target
        for _ in range(4):
            paired.setdefault(_canonical(_plain(source_current)), (source_current, target_current))
            reflected_source = tuple(tuple(reversed(row)) for row in source_current)
            reflected_target = tuple(tuple(reversed(row)) for row in target_current)
            paired.setdefault(_canonical(_plain(reflected_source)), (reflected_source, reflected_target))
            source_current, target_current = _rotate90(source_current), _rotate90(target_current)
        for transformed_source, transformed_target in paired.values():
            d4_checks += 1
            if d4_checks + palette_checks > limits.max_gauge_checks:
                return False, d4_checks, palette_checks
            try:
                output = _execute_internal(program, transformed_source, limits)[0]
            except Undefined:
                return False, d4_checks, palette_checks
            if output != transformed_target:
                return False, d4_checks, palette_checks
        colors = sorted({value for row in source for value in row} | {value for row in target for value in row})
        absent = next((color for color in range(10) if color not in colors), None)
        swaps = list(itertools.combinations(colors, 2))
        if absent is not None:
            swaps.extend((color, absent) for color in colors)
        for left, right in swaps:
            palette_checks += 1
            if d4_checks + palette_checks > limits.max_gauge_checks:
                return False, d4_checks, palette_checks
            transformed_program = _swap_program(program, left, right)
            try:
                output = _execute_internal(transformed_program, _swap_grid(source, left, right), limits)[0]
            except Undefined:
                return False, d4_checks, palette_checks
            if output != _swap_grid(target, left, right):
                return False, d4_checks, palette_checks
    return True, d4_checks, palette_checks


def compile_task(task: Any, limits: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    """Compile at most one behaviorally unique relational delta program."""

    try:
        bounds = Limits.from_value(limits)
        demonstrations, tests = _sanitize(task, bounds)
        programs, search = _synthesize(demonstrations, tests, bounds)
    except (Undefined, TypeError, ValueError, KeyError):
        return []
    if search.get("exhausted") or not programs:
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
    representative, test_outputs = equivalent[0]
    try:
        train_outputs = _behavior(representative, tuple(source for source, _ in demonstrations), bounds)
    except Undefined:
        return []
    if train_outputs != tuple(target for _, target in demonstrations):
        return []
    loo_ok, loo_checks, loo_classes = _loo_guard(demonstrations, bounds)
    if not loo_ok:
        return []
    gauge_ok, d4_checks, palette_checks = _gauge_guard(representative, demonstrations, bounds)
    if not gauge_ok:
        return []
    candidate = {
        "family": "delta_algebra",
        "program": json.loads(_canonical(representative)),
        "train_outputs": [_plain(grid) for grid in train_outputs],
        "test_outputs": [_plain(grid) for grid in test_outputs],
        "complexity": int(representative["description_length"]),
        "evidence": {
            "all_demos_exact": True,
            "exact_replay": True,
            "leave_one_demo_out_reinduction": True,
            "leave_one_out_program_checks": loo_checks,
            "leave_one_out_behavior_classes": loo_classes,
            "enumeration_complete": True,
            "hard_caps_exhausted": False,
            "atoms_considered": search.get("atoms_considered", 0),
            "selectors_considered": search.get("selectors_considered", 0),
            "rules_considered": search.get("rules_considered", 0),
            "programs_considered": search.get("programs_considered", 0),
            "executor_calls": search.get("executor_calls", 0),
            "near_mdl_programs": len(programs),
            "full_test_behavior_classes": len(behaviors),
            "full_test_behavior_hash": behavior_hash,
            "equivalent_programs": len(equivalent),
            "d4_covariance_checks": d4_checks,
            "palette_covariance_checks": palette_checks,
            "task_local_selector_atoms": sum(len(rule["selector"]["all"]) for rule in representative["rules"]),
            "serialized_resolved_coordinates": False,
            "task_identity_observed": False,
            "test_labels_observed": False,
            "solution_store_observed": False,
        },
    }
    candidate["evidence"]["candidate_semantic_hash"] = _digest(candidate)
    return [candidate][: bounds.max_candidates]


def _safe_task(task: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(task, Mapping):
        raise Undefined("task is invalid")
    train, test = task.get("train"), task.get("test")
    if not isinstance(train, list) or not isinstance(test, list):
        raise Undefined("task splits are invalid")
    return {
        "train": [{"input": example["input"], "output": example["output"]} for example in train],
        "test": [{"input": example["input"]} for example in test],
    }


def freeze_scan(
    challenges: Mapping[str, Mapping[str, Any]],
    *,
    limits: Mapping[str, Any] | None = None,
    source_hash: str | None = None,
    entrant_source_hash: str | None = None,
    run_name: str = "delta-algebra-scan",
) -> dict[str, Any]:
    """Freeze a deterministic challenge-only scan before any score access."""

    records: dict[str, Any] = {}
    activated = 0
    for raw_task_id, task in sorted(challenges.items(), key=lambda item: str(item[0])):
        task_id = str(raw_task_id)
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
        records[task_id] = record
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
            "Challenge-only deterministic scan. Compilation received demonstrations and "
            "test inputs; no solution, score, baseline, or result artifact was opened."
        ),
    }
    body["semantic_hash"] = _digest(body)
    body["content_hash"] = _digest(body)
    return body


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".partial")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    temporary.replace(path)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--challenges", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--run-name", default="delta-algebra-scan")
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
    print(
        _canonical(
            {
                "activation_count": frozen["activation_count"],
                "content_hash": frozen["content_hash"],
                "source_task_count": frozen["source_task_count"],
            }
        )
    )
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
