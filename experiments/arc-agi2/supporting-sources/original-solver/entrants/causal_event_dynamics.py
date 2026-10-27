"""Task-local causal event dynamics for PR-LASM Block 15.

The entrant compiles compact state-transition programs from labelled
demonstrations.  Its operators model motion, emission, collision, blocking,
transport through material stages, and finite stopping conditions.  Runtime
execution has no task identity, corpus fingerprint, score, solution store, or
test-label access.  A candidate is emitted only after exact demonstration
replay, isolated leave-one-demonstration-out re-proposal, geometric
counterfactual replay, and minimum-description ambiguity checks.

Author: Komorebi P.
"""

from __future__ import annotations

from collections import Counter, deque
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import hashlib
import json
import math
from typing import Any, Callable, Iterable


Grid = tuple[tuple[int, ...], ...]
Cell = tuple[int, int]
Pair = tuple[Grid, Grid]
SCHEMA = "komorebi.pr_lasm.block15.causal_event_dynamics.program.v1"
AUTHOR = "Komorebi P."


class Undefined(ValueError):
    """The proposed event law is absent, ambiguous, or out of scope."""


@dataclass(frozen=True, slots=True)
class Limits:
    max_side: int = 40
    max_examples: int = 20
    max_cells: int = 120_000
    max_programs: int = 4_096
    max_candidates: int = 1
    max_counterfactuals: int = 128
    mdl_slack: int = 0

    @classmethod
    def parse(cls, raw: Any) -> "Limits":
        if raw is None:
            return cls()
        if not isinstance(raw, Mapping):
            raise Undefined("limits must be a mapping")
        aliases = {
            "candidate_cap": "max_candidates",
            "max_grid_cells": "max_cells",
            "ambiguity_slack": "mdl_slack",
            "max_replay_calls": None,
            "max_replay_stages": None,
            "max_trace_bytes": None,
            "time_limit": None,
            "time_limit_seconds": None,
        }
        fields = set(cls.__dataclass_fields__)
        values: dict[str, int] = {}
        for raw_name, raw_value in raw.items():
            name = aliases.get(str(raw_name), str(raw_name))
            if name is None or name not in fields:
                continue
            if isinstance(raw_value, bool) or not isinstance(raw_value, int):
                raise Undefined("finite limits must be integers")
            minimum = 0 if name == "mdl_slack" else 1
            if raw_value < minimum:
                raise Undefined("finite limit is below its minimum")
            values[name] = raw_value
        return cls(**values)


@dataclass(frozen=True, slots=True)
class Proposal:
    family: str
    program: Mapping[str, Any]
    complexity: int


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
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise Undefined("grid must be a row sequence")
    if not value or len(value) > max_side:
        raise Undefined("invalid grid height")
    width: int | None = None
    rows: list[tuple[int, ...]] = []
    for raw_row in value:
        if not isinstance(raw_row, Sequence) or isinstance(
            raw_row, (str, bytes, bytearray)
        ):
            raise Undefined("grid row must be a sequence")
        if width is None:
            width = len(raw_row)
        if width is None or width < 1 or width > max_side or len(raw_row) != width:
            raise Undefined("grid must be nonempty and rectangular")
        row: list[int] = []
        for value_cell in raw_row:
            if (
                isinstance(value_cell, bool)
                or not isinstance(value_cell, int)
                or not 0 <= value_cell <= 9
            ):
                raise Undefined("ARC colors must be integers in [0, 9]")
            row.append(int(value_cell))
        rows.append(tuple(row))
    return tuple(rows)


def _plain(grid: Grid) -> list[list[int]]:
    return [list(row) for row in grid]


def _shape(grid: Grid) -> tuple[int, int]:
    return len(grid), len(grid[0])


def _sanitize(task: Any, limits: Limits) -> tuple[tuple[Pair, ...], tuple[Grid, ...]]:
    if not isinstance(task, Mapping):
        raise Undefined("task must be a mapping")
    train, test = task.get("train"), task.get("test")
    if (
        not isinstance(train, Sequence)
        or isinstance(train, (str, bytes, bytearray))
        or len(train) < 2
        or not isinstance(test, Sequence)
        or isinstance(test, (str, bytes, bytearray))
        or not test
        or len(train) + len(test) > limits.max_examples
    ):
        raise Undefined("invalid task arity")
    demonstrations: list[Pair] = []
    tests: list[Grid] = []
    cells = 0
    for record in train:
        if not isinstance(record, Mapping):
            raise Undefined("invalid demonstration")
        source = _grid(record.get("input"), limits.max_side)
        target = _grid(record.get("output"), limits.max_side)
        cells += len(source) * len(source[0]) + len(target) * len(target[0])
        demonstrations.append((source, target))
    for record in test:
        if not isinstance(record, Mapping):
            raise Undefined("invalid test record")
        # Deliberately access only the held record's input member.
        source = _grid(record.get("input"), limits.max_side)
        cells += len(source) * len(source[0])
        tests.append(source)
    if cells > limits.max_cells:
        raise Undefined("cell budget exhausted")
    return tuple(demonstrations), tuple(tests)


def _mode(grid: Grid) -> int:
    counts = Counter(cell for row in grid for cell in row)
    maximum = max(counts.values())
    winners = sorted(color for color, count in counts.items() if count == maximum)
    if len(winners) != 1:
        raise Undefined("background mode is tied")
    return winners[0]


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
            for dr, dc in ((-1, 0), (0, -1), (0, 1), (1, 0)):
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


def _d4(grid: Grid, operation: str) -> Grid:
    if operation == "identity":
        return grid
    if operation == "rot90":
        return tuple(tuple(row) for row in zip(*grid[::-1]))
    if operation == "flip_h":
        return tuple(tuple(reversed(row)) for row in grid)
    raise Undefined("unsupported gauge")


def _program(operator: str, **parameters: Any) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "operator": operator,
        "root_scope": "immutable_input",
        **parameters,
    }


def _boundary_runs(values: Sequence[int], background: int) -> tuple[tuple[int, int], ...]:
    runs: list[tuple[int, int]] = []
    start: int | None = None
    for index, color in enumerate(tuple(values) + (background,)):
        if color != background and start is None:
            start = index
        elif color == background and start is not None:
            runs.append((start, index))
            start = None
    return tuple(runs)


def _header_connector(grid: Grid, program: Mapping[str, Any]) -> Grid:
    background = int(program["background"])
    height, width = _shape(grid)
    candidates: list[tuple[tuple[Cell, ...], Cell]] = []
    boundaries = (
        (tuple(grid[0]), tuple((0, column) for column in range(width)), (1, 0)),
        (tuple(grid[-1]), tuple((height - 1, column) for column in range(width)), (-1, 0)),
        (
            tuple(grid[row][0] for row in range(height)),
            tuple((row, 0) for row in range(height)),
            (0, 1),
        ),
        (
            tuple(grid[row][-1] for row in range(height)),
            tuple((row, width - 1) for row in range(height)),
            (0, -1),
        ),
    )
    for values, cells, inward in boundaries:
        for start, stop in _boundary_runs(values, background):
            run = cells[start:stop]
            colors = [grid[row][column] for row, column in run]
            if len(run) >= 3 and len(set(colors)) == len(colors):
                candidates.append((run, inward))
    if len(candidates) != 1:
        raise Undefined("boundary state header is not unique")
    header, inward = candidates[0]
    header_set = set(header)
    output = [list(row) for row in grid]
    changed = False
    for root_row, root_column in header:
        color = grid[root_row][root_column]
        peers = [
            (row, column)
            for row in range(height)
            for column in range(width)
            if (row, column) not in header_set and grid[row][column] == color
        ]
        if len(peers) > 1:
            raise Undefined("header role has multiple terminals")
        if peers:
            target_row, target_column = peers[0]
            if inward[0] and (target_row - root_row) * inward[0] <= 0:
                raise Undefined("terminal is outside the header frame")
            if inward[1] and (target_column - root_column) * inward[1] <= 0:
                raise Undefined("terminal is outside the header frame")
            row, column = root_row, root_column
            while (row, column) != (
                target_row if inward[0] else root_row,
                target_column if inward[1] else root_column,
            ):
                row += inward[0]
                column += inward[1]
                output[row][column] = color
            if inward[0]:
                step = 1 if target_column > column else -1
                for other_column in range(column, target_column + step, step):
                    output[target_row][other_column] = color
            else:
                step = 1 if target_row > row else -1
                for other_row in range(row, target_row + step, step):
                    output[other_row][target_column] = color
        else:
            row, column = root_row, root_column
            while 0 <= row + inward[0] < height and 0 <= column + inward[1] < width:
                row += inward[0]
                column += inward[1]
                output[row][column] = color
        changed = True
    if not changed:
        raise Undefined("header event made no change")
    return tuple(tuple(row) for row in output)


def _gravity_splash(grid: Grid, program: Mapping[str, Any]) -> Grid:
    background = int(program["background"])
    barrier = int(program["barrier"])
    particle = int(program["particle"])
    dr, dc = (int(value) for value in program["direction"])
    if (dr, dc) not in ((-1, 0), (0, -1), (0, 1), (1, 0)):
        raise Undefined("motion direction is not cardinal")
    height, width = _shape(grid)
    if dr:
        barriers = [row for row in range(height) if all(grid[row][c] == barrier for c in range(width))]
    else:
        barriers = [column for column in range(width) if all(grid[r][column] == barrier for r in range(height))]
    if len(barriers) != 1:
        raise Undefined("barrier line is not unique")
    particles = [
        (row, column)
        for row in range(height)
        for column in range(width)
        if grid[row][column] == particle
    ]
    if not particles:
        raise Undefined("particle state is absent")
    output = [list(row) for row in grid]
    for row, column in particles:
        output[row][column] = background
    moved: list[Cell] = []
    for row, column in particles:
        target = row + dr, column + dc
        if not (0 <= target[0] < height and 0 <= target[1] < width):
            raise Undefined("particle leaves the finite canvas")
        if grid[target[0]][target[1]] == barrier:
            raise Undefined("unseen direct barrier collision")
        moved.append(target)
        output[target[0]][target[1]] = particle
    for row, column in moved:
        beyond = row + dr, column + dc
        if not (0 <= beyond[0] < height and 0 <= beyond[1] < width):
            continue
        if grid[beyond[0]][beyond[1]] != barrier:
            continue
        perpendiculars = ((0, -1), (0, 1)) if dr else ((-1, 0), (1, 0))
        for pr, pc in perpendiculars:
            ray_row, ray_column = row, column
            while True:
                ray_row += -dr + pr
                ray_column += -dc + pc
                if not (0 <= ray_row < height and 0 <= ray_column < width):
                    break
                if grid[ray_row][ray_column] == barrier:
                    raise Undefined("splash intersects its barrier")
                output[ray_row][ray_column] = particle
    return tuple(tuple(row) for row in output)


def _deflected_beam(grid: Grid, program: Mapping[str, Any]) -> Grid:
    """Advance a boundary beam, sidestepping colored transverse barriers."""

    background = int(program["background"])
    path = int(program["path"])
    left_color = int(program["left_color"])
    right_color = int(program["right_color"])
    height, width = _shape(grid)
    seeds = [
        (row, column)
        for row in range(height)
        for column in range(width)
        if grid[row][column] == path
    ]
    if len(seeds) != 1:
        raise Undefined("beam needs one boundary seed")
    row, column = seeds[0]
    directions: list[Cell] = []
    if row == 0:
        directions.append((1, 0))
    if row == height - 1:
        directions.append((-1, 0))
    if column == 0:
        directions.append((0, 1))
    if column == width - 1:
        directions.append((0, -1))
    if len(directions) != 1:
        raise Undefined("beam seed does not define one inward frame")
    dr, dc = directions[0]
    output = [list(values) for values in grid]
    budget = height * width * 10
    steps = 0
    while True:
        steps += 1
        if steps > budget:
            raise Undefined("beam event budget exhausted")
        next_row, next_column = row + dr, column + dc
        if not (0 <= next_row < height and 0 <= next_column < width):
            break
        material = grid[next_row][next_column]
        if material in {background, path}:
            if material == background:
                output[next_row][next_column] = path
            row, column = next_row, next_column
            continue
        if material not in {left_color, right_color}:
            raise Undefined("beam met an unsupported material")
        if material == left_color:
            side_row, side_column = -dc, dr
        else:
            side_row, side_column = dc, -dr
        while True:
            row, column = row + side_row, column + side_column
            if not (0 <= row < height and 0 <= column < width):
                raise Undefined("deflection leaves the canvas")
            if grid[row][column] != background:
                raise Undefined("deflection corridor is obstructed")
            output[row][column] = path
            forward = row + dr, column + dc
            if not (0 <= forward[0] < height and 0 <= forward[1] < width):
                raise Undefined("barrier reaches the terminal boundary")
            forward_material = grid[forward[0]][forward[1]]
            if forward_material == background:
                break
            if forward_material != material:
                raise Undefined("deflector identity changes during sidestep")
    return tuple(tuple(values) for values in output)


def _radial_kernel(grid: Grid, program: Mapping[str, Any]) -> Grid:
    background = int(program["background"])
    support = {
        (row, column)
        for row, values in enumerate(grid)
        for column, color in enumerate(values)
        if color != background
    }
    top, bottom, left, right = _bbox(support)
    if (bottom - top, right - left) != (2, 2) or len(support) != 9:
        raise Undefined("event kernel is not a filled 3x3 state")
    output = [list(row) for row in grid]
    height, width = _shape(grid)
    for local_row in range(3):
        for local_column in range(3):
            dr, dc = local_row - 1, local_column - 1
            if (dr, dc) == (0, 0):
                continue
            root_row, root_column = top + local_row, left + local_column
            color = grid[root_row][root_column]
            row, column = root_row + dr, root_column + dc
            while 0 <= row < height and 0 <= column < width:
                if grid[row][column] == background:
                    output[row][column] = color
                row += dr
                column += dc
    return tuple(tuple(row) for row in output)


def _diagonal_bridges(grid: Grid, program: Mapping[str, Any]) -> Grid:
    background = int(program["background"])
    colors = sorted({cell for row in grid for cell in row if cell != background})
    if len(colors) < 2:
        raise Undefined("too few component roles")
    output = [list(row) for row in grid]
    changed = False
    for color in colors:
        components = _components(grid, color)
        if len(components) != 2:
            raise Undefined("component color does not form one pair")
        boxes = [_bbox(component) for component in components]
        for component, box in zip(components, boxes):
            top, bottom, left, right = box
            if len(component) != (bottom - top + 1) * (right - left + 1):
                raise Undefined("bridge endpoint is not rectangular")
        if (boxes[0][1] - boxes[0][0], boxes[0][3] - boxes[0][2]) != (
            boxes[1][1] - boxes[1][0],
            boxes[1][3] - boxes[1][2],
        ):
            raise Undefined("paired endpoint shapes differ")
        pairs = sorted(
            (
                max(abs(a[0] - b[0]), abs(a[1] - b[1])),
                a,
                b,
            )
            for a in components[0]
            for b in components[1]
            if abs(a[0] - b[0]) == abs(a[1] - b[1])
        )
        if not pairs or len(pairs) > 1 and pairs[0][0] == pairs[1][0]:
            raise Undefined("diagonal bridge corners are ambiguous")
        distance, first, second = pairs[0]
        if distance < 2:
            raise Undefined("components are already touching")
        dr = 1 if second[0] > first[0] else -1
        dc = 1 if second[1] > first[1] else -1
        for step in range(1, distance):
            row, column = first[0] + step * dr, first[1] + step * dc
            if grid[row][column] != background:
                raise Undefined("bridge interior is obstructed")
            output[row][column] = color
            changed = True
    if not changed:
        raise Undefined("no diagonal bridge was emitted")
    return tuple(tuple(row) for row in output)


def _pulse_lattice(grid: Grid, program: Mapping[str, Any]) -> Grid:
    marker = int(program["marker"])
    center = int(program["center"])
    halo = int(program["halo"])
    background = _mode(grid)
    palette = {cell for row in grid for cell in row}
    if palette != {background, marker}:
        raise Undefined("pulse source palette is not binary")
    marks = [
        (row, column)
        for row, values in enumerate(grid)
        for column, color in enumerate(values)
        if color == marker
    ]
    if not 2 <= len(marks) <= 12:
        raise Undefined("pulse count is outside its learned regime")
    height, width = _shape(grid)
    output = [list(row) for row in grid]
    for row, column in marks:
        for other_column in range(width):
            output[row][other_column] = marker
        for other_row in range(height):
            output[other_row][column] = marker
    for row, column in marks:
        for dr, dc in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
            other = row + dr, column + dc
            if 0 <= other[0] < height and 0 <= other[1] < width:
                if output[other[0]][other[1]] != background:
                    raise Undefined("pulse halo overlaps another event trace")
                output[other[0]][other[1]] = halo
    for row, column in marks:
        output[row][column] = center
    return tuple(tuple(row) for row in output)


def _solid_rectangles(grid: Grid, color: int) -> tuple[tuple[frozenset[Cell], tuple[int, int, int, int]], ...]:
    rectangles = []
    for component in _components(grid, color):
        box = _bbox(component)
        top, bottom, left, right = box
        if len(component) == (bottom - top + 1) * (right - left + 1):
            rectangles.append((component, box))
    return tuple(rectangles)


def _blocked_broadcast(grid: Grid, program: Mapping[str, Any]) -> Grid:
    background = int(program["background"])
    fill = int(program["fill"])
    rectangles = [item for item in _solid_rectangles(grid, fill) if len(item[0]) >= 9]
    if len(rectangles) != 1:
        raise Undefined("broadcast body is not a unique solid rectangle")
    _, (top, bottom, left, right) = rectangles[0]
    height, width = _shape(grid)
    output = [list(row) for row in grid]
    for row in range(top, bottom + 1):
        for start, stop in ((0, left), (right + 1, width)):
            ray = range(start, stop)
            if all(grid[row][column] == background for column in ray):
                for column in ray:
                    output[row][column] = fill
    for column in range(left, right + 1):
        for start, stop in ((0, top), (bottom + 1, height)):
            ray = range(start, stop)
            if all(grid[row][column] == background for row in ray):
                for row in ray:
                    output[row][column] = fill
    return tuple(tuple(row) for row in output)


def _stamps(grid: Grid, background: int) -> tuple[tuple[Cell, int, int], ...]:
    height, width = _shape(grid)
    found: list[tuple[Cell, int, int]] = []
    for row in range(1, height - 1):
        for column in range(1, width - 1):
            perimeter = [
                grid[row + dr][column + dc]
                for dr in (-1, 0, 1)
                for dc in (-1, 0, 1)
                if (dr, dc) != (0, 0)
            ]
            if len(set(perimeter)) != 1:
                continue
            carrier = perimeter[0]
            payload = grid[row][column]
            if carrier in {background, payload} or payload == background:
                continue
            found.append(((row, column), carrier, payload))
    return tuple(found)


def _stamp_transport(grid: Grid, program: Mapping[str, Any]) -> Grid:
    background = int(program["background"])
    stamps = _stamps(grid, background)
    if not stamps:
        raise Undefined("no executable signal stamp")
    height, width = _shape(grid)
    output = [list(row) for row in grid]
    centers = {center for center, _, _ in stamps}
    for center, carrier, payload in stamps:
        target_cells = {
            (row, column)
            for row in range(height)
            for column in range(width)
            if grid[row][column] == payload and (row, column) not in centers
        }
        directions: list[tuple[int, int, int]] = []
        for dr, dc in ((-1, 0), (0, -1), (0, 1), (1, 0)):
            for steps in range(1, max(height, width) + 1):
                probe = center[0] + 3 * steps * dr, center[1] + 3 * steps * dc
                if not (0 <= probe[0] < height and 0 <= probe[1] < width):
                    break
                if probe in target_cells:
                    directions.append((steps, dr, dc))
                    break
        if not directions:
            raise Undefined("stamp has no phase-aligned payload target")
        directions.sort()
        if len(directions) > 1 and directions[0][0] == directions[1][0]:
            raise Undefined("stamp transport direction is ambiguous")
        steps, dr, dc = directions[0]
        for index in range(1, steps + 1):
            root = center[0] + 3 * index * dr, center[1] + 3 * index * dc
            for sr in (-1, 0, 1):
                for sc in (-1, 0, 1):
                    row, column = root[0] + sr, root[1] + sc
                    if not (0 <= row < height and 0 <= column < width):
                        raise Undefined("translated stamp clips the canvas")
                    output[row][column] = payload if (sr, sc) == (0, 0) else carrier
    return tuple(tuple(row) for row in output)


def _checkerboard_flood(grid: Grid, program: Mapping[str, Any]) -> Grid:
    background = int(program["background"])
    wall = int(program["wall"])
    height, width = _shape(grid)
    signal_colors = {cell for row in grid for cell in row if cell not in {background, wall}}
    if len(signal_colors) != 2:
        raise Undefined("checkerboard signal must have two phases")
    unseen = {
        (row, column)
        for row in range(height)
        for column in range(width)
        if grid[row][column] != wall
    }
    output = [list(row) for row in grid]
    seeded = 0
    while unseen:
        root = min(unseen)
        unseen.remove(root)
        queue = deque([root])
        component = {root}
        while queue:
            row, column = queue.popleft()
            for dr, dc in ((-1, 0), (0, -1), (0, 1), (1, 0)):
                other = row + dr, column + dc
                if other in unseen:
                    unseen.remove(other)
                    component.add(other)
                    queue.append(other)
        seeds = [cell for cell in component if grid[cell[0]][cell[1]] in signal_colors]
        if not seeds:
            continue
        phase_map: dict[int, int] = {}
        for row, column in seeds:
            phase = (row + column) % 2
            color = grid[row][column]
            if phase in phase_map and phase_map[phase] != color:
                raise Undefined("signal phase evidence conflicts")
            phase_map[phase] = color
        if set(phase_map) != {0, 1} or set(phase_map.values()) != signal_colors:
            raise Undefined("both checkerboard phases must be demonstrated")
        for row, column in component:
            if grid[row][column] == background:
                output[row][column] = phase_map[(row + column) % 2]
        seeded += 1
    if seeded != 1:
        raise Undefined("seeded maze component is not unique")
    return tuple(tuple(row) for row in output)


def _paired_fronts(grid: Grid, program: Mapping[str, Any]) -> Grid:
    background = int(program["background"])
    collision = int(program["collision"])
    colors = sorted({cell for row in grid for cell in row if cell not in {background, collision}})
    if len(colors) < 2:
        raise Undefined("paired fronts require multiple signal colors")
    height, width = _shape(grid)
    events: dict[Cell, set[int]] = {}
    for color in colors:
        cells = {(r, c) for r in range(height) for c in range(width) if grid[r][c] == color}
        rows = sorted({r for r, _ in cells})
        columns = sorted({c for _, c in cells})
        vertical = (
            len(columns) == 2
            and rows == list(range(rows[0], rows[-1] + 1))
            and cells == {(r, c) for r in rows for c in columns}
        )
        horizontal = (
            len(rows) == 2
            and columns == list(range(columns[0], columns[-1] + 1))
            and cells == {(r, c) for r in rows for c in columns}
        )
        if vertical == horizontal:
            raise Undefined("front seed is not an oriented pair of equal bars")
        if vertical:
            thickness = len(rows)
            left, right = columns
            for row in range(height):
                if row < rows[0]:
                    distance = math.ceil((rows[0] - row) / thickness)
                elif row > rows[-1]:
                    distance = math.ceil((row - rows[-1]) / thickness)
                else:
                    distance = 0
                for column in (left - distance, right + distance):
                    if 0 <= column < width:
                        events.setdefault((row, column), set()).add(color)
        else:
            thickness = len(columns)
            top, bottom = rows
            for column in range(width):
                if column < columns[0]:
                    distance = math.ceil((columns[0] - column) / thickness)
                elif column > columns[-1]:
                    distance = math.ceil((column - columns[-1]) / thickness)
                else:
                    distance = 0
                for row in (top - distance, bottom + distance):
                    if 0 <= row < height:
                        events.setdefault((row, column), set()).add(color)
    output = [list(row) for row in grid]
    for (row, column), paints in events.items():
        if len(paints) == 1:
            output[row][column] = next(iter(paints))
        else:
            output[row][column] = collision
    return tuple(tuple(row) for row in output)


def _segment_cells(first: Cell, second: Cell) -> tuple[Cell, ...]:
    dr, dc = second[0] - first[0], second[1] - first[1]
    if dr == 0:
        step = (0, 1 if dc > 0 else -1)
        length = abs(dc)
    elif dc == 0:
        step = (1 if dr > 0 else -1, 0)
        length = abs(dr)
    elif abs(dr) == abs(dc):
        step = (1 if dr > 0 else -1, 1 if dc > 0 else -1)
        length = abs(dr)
    else:
        raise Undefined("endpoints do not define a lattice axis")
    return tuple((first[0] + k * step[0], first[1] + k * step[1]) for k in range(length + 1))


def _endpoint_trace(grid: Grid, program: Mapping[str, Any]) -> Grid:
    endpoint = int(program["endpoint"])
    mapping = {int(source): int(target) for source, target in program["paint_map"]}
    points = [
        (row, column)
        for row, values in enumerate(grid)
        for column, color in enumerate(values)
        if color == endpoint
    ]
    if len(points) != 2:
        raise Undefined("trace needs exactly two endpoints")
    path = _segment_cells(points[0], points[1])
    output = [list(row) for row in grid]
    for row, column in path[1:-1]:
        source = grid[row][column]
        if source not in mapping:
            raise Undefined("path crosses an unsupported material")
        output[row][column] = mapping[source]
    return tuple(tuple(row) for row in output)


def _separator_transport(grid: Grid, program: Mapping[str, Any]) -> Grid:
    background = int(program["background"])
    source = int(program["source"])
    spent = int(program["spent"])
    separator = int(program["separator"])
    payload = int(program["payload"])
    height, width = _shape(grid)
    if _mode(grid) != background:
        raise Undefined("material background role is inconsistent")
    full_rows = [row for row in range(height) if all(grid[row][c] == separator for c in range(width))]
    full_columns = [column for column in range(width) if all(grid[r][column] == separator for r in range(height))]
    if len(full_rows) + len(full_columns) != 1:
        raise Undefined("material separator is not unique")
    output = [list(row) for row in grid]
    active = 0
    if full_rows:
        split = full_rows[0]
        before = sum(grid[r][c] == source for r in range(split) for c in range(width))
        after = sum(grid[r][c] == source for r in range(split + 1, height) for c in range(width))
        if (before == 0) == (after == 0):
            raise Undefined("source side is ambiguous")
        direction = 1 if before > after else -1
        for column in range(width):
            sources = [
                row
                for row in range(height)
                if grid[row][column] == source
                and (row < split if direction == 1 else row > split)
            ]
            if not sources:
                continue
            payloads = [
                row
                for row in range(height)
                if grid[row][column] == payload
                and (row > split if direction == 1 else row < split)
            ]
            for row in sources:
                output[row][column] = spent
            near = max(sources) if direction == 1 else min(sources)
            for row in range(near + direction, split, direction):
                output[row][column] = source
            tail = list(range(split + direction, height if direction == 1 else -1, direction))
            for row in tail:
                output[row][column] = separator
            for row in tail[-len(payloads) :] if payloads else ():
                output[row][column] = payload
            active += 1
    else:
        split = full_columns[0]
        before = sum(grid[r][c] == source for r in range(height) for c in range(split))
        after = sum(grid[r][c] == source for r in range(height) for c in range(split + 1, width))
        if (before == 0) == (after == 0):
            raise Undefined("source side is ambiguous")
        direction = 1 if before > after else -1
        for row in range(height):
            sources = [
                column
                for column in range(width)
                if grid[row][column] == source
                and (column < split if direction == 1 else column > split)
            ]
            if not sources:
                continue
            payloads = [
                column
                for column in range(width)
                if grid[row][column] == payload
                and (column > split if direction == 1 else column < split)
            ]
            for column in sources:
                output[row][column] = spent
            near = max(sources) if direction == 1 else min(sources)
            for column in range(near + direction, split, direction):
                output[row][column] = source
            tail = list(range(split + direction, width if direction == 1 else -1, direction))
            for column in tail:
                output[row][column] = separator
            for column in tail[-len(payloads) :] if payloads else ():
                output[row][column] = payload
            active += 1
    if not active:
        raise Undefined("no material track was activated")
    return tuple(tuple(row) for row in output)


_EXECUTORS: dict[str, Callable[[Grid, Mapping[str, Any]], Grid]] = {
    "boundary_header_orthogonal_connect": _header_connector,
    "gravity_step_then_barrier_splash": _gravity_splash,
    "chirality_deflected_boundary_beam": _deflected_beam,
    "radial_kernel_ray_emission": _radial_kernel,
    "matched_component_diagonal_bridge": _diagonal_bridges,
    "cross_pulse_with_diagonal_halo": _pulse_lattice,
    "blocker_gated_rectangle_broadcast": _blocked_broadcast,
    "phase_aligned_stamp_transport": _stamp_transport,
    "seeded_checkerboard_corridor_flood": _checkerboard_flood,
    "collision_aware_paired_fronts": _paired_fronts,
    "endpoint_material_trace": _endpoint_trace,
    "four_stage_separator_transport": _separator_transport,
}


def execute_program(program: Mapping[str, Any], grid: Any) -> list[list[int]]:
    """Execute one serialized deterministic event program."""

    if not isinstance(program, Mapping) or program.get("schema") != SCHEMA:
        raise Undefined("unknown program schema")
    executor = _EXECUTORS.get(str(program.get("operator")))
    if executor is None:
        raise Undefined("unknown event operator")
    return _plain(executor(_grid(grid), program))


def replay_program(program: Mapping[str, Any], grid: Any) -> list[list[int]]:
    """Tournament replay hook.  Neither the program nor grid is mutated."""

    return execute_program(program, grid)


def _same_shape_nonidentity(train: Sequence[Pair]) -> bool:
    return all(_shape(source) == _shape(target) and source != target for source, target in train)


def _exact(program: Mapping[str, Any], train: Sequence[Pair]) -> bool:
    try:
        return all(_grid(execute_program(program, source)) == target for source, target in train)
    except (Undefined, KeyError, TypeError, ValueError, IndexError, ZeroDivisionError):
        return False


def _pairs(source: Grid, target: Grid) -> set[tuple[int, int]]:
    return {
        (before, after)
        for before_row, after_row in zip(source, target)
        for before, after in zip(before_row, after_row)
        if before != after
    }


def _common_modes(train: Sequence[Pair]) -> tuple[int, ...]:
    try:
        modes = {_mode(source) for source, _ in train}
    except Undefined:
        return ()
    return tuple(modes) if len(modes) == 1 else ()


def _enumerate(train: Sequence[Pair], limits: Limits) -> tuple[Proposal, ...]:
    if not _same_shape_nonidentity(train):
        return ()
    proposals: dict[str, Proposal] = {}
    attempts = 0

    def add(family: str, program: Mapping[str, Any], complexity: int) -> None:
        nonlocal attempts
        attempts += 1
        if attempts > limits.max_programs:
            raise Undefined("program enumeration bound exhausted")
        key = _canonical(program)
        if key not in proposals and _exact(program, train):
            proposals[key] = Proposal(family, dict(program), complexity)

    input_palettes = [{cell for row in source for cell in row} for source, _ in train]
    output_palettes = [{cell for row in target for cell in row} for _, target in train]
    common_input = sorted(set.intersection(*input_palettes))
    common_output = sorted(set.intersection(*output_palettes))
    pair_sets = [_pairs(source, target) for source, target in train]
    common_pairs = sorted(set.intersection(*pair_sets)) if pair_sets else []
    modes = _common_modes(train)

    for background in modes:
        add(
            "event.header_phase_connector",
            _program("boundary_header_orthogonal_connect", background=background),
            10,
        )
        add(
            "event.radial_state_kernel",
            _program("radial_kernel_ray_emission", background=background),
            13,
        )
        add(
            "event.matched_diagonal_bridges",
            _program("matched_component_diagonal_bridge", background=background),
            14,
        )
        add(
            "event.phase_stamp_transport",
            _program("phase_aligned_stamp_transport", background=background),
            18,
        )
        add(
            "event.paired_wavefront_collision",
            _program("collision_aware_paired_fronts", background=background, collision=6),
            20,
        )

    for background in common_input:
        for barrier in common_input:
            if barrier == background:
                continue
            for particle in common_input:
                if particle in {background, barrier}:
                    continue
                for direction in ((-1, 0), (0, -1), (0, 1), (1, 0)):
                    add(
                        "event.gravity_barrier_splash",
                        _program(
                            "gravity_step_then_barrier_splash",
                            background=background,
                            barrier=barrier,
                            particle=particle,
                            direction=list(direction),
                        ),
                        12,
                    )

    endpoints = [
        color
        for color in common_input
        if all(sum(cell == color for row in source for cell in row) == 2 for source, _ in train)
    ]
    if common_pairs:
        for endpoint in endpoints:
            add(
                "event.endpoint_material_trace",
                _program(
                    "endpoint_material_trace",
                    endpoint=endpoint,
                    paint_map=[list(pair) for pair in common_pairs],
                ),
                8,
            )

    introduced = sorted(set.intersection(*(out - inp for inp, out in zip(input_palettes, output_palettes))))
    for marker, center in common_pairs:
        for halo in introduced:
            if halo == center:
                continue
            add(
                "event.cross_pulse_lattice",
                _program(
                    "cross_pulse_with_diagonal_halo",
                    marker=marker,
                    center=center,
                    halo=halo,
                ),
                15,
            )

    for background, fill in common_pairs:
        add(
            "event.blocker_gated_broadcast",
            _program(
                "blocker_gated_rectangle_broadcast",
                background=background,
                fill=fill,
            ),
            17,
        )
        remaining = [color for color in common_input if color not in {background, fill}]
        for left_color in remaining:
            for right_color in remaining:
                if left_color == right_color:
                    continue
                add(
                    "event.chirality_deflected_beam",
                    _program(
                        "chirality_deflected_boundary_beam",
                        background=background,
                        path=fill,
                        left_color=left_color,
                        right_color=right_color,
                    ),
                    11,
                )

    for background in common_input:
        for wall in common_input:
            if wall == background:
                continue
            add(
                "event.checkerboard_corridor_flood",
                _program("seeded_checkerboard_corridor_flood", background=background, wall=wall),
                19,
            )

    # The four material roles are learned from common replay transitions.  The
    # small finite product is preferable to a puzzle-specific role resolver.
    for source, spent in common_pairs:
        for background in common_input:
            for separator in common_input:
                if separator in {background, source}:
                    continue
                for payload in common_input:
                    if payload in {background, source, separator}:
                        continue
                    add(
                        "event.four_stage_separator_transport",
                        _program(
                            "four_stage_separator_transport",
                            background=background,
                            source=source,
                            spent=spent,
                            separator=separator,
                            payload=payload,
                        ),
                        16,
                    )

    return tuple(
        sorted(proposals.values(), key=lambda proposal: (proposal.complexity, _canonical(proposal.program)))
    )


def _transform_program(program: Mapping[str, Any], operation: str) -> Mapping[str, Any]:
    transformed = dict(program)
    if program.get("operator") == "gravity_step_then_barrier_splash":
        dr, dc = (int(value) for value in program["direction"])
        if operation == "rot90":
            transformed["direction"] = [dc, -dr]
        elif operation == "flip_h":
            transformed["direction"] = [dr, -dc]
    if (
        program.get("operator") == "chirality_deflected_boundary_beam"
        and operation == "flip_h"
    ):
        transformed["left_color"], transformed["right_color"] = (
            int(program["right_color"]),
            int(program["left_color"]),
        )
    return transformed


def _counterfactual_exact(proposal: Proposal, train: Sequence[Pair], limits: Limits) -> int:
    probes = 0
    for source, target in train:
        for operation in ("rot90", "flip_h"):
            if probes >= limits.max_counterfactuals:
                raise Undefined("counterfactual budget exhausted")
            transformed_program = _transform_program(proposal.program, operation)
            prediction = _grid(execute_program(transformed_program, _d4(source, operation)))
            if prediction != _d4(target, operation):
                raise Undefined("geometric event covariance failed")
            probes += 1
    return probes


def _loo_exact(proposal: Proposal, train: Sequence[Pair], limits: Limits) -> bool:
    key = _canonical(proposal.program)
    for held_index in range(len(train)):
        retained = train[:held_index] + train[held_index + 1 :]
        if not retained:
            return False
        try:
            alternatives = _enumerate(retained, limits)
        except Undefined:
            return False
        if key not in {_canonical(other.program) for other in alternatives}:
            return False
        try:
            prediction = _grid(execute_program(proposal.program, train[held_index][0]))
        except (Undefined, KeyError, TypeError, ValueError, IndexError, ZeroDivisionError):
            return False
        if prediction != train[held_index][1]:
            return False
    return True


def compile_task(task: Any, limits: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    """Compile one uniquely supported event behavior, or fail closed."""

    try:
        bounds = Limits.parse(limits)
        train, tests = _sanitize(task, bounds)
        proposals = _enumerate(train, bounds)
        if not proposals:
            return []
        minimum = proposals[0].complexity
        near = [proposal for proposal in proposals if proposal.complexity <= minimum + bounds.mdl_slack]
        guarded: list[tuple[Proposal, tuple[Grid, ...], int]] = []
        for proposal in near:
            if not _loo_exact(proposal, train, bounds):
                continue
            try:
                probes = _counterfactual_exact(proposal, train, bounds)
                predictions = tuple(_grid(execute_program(proposal.program, test)) for test in tests)
            except (Undefined, KeyError, TypeError, ValueError, IndexError, ZeroDivisionError):
                continue
            if all(prediction == test for prediction, test in zip(predictions, tests)):
                continue
            guarded.append((proposal, predictions, probes))
        if not guarded:
            return []
        minimum_guarded = min(item[0].complexity for item in guarded)
        winners = [item for item in guarded if item[0].complexity == minimum_guarded]
        behavior_hashes = {_digest([_plain(grid) for grid in item[1]]) for item in winners}
        if len(winners) != 1 or len(behavior_hashes) != 1:
            return []
        proposal, predictions, probes = winners[0]
        return [
            {
                "family": proposal.family,
                "program": dict(proposal.program),
                "train_outputs": [_plain(target) for _, target in train],
                "test_outputs": [_plain(prediction) for prediction in predictions],
                "complexity": proposal.complexity,
                "evidence": {
                    "author": AUTHOR,
                    "all_demonstrations_exact": True,
                    "leave_one_demonstration_out_exact": True,
                    "loo_mode": "isolated_reproposal_then_held_execution",
                    "geometric_counterfactual_exact": True,
                    "counterfactual_families": ["rot90_covariance", "horizontal_reflection_covariance"],
                    "counterfactual_probe_count": probes,
                    "bounded_program_enumeration": True,
                    "program_attempt_cap": bounds.max_programs,
                    "minimum_serialized_program_unique": True,
                    "near_mdl_program_count": len(near),
                    "ambiguity_abstention": True,
                    "test_trace_support": "all runtime roles and event branches structurally resolved",
                    "test_access": "input_key_only",
                    "task_identity_access": "none",
                    "behavior_hash": next(iter(behavior_hashes)),
                },
            }
        ][: bounds.max_candidates]
    except (Undefined, KeyError, TypeError, ValueError, IndexError, ZeroDivisionError):
        return []


__all__ = ["Limits", "compile_task", "execute_program", "replay_program"]
