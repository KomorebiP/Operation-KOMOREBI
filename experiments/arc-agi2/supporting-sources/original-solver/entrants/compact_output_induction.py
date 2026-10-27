"""Bounded task-local induction for compact ARC outputs.

The entrant searches a finite collection of executable scene programs for
selection, normalization, ordering, layering, and serialization.  Programs
are admitted only when they reproduce every labelled demonstration exactly;
their complete behavior on all test *inputs* is then quotiented before any
candidate is returned.  Test labels, task identifiers, fingerprints, solution
stores, and corpus-global lookup tables are deliberately outside the API.

All selectors are relational.  Ambiguous modes, object extrema, scene roles,
topological orders, decompositions, and exhausted search caps fail closed.

Author: Komorebi P.
"""

from __future__ import annotations

from collections import Counter, defaultdict, deque
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
import itertools
import json
from typing import Any


Grid = tuple[tuple[int, ...], ...]
JSONGrid = list[list[int]]
SCHEMA = "komorebi.pr_lasm.block14.compact_output_program"
SCHEMA_VERSION = 1


class Undefined(ValueError):
    """A relational program is not uniquely defined for an input."""


@dataclass(frozen=True, slots=True)
class Limits:
    max_side: int = 30
    max_examples: int = 16
    max_total_cells: int = 60_000
    max_objects: int = 96
    max_panels: int = 25
    max_programs: int = 90_000
    max_executions: int = 500_000
    max_exact_programs: int = 90_000
    max_candidates: int = 192

    @classmethod
    def parse(cls, value: Any) -> "Limits":
        if value is None:
            return cls()
        if not isinstance(value, Mapping):
            raise TypeError("limits must be a mapping or None")
        compatibility = {
            "candidate_cap": "max_candidates",
            "max_total_candidates": "max_candidates",
            "time_limit": None,
            "time_limit_seconds": None,
            "max_replay_calls": None,
            "max_replay_stages": None,
            "max_trace_bytes": None,
        }
        allowed = set(cls.__dataclass_fields__) | set(compatibility)
        unknown = set(value) - allowed
        if unknown:
            raise ValueError(f"unknown limits: {sorted(unknown)}")
        chosen: dict[str, int] = {}
        for key, raw in value.items():
            target = compatibility.get(key, key)
            if target is None:
                continue
            if isinstance(raw, bool) or not isinstance(raw, int) or raw < 1:
                raise ValueError("finite limits must be positive integers")
            if target in chosen:
                chosen[target] = min(chosen[target], int(raw))
            else:
                chosen[target] = int(raw)
        return cls(**chosen)


@dataclass(frozen=True, slots=True)
class Object:
    cells: tuple[tuple[int, int], ...]
    y0: int
    y1: int
    x0: int
    x1: int
    colors: tuple[int, ...]

    @property
    def area(self) -> int:
        return len(self.cells)

    @property
    def height(self) -> int:
        return self.y1 - self.y0 + 1

    @property
    def width(self) -> int:
        return self.x1 - self.x0 + 1

    @property
    def box(self) -> int:
        return self.height * self.width


@dataclass(frozen=True, slots=True)
class PanelSet:
    panels: tuple[Grid, ...]
    rows: int
    cols: int
    separator: int | None


def _canonical(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    )


def _grid(value: Any, max_side: int = 30) -> Grid:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise TypeError("grid must be a row sequence")
    if not value or len(value) > max_side:
        raise ValueError("invalid grid height")
    rows: list[tuple[int, ...]] = []
    width: int | None = None
    for raw_row in value:
        if not isinstance(raw_row, Sequence) or isinstance(
            raw_row, (str, bytes, bytearray)
        ):
            raise TypeError("grid row must be a sequence")
        if width is None:
            width = len(raw_row)
        if not width or width > max_side or len(raw_row) != width:
            raise ValueError("grid must be nonempty and rectangular")
        row: list[int] = []
        for cell in raw_row:
            if isinstance(cell, bool) or not isinstance(cell, int) or not 0 <= cell <= 9:
                raise ValueError("ARC cells must be integers in [0, 9]")
            row.append(int(cell))
        rows.append(tuple(row))
    return tuple(rows)


def _plain(value: Grid) -> JSONGrid:
    return [list(row) for row in value]


def _shape(value: Grid) -> tuple[int, int]:
    return len(value), len(value[0])


def _sanitize(
    task: Any, limits: Limits
) -> tuple[tuple[tuple[Grid, Grid], ...], tuple[Grid, ...]]:
    if not isinstance(task, Mapping):
        raise TypeError("task must be a mapping")
    raw_train, raw_test = task["train"], task["test"]
    if (
        not isinstance(raw_train, Sequence)
        or isinstance(raw_train, (str, bytes, bytearray))
        or not raw_train
        or not isinstance(raw_test, Sequence)
        or isinstance(raw_test, (str, bytes, bytearray))
        or not raw_test
        or len(raw_train) + len(raw_test) > limits.max_examples
    ):
        raise ValueError("invalid task arity")
    cells = 0
    train: list[tuple[Grid, Grid]] = []
    for example in raw_train:
        if not isinstance(example, Mapping):
            raise TypeError("training records must be mappings")
        source = _grid(example["input"], limits.max_side)
        target = _grid(example["output"], limits.max_side)
        cells += len(source) * len(source[0]) + len(target) * len(target[0])
        train.append((source, target))
    tests: list[Grid] = []
    for example in raw_test:
        if not isinstance(example, Mapping):
            raise TypeError("test records must be mappings")
        # Intentionally request exactly one test field.  A mapping may contain
        # attached labels or metadata, but they are structurally unobservable.
        source = _grid(example["input"], limits.max_side)
        cells += len(source) * len(source[0])
        tests.append(source)
    if cells > limits.max_total_cells:
        raise ValueError("task cell budget exceeded")
    return tuple(train), tuple(tests)


def _strict_mode(values: Iterable[int]) -> int:
    counts = Counter(values)
    if not counts:
        raise Undefined("empty color population")
    best = max(counts.values())
    winners = sorted(color for color, count in counts.items() if count == best)
    if len(winners) != 1:
        raise Undefined("modal color is tied")
    return winners[0]


@lru_cache(maxsize=8192)
def _background(value: Grid, role: str) -> int:
    if role == "mode":
        return _strict_mode(cell for row in value for cell in row)
    if role == "border":
        border = list(value[0]) + list(value[-1])
        border += [row[0] for row in value[1:-1]]
        border += [row[-1] for row in value[1:-1]]
        return _strict_mode(border)
    if role == "corners":
        return _strict_mode((value[0][0], value[0][-1], value[-1][0], value[-1][-1]))
    if role == "zero":
        return 0
    raise Undefined("unknown background role")


def _role_color(value: Grid, role: str, *, excluded: Iterable[int] = ()) -> int:
    excluded_set = set(excluded)
    counts = Counter(cell for row in value for cell in row if cell not in excluded_set)
    if not counts:
        raise Undefined("color role has no population")
    if role == "unique":
        if len(counts) != 1:
            raise Undefined("color role is not unique")
        return next(iter(counts))
    desired = min(counts.values()) if role == "rarest" else max(counts.values())
    if role not in {"rarest", "most"}:
        raise Undefined("unknown color role")
    winners = sorted(color for color, count in counts.items() if count == desired)
    if len(winners) != 1:
        raise Undefined("color-frequency role is tied")
    return winners[0]


def _d4(value: Grid, operation: str) -> Grid:
    if operation == "identity":
        return value
    if operation == "rot90":
        return tuple(
            tuple(value[len(value) - 1 - row][col] for row in range(len(value)))
            for col in range(len(value[0]))
        )
    if operation == "rot180":
        return tuple(tuple(reversed(row)) for row in reversed(value))
    if operation == "rot270":
        return _d4(_d4(_d4(value, "rot90"), "rot90"), "rot90")
    if operation == "flip_h":
        return tuple(tuple(reversed(row)) for row in value)
    if operation == "flip_v":
        return tuple(reversed(value))
    if operation == "transpose":
        return tuple(
            tuple(value[row][col] for row in range(len(value)))
            for col in range(len(value[0]))
        )
    if operation == "anti_transpose":
        return _d4(_d4(value, "transpose"), "rot180")
    raise Undefined("unknown D4 operation")


_D4 = (
    "identity",
    "rot90",
    "rot180",
    "rot270",
    "flip_h",
    "flip_v",
    "transpose",
    "anti_transpose",
)


def _bbox(cells: Iterable[tuple[int, int]]) -> tuple[int, int, int, int]:
    points = tuple(cells)
    if not points:
        raise Undefined("empty support")
    return (
        min(row for row, _ in points),
        max(row for row, _ in points),
        min(col for _, col in points),
        max(col for _, col in points),
    )


def _crop(value: Grid, box: tuple[int, int, int, int]) -> Grid:
    y0, y1, x0, x1 = box
    if not (0 <= y0 <= y1 < len(value) and 0 <= x0 <= x1 < len(value[0])):
        raise Undefined("crop lies outside the source")
    return tuple(tuple(value[row][x0 : x1 + 1]) for row in range(y0, y1 + 1))


def _crop_nonbackground(value: Grid, background: int) -> Grid:
    cells = [
        (row, col)
        for row, source_row in enumerate(value)
        for col, cell in enumerate(source_row)
        if cell != background
    ]
    return _crop(value, _bbox(cells))


def _offsets(mode: str) -> tuple[tuple[int, int], ...]:
    if mode.endswith("4"):
        return ((-1, 0), (1, 0), (0, -1), (0, 1))
    if mode.endswith("8"):
        return (
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1),
        )
    if mode.endswith("r2") or mode.endswith("r3"):
        radius = int(mode[-1])
        return tuple(
            (dr, dc)
            for dr in range(-radius, radius + 1)
            for dc in range(-radius, radius + 1)
            if dr or dc
        )
    raise Undefined("unknown connectivity")


@lru_cache(maxsize=16384)
def _objects(value: Grid, background: int, mode: str, cap: int = 96) -> tuple[Object, ...]:
    if mode == "color_layers":
        result = []
        for color in sorted({cell for row in value for cell in row} - {background}):
            cells = tuple(
                (row, col)
                for row, source_row in enumerate(value)
                for col, cell in enumerate(source_row)
                if cell == color
            )
            y0, y1, x0, x1 = _bbox(cells)
            result.append(Object(cells, y0, y1, x0, x1, (color,)))
        if not result:
            raise Undefined("no foreground color layers")
        return tuple(result)
    separate = mode.startswith("mono")
    offsets = _offsets(mode)
    remaining = {
        (row, col)
        for row, source_row in enumerate(value)
        for col, cell in enumerate(source_row)
        if cell != background
    }
    result: list[Object] = []
    while remaining:
        if len(result) >= cap:
            raise Undefined("object cap exceeded")
        seed = min(remaining)
        seed_color = value[seed[0]][seed[1]]
        remaining.remove(seed)
        queue = [seed]
        cells = {seed}
        while queue:
            row, col = queue.pop()
            for dr, dc in offsets:
                point = row + dr, col + dc
                if point not in remaining:
                    continue
                if separate and value[point[0]][point[1]] != seed_color:
                    continue
                remaining.remove(point)
                cells.add(point)
                queue.append(point)
        y0, y1, x0, x1 = _bbox(cells)
        colors = tuple(sorted({value[row][col] for row, col in cells}))
        result.append(Object(tuple(sorted(cells)), y0, y1, x0, x1, colors))
    if not result:
        raise Undefined("no foreground objects")
    return tuple(sorted(result, key=lambda obj: (obj.y0, obj.x0, obj.y1, obj.x1, obj.colors)))


@lru_cache(maxsize=32768)
def _object_crop(value: Grid, obj: Object, background: int, render: str) -> Grid:
    if render == "raw":
        return _crop(value, (obj.y0, obj.y1, obj.x0, obj.x1))
    cells = set(obj.cells)
    if render == "isolate":
        return tuple(
            tuple(
                value[row][col] if (row, col) in cells else background
                for col in range(obj.x0, obj.x1 + 1)
            )
            for row in range(obj.y0, obj.y1 + 1)
        )
    if render == "support_object_color":
        if len(obj.colors) != 1:
            raise Undefined("object color is not unique")
        color = obj.colors[0]
        return tuple(
            tuple(
                color if (row, col) in cells else background
                for col in range(obj.x0, obj.x1 + 1)
            )
            for row in range(obj.y0, obj.y1 + 1)
        )
    raise Undefined("unknown object rendering")


def _support(value: Grid, background: int) -> tuple[tuple[bool, ...], ...]:
    return tuple(tuple(cell != background for cell in row) for row in value)


def _symmetry_count(mask: tuple[tuple[bool, ...], ...]) -> int:
    as_int = tuple(tuple(int(cell) for cell in row) for row in mask)
    return sum(_d4(as_int, op) == as_int for op in _D4[1:])


def _holes(mask: tuple[tuple[bool, ...], ...]) -> int:
    height, width = len(mask), len(mask[0])
    remaining = {(row, col) for row in range(height) for col in range(width) if not mask[row][col]}
    count = 0
    while remaining:
        seed = min(remaining)
        remaining.remove(seed)
        queue = [seed]
        enclosed = True
        while queue:
            row, col = queue.pop()
            if row in {0, height - 1} or col in {0, width - 1}:
                enclosed = False
            for point in ((row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)):
                if point in remaining:
                    remaining.remove(point)
                    queue.append(point)
        count += int(enclosed)
    return count


def _internal_components(obj: Object, connectivity: int = 4) -> int:
    remaining = set(obj.cells)
    count = 0
    offsets = _offsets("support8" if connectivity == 8 else "support4")
    while remaining:
        count += 1
        queue = [remaining.pop()]
        while queue:
            row, col = queue.pop()
            for dr, dc in offsets:
                point = row + dr, col + dc
                if point in remaining:
                    remaining.remove(point)
                    queue.append(point)
    return count


@lru_cache(maxsize=65536)
def _feature(value: Grid, obj: Object, name: str) -> int | Fraction:
    mask = tuple(
        tuple((row, col) in set(obj.cells) for col in range(obj.x0, obj.x1 + 1))
        for row in range(obj.y0, obj.y1 + 1)
    )
    if name == "area":
        return obj.area
    if name == "box":
        return obj.box
    if name == "height":
        return obj.height
    if name == "width":
        return obj.width
    if name == "density":
        return Fraction(obj.area, obj.box)
    if name == "colors":
        return len(obj.colors)
    if name == "symmetry":
        return _symmetry_count(mask)
    if name == "holes":
        return _holes(mask)
    if name == "components4":
        return _internal_components(obj, 4)
    if name == "components8":
        return _internal_components(obj, 8)
    if name == "border_touch":
        return sum(
            (
                obj.y0 == 0,
                obj.y1 == len(value) - 1,
                obj.x0 == 0,
                obj.x1 == len(value[0]) - 1,
            )
        )
    if name == "top":
        return -obj.y0
    if name == "left":
        return -obj.x0
    if name == "bottom":
        return obj.y1
    if name == "right":
        return obj.x1
    raise Undefined("unknown object feature")


def _select_object(value: Grid, objects: Sequence[Object], selector: Mapping[str, Any]) -> Object:
    if not objects:
        raise Undefined("empty object population")
    kind = selector["kind"]
    if kind == "lexicographic":
        keys: list[tuple[int | Fraction, ...]] = []
        for obj in objects:
            record: list[int | Fraction] = []
            for item in selector["keys"]:
                score = _feature(value, obj, str(item["feature"]))
                record.append(score if item["direction"] == "max" else -score)
            keys.append(tuple(record))
        desired = max(keys)
        winners = [obj for obj, score in zip(objects, keys) if score == desired]
    elif kind == "unique_predicate":
        predicate = str(selector["predicate"])
        winners = []
        for obj in objects:
            mask = tuple(
                tuple((row, col) in set(obj.cells) for col in range(obj.x0, obj.x1 + 1))
                for row in range(obj.y0, obj.y1 + 1)
            )
            yes = {
                "hollow": _holes(mask) > 0,
                "symmetric_h": _d4(tuple(tuple(int(x) for x in row) for row in mask), "flip_h")
                == tuple(tuple(int(x) for x in row) for row in mask),
                "symmetric_v": _d4(tuple(tuple(int(x) for x in row) for row in mask), "flip_v")
                == tuple(tuple(int(x) for x in row) for row in mask),
                "symmetric_180": _d4(
                    tuple(tuple(int(x) for x in row) for row in mask), "rot180"
                )
                == tuple(tuple(int(x) for x in row) for row in mask),
                "multicolor": len(obj.colors) > 1,
                "square": obj.height == obj.width,
            }.get(predicate)
            if yes is None:
                raise Undefined("unknown object predicate")
            if yes:
                winners.append(obj)
    else:
        raise Undefined("unknown object selector")
    if len(winners) != 1:
        raise Undefined("object selector is tied")
    return winners[0]


def _bands(size: int, cuts: set[int]) -> tuple[tuple[int, int], ...]:
    result: list[tuple[int, int]] = []
    index = 0
    while index < size:
        while index < size and index in cuts:
            index += 1
        if index == size:
            break
        end = index
        while end + 1 < size and end + 1 not in cuts:
            end += 1
        result.append((index, end))
        index = end + 1
    return tuple(result)


@lru_cache(maxsize=4096)
def _split_uniform(value: Grid, separator_role: str, max_panels: int) -> PanelSet:
    height, width = _shape(value)
    palette = sorted({cell for row in value for cell in row})
    if separator_role == "background":
        candidates = [_background(value, "mode")]
    elif separator_role == "unique_uniform":
        candidates = palette
    else:
        raise Undefined("unknown separator role")
    interpretations: list[PanelSet] = []
    for separator in candidates:
        row_cuts = {
            row
            for row in range(1, height - 1)
            if all(value[row][col] == separator for col in range(width))
        }
        col_cuts = {
            col
            for col in range(1, width - 1)
            if all(value[row][col] == separator for row in range(height))
        }
        row_bands, col_bands = _bands(height, row_cuts), _bands(width, col_cuts)
        count = len(row_bands) * len(col_bands)
        if not (row_cuts or col_cuts) or count < 2 or count > max_panels:
            continue
        panels = tuple(
            tuple(
                tuple(value[row][x0 : x1 + 1])
                for row in range(y0, y1 + 1)
            )
            for y0, y1 in row_bands
            for x0, x1 in col_bands
        )
        interpretations.append(PanelSet(panels, len(row_bands), len(col_bands), separator))
    unique = {_canonical((item.rows, item.cols, item.separator, item.panels)): item for item in interpretations}
    if separator_role == "unique_uniform" and len(unique) != 1:
        raise Undefined("uniform separator interpretation is not unique")
    if not unique:
        raise Undefined("uniform separator is absent")
    # The background role already fixes a color, so only one interpretation is possible.
    return next(iter(unique.values()))


@lru_cache(maxsize=4096)
def _split_equal(value: Grid, rows: int, cols: int, max_panels: int) -> PanelSet:
    height, width = _shape(value)
    if rows * cols < 2 or rows * cols > max_panels or height % rows or width % cols:
        raise Undefined("equal partition does not divide the grid")
    ph, pw = height // rows, width // cols
    panels = tuple(
        tuple(
            tuple(value[row][col * pw : (col + 1) * pw])
            for row in range(r * ph, (r + 1) * ph)
        )
        for r in range(rows)
        for col in range(cols)
    )
    return PanelSet(panels, rows, cols, None)


def _panels(value: Grid, spec: Mapping[str, Any], max_panels: int = 25) -> PanelSet:
    if spec["kind"] == "uniform":
        return _split_uniform(value, str(spec["separator_role"]), max_panels)
    if spec["kind"] == "equal":
        return _split_equal(value, int(spec["rows"]), int(spec["cols"]), max_panels)
    raise Undefined("unknown panel partition")


def _panel_normalize(panel: Grid, root: Grid, panel_set: PanelSet, mode: str) -> Grid:
    if mode == "identity":
        return panel
    if mode == "crop_root_background":
        return _crop_nonbackground(panel, _background(root, "mode"))
    if mode == "crop_panel_background":
        return _crop_nonbackground(panel, _background(panel, "mode"))
    if mode == "crop_separator":
        if panel_set.separator is None:
            raise Undefined("partition has no carried separator")
        return _crop_nonbackground(panel, panel_set.separator)
    raise Undefined("unknown panel normalization")


def _layout(values: Sequence[Grid], rows: int, cols: int) -> Grid:
    if len(values) != rows * cols:
        raise Undefined("layout arity mismatch")
    row_heights: list[int] = []
    col_widths: list[int] = []
    for row in range(rows):
        heights = {len(values[row * cols + col]) for col in range(cols)}
        if len(heights) != 1:
            raise Undefined("layout row heights disagree")
        row_heights.append(next(iter(heights)))
    for col in range(cols):
        widths = {len(values[row * cols + col][0]) for row in range(rows)}
        if len(widths) != 1:
            raise Undefined("layout column widths disagree")
        col_widths.append(next(iter(widths)))
    result: list[tuple[int, ...]] = []
    for panel_row in range(rows):
        for inner_row in range(row_heights[panel_row]):
            row: list[int] = []
            for panel_col in range(cols):
                row.extend(values[panel_row * cols + panel_col][inner_row])
            result.append(tuple(row))
    return tuple(result)


def _panel_feature(panel: Grid, root_background: int, name: str) -> int | Fraction:
    foreground = [(r, c) for r, row in enumerate(panel) for c, v in enumerate(row) if v != root_background]
    if name == "area":
        return len(panel) * len(panel[0])
    if name == "foreground":
        return len(foreground)
    if name == "palette":
        return len({cell for row in panel for cell in row})
    if name == "bbox":
        if not foreground:
            return 0
        y0, y1, x0, x1 = _bbox(foreground)
        return (y1 - y0 + 1) * (x1 - x0 + 1)
    if name == "density":
        if not foreground:
            return Fraction(0, 1)
        y0, y1, x0, x1 = _bbox(foreground)
        return Fraction(len(foreground), (y1 - y0 + 1) * (x1 - x0 + 1))
    raise Undefined("unknown panel feature")


def _select_panel(panel_set: PanelSet, root: Grid, selector: Mapping[str, Any]) -> Grid:
    background = _background(root, "mode")
    name, direction = str(selector["feature"]), str(selector["direction"])
    scores = [_panel_feature(panel, background, name) for panel in panel_set.panels]
    desired = max(scores) if direction == "max" else min(scores)
    winners = [panel for panel, score in zip(panel_set.panels, scores) if score == desired]
    if len(winners) != 1:
        raise Undefined("panel selector is tied")
    return winners[0]


def _dense_rectangle_layout(value: Grid, program: Mapping[str, Any]) -> Grid:
    background = _background(value, str(program["background_role"]))
    min_side, min_area = int(program["min_side"]), int(program["min_area"])
    # Dense noise scenes can contain nearly one component per cell.  The
    # finite raster bound (900 cells) is the natural safe cap here; relevant
    # rectangles are filtered immediately below.
    objects = _objects(value, background, "mono4", cap=900)
    rectangles: list[Object] = []
    for obj in objects:
        if len(obj.colors) != 1 or obj.height < min_side or obj.width < min_side or obj.area < min_area:
            continue
        if obj.area != obj.box:
            continue
        rectangles.append(obj)
    if not 4 <= len(rectangles) <= 25:
        raise Undefined("solid rectangle population is outside the layout grammar")

    def interval_groups(items: Sequence[Object], axis: str) -> list[list[Object]]:
        groups: list[list[Object]] = []
        ordered = sorted(items, key=lambda obj: (obj.y0, obj.x0) if axis == "rows" else (obj.x0, obj.y0))
        for obj in ordered:
            start, end = (obj.y0, obj.y1) if axis == "rows" else (obj.x0, obj.x1)
            matching = []
            for index, group in enumerate(groups):
                low = max((member.y0 if axis == "rows" else member.x0) for member in group)
                high = min((member.y1 if axis == "rows" else member.x1) for member in group)
                if max(low, start) <= min(high, end):
                    matching.append(index)
            if len(matching) > 1:
                raise Undefined("rectangle bands overlap ambiguously")
            if matching:
                groups[matching[0]].append(obj)
            else:
                groups.append([obj])
        return groups

    row_groups, col_groups = interval_groups(rectangles, "rows"), interval_groups(rectangles, "cols")
    if len(row_groups) * len(col_groups) != len(rectangles) or min(len(row_groups), len(col_groups)) < 2:
        raise Undefined("rectangles do not form a complete lattice")
    result: list[tuple[int, ...]] = []
    for row_group in row_groups:
        row: list[int] = []
        for col_group in col_groups:
            common = [obj for obj in row_group if obj in col_group]
            if len(common) != 1 or len(common[0].colors) != 1:
                raise Undefined("rectangle lattice cell is not unique")
            row.append(common[0].colors[0])
        result.append(tuple(row))
    return tuple(result)


def _anchor_overlay(value: Grid, program: Mapping[str, Any]) -> Grid:
    background = _background(value, str(program["background_role"]))
    connectivity = int(program["connectivity"])
    adjacency = int(program["adjacency"])
    payload_mode = "mono8" if connectivity == 8 else "mono4"
    palette = sorted({cell for row in value for cell in row} - {background})
    interpretations: list[tuple[int, list[tuple[Object, tuple[int, int]]]]] = []
    for marker in palette:
        marker_cells = {
            (row, col)
            for row, source_row in enumerate(value)
            for col, cell in enumerate(source_row)
            if cell == marker
        }
        masked = tuple(
            tuple(background if cell == marker else cell for cell in row) for row in value
        )
        try:
            payloads = _objects(masked, background, payload_mode)
        except Undefined:
            continue
        attached: list[tuple[Object, tuple[int, int]]] = []
        used: set[tuple[int, int]] = set()
        valid = True
        for obj in payloads:
            neighboring = {
                marker_cell
                for marker_cell in marker_cells
                if any(
                    (
                        max(abs(row - marker_cell[0]), abs(col - marker_cell[1])) <= adjacency
                        if connectivity == 8
                        else abs(row - marker_cell[0]) + abs(col - marker_cell[1]) <= adjacency
                    )
                    for row, col in obj.cells
                )
            }
            if len(neighboring) != 1:
                valid = False
                break
            anchor = next(iter(neighboring))
            attached.append((obj, anchor))
            used.add(anchor)
        if (
            valid
            and len(attached) >= 3
            and used == marker_cells
            and len({obj.colors[0] for obj, _ in attached if len(obj.colors) == 1}) >= 2
        ):
            interpretations.append((marker, attached))
    if len(interpretations) != 1:
        raise Undefined("anchor-marker color is not unique")
    marker, attached = interpretations[0]
    order = str(program["priority"])
    if order == "anchor_scan":
        attached.sort(key=lambda item: (item[1], item[0].y0, item[0].x0, item[0].colors))
    elif order == "anchor_reverse":
        attached.sort(key=lambda item: (item[1], item[0].y0, item[0].x0, item[0].colors), reverse=True)
    elif order == "small_first":
        attached.sort(key=lambda item: (item[0].area, item[1], item[0].colors))
    elif order == "large_first":
        attached.sort(key=lambda item: (-item[0].area, item[1], item[0].colors))
    else:
        raise Undefined("unknown anchor overlay priority")
    relative: dict[tuple[int, int], int] = {(0, 0): marker}
    for obj, anchor in attached:
        for row, col in obj.cells:
            relative[(row - anchor[0], col - anchor[1])] = value[row][col]
    y0, y1, x0, x1 = _bbox(relative)
    output = tuple(
        tuple(relative.get((row, col), background) for col in range(x0, x1 + 1))
        for row in range(y0, y1 + 1)
    )
    return _d4(output, str(program["transform"]))


@dataclass(frozen=True, slots=True)
class _Line:
    color: int
    kind: str
    parameter: int
    cells: frozenset[tuple[int, int]]


def _line_cells(height: int, width: int, kind: str, parameter: int) -> frozenset[tuple[int, int]]:
    if kind == "row":
        return frozenset((parameter, col) for col in range(width))
    if kind == "col":
        return frozenset((row, parameter) for row in range(height))
    if kind == "diag_down":
        return frozenset(
            (row, col) for row in range(height) for col in range(width) if row - col == parameter
        )
    if kind == "diag_up":
        return frozenset(
            (row, col) for row in range(height) for col in range(width) if row + col == parameter
        )
    raise Undefined("unknown line kind")


def _line_layer_order(value: Grid, program: Mapping[str, Any]) -> Grid:
    background = _background(value, str(program["background_role"]))
    height, width = _shape(value)
    lines: list[_Line] = []
    for color in sorted({cell for row in value for cell in row} - {background}):
        points = {(row, col) for row in range(height) for col in range(width) if value[row][col] == color}
        if len(points) < 2:
            raise Undefined("line has insufficient visible support")
        models: list[tuple[str, int]] = []
        rows, cols = {row for row, _ in points}, {col for _, col in points}
        downs, ups = {row - col for row, col in points}, {row + col for row, col in points}
        if len(rows) == 1:
            models.append(("row", next(iter(rows))))
        if len(cols) == 1:
            models.append(("col", next(iter(cols))))
        if len(downs) == 1:
            models.append(("diag_down", next(iter(downs))))
        if len(ups) == 1:
            models.append(("diag_up", next(iter(ups))))
        models = [model for model in models if len(_line_cells(height, width, *model)) >= 3]
        if len(models) != 1:
            raise Undefined("line geometry is ambiguous")
        kind, parameter = models[0]
        cells = _line_cells(height, width, kind, parameter)
        if not points <= cells:
            raise Undefined("visible line cells violate their model")
        lines.append(_Line(color, kind, parameter, cells))
    if not 2 <= len(lines) <= 9:
        raise Undefined("line layer count is outside the grammar")
    edges: set[tuple[int, int]] = set()
    # Several ideal lines may cross at one lattice cell.  The visible color is
    # above every other participant there, which supplies all pairwise edges
    # without incorrectly treating the winner as an unrelated third color.
    for row in range(height):
        for col in range(width):
            participants = [line for line in lines if (row, col) in line.cells]
            if len(participants) < 2:
                continue
            observed = value[row][col]
            winners = [line for line in participants if line.color == observed]
            if len(winners) != 1:
                raise Undefined("line crossing has no unique visible layer")
            winner = winners[0]
            edges.update(
                (line.color, winner.color) for line in participants if line is not winner
            )
    if not edges:
        raise Undefined("line layers have no ordering evidence")
    remaining = {line.color for line in lines}
    ordered: list[int] = []
    while remaining:
        available = sorted(
            color
            for color in remaining
            if all(lower not in remaining for lower, upper in edges if upper == color)
        )
        if len(available) == 1:
            chosen = available[0]
        else:
            # Parallel layers never cross, so a task may serialize them by
            # their geometric position.  This policy is explicit in the
            # program; distinct policies survive as distinct test behaviors
            # and therefore trigger tournament-level ambiguity abstention.
            records = [next(line for line in lines if line.color == color) for color in available]
            if len({line.kind for line in records}) != 1:
                raise Undefined("line-layer partial order is not unique")
            parallel_order = str(program["parallel_order"])
            records.sort(key=lambda line: line.parameter)
            if parallel_order == "descending":
                records.reverse()
            elif parallel_order != "ascending":
                raise Undefined("unknown parallel line order")
            chosen = records[0].color
        ordered.append(chosen)
        remaining.remove(chosen)
    if str(program["direction"]) == "top_to_bottom":
        ordered.reverse()
    elif str(program["direction"]) != "bottom_to_top":
        raise Undefined("unknown layer direction")
    if str(program["axis"]) == "row":
        return (tuple(ordered),)
    if str(program["axis"]) == "col":
        return tuple((color,) for color in ordered)
    raise Undefined("unknown serialization axis")


def _uniform_macro_masks(value: Grid, background: int) -> list[tuple[int, Grid, int, int]]:
    result: list[tuple[int, Grid, int, int]] = []
    for color in sorted({cell for row in value for cell in row} - {background}):
        points = [(r, c) for r, row in enumerate(value) for c, cell in enumerate(row) if cell == color]
        y0, y1, x0, x1 = _bbox(points)
        height, width = y1 - y0 + 1, x1 - x0 + 1
        for factor_y in range(2, min(10, height) + 1):
            if height % factor_y:
                continue
            for factor_x in range(2, min(10, width) + 1):
                if width % factor_x:
                    continue
                out_h, out_w = height // factor_y, width // factor_x
                if not (2 <= out_h <= 10 and 2 <= out_w <= 10):
                    continue
                mask: list[tuple[int, ...]] = []
                valid = True
                for macro_row in range(out_h):
                    row: list[int] = []
                    for macro_col in range(out_w):
                        block = {
                            value[y0 + macro_row * factor_y + dr][x0 + macro_col * factor_x + dc]
                            == color
                            for dr in range(factor_y)
                            for dc in range(factor_x)
                        }
                        if len(block) != 1:
                            valid = False
                            break
                        row.append(int(next(iter(block))))
                    if not valid:
                        break
                    mask.append(tuple(row))
                if valid and {cell for row in mask for cell in row} == {0, 1}:
                    result.append((color, tuple(mask), factor_y, factor_x))
    # Prefer the coarsest valid representation for each color, then require
    # callers to resolve scene-level ambiguity.
    best: dict[int, tuple[int, Grid, int, int]] = {}
    for record in result:
        color, mask, fy, fx = record
        rank = (len(mask) * len(mask[0]), -(fy * fx), _canonical(mask))
        old = best.get(color)
        if old is None or rank < (len(old[1]) * len(old[1][0]), -(old[2] * old[3]), _canonical(old[1])):
            best[color] = record
    return [best[color] for color in sorted(best)]


def _macro_shape_reduce(value: Grid, program: Mapping[str, Any]) -> Grid:
    background = _background(value, str(program["background_role"]))
    masks = _uniform_macro_masks(value, background)
    if len(masks) != 1:
        raise Undefined("macro support layer is not unique")
    color, mask, _, _ = masks[0]
    true_role = str(program["true_role"])
    if true_role == "mask_color":
        true_color = color
    elif true_role in {"unique_other", "rarest_other", "most_other"}:
        other = [
            cell
            for row in value
            for cell in row
            if cell not in {background, color}
        ]
        role = {"unique_other": "unique", "rarest_other": "rarest", "most_other": "most"}[true_role]
        true_color = _role_color(tuple((tuple(other),)), role) if other else (_ for _ in ()).throw(Undefined("no other color"))
    else:
        raise Undefined("unknown macro render role")
    output = tuple(
        tuple(true_color if cell else background for cell in row) for row in mask
    )
    return _d4(output, str(program["transform"]))


def _macro_mask_payload(value: Grid, program: Mapping[str, Any]) -> Grid:
    background = _background(value, str(program["background_role"]))
    macro_records: list[tuple[int, frozenset[tuple[int, int]], Grid]] = []
    # Macro blocks often touch only at corners.  An 8-connected monochrome
    # carrier keeps that mask together while excluding a distant payload cell
    # that happens to reuse its color.
    for obj in _objects(value, background, "mono8"):
        if len(obj.colors) != 1:
            continue
        isolated = _object_crop(value, obj, background, "isolate")
        for color, mask, _, _ in _uniform_macro_masks(isolated, background):
            macro_records.append((color, frozenset(obj.cells), mask))
    support_objects = _objects(value, background, "support8")
    pairs: list[tuple[Object, Grid]] = []
    for _, macro_cells, mask in macro_records:
        target_shape = _shape(mask)
        for payload in support_objects:
            if set(payload.cells) & macro_cells:
                continue
            if (payload.height, payload.width) != target_shape or len(payload.colors) < 2:
                continue
            raw = _object_crop(value, payload, background, "raw")
            if any(cell == background for row in raw for cell in row):
                continue
            pairs.append((payload, mask))
    unique: dict[str, tuple[Object, Grid]] = {}
    for payload, mask in pairs:
        unique.setdefault(_canonical((payload.cells, mask)), (payload, mask))
    if len(unique) != 1:
        raise Undefined("macro mask/payload pairing is not unique")
    payload, mask = next(iter(unique.values()))
    raw = _object_crop(value, payload, background, "raw")
    keep = str(program["keep"])
    output = tuple(
        tuple(
            raw[row][col]
            if bool(mask[row][col]) == (keep == "occupied")
            else background
            for col in range(len(mask[0]))
        )
        for row in range(len(mask))
    )
    return _d4(output, str(program["transform"]))


def _shape_signature(value: Grid, obj: Object, background: int) -> str:
    crop = _object_crop(value, obj, background, "isolate")
    mask = tuple(tuple(int(cell != background) for cell in row) for row in crop)
    return _canonical(mask)


def _prototype_recovery(value: Grid, program: Mapping[str, Any]) -> Grid:
    background = _background(value, str(program["background_role"]))
    connectivity = int(program["connectivity"])
    mode = "mono8" if connectivity == 8 else "mono4"
    objects = list(_objects(value, background, mode))
    by_color: dict[int, list[Object]] = defaultdict(list)
    for obj in objects:
        if len(obj.colors) != 1:
            raise Undefined("prototype object is not monochrome")
        by_color[obj.colors[0]].append(obj)
    if len(by_color) < 2:
        raise Undefined("prototype scene has too few color roles")
    maximum = max(len(group) for group in by_color.values())
    outer = [group for group in by_color.values() if len(group) == maximum]
    if len(outer) != 1:
        raise Undefined("prototype carrier color is tied")
    group = outer[0]
    frequencies = Counter(_shape_signature(value, obj, background) for obj in group)
    max_frequency = max(frequencies.values())
    modal_signatures = [signature for signature, count in frequencies.items() if count == max_frequency]
    if len(modal_signatures) == 1 and max_frequency > 1:
        desired_signature = modal_signatures[0]
    else:
        scored: dict[tuple[int, int], set[str]] = defaultdict(set)
        for obj in group:
            signature = _shape_signature(value, obj, background)
            crop = _object_crop(value, obj, background, "isolate")
            symmetries = _symmetry_count(_support(crop, background))
            # A single reflection/half-turn is a stronger prototype cue than
            # an over-regular shape invariant under several D4 operations.
            # Area then resolves small repeated decoys.
            scored[(int(symmetries == 1), obj.area)].add(signature)
        desired_score = max(scored)
        if len(scored[desired_score]) != 1:
            raise Undefined("prototype fallback selector is tied")
        desired_signature = next(iter(scored[desired_score]))
    winners = [obj for obj in group if _shape_signature(value, obj, background) == desired_signature]
    rasters = {_object_crop(value, obj, background, "isolate") for obj in winners}
    if len(rasters) != 1:
        raise Undefined("equivalent prototype instances render differently")
    output = next(iter(rasters))
    return _d4(output, str(program["transform"]))


def _sparse_frame_crop(value: Grid, program: Mapping[str, Any]) -> Grid:
    background = _background(value, str(program["background_role"]))
    height, width = _shape(value)
    orientation = str(program["orientation"])
    boxes: list[tuple[int, int, int, int]] = []
    for y0 in range(height - 3):
        for y1 in range(y0 + 3, height):
            for x0 in range(width - 2):
                for x1 in range(x0 + 2, width):
                    corners = (
                        value[y0][x0],
                        value[y0][x1],
                        value[y1][x0],
                        value[y1][x1],
                    )
                    if len(set(corners)) != 1 or corners[0] == background:
                        continue
                    if orientation == "vertical_sides":
                        sides = [value[row][x0] for row in range(y0 + 1, y1)] + [
                            value[row][x1] for row in range(y0 + 1, y1)
                        ]
                    elif orientation == "horizontal_sides":
                        sides = list(value[y0][x0 + 1 : x1]) + list(
                            value[y1][x0 + 1 : x1]
                        )
                    else:
                        raise Undefined("unknown sparse frame orientation")
                    if not sides or len(set(sides)) != 1 or sides[0] in {background, corners[0]}:
                        continue
                    boxes.append((y0, y1, x0, x1))
    if len(boxes) != 1:
        raise Undefined("sparse frame is not unique")
    return _d4(_crop(value, boxes[0]), str(program["transform"]))


def _object_select_crop(value: Grid, program: Mapping[str, Any]) -> Grid:
    background = _background(value, str(program["background_role"]))
    objects = _objects(value, background, str(program["segmentation"]))
    selected = _select_object(value, objects, program["selector"])
    output = _object_crop(value, selected, background, str(program["render"]))
    return _d4(output, str(program["transform"]))


def _role_carried_reparse(value: Grid, program: Mapping[str, Any]) -> Grid:
    background = _background(value, str(program["background_role"]))
    outer_objects = _objects(value, background, str(program["outer_segmentation"]))
    outer = _select_object(value, outer_objects, program["outer_selector"])
    outer_crop = _object_crop(value, outer, background, "raw")
    # The root background is deliberately carried across the crop.  Recomputing
    # a local mode is a different, often incorrect, program.
    inner_objects = _objects(outer_crop, background, str(program["inner_segmentation"]))
    inner = _select_object(outer_crop, inner_objects, program["inner_selector"])
    output = _object_crop(outer_crop, inner, background, "isolate")
    recolor = str(program["recolor"])
    if recolor != "preserve":
        target = _role_color(
            outer_crop,
            {"rarest_foreground": "rarest", "most_foreground": "most"}[recolor],
            excluded=(background,),
        )
        inner_cells = set(inner.cells)
        output = tuple(
            tuple(
                target if (row + inner.y0, col + inner.x0) in inner_cells else background
                for col in range(inner.width)
            )
            for row in range(inner.height)
        )
    return _d4(output, str(program["transform"]))


def _pack_objects(value: Grid, program: Mapping[str, Any]) -> Grid:
    background = _background(value, str(program["background_role"]))
    objects = list(_objects(value, background, str(program["segmentation"])))
    if not 2 <= len(objects) <= 16:
        raise Undefined("object pack arity is outside the grammar")
    order = str(program["order"])
    if order == "row_major":
        objects.sort(key=lambda obj: (obj.y0, obj.x0, obj.y1, obj.x1))
    elif order == "column_major":
        objects.sort(key=lambda obj: (obj.x0, obj.y0, obj.x1, obj.y1))
    elif order == "small_first":
        objects.sort(key=lambda obj: (obj.area, obj.y0, obj.x0))
    elif order == "large_first":
        objects.sort(key=lambda obj: (-obj.area, obj.y0, obj.x0))
    else:
        raise Undefined("unknown object pack order")
    crops = [_object_crop(value, obj, background, str(program["render"])) for obj in objects]
    axis, anchor = str(program["axis"]), str(program["anchor"])
    if axis == "horizontal":
        height = max(len(crop) for crop in crops)
        canvas = [[background for _ in range(sum(len(crop[0]) for crop in crops))] for _ in range(height)]
        offset = 0
        for crop in crops:
            y = {"start": 0, "center": (height - len(crop)) // 2, "end": height - len(crop)}[anchor]
            for row in range(len(crop)):
                for col in range(len(crop[0])):
                    canvas[y + row][offset + col] = crop[row][col]
            offset += len(crop[0])
    elif axis == "vertical":
        width = max(len(crop[0]) for crop in crops)
        canvas = [[background for _ in range(width)] for _ in range(sum(len(crop) for crop in crops))]
        offset = 0
        for crop in crops:
            x = {"start": 0, "center": (width - len(crop[0])) // 2, "end": width - len(crop[0])}[anchor]
            for row in range(len(crop)):
                for col in range(len(crop[0])):
                    canvas[offset + row][x + col] = crop[row][col]
            offset += len(crop)
    else:
        raise Undefined("unknown object pack axis")
    return _d4(tuple(tuple(row) for row in canvas), str(program["transform"]))


def _serialize_objects(value: Grid, program: Mapping[str, Any]) -> Grid:
    background = _background(value, str(program["background_role"]))
    objects = list(_objects(value, background, str(program["segmentation"])))
    if not 2 <= len(objects) <= 25 or any(len(obj.colors) != 1 for obj in objects):
        raise Undefined("object serialization requires monochrome objects")
    order = str(program["order"])
    if order == "row_major":
        objects.sort(key=lambda obj: (obj.y0, obj.x0))
    elif order == "column_major":
        objects.sort(key=lambda obj: (obj.x0, obj.y0))
    elif order == "small_first":
        objects.sort(key=lambda obj: (obj.area, obj.y0, obj.x0))
    elif order == "large_first":
        objects.sort(key=lambda obj: (-obj.area, obj.y0, obj.x0))
    else:
        raise Undefined("unknown serialization order")
    colors = [obj.colors[0] for obj in objects]
    if str(program["axis"]) == "row":
        return (tuple(colors),)
    if str(program["axis"]) == "col":
        return tuple((color,) for color in colors)
    raise Undefined("unknown serialization axis")


def _count_render(value: Grid, program: Mapping[str, Any]) -> Grid:
    background = _background(value, str(program["background_role"]))
    objects = _objects(value, background, str(program["segmentation"]))
    count = len(objects)
    if not 1 <= count <= 30:
        raise Undefined("count is outside ARC output bounds")
    color_role = str(program["color_role"])
    if color_role == "unique_foreground":
        color = _role_color(value, "unique", excluded=(background,))
    elif color_role == "rarest_foreground":
        color = _role_color(value, "rarest", excluded=(background,))
    elif color_role == "most_foreground":
        color = _role_color(value, "most", excluded=(background,))
    else:
        raise Undefined("unknown count color role")
    shape = str(program["shape"])
    if shape == "row":
        return (tuple(color for _ in range(count)),)
    if shape == "col":
        return tuple((color,) for _ in range(count))
    if shape == "square":
        side = int(count ** 0.5)
        if side * side != count:
            raise Undefined("count is not square")
        return tuple(tuple(color for _ in range(side)) for _ in range(side))
    raise Undefined("unknown count rendering")


def _panel_program(value: Grid, program: Mapping[str, Any]) -> Grid:
    panel_set = _panels(value, program["partition"])
    op = str(program["op"])
    if op == "panel_normalize_layout":
        normalized = [
            _d4(
                _panel_normalize(panel, value, panel_set, str(program["normalization"])),
                str(program["panel_transform"]),
            )
            for panel in panel_set.panels
        ]
        return _d4(_layout(normalized, panel_set.rows, panel_set.cols), str(program["transform"]))
    if op == "panel_select":
        selected = _select_panel(panel_set, value, program["selector"])
        normalized = _panel_normalize(selected, value, panel_set, str(program["normalization"]))
        return _d4(normalized, str(program["transform"]))
    if op in {"panel_overlay", "panel_boolean"}:
        arrays = [
            _panel_normalize(panel, value, panel_set, str(program["normalization"]))
            for panel in panel_set.panels
        ]
        if len({_shape(array) for array in arrays}) != 1:
            raise Undefined("panel arrays are not aligned")
        background = _background(value, "mode")
        height, width = _shape(arrays[0])
        if op == "panel_overlay":
            order = range(len(arrays)) if program["priority"] == "forward" else reversed(range(len(arrays)))
            canvas = [[background for _ in range(width)] for _ in range(height)]
            for index in order:
                for row in range(height):
                    for col in range(width):
                        if arrays[index][row][col] != background:
                            canvas[row][col] = arrays[index][row][col]
            output = tuple(tuple(row) for row in canvas)
        else:
            combine = str(program["combine"])
            masks = [_support(array, background) for array in arrays]
            true_color = _role_color(value, str(program["true_role"]), excluded=(background,))
            result: list[tuple[int, ...]] = []
            for row in range(height):
                rendered: list[int] = []
                for col in range(width):
                    count = sum(mask[row][col] for mask in masks)
                    yes = {
                        "or": count >= 1,
                        "and": count == len(masks),
                        "xor": count % 2 == 1,
                        "exactly_one": count == 1,
                        "difference": masks[0][row][col] and not any(
                            mask[row][col] for mask in masks[1:]
                        ),
                    }.get(combine)
                    if yes is None:
                        raise Undefined("unknown Boolean panel operation")
                    rendered.append(true_color if yes else background)
                result.append(tuple(rendered))
            output = tuple(result)
        return _d4(output, str(program["transform"]))
    raise Undefined("unknown panel program")


def execute_program(program: Mapping[str, Any], value: Any) -> JSONGrid:
    """Execute a serialized compact-output program on one input grid."""

    if not isinstance(program, Mapping):
        raise TypeError("program must be a mapping")
    if program.get("schema") != SCHEMA or program.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported program schema")
    source = _grid(value)
    op = str(program["op"])
    if op == "dense_rectangle_layout":
        output = _dense_rectangle_layout(source, program)
    elif op == "anchor_overlay":
        output = _anchor_overlay(source, program)
    elif op == "line_layer_order":
        output = _line_layer_order(source, program)
    elif op == "macro_shape_reduce":
        output = _macro_shape_reduce(source, program)
    elif op == "macro_mask_payload":
        output = _macro_mask_payload(source, program)
    elif op == "prototype_recovery":
        output = _prototype_recovery(source, program)
    elif op == "sparse_frame_crop":
        output = _sparse_frame_crop(source, program)
    elif op == "object_select_crop":
        output = _object_select_crop(source, program)
    elif op == "role_carried_reparse":
        output = _role_carried_reparse(source, program)
    elif op == "object_pack":
        output = _pack_objects(source, program)
    elif op == "serialize_objects":
        output = _serialize_objects(source, program)
    elif op == "count_render":
        output = _count_render(source, program)
    elif op.startswith("panel_"):
        output = _panel_program(source, program)
    else:
        raise ValueError("unknown compact-output operation")
    checked = _grid(output)
    if len(checked) * len(checked[0]) > 900:
        raise Undefined("program output exceeds ARC's raster cap")
    return _plain(checked)


def _program(op: str, **parameters: Any) -> dict[str, Any]:
    return {"schema": SCHEMA, "schema_version": SCHEMA_VERSION, "op": op, **parameters}


def _selector_pool() -> tuple[dict[str, Any], ...]:
    features = (
        "area",
        "box",
        "height",
        "width",
        "density",
        "colors",
        "symmetry",
        "holes",
        "components4",
        "components8",
        "border_touch",
        "top",
        "left",
        "bottom",
        "right",
    )
    result: list[dict[str, Any]] = [
        {"kind": "lexicographic", "keys": [{"feature": feature, "direction": direction}]}
        for feature in features
        for direction in ("max", "min")
    ]
    for first, second in (
        ("symmetry", "area"),
        ("symmetry", "box"),
        ("holes", "area"),
        ("colors", "area"),
        ("area", "density"),
        ("box", "density"),
        ("height", "width"),
        ("width", "height"),
        ("components4", "area"),
        ("components8", "area"),
        ("border_touch", "area"),
        ("top", "left"),
        ("left", "top"),
        ("bottom", "right"),
        ("right", "bottom"),
    ):
        for directions in itertools.product(("max", "min"), repeat=2):
            result.append(
                {
                    "kind": "lexicographic",
                    "keys": [
                        {"feature": first, "direction": directions[0]},
                        {"feature": second, "direction": directions[1]},
                    ],
                }
            )
    result.extend(
        {"kind": "unique_predicate", "predicate": predicate}
        for predicate in (
            "hollow",
            "symmetric_h",
            "symmetric_v",
            "symmetric_180",
            "multicolor",
            "square",
        )
    )
    unique = {_canonical(item): item for item in result}
    return tuple(unique[key] for key in sorted(unique))


def _enumerate_programs() -> Iterable[tuple[str, dict[str, Any], int]]:
    backgrounds = ("mode", "border", "corners")
    transforms = _D4

    # High-signal relational scene programs come first.
    for background_role in backgrounds:
        for min_side in (2, 3, 4):
            for min_area in (4, 6, 9, 12):
                yield (
                    "compact.layout.dense_rectangles",
                    _program(
                        "dense_rectangle_layout",
                        background_role=background_role,
                        min_side=min_side,
                        min_area=min_area,
                    ),
                    6 + min_side,
                )
        for connectivity in (4, 8):
            for adjacency in (1, 2):
                for priority in ("anchor_scan", "anchor_reverse", "small_first", "large_first"):
                    for transform in transforms:
                        yield (
                            "compact.layers.anchor_overlay",
                            _program(
                                "anchor_overlay",
                                background_role=background_role,
                                connectivity=connectivity,
                                adjacency=adjacency,
                                priority=priority,
                                transform=transform,
                            ),
                            8 + (adjacency > 1) + (transform != "identity"),
                        )
        for direction in ("bottom_to_top", "top_to_bottom"):
            for axis in ("row", "col"):
                for parallel_order in ("ascending", "descending"):
                    yield (
                        "compact.layers.line_order",
                        _program(
                            "line_layer_order",
                            background_role=background_role,
                            direction=direction,
                            axis=axis,
                            parallel_order=parallel_order,
                        ),
                        8,
                    )
        for true_role in ("unique_other", "mask_color", "rarest_other", "most_other"):
            for transform in transforms:
                yield (
                    "compact.normalize.macro_support",
                    _program(
                        "macro_shape_reduce",
                        background_role=background_role,
                        true_role=true_role,
                        transform=transform,
                    ),
                    7 + (transform != "identity"),
                )
        for orientation in ("vertical_sides", "horizontal_sides"):
            for transform in transforms:
                yield (
                    "compact.select.sparse_frame",
                    _program(
                        "sparse_frame_crop",
                        background_role=background_role,
                        orientation=orientation,
                        transform=transform,
                    ),
                    8 + (transform != "identity"),
                )
        for keep in ("occupied", "empty"):
            for transform in transforms:
                yield (
                    "compact.compose.macro_payload",
                    _program(
                        "macro_mask_payload",
                        background_role=background_role,
                        keep=keep,
                        transform=transform,
                    ),
                    9 + (transform != "identity"),
                )
        for connectivity in (4, 8):
            for transform in transforms:
                yield (
                    "compact.select.prototype",
                    _program(
                        "prototype_recovery",
                        background_role=background_role,
                        connectivity=connectivity,
                        transform=transform,
                    ),
                    10 + (transform != "identity"),
                )

    partitions: list[dict[str, Any]] = [
        {"kind": "uniform", "separator_role": "unique_uniform"},
        {"kind": "uniform", "separator_role": "background"},
    ]
    partitions.extend(
        {"kind": "equal", "rows": rows, "cols": cols}
        for rows, cols in ((1, 2), (2, 1), (1, 3), (3, 1), (2, 2), (1, 4), (4, 1))
    )
    for partition in partitions:
        for normalization in (
            "identity",
            "crop_root_background",
            "crop_panel_background",
            "crop_separator",
        ):
            for panel_transform in _D4:
                for transform in _D4:
                    yield (
                        "compact.panels.normalized_layout",
                        _program(
                            "panel_normalize_layout",
                            partition=partition,
                            normalization=normalization,
                            panel_transform=panel_transform,
                            transform=transform,
                        ),
                        6
                        + (normalization != "identity")
                        + (panel_transform != "identity")
                        + (transform != "identity"),
                    )
            for feature in ("area", "foreground", "palette", "bbox", "density"):
                for direction in ("max", "min"):
                    for transform in _D4:
                        yield (
                            "compact.panels.select",
                            _program(
                                "panel_select",
                                partition=partition,
                                selector={"feature": feature, "direction": direction},
                                normalization=normalization,
                                transform=transform,
                            ),
                            6 + (normalization != "identity") + (transform != "identity"),
                        )
            for priority in ("forward", "reverse"):
                for transform in _D4:
                    yield (
                        "compact.panels.overlay",
                        _program(
                            "panel_overlay",
                            partition=partition,
                            normalization=normalization,
                            priority=priority,
                            transform=transform,
                        ),
                        8 + (normalization != "identity") + (transform != "identity"),
                    )
            for combine in ("or", "and", "xor", "exactly_one", "difference"):
                for true_role in ("unique", "rarest", "most"):
                    for transform in _D4:
                        yield (
                            "compact.panels.boolean",
                            _program(
                                "panel_boolean",
                                partition=partition,
                                normalization=normalization,
                                combine=combine,
                                true_role=true_role,
                                transform=transform,
                            ),
                            9 + (normalization != "identity") + (transform != "identity"),
                        )

    selectors = _selector_pool()
    segmentations = (
        "mono4",
        "mono8",
        "support4",
        "support8",
        "mono_r2",
        "support_r2",
        "color_layers",
    )
    for background_role in backgrounds:
        for segmentation in segmentations:
            for selector in selectors:
                for render in ("raw", "isolate", "support_object_color"):
                    for transform in _D4:
                        yield (
                            "compact.objects.select_crop",
                            _program(
                                "object_select_crop",
                                background_role=background_role,
                                segmentation=segmentation,
                                selector=selector,
                                render=render,
                                transform=transform,
                            ),
                            7
                            + (segmentation not in {"mono4", "support4"})
                            + (render == "raw")
                            + (transform != "identity"),
                        )

    small_selectors = tuple(
        selector
        for selector in selectors
        if selector["kind"] == "lexicographic"
        and len(selector["keys"]) == 1
        and selector["keys"][0]["feature"] in {"area", "box"}
    )
    for background_role in backgrounds:
        for outer_segmentation in ("mono4", "mono8", "support4", "support8", "color_layers"):
            for inner_segmentation in ("mono4", "mono8", "support4", "support8"):
                for outer_selector in small_selectors:
                    for inner_selector in small_selectors:
                        for recolor in ("preserve", "rarest_foreground", "most_foreground"):
                            yield (
                                "compact.objects.role_carried_reparse",
                                _program(
                                    "role_carried_reparse",
                                    background_role=background_role,
                                    outer_segmentation=outer_segmentation,
                                    outer_selector=outer_selector,
                                    inner_segmentation=inner_segmentation,
                                    inner_selector=inner_selector,
                                    recolor=recolor,
                                    transform="identity",
                                ),
                                12 + (recolor != "preserve"),
                            )
        for segmentation in ("mono4", "mono8", "support4", "support8"):
            for order in ("row_major", "column_major", "small_first", "large_first"):
                for axis in ("horizontal", "vertical"):
                    for anchor in ("start", "center", "end"):
                        for render in ("isolate", "raw"):
                            yield (
                                "compact.objects.pack",
                                _program(
                                    "object_pack",
                                    background_role=background_role,
                                    segmentation=segmentation,
                                    order=order,
                                    axis=axis,
                                    anchor=anchor,
                                    render=render,
                                    transform="identity",
                                ),
                                9 + (render == "raw"),
                            )
            for order in ("row_major", "column_major", "small_first", "large_first"):
                for axis in ("row", "col"):
                    yield (
                        "compact.serialize.object_colors",
                        _program(
                            "serialize_objects",
                            background_role=background_role,
                            segmentation=segmentation,
                            order=order,
                            axis=axis,
                        ),
                        7,
                    )
            for color_role in ("unique_foreground", "rarest_foreground", "most_foreground"):
                for shape in ("row", "col", "square"):
                    yield (
                        "compact.serialize.count",
                        _program(
                            "count_render",
                            background_role=background_role,
                            segmentation=segmentation,
                            color_role=color_role,
                            shape=shape,
                        ),
                        6,
                    )


class _Collector:
    def __init__(
        self,
        train: tuple[tuple[Grid, Grid], ...],
        tests: tuple[Grid, ...],
        limits: Limits,
    ) -> None:
        self.train = train
        self.tests = tests
        self.limits = limits
        self.programs = 0
        self.executions = 0
        self.exact = 0
        self.exhausted = False
        self._seen: set[str] = set()
        self._candidates: list[dict[str, Any]] = []

    def propose(self, family: str, program: dict[str, Any], complexity: int) -> None:
        key = _canonical(program)
        if key in self._seen:
            return
        self._seen.add(key)
        self.programs += 1
        if self.programs > self.limits.max_programs:
            self.exhausted = True
            return
        try:
            replay: list[JSONGrid] = []
            for source, target in self.train:
                self.executions += 1
                if self.executions > self.limits.max_executions:
                    self.exhausted = True
                    return
                actual = execute_program(program, _plain(source))
                if actual != _plain(target):
                    return
                replay.append(actual)
            predictions: list[JSONGrid] = []
            for source in self.tests:
                self.executions += 1
                if self.executions > self.limits.max_executions:
                    self.exhausted = True
                    return
                predictions.append(execute_program(program, _plain(source)))
        except (IndexError, KeyError, TypeError, ValueError, ZeroDivisionError, OverflowError):
            return
        self.exact += 1
        if self.exact > self.limits.max_exact_programs:
            self.exhausted = True
            return
        self._candidates.append(
            {
                "family": family,
                "program": program,
                "train_outputs": replay,
                "test_outputs": predictions,
                "complexity": int(complexity),
                "evidence": {
                    "all_demonstrations_exact": True,
                    "demonstrations": len(self.train),
                    "test_inputs": len(self.tests),
                    "task_identity_visible": False,
                    "test_labels_visible": False,
                    "selector_policy": "relational_unique_or_abstain",
                    "search_space": "finite_complete_within_declared_caps",
                    "author": "Komorebi P.",
                },
            }
        )

    def finish(self) -> list[dict[str, Any]]:
        if self.exhausted:
            return []
        by_behavior: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for candidate in self._candidates:
            by_behavior[_canonical(candidate["test_outputs"])].append(candidate)
        if len(by_behavior) > self.limits.max_candidates:
            return []
        result: list[dict[str, Any]] = []
        for behavior in sorted(by_behavior):
            group = by_behavior[behavior]
            group.sort(
                key=lambda item: (
                    item["complexity"],
                    item["family"],
                    _canonical(item["program"]),
                )
            )
            winner = group[0]
            winner["evidence"] = dict(winner["evidence"])
            winner["evidence"]["equivalent_exact_programs"] = len(group)
            result.append(winner)
        result.sort(
            key=lambda item: (
                item["complexity"],
                item["family"],
                _canonical(item["program"]),
                _canonical(item["test_outputs"]),
            )
        )
        return result


def _object_raster_possible(
    program: Mapping[str, Any], train: tuple[tuple[Grid, Grid], ...]
) -> bool:
    """Selector-independent exact-raster gate for the large object grammar."""

    try:
        for source, target in train:
            background = _background(source, str(program["background_role"]))
            objects = _objects(source, background, str(program["segmentation"]))
            if not any(
                _d4(
                    _object_crop(source, obj, background, str(program["render"])),
                    str(program["transform"]),
                )
                == target
                for obj in objects
            ):
                return False
        return True
    except (IndexError, KeyError, TypeError, ValueError, ZeroDivisionError, OverflowError):
        return False


def replay_program(program: Mapping[str, Any], grid: Any) -> JSONGrid:
    """Block 14 tournament replay hook for a serialized candidate program."""

    return execute_program(program, grid)


def compile_task(task: Any, limits: Any = None) -> list[dict[str, Any]]:
    """Compile exact compact-output programs under the tournament contract."""

    try:
        bounds = Limits.parse(limits)
        train, tests = _sanitize(task, bounds)
        # This lane is intentionally scoped to strict area compression.
        if not all(
            len(target) * len(target[0]) < len(source) * len(source[0])
            for source, target in train
        ):
            return []
        collector = _Collector(train, tests, bounds)
        object_gate_cache: dict[tuple[str, str, str, str], bool] = {}
        for family, program, complexity in _enumerate_programs():
            if collector.exhausted:
                break
            if program["op"] == "object_select_crop":
                gate_key = (
                    str(program["background_role"]),
                    str(program["segmentation"]),
                    str(program["render"]),
                    str(program["transform"]),
                )
                possible = object_gate_cache.get(gate_key)
                if possible is None:
                    possible = _object_raster_possible(program, train)
                    object_gate_cache[gate_key] = possible
                if not possible:
                    continue
            collector.propose(family, program, complexity)
        return collector.finish()
    except (IndexError, KeyError, TypeError, ValueError, ZeroDivisionError, OverflowError):
        return []


__all__ = ["Limits", "compile_task", "execute_program", "replay_program"]
