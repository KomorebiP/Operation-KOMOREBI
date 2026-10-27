"""Counterexample-guided relational field automata for PR-LASM Block 14.

This entrant is a new, task-identity-blind field language.  Its bounded
programs model scan-line state propagation, periodic phase continuation,
obstacle-controlled rays, square-locus completion, D4 projection, and
component-graph traversal.  Programs are executable records; compilation
requires exact replay of every demonstration, fresh leave-one-out
re-enumeration, and a single minimum-description behavior on every test
input.  Undefined roles, tied transitions, exhausted bounds, or behavioral
ambiguity abstain.

Only challenge records are accepted.  Test ``output`` members and unrelated
metadata are ignored, and neither task identifiers nor corpus fingerprints
participate in synthesis or execution.

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
Point = tuple[int, int]
Pair = tuple[Grid, Grid]

AUTHOR = "Komorebi P."
SCHEMA = "komorebi.pr_lasm.block14.relational_field_automata.program.v3"
SCAN_SCHEMA = "komorebi.pr_lasm.block14.relational_field_automata.challenge_freeze.v3"


class Undefined(ValueError):
    """A requested role or deterministic transition is not defined."""


@dataclass(frozen=True, slots=True)
class Limits:
    max_grid_cells: int = 900
    max_programs: int = 1_024
    max_evaluations: int = 120_000
    max_ray_steps: int = 3_600
    max_candidates: int = 1
    min_demos: int = 2
    mdl_slack: int = 0
    loo_mdl_slack: int = 0

    @classmethod
    def from_value(cls, value: Any) -> "Limits":
        if isinstance(value, cls):
            return value
        if value is None:
            return cls()
        if not isinstance(value, Mapping):
            raise Undefined("limits must be a mapping")
        defaults = cls()
        ceilings = {
            "max_grid_cells": 3_600,
            "max_programs": 4_096,
            "max_evaluations": 1_000_000,
            "max_ray_steps": 14_400,
            "max_candidates": 1,
            "min_demos": 10,
            "mdl_slack": 2,
            "loo_mdl_slack": 2,
        }
        aliases = {"candidate_cap": "max_candidates"}
        fields: dict[str, int] = {}
        for name in ceilings:
            raw = value.get(name, value.get(next((key for key, target in aliases.items() if target == name), ""), getattr(defaults, name)))
            if isinstance(raw, bool) or not isinstance(raw, int):
                raw = getattr(defaults, name)
            minimum = 0 if name in {"mdl_slack", "loo_mdl_slack"} else 1
            if raw < minimum:
                raw = getattr(defaults, name)
            fields[name] = min(raw, ceilings[name])
        return cls(**fields)


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
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or not value:
        raise Undefined("grid must be a nonempty sequence")
    rows: list[tuple[int, ...]] = []
    width: int | None = None
    for raw_row in value:
        if not isinstance(raw_row, Sequence) or isinstance(raw_row, (str, bytes)) or not raw_row:
            raise Undefined("grid row is invalid")
        row: list[int] = []
        for cell in raw_row:
            if isinstance(cell, bool) or not isinstance(cell, int) or not 0 <= cell <= 9:
                raise Undefined("ARC colors must be integers in [0, 9]")
            row.append(int(cell))
        if width is None:
            width = len(row)
        elif width != len(row):
            raise Undefined("grid is ragged")
        rows.append(tuple(row))
    if len(rows) * int(width or 0) > max_cells:
        raise Undefined("grid exceeds the cell bound")
    return tuple(rows)


def _sanitize(task: Any, limits: Limits) -> tuple[tuple[Pair, ...], tuple[Grid, ...]]:
    if not isinstance(task, Mapping):
        raise Undefined("task must be a mapping")
    raw_train, raw_test = task.get("train"), task.get("test")
    if (
        not isinstance(raw_train, Sequence)
        or isinstance(raw_train, (str, bytes))
        or not raw_train
        or not isinstance(raw_test, Sequence)
        or isinstance(raw_test, (str, bytes))
        or not raw_test
        or len(raw_train) + len(raw_test) > 20
    ):
        raise Undefined("task needs bounded nonempty train and test splits")
    train: list[Pair] = []
    for example in raw_train:
        if not isinstance(example, Mapping):
            raise Undefined("training example is invalid")
        train.append(
            (
                _grid(example.get("input"), limits.max_grid_cells),
                _grid(example.get("output"), limits.max_grid_cells),
            )
        )
    tests: list[Grid] = []
    for example in raw_test:
        if not isinstance(example, Mapping):
            raise Undefined("test example is invalid")
        # Deliberately do not inspect a possible test output member.
        tests.append(_grid(example.get("input"), limits.max_grid_cells))
    return tuple(train), tuple(tests)


def _shape(grid: Grid) -> tuple[int, int]:
    return len(grid), len(grid[0])


def _background(grid: Grid) -> int:
    counts = Counter(cell for row in grid for cell in row)
    maximum = max(counts.values())
    winners = sorted(color for color, count in counts.items() if count == maximum)
    if len(winners) != 1:
        raise Undefined("background mode is tied")
    return winners[0]


def _palette(grid: Grid) -> frozenset[int]:
    return frozenset(cell for row in grid for cell in row)


def _additive_guard(train: Sequence[Pair]) -> bool:
    for source, target in train:
        if _shape(source) != _shape(target) or source == target:
            return False
        try:
            background = _background(source)
        except Undefined:
            return False
        for row in range(len(source)):
            for column in range(len(source[0])):
                before, after = source[row][column], target[row][column]
                if before != after and before != background:
                    return False
    return True


def _components(
    grid: Grid,
    points: Iterable[Point],
    connectivity: int = 4,
    monochrome: bool = True,
) -> list[set[Point]]:
    remaining = set(points)
    offsets = [(-1, 0), (0, -1), (0, 1), (1, 0)]
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
                if point in remaining and (
                    not monochrome or grid[point[0]][point[1]] == grid[row][column]
                ):
                    remaining.remove(point)
                    component.add(point)
                    queue.append(point)
        answer.append(component)
    return sorted(answer, key=lambda item: (min(item), len(item)))


def _bbox(points: Iterable[Point]) -> tuple[int, int, int, int]:
    values = tuple(points)
    if not values:
        raise Undefined("point set is empty")
    return (
        min(row for row, _ in values),
        max(row for row, _ in values),
        min(column for _, column in values),
        max(column for _, column in values),
    )


def _paint(source: Grid, paints: Mapping[Point, int]) -> Grid:
    background = _background(source)
    height, width = _shape(source)
    result = [list(row) for row in source]
    changed = False
    for (row, column), color in sorted(paints.items()):
        if not (0 <= row < height and 0 <= column < width):
            raise Undefined("paint leaves the canvas")
        if isinstance(color, bool) or not isinstance(color, int) or not 0 <= color <= 9:
            raise Undefined("paint color is invalid")
        before = source[row][column]
        if before == background:
            if color == background:
                continue
            result[row][column] = color
            changed = True
        elif before != color:
            raise Undefined("field collides with existing foreground")
    if not changed:
        raise Undefined("field emits no new cell")
    return tuple(tuple(row) for row in result)


def _edge_points(height: int, width: int, edge: str) -> tuple[Point, ...]:
    if edge == "top":
        return tuple((0, column) for column in range(width))
    if edge == "bottom":
        return tuple((height - 1, column) for column in range(width))
    if edge == "left":
        return tuple((row, 0) for row in range(height))
    if edge == "right":
        return tuple((row, width - 1) for row in range(height))
    raise Undefined("unknown edge")


def _orient_top(grid: Grid, edge: str) -> Grid:
    """Map ``edge`` to the top, retaining a reversible rectangular view."""

    if edge == "top":
        return grid
    if edge == "bottom":
        return tuple(reversed(grid))
    if edge == "left":
        return tuple(tuple(grid[row][column] for row in range(len(grid))) for column in range(len(grid[0])))
    if edge == "right":
        return tuple(
            tuple(grid[row][column] for row in range(len(grid)))
            for column in reversed(range(len(grid[0])))
        )
    raise Undefined("unknown edge")


def _restore_top(grid: Grid, edge: str) -> Grid:
    if edge == "top":
        return grid
    if edge == "bottom":
        return tuple(reversed(grid))
    if edge == "left":
        return tuple(tuple(grid[column][row] for column in range(len(grid))) for row in range(len(grid[0])))
    if edge == "right":
        height, width = len(grid[0]), len(grid)
        return tuple(
            tuple(grid[width - 1 - column][row] for column in range(width))
            for row in range(height)
        )
    raise Undefined("unknown edge")


def _full_uniform_rail(grid: Grid) -> tuple[str, int]:
    background = _background(grid)
    height, width = _shape(grid)
    matches: list[tuple[str, int]] = []
    for edge in ("top", "bottom", "left", "right"):
        values = {grid[row][column] for row, column in _edge_points(height, width, edge)}
        if len(values) == 1 and next(iter(values)) != background:
            matches.append((edge, next(iter(values))))
    if len(matches) != 1:
        raise Undefined("uniform boundary rail is absent or ambiguous")
    return matches[0]


def _op_rail_scan_fill(grid: Grid) -> Grid:
    edge, _ = _full_uniform_rail(grid)
    oriented = _orient_top(grid, edge)
    background = _background(oriented)
    height, width = _shape(oriented)
    result = [list(row) for row in oriented]
    changed = False
    # Propagate toward the rail: scan each lane from the far side upward.
    for column in range(width):
        carry: int | None = None
        for row in range(height - 1, 0, -1):
            value = oriented[row][column]
            if value != background:
                carry = value
            elif carry is not None:
                result[row][column] = carry
                changed = True
    if not changed:
        raise Undefined("rail scan emits no cell")
    return _restore_top(tuple(tuple(row) for row in result), edge)


def _op_boundary_gate_fill(grid: Grid, gate_color: int) -> Grid:
    height, width = _shape(grid)
    occurrences = {
        (row, column)
        for row in range(height)
        for column in range(width)
        if grid[row][column] == gate_color
    }
    if len(occurrences) < 1:
        raise Undefined("gate color is absent")
    edges = [
        edge
        for edge in ("top", "bottom", "left", "right")
        if occurrences <= set(_edge_points(height, width, edge))
    ]
    if len(edges) != 1:
        raise Undefined("gate color is not confined to one edge")
    edge = edges[0]
    oriented = _orient_top(grid, edge)
    background = _background(oriented)
    gate_columns = [column for column, value in enumerate(oriented[0]) if value == gate_color]
    if not gate_columns:
        raise Undefined("gate edge contains no gate")
    result = [list(row) for row in oriented]
    changed = False
    for column in gate_columns:
        carry = gate_color
        for row in range(1, len(oriented)):
            value = oriented[row][column]
            if value != background:
                carry = value
            else:
                result[row][column] = carry
                changed = True
    if not changed:
        raise Undefined("gated scan emits no cell")
    return _restore_top(tuple(tuple(row) for row in result), edge)


def _op_periodic_cross(grid: Grid) -> Grid:
    background = _background(grid)
    height, width = _shape(grid)
    points = {(r, c) for r in range(height) for c in range(width) if grid[r][c] != background}
    row_counts = Counter(row for row, _ in points)
    column_counts = Counter(column for _, column in points)
    max_row, max_column = max(row_counts.values()), max(column_counts.values())
    rows = [row for row, count in row_counts.items() if count == max_row]
    columns = [column for column, count in column_counts.items() if count == max_column]
    if len(rows) != 1 or len(columns) != 1:
        raise Undefined("periodic cross axes are ambiguous")
    row, column = rows[0], columns[0]
    horizontal = sorted(c for r, c in points if r == row)
    vertical = sorted(r for r, c in points if c == column)
    if (
        len(horizontal) < 3
        or len(horizontal) != len(vertical)
        or horizontal != list(range(horizontal[0], horizontal[-1] + 1))
        or vertical != list(range(vertical[0], vertical[-1] + 1))
        or points
        != ({(row, c) for c in horizontal} | {(r, column) for r in vertical})
    ):
        raise Undefined("foreground is not one contiguous periodic cross")
    horizontal_values = [grid[row][c] for c in horizontal]
    vertical_values = [grid[r][column] for r in vertical]
    period = len(horizontal)
    paints: dict[Point, int] = {}
    for c in range(width):
        paints[(row, c)] = horizontal_values[(c - horizontal[0]) % period]
    for r in range(height):
        value = vertical_values[(r - vertical[0]) % period]
        previous = paints.get((r, column), value)
        if previous != value:
            raise Undefined("cross phase disagrees at the pivot")
        paints[(r, column)] = value
    return _paint(grid, paints)


def _op_barrier_gap_field(grid: Grid) -> Grid:
    """Fill row gaps around a singleton phase seed and project their core.

    A second foreground color supplies paired (or one-sided) barriers.  Rows
    between the first and last barrier are completed toward the singleton;
    the intersection of the two terminal gaps is continued vertically to the
    canvas boundary.  All roles are selected by multiplicity, not literals.
    """

    background = _background(grid)
    height, width = _shape(grid)
    counts = Counter(
        cell for row in grid for cell in row if cell != background
    )
    if len(counts) != 2:
        raise Undefined("barrier-gap field needs two foreground roles")
    singleton = [color for color, count in counts.items() if count == 1]
    if len(singleton) != 1:
        raise Undefined("barrier-gap phase seed is not unique")
    seed_color = singleton[0]
    barrier_color = next(color for color in counts if color != seed_color)
    seed = next(
        (r, c)
        for r in range(height)
        for c in range(width)
        if grid[r][c] == seed_color
    )
    barrier_rows = sorted(
        row for row in range(height) if barrier_color in grid[row]
    )
    if len(barrier_rows) < 2 or not barrier_rows[0] <= seed[0] <= barrier_rows[-1]:
        raise Undefined("barrier rows do not bracket the phase seed")

    def gap(row: int) -> set[int]:
        columns = [
            column
            for column, value in enumerate(grid[row])
            if value == barrier_color
        ]
        left = [column for column in columns if column < seed[1]]
        right = [column for column in columns if column >= seed[1]]
        lo = max(left) + 1 if left else 0
        hi = min(right) if right else width
        if lo >= hi:
            raise Undefined("row barriers do not expose a gap")
        return set(range(lo, hi))

    top, bottom = barrier_rows[0], barrier_rows[-1]
    paints: dict[Point, int] = {}
    for row in range(top, bottom + 1):
        for column in gap(row):
            paints[(row, column)] = seed_color
    core = gap(top) & gap(bottom)
    if not core:
        raise Undefined("terminal barrier gaps have no common projection")
    for column in core:
        for row in range(height):
            paints[(row, column)] = seed_color
    return _paint(grid, paints)


def _op_fourfold_orbit(grid: Grid) -> Grid:
    background = _background(grid)
    height, width = _shape(grid)
    foreground_by_color: dict[int, set[Point]] = {}
    for row in range(height):
        for column in range(width):
            value = grid[row][column]
            if value != background:
                foreground_by_color.setdefault(value, set()).add((row, column))
    markers: list[tuple[int, Point]] = []
    for color, cells in foreground_by_color.items():
        if len(cells) != 5:
            continue
        for center in cells:
            expected = {center} | {
                (center[0] + dr, center[1] + dc)
                for dr, dc in ((-1, -1), (-1, 1), (1, -1), (1, 1))
            }
            if cells == expected:
                markers.append((color, center))
    if len(markers) != 1:
        raise Undefined("fourfold marker is absent or ambiguous")
    marker_color, (center_row, center_column) = markers[0]
    payload = {
        (row, column)
        for row in range(height)
        for column in range(width)
        if grid[row][column] != background and grid[row][column] != marker_color
    }
    if not payload:
        raise Undefined("fourfold payload is empty")
    paints: dict[Point, int] = {}
    for row, column in payload:
        color = grid[row][column]
        for rr, cc in (
            (row, column),
            (2 * center_row - row, column),
            (row, 2 * center_column - column),
            (2 * center_row - row, 2 * center_column - column),
        ):
            if not (0 <= rr < height and 0 <= cc < width):
                raise Undefined("fourfold orbit leaves the canvas")
            paints[(rr, cc)] = color
    return _paint(grid, paints)


def _op_deflecting_rays(grid: Grid) -> Grid:
    background = _background(grid)
    height, width = _shape(grid)
    candidate_edges: list[str] = []
    for edge in ("top", "bottom", "left", "right"):
        oriented = _orient_top(grid, edge)
        first = oriented[0]
        colors = {value for value in first if value != background}
        if len(colors) != 1 or len(set(first)) < 2:
            continue
        repeated = 1
        while repeated < len(oriented) and oriented[repeated] == first:
            repeated += 1
        if repeated >= 2:
            candidate_edges.append(edge)
    if len(candidate_edges) != 1:
        raise Undefined("repeated ray boundary is absent or ambiguous")
    edge = candidate_edges[0]
    source = _orient_top(grid, edge)
    background = _background(source)
    height, width = _shape(source)
    ray_color = next(value for value in set(source[0]) if value != background)
    source_columns = [column for column, value in enumerate(source[0]) if value == ray_color]
    prefix = 1
    while prefix < height and source[prefix] == source[0]:
        prefix += 1
    if prefix >= height or not any(
        source[row][column] not in {background, ray_color}
        for row in range(prefix, height)
        for column in range(width)
    ):
        raise Undefined("deflecting rays have no obstacle field")

    paints: dict[Point, int] = {}
    occupied_paths: set[Point] = set()
    for initial_column in source_columns:
        row, column = prefix - 1, initial_column
        seen: set[Point] = {(row, column)}
        for _ in range(height * width * 2):
            if row + 1 >= height:
                break
            ahead = source[row + 1][column]
            if ahead in {background, ray_color}:
                row += 1
                if source[row][column] == background:
                    paints[(row, column)] = ray_color
                    occupied_paths.add((row, column))
                continue

            # Find the complete non-background obstacle run on the next row.
            left = right = column
            obstacle_color = ahead
            while left > 0 and source[row + 1][left - 1] == obstacle_color:
                left -= 1
            while right + 1 < width and source[row + 1][right + 1] == obstacle_color:
                right += 1
            doubled = left + right
            if 2 * column < doubled:
                direction = -1
            elif 2 * column > doubled:
                direction = 1
            else:
                left_neighbours = [initial_column - other for other in source_columns if other < initial_column]
                right_neighbours = [other - initial_column for other in source_columns if other > initial_column]
                dl = min(left_neighbours) if left_neighbours else width + 1
                dr = min(right_neighbours) if right_neighbours else width + 1
                # A centered obstacle uses the closest companion ray as a
                # phase cue.  A symmetric companion field has a canonical
                # forward-view successor (right); this is a behavior choice,
                # not an iteration-order accident.
                direction = 1 if dl == dr else (-1 if dl < dr else 1)
            next_column = column + direction
            if not 0 <= next_column < width:
                raise Undefined("ray sidestep leaves the canvas")
            if source[row][next_column] != background or (row, next_column) in occupied_paths:
                raise Undefined("ray sidestep collides")
            column = next_column
            paints[(row, column)] = ray_color
            occupied_paths.add((row, column))
            if (row, column) in seen:
                raise Undefined("ray entered a cycle")
            seen.add((row, column))
        else:
            raise Undefined("ray step bound exhausted")
    result = _paint(source, paints)
    return _restore_top(result, edge)


def _turn_right(direction: Point) -> Point:
    return direction[1], -direction[0]


def _turn_left(direction: Point) -> Point:
    return -direction[1], direction[0]


def _op_turning_ray(
    grid: Grid, start_color: int, right_color: int, left_color: int, max_steps: int
) -> Grid:
    if len({start_color, right_color, left_color}) != 3:
        raise Undefined("turning-ray colors must be distinct")
    height, width = _shape(grid)
    starts = [
        (row, column)
        for row in range(height)
        for column in range(width)
        if grid[row][column] == start_color
    ]
    if len(starts) != 1:
        raise Undefined("turning ray needs one start cell")
    start = starts[0]
    edges = [
        edge
        for edge in ("top", "bottom", "left", "right")
        if start in _edge_points(height, width, edge)
    ]
    if len(edges) != 1:
        raise Undefined("turning-ray start edge is ambiguous")
    direction = {
        "top": (1, 0),
        "bottom": (-1, 0),
        "left": (0, 1),
        "right": (0, -1),
    }[edges[0]]
    background = _background(grid)
    paints: dict[Point, int] = {}
    row, column = start
    seen: set[tuple[int, int, int, int]] = set()
    for _ in range(max_steps):
        state = row, column, direction[0], direction[1]
        if state in seen:
            raise Undefined("turning ray entered a cycle")
        seen.add(state)
        rr, cc = row + direction[0], column + direction[1]
        if not (0 <= rr < height and 0 <= cc < width):
            break
        value = grid[rr][cc]
        if value == background:
            row, column = rr, cc
            paints[(row, column)] = start_color
        elif value == right_color:
            direction = _turn_right(direction)
        elif value == left_color:
            direction = _turn_left(direction)
        else:
            raise Undefined("turning ray met an unknown obstacle")
    else:
        raise Undefined("turning ray step bound exhausted")
    return _paint(grid, paints)


def _solid_square(component: set[Point]) -> tuple[int, int, int] | None:
    top, bottom, left, right = _bbox(component)
    side = bottom - top + 1
    if side != right - left + 1:
        return None
    if component != {(r, c) for r in range(top, bottom + 1) for c in range(left, right + 1)}:
        return None
    return top, left, side


def _separator_locus(grid: Grid) -> tuple[str, int]:
    background = _background(grid)
    height, width = _shape(grid)
    candidates: list[tuple[str, int]] = []
    for row in range(height):
        values = set(grid[row])
        if len(values) == 1 and next(iter(values)) != background:
            candidates.append(("horizontal", row))
    for column in range(width):
        values = {grid[row][column] for row in range(height)}
        if len(values) == 1 and next(iter(values)) != background:
            candidates.append(("vertical", column))
    if height == width:
        main = {grid[index][index] for index in range(height)}
        anti = {grid[index][width - 1 - index] for index in range(height)}
        if len(main) == 1 and next(iter(main)) != background:
            candidates.append(("main_diagonal", 0))
        if len(anti) == 1 and next(iter(anti)) != background:
            candidates.append(("anti_diagonal", height - 1))
    if len(candidates) != 1:
        raise Undefined("separator locus is absent or ambiguous")
    return candidates[0]


def _reflect_point(point: Point, locus: tuple[str, int]) -> Point:
    row, column = point
    kind, offset = locus
    if kind == "horizontal":
        return 2 * offset - row, column
    if kind == "vertical":
        return row, 2 * offset - column
    if kind == "main_diagonal":
        return column, row
    if kind == "anti_diagonal":
        return offset - column, offset - row
    raise Undefined("unknown reflection locus")


def _op_reflect_rarest_across_locus(grid: Grid) -> Grid:
    background = _background(grid)
    locus = _separator_locus(grid)
    height, width = _shape(grid)
    separator = {
        point
        for point in ((r, c) for r in range(height) for c in range(width))
        if _reflect_point(point, locus) == point
    }
    foreground = {
        (r, c)
        for r in range(height)
        for c in range(width)
        if grid[r][c] != background and (r, c) not in separator
    }
    components = _components(grid, foreground, 4, True)
    counts = Counter(grid[row][column] for row, column in foreground)
    minimum = min(counts.values())
    rarest = [color for color, count in counts.items() if count == minimum]
    if len(rarest) != 1:
        raise Undefined("separator payload color is tied")
    selected = [
        component
        for component in components
        if {grid[row][column] for row, column in component} == {rarest[0]}
    ]
    paints: dict[Point, int] = {}
    for component in selected:
        colors = {grid[row][column] for row, column in component}
        if len(colors) != 1:
            raise Undefined("square payload is not monochrome")
        color = next(iter(colors))
        for point in component:
            reflected = _reflect_point(point, locus)
            if not (0 <= reflected[0] < height and 0 <= reflected[1] < width):
                raise Undefined("reflected square leaves the canvas")
            paints[reflected] = color
    return _paint(grid, paints)


def _component_records(grid: Grid) -> list[dict[str, Any]]:
    background = _background(grid)
    points = {
        (r, c)
        for r in range(len(grid))
        for c in range(len(grid[0]))
        if grid[r][c] != background
    }
    records: list[dict[str, Any]] = []
    for component in _components(grid, points, 4, True):
        top, bottom, left, right = _bbox(component)
        colors = {grid[row][column] for row, column in component}
        if len(colors) != 1:
            continue
        records.append(
            {
                "cells": component,
                "color": next(iter(colors)),
                "top": top,
                "bottom": bottom,
                "left": left,
                "right": right,
                "height": bottom - top + 1,
                "width": right - left + 1,
                "solid": len(component) == (bottom - top + 1) * (right - left + 1),
            }
        )
    return records


def _op_greedy_aligned_block_path(grid: Grid, connector_color: int) -> Grid:
    records = [record for record in _component_records(grid) if record["solid"]]
    by_signature: dict[tuple[int, int], list[dict[str, Any]]] = {}
    for record in records:
        by_signature.setdefault((record["height"], record["width"]), []).append(record)
    role_pairs: list[tuple[dict[str, Any], list[dict[str, Any]]]] = []
    for grouped in by_signature.values():
        by_color: dict[int, list[dict[str, Any]]] = {}
        for record in grouped:
            by_color.setdefault(record["color"], []).append(record)
        markers = [items[0] for items in by_color.values() if len(items) == 1]
        node_groups = [items for items in by_color.values() if len(items) >= 2]
        for marker in markers:
            for nodes in node_groups:
                role_pairs.append((marker, nodes))
    if len(role_pairs) != 1:
        raise Undefined("block-path marker/node roles are ambiguous")
    current, nodes = role_pairs[0]
    unvisited = list(nodes)
    paints: dict[Point, int] = {}
    edges = 0
    while True:
        choices: list[tuple[int, tuple[int, int], dict[str, Any]]] = []
        background = _background(grid)
        for node in unvisited:
            if current["top"] == node["top"] and current["height"] == node["height"]:
                if node["left"] > current["right"]:
                    gap = node["left"] - current["right"] - 1
                elif current["left"] > node["right"]:
                    gap = current["left"] - node["right"] - 1
                else:
                    continue
                lane_left = min(current["right"], node["right"]) + 1
                lane_right = max(current["left"], node["left"]) - 1
                if any(
                    grid[row][column] != background
                    for row in range(current["top"], current["bottom"] + 1)
                    for column in range(lane_left, lane_right + 1)
                ):
                    continue
                choices.append((gap, (node["top"], node["left"]), node))
            elif current["left"] == node["left"] and current["width"] == node["width"]:
                if node["top"] > current["bottom"]:
                    gap = node["top"] - current["bottom"] - 1
                elif current["top"] > node["bottom"]:
                    gap = current["top"] - node["bottom"] - 1
                else:
                    continue
                lane_top = min(current["bottom"], node["bottom"]) + 1
                lane_bottom = max(current["top"], node["top"]) - 1
                if any(
                    grid[row][column] != background
                    for row in range(lane_top, lane_bottom + 1)
                    for column in range(current["left"], current["right"] + 1)
                ):
                    continue
                choices.append((gap, (node["top"], node["left"]), node))
        if not choices:
            break
        best_gap = min(gap for gap, _, _ in choices)
        best = [entry for entry in choices if entry[0] == best_gap]
        if len(best) != 1:
            raise Undefined("greedy block-path successor is tied")
        node = best[0][2]
        if current["top"] == node["top"]:
            left = min(current["right"], node["right"]) + 1
            right = max(current["left"], node["left"]) - 1
            for row in range(current["top"], current["bottom"] + 1):
                for column in range(left, right + 1):
                    paints[(row, column)] = connector_color
        else:
            top = min(current["bottom"], node["bottom"]) + 1
            bottom = max(current["top"], node["top"]) - 1
            for row in range(top, bottom + 1):
                for column in range(current["left"], current["right"] + 1):
                    paints[(row, column)] = connector_color
        edges += 1
        unvisited.remove(node)
        current = node
    if edges < 1:
        raise Undefined("block path has no aligned successor")
    return _paint(grid, paints)


def _square_components_for_color(grid: Grid, color: int) -> list[tuple[set[Point], tuple[int, int, int]]]:
    points = {
        (r, c)
        for r in range(len(grid))
        for c in range(len(grid[0]))
        if grid[r][c] == color
    }
    answer: list[tuple[set[Point], tuple[int, int, int]]] = []
    for component in _components(grid, points, 4, True):
        spec = _solid_square(component)
        if spec is None:
            return []
        answer.append((component, spec))
    return answer


def _op_complete_square_vertices(grid: Grid, emission_color: int) -> Grid:
    background = _background(grid)
    colors = sorted(_palette(grid) - {background})
    possible: list[list[tuple[set[Point], tuple[int, int, int]]]] = []
    for color in colors:
        components = _square_components_for_color(grid, color)
        if len(components) >= 2 and len(components) % 2 == 0:
            sizes = {spec[2] for _, spec in components}
            if len(sizes) == 1:
                possible.append(components)
    if len(possible) != 1:
        raise Undefined("square-vertex source role is ambiguous")
    remaining = list(possible[0])
    pairs: list[tuple[tuple[int, int, int], tuple[int, int, int]]] = []
    while remaining:
        first = remaining[0]
        first_center = (2 * first[1][0] + first[1][2] - 1, 2 * first[1][1] + first[1][2] - 1)
        distances: list[tuple[int, int]] = []
        for index, other in enumerate(remaining[1:], start=1):
            other_center = (2 * other[1][0] + other[1][2] - 1, 2 * other[1][1] + other[1][2] - 1)
            dr, dc = other_center[0] - first_center[0], other_center[1] - first_center[1]
            if abs(dr) == abs(dc) and dr:
                distances.append((dr * dr + dc * dc, index))
        if not distances:
            raise Undefined("square vertices have no diagonal mate")
        minimum = min(distance for distance, _ in distances)
        nearest = [index for distance, index in distances if distance == minimum]
        if len(nearest) != 1:
            raise Undefined("square-vertex pairing is tied")
        second = remaining[nearest[0]]
        pairs.append((first[1], second[1]))
        remaining.pop(nearest[0])
        remaining.pop(0)

    height, width = _shape(grid)
    paints: dict[Point, int] = {}
    for first, second in pairs:
        side = first[2]
        a = (2 * first[0] + side - 1, 2 * first[1] + side - 1)
        b = (2 * second[0] + side - 1, 2 * second[1] + side - 1)
        delta = b[0] - a[0], b[1] - a[1]
        numerators = (
            (a[0] + b[0] - 3 * delta[1], a[1] + b[1] + 3 * delta[0]),
            (a[0] + b[0] + 3 * delta[1], a[1] + b[1] - 3 * delta[0]),
        )
        for nr, nc in numerators:
            if nr % 2 or nc % 2:
                raise Undefined("rotated square center is off lattice")
            center = nr // 2, nc // 2
            if (center[0] - side + 1) % 2 or (center[1] - side + 1) % 2:
                raise Undefined("rotated square placement is off lattice")
            top = (center[0] - side + 1) // 2
            left = (center[1] - side + 1) // 2
            visible = 0
            for row in range(top, top + side):
                for column in range(left, left + side):
                    if 0 <= row < height and 0 <= column < width:
                        paints[(row, column)] = emission_color
                        visible += 1
            if not visible:
                raise Undefined("completed square vertex is wholly outside the canvas")
    return _paint(grid, paints)


def _op_diagonal_stair_wave(grid: Grid, emission_color: int, chirality: int) -> Grid:
    background = _background(grid)
    seeds = [
        (row, column)
        for row in range(len(grid))
        for column in range(len(grid[0]))
        if grid[row][column] != background
    ]
    if len(seeds) != 1 or chirality not in {-1, 1}:
        raise Undefined("stair wave needs one seed and a valid chirality")
    height, width = _shape(grid)
    paints: dict[Point, int] = {}
    for vertical in (-1, 1):
        row, column = seeds[0]
        horizontal = -vertical * chirality
        while True:
            row += vertical
            if not (0 <= row < height and 0 <= column < width):
                break
            paints[(row, column)] = emission_color
            row += vertical
            if not (0 <= row < height and 0 <= column < width):
                break
            paints[(row, column)] = emission_color
            for _ in range(2):
                column += horizontal
                if not (0 <= row < height and 0 <= column < width):
                    break
                paints[(row, column)] = emission_color
            if not (0 <= row < height and 0 <= column < width):
                break
    return _paint(grid, paints)


def _program(op: str, complexity: int, **parameters: Any) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "op": op,
        "parameters": json.loads(_canonical(parameters)),
        "description_length": int(complexity),
    }


def _enumerate_programs(train: Sequence[Pair]) -> tuple[dict[str, Any], ...]:
    programs: list[dict[str, Any]] = [
        _program("rail_scan_fill", 6),
        _program("periodic_cross", 7),
        _program("barrier_gap_field", 8),
        _program("fourfold_orbit", 8),
        _program("deflecting_rays", 9),
        _program("reflect_rarest_across_locus", 9),
    ]
    for color in range(10):
        programs.append(_program("boundary_gate_fill", 7, gate_color=color))
        programs.append(_program("greedy_aligned_block_path", 10, connector_color=color))
        programs.append(_program("complete_square_vertices", 9, emission_color=color))
        for chirality in (-1, 1):
            programs.append(
                _program(
                    "diagonal_stair_wave",
                    9,
                    emission_color=color,
                    chirality=chirality,
                )
            )
    # Turning colors are bounded by the observed *input* palette.  LOO below
    # performs this enumeration afresh on each proper training subset.
    colors = sorted(set().union(*(_palette(source) for source, _ in train)))
    for start_color, right_color, left_color in itertools.permutations(colors, 3):
        programs.append(
            _program(
                "turning_ray",
                11,
                start_color=start_color,
                right_color=right_color,
                left_color=left_color,
            )
        )
    unique = {_canonical(program): program for program in programs}
    return tuple(unique[key] for key in sorted(unique))


def _execute(program: Mapping[str, Any], grid: Grid, limits: Limits) -> Grid:
    if not isinstance(program, Mapping) or program.get("schema") != SCHEMA:
        raise Undefined("program schema is invalid")
    op = program.get("op")
    parameters = program.get("parameters")
    if not isinstance(op, str) or not isinstance(parameters, Mapping):
        raise Undefined("program record is invalid")
    if op == "rail_scan_fill":
        return _op_rail_scan_fill(grid)
    if op == "boundary_gate_fill":
        return _op_boundary_gate_fill(grid, int(parameters["gate_color"]))
    if op == "periodic_cross":
        return _op_periodic_cross(grid)
    if op == "barrier_gap_field":
        return _op_barrier_gap_field(grid)
    if op == "fourfold_orbit":
        return _op_fourfold_orbit(grid)
    if op == "deflecting_rays":
        return _op_deflecting_rays(grid)
    if op == "turning_ray":
        return _op_turning_ray(
            grid,
            int(parameters["start_color"]),
            int(parameters["right_color"]),
            int(parameters["left_color"]),
            limits.max_ray_steps,
        )
    if op == "reflect_rarest_across_locus":
        return _op_reflect_rarest_across_locus(grid)
    if op == "greedy_aligned_block_path":
        return _op_greedy_aligned_block_path(grid, int(parameters["connector_color"]))
    if op == "complete_square_vertices":
        return _op_complete_square_vertices(grid, int(parameters["emission_color"]))
    if op == "diagonal_stair_wave":
        return _op_diagonal_stair_wave(
            grid,
            int(parameters["emission_color"]),
            int(parameters["chirality"]),
        )
    raise Undefined("unknown field operation")


def execute_program(
    program: Mapping[str, Any], value: Any, limits: Mapping[str, Any] | Limits | None = None
) -> list[list[int]]:
    bounds = Limits.from_value(limits)
    grid = _grid(value, bounds.max_grid_cells)
    return _plain(_execute(program, grid, bounds))


def replay_program(program: Mapping[str, Any], value: Any) -> dict[str, Any]:
    source = _plain(_grid(value, Limits().max_grid_cells))
    output = execute_program(program, source)
    return {
        "output": output,
        "stages": [
            {"name": "parse_relational_field", "input": source, "output": source},
            {
                "name": f"execute_field:{program.get('op', 'unknown')}",
                "input": source,
                "output": output,
            },
        ],
    }


@dataclass(frozen=True, slots=True)
class Evaluation:
    program: Mapping[str, Any]
    complexity: int
    train_outputs: tuple[Grid | None, ...]
    test_outputs: tuple[Grid | None, ...]


def _evaluate(
    program: Mapping[str, Any],
    train: Sequence[Pair],
    tests: Sequence[Grid],
    limits: Limits,
) -> Evaluation:
    train_outputs: list[Grid | None] = []
    test_outputs: list[Grid | None] = []
    for source, _ in train:
        try:
            train_outputs.append(_execute(program, source, limits))
        except (Undefined, KeyError, TypeError, ValueError, IndexError):
            train_outputs.append(None)
    for source in tests:
        try:
            test_outputs.append(_execute(program, source, limits))
        except (Undefined, KeyError, TypeError, ValueError, IndexError):
            test_outputs.append(None)
    return Evaluation(
        program=program,
        complexity=int(program["description_length"]),
        train_outputs=tuple(train_outputs),
        test_outputs=tuple(test_outputs),
    )


def _fresh_loo(
    train: Sequence[Pair], limits: Limits
) -> tuple[bool, int, tuple[str, ...]]:
    if len(train) < 2:
        return False, 0, ()
    checked = 0
    signatures: list[str] = []
    for held_index, (held_source, held_target) in enumerate(train):
        subset = tuple(pair for index, pair in enumerate(train) if index != held_index)
        programs = _enumerate_programs(subset)
        if len(programs) > limits.max_programs:
            return False, checked, tuple(signatures)
        signatures.append(_digest(programs))
        evaluations = [_evaluate(program, subset, (held_source,), limits) for program in programs]
        subset_targets = tuple(target for _, target in subset)
        fits = [
            evaluation
            for evaluation in evaluations
            if evaluation.train_outputs == subset_targets and evaluation.test_outputs[0] is not None
        ]
        if not fits:
            return False, checked, tuple(signatures)
        best = min(evaluation.complexity for evaluation in fits)
        near = [
            evaluation
            for evaluation in fits
            if evaluation.complexity <= best + limits.loo_mdl_slack
        ]
        predictions = {evaluation.test_outputs[0] for evaluation in near}
        checked += len(near)
        if predictions != {held_target}:
            return False, checked, tuple(signatures)
    return True, checked, tuple(signatures)


def compile_task(
    task: Any, limits: Mapping[str, Any] | Limits | None = None
) -> list[dict[str, Any]]:
    """Compile one behaviorally unambiguous, fresh-LOO-stable field program."""

    try:
        bounds = Limits.from_value(limits)
        train, tests = _sanitize(task, bounds)
    except (Undefined, KeyError, TypeError, ValueError):
        return []
    if len(train) < bounds.min_demos or not _additive_guard(train):
        return []
    programs = _enumerate_programs(train)
    if len(programs) > bounds.max_programs:
        return []
    if len(train) > 1 and _digest(programs) != _digest(_enumerate_programs(tuple(reversed(train)))):
        return []
    required = len(programs) * (len(train) + len(tests))
    if required > bounds.max_evaluations:
        return []
    evaluations = [_evaluate(program, train, tests, bounds) for program in programs]
    targets = tuple(target for _, target in train)
    exact = [
        evaluation
        for evaluation in evaluations
        if evaluation.train_outputs == targets and None not in evaluation.test_outputs
    ]
    if not exact:
        return []
    stable, loo_checked, loo_signatures = _fresh_loo(train, bounds)
    if not stable:
        return []
    best = min(evaluation.complexity for evaluation in exact)
    near = [
        evaluation
        for evaluation in exact
        if evaluation.complexity <= best + bounds.mdl_slack
    ]
    behaviors: dict[str, list[Evaluation]] = {}
    for evaluation in near:
        behavior = [_plain(output) for output in evaluation.test_outputs if output is not None]
        behaviors.setdefault(_digest(behavior), []).append(evaluation)
    if len(behaviors) != 1:
        return []
    behavior_hash, equivalent = next(iter(sorted(behaviors.items())))
    equivalent.sort(key=lambda evaluation: (evaluation.complexity, _canonical(evaluation.program)))
    representative = equivalent[0]
    candidate = {
        "family": "relational_field_automata_v3",
        "program": json.loads(_canonical(representative.program)),
        "train_outputs": [_plain(output) for output in representative.train_outputs if output is not None],
        "test_outputs": [_plain(output) for output in representative.test_outputs if output is not None],
        "complexity": representative.complexity,
        "evidence": {
            "all_demonstrations_exact": True,
            "exact_replay": True,
            "bounded_enumeration_complete": True,
            "enumerated_programs": len(programs),
            "program_evaluations": required,
            "exact_programs": len(exact),
            "minimum_description_programs": len(near),
            "test_behavior_classes": 1,
            "behavior_hash": behavior_hash,
            "fresh_leave_one_out_rediscovery": True,
            "leave_one_out_programs_checked": loo_checked,
            "leave_one_out_enumeration_signatures": list(loo_signatures),
            "demo_order_invariance_checked": len(train) > 1,
            "task_identity_observed": False,
            "test_labels_observed": False,
        },
    }
    candidate["evidence"]["candidate_semantic_hash"] = _digest(candidate)
    return [candidate][: bounds.max_candidates]


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
    limits: Mapping[str, Any] | Limits | None = None,
    source_hash: str | None = None,
    run_name: str = "relational-field-automata-v3-freeze",
) -> dict[str, Any]:
    records: dict[str, Any] = {}
    operation_counts: Counter[str] = Counter()
    predicted_outputs = 0
    for raw_task_id, raw_task in sorted(challenges.items(), key=lambda item: str(item[0])):
        task = _safe_task(raw_task)
        candidates = compile_task(task, limits)
        if len(candidates) > 1:
            raise AssertionError("one-candidate contract violated")
        if candidates:
            candidate = candidates[0]
            operation_counts[str(candidate["program"]["op"])] += 1
            predicted_outputs += len(candidate["test_outputs"])
        record = {
            "task_semantic_hash": _digest(task),
            "status": "candidate" if candidates else "abstention",
            "candidates": candidates,
        }
        record["content_hash"] = _digest(record)
        records[str(raw_task_id)] = record
    body: dict[str, Any] = {
        "schema": SCAN_SCHEMA,
        "schema_version": 3,
        "author": AUTHOR,
        "claim_boundary": "challenge-only exact-demo predictions; no held-out scoring",
        "run_name": run_name,
        "source_hash": source_hash,
        "source_task_count": len(challenges),
        "activation_count": sum(record["status"] == "candidate" for record in records.values()),
        "predicted_output_count": predicted_outputs,
        "operation_counts": dict(sorted(operation_counts.items())),
        "label_access": "none",
        "task_identity_usage": "record-key only after compilation",
        "records": records,
    }
    body["content_hash"] = _digest(body)
    return body


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".partial")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    temporary.replace(path)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--challenges", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--run-name", default="relational-field-automata-v3-freeze")
    args = parser.parse_args(argv)
    challenges_path = args.challenges.resolve()
    source_path = Path(__file__).resolve()
    challenges = json.loads(challenges_path.read_text(encoding="utf-8-sig"))
    if not isinstance(challenges, Mapping) or not challenges:
        raise SystemExit("challenge collection is invalid")
    source_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
    frozen = freeze_scan(
        challenges,
        source_hash=source_hash,
        run_name=args.run_name,
    )
    frozen["challenges_file"] = challenges_path.name
    frozen["challenges_sha256"] = hashlib.sha256(challenges_path.read_bytes()).hexdigest()
    frozen["entrant_file"] = source_path.name
    frozen["entrant_sha256"] = source_hash
    frozen["content_hash"] = _digest({key: value for key, value in frozen.items() if key != "content_hash"})
    _write_json(args.output.resolve(), frozen)
    print(
        _canonical(
            {
                "activation_count": frozen["activation_count"],
                "content_hash": frozen["content_hash"],
                "entrant_sha256": source_hash,
                "predicted_output_count": frozen["predicted_output_count"],
                "source_task_count": frozen["source_task_count"],
            }
        )
    )
    return 0


__all__ = [
    "AUTHOR",
    "Limits",
    "SCAN_SCHEMA",
    "SCHEMA",
    "Undefined",
    "compile_task",
    "execute_program",
    "freeze_scan",
    "replay_program",
]


if __name__ == "__main__":
    raise SystemExit(main())
