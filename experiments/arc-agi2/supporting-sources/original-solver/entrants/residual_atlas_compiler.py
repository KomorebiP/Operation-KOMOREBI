"""Retrospective residual-atlas compiler for Block 15.

This finite grammar was developed after inspecting the public-training
residuals and their scores.  It therefore makes a deliberately narrow,
score-seeded claim.  The runtime sees only a task's demonstrations and
unlabelled test inputs; task identities, corpus fingerprints, held outputs,
literal coordinates, and literal ARC colors are not available to it.

The first atlas contains six reusable task-local constructions:

* crop the rectangle bounded by the uniquely defective divider lines;
* select a prototype containing the run-length quotient of a large clue;
* recolor a solid-rectangle atlas from an ordered border legend;
* project content rows into the slots of a divider-separated template; and
* translate monochrome pieces into a unique square-perimeter exact cover; and
* pack freely oriented pieces into a minimum-perimeter rectangle, orienting
  the global solution by its largest piece and preserved scene order.

Every emitted behavior exactly replays all demonstrations, survives genuine
leave-one-out re-induction, has one held-out behavior across all exact
programs, and commutes with D4 and two bijective palette counterfactuals.

Author: Komorebi P.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
import hashlib
import json
from typing import Any


Grid = tuple[tuple[int, ...], ...]
Cell = tuple[int, int]
Pair = tuple[Grid, Grid]
SCHEMA = "komorebi.pr_lasm.block15.residual_atlas.program.v1"
AUTHOR = "Komorebi P."
DEVELOPMENT_REGIME = "retrospective_score_seeded_public_training_residual_atlas"


class Undefined(ValueError):
    """A structural role is absent, ambiguous, or exceeds a hard cap."""


@dataclass(frozen=True, slots=True)
class Limits:
    max_grid_cells: int = 900
    max_examples: int = 16
    max_programs: int = 16
    max_executor_calls: int = 20_000
    max_counterfactual_checks: int = 512
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
            "max_programs": 64,
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
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
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
    if not (0 <= top <= bottom < len(value) and 0 <= left <= right < len(value[0])):
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


def _inverse_transform(value: Grid, quarter_turns: int, reflected: bool) -> Grid:
    # F R^k is an involution; the inverse of R^k is R^(4-k).
    if reflected:
        return _transform(value, quarter_turns, True)
    return _transform(value, -quarter_turns, False)


def _map_palette(value: Grid, mapping: Mapping[int, int]) -> Grid:
    return tuple(tuple(mapping[cell] for cell in row) for row in value)


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
        # Any injected held-out output is deliberately ignored.
        tests.append(_grid(example.get("input"), limits))
    return tuple(train), tuple(tests)


def _oriented_unique(solver: Callable[[Grid], Grid], value: Grid) -> Grid:
    outputs: set[Grid] = set()
    for turns in range(4):
        for reflected in (False, True):
            transformed = _transform(value, turns, reflected)
            try:
                result = solver(transformed)
                outputs.add(_inverse_transform(result, turns, reflected))
            except (Undefined, TypeError, ValueError, KeyError, IndexError):
                continue
    if len(outputs) != 1:
        raise Undefined("orientation search has zero or multiple behaviors")
    return next(iter(outputs))


# ---------------------------------------------------------------------------
# Defective-divider rectangle extraction


def _defective_divider_crop(value: Grid) -> Grid:
    height, width = _shape(value)
    background = _background(value)
    colors = sorted({cell for row in value for cell in row} - {background})
    outputs: set[Grid] = set()
    for color in colors:
        row_lines = [
            row for row in range(height)
            if sum(value[row][column] == color for column in range(width)) > width // 2
        ]
        column_lines = [
            column for column in range(width)
            if sum(value[row][column] == color for row in range(height)) > height // 2
        ]
        if len(row_lines) < 3 or len(column_lines) < 3:
            continue
        row_steps = {b - a for a, b in zip(row_lines, row_lines[1:])}
        column_steps = {b - a for a, b in zip(column_lines, column_lines[1:])}
        if len(row_steps) != 1 or len(column_steps) != 1:
            continue
        defective_rows = [
            row for row in row_lines
            if any(value[row][column] != color for column in range(width))
        ]
        defective_columns = [
            column for column in column_lines
            if any(value[row][column] != color for row in range(height))
        ]
        if len(defective_rows) != 2 or len(defective_columns) != 2:
            continue
        holes = {(row, column) for row in defective_rows for column in defective_columns}
        valid = True
        for row in row_lines:
            for column in range(width):
                expected_hole = (row, column) in holes
                if (value[row][column] == color) == expected_hole:
                    valid = False
        for column in column_lines:
            for row in range(height):
                expected_hole = (row, column) in holes
                if (value[row][column] == color) == expected_hole:
                    valid = False
        if not valid or any(value[row][column] != background for row, column in holes):
            continue
        if any(
            value[row][column] == color
            and row not in row_lines
            and column not in column_lines
            for row in range(height)
            for column in range(width)
        ):
            continue
        outputs.add(_crop(value, (min(defective_rows), max(defective_rows),
                                  min(defective_columns), max(defective_columns))))
    if len(outputs) != 1:
        raise Undefined("defective divider roles are ambiguous")
    return next(iter(outputs))


# ---------------------------------------------------------------------------
# Run-length quotient prototype extraction


def _binary_crop(value: Grid, color: int) -> Grid:
    cells = {
        (row, column)
        for row in range(len(value))
        for column in range(len(value[0]))
        if value[row][column] == color
    }
    top, bottom, left, right = _bbox(cells)
    return tuple(
        tuple(int(value[row][column] == color) for column in range(left, right + 1))
        for row in range(top, bottom + 1)
    )


def _collapse_adjacent_runs(value: Grid) -> Grid:
    result = value
    while True:
        rows = tuple(row for index, row in enumerate(result) if index == 0 or row != result[index - 1])
        columns = tuple(zip(*rows))
        reduced_columns = tuple(
            column for index, column in enumerate(columns)
            if index == 0 or column != columns[index - 1]
        )
        reduced = tuple(tuple(row) for row in zip(*reduced_columns))
        if reduced == result:
            return result
        result = reduced


def _contains_mask(container: Grid, needle: Grid) -> bool:
    ch, cw = _shape(container)
    nh, nw = _shape(needle)
    if nh > ch or nw > cw:
        return False
    return any(
        all(container[top + row][left + column] == needle[row][column]
            for row in range(nh) for column in range(nw))
        for top in range(ch - nh + 1)
        for left in range(cw - nw + 1)
    )


def _prototype_quotient_extract(value: Grid) -> Grid:
    background = _background(value)
    colors = sorted({cell for row in value for cell in row} - {background})
    if len(colors) != 3:
        raise Undefined("prototype scene must have exactly three object colors")
    counts = {color: sum(cell == color for row in value for cell in row) for color in colors}
    peak = max(counts.values())
    large = [color for color in colors if counts[color] == peak]
    if len(large) != 1:
        raise Undefined("large clue color is tied")
    clue = large[0]
    clue_mask = _binary_crop(value, clue)
    quotient = _collapse_adjacent_runs(clue_mask)
    if quotient == clue_mask or min(_shape(quotient)) < 1:
        raise Undefined("large clue has no run-length quotient")
    matches: list[int] = []
    for color in colors:
        if color == clue:
            continue
        mask = _binary_crop(value, color)
        if _contains_mask(mask, quotient):
            matches.append(color)
    if len(matches) != 1:
        raise Undefined("quotient does not select one prototype")
    selected = matches[0]
    cells = {
        (row, column)
        for row in range(len(value)) for column in range(len(value[0]))
        if value[row][column] == selected
    }
    result = _crop(value, _bbox(cells))
    if any(cell not in {background, selected} for row in result for cell in row):
        raise Undefined("prototype crop contains a foreign object")
    return result


# ---------------------------------------------------------------------------
# Ordered border legend to solid-rectangle atlas


def _legend_rectangle_left(value: Grid) -> Grid:
    height, width = _shape(value)
    background = _background(value)
    all_colors = {cell for row in value for cell in row}
    bars: list[tuple[int, int]] = []
    for color in sorted(all_colors - {background}):
        cells = [(row, column) for row in range(height) for column in range(width)
                 if value[row][column] == color]
        columns = {column for _, column in cells}
        if len(cells) == height and len(columns) == 1:
            bars.append((next(iter(columns)), color))
    bars.sort()
    if len(bars) < 3:
        raise Undefined("border legend is too short")
    if [column for column, _ in bars] != list(range(1, 2 * len(bars), 2)):
        raise Undefined("legend bars are not the alternating border prefix")
    legend_colors = [color for _, color in bars]
    if len(set(legend_colors)) != len(legend_colors):
        raise Undefined("legend colors are not unique")
    prefix_end = 2 * len(bars)
    if prefix_end >= width:
        raise Undefined("legend leaves no atlas")
    for row in range(height):
        for column in range(prefix_end + 1):
            expected = legend_colors[(column - 1) // 2] if column % 2 else background
            if value[row][column] != expected:
                raise Undefined("legend prefix contains scene ink")
    remaining = all_colors - {background, *legend_colors}
    if len(remaining) != 1:
        raise Undefined("atlas must use one generic ink color")
    ink = next(iter(remaining))
    intervals: list[tuple[int, int] | None] = []
    for column in range(prefix_end + 1, width):
        rows = [row for row in range(height) if value[row][column] == ink]
        if not rows:
            intervals.append(None)
            continue
        if rows != list(range(min(rows), max(rows) + 1)):
            raise Undefined("atlas column is not a solid interval")
        intervals.append((min(rows), max(rows)))
    groups: list[tuple[int, int, int, int]] = []
    index = 0
    while index < len(intervals):
        if intervals[index] is None:
            index += 1
            continue
        start = index
        interval = intervals[index]
        while index + 1 < len(intervals) and intervals[index + 1] == interval:
            index += 1
        assert interval is not None
        groups.append((interval[0], interval[1], prefix_end + 1 + start,
                       prefix_end + 1 + index))
        index += 1
    if len(groups) != len(legend_colors):
        raise Undefined("legend length does not match the rectangle partition")
    ink_cells = {
        (row, column) for row in range(height) for column in range(width)
        if value[row][column] == ink
    }
    covered = {
        (row, column)
        for top, bottom, left, right in groups
        for row in range(top, bottom + 1)
        for column in range(left, right + 1)
    }
    if ink_cells != covered:
        raise Undefined("rectangle groups do not exactly cover the atlas")
    output = [[background] * width for _ in range(height)]
    for color, (top, bottom, left, right) in zip(legend_colors, groups):
        for row in range(top, bottom + 1):
            for column in range(left, right + 1):
                output[row][column] = color
    return tuple(tuple(row) for row in output)


def _legend_rectangle_recolor(value: Grid) -> Grid:
    return _oriented_unique(_legend_rectangle_left, value)


# ---------------------------------------------------------------------------
# Separator-mediated template/content projection


def _project_vertical_parts(
    content: Grid, template: Grid, *, background: int, divider: int
) -> Grid:
    height, content_width = _shape(content)
    if len(template) != height:
        raise Undefined("panels have different heights")
    template_width = len(template[0])
    template_colors = {cell for row in template for cell in row} - {background}
    if len(template_colors) != 1 or divider in template_colors:
        raise Undefined("template does not have one marker color")
    marker = next(iter(template_colors))
    if marker in {cell for row in content for cell in row}:
        raise Undefined("template marker leaks into content")

    suffix_start = next(
        (row for row in range(height) if all(cell == divider for cell in content[row])),
        None,
    )
    if suffix_start is None or suffix_start < 3 or height - suffix_start < 2:
        raise Undefined("content lacks an active prefix and divider suffix")
    if any(any(cell != divider for cell in content[row]) for row in range(suffix_start, height)):
        raise Undefined("divider suffix is incomplete")
    active = content[:suffix_start]
    if len(active) % 2 != 1 or content_width % 2 != 1:
        raise Undefined("content alternation is not odd-length")
    base = active[0]
    if any(active[row] != base for row in range(0, len(active), 2)):
        raise Undefined("base rows disagree")
    background_positions = tuple(range(0, content_width, 2))
    anchor_positions = tuple(range(1, content_width, 2))
    if not anchor_positions or any(base[pos] != background for pos in background_positions):
        raise Undefined("base row lacks alternating background positions")
    if any(base[pos] in {background, divider, marker} for pos in anchor_positions):
        raise Undefined("anchor roles are invalid")
    payloads: list[tuple[int, tuple[int, ...]]] = []
    for row in range(1, len(active), 2):
        line = active[row]
        values = {line[pos] for pos in background_positions}
        if len(values) != 1:
            raise Undefined("payload background positions disagree")
        fill = next(iter(values))
        anchor_values = tuple(line[pos] for pos in anchor_positions)
        if fill in {background, divider, marker}:
            raise Undefined("payload fill collides with a structural role")
        if any(color in {background, divider, marker} for color in anchor_values):
            raise Undefined("payload anchor collides with a structural role")
        payloads.append((fill, anchor_values))

    supports = [
        frozenset(column for column, cell in enumerate(row) if cell == marker)
        for row in template
    ]
    nonempty = [support for support in supports if support]
    distinct = sorted(set(nonempty), key=lambda support: (len(support), tuple(sorted(support))))
    if len(distinct) != 2:
        raise Undefined("template must have sparse and dense marker rows")
    sparse, dense = distinct
    if not sparse < dense or len(sparse) != len(anchor_positions):
        raise Undefined("sparse template support does not encode the anchors")
    if supports[0] != sparse or supports[-1] != sparse:
        raise Undefined("sparse supports must bound the template")
    dense_rows = [row for row, support in enumerate(supports) if support == dense]
    if len(dense_rows) != len(payloads):
        raise Undefined("payload count does not match template slots")
    if any(support not in {frozenset(), sparse, dense} for support in supports):
        raise Undefined("template contains an unrecognized marker line")

    output = [[background] * template_width for _ in range(height)]
    sparse_columns = sorted(sparse)
    anchor_values = [base[pos] for pos in anchor_positions]
    for row in range(height):
        for column, color in zip(sparse_columns, anchor_values):
            output[row][column] = color
    for row, (fill, slot_values) in zip(dense_rows, payloads):
        for column in range(template_width):
            if column not in sparse:
                output[row][column] = fill
        for column, color in zip(sparse_columns, slot_values):
            output[row][column] = color
    return tuple(tuple(row) for row in output)


def _template_projection_vertical(value: Grid) -> Grid:
    height, width = _shape(value)
    background = _background(value)
    dividers: list[tuple[int, int]] = []
    for column in range(1, width - 1):
        colors = {value[row][column] for row in range(height)}
        if len(colors) == 1:
            color = next(iter(colors))
            if color != background:
                dividers.append((column, color))
    if len(dividers) != 1:
        raise Undefined("there is not one nonbackground full divider")
    column, divider = dividers[0]
    left = tuple(tuple(row[:column]) for row in value)
    right = tuple(tuple(row[column + 1 :]) for row in value)
    outputs: set[Grid] = set()
    for content, template in ((left, right), (right, left)):
        if not content[0] or not template[0]:
            continue
        try:
            outputs.add(_project_vertical_parts(
                content, template, background=background, divider=divider
            ))
        except (Undefined, TypeError, ValueError, KeyError, IndexError):
            continue
    if len(outputs) != 1:
        raise Undefined("content/template assignment is ambiguous")
    return next(iter(outputs))


def _template_content_projection(value: Grid) -> Grid:
    return _oriented_unique(_template_projection_vertical, value)


# ---------------------------------------------------------------------------
# Translation-only square-perimeter exact cover


def _monochrome_components(value: Grid, background: int) -> tuple[tuple[int, frozenset[Cell]], ...]:
    height, width = _shape(value)
    remaining = {
        (row, column)
        for row in range(height) for column in range(width)
        if value[row][column] != background
    }
    result: list[tuple[int, frozenset[Cell]]] = []
    while remaining:
        seed = min(remaining)
        remaining.remove(seed)
        color = value[seed[0]][seed[1]]
        cells = {seed}
        queue = [seed]
        while queue:
            row, column = queue.pop()
            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                point = row + dr, column + dc
                if point in remaining and value[point[0]][point[1]] == color:
                    remaining.remove(point)
                    cells.add(point)
                    queue.append(point)
        result.append((color, frozenset(cells)))
    return tuple(result)


def _square_perimeter_jigsaw(value: Grid) -> Grid:
    background = _background(value)
    components = _monochrome_components(value, background)
    if not 2 <= len(components) <= 12:
        raise Undefined("perimeter jigsaw has an invalid piece count")
    total = sum(len(cells) for _, cells in components)
    if (total + 4) % 4:
        raise Undefined("piece area is not a square perimeter")
    size = (total + 4) // 4
    if not 3 <= size <= 15 or size * size >= len(value) * len(value[0]):
        raise Undefined("derived perimeter canvas is invalid")
    perimeter = {
        (row, column)
        for row in range(size) for column in range(size)
        if row in {0, size - 1} or column in {0, size - 1}
    }
    pieces: list[tuple[int, tuple[frozenset[Cell], ...]]] = []
    for color, cells in components:
        top, bottom, left, right = _bbox(cells)
        normalized = {(row - top, column - left) for row, column in cells}
        piece_height, piece_width = bottom - top + 1, right - left + 1
        placements = {
            frozenset((row + dr, column + dc) for row, column in normalized)
            for dr in range(size - piece_height + 1)
            for dc in range(size - piece_width + 1)
            if all((row + dr, column + dc) in perimeter for row, column in normalized)
        }
        if not placements or len(placements) > 128:
            raise Undefined("piece placement domain is empty or too large")
        pieces.append((color, tuple(sorted(placements, key=lambda cells: tuple(sorted(cells))))))
    pieces.sort(key=lambda item: (len(item[1]), item[0], tuple(sorted(item[1][0]))))
    outputs: set[Grid] = set()
    calls = 0

    def visit(index: int, occupied: frozenset[Cell], assignments: tuple[tuple[int, frozenset[Cell]], ...]) -> None:
        nonlocal calls
        calls += 1
        if calls > 100_000:
            raise Undefined("perimeter exact-cover cap exhausted")
        if len(outputs) > 1:
            return
        if index == len(pieces):
            if occupied != perimeter:
                return
            canvas = [[background] * size for _ in range(size)]
            for color, cells in assignments:
                for row, column in cells:
                    canvas[row][column] = color
            outputs.add(tuple(tuple(row) for row in canvas))
            return
        color, placements = pieces[index]
        for placement in placements:
            if occupied.isdisjoint(placement):
                visit(index + 1, occupied | placement, assignments + ((color, placement),))

    visit(0, frozenset(), ())
    if len(outputs) != 1:
        raise Undefined("perimeter exact cover has zero or multiple colored rasters")
    return next(iter(outputs))


# ---------------------------------------------------------------------------
# Compact minimum-perimeter rectangle jigsaw


def _normalized_cells(cells: Iterable[Cell]) -> frozenset[Cell]:
    points = frozenset(cells)
    top, _, left, _ = _bbox(points)
    return frozenset((row - top, column - left) for row, column in points)


def _cell_orientations(cells: frozenset[Cell]) -> tuple[frozenset[Cell], ...]:
    normalized = _normalized_cells(cells)
    bottom = max(row for row, _ in normalized)
    right = max(column for _, column in normalized)
    mask = tuple(
        tuple(int((row, column) in normalized) for column in range(right + 1))
        for row in range(bottom + 1)
    )
    variants: set[frozenset[Cell]] = set()
    for turns in range(4):
        for reflected in (False, True):
            transformed = _transform(mask, turns, reflected)
            variants.add(frozenset(
                (row, column)
                for row in range(len(transformed))
                for column in range(len(transformed[0]))
                if transformed[row][column]
            ))
    return tuple(sorted(variants, key=lambda points: tuple(sorted(points))))


def _d4_grid_class(value: Grid) -> tuple[tuple[tuple[int, ...], ...], ...]:
    return min(
        _transform(value, turns, reflected)
        for turns in range(4)
        for reflected in (False, True)
    )


def _compact_rectangle_jigsaw(value: Grid) -> Grid:
    background = _background(value)
    raw_components = _monochrome_components(value, background)
    if not 2 <= len(raw_components) <= 8:
        raise Undefined("compact jigsaw has an invalid piece count")
    area = sum(len(cells) for _, cells in raw_components)
    if not 4 <= area <= 36 or area >= len(value) * len(value[0]):
        raise Undefined("compact jigsaw area is invalid")
    sizes = [len(cells) for _, cells in raw_components]
    largest_size = max(sizes)
    largest = [index for index, size in enumerate(sizes) if size == largest_size]
    if len(largest) != 1:
        raise Undefined("compact jigsaw lacks a unique largest piece")
    anchor_index = largest[0]

    dimensions = [
        (height, area // height)
        for height in range(2, area + 1)
        if area % height == 0 and area // height >= 2
    ]
    if not dimensions:
        raise Undefined("foreground area has no nondegenerate rectangle")
    best_sum = min(height + width for height, width in dimensions)
    dimensions = sorted(set(
        (height, width) for height, width in dimensions if height + width == best_sum
    ))

    source_boxes = [_bbox(cells) for _, cells in raw_components]
    source_masks = [_normalized_cells(cells) for _, cells in raw_components]
    class_keys: set[Grid] = set()
    oriented_scores: dict[Grid, int] = {}
    nodes = 0

    for canvas_height, canvas_width in dimensions:
        domains: list[tuple[int, int, tuple[tuple[frozenset[Cell], bool], ...]]] = []
        for index, (color, cells) in enumerate(raw_components):
            placements: dict[frozenset[Cell], bool] = {}
            for variant in _cell_orientations(cells):
                piece_height = max(row for row, _ in variant) + 1
                piece_width = max(column for _, column in variant) + 1
                if piece_height > canvas_height or piece_width > canvas_width:
                    continue
                preserved = variant == source_masks[index]
                for dr in range(canvas_height - piece_height + 1):
                    for dc in range(canvas_width - piece_width + 1):
                        placement = frozenset((row + dr, column + dc) for row, column in variant)
                        placements[placement] = placements.get(placement, False) or preserved
            if not placements or len(placements) > 512:
                raise Undefined("compact piece domain is empty or too large")
            domain = tuple(sorted(placements.items(), key=lambda item: tuple(sorted(item[0]))))
            domains.append((index, color, domain))
        domains.sort(key=lambda item: (len(item[2]), -len(raw_components[item[0]][1]), item[0]))
        assignments: list[frozenset[Cell] | None] = [None] * len(raw_components)
        anchor_flags: list[bool] = [False] * len(raw_components)

        def preserved_order_score() -> int:
            score = 0
            centroids: list[tuple[int, int, int]] = []
            for placement in assignments:
                assert placement is not None
                centroids.append((
                    sum(row for row, _ in placement),
                    sum(column for _, column in placement),
                    len(placement),
                ))
            for first in range(len(raw_components)):
                a_top, a_bottom, a_left, a_right = source_boxes[first]
                ar, ac, an = centroids[first]
                for second in range(first + 1, len(raw_components)):
                    b_top, b_bottom, b_left, b_right = source_boxes[second]
                    br, bc, bn = centroids[second]
                    if a_bottom < b_top and ar * bn < br * an:
                        score += 1
                    elif b_bottom < a_top and br * an < ar * bn:
                        score += 1
                    if a_right < b_left and ac * bn < bc * an:
                        score += 1
                    elif b_right < a_left and bc * an < ac * bn:
                        score += 1
            return score

        def visit(position: int, occupied: frozenset[Cell]) -> None:
            nonlocal nodes
            nodes += 1
            if nodes > 250_000:
                raise Undefined("compact exact-cover cap exhausted")
            if len(class_keys) > 1:
                return
            if position == len(domains):
                if len(occupied) != area:
                    return
                canvas = [[background] * canvas_width for _ in range(canvas_height)]
                for index, (color, _) in enumerate(raw_components):
                    placement = assignments[index]
                    assert placement is not None
                    for row, column in placement:
                        canvas[row][column] = color
                raster = tuple(tuple(row) for row in canvas)
                class_keys.add(_d4_grid_class(raster))
                if anchor_flags[anchor_index]:
                    score = preserved_order_score()
                    oriented_scores[raster] = max(oriented_scores.get(raster, -1), score)
                return
            index, _, domain = domains[position]
            for placement, preserved in domain:
                if occupied.isdisjoint(placement):
                    assignments[index] = placement
                    anchor_flags[index] = preserved
                    visit(position + 1, occupied | placement)
                    assignments[index] = None
                    anchor_flags[index] = False

        visit(0, frozenset())
        if len(class_keys) > 1:
            break

    if len(class_keys) != 1 or not oriented_scores:
        raise Undefined("compact packings do not form one orientable D4 class")
    peak = max(oriented_scores.values())
    winners = [raster for raster, score in oriented_scores.items() if score == peak]
    if len(winners) != 1:
        raise Undefined("preserved scene order does not select one packing")
    return winners[0]


# ---------------------------------------------------------------------------
# Finite compilation, proof checks, and replay contract


_OPERATORS: dict[str, Callable[[Grid], Grid]] = {
    "defective_divider_crop": _defective_divider_crop,
    "prototype_run_quotient": _prototype_quotient_extract,
    "ordered_legend_rectangles": _legend_rectangle_recolor,
    "template_content_projection": _template_content_projection,
    "square_perimeter_exact_cover": _square_perimeter_jigsaw,
    "compact_rectangle_jigsaw": _compact_rectangle_jigsaw,
}


def _program(operator: str, description_length: int) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "operator": operator,
        "description_length": description_length,
        "development_regime": DEVELOPMENT_REGIME,
    }


_FIXED_PROGRAMS: tuple[dict[str, Any], ...] = (
    _program("defective_divider_crop", 10),
    _program("prototype_run_quotient", 12),
    _program("ordered_legend_rectangles", 14),
    _program("template_content_projection", 17),
    _program("square_perimeter_exact_cover", 18),
    _program("compact_rectangle_jigsaw", 22),
)


def _infer_programs(train: Sequence[Pair]) -> tuple[dict[str, Any], ...]:
    # The grammar is fixed and identity-free.  Re-induction means rerunning
    # this complete enumeration against the supplied demonstration subset.
    del train
    return _FIXED_PROGRAMS


def _execute(program: Mapping[str, Any], value: Grid) -> Grid:
    if program.get("schema") != SCHEMA:
        raise Undefined("unsupported program schema")
    operator = program.get("operator")
    if operator not in _OPERATORS:
        raise Undefined("unknown operator")
    return _OPERATORS[str(operator)](value)


def execute_program(program: Mapping[str, Any], value: Any) -> list[list[int]]:
    """Execute one serialized residual-atlas program on one raster."""
    if not isinstance(program, Mapping):
        raise ValueError("program must be a mapping")
    return _plain(_execute(program, _grid(value)))


def replay_program(program: Mapping[str, Any], value: Any) -> list[list[int]]:
    """Tournament replay hook."""
    return execute_program(program, value)


def _behavior(program: Mapping[str, Any], grids: Sequence[Grid]) -> tuple[Grid, ...]:
    return tuple(_execute(program, grid) for grid in grids)


def _exact_programs(
    train: Sequence[Pair], tests: Sequence[Grid]
) -> tuple[list[tuple[dict[str, Any], tuple[Grid, ...]]], int]:
    expected = tuple(target for _, target in train)
    exact: list[tuple[dict[str, Any], tuple[Grid, ...]]] = []
    calls = 0
    for program in _infer_programs(train):
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


def _loo_check(train: Sequence[Pair]) -> int:
    checks = 0
    for held_index, (held_source, held_target) in enumerate(train):
        remaining = tuple(pair for index, pair in enumerate(train) if index != held_index)
        exact, _ = _exact_programs(remaining, (held_source,))
        _, group = _unique_behavior(exact)
        if {outputs[0] for _, outputs in group} != {held_target}:
            raise Undefined("leave-one-out re-induction missed a demonstration")
        checks += 1
    return checks


def _counterfactual_check(
    train: Sequence[Pair], tests: Sequence[Grid], predictions: Sequence[Grid], limits: Limits
) -> tuple[int, int]:
    d4_checks = 0
    palette_checks = 0
    for turns in range(4):
        for reflected in (False, True):
            transformed_train = tuple(
                (_transform(source, turns, reflected), _transform(target, turns, reflected))
                for source, target in train
            )
            transformed_tests = tuple(_transform(source, turns, reflected) for source in tests)
            expected = tuple(_transform(output, turns, reflected) for output in predictions)
            exact, _ = _exact_programs(transformed_train, transformed_tests)
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
        exact, _ = _exact_programs(transformed_train, transformed_tests)
        _, group = _unique_behavior(exact)
        if {outputs for _, outputs in group} != {expected}:
            raise Undefined("palette counterfactual does not commute")
        palette_checks += len(train) + len(tests)
        if d4_checks + palette_checks > limits.max_counterfactual_checks:
            raise Undefined("counterfactual cap exhausted")
    return d4_checks, palette_checks


def compile_task(task: Any, limits: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    """Compile one proof-carrying atlas behavior, otherwise abstain."""
    try:
        bounds = Limits.from_value(limits)
        train, tests = _sanitize(task, bounds)
        programs = _infer_programs(train)
        if len(programs) > bounds.max_programs:
            return []
        exact, calls = _exact_programs(train, tests)
        if not exact or calls > bounds.max_executor_calls:
            return []
        behavior_hash, equivalents = _unique_behavior(exact)
        equivalents.sort(key=lambda item: (int(item[0]["description_length"]), _canonical(item[0])))
        representative, predictions = equivalents[0]
        loo_checks = _loo_check(train)
        d4_checks, palette_checks = _counterfactual_check(train, tests, predictions, bounds)
        replay = _behavior(representative, tuple(source for source, _ in train))
        if replay != tuple(target for _, target in train):
            return []
    except (Undefined, TypeError, ValueError, KeyError, IndexError, ZeroDivisionError):
        return []
    candidate = {
        "family": "residual_atlas_compiler",
        "program": json.loads(_canonical(representative)),
        "train_outputs": [_plain(grid) for grid in replay],
        "test_outputs": [_plain(grid) for grid in predictions],
        "complexity": int(representative["description_length"]),
        "evidence": {
            "development_regime": DEVELOPMENT_REGIME,
            "retrospective_score_seeded": True,
            "development_solution_store_observed": True,
            "solution_store_observed": False,
            "task_identity_observed": False,
            "runtime_test_labels_observed": False,
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
        },
    }
    candidate["evidence"]["candidate_semantic_hash"] = _digest(candidate)
    return [candidate][: bounds.max_candidates]


__all__ = [
    "AUTHOR", "DEVELOPMENT_REGIME", "Limits", "SCHEMA",
    "compile_task", "execute_program", "replay_program",
]
