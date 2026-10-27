"""Identity-blind relational field automata for the Block 14 tournament.

The entrant searches a finite product language:

``seed selector x trajectory/field x phase x stop/collision x emission``.

Every returned record is executable by :func:`execute_program`, replays every
labelled demonstration exactly, and is evaluated on test *inputs* only.  The
compiler quotients complete multi-test behaviours.  More than one surviving
behaviour, an exhausted search budget, or an undefined role causes an
abstention.

No task identifiers, corpus hashes, solution stores, score files, test labels,
or memorised grids are consulted.

Author: Komorebi P.
"""

from __future__ import annotations

from collections import Counter, deque
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import hashlib
import json
from typing import Any, Iterable


Grid = tuple[tuple[int, ...], ...]
Pair = tuple[Grid, Grid]
Point = tuple[int, int]
SCHEMA = "komorebi.pr_lasm.block14.relational_field_automaton.v1"


class _Undefined(ValueError):
    """The requested role or automaton is not defined on an input."""


@dataclass(frozen=True, slots=True)
class Limits:
    max_side: int = 30
    max_cells: int = 900
    max_programs: int = 50_000
    max_executor_calls: int = 400_000
    max_mdl: int = 40
    max_candidates: int = 1

    @classmethod
    def from_value(cls, value: Any) -> "Limits":
        if isinstance(value, cls):
            return value
        if value is None or not isinstance(value, Mapping):
            return cls()
        defaults = cls()

        def integer(name: str, default: int, ceiling: int) -> int:
            raw = value.get(name, default)
            if isinstance(raw, bool) or not isinstance(raw, int) or raw <= 0:
                return default
            return min(raw, ceiling)

        raw_candidates = value.get("candidate_cap", value.get("max_candidates", 1))
        if isinstance(raw_candidates, bool) or not isinstance(raw_candidates, int) or raw_candidates <= 0:
            raw_candidates = 1
        return cls(
            max_side=integer("max_side", defaults.max_side, 60),
            max_cells=integer("max_cells", defaults.max_cells, 3_600),
            max_programs=integer("max_programs", defaults.max_programs, 100_000),
            max_executor_calls=integer(
                "max_executor_calls", defaults.max_executor_calls, 1_000_000
            ),
            max_mdl=integer("max_mdl", defaults.max_mdl, 128),
            max_candidates=min(raw_candidates, 1),
        )


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _grid(value: Any, limits: Limits) -> Grid:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or not value:
        raise _Undefined("grid is empty")
    rows: list[tuple[int, ...]] = []
    width: int | None = None
    for raw in value:
        if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes)) or not raw:
            raise _Undefined("grid row is invalid")
        row: list[int] = []
        for cell in raw:
            if isinstance(cell, bool) or not isinstance(cell, int) or not 0 <= cell <= 9:
                raise _Undefined("ARC cell is invalid")
            row.append(int(cell))
        if width is None:
            width = len(row)
        elif len(row) != width:
            raise _Undefined("grid is ragged")
        rows.append(tuple(row))
    height, width = len(rows), int(width or 0)
    if height > limits.max_side or width > limits.max_side or height * width > limits.max_cells:
        raise _Undefined("grid exceeds bounds")
    return tuple(rows)


def _read_task(task: Any, limits: Limits) -> tuple[tuple[Pair, ...], tuple[Grid, ...]]:
    if not isinstance(task, Mapping):
        raise _Undefined("task is invalid")
    raw_train, raw_test = task.get("train"), task.get("test")
    if (
        not isinstance(raw_train, Sequence)
        or isinstance(raw_train, (str, bytes))
        or not raw_train
        or not isinstance(raw_test, Sequence)
        or isinstance(raw_test, (str, bytes))
        or not raw_test
        or len(raw_train) + len(raw_test) > 16
    ):
        raise _Undefined("examples are invalid")
    train: list[Pair] = []
    for example in raw_train:
        if not isinstance(example, Mapping):
            raise _Undefined("demonstration is invalid")
        train.append((_grid(example.get("input"), limits), _grid(example.get("output"), limits)))
    tests: list[Grid] = []
    for example in raw_test:
        if not isinstance(example, Mapping):
            raise _Undefined("test example is invalid")
        # Deliberately fetch only the input member.  A supplied output is ignored.
        tests.append(_grid(example.get("input"), limits))
    return tuple(train), tuple(tests)


def _shape(grid: Grid) -> tuple[int, int]:
    return len(grid), len(grid[0])


def _plain(grid: Grid) -> list[list[int]]:
    return [list(row) for row in grid]


def _freeze(rows: Sequence[Sequence[int]]) -> Grid:
    return tuple(tuple(int(cell) for cell in row) for row in rows)


def _background(grid: Grid) -> int:
    counts = Counter(cell for row in grid for cell in row)
    maximum = max(counts.values())
    winners = [color for color, count in counts.items() if count == maximum]
    if len(winners) != 1:
        raise _Undefined("background mode is tied")
    return winners[0]


def _palette(grid: Grid) -> set[int]:
    return {cell for row in grid for cell in row}


def _bbox(points: Iterable[Point]) -> tuple[int, int, int, int]:
    values = tuple(points)
    if not values:
        raise _Undefined("point set is empty")
    return (
        min(row for row, _ in values),
        max(row for row, _ in values),
        min(column for _, column in values),
        max(column for _, column in values),
    )


def _components(
    grid: Grid,
    points: Iterable[Point],
    connectivity: int,
    monochrome: bool = True,
) -> list[set[Point]]:
    remaining = set(points)
    offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    if connectivity == 8:
        offsets += [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    answer: list[set[Point]] = []
    while remaining:
        seed = min(remaining)
        remaining.remove(seed)
        component = {seed}
        queue = deque([seed])
        while queue:
            row, column = queue.popleft()
            for dr, dc in offsets:
                point = row + dr, column + dc
                if point in remaining and (not monochrome or grid[point[0]][point[1]] == grid[row][column]):
                    remaining.remove(point)
                    component.add(point)
                    queue.append(point)
        answer.append(component)
    return sorted(answer, key=lambda item: (min(item), len(item)))


def _foreground_counts(grid: Grid) -> Counter[int]:
    background = _background(grid)
    return Counter(cell for row in grid for cell in row if cell != background)


def _resolve_selector(grid: Grid, selector: Mapping[str, Any]) -> tuple[Point, ...]:
    background = _background(grid)
    kind = selector.get("kind")
    if kind == "all_foreground":
        points = [(r, c) for r, row in enumerate(grid) for c, cell in enumerate(row) if cell != background]
    elif kind == "literal_color":
        color = selector.get("color")
        if isinstance(color, bool) or not isinstance(color, int):
            raise _Undefined("selector color is invalid")
        points = [(r, c) for r, row in enumerate(grid) for c, cell in enumerate(row) if cell == color]
    elif kind in {"rarest_foreground", "most_foreground", "unique_foreground"}:
        counts = _foreground_counts(grid)
        if not counts:
            raise _Undefined("foreground is empty")
        if kind == "unique_foreground":
            if len(counts) != 1:
                raise _Undefined("foreground color is not unique")
            color = next(iter(counts))
        else:
            desired = min(counts.values()) if kind == "rarest_foreground" else max(counts.values())
            winners = [color for color, count in counts.items() if count == desired]
            if len(winners) != 1:
                raise _Undefined("foreground rank is tied")
            color = winners[0]
        points = [(r, c) for r, row in enumerate(grid) for c, cell in enumerate(row) if cell == color]
    elif kind == "singleton_colors":
        counts = _foreground_counts(grid)
        colors = {color for color, count in counts.items() if count == 1}
        if not colors:
            raise _Undefined("singleton color role is absent")
        points = [(r, c) for r, row in enumerate(grid) for c, cell in enumerate(row) if cell in colors]
    elif kind == "border_foreground":
        height, width = _shape(grid)
        points = [
            (r, c)
            for r, row in enumerate(grid)
            for c, cell in enumerate(row)
            if cell != background and (r in {0, height - 1} or c in {0, width - 1})
        ]
    else:
        raise _Undefined("unknown seed selector")
    if not points:
        raise _Undefined("seed selector is empty")
    return tuple(sorted(points))


def _selected_color(grid: Grid, points: Sequence[Point]) -> int:
    colors = {grid[row][column] for row, column in points}
    if len(colors) != 1:
        raise _Undefined("selected color is not unique")
    return next(iter(colors))


def _resolve_emission(
    grid: Grid,
    selector: Mapping[str, Any],
    points: Sequence[Point],
    emission: Mapping[str, Any],
) -> int:
    kind = emission.get("kind")
    if kind == "literal_color":
        color = emission.get("color")
        if isinstance(color, bool) or not isinstance(color, int) or not 0 <= color <= 9:
            raise _Undefined("emission color is invalid")
        return color
    if kind == "seed_color":
        return _selected_color(grid, points)
    counts = _foreground_counts(grid)
    if kind == "unique_nonseed_foreground":
        seed_colors = {grid[row][column] for row, column in points}
        colors = set(counts) - seed_colors
        if len(colors) != 1:
            raise _Undefined("nonseed color is not unique")
        return next(iter(colors))
    if kind in {"rarest_foreground", "most_foreground"}:
        if not counts:
            raise _Undefined("foreground is empty")
        desired = min(counts.values()) if kind == "rarest_foreground" else max(counts.values())
        winners = [color for color, count in counts.items() if count == desired]
        if len(winners) != 1:
            raise _Undefined("emission role is tied")
        return winners[0]
    raise _Undefined("unknown emission role")


def _overlay(grid: Grid, cells: Iterable[Point], color: int) -> Grid:
    background = _background(grid)
    height, width = _shape(grid)
    result = [list(row) for row in grid]
    changed = False
    for row, column in sorted(set(cells)):
        if not (0 <= row < height and 0 <= column < width):
            continue
        if grid[row][column] == background:
            result[row][column] = color
            changed = True
    if not changed:
        raise _Undefined("field emits no cells")
    return _freeze(result)


def _perimeter(top: int, bottom: int, left: int, right: int) -> set[Point]:
    if top > bottom or left > right:
        raise _Undefined("rectangle is empty")
    return (
        {(top, column) for column in range(left, right + 1)}
        | {(bottom, column) for column in range(left, right + 1)}
        | {(row, left) for row in range(top, bottom + 1)}
        | {(row, right) for row in range(top, bottom + 1)}
    )


def _field_selection_bbox(
    grid: Grid, points: Sequence[Point], field: Mapping[str, Any], color: int
) -> Grid:
    height, width = _shape(grid)
    top, bottom, left, right = _bbox(points)
    margin = field.get("margin")
    if isinstance(margin, bool) or not isinstance(margin, int):
        raise _Undefined("bbox margin is invalid")
    top, bottom, left, right = top - margin, bottom + margin, left - margin, right + margin
    if not (0 <= top <= bottom < height and 0 <= left <= right < width):
        raise _Undefined("bbox is outside canvas")
    if field.get("style") == "perimeter":
        cells = _perimeter(top, bottom, left, right)
    elif field.get("style") == "fill":
        cells = {(r, c) for r in range(top, bottom + 1) for c in range(left, right + 1)}
    else:
        raise _Undefined("bbox style is invalid")
    return _overlay(grid, cells, color)


def _field_component_bbox(
    grid: Grid, points: Sequence[Point], field: Mapping[str, Any], color: int
) -> Grid:
    connectivity = field.get("connectivity")
    if connectivity not in {4, 8}:
        raise _Undefined("connectivity is invalid")
    grouping = field.get("grouping")
    if grouping not in {"monochrome", "joint", "absorb_diagonal_singletons"}:
        raise _Undefined("component grouping is invalid")
    components = _components(grid, points, connectivity, grouping != "joint")
    if grouping == "absorb_diagonal_singletons":
        if connectivity != 4:
            raise _Undefined("singleton absorption starts from 4-components")
        majors = [set(component) for component in components if len(component) > 1]
        satellites = [set(component) for component in components if len(component) == 1]
        if not majors or not satellites:
            raise _Undefined("singleton absorption has no satellite")
        for satellite in satellites:
            point = next(iter(satellite))
            neighbours = [
                index
                for index, major in enumerate(majors)
                if any(max(abs(point[0] - row), abs(point[1] - column)) == 1 for row, column in major)
            ]
            if not neighbours:
                raise _Undefined("diagonal satellite is unattached")
            merged = set(satellite)
            for index in reversed(neighbours):
                merged |= majors.pop(index)
            majors.append(merged)
        components = sorted(majors, key=lambda item: (min(item), len(item)))
    cells: set[Point] = set()
    incomplete = 0
    for component in components:
        top, bottom, left, right = _bbox(component)
        box = {(r, c) for r in range(top, bottom + 1) for c in range(left, right + 1)}
        if box - component:
            incomplete += 1
        if field.get("style") == "fill":
            cells |= box
        elif field.get("style") == "perimeter":
            cells |= _perimeter(top, bottom, left, right)
        else:
            raise _Undefined("component bbox style is invalid")
    if incomplete == 0:
        raise _Undefined("component bboxes are already complete")
    return _overlay(grid, cells, color)


def _line_cells(first: Point, second: Point) -> set[Point]:
    dr, dc = second[0] - first[0], second[1] - first[1]
    if dr == 0:
        step = (0, 1 if dc > 0 else -1)
    elif dc == 0:
        step = (1 if dr > 0 else -1, 0)
    elif abs(dr) == abs(dc):
        step = (1 if dr > 0 else -1, 1 if dc > 0 else -1)
    else:
        raise _Undefined("points are not queen-aligned")
    length = max(abs(dr), abs(dc))
    return {(first[0] + index * step[0], first[1] + index * step[1]) for index in range(length + 1)}


def _field_aligned_segments(
    grid: Grid, points: Sequence[Point], field: Mapping[str, Any], color: int
) -> Grid:
    axes = field.get("axes")
    allowed = {
        "horizontal": {"h"},
        "vertical": {"v"},
        "orthogonal": {"h", "v"},
        "diagonal": {"d1", "d2"},
        "queen": {"h", "v", "d1", "d2"},
    }.get(str(axes))
    if allowed is None:
        raise _Undefined("alignment axes are invalid")
    grouping = field.get("grouping")
    if grouping == "joint":
        groups = [tuple(points)]
    elif grouping == "by_color":
        groups = [tuple(point for point in points if grid[point[0]][point[1]] == value) for value in sorted({grid[r][c] for r, c in points})]
    else:
        raise _Undefined("segment grouping is invalid")
    cells: set[Point] = set()
    segments = 0
    for group in groups:
        line_groups: dict[tuple[str, int], list[Point]] = {}
        for row, column in group:
            if "h" in allowed:
                line_groups.setdefault(("h", row), []).append((row, column))
            if "v" in allowed:
                line_groups.setdefault(("v", column), []).append((row, column))
            if "d1" in allowed:
                line_groups.setdefault(("d1", row - column), []).append((row, column))
            if "d2" in allowed:
                line_groups.setdefault(("d2", row + column), []).append((row, column))
        for aligned in line_groups.values():
            if len(aligned) < 2:
                continue
            ordered = sorted(aligned)
            segment = _line_cells(ordered[0], ordered[-1])
            if len(segment - set(group)) > 0:
                segments += 1
            cells |= segment
    if not segments:
        raise _Undefined("no incomplete aligned segment")
    return _overlay(grid, cells, color)


def _choose_anchor(grid: Grid, points: Sequence[Point], policy: str) -> Point:
    if len(points) != 2:
        raise _Undefined("dogleg needs exactly two seeds")
    if policy == "lex_first":
        return min(points)
    if policy == "lex_last":
        return max(points)
    if policy in {"color_min", "color_max"}:
        desired = min(grid[r][c] for r, c in points) if policy == "color_min" else max(grid[r][c] for r, c in points)
        winners = [point for point in points if grid[point[0]][point[1]] == desired]
    elif policy in {"top", "bottom", "left", "right"}:
        index = 0 if policy in {"top", "bottom"} else 1
        values = [point[index] for point in points]
        desired = min(values) if policy in {"top", "left"} else max(values)
        winners = [point for point in points if point[index] == desired]
    else:
        raise _Undefined("dogleg anchor policy is invalid")
    if len(winners) != 1:
        raise _Undefined("dogleg anchor is tied")
    return winners[0]


def _field_dogleg(
    grid: Grid, points: Sequence[Point], field: Mapping[str, Any], state: Mapping[str, Any], color: int
) -> Grid:
    start = _choose_anchor(grid, points, str(field.get("anchor")))
    end = points[0] if points[1] == start else points[1]
    dr, dc = end[0] - start[0], end[1] - start[1]
    vertical, horizontal = abs(dr), abs(dc)
    diagonal_steps = min(vertical, horizontal)
    axial_steps = abs(vertical - horizontal)
    lead = state.get("lead_diagonals")
    if isinstance(lead, bool) or not isinstance(lead, int) or not 0 <= lead <= diagonal_steps:
        raise _Undefined("dogleg phase is invalid")
    sr = 0 if dr == 0 else (1 if dr > 0 else -1)
    sc = 0 if dc == 0 else (1 if dc > 0 else -1)
    row, column = start
    path = {start}
    for _ in range(lead):
        row, column = row + sr, column + sc
        path.add((row, column))
    axial = (sr, 0) if vertical >= horizontal else (0, sc)
    for _ in range(axial_steps):
        row, column = row + axial[0], column + axial[1]
        path.add((row, column))
    for _ in range(diagonal_steps - lead):
        row, column = row + sr, column + sc
        path.add((row, column))
    if (row, column) != end:
        raise _Undefined("dogleg did not reach endpoint")
    return _overlay(grid, path, color)


def _field_segment_wave(
    grid: Grid, points: Sequence[Point], field: Mapping[str, Any], color: int
) -> Grid:
    components = _components(grid, points, 4, True)
    cells: set[Point] = set()
    valid = 0
    for component in components:
        top, bottom, left, right = _bbox(component)
        if top == bottom and len(component) == right - left + 1 and len(component) >= 3:
            valid += 1
            for distance in range(1, (right - left + 1) // 2 + 1):
                lo, hi = left + distance, right - distance
                if lo <= hi:
                    for row in (top - distance, top + distance):
                        cells |= {(row, column) for column in range(lo, hi + 1)}
        elif left == right and len(component) == bottom - top + 1 and len(component) >= 3:
            valid += 1
            for distance in range(1, (bottom - top + 1) // 2 + 1):
                lo, hi = top + distance, bottom - distance
                if lo <= hi:
                    for column in (left - distance, left + distance):
                        cells |= {(row, column) for row in range(lo, hi + 1)}
        else:
            raise _Undefined("selected component is not a straight segment")
    if not valid:
        raise _Undefined("segment wave has no source")
    return _overlay(grid, cells, color)


def _shortest_period(values: Sequence[bool], cap: int) -> int:
    for period in range(1, min(cap, len(values)) + 1):
        if all(values[index] == values[index % period] for index in range(len(values))):
            return period
    raise _Undefined("edge prefix has no bounded period")


def _field_periodic_continuation(
    grid: Grid, points: Sequence[Point], field: Mapping[str, Any], color: int
) -> Grid:
    axis, direction = field.get("axis"), field.get("direction")
    cap = field.get("max_period")
    if axis not in {"rows", "columns"} or direction not in {"forward", "reverse"} or not isinstance(cap, int):
        raise _Undefined("periodic field parameters are invalid")
    height, width = _shape(grid)
    selected = set(points)
    cells: set[Point] = set()
    complete = incomplete = 0
    line_count, line_length = (height, width) if axis == "rows" else (width, height)
    for outer in range(line_count):
        occupancy = [((outer, inner) if axis == "rows" else (inner, outer)) in selected for inner in range(line_length)]
        if direction == "reverse":
            occupancy.reverse()
        occupied = [index for index, value in enumerate(occupancy) if value]
        if not occupied:
            continue
        last = max(occupied)
        if last == line_length - 1:
            complete += 1
            continue
        incomplete += 1
        prefix = occupancy[: last + 1]
        period = _shortest_period(prefix, cap)
        for index in range(last + 1, line_length):
            if prefix[index % period]:
                actual = line_length - 1 - index if direction == "reverse" else index
                point = (outer, actual) if axis == "rows" else (actual, outer)
                cells.add(point)
    if complete < 1 or incomplete < 1:
        raise _Undefined("periodic continuation lacks reference and partial lines")
    return _overlay(grid, cells, color)


def _field_edge_motif_rays(
    grid: Grid, points: Sequence[Point], field: Mapping[str, Any], color: int
) -> Grid:
    """Complete edge-born motifs using a finite frontier state.

    Gapped bands retain their shortest row phase.  Solid path-like bands use
    the last transverse step once, then turn into a boundary ray.  At least
    one complete edge-to-edge component is required as evidence.
    """

    axis, direction = field.get("axis"), field.get("direction")
    cap = field.get("max_period")
    if axis not in {"rows", "columns"} or direction not in {"forward", "reverse"} or not isinstance(cap, int):
        raise _Undefined("edge motif parameters are invalid")
    height, width = _shape(grid)
    line_count, length = (height, width) if axis == "rows" else (width, height)

    def oriented(point: Point) -> Point:
        row, column = point
        line, position = (row, column) if axis == "rows" else (column, row)
        if direction == "reverse":
            position = length - 1 - position
        return line, position

    def original(line: int, position: int) -> Point:
        if direction == "reverse":
            position = length - 1 - position
        return (line, position) if axis == "rows" else (position, line)

    oriented_points = {oriented(point) for point in points}
    # Eight-neighbour components in (transverse line, propagation position).
    remaining = set(oriented_points)
    components: list[set[Point]] = []
    while remaining:
        seed = min(remaining)
        remaining.remove(seed)
        component = {seed}
        queue = [seed]
        while queue:
            line, position = queue.pop()
            for dl in (-1, 0, 1):
                for dp in (-1, 0, 1):
                    neighbour = line + dl, position + dp
                    if (dl or dp) and neighbour in remaining:
                        remaining.remove(neighbour)
                        component.add(neighbour)
                        queue.append(neighbour)
        components.append(component)
    anchored = [component for component in components if any(position == 0 for _, position in component)]
    if len(anchored) != len(components) or not any(any(position == length - 1 for _, position in component) for component in anchored):
        raise _Undefined("edge motif lacks a complete reference component")
    cells: set[Point] = set()
    partials = 0
    for component in anchored:
        if any(position == length - 1 for _, position in component):
            continue
        partials += 1
        by_line: dict[int, set[int]] = {}
        for line, position in component:
            by_line.setdefault(line, set()).add(position)
        has_internal_gap = any(
            any(position not in positions for position in range(min(positions), max(positions) + 1))
            for positions in by_line.values()
        )
        if has_internal_gap:
            for line, positions in by_line.items():
                last = max(positions)
                prefix = [position in positions for position in range(last + 1)]
                period = _shortest_period(prefix, cap)
                for position in range(last + 1, length):
                    if prefix[position % period]:
                        cells.add(original(line, position))
        else:
            frontier_position = max(position for _, position in component)
            frontier = [(line, position) for line, position in component if position == frontier_position]
            previous = [(line, position) for line, position in component if position == frontier_position - 1]
            if not frontier or not previous:
                raise _Undefined("path frontier is ambiguous")
            ray_lines: set[int] = set()
            for line, _ in frontier:
                nearest = min(previous, key=lambda point: (abs(point[0] - line), point[0]))
                if sum(abs(point[0] - line) == abs(nearest[0] - line) for point in previous) != 1:
                    raise _Undefined("frontier phase is tied")
                velocity = line - nearest[0]
                if abs(velocity) > 1:
                    raise _Undefined("frontier transverse velocity is too large")
                ray_line = line + velocity
                if not 0 <= ray_line < line_count or ray_line in ray_lines:
                    raise _Undefined("frontier rays collide or leave canvas")
                ray_lines.add(ray_line)
            for ray_line in ray_lines:
                cells |= {original(ray_line, position) for position in range(frontier_position + 1, length)}
    if not partials:
        raise _Undefined("edge motif has no partial component")
    return _overlay(grid, cells, color)


def _edge_points(height: int, width: int, edge: str) -> set[Point]:
    if edge == "top":
        return {(0, column) for column in range(width)}
    if edge == "bottom":
        return {(height - 1, column) for column in range(width)}
    if edge == "left":
        return {(row, 0) for row in range(height)}
    if edge == "right":
        return {(row, width - 1) for row in range(height)}
    raise _Undefined("edge is invalid")


def _inward(edge: str) -> Point:
    return {"top": (1, 0), "bottom": (-1, 0), "left": (0, 1), "right": (0, -1)}[edge]


def _side(direction: Point, handedness: str) -> Point:
    dr, dc = direction
    if handedness == "clockwise":
        return dc, -dr
    if handedness == "counterclockwise":
        return -dc, dr
    raise _Undefined("handedness is invalid")


def _field_deflecting_rays(
    grid: Grid, points: Sequence[Point], field: Mapping[str, Any], color: int
) -> Grid:
    edge = str(field.get("seed_edge"))
    handedness = str(field.get("handedness"))
    height, width = _shape(grid)
    if len(points) < 2 or any(point not in _edge_points(height, width, edge) for point in points):
        raise _Undefined("ray seeds are not confined to one edge")
    direction, side = _inward(edge), _side(_inward(edge), handedness)
    background = _background(grid)
    cells: set[Point] = set()
    for seed in points:
        current = seed
        seen = {current}
        for _ in range(height * width):
            forward = current[0] + direction[0], current[1] + direction[1]
            if not (0 <= forward[0] < height and 0 <= forward[1] < width):
                break
            if grid[forward[0]][forward[1]] == background:
                current = forward
                cells.add(current)
            else:
                lateral = current[0] + side[0], current[1] + side[1]
                if (
                    not (0 <= lateral[0] < height and 0 <= lateral[1] < width)
                    or grid[lateral[0]][lateral[1]] != background
                ):
                    break
                current = lateral
                cells.add(current)
            if current in seen:
                raise _Undefined("ray entered a cycle")
            seen.add(current)
        else:
            raise _Undefined("ray step cap exhausted")
    return _overlay(grid, cells, color)


def _perpendicular(first: str, second: str) -> bool:
    return (first in {"top", "bottom"}) != (second in {"top", "bottom"})


def _field_boundary_controlled_lattice(
    grid: Grid,
    points: Sequence[Point],
    field: Mapping[str, Any],
    emission: Mapping[str, Any],
) -> Grid:
    seed_edge, control_edge = str(field.get("seed_edge")), str(field.get("control_edge"))
    controller = field.get("controller")
    if not isinstance(controller, Mapping):
        raise _Undefined("controller selector is invalid")
    controls = _resolve_selector(grid, controller)
    height, width = _shape(grid)
    if seed_edge == "inferred" and control_edge == "inferred_perpendicular":
        seed_options = [
            edge
            for edge in ("top", "bottom", "left", "right")
            if all(point in _edge_points(height, width, edge) for point in points)
        ]
        pairs = [
            (edge, other)
            for edge in seed_options
            for other in ("top", "bottom", "left", "right")
            if _perpendicular(edge, other)
            and all(point in _edge_points(height, width, other) for point in controls)
        ]
        if len(pairs) != 1:
            raise _Undefined("lattice edge roles are ambiguous")
        seed_edge, control_edge = pairs[0]
    if not _perpendicular(seed_edge, control_edge):
        raise _Undefined("lattice edges are not perpendicular")
    if (
        len(points) < 2
        or not controls
        or any(point not in _edge_points(height, width, seed_edge) for point in points)
        or any(point not in _edge_points(height, width, control_edge) for point in controls)
    ):
        raise _Undefined("lattice boundary roles are invalid")
    color = _resolve_emission(grid, field.get("seed_selector", {}), points, emission)
    direction = _inward(seed_edge)
    shift = _inward(control_edge)
    positions = set(points)
    cells: set[Point] = set()
    slice_count = height if seed_edge in {"top", "bottom"} else width
    control_slices = {
        row if seed_edge in {"top", "bottom"} else column for row, column in controls
    }
    for _ in range(1, slice_count):
        positions = {(row + direction[0], column + direction[1]) for row, column in positions}
        sample = next(iter(positions))
        slice_coordinate = sample[0] if seed_edge in {"top", "bottom"} else sample[1]
        if slice_coordinate in control_slices:
            positions = {(row + shift[0], column + shift[1]) for row, column in positions}
        positions = {
            (row, column)
            for row, column in positions
            if 0 <= row < height and 0 <= column < width
        }
        cells |= positions
    return _overlay(grid, cells, color)


def _field_center_cross_rays(
    grid: Grid, points: Sequence[Point], field: Mapping[str, Any], color: int
) -> Grid:
    height, width = _shape(grid)
    components = _components(grid, points, 4, True)
    cells: set[Point] = set()
    for component in components:
        top, bottom, left, right = _bbox(component)
        if bottom - top != right - left or (bottom - top + 1) % 2 != 1 or bottom - top + 1 < 3:
            raise _Undefined("cross source is not an odd square")
        if component != _perimeter(top, bottom, left, right):
            raise _Undefined("cross source is not a hollow square")
        center_row, center_column = (top + bottom) // 2, (left + right) // 2
        cells |= {(center_row, column) for column in range(width)}
        cells |= {(row, center_column) for row in range(height)}
    return _overlay(grid, cells, color)


def _normalize(component: set[Point]) -> tuple[Point, ...]:
    top, _, left, _ = _bbox(component)
    return tuple(sorted((row - top, column - left) for row, column in component))


def _field_complete_component_lattice(
    grid: Grid, points: Sequence[Point], field: Mapping[str, Any], color: int
) -> Grid:
    components = _components(grid, points, 4, True)
    if len(components) < 3:
        raise _Undefined("component lattice needs three exemplars")
    shapes = {_normalize(component) for component in components}
    if len(shapes) != 1:
        raise _Undefined("component lattice motifs differ")
    shape = next(iter(shapes))
    anchors = []
    for component in components:
        top, _, left, _ = _bbox(component)
        anchors.append((top, left))
    rows, columns = sorted({row for row, _ in anchors}), sorted({column for _, column in anchors})
    if len(rows) < 2 or len(columns) < 2 or len(rows) * len(columns) == len(anchors):
        raise _Undefined("component lattice is not a partial Cartesian product")
    height, width = _shape(grid)
    cells: set[Point] = set()
    missing = 0
    occupied = set(anchors)
    for row in rows:
        for column in columns:
            if (row, column) in occupied:
                continue
            missing += 1
            motif = {(row + dr, column + dc) for dr, dc in shape}
            if any(not (0 <= rr < height and 0 <= cc < width) for rr, cc in motif):
                raise _Undefined("lattice motif leaves canvas")
            cells |= motif
    if not missing:
        raise _Undefined("component lattice is complete")
    return _overlay(grid, cells, color)


def _field_nested_rectangle_wave(grid: Grid) -> Grid:
    background = _background(grid)
    foreground = {(r, c) for r, row in enumerate(grid) for c, cell in enumerate(row) if cell != background}
    top, bottom, left, right = _bbox(foreground)
    box = {(r, c) for r in range(top, bottom + 1) for c in range(left, right + 1)}
    if foreground != box:
        raise _Undefined("nested rectangle is not solid as a two-color field")
    colors = sorted({grid[r][c] for r, c in foreground})
    if len(colors) != 2:
        raise _Undefined("nested rectangle does not have two roles")
    cores: list[tuple[int, int, int, int, int]] = []
    for color in colors:
        selected = {(r, c) for r, c in foreground if grid[r][c] == color}
        ct, cb, cl, cr = _bbox(selected)
        rectangle = {(r, c) for r in range(ct, cb + 1) for c in range(cl, cr + 1)}
        if selected == rectangle and top < ct <= cb < bottom and left < cl <= cr < right:
            cores.append((color, ct, cb, cl, cr))
    if len(cores) != 1:
        raise _Undefined("nested core is not unique")
    color, ct, cb, cl, cr = cores[0]
    height, width = _shape(grid)
    clearance = min(top, height - 1 - bottom, left, width - 1 - right)
    thickness = min(cb - ct + 1, cr - cl + 1, clearance)
    if thickness < 1:
        raise _Undefined("nested wave has no clearance")
    outer = (top - thickness, bottom + thickness, left - thickness, right + thickness)
    ot, ob, ol, oright = outer
    cells = {
        (r, c)
        for r in range(ot, ob + 1)
        for c in range(ol, oright + 1)
        if min(r - ot, ob - r, c - ol, oright - c) < thickness
    }
    return _overlay(grid, cells, color)


def _field_nearest_boundary_attraction(
    grid: Grid, points: Sequence[Point], field: Mapping[str, Any]
) -> Grid:
    orientation = field.get("orientation")
    height, width = _shape(grid)
    if orientation == "inferred":
        possibilities: list[str] = []
        if (
            len({grid[0][column] for column in range(width)}) == 1
            and len({grid[height - 1][column] for column in range(width)}) == 1
        ):
            possibilities.append("vertical")
        if (
            len({grid[row][0] for row in range(height)}) == 1
            and len({grid[row][width - 1] for row in range(height)}) == 1
        ):
            possibilities.append("horizontal")
        if len(possibilities) != 1:
            raise _Undefined("rail orientation is ambiguous")
        orientation = possibilities[0]
    if orientation == "vertical":
        first = {grid[0][column] for column in range(width)}
        second = {grid[height - 1][column] for column in range(width)}
        if len(first) != 1 or len(second) != 1:
            raise _Undefined("horizontal rails are not uniform")
        first_color, second_color = next(iter(first)), next(iter(second))
        if first_color == second_color or first_color == _background(grid) or second_color == _background(grid):
            raise _Undefined("horizontal rail colors are invalid")
        emitted: dict[Point, int] = {}
        for row, column in points:
            if row in {0, height - 1} or row == height - 1 - row:
                raise _Undefined("marker is on or tied between rails")
            step, color = (-1, first_color) if row < height - 1 - row else (1, second_color)
            emitted[(row + step, column)] = color
    elif orientation == "horizontal":
        first = {grid[row][0] for row in range(height)}
        second = {grid[row][width - 1] for row in range(height)}
        if len(first) != 1 or len(second) != 1:
            raise _Undefined("vertical rails are not uniform")
        first_color, second_color = next(iter(first)), next(iter(second))
        if first_color == second_color or first_color == _background(grid) or second_color == _background(grid):
            raise _Undefined("vertical rail colors are invalid")
        emitted = {}
        for row, column in points:
            if column in {0, width - 1} or column == width - 1 - column:
                raise _Undefined("marker is on or tied between rails")
            step, color = (-1, first_color) if column < width - 1 - column else (1, second_color)
            emitted[(row, column + step)] = color
    else:
        raise _Undefined("rail orientation is invalid")
    background = _background(grid)
    result = [list(row) for row in grid]
    changed = False
    for (row, column), color in sorted(emitted.items()):
        if grid[row][column] != background:
            raise _Undefined("rail attraction collides")
        result[row][column] = color
        changed = True
    if not changed:
        raise _Undefined("rail attraction emits no cells")
    return _freeze(result)


def execute_program(program: Mapping[str, Any], value: Any, limits: Mapping[str, Any] | None = None) -> list[list[int]]:
    """Execute one emitted program record on a new grid."""

    bounds = Limits.from_value(limits)
    grid = _grid(value, bounds)
    if not isinstance(program, Mapping) or program.get("schema") != SCHEMA:
        raise _Undefined("program schema is invalid")
    selector = program.get("seed_selector")
    field = program.get("trajectory")
    state = program.get("state")
    collision = program.get("collision")
    emission = program.get("emission")
    if not all(isinstance(part, Mapping) for part in (selector, field, state, collision, emission)):
        raise _Undefined("program factor is invalid")
    if collision.get("policy") != "preserve_existing":
        raise _Undefined("unsupported collision policy")
    generator = field.get("generator")
    if generator == "nested_rectangle_wave":
        result = _field_nested_rectangle_wave(grid)
    else:
        points = _resolve_selector(grid, selector)
        if generator == "boundary_controlled_lattice":
            embedded = dict(field)
            embedded["seed_selector"] = selector
            result = _field_boundary_controlled_lattice(grid, points, embedded, emission)
        elif generator == "nearest_boundary_attraction":
            result = _field_nearest_boundary_attraction(grid, points, field)
        else:
            color = _resolve_emission(grid, selector, points, emission)
            if generator == "selection_bbox":
                result = _field_selection_bbox(grid, points, field, color)
            elif generator == "component_bbox":
                result = _field_component_bbox(grid, points, field, color)
            elif generator == "aligned_segments":
                result = _field_aligned_segments(grid, points, field, color)
            elif generator == "phase_biased_dogleg":
                result = _field_dogleg(grid, points, field, state, color)
            elif generator == "segment_manhattan_wave":
                result = _field_segment_wave(grid, points, field, color)
            elif generator == "periodic_edge_continuation":
                result = _field_periodic_continuation(grid, points, field, color)
            elif generator == "edge_motif_frontier_rays":
                result = _field_edge_motif_rays(grid, points, field, color)
            elif generator == "deflecting_boundary_rays":
                result = _field_deflecting_rays(grid, points, field, color)
            elif generator == "component_center_cross_rays":
                result = _field_center_cross_rays(grid, points, field, color)
            elif generator == "complete_component_lattice":
                result = _field_complete_component_lattice(grid, points, field, color)
            else:
                raise _Undefined("unknown field generator")
    checked = _grid(result, bounds)
    return _plain(checked)


def replay_program(program: Mapping[str, Any], grid: Any) -> dict[str, Any]:
    """Tournament replay hook with a bounded, contiguous one-stage trace."""

    source = _plain(_grid(grid, Limits()))
    output = execute_program(program, source)
    trajectory = program.get("trajectory") if isinstance(program, Mapping) else None
    generator = trajectory.get("generator") if isinstance(trajectory, Mapping) else "field"
    return {
        "output": output,
        "stages": [
            {
                "name": f"relational-field:{generator}",
                "input": source,
                "output": output,
            }
        ],
    }


def _selector_specs(train: Sequence[Pair]) -> list[dict[str, Any]]:
    common: set[int] | None = None
    for source, _ in train:
        foreground = _palette(source) - {_background(source)}
        common = foreground if common is None else common & foreground
    specs = [
        {"kind": "all_foreground"},
        {"kind": "unique_foreground"},
        {"kind": "rarest_foreground"},
        {"kind": "most_foreground"},
        {"kind": "singleton_colors"},
        {"kind": "border_foreground"},
    ]
    specs.extend({"kind": "literal_color", "color": color} for color in sorted(common or set()))
    unique = {_canonical(spec): spec for spec in specs}
    return [unique[key] for key in sorted(unique)]


def _emission_specs(train: Sequence[Pair]) -> list[dict[str, Any]]:
    changed_sets: list[set[int]] = []
    for source, target in train:
        changed_sets.append(
            {
                target[row][column]
                for row in range(len(source))
                for column in range(len(source[0]))
                if source[row][column] != target[row][column]
            }
        )
    specs = [
        {"kind": "seed_color"},
        {"kind": "unique_nonseed_foreground"},
        {"kind": "rarest_foreground"},
        {"kind": "most_foreground"},
    ]
    common = set.intersection(*changed_sets) if changed_sets else set()
    specs.extend({"kind": "literal_color", "color": color} for color in sorted(common))
    unique = {_canonical(spec): spec for spec in specs}
    return [unique[key] for key in sorted(unique)]


def _program(
    selector: Mapping[str, Any],
    generator: str,
    *,
    trajectory: Mapping[str, Any] | None = None,
    state: Mapping[str, Any] | None = None,
    stop: Mapping[str, Any] | None = None,
    emission: Mapping[str, Any] | None = None,
    mdl: int,
) -> dict[str, Any]:
    field = {"generator": generator}
    if trajectory:
        field.update(trajectory)
    return {
        "schema": SCHEMA,
        "seed_selector": json.loads(_canonical(selector)),
        "trajectory": json.loads(_canonical(field)),
        "state": json.loads(_canonical(state or {"phase": "stationary"})),
        "stop": json.loads(_canonical(stop or {"policy": "canvas_boundary"})),
        "collision": {"policy": "preserve_existing"},
        "emission": json.loads(_canonical(emission or {"kind": "seed_color"})),
        "description_length": int(mdl),
    }


def _enumerate_programs(train: Sequence[Pair]) -> list[dict[str, Any]]:
    selectors, emissions = _selector_specs(train), _emission_specs(train)
    proposals: dict[str, dict[str, Any]] = {}

    def add(program: dict[str, Any]) -> None:
        proposals.setdefault(_canonical(program), program)

    for selector in selectors:
        for emission in emissions:
            for style in ("perimeter", "fill"):
                for margin in (-2, -1, 0, 1, 2):
                    add(_program(selector, "selection_bbox", trajectory={"style": style, "margin": margin}, emission=emission, mdl=8 + abs(margin)))
                for connectivity in (4, 8):
                    for grouping in ("monochrome", "joint", "absorb_diagonal_singletons"):
                        add(_program(selector, "component_bbox", trajectory={"style": style, "connectivity": connectivity, "grouping": grouping}, emission=emission, mdl=10))
            for axes in ("horizontal", "vertical", "orthogonal", "diagonal", "queen"):
                for grouping in ("joint", "by_color"):
                    add(_program(selector, "aligned_segments", trajectory={"axes": axes, "grouping": grouping}, emission=emission, mdl=10))
            for anchor in ("lex_first", "lex_last", "color_min", "color_max", "top", "bottom", "left", "right"):
                for lead in range(4):
                    add(_program(selector, "phase_biased_dogleg", trajectory={"anchor": anchor}, state={"phase": "split_diagonal", "lead_diagonals": lead}, emission=emission, mdl=12 + lead))
            add(_program(selector, "segment_manhattan_wave", state={"phase": "distance_layer"}, emission=emission, mdl=11))
            for axis in ("rows", "columns"):
                for direction in ("forward", "reverse"):
                    add(_program(selector, "periodic_edge_continuation", trajectory={"axis": axis, "direction": direction, "max_period": 6}, state={"phase": "minimal_prefix_period"}, emission=emission, mdl=13))
                    add(_program(selector, "edge_motif_frontier_rays", trajectory={"axis": axis, "direction": direction, "max_period": 6}, state={"phase": "frontier_velocity_then_ray"}, emission=emission, mdl=14))
            for edge in ("top", "bottom", "left", "right"):
                for handedness in ("clockwise", "counterclockwise"):
                    add(_program(selector, "deflecting_boundary_rays", trajectory={"seed_edge": edge, "handedness": handedness}, stop={"policy": "boundary_or_blocked_sidestep"}, emission=emission, mdl=13))
            add(_program(selector, "component_center_cross_rays", trajectory={"component": "hollow_odd_square"}, emission=emission, mdl=11))
            add(_program(selector, "complete_component_lattice", state={"phase": "missing_cartesian_sites"}, emission=emission, mdl=13))

    # Two independently selected boundary roles form the control automaton.
    for seed_selector in selectors:
        for controller in selectors:
            if seed_selector == controller:
                continue
            for seed_edge in ("top", "bottom", "left", "right"):
                for control_edge in ("top", "bottom", "left", "right"):
                    if _perpendicular(seed_edge, control_edge):
                        add(_program(seed_selector, "boundary_controlled_lattice", trajectory={"seed_edge": seed_edge, "control_edge": control_edge, "controller": controller}, state={"phase": "shift_on_controller_slice"}, stop={"policy": "canvas_boundary"}, emission={"kind": "seed_color"}, mdl=15))
            add(_program(seed_selector, "boundary_controlled_lattice", trajectory={"seed_edge": "inferred", "control_edge": "inferred_perpendicular", "controller": controller}, state={"phase": "shift_on_controller_slice"}, stop={"policy": "canvas_boundary"}, emission={"kind": "seed_color"}, mdl=14))

    for selector in selectors:
        for orientation in ("vertical", "horizontal", "inferred"):
            add(_program(selector, "nearest_boundary_attraction", trajectory={"orientation": orientation}, state={"phase": "one_step"}, emission={"kind": "rail_color"}, mdl=10))

    add(_program({"kind": "all_foreground"}, "nested_rectangle_wave", state={"phase": "core_width_capped_by_clearance"}, emission={"kind": "nested_core_color"}, mdl=12))
    return [proposals[key] for key in sorted(proposals)]


def _additive_guard(train: Sequence[Pair]) -> bool:
    for source, target in train:
        if _shape(source) != _shape(target):
            return False
        try:
            background = _background(source)
        except _Undefined:
            return False
        changed = False
        for row in range(len(source)):
            for column in range(len(source[0])):
                before, after = source[row][column], target[row][column]
                if before != after:
                    changed = True
                    if before != background:
                        return False
        if not changed:
            return False
    return True


def compile_task(task: Any, limits: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    """Synthesize one unambiguous exact relational-field behaviour."""

    bounds = Limits.from_value(limits)
    try:
        train, tests = _read_task(task, bounds)
    except (_Undefined, KeyError, TypeError, ValueError):
        return []
    if not _additive_guard(train):
        return []
    programs = _enumerate_programs(train)
    # Never return a result from a truncated prefix of the language.
    if len(programs) > bounds.max_programs:
        return []
    order_signature = hashlib.sha256(_canonical(programs).encode("ascii")).hexdigest()
    if len(train) > 1:
        reversed_programs = _enumerate_programs(tuple(reversed(train)))
        reversed_signature = hashlib.sha256(
            _canonical(reversed_programs).encode("ascii")
        ).hexdigest()
        if reversed_signature != order_signature:
            return []
    behaviours: dict[str, list[tuple[dict[str, Any], list[Grid], list[Grid]]]] = {}
    calls = 0
    for program in programs:
        if int(program["description_length"]) > bounds.max_mdl:
            continue
        try:
            replay: list[Grid] = []
            for source, target in train:
                calls += 1
                if calls > bounds.max_executor_calls:
                    return []
                actual = _grid(execute_program(program, source, bounds), bounds)
                if actual != target:
                    raise _Undefined("demonstration mismatch")
                replay.append(actual)
            predictions: list[Grid] = []
            for source in tests:
                calls += 1
                if calls > bounds.max_executor_calls:
                    return []
                predictions.append(_grid(execute_program(program, source, bounds), bounds))
        except (_Undefined, KeyError, TypeError, ValueError, IndexError, ZeroDivisionError):
            continue
        key = _canonical([_plain(grid) for grid in predictions])
        behaviours.setdefault(key, []).append((program, replay, predictions))
    if len(behaviours) != 1:
        return []
    entries = next(iter(behaviours.values()))
    entries.sort(key=lambda item: (int(item[0]["description_length"]), _canonical(item[0])))
    program, replay, predictions = entries[0]
    behavior_hash = hashlib.sha256(
        _canonical([_plain(grid) for grid in predictions]).encode("ascii")
    ).hexdigest()
    corroborating = sorted({entry[0]["trajectory"]["generator"] for entry in entries})
    candidate = {
        "family": "relational_field_automata",
        "program": program,
        "train_outputs": [_plain(grid) for grid in replay],
        "test_outputs": [_plain(grid) for grid in predictions],
        "complexity": int(program["description_length"]),
        "evidence": {
            "all_demonstrations_exact": True,
            "demonstration_count": len(train),
            "test_count": len(tests),
            "behavior_hash": behavior_hash,
            "complete_behavior_quotient": True,
            "unique_test_behavior": True,
            "demo_order_invariance_checked": len(train) > 1,
            "enumeration_signature": order_signature,
            "corroborating_programs": len(entries),
            "corroborating_generators": corroborating,
            "enumerated_programs": len(programs),
            "executor_calls": calls,
            "bounded_search": True,
            "task_identity_free": True,
            "test_outputs_observed": False,
        },
    }
    return [candidate] if bounds.max_candidates else []


__all__ = ["Limits", "SCHEMA", "compile_task", "execute_program", "replay_program"]
