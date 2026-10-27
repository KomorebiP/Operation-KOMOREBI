"""Bounded larger-output construction schemas for Block 13.

Author: Komorebi P.

The entrant is intentionally task agnostic.  It reads labelled demonstrations
and test inputs only, induces a small parameterized construction program, and
emits that program only after exact replay of every demonstration.  Test labels,
task identifiers, corpus hashes, and stored output grids are never inspected or
embedded.  The language is finite and MDL-capped; malformed or unsupported
tasks are ordinary abstentions.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
import hashlib
import itertools
import json
import math
from typing import Any


Grid = tuple[tuple[int, ...], ...]
Pair = tuple[Grid, Grid]
Rule = Callable[[Grid], Grid | None]


class _Undefined(ValueError):
    """Internal total-with-failure signal."""


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

        candidate_default = value.get("candidate_cap", defaults.max_candidates)
        if isinstance(candidate_default, bool) or not isinstance(candidate_default, int):
            candidate_default = defaults.max_candidates
        return cls(
            max_side=read("max_side", defaults.max_side, 60),
            max_cells=read("max_cells", defaults.max_cells, 3600),
            max_candidates=read("max_candidates", candidate_default, 256),
            max_mdl=read("max_mdl", defaults.max_mdl, 128),
        )


def _grid(value: Any, limits: Limits) -> Grid:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or not value:
        raise _Undefined("grid must be a nonempty row sequence")
    result: list[tuple[int, ...]] = []
    width: int | None = None
    for raw_row in value:
        if (
            not isinstance(raw_row, Sequence)
            or isinstance(raw_row, (str, bytes))
            or not raw_row
        ):
            raise _Undefined("invalid grid row")
        row: list[int] = []
        for cell in raw_row:
            if isinstance(cell, bool) or not isinstance(cell, int) or not 0 <= cell <= 9:
                raise _Undefined("invalid ARC color")
            row.append(int(cell))
        if width is None:
            width = len(row)
        elif width != len(row):
            raise _Undefined("ragged grid")
        result.append(tuple(row))
    if len(result) > limits.max_side or int(width or 0) > limits.max_side:
        raise _Undefined("grid exceeds side bound")
    if len(result) * int(width or 0) > limits.max_cells:
        raise _Undefined("grid exceeds cell bound")
    return tuple(result)


def _read_task(task: Any, limits: Limits) -> tuple[tuple[Pair, ...], tuple[Grid, ...]]:
    if not isinstance(task, Mapping):
        raise _Undefined("task must be a mapping")
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
        raise _Undefined("task needs train and test examples")
    train: list[Pair] = []
    for example in raw_train:
        if not isinstance(example, Mapping):
            raise _Undefined("malformed demonstration")
        train.append((_grid(example.get("input"), limits), _grid(example.get("output"), limits)))
    tests: list[Grid] = []
    for example in raw_test:
        if not isinstance(example, Mapping):
            raise _Undefined("malformed test example")
        # Deliberately read only the authorized test input field.
        tests.append(_grid(example.get("input"), limits))
    return tuple(train), tuple(tests)


def _shape(grid: Grid) -> tuple[int, int]:
    return len(grid), len(grid[0])


def _plain(grid: Grid) -> list[list[int]]:
    return [list(row) for row in grid]


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _mode(grid: Grid) -> int:
    counts = Counter(cell for row in grid for cell in row)
    return min(counts, key=lambda color: (-counts[color], color))


def _palette(grid: Grid) -> set[int]:
    return {cell for row in grid for cell in row}


def _checked(grid: Grid | None, limits: Limits) -> Grid:
    if grid is None or not grid or not grid[0]:
        raise _Undefined("undefined construction")
    height, width = _shape(grid)
    if height > limits.max_side or width > limits.max_side or height * width > limits.max_cells:
        raise _Undefined("construction exceeds bound")
    if any(len(row) != width or any(not 0 <= cell <= 9 for cell in row) for row in grid):
        raise _Undefined("invalid constructed grid")
    return grid


def _matrix(height: int, width: int, color: int) -> list[list[int]]:
    if height <= 0 or width <= 0:
        raise _Undefined("nonpositive shape")
    return [[color for _ in range(width)] for _ in range(height)]


def _freeze(rows: Sequence[Sequence[int]]) -> Grid:
    return tuple(tuple(int(cell) for cell in row) for row in rows)


def _tile(grid: Grid, row_factor: int, column_factor: int) -> Grid:
    return tuple(
        tuple(cell for _ in range(column_factor) for cell in row)
        for _ in range(row_factor)
        for row in grid
    )


def _repeat_tiles(grid: Grid, row_factor: int, column_factor: int) -> Grid:
    rows: list[tuple[int, ...]] = []
    for _ in range(row_factor):
        for row in grid:
            rows.append(tuple(row) * column_factor)
    return tuple(rows)


def _r270(grid: Grid) -> Grid:
    return tuple(tuple(row) for row in reversed(tuple(zip(*grid))))


def _rotate90(grid: Grid) -> Grid:
    return tuple(tuple(reversed(row)) for row in zip(*grid))


def _rotate180(grid: Grid) -> Grid:
    return tuple(tuple(reversed(row)) for row in reversed(grid))


def _rotate270(grid: Grid) -> Grid:
    return tuple(reversed(tuple(zip(*grid))))


def _crop_nonbackground(grid: Grid, background: int) -> Grid:
    points = [
        (row, column)
        for row, values in enumerate(grid)
        for column, value in enumerate(values)
        if value != background
    ]
    if not points:
        raise _Undefined("empty foreground")
    top = min(row for row, _ in points)
    bottom = max(row for row, _ in points)
    left = min(column for _, column in points)
    right = max(column for _, column in points)
    return tuple(tuple(row[left : right + 1]) for row in grid[top : bottom + 1])


def _added_colors(train: Sequence[Pair]) -> set[int]:
    added: set[int] | None = None
    for source, target in train:
        current = _palette(target) - _palette(source)
        added = current if added is None else added & current
    return added or set()


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
        _canonical(program)
        replay = [_checked(rule(source), limits) for source, _ in train]
        if any(result != target for result, (_, target) in zip(replay, train)):
            return None
        predictions = [_checked(rule(source), limits) for source in tests]
    except (_Undefined, IndexError, KeyError, TypeError, ValueError, ZeroDivisionError):
        return None
    behavior = hashlib.sha256(
        _canonical([_plain(grid) for grid in predictions]).encode("ascii")
    ).hexdigest()
    return {
        "family": family,
        "program": json.loads(_canonical(program)),
        "train_outputs": [_plain(grid) for grid in replay],
        "test_outputs": [_plain(grid) for grid in predictions],
        "complexity": int(complexity),
        "evidence": {
            "all_demonstrations_exact": True,
            "demonstration_count": len(train),
            "test_count": len(tests),
            "behavior_hash": behavior,
            "bounded_search": True,
            "mdl": int(complexity),
        },
    }


def _edge_duplicate_frame(train: Sequence[Pair]) -> tuple[Rule, dict[str, Any], int] | None:
    backgrounds = {target[0][0] for _, target in train}
    if len(backgrounds) != 1:
        return None
    background = next(iter(backgrounds))

    def rule(source: Grid) -> Grid:
        rows = [(background,) + source[0] + (background,)]
        rows.extend((row[0],) + row + (row[-1],) for row in source)
        rows.append((background,) + source[-1] + (background,))
        return tuple(rows)

    return rule, {"operator": "edge_duplicate_frame", "corner_fill": background}, 6


def _offset_stack(train: Sequence[Pair]) -> tuple[Rule, dict[str, Any], int] | None:
    added = _added_colors(train)
    if len(added) != 1:
        return None
    separator = next(iter(added))

    def rule(source: Grid) -> Grid | None:
        height, width = _shape(source)
        if height % 2:
            return None
        middle = height // 2
        output = _matrix(height + 1, width + 1, separator)
        for row in range(middle):
            output[row][:width] = source[row]
        for row in range(middle, height):
            output[row + 1][1:] = source[row]
        return _freeze(output)

    return rule, {"operator": "offset_half_stack", "separator": separator, "offset": [0, 1]}, 7


def _histogram_columns(train: Sequence[Pair]) -> tuple[Rule, dict[str, Any], int] | None:
    fillers = {
        cell
        for source, target in train
        for cell in _palette(target) - _palette(source)
    }
    if len(fillers) != 1:
        return None
    filler = next(iter(fillers))

    def rule(source: Grid) -> Grid:
        counts = Counter(cell for row in source for cell in row)
        colors = sorted(counts, key=lambda color: (-counts[color], color))
        height = max(counts.values())
        return tuple(
            tuple(color if row < counts[color] else filler for color in colors)
            for row in range(height)
        )

    return rule, {"operator": "frequency_columns", "order": "count_desc_color_asc", "fill": filler}, 7


def _growing_prefix(train: Sequence[Pair]) -> tuple[Rule, dict[str, Any], int] | None:
    divisors = []
    for divisor in range(1, 11):
        if all(
            len(source) == 1
            and len(target[0]) == len(source[0])
            and len(target) == len(source[0]) // divisor
            for source, target in train
        ):
            divisors.append(divisor)
    if not divisors:
        return None
    divisor = min(divisors)

    def rule(source: Grid) -> Grid | None:
        if len(source) != 1:
            return None
        row = source[0]
        foreground, background = row[0], row[-1]
        if foreground == background:
            return None
        prefix = 0
        while prefix < len(row) and row[prefix] == foreground:
            prefix += 1
        if any(cell != background for cell in row[prefix:]):
            return None
        height = len(row) // divisor
        if height <= 0 or prefix + height - 1 > len(row):
            return None
        return tuple(
            tuple(foreground if column < prefix + step else background for column in range(len(row)))
            for step in range(height)
        )

    return rule, {"operator": "growing_prefix_bar", "height_divisor": divisor, "growth": 1}, 5


def _slanted_rows(train: Sequence[Pair]) -> tuple[Rule, dict[str, Any], int] | None:
    backgrounds = {target[0][0] for _, target in train}
    if len(backgrounds) != 1:
        return None
    background = next(iter(backgrounds))

    def rule(source: Grid) -> Grid:
        height, _ = _shape(source)
        return tuple(
            (background,) * (height - 1 - row_index)
            + row
            + (background,) * row_index
            for row_index, row in enumerate(source)
        )

    return rule, {"operator": "slanted_row_padding", "slope": -1, "fill": background}, 5


def _vertical_reflection(train: Sequence[Pair]) -> tuple[Rule, dict[str, Any], int] | None:
    def rule(source: Grid) -> Grid | None:
        height, _ = _shape(source)
        if height < 2:
            return None
        period = 2 * height - 2
        output_height = 4 * height - 3
        rows = []
        for index in range(output_height):
            phase = index % period
            source_index = phase if phase < height else period - phase
            rows.append(source[source_index])
        return tuple(rows)

    return rule, {"operator": "vertical_reflection_extension", "periods": 2}, 5


def _diagonal_slide(train: Sequence[Pair]) -> tuple[Rule, dict[str, Any], int] | None:
    if any(len(source) != 1 for source, _ in train):
        return None
    backgrounds = {source[0][0] for source, _ in train if source[0][0] == 0}
    background = 0 if backgrounds else min(_palette(train[0][0]))

    def rule(source: Grid) -> Grid | None:
        if len(source) != 1:
            return None
        row = source[0]
        active = [cell for cell in row if cell != background]
        if not active:
            return None
        side = len(row) * len(active)
        output = _matrix(side, side, background)
        for output_row in range(side):
            start = side - 1 - output_row
            for column, cell in enumerate(row):
                destination = start + column
                if 0 <= destination < side:
                    output[output_row][destination] = cell
        return _freeze(output)

    return rule, {"operator": "sliding_row_diagonal", "side": "width_times_active_count", "fill": background}, 7


def _seeded_ray_lattice(train: Sequence[Pair]) -> tuple[Rule, dict[str, Any], int] | None:
    added = _added_colors(train)
    if len(added) != 1:
        return None
    lattice_color = next(iter(added))

    def rule(source: Grid) -> Grid | None:
        if len(source) != 1 or len(source[0]) % 2 == 0:
            return None
        width = len(source[0])
        background = _mode(source)
        points = [column for column, cell in enumerate(source[0]) if cell != background]
        if points != [width // 2]:
            return None
        seed_color = source[0][points[0]]
        center = width // 2
        output = _matrix(width, width, background)
        for row in range(width):
            for column in (center - row, center + row):
                if 0 <= column < width:
                    output[row][column] = seed_color
            if row >= 3:
                radius = row - 2
                for column in range(max(0, center - radius), min(width, center + radius + 1)):
                    if (column - row - center) % 4 == 0 and output[row][column] == background:
                        output[row][column] = lattice_color
        return _freeze(output)

    return rule, {
        "operator": "seeded_ray_lattice",
        "primary_rays": [-1, 1],
        "secondary_period": 4,
        "secondary_cone_delay": 2,
        "secondary_color": lattice_color,
    }, 9


def _encoded_path(train: Sequence[Pair]) -> tuple[Rule, dict[str, Any], int] | None:
    added = _added_colors(train)
    if len(added) != 1:
        return None
    marker = next(iter(added))

    def rule(source: Grid) -> Grid | None:
        if len(source) != 2:
            return None
        background = 0 if 0 in _palette(source) else _mode(source)
        inks = _palette(source) - {background}
        if len(inks) != 1:
            return None
        ink = next(iter(inks))
        groups: list[list[tuple[bool, bool]]] = []
        current_group: list[tuple[bool, bool]] = []
        for column in range(len(source[0])):
            token = (source[0][column] != background, source[1][column] != background)
            if token == (False, False):
                if current_group:
                    groups.append(current_group)
                    current_group = []
            else:
                current_group.append(token)
        if current_group:
            groups.append(current_group)
        if not groups:
            return None
        commands: list[str] = []
        for group in groups:
            if group == [(False, True), (True, True)]:
                commands.append("left")
            elif group == [(True, True), (False, True)]:
                commands.append("right")
            elif group == [(True, True)]:
                commands.append("straight")
            else:
                return None
        width = len(commands) + 2
        position = width // 2
        rows: list[list[int]] = [[background for _ in range(width)]]
        rows[0][position] = marker
        for command in commands:
            if command == "straight":
                for _ in range(2):
                    row = [background for _ in range(width)]
                    row[position] = ink
                    rows.append(row)
                continue
            displacement = -1 if command == "left" else 1
            destination = position + displacement
            if not 0 <= destination < width:
                return None
            row = [background for _ in range(width)]
            row[position] = ink
            row[destination] = ink
            rows.append(row)
            position = destination
        return _freeze(rows)

    return rule, {
        "operator": "two_row_instruction_path",
        "tokens": {"01,11": "left", "11,01": "right", "11": "straight2"},
        "marker": marker,
    }, 10


def _max_index_table(train: Sequence[Pair]) -> tuple[Rule, dict[str, Any], int] | None:
    def rule(source: Grid) -> Grid | None:
        size, width = _shape(source)
        if size != width:
            return None
        sequence = list(source[0])
        for row in range(size):
            for column in range(size):
                if source[row][column] != sequence[max(row, column)]:
                    return None
        if sequence[-1] == 0 and all(cell == 0 for cell in source[-1]) and all(row[-1] == 0 for row in source):
            while len(sequence) > 1 and sequence[-1] == 0:
                sequence.pop()
        if not sequence:
            return None
        extended = [sequence[index % len(sequence)] for index in range(2 * size)]
        return tuple(
            tuple(extended[max(row, column)] for column in range(2 * size))
            for row in range(2 * size)
        )

    return rule, {"operator": "max_index_periodic_extension", "factor": 2, "trim_zero_border": True}, 8


def _shell_extension(train: Sequence[Pair]) -> tuple[Rule, dict[str, Any], int] | None:
    def rule(source: Grid) -> Grid | None:
        size, width = _shape(source)
        if size != width or size < 3 or size % 2 == 0:
            return None
        corner = source[0][0]
        center = source[size // 2][size // 2]
        common = _mode(source)
        if len({corner, center, common}) != 3:
            return None
        # The recognized seed is a symmetric three-role diamond.
        if any(source[r][c] != source[size - 1 - r][c] for r in range(size) for c in range(size)):
            return None
        if any(source[r][c] != source[r][size - 1 - c] for r in range(size) for c in range(size)):
            return None
        output = _matrix(2 * size, 2 * size, corner)
        for row in range(size):
            output[row][:size] = source[row]
        cycle = (center, common, corner)
        previous = source[-1][-1]
        for shell in range(size, 2 * size):
            for index in range(shell):
                output[shell][index] = previous
                output[index][shell] = previous
            current = cycle[(shell - size) % 3]
            output[shell][shell] = current
            previous = current
        return _freeze(output)

    return rule, {"operator": "symmetric_shell_extension", "diagonal_cycle": ["center", "mode", "corner"], "factor": 2}, 10


def _nested_quadrant_rings(train: Sequence[Pair]) -> tuple[Rule, dict[str, Any], int] | None:
    def rule(source: Grid) -> Grid | None:
        height, width = _shape(source)
        if height % 2 or width % 2:
            return None
        blocks = [
            (
                source[row][column],
                source[row][column + 1],
                source[row + 1][column],
                source[row + 1][column + 1],
            )
            for row in range(0, height, 2)
            for column in range(0, width, 2)
        ]
        if not blocks:
            return None
        side = 2 * len(blocks)
        output = _matrix(side, side, 0)
        for ring, (upper_left, upper_right, lower_left, lower_right) in enumerate(reversed(blocks)):
            low, high = ring, side - 1 - ring
            local_side = high - low + 1
            split = local_side // 2
            for offset in range(local_side):
                output[low][low + offset] = upper_left if offset < split else upper_right
                output[high][low + offset] = lower_left if offset < split else lower_right
                output[low + offset][low] = upper_left if offset < split else lower_left
                output[low + offset][high] = upper_right if offset < split else lower_right
        return _freeze(output)

    return rule, {"operator": "nested_quadrant_rings", "source_blocks": [2, 2], "order": "reverse_row_major"}, 9


def _chebyshev_ring_cursor(train: Sequence[Pair]) -> tuple[Rule, dict[str, Any], int] | None:
    scales: set[int] = set()
    for source, target in train:
        size, width = _shape(source)
        target_size, target_width = _shape(target)
        if size != width or target_size != target_width or size < 2 or (target_size - 1) % (size - 1):
            return None
        scales.add((target_size - 1) // (size - 1))
    if len(scales) != 1:
        return None
    scale = next(iter(scales))

    def rule(source: Grid) -> Grid | None:
        size, width = _shape(source)
        if size != width:
            return None
        counts = Counter(cell for row in source for cell in row)
        singletons = [color for color, count in counts.items() if count == 1]
        if len(singletons) != 1 or len(counts) != 2:
            return None
        foreground = singletons[0]
        background = next(color for color in counts if color != foreground)
        seed_row, seed_column = next(
            (row, column)
            for row, values in enumerate(source)
            for column, cell in enumerate(values)
            if cell == foreground
        )
        side = scale * (size - 1) + 1
        center_row, center_column = scale * seed_row, scale * seed_column
        output = [
            [
                foreground
                if max(abs(row - center_row), abs(column - center_column)) % 2 == 0
                else background
                for column in range(side)
            ]
            for row in range(side)
        ]
        # A one-cell cursor cuts through the nested rings from the north-west;
        # toggling (rather than erasing) keeps the corridor continuous.
        for distance in range(1, center_row + 1):
            row = center_row - distance
            column = center_column - distance + 1
            if column < 0:
                break
            output[row][column] = background if output[row][column] == foreground else foreground
        return _freeze(output)

    return rule, {"operator": "chebyshev_ring_cursor", "coordinate_scale": scale, "cursor": "northwest_toggle"}, 9


def _periodic_max_table(train: Sequence[Pair]) -> tuple[Rule, dict[str, Any], int] | None:
    # Alias retained as a distinct hypothesis family for clear tournament logs.
    return _max_index_table(train)


def _uniform_lattice(train: Sequence[Pair]) -> tuple[Rule, dict[str, Any], int] | None:
    sides = {_shape(target) for _, target in train}
    if len(sides) != 1:
        return None
    side, width = next(iter(sides))
    if side != width:
        return None
    backgrounds = _added_colors(train)
    if len(backgrounds) != 1:
        return None
    background = next(iter(backgrounds))

    def rule(source: Grid) -> Grid | None:
        size, source_width = _shape(source)
        values = _palette(source)
        if size != source_width or len(values) != 1:
            return None
        foreground = next(iter(values))
        step = size + 1
        return tuple(
            tuple(
                foreground if (row + 1) % step == 0 or (column + 1) % step == 0 else background
                for column in range(side)
            )
            for row in range(side)
        )

    return rule, {"operator": "fixed_canvas_lattice", "side": side, "spacing": "input_side_plus_one", "fill": background}, 7


def _filled_columns_tile(train: Sequence[Pair]) -> tuple[Rule, dict[str, Any], int] | None:
    added = _added_colors(train)
    if len(added) != 1:
        return None
    accent = next(iter(added))

    def rule(source: Grid) -> Grid:
        background = _mode(source)
        active_columns = {
            column
            for column in range(len(source[0]))
            if any(source[row][column] != background for row in range(len(source)))
        }
        base = tuple(
            tuple(accent if cell == background and column in active_columns else cell for column, cell in enumerate(row))
            for row in source
        )
        return _repeat_tiles(base, 2, 2)

    return rule, {"operator": "fill_active_columns_then_tile", "accent": accent, "tile": [2, 2]}, 7


def _paint_stencil(
    source: Grid,
    factor: int,
    background: int,
    stencils: Sequence[tuple[int, Sequence[tuple[int, int]]]],
) -> Grid:
    base = _repeat_tiles(source, factor, factor)
    height, width = _shape(base)
    active = [(row, column) for row in range(height) for column in range(width) if base[row][column] != background]
    output = [list(row) for row in base]
    for color, offsets in stencils:
        destinations: set[tuple[int, int]] = set()
        for row, column in active:
            for dr, dc in offsets:
                rr, cc = row + dr, column + dc
                if 0 <= rr < height and 0 <= cc < width:
                    destinations.add((rr, cc))
        for row, column in sorted(destinations):
            if base[row][column] == background and output[row][column] == background:
                output[row][column] = color
    return _freeze(output)


def _paint_toroidal_stencil(
    source: Grid,
    factor: int,
    background: int,
    color: int,
    offsets: Sequence[tuple[int, int]],
) -> Grid:
    """Paint a stencil on one periodic cell, then repeat the completed cell."""

    height, width = _shape(source)
    output = [list(row) for row in source]
    active = [(row, column) for row in range(height) for column in range(width) if source[row][column] != background]
    for row, column in active:
        for dr, dc in offsets:
            rr, cc = (row + dr) % height, (column + dc) % width
            if source[rr][cc] == background:
                output[rr][cc] = color
    return _repeat_tiles(_freeze(output), factor, factor)


def _stencil_rules(train: Sequence[Pair]) -> list[tuple[Rule, dict[str, Any], int]]:
    results: list[tuple[Rule, dict[str, Any], int]] = []
    shape_factors = []
    for source, target in train:
        sh, sw = _shape(source)
        th, tw = _shape(target)
        if th % sh or tw % sw or th // sh != tw // sw:
            return results
        shape_factors.append(th // sh)
    if len(set(shape_factors)) != 1:
        return results
    factor = shape_factors[0]
    if factor not in (2, 3):
        return results
    added_sets = [_palette(target) - _palette(source) for source, target in train]
    if not added_sets or any(item != added_sets[0] for item in added_sets):
        return results
    added = sorted(added_sets[0])
    if len(added) == 1:
        accent = added[0]
        options = (
            ("northwest_periodic", ((-1, -1),)),
            ("four_diagonals", ((-1, -1), (-1, 1), (1, -1), (1, 1))),
        )
        for name, offsets in options:
            def rule(source: Grid, offsets: tuple[tuple[int, int], ...] = offsets, name: str = name) -> Grid:
                if name == "northwest_periodic":
                    return _paint_toroidal_stencil(source, factor, _mode(source), accent, offsets)
                return _paint_stencil(source, factor, _mode(source), ((accent, offsets),))

            results.append((rule, {"operator": "tile_then_stencil", "tile": [factor, factor], "stencil": name, "accent": accent}, 7 + len(offsets)))
    elif len(added) == 2:
        horizontal = ((0, -1), (0, 1))
        diagonal = ((-1, -1), (1, 1))
        for first, second in itertools.permutations(added):
            for reverse_priority in (False, True):
                specs = ((first, horizontal), (second, diagonal))
                if reverse_priority:
                    specs = tuple(reversed(specs))

                def rule(source: Grid, specs: tuple[tuple[int, Sequence[tuple[int, int]]], ...] = specs) -> Grid:
                    return _paint_stencil(source, factor, _mode(source), specs)

                results.append((rule, {
                    "operator": "tile_then_stencil",
                    "tile": [factor, factor],
                    "stencils": [
                        {"accent": color, "offsets": [list(offset) for offset in offsets]}
                        for color, offsets in specs
                    ],
                }, 13))
    return results


def _row_diagonal_ray_tile(train: Sequence[Pair]) -> tuple[Rule, dict[str, Any], int] | None:
    factors: list[int] = []
    additions: list[set[int]] = []
    for source, target in train:
        sh, sw = _shape(source)
        th, tw = _shape(target)
        if th % sh or tw % sw or th // sh != tw // sw:
            return None
        factors.append(th // sh)
        additions.append(_palette(target) - _palette(source))
    if len(set(factors)) != 1 or any(colors != additions[0] for colors in additions) or len(additions[0]) != 2:
        return None
    factor = factors[0]
    colors = sorted(additions[0])

    def construct(source: Grid, row_color: int, diagonal_color: int) -> Grid:
        background = _mode(source)
        base = _repeat_tiles(source, factor, factor)
        height, width = _shape(base)
        active = [(row, column) for row in range(height) for column in range(width) if base[row][column] != background]
        output = [list(row) for row in base]
        active_rows = {row for row, _ in active}
        for row in active_rows:
            for column in range(width):
                if output[row][column] == background:
                    output[row][column] = row_color
        for row, column in active:
            for dr, dc in ((-1, -1), (1, 1)):
                rr, cc = row + dr, column + dc
                if 0 <= rr < height and 0 <= cc < width and output[rr][cc] == background:
                    output[rr][cc] = diagonal_color
        return _freeze(output)

    # The demonstrations decide which added color owns rows and which owns
    # descending diagonals.  Only the exact ordering survives replay.
    for row_color, diagonal_color in itertools.permutations(colors):
        def rule(source: Grid, row_color: int = row_color, diagonal_color: int = diagonal_color) -> Grid:
            return construct(source, row_color, diagonal_color)

        if all(rule(source) == target for source, target in train):
            return rule, {
                "operator": "tile_then_row_and_diagonal_rays",
                "tile": [factor, factor],
                "row_accent": row_color,
                "diagonal_accent": diagonal_color,
            }, 10
    return None


def _triangle_outline_growth(train: Sequence[Pair]) -> tuple[Rule, dict[str, Any], int] | None:
    target_shapes = {_shape(target) for _, target in train}
    if len(target_shapes) != 1:
        return None
    side, width = next(iter(target_shapes))
    if side != width:
        return None

    def rule(source: Grid) -> Grid | None:
        height, source_width = _shape(source)
        background = _mode(source)
        colors = _palette(source) - {background}
        if len(colors) != 1:
            return None
        foreground = next(iter(colors))
        points = [(r, c) for r in range(height) for c in range(source_width) if source[r][c] == foreground]
        top, bottom = min(r for r, _ in points), max(r for r, _ in points)
        left, right = min(c for _, c in points), max(c for _, c in points)
        size = bottom - top + 1
        if size != right - left + 1 or size < 2:
            return None
        horizontal_edges = [edge for edge in (0, size - 1) if all(source[top + edge][left + c] == foreground for c in range(size))]
        vertical_edges = [edge for edge in (0, size - 1) if all(source[top + r][left + edge] == foreground for r in range(size))]
        if len(horizontal_edges) != 1 or len(vertical_edges) != 1:
            return None
        hr, vc = horizontal_edges[0], vertical_edges[0]
        expected = {(hr, c) for c in range(size)} | {(r, vc) for r in range(size)}
        actual = {(r - top, c - left) for r, c in points}
        if actual != expected:
            return None
        expanded = 2 * size
        if expanded > side:
            return None
        anchor_top = 0 if top == 0 else side - expanded if bottom == height - 1 else None
        anchor_left = 0 if left == 0 else side - expanded if right == source_width - 1 else None
        if anchor_top is None or anchor_left is None:
            return None
        output = _matrix(side, side, background)
        er = 0 if hr == 0 else expanded - 1
        ec = 0 if vc == 0 else expanded - 1
        for index in range(expanded):
            output[anchor_top + er][anchor_left + index] = foreground
            output[anchor_top + index][anchor_left + ec] = foreground
            diagonal_column = expanded - 1 - index if er == ec else index
            output[anchor_top + index][anchor_left + diagonal_column] = foreground
        return _freeze(output)

    return rule, {"operator": "corner_L_to_triangle_outline", "scale": 2, "canvas_side": side}, 11


def _four_way_orbit(train: Sequence[Pair]) -> tuple[Rule, dict[str, Any], int] | None:
    def rule(source: Grid) -> Grid | None:
        background = _mode(source)
        motif = _crop_nonbackground(source, background)
        height, width = _shape(motif)
        if height > width:
            return None
        side = 2 * width + height
        output = _matrix(side, side, background)
        placements = (
            (motif, width, 0),
            (_rotate90(motif), 0, width),
            (_rotate180(motif), width, width + height),
            (_rotate270(motif), width + height, width),
        )
        for tile, top, left in placements:
            for row, values in enumerate(tile):
                for column, cell in enumerate(values):
                    if cell != background:
                        old = output[top + row][left + column]
                        if old != background and old != cell:
                            return None
                        output[top + row][left + column] = cell
        return _freeze(output)

    return rule, {"operator": "four_way_rotational_orbit", "layout": "around_central_gap"}, 10


def _glyph_bar_layout(train: Sequence[Pair]) -> tuple[Rule, dict[str, Any], int] | None:
    def rule(source: Grid) -> Grid | None:
        background = _mode(source)
        counts = Counter(cell for row in source for cell in row if cell != background)
        markers = sorted(color for color, count in counts.items() if count == 1)
        bars: list[tuple[int, int]] = []
        for color, count in counts.items():
            if count == 1:
                continue
            side = math.isqrt(count)
            if side * side != count:
                return None
            bars.append((side, color))
        if len(bars) != 2 or len(markers) > 1:
            return None
        bars.sort()
        height = max(side for side, _ in bars)
        width = sum(side for side, _ in bars) + len(bars) - 1 + (2 if markers else 0)
        output = _matrix(height, width, background)
        column = 0
        if markers:
            output[-1][0] = markers[0]
            column = 2
        for index, (side, color) in enumerate(bars):
            top = height - side
            for row in range(top, height):
                for destination in range(column, column + side):
                    output[row][destination] = color
            column += side
            if index + 1 < len(bars):
                column += 1
        return _freeze(output)

    return rule, {
        "operator": "glyph_area_to_bar_layout",
        "side_measure": "integer_sqrt_support_count",
        "bar_order": "side_ascending",
        "alignment": "bottom",
        "singleton_role": "optional_prefix_marker",
    }, 10


def _dual_rectangle_layout(train: Sequence[Pair]) -> tuple[Rule, dict[str, Any], int] | None:
    target_heights = {len(target) for _, target in train}
    if len(target_heights) != 1:
        return None
    canvas_height = next(iter(target_heights))

    def rule(source: Grid) -> Grid | None:
        height, width = _shape(source)
        background = _mode(source)
        colors = _palette(source) - {background}
        if len(colors) != 1:
            return None
        foreground = next(iter(colors))
        column_heights: list[int] = []
        for column in range(width):
            prefix = 0
            while prefix < height and source[prefix][column] == foreground:
                prefix += 1
            if any(source[row][column] != background for row in range(prefix, height)):
                return None
            column_heights.append(prefix)
        rectangles: list[tuple[int, int]] = []
        column = 0
        while column < width:
            if column_heights[column] == 0:
                column += 1
                continue
            start = column
            rectangle_height = column_heights[column]
            while column < width and column_heights[column] != 0:
                if column_heights[column] != rectangle_height:
                    return None
                column += 1
            rectangles.append((rectangle_height, column - start))
        if not rectangles:
            return None
        landscape = [(min(h, w), max(h, w)) for h, w in rectangles]
        portrait = [(max(h, w), min(h, w)) for h, w in rectangles]
        top_width = sum(width for _, width in landscape) + len(landscape) - 1
        bottom_width = sum(width for _, width in portrait) + len(portrait) - 1
        canvas_width = max(top_width, bottom_width)
        if any(block_height > canvas_height for block_height, _ in landscape + portrait):
            return None
        output = _matrix(canvas_height, canvas_width, background)
        cursor = 0
        for block_height, block_width in landscape:
            for row in range(block_height):
                for destination in range(cursor, cursor + block_width):
                    output[row][destination] = foreground
            cursor += block_width + 1
        cursor = 0
        for block_height, block_width in portrait:
            for row in range(canvas_height - block_height, canvas_height):
                for destination in range(cursor, cursor + block_width):
                    output[row][destination] = foreground
            cursor += block_width + 1
        return _freeze(output)

    return rule, {
        "operator": "bar_code_dual_rectangle_layout",
        "top_orientation": "landscape",
        "bottom_orientation": "portrait",
        "gap": 1,
        "canvas_height": canvas_height,
    }, 11


def _split_adjacent_squares(source: Grid) -> tuple[Grid, Grid] | None:
    height, width = _shape(source)
    if width == 2 * height:
        return (
            tuple(tuple(row[:height]) for row in source),
            tuple(tuple(row[height:]) for row in source),
        )
    if height == 2 * width:
        return tuple(source[:width]), tuple(source[width:])
    return None


def _panel_kronecker(train: Sequence[Pair]) -> tuple[Rule, dict[str, Any], int] | None:
    motif_colors: set[int] | None = None
    for source, _ in train:
        panels = _split_adjacent_squares(source)
        if panels is None:
            return None
        background = 0 if 0 in _palette(source) else _mode(source)
        binary_colors = [(_palette(panel) - {background}) for panel in panels]
        choices = [colors for colors in binary_colors if len(colors) == 1]
        if not choices:
            return None
        current = set.intersection(*choices) if len(choices) > 1 else set(choices[0])
        motif_colors = current if motif_colors is None else motif_colors & current
    if not motif_colors:
        return None
    motif_color = min(motif_colors)

    def rule(source: Grid) -> Grid | None:
        panels = _split_adjacent_squares(source)
        if panels is None:
            return None
        background = 0 if 0 in _palette(source) else _mode(source)
        indices = [
            index
            for index, panel in enumerate(panels)
            if _palette(panel) - {background} == {motif_color}
        ]
        if len(indices) != 1:
            return None
        motif = panels[indices[0]]
        carrier = panels[1 - indices[0]]
        size = len(motif)
        output = _matrix(size * size, size * size, background)
        for br in range(size):
            for bc in range(size):
                carrier_color = carrier[br][bc]
                if carrier_color == background:
                    continue
                for row in range(size):
                    for column in range(size):
                        if motif[row][column] != background:
                            output[br * size + row][bc * size + column] = carrier_color
        return _freeze(output)

    return rule, {"operator": "adjacent_panel_kronecker", "motif_color": motif_color, "color_mode": "carrier"}, 9


def _split_four_separator_panels(source: Grid, separator: int) -> tuple[Grid, Grid, Grid, Grid] | None:
    height, width = _shape(source)
    columns = [column for column in range(width) if all(source[row][column] == separator for row in range(height))]
    if len(columns) != 3:
        return None
    starts = (0, columns[0] + 1, columns[1] + 1, columns[2] + 1)
    ends = (columns[0], columns[1], columns[2], width)
    widths = [end - start for start, end in zip(starts, ends)]
    if any(panel_width != height for panel_width in widths[:3]) or widths[3] not in (height, height - 1):
        return None
    background = source[0][0]
    panels: list[Grid] = []
    for start, end in zip(starts, ends):
        rows = [list(row[start:end]) for row in source]
        if end - start == height - 1:
            for row in rows:
                row.append(background)
        panels.append(_freeze(rows))
    return tuple(panels)  # type: ignore[return-value]


def _panel_mask_product(train: Sequence[Pair]) -> tuple[Rule, dict[str, Any], int] | None:
    separators: set[int] | None = None
    for source, _ in train:
        candidates = {
            color
            for color in _palette(source)
            if _split_four_separator_panels(source, color) is not None
        }
        separators = candidates if separators is None else separators & candidates
    if not separators:
        return None
    separator = min(separators)

    def rule(source: Grid) -> Grid | None:
        panels = _split_four_separator_panels(source, separator)
        if panels is None:
            return None
        size = len(source) - 2
        if size <= 0:
            return None
        inner = [tuple(tuple(row[1:-1]) for row in panel[1:-1]) for panel in panels]
        background = panels[0][0][0]
        colors2 = _palette(inner[2]) - {background}
        colors3 = _palette(inner[3]) - {background}
        if len(colors2) != 1 or len(colors3) != 1:
            return None
        color_true, color_false = next(iter(colors2)), next(iter(colors3))
        output = _matrix(size * size, size * size, color_false)
        for block_row in range(size):
            for block_column in range(size):
                if inner[1][block_row][block_column] == background:
                    continue
                for row in range(size):
                    for column in range(size):
                        if inner[0][row][column] != background:
                            output[block_row * size + row][block_column * size + column] = color_true
        return _freeze(output)

    return rule, {"operator": "separator_panel_mask_product", "separator": separator, "panel_roles": ["inner_mask", "outer_mask", "true_color", "false_color"]}, 12


def _boundary_motif_blocks(train: Sequence[Pair]) -> tuple[Rule, dict[str, Any], int] | None:
    backgrounds = {target[0][0] for _, target in train}
    if len(backgrounds) != 1:
        return None
    background = next(iter(backgrounds))

    def rule(source: Grid) -> Grid | None:
        size, width = _shape(source)
        colors = _palette(source) - {background}
        if size != width or len(colors) != 1:
            return None
        foreground = next(iter(colors))
        block_side = size + 2
        output = _matrix(block_side * size, block_side * size, background)

        def paste(tile: Grid, block_row: int, block_column: int) -> None:
            top, left = block_row * size, block_column * size
            for row, values in enumerate(tile):
                for column, cell in enumerate(values):
                    output[top + row][left + column] = cell

        solid = tuple(tuple(foreground for _ in range(size)) for _ in range(size))
        for row in range(size):
            for column in range(size):
                if source[row][column] == background:
                    continue
                paste(solid, row + 1, column + 1)
                if row == 0:
                    paste(source, 0, column + 1)
                if row == size - 1:
                    paste(source, size + 1, column + 1)
                if column == 0:
                    paste(source, row + 1, 0)
                if column == size - 1:
                    paste(source, row + 1, size + 1)
        return _freeze(output)

    return rule, {"operator": "boundary_motif_block_expansion", "padding_blocks": 1}, 11


def _marker_square_chain(train: Sequence[Pair]) -> tuple[Rule, dict[str, Any], int] | None:
    shapes = {_shape(target) for _, target in train}
    if len(shapes) != 1:
        return None
    side, width = next(iter(shapes))
    if side != width:
        return None

    def rule(source: Grid) -> Grid | None:
        background = _mode(source)
        counts = Counter(cell for row in source for cell in row if cell != background)
        if len(counts) != 2:
            return None
        marker_choices = [color for color, count in counts.items() if count == 1]
        if len(marker_choices) != 1:
            return None
        marker = marker_choices[0]
        foreground = next(color for color in counts if color != marker)
        points = [(r, c) for r, row in enumerate(source) for c, value in enumerate(row) if value != background]
        if len(points) != 4:
            return None
        top, bottom = min(r for r, _ in points), max(r for r, _ in points)
        left, right = min(c for _, c in points), max(c for _, c in points)
        if bottom - top != 1 or right - left != 1:
            return None
        mr, mc = next((r, c) for r, c in points if source[r][c] == marker)
        dr = 1 if mr == top else -1
        dc = 1 if mc == left else -1
        block = len(points)
        if side != 2 * block + 1:
            return None
        start_row = side - 2 * block if dr > 0 else side - block - 1
        start_column = side - 2 * block if dc > 0 else side - block - 1
        output = _matrix(side, side, background)
        for step in range(2):
            top_row = start_row + step * block * dr
            left_column = start_column + step * block * dc
            for row in range(top_row, top_row + block):
                for column in range(left_column, left_column + block):
                    if not (0 <= row < side and 0 <= column < side):
                        return None
                    output[row][column] = foreground
        return _freeze(output)

    return rule, {"operator": "marker_oriented_square_chain", "blocks": 2, "block_side": "support_count", "canvas_side": side}, 10


def _framed_repeat(train: Sequence[Pair]) -> tuple[Rule, dict[str, Any], int] | None:
    added = _added_colors(train)
    if len(added) != 1:
        return None
    frame = next(iter(added))

    def rule(source: Grid) -> Grid:
        background = _mode(source)
        tile = _r270(source)
        width = len(tile[0])
        border = (background,) + (frame,) * width + (background,)
        framed_rows = tuple((frame,) + row + (frame,) for row in tile)
        return (border,) + framed_rows + (border,) + framed_rows + (border,)

    return rule, {"operator": "rotate270_frame_repeat", "repeat": 2, "frame": frame}, 8


def _framed_motif_duplicate(train: Sequence[Pair]) -> tuple[Rule, dict[str, Any], int] | None:
    target_shapes = {_shape(target) for _, target in train}
    if target_shapes != {(15, 15)}:
        return None

    def rule(source: Grid) -> Grid | None:
        height, width = _shape(source)
        if height < 5 or width < 5:
            return None
        corners = {source[0][0], source[0][-1], source[-1][0], source[-1][-1]}
        if len(corners) != 1:
            return None
        background = next(iter(corners))
        top_edge = [cell for cell in source[0][1:-1] if cell != background]
        if not top_edge or len(set(top_edge)) != 1:
            return None
        frame = top_edge[0]
        markers = [
            (row, column)
            for row in range(1, height - 1)
            for column in range(1, width - 1)
            if source[row][column] != background
        ]
        if not markers:
            return None
        min_row, max_row = min(r for r, _ in markers), max(r for r, _ in markers)
        min_column, max_column = min(c for _, c in markers), max(c for _, c in markers)
        if max_row - min_row >= 3 or max_column - min_column >= 3:
            return None
        center_row = (min_row + max_row) // 2
        center_column = (min_column + max_column) // 2
        start_row = min(max(center_row - 1, 1), height - 4)
        start_column = min(max(center_column - 1, 1), width - 4)
        inner = tuple(tuple(row[start_column : start_column + 3]) for row in source[start_row : start_row + 3])
        motif_rows = _matrix(5, 5, background)
        for index in range(1, 4):
            motif_rows[0][index] = frame
            motif_rows[4][index] = frame
            motif_rows[index][0] = frame
            motif_rows[index][4] = frame
        for row in range(3):
            motif_rows[row + 1][1:4] = inner[row]
        motif = _freeze(motif_rows)
        output = _matrix(15, 15, background)
        for top, left in ((2, 2), (8, 8)):
            for row, values in enumerate(motif):
                output[top + row][left : left + 5] = values
        return _freeze(output)

    return rule, {"operator": "extract_inner3_reframe_duplicate", "motif_side": 5, "canvas_side": 15, "placements": [[2, 2], [8, 8]]}, 13


def _scaled_object_diagonals(train: Sequence[Pair]) -> tuple[Rule, dict[str, Any], int] | None:
    added = _added_colors(train)
    if len(added) != 1:
        return None
    accent = next(iter(added))

    def rule(source: Grid) -> Grid | None:
        height, width = _shape(source)
        background = source[0][0]
        factor = len(_palette(source) - {background})
        if factor < 2:
            return None
        components: list[tuple[int, int, int]] = []
        for color in _palette(source) - {background}:
            points = [(r, c) for r in range(height) for c in range(width) if source[r][c] == color]
            if len(points) == 4:
                rows = {r for r, _ in points}
                columns = {c for _, c in points}
                if len(rows) == 2 and len(columns) == 2 and len(points) == len(rows) * len(columns):
                    components.append((color, min(rows), min(columns)))
        if len(components) != 1:
            return None
        _, object_row, object_column = components[0]
        output = _matrix(height * factor, width * factor, background)
        for row in range(height):
            for column in range(width):
                color = source[row][column]
                for rr in range(row * factor, (row + 1) * factor):
                    for cc in range(column * factor, (column + 1) * factor):
                        output[rr][cc] = color
        top, left = object_row * factor, object_column * factor
        bottom, right = (object_row + 2) * factor - 1, (object_column + 2) * factor - 1
        for start_row, start_column, dr, dc in (
            (top, left, -1, -1),
            (top, right, -1, 1),
            (bottom, left, 1, -1),
            (bottom, right, 1, 1),
        ):
            row, column = start_row + dr, start_column + dc
            while 0 <= row < len(output) and 0 <= column < len(output[0]):
                if output[row][column] != background:
                    break
                output[row][column] = accent
                row += dr
                column += dc
        return _freeze(output)

    return rule, {"operator": "palette_rank_scale_with_object_diagonals", "factor": "nonbackground_palette_size", "accent": accent}, 12


def _translation_period(source: Grid, background: int) -> tuple[int, int] | None:
    height, width = _shape(source)
    ranked: list[tuple[int, int, int]] = []
    for period in range(1, min(height, width)):
        for sign in (-1, 1):
            matches = 0
            conflicts = 0
            for row in range(height - period):
                for column in range(width):
                    other_column = column + sign * period
                    if not 0 <= other_column < width:
                        continue
                    first, second = source[row][column], source[row + period][other_column]
                    if first == second and first != background:
                        matches += 1
                    elif first != background and second != background:
                        conflicts += 1
            if matches >= 2 and conflicts == 0:
                ranked.append((-matches, period, sign))
    if not ranked:
        return None
    _, period, sign = min(ranked)
    return period, sign


def _diagonal_translation(train: Sequence[Pair]) -> tuple[Rule, dict[str, Any], int] | None:
    def rule(source: Grid) -> Grid | None:
        height, width = _shape(source)
        if height != width:
            return None
        background = _mode(source)
        parameters = _translation_period(source, background)
        if parameters is None:
            return None
        period, sign = parameters
        side = 2 * height
        output = _matrix(side, side, background)
        column_offset = 0 if sign > 0 else width
        for step in range(-2 * side, 2 * side + 1):
            row_offset = step * period
            shift = step * sign * period
            for row, values in enumerate(source):
                for column, cell in enumerate(values):
                    if cell == background:
                        continue
                    rr = row + row_offset
                    cc = column + column_offset + shift
                    if 0 <= rr < side and 0 <= cc < side:
                        old = output[rr][cc]
                        if old != background and old != cell:
                            return None
                        output[rr][cc] = cell
        return _freeze(output)

    return rule, {"operator": "diagonal_translation_closure", "period": "maximum_consistent_overlap", "factor": 2}, 11


def compile_task(task: Any, limits: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    """Compile bounded exact-replay construction candidates for one task."""

    bounds = Limits.from_value(limits)
    try:
        train, tests = _read_task(task, bounds)
    except _Undefined:
        return []

    hypotheses: list[tuple[str, Rule, dict[str, Any], int]] = []

    def add(name: str, proposal: tuple[Rule, dict[str, Any], int] | None) -> None:
        if proposal is not None:
            hypotheses.append((name, proposal[0], proposal[1], proposal[2]))

    add("offset_panel_stack", _offset_stack(train))
    add("edge_frame_construction", _edge_duplicate_frame(train))
    add("frequency_histogram", _histogram_columns(train))
    add("growing_bar", _growing_prefix(train))
    add("slanted_canvas", _slanted_rows(train))
    add("reflection_extension", _vertical_reflection(train))
    add("sliding_row_construction", _diagonal_slide(train))
    add("seeded_ray_lattice", _seeded_ray_lattice(train))
    add("encoded_path", _encoded_path(train))
    add("max_index_extension", _max_index_table(train))
    add("shell_dynamics", _shell_extension(train))
    add("nested_quadrant_rings", _nested_quadrant_rings(train))
    add("chebyshev_ring_cursor", _chebyshev_ring_cursor(train))
    add("fixed_lattice", _uniform_lattice(train))
    add("column_fill_tiling", _filled_columns_tile(train))
    for stencil_rule, stencil_program, stencil_complexity in _stencil_rules(train):
        hypotheses.append(("local_stencil_tiling", stencil_rule, stencil_program, stencil_complexity))
    add("row_diagonal_ray_tiling", _row_diagonal_ray_tile(train))
    add("triangle_outline_growth", _triangle_outline_growth(train))
    add("rotational_orbit_layout", _four_way_orbit(train))
    add("glyph_bar_layout", _glyph_bar_layout(train))
    add("dual_rectangle_layout", _dual_rectangle_layout(train))
    add("panel_kronecker_product", _panel_kronecker(train))
    add("separator_mask_product", _panel_mask_product(train))
    add("boundary_motif_blocks", _boundary_motif_blocks(train))
    add("marker_square_chain", _marker_square_chain(train))
    add("framed_rotation_repeat", _framed_repeat(train))
    add("framed_motif_duplicate", _framed_motif_duplicate(train))
    add("scaled_object_diagonals", _scaled_object_diagonals(train))
    add("diagonal_translation", _diagonal_translation(train))

    candidates: list[dict[str, Any]] = []
    for family, rule, program, complexity in hypotheses:
        candidate = _candidate(family, program, complexity, rule, train, tests, bounds)
        if candidate is not None:
            candidates.append(candidate)
    candidates.sort(key=lambda item: (item["complexity"], item["family"], _canonical(item["program"])))
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for candidate in candidates:
        behavior = candidate["evidence"]["behavior_hash"]
        if behavior in seen:
            continue
        seen.add(behavior)
        unique.append(candidate)
    return unique[: bounds.max_candidates]


__all__ = ["compile_task"]
