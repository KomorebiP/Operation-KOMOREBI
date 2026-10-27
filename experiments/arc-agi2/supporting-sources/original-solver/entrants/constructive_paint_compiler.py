"""Label-blind constructive-painting compiler for PR-LASM Block 15.

The finite grammar covers same-canvas constructions whose demonstrations add
geometry rather than extract a subscene: line/ray propagation, concentric and
periodic contours, keyed frame construction, reflected and scaled stamps, and
component symmetry closure.  Programs contain only operator names and compact
parameters induced from the demonstrations; neither task identities nor cached
test rasters are available to the executor.

Author: Komorebi P.
"""

from __future__ import annotations

from collections import Counter, defaultdict, deque
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import hashlib
import itertools
import json
from typing import Any, Callable


Grid = tuple[tuple[int, ...], ...]
Cell = tuple[int, int]
Pair = tuple[Grid, Grid]

AUTHOR = "Komorebi P."
SCHEMA = "komorebi.pr_lasm.block15.constructive_paint_compiler.program.v1"


class Undefined(ValueError):
    """The requested intrinsic construction is absent or ambiguous."""


@dataclass(frozen=True, slots=True)
class Limits:
    max_grid_cells: int = 900
    max_examples: int = 20
    max_programs: int = 96
    max_executor_calls: int = 50_000
    max_components: int = 256
    max_candidates: int = 1

    @classmethod
    def from_value(cls, value: Mapping[str, Any] | None) -> "Limits":
        if value is None:
            return cls()
        if not isinstance(value, Mapping):
            raise Undefined("limits must be a mapping")
        aliases = {"candidate_cap": "max_candidates"}
        accepted = {
            "max_replay_calls",
            "max_replay_stages",
            "max_total_candidates",
            "max_trace_bytes",
            "time_limit",
            "time_limit_seconds",
        }
        ceilings = {
            "max_grid_cells": 3_600,
            "max_examples": 40,
            "max_programs": 512,
            "max_executor_calls": 500_000,
            "max_components": 1_024,
            "max_candidates": 1,
        }
        unknown = set(value) - set(ceilings) - set(aliases) - accepted
        if unknown:
            raise Undefined("unknown finite limit")
        defaults = cls()
        parsed: dict[str, int] = {}
        for name, ceiling in ceilings.items():
            alias = next((key for key, target in aliases.items() if target == name), None)
            raw = value.get(name, value.get(alias, getattr(defaults, name)))
            if isinstance(raw, bool) or not isinstance(raw, int) or raw < 1:
                raise Undefined(f"limits.{name} must be positive")
            parsed[name] = min(raw, ceiling)
        return cls(**parsed)


def _canonical(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    )


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _grid(value: Any, limits: Limits | None = None) -> Grid:
    bounds = limits or Limits()
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or not value:
        raise Undefined("grid must be a nonempty row sequence")
    rows: list[tuple[int, ...]] = []
    width: int | None = None
    for raw_row in value:
        if not isinstance(raw_row, Sequence) or isinstance(raw_row, (str, bytes)) or not raw_row:
            raise Undefined("grid row is invalid")
        row: list[int] = []
        for cell in raw_row:
            if isinstance(cell, bool) or not isinstance(cell, int) or not 0 <= cell <= 9:
                raise Undefined("grid colors must be integers in [0, 9]")
            row.append(int(cell))
        if width is None:
            width = len(row)
        elif width != len(row):
            raise Undefined("grid is ragged")
        rows.append(tuple(row))
    if len(rows) * int(width or 0) > bounds.max_grid_cells:
        raise Undefined("grid exceeds the finite cell bound")
    return tuple(rows)


def _plain(grid: Grid) -> list[list[int]]:
    return [list(row) for row in grid]


def _freeze(rows: Sequence[Sequence[int]]) -> Grid:
    return tuple(tuple(int(cell) for cell in row) for row in rows)


def _shape(grid: Grid) -> tuple[int, int]:
    return len(grid), len(grid[0])


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
        raise Undefined("task requires bounded train and test splits")
    train: list[Pair] = []
    for example in raw_train:
        if not isinstance(example, Mapping):
            raise Undefined("training example is invalid")
        source = _grid(example.get("input"), limits)
        target = _grid(example.get("output"), limits)
        if _shape(source) != _shape(target):
            raise Undefined("constructive painting requires equal canvas shapes")
        train.append((source, target))
    tests: list[Grid] = []
    for example in raw_test:
        if not isinstance(example, Mapping):
            raise Undefined("test example is invalid")
        # Deliberately ignore any injected held-out output field.
        tests.append(_grid(example.get("input"), limits))
    return tuple(train), tuple(tests)


def _background(grid: Grid) -> int:
    counts = Counter(cell for row in grid for cell in row)
    maximum = max(counts.values())
    winners = [color for color, count in counts.items() if count == maximum]
    if len(winners) != 1:
        raise Undefined("background mode is tied")
    return winners[0]


def _supports(grid: Grid, background: int) -> dict[int, frozenset[Cell]]:
    result: dict[int, set[Cell]] = defaultdict(set)
    for row, values in enumerate(grid):
        for column, color in enumerate(values):
            if color != background:
                result[color].add((row, column))
    return {color: frozenset(cells) for color, cells in result.items()}


def _components(
    grid: Grid, background: int, *, connectivity: int = 4, monochrome: bool = True
) -> tuple[tuple[int, frozenset[Cell]], ...]:
    height, width = _shape(grid)
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    if connectivity == 8:
        directions += [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    seen: set[Cell] = set()
    result: list[tuple[int, frozenset[Cell]]] = []
    for row in range(height):
        for column in range(width):
            if grid[row][column] == background or (row, column) in seen:
                continue
            color = grid[row][column]
            queue: deque[Cell] = deque([(row, column)])
            seen.add((row, column))
            cells: set[Cell] = set()
            while queue:
                current_row, current_column = queue.popleft()
                cells.add((current_row, current_column))
                for dr, dc in directions:
                    nr, nc = current_row + dr, current_column + dc
                    if not (0 <= nr < height and 0 <= nc < width) or (nr, nc) in seen:
                        continue
                    if grid[nr][nc] == background:
                        continue
                    if monochrome and grid[nr][nc] != color:
                        continue
                    seen.add((nr, nc))
                    queue.append((nr, nc))
            result.append((color, frozenset(cells)))
    result.sort(key=lambda item: (min(item[1]), item[0], len(item[1])))
    return tuple(result)


def _bbox(cells: Sequence[Cell] | set[Cell] | frozenset[Cell]) -> tuple[int, int, int, int]:
    if not cells:
        raise Undefined("empty support")
    return (
        min(row for row, _ in cells),
        max(row for row, _ in cells),
        min(column for _, column in cells),
        max(column for _, column in cells),
    )


def _paint_only(output: list[list[int]], source: Grid, cells: Sequence[tuple[int, int, int]]) -> int:
    height, width = _shape(source)
    painted = 0
    for row, column, color in cells:
        if not 0 <= row < height or not 0 <= column < width:
            continue
        if source[row][column] == _background(source):
            if output[row][column] not in (source[row][column], color):
                raise Undefined("paint layers conflict")
            if output[row][column] != color:
                output[row][column] = color
                painted += 1
        elif source[row][column] != color:
            raise Undefined("construction collides with an input object")
    return painted


def _concentric_square_contours(grid: Grid) -> tuple[Grid, dict[str, Any]]:
    background = _background(grid)
    supports = _supports(grid, background)
    if len(supports) != 1:
        raise Undefined("concentric-square seeds need one paint color")
    color, raw_points = next(iter(supports.items()))
    points = tuple(sorted(raw_points))
    if len(points) != 3:
        raise Undefined("concentric-square seeds need three points")
    centers: list[tuple[Cell, Cell, Cell]] = []
    for middle in points:
        ends = [point for point in points if point != middle]
        if ends[0][0] + ends[1][0] == 2 * middle[0] and ends[0][1] + ends[1][1] == 2 * middle[1]:
            centers.append((middle, ends[0], ends[1]))
    if len(centers) != 1:
        raise Undefined("three points have no unique midpoint")
    center, left, _ = centers[0]
    step_row, step_column = abs(left[0] - center[0]), abs(left[1] - center[1])
    if step_row == 0 or step_row != step_column:
        raise Undefined("seed spacing is not diagonal")
    height, width = _shape(grid)
    output = _plain(grid)
    painted = 0
    maximum = max(center[0], height - 1 - center[0], center[1], width - 1 - center[1])
    for radius in range(0, maximum + step_row + 1, step_row):
        for row in range(height):
            for column in range(width):
                if max(abs(row - center[0]), abs(column - center[1])) != radius:
                    continue
                if grid[row][column] == background and output[row][column] == background:
                    output[row][column] = color
                    painted += 1
    if not painted:
        raise Undefined("concentric contours add nothing")
    return _freeze(output), {"center": list(center), "spacing": step_row, "painted": painted}


def _full_cross(grid: Grid) -> tuple[int, int, int]:
    background = _background(grid)
    height, width = _shape(grid)
    rows = [(row, grid[row][0]) for row in range(height) if len(set(grid[row])) == 1 and grid[row][0] != background]
    columns = []
    for column in range(width):
        values = {grid[row][column] for row in range(height)}
        if len(values) == 1 and next(iter(values)) != background:
            columns.append((column, next(iter(values))))
    matches = [(row, column, color) for row, color in rows for column, other in columns if color == other]
    if len(matches) != 1:
        raise Undefined("a unique full cross is absent")
    return matches[0]


def _cross_chebyshev_lattice(program: Mapping[str, Any], grid: Grid) -> tuple[Grid, dict[str, Any]]:
    axis_row, axis_column, _ = _full_cross(grid)
    background = _background(grid)
    period = program.get("period")
    residue = program.get("residue")
    paint = program.get("paint")
    if (
        isinstance(period, bool)
        or not isinstance(period, int)
        or not 2 <= period <= 12
        or isinstance(residue, bool)
        or not isinstance(residue, int)
        or not 0 <= residue < period
        or isinstance(paint, bool)
        or not isinstance(paint, int)
        or not 0 <= paint <= 9
        or paint == background
    ):
        raise Undefined("invalid lattice parameters")
    output = _plain(grid)
    painted = 0
    height, width = _shape(grid)
    for row in range(height):
        for column in range(width):
            radius = max(abs(row - axis_row), abs(column - axis_column))
            if radius and radius % period == residue and grid[row][column] == background:
                output[row][column] = paint
                painted += 1
    if not painted:
        raise Undefined("cross lattice adds nothing")
    return _freeze(output), {
        "center": [axis_row, axis_column],
        "period": period,
        "residue": residue,
        "painted": painted,
    }


def _corner_stamp_network(program: Mapping[str, Any], grid: Grid) -> tuple[Grid, dict[str, Any]]:
    background = _background(grid)
    support = [(row, column, grid[row][column]) for row, values in enumerate(grid) for column, value in enumerate(values) if value != background]
    if len(support) != 4:
        raise Undefined("corner network needs exactly four markers")
    points = {(row, column): color for row, column, color in support}
    r0, r1, c0, c1 = _bbox(frozenset(points))
    corners = {(r0, c0), (r0, c1), (r1, c0), (r1, c1)}
    if set(points) != corners or r1 - r0 < 4 or c1 - c0 < 4:
        raise Undefined("markers are not a nondegenerate rectangle")
    counts = Counter(points.values())
    if len(counts) != 2 or set(counts.values()) != {2}:
        raise Undefined("corner colors do not form opposite pairs")
    if points[(r0, c0)] != points[(r1, c1)] or points[(r0, c1)] != points[(r1, c0)]:
        raise Undefined("equal corner colors must be diagonal")
    connector = program.get("connector")
    if isinstance(connector, bool) or not isinstance(connector, int) or not 0 <= connector <= 9:
        raise Undefined("invalid connector color")
    colors = sorted(counts)
    opposite = {colors[0]: colors[1], colors[1]: colors[0]}
    output = _plain(grid)
    painted = 0
    for (row, column), marker in points.items():
        for nr in range(row - 1, row + 2):
            for nc in range(column - 1, column + 2):
                if not (0 <= nr < len(grid) and 0 <= nc < len(grid[0])):
                    raise Undefined("corner stamp is clipped")
                if grid[nr][nc] == background:
                    output[nr][nc] = opposite[marker]
                    painted += 1
    for row in (r0, r1):
        for column in range(c0 + 2, c1 - 1, 2):
            if 2 * column < c0 + c1 and grid[row][column] == background:
                output[row][column] = connector
                painted += 1
        for column in range(c1 - 2, c0 + 1, -2):
            if 2 * column > c0 + c1 and grid[row][column] == background:
                output[row][column] = connector
                painted += 1
        if (c1 - c0) % 4 == 0:
            midpoint = (c0 + c1) // 2
            if grid[row][midpoint] == background:
                output[row][midpoint] = connector
                painted += 1
    for column in (c0, c1):
        for row in range(r0 + 2, r1 - 1, 2):
            if 2 * row < r0 + r1 and grid[row][column] == background:
                output[row][column] = connector
                painted += 1
        for row in range(r1 - 2, r0 + 1, -2):
            if 2 * row > r0 + r1 and grid[row][column] == background:
                output[row][column] = connector
                painted += 1
        if (r1 - r0) % 4 == 0:
            midpoint = (r0 + r1) // 2
            if grid[midpoint][column] == background:
                output[midpoint][column] = connector
                painted += 1
    if not painted:
        raise Undefined("corner network adds nothing")
    return _freeze(output), {"rectangle": [r0, r1, c0, c1], "painted": painted}


def _five_point_frame(program: Mapping[str, Any], grid: Grid) -> tuple[Grid, dict[str, Any]]:
    background = _background(grid)
    points = [(row, column, grid[row][column]) for row, values in enumerate(grid) for column, value in enumerate(values) if value != background]
    if len(points) != 5:
        raise Undefined("keyed frame needs five singleton anchors")
    if any(
        any(
            (nr, nc) != (row, column)
            and 0 <= nr < len(grid)
            and 0 <= nc < len(grid[0])
            and grid[nr][nc] != background
            for nr in range(row - 1, row + 2)
            for nc in range(column - 1, column + 2)
        )
        for row, column, _ in points
    ):
        raise Undefined("frame anchors must be isolated")
    min_row = min(row for row, _, _ in points)
    max_row = max(row for row, _, _ in points)
    min_column = min(column for _, column, _ in points)
    max_column = max(column for _, column, _ in points)
    top = [point for point in points if point[0] == min_row]
    bottom = [point for point in points if point[0] == max_row]
    left = [point for point in points if point[1] == min_column]
    right = [point for point in points if point[1] == max_column]
    if not all(len(group) == 1 for group in (top, bottom, left, right)):
        raise Undefined("directional frame anchors are ambiguous")
    outer = {top[0], bottom[0], left[0], right[0]}
    if len(outer) != 4:
        raise Undefined("one anchor occupies multiple frame roles")
    center = [point for point in points if point not in outer]
    if len(center) != 1:
        raise Undefined("frame center is ambiguous")
    center_row, center_column, center_color = center[0]
    if not (min_row < center_row < max_row and min_column < center_column < max_column):
        raise Undefined("frame center is not interior")
    cross_color = program.get("cross_color")
    if isinstance(cross_color, bool) or not isinstance(cross_color, int) or not 0 <= cross_color <= 9:
        raise Undefined("invalid cross paint")
    output = _plain(grid)
    for row in range(min_row + 1, max_row):
        if grid[row][center_column] == background:
            output[row][center_column] = cross_color
    for column in range(min_column + 1, max_column):
        if grid[center_row][column] == background:
            output[center_row][column] = cross_color
    for column in range(min_column, max_column + 1):
        output[min_row][column] = top[0][2]
        output[max_row][column] = bottom[0][2]
    for row in range(min_row + 1, max_row):
        output[row][min_column] = left[0][2]
        output[row][max_column] = right[0][2]
    output[center_row][center_column] = center_color
    result = _freeze(output)
    if result == grid:
        raise Undefined("keyed frame adds nothing")
    return result, {"rectangle": [min_row, max_row, min_column, max_column], "center": [center_row, center_column]}


def _separator_ray_field(program: Mapping[str, Any], grid: Grid) -> tuple[Grid, dict[str, Any]]:
    background = _background(grid)
    height, width = _shape(grid)
    horizontal = [(row, grid[row][0]) for row in range(height) if len(set(grid[row])) == 1 and grid[row][0] != background]
    vertical: list[tuple[int, int]] = []
    for column in range(width):
        values = {grid[row][column] for row in range(height)}
        if len(values) == 1 and next(iter(values)) != background:
            vertical.append((column, next(iter(values))))
    axes: list[tuple[str, int, int]] = [("horizontal", row, color) for row, color in horizontal] + [("vertical", column, color) for column, color in vertical]
    if len(axes) != 1:
        raise Undefined("a unique separator line is absent")
    orientation, axis, scaffold = axes[0]
    toward = program.get("toward_color")
    away = program.get("away_color")
    if (
        isinstance(toward, bool)
        or not isinstance(toward, int)
        or isinstance(away, bool)
        or not isinstance(away, int)
        or toward == away
    ):
        raise Undefined("invalid ray palette")
    colors = set(_supports(grid, background)) - {scaffold}
    if colors != {toward, away}:
        raise Undefined("separator field has an unexpected palette")
    output = _plain(grid)
    painted = 0
    for row in range(height):
        for column in range(width):
            color = grid[row][column]
            if color not in (toward, away):
                continue
            if orientation == "horizontal":
                step = 1 if row < axis else -1
                if color == away:
                    step = -step
                current = row + step
                stop = axis if color == toward else (-1 if step < 0 else height)
                while current != stop:
                    if grid[current][column] != background:
                        break
                    if output[current][column] == background:
                        output[current][column] = color
                        painted += 1
                    current += step
            else:
                step = 1 if column < axis else -1
                if color == away:
                    step = -step
                current = column + step
                stop = axis if color == toward else (-1 if step < 0 else width)
                while current != stop:
                    if grid[row][current] != background:
                        break
                    if output[row][current] == background:
                        output[row][current] = color
                        painted += 1
                    current += step
    if not painted:
        raise Undefined("separator rays add nothing")
    return _freeze(output), {"orientation": orientation, "axis": axis, "painted": painted}


def _scaled_stamp_staircase(program: Mapping[str, Any], grid: Grid) -> tuple[Grid, dict[str, Any]]:
    background = _background(grid)
    points = {(row, column) for row, values in enumerate(grid) for column, value in enumerate(values) if value != background}
    if len(points) != 4:
        raise Undefined("scaled staircase needs a two-by-two seed")
    r0, r1, c0, c1 = _bbox(frozenset(points))
    if (r1 - r0, c1 - c0) != (1, 1) or points != {(r0, c0), (r0, c1), (r1, c0), (r1, c1)}:
        raise Undefined("scaled staircase seed is not solid two-by-two")
    vertical = program.get("vertical")
    horizontal = program.get("horizontal")
    if vertical not in (-1, 1) or horizontal not in (-1, 1):
        raise Undefined("invalid staircase direction")
    seed = ((grid[r0][c0], grid[r0][c1]), (grid[r1][c0], grid[r1][c1]))
    height, width = _shape(grid)
    output = _plain(grid)
    scale = 2
    copies = 0
    while scale <= 16:
        top = r0 + vertical * (scale - 1)
        left = c0 + (2 * (scale - 1) if horizontal > 0 else -2 * (scale - 1))
        if vertical > 0:
            top = r0 + 2 - 1
        if horizontal < 0:
            left = c0 - 2 * scale + 2
        block_height = block_width = 2 * scale
        if not (0 <= top and top + block_height <= height and 0 <= left and left + block_width <= width):
            break
        for seed_row in range(2):
            for seed_column in range(2):
                color = seed[seed_row][seed_column]
                for dr in range(scale):
                    for dc in range(scale):
                        row = top + seed_row * scale + dr
                        column = left + seed_column * scale + dc
                        if grid[row][column] != background and grid[row][column] != color:
                            raise Undefined("scaled stamp collides")
                        output[row][column] = color
        copies += 1
        scale *= 2
    result = _freeze(output)
    if not copies or result == grid:
        raise Undefined("scaled staircase adds nothing")
    return result, {"copies": copies, "direction": [vertical, horizontal]}


def _boundary_run_code(program: Mapping[str, Any], grid: Grid) -> tuple[Grid, dict[str, Any]]:
    background = _background(grid)
    side = program.get("side")
    raw_mapping = program.get("mapping")
    if side not in {"top", "bottom", "left", "right"} or not isinstance(raw_mapping, list):
        raise Undefined("invalid boundary-code program")
    mapping: dict[int, int] = {}
    for item in raw_mapping:
        if (
            not isinstance(item, list)
            or len(item) != 2
            or isinstance(item[0], bool)
            or not isinstance(item[0], int)
            or item[0] < 1
            or isinstance(item[1], bool)
            or not isinstance(item[1], int)
            or not 0 <= item[1] <= 9
            or item[0] in mapping
        ):
            raise Undefined("invalid boundary-code mapping")
        mapping[item[0]] = item[1]
    height, width = _shape(grid)
    if side == "top":
        boundary = [(0, column) for column in range(width)]
    elif side == "bottom":
        boundary = [(height - 1, column) for column in range(width)]
    elif side == "left":
        boundary = [(row, 0) for row in range(height)]
    else:
        boundary = [(row, width - 1) for row in range(height)]
    anchors = [point for point in boundary if grid[point[0]][point[1]] != background]
    if len(anchors) != 1:
        raise Undefined("boundary code needs one boundary marker")
    anchor = anchors[0]
    anchor_color = grid[anchor[0]][anchor[1]]
    components = _components(grid, background, connectivity=4, monochrome=True)
    runs: list[tuple[int, int, int]] = []
    for color, cells in components:
        if cells == frozenset({anchor}):
            continue
        if anchor in cells or len(cells) < 2:
            raise Undefined("boundary payload contains a non-run object")
        rows = {row for row, _ in cells}
        columns = {column for _, column in cells}
        if side in {"top", "bottom"}:
            if len(rows) != 1 or len(cells) != max(columns) - min(columns) + 1:
                raise Undefined("boundary payload is not horizontal")
            coordinate = next(iter(rows))
            runs.append((coordinate, anchor[1], len(cells)))
        else:
            if len(columns) != 1 or len(cells) != max(rows) - min(rows) + 1:
                raise Undefined("boundary payload is not vertical")
            coordinate = next(iter(columns))
            runs.append((anchor[0], coordinate, len(cells)))
        if color == anchor_color and anchor in cells:
            raise Undefined("boundary marker merged with a payload")
    if not runs:
        raise Undefined("boundary code has no payload runs")
    output = _plain(grid)
    painted = 0
    for row, column, length in runs:
        if length not in mapping:
            raise Undefined("unseen run length")
        if grid[row][column] != background:
            raise Undefined("code column collides with a payload")
        output[row][column] = mapping[length]
        painted += 1
    if not painted:
        raise Undefined("boundary code adds nothing")
    return _freeze(output), {"side": side, "run_count": len(runs), "marker_color": anchor_color}


def _line_components_for_color(grid: Grid, color: int) -> tuple[tuple[str, int, int, int], ...]:
    background = _background(grid)
    result: list[tuple[str, int, int, int]] = []
    for component_color, cells in _components(grid, background, connectivity=4, monochrome=True):
        if component_color != color or len(cells) < 3:
            continue
        rows = {row for row, _ in cells}
        columns = {column for _, column in cells}
        if len(columns) == 1 and len(cells) == max(rows) - min(rows) + 1:
            result.append(("vertical", next(iter(columns)), min(rows), max(rows)))
        elif len(rows) == 1 and len(cells) == max(columns) - min(columns) + 1:
            result.append(("horizontal", next(iter(rows)), min(columns), max(columns)))
    return tuple(sorted(result))


def _reflect_shapes_to_markers(program: Mapping[str, Any], grid: Grid) -> tuple[Grid, dict[str, Any]]:
    background = _background(grid)
    axis_color = program.get("axis_color")
    template_color = program.get("template_color")
    if (
        isinstance(axis_color, bool)
        or not isinstance(axis_color, int)
        or isinstance(template_color, bool)
        or not isinstance(template_color, int)
        or axis_color == template_color
    ):
        raise Undefined("invalid reflected-stamp palette")
    axes = _line_components_for_color(grid, axis_color)
    if not axes:
        raise Undefined("reflected stamps need separator segments")
    templates = [cells for color, cells in _components(grid, background, connectivity=8, monochrome=True) if color == template_color]
    if len(templates) != len(axes):
        raise Undefined("separator/template arity differs")
    support_by_color = _supports(grid, background)
    marker_colors = set(support_by_color) - {axis_color, template_color}
    output = _plain(grid)
    assignments: list[tuple[int, int]] = []
    used_templates: set[int] = set()
    painted = 0
    for axis_index, (orientation, coordinate, low, high) in enumerate(axes):
        matches: list[tuple[int, frozenset[Cell], int]] = []
        for template_index, cells in enumerate(templates):
            if template_index in used_templates:
                continue
            if orientation == "vertical":
                if not all(low <= row <= high for row, _ in cells):
                    continue
                sides = {column < coordinate for _, column in cells}
                if len(sides) != 1 or any(column == coordinate for _, column in cells):
                    continue
                reflected = frozenset((row, 2 * coordinate - column) for row, column in cells)
            else:
                if not all(low <= column <= high for _, column in cells):
                    continue
                sides = {row < coordinate for row, _ in cells}
                if len(sides) != 1 or any(row == coordinate for row, _ in cells):
                    continue
                reflected = frozenset((2 * coordinate - row, column) for row, column in cells)
            height, width = _shape(grid)
            if not all(0 <= row < height and 0 <= column < width for row, column in reflected):
                continue
            colors = {
                color
                for color in marker_colors
                if support_by_color[color] & reflected
            }
            if len(colors) != 1:
                continue
            marker_color = next(iter(colors))
            if len(support_by_color[marker_color] & reflected) != 1:
                continue
            if any(
                grid[row][column] not in (background, marker_color)
                for row, column in reflected
            ):
                continue
            matches.append((template_index, reflected, marker_color))
        if len(matches) != 1:
            raise Undefined("reflected target is ambiguous")
        template_index, reflected, marker_color = matches[0]
        used_templates.add(template_index)
        assignments.append((axis_index, marker_color))
        for row, column in reflected:
            if grid[row][column] == background:
                output[row][column] = marker_color
                painted += 1
    if len(used_templates) != len(templates) or not painted:
        raise Undefined("reflected stamp construction is incomplete")
    return _freeze(output), {"stamp_count": len(assignments), "painted": painted}


def _component_axis_closure(grid: Grid) -> tuple[Grid, dict[str, Any]]:
    background = _background(grid)
    groups = sorted(_supports(grid, background).items())
    if len(groups) < 2 or len({color for color, _ in groups}) < 2:
        raise Undefined("axis closure needs multiple colored objects")
    output = _plain(grid)
    additions: dict[Cell, int] = {}
    for color, cells in groups:
        if len(cells) < 2:
            raise Undefined("axis closure rejects singleton noise")
        r0, r1, c0, c1 = _bbox(cells)
        if r1 - r0 + 1 > 9 or c1 - c0 + 1 > 9:
            raise Undefined("axis-closure object is too large")
        candidates: set[frozenset[Cell]] = set()
        row_axes = range(max(0, 2 * r0 - 2), min(2 * len(grid) - 1, 2 * r1 + 3))
        column_axes = range(max(0, 2 * c0 - 2), min(2 * len(grid[0]) - 1, 2 * c1 + 3))
        for row_axis, column_axis in itertools.product(row_axes, column_axes):
            closure = set(cells)
            for row, column in cells:
                reflected_row = row_axis - row
                reflected_column = column_axis - column
                closure.add((reflected_row, column))
                closure.add((row, reflected_column))
                closure.add((reflected_row, reflected_column))
            if closure == set(cells):
                continue
            if not all(0 <= row < len(grid) and 0 <= column < len(grid[0]) for row, column in closure):
                continue
            if any(grid[row][column] not in (background, color) for row, column in closure):
                continue
            candidates.add(frozenset(closure))
        if not candidates:
            raise Undefined("object has no nontrivial axis closure")
        minimum = min(len(candidate - cells) for candidate in candidates)
        winners = {candidate for candidate in candidates if len(candidate - cells) == minimum}
        if len(winners) != 1:
            raise Undefined("minimum object closure is ambiguous")
        closure = next(iter(winners))
        for point in closure - cells:
            row, column = point
            if grid[row][column] != background:
                raise Undefined("axis closure collides with another object")
            if point in additions and additions[point] != color:
                raise Undefined("axis closures overlap")
            additions[point] = color
    if not additions:
        raise Undefined("axis closure is vacuous")
    for (row, column), color in additions.items():
        output[row][column] = color
    return _freeze(output), {"object_count": len(groups), "painted": len(additions)}


def _paired_marker_brackets(grid: Grid) -> tuple[Grid, dict[str, Any]]:
    background = _background(grid)
    markers = [(row, column, grid[row][column]) for row, values in enumerate(grid) for column, value in enumerate(values) if value != background]
    if len(markers) != 2 or markers[0][2] == markers[1][2]:
        raise Undefined("paired brackets need two differently colored markers")
    (r0, c0, color0), (r1, c1, color1) = markers
    output = _plain(grid)
    painted = 0
    if r0 == r1:
        if c0 > c1:
            c0, c1, color0, color1 = c1, c0, color1, color0
        distance = c1 - c0
        arm = (distance - 3) // 2
        if distance < 7 or arm < 2 or r0 < 2 or r0 + 2 >= len(grid):
            raise Undefined("horizontal bracket geometry is clipped")
        left_inner, right_inner = c0 + arm, c1 - arm
        if right_inner - left_inner != 3:
            raise Undefined("markers do not admit a centered bracket gap")
        cells: list[tuple[int, int, int]] = []
        cells.extend((r0, column, color0) for column in range(c0, left_inner + 1))
        cells.extend((r0, column, color1) for column in range(right_inner, c1 + 1))
        cells.extend((row, left_inner, color0) for row in range(r0 - 2, r0 + 3))
        cells.extend((row, right_inner, color1) for row in range(r0 - 2, r0 + 3))
        cells.extend((row, left_inner + 1, color0) for row in (r0 - 2, r0 + 2))
        cells.extend((row, right_inner - 1, color1) for row in (r0 - 2, r0 + 2))
    elif c0 == c1:
        if r0 > r1:
            r0, r1, color0, color1 = r1, r0, color1, color0
        distance = r1 - r0
        arm = (distance - 3) // 2
        if distance < 7 or arm < 2 or c0 < 2 or c0 + 2 >= len(grid[0]):
            raise Undefined("vertical bracket geometry is clipped")
        top_inner, bottom_inner = r0 + arm, r1 - arm
        if bottom_inner - top_inner != 3:
            raise Undefined("markers do not admit a centered bracket gap")
        cells = []
        cells.extend((row, c0, color0) for row in range(r0, top_inner + 1))
        cells.extend((row, c0, color1) for row in range(bottom_inner, r1 + 1))
        cells.extend((top_inner, column, color0) for column in range(c0 - 2, c0 + 3))
        cells.extend((bottom_inner, column, color1) for column in range(c0 - 2, c0 + 3))
        cells.extend((top_inner + 1, column, color0) for column in (c0 - 2, c0 + 2))
        cells.extend((bottom_inner - 1, column, color1) for column in (c0 - 2, c0 + 2))
    else:
        raise Undefined("paired markers are not axis-aligned")
    for row, column, color in cells:
        if grid[row][column] == background:
            if output[row][column] not in (background, color):
                raise Undefined("paired bracket paint conflicts")
            output[row][column] = color
            painted += 1
        elif grid[row][column] != color:
            raise Undefined("paired bracket collides with a marker")
    if not painted:
        raise Undefined("paired brackets add nothing")
    return _freeze(output), {"painted": painted, "orientation": "horizontal" if r0 == r1 else "vertical"}


def _legend_stamp_sequence(grid: Grid) -> tuple[Grid, dict[str, Any]]:
    background = _background(grid)
    components = _components(grid, background, connectivity=8, monochrome=True)
    templates = [(color, cells) for color, cells in components if len(cells) > 1]
    singletons = [(color, next(iter(cells))) for color, cells in components if len(cells) == 1]
    if len(templates) != 1 or len(singletons) < 3 or len(components) != len(singletons) + 1:
        raise Undefined("stamp sequence needs one template and an aligned legend")
    template_color, template = templates[0]
    legend_rows = {point[0] for _, point in singletons}
    legend_columns = {point[1] for _, point in singletons}
    if len(legend_rows) == 1:
        orientation = "horizontal"
        ordered = sorted(singletons, key=lambda item: item[1][1])
        coordinates = [point[1] for _, point in ordered]
    elif len(legend_columns) == 1:
        orientation = "vertical"
        ordered = sorted(singletons, key=lambda item: item[1][0])
        coordinates = [point[0] for _, point in ordered]
    else:
        raise Undefined("legend markers are not collinear")
    references = [index for index, (color, _) in enumerate(ordered) if color == template_color]
    if len(references) != 1:
        raise Undefined("template color has no unique legend key")
    reference_index = references[0]
    reference_coordinate = coordinates[reference_index]
    r0, r1, c0, c1 = _bbox(template)
    template_center = (c0 + c1) // 2 if orientation == "horizontal" else (r0 + r1) // 2
    extent = c1 - c0 + 1 if orientation == "horizontal" else r1 - r0 + 1
    if extent < 2:
        raise Undefined("template has no extent along the legend")
    output = _plain(grid)
    height, width = _shape(grid)
    painted = 0
    for index, (color, _) in enumerate(ordered):
        offset_rank = index - reference_index
        center = coordinates[index] - reference_coordinate + template_center + (extent - 1) * offset_rank
        delta_row = center - template_center if orientation == "vertical" else 0
        delta_column = center - template_center if orientation == "horizontal" else 0
        translated = {(row + delta_row, column + delta_column) for row, column in template}
        if not all(0 <= row < height and 0 <= column < width for row, column in translated):
            raise Undefined("stamp sequence is clipped")
        for row, column in translated:
            if grid[row][column] not in (background, color, template_color):
                raise Undefined("stamp sequence collides")
            if color != template_color and grid[row][column] == background:
                output[row][column] = color
                painted += 1
    if not painted:
        raise Undefined("stamp sequence adds nothing")
    return _freeze(output), {"orientation": orientation, "stamp_count": len(ordered), "painted": painted}


def _plus_center_line_field(grid: Grid) -> tuple[Grid, dict[str, Any]]:
    background = _background(grid)
    height, width = _shape(grid)
    motifs: list[tuple[int, int, int, int, frozenset[Cell]]] = []
    scaffold_colors: set[int] = set()
    for row in range(1, height - 1):
        for column in range(1, width - 1):
            arms = frozenset(
                {
                    (row - 1, column),
                    (row + 1, column),
                    (row, column - 1),
                    (row, column + 1),
                }
            )
            arm_colors = {grid[nr][nc] for nr, nc in arms}
            if len(arm_colors) != 1 or background in arm_colors:
                continue
            scaffold = next(iter(arm_colors))
            center_color = grid[row][column]
            if center_color == scaffold:
                continue
            scaffold_colors.add(scaffold)
            motifs.append((row, column, center_color, scaffold, arms | {(row, column)}))
    if not 2 <= len(motifs) <= 12 or len(scaffold_colors) != 1:
        raise Undefined("plus motifs do not share a scaffold color")
    foreground = {
        (row, column)
        for row in range(height)
        for column in range(width)
        if grid[row][column] != background
    }
    covered = {
        point
        for _, _, _, _, motif_cells in motifs
        for point in motif_cells
        if grid[point[0]][point[1]] != background
    }
    if covered != foreground:
        raise Undefined("plus motifs do not cover the input scene")
    center_colors = [color for _, _, color, _, _ in motifs]
    if len(center_colors) != len(set(center_colors)) or all(
        color == background for color in center_colors
    ):
        raise Undefined("plus field has no colored centers")
    output = _plain(grid)

    def bounds(
        row: int, column: int, own: frozenset[Cell], dr: int, dc: int
    ) -> Cell:
        nr, nc = row + dr, column + dc
        while 0 <= nr < height and 0 <= nc < width:
            if grid[nr][nc] != background and (nr, nc) not in own:
                return nr - dr, nc - dc
            nr += dr
            nc += dc
        return nr - dr, nc - dc

    # Horizontal fields compose first; vertical fields are the final overlay.
    for row, column, color, _, own in motifs:
        left = bounds(row, column, own, 0, -1)[1]
        right = bounds(row, column, own, 0, 1)[1]
        for nc in range(left, right + 1):
            if grid[row][nc] == background:
                output[row][nc] = color
    for row, column, color, _, own in motifs:
        top = bounds(row, column, own, -1, 0)[0]
        bottom = bounds(row, column, own, 1, 0)[0]
        for nr in range(top, bottom + 1):
            if grid[nr][column] == background:
                output[nr][column] = color
    result = _freeze(output)
    if result == grid:
        raise Undefined("plus-line field adds nothing")
    return result, {
        "motif_count": len(motifs),
        "colored_centers": sum(color != background for color in center_colors),
    }


def _frame_seed_chebyshev_fill(
    program: Mapping[str, Any], grid: Grid
) -> tuple[Grid, dict[str, Any]]:
    """Fill a framed canvas with alternating square-distance contours."""

    background = _background(grid)
    supports = _supports(grid, background)
    if len(supports) != 1:
        raise Undefined("contour fill needs one scaffold color")
    frame_color, cells = next(iter(supports.items()))
    r0, r1, c0, c1 = _bbox(cells)
    if r1 - r0 < 4 or c1 - c0 < 4:
        raise Undefined("contour frame is too small")
    perimeter = {
        (row, column)
        for row in range(r0, r1 + 1)
        for column in range(c0, c1 + 1)
        if row in (r0, r1) or column in (c0, c1)
    }
    seeds = cells - perimeter
    if not perimeter <= cells or len(seeds) != 1 or cells != perimeter | seeds:
        raise Undefined("a closed frame and one interior seed are required")
    seed_row, seed_column = next(iter(seeds))
    if not (r0 < seed_row < r1 and c0 < seed_column < c1):
        raise Undefined("contour seed is not interior")
    odd_color = program.get("odd_color")
    even_color = program.get("even_color")
    if (
        isinstance(odd_color, bool)
        or not isinstance(odd_color, int)
        or isinstance(even_color, bool)
        or not isinstance(even_color, int)
        or odd_color == even_color
        or frame_color in (odd_color, even_color)
        or background in (odd_color, even_color)
    ):
        raise Undefined("invalid contour palette")
    output = _plain(grid)
    painted = 0
    for row in range(r0 + 1, r1):
        for column in range(c0 + 1, c1):
            if (row, column) == (seed_row, seed_column):
                continue
            if grid[row][column] != background:
                raise Undefined("contour interior contains noise")
            radius = max(abs(row - seed_row), abs(column - seed_column))
            output[row][column] = odd_color if radius % 2 else even_color
            painted += 1
    if not painted:
        raise Undefined("contour fill adds nothing")
    return _freeze(output), {
        "frame": [r0, r1, c0, c1],
        "seed": [seed_row, seed_column],
        "painted": painted,
    }


def _marked_rectangle_extrusions(grid: Grid) -> tuple[Grid, dict[str, Any]]:
    """Extend a marked edge of each solid rectangle to the canvas boundary."""

    background = _background(grid)
    components = _components(grid, background, connectivity=4, monochrome=False)
    if not 2 <= len(components) <= 8:
        raise Undefined("rectangle extrusion needs several components")
    output = _plain(grid)
    palettes: set[tuple[int, int]] = set()
    strokes: list[tuple[int, int, int]] = []
    height, width = _shape(grid)
    for _, cells in components:
        r0, r1, c0, c1 = _bbox(cells)
        rectangle = {
            (row, column)
            for row in range(r0, r1 + 1)
            for column in range(c0, c1 + 1)
        }
        if set(cells) != rectangle or min(r1 - r0, c1 - c0) < 1:
            raise Undefined("payload is not a solid rectangle")
        counts = Counter(grid[row][column] for row, column in cells)
        if len(counts) != 2 or sorted(counts.values())[0] != 1:
            raise Undefined("rectangle lacks a unique edge marker")
        marker_color = min(counts, key=counts.get)
        body_color = max(counts, key=counts.get)
        marker = next(
            (point for point in cells if grid[point[0]][point[1]] == marker_color),
            None,
        )
        if marker is None:
            raise Undefined("edge marker is absent")
        row, column = marker
        sides = []
        if row == r0:
            sides.append("top")
        if row == r1:
            sides.append("bottom")
        if column == c0:
            sides.append("left")
        if column == c1:
            sides.append("right")
        if len(sides) != 1:
            raise Undefined("marker must lie on exactly one rectangle edge")
        palettes.add((body_color, marker_color))
        side = sides[0]
        if side in {"top", "bottom"}:
            half_width = r1 - r0
            if not (0 <= column - half_width and column + half_width < width):
                raise Undefined("horizontal-edge stroke is clipped sideways")
            rows = range(0, r0) if side == "top" else range(r1 + 1, height)
            for nr in rows:
                for nc in range(column - half_width, column + half_width + 1):
                    strokes.append((nr, nc, marker_color if nc == column else body_color))
        else:
            half_width = c1 - c0
            if not (0 <= row - half_width and row + half_width < height):
                raise Undefined("vertical-edge stroke is clipped sideways")
            columns = range(0, c0) if side == "left" else range(c1 + 1, width)
            for nr in range(row - half_width, row + half_width + 1):
                for nc in columns:
                    strokes.append((nr, nc, marker_color if nr == row else body_color))
    if len(palettes) != 1 or not strokes:
        raise Undefined("rectangle stroke palettes disagree")
    painted = 0
    for row, column, color in strokes:
        if grid[row][column] != background:
            raise Undefined("rectangle extrusion collides with input")
        if output[row][column] not in (background, color):
            raise Undefined("rectangle extrusions conflict")
        if output[row][column] == background:
            output[row][column] = color
            painted += 1
    if not painted:
        raise Undefined("rectangle extrusion adds nothing")
    return _freeze(output), {"rectangle_count": len(components), "painted": painted}


def _aligned_rectangle_corridors(
    program: Mapping[str, Any], grid: Grid
) -> tuple[Grid, dict[str, Any]]:
    """Join separated, aligned rectangles through their inset overlap."""

    background = _background(grid)
    paint = program.get("paint")
    if (
        isinstance(paint, bool)
        or not isinstance(paint, int)
        or not 0 <= paint <= 9
        or paint == background
        or paint in _supports(grid, background)
    ):
        raise Undefined("invalid corridor paint")
    components = _components(grid, background, connectivity=4, monochrome=True)
    if not 3 <= len(components) <= 12:
        raise Undefined("corridors need several rectangles")
    rectangles: list[tuple[int, int, int, int, int]] = []
    for color, cells in components:
        r0, r1, c0, c1 = _bbox(cells)
        if len(cells) != (r1 - r0 + 1) * (c1 - c0 + 1) or min(r1 - r0, c1 - c0) < 1:
            raise Undefined("corridor payload is not a solid rectangle")
        rectangles.append((color, r0, r1, c0, c1))
    additions: set[Cell] = set()
    for first, second in itertools.combinations(rectangles, 2):
        color0, ar0, ar1, ac0, ac1 = first
        color1, br0, br1, bc0, bc1 = second
        if color0 != color1:
            continue
        if ac1 < bc0 or bc1 < ac0:
            left, right = (first, second) if ac1 < bc0 else (second, first)
            _, lr0, lr1, lc0, lc1 = left
            _, rr0, rr1, rc0, rc1 = right
            low, high = max(lr0, rr0) + 1, min(lr1, rr1) - 1
            if low <= high:
                corridor = {
                    (row, column)
                    for row in range(low, high + 1)
                    for column in range(lc1 + 1, rc0)
                }
                if corridor and all(grid[row][column] == background for row, column in corridor):
                    additions.update(corridor)
        if ar1 < br0 or br1 < ar0:
            top, bottom = (first, second) if ar1 < br0 else (second, first)
            _, tr0, tr1, tc0, tc1 = top
            _, dr0, dr1, dc0, dc1 = bottom
            low, high = max(tc0, dc0) + 1, min(tc1, dc1) - 1
            if low <= high:
                corridor = {
                    (row, column)
                    for row in range(tr1 + 1, dr0)
                    for column in range(low, high + 1)
                }
                if corridor and all(grid[row][column] == background for row, column in corridor):
                    additions.update(corridor)
    if not additions:
        raise Undefined("no aligned rectangle gaps exist")
    output = _plain(grid)
    for row, column in additions:
        if grid[row][column] != background:
            raise Undefined("corridor collides with an input rectangle")
        output[row][column] = paint
    return _freeze(output), {"rectangle_count": len(rectangles), "painted": len(additions)}


def _scaffold_corner_rays(grid: Grid) -> tuple[Grid, dict[str, Any]]:
    """Continue scaffold corners diagonally away from a boxed payload."""

    background = _background(grid)
    supports = _supports(grid, background)
    if len(supports) != 2:
        raise Undefined("corner rays need one scaffold and one payload")
    all_cells = frozenset().union(*supports.values())
    r0, r1, c0, c1 = _bbox(all_cells)
    if r1 - r0 < 2 or c1 - c0 < 2:
        raise Undefined("corner-ray box is too small")
    candidates: list[tuple[int, int]] = []
    for payload_color, payload in supports.items():
        pr0, pr1, pc0, pc1 = _bbox(payload)
        if len(payload) != (pr1 - pr0 + 1) * (pc1 - pc0 + 1):
            continue
        scaffold_color = next(color for color in supports if color != payload_color)
        scaffold = supports[scaffold_color]
        if not scaffold or any(
            row not in (r0, r1) and column not in (c0, c1)
            for row, column in scaffold
        ):
            continue
        scaffold_components = _components(
            grid, background, connectivity=4, monochrome=True
        )
        matching = [cells for color, cells in scaffold_components if color == scaffold_color]
        if len(matching) != 1 or matching[0] != scaffold:
            continue
        candidates.append((scaffold_color, payload_color))
    if len(candidates) != 1:
        raise Undefined("scaffold/payload roles are ambiguous")
    scaffold_color, payload_color = candidates[0]
    output = _plain(grid)
    painted = 0
    corners = [
        (r0, c0, -1, -1),
        (r0, c1, -1, 1),
        (r1, c0, 1, -1),
        (r1, c1, 1, 1),
    ]
    for row, column, dr, dc in corners:
        if grid[row][column] != scaffold_color:
            continue
        nr, nc = row + dr, column + dc
        while 0 <= nr < len(grid) and 0 <= nc < len(grid[0]):
            if grid[nr][nc] != background:
                raise Undefined("corner ray collides outside its box")
            output[nr][nc] = payload_color
            painted += 1
            nr += dr
            nc += dc
    if not painted:
        raise Undefined("scaffold corners emit no visible ray")
    return _freeze(output), {
        "box": [r0, r1, c0, c1],
        "scaffold_color": scaffold_color,
        "payload_color": payload_color,
        "painted": painted,
    }


def _diagonal_segment(grid: Grid, color: int) -> tuple[Cell, Cell]:
    background = _background(grid)
    cells = _supports(grid, background).get(color, frozenset())
    if len(cells) < 3:
        raise Undefined("diagonal ray seed is too short")
    ordered = sorted(cells)
    if any(
        ordered[index + 1][0] - ordered[index][0] != 1
        or abs(ordered[index + 1][1] - ordered[index][1]) != 1
        for index in range(len(ordered) - 1)
    ):
        raise Undefined("ray seed is not a contiguous diagonal")
    return ordered[0], ordered[-1]


def _barrier_orientation(grid: Grid, point: Cell, color: int) -> str:
    background = _background(grid)
    matches = [
        cells
        for component_color, cells in _components(
            grid, background, connectivity=4, monochrome=True
        )
        if component_color == color and point in cells
    ]
    if len(matches) != 1 or len(matches[0]) < 3:
        raise Undefined("barrier is not a unique line")
    cells = matches[0]
    rows = {row for row, _ in cells}
    columns = {column for _, column in cells}
    if len(rows) == 1 and len(cells) == max(columns) - min(columns) + 1:
        return "horizontal"
    if len(columns) == 1 and len(cells) == max(rows) - min(rows) + 1:
        return "vertical"
    raise Undefined("barrier is not straight")


def _typed_barrier_billiard(
    program: Mapping[str, Any], grid: Grid
) -> tuple[Grid, dict[str, Any]]:
    """Continue a diagonal ray through transparent and reflecting barriers."""

    ray_color = program.get("ray_color")
    pass_colors = program.get("pass_colors")
    reflect_colors = program.get("reflect_colors")
    if (
        isinstance(ray_color, bool)
        or not isinstance(ray_color, int)
        or not isinstance(pass_colors, Sequence)
        or isinstance(pass_colors, (str, bytes))
        or not isinstance(reflect_colors, Sequence)
        or isinstance(reflect_colors, (str, bytes))
    ):
        raise Undefined("invalid billiard program")
    transparent = frozenset(pass_colors)
    reflecting = frozenset(reflect_colors)
    if (
        transparent & reflecting
        or any(isinstance(color, bool) or not isinstance(color, int) for color in transparent | reflecting)
        or ray_color in transparent | reflecting
    ):
        raise Undefined("invalid barrier partition")
    background = _background(grid)
    input_colors = set(_supports(grid, background))
    if ray_color not in input_colors or not (
        input_colors - {ray_color}
    ) <= transparent | reflecting:
        raise Undefined("billiard input palette disagrees with the program")
    first, last = _diagonal_segment(grid, ray_color)
    slope = 1 if last[1] > first[1] else -1
    extensions = [
        (first, -1, -slope),
        (last, 1, slope),
    ]
    height, width = _shape(grid)
    viable = [
        item
        for item in extensions
        if 0 <= item[0][0] + item[1] < height
        and 0 <= item[0][1] + item[2] < width
    ]
    if len(viable) != 1:
        raise Undefined("ray has no unique inward endpoint")
    (row, column), dr, dc = viable[0]
    output = _plain(grid)
    painted = 0
    crossings = 0
    reflections = 0
    states: set[tuple[int, int, int, int]] = set()
    while True:
        state = (row, column, dr, dc)
        if state in states or len(states) > 4 * height * width:
            raise Undefined("billiard path cycles")
        states.add(state)
        nr, nc = row + dr, column + dc
        if not (0 <= nr < height and 0 <= nc < width):
            break
        cell = grid[nr][nc]
        if cell == background:
            output[nr][nc] = ray_color
            painted += 1
            row, column = nr, nc
            continue
        if cell in transparent:
            output[nr][nc] = ray_color
            painted += 1
            crossings += 1
            row, column = nr, nc
            continue
        if cell in reflecting:
            orientation = _barrier_orientation(grid, (nr, nc), cell)
            if orientation == "horizontal":
                dr = -dr
            else:
                dc = -dc
            reflections += 1
            continue
        raise Undefined("ray strikes an unsupported object")
    if not painted or not (crossings or reflections):
        raise Undefined("typed barrier path is vacuous")
    return _freeze(output), {
        "painted": painted,
        "crossings": crossings,
        "reflections": reflections,
    }


def _execute_internal(
    program: Mapping[str, Any], grid: Grid, limits: Limits | None = None
) -> tuple[Grid, dict[str, Any]]:
    if not isinstance(program, Mapping) or program.get("schema") != SCHEMA:
        raise Undefined("invalid constructive-painting program")
    operator = program.get("operator")
    if operator == "concentric_square_contours":
        return _concentric_square_contours(grid)
    if operator == "cross_chebyshev_lattice":
        return _cross_chebyshev_lattice(program, grid)
    if operator == "corner_stamp_network":
        return _corner_stamp_network(program, grid)
    if operator == "five_point_frame":
        return _five_point_frame(program, grid)
    if operator == "separator_ray_field":
        return _separator_ray_field(program, grid)
    if operator == "scaled_stamp_staircase":
        return _scaled_stamp_staircase(program, grid)
    if operator == "boundary_run_code":
        return _boundary_run_code(program, grid)
    if operator == "reflect_shapes_to_markers":
        return _reflect_shapes_to_markers(program, grid)
    if operator == "component_axis_closure":
        return _component_axis_closure(grid)
    if operator == "paired_marker_brackets":
        return _paired_marker_brackets(grid)
    if operator == "legend_stamp_sequence":
        return _legend_stamp_sequence(grid)
    if operator == "plus_center_line_field":
        return _plus_center_line_field(grid)
    if operator == "frame_seed_chebyshev_fill":
        return _frame_seed_chebyshev_fill(program, grid)
    if operator == "marked_rectangle_extrusions":
        return _marked_rectangle_extrusions(grid)
    if operator == "aligned_rectangle_corridors":
        return _aligned_rectangle_corridors(program, grid)
    if operator == "scaffold_corner_rays":
        return _scaffold_corner_rays(grid)
    if operator == "typed_barrier_billiard":
        return _typed_barrier_billiard(program, grid)
    raise Undefined("unknown constructive-painting operator")


def execute_program(program: Mapping[str, Any], value: Any) -> list[list[int]]:
    """Execute one serialized, task-identity-free painting program."""

    grid = _grid(value)
    return _plain(_execute_internal(program, grid)[0])


def replay_program(program: Mapping[str, Any], value: Any) -> dict[str, Any]:
    """Replay lifting, constructive painting, and raster rendering."""

    grid = _grid(value)
    output, receipt = _execute_internal(program, grid)
    lifted = {
        "kind": "same_canvas_constructive_scene",
        "shape": list(_shape(grid)),
        "background": _background(grid),
    }
    applied = {"operator": program["operator"], "receipt": receipt}
    return {
        "output": _plain(output),
        "stages": [
            {"name": "lift-constructive-scene", "input": _plain(grid), "output": lifted},
            {"name": "apply-paint-program", "input": lifted, "output": applied},
            {"name": "render-same-canvas", "input": applied, "output": _plain(output)},
        ],
    }


def _program(operator: str, description_length: int, **parameters: Any) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "operator": operator,
        "description_length": description_length,
        **parameters,
    }


def _new_palette_candidates(pairs: Sequence[Pair]) -> tuple[int, ...]:
    candidates: set[int] | None = None
    for source, target in pairs:
        source_colors = {cell for row in source for cell in row}
        target_colors = {cell for row in target for cell in row}
        current = target_colors - source_colors
        candidates = current if candidates is None else candidates & current
    return tuple(sorted(candidates or set()))


def _boundary_observations(grid: Grid, side: str) -> tuple[tuple[Cell, int], ...]:
    background = _background(grid)
    height, width = _shape(grid)
    if side == "top":
        boundary = [(0, column) for column in range(width)]
    elif side == "bottom":
        boundary = [(height - 1, column) for column in range(width)]
    elif side == "left":
        boundary = [(row, 0) for row in range(height)]
    elif side == "right":
        boundary = [(row, width - 1) for row in range(height)]
    else:
        raise Undefined("unknown boundary side")
    anchors = [point for point in boundary if grid[point[0]][point[1]] != background]
    if len(anchors) != 1:
        raise Undefined("boundary marker is ambiguous")
    anchor = anchors[0]
    observations: list[tuple[Cell, int]] = []
    for _, cells in _components(grid, background, connectivity=4, monochrome=True):
        if cells == frozenset({anchor}):
            continue
        if anchor in cells or len(cells) < 2:
            raise Undefined("payload is not a straight run")
        rows = {row for row, _ in cells}
        columns = {column for _, column in cells}
        if side in {"top", "bottom"}:
            if len(rows) != 1 or len(cells) != max(columns) - min(columns) + 1:
                raise Undefined("payload is not horizontal")
            observations.append(((next(iter(rows)), anchor[1]), len(cells)))
        else:
            if len(columns) != 1 or len(cells) != max(rows) - min(rows) + 1:
                raise Undefined("payload is not vertical")
            observations.append(((anchor[0], next(iter(columns))), len(cells)))
    if not observations:
        raise Undefined("boundary payload is empty")
    return tuple(sorted(observations))


def _induce_boundary_programs(pairs: Sequence[Pair]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for side in ("top", "bottom", "left", "right"):
        mapping: dict[int, int] = {}
        valid = True
        for source, target in pairs:
            try:
                observations = _boundary_observations(source, side)
            except Undefined:
                valid = False
                break
            expected_changes = {point for point, _ in observations}
            actual_changes = {
                (row, column)
                for row in range(len(source))
                for column in range(len(source[0]))
                if source[row][column] != target[row][column]
            }
            if actual_changes != expected_changes:
                valid = False
                break
            for (row, column), length in observations:
                color = target[row][column]
                if source[row][column] == color or (length in mapping and mapping[length] != color):
                    valid = False
                    break
                mapping[length] = color
            if not valid:
                break
        if valid and mapping:
            result.append(
                _program(
                    "boundary_run_code",
                    15 + len(mapping),
                    side=side,
                    mapping=[[length, mapping[length]] for length in sorted(mapping)],
                )
            )
    return result


def _separator_signature(grid: Grid) -> tuple[int, tuple[int, ...]] | None:
    background = _background(grid)
    height, width = _shape(grid)
    axes: list[int] = []
    for row in range(height):
        if len(set(grid[row])) == 1 and grid[row][0] != background:
            axes.append(grid[row][0])
    for column in range(width):
        values = {grid[row][column] for row in range(height)}
        if len(values) == 1 and next(iter(values)) != background:
            axes.append(next(iter(values)))
    if len(axes) != 1:
        return None
    colors = tuple(sorted(set(_supports(grid, background)) - {axes[0]}))
    return axes[0], colors


def _induce_billiard_programs(pairs: Sequence[Pair]) -> list[dict[str, Any]]:
    ray_candidates: set[int] | None = None
    for source, _ in pairs:
        background = _background(source)
        current: set[int] = set()
        for color in _supports(source, background):
            try:
                _diagonal_segment(source, color)
            except Undefined:
                continue
            current.add(color)
        ray_candidates = current if ray_candidates is None else ray_candidates & current
    if not ray_candidates:
        return []
    result: list[dict[str, Any]] = []
    for ray_color in sorted(ray_candidates):
        obstacles = sorted(
            {
                color
                for source, _ in pairs
                for color in _supports(source, _background(source))
                if color != ray_color
            }
        )
        if not 1 <= len(obstacles) <= 4:
            continue
        for roles in itertools.product(("pass", "reflect"), repeat=len(obstacles)):
            transparent = [
                color for color, role in zip(obstacles, roles) if role == "pass"
            ]
            reflecting = [
                color for color, role in zip(obstacles, roles) if role == "reflect"
            ]
            result.append(
                _program(
                    "typed_barrier_billiard",
                    14 + len(obstacles),
                    ray_color=ray_color,
                    pass_colors=transparent,
                    reflect_colors=reflecting,
                )
            )
    return result


def _learned_programs(pairs: Sequence[Pair]) -> tuple[dict[str, Any], ...]:
    programs: list[dict[str, Any]] = []
    new_colors = _new_palette_candidates(pairs)
    for paint in new_colors:
        for period in range(2, 9):
            programs.append(
                _program(
                    "cross_chebyshev_lattice",
                    10,
                    paint=paint,
                    period=period,
                    residue=0,
                )
            )
        programs.append(_program("corner_stamp_network", 14, connector=paint))
        programs.append(_program("five_point_frame", 13, cross_color=paint))
        programs.append(_program("aligned_rectangle_corridors", 15, paint=paint))
    if len(new_colors) == 2:
        for odd_color, even_color in itertools.permutations(new_colors, 2):
            programs.append(
                _program(
                    "frame_seed_chebyshev_fill",
                    14,
                    odd_color=odd_color,
                    even_color=even_color,
                )
            )
    programs.extend(_induce_boundary_programs(pairs))
    programs.extend(_induce_billiard_programs(pairs))

    first_signature = _separator_signature(pairs[0][0])
    if first_signature is not None:
        _, colors = first_signature
        if 2 <= len(colors) <= 4:
            for toward, away in itertools.permutations(colors, 2):
                programs.append(
                    _program(
                        "separator_ray_field",
                        12,
                        toward_color=toward,
                        away_color=away,
                    )
                )

    first = pairs[0][0]
    background = _background(first)
    colors = sorted(_supports(first, background))
    line_colors = [color for color in colors if _line_components_for_color(first, color)]
    if len(colors) <= 8:
        for axis_color in line_colors:
            for template_color in colors:
                if template_color != axis_color:
                    programs.append(
                        _program(
                            "reflect_shapes_to_markers",
                            16,
                            axis_color=axis_color,
                            template_color=template_color,
                        )
                    )
    unique = {_canonical(program): program for program in programs}
    return tuple(unique[key] for key in sorted(unique))


def _fixed_programs() -> tuple[dict[str, Any], ...]:
    programs = [
        _program("concentric_square_contours", 9),
        _program("component_axis_closure", 11),
        _program("paired_marker_brackets", 12),
        _program("legend_stamp_sequence", 14),
        _program("plus_center_line_field", 13),
        _program("marked_rectangle_extrusions", 14),
        _program("scaffold_corner_rays", 12),
    ]
    for vertical, horizontal in itertools.product((-1, 1), repeat=2):
        programs.append(
            _program(
                "scaled_stamp_staircase",
                12,
                vertical=vertical,
                horizontal=horizontal,
            )
        )
    return tuple(sorted(programs, key=_canonical))


def _behavior(
    program: Mapping[str, Any], grids: Sequence[Grid], limits: Limits
) -> tuple[Grid, ...]:
    return tuple(_execute_internal(program, grid, limits)[0] for grid in grids)


def compile_task(task: Any, limits: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    """Compile a unique exact constructive behavior, otherwise abstain."""

    try:
        bounds = Limits.from_value(limits)
        demonstrations, tests = _sanitize(task, bounds)
    except (Undefined, TypeError, ValueError, KeyError, IndexError):
        return []
    try:
        programs = list(_fixed_programs()) + list(_learned_programs(demonstrations))
    except (Undefined, TypeError, ValueError, KeyError, IndexError):
        return []
    programs = list({_canonical(program): program for program in programs}.values())
    programs.sort(key=lambda item: (int(item["description_length"]), _canonical(item)))
    if len(programs) > bounds.max_programs:
        return []
    expected = tuple(target for _, target in demonstrations)
    exact: list[tuple[dict[str, Any], tuple[Grid, ...], tuple[Grid, ...]]] = []
    calls = 0
    for program in programs:
        try:
            train_outputs = _behavior(
                program, tuple(source for source, _ in demonstrations), bounds
            )
            calls += len(demonstrations)
            if train_outputs != expected:
                continue
            test_outputs = _behavior(program, tests, bounds)
            calls += len(tests)
            if calls > bounds.max_executor_calls:
                return []
        except (Undefined, TypeError, ValueError, KeyError, IndexError, ZeroDivisionError):
            continue
        exact.append((program, train_outputs, test_outputs))
    if not exact:
        return []
    behaviors: dict[str, list[tuple[dict[str, Any], tuple[Grid, ...], tuple[Grid, ...]]]] = defaultdict(list)
    for item in exact:
        behavior_hash = _digest([_plain(grid) for grid in item[2]])
        behaviors[behavior_hash].append(item)
    if len(behaviors) != 1:
        return []
    behavior_hash, equivalents = next(iter(sorted(behaviors.items())))
    equivalents.sort(key=lambda item: (int(item[0]["description_length"]), _canonical(item[0])))
    representative, train_outputs, test_outputs = equivalents[0]
    # Re-execute after selection so cached values cannot bypass the executor.
    try:
        replayed_train = _behavior(
            representative, tuple(source for source, _ in demonstrations), bounds
        )
        replayed_test = _behavior(representative, tests, bounds)
    except (Undefined, TypeError, ValueError, KeyError, IndexError, ZeroDivisionError):
        return []
    if replayed_train != expected or replayed_test != test_outputs:
        return []
    candidate = {
        "family": "constructive_paint_compiler",
        "program": json.loads(_canonical(representative)),
        "train_outputs": [_plain(grid) for grid in train_outputs],
        "test_outputs": [_plain(grid) for grid in test_outputs],
        "complexity": int(representative["description_length"]),
        "evidence": {
            "same_canvas_only": True,
            "constructive_geometry": True,
            "all_demonstrations_exact": True,
            "exact_replay": True,
            "serialized_replay_program": True,
            "finite_enumeration_complete": True,
            "programs_enumerated": len(programs),
            "exact_programs": len(exact),
            "full_test_behavior_classes": len(behaviors),
            "full_test_behavior_hash": behavior_hash,
            "equivalent_programs": len(equivalents),
            "bounded_search": True,
            "hard_caps_exhausted": False,
            "task_identity_observed": False,
            "test_labels_observed": False,
            "solution_store_observed": False,
        },
    }
    candidate["evidence"]["candidate_semantic_hash"] = _digest(candidate)
    return [candidate][: bounds.max_candidates]


__all__ = [
    "AUTHOR",
    "Limits",
    "SCHEMA",
    "compile_task",
    "execute_program",
    "replay_program",
]
