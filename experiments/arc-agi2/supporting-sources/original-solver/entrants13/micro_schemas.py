"""Small, strongly typed schema entrant for PR-LASM Block 13.

The families here are intentionally narrow but semantic: constraint completion,
ray dynamics, row serialization, endpoint interpolation, and learned panel
glyphs.  Every proposal must replay all demonstrations exactly.
"""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from typing import Any, Callable, Mapping, Sequence


Grid = tuple[tuple[int, ...], ...]
Rule = Callable[[Grid], Grid | None]


def _grid(value: Any) -> Grid:
    if not isinstance(value, list) or not 1 <= len(value) <= 30:
        raise ValueError("invalid grid")
    if not all(isinstance(row, list) and row for row in value):
        raise ValueError("invalid row")
    width = len(value[0])
    if not 1 <= width <= 30 or any(len(row) != width for row in value):
        raise ValueError("non-rectangular grid")
    result: list[tuple[int, ...]] = []
    for row in value:
        if any(isinstance(cell, bool) or not isinstance(cell, int) or not 0 <= cell <= 9 for cell in row):
            raise ValueError("invalid cell")
        result.append(tuple(row))
    return tuple(result)


def _plain(grid: Grid) -> list[list[int]]:
    return [list(row) for row in grid]


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _mode(grid: Grid) -> int:
    counts = Counter(cell for row in grid for cell in row)
    return min(counts, key=lambda color: (-counts[color], color))


def _candidate(
    family: str,
    program: dict[str, Any],
    complexity: int,
    rule: Rule,
    train: Sequence[tuple[Grid, Grid]],
    tests: Sequence[Grid],
) -> dict[str, Any] | None:
    replay: list[Grid] = []
    for source, target in train:
        result = rule(source)
        if result is None or result != target:
            return None
        replay.append(result)
    predictions: list[Grid] = []
    for source in tests:
        result = rule(source)
        if result is None:
            return None
        predictions.append(result)
    behavior = hashlib.sha256(
        _canonical([_plain(grid) for grid in predictions]).encode("utf-8")
    ).hexdigest()
    return {
        "family": family,
        "program": program,
        "train_outputs": [_plain(grid) for grid in replay],
        "test_outputs": [_plain(grid) for grid in predictions],
        "complexity": complexity,
        "evidence": {
            "all_demonstrations_exact": True,
            "demonstration_permutation_invariant": True,
            "behavior_hash": behavior,
        },
    }


def _latin_rule(train: Sequence[tuple[Grid, Grid]]) -> tuple[Rule, dict[str, Any]] | None:
    sizes = {len(source) for source, _ in train}
    if len(sizes) != 1:
        return None
    size = next(iter(sizes))
    if size < 3 or any(len(row) != size for pair in train for grid in pair for row in grid):
        return None
    symbol_sets = {
        tuple(sorted({cell for row in target for cell in row})) for _, target in train
    }
    if len(symbol_sets) != 1:
        return None
    symbols = next(iter(symbol_sets))
    if len(symbols) != size:
        return None
    backgrounds: list[int] = []
    for source, target in train:
        if any(set(row) != set(symbols) for row in target):
            return None
        if any({target[row][column] for row in range(size)} != set(symbols) for column in range(size)):
            return None
        differing = [source[r][c] for r in range(size) for c in range(size) if source[r][c] != target[r][c]]
        if not differing or len(set(differing)) != 1:
            return None
        background = differing[0]
        if any(source[r][c] != background and source[r][c] != target[r][c] for r in range(size) for c in range(size)):
            return None
        backgrounds.append(background)
    if len(set(backgrounds)) != 1:
        return None
    background = backgrounds[0]

    def solve(source: Grid) -> Grid | None:
        if len(source) != size or any(len(row) != size for row in source):
            return None
        if any(cell != background and cell not in symbols for row in source for cell in row):
            return None
        board = [list(row) for row in source]
        solutions: list[Grid] = []

        def search() -> None:
            if len(solutions) > 1:
                return
            best: tuple[int, int, list[int]] | None = None
            for r in range(size):
                for c in range(size):
                    if board[r][c] != background:
                        continue
                    allowed = [
                        value
                        for value in symbols
                        if value not in board[r]
                        and all(board[rr][c] != value for rr in range(size))
                    ]
                    if not allowed:
                        return
                    if best is None or len(allowed) < len(best[2]):
                        best = (r, c, allowed)
            if best is None:
                solutions.append(tuple(tuple(row) for row in board))
                return
            r, c, allowed = best
            for value in allowed:
                board[r][c] = value
                search()
                board[r][c] = background

        search()
        return solutions[0] if len(solutions) == 1 else None

    return solve, {"operator": "unique_latin_completion", "background": background, "symbols": list(symbols)}


def _bounce(index: int, width: int) -> int:
    if width == 1:
        return 0
    period = 2 * (width - 1)
    phase = index % period
    return phase if phase < width else period - phase


def _diagonal_bounce_rules(train: Sequence[tuple[Grid, Grid]]) -> list[tuple[Rule, dict[str, Any]]]:
    marker_sets: list[tuple[int, int]] = []
    for source, target in train:
        if len(source) != len(target) or len(source[0]) != len(target[0]):
            return []
        bg = _mode(source)
        non_bg = [(r, c, source[r][c]) for r, row in enumerate(source) for c, value in enumerate(row) if value != bg]
        if len(non_bg) != 1:
            return []
        marker_sets.append((non_bg[0][2], bg))
    if len(set(marker_sets)) != 1:
        return []
    marker, background = marker_sets[0]
    fill_sets = [
        sorted({cell for row in target for cell in row} - {marker}) for _, target in train
    ]
    if not fill_sets or any(len(values) != 1 for values in fill_sets):
        return []
    if len({values[0] for values in fill_sets}) != 1:
        return []
    fill = fill_sets[0][0]
    output: list[tuple[Rule, dict[str, Any]]] = []
    for direction in (-1, 1):
        def apply(source: Grid, direction: int = direction) -> Grid | None:
            bg = _mode(source)
            seeds = [(r, c, source[r][c]) for r, row in enumerate(source) for c, value in enumerate(row) if value != bg]
            if bg != background or len(seeds) != 1 or seeds[0][2] != marker:
                return None
            sr, sc, _ = seeds[0]
            width = len(source[0])
            result = [[fill for _ in range(width)] for _ in source]
            for row in range(len(source)):
                column = _bounce(sc + direction * (sr - row), width)
                result[row][column] = marker
            return tuple(tuple(row) for row in result)

        output.append((apply, {"operator": "diagonal_bounce_fill", "marker": marker, "fill": fill, "direction": direction}))
    return output


def _prefix_repeat_rule(train: Sequence[tuple[Grid, Grid]]) -> tuple[Rule, dict[str, Any]] | None:
    backgrounds: list[int] = []
    for source, target in train:
        if len(source) != len(target) or len(source[0]) != len(target[0]):
            return None
        backgrounds.append(_mode(source))
    if len(set(backgrounds)) != 1:
        return None
    background = backgrounds[0]

    def apply(source: Grid) -> Grid | None:
        if _mode(source) != background:
            return None
        output: list[tuple[int, ...]] = []
        width = len(source[0])
        for row in source:
            end = width
            while end and row[end - 1] == background:
                end -= 1
            if end == 0 or end * 2 > width:
                return None
            prefix = row[:end]
            fill = prefix[-1]
            built = list(prefix) + [fill] * (width - end)
            built[width - end :] = prefix
            output.append(tuple(built))
        return tuple(output)

    return apply, {"operator": "row_prefix_repeat_at_far_edge", "background": background}


def _endpoint_rule(train: Sequence[tuple[Grid, Grid]]) -> tuple[Rule, dict[str, Any]] | None:
    middle_colors: list[int] = []
    backgrounds: list[int] = []
    for source, target in train:
        if len(source) != len(target) or len(source[0]) != len(target[0]):
            return None
        bg = _mode(source)
        backgrounds.append(bg)
        found = False
        for before, after in zip(source, target):
            points = [(i, value) for i, value in enumerate(before) if value != bg]
            if not points:
                if before != after:
                    return None
                continue
            if len(points) != 2 or points[0][0] >= points[1][0]:
                return None
            left, right = points
            if (right[0] - left[0]) % 2:
                return None
            mid = (left[0] + right[0]) // 2
            middle_colors.append(after[mid])
            found = True
        if not found:
            return None
    if len(set(backgrounds)) != 1 or not middle_colors or len(set(middle_colors)) != 1:
        return None
    background, middle = backgrounds[0], middle_colors[0]

    def apply(source: Grid) -> Grid | None:
        if _mode(source) != background:
            return None
        output = [list(row) for row in source]
        for r, row in enumerate(source):
            points = [(i, value) for i, value in enumerate(row) if value != background]
            if not points:
                continue
            if len(points) != 2 or (points[1][0] - points[0][0]) % 2:
                return None
            (left, lc), (right, rc) = points
            mid = (left + right) // 2
            for column in range(left, right + 1):
                output[r][column] = lc if column < mid else middle if column == mid else rc
        return tuple(tuple(row) for row in output)

    return apply, {"operator": "connect_row_endpoints_with_midpoint", "background": background, "midpoint_color": middle}


def _panel_dictionary_rules(train: Sequence[tuple[Grid, Grid]]) -> list[tuple[Rule, dict[str, Any]]]:
    rules: list[tuple[Rule, dict[str, Any]]] = []
    for axis in ("horizontal", "vertical"):
        mapping: dict[Grid, int] = {}
        panel_size: int | None = None
        valid = True
        for source, target in train:
            height, width = len(source), len(source[0])
            if (height, width) != (len(target), len(target[0])):
                valid = False
                break
            size = height if axis == "horizontal" else width
            length = width if axis == "horizontal" else height
            if size < 2 or length % size or length == size:
                valid = False
                break
            if panel_size not in (None, size):
                valid = False
                break
            panel_size = size
            count = length // size
            for index in range(count):
                if axis == "horizontal":
                    inp = tuple(tuple(row[index * size : (index + 1) * size]) for row in source)
                    out = tuple(tuple(row[index * size : (index + 1) * size]) for row in target)
                else:
                    inp = tuple(source[index * size : (index + 1) * size])
                    out = tuple(target[index * size : (index + 1) * size])
                values = {cell for row in out for cell in row}
                if len(values) != 1:
                    valid = False
                    break
                color = next(iter(values))
                if inp in mapping and mapping[inp] != color:
                    valid = False
                    break
                mapping[inp] = color
            if not valid:
                break
        if not valid or panel_size is None or len(mapping) < 2:
            continue

        def apply(source: Grid, axis: str = axis, size: int = panel_size, mapping: dict[Grid, int] = dict(mapping)) -> Grid | None:
            height, width = len(source), len(source[0])
            length = width if axis == "horizontal" else height
            if (height if axis == "horizontal" else width) != size or length % size:
                return None
            output = [[0 for _ in range(width)] for _ in range(height)]
            for index in range(length // size):
                if axis == "horizontal":
                    panel = tuple(tuple(row[index * size : (index + 1) * size]) for row in source)
                else:
                    panel = tuple(source[index * size : (index + 1) * size])
                if panel not in mapping:
                    return None
                color = mapping[panel]
                if axis == "horizontal":
                    for r in range(height):
                        for c in range(index * size, (index + 1) * size):
                            output[r][c] = color
                else:
                    for r in range(index * size, (index + 1) * size):
                        for c in range(width):
                            output[r][c] = color
            return tuple(tuple(row) for row in output)

        serial = [
            {"glyph": _plain(glyph), "color": color}
            for glyph, color in sorted(mapping.items(), key=lambda item: _canonical(item[0]))
        ]
        rules.append((apply, {"operator": "learned_panel_glyph_dictionary", "axis": axis, "panel_size": panel_size, "entries": serial}))
    return rules


def _top_seed_checker_rule(train: Sequence[tuple[Grid, Grid]]) -> tuple[Rule, dict[str, Any]] | None:
    backgrounds: list[int] = []
    for source, target in train:
        if len(source) != len(target) or len(source[0]) != len(target[0]):
            return None
        background = _mode(source)
        backgrounds.append(background)
        if any(cell != background for row in source[1:] for cell in row):
            return None
        if not any(cell != background for cell in source[0]):
            return None
    if len(set(backgrounds)) != 1:
        return None
    background = backgrounds[0]

    def apply(source: Grid) -> Grid | None:
        if _mode(source) != background or any(cell != background for row in source[1:] for cell in row):
            return None
        seeds = [(column, color) for column, color in enumerate(source[0]) if color != background]
        if not seeds:
            return None
        height, width = len(source), len(source[0])
        output = [[background for _ in range(width)] for _ in range(height)]
        for row in range(height):
            offsets = (0,) if row % 2 == 0 else (-1, 1)
            for column, color in seeds:
                for offset in offsets:
                    target_column = column + offset
                    if 0 <= target_column < width:
                        if output[row][target_column] not in (background, color):
                            return None
                        output[row][target_column] = color
        return tuple(tuple(row) for row in output)

    return apply, {"operator": "top_seed_downward_checker_cones", "background": background}


def _bottom_right_l_rule(train: Sequence[tuple[Grid, Grid]]) -> tuple[Rule, dict[str, Any]] | None:
    backgrounds = [_mode(source) for source, _ in train]
    if len(set(backgrounds)) != 1:
        return None
    background = backgrounds[0]

    def apply(source: Grid) -> Grid | None:
        if _mode(source) != background:
            return None
        points = [(r, c, value) for r, row in enumerate(source) for c, value in enumerate(row) if value != background]
        if not points:
            return None
        # The schema is defined for isolated signal cells; adjacent signal
        # pixels would instead constitute an object transformation.
        occupied = {(r, c) for r, c, _ in points}
        if any(
            (r + dr, c + dc) in occupied
            for r, c, _ in points
            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1))
        ):
            return None
        height, width = len(source), len(source[0])
        output = [list(row) for row in source]
        for row, column, color in sorted(points):
            for c in range(column, width):
                output[row][c] = color
            for r in range(row, height):
                output[r][width - 1] = color
        return tuple(tuple(row) for row in output)

    return apply, {"operator": "isolated_signals_to_bottom_right_l_rays", "background": background}


def _suffix_vertical_tile_rule(train: Sequence[tuple[Grid, Grid]]) -> tuple[Rule, dict[str, Any]] | None:
    def apply(source: Grid) -> Grid | None:
        background = _mode(source)
        active = [row for row, values in enumerate(source) if any(cell != background for cell in values)]
        if not active:
            return None
        first = min(active)
        if active != list(range(first, len(source))):
            return None
        motif = source[first:]
        if len(motif) >= len(source):
            return None
        height = len(source)
        offset = (-height) % len(motif)
        return tuple(motif[(offset + row) % len(motif)] for row in range(height))

    return apply, {"operator": "tile_active_row_suffix_upward", "background": "modal", "phase": "bottom_aligned"}


def _bar_triangles_rule(train: Sequence[tuple[Grid, Grid]]) -> tuple[Rule, dict[str, Any]] | None:
    records: list[tuple[int, int, int, int]] = []
    # (background, bar, upper, lower)
    for source, target in train:
        if len(source) != len(target) or len(source[0]) != len(target[0]):
            return None
        background = _mode(source)
        cells = [(r, c, value) for r, row in enumerate(source) for c, value in enumerate(row) if value != background]
        if not cells or len({r for r, _, _ in cells}) != 1 or len({v for _, _, v in cells}) != 1:
            return None
        row = cells[0][0]
        columns = sorted(c for _, c, _ in cells)
        if columns != list(range(columns[0], columns[-1] + 1)):
            return None
        bar = cells[0][2]
        upper_values = {target[r][c] for r in range(row) for c in range(len(source[0])) if target[r][c] != background}
        lower_values = {target[r][c] for r in range(row + 1, len(source)) for c in range(len(source[0])) if target[r][c] != background}
        if len(upper_values) != 1 or len(lower_values) != 1:
            return None
        records.append((background, bar, next(iter(upper_values)), next(iter(lower_values))))
    if len(set(records)) != 1:
        return None
    background, bar, upper, lower = records[0]

    def apply(source: Grid) -> Grid | None:
        if _mode(source) != background:
            return None
        cells = [(r, c, value) for r, row in enumerate(source) for c, value in enumerate(row) if value != background]
        if not cells or len({r for r, _, _ in cells}) != 1 or {v for _, _, v in cells} != {bar}:
            return None
        row = cells[0][0]
        columns = sorted(c for _, c, _ in cells)
        if columns != list(range(columns[0], columns[-1] + 1)):
            return None
        left, right = columns[0], columns[-1]
        height, width = len(source), len(source[0])
        result = [[background for _ in range(width)] for _ in range(height)]
        for c in columns:
            result[row][c] = bar
        for r in range(row - 1, -1, -1):
            reach = row - r
            for c in range(left, min(width - 1, right + reach) + 1):
                result[r][c] = upper
        for r in range(row + 1, height):
            shrink = r - row
            if right - shrink < left:
                continue
            for c in range(left, right - shrink + 1):
                result[r][c] = lower
        return tuple(tuple(values) for values in result)

    return apply, {"operator": "horizontal_bar_opposed_triangles", "background": background, "bar": bar, "upper": upper, "lower": lower}


def _components(grid: Grid, background: int) -> list[list[tuple[int, int]]]:
    unseen = {(r, c) for r, row in enumerate(grid) for c, value in enumerate(row) if value != background}
    output: list[list[tuple[int, int]]] = []
    while unseen:
        seed = min(unseen)
        unseen.remove(seed)
        stack = [seed]
        component = [seed]
        while stack:
            r, c = stack.pop()
            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                neighbor = (r + dr, c + dc)
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    stack.append(neighbor)
                    component.append(neighbor)
        output.append(sorted(component))
    return output


def _ranked_rectangle_rule(train: Sequence[tuple[Grid, Grid]]) -> tuple[Rule, dict[str, Any]] | None:
    rank_colors: dict[int, int] = {}
    foregrounds: list[int] = []
    backgrounds: list[int] = []
    for source, target in train:
        if len(source) != len(target) or len(source[0]) != len(target[0]):
            return None
        background = _mode(source)
        backgrounds.append(background)
        foreground = {cell for row in source for cell in row if cell != background}
        if len(foreground) != 1:
            return None
        foregrounds.append(next(iter(foreground)))
        components = _components(source, background)
        if len(components) < 2:
            return None
        boxes: list[tuple[int, int, int, int, int]] = []
        for component in components:
            rs = [r for r, _ in component]
            cs = [c for _, c in component]
            r0, r1, c0, c1 = min(rs), max(rs), min(cs), max(cs)
            if r1 - r0 < 2 or c1 - c0 < 2:
                return None
            rectangle = {(r, c) for r in range(r0, r1 + 1) for c in range(c0, c1 + 1)}
            if set(component) != rectangle:
                return None
            boxes.append(((r1 - r0 + 1) * (c1 - c0 + 1), r0, r1, c0, c1))
        if len({box[0] for box in boxes}) != len(boxes):
            return None
        for rank, (_, r0, r1, c0, c1) in enumerate(sorted(boxes)):
            colors = {target[r][c] for r in range(r0 + 1, r1) for c in range(c0 + 1, c1)}
            if len(colors) != 1:
                return None
            color = next(iter(colors))
            if rank in rank_colors and rank_colors[rank] != color:
                return None
            rank_colors[rank] = color
            if any(target[r][c] != source[r][c] for r in (r0, r1) for c in range(c0, c1 + 1)):
                return None
            if any(target[r][c] != source[r][c] for c in (c0, c1) for r in range(r0, r1 + 1)):
                return None
    if len(set(foregrounds)) != 1 or len(set(backgrounds)) != 1 or not rank_colors:
        return None
    foreground = foregrounds[0]
    background = backgrounds[0]

    def apply(source: Grid) -> Grid | None:
        if {cell for row in source for cell in row if cell != background} != {foreground}:
            return None
        boxes: list[tuple[int, int, int, int, int]] = []
        for component in _components(source, background):
            rs, cs = [r for r, _ in component], [c for _, c in component]
            r0, r1, c0, c1 = min(rs), max(rs), min(cs), max(cs)
            if r1 - r0 < 2 or c1 - c0 < 2 or len(component) != (r1 - r0 + 1) * (c1 - c0 + 1):
                return None
            boxes.append(((r1 - r0 + 1) * (c1 - c0 + 1), r0, r1, c0, c1))
        if len(boxes) != len(rank_colors) or len({box[0] for box in boxes}) != len(boxes):
            return None
        result = [list(row) for row in source]
        for rank, (_, r0, r1, c0, c1) in enumerate(sorted(boxes)):
            if rank not in rank_colors:
                return None
            for r in range(r0 + 1, r1):
                for c in range(c0 + 1, c1):
                    result[r][c] = rank_colors[rank]
        return tuple(tuple(row) for row in result)

    return apply, {"operator": "solid_rectangle_interior_by_area_rank", "background": background, "foreground": foreground, "rank_colors": rank_colors}


def _row_keyed_carrier_rule(train: Sequence[tuple[Grid, Grid]]) -> tuple[Rule, dict[str, Any]] | None:
    changed_sources: set[int] = set()
    for source, target in train:
        if len(source) != len(target) or len(source[0]) != len(target[0]):
            return None
        changed_sources.update(
            source[r][c]
            for r in range(len(source))
            for c in range(len(source[0]))
            if source[r][c] != target[r][c]
        )
    if len(changed_sources) != 1:
        return None
    carrier = next(iter(changed_sources))

    def apply(source: Grid) -> Grid | None:
        background = _mode(source)
        result = [list(row) for row in source]
        changed = False
        for r, row in enumerate(source):
            if carrier not in row:
                continue
            keys = {value for value in row if value not in (background, carrier)}
            if len(keys) != 1:
                return None
            key = next(iter(keys))
            for c, value in enumerate(row):
                if value == carrier:
                    result[r][c] = key
                    changed = True
        return tuple(tuple(row) for row in result) if changed else None

    return apply, {"operator": "recolor_row_carrier_from_unique_key", "carrier": carrier, "background": "modal"}


def _boundary_cartesian_rule(train: Sequence[tuple[Grid, Grid]]) -> tuple[Rule, dict[str, Any]] | None:
    def apply(source: Grid) -> Grid | None:
        height, width = len(source), len(source[0])
        if height < 3 or width < 3:
            return None
        background = _mode(source)
        bottom = source[-1]
        right = tuple(row[-1] for row in source)
        if not any(value != background for value in bottom) or not any(value != background for value in right):
            return None
        result = [list(row) for row in source]
        changed = False
        for r in range(height - 1):
            for c in range(width - 1):
                if right[r] == bottom[c] and right[r] != background:
                    if result[r][c] == background:
                        result[r][c] = right[r]
                        changed = True
        return tuple(tuple(row) for row in result) if changed else None

    return apply, {"operator": "matching_boundary_keys_cartesian_product", "axes": ["right", "bottom"]}


def _corner_rectangle_rule(train: Sequence[tuple[Grid, Grid]]) -> tuple[Rule, dict[str, Any]] | None:
    changed_targets: set[int] = set()
    marker_colors: set[int] = set()
    for source, target in train:
        if len(source) != len(target) or len(source[0]) != len(target[0]):
            return None
        changed_targets.update(
            target[r][c] for r in range(len(source)) for c in range(len(source[0])) if source[r][c] != target[r][c]
        )
        marker_colors.update(cell for row in source for cell in row if cell != _mode(source))
    if len(changed_targets) != 1 or len(marker_colors) != 1:
        return None
    fill, marker = next(iter(changed_targets)), next(iter(marker_colors))

    def apply(source: Grid) -> Grid | None:
        background = _mode(source)
        points = {(r, c) for r, row in enumerate(source) for c, value in enumerate(row) if value == marker}
        if len(points) < 4:
            return None
        by_row: dict[int, tuple[int, ...]] = {}
        for r in sorted({r for r, _ in points}):
            cols = tuple(sorted(c for rr, c in points if rr == r))
            if len(cols) == 2:
                by_row[r] = cols
        groups: list[tuple[int, int, int, int]] = []
        used: set[tuple[int, int]] = set()
        for top in sorted(by_row):
            for bottom in sorted(row for row in by_row if row > top):
                if by_row[top] == by_row[bottom]:
                    left, right = by_row[top]
                    if bottom - top >= 2 and right - left >= 2:
                        corners = {(top, left), (top, right), (bottom, left), (bottom, right)}
                        if not corners & used:
                            groups.append((top, bottom, left, right))
                            used.update(corners)
                            break
        if used != points or not groups:
            return None
        result = [list(row) for row in source]
        for top, bottom, left, right in groups:
            for r in range(top + 1, bottom):
                for c in range(left + 1, right):
                    if result[r][c] != background:
                        return None
                    result[r][c] = fill
        return tuple(tuple(row) for row in result)

    return apply, {"operator": "fill_interiors_of_four_marker_rectangles", "marker": marker, "fill": fill}


def _quadrant_carrier_rule(train: Sequence[tuple[Grid, Grid]]) -> tuple[Rule, dict[str, Any]] | None:
    changed_sources: set[int] = set()
    backgrounds: list[int] = []
    for source, target in train:
        if len(source) != len(target) or len(source[0]) != len(target[0]):
            return None
        backgrounds.append(_mode(source))
        changed_sources.update(
            source[r][c] for r in range(len(source)) for c in range(len(source[0])) if source[r][c] != target[r][c] and source[r][c] != _mode(source)
        )
    # Changed non-background cells include the carrier and erased corner keys;
    # the carrier is the only one occurring in solid rectangles of area >= 4.
    frequency = Counter(cell for source, _ in train for row in source for cell in row if cell != _mode(source))
    if not frequency:
        return None
    carrier = max(frequency, key=lambda color: (frequency[color], -color))

    def rectangles(source: Grid, background: int) -> list[tuple[int, int, int, int]]:
        cells = {(r, c) for r, row in enumerate(source) for c, value in enumerate(row) if value == carrier}
        output: list[tuple[int, int, int, int]] = []
        while cells:
            seed = min(cells)
            stack = [seed]
            component = {seed}
            cells.remove(seed)
            while stack:
                r, c = stack.pop()
                for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    q = (r + dr, c + dc)
                    if q in cells:
                        cells.remove(q); component.add(q); stack.append(q)
            rs, cs = [r for r, _ in component], [c for _, c in component]
            box = (min(rs), max(rs), min(cs), max(cs))
            if len(component) != (box[1] - box[0] + 1) * (box[3] - box[2] + 1):
                return []
            output.append(box)
        return sorted(output)

    def apply(source: Grid) -> Grid | None:
        background = _mode(source)
        result = [list(row) for row in source]
        boxes = rectangles(source, background)
        if not boxes:
            return None
        used_keys: set[tuple[int, int]] = set()
        for top, bottom, left, right in boxes:
            height, width = bottom - top + 1, right - left + 1
            if height % 2 or width % 2:
                return None
            key_positions = ((top - 1, left - 1), (top - 1, right + 1), (bottom + 1, left - 1), (bottom + 1, right + 1))
            if any(not (0 <= r < len(source) and 0 <= c < len(source[0])) for r, c in key_positions):
                return None
            colors = [source[r][c] for r, c in key_positions]
            if any(color in (background, carrier) for color in colors):
                return None
            for r, c in key_positions:
                result[r][c] = background
                used_keys.add((r, c))
            for r in range(top, bottom + 1):
                for c in range(left, right + 1):
                    quadrant = (0 if r < top + height // 2 else 2) + (0 if c < left + width // 2 else 1)
                    result[r][c] = colors[quadrant]
        non_carrier_keys = {(r, c) for r, row in enumerate(source) for c, value in enumerate(row) if value not in (background, carrier)}
        if non_carrier_keys != used_keys:
            return None
        return tuple(tuple(row) for row in result)

    return apply, {"operator": "fill_even_carrier_from_four_diagonal_keys", "carrier": carrier, "background": "modal"}


def _horizontal_gap_bridge_rule(train: Sequence[tuple[Grid, Grid]]) -> tuple[Rule, dict[str, Any]] | None:
    source_colors: set[int] = set()
    fill_colors: set[int] = set()
    changed_backgrounds: set[int] = set()
    for source, target in train:
        if len(source) != len(target) or len(source[0]) != len(target[0]):
            return None
        for r in range(len(source)):
            for c in range(len(source[0])):
                if source[r][c] != target[r][c]:
                    changed_backgrounds.add(source[r][c])
                    fill_colors.add(target[r][c])
    if len(changed_backgrounds) != 1 or len(fill_colors) != 1:
        return None
    background = next(iter(changed_backgrounds))
    for source, _ in train:
        source_colors.update(cell for row in source for cell in row if cell != background)
    if len(source_colors) != 1:
        return None
    source_color, fill = next(iter(source_colors)), next(iter(fill_colors))

    def apply(source: Grid) -> Grid | None:
        if {cell for row in source for cell in row if cell != background} != {source_color}:
            return None
        result = [list(row) for row in source]
        changed = False
        for r, row in enumerate(source):
            runs: list[tuple[int, int]] = []
            c = 0
            while c < len(row):
                if row[c] != source_color:
                    c += 1; continue
                start = c
                while c + 1 < len(row) and row[c + 1] == source_color:
                    c += 1
                runs.append((start, c)); c += 1
            for (_, end), (start, _) in zip(runs, runs[1:]):
                if start > end + 1:
                    for c in range(end + 1, start):
                        result[r][c] = fill
                        changed = True
        return tuple(tuple(row) for row in result) if changed else None

    return apply, {"operator": "bridge_horizontal_same_color_runs", "background": background, "source": source_color, "fill": fill}


def _rectangle_bridge_rule(train: Sequence[tuple[Grid, Grid]]) -> tuple[Rule, dict[str, Any]] | None:
    fill_colors: set[int] = set()
    for source, target in train:
        background = _mode(source)
        fill_colors.update(target[r][c] for r in range(len(source)) for c in range(len(source[0])) if source[r][c] != target[r][c] and source[r][c] == background)
    if len(fill_colors) != 1:
        return None
    fill = next(iter(fill_colors))

    def apply(source: Grid) -> Grid | None:
        background = _mode(source)
        components = _components(source, background)
        if len(components) != 2:
            return None
        boxes: list[tuple[int, int, int, int]] = []
        colors: list[int] = []
        for component in components:
            rs, cs = [r for r, _ in component], [c for _, c in component]
            box = (min(rs), max(rs), min(cs), max(cs))
            if len(component) != (box[1] - box[0] + 1) * (box[3] - box[2] + 1):
                return None
            values = {source[r][c] for r, c in component}
            if len(values) != 1:
                return None
            boxes.append(box); colors.append(next(iter(values)))
        if colors[0] == colors[1]:
            return None
        a, b = boxes
        result = [list(row) for row in source]
        painted = False
        if a[3] < b[2] or b[3] < a[2]:
            left, right = (a, b) if a[3] < b[2] else (b, a)
            r0, r1 = max(left[0], right[0]) + 1, min(left[1], right[1]) - 1
            for r in range(r0, r1 + 1):
                for c in range(left[3] + 1, right[2]):
                    result[r][c] = fill; painted = True
        elif a[1] < b[0] or b[1] < a[0]:
            top, bottom = (a, b) if a[1] < b[0] else (b, a)
            c0, c1 = max(top[2], bottom[2]) + 1, min(top[3], bottom[3]) - 1
            for r in range(top[1] + 1, bottom[0]):
                for c in range(c0, c1 + 1):
                    result[r][c] = fill; painted = True
        return tuple(tuple(row) for row in result) if painted else None

    return apply, {"operator": "bridge_separated_solid_rectangles_through_strict_overlap", "fill": fill}


def _paired_points_rectangle_rule(train: Sequence[tuple[Grid, Grid]]) -> tuple[Rule, dict[str, Any]] | None:
    def apply(source: Grid) -> Grid | None:
        background = _mode(source)
        by_color: dict[int, list[tuple[int, int]]] = {}
        for r, row in enumerate(source):
            for c, value in enumerate(row):
                if value != background:
                    by_color.setdefault(value, []).append((r, c))
        if not by_color or any(len(points) != 2 for points in by_color.values()):
            return None
        result = [list(row) for row in source]
        changed = False
        for color, points in sorted(by_color.items()):
            (r0, c0), (r1, c1) = points
            if r0 == r1 or c0 == c1:
                return None
            for r in range(min(r0, r1), max(r0, r1) + 1):
                for c in range(min(c0, c1), max(c0, c1) + 1):
                    if result[r][c] == background:
                        result[r][c] = color
                        changed = True
        return tuple(tuple(row) for row in result) if changed else None

    return apply, {"operator": "fill_bounding_rectangles_of_color_pairs", "background": "modal"}


def _component_size_color_rule(train: Sequence[tuple[Grid, Grid]]) -> tuple[Rule, dict[str, Any]] | None:
    mapping: dict[int, int] = {}
    carriers: set[int] = set()
    backgrounds: set[int] = set()
    for source, target in train:
        background = _mode(source)
        backgrounds.add(background)
        colors = {cell for row in source for cell in row if cell != background}
        if len(colors) != 1:
            return None
        carrier = next(iter(colors)); carriers.add(carrier)
        for component in _components(source, background):
            output_colors = {target[r][c] for r, c in component}
            if len(output_colors) != 1:
                return None
            out = next(iter(output_colors))
            size = len(component)
            if size in mapping and mapping[size] != out:
                return None
            mapping[size] = out
        if any(source[r][c] == background and target[r][c] != background for r in range(len(source)) for c in range(len(source[0]))):
            return None
    if len(carriers) != 1 or len(backgrounds) != 1 or len(mapping) < 2 or len(set(mapping.values())) < 2:
        return None
    carrier, background = next(iter(carriers)), next(iter(backgrounds))
    color_support = Counter(mapping.values())
    default_color = min(color_support, key=lambda color: (-color_support[color], color))
    if color_support[default_color] < 2:
        return None
    exceptions = {size: color for size, color in mapping.items() if color != default_color}

    def apply(source: Grid) -> Grid | None:
        if {cell for row in source for cell in row if cell != background} != {carrier}:
            return None
        result = [list(row) for row in source]
        for component in _components(source, background):
            color = exceptions.get(len(component), default_color)
            for r, c in component:
                result[r][c] = color
        return tuple(tuple(row) for row in result)

    return apply, {"operator": "recolor_components_by_cardinality_exceptions", "background": background, "carrier": carrier, "default_color": default_color, "size_exceptions": exceptions, "observed_size_colors": mapping}


def _legend_column_recolor_rule(train: Sequence[tuple[Grid, Grid]]) -> tuple[Rule, dict[str, Any]] | None:
    carriers: set[int] = set()
    backgrounds: set[int] = set()
    for source, target in train:
        background = _mode(source); backgrounds.add(background)
        changed_source = {source[r][c] for r in range(len(source)) for c in range(len(source[0])) if source[r][c] != target[r][c]}
        if len(changed_source) != 1:
            return None
        carriers.update(changed_source)
    if len(carriers) != 1 or len(backgrounds) != 1:
        return None
    carrier, background = next(iter(carriers)), next(iter(backgrounds))

    def apply(source: Grid) -> Grid | None:
        markers = [(r, c, value) for r, row in enumerate(source) for c, value in enumerate(row) if value not in (background, carrier)]
        if len(markers) < 2 or len({r for r, _, _ in markers}) != 1:
            return None
        marker_row = markers[0][0]
        carrier_cells = {(r, c) for r, row in enumerate(source) for c, value in enumerate(row) if value == carrier}
        if any(r <= marker_row for r, _ in carrier_cells):
            return None
        result = [list(row) for row in source]
        components = _components(tuple(tuple(carrier if (r, c) in carrier_cells else background for c in range(len(source[0]))) for r in range(len(source))), background)
        for component in components:
            center = sum(c for _, c in component) / len(component)
            distances = sorted((abs(c - center), c, color) for _, c, color in markers)
            if len(distances) > 1 and distances[0][0] == distances[1][0]:
                return None
            color = distances[0][2]
            for r, c in component:
                result[r][c] = color
        return tuple(tuple(row) for row in result)

    return apply, {"operator": "recolor_carrier_components_by_nearest_legend_column", "background": background, "carrier": carrier}


def compile_task(task: Mapping[str, Any], limits: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    try:
        train = [(_grid(example["input"]), _grid(example["output"])) for example in task["train"]]
        tests = [_grid(example["input"]) for example in task["test"]]
    except (KeyError, TypeError, ValueError):
        return []
    if not train or not tests:
        return []
    rule_specs: list[tuple[str, Rule, dict[str, Any], int]] = []
    latin = _latin_rule(train)
    if latin is not None:
        rule_specs.append(("constraint_completion", latin[0], latin[1], 8))
    for rule, program in _diagonal_bounce_rules(train):
        rule_specs.append(("ray_dynamics", rule, program, 7))
    prefix = _prefix_repeat_rule(train)
    if prefix is not None:
        rule_specs.append(("row_serialization", prefix[0], prefix[1], 5))
    endpoint = _endpoint_rule(train)
    if endpoint is not None:
        rule_specs.append(("endpoint_interpolation", endpoint[0], endpoint[1], 6))
    for rule, program in _panel_dictionary_rules(train):
        rule_specs.append(("panel_symbol_dictionary", rule, program, 10 + len(program["entries"])))
    checker = _top_seed_checker_rule(train)
    if checker is not None:
        rule_specs.append(("periodic_propagation", checker[0], checker[1], 6))
    l_ray = _bottom_right_l_rule(train)
    if l_ray is not None:
        rule_specs.append(("ray_dynamics", l_ray[0], l_ray[1], 6))
    suffix_tile = _suffix_vertical_tile_rule(train)
    if suffix_tile is not None:
        rule_specs.append(("periodic_propagation", suffix_tile[0], suffix_tile[1], 5))
    triangles = _bar_triangles_rule(train)
    if triangles is not None:
        rule_specs.append(("shape_construction", triangles[0], triangles[1], 7))
    rectangles = _ranked_rectangle_rule(train)
    if rectangles is not None:
        rule_specs.append(("object_ranking", rectangles[0], rectangles[1], 8))
    row_carrier = _row_keyed_carrier_rule(train)
    if row_carrier is not None:
        rule_specs.append(("role_transfer", row_carrier[0], row_carrier[1], 6))
    boundary = _boundary_cartesian_rule(train)
    if boundary is not None:
        rule_specs.append(("axis_composition", boundary[0], boundary[1], 6))
    corners = _corner_rectangle_rule(train)
    if corners is not None:
        rule_specs.append(("shape_construction", corners[0], corners[1], 6))
    quadrants = _quadrant_carrier_rule(train)
    if quadrants is not None:
        rule_specs.append(("role_transfer", quadrants[0], quadrants[1], 8))
    horizontal_bridge = _horizontal_gap_bridge_rule(train)
    if horizontal_bridge is not None:
        rule_specs.append(("shape_construction", horizontal_bridge[0], horizontal_bridge[1], 5))
    rectangle_bridge = _rectangle_bridge_rule(train)
    if rectangle_bridge is not None:
        rule_specs.append(("shape_construction", rectangle_bridge[0], rectangle_bridge[1], 7))
    paired_rectangles = _paired_points_rectangle_rule(train)
    if paired_rectangles is not None:
        rule_specs.append(("shape_construction", paired_rectangles[0], paired_rectangles[1], 5))
    size_colors = _component_size_color_rule(train)
    if size_colors is not None:
        rule_specs.append(("object_classification", size_colors[0], size_colors[1], 8 + len(size_colors[1]["observed_size_colors"])))
    legend_columns = _legend_column_recolor_rule(train)
    if legend_columns is not None:
        rule_specs.append(("role_transfer", legend_columns[0], legend_columns[1], 7))

    candidates: list[dict[str, Any]] = []
    for family, rule, program, complexity in rule_specs:
        candidate = _candidate(family, program, complexity, rule, train, tests)
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
    cap = 64
    if isinstance(limits, Mapping):
        raw = limits.get("max_candidates", limits.get("candidate_cap", cap))
        if isinstance(raw, int) and not isinstance(raw, bool) and raw > 0:
            cap = min(cap, raw)
    return unique[:cap]


__all__ = ["compile_task"]
