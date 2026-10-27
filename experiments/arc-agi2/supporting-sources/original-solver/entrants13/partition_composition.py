"""Panel and partition composition entrant for PR-LASM Block 13.

This module searches a deliberately bounded language of panel programs.  It
recognizes separator-line and equal-chunk partitions, then tries selection,
separator removal/rearrangement, transparent overlays, Boolean support
algebra, and panel comparisons.  A program is returned only when executing it
replays every training output exactly.

The compiler reads training input/output pairs and test *inputs* only.  It
does not inspect task identifiers, task fingerprints, test outputs, solution
files, or external corpora.  All ordering and tie breaking is deterministic.

Author: Komorebi P.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import itertools
import json
from typing import Any, Iterable


Grid = tuple[tuple[int, ...], ...]


@dataclass(frozen=True)
class Limits:
    max_side: int = 30
    max_panels: int = 25
    max_partitions: int = 72
    max_hypotheses: int = 14000
    max_candidates: int = 256

    @classmethod
    def from_value(cls, value: Any) -> "Limits":
        if value is None:
            return cls()
        if not isinstance(value, Mapping):
            raise ValueError("limits must be a mapping")

        def positive(name: str, default: int) -> int:
            raw = value.get(name, default)
            if isinstance(raw, bool) or not isinstance(raw, int) or raw < 1:
                return default
            return int(raw)

        candidate_default = positive("candidate_cap", cls.max_candidates)
        return cls(
            max_side=min(30, positive("max_side", cls.max_side)),
            max_panels=positive("max_panels", cls.max_panels),
            max_partitions=positive("max_partitions", cls.max_partitions),
            max_hypotheses=positive("max_hypotheses", cls.max_hypotheses),
            max_candidates=positive("max_candidates", candidate_default),
        )


@dataclass(frozen=True)
class PanelSet:
    panels: tuple[Grid, ...]
    rows: int
    cols: int
    separator: int | None


def _grid(value: Any, max_side: int = 30) -> Grid:
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
        for raw in raw_row:
            if isinstance(raw, bool) or not isinstance(raw, int) or not 0 <= raw <= 9:
                raise ValueError("invalid ARC color")
            row.append(int(raw))
        rows.append(tuple(row))
    return tuple(rows)


def _plain(grid: Grid) -> list[list[int]]:
    return [list(row) for row in grid]


def _shape(grid: Grid) -> tuple[int, int]:
    return len(grid), len(grid[0])


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sanitize(task: Any, limits: Limits) -> tuple[list[tuple[Grid, Grid]], list[Grid]]:
    if not isinstance(task, Mapping):
        raise ValueError("task must be a mapping")
    raw_train = task["train"]
    raw_test = task["test"]
    if (
        not isinstance(raw_train, Sequence)
        or isinstance(raw_train, (str, bytes))
        or not raw_train
        or not isinstance(raw_test, Sequence)
        or isinstance(raw_test, (str, bytes))
    ):
        raise ValueError("invalid task examples")
    train: list[tuple[Grid, Grid]] = []
    for example in raw_train:
        if not isinstance(example, Mapping):
            raise ValueError("invalid training example")
        # These are the only training fields this entrant reads.
        train.append((_grid(example["input"], limits.max_side), _grid(example["output"], limits.max_side)))
    tests: list[Grid] = []
    for example in raw_test:
        if not isinstance(example, Mapping):
            raise ValueError("invalid test example")
        # Deliberately never access a test output, even when a caller supplies one.
        tests.append(_grid(example["input"], limits.max_side))
    return train, tests


def _palette(grid: Grid) -> tuple[int, ...]:
    return tuple(sorted({cell for row in grid for cell in row}))


def _counts(grid: Grid) -> Counter[int]:
    return Counter(cell for row in grid for cell in row)


def _frequency_order(grid: Grid, descending: bool) -> tuple[int, ...]:
    counts = _counts(grid)
    return tuple(
        sorted(counts, key=lambda color: ((-counts[color] if descending else counts[color]), color))
    )


def _first_order(grid: Grid) -> tuple[int, ...]:
    seen: list[int] = []
    for row in grid:
        for color in row:
            if color not in seen:
                seen.append(color)
    return tuple(seen)


def _mode(grid: Grid) -> int:
    return _frequency_order(grid, True)[0]


def _color(selector: Mapping[str, Any], grid: Grid, panel_set: PanelSet | None = None) -> int:
    kind = selector.get("kind")
    if kind == "literal":
        value = int(selector["value"])
    elif kind == "mode":
        value = _mode(grid)
    elif kind == "least_frequent":
        value = _frequency_order(grid, False)[0]
    elif kind == "frequency_rank":
        value = _frequency_order(grid, bool(selector.get("descending", True)))[int(selector["rank"])]
    elif kind == "first_rank":
        value = _first_order(grid)[int(selector["rank"])]
    elif kind == "palette_rank":
        value = _palette(grid)[int(selector["rank"])]
    elif kind == "separator":
        if panel_set is None or panel_set.separator is None:
            raise ValueError("partition has no separator color")
        value = panel_set.separator
    elif kind in {"panel_mode", "panel_least_frequent", "panel_palette_min", "panel_palette_max"}:
        if panel_set is None:
            raise ValueError("panel selector needs a partition")
        panel = panel_set.panels[int(selector["panel"])]
        if kind == "panel_mode":
            value = _mode(panel)
        elif kind == "panel_least_frequent":
            value = _frequency_order(panel, False)[0]
        elif kind == "panel_palette_min":
            value = min(_palette(panel))
        else:
            value = max(_palette(panel))
    else:
        raise ValueError("unknown color selector")
    if not 0 <= value <= 9:
        raise ValueError("selector did not resolve to an ARC color")
    return int(value)


def _base_color_selectors() -> list[dict[str, Any]]:
    selectors: list[dict[str, Any]] = [
        {"kind": "mode"},
        {"kind": "least_frequent"},
    ]
    selectors.extend(
        {"kind": "frequency_rank", "descending": descending, "rank": rank}
        for descending in (True, False)
        for rank in range(4)
    )
    selectors.extend({"kind": "first_rank", "rank": rank} for rank in range(4))
    selectors.extend({"kind": "palette_rank", "rank": rank} for rank in range(4))
    selectors.extend({"kind": "literal", "value": value} for value in range(10))
    return selectors


def _output_color_selectors(panel_count: int, has_separator: bool) -> list[dict[str, Any]]:
    result = _base_color_selectors()
    if has_separator:
        result.insert(0, {"kind": "separator"})
    for panel in range(panel_count):
        result.extend(
            [
                {"kind": "panel_mode", "panel": panel},
                {"kind": "panel_least_frequent", "panel": panel},
                {"kind": "panel_palette_min", "panel": panel},
                {"kind": "panel_palette_max", "panel": panel},
            ]
        )
    # Canonical deduplication retains the first, more relational spelling.
    unique: dict[str, dict[str, Any]] = {}
    for selector in result:
        unique.setdefault(_canonical(selector), selector)
    return list(unique.values())


def _selector_cost(selector: Mapping[str, Any]) -> int:
    kind = str(selector.get("kind"))
    if kind in {"mode", "least_frequent", "separator"}:
        return 1
    if kind.startswith("panel_") or kind.endswith("_rank"):
        return 2
    return 3


def _bands(separator_flags: Sequence[bool]) -> list[tuple[int, int]]:
    bands: list[tuple[int, int]] = []
    start: int | None = None
    for index, is_separator in enumerate(separator_flags):
        if is_separator:
            if start is not None:
                bands.append((start, index))
                start = None
        elif start is None:
            start = index
    if start is not None:
        bands.append((start, len(separator_flags)))
    return bands


def _slice(grid: Grid, row_band: tuple[int, int], col_band: tuple[int, int]) -> Grid:
    r0, r1 = row_band
    c0, c1 = col_band
    if r0 >= r1 or c0 >= c1:
        raise ValueError("empty panel")
    return tuple(tuple(row[c0:c1]) for row in grid[r0:r1])


def _decompose(grid: Grid, spec: Mapping[str, Any]) -> PanelSet:
    height, width = _shape(grid)
    kind = spec["kind"]
    separator: int | None = None
    if kind in {"separator_rows", "separator_cols", "separator_grid"}:
        separator = _color(spec["color"], grid)
        row_flags = [all(cell == separator for cell in row) for row in grid]
        col_flags = [all(grid[row][col] == separator for row in range(height)) for col in range(width)]
        if kind == "separator_rows":
            row_bands = _bands(row_flags)
            col_bands = [(0, width)]
            if not any(row_flags) or len(row_bands) < 2:
                raise ValueError("no row partition")
        elif kind == "separator_cols":
            row_bands = [(0, height)]
            col_bands = _bands(col_flags)
            if not any(col_flags) or len(col_bands) < 2:
                raise ValueError("no column partition")
        else:
            row_bands = _bands(row_flags)
            col_bands = _bands(col_flags)
            if not any(row_flags) or not any(col_flags) or len(row_bands) < 2 or len(col_bands) < 2:
                raise ValueError("no grid partition")
    elif kind in {"uniform_rows", "uniform_cols", "uniform_grid"}:
        row_flags = [len(set(row)) == 1 for row in grid]
        col_flags = [len({grid[row][col] for row in range(height)}) == 1 for col in range(width)]
        if kind == "uniform_rows":
            row_bands = _bands(row_flags)
            col_bands = [(0, width)]
            if not any(row_flags) or len(row_bands) < 2:
                raise ValueError("no uniform-row partition")
            colors = {grid[index][0] for index, flag in enumerate(row_flags) if flag}
        elif kind == "uniform_cols":
            row_bands = [(0, height)]
            col_bands = _bands(col_flags)
            if not any(col_flags) or len(col_bands) < 2:
                raise ValueError("no uniform-column partition")
            colors = {grid[0][index] for index, flag in enumerate(col_flags) if flag}
        else:
            row_bands = _bands(row_flags)
            col_bands = _bands(col_flags)
            if not any(row_flags) or not any(col_flags) or len(row_bands) < 2 or len(col_bands) < 2:
                raise ValueError("no uniform-line grid partition")
            colors = {grid[index][0] for index, flag in enumerate(row_flags) if flag}
            colors.update(grid[0][index] for index, flag in enumerate(col_flags) if flag)
        separator = next(iter(colors)) if len(colors) == 1 else None
    elif kind == "framed_separator_grid":
        separator = _color(spec["color"], grid)
        coordinates = [
            (row, col)
            for row in range(height)
            for col in range(width)
            if grid[row][col] == separator
        ]
        if not coordinates:
            raise ValueError("framed separator is absent")
        r0 = min(row for row, _ in coordinates)
        r1 = max(row for row, _ in coordinates) + 1
        c0 = min(col for _, col in coordinates)
        c1 = max(col for _, col in coordinates) + 1
        cropped = _slice(grid, (r0, r1), (c0, c1))
        crop_h, crop_w = _shape(cropped)
        row_flags = [all(cell == separator for cell in row) for row in cropped]
        col_flags = [
            all(cropped[row][col] == separator for row in range(crop_h))
            for col in range(crop_w)
        ]
        row_bands = [(r0 + a, r0 + b) for a, b in _bands(row_flags)]
        col_bands = [(c0 + a, c0 + b) for a, b in _bands(col_flags)]
        if not any(row_flags) or not any(col_flags) or len(row_bands) < 2 or len(col_bands) < 2:
            raise ValueError("no framed separator lattice")
    elif kind == "equal_rows":
        parts = int(spec["parts"])
        if parts < 2 or height % parts:
            raise ValueError("rows do not divide evenly")
        step = height // parts
        row_bands = [(index * step, (index + 1) * step) for index in range(parts)]
        col_bands = [(0, width)]
    elif kind == "equal_cols":
        parts = int(spec["parts"])
        if parts < 2 or width % parts:
            raise ValueError("columns do not divide evenly")
        step = width // parts
        row_bands = [(0, height)]
        col_bands = [(index * step, (index + 1) * step) for index in range(parts)]
    elif kind == "equal_grid":
        row_parts, col_parts = int(spec["row_parts"]), int(spec["col_parts"])
        if row_parts < 2 or col_parts < 2 or height % row_parts or width % col_parts:
            raise ValueError("grid does not divide evenly")
        rh, cw = height // row_parts, width // col_parts
        row_bands = [(index * rh, (index + 1) * rh) for index in range(row_parts)]
        col_bands = [(index * cw, (index + 1) * cw) for index in range(col_parts)]
    else:
        raise ValueError("unknown partition")
    panels = tuple(_slice(grid, row_band, col_band) for row_band in row_bands for col_band in col_bands)
    return PanelSet(panels, len(row_bands), len(col_bands), separator)


def _partition_cost(spec: Mapping[str, Any]) -> int:
    kind = str(spec["kind"])
    role_cost = _selector_cost(spec["color"]) if "color" in spec else 0
    if kind in {"separator_rows", "separator_cols"}:
        return 1 + role_cost
    if kind == "separator_grid":
        return 2 + role_cost
    if kind in {"uniform_rows", "uniform_cols"}:
        return 3
    if kind == "uniform_grid":
        return 4
    if kind == "framed_separator_grid":
        return 4 + role_cost
    if kind in {"equal_rows", "equal_cols"}:
        return 4
    return 5


def _partition_specs(inputs: Sequence[Grid], limits: Limits) -> list[dict[str, Any]]:
    raw: list[dict[str, Any]] = []
    for selector in _base_color_selectors():
        raw.extend(
            {"kind": kind, "color": selector}
            for kind in ("separator_rows", "separator_cols", "separator_grid")
        )
        raw.append({"kind": "framed_separator_grid", "color": selector})
    raw.extend({"kind": kind} for kind in ("uniform_rows", "uniform_cols", "uniform_grid"))
    for parts in range(2, 5):
        raw.append({"kind": "equal_rows", "parts": parts})
        raw.append({"kind": "equal_cols", "parts": parts})
    for row_parts in range(2, 4):
        for col_parts in range(2, 4):
            raw.append({"kind": "equal_grid", "row_parts": row_parts, "col_parts": col_parts})

    accepted: list[tuple[int, dict[str, Any], str]] = []
    seen_behavior: set[str] = set()
    for spec in raw:
        try:
            decompositions = [_decompose(grid, spec) for grid in inputs]
        except (IndexError, KeyError, TypeError, ValueError):
            continue
        if any(not 2 <= len(item.panels) <= limits.max_panels for item in decompositions):
            continue
        # Native-layout serialization can legitimately vary its panel arity
        # between examples (for example, a 4x4 lattice followed by a 3x3 one).
        # Fixed-index programs simply fail their own exact replay when that
        # stronger invariant is absent.
        signature = _canonical(
            [
                {
                    "panels": [[_plain(panel) for panel in item.panels]],
                    "rows": item.rows,
                    "cols": item.cols,
                    "separator": item.separator,
                }
                for item in decompositions
            ]
        )
        if signature in seen_behavior:
            continue
        seen_behavior.add(signature)
        accepted.append((_partition_cost(spec), spec, _canonical(spec)))
    accepted.sort(key=lambda item: (item[0], item[2]))
    return [spec for _, spec, _ in accepted[: limits.max_partitions]]


def _transform(grid: Grid, name: str) -> Grid:
    if name == "identity":
        return grid
    if name == "flip_h":
        return tuple(tuple(reversed(row)) for row in grid)
    if name == "flip_v":
        return tuple(reversed(grid))
    if name == "rot180":
        return tuple(tuple(reversed(row)) for row in reversed(grid))
    if name == "transpose":
        height, width = _shape(grid)
        return tuple(tuple(grid[row][col] for row in range(height)) for col in range(width))
    if name == "rot90":
        height, width = _shape(grid)
        return tuple(tuple(grid[height - 1 - row][col] for row in range(height)) for col in range(width))
    if name == "rot270":
        height, width = _shape(grid)
        return tuple(tuple(grid[row][width - 1 - col] for row in range(height)) for col in range(width))
    if name == "anti_transpose":
        return _transform(_transform(grid, "rot180"), "transpose")
    raise ValueError("unknown panel transform")


_TRANSFORMS = ("identity", "flip_h", "flip_v", "rot180", "transpose", "rot90", "rot270", "anti_transpose")


def _support(grid: Grid, background: int) -> tuple[tuple[bool, ...], ...]:
    return tuple(tuple(cell != background for cell in row) for row in grid)


def _same_shape(grids: Sequence[Grid]) -> bool:
    return bool(grids) and len({_shape(grid) for grid in grids}) == 1


def _mask(arrays: Sequence[Grid], combine: str, background: int) -> tuple[tuple[bool, ...], ...]:
    if not _same_shape(arrays):
        raise ValueError("unaligned panels")
    height, width = _shape(arrays[0])
    supports = [_support(array, background) for array in arrays]
    result: list[tuple[bool, ...]] = []
    for row in range(height):
        values: list[bool] = []
        for col in range(width):
            bits = [item[row][col] for item in supports]
            pixels = [array[row][col] for array in arrays]
            if combine == "or":
                value = any(bits)
            elif combine == "and":
                value = all(bits)
            elif combine == "xor":
                value = sum(bits) % 2 == 1
            elif combine == "exactly_one":
                value = sum(bits) == 1
            elif combine == "first_minus_second":
                value = bits[0] and not bits[1]
            elif combine == "second_minus_first":
                value = bits[1] and not bits[0]
            elif combine == "support_equal":
                value = bits[0] == bits[1]
            elif combine == "support_unequal":
                value = bits[0] != bits[1]
            elif combine == "value_equal":
                value = pixels[0] == pixels[1]
            elif combine == "value_unequal":
                value = pixels[0] != pixels[1]
            else:
                raise ValueError("unknown panel algebra")
            values.append(bool(value))
        result.append(tuple(values))
    return tuple(result)


def _panel_signature(panel: Grid, d4: bool) -> str:
    variants = [_transform(panel, name) for name in _TRANSFORMS] if d4 else [panel]
    return min(_canonical(_plain(variant)) for variant in variants)


def _selected_index(selector: Mapping[str, Any], panel_set: PanelSet, background: int | None) -> int:
    kind = selector["kind"]
    panels = panel_set.panels
    if kind == "index":
        return int(selector["index"])
    if kind in {"unique_exact", "unique_d4"}:
        signatures = [_panel_signature(panel, kind == "unique_d4") for panel in panels]
        counts = Counter(signatures)
        unique = [index for index, signature in enumerate(signatures) if counts[signature] == 1]
        repeated = [count for count in counts.values() if count > 1]
        if len(unique) != 1 or not repeated:
            raise ValueError("no unique panel against a repeated class")
        return unique[0]
    if background is None:
        raise ValueError("support selector needs a background")
    scores = [sum(cell != background for row in panel for cell in row) for panel in panels]
    target = max(scores) if kind == "largest_support" else min(scores)
    winners = [index for index, score in enumerate(scores) if score == target]
    if len(winners) != 1:
        raise ValueError("panel score is tied")
    return winners[0]


def _layout(panels: Sequence[Grid], order: Sequence[int], rows: int, cols: int, gap: int, fill: int) -> Grid:
    if rows < 1 or cols < 1 or rows * cols != len(order) or sorted(order) != list(range(len(panels))):
        raise ValueError("invalid panel layout")
    chosen = [panels[index] for index in order]
    if not _same_shape(chosen):
        raise ValueError("layout panels have unequal shapes")
    panel_h, panel_w = _shape(chosen[0])
    height = rows * panel_h + (rows - 1) * gap
    width = cols * panel_w + (cols - 1) * gap
    if height > 30 or width > 30:
        raise ValueError("constructed grid exceeds ARC bounds")
    result = [[fill for _ in range(width)] for _ in range(height)]
    for slot, panel in enumerate(chosen):
        tile_row, tile_col = divmod(slot, cols)
        r0 = tile_row * (panel_h + gap)
        c0 = tile_col * (panel_w + gap)
        for row in range(panel_h):
            for col in range(panel_w):
                result[r0 + row][c0 + col] = panel[row][col]
    return tuple(tuple(row) for row in result)


def _aligned_arrays(program: Mapping[str, Any], panel_set: PanelSet) -> list[Grid]:
    indices = [int(index) for index in program["indices"]]
    transforms = list(program.get("transforms", ["identity"] * len(indices)))
    if len(transforms) != len(indices):
        raise ValueError("transform arity mismatch")
    return [_transform(panel_set.panels[index], str(transform)) for index, transform in zip(indices, transforms)]


def _components(panel: Grid, background: int, connectivity: int = 4) -> list[list[tuple[int, int, int]]]:
    height, width = _shape(panel)
    remaining = {(row, col) for row in range(height) for col in range(width) if panel[row][col] != background}
    result: list[list[tuple[int, int, int]]] = []
    if connectivity == 8:
        offsets = tuple(
            (dr, dc)
            for dr in (-1, 0, 1)
            for dc in (-1, 0, 1)
            if dr or dc
        )
    else:
        offsets = ((-1, 0), (0, -1), (0, 1), (1, 0))
    while remaining:
        seed = min(remaining)
        remaining.remove(seed)
        queue = [seed]
        cells: list[tuple[int, int, int]] = []
        while queue:
            row, col = queue.pop()
            cells.append((row, col, panel[row][col]))
            for dr, dc in offsets:
                neighbor = (row + dr, col + dc)
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    queue.append(neighbor)
        result.append(sorted(cells))
    return sorted(result, key=lambda cells: (-len(cells), cells))


def _largest_component(panel: Grid, background: int, connectivity: int) -> list[tuple[int, int, int]]:
    components = _components(panel, background, connectivity)
    if not components or (len(components) > 1 and len(components[0]) == len(components[1])):
        raise ValueError("largest component is absent or tied")
    return components[0]


def _panel_value(rule: Mapping[str, Any], panel: Grid, background: int | None) -> int:
    kind = rule["kind"]
    if kind == "mode":
        return _mode(panel)
    if kind == "least_frequent":
        return _frequency_order(panel, False)[0]
    if kind == "nonbackground_mode":
        if background is None:
            raise ValueError("nonbackground mode needs a background")
        counts = Counter(cell for row in panel for cell in row if cell != background)
        if not counts:
            return background
        return min(counts, key=lambda color: (-counts[color], color))
    if kind == "nonbackground_least":
        if background is None:
            raise ValueError("nonbackground least needs a background")
        counts = Counter(cell for row in panel for cell in row if cell != background)
        if not counts:
            return background
        return min(counts, key=lambda color: (counts[color], color))
    if kind == "top_left":
        return panel[0][0]
    if kind == "top_right":
        return panel[0][-1]
    if kind == "bottom_left":
        return panel[-1][0]
    if kind == "bottom_right":
        return panel[-1][-1]
    if kind == "center":
        return panel[(len(panel) - 1) // 2][(len(panel[0]) - 1) // 2]
    raise ValueError("unknown panel serialization rule")


def _panel_predicate(
    predicate: Mapping[str, Any], panel: Grid, background: int, connectivity: int = 4
) -> bool:
    kind = predicate["kind"]
    support_count = sum(cell != background for row in panel for cell in row)
    if kind == "support_eq":
        return support_count == int(predicate["value"])
    if kind == "support_le":
        return support_count <= int(predicate["value"])
    if kind == "support_ge":
        return support_count >= int(predicate["value"])
    if kind == "support_parity":
        return support_count % 2 == int(predicate["value"])
    if kind == "component_count_eq":
        return len(_components(panel, background, connectivity)) == int(predicate["value"])
    if kind == "horizontal_symmetry":
        return panel == _transform(panel, "flip_h")
    if kind == "vertical_symmetry":
        return panel == _transform(panel, "flip_v")
    if kind == "rotational_symmetry":
        return panel == _transform(panel, "rot180")
    raise ValueError("unknown panel predicate")


def _motif_key(panel: Grid, background: int, symmetry: str) -> str:
    binary = tuple(tuple(int(cell != background) for cell in row) for row in panel)
    variants = [binary]
    if symmetry == "d4":
        variants = [_transform(binary, transform) for transform in _TRANSFORMS]
    return min("/".join("".join(str(cell) for cell in row) for row in variant) for variant in variants)


def _translation_rank(displacement: tuple[int, int], preference: str) -> tuple[int, ...]:
    dr, dc = displacement
    distance = abs(dr) + abs(dc)
    if preference == "left":
        return distance, dc, abs(dr), dr
    if preference == "right":
        return distance, -dc, abs(dr), dr
    if preference == "up":
        return distance, dr, abs(dc), dc
    if preference == "down":
        return distance, -dr, abs(dc), dc
    if preference == "row_major":
        return distance, dr, dc
    return distance, dc, dr


def _component_pack(
    panels: Sequence[Grid],
    order: Sequence[int],
    background: int,
    connectivity: int,
    preference: str,
) -> Grid:
    if not _same_shape(panels):
        raise ValueError("component panels are unaligned")
    height, width = _shape(panels[0])
    canvas = [[background for _ in range(width)] for _ in range(height)]
    occupied: set[tuple[int, int]] = set()
    for panel_index in order:
        component = _largest_component(panels[panel_index], background, connectivity)
        options: list[tuple[tuple[int, ...], int, int]] = []
        for dr in range(-height + 1, height):
            for dc in range(-width + 1, width):
                shifted = [(row + dr, col + dc) for row, col, _ in component]
                if all(0 <= row < height and 0 <= col < width for row, col in shifted) and not any(
                    position in occupied for position in shifted
                ):
                    options.append((_translation_rank((dr, dc), preference), dr, dc))
        if not options:
            raise ValueError("component cannot be packed")
        _, dr, dc = min(options)
        for row, col, color in component:
            rr, cc = row + dr, col + dc
            canvas[rr][cc] = color
            occupied.add((rr, cc))
    return tuple(tuple(row) for row in canvas)


def _stack_motifs(
    panels: Sequence[Grid],
    order: Sequence[int],
    background: int,
    axis: str,
    anchor: str,
) -> Grid:
    if not _same_shape(panels):
        raise ValueError("motif panels are unaligned")
    height, width = _shape(panels[0])
    motifs: list[tuple[list[tuple[int, int, int]], int, int, int, int]] = []
    for index in order:
        cells = [
            (row, col, panels[index][row][col])
            for row in range(height)
            for col in range(width)
            if panels[index][row][col] != background
        ]
        if not cells:
            raise ValueError("empty motif")
        r0, r1 = min(row for row, _, _ in cells), max(row for row, _, _ in cells) + 1
        c0, c1 = min(col for _, col, _ in cells), max(col for _, col, _ in cells) + 1
        motifs.append((cells, r0, r1, c0, c1))
    extents = [(r1 - r0 if axis == "rows" else c1 - c0) for _, r0, r1, c0, c1 in motifs]
    available = height if axis == "rows" else width
    total = sum(extents)
    if total > available:
        raise ValueError("motifs do not fit")
    cursor = 0 if anchor == "start" else available - total if anchor == "end" else (available - total) // 2
    canvas = [[background for _ in range(width)] for _ in range(height)]
    occupied: set[tuple[int, int]] = set()
    for extent, (cells, r0, _r1, c0, _c1) in zip(extents, motifs):
        for row, col, color in cells:
            rr = cursor + (row - r0) if axis == "rows" else row
            cc = col if axis == "rows" else cursor + (col - c0)
            if (rr, cc) in occupied:
                raise ValueError("stacked motifs overlap")
            occupied.add((rr, cc))
            canvas[rr][cc] = color
        cursor += extent
    return tuple(tuple(row) for row in canvas)


def _ranked_motif_overlay(
    panels: Sequence[Grid],
    ranks: Sequence[int],
    order: Sequence[int],
    background: int,
    rank_axis: str,
    component_filter: str,
    missing: str,
) -> Grid:
    if not _same_shape(panels) or len(ranks) != len(panels):
        raise ValueError("ranked panels are unaligned")
    height, width = _shape(panels[0])
    selected: list[tuple[int, list[tuple[int, int]]]] = []
    for panel, rank in zip(panels, ranks):
        colors = [color for color in _palette(panel) if color != background]
        records: list[tuple[float, float, int]] = []
        for color in colors:
            cells = [(row, col) for row in range(height) for col in range(width) if panel[row][col] == color]
            mean_row = sum(row for row, _ in cells) / len(cells)
            mean_col = sum(col for _, col in cells) / len(cells)
            records.append((mean_col if rank_axis == "cols" else mean_row, mean_row if rank_axis == "cols" else mean_col, color))
        records.sort()
        if not 0 <= rank < len(records):
            if missing == "empty":
                selected.append((background, []))
                continue
            raise ValueError("motif rank outside panel palette")
        color = records[rank][2]
        cells = [(row, col) for row in range(height) for col in range(width) if panel[row][col] == color]
        if component_filter != "all":
            isolated = tuple(
                tuple(color if panel[row][col] == color else background for col in range(width))
                for row in range(height)
            )
            component = _largest_component(isolated, background, 8 if component_filter == "largest8" else 4)
            cells = [(row, col) for row, col, _ in component]
        selected.append((color, cells))
    canvas = [[background for _ in range(width)] for _ in range(height)]
    for index in order:
        color, cells = selected[index]
        for row, col in cells:
            canvas[row][col] = color
    return tuple(tuple(row) for row in canvas)


def execute_program(program: Mapping[str, Any], value: Any) -> list[list[int]]:
    """Execute one JSON program on one input grid."""

    grid = _grid(value if isinstance(value, list) else _plain(value))
    panel_set = _decompose(grid, program["partition"])
    op = program["op"]
    if op == "select":
        background_selector = program.get("background")
        background = _color(background_selector, grid, panel_set) if background_selector else None
        index = _selected_index(program["selector"], panel_set, background)
        output = _transform(panel_set.panels[index], str(program["transform"]))
    elif op == "layout":
        fill = _color(program["fill"], grid, panel_set)
        output = _layout(
            panel_set.panels,
            [int(index) for index in program["order"]],
            int(program["rows"]),
            int(program["cols"]),
            int(program["gap"]),
            fill,
        )
    elif op == "overlay":
        arrays = [panel_set.panels[int(index)] for index in program["order"]]
        if not _same_shape(arrays):
            raise ValueError("overlay panels are unaligned")
        background = _color(program["background"], grid, panel_set)
        height, width = _shape(arrays[0])
        canvas = [[background for _ in range(width)] for _ in range(height)]
        for array in arrays:
            for row in range(height):
                for col in range(width):
                    if array[row][col] != background:
                        canvas[row][col] = array[row][col]
        output = tuple(tuple(row) for row in canvas)
    elif op == "mask":
        arrays = _aligned_arrays(program, panel_set)
        background = _color(program["background"], grid, panel_set)
        mask = _mask(arrays, str(program["combine"]), background)
        false_color = _color(program["false_color"], grid, panel_set)
        render = program.get("render", "solid")
        height, width = len(mask), len(mask[0])
        if render == "solid":
            true_color = _color(program["true_color"], grid, panel_set)
            output = tuple(
                tuple(true_color if mask[row][col] else false_color for col in range(width))
                for row in range(height)
            )
        elif render == "panel":
            source = arrays[int(program["render_index"])]
            output = tuple(
                tuple(source[row][col] if mask[row][col] else false_color for col in range(width))
                for row in range(height)
            )
        else:
            raise ValueError("unknown mask rendering")
    elif op == "serialize":
        background_selector = program.get("background")
        background = _color(background_selector, grid, panel_set) if background_selector else None
        values = [
            _panel_value(program["cell_rule"], panel, background)
            for panel in panel_set.panels
        ]
        singleton_panels = [((value,),) for value in values]
        fill = _color(program["fill"], grid, panel_set)
        output = _layout(
            singleton_panels,
            [int(index) for index in program["order"]],
            int(program["rows"]),
            int(program["cols"]),
            int(program["gap"]),
            fill,
        )
        output = _transform(output, str(program.get("output_transform", "identity")))
    elif op == "serialize_native":
        background_selector = program.get("background")
        background = _color(background_selector, grid, panel_set) if background_selector else None
        values = [_panel_value(program["cell_rule"], panel, background) for panel in panel_set.panels]
        fill = _color(program["fill"], grid, panel_set)
        output = _layout(
            [((value,),) for value in values],
            list(range(len(values))),
            panel_set.rows,
            panel_set.cols,
            int(program["gap"]),
            fill,
        )
        output = _transform(output, str(program.get("output_transform", "identity")))
    elif op == "serialize_predicate":
        background = _color(program["background"], grid, panel_set)
        true_color = _color(program["true_color"], grid, panel_set)
        false_color = _color(program["false_color"], grid, panel_set)
        values = [
            true_color
            if _panel_predicate(program["predicate"], panel, background, int(program.get("connectivity", 4)))
            else false_color
            for panel in panel_set.panels
        ]
        singleton_panels = [((value,),) for value in values]
        fill = _color(program["fill"], grid, panel_set)
        output = _layout(
            singleton_panels,
            [int(index) for index in program["order"]],
            int(program["rows"]),
            int(program["cols"]),
            int(program["gap"]),
            fill,
        )
    elif op == "motif_codes":
        background = _color(program["background"], grid, panel_set)
        mapping = {str(item["key"]): item["color"] for item in program["mapping"]}
        codes: list[int] = []
        for panel in panel_set.panels:
            key = _motif_key(panel, background, str(program["symmetry"]))
            if key not in mapping:
                raise ValueError("unseen panel motif")
            codes.append(_color(mapping[key], grid, panel_set))
        mode = program["layout"]
        if mode == "row_stripes":
            output = tuple(tuple(value for _ in range(len(codes))) for value in codes)
        elif mode == "col_stripes":
            output = tuple(tuple(codes[col] for col in range(len(codes))) for _ in range(len(codes)))
        elif mode == "partition":
            output = _layout([((value,),) for value in codes], list(range(len(codes))), panel_set.rows, panel_set.cols, 0, background)
        else:
            raise ValueError("unknown motif-code layout")
    elif op == "component_pack":
        background = _color(program["background"], grid, panel_set)
        output = _component_pack(
            panel_set.panels,
            [int(index) for index in program["order"]],
            background,
            int(program["connectivity"]),
            str(program["preference"]),
        )
    elif op == "stack_motifs":
        background = _color(program["background"], grid, panel_set)
        output = _stack_motifs(
            panel_set.panels,
            [int(index) for index in program["order"]],
            background,
            str(program["axis"]),
            str(program["anchor"]),
        )
    elif op == "ranked_motif_overlay":
        background = _color(program["background"], grid, panel_set)
        output = _ranked_motif_overlay(
            panel_set.panels,
            [int(index) for index in program["ranks"]],
            [int(index) for index in program["order"]],
            background,
            str(program["rank_axis"]),
            str(program.get("component_filter", "all")),
            str(program.get("missing", "error")),
        )
    elif op == "keyed_quadrants":
        if panel_set.rows != 3 or panel_set.cols != 3 or len(panel_set.panels) != 9:
            raise ValueError("corner-key program needs a 3 by 3 partition")
        background = _color(program["background"], grid, panel_set)
        motif = panel_set.panels[int(program.get("motif_panel", 4))]
        key_indices = [int(index) for index in program["key_panels"]]
        if len(key_indices) != 4:
            raise ValueError("corner-key arity mismatch")
        keys = [_panel_value(program["key_rule"], panel_set.panels[index], background) for index in key_indices]
        motif_h, motif_w = _shape(motif)
        output = tuple(
            tuple(
                background
                if motif[row][col] == background
                else keys[(0 if row * 2 < motif_h else 2) + (0 if col * 2 < motif_w else 1)]
                for col in range(motif_w)
            )
            for row in range(motif_h)
        )
    else:
        raise ValueError("unknown partition operation")
    return _plain(output)


def _layout_orders(count: int, source_rows: int, source_cols: int) -> list[tuple[list[int], int, int]]:
    original = list(range(count))
    records: list[tuple[list[int], int, int]] = []
    if count <= 4:
        permutations: Iterable[tuple[int, ...]] = itertools.permutations(range(count))
    else:
        permutations = (tuple(original), tuple(reversed(original)))
    for order_tuple in permutations:
        order = list(order_tuple)
        records.append((order, 1, count))
        records.append((order, count, 1))
        if source_rows * source_cols == count:
            records.append((order, source_rows, source_cols))
    if source_rows > 1 and source_cols > 1:
        flip_rows = [row * source_cols + col for row in reversed(range(source_rows)) for col in range(source_cols)]
        flip_cols = [row * source_cols + col for row in range(source_rows) for col in reversed(range(source_cols))]
        transpose = [row * source_cols + col for col in range(source_cols) for row in range(source_rows)]
        records.extend(
            [
                (flip_rows, source_rows, source_cols),
                (flip_cols, source_rows, source_cols),
                (transpose, source_cols, source_rows),
            ]
        )
    unique: dict[str, tuple[list[int], int, int]] = {}
    for record in records:
        unique.setdefault(_canonical(record), record)
    return list(unique.values())


def _infer_selectors(
    observed: Sequence[int],
    contexts: Sequence[tuple[Grid, PanelSet]],
    pool: Sequence[dict[str, Any]],
    cap: int = 8,
) -> list[dict[str, Any]]:
    matches: list[tuple[int, str, dict[str, Any]]] = []
    for selector in pool:
        try:
            actual = [_color(selector, grid, panel_set) for grid, panel_set in contexts]
        except (IndexError, KeyError, TypeError, ValueError):
            continue
        if list(observed) == actual:
            matches.append((_selector_cost(selector), _canonical(selector), selector))
    matches.sort(key=lambda item: (item[0], item[1]))
    return [selector for _, _, selector in matches[:cap]]


class _Collector:
    def __init__(
        self,
        train: Sequence[tuple[Grid, Grid]],
        tests: Sequence[Grid],
        limits: Limits,
    ) -> None:
        self.train = list(train)
        self.tests = list(tests)
        self.limits = limits
        self.hypotheses = 0
        self.seen_programs: set[str] = set()
        self.candidates: list[dict[str, Any]] = []

    @property
    def full(self) -> bool:
        return self.hypotheses >= self.limits.max_hypotheses or len(self.candidates) >= self.limits.max_candidates * 8

    def propose(self, family: str, program: dict[str, Any], complexity: int) -> None:
        if self.full:
            return
        key = _canonical(program)
        if key in self.seen_programs:
            return
        self.seen_programs.add(key)
        self.hypotheses += 1
        try:
            replay = [execute_program(program, _plain(source)) for source, _ in self.train]
            expected = [_plain(target) for _, target in self.train]
            if replay != expected:
                return
            # Do not promote a panel program on wholly identity demonstrations.
            if all(source == target for source, target in self.train):
                return
            predictions = [execute_program(program, _plain(source)) for source in self.tests]
        except (IndexError, KeyError, TypeError, ValueError, OverflowError):
            return
        self.candidates.append(
            {
                "family": family,
                "program": program,
                "train_outputs": replay,
                "test_outputs": predictions,
                "complexity": int(complexity),
                "evidence": {
                    "all_demonstrations_exact": True,
                    "demonstrations": len(self.train),
                    "changed_demonstrations": sum(source != target for source, target in self.train),
                    "partition_kind": program["partition"]["kind"],
                    "test_inputs": len(self.tests),
                    "label_access": "training_outputs_only",
                    "author": "Komorebi P.",
                },
            }
        )


def _mask_observations(
    train: Sequence[tuple[Grid, Grid]],
    base_program: Mapping[str, Any],
) -> tuple[list[tuple[Grid, PanelSet]], list[int], list[int]] | None:
    contexts: list[tuple[Grid, PanelSet]] = []
    false_values: list[int] = []
    true_values: list[int] = []
    for source, target in train:
        try:
            panel_set = _decompose(source, base_program["partition"])
            arrays = _aligned_arrays(base_program, panel_set)
            background = _color(base_program["background"], source, panel_set)
            mask = _mask(arrays, str(base_program["combine"]), background)
        except (IndexError, KeyError, TypeError, ValueError):
            return None
        if _shape(target) != (len(mask), len(mask[0])):
            return None
        false_cells = [target[row][col] for row in range(len(mask)) for col in range(len(mask[0])) if not mask[row][col]]
        true_cells = [target[row][col] for row in range(len(mask)) for col in range(len(mask[0])) if mask[row][col]]
        # Seeing both states in every demonstration sharply reduces vacuous fits.
        if not false_cells or not true_cells or len(set(false_cells)) != 1 or len(set(true_cells)) != 1:
            return None
        contexts.append((source, panel_set))
        false_values.append(false_cells[0])
        true_values.append(true_cells[0])
    return contexts, false_values, true_values


def _masked_panel_false_observations(
    train: Sequence[tuple[Grid, Grid]],
    base_program: Mapping[str, Any],
    render_index: int,
) -> tuple[list[tuple[Grid, PanelSet]], list[int]] | None:
    contexts: list[tuple[Grid, PanelSet]] = []
    false_values: list[int] = []
    for source, target in train:
        try:
            panel_set = _decompose(source, base_program["partition"])
            arrays = _aligned_arrays(base_program, panel_set)
            background = _color(base_program["background"], source, panel_set)
            mask = _mask(arrays, str(base_program["combine"]), background)
        except (IndexError, KeyError, TypeError, ValueError):
            return None
        if _shape(target) != (len(mask), len(mask[0])):
            return None
        false_cells: list[int] = []
        for row in range(len(mask)):
            for col in range(len(mask[0])):
                if mask[row][col]:
                    if target[row][col] != arrays[render_index][row][col]:
                        return None
                else:
                    false_cells.append(target[row][col])
        if not false_cells or len(set(false_cells)) != 1:
            return None
        contexts.append((source, panel_set))
        false_values.append(false_cells[0])
    return contexts, false_values


def _likely_backgrounds(has_separator: bool) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = [
        {"kind": "mode"},
        {"kind": "frequency_rank", "descending": True, "rank": 0},
    ]
    if has_separator:
        result.append({"kind": "separator"})
    result.extend({"kind": "literal", "value": value} for value in range(10))
    unique: dict[str, dict[str, Any]] = {}
    for selector in result:
        unique.setdefault(_canonical(selector), selector)
    return list(unique.values())


def _predicate_observations(
    train: Sequence[tuple[Grid, Grid]],
    spec: Mapping[str, Any],
    predicate: Mapping[str, Any],
    background_selector: Mapping[str, Any],
    connectivity: int,
) -> tuple[list[tuple[Grid, PanelSet]], list[int], list[int]] | None:
    contexts: list[tuple[Grid, PanelSet]] = []
    false_values: list[int] = []
    true_values: list[int] = []
    for source, target in train:
        try:
            panel_set = _decompose(source, spec)
            background = _color(background_selector, source, panel_set)
            flags = [
                _panel_predicate(predicate, panel, background, connectivity)
                for panel in panel_set.panels
            ]
        except (IndexError, KeyError, TypeError, ValueError):
            return None
        if _shape(target) != (panel_set.rows, panel_set.cols):
            return None
        flat_target = [cell for row in target for cell in row]
        false_cells = [color for color, flag in zip(flat_target, flags) if not flag]
        true_cells = [color for color, flag in zip(flat_target, flags) if flag]
        if not false_cells or not true_cells or len(set(false_cells)) != 1 or len(set(true_cells)) != 1:
            return None
        contexts.append((source, panel_set))
        false_values.append(false_cells[0])
        true_values.append(true_cells[0])
    return contexts, false_values, true_values


def _motif_code_program(
    train: Sequence[tuple[Grid, Grid]],
    spec: Mapping[str, Any],
    background_selector: Mapping[str, Any],
    symmetry: str,
    layout: str,
) -> dict[str, Any] | None:
    observations: dict[str, list[tuple[int, Grid, PanelSet]]] = {}
    for source, target in train:
        try:
            panel_set = _decompose(source, spec)
            background = _color(background_selector, source, panel_set)
            keys = [_motif_key(panel, background, symmetry) for panel in panel_set.panels]
        except (IndexError, KeyError, TypeError, ValueError):
            return None
        count = len(keys)
        if layout == "row_stripes":
            if _shape(target) != (count, count) or any(len(set(row)) != 1 for row in target):
                return None
            codes = [row[0] for row in target]
        elif layout == "col_stripes":
            if _shape(target) != (count, count):
                return None
            columns = [[target[row][col] for row in range(count)] for col in range(count)]
            if any(len(set(column)) != 1 for column in columns):
                return None
            codes = [column[0] for column in columns]
        else:
            if _shape(target) != (panel_set.rows, panel_set.cols):
                return None
            codes = [cell for row in target for cell in row]
        for key, code in zip(keys, codes):
            observations.setdefault(key, []).append((code, source, panel_set))
    mapping: list[dict[str, Any]] = []
    for key in sorted(observations):
        records = observations[key]
        contexts = [(source, panel_set) for _, source, panel_set in records]
        observed = [code for code, _, _ in records]
        pool = _output_color_selectors(len(contexts[0][1].panels), contexts[0][1].separator is not None)
        selectors = _infer_selectors(observed, contexts, pool, cap=1)
        if not selectors:
            return None
        mapping.append({"key": key, "color": selectors[0]})
    return {
        "op": "motif_codes",
        "partition": dict(spec),
        "background": dict(background_selector),
        "symmetry": symmetry,
        "layout": layout,
        "mapping": mapping,
    }


def _enumerate_partition(collector: _Collector, spec: dict[str, Any]) -> None:
    if collector.full:
        return
    all_inputs = [source for source, _ in collector.train] + collector.tests
    try:
        decompositions = [_decompose(source, spec) for source in all_inputs]
    except (IndexError, KeyError, TypeError, ValueError):
        return
    first = decompositions[0]
    count = len(first.panels)
    partition_cost = _partition_cost(spec)
    train_decompositions = decompositions[: len(collector.train)]
    target_shapes = [_shape(target) for _, target in collector.train]
    panel_output_shape = all(
        target_shape in {_shape(panel) for panel in panel_set.panels}
        for target_shape, panel_set in zip(target_shapes, train_decompositions)
    )
    aligned_panel_output = panel_output_shape and all(
        _same_shape(panel_set.panels) for panel_set in train_decompositions
    )
    native_meta_shape = all(
        target_shape
        in {
            (panel_set.rows, panel_set.cols),
            (panel_set.cols, panel_set.rows),
            (panel_set.rows * 2 - 1, panel_set.cols * 2 - 1),
            (panel_set.cols * 2 - 1, panel_set.rows * 2 - 1),
        }
        for target_shape, panel_set in zip(target_shapes, train_decompositions)
    )
    predicate_meta_shape = all(
        target_shape == (panel_set.rows, panel_set.cols)
        for target_shape, panel_set in zip(target_shapes, train_decompositions)
    )
    code_shape = all(
        target_shape
        in {
            (len(panel_set.panels), len(panel_set.panels)),
            (panel_set.rows, panel_set.cols),
        }
        for target_shape, panel_set in zip(target_shapes, train_decompositions)
    )

    def layout_shape_possible(target_shape: tuple[int, int], panel_set: PanelSet) -> bool:
        if not _same_shape(panel_set.panels):
            return False
        panel_h, panel_w = _shape(panel_set.panels[0])
        options = {
            (panel_h, len(panel_set.panels) * panel_w),
            (len(panel_set.panels) * panel_h, panel_w),
            (panel_set.rows * panel_h, panel_set.cols * panel_w),
        }
        if panel_set.separator is not None:
            options.update(
                {
                    (panel_h, len(panel_set.panels) * panel_w + len(panel_set.panels) - 1),
                    (len(panel_set.panels) * panel_h + len(panel_set.panels) - 1, panel_w),
                    (
                        panel_set.rows * panel_h + panel_set.rows - 1,
                        panel_set.cols * panel_w + panel_set.cols - 1,
                    ),
                }
            )
        return target_shape in options

    layout_output_shape = all(
        layout_shape_possible(target_shape, panel_set)
        for target_shape, panel_set in zip(target_shapes, train_decompositions)
    )

    # Fixed and relational panel selection, with all D4 orientations.
    selectors: list[tuple[dict[str, Any], dict[str, Any] | None]] = [
        ({"kind": "index", "index": index}, None) for index in range(count)
    ] if panel_output_shape else []
    if panel_output_shape:
        selectors.extend([({"kind": "unique_exact"}, None), ({"kind": "unique_d4"}, None)])
    support_backgrounds = _base_color_selectors()[:10] + [{"kind": "literal", "value": value} for value in range(10)]
    if first.separator is not None:
        support_backgrounds.insert(0, {"kind": "separator"})
    if panel_output_shape:
        for background in support_backgrounds:
            selectors.append(({"kind": "largest_support"}, background))
            selectors.append(({"kind": "smallest_support"}, background))
    for selector, background in selectors:
        for transform in _TRANSFORMS:
            program: dict[str, Any] = {
                "op": "select",
                "partition": spec,
                "selector": selector,
                "transform": transform,
            }
            if background is not None:
                program["background"] = background
            collector.propose(
                "partition_select",
                program,
                partition_cost + 1 + (0 if transform == "identity" else 1) + (1 if background else 0),
            )

    # The canonical separator-removal move is cheap and should never be
    # displaced from the bounded search by richer downstream panel models.
    if layout_output_shape:
        collector.propose(
            "partition_layout",
            {
                "op": "layout",
                "partition": spec,
                "order": list(range(count)),
                "rows": first.rows,
                "cols": first.cols,
                "gap": 0,
                "fill": {"kind": "literal", "value": 0},
            },
            partition_cost + 2,
        )

    # Compress every panel to one representative color.  This covers both
    # separator removal (gap zero) and small keyed maps which retain a one-cell
    # divider.  It is a genuine serialization operation, not a grid lookup.
    serialize_rules = (
        {"kind": "mode"},
        {"kind": "least_frequent"},
        {"kind": "top_left"},
        {"kind": "top_right"},
        {"kind": "bottom_left"},
        {"kind": "bottom_right"},
        {"kind": "center"},
    ) if native_meta_shape else ()
    candidates_before_native_serialization = len(collector.candidates)
    for rule in serialize_rules:
        for output_transform in _TRANSFORMS:
            collector.propose(
                "panel_serialization_native",
                {
                    "op": "serialize_native",
                    "partition": spec,
                    "cell_rule": rule,
                    "gap": 0,
                    "fill": {"kind": "literal", "value": 0},
                    "output_transform": output_transform,
                },
                partition_cost + 2 + (output_transform != "identity"),
            )
            if all(item.separator is not None for item in decompositions):
                collector.propose(
                    "panel_serialization_native",
                    {
                        "op": "serialize_native",
                        "partition": spec,
                        "cell_rule": rule,
                        "gap": 1,
                        "fill": {"kind": "separator"},
                        "output_transform": output_transform,
                    },
                    partition_cost + 3 + (output_transform != "identity"),
                )
    for background in _likely_backgrounds(first.separator is not None):
        for rule in ({"kind": "nonbackground_mode"}, {"kind": "nonbackground_least"}):
            collector.propose(
                "panel_serialization_native",
                {
                    "op": "serialize_native",
                    "partition": spec,
                    "background": background,
                    "cell_rule": rule,
                    "gap": 0,
                    "fill": {"kind": "literal", "value": 0},
                },
                partition_cost + 3 + _selector_cost(background),
            )
    if count > 6 and len(collector.candidates) > candidates_before_native_serialization:
        return
    serialize_orders: list[tuple[list[int], int, int]] = [
        (list(range(count)), first.rows, first.cols),
        (list(reversed(range(count))), first.rows, first.cols),
    ]
    if first.rows > 1 and first.cols > 1:
        serialize_orders.extend(
            [
                ([row * first.cols + col for row in reversed(range(first.rows)) for col in range(first.cols)], first.rows, first.cols),
                ([row * first.cols + col for row in range(first.rows) for col in reversed(range(first.cols))], first.rows, first.cols),
                ([row * first.cols + col for col in range(first.cols) for row in range(first.rows)], first.cols, first.rows),
            ]
        )
    unique_serialize_orders: dict[str, tuple[list[int], int, int]] = {}
    for record in serialize_orders:
        unique_serialize_orders.setdefault(_canonical(record), record)
    for rule in serialize_rules:
        for order, rows, cols in unique_serialize_orders.values():
            collector.propose(
                "panel_serialization",
                {
                    "op": "serialize",
                    "partition": spec,
                    "cell_rule": rule,
                    "order": order,
                    "rows": rows,
                    "cols": cols,
                    "gap": 0,
                    "fill": {"kind": "literal", "value": 0},
                },
                partition_cost + 3,
            )
            if first.separator is not None:
                collector.propose(
                    "panel_serialization",
                    {
                        "op": "serialize",
                        "partition": spec,
                        "cell_rule": rule,
                        "order": order,
                        "rows": rows,
                        "cols": cols,
                        "gap": 1,
                        "fill": {"kind": "separator"},
                    },
                    partition_cost + 4,
                )
    for background in _likely_backgrounds(first.separator is not None):
        for rule in ({"kind": "nonbackground_mode"}, {"kind": "nonbackground_least"}):
            collector.propose(
                "panel_serialization",
                {
                    "op": "serialize",
                    "partition": spec,
                    "background": background,
                    "cell_rule": rule,
                    "order": list(range(count)),
                    "rows": first.rows,
                    "cols": first.cols,
                    "gap": 0,
                    "fill": {"kind": "literal", "value": 0},
                },
                partition_cost + 4 + _selector_cost(background),
            )

    # Boolean panel serialization, e.g. reduce each tile to whether it has two
    # marks or a particular symmetry.  Output colors remain learned source-role
    # expressions (or explicit ARC literals) and must replay every demo.
    panel_areas = sorted({_shape(panel)[0] * _shape(panel)[1] for panel in first.panels})
    max_area = max(panel_areas)
    predicates: list[dict[str, Any]] = []
    for value in range(0, min(max_area, 12) + 1):
        predicates.append({"kind": "support_eq", "value": value})
    for value in range(1, min(max_area, 8) + 1):
        predicates.append({"kind": "support_le", "value": value})
        predicates.append({"kind": "support_ge", "value": value})
    predicates.extend(
        [
            {"kind": "support_parity", "value": 0},
            {"kind": "support_parity", "value": 1},
            {"kind": "component_count_eq", "value": 1},
            {"kind": "component_count_eq", "value": 2},
            {"kind": "component_count_eq", "value": 3},
            {"kind": "horizontal_symmetry"},
            {"kind": "vertical_symmetry"},
            {"kind": "rotational_symmetry"},
        ]
    )
    if not predicate_meta_shape:
        predicates = []
    for background in _likely_backgrounds(first.separator is not None):
        for connectivity in (4, 8):
            for predicate in predicates:
                observations = _predicate_observations(collector.train, spec, predicate, background, connectivity)
                if observations is None:
                    continue
                contexts, false_values, true_values = observations
                pool = _output_color_selectors(count, first.separator is not None)
                false_selectors = _infer_selectors(false_values, contexts, pool, cap=4)
                true_selectors = _infer_selectors(true_values, contexts, pool, cap=4)
                for false_color, true_color in itertools.product(false_selectors, true_selectors):
                    collector.propose(
                        "panel_predicate_serialization",
                        {
                            "op": "serialize_predicate",
                            "partition": spec,
                            "background": background,
                            "predicate": predicate,
                            "connectivity": connectivity,
                            "false_color": false_color,
                            "true_color": true_color,
                            "order": list(range(count)),
                            "rows": first.rows,
                            "cols": first.cols,
                            "gap": 0,
                            "fill": {"kind": "literal", "value": 0},
                        },
                        partition_cost
                        + 6
                        + _selector_cost(background)
                        + _selector_cost(false_color)
                        + _selector_cost(true_color),
                    )

    # A finite vocabulary of small panel masks can encode output color tokens.
    # The learned key is background-relative geometry only, never an input grid
    # or task fingerprint.  Unknown test motifs fail closed.
    if count <= 6 and code_shape:
        for background in _likely_backgrounds(first.separator is not None):
            for symmetry in ("identity", "d4"):
                for layout in ("partition", "row_stripes", "col_stripes"):
                    program = _motif_code_program(collector.train, spec, background, symmetry, layout)
                    if program is not None:
                        collector.propose(
                            "panel_motif_codes",
                            program,
                            partition_cost + 8 + len(program["mapping"]) + (symmetry == "d4"),
                        )

    # Whole motifs can be packed within their panel-sized canvas.  The first
    # form removes all but the unique largest component and resolves collisions
    # by minimum translation; the second stacks full motif bounding boxes.
    if count <= 4 and aligned_panel_output and all(_same_shape(item.panels) for item in decompositions):
        orders = list(itertools.permutations(range(count)))
        for background in _likely_backgrounds(first.separator is not None):
            for order_tuple in orders:
                order = list(order_tuple)
                for connectivity in (4, 8):
                    for preference in ("left", "right", "up", "down", "row_major", "col_major"):
                        collector.propose(
                            "panel_component_pack",
                            {
                                "op": "component_pack",
                                "partition": spec,
                                "background": background,
                                "order": order,
                                "connectivity": connectivity,
                                "preference": preference,
                            },
                            partition_cost + 8 + count + _selector_cost(background),
                        )
                for axis in ("rows", "cols"):
                    for anchor in ("start", "center", "end"):
                        collector.propose(
                            "panel_motif_stack",
                            {
                                "op": "stack_motifs",
                                "partition": spec,
                                "background": background,
                                "order": order,
                                "axis": axis,
                                "anchor": anchor,
                            },
                            partition_cost + 7 + count + _selector_cost(background),
                        )

        # Select a spatially ranked color motif from each panel and merge those
        # motifs.  This expresses diagonal/anti-diagonal layer assembly without
        # encoding any absolute task identity.
        if count <= 3:
            rank_vectors: Iterable[tuple[int, ...]] = itertools.product(range(count), repeat=count)
        else:
            rank_vectors = (
                tuple(range(count)),
                tuple(reversed(range(count))),
                tuple(0 for _ in range(count)),
                tuple(count - 1 for _ in range(count)),
            )
        rank_vectors = list(rank_vectors)
        for background in _likely_backgrounds(first.separator is not None):
            for ranks in rank_vectors:
                for order_tuple in orders:
                    for rank_axis in ("rows", "cols"):
                        for component_filter in ("all", "largest4", "largest8"):
                            collector.propose(
                                "ranked_panel_motif_overlay",
                                {
                                    "op": "ranked_motif_overlay",
                                    "partition": spec,
                                    "background": background,
                                    "ranks": list(ranks),
                                    "order": list(order_tuple),
                                    "rank_axis": rank_axis,
                                    "component_filter": component_filter,
                                    "missing": "empty",
                                },
                                partition_cost
                                + 9
                                + count
                                + _selector_cost(background)
                                + (component_filter != "all"),
                            )

    # A central mask surrounded by four corner keys is a compact instruction:
    # recolor each occupied quadrant with its corresponding corner token.
    if count == 9 and first.rows == 3 and first.cols == 3:
        for background in _likely_backgrounds(first.separator is not None):
            for key_rule in ({"kind": "mode"}, {"kind": "least_frequent"}, {"kind": "nonbackground_mode"}):
                collector.propose(
                    "corner_keyed_motif",
                    {
                        "op": "keyed_quadrants",
                        "partition": spec,
                        "background": background,
                        "motif_panel": 4,
                        "key_panels": [0, 2, 6, 8],
                        "key_rule": key_rule,
                    },
                    partition_cost + 9 + _selector_cost(background),
                )

    # Pairwise permutation algebra grows quadratically and is not a credible
    # interpretation of large meta-grids.  The serialization/keyed families
    # above are the appropriate bounded language for those decompositions.
    if count > 6:
        return

    # Removing separators and rearranging equal panels into rows, columns, or
    # the original tile geometry.  A one-cell separator can also be retained.
    layout_records = _layout_orders(count, first.rows, first.cols) if layout_output_shape else []
    for order, rows, cols in layout_records:
        fill_selectors = [{"kind": "literal", "value": 0}]
        if first.separator is not None:
            fill_selectors.insert(0, {"kind": "separator"})
        for gap in (0, 1):
            if gap == 1 and first.separator is None:
                continue
            for fill in fill_selectors[:1] if gap == 0 else fill_selectors:
                collector.propose(
                    "partition_layout",
                    {
                        "op": "layout",
                        "partition": spec,
                        "order": order,
                        "rows": rows,
                        "cols": cols,
                        "gap": gap,
                        "fill": fill,
                    },
                    partition_cost + 2 + (order != list(range(count))) + gap,
                )

    # Transparent color overlays.  Up to four panels receive every priority
    # ordering; larger decompositions retain canonical and reverse priority.
    if not aligned_panel_output:
        overlay_orders: Iterable[tuple[int, ...]] = ()
    elif count <= 4:
        overlay_orders: Iterable[tuple[int, ...]] = itertools.permutations(range(count))
    else:
        overlay_orders = (tuple(range(count)), tuple(reversed(range(count))))
    overlay_backgrounds = _base_color_selectors()
    if first.separator is not None:
        overlay_backgrounds = [{"kind": "separator"}] + overlay_backgrounds
    for order in overlay_orders:
        for background in overlay_backgrounds:
            collector.propose(
                "partition_overlay",
                {
                    "op": "overlay",
                    "partition": spec,
                    "order": list(order),
                    "background": background,
                },
                partition_cost + 3 + count + _selector_cost(background),
            )

    # Boolean support algebra and pixel equality comparisons.  Pair programs
    # may align the second panel through any D4 transform; n-ary programs use
    # their common native frame.
    backgrounds = _base_color_selectors()
    if first.separator is not None:
        backgrounds = [{"kind": "separator"}] + backgrounds
    pair_combines = (
        "or",
        "and",
        "xor",
        "first_minus_second",
        "second_minus_first",
        "support_equal",
        "support_unequal",
        "value_equal",
        "value_unequal",
    )
    pairs = list(itertools.combinations(range(count), 2)) if aligned_panel_output else []
    for left, right in pairs:
        for transform in _TRANSFORMS:
            for background in backgrounds:
                for combine in pair_combines:
                    if collector.full:
                        return
                    base = {
                        "op": "mask",
                        "partition": spec,
                        "indices": [left, right],
                        "transforms": ["identity", transform],
                        "background": background,
                        "combine": combine,
                    }
                    observed = _mask_observations(collector.train, base)
                    if observed is not None:
                        contexts, false_values, true_values = observed
                        pool = _output_color_selectors(count, first.separator is not None)
                        false_selectors = _infer_selectors(false_values, contexts, pool)
                        true_selectors = _infer_selectors(true_values, contexts, pool)
                        for false_color, true_color in itertools.product(false_selectors, true_selectors):
                            program = dict(base)
                            program.update(
                                {
                                    "render": "solid",
                                    "false_color": false_color,
                                    "true_color": true_color,
                                }
                            )
                            collector.propose(
                                "partition_boolean",
                                program,
                                partition_cost
                                + 5
                                + (transform != "identity")
                                + _selector_cost(background)
                                + _selector_cost(false_color)
                                + _selector_cost(true_color),
                            )
                    for render_index in (0, 1):
                        panel_observed = _masked_panel_false_observations(collector.train, base, render_index)
                        if panel_observed is None:
                            continue
                        contexts, false_values = panel_observed
                        pool = _output_color_selectors(count, first.separator is not None)
                        for false_color in _infer_selectors(false_values, contexts, pool):
                            program = dict(base)
                            program.update(
                                {
                                    "render": "panel",
                                    "render_index": render_index,
                                    "false_color": false_color,
                                }
                            )
                            collector.propose(
                                "partition_comparison",
                                program,
                                partition_cost
                                + 5
                                + (transform != "identity")
                                + _selector_cost(background)
                                + _selector_cost(false_color),
                            )

    if count > 2 and aligned_panel_output:
        for combine in ("or", "and", "xor", "exactly_one"):
            for background in backgrounds:
                if collector.full:
                    return
                base = {
                    "op": "mask",
                    "partition": spec,
                    "indices": list(range(count)),
                    "transforms": ["identity"] * count,
                    "background": background,
                    "combine": combine,
                }
                observed = _mask_observations(collector.train, base)
                if observed is None:
                    continue
                contexts, false_values, true_values = observed
                pool = _output_color_selectors(count, first.separator is not None)
                false_selectors = _infer_selectors(false_values, contexts, pool)
                true_selectors = _infer_selectors(true_values, contexts, pool)
                for false_color, true_color in itertools.product(false_selectors, true_selectors):
                    program = dict(base)
                    program.update(
                        {
                            "render": "solid",
                            "false_color": false_color,
                            "true_color": true_color,
                        }
                    )
                    collector.propose(
                        "partition_boolean_nary",
                        program,
                        partition_cost
                        + 5
                        + count
                        + _selector_cost(background)
                        + _selector_cost(false_color)
                        + _selector_cost(true_color),
                    )


def compile_task(task: Any, limits: Any = None) -> list[dict[str, Any]]:
    """Return exact-fit panel programs in the Block 13 tournament contract."""

    try:
        bounds = Limits.from_value(limits)
        train, tests = _sanitize(task, bounds)
        all_inputs = [source for source, _ in train] + list(tests)
        specs = _partition_specs(all_inputs, bounds)

        def demo_shape_priority(spec: Mapping[str, Any]) -> tuple[int, int, int, str]:
            native = True
            selected = True
            layouts: set[tuple[int, int, int]] = set()
            try:
                for source, target in train:
                    panel_set = _decompose(source, spec)
                    layouts.add((panel_set.rows, panel_set.cols, len(panel_set.panels)))
                    target_shape = _shape(target)
                    native_shapes = {
                        (panel_set.rows, panel_set.cols),
                        (panel_set.cols, panel_set.rows),
                    }
                    if panel_set.separator is not None:
                        native_shapes.update(
                            {
                                (panel_set.rows * 2 - 1, panel_set.cols * 2 - 1),
                                (panel_set.cols * 2 - 1, panel_set.rows * 2 - 1),
                            }
                        )
                    native &= target_shape in native_shapes
                    selected &= target_shape in {_shape(panel) for panel in panel_set.panels}
            except (IndexError, KeyError, TypeError, ValueError):
                return 3, 1, _partition_cost(spec), _canonical(spec)
            return (
                0 if native else 1 if selected else 2,
                0 if len(layouts) == 1 else 1,
                _partition_cost(spec),
                _canonical(spec),
            )

        specs.sort(key=demo_shape_priority)
        collector = _Collector(train, tests, bounds)
        for spec in specs:
            _enumerate_partition(collector, spec)
            if collector.full:
                break
    except (IndexError, KeyError, TypeError, ValueError, OverflowError):
        return []

    # Quotient candidates by their complete test behavior.  Within a behavior,
    # retain the least complex canonical program.  This is deterministic and
    # does not consult any held-out labels.
    best: dict[str, dict[str, Any]] = {}
    for candidate in collector.candidates:
        behavior = _canonical(candidate["test_outputs"])
        old = best.get(behavior)
        rank = (candidate["complexity"], candidate["family"], _canonical(candidate["program"]))
        if old is None:
            best[behavior] = candidate
        else:
            old_rank = (old["complexity"], old["family"], _canonical(old["program"]))
            if rank < old_rank:
                best[behavior] = candidate
    result = sorted(
        best.values(),
        key=lambda item: (item["complexity"], item["family"], _canonical(item["program"]), _canonical(item["test_outputs"])),
    )
    return result[: bounds.max_candidates]


__all__ = ["compile_task", "execute_program"]
