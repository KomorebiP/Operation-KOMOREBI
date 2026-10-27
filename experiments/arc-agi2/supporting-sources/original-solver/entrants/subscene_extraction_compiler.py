"""Role-selected subscene extraction and compact projection for Block 15.

The entrant is deliberately identity blind.  It accepts only demonstration
pairs and held-out inputs and enumerates a small, finite grammar of structural
programs.  A candidate is emitted only when every demonstration replays,
all exact programs agree on the held-out behavior, leave-one-out induction
recovers the same branch, and D4 plus palette counterfactuals commute.

The grammar contains reusable mechanisms rather than task-indexed clauses:

* select the carrier panel containing the most complete plus motifs;
* extract a low-entropy rectangle from a noisy field and project marker rays;
* decode two-cell palette keys and recolor a filled exemplar;
* serialize overlapping solid rectangles by their ordered side lengths;
* recover the exceptional prototype in the most repeated color family; and
* decode a scalar from reflection symmetry using a learned two-class codebook.

Author: Komorebi P.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
import hashlib
import json
from typing import Any


Grid = tuple[tuple[int, ...], ...]
Cell = tuple[int, int]
Pair = tuple[Grid, Grid]
SCHEMA = "komorebi.pr_lasm.block15.subscene_extraction.program.v1"
AUTHOR = "Komorebi P."


class Undefined(ValueError):
    """A structural role or continuation is absent or ambiguous."""


@dataclass(frozen=True, slots=True)
class Limits:
    max_grid_cells: int = 900
    max_examples: int = 16
    max_programs: int = 64
    max_executor_calls: int = 20_000
    max_counterfactual_checks: int = 256
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
            "max_examples": 32,
            "max_programs": 256,
            "max_executor_calls": 200_000,
            "max_counterfactual_checks": 4_096,
            "max_candidates": 1,
        }
        result: dict[str, int] = {}
        for name in cls.__dataclass_fields__:
            raw = value.get(name, getattr(defaults, name))
            if name == "max_candidates" and "candidate_cap" in value:
                raw = value["candidate_cap"]
            if isinstance(raw, bool) or not isinstance(raw, int) or raw < 0:
                raise Undefined(f"limits.{name} must be a nonnegative integer")
            result[name] = min(raw, ceilings[name])
        return cls(**result)


def _canonical(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    )


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _grid(value: Any, limits: Limits | None = None) -> Grid:
    bounds = limits or Limits()
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
            raise Undefined("grid row must be a nonempty sequence")
        row: list[int] = []
        for raw_cell in raw_row:
            if (
                isinstance(raw_cell, bool)
                or not isinstance(raw_cell, int)
                or not 0 <= raw_cell <= 9
            ):
                raise Undefined("invalid ARC color")
            row.append(int(raw_cell))
        if width is None:
            width = len(row)
        elif len(row) != width:
            raise Undefined("ragged grid")
        rows.append(tuple(row))
    if len(rows) * int(width or 0) > bounds.max_grid_cells:
        raise Undefined("grid exceeds the cell cap")
    return tuple(rows)


def _plain(value: Grid) -> list[list[int]]:
    return [list(row) for row in value]


def _shape(value: Grid) -> tuple[int, int]:
    return len(value), len(value[0])


def _strict_mode(values: Iterable[int]) -> int:
    counts = Counter(values)
    if not counts:
        raise Undefined("empty population")
    peak = max(counts.values())
    winners = [color for color, count in counts.items() if count == peak]
    if len(winners) != 1:
        raise Undefined("modal color is tied")
    return winners[0]


def _background(value: Grid) -> int:
    return _strict_mode(cell for row in value for cell in row)


def _border_background(value: Grid) -> int:
    height, width = _shape(value)
    border = list(value[0]) + list(value[-1])
    border.extend(value[row][0] for row in range(1, height - 1))
    border.extend(value[row][width - 1] for row in range(1, height - 1))
    return _strict_mode(border)


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


def _crop(value: Grid, box: tuple[int, int, int, int]) -> Grid:
    top, bottom, left, right = box
    if not (
        0 <= top <= bottom < len(value)
        and 0 <= left <= right < len(value[0])
    ):
        raise Undefined("invalid crop")
    return tuple(tuple(value[row][left : right + 1]) for row in range(top, bottom + 1))


def _rotate(value: Grid) -> Grid:
    return tuple(tuple(row) for row in zip(*reversed(value)))


def _reflect(value: Grid) -> Grid:
    return tuple(tuple(reversed(row)) for row in value)


def _transform(value: Grid, quarter_turns: int, reflected: bool) -> Grid:
    result = value
    for _ in range(quarter_turns % 4):
        result = _rotate(result)
    return _reflect(result) if reflected else result


def _d4(value: Grid) -> tuple[Grid, ...]:
    return tuple(
        dict.fromkeys(
            _transform(value, turns, reflected)
            for turns in range(4)
            for reflected in (False, True)
        )
    )


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
            raise Undefined("invalid held-out example")
        # Test labels, if maliciously injected, are intentionally ignored.
        tests.append(_grid(example.get("input"), limits))
    return tuple(train), tuple(tests)


@dataclass(frozen=True, slots=True)
class Component:
    color: int | None
    cells: tuple[Cell, ...]
    box: tuple[int, int, int, int]

    @property
    def area(self) -> int:
        return len(self.cells)

    @property
    def height(self) -> int:
        return self.box[1] - self.box[0] + 1

    @property
    def width(self) -> int:
        return self.box[3] - self.box[2] + 1


def _components(value: Grid, background: int, *, monochrome: bool) -> tuple[Component, ...]:
    height, width = _shape(value)
    remaining = {
        (row, column)
        for row in range(height)
        for column in range(width)
        if value[row][column] != background
    }
    result: list[Component] = []
    while remaining:
        seed = min(remaining)
        remaining.remove(seed)
        seed_color = value[seed[0]][seed[1]]
        queue = [seed]
        cells = {seed}
        while queue:
            row, column = queue.pop()
            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                point = row + dr, column + dc
                if point not in remaining:
                    continue
                if monochrome and value[point[0]][point[1]] != seed_color:
                    continue
                remaining.remove(point)
                cells.add(point)
                queue.append(point)
        result.append(
            Component(
                seed_color if monochrome else None,
                tuple(sorted(cells)),
                _bbox(cells),
            )
        )
    return tuple(sorted(result, key=lambda item: (item.box, item.color)))


# ---------------------------------------------------------------------------
# Structural executors


def _plus_centers(value: Grid, color: int) -> int:
    height, width = _shape(value)
    centers = 0
    for row in range(1, height - 1):
        for column in range(1, width - 1):
            if all(
                value[row + dr][column + dc] == color
                for dr, dc in ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1))
            ):
                centers += 1
    return centers


def _plus_panel_extract(value: Grid) -> Grid:
    # Panels can occupy more cells than the surrounding field on the held-out
    # raster, so the exterior role is resolved from the border, not by area.
    background = _border_background(value)
    candidates: list[tuple[int, Grid]] = []
    for component in _components(value, background, monochrome=True):
        if component.height < 5 or component.width < 5 or component.height * component.width < 25:
            continue
        raster = _crop(value, component.box)
        palette = {cell for row in raster for cell in row}
        if background in palette or len(palette) != 2 or component.color not in palette:
            continue
        signal = next(iter(palette - {int(component.color)}))
        score = _plus_centers(raster, signal)
        if score:
            candidates.append((score, raster))
    if not candidates:
        raise Undefined("no carrier panel with complete plus motifs")
    peak = max(score for score, _ in candidates)
    winners = {raster for score, raster in candidates if score == peak}
    if peak < 2 or len(winners) != 1:
        raise Undefined("plus-panel selector is tied")
    return next(iter(winners))


def _largest_allowed_rectangles(value: Grid, allowed: frozenset[int]) -> tuple[tuple[int, int, int, int], ...]:
    """Return every maximum-area rectangle containing only ``allowed`` colors."""

    height, width = _shape(value)
    bars = [0] * width
    best_area = 0
    boxes: set[tuple[int, int, int, int]] = set()
    for bottom in range(height):
        for column in range(width):
            bars[column] = bars[column] + 1 if value[bottom][column] in allowed else 0
        stack: list[tuple[int, int]] = []
        for column in range(width + 1):
            current = bars[column] if column < width else 0
            start = column
            while stack and stack[-1][1] > current:
                left, bar_height = stack.pop()
                start = left
                if bar_height >= 3 and column - left >= 3:
                    area = bar_height * (column - left)
                    box = bottom - bar_height + 1, bottom, left, column - 1
                    if area > best_area:
                        best_area, boxes = area, {box}
                    elif area == best_area:
                        boxes.add(box)
            if not stack or stack[-1][1] < current:
                stack.append((start, current))
    return tuple(sorted(boxes))


def _marker_cross_projection(value: Grid) -> Grid:
    carrier = _background(value)
    palette = sorted({cell for row in value for cell in row} - {carrier})
    candidates: list[tuple[int, tuple[int, int, int, int], int]] = []
    for marker in palette:
        for box in _largest_allowed_rectangles(value, frozenset((carrier, marker))):
            raster = _crop(value, box)
            counts = Counter(cell for row in raster for cell in row)
            area = len(raster) * len(raster[0])
            marker_count = counts[marker]
            if counts[carrier] < 3 * marker_count or not 1 <= marker_count <= max(1, area // 5):
                continue
            points = {
                (row, column)
                for row, source_row in enumerate(raster)
                for column, cell in enumerate(source_row)
                if cell == marker
            }
            if any(
                (row + dr, column + dc) in points
                for row, column in points
                for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1))
            ):
                continue
            candidates.append((area, box, marker))
    if not candidates:
        raise Undefined("no low-entropy marker rectangle")
    best_area = max(item[0] for item in candidates)
    winners = {(box, marker) for area, box, marker in candidates if area == best_area}
    if len(winners) != 1:
        raise Undefined("marker rectangle is tied")
    box, marker = next(iter(winners))
    raster = [list(row) for row in _crop(value, box)]
    rows = {row for row, line in enumerate(raster) if marker in line}
    columns = {
        column
        for column in range(len(raster[0]))
        if any(raster[row][column] == marker for row in range(len(raster)))
    }
    for row in range(len(raster)):
        for column in range(len(raster[0])):
            if row in rows or column in columns:
                raster[row][column] = marker
    return tuple(tuple(row) for row in raster)


def _domino_palette_recode(value: Grid) -> Grid:
    background = _background(value)
    components = _components(value, background, monochrome=False)
    mains: list[Component] = []
    for component in components:
        raster = _crop(value, component.box)
        palette = {cell for row in raster for cell in row}
        if (
            component.area == component.height * component.width
            and component.area >= 12
            and len(palette) >= 3
        ):
            mains.append(component)
    if not mains:
        raise Undefined("filled multicolor exemplar is absent")
    peak = max(component.area for component in mains)
    winners = [component for component in mains if component.area == peak]
    if len(winners) != 1:
        raise Undefined("main exemplar is tied")
    main = winners[0]
    raster = _crop(value, main.box)
    carrier = _strict_mode(cell for row in raster for cell in row)
    main_palette = {cell for row in raster for cell in row}
    payload = main_palette - {carrier}
    main_cells = set(main.cells)
    mapping: dict[int, int] = {}
    key_count = 0
    for component in components:
        if set(component.cells) == main_cells:
            continue
        colors = {value[row][column] for row, column in component.cells}
        if component.area != 2 or len(colors) != 2:
            raise Undefined("non-key component accompanies the exemplar")
        source_options = colors & payload
        replacement_options = colors - main_palette
        if len(source_options) != 1 or len(replacement_options) != 1:
            raise Undefined("domino key does not cross the exemplar palette")
        source, replacement = next(iter(source_options)), next(iter(replacement_options))
        if source in mapping and mapping[source] != replacement:
            raise Undefined("palette key conflicts")
        mapping[source] = replacement
        key_count += 1
    if key_count < 2 or set(mapping) != payload:
        raise Undefined("palette keys do not cover the exemplar payload")
    return tuple(tuple(mapping.get(cell, cell) for cell in row) for row in raster)


def _rectangle_histogram(value: Grid, program: Mapping[str, Any]) -> Grid:
    background = _background(value)
    colors = sorted({cell for row in value for cell in row} - {background})
    if not 3 <= len(colors) <= 8:
        raise Undefined("rectangle population outside the bounded grammar")
    records: list[tuple[int, int]] = []
    measure = str(program["measure"])
    for color in colors:
        points = {
            (row, column)
            for row, source_row in enumerate(value)
            for column, cell in enumerate(source_row)
            if cell == color
        }
        top, bottom, left, right = _bbox(points)
        # Every absent cell inside the color's inferred rectangle must be
        # explained by another foreground layer, never by empty background.
        if any(
            value[row][column] == background
            for row in range(top, bottom + 1)
            for column in range(left, right + 1)
        ):
            raise Undefined("color layer is not an occluded solid rectangle")
        extent = bottom - top + 1 if measure == "height" else right - left + 1
        records.append((extent, color))
    if len({extent for extent, _ in records}) != len(records):
        raise Undefined("rectangle extents are tied")
    records.sort(reverse=program["order"] == "descending")
    maximum = max(extent for extent, _ in records)
    layout, alignment = str(program["layout"]), str(program["alignment"])
    if layout == "columns":
        canvas = [[background for _ in records] for _ in range(maximum)]
        for column, (extent, color) in enumerate(records):
            start = 0 if alignment == "start" else maximum - extent
            for row in range(start, start + extent):
                canvas[row][column] = color
    elif layout == "rows":
        canvas = [[background for _ in range(maximum)] for _ in records]
        for row, (extent, color) in enumerate(records):
            start = 0 if alignment == "start" else maximum - extent
            for column in range(start, start + extent):
                canvas[row][column] = color
    else:
        raise Undefined("unknown histogram layout")
    return tuple(tuple(row) for row in canvas)


def _mask_crop(value: Grid, component: Component, background: int) -> Grid:
    cells = set(component.cells)
    top, bottom, left, right = component.box
    color = int(component.color)
    return tuple(
        tuple(color if (row, column) in cells else background for column in range(left, right + 1))
        for row in range(top, bottom + 1)
    )


def _support_raster(value: Grid, foreground: int, background: int) -> Grid:
    return tuple(tuple(int(cell == foreground) for cell in row) for row in value)


def _dominant_prototype(value: Grid) -> Grid:
    background = _background(value)
    counts = Counter(cell for row in value for cell in row if cell != background)
    if len(counts) < 2:
        raise Undefined("prototype field has too few colors")
    peak = max(counts.values())
    winners = [color for color, count in counts.items() if count == peak]
    if len(winners) != 1:
        raise Undefined("dominant prototype color is tied")
    color = winners[0]
    components = tuple(
        component
        for component in _components(value, background, monochrome=True)
        if component.color == color
    )
    if len(components) < 4:
        raise Undefined("prototype population is too small")
    records: list[tuple[Grid, Grid, Component]] = []
    for component in components:
        raster = _mask_crop(value, component, background)
        mask = _support_raster(raster, color, background)
        canonical_mask = min(_d4(mask))
        records.append((canonical_mask, raster, component))
    classes = Counter(mask for mask, _, _ in records)
    if len(classes) == 1:
        orientations = Counter(raster for _, raster, _ in records)
        frequency = max(orientations.values())
        orientation_winners = [raster for raster, count in orientations.items() if count == frequency]
        if len(orientation_winners) != 1:
            raise Undefined("prototype orientation is tied")
        return orientation_winners[0]
    singleton_records = [
        (component.area, raster)
        for mask, raster, component in records
        if classes[mask] == 1
    ]
    if not singleton_records:
        raise Undefined("no exceptional prototype class")
    smallest = min(area for area, _ in singleton_records)
    exceptional = {raster for area, raster in singleton_records if area == smallest}
    if len(exceptional) != 1:
        raise Undefined("exceptional prototype is tied")
    return next(iter(exceptional))


def _has_reflection(value: Grid) -> int:
    variants = tuple(
        _transform(value, turns, True)
        for turns in range(4)
    )
    return int(any(candidate == value for candidate in variants))


def _symmetry_scalar(value: Grid, program: Mapping[str, Any]) -> Grid:
    mapping = {int(key): int(color) for key, color in program["mapping"]}
    feature = _has_reflection(value)
    if feature not in mapping:
        raise Undefined("unseen symmetry class")
    return ((mapping[feature],),)


def _execute(program: Mapping[str, Any], value: Grid) -> Grid:
    if program.get("schema") != SCHEMA:
        raise Undefined("unsupported program schema")
    operator = program.get("operator")
    if operator == "plus_panel_extract":
        return _plus_panel_extract(value)
    if operator == "marker_cross_projection":
        return _marker_cross_projection(value)
    if operator == "domino_palette_recode":
        return _domino_palette_recode(value)
    if operator == "rectangle_histogram":
        return _rectangle_histogram(value, program)
    if operator == "dominant_prototype":
        return _dominant_prototype(value)
    if operator == "symmetry_scalar":
        return _symmetry_scalar(value, program)
    raise Undefined("unknown operator")


def execute_program(program: Mapping[str, Any], value: Any) -> list[list[int]]:
    """Execute one serialized subscene program on a grid."""

    if not isinstance(program, Mapping):
        raise ValueError("program must be a mapping")
    return _plain(_execute(program, _grid(value)))


def replay_program(program: Mapping[str, Any], value: Any) -> list[list[int]]:
    """Tournament replay hook."""

    return execute_program(program, value)


# ---------------------------------------------------------------------------
# Finite induction and falsification


def _program(operator: str, length: int, **parameters: Any) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "operator": operator,
        "description_length": length,
        **parameters,
    }


_FIXED_PROGRAMS: tuple[dict[str, Any], ...] = (
    _program("plus_panel_extract", 10),
    _program("marker_cross_projection", 12),
    _program("domino_palette_recode", 11),
    _program("dominant_prototype", 11),
)


def _infer_programs(train: Sequence[Pair]) -> tuple[dict[str, Any], ...]:
    programs = list(_FIXED_PROGRAMS)
    for measure in ("height", "width"):
        for layout in ("columns", "rows"):
            for alignment in ("start", "end"):
                for order in ("descending", "ascending"):
                    programs.append(
                        _program(
                            "rectangle_histogram",
                            9,
                            measure=measure,
                            layout=layout,
                            alignment=alignment,
                            order=order,
                        )
                    )
    # The scalar codebook is task-local: both structural classes must occur at
    # least twice, which makes every LOO prediction independently recoverable.
    if train and all(_shape(target) == (1, 1) for _, target in train):
        observations: dict[int, set[int]] = defaultdict(set)
        frequencies: Counter[int] = Counter()
        for source, target in train:
            feature = _has_reflection(source)
            observations[feature].add(target[0][0])
            frequencies[feature] += 1
        if (
            set(observations) == {0, 1}
            and all(len(colors) == 1 for colors in observations.values())
            and all(frequencies[key] >= 2 for key in (0, 1))
        ):
            mapping = [[key, next(iter(observations[key]))] for key in (0, 1)]
            programs.append(_program("symmetry_scalar", 7, mapping=mapping))
    unique = {_canonical(program): program for program in programs}
    return tuple(unique[key] for key in sorted(unique))


def _behavior(program: Mapping[str, Any], grids: Sequence[Grid]) -> tuple[Grid, ...]:
    return tuple(_execute(program, grid) for grid in grids)


def _exact_programs(
    train: Sequence[Pair],
    tests: Sequence[Grid],
    *,
    operator: str | None = None,
) -> tuple[list[tuple[dict[str, Any], tuple[Grid, ...]]], int]:
    expected = tuple(target for _, target in train)
    exact: list[tuple[dict[str, Any], tuple[Grid, ...]]] = []
    calls = 0
    for program in _infer_programs(train):
        if operator is not None and program["operator"] != operator:
            continue
        try:
            replay = _behavior(program, tuple(source for source, _ in train))
            calls += len(train)
            if replay != expected:
                continue
            predictions = _behavior(program, tests)
            calls += len(tests)
        except (Undefined, TypeError, ValueError, KeyError, IndexError, ZeroDivisionError):
            continue
        exact.append((program, predictions))
    return exact, calls


def _unique_behavior(
    exact: Sequence[tuple[dict[str, Any], tuple[Grid, ...]]]
) -> tuple[str, list[tuple[dict[str, Any], tuple[Grid, ...]]]]:
    groups: dict[str, list[tuple[dict[str, Any], tuple[Grid, ...]]]] = defaultdict(list)
    for program, outputs in exact:
        groups[_digest([_plain(grid) for grid in outputs])].append((program, outputs))
    if len(groups) != 1:
        raise Undefined("exact grammar has zero or multiple held-out behaviors")
    return next(iter(sorted(groups.items())))


def _loo_check(train: Sequence[Pair], operator: str) -> int:
    checks = 0
    for held_index, (held_source, held_target) in enumerate(train):
        remaining = tuple(pair for index, pair in enumerate(train) if index != held_index)
        exact, _ = _exact_programs(remaining, (held_source,), operator=operator)
        _, group = _unique_behavior(exact)
        predictions = {outputs[0] for _, outputs in group}
        if predictions != {held_target}:
            raise Undefined("leave-one-out re-induction missed the held demonstration")
        checks += 1
    return checks


def _map_palette(value: Grid, mapping: Mapping[int, int]) -> Grid:
    return tuple(tuple(mapping[cell] for cell in row) for row in value)


def _counterfactual_check(
    train: Sequence[Pair],
    tests: Sequence[Grid],
    predictions: Sequence[Grid],
    operator: str,
    limits: Limits,
) -> tuple[int, int]:
    d4_checks = 0
    palette_checks = 0
    for turns in range(4):
        for reflected in (False, True):
            transformed_train = tuple(
                (
                    _transform(source, turns, reflected),
                    _transform(target, turns, reflected),
                )
                for source, target in train
            )
            transformed_tests = tuple(_transform(source, turns, reflected) for source in tests)
            expected = tuple(_transform(output, turns, reflected) for output in predictions)
            exact, _ = _exact_programs(
                transformed_train, transformed_tests, operator=operator
            )
            _, group = _unique_behavior(exact)
            if {outputs for _, outputs in group} != {expected}:
                raise Undefined("D4 counterfactual does not commute")
            d4_checks += len(train) + len(tests)
            if d4_checks + palette_checks > limits.max_counterfactual_checks:
                raise Undefined("counterfactual cap exhausted")
    permutations = (
        {color: (color + 1) % 10 for color in range(10)},
        {color: 9 - color for color in range(10)},
    )
    for mapping in permutations:
        transformed_train = tuple(
            (_map_palette(source, mapping), _map_palette(target, mapping))
            for source, target in train
        )
        transformed_tests = tuple(_map_palette(source, mapping) for source in tests)
        expected = tuple(_map_palette(output, mapping) for output in predictions)
        exact, _ = _exact_programs(transformed_train, transformed_tests, operator=operator)
        _, group = _unique_behavior(exact)
        if {outputs for _, outputs in group} != {expected}:
            raise Undefined("palette counterfactual does not commute")
        palette_checks += len(train) + len(tests)
        if d4_checks + palette_checks > limits.max_counterfactual_checks:
            raise Undefined("counterfactual cap exhausted")
    return d4_checks, palette_checks


def compile_task(task: Any, limits: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    """Compile one proof-carrying held-out behavior, otherwise abstain."""

    try:
        bounds = Limits.from_value(limits)
        train, tests = _sanitize(task, bounds)
        # This lane is intentionally scoped to output compression.
        if not all(
            len(source) * len(source[0]) > len(target) * len(target[0])
            for source, target in train
        ):
            return []
        programs = _infer_programs(train)
        if len(programs) > bounds.max_programs:
            return []
        exact, calls = _exact_programs(train, tests)
        if not exact or calls > bounds.max_executor_calls:
            return []
        behavior_hash, equivalents = _unique_behavior(exact)
        equivalents.sort(
            key=lambda item: (int(item[0]["description_length"]), _canonical(item[0]))
        )
        representative, predictions = equivalents[0]
        operator = str(representative["operator"])
        loo_checks = _loo_check(train, operator)
        d4_checks, palette_checks = _counterfactual_check(
            train, tests, predictions, operator, bounds
        )
        replay = _behavior(representative, tuple(source for source, _ in train))
        expected = tuple(target for _, target in train)
        if replay != expected:
            return []
    except (Undefined, TypeError, ValueError, KeyError, IndexError, ZeroDivisionError):
        return []
    candidate = {
        "family": "subscene_extraction_compiler",
        "program": json.loads(_canonical(representative)),
        "train_outputs": [_plain(grid) for grid in replay],
        "test_outputs": [_plain(grid) for grid in predictions],
        "complexity": int(representative["description_length"]),
        "evidence": {
            "all_demonstrations_exact": True,
            "exact_replay": True,
            "serialized_replay_program": True,
            "finite_enumeration_complete": True,
            "programs_enumerated": len(programs),
            "exact_programs": len(exact),
            "full_test_behavior_classes": 1,
            "full_test_behavior_hash": behavior_hash,
            "equivalent_programs": len(equivalents),
            "loo_reinductions": loo_checks,
            "d4_counterfactual_checks": d4_checks,
            "palette_counterfactual_checks": palette_checks,
            "bounded_search": True,
            "hard_caps_exhausted": False,
            "task_identity_observed": False,
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
    "compile_task",
    "execute_program",
    "replay_program",
]
