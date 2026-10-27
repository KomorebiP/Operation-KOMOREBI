"""Bounded same-shape structural schemas for the Block 13 tournament.

Every emitted program is a small, task-independent geometric rule.  Programs
are admitted only after exact replay of every demonstration, and they receive
only demonstrations plus test inputs.  No task identity, corpus fingerprint,
or held-out target is used.

Author: Komorebi P.
"""

from __future__ import annotations

from collections import Counter, defaultdict, deque
from dataclasses import dataclass
import itertools
import json
from typing import Any, Callable, Iterable, Mapping, Sequence


Grid = list[list[int]]


@dataclass(frozen=True)
class Limits:
    max_side: int = 30
    max_candidates: int = 96
    max_cover_nodes: int = 20_000

    @classmethod
    def from_value(cls, value: Mapping[str, Any] | None) -> "Limits":
        if not isinstance(value, Mapping):
            return cls()
        cap_values = [
            int(value[key])
            for key in ("max_candidates", "candidate_cap", "max_programs")
            if key in value
        ]
        return cls(
            max_side=int(value.get("max_side", cls.max_side)),
            max_candidates=min(cap_values) if cap_values else cls.max_candidates,
            max_cover_nodes=int(value.get("max_cover_nodes", cls.max_cover_nodes)),
        )


@dataclass
class Proposal:
    operator: str
    parameters: dict[str, Any]
    execute: Callable[[Grid], Grid]
    complexity: int
    evidence: dict[str, Any]


def _grid(value: Any, limits: Limits) -> Grid:
    if not isinstance(value, list) or not value or len(value) > limits.max_side:
        raise ValueError("invalid grid rows")
    if not all(isinstance(row, list) and row for row in value):
        raise ValueError("invalid grid row")
    width = len(value[0])
    if width > limits.max_side or any(len(row) != width for row in value):
        raise ValueError("invalid grid shape")
    result: Grid = []
    for row in value:
        if any(isinstance(cell, bool) or not isinstance(cell, int) or not 0 <= cell <= 9 for cell in row):
            raise ValueError("invalid ARC color")
        result.append([int(cell) for cell in row])
    return result


def _copy(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def _shape(grid: Grid) -> tuple[int, int]:
    return len(grid), len(grid[0])


def _mode(grid: Grid) -> int:
    counts = Counter(cell for row in grid for cell in row)
    return min(counts, key=lambda color: (-counts[color], color))


def _palette(grid: Grid) -> set[int]:
    return {cell for row in grid for cell in row}


def _components(points: Iterable[tuple[int, int]]) -> list[set[tuple[int, int]]]:
    remaining = set(points)
    result: list[set[tuple[int, int]]] = []
    while remaining:
        seed = min(remaining)
        remaining.remove(seed)
        component = {seed}
        queue = [seed]
        while queue:
            row, column = queue.pop()
            for dr, dc in ((-1, 0), (0, -1), (0, 1), (1, 0)):
                point = (row + dr, column + dc)
                if point in remaining:
                    remaining.remove(point)
                    component.add(point)
                    queue.append(point)
        result.append(component)
    return sorted(result, key=lambda component: (min(component), len(component)))


def _normalize(points: Iterable[tuple[int, int]]) -> tuple[tuple[int, int], ...]:
    points = tuple(points)
    top = min(row for row, _ in points)
    left = min(column for _, column in points)
    return tuple(sorted((row - top, column - left) for row, column in points))


def _rot90(grid: Grid, turns: int) -> Grid:
    result = _copy(grid)
    for _ in range(turns % 4):
        result = [list(row) for row in zip(*result[::-1])]
    return result


def _proposal(
    operator: str,
    parameters: Mapping[str, Any],
    execute: Callable[[Grid], Grid],
    complexity: int,
    **evidence: Any,
) -> Proposal:
    return Proposal(operator, dict(parameters), execute, complexity, dict(evidence))


def _central_axis_proposals(train: Sequence[tuple[Grid, Grid]]) -> list[Proposal]:
    result: list[Proposal] = []
    for axis in ("column", "row"):
        def execute(grid: Grid, axis: str = axis) -> Grid:
            height, width = _shape(grid)
            background = _mode(grid)
            output = [[background] * width for _ in range(height)]
            if axis == "column":
                if width % 2 == 0:
                    raise ValueError("no central column")
                column = width // 2
                for row in range(height):
                    output[row][column] = grid[row][column]
            else:
                if height % 2 == 0:
                    raise ValueError("no central row")
                row = height // 2
                output[row] = grid[row][:]
            return output
        result.append(_proposal("retain_central_axis", {"axis": axis}, execute, 2, axis_role=True))
    return result


def _marker_component_proposals(train: Sequence[tuple[Grid, Grid]]) -> list[Proposal]:
    common = set.intersection(*(_palette(source) for source, _ in train))
    result: list[Proposal] = []
    for source_color in sorted(common):
        def execute(grid: Grid, source_color: int = source_color) -> Grid:
            height, width = _shape(grid)
            background = _mode(grid)
            if source_color == background:
                raise ValueError("source equals background")
            marker_points = {
                (row, column): grid[row][column]
                for row in range(height)
                for column in range(width)
                if grid[row][column] not in {background, source_color}
            }
            output = _copy(grid)
            for row, column in marker_points:
                output[row][column] = background
            source_points = {
                (row, column)
                for row in range(height)
                for column in range(width)
                if grid[row][column] == source_color
            }
            for component in _components(source_points):
                labels: set[int] = set()
                for row, column in component:
                    for dr, dc in ((-1, 0), (0, -1), (0, 1), (1, 0)):
                        label = marker_points.get((row + dr, column + dc))
                        if label is not None:
                            labels.add(label)
                if len(labels) == 1:
                    label = next(iter(labels))
                    for row, column in component:
                        output[row][column] = label
            return output
        result.append(_proposal(
            "adjacent_marker_component_label",
            {"source_color": source_color, "connectivity": 4, "erase_markers": True},
            execute,
            5,
            component_local=True,
        ))
    return result


def _duplicate_component_consolidation_proposal() -> Proposal:
    def execute(grid: Grid) -> Grid:
        height, width = _shape(grid)
        background = _mode(grid)
        output = _copy(grid)
        consolidated = 0
        for color in sorted(_palette(grid) - {background}):
            points = {(row, column) for row in range(height) for column in range(width) if grid[row][column] == color}
            components = _components(points)
            if len(components) <= 1:
                continue
            consolidated += 1
            target = max(
                components,
                key=lambda component: (
                    max(column for _, column in component),
                    min(column for _, column in component),
                    len(component),
                ),
            )
            for row in range(height):
                for column in range(width):
                    if output[row][column] == color:
                        output[row][column] = background
            top = min(row for row, _ in target)
            bottom = max(row for row, _ in target)
            left = max(0, min(column for _, column in target) - 1)
            right = max(column for _, column in target)
            for row in range(top, bottom + 1):
                for column in range(left, right + 1):
                    if output[row][column] != background:
                        raise ValueError("consolidated rectangle collides")
                    output[row][column] = color
        if consolidated == 0:
            raise ValueError("no duplicate color components")
        return output

    return _proposal(
        "consolidate_duplicate_color_into_expanded_rightmost_bbox",
        {"expansion": "one_column_toward_duplicates"},
        execute,
        6,
        component_count_triggered=True,
    )


def _quadrant_completion_proposal() -> Proposal:
    def execute(grid: Grid) -> Grid:
        height, width = _shape(grid)
        separator_rows = [row for row in range(height) if len(set(grid[row])) == 1]
        separator_columns = [
            column for column in range(width)
            if len({grid[row][column] for row in range(height)}) == 1
        ]
        choices = [
            (row, column, grid[row][column])
            for row in separator_rows
            for column in separator_columns
            if grid[row][column] == grid[row][0]
            and all(grid[r][column] == grid[row][0] for r in range(height))
        ]
        if len(choices) != 1:
            raise ValueError("not one cross separator")
        split_row, split_column, separator = choices[0]
        if not (0 < split_row < height - 1 and 0 < split_column < width - 1):
            raise ValueError("separator is not interior")
        colors = _palette(grid) - {separator}
        if not colors:
            raise ValueError("empty quadrant palette")
        output = _copy(grid)
        regions = (
            (range(0, split_row), range(0, split_column)),
            (range(0, split_row), range(split_column + 1, width)),
            (range(split_row + 1, height), range(0, split_column)),
            (range(split_row + 1, height), range(split_column + 1, width)),
        )
        region_points = [[(row, column) for row in rows for column in columns] for rows, columns in regions]
        desired_counts = {
            color: max(sum(grid[row][column] == color for row, column in points) for points in region_points)
            for color in colors
        }
        if sum(desired_counts.values()) != len(region_points[0]):
            raise ValueError("quadrants do not share a complete color multiset")
        for points in region_points:
            holes = [(row, column) for row, column in points if grid[row][column] == separator]
            missing: list[int] = []
            for color in sorted(colors):
                present = sum(grid[row][column] == color for row, column in points)
                if present > desired_counts[color]:
                    raise ValueError("quadrant exceeds shared multiset")
                missing.extend([color] * (desired_counts[color] - present))
            if len(missing) != len(holes):
                raise ValueError("quadrant holes do not match shared multiset")
            for (row, column), fill in zip(sorted(holes), missing):
                output[row][column] = fill
        return output
    return _proposal("quadrant_missing_palette_completion", {}, execute, 5, palette_relational=True)


def _rotational_panel_proposals() -> list[Proposal]:
    result: list[Proposal] = []
    for turns in (1, 2, 3):
        def execute(grid: Grid, turns: int = turns) -> Grid:
            height, width = _shape(grid)
            background = _mode(grid)
            columns_by_color: dict[int, list[int]] = defaultdict(list)
            for column in range(width):
                values = {grid[row][column] for row in range(height)}
                if len(values) == 1:
                    color = next(iter(values))
                    if color != background:
                        columns_by_color[color].append(column)
            candidates = [(color, cols) for color, cols in columns_by_color.items() if len(cols) >= 2]
            if len(candidates) != 1:
                raise ValueError("not a separated panel row")
            separator, columns = candidates[0]
            boundaries = [-1] + columns + [width]
            panels = [(boundaries[i] + 1, boundaries[i + 1]) for i in range(len(boundaries) - 1)]
            if len(panels) < 2 or any(right - left != height for left, right in panels):
                raise ValueError("panels are not equal squares")
            base = [row[panels[0][0]:panels[0][1]] for row in grid]
            output = _copy(grid)
            for index, (left, right) in enumerate(panels):
                tile = _rot90(base, turns * index)
                for row in range(height):
                    output[row][left:right] = tile[row]
            for column in columns:
                for row in range(height):
                    output[row][column] = separator
            return output
        result.append(_proposal(
            "rotational_panel_replication",
            {"quarter_turn_step": turns},
            execute,
            4,
            equal_square_panels=True,
        ))
    return result


def _top_zigzag_proposal() -> Proposal:
    def execute(grid: Grid) -> Grid:
        height, width = _shape(grid)
        background = _mode(grid)
        if any(grid[row][column] != background for row in range(1, height) for column in range(width)):
            raise ValueError("ink is not confined to the top row")
        seeds = [(column, grid[0][column]) for column in range(width) if grid[0][column] != background]
        if not seeds:
            raise ValueError("no seeds")
        output = [[background] * width for _ in range(height)]
        for row in range(height):
            for column, color in seeds:
                targets = (column,) if row % 2 == 0 else (column - 1, column + 1)
                for target in targets:
                    if 0 <= target < width:
                        if output[row][target] not in {background, color}:
                            raise ValueError("colored seed collision")
                        output[row][target] = color
        return output
    return _proposal("vertical_zigzag_seed_propagation", {"period": 2}, execute, 3, translation_equivariant=True)


def _project_2x2_proposal() -> Proposal:
    def execute(grid: Grid) -> Grid:
        height, width = _shape(grid)
        background = _mode(grid)
        points = [(row, column) for row in range(height) for column in range(width) if grid[row][column] != background]
        if len(points) != 4:
            raise ValueError("not a four-cell block")
        top = min(row for row, _ in points)
        left = min(column for _, column in points)
        if set(points) != {(top + dr, left + dc) for dr in (0, 1) for dc in (0, 1)}:
            raise ValueError("not a 2x2 block")
        output = _copy(grid)
        specifications = (
            (0, 0, 2, 2),
            (0, 1, 2, -2),
            (1, 0, -2, 2),
            (1, 1, -2, -2),
        )
        for dr, dc, row_offset, column_offset in specifications:
            color = grid[top + dr][left + dc]
            patch_top = top + row_offset
            patch_left = left + column_offset
            for rr in range(patch_top, patch_top + 2):
                for cc in range(patch_left, patch_left + 2):
                    if 0 <= rr < height and 0 <= cc < width:
                        output[rr][cc] = color
        return output
    return _proposal("diagonal_corner_projection_2x2", {"patch_side": 2}, execute, 5, clipping_equivariant=True)


def _rightward_scan_proposal() -> Proposal:
    def execute(grid: Grid) -> Grid:
        height, width = _shape(grid)
        background = _mode(grid)
        output = [[background] * width for _ in range(height)]
        active: int | None = None
        observed = 0
        for row in range(height):
            points = [(column, grid[row][column]) for column in range(width) if grid[row][column] != background]
            if len(points) > 1:
                raise ValueError("more than one row seed")
            if points:
                observed += 1
                column, active = points[0]
                for cc in range(column, width):
                    output[row][cc] = active
            elif active is not None:
                output[row][width - 1] = active
        if observed == 0:
            raise ValueError("no row seeds")
        return output
    return _proposal("rightward_row_rays_with_edge_memory", {}, execute, 4, scan_order="top_to_bottom")


def _vertical_periodic_proposal() -> Proposal:
    def execute(grid: Grid) -> Grid:
        height, width = _shape(grid)
        background = _mode(grid)
        nonblank = [row for row in range(height) if any(cell != background for cell in grid[row])]
        if not nonblank:
            raise ValueError("no suffix pattern")
        start = min(nonblank)
        if nonblank != list(range(start, height)) or start == 0:
            raise ValueError("pattern is not a proper suffix")
        suffix = grid[start:]
        period = len(suffix)
        for candidate in range(1, len(suffix) + 1):
            if all(suffix[index] == suffix[index % candidate] for index in range(len(suffix))):
                period = candidate
                break
        motif = suffix[:period]
        return [motif[(row - start) % period][:] for row in range(height)]
    return _proposal("vertical_periodic_suffix_extension", {}, execute, 4, phase_aligned_to_suffix=True)


def _background_recolor_proposals() -> list[Proposal]:
    result: list[Proposal] = []
    for color in range(10):
        def execute(grid: Grid, color: int = color) -> Grid:
            background = _mode(grid)
            if color == background:
                raise ValueError("identity recolor")
            return [[color if cell == background else cell for cell in row] for row in grid]
        result.append(_proposal("background_recolor", {"target_color": color}, execute, 2, preserves_foreground=True))
    return result


def _shift_foreground_recolor_proposals() -> list[Proposal]:
    """Move every foreground cell one step, clipping at the canvas, then recolor empty space."""

    result: list[Proposal] = []
    for dr, dc, direction in ((0, -1, "left"), (0, 1, "right"), (-1, 0, "up"), (1, 0, "down")):
        for fill in range(10):
            def execute(grid: Grid, dr: int = dr, dc: int = dc, fill: int = fill) -> Grid:
                height, width = _shape(grid)
                background = _mode(grid)
                if fill == background:
                    raise ValueError("identity background")
                output = [[fill] * width for _ in range(height)]
                for row in range(height):
                    for column in range(width):
                        if grid[row][column] == background:
                            continue
                        rr, cc = row + dr, column + dc
                        if 0 <= rr < height and 0 <= cc < width:
                            output[rr][cc] = grid[row][column]
                return output
            result.append(_proposal(
                "shift_foreground_and_recolor_background",
                {"direction": direction, "fill": fill},
                execute,
                4,
                translation_distance=1,
            ))
    return result


def _manhattan_cycle_proposals(train: Sequence[tuple[Grid, Grid]]) -> list[Proposal]:
    successor: dict[int, int] = {}
    valid = True
    for source, target in train:
        height, width = _shape(source)
        background = _mode(source)
        seeds = [(row, column, source[row][column]) for row in range(height) for column in range(width) if source[row][column] != background]
        if len(seeds) != 1 or _shape(target) != (height, width):
            valid = False
            break
        seed_row, seed_column, seed_color = seeds[0]
        rings: dict[int, set[int]] = defaultdict(set)
        for row in range(height):
            for column in range(width):
                rings[abs(row - seed_row) + abs(column - seed_column)].add(target[row][column])
        if any(len(values) != 1 for values in rings.values()) or next(iter(rings[0])) != seed_color:
            valid = False
            break
        sequence = [next(iter(rings[distance])) for distance in range(max(rings) + 1)]
        for before, after in zip(sequence, sequence[1:]):
            if before in successor and successor[before] != after:
                valid = False
                break
            successor[before] = after
        if not valid:
            break
    if not valid or len(successor) < 2:
        return []

    def execute(grid: Grid) -> Grid:
        height, width = _shape(grid)
        background = _mode(grid)
        seeds = [(row, column, grid[row][column]) for row in range(height) for column in range(width) if grid[row][column] != background]
        if len(seeds) != 1:
            raise ValueError("not one radial seed")
        seed_row, seed_column, seed_color = seeds[0]
        max_distance = max(seed_row + seed_column, seed_row + width - 1 - seed_column, height - 1 - seed_row + seed_column, height - 1 - seed_row + width - 1 - seed_column)
        sequence = [seed_color]
        for _ in range(max_distance):
            if sequence[-1] not in successor:
                raise ValueError("cycle not demonstrated far enough")
            sequence.append(successor[sequence[-1]])
        return [[sequence[abs(row - seed_row) + abs(column - seed_column)] for column in range(width)] for row in range(height)]

    return [_proposal(
        "manhattan_radial_color_cycle",
        {"successor": {str(key): successor[key] for key in sorted(successor)}},
        execute,
        5 + len(successor),
        ring_constant=True,
        transition_observations=len(successor),
    )]


def _point_lattice_proposal(train: Sequence[tuple[Grid, Grid]]) -> list[Proposal]:
    additions: set[int] = set()
    for source, target in train:
        height, width = _shape(source)
        background = _mode(source)
        seeds = [(row, column) for row in range(height) for column in range(width) if source[row][column] != background]
        if len(seeds) != 1:
            return []
        additions.update(target[row][column] for row in range(height) for column in range(width) if target[row][column] != source[row][column])
    if len(additions) != 1:
        return []
    draw = next(iter(additions))

    def execute(grid: Grid) -> Grid:
        height, width = _shape(grid)
        background = _mode(grid)
        seeds = [(row, column) for row in range(height) for column in range(width) if grid[row][column] != background]
        if len(seeds) != 1:
            raise ValueError("not a rare point")
        row, column = seeds[0]
        output = _copy(grid)
        for rr in range(height):
            if rr != row:
                output[rr][column] = draw
        if (row + column) % 2:
            top_columns = range(0, column + 1)
            bottom_columns = range(column, width)
        else:
            top_columns = range(column, width)
            bottom_columns = range(0, column + 1)
        for cc in top_columns:
            output[0][cc] = draw
        for cc in bottom_columns:
            output[height - 1][cc] = draw
        output[row][column] = grid[row][column]
        return output

    return [_proposal(
        "point_parity_axis_edge_lattice",
        {"draw_color": draw, "orientation": "coordinate_parity"},
        execute,
        5,
        coordinate_equivariant=True,
    )]


def _swirl_proposals() -> list[Proposal]:
    result: list[Proposal] = []
    for direction in (1, -1):
        def execute(grid: Grid, direction: int = direction) -> Grid:
            height, width = _shape(grid)
            background = _mode(grid)
            points = {(row, column) for row in range(height) for column in range(width) if grid[row][column] != background}
            components = _components(points)
            if not components:
                raise ValueError("no blocks")
            boxes: list[tuple[int, int]] = []
            for component in components:
                top = min(row for row, _ in component)
                bottom = max(row for row, _ in component)
                left = min(column for _, column in component)
                right = max(column for _, column in component)
                if bottom - top != 2 or right - left != 2:
                    raise ValueError("non-3x3 component box")
                boxes.append((top, left))
            output = _copy(grid)
            corners = ((0, 0), (0, 2), (2, 2), (2, 0))
            edges = ((0, 1), (1, 2), (2, 1), (1, 0))
            for top, left in boxes:
                original = [row[left:left + 3] for row in grid[top:top + 3]]
                for index, (dr, dc) in enumerate(corners):
                    source_index = (index + direction) % 4
                    sr, sc = corners[source_index]
                    output[top + dr][left + dc] = original[sr][sc]
                for index, (dr, dc) in enumerate(edges):
                    source_index = (index - direction) % 4
                    sr, sc = edges[source_index]
                    output[top + dr][left + dc] = original[sr][sc]
            return output
        result.append(_proposal(
            "counter_rotating_3x3_rings",
            {"corner_direction": direction, "edge_direction": -direction},
            execute,
            4,
            object_local=True,
        ))
    return result


def _symmetry_recolor_proposals(train: Sequence[tuple[Grid, Grid]]) -> list[Proposal]:
    common = set.intersection(*(_palette(source) for source, _ in train))
    transformations = ("flip_vertical", "flip_horizontal", "rotate_180", "transpose", "anti_transpose")
    result: list[Proposal] = []
    for ink in sorted(common):
        for transformation in transformations:
            observations: dict[bool, set[int]] = defaultdict(set)
            valid = True
            for source, target in train:
                height, width = _shape(source)
                others = _palette(source) - {ink}
                if len(others) != 1:
                    valid = False
                    break
                background = next(iter(others))
                if any(source[row][column] == background and target[row][column] != background for row in range(height) for column in range(width)):
                    valid = False
                    break
                for row in range(height):
                    for column in range(width):
                        if source[row][column] != ink:
                            if target[row][column] != background:
                                valid = False
                            continue
                        if transformation == "flip_vertical":
                            rr, cc = height - 1 - row, column
                        elif transformation == "flip_horizontal":
                            rr, cc = row, width - 1 - column
                        elif transformation == "rotate_180":
                            rr, cc = height - 1 - row, width - 1 - column
                        elif transformation == "transpose":
                            if height != width:
                                valid = False
                                break
                            rr, cc = column, row
                        else:
                            if height != width:
                                valid = False
                                break
                            rr, cc = width - 1 - column, height - 1 - row
                        observations[source[rr][cc] == ink].add(target[row][column])
                    if not valid:
                        break
                if not valid:
                    break
            if not valid or set(observations) != {False, True} or any(len(values) != 1 for values in observations.values()):
                continue
            labels = {state: next(iter(values)) for state, values in observations.items()}

            def execute(grid: Grid, ink: int = ink, transformation: str = transformation, labels: dict[bool, int] = labels) -> Grid:
                height, width = _shape(grid)
                others = _palette(grid) - {ink}
                if len(others) != 1:
                    raise ValueError("not a binary symmetry input")
                background = next(iter(others))
                output = [[background] * width for _ in range(height)]
                for row in range(height):
                    for column in range(width):
                        if grid[row][column] != ink:
                            if grid[row][column] != background:
                                raise ValueError("unexpected third input color")
                            continue
                        if transformation == "flip_vertical":
                            rr, cc = height - 1 - row, column
                        elif transformation == "flip_horizontal":
                            rr, cc = row, width - 1 - column
                        elif transformation == "rotate_180":
                            rr, cc = height - 1 - row, width - 1 - column
                        elif transformation == "transpose":
                            if height != width:
                                raise ValueError("nonsquare transpose")
                            rr, cc = column, row
                        else:
                            if height != width:
                                raise ValueError("nonsquare anti-transpose")
                            rr, cc = width - 1 - column, height - 1 - row
                        output[row][column] = labels[grid[rr][cc] == ink]
                return output

            result.append(_proposal(
                "symmetry_membership_recolor",
                {"ink": ink, "transform": transformation, "absent_label": labels[False], "present_label": labels[True]},
                execute,
                5,
                symmetry_relational=True,
            ))
    return result


def _edge_marker_fold_proposals(train: Sequence[tuple[Grid, Grid]]) -> list[Proposal]:
    """Fold a binary checker field toward a unique edge marker and draw its far-side wake."""

    common = set.intersection(*(_palette(source) for source, _ in train))
    result: list[Proposal] = []
    for marker in sorted(common):
        if any(sum(cell == marker for row in source for cell in row) != 1 for source, _ in train):
            continue
        output_roles = set.intersection(*(_palette(target) - {marker} for _, target in train))
        if len(output_roles) != 3:
            continue
        for near, far, trail in itertools.permutations(sorted(output_roles), 3):
            def execute(
                grid: Grid,
                marker: int = marker,
                near: int = near,
                far: int = far,
                trail: int = trail,
            ) -> Grid:
                height, width = _shape(grid)
                marker_points = [(row, column) for row in range(height) for column in range(width) if grid[row][column] == marker]
                if len(marker_points) != 1:
                    raise ValueError("not one edge marker")
                marker_row, marker_column = marker_points[0]
                sides: list[tuple[str, bool]] = []
                if marker_column == 0:
                    sides.append(("horizontal", False))
                if marker_column == width - 1:
                    sides.append(("horizontal", True))
                if marker_row == 0:
                    sides.append(("vertical", False))
                if marker_row == height - 1:
                    sides.append(("vertical", True))
                if len(sides) != 1:
                    raise ValueError("marker is not on exactly one edge")
                axis, high_side = sides[0]
                binary = _palette(grid) - {marker}
                if len(binary) != 2 or binary != {near, far}:
                    raise ValueError("field is not the inferred binary palette")
                output = [[far] * width for _ in range(height)]
                axis_size = width if axis == "horizontal" else height
                middle_twice = axis_size - 1
                for row in range(height):
                    for column in range(width):
                        coordinate = column if axis == "horizontal" else row
                        signed = 2 * coordinate - middle_twice
                        on_near_side = signed > 0 if high_side else signed < 0
                        on_far_side = signed < 0 if high_side else signed > 0
                        if on_near_side:
                            output[row][column] = near
                        elif on_far_side:
                            output[row][column] = far
                        else:
                            output[row][column] = far if grid[row][column] == near else near

                half = axis_size // 2
                perpendicular_size = height if axis == "horizontal" else width
                perpendicular_coordinate = marker_row if axis == "horizontal" else marker_column
                perpendicular_mid = (perpendicular_size - 1) // 2
                wake_length = max(1, half - max(0, perpendicular_mid - perpendicular_coordinate))
                if high_side:
                    wake_coordinates = range(half - wake_length, half)
                else:
                    start = (axis_size + 1) // 2
                    wake_coordinates = range(start, min(axis_size, start + wake_length))
                for coordinate in wake_coordinates:
                    row = marker_row if axis == "horizontal" else coordinate
                    column = coordinate if axis == "horizontal" else marker_column
                    output[row][column] = trail
                output[marker_row][marker_column] = marker
                return output

            result.append(_proposal(
                "edge_marker_binary_fold_with_wake",
                {"marker": marker, "near": near, "far": far, "wake": trail},
                execute,
                7,
                edge_relational=True,
            ))
    return result


def _exact_cover(
    grid: Grid,
    background: int,
    ink: int,
    templates: Mapping[int, tuple[tuple[int, int], ...]],
    max_nodes: int,
) -> Grid:
    height, width = _shape(grid)
    ink_points = {(row, column) for row in range(height) for column in range(width) if grid[row][column] == ink}
    if any(grid[row][column] not in {background, ink} for row in range(height) for column in range(width)) or not ink_points:
        raise ValueError("not a binary tiling")
    placements: list[tuple[int, tuple[tuple[int, int], ...]]] = []
    for label, shape in sorted(templates.items()):
        piece_height = max(row for row, _ in shape) + 1
        piece_width = max(column for _, column in shape) + 1
        for top in range(height - piece_height + 1):
            for left in range(width - piece_width + 1):
                points = tuple(sorted((top + row, left + column) for row, column in shape))
                if set(points) <= ink_points:
                    placements.append((label, points))
    by_point: dict[tuple[int, int], list[tuple[int, tuple[tuple[int, int], ...]]]] = defaultdict(list)
    for placement in placements:
        for point in placement[1]:
            by_point[point].append(placement)
    solutions: list[list[tuple[int, tuple[tuple[int, int], ...]]]] = []
    nodes = 0

    def search(remaining: set[tuple[int, int]], chosen: list[tuple[int, tuple[tuple[int, int], ...]]]) -> None:
        nonlocal nodes
        nodes += 1
        if nodes > max_nodes or len(solutions) > 1:
            return
        if not remaining:
            solutions.append(chosen[:])
            return
        point = min(
            remaining,
            key=lambda item: sum(set(placement[1]) <= remaining for placement in by_point.get(item, ())),
        )
        options = [placement for placement in by_point.get(point, ()) if set(placement[1]) <= remaining]
        for placement in sorted(options, key=lambda item: (item[0], item[1])):
            search(remaining - set(placement[1]), chosen + [placement])

    search(set(ink_points), [])
    if len(solutions) != 1:
        raise ValueError("tiling is not unique")
    output = [[background] * width for _ in range(height)]
    for label, points in solutions[0]:
        for row, column in points:
            output[row][column] = label
    return output


def _tiling_proposals(train: Sequence[tuple[Grid, Grid]], limits: Limits) -> list[Proposal]:
    backgrounds = {_mode(source) for source, _ in train}
    if len(backgrounds) != 1:
        return []
    background = next(iter(backgrounds))
    source_palettes = [_palette(source) - {background} for source, _ in train]
    if any(len(colors) != 1 for colors in source_palettes):
        return []
    inks = {next(iter(colors)) for colors in source_palettes}
    if len(inks) != 1:
        return []
    ink = next(iter(inks))
    shapes_by_label: dict[int, set[tuple[tuple[int, int], ...]]] = defaultdict(set)
    for source, target in train:
        height, width = _shape(source)
        if _shape(target) != (height, width):
            return []
        for row in range(height):
            for column in range(width):
                if source[row][column] == background and target[row][column] != background:
                    return []
                if source[row][column] == ink and target[row][column] == background:
                    return []
        labels = _palette(target) - {background}
        for label in labels:
            points = {(row, column) for row in range(height) for column in range(width) if target[row][column] == label}
            for component in _components(points):
                shape = _normalize(component)
                if len(shape) > 6:
                    return []
                shapes_by_label[label].add(shape)
    if len(shapes_by_label) < 2 or any(len(shapes) != 1 for shapes in shapes_by_label.values()):
        return []
    templates = {label: next(iter(shapes)) for label, shapes in shapes_by_label.items()}

    def execute(grid: Grid) -> Grid:
        return _exact_cover(grid, background, ink, templates, limits.max_cover_nodes)

    return [_proposal(
        "learned_polyomino_unique_exact_cover",
        {
            "background": background,
            "ink": ink,
            "templates": {str(label): [list(point) for point in templates[label]] for label in sorted(templates)},
            "solution_policy": "unique",
        },
        execute,
        7 + sum(len(shape) for shape in templates.values()),
        decomposition_unique=True,
        template_occurrences=sum(len(_components({(r, c) for r in range(len(target)) for c in range(len(target[0])) if target[r][c] == label})) for _, target in train for label in templates),
    )]


def _right_parity_recolor_proposals(train: Sequence[tuple[Grid, Grid]]) -> list[Proposal]:
    common = set.intersection(*(_palette(source) for source, _ in train))
    result: list[Proposal] = []
    for ink in sorted(common):
        changed_colors = {
            target[row][column]
            for source, target in train
            for row in range(len(source))
            for column in range(len(source[0]))
            if source[row][column] == ink and target[row][column] != ink
        }
        if len(changed_colors) != 1:
            continue
        replacement = next(iter(changed_colors))
        for phase in (0, 1):
            def execute(grid: Grid, ink: int = ink, replacement: int = replacement, phase: int = phase) -> Grid:
                height, width = _shape(grid)
                background = _mode(grid)
                output = _copy(grid)
                for column in range(width):
                    rows = [row for row in range(height) if grid[row][column] == ink]
                    if len(rows) != 1:
                        raise ValueError("not one ink per column")
                    if (width - 1 - column) % 2 == phase:
                        output[rows[0]][column] = replacement
                if any(grid[row][column] not in {background, ink} for row in range(height) for column in range(width)):
                    raise ValueError("unexpected palette")
                return output
            result.append(_proposal(
                "right_anchored_alternating_column_recolor",
                {"ink": ink, "replacement": replacement, "phase": phase},
                execute,
                4,
                period=2,
            ))
    return result


def _triangular_ca_proposals(train: Sequence[tuple[Grid, Grid]]) -> list[Proposal]:
    result: list[Proposal] = []
    backgrounds = {_mode(source) for source, _ in train}
    if len(backgrounds) != 1:
        return result
    background = next(iter(backgrounds))
    mapping: dict[int, int] = {}
    valid = True
    for source, target in train:
        height, width = _shape(source)
        if any(source[row][column] != background for row in range(1, height) for column in range(width)):
            valid = False
            break
        for row in range(1, height):
            previous = target[row - 1]
            for column in range(width):
                parents_active = 0 < column < width - 1 and previous[column - 1] != background and previous[column + 1] != background
                if parents_active:
                    before = previous[column - 1]
                    after = target[row][column]
                    if after == background or (before in mapping and mapping[before] != after):
                        valid = False
                        break
                    mapping[before] = after
                elif target[row][column] != background:
                    valid = False
                    break
            if not valid:
                break
        if not valid:
            break
    if not valid or len(mapping) < 2:
        return result

    def execute(grid: Grid) -> Grid:
        height, width = _shape(grid)
        if any(grid[row][column] != background for row in range(1, height) for column in range(width)):
            raise ValueError("nonblank CA body")
        output = [[background] * width for _ in range(height)]
        output[0] = grid[0][:]
        for row in range(1, height):
            previous = output[row - 1]
            for column in range(1, width - 1):
                if previous[column - 1] != background and previous[column + 1] != background:
                    if previous[column - 1] not in mapping:
                        raise ValueError("unseen CA state")
                    output[row][column] = mapping[previous[column - 1]]
        return output

    result.append(_proposal(
        "triangular_two_parent_cellular_automaton",
        {"background": background, "left_parent_map": {str(key): mapping[key] for key in sorted(mapping)}},
        execute,
        5 + len(mapping),
        local_radius=1,
    ))
    return result


def _rotate_180_proposal() -> Proposal:
    return _proposal("whole_grid_rotate_180", {}, lambda grid: [row[::-1] for row in grid[::-1]], 1, rigid_motion=True)


def _roll_object_up_right_proposal() -> Proposal:
    """Half-turn the sole object and advance it by one own bounding box up/right."""

    def execute(grid: Grid) -> Grid:
        height, width = _shape(grid)
        background = _mode(grid)
        points = [(row, column) for row in range(height) for column in range(width) if grid[row][column] != background]
        if not points:
            raise ValueError("no object")
        top = min(row for row, _ in points)
        bottom = max(row for row, _ in points)
        left = min(column for _, column in points)
        right = max(column for _, column in points)
        box_height = bottom - top + 1
        box_width = right - left + 1
        new_top = max(0, top - (box_height - 1))
        new_left = min(width - box_width, left + (box_width - 1))
        output = [[background] * width for _ in range(height)]
        for row, column in points:
            rr = new_top + (bottom - row)
            cc = new_left + (right - column)
            output[rr][cc] = grid[row][column]
        return output

    return _proposal(
        "half_turn_object_then_advance_up_right",
        {"step": "own_bbox_minus_one", "clip_translation": True},
        execute,
        5,
        object_rigid=True,
    )


def _vertical_extrema_proposals(train: Sequence[tuple[Grid, Grid]]) -> list[Proposal]:
    common_inks: set[int] | None = None
    for source, _ in train:
        background = _mode(source)
        colors = _palette(source) - {background}
        common_inks = colors if common_inks is None else common_inks & colors
    result: list[Proposal] = []
    for ink in sorted(common_inks or ()):
        maximum_labels: set[int] = set()
        minimum_labels: set[int] = set()
        valid = True
        for source, target in train:
            height, width = _shape(source)
            background = _mode(source)
            bars = {column: [row for row in range(height) if source[row][column] == ink] for column in range(width)}
            bars = {column: rows for column, rows in bars.items() if rows}
            if len(bars) < 3 or any(rows != list(range(min(rows), max(rows) + 1)) for rows in bars.values()):
                valid = False
                break
            lengths = {column: len(rows) for column, rows in bars.items()}
            maxima = [column for column, length in lengths.items() if length == max(lengths.values())]
            minima = [column for column, length in lengths.items() if length == min(lengths.values())]
            if len(maxima) != 1 or len(minima) != 1:
                valid = False
                break
            maximum_labels.update(target[row][maxima[0]] for row in bars[maxima[0]])
            minimum_labels.update(target[row][minima[0]] for row in bars[minima[0]])
        if not valid or len(maximum_labels) != 1 or len(minimum_labels) != 1:
            continue
        maximum_label = next(iter(maximum_labels))
        minimum_label = next(iter(minimum_labels))

        def execute(grid: Grid, ink: int = ink, maximum_label: int = maximum_label, minimum_label: int = minimum_label) -> Grid:
            height, width = _shape(grid)
            background = _mode(grid)
            bars = {column: [row for row in range(height) if grid[row][column] == ink] for column in range(width)}
            bars = {column: rows for column, rows in bars.items() if rows}
            if any(rows != list(range(min(rows), max(rows) + 1)) for rows in bars.values()):
                raise ValueError("noncontiguous vertical bars")
            lengths = {column: len(rows) for column, rows in bars.items()}
            maxima = [column for column, length in lengths.items() if length == max(lengths.values())]
            minima = [column for column, length in lengths.items() if length == min(lengths.values())]
            if len(maxima) != 1 or len(minima) != 1:
                raise ValueError("bar extrema are tied")
            output = [[background] * width for _ in range(height)]
            for row in bars[maxima[0]]:
                output[row][maxima[0]] = maximum_label
            for row in bars[minima[0]]:
                output[row][minima[0]] = minimum_label
            return output

        result.append(_proposal(
            "vertical_bar_length_extrema",
            {"ink": ink, "maximum_label": maximum_label, "minimum_label": minimum_label},
            execute,
            5,
            ordinal_only=True,
        ))
    return result


def _signed_bar_arithmetic_proposals(train: Sequence[tuple[Grid, Grid]]) -> list[Proposal]:
    """Append a bottom-aligned bar whose height is a signed sum of prior bar heights."""

    records: list[tuple[list[tuple[int, int, int]], int, int]] = []
    input_colors: set[int] = set()
    paint_colors: set[int] = set()
    for source, target in train:
        height, width = _shape(source)
        background = _mode(source)
        bars: list[tuple[int, int, int]] = []
        for column in range(width):
            rows = [row for row in range(height) if source[row][column] != background]
            if not rows:
                continue
            values = {source[row][column] for row in rows}
            if len(values) != 1 or rows != list(range(height - len(rows), height)):
                return []
            color = next(iter(values))
            bars.append((column, color, len(rows)))
            input_colors.add(color)
        if len(bars) < 2:
            return []
        gaps = [right[0] - left[0] for left, right in zip(bars, bars[1:])]
        if not gaps or len(set(gaps)) != 1:
            return []
        next_column = bars[-1][0] + gaps[0]
        if not 0 <= next_column < width:
            return []
        changes = [
            (row, column, target[row][column])
            for row in range(height)
            for column in range(width)
            if source[row][column] != target[row][column]
        ]
        if not changes or {column for _, column, _ in changes} != {next_column}:
            return []
        paint = {color for _, _, color in changes}
        if len(paint) != 1:
            return []
        paint_color = next(iter(paint))
        changed_rows = [row for row, _, _ in changes]
        if changed_rows != list(range(height - len(changed_rows), height)):
            return []
        paint_colors.add(paint_color)
        records.append((bars, next_column, len(changed_rows)))
    if len(paint_colors) != 1 or not input_colors:
        return []
    paint = next(iter(paint_colors))
    result: list[Proposal] = []
    colors = sorted(input_colors)
    for signs_tuple in itertools.product((-1, 1), repeat=len(colors)):
        signs = dict(zip(colors, signs_tuple))
        if not all(sum(signs[color] * bar_height for _, color, bar_height in bars) == result_height for bars, _, result_height in records):
            continue

        def execute(grid: Grid, signs: dict[int, int] = signs, paint: int = paint) -> Grid:
            height, width = _shape(grid)
            background = _mode(grid)
            bars: list[tuple[int, int, int]] = []
            for column in range(width):
                rows = [row for row in range(height) if grid[row][column] != background]
                if not rows:
                    continue
                values = {grid[row][column] for row in rows}
                if len(values) != 1 or rows != list(range(height - len(rows), height)):
                    raise ValueError("not bottom-aligned monochrome bars")
                color = next(iter(values))
                if color not in signs:
                    raise ValueError("unseen arithmetic bar color")
                bars.append((column, color, len(rows)))
            gaps = [right[0] - left[0] for left, right in zip(bars, bars[1:])]
            if len(bars) < 2 or not gaps or len(set(gaps)) != 1:
                raise ValueError("bar spacing is not regular")
            next_column = bars[-1][0] + gaps[0]
            result_height = sum(signs[color] * bar_height for _, color, bar_height in bars)
            if not (0 < result_height <= height and 0 <= next_column < width):
                raise ValueError("arithmetic result does not fit")
            output = _copy(grid)
            for row in range(height - result_height, height):
                if output[row][next_column] != background:
                    raise ValueError("result bar collides")
                output[row][next_column] = paint
            return output

        result.append(_proposal(
            "signed_vertical_bar_arithmetic",
            {"signs": {str(color): signs[color] for color in colors}, "paint": paint, "placement": "next_regular_column"},
            execute,
            6 + len(signs),
            bar_height_arithmetic=True,
        ))
    return result


def _pack_to_divider_proposals(train: Sequence[tuple[Grid, Grid]]) -> list[Proposal]:
    result: list[Proposal] = []
    for orientation, side in itertools.product(("vertical", "horizontal"), ("low", "high")):
        def execute(grid: Grid, orientation: str = orientation, side: str = side) -> Grid:
            height, width = _shape(grid)
            background = _mode(grid)
            if orientation == "vertical":
                index = 0 if side == "low" else width - 1
                values = {grid[row][index] for row in range(height)}
                if len(values) != 1:
                    raise ValueError("no uniform vertical divider")
                divider = next(iter(values))
                if divider == background:
                    raise ValueError("divider is background")
                output = [[background] * width for _ in range(height)]
                for row in range(height):
                    output[row][index] = divider
                movement = (0, -1 if side == "low" else 1)
            else:
                index = 0 if side == "low" else height - 1
                values = set(grid[index])
                if len(values) != 1:
                    raise ValueError("no uniform horizontal divider")
                divider = next(iter(values))
                if divider == background:
                    raise ValueError("divider is background")
                output = [[background] * width for _ in range(height)]
                output[index] = [divider] * width
                movement = (-1 if side == "low" else 1, 0)

            # Preserve each monochrome object's geometry.  Nearest objects settle
            # first, so farther objects stop against them just as stable gravity.
            pieces: list[list[tuple[int, int, int]]] = []
            for color in sorted(_palette(grid) - {background, divider}):
                points = {
                    (row, column)
                    for row in range(height)
                    for column in range(width)
                    if grid[row][column] == color
                }
                for component in _components(points):
                    pieces.append([(row, column, color) for row, column in sorted(component)])
            if not pieces:
                raise ValueError("no objects to pack")
            if orientation == "vertical" and side == "low":
                pieces.sort(key=lambda piece: min(column for _, column, _ in piece))
            elif orientation == "vertical":
                pieces.sort(key=lambda piece: -max(column for _, column, _ in piece))
            elif side == "low":
                pieces.sort(key=lambda piece: min(row for row, _, _ in piece))
            else:
                pieces.sort(key=lambda piece: -max(row for row, _, _ in piece))

            dr, dc = movement
            occupied = {
                (row, column)
                for row in range(height)
                for column in range(width)
                if output[row][column] != background
            }
            for piece in pieces:
                current = piece
                while True:
                    shifted = [(row + dr, column + dc, color) for row, column, color in current]
                    if any(
                        not (0 <= row < height and 0 <= column < width)
                        or (row, column) in occupied
                        for row, column, _ in shifted
                    ):
                        break
                    current = shifted
                for row, column, color in current:
                    output[row][column] = color
                    occupied.add((row, column))
            return output
        result.append(_proposal(
            "stable_pack_toward_uniform_divider",
            {"orientation": orientation, "side": side},
            execute,
            4,
            stable_order=True,
        ))
    return result


def _auto_pack_to_divider_proposal() -> Proposal:
    def execute(grid: Grid) -> Grid:
        height, width = _shape(grid)
        background = _mode(grid)
        choices: list[tuple[str, str]] = []
        for side, column in (("low", 0), ("high", width - 1)):
            values = {grid[row][column] for row in range(height)}
            if len(values) == 1 and next(iter(values)) != background:
                choices.append(("vertical", side))
        for side, row in (("low", 0), ("high", height - 1)):
            values = set(grid[row])
            if len(values) == 1 and next(iter(values)) != background:
                choices.append(("horizontal", side))
        if len(choices) != 1:
            raise ValueError("not one nonbackground edge divider")
        orientation, side = choices[0]
        matching = next(
            proposal
            for proposal in _pack_to_divider_proposals(())
            if proposal.parameters == {"orientation": orientation, "side": side}
        )
        return matching.execute(grid)

    return _proposal(
        "stable_object_pack_toward_detected_edge_divider",
        {"divider_selection": "unique_uniform_nonbackground_edge"},
        execute,
        5,
        stable_order=True,
        object_geometry_preserved=True,
    )


def _longest_diagonal_proposals() -> list[Proposal]:
    result: list[Proposal] = []
    for slope in (-1, 1):
        def execute(grid: Grid, slope: int = slope) -> Grid:
            height, width = _shape(grid)
            background = _mode(grid)
            segments: list[tuple[int, tuple[tuple[int, int], ...]]] = []
            for row in range(height):
                for column in range(width):
                    color = grid[row][column]
                    if color == background:
                        continue
                    previous = (row - 1, column - slope)
                    if 0 <= previous[0] < height and 0 <= previous[1] < width and grid[previous[0]][previous[1]] == color:
                        continue
                    points: list[tuple[int, int]] = []
                    rr, cc = row, column
                    while 0 <= rr < height and 0 <= cc < width and grid[rr][cc] == color:
                        points.append((rr, cc))
                        rr += 1
                        cc += slope
                    if len(points) >= 2:
                        segments.append((color, tuple(points)))
            if not segments:
                raise ValueError("no diagonal segment")
            longest = max(len(points) for _, points in segments)
            winners = [(color, points) for color, points in segments if len(points) == longest]
            if len(winners) != 1:
                raise ValueError("longest diagonal tied")
            color, points = winners[0]
            output = [[background] * width for _ in range(height)]
            for row, column in points:
                output[row][column] = color
            return output
        result.append(_proposal(
            "retain_unique_longest_monochrome_diagonal",
            {"slope": slope},
            execute,
            4,
            ordinal_selection=True,
        ))
    return result


def _center_color_diagonal_ray_proposal() -> Proposal:
    def execute(grid: Grid) -> Grid:
        height, width = _shape(grid)
        if height % 2 == 0 or width % 2 == 0:
            raise ValueError("no central cell")
        background = _mode(grid)
        center_row, center_column = height // 2, width // 2
        color = grid[center_row][center_column]
        if color == background:
            raise ValueError("center is background")
        scored: list[tuple[int, int, int, tuple[tuple[int, int], ...]]] = []
        for dr, dc in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
            points: list[tuple[int, int]] = []
            row, column = center_row, center_column
            while 0 <= row < height and 0 <= column < width:
                points.append((row, column))
                row += dr
                column += dc
            support = sum(grid[row][column] == color for row, column in points)
            scored.append((support, dr, dc, tuple(points)))
        best_support = max(item[0] for item in scored)
        winners = [item for item in scored if item[0] == best_support]
        if best_support < 2 or len(winners) != 1:
            raise ValueError("diagonal direction is unsupported or tied")
        points = winners[0][3]
        output = [[background] * width for _ in range(height)]
        for row, column in points:
            output[row][column] = color
        return output

    return _proposal(
        "extend_center_color_along_best_supported_diagonal_ray",
        {"origin": "grid_center", "selection": "same_color_support"},
        execute,
        4,
        ordinal_selection=True,
    )


def _compact_mover_proposals(train: Sequence[tuple[Grid, Grid]]) -> list[Proposal]:
    common = set.intersection(*(_palette(source) for source, _ in train))
    result: list[Proposal] = []
    for mover in sorted(common):
        def execute(grid: Grid, mover: int = mover) -> Grid:
            height, width = _shape(grid)
            background = _mode(grid)
            if mover == background:
                raise ValueError("mover is background")
            output = [[background if cell == mover else cell for cell in row] for row in grid]
            moved = 0
            for row in range(height):
                count = sum(cell == mover for cell in grid[row])
                if not count:
                    continue
                moved += count
                obstacles = [column for column in range(width) if grid[row][column] not in {background, mover}]
                start = max(obstacles) + 1 if obstacles else 0
                if start + count > width or any(output[row][column] != background for column in range(start, start + count)):
                    raise ValueError("mover does not fit")
                for column in range(start, start + count):
                    output[row][column] = mover
            if not moved:
                raise ValueError("no movers")
            return output
        result.append(_proposal(
            "row_compact_mover_after_rightmost_obstacle",
            {"mover": mover},
            execute,
            3,
            row_local=True,
        ))
    return result


def _bracket_fill_proposal() -> Proposal:
    def execute(grid: Grid) -> Grid:
        height, width = _shape(grid)
        background = _mode(grid)
        colors = _palette(grid) - {background}
        if len(colors) != 1:
            raise ValueError("not a monochrome boundary")
        ink = next(iter(colors))
        active_rows = [row for row in range(height) if any(grid[row][column] == ink for column in range(width))]
        if len(active_rows) < 3 or active_rows != list(range(min(active_rows), max(active_rows) + 1)):
            raise ValueError("boundary rows are not contiguous")
        first, last = min(active_rows), max(active_rows)
        output = [[background] * width for _ in range(height)]
        for row in range(first + 1, last):
            columns = [column for column in range(width) if grid[row][column] == ink]
            if not columns:
                raise ValueError("missing boundary point")
            left = max(columns)
            right = width - 1 - left
            lo, hi = sorted((left, right))
            if hi - lo == 1:
                targets = range(lo, hi + 1)
            else:
                targets = range(lo + 1, hi)
            for column in targets:
                output[row][column] = ink
        return output
    return _proposal(
        "mirror_boundary_and_fill_strict_interior",
        {"axis": "vertical_grid_center", "exclude_endpoint_rows": True},
        execute,
        5,
        shape_completion=True,
    )


def _panel_fill_proposals(train: Sequence[tuple[Grid, Grid]]) -> list[Proposal]:
    # Infer a literal marker-to-fill map; geometry and separators remain dynamic.
    mappings: dict[int, int] = {}
    valid = True

    def partition(grid: Grid) -> tuple[int, int, list[int], list[int], list[tuple[range, range]]]:
        height, width = _shape(grid)
        background = _mode(grid)
        row_lines: dict[int, list[int]] = defaultdict(list)
        col_lines: dict[int, list[int]] = defaultdict(list)
        for row in range(height):
            if len(set(grid[row])) == 1 and grid[row][0] != background:
                row_lines[grid[row][0]].append(row)
        for column in range(width):
            values = {grid[row][column] for row in range(height)}
            if len(values) == 1 and next(iter(values)) != background:
                col_lines[next(iter(values))].append(column)
        candidates = set(row_lines) | set(col_lines)
        if len(candidates) != 1:
            raise ValueError("not one separator color")
        separator = next(iter(candidates))
        rows = row_lines.get(separator, [])
        columns = col_lines.get(separator, [])
        row_bounds = [-1] + rows + [height]
        col_bounds = [-1] + columns + [width]
        regions = [
            (range(row_bounds[i] + 1, row_bounds[i + 1]), range(col_bounds[j] + 1, col_bounds[j + 1]))
            for i in range(len(row_bounds) - 1)
            for j in range(len(col_bounds) - 1)
        ]
        return background, separator, rows, columns, regions

    for source, target in train:
        try:
            background, separator, rows, columns, regions = partition(source)
        except ValueError:
            valid = False
            break
        if _shape(source) != _shape(target):
            valid = False
            break
        for row in rows:
            if target[row] != source[row]:
                valid = False
        for column in columns:
            if any(target[row][column] != separator for row in range(len(source))):
                valid = False
        for row_range, column_range in regions:
            points = [(row, column) for row in row_range for column in column_range]
            if not points:
                continue
            markers = {source[row][column] for row, column in points} - {background}
            fills = {target[row][column] for row, column in points}
            if len(markers) != 1 or len(fills) != 1:
                valid = False
                break
            marker = next(iter(markers))
            fill = next(iter(fills))
            if marker in mappings and mappings[marker] != fill:
                valid = False
                break
            mappings[marker] = fill
        if not valid:
            break
    if not valid or len(mappings) < 2:
        return []

    def execute(grid: Grid) -> Grid:
        background, separator, rows, columns, regions = partition(grid)
        output = _copy(grid)
        for row_range, column_range in regions:
            points = [(row, column) for row in row_range for column in column_range]
            if not points:
                continue
            markers = {grid[row][column] for row, column in points} - {background}
            if len(markers) != 1:
                raise ValueError("panel does not contain one marker role")
            marker = next(iter(markers))
            if marker not in mappings:
                raise ValueError("unseen panel marker")
            for row, column in points:
                output[row][column] = mappings[marker]
        for row in rows:
            output[row] = [separator] * len(output[row])
        for column in columns:
            for row in range(len(output)):
                output[row][column] = separator
        return output

    return [_proposal(
        "separator_panel_uniform_fill",
        {"marker_to_fill": {str(key): mappings[key] for key in sorted(mappings)}},
        execute,
        5 + len(mappings),
        partition_relational=True,
    )]


def _cyclic_panel_fill_proposal() -> Proposal:
    def execute(grid: Grid) -> Grid:
        height, width = _shape(grid)
        background = _mode(grid)
        separators = [
            column
            for column in range(width)
            if all(grid[row][column] == background for row in range(height))
        ]
        if len(separators) < 2:
            raise ValueError("fewer than two background separators")
        bounds = [-1] + separators + [width]
        panels = [(bounds[index] + 1, bounds[index + 1]) for index in range(len(bounds) - 1)]
        panels = [(left, right) for left, right in panels if left < right]
        if len(panels) < 3:
            raise ValueError("fewer than three nonempty panels")
        colors: list[int] = []
        for left, right in panels:
            foreground = {
                grid[row][column]
                for row in range(height)
                for column in range(left, right)
                if grid[row][column] != background
            }
            if len(foreground) != 1:
                raise ValueError("panel does not have one foreground role")
            colors.append(next(iter(foreground)))
        if len(set(colors)) != len(colors):
            raise ValueError("panel roles are not distinct")
        output = _copy(grid)
        for index, (left, right) in enumerate(panels):
            fill = colors[(index + 1) % len(colors)]
            for row in range(height):
                for column in range(left, right):
                    if output[row][column] == background:
                        output[row][column] = fill
        return output

    return _proposal(
        "cyclic_next_panel_color_background_fill",
        {"partition": "full_background_columns"},
        execute,
        5,
        panel_role_cycle=True,
    )


def _wall_region_bipartite_proposals(train: Sequence[tuple[Grid, Grid]]) -> list[Proposal]:
    common = set.intersection(*(_palette(source) for source, _ in train))
    result: list[Proposal] = []
    for wall in sorted(common):
        root_labels: set[int] = set()
        alternate_labels: set[int] = set()

        def analyze(grid: Grid, wall: int = wall) -> tuple[int, list[set[tuple[int, int]]], dict[tuple[int, int], int], dict[int, int]]:
            height, width = _shape(grid)
            others = _palette(grid) - {wall}
            if len(others) != 1:
                raise ValueError("input is not one wall plus one background")
            background = next(iter(others))
            points = {(row, column) for row in range(height) for column in range(width) if grid[row][column] == background}
            components = _components(points)
            owner = {point: index for index, component in enumerate(components) for point in component}
            if (height - 1, 0) not in owner:
                raise ValueError("bottom-left background anchor absent")
            edges: set[tuple[int, int]] = set()
            for row in range(height):
                for column in range(width):
                    if grid[row][column] != wall:
                        continue
                    neighbors = {
                        owner[(rr, cc)]
                        for dr, dc in ((-1, 0), (0, -1), (0, 1), (1, 0))
                        if 0 <= (rr := row + dr) < height
                        and 0 <= (cc := column + dc) < width
                        and (rr, cc) in owner
                    }
                    for first in neighbors:
                        for second in neighbors:
                            if first < second:
                                edges.add((first, second))
            adjacency: dict[int, set[int]] = defaultdict(set)
            for first, second in edges:
                adjacency[first].add(second)
                adjacency[second].add(first)
            root = owner[(height - 1, 0)]
            parity = {root: 0}
            queue = deque([root])
            while queue:
                current = queue.popleft()
                for neighbor in sorted(adjacency[current]):
                    expected = 1 - parity[current]
                    if neighbor in parity and parity[neighbor] != expected:
                        raise ValueError("region graph is not bipartite")
                    if neighbor not in parity:
                        parity[neighbor] = expected
                        queue.append(neighbor)
            if len(parity) != len(components):
                raise ValueError("region graph is disconnected")
            return background, components, owner, parity

        valid = True
        for source, target in train:
            try:
                _, components, _, parity = analyze(source)
            except ValueError:
                valid = False
                break
            for index, component in enumerate(components):
                labels = {target[row][column] for row, column in component}
                if len(labels) != 1:
                    valid = False
                    break
                label = next(iter(labels))
                (root_labels if parity[index] == 0 else alternate_labels).add(label)
            if any(
                source[row][column] == wall and target[row][column] != wall
                for row in range(len(source))
                for column in range(len(source[0]))
            ):
                valid = False
            if not valid:
                break
        if not valid or len(root_labels) != 1 or len(alternate_labels) != 1 or root_labels == alternate_labels:
            continue
        root_label = next(iter(root_labels))
        alternate_label = next(iter(alternate_labels))

        def execute(
            grid: Grid,
            wall: int = wall,
            root_label: int = root_label,
            alternate_label: int = alternate_label,
            analyze_fn: Callable[[Grid], tuple[int, list[set[tuple[int, int]]], dict[tuple[int, int], int], dict[int, int]]] = analyze,
        ) -> Grid:
            _, components, _, parity = analyze_fn(grid)
            output = _copy(grid)
            for index, component in enumerate(components):
                label = root_label if parity[index] == 0 else alternate_label
                for row, column in component:
                    output[row][column] = label
            return output

        result.append(_proposal(
            "bipartite_wall_region_coloring",
            {"wall": wall, "root_corner": "bottom_left", "root_label": root_label, "alternate_label": alternate_label},
            execute,
            7,
            region_adjacency=True,
        ))
    return result


def _periodic_column_proposals(train: Sequence[tuple[Grid, Grid]]) -> list[Proposal]:
    heights = {len(source) for source, _ in train}
    widths = {len(source[0]) for source, _ in train}
    if len(heights) != 1 or len(widths) < 2 or len(train) < 3:
        return []
    height = next(iter(heights))
    result: list[Proposal] = []
    for period in range(1, 17):
        input_template: dict[int, tuple[int, ...]] = {}
        output_template: dict[int, tuple[int, ...]] = {}
        valid = True
        for source, target in train:
            if _shape(source) != _shape(target):
                valid = False
                break
            width = len(source[0])
            for column in range(width):
                phase = column % period
                before = tuple(source[row][column] for row in range(height))
                after = tuple(target[row][column] for row in range(height))
                if phase in input_template and input_template[phase] != before:
                    valid = False
                    break
                if phase in output_template and output_template[phase] != after:
                    valid = False
                    break
                input_template[phase] = before
                output_template[phase] = after
            if not valid:
                break
        if not valid or len(input_template) != period or len(output_template) != period or period >= max(widths):
            continue

        def execute(
            grid: Grid,
            period: int = period,
            input_template: dict[int, tuple[int, ...]] = input_template,
            output_template: dict[int, tuple[int, ...]] = output_template,
        ) -> Grid:
            if len(grid) != height:
                raise ValueError("periodic strip height changed")
            width = len(grid[0])
            for column in range(width):
                if tuple(grid[row][column] for row in range(height)) != input_template[column % period]:
                    raise ValueError("test is not the learned periodic strip")
            return [[output_template[column % period][row] for column in range(width)] for row in range(height)]

        result.append(_proposal(
            "one_dimensional_periodic_column_transducer",
            {
                "period": period,
                "input_columns": [list(input_template[index]) for index in range(period)],
                "output_columns": [list(output_template[index]) for index in range(period)],
            },
            execute,
            6 + 2 * period,
            independent_widths=len(widths),
            periodic=True,
        ))
        break
    return result


def _periodic_border_run_proposal() -> Proposal:
    def perimeter(height: int, width: int) -> list[tuple[int, int]]:
        if height < 2 or width < 2:
            raise ValueError("degenerate perimeter")
        points = [(0, column) for column in range(width)]
        points += [(row, width - 1) for row in range(1, height)]
        points += [(height - 1, column) for column in range(width - 2, -1, -1)]
        points += [(row, 0) for row in range(height - 2, 0, -1)]
        return points

    def execute(grid: Grid) -> Grid:
        height, width = _shape(grid)
        background = _mode(grid)
        border = perimeter(height, width)
        border_index = {point: index for index, point in enumerate(border)}
        ink_points = [(row, column) for row in range(height) for column in range(width) if grid[row][column] != background]
        if not ink_points or any(point not in border_index for point in ink_points):
            raise ValueError("ink is not confined to the border")
        colors = {grid[row][column] for row, column in ink_points}
        if len(colors) != 1:
            raise ValueError("border run is not monochrome")
        color = next(iter(colors))
        indices = {border_index[point] for point in ink_points}
        length = len(indices)
        starts = [
            start
            for start in sorted(indices)
            if {(start + offset) % len(border) for offset in range(length)} == indices
        ]
        if len(starts) != 1:
            raise ValueError("border seed is not one cyclic run")
        start = starts[0]
        output = [[background] * width for _ in range(height)]
        for index, (row, column) in enumerate(border):
            if (index - start) % (2 * length) < length:
                output[row][column] = color
        return output

    return _proposal(
        "repeat_monochrome_border_run_with_equal_gaps",
        {"period": "twice_seed_run"},
        execute,
        4,
        cyclic_border=True,
    )


def _all_proposals(train: Sequence[tuple[Grid, Grid]], limits: Limits) -> list[Proposal]:
    proposals: list[Proposal] = []
    proposals.extend(_central_axis_proposals(train))
    proposals.extend(_marker_component_proposals(train))
    proposals.append(_duplicate_component_consolidation_proposal())
    proposals.append(_quadrant_completion_proposal())
    proposals.extend(_rotational_panel_proposals())
    proposals.append(_top_zigzag_proposal())
    proposals.append(_project_2x2_proposal())
    proposals.append(_rightward_scan_proposal())
    proposals.append(_vertical_periodic_proposal())
    proposals.extend(_background_recolor_proposals())
    proposals.extend(_shift_foreground_recolor_proposals())
    proposals.extend(_manhattan_cycle_proposals(train))
    proposals.extend(_point_lattice_proposal(train))
    proposals.extend(_swirl_proposals())
    proposals.extend(_symmetry_recolor_proposals(train))
    proposals.extend(_edge_marker_fold_proposals(train))
    proposals.extend(_tiling_proposals(train, limits))
    proposals.extend(_right_parity_recolor_proposals(train))
    proposals.extend(_triangular_ca_proposals(train))
    proposals.append(_rotate_180_proposal())
    proposals.append(_roll_object_up_right_proposal())
    proposals.extend(_vertical_extrema_proposals(train))
    proposals.extend(_signed_bar_arithmetic_proposals(train))
    proposals.extend(_pack_to_divider_proposals(train))
    proposals.append(_auto_pack_to_divider_proposal())
    proposals.extend(_longest_diagonal_proposals())
    proposals.append(_center_color_diagonal_ray_proposal())
    proposals.extend(_compact_mover_proposals(train))
    proposals.append(_bracket_fill_proposal())
    proposals.extend(_panel_fill_proposals(train))
    proposals.append(_cyclic_panel_fill_proposal())
    proposals.extend(_wall_region_bipartite_proposals(train))
    proposals.extend(_periodic_column_proposals(train))
    proposals.append(_periodic_border_run_proposal())
    return proposals


def compile_task(task: Mapping[str, Any], limits: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    """Compile exact-demo same-shape candidates under a deterministic cap."""

    bounds = Limits.from_value(limits)
    if not isinstance(task, Mapping):
        return []
    try:
        raw_train = task["train"]
        raw_tests = task["test"]
        if not isinstance(raw_train, list) or not raw_train or not isinstance(raw_tests, list) or not raw_tests:
            return []
        train = [(_grid(example["input"], bounds), _grid(example["output"], bounds)) for example in raw_train]
        tests = [_grid(example["input"], bounds) for example in raw_tests]
    except (KeyError, TypeError, ValueError):
        return []
    if any(_shape(source) != _shape(target) for source, target in train):
        return []

    admitted: list[dict[str, Any]] = []
    for proposal in _all_proposals(train, bounds):
        try:
            train_outputs = [proposal.execute(source) for source, _ in train]
            if any(prediction != target for prediction, (_, target) in zip(train_outputs, train)):
                continue
            test_outputs = [proposal.execute(grid) for grid in tests]
            for output, source in zip(test_outputs, tests):
                if _shape(output) != _shape(source):
                    raise ValueError("schema changed shape")
                _grid(output, bounds)
        except (IndexError, KeyError, StopIteration, TypeError, ValueError):
            continue
        program = {"operator": proposal.operator, **proposal.parameters}
        admitted.append(
            {
                "family": "targeted_same_shape",
                "program": program,
                "train_outputs": train_outputs,
                "test_outputs": test_outputs,
                "complexity": int(proposal.complexity),
                "evidence": {
                    "all_demonstrations_exact": True,
                    "same_shape": True,
                    "bounded": True,
                    "task_identity_free": True,
                    **proposal.evidence,
                },
            }
        )

    admitted.sort(
        key=lambda item: (
            item["complexity"],
            json.dumps(item["program"], sort_keys=True, separators=(",", ":")),
        )
    )
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for candidate in admitted:
        behavior = json.dumps(candidate["test_outputs"], separators=(",", ":"), sort_keys=True)
        if behavior in seen:
            continue
        seen.add(behavior)
        result.append(candidate)
        if len(result) >= max(0, bounds.max_candidates):
            break
    return result


__all__ = ["Limits", "compile_task"]
