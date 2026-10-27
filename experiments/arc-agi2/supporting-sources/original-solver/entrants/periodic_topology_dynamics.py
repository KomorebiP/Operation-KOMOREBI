"""Bounded periodic and topological dynamics synthesis for Block 14.

The entrant compiles small executable programs from demonstrations and test
inputs only.  It deliberately targets mechanisms whose description is stable
under changes of canvas size and object placement: periodic residue repair,
phase continuation from a compact legend, parity fields, line/backbone
propagation, rectangular and concentric frames, and conservative topology
fills.  Programs are JSON-safe and replayed independently by
``replay_program``.

No task identifier, corpus fingerprint, test target, solution, or score is
observed by compilation or replay.

Author: Komorebi P.
"""

from __future__ import annotations

from collections import Counter, defaultdict, deque
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
from typing import Any, Callable, Iterable


Grid = tuple[tuple[int, ...], ...]
Cell = tuple[int, int]
Pair = tuple[Grid, Grid]
SCHEMA = "komorebi.pr_lasm.block14.periodic_topology_dynamics.v1"
AUTHOR = "Komorebi P."


class Undefined(ValueError):
    """The program has no unique meaning on a supplied grid."""


@dataclass(frozen=True, slots=True)
class Limits:
    max_side: int = 30
    max_examples: int = 16
    max_hypotheses: int = 384
    max_period: int = 6
    max_rectangle_checks: int = 250_000
    max_counterfactuals: int = 48
    ambiguity_slack: int = 0
    max_candidates: int = 1

    @classmethod
    def from_value(cls, value: Mapping[str, Any] | None) -> "Limits":
        if value is None:
            return cls()
        if not isinstance(value, Mapping):
            raise TypeError("limits must be a mapping")
        defaults = cls()
        fields: dict[str, int] = {}
        for name in cls.__dataclass_fields__:
            raw = value.get(name, getattr(defaults, name))
            if isinstance(raw, bool) or not isinstance(raw, int):
                raise TypeError(f"limits.{name} must be an integer")
            fields[name] = raw
        result = cls(**fields)
        for name in cls.__dataclass_fields__:
            minimum = 0 if name == "ambiguity_slack" else 1
            if getattr(result, name) < minimum:
                raise ValueError(f"limits.{name} is below {minimum}")
        return result


@dataclass(frozen=True, slots=True)
class Proposal:
    family: str
    program: Mapping[str, Any]
    complexity: int
    invariant: str


def _canonical(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def _grid(value: Any, limits: Limits | None = None) -> Grid:
    bounds = limits or Limits()
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise TypeError("grid must be a sequence")
    if not value or len(value) > bounds.max_side:
        raise ValueError("invalid grid height")
    rows: list[tuple[int, ...]] = []
    width: int | None = None
    for raw_row in value:
        if not isinstance(raw_row, Sequence) or isinstance(
            raw_row, (str, bytes, bytearray)
        ):
            raise TypeError("grid row must be a sequence")
        if not raw_row or len(raw_row) > bounds.max_side:
            raise ValueError("invalid grid width")
        row: list[int] = []
        for cell in raw_row:
            if isinstance(cell, bool) or not isinstance(cell, int) or not 0 <= cell <= 9:
                raise ValueError("invalid ARC color")
            row.append(int(cell))
        if width is None:
            width = len(row)
        elif len(row) != width:
            raise ValueError("grid is not rectangular")
        rows.append(tuple(row))
    return tuple(rows)


def _plain(value: Grid) -> list[list[int]]:
    return [list(row) for row in value]


def _shape(value: Grid) -> tuple[int, int]:
    return len(value), len(value[0])


def _mode(values: Iterable[int]) -> int:
    counts = Counter(values)
    if not counts:
        raise Undefined("empty mode")
    maximum = max(counts.values())
    return min(color for color, count in counts.items() if count == maximum)


def _border_mode(value: Grid) -> int:
    height, width = _shape(value)
    cells = list(value[0])
    if height > 1:
        cells.extend(value[-1])
    if height > 2:
        cells.extend(value[row][0] for row in range(1, height - 1))
        if width > 1:
            cells.extend(value[row][-1] for row in range(1, height - 1))
    return _mode(cells)


def _changed_pairs(train: Sequence[Pair]) -> tuple[tuple[int, int], ...]:
    pairs = {
        (before, after)
        for source, target in train
        for source_row, target_row in zip(source, target)
        for before, after in zip(source_row, target_row)
        if before != after
    }
    return tuple(sorted(pairs))


def _changed_cells(source: Grid, target: Grid) -> frozenset[Cell]:
    return frozenset(
        (row, column)
        for row in range(len(source))
        for column in range(len(source[0]))
        if source[row][column] != target[row][column]
    )


def _components(value: Grid, color: int, connectivity: int = 4) -> tuple[frozenset[Cell], ...]:
    height, width = _shape(value)
    unseen = {
        (row, column)
        for row in range(height)
        for column in range(width)
        if value[row][column] == color
    }
    if connectivity == 4:
        offsets = ((-1, 0), (1, 0), (0, -1), (0, 1))
    elif connectivity == 8:
        offsets = tuple(
            (dr, dc)
            for dr in (-1, 0, 1)
            for dc in (-1, 0, 1)
            if dr or dc
        )
    else:
        raise Undefined("invalid connectivity")
    result: list[frozenset[Cell]] = []
    while unseen:
        root = min(unseen)
        unseen.remove(root)
        queue = deque([root])
        cells = {root}
        while queue:
            row, column = queue.popleft()
            for dr, dc in offsets:
                other = row + dr, column + dc
                if other in unseen:
                    unseen.remove(other)
                    cells.add(other)
                    queue.append(other)
        result.append(frozenset(cells))
    return tuple(sorted(result, key=lambda cells: (min(cells), len(cells))))


def _bbox(cells: Iterable[Cell]) -> tuple[int, int, int, int]:
    points = tuple(cells)
    if not points:
        raise Undefined("empty bounding box")
    return (
        min(row for row, _ in points),
        max(row for row, _ in points),
        min(column for _, column in points),
        max(column for _, column in points),
    )


def _perimeter(box: tuple[int, int, int, int]) -> frozenset[Cell]:
    top, bottom, left, right = box
    return frozenset(
        (row, column)
        for row in range(top, bottom + 1)
        for column in range(left, right + 1)
        if row in (top, bottom) or column in (left, right)
    )


def _filled_rectangle(cells: frozenset[Cell]) -> bool:
    top, bottom, left, right = _bbox(cells)
    return len(cells) == (bottom - top + 1) * (right - left + 1)


def _rectangular_perimeter(cells: frozenset[Cell]) -> bool:
    if not cells:
        return False
    top, bottom, left, right = _bbox(cells)
    return bottom - top >= 2 and right - left >= 2 and cells == _perimeter(
        (top, bottom, left, right)
    )


def _uniform_rectangles(value: Grid, color: int) -> tuple[tuple[int, int, int, int], ...]:
    """Enumerate maximal-width, at-least-2x2 uniform rectangles.

    A maximum-area rectangle always appears in this reduced enumeration, so
    there is no reason to materialize every contained subrectangle.
    """

    height, width = _shape(value)
    result: list[tuple[int, int, int, int]] = []
    for top in range(height):
        valid = [True] * width
        for bottom in range(top, height):
            valid = [
                old and value[bottom][column] == color
                for column, old in enumerate(valid)
            ]
            if bottom == top:
                continue
            column = 0
            while column < width:
                if not valid[column]:
                    column += 1
                    continue
                left = column
                while column < width and valid[column]:
                    column += 1
                right = column - 1
                if right > left:
                    result.append((top, bottom, left, right))
    return tuple(result)


def _all_uniform_squares(value: Grid, color: int) -> tuple[tuple[int, int, int], ...]:
    height, width = _shape(value)
    integral = [[0] * (width + 1) for _ in range(height + 1)]
    for row in range(height):
        for column in range(width):
            integral[row + 1][column + 1] = (
                integral[row][column + 1]
                + integral[row + 1][column]
                - integral[row][column]
                + int(value[row][column] == color)
            )
    result: list[tuple[int, int, int]] = []
    for size in range(2, min(height, width) + 1):
        area = size * size
        for top in range(height - size + 1):
            for left in range(width - size + 1):
                count = (
                    integral[top + size][left + size]
                    - integral[top][left + size]
                    - integral[top + size][left]
                    + integral[top][left]
                )
                if count == area:
                    result.append((size, top, left))
    return tuple(result)


def _largest_rectangle_interior(value: Grid, program: Mapping[str, Any]) -> Grid:
    source, paint = int(program["source"]), int(program["paint"])
    rectangles = _uniform_rectangles(value, source)
    if not rectangles:
        raise Undefined("no two-dimensional uniform rectangle")
    maximum = max(
        (bottom - top + 1) * (right - left + 1)
        for top, bottom, left, right in rectangles
    )
    winners = tuple(
        rectangle
        for rectangle in rectangles
        if (rectangle[1] - rectangle[0] + 1)
        * (rectangle[3] - rectangle[2] + 1)
        == maximum
    )
    if len(winners) != 1:
        raise Undefined("largest uniform rectangle is tied")
    top, bottom, left, right = winners[0]
    if bottom - top < 2 or right - left < 2:
        raise Undefined("rectangle has no strict interior")
    output = [list(row) for row in value]
    changed = False
    for row in range(top + 1, bottom):
        for column in range(left + 1, right):
            changed |= output[row][column] != paint
            output[row][column] = paint
    if not changed:
        raise Undefined("rectangle interior already painted")
    return tuple(tuple(row) for row in output)


def _disjoint_squares(value: Grid, program: Mapping[str, Any]) -> Grid:
    source, paint = int(program["source"]), int(program["paint"])
    scope = str(program["scope"])
    squares = list(_all_uniform_squares(value, source))
    if not squares:
        raise Undefined("no uniform square")
    if scope == "globally_largest":
        maximum = max(size for size, _, _ in squares)
        squares = [item for item in squares if item[0] == maximum]
    elif scope != "all_sizes":
        raise Undefined("invalid square scope")
    used: set[Cell] = set()
    selected = 0
    for size, top, left in sorted(squares, key=lambda item: (-item[0], item[1], item[2])):
        cells = {
            (row, column)
            for row in range(top, top + size)
            for column in range(left, left + size)
        }
        if cells & used:
            continue
        used.update(cells)
        selected += 1
    if not selected:
        raise Undefined("no disjoint square selected")
    output = [list(row) for row in value]
    for row, column in used:
        output[row][column] = paint
    return tuple(tuple(row) for row in output)


def _clustered_bbox_completion(value: Grid, program: Mapping[str, Any]) -> Grid:
    source = int(program["source"])
    paint = int(program["paint"])
    object_color = int(program["object_color"])
    components = _components(value, object_color, 4)
    bodies = [set(cells) for cells in components if len(cells) > 1]
    markers = [next(iter(cells)) for cells in components if len(cells) == 1]
    if not bodies or not markers:
        raise Undefined("body-plus-marker topology is absent")
    for marker in markers:
        distances = [
            Fraction(
                (marker[0] * len(body) - sum(row for row, _ in body)) ** 2
                + (marker[1] * len(body) - sum(column for _, column in body)) ** 2,
                len(body) ** 2,
            )
            for body in bodies
        ]
        minimum = min(distances)
        if distances.count(minimum) != 1:
            raise Undefined("singleton attachment is ambiguous")
        bodies[distances.index(minimum)].add(marker)
    output = [list(row) for row in value]
    changed = False
    for body in bodies:
        top, bottom, left, right = _bbox(body)
        for row in range(top, bottom + 1):
            for column in range(left, right + 1):
                if value[row][column] == source:
                    changed |= output[row][column] != paint
                    output[row][column] = paint
    if not changed:
        raise Undefined("bounding boxes need no completion")
    return tuple(tuple(row) for row in output)


def _axis_backbone(value: Grid, program: Mapping[str, Any]) -> Grid:
    background, paint = int(program["source"]), int(program["paint"])
    height, width = _shape(value)
    points = [
        (row, column)
        for row in range(height)
        for column in range(width)
        if value[row][column] != background
    ]
    if not points or len({value[row][column] for row, column in points}) != 1:
        raise Undefined("backbone requires one marker color")
    rows: dict[int, list[int]] = defaultdict(list)
    columns: dict[int, list[int]] = defaultdict(list)
    for row, column in points:
        rows[row].append(column)
        columns[column].append(row)
    lines = [
        ("horizontal", row, min(values), max(values), len(values))
        for row, values in rows.items()
        if len(values) >= 2
    ]
    lines.extend(
        ("vertical", column, min(values), max(values), len(values))
        for column, values in columns.items()
        if len(values) >= 2
    )
    if not lines:
        raise Undefined("no repeated marker coordinate")
    maximum = max(line[4] for line in lines)
    lines = [line for line in lines if line[4] == maximum]
    if len(lines) != 1:
        raise Undefined("backbone axis is tied")
    axis, fixed, start, stop, _ = lines[0]
    output = [list(row) for row in value]
    if axis == "horizontal":
        for column in range(start, stop + 1):
            if output[fixed][column] == background:
                output[fixed][column] = paint
        for row, column in points:
            if row == fixed:
                continue
            if not start <= column <= stop:
                raise Undefined("branch falls outside backbone")
            for other_row in range(min(row, fixed) + 1, max(row, fixed)):
                if output[other_row][column] != background:
                    raise Undefined("branch is obstructed")
                output[other_row][column] = paint
    else:
        for row in range(start, stop + 1):
            if output[row][fixed] == background:
                output[row][fixed] = paint
        for row, column in points:
            if column == fixed:
                continue
            if not start <= row <= stop:
                raise Undefined("branch falls outside backbone")
            for other_column in range(min(column, fixed) + 1, max(column, fixed)):
                if output[row][other_column] != background:
                    raise Undefined("branch is obstructed")
                output[row][other_column] = paint
    return tuple(tuple(row) for row in output)


def _complete_frames(value: Grid) -> tuple[tuple[int, int, int, int, int], ...]:
    height, width = _shape(value)
    result: list[tuple[int, int, int, int, int]] = []
    checks = 0
    for top in range(height - 2):
        for bottom in range(top + 2, height):
            for left in range(width - 2):
                for right in range(left + 2, width):
                    checks += 1
                    if checks > 250_000:
                        raise Undefined("rectangle bound exhausted")
                    color = value[top][left]
                    if all(
                        value[row][column] == color
                        for row, column in _perimeter((top, bottom, left, right))
                    ):
                        result.append((top, bottom, left, right, color))
    return tuple(result)


def _zero_interior_frames(value: Grid) -> tuple[tuple[int, int, int, int, int], ...]:
    return tuple(
        (top, bottom, left, right, color)
        for top, bottom, left, right, color in _complete_frames(value)
        if color != 0
        and all(
            value[row][column] == 0
            for row in range(top + 1, bottom)
            for column in range(left + 1, right)
        )
    )


def _unique_largest_frame(value: Grid) -> tuple[int, int, int, int, int]:
    frames = _zero_interior_frames(value)
    if not frames:
        raise Undefined("no hollow nonzero frame")
    maximum = max(
        (bottom - top + 1) * (right - left + 1)
        for top, bottom, left, right, _ in frames
    )
    winners = [
        frame
        for frame in frames
        if (frame[1] - frame[0] + 1) * (frame[3] - frame[2] + 1) == maximum
    ]
    if len(winners) != 1:
        raise Undefined("largest frame is tied")
    return winners[0]


def _clone_frame(value: Grid, _program: Mapping[str, Any]) -> Grid:
    top, bottom, left, right, color = _unique_largest_frame(value)
    height, width = _shape(value)
    inner_height, inner_width = bottom - top - 1, right - left - 1
    locations: list[tuple[int, int, int, int]] = []
    for inner_top in range(1, height - inner_height):
        for inner_left in range(1, width - inner_width):
            if all(
                value[row][column] == 0
                for row in range(inner_top, inner_top + inner_height)
                for column in range(inner_left, inner_left + inner_width)
            ):
                locations.append(
                    (
                        inner_top - 1,
                        inner_top + inner_height,
                        inner_left - 1,
                        inner_left + inner_width,
                    )
                )
    targets = [location for location in locations if location != (top, bottom, left, right)]
    if len(targets) != 1:
        raise Undefined("matching blank frame interior is not unique")
    output = [list(row) for row in value]
    for row, column in _perimeter(targets[0]):
        output[row][column] = color
    return tuple(tuple(row) for row in output)


def _concentric_clue_frame(value: Grid, _program: Mapping[str, Any]) -> Grid:
    top, bottom, left, right, frame_color = _unique_largest_frame(value)
    height, width = _shape(value)
    clues: list[list[int]] = []
    for corner_row, corner_column, dr, dc in (
        (top, left, -1, -1),
        (top, right, -1, 1),
        (bottom, left, 1, -1),
        (bottom, right, 1, 1),
    ):
        values: list[int] = []
        row, column = corner_row + dr, corner_column + dc
        while 0 <= row < height and 0 <= column < width:
            values.append(value[row][column])
            row += dr
            column += dc
        if len(values) >= 2 and all(color not in (0, frame_color) for color in values):
            clues.append(list(reversed(values)))
    if len(clues) != 1:
        raise Undefined("corner clue ray is absent or tied")
    colors = clues[0]
    maximum_layers = (min(bottom - top - 1, right - left - 1) + 1) // 2
    if len(colors) > maximum_layers:
        raise Undefined("too many clue colors for frame")
    output = [list(row) for row in value]
    for row in range(top + 1, bottom):
        for column in range(left + 1, right):
            layer = min(
                row - top - 1,
                bottom - row - 1,
                column - left - 1,
                right - column - 1,
            )
            output[row][column] = colors[min(layer, len(colors) - 1)]
    return tuple(tuple(row) for row in output)


def _nonbackground_components(value: Grid, background: int) -> tuple[frozenset[Cell], ...]:
    height, width = _shape(value)
    unseen = {
        (row, column)
        for row in range(height)
        for column in range(width)
        if value[row][column] != background
    }
    result: list[frozenset[Cell]] = []
    while unseen:
        root = min(unseen)
        unseen.remove(root)
        queue = deque([root])
        cells = {root}
        while queue:
            row, column = queue.popleft()
            for other in ((row - 1, column), (row + 1, column), (row, column - 1), (row, column + 1)):
                if other in unseen:
                    unseen.remove(other)
                    cells.add(other)
                    queue.append(other)
        result.append(frozenset(cells))
    return tuple(sorted(result, key=lambda cells: min(cells)))


def _transform_patch(patch: Grid, operation: str) -> Grid:
    if operation == "identity":
        return patch
    if operation == "flip_columns":
        return tuple(tuple(reversed(row)) for row in patch)
    if operation == "flip_rows":
        return tuple(reversed(patch))
    if operation == "rotate_180":
        return tuple(tuple(reversed(row)) for row in reversed(patch))
    if operation == "transpose":
        return tuple(tuple(patch[row][column] for row in range(len(patch))) for column in range(len(patch[0])))
    raise Undefined("unknown patch transform")


def _template_to_uniform_rectangle(value: Grid, program: Mapping[str, Any]) -> Grid:
    background = _border_mode(value)
    components = _nonbackground_components(value, background)
    rectangles: list[tuple[frozenset[Cell], tuple[int, int, int, int], frozenset[int]]] = []
    for cells in components:
        if not _filled_rectangle(cells):
            continue
        box = _bbox(cells)
        if box[1] == box[0] or box[3] == box[2]:
            continue
        colors = frozenset(value[row][column] for row, column in cells)
        rectangles.append((cells, box, colors))
    matches: list[
        tuple[tuple[int, int, int, int], tuple[int, int, int, int]]
    ] = []
    for _, blank_box, blank_colors in rectangles:
        if len(blank_colors) != 1:
            continue
        blank_color = next(iter(blank_colors))
        blank_shape = blank_box[1] - blank_box[0] + 1, blank_box[3] - blank_box[2] + 1
        peers = [
            template_box
            for _, template_box, template_colors in rectangles
            if template_box != blank_box
            and len(template_colors) >= 2
            and blank_color not in template_colors
            and (
                template_box[1] - template_box[0] + 1,
                template_box[3] - template_box[2] + 1,
            )
            == blank_shape
        ]
        if len(peers) == 1:
            matches.append((blank_box, peers[0]))
    if len(matches) != 1:
        raise Undefined("template/blank rectangle pairing is not unique")
    blank_box, template_box = matches[0]
    patch = tuple(
        tuple(value[row][column] for column in range(template_box[2], template_box[3] + 1))
        for row in range(template_box[0], template_box[1] + 1)
    )
    patch = _transform_patch(patch, str(program["patch_transform"]))
    blank_height = blank_box[1] - blank_box[0] + 1
    blank_width = blank_box[3] - blank_box[2] + 1
    if _shape(patch) != (blank_height, blank_width):
        raise Undefined("transformed patch does not fit blank")
    output = [list(row) for row in value]
    for row in range(blank_height):
        for column in range(blank_width):
            output[blank_box[0] + row][blank_box[2] + column] = patch[row][column]
    return tuple(tuple(row) for row in output)


def _d4(value: Grid, operation: str) -> Grid:
    if operation == "identity":
        return value
    if operation == "rot90":
        height, width = _shape(value)
        return tuple(
            tuple(value[height - 1 - row][column] for row in range(height))
            for column in range(width)
        )
    if operation == "rot180":
        return _d4(_d4(value, "rot90"), "rot90")
    if operation == "rot270":
        return _d4(_d4(value, "rot180"), "rot90")
    if operation == "flip_h":
        return tuple(tuple(reversed(row)) for row in value)
    if operation == "flip_v":
        return tuple(reversed(value))
    if operation == "transpose":
        return tuple(
            tuple(value[row][column] for row in range(len(value)))
            for column in range(len(value[0]))
        )
    if operation == "anti_transpose":
        return _d4(_d4(value, "rot180"), "transpose")
    raise Undefined("unknown D4 operation")


_D4_OPERATIONS = (
    "identity",
    "rot90",
    "rot180",
    "rot270",
    "flip_h",
    "flip_v",
    "transpose",
    "anti_transpose",
)
_D4_INVERSE = {
    "identity": "identity",
    "rot90": "rot270",
    "rot180": "rot180",
    "rot270": "rot90",
    "flip_h": "flip_h",
    "flip_v": "flip_v",
    "transpose": "transpose",
    "anti_transpose": "anti_transpose",
}


def _oriented(value: Grid, canonical: Callable[[Grid], Grid]) -> Grid:
    outputs: dict[str, Grid] = {}
    for operation in _D4_OPERATIONS:
        transformed = _d4(value, operation)
        try:
            result = canonical(transformed)
        except Undefined:
            continue
        restored = _d4(result, _D4_INVERSE[operation])
        outputs.setdefault(_canonical(_plain(restored)), restored)
    if len(outputs) != 1:
        raise Undefined("orientation is absent or behaviorally ambiguous")
    return next(iter(outputs.values()))


def _edge_xor_canonical(value: Grid) -> Grid:
    background = _border_mode(value)
    height, width = _shape(value)
    markers = [(column, value[0][column]) for column in range(width) if value[0][column] != background]
    if len(markers) < 2:
        raise Undefined("top-edge marker legend is too short")
    for column, _ in markers:
        if column in (0, width - 1):
            raise Undefined("edge marker touches a corner")
        if value[0][column - 1] != background or value[0][column + 1] != background:
            raise Undefined("edge marker is not isolated")
    if any(value[-1][column] != background for column in range(width)):
        raise Undefined("opposite edge is not blank")
    output = [list(row) for row in value]
    for column, marker in markers:
        for row in range(height):
            output[row][column] = (
                background if row > 0 and value[row][column] == marker else marker
            )
    return tuple(tuple(row) for row in output)


def _edge_xor_projection(value: Grid, _program: Mapping[str, Any]) -> Grid:
    return _oriented(value, _edge_xor_canonical)


def _periodic_legend_canonical(value: Grid) -> Grid:
    background = _mode(cell for row in value for cell in row)
    height, width = _shape(value)
    legend: list[tuple[int, int]] = []
    for column in range(width - 1, -1, -1):
        colors = {value[row][column] for row in range(height)}
        if len(colors) == 1 and next(iter(colors)) != background:
            legend.append((column, next(iter(colors))))
        else:
            break
    legend.reverse()
    if len(legend) < 2 or legend[0][0] < 2:
        raise Undefined("right-edge periodic legend is absent")
    marker_color = value[0][0]
    if marker_color == background:
        raise Undefined("phase-length marker is absent")
    run_length = 0
    while run_length < height and value[run_length][0] == marker_color:
        run_length += 1
    if any(value[row][0] != background for row in range(run_length, height)):
        raise Undefined("phase marker column has extra foreground")
    target_column = legend[0][0] - 1
    if any(value[row][target_column] != background for row in range(height)):
        raise Undefined("periodic render column is occupied")
    palette = [color for _, color in legend]
    output = [list(row) for row in value]
    for row in range(height):
        output[row][target_column] = palette[(row // run_length) % len(palette)]
    for column, _ in legend:
        for row in range(height):
            output[row][column] = background
    return tuple(tuple(row) for row in output)


def _periodic_legend_phase(value: Grid, _program: Mapping[str, Any]) -> Grid:
    return _oriented(value, _periodic_legend_canonical)


def _periodic_residue_repair(value: Grid, program: Mapping[str, Any]) -> Grid:
    source = int(program["source"])
    row_period = int(program["row_period"])
    column_period = int(program["column_period"])
    policy = str(program["policy"])
    height, width = _shape(value)
    if not (1 <= row_period <= 6 and 1 <= column_period <= 6):
        raise Undefined("period outside grammar")
    groups: list[list[list[int]]] = [
        [[] for _ in range(column_period)] for _ in range(row_period)
    ]
    for row in range(height):
        for column in range(width):
            groups[row % row_period][column % column_period].append(value[row][column])
    template: list[list[int]] = []
    for row in range(row_period):
        template_row: list[int] = []
        for column in range(column_period):
            visible = [color for color in groups[row][column] if color != source]
            if not visible:
                template_row.append(source)
            elif policy == "unique_non_source":
                if len(set(visible)) != 1:
                    raise Undefined("residue has conflicting observations")
                template_row.append(visible[0])
            elif policy == "non_source_mode":
                template_row.append(_mode(visible))
            else:
                raise Undefined("unknown periodic repair policy")
        template.append(template_row)
    output = [list(row) for row in value]
    changed = False
    for row in range(height):
        for column in range(width):
            expected = template[row % row_period][column % column_period]
            if value[row][column] == source and expected != source:
                output[row][column] = expected
                changed = True
    if not changed:
        raise Undefined("periodic repair makes no change")
    return tuple(tuple(row) for row in output)


def _parity_wave(value: Grid, program: Mapping[str, Any]) -> Grid:
    source, paint = int(program["source"]), int(program["paint"])
    seed_color = int(program["seed_color"])
    metric = str(program["metric"])
    modulus, residue = int(program["modulus"]), int(program["residue"])
    height, width = _shape(value)
    seeds = [
        (row, column)
        for row in range(height)
        for column in range(width)
        if value[row][column] == seed_color
    ]
    if not seeds or not (2 <= modulus <= 4 and 0 <= residue < modulus):
        raise Undefined("invalid wave definition")
    output = [list(row) for row in value]
    changed = False
    for row in range(height):
        for column in range(width):
            if value[row][column] != source:
                continue
            if metric == "manhattan":
                distance = min(abs(row - rr) + abs(column - cc) for rr, cc in seeds)
            elif metric == "chebyshev":
                distance = min(max(abs(row - rr), abs(column - cc)) for rr, cc in seeds)
            else:
                raise Undefined("unknown wave metric")
            if distance % modulus == residue:
                output[row][column] = paint
                changed = True
    if not changed:
        raise Undefined("wave makes no change")
    return tuple(tuple(row) for row in output)


_EXECUTORS: dict[str, Callable[[Grid, Mapping[str, Any]], Grid]] = {
    "largest_uniform_rectangle_interior": _largest_rectangle_interior,
    "disjoint_uniform_squares": _disjoint_squares,
    "clustered_bbox_completion": _clustered_bbox_completion,
    "axis_backbone_network": _axis_backbone,
    "clone_frame_around_matching_interior": _clone_frame,
    "concentric_frame_from_corner_clues": _concentric_clue_frame,
    "template_to_uniform_rectangle": _template_to_uniform_rectangle,
    "edge_marker_xor_projection": _edge_xor_projection,
    "periodic_legend_phase_continuation": _periodic_legend_phase,
    "periodic_residue_repair": _periodic_residue_repair,
    "distance_parity_wave": _parity_wave,
}


def _execute(value: Grid, program: Mapping[str, Any]) -> Grid:
    if program.get("schema") != SCHEMA:
        raise Undefined("unknown schema")
    operator = str(program.get("operator"))
    executor = _EXECUTORS.get(operator)
    if executor is None:
        raise Undefined("unknown operator")
    return executor(value, program)


def replay_program(program: Mapping[str, Any], grid: Any) -> list[list[int]]:
    """Replay one serialized dynamics program on one input grid."""

    if not isinstance(program, Mapping):
        raise TypeError("program must be a mapping")
    return _plain(_execute(_grid(grid), program))


def _program(operator: str, **parameters: Any) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "operator": operator,
        "role_scope": "immutable_root_input",
        **parameters,
    }


def _all_same_shape_nonidentity(train: Sequence[Pair]) -> bool:
    return all(_shape(source) == _shape(target) and source != target for source, target in train)


def _frame_delta_gate(train: Sequence[Pair]) -> bool:
    for source, target in train:
        changed = _changed_cells(source, target)
        if not _rectangular_perimeter(changed):
            return False
        if len({target[row][column] for row, column in changed}) != 1:
            return False
    return True


def _filled_delta_gate(train: Sequence[Pair]) -> bool:
    return all(_filled_rectangle(_changed_cells(source, target)) for source, target in train)


def _axis_delta_gate(train: Sequence[Pair]) -> bool:
    for source, target in train:
        changed = _changed_cells(source, target)
        rows = {row for row, _ in changed}
        columns = {column for _, column in changed}
        if not changed or (len(rows) > 8 and len(columns) > 8):
            return False
    return True


def _exact(program: Mapping[str, Any], train: Sequence[Pair]) -> bool:
    try:
        return all(_execute(source, program) == target for source, target in train)
    except (Undefined, KeyError, TypeError, ValueError, IndexError, ZeroDivisionError):
        return False


def _enumerate_raw(train: Sequence[Pair], limits: Limits) -> tuple[Proposal, ...]:
    proposals: dict[str, Proposal] = {}

    def add(family: str, program: dict[str, Any], complexity: int, invariant: str) -> None:
        if len(proposals) >= limits.max_hypotheses:
            raise Undefined("hypothesis bound exhausted")
        key = _canonical(program)
        if key in proposals or not _exact(program, train):
            return
        proposals[key] = Proposal(family, program, complexity, invariant)

    pairs = _changed_pairs(train)
    if len(pairs) == 1:
        source, paint = pairs[0]
        add(
            "topology_fill",
            _program(
                "largest_uniform_rectangle_interior",
                source=source,
                paint=paint,
                selection="unique_maximum_area",
                margin=1,
            ),
            7,
            "d4",
        )
        for scope, cost in (("all_sizes", 8), ("globally_largest", 9)):
            add(
                "topology_fill",
                _program(
                    "disjoint_uniform_squares",
                    source=source,
                    paint=paint,
                    minimum_size=2,
                    scope=scope,
                    overlap_policy="descending_size_then_northwest_disjoint",
                ),
                cost,
                "translation",
            )
        common_colors = set.intersection(
            *(set(cell for row in source_grid for cell in row) for source_grid, _ in train)
        )
        for object_color in sorted(common_colors - {source, paint}):
            add(
                "topology_fill",
                _program(
                    "clustered_bbox_completion",
                    source=source,
                    paint=paint,
                    object_color=object_color,
                    connectivity=4,
                    singleton_attachment="unique_nearest_component_centroid",
                ),
                10,
                "d4",
            )
        add(
            "connectivity_path",
            _program(
                "axis_backbone_network",
                source=source,
                paint=paint,
                backbone="unique_axis_with_most_markers",
            ),
            8,
            "d4",
        )

        minimum_height = min(len(source_grid) for source_grid, _ in train)
        minimum_width = min(len(source_grid[0]) for source_grid, _ in train)
        for row_period in range(1, min(limits.max_period, minimum_height) + 1):
            for column_period in range(1, min(limits.max_period, minimum_width) + 1):
                for policy, extra in (("unique_non_source", 0), ("non_source_mode", 1)):
                    add(
                        "periodic_repair",
                        _program(
                            "periodic_residue_repair",
                            source=source,
                            row_period=row_period,
                            column_period=column_period,
                            policy=policy,
                        ),
                        12 + row_period + column_period + extra,
                        "d4",
                    )
        common_seed_colors = sorted(common_colors - {source})[:4]
        for seed_color in common_seed_colors:
            for metric in ("manhattan", "chebyshev"):
                for modulus in (2, 3, 4):
                    for residue in range(modulus):
                        add(
                            "parity_wave",
                            _program(
                                "distance_parity_wave",
                                source=source,
                                paint=paint,
                                seed_color=seed_color,
                                metric=metric,
                                modulus=modulus,
                                residue=residue,
                            ),
                            15 + modulus + (metric == "chebyshev"),
                            "d4",
                        )

    if _frame_delta_gate(train):
        add(
            "frame_completion",
            _program(
                "clone_frame_around_matching_interior",
                frame_role="unique_largest_nonzero_frame_with_zero_interior",
                destination_role="unique_other_matching_zero_interior",
            ),
            7,
            "d4",
        )
    if _filled_delta_gate(train):
        add(
            "concentric_ring_completion",
            _program(
                "concentric_frame_from_corner_clues",
                frame_role="unique_largest_nonzero_frame_with_zero_interior",
                clue_role="unique_outward_corner_diagonal",
                terminal_clue="fill_remaining_core",
            ),
            8,
            "d4",
        )
        for transform, extra in (
            ("identity", 0),
            ("flip_columns", 1),
            ("flip_rows", 1),
            ("rotate_180", 2),
            ("transpose", 2),
        ):
            add(
                "topological_layout",
                _program(
                    "template_to_uniform_rectangle",
                    background_role="border_mode",
                    patch_transform=transform,
                ),
                9 + extra,
                "translation",
            )
    if _axis_delta_gate(train):
        add(
            "line_propagation",
            _program(
                "edge_marker_xor_projection",
                background_role="border_mode",
                collision="matching_color_erases_otherwise_overwrite",
            ),
            7,
            "d4",
        )
    add(
        "phase_continuation",
        _program(
            "periodic_legend_phase_continuation",
            background_role="global_mode",
            phase_length_role="opposite_edge_marker_run",
            palette_role="solid_edge_stripes_inward_order",
        ),
        7,
        "d4",
    )
    return tuple(sorted(proposals.values(), key=lambda item: (item.complexity, _canonical(item.program))))


def _pad(value: Grid, color: int) -> Grid:
    width = len(value[0]) + 2
    blank = (color,) * width
    return (blank,) + tuple((color,) + row + (color,) for row in value) + (blank,)


def _counterfactual(
    proposal: Proposal,
    train: Sequence[Pair],
    limits: Limits,
) -> tuple[tuple[str, ...], int] | None:
    probes = 0
    try:
        if proposal.invariant == "d4":
            for source, target in train:
                for operation in ("flip_h", "rot90"):
                    if probes >= limits.max_counterfactuals:
                        raise Undefined("counterfactual bound exhausted")
                    transformed_source = _d4(source, operation)
                    transformed_target = _d4(target, operation)
                    if _execute(transformed_source, proposal.program) != transformed_target:
                        return None
                    probes += 1
            return ("d4_covariance",), probes
        if proposal.invariant == "translation":
            for source, target in train:
                if max(len(source), len(source[0])) >= limits.max_side:
                    return None
                if proposal.program.get("operator") == "disjoint_uniform_squares":
                    unavailable = {cell for row in source for cell in row}
                    unavailable.update(
                        int(proposal.program[name])
                        for name in ("source", "paint")
                        if name in proposal.program
                    )
                    choices = [color for color in range(10) if color not in unavailable]
                    if not choices:
                        return None
                    background = choices[0]
                else:
                    background = _border_mode(source)
                if _execute(_pad(source, background), proposal.program) != _pad(target, background):
                    return None
                probes += 1
            return ("background_padding_translation",), probes
        return None
    except (Undefined, KeyError, TypeError, ValueError, IndexError, ZeroDivisionError):
        return None


def _loo_exact(proposal: Proposal, train: Sequence[Pair], limits: Limits) -> bool:
    key = _canonical(proposal.program)
    for held_out in range(len(train)):
        retained = train[:held_out] + train[held_out + 1 :]
        if not retained:
            return False
        try:
            alternatives = _enumerate_raw(retained, limits)
        except Undefined:
            return False
        if key not in {_canonical(other.program) for other in alternatives}:
            return False
        try:
            if _execute(train[held_out][0], proposal.program) != train[held_out][1]:
                return False
        except (Undefined, KeyError, TypeError, ValueError, IndexError, ZeroDivisionError):
            return False
    return True


def _behavior_hash(outputs: Sequence[Grid]) -> str:
    return hashlib.sha256(
        _canonical([_plain(output) for output in outputs]).encode("utf-8")
    ).hexdigest()


def compile_task(task: Any, limits: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    """Compile one uniquely identified, guarded dynamics program or abstain."""

    try:
        bounds = Limits.from_value(limits)
        if not isinstance(task, Mapping):
            return []
        raw_train, raw_test = task["train"], task["test"]
        if (
            not isinstance(raw_train, Sequence)
            or isinstance(raw_train, (str, bytes, bytearray))
            or len(raw_train) < 2
            or not isinstance(raw_test, Sequence)
            or isinstance(raw_test, (str, bytes, bytearray))
            or not raw_test
            or len(raw_train) + len(raw_test) > bounds.max_examples
        ):
            return []
        train = tuple(
            (_grid(example["input"], bounds), _grid(example["output"], bounds))
            for example in raw_train
        )
        # Deliberately read exactly one key of each test record.
        tests = tuple(_grid(example["input"], bounds) for example in raw_test)
        if not _all_same_shape_nonidentity(train):
            return []
        proposals = _enumerate_raw(train, bounds)
        if not proposals:
            return []
        minimum = proposals[0].complexity
        near = [
            proposal
            for proposal in proposals
            if proposal.complexity <= minimum + bounds.ambiguity_slack
        ]
        guarded: list[
            tuple[Proposal, tuple[Grid, ...], tuple[str, ...], int]
        ] = []
        for proposal in near:
            if not _loo_exact(proposal, train, bounds):
                continue
            certificate = _counterfactual(proposal, train, bounds)
            if certificate is None:
                continue
            try:
                predictions = tuple(_execute(test, proposal.program) for test in tests)
            except (Undefined, KeyError, TypeError, ValueError, IndexError, ZeroDivisionError):
                continue
            if all(prediction == test for prediction, test in zip(predictions, tests)):
                continue
            guarded.append((proposal, predictions, certificate[0], certificate[1]))
        if not guarded:
            return []
        # A predictive capsule must be a unique serialized minimum, not merely
        # one arbitrary member of a behaviorally equivalent tie.
        minimum_guarded = min(item[0].complexity for item in guarded)
        winners = [item for item in guarded if item[0].complexity == minimum_guarded]
        if len(winners) != 1:
            return []
        proposal, predictions, invariants, probes = winners[0]
        candidate = {
            "family": proposal.family,
            "program": dict(proposal.program),
            "train_outputs": [_plain(target) for _, target in train],
            "test_outputs": [_plain(output) for output in predictions],
            "complexity": proposal.complexity,
            "evidence": {
                "author": AUTHOR,
                "all_demonstrations_exact": True,
                "leave_one_demonstration_out_exact": True,
                "demonstration_permutation_invariant": True,
                "counterfactual_families": list(invariants),
                "counterfactual_probe_count": probes,
                "minimum_serialized_program_unique": True,
                "near_mdl_programs": len(near),
                "ambiguity_abstention": True,
                "challenge_only_test_access": "input_key_only",
                "behavior_hash": _behavior_hash(predictions),
            },
        }
        return [candidate][: bounds.max_candidates]
    except (Undefined, KeyError, TypeError, ValueError, IndexError, ZeroDivisionError):
        return []


__all__ = ["Limits", "compile_task", "replay_program"]
