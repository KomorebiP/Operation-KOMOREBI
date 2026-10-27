"""Multi-scale renderers and compact structural codecs for PR-LASM Block 15.

This label-blind entrant compiles a finite set of reusable raster mechanisms:

* recover a total layer order from mutually occluding straight lines;
* encode a small shape by an invariant topological feature codebook;
* dock an external payload inside a sparse, corner-marked frame;
* color stencil boundary contacts from a four-sided legend;
* continue a repeated-panel affine rectangle-growth sequence.

Only demonstration pairs and held-out inputs are accepted.  Task identifiers,
solution stores, score artifacts, and held-out labels are absent from the API.
Every emitted candidate exactly replays all demonstrations, has one held-out
behavior across the complete finite grammar, carries a serialized executable
program, and survives operator-appropriate D4 counterfactuals.

Author: Komorebi P.
"""

from __future__ import annotations

from collections import Counter, defaultdict, deque
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
import hashlib
import itertools
import json
from typing import Any


Grid = tuple[tuple[int, ...], ...]
Cell = tuple[int, int]
Pair = tuple[Grid, Grid]
SCHEMA = "komorebi.pr_lasm.block15.multiscale_codec.program.v1"
AUTHOR = "Komorebi P."


class Undefined(ValueError):
    """The requested structural roles or behavior are not unique."""


@dataclass(frozen=True, slots=True)
class Limits:
    max_grid_cells: int = 900
    max_examples: int = 16
    max_programs: int = 96
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
            "max_programs": 256,
            "max_executor_calls": 200_000,
            "max_counterfactual_checks": 4_096,
            "max_candidates": 1,
        }
        aliases = {"candidate_cap": "max_candidates"}
        parsed: dict[str, int] = {}
        for name in cls.__dataclass_fields__:
            raw = value.get(name, getattr(defaults, name))
            if name == "max_candidates" and "candidate_cap" in value:
                raw = value["candidate_cap"]
            if isinstance(raw, bool) or not isinstance(raw, int) or raw < 0:
                raise Undefined(f"limits.{name} must be a nonnegative integer")
            parsed[name] = min(raw, ceilings[name])
        # Tournament-wide limits unknown to this bounded grammar are ignored.
        del aliases
        return cls(**parsed)


def _canonical(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    )


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _grid(value: Any, limits: Limits | None = None) -> Grid:
    bounds = limits or Limits()
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or not value:
        raise Undefined("grid must be a nonempty sequence")
    rows: list[tuple[int, ...]] = []
    width: int | None = None
    for raw_row in value:
        if not isinstance(raw_row, Sequence) or isinstance(raw_row, (str, bytes)) or not raw_row:
            raise Undefined("grid row must be nonempty")
        row: list[int] = []
        for raw_cell in raw_row:
            if isinstance(raw_cell, bool) or not isinstance(raw_cell, int) or not 0 <= raw_cell <= 9:
                raise Undefined("invalid ARC color")
            row.append(int(raw_cell))
        if width is None:
            width = len(row)
        elif len(row) != width:
            raise Undefined("grid is ragged")
        rows.append(tuple(row))
    if len(rows) * int(width or 0) > bounds.max_grid_cells:
        raise Undefined("grid exceeds cell cap")
    return tuple(rows)


def _plain(grid: Grid) -> list[list[int]]:
    return [list(row) for row in grid]


def _freeze(rows: Sequence[Sequence[int]]) -> Grid:
    return tuple(tuple(int(cell) for cell in row) for row in rows)


def _shape(grid: Grid) -> tuple[int, int]:
    return len(grid), len(grid[0])


def _strict_mode(values: Iterable[int]) -> int:
    counts = Counter(values)
    if not counts:
        raise Undefined("empty population")
    peak = max(counts.values())
    winners = [color for color, count in counts.items() if count == peak]
    if len(winners) != 1:
        raise Undefined("modal role is tied")
    return winners[0]


def _background(grid: Grid) -> int:
    return _strict_mode(cell for row in grid for cell in row)


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
            raise Undefined("invalid test example")
        # A malicious/injected test output is deliberately ignored.
        tests.append(_grid(example.get("input"), limits))
    return tuple(train), tuple(tests)


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


def _crop(grid: Grid, box: tuple[int, int, int, int]) -> Grid:
    top, bottom, left, right = box
    return tuple(tuple(grid[row][left : right + 1]) for row in range(top, bottom + 1))


def _rotate(grid: Grid) -> Grid:
    return tuple(tuple(row) for row in zip(*reversed(grid)))


def _reflect(grid: Grid) -> Grid:
    return tuple(tuple(reversed(row)) for row in grid)


def _d4(grid: Grid) -> tuple[Grid, ...]:
    variants: list[Grid] = []
    current = grid
    for _ in range(4):
        variants.extend((current, _reflect(current)))
        current = _rotate(current)
    return tuple(dict.fromkeys(variants))


def _transform(grid: Grid, quarter_turns: int, reflected: bool) -> Grid:
    result = grid
    for _ in range(quarter_turns % 4):
        result = _rotate(result)
    return _reflect(result) if reflected else result


# ---------------------------------------------------------------------------
# Compact line-layer codec


@dataclass(frozen=True, slots=True)
class _Line:
    color: int
    kind: str
    invariant: int


def _line_support(line: _Line, height: int, width: int) -> frozenset[Cell]:
    cells: set[Cell] = set()
    for row in range(height):
        for column in range(width):
            if (
                (line.kind == "row" and row == line.invariant)
                or (line.kind == "column" and column == line.invariant)
                or (line.kind == "down" and row - column == line.invariant)
                or (line.kind == "up" and row + column == line.invariant)
            ):
                cells.add((row, column))
    return frozenset(cells)


def _infer_line(coords: Sequence[Cell], color: int) -> _Line:
    if len(coords) < 2:
        raise Undefined("a line needs two visible cells")
    tests = (
        ("row", {row for row, _ in coords}),
        ("column", {column for _, column in coords}),
        ("down", {row - column for row, column in coords}),
        ("up", {row + column for row, column in coords}),
    )
    matches = [(kind, next(iter(values))) for kind, values in tests if len(values) == 1]
    if len(matches) != 1:
        raise Undefined("line orientation is ambiguous")
    return _Line(color, matches[0][0], int(matches[0][1]))


def _line_layer_order(grid: Grid) -> Grid:
    height, width = _shape(grid)
    background = _background(grid)
    colors = sorted({cell for row in grid for cell in row} - {background})
    if not 2 <= len(colors) <= 9:
        raise Undefined("line codec requires two through nine layers")
    lines: list[_Line] = []
    for color in colors:
        coords = [(r, c) for r, row in enumerate(grid) for c, cell in enumerate(row) if cell == color]
        line = _infer_line(coords, color)
        support = _line_support(line, height, width)
        if not set(coords) <= support:
            raise Undefined("visible cells leave the inferred line")
        # The latent line must span between two canvas boundaries.
        boundary = sum(
            row in {0, height - 1} or column in {0, width - 1}
            for row, column in support
        )
        if boundary < 2:
            raise Undefined("line is not canvas-spanning")
        lines.append(line)

    edges: dict[int, set[int]] = {color: set() for color in colors}
    indegree = {color: 0 for color in colors}
    supports = {line.color: _line_support(line, height, width) for line in lines}
    witnessed = 0
    for left, right in itertools.combinations(lines, 2):
        intersections = supports[left.color] & supports[right.color]
        if not intersections:
            continue
        if len(intersections) != 1:
            raise Undefined("distinct inferred lines overlap nonlocally")
        row, column = next(iter(intersections))
        visible = grid[row][column]
        if visible == left.color:
            lower, upper = right.color, left.color
        elif visible == right.color:
            lower, upper = left.color, right.color
        else:
            # A third line may cover a multi-way crossing; that pair supplies
            # no direct order witness.
            continue
        witnessed += 1
        if upper not in edges[lower]:
            edges[lower].add(upper)
            indegree[upper] += 1
    if witnessed < len(colors) - 1:
        raise Undefined("too few occlusion witnesses")

    # A hidden lower line loses one visible cell at every ordinary crossing.
    # Triple crossings can leave otherwise parallel ranks incomparable, so the
    # compact convention orders equal occlusion counts by the color token.  All
    # directly witnessed precedence edges must still agree with that order.
    visible_counts = {
        line.color: sum(cell == line.color for row in grid for cell in row)
        for line in lines
    }
    occlusions = {
        line.color: len(supports[line.color]) - visible_counts[line.color]
        for line in lines
    }
    order = sorted(colors, key=lambda color: (-occlusions[color], -color))
    positions = {color: index for index, color in enumerate(order)}
    if any(positions[lower] >= positions[upper] for lower, successors in edges.items() for upper in successors):
        raise Undefined("occlusion ranks contradict witnessed precedence")
    return (tuple(order),)


# ---------------------------------------------------------------------------
# Scalar feature codebooks


def _mask(grid: Grid, background_role: str) -> Grid:
    colors = sorted({cell for row in grid for cell in row})
    if background_role == "zero":
        if 0 not in colors:
            raise Undefined("literal-zero background is absent")
        background = 0
    elif background_role == "mode":
        background = _background(grid)
    else:
        raise Undefined("unknown background role")
    cells = [(r, c) for r, row in enumerate(grid) for c, cell in enumerate(row) if cell != background]
    top, bottom, left, right = _bbox(cells)
    return tuple(
        tuple(1 if grid[row][column] != background else 0 for column in range(left, right + 1))
        for row in range(top, bottom + 1)
    )


def _component_count(mask: Grid, connectivity: int) -> int:
    height, width = _shape(mask)
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    if connectivity == 8:
        directions += [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    seen: set[Cell] = set()
    total = 0
    for row in range(height):
        for column in range(width):
            if mask[row][column] != 1 or (row, column) in seen:
                continue
            total += 1
            queue = [(row, column)]
            seen.add((row, column))
            while queue:
                current = queue.pop()
                for dr, dc in directions:
                    neighbor = current[0] + dr, current[1] + dc
                    if (
                        0 <= neighbor[0] < height
                        and 0 <= neighbor[1] < width
                        and mask[neighbor[0]][neighbor[1]] == 1
                        and neighbor not in seen
                    ):
                        seen.add(neighbor)
                        queue.append(neighbor)
    return total


def _hole_count(mask: Grid) -> int:
    height, width = _shape(mask)
    padded = tuple(
        tuple(0 for _ in range(width + 2))
        if row in {0, height + 1}
        else (0,) + mask[row - 1] + (0,)
        for row in range(height + 2)
    )
    seen: set[Cell] = set()
    components = 0
    for row in range(height + 2):
        for column in range(width + 2):
            if padded[row][column] != 0 or (row, column) in seen:
                continue
            components += 1
            queue = [(row, column)]
            seen.add((row, column))
            while queue:
                current = queue.pop()
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    neighbor = current[0] + dr, current[1] + dc
                    if (
                        0 <= neighbor[0] < height + 2
                        and 0 <= neighbor[1] < width + 2
                        and padded[neighbor[0]][neighbor[1]] == 0
                        and neighbor not in seen
                    ):
                        seen.add(neighbor)
                        queue.append(neighbor)
    return max(0, components - 1)


def _mask_feature(grid: Grid, background_role: str, feature: str) -> str:
    mask = _mask(grid, background_role)
    variants = _d4(mask)
    stabilizer = sum(variant == mask for variant in variants)
    # _d4 removes duplicate values, so compute the full eight-action
    # stabilizer explicitly.
    full: list[Grid] = []
    current = mask
    for _ in range(4):
        full.extend((current, _reflect(current)))
        current = _rotate(current)
    stabilizer = sum(variant == mask for variant in full)
    values: dict[str, Any] = {
        "area": sum(cell for row in mask for cell in row),
        "components4": _component_count(mask, 4),
        "components8": _component_count(mask, 8),
        "holes": _hole_count(mask),
        "symmetries": stabilizer,
        "orbit": len(set(full)),
        "bbox_shape": sorted(_shape(mask)),
        "canonical_mask": min(_canonical(_plain(variant)) for variant in full),
    }
    values["topology"] = [
        values["area"],
        values["components4"],
        values["components8"],
        values["holes"],
        values["symmetries"],
        values["orbit"],
        values["bbox_shape"],
    ]
    if feature not in values:
        raise Undefined("unknown mask feature")
    return _canonical(values[feature])


def _scalar_codebook(program: Mapping[str, Any], grid: Grid) -> Grid:
    role = str(program.get("background_role"))
    feature = str(program.get("feature"))
    raw_mapping = program.get("mapping")
    if not isinstance(raw_mapping, list):
        raise Undefined("malformed codebook")
    mapping: dict[str, int] = {}
    for record in raw_mapping:
        if (
            not isinstance(record, list)
            or len(record) != 2
            or not isinstance(record[0], str)
            or isinstance(record[1], bool)
            or not isinstance(record[1], int)
            or not 0 <= record[1] <= 9
        ):
            raise Undefined("malformed codebook entry")
        mapping[record[0]] = int(record[1])
    key = _mask_feature(grid, role, feature)
    if key not in mapping:
        raise Undefined("unseen structural code")
    return ((mapping[key],),)


def _infer_scalar_programs(demonstrations: Sequence[Pair]) -> list[dict[str, Any]]:
    if any(_shape(target) != (1, 1) for _, target in demonstrations):
        return []
    if any(len(source) > 9 or len(source[0]) > 9 for source, _ in demonstrations):
        return []
    programs: list[dict[str, Any]] = []
    roles = ["zero"] if all(0 in {cell for row in source for cell in row} for source, _ in demonstrations) else ["mode"]
    features = (
        "area",
        "components4",
        "components8",
        "holes",
        "symmetries",
        "orbit",
        "bbox_shape",
        "canonical_mask",
        "topology",
    )
    for role in roles:
        for feature in features:
            mapping: dict[str, int] = {}
            valid = True
            try:
                for source, target in demonstrations:
                    key = _mask_feature(source, role, feature)
                    value = target[0][0]
                    if key in mapping and mapping[key] != value:
                        valid = False
                        break
                    mapping[key] = value
            except Undefined:
                valid = False
            if not valid or len(mapping) < 2 or len(set(mapping.values())) < 2:
                continue
            programs.append(
                {
                    "schema": SCHEMA,
                    "operator": "scalar_feature_codebook",
                    "background_role": role,
                    "feature": feature,
                    "mapping": [[key, mapping[key]] for key in sorted(mapping)],
                    "description_length": 8 + len(mapping),
                }
            )
    return programs


# ---------------------------------------------------------------------------
# Sparse corner frame plus payload


def _corner_frame_payload(grid: Grid) -> Grid:
    background = _background(grid)
    height, width = _shape(grid)
    outputs: set[Grid] = set()
    palette = sorted({cell for row in grid for cell in row} - {background})
    for corner_color in palette:
        coords = {(r, c) for r, row in enumerate(grid) for c, cell in enumerate(row) if cell == corner_color}
        if len(coords) != 4:
            continue
        rows = sorted({row for row, _ in coords})
        columns = sorted({column for _, column in coords})
        if len(rows) != 2 or len(columns) != 2:
            continue
        top, bottom = rows
        left, right = columns
        corners = {(top, left), (top, right), (bottom, left), (bottom, right)}
        if coords != corners or bottom - top < 2 or right - left < 2:
            continue
        frame_cells = set(corners)
        anchors: dict[str, int] = {}
        side_cells = {
            "top": [(top, column) for column in range(left + 1, right)],
            "bottom": [(bottom, column) for column in range(left + 1, right)],
            "left": [(row, left) for row in range(top + 1, bottom)],
            "right": [(row, right) for row in range(top + 1, bottom)],
        }
        valid_frame = True
        for side, cells in side_cells.items():
            visible = [grid[row][column] for row, column in cells if grid[row][column] != background]
            if visible:
                if len(set(visible)) != 1:
                    valid_frame = False
                    break
                anchors[side] = visible[0]
                frame_cells.update((row, column) for row, column in cells if grid[row][column] != background)
        if not valid_frame or len(anchors) < 2:
            continue
        # All non-background material inside the rectangle must be scaffold.
        if any(
            grid[row][column] != background and (row, column) not in frame_cells
            for row in range(top, bottom + 1)
            for column in range(left, right + 1)
        ):
            continue
        outside = [
            (row, column)
            for row in range(height)
            for column in range(width)
            if grid[row][column] != background and (row, column) not in frame_cells
        ]
        if not outside:
            continue
        payload = _crop(grid, _bbox(outside))
        inner_height, inner_width = bottom - top - 1, right - left - 1
        if set(anchors) <= {"left", "right"}:
            variants = (payload, _reflect(payload))
        elif set(anchors) <= {"top", "bottom"}:
            variants = (payload, tuple(reversed(payload)))
        else:
            variants = _d4(payload)
        for variant in dict.fromkeys(variants):
            if _shape(variant) != (inner_height, inner_width):
                continue
            side_positions = {
                "top": [(0, column) for column in range(inner_width)],
                "bottom": [(inner_height - 1, column) for column in range(inner_width)],
                "left": [(row, 0) for row in range(inner_height)],
                "right": [(row, inner_width - 1) for row in range(inner_height)],
            }
            docked = True
            for side, color in anchors.items():
                touching = [variant[row][column] for row, column in side_positions[side] if variant[row][column] != background]
                if not touching or any(value != color for value in touching):
                    docked = False
                    break
            if not docked:
                continue
            canvas = [list(row[left : right + 1]) for row in grid[top : bottom + 1]]
            for row in range(inner_height):
                for column in range(inner_width):
                    if variant[row][column] != background:
                        canvas[row + 1][column + 1] = variant[row][column]
            outputs.add(_freeze(canvas))
    if len(outputs) != 1:
        raise Undefined("corner-frame docking is ambiguous")
    return next(iter(outputs))


# ---------------------------------------------------------------------------
# Four-side frame legend applied to stencil boundary contacts


def _horizontal_runs(grid: Grid, background: int) -> list[tuple[int, int, int, int]]:
    runs: list[tuple[int, int, int, int]] = []
    for row, line in enumerate(grid):
        column = 0
        while column < len(line):
            color = line[column]
            if color == background:
                column += 1
                continue
            right = column
            while right + 1 < len(line) and line[right + 1] == color:
                right += 1
            if right - column + 1 >= 2:
                runs.append((row, column, right, color))
            column = right + 1
    return runs


def _geodesic_stencil_legend(grid: Grid) -> Grid:
    background = _background(grid)
    height, width = _shape(grid)
    outputs: set[Grid] = set()
    runs = _horizontal_runs(grid, background)
    for top_run, bottom_run in itertools.combinations(runs, 2):
        top, start, end, top_color = top_run
        bottom, start2, end2, bottom_color = bottom_run
        if start != start2 or end != end2 or bottom <= top + 1:
            continue
        left, right = start - 1, end + 1
        if left < 0 or right >= width:
            continue
        if grid[top][left] != background or grid[top][right] != background:
            continue
        if grid[bottom][left] != background or grid[bottom][right] != background:
            continue
        left_values = [grid[row][left] for row in range(top + 1, bottom)]
        right_values = [grid[row][right] for row in range(top + 1, bottom)]
        if (
            not left_values
            or background in left_values
            or len(set(left_values)) != 1
            or background in right_values
            or len(set(right_values)) != 1
        ):
            continue
        left_color, right_color = left_values[0], right_values[0]
        side_colors = (top_color, right_color, bottom_color, left_color)
        if len(set(side_colors)) != 4:
            continue
        # The rectangle interior is an empty target canvas.
        if any(
            grid[row][column] != background
            for row in range(top + 1, bottom)
            for column in range(left + 1, right)
        ):
            continue
        frame_cells = (
            {(top, column) for column in range(start, end + 1)}
            | {(bottom, column) for column in range(start, end + 1)}
            | {(row, left) for row in range(top + 1, bottom)}
            | {(row, right) for row in range(top + 1, bottom)}
        )
        outside = [
            (row, column)
            for row in range(height)
            for column in range(width)
            if grid[row][column] != background and (row, column) not in frame_cells
        ]
        if not outside:
            continue
        stencil_colors = {grid[row][column] for row, column in outside}
        if len(stencil_colors) != 1:
            continue
        stencil_color = next(iter(stencil_colors))
        stencil = _crop(grid, _bbox(outside))
        inner_height, inner_width = bottom - top - 1, right - left - 1
        if _shape(stencil) != (inner_height, inner_width):
            continue
        occupied = {
            (row, column)
            for row in range(inner_height)
            for column in range(inner_width)
            if stencil[row][column] == stencil_color
        }
        if not occupied:
            continue
        canvas = [[background] * (inner_width + 2) for _ in range(inner_height + 2)]
        for column in range(1, inner_width + 1):
            canvas[0][column] = top_color
            canvas[-1][column] = bottom_color
        for row in range(1, inner_height + 1):
            canvas[row][0] = left_color
            canvas[row][-1] = right_color
        contacts_seen: set[int] = set()
        for row, column in occupied:
            contacts: set[int] = set()
            if row == 0:
                contacts.add(top_color)
            if row == inner_height - 1:
                contacts.add(bottom_color)
            if column == 0:
                contacts.add(left_color)
            if column == inner_width - 1:
                contacts.add(right_color)
            if len(contacts) == 1:
                color = next(iter(contacts))
                contacts_seen.add(color)
                canvas[row + 1][column + 1] = color
            else:
                canvas[row + 1][column + 1] = stencil_color
        if len(contacts_seen) < 2:
            continue
        outputs.add(_freeze(canvas))
    if len(outputs) != 1:
        raise Undefined("stencil legend is absent or ambiguous")
    return next(iter(outputs))


# ---------------------------------------------------------------------------
# Repeated panels with affine solid-rectangle growth


def _split_panels(grid: Grid) -> list[tuple[str, tuple[Grid, ...]]]:
    height, width = _shape(grid)
    results: list[tuple[str, tuple[Grid, ...]]] = []
    for count in range(3, 9):
        if height % count == 0:
            side = height // count
            panels = tuple(grid[index * side : (index + 1) * side] for index in range(count))
            results.append(("vertical", panels))
            results.append(("vertical-reversed", tuple(reversed(panels))))
        if width % count == 0:
            side = width // count
            panels = tuple(tuple(row[index * side : (index + 1) * side] for row in grid) for index in range(count))
            results.append(("horizontal", panels))
            results.append(("horizontal-reversed", tuple(reversed(panels))))
    return results


def _panel_affine_growth(grid: Grid) -> Grid:
    outputs: set[Grid] = set()
    for _axis, panels in _split_panels(grid):
        base = panels[-1]
        visible = panels[:-1]
        if len(visible) < 2 or any(_shape(panel) != _shape(base) for panel in visible):
            continue
        try:
            base_background = _background(base)
        except Undefined:
            continue
        if any(
            panel[row][column] == base_background
            and panel[row][column] != base[row][column]
            for panel in visible
            for row in range(len(base))
            for column in range(len(base[0]))
        ):
            continue
        colors = sorted({cell for panel in panels for row in panel for cell in row})
        records: list[
            tuple[int, Grid, tuple[int, int, int, int], tuple[int, int, int, int]]
        ] = []
        valid = True
        for color in colors:
            if color == base_background:
                continue
            occurrences: list[tuple[int, Grid, set[Cell]]] = []
            for index, panel in enumerate(visible):
                support = {
                    (row, column)
                    for row, line in enumerate(panel)
                    for column, value in enumerate(line)
                    if value == color and value != base[row][column]
                }
                if support:
                    occurrences.append((index, panel, support))
            if not occurrences:
                continue
            if len(occurrences) < 2:
                valid = False
                break
            periods = {
                right[0] - left[0]
                for left, right in zip(occurrences, occurrences[1:])
            }
            if len(periods) != 1:
                valid = False
                break
            period = next(iter(periods))
            if len(visible) - occurrences[-1][0] != period:
                # A regular alternating role that is not due on the next
                # panel contributes no paint to this successor.
                continue
            previous, latest = occurrences[-2], occurrences[-1]
            records.append(
                (color, latest[1], _bbox(previous[2]), _bbox(latest[2]))
            )
        if not valid or not records:
            continue
        canvas = [list(row) for row in base]
        # Higher color tokens are rendered first; a lower token that already
        # forms the inner member of a nested motif remains visible on top.
        for color, latest_panel, box0, box1 in sorted(records, reverse=True):
            predicted = tuple(2 * right - left for left, right in zip(box0, box1))
            top, bottom, left, right = predicted
            panel_height, panel_width = _shape(base)
            if not (0 <= top <= bottom < panel_height and 0 <= left <= right < panel_width):
                valid = False
                break
            old_height = box1[1] - box1[0] + 1
            old_width = box1[3] - box1[2] + 1
            new_height = bottom - top + 1
            new_width = right - left + 1
            row_signatures = tuple(
                tuple(
                    latest_panel[box1[0] + row][box1[2] + column] == color
                    for column in range(old_width)
                )
                for row in range(old_height)
            )
            column_signatures = tuple(
                tuple(row_signatures[row][column] for row in range(old_height))
                for column in range(old_width)
            )

            def period(signatures: Sequence[tuple[bool, ...]]) -> int | None:
                for candidate in range(1, len(signatures) // 2 + 1):
                    if all(
                        signatures[index] == signatures[index % candidate]
                        for index in range(len(signatures))
                    ):
                        return candidate
                return None

            row_period = period(row_signatures)
            column_period = period(column_signatures)

            def project(offset: int, size: int, repeat: int | None) -> int:
                if 0 <= offset < size:
                    return offset
                if repeat is not None:
                    return offset % repeat
                return min(size - 1, max(0, offset))

            for row in range(new_height):
                source_row_offset = project(
                    top + row - box1[0], old_height, row_period
                )
                source_row = box1[0] + source_row_offset
                for column in range(new_width):
                    source_column_offset = project(
                        left + column - box1[2], old_width, column_period
                    )
                    source_column = box1[2] + source_column_offset
                    if latest_panel[source_row][source_column] == color:
                        canvas[top + row][left + column] = color
        if valid:
            outputs.add(_freeze(canvas))
    if len(outputs) != 1:
        raise Undefined("panel progression is absent or ambiguous")
    return next(iter(outputs))


# ---------------------------------------------------------------------------
# Program enumeration, replay, and proof-carrying compiler


_FIXED_PROGRAMS: tuple[dict[str, Any], ...] = (
    {
        "schema": SCHEMA,
        "operator": "line_layer_order",
        "description_length": 9,
    },
    {
        "schema": SCHEMA,
        "operator": "corner_frame_payload",
        "description_length": 14,
    },
    {
        "schema": SCHEMA,
        "operator": "boundary_stencil_legend",
        "description_length": 16,
    },
    {
        "schema": SCHEMA,
        "operator": "panel_affine_growth",
        "description_length": 13,
    },
)


def _execute(program: Mapping[str, Any], grid: Grid) -> Grid:
    if program.get("schema") != SCHEMA:
        raise Undefined("wrong program schema")
    operator = program.get("operator")
    if operator == "line_layer_order":
        return _line_layer_order(grid)
    if operator == "scalar_feature_codebook":
        return _scalar_codebook(program, grid)
    if operator == "corner_frame_payload":
        return _corner_frame_payload(grid)
    if operator == "boundary_stencil_legend":
        return _geodesic_stencil_legend(grid)
    if operator == "panel_affine_growth":
        return _panel_affine_growth(grid)
    raise Undefined("unknown operator")


def execute_program(program: Mapping[str, Any], value: Any) -> list[list[int]]:
    """Execute a serialized compact-codec program on one input grid."""

    if not isinstance(program, Mapping):
        raise ValueError("program must be a mapping")
    return _plain(_execute(program, _grid(value)))


def replay_program(program: Mapping[str, Any], value: Any) -> list[list[int]]:
    """Tournament replay hook; the tournament seals the single-stage receipt."""

    return execute_program(program, value)


def _programs(demonstrations: Sequence[Pair]) -> tuple[dict[str, Any], ...]:
    candidates = list(_FIXED_PROGRAMS)
    candidates.extend(_infer_scalar_programs(demonstrations))
    unique = {_canonical(program): program for program in candidates}
    return tuple(unique[key] for key in sorted(unique))


def _behavior(program: Mapping[str, Any], grids: Sequence[Grid]) -> tuple[Grid, ...]:
    return tuple(_execute(program, grid) for grid in grids)


def _counterfactuals(
    program: Mapping[str, Any], demonstrations: Sequence[Pair], limits: Limits
) -> tuple[bool, int]:
    checks = 0
    invariant_output = program.get("operator") in {"line_layer_order", "scalar_feature_codebook"}
    for source, target in demonstrations:
        for quarter_turns in range(4):
            for reflected in (False, True):
                transformed_source = _transform(source, quarter_turns, reflected)
                expected = target if invariant_output else _transform(target, quarter_turns, reflected)
                checks += 1
                if checks > limits.max_counterfactual_checks:
                    return False, checks
                try:
                    actual = _execute(program, transformed_source)
                except (Undefined, ValueError, KeyError, IndexError, ZeroDivisionError):
                    return False, checks
                if actual != expected:
                    return False, checks
    return True, checks


def compile_task(task: Any, limits: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    """Compile one unique, counterfactually checked behavior or abstain."""

    try:
        bounds = Limits.from_value(limits)
        demonstrations, tests = _sanitize(task, bounds)
    except (Undefined, TypeError, ValueError, KeyError):
        return []
    programs = _programs(demonstrations)
    if len(programs) > bounds.max_programs:
        return []
    exact: list[tuple[dict[str, Any], tuple[Grid, ...]]] = []
    calls = 0
    expected = tuple(target for _, target in demonstrations)
    for program in programs:
        try:
            train_outputs = _behavior(program, tuple(source for source, _ in demonstrations))
            calls += len(demonstrations)
            if train_outputs != expected:
                continue
            test_outputs = _behavior(program, tests)
            calls += len(tests)
            if calls > bounds.max_executor_calls:
                return []
        except (Undefined, TypeError, ValueError, KeyError, IndexError, ZeroDivisionError):
            continue
        exact.append((program, test_outputs))
    if not exact:
        return []
    behaviors: dict[str, list[tuple[dict[str, Any], tuple[Grid, ...]]]] = defaultdict(list)
    for program, outputs in exact:
        behaviors[_digest([_plain(grid) for grid in outputs])].append((program, outputs))
    if len(behaviors) != 1:
        return []
    behavior_hash, equivalents = next(iter(sorted(behaviors.items())))
    equivalents.sort(key=lambda item: (int(item[0]["description_length"]), _canonical(item[0])))
    representative, test_outputs = equivalents[0]
    counterfactual_ok, counterfactual_checks = _counterfactuals(
        representative, demonstrations, bounds
    )
    if not counterfactual_ok:
        return []
    try:
        train_outputs = _behavior(representative, tuple(source for source, _ in demonstrations))
    except Undefined:
        return []
    if train_outputs != expected:
        return []
    candidate = {
        "family": "multiscale_codec",
        "program": json.loads(_canonical(representative)),
        "train_outputs": [_plain(grid) for grid in train_outputs],
        "test_outputs": [_plain(grid) for grid in test_outputs],
        "complexity": int(representative["description_length"]),
        "evidence": {
            "all_demonstrations_exact": True,
            "exact_replay": True,
            "serialized_replay_program": True,
            "finite_enumeration_complete": True,
            "programs_enumerated": len(programs),
            "exact_programs": len(exact),
            "full_test_behavior_classes": len(behaviors),
            "full_test_behavior_hash": behavior_hash,
            "equivalent_programs": len(equivalents),
            "d4_counterfactual_checks": counterfactual_checks,
            "bounded_search": True,
            "hard_caps_exhausted": False,
            "task_identity_observed": False,
            "test_labels_observed": False,
            "solution_store_observed": False,
        },
    }
    candidate["evidence"]["candidate_semantic_hash"] = _digest(candidate)
    return [candidate][: bounds.max_candidates]


__all__ = ["AUTHOR", "Limits", "SCHEMA", "compile_task", "execute_program", "replay_program"]
