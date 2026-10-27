"""Compact scene codecs for Block 14 residual ARC tasks.

This entrant is deliberately task-local and label separated.  It compiles a
small finite grammar for panel-sequence projection, macro-grid self products,
separator count summaries, keyed payload placement, and square-histogram
serialization.  Every returned program is executable JSON and must replay all
labelled demonstrations exactly before it is allowed to see any test input.

The compiler has no task-identity parameter and does not use identifiers,
fingerprints, corpus tables, solution stores, or attached test labels.  Colors
are resolved from roles at replay time.  Structural ties and exhausted budgets
abstain.

Author: Komorebi P.
"""

from __future__ import annotations

from collections import Counter, defaultdict, deque
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
import json
from typing import Any


Grid = tuple[tuple[int, ...], ...]
JSONGrid = list[list[int]]
SCHEMA = "komorebi.pr_lasm.block14.compact_codec_v2_program"
SCHEMA_VERSION = 2


class Undefined(ValueError):
    """A structural role or continuation is not uniquely determined."""


@dataclass(frozen=True, slots=True)
class Limits:
    max_side: int = 30
    max_examples: int = 20
    max_total_cells: int = 80_000
    max_programs: int = 96
    max_executions: int = 1_024
    max_candidates: int = 256

    @classmethod
    def parse(cls, value: Any) -> "Limits":
        if value is None:
            return cls()
        if not isinstance(value, Mapping):
            raise TypeError("limits must be a mapping or None")
        aliases = {
            "candidate_cap": "max_candidates",
            "max_total_candidates": "max_candidates",
            "max_replay_calls": None,
            "max_replay_stages": None,
            "max_trace_bytes": None,
            "time_limit": None,
            "time_limit_seconds": None,
        }
        allowed = set(cls.__dataclass_fields__) | set(aliases)
        unknown = set(value) - allowed
        if unknown:
            raise ValueError(f"unknown limits: {sorted(unknown)}")
        selected: dict[str, int] = {}
        for key, raw in value.items():
            target = aliases.get(key, key)
            if target is None:
                continue
            if isinstance(raw, bool) or not isinstance(raw, int) or raw < 1:
                raise ValueError("finite limits must be positive integers")
            selected[target] = min(selected.get(target, raw), raw)
        return cls(**selected)


@dataclass(frozen=True, slots=True)
class Object:
    cells: tuple[tuple[int, int], ...]
    color: int
    y0: int
    y1: int
    x0: int
    x1: int

    @property
    def height(self) -> int:
        return self.y1 - self.y0 + 1

    @property
    def width(self) -> int:
        return self.x1 - self.x0 + 1

    @property
    def area(self) -> int:
        return len(self.cells)


def _canonical(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def _grid(value: Any, max_side: int = 30) -> Grid:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise TypeError("grid must be a sequence of rows")
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
        if width is None or width < 1 or width > max_side or len(raw_row) != width:
            raise ValueError("grid must be nonempty and rectangular")
        row: list[int] = []
        for cell in raw_row:
            if isinstance(cell, bool) or not isinstance(cell, int) or not 0 <= cell <= 9:
                raise ValueError("ARC cells must be integer colors in [0, 9]")
            row.append(int(cell))
        rows.append(tuple(row))
    return tuple(rows)


def _plain(value: Grid) -> JSONGrid:
    return [list(row) for row in value]


def _sanitize(
    task: Any, limits: Limits
) -> tuple[tuple[tuple[Grid, Grid], ...], tuple[Grid, ...]]:
    if not isinstance(task, Mapping):
        raise TypeError("task must be a mapping")
    raw_train = task["train"]
    raw_test = task["test"]
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
    for record in raw_train:
        if not isinstance(record, Mapping):
            raise TypeError("training records must be mappings")
        source = _grid(record["input"], limits.max_side)
        target = _grid(record["output"], limits.max_side)
        cells += len(source) * len(source[0]) + len(target) * len(target[0])
        train.append((source, target))
    tests: list[Grid] = []
    for record in raw_test:
        if not isinstance(record, Mapping):
            raise TypeError("test records must be mappings")
        # Deliberately request only the observable input field.
        source = _grid(record["input"], limits.max_side)
        cells += len(source) * len(source[0])
        tests.append(source)
    if cells > limits.max_total_cells:
        raise ValueError("task cell budget exceeded")
    return tuple(train), tuple(tests)


def _strict_mode(values: Iterable[int]) -> int:
    counts = Counter(values)
    if not counts:
        raise Undefined("empty color population")
    peak = max(counts.values())
    winners = sorted(color for color, count in counts.items() if count == peak)
    if len(winners) != 1:
        raise Undefined("modal color is tied")
    return winners[0]


def _background(value: Grid, role: str) -> int:
    if role == "mode":
        return _strict_mode(cell for row in value for cell in row)
    if role == "border":
        population = list(value[0]) + list(value[-1])
        population.extend(row[0] for row in value[1:-1])
        population.extend(row[-1] for row in value[1:-1])
        return _strict_mode(population)
    if role == "corners":
        return _strict_mode((value[0][0], value[0][-1], value[-1][0], value[-1][-1]))
    raise Undefined("unknown background role")


def _bbox(cells: Iterable[tuple[int, int]]) -> tuple[int, int, int, int]:
    materialized = tuple(cells)
    if not materialized:
        raise Undefined("empty support")
    ys = [cell[0] for cell in materialized]
    xs = [cell[1] for cell in materialized]
    return min(ys), max(ys), min(xs), max(xs)


def _crop(value: Grid, box: tuple[int, int, int, int]) -> Grid:
    y0, y1, x0, x1 = box
    return tuple(tuple(value[y][x0 : x1 + 1]) for y in range(y0, y1 + 1))


def _components(
    value: Grid,
    background: int,
    *,
    connectivity: int,
    monochrome: bool = True,
    excluded: Iterable[int] = (),
) -> tuple[Object, ...]:
    excluded_set = set(excluded) | {background}
    if connectivity not in {4, 8}:
        raise Undefined("unsupported connectivity")
    neighbors = (
        ((-1, 0), (0, -1), (0, 1), (1, 0))
        if connectivity == 4
        else tuple(
            (dy, dx)
            for dy in (-1, 0, 1)
            for dx in (-1, 0, 1)
            if (dy, dx) != (0, 0)
        )
    )
    height, width = len(value), len(value[0])
    seen: set[tuple[int, int]] = set()
    result: list[Object] = []
    for y in range(height):
        for x in range(width):
            color = value[y][x]
            if color in excluded_set or (y, x) in seen:
                continue
            queue = deque([(y, x)])
            seen.add((y, x))
            cells: list[tuple[int, int]] = []
            while queue:
                cy, cx = queue.popleft()
                cells.append((cy, cx))
                for dy, dx in neighbors:
                    ny, nx = cy + dy, cx + dx
                    if not (0 <= ny < height and 0 <= nx < width) or (ny, nx) in seen:
                        continue
                    neighbor = value[ny][nx]
                    if neighbor in excluded_set:
                        continue
                    if monochrome and neighbor != color:
                        continue
                    seen.add((ny, nx))
                    queue.append((ny, nx))
            y0, y1, x0, x1 = _bbox(cells)
            colors = {value[cy][cx] for cy, cx in cells}
            if monochrome and colors != {color}:
                raise Undefined("monochrome component changed color")
            result.append(Object(tuple(sorted(cells)), color, y0, y1, x0, x1))
    result.sort(key=lambda obj: (obj.y0, obj.x0, obj.y1, obj.x1, obj.color))
    return tuple(result)


def _object_crop(value: Grid, obj: Object, background: int) -> Grid:
    canvas = [[background for _ in range(obj.width)] for _ in range(obj.height)]
    for y, x in obj.cells:
        canvas[y - obj.y0][x - obj.x0] = value[y][x]
    return tuple(tuple(row) for row in canvas)


def _arithmetic_next(values: Sequence[int]) -> int:
    if len(values) < 3:
        raise Undefined("continuation needs at least three observations")
    differences = [b - a for a, b in zip(values, values[1:])]
    if len(set(differences)) != 1:
        raise Undefined("sequence is not arithmetic")
    return values[-1] + differences[-1]


def _uniform_axis_lines(value: Grid, axis: str) -> dict[int, list[int]]:
    result: dict[int, list[int]] = defaultdict(list)
    if axis == "horizontal":
        for index, row in enumerate(value):
            if len(set(row)) == 1:
                result[row[0]].append(index)
    elif axis == "vertical":
        for index in range(len(value[0])):
            column = [row[index] for row in value]
            if len(set(column)) == 1:
                result[column[0]].append(index)
    else:
        raise Undefined("unknown partition axis")
    return dict(result)


def _regular_panels(value: Grid, axis: str, boundary_mode: str) -> tuple[Grid, ...]:
    length = len(value) if axis == "horizontal" else len(value[0])
    background = _background(value, "mode")
    candidates: list[tuple[int, tuple[Grid, ...]]] = []
    for color, indices in _uniform_axis_lines(value, axis).items():
        if color == background or len(indices) < 2:
            continue
        steps = [b - a for a, b in zip(indices, indices[1:])]
        if not steps or len(set(steps)) != 1 or steps[0] < 2:
            continue
        stride = steps[0]
        ranges: list[tuple[int, int]] = []
        if boundary_mode == "exclusive":
            if indices[0] != stride - 1 or indices[-1] != length - stride:
                continue
            starts = [0] + [index + 1 for index in indices]
            stops = list(indices) + [length]
            ranges = list(zip(starts, stops))
            if any(stop - start != stride - 1 for start, stop in ranges):
                continue
        elif boundary_mode == "shared":
            if len(indices) < 3 or indices[0] != 0 or indices[-1] != length - 1:
                continue
            ranges = [(a, b + 1) for a, b in zip(indices, indices[1:])]
            if any(stop - start != stride + 1 for start, stop in ranges):
                continue
        else:
            raise Undefined("unknown boundary mode")
        panels: list[Grid] = []
        for start, stop in ranges:
            if axis == "horizontal":
                panels.append(tuple(value[start:stop]))
            else:
                panels.append(tuple(tuple(row[start:stop]) for row in value))
        if len(panels) >= 3 and len({(len(p), len(p[0])) for p in panels}) == 1:
            candidates.append((color, tuple(panels)))
    if len(candidates) != 1:
        raise Undefined("regular nonbackground divider is not unique")
    return candidates[0][1]


def _interior_positions(panel: Grid, boundary_mode: str) -> tuple[tuple[int, int], ...]:
    height, width = len(panel), len(panel[0])
    ys = range(height)
    xs = range(width)
    if boundary_mode == "shared":
        # Shared panel boundaries can form a complete frame.  Remove each
        # monochrome edge independently; interior anomalies may use the same
        # color as the frame and therefore cannot be filtered by color alone.
        if len(set(panel[0])) == 1:
            ys = range(1, height)
        if len(set(panel[-1])) == 1:
            ys = range(ys.start, height - 1)
        if len({row[0] for row in panel}) == 1:
            xs = range(1, width)
        if len({row[-1] for row in panel}) == 1:
            xs = range(xs.start, width - 1)
    positions = tuple((y, x) for y in ys for x in xs)
    if not positions:
        raise Undefined("panel has no interior")
    return positions


def _panel_payloads(
    panels: Sequence[Grid], boundary_mode: str, background_role: str
) -> tuple[int, tuple[tuple[tuple[int, int], ...], ...]]:
    positions = _interior_positions(panels[0], boundary_mode)
    backgrounds: list[int] = []
    supports: list[tuple[tuple[int, int], ...]] = []
    for panel in panels:
        if _interior_positions(panel, boundary_mode) != positions:
            raise Undefined("panel interiors differ")
        if background_role == "mode":
            background = _strict_mode(panel[y][x] for y, x in positions)
        elif background_role == "zero":
            background = 0
        elif background_role == "corners":
            background = _background(panel, "corners")
        else:
            raise Undefined("unknown panel background role")
        backgrounds.append(background)
        support = tuple((y, x) for y, x in positions if panel[y][x] != background)
        if not support:
            raise Undefined("empty panel payload")
        supports.append(support)
    if len(set(backgrounds)) != 1:
        raise Undefined("panel backgrounds differ")
    return backgrounds[0], tuple(supports)


def _translate_panel_next(
    panels: Sequence[Grid], boundary_mode: str, background_role: str
) -> Grid:
    background, supports = _panel_payloads(panels, boundary_mode, background_role)
    boxes = [_bbox(support) for support in supports]
    crops = [_crop(panel, box) for panel, box in zip(panels, boxes)]
    if len(set(crops)) != 1:
        raise Undefined("payload crops are not identical")
    y0 = _arithmetic_next([box[0] for box in boxes])
    x0 = _arithmetic_next([box[2] for box in boxes])
    crop = crops[-1]
    if y0 < 0 or x0 < 0 or y0 + len(crop) > len(panels[-1]) or x0 + len(crop[0]) > len(panels[-1][0]):
        raise Undefined("translated payload leaves panel")
    canvas = [list(row) for row in panels[-1]]
    for y, x in supports[-1]:
        canvas[y][x] = background
    for y, row in enumerate(crop):
        for x, color in enumerate(row):
            if color != background:
                canvas[y0 + y][x0 + x] = color
    return tuple(tuple(row) for row in canvas)


def _rectangle_panel_next(
    panels: Sequence[Grid], boundary_mode: str, background_role: str
) -> Grid:
    background, supports = _panel_payloads(panels, boundary_mode, background_role)
    boxes = [_bbox(support) for support in supports]
    colors: list[int] = []
    for panel, support, box in zip(panels, supports, boxes):
        population = {panel[y][x] for y, x in support}
        if len(population) != 1:
            raise Undefined("rectangle payload is multicolor")
        color = next(iter(population))
        y0, y1, x0, x1 = box
        if len(support) != (y1 - y0 + 1) * (x1 - x0 + 1):
            raise Undefined("payload is not a filled rectangle")
        colors.append(color)
    if len(set(colors)) != 1:
        raise Undefined("rectangle color changes")
    next_y = _arithmetic_next([box[0] for box in boxes])
    next_x = _arithmetic_next([box[2] for box in boxes])
    next_h = _arithmetic_next([box[1] - box[0] + 1 for box in boxes])
    next_w = _arithmetic_next([box[3] - box[2] + 1 for box in boxes])
    if (
        next_y < 0
        or next_x < 0
        or next_h < 1
        or next_w < 1
        or next_y + next_h > len(panels[-1])
        or next_x + next_w > len(panels[-1][0])
    ):
        raise Undefined("rectangle continuation leaves panel")
    canvas = [list(row) for row in panels[-1]]
    for y, x in supports[-1]:
        canvas[y][x] = background
    for y in range(next_y, next_y + next_h):
        for x in range(next_x, next_x + next_w):
            canvas[y][x] = colors[0]
    return tuple(tuple(row) for row in canvas)


def _monotone_recolor_next(
    panels: Sequence[Grid], boundary_mode: str, background_role: str
) -> Grid:
    background, supports = _panel_payloads(panels, boundary_mode, background_role)
    if len(set(supports)) != 1:
        raise Undefined("support changes during recoloring")
    changes: list[tuple[tuple[int, int, int, int], ...]] = []
    pairs: set[tuple[int, int]] = set()
    for before, after in zip(panels, panels[1:]):
        delta: list[tuple[int, int, int, int]] = []
        for y, x in supports[0]:
            if before[y][x] != after[y][x]:
                delta.append((y, x, before[y][x], after[y][x]))
                pairs.add((before[y][x], after[y][x]))
        if not delta:
            raise Undefined("recolor transition is empty")
        changes.append(tuple(delta))
    if len(pairs) != 1:
        raise Undefined("recolor role pair is not unique")
    source_color, target_color = next(iter(pairs))
    if source_color in {background, target_color}:
        raise Undefined("recolor roles are degenerate")
    predictions: list[Grid] = []
    for coordinate_axis in (0, 1):
        coordinates: list[int] = []
        valid = True
        for delta in changes:
            values = {item[coordinate_axis] for item in delta}
            if len(values) != 1:
                valid = False
                break
            coordinates.append(next(iter(values)))
        if not valid:
            continue
        try:
            coordinate = _arithmetic_next(coordinates)
        except Undefined:
            continue
        canvas = [list(row) for row in panels[-1]]
        changed = 0
        for y, x in supports[-1]:
            if (y if coordinate_axis == 0 else x) == coordinate and canvas[y][x] == source_color:
                canvas[y][x] = target_color
                changed += 1
        if changed:
            predictions.append(tuple(tuple(row) for row in canvas))
    unique = {_canonical(_plain(prediction)): prediction for prediction in predictions}
    if len(unique) != 1:
        raise Undefined("monotone continuation is ambiguous")
    return next(iter(unique.values()))


def _panel_sequence_projection(value: Grid, program: Mapping[str, Any]) -> Grid:
    panels = _regular_panels(value, str(program["axis"]), str(program["boundary_mode"]))
    predictions: list[Grid] = []
    for model in (_translate_panel_next, _rectangle_panel_next, _monotone_recolor_next):
        try:
            predictions.append(
                model(
                    panels,
                    str(program["boundary_mode"]),
                    str(program["panel_background_role"]),
                )
            )
        except (IndexError, TypeError, ValueError, ZeroDivisionError, OverflowError):
            continue
    unique = {_canonical(_plain(prediction)): prediction for prediction in predictions}
    if len(unique) != 1:
        raise Undefined("panel continuation model is not unique")
    return next(iter(unique.values()))


def _macro_self_product(value: Grid, program: Mapping[str, Any]) -> Grid:
    background = _background(value, str(program["background_role"]))
    colors = sorted({cell for row in value for cell in row if cell != background})
    if len(colors) != 1:
        raise Undefined("macro self-product needs one foreground color")
    foreground = colors[0]
    support = tuple((y, x) for y, row in enumerate(value) for x, cell in enumerate(row) if cell == foreground)
    y0, y1, x0, x1 = _bbox(support)
    height, width = y1 - y0 + 1, x1 - x0 + 1
    side = int(program["macro_side"])
    if side < 2 or height != width or height % side:
        raise Undefined("macro bounding square is incompatible")
    block = height // side
    if block < 2:
        raise Undefined("macro cells are not expanded blocks")
    pattern: list[list[bool]] = []
    for macro_y in range(side):
        row: list[bool] = []
        for macro_x in range(side):
            population = {
                value[y][x]
                for y in range(y0 + macro_y * block, y0 + (macro_y + 1) * block)
                for x in range(x0 + macro_x * block, x0 + (macro_x + 1) * block)
            }
            if population == {foreground}:
                row.append(True)
            elif population == {background}:
                row.append(False)
            else:
                raise Undefined("macro cell is not uniform")
        pattern.append(row)
    if any(not any(row) for row in pattern) or any(
        not any(pattern[y][x] for y in range(side)) for x in range(side)
    ):
        raise Undefined("trimmed macro pattern has an empty boundary")
    output: list[tuple[int, ...]] = []
    for outer_y in range(side):
        for inner_y in range(side):
            rendered: list[int] = []
            for outer_x in range(side):
                for inner_x in range(side):
                    rendered.append(
                        foreground
                        if pattern[outer_y][outer_x] and pattern[inner_y][inner_x]
                        else background
                    )
            output.append(tuple(rendered))
    return tuple(output)


def _separator_count_summary(value: Grid, program: Mapping[str, Any]) -> Grid:
    background = _background(value, str(program["background_role"]))
    uniform = [
        (y, row[0])
        for y, row in enumerate(value)
        if len(set(row)) == 1 and row[0] != background
    ]
    if len(uniform) < 3:
        raise Undefined("not enough colored separator rows")
    terminator_y, terminator_color = uniform[-1]
    if any(cell != background for row in value[terminator_y + 1 :] for cell in row):
        raise Undefined("terminal separator is not terminal")
    data_lines = uniform[:-1]
    data_colors = [color for _, color in data_lines]
    if not 2 <= len(data_lines) <= 6 or len(set(data_colors)) != len(data_colors):
        raise Undefined("data separator colors are not unique")
    if terminator_color in data_colors:
        raise Undefined("terminator color is reused")
    excluded = {background, terminator_color, *data_colors}
    marker_cells = [
        (y, x, cell)
        for y, row in enumerate(value)
        for x, cell in enumerate(row)
        if cell not in excluded
    ]
    if len(marker_cells) != 1:
        raise Undefined("summary marker is not a unique cell")
    marker_y, marker_x, marker_color = marker_cells[0]
    del marker_y
    count_width = len(data_lines)
    counts: list[int] = []
    boundaries = [y for y, _ in data_lines] + [terminator_y]
    for (line_y, color), next_y in zip(data_lines, boundaries[1:]):
        populations = [row.count(color) for row in value[line_y + 1 : next_y]]
        positives = [count for count in populations if count > 0]
        count = positives.count(max(positives)) if positives else 0
        if count > count_width:
            raise Undefined("summary count exceeds unary field")
        counts.append(count)
    zone = min(count_width - 1, marker_x * count_width // len(value[0]))
    marker_row = zone if program["zone_order"] == "forward" else count_width - 1 - zone
    rows: list[tuple[int, ...]] = []
    for index, (color, count) in enumerate(zip(data_colors, counts)):
        row = [color] * count + [background] * (count_width - count)
        row.extend((terminator_color, marker_color if index == marker_row else background))
        rows.append(tuple(row))
    return tuple(rows)


def _keyed_payload_place(value: Grid, program: Mapping[str, Any]) -> Grid:
    background = _background(value, str(program["background_role"]))
    separator_rows = [
        y
        for y, row in enumerate(value)
        if len(set(row)) == 1 and row[0] != background
    ]
    if len(separator_rows) != 1:
        raise Undefined("keyed scene needs one colored divider")
    separator_y = separator_rows[0]
    if separator_y < 2 or separator_y > len(value) - 3:
        raise Undefined("divider leaves an empty scene")
    separator_color = value[separator_y][0]
    upper = tuple(value[:separator_y])
    lower = tuple(value[separator_y + 1 :])
    connectivity = int(program["connectivity"])
    upper_objects = _components(
        upper, background, connectivity=connectivity, excluded=(separator_color,)
    )
    lower_objects = _components(
        lower, background, connectivity=connectivity, excluded=(separator_color,)
    )
    if len(upper_objects) != 3 or len(lower_objects) != 1:
        raise Undefined("keyed scene object arity differs")
    lower_key = lower_objects[0]
    lower_crop = _object_crop(lower, lower_key, background)
    matches = [
        obj
        for obj in upper_objects
        if obj.color == lower_key.color
        and _object_crop(upper, obj, background) == lower_crop
    ]
    if len(matches) != 1:
        raise Undefined("upper key is not uniquely matched")
    upper_key = matches[0]
    others = [obj for obj in upper_objects if obj != upper_key]
    if not all(obj.y0 == upper_key.y0 and obj.height == upper_key.height for obj in others):
        raise Undefined("key, guide, and payload are not aligned")
    distances = sorted((abs(obj.x0 - upper_key.x0), obj) for obj in others)
    if distances[0][0] == distances[1][0]:
        raise Undefined("guide proximity is tied")
    guide = distances[0][1]
    payload = distances[1][1]
    guide_crop = _object_crop(upper, guide, background)
    first_support = sum(cell != background for cell in guide_crop[0])
    last_support = sum(cell != background for cell in guide_crop[-1])
    if first_support == last_support:
        raise Undefined("guide has no vertical direction")
    payload_crop = _object_crop(upper, payload, background)
    target_y = (
        lower_key.y1 + 1
        if first_support > last_support
        else lower_key.y0 - len(payload_crop)
    )
    target_x = lower_key.x0
    if (
        target_y < 0
        or target_x < 0
        or target_y + len(payload_crop) > len(lower)
        or target_x + len(payload_crop[0]) > len(lower[0])
    ):
        raise Undefined("payload placement leaves lower scene")
    canvas = [list(row) for row in lower]
    for y, row in enumerate(payload_crop):
        for x, color in enumerate(row):
            if color == background:
                continue
            if canvas[target_y + y][target_x + x] != background:
                raise Undefined("payload overlaps the key")
            canvas[target_y + y][target_x + x] = color
    return tuple(tuple(row) for row in canvas)


def _solid_square_groups(value: Grid, background: int) -> dict[int, tuple[int, int]]:
    """Return side -> (color, count) for clean repeated square components."""

    groups: dict[int, tuple[int, int]] = {}
    colors = sorted({cell for row in value for cell in row if cell != background})
    for color in colors:
        objects = _components(value, background, connectivity=4, excluded=set(colors) - {color})
        if not objects:
            continue
        sides: list[int] = []
        valid = True
        for obj in objects:
            if obj.height != obj.width or obj.height < 2 or obj.area != obj.height * obj.width:
                valid = False
                break
            sides.append(obj.height)
        if not valid or len(set(sides)) != 1:
            continue
        side = sides[0]
        if side in groups:
            raise Undefined("square sizes do not uniquely encode colors")
        groups[side] = (color, len(objects))
    return groups


def _square_histogram_pack(value: Grid, program: Mapping[str, Any]) -> Grid:
    background = _background(value, str(program["background_role"]))
    groups = _solid_square_groups(value, background)
    if len(groups) < 3:
        raise Undefined("square histogram needs at least three ranks")
    sides = sorted(groups)
    if sides != list(range(sides[0], sides[-1] + 1)) or sides[0] != 2 or sides[-1] > 6:
        raise Undefined("square ranks are not consecutive from two")
    shape_colors = {color for color, _ in groups.values()}
    other_colors = {
        cell for row in value for cell in row if cell not in shape_colors | {background}
    }
    if len(other_colors) > 1:
        raise Undefined("noise role is not unique")
    if other_colors:
        noise = next(iter(other_colors))
        noise_objects = _components(
            value,
            background,
            connectivity=4,
            excluded=shape_colors,
        )
        if not noise_objects or any(obj.color != noise for obj in noise_objects):
            raise Undefined("noise color mixes structural objects")
        if sum(obj.area == 1 for obj in noise_objects) * 2 < len(noise_objects):
            raise Undefined("noise role is not dominated by singleton marks")
    counts = {side: count for side, (_, count) in groups.items()}
    if program["smallest_cap"] == "largest_side":
        counts[sides[0]] = min(counts[sides[0]], sides[-1])
    elif program["smallest_cap"] != "none":
        raise Undefined("unknown square-count cap")
    stack_count = max(counts.values())
    height = sides[-1] + 1
    rows: list[list[int]] = [[] for _ in range(height)]
    for stack in range(stack_count):
        active = [side for side in sides if stack < counts[side]]
        if not active:
            raise Undefined("empty histogram stack")
        width = max(active)
        block = [[background for _ in range(width)] for _ in range(height)]
        for side in sorted(active, reverse=True):
            color = groups[side][0]
            for y in range(side):
                for x in range(side):
                    block[y][x] = color
        for y in range(height):
            rows[y].extend(block[y])
            rows[y].append(background)
    if not rows or len(rows[0]) > 30:
        raise Undefined("serialized histogram exceeds ARC bounds")
    return tuple(tuple(row) for row in rows)


def execute_program(program: Mapping[str, Any], value: Any) -> JSONGrid:
    """Execute one serialized compact-codec program on an input grid."""

    if not isinstance(program, Mapping):
        raise TypeError("program must be a mapping")
    if program.get("schema") != SCHEMA or program.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported compact-codec schema")
    source = _grid(value)
    op = str(program["op"])
    if op == "panel_sequence_projection":
        output = _panel_sequence_projection(source, program)
    elif op == "macro_self_product":
        output = _macro_self_product(source, program)
    elif op == "separator_count_summary":
        output = _separator_count_summary(source, program)
    elif op == "keyed_payload_place":
        output = _keyed_payload_place(source, program)
    elif op == "square_histogram_pack":
        output = _square_histogram_pack(source, program)
    else:
        raise ValueError("unknown compact-codec operation")
    checked = _grid(output)
    return _plain(checked)


def replay_program(program: Mapping[str, Any], grid: Any) -> JSONGrid:
    """Tournament replay hook for serialized programs."""

    return execute_program(program, grid)


def _program(op: str, **parameters: Any) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "op": op,
        **parameters,
    }


def _enumerate_programs() -> tuple[tuple[str, dict[str, Any], int], ...]:
    programs: list[tuple[str, dict[str, Any], int]] = []
    for axis in ("horizontal", "vertical"):
        for boundary_mode in ("exclusive", "shared"):
            for panel_background_role in ("zero", "mode", "corners"):
                programs.append(
                    (
                        "compact_codec_v2.panels.sequence_projection",
                        _program(
                            "panel_sequence_projection",
                            axis=axis,
                            boundary_mode=boundary_mode,
                            panel_background_role=panel_background_role,
                            separator_role="unique_regular_nonbackground",
                            continuation="unique_structural_model",
                        ),
                        18,
                    )
                )
    for background_role in ("mode", "border", "corners"):
        for macro_side in range(2, 7):
            programs.append(
                (
                    "compact_codec_v2.macro.self_product",
                    _program(
                        "macro_self_product",
                        background_role=background_role,
                        macro_side=macro_side,
                    ),
                    12 + macro_side,
                )
            )
    for zone_order in ("reverse", "forward"):
        programs.append(
            (
                "compact_codec_v2.count.separator_summary",
                _program(
                    "separator_count_summary",
                    background_role="mode",
                    count_code="maximal_rows_unary",
                    zone_order=zone_order,
                ),
                16,
            )
        )
    for connectivity in (8, 4):
        programs.append(
            (
                "compact_codec_v2.compose.keyed_payload",
                _program(
                    "keyed_payload_place",
                    background_role="mode",
                    connectivity=connectivity,
                    guide_role="nearest_edge_heavy_object",
                ),
                20,
            )
        )
    for smallest_cap in ("largest_side", "none"):
        programs.append(
            (
                "compact_codec_v2.serialize.square_histogram",
                _program(
                    "square_histogram_pack",
                    background_role="mode",
                    smallest_cap=smallest_cap,
                    stack_order="largest_base_then_smaller_overlay",
                ),
                17 if smallest_cap == "none" else 19,
            )
        )
    programs.sort(key=lambda item: (item[2], item[0], _canonical(item[1])))
    return tuple(programs)


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
        self.exhausted = False
        self.candidates: list[dict[str, Any]] = []

    def propose(self, family: str, program: Mapping[str, Any], complexity: int) -> None:
        if self.exhausted:
            return
        self.programs += 1
        if self.programs > self.limits.max_programs:
            self.exhausted = True
            self.candidates.clear()
            return
        train_outputs: list[JSONGrid] = []
        test_outputs: list[JSONGrid] = []
        try:
            for source, target in self.train:
                self.executions += 1
                if self.executions > self.limits.max_executions:
                    raise OverflowError("execution budget exhausted")
                output = execute_program(program, source)
                if _grid(output) != target:
                    return
                train_outputs.append(output)
            for source in self.tests:
                self.executions += 1
                if self.executions > self.limits.max_executions:
                    raise OverflowError("execution budget exhausted")
                test_outputs.append(execute_program(program, source))
        except OverflowError:
            self.exhausted = True
            self.candidates.clear()
            return
        except (IndexError, KeyError, TypeError, ValueError, ZeroDivisionError):
            return
        self.candidates.append(
            {
                "family": family,
                "program": dict(program),
                "train_outputs": train_outputs,
                "test_outputs": test_outputs,
                "complexity": int(complexity),
                "evidence": {
                    "all_demonstrations_exact": True,
                    "exact_replay": True,
                    "demonstration_count": len(self.train),
                    "test_input_count": len(self.tests),
                    "label_access": "demonstrations_only",
                    "identity_access": False,
                },
            }
        )
        if len(self.candidates) > self.limits.max_candidates:
            self.exhausted = True
            self.candidates.clear()

    def finish(self) -> list[dict[str, Any]]:
        if self.exhausted or not self.candidates:
            return []
        by_behavior: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for candidate in self.candidates:
            by_behavior[_canonical(candidate["test_outputs"])].append(candidate)
        # Compact-codec v2 fails closed rather than exporting behavior ties.
        if len(by_behavior) != 1:
            return []
        group = next(iter(by_behavior.values()))
        group.sort(
            key=lambda candidate: (
                candidate["complexity"],
                candidate["family"],
                _canonical(candidate["program"]),
            )
        )
        winner = group[0]
        winner["evidence"] = dict(winner["evidence"])
        winner["evidence"]["equivalent_exact_programs"] = len(group)
        return [winner]


def compile_task(task: Any, limits: Any = None) -> list[dict[str, Any]]:
    """Compile the unique replay-safe compact behavior for ``task``."""

    try:
        bounds = Limits.parse(limits)
        train, tests = _sanitize(task, bounds)
        if not all(
            len(target) * len(target[0]) < len(source) * len(source[0])
            for source, target in train
        ):
            return []
        collector = _Collector(train, tests, bounds)
        for family, program, complexity in _enumerate_programs():
            collector.propose(family, program, complexity)
            if collector.exhausted:
                break
        return collector.finish()
    except (IndexError, KeyError, TypeError, ValueError, ZeroDivisionError, OverflowError):
        return []


__all__ = ["Limits", "compile_task", "execute_program", "replay_program"]
