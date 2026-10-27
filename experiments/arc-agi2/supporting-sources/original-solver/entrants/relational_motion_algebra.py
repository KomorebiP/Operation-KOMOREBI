"""Replayable relational motion algebra for PR-LASM Block 14.

The entrant induces a finite language of component translations, local D4
transforms, swaps, alignments, and marker/frame-directed transport.  It also
contains a few geometric normal forms whose semantics are still relational:
particle pyramids, comb slots, staggered touching pairs, matched stencils, and
inward hinge rotations.  Every role is derived from the current grid.  Task
identities, corpus fingerprints, test labels, scores, and solution stores are
not inputs to compilation or replay.

Programs must exactly replay every demonstration, survive leave-one-out
reinduction and D4/palette gauges, and belong to one minimum-description test
behavior class.  Ambiguity, undefined roles, or exhausted bounds abstain.

Author: Komorebi P.
"""
from __future__ import annotations

import argparse
from collections import Counter, deque
from dataclasses import dataclass
import hashlib
import itertools
import json
import math
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


Grid = tuple[tuple[int, ...], ...]
Cell = tuple[int, int]
SCHEMA = "komorebi.pr_lasm.block14.relational_motion_algebra.program.v1"
SCAN_SCHEMA = "komorebi.pr_lasm.block14.relational_motion_algebra.scan.v1"
AUTHOR = "Komorebi P."
FOUR: tuple[Cell, ...] = ((-1, 0), (0, -1), (0, 1), (1, 0))
EIGHT: tuple[Cell, ...] = tuple(
    (dr, dc)
    for dr in (-1, 0, 1)
    for dc in (-1, 0, 1)
    if (dr, dc) != (0, 0)
)
D4 = ("id", "r90", "r180", "r270", "fh", "fv", "diag", "anti")

DEFAULTS = {
    "max_candidates": 1,
    "max_programs": 2_048,
    "max_evaluations": 24_000,
    "max_grid_cells": 900,
    "max_components": 160,
    "max_gauge_checks": 512,
    "mdl_slack": 0,
    "loo_slack": 0,
    "min_demos": 2,
}
HARD_CAPS = {
    "max_candidates": 8,
    "max_programs": 8_192,
    "max_evaluations": 100_000,
    "max_grid_cells": 3_600,
    "max_components": 320,
    "max_gauge_checks": 2_048,
    "mdl_slack": 2,
    "loo_slack": 1,
    "min_demos": 10,
}


class Undefined(ValueError):
    """A relational role or motion is absent, tied, or invalid."""


def _canonical(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _plain(grid: Grid) -> list[list[int]]:
    return [list(row) for row in grid]


def _grid(value: Any, max_cells: int) -> Grid:
    if not isinstance(value, (list, tuple)) or not value:
        raise Undefined("grid must be a nonempty sequence")
    rows: list[tuple[int, ...]] = []
    width: int | None = None
    for raw in value:
        if not isinstance(raw, (list, tuple)) or not raw:
            raise Undefined("grid row must be a nonempty sequence")
        row: list[int] = []
        for cell in raw:
            if isinstance(cell, bool) or not isinstance(cell, int) or not 0 <= cell <= 9:
                raise Undefined("ARC colors must be integers in [0, 9]")
            row.append(int(cell))
        if width is None:
            width = len(row)
        elif len(row) != width:
            raise Undefined("grid must be rectangular")
        rows.append(tuple(row))
    if len(rows) * int(width or 0) > max_cells:
        raise Undefined("grid exceeds the declared cell budget")
    return tuple(rows)


def _read_limits(value: Any) -> dict[str, int]:
    result = dict(DEFAULTS)
    if value is None:
        return result
    if not isinstance(value, Mapping):
        raise Undefined("limits must be a mapping")
    aliases = {"candidate_cap": "max_candidates"}
    for raw_name, raw_value in value.items():
        name = aliases.get(str(raw_name), str(raw_name))
        if name not in DEFAULTS:
            continue
        if isinstance(raw_value, bool) or not isinstance(raw_value, int):
            raise Undefined("limit must be an integer")
        minimum = 0 if name in {"mdl_slack", "loo_slack"} else 1
        if raw_value < minimum:
            raise Undefined("limit is below its minimum")
        result[name] = min(raw_value, HARD_CAPS[name])
    return result


def _sanitize(
    task: Any, limits: Mapping[str, int]
) -> tuple[tuple[tuple[Grid, Grid], ...], tuple[Grid, ...]]:
    if not isinstance(task, Mapping):
        raise Undefined("task must be a mapping")
    train, test = task.get("train"), task.get("test")
    if (
        not isinstance(train, Sequence)
        or isinstance(train, (str, bytes))
        or not train
        or not isinstance(test, Sequence)
        or isinstance(test, (str, bytes))
        or not test
    ):
        raise Undefined("task needs nonempty train and test splits")
    demonstrations: list[tuple[Grid, Grid]] = []
    tests: list[Grid] = []
    for example in train:
        if not isinstance(example, Mapping):
            raise Undefined("demonstration is invalid")
        demonstrations.append(
            (
                _grid(example.get("input"), limits["max_grid_cells"]),
                _grid(example.get("output"), limits["max_grid_cells"]),
            )
        )
    for example in test:
        if not isinstance(example, Mapping):
            raise Undefined("test example is invalid")
        tests.append(_grid(example.get("input"), limits["max_grid_cells"]))
    return tuple(demonstrations), tuple(tests)


def _shape(grid: Grid) -> tuple[int, int]:
    return len(grid), len(grid[0])


def _background(grid: Grid) -> int:
    counts = Counter(cell for row in grid for cell in row)
    maximum = max(counts.values())
    winners = sorted(color for color, count in counts.items() if count == maximum)
    if len(winners) == 1:
        return winners[0]
    # Tiny ARC canvases can tie a solid support with the empty field.  The
    # upper-left cell is a palette-covariant, geometry-local tiebreaker.
    if grid[0][0] in winners:
        return grid[0][0]
    raise Undefined("background mode is tied")


def _d4(grid: Grid, name: str) -> Grid:
    if name == "id":
        return grid
    if name == "r90":
        return tuple(tuple(row) for row in zip(*grid[::-1]))
    if name == "r180":
        return tuple(tuple(reversed(row)) for row in reversed(grid))
    if name == "r270":
        return tuple(tuple(row) for row in zip(*grid))[::-1]
    if name == "fh":
        return tuple(tuple(reversed(row)) for row in grid)
    if name == "fv":
        return tuple(reversed(grid))
    if name == "diag":
        return tuple(tuple(row) for row in zip(*grid))
    if name == "anti":
        transposed = tuple(tuple(row) for row in zip(*grid))
        return tuple(tuple(reversed(row)) for row in reversed(transposed))
    raise Undefined("unknown D4 transform")


_D4_PROBE: Grid = ((0, 1, 2), (3, 4, 5))
_D4_SIGNATURE = {_d4(_D4_PROBE, name): name for name in D4}


def _compose(left: str, right: str) -> str:
    """Return the transform obtained by applying ``right`` then ``left``."""

    return _D4_SIGNATURE[_d4(_d4(_D4_PROBE, right), left)]


def _inverse(name: str) -> str:
    for candidate in D4:
        if _compose(candidate, name) == "id" and _compose(name, candidate) == "id":
            return candidate
    raise AssertionError("D4 inverse is absent")


def _normalize(cells: Iterable[Cell]) -> tuple[Cell, ...]:
    points = tuple(cells)
    if not points:
        raise Undefined("empty shape")
    top = min(row for row, _ in points)
    left = min(column for _, column in points)
    return tuple(sorted((row - top, column - left) for row, column in points))


def _shape_d4(cells: Iterable[Cell]) -> tuple[Cell, ...]:
    points = _normalize(cells)
    height = max(row for row, _ in points) + 1
    width = max(column for _, column in points) + 1
    canvas = tuple(
        tuple(1 if (row, column) in points else 0 for column in range(width))
        for row in range(height)
    )
    variants = []
    for name in D4:
        transformed = _d4(canvas, name)
        variants.append(
            _normalize(
                (row, column)
                for row, values in enumerate(transformed)
                for column, value in enumerate(values)
                if value
            )
        )
    return min(variants)


@dataclass(frozen=True, slots=True)
class Component:
    cells: tuple[tuple[int, int, int], ...]
    grid_height: int
    grid_width: int

    @property
    def positions(self) -> frozenset[Cell]:
        return frozenset((row, column) for row, column, _ in self.cells)

    @property
    def area(self) -> int:
        return len(self.cells)

    @property
    def colors(self) -> tuple[int, ...]:
        return tuple(sorted({color for _, _, color in self.cells}))

    @property
    def top(self) -> int:
        return min(row for row, _, _ in self.cells)

    @property
    def bottom(self) -> int:
        return max(row for row, _, _ in self.cells)

    @property
    def left(self) -> int:
        return min(column for _, column, _ in self.cells)

    @property
    def right(self) -> int:
        return max(column for _, column, _ in self.cells)

    @property
    def height(self) -> int:
        return self.bottom - self.top + 1

    @property
    def width(self) -> int:
        return self.right - self.left + 1

    @property
    def bbox_area(self) -> int:
        return self.height * self.width

    @property
    def center2(self) -> tuple[int, int]:
        return self.top + self.bottom, self.left + self.right

    @property
    def shape(self) -> tuple[Cell, ...]:
        return _normalize(self.positions)

    @property
    def d4_shape(self) -> tuple[Cell, ...]:
        return _shape_d4(self.positions)

    @property
    def touches_border(self) -> bool:
        return (
            self.top == 0
            or self.left == 0
            or self.bottom == self.grid_height - 1
            or self.right == self.grid_width - 1
        )


SceneCache = dict[tuple[Grid, int, bool, int], tuple[Component, ...]]


def _components(
    grid: Grid,
    connectivity: int,
    monochrome: bool,
    maximum: int,
    cache: SceneCache | None = None,
) -> tuple[Component, ...]:
    key = grid, connectivity, monochrome, maximum
    if cache is not None and key in cache:
        return cache[key]
    background = _background(grid)
    steps = FOUR if connectivity == 4 else EIGHT if connectivity == 8 else None
    if steps is None:
        raise Undefined("connectivity must be four or eight")
    height, width = _shape(grid)
    remaining = {
        (row, column)
        for row, values in enumerate(grid)
        for column, value in enumerate(values)
        if value != background
    }
    result: list[Component] = []
    while remaining:
        seed = min(remaining)
        remaining.remove(seed)
        queue = deque([seed])
        positions = {seed}
        seed_color = grid[seed[0]][seed[1]]
        while queue:
            row, column = queue.popleft()
            for dr, dc in steps:
                neighbor = row + dr, column + dc
                if neighbor not in remaining:
                    continue
                if monochrome and grid[neighbor[0]][neighbor[1]] != seed_color:
                    continue
                remaining.remove(neighbor)
                positions.add(neighbor)
                queue.append(neighbor)
        cells = tuple(sorted((row, column, grid[row][column]) for row, column in positions))
        result.append(Component(cells, height, width))
        if len(result) > maximum:
            raise Undefined("component budget exceeded")
    if not result:
        raise Undefined("scene has no foreground")
    answer = tuple(sorted(result, key=lambda item: (item.top, item.left, item.bottom, item.right, item.colors)))
    if cache is not None:
        cache[key] = answer
    return answer


def _foreground_counts(grid: Grid) -> Counter[int]:
    background = _background(grid)
    return Counter(cell for row in grid for cell in row if cell != background)


def _unique_extreme(values: Mapping[Any, int], *, maximum: bool) -> Any:
    if not values:
        raise Undefined("role population is empty")
    wanted = max(values.values()) if maximum else min(values.values())
    winners = [key for key, value in values.items() if value == wanted]
    if len(winners) != 1:
        raise Undefined("role extreme is tied")
    return winners[0]


def _select(
    grid: Grid,
    components: Sequence[Component],
    role: str,
) -> tuple[int, ...]:
    if not components:
        raise Undefined("selector population is empty")
    if role == "all":
        selected = tuple(range(len(components)))
    elif role in {"unique_min_area", "unique_max_area"}:
        areas = {index: component.area for index, component in enumerate(components)}
        selected = (_unique_extreme(areas, maximum=role.endswith("max_area")),)
    elif role in {"rare_color", "common_color"}:
        counts = _foreground_counts(grid)
        color = _unique_extreme(counts, maximum=role == "common_color")
        selected = tuple(
            index for index, component in enumerate(components) if component.colors == (color,)
        )
    elif role == "singletons":
        selected = tuple(index for index, component in enumerate(components) if component.area == 1)
    elif role == "non_singletons":
        selected = tuple(index for index, component in enumerate(components) if component.area > 1)
    elif role in {"unique_shape", "repeated_shapes"}:
        shapes = [component.d4_shape for component in components]
        counts = Counter(shapes)
        if role == "unique_shape":
            selected = tuple(index for index, shape in enumerate(shapes) if counts[shape] == 1)
            if len(selected) != 1:
                raise Undefined("unique shape role is tied")
        else:
            selected = tuple(index for index, shape in enumerate(shapes) if counts[shape] > 1)
    elif role == "border":
        selected = tuple(index for index, component in enumerate(components) if component.touches_border)
    elif role == "interior":
        selected = tuple(index for index, component in enumerate(components) if not component.touches_border)
    elif role == "min_max_pair":
        areas = {index: component.area for index, component in enumerate(components)}
        low = _unique_extreme(areas, maximum=False)
        high = _unique_extreme(areas, maximum=True)
        selected = (low, high) if low != high else ()
    else:
        raise Undefined("unknown component selector")
    if not selected:
        raise Undefined("component selector is empty")
    return tuple(sorted(selected))


def _render_moves(
    grid: Grid,
    components: Sequence[Component],
    replacements: Mapping[int, Sequence[tuple[int, int, int]]],
) -> Grid:
    if not replacements:
        raise Undefined("motion has no movers")
    background = _background(grid)
    height, width = _shape(grid)
    selected = set(replacements)
    occupied = {
        (row, column)
        for index, component in enumerate(components)
        if index not in selected
        for row, column in component.positions
    }
    mutable = [list(row) for row in grid]
    for index in selected:
        for row, column, _ in components[index].cells:
            mutable[row][column] = background
    targets: set[Cell] = set()
    for cells in replacements.values():
        for row, column, color in cells:
            if not (0 <= row < height and 0 <= column < width):
                raise Undefined("motion leaves the canvas")
            if (row, column) in occupied or (row, column) in targets:
                raise Undefined("motion collides")
            targets.add((row, column))
            mutable[row][column] = color
    result = tuple(tuple(row) for row in mutable)
    if result == grid:
        raise Undefined("motion is an identity")
    return result


def _translate_cells(component: Component, dr: int, dc: int) -> tuple[tuple[int, int, int], ...]:
    return tuple((row + dr, column + dc, color) for row, column, color in component.cells)


def _core_translate_canvas(
    grid: Grid, program: Mapping[str, Any], limits: Mapping[str, int], cache: SceneCache
) -> tuple[Grid, dict[str, Any]]:
    components = _components(
        grid, int(program["connectivity"]), True, limits["max_components"], cache
    )
    selected = _select(grid, components, str(program["selector"]))
    top = min(components[index].top for index in selected)
    bottom = max(components[index].bottom for index in selected)
    left = min(components[index].left for index in selected)
    right = max(components[index].right for index in selected)
    height, width = _shape(grid)
    dr = height - 1 - bottom
    alignment = str(program["alignment"])
    if alignment == "preserve":
        dc = 0
    elif alignment == "left":
        dc = -left
    elif alignment == "right":
        dc = width - 1 - right
    elif alignment == "center":
        numerator = width - 1 - (left + right)
        if numerator % 2:
            raise Undefined("center alignment is half-integral")
        dc = numerator // 2
    else:
        raise Undefined("unknown canvas alignment")
    replacements = {
        index: _translate_cells(components[index], dr, dc) for index in selected
    }
    return _render_moves(grid, components, replacements), {
        "operation": "translate_canvas_bottom",
        "selected": list(selected),
        "delta": [dr, dc],
    }


def _core_slide(
    grid: Grid, program: Mapping[str, Any], limits: Mapping[str, int], cache: SceneCache
) -> tuple[Grid, dict[str, Any]]:
    components = _components(
        grid, int(program["connectivity"]), True, limits["max_components"], cache
    )
    selected = _select(grid, components, str(program["selector"]))
    height, _ = _shape(grid)
    if program["mode"] == "rigid":
        selected_positions = set().union(*(components[index].positions for index in selected))
        fixed = set().union(
            *(component.positions for index, component in enumerate(components) if index not in selected)
        ) if len(selected) < len(components) else set()
        distance = 0
        while all(
            row + distance + 1 < height and (row + distance + 1, column) not in fixed
            for row, column in selected_positions
        ):
            distance += 1
        replacements = {
            index: _translate_cells(components[index], distance, 0) for index in selected
        }
    elif program["mode"] == "individual":
        fixed = set().union(
            *(component.positions for index, component in enumerate(components) if index not in selected)
        ) if len(selected) < len(components) else set()
        replacements: dict[int, tuple[tuple[int, int, int], ...]] = {}
        for index in sorted(selected, key=lambda item: components[item].bottom, reverse=True):
            component = components[index]
            distance = 0
            while all(
                row + distance + 1 < height and (row + distance + 1, column) not in fixed
                for row, column in component.positions
            ):
                distance += 1
            moved = _translate_cells(component, distance, 0)
            replacements[index] = moved
            fixed.update((row, column) for row, column, _ in moved)
    else:
        raise Undefined("unknown slide mode")
    return _render_moves(grid, components, replacements), {
        "operation": "slide_down",
        "selected": list(selected),
        "mode": program["mode"],
    }


def _local_transform(component: Component, name: str, placement: str) -> tuple[tuple[int, int, int], ...]:
    height, width = component.height, component.width
    relative = [(row - component.top, column - component.left, color) for row, column, color in component.cells]
    if name == "fh":
        transformed = [(row, width - 1 - column, color) for row, column, color in relative]
        new_height, new_width = height, width
    elif name == "fv":
        transformed = [(height - 1 - row, column, color) for row, column, color in relative]
        new_height, new_width = height, width
    elif name == "r180":
        transformed = [(height - 1 - row, width - 1 - column, color) for row, column, color in relative]
        new_height, new_width = height, width
    elif name == "r90":
        transformed = [(column, height - 1 - row, color) for row, column, color in relative]
        new_height, new_width = width, height
    elif name == "r270":
        transformed = [(width - 1 - column, row, color) for row, column, color in relative]
        new_height, new_width = width, height
    else:
        raise Undefined("unknown local transform")
    if placement == "origin":
        top, left = component.top, component.left
    elif placement == "center":
        row_numerator = component.top + component.bottom - (new_height - 1)
        col_numerator = component.left + component.right - (new_width - 1)
        if row_numerator % 2 or col_numerator % 2:
            raise Undefined("local transform center is half-integral")
        top, left = row_numerator // 2, col_numerator // 2
    else:
        raise Undefined("unknown local placement")
    return tuple((top + row, left + column, color) for row, column, color in transformed)


def _core_component_d4(
    grid: Grid, program: Mapping[str, Any], limits: Mapping[str, int], cache: SceneCache
) -> tuple[Grid, dict[str, Any]]:
    components = _components(
        grid, int(program["connectivity"]), True, limits["max_components"], cache
    )
    selected = _select(grid, components, str(program["selector"]))
    replacements = {
        index: _local_transform(components[index], str(program["transform"]), str(program["placement"]))
        for index in selected
    }
    return _render_moves(grid, components, replacements), {
        "operation": "component_d4",
        "selected": list(selected),
        "transform": program["transform"],
    }


def _core_swap(
    grid: Grid, program: Mapping[str, Any], limits: Mapping[str, int], cache: SceneCache
) -> tuple[Grid, dict[str, Any]]:
    components = _components(
        grid, int(program["connectivity"]), True, limits["max_components"], cache
    )
    selected = _select(grid, components, str(program["selector"]))
    if len(selected) != 2:
        raise Undefined("swap selector must resolve to two components")
    first, second = (components[index] for index in selected)
    if (first.height, first.width) != (second.height, second.width):
        raise Undefined("swap needs equal component boxes")
    replacements = {
        selected[0]: _translate_cells(first, second.top - first.top, second.left - first.left),
        selected[1]: _translate_cells(second, first.top - second.top, first.left - second.left),
    }
    return _render_moves(grid, components, replacements), {
        "operation": "swap_components",
        "selected": list(selected),
    }


def _core_align_below(
    grid: Grid, program: Mapping[str, Any], limits: Mapping[str, int], cache: SceneCache
) -> tuple[Grid, dict[str, Any]]:
    components = _components(
        grid, int(program["connectivity"]), True, limits["max_components"], cache
    )
    movers = _select(grid, components, str(program["mover"]))
    anchors = _select(grid, components, str(program["anchor"]))
    if len(movers) != 1 or len(anchors) != 1 or movers[0] == anchors[0]:
        raise Undefined("alignment roles must resolve to distinct singletons")
    mover, anchor = components[movers[0]], components[anchors[0]]
    top = anchor.bottom + 1
    alignment = str(program["alignment"])
    if alignment == "left":
        left = anchor.left
    elif alignment == "right":
        left = anchor.right - mover.width + 1
    elif alignment == "center":
        numerator = anchor.left + anchor.right - (mover.width - 1)
        if numerator % 2:
            raise Undefined("anchor center is half-integral")
        left = numerator // 2
    else:
        raise Undefined("unknown anchor alignment")
    replacement = _translate_cells(mover, top - mover.top, left - mover.left)
    return _render_moves(grid, components, {movers[0]: replacement}), {
        "operation": "align_below_anchor",
        "mover": movers[0],
        "anchor": anchors[0],
        "alignment": alignment,
    }


def _core_pack_pyramid(grid: Grid) -> tuple[Grid, dict[str, Any]]:
    background = _background(grid)
    points = [(row, column, value) for row, values in enumerate(grid) for column, value in enumerate(values) if value != background]
    height, width = _shape(grid)
    if not points:
        raise Undefined("pyramid source is empty")
    columns = sorted({column for _, column, _ in points})
    mutable = [[background] * width for _ in range(height)]
    occupied_targets: set[Cell] = set()
    layer_total = 0
    for center in columns:
        group = [(row, value) for row, column, value in points if column == center]
        side = math.isqrt(len(group))
        if side * side != len(group) or side > height:
            raise Undefined("odd-layer pyramid requires a square particle count per axis")
        if center - side + 1 < 0 or center + side - 1 >= width:
            raise Undefined("pyramid leaves the canvas")
        colors = sorted({value for _, value in group})
        first_rows = {color: min(row for row, value in group if value == color) for color in colors}
        if len(set(first_rows.values())) != len(colors):
            raise Undefined("pyramid layer colors are ambiguous")
        order = sorted(colors, key=lambda color: first_rows[color])
        counts = Counter(value for _, value in group)
        layers: list[int] = []
        next_layer = 0
        for color in order:
            accumulated = 0
            while next_layer < side and accumulated < counts[color]:
                accumulated += 2 * next_layer + 1
                layers.append(color)
                next_layer += 1
            if accumulated != counts[color]:
                raise Undefined("particle color count splits an odd layer")
        if next_layer != side:
            raise Undefined("pyramid layers are incomplete")
        for index, color in enumerate(layers):
            row = height - side + index
            start = center - index
            for column in range(start, center + index + 1):
                if (row, column) in occupied_targets:
                    raise Undefined("particle pyramids overlap")
                occupied_targets.add((row, column))
                mutable[row][column] = color
        layer_total += side
    result = tuple(tuple(row) for row in mutable)
    if result == grid:
        raise Undefined("pyramid packing is an identity")
    return result, {
        "operation": "pack_particle_pyramid",
        "pyramids": len(columns),
        "layers": layer_total,
    }


def _core_complete_pyramid(
    grid: Grid, limits: Mapping[str, int], cache: SceneCache
) -> tuple[Grid, dict[str, Any]]:
    background = _background(grid)
    colors = sorted(set(cell for row in grid for cell in row) - {background})
    if len(colors) != 2:
        raise Undefined("pyramid completion requires two foreground colors")
    mono = _components(grid, 8, True, limits["max_components"], cache)
    candidates: list[tuple[int, int, frozenset[Cell]]] = []
    for marker_color in colors:
        marker_components = [component for component in mono if component.colors == (marker_color,)]
        marker_cells = {
            (row, column)
            for component in marker_components
            for row, column in component.positions
        }
        if not marker_components:
            continue
        structure_color = next(color for color in colors if color != marker_color)
        for index, component in enumerate(mono):
            if component.colors != (structure_color,) or component.area < 3:
                continue
            desired_cells: set[Cell] = set()
            for row in range(component.top, component.bottom + 1):
                columns = [column for candidate_row, column in component.positions if candidate_row == row]
                if not columns:
                    continue
                desired_cells.update((row, column) for column in range(min(columns), max(columns) + 1))
            desired = frozenset(desired_cells)
            missing = desired - component.positions
            if missing and len(missing) == len(marker_cells):
                candidates.append((marker_color, index, missing))
    if len(candidates) != 1:
        raise Undefined("span-completion role is absent or tied")
    marker_color, component_index, missing = candidates[0]
    mutable = [list(row) for row in grid]
    for row, values in enumerate(grid):
        for column, value in enumerate(values):
            if value == marker_color:
                mutable[row][column] = background
    for row, column in missing:
        mutable[row][column] = marker_color
    result = tuple(tuple(row) for row in mutable)
    if result == grid:
        raise Undefined("pyramid completion is an identity")
    return result, {
        "operation": "complete_sparse_spans",
        "structure_component": component_index,
        "moved_marker_cells": len(missing),
    }


def _core_stagger_pairs(
    grid: Grid, limits: Mapping[str, int], cache: SceneCache
) -> tuple[Grid, dict[str, Any]]:
    components = _components(grid, 4, True, limits["max_components"], cache)
    groups: dict[tuple[int, int], list[int]] = {}
    for index, component in enumerate(components):
        groups.setdefault((component.left, component.right), []).append(index)
    pairs: list[tuple[int, int]] = []
    for indices in groups.values():
        if len(indices) != 2:
            raise Undefined("stagger groups must be vertical pairs")
        upper, lower = sorted(indices, key=lambda index: (components[index].top, components[index].bottom))
        if components[upper].bottom + 1 != components[lower].top:
            raise Undefined("stagger pair is not edge-adjacent")
        pairs.append((upper, lower))
    if not pairs:
        raise Undefined("stagger relation has no pairs")
    replacements: dict[int, tuple[tuple[int, int, int], ...]] = {}
    for upper, lower in pairs:
        replacements[upper] = _translate_cells(components[upper], 0, -1)
        replacements[lower] = _translate_cells(components[lower], 0, 1)
    return _render_moves(grid, components, replacements), {
        "operation": "stagger_touching_pairs",
        "pair_count": len(pairs),
    }


def _is_downward_frame(component: Component) -> bool:
    if component.top != 0 or component.width < 3 or component.height < 2:
        return False
    relative = component.shape
    expected = {
        (0, column) for column in range(component.width)
    } | {
        (row, column)
        for row in range(1, component.height)
        for column in (0, component.width - 1)
    }
    return set(relative) == expected


def _core_frame_project(
    grid: Grid, limits: Mapping[str, int], cache: SceneCache
) -> tuple[Grid, dict[str, Any]]:
    components = _components(grid, 4, True, limits["max_components"], cache)
    candidates: list[tuple[int, int]] = []
    for frame_index, frame in enumerate(components):
        if len(frame.colors) != 1 or not _is_downward_frame(frame):
            continue
        peers = [
            index
            for index, component in enumerate(components)
            if index != frame_index
            and component.colors == frame.colors
            and component.d4_shape == frame.d4_shape
        ]
        movers = [index for index, component in enumerate(components) if component.colors != frame.colors]
        if peers and len(movers) == 1 and components[movers[0]].width == frame.width - 2:
            candidates.append((frame_index, movers[0]))
    if len(candidates) != 1:
        raise Undefined("frame projection roles are absent or tied")
    frame_index, mover_index = candidates[0]
    frame, mover = components[frame_index], components[mover_index]
    top = len(grid) - mover.height
    left = frame.left + 1
    replacement = _translate_cells(mover, top - mover.top, left - mover.left)
    return _render_moves(grid, components, {mover_index: replacement}), {
        "operation": "project_payload_from_frame",
        "frame": frame_index,
        "mover": mover_index,
    }


def _perfect_assignments(options: Sequence[Sequence[int]]) -> list[tuple[int, ...]]:
    if len(options) > 8:
        raise Undefined("assignment exceeds finite bound")
    assignments = []
    for permutation in itertools.permutations(range(len(options))):
        if all(permutation[index] in options[index] for index in range(len(options))):
            assignments.append(permutation)
            if len(assignments) > 1:
                break
    return assignments


def _core_comb_pack(
    grid: Grid, limits: Mapping[str, int], cache: SceneCache
) -> tuple[Grid, dict[str, Any]]:
    components = _components(grid, 4, True, limits["max_components"], cache)
    height, width = _shape(grid)
    bases = []
    for index, component in enumerate(components):
        if component.bottom != height - 1 or component.left != 0 or component.right != width - 1:
            continue
        if not all((height - 1, column) in component.positions for column in range(width)):
            continue
        bases.append(index)
    if len(bases) != 1:
        raise Undefined("comb base is absent or tied")
    base_index = bases[0]
    base = components[base_index]
    posts = sorted(column for row, column in base.positions if row == base.top)
    slots: list[tuple[int, int]] = []
    for left, right in zip(posts, posts[1:]):
        if right - left > 1:
            slots.append((left + 1, right - 1))
    movers = [index for index in range(len(components)) if index != base_index]
    if not slots or len(slots) != len(movers):
        raise Undefined("comb slots and movers do not correspond")
    options: list[list[int]] = []
    for slot_left, slot_right in slots:
        slot_width = slot_right - slot_left + 1
        possible = []
        dimensions = None
        for mover_position, component_index in enumerate(movers):
            component = components[component_index]
            if component.area != component.bbox_area or component.area % slot_width:
                continue
            target_height = component.area // slot_width
            if sorted((component.height, component.width)) != sorted((target_height, slot_width)):
                continue
            possible.append(mover_position)
            dimensions = (target_height, slot_width)
        if not possible or dimensions is None:
            raise Undefined("comb slot has no fitting rectangular mover")
        options.append(possible)
    assignments = _perfect_assignments(options)
    if len(assignments) != 1:
        raise Undefined("comb mover assignment is ambiguous")
    replacements: dict[int, tuple[tuple[int, int, int], ...]] = {}
    for slot_index, mover_position in enumerate(assignments[0]):
        component_index = movers[mover_position]
        component = components[component_index]
        slot_left, slot_right = slots[slot_index]
        slot_width = slot_right - slot_left + 1
        target_height = component.area // slot_width
        top = base.top - target_height + 1
        color = component.colors[0]
        replacements[component_index] = tuple(
            (row, column, color)
            for row in range(top, base.top + 1)
            for column in range(slot_left, slot_left + slot_width)
        )
    return _render_moves(grid, components, replacements), {
        "operation": "pack_rectangles_into_comb",
        "base": base_index,
        "slots": len(slots),
    }


def _core_stencil_match(
    grid: Grid, match: str, limits: Mapping[str, int], cache: SceneCache
) -> tuple[Grid, dict[str, Any]]:
    background = _background(grid)
    height, width = _shape(grid)
    occupied_rows = [
        any(value != background for value in grid[row]) for row in range(height)
    ]
    bands: list[tuple[int, int]] = []
    row = 0
    while row < height:
        if not occupied_rows[row]:
            row += 1
            continue
        top = row
        while row + 1 < height and occupied_rows[row + 1]:
            row += 1
        bands.append((top, row))
        row += 1
    if len(bands) < 2:
        raise Undefined("stencil matching needs separated bands")
    components = _components(grid, 4, True, limits["max_components"], cache)
    if any(not any(top <= component.top and component.bottom <= bottom for top, bottom in bands) for component in components):
        raise Undefined("a component crosses stencil separators")
    colors = sorted({component.colors[0] for component in components})
    candidates: list[tuple[int, int, tuple[int, ...], tuple[frozenset[Cell], ...]]] = []
    signature = (lambda cells: _normalize(cells)) if match == "exact" else (lambda cells: _shape_d4(cells))
    for anchor_color in colors:
        anchors = [component for component in components if component.colors == (anchor_color,)]
        if len(anchors) != len(bands):
            continue
        ordered_anchors: list[Component] = []
        valid = True
        for top, bottom in bands:
            matches = [component for component in anchors if top <= component.top and component.bottom <= bottom]
            if len(matches) != 1 or matches[0].top != top or matches[0].bottom != bottom:
                valid = False
                break
            ordered_anchors.append(matches[0])
        if not valid:
            continue
        payloads = [component for component in components if component.colors != (anchor_color,)]
        if len(payloads) != len(bands) or len({component.colors for component in payloads}) != len(payloads):
            continue
        for rectangle_width in range(max(component.width for component in ordered_anchors) + 1, width + 1):
            complements: list[frozenset[Cell]] = []
            options: list[list[int]] = []
            for anchor in ordered_anchors:
                rectangle = {
                    (row, column)
                    for row in range(anchor.top, anchor.bottom + 1)
                    for column in range(anchor.left, anchor.left + rectangle_width)
                    if column < width
                }
                if len(rectangle) != anchor.height * rectangle_width or not anchor.positions <= rectangle:
                    valid = False
                    break
                complement = frozenset(rectangle - anchor.positions)
                complements.append(complement)
                wanted = signature(complement)
                options.append(
                    [index for index, payload in enumerate(payloads) if signature(payload.positions) == wanted]
                )
            else:
                assignments = _perfect_assignments(options) if all(options) else []
                if len(assignments) == 1:
                    candidates.append((anchor_color, rectangle_width, assignments[0], tuple(complements)))
            valid = True
    if len(candidates) != 1:
        raise Undefined("stencil/payload correspondence is absent or tied")
    anchor_color, rectangle_width, assignment, complements = candidates[0]
    anchors = sorted(
        (component for component in components if component.colors == (anchor_color,)),
        key=lambda item: item.top,
    )
    payloads = [component for component in components if component.colors != (anchor_color,)]
    mutable = [list(row) for row in grid]
    for payload in payloads:
        for row, column in payload.positions:
            mutable[row][column] = background
    for band_index, payload_index in enumerate(assignment):
        color = payloads[payload_index].colors[0]
        for row, column in complements[band_index]:
            mutable[row][column] = color
    result = tuple(tuple(row) for row in mutable)
    if result == grid:
        raise Undefined("stencil matching is an identity")
    return result, {
        "operation": "match_payloads_to_stencils",
        "bands": len(anchors),
        "rectangle_width": rectangle_width,
        "shape_match": match,
    }


def _ray_run(grid: Grid, start: Cell, direction: Cell, color: int) -> tuple[Cell, ...]:
    height, width = _shape(grid)
    row, column = start[0] + direction[0], start[1] + direction[1]
    result = []
    while 0 <= row < height and 0 <= column < width and grid[row][column] == color:
        result.append((row, column))
        row += direction[0]
        column += direction[1]
    return tuple(result)


def _core_hinge_inward(grid: Grid) -> tuple[Grid, dict[str, Any]]:
    background = _background(grid)
    colors = sorted(set(cell for row in grid for cell in row) - {background})
    if len(colors) != 3:
        raise Undefined("hinge grammar requires three foreground colors")
    height, width = _shape(grid)
    interpretations = []
    directions = ((-1, 0), (0, 1), (1, 0), (0, -1))
    for arm_color, pivot_color, marker_color in itertools.permutations(colors):
        pivots = [(row, column) for row, values in enumerate(grid) for column, value in enumerate(values) if value == pivot_color]
        chains = []
        used_arm: set[Cell] = set()
        valid = bool(pivots)
        for pivot in pivots:
            possibilities = []
            for direction in directions:
                fixed = _ray_run(grid, pivot, direction, arm_color)
                free_direction = (-direction[0], -direction[1])
                free = _ray_run(grid, pivot, free_direction, arm_color)
                if not free:
                    continue
                after = (
                    pivot[0] + direction[0] * (len(fixed) + 1),
                    pivot[1] + direction[1] * (len(fixed) + 1),
                )
                if not (0 <= after[0] < height and 0 <= after[1] < width):
                    continue
                if grid[after[0]][after[1]] != marker_color:
                    continue
                possibilities.append((fixed, free, free_direction))
            if len(possibilities) != 1:
                valid = False
                break
            fixed, free, free_direction = possibilities[0]
            used_arm.update(fixed)
            used_arm.update(free)
            rotations = [
                (-free_direction[1], free_direction[0]),
                (free_direction[1], -free_direction[0]),
            ]
            scored = []
            for candidate_direction in rotations:
                targets = tuple(
                    (pivot[0] + candidate_direction[0] * step, pivot[1] + candidate_direction[1] * step)
                    for step in range(1, len(free) + 1)
                )
                if not all(0 <= row < height and 0 <= column < width for row, column in targets):
                    continue
                score = sum(
                    (2 * row - (height - 1)) ** 2 + (2 * column - (width - 1)) ** 2
                    for row, column in targets
                )
                scored.append((score, targets))
            if not scored:
                valid = False
                break
            best = min(score for score, _ in scored)
            winners = [targets for score, targets in scored if score == best]
            if len(winners) != 1:
                valid = False
                break
            chains.append((free, winners[0]))
        all_arm = {
            (row, column)
            for row, values in enumerate(grid)
            for column, value in enumerate(values)
            if value == arm_color
        }
        if valid and used_arm == all_arm:
            interpretations.append((arm_color, chains))
    if len(interpretations) != 1:
        raise Undefined("hinge color roles are absent or tied")
    arm_color, chains = interpretations[0]
    mutable = [list(row) for row in grid]
    free_origins = {cell for free, _ in chains for cell in free}
    targets = [cell for _, cells in chains for cell in cells]
    if len(set(targets)) != len(targets):
        raise Undefined("hinge rotations collide")
    for row, column in free_origins:
        mutable[row][column] = background
    for row, column in targets:
        if grid[row][column] != background and (row, column) not in free_origins:
            raise Undefined("hinge rotation meets an obstacle")
        mutable[row][column] = arm_color
    result = tuple(tuple(row) for row in mutable)
    if result == grid:
        raise Undefined("hinge rotation is an identity")
    return result, {"operation": "rotate_hinges_inward", "hinges": len(chains)}


def _execute_oriented(
    program: Mapping[str, Any], grid: Grid, limits: Mapping[str, int], cache: SceneCache
) -> tuple[Grid, dict[str, Any]]:
    core = str(program["core"])
    if core == "translate_canvas_bottom":
        return _core_translate_canvas(grid, program, limits, cache)
    if core == "slide_down":
        return _core_slide(grid, program, limits, cache)
    if core == "component_d4":
        return _core_component_d4(grid, program, limits, cache)
    if core == "swap_components":
        return _core_swap(grid, program, limits, cache)
    if core == "align_below_anchor":
        return _core_align_below(grid, program, limits, cache)
    if core == "pack_particle_pyramid":
        return _core_pack_pyramid(grid)
    if core == "complete_sparse_pyramid":
        return _core_complete_pyramid(grid, limits, cache)
    if core == "stagger_touching_pairs":
        return _core_stagger_pairs(grid, limits, cache)
    if core == "project_payload_from_frame":
        return _core_frame_project(grid, limits, cache)
    if core == "pack_rectangles_into_comb":
        return _core_comb_pack(grid, limits, cache)
    if core == "match_payloads_to_stencils":
        return _core_stencil_match(grid, str(program["shape_match"]), limits, cache)
    if core == "rotate_hinges_inward":
        return _core_hinge_inward(grid)
    raise Undefined("unknown motion core")


def _execute(
    program: Mapping[str, Any],
    grid: Grid,
    limits: Mapping[str, int],
    cache: SceneCache | None = None,
) -> tuple[Grid, dict[str, Any]]:
    if not isinstance(program, Mapping) or program.get("schema") != SCHEMA:
        raise Undefined("invalid motion-algebra program")
    view = str(program.get("view", "id"))
    oriented = _d4(grid, view)
    output, trace = _execute_oriented(program, oriented, limits, {} if cache is None else cache)
    restored = _d4(output, _inverse(view))
    if restored == grid:
        raise Undefined("motion is an identity")
    return restored, {**trace, "view": view}


def execute_program(program: Mapping[str, Any], value: Any) -> list[list[int]]:
    limits = dict(DEFAULTS)
    grid = _grid(value, limits["max_grid_cells"])
    return _plain(_execute(program, grid, limits)[0])


def replay_program(program: Mapping[str, Any], value: Any) -> dict[str, Any]:
    limits = dict(DEFAULTS)
    grid = _grid(value, limits["max_grid_cells"])
    output, motion = _execute(program, grid, limits)
    parse = {
        "kind": "motion_scene",
        "shape": list(_shape(grid)),
        "background": _background(grid),
        "foreground_histogram": dict(sorted(_foreground_counts(grid).items())),
        "program_view": program.get("view", "id"),
    }
    return {
        "output": _plain(output),
        "stages": [
            {"name": "parse_motion_scene", "input": _plain(grid), "output": parse},
            {"name": "resolve_dynamic_motion", "input": parse, "output": motion},
            {"name": "render_motion", "input": motion, "output": _plain(output)},
        ],
    }


def _program(core: str, *, view: str = "id", **fields: Any) -> dict[str, Any]:
    return {"schema": SCHEMA, "core": core, "view": view, **fields}


SELECTORS = (
    "all",
    "unique_min_area",
    "unique_max_area",
    "rare_color",
    "common_color",
    "singletons",
    "non_singletons",
    "unique_shape",
    "repeated_shapes",
    "border",
    "interior",
    "min_max_pair",
)


def _programs() -> tuple[dict[str, Any], ...]:
    result: list[dict[str, Any]] = []
    for view in D4:
        for core in (
            "pack_particle_pyramid",
            "complete_sparse_pyramid",
            "stagger_touching_pairs",
            "project_payload_from_frame",
            "pack_rectangles_into_comb",
        ):
            result.append(_program(core, view=view))
        for match in ("exact", "d4"):
            result.append(_program("match_payloads_to_stencils", view=view, shape_match=match))
    result.append(_program("rotate_hinges_inward"))
    for connectivity, selector in itertools.product((4, 8), SELECTORS):
        for view, alignment in itertools.product(D4, ("preserve", "left", "center", "right")):
            result.append(
                _program(
                    "translate_canvas_bottom",
                    view=view,
                    connectivity=connectivity,
                    selector=selector,
                    alignment=alignment,
                )
            )
        for view, mode in itertools.product(D4, ("rigid", "individual")):
            result.append(
                _program(
                    "slide_down",
                    view=view,
                    connectivity=connectivity,
                    selector=selector,
                    mode=mode,
                )
            )
        for transform, placement in itertools.product(
            ("fh", "fv", "r180", "r90", "r270"), ("origin", "center")
        ):
            result.append(
                _program(
                    "component_d4",
                    connectivity=connectivity,
                    selector=selector,
                    transform=transform,
                    placement=placement,
                )
            )
        result.append(
            _program("swap_components", connectivity=connectivity, selector=selector)
        )
    anchor_roles = ("unique_min_area", "unique_max_area", "rare_color", "common_color", "unique_shape")
    for connectivity, mover, anchor, alignment, view in itertools.product(
        (4, 8), anchor_roles, anchor_roles, ("left", "center", "right"), ("id", "r90", "r180", "r270")
    ):
        if mover != anchor:
            result.append(
                _program(
                    "align_below_anchor",
                    view=view,
                    connectivity=connectivity,
                    mover=mover,
                    anchor=anchor,
                    alignment=alignment,
                )
            )
    unique = {_canonical(item): item for item in result}
    return tuple(unique[key] for key in sorted(unique))


def _complexity(program: Mapping[str, Any]) -> int:
    core = str(program["core"])
    special = {
        "pack_particle_pyramid": 5,
        "stagger_touching_pairs": 6,
        "complete_sparse_pyramid": 7,
        "project_payload_from_frame": 7,
        "pack_rectangles_into_comb": 7,
        "match_payloads_to_stencils": 8,
        "rotate_hinges_inward": 8,
    }
    if core in special:
        return special[core] + int(program.get("view", "id") != "id") + int(program.get("shape_match") == "d4")
    selector_cost = 0 if program.get("selector") == "all" else 1
    if core == "component_d4":
        return 5 + selector_cost + int(program["placement"] == "center")
    if core in {"translate_canvas_bottom", "slide_down", "swap_components"}:
        return 6 + selector_cost + int(program.get("view", "id") != "id")
    if core == "align_below_anchor":
        return 8 + int(program.get("view", "id") != "id")
    raise Undefined("unknown program complexity")


@dataclass(frozen=True, slots=True)
class Evaluation:
    program: Mapping[str, Any]
    complexity: int
    train_outputs: tuple[Grid | None, ...]
    test_outputs: tuple[Grid | None, ...]


def _evaluate(
    program: Mapping[str, Any],
    demonstrations: Sequence[tuple[Grid, Grid]],
    tests: Sequence[Grid],
    limits: Mapping[str, int],
    cache: SceneCache,
) -> Evaluation:
    train_outputs: list[Grid | None] = []
    test_outputs: list[Grid | None] = []
    for source, _ in demonstrations:
        try:
            train_outputs.append(_execute(program, source, limits, cache)[0])
        except Undefined:
            train_outputs.append(None)
    for source in tests:
        try:
            test_outputs.append(_execute(program, source, limits, cache)[0])
        except Undefined:
            test_outputs.append(None)
    return Evaluation(program, _complexity(program), tuple(train_outputs), tuple(test_outputs))


def _loo_stable(
    evaluations: Sequence[Evaluation], targets: Sequence[Grid], slack: int
) -> tuple[bool, int]:
    if len(targets) < 2:
        return False, 0
    checked = 0
    for held_out in range(len(targets)):
        fits = [
            evaluation
            for evaluation in evaluations
            if all(
                index == held_out or evaluation.train_outputs[index] == target
                for index, target in enumerate(targets)
            )
        ]
        if not fits:
            return False, checked
        best = min(evaluation.complexity for evaluation in fits)
        near = [evaluation for evaluation in fits if evaluation.complexity <= best + slack]
        predictions = {evaluation.train_outputs[held_out] for evaluation in near}
        checked += len(near)
        if None in predictions or predictions != {targets[held_out]}:
            return False, checked
    return True, checked


def _palette_swap(grid: Grid, left: int, right: int) -> Grid:
    return tuple(
        tuple(right if cell == left else left if cell == right else cell for cell in row)
        for row in grid
    )


def _conjugate(program: Mapping[str, Any], external: str) -> dict[str, Any]:
    result = json.loads(_canonical(program))
    result["view"] = _compose(str(program.get("view", "id")), _inverse(external))
    return result


def _gauge_guard(
    program: Mapping[str, Any],
    demonstrations: Sequence[tuple[Grid, Grid]],
    limits: Mapping[str, int],
) -> tuple[bool, int, int]:
    required = len(demonstrations) * (len(D4) + 45)
    if required > limits["max_gauge_checks"]:
        return False, 0, 0
    d4_checks = 0
    palette_checks = 0
    for source, target in demonstrations:
        for transform in D4:
            transformed_source = _d4(source, transform)
            transformed_target = _d4(target, transform)
            try:
                prediction = _execute(_conjugate(program, transform), transformed_source, limits)[0]
            except Undefined:
                return False, d4_checks, palette_checks
            d4_checks += 1
            if prediction != transformed_target:
                return False, d4_checks, palette_checks
        for left, right in itertools.combinations(range(10), 2):
            transformed_source = _palette_swap(source, left, right)
            transformed_target = _palette_swap(target, left, right)
            try:
                prediction = _execute(program, transformed_source, limits)[0]
            except Undefined:
                return False, d4_checks, palette_checks
            palette_checks += 1
            if prediction != transformed_target:
                return False, d4_checks, palette_checks
    return True, d4_checks, palette_checks


def compile_task(task: Any, limits: Any = None) -> list[dict[str, Any]]:
    """Compile one exact, behaviorally unique relational-motion program."""

    try:
        normalized_limits = _read_limits(limits)
        demonstrations, tests = _sanitize(task, normalized_limits)
    except Undefined:
        return []
    if len(demonstrations) < normalized_limits["min_demos"]:
        return []
    for source, target in demonstrations:
        if _shape(source) != _shape(target) or source == target:
            return []
        if Counter(cell for row in source for cell in row) != Counter(
            cell for row in target for cell in row
        ):
            return []
    programs = _programs()
    if len(programs) > normalized_limits["max_programs"]:
        return []
    required_evaluations = len(programs) * (len(demonstrations) + len(tests))
    if required_evaluations > normalized_limits["max_evaluations"]:
        return []
    cache: SceneCache = {}
    evaluations = [
        _evaluate(program, demonstrations, tests, normalized_limits, cache)
        for program in programs
    ]
    targets = tuple(target for _, target in demonstrations)
    exact = [
        evaluation
        for evaluation in evaluations
        if evaluation.train_outputs == targets and None not in evaluation.test_outputs
    ]
    if not exact:
        return []
    stable, loo_checked = _loo_stable(
        evaluations, targets, normalized_limits["loo_slack"]
    )
    if not stable:
        return []
    best = min(evaluation.complexity for evaluation in exact)
    near = [
        evaluation
        for evaluation in exact
        if evaluation.complexity <= best + normalized_limits["mdl_slack"]
    ]
    behaviors: dict[str, list[Evaluation]] = {}
    for evaluation in near:
        behavior = [_plain(output) for output in evaluation.test_outputs if output is not None]
        behaviors.setdefault(_digest(behavior), []).append(evaluation)
    if len(behaviors) != 1:
        return []
    behavior_hash, equivalent = next(iter(sorted(behaviors.items())))
    equivalent.sort(key=lambda item: (item.complexity, _canonical(item.program)))
    representative: Evaluation | None = None
    gauge = (0, 0)
    for evaluation in equivalent:
        guarded, d4_checks, palette_checks = _gauge_guard(
            evaluation.program, demonstrations, normalized_limits
        )
        if guarded:
            representative = evaluation
            gauge = d4_checks, palette_checks
            break
    if representative is None:
        return []
    candidate = {
        "family": "relational_motion_algebra",
        "program": json.loads(_canonical(representative.program)),
        "train_outputs": [_plain(output) for output in representative.train_outputs if output is not None],
        "test_outputs": [_plain(output) for output in representative.test_outputs if output is not None],
        "complexity": representative.complexity,
        "evidence": {
            "all_demos_exact": True,
            "exact_replay": True,
            "enumeration_complete": True,
            "programs_enumerated": len(programs),
            "program_evaluations": required_evaluations,
            "exact_programs": len(exact),
            "near_mdl_programs": len(near),
            "test_behavior_classes": 1,
            "behavior_hash": behavior_hash,
            "leave_one_out_stable": True,
            "leave_one_out_programs_checked": loo_checked,
            "d4_equivariance_checks": gauge[0],
            "palette_bijection_checks": gauge[1],
            "task_identity_observed": False,
            "test_labels_observed": False,
        },
    }
    candidate["evidence"]["candidate_semantic_hash"] = _digest(candidate)
    return [candidate][: normalized_limits["max_candidates"]]


def _safe_task(task: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "train": [
            {"input": example["input"], "output": example["output"]}
            for example in task["train"]
        ],
        "test": [{"input": example["input"]} for example in task["test"]],
    }


def freeze_scan(
    challenges: Mapping[str, Mapping[str, Any]],
    *,
    limits: Mapping[str, Any] | None = None,
    source_hash: str | None = None,
    run_name: str = "relational-motion-algebra-scan",
) -> dict[str, Any]:
    records: dict[str, Any] = {}
    activated = 0
    for raw_task_id, task in sorted(challenges.items(), key=lambda item: str(item[0])):
        safe = _safe_task(task)
        candidates = compile_task(safe, limits)
        if len(candidates) > 1:
            raise AssertionError("one-candidate contract violated")
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
        "source_task_count": len(challenges),
        "activation_count": activated,
        "records": records,
        "claim_boundary": (
            "Challenge-only scan. Compilation received demonstrations and test inputs; "
            "no solution, score, baseline, or result artifact was opened."
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
    parser.add_argument("--run-name", default="relational-motion-algebra-scan")
    args = parser.parse_args(argv)
    raw = args.challenges.read_bytes()
    challenges = json.loads(raw.decode("utf-8-sig"))
    if not isinstance(challenges, Mapping):
        raise ValueError("challenges JSON must be an object")
    frozen = freeze_scan(
        challenges,
        source_hash=hashlib.sha256(raw).hexdigest(),
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
    "DEFAULTS",
    "SCHEMA",
    "Undefined",
    "compile_task",
    "execute_program",
    "freeze_scan",
    "replay_program",
]


if __name__ == "__main__":
    raise SystemExit(main())
