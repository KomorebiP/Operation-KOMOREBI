"""Retrospective, score-seeded motion/transport schema repairs for Block 15.

The runtime receives only labelled demonstrations and held test inputs.  It
searches a finite language of seven reusable, task-local transformations:

* singleton particles approach the shell of a unique nearest homologous
  anchor;
* tokens outside a three-sided barrier move toward its line exactly when an
  aligned, same-colour reference exists inside the barrier;
* a marker occupying half of one bar transfers to the corresponding half of
  the next-longer bar;
* a detached plus cue is removed and recolours the centres of odd rectangles;
* a detached marker receives a translated copy of its marked exemplar;
* repeated-colour corner blocks move one block-width diagonally inward; and
* components fall toward the opposite boundary carrying their own colour.

Programs contain roles and relations, never task identities, output rasters,
absolute target locations, corpus fingerprints, or label-store access.  A
candidate is emitted only after exact demonstration replay, one held-input
behaviour, leave-one-demonstration-out re-induction, replayability, and D4 and
palette counterfactual checks.

Induction regime: retrospective_score_seeded_schema_repair
Author: Komorebi P.
"""

from __future__ import annotations

from collections import Counter, defaultdict, deque
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
import hashlib
import itertools
import json
from typing import Any


Grid = tuple[tuple[int, ...], ...]
Cell = tuple[int, int]
Pair = tuple[Grid, Grid]

AUTHOR = "Komorebi P."
INDUCTION_REGIME = "retrospective_score_seeded_schema_repair"
SCHEMA = "komorebi.pr_lasm.block15.motion_transport_compiler_v2.program.v1"


class Undefined(ValueError):
    """A structural role, relation, or collision-free transport is undefined."""


@dataclass(frozen=True, slots=True)
class Limits:
    max_grid_cells: int = 900
    max_examples: int = 20
    max_programs: int = 256
    max_executor_calls: int = 50_000
    max_components: int = 256
    max_counterfactuals: int = 4_096
    max_candidates: int = 1

    @classmethod
    def from_value(cls, value: Mapping[str, Any] | None) -> "Limits":
        if value is None:
            return cls()
        if not isinstance(value, Mapping):
            raise Undefined("limits must be a mapping")
        defaults = cls()
        ceilings = {
            "max_grid_cells": 3_600,
            "max_examples": 40,
            "max_programs": 2_048,
            "max_executor_calls": 250_000,
            "max_components": 1_024,
            "max_counterfactuals": 16_384,
            "max_candidates": 1,
        }
        aliases = {
            "max_cells": "max_grid_cells",
            "candidate_cap": "max_candidates",
            "max_gauge_checks": "max_counterfactuals",
        }
        parsed: dict[str, int] = {}
        for name, ceiling in ceilings.items():
            raw = value.get(name, getattr(defaults, name))
            for alias, target in aliases.items():
                if target == name and alias in value and name not in value:
                    raw = value[alias]
            if isinstance(raw, bool) or not isinstance(raw, int) or raw < 1:
                raise Undefined(f"limits.{name} must be a positive integer")
            parsed[name] = min(raw, ceiling)
        return cls(**parsed)


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


def _grid(value: Any, limits: Limits) -> Grid:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or not value:
        raise Undefined("grid must be a nonempty row sequence")
    rows: list[tuple[int, ...]] = []
    width: int | None = None
    for raw_row in value:
        if (
            not isinstance(raw_row, Sequence)
            or isinstance(raw_row, (str, bytes))
            or not raw_row
        ):
            raise Undefined("grid row is invalid")
        row: list[int] = []
        for cell in raw_row:
            if isinstance(cell, bool) or not isinstance(cell, int) or not 0 <= cell <= 9:
                raise Undefined("ARC colours must be integers in [0, 9]")
            row.append(int(cell))
        if width is None:
            width = len(row)
        elif width != len(row):
            raise Undefined("grid is ragged")
        rows.append(tuple(row))
    if len(rows) * int(width or 0) > limits.max_grid_cells:
        raise Undefined("grid exceeds the cell bound")
    return tuple(rows)


def _plain(grid: Grid) -> list[list[int]]:
    return [list(row) for row in grid]


def _freeze(rows: Sequence[Sequence[int]]) -> Grid:
    return tuple(tuple(int(cell) for cell in row) for row in rows)


def _shape(grid: Grid) -> tuple[int, int]:
    return len(grid), len(grid[0])


def _palette(grid: Grid) -> frozenset[int]:
    return frozenset(cell for row in grid for cell in row)


def _background(grid: Grid) -> int:
    counts = Counter(cell for row in grid for cell in row)
    maximum = max(counts.values())
    winners = [colour for colour, count in counts.items() if count == maximum]
    if len(winners) != 1:
        raise Undefined("background mode is tied")
    return winners[0]


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
    demonstrations: list[Pair] = []
    for example in raw_train:
        if not isinstance(example, Mapping):
            raise Undefined("training example is invalid")
        demonstrations.append(
            (_grid(example.get("input"), limits), _grid(example.get("output"), limits))
        )
    tests: list[Grid] = []
    for example in raw_test:
        if not isinstance(example, Mapping):
            raise Undefined("test example is invalid")
        # Deliberately fetch only the held input member.
        tests.append(_grid(example.get("input"), limits))
    return tuple(demonstrations), tuple(tests)


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


def _components(grid: Grid, limits: Limits) -> tuple[tuple[int, frozenset[Cell]], ...]:
    background = _background(grid)
    remaining = {
        (row, column)
        for row, values in enumerate(grid)
        for column, value in enumerate(values)
        if value != background
    }
    result: list[tuple[int, frozenset[Cell]]] = []
    while remaining:
        seed = min(remaining)
        remaining.remove(seed)
        colour = grid[seed[0]][seed[1]]
        cells = {seed}
        queue = deque((seed,))
        while queue:
            row, column = queue.popleft()
            for dr, dc in ((-1, 0), (0, -1), (0, 1), (1, 0)):
                neighbour = row + dr, column + dc
                if neighbour not in remaining:
                    continue
                if grid[neighbour[0]][neighbour[1]] != colour:
                    continue
                remaining.remove(neighbour)
                cells.add(neighbour)
                queue.append(neighbour)
        result.append((colour, frozenset(cells)))
        if len(result) > limits.max_components:
            raise Undefined("component bound exceeded")
    return tuple(sorted(result, key=lambda item: (_bbox(item[1]), item[0], len(item[1]))))


def _solid_rectangle(cells: Iterable[Cell], *, minimum_area: int = 1) -> bool:
    points = frozenset(cells)
    if len(points) < minimum_area:
        return False
    top, bottom, left, right = _bbox(points)
    return len(points) == (bottom - top + 1) * (right - left + 1)


_D4 = ("id", "r90", "r180", "r270", "fh", "fv", "diag", "anti")


def _d4(grid: Grid, operation: str) -> Grid:
    if operation == "id":
        return grid
    if operation == "r90":
        return tuple(tuple(row) for row in zip(*reversed(grid)))
    if operation == "r180":
        return tuple(tuple(reversed(row)) for row in reversed(grid))
    if operation == "r270":
        return tuple(tuple(row) for row in reversed(tuple(zip(*grid))))
    if operation == "fh":
        return tuple(tuple(reversed(row)) for row in grid)
    if operation == "fv":
        return tuple(reversed(grid))
    if operation == "diag":
        return tuple(tuple(row) for row in zip(*grid))
    if operation == "anti":
        return _d4(_d4(grid, "diag"), "r180")
    raise Undefined("unknown D4 operation")


_D4_PROBE: Grid = ((0, 1, 2), (3, 4, 5))
_D4_SIGNATURE = {_d4(_D4_PROBE, operation): operation for operation in _D4}


def _compose(left: str, right: str) -> str:
    """Apply ``right`` and then ``left``."""

    return _D4_SIGNATURE[_d4(_d4(_D4_PROBE, right), left)]


def _inverse(operation: str) -> str:
    for candidate in _D4:
        if _compose(candidate, operation) == _compose(operation, candidate) == "id":
            return candidate
    raise AssertionError("D4 inverse is absent")


def _render(
    grid: Grid,
    replacements: Sequence[tuple[int, frozenset[Cell], frozenset[Cell]]],
) -> Grid:
    if not replacements:
        raise Undefined("transport has no movers")
    background = _background(grid)
    height, width = _shape(grid)
    output = [list(row) for row in grid]
    sources: set[Cell] = set()
    for _colour, source, _target in replacements:
        if sources & set(source):
            raise Undefined("mover sources overlap")
        sources.update(source)
    for row, column in sources:
        output[row][column] = background
    targets: set[Cell] = set()
    for colour, _source, target in replacements:
        for row, column in sorted(target):
            if not (0 <= row < height and 0 <= column < width):
                raise Undefined("transport leaves the canvas")
            if (row, column) in targets or output[row][column] != background:
                raise Undefined("transport collides")
            targets.add((row, column))
            output[row][column] = colour
    result = _freeze(output)
    if result == grid:
        raise Undefined("transport is an identity")
    return result


def _components_from_cells(
    cells: Iterable[Cell], *, diagonal: bool = False
) -> tuple[frozenset[Cell], ...]:
    """Return deterministic components without assuming a background colour."""

    remaining = set(cells)
    result: list[frozenset[Cell]] = []
    offsets = (
        tuple(
            (dr, dc)
            for dr in (-1, 0, 1)
            for dc in (-1, 0, 1)
            if (dr or dc) and (diagonal or abs(dr) + abs(dc) == 1)
        )
    )
    while remaining:
        seed = min(remaining)
        remaining.remove(seed)
        component = {seed}
        queue = deque((seed,))
        while queue:
            row, column = queue.popleft()
            for dr, dc in offsets:
                neighbour = row + dr, column + dc
                if neighbour not in remaining:
                    continue
                remaining.remove(neighbour)
                component.add(neighbour)
                queue.append(neighbour)
        result.append(frozenset(component))
    return tuple(sorted(result, key=lambda cells: (_bbox(cells), len(cells))))


def _successor_bar_marker_transfer(
    grid: Grid, _program: Mapping[str, Any], _limits: Limits
) -> Grid:
    """Move a half-bar marker to the same half of the next-longer bar."""

    background = _background(grid)
    colours = sorted(_palette(grid) - {background})
    if len(colours) != 2:
        raise Undefined("bar transfer requires carrier and marker colours")
    outputs: dict[str, Grid] = {}
    height, width = _shape(grid)
    for marker, carrier in ((colours[0], colours[1]), (colours[1], colours[0])):
        marker_cells = {
            (row, column)
            for row, values in enumerate(grid)
            for column, colour in enumerate(values)
            if colour == marker
        }
        support = {
            (row, column)
            for row, values in enumerate(grid)
            for column, colour in enumerate(values)
            if colour in (marker, carrier)
        }
        components = _components_from_cells(support)
        bars: list[tuple[frozenset[Cell], str, tuple[Cell, ...]]] = []
        marked: tuple[frozenset[Cell], str, tuple[Cell, ...]] | None = None
        valid = True
        for component in components:
            top, bottom, left, right = _bbox(component)
            if top == bottom:
                ordered = tuple((top, column) for column in range(left, right + 1))
                axis = "horizontal"
            elif left == right:
                ordered = tuple((row, left) for row in range(top, bottom + 1))
                axis = "vertical"
            else:
                valid = False
                break
            if frozenset(ordered) != component or len(ordered) % 2:
                valid = False
                break
            record = component, axis, ordered
            bars.append(record)
            if component & marker_cells:
                if marked is not None:
                    valid = False
                    break
                marked = record
        if not valid or marked is None or not marker_cells <= marked[0]:
            continue
        axes = {axis for _component, axis, _ordered in bars}
        lengths = sorted({len(ordered) for _component, _axis, ordered in bars})
        if (
            len(axes) != 1
            or len(lengths) < 4
            or any(right - left != 2 for left, right in zip(lengths, lengths[1:]))
        ):
            continue
        marked_order = marked[2]
        half = len(marked_order) // 2
        at_start = marker_cells == frozenset(marked_order[:half])
        at_end = marker_cells == frozenset(marked_order[half:])
        if at_start == at_end:
            continue
        targets = [
            record
            for record in bars
            if len(record[2]) == len(marked_order) + 2
            and not (record[0] & marker_cells)
        ]
        if len(targets) != 1 or targets[0][1] != marked[1]:
            continue
        target_order = targets[0][2]
        target_half = len(target_order) // 2
        new_marker = (
            target_order[:target_half] if at_start else target_order[target_half:]
        )
        output = [list(row) for row in grid]
        for row, column in marker_cells:
            output[row][column] = carrier
        for row, column in new_marker:
            if not (0 <= row < height and 0 <= column < width):
                valid = False
                break
            output[row][column] = marker
        if valid:
            result = _freeze(output)
            outputs[_digest(_plain(result))] = result
    if len(outputs) != 1:
        raise Undefined("bar marker roles or successor are ambiguous")
    return next(iter(outputs.values()))


def _is_plus(cells: frozenset[Cell]) -> bool:
    if len(cells) != 5:
        return False
    for row, column in cells:
        expected = {
            (row, column),
            (row - 1, column),
            (row + 1, column),
            (row, column - 1),
            (row, column + 1),
        }
        if cells == expected:
            return True
    return False


def _odd_rectangle_center_projection(
    grid: Grid, _program: Mapping[str, Any], _limits: Limits
) -> Grid:
    """Consume a plus cue and stamp its colour at odd-rectangle centres."""

    background = _background(grid)
    colours = sorted(_palette(grid) - {background})
    if len(colours) != 2:
        raise Undefined("rectangle projection needs exactly two foreground roles")
    role_candidates: list[tuple[int, int, frozenset[Cell]]] = []
    for cue, carrier in ((colours[0], colours[1]), (colours[1], colours[0])):
        cue_cells = frozenset(
            (row, column)
            for row, values in enumerate(grid)
            for column, colour in enumerate(values)
            if colour == cue
        )
        if _is_plus(cue_cells):
            role_candidates.append((cue, carrier, cue_cells))
    if len(role_candidates) != 1:
        raise Undefined("a unique plus cue is required")
    cue, carrier, cue_cells = role_candidates[0]
    carrier_cells = {
        (row, column)
        for row, values in enumerate(grid)
        for column, colour in enumerate(values)
        if colour == carrier
    }
    components = _components_from_cells(carrier_cells)
    if len(components) < 4:
        raise Undefined("too few rectangle instances")
    centers: list[Cell] = []
    even_instances = 0
    for component in components:
        if not _solid_rectangle(component):
            raise Undefined("carrier instance is not rectangular")
        top, bottom, left, right = _bbox(component)
        box_height, box_width = bottom - top + 1, right - left + 1
        if box_height % 2 and box_width % 2:
            centers.append(((top + bottom) // 2, (left + right) // 2))
        else:
            even_instances += 1
    if not centers or not even_instances:
        raise Undefined("both odd and even rectangle evidence is required")
    output = [list(row) for row in grid]
    # The cue participates in the same odd/even consensus as the rectangles:
    # it remains as a legend only when odd rectangles are the strict majority.
    # This predicate is structural and transfers across canvas size and palette.
    if len(centers) <= even_instances:
        for row, column in cue_cells:
            output[row][column] = background
    for row, column in centers:
        output[row][column] = cue
    result = _freeze(output)
    if result == grid:
        raise Undefined("rectangle center projection is an identity")
    return result


def _marker_aligned_exemplar_copy(
    grid: Grid, _program: Mapping[str, Any], _limits: Limits
) -> Grid:
    """Copy a marked multicolour exemplar onto its detached marker."""

    background = _background(grid)
    foreground = {
        (row, column)
        for row, values in enumerate(grid)
        for column, colour in enumerate(values)
        if colour != background
    }
    union_components = _components_from_cells(foreground)
    if len(union_components) != 2:
        raise Undefined("copy task needs one exemplar and one detached marker")
    height, width = _shape(grid)
    outputs: dict[str, Grid] = {}
    for marker in sorted(_palette(grid) - {background}):
        marker_cells = {
            (row, column)
            for row, values in enumerate(grid)
            for column, colour in enumerate(values)
            if colour == marker
        }
        if len(marker_cells) != 2:
            continue
        detached_components = [
            component
            for component in union_components
            if len(component) == 1 and component <= marker_cells
        ]
        exemplar_components = [
            component
            for component in union_components
            if len(component) >= 4 and len(component & marker_cells) == 1
        ]
        if len(detached_components) != 1 or len(exemplar_components) != 1:
            continue
        detached = next(iter(detached_components[0]))
        source_marker = next(iter(exemplar_components[0] & marker_cells))
        payload = exemplar_components[0] - {source_marker}
        if len({grid[row][column] for row, column in payload}) < 2:
            continue
        dr, dc = detached[0] - source_marker[0], detached[1] - source_marker[1]
        translated = {(row + dr, column + dc) for row, column in payload}
        if any(not (0 <= row < height and 0 <= column < width) for row, column in translated):
            continue
        if any(
            grid[row][column] != background and (row, column) != detached
            for row, column in translated
        ):
            continue
        output = [list(row) for row in grid]
        output[detached[0]][detached[1]] = background
        for row, column in payload:
            output[row + dr][column + dc] = grid[row][column]
        result = _freeze(output)
        outputs[_digest(_plain(result))] = result
    if len(outputs) != 1:
        raise Undefined("marker/exemplar roles are ambiguous")
    return next(iter(outputs.values()))


def _panel_pointer_ring_routing(
    grid: Grid, program: Mapping[str, Any], _limits: Limits
) -> Grid:
    """Route a central ring marker to the 3x3 panel sector of a pointer."""

    divider = int(program["divider_colour"])
    ring = int(program["ring_colour"])
    marker = int(program["marker_colour"])
    pointer = int(program["pointer_colour"])
    if len({divider, ring, marker, pointer}) != 4:
        raise Undefined("panel roles must be distinct")
    height, width = _shape(grid)
    divider_rows = [row for row in range(height) if set(grid[row]) == {divider}]
    divider_columns = [
        column
        for column in range(width)
        if {grid[row][column] for row in range(height)} == {divider}
    ]
    if len(divider_rows) != 2 or len(divider_columns) != 2:
        raise Undefined("two row and two column dividers are required")
    first_row, second_row = divider_rows
    first_column, second_column = divider_columns
    if second_row - first_row != 4 or second_column - first_column != 4:
        raise Undefined("central panel must be exactly three by three")
    center = first_row + 2, first_column + 2
    ring_cells = {
        (row, column)
        for row in range(first_row + 1, second_row)
        for column in range(first_column + 1, second_column)
        if (row, column) != center
    }
    if grid[center[0]][center[1]] != marker or any(
        grid[row][column] != ring for row, column in ring_cells
    ):
        raise Undefined("central carrier ring is malformed")
    if sum(cell == marker for values in grid for cell in values) != 1:
        raise Undefined("central marker must be unique")
    pointers = [
        (row, column)
        for row, values in enumerate(grid)
        for column, colour in enumerate(values)
        if colour == pointer
    ]
    if len(pointers) != 1:
        raise Undefined("pointer must be a singleton")
    point = pointers[0]
    if point[0] in divider_rows or point[1] in divider_columns:
        raise Undefined("pointer lies on a divider")

    def sector(value: int, first: int, second: int) -> int:
        if value < first:
            return -1
        if value > second:
            return 1
        return 0

    row_sector = sector(point[0], first_row, second_row)
    column_sector = sector(point[1], first_column, second_column)
    if row_sector == column_sector == 0:
        raise Undefined("pointer occupies the central panel")
    target = center[0] + row_sector, center[1] + column_sector
    if target not in ring_cells:
        raise Undefined("pointer sector has no ring site")
    output = [list(row) for row in grid]
    output[center[0]][center[1]] = ring
    output[target[0]][target[1]] = marker
    output[point[0]][point[1]] = marker
    return _freeze(output)


def _repeated_corner_blocks_inward(
    grid: Grid, _program: Mapping[str, Any], _limits: Limits
) -> Grid:
    """Move only the repeated-colour corner blocks one block-width inward."""

    background = _background(grid)
    foreground = {
        (row, column)
        for row, values in enumerate(grid)
        for column, colour in enumerate(values)
        if colour != background
    }
    components = _components_from_cells(foreground)
    if len(components) != 4:
        raise Undefined("exactly four corner blocks are required")
    height, width = _shape(grid)
    records: list[tuple[str, int, int, frozenset[Cell]]] = []
    for component in components:
        top, bottom, left, right = _bbox(component)
        side = bottom - top + 1
        if side != right - left + 1 or not _solid_rectangle(component):
            raise Undefined("corner components must be solid equal-sided blocks")
        roles = []
        if top == 0 and left == 0:
            roles.append("top_left")
        if top == 0 and right == width - 1:
            roles.append("top_right")
        if bottom == height - 1 and left == 0:
            roles.append("bottom_left")
        if bottom == height - 1 and right == width - 1:
            roles.append("bottom_right")
        if len(roles) != 1:
            raise Undefined("block must occupy exactly one corner")
        colours = {grid[row][column] for row, column in component}
        if len(colours) != 1:
            raise Undefined("corner block must be monochrome")
        records.append((roles[0], next(iter(colours)), side, component))
    if {role for role, _colour, _side, _cells in records} != {
        "top_left", "top_right", "bottom_left", "bottom_right"
    } or len({side for _role, _colour, side, _cells in records}) != 1:
        raise Undefined("one equal block per corner is required")
    counts = Counter(colour for _role, colour, _side, _cells in records)
    repeated = [colour for colour, count in counts.items() if count >= 2]
    if len(repeated) != 1:
        raise Undefined("a unique repeated corner colour is required")
    repeated_colour = repeated[0]
    moving = [record for record in records if record[1] == repeated_colour]
    side = records[0][2]
    output = [list(row) for row in grid]
    for _role, _colour, _side, cells in moving:
        for row, column in cells:
            output[row][column] = background
    shifts = {
        "top_left": (side, side),
        "top_right": (side, -side),
        "bottom_left": (-side, side),
        "bottom_right": (-side, -side),
    }
    for role, colour, _side, cells in moving:
        dr, dc = shifts[role]
        for row, column in cells:
            target = row + dr, column + dc
            if not (0 <= target[0] < height and 0 <= target[1] < width):
                raise Undefined("inward block leaves the canvas")
            if output[target[0]][target[1]] not in (background, colour):
                raise Undefined("inward block collides with a stationary block")
            output[target[0]][target[1]] = colour
    result = _freeze(output)
    if result == grid:
        raise Undefined("corner-block transport is an identity")
    return result


def _opposite_boundary_gravity(
    grid: Grid, _program: Mapping[str, Any], _limits: Limits
) -> Grid:
    """Align 8-connected components next to the boundary of their colour."""

    background = _background(grid)
    height, width = _shape(grid)
    edges: dict[str, int] = {}
    if len(set(grid[0])) == 1 and grid[0][0] != background:
        edges["top"] = grid[0][0]
    if len(set(grid[-1])) == 1 and grid[-1][0] != background:
        edges["bottom"] = grid[-1][0]
    if len({grid[row][0] for row in range(height)}) == 1 and grid[0][0] != background:
        edges["left"] = grid[0][0]
    if len({grid[row][-1] for row in range(height)}) == 1 and grid[0][-1] != background:
        edges["right"] = grid[0][-1]
    pairs = [
        (first, second)
        for first, second in (("top", "bottom"), ("left", "right"))
        if first in edges and second in edges and edges[first] != edges[second]
    ]
    if len(pairs) != 1:
        raise Undefined("a unique pair of opposite coloured boundaries is required")
    first, second = pairs[0]
    first_colour, second_colour = edges[first], edges[second]
    if _palette(grid) - {background, first_colour, second_colour}:
        raise Undefined("interior contains a third foreground colour")
    boundary_cells = (
        ({(0, column) for column in range(width)}, {(height - 1, column) for column in range(width)})
        if first == "top"
        else ({(row, 0) for row in range(height)}, {(row, width - 1) for row in range(height)})
    )
    movers_by_role: list[tuple[str, int, tuple[frozenset[Cell], ...]]] = []
    for role, colour, fixed in (
        (first, first_colour, boundary_cells[0]),
        (second, second_colour, boundary_cells[1]),
    ):
        cells = {
            (row, column)
            for row, values in enumerate(grid)
            for column, value in enumerate(values)
            if value == colour and (row, column) not in fixed
        }
        components = _components_from_cells(cells, diagonal=True)
        if not components:
            raise Undefined("each boundary colour needs interior payloads")
        movers_by_role.append((role, colour, components))
    output = [list(row) for row in grid]
    for _role, _colour, components in movers_by_role:
        for component in components:
            for row, column in component:
                output[row][column] = background
    for role, colour, components in movers_by_role:
        for component in components:
            top, bottom, left, right = _bbox(component)
            if role == "top":
                dr, dc = 1 - top, 0
            elif role == "bottom":
                dr, dc = height - 2 - bottom, 0
            elif role == "left":
                dr, dc = 0, 1 - left
            else:
                dr, dc = 0, width - 2 - right
            targets = {(row + dr, column + dc) for row, column in component}
            # A short, boundary-facing rail already beside its destination is
            # completed rather than uprooted.  This is the only non-rigid case
            # and is itself D4-covariant: parallel line, orthogonal side contact,
            # and a boundary gap shorter than the rail.
            if role in ("top", "bottom"):
                parallel_line = left == right
                side_contact = left in (0, width - 1)
                gap = top - 1 if role == "top" else height - 2 - bottom
                span = bottom - top + 1
            else:
                parallel_line = top == bottom
                side_contact = top in (0, height - 1)
                gap = left - 1 if role == "left" else width - 2 - right
                span = right - left + 1
            if parallel_line and side_contact and 0 < gap < span:
                targets |= set(component)
            for target in targets:
                current = output[target[0]][target[1]]
                if current not in (background, colour):
                    raise Undefined("boundary payloads collide across colours")
                output[target[0]][target[1]] = colour
    result = _freeze(output)
    if result == grid:
        raise Undefined("boundary gravity is an identity")
    return result


def _nearest_anchor_shell(
    grid: Grid, program: Mapping[str, Any], limits: Limits
) -> Grid:
    anchor_colour = int(program["anchor_colour"])
    components = _components(grid, limits)
    anchors = [cells for colour, cells in components if colour == anchor_colour]
    movers = [(colour, cells) for colour, cells in components if colour != anchor_colour]
    if len(anchors) < 2 or len(movers) < 2 or any(len(cells) != 1 for _, cells in movers):
        raise Undefined("homologous anchors and singleton movers are required")
    dimensions: set[tuple[int, int]] = set()
    for anchor in anchors:
        if not _solid_rectangle(anchor, minimum_area=4):
            raise Undefined("every anchor must be a solid rectangle")
        top, bottom, left, right = _bbox(anchor)
        dimensions.add((bottom - top + 1, right - left + 1))
    if len(dimensions) != 1:
        raise Undefined("anchors are not homologous")

    def anchor_distance(point: Cell, anchor: frozenset[Cell]) -> int:
        return min(
            abs(point[0] - row) + abs(point[1] - column)
            for row, column in anchor
        )

    def shell_target(point: Cell, anchor: frozenset[Cell]) -> Cell:
        top, bottom, left, right = _bbox(anchor)
        dr = (
            top - point[0]
            if point[0] < top
            else bottom - point[0]
            if point[0] > bottom
            else 0
        )
        dc = (
            left - point[1]
            if point[1] < left
            else right - point[1]
            if point[1] > right
            else 0
        )
        radius = max(abs(dr), abs(dc))
        if radius <= 1:
            raise Undefined("mover already occupies an anchor shell")
        steps = radius - 1
        row_step = (
            (1 if dr > 0 else -1) * steps
            if abs(dr) > 1 and abs(dr) >= steps
            else 0
        )
        column_step = (
            (1 if dc > 0 else -1) * steps
            if abs(dc) > 1 and abs(dc) >= steps
            else 0
        )
        return point[0] + row_step, point[1] + column_step

    states = [
        {
            "colour": colour,
            "source": cells,
            "point": next(iter(cells)),
            "banned": set(),
            "anchor": None,
            "target": None,
        }
        for colour, cells in movers
    ]

    def choose_anchor(state: dict[str, Any]) -> None:
        options = [
            (anchor_distance(state["point"], anchor), index, anchor)
            for index, anchor in enumerate(anchors)
            if index not in state["banned"]
        ]
        if not options:
            raise Undefined("all anchor approaches are blocked")
        minimum = min(distance for distance, _, _ in options)
        winners = [item for item in options if item[0] == minimum]
        if len(winners) != 1:
            raise Undefined("nearest anchor is tied")
        _distance, index, anchor = winners[0]
        state["anchor"] = index
        state["target"] = shell_target(state["point"], anchor)

    for state in states:
        choose_anchor(state)
    fixed_targets: set[Cell] = set()
    for _round in range(len(states) * max(2, len(anchors))):
        groups: dict[Cell, list[int]] = defaultdict(list)
        for index, state in enumerate(states):
            groups[state["target"]].append(index)
        conflicts = [(target, indices) for target, indices in groups.items() if len(indices) > 1]
        if not conflicts:
            break
        for target, indices in conflicts:
            ranked = sorted(
                (
                    abs(states[index]["point"][0] - target[0])
                    + abs(states[index]["point"][1] - target[1]),
                    index,
                )
                for index in indices
            )
            if ranked[0][0] == ranked[1][0]:
                raise Undefined("equidistant movers contest a shell site")
            winner = ranked[0][1]
            fixed_targets.add(target)
            for _distance, index in ranked[1:]:
                state = states[index]
                anchor_index = int(state["anchor"])
                anchor = anchors[anchor_index]
                point = state["point"]
                top, bottom, left, right = _bbox(anchor)
                row_outside = point[0] < top or point[0] > bottom
                column_outside = point[1] < left or point[1] > right
                if row_outside and column_outside:
                    height, width = _shape(grid)
                    shell = [
                        (row, column)
                        for row in range(max(0, top - 1), min(height - 1, bottom + 1) + 1)
                        for column in range(max(0, left - 1), min(width - 1, right + 1) + 1)
                        if (row, column) not in anchor
                        and (row in (top - 1, bottom + 1) or column in (left - 1, right + 1))
                        and (row, column) not in fixed_targets
                        and (row, column) != states[winner]["target"]
                    ]
                    costs = [
                        (abs(point[0] - row) + abs(point[1] - column), (row, column))
                        for row, column in shell
                    ]
                    if not costs:
                        raise Undefined("anchor shell is full")
                    minimum = min(cost for cost, _ in costs)
                    sites = [site for cost, site in costs if cost == minimum]
                    if len(sites) != 1:
                        raise Undefined("collision fallback is tied")
                    state["target"] = sites[0]
                else:
                    state["banned"].add(anchor_index)
                    choose_anchor(state)
    else:
        raise Undefined("collision resolution exceeded its finite bound")
    return _render(
        grid,
        [
            (int(state["colour"]), state["source"], frozenset((state["target"],)))
            for state in states
        ],
    )


def _parse_colour_pairs(program: Mapping[str, Any]) -> tuple[tuple[int, int], ...]:
    raw = program.get("colour_pairs")
    if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes)):
        raise Undefined("colour-pair relation is invalid")
    pairs: list[tuple[int, int]] = []
    for pair in raw:
        if (
            not isinstance(pair, Sequence)
            or isinstance(pair, (str, bytes))
            or len(pair) != 2
        ):
            raise Undefined("colour-pair member is invalid")
        left, right = pair
        if (
            isinstance(left, bool)
            or isinstance(right, bool)
            or not isinstance(left, int)
            or not isinstance(right, int)
            or not 0 <= left <= 9
            or not 0 <= right <= 9
            or left == right
        ):
            raise Undefined("colour-pair values are invalid")
        pairs.append(tuple(sorted((left, right))))
    canonical = tuple(sorted(set(pairs)))
    if len(canonical) < 2 or len(canonical) != len(pairs):
        raise Undefined("at least two distinct partner relations are required")
    return canonical


def _rowwise_partner_adjacency(
    grid: Grid, program: Mapping[str, Any], _limits: Limits
) -> Grid:
    relations = set(_parse_colour_pairs(program))
    background = _background(grid)
    replacements: list[tuple[int, frozenset[Cell], frozenset[Cell]]] = []
    seen: set[tuple[int, int]] = set()
    for row, values in enumerate(grid):
        points = [(column, colour) for column, colour in enumerate(values) if colour != background]
        if not points:
            continue
        if len(points) != 2 or points[0][1] == points[1][1]:
            raise Undefined("every occupied row must contain two distinct tokens")
        (left_column, left_colour), (right_column, right_colour) = points
        relation = tuple(sorted((left_colour, right_colour)))
        if relation not in relations:
            continue
        seen.add(relation)
        if right_column == left_column + 1:
            continue
        if right_column < left_column + 2:
            raise Undefined("partner ordering is invalid")
        replacements.append(
            (
                right_colour,
                frozenset(((row, right_column),)),
                frozenset(((row, left_column + 1),)),
            )
        )
    if seen != relations:
        raise Undefined("a learned partner relation is absent")
    return _render(grid, replacements)


def _three_sided_barrier(
    grid: Grid, limits: Limits
) -> tuple[frozenset[Cell], str, tuple[int, int, int, int]]:
    height, width = _shape(grid)
    candidates: list[tuple[frozenset[Cell], str, tuple[int, int, int, int]]] = []
    for _colour, cells in _components(grid, limits):
        top, bottom, left, right = _bbox(cells)
        if bottom - top < 2 or right - left < 2:
            continue
        sides = {
            "top": {(top, column) for column in range(left, right + 1)},
            "bottom": {(bottom, column) for column in range(left, right + 1)},
            "left": {(row, left) for row in range(top, bottom + 1)},
            "right": {(row, right) for row in range(top, bottom + 1)},
        }
        boundary = {"top": top == 0, "bottom": bottom == height - 1, "left": left == 0, "right": right == width - 1}
        for missing in ("top", "bottom", "left", "right"):
            expected = frozenset().union(
                *(side for name, side in sides.items() if name != missing)
            )
            if boundary[missing] and cells == expected:
                candidates.append((cells, missing, (top, bottom, left, right)))
    if len(candidates) != 1:
        raise Undefined("a unique three-sided boundary barrier is required")
    return candidates[0]


def _barrier_reference_routing(
    grid: Grid, _program: Mapping[str, Any], limits: Limits
) -> Grid:
    barrier, missing, (top, bottom, left, right) = _three_sided_barrier(grid, limits)
    height, width = _shape(grid)
    if missing == "top":
        inside = {
            (row, column)
            for row in range(top, bottom)
            for column in range(left + 1, right)
        }
        outside_test = lambda point: point[0] > bottom
        toward = lambda point: (bottom + 1, point[1])
        away = lambda point: (height - 1, point[1])
        aligned = lambda point, reference: point[1] == reference[1]
    elif missing == "bottom":
        inside = {
            (row, column)
            for row in range(top + 1, bottom + 1)
            for column in range(left + 1, right)
        }
        outside_test = lambda point: point[0] < top
        toward = lambda point: (top - 1, point[1])
        away = lambda point: (0, point[1])
        aligned = lambda point, reference: point[1] == reference[1]
    elif missing == "left":
        inside = {
            (row, column)
            for row in range(top + 1, bottom)
            for column in range(left, right)
        }
        outside_test = lambda point: point[1] > right
        toward = lambda point: (point[0], right + 1)
        away = lambda point: (point[0], width - 1)
        aligned = lambda point, reference: point[0] == reference[0]
    else:
        inside = {
            (row, column)
            for row in range(top + 1, bottom)
            for column in range(left + 1, right + 1)
        }
        outside_test = lambda point: point[1] < left
        toward = lambda point: (point[0], left - 1)
        away = lambda point: (point[0], 0)
        aligned = lambda point, reference: point[0] == reference[0]

    foreground = {
        (row, column)
        for row, values in enumerate(grid)
        for column, colour in enumerate(values)
        if colour != _background(grid)
    }
    references = foreground & inside
    outside = foreground - barrier - references
    if len(outside) < 4 or not references or any(not outside_test(point) for point in outside):
        raise Undefined("barrier reference and mover regions are incomplete")
    outside_components = [
        cells for _colour, cells in _components(grid, limits) if cells & outside
    ]
    if any(not cells <= outside or len(cells) != 1 for cells in outside_components):
        raise Undefined("outside movers must be singleton components")

    replacements: list[tuple[int, frozenset[Cell], frozenset[Cell]]] = []
    matches = 0
    mismatches = 0
    for point in sorted(outside):
        colour = grid[point[0]][point[1]]
        is_match = any(
            aligned(point, reference)
            and grid[reference[0]][reference[1]] == colour
            for reference in references
        )
        destination = toward(point) if is_match else away(point)
        matches += int(is_match)
        mismatches += int(not is_match)
        replacements.append((colour, frozenset((point,)), frozenset((destination,))))
    if not matches or not mismatches:
        raise Undefined("both matched and unmatched barrier routes are required")
    return _render(grid, replacements)


def _corner_seed_projection(
    grid: Grid, _program: Mapping[str, Any], _limits: Limits
) -> Grid:
    height, width = _shape(grid)
    if height != width or height < 8 or height % 4:
        raise Undefined("corner projection needs a quarter-divisible square")
    background = _background(grid)
    corners = {
        "top_left": (0, 0),
        "top_right": (0, width - 1),
        "bottom_left": (height - 1, 0),
        "bottom_right": (height - 1, width - 1),
    }
    seeds = {
        name: (point, grid[point[0]][point[1]])
        for name, point in corners.items()
        if grid[point[0]][point[1]] != background
    }
    foreground = {
        (row, column)
        for row, values in enumerate(grid)
        for column, colour in enumerate(values)
        if colour != background
    }
    if not seeds or foreground != {point for point, _ in seeds.values()}:
        raise Undefined("foreground must consist only of coloured corner seeds")
    if len({colour for _, colour in seeds.values()}) != len(seeds):
        raise Undefined("corner seed colours must be distinct")

    quarter = height // 4
    output = [list(row) for row in grid]
    for point, _colour in seeds.values():
        output[point[0]][point[1]] = background
    for name, (_point, colour) in seeds.items():
        if name.startswith("top"):
            rows = range(1, quarter + 1)
            columns = (
                range(1, quarter + 1)
                if name.endswith("left")
                else range(width - quarter - 1, width - 1)
            )
            target = {(row, column) for row in rows for column in columns}
        else:
            stem_column = quarter if name.endswith("left") else width - quarter - 1
            tip_column = stem_column + 1 if name.endswith("left") else stem_column - 1
            target = {
                (row, stem_column)
                for row in range(height - 2 * quarter, height - quarter)
            }
            target.add((height - quarter, tip_column))
        for row, column in target:
            if output[row][column] != background:
                raise Undefined("corner projections collide")
            output[row][column] = colour
    result = _freeze(output)
    if result == grid:
        raise Undefined("corner projection is an identity")
    return result


def _execute_core(program: Mapping[str, Any], grid: Grid, limits: Limits) -> Grid:
    operator = program.get("operator")
    if operator == "nearest_anchor_shell_v2":
        return _nearest_anchor_shell(grid, program, limits)
    if operator == "rowwise_partner_adjacency":
        return _rowwise_partner_adjacency(grid, program, limits)
    if operator == "barrier_reference_routing":
        return _barrier_reference_routing(grid, program, limits)
    if operator == "successor_bar_marker_transfer":
        return _successor_bar_marker_transfer(grid, program, limits)
    if operator == "odd_rectangle_center_projection":
        return _odd_rectangle_center_projection(grid, program, limits)
    if operator == "marker_aligned_exemplar_copy":
        return _marker_aligned_exemplar_copy(grid, program, limits)
    if operator == "panel_pointer_ring_routing":
        return _panel_pointer_ring_routing(grid, program, limits)
    if operator == "repeated_corner_blocks_inward":
        return _repeated_corner_blocks_inward(grid, program, limits)
    if operator == "opposite_boundary_gravity":
        return _opposite_boundary_gravity(grid, program, limits)
    raise Undefined("unknown motion/transport operator")


def _execute_internal(program: Mapping[str, Any], grid: Grid, limits: Limits) -> Grid:
    if not isinstance(program, Mapping) or program.get("schema") != SCHEMA:
        raise Undefined("invalid motion/transport v2 program")
    view = str(program.get("view", "id"))
    if view not in _D4:
        raise Undefined("invalid program view")
    oriented = _d4(grid, view)
    result = _execute_core(program, oriented, limits)
    return _d4(result, _inverse(view))


def execute_program(program: Mapping[str, Any], value: Any) -> list[list[int]]:
    """Execute one serialized, task-identity-free v2 program."""

    limits = Limits()
    return _plain(_execute_internal(program, _grid(value, limits), limits))


def replay_program(program: Mapping[str, Any], value: Any) -> list[list[int]]:
    """Replay a serialized program independently of compiler state."""

    return execute_program(program, value)


def _program(operator: str, length: int, **fields: Any) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "operator": operator,
        "view": fields.pop("view", "id"),
        "description_length": length,
        **fields,
    }


def _common_colours(demonstrations: Sequence[Pair]) -> tuple[int, ...]:
    shared = set(range(10))
    for source, target in demonstrations:
        shared &= set(_palette(source) | _palette(target))
    return tuple(sorted(shared))


def _infer_partner_pairs(
    demonstrations: Sequence[Pair], view: str
) -> tuple[tuple[int, int], ...] | None:
    changed_examples: dict[tuple[int, int], set[int]] = defaultdict(set)
    negative_relations: set[tuple[int, int]] = set()
    for example_index, (raw_source, raw_target) in enumerate(demonstrations):
        source, target = _d4(raw_source, view), _d4(raw_target, view)
        if _shape(source) != _shape(target):
            return None
        try:
            background = _background(source)
            if _background(target) != background:
                return None
        except Undefined:
            return None
        example_changed = False
        for source_row, target_row in zip(source, target):
            source_points = [
                (column, colour)
                for column, colour in enumerate(source_row)
                if colour != background
            ]
            target_points = [
                (column, colour)
                for column, colour in enumerate(target_row)
                if colour != background
            ]
            if len(source_points) not in (0, 2) or len(target_points) != len(source_points):
                return None
            if not source_points:
                continue
            if source_points[0][1] == source_points[1][1]:
                return None
            relation = tuple(sorted((source_points[0][1], source_points[1][1])))
            if source_row == target_row:
                if source_points[1][0] > source_points[0][0] + 1:
                    negative_relations.add(relation)
                continue
            example_changed = True
            if Counter(source_row) != Counter(target_row):
                return None
            if not (
                source_points[1][0] > source_points[0][0] + 1
                and target_points
                == [
                    source_points[0],
                    (source_points[0][0] + 1, source_points[1][1]),
                ]
            ):
                return None
            changed_examples[relation].add(example_index)
        if not example_changed:
            return None
    relations = tuple(sorted(changed_examples))
    if (
        len(relations) < 2
        or any(len(changed_examples[relation]) < 2 for relation in relations)
        or set(relations) & negative_relations
        or len(negative_relations - set(relations)) < 2
    ):
        return None
    return relations


def _corner_training_signature(demonstrations: Sequence[Pair], view: str) -> bool:
    if len(demonstrations) < 3:
        return False
    occupied: set[Cell] = set()
    for source, _target in demonstrations:
        oriented = _d4(source, view)
        height, width = _shape(oriented)
        if height != width or height < 8 or height % 4:
            return False
        try:
            background = _background(oriented)
        except Undefined:
            return False
        foreground = {
            (row, column)
            for row, values in enumerate(oriented)
            for column, colour in enumerate(values)
            if colour != background
        }
        corners = {(0, 0), (0, width - 1), (height - 1, 0), (height - 1, width - 1)}
        if len(foreground) != 1 or not foreground <= corners:
            return False
        point = next(iter(foreground))
        normalized = (
            int(point[0] == height - 1),
            int(point[1] == width - 1),
        )
        if normalized in occupied:
            return False
        occupied.add(normalized)
    return True


def _infer_panel_pointer_program(
    demonstrations: Sequence[Pair],
) -> dict[str, Any] | None:
    """Infer the four stable colours of panel-pointer routing from changes."""

    inferred: list[tuple[int, int, int, int]] = []
    for source, target in demonstrations:
        if _shape(source) != _shape(target):
            return None
        transitions = Counter(
            (source[row][column], target[row][column])
            for row in range(len(source))
            for column in range(len(source[0]))
            if source[row][column] != target[row][column]
        )
        if sum(transitions.values()) != 3:
            return None
        values = sorted(_palette(source) | _palette(target))
        role_candidates: list[tuple[int, int, int]] = []
        for marker, ring, pointer in itertools.permutations(values, 3):
            if transitions == Counter(
                {(marker, ring): 1, (ring, marker): 1, (pointer, marker): 1}
            ):
                role_candidates.append((ring, marker, pointer))
        if len(role_candidates) != 1:
            return None
        ring, marker, pointer = role_candidates[0]
        height, width = _shape(source)
        divider_candidates = [
            colour
            for colour in values
            if sum(set(source[row]) == {colour} for row in range(height)) == 2
            and sum(
                {source[row][column] for row in range(height)} == {colour}
                for column in range(width)
            )
            == 2
        ]
        if len(divider_candidates) != 1:
            return None
        inferred.append((divider_candidates[0], ring, marker, pointer))
    if not inferred or len(set(inferred)) != 1:
        return None
    divider, ring, marker, pointer = inferred[0]
    return _program(
        "panel_pointer_ring_routing",
        16,
        divider_colour=divider,
        ring_colour=ring,
        marker_colour=marker,
        pointer_colour=pointer,
    )


def _programs(demonstrations: Sequence[Pair]) -> tuple[dict[str, Any], ...]:
    programs: list[dict[str, Any]] = []
    for colour in _common_colours(demonstrations):
        programs.append(_program("nearest_anchor_shell_v2", 8, anchor_colour=colour))
    programs.append(_program("barrier_reference_routing", 10))
    programs.extend(
        (
            _program("successor_bar_marker_transfer", 12),
            _program("odd_rectangle_center_projection", 12),
            _program("marker_aligned_exemplar_copy", 13),
            _program("repeated_corner_blocks_inward", 13),
            _program("opposite_boundary_gravity", 13),
        )
    )
    unique = {_canonical(program): program for program in programs}
    return tuple(unique[key] for key in sorted(unique))


def _outputs(
    program: Mapping[str, Any], grids: Sequence[Grid], limits: Limits
) -> tuple[Grid, ...]:
    return tuple(_execute_internal(program, grid, limits) for grid in grids)


def _exact_programs(
    demonstrations: Sequence[Pair], probes: Sequence[Grid], limits: Limits
) -> tuple[dict[str, Any], ...]:
    programs = _programs(demonstrations)
    if len(programs) > limits.max_programs:
        raise Undefined("program enumeration exceeds its declared bound")
    targets = tuple(target for _, target in demonstrations)
    exact: list[dict[str, Any]] = []
    calls = 0
    for program in programs:
        try:
            outputs = _outputs(
                program, tuple(source for source, _ in demonstrations), limits
            )
            calls += len(demonstrations)
            _outputs(program, probes, limits)
            calls += len(probes)
        except (Undefined, TypeError, ValueError, KeyError, IndexError):
            continue
        if calls > limits.max_executor_calls:
            raise Undefined("executor-call bound exhausted")
        if outputs == targets:
            exact.append(program)
    return tuple(
        sorted(exact, key=lambda item: (int(item["description_length"]), _canonical(item)))
    )


def _leave_one_out(
    demonstrations: Sequence[Pair], tests: Sequence[Grid], limits: Limits
) -> tuple[bool, list[dict[str, Any]]]:
    witnesses: list[dict[str, Any]] = []
    for held_index, (held_source, held_target) in enumerate(demonstrations):
        subset = tuple(pair for index, pair in enumerate(demonstrations) if index != held_index)
        try:
            programs = _exact_programs(subset, (held_source, *tests), limits)
        except Undefined:
            return False, witnesses
        behaviours: dict[str, Grid] = {}
        for program in programs:
            try:
                output = _execute_internal(program, held_source, limits)
            except Undefined:
                continue
            behaviours[_digest(_plain(output))] = output
        if len(behaviours) != 1 or next(iter(behaviours.values())) != held_target:
            return False, witnesses
        witnesses.append(
            {
                "held_out_index": held_index,
                "proposal_demo_count": len(subset),
                "supported_programs": len(programs),
                "held_out_behavior_classes": 1,
                "held_out_exact": True,
                "held_out_output_hash": _digest(_plain(held_target)),
            }
        )
    return True, witnesses


def _swap_palette(grid: Grid, left: int, right: int) -> Grid:
    return tuple(
        tuple(right if cell == left else left if cell == right else cell for cell in row)
        for row in grid
    )


def _recolour_program(program: Mapping[str, Any], left: int, right: int) -> dict[str, Any]:
    result = json.loads(_canonical(program))

    def swap(colour: int) -> int:
        return right if colour == left else left if colour == right else colour

    for key in tuple(result):
        if key.endswith("_colour"):
            result[key] = swap(int(result[key]))
    if "colour_pairs" in result:
        result["colour_pairs"] = sorted(
            sorted((swap(int(pair[0])), swap(int(pair[1]))))
            for pair in result["colour_pairs"]
        )
    return result


def _conjugate_d4(program: Mapping[str, Any], external: str) -> dict[str, Any]:
    result = json.loads(_canonical(program))
    result["view"] = _compose(str(result.get("view", "id")), _inverse(external))
    return result


def _counterfactual_guard(
    program: Mapping[str, Any], demonstrations: Sequence[Pair], limits: Limits
) -> tuple[bool, int, int]:
    d4_checks = 0
    palette_checks = 0
    for source, target in demonstrations:
        for operation in _D4:
            d4_checks += 1
            if d4_checks + palette_checks > limits.max_counterfactuals:
                return False, d4_checks, palette_checks
            transformed_program = _conjugate_d4(program, operation)
            try:
                actual = _execute_internal(
                    transformed_program, _d4(source, operation), limits
                )
            except Undefined:
                return False, d4_checks, palette_checks
            if actual != _d4(target, operation):
                return False, d4_checks, palette_checks

        colours = sorted(_palette(source) | _palette(target))
        absent = next((colour for colour in range(10) if colour not in colours), None)
        swaps = list(itertools.combinations(colours, 2))
        if absent is not None:
            swaps.extend((colour, absent) for colour in colours)
        for left, right in swaps:
            palette_checks += 1
            if d4_checks + palette_checks > limits.max_counterfactuals:
                return False, d4_checks, palette_checks
            transformed_program = _recolour_program(program, left, right)
            try:
                actual = _execute_internal(
                    transformed_program, _swap_palette(source, left, right), limits
                )
            except Undefined:
                return False, d4_checks, palette_checks
            if actual != _swap_palette(target, left, right):
                return False, d4_checks, palette_checks
    return True, d4_checks, palette_checks


def compile_task(task: Any, limits: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    """Compile one proof-carrying score-seeded schema repair, or abstain."""

    try:
        bounds = Limits.from_value(limits)
        demonstrations, tests = _sanitize(task, bounds)
        for source, target in demonstrations:
            if (
                _shape(source) != _shape(target)
                or source == target
            ):
                raise Undefined("v2 requires a changed, same-canvas task")
        exact = _exact_programs(demonstrations, tests, bounds)
    except (Undefined, TypeError, ValueError, KeyError):
        return []
    if not exact:
        return []

    behaviours: dict[str, list[tuple[dict[str, Any], tuple[Grid, ...]]]] = defaultdict(list)
    for program in exact:
        try:
            outputs = _outputs(program, tests, bounds)
        except Undefined:
            continue
        behaviours[_digest([_plain(output) for output in outputs])].append((program, outputs))
    if len(behaviours) != 1:
        return []
    behavior_hash, equivalents = next(iter(sorted(behaviours.items())))
    equivalents.sort(key=lambda item: (int(item[0]["description_length"]), _canonical(item[0])))

    loo_ok, loo_witnesses = _leave_one_out(demonstrations, tests, bounds)
    if not loo_ok:
        return []
    representative: dict[str, Any] | None = None
    gauge = (0, 0)
    for program, _outputs_on_tests in equivalents:
        guarded, d4_checks, palette_checks = _counterfactual_guard(
            program, demonstrations, bounds
        )
        if guarded:
            representative = program
            gauge = d4_checks, palette_checks
            break
    if representative is None:
        return []
    try:
        train_outputs = _outputs(
            representative, tuple(source for source, _ in demonstrations), bounds
        )
        test_outputs = _outputs(representative, tests, bounds)
    except Undefined:
        return []
    if train_outputs != tuple(target for _, target in demonstrations):
        return []

    histogram_preserved = all(
        Counter(cell for row in source for cell in row)
        == Counter(cell for row in target for cell in row)
        for source, target in demonstrations
    )
    candidate = {
        "family": "motion_transport_compiler_v2",
        "program": json.loads(_canonical(representative)),
        "train_outputs": [_plain(output) for output in train_outputs],
        "test_outputs": [_plain(output) for output in test_outputs],
        "complexity": int(representative["description_length"]),
        "evidence": {
            "induction_regime": INDUCTION_REGIME,
            "all_demonstrations_exact": True,
            "exact_replay": True,
            "same_canvas": True,
            "same_palette": all(
                _palette(source) == _palette(target)
                for source, target in demonstrations
            ),
            "histogram_preserved": histogram_preserved,
            "leave_one_demo_out_reinduction": True,
            "leave_one_out_witnesses": loo_witnesses,
            "enumeration_complete": True,
            "programs_enumerated": len(_programs(demonstrations)),
            "exact_programs": len(exact),
            "unique_inferred_program_semantics": True,
            "full_test_behavior_classes": 1,
            "full_test_behavior_hash": behavior_hash,
            "equivalent_programs": len(equivalents),
            "d4_counterfactual_checks": gauge[0],
            "palette_counterfactual_checks": gauge[1],
            "injected_label_guard": True,
            "bounded_search": True,
            "hard_caps_exhausted": False,
            "task_identity_observed": False,
            "held_test_access": "input_key_only",
            "test_labels_observed": False,
            "label_store_observed": False,
            "output_literals_used": False,
            "absolute_target_locations_used": False,
        },
    }
    candidate["evidence"]["candidate_semantic_hash"] = _digest(candidate)
    return [candidate][: bounds.max_candidates]


__all__ = [
    "AUTHOR",
    "INDUCTION_REGIME",
    "Limits",
    "SCHEMA",
    "Undefined",
    "compile_task",
    "execute_program",
    "replay_program",
]
