"""Task-local relational palette flow for PR-LASM Block 14.

This entrant treats colors as values carried by geometric roles rather than
as globally fixed labels.  Its finite grammar contains five independently
replayable operators:

* an ordered, sequential palette table;
* a corner key projected into spatial bins;
* a magnified binary mask stamped into lattice tiles;
* a dense palette matrix projected onto a grid of repeated glyphs; and
* a marker map aligned to a constellation of monochrome objects.

Every candidate must exactly replay all demonstrations, survive genuine
leave-one-demonstration-out re-induction, and induce one unique test behavior.
Test records are read through their ``input`` member only.  Task identifiers,
solutions, scores, result stores, and corpus fingerprints are never inputs.

Author: Komorebi P.
"""
from __future__ import annotations

from collections import Counter, deque
from collections.abc import Mapping, Sequence
from fractions import Fraction
import hashlib
import itertools
import json
from typing import Any, Callable, Iterable


Grid = tuple[tuple[int, ...], ...]
Point = tuple[int, int]
Pair = tuple[Grid, Grid]
SCHEMA = "komorebi.pr_lasm.block14.relational_palette_flow.v1"
AUTHOR = "Komorebi P."


class Undefined(ValueError):
    """A structural role or a requested replay is not uniquely defined."""


def _canonical(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def _grid(value: Any) -> Grid:
    if (
        not isinstance(value, Sequence)
        or isinstance(value, (str, bytes, bytearray))
        or not value
        or len(value) > 30
    ):
        raise Undefined("invalid grid height")
    rows: list[tuple[int, ...]] = []
    width: int | None = None
    for raw_row in value:
        if (
            not isinstance(raw_row, Sequence)
            or isinstance(raw_row, (str, bytes, bytearray))
            or not raw_row
            or len(raw_row) > 30
        ):
            raise Undefined("invalid grid row")
        row: list[int] = []
        for cell in raw_row:
            if isinstance(cell, bool) or not isinstance(cell, int) or not 0 <= cell <= 9:
                raise Undefined("invalid ARC color")
            row.append(int(cell))
        if width is None:
            width = len(row)
        elif len(row) != width:
            raise Undefined("ragged grid")
        rows.append(tuple(row))
    return tuple(rows)


def _plain(grid: Grid) -> list[list[int]]:
    return [list(row) for row in grid]


def _background(grid: Grid) -> int:
    counts = Counter(cell for row in grid for cell in row)
    maximum = max(counts.values())
    winners = [color for color, count in counts.items() if count == maximum]
    if len(winners) != 1:
        raise Undefined("background role is tied")
    return winners[0]


def _bbox(points: Iterable[Point]) -> tuple[int, int, int, int]:
    cells = tuple(points)
    if not cells:
        raise Undefined("empty point set")
    return (
        min(row for row, _ in cells),
        max(row for row, _ in cells),
        min(column for _, column in cells),
        max(column for _, column in cells),
    )


def _normalized(points: Iterable[Point]) -> tuple[Point, ...]:
    cells = tuple(points)
    top, _, left, _ = _bbox(cells)
    return tuple(sorted((row - top, column - left) for row, column in cells))


def _components(
    grid: Grid,
    points: Iterable[Point],
    *,
    monochrome: bool,
    connectivity: int = 4,
) -> tuple[frozenset[Point], ...]:
    if connectivity not in {4, 8}:
        raise Undefined("unsupported connectivity")
    remaining = set(points)
    answer: list[frozenset[Point]] = []
    while remaining:
        seed = min(remaining)
        remaining.remove(seed)
        component = {seed}
        queue = deque([seed])
        while queue:
            row, column = queue.popleft()
            neighbors = [
                (row - 1, column),
                (row + 1, column),
                (row, column - 1),
                (row, column + 1),
            ]
            if connectivity == 8:
                neighbors.extend(
                    (
                        (row - 1, column - 1),
                        (row - 1, column + 1),
                        (row + 1, column - 1),
                        (row + 1, column + 1),
                    )
                )
            for neighbor in neighbors:
                if neighbor not in remaining:
                    continue
                if monochrome and grid[neighbor[0]][neighbor[1]] != grid[row][column]:
                    continue
                remaining.remove(neighbor)
                component.add(neighbor)
                queue.append(neighbor)
        answer.append(frozenset(component))
    return tuple(sorted(answer, key=lambda cells: (_bbox(cells), len(cells), tuple(cells))))


def _foreground_components(
    grid: Grid, *, monochrome: bool, connectivity: int = 4
) -> tuple[frozenset[Point], ...]:
    background = _background(grid)
    return _components(
        grid,
        (
            (row, column)
            for row, values in enumerate(grid)
            for column, value in enumerate(values)
            if value != background
        ),
        monochrome=monochrome,
        connectivity=connectivity,
    )


def _transform_square(matrix: tuple[tuple[int, ...], ...], transform: str) -> tuple[tuple[int, ...], ...]:
    if not matrix or any(len(row) != len(matrix) for row in matrix):
        raise Undefined("D4 palette transform requires a square matrix")
    value = matrix
    if transform.startswith("mirror_"):
        value = tuple(tuple(reversed(row)) for row in value)
        transform = transform.removeprefix("mirror_")
    turns = {"r0": 0, "r1": 1, "r2": 2, "r3": 3}.get(transform)
    if turns is None:
        raise Undefined("unknown D4 palette transform")
    for _ in range(turns):
        value = tuple(tuple(value[len(value) - 1 - row][column] for row in range(len(value))) for column in range(len(value)))
    return value


_D4 = ("r0", "r1", "r2", "r3", "mirror_r0", "mirror_r1", "mirror_r2", "mirror_r3")


def _find_ordered_table(grid: Grid, axis: str) -> tuple[tuple[Point, ...], tuple[tuple[int, int], ...]]:
    background = _background(grid)
    height, width = len(grid), len(grid[0])
    outer = height if axis == "rows" else width
    inner = width if axis == "rows" else height
    candidates: list[tuple[int, tuple[Point, ...], tuple[tuple[int, int], ...]]] = []
    for fixed in range(inner - 1):
        valid: list[bool] = []
        for moving in range(outer):
            first = grid[moving][fixed] if axis == "rows" else grid[fixed][moving]
            second = grid[moving][fixed + 1] if axis == "rows" else grid[fixed + 1][moving]
            valid.append(first != background and second != background and first != second)
        start = 0
        while start < outer:
            if not valid[start]:
                start += 1
                continue
            stop = start
            while stop < outer and valid[stop]:
                stop += 1
            if stop - start >= 3:
                if axis == "rows":
                    cells = tuple(
                        (moving, column)
                        for moving in range(start, stop)
                        for column in (fixed, fixed + 1)
                    )
                    pairs = tuple((grid[moving][fixed], grid[moving][fixed + 1]) for moving in range(start, stop))
                else:
                    cells = tuple(
                        (row, moving)
                        for moving in range(start, stop)
                        for row in (fixed, fixed + 1)
                    )
                    pairs = tuple((grid[fixed][moving], grid[fixed + 1][moving]) for moving in range(start, stop))
                palette = {color for pair in pairs for color in pair}
                if len(palette) >= 3:
                    candidates.append((stop - start, cells, pairs))
            start = stop
    if not candidates:
        raise Undefined("no ordered palette table")
    maximum = max(length for length, _, _ in candidates)
    best = [(cells, pairs) for length, cells, pairs in candidates if length == maximum]
    if len(best) != 1:
        raise Undefined("ordered palette table is ambiguous")
    return best[0]


def _execute_ordered_table(program: Mapping[str, Any], grid: Grid) -> Grid:
    axis = str(program.get("axis"))
    order = str(program.get("order"))
    direction = str(program.get("direction"))
    if axis not in {"rows", "columns"} or order not in {"forward", "reverse"} or direction not in {"forward", "reverse"}:
        raise Undefined("invalid ordered-table program")
    cells, raw_pairs = _find_ordered_table(grid, axis)
    pairs = raw_pairs if order == "forward" else tuple(reversed(raw_pairs))
    if direction == "reverse":
        pairs = tuple((target, source) for source, target in pairs)
    protected = set(cells)
    output = [list(row) for row in grid]
    for source, target in pairs:
        for row in range(len(output)):
            for column in range(len(output[0])):
                if (row, column) not in protected and output[row][column] == source:
                    output[row][column] = target
    return tuple(tuple(row) for row in output)


def _corner_decompositions(grid: Grid, bins: int) -> list[dict[str, Any]]:
    height, width = len(grid), len(grid[0])
    if bins < 2 or height <= bins or width <= bins:
        return []
    result: list[dict[str, Any]] = []
    for key_bottom in (False, True):
        for key_right in (False, True):
            key_rows = tuple(range(height - bins, height)) if key_bottom else tuple(range(bins))
            key_columns = tuple(range(width - bins, width)) if key_right else tuple(range(bins))
            main_rows = tuple(range(height - bins)) if key_bottom else tuple(range(bins, height))
            main_columns = tuple(range(width - bins)) if key_right else tuple(range(bins, width))
            if len(main_rows) % bins or len(main_columns) % bins:
                continue
            cross = [grid[row][column] for row in key_rows for column in main_columns]
            cross += [grid[row][column] for row in main_rows for column in key_columns]
            if not cross or len(set(cross)) != 1:
                continue
            separator = cross[0]
            main_values = [grid[row][column] for row in main_rows for column in main_columns]
            counts = Counter(main_values)
            maximum = max(counts.values())
            backgrounds = [color for color, count in counts.items() if count == maximum]
            if len(backgrounds) != 1:
                continue
            background = backgrounds[0]
            foregrounds = set(main_values) - {background}
            if len(foregrounds) != 1 or separator in {background, *foregrounds}:
                continue
            key = tuple(tuple(grid[row][column] for column in key_columns) for row in key_rows)
            if len({value for row in key for value in row}) < 2 or separator in {value for row in key for value in row}:
                continue
            result.append(
                {
                    "key": key,
                    "main_rows": main_rows,
                    "main_columns": main_columns,
                    "foreground": next(iter(foregrounds)),
                }
            )
    return result


def _execute_corner_projection(program: Mapping[str, Any], grid: Grid) -> Grid:
    bins = int(program.get("bins", 0))
    transform = str(program.get("transform"))
    decompositions = _corner_decompositions(grid, bins)
    if len(decompositions) != 1:
        raise Undefined("corner palette decomposition is ambiguous")
    item = decompositions[0]
    key = _transform_square(item["key"], transform)
    rows: tuple[int, ...] = item["main_rows"]
    columns: tuple[int, ...] = item["main_columns"]
    foreground = int(item["foreground"])
    output = [list(row) for row in grid]
    for row_index, row in enumerate(rows):
        for column_index, column in enumerate(columns):
            if grid[row][column] == foreground:
                key_row = min(bins - 1, row_index * bins // len(rows))
                key_column = min(bins - 1, column_index * bins // len(columns))
                output[row][column] = key[key_row][key_column]
    return tuple(tuple(row) for row in output)


def _lattice_roles(grid: Grid, tile: int, gap: int, scale: int) -> dict[str, Any]:
    pitch = tile + gap
    height, width = len(grid), len(grid[0])
    if tile < 2 or gap != 1 or scale < 2 or height < tile or width < tile:
        raise Undefined("invalid lattice parameters")
    if (height + gap) % pitch or (width + gap) % pitch:
        raise Undefined("grid does not close on lattice pitch")
    colors = set(cell for row in grid for cell in row)
    divider_positions = [
        (row, column)
        for row in range(height)
        for column in range(width)
        if row % pitch >= tile or column % pitch >= tile
    ]
    separator_counts = Counter(grid[row][column] for row, column in divider_positions)
    maximum_separator = max(separator_counts.values())
    separators = [
        color
        for color, count in separator_counts.items()
        if count == maximum_separator and count * 4 >= len(divider_positions) * 3
    ]
    if len(separators) != 1:
        raise Undefined("lattice separator is ambiguous")
    candidates: list[dict[str, Any]] = []
    for separator in separators:
        interior_values = [
            grid[row][column]
            for row in range(height)
            for column in range(width)
            if row % pitch < tile and column % pitch < tile and grid[row][column] != separator
        ]
        background_counts = Counter(interior_values)
        maximum_background = max(background_counts.values())
        backgrounds = [
            color for color, count in background_counts.items() if count == maximum_background
        ]
        if len(backgrounds) != 1:
            continue
        background = backgrounds[0]
        regular_interior: list[int] = []
        exceptional: set[int] = set()
        for row in range(height):
            for column in range(width):
                value = grid[row][column]
                divider = row % pitch >= tile or column % pitch >= tile
                if divider:
                    if value != separator:
                        exceptional.add(value)
                else:
                    if value not in {background, separator}:
                        regular_interior.append(value)
        content_counts = Counter(regular_interior)
        if not content_counts:
            continue
        content, count = content_counts.most_common(1)[0]
        if len(content_counts) != 2:
            # One ordinary content color and one special mask color must
            # occur inside tile interiors.
            continue
        special_candidates = set(content_counts) - {content}
        special_candidates |= exceptional - {separator, background, content}
        if len(special_candidates) != 1:
            continue
        special = next(iter(special_candidates))
        special_cells = {(row, column) for row in range(height) for column in range(width) if grid[row][column] == special}
        if not special_cells:
            continue
        top, bottom, left, right = _bbox(special_cells)
        # The magnified reference is allowed to overwrite and locally displace
        # divider ink.  Away from its one-cell halo, the lattice alphabet must
        # remain exact.
        valid = True
        for row in range(height):
            for column in range(width):
                if top - scale <= row <= bottom + scale and left - scale <= column <= right + scale:
                    continue
                value = grid[row][column]
                divider = row % pitch >= tile or column % pitch >= tile
                allowed = {separator} if divider else {background, content}
                if value not in allowed:
                    valid = False
                    break
            if not valid:
                break
        if not valid:
            continue
        box_height, box_width = bottom - top + 1, right - left + 1
        if box_height % scale or box_width % scale or box_height // scale > tile or box_width // scale > tile:
            continue
        mask: set[Point] = set()
        block_valid = True
        for block_row in range(box_height // scale):
            for block_column in range(box_width // scale):
                block = {
                    (top + block_row * scale + dr, left + block_column * scale + dc)
                    for dr in range(scale)
                    for dc in range(scale)
                }
                occupied = len(block & special_cells)
                if occupied not in {0, scale * scale}:
                    block_valid = False
                elif occupied:
                    mask.add((block_row, block_column))
        if not block_valid or not mask or len(mask) * scale * scale != len(special_cells):
            continue
        candidates.append(
            {
                "background": background,
                "separator": separator,
                "content": content,
                "special": special,
                "special_cells": special_cells,
                "special_bbox": (top, bottom, left, right),
                "mask": frozenset(mask),
            }
        )
    if len(candidates) != 1:
        raise Undefined("lattice roles are ambiguous")
    return candidates[0]


def _execute_magnified_mask(program: Mapping[str, Any], grid: Grid) -> Grid:
    tile = int(program.get("tile", 0))
    gap = int(program.get("gap", 0))
    scale = int(program.get("scale", 0))
    roles = _lattice_roles(grid, tile, gap, scale)
    pitch = tile + gap
    output = [list(row) for row in grid]
    top, bottom, left, right = roles["special_bbox"]
    for tile_top in range(0, len(grid), pitch):
        for tile_left in range(0, len(grid[0]), pitch):
            tile_cells = {
                (tile_top + row, tile_left + column)
                for row in range(tile)
                for column in range(tile)
            }
            if tile_cells & roles["special_cells"]:
                continue
            # Exclude any ordinary tile whose interior overlaps the reference
            # bounding box, even if a sparse mask leaves holes in the box.
            if not (
                tile_top + tile - 1 < top
                or tile_top > bottom
                or tile_left + tile - 1 < left
                or tile_left > right
            ):
                continue
            points = [(tile_top + row, tile_left + column) for row, column in roles["mask"]]
            if all(grid[row][column] == roles["content"] for row, column in points):
                for row, column in points:
                    output[row][column] = roles["special"]
    return tuple(tuple(row) for row in output)


def _monochrome_components_by_color(grid: Grid, color: int) -> tuple[frozenset[Point], ...]:
    return _components(
        grid,
        (
            (row, column)
            for row, values in enumerate(grid)
            for column, value in enumerate(values)
            if value == color
        ),
        monochrome=True,
    )


def _glyph_key_decompositions(grid: Grid) -> list[dict[str, Any]]:
    background = _background(grid)
    colors = sorted({cell for row in grid for cell in row} - {background})
    height, width = len(grid), len(grid[0])
    result: list[dict[str, Any]] = []
    for source in colors:
        components = _monochrome_components_by_color(grid, source)
        groups: dict[tuple[Point, ...], list[frozenset[Point]]] = {}
        for component in components:
            groups.setdefault(_normalized(component), []).append(component)
        for shape, cohort in groups.items():
            if len(cohort) < 4 or len(cohort) != len(components):
                continue
            tops = sorted({_bbox(component)[0] for component in cohort})
            lefts = sorted({_bbox(component)[2] for component in cohort})
            if len(tops) < 2 or len(lefts) < 2 or len(tops) * len(lefts) != len(cohort):
                continue
            by_anchor = {(_bbox(component)[0], _bbox(component)[2]): component for component in cohort}
            if set(by_anchor) != set(itertools.product(tops, lefts)):
                continue
            glyph_cells = set().union(*cohort)
            rows, columns = len(tops), len(lefts)
            key_candidates: list[tuple[tuple[tuple[int, ...], ...], set[Point]]] = []
            for key_rows, key_columns in {(rows, columns), (columns, rows)}:
                for top in range(height - key_rows + 1):
                    for left in range(width - key_columns + 1):
                        cells = {
                            (row, column)
                            for row in range(top, top + key_rows)
                            for column in range(left, left + key_columns)
                        }
                        if cells & glyph_cells:
                            continue
                        values = [grid[row][column] for row, column in cells]
                        if background in values or source in values or len(set(values)) < 2:
                            continue
                        # The table is a maximal dense island, not an arbitrary
                        # subrectangle cut out of a larger foreground object.
                        border = set()
                        for row, column in cells:
                            border.update(((row - 1, column), (row + 1, column), (row, column - 1), (row, column + 1)))
                        border -= cells
                        if any(
                            0 <= row < height
                            and 0 <= column < width
                            and grid[row][column] != background
                            for row, column in border
                        ):
                            continue
                        key = tuple(
                            tuple(grid[row][column] for column in range(left, left + key_columns))
                            for row in range(top, top + key_rows)
                        )
                        key_candidates.append((key, cells))
            if len(key_candidates) == 1:
                key, key_cells = key_candidates[0]
                result.append(
                    {
                        "source": source,
                        "tops": tuple(tops),
                        "lefts": tuple(lefts),
                        "by_anchor": by_anchor,
                        "key": key,
                        "key_cells": key_cells,
                    }
                )
    return result


def _matrix_variants(matrix: tuple[tuple[int, ...], ...]) -> dict[str, tuple[tuple[int, ...], ...]]:
    def rotate(value: tuple[tuple[int, ...], ...]) -> tuple[tuple[int, ...], ...]:
        return tuple(tuple(value[len(value) - 1 - row][column] for row in range(len(value))) for column in range(len(value[0])))

    result: dict[str, tuple[tuple[int, ...], ...]] = {}
    value = matrix
    for turns in range(4):
        result[f"r{turns}"] = value
        result[f"mirror_r{turns}"] = tuple(tuple(reversed(row)) for row in value)
        value = rotate(value)
    return result


def _execute_matrix_projection(program: Mapping[str, Any], grid: Grid) -> Grid:
    transform = str(program.get("transform"))
    decompositions = _glyph_key_decompositions(grid)
    candidates: list[Grid] = []
    for item in decompositions:
        variants = _matrix_variants(item["key"])
        key = variants.get(transform)
        if key is None or len(key) != len(item["tops"]) or len(key[0]) != len(item["lefts"]):
            continue
        output = [list(row) for row in grid]
        for row_index, top in enumerate(item["tops"]):
            for column_index, left in enumerate(item["lefts"]):
                component = item["by_anchor"][(top, left)]
                color = key[row_index][column_index]
                for row, column in component:
                    output[row][column] = color
        candidates.append(tuple(tuple(row) for row in output))
    unique = {_canonical(_plain(candidate)): candidate for candidate in candidates}
    if len(unique) != 1:
        raise Undefined("glyph palette projection is ambiguous")
    return next(iter(unique.values()))


def _normalize_points(points: Sequence[tuple[Fraction, Fraction]]) -> tuple[tuple[Fraction, Fraction], ...]:
    rows = [point[0] for point in points]
    columns = [point[1] for point in points]
    top, bottom = min(rows), max(rows)
    left, right = min(columns), max(columns)
    return tuple(
        (
            (row - top) / (bottom - top) if bottom != top else Fraction(0),
            (column - left) / (right - left) if right != left else Fraction(0),
        )
        for row, column in points
    )


def _transform_points(points: Sequence[tuple[Fraction, Fraction]], transform: str) -> tuple[tuple[Fraction, Fraction], ...]:
    result: list[tuple[Fraction, Fraction]] = []
    for row, column in points:
        if transform.startswith("mirror_"):
            column = 1 - column
            turns_name = transform.removeprefix("mirror_")
        else:
            turns_name = transform
        turns = {"r0": 0, "r1": 1, "r2": 2, "r3": 3}.get(turns_name)
        if turns is None:
            raise Undefined("unknown point transform")
        for _ in range(turns):
            row, column = column, 1 - row
        result.append((row, column))
    return tuple(result)


def _marker_decompositions(grid: Grid) -> list[dict[str, Any]]:
    background = _background(grid)
    support = _foreground_components(grid, monochrome=False, connectivity=8)
    result: list[dict[str, Any]] = []
    for reference in support:
        counts = Counter(grid[row][column] for row, column in reference)
        if len(counts) < 3:
            continue
        base, base_count = counts.most_common(1)[0]
        markers = [(row, column, grid[row][column]) for row, column in reference if grid[row][column] != base]
        if not 2 <= len(markers) <= 7 or any(count != 1 for color, count in counts.items() if color != base):
            continue
        if len({color for _, _, color in markers}) != len(markers) or base_count * 4 < len(reference) * 3:
            continue
        top, bottom, left, right = _bbox(reference)
        if len(reference) != (bottom - top + 1) * (right - left + 1):
            continue
        payload = [component for component in support if component != reference]
        if len(payload) != len(markers):
            continue
        payload_colors = {
            grid[next(iter(component))[0]][next(iter(component))[1]]
            for component in payload
            if len({grid[row][column] for row, column in component}) == 1
        }
        if len(payload_colors) != 1 or any(len({grid[row][column] for row, column in component}) != 1 for component in payload):
            continue
        result.append(
            {
                "reference": reference,
                "markers": tuple(sorted(markers)),
                "payload": tuple(sorted(payload, key=lambda cells: (_bbox(cells), len(cells)))),
            }
        )
    return result


def _execute_marker_map(program: Mapping[str, Any], grid: Grid) -> Grid:
    transform = str(program.get("transform"))
    candidates: list[Grid] = []
    for item in _marker_decompositions(grid):
        markers = item["markers"]
        payload = item["payload"]
        marker_points = _normalize_points(tuple((Fraction(row), Fraction(column)) for row, column, _ in markers))
        marker_points = _transform_points(marker_points, transform)
        payload_points = _normalize_points(
            tuple(
                (
                    Fraction(sum(row for row, _ in component), len(component)),
                    Fraction(sum(column for _, column in component), len(component)),
                )
                for component in payload
            )
        )
        scored: list[tuple[Fraction, tuple[int, ...]]] = []
        for permutation in itertools.permutations(range(len(payload))):
            score = sum(
                abs(marker_points[index][0] - payload_points[permutation[index]][0])
                + abs(marker_points[index][1] - payload_points[permutation[index]][1])
                for index in range(len(markers))
            )
            scored.append((score, permutation))
        scored.sort()
        if len(scored) > 1 and scored[0][0] == scored[1][0]:
            continue
        output = [list(row) for row in grid]
        for marker_index, payload_index in enumerate(scored[0][1]):
            color = markers[marker_index][2]
            for row, column in payload[payload_index]:
                output[row][column] = color
        candidates.append(tuple(tuple(row) for row in output))
    unique = {_canonical(_plain(candidate)): candidate for candidate in candidates}
    if len(unique) != 1:
        raise Undefined("marker-map alignment is ambiguous")
    return next(iter(unique.values()))


def _execute(program: Mapping[str, Any], grid: Grid) -> Grid:
    if program.get("schema") != SCHEMA:
        raise Undefined("foreign palette-flow program")
    operator = str(program.get("operator"))
    executors: dict[str, Callable[[Mapping[str, Any], Grid], Grid]] = {
        "ordered_palette_table": _execute_ordered_table,
        "corner_palette_projection": _execute_corner_projection,
        "magnified_mask_stamp": _execute_magnified_mask,
        "matrix_palette_projection": _execute_matrix_projection,
        "relational_marker_map": _execute_marker_map,
    }
    executor = executors.get(operator)
    if executor is None:
        raise Undefined("unknown palette-flow operator")
    return executor(program, grid)


def replay_program(program: Mapping[str, Any], grid: Any) -> list[list[int]]:
    """Replay a serialized relational palette program without task context."""

    if not isinstance(program, Mapping):
        raise Undefined("program must be a mapping")
    return _plain(_execute(program, _grid(grid)))


def _grammar() -> tuple[tuple[int, dict[str, Any]], ...]:
    programs: list[tuple[int, dict[str, Any]]] = []
    for axis, order, direction in itertools.product(
        ("rows", "columns"), ("forward", "reverse"), ("forward", "reverse")
    ):
        programs.append(
            (
                14,
                {
                    "schema": SCHEMA,
                    "operator": "ordered_palette_table",
                    "axis": axis,
                    "order": order,
                    "direction": direction,
                },
            )
        )
    for bins in (2, 3, 4):
        for transform in _D4:
            programs.append(
                (
                    12,
                    {
                        "schema": SCHEMA,
                        "operator": "corner_palette_projection",
                        "bins": bins,
                        "transform": transform,
                    },
                )
            )
    for tile in range(2, 6):
        for scale in (2, 3):
            programs.append(
                (
                    16,
                    {
                        "schema": SCHEMA,
                        "operator": "magnified_mask_stamp",
                        "tile": tile,
                        "gap": 1,
                        "scale": scale,
                    },
                )
            )
    for transform in _D4:
        programs.append(
            (
                15,
                {
                    "schema": SCHEMA,
                    "operator": "matrix_palette_projection",
                    "transform": transform,
                },
            )
        )
        programs.append(
            (
                17,
                {
                    "schema": SCHEMA,
                    "operator": "relational_marker_map",
                    "transform": transform,
                },
            )
        )
    return tuple(sorted(programs, key=lambda item: (item[0], _canonical(item[1]))))


_PROGRAMS = _grammar()


def _fit_programs(train: Sequence[Pair]) -> dict[str, tuple[int, dict[str, Any]]]:
    result: dict[str, tuple[int, dict[str, Any]]] = {}
    for complexity, program in _PROGRAMS:
        try:
            outputs = tuple(_execute(program, source) for source, _ in train)
        except (KeyError, TypeError, ValueError, IndexError, ZeroDivisionError):
            continue
        if outputs == tuple(target for _, target in train) and any(source != target for source, target in train):
            result[_canonical(program)] = (complexity, program)
    return result


def _behavior_hash(outputs: Sequence[Grid]) -> str:
    return hashlib.sha256(_canonical([_plain(output) for output in outputs]).encode("utf-8")).hexdigest()


def compile_task(task: Any, limits: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    """Compile at most one exact, LOO-stable relational palette program."""

    try:
        if not isinstance(task, Mapping):
            return []
        raw_train = task.get("train")
        raw_test = task.get("test")
        if (
            not isinstance(raw_train, Sequence)
            or isinstance(raw_train, (str, bytes, bytearray))
            or len(raw_train) < 2
            or len(raw_train) > 10
            or not isinstance(raw_test, Sequence)
            or isinstance(raw_test, (str, bytes, bytearray))
            or not raw_test
            or len(raw_test) > 10
        ):
            return []
        if limits is not None and not isinstance(limits, Mapping):
            return []
        cap = 1
        if limits is not None:
            raw_cap = limits.get("max_candidates", limits.get("candidate_cap", 1))
            if isinstance(raw_cap, bool) or not isinstance(raw_cap, int) or raw_cap < 1:
                return []
            cap = min(raw_cap, 1)
        train = tuple(
            (_grid(example["input"]), _grid(example["output"]))
            for example in raw_train
            if isinstance(example, Mapping)
        )
        tests = tuple(
            _grid(example["input"])
            for example in raw_test
            if isinstance(example, Mapping)
        )
        if len(train) != len(raw_train) or len(tests) != len(raw_test):
            return []
        full = _fit_programs(train)
        if not full:
            return []
        # Genuine LOO re-induction: each serialized program must be recovered
        # from every strict training subset before the held-out example is
        # replayed.  The held-out target never participates in re-proposal.
        loo_sets = [
            _fit_programs(tuple(pair for index, pair in enumerate(train) if index != held_out))
            for held_out in range(len(train))
        ]
        proposals: list[tuple[int, str, dict[str, Any], tuple[Grid, ...]]] = []
        for key, (complexity, program) in full.items():
            if any(key not in loo for loo in loo_sets):
                continue
            try:
                forecasts = tuple(_execute(program, test) for test in tests)
            except (KeyError, TypeError, ValueError, IndexError, ZeroDivisionError):
                continue
            if all(forecast == test for forecast, test in zip(forecasts, tests)):
                continue
            proposals.append((complexity, key, program, forecasts))
        if not proposals:
            return []
        # All surviving programs are semantic competitors, not merely the
        # minimum-cost subset.  Any forecast disagreement forces abstention.
        behaviors = {_behavior_hash(item[3]) for item in proposals}
        if len(behaviors) != 1:
            return []
        proposals.sort(key=lambda item: (item[0], item[1]))
        complexity, _, program, forecasts = proposals[0]
        candidate = {
            "family": "relational_palette_flow",
            "program": program,
            "train_outputs": [_plain(target) for _, target in train],
            "test_outputs": [_plain(output) for output in forecasts],
            "complexity": complexity,
            "evidence": {
                "author": AUTHOR,
                "all_demonstrations_exact": True,
                "leave_one_demonstration_out_reinduced": True,
                "independent_replay": True,
                "task_identity_blind": True,
                "test_labels_unread": True,
                "ambiguity_abstention": True,
                "equivalent_programs": len(proposals),
                "test_behavior_hash": _behavior_hash(forecasts),
            },
        }
        return [candidate][:cap]
    except (KeyError, TypeError, ValueError, IndexError, ZeroDivisionError):
        return []


__all__ = ["compile_task", "replay_program"]
