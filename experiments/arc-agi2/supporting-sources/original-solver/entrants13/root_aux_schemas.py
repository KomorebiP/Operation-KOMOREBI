"""Compact reusable schemas recovered during the Block 13 tournament.

The entrant is task-identity blind.  It learns only from demonstration pairs,
replays every demonstration exactly, and then applies the same structural rule
to test inputs.
"""

from __future__ import annotations

from collections import Counter, deque
import hashlib
import itertools
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
    if any(isinstance(v, bool) or not isinstance(v, int) or not 0 <= v <= 9 for row in value for v in row):
        raise ValueError("invalid cell")
    return tuple(tuple(row) for row in value)


def _plain(grid: Grid) -> list[list[int]]:
    return [list(row) for row in grid]


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _mode(grid: Grid) -> int:
    counts = Counter(v for row in grid for v in row)
    return min(counts, key=lambda v: (-counts[v], v))


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


def _extract_layout(source: Grid, oh: int, ow: int, layout: tuple[str, int, int]) -> list[Grid] | None:
    kind, nr, nc = layout
    height, width = len(source), len(source[0])
    if kind == "packed":
        if height != nr * oh or width != nc * ow:
            return None
        return [
            tuple(tuple(source[rr * oh + r][cc * ow + c] for c in range(ow)) for r in range(oh))
            for rr in range(nr)
            for cc in range(nc)
        ]
    if height != nr * oh + nr - 1 or width != nc * ow + nc - 1:
        return None
    separator_cells = []
    for r in range(height):
        for c in range(width):
            if (r + 1) % (oh + 1) == 0 or (c + 1) % (ow + 1) == 0:
                separator_cells.append(source[r][c])
    if not separator_cells or len(set(separator_cells)) != 1:
        return None
    return [
        tuple(
            tuple(source[rr * (oh + 1) + r][cc * (ow + 1) + c] for c in range(ow))
            for r in range(oh)
        )
        for rr in range(nr)
        for cc in range(nc)
    ]


def _layout_options(source: Grid, target: Grid) -> list[tuple[str, int, int]]:
    height, width = len(source), len(source[0])
    oh, ow = len(target), len(target[0])
    options: list[tuple[str, int, int]] = []
    if height % oh == 0 and width % ow == 0:
        nr, nc = height // oh, width // ow
        if 2 <= nr * nc <= 6:
            options.append(("packed", nr, nc))
    if (height + 1) % (oh + 1) == 0 and (width + 1) % (ow + 1) == 0:
        nr, nc = (height + 1) // (oh + 1), (width + 1) // (ow + 1)
        if 2 <= nr * nc <= 6:
            options.append(("separator_grid", nr, nc))
    return options


def _priority_overlay_rule(train: Sequence[tuple[Grid, Grid]]) -> tuple[Rule, dict[str, Any]] | None:
    shared = set(_layout_options(*train[0]))
    for source, target in train[1:]:
        shared &= set(_layout_options(source, target))
    learned: list[tuple[tuple[str, int, int], int, tuple[int, ...], tuple[int, ...]]] = []
    for layout in sorted(shared):
        examples: list[tuple[list[Grid], Grid]] = []
        all_panels: list[Grid] = []
        valid = True
        for source, target in train:
            panels = _extract_layout(source, len(target), len(target[0]), layout)
            if panels is None:
                valid = False
                break
            examples.append((panels, target))
            all_panels.extend(panels)
        if not valid:
            continue
        common = set(v for row in all_panels[0] for v in row)
        for panel in all_panels[1:]:
            common &= {v for row in panel for v in row}
        if len(common) != 1:
            continue
        background = next(iter(common))
        panel_count = layout[1] * layout[2]
        slot_colors: list[int] = []
        for slot in range(panel_count):
            choices = set()
            for panels, _ in examples:
                colors = {v for row in panels[slot] for v in row if v != background}
                if len(colors) != 1:
                    valid = False
                    break
                choices |= colors
            if not valid or len(choices) != 1:
                valid = False
                break
            slot_colors.append(next(iter(choices)))
        if not valid or len(set(slot_colors)) != panel_count:
            continue
        fitting: list[tuple[int, ...]] = []
        for order in itertools.permutations(slot_colors):
            rank = {color: index for index, color in enumerate(order)}
            ok = True
            for panels, target in examples:
                for r in range(len(target)):
                    for c in range(len(target[0])):
                        active = [slot_colors[i] for i, panel in enumerate(panels) if panel[r][c] == slot_colors[i]]
                        predicted = max(active, key=rank.__getitem__) if active else background
                        if predicted != target[r][c]:
                            ok = False
                            break
                    if not ok:
                        break
                if not ok:
                    break
            if ok:
                fitting.append(order)
        if len(fitting) == 1:
            learned.append((layout, background, tuple(slot_colors), fitting[0]))
    if len(learned) != 1:
        return None
    layout, background, slot_colors, order = learned[0]
    oh, ow = len(train[0][1]), len(train[0][1][0])
    rank = {color: index for index, color in enumerate(order)}

    def apply(source: Grid) -> Grid | None:
        panels = _extract_layout(source, oh, ow, layout)
        if panels is None or len(panels) != len(slot_colors):
            return None
        for panel, color in zip(panels, slot_colors):
            if any(v not in {background, color} for row in panel for v in row):
                return None
        result = []
        for r in range(oh):
            row = []
            for c in range(ow):
                active = [slot_colors[i] for i, panel in enumerate(panels) if panel[r][c] == slot_colors[i]]
                row.append(max(active, key=rank.__getitem__) if active else background)
            result.append(tuple(row))
        return tuple(result)

    return apply, {
        "operator": "priority_overlay_of_layout_panels",
        "layout": list(layout),
        "background": background,
        "panel_colors": list(slot_colors),
        "priority_low_to_high": list(order),
    }


def _panel_count_rule(train: Sequence[tuple[Grid, Grid]]) -> tuple[Rule, dict[str, Any]] | None:
    learned_mapping: dict[int, int] = {}
    signal_color: int | None = None
    panel_background: int | None = None
    output_shape = (len(train[0][1]), len(train[0][1][0]))
    panel_shape: tuple[int, int] | None = None
    separator_color: int | None = None
    for source, target in train:
        rows, columns = len(target), len(target[0])
        if (rows, columns) != output_shape:
            return None
        dh, dw = len(source) - (rows - 1), len(source[0]) - (columns - 1)
        if dh <= 0 or dw <= 0 or dh % rows or dw % columns:
            return None
        ph, pw = dh // rows, dw // columns
        if ph < 2 or pw < 2 or (panel_shape is not None and panel_shape != (ph, pw)):
            return None
        panel_shape = (ph, pw)
        separators = [
            source[r][c]
            for r in range(len(source))
            for c in range(len(source[0]))
            if (r + 1) % (ph + 1) == 0 or (c + 1) % (pw + 1) == 0
        ]
        if not separators or len(set(separators)) != 1:
            return None
        sep = separators[0]
        if separator_color is not None and sep != separator_color:
            return None
        separator_color = sep
        panels = _extract_layout(source, ph, pw, ("separator_grid", rows, columns))
        if panels is None:
            return None
        colors = Counter(v for panel in panels for row in panel for v in row)
        bg = max(colors, key=lambda v: (colors[v], -v))
        others = {v for panel in panels for row in panel for v in row if v != bg}
        if len(others) != 1:
            return None
        sig = next(iter(others))
        if panel_background is not None and bg != panel_background:
            return None
        if signal_color is not None and sig != signal_color:
            return None
        panel_background, signal_color = bg, sig
        for index, panel in enumerate(panels):
            count = sum(v == sig for row in panel for v in row)
            value = target[index // columns][index % columns]
            prior = learned_mapping.setdefault(count, value)
            if prior != value:
                return None
    if panel_shape is None or signal_color is None or panel_background is None or len(learned_mapping) < 2:
        return None
    ph, pw = panel_shape
    rows, columns = output_shape

    def apply(source: Grid) -> Grid | None:
        panels = _extract_layout(source, ph, pw, ("separator_grid", rows, columns))
        if panels is None:
            return None
        values = []
        for panel in panels:
            if any(v not in {panel_background, signal_color} for row in panel for v in row):
                return None
            count = sum(v == signal_color for row in panel for v in row)
            if count not in learned_mapping:
                return None
            values.append(learned_mapping[count])
        return tuple(tuple(values[r * columns:(r + 1) * columns]) for r in range(rows))

    return apply, {
        "operator": "serialize_panel_signal_cardinality",
        "panel_shape": [ph, pw],
        "mapping": [[count, learned_mapping[count]] for count in sorted(learned_mapping)],
    }


def _concentric_frequency_rule(train: Sequence[tuple[Grid, Grid]]) -> tuple[Rule, dict[str, Any]] | None:
    def transform(source: Grid) -> Grid | None:
        background = _mode(source)
        counts = Counter(v for row in source for v in row if v != background)
        if not 2 <= len(counts) <= 8 or len(set(counts.values())) != len(counts):
            return None
        colors = sorted(counts, key=lambda v: (-counts[v], v))
        size = 2 * len(colors) - 1
        return tuple(
            tuple(colors[min(r, c, size - 1 - r, size - 1 - c)] for c in range(size))
            for r in range(size)
        )

    if any(transform(source) != target for source, target in train):
        return None
    return transform, {"operator": "complete_concentric_frames_by_clue_frequency"}


def _components(grid: Grid, background: int) -> list[list[tuple[int, int]]]:
    seen: set[tuple[int, int]] = set()
    result: list[list[tuple[int, int]]] = []
    for r, row in enumerate(grid):
        for c, value in enumerate(row):
            if value == background or (r, c) in seen:
                continue
            color = value
            component: list[tuple[int, int]] = []
            queue = deque([(r, c)])
            seen.add((r, c))
            while queue:
                rr, cc = queue.popleft()
                component.append((rr, cc))
                for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nr, nc = rr + dr, cc + dc
                    if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and (nr, nc) not in seen and grid[nr][nc] == color:
                        seen.add((nr, nc))
                        queue.append((nr, nc))
            result.append(component)
    return result


def _replicate_template(source: Grid) -> Grid | None:
    background = _mode(source)
    by_color: dict[int, list[tuple[int, int]]] = {}
    for r, row in enumerate(source):
        for c, value in enumerate(row):
            if value != background:
                by_color.setdefault(value, []).append((r, c))
    prototype_colors = [color for color, cells in by_color.items() if len(cells) > 1]
    signal_colors = [color for color, cells in by_color.items() if len(cells) == 1]
    if len(prototype_colors) != 1 or not 1 <= len(signal_colors) <= 8:
        return None
    proto_color = prototype_colors[0]
    prototype = by_color[proto_color]
    signals = [(by_color[color][0][0], by_color[color][0][1], color) for color in signal_colors]
    same_row = len({r for r, _, _ in signals}) == 1
    same_column = len({c for _, c, _ in signals}) == 1
    if same_row == same_column:
        return None
    min_r = min(r for r, _ in prototype)
    max_r = max(r for r, _ in prototype)
    min_c = min(c for _, c in prototype)
    max_c = max(c for _, c in prototype)
    shape = {(r - min_r, c - min_c) for r, c in prototype}
    ph, pw = max_r - min_r + 1, max_c - min_c + 1
    signals.sort(key=(lambda item: item[1]) if same_row else (lambda item: item[0]))
    height, width = (ph, pw * len(signals)) if same_row else (ph * len(signals), pw)
    result = [[background] * width for _ in range(height)]
    for index, (_, _, color) in enumerate(signals):
        row_offset, column_offset = (0, index * pw) if same_row else (index * ph, 0)
        for r, c in shape:
            result[row_offset + r][column_offset + c] = color
    return tuple(tuple(row) for row in result)


def _template_replication_rule(train: Sequence[tuple[Grid, Grid]]) -> tuple[Rule, dict[str, Any]] | None:
    if any(_replicate_template(source) != target for source, target in train):
        return None
    return _replicate_template, {"operator": "replicate_prototype_at_ordered_color_signals"}


def _lattice_upsample_rule(train: Sequence[tuple[Grid, Grid]]) -> tuple[Rule, dict[str, Any]] | None:
    fitting: list[tuple[int, int, int, int, int, int]] = []
    for row_stride in range(1, 5):
        for column_stride in range(1, 5):
            for row_offset in range(row_stride):
                for column_offset in range(column_stride):
                    specs: list[tuple[int, int]] = []
                    valid = True
                    for source, target in train:
                        sampled_height = len(range(row_offset, len(source), row_stride))
                        sampled_width = len(range(column_offset, len(source[0]), column_stride))
                        if not sampled_height or not sampled_width or len(target) % sampled_height or len(target[0]) % sampled_width:
                            valid = False
                            break
                        scale_r, scale_c = len(target) // sampled_height, len(target[0]) // sampled_width
                        if not 2 <= scale_r <= 6 or not 2 <= scale_c <= 6:
                            valid = False
                            break
                        specs.append((scale_r, scale_c))
                        prediction = tuple(
                            tuple(
                                source[row_offset + (r // scale_r) * row_stride][column_offset + (c // scale_c) * column_stride]
                                for c in range(len(target[0]))
                            )
                            for r in range(len(target))
                        )
                        if prediction != target:
                            valid = False
                            break
                    if valid and len(set(specs)) == 1:
                        scale_r, scale_c = specs[0]
                        fitting.append((row_stride, column_stride, row_offset, column_offset, scale_r, scale_c))
    if len(fitting) != 1:
        return None
    row_stride, column_stride, row_offset, column_offset, scale_r, scale_c = fitting[0]

    def apply(source: Grid) -> Grid | None:
        sampled_rows = list(range(row_offset, len(source), row_stride))
        sampled_columns = list(range(column_offset, len(source[0]), column_stride))
        height, width = len(sampled_rows) * scale_r, len(sampled_columns) * scale_c
        if height > 30 or width > 30:
            return None
        return tuple(
            tuple(source[sampled_rows[r // scale_r]][sampled_columns[c // scale_c]] for c in range(width))
            for r in range(height)
        )

    return apply, {
        "operator": "sample_lattice_then_block_upsample",
        "stride": [row_stride, column_stride],
        "offset": [row_offset, column_offset],
        "scale": [scale_r, scale_c],
    }


def _three_row_recolor_rule(train: Sequence[tuple[Grid, Grid]]) -> tuple[Rule, dict[str, Any]] | None:
    fill_colors: set[int] = set()
    for source, target in train:
        if len(target) != 3 or len(source) < 3 or len(source[0]) != len(target[0]):
            return None
        if target[0] != source[0] or target[1] != source[1]:
            return None
        carrier = _mode((source[1],))
        changed_source_colors = {source[0][c] for c in range(len(source[0])) if target[2][c] != source[0][c]}
        changed_target_colors = {target[2][c] for c in range(len(source[0])) if target[2][c] != source[0][c]}
        if len(changed_source_colors) != 1 or carrier in changed_source_colors or len(changed_target_colors) != 1:
            return None
        if any((target[2][c] == source[0][c]) != (source[0][c] == carrier) for c in range(len(source[0]))):
            return None
        fill_colors |= changed_target_colors
        if any(len({v for v in row if v != carrier}) > 1 for row in source[1:]):
            return None
    if len(fill_colors) != 1:
        return None
    fill = next(iter(fill_colors))

    def apply(source: Grid) -> Grid | None:
        if len(source) < 2:
            return None
        carrier = _mode((source[1],))
        colors = {v for v in source[0] if v != carrier}
        if len(colors) != 1:
            return None
        third = tuple(carrier if v == carrier else fill for v in source[0])
        return source[0], source[1], third

    return apply, {"operator": "continue_line_state_with_recolored_pattern", "successor_color": fill}


def _marked_half_transform(source: Grid, marker: int) -> Grid | None:
    background = _mode(source)
    positions = [(r, c) for r, row in enumerate(source) for c, value in enumerate(row) if value == marker]
    if not positions or marker == background:
        return None
    height, width = len(source), len(source[0])
    if all(c == 0 for _, c in positions) or all(c == width - 1 for _, c in positions):
        if height % 2:
            return None
        halves = (source[: height // 2], source[height // 2 :])
        membership = {0 if r < height // 2 else 1 for r, _ in positions}
    elif all(r == 0 for r, _ in positions) or all(r == height - 1 for r, _ in positions):
        if width % 2:
            return None
        halves = (
            tuple(tuple(row[: width // 2]) for row in source),
            tuple(tuple(row[width // 2 :]) for row in source),
        )
        membership = {0 if c < width // 2 else 1 for _, c in positions}
    else:
        return None
    if len(membership) != 1:
        return None
    chosen = halves[next(iter(membership))]
    return tuple(tuple(background if value == marker else value for value in row) for row in chosen)


def _marked_half_rule(train: Sequence[tuple[Grid, Grid]]) -> tuple[Rule, dict[str, Any]] | None:
    common_colors = set(v for row in train[0][0] for v in row)
    for source, _ in train[1:]:
        common_colors &= {v for row in source for v in row}
    fitting = [marker for marker in sorted(common_colors) if all(_marked_half_transform(source, marker) == target for source, target in train)]
    if len(fitting) != 1:
        return None
    marker = fitting[0]
    return lambda source: _marked_half_transform(source, marker), {
        "operator": "select_edge_marked_half_and_erase_marker",
        "marker": marker,
    }


def _panel_difference_rule(train: Sequence[tuple[Grid, Grid]]) -> tuple[Rule, dict[str, Any]] | None:
    left_only_codes: set[int] = set()
    right_only_codes: set[int] = set()
    backgrounds: set[int] = set()
    separators: set[int] = set()
    for source, target in train:
        height, width = len(source), len(source[0])
        if len(target) != height or width != 2 * len(target[0]) + 1:
            return None
        panel_width = len(target[0])
        separator = {source[r][panel_width] for r in range(height)}
        if len(separator) != 1:
            return None
        separators |= separator
        left = tuple(tuple(row[:panel_width]) for row in source)
        right = tuple(tuple(row[panel_width + 1:]) for row in source)
        background = _mode(left + right)
        backgrounds.add(background)
        for r in range(height):
            for c in range(panel_width):
                lv, rv, tv = left[r][c], right[r][c], target[r][c]
                if lv == rv:
                    if tv != lv:
                        return None
                elif lv == background and rv != background:
                    right_only_codes.add(tv)
                elif lv != background and rv == background:
                    left_only_codes.add(tv)
                else:
                    return None
    if len(backgrounds) != 1 or len(separators) != 1 or len(left_only_codes) != 1 or len(right_only_codes) != 1:
        return None
    background = next(iter(backgrounds))
    separator = next(iter(separators))
    left_code = next(iter(left_only_codes))
    right_code = next(iter(right_only_codes))
    if left_code == right_code:
        return None

    def apply(source: Grid) -> Grid | None:
        width = len(source[0])
        if width % 2 != 1:
            return None
        panel_width = width // 2
        if any(row[panel_width] != separator for row in source):
            return None
        result = []
        for row in source:
            out_row = []
            for c in range(panel_width):
                lv, rv = row[c], row[panel_width + 1 + c]
                if lv == rv:
                    out_row.append(lv)
                elif lv == background and rv != background:
                    out_row.append(right_code)
                elif lv != background and rv == background:
                    out_row.append(left_code)
                else:
                    return None
            result.append(tuple(out_row))
        return tuple(result)

    return apply, {
        "operator": "compare_aligned_panels_with_directional_difference_codes",
        "left_only": left_code,
        "right_only": right_code,
        "separator": separator,
    }


def compile_task(task: Mapping[str, Any], limits: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    try:
        train = [(_grid(example["input"]), _grid(example["output"])) for example in task["train"]]
        tests = [_grid(example["input"]) for example in task["test"]]
    except (KeyError, TypeError, ValueError):
        return []
    if not train or not tests:
        return []
    specs: list[tuple[str, Rule, dict[str, Any], int]] = []
    overlay = _priority_overlay_rule(train)
    if overlay is not None:
        specs.append(("panel_composition", overlay[0], overlay[1], 8))
    panel_count = _panel_count_rule(train)
    if panel_count is not None:
        specs.append(("panel_serialization", panel_count[0], panel_count[1], 7))
    rings = _concentric_frequency_rule(train)
    if rings is not None:
        specs.append(("concentric_completion", rings[0], rings[1], 6))
    replication = _template_replication_rule(train)
    if replication is not None:
        specs.append(("template_replication", replication[0], replication[1], 7))
    lattice = _lattice_upsample_rule(train)
    if lattice is not None:
        specs.append(("lattice_projection", lattice[0], lattice[1], 6))
    successor = _three_row_recolor_rule(train)
    if successor is not None:
        specs.append(("line_state", successor[0], successor[1], 6))
    marked_half = _marked_half_rule(train)
    if marked_half is not None:
        specs.append(("marked_extraction", marked_half[0], marked_half[1], 6))
    panel_difference = _panel_difference_rule(train)
    if panel_difference is not None:
        specs.append(("panel_comparison", panel_difference[0], panel_difference[1], 6))
    candidates = []
    for family, rule, program, complexity in specs:
        candidate = _candidate(family, program, complexity, rule, train, tests)
        if candidate is not None:
            candidates.append(candidate)
    candidates.sort(key=lambda item: (item["complexity"], item["family"], _canonical(item["program"])))
    cap = 64
    if isinstance(limits, Mapping):
        raw = limits.get("max_candidates", limits.get("candidate_cap", cap))
        if isinstance(raw, int) and not isinstance(raw, bool) and raw > 0:
            cap = min(cap, raw)
    return candidates[:cap]


__all__ = ["compile_task"]
