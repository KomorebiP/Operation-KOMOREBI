"""Bounded topology, component, mask, symmetry, and occlusion entrant.

The public boundary is deliberately small: :func:`compile_task` accepts a
sanitized ARC task containing training input/output pairs and test inputs only.
It returns deterministic, JSON-serializable candidates that exactly replay all
training demonstrations.  Invalid, over-budget, or test-labelled tasks fail
closed with an empty candidate list.

This module is standalone on purpose.  Tournament harnesses may load entrants
directly from their paths without installing any of the earlier PR-LASM
packages.

Author: Komorebi P.
"""
from __future__ import annotations

from collections import Counter, deque
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from fractions import Fraction
import json
from typing import Any


Grid = tuple[tuple[int, ...], ...]
Cell = tuple[int, int]

ORTHOGONAL: tuple[Cell, ...] = ((-1, 0), (0, -1), (0, 1), (1, 0))
EIGHT: tuple[Cell, ...] = tuple(
    (dr, dc)
    for dr in (-1, 0, 1)
    for dc in (-1, 0, 1)
    if (dr, dc) != (0, 0)
)

PROGRAM_SCHEMA = "komorebi.block13.topology_symmetry.program.v1"
DEFAULT_MAX_CANDIDATES = 64
DEFAULT_MAX_HYPOTHESES = 15_000
MAX_CANDIDATES = 256
MAX_HYPOTHESES = 250_000
MAX_EXAMPLES = 12
MAX_TOTAL_CELLS = 48_000
MAX_OBJECTS = 128


class UndefinedRule(ValueError):
    """Raised when a program has no unambiguous meaning on an input."""


@dataclass(frozen=True, slots=True)
class SceneObject:
    cells: frozenset[Cell]
    color: int | None
    top: int
    left: int
    bottom: int
    right: int
    holes: frozenset[Cell]

    @property
    def size(self) -> int:
        return len(self.cells)

    @property
    def bbox_area(self) -> int:
        return (self.bottom - self.top + 1) * (self.right - self.left + 1)

    @property
    def density(self) -> Fraction:
        return Fraction(self.size, self.bbox_area)


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _grid(value: Any) -> Grid:
    if not isinstance(value, (list, tuple)) or not value:
        raise ValueError("grid must be a nonempty row sequence")
    if len(value) > 30:
        raise ValueError("grid exceeds ARC height")
    width: int | None = None
    rows: list[tuple[int, ...]] = []
    for raw_row in value:
        if not isinstance(raw_row, (list, tuple)) or not raw_row:
            raise ValueError("grid rows must be nonempty sequences")
        if width is None:
            width = len(raw_row)
            if width > 30:
                raise ValueError("grid exceeds ARC width")
        elif len(raw_row) != width:
            raise ValueError("grid must be rectangular")
        row: list[int] = []
        for cell in raw_row:
            if isinstance(cell, bool) or not isinstance(cell, int) or not 0 <= cell <= 9:
                raise ValueError("ARC colors must be integers in [0, 9]")
            row.append(cell)
        rows.append(tuple(row))
    return tuple(rows)


def _as_lists(grid: Grid) -> list[list[int]]:
    return [list(row) for row in grid]


def _sanitize(task: Any) -> tuple[tuple[tuple[Grid, Grid], ...], tuple[Grid, ...]]:
    if not isinstance(task, Mapping) or set(task) != {"train", "test"}:
        raise ValueError("task must contain only train and test")
    train_raw, test_raw = task["train"], task["test"]
    if (
        not isinstance(train_raw, (list, tuple))
        or not isinstance(test_raw, (list, tuple))
        or not train_raw
        or not test_raw
        or len(train_raw) > MAX_EXAMPLES
        or len(test_raw) > MAX_EXAMPLES
    ):
        raise ValueError("task has an invalid example count")
    train: list[tuple[Grid, Grid]] = []
    tests: list[Grid] = []
    cells = 0
    for example in train_raw:
        if not isinstance(example, Mapping) or set(example) != {"input", "output"}:
            raise ValueError("training records must contain only input and output")
        source, target = _grid(example["input"]), _grid(example["output"])
        cells += len(source) * len(source[0]) + len(target) * len(target[0])
        train.append((source, target))
    for example in test_raw:
        # In particular, reject test outputs instead of silently discarding them.
        if not isinstance(example, Mapping) or set(example) != {"input"}:
            raise ValueError("test records must contain an input only")
        source = _grid(example["input"])
        cells += len(source) * len(source[0])
        tests.append(source)
    if cells > MAX_TOTAL_CELLS:
        raise ValueError("task exceeds the cell budget")
    return tuple(train), tuple(tests)


def _limits(value: Any) -> tuple[int, int]:
    if value is None:
        return DEFAULT_MAX_CANDIDATES, DEFAULT_MAX_HYPOTHESES
    if isinstance(value, bool):
        raise ValueError("boolean limit is invalid")
    if isinstance(value, int):
        if value < 1:
            raise ValueError("candidate limit must be positive")
        return min(value, MAX_CANDIDATES), DEFAULT_MAX_HYPOTHESES
    if not isinstance(value, Mapping):
        raise ValueError("limits must be an integer or mapping")
    candidate_cap = value.get("max_candidates", value.get("candidate_cap", DEFAULT_MAX_CANDIDATES))
    hypothesis_cap = value.get("max_hypotheses", DEFAULT_MAX_HYPOTHESES)
    if (
        isinstance(candidate_cap, bool)
        or isinstance(hypothesis_cap, bool)
        or not isinstance(candidate_cap, int)
        or not isinstance(hypothesis_cap, int)
        or candidate_cap < 1
        or hypothesis_cap < 1
    ):
        raise ValueError("limits must be positive integers")
    return min(candidate_cap, MAX_CANDIDATES), min(hypothesis_cap, MAX_HYPOTHESES)


def _unique_extreme(counts: Counter[int], maximum: bool) -> int:
    if not counts:
        raise UndefinedRule("empty color population")
    wanted = max(counts.values()) if maximum else min(counts.values())
    winners = sorted(color for color, count in counts.items() if count == wanted)
    if len(winners) != 1:
        raise UndefinedRule("color role is tied")
    return winners[0]


def _background(grid: Grid, spec: str) -> int:
    if spec == "zero":
        return 0
    if spec.startswith("literal:"):
        return int(spec.split(":", 1)[1])
    height, width = len(grid), len(grid[0])
    if spec == "mode":
        values = (cell for row in grid for cell in row)
    elif spec == "border_mode":
        values = (
            grid[row][col]
            for row in range(height)
            for col in range(width)
            if row in {0, height - 1} or col in {0, width - 1}
        )
    elif spec == "corners":
        values = (grid[0][0], grid[0][-1], grid[-1][0], grid[-1][-1])
    else:
        raise UndefinedRule(f"unknown background role {spec}")
    return _unique_extreme(Counter(values), maximum=True)


def _resolve_color(grid: Grid, background: int, spec: str) -> int:
    if spec.startswith("literal:"):
        return int(spec.split(":", 1)[1])
    if spec == "background":
        return background
    counts = Counter(cell for row in grid for cell in row if cell != background)
    if spec == "foreground_unique":
        if len(counts) != 1:
            raise UndefinedRule("foreground is not single-colored")
        return next(iter(counts))
    if spec == "foreground_most":
        return _unique_extreme(counts, maximum=True)
    if spec == "foreground_least":
        return _unique_extreme(counts, maximum=False)
    if spec == "foreground_second_least":
        levels = sorted(set(counts.values()))
        if len(levels) < 2:
            raise UndefinedRule("second foreground rank is unavailable")
        winners = sorted(color for color, count in counts.items() if count == levels[1])
        if len(winners) != 1:
            raise UndefinedRule("second foreground rank is tied")
        return winners[0]
    raise UndefinedRule(f"unknown color role {spec}")


def _components(cells: Iterable[Cell], connectivity: int) -> tuple[frozenset[Cell], ...]:
    neighbors = ORTHOGONAL if connectivity == 4 else EIGHT
    unseen = set(cells)
    groups: list[frozenset[Cell]] = []
    while unseen:
        seed = min(unseen)
        unseen.remove(seed)
        queue = deque((seed,))
        group = {seed}
        while queue:
            row, col = queue.popleft()
            for dr, dc in neighbors:
                neighbor = row + dr, col + dc
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    group.add(neighbor)
                    queue.append(neighbor)
        groups.append(frozenset(group))
    return tuple(sorted(groups, key=lambda group: (min(group), len(group))))


def _bbox(cells: Iterable[Cell]) -> tuple[int, int, int, int]:
    materialized = tuple(cells)
    if not materialized:
        raise UndefinedRule("empty support")
    rows = [row for row, _ in materialized]
    cols = [col for _, col in materialized]
    return min(rows), min(cols), max(rows), max(cols)


def _holes(cells: frozenset[Cell]) -> frozenset[Cell]:
    top, left, bottom, right = _bbox(cells)
    empty = {
        (row, col)
        for row in range(top, bottom + 1)
        for col in range(left, right + 1)
        if (row, col) not in cells
    }
    exterior = {
        cell
        for cell in empty
        if cell[0] in {top, bottom} or cell[1] in {left, right}
    }
    queue = deque(sorted(exterior))
    while queue:
        row, col = queue.popleft()
        for dr, dc in ORTHOGONAL:
            neighbor = row + dr, col + dc
            if neighbor in empty and neighbor not in exterior:
                exterior.add(neighbor)
                queue.append(neighbor)
    return frozenset(empty - exterior)


def _objects(grid: Grid, bg: int, connectivity: int, partition: str) -> tuple[SceneObject, ...]:
    height, width = len(grid), len(grid[0])
    raw: list[tuple[frozenset[Cell], int | None]] = []
    if partition == "color":
        for color in sorted({cell for row in grid for cell in row} - {bg}):
            support = {
                (row, col)
                for row in range(height)
                for col in range(width)
                if grid[row][col] == color
            }
            raw.extend((group, color) for group in _components(support, connectivity))
    elif partition == "foreground":
        support = {
            (row, col)
            for row in range(height)
            for col in range(width)
            if grid[row][col] != bg
        }
        for group in _components(support, connectivity):
            colors = {grid[row][col] for row, col in group}
            raw.append((group, next(iter(colors)) if len(colors) == 1 else None))
    else:
        raise UndefinedRule(f"unknown partition {partition}")
    if not raw or len(raw) > MAX_OBJECTS:
        raise UndefinedRule("object population is empty or over budget")
    result = []
    for cells, color in raw:
        top, left, bottom, right = _bbox(cells)
        result.append(SceneObject(cells, color, top, left, bottom, right, _holes(cells)))
    return tuple(sorted(result, key=lambda item: (item.top, item.left, item.bottom, item.right, item.color or -1)))


def _metric(item: SceneObject, name: str, objects: Sequence[SceneObject], grid: Grid) -> Any:
    if name == "size":
        return item.size
    if name == "bbox_area":
        return item.bbox_area
    if name == "density":
        return item.density
    if name == "holes":
        return len(item.holes)
    if name == "color_pixels":
        if item.color is None:
            raise UndefinedRule("mixed-color object has no color frequency")
        return sum(row.count(item.color) for row in grid)
    if name == "color_components":
        if item.color is None:
            raise UndefinedRule("mixed-color object has no component frequency")
        return sum(peer.color == item.color for peer in objects)
    raise UndefinedRule(f"unknown metric {name}")


def _select_objects(
    selector: str,
    objects: tuple[SceneObject, ...],
    grid: Grid,
    bg: int,
) -> tuple[SceneObject, ...]:
    if selector == "all":
        return objects
    if selector == "has_holes":
        result = tuple(item for item in objects if item.holes)
    elif selector == "no_holes":
        result = tuple(item for item in objects if not item.holes)
    elif selector.startswith("color:"):
        color = _resolve_color(grid, bg, selector.split(":", 1)[1])
        result = tuple(item for item in objects if item.color == color)
    else:
        parts = selector.split(":")
        if len(parts) != 2:
            raise UndefinedRule(f"unknown selector {selector}")
        metric_name, extreme = parts
        values = [(item, _metric(item, metric_name, objects, grid)) for item in objects]
        want_max = extreme.endswith("max")
        wanted = max(value for _, value in values) if want_max else min(value for _, value in values)
        result = tuple(item for item, value in values if value == wanted)
        if extreme.startswith("unique_") and len(result) != 1:
            raise UndefinedRule("selector extreme is tied")
    if not result:
        raise UndefinedRule("selector is empty")
    return result


def _support(grid: Grid, bg: int, spec: str) -> frozenset[Cell]:
    height, width = len(grid), len(grid[0])
    if spec == "all_foreground":
        cells = {
            (row, col)
            for row in range(height)
            for col in range(width)
            if grid[row][col] != bg
        }
    else:
        color = _resolve_color(grid, bg, spec)
        cells = {
            (row, col)
            for row in range(height)
            for col in range(width)
            if grid[row][col] == color
        }
    if not cells:
        raise UndefinedRule("source support is empty")
    return frozenset(cells)


def _enclosed_regions(grid: Grid, bg: int, connectivity: int) -> tuple[frozenset[Cell], ...]:
    height, width = len(grid), len(grid[0])
    support = {
        (row, col)
        for row in range(height)
        for col in range(width)
        if grid[row][col] == bg
    }
    regions = []
    for group in _components(support, connectivity):
        if not any(row in {0, height - 1} or col in {0, width - 1} for row, col in group):
            regions.append(group)
    if not regions:
        raise UndefinedRule("no enclosed background region")
    return tuple(regions)


def _select_regions(selector: str, regions: tuple[frozenset[Cell], ...]) -> tuple[frozenset[Cell], ...]:
    if selector == "all":
        return regions
    sizes = [len(region) for region in regions]
    if selector.endswith("largest"):
        wanted = max(sizes)
    elif selector.endswith("smallest"):
        wanted = min(sizes)
    else:
        raise UndefinedRule(f"unknown region selector {selector}")
    result = tuple(region for region in regions if len(region) == wanted)
    if selector.startswith("unique_") and len(result) != 1:
        raise UndefinedRule("region selector is tied")
    return result


def _blank(height: int, width: int, color: int) -> list[list[int]]:
    return [[color for _ in range(width)] for _ in range(height)]


def _paint_cells(
    output: list[list[int]],
    cells: Iterable[Cell],
    color: int,
    *,
    policy: str,
    background: int,
) -> None:
    for row, col in cells:
        if policy == "overwrite" or output[row][col] == background:
            output[row][col] = color


def _execute_enclosed(program: Mapping[str, Any], grid: Grid) -> Grid:
    bg = _background(grid, program["background"])
    regions = _select_regions(
        program["selector"],
        _enclosed_regions(grid, bg, int(program["connectivity"])),
    )
    paint = _resolve_color(grid, bg, program["paint"])
    output = _as_lists(grid) if program["base"] == "preserve" else _blank(len(grid), len(grid[0]), bg)
    for region in regions:
        _paint_cells(output, region, paint, policy="overwrite", background=bg)
    return tuple(tuple(row) for row in output)


def _geometry_cells(action: str, support: frozenset[Cell]) -> frozenset[Cell]:
    top, left, bottom, right = _bbox(support)
    if action == "bbox_frame":
        return frozenset(
            (row, col)
            for row in range(top, bottom + 1)
            for col in range(left, right + 1)
            if row in {top, bottom} or col in {left, right}
        )
    if action == "bbox_fill":
        return frozenset(
            (row, col)
            for row in range(top, bottom + 1)
            for col in range(left, right + 1)
        )
    if action == "bbox_interior":
        return frozenset(
            (row, col)
            for row in range(top + 1, bottom)
            for col in range(left + 1, right)
        )
    if action in {"object_outline", "object_interior"}:
        outline = {
            cell
            for cell in support
            if any((cell[0] + dr, cell[1] + dc) not in support for dr, dc in ORTHOGONAL)
        }
        return frozenset(outline if action == "object_outline" else set(support) - outline)
    raise UndefinedRule(f"unknown geometry action {action}")


def _execute_geometry(program: Mapping[str, Any], grid: Grid) -> Grid:
    bg = _background(grid, program["background"])
    support = _support(grid, bg, program["source"])
    top, left, bottom, right = _bbox(support)
    action = program["action"]
    if action in {"crop_input", "crop_support"}:
        if action == "crop_input":
            return tuple(tuple(grid[row][left : right + 1]) for row in range(top, bottom + 1))
        return tuple(
            tuple(grid[row][col] if (row, col) in support else bg for col in range(left, right + 1))
            for row in range(top, bottom + 1)
        )
    paint = _resolve_color(grid, bg, program["paint"])
    cells = _geometry_cells(action, support)
    base = program["base"]
    if base == "preserve":
        output = _as_lists(grid)
    else:
        output = _blank(len(grid), len(grid[0]), bg)
        if base == "support":
            for row, col in support:
                output[row][col] = grid[row][col]
    _paint_cells(
        output,
        cells,
        paint,
        policy=program["paint_policy"],
        background=bg,
    )
    return tuple(tuple(row) for row in output)


def _combined_bbox(objects: Sequence[SceneObject]) -> tuple[int, int, int, int]:
    return _bbox(cell for item in objects for cell in item.cells)


def _object_boundary(item: SceneObject) -> tuple[frozenset[Cell], frozenset[Cell]]:
    outline = frozenset(
        cell
        for cell in item.cells
        if any((cell[0] + dr, cell[1] + dc) not in item.cells for dr, dc in ORTHOGONAL)
    )
    return outline, frozenset(set(item.cells) - set(outline))


def _execute_components(program: Mapping[str, Any], grid: Grid) -> Grid:
    bg = _background(grid, program["background"])
    objects = _objects(grid, bg, int(program["connectivity"]), program["partition"])
    selected = _select_objects(program["selector"], objects, grid, bg)
    selected_cells = frozenset(cell for item in selected for cell in item.cells)
    action = program["action"]
    if action in {"crop_original", "crop_selected"}:
        top, left, bottom, right = _combined_bbox(selected)
        if action == "crop_original":
            return tuple(tuple(grid[row][left : right + 1]) for row in range(top, bottom + 1))
        return tuple(
            tuple(grid[row][col] if (row, col) in selected_cells else bg for col in range(left, right + 1))
            for row in range(top, bottom + 1)
        )
    if action == "isolate_original":
        output = _blank(len(grid), len(grid[0]), bg)
        for row, col in selected_cells:
            output[row][col] = grid[row][col]
        return tuple(tuple(row) for row in output)
    if action == "erase_selected":
        output = _as_lists(grid)
        for row, col in selected_cells:
            output[row][col] = bg
        return tuple(tuple(row) for row in output)

    paint = _resolve_color(grid, bg, program["paint"])
    base = program.get("base", "preserve")
    output = _as_lists(grid) if base == "preserve" else _blank(len(grid), len(grid[0]), bg)
    if base == "support":
        for row, col in selected_cells:
            output[row][col] = grid[row][col]
    if action in {"recolor_selected", "isolate_recolor"}:
        if action == "isolate_recolor" and base == "preserve":
            output = _blank(len(grid), len(grid[0]), bg)
        _paint_cells(output, selected_cells, paint, policy="overwrite", background=bg)
    elif action == "fill_holes":
        _paint_cells(
            output,
            (cell for item in selected for cell in item.holes),
            paint,
            policy="overwrite",
            background=bg,
        )
    elif action.startswith("bbox_"):
        kind = action
        for item in selected:
            cells = _geometry_cells(kind, item.cells)
            _paint_cells(
                output,
                cells,
                paint,
                policy=program["paint_policy"],
                background=bg,
            )
    elif action in {"extract_outline", "extract_interior"}:
        cells: set[Cell] = set()
        for item in selected:
            outline, interior = _object_boundary(item)
            cells.update(outline if action == "extract_outline" else interior)
        _paint_cells(output, cells, paint, policy="overwrite", background=bg)
    else:
        raise UndefinedRule(f"unknown component action {action}")
    return tuple(tuple(row) for row in output)


GROUPS: dict[str, tuple[str, ...]] = {
    "reflect_lr": ("identity", "reflect_lr"),
    "reflect_ud": ("identity", "reflect_ud"),
    "halfturn": ("identity", "rot180"),
    "main_diagonal": ("identity", "main_diagonal"),
    "anti_diagonal": ("identity", "anti_diagonal"),
    "axes": ("identity", "reflect_lr", "reflect_ud", "rot180"),
    "diagonals": ("identity", "main_diagonal", "anti_diagonal", "rot180"),
    "rot4": ("identity", "rot90", "rot180", "rot270"),
    "d4": (
        "identity",
        "reflect_lr",
        "reflect_ud",
        "rot180",
        "rot90",
        "rot270",
        "main_diagonal",
        "anti_diagonal",
    ),
}


def _transform(row: int, col: int, height: int, width: int, name: str) -> Cell:
    if name == "identity":
        return row, col
    if name == "reflect_lr":
        return row, width - 1 - col
    if name == "reflect_ud":
        return height - 1 - row, col
    if name == "rot180":
        return height - 1 - row, width - 1 - col
    if height != width:
        raise UndefinedRule("quarter-turn and diagonal actions require a square scope")
    if name == "rot90":
        return col, height - 1 - row
    if name == "rot270":
        return width - 1 - col, row
    if name == "main_diagonal":
        return col, row
    if name == "anti_diagonal":
        return width - 1 - col, height - 1 - row
    raise UndefinedRule(f"unknown D4 action {name}")


def _symmetry_apply(
    program: Mapping[str, Any],
    grid: Grid,
    *,
    cleaned: Grid | None = None,
) -> Grid:
    working = cleaned if cleaned is not None else grid
    bg = _background(grid, program["background"])
    support = _support(working, bg, program["source"])
    if program["scope"] == "canvas":
        top, left, bottom, right = 0, 0, len(grid) - 1, len(grid[0]) - 1
    elif program["scope"] == "source_bbox":
        top, left, bottom, right = _bbox(support)
    else:
        raise UndefinedRule(f"unknown symmetry scope {program['scope']}")
    scope_height, scope_width = bottom - top + 1, right - left + 1
    base = program["base"]
    output = _as_lists(working) if base == "preserve" else _blank(len(grid), len(grid[0]), bg)
    color_mode = program["color_mode"]
    paint = None if color_mode == "preserve" else _resolve_color(grid, bg, program["paint"])
    orbit: dict[Cell, set[int]] = {}
    for source_row, source_col in sorted(support):
        original_color = working[source_row][source_col]
        local_row, local_col = source_row - top, source_col - left
        for transform in GROUPS[program["group"]]:
            target_row, target_col = _transform(local_row, local_col, scope_height, scope_width, transform)
            target = top + target_row, left + target_col
            if color_mode == "preserve":
                color = original_color
            elif color_mode == "new_constant" and target in support:
                color = original_color
            else:
                color = int(paint)
            orbit.setdefault(target, set()).add(color)
    for target, colors in orbit.items():
        if len(colors) != 1:
            raise UndefinedRule("symmetry orbit has a color collision")
        row, col = target
        if program["paint_policy"] == "background_only" and output[row][col] != bg and target not in support:
            continue
        output[row][col] = next(iter(colors))
    return tuple(tuple(row) for row in output)


def _execute_symmetry(program: Mapping[str, Any], grid: Grid) -> Grid:
    return _symmetry_apply(program, grid)


def _split_panels(grid: Grid, axis: str, gap: int) -> tuple[Grid, Grid]:
    height, width = len(grid), len(grid[0])
    if axis == "columns":
        if (width - gap) <= 0 or (width - gap) % 2:
            raise UndefinedRule("input cannot be split into equal column panels")
        size = (width - gap) // 2
        if gap and len({grid[row][size] for row in range(height)}) != 1:
            raise UndefinedRule("column separator is not uniform")
        return (
            tuple(tuple(row[:size]) for row in grid),
            tuple(tuple(row[size + gap :]) for row in grid),
        )
    if axis == "rows":
        if (height - gap) <= 0 or (height - gap) % 2:
            raise UndefinedRule("input cannot be split into equal row panels")
        size = (height - gap) // 2
        if gap and len(set(grid[size])) != 1:
            raise UndefinedRule("row separator is not uniform")
        return tuple(grid[:size]), tuple(grid[size + gap :])
    raise UndefinedRule(f"unknown panel axis {axis}")


def _execute_mask(program: Mapping[str, Any], grid: Grid) -> Grid:
    left, right = _split_panels(grid, program["axis"], int(program["gap"]))
    left_bg = _background(left, program["panel_background"])
    right_bg = _background(right, program["panel_background"])
    left_mask = tuple(tuple(cell != left_bg for cell in row) for row in left)
    right_mask = tuple(tuple(cell != right_bg for cell in row) for row in right)
    height, width = len(left), len(left[0])
    operation = program["operation"]
    result: list[list[bool]] = []
    for row in range(height):
        result_row = []
        for col in range(width):
            a, b = left_mask[row][col], right_mask[row][col]
            if operation == "union":
                value = a or b
            elif operation == "intersection":
                value = a and b
            elif operation == "xor":
                value = a != b
            elif operation == "left_minus_right":
                value = a and not b
            elif operation == "right_minus_left":
                value = b and not a
            elif operation == "equivalence":
                value = a == b
            elif operation == "complement_left":
                value = not a
            elif operation == "complement_right":
                value = not b
            else:
                raise UndefinedRule(f"unknown mask operation {operation}")
            result_row.append(value)
        result.append(result_row)
    global_bg = _background(grid, program["output_background"])
    paint = _resolve_color(grid, global_bg, program["paint"])
    return tuple(
        tuple(paint if result[row][col] else global_bg for col in range(width))
        for row in range(height)
    )


def _execute_bridge(program: Mapping[str, Any], grid: Grid) -> Grid:
    bg = _background(grid, program["background"])
    direction = program["direction"]
    if program["source"] == "span_endpoint_color":
        height, width = len(grid), len(grid[0])
        endpoint_colors: list[int] = []
        if direction in {"rows", "both"}:
            for row in range(height):
                cols = [col for col in range(width) if grid[row][col] != bg]
                if len(cols) >= 2:
                    endpoint_colors.extend((grid[row][min(cols)], grid[row][max(cols)]))
        if direction in {"columns", "both"}:
            for col in range(width):
                rows = [row for row in range(height) if grid[row][col] != bg]
                if len(rows) >= 2:
                    endpoint_colors.extend((grid[min(rows)][col], grid[max(rows)][col]))
        source_color = _unique_extreme(Counter(endpoint_colors), maximum=True)
        support = frozenset(
            (row, col)
            for row in range(height)
            for col in range(width)
            if grid[row][col] == source_color
        )
    else:
        support = _support(grid, bg, program["source"])
    if program["paint"] == "source":
        colors = {grid[row][col] for row, col in support}
        if len(colors) != 1:
            raise UndefinedRule("bridge source is multicolored")
        paint = next(iter(colors))
    else:
        paint = _resolve_color(grid, bg, program["paint"])
    height, width = len(grid), len(grid[0])
    targets: set[Cell] = set()
    if direction in {"rows", "both"}:
        for row in range(height):
            cols = sorted(col for candidate_row, col in support if candidate_row == row)
            if len(cols) >= 2:
                start, stop = (0, width - 1) if program["span"] == "canvas" else (cols[0], cols[-1])
                targets.update((row, col) for col in range(start, stop + 1))
    if direction in {"columns", "both"}:
        for col in range(width):
            rows = sorted(row for row, candidate_col in support if candidate_col == col)
            if len(rows) >= 2:
                start, stop = (0, height - 1) if program["span"] == "canvas" else (rows[0], rows[-1])
                targets.update((row, col) for row in range(start, stop + 1))
    if not targets:
        raise UndefinedRule("no bridge span")
    output = _as_lists(grid)
    replacement = program["replacement"]
    occluder = int(program.get("occluder", -1))
    for row, col in sorted(targets):
        if replacement == "background_only" and output[row][col] != bg:
            continue
        if replacement == "occluder_only" and output[row][col] not in {bg, occluder}:
            continue
        output[row][col] = paint
    return tuple(tuple(row) for row in output)


def _execute_occlusion_symmetry(program: Mapping[str, Any], grid: Grid) -> Grid:
    bg = _background(grid, program["background"])
    occluder = _resolve_color(grid, bg, program["occluder"])
    cleaned = tuple(
        tuple(bg if cell == occluder else cell for cell in row)
        for row in grid
    )
    return _symmetry_apply(program, grid, cleaned=cleaned)


def execute_program(program: Mapping[str, Any], value: Any) -> list[list[int]]:
    """Execute one emitted JSON program on a grid.

    The function is useful to tournament verifiers and intentionally performs
    the same structural checks used during synthesis.
    """

    grid = _grid(value)
    if not isinstance(program, Mapping) or program.get("schema") != PROGRAM_SCHEMA:
        raise ValueError("invalid topology/symmetry program")
    op = program.get("op")
    if op == "enclosed_regions":
        output = _execute_enclosed(program, grid)
    elif op == "support_geometry":
        output = _execute_geometry(program, grid)
    elif op == "components":
        output = _execute_components(program, grid)
    elif op == "symmetry_completion":
        output = _execute_symmetry(program, grid)
    elif op == "boolean_panels":
        output = _execute_mask(program, grid)
    elif op == "bridge_occlusion":
        output = _execute_bridge(program, grid)
    elif op == "occlusion_symmetry":
        output = _execute_occlusion_symmetry(program, grid)
    else:
        raise ValueError("unknown topology/symmetry operation")
    validated = _grid(output)
    return _as_lists(validated)


def _background_specs(train: Sequence[tuple[Grid, Grid]]) -> tuple[str, ...]:
    literals: set[str] = set()
    for source, _ in train:
        height, width = len(source), len(source[0])
        border = Counter(
            source[row][col]
            for row in range(height)
            for col in range(width)
            if row in {0, height - 1} or col in {0, width - 1}
        )
        if border:
            literals.add(f"literal:{border.most_common(1)[0][0]}")
        literals.add(f"literal:{source[0][0]}")
    return ("mode", "border_mode", "corners", "zero", *sorted(literals))


def _paint_specs(train: Sequence[tuple[Grid, Grid]]) -> tuple[str, ...]:
    colors: set[int] = set()
    for source, target in train:
        if (len(source), len(source[0])) == (len(target), len(target[0])):
            colors.update(
                target[row][col]
                for row in range(len(source))
                for col in range(len(source[0]))
                if source[row][col] != target[row][col]
            )
        else:
            colors.update(cell for row in target for cell in row)
    return (
        "foreground_unique",
        "foreground_most",
        "foreground_least",
        *(f"literal:{color}" for color in sorted(colors)),
    )


def _source_specs(train: Sequence[tuple[Grid, Grid]]) -> tuple[str, ...]:
    colors = sorted({cell for source, _ in train for row in source for cell in row})
    return (
        "all_foreground",
        "foreground_unique",
        "foreground_most",
        "foreground_least",
        *(f"literal:{color}" for color in colors),
    )


def _selector_specs(source_specs: Sequence[str]) -> tuple[str, ...]:
    selectors = {
        "all",
        "has_holes",
        "no_holes",
        *(
            f"{metric}:{extreme}"
            for metric in ("size", "bbox_area", "density", "holes", "color_pixels", "color_components")
            for extreme in ("min", "max", "unique_min", "unique_max")
        ),
    }
    selectors.update(f"color:{spec}" for spec in source_specs if spec != "all_foreground")
    return tuple(sorted(selectors))


def _same_shapes(train: Sequence[tuple[Grid, Grid]]) -> bool:
    return all((len(source), len(source[0])) == (len(target), len(target[0])) for source, target in train)


def _effect_profile(train: Sequence[tuple[Grid, Grid]]) -> tuple[bool, bool, bool]:
    additions = removals = recolors = False
    for source, target in train:
        if (len(source), len(source[0])) != (len(target), len(target[0])):
            continue
        source_mode = Counter(cell for row in source for cell in row).most_common(1)[0][0]
        for row in range(len(source)):
            for col in range(len(source[0])):
                before, after = source[row][col], target[row][col]
                if before == after:
                    continue
                additions |= before == source_mode and after != source_mode
                removals |= before != source_mode and after == source_mode
                recolors |= before != source_mode and after != source_mode
    return additions, removals, recolors


def _delta_shape_profile(
    train: Sequence[tuple[Grid, Grid]],
) -> tuple[bool, bool, bool, bool]:
    """Cheap necessary conditions for the single-effect grammars.

    Most programs in this entrant paint one learned color (occasionally plus
    the background).  Rejecting a whole family when a demonstration needs
    three or more distinct changed target colors is logically exact and saves
    millions of cell visits on obviously unrelated residual tasks.
    """

    one_target = True
    two_target = True
    preserve_palette = True
    binary_outputs = True
    for source, target in train:
        binary_outputs &= len({cell for row in target for cell in row}) <= 2
        if (len(source), len(source[0])) != (len(target), len(target[0])):
            continue
        changes = [
            (source[row][col], target[row][col])
            for row in range(len(source))
            for col in range(len(source[0]))
            if source[row][col] != target[row][col]
        ]
        after = {right for _, right in changes}
        one_target &= len(after) <= 1
        two_target &= len(after) <= 2
        preserve_palette &= after <= {cell for row in source for cell in row}
    return one_target, two_target, preserve_palette, binary_outputs


def _program(op: str, **fields: Any) -> dict[str, Any]:
    return {"schema": PROGRAM_SCHEMA, "op": op, **fields}


def _enumerate_programs(train: Sequence[tuple[Grid, Grid]]) -> list[tuple[str, int, dict[str, Any]]]:
    backgrounds = _background_specs(train)
    paints = _paint_specs(train)
    sources = _source_specs(train)
    selectors = _selector_specs(sources)
    same_shape = _same_shapes(train)
    additions, removals, recolors = _effect_profile(train)
    one_target, two_target, preserve_palette, binary_outputs = _delta_shape_profile(train)
    programs: list[tuple[str, int, dict[str, Any]]] = []

    if same_shape and additions and one_target:
        for background in backgrounds:
            for connectivity in (4, 8):
                for selector in ("all", "largest", "smallest", "unique_largest", "unique_smallest"):
                    for paint in paints:
                        for base in ("preserve", "blank"):
                            programs.append((
                                "topology.enclosed_regions",
                                3 + (selector != "all") + (base == "blank") + (connectivity == 8),
                                _program(
                                    "enclosed_regions",
                                    background=background,
                                    connectivity=connectivity,
                                    selector=selector,
                                    paint=paint,
                                    base=base,
                                ),
                            ))

    geometry_actions = ("bbox_frame", "bbox_fill", "bbox_interior", "object_outline", "object_interior")
    if same_shape and two_target:
        for background in backgrounds:
            for source in sources:
                for action in geometry_actions:
                    for paint in paints:
                        bases = ("preserve",) if not one_target else ("preserve", "blank", "support")
                        if one_target:
                            bases = ("preserve", "blank", "support")
                        elif two_target:
                            bases = ("blank", "support")
                        for base in bases:
                            for policy in ("overwrite", "background_only"):
                                programs.append((
                                    "geometry.envelope",
                                    5 + (source != "all_foreground") + (base != "preserve") + (policy != "overwrite"),
                                    _program(
                                        "support_geometry",
                                        background=background,
                                        source=source,
                                        action=action,
                                        paint=paint,
                                        base=base,
                                        paint_policy=policy,
                                    ),
                                ))
    else:
        for background in backgrounds:
            for source in sources:
                for action in ("crop_input", "crop_support"):
                    programs.append((
                        "geometry.envelope",
                        4 + (source != "all_foreground") + (action == "crop_support"),
                        _program("support_geometry", background=background, source=source, action=action),
                    ))

    component_actions: list[str] = []
    if same_shape and two_target:
        if removals:
            component_actions.extend(("isolate_original", "erase_selected"))
        if recolors and one_target:
            component_actions.extend(("recolor_selected", "isolate_recolor"))
        if additions and one_target:
            component_actions.extend(("fill_holes", "bbox_frame", "bbox_fill", "bbox_interior"))
        if removals or recolors:
            component_actions.extend(("extract_outline", "extract_interior"))
    else:
        component_actions.extend(("crop_original", "crop_selected"))

    for background in backgrounds:
        for connectivity in (4, 8):
            for partition in ("color", "foreground"):
                for selector in selectors:
                    for action in component_actions:
                        if action in {"isolate_original", "erase_selected", "crop_original", "crop_selected"}:
                            programs.append((
                                "components.attribute_rule",
                                5 + (selector != "all") + (connectivity == 8) + (partition == "foreground"),
                                _program(
                                    "components",
                                    background=background,
                                    connectivity=connectivity,
                                    partition=partition,
                                    selector=selector,
                                    action=action,
                                ),
                            ))
                            continue
                        for paint in paints:
                            bases = ("preserve", "blank") if action not in {"recolor_selected", "isolate_recolor"} else ("preserve",)
                            for base in bases:
                                policies = ("overwrite", "background_only") if action.startswith("bbox_") else ("overwrite",)
                                for policy in policies:
                                    programs.append((
                                        "components.attribute_rule",
                                        6 + (selector != "all") + (connectivity == 8) + (partition == "foreground") + (base == "blank"),
                                        _program(
                                            "components",
                                            background=background,
                                            connectivity=connectivity,
                                            partition=partition,
                                            selector=selector,
                                            action=action,
                                            paint=paint,
                                            base=base,
                                            paint_policy=policy,
                                        ),
                                    ))

    if same_shape and (additions or recolors) and (preserve_palette or one_target):
        for background in backgrounds:
            for source in sources:
                for scope in ("canvas", "source_bbox"):
                    for group in GROUPS:
                        if preserve_palette:
                            programs.append((
                                "symmetry.subgroup_completion",
                                5 + len(GROUPS[group]) // 2 + (scope == "source_bbox"),
                                _program(
                                    "symmetry_completion",
                                    background=background,
                                    source=source,
                                    scope=scope,
                                    group=group,
                                    base="preserve",
                                    color_mode="preserve",
                                    paint=None,
                                    paint_policy="background_only",
                                ),
                            ))
                        if one_target:
                            for paint in paints:
                                for base in ("preserve", "blank"):
                                    for color_mode in ("constant", "new_constant"):
                                        programs.append((
                                            "symmetry.orbit_painting",
                                            6 + len(GROUPS[group]) // 2 + (scope == "source_bbox") + (base == "blank"),
                                            _program(
                                                "symmetry_completion",
                                                background=background,
                                                source=source,
                                                scope=scope,
                                                group=group,
                                                base=base,
                                                color_mode=color_mode,
                                                paint=paint,
                                                paint_policy="background_only",
                                            ),
                                        ))

    if not same_shape and binary_outputs:
        for panel_background in backgrounds:
            for output_background in backgrounds:
                for axis in ("columns", "rows"):
                    for gap in (0, 1):
                        for operation in (
                            "union",
                            "intersection",
                            "xor",
                            "left_minus_right",
                            "right_minus_left",
                            "equivalence",
                            "complement_left",
                            "complement_right",
                        ):
                            for paint in paints:
                                programs.append((
                                    "masks.boolean_algebra",
                                    4 + gap + (operation not in {"union", "intersection", "xor"}),
                                    _program(
                                        "boolean_panels",
                                        panel_background=panel_background,
                                        output_background=output_background,
                                        axis=axis,
                                        gap=gap,
                                        operation=operation,
                                        paint=paint,
                                    ),
                                ))

    if same_shape and (additions or recolors) and one_target:
        input_colors = sorted({cell for source, _ in train for row in source for cell in row})
        for background in backgrounds:
            for source in (*sources, "span_endpoint_color"):
                for direction in ("rows", "columns", "both"):
                    for span in ("between", "canvas"):
                        bridge_paints = ("source",) if source == "span_endpoint_color" else ("source", *paints)
                        for paint in bridge_paints:
                            for replacement in ("background_only", "any"):
                                programs.append((
                                    "occlusion.line_completion",
                                    4
                                    + (direction == "both")
                                    + (span == "canvas")
                                    + (replacement == "any")
                                    - (source == "span_endpoint_color"),
                                    _program(
                                        "bridge_occlusion",
                                        background=background,
                                        source=source,
                                        direction=direction,
                                        span=span,
                                        paint=paint,
                                        replacement=replacement,
                                    ),
                                ))
                            for occluder in (() if source == "span_endpoint_color" else input_colors):
                                programs.append((
                                    "occlusion.line_completion",
                                    6 + (direction == "both") + (span == "canvas"),
                                    _program(
                                        "bridge_occlusion",
                                        background=background,
                                        source=source,
                                        direction=direction,
                                        span=span,
                                        paint=paint,
                                        replacement="occluder_only",
                                        occluder=occluder,
                                    ),
                                ))

        for background in backgrounds:
            for source in sources:
                for occluder in sources:
                    if occluder == source or occluder == "all_foreground":
                        continue
                    for scope in ("canvas", "source_bbox"):
                        for group in GROUPS:
                            programs.append((
                                "occlusion.symmetry_completion",
                                8 + len(GROUPS[group]) // 2 + (scope == "source_bbox"),
                                _program(
                                    "occlusion_symmetry",
                                    background=background,
                                    source=source,
                                    occluder=occluder,
                                    scope=scope,
                                    group=group,
                                    base="preserve",
                                    color_mode="preserve",
                                    paint=None,
                                    paint_policy="background_only",
                                ),
                            ))

    # Canonical program deduplication happens before the hypothesis budget.
    unique: dict[str, tuple[str, int, dict[str, Any]]] = {}
    for family, complexity, program in programs:
        key = _canonical(program)
        old = unique.get(key)
        record = (family, complexity, program)
        if old is None or (complexity, family) < (old[1], old[0]):
            unique[key] = record
    return sorted(unique.values(), key=lambda item: (item[1], item[0], _canonical(item[2])))


def compile_task(task: Any, limits: Any = None) -> list[dict[str, Any]]:
    """Compile a sanitized task into exact-replay tournament candidates.

    Returned candidates have the common entrant fields ``family``, ``program``,
    ``train_outputs``, ``test_outputs``, ``complexity``, and ``evidence``.  The
    compiler is deterministic and behavior-deduplicated.  It never reads task
    identifiers or test solutions because their presence invalidates the input.
    """

    try:
        train, tests = _sanitize(task)
        candidate_cap, hypothesis_cap = _limits(limits)
        hypotheses = _enumerate_programs(train)[:hypothesis_cap]
    except (KeyError, TypeError, ValueError, OverflowError):
        return []

    exact: list[dict[str, Any]] = []
    best_complexity: int | None = None
    for family, complexity, program in hypotheses:
        # Programs are complexity-sorted.  Once an exact explanation exists,
        # one additional description-length tier is enough to preserve close
        # ambiguity without spending the tournament budget on baroque aliases.
        if best_complexity is not None and complexity > best_complexity + 1:
            break
        replay: list[list[list[int]]] = []
        applicable = True
        try:
            for source, target in train:
                predicted = execute_program(program, source)
                if _grid(predicted) != target:
                    applicable = False
                    break
                replay.append(predicted)
            if not applicable:
                continue
            # Do not admit a vacuous identity explanation into this specialist.
            if all(source == target for source, target in train):
                continue
            predictions = [execute_program(program, source) for source in tests]
        except (KeyError, TypeError, ValueError, IndexError, ArithmeticError):
            continue
        changed = sum(source != target for source, target in train)
        exact.append({
            "family": family,
            "program": program,
            "train_outputs": replay,
            "test_outputs": predictions,
            "complexity": int(complexity),
            "evidence": {
                "train_exact": True,
                "demonstrations": len(train),
                "changed_demonstrations": changed,
                "test_inputs": len(tests),
                "label_access": "training_outputs_only",
            },
        })
        if best_complexity is None:
            best_complexity = complexity

    # Quotient extensionally equivalent held-out behaviors.  Keeping the least
    # complex canonical representative makes the result independent of set or
    # dictionary iteration order while retaining genuinely ambiguous behaviors.
    quotient: dict[str, dict[str, Any]] = {}
    for candidate in exact:
        behavior = _canonical(candidate["test_outputs"])
        old = quotient.get(behavior)
        rank = (candidate["complexity"], candidate["family"], _canonical(candidate["program"]))
        if old is None:
            quotient[behavior] = candidate
        else:
            old_rank = (old["complexity"], old["family"], _canonical(old["program"]))
            if rank < old_rank:
                quotient[behavior] = candidate
    result = sorted(
        quotient.values(),
        key=lambda item: (item["complexity"], item["family"], _canonical(item["program"]), _canonical(item["test_outputs"])),
    )
    return result[:candidate_cap]


__all__ = ["PROGRAM_SCHEMA", "compile_task", "execute_program"]
