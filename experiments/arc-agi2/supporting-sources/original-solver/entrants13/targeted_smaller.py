"""Bounded structural serializers for small-output ARC tasks.

The entrant is intentionally a collection of *schemas*, not task cases.  A
schema may be admitted only when it exactly replays every labelled training
demonstration.  Test records are read through their ``input`` member only.
Learned constants are compact structural parameters (dimensions, a small
panel-template codebook, or a finite occupancy truth table); task identities,
grid fingerprints, and test targets are neither accepted nor represented.

Author: Komorebi P.
"""
from __future__ import annotations

from collections import Counter, deque
from collections.abc import Mapping, Sequence
import json
from typing import Any, Callable


Grid = tuple[tuple[int, ...], ...]
PROGRAM_SCHEMA = "komorebi.pr_lasm.block13.targeted_smaller_program"
MAX_CANDIDATES = 64
MAX_EXAMPLES = 16
MAX_TOTAL_CELLS = 60_000


class UndefinedRule(ValueError):
    """The structural preconditions of a schema do not hold."""


def _grid(value: Any) -> Grid:
    if not isinstance(value, (list, tuple)) or not value or len(value) > 30:
        raise ValueError("grid must be a nonempty ARC row sequence")
    width: int | None = None
    rows: list[tuple[int, ...]] = []
    for raw in value:
        if not isinstance(raw, (list, tuple)) or not raw:
            raise ValueError("grid row must be nonempty")
        if width is None:
            width = len(raw)
            if width > 30:
                raise ValueError("grid is wider than ARC")
        elif len(raw) != width:
            raise ValueError("grid must be rectangular")
        row: list[int] = []
        for cell in raw:
            if isinstance(cell, bool) or not isinstance(cell, int) or not 0 <= cell <= 9:
                raise ValueError("ARC cells must be integers in [0, 9]")
            row.append(cell)
        rows.append(tuple(row))
    return tuple(rows)


def _sanitize(task: Any) -> tuple[tuple[tuple[Grid, Grid], ...], tuple[Grid, ...]]:
    if not isinstance(task, Mapping):
        raise ValueError("task must be a mapping")
    train_raw, test_raw = task["train"], task["test"]
    if (
        not isinstance(train_raw, Sequence)
        or isinstance(train_raw, (str, bytes))
        or not isinstance(test_raw, Sequence)
        or isinstance(test_raw, (str, bytes))
        or not train_raw
        or not test_raw
        or len(train_raw) + len(test_raw) > MAX_EXAMPLES
    ):
        raise ValueError("invalid example count")
    cells = 0
    train: list[tuple[Grid, Grid]] = []
    tests: list[Grid] = []
    for example in train_raw:
        if not isinstance(example, Mapping):
            raise ValueError("training record must be a mapping")
        source, result = _grid(example["input"]), _grid(example["output"])
        cells += len(source) * len(source[0]) + len(result) * len(result[0])
        train.append((source, result))
    for example in test_raw:
        if not isinstance(example, Mapping):
            raise ValueError("test record must be a mapping")
        # Do not enumerate keys or call get(): exactly one observable member.
        source = _grid(example["input"])
        cells += len(source) * len(source[0])
        tests.append(source)
    if cells > MAX_TOTAL_CELLS:
        raise ValueError("task exceeds the finite cell budget")
    return tuple(train), tuple(tests)


def _candidate_cap(limits: Any) -> int:
    if limits is None:
        return MAX_CANDIDATES
    if isinstance(limits, bool):
        raise ValueError("boolean limit is invalid")
    if isinstance(limits, int):
        return max(1, min(MAX_CANDIDATES, limits))
    if not isinstance(limits, Mapping):
        raise ValueError("limits must be a mapping or integer")
    raw = limits.get("max_candidates", limits.get("candidate_cap", MAX_CANDIDATES))
    if isinstance(raw, bool) or not isinstance(raw, int) or raw < 1:
        raise ValueError("candidate cap must be positive")
    return min(MAX_CANDIDATES, raw)


def _lists(grid: Grid) -> list[list[int]]:
    return [list(row) for row in grid]


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _mode(grid: Grid) -> int:
    counts = Counter(cell for row in grid for cell in row)
    return min(counts, key=lambda color: (-counts[color], color))


def _components(grid: Grid, background: int, connectivity: int = 4) -> list[dict[str, Any]]:
    remaining = {
        (r, c)
        for r, row in enumerate(grid)
        for c, value in enumerate(row)
        if value != background
    }
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    if connectivity == 8:
        directions += [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    result: list[dict[str, Any]] = []
    while remaining:
        seed = min(remaining)
        color = grid[seed[0]][seed[1]]
        queue = deque([seed])
        remaining.remove(seed)
        cells: list[tuple[int, int]] = []
        while queue:
            cell = queue.popleft()
            cells.append(cell)
            for dr, dc in directions:
                nxt = (cell[0] + dr, cell[1] + dc)
                if nxt in remaining and grid[nxt[0]][nxt[1]] == color:
                    remaining.remove(nxt)
                    queue.append(nxt)
        rs = [cell[0] for cell in cells]
        cs = [cell[1] for cell in cells]
        result.append(
            {
                "cells": tuple(sorted(cells)),
                "color": color,
                "r0": min(rs),
                "r1": max(rs),
                "c0": min(cs),
                "c1": max(cs),
            }
        )
    return sorted(result, key=lambda obj: (obj["r0"], obj["c0"], obj["color"]))


def _crop_object(grid: Grid, obj: Mapping[str, Any], background: int) -> Grid:
    return tuple(
        tuple(
            grid[r][c] if (r, c) in obj["cells"] else background
            for c in range(obj["c0"], obj["c1"] + 1)
        )
        for r in range(obj["r0"], obj["r1"] + 1)
    )


def _crop_nonbackground(grid: Grid, background: int) -> Grid:
    cells = [(r, c) for r, row in enumerate(grid) for c, value in enumerate(row) if value != background]
    if not cells:
        raise UndefinedRule("cannot crop an empty raster")
    r0, r1 = min(r for r, _ in cells), max(r for r, _ in cells)
    c0, c1 = min(c for _, c in cells), max(c for _, c in cells)
    return tuple(tuple(grid[r][c0 : c1 + 1]) for r in range(r0, r1 + 1))


def _d4(grid: Grid) -> list[tuple[str, Grid]]:
    r90 = tuple(tuple(row) for row in zip(*grid[::-1]))
    r180 = tuple(tuple(row[::-1]) for row in grid[::-1])
    r270 = tuple(tuple(row) for row in zip(*grid))[::-1]
    flip = tuple(tuple(row[::-1]) for row in grid)
    flip90 = tuple(tuple(row) for row in zip(*flip[::-1]))
    flip180 = tuple(tuple(row[::-1]) for row in flip[::-1])
    flip270 = tuple(tuple(row) for row in zip(*flip))[::-1]
    return [
        ("identity", grid),
        ("rotate90", r90),
        ("rotate180", r180),
        ("rotate270", r270),
        ("mirror", flip),
        ("mirror_rotate90", flip90),
        ("mirror_rotate180", flip180),
        ("mirror_rotate270", flip270),
    ]


def _transform(grid: Grid, name: str) -> Grid:
    return dict(_d4(grid))[name]


def _unique_control_index(values: Sequence[int], excluded: int | None = None) -> int:
    counts = Counter(values)
    choices = [
        (count, color, index)
        for index, color in enumerate(values)
        if color != excluded and (count := counts[color]) == 1
    ]
    if len(choices) != 1:
        raise UndefinedRule("control marker is not unique")
    return choices[0][2]


def _panel_template(panel: Grid) -> str:
    background = _mode(panel)
    return "/".join(
        "".join("1" if value == background else "0" for value in row) for row in panel
    )


def _execute(source: Grid, program: Mapping[str, Any]) -> Grid:
    kind = program["kind"]
    h, w = len(source), len(source[0])

    if kind == "northwest_crop":
        oh, ow = int(program["raster_h"]), int(program["raster_w"])
        if oh > h or ow > w:
            raise UndefinedRule("crop exceeds input")
        return tuple(tuple(source[r][:ow]) for r in range(oh))

    if kind == "five_by_five_diagonal_compaction":
        if (h, w) != (5, 5):
            raise UndefinedRule("diagonal compaction requires 5x5")
        coordinates = (
            ((0, 0), (1, 1), (0, 4)),
            ((1, 3), (2, 2), (3, 1)),
            ((4, 0), (3, 3), (4, 4)),
        )
        return tuple(tuple(source[r][c] for r, c in row) for row in coordinates)

    if kind == "sector_singleton_serialization":
        oh, ow = int(program["raster_h"]), int(program["raster_w"])
        background = _mode(source)
        result = [[background for _ in range(ow)] for _ in range(oh)]
        seen: set[tuple[int, int]] = set()
        for r, row in enumerate(source):
            for c, value in enumerate(row):
                if value == background:
                    continue
                cell = (min(oh - 1, r * oh // h), min(ow - 1, c * ow // w))
                if cell in seen:
                    raise UndefinedRule("sector contains multiple marks")
                seen.add(cell)
                result[cell[0]][cell[1]] = value
        if len(seen) != oh * ow:
            raise UndefinedRule("not every sector is occupied")
        return tuple(tuple(row) for row in result)

    if kind == "corner_colored_interior_mask":
        if h < 5 or w < 5:
            raise UndefinedRule("framed mask is too small")
        inner_h, inner_w = h - 4, w - 4
        marker_counts = Counter(
            source[r][c] for r in range(2, h - 2) for c in range(2, w - 2) if source[r][c] != 0
        )
        if len(marker_counts) != 1:
            raise UndefinedRule("interior mask color is not unique")
        marker = next(iter(marker_counts))
        corners = ((source[0][0], source[0][-1]), (source[-1][0], source[-1][-1]))
        result: list[tuple[int, ...]] = []
        for r in range(inner_h):
            row: list[int] = []
            for c in range(inner_w):
                if source[r + 2][c + 2] != marker:
                    row.append(0)
                else:
                    row.append(corners[0 if 2 * r < inner_h else 1][0 if 2 * c < inner_w else 1])
            result.append(tuple(row))
        return tuple(result)

    if kind == "triptych_apply_relation":
        if w % 3 or int(program["chip_w"]) < 1:
            raise UndefinedRule("triptych width is invalid")
        panel_w = w // 3
        background = _mode(source)
        result = [[background] * int(program["chip_w"]) for _ in range(h)]
        active_rows = [r for r in range(h) if any(value != background for value in source[r])]
        runs: list[list[int]] = []
        for r in active_rows:
            if not runs or r != runs[-1][-1] + 1:
                runs.append([r])
            else:
                runs[-1].append(r)
        for run in runs:
            panels = [
                tuple(tuple(source[r][k * panel_w : (k + 1) * panel_w]) for r in run)
                for k in range(3)
            ]
            cropped = [_crop_nonbackground(panel, background) for panel in panels]
            left, middle, payload = cropped
            preferred = str(program.get("preferred_relation", "identity"))
            names = [name for name, _ in _d4(left)]
            relation_rank = [preferred] + [name for name in names if name != preferred]
            relations: list[tuple[int, int, str, dict[int, int]]] = []
            for order, (name, transformed) in enumerate(_d4(left)):
                if (len(transformed), len(transformed[0])) != (len(middle), len(middle[0])):
                    continue
                mapping: dict[int, int] = {background: background}
                reverse: dict[int, int] = {background: background}
                valid = True
                for arow, brow in zip(transformed, middle):
                    for a, b in zip(arow, brow):
                        if (a in mapping and mapping[a] != b) or (b in reverse and reverse[b] != a):
                            valid = False
                            break
                        mapping[a], reverse[b] = b, a
                    if not valid:
                        break
                if valid:
                    recolors = sum(a != b for a, b in mapping.items())
                    relations.append((recolors, relation_rank.index(name), name, mapping))
            if not relations:
                raise UndefinedRule("no finite panel relation")
            _, _, name, mapping = min(relations)
            moved = _transform(payload, name)
            painted = tuple(tuple(mapping.get(value, value) for value in row) for row in moved)
            painted = _crop_nonbackground(painted, background)
            if len(painted) != len(run) or len(painted[0]) != len(result[0]):
                raise UndefinedRule("transformed chip has unexpected shape")
            for rr, r in enumerate(run):
                result[r] = list(painted[rr])
        return tuple(tuple(row) for row in result)

    if kind == "corner_tile_union":
        tile = int(program["tile"])
        background = _mode(source)
        if h != 2 * tile + 1 or w < 2 * tile + 1:
            raise UndefinedRule("corner tile layout is invalid")
        starts = ((0, 0), (0, w - tile), (h - tile, 0), (h - tile, w - tile))
        destinations = ((0, 0), (0, tile - 1), (tile - 1, 0), (tile - 1, tile - 1))
        result = [[background] * (2 * tile - 1) for _ in range(2 * tile - 1)]
        for (sr, sc), (dr, dc) in zip(starts, destinations):
            for r in range(tile):
                for c in range(tile):
                    value = source[sr + r][sc + c]
                    if value != background:
                        prior = result[dr + r][dc + c]
                        if prior != background and prior != value:
                            raise UndefinedRule("corner tiles conflict")
                        result[dr + r][dc + c] = value
        return tuple(tuple(row) for row in result)

    if kind == "left_control_cyclic_shift":
        control = [row[0] for row in source]
        marker = _unique_control_index(control)
        payload = [tuple(row[1:]) for row in source]
        shift = (-marker) % h
        return tuple(payload[shift:] + payload[:shift])

    if kind == "top_left_controls_torus_shift":
        corner = source[0][0]
        row_marker = _unique_control_index([source[r][0] for r in range(1, h)], excluded=corner)
        col_marker = _unique_control_index(list(source[0][1:]), excluded=corner)
        payload = tuple(tuple(row[1:]) for row in source[1:])
        ph, pw = h - 1, w - 1
        dy, dx = (-row_marker) % ph, (-col_marker) % pw
        return tuple(tuple(payload[(r + dy) % ph][(c + dx) % pw] for c in range(pw)) for r in range(ph))

    if kind == "panel_template_codebook":
        panel_count = int(program["panel_count"])
        panel_w = int(program["panel_w"])
        separator = int(program["separator"])
        codebook = program["codebook"]
        if w != panel_count * panel_w + (panel_count - 1) * separator:
            raise UndefinedRule("coded panels have unexpected width")
        colors: list[int] = []
        for index in range(panel_count):
            start = index * (panel_w + separator)
            panel = tuple(tuple(row[start : start + panel_w]) for row in source)
            key = _panel_template(panel)
            if key not in codebook:
                raise UndefinedRule("unseen finite panel template")
            colors.append(int(codebook[key]))
        return tuple(tuple([color] * panel_count) for color in colors)

    if kind == "largest_object_color_chip":
        size = int(program["chip"])
        background = _mode(source)
        objects = _components(source, background, 4)
        if len(objects) < 2:
            raise UndefinedRule("need competing objects")
        chosen = max(
            objects,
            key=lambda obj: (
                (obj["r1"] - obj["r0"] + 1) * (obj["c1"] - obj["c0"] + 1),
                len(obj["cells"]),
                obj["r0"],
                obj["c0"],
            ),
        )
        return tuple(tuple([chosen["color"]] * size) for _ in range(size))

    if kind == "four_object_tile_pack":
        tile = int(program["tile"])
        background = _mode(source)
        objects = _components(source, background, 8)
        if len(objects) != 4:
            raise UndefinedRule("tile pack needs four objects")
        result = [[background] * (2 * tile) for _ in range(2 * tile)]
        occupied_quadrants: set[tuple[int, int]] = set()
        for obj in objects:
            chip = _crop_object(source, obj, background)
            if len(chip) != tile or len(chip[0]) != tile:
                raise UndefinedRule("object does not exactly fill a tile extent")
            holes = [(r, c) for r in range(tile) for c in range(tile) if chip[r][c] == background]
            if len(holes) != 1 or holes[0] not in {(0, 0), (0, tile - 1), (tile - 1, 0), (tile - 1, tile - 1)}:
                raise UndefinedRule("tile has no unique corner notch")
            # The missing corner faces the centre of the completed mosaic.
            hr, hc = holes[0]
            gy = 0 if hr == tile - 1 else 1
            gx = 0 if hc == tile - 1 else 1
            if (gy, gx) in occupied_quadrants:
                raise UndefinedRule("two objects claim one mosaic quadrant")
            occupied_quadrants.add((gy, gx))
            for r, row in enumerate(chip):
                for c, value in enumerate(row):
                    result[gy * tile + r][gx * tile + c] = value
        if len(occupied_quadrants) != 4:
            raise UndefinedRule("mosaic quadrants are incomplete")
        return tuple(tuple(row) for row in result)

    if kind == "color_centroid_order":
        colors = sorted(set(cell for row in source for cell in row))
        if len(colors) < 2:
            raise UndefinedRule("need multiple color regions")
        centers: list[tuple[int, float, float]] = []
        for color in colors:
            cells = [(r, c) for r, row in enumerate(source) for c, value in enumerate(row) if value == color]
            centers.append((color, sum(r for r, _ in cells) / len(cells), sum(c for _, c in cells) / len(cells)))
        row_span = max(x[1] for x in centers) - min(x[1] for x in centers)
        col_span = max(x[2] for x in centers) - min(x[2] for x in centers)
        if abs(row_span - col_span) < 0.25:
            raise UndefinedRule("dominant ordering axis is tied")
        if row_span > col_span:
            ordered = [item[0] for item in sorted(centers, key=lambda item: (item[1], item[2], item[0]))]
            return tuple((color,) for color in ordered)
        ordered = [item[0] for item in sorted(centers, key=lambda item: (item[2], item[1], item[0]))]
        return (tuple(ordered),)

    if kind == "quadrant_occupancy_table":
        oh, ow = int(program["raster_h"]), int(program["raster_w"])
        if h != 2 * oh or w != 2 * ow:
            raise UndefinedRule("quadrant dimensions mismatch")
        panels = (
            tuple(tuple(source[r][c] for c in range(ow)) for r in range(oh)),
            tuple(tuple(source[r][c + ow] for c in range(ow)) for r in range(oh)),
            tuple(tuple(source[r + oh][c] for c in range(ow)) for r in range(oh)),
            tuple(tuple(source[r + oh][c + ow] for c in range(ow)) for r in range(oh)),
        )
        colors: list[int] = []
        for panel in panels:
            nonzero = {value for row in panel for value in row if value != 0}
            if len(nonzero) != 1:
                raise UndefinedRule("quadrant has no unique role color")
            colors.append(next(iter(nonzero)))
        table = program["table"]
        result: list[tuple[int, ...]] = []
        for r in range(oh):
            row: list[int] = []
            for c in range(ow):
                key = "".join("1" if panel[r][c] != 0 else "0" for panel in panels)
                if key not in table:
                    raise UndefinedRule("unseen occupancy state")
                role = int(table[key])
                row.append(0 if role < 0 else colors[role])
            result.append(tuple(row))
        return tuple(result)

    if kind == "container_empty_rows_unary":
        oh, ow = int(program["raster_h"]), int(program["raster_w"])
        paint = int(program["paint"])
        other = [(r, c) for r, row in enumerate(source) for c, value in enumerate(row) if value not in {0, paint}]
        fill = [(r, c) for r, row in enumerate(source) for c, value in enumerate(row) if value == paint]
        if not other or not fill:
            raise UndefinedRule("container or fill is absent")
        empty = min(r for r, _ in fill) - min(r for r, _ in other)
        if not 0 <= empty <= oh * ow:
            raise UndefinedRule("unary count is outside raster")
        order: list[tuple[int, int]] = []
        top, left, bottom, right = 0, 0, oh - 1, ow - 1
        while top <= bottom and left <= right:
            order.extend((top, c) for c in range(left, right + 1))
            top += 1
            order.extend((r, right) for r in range(top, bottom + 1))
            right -= 1
            if top <= bottom:
                order.extend((bottom, c) for c in range(right, left - 1, -1))
                bottom -= 1
            if left <= right:
                order.extend((r, left) for r in range(bottom, top - 1, -1))
                left += 1
        cells = set(order[:empty])
        return tuple(tuple(paint if (r, c) in cells else 0 for c in range(ow)) for r in range(oh))

    if kind == "periodic_hole_patch":
        background = int(program["hole"])
        holes = [(r, c) for r, row in enumerate(source) for c, value in enumerate(row) if value == background]
        if not holes:
            raise UndefinedRule("periodic raster has no holes")
        viable: list[tuple[int, int, int, dict[tuple[int, int], int]]] = []
        for rp in range(1, h + 1):
            for cp in range(1, w + 1):
                table: dict[tuple[int, int], int] = {}
                valid = True
                for r, row in enumerate(source):
                    for c, value in enumerate(row):
                        if value == background:
                            continue
                        key = (r % rp, c % cp)
                        if key in table and table[key] != value:
                            valid = False
                            break
                        table[key] = value
                    if not valid:
                        break
                if valid and all((r % rp, c % cp) in table for r, c in holes):
                    viable.append((rp * cp, rp, cp, table))
        if not viable:
            raise UndefinedRule("no complete periodic explanation")
        _, rp, cp, table = min(viable, key=lambda item: (item[0], item[1] + item[2], item[1], item[2]))
        r0, r1 = min(r for r, _ in holes), max(r for r, _ in holes)
        c0, c1 = min(c for _, c in holes), max(c for _, c in holes)
        if any(source[r][c] != background for r in range(r0, r1 + 1) for c in range(c0, c1 + 1)):
            raise UndefinedRule("holes do not form a rectangular patch")
        return tuple(tuple(table[(r % rp, c % cp)] for c in range(c0, c1 + 1)) for r in range(r0, r1 + 1))

    if kind == "object_rectangle_tiling":
        oh, ow = int(program["raster_h"]), int(program["raster_w"])
        background = _mode(source)
        objects = _components(source, background, 4)
        if not 2 <= len(objects) <= 6:
            raise UndefinedRule("tiling object count is outside the bound")
        shapes: list[tuple[int, tuple[tuple[int, int], ...], int, int]] = []
        for obj in objects:
            rel = tuple((r - obj["r0"], c - obj["c0"]) for r, c in obj["cells"])
            shapes.append((obj["color"], rel, obj["r1"] - obj["r0"] + 1, obj["c1"] - obj["c0"] + 1))
        if sum(len(shape[1]) for shape in shapes) != oh * ow:
            raise UndefinedRule("objects cannot tile the requested rectangle")
        rasters: set[Grid] = set()
        board = [[background] * ow for _ in range(oh)]
        nodes = 0

        def place(index: int) -> None:
            nonlocal nodes
            nodes += 1
            if nodes > 100_000:
                raise UndefinedRule("rectangle tiling exceeded its node budget")
            if len(rasters) > 8:
                return
            if index == len(shapes):
                if all(value != background for row in board for value in row):
                    rasters.add(tuple(tuple(row) for row in board))
                return
            color, cells, sh, sw = shapes[index]
            for dr in range(oh - sh + 1):
                for dc in range(ow - sw + 1):
                    absolute = [(dr + r, dc + c) for r, c in cells]
                    if any(board[r][c] != background for r, c in absolute):
                        continue
                    for r, c in absolute:
                        board[r][c] = color
                    place(index + 1)
                    for r, c in absolute:
                        board[r][c] = background

        place(0)
        if len(rasters) != 1:
            raise UndefinedRule("rectangle tiling is not behaviourally unique")
        return next(iter(rasters))

    if kind == "separator_block_modes":
        background = _mode(source)
        separator_rows = [r for r, row in enumerate(source) if all(value == background for value in row)]
        separator_cols = [c for c in range(w) if all(source[r][c] == background for r in range(h))]

        def runs(size: int, separators: Sequence[int]) -> list[tuple[int, int]]:
            blocked = set(separators)
            found: list[tuple[int, int]] = []
            start: int | None = None
            for index in range(size + 1):
                if index < size and index not in blocked:
                    if start is None:
                        start = index
                elif start is not None:
                    found.append((start, index))
                    start = None
            return found

        row_runs, col_runs = runs(h, separator_rows), runs(w, separator_cols)
        if not row_runs or not col_runs:
            raise UndefinedRule("separator layout has no blocks")
        core: list[list[int]] = []
        for r0, r1 in row_runs:
            row: list[int] = []
            for c0, c1 in col_runs:
                counts = Counter(
                    source[r][c]
                    for r in range(r0, r1)
                    for c in range(c0, c1)
                    if source[r][c] != background
                )
                if not counts:
                    raise UndefinedRule("separator block is empty")
                row.append(min(counts, key=lambda color: (-counts[color], color)))
            core.append(row)
        result = [[background] * (len(col_runs) + 2)]
        result.extend([[background, *row, background] for row in core])
        result.append([background] * (len(col_runs) + 2))
        return tuple(tuple(row) for row in result)

    if kind == "left_template_recolors_right":
        panel_h = int(program["panel_h"])
        panel_w = int(program["panel_w"])
        gap = int(program["gap"])
        if h != panel_h + 2 or w != 2 * panel_w + gap + 2:
            raise UndefinedRule("template panel dimensions mismatch")
        left = tuple(tuple(source[r + 1][c + 1] for c in range(panel_w)) for r in range(panel_h))
        right_start = 1 + panel_w + gap
        right = tuple(tuple(source[r + 1][right_start + c] for c in range(panel_w)) for r in range(panel_h))
        key = "/".join("".join("1" if value != 0 else "0" for value in row) for row in left)
        if key not in program["codebook"]:
            raise UndefinedRule("unseen left-panel template")
        paint = int(program["codebook"][key])
        return tuple(tuple(paint if value != 0 else 0 for value in row) for row in right)

    if kind == "collision_gated_panel_union":
        split = int(program["split"])
        if w != 2 * split + 1:
            raise UndefinedRule("paired panel width mismatch")
        left = tuple(tuple(row[:split]) for row in source)
        right = tuple(tuple(row[split + 1 :]) for row in source)
        if any(left[r][c] != 0 and right[r][c] != 0 for r in range(h) for c in range(split)):
            return left
        return tuple(
            tuple(right[r][c] if right[r][c] != 0 else left[r][c] for c in range(split))
            for r in range(h)
        )

    if kind == "control_matrix_macro_recolor":
        full_rows = [r for r, row in enumerate(source) if len(set(row)) == 1 and row[0] != 0]
        full_cols = [c for c in range(w) if len({source[r][c] for r in range(h)}) == 1 and source[0][c] != 0]
        if len(full_rows) != 1 or len(full_cols) != 1:
            raise UndefinedRule("control separator cross is not unique")
        sr, sc = full_rows[0], full_cols[0]
        separator = source[sr][sc]
        quadrants = (
            tuple(tuple(source[r][c] for c in range(sc)) for r in range(sr)),
            tuple(tuple(source[r][c] for c in range(sc + 1, w)) for r in range(sr)),
            tuple(tuple(source[r][c] for c in range(sc)) for r in range(sr + 1, h)),
            tuple(tuple(source[r][c] for c in range(sc + 1, w)) for r in range(sr + 1, h)),
        )
        active = [
            (index, sum(value not in {0, separator} for row in quadrant for value in row))
            for index, quadrant in enumerate(quadrants)
        ]
        # The compact control is the nonempty quadrant with the fewest marks;
        # the dense quadrant is the mask.  Empty quadrants remain irrelevant.
        nonempty = [(index, count) for index, count in active if count]
        if len(nonempty) != 2:
            raise UndefinedRule("expected one control and one mask quadrant")
        control_index = min(nonempty, key=lambda item: (item[1], item[0]))[0]
        mask_index = max(nonempty, key=lambda item: (item[1], -item[0]))[0]
        control = _crop_nonbackground(quadrants[control_index], 0)
        mask = quadrants[mask_index]
        ch, cw = len(control), len(control[0])
        mh, mw = len(mask), len(mask[0])
        if ch * cw > 16 or mh % ch or mw % cw:
            raise UndefinedRule("control does not partition the mask")
        block_h, block_w = mh // ch, mw // cw
        result: list[tuple[int, ...]] = []
        for r in range(mh):
            row: list[int] = []
            for c in range(mw):
                row.append(0 if mask[r][c] == 0 else control[r // block_h][c // block_w])
            result.append(tuple(row))
        return tuple(result)

    if kind == "centered_color_motif_overlay":
        background = _mode(source)
        colors = sorted(set(value for row in source for value in row) - {background})
        if not colors:
            raise UndefinedRule("motif overlay has no motifs")
        motifs: list[tuple[int, list[tuple[int, int]], int, int]] = []
        maximum_span = 0
        for color in colors:
            cells = [(r, c) for r, row in enumerate(source) for c, value in enumerate(row) if value == color]
            r0, r1 = min(r for r, _ in cells), max(r for r, _ in cells)
            c0, c1 = min(c for _, c in cells), max(c for _, c in cells)
            rh, cw = r1 - r0 + 1, c1 - c0 + 1
            maximum_span = max(maximum_span, rh, cw)
            motifs.append((color, [(r - r0, c - c0) for r, c in cells], rh, cw))
        if maximum_span > 15 or maximum_span % 2 == 0:
            raise UndefinedRule("canonical motif canvas must be small and odd")
        result = [[background] * maximum_span for _ in range(maximum_span)]
        for color, cells, rh, cw in motifs:
            if (maximum_span - rh) % 2 or (maximum_span - cw) % 2:
                raise UndefinedRule("motif cannot be centered integrally")
            dr, dc = (maximum_span - rh) // 2, (maximum_span - cw) // 2
            for r, c in cells:
                rr, cc = dr + r, dc + c
                if result[rr][cc] != background and result[rr][cc] != color:
                    raise UndefinedRule("centered motifs conflict")
                result[rr][cc] = color
        return tuple(tuple(row) for row in result)

    if kind == "select_unique_nondiagonal_panel":
        ph, pw = int(program["panel_h"]), int(program["panel_w"])
        if w != pw or h % ph:
            raise UndefinedRule("stacked panel geometry mismatch")
        panels = [tuple(tuple(row) for row in source[start : start + ph]) for start in range(0, h, ph)]
        asymmetric = [panel for panel in panels if panel != tuple(tuple(row) for row in zip(*panel))]
        if len(asymmetric) != 1:
            raise UndefinedRule("non-diagonal panel is not unique")
        return asymmetric[0]

    if kind == "match_hole_shape_to_color":
        if w % 2:
            raise UndefinedRule("shape-match panel width mismatch")
        panel_w = w // 2
        left = tuple(tuple(row[:panel_w]) for row in source)
        right = tuple(tuple(row[panel_w:]) for row in source)
        base = _mode(left)

        def normalized(cells: Sequence[tuple[int, int]]) -> tuple[tuple[int, int], ...]:
            if not cells:
                raise UndefinedRule("cannot normalize empty shape")
            r0, c0 = min(r for r, _ in cells), min(c for _, c in cells)
            return tuple(sorted((r - r0, c - c0) for r, c in cells))

        right_colors = sorted(set(value for row in right for value in row) - {0})
        shapes = {
            color: normalized(
                [(r, c) for r, row in enumerate(right) for c, value in enumerate(row) if value == color]
            )
            for color in right_colors
        }
        active_rows = [r for r, row in enumerate(left) if any(value != base for value in row)]
        runs: list[list[int]] = []
        for r in active_rows:
            if not runs or r != runs[-1][-1] + 1:
                runs.append([r])
            else:
                runs[-1].append(r)
        result = [list(row) for row in left]
        used: set[int] = set()
        for run in runs:
            holes = [(r, c) for r in run for c, value in enumerate(left[r]) if value != base]
            shape = normalized(holes)
            matches = [color for color, candidate in shapes.items() if candidate == shape and color not in used]
            if len(matches) != 1:
                raise UndefinedRule("hole shape has no unique color mate")
            color = matches[0]
            used.add(color)
            for r, c in holes:
                result[r][c] = color
        if used != set(right_colors):
            raise UndefinedRule("not every right-side code shape was consumed")
        return tuple(tuple(row) for row in result)

    if kind == "component_count_identity":
        connectivity = int(program["connectivity"])
        background = _mode(source)
        objects = _components(source, background, connectivity)
        colors = {obj["color"] for obj in objects}
        if len(colors) != 1 or not objects:
            raise UndefinedRule("identity count requires one foreground color")
        n, color = len(objects), next(iter(colors))
        if n > 30:
            raise UndefinedRule("identity raster too large")
        return tuple(tuple(color if r == c else background for c in range(n)) for r in range(n))

    if kind == "framed_interior_count_unary":
        oh, ow = int(program["raster_h"]), int(program["raster_w"])
        background = _mode(source)
        objects = _components(source, background, 4)
        frame = max(objects, key=lambda obj: ((obj["r1"] - obj["r0"] + 1) * (obj["c1"] - obj["c0"] + 1), len(obj["cells"])))
        markers = [
            (r, c, source[r][c])
            for r in range(frame["r0"] + 1, frame["r1"])
            for c in range(frame["c0"] + 1, frame["c1"])
            if source[r][c] not in {background, frame["color"]}
        ]
        colors = {value for _, _, value in markers}
        if len(colors) != 1 or len(markers) > oh * ow:
            raise UndefinedRule("interior markers are invalid")
        color = next(iter(colors))
        return tuple(tuple(color if r * ow + c < len(markers) else background for c in range(ow)) for r in range(oh))

    if kind == "cross_fourfold_completion":
        full_rows = [r for r, row in enumerate(source) if len(set(row)) == 1 and row[0] != 0]
        full_cols = [c for c in range(w) if len({source[r][c] for r in range(h)}) == 1 and source[0][c] != 0]
        if len(full_rows) != 1 or len(full_cols) != 1:
            raise UndefinedRule("separator cross is not unique")
        sr, sc = full_rows[0], full_cols[0]
        if h != 2 * sr + 1 or w != 2 * sc + 1 or source[sr][sc] != source[sr][0]:
            raise UndefinedRule("cross is not centered")
        paint = source[sr][sc]
        quadrants = (
            tuple(tuple(source[r][c] for c in range(sc)) for r in range(sr)),
            tuple(tuple(source[r][c] for c in range(sc + 1, w)) for r in range(sr)),
            tuple(tuple(source[r][c] for c in range(sc)) for r in range(sr + 1, h)),
            tuple(tuple(source[r][c] for c in range(sc + 1, w)) for r in range(sr + 1, h)),
        )
        populated = [index for index, q in enumerate(quadrants) if any(value not in {0, paint} for row in q for value in row)]
        if len(populated) != 1:
            raise UndefinedRule("need exactly one seed quadrant")
        seed = quadrants[populated[0]]
        # Orient the seed as the northwest quadrant before reflection.
        if populated[0] in {1, 3}:
            seed = tuple(tuple(row[::-1]) for row in seed)
        if populated[0] in {2, 3}:
            seed = seed[::-1]
        mask = tuple(tuple(value not in {0, paint} for value in row) for row in seed)
        top = tuple(
            tuple(paint if bit else 0 for bit in row + row[::-1]) for row in mask
        )
        return top + top[::-1]

    raise UndefinedRule("unknown program kind")


def _infer_codebook(train: tuple[tuple[Grid, Grid], ...]) -> dict[str, Any] | None:
    first_source, first_result = train[0]
    n = len(first_result)
    if n < 2 or len(first_result[0]) != n or any(len(set(row)) != 1 for row in first_result):
        return None
    w = len(first_source[0])
    if (w - (n - 1)) % n:
        return None
    panel_w = (w - (n - 1)) // n
    if panel_w < 2:
        return None
    table: dict[str, int] = {}
    for source, result in train:
        if len(result) != n or any(len(row) != n or len(set(row)) != 1 for row in result):
            return None
        if len(source[0]) != w:
            return None
        for index in range(n):
            start = index * (panel_w + 1)
            panel = tuple(tuple(row[start : start + panel_w]) for row in source)
            key, value = _panel_template(panel), result[index][0]
            if key in table and table[key] != value:
                return None
            table[key] = value
    return {
        "schema": PROGRAM_SCHEMA,
        "kind": "panel_template_codebook",
        "panel_count": n,
        "panel_w": panel_w,
        "separator": 1,
        "codebook": dict(sorted(table.items())),
    }


def _infer_quadrant_table(train: tuple[tuple[Grid, Grid], ...]) -> dict[str, Any] | None:
    oh, ow = len(train[0][1]), len(train[0][1][0])
    table: dict[str, int] = {}
    for source, result in train:
        if len(source) != 2 * oh or len(source[0]) != 2 * ow or (len(result), len(result[0])) != (oh, ow):
            return None
        panels = (
            tuple(tuple(source[r][c] for c in range(ow)) for r in range(oh)),
            tuple(tuple(source[r][c + ow] for c in range(ow)) for r in range(oh)),
            tuple(tuple(source[r + oh][c] for c in range(ow)) for r in range(oh)),
            tuple(tuple(source[r + oh][c + ow] for c in range(ow)) for r in range(oh)),
        )
        colors: list[int] = []
        for panel in panels:
            values = {value for row in panel for value in row if value != 0}
            if len(values) != 1:
                return None
            colors.append(next(iter(values)))
        for r in range(oh):
            for c in range(ow):
                key = "".join("1" if panel[r][c] != 0 else "0" for panel in panels)
                value = result[r][c]
                if value == 0:
                    role = -1
                elif value in colors:
                    role = colors.index(value)
                else:
                    return None
                if key in table and table[key] != role:
                    return None
                table[key] = role
    return {
        "schema": PROGRAM_SCHEMA,
        "kind": "quadrant_occupancy_table",
        "raster_h": oh,
        "raster_w": ow,
        "table": dict(sorted(table.items())),
    }


def _infer_left_template_recolor(train: tuple[tuple[Grid, Grid], ...]) -> dict[str, Any] | None:
    panel_h, panel_w = len(train[0][1]), len(train[0][1][0])
    first_source = train[0][0]
    if len(first_source) != panel_h + 2:
        return None
    gap = len(first_source[0]) - 2 * panel_w - 2
    if gap < 1:
        return None
    table: dict[str, int] = {}
    for source, result in train:
        if len(source) != panel_h + 2 or len(source[0]) != 2 * panel_w + gap + 2:
            return None
        left = tuple(tuple(source[r + 1][c + 1] for c in range(panel_w)) for r in range(panel_h))
        right_start = 1 + panel_w + gap
        right = tuple(tuple(source[r + 1][right_start + c] for c in range(panel_w)) for r in range(panel_h))
        colors = {value for row in result for value in row if value != 0}
        if len(colors) != 1:
            return None
        paint = next(iter(colors))
        wanted = tuple(tuple(paint if value != 0 else 0 for value in row) for row in right)
        if wanted != result:
            return None
        key = "/".join("".join("1" if value != 0 else "0" for value in row) for row in left)
        if key in table and table[key] != paint:
            return None
        table[key] = paint
    return {
        "schema": PROGRAM_SCHEMA,
        "kind": "left_template_recolors_right",
        "panel_h": panel_h,
        "panel_w": panel_w,
        "gap": gap,
        "codebook": dict(sorted(table.items())),
    }


def _programs(train: tuple[tuple[Grid, Grid], ...]) -> list[dict[str, Any]]:
    first_source, first_result = train[0]
    oh, ow = len(first_result), len(first_result[0])
    base = lambda kind, **params: {"schema": PROGRAM_SCHEMA, "kind": kind, **params}
    programs: list[dict[str, Any]] = [
        base("northwest_crop", raster_h=oh, raster_w=ow),
        base("five_by_five_diagonal_compaction"),
        base("sector_singleton_serialization", raster_h=oh, raster_w=ow),
        base("corner_colored_interior_mask"),
        base("corner_tile_union", tile=(oh + 1) // 2),
        base("left_control_cyclic_shift"),
        base("top_left_controls_torus_shift"),
        base("largest_object_color_chip", chip=oh),
        base("four_object_tile_pack", tile=oh // 2),
        base("color_centroid_order"),
        base("periodic_hole_patch", hole=0),
        base("object_rectangle_tiling", raster_h=oh, raster_w=ow),
        base("separator_block_modes"),
        base("collision_gated_panel_union", split=ow),
        base("control_matrix_macro_recolor"),
        base("centered_color_motif_overlay"),
        base("select_unique_nondiagonal_panel", panel_h=oh, panel_w=ow),
        base("match_hole_shape_to_color"),
        base("component_count_identity", connectivity=4),
        base("component_count_identity", connectivity=8),
        base("framed_interior_count_unary", raster_h=oh, raster_w=ow),
        base("cross_fourfold_completion"),
    ]
    programs.extend(
        base("triptych_apply_relation", chip_w=ow, preferred_relation=name)
        for name, _ in _d4(((1, 2), (3, 4)))
    )
    foreground = {value for row in first_result for value in row if value != 0}
    if len(foreground) == 1:
        programs.append(
            base(
                "container_empty_rows_unary",
                raster_h=oh,
                raster_w=ow,
                paint=next(iter(foreground)),
            )
        )
    codebook = _infer_codebook(train)
    if codebook is not None:
        programs.append(codebook)
    quadrant = _infer_quadrant_table(train)
    if quadrant is not None:
        programs.append(quadrant)
    template_recolor = _infer_left_template_recolor(train)
    if template_recolor is not None:
        programs.append(template_recolor)
    # Stable schema/parameter ordering is part of the reproducibility contract.
    return sorted(programs, key=lambda program: (len(_canonical(program)), _canonical(program)))


def compile_task(task: Any, limits: Any = None) -> list[dict[str, Any]]:
    """Compile bounded, exact-demo structural candidates for one ARC task."""

    try:
        cap = _candidate_cap(limits)
        train, tests = _sanitize(task)
        admitted: list[tuple[int, str, dict[str, Any], tuple[Grid, ...], tuple[Grid, ...]]] = []
        for program in _programs(train):
            try:
                replay = tuple(_execute(source, program) for source, _ in train)
                if any(actual != wanted for actual, (_, wanted) in zip(replay, train)):
                    continue
                forecast = tuple(_execute(source, program) for source in tests)
            except (KeyError, TypeError, ValueError, IndexError, ZeroDivisionError):
                continue
            complexity = len(_canonical(program))
            admitted.append((complexity, _canonical(program), program, replay, forecast))

        # Quotient by complete test-input behaviour and retain the shortest
        # (then canonical) representative: a finite MDL selection.
        best: dict[str, tuple[int, str, dict[str, Any], tuple[Grid, ...], tuple[Grid, ...]]] = {}
        for item in admitted:
            behavior = _canonical(item[4])
            if behavior not in best or item[:2] < best[behavior][:2]:
                best[behavior] = item
        results: list[dict[str, Any]] = []
        for complexity, _, program, replay, forecast in sorted(best.values(), key=lambda item: item[:2])[:cap]:
            results.append(
                {
                    "family": "targeted_smaller",
                    "program": program,
                    "train_outputs": [_lists(grid) for grid in replay],
                    "test_outputs": [_lists(grid) for grid in forecast],
                    "complexity": complexity,
                    "evidence": {
                        "all_demos_exact": True,
                        "demo_count": len(train),
                        "selection": "minimum_description_length",
                        "schema_kind": program["kind"],
                    },
                }
            )
        return results
    except (KeyError, TypeError, ValueError, IndexError, ZeroDivisionError):
        return []


__all__ = ["compile_task"]
