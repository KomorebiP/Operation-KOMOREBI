"""Bounded mixed/layout schemas for the Block 13 tournament.

The compiler is identity blind: it receives labelled demonstrations and test
inputs, enumerates a finite collection of small geometric programs, and emits
only programs that replay every demonstration exactly.  It never reads task
identifiers, test labels, corpus fingerprints, solution files, or score files.

Author: Komorebi P.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
import hashlib
import itertools
import json
from typing import Any, Iterable


Grid = tuple[tuple[int, ...], ...]
Pair = tuple[Grid, Grid]
Rule = Callable[[Grid], Grid | None]


class _Undefined(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class Limits:
    max_side: int = 30
    max_cells: int = 900
    max_candidates: int = 64
    max_mdl: int = 32

    @classmethod
    def from_value(cls, value: Any) -> "Limits":
        if not isinstance(value, Mapping):
            return cls()
        defaults = cls()

        def read(name: str, default: int, upper: int) -> int:
            raw = value.get(name, default)
            if isinstance(raw, bool) or not isinstance(raw, int) or raw <= 0:
                return default
            return min(raw, upper)

        raw_cap = value.get("candidate_cap", defaults.max_candidates)
        if isinstance(raw_cap, bool) or not isinstance(raw_cap, int):
            raw_cap = defaults.max_candidates
        return cls(
            max_side=read("max_side", defaults.max_side, 60),
            max_cells=read("max_cells", defaults.max_cells, 3600),
            max_candidates=read("max_candidates", raw_cap, 256),
            max_mdl=read("max_mdl", defaults.max_mdl, 128),
        )


def _grid(value: Any, limits: Limits) -> Grid:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or not value:
        raise _Undefined("empty grid")
    rows: list[tuple[int, ...]] = []
    width: int | None = None
    for raw in value:
        if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes)) or not raw:
            raise _Undefined("bad row")
        row: list[int] = []
        for cell in raw:
            if isinstance(cell, bool) or not isinstance(cell, int) or not 0 <= cell <= 9:
                raise _Undefined("bad color")
            row.append(int(cell))
        if width is None:
            width = len(row)
        elif len(row) != width:
            raise _Undefined("ragged grid")
        rows.append(tuple(row))
    if len(rows) > limits.max_side or int(width or 0) > limits.max_side:
        raise _Undefined("side bound")
    if len(rows) * int(width or 0) > limits.max_cells:
        raise _Undefined("cell bound")
    return tuple(rows)


def _read_task(task: Any, limits: Limits) -> tuple[tuple[Pair, ...], tuple[Grid, ...]]:
    if not isinstance(task, Mapping):
        raise _Undefined("bad task")
    raw_train, raw_test = task.get("train"), task.get("test")
    if (
        not isinstance(raw_train, Sequence)
        or isinstance(raw_train, (str, bytes))
        or not raw_train
        or not isinstance(raw_test, Sequence)
        or isinstance(raw_test, (str, bytes))
        or not raw_test
    ):
        raise _Undefined("missing examples")
    train: list[Pair] = []
    for example in raw_train:
        if not isinstance(example, Mapping):
            raise _Undefined("bad demonstration")
        train.append((_grid(example.get("input"), limits), _grid(example.get("output"), limits)))
    tests: list[Grid] = []
    for example in raw_test:
        if not isinstance(example, Mapping):
            raise _Undefined("bad test")
        # The output field, even if a caller supplied one, is intentionally ignored.
        tests.append(_grid(example.get("input"), limits))
    return tuple(train), tuple(tests)


def _shape(grid: Grid) -> tuple[int, int]:
    return len(grid), len(grid[0])


def _mode(grid: Grid) -> int:
    counts = Counter(cell for row in grid for cell in row)
    return min(counts, key=lambda color: (-counts[color], color))


def _palette(grid: Grid) -> set[int]:
    return {cell for row in grid for cell in row}


def _freeze(rows: Sequence[Sequence[int]]) -> Grid:
    return tuple(tuple(int(cell) for cell in row) for row in rows)


def _plain(grid: Grid) -> list[list[int]]:
    return [list(row) for row in grid]


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _checked(grid: Grid | None, limits: Limits) -> Grid:
    if grid is None or not grid or not grid[0]:
        raise _Undefined("undefined program")
    height, width = _shape(grid)
    if height > limits.max_side or width > limits.max_side or height * width > limits.max_cells:
        raise _Undefined("output bound")
    if any(len(row) != width or any(not 0 <= cell <= 9 for cell in row) for row in grid):
        raise _Undefined("bad output")
    return grid


def _candidate(
    family: str,
    program: Mapping[str, Any],
    complexity: int,
    rule: Rule,
    train: Sequence[Pair],
    tests: Sequence[Grid],
    limits: Limits,
) -> dict[str, Any] | None:
    if complexity > limits.max_mdl:
        return None
    try:
        replay = [_checked(rule(source), limits) for source, _ in train]
        if any(got != target for got, (_, target) in zip(replay, train)):
            return None
        predictions = [_checked(rule(source), limits) for source in tests]
        encoded_program = json.loads(_canonical(program))
    except (_Undefined, IndexError, KeyError, TypeError, ValueError, ZeroDivisionError):
        return None
    behavior = hashlib.sha256(
        _canonical([_plain(grid) for grid in predictions]).encode("ascii")
    ).hexdigest()
    return {
        "family": family,
        "program": encoded_program,
        "train_outputs": [_plain(grid) for grid in replay],
        "test_outputs": [_plain(grid) for grid in predictions],
        "complexity": int(complexity),
        "evidence": {
            "all_demonstrations_exact": True,
            "demonstration_count": len(train),
            "test_count": len(tests),
            "behavior_hash": behavior,
            "bounded_search": True,
            "task_identity_free": True,
            "mdl": int(complexity),
        },
    }


def _components(points: Iterable[tuple[int, int]]) -> list[set[tuple[int, int]]]:
    remaining = set(points)
    answer: list[set[tuple[int, int]]] = []
    while remaining:
        seed = min(remaining)
        remaining.remove(seed)
        component = {seed}
        queue = [seed]
        while queue:
            row, column = queue.pop()
            for point in ((row - 1, column), (row + 1, column), (row, column - 1), (row, column + 1)):
                if point in remaining:
                    remaining.remove(point)
                    component.add(point)
                    queue.append(point)
        answer.append(component)
    return sorted(answer, key=lambda component: (min(component), len(component)))


def _bbox(points: Iterable[tuple[int, int]]) -> tuple[int, int, int, int]:
    points = tuple(points)
    return (
        min(row for row, _ in points),
        max(row for row, _ in points),
        min(column for _, column in points),
        max(column for _, column in points),
    )


def _filled_bbox(component: set[tuple[int, int]]) -> bool:
    top, bottom, left, right = _bbox(component)
    return len(component) == (bottom - top + 1) * (right - left + 1)


def _same_shape_guard(train: Sequence[Pair]) -> bool:
    return all(_shape(source) == _shape(target) for source, target in train)


def _added_colors(train: Sequence[Pair]) -> set[int]:
    return set.union(*(_palette(target) - _palette(source) for source, target in train))


# ---------------------------------------------------------------------------
# Same-canvas geometric programs


def _filled_rectangle_bridges(train: Sequence[Pair]) -> tuple[Rule, dict[str, Any], int] | None:
    added = _added_colors(train)
    if len(added) != 1:
        return None
    paint = next(iter(added))

    def rule(source: Grid) -> Grid | None:
        height, width = _shape(source)
        background = _mode(source)
        output = [list(row) for row in source]
        rectangles: dict[int, list[tuple[int, int, int, int]]] = {}
        for color in sorted(_palette(source) - {background}):
            comps = _components(
                (row, column)
                for row in range(height)
                for column in range(width)
                if source[row][column] == color
            )
            rectangles[color] = [_bbox(comp) for comp in comps if _filled_bbox(comp)]
        bridges = 0
        for boxes in rectangles.values():
            for first, second in itertools.combinations(boxes, 2):
                t1, b1, l1, r1 = first
                t2, b2, l2, r2 = second
                overlap_top, overlap_bottom = max(t1, t2), min(b1, b2)
                if overlap_bottom - overlap_top + 1 >= 3:
                    if r1 < l2:
                        columns = range(r1 + 1, l2)
                    elif r2 < l1:
                        columns = range(r2 + 1, l1)
                    else:
                        columns = range(0)
                    for row in range(overlap_top + 1, overlap_bottom):
                        for column in columns:
                            if output[row][column] == background:
                                output[row][column] = paint
                                bridges += 1
                overlap_left, overlap_right = max(l1, l2), min(r1, r2)
                if overlap_right - overlap_left + 1 >= 3:
                    if b1 < t2:
                        rows = range(b1 + 1, t2)
                    elif b2 < t1:
                        rows = range(b2 + 1, t1)
                    else:
                        rows = range(0)
                    for row in rows:
                        for column in range(overlap_left + 1, overlap_right):
                            if output[row][column] == background:
                                output[row][column] = paint
                                bridges += 1
        return _freeze(output) if bridges else None

    return rule, {"operator": "bridge_same_color_filled_rectangles", "trim_overlap": 1, "paint": paint}, 9


def _cross_center_projection_proposals(train: Sequence[Pair]) -> list[tuple[Rule, dict[str, Any], int]]:
    common = set.intersection(*(_palette(source) for source, _ in train))
    proposals: list[tuple[Rule, dict[str, Any], int]] = []
    for arm in sorted(common):
        def rule(source: Grid, arm: int = arm) -> Grid | None:
            height, width = _shape(source)
            centers: list[tuple[int, int, int]] = []
            for row in range(1, height - 1):
                for column in range(1, width - 1):
                    if source[row][column] == arm:
                        continue
                    if all(
                        source[rr][cc] == arm
                        for rr, cc in ((row - 1, column), (row + 1, column), (row, column - 1), (row, column + 1))
                    ):
                        centers.append((row, column, source[row][column]))
            if not centers:
                return None
            output = [list(row) for row in source]
            for row, _, color in centers:
                output[row] = [color] * width
            for _, column, color in centers:
                for row in range(height):
                    output[row][column] = color
            background = _mode(source)
            for row in range(height):
                for column in range(width):
                    if source[row][column] != background:
                        output[row][column] = source[row][column]
            return _freeze(output)

        proposals.append((rule, {"operator": "project_cross_centers", "arm_color": arm, "vertical_precedence": True}, 8))
    return proposals


def _move_points_to_blocks_proposals(train: Sequence[Pair]) -> list[tuple[Rule, dict[str, Any], int]]:
    common = set.intersection(*(_palette(source) for source, _ in train))
    proposals: list[tuple[Rule, dict[str, Any], int]] = []
    for mover, block in itertools.permutations(sorted(common), 2):
        def rule(source: Grid, mover: int = mover, block: int = block) -> Grid | None:
            height, width = _shape(source)
            block_components = _components(
                (row, column)
                for row in range(height)
                for column in range(width)
                if source[row][column] == block
            )
            boxes = [_bbox(comp) for comp in block_components if _filled_bbox(comp) and len(comp) >= 4]
            if not boxes:
                return None
            output = [list(row) for row in source]
            moved = 0
            for row in range(height):
                for column in range(width):
                    if source[row][column] != mover:
                        continue
                    choices: list[tuple[int, int, int]] = []
                    for top, bottom, left, right in boxes:
                        if top <= row <= bottom and column < left:
                            choices.append((left - column, row, left - 1))
                        if top <= row <= bottom and column > right:
                            choices.append((column - right, row, right + 1))
                        if left <= column <= right and row < top:
                            choices.append((top - row, top - 1, column))
                        if left <= column <= right and row > bottom:
                            choices.append((row - bottom, bottom + 1, column))
                    if not choices:
                        continue
                    distance, rr, cc = min(choices)
                    if sum(choice[0] == distance for choice in choices) != 1 or (rr, cc) == (row, column):
                        continue
                    if source[rr][cc] != _mode(source):
                        continue
                    output[row][column] = _mode(source)
                    output[rr][cc] = mover
                    moved += 1
            return _freeze(output) if moved else None

        proposals.append((rule, {"operator": "slide_aligned_points_to_block_edge", "mover": mover, "block": block}, 8))
    return proposals


def _greedy_aligned_block_chain(train: Sequence[Pair]) -> list[tuple[Rule, dict[str, Any], int]]:
    source_common = set.intersection(*(_palette(source) for source, _ in train))
    added = _added_colors(train)
    proposals: list[tuple[Rule, dict[str, Any], int]] = []
    for start, node in itertools.permutations(sorted(source_common), 2):
        for paint in sorted(added):
            def rule(source: Grid, start: int = start, node: int = node, paint: int = paint) -> Grid | None:
                height, width = _shape(source)

                def boxes(color: int) -> list[tuple[int, int, int, int]]:
                    return [
                        _bbox(comp)
                        for comp in _components(
                            (row, column)
                            for row in range(height)
                            for column in range(width)
                            if source[row][column] == color
                        )
                        if _filled_bbox(comp)
                    ]

                starts, nodes = boxes(start), boxes(node)
                if len(starts) != 1 or not nodes:
                    return None
                current = starts[0]
                dimensions = (current[1] - current[0] + 1, current[3] - current[2] + 1)
                if any((box[1] - box[0] + 1, box[3] - box[2] + 1) != dimensions for box in nodes):
                    return None
                remaining = list(nodes)
                output = [list(row) for row in source]
                links = 0
                while remaining:
                    ranked: list[tuple[int, tuple[int, int, int, int]]] = []
                    top, bottom, left, right = current
                    for box in remaining:
                        tt, bb, ll, rr = box
                        if (tt, bb) == (top, bottom):
                            ranked.append((max(ll - right - 1, left - rr - 1), box))
                        elif (ll, rr) == (left, right):
                            ranked.append((max(tt - bottom - 1, top - bb - 1), box))
                    if not ranked:
                        break
                    ranked.sort(key=lambda item: (item[0], item[1]))
                    distance, nxt = ranked[0]
                    if len(ranked) > 1 and ranked[1][0] == distance:
                        return None
                    nt, nb, nl, nr = nxt
                    if (nt, nb) == (top, bottom):
                        lo, hi = sorted((right, nl)) if right < nl else sorted((nr, left))
                        for row in range(top, bottom + 1):
                            for column in range(lo + 1, hi):
                                output[row][column] = paint
                    else:
                        lo, hi = sorted((bottom, nt)) if bottom < nt else sorted((nb, top))
                        for row in range(lo + 1, hi):
                            for column in range(left, right + 1):
                                output[row][column] = paint
                    links += 1
                    remaining.remove(nxt)
                    current = nxt
                return _freeze(output) if links else None

            proposals.append((rule, {"operator": "greedy_nearest_aligned_block_chain", "start": start, "node": node, "paint": paint}, 12))
    return proposals


def _marker_reflection_proposals(train: Sequence[Pair]) -> list[tuple[Rule, dict[str, Any], int]]:
    common = set.intersection(*(_palette(source) for source, _ in train))
    proposals: list[tuple[Rule, dict[str, Any], int]] = []
    for marker in sorted(common):
        def rule(source: Grid, marker: int = marker) -> Grid | None:
            height, width = _shape(source)
            background = _mode(source)
            comps = _components(
                (row, column)
                for row in range(height)
                for column in range(width)
                if source[row][column] == marker
            )
            filled = [comp for comp in comps if _filled_bbox(comp)]
            if len(filled) != 1:
                return None
            top, bottom, left, right = _bbox(filled[0])
            output = [list(row) for row in source]
            ink = [
                (row, column, source[row][column])
                for row in range(height)
                for column in range(width)
                if source[row][column] not in {background, marker}
            ]
            if not ink:
                return None
            for row, column, color in ink:
                for rr, cc in ((row, column), (top + bottom - row, column), (row, left + right - column), (top + bottom - row, left + right - column)):
                    if 0 <= rr < height and 0 <= cc < width:
                        if output[rr][cc] not in {background, color}:
                            return None
                        output[rr][cc] = color
            return _freeze(output)

        proposals.append((rule, {"operator": "reflect_ink_across_marker_axes", "marker": marker, "orbit": "Klein-four"}, 7))
    return proposals


def _path_extension_recolor() -> tuple[Rule, dict[str, Any], int]:
    def rule(source: Grid) -> Grid | None:
        height, width = _shape(source)
        background = _mode(source)
        output = [list(row) for row in source]
        by_color: dict[int, list[set[tuple[int, int]]]] = {}
        for color in sorted(_palette(source) - {background}):
            by_color[color] = _components(
                (row, column)
                for row in range(height)
                for column in range(width)
                if source[row][column] == color
            )
        singleton_markers = [
            (next(iter(comp)), color)
            for color, comps in by_color.items()
            for comp in comps
            if len(comp) == 1
        ]
        changed = 0
        for color, comps in by_color.items():
            for comp in comps:
                if len(comp) < 2:
                    continue
                adjacency = {
                    point: sorted(
                        other
                        for other in comp
                        if abs(point[0] - other[0]) + abs(point[1] - other[1]) == 1
                    )
                    for point in comp
                }
                endpoints = sorted(point for point, neighbors in adjacency.items() if len(neighbors) == 1)
                if len(endpoints) != 2 or any(len(neighbors) > 2 for neighbors in adjacency.values()):
                    continue
                choices: list[tuple[int, tuple[int, int], int, tuple[int, int]]] = []
                for endpoint in endpoints:
                    neighbor = adjacency[endpoint][0]
                    direction = (endpoint[0] - neighbor[0], endpoint[1] - neighbor[1])
                    for marker, marker_color in singleton_markers:
                        if marker_color == color:
                            continue
                        dr, dc = marker[0] - endpoint[0], marker[1] - endpoint[1]
                        if direction[0] and dc == 0 and dr * direction[0] >= 2:
                            choices.append((abs(dr), endpoint, marker_color, marker))
                        if direction[1] and dr == 0 and dc * direction[1] >= 2:
                            choices.append((abs(dc), endpoint, marker_color, marker))
                if not choices:
                    continue
                choices.sort()
                distance, near_endpoint, marker_color, marker = choices[0]
                if len(choices) > 1 and choices[1][0] == distance:
                    continue
                gap = distance - 1
                other_endpoint = endpoints[1] if near_endpoint == endpoints[0] else endpoints[0]
                # Order the simple path from its far endpoint.
                ordered = [other_endpoint]
                previous: tuple[int, int] | None = None
                current = other_endpoint
                while current != near_endpoint:
                    next_points = [point for point in adjacency[current] if point != previous]
                    if len(next_points) != 1:
                        raise _Undefined("not a simple path")
                    previous, current = current, next_points[0]
                    ordered.append(current)
                if gap > len(ordered):
                    continue
                for row, column in ordered[:gap]:
                    output[row][column] = marker_color
                step = (
                    (marker[0] - near_endpoint[0]) // distance,
                    (marker[1] - near_endpoint[1]) // distance,
                )
                for offset in range(1, distance):
                    row = near_endpoint[0] + step[0] * offset
                    column = near_endpoint[1] + step[1] * offset
                    if source[row][column] != background:
                        raise _Undefined("extension collision")
                    output[row][column] = color
                changed += 1
        return _freeze(output) if changed else None

    return rule, {"operator": "extend_path_to_marker_and_recolor_far_prefix", "prefix_length": "gap"}, 12


# ---------------------------------------------------------------------------
# Panel and lattice programs


def _panel_bounds(grid: Grid) -> tuple[int, list[tuple[int, int]], list[tuple[int, int]]] | None:
    height, width = _shape(grid)
    ranked: list[tuple[int, int, list[int], list[int]]] = []
    for color in sorted(_palette(grid)):
        rows = [row for row in range(height) if all(cell == color for cell in grid[row])]
        columns = [column for column in range(width) if all(grid[row][column] == color for row in range(height))]
        if rows and columns:
            ranked.append((len(rows) + len(columns), color, rows, columns))
    if not ranked:
        return None
    _, separator, separator_rows, separator_columns = max(ranked)

    def gaps(size: int, separators: Sequence[int]) -> list[tuple[int, int]]:
        answer: list[tuple[int, int]] = []
        start = 0
        for value in separators:
            if start < value:
                answer.append((start, value))
            start = value + 1
        if start < size:
            answer.append((start, size))
        return answer

    row_bounds, column_bounds = gaps(height, separator_rows), gaps(width, separator_columns)
    if len(row_bounds) < 2 or len(column_bounds) < 2:
        return None
    if len({bottom - top for top, bottom in row_bounds}) != 1 or len({right - left for left, right in column_bounds}) != 1:
        return None
    return separator, row_bounds, column_bounds


def _panel_stamp() -> tuple[Rule, dict[str, Any], int]:
    def rule(source: Grid) -> Grid | None:
        panel_data = _panel_bounds(source)
        if panel_data is None:
            return None
        separator, row_bounds, column_bounds = panel_data
        background = _mode(source)
        matrix: list[list[int]] = []
        for top, bottom in row_bounds:
            row_values: list[int] = []
            for left, right in column_bounds:
                values = {source[row][column] for row in range(top, bottom) for column in range(left, right)}
                if len(values) != 1:
                    return None
                row_values.append(next(iter(values)))
            matrix.append(row_values)
        colors = sorted(set(sum(matrix, [])) - {background, separator})
        ranked: list[tuple[int, int, int, int, tuple[tuple[int, int], ...]]] = []
        for center_color, stamp_color in itertools.permutations(colors, 2):
            for row in range(len(matrix)):
                for column in range(len(matrix[0])):
                    if matrix[row][column] != center_color:
                        continue
                    offsets = tuple(
                        (dr, dc)
                        for dr in (-1, 0, 1)
                        for dc in (-1, 0, 1)
                        if (dr or dc)
                        and 0 <= row + dr < len(matrix)
                        and 0 <= column + dc < len(matrix[0])
                        and matrix[row + dr][column + dc] == stamp_color
                    )
                    if len(offsets) >= 2:
                        ranked.append((-len(offsets), center_color, stamp_color, row * len(matrix[0]) + column, offsets))
        if not ranked:
            return None
        ranked.sort()
        _, center_color, stamp_color, _, offsets = ranked[0]
        output = [list(row) for row in source]
        stamped = 0
        for row in range(len(matrix)):
            for column in range(len(matrix[0])):
                if matrix[row][column] != center_color:
                    continue
                for dr, dc in offsets:
                    rr, cc = row + dr, column + dc
                    if not (0 <= rr < len(matrix) and 0 <= cc < len(matrix[0])):
                        continue
                    if matrix[rr][cc] != background:
                        continue
                    top, bottom = row_bounds[rr]
                    left, right = column_bounds[cc]
                    for real_row in range(top, bottom):
                        for real_column in range(left, right):
                            output[real_row][real_column] = stamp_color
                    stamped += 1
        return _freeze(output) if stamped else None

    return rule, {"operator": "replicate_local_panel_stamp", "radius": 1, "clip": True}, 11


def _panel_connections(train: Sequence[Pair]) -> tuple[Rule, dict[str, Any], int] | None:
    additions = _added_colors(train)
    if len(additions) != 1:
        return None
    crossing = next(iter(additions))

    def rule(source: Grid) -> Grid | None:
        panel_data = _panel_bounds(source)
        if panel_data is None:
            return None
        separator, row_bounds, column_bounds = panel_data
        background = _mode(source)
        markers: dict[int, list[tuple[int, int]]] = {}
        for pr, (top, bottom) in enumerate(row_bounds):
            for pc, (left, right) in enumerate(column_bounds):
                colors = {
                    source[row][column]
                    for row in range(top, bottom)
                    for column in range(left, right)
                    if source[row][column] not in {background, separator}
                }
                if len(colors) > 1:
                    return None
                if colors:
                    markers.setdefault(next(iter(colors)), []).append((pr, pc))
        assignments: dict[tuple[int, int], set[int]] = {}
        lines = 0
        for color, points in markers.items():
            for first, second in itertools.combinations(points, 2):
                if first[0] == second[0]:
                    for column in range(min(first[1], second[1]), max(first[1], second[1]) + 1):
                        assignments.setdefault((first[0], column), set()).add(color)
                    lines += 1
                if first[1] == second[1]:
                    for row in range(min(first[0], second[0]), max(first[0], second[0]) + 1):
                        assignments.setdefault((row, first[1]), set()).add(color)
                    lines += 1
        if not lines:
            return None
        output = [list(row) for row in source]
        for (pr, pc), colors in assignments.items():
            color = next(iter(colors)) if len(colors) == 1 else crossing
            top, bottom = row_bounds[pr]
            left, right = column_bounds[pc]
            for row in range(top, bottom):
                for column in range(left, right):
                    output[row][column] = color
        return _freeze(output)

    return rule, {"operator": "connect_matching_panel_markers", "intersection": crossing}, 11


def _rare_aligned_component_connections() -> tuple[Rule, dict[str, Any], int]:
    def rule(source: Grid) -> Grid | None:
        height, width = _shape(source)
        background = _mode(source)
        counts = Counter(cell for row in source for cell in row if cell != background)
        if len(counts) < 2:
            return None
        rare_count = min(counts.values())
        colors = [color for color, count in counts.items() if count == rare_count]
        output = [list(row) for row in source]
        connections = 0
        for color in sorted(colors):
            comps = _components(
                (row, column)
                for row in range(height)
                for column in range(width)
                if source[row][column] == color
            )
            if len(comps) < 2 or any(not _filled_bbox(comp) for comp in comps):
                continue
            boxes = [_bbox(comp) for comp in comps]
            dimensions = {(bottom - top + 1, right - left + 1) for top, bottom, left, right in boxes}
            if len(dimensions) != 1:
                continue
            for first, second in itertools.combinations(boxes, 2):
                t1, b1, l1, r1 = first
                t2, b2, l2, r2 = second
                if (t1, b1) == (t2, b2):
                    for row in range(t1, b1 + 1):
                        for column in range(min(l1, l2), max(r1, r2) + 1):
                            output[row][column] = color
                    connections += 1
                if (l1, r1) == (l2, r2):
                    for row in range(min(t1, t2), max(b1, b2) + 1):
                        for column in range(l1, r1 + 1):
                            output[row][column] = color
                    connections += 1
        return _freeze(output) if connections else None

    return rule, {"operator": "connect_rarest_equal_rectangles", "alignment": "exact"}, 10


def _diagonal_rotating_bar_lattice(train: Sequence[Pair]) -> tuple[Rule, dict[str, Any], int] | None:
    target_colors = set.intersection(*(_palette(target) - {_mode(target)} for _, target in train))
    if len(target_colors) != 2:
        return None
    cycle = tuple(sorted(target_colors))

    def rule(source: Grid) -> Grid | None:
        height, width = _shape(source)
        background = _mode(source)
        points = {(row, column) for row in range(height) for column in range(width) if source[row][column] != background}
        comps = _components(points)
        if len(comps) != 1 or not _filled_bbox(comps[0]):
            return None
        top, bottom, left, right = _bbox(comps[0])
        seed_color = source[top][left]
        if seed_color not in cycle:
            return None
        other_color = cycle[1] if seed_color == cycle[0] else cycle[0]
        seed_height, seed_width = bottom - top + 1, right - left + 1
        if seed_height == seed_width:
            return None
        center_row2, center_column2 = top + bottom, left + right
        step2 = seed_height + seed_width
        output = [[background] * width for _ in range(height)]
        placed = 0
        for sr in (-1, 1):
            for sc in (-1, 1):
                for distance in range(0, 2 * (height + width) + 1):
                    row2 = center_row2 + sr * distance * step2
                    column2 = center_column2 + sc * distance * step2
                    copy_height, copy_width = ((seed_height, seed_width) if distance % 2 == 0 else (seed_width, seed_height))
                    numerator_row = row2 - (copy_height - 1)
                    numerator_column = column2 - (copy_width - 1)
                    if numerator_row % 2 or numerator_column % 2:
                        continue
                    copy_top, copy_left = numerator_row // 2, numerator_column // 2
                    copy_bottom, copy_right = copy_top + copy_height, copy_left + copy_width
                    if copy_bottom <= 0 or copy_top >= height or copy_right <= 0 or copy_left >= width:
                        if distance and (abs(row2 - center_row2) > 2 * height and abs(column2 - center_column2) > 2 * width):
                            break
                        continue
                    color = seed_color if distance % 2 == 0 else other_color
                    for row in range(max(0, copy_top), min(height, copy_bottom)):
                        for column in range(max(0, copy_left), min(width, copy_right)):
                            if output[row][column] not in {background, color}:
                                return None
                            output[row][column] = color
                    placed += 1
        return _freeze(output) if placed > 1 else None

    return rule, {"operator": "diagonal_rotating_bar_lattice", "color_cycle": list(cycle), "step": "half_perimeter"}, 13


def _periodic_comb_lattice(train: Sequence[Pair]) -> tuple[Rule, dict[str, Any], int] | None:
    added = _added_colors(train)
    if len(added) != 1:
        return None
    alternate = next(iter(added))

    def rule(source: Grid) -> Grid | None:
        height, width = _shape(source)
        background = _mode(source)
        points = {(row, column) for row in range(height) for column in range(width) if source[row][column] != background}
        comps = _components(points)
        if len(comps) != 1:
            return None
        component = comps[0]
        top, bottom, left, right = _bbox(component)
        seed_color = source[top][left]
        if any(source[row][column] != seed_color for row, column in component):
            return None
        mask = {(row - top, column - left) for row, column in component}
        box_height, box_width = bottom - top + 1, right - left + 1
        output = [[background] * width for _ in range(height)]

        def place(origin_row: int, origin_column: int, color: int) -> None:
            for dr, dc in mask:
                row, column = origin_row + dr, origin_column + dc
                if 0 <= row < height and 0 <= column < width:
                    output[row][column] = color

        column_index = 0
        while left + column_index * (box_width + 1) < width:
            origin_column = left + column_index * (box_width + 1)
            if column_index % 3 < 2:
                place(top, origin_column, seed_color)
            else:
                row = top
                while row < height:
                    place(row, origin_column, alternate)
                    row += box_height + 1
            column_index += 1
        return _freeze(output)

    return rule, {"operator": "periodic_top_comb_with_spokes", "run": 2, "period": 3, "alternate": alternate}, 12


def _nested_rectangle_transfer() -> tuple[Rule, dict[str, Any], int]:
    side_names = ("top", "bottom", "left", "right")

    def rule(source: Grid) -> Grid | None:
        height, width = _shape(source)
        background = _mode(source)
        points = {(row, column) for row in range(height) for column in range(width) if source[row][column] != background}
        comps = _components(points)
        records: list[tuple[set[tuple[int, int]], tuple[int, int, int, int], set[int]]] = []
        for comp in comps:
            box = _bbox(comp)
            top, bottom, left, right = box
            if len(comp) != (bottom - top + 1) * (right - left + 1):
                return None
            records.append((comp, box, {source[row][column] for row, column in comp}))
        exemplars = [record for record in records if len(record[2]) > 1]
        if len(exemplars) != 1 or len(records) < 2:
            return None
        _, exemplar_box, _ = exemplars[0]
        et, eb, el, er = exemplar_box
        base = source[et][el]
        if any(colors != {base} for _, box, colors in records if box != exemplar_box):
            return None
        ranked: list[tuple[int, tuple[str, ...], dict[int, int]]] = []
        for size in range(1, 5):
            for sides in itertools.combinations(side_names, size):
                mapping: dict[int, int] = {}
                valid = True
                for row in range(et, eb + 1):
                    for column in range(el, er + 1):
                        distances: list[int] = []
                        if "top" in sides:
                            distances.append(row - et)
                        if "bottom" in sides:
                            distances.append(eb - row)
                        if "left" in sides:
                            distances.append(column - el)
                        if "right" in sides:
                            distances.append(er - column)
                        depth = min(distances)
                        color = source[row][column]
                        if depth in mapping and mapping[depth] != color:
                            valid = False
                            break
                        mapping[depth] = color
                    if not valid:
                        break
                if valid and len(set(mapping.values())) > 1:
                    ranked.append((-size, sides, mapping))
        if not ranked:
            return None
        ranked.sort(key=lambda item: (item[0], item[1]))
        _, sides, mapping = ranked[0]
        deepest = max(mapping)
        output = [list(row) for row in source]
        for _, (top, bottom, left, right), _ in records:
            for row in range(top, bottom + 1):
                for column in range(left, right + 1):
                    distances = []
                    if "top" in sides:
                        distances.append(row - top)
                    if "bottom" in sides:
                        distances.append(bottom - row)
                    if "left" in sides:
                        distances.append(column - left)
                    if "right" in sides:
                        distances.append(right - column)
                    depth = min(distances)
                    output[row][column] = mapping.get(depth, mapping[deepest])
        return _freeze(output)

    return rule, {"operator": "transfer_nested_rectangle_depth_palette", "sides": "infer-maximal"}, 14


def _solid_window_recolor_proposals(train: Sequence[Pair]) -> list[tuple[Rule, dict[str, Any], int]]:
    changed_targets = {
        target[row][column]
        for source, target in train
        for row in range(len(source))
        for column in range(len(source[0]))
        if source[row][column] != target[row][column]
    }
    proposals: list[tuple[Rule, dict[str, Any], int]] = []
    for paint in sorted(changed_targets):
        # Five is the smallest window admitted by this language: it avoids
        # treating ordinary short texture runs as latent solid rectangles.
        for side in (5,):
            def rule(source: Grid, paint: int = paint, side: int = side) -> Grid | None:
                height, width = _shape(source)
                marked: set[tuple[int, int]] = set()
                for top in range(height - side + 1):
                    for left in range(width - side + 1):
                        color = source[top][left]
                        if all(source[row][column] == color for row in range(top, top + side) for column in range(left, left + side)):
                            marked.update((row, column) for row in range(top, top + side) for column in range(left, left + side))
                if not marked:
                    return None
                output = [list(row) for row in source]
                changed = 0
                for row, column in marked:
                    if output[row][column] != paint:
                        output[row][column] = paint
                        changed += 1
                return _freeze(output) if changed else None

            proposals.append((rule, {"operator": "recolor_cells_in_solid_windows", "side": side, "paint": paint}, 8))
    return proposals


def _edge_stencil_proposals() -> list[tuple[Rule, dict[str, Any], int]]:
    proposals: list[tuple[Rule, dict[str, Any], int]] = []
    for edge in ("top", "bottom", "left", "right"):
        def rule(source: Grid, edge: str = edge) -> Grid | None:
            height, width = _shape(source)
            if edge in {"top", "bottom"}:
                index = 0 if edge == "top" else height - 1
                stencil = list(source[index])
            else:
                index = 0 if edge == "left" else width - 1
                stencil = [source[row][index] for row in range(height)]
            counts = Counter(stencil)
            baseline = min(counts, key=lambda color: (-counts[color], color))
            markers = [(position, color) for position, color in enumerate(stencil) if color != baseline]
            if not markers:
                return None
            output = [list(row) for row in source]
            if edge in {"top", "bottom"}:
                for column, color in markers:
                    for row in range(height):
                        output[row][column] = color
            else:
                for row, color in markers:
                    for column in range(width):
                        output[row][column] = color
            return _freeze(output)

        proposals.append((rule, {"operator": "project_edge_stencil", "edge": edge}, 6))
    return proposals


def _translated_ring_diagonals() -> tuple[Rule, dict[str, Any], int]:
    def rule(source: Grid) -> Grid | None:
        height, width = _shape(source)
        background = _mode(source)
        palette = _palette(source) - {background}
        candidates: list[tuple[int, int, int, int]] = []
        for top in range(height - 2):
            for left in range(width - 2):
                border = [
                    source[top + dr][left + dc]
                    for dr in range(3)
                    for dc in range(3)
                    if (dr, dc) != (1, 1)
                ]
                if len(set(border)) == 1 and border[0] != background:
                    candidates.append((top + 1, left + 1, border[0], source[top + 1][left + 1]))
        if len(candidates) != 1:
            return None
        center_row, center_column, ring_color, base = candidates[0]
        if base in {background, ring_color}:
            return None
        starts = [(row, column) for row in range(height) for column in range(width) if source[row][column] == base and (row, column) != (center_row, center_column)]
        endpoints = [(row, column) for row in range(height) for column in range(width) if source[row][column] == ring_color and max(abs(row - center_row), abs(column - center_column)) > 1]
        if len(starts) != 1 or len(endpoints) != 1:
            return None
        start, endpoint = starts[0], endpoints[0]
        new_row = center_row + endpoint[0] - start[0]
        new_column = center_column + endpoint[1] - start[1]
        if not (0 <= new_row < height and 0 <= new_column < width):
            return None
        output = [[base] * width for _ in range(height)]
        for row in range(height):
            for column in range(width):
                if (row, column) != (new_row, new_column) and abs(row - new_row) == abs(column - new_column):
                    output[row][column] = ring_color
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                row, column = new_row + dr, new_column + dc
                if 0 <= row < height and 0 <= column < width and (dr or dc):
                    output[row][column] = ring_color
        return _freeze(output)

    return rule, {"operator": "translate_ring_by_encoded_path_displacement_and_extend_diagonals"}, 14


def compile_task(task: Any, limits: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    """Compile deterministic MDL-capped mixed/layout candidates."""

    bounds = Limits.from_value(limits)
    try:
        train, tests = _read_task(task, bounds)
    except _Undefined:
        return []
    if not _same_shape_guard(train):
        return []

    hypotheses: list[tuple[str, Rule, dict[str, Any], int]] = []

    def add(name: str, proposal: tuple[Rule, dict[str, Any], int] | None) -> None:
        if proposal is not None:
            hypotheses.append((name, proposal[0], proposal[1], proposal[2]))

    add("rectangle_bridges", _filled_rectangle_bridges(train))
    for proposal in _cross_center_projection_proposals(train):
        add("cross_center_projection", proposal)
    for proposal in _move_points_to_blocks_proposals(train):
        add("landmark_point_motion", proposal)
    for proposal in _greedy_aligned_block_chain(train):
        add("greedy_block_chain", proposal)
    for proposal in _marker_reflection_proposals(train):
        add("marker_axis_reflection", proposal)
    add("path_extension_recolor", _path_extension_recolor())
    add("panel_stamp", _panel_stamp())
    add("panel_connections", _panel_connections(train))
    add("rare_component_connections", _rare_aligned_component_connections())
    add("diagonal_bar_lattice", _diagonal_rotating_bar_lattice(train))
    add("periodic_comb_lattice", _periodic_comb_lattice(train))
    add("nested_rectangle_transfer", _nested_rectangle_transfer())
    for proposal in _solid_window_recolor_proposals(train):
        add("solid_window_recolor", proposal)
    for proposal in _edge_stencil_proposals():
        add("edge_stencil", proposal)
    add("translated_ring_diagonals", _translated_ring_diagonals())

    admitted: list[dict[str, Any]] = []
    for family, rule, program, complexity in hypotheses:
        candidate = _candidate(family, program, complexity, rule, train, tests, bounds)
        if candidate is not None:
            admitted.append(candidate)
    admitted.sort(key=lambda item: (item["complexity"], item["family"], _canonical(item["program"])))
    unique: list[dict[str, Any]] = []
    seen: set[str] = set()
    for candidate in admitted:
        behavior = candidate["evidence"]["behavior_hash"]
        if behavior in seen:
            continue
        seen.add(behavior)
        unique.append(candidate)
    return unique[: bounds.max_candidates]


__all__ = ["Limits", "compile_task"]
