"""Finite extraction and compact-serialization tournament entrant.

The entrant compiles only from labelled training demonstrations and test
*inputs*.  It enumerates a closed, deterministic grammar, admits a program
only after exact replay of every demonstration, then quotients programs by
their complete tuple of test-input raster behaviours.  Invalid inputs,
incomplete budgeted searches, and over-large result sets fail closed.

Author: Komorebi P.
"""
from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass
from functools import lru_cache
import json
from typing import Any, Iterable, Mapping, Sequence


Grid = tuple[tuple[int, ...], ...]
PROGRAM_SCHEMA = "komorebi.pr_lasm.block13.extraction_program"
SCHEMA_VERSION = 1

_BACKGROUND_ROLES = ("mode", "border", "corners")
_CONNECTIVITIES = (4, 8)
_SEPARATIONS = (False, True)
_MAX_GRID_DIMENSION = 30
_MAX_GRID_CELLS = 900
_FORBIDDEN_PROGRAM_KEYS = frozenset(
    {
        "id",
        "task_id",
        "solution",
        "solutions",
        "target",
        "targets",
        "output",
        "outputs",
        "prediction",
        "predictions",
        "answer",
        "answers",
        "label",
        "labels",
    }
)


@dataclass(frozen=True, slots=True)
class _Limits:
    max_programs: int = 9000
    max_executions: int = 150_000
    max_exact_programs: int = 4096
    max_candidates: int = 256
    max_examples: int = 16
    max_objects: int = 64


@dataclass(frozen=True, slots=True)
class _Object:
    cells: tuple[tuple[int, int, int], ...]
    y0: int
    y1: int
    x0: int
    x1: int
    color: int

    @property
    def area(self) -> int:
        return len(self.cells)

    @property
    def height(self) -> int:
        return self.y1 - self.y0

    @property
    def width(self) -> int:
        return self.x1 - self.x0

    @property
    def density_key(self) -> tuple[int, int]:
        return self.area, self.height * self.width


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _grid(value: Any) -> Grid:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise TypeError("grid must be a sequence of rows")
    rows: list[tuple[int, ...]] = []
    for raw_row in value:
        if not isinstance(raw_row, Sequence) or isinstance(
            raw_row, (str, bytes, bytearray)
        ):
            raise TypeError("grid rows must be sequences")
        row: list[int] = []
        for cell in raw_row:
            if isinstance(cell, bool) or not isinstance(cell, int):
                raise TypeError("ARC cells must be integers")
            if not 0 <= cell <= 9:
                raise ValueError("ARC cells must lie in [0, 9]")
            row.append(int(cell))
        rows.append(tuple(row))
    result = tuple(rows)
    if not result or not result[0] or any(len(row) != len(result[0]) for row in result):
        raise ValueError("grid must be nonempty and rectangular")
    if len(result) > _MAX_GRID_DIMENSION or len(result[0]) > _MAX_GRID_DIMENSION:
        raise ValueError("grid exceeds ARC's 30x30 bound")
    return result


def _checked_output(value: Grid) -> Grid:
    result = _grid(value)
    if len(result) * len(result[0]) > _MAX_GRID_CELLS:
        raise ValueError("output exceeds the raster cap")
    return result


def _parse_limits(value: Any) -> _Limits:
    if value is None:
        return _Limits()
    if not isinstance(value, Mapping):
        raise TypeError("limits must be a mapping or None")
    # These keys belong to the shared tournament envelope.  Accept them
    # without letting them expand this entrant's stricter local bounds.
    compatibility = {
        "candidate_cap",
        "max_total_candidates",
        "max_replay_calls",
        "max_replay_stages",
        "max_trace_bytes",
    }
    allowed = set(_Limits.__dataclass_fields__) | compatibility
    if set(value) - allowed:
        raise ValueError("unknown extraction limit")
    fields: dict[str, int] = {}
    for key, raw in value.items():
        if isinstance(raw, bool) or not isinstance(raw, int) or raw < 1:
            raise ValueError("limits must be positive integers")
        if key not in compatibility:
            fields[str(key)] = int(raw)
    if "candidate_cap" in value and "max_candidates" not in value:
        fields["max_candidates"] = int(value["candidate_cap"])
    return _Limits(**fields)


def _sanitize(task: Any, limits: _Limits) -> tuple[tuple[tuple[Grid, Grid], ...], tuple[Grid, ...]]:
    if not isinstance(task, Mapping):
        raise TypeError("task must be a mapping")
    raw_train = task["train"]
    raw_test = task["test"]
    if not isinstance(raw_train, Sequence) or isinstance(raw_train, (str, bytes, bytearray)):
        raise TypeError("train must be a sequence")
    if not isinstance(raw_test, Sequence) or isinstance(raw_test, (str, bytes, bytearray)):
        raise TypeError("test must be a sequence")
    if not raw_train or not raw_test or len(raw_train) + len(raw_test) > limits.max_examples:
        raise ValueError("task example count is outside the finite contract")
    train: list[tuple[Grid, Grid]] = []
    for example in raw_train:
        if not isinstance(example, Mapping):
            raise TypeError("training examples must be mappings")
        train.append((_grid(example["input"]), _grid(example["output"])))
    # Deliberately ask test records for exactly one field.  Attached labels,
    # identifiers, and metadata remain structurally unobservable here.
    test: list[Grid] = []
    for example in raw_test:
        if not isinstance(example, Mapping):
            raise TypeError("test examples must be mappings")
        test.append(_grid(example["input"]))
    return tuple(train), tuple(test)


def _shape(grid: Grid) -> tuple[int, int]:
    return len(grid), len(grid[0])


def _transpose(grid: Grid) -> Grid:
    return tuple(tuple(grid[y][x] for y in range(len(grid))) for x in range(len(grid[0])))


def _mode(values: Iterable[int]) -> int:
    counts = Counter(values)
    if not counts:
        raise ValueError("cannot choose a color from no cells")
    return min(counts, key=lambda color: (-counts[color], color))


@lru_cache(maxsize=8192)
def _resolve_background(grid: Grid, role: str) -> int:
    if role == "mode":
        return _mode(cell for row in grid for cell in row)
    if role == "border":
        h, w = _shape(grid)
        cells = list(grid[0]) + (list(grid[-1]) if h > 1 else [])
        cells.extend(grid[y][0] for y in range(1, h - 1))
        if w > 1:
            cells.extend(grid[y][-1] for y in range(1, h - 1))
        return _mode(cells)
    if role == "corners":
        return _mode((grid[0][0], grid[0][-1], grid[-1][0], grid[-1][-1]))
    raise ValueError("unknown background role")


def _foreground_counts(grid: Grid, background: int) -> Counter[int]:
    return Counter(cell for row in grid for cell in row if cell != background)


def _resolve_color_selector(grid: Grid, background: int, selector: Any) -> int:
    if isinstance(selector, bool):
        raise ValueError("Boolean color is forbidden")
    if isinstance(selector, int):
        if not 0 <= selector <= 9:
            raise ValueError("color is outside ARC's palette")
        return selector
    counts = _foreground_counts(grid, background)
    if not counts:
        raise ValueError("no foreground colors")
    if selector == "rarest_foreground":
        return min(counts, key=lambda color: (counts[color], color))
    if selector == "most_foreground":
        return min(counts, key=lambda color: (-counts[color], color))
    if selector == "lowest_foreground":
        return min(counts)
    if selector == "highest_foreground":
        return max(counts)
    raise ValueError("unknown color selector")


@lru_cache(maxsize=8192)
def _components(
    grid: Grid,
    background: int,
    connectivity: int,
    separate_colors: bool,
) -> tuple[_Object, ...]:
    if connectivity not in _CONNECTIVITIES:
        raise ValueError("unsupported connectivity")
    h, w = _shape(grid)
    remaining = {
        (y, x)
        for y in range(h)
        for x in range(w)
        if grid[y][x] != background
    }
    neighbors = ((-1, 0), (1, 0), (0, -1), (0, 1))
    if connectivity == 8:
        neighbors += ((-1, -1), (-1, 1), (1, -1), (1, 1))
    result: list[_Object] = []
    while remaining:
        seed = min(remaining)
        seed_color = grid[seed[0]][seed[1]]
        queue = deque((seed,))
        remaining.remove(seed)
        positions: list[tuple[int, int]] = []
        while queue:
            y, x = queue.popleft()
            positions.append((y, x))
            for dy, dx in neighbors:
                point = y + dy, x + dx
                if point not in remaining:
                    continue
                if separate_colors and grid[point[0]][point[1]] != seed_color:
                    continue
                remaining.remove(point)
                queue.append(point)
        cells = tuple(sorted((y, x, grid[y][x]) for y, x in positions))
        colors = Counter(cell[2] for cell in cells)
        color = min(colors, key=lambda item: (-colors[item], item))
        ys = [cell[0] for cell in cells]
        xs = [cell[1] for cell in cells]
        result.append(
            _Object(cells, min(ys), max(ys) + 1, min(xs), max(xs) + 1, color)
        )
    return tuple(sorted(result, key=lambda obj: (obj.y0, obj.x0, obj.y1, obj.x1, obj.color, obj.cells)))


def _object_key(obj: _Object) -> tuple[Any, ...]:
    return obj.y0, obj.x0, obj.y1, obj.x1, obj.color, obj.cells


def _select_object(objects: Sequence[_Object], selector: str) -> _Object:
    if not objects:
        raise ValueError("no selectable objects")
    reading = _object_key
    keys = {
        "reading_first": lambda obj: reading(obj),
        "reading_last": lambda obj: tuple(-v if isinstance(v, int) else v for v in reading(obj)[:5]),
        "topmost": lambda obj: (obj.y0, obj.x0, reading(obj)),
        "bottommost": lambda obj: (-obj.y1, obj.x0, reading(obj)),
        "leftmost": lambda obj: (obj.x0, obj.y0, reading(obj)),
        "rightmost": lambda obj: (-obj.x1, obj.y0, reading(obj)),
        "smallest": lambda obj: (obj.area, reading(obj)),
        "largest": lambda obj: (-obj.area, reading(obj)),
        "shortest": lambda obj: (obj.height, reading(obj)),
        "tallest": lambda obj: (-obj.height, reading(obj)),
        "narrowest": lambda obj: (obj.width, reading(obj)),
        "widest": lambda obj: (-obj.width, reading(obj)),
        "sparsest": lambda obj: (obj.area / (obj.height * obj.width), reading(obj)),
        "densest": lambda obj: (-obj.area / (obj.height * obj.width), reading(obj)),
        "color_low": lambda obj: (obj.color, reading(obj)),
        "color_high": lambda obj: (-obj.color, reading(obj)),
    }
    if selector not in keys:
        raise ValueError("unknown object selector")
    return min(objects, key=keys[selector])


def _order_objects(objects: Sequence[_Object], order: str) -> tuple[_Object, ...]:
    keys = {
        "reading": lambda obj: (obj.y0, obj.x0, _object_key(obj)),
        "reverse_reading": lambda obj: (-obj.y0, -obj.x0, _object_key(obj)),
        "top_bottom": lambda obj: (obj.y0, obj.x0, _object_key(obj)),
        "bottom_top": lambda obj: (-obj.y1, obj.x0, _object_key(obj)),
        "left_right": lambda obj: (obj.x0, obj.y0, _object_key(obj)),
        "right_left": lambda obj: (-obj.x1, obj.y0, _object_key(obj)),
        "area_asc": lambda obj: (obj.area, obj.y0, obj.x0, _object_key(obj)),
        "area_desc": lambda obj: (-obj.area, obj.y0, obj.x0, _object_key(obj)),
        "color_asc": lambda obj: (obj.color, obj.y0, obj.x0, _object_key(obj)),
        "color_desc": lambda obj: (-obj.color, obj.y0, obj.x0, _object_key(obj)),
    }
    if order not in keys:
        raise ValueError("unknown object order")
    return tuple(sorted(objects, key=keys[order]))


def _crop_coordinates(grid: Grid, y0: int, y1: int, x0: int, x1: int) -> Grid:
    h, w = _shape(grid)
    if not (0 <= y0 < y1 <= h and 0 <= x0 < x1 <= w):
        raise ValueError("empty or invalid crop")
    return tuple(tuple(grid[y][x] for x in range(x0, x1)) for y in range(y0, y1))


def _tight_crop(grid: Grid, background: int) -> Grid:
    points = [
        (y, x)
        for y, row in enumerate(grid)
        for x, cell in enumerate(row)
        if cell != background
    ]
    if not points:
        raise ValueError("cannot tightly crop an empty foreground")
    ys = [point[0] for point in points]
    xs = [point[1] for point in points]
    return _crop_coordinates(grid, min(ys), max(ys) + 1, min(xs), max(xs) + 1)


def _render_object(
    grid: Grid,
    obj: _Object,
    background: int,
    render: str,
    mask_color: Any = "object_color",
) -> Grid:
    if render == "raw":
        return _crop_coordinates(grid, obj.y0, obj.y1, obj.x0, obj.x1)
    canvas = [[background for _ in range(obj.width)] for _ in range(obj.height)]
    color = obj.color
    if render == "mask":
        color = (
            obj.color
            if mask_color == "object_color"
            else _resolve_color_selector(grid, background, mask_color)
        )
    elif render != "isolated":
        raise ValueError("unknown object renderer")
    for y, x, source_color in obj.cells:
        canvas[y - obj.y0][x - obj.x0] = color if render == "mask" else source_color
    return tuple(tuple(row) for row in canvas)


@lru_cache(maxsize=8192)
def _region_points(grid: Grid, background: int, selector: Any) -> tuple[tuple[int, int], ...]:
    if selector == "all_foreground":
        points = tuple(
            (y, x)
            for y, row in enumerate(grid)
            for x, cell in enumerate(row)
            if cell != background
        )
    else:
        color = _resolve_color_selector(grid, background, selector)
        points = tuple(
            (y, x)
            for y, row in enumerate(grid)
            for x, cell in enumerate(row)
            if cell == color
        )
    if not points:
        raise ValueError("selected region is empty")
    return points


def _bbox(points: Sequence[tuple[int, int]], grid: Grid, adjustment: str) -> tuple[int, int, int, int]:
    ys = [point[0] for point in points]
    xs = [point[1] for point in points]
    y0, y1, x0, x1 = min(ys), max(ys) + 1, min(xs), max(xs) + 1
    if adjustment == "inner1":
        y0, y1, x0, x1 = y0 + 1, y1 - 1, x0 + 1, x1 - 1
    elif adjustment == "outer1":
        h, w = _shape(grid)
        y0, y1, x0, x1 = max(0, y0 - 1), min(h, y1 + 1), max(0, x0 - 1), min(w, x1 + 1)
    elif adjustment != "tight":
        raise ValueError("unknown bounding-box adjustment")
    if y0 >= y1 or x0 >= x1:
        raise ValueError("bounding-box adjustment is empty")
    return y0, y1, x0, x1


def _segments(length: int, separators: set[int]) -> tuple[tuple[int, int], ...]:
    result: list[tuple[int, int]] = []
    start: int | None = None
    for index in range(length):
        if index in separators:
            if start is not None:
                result.append((start, index))
                start = None
        elif start is None:
            start = index
    if start is not None:
        result.append((start, length))
    return tuple(segment for segment in result if segment[0] < segment[1])


def _separator_indices(grid: Grid, axis: str, kind: str, background: int) -> set[int]:
    lines = grid if axis == "rows" else _transpose(grid)
    result = set()
    for index, line in enumerate(lines):
        uniform = len(set(line)) == 1
        if kind == "uniform" and uniform:
            result.add(index)
        elif kind == "background" and uniform and line[0] == background:
            result.add(index)
    if kind not in {"uniform", "background"}:
        raise ValueError("unknown separator kind")
    return result


@lru_cache(maxsize=8192)
def _panels(grid: Grid, axis: str, kind: str, background: int) -> tuple[Grid, ...]:
    h, w = _shape(grid)
    row_sep = _separator_indices(grid, "rows", kind, background) if axis in {"rows", "both"} else set()
    col_sep = _separator_indices(grid, "columns", kind, background) if axis in {"columns", "both"} else set()
    row_ranges = _segments(h, row_sep) if axis in {"rows", "both"} else ((0, h),)
    col_ranges = _segments(w, col_sep) if axis in {"columns", "both"} else ((0, w),)
    if axis == "rows" and len(row_ranges) < 2:
        raise ValueError("no row panel split")
    if axis == "columns" and len(col_ranges) < 2:
        raise ValueError("no column panel split")
    if axis == "both" and (len(row_ranges) < 2 or len(col_ranges) < 2):
        raise ValueError("no two-axis panel split")
    return tuple(
        _crop_coordinates(grid, y0, y1, x0, x1)
        for y0, y1 in row_ranges
        for x0, x1 in col_ranges
    )


def _select_panel(panels: Sequence[Grid], selector: Any, background: int) -> Grid:
    if not panels:
        raise ValueError("no panels")
    if isinstance(selector, int) and not isinstance(selector, bool):
        if selector < 0 or selector >= len(panels):
            raise ValueError("panel index is unavailable")
        return panels[selector]
    if selector == "last":
        return panels[-1]
    if selector in {"unique_content", "repeated_content"}:
        counts = Counter(panels)
        wanted = 1 if selector == "unique_content" else max(counts.values())
        choices = [panel for panel in panels if counts[panel] == wanted]
        if selector == "unique_content" and len(choices) != 1:
            raise ValueError("content uniqueness is ambiguous")
        return choices[0]

    def features(item: tuple[int, Grid]) -> tuple[int, int, int, int, int]:
        index, panel = item
        area = len(panel) * len(panel[0])
        foreground = sum(cell != background for row in panel for cell in row)
        colors = len(set(cell for row in panel for cell in row if cell != background))
        return area, foreground, colors, len(panel), index

    keyed = list(enumerate(panels))
    key_functions = {
        "smallest_area": lambda item: (features(item)[0], item[0]),
        "largest_area": lambda item: (-features(item)[0], item[0]),
        "least_foreground": lambda item: (features(item)[1], item[0]),
        "most_foreground": lambda item: (-features(item)[1], item[0]),
        "least_colors": lambda item: (features(item)[2], item[0]),
        "most_colors": lambda item: (-features(item)[2], item[0]),
        "sparsest": lambda item: (features(item)[1] / features(item)[0], item[0]),
        "densest": lambda item: (-features(item)[1] / features(item)[0], item[0]),
    }
    if selector not in key_functions:
        raise ValueError("unknown panel selector")
    return min(keyed, key=key_functions[selector])[1]


def _combine_panels(panels: Sequence[Grid], background: int, method: str) -> Grid:
    if len(panels) < 2 or len({_shape(panel) for panel in panels}) != 1:
        raise ValueError("panel combination requires equal-shaped panels")
    h, w = _shape(panels[0])
    out = [[background for _ in range(w)] for _ in range(h)]
    for y in range(h):
        for x in range(w):
            values = [panel[y][x] for panel in panels]
            foreground = [value for value in values if value != background]
            if method == "overlay_first" and foreground:
                out[y][x] = foreground[0]
            elif method == "overlay_last" and foreground:
                out[y][x] = foreground[-1]
            elif method == "agreement" and len(set(values)) == 1:
                out[y][x] = values[0]
            elif method == "intersection" and len(foreground) == len(values):
                out[y][x] = values[0]
            elif method == "xor" and len(foreground) == 1:
                out[y][x] = foreground[0]
            elif method == "difference_first" and values[0] != background and all(
                value == background for value in values[1:]
            ):
                out[y][x] = values[0]
    return tuple(tuple(row) for row in out)


def _line_selected(line: tuple[int, ...], predicate: str, background: int, all_lines: Sequence[tuple[int, ...]]) -> bool:
    foreground = sum(cell != background for cell in line)
    distinct = len(set(line))
    scores_fg = [sum(cell != background for cell in other) for other in all_lines]
    scores_distinct = [len(set(other)) for other in all_lines]
    counts = Counter(all_lines)
    if predicate == "not_background":
        return foreground > 0
    if predicate == "background":
        return foreground == 0
    if predicate == "uniform":
        return distinct == 1
    if predicate == "nonuniform":
        return distinct > 1
    if predicate == "min_foreground":
        return foreground == min(scores_fg)
    if predicate == "max_foreground":
        return foreground == max(scores_fg)
    if predicate == "min_distinct":
        return distinct == min(scores_distinct)
    if predicate == "max_distinct":
        return distinct == max(scores_distinct)
    if predicate == "unique_pattern":
        return counts[line] == 1
    if predicate == "repeated_pattern":
        return counts[line] > 1
    if predicate == "singleton_foreground":
        return foreground == 1
    raise ValueError("unknown line predicate")


def _filter_lines(grid: Grid, axis: str, predicate: str, background: int) -> Grid:
    transposed = axis == "columns"
    if axis not in {"rows", "columns"}:
        raise ValueError("unknown line axis")
    source = _transpose(grid) if transposed else grid
    selected = tuple(
        line for line in source if _line_selected(line, predicate, background, source)
    )
    if not selected:
        raise ValueError("line selection is empty")
    return _transpose(selected) if transposed else selected


def _dedupe_lines(grid: Grid, axis: str, mode: str) -> Grid:
    def one(source: Grid) -> Grid:
        result: list[tuple[int, ...]] = []
        seen: set[tuple[int, ...]] = set()
        for line in source:
            keep = not result or line != result[-1] if mode == "adjacent" else line not in seen
            if keep:
                result.append(line)
            seen.add(line)
        return tuple(result)

    if mode not in {"adjacent", "global"}:
        raise ValueError("unknown line dedupe mode")
    result = grid
    if axis in {"rows", "both"}:
        result = one(result)
    if axis in {"columns", "both"}:
        result = _transpose(one(_transpose(result)))
    if axis not in {"rows", "columns", "both"}:
        raise ValueError("unknown line dedupe axis")
    return result


def _pack_objects(grid: Grid, objects: Sequence[_Object], background: int, order: str, axis: str) -> Grid:
    ordered = _order_objects(objects, order)
    crops = [_render_object(grid, obj, background, "isolated") for obj in ordered]
    if not crops:
        raise ValueError("no objects to pack")
    if axis == "row":
        h = max(len(crop) for crop in crops)
        w = sum(len(crop[0]) for crop in crops)
        if h > 30 or w > 30:
            raise ValueError("packed row exceeds ARC bounds")
        out = [[background for _ in range(w)] for _ in range(h)]
        cursor = 0
        for crop in crops:
            for y, row in enumerate(crop):
                out[y][cursor : cursor + len(row)] = row
            cursor += len(crop[0])
    elif axis == "column":
        h = sum(len(crop) for crop in crops)
        w = max(len(crop[0]) for crop in crops)
        if h > 30 or w > 30:
            raise ValueError("packed column exceeds ARC bounds")
        out = [[background for _ in range(w)] for _ in range(h)]
        cursor = 0
        for crop in crops:
            for y, row in enumerate(crop):
                out[cursor + y][: len(row)] = row
            cursor += len(crop)
    else:
        raise ValueError("unknown pack axis")
    return tuple(tuple(row) for row in out)


def _serialize_objects(
    grid: Grid,
    objects: Sequence[_Object],
    background: int,
    order: str,
    kind: str,
    axis: str,
    fill: Any,
) -> Grid:
    ordered = _order_objects(objects, order)
    if not ordered:
        raise ValueError("no objects to serialize")
    if kind == "colors":
        values = [obj.color for obj in ordered]
    elif kind == "areas_as_runs":
        values = [obj.color for obj in ordered for _ in range(obj.area)]
    elif kind == "count_bar":
        color = _resolve_color_selector(grid, background, fill)
        values = [color] * len(ordered)
    elif kind == "foreground_bar":
        color = _resolve_color_selector(grid, background, fill)
        values = [color] * sum(obj.area for obj in ordered)
    elif kind == "component_count":
        if len(ordered) > 9:
            raise ValueError("component count is not an ARC color")
        return ((len(ordered),),)
    elif kind == "foreground_count":
        count = sum(obj.area for obj in ordered)
        if count > 9:
            raise ValueError("foreground count is not an ARC color")
        return ((count,),)
    elif kind in {"bbox_dimensions", "color_area"}:
        rows = []
        for obj in ordered:
            row = (obj.height, obj.width) if kind == "bbox_dimensions" else (obj.color, obj.area)
            if any(value > 9 for value in row):
                raise ValueError("serialized numeric feature is not an ARC color")
            rows.append(row)
        result = tuple(rows)
        return _transpose(result) if axis == "row" else result
    elif kind == "color_histogram":
        histogram = Counter(obj.color for obj in ordered)
        rows = tuple((color, histogram[color]) for color in sorted(histogram))
        if any(count > 9 for _, count in rows):
            raise ValueError("histogram count is not an ARC color")
        return _transpose(rows) if axis == "row" else rows
    else:
        raise ValueError("unknown serialization kind")
    if not values or len(values) > 30:
        raise ValueError("serialized line exceeds ARC bounds")
    return (tuple(values),) if axis == "row" else tuple((value,) for value in values)


def _program(family: str, **parameters: Any) -> dict[str, Any]:
    return {
        "schema": PROGRAM_SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "family": family,
        "parameters": parameters,
    }


def _validate_program(program: Mapping[str, Any]) -> None:
    if set(program) != {"schema", "schema_version", "family", "parameters"}:
        raise ValueError("program record has an invalid shape")
    if program["schema"] != PROGRAM_SCHEMA or program["schema_version"] != SCHEMA_VERSION:
        raise ValueError("program schema mismatch")
    if not isinstance(program["family"], str) or not program["family"]:
        raise ValueError("program family must be a nonempty string")
    if not isinstance(program["parameters"], Mapping):
        raise TypeError("program parameters must be a mapping")

    def visit(value: Any) -> None:
        if isinstance(value, Mapping):
            if _FORBIDDEN_PROGRAM_KEYS & {str(key).lower() for key in value}:
                raise ValueError("target-bearing program field is forbidden")
            for key, child in value.items():
                if not isinstance(key, str):
                    raise TypeError("program keys must be strings")
                visit(child)
        elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            for child in value:
                visit(child)
        elif value is not None and not isinstance(value, (str, int, float, bool)):
            raise TypeError("program value is not JSON-compatible")

    visit(program)
    json.loads(_canonical(program))


@lru_cache(maxsize=1)
def _enumerate_programs() -> tuple[dict[str, Any], ...]:
    programs: list[dict[str, Any]] = []
    object_selectors = (
        "reading_first",
        "reading_last",
        "topmost",
        "bottommost",
        "leftmost",
        "rightmost",
        "smallest",
        "largest",
        "shortest",
        "tallest",
        "narrowest",
        "widest",
        "sparsest",
        "densest",
        "color_low",
        "color_high",
    )
    orders = (
        "reading",
        "reverse_reading",
        "top_bottom",
        "bottom_top",
        "left_right",
        "right_left",
        "area_asc",
        "area_desc",
        "color_asc",
        "color_desc",
    )
    dynamic_colors: tuple[Any, ...] = (
        "rarest_foreground",
        "most_foreground",
        "lowest_foreground",
        "highest_foreground",
    )
    region_selectors: tuple[Any, ...] = ("all_foreground",) + dynamic_colors + tuple(range(10))

    for background_role in _BACKGROUND_ROLES:
        for connectivity in _CONNECTIVITIES:
            for separate_colors in _SEPARATIONS:
                common = {
                    "background_role": background_role,
                    "connectivity": connectivity,
                    "separate_colors": separate_colors,
                }
                for selector in object_selectors:
                    programs.append(_program("object_crop", **common, selector=selector, render="raw"))
                    programs.append(_program("object_crop", **common, selector=selector, render="isolated"))
                    for mask_color in dynamic_colors:
                        programs.append(
                            _program(
                                "object_crop",
                                **common,
                                selector=selector,
                                render="mask",
                                mask_color=mask_color,
                            )
                        )
                    programs.append(
                        _program(
                            "object_crop",
                            **common,
                            selector=selector,
                            render="mask",
                            mask_color="object_color",
                        )
                    )
                for order in orders:
                    for axis in ("row", "column"):
                        programs.append(_program("object_pack", **common, order=order, axis=axis))
                        for kind in (
                            "colors",
                            "areas_as_runs",
                            "component_count",
                            "foreground_count",
                            "bbox_dimensions",
                            "color_area",
                            "color_histogram",
                        ):
                            programs.append(
                                _program(
                                    "object_serialize",
                                    **common,
                                    order=order,
                                    kind=kind,
                                    axis=axis,
                                    fill="most_foreground",
                                )
                            )
                        for kind in ("count_bar", "foreground_bar"):
                            for fill in dynamic_colors:
                                programs.append(
                                    _program(
                                        "object_serialize",
                                        **common,
                                        order=order,
                                        kind=kind,
                                        axis=axis,
                                        fill=fill,
                                    )
                                )

        for selector in region_selectors:
            for adjustment in ("tight", "inner1", "outer1"):
                for render in ("raw", "isolated"):
                    programs.append(
                        _program(
                            "bounding_box_extract",
                            background_role=background_role,
                            selector=selector,
                            adjustment=adjustment,
                            render=render,
                        )
                    )
            for crop in (False, True):
                programs.append(
                    _program(
                        "mask_extract",
                        background_role=background_role,
                        selector=selector,
                        crop=crop,
                        render="preserve",
                    )
                )
                for fill in dynamic_colors + tuple(range(10)):
                    programs.append(
                        _program(
                            "mask_extract",
                            background_role=background_role,
                            selector=selector,
                            crop=crop,
                            render="constant",
                            fill=fill,
                        )
                    )

        for separator_kind in ("background", "uniform"):
            for axis in ("rows", "columns", "both"):
                panel_common = {
                    "background_role": background_role,
                    "separator_kind": separator_kind,
                    "axis": axis,
                }
                programs.append(_program("separator_remove", **panel_common))
                for selector in tuple(range(9)) + (
                    "last",
                    "smallest_area",
                    "largest_area",
                    "least_foreground",
                    "most_foreground",
                    "least_colors",
                    "most_colors",
                    "sparsest",
                    "densest",
                    "unique_content",
                    "repeated_content",
                ):
                    for crop in (False, True):
                        programs.append(
                            _program("panel_select", **panel_common, selector=selector, crop=crop)
                        )
                for method in (
                    "overlay_first",
                    "overlay_last",
                    "agreement",
                    "intersection",
                    "xor",
                    "difference_first",
                ):
                    for crop in (False, True):
                        programs.append(
                            _program("panel_combine", **panel_common, method=method, crop=crop)
                        )
                for data_index in (0, 1):
                    for keep in ("mask_foreground", "mask_background"):
                        for crop in (False, True):
                            programs.append(
                                _program(
                                    "panel_pair_mask",
                                    **panel_common,
                                    data_index=data_index,
                                    keep=keep,
                                    crop=crop,
                                )
                            )

        predicates = (
            "not_background",
            "background",
            "uniform",
            "nonuniform",
            "min_foreground",
            "max_foreground",
            "min_distinct",
            "max_distinct",
            "unique_pattern",
            "repeated_pattern",
            "singleton_foreground",
        )
        for axis in ("rows", "columns"):
            for predicate in predicates:
                programs.append(
                    _program(
                        "line_select",
                        background_role=background_role,
                        axis=axis,
                        predicate=predicate,
                    )
                )
            for color in dynamic_colors + tuple(range(10)):
                for keep in (True, False):
                    programs.append(
                        _program(
                            "color_line_select",
                            background_role=background_role,
                            axis=axis,
                            color=color,
                            keep=keep,
                        )
                    )
        for row_predicate in ("not_background", "nonuniform", "min_foreground", "max_foreground"):
            for column_predicate in (
                "not_background",
                "nonuniform",
                "min_foreground",
                "max_foreground",
            ):
                programs.append(
                    _program(
                        "row_column_select",
                        background_role=background_role,
                        row_predicate=row_predicate,
                        column_predicate=column_predicate,
                    )
                )

    for axis in ("rows", "columns", "both"):
        for mode in ("adjacent", "global"):
            programs.append(_program("line_dedupe", axis=axis, mode=mode))

    for row_stride in range(1, 7):
        for column_stride in range(1, 7):
            if (row_stride, column_stride) == (1, 1):
                continue
            for row_phase in range(row_stride):
                for column_phase in range(column_stride):
                    programs.append(
                        _program(
                            "polyphase_extract",
                            row_stride=row_stride,
                            column_stride=column_stride,
                            row_phase=row_phase,
                            column_phase=column_phase,
                        )
                    )

    for row_parts in range(1, 5):
        for column_parts in range(1, 5):
            if (row_parts, column_parts) == (1, 1):
                continue
            for row_index in range(row_parts):
                for column_index in range(column_parts):
                    programs.append(
                        _program(
                            "subgrid_extract",
                            row_parts=row_parts,
                            column_parts=column_parts,
                            row_index=row_index,
                            column_index=column_index,
                        )
                    )

    unique = {_canonical(program): program for program in programs}
    result = tuple(unique[key] for key in sorted(unique))
    for program in result:
        _validate_program(program)
    return result


def _execute(grid: Grid, program: Mapping[str, Any], max_objects: int) -> Grid:
    _validate_program(program)
    family = program["family"]
    p = program["parameters"]

    if family == "polyphase_extract":
        result = tuple(
            tuple(row[p["column_phase"] :: p["column_stride"]])
            for row in grid[p["row_phase"] :: p["row_stride"]]
        )
        return _checked_output(result)

    if family == "subgrid_extract":
        h, w = _shape(grid)
        rp, cp = p["row_parts"], p["column_parts"]
        if h % rp or w % cp:
            raise ValueError("grid is not divisible into requested subgrids")
        dh, dw = h // rp, w // cp
        y0, x0 = p["row_index"] * dh, p["column_index"] * dw
        return _checked_output(_crop_coordinates(grid, y0, y0 + dh, x0, x0 + dw))

    if family == "line_dedupe":
        return _checked_output(_dedupe_lines(grid, p["axis"], p["mode"]))

    background = _resolve_background(grid, p["background_role"])

    if family in {"object_crop", "object_pack", "object_serialize"}:
        objects = _components(grid, background, p["connectivity"], p["separate_colors"])
        if not objects or len(objects) > max_objects:
            raise ValueError("object count is outside the finite contract")
        if family == "object_crop":
            obj = _select_object(objects, p["selector"])
            return _checked_output(
                _render_object(grid, obj, background, p["render"], p.get("mask_color"))
            )
        if family == "object_pack":
            return _checked_output(_pack_objects(grid, objects, background, p["order"], p["axis"]))
        return _checked_output(
            _serialize_objects(
                grid,
                objects,
                background,
                p["order"],
                p["kind"],
                p["axis"],
                p["fill"],
            )
        )

    if family in {"bounding_box_extract", "mask_extract"}:
        points = _region_points(grid, background, p["selector"])
        if family == "bounding_box_extract":
            y0, y1, x0, x1 = _bbox(points, grid, p["adjustment"])
            if p["render"] == "raw":
                return _checked_output(_crop_coordinates(grid, y0, y1, x0, x1))
            chosen = set(points)
            result = tuple(
                tuple(grid[y][x] if (y, x) in chosen else background for x in range(x0, x1))
                for y in range(y0, y1)
            )
            return _checked_output(result)
        chosen = set(points)
        if p["render"] == "preserve":
            rendered = tuple(
                tuple(cell if (y, x) in chosen else background for x, cell in enumerate(row))
                for y, row in enumerate(grid)
            )
        elif p["render"] == "constant":
            fill = _resolve_color_selector(grid, background, p["fill"])
            rendered = tuple(
                tuple(fill if (y, x) in chosen else background for x in range(len(row)))
                for y, row in enumerate(grid)
            )
        else:
            raise ValueError("unknown mask renderer")
        return _checked_output(_tight_crop(rendered, background) if p["crop"] else rendered)

    if family in {"separator_remove", "panel_select", "panel_combine", "panel_pair_mask"}:
        panels = _panels(grid, p["axis"], p["separator_kind"], background)
        if family == "separator_remove":
            h, w = _shape(grid)
            rows = (
                set(range(h)) - _separator_indices(grid, "rows", p["separator_kind"], background)
                if p["axis"] in {"rows", "both"}
                else set(range(h))
            )
            columns = (
                set(range(w)) - _separator_indices(grid, "columns", p["separator_kind"], background)
                if p["axis"] in {"columns", "both"}
                else set(range(w))
            )
            if not rows or not columns:
                raise ValueError("separator removal emptied grid")
            result = tuple(tuple(grid[y][x] for x in sorted(columns)) for y in sorted(rows))
            return _checked_output(result)
        if family == "panel_select":
            result = _select_panel(panels, p["selector"], background)
        elif family == "panel_combine":
            result = _combine_panels(panels, background, p["method"])
        else:
            if len(panels) != 2 or _shape(panels[0]) != _shape(panels[1]):
                raise ValueError("pair mask requires exactly two equal panels")
            data_index = p["data_index"]
            mask_index = 1 - data_index
            data, mask = panels[data_index], panels[mask_index]
            result = tuple(
                tuple(
                    data[y][x]
                    if ((mask[y][x] != background) == (p["keep"] == "mask_foreground"))
                    else background
                    for x in range(len(data[0]))
                )
                for y in range(len(data))
            )
        if p["crop"]:
            result = _tight_crop(result, background)
        return _checked_output(result)

    if family == "line_select":
        return _checked_output(_filter_lines(grid, p["axis"], p["predicate"], background))

    if family == "row_column_select":
        rows = _filter_lines(grid, "rows", p["row_predicate"], background)
        return _checked_output(_filter_lines(rows, "columns", p["column_predicate"], background))

    if family == "color_line_select":
        color = _resolve_color_selector(grid, background, p["color"])
        transposed = p["axis"] == "columns"
        if p["axis"] not in {"rows", "columns"}:
            raise ValueError("unknown line axis")
        source = _transpose(grid) if transposed else grid
        selected = tuple(line for line in source if ((color in line) == p["keep"]))
        if not selected:
            raise ValueError("color line selection is empty")
        return _checked_output(_transpose(selected) if transposed else selected)

    raise ValueError("unsupported extraction family")


_FAMILY_COMPLEXITY = {
    "polyphase_extract": 2,
    "subgrid_extract": 2,
    "line_dedupe": 2,
    "line_select": 3,
    "color_line_select": 3,
    "row_column_select": 4,
    "separator_remove": 3,
    "panel_select": 4,
    "panel_combine": 6,
    "panel_pair_mask": 6,
    "bounding_box_extract": 4,
    "mask_extract": 5,
    "object_crop": 5,
    "object_pack": 7,
    "object_serialize": 7,
}


def _complexity(program: Mapping[str, Any]) -> int:
    parameters = program["parameters"]
    nondefault = sum(
        value not in (False, 0, 1, "mode", "reading", "raw", "tight")
        for value in parameters.values()
    )
    return _FAMILY_COMPLEXITY[program["family"]] + len(parameters) + nondefault


def _json_grid(grid: Grid) -> list[list[int]]:
    return [list(row) for row in grid]


def compile_task(task: Mapping[str, Any], limits: Mapping[str, int] | None = None) -> list[dict[str, Any]]:
    """Compile exact-replay extraction candidates from a sanitized ARC task.

    The returned list is deterministic and contains one representative per
    exact test-behaviour class.  Any malformed task, exhausted finite budget,
    excess object count, or candidate cap violation returns ``[]``; no partial
    enumeration is ever exposed.
    """

    try:
        resolved_limits = _parse_limits(limits)
        train, test = _sanitize(task, resolved_limits)
        programs = _enumerate_programs()
        if len(programs) > resolved_limits.max_programs:
            return []
        planned = len(programs) * (len(train) + len(test))
        if planned > resolved_limits.max_executions:
            return []

        admitted: list[tuple[dict[str, Any], tuple[Grid, ...], tuple[Grid, ...], int]] = []
        executions = 0
        for program in programs:
            replay: list[Grid] = []
            exact = True
            try:
                for source, target in train:
                    executions += 1
                    if executions > resolved_limits.max_executions:
                        return []
                    produced = _execute(source, program, resolved_limits.max_objects)
                    if produced != target:
                        exact = False
                        break
                    replay.append(produced)
                if not exact:
                    continue
                predictions: list[Grid] = []
                for source in test:
                    executions += 1
                    if executions > resolved_limits.max_executions:
                        return []
                    predictions.append(_execute(source, program, resolved_limits.max_objects))
            except (KeyError, TypeError, ValueError, IndexError, ZeroDivisionError):
                continue
            admitted.append((program, tuple(replay), tuple(predictions), _complexity(program)))
            if len(admitted) > resolved_limits.max_exact_programs:
                return []

        by_behavior: dict[str, list[tuple[dict[str, Any], tuple[Grid, ...], tuple[Grid, ...], int]]] = {}
        for candidate in admitted:
            key = _canonical(candidate[2])
            by_behavior.setdefault(key, []).append(candidate)
        if len(by_behavior) > resolved_limits.max_candidates:
            return []

        result: list[dict[str, Any]] = []
        for behavior_key in sorted(by_behavior):
            group = sorted(
                by_behavior[behavior_key],
                key=lambda item: (item[3], item[0]["family"], _canonical(item[0])),
            )
            representative, replay, predictions, complexity = group[0]
            result.append(
                {
                    "family": representative["family"],
                    "program": json.loads(_canonical(representative)),
                    "train_outputs": [_json_grid(grid) for grid in replay],
                    "test_outputs": [_json_grid(grid) for grid in predictions],
                    "complexity": complexity,
                    "evidence": {
                        "all_demos_exact": True,
                        "demonstrations": len(train),
                        "equivalent_programs": len(group),
                        "equivalent_families": sorted({item[0]["family"] for item in group}),
                    },
                }
            )
        result.sort(
            key=lambda item: (
                item["complexity"],
                item["family"],
                _canonical(item["program"]),
                _canonical(item["test_outputs"]),
            )
        )
        return result
    except (KeyError, TypeError, ValueError, IndexError, OverflowError):
        return []


__all__ = ["compile_task"]
