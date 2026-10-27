"""Bounded label-blind compositional program search for Block 15.

The entrant searches a deliberately small, typed DSL assembled from reusable
ARC primitives.  Programs have two or three semantically distinct stages:

* foreground crop, panel selection/masking, or component extraction;
* D4 symmetry, integer scaling/tiling, object translation/stamping, or a
  conservative line/fill renderer;
* an optional demonstration-induced palette transport.

Every cell carries root-pixel ancestry through execution.  Search is accepted
only when the complete minimum-description tier contains one literal program,
every demonstration replays exactly, leave-one-demonstration-out re-induction
recovers a unique program and predicts the omitted example, and palette
counterfactuals commute.
The compiler reads demonstration pairs and held-out *inputs* only.  It has no
filesystem access, task identity branch, cached raster, or solution interface.

Author: Komorebi P.
"""

from __future__ import annotations

from collections import Counter, deque
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
import hashlib
import json
from typing import Any


Grid = tuple[tuple[int, ...], ...]
Cell = tuple[int, int]
Lineage = tuple[tuple[tuple[str, ...], ...], ...]
Pair = tuple[Grid, Grid]
AUTHOR = "Komorebi P."
SCHEMA = "komorebi.pr_lasm.block15.compositional_program_search.v1"
MAX_SIDE = 30


class Undefined(ValueError):
    """A primitive or an induced role is absent, ambiguous, or out of bounds."""


@dataclass(frozen=True, slots=True)
class Limits:
    max_side: int = MAX_SIDE
    max_examples: int = 20
    max_programs: int = 2048
    max_executor_calls: int = 30_000
    max_counterfactual_checks: int = 160
    max_candidates: int = 1

    @classmethod
    def parse(cls, value: Any) -> "Limits":
        if value is None:
            return cls()
        if isinstance(value, cls):
            return value
        if not isinstance(value, Mapping):
            raise Undefined("limits must be a mapping")
        defaults = cls()

        def bounded(name: str, default: int, ceiling: int) -> int:
            raw = value.get(name, default)
            if isinstance(raw, bool) or not isinstance(raw, int) or raw < 1:
                raise Undefined(f"{name} must be a positive integer")
            return min(raw, ceiling)

        raw_candidates = value.get("candidate_cap", value.get("max_candidates", 1))
        if (
            isinstance(raw_candidates, bool)
            or not isinstance(raw_candidates, int)
            or raw_candidates < 1
        ):
            raise Undefined("candidate cap must be a positive integer")
        return cls(
            max_side=bounded("max_side", defaults.max_side, MAX_SIDE),
            max_examples=bounded("max_examples", defaults.max_examples, 40),
            max_programs=bounded("max_programs", defaults.max_programs, 4096),
            max_executor_calls=bounded(
                "max_executor_calls", defaults.max_executor_calls, 100_000
            ),
            max_counterfactual_checks=bounded(
                "max_counterfactual_checks",
                defaults.max_counterfactual_checks,
                1000,
            ),
            max_candidates=min(raw_candidates, 1),
        )


@dataclass(frozen=True, slots=True)
class State:
    grid: Grid
    lineage: Lineage


@dataclass(frozen=True, slots=True)
class Component:
    color: int
    cells: frozenset[Cell]

    @property
    def bbox(self) -> tuple[int, int, int, int]:
        return _bbox(self.cells)

    @property
    def area(self) -> int:
        return len(self.cells)

    @property
    def normalized(self) -> tuple[Cell, ...]:
        top, _, left, _ = self.bbox
        return tuple(sorted((row - top, column - left) for row, column in self.cells))


def _canonical(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _grid(value: Any, max_side: int = MAX_SIDE) -> Grid:
    if (
        not isinstance(value, Sequence)
        or isinstance(value, (str, bytes, bytearray))
        or not value
        or len(value) > max_side
    ):
        raise Undefined("invalid grid height")
    rows: list[tuple[int, ...]] = []
    width: int | None = None
    for raw_row in value:
        if (
            not isinstance(raw_row, Sequence)
            or isinstance(raw_row, (str, bytes, bytearray))
            or not raw_row
            or len(raw_row) > max_side
        ):
            raise Undefined("invalid grid row")
        row: list[int] = []
        for cell in raw_row:
            if isinstance(cell, bool) or not isinstance(cell, int) or not 0 <= cell <= 9:
                raise Undefined("ARC colors must be integers in [0, 9]")
            row.append(int(cell))
        if width is None:
            width = len(row)
        elif len(row) != width:
            raise Undefined("ragged grid")
        rows.append(tuple(row))
    return tuple(rows)


def _plain(grid: Grid) -> list[list[int]]:
    return [list(row) for row in grid]


def _shape(grid: Grid) -> tuple[int, int]:
    return len(grid), len(grid[0])


def _sanitize(task: Any, limits: Limits) -> tuple[tuple[Pair, ...], tuple[Grid, ...]]:
    if not isinstance(task, Mapping):
        raise Undefined("task must be a mapping")
    train = task.get("train")
    tests = task.get("test")
    if (
        not isinstance(train, Sequence)
        or isinstance(train, (str, bytes, bytearray))
        or len(train) < 2
        or not isinstance(tests, Sequence)
        or isinstance(tests, (str, bytes, bytearray))
        or not tests
        or len(train) + len(tests) > limits.max_examples
    ):
        raise Undefined("task needs at least two demonstrations and one test input")
    pairs: list[Pair] = []
    for index, example in enumerate(train):
        if not isinstance(example, Mapping):
            raise Undefined(f"train[{index}] is invalid")
        pairs.append(
            (
                _grid(example.get("input"), limits.max_side),
                _grid(example.get("output"), limits.max_side),
            )
        )
    held_out: list[Grid] = []
    for index, example in enumerate(tests):
        if not isinstance(example, Mapping):
            raise Undefined(f"test[{index}] is invalid")
        # Deliberately dereference only the input member.
        held_out.append(_grid(example.get("input"), limits.max_side))
    return tuple(pairs), tuple(held_out)


def _mode(grid: Grid) -> int:
    counts = Counter(cell for row in grid for cell in row)
    peak = max(counts.values())
    winners = [color for color, count in sorted(counts.items()) if count == peak]
    if len(winners) != 1:
        raise Undefined("background mode is ambiguous")
    return winners[0]


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


def _components(grid: Grid) -> tuple[Component, ...]:
    background = _mode(grid)
    height, width = _shape(grid)
    remaining = {
        (row, column)
        for row in range(height)
        for column in range(width)
        if grid[row][column] != background
    }
    result: list[Component] = []
    while remaining:
        seed = min(remaining)
        color = grid[seed[0]][seed[1]]
        remaining.remove(seed)
        queue = deque([seed])
        cells = {seed}
        while queue:
            row, column = queue.popleft()
            for dr, dc in ((-1, 0), (0, -1), (0, 1), (1, 0)):
                neighbor = row + dr, column + dc
                if neighbor in remaining and grid[neighbor[0]][neighbor[1]] == color:
                    remaining.remove(neighbor)
                    cells.add(neighbor)
                    queue.append(neighbor)
        result.append(Component(color, frozenset(cells)))
    return tuple(
        sorted(
            result,
            key=lambda item: (item.bbox, item.color, item.area, item.normalized),
        )
    )


def _lift(grid: Grid) -> State:
    lineage = tuple(
        tuple((f"p{row:02d}.{column:02d}",) for column in range(len(grid[0])))
        for row in range(len(grid))
    )
    return State(grid, lineage)


def _entities(state: State) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    try:
        components = _components(state.grid)
    except Undefined:
        components = ()
    for index, component in enumerate(components):
        roots = sorted(
            {
                root
                for row, column in component.cells
                for root in state.lineage[row][column]
            }
        )
        records.append(
            {
                "entity_id": _digest(
                    {"root_pixel_ids": roots, "occurrence": index}
                ),
                "color": component.color,
                "cells": [list(cell) for cell in sorted(component.cells)],
                "root_pixel_ids": roots,
            }
        )
    return records


def _state_json(state: State) -> dict[str, Any]:
    return {
        "grid": _plain(state.grid),
        "lineage": [[list(roots) for roots in row] for row in state.lineage],
        "entities": _entities(state),
    }


def _freeze_state(
    grid: Sequence[Sequence[int]], lineage: Sequence[Sequence[Iterable[str]]]
) -> State:
    frozen_grid = tuple(tuple(int(cell) for cell in row) for row in grid)
    frozen_lineage = tuple(
        tuple(tuple(sorted(set(roots))) for roots in row) for row in lineage
    )
    if _shape(frozen_grid) != (len(frozen_lineage), len(frozen_lineage[0])):
        raise Undefined("lineage shape mismatch")
    if any(not roots for row in frozen_lineage for roots in row):
        raise Undefined("every rendered cell needs ancestry")
    if len(frozen_grid) > MAX_SIDE or len(frozen_grid[0]) > MAX_SIDE:
        raise Undefined("primitive exceeded ARC dimensions")
    return State(frozen_grid, frozen_lineage)


def _crop_state(state: State) -> State:
    background = _mode(state.grid)
    cells = {
        (row, column)
        for row, line in enumerate(state.grid)
        for column, value in enumerate(line)
        if value != background
    }
    top, bottom, left, right = _bbox(cells)
    return State(
        tuple(row[left : right + 1] for row in state.grid[top : bottom + 1]),
        tuple(row[left : right + 1] for row in state.lineage[top : bottom + 1]),
    )


def _d4_state(state: State, code: str) -> State:
    grid: tuple[tuple[Any, ...], ...] = state.grid
    lineage: tuple[tuple[Any, ...], ...] = state.lineage

    def rotate(value: tuple[tuple[Any, ...], ...]) -> tuple[tuple[Any, ...], ...]:
        return tuple(tuple(row) for row in zip(*value[::-1]))

    if code.startswith("mirror_"):
        grid = tuple(tuple(reversed(row)) for row in grid)
        lineage = tuple(tuple(reversed(row)) for row in lineage)
        code = code.removeprefix("mirror_")
    turns = {"r0": 0, "r1": 1, "r2": 2, "r3": 3}.get(code)
    if turns is None:
        raise Undefined("unknown D4 transform")
    for _ in range(turns):
        grid = rotate(grid)
        lineage = rotate(lineage)
    return State(grid, lineage)


def _scale_state(state: State, rows: int, columns: int) -> State:
    if (
        not 1 <= rows <= 4
        or not 1 <= columns <= 4
        or rows * columns == 1
    ):
        raise Undefined("scale factors are outside the DSL")
    height, width = _shape(state.grid)
    if height * rows > MAX_SIDE or width * columns > MAX_SIDE:
        raise Undefined("scaled grid exceeds ARC dimensions")
    grid: list[list[int]] = []
    lineage: list[list[tuple[str, ...]]] = []
    for row in range(height):
        expanded_grid = [value for value in state.grid[row] for _ in range(columns)]
        expanded_roots = [roots for roots in state.lineage[row] for _ in range(columns)]
        for _ in range(rows):
            grid.append(list(expanded_grid))
            lineage.append(list(expanded_roots))
    return _freeze_state(grid, lineage)


def _tile_state(state: State, rows: int, columns: int) -> State:
    if not 1 <= rows <= 4 or not 1 <= columns <= 4 or rows * columns == 1:
        raise Undefined("tile factors are outside the DSL")
    height, width = _shape(state.grid)
    if height * rows > MAX_SIDE or width * columns > MAX_SIDE:
        raise Undefined("tiled grid exceeds ARC dimensions")
    grid = [
        [state.grid[row % height][column % width] for column in range(width * columns)]
        for row in range(height * rows)
    ]
    lineage = [
        [
            state.lineage[row % height][column % width]
            for column in range(width * columns)
        ]
        for row in range(height * rows)
    ]
    return _freeze_state(grid, lineage)


def _compress_blocks_state(state: State, rows: int, columns: int) -> State:
    if (
        not 1 <= rows <= 4
        or not 1 <= columns <= 4
        or rows * columns == 1
    ):
        raise Undefined("compression factors are outside the DSL")
    height, width = _shape(state.grid)
    if height % rows or width % columns:
        raise Undefined("grid is not divisible into compression blocks")
    grid: list[list[int]] = []
    lineage: list[list[tuple[str, ...]]] = []
    for top in range(0, height, rows):
        output_row: list[int] = []
        lineage_row: list[tuple[str, ...]] = []
        for left in range(0, width, columns):
            values = {
                state.grid[row][column]
                for row in range(top, top + rows)
                for column in range(left, left + columns)
            }
            if len(values) != 1:
                raise Undefined("compression block is not uniform")
            output_row.append(next(iter(values)))
            lineage_row.append(
                tuple(
                    sorted(
                        {
                            root
                            for row in range(top, top + rows)
                            for column in range(left, left + columns)
                            for root in state.lineage[row][column]
                        }
                    )
                )
            )
        grid.append(output_row)
        lineage.append(lineage_row)
    return _freeze_state(grid, lineage)


def _collapse_repeats_state(state: State) -> State:
    row_indices = [0]
    row_lengths: list[int] = []
    start = 0
    for index in range(1, len(state.grid)):
        if state.grid[index] != state.grid[index - 1]:
            row_lengths.append(index - start)
            start = index
            row_indices.append(index)
    row_lengths.append(len(state.grid) - start)
    intermediate_grid = tuple(state.grid[index] for index in row_indices)
    intermediate_lineage = tuple(state.lineage[index] for index in row_indices)
    columns = [tuple(row[column] for row in intermediate_grid) for column in range(len(intermediate_grid[0]))]
    column_indices = [0]
    column_lengths: list[int] = []
    start = 0
    for index in range(1, len(columns)):
        if columns[index] != columns[index - 1]:
            column_lengths.append(index - start)
            start = index
            column_indices.append(index)
    column_lengths.append(len(columns) - start)
    if len(row_indices) == len(state.grid) and len(column_indices) == len(state.grid[0]):
        raise Undefined("grid has no repeated adjacent rows or columns")
    for lengths in (row_lengths, column_lengths):
        if any(length > 1 for length in lengths) and (
            len(set(lengths)) != 1 or lengths[0] < 2
        ):
            raise Undefined("repeat runs do not have one uniform scale factor")
    return State(
        tuple(tuple(row[index] for index in column_indices) for row in intermediate_grid),
        tuple(
            tuple(row[index] for index in column_indices)
            for row in intermediate_lineage
        ),
    )


def _mirror_append_state(state: State, axis: str) -> State:
    height, width = _shape(state.grid)
    if axis == "horizontal":
        if width * 2 > MAX_SIDE:
            raise Undefined("mirror append exceeds ARC dimensions")
        grid = [list(row) + list(reversed(row)) for row in state.grid]
        lineage = [list(row) + list(reversed(row)) for row in state.lineage]
    elif axis == "vertical":
        if height * 2 > MAX_SIDE:
            raise Undefined("mirror append exceeds ARC dimensions")
        grid = [list(row) for row in state.grid] + [
            list(row) for row in reversed(state.grid)
        ]
        lineage = [list(row) for row in state.lineage] + [
            list(row) for row in reversed(state.lineage)
        ]
    else:
        raise Undefined("unknown mirror axis")
    return _freeze_state(grid, lineage)


def _panel_rects(
    grid: Grid, axis: str, divider: str = "line", count: int = 0
) -> tuple[tuple[int, int, int, int], ...]:
    height, width = _shape(grid)
    if divider == "none":
        if count not in {2, 3}:
            raise Undefined("unguttered panel count is invalid")
        extent = height if axis == "horizontal" else width
        if extent % count:
            raise Undefined("unguttered panels do not divide evenly")
        size = extent // count
        if axis == "horizontal":
            return tuple(
                (index * size, (index + 1) * size - 1, 0, width - 1)
                for index in range(count)
            )
        if axis == "vertical":
            return tuple(
                (0, height - 1, index * size, (index + 1) * size - 1)
                for index in range(count)
            )
        raise Undefined("unknown panel axis")
    if divider != "line":
        raise Undefined("unknown panel divider")
    if axis == "horizontal":
        lines = [row for row in range(1, height - 1) if len(set(grid[row])) == 1]
        color_at = lambda index: grid[index][0]
        extent = height
    elif axis == "vertical":
        lines = [
            column
            for column in range(1, width - 1)
            if len({grid[row][column] for row in range(height)}) == 1
        ]
        color_at = lambda index: grid[0][index]
        extent = width
    else:
        raise Undefined("unknown panel axis")
    candidates: list[tuple[tuple[int, int, int, int], ...]] = []
    # Blank gutters are common panel separators too.  Equal-sized-segment and
    # uniqueness guards below prevent ordinary empty margins from qualifying.
    for separator_color in sorted({color_at(index) for index in lines}):
        selected = [index for index in lines if color_at(index) == separator_color]
        runs: list[tuple[int, int]] = []
        for index in selected:
            if not runs or index > runs[-1][1] + 1:
                runs.append((index, index))
            else:
                runs[-1] = runs[-1][0], index
        boundaries = [-1] + [edge for run in runs for edge in run] + [extent]
        segments: list[tuple[int, int]] = []
        start = 0
        for first, last in runs:
            if first > start:
                segments.append((start, first - 1))
            start = last + 1
        if start < extent:
            segments.append((start, extent - 1))
        if not 2 <= len(segments) <= 4:
            continue
        lengths = {last - first + 1 for first, last in segments}
        if len(lengths) != 1:
            continue
        if axis == "horizontal":
            rects = tuple((first, last, 0, width - 1) for first, last in segments)
        else:
            rects = tuple((0, height - 1, first, last) for first, last in segments)
        candidates.append(rects)
    unique = {_canonical(candidate): candidate for candidate in candidates}
    if len(unique) != 1:
        raise Undefined("panel layout is absent or ambiguous")
    return next(iter(unique.values()))


def _rect_state(state: State, rect: tuple[int, int, int, int]) -> State:
    top, bottom, left, right = rect
    return State(
        tuple(row[left : right + 1] for row in state.grid[top : bottom + 1]),
        tuple(row[left : right + 1] for row in state.lineage[top : bottom + 1]),
    )


def _unique_rank(items: Sequence[Any], key: Any, largest: bool) -> Any:
    values = [key(item) for item in items]
    target = (max if largest else min)(values)
    winners = [item for item, value in zip(items, values) if value == target]
    if len(winners) != 1:
        raise Undefined("rank selector is tied")
    return winners[0]


def _select_panel_state(
    state: State, axis: str, selector: str, divider: str, count: int
) -> State:
    panels = [
        _rect_state(state, rect)
        for rect in _panel_rects(state.grid, axis, divider, count)
    ]
    if selector == "first":
        chosen = panels[0]
    elif selector == "last":
        chosen = panels[-1]
    elif selector in {"largest_foreground", "smallest_foreground"}:
        def area(panel: State) -> int:
            background = _mode(panel.grid)
            return sum(cell != background for row in panel.grid for cell in row)

        chosen = _unique_rank(panels, area, selector.startswith("largest"))
    elif selector in {"most_colors", "fewest_colors"}:
        chosen = _unique_rank(
            panels,
            lambda panel: len({cell for row in panel.grid for cell in row}),
            selector.startswith("most"),
        )
    else:
        raise Undefined("unknown panel selector")
    return chosen


def _select_component(components: Sequence[Component], selector: str) -> Component:
    if not components:
        raise Undefined("no foreground component")
    if selector == "only":
        if len(components) != 1:
            raise Undefined("foreground is not a single component")
        return components[0]
    if selector in {"largest", "smallest"}:
        return _unique_rank(
            components, lambda component: component.area, selector == "largest"
        )
    if selector in {"topmost", "bottommost", "leftmost", "rightmost"}:
        index = {"topmost": 0, "bottommost": 1, "leftmost": 2, "rightmost": 3}[selector]
        return _unique_rank(
            components,
            lambda component: component.bbox[index],
            selector in {"bottommost", "rightmost"},
        )
    if selector == "odd_color":
        frequencies = Counter(component.color for component in components)
        winners = [component for component in components if frequencies[component.color] == 1]
        if len(winners) != 1 or not any(count > 1 for count in frequencies.values()):
            raise Undefined("odd-color component is absent or ambiguous")
        return winners[0]
    if selector == "odd_shape":
        frequencies = Counter(component.normalized for component in components)
        winners = [
            component for component in components if frequencies[component.normalized] == 1
        ]
        if len(winners) != 1 or not any(count > 1 for count in frequencies.values()):
            raise Undefined("odd-shape component is absent or ambiguous")
        return winners[0]
    raise Undefined("unknown object selector")


def _extract_object_state(state: State, selector: str) -> State:
    component = _select_component(_components(state.grid), selector)
    top, bottom, left, right = component.bbox
    background = _mode(state.grid)
    grid: list[list[int]] = []
    lineage: list[list[tuple[str, ...]]] = []
    for row in range(top, bottom + 1):
        grid_row: list[int] = []
        lineage_row: list[tuple[str, ...]] = []
        for column in range(left, right + 1):
            grid_row.append(
                state.grid[row][column] if (row, column) in component.cells else background
            )
            lineage_row.append(state.lineage[row][column])
        grid.append(grid_row)
        lineage.append(lineage_row)
    return _freeze_state(grid, lineage)


def _select_color_state(state: State, selector: str) -> State:
    background = _mode(state.grid)
    colors = sorted({cell for row in state.grid for cell in row} - {background})
    if len(colors) < 2:
        raise Undefined("color selection needs competing foreground roles")
    supports = {
        color: {
            (row, column)
            for row, line in enumerate(state.grid)
            for column, value in enumerate(line)
            if value == color
        }
        for color in colors
    }
    if selector in {"rarest_cells", "most_cells"}:
        chosen = _unique_rank(
            colors, lambda color: len(supports[color]), selector == "most_cells"
        )
    elif selector in {"topmost_color", "bottommost_color"}:
        chosen = _unique_rank(
            colors,
            lambda color: min(row for row, _ in supports[color]),
            selector == "bottommost_color",
        )
    elif selector in {"leftmost_color", "rightmost_color"}:
        chosen = _unique_rank(
            colors,
            lambda color: min(column for _, column in supports[color]),
            selector == "rightmost_color",
        )
    elif selector in {"fewest_components", "most_components"}:
        counts = Counter(component.color for component in _components(state.grid))
        chosen = _unique_rank(
            colors, lambda color: counts[color], selector == "most_components"
        )
    else:
        raise Undefined("unknown color selector")
    top, bottom, left, right = _bbox(supports[chosen])
    grid: list[list[int]] = []
    lineage: list[list[tuple[str, ...]]] = []
    for row in range(top, bottom + 1):
        grid.append(
            [
                state.grid[row][column]
                if state.grid[row][column] == chosen
                else background
                for column in range(left, right + 1)
            ]
        )
        lineage.append(
            [state.lineage[row][column] for column in range(left, right + 1)]
        )
    return _freeze_state(grid, lineage)


def _panel_mask_state(
    state: State,
    axis: str,
    boolean: str,
    divider: str,
    count: int,
    paint: str,
    background_override: int | None,
) -> State:
    panels = [
        _rect_state(state, rect)
        for rect in _panel_rects(state.grid, axis, divider, count)
    ]
    if len(panels) not in {2, 3}:
        raise Undefined("mask composition needs two or three panels")
    if len({_shape(panel.grid) for panel in panels}) != 1:
        raise Undefined("mask panels differ in shape")
    # Zero is the conventional sparse-mask background even when a tiny panel's
    # foreground happens to occupy a majority of its cells.
    if background_override is not None:
        if not 0 <= background_override <= 9:
            raise Undefined("panel background override is invalid")
        backgrounds = [background_override] * len(panels)
    else:
        backgrounds = [
            0 if any(cell == 0 for row in panel.grid for cell in row) else _mode(panel.grid)
            for panel in panels
        ]
    height, width = _shape(panels[0].grid)
    output_background = (
        backgrounds[0] if len(set(backgrounds)) == 1 else _mode(state.grid)
    )
    grid = [[output_background] * width for _ in range(height)]
    lineage: list[list[tuple[str, ...]]] = [
        [[root for panel in panels for root in panel.lineage[row][column]] for column in range(width)]
        for row in range(height)
    ]
    for row in range(height):
        for column in range(width):
            occupied = [
                panel.grid[row][column] != background
                for panel, background in zip(panels, backgrounds)
            ]
            if boolean == "and":
                keep = all(occupied)
            elif boolean == "or":
                keep = any(occupied)
            elif boolean == "xor":
                keep = sum(occupied) == 1
            elif boolean == "difference":
                keep = occupied[0] and not any(occupied[1:])
            else:
                raise Undefined("unknown mask Boolean")
            if keep:
                colors = [
                    panel.grid[row][column]
                    for panel, present in zip(panels, occupied)
                    if present
                ]
                if not colors:
                    raise Undefined("mask support has no color")
                if paint == "source":
                    grid[row][column] = colors[0]
                elif paint == "role":
                    grid[row][column] = 10
                else:
                    raise Undefined("unknown mask paint role")
    return _freeze_state(grid, lineage)


def _fill_holes_state(state: State, paint: str) -> State:
    grid = [list(row) for row in state.grid]
    lineage = [[roots for roots in row] for row in state.lineage]
    background = _mode(state.grid)
    height, width = _shape(state.grid)
    remaining = {
        (row, column)
        for row in range(height)
        for column in range(width)
        if state.grid[row][column] == background
    }
    filled = 0
    while remaining:
        seed = min(remaining)
        remaining.remove(seed)
        queue = deque([seed])
        region = {seed}
        boundary = False
        neighbors: set[Cell] = set()
        while queue:
            row, column = queue.popleft()
            boundary |= row in {0, height - 1} or column in {0, width - 1}
            for dr, dc in ((-1, 0), (0, -1), (0, 1), (1, 0)):
                point = row + dr, column + dc
                if not (0 <= point[0] < height and 0 <= point[1] < width):
                    continue
                if point in remaining:
                    remaining.remove(point)
                    region.add(point)
                    queue.append(point)
                elif state.grid[point[0]][point[1]] != background:
                    neighbors.add(point)
        if boundary:
            continue
        colors = {state.grid[row][column] for row, column in neighbors}
        if len(colors) != 1:
            raise Undefined("hole boundary has ambiguous color")
        if paint == "source":
            color = next(iter(colors))
        elif paint == "role":
            color = 10
        else:
            raise Undefined("unknown hole paint role")
        roots = tuple(
            sorted(
                {
                    root
                    for row, column in neighbors
                    for root in state.lineage[row][column]
                }
            )
        )
        for row, column in region:
            grid[row][column] = color
            lineage[row][column] = roots
            filled += 1
    if not filled:
        raise Undefined("no enclosed hole")
    return _freeze_state(grid, lineage)


def _bbox_render_state(state: State, mode: str, paint: str) -> State:
    background = _mode(state.grid)
    foreground = {
        (row, column)
        for row, line in enumerate(state.grid)
        for column, value in enumerate(line)
        if value != background
    }
    colors = {state.grid[row][column] for row, column in foreground}
    if len(colors) != 1:
        raise Undefined("bbox rendering requires one foreground color")
    color = next(iter(colors))
    top, bottom, left, right = _bbox(foreground)
    roots = tuple(
        sorted(
            {root for row, column in foreground for root in state.lineage[row][column]}
        )
    )
    grid = [list(row) for row in state.grid]
    lineage = [[value for value in row] for row in state.lineage]
    changed = 0
    for row in range(top, bottom + 1):
        for column in range(left, right + 1):
            selected = mode == "fill" or row in {top, bottom} or column in {left, right}
            if selected and grid[row][column] != color:
                if paint == "source":
                    rendered = color
                elif paint == "role":
                    rendered = 10
                else:
                    raise Undefined("unknown bbox paint role")
                grid[row][column] = rendered
                lineage[row][column] = roots
                changed += 1
    if not changed:
        raise Undefined("bbox renderer is a no-op")
    return _freeze_state(grid, lineage)


def _connect_state(state: State, axis: str, paint: str) -> State:
    grid = [list(row) for row in state.grid]
    lineage = [[value for value in row] for row in state.lineage]
    background = _mode(state.grid)
    height, width = _shape(state.grid)
    changed = 0
    axes = ("horizontal", "vertical") if axis == "both" else (axis,)
    for color in sorted({cell for row in state.grid for cell in row} - {background}):
        if "horizontal" in axes:
            for row in range(height):
                points = [column for column in range(width) if state.grid[row][column] == color]
                if len(points) >= 2:
                    roots = tuple(
                        sorted(
                            {
                                root
                                for column in points
                                for root in state.lineage[row][column]
                            }
                        )
                    )
                    for column in range(min(points), max(points) + 1):
                        if grid[row][column] == background:
                            if paint not in {"source", "role"}:
                                raise Undefined("unknown connector paint role")
                            grid[row][column] = color if paint == "source" else 10
                            lineage[row][column] = roots
                            changed += 1
        if "vertical" in axes:
            for column in range(width):
                points = [row for row in range(height) if state.grid[row][column] == color]
                if len(points) >= 2:
                    roots = tuple(
                        sorted(
                            {
                                root
                                for row in points
                                for root in state.lineage[row][column]
                            }
                        )
                    )
                    for row in range(min(points), max(points) + 1):
                        if grid[row][column] == background:
                            if paint not in {"source", "role"}:
                                raise Undefined("unknown connector paint role")
                            grid[row][column] = color if paint == "source" else 10
                            lineage[row][column] = roots
                            changed += 1
    if not changed:
        raise Undefined("line connector is a no-op")
    return _freeze_state(grid, lineage)


def _destination_delta(
    bbox: tuple[int, int, int, int], shape: tuple[int, int], destination: str
) -> tuple[int, int]:
    top, bottom, left, right = bbox
    height, width = shape
    if destination == "top":
        return -top, 0
    if destination == "bottom":
        return height - 1 - bottom, 0
    if destination == "left":
        return 0, -left
    if destination == "right":
        return 0, width - 1 - right
    if destination == "top_left":
        return -top, -left
    if destination == "top_right":
        return -top, width - 1 - right
    if destination == "bottom_left":
        return height - 1 - bottom, -left
    if destination == "bottom_right":
        return height - 1 - bottom, width - 1 - right
    raise Undefined("unknown object destination")


def _move_stamp_state(
    state: State, selector: str, destination: str, copy_object: bool
) -> State:
    background = _mode(state.grid)
    component = _select_component(_components(state.grid), selector)
    dr, dc = _destination_delta(component.bbox, _shape(state.grid), destination)
    if (dr, dc) == (0, 0):
        raise Undefined("object is already at destination")
    grid = [list(row) for row in state.grid]
    lineage = [[roots for roots in row] for row in state.lineage]
    if not copy_object:
        for row, column in component.cells:
            grid[row][column] = background
    targets = {(row + dr, column + dc) for row, column in component.cells}
    height, width = _shape(state.grid)
    if any(not (0 <= row < height and 0 <= column < width) for row, column in targets):
        raise Undefined("object move leaves canvas")
    for (source_row, source_column), (row, column) in zip(
        sorted(component.cells), sorted(targets)
    ):
        if grid[row][column] != background and (row, column) not in component.cells:
            raise Undefined("object destination is occupied")
        grid[row][column] = component.color
        lineage[row][column] = state.lineage[source_row][source_column]
    return _freeze_state(grid, lineage)


def _translate_foreground_state(state: State, destination: str) -> State:
    background = _mode(state.grid)
    foreground = {
        (row, column)
        for row, line in enumerate(state.grid)
        for column, value in enumerate(line)
        if value != background
    }
    box = _bbox(foreground)
    dr, dc = _destination_delta(box, _shape(state.grid), destination)
    if (dr, dc) == (0, 0):
        raise Undefined("foreground is already at destination")
    grid = [[background] * len(state.grid[0]) for _ in state.grid]
    # Background ancestry stays coordinate-local; moved foreground carries roots.
    lineage = [[roots for roots in row] for row in state.lineage]
    for row, column in foreground:
        grid[row + dr][column + dc] = state.grid[row][column]
        lineage[row + dr][column + dc] = state.lineage[row][column]
    return _freeze_state(grid, lineage)


def _stamp_template_state(
    state: State, anchor: str, keep_template: bool, erase_markers: bool
) -> State:
    background = _mode(state.grid)
    components = _components(state.grid)
    template = _select_component(components, "largest")
    if template.area < 2:
        raise Undefined("stamp template is not a multi-cell object")
    markers = [component for component in components if component.area == 1]
    if not markers or len(markers) + 1 != len(components):
        raise Undefined("stamp inventory must contain one template and point markers")
    marker_colors = {marker.color for marker in markers}
    if len(marker_colors) != 1 or template.color in marker_colors:
        raise Undefined("stamp markers do not form one distinct role")
    top, bottom, left, right = template.bbox
    normalized = sorted((row - top, column - left) for row, column in template.cells)
    template_lineage = {
        (row - top, column - left): state.lineage[row][column]
        for row, column in template.cells
    }
    template_height, template_width = bottom - top + 1, right - left + 1
    grid = [list(row) for row in state.grid]
    lineage = [[roots for roots in row] for row in state.lineage]
    if not keep_template:
        for row, column in template.cells:
            grid[row][column] = background
    height, width = _shape(state.grid)
    for marker in markers:
        marker_row, marker_column = next(iter(marker.cells))
        if erase_markers:
            grid[marker_row][marker_column] = background
        if anchor == "top_left":
            origin_row, origin_column = marker_row, marker_column
        elif anchor == "center":
            origin_row = marker_row - (template_height - 1) // 2
            origin_column = marker_column - (template_width - 1) // 2
        else:
            raise Undefined("unknown stamp anchor")
        targets = [
            (origin_row + row, origin_column + column) for row, column in normalized
        ]
        if any(not (0 <= row < height and 0 <= column < width) for row, column in targets):
            raise Undefined("stamped object leaves canvas")
        marker_roots = state.lineage[marker_row][marker_column]
        for (local_row, local_column), (row, column) in zip(normalized, targets):
            if grid[row][column] != background and (row, column) != (marker_row, marker_column):
                raise Undefined("stamped object collides with existing content")
            grid[row][column] = template.color
            lineage[row][column] = tuple(
                sorted(set(template_lineage[(local_row, local_column)]) | set(marker_roots))
            )
    return _freeze_state(grid, lineage)


def _mask_background(grid: Grid, override: int | None) -> int:
    if override is not None:
        if not 0 <= override <= 9:
            raise Undefined("mask background override is invalid")
        return override
    if any(cell == 0 for row in grid for cell in row):
        return 0
    return _mode(grid)


def _binary_mask_state(state: State, background_override: int | None) -> State:
    background = _mask_background(state.grid, background_override)
    if all(cell == background for row in state.grid for cell in row):
        raise Undefined("binary mask has no foreground")
    return State(
        tuple(
            tuple(background if cell == background else 10 for cell in row)
            for row in state.grid
        ),
        state.lineage,
    )


def _isolate_monochrome_mask_state(
    state: State, background_override: int | None
) -> State:
    background = _mask_background(state.grid, background_override)
    foreground = {cell for row in state.grid for cell in row if cell != background}
    if len(foreground) != 1:
        raise Undefined("grid is not a monochrome foreground mask")
    # This is a latent type refinement: raster and ancestry stay unchanged.
    return state


def _self_kronecker_state(state: State, invert: bool) -> State:
    height, width = _shape(state.grid)
    if height * height > MAX_SIDE or width * width > MAX_SIDE:
        raise Undefined("self-Kronecker product exceeds ARC dimensions")
    values = {cell for row in state.grid for cell in row}
    if 10 not in values or len(values) != 2:
        raise Undefined("self-Kronecker input is not a role mask")
    background = next(value for value in values if value != 10)
    grid = [[background] * (width * width) for _ in range(height * height)]
    lineage: list[list[tuple[str, ...]]] = [
        [[state.lineage[0][0][0]] for _ in range(width * width)]
        for _ in range(height * height)
    ]
    for outer_row in range(height):
        for outer_column in range(width):
            active = state.grid[outer_row][outer_column] == 10
            if invert:
                active = not active
            for inner_row in range(height):
                for inner_column in range(width):
                    row = outer_row * height + inner_row
                    column = outer_column * width + inner_column
                    value = state.grid[inner_row][inner_column] if active else background
                    grid[row][column] = value
                    lineage[row][column] = tuple(
                        sorted(
                            set(state.lineage[outer_row][outer_column])
                            | set(state.lineage[inner_row][inner_column])
                        )
                    )
    return _freeze_state(grid, lineage)


def _source_kronecker_state(
    state: State, invert: bool, background_override: int | None
) -> State:
    height, width = _shape(state.grid)
    if height * height > MAX_SIDE or width * width > MAX_SIDE:
        raise Undefined("source Kronecker product exceeds ARC dimensions")
    background = _mask_background(state.grid, background_override)
    foreground = {cell for row in state.grid for cell in row if cell != background}
    if len(foreground) != 1:
        raise Undefined("source Kronecker needs one foreground color")
    grid = [[background] * (width * width) for _ in range(height * height)]
    lineage: list[list[tuple[str, ...]]] = [
        [[state.lineage[0][0][0]] for _ in range(width * width)]
        for _ in range(height * height)
    ]
    for outer_row in range(height):
        for outer_column in range(width):
            active = state.grid[outer_row][outer_column] != background
            if invert:
                active = not active
            for inner_row in range(height):
                for inner_column in range(width):
                    row = outer_row * height + inner_row
                    column = outer_column * width + inner_column
                    grid[row][column] = (
                        state.grid[inner_row][inner_column] if active else background
                    )
                    lineage[row][column] = tuple(
                        sorted(
                            set(state.lineage[outer_row][outer_column])
                            | set(state.lineage[inner_row][inner_column])
                        )
                    )
    return _freeze_state(grid, lineage)


def _palette_state(state: State, raw_mapping: Any) -> State:
    if not isinstance(raw_mapping, list):
        raise Undefined("palette map is malformed")
    mapping: dict[int, int] = {}
    for item in raw_mapping:
        if (
            not isinstance(item, list)
            or len(item) != 2
            or isinstance(item[0], bool)
            or isinstance(item[1], bool)
            or not isinstance(item[0], int)
            or not isinstance(item[1], int)
            or not 0 <= item[0] <= 19
            or not 0 <= item[1] <= 9
        ):
            raise Undefined("palette entry is malformed")
        if item[0] in mapping and mapping[item[0]] != item[1]:
            raise Undefined("palette map is not functional")
        mapping[item[0]] = item[1]
    if not mapping or all(source == target for source, target in mapping.items()):
        raise Undefined("palette stage must be nontrivial")
    return State(
        tuple(tuple(mapping.get(cell, cell) for cell in row) for row in state.grid),
        state.lineage,
    )


def _apply(state: State, operation: Mapping[str, Any]) -> State:
    name = operation.get("op")
    if name == "crop_foreground":
        return _crop_state(state)
    if name == "d4":
        return _d4_state(state, str(operation.get("code")))
    if name == "scale_cells":
        return _scale_state(state, int(operation.get("rows")), int(operation.get("columns")))
    if name == "tile_grid":
        return _tile_state(state, int(operation.get("rows")), int(operation.get("columns")))
    if name == "compress_blocks":
        return _compress_blocks_state(
            state, int(operation.get("rows")), int(operation.get("columns"))
        )
    if name == "collapse_repeats":
        return _collapse_repeats_state(state)
    if name == "mirror_append":
        return _mirror_append_state(state, str(operation.get("axis")))
    if name == "select_panel":
        return _select_panel_state(
            state,
            str(operation.get("axis")),
            str(operation.get("selector")),
            str(operation.get("divider", "line")),
            int(operation.get("count", 0)),
        )
    if name == "extract_object":
        return _extract_object_state(state, str(operation.get("selector")))
    if name == "select_color":
        return _select_color_state(state, str(operation.get("selector")))
    if name == "panel_mask":
        return _panel_mask_state(
            state,
            str(operation.get("axis")),
            str(operation.get("boolean")),
            str(operation.get("divider", "line")),
            int(operation.get("count", 0)),
            str(operation.get("paint", "source")),
            (
                int(operation["background_override"])
                if "background_override" in operation
                else None
            ),
        )
    if name == "fill_holes":
        return _fill_holes_state(state, str(operation.get("paint", "source")))
    if name == "fill_bbox":
        return _bbox_render_state(
            state, "fill", str(operation.get("paint", "source"))
        )
    if name == "outline_bbox":
        return _bbox_render_state(
            state, "outline", str(operation.get("paint", "source"))
        )
    if name == "connect_lines":
        return _connect_state(
            state,
            str(operation.get("axis")),
            str(operation.get("paint", "source")),
        )
    if name == "move_stamp":
        return _move_stamp_state(
            state,
            str(operation.get("selector")),
            str(operation.get("destination")),
            bool(operation.get("copy")),
        )
    if name == "translate_foreground":
        return _translate_foreground_state(state, str(operation.get("destination")))
    if name == "stamp_template":
        return _stamp_template_state(
            state,
            str(operation.get("anchor")),
            bool(operation.get("keep_template")),
            bool(operation.get("erase_markers")),
        )
    if name == "binary_mask":
        return _binary_mask_state(
            state,
            int(operation["background_override"])
            if "background_override" in operation
            else None,
        )
    if name == "isolate_monochrome_mask":
        return _isolate_monochrome_mask_state(
            state,
            int(operation["background_override"])
            if "background_override" in operation
            else None,
        )
    if name == "self_kronecker":
        return _self_kronecker_state(state, bool(operation.get("invert")))
    if name == "source_kronecker":
        return _source_kronecker_state(
            state,
            bool(operation.get("invert")),
            int(operation["background_override"])
            if "background_override" in operation
            else None,
        )
    if name == "palette_map":
        return _palette_state(state, operation.get("mapping"))
    raise Undefined("unknown primitive")


def _execute_state(program: Mapping[str, Any], grid: Grid) -> State:
    if program.get("schema") != SCHEMA:
        raise Undefined("wrong program schema")
    operations = program.get("operations")
    if not isinstance(operations, list) or not 2 <= len(operations) <= 3:
        raise Undefined("program depth must be two or three")
    state = _lift(grid)
    for operation in operations:
        if not isinstance(operation, Mapping):
            raise Undefined("operation must be a mapping")
        state = _apply(state, operation)
    return state


def execute_program(program: Mapping[str, Any], value: Any) -> list[list[int]]:
    """Execute a serialized compositional program on one grid."""

    if not isinstance(program, Mapping):
        raise ValueError("program must be a mapping")
    return _plain(_execute_state(program, _grid(value)).grid)


def replay_program(program: Mapping[str, Any], value: Any) -> dict[str, Any]:
    """Replay all stages while exposing exact cell and object ancestry."""

    source = _grid(value)
    if program.get("schema") != SCHEMA:
        raise ValueError("wrong program schema")
    operations = program.get("operations")
    if not isinstance(operations, list) or not 2 <= len(operations) <= 3:
        raise ValueError("program depth must be two or three")
    stages: list[dict[str, Any]] = []
    state = _lift(source)
    state_json = _state_json(state)
    stages.append(
        {"name": "lift-persistent-lineage", "input": _plain(source), "output": state_json}
    )
    for index, operation in enumerate(operations):
        prior = state_json
        state = _apply(state, operation)
        state_json = _state_json(state)
        stages.append(
            {
                "name": f"compose-{index + 1}-{operation.get('op')}",
                "input": prior,
                "output": state_json,
            }
        )
    output = _plain(state.grid)
    stages.append(
        {"name": "render-with-lineage", "input": state_json, "output": output}
    )
    return {"output": output, "stages": stages}


_OP_COST = {
    "crop_foreground": 4,
    "d4": 4,
    "scale_cells": 6,
    "tile_grid": 7,
    "compress_blocks": 7,
    "collapse_repeats": 7,
    "mirror_append": 6,
    "select_panel": 8,
    "extract_object": 8,
    "select_color": 9,
    "panel_mask": 10,
    "fill_holes": 7,
    "fill_bbox": 7,
    "outline_bbox": 8,
    "connect_lines": 8,
    "move_stamp": 11,
    "translate_foreground": 8,
    "stamp_template": 12,
    "binary_mask": 5,
    "isolate_monochrome_mask": 4,
    "self_kronecker": 10,
    "source_kronecker": 10,
    "palette_map": 3,
}


def _schema_for(operation: Mapping[str, Any]) -> str:
    name = str(operation.get("op"))
    return {
        "crop_foreground": "selection",
        "select_panel": "selection",
        "extract_object": "object",
        "select_color": "color_selection",
        "panel_mask": "mask",
        "d4": "symmetry",
        "mirror_append": "symmetry",
        "scale_cells": "resampling",
        "tile_grid": "resampling",
        "compress_blocks": "resampling",
        "collapse_repeats": "resampling",
        "fill_holes": "rendering",
        "fill_bbox": "rendering",
        "outline_bbox": "rendering",
        "connect_lines": "rendering",
        "move_stamp": "object_motion",
        "translate_foreground": "state_transition",
        "stamp_template": "object_stamp",
        "binary_mask": "mask",
        "isolate_monochrome_mask": "mask",
        "self_kronecker": "resampling",
        "source_kronecker": "resampling",
        "palette_map": "palette",
    }.get(name, "unknown")


def _complexity(operations: Sequence[Mapping[str, Any]]) -> int:
    result = len(operations)
    for operation in operations:
        name = str(operation.get("op"))
        result += _OP_COST.get(name, 100)
        # A generated structural role is the canonical normal form; carrying
        # an arbitrary source pigment through a renderer is an extra choice.
        if operation.get("paint") == "source":
            result += 1
        if operation.get("divider") == "none":
            result += 1
        if name == "palette_map":
            result += len(operation.get("mapping", []))
    return result


def _program(operations: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    normalized = json.loads(_canonical(list(operations)))
    return {
        "schema": SCHEMA,
        "operations": normalized,
        "depth": len(normalized),
        "primitive_schemas": sorted({_schema_for(item) for item in normalized}),
        "description_length": _complexity(normalized),
    }


def _operation_library() -> tuple[
    tuple[dict[str, Any], ...],
    tuple[dict[str, Any], ...],
    tuple[dict[str, Any], ...],
]:
    selectors: list[dict[str, Any]] = [{"op": "crop_foreground"}]
    for axis in ("horizontal", "vertical"):
        for selector in (
            "first",
            "last",
            "largest_foreground",
            "smallest_foreground",
            "most_colors",
            "fewest_colors",
        ):
            selectors.append({"op": "select_panel", "axis": axis, "selector": selector})
        for boolean in ("and", "or", "xor", "difference"):
            for paint in ("source", "role"):
                selectors.append(
                    {
                        "op": "panel_mask",
                        "axis": axis,
                        "boolean": boolean,
                        "paint": paint,
                    }
                )
            for count in (2, 3):
                for paint in ("source", "role"):
                    selectors.append(
                        {
                            "op": "panel_mask",
                            "axis": axis,
                            "boolean": boolean,
                            "divider": "none",
                            "count": count,
                            "paint": paint,
                        }
                    )
    for selector in (
        "only",
        "largest",
        "smallest",
        "topmost",
        "bottommost",
        "leftmost",
        "rightmost",
        "odd_color",
        "odd_shape",
    ):
        selectors.append({"op": "extract_object", "selector": selector})
    for selector in (
        "rarest_cells",
        "most_cells",
        "topmost_color",
        "bottommost_color",
        "leftmost_color",
        "rightmost_color",
        "fewest_components",
        "most_components",
    ):
        selectors.append({"op": "select_color", "selector": selector})

    geometry: list[dict[str, Any]] = []
    for code in ("r1", "r2", "r3", "mirror_r0", "mirror_r1", "mirror_r2", "mirror_r3"):
        geometry.append({"op": "d4", "code": code})
    for rows in range(1, 5):
        for columns in range(1, 5):
            if rows * columns > 1 and (rows == 1 or columns == 1 or rows == columns):
                geometry.append({"op": "scale_cells", "rows": rows, "columns": columns})
    for rows in range(1, 5):
        for columns in range(1, 5):
            # Axis repeats and square repeats cover the reusable tiling modes;
            # excluding arbitrary rectangular products keeps the grammar finite.
            if rows * columns > 1 and (rows == 1 or columns == 1 or rows == columns):
                geometry.append({"op": "tile_grid", "rows": rows, "columns": columns})
    for axis in ("horizontal", "vertical"):
        geometry.append({"op": "mirror_append", "axis": axis})
    for rows in range(1, 5):
        for columns in range(1, 5):
            if rows * columns > 1 and (rows == 1 or columns == 1 or rows == columns):
                geometry.append(
                    {"op": "compress_blocks", "rows": rows, "columns": columns}
                )
    geometry.append({"op": "collapse_repeats"})

    editors: list[dict[str, Any]] = []
    for name in ("fill_holes", "fill_bbox", "outline_bbox"):
        for paint in ("source", "role"):
            editors.append({"op": name, "paint": paint})
    for axis in ("horizontal", "vertical", "both"):
        for paint in ("source", "role"):
            editors.append({"op": "connect_lines", "axis": axis, "paint": paint})
    destinations = (
        "top",
        "bottom",
        "left",
        "right",
        "top_left",
        "top_right",
        "bottom_left",
        "bottom_right",
    )
    for destination in destinations:
        editors.append({"op": "translate_foreground", "destination": destination})
    for anchor in ("top_left", "center"):
        for keep_template in (False, True):
            for erase_markers in (False, True):
                editors.append(
                    {
                        "op": "stamp_template",
                        "anchor": anchor,
                        "keep_template": keep_template,
                        "erase_markers": erase_markers,
                    }
                )
    for selector in ("only", "largest", "smallest", "odd_color", "odd_shape"):
        for destination in destinations:
            for copy_object in (False, True):
                editors.append(
                    {
                        "op": "move_stamp",
                        "selector": selector,
                        "destination": destination,
                        "copy": copy_object,
                    }
                )
    return tuple(selectors), tuple(geometry), tuple(editors)


def _skeletons(max_programs: int) -> tuple[tuple[dict[str, Any], ...], ...]:
    selectors, geometry, editors = _operation_library()
    raw: list[tuple[dict[str, Any], ...]] = []
    # One structural primitive can become a depth-two program only by learning
    # a palette stage.  Two-primitive skeletons may stand alone or gain one.
    raw.extend((item,) for item in selectors + geometry + editors)
    geometry_selectors = tuple(
        item for item in selectors if item.get("op") != "panel_mask"
    )
    render_selectors = tuple(
        item
        for item in selectors
        if item.get("op") in {"crop_foreground", "extract_object", "select_color"}
    )
    forward_geometry = tuple(
        item
        for item in geometry
        if item.get("op") not in {"compress_blocks", "collapse_repeats"}
    )
    compression_geometry = tuple(
        item
        for item in geometry
        if item.get("op") in {"compress_blocks", "collapse_repeats"}
    )
    symmetries = tuple(item for item in geometry if item.get("op") == "d4")
    scales = tuple(item for item in geometry if item.get("op") == "scale_cells")
    raw.extend(
        (left, right) for left in geometry_selectors for right in forward_geometry
    )
    raw.extend(
        (left, right) for left in render_selectors for right in compression_geometry
    )
    raw.extend((left, right) for left in render_selectors for right in editors[:6])
    raw.extend((left, right) for left in symmetries for right in scales)
    raw.extend((left, {"op": "crop_foreground"}) for left in editors[:12])
    raw.extend(
        (left, {"op": "crop_foreground"})
        for left in editors
        if left.get("op") == "stamp_template"
    )
    for invert in (False, True):
        raw.append(
            (
                {"op": "binary_mask"},
                {"op": "self_kronecker", "invert": invert},
            )
        )
        raw.append(
            (
                {"op": "isolate_monochrome_mask"},
                {"op": "source_kronecker", "invert": invert},
            )
        )
    # A narrow depth-three geometry grammar captures true select-transform-scale
    # programs without opening the full Cartesian cube.
    compositional_selectors = tuple(
        selector
        for selector in selectors
        if selector.get("op") == "crop_foreground"
        or selector.get("selector") in {"first", "last", "only", "largest", "odd_shape"}
    )
    for selector in compositional_selectors:
        for symmetry in symmetries:
            for resample in scales:
                raw.append((selector, symmetry, resample))
    unique = {_canonical(sequence): sequence for sequence in raw}
    ordered = tuple(unique[key] for key in sorted(unique))
    if len(ordered) > max_programs:
        # This is a hard fail-closed bound, never a data-dependent truncation.
        raise Undefined("finite DSL exceeds configured max_programs")
    return ordered


def _run_operations(operations: Sequence[Mapping[str, Any]], grid: Grid) -> Grid:
    state = _lift(grid)
    for operation in operations:
        state = _apply(state, operation)
    return state.grid


def _infer_palette(intermediate: Sequence[Grid], targets: Sequence[Grid]) -> list[list[int]] | None:
    mapping: dict[int, int] = {}
    for source, target in zip(intermediate, targets):
        if _shape(source) != _shape(target):
            return None
        for source_row, target_row in zip(source, target):
            for before, after in zip(source_row, target_row):
                if before in mapping and mapping[before] != after:
                    return None
                mapping[before] = after
    changed = [[source, target] for source, target in sorted(mapping.items()) if source != target]
    return changed or None


def _exact_programs(
    pairs: Sequence[Pair], limits: Limits
) -> tuple[list[dict[str, Any]], int, int]:
    expected = tuple(target for _, target in pairs)
    exact: dict[str, dict[str, Any]] = {}
    calls = 0
    skeleton_count = 0
    prefix_cache: dict[tuple[int, str], State] = {}
    failed_prefixes: set[tuple[int, str]] = set()

    def evaluate(index: int, source: Grid, skeleton: Sequence[Mapping[str, Any]]) -> Grid:
        nonlocal calls
        state = _lift(source)
        prefix: list[Mapping[str, Any]] = []
        for operation in skeleton:
            prefix.append(operation)
            key = index, _canonical(prefix)
            if key in failed_prefixes:
                raise Undefined("cached undefined prefix")
            cached = prefix_cache.get(key)
            if cached is not None:
                state = cached
                continue
            try:
                state = _apply(state, operation)
                calls += 1
            except (Undefined, KeyError, TypeError, ValueError, IndexError, ZeroDivisionError):
                failed_prefixes.add(key)
                raise
            prefix_cache[key] = state
        return state.grid

    for skeleton in _skeletons(limits.max_programs):
        skeleton_count += 1
        try:
            intermediate = tuple(
                evaluate(index, source, skeleton)
                for index, (source, _) in enumerate(pairs)
            )
        except (Undefined, KeyError, TypeError, ValueError, IndexError, ZeroDivisionError):
            continue
        candidates: list[tuple[Mapping[str, Any], ...]] = []
        if len(skeleton) >= 2 and intermediate == expected:
            candidates.append(skeleton)
        if len(skeleton) <= 2:
            mapping = _infer_palette(intermediate, expected)
            if mapping is not None:
                candidates.append(skeleton + ({"op": "palette_map", "mapping": mapping},))
        for operations in candidates:
            if not 2 <= len(operations) <= 3:
                continue
            schemas = {_schema_for(operation) for operation in operations}
            if len(schemas) < 2 or "unknown" in schemas:
                continue
            program = _program(operations)
            exact[_canonical(program)] = program
        if calls > limits.max_executor_calls:
            raise Undefined("executor call cap exhausted")
    if not exact:
        return [], skeleton_count, calls
    programs = list(exact.values())
    minimum = min(int(program["description_length"]) for program in programs)
    return (
        sorted(
            [program for program in programs if program["description_length"] == minimum],
            key=_canonical,
        ),
        skeleton_count,
        calls,
    )


def _behavior(
    programs: Sequence[Mapping[str, Any]], grids: Sequence[Grid]
) -> dict[str, tuple[tuple[Grid, ...], list[Mapping[str, Any]]]]:
    groups: dict[str, tuple[tuple[Grid, ...], list[Mapping[str, Any]]]] = {}
    for program in programs:
        try:
            outputs = tuple(_execute_state(program, grid).grid for grid in grids)
        except (Undefined, KeyError, TypeError, ValueError, IndexError, ZeroDivisionError):
            continue
        key = _digest([_plain(grid) for grid in outputs])
        if key not in groups:
            groups[key] = outputs, []
        groups[key][1].append(program)
    return groups


def _skeleton_signature(program: Mapping[str, Any]) -> tuple[str, ...]:
    operations = program.get("operations", [])
    return tuple(str(operation.get("op")) for operation in operations)


def _leave_one_out(
    chosen: Mapping[str, Any], pairs: Sequence[Pair], limits: Limits
) -> tuple[bool, list[dict[str, Any]], int]:
    witnesses: list[dict[str, Any]] = []
    calls = 0
    chosen_signature = _skeleton_signature(chosen)
    for held_index, held_pair in enumerate(pairs):
        reduced = tuple(pair for index, pair in enumerate(pairs) if index != held_index)
        programs, enumerated, local_calls = _exact_programs(reduced, limits)
        calls += local_calls
        # Stability means re-induction recovers one literal minimum-MDL
        # explanation, not merely several explanations that happen to agree on
        # this single withheld input.
        if len(programs) != 1:
            return False, witnesses, calls
        quotient = _behavior(programs, (held_pair[0],))
        if len(quotient) != 1:
            return False, witnesses, calls
        output, equivalents = next(iter(quotient.values()))
        if output != (held_pair[1],):
            return False, witnesses, calls
        stable = any(_skeleton_signature(program) == chosen_signature for program in equivalents)
        if not stable:
            return False, witnesses, calls
        witnesses.append(
            {
                "held_out_index": held_index,
                "held_out_exact": True,
                "unique_minimum_behavior": True,
                "structural_signature_recovered": True,
                "minimum_programs": len(programs),
                "skeletons_enumerated": enumerated,
                "behavior_hash": next(iter(quotient)),
            }
        )
    return True, witnesses, calls


def _swap_grid(grid: Grid, left: int, right: int) -> Grid:
    return tuple(
        tuple(right if cell == left else left if cell == right else cell for cell in row)
        for row in grid
    )


def _swap(value: int, left: int, right: int) -> int:
    return right if value == left else left if value == right else value


def _transport_program(
    program: Mapping[str, Any], left: int, right: int
) -> dict[str, Any]:
    transported = json.loads(_canonical(program))
    for operation in transported["operations"]:
        if operation.get("op") in {
            "panel_mask",
            "binary_mask",
            "isolate_monochrome_mask",
            "source_kronecker",
        } and left == 0:
            operation["background_override"] = right
        if operation.get("op") == "palette_map":
            operation["mapping"] = sorted(
                [
                    [_swap(source, left, right), _swap(target, left, right)]
                    for source, target in operation["mapping"]
                ]
            )
    return transported


def _counterfactuals(
    program: Mapping[str, Any], pairs: Sequence[Pair], limits: Limits
) -> tuple[bool, int]:
    used = sorted(
        {
            cell
            for source, target in pairs
            for grid in (source, target)
            for row in grid
            for cell in row
        }
    )
    absent = next((color for color in range(10) if color not in used), None)
    if absent is None or len(used) < 2:
        return False, 0
    checks = 0
    # Check every used role when cheap; otherwise a deterministic spanning set.
    colors = used if len(used) * len(pairs) <= limits.max_counterfactual_checks else used[:2]
    for color in colors:
        transported = _transport_program(program, color, absent)
        for source, target in pairs:
            checks += 1
            if checks > limits.max_counterfactual_checks:
                return False, checks
            try:
                actual = _execute_state(transported, _swap_grid(source, color, absent)).grid
            except (Undefined, KeyError, TypeError, ValueError, IndexError, ZeroDivisionError):
                return False, checks
            if actual != _swap_grid(target, color, absent):
                return False, checks
    return checks >= len(pairs) * 2, checks


def _lineage_audit(program: Mapping[str, Any], grids: Sequence[Grid]) -> tuple[bool, int]:
    cells = 0
    for grid in grids:
        roots = {root for row in _lift(grid).lineage for item in row for root in item}
        try:
            state = _execute_state(program, grid)
        except (Undefined, KeyError, TypeError, ValueError, IndexError, ZeroDivisionError):
            return False, cells
        for row in state.lineage:
            for ancestry in row:
                cells += 1
                if not ancestry or not set(ancestry) <= roots:
                    return False, cells
    return cells > 0, cells


def compile_task(task: Any, limits: Mapping[str, Any] | Limits | None = None) -> list[dict[str, Any]]:
    """Return one proof-carrying minimum compositional behavior or abstain."""

    try:
        bounds = Limits.parse(limits)
        pairs, tests = _sanitize(task, bounds)
        programs, enumerated, calls = _exact_programs(pairs, bounds)
        # A behavior quotient alone is insufficient: agreeing aliases can hide
        # an underdetermined explanation.  Freeze only a unique literal member
        # of the complete minimum-description-length tier.
        if len(programs) != 1:
            return []
        quotient = _behavior(programs, tests)
        if len(quotient) != 1:
            return []
        behavior_hash, (test_outputs, equivalents) = next(iter(sorted(quotient.items())))
        # Canonical normal form represents a complete semantic equivalence class.
        chosen = min(equivalents, key=_canonical)
        loo_ok, witnesses, loo_calls = _leave_one_out(chosen, pairs, bounds)
        if not loo_ok or calls + loo_calls > bounds.max_executor_calls * (len(pairs) + 1):
            return []
        counterfactual_ok, counterfactual_checks = _counterfactuals(chosen, pairs, bounds)
        lineage_ok, lineage_cells = _lineage_audit(
            chosen, tuple(source for source, _ in pairs) + tests
        )
        if not counterfactual_ok or not lineage_ok:
            return []
        train_outputs = tuple(
            _execute_state(chosen, source).grid for source, _ in pairs
        )
        if train_outputs != tuple(target for _, target in pairs):
            return []
    except (Undefined, KeyError, TypeError, ValueError, IndexError, ZeroDivisionError):
        return []
    candidate: dict[str, Any] = {
        "family": "compositional_program_search",
        "program": json.loads(_canonical(chosen)),
        "train_outputs": [_plain(grid) for grid in train_outputs],
        "test_outputs": [_plain(grid) for grid in test_outputs],
        "complexity": int(chosen["description_length"]),
        "evidence": {
            "all_demonstrations_exact": True,
            "exact_replay": True,
            "serialized_replay_program": True,
            "program_depth": len(chosen["operations"]),
            "cross_schema_composition": True,
            "primitive_schemas": chosen["primitive_schemas"],
            "persistent_object_correspondence": True,
            "exact_root_pixel_lineage": True,
            "lineage_cells_audited": lineage_cells,
            "complete_minimum_mdl_tier": True,
            "unique_simplest_program": True,
            "minimum_programs": len(programs),
            "minimum_semantic_classes": len(quotient),
            "canonical_equivalent_programs": len(equivalents),
            "unique_simplest_test_behavior": True,
            "full_test_behavior_hash": behavior_hash,
            "leave_one_demo_out_reinduction": True,
            "leave_one_out_witnesses": witnesses,
            "palette_transport_counterfactuals": counterfactual_checks,
            "skeletons_enumerated": enumerated,
            "executor_calls": calls + loo_calls,
            "bounded_search": True,
            "hard_caps_exhausted": False,
            "task_identity_observed": False,
            "held_out_labels_observed": False,
            "test_access": "input_key_only",
            "solution_store_observed": False,
        },
    }
    candidate["evidence"]["candidate_semantic_hash"] = _digest(candidate)
    return [candidate][: bounds.max_candidates]


def predict_task(task_id: Any, task: Any) -> list[list[list[int]]]:
    """Compatibility wrapper; task identity is intentionally discarded."""

    del task_id
    candidates = compile_task(task)
    return candidates[0]["test_outputs"] if len(candidates) == 1 else []


__all__ = [
    "AUTHOR",
    "Limits",
    "SCHEMA",
    "Undefined",
    "compile_task",
    "execute_program",
    "predict_task",
    "replay_program",
]
