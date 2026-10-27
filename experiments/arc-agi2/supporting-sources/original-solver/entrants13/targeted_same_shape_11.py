"""Generation-11 same-shape structural entrant for PR-LASM Block 13.

The operations here are reusable, identity-blind geometry programs inferred
from demonstrations: corner-directed diagonal beams, recursive motif stamping,
component rectangle completion, separator projection, obstacle-deflected
ribbons, empty-diagonal selection, row bridging, distance-scaled marker
squares, aligned-point connection, reflection from a boundary wall, marker-
count translation, row shear, square spirals, binary-template extension, and
frequency-selected bars.

Only training outputs and test inputs are accepted.  Every returned program
exactly replays every demonstration, is deterministic and bounded, and has a
JSON-safe tournament record.

Author: Komorebi P.
"""

from __future__ import annotations

from collections import Counter, deque
from collections.abc import Mapping, Sequence
from hashlib import sha256
import json
from typing import Any, Callable, Iterable


Grid = tuple[tuple[int, ...], ...]
Cell = tuple[int, int]
SCHEMA = "komorebi.pr_lasm.block13.targeted_same_shape_11.program.v1"
ORTHOGONAL: tuple[Cell, ...] = ((-1, 0), (0, -1), (0, 1), (1, 0))
EIGHT: tuple[Cell, ...] = tuple(
    (dr, dc)
    for dr in (-1, 0, 1)
    for dc in (-1, 0, 1)
    if (dr, dc) != (0, 0)
)


class Undefined(ValueError):
    """The structural preconditions for a candidate are absent."""


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _digest(value: Any) -> str:
    return sha256(_canonical(value).encode("utf-8")).hexdigest()


def _grid(value: Any) -> Grid:
    if not isinstance(value, (list, tuple)) or not value:
        raise Undefined("grid must be nonempty")
    rows: list[tuple[int, ...]] = []
    width: int | None = None
    for raw_row in value:
        if not isinstance(raw_row, (list, tuple)) or not raw_row:
            raise Undefined("invalid grid row")
        row: list[int] = []
        for cell in raw_row:
            if isinstance(cell, bool) or not isinstance(cell, int) or not 0 <= cell <= 9:
                raise Undefined("invalid ARC color")
            row.append(int(cell))
        if width is None:
            width = len(row)
        elif len(row) != width:
            raise Undefined("ragged grid")
        rows.append(tuple(row))
    if len(rows) * int(width or 0) > 3_600:
        raise Undefined("grid exceeds finite bound")
    return tuple(rows)


def _plain(grid: Grid) -> list[list[int]]:
    return [list(row) for row in grid]


def _shape(grid: Grid) -> tuple[int, int]:
    return len(grid), len(grid[0])


def _mode(grid: Grid) -> int:
    counts = Counter(cell for row in grid for cell in row)
    return min(counts, key=lambda color: (-counts[color], color))


def _background(grid: Grid) -> int:
    """Use ARC's conventional zero when present, otherwise a stable mode."""

    return 0 if any(value == 0 for row in grid for value in row) else _mode(grid)


def _sanitize(task: Any) -> tuple[tuple[tuple[Grid, Grid], ...], tuple[Grid, ...]]:
    if not isinstance(task, Mapping):
        raise Undefined("task must be a mapping")
    raw_train, raw_test = task["train"], task["test"]
    if (
        not isinstance(raw_train, Sequence)
        or isinstance(raw_train, (str, bytes))
        or not raw_train
        or len(raw_train) > 12
        or not isinstance(raw_test, Sequence)
        or isinstance(raw_test, (str, bytes))
        or len(raw_test) > 12
    ):
        raise Undefined("invalid split")
    train: list[tuple[Grid, Grid]] = []
    tests: list[Grid] = []
    for example in raw_train:
        if not isinstance(example, Mapping):
            raise Undefined("invalid training example")
        source, target = _grid(example["input"]), _grid(example["output"])
        if _shape(source) != _shape(target):
            raise Undefined("same-shape entrant")
        train.append((source, target))
    for example in raw_test:
        if not isinstance(example, Mapping):
            raise Undefined("invalid test example")
        # Deliberately access only the permitted field.  In particular, do not
        # iterate the mapping or probe for output/answer/solution keys.
        tests.append(_grid(example["input"]))
    return tuple(train), tuple(tests)


def _palette(train: Sequence[tuple[Grid, Grid]]) -> tuple[int, ...]:
    return tuple(sorted({
        color
        for source, target in train
        for grid in (source, target)
        for row in grid
        for color in row
    }))


def _changed_pairs(train: Sequence[tuple[Grid, Grid]]) -> tuple[tuple[int, int], ...]:
    return tuple(sorted({
        (before, after)
        for source, target in train
        for source_row, target_row in zip(source, target)
        for before, after in zip(source_row, target_row)
        if before != after
    }))


def _components(grid: Grid, color: int, *, eight: bool = False) -> tuple[tuple[Cell, ...], ...]:
    height, width = _shape(grid)
    steps = EIGHT if eight else ORTHOGONAL
    seen: set[Cell] = set()
    result: list[tuple[Cell, ...]] = []
    for row in range(height):
        for col in range(width):
            if grid[row][col] != color or (row, col) in seen:
                continue
            seen.add((row, col))
            queue = deque([(row, col)])
            cells: list[Cell] = []
            while queue:
                current = queue.popleft()
                cells.append(current)
                for dr, dc in steps:
                    nxt = current[0] + dr, current[1] + dc
                    if (
                        0 <= nxt[0] < height
                        and 0 <= nxt[1] < width
                        and nxt not in seen
                        and grid[nxt[0]][nxt[1]] == color
                    ):
                        seen.add(nxt)
                        queue.append(nxt)
            result.append(tuple(sorted(cells)))
    if len(result) > 256:
        raise Undefined("too many components")
    return tuple(result)


def _require_changed(source: Grid, target: Grid) -> Grid:
    if source == target:
        raise Undefined("operation made no change")
    return target


def _corner_beams(grid: Grid, program: Mapping[str, Any]) -> Grid:
    marker = int(program["marker"])
    background = _background(grid)
    cells = [(r, c) for r, row in enumerate(grid) for c, value in enumerate(row) if value != background]
    if len(cells) != 4:
        raise Undefined("a full two-by-two seed is required")
    top, bottom = min(r for r, _ in cells), max(r for r, _ in cells)
    left, right = min(c for _, c in cells), max(c for _, c in cells)
    if bottom != top + 1 or right != left + 1 or set(cells) != {
        (top, left), (top, right), (bottom, left), (bottom, right)
    }:
        raise Undefined("seed is not a full two-by-two block")
    marker_cells = [(r, c) for r, c in cells if grid[r][c] == marker]
    payload = {grid[r][c] for r, c in cells if grid[r][c] != marker}
    if not marker_cells or len(payload) != 1:
        raise Undefined("marker/payload roles are ambiguous")
    paint = next(iter(payload))
    canvas = [list(row) for row in grid]
    for row, col in marker_cells:
        canvas[row][col] = paint
        vr = -1 if row == top else 1
        vc = -1 if col == left else 1
        for distance in range(max(_shape(grid)) + 1):
            target_row = row + vr * distance
            center_col = col + vc * distance
            if not 0 <= target_row < len(grid):
                continue
            for target_col in range(center_col - 1, center_col + 2):
                if 0 <= target_col < len(grid[0]) and canvas[target_row][target_col] in {
                    background, marker, paint
                }:
                    canvas[target_row][target_col] = paint
    return _require_changed(grid, tuple(tuple(row) for row in canvas))


def _recursive_motif_stamp(grid: Grid, program: Mapping[str, Any]) -> Grid:
    background = _background(grid)
    colors = {value for row in grid for value in row if value != background}
    if len(colors) != 1:
        raise Undefined("one motif color is required")
    paint = next(iter(colors))
    cells = [(r, c) for r, row in enumerate(grid) for c, value in enumerate(row) if value == paint]
    top, bottom = min(r for r, _ in cells), max(r for r, _ in cells)
    left, right = min(c for _, c in cells), max(c for _, c in cells)
    motif_height, motif_width = bottom - top + 1, right - left + 1
    height, width = _shape(grid)
    if height != motif_height * motif_height or width != motif_width * motif_width:
        raise Undefined("canvas is not the motif's recursive scale")
    if top % motif_height or left % motif_width:
        raise Undefined("motif is not tile-aligned")
    support = {(r - top, c - left) for r, c in cells}
    if (top // motif_height, left // motif_width) not in support:
        raise Undefined("motif does not select its source tile")
    canvas = [[background for _ in range(width)] for _ in range(height)]
    for meta_row, meta_col in support:
        for shape_row, shape_col in support:
            canvas[meta_row * motif_height + shape_row][meta_col * motif_width + shape_col] = paint
    return _require_changed(grid, tuple(tuple(row) for row in canvas))


def _fill_component_bboxes(grid: Grid, program: Mapping[str, Any]) -> Grid:
    source, paint = int(program["source"]), int(program["paint"])
    background = _background(grid)
    components = list(_components(grid, source, eight=False))
    if not components:
        raise Undefined("source components absent")
    # A singleton diagonally touching one substantial orthogonal component is
    # a detached corner of that object; absorb it.  Two substantial shapes
    # that merely touch corners remain separate objects.
    groups = [set(component) for component in components if len(component) > 1]
    singletons = [component[0] for component in components if len(component) == 1]
    if not groups:
        groups = [{point} for point in singletons]
        singletons = []
    for point in singletons:
        neighbors = [
            group for group in groups
            if any(max(abs(point[0] - row), abs(point[1] - col)) == 1 for row, col in group)
        ]
        if len(neighbors) == 1:
            neighbors[0].add(point)
        else:
            groups.append({point})
    canvas = [list(row) for row in grid]
    for component in groups:
        top, bottom = min(r for r, _ in component), max(r for r, _ in component)
        left, right = min(c for _, c in component), max(c for _, c in component)
        for row in range(top, bottom + 1):
            for col in range(left, right + 1):
                if canvas[row][col] == background:
                    canvas[row][col] = paint
    return _require_changed(grid, tuple(tuple(row) for row in canvas))


def _separator_overlap_projection(grid: Grid, program: Mapping[str, Any]) -> Grid:
    paint = int(program["paint"])
    separator_color = int(program["separator"])
    background = _background(grid)
    height, width = _shape(grid)
    separators = [
        (row, grid[row][0])
        for row in range(height)
        if grid[row][0] == separator_color and all(value == separator_color for value in grid[row])
    ]
    if len(separators) != 1:
        raise Undefined("one horizontal separator is required")
    separator_row, separator_color = separators[0]
    runs: list[tuple[int, int, int, int]] = []
    for row in range(height):
        positions = [
            col for col, value in enumerate(grid[row])
            if value not in {background, separator_color}
        ]
        if positions:
            if positions != list(range(min(positions), max(positions) + 1)):
                raise Undefined("payload must be a horizontal run")
            colors = {grid[row][col] for col in positions}
            if len(colors) != 1:
                raise Undefined("payload run must be monochrome")
            runs.append((row, min(positions), max(positions), next(iter(colors))))
    if len(runs) != 2 or runs[0][0] >= separator_row or runs[1][0] <= separator_row:
        raise Undefined("opposed payload runs are required")
    upper, lower = runs
    if upper[3] != lower[3] or upper[2] - upper[1] == lower[2] - lower[1]:
        raise Undefined("one same-colored run must be shorter")
    overlap_left, overlap_right = max(upper[1], lower[1]), min(upper[2], lower[2])
    if overlap_left > overlap_right:
        raise Undefined("payload projections do not overlap")
    smaller_is_upper = upper[2] - upper[1] < lower[2] - lower[1]
    start = separator_row + 1 if smaller_is_upper else upper[0] + 1
    stop = lower[0] if smaller_is_upper else separator_row
    canvas = [list(row) for row in grid]
    for row in range(start, stop):
        for col in range(overlap_left, overlap_right + 1):
            if canvas[row][col] != background:
                raise Undefined("projection collides")
            canvas[row][col] = paint
    return _require_changed(grid, tuple(tuple(row) for row in canvas))


def _deflected_diagonal_ribbon(grid: Grid, program: Mapping[str, Any]) -> Grid:
    paint = int(program["paint"])
    background = _background(grid)
    height, width = _shape(grid)
    seeds = [(height - 1, col) for col, value in enumerate(grid[-1]) if value == paint]
    if len(seeds) != 1 or sum(value == paint for row in grid for value in row) != 1:
        raise Undefined("one bottom-edge ribbon seed is required")
    other_colors = {value for row in grid for value in row if value not in {background, paint}}
    if len(other_colors) > 1:
        raise Undefined("ribbon has multiple blocker colors")
    blocker = next(iter(other_colors)) if other_colors else None
    canvas = [list(row) for row in grid]
    state_start = seeds[0][1] - 1
    previous_start = seeds[0][1]
    previous_end = seeds[0][1]
    for row in range(height - 2, -1, -1):
        desired = state_start + 1
        new_start = desired
        blockers = [col for col in range(width) if blocker is not None and grid[row][col] == blocker]
        if any(desired <= col <= desired + 1 for col in blockers):
            # A horizontal blocker run pushes the ribbon just beyond its right
            # edge.  The row below bridges the old and new ribbon positions.
            new_start = max(blockers) + 1
            for col in range(previous_end + 1, new_start + 1):
                if 0 <= col < width and canvas[row + 1][col] == background:
                    canvas[row + 1][col] = paint
        for col in range(new_start, new_start + 2):
            if 0 <= col < width and canvas[row][col] == background:
                canvas[row][col] = paint
        previous_start, previous_end = new_start, new_start + 1
        state_start = new_start
    return _require_changed(grid, tuple(tuple(row) for row in canvas))


def _longest_empty_diagonal(grid: Grid, program: Mapping[str, Any]) -> Grid:
    paint = int(program["paint"])
    background = _background(grid)
    height, width = _shape(grid)
    runs: list[tuple[Cell, ...]] = []
    for dc in (-1, 1):
        for row in range(height):
            for col in range(width):
                if grid[row][col] != background:
                    continue
                predecessor = row - 1, col - dc
                if 0 <= predecessor[0] < height and 0 <= predecessor[1] < width and grid[predecessor[0]][predecessor[1]] == background:
                    continue
                cells: list[Cell] = []
                current_row, current_col = row, col
                while 0 <= current_row < height and 0 <= current_col < width and grid[current_row][current_col] == background:
                    cells.append((current_row, current_col))
                    current_row += 1
                    current_col += dc
                if len(cells) >= 2:
                    runs.append(tuple(cells))
    if not runs:
        raise Undefined("no empty diagonal run")
    longest = max(map(len, runs))
    winners = sorted(set(run for run in runs if len(run) == longest))
    if len(winners) != 1:
        # A corridor of odd width has several parallel longest diagonals; its
        # centerline is the canonical path.
        directions = {(run[1][1] - run[0][1]) for run in winners}
        if len(directions) != 1 or len(winners) % 2 == 0:
            raise Undefined("longest empty diagonal is tied")
        winners = [winners[len(winners) // 2]]
    canvas = [list(row) for row in grid]
    for row, col in winners[0]:
        canvas[row][col] = paint
    return _require_changed(grid, tuple(tuple(row) for row in canvas))


def _bridge_row_spans(grid: Grid, program: Mapping[str, Any]) -> Grid:
    source, paint = int(program["source"]), int(program["paint"])
    background = _background(grid)
    components = _components(grid, source)
    if len(components) < 2:
        raise Undefined("multiple bridge objects required")
    boxes = [
        (min(r for r, _ in component), max(r for r, _ in component),
         min(c for _, c in component), max(c for _, c in component))
        for component in components
    ]
    edges: list[tuple[int, int, int, int, int, int, int]] = []
    for first in range(len(boxes)):
        at, ab, al, ar = boxes[first]
        for second in range(first + 1, len(boxes)):
            bt, bb, bl, br = boxes[second]
            overlap_top, overlap_bottom = max(at, bt), min(ab, bb)
            if overlap_top > overlap_bottom:
                continue
            if ar < bl:
                gap_left, gap_right = ar + 1, bl - 1
            elif br < al:
                gap_left, gap_right = br + 1, al - 1
            else:
                continue
            edges.append((gap_right - gap_left + 1, overlap_top, gap_left,
                          first, second, overlap_bottom, gap_right))
    parent = list(range(len(components)))

    def root(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    canvas = [list(row) for row in grid]
    selected = 0
    for _, top, left, first, second, bottom, right in sorted(edges):
        first_root, second_root = root(first), root(second)
        if first_root == second_root:
            continue
        parent[second_root] = first_root
        selected += 1
        for row in range(top, bottom + 1):
            for col in range(left, right + 1):
                if canvas[row][col] == background:
                    canvas[row][col] = paint
    if selected != len(components) - 1:
        raise Undefined("horizontal bridge graph is disconnected")
    return _require_changed(grid, tuple(tuple(row) for row in canvas))


def _distance_marker_squares(grid: Grid, program: Mapping[str, Any]) -> Grid:
    center_color = int(program["center"])
    marker_color = int(program["marker"])
    paint = int(program["paint"])
    background = _background(grid)
    centers = [(r, c) for r, row in enumerate(grid) for c, value in enumerate(row) if value == center_color]
    markers = [(r, c) for r, row in enumerate(grid) for c, value in enumerate(row) if value == marker_color]
    if not centers or not markers:
        raise Undefined("centers and distance markers are required")
    if any(len(component) != 1 for component in _components(grid, center_color)):
        raise Undefined("centers must be singletons")
    if any(len(component) != 1 for component in _components(grid, marker_color)):
        raise Undefined("markers must be singletons")
    height, width = _shape(grid)
    canvas = [list(row) for row in grid]
    for center_row, center_col in centers:
        distance = min(max(abs(center_row - row), abs(center_col - col)) for row, col in markers)
        if distance < 2:
            raise Undefined("marker does not encode a positive radius")
        radius = distance - 1
        for row in range(max(0, center_row - radius), min(height, center_row + radius + 1)):
            for col in range(max(0, center_col - radius), min(width, center_col + radius + 1)):
                if canvas[row][col] == background:
                    canvas[row][col] = paint
    return _require_changed(grid, tuple(tuple(row) for row in canvas))


def _connect_aligned_points(grid: Grid, program: Mapping[str, Any]) -> Grid:
    source, paint = int(program["source"]), int(program["paint"])
    background = _background(grid)
    points = [(r, c) for r, row in enumerate(grid) for c, value in enumerate(row) if value == source]
    if not points or any(len(component) != 1 for component in _components(grid, source)):
        raise Undefined("singleton points are required")
    canvas = [list(row) for row in grid]
    for row in range(len(grid)):
        columns = [col for point_row, col in points if point_row == row]
        if len(columns) >= 2:
            for col in range(min(columns) + 1, max(columns)):
                if canvas[row][col] == background:
                    canvas[row][col] = paint
    for col in range(len(grid[0])):
        rows = [row for row, point_col in points if point_col == col]
        if len(rows) >= 2:
            for row in range(min(rows) + 1, max(rows)):
                if canvas[row][col] == background:
                    canvas[row][col] = paint
    # A grid with unaligned points legitimately remains unchanged; such demos
    # are important negative evidence for this operation.
    return tuple(tuple(row) for row in canvas)


def _reflect_diagonal_from_wall(grid: Grid, program: Mapping[str, Any]) -> Grid:
    wall, seed, paint = int(program["wall"]), int(program["seed"]), int(program["paint"])
    height, width = _shape(grid)
    background = _background(grid)
    row_walls = [row for row in range(height) if all(value == wall for value in grid[row])]
    col_walls = [col for col in range(width) if all(grid[row][col] == wall for row in range(height))]
    specifications: list[tuple[str, int]] = []
    if row_walls and row_walls == list(range(min(row_walls), height)):
        specifications.append(("bottom", min(row_walls)))
    if row_walls and row_walls == list(range(0, max(row_walls) + 1)):
        specifications.append(("top", max(row_walls)))
    if col_walls and col_walls == list(range(min(col_walls), width)):
        specifications.append(("right", min(col_walls)))
    if col_walls and col_walls == list(range(0, max(col_walls) + 1)):
        specifications.append(("left", max(col_walls)))
    if len(specifications) != 1:
        raise Undefined("one boundary wall slab is required")
    side, edge = specifications[0]
    seeds = [(r, c) for r, row in enumerate(grid) for c, value in enumerate(row) if value == seed]
    if len(seeds) < 2:
        raise Undefined("diagonal seed segment is required")
    seed_set = set(seeds)
    endpoints = [
        point for point in seeds
        if sum((point[0] + dr, point[1] + dc) in seed_set for dr, dc in ((-1, -1), (-1, 1), (1, -1), (1, 1))) == 1
    ]
    if len(endpoints) != 2 or len(seeds) != max(abs(endpoints[0][0] - endpoints[1][0]), abs(endpoints[0][1] - endpoints[1][1])) + 1:
        raise Undefined("seed is not one contiguous diagonal")
    distance = {
        "bottom": lambda p: edge - p[0],
        "top": lambda p: p[0] - edge,
        "right": lambda p: edge - p[1],
        "left": lambda p: p[1] - edge,
    }[side]
    ordered = sorted(endpoints, key=lambda point: (distance(point), point))
    if distance(ordered[0]) == distance(ordered[1]):
        raise Undefined("seed does not point toward wall")
    near, far = ordered
    dr = (near[0] > far[0]) - (near[0] < far[0])
    dc = (near[1] > far[1]) - (near[1] < far[1])
    if abs(dr) != 1 or abs(dc) != 1:
        raise Undefined("invalid seed direction")
    canvas = [list(row) for row in grid]
    current = near
    touched = False
    for _ in range(height + width + 2):
        nxt = current[0] + dr, current[1] + dc
        if not (0 <= nxt[0] < height and 0 <= nxt[1] < width):
            break
        if grid[nxt[0]][nxt[1]] == wall:
            touched = True
            break
        if canvas[nxt[0]][nxt[1]] != background:
            raise Undefined("incoming ray collides")
        canvas[nxt[0]][nxt[1]] = paint
        current = nxt
    if not touched:
        raise Undefined("ray does not reach wall")
    reflected = (-dr, dc) if side in {"top", "bottom"} else (dr, -dc)
    for _ in range(height + width + 2):
        nxt = current[0] + reflected[0], current[1] + reflected[1]
        if not (0 <= nxt[0] < height and 0 <= nxt[1] < width):
            break
        if canvas[nxt[0]][nxt[1]] != background:
            raise Undefined("reflected ray collides")
        canvas[nxt[0]][nxt[1]] = paint
        current = nxt
    return _require_changed(grid, tuple(tuple(row) for row in canvas))


def _translate_by_marker_count(grid: Grid, program: Mapping[str, Any]) -> Grid:
    marker = int(program["marker"])
    background = _background(grid)
    marker_cells = [(r, c) for r, row in enumerate(grid) for c, value in enumerate(row) if value == marker]
    payload = [(r, c, value) for r, row in enumerate(grid) for c, value in enumerate(row) if value not in {background, marker}]
    if not marker_cells or not payload or len({value for _, _, value in payload}) != 1:
        raise Undefined("one payload color and marker population required")
    offset = len(marker_cells)
    height, width = _shape(grid)
    paint = payload[0][2]
    full_rows = [row for row in range(height) if all(value == paint for value in grid[row])]
    full_cols = [col for col in range(width) if all(grid[row][col] == paint for row in range(height))]
    if len(full_rows) != 1 or len(full_cols) != 1:
        raise Undefined("payload must be one full cross")
    target_row, target_col = full_rows[0] + offset, full_cols[0] - offset
    if not (0 <= target_row < height and 0 <= target_col < width):
        raise Undefined("marker-count translation leaves canvas")
    canvas = [list(row) for row in grid]
    for row, col in marker_cells:
        canvas[row][col] = background
    for row, col, _ in payload:
        canvas[row][col] = background
    for col in range(width):
        canvas[target_row][col] = paint
    for row in range(height):
        canvas[row][target_col] = paint
    return _require_changed(grid, tuple(tuple(row) for row in canvas))


def _left_shear_by_bottom(grid: Grid, program: Mapping[str, Any]) -> Grid:
    background = _background(grid)
    colors = {value for row in grid for value in row if value != background}
    if len(colors) != 1:
        raise Undefined("one foreground color required")
    paint = next(iter(colors))
    cells = [(r, c) for r, row in enumerate(grid) for c, value in enumerate(row) if value == paint]
    bottom = max(row for row, _ in cells)
    canvas = [[background if value == paint else value for value in row] for row in grid]
    for row, col in cells:
        target_col = col - (bottom - row)
        if 0 <= target_col < len(grid[0]):
            if canvas[row][target_col] != background:
                raise Undefined("shear collision")
            canvas[row][target_col] = paint
    return _require_changed(grid, tuple(tuple(row) for row in canvas))


def _outward_square_spiral(grid: Grid, program: Mapping[str, Any]) -> Grid:
    paint = int(program["paint"])
    background = _background(grid)
    anchors = [(r, c) for r, row in enumerate(grid) for c, value in enumerate(row) if value == paint]
    if len(anchors) != 1:
        raise Undefined("one spiral anchor required")
    height, width = _shape(grid)
    canvas = [list(row) for row in grid]
    row, col = anchors[0]
    directions = ((-1, 0), (0, 1), (1, 0), (0, -1))
    segment_length = 2
    # Once the even side length exceeds this bound, all later square sides lie
    # strictly outside the finite canvas and cannot re-enter it.
    max_segment = 4 * (height + width + 2)
    direction_index = 0
    while segment_length <= max_segment:
        for _ in range(2):
            dr, dc = directions[direction_index % 4]
            direction_index += 1
            for _step in range(segment_length):
                row, col = row + dr, col + dc
                if 0 <= row < height and 0 <= col < width:
                    value = grid[row][col]
                    if value not in {background, paint}:
                        return _require_changed(grid, tuple(tuple(values) for values in canvas))
                    canvas[row][col] = paint
        segment_length += 2
    return _require_changed(grid, tuple(tuple(values) for values in canvas))


def _binary_template_extension(grid: Grid, program: Mapping[str, Any]) -> Grid:
    background = _background(grid)
    height, width = _shape(grid)
    rows = [
        (row, [value for value in grid[row] if value != background])
        for row in range(height)
        if any(value != background for value in grid[row])
    ]
    templates = [(row, values) for row, values in rows if len(values) == width and len(set(values)) == 2]
    if len(templates) != 1:
        raise Undefined("one full-width binary template required")
    template_row, template = templates[0]
    template_colors: list[int] = []
    for value in template:
        if value not in template_colors:
            template_colors.append(value)
    canvas = [list(row) for row in grid]
    changed = False
    for row, _ in rows:
        if row == template_row:
            continue
        prefix: list[int] = []
        for value in grid[row]:
            if value == background:
                break
            prefix.append(value)
        if not prefix or any(value != background for value in grid[row][len(prefix):]):
            raise Undefined("payload must be a left prefix")
        mapping: dict[int, int] = {}
        reverse: dict[int, int] = {}
        for source, target in zip(template, prefix):
            if source in mapping and mapping[source] != target:
                raise Undefined("prefix contradicts template")
            if target in reverse and reverse[target] != source:
                raise Undefined("prefix mapping is not one-to-one")
            mapping[source] = target
            reverse[target] = source
        if set(mapping) != set(template_colors):
            raise Undefined("prefix does not establish both template labels")
        expanded = [mapping[value] for value in template]
        if expanded != list(grid[row]):
            changed = True
        canvas[row] = expanded
    if not changed:
        raise Undefined("template is already extended")
    return tuple(tuple(row) for row in canvas)


def _frequency_selected_bars(grid: Grid, program: Mapping[str, Any]) -> Grid:
    marker = int(program["marker"])
    separator = int(program["separator"])
    background = _background(grid)
    height, width = _shape(grid)
    marker_runs: list[tuple[int, int]] = []
    for row in range(height):
        length = 0
        while length < width and grid[row][length] == marker:
            length += 1
        if length and all(value == background for value in grid[row][length:]):
            marker_runs.append((row, length))
    if len(marker_runs) != 1:
        raise Undefined("one horizontal marker run required")
    marker_row, marker_count = marker_runs[0]
    separators = [row for row in range(height) if all(value == separator for value in grid[row])]
    if len(separators) != 1:
        raise Undefined("one full separator row required")
    separator_row = separators[0]
    payload_rows = [
        row for row in range(separator_row + 1, height)
        if any(value != background for value in grid[row])
    ]
    if len(payload_rows) != 1 or marker_row >= separator_row:
        raise Undefined("one code row below separator required")
    code = grid[payload_rows[0]]
    counts = Counter(value for value in code if value != background)
    selected = {value for value, count in counts.items() if count == marker_count}
    if not selected:
        raise Undefined("no code color has marker frequency")
    filtered = tuple(value if value in selected else background for value in code)
    canvas = [list(row) for row in grid]
    for row in range(separator_row - marker_count, separator_row):
        if row < 0 or any(value != background for value in grid[row]):
            raise Undefined("bar placement area is occupied")
        canvas[row] = list(filtered)
    return _require_changed(grid, tuple(tuple(row) for row in canvas))


def _scaffold_axis_tiling(grid: Grid, program: Mapping[str, Any]) -> Grid:
    """Tile payload labels/patterns across rectangles delimited by scaffold arms."""

    scaffold = int(program["scaffold"])
    background = _background(grid)
    height, width = _shape(grid)
    canvas = [list(row) for row in grid]
    horizontal_runs: list[tuple[int, int, int]] = []
    for row in range(height):
        col = 0
        while col < width:
            if grid[row][col] != scaffold:
                col += 1
                continue
            start = col
            while col < width and grid[row][col] == scaffold:
                col += 1
            if col - start >= 2:
                horizontal_runs.append((row, start, col - 1))
    vertical_runs: list[tuple[int, int, int]] = []
    for col in range(width):
        row = 0
        while row < height:
            if grid[row][col] != scaffold:
                row += 1
                continue
            start = row
            while row < height and grid[row][col] == scaffold:
                row += 1
            if row - start >= 2:
                vertical_runs.append((col, start, row - 1))
    if not horizontal_runs and not vertical_runs:
        raise Undefined("no scaffold arm")

    applications = 0
    for bar_row, left, right in horizontal_runs:
        choices: list[tuple[int, list[tuple[int, int]]]] = []
        for anchor in (left, right):
            labels: list[tuple[int, int]] = []
            for row in range(height):
                value = grid[row][anchor]
                if row != bar_row and value not in {background, scaffold} and all(
                    grid[row][col] == background for col in range(left, right + 1) if col != anchor
                ):
                    labels.append((row, value))
            if labels:
                choices.append((anchor, labels))
        if len(choices) > 1:
            raise Undefined("horizontal scaffold endpoint is ambiguous")
        if choices:
            _, labels = choices[0]
            applications += 1
            for row, value in labels:
                for col in range(left, right + 1):
                    if canvas[row][col] not in {background, value}:
                        raise Undefined("horizontal scaffold fill collides")
                    canvas[row][col] = value

    for col, top, bottom in vertical_runs:
        pattern_rows = [
            row for row in range(top, bottom + 1)
            if (
                (col + 1 < width and grid[row][col + 1] not in {background, scaffold})
                or (col > 0 and grid[row][col - 1] not in {background, scaffold})
            )
        ]
        if not pattern_rows:
            continue
        if pattern_rows == list(range(top, max(pattern_rows) + 1)):
            template_rows = pattern_rows
        elif pattern_rows == list(range(min(pattern_rows), bottom + 1)):
            template_rows = pattern_rows
        else:
            raise Undefined("vertical scaffold templates must touch one end")
        non_scaffold_columns = [
            candidate
            for row in template_rows
            for candidate in range(width)
            if grid[row][candidate] not in {background, scaffold}
        ]
        if not non_scaffold_columns:
            continue
        if all(candidate > col for candidate in non_scaffold_columns):
            start_col, stop_col = col, max(non_scaffold_columns)
        elif all(candidate < col for candidate in non_scaffold_columns):
            start_col, stop_col = min(non_scaffold_columns), col
        else:
            raise Undefined("vertical scaffold payload straddles arm")
        templates = [tuple(grid[row][start_col:stop_col + 1]) for row in template_rows]
        applications += 1
        first_template = template_rows[0]
        for row in range(top, bottom + 1):
            template = templates[(row - first_template) % len(templates)]
            for offset, value in enumerate(template):
                target_col = start_col + offset
                if canvas[row][target_col] not in {background, scaffold, value}:
                    raise Undefined("vertical scaffold tiling collides")
                canvas[row][target_col] = value
    if not applications:
        raise Undefined("scaffold has no payload")
    return _require_changed(grid, tuple(tuple(row) for row in canvas))


def _marker_tiled_template_stamp(grid: Grid, program: Mapping[str, Any]) -> Grid:
    scaffold, marker = int(program["scaffold"]), int(program["marker"])
    background = _background(grid)
    height, width = _shape(grid)
    separators = [
        col for col in range(width)
        if all(grid[row][col] == scaffold for row in range(height))
    ]
    if len(separators) != 1:
        raise Undefined("one full-height template separator required")
    separator = separators[0]
    side_specs: list[tuple[int, int, int, int]] = []
    # (template_left, template_right, region_left, region_right)
    if separator > 0:
        side_specs.append((0, separator - 1, separator + 1, width - 1))
    if separator + 1 < width:
        side_specs.append((separator + 1, width - 1, 0, separator - 1))
    valid: list[tuple[int, int, int, int, int, int, tuple[tuple[int, ...], ...]]] = []
    for template_left, template_right, region_left, region_right in side_specs:
        template_cells = [
            (row, col) for row in range(height) for col in range(template_left, template_right + 1)
            if grid[row][col] != background
        ]
        if not template_cells:
            continue
        top, bottom = min(r for r, _ in template_cells), max(r for r, _ in template_cells)
        left, right = min(c for _, c in template_cells), max(c for _, c in template_cells)
        tile_height, tile_width = bottom - top + 1, right - left + 1
        if top != 0 or left != template_left or right != template_right:
            continue
        if height % tile_height or (region_right - region_left + 1) % tile_width:
            continue
        raster = tuple(tuple(grid[row][col] for col in range(left, right + 1)) for row in range(tile_height))
        if any(value == background for row in raster for value in row):
            continue
        region_values = {
            grid[row][col] for row in range(height) for col in range(region_left, region_right + 1)
        }
        if not region_values <= {background, marker} or marker not in region_values:
            continue
        valid.append((region_left, region_right, tile_height, tile_width, left, right, raster))
    if len(valid) != 1:
        raise Undefined("template side is ambiguous")
    region_left, region_right, tile_height, tile_width, _, _, raster = valid[0]
    markers = [
        (row, col) for row in range(height) for col in range(region_left, region_right + 1)
        if grid[row][col] == marker
    ]
    canvas = [list(row) for row in grid]
    for row, col in markers:
        canvas[row][col] = background
    occupied_tiles: set[tuple[int, int]] = set()
    for row, col in markers:
        origin_row = (row // tile_height) * tile_height
        origin_col = region_left + ((col - region_left) // tile_width) * tile_width
        tile = origin_row, origin_col
        if tile in occupied_tiles:
            raise Undefined("multiple markers select one tile")
        occupied_tiles.add(tile)
        for dr in range(tile_height):
            for dc in range(tile_width):
                target_row, target_col = origin_row + dr, origin_col + dc
                if canvas[target_row][target_col] != background:
                    raise Undefined("template stamp collides")
                canvas[target_row][target_col] = raster[dr][dc]
    return _require_changed(grid, tuple(tuple(row) for row in canvas))


def _marker_select_u_or_edge(grid: Grid, program: Mapping[str, Any]) -> Grid:
    marker, frame, paint = (
        int(program["marker"]), int(program["frame"]), int(program["paint"])
    )
    background = _background(grid)
    height, width = _shape(grid)
    markers = [(r, c) for r, row in enumerate(grid) for c, value in enumerate(row) if value == marker]
    if len(markers) != 1:
        raise Undefined("one selector marker required")
    marker_row, marker_col = markers[0]
    frames: list[tuple[int, int, int, int]] = []
    for top in range(height - 1):
        for bottom in range(top + 1, height):
            for left in range(width - 2):
                for right in range(left + 2, width):
                    if not (left < marker_col < right):
                        continue
                    if not all(grid[row][left] == frame and grid[row][right] == frame for row in range(top, bottom + 1)):
                        continue
                    if not all(grid[bottom][col] == frame for col in range(left, right + 1)):
                        continue
                    if any(grid[row][col] != background for row in range(top, bottom) for col in range(left + 1, right)):
                        continue
                    # The maximal vertical sides identify one U rather than
                    # every suffix of the same frame.
                    if top > 0 and grid[top - 1][left] == frame and grid[top - 1][right] == frame:
                        continue
                    frames.append((top, bottom, left, right))
    canvas = [list(row) for row in grid]
    canvas[marker_row][marker_col] = background
    if frames:
        # Nested complete U-frames are structurally ambiguous.
        if len(frames) != 1:
            raise Undefined("selector points into multiple complete U-frames")
        top, bottom, left, right = frames[0]
        for row in range(top, bottom):
            for col in range(left + 1, right):
                canvas[row][col] = paint
    else:
        if marker_row >= height // 2:
            edge_row = 0
        else:
            edge_row = height - 1
        if any(value != background for value in canvas[edge_row]):
            raise Undefined("fallback edge is occupied")
        canvas[edge_row] = [paint] * width
    return _require_changed(grid, tuple(tuple(row) for row in canvas))


EXECUTORS: dict[str, Callable[[Grid, Mapping[str, Any]], Grid]] = {
    "corner_beams": _corner_beams,
    "recursive_motif_stamp": _recursive_motif_stamp,
    "fill_component_bboxes": _fill_component_bboxes,
    "separator_overlap_projection": _separator_overlap_projection,
    "deflected_diagonal_ribbon": _deflected_diagonal_ribbon,
    "longest_empty_diagonal": _longest_empty_diagonal,
    "bridge_row_spans": _bridge_row_spans,
    "distance_marker_squares": _distance_marker_squares,
    "connect_aligned_points": _connect_aligned_points,
    "reflect_diagonal_from_wall": _reflect_diagonal_from_wall,
    "translate_by_marker_count": _translate_by_marker_count,
    "left_shear_by_bottom": _left_shear_by_bottom,
    "outward_square_spiral": _outward_square_spiral,
    "binary_template_extension": _binary_template_extension,
    "frequency_selected_bars": _frequency_selected_bars,
    "scaffold_axis_tiling": _scaffold_axis_tiling,
    "marker_tiled_template_stamp": _marker_tiled_template_stamp,
    "marker_select_u_or_edge": _marker_select_u_or_edge,
}


def execute_program(program: Mapping[str, Any], value: Any) -> list[list[int]]:
    if not isinstance(program, Mapping) or program.get("schema") != SCHEMA:
        raise ValueError("invalid targeted-same-shape-11 program")
    op = str(program.get("op"))
    if op not in EXECUTORS:
        raise ValueError("unknown targeted-same-shape-11 operation")
    return _plain(EXECUTORS[op](_grid(value), program))


def _record(op: str, **parameters: Any) -> dict[str, Any]:
    return {"schema": SCHEMA, "op": op, **parameters}


def _programs(train: Sequence[tuple[Grid, Grid]]) -> list[tuple[int, str, dict[str, Any]]]:
    colors = _palette(train)
    pairs = _changed_pairs(train)
    before = tuple(sorted({source for source, _ in pairs}))
    after = tuple(sorted({target for _, target in pairs}))
    structural: list[tuple[int, str, dict[str, Any]]] = [
        (4, "same_shape.recursive_motif_stamp", _record("recursive_motif_stamp")),
        (5, "same_shape.left_shear_by_bottom", _record("left_shear_by_bottom")),
        (6, "same_shape.binary_template_extension", _record("binary_template_extension")),
    ]
    result: list[tuple[int, str, dict[str, Any]]] = structural
    for paint in after:
        result.extend([
            (5, "same_shape.deflected_diagonal_ribbon", _record("deflected_diagonal_ribbon", paint=paint)),
            (5, "same_shape.longest_empty_diagonal", _record("longest_empty_diagonal", paint=paint)),
            (6, "same_shape.outward_square_spiral", _record("outward_square_spiral", paint=paint)),
        ])
        for separator in colors:
            result.append((5, "same_shape.separator_overlap_projection", _record(
                "separator_overlap_projection", separator=separator, paint=paint,
            )))
    for marker in before:
        result.append((5, "same_shape.corner_beams", _record("corner_beams", marker=marker)))
        result.append((6, "same_shape.translate_by_marker_count", _record("translate_by_marker_count", marker=marker)))
    for source in colors:
        for paint in after:
            if source == paint:
                continue
            result.extend([
                (5, "same_shape.fill_component_bboxes", _record("fill_component_bboxes", source=source, paint=paint)),
                (4, "same_shape.bridge_row_spans", _record("bridge_row_spans", source=source, paint=paint)),
                (4, "same_shape.connect_aligned_points", _record("connect_aligned_points", source=source, paint=paint)),
            ])
    for center in colors:
        for marker in colors:
            if center == marker:
                continue
            for paint in after:
                result.append((6, "same_shape.distance_marker_squares", _record(
                    "distance_marker_squares", center=center, marker=marker, paint=paint,
                )))
    for wall in colors:
        for seed in colors:
            if wall == seed:
                continue
            for paint in after:
                if paint not in {wall, seed}:
                    result.append((6, "same_shape.reflect_diagonal_from_wall", _record(
                        "reflect_diagonal_from_wall", wall=wall, seed=seed, paint=paint,
                    )))
    for marker in colors:
        for separator in colors:
            if marker != separator:
                result.append((6, "same_shape.frequency_selected_bars", _record(
                    "frequency_selected_bars", marker=marker, separator=separator,
                )))
        result.append((6, "same_shape.scaffold_axis_tiling", _record(
            "scaffold_axis_tiling", scaffold=marker,
        )))
        for stamp_marker in colors:
            if stamp_marker != marker:
                result.append((6, "same_shape.marker_tiled_template_stamp", _record(
                    "marker_tiled_template_stamp", scaffold=marker, marker=stamp_marker,
                )))
                for paint in after:
                    result.append((7, "same_shape.marker_select_u_or_edge", _record(
                        "marker_select_u_or_edge", marker=marker, frame=stamp_marker, paint=paint,
                    )))
    unique: dict[str, tuple[int, str, dict[str, Any]]] = {}
    for item in result:
        key = _canonical(item[2])
        old = unique.get(key)
        if old is None or item[:2] < old[:2]:
            unique[key] = item
    return sorted(unique.values(), key=lambda item: (item[0], item[1], _canonical(item[2])))[:20_000]


def compile_task(task: Any, limits: Any = None) -> list[dict[str, Any]]:
    try:
        train, tests = _sanitize(task)
        if limits is not None and not isinstance(limits, Mapping):
            raise Undefined("limits must be a mapping")
        candidate_cap = 64
        if isinstance(limits, Mapping):
            declared: list[int] = []
            for name in ("max_candidates", "max_programs", "candidate_cap"):
                if name not in limits:
                    continue
                value = limits[name]
                if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                    raise Undefined(f"invalid limit {name}")
                declared.append(value)
            if declared:
                candidate_cap = min(64, *declared)
            candidate_cap = min(candidate_cap, 256)
        if all(source == target for source, target in train):
            return []
    except (KeyError, TypeError, ValueError, OverflowError):
        return []

    candidates: dict[str, dict[str, Any]] = {}
    mechanisms: dict[str, set[str]] = {}
    for complexity, family, program in _programs(train):
        try:
            replay = [execute_program(program, source) for source, _ in train]
            if any(_grid(prediction) != target for prediction, (_, target) in zip(replay, train)):
                continue
            predictions = [execute_program(program, source) for source in tests]
        except (KeyError, TypeError, ValueError, IndexError, ArithmeticError, StopIteration):
            continue
        behavior = _digest(predictions)
        mechanisms.setdefault(behavior, set()).add(family)
        candidate = {
            "family": family,
            "program": program,
            "train_outputs": replay,
            "test_outputs": predictions,
            "complexity": complexity,
            "evidence": {
                "all_demos_exact": True,
                "demonstrations": len(train),
                "label_access": "training_outputs_only",
                "structural_preconditions_fail_closed": True,
            },
        }
        old = candidates.get(behavior)
        if old is None or (complexity, family, _canonical(program)) < (
            old["complexity"], old["family"], _canonical(old["program"])
        ):
            candidates[behavior] = candidate
    output: list[dict[str, Any]] = []
    for behavior, candidate in candidates.items():
        candidate["evidence"]["behavior_hash"] = behavior
        candidate["evidence"]["mechanism_support"] = len(mechanisms[behavior])
        candidate["evidence"]["equivalent_families"] = sorted(mechanisms[behavior])
        output.append(candidate)
    output.sort(key=lambda candidate: (
        candidate["complexity"],
        -candidate["evidence"]["mechanism_support"],
        candidate["family"],
        _canonical(candidate["program"]),
    ))
    return output[:candidate_cap]


__all__ = ["SCHEMA", "compile_task", "execute_program"]
