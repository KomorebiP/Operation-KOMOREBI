"""Hidden-structure recovery and relational routing for PR-LASM Block 15.

The entrant exposes a small, task-independent language for structures that are
easy to miss in the raw raster: guarded negative-space corridors, a compact
Cartesian subgrid hidden inside an interleaving, parity signals seeded inside
a maze, material-sensitive endpoint traces, stamp propagation across an axis
system, minimum-spanning connections between hollow frames, wiring between
four lattice ports, interacting finite emitters, and obstacle-triggered ray
routes.

Programs contain only operator names and scalar relational roles learned from
demonstrations.  They never contain task identifiers, corpus hashes, resolved
coordinates, test targets, or score information.  Compilation requires exact
demonstration replay, genuine leave-one-demonstration-out re-proposal,
deterministic double execution, and a single minimum-description behavior on
all supplied test inputs.  Undefined roles, tied routes, non-unique spanning
trees, and exhausted finite caps abstain.

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
from typing import Any, Callable


Grid = tuple[tuple[int, ...], ...]
Cell = tuple[int, int]
Pair = tuple[Grid, Grid]

AUTHOR = "Komorebi P."
SCHEMA = "komorebi.pr_lasm.block15.hidden_signal_router.program.v1"
SCAN_SCHEMA = "komorebi.pr_lasm.block15.hidden_signal_router.freeze.v1"
FOUR: tuple[Cell, ...] = ((-1, 0), (0, -1), (0, 1), (1, 0))


class Undefined(ValueError):
    """A structural role, unique route, or finite search is undefined."""


@dataclass(frozen=True, slots=True)
class Limits:
    max_side: int = 40
    max_examples: int = 20
    max_total_cells: int = 120_000
    max_programs: int = 256
    max_route_states: int = 100_000
    max_route_turns: int = 8
    max_candidates: int = 1
    mdl_slack: int = 0

    @classmethod
    def from_value(cls, raw: Any) -> "Limits":
        if isinstance(raw, cls):
            return raw
        if raw is None:
            return cls()
        if not isinstance(raw, Mapping):
            raise Undefined("limits must be a mapping")
        aliases = {
            "candidate_cap": "max_candidates",
            "max_grid_cells": "max_total_cells",
            "ambiguity_slack": "mdl_slack",
        }
        ignored = {
            "max_replay_calls",
            "max_replay_stages",
            "max_total_candidates",
            "max_trace_bytes",
            "time_limit",
            "time_limit_seconds",
        }
        values: dict[str, int] = {}
        for raw_name, raw_value in raw.items():
            name = aliases.get(str(raw_name), str(raw_name))
            if name in ignored:
                continue
            if name not in cls.__dataclass_fields__:
                raise Undefined("unknown finite limit")
            if isinstance(raw_value, bool) or not isinstance(raw_value, int):
                raise Undefined("finite limits must be integers")
            minimum = 0 if name == "mdl_slack" else 1
            if raw_value < minimum:
                raise Undefined("finite limit is below its minimum")
            values[name] = raw_value
        return cls(**values)


COMPLEXITY = {
    "cartesian_subgrid_extract": 6,
    "seeded_checker_component": 8,
    "endpoint_material_line": 9,
    "stamp_axis_completion": 10,
    "negative_space_router": 11,
    "frame_mst_connection": 12,
    "lattice_signal_wiring": 13,
    "interacting_emitters": 14,
    "obstacle_ray_route": 15,
}


def _canonical(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _grid(value: Any, max_side: int = 40) -> Grid:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or not value:
        raise Undefined("grid must be a nonempty row sequence")
    if len(value) > max_side:
        raise Undefined("grid height exceeds its cap")
    rows: list[tuple[int, ...]] = []
    width: int | None = None
    for raw_row in value:
        if (
            not isinstance(raw_row, Sequence)
            or isinstance(raw_row, (str, bytes))
            or not raw_row
        ):
            raise Undefined("grid row is invalid")
        if width is None:
            width = len(raw_row)
        if len(raw_row) != width or int(width) > max_side:
            raise Undefined("grid is ragged or too wide")
        row: list[int] = []
        for cell in raw_row:
            if isinstance(cell, bool) or not isinstance(cell, int) or not 0 <= cell <= 9:
                raise Undefined("ARC colors must be integers in [0, 9]")
            row.append(int(cell))
        rows.append(tuple(row))
    return tuple(rows)


def _plain(grid: Grid) -> list[list[int]]:
    return [list(row) for row in grid]


def _shape(grid: Grid) -> tuple[int, int]:
    return len(grid), len(grid[0])


def _mode(grid: Grid) -> int:
    counts = Counter(cell for row in grid for cell in row)
    peak = max(counts.values())
    winners = sorted(color for color, count in counts.items() if count == peak)
    if len(winners) != 1:
        raise Undefined("modal background is tied")
    return winners[0]


def _palette(grid: Grid) -> frozenset[int]:
    return frozenset(cell for row in grid for cell in row)


def _sanitize(task: Any, limits: Limits) -> tuple[tuple[Pair, ...], tuple[Grid, ...]]:
    if not isinstance(task, Mapping):
        raise Undefined("task must be a mapping")
    raw_train, raw_test = task.get("train"), task.get("test")
    if (
        not isinstance(raw_train, Sequence)
        or isinstance(raw_train, (str, bytes))
        or len(raw_train) < 2
        or not isinstance(raw_test, Sequence)
        or isinstance(raw_test, (str, bytes))
        or not raw_test
        or len(raw_train) + len(raw_test) > limits.max_examples
    ):
        raise Undefined("task needs bounded train and test splits")
    pairs: list[Pair] = []
    tests: list[Grid] = []
    cells = 0
    for record in raw_train:
        if not isinstance(record, Mapping):
            raise Undefined("demonstration must be a mapping")
        source = _grid(record.get("input"), limits.max_side)
        target = _grid(record.get("output"), limits.max_side)
        cells += len(source) * len(source[0]) + len(target) * len(target[0])
        pairs.append((source, target))
    for record in raw_test:
        if not isinstance(record, Mapping):
            raise Undefined("test record must be a mapping")
        # Deliberately read only the held record's input member.
        source = _grid(record.get("input"), limits.max_side)
        cells += len(source) * len(source[0])
        tests.append(source)
    if cells > limits.max_total_cells:
        raise Undefined("total cell cap exhausted")
    return tuple(pairs), tuple(tests)


def _components(grid: Grid, color: int) -> tuple[frozenset[Cell], ...]:
    height, width = _shape(grid)
    unseen = {
        (row, column)
        for row in range(height)
        for column in range(width)
        if grid[row][column] == color
    }
    result: list[frozenset[Cell]] = []
    while unseen:
        root = min(unseen)
        unseen.remove(root)
        queue = deque([root])
        cells = {root}
        while queue:
            row, column = queue.popleft()
            for dr, dc in FOUR:
                other = row + dr, column + dc
                if other in unseen:
                    unseen.remove(other)
                    cells.add(other)
                    queue.append(other)
        result.append(frozenset(cells))
    return tuple(sorted(result, key=lambda cells: (min(cells), len(cells))))


def _bbox(cells: Iterable[Cell]) -> tuple[int, int, int, int]:
    points = tuple(cells)
    if not points:
        raise Undefined("empty support")
    return (
        min(row for row, _ in points),
        max(row for row, _ in points),
        min(column for _, column in points),
        max(column for _, column in points),
    )


def _changed(source: Grid, target: Grid) -> tuple[tuple[int, int, int, int], ...]:
    if _shape(source) != _shape(target):
        return ()
    height, width = _shape(source)
    return tuple(
        (row, column, source[row][column], target[row][column])
        for row in range(height)
        for column in range(width)
        if source[row][column] != target[row][column]
    )


def _program(operator: str, **parameters: Any) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "operator": operator,
        "description_length": COMPLEXITY[operator],
        "root_scope": "immutable_input",
        "parameters": parameters,
    }


def _validate_program(value: Any) -> tuple[str, Mapping[str, Any]]:
    if not isinstance(value, Mapping) or value.get("schema") != SCHEMA:
        raise Undefined("program schema is invalid")
    operator = value.get("operator")
    parameters = value.get("parameters")
    if operator not in COMPLEXITY or not isinstance(parameters, Mapping):
        raise Undefined("operator or parameters are invalid")
    if value.get("root_scope") != "immutable_input":
        raise Undefined("program must execute from the immutable input")
    if value.get("description_length") != COMPLEXITY[operator]:
        raise Undefined("description length is invalid")
    return str(operator), parameters


def _proper_cartesian_subgrids(grid: Grid) -> tuple[Grid, ...]:
    height, width = _shape(grid)
    palette = sorted(_palette(grid))
    outputs: set[Grid] = set()
    for size in range(1, min(3, len(palette) - 1) + 1):
        for colors_tuple in itertools.combinations(palette, size):
            colors = frozenset(colors_tuple)
            points = {
                (row, column)
                for row in range(height)
                for column in range(width)
                if grid[row][column] in colors
            }
            rows = sorted({row for row, _ in points})
            columns = sorted({column for _, column in points})
            if len(rows) < 2 or len(rows) != len(columns):
                continue
            if points != {(row, column) for row in rows for column in columns}:
                continue
            outputs.add(tuple(tuple(grid[row][column] for column in columns) for row in rows))
    return tuple(sorted(outputs, key=_canonical))


def _cartesian_subgrid_extract(grid: Grid) -> Grid:
    outputs = _proper_cartesian_subgrids(grid)
    if len(outputs) != 1:
        raise Undefined("compact Cartesian subgrid is absent or tied")
    return outputs[0]


def _seeded_checker_component(grid: Grid, substrate: int) -> Grid:
    height, width = _shape(grid)
    counts = Counter(cell for row in grid for cell in row)
    candidates: list[tuple[Cell, int, int]] = []
    for row in range(height):
        for column in range(width):
            center_color = grid[row][column]
            if center_color == substrate or counts[center_color] != 1:
                continue
            neighbors = [
                grid[row + dr][column + dc]
                for dr, dc in FOUR
                if 0 <= row + dr < height and 0 <= column + dc < width
            ]
            noncenter = Counter(color for color in neighbors if color != center_color)
            if not noncenter:
                continue
            peak = max(noncenter.values())
            winners = sorted(color for color, count in noncenter.items() if count == peak)
            if peak < 3 or len(winners) != 1:
                continue
            neighbor_color = winners[0]
            if neighbor_color == substrate or counts[neighbor_color] not in (3, 4):
                continue
            neighbor_points = {
                (rr, cc)
                for rr in range(height)
                for cc in range(width)
                if grid[rr][cc] == neighbor_color
            }
            cardinal = {
                (row + dr, column + dc)
                for dr, dc in FOUR
                if 0 <= row + dr < height and 0 <= column + dc < width
            }
            if not neighbor_points <= cardinal:
                continue
            candidates.append(((row, column), center_color, neighbor_color))
    if len(candidates) != 1:
        raise Undefined("checker seed is absent or tied")
    center, center_color, neighbor_color = candidates[0]
    walkable = {substrate, center_color, neighbor_color}
    queue = deque([center])
    reached = {center}
    while queue:
        row, column = queue.popleft()
        for dr, dc in FOUR:
            other = row + dr, column + dc
            if (
                0 <= other[0] < height
                and 0 <= other[1] < width
                and other not in reached
                and grid[other[0]][other[1]] in walkable
            ):
                reached.add(other)
                queue.append(other)
    if not all(
        (row, column) in reached
        for row in range(height)
        for column in range(width)
        if grid[row][column] in (center_color, neighbor_color)
    ):
        raise Undefined("checker seeds occupy multiple components")
    output = _plain(grid)
    changed = 0
    for row, column in reached:
        if grid[row][column] != substrate:
            continue
        parity = (abs(row - center[0]) + abs(column - center[1])) % 2
        output[row][column] = center_color if parity == 0 else neighbor_color
        changed += 1
    if not changed:
        raise Undefined("checker component has no substrate")
    return _grid(output)


def _bresenham(first: Cell, second: Cell) -> tuple[Cell, ...]:
    row0, column0 = min(first, second)
    row1, column1 = max(first, second)
    delta_column = abs(column1 - column0)
    step_column = 1 if column0 < column1 else -1
    delta_row = -abs(row1 - row0)
    step_row = 1 if row0 < row1 else -1
    error = delta_column + delta_row
    points: list[Cell] = []
    while True:
        points.append((row0, column0))
        if (row0, column0) == (row1, column1):
            break
        twice = 2 * error
        if twice >= delta_row:
            error += delta_row
            column0 += step_column
        if twice <= delta_column:
            error += delta_column
            row0 += step_row
    return tuple(points)


def _endpoint_material_line(grid: Grid, accent: int, background: int) -> Grid:
    height, width = _shape(grid)
    if background not in _palette(grid):
        raise Undefined("endpoint background is absent")
    candidates: list[tuple[int, tuple[Cell, Cell]]] = []
    for color in sorted(_palette(grid) - {background}):
        points = tuple(
            (row, column)
            for row in range(height)
            for column in range(width)
            if grid[row][column] == color
        )
        if len(points) != 2:
            continue
        if not all(
            row in (0, height - 1) or column in (0, width - 1)
            for row, column in points
        ):
            continue
        candidates.append((color, (points[0], points[1])))
    if len(candidates) != 1 or accent in _palette(grid):
        raise Undefined("endpoint role is absent or tied")
    marker, endpoints = candidates[0]
    path = _bresenham(*endpoints)
    if len(path) < 3:
        raise Undefined("endpoint path is too short")
    output = _plain(grid)
    for row, column in path[1:-1]:
        if grid[row][column] == marker:
            raise Undefined("endpoint marker recurs inside the path")
        output[row][column] = marker if grid[row][column] == background else accent
    return _grid(output)


def _stamp_structures(grid: Grid) -> tuple[tuple[str, tuple[int, ...], tuple[Cell, ...]], ...]:
    height, width = _shape(grid)
    by_roles: dict[tuple[int, int], list[Cell]] = {}
    for row in range(1, height - 1):
        for column in range(1, width - 1):
            center_color = grid[row][column]
            ring = [
                grid[rr][cc]
                for rr in range(row - 1, row + 2)
                for cc in range(column - 1, column + 2)
                if (rr, cc) != (row, column)
            ]
            if len(set(ring)) == 1 and ring[0] != center_color:
                by_roles.setdefault((ring[0], center_color), []).append((row, column))
    structures: list[tuple[str, tuple[int, ...], tuple[Cell, ...]]] = []
    for (stamp_color, line_color), raw_centers in sorted(by_roles.items()):
        centers = tuple(sorted(raw_centers))
        columns = tuple(
            column
            for column in range(width)
            if all(grid[row][column] in (line_color, stamp_color) for row in range(height))
            and any(grid[row][column] == line_color for row in range(height))
        )
        rows = tuple(
            row
            for row in range(height)
            if all(grid[row][column] in (line_color, stamp_color) for column in range(width))
            and any(grid[row][column] == line_color for column in range(width))
        )
        if bool(columns) == bool(rows):
            continue
        if columns and all(column in columns for _, column in centers):
            structures.append(("vertical", columns, centers))
        elif rows and all(row in rows for row, _ in centers):
            structures.append(("horizontal", rows, centers))
    return tuple(structures)


def _stamp_axis_completion(grid: Grid, fill: int) -> Grid:
    structures = _stamp_structures(grid)
    if len(structures) != 1 or fill in _palette(grid):
        raise Undefined("axis/stamp structure is absent or tied")
    orientation, axes, centers = structures[0]
    height, width = _shape(grid)
    background = _mode(grid)
    output = _plain(grid)
    center_set = set(centers)
    if orientation == "vertical":
        event_axes = sorted({row for row, _ in centers})
        for row in event_axes:
            for column in range(width):
                if output[row][column] == background:
                    output[row][column] = fill
        crossings = ((row, column) for row in event_axes for column in axes)
    else:
        event_axes = sorted({column for _, column in centers})
        for column in event_axes:
            for row in range(height):
                if output[row][column] == background:
                    output[row][column] = fill
        crossings = ((row, column) for row in axes for column in event_axes)
    for row, column in crossings:
        if (row, column) in center_set:
            continue
        if not (1 <= row < height - 1 and 1 <= column < width - 1):
            raise Undefined("derived stamp leaves the canvas")
        for rr in range(row - 1, row + 2):
            for cc in range(column - 1, column + 2):
                if (rr, cc) != (row, column):
                    output[rr][cc] = fill
    return _grid(output)


def _maximal_empty_rectangles(grid: Grid, background: int) -> tuple[tuple[int, int, int, int], ...]:
    height, width = _shape(grid)
    best_area = 0
    best: list[tuple[int, int, int, int]] = []
    for top in range(height):
        open_columns = [True] * width
        for bottom in range(top, height):
            open_columns = [
                open_columns[column] and grid[bottom][column] == background
                for column in range(width)
            ]
            column = 0
            while column < width:
                if not open_columns[column]:
                    column += 1
                    continue
                left = column
                while column + 1 < width and open_columns[column + 1]:
                    column += 1
                right = column
                area = (bottom - top + 1) * (right - left + 1)
                rectangle = (top, bottom, left, right)
                if area > best_area:
                    best_area, best = area, [rectangle]
                elif area == best_area:
                    best.append(rectangle)
                column += 1
    return tuple(best)


def _negative_space_router(grid: Grid, fill: int) -> Grid:
    if len(_palette(grid)) != 2 or fill in _palette(grid):
        raise Undefined("negative-space source palette is invalid")
    height, width = _shape(grid)
    background = _mode(grid)
    rectangles = _maximal_empty_rectangles(grid, background)
    if len(rectangles) != 1:
        raise Undefined("maximum empty corridor is tied")
    top, bottom, left, right = rectangles[0]
    corridor_height, corridor_width = bottom - top + 1, right - left + 1
    if max(corridor_height, corridor_width) < 2 * min(corridor_height, corridor_width):
        raise Undefined("maximum empty rectangle is not a corridor")
    output = _plain(grid)
    if corridor_height > corridor_width:
        if corridor_width < 3:
            raise Undefined("vertical corridor lacks a guard band")
        longitudinal = range(top + int(top > 0), bottom + 1 - int(bottom < height - 1))
        for row in longitudinal:
            for column in range(left + 1, right):
                output[row][column] = fill
        side_domains = ((0, left), (right, width - 1))
        for start_column, end_column in side_domains:
            good = [
                all(grid[row][column] == background for column in range(start_column, end_column + 1))
                for row in range(height)
            ]
            row = 0
            while row < height:
                if not good[row]:
                    row += 1
                    continue
                start_row = row
                while row + 1 < height and good[row + 1]:
                    row += 1
                end_row = row
                if end_row - start_row + 1 >= 3:
                    inner_start = start_row + int(start_row > 0)
                    inner_end = end_row - int(end_row < height - 1)
                    for rr in range(inner_start, inner_end + 1):
                        for column in range(start_column, end_column + 1):
                            output[rr][column] = fill
                row += 1
    else:
        if corridor_height < 3:
            raise Undefined("horizontal corridor lacks a guard band")
        longitudinal = range(left + int(left > 0), right + 1 - int(right < width - 1))
        for row in range(top + 1, bottom):
            for column in longitudinal:
                output[row][column] = fill
        side_domains = ((0, top), (bottom, height - 1))
        for start_row, end_row in side_domains:
            good = [
                all(grid[row][column] == background for row in range(start_row, end_row + 1))
                for column in range(width)
            ]
            column = 0
            while column < width:
                if not good[column]:
                    column += 1
                    continue
                start_column = column
                while column + 1 < width and good[column + 1]:
                    column += 1
                end_column = column
                if end_column - start_column + 1 >= 3:
                    inner_start = start_column + int(start_column > 0)
                    inner_end = end_column - int(end_column < width - 1)
                    for cc in range(inner_start, inner_end + 1):
                        for row in range(start_row, end_row + 1):
                            output[row][cc] = fill
                column += 1
    result = _grid(output)
    if result == grid:
        raise Undefined("negative-space router is an identity")
    return result


def _hollow_rectangles(grid: Grid) -> tuple[int, int, tuple[tuple[int, int, int, int], ...]]:
    background = _mode(grid)
    colors = sorted(_palette(grid) - {background})
    if len(colors) != 1:
        raise Undefined("frame scene must be binary")
    frame = colors[0]
    rectangles: list[tuple[int, int, int, int]] = []
    for component in _components(grid, frame):
        top, bottom, left, right = _bbox(component)
        if bottom - top < 2 or right - left < 2:
            raise Undefined("frame has no interior")
        perimeter = {
            (row, column)
            for row in range(top, bottom + 1)
            for column in range(left, right + 1)
            if row in (top, bottom) or column in (left, right)
        }
        if set(component) != perimeter:
            raise Undefined("component is not a hollow rectangle")
        rectangles.append((top, bottom, left, right))
    if len(rectangles) < 2:
        raise Undefined("frame scene needs multiple rectangles")
    return background, frame, tuple(sorted(rectangles))


def _frame_edges(rectangles: Sequence[tuple[int, int, int, int]]) -> tuple[tuple[Any, ...], ...]:
    edges: list[tuple[Any, ...]] = []
    for first_index, first in enumerate(rectangles):
        for second_index in range(first_index + 1, len(rectangles)):
            second = rectangles[second_index]
            if first[3] < second[2] or second[3] < first[2]:
                left, right = (first, second) if first[3] < second[2] else (second, first)
                low = max(left[0] + 1, right[0] + 1)
                high = min(left[1] - 1, right[1] - 1)
                if low <= high:
                    gap = right[2] - left[3] - 1
                    edges.append((gap, first_index, second_index, "horizontal", low, high, left[3], right[2]))
            if first[1] < second[0] or second[1] < first[0]:
                upper, lower = (first, second) if first[1] < second[0] else (second, first)
                low = max(upper[2] + 1, lower[2] + 1)
                high = min(upper[3] - 1, lower[3] - 1)
                if low <= high:
                    gap = lower[0] - upper[1] - 1
                    edges.append((gap, first_index, second_index, "vertical", low, high, upper[1], lower[0]))
    return tuple(edges)


def _mst(
    edges: Sequence[tuple[Any, ...]],
    vertex_count: int,
    skip: int | None = None,
) -> tuple[int, tuple[int, ...]] | None:
    parents = list(range(vertex_count))

    def root(vertex: int) -> int:
        while parents[vertex] != vertex:
            parents[vertex] = parents[parents[vertex]]
            vertex = parents[vertex]
        return vertex

    chosen: list[int] = []
    total = 0
    order = sorted(range(len(edges)), key=lambda index: (edges[index], index))
    for edge_index in order:
        if edge_index == skip:
            continue
        edge = edges[edge_index]
        first, second = root(int(edge[1])), root(int(edge[2]))
        if first == second:
            continue
        parents[first] = second
        total += int(edge[0])
        chosen.append(edge_index)
    if len(chosen) != vertex_count - 1:
        return None
    return total, tuple(chosen)


def _frame_mst_connection(grid: Grid) -> Grid:
    background, frame, rectangles = _hollow_rectangles(grid)
    edges = _frame_edges(rectangles)
    spanning = _mst(edges, len(rectangles))
    if spanning is None:
        raise Undefined("frame graph is disconnected")
    total, chosen = spanning
    for edge_index in chosen:
        alternate = _mst(edges, len(rectangles), skip=edge_index)
        if alternate is not None and alternate[0] == total:
            raise Undefined("minimum frame connection is not unique")
    output = _plain(grid)
    for edge_index in chosen:
        _, _, _, orientation, low, high, start, end = edges[edge_index]
        if orientation == "horizontal":
            for row in range(low, high + 1):
                for column in range(start, end + 1):
                    output[row][column] = frame if row in (low, high) else background
        else:
            for row in range(start, end + 1):
                for column in range(low, high + 1):
                    output[row][column] = frame if column in (low, high) else background
    return _grid(output)


def _signal_rectangles(grid: Grid, color: int) -> tuple[tuple[int, int, int, int], ...] | None:
    components = _components(grid, color)
    if len(components) != 4:
        return None
    boxes: list[tuple[int, int, int, int]] = []
    for component in components:
        box = _bbox(component)
        if len(component) != (box[1] - box[0] + 1) * (box[3] - box[2] + 1):
            return None
        boxes.append(box)
    heights = {bottom - top + 1 for top, bottom, _, _ in boxes}
    widths = {right - left + 1 for _, _, left, right in boxes}
    tops = sorted({top for top, _, _, _ in boxes})
    lefts = sorted({left for _, _, left, _ in boxes})
    if len(heights) != 1 or len(widths) != 1 or len(tops) != 2 or len(lefts) != 2:
        return None
    if {(top, left) for top, _, left, _ in boxes} != {
        (top, left) for top in tops for left in lefts
    }:
        return None
    return tuple(sorted(boxes))


def _lattice_signal_wiring(grid: Grid, carrier: int) -> Grid:
    height, width = _shape(grid)
    if carrier not in _palette(grid):
        raise Undefined("carrier color is absent")
    claims: dict[Cell, int] = {}
    signal_count = 0
    for color in sorted(_palette(grid) - {carrier}):
        boxes = _signal_rectangles(grid, color)
        if boxes is None:
            continue
        signal_count += 1
        box_height = boxes[0][1] - boxes[0][0] + 1
        box_width = boxes[0][3] - boxes[0][2] + 1
        tops = sorted({box[0] for box in boxes})
        lefts = sorted({box[2] for box in boxes})
        edge_cells = {
            (row, column)
            for row in tuple(range(tops[0], tops[0] + box_height))
            + tuple(range(tops[1], tops[1] + box_height))
            for column in range(lefts[0], lefts[1] + box_width)
        } | {
            (row, column)
            for row in range(tops[0], tops[1] + box_height)
            for column in tuple(range(lefts[0], lefts[0] + box_width))
            + tuple(range(lefts[1], lefts[1] + box_width))
        }
        for cell in edge_cells:
            if grid[cell[0]][cell[1]] != carrier:
                continue
            if cell in claims and claims[cell] != color:
                raise Undefined("signal wires collide")
            claims[cell] = color
    if not signal_count or not claims:
        raise Undefined("four-port signal rectangle is absent")
    output = _plain(grid)
    for (row, column), color in claims.items():
        output[row][column] = color
    return _grid(output)


ACTION_SPECS: Mapping[str, tuple[Cell, tuple[Cell, ...]]] = {
    "hook_ne": ((-1, 2), ((0, 1), (0, 2))),
    "west_four": ((0, -4), ((0, -1), (0, -2), (0, -3))),
    "south_three": ((3, 0), ((1, 0), (2, 0))),
    "north_six": ((-6, 0), ((-1, 0), (-2, 0), (-3, 0), (-4, 0), (-5, 0))),
}


def _interacting_emitters(
    grid: Grid,
    colors_by_action: Mapping[str, Any],
    trail: int,
    collision: int,
) -> Grid:
    height, width = _shape(grid)
    background = _mode(grid)
    if set(colors_by_action) != set(ACTION_SPECS):
        raise Undefined("emitter role map is incomplete")
    action_by_color: dict[int, str] = {}
    for action, raw_color in colors_by_action.items():
        if isinstance(raw_color, bool) or not isinstance(raw_color, int):
            raise Undefined("emitter color is invalid")
        if int(raw_color) in action_by_color:
            raise Undefined("emitter colors are not injective")
        action_by_color[int(raw_color)] = action
    emitters: list[tuple[Cell, int, str]] = []
    for row in range(height):
        for column in range(width):
            color = grid[row][column]
            if color == background:
                continue
            if color not in action_by_color:
                raise Undefined("unbound emitter color")
            emitters.append(((row, column), color, action_by_color[color]))
    if not emitters or len({color for _, color, _ in emitters}) != len(emitters):
        raise Undefined("emitters must be singleton roles")
    proposals: dict[Cell, list[int]] = {}
    clones: list[tuple[Cell, int]] = []
    for (row, column), color, action in emitters:
        duplicate, trail_offsets = ACTION_SPECS[action]
        destination = row + duplicate[0], column + duplicate[1]
        if not (0 <= destination[0] < height and 0 <= destination[1] < width):
            raise Undefined("emitter clone leaves the canvas")
        if grid[destination[0]][destination[1]] != background:
            raise Undefined("emitter clone collides with source material")
        clones.append((destination, color))
        for dr, dc in trail_offsets:
            cell = row + dr, column + dc
            if not (0 <= cell[0] < height and 0 <= cell[1] < width):
                raise Undefined("emitter trail leaves the canvas")
            if grid[cell[0]][cell[1]] != background:
                raise Undefined("emitter trail collides with source material")
            proposals.setdefault(cell, []).append(color)
    if len({cell for cell, _ in clones}) != len(clones):
        raise Undefined("emitter clones collide")
    output = _plain(grid)
    for (row, column), sources in proposals.items():
        output[row][column] = collision if len(sources) > 1 else trail
    for (row, column), color in clones:
        if (row, column) in proposals:
            raise Undefined("clone and trail collide")
        output[row][column] = color
    collision_cells = sorted(cell for cell, sources in proposals.items() if len(sources) > 1)
    for row, column in collision_cells:
        while 0 <= row < height and 0 <= column < width:
            if grid[row][column] != background:
                raise Undefined("collision ray strikes source material")
            output[row][column] = collision
            row += 1
            column -= 1
    return _grid(output)


def _ray_routes(
    grid: Grid,
    source_color: int,
    target_color: int,
    limits: Limits,
) -> tuple[tuple[Cell, ...], ...]:
    height, width = _shape(grid)
    background = _mode(grid)
    source_components = _components(grid, source_color)
    target_components = _components(grid, target_color)
    if len(source_components) != 1 or len(target_components) != 1:
        raise Undefined("route ports must each be connected")
    source, target = source_components[0], target_components[0]
    if len(source) != 2 or len(target) != 2:
        raise Undefined("route ports must be dominoes")
    first, second = tuple(sorted(source))
    if abs(first[0] - second[0]) + abs(first[1] - second[1]) != 1:
        raise Undefined("source port is not an axial domino")
    starts = (
        (first, (first[0] - second[0], first[1] - second[1])),
        (second, (second[0] - first[0], second[1] - first[1])),
    )
    stack: list[tuple[Cell, Cell, tuple[Cell, ...], int, frozenset[tuple[Cell, Cell]]]] = [
        (position, direction, (), 0, frozenset({(position, direction)}))
        for position, direction in starts
    ]
    routes: set[tuple[Cell, ...]] = set()
    states = 0
    while stack:
        position, direction, path, turns, seen = stack.pop()
        states += 1
        if states > limits.max_route_states:
            raise Undefined("route state cap exhausted")
        if path and any(
            abs(position[0] - row) + abs(position[1] - column) == 1
            for row, column in target
        ):
            routes.add(path)
            continue
        forward = position[0] + direction[0], position[1] + direction[1]
        if (
            0 <= forward[0] < height
            and 0 <= forward[1] < width
            and grid[forward[0]][forward[1]] == background
            and forward not in path
        ):
            state = forward, direction
            if state not in seen:
                stack.append((forward, direction, path + (forward,), turns, seen | {state}))
            continue
        if turns >= limits.max_route_turns:
            continue
        for new_direction in (
            (-direction[1], direction[0]),
            (direction[1], -direction[0]),
        ):
            neighbor = position[0] + new_direction[0], position[1] + new_direction[1]
            state = position, new_direction
            if (
                0 <= neighbor[0] < height
                and 0 <= neighbor[1] < width
                and grid[neighbor[0]][neighbor[1]] == background
                and state not in seen
            ):
                stack.append((position, new_direction, path, turns + 1, seen | {state}))
    return tuple(sorted(routes, key=lambda path: (len(path), path)))


def _obstacle_ray_route(
    grid: Grid,
    source_color: int,
    target_color: int,
    limits: Limits,
) -> Grid:
    routes = _ray_routes(grid, source_color, target_color, limits)
    if not routes:
        raise Undefined("no obstacle-triggered route reaches the target port")
    shortest = len(routes[0])
    winners = tuple(path for path in routes if len(path) == shortest)
    if len(winners) != 1:
        raise Undefined("shortest obstacle-triggered route is tied")
    output = _plain(grid)
    for row, column in winners[0]:
        output[row][column] = source_color
    return _grid(output)


def _execute(program: Mapping[str, Any], grid: Grid, limits: Limits) -> Grid:
    operator, parameters = _validate_program(program)
    if operator == "cartesian_subgrid_extract":
        return _cartesian_subgrid_extract(grid)
    if operator == "seeded_checker_component":
        return _seeded_checker_component(grid, int(parameters["substrate"]))
    if operator == "endpoint_material_line":
        return _endpoint_material_line(
            grid,
            int(parameters["accent"]),
            int(parameters["background"]),
        )
    if operator == "stamp_axis_completion":
        return _stamp_axis_completion(grid, int(parameters["fill"]))
    if operator == "negative_space_router":
        return _negative_space_router(grid, int(parameters["fill"]))
    if operator == "frame_mst_connection":
        return _frame_mst_connection(grid)
    if operator == "lattice_signal_wiring":
        return _lattice_signal_wiring(grid, int(parameters["carrier"]))
    if operator == "interacting_emitters":
        colors = parameters.get("colors_by_action")
        if not isinstance(colors, Mapping):
            raise Undefined("emitter role map is missing")
        return _interacting_emitters(
            grid,
            colors,
            int(parameters["trail"]),
            int(parameters["collision"]),
        )
    if operator == "obstacle_ray_route":
        return _obstacle_ray_route(
            grid,
            int(parameters["source_color"]),
            int(parameters["target_color"]),
            limits,
        )
    raise Undefined("unknown operator")


def execute_program(
    program: Mapping[str, Any],
    value: Any,
    limits: Mapping[str, Any] | Limits | None = None,
) -> list[list[int]]:
    """Execute a frozen hidden-signal program from an immutable raster."""

    bounds = Limits.from_value(limits)
    return _plain(_execute(program, _grid(value, bounds.max_side), bounds))


def replay_program(
    program: Mapping[str, Any],
    value: Any,
    limits: Mapping[str, Any] | Limits | None = None,
) -> dict[str, Any]:
    """Return a deterministic, tournament-verifiable one-stage replay."""

    bounds = Limits.from_value(limits)
    source = _grid(value, bounds.max_side)
    output = _execute(program, source, bounds)
    operator, _ = _validate_program(program)
    return {
        "output": _plain(output),
        "stages": [
            {
                "name": operator,
                "input": _plain(source),
                "output": _plain(output),
            }
        ],
    }


def _uniform_target_only(pairs: Sequence[Pair]) -> tuple[int, ...]:
    candidates: set[int] | None = None
    for source, target in pairs:
        extra = set(_palette(target) - _palette(source))
        candidates = extra if candidates is None else candidates & extra
    return tuple(sorted(candidates or ()))


def _uniform_changed_source(pairs: Sequence[Pair]) -> tuple[int, ...]:
    candidates: set[int] | None = None
    for source, target in pairs:
        changes = _changed(source, target)
        old = {before for _, _, before, _ in changes}
        candidates = old if candidates is None else candidates & old
    return tuple(sorted(candidates or ()))


def _candidate_parameters(pairs: Sequence[Pair], limits: Limits) -> Iterable[dict[str, Any]]:
    # Parameter-free structural recognizers.
    yield _program("cartesian_subgrid_extract")
    yield _program("frame_mst_connection")

    for color in _uniform_target_only(pairs):
        yield _program("stamp_axis_completion", fill=color)
        yield _program("negative_space_router", fill=color)
        background_candidates: set[int] | None = None
        for source, target in pairs:
            height, width = _shape(source)
            local: set[int] = set()
            if _shape(source) == _shape(target):
                for marker in _palette(source):
                    points = [
                        (row, column)
                        for row in range(height)
                        for column in range(width)
                        if source[row][column] == marker
                    ]
                    if len(points) != 2:
                        continue
                    local.update(
                        before
                        for _, _, before, after in _changed(source, target)
                        if after == marker
                    )
            background_candidates = (
                local
                if background_candidates is None
                else background_candidates & local
            )
        for background in sorted(background_candidates or ()):
            yield _program(
                "endpoint_material_line",
                accent=color,
                background=background,
            )

    for color in _uniform_changed_source(pairs):
        yield _program("seeded_checker_component", substrate=color)
        yield _program("lattice_signal_wiring", carrier=color)

    # Infer source and target port colors from added route material.
    port_candidates: set[tuple[int, int]] | None = None
    for source, target in pairs:
        changes = _changed(source, target)
        added = {after for _, _, _, after in changes}
        local: set[tuple[int, int]] = set()
        if len(added) == 1:
            source_color = next(iter(added))
            for target_color in sorted(_palette(source) - {_mode(source), source_color}):
                local.add((source_color, target_color))
        port_candidates = local if port_candidates is None else port_candidates & local
    for source_color, target_color in sorted(port_candidates or ()):
        yield _program(
            "obstacle_ray_route",
            source_color=source_color,
            target_color=target_color,
        )

    # The emitter algebra is inferred jointly so every role remains observable
    # in every leave-one-demonstration-out training fold.
    backgrounds: list[int] = []
    role_colors: set[int] = set()
    for source, _ in pairs:
        try:
            background = _mode(source)
        except Undefined:
            break
        backgrounds.append(background)
        role_colors.update(_palette(source) - {background})
    target_only = set().union(*(_palette(target) - _palette(source) for source, target in pairs))
    if len(role_colors) == 4 and len(target_only) == 2 and len(set(backgrounds)) == 1:
        actions = tuple(sorted(ACTION_SPECS))
        for ordered_colors in itertools.permutations(sorted(role_colors)):
            colors_by_action = dict(zip(actions, ordered_colors))
            for trail, collision in itertools.permutations(sorted(target_only)):
                yield _program(
                    "interacting_emitters",
                    colors_by_action=colors_by_action,
                    trail=trail,
                    collision=collision,
                )


def _exact_programs(pairs: Sequence[Pair], limits: Limits) -> tuple[dict[str, Any], ...]:
    seen: set[str] = set()
    exact: list[dict[str, Any]] = []
    generated = 0
    for program in _candidate_parameters(pairs, limits):
        key = _canonical(program)
        if key in seen:
            continue
        seen.add(key)
        generated += 1
        if generated > limits.max_programs:
            raise Undefined("program enumeration cap exhausted")
        try:
            predictions = tuple(_execute(program, source, limits) for source, _ in pairs)
        except (Undefined, KeyError, TypeError, ValueError):
            continue
        if predictions == tuple(target for _, target in pairs):
            exact.append(program)
    return tuple(sorted(exact, key=lambda program: (program["description_length"], _canonical(program))))


def _minimum_programs(pairs: Sequence[Pair], limits: Limits) -> tuple[dict[str, Any], ...]:
    exact = _exact_programs(pairs, limits)
    if not exact:
        return ()
    minimum = min(int(program["description_length"]) for program in exact)
    return tuple(
        program
        for program in exact
        if int(program["description_length"]) <= minimum + limits.mdl_slack
    )


def _loo_guard(pairs: Sequence[Pair], limits: Limits) -> tuple[bool, int, int]:
    re_proposals = 0
    behavior_classes = 0
    for held_index, (held_source, held_target) in enumerate(pairs):
        reduced = tuple(pair for index, pair in enumerate(pairs) if index != held_index)
        if not reduced:
            return False, re_proposals, behavior_classes
        try:
            programs = _minimum_programs(reduced, limits)
        except Undefined:
            return False, re_proposals, behavior_classes
        re_proposals += len(programs)
        if not programs:
            return False, re_proposals, behavior_classes
        predictions: set[Grid] = set()
        for program in programs:
            try:
                predictions.add(_execute(program, held_source, limits))
            except (Undefined, KeyError, TypeError, ValueError):
                return False, re_proposals, behavior_classes
        behavior_classes += len(predictions)
        if predictions != {held_target}:
            return False, re_proposals, behavior_classes
    return True, re_proposals, behavior_classes


def compile_task(
    task: Any,
    limits: Mapping[str, Any] | Limits | None = None,
) -> list[dict[str, Any]]:
    """Compile one exact, LOO-stable, behaviorally unique router or abstain."""

    try:
        bounds = Limits.from_value(limits)
        if bounds.max_programs < len(COMPLEXITY):
            raise Undefined("operator-family enumeration cap exhausted")
        pairs, tests = _sanitize(task, bounds)
        programs = _minimum_programs(pairs, bounds)
    except (Undefined, KeyError, TypeError, ValueError):
        return []
    if not programs:
        return []
    behaviors: dict[str, list[tuple[dict[str, Any], tuple[Grid, ...]]]] = {}
    for program in programs:
        try:
            outputs = tuple(_execute(program, grid, bounds) for grid in tests)
        except (Undefined, KeyError, TypeError, ValueError):
            continue
        key = _digest([_plain(output) for output in outputs])
        behaviors.setdefault(key, []).append((program, outputs))
    if len(behaviors) != 1:
        return []
    behavior_hash, equivalents = next(iter(sorted(behaviors.items())))
    equivalents.sort(key=lambda item: (item[0]["description_length"], _canonical(item[0])))
    representative, test_outputs = equivalents[0]
    loo_ok, re_proposals, loo_classes = _loo_guard(pairs, bounds)
    if not loo_ok:
        return []
    try:
        train_outputs = tuple(_execute(representative, source, bounds) for source, _ in pairs)
        train_repeat = tuple(_execute(representative, source, bounds) for source, _ in pairs)
        test_repeat = tuple(_execute(representative, source, bounds) for source in tests)
    except (Undefined, KeyError, TypeError, ValueError):
        return []
    if (
        train_outputs != tuple(target for _, target in pairs)
        or train_outputs != train_repeat
        or test_outputs != test_repeat
    ):
        return []
    operator = str(representative["operator"])
    candidate: dict[str, Any] = {
        "family": f"hidden_signal_router.{operator}",
        "program": representative,
        "train_outputs": [_plain(output) for output in train_outputs],
        "test_outputs": [_plain(output) for output in test_outputs],
        "complexity": int(representative["description_length"]),
        "evidence": {
            "all_demonstrations_exact": True,
            "exact_replay": True,
            "leave_one_demonstration_out_reproposal": True,
            "leave_one_out_programs": re_proposals,
            "leave_one_out_behavior_classes": loo_classes,
            "deterministic_double_execution": True,
            "bounded_enumeration_complete": True,
            "hard_caps_exhausted": False,
            "minimum_mdl_programs": len(programs),
            "full_test_behavior_classes": len(behaviors),
            "full_test_behavior_hash": behavior_hash,
            "equivalent_programs": len(equivalents),
            "serialized_resolved_coordinates": False,
            "runtime_task_identity_observed": False,
            "test_labels_observed": False,
            "solution_store_observed": False,
            "score_observed": False,
        },
    }
    candidate["evidence"]["candidate_semantic_hash"] = _digest(candidate)
    return [candidate][: bounds.max_candidates]


def freeze_challenges(challenges: Mapping[str, Any]) -> dict[str, Any]:
    """Run a label-blind challenge scan and freeze every activation."""

    activations: list[dict[str, Any]] = []
    for task_id in sorted(challenges):
        candidates = compile_task(challenges[task_id])
        if not candidates:
            continue
        activations.append({"task_id": task_id, **candidates[0]})
    body: dict[str, Any] = {
        "schema": SCAN_SCHEMA,
        "author": AUTHOR,
        "phase": "label_blind_challenge_only_freeze",
        "tasks_scanned": len(challenges),
        "activation_count": len(activations),
        "activations": activations,
        "solutions_observed": False,
        "submission_observed": False,
        "scores_observed": False,
    }
    body["content_hash"] = _digest(body)
    return body


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--challenges", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    challenges = json.loads(args.challenges.read_text(encoding="utf-8-sig"))
    freeze = freeze_challenges(challenges)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(freeze, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(_canonical({key: freeze[key] for key in ("tasks_scanned", "activation_count", "content_hash")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
