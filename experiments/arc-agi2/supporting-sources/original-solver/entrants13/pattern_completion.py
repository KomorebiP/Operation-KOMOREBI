"""Deterministic periodic and symmetry completion entrant for Block 13.

Author: Komorebi P.

This module is a bounded, task-agnostic program synthesizer.  It sees only
demonstration input/output pairs and test *inputs*.  Every returned program is
independently executable, JSON-safe, and is retained only when it reproduces
all demonstrations exactly.  The candidate order is minimum-description-
length (MDL) order, so ``max_programs=1`` is a supported, principled mode rather
than an incidental truncation of enumeration order.

The language covers four deliberately related kinds of regularity:

* periodic residue reconstruction, including row-only and column-only periods;
* tiling or reflected tiling of a full grid or a detected motif;
* conservative horizontal, vertical, rotational, and diagonal completion;
* coordinate color cycles (rows, columns, diagonals, checkerboards, and rings).

There are no task identifiers, corpus fingerprints, test targets, or stored
solutions anywhere in this implementation.
"""

from __future__ import annotations

from collections import Counter, deque
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import json
from typing import Any, Optional


Grid = list[list[int]]
Pair = tuple[Grid, Grid]


class _Undefined(ValueError):
    """A program is outside its semantic domain for a particular grid."""


@dataclass(frozen=True)
class Limits:
    max_side: int = 30
    max_programs: int = 64
    max_period: int = 8
    max_hypotheses: int = 12000

    @classmethod
    def from_value(cls, value: Any) -> "Limits":
        if value is None:
            return cls()

        def read(name: str, default: int) -> int:
            if isinstance(value, Mapping):
                raw = value.get(name, default)
            else:
                raw = getattr(value, name, default)
            if isinstance(raw, bool) or not isinstance(raw, int):
                return default
            return raw

        max_programs = read("max_programs", read("max_candidates", cls.max_programs))
        if isinstance(value, Mapping):
            cap = value.get("max_candidates")
            if isinstance(cap, int) and not isinstance(cap, bool):
                max_programs = min(max_programs, cap)
        return cls(
            max_side=max(1, min(60, read("max_side", cls.max_side))),
            max_programs=max(0, min(256, max_programs)),
            max_period=max(1, min(15, read("max_period", cls.max_period))),
            max_hypotheses=max(1, min(100000, read("max_hypotheses", cls.max_hypotheses))),
        )


def _grid(value: Any, max_side: int) -> Optional[Grid]:
    if not isinstance(value, list) or not value or len(value) > max_side:
        return None
    width: Optional[int] = None
    result: Grid = []
    for raw_row in value:
        if not isinstance(raw_row, list) or not raw_row or len(raw_row) > max_side:
            return None
        if width is None:
            width = len(raw_row)
        elif len(raw_row) != width:
            return None
        row: list[int] = []
        for value_cell in raw_row:
            if isinstance(value_cell, bool) or not isinstance(value_cell, int):
                return None
            if value_cell < 0 or value_cell > 9:
                return None
            row.append(int(value_cell))
        result.append(row)
    return result


def _read_task(task: Any, limits: Limits) -> Optional[tuple[list[Pair], list[Grid]]]:
    if not isinstance(task, Mapping):
        return None
    raw_train = task.get("train")
    raw_test = task.get("test")
    if (
        not isinstance(raw_train, Sequence)
        or isinstance(raw_train, (str, bytes))
        or not raw_train
        or not isinstance(raw_test, Sequence)
        or isinstance(raw_test, (str, bytes))
        or not raw_test
    ):
        return None
    train: list[Pair] = []
    for example in raw_train:
        if not isinstance(example, Mapping):
            return None
        source = _grid(example.get("input"), limits.max_side)
        target = _grid(example.get("output"), limits.max_side)
        if source is None or target is None:
            return None
        train.append((source, target))
    tests: list[Grid] = []
    for example in raw_test:
        if not isinstance(example, Mapping):
            return None
        # Do not inspect any field except the test input.
        source = _grid(example.get("input"), limits.max_side)
        if source is None:
            return None
        tests.append(source)
    return train, tests


def _shape(grid: Grid) -> tuple[int, int]:
    return len(grid), len(grid[0])


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _mode(values: Sequence[int], tie: str = "smallest") -> int:
    if not values:
        raise _Undefined("empty mode")
    counts = Counter(values)
    maximum = max(counts.values())
    tied = {value for value, count in counts.items() if count == maximum}
    if tie == "first":
        return next(value for value in values if value in tied)
    if tie == "last":
        return next(value for value in reversed(values) if value in tied)
    return min(tied)


def _background(grid: Grid, record: Mapping[str, Any]) -> int:
    kind = record.get("kind")
    values = [cell for row in grid for cell in row]
    if kind == "modal":
        return _mode(values)
    if kind == "literal":
        color = int(record.get("color", -1))
        if not 0 <= color <= 9:
            raise _Undefined("invalid literal background")
        return color
    raise _Undefined("unknown background selector")


def _shape_rules(train: Sequence[Pair]) -> list[dict[str, Any]]:
    rules: list[dict[str, Any]] = []

    def add(rule: dict[str, Any]) -> None:
        key = _canonical(rule)
        if key not in {_canonical(old) for old in rules}:
            rules.append(rule)

    source_shapes = [_shape(source) for source, _ in train]
    target_shapes = [_shape(target) for _, target in train]
    if all(source == target for source, target in zip(source_shapes, target_shapes)):
        add({"kind": "same"})
    if all((w, h) == target for (h, w), target in zip(source_shapes, target_shapes)):
        add({"kind": "transpose"})

    deltas = [(oh - ih, ow - iw) for (ih, iw), (oh, ow) in zip(source_shapes, target_shapes)]
    if len(set(deltas)) == 1:
        dh, dw = deltas[0]
        if (dh, dw) != (0, 0):
            add({"kind": "add", "rows": dh, "columns": dw})

    factors: list[tuple[int, int]] = []
    if all(oh % ih == 0 and ow % iw == 0 for (ih, iw), (oh, ow) in zip(source_shapes, target_shapes)):
        factors = [(oh // ih, ow // iw) for (ih, iw), (oh, ow) in zip(source_shapes, target_shapes)]
    if factors and len(set(factors)) == 1 and factors[0] != (1, 1):
        rh, rw = factors[0]
        add({"kind": "scale", "rows": rh, "columns": rw})

    if len(set(target_shapes)) == 1:
        height, width = target_shapes[0]
        add({"kind": "fixed", "height": height, "width": width})
    if all(oh == ow == max(ih, iw) for (ih, iw), (oh, ow) in zip(source_shapes, target_shapes)):
        add({"kind": "square_max"})
    return rules


def _resolve_shape(source: Grid, rule: Mapping[str, Any]) -> tuple[int, int]:
    height, width = _shape(source)
    kind = rule.get("kind")
    if kind == "same":
        result = height, width
    elif kind == "transpose":
        result = width, height
    elif kind == "add":
        result = height + int(rule["rows"]), width + int(rule["columns"])
    elif kind == "scale":
        result = height * int(rule["rows"]), width * int(rule["columns"])
    elif kind == "fixed":
        result = int(rule["height"]), int(rule["width"])
    elif kind == "square_max":
        result = max(height, width), max(height, width)
    else:
        raise _Undefined("unknown shape rule")
    if result[0] <= 0 or result[1] <= 0 or result[0] > 60 or result[1] > 60:
        raise _Undefined("invalid output shape")
    return result


def _shape_cost(rule: Mapping[str, Any]) -> int:
    return {
        "same": 0,
        "transpose": 1,
        "scale": 2,
        "add": 3,
        "square_max": 3,
        "fixed": 7,
    }.get(str(rule.get("kind")), 9)


def _palette(grid: Grid) -> list[int]:
    return sorted({cell for row in grid for cell in row})


def _first_order(grid: Grid) -> list[int]:
    result: list[int] = []
    for row in grid:
        for color in row:
            if color not in result:
                result.append(color)
    return result


def _frequency_order(grid: Grid, descending: bool) -> list[int]:
    values = [cell for row in grid for cell in row]
    counts = Counter(values)
    return sorted(counts, key=lambda color: ((-counts[color] if descending else counts[color]), color))


def _resolve_color(grid: Grid, selector: Mapping[str, Any]) -> int:
    kind = selector.get("kind")
    if kind == "literal":
        result = int(selector["color"])
    elif kind == "modal":
        result = _mode([cell for row in grid for cell in row])
    elif kind == "unique_nonmodal":
        modal = _mode([cell for row in grid for cell in row])
        others = [color for color in _palette(grid) if color != modal]
        if len(others) != 1:
            raise _Undefined("nonmodal color is not unique")
        result = others[0]
    else:
        index = int(selector.get("index", -1))
        if kind == "first_occurrence":
            order = _first_order(grid)
        elif kind == "sorted_palette":
            order = _palette(grid)
        elif kind == "frequency_descending":
            order = _frequency_order(grid, True)
        elif kind == "frequency_ascending":
            order = _frequency_order(grid, False)
        else:
            raise _Undefined("unknown color selector")
        if not 0 <= index < len(order):
            raise _Undefined("color role outside palette")
        result = order[index]
    if not 0 <= result <= 9:
        raise _Undefined("invalid resolved color")
    return result


def _selector_cost(selector: Mapping[str, Any]) -> int:
    return {
        "modal": 1,
        "unique_nonmodal": 1,
        "frequency_descending": 2,
        "frequency_ascending": 2,
        "first_occurrence": 2,
        "sorted_palette": 2,
        "literal": 4,
    }.get(str(selector.get("kind")), 8)


def _selector_options(observations: Sequence[tuple[Grid, int]]) -> list[dict[str, Any]]:
    if not observations:
        return []
    maximum_palette = max(len(_palette(grid)) for grid, _ in observations)
    proposals: list[dict[str, Any]] = [{"kind": "modal"}, {"kind": "unique_nonmodal"}]
    for index in range(maximum_palette):
        for kind in (
            "frequency_descending",
            "frequency_ascending",
            "first_occurrence",
            "sorted_palette",
        ):
            proposals.append({"kind": kind, "index": index})
    targets = {target for _, target in observations}
    if len(targets) == 1:
        proposals.append({"kind": "literal", "color": next(iter(targets))})
    result: list[dict[str, Any]] = []
    for proposal in proposals:
        try:
            if all(_resolve_color(grid, proposal) == target for grid, target in observations):
                result.append(proposal)
        except _Undefined:
            continue
    result.sort(key=lambda record: (_selector_cost(record), _canonical(record)))
    return result


def _resolve_period(value: Any, source: Grid, axis: str) -> int:
    if value == "height" and axis == "row":
        return len(source)
    if value == "width" and axis == "column":
        return len(source[0])
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise _Undefined("invalid period")
    return value


def _residue_template(
    source: Grid,
    row_period: int,
    column_period: int,
    reducer: str,
    background: Mapping[str, Any],
) -> Grid:
    groups: list[list[list[int]]] = [
        [[] for _ in range(column_period)] for _ in range(row_period)
    ]
    for row, values in enumerate(source):
        for column, color in enumerate(values):
            groups[row % row_period][column % column_period].append(color)
    bg = _background(source, background)
    result: Grid = []
    for row in range(row_period):
        output_row: list[int] = []
        for column in range(column_period):
            values = groups[row][column]
            if not values:
                raise _Undefined("unobserved residue")
            if reducer == "mode_smallest":
                color = _mode(values, "smallest")
            elif reducer == "mode_first":
                color = _mode(values, "first")
            elif reducer == "mode_last":
                color = _mode(values, "last")
            elif reducer == "nonbackground_mode":
                visible = [value for value in values if value != bg]
                color = _mode(visible, "first") if visible else bg
            elif reducer == "first":
                color = values[0]
            elif reducer == "last":
                color = values[-1]
            else:
                raise _Undefined("unknown residue reducer")
            output_row.append(color)
        result.append(output_row)
    return result


def _bbox_region(source: Grid, background: int) -> Grid:
    points = [
        (row, column)
        for row, values in enumerate(source)
        for column, color in enumerate(values)
        if color != background
    ]
    if not points:
        raise _Undefined("empty foreground")
    top = min(row for row, _ in points)
    bottom = max(row for row, _ in points)
    left = min(column for _, column in points)
    right = max(column for _, column in points)
    return [values[left : right + 1] for values in source[top : bottom + 1]]


def _component_region(source: Grid, background: int, connectivity: int) -> Grid:
    height, width = _shape(source)
    remaining = {
        (row, column)
        for row in range(height)
        for column in range(width)
        if source[row][column] != background
    }
    components: list[list[tuple[int, int]]] = []
    if connectivity == 4:
        offsets = ((-1, 0), (0, -1), (0, 1), (1, 0))
    else:
        offsets = tuple(
            (dr, dc)
            for dr in (-1, 0, 1)
            for dc in (-1, 0, 1)
            if (dr, dc) != (0, 0)
        )
    while remaining:
        seed = min(remaining)
        remaining.remove(seed)
        queue = deque([seed])
        component = [seed]
        while queue:
            row, column = queue.popleft()
            for dr, dc in offsets:
                point = row + dr, column + dc
                if point in remaining:
                    remaining.remove(point)
                    queue.append(point)
                    component.append(point)
        components.append(component)
    component = min(
        components,
        key=lambda points: (-len(points), min(points), max(points)),
    )
    top = min(row for row, _ in component)
    bottom = max(row for row, _ in component)
    left = min(column for _, column in component)
    right = max(column for _, column in component)
    return [values[left : right + 1] for values in source[top : bottom + 1]]


def _minimal_exact_tile(source: Grid) -> Grid:
    height, width = _shape(source)
    for area in range(1, height * width + 1):
        for rows in range(1, height + 1):
            if area % rows:
                continue
            columns = area // rows
            if columns > width:
                continue
            if all(
                source[row][column] == source[row % rows][column % columns]
                for row in range(height)
                for column in range(width)
            ):
                return [values[:columns] for values in source[:rows]]
    return [row[:] for row in source]


def _trim_uniform_bottom_right(source: Grid) -> Grid:
    """Remove a same-colored solid suffix frame from bottom and right.

    Several completion tasks present a periodic prefix in the upper-left and
    reserve one or more solid rows/columns as the area to continue into.  The
    suffix width is deliberately inferred afresh for each input.
    """

    height, width = _shape(source)
    color = source[-1][-1]
    trailing_rows = 0
    for row in range(height - 1, -1, -1):
        if all(value == color for value in source[row]):
            trailing_rows += 1
        else:
            break
    trailing_columns = 0
    for column in range(width - 1, -1, -1):
        if all(source[row][column] == color for row in range(height)):
            trailing_columns += 1
        else:
            break
    if trailing_rows == 0 or trailing_columns == 0:
        raise _Undefined("no solid bottom-right suffix")
    kept_height = height - trailing_rows
    kept_width = width - trailing_columns
    if kept_height <= 0 or kept_width <= 0:
        raise _Undefined("suffix consumed whole grid")
    return [row[:kept_width] for row in source[:kept_height]]


def _region(source: Grid, record: Mapping[str, Any]) -> Grid:
    kind = record.get("kind")
    if kind == "full":
        return [row[:] for row in source]
    if kind == "minimal_exact_tile":
        return _minimal_exact_tile(source)
    if kind == "trim_suffix_minimal_tile":
        return _minimal_exact_tile(_trim_uniform_bottom_right(source))
    if kind in {"foreground_bbox", "largest_component"}:
        bg = _background(source, record["background"])
        if kind == "foreground_bbox":
            return _bbox_region(source, bg)
        return _component_region(source, bg, int(record.get("connectivity", 4)))
    if kind == "first_row":
        return [source[0][:]]
    if kind == "first_column":
        return [[row[0]] for row in source]
    raise _Undefined("unknown motif region")


def _bounce(index: int, length: int, duplicate_edge: bool) -> int:
    if length <= 0:
        raise _Undefined("empty reflected tile")
    if length == 1:
        return 0
    period = 2 * length if duplicate_edge else 2 * (length - 1)
    value = index % period
    if duplicate_edge:
        return value if value < length else period - 1 - value
    return value if value < length else period - value


def _symmetry_coordinate(kind: str, row: int, column: int, height: int, width: int) -> tuple[int, int]:
    if kind == "horizontal":
        return height - 1 - row, column
    if kind == "vertical":
        return row, width - 1 - column
    if kind == "rotation_180":
        return height - 1 - row, width - 1 - column
    if kind == "main_diagonal" and height == width:
        return column, row
    if kind == "anti_diagonal" and height == width:
        return width - 1 - column, height - 1 - row
    raise _Undefined("symmetry unavailable for shape")


def _symmetry_orbit(source: Grid, row: int, column: int, transforms: Sequence[str]) -> list[tuple[int, int]]:
    height, width = _shape(source)
    seen = {(row, column)}
    queue = deque([(row, column)])
    while queue:
        rr, cc = queue.popleft()
        for transform in transforms:
            point = _symmetry_coordinate(transform, rr, cc, height, width)
            if point not in seen:
                seen.add(point)
                queue.append(point)
    return sorted(seen)


def _symmetry_complete(source: Grid, program: Mapping[str, Any]) -> Grid:
    transforms = [str(value) for value in program["transforms"]]
    policy = str(program["policy"])
    bg = _background(source, program["background"])
    result = [row[:] for row in source]
    visited: set[tuple[int, int]] = set()
    height, width = _shape(source)
    for row in range(height):
        for column in range(width):
            if (row, column) in visited:
                continue
            orbit = _symmetry_orbit(source, row, column, transforms)
            visited.update(orbit)
            values = [source[rr][cc] for rr, cc in orbit]
            visible = [value for value in values if value != bg]
            if policy == "fill_background_unique":
                colors = set(visible)
                if len(colors) != 1:
                    continue
                color = visible[0]
                for rr, cc in orbit:
                    if source[rr][cc] == bg:
                        result[rr][cc] = color
            elif policy == "fill_background_mode":
                if not visible:
                    continue
                color = _mode(visible, "first")
                for rr, cc in orbit:
                    if source[rr][cc] == bg:
                        result[rr][cc] = color
            elif policy == "orbit_nonbackground_mode":
                if visible:
                    color = _mode(visible, "first")
                    for rr, cc in orbit:
                        result[rr][cc] = color
            elif policy == "orbit_mode":
                color = _mode(values, "first")
                for rr, cc in orbit:
                    result[rr][cc] = color
            else:
                raise _Undefined("unknown symmetry policy")
    return result


def _mirror_expand(source: Grid, program: Mapping[str, Any]) -> Grid:
    result = [row[:] for row in source]
    vertical = bool(program.get("vertical"))
    horizontal = bool(program.get("horizontal"))
    overlap = int(program.get("overlap", 0))
    reverse_order = bool(program.get("reverse_order"))
    if horizontal:
        mirrored = [list(reversed(row)) for row in result]
        if overlap:
            mirrored = [row[1:] if reverse_order else row[:-1] for row in mirrored]
        result = [
            (mirror + row if reverse_order else row + mirror)
            for row, mirror in zip(result, mirrored)
        ]
    if vertical:
        mirrored_rows = [row[:] for row in reversed(result)]
        if overlap:
            mirrored_rows = mirrored_rows[1:] if reverse_order else mirrored_rows[:-1]
        result = mirrored_rows + result if reverse_order else result + mirrored_rows
    return result


def _coordinate_index(kind: str, row: int, column: int, height: int, width: int, period: int) -> int:
    if kind == "row":
        value = row
    elif kind == "column":
        value = column
    elif kind == "diagonal":
        value = row + column
    elif kind == "anti_diagonal":
        value = row - column
    elif kind == "ring":
        value = min(row, column, height - 1 - row, width - 1 - column)
    else:
        raise _Undefined("unknown coordinate cycle")
    return value % period


def _singletons(source: Grid, background: int) -> list[tuple[int, int, int]]:
    counts = Counter(cell for row in source for cell in row if cell != background)
    return [
        (row, column, color)
        for row, values in enumerate(source)
        for column, color in enumerate(values)
        if color != background and counts[color] == 1
    ]


def _ring_clue_fill(source: Grid, background: Mapping[str, Any]) -> Grid:
    bg = _background(source, background)
    height, width = _shape(source)
    maximum_ring = (min(height, width) - 1) // 2
    clues: dict[int, int] = {}
    for row in range(height):
        for column in range(width):
            color = source[row][column]
            if color == bg:
                continue
            ring = min(row, column, height - 1 - row, width - 1 - column)
            if ring in clues and clues[ring] != color:
                raise _Undefined("conflicting ring clues")
            clues[ring] = color
    if set(clues) != set(range(maximum_ring + 1)):
        raise _Undefined("one clue is required for every ring")
    return [
        [clues[min(row, column, height - 1 - row, width - 1 - column)] for column in range(width)]
        for row in range(height)
    ]


def _singleton_cross(source: Grid, background: Mapping[str, Any]) -> Grid:
    bg = _background(source, background)
    markers = _singletons(source, bg)
    if len(markers) != 1:
        raise _Undefined("cross requires one singleton color")
    marker_row, marker_column, marker_color = markers[0]
    result = [row[:] for row in source]
    for row in range(len(source)):
        if result[row][marker_column] == bg:
            result[row][marker_column] = marker_color
    for column in range(len(source[0])):
        if result[marker_row][column] == bg:
            result[marker_row][column] = marker_color
    return result


def _alternating_rays(source: Grid, program: Mapping[str, Any]) -> Grid:
    bg = _background(source, program["background"])
    fill = int(program["alternating_color"])
    direction = str(program["direction"])
    offsets = {"right": (0, 1), "left": (0, -1), "down": (1, 0), "up": (-1, 0)}
    if direction not in offsets:
        raise _Undefined("unknown ray direction")
    dr, dc = offsets[direction]
    height, width = _shape(source)
    seeds = [
        (row, column, source[row][column])
        for row in range(height)
        for column in range(width)
        if source[row][column] != bg
    ]
    if not seeds:
        raise _Undefined("no ray seeds")
    overlay: dict[tuple[int, int], int] = {}
    for row, column, seed_color in seeds:
        rr, cc, distance = row, column, 0
        while 0 <= rr < height and 0 <= cc < width:
            color = seed_color if distance % 2 == 0 else fill
            old = overlay.get((rr, cc))
            if old is not None and old != color:
                raise _Undefined("crossing alternating rays disagree")
            overlay[rr, cc] = color
            rr += dr
            cc += dc
            distance += 1
    result = [row[:] for row in source]
    for (row, column), color in overlay.items():
        if source[row][column] == bg or source[row][column] == color:
            result[row][column] = color
        elif source[row][column] != color:
            raise _Undefined("ray overwrites a seed")
    return result


def _centered_inventory_line(source: Grid, program: Mapping[str, Any]) -> Grid:
    bg = _background(source, program["background"])
    foreground = [(r, c, value) for r, row in enumerate(source) for c, value in enumerate(row) if value != bg]
    colors = {value for _, _, value in foreground}
    if len(colors) != 1 or not foreground:
        raise _Undefined("inventory line requires one foreground color")
    color = next(iter(colors))
    count = len(foreground)
    height, width = _shape(source)
    result = [[bg for _ in range(width)] for _ in range(height)]
    orientation = str(program["orientation"])
    if orientation == "horizontal":
        if count > width:
            raise _Undefined("inventory does not fit horizontally")
        row = height // 2
        left = (width - count) // 2
        for column in range(left, left + count):
            result[row][column] = color
    elif orientation == "vertical":
        if count > height:
            raise _Undefined("inventory does not fit vertically")
        column = width // 2
        top = (height - count) // 2
        for row in range(top, top + count):
            result[row][column] = color
    else:
        raise _Undefined("unknown inventory orientation")
    return result


def _left_edge_diagonal_frame(source: Grid, program: Mapping[str, Any]) -> Grid:
    bg = _background(source, program["background"])
    height, width = _shape(source)
    if height != width:
        raise _Undefined("diagonal frame requires a square")
    edge_color = source[0][0]
    if edge_color == bg or any(source[row][0] != edge_color for row in range(height)):
        raise _Undefined("left edge is not the seed line")
    if any(source[row][column] != bg for row in range(height) for column in range(1, width)):
        raise _Undefined("unexpected nonbackground outside seed edge")
    diagonal_color = int(program["diagonal_color"])
    base_color = int(program["base_color"])
    result = [row[:] for row in source]
    for row in range(height - 1):
        result[row][width - 1 - row] = diagonal_color
    for column in range(1, width):
        result[height - 1][column] = base_color
    return result


def _component_cells(source: Grid, color: int, connectivity: int) -> list[list[tuple[int, int]]]:
    height, width = _shape(source)
    remaining = {(r, c) for r in range(height) for c in range(width) if source[r][c] == color}
    offsets = (
        ((-1, 0), (0, -1), (0, 1), (1, 0))
        if connectivity == 4
        else tuple(
            (dr, dc)
            for dr in (-1, 0, 1)
            for dc in (-1, 0, 1)
            if (dr, dc) != (0, 0)
        )
    )
    result: list[list[tuple[int, int]]] = []
    while remaining:
        seed = min(remaining)
        remaining.remove(seed)
        queue = deque([seed])
        component = [seed]
        while queue:
            row, column = queue.popleft()
            for dr, dc in offsets:
                point = row + dr, column + dc
                if point in remaining:
                    remaining.remove(point)
                    queue.append(point)
                    component.append(point)
        result.append(component)
    return result


def _component_seed_flood(source: Grid, program: Mapping[str, Any]) -> Grid:
    bg = _background(source, program["background"])
    fill = int(program["fill_color"])
    connectivity = int(program["connectivity"])
    adjacency = int(program["adjacency"])
    neighbor_offsets = (
        ((-1, 0), (0, -1), (0, 1), (1, 0))
        if adjacency == 4
        else tuple(
            (dr, dc)
            for dr in (-1, 0, 1)
            for dc in (-1, 0, 1)
            if (dr, dc) != (0, 0)
        )
    )
    height, width = _shape(source)
    result = [row[:] for row in source]
    for component in _component_cells(source, fill, connectivity):
        seeds: set[int] = set()
        for row, column in component:
            for dr, dc in neighbor_offsets:
                rr, cc = row + dr, column + dc
                if 0 <= rr < height and 0 <= cc < width:
                    value = source[rr][cc]
                    if value not in {bg, fill}:
                        seeds.add(value)
        if len(seeds) != 1:
            raise _Undefined("fill component lacks a unique adjacent seed")
        color = next(iter(seeds))
        for row, column in component:
            result[row][column] = color
    return result


def _largest_background_rectangle(source: Grid, background: int) -> tuple[int, int, int, int]:
    height, width = _shape(source)
    candidates: set[tuple[int, int, int, int]] = set()
    for top in range(height):
        valid = [True] * width
        for bottom in range(top, height):
            valid = [old and source[bottom][column] == background for column, old in enumerate(valid)]
            left = 0
            while left < width:
                while left < width and not valid[left]:
                    left += 1
                right = left
                while right < width and valid[right]:
                    right += 1
                if bottom > top and right - left >= 2:
                    candidates.add((top, bottom, left, right - 1))
                left = right + 1
    if not candidates:
        raise _Undefined("no two-dimensional background rectangle")
    areas = {
        rectangle: (rectangle[1] - rectangle[0] + 1) * (rectangle[3] - rectangle[2] + 1)
        for rectangle in candidates
    }
    maximum = max(areas.values())
    winners = [rectangle for rectangle, area in areas.items() if area == maximum]
    if len(winners) != 1:
        raise _Undefined("largest rectangle is not unique")
    return winners[0]


def _rectangle_fill(source: Grid, program: Mapping[str, Any]) -> Grid:
    bg = _background(source, program["background"])
    top, bottom, left, right = _largest_background_rectangle(source, bg)
    result = [row[:] for row in source]
    color = int(program["fill_color"])
    for row in range(top, bottom + 1):
        for column in range(left, right + 1):
            result[row][column] = color
    return result


def _vertical_bar_fan(source: Grid, program: Mapping[str, Any]) -> Grid:
    bg = _background(source, program["background"])
    points = [(r, c, v) for r, row in enumerate(source) for c, v in enumerate(row) if v != bg]
    if not points:
        raise _Undefined("fan requires a seed bar")
    columns = {column for _, column, _ in points}
    colors = {color for _, _, color in points}
    if len(columns) != 1 or len(colors) != 1:
        raise _Undefined("fan seed is not one vertical bar")
    column = next(iter(columns))
    seed_color = next(iter(colors))
    rows = sorted(row for row, _, _ in points)
    if rows != list(range(len(rows))):
        raise _Undefined("fan bar must start at the top")
    length = len(rows)
    left_color = int(program["left_color"])
    right_color = int(program["right_color"])
    height, width = _shape(source)
    result = [row[:] for row in source]
    for row in range(height):
        for cc in range(width):
            if cc < column and row < length + 2 * (column - cc):
                result[row][cc] = left_color
            elif cc > column and row < length - 2 * (cc - column):
                result[row][cc] = right_color
    for row in rows:
        result[row][column] = seed_color
    return result


def _nearest_parallel_borders(source: Grid, program: Mapping[str, Any]) -> Grid:
    bg = _background(source, program["background"])
    height, width = _shape(source)
    horizontal = len(set(source[0])) == 1 and len(set(source[-1])) == 1
    vertical = len({source[row][0] for row in range(height)}) == 1 and len(
        {source[row][-1] for row in range(height)}
    ) == 1
    if horizontal and source[0][0] != bg and source[-1][0] != bg and source[0][0] != source[-1][0]:
        orientation = "horizontal"
        first, second = source[0][0], source[-1][0]
    elif vertical and source[0][0] != bg and source[0][-1] != bg and source[0][0] != source[0][-1]:
        orientation = "vertical"
        first, second = source[0][0], source[0][-1]
    else:
        raise _Undefined("no opposing colored borders")
    tie_first = bool(program.get("tie_first", True))
    result = [row[:] for row in source]
    for row in range(height):
        for column in range(width):
            value = source[row][column]
            if value in {bg, first, second}:
                continue
            if orientation == "horizontal":
                first_distance, second_distance = row, height - 1 - row
            else:
                first_distance, second_distance = column, width - 1 - column
            result[row][column] = first if first_distance < second_distance or (
                first_distance == second_distance and tie_first
            ) else second
    return result


def _singleton_focus(source: Grid, program: Mapping[str, Any]) -> Grid:
    bg = _background(source, program["background"])
    markers = _singletons(source, bg)
    if len(markers) != 1:
        raise _Undefined("focus requires exactly one singleton-colored cell")
    marker_row, marker_column, marker_color = markers[0]
    ring_color = int(program["ring_color"])
    height, width = _shape(source)
    result = [[bg for _ in range(width)] for _ in range(height)]
    for row in range(max(0, marker_row - 1), min(height, marker_row + 2)):
        for column in range(max(0, marker_column - 1), min(width, marker_column + 2)):
            result[row][column] = ring_color
    result[marker_row][marker_column] = marker_color
    return result


def _marker_line_projection(source: Grid, program: Mapping[str, Any]) -> Grid:
    bg = _background(source, program["background"])
    horizontal_colors = {int(color) for color in program["horizontal_colors"]}
    vertical_colors = {int(color) for color in program["vertical_colors"]}
    if horizontal_colors & vertical_colors:
        raise _Undefined("projection orientation overlap")
    markers = [(r, c, v) for r, row in enumerate(source) for c, v in enumerate(row) if v != bg]
    if any(color not in horizontal_colors | vertical_colors for _, _, color in markers):
        raise _Undefined("unclassified projection marker")
    result = [row[:] for row in source]
    height, width = _shape(source)

    def horizontal() -> None:
        for row, _, color in markers:
            if color in horizontal_colors:
                for column in range(width):
                    result[row][column] = color

    def vertical() -> None:
        for _, column, color in markers:
            if color in vertical_colors:
                for row in range(height):
                    result[row][column] = color

    if program.get("horizontal_priority", True):
        vertical()
        horizontal()
    else:
        horizontal()
        vertical()
    return result


def _bottom_seed_serpentine(source: Grid, program: Mapping[str, Any]) -> Grid:
    bg = _background(source, program["background"])
    markers = _singletons(source, bg)
    if len(markers) != 1 or markers[0][0] != len(source) - 1:
        raise _Undefined("serpentine requires one bottom-edge seed")
    _, start, seed_color = markers[0]
    accent = int(program["accent_color"])
    height, width = _shape(source)
    result = [[bg for _ in range(width)] for _ in range(height)]
    for column in range(start, width, 2):
        for row in range(height):
            result[row][column] = seed_color
    for index, column in enumerate(range(start + 1, width, 2)):
        row = 0 if index % 2 == 0 else height - 1
        result[row][column] = accent
    return result


def _frame_marker_quadrants(source: Grid, program: Mapping[str, Any]) -> Grid:
    bg = _background(source, program["background"])
    frame_color = int(program["frame_color"])
    height, width = _shape(source)
    points = [(r, c) for r in range(height) for c in range(width) if source[r][c] == frame_color]
    if not points:
        raise _Undefined("missing frame")
    top, bottom = min(r for r, _ in points), max(r for r, _ in points)
    left, right = min(c for _, c in points), max(c for _, c in points)
    if bottom - top < 2 or right - left < 2:
        raise _Undefined("frame has no interior")
    border = {
        (r, c)
        for r in range(top, bottom + 1)
        for c in range(left, right + 1)
        if r in {top, bottom} or c in {left, right}
    }
    if any(source[r][c] != frame_color for r, c in border):
        raise _Undefined("frame border is incomplete")
    markers = [
        (r, c, source[r][c])
        for r in range(height)
        for c in range(width)
        if source[r][c] not in {bg, frame_color}
    ]
    if len(markers) != 2 or markers[0][2] == markers[1][2]:
        raise _Undefined("two distinct external markers required")
    corners = {
        "tl": (top + 1, left + 1),
        "tr": (top + 1, right - 1),
        "bl": (bottom - 1, left + 1),
        "br": (bottom - 1, right - 1),
    }
    opposite = {"tl": "br", "br": "tl", "tr": "bl", "bl": "tr"}
    assignments: dict[str, int] = {}
    for row, column, color in markers:
        distances = {
            name: abs(row - point[0]) + abs(column - point[1]) for name, point in corners.items()
        }
        minimum = min(distances.values())
        nearest = [name for name, distance in distances.items() if distance == minimum]
        if len(nearest) != 1:
            raise _Undefined("marker is equidistant from frame corners")
        corner = nearest[0]
        for name in (corner, opposite[corner]):
            if name in assignments and assignments[name] != color:
                raise _Undefined("corner assignment conflict")
            assignments[name] = color
    if set(assignments) != set(corners):
        raise _Undefined("markers do not determine all quadrants")
    middle_row = (top + bottom) / 2
    middle_column = (left + right) / 2
    result = [row[:] for row in source]
    for row in range(top + 1, bottom):
        for column in range(left + 1, right):
            name = ("t" if row < middle_row else "b") + ("l" if column < middle_column else "r")
            result[row][column] = assignments[name]
    return result


def _row_or_column_seed_recolor(source: Grid, program: Mapping[str, Any]) -> Grid:
    bg = _background(source, program["background"])
    fill = int(program["fill_color"])
    orientation = str(program["orientation"])
    height, width = _shape(source)
    result = [row[:] for row in source]
    if orientation == "row":
        for row in range(height):
            if fill not in source[row]:
                continue
            seeds = {color for color in source[row] if color not in {bg, fill}}
            if len(seeds) != 1:
                raise _Undefined("row material lacks one seed color")
            seed = next(iter(seeds))
            for column in range(width):
                if source[row][column] == fill:
                    result[row][column] = seed
    elif orientation == "column":
        for column in range(width):
            values = [source[row][column] for row in range(height)]
            if fill not in values:
                continue
            seeds = {color for color in values if color not in {bg, fill}}
            if len(seeds) != 1:
                raise _Undefined("column material lacks one seed color")
            seed = next(iter(seeds))
            for row in range(height):
                if source[row][column] == fill:
                    result[row][column] = seed
    else:
        raise _Undefined("unknown seed-recolor orientation")
    return result


def _diagonal_block_rays(source: Grid, program: Mapping[str, Any]) -> Grid:
    bg = _background(source, program["background"])
    directions = {int(color): str(direction) for color, direction in program["directions"]}
    offsets = {"nw": (-1, -1), "ne": (-1, 1), "sw": (1, -1), "se": (1, 1)}
    if any(direction not in offsets for direction in directions.values()):
        raise _Undefined("invalid diagonal direction")
    height, width = _shape(source)
    present = {cell for row in source for cell in row if cell != bg}
    if present != set(directions):
        raise _Undefined("diagonal direction table does not match colors")
    result = [row[:] for row in source]
    for color in sorted(present):
        points = [(r, c) for r in range(height) for c in range(width) if source[r][c] == color]
        rows = sorted({r for r, _ in points})
        columns = sorted({c for _, c in points})
        if len(rows) != 2 or len(columns) != 2 or set(points) != {
            (r, c) for r in rows for c in columns
        }:
            raise _Undefined("ray seed must be a solid two-by-two block")
        direction = directions[color]
        dr, dc = offsets[direction]
        start_row = min(rows) if dr < 0 else max(rows)
        start_column = min(columns) if dc < 0 else max(columns)
        row, column = start_row + dr, start_column + dc
        while 0 <= row < height and 0 <= column < width:
            if source[row][column] != bg:
                raise _Undefined("diagonal ray hits another block")
            result[row][column] = color
            row += dr
            column += dc
    return result


def _open_box_marker_fill(source: Grid, program: Mapping[str, Any]) -> Grid:
    bg = _background(source, program["background"])
    frame = int(program["frame_color"])
    height, width = _shape(source)
    result = [row[:] for row in source]
    components = _component_cells(source, frame, 4)
    if not components:
        raise _Undefined("no open boxes")
    for component in components:
        top, bottom = min(r for r, _ in component), max(r for r, _ in component)
        left, right = min(c for _, c in component), max(c for _, c in component)
        if bottom - top < 2 or right - left < 2:
            raise _Undefined("box too small")
        markers = {
            source[row][column]
            for row in range(top + 1, bottom)
            for column in range(left + 1, right)
            if source[row][column] not in {bg, frame}
        }
        if len(markers) != 1:
            raise _Undefined("box interior lacks one marker")
        marker = next(iter(markers))
        sides = {
            "top": [(top, c) for c in range(left, right + 1)],
            "bottom": [(bottom, c) for c in range(left, right + 1)],
            "left": [(r, left) for r in range(top, bottom + 1)],
            "right": [(r, right) for r in range(top, bottom + 1)],
        }
        open_sides = [
            name
            for name, cells in sides.items()
            if any(source[row][column] == bg for row, column in cells[1:-1])
        ]
        if len(open_sides) != 1:
            raise _Undefined("box must have one open side")
        side = open_sides[0]
        for row, column in sides[side]:
            if result[row][column] == bg:
                result[row][column] = marker
        for row in range(top + 1, bottom):
            for column in range(left + 1, right):
                if result[row][column] == bg:
                    result[row][column] = marker
        if side == "top":
            outside = [(top - 1, c) for c in range(left, right + 1)]
        elif side == "bottom":
            outside = [(bottom + 1, c) for c in range(left, right + 1)]
        elif side == "left":
            outside = [(r, left - 1) for r in range(top, bottom + 1)]
        else:
            outside = [(r, right + 1) for r in range(top, bottom + 1)]
        for row, column in outside:
            if 0 <= row < height and 0 <= column < width and result[row][column] == bg:
                result[row][column] = marker
    return result


def _boundary_signal_bounce(source: Grid, program: Mapping[str, Any]) -> Grid:
    bg = _background(source, program["background"])
    height, width = _shape(source)
    edges = []
    if len(set(source[0])) == 1 and source[0][0] != bg:
        edges.append(("top", source[0][0]))
    if len(set(source[-1])) == 1 and source[-1][0] != bg:
        edges.append(("bottom", source[-1][0]))
    if len({source[row][0] for row in range(height)}) == 1 and source[0][0] != bg:
        edges.append(("left", source[0][0]))
    if len({source[row][-1] for row in range(height)}) == 1 and source[0][-1] != bg:
        edges.append(("right", source[0][-1]))
    # Corner intersections can make the perpendicular edge superficially
    # uniform only on a one-cell grid, which sanitization excludes here.
    if len(edges) != 1:
        raise _Undefined("one signal boundary is required")
    side, boundary = edges[0]
    other_colors = {
        cell for row in source for cell in row if cell not in {bg, boundary}
    }
    if len(other_colors) != 1:
        raise _Undefined("one signal color is required")
    signal = next(iter(other_colors))
    result = [row[:] for row in source]

    if side in {"left", "right"}:
        depth = width
        lanes = height

        def point(lane: int, inward: int) -> tuple[int, int]:
            return (lane, inward if side == "left" else width - 1 - inward)

    else:
        depth = height
        lanes = width

        def point(lane: int, inward: int) -> tuple[int, int]:
            return (inward if side == "top" else height - 1 - inward, lane)

    if depth < 4:
        raise _Undefined("signal grid too shallow")
    for lane in range(lanes):
        first = point(lane, 1)
        second = point(lane, 2)
        if source[first[0]][first[1]] != signal:
            continue
        if source[second[0]][second[1]] == signal:
            result[first[0]][first[1]] = bg
            result[second[0]][second[1]] = bg
            for opposite_depth in (0, 1):
                rr, cc = point(lane, depth - 1 - opposite_depth)
                result[rr][cc] = boundary
        elif source[second[0]][second[1]] == bg:
            result[second[0]][second[1]] = signal
        else:
            raise _Undefined("signal meets an obstruction")
    return result


def _open_frame_beam_fill(source: Grid, program: Mapping[str, Any]) -> Grid:
    bg = _background(source, program["background"])
    frame = int(program["frame_color"])
    fill = int(program["fill_color"])
    height, width = _shape(source)
    result = [row[:] for row in source]
    components = _component_cells(source, frame, 4)
    if not components:
        raise _Undefined("no frames")
    for component in components:
        top, bottom = min(r for r, _ in component), max(r for r, _ in component)
        left, right = min(c for _, c in component), max(c for _, c in component)
        if bottom - top < 2 or right - left < 2:
            raise _Undefined("frame is too small")
        sides = {
            "top": [(top, c) for c in range(left + 1, right)],
            "bottom": [(bottom, c) for c in range(left + 1, right)],
            "left": [(r, left) for r in range(top + 1, bottom)],
            "right": [(r, right) for r in range(top + 1, bottom)],
        }
        gaps = {
            name: [(r, c) for r, c in cells if source[r][c] == bg]
            for name, cells in sides.items()
        }
        open_sides = [name for name, cells in gaps.items() if cells]
        if len(open_sides) != 1:
            raise _Undefined("frame does not have exactly one open side")
        side = open_sides[0]
        # All non-open border positions must be genuine frame cells.
        if any(
            source[r][c] != frame
            for name, cells in sides.items()
            if name != side
            for r, c in cells
        ):
            raise _Undefined("other frame side is incomplete")
        for row in range(top + 1, bottom):
            for column in range(left + 1, right):
                if source[row][column] == bg:
                    result[row][column] = fill
        for row, column in gaps[side]:
            result[row][column] = fill
            if side == "top":
                ray = ((rr, column) for rr in range(top - 1, -1, -1))
            elif side == "bottom":
                ray = ((rr, column) for rr in range(bottom + 1, height))
            elif side == "left":
                ray = ((row, cc) for cc in range(left - 1, -1, -1))
            else:
                ray = ((row, cc) for cc in range(right + 1, width))
            for rr, cc in ray:
                if result[rr][cc] != bg:
                    raise _Undefined("beam crosses another object")
                result[rr][cc] = fill
    return result


def _open_box_lateral_beam(source: Grid, program: Mapping[str, Any]) -> Grid:
    bg = _background(source, program["background"])
    frame = int(program["frame_color"])
    fill = int(program["fill_color"])
    height, width = _shape(source)
    result = [row[:] for row in source]
    components = _component_cells(source, frame, 4)
    if not components:
        raise _Undefined("no lateral-beam boxes")
    for component in components:
        top, bottom = min(r for r, _ in component), max(r for r, _ in component)
        left, right = min(c for _, c in component), max(c for _, c in component)
        if top == 0 or bottom - top < 2 or right - left < 2:
            raise _Undefined("lateral-beam box has invalid bounds")
        top_gaps = [column for column in range(left + 1, right) if source[top][column] == bg]
        if len(top_gaps) != 1:
            raise _Undefined("one top opening required")
        gap = top_gaps[0]
        if any(source[bottom][column] != frame for column in range(left, right + 1)):
            raise _Undefined("bottom side incomplete")
        if any(source[row][left] != frame or source[row][right] != frame for row in range(top, bottom + 1)):
            raise _Undefined("vertical sides incomplete")
        for row in range(top + 1, bottom):
            for column in range(left + 1, right):
                if source[row][column] == bg:
                    result[row][column] = fill
        result[top][gap] = fill
        outside_row = top - 1
        middle = (left + right) / 2
        columns = range(gap, width) if gap < middle else range(0, gap + 1)
        for column in columns:
            if result[outside_row][column] != bg:
                raise _Undefined("lateral beam crosses another object")
            result[outside_row][column] = fill
    return result


def _nested_tile_state_denoise(source: Grid, program: Mapping[str, Any]) -> Grid:
    separator = int(program["separator_color"])
    noise = int(program["noise_color"])
    height, width = _shape(source)
    if height != width:
        raise _Undefined("nested tile grid must be square")
    sizes = [size for size in range(2, 8) if size * size + size - 1 == height]
    if len(sizes) != 1:
        raise _Undefined("grid side does not encode one tile size")
    size = sizes[0]
    tiles: list[Grid] = []
    for tile_row in range(size):
        top = tile_row * (size + 1)
        for tile_column in range(size):
            left = tile_column * (size + 1)
            tiles.append([row[left : left + size] for row in source[top : top + size]])
    material = sorted(
        {
            color
            for tile in tiles
            for row in tile
            for color in row
            if color not in {separator, noise}
        }
    )
    if len(material) != 2:
        raise _Undefined("nested states require two material colors")
    hypotheses: list[tuple[int, int, int, Grid]] = []
    for candidate_primary in material:
        candidate_secondary = next(color for color in material if color != candidate_primary)
        candidate_template: Grid = []
        for row in range(size):
            output_row: list[int] = []
            for column in range(size):
                values = [tile[row][column] for tile in tiles if tile[row][column] != noise]
                if not values:
                    raise _Undefined("noise obscures a whole template position")
                counts = Counter(values)
                maximum = max(counts.values())
                tied = {color for color, count in counts.items() if count == maximum}
                output_row.append(
                    candidate_primary if candidate_primary in tied else min(tied)
                )
            candidate_template.append(output_row)
        template_counts = Counter(cell for row in candidate_template for cell in row)
        if template_counts[candidate_primary] <= template_counts[candidate_secondary]:
            continue
        reconstruction_error = 0
        for tile in tiles:
            distance_template = 0
            distance_solid = 0
            for row in range(size):
                for column in range(size):
                    value = tile[row][column]
                    if value == noise:
                        continue
                    distance_template += int(value != candidate_template[row][column])
                    distance_solid += int(value != candidate_secondary)
            reconstruction_error += min(distance_template, distance_solid)
        hypotheses.append(
            (
                reconstruction_error,
                -template_counts[candidate_primary],
                candidate_primary,
                candidate_template,
            )
        )
    if not hypotheses:
        raise _Undefined("no binary-state template")
    hypotheses.sort(key=lambda item: (item[0], item[1], item[2]))
    if len(hypotheses) > 1 and hypotheses[0][:2] == hypotheses[1][:2]:
        raise _Undefined("binary-state template is ambiguous")
    _, _, primary, template = hypotheses[0]
    secondary = next(color for color in material if color != primary)
    result = [[separator for _ in range(width)] for _ in range(height)]
    for index, tile in enumerate(tiles):
        distance_template = 0
        distance_solid = 0
        observed = 0
        for row in range(size):
            for column in range(size):
                value = tile[row][column]
                if value == noise:
                    continue
                if value not in material:
                    raise _Undefined("separator leaked into a tile")
                observed += 1
                distance_template += int(value != template[row][column])
                distance_solid += int(value != secondary)
        if observed == 0 or distance_template == distance_solid:
            raise _Undefined("tile state is ambiguous")
        rendered = template if distance_solid < distance_template else [
            [primary for _ in range(size)] for _ in range(size)
        ]
        tile_row, tile_column = divmod(index, size)
        top, left = tile_row * (size + 1), tile_column * (size + 1)
        for row in range(size):
            result[top + row][left : left + size] = rendered[row][:]
    return result


def _grid_three_diagonal_fill(source: Grid, program: Mapping[str, Any]) -> Grid:
    background = int(program["background_color"])
    separator = int(program["separator_color"])
    colors = [int(color) for color in program["fill_colors"]]
    if len(colors) != 3 or len(set(colors)) != 3:
        raise _Undefined("three distinct diagonal colors required")
    height, width = _shape(source)
    separator_rows = [row for row in range(height) if all(value == separator for value in source[row])]
    separator_columns = [
        column for column in range(width) if all(source[row][column] == separator for row in range(height))
    ]

    def bands(length: int, separators: Sequence[int]) -> list[tuple[int, int]]:
        result: list[tuple[int, int]] = []
        start = 0
        for divider in list(separators) + [length]:
            if start < divider:
                result.append((start, divider))
            start = divider + 1
        return result

    row_bands = bands(height, separator_rows)
    column_bands = bands(width, separator_columns)
    if len(row_bands) < 3 or len(column_bands) < 3 or len(row_bands) % 2 == 0 or len(column_bands) % 2 == 0:
        raise _Undefined("odd grids with at least three bands required")
    selected = [
        (row_bands[0], column_bands[0], colors[0]),
        (row_bands[len(row_bands) // 2], column_bands[len(column_bands) // 2], colors[1]),
        (row_bands[-1], column_bands[-1], colors[2]),
    ]
    result = [row[:] for row in source]
    for (top, bottom), (left, right), color in selected:
        for row in range(top, bottom):
            for column in range(left, right):
                if source[row][column] != background:
                    raise _Undefined("selected grid panel is not empty")
                result[row][column] = color
    return result


def _barrier_region_normalization(source: Grid, program: Mapping[str, Any]) -> Grid:
    background = int(program["background_color"])
    barrier = int(program["barrier_color"])
    height, width = _shape(source)
    payloads = {
        cell for row in source for cell in row if cell not in {background, barrier}
    }
    if len(payloads) != 1:
        raise _Undefined("one payload color required")
    payload = next(iter(payloads))
    if source[0][-1] == barrier or source[-1][0] == barrier:
        raise _Undefined("barrier occupies a reference corner")
    remaining = {
        (row, column)
        for row in range(height)
        for column in range(width)
        if source[row][column] != barrier
    }
    components: list[set[tuple[int, int]]] = []
    while remaining:
        seed = min(remaining)
        remaining.remove(seed)
        component = {seed}
        queue = deque([seed])
        while queue:
            row, column = queue.popleft()
            for dr, dc in ((-1, 0), (0, -1), (0, 1), (1, 0)):
                point = row + dr, column + dc
                if point in remaining:
                    remaining.remove(point)
                    component.add(point)
                    queue.append(point)
        components.append(component)
    upper = next((component for component in components if (0, width - 1) in component), None)
    lower = next((component for component in components if (height - 1, 0) in component), None)
    if upper is None or lower is None or upper is lower or len(components) != 2:
        raise _Undefined("barrier does not split corner regions exactly")
    result = [row[:] for row in source]
    for row, column in upper:
        result[row][column] = background
    for row, column in lower:
        result[row][column] = payload
    return result


def _frame_interior_palette_swap(source: Grid, program: Mapping[str, Any]) -> Grid:
    frame = int(program["frame_color"])
    height, width = _shape(source)
    points = [(r, c) for r in range(height) for c in range(width) if source[r][c] == frame]
    if not points:
        raise _Undefined("missing swap frame")
    top, bottom = min(r for r, _ in points), max(r for r, _ in points)
    left, right = min(c for _, c in points), max(c for _, c in points)
    border = {
        (r, c)
        for r in range(top, bottom + 1)
        for c in range(left, right + 1)
        if r in {top, bottom} or c in {left, right}
    }
    if any(source[r][c] != frame for r, c in border):
        raise _Undefined("swap frame is incomplete")
    interior_values = {
        source[r][c]
        for r in range(top + 1, bottom)
        for c in range(left + 1, right)
    }
    # Zero is a transparent/background value inside all members of this
    # schema; exactly two material colors exchange roles around it.
    materials = sorted(interior_values - {0, frame})
    if len(materials) != 2:
        raise _Undefined("swap frame does not contain two materials")
    first, second = materials
    result = [row[:] for row in source]
    for row in range(top + 1, bottom):
        for column in range(left + 1, right):
            if source[row][column] == first:
                result[row][column] = second
            elif source[row][column] == second:
                result[row][column] = first
    return result


def _nested_square_pulse_expand(source: Grid, program: Mapping[str, Any]) -> Grid:
    bg = _background(source, program["background"])
    height, width = _shape(source)
    foreground = {
        (row, column)
        for row in range(height)
        for column in range(width)
        if source[row][column] != bg
    }
    components: list[set[tuple[int, int]]] = []
    while foreground:
        seed = min(foreground)
        foreground.remove(seed)
        component = {seed}
        queue = deque([seed])
        while queue:
            row, column = queue.popleft()
            for dr, dc in ((-1, 0), (0, -1), (0, 1), (1, 0)):
                point = row + dr, column + dc
                if point in foreground:
                    foreground.remove(point)
                    component.add(point)
                    queue.append(point)
        components.append(component)
    if not components:
        raise _Undefined("no nested squares")
    result = [[bg for _ in range(width)] for _ in range(height)]
    for component in components:
        top, bottom = min(r for r, _ in component), max(r for r, _ in component)
        left, right = min(c for _, c in component), max(c for _, c in component)
        if bottom - top != right - left or bottom - top < 2:
            raise _Undefined("nested object is not square")
        side = bottom - top + 1
        inner_size = side - 2
        outer_values = {
            source[row][column]
            for row in range(top, bottom + 1)
            for column in range(left, right + 1)
            if row in {top, bottom} or column in {left, right}
        }
        inner_values = {
            source[row][column]
            for row in range(top + 1, bottom)
            for column in range(left + 1, right)
        }
        if len(outer_values) != 1 or len(inner_values) != 1:
            raise _Undefined("nested square layers are not uniform")
        outer = next(iter(outer_values))
        inner = next(iter(inner_values))
        if outer in {bg, inner} or inner == bg:
            raise _Undefined("nested square colors are degenerate")
        expanded_side = 3 * inner_size + 2
        expanded_top = top - inner_size
        expanded_left = left - inner_size
        if (
            expanded_top < 0
            or expanded_left < 0
            or expanded_top + expanded_side > height
            or expanded_left + expanded_side > width
        ):
            raise _Undefined("expanded nested square leaves canvas")
        patch = [[bg for _ in range(expanded_side)] for _ in range(expanded_side)]
        core_start = inner_size
        core_end = core_start + inner_size + 1
        for row in range(expanded_side):
            for column in range(expanded_side):
                in_vertical_arm = core_start <= column <= core_end
                in_horizontal_arm = core_start <= row <= core_end
                if in_vertical_arm or in_horizontal_arm:
                    patch[row][column] = outer
        # Inner color forms a one-cell frame around a restored outer-color
        # center of the original inner dimensions.
        for row in range(core_start, core_end + 1):
            for column in range(core_start, core_end + 1):
                patch[row][column] = inner
        for row in range(core_start + 1, core_end):
            for column in range(core_start + 1, core_end):
                patch[row][column] = outer
        for row in range(expanded_side):
            for column in range(expanded_side):
                color = patch[row][column]
                rr, cc = expanded_top + row, expanded_left + column
                if color != bg:
                    if result[rr][cc] not in {bg, color}:
                        raise _Undefined("expanded pulses conflict")
                    result[rr][cc] = color
    return result


def _fit_marker_topology_to_frame(source: Grid, program: Mapping[str, Any]) -> Grid:
    bg = _background(source, program["background"])
    frame = int(program["frame_color"])
    height, width = _shape(source)
    frame_points = [(r, c) for r in range(height) for c in range(width) if source[r][c] == frame]
    if not frame_points:
        raise _Undefined("missing topology frame")
    top, bottom = min(r for r, _ in frame_points), max(r for r, _ in frame_points)
    left, right = min(c for _, c in frame_points), max(c for _, c in frame_points)
    border = {
        (r, c)
        for r in range(top, bottom + 1)
        for c in range(left, right + 1)
        if r in {top, bottom} or c in {left, right}
    }
    if any(source[r][c] != frame for r, c in border):
        raise _Undefined("topology frame is incomplete")
    interior_height, interior_width = bottom - top - 1, right - left - 1
    if interior_height <= 0 or interior_width <= 0:
        raise _Undefined("topology frame has no interior")
    marker_points = [
        (r, c, source[r][c])
        for r in range(height)
        for c in range(width)
        if source[r][c] not in {bg, frame}
    ]
    marker_colors = {value for _, _, value in marker_points}
    if len(marker_colors) != 1 or not marker_points:
        raise _Undefined("one external marker object required")
    marker_color = next(iter(marker_colors))
    if any(top < r < bottom and left < c < right for r, c, _ in marker_points):
        raise _Undefined("marker is already inside frame")
    marker_top, marker_bottom = min(r for r, _, _ in marker_points), max(r for r, _, _ in marker_points)
    marker_left, marker_right = min(c for _, c, _ in marker_points), max(c for _, c, _ in marker_points)
    marker_set = {(r - marker_top, c - marker_left) for r, c, _ in marker_points}
    marker_height = marker_bottom - marker_top + 1
    marker_width = marker_right - marker_left + 1
    # Require one connected marker object.
    if len(_component_cells(source, marker_color, 4)) != 1:
        raise _Undefined("marker is disconnected")
    result = [row[:] for row in source]
    for row, column, _ in marker_points:
        result[row][column] = bg
    if len(marker_set) == marker_height * marker_width:
        for row in range(top + 1, bottom):
            for column in range(left + 1, right):
                result[row][column] = marker_color
        return result

    def map_row(row: int) -> int:
        if marker_height == 1:
            return (interior_height - 1) // 2
        return round(row * (interior_height - 1) / (marker_height - 1))

    def map_column(column: int) -> int:
        if marker_width == 1:
            return (interior_width - 1) // 2
        return round(column * (interior_width - 1) / (marker_width - 1))

    mapped = {
        point: (map_row(point[0]), map_column(point[1])) for point in marker_set
    }
    for point, (row, column) in mapped.items():
        result[top + 1 + row][left + 1 + column] = marker_color
        for dr, dc in ((0, 1), (1, 0)):
            neighbor = point[0] + dr, point[1] + dc
            if neighbor not in mapped:
                continue
            rr, cc = mapped[neighbor]
            if row == rr:
                for value in range(min(column, cc), max(column, cc) + 1):
                    result[top + 1 + row][left + 1 + value] = marker_color
            elif column == cc:
                for value in range(min(row, rr), max(row, rr) + 1):
                    result[top + 1 + value][left + 1 + column] = marker_color
            else:
                raise _Undefined("axis edge became diagonal")
    return result


def _pack_objects_by_area(source: Grid, program: Mapping[str, Any]) -> Grid:
    bg = _background(source, program["background"])
    height, width = _shape(source)
    remaining = {
        (row, column)
        for row in range(height)
        for column in range(width)
        if source[row][column] != bg
    }
    objects: list[tuple[int, int, int, int, int, list[tuple[int, int, int]]]] = []
    while remaining:
        seed = min(remaining)
        seed_color = source[seed[0]][seed[1]]
        remaining.remove(seed)
        queue = deque([seed])
        points = [seed]
        while queue:
            row, column = queue.popleft()
            for dr, dc in ((-1, 0), (0, -1), (0, 1), (1, 0)):
                point = row + dr, column + dc
                if point in remaining and source[point[0]][point[1]] == seed_color:
                    remaining.remove(point)
                    queue.append(point)
                    points.append(point)
        top, bottom = min(r for r, _ in points), max(r for r, _ in points)
        left, right = min(c for _, c in points), max(c for _, c in points)
        if top == 0 and left == 0 and bottom == height - 1 and right == width - 1:
            continue
        normalized = [(r - top, c - left, seed_color) for r, c in points]
        objects.append((len(points), bottom - top + 1, right - left + 1, top, left, normalized))
    if not objects:
        raise _Undefined("no packable objects")
    objects.sort(key=lambda item: (item[0], item[1] * item[2], item[3], item[4], item[5]))
    if sum(item[2] for item in objects) > width:
        raise _Undefined("objects do not fit packed row")
    result = [[bg for _ in range(width)] for _ in range(height)]
    offset = 0
    for _, object_height, object_width, _, _, points in objects:
        top = height - object_height
        for row, column, color in points:
            result[top + row][offset + column] = color
        offset += object_width
    return result


def _counterrotate_bar_attributes(source: Grid, program: Mapping[str, Any]) -> Grid:
    bg = _background(source, program["background"])
    height, width = _shape(source)
    bars: list[tuple[int, int, int]] = []
    for column in range(width):
        points = [(row, source[row][column]) for row in range(height) if source[row][column] != bg]
        if not points:
            continue
        colors = {color for _, color in points}
        rows = [row for row, _ in points]
        if len(colors) != 1 or rows != list(range(height - len(rows), height)):
            raise _Undefined("foreground is not a set of bottom-aligned bars")
        bars.append((column, len(rows), next(iter(colors))))
    if len(bars) < 3:
        raise _Undefined("counterrotation requires at least three bars")
    result = [[bg for _ in range(width)] for _ in range(height)]
    count = len(bars)
    for index, (column, _, _) in enumerate(bars):
        length = bars[(index + 1) % count][1]
        color = bars[(index - 1) % count][2]
        for row in range(height - length, height):
            result[row][column] = color
    return result


def execute_program(program: Mapping[str, Any], value: Any) -> Grid:
    """Execute a synthesized program on one grid without learned state."""

    source = _grid(value, 60)
    if source is None or not isinstance(program, Mapping):
        raise ValueError("invalid program input")
    operator = program.get("operator")
    if operator == "periodic_residue":
        rows = _resolve_period(program["row_period"], source, "row")
        columns = _resolve_period(program["column_period"], source, "column")
        template = _residue_template(
            source,
            rows,
            columns,
            str(program["reducer"]),
            program["background"],
        )
        out_height, out_width = _resolve_shape(source, program["shape"])
        row_offset = int(program.get("row_offset", 0))
        column_offset = int(program.get("column_offset", 0))
        return [
            [template[(row + row_offset) % rows][(column + column_offset) % columns] for column in range(out_width)]
            for row in range(out_height)
        ]
    if operator in {"tile_region", "reflect_region", "stamp_region"}:
        motif = _region(source, program["region"])
        motif_height, motif_width = _shape(motif)
        out_height, out_width = _resolve_shape(source, program["shape"])
        row_offset = int(program.get("row_offset", 0))
        column_offset = int(program.get("column_offset", 0))
        if operator == "tile_region":
            return [
                [motif[(row + row_offset) % motif_height][(column + column_offset) % motif_width] for column in range(out_width)]
                for row in range(out_height)
            ]
        if operator == "reflect_region":
            duplicate = bool(program.get("duplicate_edge"))
            return [
                [
                    motif[_bounce(row + row_offset, motif_height, duplicate)][
                        _bounce(column + column_offset, motif_width, duplicate)
                    ]
                    for column in range(out_width)
                ]
                for row in range(out_height)
            ]
        bg = _background(source, program["background"])
        result = [[bg for _ in range(out_width)] for _ in range(out_height)]
        row_step = motif_height + int(program["row_gap"])
        column_step = motif_width + int(program["column_gap"])
        transparent = bool(program.get("transparent_background"))
        motif_bg = _background(motif, program["background"])
        for top in range(row_offset, out_height, row_step):
            for left in range(column_offset, out_width, column_step):
                for row in range(motif_height):
                    for column in range(motif_width):
                        rr, cc = top + row, left + column
                        color = motif[row][column]
                        if 0 <= rr < out_height and 0 <= cc < out_width:
                            if not transparent or color != motif_bg:
                                result[rr][cc] = color
        return result
    if operator == "symmetry_completion":
        return _symmetry_complete(source, program)
    if operator == "mirror_expand":
        return _mirror_expand(source, program)
    if operator == "coordinate_cycle":
        out_height, out_width = _resolve_shape(source, program["shape"])
        period = int(program["period"])
        selectors = program["selectors"]
        if not isinstance(selectors, list) or len(selectors) != period:
            raise _Undefined("coordinate selector arity")
        colors = [_resolve_color(source, selector) for selector in selectors]
        return [
            [
                colors[
                    _coordinate_index(
                        str(program["coordinate"]),
                        row,
                        column,
                        out_height,
                        out_width,
                        period,
                    )
                ]
                for column in range(out_width)
            ]
            for row in range(out_height)
        ]
    if operator == "dynamic_coordinate_cycle":
        motif = _trim_uniform_bottom_right(source)
        order_kind = str(program["order"])
        if order_kind == "first_row":
            sequence = _first_order([motif[0]])
        elif order_kind == "first_column":
            sequence = _first_order([[row[0]] for row in motif])
        elif order_kind == "flat_first":
            sequence = _first_order(motif)
        elif order_kind == "sorted_palette":
            sequence = _palette(motif)
        elif order_kind == "frequency_descending":
            sequence = _frequency_order(motif, True)
        else:
            raise _Undefined("unknown dynamic cycle order")
        if not sequence:
            raise _Undefined("empty dynamic cycle")
        out_height, out_width = _resolve_shape(source, program["shape"])
        row_step = int(program["row_step"])
        column_step = int(program["column_step"])
        phase = int(program["phase"])
        return [
            [
                sequence[(phase + row * row_step + column * column_step) % len(sequence)]
                for column in range(out_width)
            ]
            for row in range(out_height)
        ]
    if operator == "dynamic_motif_color_cycle":
        trimmed = _trim_uniform_bottom_right(source)
        motif = _minimal_exact_tile(trimmed)
        order_kind = str(program["order"])
        if order_kind == "first_row":
            sequence = _first_order([trimmed[0]])
        elif order_kind == "first_column":
            sequence = _first_order([[row[0]] for row in trimmed])
        elif order_kind == "flat_first":
            sequence = _first_order(trimmed)
        elif order_kind == "sorted_palette":
            sequence = _palette(trimmed)
        else:
            raise _Undefined("unknown motif color order")
        if not sequence or any(color not in sequence for row in motif for color in row):
            raise _Undefined("motif colors not covered by cycle")
        shift = int(program["shift"])
        mapping = {
            color: sequence[(index + shift) % len(sequence)]
            for index, color in enumerate(sequence)
        }
        out_height, out_width = _resolve_shape(source, program["shape"])
        return [
            [mapping[motif[row % len(motif)][column % len(motif[0])]] for column in range(out_width)]
            for row in range(out_height)
        ]
    if operator == "ring_clue_completion":
        return _ring_clue_fill(source, program["background"])
    if operator == "singleton_cross":
        return _singleton_cross(source, program["background"])
    if operator == "alternating_rays":
        return _alternating_rays(source, program)
    if operator == "centered_inventory_line":
        return _centered_inventory_line(source, program)
    if operator == "left_edge_diagonal_frame":
        return _left_edge_diagonal_frame(source, program)
    if operator == "component_seed_flood":
        return _component_seed_flood(source, program)
    if operator == "largest_rectangle_fill":
        return _rectangle_fill(source, program)
    if operator == "vertical_bar_fan":
        return _vertical_bar_fan(source, program)
    if operator == "nearest_parallel_borders":
        return _nearest_parallel_borders(source, program)
    if operator == "singleton_focus":
        return _singleton_focus(source, program)
    if operator == "marker_line_projection":
        return _marker_line_projection(source, program)
    if operator == "bottom_seed_serpentine":
        return _bottom_seed_serpentine(source, program)
    if operator == "frame_marker_quadrants":
        return _frame_marker_quadrants(source, program)
    if operator == "row_or_column_seed_recolor":
        return _row_or_column_seed_recolor(source, program)
    if operator == "diagonal_block_rays":
        return _diagonal_block_rays(source, program)
    if operator == "open_box_marker_fill":
        return _open_box_marker_fill(source, program)
    if operator == "boundary_signal_bounce":
        return _boundary_signal_bounce(source, program)
    if operator == "open_frame_beam_fill":
        return _open_frame_beam_fill(source, program)
    if operator == "open_box_lateral_beam":
        return _open_box_lateral_beam(source, program)
    if operator == "nested_tile_state_denoise":
        return _nested_tile_state_denoise(source, program)
    if operator == "grid_three_diagonal_fill":
        return _grid_three_diagonal_fill(source, program)
    if operator == "barrier_region_normalization":
        return _barrier_region_normalization(source, program)
    if operator == "frame_interior_palette_swap":
        return _frame_interior_palette_swap(source, program)
    if operator == "nested_square_pulse_expand":
        return _nested_square_pulse_expand(source, program)
    if operator == "fit_marker_topology_to_frame":
        return _fit_marker_topology_to_frame(source, program)
    if operator == "pack_objects_by_area":
        return _pack_objects_by_area(source, program)
    if operator == "counterrotate_bar_attributes":
        return _counterrotate_bar_attributes(source, program)
    raise ValueError("unknown pattern-completion operator")


class _Collector:
    def __init__(self, train: list[Pair], tests: list[Grid], limits: Limits) -> None:
        self.train = train
        self.tests = tests
        self.limits = limits
        self.hypotheses = 0
        self.seen_programs: set[str] = set()
        self.candidates: list[dict[str, Any]] = []

    def add(self, family: str, program: dict[str, Any], complexity: int, evidence: dict[str, Any]) -> None:
        if self.hypotheses >= self.limits.max_hypotheses:
            return
        self.hypotheses += 1
        key = _canonical(program)
        if key in self.seen_programs:
            return
        self.seen_programs.add(key)
        try:
            replay = [execute_program(program, source) for source, _ in self.train]
            if any(prediction != target for prediction, (_, target) in zip(replay, self.train)):
                return
            predictions = [execute_program(program, source) for source in self.tests]
            if any(max(_shape(grid)) > self.limits.max_side for grid in predictions):
                return
        except (IndexError, KeyError, TypeError, ValueError, ZeroDivisionError):
            return
        changed = sum(
            sum(
                1
                for row in range(min(len(source), len(target)))
                for column in range(min(len(source[0]), len(target[0])))
                if source[row][column] != target[row][column]
            )
            + abs(len(source) * len(source[0]) - len(target) * len(target[0]))
            for source, target in self.train
        )
        record_evidence = {
            "all_demonstrations_exact": True,
            "demonstration_count": len(self.train),
            "changed_cell_support": changed,
            "demonstration_permutation_invariant": True,
            "mdl": {
                "description_length": int(complexity),
                "literal_color_cost": _literal_cost(program),
                "shape_rule_cost": _shape_cost(program.get("shape", {"kind": "same"})),
            },
        }
        record_evidence.update(evidence)
        self.candidates.append(
            {
                "family": family,
                "program": program,
                "train_outputs": replay,
                "test_outputs": predictions,
                "complexity": int(max(0, complexity)),
                "evidence": record_evidence,
            }
        )


def _literal_cost(value: Any) -> int:
    if isinstance(value, Mapping):
        if value.get("kind") == "literal" and "color" in value:
            return 1
        return sum(_literal_cost(item) for item in value.values())
    if isinstance(value, list):
        return sum(_literal_cost(item) for item in value)
    return 0


def _common_changed_colors(train: Sequence[Pair], *, before: bool) -> set[int]:
    sets: list[set[int]] = []
    for source, target in train:
        if _shape(source) != _shape(target):
            return set()
        colors = {
            (source[row][column] if before else target[row][column])
            for row in range(len(source))
            for column in range(len(source[0]))
            if source[row][column] != target[row][column]
        }
        if not colors:
            return set()
        sets.append(colors)
    return set.intersection(*sets) if sets else set()


def _generate_targeted_patterns(collector: _Collector) -> None:
    backgrounds = (({"kind": "modal"}, 0), ({"kind": "literal", "color": 0}, 1))

    for background, cost in backgrounds:
        collector.add(
            "pattern.ring_clue_completion",
            {"operator": "ring_clue_completion", "background": background},
            3 + cost,
            {"regularity": "one_positional_clue_per_concentric_ring"},
        )
        collector.add(
            "pattern.singleton_cross",
            {"operator": "singleton_cross", "background": background},
            4 + cost,
            {"regularity": "singleton_marker_row_column_cross", "preserves_obstacles": True},
        )
        for orientation in ("horizontal", "vertical"):
            collector.add(
                "pattern.centered_inventory_line",
                {
                    "operator": "centered_inventory_line",
                    "background": background,
                    "orientation": orientation,
                },
                4 + cost,
                {"regularity": "foreground_inventory_conservation", "orientation": orientation},
            )

    changed_after = _common_changed_colors(collector.train, before=False)
    changed_before = _common_changed_colors(collector.train, before=True)

    # Rays alternate their own seed color with one demonstration-stable color.
    for alternating_color in sorted(changed_after):
        for direction in ("right", "left", "down", "up"):
            for background, bg_cost in backgrounds:
                collector.add(
                    "pattern.alternating_rays",
                    {
                        "operator": "alternating_rays",
                        "background": background,
                        "alternating_color": alternating_color,
                        "direction": direction,
                    },
                    6 + bg_cost,
                    {"regularity": "seed_literal_alternating_ray", "direction": direction},
                )

    # A complete seed edge plus two stable construction colors describes the
    # diagonal/baseline pattern without encoding a target raster.
    stable_construct_colors = sorted(changed_after)
    for diagonal_color in stable_construct_colors:
        for base_color in stable_construct_colors:
            if diagonal_color == base_color:
                continue
            collector.add(
                "pattern.edge_diagonal_frame",
                {
                    "operator": "left_edge_diagonal_frame",
                    "background": {"kind": "literal", "color": 0},
                    "diagonal_color": diagonal_color,
                    "base_color": base_color,
                },
                7,
                {"regularity": "seed_edge_opposite_diagonal_and_base"},
            )

    # Recolor a repeated neutral material by the one colored seed touching
    # each of its components.
    for fill_color in sorted(changed_before):
        for connectivity in (4, 8):
            for adjacency in (4, 8):
                for background, bg_cost in backgrounds:
                    collector.add(
                        "pattern.component_seed_flood",
                        {
                            "operator": "component_seed_flood",
                            "background": background,
                            "fill_color": fill_color,
                            "connectivity": connectivity,
                            "adjacency": adjacency,
                        },
                        6 + bg_cost + int(connectivity == 8) + int(adjacency == 8),
                        {
                            "regularity": "component_recolored_by_unique_adjacent_seed",
                            "connectivity": connectivity,
                            "adjacency": adjacency,
                        },
                    )

    for fill_color in stable_construct_colors:
        for background, bg_cost in backgrounds:
            collector.add(
                "pattern.largest_rectangle_fill",
                {
                    "operator": "largest_rectangle_fill",
                    "background": background,
                    "fill_color": fill_color,
                },
                6 + bg_cost,
                {"regularity": "unique_largest_two_dimensional_background_rectangle"},
            )

    # A top-anchored vertical bar generates linear two-sided height ramps.
    for left_color in stable_construct_colors:
        for right_color in stable_construct_colors:
            if left_color == right_color:
                continue
            collector.add(
                "pattern.vertical_bar_fan",
                {
                    "operator": "vertical_bar_fan",
                    "background": {"kind": "literal", "color": 0},
                    "left_color": left_color,
                    "right_color": right_color,
                },
                7,
                {"regularity": "top_bar_linear_height_fan", "slope": 2},
            )

    for tie_first in (True, False):
        collector.add(
            "pattern.nearest_parallel_borders",
            {
                "operator": "nearest_parallel_borders",
                "background": {"kind": "literal", "color": 0},
                "tie_first": tie_first,
            },
            4 + int(not tie_first),
            {"regularity": "marker_recolored_by_nearest_opposing_border"},
        )

    for ring_color in stable_construct_colors:
        collector.add(
            "pattern.singleton_focus",
            {
                "operator": "singleton_focus",
                "background": {"kind": "literal", "color": 0},
                "ring_color": ring_color,
            },
            5,
            {"regularity": "unique_singleton_retained_in_three_by_three_focus"},
        )

    # Marker colors recur at evaluation time in this schema.  Bound the
    # learned orientation table to keep literal enumeration honest and cheap.
    projection_colors = sorted(
        {
            color
            for source, _ in collector.train
            for row in source
            for color in row
            if color != 0
        }
    )
    if 0 < len(projection_colors) <= 5:
        for mask in range(1 << len(projection_colors)):
            horizontal = [
                color for index, color in enumerate(projection_colors) if mask & (1 << index)
            ]
            vertical = [color for color in projection_colors if color not in horizontal]
            for horizontal_priority in (True, False):
                collector.add(
                    "pattern.marker_line_projection",
                    {
                        "operator": "marker_line_projection",
                        "background": {"kind": "literal", "color": 0},
                        "horizontal_colors": horizontal,
                        "vertical_colors": vertical,
                        "horizontal_priority": horizontal_priority,
                    },
                    7 + len(projection_colors) + int(not horizontal_priority),
                    {
                        "regularity": "literal_marker_to_full_row_or_column",
                        "orientation_table_size": len(projection_colors),
                    },
                )

    for accent_color in stable_construct_colors:
        collector.add(
            "pattern.bottom_seed_serpentine",
            {
                "operator": "bottom_seed_serpentine",
                "background": {"kind": "literal", "color": 0},
                "accent_color": accent_color,
            },
            5,
            {"regularity": "bottom_seed_alternating_columns_with_edge_turns"},
        )

    for frame_color in range(1, 10):
        collector.add(
            "pattern.frame_marker_quadrants",
            {
                "operator": "frame_marker_quadrants",
                "background": {"kind": "literal", "color": 0},
                "frame_color": frame_color,
            },
            5,
            {"regularity": "external_markers_assign_opposite_frame_quadrants"},
        )

    for fill_color in sorted(changed_before):
        for orientation in ("row", "column"):
            for background, bg_cost in backgrounds:
                collector.add(
                    "pattern.seeded_material_recolor",
                    {
                        "operator": "row_or_column_seed_recolor",
                        "background": background,
                        "fill_color": fill_color,
                        "orientation": orientation,
                    },
                    5 + bg_cost,
                    {
                        "regularity": "shared_axis_seed_recolors_neutral_material",
                        "orientation": orientation,
                    },
                )

    # Two-by-two symbol blocks emit color-preserving diagonal rays.  The tiny
    # orientation table is learned from demonstrations and capped at three
    # colors (at most 4^3 deterministic hypotheses).
    if 0 < len(projection_colors) <= 3:
        directions = ("nw", "ne", "sw", "se")
        products: list[list[str]] = [[]]
        for _ in projection_colors:
            products = [prefix + [direction] for prefix in products for direction in directions]
        for product in products:
            collector.add(
                "pattern.diagonal_block_rays",
                {
                    "operator": "diagonal_block_rays",
                    "background": {"kind": "literal", "color": 0},
                    "directions": [
                        [color, direction] for color, direction in zip(projection_colors, product)
                    ],
                },
                7 + 2 * len(projection_colors),
                {
                    "regularity": "two_by_two_blocks_emit_diagonal_corner_rays",
                    "orientation_table_size": len(projection_colors),
                },
            )

    for frame_color in range(1, 10):
        collector.add(
            "pattern.open_box_marker_fill",
            {
                "operator": "open_box_marker_fill",
                "background": {"kind": "literal", "color": 0},
                "frame_color": frame_color,
            },
            6,
            {"regularity": "open_box_interior_and_adjacent_strip_take_marker_color"},
        )

    collector.add(
        "pattern.boundary_signal_bounce",
        {"operator": "boundary_signal_bounce", "background": {"kind": "modal"}},
        5,
        {
            "regularity": "one_pulse_extends_two_pulse_bounces_to_opposite_edge",
            "orientation": "inferred_from_uniform_boundary",
        },
    )

    for fill_color in stable_construct_colors:
        for frame_color in range(1, 10):
            collector.add(
                "pattern.open_frame_beam_fill",
                {
                    "operator": "open_frame_beam_fill",
                    "background": {"kind": "modal"},
                    "frame_color": frame_color,
                    "fill_color": fill_color,
                },
                7,
                {"regularity": "one_gap_frame_fills_interior_and_projects_to_boundary"},
            )
            collector.add(
                "pattern.open_box_lateral_beam",
                {
                    "operator": "open_box_lateral_beam",
                    "background": {"kind": "literal", "color": 0},
                    "frame_color": frame_color,
                    "fill_color": fill_color,
                },
                7,
                {"regularity": "top_gap_box_fills_and_turns_toward_far_horizontal_edge"},
            )

    for noise_color in range(10):
        if noise_color == 0:
            continue
        collector.add(
            "pattern.nested_tile_state_denoise",
            {
                "operator": "nested_tile_state_denoise",
                "separator_color": 0,
                "noise_color": noise_color,
            },
            7,
            {
                "regularity": "consensus_template_then_binary_state_decrement",
                "noise_treatment": "ignored_per_template_coordinate",
            },
        )

    if len(stable_construct_colors) == 3:
        for first in stable_construct_colors:
            for second in stable_construct_colors:
                for third in stable_construct_colors:
                    if len({first, second, third}) != 3:
                        continue
                    for separator_color in range(1, 10):
                        collector.add(
                            "pattern.grid_three_diagonal_fill",
                            {
                                "operator": "grid_three_diagonal_fill",
                                "background_color": 0,
                                "separator_color": separator_color,
                                "fill_colors": [first, second, third],
                            },
                            8,
                            {"regularity": "first_middle_last_panels_on_odd_grid_diagonal"},
                        )

    for barrier_color in range(1, 10):
        collector.add(
            "pattern.barrier_region_normalization",
            {
                "operator": "barrier_region_normalization",
                "background_color": 0,
                "barrier_color": barrier_color,
            },
            5,
            {"regularity": "barrier_separates_cleared_upper_left_and_filled_lower_right"},
        )
        collector.add(
            "pattern.frame_interior_palette_swap",
            {"operator": "frame_interior_palette_swap", "frame_color": barrier_color},
            4,
            {"regularity": "complete_frame_swaps_two_interior_material_roles"},
        )
    collector.add(
        "pattern.nested_square_pulse_expand",
        {
            "operator": "nested_square_pulse_expand",
            "background": {"kind": "literal", "color": 0},
        },
        7,
        {"regularity": "nested_square_emits_size_scaled_cross_pulse"},
    )
    for frame_color in range(1, 10):
        collector.add(
            "pattern.fit_marker_topology_to_frame",
            {
                "operator": "fit_marker_topology_to_frame",
                "background": {"kind": "modal"},
                "frame_color": frame_color,
            },
            8,
            {"regularity": "external_marker_graph_stretched_into_hollow_frame"},
        )
    collector.add(
        "pattern.pack_objects_by_area",
        {"operator": "pack_objects_by_area", "background": {"kind": "modal"}},
        7,
        {"regularity": "discard_full_canvas_container_then_bottom_pack_by_area"},
    )
    collector.add(
        "pattern.counterrotate_bar_attributes",
        {"operator": "counterrotate_bar_attributes", "background": {"kind": "modal"}},
        6,
        {"regularity": "bar_lengths_and_colors_rotate_in_opposite_directions"},
    )


def _period_cost(value: Any, source_shapes: Sequence[tuple[int, int]], axis: str) -> int:
    if value in {"height", "width"}:
        return 3
    period = int(value)
    # A period which cannot repeat in any demonstration is a verbose copy, not
    # evidence of regularity, and receives a strong description penalty.
    dimension_index = 0 if axis == "row" else 1
    repeats = any(shape[dimension_index] > period for shape in source_shapes)
    return 1 + period + (0 if repeats else 8)


def _generate_periodic(collector: _Collector, shape_rules: Sequence[dict[str, Any]]) -> None:
    source_shapes = [_shape(source) for source, _ in collector.train]
    minimum_height = min(height for height, _ in source_shapes)
    minimum_width = min(width for _, width in source_shapes)
    row_periods: list[Any] = list(range(1, min(collector.limits.max_period, minimum_height) + 1))
    column_periods: list[Any] = list(range(1, min(collector.limits.max_period, minimum_width) + 1))
    period_pairs: list[tuple[Any, Any]] = [
        (row, column) for row in row_periods for column in column_periods
    ]
    period_pairs += [(row, "width") for row in row_periods]
    period_pairs += [("height", column) for column in column_periods]
    reducers = (
        ("mode_smallest", {"kind": "modal"}, 0),
        ("mode_first", {"kind": "modal"}, 1),
        ("mode_last", {"kind": "modal"}, 1),
        ("nonbackground_mode", {"kind": "modal"}, 2),
        ("nonbackground_mode", {"kind": "literal", "color": 0}, 3),
        ("first", {"kind": "modal"}, 2),
        ("last", {"kind": "modal"}, 2),
    )
    offsets = ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1))
    for shape_rule in shape_rules:
        for row_period, column_period in period_pairs:
            # Any rendered residue program is periodic regardless of its
            # reducer.  Reject impossible period pairs before paying for seven
            # executions over every cell.  This is an exact semantic filter,
            # not a heuristic, and makes the lane cheap on irregular tasks.
            possible = True
            for source, target in collector.train:
                rows = _resolve_period(row_period, source, "row")
                columns = _resolve_period(column_period, source, "column")
                out_height, out_width = _shape(target)
                if any(
                    target[row][column]
                    != target[row % rows][column % columns]
                    for row in range(out_height)
                    for column in range(out_width)
                    if row % rows < out_height and column % columns < out_width
                ):
                    possible = False
                    break
            if not possible:
                continue
            for reducer, background, reducer_cost in reducers:
                # Phase shifts matter primarily when extending/cropping.  Same-
                # shape repair has one canonical phase and stays cheap.
                these_offsets = offsets if shape_rule.get("kind") != "same" else ((0, 0),)
                for row_offset, column_offset in these_offsets:
                    program = {
                        "operator": "periodic_residue",
                        "row_period": row_period,
                        "column_period": column_period,
                        "reducer": reducer,
                        "background": background,
                        "shape": shape_rule,
                        "row_offset": row_offset,
                        "column_offset": column_offset,
                    }
                    complexity = (
                        5
                        + _shape_cost(shape_rule)
                        + _period_cost(row_period, source_shapes, "row")
                        + _period_cost(column_period, source_shapes, "column")
                        + reducer_cost
                        + abs(row_offset)
                        + abs(column_offset)
                        + int(row_offset < 0)
                        + int(column_offset < 0)
                    )
                    collector.add(
                        "pattern.periodic_residue",
                        program,
                        complexity,
                        {
                            "regularity": "row_column_residue_consensus",
                            "noise_policy": reducer,
                            "periodic_axes": 2,
                        },
                    )


def _region_specs() -> list[tuple[dict[str, Any], int]]:
    result: list[tuple[dict[str, Any], int]] = [
        ({"kind": "full"}, 0),
        ({"kind": "minimal_exact_tile"}, 2),
        ({"kind": "trim_suffix_minimal_tile"}, 2),
        ({"kind": "first_row"}, 3),
        ({"kind": "first_column"}, 3),
    ]
    for background, cost in (({"kind": "modal"}, 1), ({"kind": "literal", "color": 0}, 2)):
        result.append(({"kind": "foreground_bbox", "background": background}, 3 + cost))
        for connectivity in (4, 8):
            result.append(
                (
                    {
                        "kind": "largest_component",
                        "background": background,
                        "connectivity": connectivity,
                    },
                    5 + cost,
                )
            )
    return result


def _generate_region_renderers(collector: _Collector, shape_rules: Sequence[dict[str, Any]]) -> None:
    offsets = ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1))
    for shape_rule in shape_rules:
        for region, region_cost in _region_specs():
            for row_offset, column_offset in offsets:
                program = {
                    "operator": "tile_region",
                    "region": region,
                    "shape": shape_rule,
                    "row_offset": row_offset,
                    "column_offset": column_offset,
                }
                collector.add(
                    "pattern.motif_tile",
                    program,
                    6
                    + region_cost
                    + _shape_cost(shape_rule)
                    + abs(row_offset)
                    + abs(column_offset)
                    + int(row_offset < 0)
                    + int(column_offset < 0),
                    {"regularity": "translated_motif_tiling", "motif_selector": region["kind"]},
                )
            for duplicate_edge in (False, True):
                program = {
                    "operator": "reflect_region",
                    "region": region,
                    "shape": shape_rule,
                    "row_offset": 0,
                    "column_offset": 0,
                    "duplicate_edge": duplicate_edge,
                }
                collector.add(
                    "pattern.reflected_tile",
                    program,
                    8 + region_cost + _shape_cost(shape_rule) + int(duplicate_edge),
                    {"regularity": "dihedral_reflected_tiling", "motif_selector": region["kind"]},
                )
            for gap in (1, 2):
                for row_gap, column_gap in ((gap, 0), (0, gap), (gap, gap)):
                    for transparent in (False, True):
                        for background, bg_cost in (
                            ({"kind": "modal"}, 1),
                            ({"kind": "literal", "color": 0}, 2),
                        ):
                            program = {
                                "operator": "stamp_region",
                                "region": region,
                                "shape": shape_rule,
                                "row_gap": row_gap,
                                "column_gap": column_gap,
                                "row_offset": 0,
                                "column_offset": 0,
                                "background": background,
                                "transparent_background": transparent,
                            }
                            collector.add(
                                "pattern.motif_canvas",
                                program,
                                11
                                + region_cost
                                + _shape_cost(shape_rule)
                                + gap
                                + bg_cost
                                + int(transparent),
                                {
                                    "regularity": "spaced_motif_canvas",
                                    "motif_selector": region["kind"],
                                },
                            )


def _generate_symmetry(collector: _Collector) -> None:
    transform_sets = [
        ["horizontal"],
        ["vertical"],
        ["rotation_180"],
        ["main_diagonal"],
        ["anti_diagonal"],
        ["horizontal", "vertical"],
        ["main_diagonal", "anti_diagonal"],
    ]
    policies = (
        ("fill_background_unique", 0),
        ("fill_background_mode", 1),
        ("orbit_nonbackground_mode", 2),
        ("orbit_mode", 3),
    )
    for transforms in transform_sets:
        for policy, policy_cost in policies:
            for background, bg_cost in (({"kind": "modal"}, 0), ({"kind": "literal", "color": 0}, 1)):
                program = {
                    "operator": "symmetry_completion",
                    "transforms": transforms,
                    "policy": policy,
                    "background": background,
                }
                collector.add(
                    "pattern.symmetry_completion",
                    program,
                    4 + len(transforms) + policy_cost + bg_cost,
                    {
                        "regularity": "symmetry_orbit_completion",
                        "symmetry_group": transforms,
                        "conservative_fill": policy.startswith("fill_background"),
                    },
                )

    for vertical, horizontal in ((True, False), (False, True), (True, True)):
        for overlap in (0, 1):
            for reverse_order in (False, True):
                program = {
                    "operator": "mirror_expand",
                    "vertical": vertical,
                    "horizontal": horizontal,
                    "overlap": overlap,
                    "reverse_order": reverse_order,
                }
                collector.add(
                    "pattern.mirror_expand",
                    program,
                    5 + int(vertical) + int(horizontal) + overlap + int(reverse_order),
                    {"regularity": "axis_mirror_concatenation"},
                )


def _infer_coordinate_selectors(
    train: Sequence[Pair],
    coordinate: str,
    period: int,
    dynamic_first: bool,
) -> Optional[list[dict[str, Any]]]:
    choices: list[dict[str, Any]] = []
    for residue in range(period):
        observations: list[tuple[Grid, int]] = []
        for source, target in train:
            height, width = _shape(target)
            values = {
                target[row][column]
                for row in range(height)
                for column in range(width)
                if _coordinate_index(coordinate, row, column, height, width, period) == residue
            }
            if len(values) != 1:
                return None
            observations.append((source, next(iter(values))))
        options = _selector_options(observations)
        if not options:
            return None
        if dynamic_first:
            choices.append(options[0])
        else:
            literal = next((record for record in options if record["kind"] == "literal"), None)
            choices.append(literal or options[0])
    return choices


def _generate_coordinate_cycles(collector: _Collector, shape_rules: Sequence[dict[str, Any]]) -> None:
    geometries = ("row", "column", "diagonal", "anti_diagonal", "ring")
    for shape_rule in shape_rules:
        for coordinate in geometries:
            for period in range(1, collector.limits.max_period + 1):
                selector_variants: list[list[dict[str, Any]]] = []
                for dynamic_first in (True, False):
                    selectors = _infer_coordinate_selectors(
                        collector.train, coordinate, period, dynamic_first
                    )
                    if selectors is not None and _canonical(selectors) not in {
                        _canonical(old) for old in selector_variants
                    }:
                        selector_variants.append(selectors)
                for selectors in selector_variants:
                    # Period-one constant fills are valid but weak; MDL ranks
                    # them behind genuinely cyclic descriptions.
                    diversity = len({_canonical(selector) for selector in selectors})
                    program = {
                        "operator": "coordinate_cycle",
                        "coordinate": coordinate,
                        "period": period,
                        "selectors": selectors,
                        "shape": shape_rule,
                    }
                    literal_count = sum(selector["kind"] == "literal" for selector in selectors)
                    complexity = (
                        5
                        + _shape_cost(shape_rule)
                        + period
                        + sum(_selector_cost(selector) for selector in selectors)
                        + (3 if period == 1 else 0)
                    )
                    family = "pattern.frame_cycle" if coordinate == "ring" else "pattern.color_cycle"
                    collector.add(
                        family,
                        program,
                        complexity,
                        {
                            "regularity": f"{coordinate}_coordinate_cycle",
                            "period": period,
                            "distinct_roles": diversity,
                            "dynamic_role_count": period - literal_count,
                        },
                    )

    # A suffix-framed periodic prefix can reveal the cycle alphabet while its
    # cardinality changes between demonstrations and the test case.  Fixed
    # period synthesis cannot express that transfer, so infer the alphabet
    # afresh from the trimmed prefix and keep only a small coordinate grammar.
    for shape_rule in shape_rules:
        for order, order_cost in (
            ("first_row", 0),
            ("first_column", 1),
            ("flat_first", 2),
            ("sorted_palette", 2),
        ):
            for shift in (1, -1, 2, -2):
                program = {
                    "operator": "dynamic_motif_color_cycle",
                    "order": order,
                    "shift": shift,
                    "shape": shape_rule,
                }
                collector.add(
                    "pattern.dynamic_motif_cycle",
                    program,
                    4
                    + _shape_cost(shape_rule)
                    + order_cost
                    + abs(shift)
                    + int(shift < 0),
                    {
                        "regularity": "periodic_motif_with_palette_successor",
                        "dynamic_role_count": "trimmed_motif_palette_cardinality",
                        "suffix_frame_removed": True,
                    },
                )

    for shape_rule in shape_rules:
        for order, order_cost in (
            ("first_row", 0),
            ("first_column", 1),
            ("flat_first", 2),
            ("sorted_palette", 2),
            ("frequency_descending", 3),
        ):
            for row_step, column_step in (
                (1, 1),
                (1, -1),
                (-1, 1),
                (-1, -1),
                (1, 0),
                (-1, 0),
                (0, 1),
                (0, -1),
            ):
                for phase in (0, 1, -1, 2, -2):
                    program = {
                        "operator": "dynamic_coordinate_cycle",
                        "order": order,
                        "row_step": row_step,
                        "column_step": column_step,
                        "phase": phase,
                        "shape": shape_rule,
                    }
                    complexity = (
                        5
                        + _shape_cost(shape_rule)
                        + order_cost
                        + int(row_step < 0)
                        + int(column_step < 0)
                        + abs(phase)
                        + int(phase < 0)
                    )
                    collector.add(
                        "pattern.dynamic_color_cycle",
                        program,
                        complexity,
                        {
                            "regularity": "input_derived_variable_cardinality_cycle",
                            "dynamic_role_count": "input_palette_cardinality",
                            "suffix_frame_removed": True,
                        },
                    )


def _family_rank(candidate: Mapping[str, Any]) -> int:
    family = str(candidate["family"])
    return {
        "pattern.ring_clue_completion": 0,
        "pattern.singleton_cross": 0,
        "pattern.centered_inventory_line": 0,
        "pattern.alternating_rays": 0,
        "pattern.edge_diagonal_frame": 0,
        "pattern.component_seed_flood": 0,
        "pattern.largest_rectangle_fill": 0,
        "pattern.vertical_bar_fan": 0,
        "pattern.nearest_parallel_borders": 0,
        "pattern.singleton_focus": 0,
        "pattern.marker_line_projection": 0,
        "pattern.bottom_seed_serpentine": 0,
        "pattern.frame_marker_quadrants": 0,
        "pattern.seeded_material_recolor": 0,
        "pattern.diagonal_block_rays": 0,
        "pattern.open_box_marker_fill": 0,
        "pattern.boundary_signal_bounce": 0,
        "pattern.open_frame_beam_fill": 0,
        "pattern.open_box_lateral_beam": 0,
        "pattern.nested_tile_state_denoise": 0,
        "pattern.grid_three_diagonal_fill": 0,
        "pattern.barrier_region_normalization": 0,
        "pattern.frame_interior_palette_swap": 0,
        "pattern.nested_square_pulse_expand": 0,
        "pattern.fit_marker_topology_to_frame": 0,
        "pattern.pack_objects_by_area": 0,
        "pattern.counterrotate_bar_attributes": 0,
        "pattern.symmetry_completion": 0,
        "pattern.periodic_residue": 1,
        "pattern.mirror_expand": 2,
        "pattern.motif_tile": 3,
        "pattern.reflected_tile": 4,
        "pattern.color_cycle": 5,
        "pattern.dynamic_motif_cycle": 5,
        "pattern.dynamic_color_cycle": 6,
        "pattern.frame_cycle": 6,
        "pattern.motif_canvas": 7,
    }.get(family, 20)


def _rank(candidate: Mapping[str, Any]) -> tuple[Any, ...]:
    evidence = candidate["evidence"]
    mdl = evidence["mdl"]
    # Description length is primary.  Equal-length programs prefer fewer
    # literals, structural families with smaller inductive scope, and greater
    # observed edit support.  Every term is independent of test targets.
    return (
        int(mdl["description_length"]),
        int(mdl["literal_color_cost"]),
        _family_rank(candidate),
        -int(evidence["changed_cell_support"]),
        _canonical(candidate["program"]),
    )


def compile_task(task: Any, limits: Any = None) -> list[dict[str, Any]]:
    """Return exact-replay periodic-pattern candidates in deterministic order."""

    bounds = Limits.from_value(limits)
    if bounds.max_programs == 0:
        return []
    parsed = _read_task(task, bounds)
    if parsed is None:
        return []
    train, tests = parsed
    # Identity-only demonstrations contain no evidence that this lane should
    # replace the inherited answer, so emit no speculative no-op candidate.
    if all(source == target for source, target in train):
        return []
    shape_rules = _shape_rules(train)
    if not shape_rules:
        return []
    collector = _Collector(train, tests, bounds)
    _generate_targeted_patterns(collector)
    _generate_symmetry(collector)
    _generate_periodic(collector, shape_rules)
    _generate_coordinate_cycles(collector, shape_rules)
    _generate_region_renderers(collector, shape_rules)

    collector.candidates.sort(key=_rank)
    result: list[dict[str, Any]] = []
    seen_behaviors: set[str] = set()
    for candidate in collector.candidates:
        behavior = _canonical(candidate["test_outputs"])
        if behavior in seen_behaviors:
            continue
        seen_behaviors.add(behavior)
        result.append(candidate)
        if len(result) >= bounds.max_programs:
            break
    return result


__all__ = ["Limits", "compile_task", "execute_program"]
