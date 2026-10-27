"""Proof-carrying multi-object motion and transport compiler for Block 15.

The entrant searches a small, finite language of object-preserving programs:
particles may be transported to repeated anchors, pushed to a canvas boundary
by adjacent markers, attracted along anchor corridors, dropped under a
size-threshold gravity rule, packed against a same-colour parent object, or
placed into count-matched frame slots.  Roles are inferred from each grid;
task identifiers and held-out labels are not accepted by the runtime.

Every proposal exactly replays all demonstrations, has one complete held-test
behaviour, survives leave-one-demonstration-out re-induction, and passes D4
and palette counterfactuals.  Undefined roles, collisions, truncated searches,
and competing held behaviours abstain.

Author: Komorebi P.
"""

from __future__ import annotations

from collections import Counter, deque
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
SCHEMA = "komorebi.pr_lasm.block15.motion_transport_compiler.program.v1"


class Undefined(ValueError):
    """A required relational role or collision-free transport is undefined."""


@dataclass(frozen=True, slots=True)
class Limits:
    max_grid_cells: int = 900
    max_examples: int = 20
    max_programs: int = 512
    max_executor_calls: int = 50_000
    max_components: int = 256
    max_counterfactuals: int = 2_048
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
            "max_programs": 4_096,
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
    train: list[Pair] = []
    for example in raw_train:
        if not isinstance(example, Mapping):
            raise Undefined("training example is invalid")
        train.append(
            (_grid(example.get("input"), limits), _grid(example.get("output"), limits))
        )
    tests: list[Grid] = []
    for example in raw_test:
        if not isinstance(example, Mapping):
            raise Undefined("test example is invalid")
        # Fetch only the held input.  An injected output member is never read.
        tests.append(_grid(example.get("input"), limits))
    return tuple(train), tuple(tests)


def _background(grid: Grid) -> int:
    counts = Counter(cell for row in grid for cell in row)
    maximum = max(counts.values())
    winners = [colour for colour, count in counts.items() if count == maximum]
    if len(winners) != 1:
        raise Undefined("background mode is tied")
    return winners[0]


def _palette(grid: Grid) -> frozenset[int]:
    return frozenset(cell for row in grid for cell in row)


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


def _components(
    grid: Grid, limits: Limits, *, colour: int | None = None
) -> tuple[tuple[int, frozenset[Cell]], ...]:
    background = _background(grid)
    remaining = {
        (row, column)
        for row, values in enumerate(grid)
        for column, value in enumerate(values)
        if value != background and (colour is None or value == colour)
    }
    result: list[tuple[int, frozenset[Cell]]] = []
    while remaining:
        seed = min(remaining)
        remaining.remove(seed)
        seed_colour = grid[seed[0]][seed[1]]
        queue = deque([seed])
        cells = {seed}
        while queue:
            row, column = queue.popleft()
            for dr, dc in ((-1, 0), (0, -1), (0, 1), (1, 0)):
                neighbour = row + dr, column + dc
                if neighbour not in remaining:
                    continue
                if grid[neighbour[0]][neighbour[1]] != seed_colour:
                    continue
                remaining.remove(neighbour)
                cells.add(neighbour)
                queue.append(neighbour)
        result.append((seed_colour, frozenset(cells)))
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
    """Return the D4 operation obtained by applying right, then left."""

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
    source_cells: set[Cell] = set()
    for _colour, source, _target in replacements:
        if source_cells & set(source):
            raise Undefined("mover sources overlap")
        source_cells.update(source)
    for row, column in source_cells:
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


def _nearest_anchor_shell(grid: Grid, program: Mapping[str, Any], limits: Limits) -> Grid:
    anchor_colour = int(program["anchor_colour"])
    components = _components(grid, limits)
    anchors = [cells for colour, cells in components if colour == anchor_colour]
    movers = [(colour, cells) for colour, cells in components if colour != anchor_colour]
    if len(anchors) < 2 or not movers or any(len(cells) != 1 for _, cells in movers):
        raise Undefined("repeated anchors and singleton particles are required")
    dimensions: list[tuple[int, int]] = []
    for anchor in anchors:
        if not _solid_rectangle(anchor, minimum_area=4):
            raise Undefined("anchors must be solid rectangles")
        top, bottom, left, right = _bbox(anchor)
        dimensions.append((bottom - top + 1, right - left + 1))
    if len(set(dimensions)) != 1:
        raise Undefined("anchor frames are not homologous")

    # Each particle follows one of the eight compass rays toward a unique
    # nearest anchor.  A contested shell site is awarded to the closest
    # particle.  Diagonal arrivals take the nearest free site on that same
    # shell; axial arrivals continue to the next unique anchor.  This is a
    # finite collision semantics, not a raster-specific placement table.
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

    def anchor_distance(point: Cell, anchor: frozenset[Cell]) -> int:
        return min(
            abs(point[0] - row) + abs(point[1] - column)
            for row, column in anchor
        )

    def compass_target(point: Cell, anchor: frozenset[Cell]) -> Cell:
        top, bottom, left, right = _bbox(anchor)
        dr = top - point[0] if point[0] < top else bottom - point[0] if point[0] > bottom else 0
        dc = left - point[1] if point[1] < left else right - point[1] if point[1] > right else 0
        radius = max(abs(dr), abs(dc))
        if radius <= 1:
            raise Undefined("particle already occupies an anchor shell")
        steps = radius - 1
        row_step = (1 if dr > 0 else -1 if dr < 0 else 0) * (
            steps if abs(dr) >= steps else 0
        )
        column_step = (1 if dc > 0 else -1 if dc < 0 else 0) * (
            steps if abs(dc) >= steps else 0
        )
        return point[0] + row_step, point[1] + column_step

    def choose_anchor(state: dict[str, Any]) -> None:
        point = state["point"]
        options = [
            (anchor_distance(point, anchor), index, anchor)
            for index, anchor in enumerate(anchors)
            if index not in state["banned"]
        ]
        if not options:
            raise Undefined("every anchor approach is collision-blocked")
        minimum = min(distance for distance, _, _ in options)
        winners = [item for item in options if item[0] == minimum]
        if len(winners) != 1:
            raise Undefined("nearest dynamic anchor is tied")
        _distance, index, anchor = winners[0]
        state["anchor"] = index
        state["target"] = compass_target(point, anchor)

    for state in states:
        choose_anchor(state)
    fixed_targets: set[Cell] = set()
    for _round in range(len(states) * max(2, len(anchors))):
        groups: dict[Cell, list[int]] = {}
        for index, state in enumerate(states):
            groups.setdefault(state["target"], []).append(index)
        conflicts = [(target, indices) for target, indices in groups.items() if len(indices) > 1]
        if not conflicts:
            break
        changed = False
        for target, indices in conflicts:
            ranked = sorted(
                (
                    abs(states[index]["point"][0] - target[0])
                    + abs(states[index]["point"][1] - target[1]),
                    index,
                )
                for index in indices
            )
            if len(ranked) > 1 and ranked[0][0] == ranked[1][0]:
                raise Undefined("equidistant particles contest one shell site")
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
                        and (
                            row in (top - 1, bottom + 1)
                            or column in (left - 1, right + 1)
                        )
                        and (row, column) not in fixed_targets
                        and (row, column) != states[winner]["target"]
                    ]
                    if not shell:
                        raise Undefined("anchor shell has no collision-free site")
                    costs = [
                        (abs(point[0] - row) + abs(point[1] - column), (row, column))
                        for row, column in shell
                    ]
                    minimum = min(cost for cost, _ in costs)
                    sites = [site for cost, site in costs if cost == minimum]
                    if len(sites) != 1:
                        raise Undefined("diagonal collision fallback is tied")
                    state["target"] = sites[0]
                else:
                    state["banned"].add(anchor_index)
                    choose_anchor(state)
                changed = True
        if not changed:
            raise Undefined("particle collision resolution made no progress")
    else:
        raise Undefined("particle collision resolution exceeded its finite bound")
    replacements = [
        (
            int(state["colour"]),
            state["source"],
            frozenset((state["target"],)),
        )
        for state in states
    ]
    return _render(grid, replacements)


def _marker_push_to_boundary(grid: Grid, program: Mapping[str, Any], limits: Limits) -> Grid:
    marker_colour = int(program["marker_colour"])
    components = _components(grid, limits)
    markers = frozenset(
        point
        for colour, cells in components
        if colour == marker_colour
        for point in cells
    )
    movers = [(colour, cells) for colour, cells in components if colour != marker_colour]
    if not markers or len(movers) < 2:
        raise Undefined("marker-push scene is incomplete")
    height, width = _shape(grid)
    replacements: list[tuple[int, frozenset[Cell], frozenset[Cell]]] = []
    moved = False
    for colour, cells in movers:
        directions: set[Cell] = set()
        for row, column in cells:
            if (row - 1, column) in markers:
                directions.add((1, 0))
            if (row + 1, column) in markers:
                directions.add((-1, 0))
            if (row, column - 1) in markers:
                directions.add((0, 1))
            if (row, column + 1) in markers:
                directions.add((0, -1))
        if len(directions) != 1:
            raise Undefined("a mover lacks one marker-defined push direction")
        dr, dc = next(iter(directions))
        top, bottom, left, right = _bbox(cells)
        distance = (
            top
            if dr < 0
            else height - 1 - bottom
            if dr > 0
            else left
            if dc < 0
            else width - 1 - right
        )
        moved = moved or distance > 0
        target = frozenset(
            (row + distance * dr, column + distance * dc) for row, column in cells
        )
        replacements.append((colour, cells, target))
    if not moved:
        raise Undefined("all pushed movers already touch their boundaries")
    return _render(grid, replacements)


def _pack_particles_against_parent(
    grid: Grid, _program: Mapping[str, Any], limits: Limits
) -> Grid:
    background = _background(grid)
    colours = sorted(_palette(grid) - {background})
    if len(colours) < 2:
        raise Undefined("at least two parent species are required")
    replacements: list[tuple[int, frozenset[Cell], frozenset[Cell]]] = []
    for colour in colours:
        components = [cells for _, cells in _components(grid, limits, colour=colour)]
        parents = [
            cells for cells in components if _solid_rectangle(cells, minimum_area=4)
        ]
        particle_cells = frozenset(
            point for cells in components if len(cells) == 1 for point in cells
        )
        # Adjacent particles may form incidental short runs before transport;
        # every cell outside the unique solid parent is still an atomic token.
        if len(parents) == 1:
            particle_cells = frozenset(
                point for cells in components if cells != parents[0] for point in cells
            )
        if (
            len(parents) != 1
            or not particle_cells
            or not _solid_rectangle(parents[0], minimum_area=4)
        ):
            raise Undefined("each species needs one solid parent and particle tokens")
        parent = parents[0]
        top, bottom, left, right = _bbox(parent)
        for point in sorted(particle_cells):
            particle = frozenset((point,))
            row, column = point
            nearest = (min(max(row, top), bottom), min(max(column, left), right))
            dr, dc = nearest[0] - row, nearest[1] - column
            radius = max(abs(dr), abs(dc))
            if radius <= 1:
                raise Undefined("particle already occupies the parent shell")
            steps = radius - 1
            destination = (
                row + (1 if dr > 0 else -1 if dr < 0 else 0) * min(steps, abs(dr)),
                column
                + (1 if dc > 0 else -1 if dc < 0 else 0) * min(steps, abs(dc)),
            )
            replacements.append((colour, particle, frozenset((destination,))))
    return _render(grid, replacements)


def _corridor_attraction(grid: Grid, program: Mapping[str, Any], limits: Limits) -> Grid:
    anchor_colour = int(program["anchor_colour"])
    mover_colour = int(program["mover_colour"])
    margin = int(program["corridor_margin"])
    if margin not in (0, 1) or anchor_colour == mover_colour:
        raise Undefined("invalid corridor program")
    components = _components(grid, limits)
    if any(colour not in {anchor_colour, mover_colour} for colour, _ in components):
        raise Undefined("corridor scene has an unmodelled foreground species")
    anchors = [cells for colour, cells in components if colour == anchor_colour]
    movers = [cells for colour, cells in components if colour == mover_colour]
    if len(anchors) < 2 or not movers or any(len(cells) != 1 for cells in movers):
        raise Undefined("corridor roles are incomplete")
    anchor_shapes: set[tuple[int, int]] = set()
    for anchor in anchors:
        if not _solid_rectangle(anchor, minimum_area=4):
            raise Undefined("corridor anchors must be solid rectangles")
        top, bottom, left, right = _bbox(anchor)
        anchor_shapes.add((bottom - top + 1, right - left + 1))
    if len(anchor_shapes) != 1:
        raise Undefined("corridor anchors are not homologous")

    replacements: list[tuple[int, frozenset[Cell], frozenset[Cell]]] = []
    moved = False
    for particle in movers:
        (point,) = tuple(particle)
        options: list[tuple[int, Cell]] = []
        for anchor in anchors:
            top, bottom, left, right = _bbox(anchor)
            row_aligned = top - margin <= point[0] <= bottom + margin
            column_aligned = left - margin <= point[1] <= right + margin
            if row_aligned == column_aligned:
                continue
            destination = (
                min(max(point[0], top - 1), bottom + 1),
                min(max(point[1], left - 1), right + 1),
            )
            distance = abs(destination[0] - point[0]) + abs(destination[1] - point[1])
            options.append((distance, destination))
        if not options:
            continue
        minimum = min(distance for distance, _ in options)
        winners = [destination for distance, destination in options if distance == minimum]
        if len(winners) != 1:
            raise Undefined("corridor target is tied")
        destination = winners[0]
        moved = moved or destination != point
        replacements.append((mover_colour, particle, frozenset((destination,))))
    if not moved:
        raise Undefined("no particle is transported through a corridor")
    # Unaligned particles are deliberately absent from replacements and stay put.
    return _render(grid, replacements)


def _gravity_by_area(grid: Grid, program: Mapping[str, Any], limits: Limits) -> Grid:
    minimum_area = int(program["minimum_area"])
    if minimum_area != 4:
        raise Undefined("gravity uses the grammar's non-tiny object threshold")
    background = _background(grid)
    if len(_palette(grid) - {background}) != 1:
        raise Undefined("area gravity needs one foreground species")
    components = _components(grid, limits)
    movers = [(colour, cells) for colour, cells in components if len(cells) >= minimum_area]
    fixed = {
        point for _colour, cells in components if len(cells) < minimum_area for point in cells
    }
    if not movers:
        raise Undefined("area gravity selects no component")
    height, width = _shape(grid)
    placed = set(fixed)
    replacements: list[tuple[int, frozenset[Cell], frozenset[Cell]]] = []
    changed = False
    # Bottommost movers settle first; selected sources are absent from the field.
    for colour, source in sorted(movers, key=lambda item: (-_bbox(item[1])[1], _bbox(item[1]))):
        current = set(source)
        distance = 0
        while True:
            successor = {(row + 1, column) for row, column in current}
            if any(row >= height or (row, column) in placed for row, column in successor):
                break
            current = successor
            distance += 1
        changed = changed or distance > 0
        target = frozenset(current)
        placed.update(target)
        replacements.append((colour, source, target))
    if not changed:
        raise Undefined("selected components cannot fall")
    return _render(grid, replacements)


def _orient_dominoes_to_markers(
    grid: Grid, program: Mapping[str, Any], limits: Limits
) -> Grid:
    marker_colour = int(program["marker_colour"])
    near_colour = int(program["near_colour"])
    far_colour = int(program["far_colour"])
    if len({marker_colour, near_colour, far_colour}) != 3:
        raise Undefined("domino roles must use three distinct colours")
    components = _components(grid, limits)
    markers = frozenset(
        point
        for colour, cells in components
        if colour == marker_colour
        for point in cells
    )
    near = frozenset(
        point
        for colour, cells in components
        if colour == near_colour
        for point in cells
    )
    far = frozenset(
        point
        for colour, cells in components
        if colour == far_colour
        for point in cells
    )
    if not markers or not near or len(near) != len(far):
        raise Undefined("marker-oriented domino roles are incomplete")
    pairs = sorted(
        (near_point, far_point)
        for near_point in near
        for far_point in far
        if abs(near_point[0] - far_point[0])
        + abs(near_point[1] - far_point[1])
        == 1
    )
    if not pairs:
        raise Undefined("no bichromatic domino edge exists")

    writes: dict[Cell, int] = {}
    aligned = 0
    for near_point, far_point in pairs:
        if near_point[0] == far_point[0]:
            candidates = [marker for marker in markers if marker[0] == near_point[0]]
        else:
            candidates = [marker for marker in markers if marker[1] == near_point[1]]
        if not candidates:
            continue
        distances = [
            (
                min(
                    abs(marker[0] - near_point[0]) + abs(marker[1] - near_point[1]),
                    abs(marker[0] - far_point[0]) + abs(marker[1] - far_point[1]),
                ),
                marker,
            )
            for marker in candidates
        ]
        minimum = min(distance for distance, _ in distances)
        winners = [marker for distance, marker in distances if distance == minimum]
        if len(winners) != 1:
            raise Undefined("aligned marker is tied")
        aligned += 1
        marker = winners[0]
        near_distance = abs(marker[0] - near_point[0]) + abs(marker[1] - near_point[1])
        far_distance = abs(marker[0] - far_point[0]) + abs(marker[1] - far_point[1])
        if near_distance == far_distance:
            raise Undefined("marker is equidistant from a domino")
        desired = (
            ((near_point, near_colour), (far_point, far_colour))
            if near_distance < far_distance
            else ((near_point, far_colour), (far_point, near_colour))
        )
        for point, colour in desired:
            previous = writes.get(point)
            if previous is not None and previous != colour:
                raise Undefined("overlapping domino edges imply conflicting colours")
            writes[point] = colour
    if not aligned:
        raise Undefined("no domino edge is aligned with a marker")
    changed = sum(grid[row][column] != colour for (row, column), colour in writes.items())
    if not changed:
        raise Undefined("no marker-oriented domino changes orientation")
    output = [list(row) for row in grid]
    for (row, column), colour in writes.items():
        output[row][column] = colour
    return _freeze(output)


def _rectangular_frames(
    grid: Grid, limits: Limits
) -> tuple[tuple[int, frozenset[Cell], tuple[int, int, int, int]], ...]:
    frames: list[tuple[int, frozenset[Cell], tuple[int, int, int, int]]] = []
    for colour, cells in _components(grid, limits):
        top, bottom, left, right = _bbox(cells)
        if bottom - top < 2 or right - left < 2:
            continue
        perimeter = frozenset(
            (row, column)
            for row in range(top, bottom + 1)
            for column in range(left, right + 1)
            if row in (top, bottom) or column in (left, right)
        )
        if cells == perimeter:
            frames.append((colour, cells, (top, bottom, left, right)))
    return tuple(sorted(frames, key=lambda item: item[2]))


def _pack_payloads_into_frames(
    grid: Grid, program: Mapping[str, Any], limits: Limits
) -> Grid:
    phase = int(program["checker_phase"])
    if phase not in (0, 1):
        raise Undefined("checker phase is invalid")
    background = _background(grid)
    frames = _rectangular_frames(grid, limits)
    if len(frames) < 2 or len({colour for colour, _, _ in frames}) != len(frames):
        raise Undefined("two uniquely coloured rectangular frames are required")
    frame_colours = {colour for colour, _, _ in frames}
    payload_colours = sorted(_palette(grid) - {background} - frame_colours)
    if len(payload_colours) != len(frames):
        raise Undefined("frame/payload arity differs")
    counts = Counter(cell for row in grid for cell in row if cell in payload_colours)
    assignments: list[tuple[int, ...]] = []
    for permutation in itertools.permutations(payload_colours):
        valid = True
        for payload, (_frame_colour, _cells, box) in zip(permutation, frames):
            top, bottom, left, right = box
            capacity = sum(
                (row - top - 1 + column - left - 1) % 2 == phase
                for row in range(top + 1, bottom)
                for column in range(left + 1, right)
            )
            valid = valid and counts[payload] == capacity
        if valid:
            assignments.append(permutation)
    if len(assignments) != 1:
        raise Undefined("count-matched frame assignment is absent or tied")

    replacements: list[tuple[int, frozenset[Cell], frozenset[Cell]]] = []
    for payload, (_frame_colour, _cells, box) in zip(assignments[0], frames):
        source = frozenset(
            (row, column)
            for row, values in enumerate(grid)
            for column, value in enumerate(values)
            if value == payload
        )
        top, bottom, left, right = box
        target = frozenset(
            (row, column)
            for row in range(top + 1, bottom)
            for column in range(left + 1, right)
            if (row - top - 1 + column - left - 1) % 2 == phase
        )
        replacements.append((payload, source, target))
    return _render(grid, replacements)


def _execute_core(program: Mapping[str, Any], grid: Grid, limits: Limits) -> Grid:
    operator = program.get("operator")
    if operator == "nearest_anchor_shell":
        return _nearest_anchor_shell(grid, program, limits)
    if operator == "marker_push_to_boundary":
        return _marker_push_to_boundary(grid, program, limits)
    if operator == "pack_particles_against_parent":
        return _pack_particles_against_parent(grid, program, limits)
    if operator == "corridor_attraction":
        return _corridor_attraction(grid, program, limits)
    if operator == "gravity_by_area":
        return _gravity_by_area(grid, program, limits)
    if operator == "orient_dominoes_to_markers":
        return _orient_dominoes_to_markers(grid, program, limits)
    if operator == "pack_payloads_into_frames":
        return _pack_payloads_into_frames(grid, program, limits)
    raise Undefined("unknown motion/transport operator")


def _execute_internal(program: Mapping[str, Any], grid: Grid, limits: Limits) -> Grid:
    if not isinstance(program, Mapping) or program.get("schema") != SCHEMA:
        raise Undefined("invalid motion/transport program")
    view = str(program.get("view", "id"))
    if view not in _D4:
        raise Undefined("invalid program view")
    oriented = _d4(grid, view)
    result = _execute_core(program, oriented, limits)
    return _d4(result, _inverse(view))


def execute_program(program: Mapping[str, Any], value: Any) -> list[list[int]]:
    """Execute one serialized, task-identity-free transport program."""

    limits = Limits()
    return _plain(_execute_internal(program, _grid(value, limits), limits))


def replay_program(program: Mapping[str, Any], value: Any) -> list[list[int]]:
    """Replay a serialized program independently of compiler caches."""

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


def _programs(demonstrations: Sequence[Pair]) -> tuple[dict[str, Any], ...]:
    colours = _common_colours(demonstrations)
    programs: list[dict[str, Any]] = []
    for colour in colours:
        programs.append(_program("nearest_anchor_shell", 7, anchor_colour=colour))
        programs.append(_program("marker_push_to_boundary", 8, marker_colour=colour))
    programs.append(_program("pack_particles_against_parent", 8))
    for anchor_colour, mover_colour in itertools.permutations(colours, 2):
        for margin in (0, 1):
            programs.append(
                _program(
                    "corridor_attraction",
                    9 + margin,
                    anchor_colour=anchor_colour,
                    mover_colour=mover_colour,
                    corridor_margin=margin,
                )
            )
    for view in ("id", "r90", "r180", "r270"):
        programs.append(
            _program(
                "gravity_by_area",
                6 + int(view != "id"),
                view=view,
                minimum_area=4,
            )
        )
    if len(colours) <= 6:
        for marker_colour, near_colour, far_colour in itertools.permutations(colours, 3):
            programs.append(
                _program(
                    "orient_dominoes_to_markers",
                    9,
                    marker_colour=marker_colour,
                    near_colour=near_colour,
                    far_colour=far_colour,
                )
            )
    for phase in (0, 1):
        programs.append(_program("pack_payloads_into_frames", 10, checker_phase=phase))
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
    calls = 0
    exact: list[dict[str, Any]] = []
    targets = tuple(target for _, target in demonstrations)
    for program in programs:
        try:
            train_outputs = _outputs(
                program, tuple(source for source, _ in demonstrations), limits
            )
            calls += len(demonstrations)
            _outputs(program, probes, limits)
            calls += len(probes)
        except (Undefined, TypeError, ValueError, KeyError, IndexError):
            continue
        if calls > limits.max_executor_calls:
            raise Undefined("executor-call bound exhausted")
        if train_outputs == targets:
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
        held_behaviours: dict[str, Grid] = {}
        for program in programs:
            try:
                output = _execute_internal(program, held_source, limits)
            except Undefined:
                continue
            held_behaviours[_digest(_plain(output))] = output
        if len(held_behaviours) != 1 or next(iter(held_behaviours.values())) != held_target:
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
    for key in (
        "anchor_colour",
        "mover_colour",
        "marker_colour",
        "near_colour",
        "far_colour",
    ):
        if key not in result:
            continue
        value = result[key]
        result[key] = right if value == left else left if value == right else value
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
                actual = _execute_internal(transformed_program, _d4(source, operation), limits)
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
    """Compile one proof-carrying motion behaviour, or abstain on ambiguity."""

    try:
        bounds = Limits.from_value(limits)
        demonstrations, tests = _sanitize(task, bounds)
        for source, target in demonstrations:
            if (
                _shape(source) != _shape(target)
                or source == target
                or Counter(cell for row in source for cell in row)
                != Counter(cell for row in target for cell in row)
            ):
                raise Undefined("motion lane requires a changed, histogram-preserving canvas")
        exact = _exact_programs(demonstrations, tests, bounds)
    except (Undefined, TypeError, ValueError, KeyError):
        return []
    if not exact:
        return []

    behaviours: dict[str, list[tuple[dict[str, Any], tuple[Grid, ...]]]] = {}
    for program in exact:
        try:
            outputs = _outputs(program, tests, bounds)
        except Undefined:
            continue
        behaviour_hash = _digest([_plain(output) for output in outputs])
        behaviours.setdefault(behaviour_hash, []).append((program, outputs))
    if len(behaviours) != 1:
        return []
    behaviour_hash, equivalents = next(iter(sorted(behaviours.items())))
    equivalents.sort(key=lambda item: (int(item[0]["description_length"]), _canonical(item[0])))

    loo_ok, loo_witnesses = _leave_one_out(demonstrations, tests, bounds)
    if not loo_ok:
        return []
    representative: dict[str, Any] | None = None
    gauge = (0, 0)
    for program, _ in equivalents:
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

    candidate = {
        "family": "motion_transport_compiler",
        "program": json.loads(_canonical(representative)),
        "train_outputs": [_plain(output) for output in train_outputs],
        "test_outputs": [_plain(output) for output in test_outputs],
        "complexity": int(representative["description_length"]),
        "evidence": {
            "all_demonstrations_exact": True,
            "exact_replay": True,
            "same_canvas": True,
            "histogram_preserved": True,
            "object_transport_semantics": True,
            "leave_one_demo_out_reinduction": True,
            "leave_one_out_witnesses": loo_witnesses,
            "enumeration_complete": True,
            "programs_enumerated": len(_programs(demonstrations)),
            "exact_programs": len(exact),
            "unique_inferred_program_semantics": True,
            "full_test_behavior_classes": 1,
            "full_test_behavior_hash": behaviour_hash,
            "equivalent_programs": len(equivalents),
            "d4_counterfactual_checks": gauge[0],
            "palette_counterfactual_checks": gauge[1],
            "bounded_search": True,
            "hard_caps_exhausted": False,
            "task_identity_observed": False,
            "held_test_access": "input_key_only",
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
    "Undefined",
    "compile_task",
    "execute_program",
    "replay_program",
]
