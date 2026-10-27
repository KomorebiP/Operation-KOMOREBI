"""Proof-carrying relational geometry compiler for PR-LASM Block 15.

The grammar operates on intrinsic objects, axes, panels, and keyed templates.
It deliberately has no task-identity or held-out-label interface.  A candidate
is emitted only after exact demonstration replay, isolated leave-one-out
re-induction, a unique complete test behavior, and D4/palette counterfactual
checks.

Author: Komorebi P.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
import hashlib
import itertools
import json
from typing import Any


Grid = tuple[tuple[int, ...], ...]
Cell = tuple[int, int]
Pair = tuple[Grid, Grid]

AUTHOR = "Komorebi P."
SCHEMA = "komorebi.pr_lasm.block15.relational_geometry_compiler.program.v1"


class Undefined(ValueError):
    """A geometric role or a unique bounded rendering is undefined."""


@dataclass(frozen=True, slots=True)
class Limits:
    max_grid_cells: int = 900
    max_examples: int = 20
    max_programs: int = 16
    max_executor_calls: int = 20_000
    max_components: int = 256
    max_renderings: int = 256
    max_gauge_checks: int = 8_192
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
            "max_examples": 40,
            "max_programs": 128,
            "max_executor_calls": 200_000,
            "max_components": 1_024,
            "max_renderings": 4_096,
            "max_gauge_checks": 32_768,
            "max_candidates": 1,
        }
        aliases = {"candidate_cap": "max_candidates"}
        accepted_passthrough = {
            "max_replay_calls",
            "max_replay_stages",
            "max_total_candidates",
            "max_trace_bytes",
            "time_limit",
            "time_limit_seconds",
        }
        unknown = set(value) - set(ceilings) - set(aliases) - accepted_passthrough
        if unknown:
            raise Undefined("unknown finite limit")
        parsed: dict[str, int] = {}
        for name, ceiling in ceilings.items():
            alias = next((key for key, target in aliases.items() if target == name), None)
            raw = value.get(name, value.get(alias, getattr(defaults, name)))
            if isinstance(raw, bool) or not isinstance(raw, int) or raw < 1:
                raise Undefined(f"limits.{name} must be a positive integer")
            parsed[name] = min(raw, ceiling)
        return cls(**parsed)


def _canonical(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    )


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _grid(value: Any, limits: Limits) -> Grid:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or not value:
        raise Undefined("grid must be a nonempty row sequence")
    rows: list[tuple[int, ...]] = []
    width: int | None = None
    for raw_row in value:
        if not isinstance(raw_row, Sequence) or isinstance(raw_row, (str, bytes)) or not raw_row:
            raise Undefined("grid row is invalid")
        row: list[int] = []
        for cell in raw_row:
            if isinstance(cell, bool) or not isinstance(cell, int) or not 0 <= cell <= 9:
                raise Undefined("ARC colors must be integers in [0, 9]")
            row.append(int(cell))
        if width is None:
            width = len(row)
        elif width != len(row):
            raise Undefined("grid is ragged")
        rows.append(tuple(row))
    if len(rows) * int(width or 0) > limits.max_grid_cells:
        raise Undefined("grid exceeds the cell bound")
    return tuple(rows)


def _plain(grid: Grid) -> list[list[int]]:
    return [list(row) for row in grid]


def _freeze(rows: Sequence[Sequence[int]]) -> Grid:
    return tuple(tuple(int(cell) for cell in row) for row in rows)


def _shape(grid: Grid) -> tuple[int, int]:
    return len(grid), len(grid[0])


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
        raise Undefined("task needs bounded train and test splits")
    train: list[Pair] = []
    for example in raw_train:
        if not isinstance(example, Mapping):
            raise Undefined("training example is invalid")
        train.append((_grid(example.get("input"), limits), _grid(example.get("output"), limits)))
    tests: list[Grid] = []
    for example in raw_test:
        if not isinstance(example, Mapping):
            raise Undefined("test example is invalid")
        # Deliberately ignore an injected held-out ``output`` field.
        tests.append(_grid(example.get("input"), limits))
    return tuple(train), tuple(tests)


def _background(grid: Grid) -> int:
    counts = Counter(cell for row in grid for cell in row)
    maximum = max(counts.values())
    winners = [color for color, count in counts.items() if count == maximum]
    if len(winners) != 1:
        raise Undefined("background mode is tied")
    return winners[0]


def _components(
    grid: Grid, background: int, *, connectivity: int = 4, monochrome: bool = True
) -> tuple[tuple[int | None, frozenset[Cell]], ...]:
    height, width = _shape(grid)
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    if connectivity == 8:
        directions += [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    seen: set[Cell] = set()
    result: list[tuple[int | None, frozenset[Cell]]] = []
    for row in range(height):
        for column in range(width):
            if grid[row][column] == background or (row, column) in seen:
                continue
            seed_color = grid[row][column]
            queue = [(row, column)]
            seen.add((row, column))
            cells: set[Cell] = set()
            for current_row, current_column in queue:
                cells.add((current_row, current_column))
                for dr, dc in directions:
                    nr, nc = current_row + dr, current_column + dc
                    if not (0 <= nr < height and 0 <= nc < width) or (nr, nc) in seen:
                        continue
                    if grid[nr][nc] == background:
                        continue
                    if monochrome and grid[nr][nc] != seed_color:
                        continue
                    seen.add((nr, nc))
                    queue.append((nr, nc))
            result.append((seed_color if monochrome else None, frozenset(cells)))
    result.sort(key=lambda item: (min(item[1]), len(item[1]), -1 if item[0] is None else item[0]))
    return tuple(result)


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


def _solid_square(cells: Iterable[Cell]) -> tuple[int, int, int] | None:
    points = frozenset(cells)
    if not points:
        return None
    r0, r1, c0, c1 = _bbox(points)
    side = r1 - r0 + 1
    if side != c1 - c0 + 1 or len(points) != side * side:
        return None
    return r0, c0, side


_D4 = ("identity", "rot90", "rot180", "rot270", "flip_h", "flip_v", "transpose", "anti")
_D4_INVERSE = {
    "identity": "identity",
    "rot90": "rot270",
    "rot180": "rot180",
    "rot270": "rot90",
    "flip_h": "flip_h",
    "flip_v": "flip_v",
    "transpose": "transpose",
    "anti": "anti",
}


def _d4(grid: Grid, operation: str) -> Grid:
    if operation == "identity":
        return grid
    if operation == "rot90":
        return tuple(tuple(row) for row in zip(*reversed(grid)))
    if operation == "rot180":
        return _d4(_d4(grid, "rot90"), "rot90")
    if operation == "rot270":
        return _d4(_d4(grid, "rot180"), "rot90")
    if operation == "flip_h":
        return tuple(tuple(reversed(row)) for row in grid)
    if operation == "flip_v":
        return tuple(reversed(grid))
    if operation == "transpose":
        return tuple(tuple(grid[row][column] for row in range(len(grid))) for column in range(len(grid[0])))
    if operation == "anti":
        return _d4(_d4(grid, "transpose"), "rot180")
    raise Undefined("unknown D4 operation")


def _transform_cell(row: int, column: int, height: int, width: int, operation: str) -> Cell:
    if operation == "identity":
        return row, column
    if operation == "rot90":
        return column, height - 1 - row
    if operation == "rot180":
        return height - 1 - row, width - 1 - column
    if operation == "rot270":
        return width - 1 - column, row
    if operation == "flip_h":
        return row, width - 1 - column
    if operation == "flip_v":
        return height - 1 - row, column
    if operation == "transpose":
        return column, row
    if operation == "anti":
        return width - 1 - column, height - 1 - row
    raise Undefined("unknown D4 operation")


def _paint_atomic(grid: Grid, writes: Mapping[Cell, int], background: int) -> Grid:
    height, width = _shape(grid)
    output = _plain(grid)
    for (row, column), color in sorted(writes.items()):
        if not (0 <= row < height and 0 <= column < width):
            raise Undefined("geometric write is outside the canvas")
        if output[row][column] not in (background, color):
            raise Undefined("geometric writes collide")
        output[row][column] = color
    return _freeze(output)


def _reflect_template_to_aligned_singletons(grid: Grid) -> tuple[Grid, dict[str, Any]]:
    background = _background(grid)
    counts = Counter(cell for row in grid for cell in row)
    roles = {
        color: frozenset(
            (row, column)
            for row, line in enumerate(grid)
            for column, cell in enumerate(line)
            if cell == color
        )
        for color in counts
        if color != background
    }
    templates = [(color, cells) for color, cells in roles.items() if len(cells) > 1]
    markers = [(color, cells) for color, cells in roles.items() if len(cells) == 1]
    if len(templates) != 1 or not markers or len(templates[0][1]) < 4:
        raise Undefined("one template and singleton anchors are required")
    _, template = templates[0]
    r0, r1, c0, c1 = _bbox(template)
    writes: dict[Cell, int] = {}
    for marker_color, marker_cells in markers:
        (marker_row, marker_column), = marker_cells
        if c0 <= marker_column <= c1 and marker_row < r0:
            aligned = [point for point in template if point[1] == marker_column]
            anchor = min(aligned) if aligned else None
            axis = "vertical"
        elif c0 <= marker_column <= c1 and marker_row > r1:
            aligned = [point for point in template if point[1] == marker_column]
            anchor = max(aligned) if aligned else None
            axis = "vertical"
        elif r0 <= marker_row <= r1 and marker_column < c0:
            aligned = [point for point in template if point[0] == marker_row]
            anchor = min(aligned, key=lambda point: point[1]) if aligned else None
            axis = "horizontal"
        elif r0 <= marker_row <= r1 and marker_column > c1:
            aligned = [point for point in template if point[0] == marker_row]
            anchor = max(aligned, key=lambda point: point[1]) if aligned else None
            axis = "horizontal"
        else:
            raise Undefined("anchor is not cardinally aligned outside the template")
        if anchor is None:
            raise Undefined("template has no homologous anchor cell")
        anchor_row, anchor_column = anchor
        if axis == "vertical":
            reflected_anchor = (r0 + r1 - anchor_row, anchor_column)
        else:
            reflected_anchor = (anchor_row, c0 + c1 - anchor_column)
        for row, column in template:
            if axis == "vertical":
                reflected = (r0 + r1 - row, column)
            else:
                reflected = (row, c0 + c1 - column)
            target = (
                reflected[0] + marker_row - reflected_anchor[0],
                reflected[1] + marker_column - reflected_anchor[1],
            )
            if target in writes and writes[target] != marker_color:
                raise Undefined("reflected stencils conflict")
            writes[target] = marker_color
    result = _paint_atomic(grid, writes, background)
    return result, {"templates": 1, "anchors": len(markers), "relation": "cardinal-reflection"}


def _project_objects_away_from_anchor(grid: Grid) -> tuple[Grid, dict[str, Any]]:
    background = _background(grid)
    height, width = _shape(grid)
    components = _components(grid, background, connectivity=4, monochrome=True)
    colors = sorted({int(color) for color, _ in components if color is not None})
    candidates: list[tuple[int, list[tuple[int, frozenset[Cell], str]]]] = []
    for anchor_color in colors:
        anchor_cells = frozenset(
            (row, column)
            for row, line in enumerate(grid)
            for column, cell in enumerate(line)
            if cell == anchor_color
        )
        others = [(int(color), cells) for color, cells in components if color != anchor_color]
        if len(others) < 2:
            continue
        directed: list[tuple[int, frozenset[Cell], str]] = []
        valid = True
        for color, cells in others:
            contacts: set[str] = set()
            for row, column in cells:
                for dr, dc, name in (
                    (-1, 0, "up"),
                    (1, 0, "down"),
                    (0, -1, "left"),
                    (0, 1, "right"),
                ):
                    if (row - dr, column - dc) in anchor_cells:
                        contacts.add(name)
            if len(contacts) != 1:
                valid = False
                break
            directed.append((color, cells, next(iter(contacts))))
        if valid:
            candidates.append((anchor_color, directed))
    if len(candidates) != 1:
        raise Undefined("anchor role is absent or ambiguous")
    anchor_color, directed = candidates[0]
    output = _plain(grid)
    for _, cells, _ in directed:
        for row, column in cells:
            output[row][column] = background
    occupied: set[Cell] = set()
    for color, cells, direction in directed:
        r0, r1, c0, c1 = _bbox(cells)
        dr = dc = 0
        if direction == "up":
            dr = -r0
        elif direction == "down":
            dr = height - 1 - r1
        elif direction == "left":
            dc = -c0
        else:
            dc = width - 1 - c1
        for row, column in cells:
            target = (row + dr, column + dc)
            if target in occupied or output[target[0]][target[1]] != background:
                raise Undefined("boundary projection collides")
            occupied.add(target)
            output[target[0]][target[1]] = color
    return _freeze(output), {
        "anchor_color_components": sum(1 for color, _ in components if color == anchor_color),
        "projected_objects": len(directed),
    }


def _transform_local_map(
    points: Mapping[Cell, int], operation: str
) -> dict[Cell, int]:
    r0, r1, c0, c1 = _bbox(points)
    height, width = r1 - r0 + 1, c1 - c0 + 1
    return {
        _transform_cell(row - r0, column - c0, height, width, operation): color
        for (row, column), color in points.items()
    }


def _relocate_keyed_templates(grid: Grid, limits: Limits) -> tuple[Grid, dict[str, Any]]:
    background = _background(grid)
    height, width = _shape(grid)
    mixed = _components(grid, background, connectivity=8, monochrome=False)
    templates: list[tuple[frozenset[Cell], int, frozenset[int]]] = []
    for _, cells in mixed:
        counts = Counter(grid[row][column] for row, column in cells)
        ordered = counts.most_common()
        if (
            len(counts) >= 4
            and ordered[0][1] >= 2
            and ordered[0][1] > ordered[1][1]
            and all(count == 1 for color, count in counts.items() if color != ordered[0][0])
        ):
            templates.append((cells, ordered[0][0], frozenset(counts) - {ordered[0][0]}))
    if not templates:
        raise Undefined("no keyed templates")
    template_cells = frozenset().union(*(cells for cells, _, _ in templates))
    external = {
        (row, column): grid[row][column]
        for row in range(height)
        for column in range(width)
        if grid[row][column] != background and (row, column) not in template_cells
    }
    if len(external) != sum(len(keys) for _, _, keys in templates):
        raise Undefined("external key inventory does not balance")
    choices: list[list[tuple[dict[Cell, int], frozenset[Cell]]]] = []
    for cells, scaffold, _ in templates:
        points = {(row, column): grid[row][column] for row, column in cells}
        candidates: dict[str, tuple[dict[Cell, int], frozenset[Cell]]] = {}
        for operation in _D4:
            transformed = _transform_local_map(points, operation)
            keys = [(point, color) for point, color in transformed.items() if color != scaffold]
            if not keys:
                continue
            first_point, first_color = keys[0]
            shifts = {
                (anchor[0] - first_point[0], anchor[1] - first_point[1])
                for anchor, color in external.items()
                if color == first_color
            }
            for dr, dc in shifts:
                mapped = {(row + dr, column + dc): color for (row, column), color in transformed.items()}
                if any(not (0 <= row < height and 0 <= column < width) for row, column in mapped):
                    continue
                if not all(
                    external.get(point) == color
                    for point, color in mapped.items()
                    if color != scaffold
                ):
                    continue
                if not all(grid[row][column] in (background, color) for (row, column), color in mapped.items()):
                    continue
                consumed = frozenset(point for point, color in mapped.items() if color != scaffold)
                candidates[_digest(sorted((list(point), color) for point, color in mapped.items()))] = (
                    mapped,
                    consumed,
                )
        if not candidates:
            raise Undefined("a keyed template has no target constellation")
        choices.append(list(candidates.values()))
    renderings: dict[str, Grid] = {}
    for combination in itertools.product(*choices):
        consumed_sets = [consumed for _, consumed in combination]
        consumed = frozenset().union(*consumed_sets)
        if consumed != frozenset(external) or sum(len(value) for value in consumed_sets) != len(external):
            continue
        output = _plain(grid)
        for cells, _, _ in templates:
            for row, column in cells:
                output[row][column] = background
        valid = True
        for mapped, _ in combination:
            for (row, column), color in mapped.items():
                if output[row][column] not in (background, color):
                    valid = False
                    break
                output[row][column] = color
            if not valid:
                break
        if valid:
            frozen = _freeze(output)
            renderings[_digest(_plain(frozen))] = frozen
        if len(renderings) > limits.max_renderings:
            raise Undefined("rendering cap exhausted")
    if len(renderings) != 1:
        raise Undefined("keyed relocation behavior is absent or ambiguous")
    return next(iter(renderings.values())), {"templates": len(templates), "behavior_classes": 1}


def _swap_shape_species(grid: Grid) -> tuple[Grid, dict[str, Any]]:
    background = _background(grid)
    height, width = _shape(grid)
    colors = sorted({cell for row in grid for cell in row} - {background})
    if len(colors) != 2:
        raise Undefined("shape exchange needs two species")
    by_color: dict[int, list[frozenset[Cell]]] = {color: [] for color in colors}
    for color, cells in _components(grid, background, connectivity=8, monochrome=True):
        if color is None:
            raise Undefined("invalid component color")
        by_color[int(color)].append(cells)
    prototypes: dict[int, tuple[frozenset[Cell], tuple[int, int]]] = {}
    for color, components in by_color.items():
        normalized: set[tuple[frozenset[Cell], tuple[int, int]]] = set()
        for cells in components:
            r0, r1, c0, c1 = _bbox(cells)
            normalized.add(
                (
                    frozenset((row - r0, column - c0) for row, column in cells),
                    (r1 - r0 + 1, c1 - c0 + 1),
                )
            )
        if len(normalized) != 1:
            raise Undefined("a species has multiple intrinsic shapes")
        prototypes[color] = next(iter(normalized))
    if prototypes[colors[0]][1] != prototypes[colors[1]][1]:
        raise Undefined("species frames differ")
    if sum(len(components) for components in by_color.values()) < 3:
        raise Undefined("shape exchange lacks multiplicity")
    output = [[background] * width for _ in range(height)]
    for color, replacement in ((colors[0], colors[1]), (colors[1], colors[0])):
        mask, _ = prototypes[replacement]
        for cells in by_color[color]:
            r0, _, c0, _ = _bbox(cells)
            for dr, dc in mask:
                output[r0 + dr][c0 + dc] = replacement
    return _freeze(output), {
        "species": 2,
        "instances": sum(len(components) for components in by_color.values()),
    }


def _mirror_complete_about_cross(grid: Grid) -> tuple[Grid, dict[str, Any]]:
    background = _background(grid)
    height, width = _shape(grid)
    candidates: list[tuple[int, int, int]] = []
    for color in sorted({cell for row in grid for cell in row} - {background}):
        rows = [row for row in range(height) if all(cell == color for cell in grid[row])]
        columns = [column for column in range(width) if all(grid[row][column] == color for row in range(height))]
        if len(rows) == 1 and len(columns) == 1:
            candidates.append((color, rows[0], columns[0]))
    if len(candidates) != 1:
        raise Undefined("one cross scaffold is required")
    scaffold, axis_row, axis_column = candidates[0]
    output = _plain(grid)
    payload = [
        (row, column, grid[row][column])
        for row in range(height)
        for column in range(width)
        if grid[row][column] not in (background, scaffold)
    ]
    if not payload:
        raise Undefined("cross has no payload")
    for row, column, color in payload:
        for target_row, target_column in (
            (row, column),
            (2 * axis_row - row, column),
            (row, 2 * axis_column - column),
            (2 * axis_row - row, 2 * axis_column - column),
        ):
            if not (0 <= target_row < height and 0 <= target_column < width):
                continue
            if output[target_row][target_column] not in (background, color):
                raise Undefined("cross reflection conflicts")
            output[target_row][target_column] = color
    return _freeze(output), {"axes": 2, "payload_cells": len(payload), "clipped": True}


def _reflect_and_swap_across_separator(grid: Grid) -> tuple[Grid, dict[str, Any]]:
    background = _background(grid)
    height, width = _shape(grid)
    lines: list[tuple[int, str, int]] = []
    for color in sorted({cell for row in grid for cell in row} - {background}):
        rows = [row for row in range(height) if all(cell == color for cell in grid[row])]
        columns = [column for column in range(width) if all(grid[row][column] == color for row in range(height))]
        if len(rows) + len(columns) == 1:
            lines.append((color, "rows", rows[0]) if rows else (color, "columns", columns[0]))
    if len(lines) != 1:
        raise Undefined("one separator axis is required")
    scaffold, axis, index = lines[0]
    colors = sorted({cell for row in grid for cell in row} - {background, scaffold})
    if len(colors) != 2:
        raise Undefined("separator payload needs two colors")
    payload = [
        (row, column, grid[row][column])
        for row in range(height)
        for column in range(width)
        if grid[row][column] in colors
    ]
    sides = {
        -1 if (row if axis == "rows" else column) < index else 1
        if (row if axis == "rows" else column) > index
        else 0
        for row, column, _ in payload
    }
    if len(sides) != 1 or 0 in sides:
        raise Undefined("payload must lie on one side")
    output = _plain(grid)
    left, right = colors
    for row, column, color in payload:
        output[row][column] = right if color == left else left
        target = (2 * index - row, column) if axis == "rows" else (row, 2 * index - column)
        if not (0 <= target[0] < height and 0 <= target[1] < width):
            raise Undefined("reflected payload leaves the canvas")
        if output[target[0]][target[1]] not in (background, color):
            raise Undefined("reflected payload collides")
        output[target[0]][target[1]] = color
    return _freeze(output), {"axis": axis, "payload_cells": len(payload), "palette_involution": True}


def _instantiate_scaled_keyed_template(grid: Grid, limits: Limits) -> tuple[Grid, dict[str, Any]]:
    background = _background(grid)
    height, width = _shape(grid)
    mixed = _components(grid, background, connectivity=8, monochrome=False)
    templates: list[tuple[frozenset[Cell], int, frozenset[int], int, int, int]] = []
    for _, cells in mixed:
        counts = Counter(grid[row][column] for row, column in cells)
        ordered = counts.most_common()
        if not (
            len(counts) == 3
            and ordered[0][1] >= 3
            and ordered[0][1] > ordered[1][1]
            and ordered[1][1] == ordered[2][1] == 1
        ):
            continue
        r0, r1, c0, c1 = _bbox(cells)
        if r1 - r0 != c1 - c0 or r1 - r0 + 1 < 2:
            continue
        templates.append(
            (cells, ordered[0][0], frozenset(counts) - {ordered[0][0]}, r0, c0, r1 - r0 + 1)
        )
    if len(templates) != 1:
        raise Undefined("one square keyed template is required")
    template_cells, scaffold, key_colors, top, left, side = templates[0]
    template = {
        (row - top, column - left): grid[row][column]
        for row in range(top, top + side)
        for column in range(left, left + side)
    }
    if any(sum(color == key for color in template.values()) != 1 for key in key_colors):
        raise Undefined("template keys are not singleton roles")
    monochrome = _components(grid, background, connectivity=4, monochrome=True)
    external: list[tuple[int, frozenset[Cell], int, int, int]] = []
    for color, cells in monochrome:
        if color not in key_colors or cells <= template_cells:
            continue
        square = _solid_square(cells)
        if square is None:
            raise Undefined("external key is not a solid scale block")
        external.append((int(color), cells, *square))
    if len(external) < len(key_colors) or len(external) % len(key_colors):
        raise Undefined("external key blocks do not form complete packets")
    if set(key_colors) != {color for color, *_ in external}:
        raise Undefined("external key palette is incomplete")
    placements: dict[str, tuple[dict[Cell, int], frozenset[frozenset[Cell]]]] = {}
    for operation in _D4:
        transformed = {
            _transform_cell(row, column, side, side, operation): color
            for (row, column), color in template.items()
        }
        for anchor_color, anchor_cells, anchor_row, anchor_column, scale in external:
            anchor_locations = [point for point, color in transformed.items() if color == anchor_color]
            if len(anchor_locations) != 1:
                continue
            local_anchor = anchor_locations[0]
            render_top = anchor_row - local_anchor[0] * scale
            render_left = anchor_column - local_anchor[1] * scale
            mapped: dict[Cell, int] = {}
            consumed: list[frozenset[Cell]] = []
            valid = True
            for (local_row, local_column), color in transformed.items():
                block = frozenset(
                    (
                        render_top + local_row * scale + dr,
                        render_left + local_column * scale + dc,
                    )
                    for dr in range(scale)
                    for dc in range(scale)
                )
                if any(not (0 <= row < height and 0 <= column < width) for row, column in block):
                    valid = False
                    break
                if color in key_colors:
                    matches = [
                        cells
                        for candidate_color, cells, *_ in external
                        if candidate_color == color and cells == block
                    ]
                    if len(matches) != 1:
                        valid = False
                        break
                    consumed.append(matches[0])
                elif color == scaffold:
                    if any(grid[row][column] != background for row, column in block):
                        valid = False
                        break
                elif color == background:
                    if any(grid[row][column] != background for row, column in block):
                        valid = False
                        break
                else:
                    valid = False
                    break
                mapped.update({point: color for point in block})
            if valid:
                key = _digest(sorted((list(point), color) for point, color in mapped.items()))
                placements[key] = (mapped, frozenset(consumed))
    target = frozenset(cells for _, cells, *_ in external)
    placement_values = list(placements.values())
    renderings: dict[str, Grid] = {}

    def exact_cover(start: int, used: frozenset[frozenset[Cell]], maps: tuple[dict[Cell, int], ...]) -> None:
        if used == target:
            output = _plain(grid)
            for mapped in maps:
                for (row, column), color in mapped.items():
                    if color != background:
                        if output[row][column] not in (background, color):
                            return
                        output[row][column] = color
            frozen = _freeze(output)
            renderings[_digest(_plain(frozen))] = frozen
            if len(renderings) > limits.max_renderings:
                raise Undefined("rendering cap exhausted")
            return
        for index in range(start, len(placement_values)):
            mapped, consumed = placement_values[index]
            if consumed & used:
                continue
            exact_cover(index + 1, used | consumed, maps + (mapped,))

    exact_cover(0, frozenset(), ())
    if len(renderings) != 1:
        raise Undefined("scaled keyed template behavior is absent or ambiguous")
    return next(iter(renderings.values())), {
        "template_side": side,
        "external_key_blocks": len(external),
        "behavior_classes": 1,
    }


def _complete_scaled_exemplar_motifs(grid: Grid) -> tuple[Grid, dict[str, Any]]:
    background = _background(grid)
    height, width = _shape(grid)
    groups = _components(grid, background, connectivity=4, monochrome=False)
    exemplars: list[tuple[frozenset[Cell], int, int]] = []
    for _, cells in groups:
        counts = Counter(grid[row][column] for row, column in cells)
        singleton_colors = [color for color, count in counts.items() if count == 1]
        if len(counts) == 2 and len(singleton_colors) == 1 and max(counts.values()) >= 4:
            marker = singleton_colors[0]
            paint = next(color for color in counts if color != marker)
            exemplars.append((cells, marker, paint))
    if len(exemplars) != 1:
        raise Undefined("one complete exemplar motif is required")
    exemplar, marker, exemplar_paint = exemplars[0]
    r0, r1, c0, c1 = _bbox(exemplar)
    exemplar_map = {
        (row - r0, column - c0): grid[row][column] for row, column in exemplar
    }
    marker_locations = [point for point, color in exemplar_map.items() if color == marker]
    if len(marker_locations) != 1:
        raise Undefined("exemplar marker role is ambiguous")
    marker_local = marker_locations[0]
    output = _plain(grid)
    completed = 0
    for _, cells in groups:
        if cells == exemplar:
            continue
        by_color: dict[int, set[Cell]] = defaultdict(set)
        for row, column in cells:
            by_color[grid[row][column]].add((row, column))
        if marker not in by_color or len(by_color) != 2:
            raise Undefined("target motif does not share the exemplar marker")
        paint = next(color for color in by_color if color != marker)
        marker_square = _solid_square(by_color[marker])
        paint_square = _solid_square(by_color[paint])
        if marker_square is None or paint_square is None or marker_square[2] != paint_square[2]:
            raise Undefined("target motif does not expose equal scale blocks")
        scale = marker_square[2]
        render_top = marker_square[0] - marker_local[0] * scale
        render_left = marker_square[1] - marker_local[1] * scale
        if not any(
            color == exemplar_paint
            and paint_square[0] == render_top + local_row * scale
            and paint_square[1] == render_left + local_column * scale
            for (local_row, local_column), color in exemplar_map.items()
        ):
            raise Undefined("target paint does not bind an exemplar cell")
        for (local_row, local_column), source_color in exemplar_map.items():
            target_color = marker if source_color == marker else paint
            for dr in range(scale):
                for dc in range(scale):
                    row = render_top + local_row * scale + dr
                    column = render_left + local_column * scale + dc
                    if not (0 <= row < height and 0 <= column < width):
                        raise Undefined("scaled exemplar leaves the canvas")
                    if output[row][column] not in (background, target_color):
                        raise Undefined("scaled exemplar collides")
                    output[row][column] = target_color
        completed += 1
    if not completed:
        raise Undefined("no incomplete exemplar target")
    return _freeze(output), {"completed_targets": completed, "orientation": "exemplar-local"}


def _copy_corresponding_panels(grid: Grid) -> tuple[Grid, dict[str, Any]]:
    background = _background(grid)
    height, width = _shape(grid)
    candidates: list[tuple[int, tuple[int, ...], tuple[int, ...]]] = []
    for color in sorted({cell for row in grid for cell in row} - {background}):
        rows = tuple(row for row in range(height) if all(cell == color for cell in grid[row]))
        columns = tuple(
            column for column in range(width) if all(grid[row][column] == color for row in range(height))
        )
        if (rows or columns):
            candidates.append((color, rows, columns))
    if len(candidates) != 1:
        raise Undefined("one centered panel scaffold is required")
    scaffold, rows, columns = candidates[0]
    row_boundaries = (-1, *rows, height)
    column_boundaries = (-1, *columns, width)
    row_ranges = tuple(
        range(left + 1, right) for left, right in zip(row_boundaries, row_boundaries[1:])
    )
    column_ranges = tuple(
        range(left + 1, right)
        for left, right in zip(column_boundaries, column_boundaries[1:])
    )
    if len({len(value) for value in row_ranges}) != 1 or len({len(value) for value in column_ranges}) != 1:
        raise Undefined("panel frames are not homologous")
    panel_height, panel_width = len(row_ranges[0]), len(column_ranges[0])
    output = _plain(grid)
    painted = 0
    for local_row in range(panel_height):
        for local_column in range(panel_width):
            homologues = [
                (row_range.start + local_row, column_range.start + local_column)
                for row_range in row_ranges
                for column_range in column_ranges
            ]
            values = {
                grid[row][column]
                for row, column in homologues
                if grid[row][column] != background
            }
            if len(values) > 1:
                raise Undefined("homologous panel cells disagree")
            if values:
                value = next(iter(values))
                if value == scaffold:
                    raise Undefined("scaffold leaked into a panel")
                for row, column in homologues:
                    if output[row][column] == background:
                        output[row][column] = value
                        painted += 1
    if not painted:
        raise Undefined("panel correspondence adds nothing")
    return _freeze(output), {
        "panel_rows": len(row_ranges),
        "panel_columns": len(column_ranges),
        "painted_cells": painted,
        "reflection": False,
    }


def _execute_internal(
    program: Mapping[str, Any], grid: Grid, limits: Limits | None = None
) -> tuple[Grid, dict[str, Any]]:
    if not isinstance(program, Mapping) or program.get("schema") != SCHEMA:
        raise Undefined("invalid relational-geometry program")
    bounds = limits or Limits()
    operator = program.get("operator")
    if operator == "reflect_template_to_aligned_singletons":
        return _reflect_template_to_aligned_singletons(grid)
    if operator == "project_objects_away_from_anchor":
        return _project_objects_away_from_anchor(grid)
    if operator == "relocate_keyed_templates":
        return _relocate_keyed_templates(grid, bounds)
    if operator == "swap_shape_species":
        return _swap_shape_species(grid)
    if operator == "mirror_complete_about_cross":
        return _mirror_complete_about_cross(grid)
    if operator == "reflect_and_swap_across_separator":
        return _reflect_and_swap_across_separator(grid)
    if operator == "instantiate_scaled_keyed_template":
        return _instantiate_scaled_keyed_template(grid, bounds)
    if operator == "complete_scaled_exemplar_motifs":
        return _complete_scaled_exemplar_motifs(grid)
    if operator == "copy_corresponding_panels":
        return _copy_corresponding_panels(grid)
    raise Undefined("unknown relational-geometry operator")


def execute_program(program: Mapping[str, Any], value: Any) -> list[list[int]]:
    """Execute one serialized task-identity-free geometry program."""

    limits = Limits()
    grid = _grid(value, limits)
    return _plain(_execute_internal(program, grid, limits)[0])


def replay_program(program: Mapping[str, Any], value: Any) -> dict[str, Any]:
    """Replay lift, relational construction, and raster rendering stages."""

    limits = Limits()
    grid = _grid(value, limits)
    output, receipt = _execute_internal(program, grid, limits)
    lifted = {
        "kind": "intrinsic_relational_geometry",
        "shape": list(_shape(grid)),
        "coordinate_identity": "object_local",
    }
    applied = {"operator": program["operator"], "receipt": receipt}
    return {
        "output": _plain(output),
        "stages": [
            {"name": "lift-object-frames", "input": _plain(grid), "output": lifted},
            {"name": "apply-relational-construction", "input": lifted, "output": applied},
            {"name": "render-with-geometric-lineage", "input": applied, "output": _plain(output)},
        ],
    }


def _programs() -> tuple[dict[str, Any], ...]:
    lengths = {
        "reflect_template_to_aligned_singletons": 15,
        "project_objects_away_from_anchor": 13,
        "relocate_keyed_templates": 18,
        "swap_shape_species": 12,
        "mirror_complete_about_cross": 10,
        "reflect_and_swap_across_separator": 12,
        "instantiate_scaled_keyed_template": 18,
        "complete_scaled_exemplar_motifs": 16,
        "copy_corresponding_panels": 11,
    }
    return tuple(
        sorted(
            (
                {"schema": SCHEMA, "operator": operator, "description_length": length}
                for operator, length in lengths.items()
            ),
            key=_canonical,
        )
    )


def _behavior(
    program: Mapping[str, Any], grids: Sequence[Grid], limits: Limits
) -> tuple[Grid, ...]:
    return tuple(_execute_internal(program, grid, limits)[0] for grid in grids)


def _exact_programs(
    pairs: Sequence[Pair], probes: Sequence[Grid], limits: Limits
) -> tuple[dict[str, Any], ...]:
    exact: list[dict[str, Any]] = []
    calls = 0
    for program in _programs():
        try:
            outputs: list[Grid] = []
            for source, _ in pairs:
                outputs.append(_execute_internal(program, source, limits)[0])
                calls += 1
            for probe in probes:
                _execute_internal(program, probe, limits)
                calls += 1
            if calls > limits.max_executor_calls:
                raise Undefined("executor call cap exhausted")
        except (Undefined, TypeError, ValueError, KeyError, IndexError, ZeroDivisionError):
            continue
        if tuple(outputs) == tuple(target for _, target in pairs):
            exact.append(program)
    return tuple(sorted(exact, key=lambda value: (int(value["description_length"]), _canonical(value))))


def _loo(demonstrations: Sequence[Pair], limits: Limits) -> tuple[bool, list[dict[str, Any]]]:
    witnesses: list[dict[str, Any]] = []
    for held_index, (source, target) in enumerate(demonstrations):
        subset = tuple(pair for index, pair in enumerate(demonstrations) if index != held_index)
        programs = _exact_programs(subset, (source,), limits)
        behaviors: dict[str, tuple[Grid, ...]] = {}
        for program in programs:
            try:
                output = _behavior(program, (source,), limits)
            except Undefined:
                continue
            behaviors[_digest([_plain(grid) for grid in output])] = output
        if len(behaviors) != 1 or next(iter(behaviors.values())) != (target,):
            return False, witnesses
        witnesses.append(
            {
                "held_out_index": held_index,
                "proposal_demo_count": len(subset),
                "held_out_behavior_classes": 1,
                "held_out_exact": True,
                "held_out_output_hash": _digest(_plain(target)),
            }
        )
    return True, witnesses


def _swap_grid(grid: Grid, left: int, right: int) -> Grid:
    return tuple(
        tuple(right if cell == left else left if cell == right else cell for cell in row)
        for row in grid
    )


def _gauge(
    program: Mapping[str, Any], demonstrations: Sequence[Pair], limits: Limits
) -> tuple[bool, int, int]:
    d4_checks = 0
    palette_checks = 0
    for source, target in demonstrations:
        for operation in _D4:
            d4_checks += 1
            if d4_checks + palette_checks > limits.max_gauge_checks:
                return False, d4_checks, palette_checks
            try:
                actual = _execute_internal(program, _d4(source, operation), limits)[0]
            except Undefined:
                return False, d4_checks, palette_checks
            if actual != _d4(target, operation):
                return False, d4_checks, palette_checks
        colors = sorted({cell for row in source for cell in row} | {cell for row in target for cell in row})
        absent = next((color for color in range(10) if color not in colors), None)
        swaps = list(itertools.combinations(colors, 2))
        if absent is not None:
            swaps.extend((color, absent) for color in colors)
        for left, right in swaps:
            palette_checks += 1
            if d4_checks + palette_checks > limits.max_gauge_checks:
                return False, d4_checks, palette_checks
            try:
                actual = _execute_internal(program, _swap_grid(source, left, right), limits)[0]
            except Undefined:
                return False, d4_checks, palette_checks
            if actual != _swap_grid(target, left, right):
                return False, d4_checks, palette_checks
    return True, d4_checks, palette_checks


def compile_task(task: Any, limits: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    """Compile one unique proof-carrying geometry behavior or abstain."""

    try:
        bounds = Limits.from_value(limits)
        demonstrations, tests = _sanitize(task, bounds)
    except (Undefined, TypeError, ValueError, KeyError):
        return []
    programs = _programs()
    if len(programs) > bounds.max_programs:
        return []
    exact = _exact_programs(demonstrations, tests, bounds)
    if not exact:
        return []
    behaviors: dict[str, list[tuple[dict[str, Any], tuple[Grid, ...]]]] = {}
    for program in exact:
        try:
            outputs = _behavior(program, tests, bounds)
        except Undefined:
            continue
        behavior_hash = _digest([_plain(grid) for grid in outputs])
        behaviors.setdefault(behavior_hash, []).append((program, outputs))
    if len(behaviors) != 1:
        return []
    behavior_hash, equivalent = next(iter(sorted(behaviors.items())))
    equivalent.sort(key=lambda item: (int(item[0]["description_length"]), _canonical(item[0])))
    representative, outputs = equivalent[0]
    loo_ok, loo_witnesses = _loo(demonstrations, bounds)
    if not loo_ok:
        return []
    gauge_ok, d4_checks, palette_checks = _gauge(representative, demonstrations, bounds)
    if not gauge_ok:
        return []
    try:
        train_outputs = _behavior(
            representative, tuple(source for source, _ in demonstrations), bounds
        )
    except Undefined:
        return []
    if train_outputs != tuple(target for _, target in demonstrations):
        return []
    candidate = {
        "family": "relational_geometry_compiler",
        "program": json.loads(_canonical(representative)),
        "train_outputs": [_plain(grid) for grid in train_outputs],
        "test_outputs": [_plain(grid) for grid in outputs],
        "complexity": int(representative["description_length"]),
        "evidence": {
            "intrinsic_object_frames": True,
            "relational_geometry": True,
            "all_demonstrations_exact": True,
            "exact_replay": True,
            "leave_one_demo_out_reinduction": True,
            "leave_one_out_witnesses": loo_witnesses,
            "enumeration_complete": True,
            "programs_enumerated": len(programs),
            "exact_programs": len(exact),
            "full_test_behavior_classes": len(behaviors),
            "full_test_behavior_hash": behavior_hash,
            "equivalent_programs": len(equivalent),
            "d4_covariance_checks": d4_checks,
            "palette_covariance_checks": palette_checks,
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
