"""Bounded panel, separator, and template composition synthesis.

The entrant recognizes a deliberately small language of executable layout
programs.  Programs discover separators, panels, masks, objects, and colour
roles again at replay time; they never retain task identities or test grids.
Compilation requires exact replay of every demonstration and quotients the
complete multi-test behaviour.  Undefined roles, exhausted budgets, and
behavioural ambiguity all cause abstention.

Author: Komorebi P.
"""

from __future__ import annotations

from collections import Counter, deque
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import hashlib
import json
from math import gcd
from typing import Any, Iterable


Grid = tuple[tuple[int, ...], ...]
Point = tuple[int, int]
Pair = tuple[Grid, Grid]
SCHEMA = "komorebi.pr_lasm.block14.panel_template_composer.v1"


class _Undefined(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class Limits:
    max_side: int = 30
    max_cells: int = 900
    max_programs: int = 128
    max_executor_calls: int = 4096
    max_mdl: int = 32
    max_candidates: int = 1

    @classmethod
    def from_value(cls, value: Any) -> "Limits":
        if isinstance(value, cls):
            return value
        if not isinstance(value, Mapping):
            return cls()
        default = cls()

        def integer(name: str, fallback: int, ceiling: int) -> int:
            raw = value.get(name, fallback)
            if isinstance(raw, bool) or not isinstance(raw, int) or raw <= 0:
                return fallback
            return min(raw, ceiling)

        cap = value.get("candidate_cap", value.get("max_candidates", 1))
        if isinstance(cap, bool) or not isinstance(cap, int) or cap <= 0:
            cap = 1
        return cls(
            max_side=integer("max_side", default.max_side, 60),
            max_cells=integer("max_cells", default.max_cells, 3600),
            max_programs=integer("max_programs", default.max_programs, 512),
            max_executor_calls=integer(
                "max_executor_calls", default.max_executor_calls, 100_000
            ),
            max_mdl=integer("max_mdl", default.max_mdl, 128),
            max_candidates=min(cap, 1),
        )


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _grid(value: Any, limits: Limits) -> Grid:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or not value:
        raise _Undefined("empty grid")
    rows: list[tuple[int, ...]] = []
    width: int | None = None
    for raw in value:
        if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes)) or not raw:
            raise _Undefined("invalid row")
        row: list[int] = []
        for cell in raw:
            if isinstance(cell, bool) or not isinstance(cell, int) or not 0 <= cell <= 9:
                raise _Undefined("invalid cell")
            row.append(cell)
        if width is None:
            width = len(row)
        elif width != len(row):
            raise _Undefined("ragged grid")
        rows.append(tuple(row))
    h, w = len(rows), int(width or 0)
    if h > limits.max_side or w > limits.max_side or h * w > limits.max_cells:
        raise _Undefined("grid exceeds cap")
    return tuple(rows)


def _plain(grid: Grid) -> list[list[int]]:
    return [list(row) for row in grid]


def _freeze(rows: Sequence[Sequence[int]]) -> Grid:
    return tuple(tuple(int(cell) for cell in row) for row in rows)


def _read_task(task: Any, limits: Limits) -> tuple[tuple[Pair, ...], tuple[Grid, ...]]:
    if not isinstance(task, Mapping):
        raise _Undefined("invalid task")
    raw_train, raw_test = task.get("train"), task.get("test")
    if (
        not isinstance(raw_train, Sequence)
        or isinstance(raw_train, (str, bytes))
        or not raw_train
        or not isinstance(raw_test, Sequence)
        or isinstance(raw_test, (str, bytes))
        or not raw_test
        or len(raw_train) + len(raw_test) > 16
    ):
        raise _Undefined("invalid examples")
    train: list[Pair] = []
    for example in raw_train:
        if not isinstance(example, Mapping):
            raise _Undefined("invalid demonstration")
        train.append(
            (_grid(example.get("input"), limits), _grid(example.get("output"), limits))
        )
    tests: list[Grid] = []
    for example in raw_test:
        if not isinstance(example, Mapping):
            raise _Undefined("invalid test")
        # Test outputs, even if injected by a caller, are intentionally ignored.
        tests.append(_grid(example.get("input"), limits))
    return tuple(train), tuple(tests)


def _shape(grid: Grid) -> tuple[int, int]:
    return len(grid), len(grid[0])


def _mode(values: Iterable[int]) -> int:
    counts = Counter(values)
    if not counts:
        raise _Undefined("empty role")
    maximum = max(counts.values())
    winners = [color for color, count in counts.items() if count == maximum]
    if len(winners) != 1:
        raise _Undefined("tied mode")
    return winners[0]


def _background(grid: Grid) -> int:
    return _mode(cell for row in grid for cell in row)


def _bbox(points: Iterable[Point]) -> tuple[int, int, int, int]:
    values = tuple(points)
    if not values:
        raise _Undefined("empty object")
    return (
        min(r for r, _ in values),
        max(r for r, _ in values),
        min(c for _, c in values),
        max(c for _, c in values),
    )


def _components(grid: Grid, points: Iterable[Point], connectivity: int = 4) -> list[set[Point]]:
    remaining = set(points)
    offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    if connectivity == 8:
        offsets += [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    answer: list[set[Point]] = []
    while remaining:
        seed = min(remaining)
        remaining.remove(seed)
        component = {seed}
        queue = deque([seed])
        while queue:
            r, c = queue.popleft()
            for dr, dc in offsets:
                point = r + dr, c + dc
                if point in remaining:
                    remaining.remove(point)
                    component.add(point)
                    queue.append(point)
        answer.append(component)
    return sorted(answer, key=lambda item: min(item))


def _axis_intervals(length: int, lines: Sequence[int]) -> tuple[tuple[int, int], ...] | None:
    if not lines:
        return ((0, length),)
    if any(b == a + 1 for a, b in zip(lines, lines[1:])):
        # Multi-cell divider bands are not part of this deliberately narrow grammar.
        return None
    intervals: list[tuple[int, int]] = []
    start = 0
    for line in lines:
        if line > start:
            intervals.append((start, line))
        start = line + 1
    if start < length:
        intervals.append((start, length))
    if not intervals:
        return None
    lengths = [b - a for a, b in intervals]
    if len(set(lengths)) != 1:
        # A short trailing pad is common when a regular tiled workspace does
        # not consume the whole ARC canvas.  It is not treated as a panel.
        if len(intervals) >= 2 and len(set(lengths[:-1])) == 1 and lengths[-1] < lengths[0]:
            intervals.pop()
        else:
            return None
    return tuple(intervals)


@dataclass(frozen=True, slots=True)
class _Lattice:
    separator: int
    rows: tuple[tuple[int, int], ...]
    columns: tuple[tuple[int, int], ...]
    row_lines: tuple[int, ...]
    column_lines: tuple[int, ...]


def _lattice(grid: Grid, *, both_axes: bool = False) -> _Lattice:
    h, w = _shape(grid)
    proposals: list[_Lattice] = []
    for color in sorted({cell for row in grid for cell in row}):
        row_lines = tuple(i for i, row in enumerate(grid) if all(x == color for x in row))
        column_lines = tuple(
            j for j in range(w) if all(grid[i][j] == color for i in range(h))
        )
        rows = _axis_intervals(h, row_lines)
        columns = _axis_intervals(w, column_lines)
        if rows is None or columns is None:
            continue
        if both_axes and (len(rows) < 2 or len(columns) < 2):
            continue
        if not both_axes and len(rows) < 2 and len(columns) < 2:
            continue
        if len(rows) * len(columns) > 100:
            continue
        proposals.append(_Lattice(color, rows, columns, row_lines, column_lines))
    if not proposals:
        raise _Undefined("no regular lattice")
    score = max(
        (len(p.rows) * len(p.columns), len(p.row_lines) + len(p.column_lines))
        for p in proposals
    )
    winners = [
        p
        for p in proposals
        if (len(p.rows) * len(p.columns), len(p.row_lines) + len(p.column_lines)) == score
    ]
    geometries = {
        (p.separator, p.rows, p.columns, p.row_lines, p.column_lines): p for p in winners
    }
    if len(geometries) != 1:
        raise _Undefined("ambiguous lattice")
    return next(iter(geometries.values()))


def _panels(grid: Grid, lattice: _Lattice) -> list[list[Grid]]:
    return [
        [
            tuple(tuple(grid[r][c] for c in range(c0, c1)) for r in range(r0, r1))
            for c0, c1 in lattice.columns
        ]
        for r0, r1 in lattice.rows
    ]


def _panel_base(panels: Sequence[Sequence[Grid]], separator: int) -> int:
    return _mode(
        cell
        for row in panels
        for panel in row
        for line in panel
        for cell in line
        if cell != separator
    )


def _blank_layout(grid: Grid, lattice: _Lattice, base: int) -> list[list[int]]:
    result = [list(row) for row in grid]
    for r0, r1 in lattice.rows:
        for c0, c1 in lattice.columns:
            for r in range(r0, r1):
                for c in range(c0, c1):
                    result[r][c] = base
    return result


def _put_panel(
    result: list[list[int]], lattice: _Lattice, row: int, column: int, panel: Grid
) -> None:
    r0, r1 = lattice.rows[row]
    c0, c1 = lattice.columns[column]
    if _shape(panel) != (r1 - r0, c1 - c0):
        raise _Undefined("panel shape mismatch")
    for i, line in enumerate(panel):
        result[r0 + i][c0:c1] = list(line)


def _panel_mask(panel: Grid, base: int) -> tuple[Point, ...]:
    return tuple(
        (r, c)
        for r, row in enumerate(panel)
        for c, cell in enumerate(row)
        if cell != base
    )


def _single_ink(panel: Grid, base: int) -> tuple[int, tuple[Point, ...]] | None:
    mask = _panel_mask(panel, base)
    if not mask:
        return None
    colors = {panel[r][c] for r, c in mask}
    if len(colors) != 1:
        raise _Undefined("multicolour panel")
    return next(iter(colors)), mask


def _macro_argmax_fill(grid: Grid) -> Grid:
    lattice = _lattice(grid, both_axes=True)
    panels = _panels(grid, lattice)
    base = _panel_base(panels, lattice.separator)
    inks: list[list[tuple[int, tuple[Point, ...]] | None]] = []
    colors: set[int] = set()
    for row in panels:
        line = []
        for panel in row:
            item = _single_ink(panel, base)
            if item:
                colors.add(item[0])
            line.append(item)
        inks.append(line)
    if len(colors) != 1:
        raise _Undefined("argmax requires one ink role")
    maximum = max((len(item[1]) for row in inks for item in row if item), default=0)
    minimum = min((len(item[1]) for row in inks for item in row if item), default=0)
    if not maximum or maximum == minimum:
        raise _Undefined("no count contrast")
    result = _blank_layout(grid, lattice, base)
    ph, pw = _shape(panels[0][0])
    changed = False
    for r, row in enumerate(inks):
        for c, item in enumerate(row):
            if item and len(item[1]) == maximum:
                color = item[0]
                _put_panel(result, lattice, r, c, tuple((color,) * pw for _ in range(ph)))
                changed = True
    if not changed:
        raise _Undefined("no selected panel")
    return _freeze(result)


def _macro_row_template(grid: Grid) -> Grid:
    lattice = _lattice(grid, both_axes=True)
    panels = _panels(grid, lattice)
    nr, nc = len(panels), len(panels[0])
    if nr < 2 or nc < 2:
        raise _Undefined("layout too small")
    base = _panel_base(panels, lattice.separator)
    locations: dict[int, list[tuple[int, int, tuple[Point, ...]]]] = {}
    for r, row in enumerate(panels):
        for c, panel in enumerate(row):
            for color in sorted({x for line in panel for x in line if x != base}):
                mask = tuple(
                    (i, j)
                    for i, line in enumerate(panel)
                    for j, value in enumerate(line)
                    if value == color
                )
                locations.setdefault(color, []).append((r, c, mask))
    if len(locations) != nr + 1:
        raise _Undefined("wrong number of template roles")
    totals = {color: sum(len(mask) for _, _, mask in values) for color, values in locations.items()}
    maximum = max(totals.values())
    templates = [color for color, count in totals.items() if count == maximum]
    if len(templates) != 1:
        raise _Undefined("template is tied")
    template_color = templates[0]
    if len(locations[template_color]) != 1:
        raise _Undefined("template is distributed")
    template_mask = locations[template_color][0][2]
    keys: dict[int, int] = {}
    key_masks: set[tuple[Point, ...]] = set()
    for color, values in locations.items():
        if color == template_color or len(values) != 1:
            continue
        row, _, mask = values[0]
        if row in keys:
            raise _Undefined("two row keys")
        keys[row] = color
        key_masks.add(mask)
    if len(keys) != nr or len(key_masks) != 1 or template_mask in key_masks:
        raise _Undefined("row key grammar mismatch")
    result = _blank_layout(grid, lattice, base)
    ph, pw = _shape(panels[0][0])
    for r in range(nr):
        tile = [[base] * pw for _ in range(ph)]
        for i, j in template_mask:
            tile[i][j] = keys[r]
        frozen = _freeze(tile)
        for c in range(nc):
            _put_panel(result, lattice, r, c, frozen)
    return _freeze(result)


def _macro_marker_template(grid: Grid) -> Grid:
    lattice = _lattice(grid, both_axes=True)
    panels = _panels(grid, lattice)
    base = _panel_base(panels, lattice.separator)
    by_color: dict[int, list[tuple[int, int, tuple[Point, ...]]]] = {}
    for r, row in enumerate(panels):
        for c, panel in enumerate(row):
            item = _single_ink(panel, base)
            if item:
                color, mask = item
                by_color.setdefault(color, []).append((r, c, mask))
    if len(by_color) != 2:
        raise _Undefined("marker/template needs two roles")
    possibilities = []
    for template, markers in ((a, b) for a in by_color for b in by_color if a != b):
        if len(by_color[template]) != 1 or len(by_color[markers]) < 2:
            continue
        marker_masks = {entry[2] for entry in by_color[markers]}
        if len(marker_masks) != 1:
            continue
        template_mask = by_color[template][0][2]
        marker_mask = next(iter(marker_masks))
        if len(template_mask) <= len(marker_mask):
            continue
        possibilities.append((template, markers, template_mask))
    if len(possibilities) != 1:
        raise _Undefined("ambiguous template role")
    template, marker, template_mask = possibilities[0]
    result = _blank_layout(grid, lattice, base)
    ph, pw = _shape(panels[0][0])
    tile = [[base] * pw for _ in range(ph)]
    for i, j in template_mask:
        tile[i][j] = template
    filled = _freeze(tile)
    for color in (template, marker):
        for r, c, _ in by_color[color]:
            _put_panel(result, lattice, r, c, filled)
    return _freeze(result)


def _macro_halo(grid: Grid) -> Grid:
    lattice = _lattice(grid, both_axes=True)
    panels = _panels(grid, lattice)
    ph, pw = _shape(panels[0][0])
    base = _panel_base(panels, lattice.separator)
    macro: list[list[int]] = []
    for row in panels:
        line = []
        for panel in row:
            values = {x for raw in panel for x in raw}
            if len(values) != 1:
                raise _Undefined("halo tiles must be uniform")
            line.append(next(iter(values)))
        macro.append(line)
    colors = sorted({x for row in macro for x in row if x != base})
    if len(colors) < 2:
        raise _Undefined("halo requires anchor and brush roles")
    nr, nc = len(macro), len(macro[0])
    candidates = []
    for anchor in colors:
        anchors = [(r, c) for r in range(nr) for c in range(nc) if macro[r][c] == anchor]
        if len(anchors) < 2:
            continue
        masks = []
        for r, c in anchors:
            mask = tuple(
                (dr, dc, macro[r + dr][c + dc])
                for dr in (-1, 0, 1)
                for dc in (-1, 0, 1)
                if (dr or dc)
                and 0 <= r + dr < nr
                and 0 <= c + dc < nc
                and macro[r + dr][c + dc] not in (base, anchor)
            )
            masks.append(mask)
        maximum = max(map(len, masks))
        patterns = {mask for mask in masks if len(mask) == maximum}
        if maximum < 2 or len(patterns) != 1:
            continue
        pattern = next(iter(patterns))
        if not any(
            0 <= r + dr < nr
            and 0 <= c + dc < nc
            and macro[r + dr][c + dc] == base
            for r, c in anchors
            for dr, dc, _ in pattern
        ):
            continue
        candidates.append((anchor, pattern, anchors))
    if len(candidates) != 1:
        raise _Undefined("halo roles are ambiguous")
    _, pattern, anchors = candidates[0]
    out = [row[:] for row in macro]
    changed = False
    for r, c in anchors:
        for dr, dc, brush in pattern:
            rr, cc = r + dr, c + dc
            if 0 <= rr < nr and 0 <= cc < nc:
                if out[rr][cc] == base:
                    out[rr][cc] = brush
                    changed = True
                elif out[rr][cc] not in (brush, macro[r][c]):
                    raise _Undefined("halo collision")
    if not changed:
        raise _Undefined("halo made no change")
    result = _blank_layout(grid, lattice, base)
    for r in range(nr):
        for c in range(nc):
            color = out[r][c]
            _put_panel(result, lattice, r, c, tuple((color,) * pw for _ in range(ph)))
    return _freeze(result)


def _flip_mask(mask: tuple[Point, ...], h: int, w: int, vertical: bool, horizontal: bool) -> tuple[Point, ...]:
    return tuple(
        sorted(
            ((h - 1 - r if vertical else r), (w - 1 - c if horizontal else c))
            for r, c in mask
        )
    )


def _macro_complete_quartets(grid: Grid) -> Grid:
    lattice = _lattice(grid, both_axes=True)
    panels = _panels(grid, lattice)
    nr, nc = len(panels), len(panels[0])
    base = _panel_base(panels, lattice.separator)
    ph, pw = _shape(panels[0][0])
    items = [[_single_ink(panel, base) for panel in row] for row in panels]
    additions: dict[tuple[int, int], tuple[int, tuple[Point, ...]]] = {}
    for r in range(nr - 1):
        for c in range(nc - 1):
            cells = [(r, c), (r, c + 1), (r + 1, c), (r + 1, c + 1)]
            present = [(index, items[rr][cc]) for index, (rr, cc) in enumerate(cells) if items[rr][cc]]
            if len(present) != 3:
                continue
            colors = {item[0] for _, item in present if item}
            if len(colors) != 1:
                continue
            canonical = []
            for index, item in present:
                assert item is not None
                vertical, horizontal = index >= 2, index % 2 == 1
                canonical.append(_flip_mask(item[1], ph, pw, vertical, horizontal))
            if len(set(canonical)) != 1:
                continue
            missing = next(index for index in range(4) if items[cells[index][0]][cells[index][1]] is None)
            vertical, horizontal = missing >= 2, missing % 2 == 1
            mask = _flip_mask(canonical[0], ph, pw, vertical, horizontal)
            key = cells[missing]
            value = (next(iter(colors)), mask)
            if key in additions and additions[key] != value:
                raise _Undefined("quartet collision")
            additions[key] = value
    if not additions:
        raise _Undefined("no incomplete quartet")
    result = [list(row) for row in grid]
    for (r, c), (color, mask) in additions.items():
        tile = [[base] * pw for _ in range(ph)]
        for i, j in mask:
            tile[i][j] = color
        _put_panel(result, lattice, r, c, _freeze(tile))
    return _freeze(result)


def _macro_complete_from_template(grid: Grid) -> Grid:
    lattice = _lattice(grid, both_axes=True)
    panels = _panels(grid, lattice)
    base = _panel_base(panels, lattice.separator)
    masks = [[set(_panel_mask(panel, base)) for panel in row] for row in panels]
    maximum = max(len(mask) for row in masks for mask in row)
    templates = {frozenset(mask) for row in masks for mask in row if len(mask) == maximum}
    if len(templates) != 1 or maximum < 4:
        raise _Undefined("dense template is not unique")
    template = set(next(iter(templates)))
    if any(not mask <= template for row in masks for mask in row):
        raise _Undefined("panel is not a template subset")
    if all(mask == template for row in masks for mask in row):
        raise _Undefined("template already complete")
    result = _blank_layout(grid, lattice, base)
    ph, pw = _shape(panels[0][0])
    for r, row in enumerate(panels):
        for c, panel in enumerate(row):
            tile = [[base] * pw for _ in range(ph)]
            for i, j in template:
                tile[i][j] = panel[i][j] if panel[i][j] != base else lattice.separator
            _put_panel(result, lattice, r, c, _freeze(tile))
    return _freeze(result)


def _macro_sort_by_internal_position(grid: Grid) -> Grid:
    lattice = _lattice(grid, both_axes=True)
    panels = _panels(grid, lattice)
    if len(panels) != 3 or len(panels[0]) != 3:
        raise _Undefined("positional sorting requires a 3 by 3 layout")
    base = _panel_base(panels, lattice.separator)
    ph, pw = _shape(panels[0][0])
    if ph < 3 or pw < 3:
        raise _Undefined("panels too small for positional sorting")
    entries = [(panel, tuple(_panel_mask(panel, base))) for row in panels for panel in row]
    if any(not mask for _, mask in entries):
        raise _Undefined("positional sort has an empty tile")
    sizes = [len(mask) for _, mask in entries]
    maximum = max(sizes)
    composites = [(panel, mask) for panel, mask in entries if len(mask) == maximum]
    if len(composites) != 1 or maximum <= max(size for size in sizes if size != maximum):
        raise _Undefined("composite tile is not unique")
    placements: dict[tuple[int, int], Grid] = {(1, 1): composites[0][0]}
    for panel, mask in entries:
        if panel == composites[0][0] and mask == composites[0][1]:
            continue
        r0, r1, c0, c1 = _bbox(mask)
        vertical = 0 if r1 < ph // 2 else 2 if r0 > (ph - 1) // 2 else 1
        horizontal = 0 if c1 < pw // 2 else 2 if c0 > (pw - 1) // 2 else 1
        key = vertical, horizontal
        if key == (1, 1) or key in placements:
            raise _Undefined("internal positions collide")
        placements[key] = panel
    if set(placements) != {(r, c) for r in range(3) for c in range(3)}:
        raise _Undefined("internal position set incomplete")
    result = _blank_layout(grid, lattice, base)
    for key, panel in placements.items():
        _put_panel(result, lattice, key[0], key[1], panel)
    return _freeze(result)


def _macro_sort_by_ink_count(grid: Grid) -> Grid:
    lattice = _lattice(grid, both_axes=True)
    panels = _panels(grid, lattice)
    nr, nc = len(panels), len(panels[0])
    base = _panel_base(panels, lattice.separator)
    entries = [
        (len(_panel_mask(panel, base)), r, c, panel)
        for r, row in enumerate(panels)
        for c, panel in enumerate(row)
    ]
    counts = [count for count, _, _, _ in entries]
    if len(set(counts)) != nr * nc or min(counts) != 0:
        raise _Undefined("ink counts are not a unique rank set")
    by_count = {count: panel for count, _, _, panel in entries}
    zero = next((r, c) for count, r, c, _ in entries if count == 0)
    full = next((r, c) for count, r, c, _ in entries if count == max(counts))
    if full[0] == zero[0]:
        forward = full[1] < zero[1]
    else:
        forward = full[0] < zero[0]
    result = _blank_layout(grid, lattice, base)
    ranked = [panel for _, panel in sorted(by_count.items())]
    for rank, panel in enumerate(ranked):
        r, offset = divmod(rank, nc)
        key = (r, nc - 1 - offset) if forward else (nr - 1 - r, offset)
        _put_panel(result, lattice, key[0], key[1], panel)
    return _freeze(result)


def _macro_connect_matching(grid: Grid, connector: int) -> Grid:
    lattice = _lattice(grid, both_axes=True)
    panels = _panels(grid, lattice)
    base = _panel_base(panels, lattice.separator)
    extra = sorted(
        {
            cell
            for row in panels
            for panel in row
            for line in panel
            for cell in line
            if cell not in (base, lattice.separator)
        }
    )
    if len(extra) != 1:
        raise _Undefined("marked prototype is not unique-coloured")
    marker = extra[0]
    if connector in (base, lattice.separator, marker):
        raise _Undefined("connector collides with layout roles")
    marked = []
    for r, row in enumerate(panels):
        for c, panel in enumerate(row):
            if any(marker in line for line in panel):
                marked.append((r, c, panel))
    if len(marked) != 1:
        raise _Undefined("prototype marker is distributed")
    _, _, prototype = marked[0]
    holes = tuple(
        (r, c)
        for r, row in enumerate(prototype)
        for c, cell in enumerate(row)
        if cell == lattice.separator
    )
    if not holes:
        raise _Undefined("prototype has no structural holes")
    matches = []
    for r, row in enumerate(panels):
        for c, panel in enumerate(row):
            panel_holes = tuple(
                (i, j)
                for i, line in enumerate(panel)
                for j, cell in enumerate(line)
                if cell == lattice.separator
            )
            if panel_holes == holes:
                matches.append((r, c))
    if len(matches) < 3:
        raise _Undefined("too few matching panels")
    match_set = set(matches)
    connectors: set[tuple[int, int]] = set()
    for r in range(len(panels)):
        columns = sorted(c for rr, c in matches if rr == r)
        for left, right in zip(columns, columns[1:]):
            connectors.update((r, c) for c in range(left + 1, right))
    for c in range(len(panels[0])):
        rows = sorted(r for r, cc in matches if cc == c)
        for top, bottom in zip(rows, rows[1:]):
            connectors.update((r, c) for r in range(top + 1, bottom))
    connectors -= match_set
    if not connectors:
        raise _Undefined("matching panels are not alignable")
    result = [list(row) for row in grid]
    ph, pw = _shape(panels[0][0])
    for r, c in sorted(connectors | match_set):
        color = marker if (r, c) in match_set else connector
        tile = [list(line) for line in panels[r][c]]
        for i in range(ph):
            for j in range(pw):
                if tile[i][j] != lattice.separator:
                    tile[i][j] = color
        _put_panel(result, lattice, r, c, _freeze(tile))
    return _freeze(result)


def _macro_addressed_transport(grid: Grid, marker: int) -> Grid:
    lattice = _lattice(grid, both_axes=True)
    panels = _panels(grid, lattice)
    nr, nc = len(panels), len(panels[0])
    ph, pw = _shape(panels[0][0])
    if (nr, nc) != (ph, pw):
        raise _Undefined("address and layout dimensions differ")
    occurrences = []
    for r, row in enumerate(panels):
        for c, panel in enumerate(row):
            for i, line in enumerate(panel):
                for j, cell in enumerate(line):
                    if cell == marker:
                        occurrences.append((r, c, i, j))
    if len(occurrences) != 1:
        raise _Undefined("address marker is not singleton")
    source_r, source_c, address_r, address_c = occurrences[0]
    base = _panel_base(panels, lattice.separator)
    result = _blank_layout(grid, lattice, base)
    _put_panel(result, lattice, address_r, address_c, panels[source_r][source_c])
    return _freeze(result)


def _lattice_candidates(grid: Grid) -> list[_Lattice]:
    h, w = _shape(grid)
    proposals = []
    for color in sorted({cell for row in grid for cell in row}):
        row_lines = tuple(i for i, row in enumerate(grid) if all(x == color for x in row))
        column_lines = tuple(j for j in range(w) if all(grid[i][j] == color for i in range(h)))
        rows, columns = _axis_intervals(h, row_lines), _axis_intervals(w, column_lines)
        if rows is None or columns is None or (len(rows) < 2 and len(columns) < 2):
            continue
        if len(rows) * len(columns) <= 100:
            proposals.append(_Lattice(color, rows, columns, row_lines, column_lines))
    return proposals


def _sequence_panel_options(grid: Grid) -> list[tuple[list[Grid], int]]:
    options = []
    for lattice in _lattice_candidates(grid):
        panels = _panels(grid, lattice)
        try:
            base = _panel_base(panels, lattice.separator)
        except _Undefined:
            continue
        if len(lattice.rows) >= 2 and len(lattice.columns) == 1:
            options.append(([row[0] for row in panels], base))
        elif len(lattice.columns) >= 2 and len(lattice.rows) == 1:
            options.append((panels[0], base))
    return options


def _object_crop(panel: Grid, base: int) -> tuple[int, int, Grid]:
    points = [(r, c) for r, row in enumerate(panel) for c, x in enumerate(row) if x != base]
    r0, r1, c0, c1 = _bbox(points)
    crop = tuple(tuple(panel[r][c] for c in range(c0, c1 + 1)) for r in range(r0, r1 + 1))
    return r0, c0, crop


def _sequence_translate(grid: Grid) -> Grid:
    answers = []
    for panels, base in _sequence_panel_options(grid):
        try:
            answers.append(_sequence_translate_panels(panels, base))
        except _Undefined:
            pass
    unique = {_canonical(_plain(answer)): answer for answer in answers}
    if len(unique) != 1:
        raise _Undefined("translation partition ambiguous")
    return next(iter(unique.values()))


def _sequence_translate_panels(panels: Sequence[Grid], base: int) -> Grid:
    if len(panels) < 3:
        raise _Undefined("sequence too short")
    objects = [_object_crop(panel, base) for panel in panels]
    normalized = [obj[2] for obj in objects]
    if len(set(normalized)) != 1:
        raise _Undefined("object shape changes")
    dr = objects[-1][0] - objects[-2][0]
    dc = objects[-1][1] - objects[-2][1]
    if not dr and not dc:
        raise _Undefined("stationary sequence")
    r0, c0, crop = objects[-1][0] + dr, objects[-1][1] + dc, objects[-1][2]
    h, w = _shape(panels[-1])
    ch, cw = _shape(crop)
    if not (0 <= r0 <= h - ch and 0 <= c0 <= w - cw):
        raise _Undefined("extrapolation leaves panel")
    result = [[base] * w for _ in range(h)]
    for r, row in enumerate(crop):
        result[r0 + r][c0 : c0 + cw] = list(row)
    return _freeze(result)


def _sequence_rectangle_growth(grid: Grid) -> Grid:
    answers = []
    for panels, base in _sequence_panel_options(grid):
        try:
            answers.append(_sequence_growth_panels(panels, base))
        except _Undefined:
            pass
    unique = {_canonical(_plain(answer)): answer for answer in answers}
    if len(unique) != 1:
        raise _Undefined("growth partition ambiguous")
    return next(iter(unique.values()))


def _sequence_growth_panels(panels: Sequence[Grid], base: int) -> Grid:
    if len(panels) < 3:
        raise _Undefined("sequence too short")
    boxes = []
    color: int | None = None
    for panel in panels:
        points = [(r, c) for r, row in enumerate(panel) for c, x in enumerate(row) if x != base]
        r0, r1, c0, c1 = _bbox(points)
        colors = {panel[r][c] for r, c in points}
        if len(colors) != 1 or len(points) != (r1 - r0 + 1) * (c1 - c0 + 1):
            raise _Undefined("not a solid rectangle")
        if color is None:
            color = next(iter(colors))
        elif color != next(iter(colors)):
            raise _Undefined("rectangle colour changes")
        boxes.append((r0, c0, r1 - r0 + 1, c1 - c0 + 1))
    deltas = [tuple(b - a for a, b in zip(x, y)) for x, y in zip(boxes, boxes[1:])]
    if len(set(deltas)) != 1 or not any(deltas[-1]):
        raise _Undefined("nonlinear growth")
    next_box = tuple(a + b for a, b in zip(boxes[-1], deltas[-1]))
    r0, c0, bh, bw = next_box
    h, w = _shape(panels[-1])
    if bh <= 0 or bw <= 0 or not (0 <= r0 <= h - bh and 0 <= c0 <= w - bw):
        raise _Undefined("growth leaves panel")
    result = [[base] * w for _ in range(h)]
    for r in range(r0, r0 + bh):
        for c in range(c0, c0 + bw):
            result[r][c] = int(color)
    return _freeze(result)


def _sequence_progression(grid: Grid) -> Grid:
    answers = []
    for operation in (_sequence_translate, _sequence_rectangle_growth, _sequence_cumulative_frontier):
        try:
            answers.append(operation(grid))
        except _Undefined:
            pass
    unique = {_canonical(_plain(answer)): answer for answer in answers}
    if len(unique) != 1:
        raise _Undefined("sequence model ambiguous")
    return next(iter(unique.values()))


def _sequence_cumulative_frontier(grid: Grid) -> Grid:
    answers = []
    for panels, _ in _sequence_panel_options(grid):
        try:
            answers.append(_cumulative_frontier_panels(panels))
        except _Undefined:
            pass
    unique = {_canonical(_plain(answer)): answer for answer in answers}
    if len(unique) != 1:
        raise _Undefined("frontier partition ambiguous")
    return next(iter(unique.values()))


def _cumulative_frontier_panels(panels: Sequence[Grid]) -> Grid:
    if len(panels) < 3 or len({_shape(panel) for panel in panels}) != 1:
        raise _Undefined("frontier sequence malformed")
    changes: list[tuple[tuple[Point, ...], int, int]] = []
    for before, after in zip(panels, panels[1:]):
        delta = [
            (r, c)
            for r in range(len(before))
            for c in range(len(before[0]))
            if before[r][c] != after[r][c]
        ]
        if not delta:
            raise _Undefined("empty frontier")
        transitions = {(before[r][c], after[r][c]) for r, c in delta}
        if len(transitions) != 1:
            raise _Undefined("frontier has multiple states")
        old, new = next(iter(transitions))
        changes.append((tuple(delta), old, new))
    if len({(old, new) for _, old, new in changes}) != 1:
        raise _Undefined("frontier state changes")
    old, new = changes[-1][1], changes[-1][2]
    last = panels[-1]

    def normalize(mask: tuple[Point, ...]) -> tuple[Point, ...]:
        r0, _, c0, _ = _bbox(mask)
        return tuple(sorted((r - r0, c - c0) for r, c in mask))

    normalized = [normalize(mask) for mask, _, _ in changes]
    next_mask: tuple[Point, ...] | None = None
    if len(set(normalized)) == 1:
        boxes = [_bbox(mask) for mask, _, _ in changes]
        if len(boxes) < 2:
            raise _Undefined("frontier motion underdetermined")
        dr, dc = boxes[-1][0] - boxes[-2][0], boxes[-1][2] - boxes[-2][2]
        candidate = tuple((r + dr, c + dc) for r, c in changes[-1][0])
        if all(0 <= r < len(last) and 0 <= c < len(last[0]) and last[r][c] == old for r, c in candidate):
            next_mask = candidate
    if next_mask is None:
        # A shrinking sweep may finish one repeated motif.  Restart the first
        # observed frontier shape at the earliest still-unpainted translation
        # strictly after the last frontier in reading order.
        template = normalized[0]
        boxes = [_bbox(mask) for mask, _, _ in changes]
        horizontal = len(boxes) >= 2 and abs(boxes[-1][2] - boxes[-2][2]) >= abs(boxes[-1][0] - boxes[-2][0])
        last_axis = boxes[-1][2] if horizontal else boxes[-1][0]
        candidates = []
        for r0 in range(len(last)):
            for c0 in range(len(last[0])):
                candidate = tuple((r0 + r, c0 + c) for r, c in template)
                first_axis = min(c for _, c in candidate) if horizontal else min(r for r, _ in candidate)
                if first_axis <= last_axis:
                    continue
                if all(
                    0 <= r < len(last)
                    and 0 <= c < len(last[0])
                    and last[r][c] == old
                    for r, c in candidate
                ):
                    candidates.append(candidate)
        if not candidates:
            raise _Undefined("no next frontier site")
        next_mask = min(
            candidates,
            key=lambda mask: (
                min(c for _, c in mask), min(r for r, _ in mask)
            ) if horizontal else (
                min(r for r, _ in mask), min(c for _, c in mask)
            ),
        )
    result = [list(row) for row in last]
    for r, c in next_mask:
        result[r][c] = new
    return _freeze(result)


def _bordered_panel_extrapolate(grid: Grid) -> Grid:
    lattice = _lattice(grid)
    if len(lattice.rows) != 1 or len(lattice.columns) < 3:
        raise _Undefined("requires a horizontal panel strip")
    h, w = _shape(grid)
    if (
        tuple(sorted(lattice.row_lines)) != (0, h - 1)
        or not lattice.column_lines
        or lattice.column_lines[0] != 0
        or lattice.column_lines[-1] != w - 1
    ):
        raise _Undefined("strip is not enclosed")
    panels = _panels(grid, lattice)[0]
    base = _panel_base([panels], lattice.separator)
    objects = [_object_crop(panel, base) for panel in panels]
    if len({obj[2] for obj in objects}) != 1:
        raise _Undefined("strip objects differ")
    dr = objects[-1][0] - objects[-2][0]
    dc = objects[-1][1] - objects[-2][1]
    if not dr and not dc:
        raise _Undefined("stationary strip")
    # Moving downward uses the next free leading row beyond the translated
    # object extent; upward motion already exposes that leading edge.
    extent_bias = len(objects[-1][2]) - 1 if dr > 0 else 0
    r0, c0, crop = objects[-1][0] + dr + extent_bias, objects[-1][1] + dc, objects[-1][2]
    ph, pw = _shape(panels[0])
    ch, cw = _shape(crop)
    if not (0 <= r0 <= ph - ch and 0 <= c0 <= pw - cw):
        raise _Undefined("strip extrapolation leaves panel")
    out = [[lattice.separator] * (pw + 2) for _ in range(ph + 2)]
    for r in range(ph):
        for c in range(pw):
            out[r + 1][c + 1] = base
    for r, row in enumerate(crop):
        out[1 + r0 + r][1 + c0 : 1 + c0 + cw] = list(row)
    return _freeze(out)


def _color_components(grid: Grid, excluded: set[int]) -> dict[int, list[set[Point]]]:
    result: dict[int, list[set[Point]]] = {}
    for color in sorted({x for row in grid for x in row} - excluded):
        points = [(r, c) for r, row in enumerate(grid) for c, x in enumerate(row) if x == color]
        result[color] = _components(grid, points, 4)
    return result


def _normalized_color_shape(grid: Grid, points: set[Point]) -> tuple[Point, ...]:
    r0, _, c0, _ = _bbox(points)
    return tuple(sorted((r - r0, c - c0) for r, c in points))


def _glyph_direction(shape: tuple[Point, ...]) -> tuple[int, int]:
    if len(shape) != 5:
        raise _Undefined("guide is not a five-cell T")
    transforms = {
        tuple(sorted([(0, 0), (0, 1), (0, 2), (1, 1), (2, 1)])): (1, 0),
        tuple(sorted([(2, 0), (2, 1), (2, 2), (0, 1), (1, 1)])): (-1, 0),
        tuple(sorted([(0, 0), (1, 0), (2, 0), (1, 1), (1, 2)])): (0, 1),
        tuple(sorted([(0, 2), (1, 2), (2, 2), (1, 0), (1, 1)])): (0, -1),
    }
    if shape not in transforms:
        raise _Undefined("unknown guide orientation")
    return transforms[shape]


def _guided_transport(grid: Grid) -> Grid:
    h, w = _shape(grid)
    candidates = []
    for sep in sorted({x for row in grid for x in row}):
        lines = [r for r, row in enumerate(grid) if all(x == sep for x in row)]
        if len(lines) == 1 and 0 < lines[0] < h - 1:
            candidates.append((sep, lines[0]))
    if len(candidates) != 1:
        raise _Undefined("guide separator ambiguous")
    sep, line = candidates[0]
    base = _mode(
        grid[r][c]
        for r in range(h)
        for c in range(w)
        if r != line and grid[r][c] != sep
    )
    top = tuple(grid[:line])
    bottom = tuple(grid[line + 1 :])
    top_objects = {
        color: [{(r, c) for r, row in enumerate(top) for c, x in enumerate(row) if x == color}]
        for color in sorted({x for row in top for x in row} - {base, sep})
    }
    bottom_objects = {
        color: [{(r, c) for r, row in enumerate(bottom) for c, x in enumerate(row) if x == color}]
        for color in sorted({x for row in bottom for x in row} - {base, sep})
    }
    references = []
    for color in set(top_objects) & set(bottom_objects):
        if len(top_objects[color]) == len(bottom_objects[color]) == 1:
            a, b = top_objects[color][0], bottom_objects[color][0]
            if _normalized_color_shape(top, a) == _normalized_color_shape(bottom, b):
                references.append(color)
    if len(references) != 1:
        raise _Undefined("reference object ambiguous")
    reference = references[0]
    other = [color for color in top_objects if color != reference]
    if len(other) != 2 or any(len(top_objects[color]) != 1 for color in other):
        raise _Undefined("guide/payload roles malformed")
    directed = []
    for color in other:
        shape = _normalized_color_shape(top, top_objects[color][0])
        try:
            direction = _glyph_direction(shape)
        except _Undefined:
            continue
        directed.append((color, direction))
    if len(directed) != 1:
        raise _Undefined("guide role ambiguous")
    guide, (dr, dc) = directed[0]
    payload = next(color for color in other if color != guide)
    payload_points = top_objects[payload][0]
    pr0, pr1, pc0, pc1 = _bbox(payload_points)
    payload_crop = tuple(
        tuple(top[r][c] for c in range(pc0, pc1 + 1)) for r in range(pr0, pr1 + 1)
    )
    rr0, rr1, rc0, rc1 = _bbox(bottom_objects[reference][0])
    ph, pw = _shape(payload_crop)
    rh, rw = rr1 - rr0 + 1, rc1 - rc0 + 1
    target_r = rr0 + (rh if dr > 0 else -ph if dr < 0 else 0)
    target_c = rc0 + (rw if dc > 0 else -pw if dc < 0 else 0)
    bh, bw = _shape(bottom)
    if not (0 <= target_r <= bh - ph and 0 <= target_c <= bw - pw):
        raise _Undefined("guided placement leaves canvas")
    result = [list(row) for row in bottom]
    for r, row in enumerate(payload_crop):
        for c, value in enumerate(row):
            if value != base:
                old = result[target_r + r][target_c + c]
                if old != base:
                    raise _Undefined("guided placement collision")
                result[target_r + r][target_c + c] = value
    return _freeze(result)


def _split_arrow_transport(grid: Grid) -> Grid:
    h, w = _shape(grid)
    separators = []
    for color in sorted({x for row in grid for x in row}):
        for line in range(1, h - 1):
            if all(x == color for x in grid[line]) and line == h - line - 1:
                separators.append((color, line))
    if len(separators) != 1:
        raise _Undefined("arrow separator ambiguous")
    separator, line = separators[0]
    top, bottom = tuple(grid[:line]), tuple(grid[line + 1 :])
    base = _background(bottom)
    if any(cell != base for row in top for cell in row):
        raise _Undefined("arrow destination is not blank")
    roles = sorted({cell for row in bottom for cell in row if cell != base})
    if len(roles) != 2:
        raise _Undefined("arrow scene needs guide and payload")
    canonical_guide = tuple(sorted([(0, 2), (1, 2), (2, 0), (2, 2), (3, 1)]))
    possibilities = []
    for guide in roles:
        points = {
            (r, c)
            for r, row in enumerate(bottom)
            for c, cell in enumerate(row)
            if cell == guide
        }
        if _normalized_color_shape(bottom, points) == canonical_guide:
            possibilities.append((guide, points))
    if len(possibilities) != 1:
        raise _Undefined("left-arrow guide ambiguous")
    guide, guide_points = possibilities[0]
    payload = next(color for color in roles if color != guide)
    payload_points = {
        (r, c)
        for r, row in enumerate(bottom)
        for c, cell in enumerate(row)
        if cell == payload
    }
    pr0, pr1, pc0, pc1 = _bbox(payload_points)
    gr0, _, gc0, _ = _bbox(guide_points)
    tip = gr0 + 2, gc0
    dr, dc = tip[0] - pr1, tip[1] - pc1
    moved = {(r + dr, c + dc) for r, c in payload_points}
    if any(not (0 <= r < len(bottom) and 0 <= c < w) for r, c in moved):
        raise _Undefined("arrow placement leaves panel")
    scene = [list(row) for row in bottom]
    for r, c in payload_points:
        scene[r][c] = base
    for r, c in moved:
        scene[r][c] = payload
    result = [row[:] for row in scene]
    result.append([separator] * w)
    result.extend([[base] * w for _ in range(len(bottom))])
    return _freeze(result)


def _self_kronecker(grid: Grid) -> Grid:
    base = _background(grid)
    colors = {x for row in grid for x in row if x != base}
    if len(colors) != 1:
        raise _Undefined("self product needs one ink")
    color = next(iter(colors))
    points = [(r, c) for r, row in enumerate(grid) for c, x in enumerate(row) if x == color]
    r0, r1, c0, c1 = _bbox(points)
    crop = tuple(tuple(grid[r][c] for c in range(c0, c1 + 1)) for r in range(r0, r1 + 1))
    candidates = []
    for block in range(2, 7):
        if len(crop) != block * block or len(crop[0]) != block * block:
            continue
        mask = []
        okay = True
        for br in range(block):
            row = []
            for bc in range(block):
                values = {
                    crop[br * block + r][bc * block + c]
                    for r in range(block)
                    for c in range(block)
                }
                if values == {color}:
                    row.append(1)
                elif values == {base}:
                    row.append(0)
                else:
                    okay = False
                
            mask.append(row)
        if okay and 0 < sum(map(sum, mask)) < block * block:
            candidates.append((block, mask))
    if len(candidates) != 1:
        raise _Undefined("self-product scale ambiguous")
    block, mask = candidates[0]
    result = [[base] * (block * block) for _ in range(block * block)]
    for ar in range(block):
        for ac in range(block):
            if not mask[ar][ac]:
                continue
            for br in range(block):
                for bc in range(block):
                    if mask[br][bc]:
                        result[ar * block + br][ac * block + bc] = color
    return _freeze(result)


def _mask_template_kronecker(grid: Grid) -> Grid:
    h, w = _shape(grid)
    separators = []
    for color in sorted({x for row in grid for x in row}):
        lines = [r for r, row in enumerate(grid) if all(x == color for x in row)]
        for line in lines:
            if line > 0 and h - line - 1 == line:
                separators.append((color, line))
    if len(separators) != 1:
        raise _Undefined("template separator ambiguous")
    separator, line = separators[0]
    top, mask_grid = tuple(grid[:line]), tuple(grid[line + 1 :])
    base = _background(mask_grid)
    mask_colors = {x for row in mask_grid for x in row if x != base}
    if len(mask_colors) != 1:
        raise _Undefined("placement mask must be binary")
    candidates = []
    for scale in range(2, 5):
        if line % scale or w % scale:
            continue
        th, tw = line // scale, w // scale
        template = []
        okay = True
        for r in range(th):
            row = []
            for c in range(tw):
                values = {
                    top[r * scale + i][c * scale + j]
                    for i in range(scale)
                    for j in range(scale)
                }
                if len(values) != 1:
                    okay = False
                    break
                row.append(next(iter(values)))
            template.append(row)
        if okay and len({x for row in template for x in row if x != base}) >= 2:
            candidates.append(_freeze(template))
    if len(candidates) != 1:
        raise _Undefined("template compression ambiguous")
    template = candidates[0]
    th, tw = _shape(template)
    mh, mw = _shape(mask_grid)
    result = [[base] * (mw * tw) for _ in range(mh * th)]
    for mr in range(mh):
        for mc in range(mw):
            if mask_grid[mr][mc] == base:
                continue
            for r in range(th):
                for c in range(tw):
                    result[mr * th + r][mc * tw + c] = template[r][c]
    return _freeze(result)


def _checker_expand(grid: Grid, side: int) -> Grid:
    lattice = _lattice(grid)
    panels = _panels(grid, lattice)
    nr, nc = len(panels), len(panels[0])
    if nr < 2 or nc < 2 or any(_shape(panel) != (1, 1) for row in panels for panel in row):
        raise _Undefined("not a checkerboard code")
    gap = 2
    inner_h = side - gap * (nr + 1)
    inner_w = side - gap * (nc + 1)
    if inner_h <= 0 or inner_w <= 0 or inner_h % nr or inner_w % nc:
        raise _Undefined("fixed canvas cannot tile code")
    bh, bw = inner_h // nr, inner_w // nc
    result = [[lattice.separator] * side for _ in range(side)]
    for r in range(nr):
        for c in range(nc):
            color = panels[r][c][0][0]
            r0, c0 = gap + r * (bh + gap), gap + c * (bw + gap)
            for i in range(bh):
                for j in range(bw):
                    result[r0 + i][c0 + j] = color
    # Equal adjacent macro colours form one region; bridge the artificial
    # two-cell gutter between their expanded blocks.
    for r in range(nr):
        for c in range(nc - 1):
            left, right = panels[r][c][0][0], panels[r][c + 1][0][0]
            if left == right and left != lattice.separator:
                r0 = gap + r * (bh + gap)
                c0 = gap + c * (bw + gap) + bw
                for i in range(bh):
                    for j in range(gap):
                        result[r0 + i][c0 + j] = left
    for r in range(nr - 1):
        for c in range(nc):
            above, below = panels[r][c][0][0], panels[r + 1][c][0][0]
            if above == below and above != lattice.separator:
                r0 = gap + r * (bh + gap) + bh
                c0 = gap + c * (bw + gap)
                for i in range(gap):
                    for j in range(bw):
                        result[r0 + i][c0 + j] = above
    return _freeze(result)


def _object_extract(grid: Grid, selector: str, connectivity: int) -> Grid:
    base = _background(grid)
    points = [(r, c) for r, row in enumerate(grid) for c, x in enumerate(row) if x != base]
    components = _components(grid, points, connectivity)
    if len(components) < 2:
        raise _Undefined("needs multiple objects")

    def features(component: set[Point]) -> tuple[int, int, int, int, int]:
        r0, r1, c0, c1 = _bbox(component)
        area = len(component)
        box = (r1 - r0 + 1) * (c1 - c0 + 1)
        return area, box, area * 1000 // box, r1 - r0 + 1, c1 - c0 + 1

    index = {
        "largest_area": (0, 1),
        "smallest_area": (0, -1),
        "largest_box": (1, 1),
        "smallest_box": (1, -1),
        "densest": (2, 1),
        "sparsest": (2, -1),
        "tallest": (3, 1),
        "shortest": (3, -1),
        "widest": (4, 1),
        "narrowest": (4, -1),
    }
    if selector not in index:
        raise _Undefined("unknown object role")
    feature, sign = index[selector]
    values = [features(component)[feature] for component in components]
    target = max(values) if sign > 0 else min(values)
    winners = [component for component, value in zip(components, values) if value == target]
    if len(winners) != 1:
        raise _Undefined("object role tied")
    r0, r1, c0, c1 = _bbox(winners[0])
    return tuple(tuple(grid[r][c] for c in range(c0, c1 + 1)) for r in range(r0, r1 + 1))


def _remove_uniform_lines(grid: Grid, color_role: str) -> Grid:
    h, w = _shape(grid)
    candidates = []
    for color in sorted({x for row in grid for x in row}):
        rows = [r for r, row in enumerate(grid) if all(x == color for x in row)]
        cols = [c for c in range(w) if all(grid[r][c] == color for r in range(h))]
        if rows or cols:
            candidates.append((color, rows, cols))
    if color_role == "most_lines":
        maximum = max((len(r) + len(c) for _, r, c in candidates), default=0)
        candidates = [x for x in candidates if len(x[1]) + len(x[2]) == maximum]
    elif color_role == "nonbackground":
        base = _background(grid)
        candidates = [x for x in candidates if x[0] != base]
    else:
        raise _Undefined("unknown line role")
    if len(candidates) != 1:
        raise _Undefined("line role ambiguous")
    _, rows, cols = candidates[0]
    kept_rows = [r for r in range(h) if r not in set(rows)]
    kept_cols = [c for c in range(w) if c not in set(cols)]
    if not kept_rows or not kept_cols:
        raise _Undefined("line removal empties grid")
    return tuple(tuple(grid[r][c] for c in kept_cols) for r in kept_rows)


_OPERATORS: dict[str, tuple[Any, int]] = {
    "macro_argmax_fill": (_macro_argmax_fill, 8),
    "macro_row_template": (_macro_row_template, 13),
    "macro_marker_template": (_macro_marker_template, 11),
    "macro_halo": (_macro_halo, 12),
    "macro_complete_quartets": (_macro_complete_quartets, 12),
    "macro_complete_from_template": (_macro_complete_from_template, 11),
    "macro_sort_by_internal_position": (_macro_sort_by_internal_position, 12),
    "macro_sort_by_ink_count": (_macro_sort_by_ink_count, 10),
    "sequence_translate": (_sequence_translate, 9),
    "sequence_rectangle_growth": (_sequence_rectangle_growth, 10),
    "sequence_progression": (_sequence_progression, 11),
    "sequence_cumulative_frontier": (_sequence_cumulative_frontier, 11),
    "bordered_panel_extrapolate": (_bordered_panel_extrapolate, 12),
    "guided_transport": (_guided_transport, 13),
    "split_arrow_transport": (_split_arrow_transport, 12),
    "self_kronecker": (_self_kronecker, 10),
    "mask_template_kronecker": (_mask_template_kronecker, 13),
}


def execute_program(
    program: Mapping[str, Any], value: Any, limits: Mapping[str, Any] | None = None
) -> list[list[int]]:
    """Execute a serialized program on one grid."""

    bounds = Limits.from_value(limits)
    grid = _grid(value, bounds)
    if not isinstance(program, Mapping) or program.get("schema") != SCHEMA:
        raise _Undefined("invalid program schema")
    operator = program.get("operator")
    if operator == "checker_expand":
        side = program.get("output_side")
        if isinstance(side, bool) or not isinstance(side, int) or not 3 <= side <= bounds.max_side:
            raise _Undefined("invalid output side")
        result = _checker_expand(grid, side)
    elif operator == "macro_connect_matching":
        connector = program.get("connector_color")
        if isinstance(connector, bool) or not isinstance(connector, int) or not 0 <= connector <= 9:
            raise _Undefined("invalid connector colour")
        result = _macro_connect_matching(grid, connector)
    elif operator == "macro_addressed_transport":
        marker = program.get("marker_color")
        if isinstance(marker, bool) or not isinstance(marker, int) or not 0 <= marker <= 9:
            raise _Undefined("invalid address marker")
        result = _macro_addressed_transport(grid, marker)
    elif operator == "object_extract":
        selector = program.get("selector")
        connectivity = program.get("connectivity")
        if not isinstance(selector, str) or connectivity not in (4, 8):
            raise _Undefined("invalid object selector")
        result = _object_extract(grid, selector, connectivity)
    elif operator == "remove_uniform_lines":
        role = program.get("color_role")
        if not isinstance(role, str):
            raise _Undefined("invalid line selector")
        result = _remove_uniform_lines(grid, role)
    else:
        entry = _OPERATORS.get(str(operator))
        if entry is None:
            raise _Undefined("unknown operator")
        result = entry[0](grid)
    checked = _grid(result, bounds)
    return _plain(checked)


def replay_program(program: Mapping[str, Any], grid: Any) -> dict[str, Any]:
    """Deterministic tournament replay hook with a contiguous stage trace."""

    source = _plain(_grid(grid, Limits()))
    output = execute_program(program, source)
    return {
        "output": output,
        "stages": [
            {
                "name": f"panel-template:{program.get('operator', 'unknown')}",
                "input": source,
                "output": output,
            }
        ],
    }


def _programs(train: Sequence[Pair]) -> list[dict[str, Any]]:
    programs = [
        {
            "schema": SCHEMA,
            "operator": name,
            "description_length": mdl,
        }
        for name, (_, mdl) in sorted(_OPERATORS.items())
    ]
    for connectivity in (4, 8):
        for selector in (
            "largest_area",
            "smallest_area",
            "largest_box",
            "smallest_box",
            "densest",
            "sparsest",
            "tallest",
            "shortest",
            "widest",
            "narrowest",
        ):
            programs.append(
                {
                    "schema": SCHEMA,
                    "operator": "object_extract",
                    "selector": selector,
                    "connectivity": connectivity,
                    "description_length": 8,
                }
            )
    for role in ("most_lines", "nonbackground"):
        programs.append(
            {
                "schema": SCHEMA,
                "operator": "remove_uniform_lines",
                "color_role": role,
                "description_length": 7,
            }
        )
    target_shapes = {_shape(target) for _, target in train}
    introduced_sets = []
    for source, target in train:
        introduced_sets.append(
            {cell for row in target for cell in row}
            - {cell for row in source for cell in row}
        )
    introduced = set.intersection(*introduced_sets) if introduced_sets else set()
    for connector in sorted(introduced):
        programs.append(
            {
                "schema": SCHEMA,
                "operator": "macro_connect_matching",
                "connector_color": connector,
                "description_length": 13,
            }
        )
    singleton_sets = []
    for source, _ in train:
        counts = Counter(cell for row in source for cell in row)
        singleton_sets.append({color for color, count in counts.items() if count == 1})
    common_singletons = set.intersection(*singleton_sets) if singleton_sets else set()
    for marker in sorted(common_singletons):
        programs.append(
            {
                "schema": SCHEMA,
                "operator": "macro_addressed_transport",
                "marker_color": marker,
                "description_length": 11,
            }
        )
    if len(target_shapes) == 1:
        oh, ow = next(iter(target_shapes))
        if oh == ow:
            programs.append(
                {
                    "schema": SCHEMA,
                    "operator": "checker_expand",
                    "output_side": oh,
                    "description_length": 10,
                }
            )
    unique = {_canonical(program): program for program in programs}
    return [unique[key] for key in sorted(unique)]


def compile_task(task: Any, limits: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    """Compile one unique, exact, bounded panel/template behaviour."""

    bounds = Limits.from_value(limits)
    try:
        train, tests = _read_task(task, bounds)
    except (_Undefined, KeyError, TypeError, ValueError):
        return []
    programs = _programs(train)
    if len(programs) > bounds.max_programs:
        return []
    signature = hashlib.sha256(_canonical(programs).encode("ascii")).hexdigest()
    if len(train) > 1:
        reverse = _programs(tuple(reversed(train)))
        if hashlib.sha256(_canonical(reverse).encode("ascii")).hexdigest() != signature:
            return []
    behaviours: dict[str, list[tuple[dict[str, Any], list[Grid], list[Grid]]]] = {}
    calls = 0
    for program in programs:
        if int(program["description_length"]) > bounds.max_mdl:
            continue
        try:
            replay: list[Grid] = []
            for source, target in train:
                calls += 1
                if calls > bounds.max_executor_calls:
                    return []
                actual = _grid(execute_program(program, source, bounds), bounds)
                if actual != target:
                    raise _Undefined("demonstration mismatch")
                replay.append(actual)
            predictions = []
            for source in tests:
                calls += 1
                if calls > bounds.max_executor_calls:
                    return []
                predictions.append(_grid(execute_program(program, source, bounds), bounds))
        except (
            _Undefined,
            KeyError,
            TypeError,
            ValueError,
            IndexError,
            ZeroDivisionError,
        ):
            continue
        key = _canonical([_plain(output) for output in predictions])
        behaviours.setdefault(key, []).append((program, replay, predictions))
    if len(behaviours) != 1:
        return []
    entries = next(iter(behaviours.values()))
    entries.sort(key=lambda entry: (int(entry[0]["description_length"]), _canonical(entry[0])))
    program, replay, predictions = entries[0]
    behavior_hash = hashlib.sha256(
        _canonical([_plain(output) for output in predictions]).encode("ascii")
    ).hexdigest()
    return [
        {
            "family": "panel_template_composer",
            "program": program,
            "train_outputs": [_plain(output) for output in replay],
            "test_outputs": [_plain(output) for output in predictions],
            "complexity": int(program["description_length"]),
            "evidence": {
                "all_demonstrations_exact": True,
                "demonstration_count": len(train),
                "test_count": len(tests),
                "complete_behavior_quotient": True,
                "unique_test_behavior": True,
                "demo_order_invariance_checked": len(train) > 1,
                "enumeration_signature": signature,
                "corroborating_programs": len(entries),
                "corroborating_operators": sorted(
                    {str(entry[0]["operator"]) for entry in entries}
                ),
                "enumerated_programs": len(programs),
                "executor_calls": calls,
                "behavior_hash": behavior_hash,
                "bounded_search": True,
                "task_identity_free": True,
                "test_outputs_observed": False,
            },
        }
    ] if bounds.max_candidates else []


__all__ = ["Limits", "SCHEMA", "compile_task", "execute_program", "replay_program"]
