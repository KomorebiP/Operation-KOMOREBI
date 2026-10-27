"""Second-batch, same-shape structural entrant for PR-LASM Block 13.

This module contains reusable transformations inferred from demonstration-only
residual morphology: template transfer, marker-centred stamping, ranked solid
rectangle interiors, row labels, partial-frame completion, object docking,
half-run recolouring, periodic border continuation, and paired inward growth.
Every emitted program exactly replays every training pair; test outputs and task
metadata are neither accepted nor inspected.

Author: Komorebi P.
"""

from __future__ import annotations

from collections import Counter, deque
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from hashlib import sha256
import json
import math
from typing import Any, Callable, Iterable


Grid = tuple[tuple[int, ...], ...]
Cell = tuple[int, int]
SCHEMA = "komorebi.pr_lasm.block13.targeted_same_shape_2.program.v1"
STEPS: tuple[Cell, ...] = ((-1, 0), (0, -1), (0, 1), (1, 0))


class Undefined(ValueError):
    """A structural precondition is absent or ambiguous."""


@dataclass(frozen=True, slots=True)
class Obj:
    cells: tuple[tuple[int, int, int], ...]

    @property
    def top(self) -> int:
        return min(row for row, _, _ in self.cells)

    @property
    def bottom(self) -> int:
        return max(row for row, _, _ in self.cells)

    @property
    def left(self) -> int:
        return min(col for _, col, _ in self.cells)

    @property
    def right(self) -> int:
        return max(col for _, col, _ in self.cells)

    @property
    def height(self) -> int:
        return self.bottom - self.top + 1

    @property
    def width(self) -> int:
        return self.right - self.left + 1

    @property
    def area(self) -> int:
        return len(self.cells)

    @property
    def colors(self) -> frozenset[int]:
        return frozenset(color for _, _, color in self.cells)

    @property
    def support(self) -> frozenset[Cell]:
        return frozenset((row - self.top, col - self.left) for row, col, _ in self.cells)

    @property
    def raster(self) -> dict[Cell, int]:
        return {(row - self.top, col - self.left): color for row, col, color in self.cells}


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _digest(value: Any) -> str:
    return sha256(_canonical(value).encode("utf-8")).hexdigest()


def _grid(value: Any) -> Grid:
    if not isinstance(value, (list, tuple)) or not value:
        raise Undefined("grid must be nonempty")
    width: int | None = None
    rows: list[tuple[int, ...]] = []
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


def _sanitize(task: Any) -> tuple[tuple[tuple[Grid, Grid], ...], tuple[Grid, ...]]:
    if not isinstance(task, Mapping):
        raise Undefined("task must be a mapping")
    try:
        raw_train, raw_test = task["train"], task["test"]
    except (KeyError, TypeError) as error:
        raise Undefined("task lacks a split") from error
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
            raise Undefined("specialist accepts same-shape pairs only")
        train.append((source, target))
    for example in raw_test:
        if not isinstance(example, Mapping):
            raise Undefined("invalid test example")
        # Deliberately request only ``input``.  A supplied output/answer is not
        # queried through membership, iteration, get(), or indexing.
        tests.append(_grid(example["input"]))
    return tuple(train), tuple(tests)


def _shape(grid: Grid) -> tuple[int, int]:
    return len(grid), len(grid[0])


def _mode(grid: Grid) -> int:
    counts = Counter(cell for row in grid for cell in row)
    return min(counts, key=lambda color: (-counts[color], color))


def _components(grid: Grid, background: int, *, mono: bool) -> tuple[Obj, ...]:
    height, width = _shape(grid)
    seen: set[Cell] = set()
    result: list[Obj] = []
    for row in range(height):
        for col in range(width):
            if (row, col) in seen or grid[row][col] == background:
                continue
            seed = grid[row][col]
            seen.add((row, col))
            queue = deque([(row, col)])
            cells: list[tuple[int, int, int]] = []
            while queue:
                current_row, current_col = queue.popleft()
                cells.append((current_row, current_col, grid[current_row][current_col]))
                for dr, dc in STEPS:
                    next_row, next_col = current_row + dr, current_col + dc
                    if not (0 <= next_row < height and 0 <= next_col < width):
                        continue
                    if (next_row, next_col) in seen or grid[next_row][next_col] == background:
                        continue
                    if mono and grid[next_row][next_col] != seed:
                        continue
                    seen.add((next_row, next_col))
                    queue.append((next_row, next_col))
            result.append(Obj(tuple(sorted(cells))))
    if len(result) > 256:
        raise Undefined("too many components")
    return tuple(sorted(result, key=lambda obj: (obj.top, obj.left, obj.bottom, obj.right, obj.cells)))


def _changed_pairs(train: Sequence[tuple[Grid, Grid]]) -> tuple[tuple[int, int], ...]:
    return tuple(sorted({
        (before, after)
        for source, target in train
        for source_row, target_row in zip(source, target)
        for before, after in zip(source_row, target_row)
        if before != after
    }))


def _palette(train: Sequence[tuple[Grid, Grid]]) -> tuple[int, ...]:
    return tuple(sorted({
        color
        for source, target in train
        for grid in (source, target)
        for row in grid
        for color in row
    }))


def _unique(items: Iterable[Any], what: str) -> Any:
    values = tuple(items)
    if len(values) != 1:
        raise Undefined(f"{what} is not unique")
    return values[0]


def _recolor_lower_bbox_half(grid: Grid, program: Mapping[str, Any]) -> Grid:
    source, paint = int(program["source"]), int(program["paint"])
    positions = [(row, col) for row, values in enumerate(grid) for col, color in enumerate(values) if color == source]
    if not positions:
        raise Undefined("source color absent")
    top, bottom = min(row for row, _ in positions), max(row for row, _ in positions)
    threshold = top + (bottom - top + 1) // 2
    canvas = [list(row) for row in grid]
    for row, col in positions:
        if row >= threshold:
            canvas[row][col] = paint
    return tuple(tuple(row) for row in canvas)


def _recolor_lower_vertical_runs(grid: Grid, program: Mapping[str, Any]) -> Grid:
    source, paint = int(program["source"]), int(program["paint"])
    height, width = _shape(grid)
    canvas = [list(row) for row in grid]
    seen_any = False
    for col in range(width):
        row = 0
        while row < height:
            if grid[row][col] != source:
                row += 1
                continue
            start = row
            while row < height and grid[row][col] == source:
                row += 1
            length = row - start
            seen_any = True
            for changed_row in range(start + (length + 1) // 2, row):
                canvas[changed_row][col] = paint
    if not seen_any:
        raise Undefined("source color absent")
    return tuple(tuple(row) for row in canvas)


def _ranked_rectangle_interiors(grid: Grid, program: Mapping[str, Any]) -> Grid:
    background = int(program.get("background", _mode(grid)))
    frame = int(program["frame"])
    large_paint, small_paint = int(program["large_paint"]), int(program["small_paint"])
    objects = [obj for obj in _components(grid, background, mono=True) if obj.colors == {frame}]
    rectangles = []
    for obj in objects:
        full = {
            (row, col)
            for row in range(obj.top, obj.bottom + 1)
            for col in range(obj.left, obj.right + 1)
        }
        if {(row, col) for row, col, _ in obj.cells} == full and obj.height >= 3 and obj.width >= 3:
            rectangles.append(obj)
    if len(rectangles) != 2 or rectangles[0].height * rectangles[0].width == rectangles[1].height * rectangles[1].width:
        raise Undefined("two differently sized solid rectangles required")
    rectangles.sort(key=lambda obj: obj.height * obj.width)
    canvas = [list(row) for row in grid]
    for obj, paint in ((rectangles[0], small_paint), (rectangles[1], large_paint)):
        for row in range(obj.top + 1, obj.bottom):
            for col in range(obj.left + 1, obj.right):
                canvas[row][col] = paint
    return tuple(tuple(row) for row in canvas)


def _row_label_transfer(grid: Grid, program: Mapping[str, Any]) -> Grid:
    background, mask = _mode(grid), int(program["mask"])
    canvas = [list(row) for row in grid]
    changed = 0
    for row, values in enumerate(grid):
        labels = []
        for col, color in enumerate(values):
            if color not in {background, mask}:
                labels.append((col, color))
        if not labels:
            continue
        colors = {color for _, color in labels}
        if len(colors) != 1:
            raise Undefined("row label is ambiguous")
        label_col = min(col for col, _ in labels)
        mask_cols = [col for col, color in enumerate(values) if color == mask]
        if mask_cols and label_col >= min(mask_cols):
            raise Undefined("label must precede the mask")
        label = next(iter(colors))
        for col in mask_cols:
            canvas[row][col] = label
            changed += 1
    if not changed:
        raise Undefined("no labelled mask cells")
    return tuple(tuple(row) for row in canvas)


def _template_placeholders(grid: Grid, program: Mapping[str, Any]) -> Grid:
    background, placeholder = _mode(grid), int(program["placeholder"])
    mono = _components(grid, background, mono=True)
    placeholders = [obj for obj in mono if obj.colors == {placeholder}]
    if not placeholders:
        raise Undefined("no placeholders")
    foreground = _components(grid, background, mono=False)
    templates = [obj for obj in foreground if len(obj.colors) >= 2 and placeholder not in obj.colors]
    template = _unique(templates, "multicolor template")
    matching = [obj for obj in placeholders if obj.support == template.support]
    if not matching or len(matching) != len(placeholders):
        raise Undefined("placeholder support differs from template")
    canvas = [list(row) for row in grid]
    raster = template.raster
    for obj in matching:
        for row, col, _ in obj.cells:
            canvas[row][col] = raster[(row - obj.top, col - obj.left)]
    if bool(program.get("erase_template", False)):
        for row, col, _ in template.cells:
            canvas[row][col] = background
    return tuple(tuple(row) for row in canvas)


def _marker_center_copy(grid: Grid, program: Mapping[str, Any]) -> Grid:
    background, marker_color = _mode(grid), int(program["marker"])
    mono = _components(grid, background, mono=True)
    marker = _unique((obj for obj in mono if obj.colors == {marker_color} and obj.area == 1), "marker")
    marker_cell = (marker.cells[0][0], marker.cells[0][1])
    foreground = _components(grid, background, mono=False)
    templates = [obj for obj in foreground if marker_cell not in {(row, col) for row, col, _ in obj.cells} and obj.area > 1]
    template = _unique(templates, "template")
    top = marker_cell[0] - (template.height - 1) // 2
    left = marker_cell[1] - (template.width - 1) // 2
    height, width = _shape(grid)
    if top < 0 or left < 0 or top + template.height > height or left + template.width > width:
        raise Undefined("copy would leave canvas")
    canvas = [list(row) for row in grid]
    canvas[marker_cell[0]][marker_cell[1]] = background
    for (relative_row, relative_col), color in template.raster.items():
        canvas[top + relative_row][left + relative_col] = color
    return tuple(tuple(row) for row in canvas)


def _gapped_frame_fill_ray(grid: Grid, program: Mapping[str, Any]) -> Grid:
    background, frame, paint = _mode(grid), int(program["frame"]), int(program["paint"])
    objects = [obj for obj in _components(grid, background, mono=True) if obj.colors == {frame}]
    candidates: list[tuple[Obj, Cell]] = []
    for obj in objects:
        if obj.height < 3 or obj.width < 3:
            continue
        perimeter = {
            (row, col)
            for row in range(obj.top, obj.bottom + 1)
            for col in range(obj.left, obj.right + 1)
            if row in {obj.top, obj.bottom} or col in {obj.left, obj.right}
        }
        missing = perimeter - {(row, col) for row, col, _ in obj.cells}
        extras = {(row, col) for row, col, _ in obj.cells} - perimeter
        if len(missing) == 1 and not extras:
            candidates.append((obj, next(iter(missing))))
    obj, gap = _unique(candidates, "one-gap frame")
    canvas = [list(row) for row in grid]
    for row in range(obj.top + 1, obj.bottom):
        for col in range(obj.left + 1, obj.right):
            canvas[row][col] = paint
    height, width = _shape(grid)
    row, col = gap
    if row == obj.top:
        ray = ((rr, col) for rr in range(0, obj.top + 1))
    elif row == obj.bottom:
        ray = ((rr, col) for rr in range(obj.bottom, height))
    elif col == obj.left:
        ray = ((row, cc) for cc in range(0, obj.left + 1))
    elif col == obj.right:
        ray = ((row, cc) for cc in range(obj.right, width))
    else:
        raise Undefined("gap is not on frame")
    for rr, cc in ray:
        if canvas[rr][cc] not in {background, paint}:
            raise Undefined("ray is obstructed")
        canvas[rr][cc] = paint
    return tuple(tuple(values) for values in canvas)


def _dock_to_line(grid: Grid, program: Mapping[str, Any]) -> Grid:
    background, separator = _mode(grid), int(program["separator"])
    height, width = _shape(grid)
    mono = _components(grid, background, mono=True)
    full_rows = [
        (obj.top, next(iter(obj.colors)))
        for obj in mono
        if obj.height == 1 and obj.width == width and obj.area == width
    ]
    full_cols = [
        (obj.left, next(iter(obj.colors)))
        for obj in mono
        if obj.width == 1 and obj.height == height and obj.area == height
    ]
    orientation, index, line_color = _unique(
        [("row", row, color) for row, color in full_rows]
        + [("col", col, color) for col, color in full_cols],
        "separator line",
    )
    objects = [obj for obj in _components(grid, background, mono=False) if line_color not in obj.colors]
    obj = _unique(objects, "movable object")
    canvas = [list(row) for row in grid]
    for row, col, _ in obj.cells:
        canvas[row][col] = background
    if orientation == "row":
        if obj.bottom < index:
            top = index - obj.height
            separator_index = top - 1
        elif obj.top > index:
            top = index + 1
            separator_index = top + obj.height
        else:
            raise Undefined("object crosses docking line")
        left = obj.left
        if not 0 <= separator_index < height:
            raise Undefined("no room for trailing separator")
        for col in range(width):
            canvas[separator_index][col] = separator
    else:
        if obj.right < index:
            left = index - obj.width
            separator_index = left - 1
        elif obj.left > index:
            left = index + 1
            separator_index = left + obj.width
        else:
            raise Undefined("object crosses docking line")
        top = obj.top
        if not 0 <= separator_index < width:
            raise Undefined("no room for trailing separator")
        for row in range(height):
            canvas[row][separator_index] = separator
    for relative, color in obj.raster.items():
        row, col = top + relative[0], left + relative[1]
        if not (0 <= row < height and 0 <= col < width):
            raise Undefined("docked object leaves canvas")
        canvas[row][col] = color
    return tuple(tuple(row) for row in canvas)


def _bar_wedges(grid: Grid, program: Mapping[str, Any]) -> Grid:
    background = _mode(grid)
    bar_color = int(program["bar"])
    above, below = int(program["above"]), int(program["below"])
    objects = [obj for obj in _components(grid, background, mono=True) if obj.colors == {bar_color}]
    bar = _unique((obj for obj in objects if obj.height == 1 and obj.width == obj.area), "horizontal bar")
    # The demonstrated construction grows into the larger horizontal side.
    left_room, right_room = bar.left, len(grid[0]) - 1 - bar.right
    if left_room == right_room:
        raise Undefined("bar growth direction is tied")
    direction = 1 if right_room > left_room else -1
    canvas = [list(row) for row in grid]
    for distance in range(1, bar.top + 1):
        row = bar.top - distance
        length = bar.width + distance
        start = bar.left if direction == 1 else bar.right - length + 1
        for col in range(start, start + length):
            if 0 <= col < len(grid[0]):
                canvas[row][col] = above
    for distance in range(1, len(grid) - bar.bottom):
        length = bar.width - distance
        if length <= 0:
            break
        row = bar.bottom + distance
        start = bar.left if direction == 1 else bar.right - length + 1
        for col in range(start, start + length):
            if 0 <= col < len(grid[0]):
                canvas[row][col] = below
    return tuple(tuple(row) for row in canvas)


def _paired_inward_extrude(grid: Grid, program: Mapping[str, Any]) -> Grid:
    background = _mode(grid)
    objects = _components(grid, background, mono=True)
    if len(objects) != 2 or any(obj.area != obj.height * obj.width for obj in objects):
        raise Undefined("two solid objects required")
    first, second = objects
    canvas = [list(row) for row in grid]
    height, width = _shape(grid)
    if first.right < second.left and first.height == second.height and first.top == second.top:
        left, right = first, second
        gap = list(range(left.right + 1, right.left))
        half = len(gap) // 2
        for col in gap[:half]:
            for row in range(height):
                canvas[row][col] = next(iter(left.colors))
        for col in gap[len(gap) - half:]:
            for row in range(height):
                canvas[row][col] = next(iter(right.colors))
    elif first.bottom < second.top and first.width == second.width and first.left == second.left:
        top_obj, bottom_obj = first, second
        gap = list(range(top_obj.bottom + 1, bottom_obj.top))
        half = len(gap) // 2
        for row in gap[:half]:
            for col in range(width):
                canvas[row][col] = next(iter(top_obj.colors))
        for row in gap[len(gap) - half:]:
            for col in range(width):
                canvas[row][col] = next(iter(bottom_obj.colors))
    else:
        raise Undefined("objects are not opposed and aligned")
    return tuple(tuple(row) for row in canvas)


def _shift_periodic_border(grid: Grid, program: Mapping[str, Any]) -> Grid:
    height, width = _shape(grid)
    # Find a color occupying a complete lower row and complete right column;
    # the upper-left rectangle before those suffixes is the observed tile.
    candidates: list[tuple[int, int, int]] = []
    for border in sorted({cell for row in grid for cell in row}):
        full_rows = [row for row in range(height) if all(grid[row][col] == border for col in range(width))]
        full_cols = [col for col in range(width) if all(grid[row][col] == border for row in range(height))]
        if not full_rows or not full_cols:
            continue
        tile_height, tile_width = min(full_rows), min(full_cols)
        if tile_height >= 2 and tile_width >= 2:
            candidates.append((border, tile_height, tile_width))
    _, tile_height, tile_width = _unique(candidates, "periodic border")
    tile = tuple(tuple(grid[row][col] for col in range(tile_width)) for row in range(tile_height))
    # Determine fundamental row/column periods of the observed tile.
    row_period = next(
        period for period in range(1, tile_height + 1)
        if all(tile[row][col] == tile[row % period][col] for row in range(tile_height) for col in range(tile_width))
    )
    col_period = next(
        period for period in range(1, tile_width + 1)
        if all(tile[row][col] == tile[row][col % period] for row in range(tile_height) for col in range(tile_width))
    )
    if col_period < 2:
        raise Undefined("horizontal phase shift is vacuous")
    output = tuple(
        tuple(tile[row % row_period][(col + 1) % col_period] for col in range(width))
        for row in range(height)
    )
    return output


def _extend_lines_to_canvas(grid: Grid, program: Mapping[str, Any]) -> Grid:
    """Extend every isolated monochrome segment along its demonstrated axis."""

    background = _mode(grid)
    objects = _components(grid, background, mono=True)
    if not objects:
        raise Undefined("no line objects")
    horizontal: list[Obj] = []
    vertical: list[Obj] = []
    for obj in objects:
        if obj.height == 1 and obj.width == obj.area and obj.area >= 2:
            horizontal.append(obj)
        elif obj.width == 1 and obj.height == obj.area and obj.area >= 2:
            vertical.append(obj)
        else:
            raise Undefined("every object must be a straight segment")
    if not horizontal or not vertical:
        raise Undefined("both segment axes are required")
    height, width = _shape(grid)
    canvas = [list(row) for row in grid]
    # Horizontal strokes are rendered last.  This is an explicit, reusable
    # crossing convention and is checked against every demonstration.
    for obj in vertical:
        color = next(iter(obj.colors))
        for row in range(height):
            canvas[row][obj.left] = color
    for obj in horizontal:
        color = next(iter(obj.colors))
        for col in range(width):
            canvas[obj.top][col] = color
    return tuple(tuple(row) for row in canvas)


def _repeat_rows_right(grid: Grid, program: Mapping[str, Any]) -> Grid:
    """Infer one shared horizontal period from a populated left prefix."""

    background = _mode(grid)
    height, width = _shape(grid)
    prefixes: list[int] = []
    for row in grid:
        nonbackground = [col for col, color in enumerate(row) if color != background]
        prefixes.append(max(nonbackground) + 1 if nonbackground else 0)
    candidate_periods: list[int] = []
    for period in range(1, width):
        evidence = False
        valid = True
        for row, prefix in zip(grid, prefixes):
            if prefix == 0:
                continue
            if prefix > period:
                evidence = True
            if any(row[col] != row[col % period] for col in range(prefix)):
                valid = False
                break
        if valid and evidence:
            candidate_periods.append(period)
    if not candidate_periods:
        raise Undefined("no supported row period")
    period = min(candidate_periods)
    canvas = [list(row) for row in grid]
    changed = 0
    for row in range(height):
        if prefixes[row] == 0:
            continue
        for col in range(prefixes[row], width):
            canvas[row][col] = grid[row][col % period]
            changed += canvas[row][col] != grid[row][col]
    if not changed:
        raise Undefined("periodic extension is vacuous")
    return tuple(tuple(row) for row in canvas)


def _complete_missing_corner_triangle(grid: Grid, program: Mapping[str, Any]) -> Grid:
    """Complete the three sides of a corner triangle from four sparse marks."""

    marker, paint = int(program["marker"]), int(program["paint"])
    points = {(row, col) for row, values in enumerate(grid) for col, color in enumerate(values) if color == marker}
    if len(points) != 4:
        raise Undefined("four marker cells required")
    top, bottom = min(row for row, _ in points), max(row for row, _ in points)
    left, right = min(col for _, col in points), max(col for _, col in points)
    if bottom - top != right - left or bottom == top:
        raise Undefined("markers need a square envelope")
    corners = {(top, left), (top, right), (bottom, left), (bottom, right)}
    present_corners = points & corners
    if len(present_corners) != 3:
        raise Undefined("exactly one envelope corner must be missing")
    missing = next(iter(corners - present_corners))
    interior = next(iter(points - present_corners))
    # The fourth mark must lie strictly in the triangular sector of the
    # missing corner, excluding both diagonals.
    size = bottom - top
    rr, cc = interior[0] - top, interior[1] - left
    sectors = {
        (top, left): rr + cc < size,
        (top, right): rr < cc,
        (bottom, left): rr > cc,
        (bottom, right): rr + cc > size,
    }
    if not sectors[missing]:
        raise Undefined("interior mark contradicts missing corner")
    if missing == (top, left):
        boundary = (
            {(top, col) for col in range(left, right + 1)}
            | {(row, left) for row in range(top, bottom + 1)}
            | {(top + offset, right - offset) for offset in range(size + 1)}
        )
    elif missing == (top, right):
        boundary = (
            {(top, col) for col in range(left, right + 1)}
            | {(row, right) for row in range(top, bottom + 1)}
            | {(top + offset, left + offset) for offset in range(size + 1)}
        )
    elif missing == (bottom, left):
        boundary = (
            {(bottom, col) for col in range(left, right + 1)}
            | {(row, left) for row in range(top, bottom + 1)}
            | {(top + offset, left + offset) for offset in range(size + 1)}
        )
    else:
        boundary = (
            {(bottom, col) for col in range(left, right + 1)}
            | {(row, right) for row in range(top, bottom + 1)}
            | {(top + offset, right - offset) for offset in range(size + 1)}
        )
    canvas = [list(row) for row in grid]
    for row, col in boundary - points:
        canvas[row][col] = paint
    return tuple(tuple(row) for row in canvas)


def _frequency_sort_columns(grid: Grid, program: Mapping[str, Any]) -> Grid:
    """Group a dense palette by frequency along bottom-up columns."""

    height, width = _shape(grid)
    counts = Counter(cell for row in grid for cell in row)
    if len(counts) < 3 or any(count == 1 for count in counts.values()):
        raise Undefined("dense multi-color population required")
    ordered_colors = sorted(counts, key=lambda color: (-counts[color], color))
    sequence = [color for color in ordered_colors for _ in range(counts[color])]
    canvas = [[0 for _ in range(width)] for _ in range(height)]
    index = 0
    for col in range(width):
        for row in range(height - 1, -1, -1):
            canvas[row][col] = sequence[index]
            index += 1
    return tuple(tuple(row) for row in canvas)


def _rotate_region_palette(grid: Grid, program: Mapping[str, Any]) -> Grid:
    """Rotate labels of peripheral regions while preserving a scaffold."""

    scaffold = {int(color) for color in program["scaffold"]}
    shift = int(program["shift"])
    payload = sorted({cell for row in grid for cell in row} - scaffold)
    if len(payload) < 2:
        raise Undefined("at least two peripheral colors required")
    height, width = _shape(grid)
    center_row, center_col = (height - 1) / 2, (width - 1) / 2
    angular: list[tuple[float, int]] = []
    for color in payload:
        cells = [(row, col) for row in range(height) for col in range(width) if grid[row][col] == color]
        mean_row = sum(row for row, _ in cells) / len(cells)
        mean_col = sum(col for _, col in cells) / len(cells)
        angular.append((math.atan2(mean_row - center_row, mean_col - center_col), color))
    angular.sort()
    order = [color for _, color in angular]
    mapping = {color: order[(index + shift) % len(order)] for index, color in enumerate(order)}
    return tuple(tuple(mapping.get(color, color) for color in row) for row in grid)


def _levitate_by_area(grid: Grid, program: Mapping[str, Any]) -> Grid:
    """Translate objects away from a full boundary rail by their cell count."""

    background = _mode(grid)
    height, width = _shape(grid)
    mono = _components(grid, background, mono=True)
    rails: list[tuple[str, Obj]] = []
    for obj in mono:
        if obj.height == 1 and obj.width == width and obj.area == width and obj.top in {0, height - 1}:
            rails.append(("row", obj))
        if obj.width == 1 and obj.height == height and obj.area == height and obj.left in {0, width - 1}:
            rails.append(("col", obj))
    orientation, rail = _unique(rails, "boundary rail")
    moving = [obj for obj in mono if obj is not rail]
    if not moving:
        raise Undefined("no objects to translate")
    canvas = [list(row) for row in grid]
    for obj in moving:
        for row, col, _ in obj.cells:
            canvas[row][col] = background
    occupied: set[Cell] = set()
    for obj in moving:
        if orientation == "row":
            delta_row = obj.area if rail.top == 0 else -obj.area
            delta_col = 0
        else:
            delta_row = 0
            delta_col = obj.area if rail.left == 0 else -obj.area
        for row, col, color in obj.cells:
            target = row + delta_row, col + delta_col
            if not (0 <= target[0] < height and 0 <= target[1] < width):
                raise Undefined("area translation leaves canvas")
            if target in occupied or canvas[target[0]][target[1]] != background:
                raise Undefined("area translation collides")
            occupied.add(target)
            canvas[target[0]][target[1]] = color
    return tuple(tuple(row) for row in canvas)


def _color_rail_gravity(grid: Grid, program: Mapping[str, Any]) -> Grid:
    """Slide rigid same-colored pieces toward their full-height edge rail."""

    background = _mode(grid)
    height, width = _shape(grid)
    mono = _components(grid, background, mono=True)
    rail_specs: list[tuple[int, int, Obj]] = []
    for obj in mono:
        color = next(iter(obj.colors))
        positions = {(row, col) for row, col, _ in obj.cells}
        if all((row, 0) in positions for row in range(height)):
            rail_specs.append((color, -1, obj))
        if all((row, width - 1) in positions for row in range(height)):
            rail_specs.append((color, 1, obj))
    if len(rail_specs) != 2 or {direction for _, direction, _ in rail_specs} != {-1, 1}:
        raise Undefined("opposed color rails required")
    moving: list[tuple[int, int, Obj]] = []
    rail_objects = {id(obj) for _, _, obj in rail_specs}
    by_color = {color: direction for color, direction, _ in rail_specs}
    for obj in mono:
        color = next(iter(obj.colors))
        if id(obj) not in rail_objects:
            if color not in by_color:
                raise Undefined("every piece color needs a rail")
            moving.append((color, by_color[color], obj))
    if not moving:
        raise Undefined("no movable rail pieces")
    canvas = [list(row) for row in grid]
    for _, _, obj in moving:
        for row, col, _ in obj.cells:
            canvas[row][col] = background
    # Nearest pieces settle first, exactly as one-axis rigid gravity.
    moving.sort(key=lambda item: (
        item[2].left if item[1] == -1 else width - 1 - item[2].right,
        item[2].top, item[2].left, item[0],
    ))
    settled_by_color: dict[int, set[Cell]] = {
        color: {(row, col) for row, col, _ in rail.cells}
        for color, _, rail in rail_specs
    }
    for color, direction, obj in moving:
        positions = {(row, col) for row, col, _ in obj.cells}
        contact = str(program.get("left_contact" if direction == -1 else "right_contact", "overlap"))
        if contact not in {"overlap", "chebyshev_singleton"}:
            raise Undefined("unknown rail contact policy")
        while True:
            settled = settled_by_color[color]
            if contact == "chebyshev_singleton" and obj.area == 1 and any(
                max(abs(row - other_row), abs(col - other_col)) <= 1
                for row, col in positions
                for other_row, other_col in settled
            ):
                break
            shifted = {(row, col + direction) for row, col in positions}
            if any(col < 0 or col >= width or canvas[row][col] != background for row, col in shifted):
                break
            positions = shifted
        for row, col in positions:
            canvas[row][col] = color
        settled_by_color[color].update(positions)
    return tuple(tuple(row) for row in canvas)


EXECUTORS: dict[str, Callable[[Grid, Mapping[str, Any]], Grid]] = {
    "recolor_lower_bbox_half": _recolor_lower_bbox_half,
    "recolor_lower_vertical_runs": _recolor_lower_vertical_runs,
    "ranked_rectangle_interiors": _ranked_rectangle_interiors,
    "row_label_transfer": _row_label_transfer,
    "template_placeholders": _template_placeholders,
    "marker_center_copy": _marker_center_copy,
    "gapped_frame_fill_ray": _gapped_frame_fill_ray,
    "dock_to_line": _dock_to_line,
    "bar_wedges": _bar_wedges,
    "paired_inward_extrude": _paired_inward_extrude,
    "shift_periodic_border": _shift_periodic_border,
    "extend_lines_to_canvas": _extend_lines_to_canvas,
    "repeat_rows_right": _repeat_rows_right,
    "complete_missing_corner_triangle": _complete_missing_corner_triangle,
    "frequency_sort_columns": _frequency_sort_columns,
    "rotate_region_palette": _rotate_region_palette,
    "levitate_by_area": _levitate_by_area,
    "color_rail_gravity": _color_rail_gravity,
}


def execute_program(program: Mapping[str, Any], value: Any) -> list[list[int]]:
    if not isinstance(program, Mapping) or program.get("schema") != SCHEMA:
        raise ValueError("invalid targeted-same-shape-2 program")
    op = str(program.get("op"))
    if op not in EXECUTORS:
        raise ValueError("unknown targeted-same-shape-2 operation")
    return _plain(EXECUTORS[op](_grid(value), program))


def _record(op: str, **parameters: Any) -> dict[str, Any]:
    return {"schema": SCHEMA, "op": op, **parameters}


def _programs(train: Sequence[tuple[Grid, Grid]]) -> list[tuple[int, str, dict[str, Any]]]:
    pairs = _changed_pairs(train)
    colors = _palette(train)
    before_colors = tuple(sorted({before for before, _ in pairs}))
    after_colors = tuple(sorted({after for _, after in pairs}))
    training_backgrounds = tuple(sorted({_mode(source) for source, _ in train}))
    result: list[tuple[int, str, dict[str, Any]]] = [
        (5, "same_shape.paired_inward_extrude", _record("paired_inward_extrude")),
        (5, "same_shape.shift_periodic_border", _record("shift_periodic_border")),
        (4, "same_shape.extend_lines_to_canvas", _record("extend_lines_to_canvas")),
        (4, "same_shape.repeat_rows_right", _record("repeat_rows_right")),
        (4, "same_shape.frequency_sort_columns", _record("frequency_sort_columns")),
        (5, "same_shape.levitate_by_area", _record("levitate_by_area")),
    ]
    for left_contact in ("overlap", "chebyshev_singleton"):
        for right_contact in ("overlap", "chebyshev_singleton"):
            result.append((
                6 + (left_contact != "overlap") + (right_contact != "overlap"),
                "same_shape.color_rail_gravity",
                _record(
                    "color_rail_gravity",
                    left_contact=left_contact,
                    right_contact=right_contact,
                ),
            ))
    for source, paint in pairs:
        result.extend([
            (4, "same_shape.lower_bbox_half", _record("recolor_lower_bbox_half", source=source, paint=paint)),
            (5, "same_shape.lower_vertical_runs", _record("recolor_lower_vertical_runs", source=source, paint=paint)),
        ])
        result.append((6, "same_shape.missing_corner_triangle", _record(
            "complete_missing_corner_triangle", marker=source, paint=paint,
        )))
    # The marker itself is often unchanged; enumerate sparse input colors as
    # triangle markers and only demonstrated destination colors as paint.
    for marker in colors:
        for paint in after_colors:
            result.append((6, "same_shape.missing_corner_triangle", _record(
                "complete_missing_corner_triangle", marker=marker, paint=paint,
            )))
    for first_index, first in enumerate(colors):
        for second in colors[first_index + 1:]:
            for shift in (-1, 1):
                result.append((6, "same_shape.rotate_region_palette", _record(
                    "rotate_region_palette", scaffold=[first, second], shift=shift,
                )))
    for frame in colors:
        for paint in after_colors:
            result.append((6, "same_shape.gapped_frame", _record(
                "gapped_frame_fill_ray", frame=frame, paint=paint,
            )))
    for source in before_colors:
        result.append((5, "same_shape.row_label_transfer", _record("row_label_transfer", mask=source)))
        result.append((6, "same_shape.template_placeholders", _record(
            "template_placeholders", placeholder=source, erase_template=False,
        )))
        result.append((7, "same_shape.template_placeholders", _record(
            "template_placeholders", placeholder=source, erase_template=True,
        )))
        result.append((6, "same_shape.marker_center_copy", _record("marker_center_copy", marker=source)))
    for separator in after_colors:
        result.append((6, "same_shape.dock_to_line", _record("dock_to_line", separator=separator)))
    for frame in colors:
        for background in training_backgrounds:
            for large_paint in after_colors:
                for small_paint in after_colors:
                    if large_paint != small_paint:
                        result.append((7, "same_shape.ranked_rectangle_interiors", _record(
                            "ranked_rectangle_interiors", frame=frame, background=background,
                            large_paint=large_paint, small_paint=small_paint,
                        )))
    for bar in colors:
        for above in after_colors:
            for below in after_colors:
                if above != below:
                    result.append((7, "same_shape.bar_wedges", _record(
                        "bar_wedges", bar=bar, above=above, below=below,
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
            candidate_cap = limits.get("max_candidates", limits.get("candidate_cap", 64))
            if isinstance(candidate_cap, bool) or not isinstance(candidate_cap, int) or candidate_cap < 1:
                raise Undefined("invalid candidate cap")
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
    output = []
    for behavior, candidate in candidates.items():
        candidate["evidence"]["behavior_hash"] = behavior
        candidate["evidence"]["mechanism_support"] = len(mechanisms[behavior])
        candidate["evidence"]["equivalent_families"] = sorted(mechanisms[behavior])
        output.append(candidate)
    output.sort(key=lambda candidate: (
        candidate["complexity"], -candidate["evidence"]["mechanism_support"],
        candidate["family"], _canonical(candidate["program"]),
    ))
    return output[:candidate_cap]


__all__ = ["SCHEMA", "compile_task", "execute_program"]
