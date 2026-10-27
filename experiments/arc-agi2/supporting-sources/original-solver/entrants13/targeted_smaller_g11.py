"""Generation-11 small-output structural tournament entrant.

Every hypothesis is an ID-blind, bounded scene schema.  Hypotheses see
labelled demonstrations and test inputs only, are retained after exact replay
of every demonstration, and are quotiented by complete test-input behaviour.

Author: Komorebi P.
"""
from __future__ import annotations

from collections import Counter, deque
from collections.abc import Mapping, Sequence
from itertools import permutations
import json
from typing import Any


Grid = tuple[tuple[int, ...], ...]
SCHEMA = "komorebi.pr_lasm.block13.targeted_smaller_g11_program"
MAX_CANDIDATES = 48
MAX_TOTAL_CELLS = 60_000
MAX_LINE_EXTENSIONS = 32


class UndefinedRule(ValueError):
    pass


def _grid(value: Any) -> Grid:
    if not isinstance(value, (list, tuple)) or not value or len(value) > 30:
        raise ValueError("invalid grid")
    width = len(value[0]) if isinstance(value[0], (list, tuple)) else 0
    if not width or width > 30:
        raise ValueError("invalid grid width")
    rows: list[tuple[int, ...]] = []
    for raw in value:
        if not isinstance(raw, (list, tuple)) or len(raw) != width:
            raise ValueError("grid must be rectangular")
        row: list[int] = []
        for cell in raw:
            if isinstance(cell, bool) or not isinstance(cell, int) or not 0 <= cell <= 9:
                raise ValueError("invalid ARC cell")
            row.append(cell)
        rows.append(tuple(row))
    return tuple(rows)


def _sanitize(task: Any) -> tuple[tuple[tuple[Grid, Grid], ...], tuple[Grid, ...]]:
    if not isinstance(task, Mapping):
        raise ValueError("task must be a mapping")
    raw_train, raw_test = task["train"], task["test"]
    if (
        not isinstance(raw_train, Sequence)
        or isinstance(raw_train, (str, bytes))
        or not isinstance(raw_test, Sequence)
        or isinstance(raw_test, (str, bytes))
        or not raw_train
        or not raw_test
        or len(raw_train) + len(raw_test) > 16
    ):
        raise ValueError("invalid task arity")
    train: list[tuple[Grid, Grid]] = []
    tests: list[Grid] = []
    cells = 0
    for example in raw_train:
        if not isinstance(example, Mapping):
            raise ValueError("invalid training record")
        source, result = _grid(example["input"]), _grid(example["output"])
        cells += len(source) * len(source[0]) + len(result) * len(result[0])
        train.append((source, result))
    for example in raw_test:
        if not isinstance(example, Mapping):
            raise ValueError("invalid test record")
        source = _grid(example["input"])
        cells += len(source) * len(source[0])
        tests.append(source)
    if cells > MAX_TOTAL_CELLS:
        raise ValueError("cell budget exceeded")
    return tuple(train), tuple(tests)


def _cap(limits: Any) -> int:
    if limits is None:
        return MAX_CANDIDATES
    if isinstance(limits, bool):
        raise ValueError("invalid limit")
    if isinstance(limits, int):
        return min(MAX_CANDIDATES, max(1, limits))
    if not isinstance(limits, Mapping):
        raise ValueError("invalid limits")
    value = limits.get("max_candidates", limits.get("candidate_cap", MAX_CANDIDATES))
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError("invalid candidate cap")
    return min(MAX_CANDIDATES, value)


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _mode(grid: Grid) -> int:
    counts = Counter(value for row in grid for value in row)
    return min(counts, key=lambda value: (-counts[value], value))


def _components(
    grid: Grid,
    background: int,
    *,
    separate_colors: bool = True,
    radius: int = 1,
) -> list[dict[str, Any]]:
    remaining = {
        (r, c)
        for r, row in enumerate(grid)
        for c, value in enumerate(row)
        if value != background
    }
    result: list[dict[str, Any]] = []
    while remaining:
        seed = min(remaining)
        color = grid[seed[0]][seed[1]]
        queue = [seed]
        remaining.remove(seed)
        cells: list[tuple[int, int]] = []
        while queue:
            r, c = queue.pop()
            cells.append((r, c))
            for dr in range(-radius, radius + 1):
                for dc in range(-radius, radius + 1):
                    if not dr and not dc:
                        continue
                    rr, cc = r + dr, c + dc
                    if (rr, cc) not in remaining:
                        continue
                    if separate_colors and grid[rr][cc] != color:
                        continue
                    remaining.remove((rr, cc))
                    queue.append((rr, cc))
        rs, cs = [r for r, _ in cells], [c for _, c in cells]
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


def _crop(grid: Grid, r0: int, r1: int, c0: int, c1: int) -> Grid:
    return tuple(tuple(grid[r][c0 : c1 + 1]) for r in range(r0, r1 + 1))


def _transform(grid: Grid, name: str) -> Grid:
    if name == "identity":
        return grid
    if name == "mirror_horizontal":
        return tuple(tuple(row[::-1]) for row in grid)
    if name == "mirror_vertical":
        return grid[::-1]
    if name == "rotate180":
        return tuple(tuple(row[::-1]) for row in grid[::-1])
    raise UndefinedRule("unknown raster transform")


def _linear_extensions(nodes: Sequence[int], edges: set[tuple[int, int]]) -> list[tuple[int, ...]]:
    """Return a deterministic bounded prefix of the partial-order extensions."""
    orders: list[tuple[int, ...]] = []

    def visit(prefix: tuple[int, ...], remaining: frozenset[int]) -> None:
        if len(orders) >= MAX_LINE_EXTENSIONS:
            return
        if not remaining:
            orders.append(prefix)
            return
        available = sorted(
            node
            for node in remaining
            if all(lower not in remaining for lower, upper in edges if upper == node)
        )
        for node in available:
            visit(prefix + (node,), remaining - {node})

    visit((), frozenset(nodes))
    return orders


def _orthogonal_groups(cells: set[tuple[int, int]]) -> list[set[tuple[int, int]]]:
    groups: list[set[tuple[int, int]]] = []
    remaining = set(cells)
    while remaining:
        seed = min(remaining)
        remaining.remove(seed)
        queue = [seed]
        group = {seed}
        while queue:
            r, c = queue.pop()
            for neighbor in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    group.add(neighbor)
                    queue.append(neighbor)
        groups.append(group)
    return sorted(groups, key=lambda group: min(group))


def _execute(source: Grid, program: Mapping[str, Any]) -> Grid:
    kind = program["kind"]
    height, width = len(source), len(source[0])

    if kind == "unique_holed_object_color":
        background = _mode(source)
        objects = _components(source, background)
        holed = [
            obj
            for obj in objects
            if len(obj["cells"])
            < (obj["r1"] - obj["r0"] + 1) * (obj["c1"] - obj["c0"] + 1)
        ]
        if len(holed) != 1 or any(
            len(obj["cells"])
            != (obj["r1"] - obj["r0"] + 1) * (obj["c1"] - obj["c0"] + 1)
            for obj in objects
            if obj is not holed[0]
        ):
            raise UndefinedRule("holed object is not unique")
        return ((holed[0]["color"],),)

    if kind == "solid_rectangle_partition":
        background = _mode(source)
        rectangles = []
        for obj in _components(source, background):
            rh, cw = obj["r1"] - obj["r0"] + 1, obj["c1"] - obj["c0"] + 1
            if len(obj["cells"]) == rh * cw and len(obj["cells"]) >= 4:
                rectangles.append(obj)
        if len(rectangles) < 4 or len(rectangles) > 36:
            raise UndefinedRule("invalid rectangle population")
        row_edges = sorted({edge for obj in rectangles for edge in (obj["r0"], obj["r1"] + 1)})
        col_edges = sorted({edge for obj in rectangles for edge in (obj["c0"], obj["c1"] + 1)})
        row_spans = [
            (a, b)
            for a, b in zip(row_edges, row_edges[1:])
            if any(obj["r0"] <= a and b - 1 <= obj["r1"] for obj in rectangles)
        ]
        col_spans = [
            (a, b)
            for a, b in zip(col_edges, col_edges[1:])
            if any(obj["c0"] <= a and b - 1 <= obj["c1"] for obj in rectangles)
        ]
        result: list[tuple[int, ...]] = []
        for ra, rb in row_spans:
            row: list[int] = []
            for ca, cb in col_spans:
                covering = [
                    obj
                    for obj in rectangles
                    if obj["r0"] <= ra
                    and rb - 1 <= obj["r1"]
                    and obj["c0"] <= ca
                    and cb - 1 <= obj["c1"]
                ]
                if len(covering) != 1:
                    raise UndefinedRule("rectangle partition is incomplete")
                row.append(covering[0]["color"])
            result.append(tuple(row))
        if not result or len(result) > 12 or len(result[0]) > 12:
            raise UndefinedRule("rectangle partition output is invalid")
        return tuple(result)

    if kind == "row_palette_macro_mosaic":
        background = _mode(source)
        objects = _components(source, background, separate_colors=False)
        if not objects:
            raise UndefinedRule("no mosaic")
        main = max(objects, key=lambda obj: len(obj["cells"]))
        raster = _crop(source, main["r0"], main["r1"], main["c0"], main["c1"])
        rh, rw = len(raster), len(raster[0])
        row_keys = [tuple(sorted(set(row) - {background})) for row in raster]
        col_keys = [
            tuple(sorted({raster[r][c] for r in range(rh)} - {background}))
            for c in range(rw)
        ]

        def runs(keys: Sequence[tuple[int, ...]]) -> list[tuple[int, int]]:
            result: list[tuple[int, int]] = []
            start = 0
            for index in range(1, len(keys) + 1):
                if index == len(keys) or keys[index] != keys[start]:
                    if not keys[start]:
                        raise UndefinedRule("empty palette band")
                    result.append((start, index))
                    start = index
            return result

        row_runs, col_runs = runs(row_keys), runs(col_keys)
        if len(row_runs) > 10 or len(col_runs) > 10:
            raise UndefinedRule("macro mosaic is too large")
        coarse: list[tuple[int, ...]] = []
        for r0, r1 in row_runs:
            row: list[int] = []
            for c0, c1 in col_runs:
                counts = Counter(
                    raster[r][c]
                    for r in range(r0, r1)
                    for c in range(c0, c1)
                    if raster[r][c] != background
                )
                if not counts:
                    raise UndefinedRule("empty macro cell")
                row.append(min(counts, key=lambda value: (-counts[value], value)))
            coarse.append(tuple(row))
        return _transform(tuple(coarse), str(program["transform"]))

    if kind == "line_occlusion_order":
        background = _mode(source)
        colors = sorted(set(value for row in source for value in row) - {background})
        if not 2 <= len(colors) <= 9:
            raise UndefinedRule("line count is invalid")
        lines: dict[int, tuple[str, int]] = {}
        for color in colors:
            cells = [(r, c) for r, row in enumerate(source) for c, value in enumerate(row) if value == color]
            candidates: list[tuple[str, int]] = []
            descriptors = (
                ("row", [r for r, _ in cells]),
                ("column", [c for _, c in cells]),
                ("diagonal", [r - c for r, c in cells]),
                ("antidiagonal", [r + c for r, c in cells]),
            )
            for name, values in descriptors:
                if len(set(values)) == 1:
                    candidates.append((name, values[0]))
            if len(candidates) != 1:
                raise UndefinedRule("colored line is ambiguous")
            lines[color] = candidates[0]

        def on_line(r: int, c: int, line: tuple[str, int]) -> bool:
            name, value = line
            return (
                r == value
                if name == "row"
                else c == value
                if name == "column"
                else r - c == value
                if name == "diagonal"
                else r + c == value
            )

        edges: set[tuple[int, int]] = set()
        for index, a in enumerate(colors):
            for b in colors[index + 1 :]:
                intersections = [
                    (r, c)
                    for r in range(height)
                    for c in range(width)
                    if on_line(r, c, lines[a]) and on_line(r, c, lines[b])
                ]
                if len(intersections) != 1:
                    continue
                r, c = intersections[0]
                visible = source[r][c]
                if visible == a:
                    edges.add((b, a))
                elif visible == b:
                    edges.add((a, b))
        orders = _linear_extensions(colors, edges)
        if not orders:
            raise UndefinedRule("layer constraints are cyclic")
        rank = int(program.get("extension_rank", 0))
        if not 0 <= rank < MAX_LINE_EXTENSIONS:
            raise UndefinedRule("invalid extension rank")
        # A unique training order supports every bounded tie policy; a test
        # scene may leave independent layers observationally unordered.  The
        # portfolio then exposes the bounded linear-extension ambiguity rather
        # than smuggling in a task-specific tie break.
        return (orders[rank % len(orders)],)

    if kind == "rectangle_occlusion_order":
        background = _mode(source)
        colors = sorted(set(value for row in source for value in row) - {background})
        if not 2 <= len(colors) <= 8:
            raise UndefinedRule("outline count is invalid")
        boxes: dict[int, tuple[int, int, int, int]] = {}
        for color in colors:
            cells = {(r, c) for r, row in enumerate(source) for c, value in enumerate(row) if value == color}
            r0, r1 = min(r for r, _ in cells), max(r for r, _ in cells)
            c0, c1 = min(c for _, c in cells), max(c for _, c in cells)
            if r1 <= r0 or c1 <= c0 or any(
                r not in (r0, r1) and c not in (c0, c1) for r, c in cells
            ):
                raise UndefinedRule("color is not an outline")
            boxes[color] = (r0, r1, c0, c1)

        def perimeter(box: tuple[int, int, int, int]) -> set[tuple[int, int]]:
            r0, r1, c0, c1 = box
            return {
                (r, c)
                for r in range(r0, r1 + 1)
                for c in range(c0, c1 + 1)
                if r in (r0, r1) or c in (c0, c1)
            }

        outlines = {color: perimeter(box) for color, box in boxes.items()}
        edges: set[tuple[int, int]] = set()
        for index, a in enumerate(colors):
            for b in colors[index + 1 :]:
                winners = {
                    source[r][c]
                    for r, c in outlines[a] & outlines[b]
                    if source[r][c] in (a, b)
                }
                if winners == {a}:
                    edges.add((b, a))
                elif winners == {b}:
                    edges.add((a, b))
                elif len(winners) > 1:
                    raise UndefinedRule("outline overlap reverses layer order")
        orders = _linear_extensions(colors, edges)
        if not orders:
            raise UndefinedRule("outline constraints are cyclic")
        rank = int(program.get("extension_rank", 0))
        if not 0 <= rank < MAX_LINE_EXTENSIONS:
            raise UndefinedRule("invalid extension rank")
        return tuple((color,) for color in orders[rank % len(orders)])

    if kind == "divider_grid_collapse":
        base = _mode(source)
        full_rows = [r for r, row in enumerate(source) if len(set(row)) == 1 and row[0] != base]
        full_cols = [
            c
            for c in range(width)
            if len({source[r][c] for r in range(height)}) == 1 and source[0][c] != base
        ]
        separators = {source[r][0] for r in full_rows} | {source[0][c] for c in full_cols}
        if not full_rows or not full_cols or len(separators) != 1:
            raise UndefinedRule("divider grid is invalid")
        separator = next(iter(separators))
        full_row_set, full_col_set = set(full_rows), set(full_cols)
        if any(
            source[r][c] != (separator if r in full_row_set or c in full_col_set else base)
            for r in range(height)
            for c in range(width)
        ):
            raise UndefinedRule("divider raster is not uniform")

        def band_count(size: int, cuts: set[int]) -> int:
            return sum(index not in cuts and (index == 0 or index - 1 in cuts) for index in range(size))

        rh, rw = band_count(height, full_row_set), band_count(width, full_col_set)
        if not rh or not rw:
            raise UndefinedRule("divider grid has no cells")
        return tuple(tuple([base] * rw) for _ in range(rh))

    if kind == "lattice_corner_cell_decode":
        background = source[0][0]
        if any(source[r][c] != background for r, c in ((0, 0), (0, width-1), (height-1, 0), (height-1, width-1))):
            raise UndefinedRule("lattice background is not corner-stable")
        counts = Counter(value for row in source for value in row if value != background)
        if not counts:
            raise UndefinedRule("lattice color is absent")
        lattice = min(counts, key=lambda value: (-counts[value], value))
        line_rows = [r for r, row in enumerate(source) if background not in row]
        line_cols = [
            c for c in range(width)
            if all(source[r][c] != background for r in range(height))
        ]
        if len(line_rows) < 2 or len(line_cols) < 2:
            raise UndefinedRule("lattice has too few lines")
        decoded = [[background] * (len(line_cols) - 1) for _ in range(len(line_rows) - 1)]
        for r_index, (ra, rb) in enumerate(zip(line_rows, line_rows[1:])):
            for c_index, (ca, cb) in enumerate(zip(line_cols, line_cols[1:])):
                corners = {source[ra][ca], source[ra][cb], source[rb][ca], source[rb][cb]}
                if len(corners) == 1:
                    value = next(iter(corners))
                    if value not in (background, lattice):
                        decoded[r_index][c_index] = value
        marked = [
            (r, c)
            for r, row in enumerate(decoded)
            for c, value in enumerate(row)
            if value != background
        ]
        if not marked:
            raise UndefinedRule("lattice contains no encoded cells")
        r0, r1 = min(r for r, _ in marked), max(r for r, _ in marked)
        c0, c1 = min(c for _, c in marked), max(c for _, c in marked)
        if r1-r0+1 > 12 or c1-c0+1 > 12:
            raise UndefinedRule("decoded lattice payload is too large")
        return tuple(tuple(decoded[r][c0:c1 + 1]) for r in range(r0, r1 + 1))

    if kind == "background_panel_modes":
        background = _mode(source)
        empty_rows = {r for r, row in enumerate(source) if set(row) == {background}}
        empty_cols = {
            c for c in range(width)
            if {source[r][c] for r in range(height)} == {background}
        }

        def bands(size: int, empty: set[int]) -> list[tuple[int, int]]:
            result: list[tuple[int, int]] = []
            start = 0
            while start < size:
                while start < size and start in empty:
                    start += 1
                if start == size:
                    break
                end = start
                while end + 1 < size and end + 1 not in empty:
                    end += 1
                result.append((start, end))
                start = end + 1
            return result

        row_bands, col_bands = bands(height, empty_rows), bands(width, empty_cols)
        if len(row_bands) < 2 and len(col_bands) < 2:
            raise UndefinedRule("panel separators are absent")
        if len(row_bands) > 10 or len(col_bands) > 10:
            raise UndefinedRule("panel array is too large")
        result: list[tuple[int, ...]] = []
        for ra, rb in row_bands:
            row: list[int] = []
            for ca, cb in col_bands:
                counts = Counter(
                    source[r][c]
                    for r in range(ra, rb + 1)
                    for c in range(ca, cb + 1)
                    if source[r][c] != background
                )
                if not counts:
                    raise UndefinedRule("panel has no payload color")
                row.append(min(counts, key=lambda value: (-counts[value], value)))
            result.append(tuple(row))
        return tuple(result)

    if kind == "macro_block_occupancy":
        background = _mode(source)
        colors = sorted(set(value for row in source for value in row) - {background})
        if len(colors) != 2:
            raise UndefinedRule("occupancy scene needs structure and ink")
        totals = Counter(value for row in source for value in row if value != background)
        structure = min(colors, key=lambda value: (-totals[value], value))
        ink = next(value for value in colors if value != structure)
        cells = [(r, c) for r, row in enumerate(source) for c, value in enumerate(row) if value == structure]
        r0, r1 = min(r for r, _ in cells), max(r for r, _ in cells)
        c0, c1 = min(c for _, c in cells), max(c for _, c in cells)
        out_h, out_w = int(program["height"]), int(program["width"])
        if (r1-r0+1) % out_h or (c1-c0+1) % out_w:
            raise UndefinedRule("structure does not divide into macro cells")
        cell_h, cell_w = (r1-r0+1)//out_h, (c1-c0+1)//out_w
        if cell_h < 2 or cell_w < 2:
            raise UndefinedRule("macro blocks are too small")
        result: list[tuple[int, ...]] = []
        for gy in range(out_h):
            row: list[int] = []
            for gx in range(out_w):
                count = sum(
                    source[r][c] == structure
                    for r in range(r0 + gy*cell_h, r0 + (gy+1)*cell_h)
                    for c in range(c0 + gx*cell_w, c0 + (gx+1)*cell_w)
                )
                row.append(ink if count * 2 >= cell_h * cell_w else background)
            result.append(tuple(row))
        return tuple(result)

    if kind == "divider_cell_modes":
        outer = _mode(source)
        nonouter = [(r, c) for r, row in enumerate(source) for c, value in enumerate(row) if value != outer]
        if not nonouter:
            raise UndefinedRule("divider board is empty")
        r0, r1 = min(r for r, _ in nonouter), max(r for r, _ in nonouter)
        c0, c1 = min(c for _, c in nonouter), max(c for _, c in nonouter)
        board = _crop(source, r0, r1, c0, c1)
        bh, bw = len(board), len(board[0])
        candidates: list[Grid] = []
        for divider in sorted(set(value for row in board for value in row)):
            full_rows = {r for r, row in enumerate(board) if set(row) == {divider}}
            full_cols = {c for c in range(bw) if {board[r][c] for r in range(bh)} == {divider}}
            if not full_rows or not full_cols:
                continue

            def runs(size: int, cuts: set[int]) -> list[tuple[int, int]]:
                bands: list[tuple[int, int]] = []
                index = 0
                while index < size:
                    while index < size and index in cuts:
                        index += 1
                    if index == size:
                        break
                    end = index
                    while end + 1 < size and end + 1 not in cuts:
                        end += 1
                    bands.append((index, end))
                    index = end + 1
                return bands

            row_bands, col_bands = runs(bh, full_rows), runs(bw, full_cols)
            if not row_bands or not col_bands or len(row_bands) > 12 or len(col_bands) > 12:
                continue
            decoded = tuple(
                tuple(
                    _mode(tuple(tuple(board[r][c] for c in range(ca, cb+1)) for r in range(ra, rb+1)))
                    for ca, cb in col_bands
                )
                for ra, rb in row_bands
            )
            candidates.append(decoded)
        if len(set(candidates)) != 1:
            raise UndefinedRule("divider board interpretation is not unique")
        return candidates[0]

    if kind == "repeated_tile_disagreement":
        marker = int(program["marker"])
        interpretations: set[Grid] = set()
        for divider in sorted(set(value for row in source for value in row)):
            cut_rows = {r for r, row in enumerate(source) if set(row) == {divider}}
            cut_cols = {c for c in range(width) if {source[r][c] for r in range(height)} == {divider}}
            if not cut_rows or not cut_cols:
                continue

            def runs(size: int, cuts: set[int]) -> list[tuple[int, int]]:
                bands: list[tuple[int, int]] = []
                index = 0
                while index < size:
                    while index < size and index in cuts:
                        index += 1
                    if index == size:
                        break
                    end = index
                    while end+1 < size and end+1 not in cuts:
                        end += 1
                    bands.append((index, end))
                    index = end+1
                return bands

            row_bands, col_bands = runs(height, cut_rows), runs(width, cut_cols)
            shapes = {(rb-ra+1, cb-ca+1) for ra, rb in row_bands for ca, cb in col_bands}
            if len(shapes) != 1 or len(row_bands)*len(col_bands) < 4:
                continue
            th, tw = next(iter(shapes))
            tiles = [_crop(source, ra, rb, ca, cb) for ra, rb in row_bands for ca, cb in col_bands]
            result: list[tuple[int, ...]] = []
            disputed = False
            for r in range(th):
                row: list[int] = []
                for c in range(tw):
                    values = [tile[r][c] for tile in tiles]
                    counts = Counter(values)
                    common = min(counts, key=lambda value: (-counts[value], value))
                    if len(counts) > 1:
                        disputed = True
                        row.append(marker)
                    else:
                        row.append(common)
                result.append(tuple(row))
            if disputed:
                interpretations.add(tuple(result))
        if len(interpretations) != 1:
            raise UndefinedRule("repeated tiling is not unique")
        return next(iter(interpretations))

    if kind == "grid_payload_color_counts":
        background = source[0][0]
        interpretations: set[Grid] = set()
        for divider in sorted(set(value for row in source for value in row) - {background}):
            full_rows = {r for r, row in enumerate(source) if set(row) == {divider}}
            full_cols = {c for c in range(width) if {source[r][c] for r in range(height)} == {divider}}
            if not full_rows or not full_cols:
                continue
            payload = [
                obj for obj in _components(source, background)
                if obj["color"] != divider
            ]
            counts = Counter(obj["color"] for obj in payload)
            if not counts:
                continue
            out_w = max(counts.values())
            result = tuple(
                tuple([color]*count + [background]*(out_w-count))
                for color, count in sorted(counts.items(), key=lambda item: (item[1], item[0]))
            )
            interpretations.add(result)
        if len(interpretations) != 1:
            raise UndefinedRule("payload count grid is ambiguous")
        return next(iter(interpretations))

    if kind == "frame_marker_counts":
        background, marker = _mode(source), int(program["marker"])
        rows: list[tuple[int, int]] = []
        for color in sorted(set(value for row in source for value in row) - {background, marker}):
            cells = {(r, c) for r, row in enumerate(source) for c, value in enumerate(row) if value == color}
            r0, r1 = min(r for r, _ in cells), max(r for r, _ in cells)
            c0, c1 = min(c for _, c in cells), max(c for _, c in cells)
            if r1-r0 < 2 or c1-c0 < 2:
                continue
            perimeter = {
                (r, c)
                for r in range(r0, r1+1)
                for c in range(c0, c1+1)
                if r in (r0, r1) or c in (c0, c1)
            }
            if not {(r0,c0),(r0,c1),(r1,c0),(r1,c1)} <= cells or len(cells & perimeter)*2 < len(perimeter):
                continue
            count = sum(source[r][c] == marker for r in range(r0+1, r1) for c in range(c0+1, c1))
            if count:
                rows.append((count, color))
        if not rows:
            raise UndefinedRule("no marked frames")
        width_out = max(count for count, _ in rows)
        return tuple(
            tuple([color]*count + [background]*(width_out-count))
            for count, color in sorted(rows)
        )

    if kind == "paired_block_strip_extract":
        marker = int(program["marker"])
        blocks = [
            (r, c)
            for r in range(height-1)
            for c in range(width-1)
            if all(source[rr][cc] == marker for rr in (r, r+1) for cc in (c, c+1))
        ]
        by_row: dict[int, list[int]] = {}
        for r, c in blocks:
            by_row.setdefault(r, []).append(c)
        pairs = [(r, sorted(cols)) for r, cols in sorted(by_row.items()) if len(cols) == 2]
        if not pairs or any(len(cols) != 2 or cols[1]-cols[0] <= 2 for _, cols in pairs):
            raise UndefinedRule("2x2 marker pairs are invalid")
        widths = {cols[1]-cols[0]-2 for _, cols in pairs}
        if len(widths) != 1:
            raise UndefinedRule("marker strips have inconsistent widths")
        result: list[tuple[int, ...]] = []
        for r, (left, right) in pairs:
            result.extend(tuple(source[rr][left+2:right]) for rr in (r, r+1))
        return tuple(result)

    if kind == "swap_two_color_crop":
        background = _mode(source)
        colors = sorted(set(value for row in source for value in row) - {background})
        if len(colors) != 2:
            raise UndefinedRule("swap crop needs two colors")
        cells = [(r, c) for r, row in enumerate(source) for c, value in enumerate(row) if value != background]
        if not cells:
            raise UndefinedRule("empty swap crop")
        r0, r1 = min(r for r, _ in cells), max(r for r, _ in cells)
        c0, c1 = min(c for _, c in cells), max(c for _, c in cells)
        mapping = {colors[0]: colors[1], colors[1]: colors[0], background: background}
        return tuple(tuple(mapping[source[r][c]] for c in range(c0, c1 + 1)) for r in range(r0, r1 + 1))

    if kind == "component_count_pack":
        background = _mode(source)
        order = tuple(int(value) for value in program["order"])
        if set(order) != set(value for row in source for value in row) - {background}:
            raise UndefinedRule("component palette changed")
        objects = _components(source, background)
        if any(obj["r0"] != obj["r1"] or len(obj["cells"]) < 2 for obj in objects):
            raise UndefinedRule("count tokens are not horizontal bars")
        sequence = [color for color in order for _ in range(sum(obj["color"] == color for obj in objects))]
        out_h, out_w, padding = int(program["height"]), int(program["width"]), int(program["padding"])
        if len(sequence) > out_h * out_w:
            raise UndefinedRule("count pack overflows")
        sequence.extend([padding] * (out_h * out_w - len(sequence)))
        return tuple(tuple(sequence[r * out_w : (r + 1) * out_w]) for r in range(out_h))

    if kind == "halfturn_hidden_patch":
        marker = int(program["marker"])
        cells = {(r, c) for r, row in enumerate(source) for c, value in enumerate(row) if value == marker}
        if not cells:
            raise UndefinedRule("hidden patch marker is absent")
        r0, r1 = min(r for r, _ in cells), max(r for r, _ in cells)
        c0, c1 = min(c for _, c in cells), max(c for _, c in cells)
        if cells != {(r, c) for r in range(r0, r1 + 1) for c in range(c0, c1 + 1)}:
            raise UndefinedRule("hidden patch is not rectangular")
        if any(source[height - 1 - r][width - 1 - c] == marker for r, c in cells):
            raise UndefinedRule("half-turn reference is also hidden")
        return tuple(
            tuple(source[height - 1 - r][width - 1 - c] for c in range(c0, c1 + 1))
            for r in range(r0, r1 + 1)
        )

    if kind == "frame_scaled_glyph":
        background = _mode(source)
        colors = sorted(set(value for row in source for value in row) - {background})
        frames: list[tuple[int, int, int, int, int]] = []
        for color in colors:
            cells = {(r, c) for r, row in enumerate(source) for c, value in enumerate(row) if value == color}
            r0, r1 = min(r for r, _ in cells), max(r for r, _ in cells)
            c0, c1 = min(c for _, c in cells), max(c for _, c in cells)
            perimeter = {
                (r, c)
                for r in range(r0, r1 + 1)
                for c in range(c0, c1 + 1)
                if r in (r0, r1) or c in (c0, c1)
            }
            if cells == perimeter and r1-r0 > 2 and c1-c0 > 2:
                frames.append((color, r0, r1, c0, c1))
        if len(frames) != 1:
            raise UndefinedRule("scaled-glyph frame is not unique")
        frame, r0, r1, c0, c1 = frames[0]
        glyph_cells = [
            (r, c)
            for r, row in enumerate(source)
            for c, value in enumerate(row)
            if value not in (background, frame)
        ]
        glyph_colors = {source[r][c] for r, c in glyph_cells}
        if not glyph_cells or len(glyph_colors) != 1:
            raise UndefinedRule("scaled glyph is not monochrome")
        gr0, gr1 = min(r for r, _ in glyph_cells), max(r for r, _ in glyph_cells)
        gc0, gc1 = min(c for _, c in glyph_cells), max(c for _, c in glyph_cells)
        gh, gw = gr1-gr0+1, gc1-gc0+1
        inner_h, inner_w = r1-r0-1, c1-c0-1
        if inner_h % gh or inner_w % gw or inner_h // gh != inner_w // gw:
            raise UndefinedRule("glyph does not scale uniformly into frame")
        scale = inner_h // gh
        if not 1 <= scale <= 10:
            raise UndefinedRule("glyph scale is invalid")
        glyph_color = next(iter(glyph_colors))
        raster = [[frame] * (c1-c0+1)]
        for r in range(gh):
            expanded = []
            for c in range(gw):
                value = glyph_color if source[gr0+r][gc0+c] == glyph_color else background
                expanded.extend([value] * scale)
            for _ in range(scale):
                raster.append([frame] + expanded + [frame])
        raster.append([frame] * (c1-c0+1))
        return tuple(tuple(row) for row in raster)

    if kind == "first_row_color_bars":
        background = _mode(source)
        colors = sorted(set(value for row in source for value in row) - {background})
        first_rows = {
            color: min(r for r, row in enumerate(source) if color in row)
            for color in colors
        }
        if len(set(first_rows.values())) != len(colors):
            raise UndefinedRule("color arrivals are tied")
        sequence = [color for color in sorted(colors, key=lambda value: first_rows[value])]
        out_h, out_w = int(program["height"]), int(program["width"])
        if len(sequence) > out_h:
            raise UndefinedRule("color barcode overflows")
        sequence = [background] * (out_h - len(sequence)) + sequence
        return tuple(tuple([color] * out_w) for color in sequence)

    if kind == "template_gap_fill":
        background = _mode(source)
        objects = _components(source, background)
        outputs: set[Grid] = set()
        for candidate_index, candidate in enumerate(objects):
            r0, r1, c0, c1 = candidate["r0"], candidate["r1"], candidate["c0"], candidate["c1"]
            if r1 <= r0 or c1 <= c0 or len(candidate["cells"]) == (r1-r0+1)*(c1-c0+1):
                continue
            gaps = {(r, c) for r in range(r0, r1 + 1) for c in range(c0, c1 + 1) if source[r][c] == background}
            gap_groups = _orthogonal_groups(gaps)
            gap_shapes: list[tuple[set[tuple[int, int]], int, int]] = []
            valid = True
            for group in gap_groups:
                gr0, gr1 = min(r for r, _ in group), max(r for r, _ in group)
                gc0, gc1 = min(c for _, c in group), max(c for _, c in group)
                if len(group) != (gr1-gr0+1)*(gc1-gc0+1):
                    valid = False
                    break
                gap_shapes.append((group, gr1-gr0+1, gc1-gc0+1))
            if not valid or not gap_shapes:
                continue
            available: list[tuple[int, int, int, int]] = []
            for object_index, obj in enumerate(objects):
                if object_index == candidate_index:
                    continue
                rh, rw = obj["r1"]-obj["r0"]+1, obj["c1"]-obj["c0"]+1
                if len(obj["cells"]) == rh * rw:
                    available.append((object_index, obj["color"], rh, rw))
            fill_colors: list[int] = []
            used: set[int] = set()
            for _, rh, rw in gap_shapes:
                matches = [item for item in available if item[0] not in used and item[2:] == (rh, rw)]
                if not matches or len({item[1] for item in matches}) != 1:
                    valid = False
                    break
                chosen = min(matches)
                used.add(chosen[0])
                fill_colors.append(chosen[1])
            if not valid:
                continue
            raster = [list(row[c0 : c1 + 1]) for row in source[r0 : r1 + 1]]
            for (group, _, _), color in zip(gap_shapes, fill_colors):
                for r, c in group:
                    raster[r-r0][c-c0] = color
            outputs.add(tuple(tuple(row) for row in raster))
        if len(outputs) != 1:
            raise UndefinedRule("gap template is not unique")
        return next(iter(outputs))

    if kind == "labeled_component_pack":
        background = _mode(source)
        objects = _components(source, background)
        by_color: dict[int, list[dict[str, Any]]] = {}
        for obj in objects:
            by_color.setdefault(obj["color"], []).append(obj)
        candidates: list[tuple[list[dict[str, Any]], list[tuple[int, int]]]] = []
        for color, templates in by_color.items():
            if len(templates) < 2 or any(len(obj["cells"]) < 2 for obj in templates):
                continue
            labels = [obj for other, group in by_color.items() if other != color for obj in group]
            if len(labels) != len(templates) or any(len(obj["cells"]) != 1 for obj in labels):
                continue
            if len({(obj["r1"]-obj["r0"]+1, obj["c1"]-obj["c0"]+1) for obj in templates}) != 1:
                continue
            costs: list[tuple[int, tuple[int, ...]]] = []
            for assignment in permutations(range(len(labels))):
                cost = sum(
                    min(abs(lr-r)+abs(lc-c) for r, c in template["cells"])
                    for template, label_index in zip(templates, assignment)
                    for lr, lc in [labels[label_index]["cells"][0]]
                )
                costs.append((cost, assignment))
            best_cost = min(cost for cost, _ in costs)
            best = [assignment for cost, assignment in costs if cost == best_cost]
            if len(best) != 1:
                continue
            candidates.append((templates, [(labels[index]["color"], index) for index in best[0]]))
        if len(candidates) != 1:
            raise UndefinedRule("labeled component family is not unique")
        templates, assignments = candidates[0]
        row_centers = [obj["r0"] + obj["r1"] for obj in templates]
        col_centers = [obj["c0"] + obj["c1"] for obj in templates]
        horizontal = max(col_centers)-min(col_centers) > max(row_centers)-min(row_centers)
        order = sorted(range(len(templates)), key=lambda index: (
            templates[index]["c0"] if horizontal else templates[index]["r0"],
            templates[index]["r0"] if horizontal else templates[index]["c0"],
        ))
        tiles: list[Grid] = []
        for index in order:
            obj, color = templates[index], assignments[index][0]
            tile = tuple(
                tuple(color if source[r][c] == obj["color"] else background for c in range(obj["c0"], obj["c1"] + 1))
                for r in range(obj["r0"], obj["r1"] + 1)
            )
            tiles.append(tile)
        if horizontal:
            return tuple(tuple(value for tile in tiles for value in tile[r]) for r in range(len(tiles[0])))
        return tuple(row for tile in tiles for row in tile)

    if kind == "four_cluster_gap_pack":
        background = _mode(source)
        clusters = _components(source, background, separate_colors=False, radius=2)
        if len(clusters) != 4:
            raise UndefinedRule("need four proximity clusters")
        clusters = sorted(clusters, key=lambda obj: ((obj["r0"] + obj["r1"]), obj["c0"]))
        groups = (clusters[:2], clusters[2:])
        result = [[background] * 7 for _ in range(7)]
        for gy, group in enumerate(groups):
            for gx, obj in enumerate(sorted(group, key=lambda item: item["c0"] + item["c1"])):
                rh, rw = obj["r1"] - obj["r0"] + 1, obj["c1"] - obj["c0"] + 1
                if rh > 3 or rw > 3:
                    raise UndefinedRule("cluster exceeds 3x3 tile")
                for r, c in obj["cells"]:
                    result[gy * 4 + r - obj["r0"]][gx * 4 + c - obj["c0"]] = source[r][c]
        return tuple(tuple(row) for row in result)

    if kind == "paired_row_marker_extract":
        left_marker, right_marker = int(program["marker_a"]), int(program["marker_b"])
        rows: list[tuple[int, ...]] = []
        for row in source:
            if row.count(left_marker) == 1 and row.count(right_marker) == 1:
                a, b = row.index(left_marker), row.index(right_marker)
                lo, hi = sorted((a, b))
                if hi - lo < 2:
                    raise UndefinedRule("markers have no payload")
                rows.append(tuple(row[lo + 1 : hi]))
        if not rows or len({len(row) for row in rows}) != 1:
            raise UndefinedRule("paired marker rows are inconsistent")
        return tuple(rows)

    if kind == "marked_object_repair":
        background, marker = _mode(source), int(program["marker"])
        objects = _components(source, background, separate_colors=False)
        marked = [obj for obj in objects if any(source[r][c] == marker for r, c in obj["cells"])]
        if len(marked) != 1:
            raise UndefinedRule("marked object is not unique")
        obj = marked[0]
        colors = Counter(source[r][c] for r, c in obj["cells"] if source[r][c] != marker)
        if not colors:
            raise UndefinedRule("marked object has no repair color")
        repair = min(colors, key=lambda value: (-colors[value], value))
        cells = set(obj["cells"])
        return tuple(
            tuple(
                (repair if source[r][c] == marker else source[r][c]) if (r, c) in cells else background
                for c in range(obj["c0"], obj["c1"] + 1)
            )
            for r in range(obj["r0"], obj["r1"] + 1)
        )

    if kind == "corner_marker_interior_recolor":
        background = _mode(source)
        colors = sorted(set(value for row in source for value in row) - {background})
        marker_options: list[tuple[int, int, int, int, int]] = []
        for color in colors:
            cells = [(r, c) for r, row in enumerate(source) for c, value in enumerate(row) if value == color]
            if len(cells) != 4:
                continue
            r0, r1 = min(r for r, _ in cells), max(r for r, _ in cells)
            c0, c1 = min(c for _, c in cells), max(c for _, c in cells)
            if set(cells) == {(r0, c0), (r0, c1), (r1, c0), (r1, c1)} and r1-r0>1 and c1-c0>1:
                marker_options.append((color, r0, r1, c0, c1))
        if len(marker_options) != 1:
            raise UndefinedRule("corner marker rectangle is not unique")
        marker, r0, r1, c0, c1 = marker_options[0]
        return tuple(
            tuple(marker if source[r][c] != background else background for c in range(c0 + 1, c1))
            for r in range(r0 + 1, r1)
        )

    raise UndefinedRule("unknown schema")


def _programs(train: tuple[tuple[Grid, Grid], ...]) -> list[dict[str, Any]]:
    base = lambda kind, **params: {"schema": SCHEMA, "kind": kind, **params}
    programs = [
        base("unique_holed_object_color"),
        base("solid_rectangle_partition"),
        base("divider_grid_collapse"),
        base("swap_two_color_crop"),
        base("four_cluster_gap_pack"),
        base("corner_marker_interior_recolor"),
        base("template_gap_fill"),
        base("labeled_component_pack"),
        base("lattice_corner_cell_decode"),
        base("frame_scaled_glyph"),
        base("background_panel_modes"),
        base("divider_cell_modes"),
        base("grid_payload_color_counts"),
    ]
    programs.extend(base("line_occlusion_order", extension_rank=rank) for rank in range(MAX_LINE_EXTENSIONS))
    programs.extend(base("rectangle_occlusion_order", extension_rank=rank) for rank in range(MAX_LINE_EXTENSIONS))
    programs.extend(base("row_palette_macro_mosaic", transform=name) for name in (
        "identity", "mirror_horizontal", "mirror_vertical", "rotate180"
    ))
    source_colors = [set(value for row in source for value in row) for source, _ in train]
    result_colors = [set(value for row in result for value in row) for _, result in train]
    result_shapes = {(len(result), len(result[0])) for _, result in train}
    source_foregrounds = [
        set(value for row in source for value in row) - {_mode(source)}
        for source, _ in train
    ]
    if len(result_shapes) == 1:
        out_h, out_w = next(iter(result_shapes))
        programs.append(base("first_row_color_bars", height=out_h, width=out_w))
        programs.append(base("macro_block_occupancy", height=out_h, width=out_w))
        stable_foreground = set.intersection(*source_foregrounds)
        padding = set.union(*result_colors) - stable_foreground
        if len(stable_foreground) == 2 and len(padding) == 1:
            for order in permutations(sorted(stable_foreground)):
                programs.append(
                    base(
                        "component_count_pack",
                        height=out_h,
                        width=out_w,
                        order=list(order),
                        padding=next(iter(padding)),
                    )
                )
    hidden = set.intersection(*source_colors) - set.union(*result_colors)
    if len(hidden) == 2:
        a, b = sorted(hidden)
        programs.append(base("paired_row_marker_extract", marker_a=a, marker_b=b))
    marker_candidates = set.intersection(*source_colors) - set.union(*result_colors)
    for marker in sorted(marker_candidates):
        programs.append(base("marked_object_repair", marker=marker))
        programs.append(base("halfturn_hidden_patch", marker=marker))
        programs.append(base("frame_marker_counts", marker=marker))
    novel_result_colors = set.intersection(*result_colors) - set.union(*source_colors)
    for marker in sorted(novel_result_colors):
        programs.append(base("repeated_tile_disagreement", marker=marker))
    for marker in sorted(set.intersection(*source_colors)):
        programs.append(base("paired_block_strip_extract", marker=marker))
    return sorted(programs, key=lambda item: (len(_canonical(item)), _canonical(item)))


def compile_task(task: Any, limits: Any = None) -> list[dict[str, Any]]:
    try:
        cap = _cap(limits)
        train, tests = _sanitize(task)
        admitted = []
        for program in _programs(train):
            try:
                replay = tuple(_execute(source, program) for source, _ in train)
                if any(actual != expected for actual, (_, expected) in zip(replay, train)):
                    continue
                forecast = tuple(_execute(source, program) for source in tests)
            except (KeyError, TypeError, ValueError, IndexError, ZeroDivisionError):
                continue
            description = _canonical(program)
            admitted.append((len(description), description, program, replay, forecast))
        best: dict[str, Any] = {}
        for item in admitted:
            behavior = _canonical(item[4])
            if behavior not in best or item[:2] < best[behavior][:2]:
                best[behavior] = item
        result = []
        for complexity, _, program, replay, forecast in sorted(best.values(), key=lambda x: x[:2])[:cap]:
            result.append(
                {
                    "family": "targeted_smaller_g11",
                    "program": program,
                    "train_outputs": [[list(row) for row in grid] for grid in replay],
                    "test_outputs": [[list(row) for row in grid] for grid in forecast],
                    "complexity": complexity,
                    "evidence": {
                        "all_demos_exact": True,
                        "demo_count": len(train),
                        "selection": "minimum_description_length",
                        "schema_kind": program["kind"],
                    },
                }
            )
        return result
    except (KeyError, TypeError, ValueError, IndexError, ZeroDivisionError):
        return []


__all__ = ["compile_task"]
