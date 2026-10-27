"""Finite object-selection and manipulation entrant for PR-LASM Block 13.

The entrant synthesizes small executable programs over connected components.  It
reads training input/output pairs and test *inputs* only, admits a program only
when it exactly replays every demonstration, and returns deterministic,
JSON-serializable tournament records.  Object selection is deliberately
fail-closed: a selector whose advertised uniqueness is false makes the program
undefined instead of resolving a tie by scan order.

Covered operations include component selection, crop/recolor/isolation,
translation and D4 transforms, edge alignment and packing, marker-directed
copy/stamp, singleton-color transfer, decoy erasure, and bounding-box geometry.

Author: Komorebi P.
"""

from __future__ import annotations

from collections import Counter, deque
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any, Iterator


Grid = tuple[tuple[int, ...], ...]
Cell = tuple[int, int]

SCHEMA = "komorebi.pr_lasm.block13.object_operations.program.v1"
ORTHOGONAL: tuple[Cell, ...] = ((-1, 0), (0, -1), (0, 1), (1, 0))
EIGHT: tuple[Cell, ...] = tuple(
    (dr, dc)
    for dr in (-1, 0, 1)
    for dc in (-1, 0, 1)
    if (dr, dc) != (0, 0)
)

DEFAULTS = {
    "max_candidates": 64,
    "max_programs": 64,
    "max_hypotheses": 180_000,
    "max_grid_cells": 2_500,
    "max_objects": 96,
}
HARD_CAPS = {
    "max_candidates": 256,
    "max_programs": 256,
    "max_hypotheses": 500_000,
    "max_grid_cells": 3_600,
    "max_objects": 256,
}


class Undefined(ValueError):
    """A program is inapplicable or structurally ambiguous on this grid."""


@dataclass(frozen=True, slots=True)
class Component:
    cells: tuple[tuple[int, int, int], ...]

    @property
    def area(self) -> int:
        return len(self.cells)

    @property
    def top(self) -> int:
        return min(row for row, _, _ in self.cells)

    @property
    def bottom(self) -> int:
        return max(row for row, _, _ in self.cells)

    @property
    def left(self) -> int:
        return min(col for _, col, _ in self.cells)

    @property
    def right(self) -> int:
        return max(col for _, col, _ in self.cells)

    @property
    def height(self) -> int:
        return self.bottom - self.top + 1

    @property
    def width(self) -> int:
        return self.right - self.left + 1

    @property
    def bbox_area(self) -> int:
        return self.height * self.width

    @property
    def colors(self) -> tuple[int, ...]:
        return tuple(sorted({color for _, _, color in self.cells}))

    @property
    def center2(self) -> tuple[int, int]:
        return self.top + self.bottom, self.left + self.right

    @property
    def positions(self) -> frozenset[Cell]:
        return frozenset((row, col) for row, col, _ in self.cells)

    def normalized(self, *, include_color: bool = False) -> tuple[Any, ...]:
        if include_color:
            return tuple(
                sorted((row - self.top, col - self.left, color) for row, col, color in self.cells)
            )
        return tuple(sorted((row - self.top, col - self.left) for row, col, _ in self.cells))

    def key(self) -> tuple[Any, ...]:
        return self.top, self.left, self.bottom, self.right, self.colors, self.cells


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _digest(value: Any) -> str:
    return sha256(_canonical(value).encode("utf-8")).hexdigest()


def _plain(grid: Grid) -> list[list[int]]:
    return [list(row) for row in grid]


def _grid(value: Any, max_cells: int) -> Grid:
    if not isinstance(value, (list, tuple)) or not value:
        raise Undefined("grid must be a nonempty sequence")
    rows: list[tuple[int, ...]] = []
    width: int | None = None
    for raw_row in value:
        if not isinstance(raw_row, (list, tuple)) or not raw_row:
            raise Undefined("grid rows must be nonempty sequences")
        row: list[int] = []
        for cell in raw_row:
            if isinstance(cell, bool) or not isinstance(cell, int) or not 0 <= cell <= 9:
                raise Undefined("ARC colors must be integers in [0, 9]")
            row.append(int(cell))
        if width is None:
            width = len(row)
        elif len(row) != width:
            raise Undefined("grid must be rectangular")
        rows.append(tuple(row))
    if len(rows) * int(width or 0) > max_cells:
        raise Undefined("grid exceeds the declared cell budget")
    return tuple(rows)


def _read_limits(value: Any) -> dict[str, int]:
    if value is None:
        return dict(DEFAULTS)
    if not isinstance(value, Mapping):
        raise Undefined("limits must be a mapping")
    result = dict(DEFAULTS)
    for name, default in DEFAULTS.items():
        if name not in value:
            continue
        candidate = value[name]
        if isinstance(candidate, bool) or not isinstance(candidate, int) or candidate < 1:
            raise Undefined(f"invalid limit {name}")
        result[name] = min(candidate, HARD_CAPS[name])
    # ``candidate_cap`` is the tournament-wide spelling used by some callers.
    if "candidate_cap" in value:
        candidate = value["candidate_cap"]
        if isinstance(candidate, bool) or not isinstance(candidate, int) or candidate < 1:
            raise Undefined("invalid limit candidate_cap")
        result["max_candidates"] = min(candidate, HARD_CAPS["max_candidates"])
    return result


def _sanitize(
    task: Any, limits: Mapping[str, int]
) -> tuple[tuple[tuple[Grid, Grid], ...], tuple[Grid, ...]]:
    """Copy only permitted fields; in particular never inspect test labels."""

    if not isinstance(task, Mapping):
        raise Undefined("task must be a mapping")
    try:
        raw_train = task["train"]
        raw_test = task["test"]
    except (KeyError, TypeError) as error:
        raise Undefined("task needs train and test") from error
    if (
        not isinstance(raw_train, Sequence)
        or isinstance(raw_train, (str, bytes))
        or not raw_train
        or not isinstance(raw_test, Sequence)
        or isinstance(raw_test, (str, bytes))
    ):
        raise Undefined("invalid split")
    train: list[tuple[Grid, Grid]] = []
    tests: list[Grid] = []
    for example in raw_train:
        if not isinstance(example, Mapping):
            raise Undefined("invalid demonstration")
        try:
            source = _grid(example["input"], limits["max_grid_cells"])
            target = _grid(example["output"], limits["max_grid_cells"])
        except (KeyError, TypeError) as error:
            raise Undefined("invalid demonstration") from error
        train.append((source, target))
    for example in raw_test:
        if not isinstance(example, Mapping):
            raise Undefined("invalid test input")
        try:
            source = _grid(example["input"], limits["max_grid_cells"])
        except (KeyError, TypeError) as error:
            raise Undefined("invalid test input") from error
        tests.append(source)
    return tuple(train), tuple(tests)


def _shape(grid: Grid) -> tuple[int, int]:
    return len(grid), len(grid[0])


def _unique_extreme(values: Sequence[tuple[int, Component]], *, maximum: bool) -> Component:
    if not values:
        raise Undefined("empty selector population")
    wanted = max(value for value, _ in values) if maximum else min(value for value, _ in values)
    selected = [component for value, component in values if value == wanted]
    if len(selected) != 1:
        raise Undefined("selector extreme is tied")
    return selected[0]


def _unique_color(counts: Counter[int], *, maximum: bool) -> int:
    if not counts:
        raise Undefined("empty color population")
    wanted = max(counts.values()) if maximum else min(counts.values())
    colors = sorted(color for color, count in counts.items() if count == wanted)
    if len(colors) != 1:
        raise Undefined("color role is tied")
    return colors[0]


def _background(grid: Grid, spec: str) -> int:
    height, width = _shape(grid)
    if spec.startswith("literal:"):
        return int(spec.split(":", 1)[1])
    if spec == "mode":
        values = [cell for row in grid for cell in row]
    elif spec == "border_mode":
        values = [
            grid[row][col]
            for row in range(height)
            for col in range(width)
            if row in {0, height - 1} or col in {0, width - 1}
        ]
    elif spec == "corner_mode":
        values = [grid[0][0], grid[0][-1], grid[-1][0], grid[-1][-1]]
    else:
        raise Undefined("unknown background role")
    return _unique_color(Counter(values), maximum=True)


def _components(
    grid: Grid,
    background: int,
    connectivity: int,
    partition: str,
    max_objects: int,
) -> tuple[Component, ...]:
    if connectivity not in (4, 8) or partition not in {"mono", "foreground"}:
        raise Undefined("invalid component grammar")
    steps = ORTHOGONAL if connectivity == 4 else EIGHT
    height, width = _shape(grid)
    seen: set[Cell] = set()
    result: list[Component] = []
    for row in range(height):
        for col in range(width):
            if (row, col) in seen or grid[row][col] == background:
                continue
            seed_color = grid[row][col]
            seen.add((row, col))
            queue = deque([(row, col)])
            cells: list[tuple[int, int, int]] = []
            while queue:
                current_row, current_col = queue.popleft()
                color = grid[current_row][current_col]
                cells.append((current_row, current_col, color))
                for dr, dc in steps:
                    other_row, other_col = current_row + dr, current_col + dc
                    if not (0 <= other_row < height and 0 <= other_col < width):
                        continue
                    if (other_row, other_col) in seen or grid[other_row][other_col] == background:
                        continue
                    if partition == "mono" and grid[other_row][other_col] != seed_color:
                        continue
                    seen.add((other_row, other_col))
                    queue.append((other_row, other_col))
            result.append(Component(tuple(sorted(cells))))
            if len(result) > max_objects:
                raise Undefined("object count exceeds budget")
    return tuple(sorted(result, key=Component.key))


def _select(
    objects: Sequence[Component],
    selector: str,
    grid: Grid,
    background: int,
) -> tuple[Component, ...]:
    if not objects:
        raise Undefined("no objects")
    if selector == "all":
        return tuple(objects)
    if selector == "singletons":
        selected = tuple(obj for obj in objects if obj.area == 1)
        if not selected:
            raise Undefined("no singleton objects")
        return selected
    if selector == "non_singletons":
        selected = tuple(obj for obj in objects if obj.area > 1)
        if not selected:
            raise Undefined("no non-singleton objects")
        return selected
    if selector == "unique_singleton":
        selected = tuple(obj for obj in objects if obj.area == 1)
        if len(selected) != 1:
            raise Undefined("singleton selector is not unique")
        return selected
    if selector == "unique_non_singleton":
        selected = tuple(obj for obj in objects if obj.area > 1)
        if len(selected) != 1:
            raise Undefined("non-singleton selector is not unique")
        return selected

    attribute_getters = {
        "area": lambda obj: obj.area,
        "bbox_area": lambda obj: obj.bbox_area,
        "height": lambda obj: obj.height,
        "width": lambda obj: obj.width,
        "density_scaled": lambda obj: obj.area * 10_000 // obj.bbox_area,
    }
    if selector.startswith("unique_largest_") or selector.startswith("unique_smallest_"):
        maximum = selector.startswith("unique_largest_")
        attribute = selector.split("_", 2)[2]
        getter = attribute_getters.get(attribute)
        if getter is None:
            raise Undefined("unknown object attribute")
        return (_unique_extreme([(getter(obj), obj) for obj in objects], maximum=maximum),)

    spatial = {
        "unique_topmost": (lambda obj: obj.top, False),
        "unique_bottommost": (lambda obj: obj.bottom, True),
        "unique_leftmost": (lambda obj: obj.left, False),
        "unique_rightmost": (lambda obj: obj.right, True),
    }
    if selector in spatial:
        getter, maximum = spatial[selector]
        return (_unique_extreme([(getter(obj), obj) for obj in objects], maximum=maximum),)

    if selector in {"unique_area_frequency", "unique_shape", "unique_colored_shape"}:
        if selector == "unique_area_frequency":
            keys = [obj.area for obj in objects]
        elif selector == "unique_shape":
            keys = [obj.normalized() for obj in objects]
        else:
            keys = [obj.normalized(include_color=True) for obj in objects]
        counts = Counter(keys)
        selected = tuple(obj for obj, key in zip(objects, keys) if counts[key] == 1)
        if len(selected) != 1:
            raise Undefined("uniqueness selector has no single result")
        return selected

    if selector.startswith("color:"):
        spec = selector.split(":", 1)[1]
        color = _resolve_color(grid, background, spec, objects=objects, selected=())
        selected = tuple(obj for obj in objects if color in obj.colors)
        if not selected:
            raise Undefined("color selector is empty")
        return selected

    if selector.startswith("unique_color:"):
        spec = selector.split(":", 1)[1]
        color = _resolve_color(grid, background, spec, objects=objects, selected=())
        selected = tuple(obj for obj in objects if color in obj.colors)
        if len(selected) != 1:
            raise Undefined("color selector is not unique")
        return selected

    raise Undefined("unknown selector")


def _resolve_color(
    grid: Grid,
    background: int,
    spec: str,
    *,
    objects: Sequence[Component],
    selected: Sequence[Component],
    marker: Component | None = None,
) -> int:
    if spec.startswith("literal:"):
        return int(spec.split(":", 1)[1])
    if spec == "background":
        return background
    if spec == "selected_color":
        colors = {color for obj in selected for color in obj.colors}
        if len(colors) != 1:
            raise Undefined("selected objects lack one color")
        return next(iter(colors))
    if spec == "marker_color":
        markers = [obj for obj in objects if obj.area == 1 and obj not in selected]
        colors = {obj.cells[0][2] for obj in markers}
        if len(colors) != 1:
            raise Undefined("marker color is not unique")
        return next(iter(colors))
    if spec == "this_marker_color":
        if marker is None or marker.area != 1:
            raise Undefined("a singleton marker is required")
        return marker.cells[0][2]
    counts = Counter(cell for row in grid for cell in row if cell != background)
    if spec == "foreground_unique":
        if len(counts) != 1:
            raise Undefined("foreground color is not unique")
        return next(iter(counts))
    if spec == "foreground_most":
        return _unique_color(counts, maximum=True)
    if spec == "foreground_least":
        return _unique_color(counts, maximum=False)
    if spec == "component_color_most":
        component_counts = Counter(color for obj in objects for color in obj.colors)
        return _unique_color(component_counts, maximum=True)
    if spec == "component_color_least":
        component_counts = Counter(color for obj in objects for color in obj.colors)
        return _unique_color(component_counts, maximum=False)
    raise Undefined("unknown color role")


def _blank(height: int, width: int, color: int) -> list[list[int]]:
    return [[color for _ in range(width)] for _ in range(height)]


def _crop(canvas: Sequence[Sequence[int]], cells: Iterable[Cell]) -> Grid:
    positions = tuple(cells)
    if not positions:
        raise Undefined("cannot crop empty support")
    top = min(row for row, _ in positions)
    bottom = max(row for row, _ in positions)
    left = min(col for _, col in positions)
    right = max(col for _, col in positions)
    return tuple(tuple(int(canvas[row][col]) for col in range(left, right + 1)) for row in range(top, bottom + 1))


def _outline_positions(component: Component) -> frozenset[Cell]:
    support = component.positions
    return frozenset(
        (row, col)
        for row, col in support
        if any((row + dr, col + dc) not in support for dr, dc in ORTHOGONAL)
    )


def _bbox_positions(component: Component, action: str) -> frozenset[Cell]:
    all_cells = frozenset(
        (row, col)
        for row in range(component.top, component.bottom + 1)
        for col in range(component.left, component.right + 1)
    )
    frame = frozenset(
        (row, col)
        for row, col in all_cells
        if row in {component.top, component.bottom} or col in {component.left, component.right}
    )
    if action == "bbox_fill":
        return all_cells
    if action == "bbox_frame":
        return frame
    if action == "bbox_interior":
        return all_cells - frame
    if action == "outline":
        return _outline_positions(component)
    raise Undefined("unknown geometry action")


def _base_canvas(
    grid: Grid,
    background: int,
    objects: Sequence[Component],
    selected: Sequence[Component],
    base: str,
) -> list[list[int]]:
    height, width = _shape(grid)
    if base == "preserve":
        return [list(row) for row in grid]
    if base == "blank":
        return _blank(height, width, background)
    canvas = [list(row) for row in grid]
    if base == "erase_selected":
        erased = selected
    elif base == "erase_all_objects":
        erased = objects
    elif base == "erase_decoys":
        erased = [obj for obj in objects if obj not in selected]
    elif base == "erase_markers":
        erased = [obj for obj in objects if obj.area == 1 and obj not in selected]
    else:
        raise Undefined("unknown canvas base")
    for obj in erased:
        for row, col, _ in obj.cells:
            canvas[row][col] = background
    return canvas


def _paint_component_cells(
    canvas: list[list[int]],
    component: Component,
    color: int | None,
) -> None:
    for row, col, old_color in component.cells:
        canvas[row][col] = old_color if color is None else color


def _execute_component_action(
    program: Mapping[str, Any],
    grid: Grid,
    objects: Sequence[Component],
    selected: Sequence[Component],
    background: int,
) -> Grid:
    action = str(program["action"])
    paint_spec = program.get("paint")
    paint = None
    if paint_spec is not None and paint_spec != "preserve":
        paint = _resolve_color(
            grid, background, str(paint_spec), objects=objects, selected=selected
        )
    base = str(program.get("base", "preserve"))
    canvas = _base_canvas(grid, background, objects, selected, base)

    if action in {"recolor", "isolate", "erase", "crop_original", "crop_selected", "crop_recolor"}:
        if action == "erase":
            for obj in selected:
                for row, col, _ in obj.cells:
                    canvas[row][col] = background
        elif action not in {"crop_original"}:
            for obj in selected:
                _paint_component_cells(canvas, obj, paint)
        if action.startswith("crop_"):
            positions = frozenset((row, col) for obj in selected for row, col, _ in obj.cells)
            return _crop(canvas, positions)
        return tuple(tuple(row) for row in canvas)

    if action in {"bbox_frame", "bbox_fill", "bbox_interior", "outline"}:
        if paint is None:
            raise Undefined("geometry needs a paint")
        policy = str(program.get("policy", "overwrite"))
        for obj in selected:
            for row, col in _bbox_positions(obj, action):
                if policy == "background_only" and canvas[row][col] != background:
                    continue
                canvas[row][col] = paint
        return tuple(tuple(row) for row in canvas)
    raise Undefined("unknown component action")


def _transform_cells(component: Component, transform: str) -> tuple[tuple[int, int, int], ...]:
    height, width = component.height, component.width
    relative = [(row - component.top, col - component.left, color) for row, col, color in component.cells]
    transformed: list[tuple[int, int, int]] = []
    for row, col, color in relative:
        if transform == "identity":
            new_row, new_col = row, col
        elif transform == "r90":
            new_row, new_col = col, height - 1 - row
        elif transform == "r180":
            new_row, new_col = height - 1 - row, width - 1 - col
        elif transform == "r270":
            new_row, new_col = width - 1 - col, row
        elif transform == "mirror_lr":
            new_row, new_col = row, width - 1 - col
        elif transform == "mirror_tb":
            new_row, new_col = height - 1 - row, col
        elif transform == "transpose":
            new_row, new_col = col, row
        elif transform == "anti_transpose":
            new_row, new_col = width - 1 - col, height - 1 - row
        else:
            raise Undefined("unknown D4 transform")
        transformed.append((new_row, new_col, color))
    return tuple(sorted(transformed))


def _transformed_shape(cells: Sequence[tuple[int, int, int]]) -> tuple[int, int]:
    if not cells:
        raise Undefined("empty transformed component")
    return max(row for row, _, _ in cells) + 1, max(col for _, col, _ in cells) + 1


def _marker_objects(
    objects: Sequence[Component], selected: Sequence[Component], *, unique: bool
) -> tuple[Component, ...]:
    markers = tuple(obj for obj in objects if obj.area == 1 and obj not in selected)
    if not markers or (unique and len(markers) != 1):
        raise Undefined("marker population is not valid")
    return markers


def _anchor(
    destination: str,
    grid_shape: tuple[int, int],
    object_shape: tuple[int, int],
    original: Component,
    marker: Component | None,
) -> Cell:
    height, width = grid_shape
    object_height, object_width = object_shape
    if destination == "same_bbox":
        return original.top, original.left
    anchors = {
        "top_left": (0, 0),
        "top_right": (0, width - object_width),
        "bottom_left": (height - object_height, 0),
        "bottom_right": (height - object_height, width - object_width),
        "top_center": (0, (width - object_width) // 2),
        "bottom_center": (height - object_height, (width - object_width) // 2),
        "left_center": ((height - object_height) // 2, 0),
        "right_center": ((height - object_height) // 2, width - object_width),
        "center": ((height - object_height) // 2, (width - object_width) // 2),
        "center_ceil": ((height - object_height + 1) // 2, (width - object_width + 1) // 2),
        "to_top": (0, original.left),
        "to_bottom": (height - object_height, original.left),
        "to_left": (original.top, 0),
        "to_right": (original.top, width - object_width),
    }
    if destination in anchors:
        return anchors[destination]
    if marker is None:
        raise Undefined("destination needs a marker")
    marker_row, marker_col, _ = marker.cells[0]
    marker_anchors = {
        "marker_top_left": (marker_row, marker_col),
        "marker_center": (marker_row - (object_height - 1) // 2, marker_col - (object_width - 1) // 2),
        "marker_center_ceil": (marker_row - object_height // 2, marker_col - object_width // 2),
        "marker_above": (marker_row - object_height, marker_col - (object_width - 1) // 2),
        "marker_below": (marker_row + 1, marker_col - (object_width - 1) // 2),
        "marker_left": (marker_row - (object_height - 1) // 2, marker_col - object_width),
        "marker_right": (marker_row - (object_height - 1) // 2, marker_col + 1),
    }
    if destination not in marker_anchors:
        raise Undefined("unknown destination")
    return marker_anchors[destination]


def _place_cells(
    canvas: list[list[int]],
    cells: Sequence[tuple[int, int, int]],
    top: int,
    left: int,
    *,
    background: int,
    color: int | None,
    policy: str,
) -> None:
    height, width = len(canvas), len(canvas[0])
    targets = [(top + row, left + col, old_color if color is None else color) for row, col, old_color in cells]
    if any(not (0 <= row < height and 0 <= col < width) for row, col, _ in targets):
        raise Undefined("placement is outside the canvas")
    if policy == "fail" and any(canvas[row][col] != background for row, col, _ in targets):
        raise Undefined("placement collides")
    for row, col, value in targets:
        if policy == "background_only" and canvas[row][col] != background:
            continue
        canvas[row][col] = value


def _execute_move(
    program: Mapping[str, Any],
    grid: Grid,
    objects: Sequence[Component],
    selected: Sequence[Component],
    background: int,
) -> Grid:
    if len(selected) != 1:
        raise Undefined("move requires one selected object")
    obj = selected[0]
    destination = str(program["destination"])
    marker = None
    if destination.startswith("marker_"):
        marker = _marker_objects(objects, selected, unique=True)[0]
    cells = _transform_cells(obj, str(program.get("transform", "identity")))
    object_shape = _transformed_shape(cells)
    top, left = _anchor(destination, _shape(grid), object_shape, obj, marker)
    canvas = _base_canvas(
        grid, background, objects, selected, str(program.get("base", "erase_selected"))
    )
    if bool(program.get("erase_marker", False)) and marker is not None:
        marker_row, marker_col, _ = marker.cells[0]
        canvas[marker_row][marker_col] = background
    paint_spec = str(program.get("paint", "preserve"))
    paint = None
    if paint_spec != "preserve":
        paint = _resolve_color(
            grid, background, paint_spec, objects=objects, selected=selected, marker=marker
        )
    _place_cells(
        canvas,
        cells,
        top,
        left,
        background=background,
        color=paint,
        policy=str(program.get("policy", "overwrite")),
    )
    return tuple(tuple(row) for row in canvas)


def _execute_stamp(
    program: Mapping[str, Any],
    grid: Grid,
    objects: Sequence[Component],
    selected: Sequence[Component],
    background: int,
) -> Grid:
    if len(selected) != 1:
        raise Undefined("stamping needs one template")
    template = selected[0]
    markers = _marker_objects(objects, selected, unique=False)
    cells = _transform_cells(template, str(program.get("transform", "identity")))
    object_shape = _transformed_shape(cells)
    canvas = _base_canvas(
        grid, background, objects, selected, str(program.get("base", "preserve"))
    )
    erase_markers = bool(program.get("erase_markers", True))
    for marker in markers:
        if erase_markers:
            row, col, _ = marker.cells[0]
            canvas[row][col] = background
    for marker in markers:
        top, left = _anchor(
            str(program["anchor"]), _shape(grid), object_shape, template, marker
        )
        paint_spec = str(program.get("paint", "preserve"))
        paint = None
        if paint_spec != "preserve":
            paint = _resolve_color(
                grid,
                background,
                paint_spec,
                objects=objects,
                selected=selected,
                marker=marker,
            )
        _place_cells(
            canvas,
            cells,
            top,
            left,
            background=background,
            color=paint,
            policy=str(program.get("policy", "overwrite")),
        )
    return tuple(tuple(row) for row in canvas)


def _order_objects(objects: Sequence[Component], order: str) -> list[Component]:
    keys = {
        "spatial": lambda obj: (obj.top, obj.left, obj.key()),
        "spatial_reverse": lambda obj: (-obj.top, -obj.left, obj.key()),
        "area_ascending": lambda obj: (obj.area, obj.top, obj.left, obj.key()),
        "area_descending": lambda obj: (-obj.area, obj.top, obj.left, obj.key()),
        "height_ascending": lambda obj: (obj.height, obj.width, obj.top, obj.left, obj.key()),
        "height_descending": lambda obj: (-obj.height, -obj.width, obj.top, obj.left, obj.key()),
        "color_ascending": lambda obj: (obj.colors, obj.top, obj.left, obj.key()),
        "color_descending": lambda obj: (tuple(-color for color in obj.colors), obj.top, obj.left, obj.key()),
    }
    if order not in keys:
        raise Undefined("unknown component ordering")
    return sorted(objects, key=keys[order])


def _execute_align_pack(
    program: Mapping[str, Any],
    grid: Grid,
    objects: Sequence[Component],
    selected: Sequence[Component],
    background: int,
) -> Grid:
    ordered = _order_objects(selected, str(program.get("order", "spatial")))
    output_mode = str(program.get("output", "canvas"))
    canvas = _base_canvas(
        grid, background, objects, selected, str(program.get("base", "erase_selected"))
    )
    layout = str(program["layout"])
    gap = int(program.get("gap", 0))
    placements: list[tuple[Component, int, int]] = []
    height, width = _shape(grid)

    if layout.startswith("align_"):
        for obj in ordered:
            if layout == "align_top":
                top, left = 0, obj.left
            elif layout == "align_bottom":
                top, left = height - obj.height, obj.left
            elif layout == "align_left":
                top, left = obj.top, 0
            elif layout == "align_right":
                top, left = obj.top, width - obj.width
            elif layout == "align_center_row":
                top, left = (height - obj.height) // 2, obj.left
            elif layout == "align_center_col":
                top, left = obj.top, (width - obj.width) // 2
            else:
                raise Undefined("unknown alignment")
            placements.append((obj, top, left))
    elif layout in {"pack_row", "pack_column"}:
        if layout == "pack_row":
            total_width = sum(obj.width for obj in ordered) + gap * (len(ordered) - 1)
            total_height = max(obj.height for obj in ordered)
        else:
            total_height = sum(obj.height for obj in ordered) + gap * (len(ordered) - 1)
            total_width = max(obj.width for obj in ordered)
        anchor = str(program.get("anchor", "top_left"))
        origins = {
            "top_left": (0, 0),
            "top_right": (0, width - total_width),
            "bottom_left": (height - total_height, 0),
            "bottom_right": (height - total_height, width - total_width),
            "center": ((height - total_height) // 2, (width - total_width) // 2),
        }
        if anchor not in origins:
            raise Undefined("unknown pack anchor")
        cursor_row, cursor_col = origins[anchor]
        for obj in ordered:
            if layout == "pack_row":
                placements.append((obj, cursor_row, cursor_col))
                cursor_col += obj.width + gap
            else:
                placements.append((obj, cursor_row, cursor_col))
                cursor_row += obj.height + gap
    else:
        raise Undefined("unknown layout")

    occupied: set[Cell] = set()
    for obj, top, left in placements:
        cells = _transform_cells(obj, "identity")
        targets = {(top + row, left + col) for row, col, _ in cells}
        if targets & occupied:
            raise Undefined("packed objects overlap")
        occupied.update(targets)
        _place_cells(
            canvas,
            cells,
            top,
            left,
            background=background,
            color=None,
            policy=str(program.get("policy", "overwrite")),
        )
    result = tuple(tuple(row) for row in canvas)
    if output_mode == "crop":
        return _crop(result, occupied)
    if output_mode != "canvas":
        raise Undefined("unknown pack output mode")
    return result


def execute_program(program: Mapping[str, Any], value: Any) -> list[list[int]]:
    """Execute one emitted program without consulting any stored predictions."""

    if not isinstance(program, Mapping) or program.get("schema") != SCHEMA:
        raise ValueError("invalid object-operations program")
    grid = _grid(value, HARD_CAPS["max_grid_cells"])
    background = _background(grid, str(program["background"]))
    objects = _components(
        grid,
        background,
        int(program["connectivity"]),
        str(program["partition"]),
        HARD_CAPS["max_objects"],
    )
    selected = _select(objects, str(program["selector"]), grid, background)
    op = str(program["op"])
    if op == "component_action":
        output = _execute_component_action(program, grid, objects, selected, background)
    elif op == "move":
        output = _execute_move(program, grid, objects, selected, background)
    elif op == "stamp":
        output = _execute_stamp(program, grid, objects, selected, background)
    elif op == "align_pack":
        output = _execute_align_pack(program, grid, objects, selected, background)
    else:
        raise ValueError("unknown object-operations opcode")
    return _plain(output)


def _program(op: str, background: str, connectivity: int, partition: str, selector: str, **fields: Any) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "op": op,
        "background": background,
        "connectivity": connectivity,
        "partition": partition,
        "selector": selector,
        **fields,
    }


def _training_specs(train: Sequence[tuple[Grid, Grid]]) -> tuple[list[str], list[str]]:
    input_palettes = [{cell for row in source for cell in row} for source, _ in train]
    common_input = set.intersection(*input_palettes)
    output_colors = {cell for _, target in train for row in target for cell in row}
    backgrounds = ["mode", "border_mode", "corner_mode"]
    for color in sorted(common_input):
        backgrounds.append(f"literal:{color}")
    backgrounds = list(dict.fromkeys(backgrounds))[:6]

    colors = [
        "selected_color",
        "marker_color",
        "foreground_unique",
        "foreground_most",
        "foreground_least",
        "component_color_most",
        "component_color_least",
    ]
    colors.extend(f"literal:{color}" for color in sorted(output_colors | common_input))
    return backgrounds, list(dict.fromkeys(colors))


def _selector_specs() -> tuple[str, ...]:
    color_roles = (
        "foreground_unique",
        "foreground_most",
        "foreground_least",
        "component_color_most",
        "component_color_least",
    )
    selectors = [
        "all",
        "unique_non_singleton",
        "unique_singleton",
        "non_singletons",
        "singletons",
        "unique_largest_area",
        "unique_smallest_area",
        "unique_largest_bbox_area",
        "unique_smallest_bbox_area",
        "unique_largest_height",
        "unique_smallest_height",
        "unique_largest_width",
        "unique_smallest_width",
        "unique_largest_density_scaled",
        "unique_smallest_density_scaled",
        "unique_topmost",
        "unique_bottommost",
        "unique_leftmost",
        "unique_rightmost",
        "unique_area_frequency",
        "unique_shape",
        "unique_colored_shape",
    ]
    selectors.extend(f"unique_color:{role}" for role in color_roles)
    return tuple(selectors)


def _effect_profile(
    train: Sequence[tuple[Grid, Grid]],
) -> tuple[bool, bool, bool]:
    """Return whether same-shaped demos add, remove, or recolor support."""

    additions = removals = recolors = False
    for source, target in train:
        if _shape(source) != _shape(target):
            continue
        counts = Counter(cell for row in source for cell in row)
        background = min(counts, key=lambda color: (-counts[color], color))
        for before_row, after_row in zip(source, target):
            for before, after in zip(before_row, after_row):
                if before == after:
                    continue
                if before == background and after != background:
                    additions = True
                elif before != background and after == background:
                    removals = True
                else:
                    recolors = True
    return additions, removals, recolors


def _enumerate_programs(train: Sequence[tuple[Grid, Grid]]) -> Iterator[tuple[int, str, dict[str, Any]]]:
    backgrounds, paints = _training_specs(train)
    shared_colors = set.intersection(
        *({cell for row in source for cell in row} for source, _ in train)
    )
    selectors = tuple(
        dict.fromkeys(
            (*_selector_specs(),
             *(f"color:literal:{color}" for color in sorted(shared_colors)),
             *(f"unique_color:literal:{color}" for color in sorted(shared_colors)))
        )
    )
    same_shape = all(_shape(source) == _shape(target) for source, target in train)
    any_shape_change = any(_shape(source) != _shape(target) for source, target in train)
    additions, removals, recolors = _effect_profile(train)
    specs = [(background, connectivity, partition) for background in backgrounds for connectivity in (4, 8) for partition in ("mono", "foreground")]

    # Small object rules come first in the MDL ordering.
    for background, connectivity, partition in specs:
        for selector in selectors:
            selector_cost = 0 if selector in {"all", "unique_non_singleton", "unique_largest_area"} else 1
            if any_shape_change:
                for action, base in (
                    ("crop_original", "preserve"),
                    ("crop_selected", "blank"),
                ):
                    yield 4 + selector_cost, "objects.crop", _program(
                        "component_action", background, connectivity, partition, selector,
                        action=action, base=base, paint="preserve"
                    )
                for paint in paints:
                    yield 6 + selector_cost, "objects.crop_recolor", _program(
                        "component_action", background, connectivity, partition, selector,
                        action="crop_recolor", base="blank", paint=paint
                    )
            if same_shape:
                if removals:
                    for action, base, paint in (
                        ("isolate", "erase_decoys", "preserve"),
                        ("erase", "preserve", "background"),
                    ):
                        yield 4 + selector_cost, "objects.filter", _program(
                            "component_action", background, connectivity, partition, selector,
                            action=action, base=base, paint=paint
                        )
                if recolors:
                    for paint in paints:
                        yield 5 + selector_cost, "objects.recolor", _program(
                            "component_action", background, connectivity, partition, selector,
                            action="recolor", base="preserve", paint=paint
                        )
                        if removals:
                            yield 6 + selector_cost, "objects.isolate_recolor", _program(
                                "component_action", background, connectivity, partition, selector,
                                action="isolate", base="erase_decoys", paint=paint
                            )
                if additions:
                    for paint in paints:
                        for action in ("bbox_frame", "bbox_fill", "bbox_interior", "outline"):
                            # These are the two useful geometric semantics: add
                            # to a scene or render a clean geometric summary.
                            for base, policy in (("preserve", "background_only"), ("blank", "overwrite")):
                                yield 7 + selector_cost + (base == "blank") + (policy == "background_only"), "objects.geometry", _program(
                                    "component_action", background, connectivity, partition, selector,
                                    action=action, base=base, paint=paint, policy=policy
                                )

    if same_shape and additions:
        single_selectors = tuple(
            selector for selector in selectors
            if selector not in {"all", "singletons", "non_singletons"}
        )
        destinations = (
            "same_bbox", "top_left", "top_right", "bottom_left", "bottom_right",
            "top_center", "bottom_center", "left_center", "right_center",
            "center", "center_ceil", "to_top", "to_bottom", "to_left", "to_right",
            "marker_top_left", "marker_center", "marker_center_ceil",
            "marker_above", "marker_below", "marker_left", "marker_right",
        )
        transforms = (
            "identity", "r90", "r180", "r270", "mirror_lr", "mirror_tb",
            "transpose", "anti_transpose",
        )
        for background, connectivity, partition in specs:
            for selector in single_selectors:
                selector_cost = 0 if selector in {"unique_non_singleton", "unique_largest_area"} else 1
                for destination in destinations:
                    marker_cost = 1 if destination.startswith("marker_") else 0
                    # Translation and D4 transformation are separate low-MDL
                    # axes.  Their unrestricted Cartesian product burns a
                    # finite budget on elaborate compositions before stamp and
                    # pack families receive a heat.  Canvas/marker anchors use
                    # identity, while ``same_bbox`` is the complete D4 heat.
                    destination_transforms = (
                        transforms
                        if destination == "same_bbox"
                        else ("identity",)
                    )
                    for transform in destination_transforms:
                        transform_cost = 0 if transform == "identity" else 2
                        move_bases = ("erase_selected", "blank", "preserve") if removals else ("preserve",)
                        for base in move_bases:
                            base_cost = {"erase_selected": 0, "blank": 1, "preserve": 1}[base]
                            paint_specs = ("preserve", "marker_color") if destination.startswith("marker_") else ("preserve",)
                            for paint in paint_specs:
                                erase_options = (False, True) if destination.startswith("marker_") else (False,)
                                for erase_marker in erase_options:
                                    yield 6 + selector_cost + marker_cost + transform_cost + base_cost + (paint != "preserve") + erase_marker, "objects.move_d4", _program(
                                        "move", background, connectivity, partition, selector,
                                        destination=destination, transform=transform, base=base,
                                        paint=paint, erase_marker=erase_marker, policy="overwrite"
                                    )

        # Repeated stamping is useful only when singleton markers coexist with
        # a non-singleton template, so those selectors are sufficient.
        stamp_selectors = ("unique_non_singleton", "unique_largest_area", "unique_colored_shape")
        stamp_anchors = (
            "marker_top_left", "marker_center", "marker_center_ceil",
            "marker_above", "marker_below", "marker_left", "marker_right",
        )
        for background, connectivity, partition in specs:
            for selector in stamp_selectors:
                for anchor in stamp_anchors:
                    for transform in ("identity", "r90", "r180", "r270", "mirror_lr", "mirror_tb"):
                        for base in ("preserve", "erase_selected", "blank"):
                            for paint in ("preserve", "this_marker_color"):
                                yield 8 + (transform != "identity") * 2 + (base != "preserve") + (paint != "preserve"), "objects.marker_stamp", _program(
                                    "stamp", background, connectivity, partition, selector,
                                    anchor=anchor, transform=transform, base=base, paint=paint,
                                    erase_markers=True, policy="overwrite"
                                )

        if removals:
            layouts = (
                "align_top", "align_bottom", "align_left", "align_right",
                "align_center_row", "align_center_col", "pack_row", "pack_column",
            )
            orders = (
                "spatial", "spatial_reverse", "area_ascending", "area_descending",
                "height_ascending", "height_descending", "color_ascending", "color_descending",
            )
            for background, connectivity, partition in specs:
                for selector in ("all", "non_singletons"):
                    for layout in layouts:
                        for order in orders:
                            for gap in (0, 1):
                                anchors = ("top_left",) if layout.startswith("align_") else (
                                    "top_left", "top_right", "bottom_left", "bottom_right", "center"
                                )
                                for anchor in anchors:
                                    yield 7 + (selector != "all") + (order != "spatial") + gap + (anchor != "top_left"), "objects.align_pack", _program(
                                        "align_pack", background, connectivity, partition, selector,
                                        layout=layout, order=order, gap=gap, anchor=anchor,
                                        base="erase_selected", output="canvas", policy="overwrite"
                                    )

    if any_shape_change:
        # Packed minimal outputs catch object serialization tasks.
        for background, connectivity, partition in specs:
            for layout in ("pack_row", "pack_column"):
                for order in ("spatial", "area_ascending", "area_descending", "color_ascending"):
                    for gap in (0, 1):
                        yield 8 + (order != "spatial") + gap, "objects.pack_crop", _program(
                            "align_pack", background, connectivity, partition, "all",
                            layout=layout, order=order, gap=gap, anchor="top_left",
                            base="blank", output="crop", policy="overwrite"
                        )


def _rank(record: Mapping[str, Any]) -> tuple[Any, ...]:
    evidence = record["evidence"]
    return (
        int(record["complexity"]),
        -int(evidence.get("mechanism_support", 1)),
        str(record["family"]),
        _canonical(record["program"]),
    )


def compile_task(task: Any, limits: Any = None) -> list[dict[str, Any]]:
    """Return finite, exact-demonstration-replay object hypotheses.

    ``max_programs`` caps returned behaviorally distinct programs.  In
    particular, ``max_programs=1`` returns the single minimum-description-length
    survivor.  ``max_hypotheses`` separately bounds synthesis work.
    """

    try:
        bounds = _read_limits(limits)
        train, tests = _sanitize(task, bounds)
    except (KeyError, TypeError, ValueError, OverflowError):
        return []
    if all(source == target for source, target in train):
        return []

    # Materialize and MDL-sort the bounded grammar once.  This makes the
    # ``max_programs=1`` promise meaningful across families rather than making
    # it depend on source-code enumeration order.
    enumerated: dict[str, tuple[int, str, dict[str, Any]]] = {}
    for complexity, family, program in _enumerate_programs(train):
        key = _canonical(program)
        old = enumerated.get(key)
        if old is None or (complexity, family) < (old[0], old[1]):
            enumerated[key] = (complexity, family, program)
    ordered = sorted(
        enumerated.values(),
        key=lambda item: (item[0], item[1], _canonical(item[2])),
    )[: bounds["max_hypotheses"]]

    hypotheses = 0
    exact: list[dict[str, Any]] = []
    mechanisms_by_behavior: dict[str, set[str]] = {}
    records_by_behavior: dict[str, dict[str, Any]] = {}
    best_complexity: int | None = None
    for complexity, family, program in ordered:
        if best_complexity is not None and complexity > best_complexity + 1:
            break
        hypotheses += 1
        try:
            replay = [execute_program(program, source) for source, _ in train]
            if any(_grid(prediction, bounds["max_grid_cells"]) != target for prediction, (_, target) in zip(replay, train)):
                continue
            predictions = [execute_program(program, source) for source in tests]
        except (KeyError, TypeError, ValueError, IndexError, ArithmeticError):
            continue
        behavior = _digest(predictions)
        if best_complexity is None:
            best_complexity = complexity
        mechanisms_by_behavior.setdefault(behavior, set()).add(family)
        record = {
            "family": family,
            "program": program,
            "train_outputs": replay,
            "test_outputs": predictions,
            "complexity": int(complexity),
            "evidence": {
                "all_demos_exact": True,
                "demonstrations": len(train),
                "changed_demonstrations": sum(source != target for source, target in train),
                "object_selection_fail_closed": True,
                "label_access": "training_outputs_only",
                "mechanism_support": 1,
                "hypotheses_tested_at_discovery": hypotheses,
            },
        }
        old = records_by_behavior.get(behavior)
        if old is None or _rank(record) < _rank(old):
            records_by_behavior[behavior] = record

    for behavior, record in records_by_behavior.items():
        record["evidence"]["mechanism_support"] = len(mechanisms_by_behavior[behavior])
        record["evidence"]["equivalent_families"] = sorted(mechanisms_by_behavior[behavior])
        record["evidence"]["behavior_hash"] = behavior
        exact.append(record)
    exact.sort(key=_rank)
    cap = min(bounds["max_candidates"], bounds["max_programs"])
    return exact[:cap]


__all__ = ["Component", "SCHEMA", "compile_task", "execute_program"]
