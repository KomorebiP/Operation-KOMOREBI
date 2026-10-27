"""Proof-carrying panel and layout programs for PR-LASM Block 15.

The compiler is deliberately task-identity-free.  It recognizes a small set
of relational layouts (panel lattices, template keys, occluded line stacks,
and rectangle atlases), replays every demonstration, and predicts held-out
inputs only when all surviving programs agree on the complete behavior.

Every accepted behavior also survives leave-one-demonstration-out
re-induction and a non-trivial palette-swap counterfactual.  Test labels,
solution stores, task identifiers, corpus fingerprints, and resolved test
coordinates are not accepted by this module.

Author: Komorebi P.
"""

from __future__ import annotations

from collections import Counter, defaultdict, deque
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
import hashlib
import json
from typing import Any, Callable


Grid = tuple[tuple[int, ...], ...]
Cell = tuple[int, int]
Pair = tuple[Grid, Grid]
SCHEMA = "komorebi.pr_lasm.block15.panel_layout_compiler.program.v1"
AUTHOR = "Komorebi P."


class Undefined(ValueError):
    """A requested relational role is absent or ambiguous."""


@dataclass(frozen=True, slots=True)
class Limits:
    max_grid_cells: int = 900
    max_examples: int = 16
    max_programs: int = 16
    max_executor_calls: int = 20_000
    max_counterfactual_calls: int = 2_048
    max_candidates: int = 1

    @classmethod
    def from_value(cls, value: Mapping[str, Any] | None) -> "Limits":
        if value is None:
            return cls()
        if not isinstance(value, Mapping):
            raise Undefined("limits must be a mapping")
        default = cls()
        ceilings = {
            "max_grid_cells": 3_600,
            "max_examples": 24,
            "max_programs": 64,
            "max_executor_calls": 200_000,
            "max_counterfactual_calls": 16_384,
            "max_candidates": 1,
        }
        parsed: dict[str, int] = {}
        for name in cls.__dataclass_fields__:
            source = "candidate_cap" if name == "max_candidates" and "candidate_cap" in value else name
            raw = value.get(source, getattr(default, name))
            if isinstance(raw, bool) or not isinstance(raw, int) or raw < 0:
                raise Undefined(f"limits.{name} must be a nonnegative integer")
            parsed[name] = min(raw, ceilings[name])
        return cls(**parsed)


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _grid(value: Any, limits: Limits | None = None) -> Grid:
    bounds = limits or Limits()
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or not value:
        raise Undefined("grid must be a nonempty sequence")
    rows: list[tuple[int, ...]] = []
    width: int | None = None
    for raw_row in value:
        if not isinstance(raw_row, Sequence) or isinstance(raw_row, (str, bytes)) or not raw_row:
            raise Undefined("grid row must be nonempty")
        row: list[int] = []
        for raw_cell in raw_row:
            if isinstance(raw_cell, bool) or not isinstance(raw_cell, int) or not 0 <= raw_cell <= 9:
                raise Undefined("invalid ARC color")
            row.append(int(raw_cell))
        if width is None:
            width = len(row)
        elif width != len(row):
            raise Undefined("ragged grid")
        rows.append(tuple(row))
    if len(rows) * int(width or 0) > bounds.max_grid_cells:
        raise Undefined("grid exceeds cell cap")
    return tuple(rows)


def _plain(grid: Grid) -> list[list[int]]:
    return [list(row) for row in grid]


def _freeze(rows: Sequence[Sequence[int]]) -> Grid:
    return tuple(tuple(int(cell) for cell in row) for row in rows)


def _shape(grid: Grid) -> tuple[int, int]:
    return len(grid), len(grid[0])


def _palette(grid: Grid) -> tuple[int, ...]:
    return tuple(sorted({cell for row in grid for cell in row}))


def _unique_mode(values: Iterable[int]) -> int:
    counts = Counter(values)
    if not counts:
        raise Undefined("empty color role")
    maximum = max(counts.values())
    winners = sorted(color for color, count in counts.items() if count == maximum)
    if len(winners) != 1:
        raise Undefined("color role is tied")
    return winners[0]


def _border_mode(grid: Grid) -> int:
    height, width = _shape(grid)
    values = list(grid[0]) + list(grid[-1])
    values += [grid[row][0] for row in range(1, height - 1)]
    if width > 1:
        values += [grid[row][-1] for row in range(1, height - 1)]
    return _unique_mode(values)


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


def _crop(grid: Grid, box: tuple[int, int, int, int]) -> Grid:
    r0, r1, c0, c1 = box
    if not (0 <= r0 <= r1 < len(grid) and 0 <= c0 <= c1 < len(grid[0])):
        raise Undefined("invalid crop")
    return tuple(tuple(grid[row][c0 : c1 + 1]) for row in range(r0, r1 + 1))


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
        raise Undefined("invalid example collection")
    train: list[Pair] = []
    for example in raw_train:
        if not isinstance(example, Mapping):
            raise Undefined("invalid demonstration")
        train.append((_grid(example.get("input"), limits), _grid(example.get("output"), limits)))
    tests: list[Grid] = []
    for example in raw_test:
        if not isinstance(example, Mapping):
            raise Undefined("invalid test")
        # Intentionally ignore an injected held-out ``output`` member.
        tests.append(_grid(example.get("input"), limits))
    return tuple(train), tuple(tests)


def _bands(length: int, separators: Sequence[int]) -> tuple[tuple[int, int], ...]:
    result: list[tuple[int, int]] = []
    start = 0
    for index in separators:
        if start < index:
            result.append((start, index))
        start = index + 1
    if start < length:
        result.append((start, length))
    return tuple(result)


def _components(grid: Grid, background: int, connectivity: int = 4) -> tuple[frozenset[Cell], ...]:
    height, width = _shape(grid)
    directions = ((1, 0), (-1, 0), (0, 1), (0, -1))
    if connectivity == 8:
        directions += ((1, 1), (1, -1), (-1, 1), (-1, -1))
    seen: set[Cell] = set()
    result: list[frozenset[Cell]] = []
    for row in range(height):
        for column in range(width):
            if grid[row][column] == background or (row, column) in seen:
                continue
            queue = deque([(row, column)])
            seen.add((row, column))
            cells: set[Cell] = set()
            while queue:
                current = queue.popleft()
                cells.add(current)
                for dr, dc in directions:
                    neighbor = current[0] + dr, current[1] + dc
                    if (
                        0 <= neighbor[0] < height
                        and 0 <= neighbor[1] < width
                        and neighbor not in seen
                        and grid[neighbor[0]][neighbor[1]] != background
                    ):
                        seen.add(neighbor)
                        queue.append(neighbor)
            result.append(frozenset(cells))
    return tuple(sorted(result, key=lambda cells: (_bbox(cells), len(cells))))


# ---------------------------------------------------------------------------
# Executable operators


def _nest_rectangles(grid: Grid) -> tuple[Grid, dict[str, Any]]:
    background = _border_mode(grid)
    records: list[tuple[int, int, int, tuple[int, int, int, int]]] = []
    for color in _palette(grid):
        if color == background:
            continue
        cells = {(row, column) for row, line in enumerate(grid) for column, value in enumerate(line) if value == color}
        box = _bbox(cells)
        r0, r1, c0, c1 = box
        height, width = r1 - r0 + 1, c1 - c0 + 1
        if any(grid[row][column] == background for row in range(r0, r1 + 1) for column in range(c0, c1 + 1)):
            raise Undefined("a rectangle contains a background hole")
        records.append((height * width, height, width, box))
    if len(records) < 3 or len({area for area, *_ in records}) != len(records):
        raise Undefined("rectangle nesting needs three distinct areas")
    # Recover each rectangle's semantic color from a point in its own support.
    colored: list[tuple[int, int, int, int]] = []
    for area, height, width, box in records:
        r0, r1, c0, c1 = box
        counts = Counter(
            grid[row][column]
            for row in range(r0, r1 + 1)
            for column in range(c0, c1 + 1)
        )
        candidates = [color for color in counts if color != background and sum(value == color for line in grid for value in line) > 0]
        own = [color for color in candidates if _bbox((
            (row, column)
            for row, line in enumerate(grid)
            for column, value in enumerate(line)
            if value == color
        )) == box]
        if len(own) != 1:
            raise Undefined("rectangle color is ambiguous")
        colored.append((area, height, width, own[0]))
    colored.sort(reverse=True)
    max_area, out_h, out_w, _ = colored[0]
    if max_area != out_h * out_w or any(height > out_h or width > out_w for _, height, width, _ in colored):
        raise Undefined("rectangles do not nest in one canvas")
    canvas = [[background for _ in range(out_w)] for _ in range(out_h)]
    for _area, height, width, color in colored:
        for row in range(height):
            for column in range(width):
                canvas[row][column] = color
    return _freeze(canvas), {"rectangles": len(colored), "order": "descending-area", "anchor": "top-left"}


def _line_geometry(cells: set[Cell], height: int, width: int) -> tuple[str, tuple[Cell, ...]]:
    if len(cells) < 2:
        raise Undefined("line has fewer than two visible cells")
    rows = {row for row, _ in cells}
    columns = {column for _, column in cells}
    differences = {row - column for row, column in cells}
    sums = {row + column for row, column in cells}
    options: list[tuple[str, tuple[Cell, ...]]] = []
    if len(rows) == 1:
        row = next(iter(rows))
        options.append(("horizontal", tuple((row, column) for column in range(width))))
    if len(columns) == 1:
        column = next(iter(columns))
        options.append(("vertical", tuple((row, column) for row in range(height))))
    if len(differences) == 1:
        offset = next(iter(differences))
        options.append(("diagonal_down", tuple((row, row - offset) for row in range(height) if 0 <= row - offset < width)))
    if len(sums) == 1:
        total = next(iter(sums))
        options.append(("diagonal_up", tuple((row, total - row) for row in range(height) if 0 <= total - row < width)))
    options = [(name, support) for name, support in options if cells <= set(support)]
    if len(options) != 1:
        raise Undefined("line geometry is absent or ambiguous")
    return options[0]


def _occlusion_line_order(grid: Grid) -> tuple[Grid, dict[str, Any]]:
    height, width = _shape(grid)
    background = _unique_mode(cell for row in grid for cell in row)
    colors = [color for color in _palette(grid) if color != background]
    if not 2 <= len(colors) <= 8:
        raise Undefined("line layer count is outside the bound")
    geometry: dict[int, tuple[str, tuple[Cell, ...]]] = {}
    for color in colors:
        cells = {(row, column) for row in range(height) for column in range(width) if grid[row][column] == color}
        name, support = _line_geometry(cells, height, width)
        if len(support) < 3:
            raise Undefined("geometric line is too short")
        geometry[color] = name, support
    supports = {color: set(record[1]) for color, record in geometry.items()}
    for color, support in supports.items():
        for point in support:
            visible = grid[point[0]][point[1]]
            if visible == background or (visible != color and point not in supports.get(visible, set())):
                raise Undefined("a line interruption lacks an occluding line")
    edges: dict[int, set[int]] = {color: set() for color in colors}
    intersections = 0
    for index, left in enumerate(colors):
        for right in colors[index + 1 :]:
            overlap = supports[left] & supports[right]
            if not overlap:
                # Parallel lines acquire their relative depth through shared
                # transversals; they need not intersect each other.
                continue
            if len(overlap) != 1:
                raise Undefined("line pair has a coincident support")
            intersections += 1
            row, column = next(iter(overlap))
            visible = grid[row][column]
            if visible == left:
                edges[right].add(left)
            elif visible == right:
                edges[left].add(right)
            else:
                # A third line can cover a coincident crossing, but then this
                # pair contributes no comparison and uniqueness must come from
                # its other crossings.
                if visible not in colors:
                    raise Undefined("crossing has no visible line")
    orders: list[tuple[int, ...]] = []

    def visit(prefix: tuple[int, ...], remaining: frozenset[int]) -> None:
        if len(orders) > 1:
            return
        if not remaining:
            orders.append(prefix)
            return
        available = sorted(color for color in remaining if not (edges[color] & remaining))
        for color in available:
            visit(prefix + (color,), remaining - {color})

    visit((), frozenset(colors))
    if len(orders) != 1 or intersections < len(colors) - 1:
        raise Undefined("line occlusion order is not total")
    # ``visit`` removes sinks first (visible/top layers).  The requested
    # serialized stack is bottom-to-top.
    return (tuple(reversed(orders[0])),), {"lines": len(colors), "pairwise_crossings": intersections, "order": "bottom-to-top"}


def _vertical_three_panels(grid: Grid) -> tuple[int, tuple[Grid, Grid, Grid]]:
    height, width = _shape(grid)
    proposals: list[tuple[int, tuple[Grid, Grid, Grid]]] = []
    for separator in _palette(grid):
        columns = [column for column in range(width) if all(grid[row][column] == separator for row in range(height))]
        if len(columns) != 2 or columns[1] != columns[0] * 2 + 1:
            continue
        bands = _bands(width, columns)
        if len(bands) != 3 or len({end - start for start, end in bands}) != 1:
            continue
        panels = tuple(tuple(tuple(row[start:end]) for row in grid) for start, end in bands)
        proposals.append((separator, panels))
    unique = {_canonical([separator, [[_plain(panel) for panel in panels]]]): (separator, panels) for separator, panels in proposals}
    if len(unique) != 1:
        raise Undefined("three-panel strip is absent or ambiguous")
    return next(iter(unique.values()))


def _ranked_panel_layers(grid: Grid) -> tuple[Grid, dict[str, Any]]:
    separator, panels = _vertical_three_panels(grid)
    background = _unique_mode(cell for panel in panels for row in panel for cell in row if cell != separator)
    height, width = _shape(panels[0])
    canvas = [[background for _ in range(width)] for _ in range(height)]
    selected: list[int] = []
    for rank, panel in enumerate(panels):
        records: list[tuple[float, float, int, frozenset[Cell]]] = []
        for color in _palette(panel):
            if color == background:
                continue
            remaining = {(row, column) for row in range(height) for column in range(width) if panel[row][column] == color}
            while remaining:
                seed = min(remaining)
                remaining.remove(seed)
                queue = [seed]
                cells: set[Cell] = set()
                while queue:
                    current = queue.pop()
                    cells.add(current)
                    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        neighbor = current[0] + dr, current[1] + dc
                        if neighbor in remaining:
                            remaining.remove(neighbor)
                            queue.append(neighbor)
                records.append(
                    (
                        sum(column for _, column in cells) / len(cells),
                        sum(row for row, _ in cells) / len(cells),
                        color,
                        frozenset(cells),
                    )
                )
        records.sort()
        if rank >= len(records) or (rank and records[rank - 1][:2] == records[rank][:2]):
            raise Undefined("spatial color rank is absent")
        color, cells = records[rank][2], records[rank][3]
        selected.append(color)
        for row, column in cells:
            if canvas[row][column] not in {background, color}:
                raise Undefined("ranked panel layers collide")
            canvas[row][column] = color
    return _freeze(canvas), {"panels": 3, "selection": "left-center-right color centroid", "separator": separator}


def _lattice_pattern_substitution(grid: Grid) -> tuple[Grid, dict[str, Any]]:
    height, width = _shape(grid)
    proposals: list[tuple[int, tuple[int, ...], tuple[int, ...]]] = []
    for separator in _palette(grid):
        rows = tuple(row for row in range(height) if all(value == separator for value in grid[row]))
        columns = tuple(column for column in range(width) if all(grid[row][column] == separator for row in range(height)))
        if len(rows) < 3 or len(columns) < 2 or rows[0] != 0 or rows[-1] != height - 1 or columns[-1] != width - 1:
            continue
        if any(right == left + 1 for left, right in zip(rows, rows[1:])) or any(right == left + 1 for left, right in zip(columns, columns[1:])):
            continue
        proposals.append((separator, rows, columns))
    if len(proposals) != 1:
        raise Undefined("keyed lattice is absent or ambiguous")
    separator, row_lines, column_lines = proposals[0]
    row_bands = tuple((row_lines[index] + 1, row_lines[index + 1]) for index in range(len(row_lines) - 1))
    column_bands = [(1, column_lines[0])]
    column_bands += [(column_lines[index] + 1, column_lines[index + 1]) for index in range(len(column_lines) - 1)]
    if len({end - start for start, end in row_bands}) != 1 or len({end - start for start, end in column_bands}) != 1:
        raise Undefined("lattice panels are not congruent")
    panels: list[list[Grid]] = []
    keys: list[int] = []
    for r0, r1 in row_bands:
        key_values = {grid[row][0] for row in range(r0, r1)}
        if len(key_values) != 1:
            raise Undefined("row key is not constant")
        keys.append(next(iter(key_values)))
        panels.append([tuple(tuple(grid[row][c0:c1]) for row in range(r0, r1)) for c0, c1 in column_bands])
    base = _unique_mode(cell for row in panels for panel in row for line in panel for cell in line)
    panel_h, panel_w = _shape(panels[0][0])
    rendered: list[Grid] = []
    for column in range(len(column_bands)):
        column_panels = [panels[row][column] for row in range(len(row_bands))]
        classes = Counter(_canonical(_plain(panel)) for panel in column_panels)
        repeated_keys = [key for key, count in classes.items() if count == len(column_panels) - 1]
        if len(repeated_keys) != 1:
            raise Undefined("one pattern is not repeated outside one key row")
        pattern_key = repeated_keys[0]
        pattern = next(panel for panel in column_panels if _canonical(_plain(panel)) == pattern_key)
        exceptional = [index for index, panel in enumerate(column_panels) if _canonical(_plain(panel)) != pattern_key]
        if len(exceptional) != 1:
            raise Undefined("solid exemplar row is ambiguous")
        source_index = exceptional[0]
        solid = column_panels[source_index]
        interior = [solid[row][column_] for row in range(1, panel_h - 1) for column_ in range(1, panel_w - 1)]
        if not interior or len(set(interior)) != 1 or any(solid[row][column_] != base for row in range(panel_h) for column_ in range(panel_w) if row in {0, panel_h - 1} or column_ in {0, panel_w - 1}):
            raise Undefined("exceptional panel is not a solid framed exemplar")
        solid_color = interior[0]
        motif_colors = {cell for line in pattern for cell in line} - {base, separator}
        if len(motif_colors) != 1:
            raise Undefined("pattern has no unique replaceable motif role")
        motif_color = next(iter(motif_colors))
        output = tuple(
            tuple(
                keys[source_index] if value == base else solid_color if value == motif_color else value
                for value in line
            )
            for line in pattern
        )
        rendered.append(output)
    result = [[separator for _ in range(len(rendered) * panel_w + len(rendered) - 1)] for _ in range(panel_h)]
    for index, panel in enumerate(rendered):
        offset = index * (panel_w + 1)
        for row in range(panel_h):
            result[row][offset : offset + panel_w] = list(panel[row])
    return _freeze(result), {"rows": len(row_bands), "columns": len(column_bands), "schema_role": "solid-key substitutes repeated motif"}


def _template_hole_decode(grid: Grid) -> tuple[Grid, dict[str, Any]]:
    background = _border_mode(grid)
    nonbackground = {(row, column) for row, line in enumerate(grid) for column, value in enumerate(line) if value != background}
    crop = _crop(grid, _bbox(nonbackground))
    height, width = _shape(crop)
    row_lines = tuple(row for row in range(height) if all(value == background for value in crop[row]))
    column_lines = tuple(column for column in range(width) if all(crop[row][column] == background for row in range(height)))
    row_bands, column_bands = _bands(height, row_lines), _bands(width, column_lines)
    if len(row_bands) < 2 or len(column_bands) < 2 or len({end - start for start, end in row_bands}) != 1 or len({end - start for start, end in column_bands}) != 1:
        raise Undefined("template lattice is absent")
    panels = [tuple(tuple(crop[row][c0:c1]) for row in range(r0, r1)) for r0, r1 in row_bands for c0, c1 in column_bands]
    classes = Counter(_canonical(_plain(panel)) for panel in panels)
    modal_key, count = classes.most_common(1)[0]
    if count != len(panels) - 1 or len(classes) != 2:
        raise Undefined("lattice lacks one exceptional template")
    template = next(panel for panel in panels if _canonical(_plain(panel)) == modal_key)
    exceptional = next(panel for panel in panels if _canonical(_plain(panel)) != modal_key)
    base = _unique_mode(cell for row in template for cell in row)
    if set(_palette(template)) != {background, base}:
        raise Undefined("template is not binary")
    hole_rows = sorted({row for row, line in enumerate(template) for value in line if value == background})
    hole_columns = sorted({column for line in template for column, value in enumerate(line) if value == background})
    if len(hole_rows) != len(row_bands) or len(hole_columns) != len(column_bands):
        raise Undefined("template holes do not encode the lattice shape")
    if any(exceptional[row][column] != template[row][column] for row in range(len(template)) for column in range(len(template[0])) if template[row][column] == base):
        raise Undefined("exceptional template changes its scaffold")
    values = [[exceptional[row][column] for column in hole_columns] for row in hole_rows]
    if all(value in {background, base} for row in values for value in row):
        raise Undefined("exceptional template contains no key colors")
    tile_h, tile_w = _shape(template)
    out_h = len(values) * tile_h + len(values) - 1
    out_w = len(values[0]) * tile_w + len(values[0]) - 1
    canvas = [[base for _ in range(out_w)] for _ in range(out_h)]
    for tile_row, value_row in enumerate(values):
        for tile_column, value in enumerate(value_row):
            tile = tuple(tuple(value if cell == base else base for cell in line) for line in template)
            r0, c0 = tile_row * (tile_h + 1), tile_column * (tile_w + 1)
            for row in range(tile_h):
                canvas[r0 + row][c0 : c0 + tile_w] = list(tile[row])
    return _freeze(canvas), {"encoded_rows": len(values), "encoded_columns": len(values[0]), "exceptional_panels": 1}


def _interval_support(cells: set[Cell], axis: str) -> dict[int, tuple[int, int]]:
    grouped: dict[int, list[int]] = defaultdict(list)
    for row, column in cells:
        grouped[row if axis == "rows" else column].append(column if axis == "rows" else row)
    result: dict[int, tuple[int, int]] = {}
    for key, values in grouped.items():
        low, high = min(values), max(values)
        if set(values) != set(range(low, high + 1)):
            raise Undefined("dynamic slice is not an interval")
        result[key] = low, high
    return result


def _growth_step_axis(first: Grid, second: Grid, scaffold: Grid, axis: str) -> Grid:
    if not (_shape(first) == _shape(second) == _shape(scaffold)):
        raise Undefined("growth panels are not aligned")
    height, width = _shape(first)
    colors = sorted({second[row][column] for row in range(height) for column in range(width) if second[row][column] != scaffold[row][column]})
    if not colors:
        raise Undefined("growth sequence has no dynamic colors")
    result = [list(row) for row in scaffold]
    occupied: dict[Cell, int] = {}
    for color in colors:
        left = {(row, column) for row in range(height) for column in range(width) if first[row][column] == color and first[row][column] != scaffold[row][column]}
        right = {(row, column) for row in range(height) for column in range(width) if second[row][column] == color and second[row][column] != scaffold[row][column]}
        if not left or left == right:
            raise Undefined("dynamic support does not change")
        left_intervals = _interval_support(left, axis)
        right_intervals = _interval_support(right, axis)
        if set(left_intervals) != set(right_intervals):
            raise Undefined("dynamic slices do not persist")
        support: set[Cell] = set()
        changed = False
        for key in sorted(left_intervals):
            left_low, left_high = left_intervals[key]
            right_low, right_high = right_intervals[key]
            next_low = 2 * right_low - left_low
            next_high = 2 * right_high - left_high
            if not (0 <= next_low <= next_high < (width if axis == "rows" else height)):
                raise Undefined("extrapolated interval leaves the canvas")
            changed |= (next_low, next_high) != (right_low, right_high)
            for value in range(next_low, next_high + 1):
                support.add((key, value) if axis == "rows" else (value, key))
        if not changed:
            raise Undefined("interval endpoints do not extrapolate")
        for point in support:
            if point in occupied and occupied[point] != color:
                raise Undefined("growth colors collide")
            occupied[point] = color
    for (row, column), color in occupied.items():
        result[row][column] = color
    return _freeze(result)


def _growth_step(first: Grid, second: Grid, scaffold: Grid) -> Grid:
    proposals: dict[str, Grid] = {}
    for axis in ("rows", "columns"):
        try:
            output = _growth_step_axis(first, second, scaffold, axis)
        except Undefined:
            continue
        proposals[_canonical(_plain(output))] = output
    if len(proposals) != 1:
        raise Undefined("growth axis is absent or behaviorally ambiguous")
    return next(iter(proposals.values()))


def _panel_growth_extrapolate(grid: Grid) -> tuple[Grid, dict[str, Any]]:
    height, width = _shape(grid)
    proposals: list[tuple[str, Grid]] = []
    if height % 3 == 0:
        step = height // 3
        panels = tuple(tuple(grid[index * step + row] for row in range(step)) for index in range(3))
        proposals.append(("vertical", _growth_step(panels[0], panels[1], panels[2])))
    if width % 3 == 0:
        step = width // 3
        panels = tuple(tuple(tuple(row[index * step : (index + 1) * step]) for row in grid) for index in range(3))
        try:
            proposals.append(("horizontal", _growth_step(panels[0], panels[1], panels[2])))
        except Undefined:
            pass
    unique = {_canonical(_plain(output)): (axis, output) for axis, output in proposals}
    if len(unique) != 1:
        raise Undefined("growth panelization is absent or ambiguous")
    axis, output = next(iter(unique.values()))
    return output, {"panels": 3, "axis": axis, "continuation": "translate newly added frontier"}


def _keyed_quadrant_assembly(grid: Grid) -> tuple[Grid, dict[str, Any]]:
    background = _border_mode(grid)
    height, width = _shape(grid)
    proposals: list[tuple[tuple[int, int, int, int], int, dict[int, Cell]]] = []
    for base in _palette(grid):
        if base == background:
            continue
        base_cells = {(row, column) for row in range(height) for column in range(width) if grid[row][column] == base}
        box = _bbox(base_cells)
        r0, r1, c0, c1 = box
        if (r1 - r0 + 1) * (c1 - c0 + 1) < 25:
            continue
        values = [grid[row][column] for row in range(r0, r1 + 1) for column in range(c0, c1 + 1)]
        if background in values:
            continue
        markers: dict[int, list[Cell]] = defaultdict(list)
        for row in range(r0, r1 + 1):
            for column in range(c0, c1 + 1):
                if grid[row][column] != base:
                    markers[grid[row][column]].append((row, column))
        if len(markers) != 4 or any(len(cells) != 1 for cells in markers.values()):
            continue
        positions = {color: cells[0] for color, cells in markers.items()}
        if len({row for row, _ in positions.values()}) != 2 or len({column for _, column in positions.values()}) != 2:
            continue
        proposals.append((box, base, positions))
    if len(proposals) != 1:
        raise Undefined("quadrant key is absent or ambiguous")
    box, base, positions = proposals[0]
    r0, r1, c0, c1 = box
    marker_rows = {row: index for index, row in enumerate(sorted({row for row, _ in positions.values()}))}
    marker_columns = {column: index for index, column in enumerate(sorted({column for _, column in positions.values()}))}
    motifs: dict[int, Grid] = {}
    for color in positions:
        cells = {(row, column) for row in range(height) for column in range(width) if grid[row][column] == color and not (r0 <= row <= r1 and c0 <= column <= c1)}
        if not cells:
            raise Undefined("quadrant key has no external motif")
        # One monochrome connected object per role.
        object_grid = tuple(tuple(color if (row, column) in cells else background for column in range(width)) for row in range(height))
        components = _components(object_grid, background, 8)
        if len(components) != 1:
            raise Undefined("external motif is disconnected")
        motifs[color] = _crop(grid, _bbox(cells))
    shapes = {_shape(motif) for motif in motifs.values()}
    if len(shapes) != 1:
        raise Undefined("quadrant motifs are not congruent")
    motif_h, motif_w = next(iter(shapes))
    canvas = [[background for _ in range(2 * motif_w + 1)] for _ in range(2 * motif_h + 1)]
    for color, (row, column) in positions.items():
        rslot, cslot = marker_rows[row], marker_columns[column]
        motif = motifs[color]
        rr, cc = rslot * (motif_h + 1), cslot * (motif_w + 1)
        for local_row in range(motif_h):
            canvas[rr + local_row][cc : cc + motif_w] = list(motif[local_row])
    return _freeze(canvas), {"quadrants": 4, "key_base": "filled reference panel", "gap": 1}


def _motif_template(height: int, width: int, name: str, length: int = 1) -> frozenset[Cell]:
    if height < 3 or width < 3:
        raise Undefined("rectangle is too small for an inset motif")
    top, bottom, left, right = 1, height - 2, 1, width - 2
    if name == "inner_horizontal_edges":
        return frozenset({(row, column) for row in (top, bottom) for column in range(left, right + 1)})
    if name == "inner_vertical_edges":
        return frozenset({(row, column) for column in (left, right) for row in range(top, bottom + 1)})
    if name == "inner_corners":
        return frozenset({(top, left), (top, right), (bottom, left), (bottom, right)})
    if name == "inner_frame":
        return _motif_template(height, width, "inner_horizontal_edges") | _motif_template(height, width, "inner_vertical_edges")
    if name == "inner_corner_l":
        points: set[Cell] = set()
        for row_anchor, row_sign in ((top, 1), (bottom, -1)):
            for column_anchor, column_sign in ((left, 1), (right, -1)):
                points.update((row_anchor, column_anchor + column_sign * offset) for offset in range(length) if left <= column_anchor + column_sign * offset <= right)
                points.update((row_anchor + row_sign * offset, column_anchor) for offset in range(length) if top <= row_anchor + row_sign * offset <= bottom)
        return frozenset(points)
    if name == "inner_corner_vertical":
        return frozenset(
            (row_anchor + row_sign * offset, column_anchor)
            for row_anchor, row_sign in ((top, 1), (bottom, -1))
            for column_anchor in (left, right)
            for offset in range(length)
            if top <= row_anchor + row_sign * offset <= bottom
        )
    if name == "inner_corner_horizontal":
        return frozenset(
            (row_anchor, column_anchor + column_sign * offset)
            for row_anchor in (top, bottom)
            for column_anchor, column_sign in ((left, 1), (right, -1))
            for offset in range(length)
            if left <= column_anchor + column_sign * offset <= right
        )
    raise Undefined("unknown motif template")


def _blank_rectangle_completion(grid: Grid) -> tuple[Grid, dict[str, Any]]:
    background = _border_mode(grid)
    colors = [color for color in _palette(grid) if color != background]
    proposals: list[tuple[int, int, tuple[int, int, int, int], str, int, int]] = []
    for marker in colors:
        regions: list[tuple[int, tuple[int, int, int, int], frozenset[Cell]]] = []
        for base in colors:
            if base == marker:
                continue
            base_cells = {(row, column) for row, line in enumerate(grid) for column, value in enumerate(line) if value == base}
            if not base_cells:
                continue
            box = _bbox(base_cells)
            r0, r1, c0, c1 = box
            values = {grid[row][column] for row in range(r0, r1 + 1) for column in range(c0, c1 + 1)}
            if not values <= {base, marker} or background in values:
                continue
            mask = frozenset((row - r0, column - c0) for row in range(r0, r1 + 1) for column in range(c0, c1 + 1) if grid[row][column] == marker)
            regions.append((base, box, mask))
        blanks = [record for record in regions if not record[2]]
        patterned = [record for record in regions if record[2]]
        if len(blanks) != 1 or len(patterned) < 2:
            continue
        kinds = [("inner_horizontal_edges", 1), ("inner_vertical_edges", 1), ("inner_corners", 1), ("inner_frame", 1)]
        kinds += [("inner_corner_l", length) for length in range(2, 5)]
        kinds += [("inner_corner_vertical", length) for length in range(2, 5)]
        kinds += [("inner_corner_horizontal", length) for length in range(2, 5)]
        for name, length in kinds:
            if all(mask == _motif_template(box[1] - box[0] + 1, box[3] - box[2] + 1, name, length) for _base, box, mask in patterned):
                base, box, _mask = blanks[0]
                proposals.append((marker, base, box, name, length, len(patterned)))
    behaviors: dict[str, list[tuple[tuple[int, int, tuple[int, int, int, int], str, int, int], Grid]]] = defaultdict(list)
    for proposal in proposals:
        marker, base, box, name, length, _support_regions = proposal
        height, width = box[1] - box[0] + 1, box[3] - box[2] + 1
        mask = _motif_template(height, width, name, length)
        output = tuple(
            tuple(marker if (row, column) in mask else base for column in range(width))
            for row in range(height)
        )
        behaviors[_canonical(_plain(output))].append((proposal, output))
    if len(behaviors) != 1:
        raise Undefined("blank rectangle motif is absent or ambiguous")
    entries = next(iter(behaviors.values()))
    entries.sort(key=lambda entry: (entry[0][3], entry[0][4], _canonical(entry[0][:5])))
    (marker, base, box, name, length, support_regions), output = entries[0]
    return output, {
        "exemplars": support_regions,
        "template": name,
        "length": length,
        "equivalent_local_templates": len(entries),
        "target": "unique blank rectangle",
    }


_OPERATORS: tuple[tuple[str, int, Callable[[Grid], tuple[Grid, dict[str, Any]]]], ...] = (
    ("nest_rectangles_top_left", 12, _nest_rectangles),
    ("occlusion_line_order", 13, _occlusion_line_order),
    ("ranked_panel_layers", 13, _ranked_panel_layers),
    ("lattice_pattern_substitution", 16, _lattice_pattern_substitution),
    ("template_hole_decode", 17, _template_hole_decode),
    ("panel_growth_extrapolate", 15, _panel_growth_extrapolate),
    ("keyed_quadrant_assembly", 16, _keyed_quadrant_assembly),
    ("blank_rectangle_completion", 15, _blank_rectangle_completion),
)
_FUNCTIONS = {name: function for name, _cost, function in _OPERATORS}


def _programs() -> tuple[dict[str, Any], ...]:
    return tuple(
        {"schema": SCHEMA, "operator": name, "description_length": cost}
        for name, cost, _function in _OPERATORS
    )


def _execute_internal(program: Mapping[str, Any], grid: Grid) -> tuple[Grid, dict[str, Any]]:
    if not isinstance(program, Mapping) or program.get("schema") != SCHEMA:
        raise Undefined("invalid panel-layout program")
    operator = program.get("operator")
    if operator not in _FUNCTIONS:
        raise Undefined("unknown panel-layout operator")
    return _FUNCTIONS[str(operator)](grid)


def execute_program(program: Mapping[str, Any], value: Any) -> list[list[int]]:
    """Execute one serialized panel-layout program."""

    return _plain(_execute_internal(program, _grid(value))[0])


def replay_program(program: Mapping[str, Any], value: Any) -> dict[str, Any]:
    """Replay an explicit parse, relational action, and render trace."""

    grid = _grid(value)
    output, receipt = _execute_internal(program, grid)
    parsed = {"kind": "panel_layout_atlas", "shape": list(_shape(grid))}
    action = {"operator": program["operator"], "receipt": receipt}
    return {
        "output": _plain(output),
        "stages": [
            {"name": "parse-layout-atlas", "input": _plain(grid), "output": parsed},
            {"name": "apply-relational-layout-program", "input": parsed, "output": action},
            {"name": "render-layout", "input": action, "output": _plain(output)},
        ],
    }


def _exact_programs(pairs: Sequence[Pair], probes: Sequence[Grid], limits: Limits) -> tuple[dict[str, Any], ...]:
    exact: list[dict[str, Any]] = []
    calls = 0
    for program in _programs():
        try:
            actual = []
            for source, _target in pairs:
                actual.append(_execute_internal(program, source)[0])
                calls += 1
            for probe in probes:
                _execute_internal(program, probe)
                calls += 1
            if calls > limits.max_executor_calls:
                raise Undefined("executor call cap exceeded")
        except (Undefined, ValueError, TypeError, KeyError, IndexError, ZeroDivisionError):
            continue
        if tuple(actual) == tuple(target for _source, target in pairs):
            exact.append(program)
    return tuple(exact)


def _behavior(program: Mapping[str, Any], grids: Sequence[Grid]) -> tuple[Grid, ...]:
    return tuple(_execute_internal(program, grid)[0] for grid in grids)


def _leave_one_out(train: Sequence[Pair], limits: Limits) -> tuple[bool, list[dict[str, Any]]]:
    witnesses: list[dict[str, Any]] = []
    for held_index, (held_source, held_target) in enumerate(train):
        subset = tuple(pair for index, pair in enumerate(train) if index != held_index)
        programs = _exact_programs(subset, (held_source,), limits)
        behaviors: dict[str, tuple[Grid, ...]] = {}
        for program in programs:
            try:
                output = _behavior(program, (held_source,))
            except Undefined:
                continue
            behaviors[_canonical([_plain(grid) for grid in output])] = output
        if len(behaviors) != 1 or next(iter(behaviors.values())) != (held_target,):
            return False, witnesses
        witnesses.append(
            {
                "held_out_index": held_index,
                "proposal_demo_count": len(subset),
                "rediscovered_programs": len(programs),
                "held_out_behavior_classes": 1,
                "held_out_exact": True,
                "held_out_output_hash": _digest(_plain(held_target)),
            }
        )
    return True, witnesses


def _swap(grid: Grid, left: int, right: int) -> Grid:
    return tuple(tuple(right if cell == left else left if cell == right else cell for cell in row) for row in grid)


def _palette_counterfactual(program: Mapping[str, Any], train: Sequence[Pair], limits: Limits) -> tuple[bool, list[dict[str, Any]]]:
    witnesses: list[dict[str, Any]] = []
    calls = 0
    for index, (source, target) in enumerate(train):
        colors = sorted(set(_palette(source)) | set(_palette(target)))
        if len(colors) < 2:
            return False, witnesses
        # Swap colors with distinct source frequencies when possible.  This is
        # a genuine role perturbation, not an identity rename.
        counts = Counter(cell for row in source for cell in row)
        pairs = [(left, right) for i, left in enumerate(colors) for right in colors[i + 1 :] if counts[left] != counts[right]]
        if not pairs:
            pairs = [(colors[0], colors[1])]
        left, right = pairs[0]
        calls += 1
        if calls > limits.max_counterfactual_calls:
            return False, witnesses
        try:
            actual = _execute_internal(program, _swap(source, left, right))[0]
        except Undefined:
            return False, witnesses
        expected = _swap(target, left, right)
        if actual != expected:
            return False, witnesses
        witnesses.append({"demo_index": index, "swap": [left, right], "conjugate_exact": True, "output_hash": _digest(_plain(actual))})
    return True, witnesses


def compile_task(task: Any, limits: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    """Compile one unique, proof-carrying held-out behavior or abstain."""

    try:
        bounds = Limits.from_value(limits)
        train, tests = _sanitize(task, bounds)
    except (Undefined, ValueError, TypeError, KeyError):
        return []
    programs = _programs()
    if len(programs) > bounds.max_programs:
        return []
    exact = _exact_programs(train, tests, bounds)
    if not exact:
        return []
    behaviors: dict[str, list[tuple[dict[str, Any], tuple[Grid, ...]]]] = defaultdict(list)
    for program in exact:
        try:
            predictions = _behavior(program, tests)
        except Undefined:
            continue
        behaviors[_canonical([_plain(grid) for grid in predictions])].append((program, predictions))
    if len(behaviors) != 1:
        return []
    behavior_key, entries = next(iter(behaviors.items()))
    entries.sort(key=lambda item: (int(item[0]["description_length"]), _canonical(item[0])))
    program, predictions = entries[0]
    loo_ok, loo_witnesses = _leave_one_out(train, bounds)
    if not loo_ok:
        return []
    counterfactual_ok, counterfactual_witnesses = _palette_counterfactual(program, train, bounds)
    if not counterfactual_ok:
        return []
    try:
        replay = _behavior(program, tuple(source for source, _target in train))
    except Undefined:
        return []
    if replay != tuple(target for _source, target in train):
        return []
    return [
        {
            "family": "panel_layout_compiler",
            "program": json.loads(_canonical(program)),
            "train_outputs": [_plain(grid) for grid in replay],
            "test_outputs": [_plain(grid) for grid in predictions],
            "complexity": int(program["description_length"]),
            "evidence": {
                "author": AUTHOR,
                "all_demonstrations_exact": True,
                "exact_replay": True,
                "strict_leave_one_out": True,
                "leave_one_out_witnesses": loo_witnesses,
                "palette_counterfactual": True,
                "palette_counterfactual_witnesses": counterfactual_witnesses,
                "complete_behavior_quotient": True,
                "unique_test_behavior": True,
                "behavior_hash": _digest(json.loads(behavior_key)),
                "corroborating_programs": len(entries),
                "programs_enumerated": len(programs),
                "bounded_search": True,
                "task_identity_free": True,
                "test_outputs_observed": False,
            },
        }
    ] if bounds.max_candidates else []


__all__ = ["AUTHOR", "Limits", "SCHEMA", "compile_task", "execute_program", "replay_program"]
