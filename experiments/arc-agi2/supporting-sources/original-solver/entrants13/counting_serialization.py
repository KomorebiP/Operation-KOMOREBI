"""Bounded counting and serialization entrant for PR-LASM Block 13.

This module searches a small, explicit grammar of programs which turn counts
or ordered object measurements into grids.  Every emitted program replays all
demonstrations exactly.  The compiler accepts only the sanitized tournament
view (training pairs and test inputs), is deterministic, and never consults a
task identifier, solution, fingerprint, or external corpus.

The grammar covers scalar counts, unary/geometric count renderings, compact
histograms, sorted component packing, repeated motifs, and two conventional
small numeral alphabets.  Candidates are ordered by a simple description
length before the finite program and candidate caps are applied.

Author: Komorebi P.
"""

from __future__ import annotations

from collections import Counter, deque
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from functools import lru_cache
import hashlib
import json
import math
from typing import Any, Iterable


Grid = tuple[tuple[int, ...], ...]
JSONGrid = list[list[int]]


@dataclass(frozen=True)
class Limits:
    max_side: int = 30
    max_objects: int = 128
    max_programs: int = 6000
    max_candidates: int = 96
    max_executions: int = 500000

    @classmethod
    def parse(cls, value: Any) -> "Limits":
        if value is None:
            return cls()
        if not isinstance(value, Mapping):
            return cls()
        aliases = {"candidate_cap": "max_candidates"}
        fields: dict[str, int] = {}
        for name in ("max_side", "max_objects", "max_programs", "max_candidates", "max_executions"):
            raw = value.get(name, value.get(next((a for a, b in aliases.items() if b == name), ""), getattr(cls, name)))
            if isinstance(raw, bool) or not isinstance(raw, int) or raw < 0:
                raise ValueError("invalid finite limit")
            fields[name] = raw
        return cls(**fields)


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _plain(grid: Grid) -> JSONGrid:
    return [list(row) for row in grid]


def _as_grid(value: Any, max_side: int) -> Grid:
    if not isinstance(value, list) or not value or len(value) > max_side:
        raise ValueError("invalid grid height")
    width: int | None = None
    rows: list[tuple[int, ...]] = []
    for raw_row in value:
        if not isinstance(raw_row, list) or not raw_row or len(raw_row) > max_side:
            raise ValueError("invalid grid row")
        if width is None:
            width = len(raw_row)
        if len(raw_row) != width:
            raise ValueError("ragged grid")
        row: list[int] = []
        for cell in raw_row:
            if isinstance(cell, bool) or not isinstance(cell, int) or not 0 <= cell <= 9:
                raise ValueError("invalid ARC color")
            row.append(int(cell))
        rows.append(tuple(row))
    return tuple(rows)


def _sanitize(task: Any, limits: Limits) -> tuple[list[tuple[Grid, Grid]], list[Grid]]:
    if not isinstance(task, Mapping):
        raise ValueError("task must be a mapping")
    train_raw, test_raw = task.get("train"), task.get("test")
    if (
        not isinstance(train_raw, Sequence)
        or isinstance(train_raw, (str, bytes))
        or not train_raw
        or not isinstance(test_raw, Sequence)
        or isinstance(test_raw, (str, bytes))
        or not test_raw
        or len(train_raw) > 10
        or len(test_raw) > 10
    ):
        raise ValueError("invalid task arity")
    train: list[tuple[Grid, Grid]] = []
    for example in train_raw:
        if not isinstance(example, Mapping):
            raise ValueError("invalid demonstration")
        train.append((_as_grid(example["input"], limits.max_side), _as_grid(example["output"], limits.max_side)))
    tests: list[Grid] = []
    for example in test_raw:
        if not isinstance(example, Mapping):
            raise ValueError("invalid test")
        # Intentionally access only the input member of a test item.
        tests.append(_as_grid(example["input"], limits.max_side))
    return train, tests


def _shape(grid: Grid) -> tuple[int, int]:
    return len(grid), len(grid[0])


@lru_cache(maxsize=1024)
def _mode(grid: Grid) -> int:
    counts = Counter(cell for row in grid for cell in row)
    return min(counts, key=lambda color: (-counts[color], color))


@lru_cache(maxsize=1024)
def _palette(grid: Grid) -> tuple[int, ...]:
    return tuple(sorted({cell for row in grid for cell in row}))


@lru_cache(maxsize=1024)
def _first_palette(grid: Grid) -> tuple[int, ...]:
    result: list[int] = []
    for row in grid:
        for color in row:
            if color not in result:
                result.append(color)
    return tuple(result)


@lru_cache(maxsize=2048)
def _frequency_palette(grid: Grid, descending: bool) -> tuple[int, ...]:
    counts = Counter(cell for row in grid for cell in row)
    return tuple(sorted(counts, key=lambda c: ((-counts[c] if descending else counts[c]), c)))


def _resolve_selector(grid: Grid, selector: Mapping[str, Any]) -> int:
    kind = selector["kind"]
    if kind == "literal":
        return int(selector["color"])
    if kind == "mode":
        return _mode(grid)
    palette = _palette(grid)
    background = _mode(grid)
    nonbackground = [c for c in palette if c != background]
    if kind == "unique_nonbackground":
        if len(nonbackground) != 1:
            raise ValueError("not unique")
        return nonbackground[0]
    nonzero = [c for c in palette if c != 0]
    if kind == "unique_nonzero":
        if len(nonzero) != 1:
            raise ValueError("not one nonzero color")
        return nonzero[0]
    if kind == "least_frequent_nonbackground":
        counts = Counter(cell for row in grid for cell in row)
        if not nonbackground:
            raise ValueError("no foreground")
        return min(nonbackground, key=lambda c: (counts[c], c))
    if kind == "most_frequent_nonbackground":
        counts = Counter(cell for row in grid for cell in row)
        if not nonbackground:
            raise ValueError("no foreground")
        return min(nonbackground, key=lambda c: (-counts[c], c))
    if kind == "least_frequent_nonzero":
        counts = Counter(cell for row in grid for cell in row)
        if not nonzero:
            raise ValueError("no nonzero color")
        return min(nonzero, key=lambda c: (counts[c], c))
    if kind == "most_frequent_nonzero":
        counts = Counter(cell for row in grid for cell in row)
        if not nonzero:
            raise ValueError("no nonzero color")
        return min(nonzero, key=lambda c: (-counts[c], c))
    if kind == "minimum_nonbackground":
        if not nonbackground:
            raise ValueError("no foreground")
        return min(nonbackground)
    if kind == "maximum_nonbackground":
        if not nonbackground:
            raise ValueError("no foreground")
        return max(nonbackground)
    if kind == "minimum_nonzero":
        if not nonzero:
            raise ValueError("no nonzero color")
        return min(nonzero)
    if kind == "maximum_nonzero":
        if not nonzero:
            raise ValueError("no nonzero color")
        return max(nonzero)
    if kind == "first_nonbackground":
        for c in _first_palette(grid):
            if c != background:
                return c
        raise ValueError("no foreground")
    if kind == "first_nonzero":
        for c in _first_palette(grid):
            if c != 0:
                return c
        raise ValueError("no nonzero color")
    if kind == "palette_rank":
        return palette[int(selector["index"])]
    if kind == "frequency_rank":
        return _frequency_palette(grid, bool(selector["descending"]))[int(selector["index"])]
    if kind == "first_rank":
        return _first_palette(grid)[int(selector["index"])]
    raise ValueError("unknown color selector")


def _selector_cost(selector: Mapping[str, Any]) -> int:
    return {
        "mode": 1,
        "unique_nonbackground": 1,
        "unique_nonzero": 1,
        "least_frequent_nonbackground": 2,
        "most_frequent_nonbackground": 2,
        "minimum_nonbackground": 2,
        "maximum_nonbackground": 2,
        "first_nonbackground": 2,
        "least_frequent_nonzero": 2,
        "most_frequent_nonzero": 2,
        "minimum_nonzero": 2,
        "maximum_nonzero": 2,
        "first_nonzero": 2,
        "palette_rank": 3,
        "frequency_rank": 4,
        "first_rank": 4,
        "literal": 5,
    }.get(str(selector.get("kind")), 8)


def _selector_inventory(grids: Sequence[Grid]) -> list[dict[str, Any]]:
    maximum_palette = max(len(_palette(grid)) for grid in grids)
    result: list[dict[str, Any]] = [
        {"kind": "mode"},
        {"kind": "unique_nonbackground"},
        {"kind": "least_frequent_nonbackground"},
        {"kind": "most_frequent_nonbackground"},
        {"kind": "minimum_nonbackground"},
        {"kind": "maximum_nonbackground"},
        {"kind": "first_nonbackground"},
        {"kind": "unique_nonzero"},
        {"kind": "least_frequent_nonzero"},
        {"kind": "most_frequent_nonzero"},
        {"kind": "minimum_nonzero"},
        {"kind": "maximum_nonzero"},
        {"kind": "first_nonzero"},
    ]
    for index in range(maximum_palette):
        result.extend(
            [
                {"kind": "palette_rank", "index": index},
                {"kind": "frequency_rank", "index": index, "descending": True},
                {"kind": "frequency_rank", "index": index, "descending": False},
                {"kind": "first_rank", "index": index},
            ]
        )
    result.extend({"kind": "literal", "color": color} for color in range(10))
    unique = {_canonical(item): item for item in result}
    return sorted(unique.values(), key=lambda item: (_selector_cost(item), _canonical(item)))


def _background(grid: Grid, name: str) -> int:
    if name == "mode":
        return _mode(grid)
    if name == "zero":
        return 0
    raise ValueError("unknown background")


def _neighbors(row: int, col: int, connectivity: int) -> Iterable[tuple[int, int]]:
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == dc == 0:
                continue
            if connectivity == 4 and abs(dr) + abs(dc) != 1:
                continue
            yield row + dr, col + dc


@lru_cache(maxsize=4096)
def _components(
    grid: Grid,
    background_name: str,
    connectivity: int,
    partition: str,
    max_objects: int,
) -> list[dict[str, Any]]:
    h, w = _shape(grid)
    bg = _background(grid, background_name)
    unseen = {(r, c) for r in range(h) for c in range(w) if grid[r][c] != bg}
    result: list[dict[str, Any]] = []
    while unseen:
        start = min(unseen)
        color = grid[start[0]][start[1]]
        queue = deque([start])
        unseen.remove(start)
        cells: list[tuple[int, int]] = []
        while queue:
            r, c = queue.popleft()
            cells.append((r, c))
            for rr, cc in _neighbors(r, c, connectivity):
                if (rr, cc) not in unseen:
                    continue
                if partition == "monochrome" and grid[rr][cc] != color:
                    continue
                unseen.remove((rr, cc))
                queue.append((rr, cc))
        r0, c0 = min(cells)
        rows = [p[0] for p in cells]
        cols = [p[1] for p in cells]
        counts = Counter(grid[r][c] for r, c in cells)
        representative = min(counts, key=lambda x: (-counts[x], x))
        result.append(
            {
                "cells": tuple(sorted(cells)),
                "size": len(cells),
                "bbox": (min(rows), min(cols), max(rows), max(cols)),
                "anchor": (r0, c0),
                "color": representative,
            }
        )
        if len(result) > max_objects:
            raise ValueError("object cap exceeded")
    return sorted(result, key=lambda obj: obj["anchor"])


@lru_cache(maxsize=2048)
def _holes(grid: Grid, background_name: str, connectivity: int) -> int:
    h, w = _shape(grid)
    bg = _background(grid, background_name)
    unseen = {(r, c) for r in range(h) for c in range(w) if grid[r][c] == bg}
    holes = 0
    while unseen:
        start = min(unseen)
        queue = deque([start])
        unseen.remove(start)
        touches = False
        while queue:
            r, c = queue.popleft()
            touches |= r in (0, h - 1) or c in (0, w - 1)
            for rr, cc in _neighbors(r, c, connectivity):
                if (rr, cc) in unseen:
                    unseen.remove((rr, cc))
                    queue.append((rr, cc))
        holes += int(not touches)
    return holes


@lru_cache(maxsize=2048)
def _runs(grid: Grid, background_name: str, axis: str) -> int:
    bg = _background(grid, background_name)
    rows: Iterable[Iterable[int]]
    if axis == "rows":
        rows = grid
    else:
        rows = zip(*grid)
    total = 0
    for row in rows:
        active = False
        for cell in row:
            if cell != bg and not active:
                total += 1
                active = True
            elif cell == bg:
                active = False
    return total


def _scalar(grid: Grid, spec: Mapping[str, Any], max_objects: int) -> int:
    kind = spec["kind"]
    bg_name = str(spec.get("background", "mode"))
    bg = _background(grid, bg_name)
    h, w = _shape(grid)
    if kind == "foreground_cells":
        return sum(cell != bg for row in grid for cell in row)
    if kind == "distinct_foreground_colors":
        return len({cell for row in grid for cell in row if cell != bg})
    if kind == "color_cells":
        color = _resolve_selector(grid, spec["color"])
        return sum(cell == color for row in grid for cell in row)
    if kind == "occupied_rows":
        return sum(any(cell != bg for cell in row) for row in grid)
    if kind == "occupied_columns":
        return sum(any(grid[r][c] != bg for r in range(h)) for c in range(w))
    if kind == "full_rows":
        return sum(all(cell != bg for cell in row) for row in grid)
    if kind == "full_columns":
        return sum(all(grid[r][c] != bg for r in range(h)) for c in range(w))
    if kind == "runs":
        return _runs(grid, bg_name, str(spec["axis"]))
    if kind == "components":
        return len(_components(grid, bg_name, int(spec["connectivity"]), str(spec["partition"]), max_objects))
    if kind == "holes":
        return _holes(grid, bg_name, int(spec["connectivity"]))
    if kind == "isolated_cells":
        objects = _components(grid, bg_name, int(spec["connectivity"]), str(spec["partition"]), max_objects)
        return sum(obj["size"] == 1 for obj in objects)
    if kind == "rectangular_objects":
        objects = _components(grid, bg_name, int(spec["connectivity"]), str(spec["partition"]), max_objects)
        return sum(obj["size"] == (obj["bbox"][2] - obj["bbox"][0] + 1) * (obj["bbox"][3] - obj["bbox"][1] + 1) for obj in objects)
    raise ValueError("unknown scalar statistic")


def _scalar_specs(selectors: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for background in ("mode", "zero"):
        result.extend(
            {"kind": kind, "background": background}
            for kind in (
                "foreground_cells",
                "distinct_foreground_colors",
                "occupied_rows",
                "occupied_columns",
                "full_rows",
                "full_columns",
            )
        )
        for axis in ("rows", "columns"):
            result.append({"kind": "runs", "background": background, "axis": axis})
        for connectivity in (4, 8):
            result.append({"kind": "holes", "background": background, "connectivity": connectivity})
            for partition in ("union", "monochrome"):
                for kind in ("components", "isolated_cells", "rectangular_objects"):
                    result.append(
                        {
                            "kind": kind,
                            "background": background,
                            "connectivity": connectivity,
                            "partition": partition,
                        }
                    )
    # Color counts use only the shortest role descriptions plus all literals.
    color_selectors = [s for s in selectors if _selector_cost(s) <= 2 or s["kind"] == "literal"]
    for selector in color_selectors:
        result.append({"kind": "color_cells", "color": dict(selector), "background": "mode"})
    unique = {_canonical(item): item for item in result}
    return sorted(unique.values(), key=lambda item: (_stat_cost(item), _canonical(item)))


def _stat_cost(spec: Mapping[str, Any]) -> int:
    cost = {
        "foreground_cells": 1,
        "components": 2,
        "distinct_foreground_colors": 2,
        "occupied_rows": 2,
        "occupied_columns": 2,
        "color_cells": 3,
        "holes": 3,
        "runs": 3,
        "isolated_cells": 4,
        "full_rows": 4,
        "full_columns": 4,
        "rectangular_objects": 5,
    }.get(str(spec["kind"]), 8)
    cost += int(spec.get("background") == "zero")
    cost += int(spec.get("connectivity") == 8)
    if "color" in spec:
        cost += _selector_cost(spec["color"])
    return cost


def _eval_dimension(expr: Mapping[str, Any], n: int) -> int:
    kind = expr["kind"]
    if kind == "constant":
        value = int(expr["value"])
    elif kind == "affine":
        value = int(expr["scale"]) * n + int(expr["offset"])
    elif kind == "ceil_sqrt":
        value = math.ceil(math.sqrt(n))
    elif kind == "floor_sqrt":
        value = math.floor(math.sqrt(n))
    else:
        raise ValueError("unknown dimension expression")
    if not 1 <= value <= 30:
        raise ValueError("output dimension outside ARC domain")
    return value


def _dimension_cost(expr: Mapping[str, Any]) -> int:
    if expr["kind"] == "affine":
        return 1 + abs(int(expr["scale"]) - 1) + abs(int(expr["offset"]))
    if expr["kind"] in {"ceil_sqrt", "floor_sqrt"}:
        return 3
    return 4


def _dimension_expressions(values: Sequence[int], targets: Sequence[int]) -> list[dict[str, Any]]:
    proposals: list[dict[str, Any]] = []
    for scale in (1, 2, 3):
        for offset in range(-4, 5):
            proposals.append({"kind": "affine", "scale": scale, "offset": offset})
    proposals.extend(({"kind": "ceil_sqrt"}, {"kind": "floor_sqrt"}))
    if len(set(targets)) == 1:
        proposals.append({"kind": "constant", "value": int(targets[0])})
    result = []
    for proposal in proposals:
        try:
            if all(_eval_dimension(proposal, n) == target for n, target in zip(values, targets)):
                result.append(proposal)
        except ValueError:
            continue
    unique = {_canonical(item): item for item in result}
    return sorted(unique.values(), key=lambda item: (_dimension_cost(item), _canonical(item)))[:6]


_DIGITS_3X3: dict[int, tuple[str, ...]] = {
    0: ("111", "101", "111"), 1: ("010", "110", "010"),
    2: ("110", "010", "111"), 3: ("110", "011", "110"),
    4: ("101", "111", "001"), 5: ("111", "110", "011"),
    6: ("100", "111", "111"), 7: ("111", "001", "001"),
    8: ("111", "111", "111"), 9: ("111", "111", "001"),
}


_SEGMENTS = {
    0: "abcedf", 1: "bc", 2: "abdeg", 3: "abcdg", 4: "bcfg",
    5: "acdfg", 6: "acdefg", 7: "abc", 8: "abcdefg", 9: "abcdfg",
}


def _mask(kind: str, n: int, h: int, w: int) -> set[tuple[int, int]]:
    cells = [(r, c) for r in range(h) for c in range(w)]
    if kind == "all":
        return set(cells)
    if kind == "prefix_row":
        if n > len(cells): raise ValueError("count exceeds canvas")
        return set(cells[:n])
    if kind == "suffix_row":
        if n > len(cells): raise ValueError("count exceeds canvas")
        return set(cells[len(cells) - n :]) if n else set()
    column_cells = [(r, c) for c in range(w) for r in range(h)]
    if kind == "prefix_column":
        if n > len(cells): raise ValueError("count exceeds canvas")
        return set(column_cells[:n])
    if kind == "suffix_column":
        if n > len(cells): raise ValueError("count exceeds canvas")
        return set(column_cells[len(cells) - n :]) if n else set()
    if kind == "outline":
        return {(r, c) for r, c in cells if r in (0, h - 1) or c in (0, w - 1)}
    if kind == "main_diagonal":
        return {(r, c) for r, c in cells if r == c}
    if kind == "anti_diagonal":
        return {(r, c) for r, c in cells if r + c == w - 1}
    if kind == "both_diagonals":
        return {(r, c) for r, c in cells if r == c or r + c == w - 1}
    if kind == "lower_triangle":
        return {(r, c) for r, c in cells if c <= r}
    if kind == "upper_triangle":
        return {(r, c) for r, c in cells if c >= r}
    if kind == "checkerboard":
        return {(r, c) for r, c in cells if (r + c) % 2 == 0}
    if kind == "digit_3x3":
        if n not in _DIGITS_3X3 or (h, w) != (3, 3):
            raise ValueError("digit outside alphabet")
        return {(r, c) for r in range(3) for c in range(3) if _DIGITS_3X3[n][r][c] == "1"}
    if kind == "digit_3x5":
        if n not in _SEGMENTS or (h, w) != (5, 3):
            raise ValueError("digit outside alphabet")
        active = _SEGMENTS[n]
        segment_cells = {
            "a": {(0, 0), (0, 1), (0, 2)}, "b": {(0, 2), (1, 2), (2, 2)},
            "c": {(2, 2), (3, 2), (4, 2)}, "d": {(4, 0), (4, 1), (4, 2)},
            "e": {(2, 0), (3, 0), (4, 0)}, "f": {(0, 0), (1, 0), (2, 0)},
            "g": {(2, 0), (2, 1), (2, 2)},
        }
        return set().union(*(segment_cells[s] for s in active))
    raise ValueError("unknown scalar mask")


def _matching_selectors(
    inputs: Sequence[Grid],
    desired: Sequence[int],
    inventory: Sequence[Mapping[str, Any]],
    signature_index: Mapping[tuple[int, ...], list[dict[str, Any]]] | None = None,
) -> list[dict[str, Any]]:
    if signature_index is not None:
        matches = [dict(item) for item in signature_index.get(tuple(desired), [])]
    else:
        matches = []
        for selector in inventory:
            try:
                if all(_resolve_selector(grid, selector) == value for grid, value in zip(inputs, desired)):
                    matches.append(dict(selector))
            except (IndexError, ValueError):
                continue
    # Preserve a compact ambiguity basis: the four shortest role descriptions,
    # one explicitly-zero-relative role, and one literal.  This keeps both of
    # the important transfer alternatives without multiplying every induced
    # mask by a long list of train-equivalent color names.
    chosen = matches[:4]
    for predicate in (
        lambda item: "nonzero" in str(item.get("kind", "")),
        lambda item: item.get("kind") == "literal",
    ):
        extra = next((item for item in matches if predicate(item)), None)
        if extra is not None and _canonical(extra) not in {_canonical(item) for item in chosen}:
            chosen.append(extra)
    return chosen


def _selector_signature_index(
    inputs: Sequence[Grid], inventory: Sequence[Mapping[str, Any]]
) -> dict[tuple[int, ...], list[dict[str, Any]]]:
    result: dict[tuple[int, ...], list[dict[str, Any]]] = {}
    for selector in inventory:
        try:
            signature = tuple(_resolve_selector(grid, selector) for grid in inputs)
        except (IndexError, ValueError):
            continue
        result.setdefault(signature, []).append(dict(selector))
    return result


def _induce_scalar_renderers(
    spec: Mapping[str, Any],
    train: Sequence[tuple[Grid, Grid]],
    selectors: Sequence[Mapping[str, Any]],
    max_objects: int,
    selector_index: Mapping[tuple[int, ...], list[dict[str, Any]]] | None = None,
) -> list[dict[str, Any]]:
    inputs = [source for source, _ in train]
    targets = [target for _, target in train]
    try:
        values = [_scalar(source, spec, max_objects) for source in inputs]
    except ValueError:
        return []
    programs: list[dict[str, Any]] = [{"kind": "scalar_numeric_cell", "statistic": dict(spec)}]
    heights = [len(target) for target in targets]
    widths = [len(target[0]) for target in targets]
    height_exprs = _dimension_expressions(values, heights)
    width_exprs = _dimension_expressions(values, widths)
    patterns = (
        "all", "prefix_row", "prefix_column", "suffix_row", "suffix_column",
        "outline", "main_diagonal", "anti_diagonal", "both_diagonals",
        "lower_triangle", "upper_triangle", "checkerboard", "digit_3x3", "digit_3x5",
    )
    for height in height_exprs:
        for width in width_exprs:
            for pattern in patterns:
                fill_values: list[int] = []
                background_values: list[int] = []
                uses_background = False
                valid = True
                for n, target in zip(values, targets):
                    h, w = _shape(target)
                    try:
                        selected = _mask(pattern, n, h, w)
                    except ValueError:
                        valid = False
                        break
                    inside = {target[r][c] for r, c in selected}
                    outside = {target[r][c] for r in range(h) for c in range(w) if (r, c) not in selected}
                    if len(inside) != 1 or len(outside) > 1:
                        valid = False
                        break
                    fill_values.append(next(iter(inside)))
                    if outside:
                        uses_background = True
                        background_values.append(next(iter(outside)))
                    else:
                        background_values.append(next(iter(inside)))
                if not valid:
                    continue
                fills = _matching_selectors(inputs, fill_values, selectors, selector_index)
                backgrounds = _matching_selectors(inputs, background_values, selectors, selector_index) if uses_background else [None]
                for fill in fills:
                    for background in backgrounds:
                        programs.append(
                            {
                                "kind": "scalar_mask",
                                "statistic": dict(spec),
                                "height": dict(height),
                                "width": dict(width),
                                "mask": pattern,
                                "fill": fill,
                                "background": background,
                            }
                        )
    return programs


def _vector(grid: Grid, spec: Mapping[str, Any], max_objects: int) -> list[tuple[int, int | None]]:
    bg_name = str(spec.get("background", "mode"))
    bg = _background(grid, bg_name)
    kind = spec["kind"]
    if kind in {"row_counts", "column_counts"}:
        lines = grid if kind == "row_counts" else tuple(zip(*grid))
        values = [(sum(cell != bg for cell in line), None) for line in lines]
        if spec.get("drop_zeros"):
            values = [item for item in values if item[0] != 0]
        return values
    if kind == "color_counts":
        counts = Counter(cell for row in grid for cell in row if cell != bg)
        first = [c for c in _first_palette(grid) if c != bg]
        items = [(counts[c], c) for c in counts]
        order = spec["order"]
        if order == "color": items.sort(key=lambda x: x[1])
        elif order == "first": items.sort(key=lambda x: first.index(x[1]))
        elif order == "count_ascending": items.sort(key=lambda x: (x[0], x[1]))
        elif order == "count_descending": items.sort(key=lambda x: (-x[0], x[1]))
        else: raise ValueError("bad vector order")
        return items
    if kind in {"component_sizes", "component_colors"}:
        objects = list(_components(grid, bg_name, int(spec["connectivity"]), str(spec["partition"]), max_objects))
        order = spec["order"]
        if order == "reading": pass
        elif order == "reverse_reading": objects.reverse()
        elif order == "size_ascending": objects.sort(key=lambda x: (x["size"], x["anchor"]))
        elif order == "size_descending": objects.sort(key=lambda x: (-x["size"], x["anchor"]))
        elif order == "color_ascending": objects.sort(key=lambda x: (x["color"], x["anchor"]))
        elif order == "color_descending": objects.sort(key=lambda x: (-x["color"], x["anchor"]))
        else: raise ValueError("bad component order")
        if kind == "component_colors":
            return [(int(obj["color"]), int(obj["color"])) for obj in objects]
        return [(int(obj["size"]), int(obj["color"])) for obj in objects]
    raise ValueError("unknown vector")


def _vector_specs() -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for background in ("mode", "zero"):
        for kind in ("row_counts", "column_counts"):
            for drop in (False, True):
                result.append({"kind": kind, "background": background, "drop_zeros": drop})
        for order in ("color", "first", "count_ascending", "count_descending"):
            result.append({"kind": "color_counts", "background": background, "order": order})
        for connectivity in (4, 8):
            for partition in ("union", "monochrome"):
                for order in ("reading", "reverse_reading", "size_ascending", "size_descending", "color_ascending", "color_descending"):
                    for kind in ("component_sizes", "component_colors"):
                        result.append(
                            {"kind": kind, "background": background, "connectivity": connectivity, "partition": partition, "order": order}
                        )
    return sorted(result, key=lambda item: (_vector_cost(item), _canonical(item)))


def _vector_cost(spec: Mapping[str, Any]) -> int:
    cost = 3 + int(spec.get("background") == "zero") + int(spec.get("connectivity") == 8)
    cost += {"reading": 0, "color": 0, "first": 1, "size_ascending": 1, "size_descending": 1}.get(str(spec.get("order")), 2)
    cost += int(bool(spec.get("drop_zeros")))
    return cost


def _render_vector(grid: Grid, program: Mapping[str, Any], max_objects: int) -> Grid:
    items = _vector(grid, program["vector"], max_objects)
    values = [value for value, _ in items]
    if not values:
        raise ValueError("empty serialization")
    mode = program["render"]
    if mode == "numeric_row":
        if any(not 0 <= value <= 9 for value in values): raise ValueError("count not a color")
        return (tuple(values),)
    if mode == "numeric_column":
        if any(not 0 <= value <= 9 for value in values): raise ValueError("count not a color")
        return tuple((value,) for value in values)
    maximum = max(values)
    if maximum < 1 or maximum > 30 or len(values) > 30:
        raise ValueError("histogram outside ARC domain")
    orientation = str(program["orientation"])
    if orientation == "vertical": h, w = maximum, len(values)
    else: h, w = len(values), maximum
    background = _resolve_selector(grid, program["background"])
    output = [[background for _ in range(w)] for _ in range(h)]
    for index, (value, own_color) in enumerate(items):
        if program["color_mode"] == "item":
            if own_color is None: raise ValueError("no item color")
            fill = own_color
        else:
            fill = _resolve_selector(grid, program["fill"])
        if orientation == "vertical":
            rows = range(h - value, h) if program["anchor"] == "end" else range(value)
            for r in rows: output[r][index] = fill
        else:
            cols = range(w - value, w) if program["anchor"] == "end" else range(value)
            for c in cols: output[index][c] = fill
    return tuple(tuple(row) for row in output)


def _crop_object(grid: Grid, obj: Mapping[str, Any], background: int, recolor: int | None = None) -> Grid:
    r0, c0, r1, c1 = obj["bbox"]
    cells = set(obj["cells"])
    return tuple(
        tuple((recolor if recolor is not None else grid[r][c]) if (r, c) in cells else background for c in range(c0, c1 + 1))
        for r in range(r0, r1 + 1)
    )


def _ordered_objects(grid: Grid, spec: Mapping[str, Any], max_objects: int) -> list[dict[str, Any]]:
    objects = list(_components(grid, str(spec["background"]), int(spec["connectivity"]), str(spec["partition"]), max_objects))
    order = spec["order"]
    if order == "reading": pass
    elif order == "reverse_reading": objects.reverse()
    elif order == "size_ascending": objects.sort(key=lambda x: (x["size"], x["anchor"]))
    elif order == "size_descending": objects.sort(key=lambda x: (-x["size"], x["anchor"]))
    elif order == "color_ascending": objects.sort(key=lambda x: (x["color"], x["anchor"]))
    elif order == "color_descending": objects.sort(key=lambda x: (-x["color"], x["anchor"]))
    else: raise ValueError("unknown object order")
    return objects


def _pack_objects(grid: Grid, program: Mapping[str, Any], max_objects: int) -> Grid:
    objects = _ordered_objects(grid, program, max_objects)
    if not objects: raise ValueError("no objects")
    bg = _background(grid, str(program["background"]))
    recolor = None if program["recolor"] is None else _resolve_selector(grid, program["recolor"])
    crops = [_crop_object(grid, obj, bg, recolor) for obj in objects]
    axis, gap, align = str(program["axis"]), int(program["gap"]), str(program["align"])
    if axis == "horizontal":
        h = max(len(crop) for crop in crops); w = sum(len(crop[0]) for crop in crops) + gap * (len(crops) - 1)
    else:
        h = sum(len(crop) for crop in crops) + gap * (len(crops) - 1); w = max(len(crop[0]) for crop in crops)
    if max(h, w) > 30: raise ValueError("packed output too large")
    output = [[bg for _ in range(w)] for _ in range(h)]
    cursor = 0
    for crop in crops:
        ch, cw = _shape(crop)
        if axis == "horizontal":
            offset = 0 if align == "start" else (h - ch if align == "end" else (h - ch) // 2)
            for r in range(ch):
                for c in range(cw): output[offset + r][cursor + c] = crop[r][c]
            cursor += cw + gap
        else:
            offset = 0 if align == "start" else (w - cw if align == "end" else (w - cw) // 2)
            for r in range(ch):
                for c in range(cw): output[cursor + r][offset + c] = crop[r][c]
            cursor += ch + gap
    return tuple(tuple(row) for row in output)


def _select_object(objects: list[dict[str, Any]], name: str) -> dict[str, Any]:
    if not objects: raise ValueError("no motif")
    if name == "only":
        if len(objects) != 1: raise ValueError("not one object")
        return objects[0]
    if name == "first": return objects[0]
    if name == "last": return objects[-1]
    if name == "smallest": return min(objects, key=lambda x: (x["size"], x["anchor"]))
    if name == "largest": return min(objects, key=lambda x: (-x["size"], x["anchor"]))
    raise ValueError("unknown motif selector")


def _repeat_motif(grid: Grid, program: Mapping[str, Any], max_objects: int) -> Grid:
    count = _scalar(grid, program["statistic"], max_objects)
    if not 1 <= count <= 30: raise ValueError("bad repetition count")
    objects = _components(grid, str(program["background"]), int(program["connectivity"]), str(program["partition"]), max_objects)
    motif_obj = _select_object(objects, str(program["object_selector"]))
    bg = _background(grid, str(program["background"]))
    recolor = None if program["recolor"] is None else _resolve_selector(grid, program["recolor"])
    motif = _crop_object(grid, motif_obj, bg, recolor)
    mh, mw = _shape(motif); gap = int(program["gap"]); layout = str(program["layout"])
    if layout == "horizontal": rows, cols = 1, count
    elif layout == "vertical": rows, cols = count, 1
    elif layout == "square": rows = cols = math.ceil(math.sqrt(count))
    elif layout == "diagonal": rows = cols = count
    else: raise ValueError("unknown repeat layout")
    h = rows * mh + (rows - 1) * gap; w = cols * mw + (cols - 1) * gap
    if max(h, w) > 30: raise ValueError("repeat output too large")
    output = [[bg for _ in range(w)] for _ in range(h)]
    for index in range(count):
        if layout == "diagonal": rr = cc = index
        else: rr, cc = divmod(index, cols)
        r0, c0 = rr * (mh + gap), cc * (mw + gap)
        for r in range(mh):
            for c in range(mw): output[r0 + r][c0 + c] = motif[r][c]
    return tuple(tuple(row) for row in output)


def execute_program(grid_value: Any, program: Mapping[str, Any], limits: Mapping[str, Any] | None = None) -> JSONGrid:
    """Execute one JSON-safe program independently of the compiler."""

    bounds = Limits.parse(limits)
    grid = _as_grid(grid_value, bounds.max_side) if isinstance(grid_value, list) else grid_value
    if not isinstance(grid, tuple): raise ValueError("invalid grid")
    kind = program["kind"]
    if kind == "scalar_numeric_cell":
        n = _scalar(grid, program["statistic"], bounds.max_objects)
        if not 0 <= n <= 9: raise ValueError("count not an ARC color")
        result: Grid = ((n,),)
    elif kind == "scalar_mask":
        n = _scalar(grid, program["statistic"], bounds.max_objects)
        h, w = _eval_dimension(program["height"], n), _eval_dimension(program["width"], n)
        selected = _mask(str(program["mask"]), n, h, w)
        fill = _resolve_selector(grid, program["fill"])
        background = fill if program["background"] is None else _resolve_selector(grid, program["background"])
        result = tuple(tuple(fill if (r, c) in selected else background for c in range(w)) for r in range(h))
    elif kind == "vector_render":
        result = _render_vector(grid, program, bounds.max_objects)
    elif kind == "object_pack":
        result = _pack_objects(grid, program, bounds.max_objects)
    elif kind == "repeat_motif":
        result = _repeat_motif(grid, program, bounds.max_objects)
    else:
        raise ValueError("unknown counting program")
    _as_grid(_plain(result), bounds.max_side)
    return _plain(result)


def _program_cost(program: Mapping[str, Any]) -> int:
    kind = program["kind"]
    if kind == "scalar_numeric_cell":
        return 2 + _stat_cost(program["statistic"])
    if kind == "scalar_mask":
        return (
            3 + _stat_cost(program["statistic"]) + _dimension_cost(program["height"])
            + _dimension_cost(program["width"]) + _selector_cost(program["fill"])
            + (0 if program["background"] is None else _selector_cost(program["background"]))
            + {"all": 0, "prefix_row": 1, "prefix_column": 1, "main_diagonal": 2, "anti_diagonal": 2}.get(str(program["mask"]), 3)
        )
    if kind == "vector_render":
        return 5 + _vector_cost(program["vector"]) + int(program["render"] not in {"numeric_row", "numeric_column"}) * 3
    if kind == "object_pack":
        return 9 + int(program["partition"] == "union") + int(program["connectivity"] == 8) + int(program["gap"]) + int(program["recolor"] is not None) * 3
    if kind == "repeat_motif":
        return 10 + _stat_cost(program["statistic"]) + int(program["gap"]) + int(program["recolor"] is not None) * 3
    return 99


def _enumerate_programs(train: Sequence[tuple[Grid, Grid]], selectors: Sequence[Mapping[str, Any]], limits: Limits) -> list[dict[str, Any]]:
    programs: list[dict[str, Any]] = []
    scalar_specs = _scalar_specs(selectors)
    selector_index = _selector_signature_index([source for source, _ in train], selectors)
    for spec in scalar_specs:
        programs.extend(_induce_scalar_renderers(spec, train, selectors, limits.max_objects, selector_index))
    render_fills = [
        *selectors[:7],
        *({"kind": "literal", "color": color} for color in range(10)),
    ]
    render_backgrounds = [{"kind": "mode"}, {"kind": "literal", "color": 0}]
    for vector in _vector_specs():
        programs.extend(
            [
                {"kind": "vector_render", "vector": vector, "render": "numeric_row"},
                {"kind": "vector_render", "vector": vector, "render": "numeric_column"},
            ]
        )
        for orientation in ("vertical", "horizontal"):
            for anchor in ("end", "start"):
                for background in render_backgrounds:
                    programs.append(
                        {
                            "kind": "vector_render", "vector": vector, "render": "histogram",
                            "orientation": orientation, "anchor": anchor, "color_mode": "item",
                            "fill": None, "background": dict(background),
                        }
                    )
                for fill in render_fills:
                    for background in render_backgrounds:
                        programs.append(
                            {
                                "kind": "vector_render", "vector": vector, "render": "histogram",
                                "orientation": orientation, "anchor": anchor, "color_mode": "unified",
                                "fill": dict(fill), "background": dict(background),
                            }
                        )
    object_selectors = [None, *selectors[:6]]
    for background in ("mode", "zero"):
        for connectivity in (4, 8):
            for partition in ("monochrome", "union"):
                for order in ("reading", "reverse_reading", "size_ascending", "size_descending", "color_ascending", "color_descending"):
                    for axis in ("horizontal", "vertical"):
                        for gap in (0, 1):
                            for align in ("start", "end", "center"):
                                for recolor in object_selectors:
                                    programs.append(
                                        {
                                            "kind": "object_pack", "background": background,
                                            "connectivity": connectivity, "partition": partition,
                                            "order": order, "axis": axis, "gap": gap, "align": align,
                                            "recolor": recolor,
                                        }
                                    )
    # Keep motif search narrower: it is a higher-description-length family.
    repeat_specs = scalar_specs[:20]
    for statistic in repeat_specs:
        for background in ("mode", "zero"):
            for selector in ("only", "first", "smallest", "largest"):
                for layout in ("horizontal", "vertical", "square", "diagonal"):
                    for gap in (0, 1):
                        for recolor in object_selectors[:4]:
                            programs.append(
                                {
                                    "kind": "repeat_motif", "statistic": statistic,
                                    "background": background, "connectivity": 4,
                                    "partition": "monochrome", "object_selector": selector,
                                    "layout": layout, "gap": gap, "recolor": recolor,
                                }
                            )
    unique = {_canonical(program): program for program in programs}
    # Scalar renderers are induced from output dimensions, masks, and colors,
    # whereas the remaining schemas come from a larger generic cross product.
    # Reserve half the finite budget for each stratum so a sea of short object
    # pack descriptions cannot starve an induced count renderer (or vice
    # versa).  Ordering remains MDL-first within each declared stratum.
    scalar = sorted(
        (p for p in unique.values() if p["kind"] in {"scalar_numeric_cell", "scalar_mask"}),
        key=lambda p: (_program_cost(p), _canonical(p)),
    )
    generic = sorted(
        (p for p in unique.values() if p["kind"] not in {"scalar_numeric_cell", "scalar_mask"}),
        key=lambda p: (_program_cost(p), _canonical(p)),
    )
    scalar_cap = min(len(scalar), (limits.max_programs + 1) // 2)
    selected = scalar[:scalar_cap] + generic[: limits.max_programs - scalar_cap]
    return sorted(selected, key=lambda p: (_program_cost(p), _canonical(p)))


def compile_task(task: Any, limits: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    """Compile exact-demo-fit counting candidates under explicit finite caps."""

    try:
        bounds = Limits.parse(limits)
        if bounds.max_programs == 0 or bounds.max_candidates == 0 or bounds.max_executions == 0:
            return []
        train, tests = _sanitize(task, bounds)
        inputs = [source for source, _ in train]
        selector_inventory = _selector_inventory(inputs)
        programs = _enumerate_programs(train, selector_inventory, bounds)
        best_by_behavior: dict[str, dict[str, Any]] = {}
        executions = 0
        exhausted = False
        for program in programs:
            replay: list[JSONGrid] = []
            exact = True
            try:
                for source, target in train:
                    executions += 1
                    if executions > bounds.max_executions:
                        exhausted = True
                        break
                    prediction = execute_program(_plain(source), program, limits)
                    if prediction != _plain(target):
                        exact = False
                        break
                    replay.append(prediction)
                if exhausted:
                    break
                if not exact:
                    continue
                predictions = []
                for source in tests:
                    executions += 1
                    if executions > bounds.max_executions:
                        exhausted = True
                        break
                    predictions.append(execute_program(_plain(source), program, limits))
                if exhausted:
                    break
            except (IndexError, KeyError, TypeError, ValueError, ZeroDivisionError):
                continue
            behavior = hashlib.sha256(_canonical(predictions).encode("utf-8")).hexdigest()
            complexity = _program_cost(program)
            candidate = {
                "family": "counting_serialization",
                "program": json.loads(_canonical(program)),
                "train_outputs": replay,
                "test_outputs": predictions,
                "complexity": complexity,
                "evidence": {
                    "all_demonstrations_exact": True,
                    "bounded_program_search": True,
                    "description_length": complexity,
                    "demonstrations": len(train),
                    "behavior_hash": behavior,
                    "label_access": "none",
                },
            }
            previous = best_by_behavior.get(behavior)
            if previous is None or (complexity, _canonical(program)) < (previous["complexity"], _canonical(previous["program"])):
                best_by_behavior[behavior] = candidate
        if exhausted:
            # A partial inventory can look spuriously unique.  Abstain rather
            # than allow a resource cutoff to become a selection mechanism.
            return []
        result = sorted(
            best_by_behavior.values(),
            key=lambda item: (item["complexity"], item["evidence"]["behavior_hash"], _canonical(item["program"])),
        )
        return result[: bounds.max_candidates]
    except (IndexError, KeyError, TypeError, ValueError, OverflowError):
        return []


__all__ = ["Limits", "compile_task", "execute_program"]
