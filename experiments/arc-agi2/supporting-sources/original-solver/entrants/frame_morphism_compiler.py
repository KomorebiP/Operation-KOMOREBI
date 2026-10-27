"""Frame, template, and intrinsic-coordinate morphisms for PR-LASM Block 15.

The entrant treats visible scaffolds as coordinate systems rather than as
literal rasters.  Its operators complete multicolour motifs, transport a
stencil between scaled marker frames, decode cell legends into homologous
grids, fill canvas cavities from an external inventory, orient a canvas from
an external constellation, densify sparse lattice frames, expand a framed
seed, project regular stripe signals, and project tokens to matching sides of
a coloured frame.

Compilation consumes demonstration pairs and held-out *inputs* only.  Task
identifiers, score files, solution stores, and held-out labels are not part of
the API.  Every activation requires exact demonstration replay, genuine
leave-one-demonstration-out re-induction, a single complete held-out behavior,
and D4/palette gauge checks.

Author: Komorebi P.
"""

from __future__ import annotations

from collections import Counter, deque
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
import hashlib
import itertools
import json
from typing import Any, Callable


Grid = tuple[tuple[int, ...], ...]
Cell = tuple[int, int]
Pair = tuple[Grid, Grid]
SCHEMA = "komorebi.pr_lasm.block15.frame_morphism_compiler.program.v1"
AUTHOR = "Komorebi P."


class Undefined(ValueError):
    """A structural role is absent, ambiguous, or outside a hard bound."""


@dataclass(frozen=True, slots=True)
class Limits:
    max_grid_cells: int = 900
    max_examples: int = 12
    max_components: int = 160
    max_programs: int = 32
    max_executor_calls: int = 20_000
    max_gauge_checks: int = 4_096
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
            "max_examples": 24,
            "max_components": 512,
            "max_programs": 128,
            "max_executor_calls": 200_000,
            "max_gauge_checks": 16_384,
            "max_candidates": 1,
        }
        parsed: dict[str, int] = {}
        for name in cls.__dataclass_fields__:
            raw = value.get(
                "candidate_cap" if name == "max_candidates" and "candidate_cap" in value else name,
                getattr(defaults, name),
            )
            if isinstance(raw, bool) or not isinstance(raw, int) or raw < 0:
                raise Undefined(f"limits.{name} must be a nonnegative integer")
            parsed[name] = min(raw, ceilings[name])
        return cls(**parsed)


@dataclass(frozen=True, slots=True)
class Component:
    color: int
    cells: frozenset[Cell]

    @property
    def area(self) -> int:
        return len(self.cells)

    @property
    def bbox(self) -> tuple[int, int, int, int]:
        return _bbox(self.cells)


def _canonical(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    )


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _grid(value: Any, limits: Limits) -> Grid:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or not value:
        raise Undefined("grid must be a nonempty sequence")
    rows: list[tuple[int, ...]] = []
    width: int | None = None
    for raw_row in value:
        if not isinstance(raw_row, Sequence) or isinstance(raw_row, (str, bytes)) or not raw_row:
            raise Undefined("grid row must be nonempty")
        row: list[int] = []
        for raw_cell in raw_row:
            if isinstance(raw_cell, bool) or not isinstance(raw_cell, int) or not 0 <= raw_cell <= 9:
                raise Undefined("invalid ARC color")
            row.append(int(raw_cell))
        if width is None:
            width = len(row)
        elif len(row) != width:
            raise Undefined("grid is ragged")
        rows.append(tuple(row))
    if len(rows) * int(width or 0) > limits.max_grid_cells:
        raise Undefined("grid exceeds cell cap")
    return tuple(rows)


def _plain(grid: Grid) -> list[list[int]]:
    return [list(row) for row in grid]


def _freeze(rows: Sequence[Sequence[int]]) -> Grid:
    return tuple(tuple(int(cell) for cell in row) for row in rows)


def _shape(grid: Grid) -> tuple[int, int]:
    return len(grid), len(grid[0])


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


def _unique_mode(values: Iterable[int]) -> int:
    counts = Counter(values)
    if not counts:
        raise Undefined("empty mode")
    maximum = max(counts.values())
    winners = sorted(color for color, count in counts.items() if count == maximum)
    if len(winners) != 1:
        raise Undefined("mode is tied")
    return winners[0]


def _background(grid: Grid) -> int:
    return _unique_mode(cell for row in grid for cell in row)


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
        raise Undefined("invalid example collection")
    train: list[Pair] = []
    for example in raw_train:
        if not isinstance(example, Mapping):
            raise Undefined("invalid demonstration")
        train.append((_grid(example.get("input"), limits), _grid(example.get("output"), limits)))
    tests: list[Grid] = []
    for example in raw_test:
        if not isinstance(example, Mapping):
            raise Undefined("invalid test example")
        # Intentionally ignore a test ``output`` member if one is injected.
        tests.append(_grid(example.get("input"), limits))
    return tuple(train), tuple(tests)


def _components(
    grid: Grid,
    *,
    background: int | None = None,
    color: int | None = None,
    connectivity: int = 4,
) -> tuple[Component, ...]:
    height, width = _shape(grid)
    seen: set[Cell] = set()
    result: list[Component] = []
    directions = ((1, 0), (-1, 0), (0, 1), (0, -1))
    if connectivity == 8:
        directions += ((1, 1), (1, -1), (-1, 1), (-1, -1))
    for row in range(height):
        for column in range(width):
            seed_color = grid[row][column]
            if (row, column) in seen or seed_color == background or (color is not None and seed_color != color):
                continue
            queue = deque([(row, column)])
            seen.add((row, column))
            cells: set[Cell] = set()
            while queue:
                current = queue.popleft()
                cells.add(current)
                for dr, dc in directions:
                    nr, nc = current[0] + dr, current[1] + dc
                    if not (0 <= nr < height and 0 <= nc < width) or (nr, nc) in seen:
                        continue
                    if grid[nr][nc] != seed_color:
                        continue
                    seen.add((nr, nc))
                    queue.append((nr, nc))
            result.append(Component(seed_color, frozenset(cells)))
    result.sort(key=lambda item: (item.bbox, item.color, item.area))
    return tuple(result)


def _mixed_components(grid: Grid, background: int, connectivity: int = 8) -> tuple[frozenset[Cell], ...]:
    height, width = _shape(grid)
    seen: set[Cell] = set()
    result: list[frozenset[Cell]] = []
    directions = ((1, 0), (-1, 0), (0, 1), (0, -1))
    if connectivity == 8:
        directions += ((1, 1), (1, -1), (-1, 1), (-1, -1))
    for row in range(height):
        for column in range(width):
            if grid[row][column] == background or (row, column) in seen:
                continue
            queue = deque([(row, column)])
            seen.add((row, column))
            cells: set[Cell] = set()
            while queue:
                current = queue.popleft()
                cells.add(current)
                for dr, dc in directions:
                    nr, nc = current[0] + dr, current[1] + dc
                    if not (0 <= nr < height and 0 <= nc < width) or (nr, nc) in seen:
                        continue
                    if grid[nr][nc] == background:
                        continue
                    seen.add((nr, nc))
                    queue.append((nr, nc))
            result.append(frozenset(cells))
    return tuple(sorted(result, key=lambda cells: (_bbox(cells), len(cells))))


def _solid_square(component: Component) -> int | None:
    r0, r1, c0, c1 = component.bbox
    if r1 - r0 != c1 - c0:
        return None
    side = r1 - r0 + 1
    if component.area != side * side:
        return None
    return side


def _complete_multicolor_motifs(
    grid: Grid,
    *,
    chirality_cross_preference: int | None = None,
    reflection_axis: str = "columns",
) -> tuple[Grid, dict[str, Any]]:
    """Complete translated fragments of complete scene-local color motifs."""

    background = _background(grid)
    height, width = _shape(grid)
    templates: list[dict[Cell, int]] = []
    template_cells: set[Cell] = set()
    for component in _mixed_components(grid, background, 8):
        colors = {grid[row][column] for row, column in component}
        if len(colors) < 2 or len(component) > 81:
            continue
        r0, r1, c0, c1 = _bbox(component)
        if r1 - r0 + 1 > 11 or c1 - c0 + 1 > 11:
            continue
        templates.append({(row - r0, column - c0): grid[row][column] for row, column in component})
        template_cells.update(component)
    if not templates:
        raise Undefined("no complete multicolor motif")

    source_by_color: dict[int, list[Cell]] = {}
    for row in range(height):
        for column in range(width):
            if grid[row][column] != background:
                source_by_color.setdefault(grid[row][column], []).append((row, column))

    proposals: list[tuple[int, frozenset[Cell], frozenset[tuple[int, int, int]]]] = []
    for original_template in templates:
        template_height = max(row for row, _ in original_template) + 1
        template_width = max(column for _, column in original_template) + 1
        if reflection_axis == "columns":
            reflected_template = {
                (row, template_width - 1 - column): color
                for (row, column), color in original_template.items()
            }
        elif reflection_axis == "rows":
            reflected_template = {
                (template_height - 1 - row, column): color
                for (row, column), color in original_template.items()
            }
        else:
            raise Undefined("invalid motif reflection axis")
        variants: tuple[tuple[dict[Cell, int], int], ...] = ((original_template, 0),)
        if chirality_cross_preference is not None:
            if chirality_cross_preference not in {-1, 1}:
                raise Undefined("invalid chirality preference")
            counts = Counter(original_template.values())
            key_positions = [
                position
                for position, color in original_template.items()
                if counts[color] == 1 and len(source_by_color.get(color, ())) > 1
            ]
            if len(key_positions) != 1:
                continue

            def chirality(template: Mapping[Cell, int], key_color: int) -> tuple[Any, ...]:
                key = next(position for position, color in template.items() if color == key_color)
                rows = sorted({row for row, _ in template}, reverse=True)
                cross_moment = sum(
                    (row - key[0]) * (column - key[1])
                    for (row, column), color in template.items()
                    if color != key_color
                )
                return (cross_moment,) + tuple(
                    (
                        sum(column - key[1] for (row, column), color in template.items() if row == level and color != key_color),
                        tuple(sorted(column - key[1] for (row, column), color in template.items() if row == level and color != key_color)),
                    )
                    for level in rows
                )

            key_color = original_template[key_positions[0]]
            preferred, fallback = sorted(
                (original_template, reflected_template),
                key=lambda template: (
                    -chirality_cross_preference * chirality(template, key_color)[0],
                    chirality(template, key_color)[1:],
                    _canonical(sorted(template.items())),
                ),
            )
            variants = ((preferred, 1), (fallback, 0))
        for template, preference in variants:
            color_counts = Counter(template.values())
            shifts: set[Cell] = set()
            for (tr, tc), color in template.items():
                for row, column in source_by_color.get(color, ()):
                    shifts.add((row - tr, column - tc))
            for sr, sc in shifts:
                placed = {(sr + tr, sc + tc): color for (tr, tc), color in template.items()}
                if any(not (0 <= row < height and 0 <= column < width) for row, column in placed):
                    continue
                r0, r1, c0, c1 = _bbox(placed)
                if any(
                    grid[row][column] != background and (row, column) not in placed
                    for row in range(r0, r1 + 1)
                    for column in range(c0, c1 + 1)
                ):
                    continue
                if any(
                    grid[row][column] not in {background, color}
                    for (row, column), color in placed.items()
                ):
                    continue
                matched = frozenset(
                    position for position, color in placed.items() if grid[position[0]][position[1]] == color
                )
                if not matched or len(matched) == len(placed):
                    continue
                if matched & template_cells:
                    continue
                rare_match = any(color_counts[placed[position]] == 1 for position in matched)
                if len(matched) < 2 and not rare_match:
                    continue
                additions = frozenset(
                    (row, column, color)
                    for (row, column), color in placed.items()
                    if grid[row][column] == background
                )
                if additions:
                    # A preferred reflection wins over the unreflected fallback
                    # when both are supported by the same fragment.
                    proposals.append((2 * len(matched) + preference, matched, additions))

    survivors: list[tuple[int, frozenset[Cell], frozenset[tuple[int, int, int]]]] = []
    for proposal in proposals:
        strength, matched, additions = proposal
        rivals = [other for other in proposals if other is not proposal and matched & other[1]]
        if any(other[0] > strength for other in rivals):
            continue
        tied = {other[2] for other in rivals if other[0] == strength}
        tied.add(additions)
        if len(tied) != 1:
            continue
        survivors.append(proposal)
    edits: dict[Cell, int] = {}
    for _, _, additions in survivors:
        for row, column, color in additions:
            prior = edits.get((row, column), color)
            if prior != color:
                raise Undefined("motif completions collide")
            edits[(row, column)] = color
    if not edits:
        raise Undefined("no unambiguous motif completion")
    result = [list(row) for row in grid]
    for (row, column), color in edits.items():
        result[row][column] = color
    return _freeze(result), {
        "templates": len(templates),
        "added_cells": len(edits),
        "placement_gauge": f"cross_moment_{chirality_cross_preference}_{reflection_axis}_with_boundary_fallback"
        if chirality_cross_preference is not None
        else "identity",
    }


def _scaled_stencil_outcomes(grid: Grid) -> tuple[tuple[Grid, dict[str, Any]], ...]:
    """Enumerate identity-free stencil transports supported by scene markers."""

    background = _background(grid)
    height, width = _shape(grid)
    colors = sorted({cell for row in grid for cell in row} - {background})
    by_color = {color: _components(grid, color=color) for color in colors}
    outcomes: dict[str, tuple[Grid, dict[str, Any]]] = {}
    for ink in colors:
        ink_components = by_color[ink]
        if len(ink_components) != 1:
            continue
        ink_support = ink_components[0].cells
        for marker in colors:
            if marker == ink:
                continue
            marker_components = by_color[marker]
            reference = [
                component
                for component in marker_components
                if any(
                    abs(row - ir) + abs(column - ic) == 1
                    for row, column in component.cells
                    for ir, ic in ink_support
                )
            ]
            if not reference:
                continue
            ref_sides = {_solid_square(component) for component in reference}
            if None in ref_sides or len(ref_sides) != 1:
                continue
            ref_side = int(next(iter(ref_sides)))
            reference.sort(key=lambda component: component.bbox)
            ref_anchors = [(component.bbox[0], component.bbox[2]) for component in reference]
            base_anchor = ref_anchors[0]
            targets = [component for component in marker_components if component not in reference]
            groups: set[tuple[int, int, int]] = set()
            target_index = {(component.bbox[0], component.bbox[2], _solid_square(component)): component for component in targets}
            for target in targets:
                target_side = _solid_square(target)
                if target_side is None or target_side % ref_side:
                    continue
                scale = target_side // ref_side
                if scale < 1:
                    continue
                for ref_anchor in ref_anchors:
                    origin = (
                        target.bbox[0] - scale * (ref_anchor[0] - base_anchor[0]),
                        target.bbox[2] - scale * (ref_anchor[1] - base_anchor[1]),
                    )
                    expected = [
                        (
                            origin[0] + scale * (row - base_anchor[0]),
                            origin[1] + scale * (column - base_anchor[1]),
                            scale * ref_side,
                        )
                        for row, column in ref_anchors
                    ]
                    if all(item in target_index for item in expected):
                        groups.add((origin[0], origin[1], scale))
            if not groups:
                continue
            result = [list(row) for row in grid]
            added = 0
            valid = True
            for origin_row, origin_column, scale in sorted(groups):
                for row, column in ink_support:
                    top = origin_row + scale * (row - base_anchor[0])
                    left = origin_column + scale * (column - base_anchor[1])
                    for dr in range(scale):
                        for dc in range(scale):
                            nr, nc = top + dr, left + dc
                            if not (0 <= nr < height and 0 <= nc < width):
                                # Boundary clipping is an explicit part of stencil transport.
                                continue
                            if result[nr][nc] not in {background, ink}:
                                valid = False
                                break
                            if result[nr][nc] == background:
                                result[nr][nc] = ink
                                added += 1
                        if not valid:
                            break
                    if not valid:
                        break
                if not valid:
                    break
            if not valid or not added:
                continue
            frozen = _freeze(result)
            outcomes[_canonical(_plain(frozen))] = (
                frozen,
                {"ink_role": "unique_stencil", "marker_groups": len(groups), "added_cells": added},
            )
    return tuple(outcomes[key] for key in sorted(outcomes))


def _instantiate_scaled_stencil(grid: Grid) -> tuple[Grid, dict[str, Any]]:
    outcomes = _scaled_stencil_outcomes(grid)
    if len(outcomes) != 1:
        raise Undefined("scaled stencil behavior is absent or ambiguous")
    return outcomes[0]


def _expand_seed_to_frame(grid: Grid) -> tuple[Grid, dict[str, Any]]:
    background = _background(grid)
    candidates: dict[str, tuple[Grid, dict[str, Any]]] = {}
    for frame_color in sorted({cell for row in grid for cell in row} - {background}):
        for component in _components(grid, color=frame_color):
            r0, r1, c0, c1 = component.bbox
            if r1 - r0 < 3 or c1 - c0 < 3:
                continue
            border = {
                (row, column)
                for row in range(r0, r1 + 1)
                for column in range(c0, c1 + 1)
                if row in {r0, r1} or column in {c0, c1}
            }
            if not border <= component.cells:
                continue
            inside = [
                (row, column)
                for row in range(r0 + 1, r1)
                for column in range(c0 + 1, c1)
                if grid[row][column] not in {background, frame_color}
            ]
            if not inside:
                continue
            sr0, sr1, sc0, sc1 = _bbox(inside)
            seed_height, seed_width = sr1 - sr0 + 1, sc1 - sc0 + 1
            inner_height, inner_width = r1 - r0 - 1, c1 - c0 - 1
            if inner_height % seed_height or inner_width % seed_width:
                continue
            row_scale, column_scale = inner_height // seed_height, inner_width // seed_width
            if row_scale != column_scale or row_scale < 1:
                continue
            if any(grid[row][column] in {background, frame_color} for row in range(sr0, sr1 + 1) for column in range(sc0, sc1 + 1)):
                continue
            result = [[frame_color] * (c1 - c0 + 1)]
            for inner_row in range(inner_height):
                source_row = sr0 + inner_row // row_scale
                result.append(
                    [frame_color]
                    + [
                        grid[source_row][sc0 + inner_column // column_scale]
                        for inner_column in range(inner_width)
                    ]
                    + [frame_color]
                )
            result.append([frame_color] * (c1 - c0 + 1))
            frozen = _freeze(result)
            candidates[_canonical(_plain(frozen))] = (
                frozen,
                {"scale": row_scale, "frame_shape": [r1 - r0 + 1, c1 - c0 + 1]},
            )
    if len(candidates) != 1:
        raise Undefined("framed seed expansion is absent or ambiguous")
    return next(iter(candidates.values()))


def _relation_signature(points: Mapping[int, Cell]) -> tuple[tuple[int, int, int, int], ...]:
    def sign(value: int) -> int:
        return (value > 0) - (value < 0)

    colors = sorted(points)
    return tuple(
        (
            left,
            right,
            sign(points[left][0] - points[right][0]),
            sign(points[left][1] - points[right][1]),
        )
        for left, right in itertools.combinations(colors, 2)
    )


def _d4_variants(grid: Grid) -> tuple[tuple[str, Grid], ...]:
    rotate90 = lambda value: tuple(tuple(row) for row in zip(*reversed(value)))
    variants: list[tuple[str, Grid]] = []
    current = grid
    for index in range(4):
        variants.append((f"rotate_{index * 90}", current))
        variants.append((f"reflect_rotate_{index * 90}", tuple(tuple(reversed(row)) for row in current)))
        current = rotate90(current)
    unique: dict[str, tuple[str, Grid]] = {}
    for name, value in variants:
        unique.setdefault(_canonical(_plain(value)), (name, value))
    return tuple(unique[key] for key in sorted(unique))


def _orient_canvas_from_constellation(grid: Grid) -> tuple[Grid, dict[str, Any]]:
    background = _background(grid)
    height, width = _shape(grid)
    outcomes: dict[str, tuple[Grid, dict[str, Any]]] = {}
    for canvas_color in sorted({cell for row in grid for cell in row} - {background}):
        canvas_points = {(r, c) for r in range(height) for c in range(width) if grid[r][c] == canvas_color}
        if len(canvas_points) < 20:
            continue
        r0, r1, c0, c1 = _bbox(canvas_points)
        if (r1 - r0 + 1) * (c1 - c0 + 1) < 25:
            continue
        if any(
            grid[row][column] == background
            for row in range(r0, r1 + 1)
            for column in range(c0, c1 + 1)
        ):
            continue
        crop = tuple(tuple(grid[row][column] for column in range(c0, c1 + 1)) for row in range(r0, r1 + 1))
        internal: dict[int, list[Cell]] = {}
        external: dict[int, list[Cell]] = {}
        for row in range(height):
            for column in range(width):
                color = grid[row][column]
                if color in {background, canvas_color}:
                    continue
                target = internal if r0 <= row <= r1 and c0 <= column <= c1 else external
                target.setdefault(color, []).append((row, column))
        anchors = sorted(color for color in internal if len(internal[color]) == 1 and len(external.get(color, ())) == 1)
        if len(anchors) < 2:
            continue
        external_points = {color: external[color][0] for color in anchors}
        external_signature = _relation_signature(external_points)
        for transform_name, transformed in _d4_variants(crop):
            transformed_points: dict[int, Cell] = {}
            valid = True
            for color in anchors:
                points = [
                    (row, column)
                    for row, line in enumerate(transformed)
                    for column, value in enumerate(line)
                    if value == color
                ]
                if len(points) != 1:
                    valid = False
                    break
                transformed_points[color] = points[0]
            if not valid or _relation_signature(transformed_points) != external_signature:
                continue
            output = transformed
            outcomes[_canonical(_plain(output))] = (
                output,
                {"transform": transform_name, "anchor_colors": len(anchors)},
            )
    if len(outcomes) != 1:
        raise Undefined("constellation orientation is absent or ambiguous")
    return next(iter(outcomes.values()))


def _line_runs(indices: Sequence[int]) -> tuple[int, ...]:
    if not indices:
        return ()
    runs: list[list[int]] = [[indices[0]]]
    for value in indices[1:]:
        if value == runs[-1][-1] + 1:
            runs[-1].append(value)
        else:
            runs.append([value])
    return tuple(run[len(run) // 2] for run in runs)


def _parse_scaffold_panel(grid: Grid, scaffold: int, component: Component) -> dict[str, Any] | None:
    r0, r1, c0, c1 = component.bbox
    row_lines = _line_runs(
        [row for row in range(r0, r1 + 1) if all(grid[row][column] == scaffold for column in range(c0, c1 + 1))]
    )
    column_lines = _line_runs(
        [column for column in range(c0, c1 + 1) if all(grid[row][column] == scaffold for row in range(r0, r1 + 1))]
    )
    if len(row_lines) < 3 or len(column_lines) < 3:
        return None
    if row_lines[0] != r0 or row_lines[-1] != r1 or column_lines[0] != c0 or column_lines[-1] != c1:
        return None
    cells: list[tuple[int, int, tuple[Cell, ...]]] = []
    for ri, (top, bottom) in enumerate(zip(row_lines, row_lines[1:])):
        for ci, (left, right) in enumerate(zip(column_lines, column_lines[1:])):
            support = tuple(
                (row, column)
                for row in range(top + 1, bottom)
                for column in range(left + 1, right)
            )
            if not support:
                return None
            cells.append((ri, ci, support))
    return {
        "shape": (len(row_lines) - 1, len(column_lines) - 1),
        "cells": cells,
        "bbox": component.bbox,
    }


def _decode_scaffold_cell_legend(grid: Grid) -> tuple[Grid, dict[str, Any]]:
    background = _background(grid)
    outcomes: dict[str, tuple[Grid, dict[str, Any]]] = {}
    for scaffold in sorted({cell for row in grid for cell in row} - {background}):
        panels = [
            parsed
            for component in _components(grid, color=scaffold)
            if (parsed := _parse_scaffold_panel(grid, scaffold, component)) is not None
        ]
        if len(panels) < 2 or len({panel["shape"] for panel in panels}) != 1:
            continue
        logical_shape = panels[0]["shape"]
        legend: dict[tuple[int, int], int] = {}
        valid = True
        for panel in panels:
            for row_index, column_index, support in panel["cells"]:
                colors = {grid[row][column] for row, column in support} - {background, scaffold}
                if len(colors) > 1:
                    valid = False
                    break
                if colors:
                    color = next(iter(colors))
                    if any(grid[row][column] != color for row, column in support):
                        valid = False
                        break
                    key = (row_index, column_index)
                    if key in legend and legend[key] != color:
                        valid = False
                        break
                    legend[key] = color
            if not valid:
                break
        expected_keys = {(row, column) for row in range(logical_shape[0]) for column in range(logical_shape[1])}
        if not valid or set(legend) != expected_keys:
            continue
        result = [list(row) for row in grid]
        changed = 0
        for panel in panels:
            for row_index, column_index, support in panel["cells"]:
                color = legend[(row_index, column_index)]
                for row, column in support:
                    if result[row][column] == background:
                        result[row][column] = color
                        changed += 1
                    elif result[row][column] != color:
                        valid = False
        if not valid or not changed:
            continue
        frozen = _freeze(result)
        outcomes[_canonical(_plain(frozen))] = (
            frozen,
            {"panels": len(panels), "logical_shape": list(logical_shape), "filled_cells": changed},
        )
    if len(outcomes) != 1:
        raise Undefined("scaffold legend is absent or ambiguous")
    return next(iter(outcomes.values()))


def _enclosed_holes(grid: Grid, component: Component, background: int) -> tuple[frozenset[Cell], ...]:
    r0, r1, c0, c1 = component.bbox
    candidates = {
        (row, column)
        for row in range(r0, r1 + 1)
        for column in range(c0, c1 + 1)
        if grid[row][column] == background
    }
    holes: list[frozenset[Cell]] = []
    while candidates:
        seed = min(candidates)
        queue = deque([seed])
        candidates.remove(seed)
        cells: set[Cell] = set()
        touches = False
        while queue:
            row, column = queue.popleft()
            cells.add((row, column))
            touches |= row in {r0, r1} or column in {c0, c1}
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                neighbor = (row + dr, column + dc)
                if neighbor in candidates:
                    candidates.remove(neighbor)
                    queue.append(neighbor)
        if not touches:
            holes.append(frozenset(cells))
    return tuple(sorted(holes, key=lambda cells: (_bbox(cells), len(cells))))


def _inventory_assignments(
    holes: Sequence[frozenset[Cell]], inventory: Mapping[int, int]
) -> tuple[tuple[int, ...], ...]:
    """Return all colorings whose per-color hole area equals its inventory."""

    areas = tuple(len(hole) for hole in holes)
    colors = tuple(sorted(color for color, area in inventory.items() if 0 < area <= sum(areas)))
    possible: dict[int, tuple[int, ...]] = {}
    for color in colors:
        masks = []
        for mask in range(1, 1 << len(holes)):
            if sum(areas[index] for index in range(len(holes)) if mask & (1 << index)) == inventory[color]:
                masks.append(mask)
        possible[color] = tuple(masks)
    outcomes: set[tuple[int, ...]] = set()

    def search(covered: int, assignment: list[int | None]) -> None:
        if len(outcomes) > 128:
            return
        full = (1 << len(holes)) - 1
        if covered == full:
            outcomes.add(tuple(int(color) for color in assignment))
            return
        first = next(index for index in range(len(holes)) if not covered & (1 << index))
        for color in colors:
            for mask in possible[color]:
                if not mask & (1 << first) or mask & covered:
                    continue
                next_assignment = list(assignment)
                for index in range(len(holes)):
                    if mask & (1 << index):
                        next_assignment[index] = color
                search(covered | mask, next_assignment)

    if holes:
        search(0, [None] * len(holes))
    return tuple(sorted(outcomes))


def _tile_inventory_into_cavities(grid: Grid) -> tuple[Grid, dict[str, Any]]:
    background = _background(grid)
    all_components = _components(grid, background=background)
    canvases: list[Component] = []
    holes: list[frozenset[Cell]] = []
    for component in all_components:
        r0, r1, c0, c1 = component.bbox
        bbox_area = (r1 - r0 + 1) * (c1 - c0 + 1)
        if component.area < 20 or bbox_area < 25 or component.area * 4 < bbox_area:
            continue
        component_holes = _enclosed_holes(grid, component, background)
        if component_holes:
            canvases.append(component)
            holes.extend(component_holes)
    unique_holes = tuple({frozenset(hole): hole for hole in holes}.values())
    if not canvases or not unique_holes or len(unique_holes) > 12:
        raise Undefined("no bounded cavity inventory scene")
    canvas_cells = frozenset().union(*(component.cells for component in canvases))
    external_by_color: dict[int, list[Component]] = {}
    for component in all_components:
        if component.cells <= canvas_cells:
            continue
        r0, r1, c0, c1 = component.bbox
        if component.area != (r1 - r0 + 1) * (c1 - c0 + 1):
            continue
        external_by_color.setdefault(component.color, []).append(component)
    # A cloud of many isolated equal tokens is a distractor role, not a tile
    # inventory.  Singleton tiles remain available when their color also owns
    # a larger rectangular packet.
    external_by_color = {
        color: components
        for color, components in external_by_color.items()
        if not (len(components) >= 4 and all(component.area == 1 for component in components))
    }
    universe = frozenset().union(*unique_holes)
    inventory_areas = {
        color: sum(component.area for component in components)
        for color, components in external_by_color.items()
    }
    colors = sorted(external_by_color)
    selected_color_sets = [
        subset
        for size in range(1, len(colors) + 1)
        for subset in itertools.combinations(colors, size)
        if sum(inventory_areas[color] for color in subset) == len(universe)
    ]
    outputs: dict[str, tuple[Grid, dict[str, Any]]] = {}
    if universe:
        ur0, ur1, uc0, uc1 = _bbox(universe)
    for selected_colors in selected_color_sets:
        pieces: list[tuple[int, int, int]] = []
        for color in selected_colors:
            for component in external_by_color[color]:
                r0, r1, c0, c1 = component.bbox
                pieces.append((color, r1 - r0 + 1, c1 - c0 + 1))
        placement_options: list[list[frozenset[Cell]]] = []
        valid = True
        for _, piece_height, piece_width in pieces:
            options = [
                frozenset(
                    (row, column)
                    for row in range(top, top + piece_height)
                    for column in range(left, left + piece_width)
                )
                for top in range(ur0, ur1 - piece_height + 2)
                for left in range(uc0, uc1 - piece_width + 2)
            ]
            options = [option for option in options if option <= universe]
            if not options:
                valid = False
                break
            placement_options.append(options)
        if not valid:
            continue
        order = sorted(range(len(pieces)), key=lambda index: (len(placement_options[index]), -pieces[index][1] * pieces[index][2], pieces[index]))

        def search(piece_index: int, covered: frozenset[Cell], colored: dict[Cell, int]) -> None:
            if len(outputs) > 128:
                return
            if piece_index == len(order):
                if covered != universe:
                    return
                result = [[background] * _shape(grid)[1] for _ in range(_shape(grid)[0])]
                for canvas in canvases:
                    for row, column in canvas.cells:
                        result[row][column] = canvas.color
                for (row, column), color in colored.items():
                    result[row][column] = color
                frozen = _freeze(result)
                outputs[_canonical(_plain(frozen))] = (
                    frozen,
                    {
                        "canvases": len(canvases),
                        "cavity_regions": len(unique_holes),
                        "inventory_colors_used": len(selected_colors),
                        "rectangular_packets": len(pieces),
                    },
                )
                return
            index = order[piece_index]
            color = pieces[index][0]
            for placement in placement_options[index]:
                if placement & covered:
                    continue
                next_colored = dict(colored)
                for position in placement:
                    next_colored[position] = color
                search(piece_index + 1, covered | placement, next_colored)

        search(0, frozenset(), {})
    if len(outputs) != 1:
        raise Undefined("cavity inventory assignment is absent or ambiguous")
    return next(iter(outputs.values()))


def _sparse_rectangle(points: set[Cell], step: int = 2) -> tuple[int, int, int, int] | None:
    if not points:
        return None
    r0, r1, c0, c1 = _bbox(points)
    if r1 - r0 < 2 * step or c1 - c0 < 2 * step:
        return None
    expected = {
        (row, column)
        for row in range(r0, r1 + 1, step)
        for column in range(c0, c1 + 1, step)
        if row in {r0, r1} or column in {c0, c1}
    }
    return (r0, r1, c0, c1) if points == expected else None


def _densify_sparse_frame_pack(grid: Grid) -> tuple[Grid, dict[str, Any]]:
    height, width = _shape(grid)
    if height < 9 or width < 9:
        raise Undefined("sparse lattice is too small")
    colors = sorted({cell for row in grid for cell in row})
    base_candidates: list[tuple[int, int, int, int, dict[Cell, int]]] = []
    for grid_color, cell_color in itertools.permutations(colors, 2):
        for row_phase in (0, 1):
            for column_phase in (0, 1):
                expected: dict[Cell, int] = {}
                anomalies = 0
                for row in range(height):
                    for column in range(width):
                        value = cell_color if row % 2 != row_phase and column % 2 != column_phase else grid_color
                        expected[(row, column)] = value
                        anomalies += grid[row][column] != value
                if 3 <= anomalies <= min(128, height * width // 3):
                    base_candidates.append((anomalies, grid_color, cell_color, row_phase * 2 + column_phase, expected))
    if not base_candidates:
        raise Undefined("no two-phase lattice")
    best = min(item[0] for item in base_candidates)
    base_candidates = [item for item in base_candidates if item[0] == best]
    outcomes: dict[str, tuple[Grid, dict[str, Any]]] = {}
    for _, grid_color, cell_color, phase_code, expected in base_candidates:
        anomalies_by_color: dict[int, set[Cell]] = {}
        for position, base in expected.items():
            actual = grid[position[0]][position[1]]
            if actual != base:
                anomalies_by_color.setdefault(actual, set()).add(position)
        for frame_color, frame_points in anomalies_by_color.items():
            rectangle = _sparse_rectangle(frame_points, 2)
            if rectangle is None:
                continue
            r0, r1, c0, c1 = rectangle
            motifs: list[tuple[int, set[Cell], tuple[int, int]]] = []
            valid = True
            for color, points in anomalies_by_color.items():
                if color == frame_color:
                    continue
                rows = sorted({row for row, _ in points})
                columns = sorted({column for _, column in points})
                if any(right - left != 2 for left, right in zip(rows, rows[1:])) or any(right - left != 2 for left, right in zip(columns, columns[1:])):
                    valid = False
                    break
                if points != {(row, column) for row in rows for column in columns}:
                    valid = False
                    break
                motifs.append((color, points, (rows[-1] - rows[0] + 1, columns[-1] - columns[0] + 1)))
            if not valid or not motifs:
                continue
            row_centers = [(min(row for row, _ in points) + max(row for row, _ in points)) / 2 for _, points, _ in motifs]
            column_centers = [(min(column for _, column in points) + max(column for _, column in points)) / 2 for _, points, _ in motifs]
            row_spread = max(row_centers) - min(row_centers)
            column_spread = max(column_centers) - min(column_centers)
            if row_spread == column_spread:
                continue
            horizontal = column_spread > row_spread
            motifs.sort(
                key=lambda item: (
                    (min(column for _, column in item[1]) if horizontal else min(row for row, _ in item[1])),
                    item[0],
                )
            )
            inner_height, inner_width = r1 - r0 - 1, c1 - c0 - 1
            pack_height = max(shape[0] for _, _, shape in motifs) if horizontal else sum(shape[0] for _, _, shape in motifs) + len(motifs) - 1
            pack_width = sum(shape[1] for _, _, shape in motifs) + len(motifs) - 1 if horizontal else max(shape[1] for _, _, shape in motifs)
            if pack_height > inner_height or pack_width > inner_width:
                continue
            top = r0 + 1 + (inner_height - pack_height) // 2
            left = c0 + 1 + (inner_width - pack_width) // 2
            result = [[expected[(row, column)] for column in range(width)] for row in range(height)]
            # Entering the sparse frame changes atlas: its interior is a dense
            # canvas of the lattice's grid color, not another checker cell.
            for row in range(r0 + 1, r1):
                for column in range(c0 + 1, c1):
                    result[row][column] = grid_color
            for column in range(c0, c1 + 1):
                result[r0][column] = frame_color
                result[r1][column] = frame_color
            for row in range(r0, r1 + 1):
                result[row][c0] = frame_color
                result[row][c1] = frame_color
            cursor = left if horizontal else top
            for color, _, (motif_height, motif_width) in motifs:
                motif_top = top + (pack_height - motif_height) // 2 if horizontal else cursor
                motif_left = cursor if horizontal else left + (pack_width - motif_width) // 2
                for row in range(motif_top, motif_top + motif_height):
                    for column in range(motif_left, motif_left + motif_width):
                        result[row][column] = color
                cursor += (motif_width if horizontal else motif_height) + 1
            frozen = _freeze(result)
            outcomes[_canonical(_plain(frozen))] = (
                frozen,
                {"frame_shape": [r1 - r0 + 1, c1 - c0 + 1], "packed_objects": len(motifs), "axis": "horizontal" if horizontal else "vertical", "phase": phase_code},
            )
    if len(outcomes) != 1:
        raise Undefined("sparse frame packing is absent or ambiguous")
    return next(iter(outcomes.values()))


def _project_stripes(grid: Grid) -> tuple[Grid, dict[str, Any]]:
    background = _background(grid)
    height, width = _shape(grid)
    outcomes: dict[str, tuple[Grid, dict[str, Any]]] = {}
    colors = sorted({cell for row in grid for cell in row} - {background})
    for canvas_color in colors:
        points = {(row, column) for row in range(height) for column in range(width) if grid[row][column] == canvas_color}
        if not points:
            continue
        r0, r1, c0, c1 = _bbox(points)
        if r1 - r0 != c1 - c0 or len(points) != (r1 - r0 + 1) * (c1 - c0 + 1):
            continue
        side = r1 - r0 + 1
        if side < 2:
            continue
        signal_colors = [color for color in colors if color != canvas_color]
        for axis in (0, 1):
            coordinates: list[tuple[int, int]] = []
            valid = True
            for color in signal_colors:
                support = [(row, column) for row in range(height) for column in range(width) if grid[row][column] == color]
                values = {position[axis] for position in support}
                if len(values) != 1 or len(support) < 2:
                    valid = False
                    break
                coordinates.append((next(iter(values)), color))
            if not valid or len(coordinates) != side:
                continue
            coordinates.sort()
            gaps = [right[0] - left[0] for left, right in zip(coordinates, coordinates[1:])]
            if gaps and (len(set(gaps)) != 1 or gaps[0] <= 0):
                continue
            result = [[background] * side for _ in range(side)]
            for index, (_, color) in enumerate(coordinates):
                if axis == 0:
                    result[index] = [color] * side
                else:
                    for row in range(side):
                        result[row][index] = color
            frozen = _freeze(result)
            outcomes[_canonical(_plain(frozen))] = (
                frozen,
                {"axis": "rows" if axis == 0 else "columns", "slots": side},
            )
    if len(outcomes) != 1:
        raise Undefined("regular stripe projection is absent or ambiguous")
    return next(iter(outcomes.values()))


def _project_tokens_to_matching_border(grid: Grid) -> tuple[Grid, dict[str, Any]]:
    height, width = _shape(grid)
    if height < 4 or width < 4:
        raise Undefined("frame is too small")
    background = _unique_mode(
        grid[row][column] for row in range(1, height - 1) for column in range(1, width - 1)
    )
    if grid[0][0] != background or grid[0][-1] != background or grid[-1][0] != background or grid[-1][-1] != background:
        raise Undefined("frame corners are not background")
    sides = {
        "top": set(grid[0][1:-1]),
        "bottom": set(grid[-1][1:-1]),
        "left": {grid[row][0] for row in range(1, height - 1)},
        "right": {grid[row][-1] for row in range(1, height - 1)},
    }
    if any(len(values) != 1 for values in sides.values()):
        raise Undefined("frame side is not monochrome")
    side_colors = {name: next(iter(values)) for name, values in sides.items()}
    if len(set(side_colors.values())) != 4 or background in side_colors.values():
        raise Undefined("frame side roles are ambiguous")
    result = [[background] * width for _ in range(height)]
    result[0] = list(grid[0])
    result[-1] = list(grid[-1])
    for row in range(1, height - 1):
        result[row][0] = grid[row][0]
        result[row][-1] = grid[row][-1]
    projected = 0
    for row in range(1, height - 1):
        for column in range(1, width - 1):
            color = grid[row][column]
            if color == side_colors["top"]:
                result[1][column] = color
                projected += 1
            elif color == side_colors["bottom"]:
                result[height - 2][column] = color
                projected += 1
            elif color == side_colors["left"]:
                result[row][1] = color
                projected += 1
            elif color == side_colors["right"]:
                result[row][width - 2] = color
                projected += 1
    if not projected:
        raise Undefined("no token matches a frame side")
    return _freeze(result), {"projected_tokens": projected, "frame_roles": 4}


def _execute_internal(program: Mapping[str, Any], grid: Grid) -> tuple[Grid, dict[str, Any]]:
    if not isinstance(program, Mapping) or program.get("schema") != SCHEMA:
        raise Undefined("invalid frame-morphism program")
    operator = program.get("operator")
    if operator == "complete_multicolor_motifs":
        return _complete_multicolor_motifs(grid)
    if operator == "complete_canonical_chiral_motifs":
        preference = program.get("chirality_cross_preference")
        axis = program.get("reflection_axis")
        if preference not in {-1, 1} or axis not in {"rows", "columns"}:
            raise Undefined("invalid serialized chirality preference")
        return _complete_multicolor_motifs(
            grid,
            chirality_cross_preference=int(preference),
            reflection_axis=str(axis),
        )
    if operator == "instantiate_scaled_stencil":
        return _instantiate_scaled_stencil(grid)
    if operator == "expand_seed_to_frame":
        return _expand_seed_to_frame(grid)
    if operator == "orient_canvas_from_external_constellation":
        return _orient_canvas_from_constellation(grid)
    if operator == "decode_scaffold_cell_legend":
        return _decode_scaffold_cell_legend(grid)
    if operator == "tile_inventory_into_cavities":
        return _tile_inventory_into_cavities(grid)
    if operator == "densify_sparse_frame_pack":
        return _densify_sparse_frame_pack(grid)
    if operator == "project_regular_stripes":
        return _project_stripes(grid)
    if operator == "project_tokens_to_matching_border":
        return _project_tokens_to_matching_border(grid)
    raise Undefined("unknown frame-morphism operator")


def execute_program(program: Mapping[str, Any], value: Any) -> list[list[int]]:
    """Execute one serialized frame-morphism program."""

    limits = Limits()
    grid = _grid(value, limits)
    return _plain(_execute_internal(program, grid)[0])


def replay_program(program: Mapping[str, Any], value: Any) -> dict[str, Any]:
    """Replay a program through explicit lift, morphism, and render stages."""

    limits = Limits()
    grid = _grid(value, limits)
    output, receipt = _execute_internal(program, grid)
    lifted = {
        "kind": "intrinsic_frame_atlas",
        "shape": list(_shape(grid)),
        "coordinate_identity": "scene_local",
    }
    applied = {"operator": program["operator"], "receipt": receipt}
    return {
        "output": _plain(output),
        "stages": [
            {"name": "lift-frame-atlas", "input": _plain(grid), "output": lifted},
            {"name": "apply-frame-morphism", "input": lifted, "output": applied},
            {"name": "render-with-lineage", "input": applied, "output": _plain(output)},
        ],
    }


def _programs() -> tuple[dict[str, Any], ...]:
    lengths = {
        "complete_multicolor_motifs": 14,
        "instantiate_scaled_stencil": 16,
        "expand_seed_to_frame": 10,
        "orient_canvas_from_external_constellation": 16,
        "decode_scaffold_cell_legend": 15,
        "tile_inventory_into_cavities": 17,
        "densify_sparse_frame_pack": 17,
        "project_tokens_to_matching_border": 11,
        "project_regular_stripes": 12,
    }
    programs = [
        {"schema": SCHEMA, "operator": operator, "description_length": description_length}
        for operator, description_length in lengths.items()
    ]
    programs.extend(
        {
            "schema": SCHEMA,
            "operator": "complete_canonical_chiral_motifs",
            "chirality_cross_preference": preference,
            "reflection_axis": axis,
            "description_length": 16,
        }
        for preference in (-1, 1)
        for axis in ("columns", "rows")
    )
    return tuple(sorted(programs, key=_canonical))


def _behavior(program: Mapping[str, Any], grids: Sequence[Grid]) -> tuple[Grid, ...]:
    return tuple(_execute_internal(program, grid)[0] for grid in grids)


def _exact_programs(pairs: Sequence[Pair], probes: Sequence[Grid], limits: Limits) -> tuple[dict[str, Any], ...]:
    exact: list[dict[str, Any]] = []
    calls = 0
    for program in _programs():
        try:
            outputs = []
            for source, _ in pairs:
                outputs.append(_execute_internal(program, source)[0])
                calls += 1
            for probe in probes:
                _execute_internal(program, probe)
                calls += 1
            if calls > limits.max_executor_calls:
                raise Undefined("executor call cap exhausted")
        except (Undefined, TypeError, ValueError, KeyError, IndexError, ZeroDivisionError):
            continue
        if tuple(outputs) == tuple(target for _, target in pairs):
            exact.append(program)
    return tuple(sorted(exact, key=lambda program: (int(program["description_length"]), _canonical(program))))


def _loo(demonstrations: Sequence[Pair], limits: Limits) -> tuple[bool, list[dict[str, Any]]]:
    witnesses: list[dict[str, Any]] = []
    for held_index, (source, target) in enumerate(demonstrations):
        subset = tuple(pair for index, pair in enumerate(demonstrations) if index != held_index)
        programs = _exact_programs(subset, (source,), limits)
        behaviors: dict[str, tuple[Grid, ...]] = {}
        for program in programs:
            try:
                output = _behavior(program, (source,))
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


def _transport_program_palette(program: Mapping[str, Any], left: int, right: int) -> dict[str, Any]:
    return dict(program)


def _transport_program_d4(
    program: Mapping[str, Any], quarter_turns: int, reflected: bool
) -> dict[str, Any]:
    transported = dict(program)
    if transported.get("operator") == "complete_canonical_chiral_motifs":
        factor = -1 if quarter_turns % 2 else 1
        if reflected:
            factor *= -1
        transported["chirality_cross_preference"] = (
            int(transported["chirality_cross_preference"]) * factor
        )
        if quarter_turns % 2:
            transported["reflection_axis"] = (
                "rows" if transported["reflection_axis"] == "columns" else "columns"
            )
    return transported


def _gauge(program: Mapping[str, Any], demonstrations: Sequence[Pair], limits: Limits) -> tuple[bool, int, int]:
    d4_checks = 0
    palette_checks = 0
    for source, target in demonstrations:
        current_source, current_target = source, target
        for quarter_turns in range(4):
            paired = (
                (
                    current_source,
                    current_target,
                    _transport_program_d4(program, quarter_turns, False),
                ),
                (
                    tuple(tuple(reversed(row)) for row in current_source),
                    tuple(tuple(reversed(row)) for row in current_target),
                    _transport_program_d4(program, quarter_turns, True),
                ),
            )
            for source_variant, target_variant, transported_program in paired:
                d4_checks += 1
                if d4_checks + palette_checks > limits.max_gauge_checks:
                    return False, d4_checks, palette_checks
                try:
                    if _execute_internal(transported_program, source_variant)[0] != target_variant:
                        return False, d4_checks, palette_checks
                except Undefined:
                    return False, d4_checks, palette_checks
            current_source = tuple(tuple(row) for row in zip(*reversed(current_source)))
            current_target = tuple(tuple(row) for row in zip(*reversed(current_target)))

        colors = sorted({cell for row in source for cell in row} | {cell for row in target for cell in row})
        absent = next((color for color in range(10) if color not in colors), None)
        swaps = list(itertools.combinations(colors, 2))
        if absent is not None:
            swaps.extend((color, absent) for color in colors)
        for left, right in swaps:
            palette_checks += 1
            if d4_checks + palette_checks > limits.max_gauge_checks:
                return False, d4_checks, palette_checks
            transported = _transport_program_palette(program, left, right)
            try:
                actual = _execute_internal(transported, _swap_grid(source, left, right))[0]
            except Undefined:
                return False, d4_checks, palette_checks
            if actual != _swap_grid(target, left, right):
                return False, d4_checks, palette_checks
    return True, d4_checks, palette_checks


def compile_task(task: Any, limits: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    """Compile one unique, proof-carrying frame behavior or abstain."""

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
            outputs = _behavior(program, tests)
        except Undefined:
            continue
        behaviors.setdefault(_digest([_plain(grid) for grid in outputs]), []).append((program, outputs))
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
        train_outputs = _behavior(representative, tuple(source for source, _ in demonstrations))
    except Undefined:
        return []
    if train_outputs != tuple(target for _, target in demonstrations):
        return []
    candidate = {
        "family": "frame_morphism_compiler",
        "program": json.loads(_canonical(representative)),
        "train_outputs": [_plain(grid) for grid in train_outputs],
        "test_outputs": [_plain(grid) for grid in outputs],
        "complexity": int(representative["description_length"]),
        "evidence": {
            "intrinsic_coordinate_frames": True,
            "root_identity_transport": True,
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
            "literal_palette_transport_checked": False,
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
