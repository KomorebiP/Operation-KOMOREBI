"""Bounded ARC object-graph and discrete-dynamics tournament entrant.

The entrant deliberately has no task-id or held-out-label interface.  It compiles a
small, explicit JSON grammar against *all* demonstrations, executes surviving
programs on the test inputs, and quotients programs by their complete behavior.
Every executor is total-with-failure: an invalid selection, collision, route, or
bound returns ``None`` and therefore cannot become a candidate.
"""

from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Iterable, Iterator, Mapping, Sequence


Grid = tuple[tuple[int, ...], ...]
Cell = tuple[int, int]

_D4: tuple[Cell, ...] = ((-1, 0), (0, -1), (0, 1), (1, 0))
_D8: tuple[Cell, ...] = (
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1), (0, 1),
    (1, -1), (1, 0), (1, 1),
)

_DEFAULT_LIMITS = {
    "max_candidates": 128,
    "max_programs": 120_000,
    "max_grid_cells": 2_500,
    "max_objects": 96,
    "max_growth_steps": 32,
    "max_path_states": 5_000,
    "max_relation_pairs": 64,
    "max_side": 30,
    "max_examples": 10,
}


class _Undefined(Exception):
    """Internal fail-closed signal; never escapes ``compile_task``."""


@dataclass(frozen=True)
class Obj:
    cells: tuple[tuple[int, int, int], ...]

    @property
    def area(self) -> int:
        return len(self.cells)

    @property
    def colors(self) -> tuple[int, ...]:
        return tuple(sorted({value for _, _, value in self.cells}))

    @property
    def min_r(self) -> int:
        return min(r for r, _, _ in self.cells)

    @property
    def max_r(self) -> int:
        return max(r for r, _, _ in self.cells)

    @property
    def min_c(self) -> int:
        return min(c for _, c, _ in self.cells)

    @property
    def max_c(self) -> int:
        return max(c for _, c, _ in self.cells)

    @property
    def height(self) -> int:
        return self.max_r - self.min_r + 1

    @property
    def width(self) -> int:
        return self.max_c - self.min_c + 1

    @property
    def center2(self) -> Cell:
        """Twice the bounding-box center, avoiding floating-point comparisons."""

        return (self.min_r + self.max_r, self.min_c + self.max_c)

    @property
    def positions(self) -> frozenset[Cell]:
        return frozenset((r, c) for r, c, _ in self.cells)

    def key(self) -> tuple[Any, ...]:
        return (self.min_r, self.min_c, self.max_r, self.max_c, self.colors, self.cells)


def _jsonable(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    return value


def _canonical(value: Any) -> str:
    return json.dumps(_jsonable(value), sort_keys=True, separators=(",", ":"))


def _digest(value: Any) -> str:
    return sha256(_canonical(value).encode("utf-8")).hexdigest()


def _grid(value: Any, max_cells: int, max_side: int = 30) -> Grid:
    if not isinstance(value, (list, tuple)) or not value:
        raise _Undefined("grid must be a non-empty row sequence")
    rows: list[tuple[int, ...]] = []
    width: int | None = None
    for raw_row in value:
        if not isinstance(raw_row, (list, tuple)) or not raw_row:
            raise _Undefined("grid rows must be non-empty sequences")
        row: list[int] = []
        for cell in raw_row:
            if isinstance(cell, bool) or not isinstance(cell, int) or not 0 <= cell <= 9:
                raise _Undefined("ARC colors must be integers in [0, 9]")
            row.append(cell)
        if width is None:
            width = len(row)
        elif len(row) != width:
            raise _Undefined("ragged grid")
        rows.append(tuple(row))
    if len(rows) > max_side or int(width or 0) > max_side:
        raise _Undefined("grid side limit")
    if len(rows) * int(width or 0) > max_cells:
        raise _Undefined("grid cell limit")
    return tuple(rows)


def _limits(raw: Any) -> dict[str, int]:
    if raw is None:
        return dict(_DEFAULT_LIMITS)
    if not isinstance(raw, Mapping):
        raise _Undefined("limits must be a mapping or None")
    result = dict(_DEFAULT_LIMITS)
    for key in result:
        if key not in raw:
            continue
        value = raw[key]
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise _Undefined(f"invalid limit: {key}")
        result[key] = value
    return result


def _sanitize(task: Any, limits: Mapping[str, int]) -> dict[str, tuple[dict[str, Grid], ...]]:
    """Copy only authorized ARC fields; metadata and test labels are unreachable."""

    if not isinstance(task, Mapping):
        raise _Undefined("task must be a mapping")
    raw_train = task.get("train")
    raw_test = task.get("test")
    if not isinstance(raw_train, (list, tuple)) or not raw_train:
        raise _Undefined("at least one training demonstration is required")
    if not isinstance(raw_test, (list, tuple)):
        raise _Undefined("test split must be a sequence")
    if not raw_test or len(raw_train) > limits["max_examples"] or len(raw_test) > limits["max_examples"]:
        raise _Undefined("example-count limit")
    train: list[dict[str, Grid]] = []
    for example in raw_train:
        if not isinstance(example, Mapping) or "input" not in example or "output" not in example:
            raise _Undefined("malformed training demonstration")
        train.append({
            "input": _grid(example["input"], limits["max_grid_cells"], limits["max_side"]),
            "output": _grid(example["output"], limits["max_grid_cells"], limits["max_side"]),
        })
    tests: list[dict[str, Grid]] = []
    for example in raw_test:
        if not isinstance(example, Mapping) or "input" not in example:
            raise _Undefined("malformed test example")
        # In particular, deliberately do not copy a supplied ``output`` key.
        tests.append({"input": _grid(example["input"], limits["max_grid_cells"], limits["max_side"])})
    return {"train": tuple(train), "test": tuple(tests)}


def _shape(grid: Grid) -> tuple[int, int]:
    return len(grid), len(grid[0])


@lru_cache(maxsize=256)
def _modal_background(grid: Grid) -> int:
    counts = Counter(cell for row in grid for cell in row)
    return min(counts, key=lambda color: (-counts[color], color))


def _background(grid: Grid, spec: Any) -> int:
    if spec == "modal":
        return _modal_background(grid)
    if isinstance(spec, int) and 0 <= spec <= 9:
        return spec
    raise _Undefined("invalid background")


@lru_cache(maxsize=512)
def _components_cached(
    grid: Grid,
    background: int,
    connectivity: int,
    object_mode: str,
) -> tuple[Obj, ...]:
    if connectivity not in (4, 8) or object_mode not in ("mono", "multicolor"):
        raise _Undefined("invalid object grammar")
    height, width = _shape(grid)
    steps = _D4 if connectivity == 4 else _D8
    seen: set[Cell] = set()
    result: list[Obj] = []
    for row in range(height):
        for col in range(width):
            color = grid[row][col]
            if color == background or (row, col) in seen:
                continue
            seen.add((row, col))
            queue = deque([(row, col)])
            cells: list[tuple[int, int, int]] = []
            while queue:
                r, c = queue.popleft()
                value = grid[r][c]
                cells.append((r, c, value))
                for dr, dc in steps:
                    nr, nc = r + dr, c + dc
                    if not (0 <= nr < height and 0 <= nc < width) or (nr, nc) in seen:
                        continue
                    neighbor = grid[nr][nc]
                    if neighbor == background:
                        continue
                    if object_mode == "mono" and neighbor != color:
                        continue
                    seen.add((nr, nc))
                    queue.append((nr, nc))
            result.append(Obj(tuple(sorted(cells))))
    return tuple(sorted(result, key=Obj.key))


def _components(
    grid: Grid,
    background: int,
    connectivity: int,
    object_mode: str,
    max_objects: int,
) -> tuple[Obj, ...]:
    result = _components_cached(grid, background, connectivity, object_mode)
    if len(result) > max_objects:
        raise _Undefined("object limit")
    return result


@lru_cache(maxsize=65_536)
def _cell_distance(a: Obj, b: Obj, metric: str = "manhattan") -> int:
    if metric == "manhattan":
        return min(abs(ar - br) + abs(ac - bc) for ar, ac, _ in a.cells for br, bc, _ in b.cells)
    if metric == "chebyshev":
        return min(max(abs(ar - br), abs(ac - bc)) for ar, ac, _ in a.cells for br, bc, _ in b.cells)
    raise _Undefined("unknown distance metric")


def _contains(a: Obj, b: Obj) -> bool:
    return (
        a.min_r <= b.min_r <= b.max_r <= a.max_r
        and a.min_c <= b.min_c <= b.max_c <= a.max_c
        and (a.min_r, a.min_c, a.max_r, a.max_c)
        != (b.min_r, b.min_c, b.max_r, b.max_c)
    )


def _relation(a: Obj, b: Obj, name: str, connectivity: int) -> bool:
    if name == "row_aligned":
        return not (a.max_r < b.min_r or b.max_r < a.min_r)
    if name == "col_aligned":
        return not (a.max_c < b.min_c or b.max_c < a.min_c)
    if name == "aligned":
        return _relation(a, b, "row_aligned", connectivity) or _relation(a, b, "col_aligned", connectivity)
    if name == "touching":
        metric = "manhattan" if connectivity == 4 else "chebyshev"
        return _cell_distance(a, b, metric) == 1
    if name == "containment":
        return _contains(a, b) or _contains(b, a)
    raise _Undefined("unknown relation")


def _select(objects: Sequence[Obj], selector: Mapping[str, Any]) -> tuple[Obj, ...]:
    kind = selector.get("kind")
    if kind == "all":
        chosen = list(objects)
    elif kind == "color":
        color = selector.get("color")
        chosen = [obj for obj in objects if color in obj.colors]
    elif kind == "largest":
        size = max((obj.area for obj in objects), default=-1)
        chosen = [obj for obj in objects if obj.area == size]
    elif kind == "smallest":
        size = min((obj.area for obj in objects), default=-1)
        chosen = [obj for obj in objects if obj.area == size]
    elif kind == "unique_largest":
        ranked = sorted(objects, key=lambda obj: (-obj.area, obj.key()))
        chosen = ranked[:1] if len(ranked) == 1 or ranked[0].area > ranked[1].area else []
    elif kind == "unique_smallest":
        ranked = sorted(objects, key=lambda obj: (obj.area, obj.key()))
        chosen = ranked[:1] if len(ranked) == 1 or ranked[0].area < ranked[1].area else []
    elif kind == "singletons":
        chosen = [obj for obj in objects if obj.area == 1]
    elif kind == "non_largest":
        size = max((obj.area for obj in objects), default=-1)
        chosen = [obj for obj in objects if obj.area != size]
    elif kind == "non_smallest":
        size = min((obj.area for obj in objects), default=-1)
        chosen = [obj for obj in objects if obj.area != size]
    else:
        raise _Undefined("unknown selector")
    if not chosen:
        raise _Undefined("empty selection")
    return tuple(sorted(chosen, key=Obj.key))


@lru_cache(maxsize=8_192)
def _pairs(objects: tuple[Obj, ...], pairing: str, connectivity: int) -> tuple[tuple[Obj, Obj], ...]:
    pairs = [(objects[i], objects[j]) for i in range(len(objects)) for j in range(i + 1, len(objects))]
    if not pairs:
        raise _Undefined("pair operation requires at least two objects")
    if pairing == "all":
        chosen = pairs
    elif pairing in ("nearest", "farthest"):
        distances = [_cell_distance(a, b) for a, b in pairs]
        target = min(distances) if pairing == "nearest" else max(distances)
        chosen = [pair for pair, distance in zip(pairs, distances) if distance == target]
    elif pairing == "nearest_each":
        keys: set[tuple[tuple[Any, ...], tuple[Any, ...]]] = set()
        by_key = {obj.key(): obj for obj in objects}
        for obj in objects:
            others = [other for other in objects if other != obj]
            target = min(_cell_distance(obj, other) for other in others)
            for other in others:
                if _cell_distance(obj, other) != target:
                    continue
                first, second = sorted((obj.key(), other.key()))
                keys.add((first, second))
        chosen = [(by_key[first], by_key[second]) for first, second in sorted(keys)]
    elif pairing in ("aligned", "row_aligned", "col_aligned", "touching", "containment"):
        chosen = [pair for pair in pairs if _relation(pair[0], pair[1], pairing, connectivity)]
    else:
        raise _Undefined("unknown pairing")
    if not chosen:
        raise _Undefined("relation selected no pairs")
    return tuple(chosen)


def _paint_value(spec: Any, first: Obj | None = None, second: Obj | None = None) -> int:
    if isinstance(spec, int) and 0 <= spec <= 9:
        return spec
    if spec == "first" and first is not None and len(first.colors) == 1:
        return first.colors[0]
    if spec == "second" and second is not None and len(second.colors) == 1:
        return second.colors[0]
    if spec == "min_object" and first is not None:
        return min(first.colors)
    if spec == "max_object" and first is not None:
        return max(first.colors)
    raise _Undefined("paint color is undefined")


def _mutable(grid: Grid) -> list[list[int]]:
    return [list(row) for row in grid]


def _freeze(grid: Sequence[Sequence[int]]) -> Grid:
    return tuple(tuple(row) for row in grid)


def _shortest_path(
    grid: Grid,
    background: int,
    first: Obj,
    second: Obj,
    connectivity: int,
    max_states: int,
) -> tuple[Cell, ...]:
    """Canonical shortest path whose interior consists only of background cells."""

    height, width = _shape(grid)
    starts = sorted(first.positions)
    goals = second.positions
    allowed_endpoints = first.positions | second.positions
    steps = _D4 if connectivity == 4 else _D8
    queue: deque[Cell] = deque(starts)
    predecessor: dict[Cell, Cell | None] = {cell: None for cell in starts}
    found: Cell | None = None
    states = 0
    while queue:
        cell = queue.popleft()
        states += 1
        if states > max_states:
            raise _Undefined("path-state limit")
        if cell in goals:
            found = cell
            break
        r, c = cell
        for dr, dc in steps:
            nxt = (r + dr, c + dc)
            nr, nc = nxt
            if not (0 <= nr < height and 0 <= nc < width) or nxt in predecessor:
                continue
            if nxt not in allowed_endpoints and grid[nr][nc] != background:
                continue
            predecessor[nxt] = cell
            queue.append(nxt)
    if found is None:
        raise _Undefined("no background path")
    reverse: list[Cell] = []
    cursor: Cell | None = found
    while cursor is not None:
        reverse.append(cursor)
        cursor = predecessor[cursor]
    return tuple(reversed(reverse))


def _straight_path(first: Obj, second: Obj) -> tuple[Cell, ...]:
    candidates: list[tuple[int, tuple[Cell, ...]]] = []
    for ar, ac, _ in first.cells:
        for br, bc, _ in second.cells:
            if ar == br:
                lo, hi = sorted((ac, bc))
                path = tuple((ar, c) for c in range(lo, hi + 1))
                candidates.append((len(path), path if ac <= bc else tuple(reversed(path))))
            if ac == bc:
                lo, hi = sorted((ar, br))
                path = tuple((r, ac) for r in range(lo, hi + 1))
                candidates.append((len(path), path if ar <= br else tuple(reversed(path))))
    if not candidates:
        raise _Undefined("objects are not straight-line aligned")
    return min(candidates, key=lambda item: (item[0], item[1]))[1]


def _object_context(
    grid: Grid, program: Mapping[str, Any], limits: Mapping[str, int]
) -> tuple[int, tuple[Obj, ...]]:
    background = _background(grid, program.get("background", "modal"))
    objects = _components(
        grid,
        background,
        int(program.get("connectivity", 4)),
        str(program.get("object_mode", "mono")),
        limits["max_objects"],
    )
    if not objects:
        raise _Undefined("no foreground objects")
    return background, objects


def _execute_connect(grid: Grid, program: Mapping[str, Any], limits: Mapping[str, int]) -> Grid:
    background, objects = _object_context(grid, program, limits)
    selected = _select(objects, program["selector"])
    pairs = _pairs(selected, str(program["pairing"]), int(program["connectivity"]))
    if len(pairs) > limits["max_relation_pairs"]:
        raise _Undefined("relation-pair limit")
    canvas = _mutable(grid)
    route = program["route"]
    for first, second in pairs:
        if route == "straight":
            path = _straight_path(first, second)
            for r, c in path[1:-1]:
                if grid[r][c] != background:
                    raise _Undefined("straight route crosses an obstacle")
        elif route in ("shortest4", "shortest8"):
            path = _shortest_path(
                grid,
                background,
                first,
                second,
                4 if route == "shortest4" else 8,
                limits["max_path_states"],
            )
        else:
            raise _Undefined("unknown connection route")
        color = _paint_value(program["paint"], first, second)
        for r, c in path[1:-1]:
            if canvas[r][c] == background:
                canvas[r][c] = color
            elif canvas[r][c] != color:
                raise _Undefined("connections conflict")
    return _freeze(canvas)


def _direction_set(spec: str) -> tuple[Cell, ...]:
    names = {
        "n": ((-1, 0),), "s": ((1, 0),), "w": ((0, -1),), "e": ((0, 1),),
        "nw": ((-1, -1),), "ne": ((-1, 1),), "sw": ((1, -1),), "se": ((1, 1),),
        "cardinal": _D4, "diagonal": ((-1, -1), (-1, 1), (1, -1), (1, 1)),
        "eight": _D8,
    }
    if spec not in names:
        raise _Undefined("unknown ray direction")
    return names[spec]


def _ray_frontier(obj: Obj, direction: Cell) -> tuple[tuple[int, int, int], ...]:
    dr, dc = direction
    positions = obj.positions
    return tuple(
        cell for cell in obj.cells
        if (cell[0] + dr, cell[1] + dc) not in positions
    )


def _execute_ray(grid: Grid, program: Mapping[str, Any], limits: Mapping[str, int]) -> Grid:
    background, objects = _object_context(grid, program, limits)
    selected = _select(objects, program["selector"])
    directions = _direction_set(str(program["directions"]))
    height, width = _shape(grid)
    proposals: dict[Cell, set[int]] = {}
    require_obstacle = program.get("stop") == "obstacle"
    for obj in selected:
        for direction in directions:
            dr, dc = direction
            for r, c, source_color in _ray_frontier(obj, direction):
                nr, nc = r + dr, c + dc
                ray: list[Cell] = []
                hit_obstacle = False
                while 0 <= nr < height and 0 <= nc < width:
                    if grid[nr][nc] != background:
                        hit_obstacle = True
                        break
                    ray.append((nr, nc))
                    nr += dr
                    nc += dc
                if require_obstacle and not hit_obstacle:
                    continue
                paint = source_color if program["paint"] == "source" else _paint_value(program["paint"], obj)
                for cell in ray:
                    proposals.setdefault(cell, set()).add(paint)
    if not proposals:
        raise _Undefined("ray paints no cells")
    canvas = _mutable(grid)
    conflict = str(program.get("conflict", "fail"))
    for (r, c), colors in sorted(proposals.items()):
        if len(colors) == 1:
            canvas[r][c] = next(iter(colors))
        elif conflict == "min":
            canvas[r][c] = min(colors)
        elif conflict == "leave":
            continue
        else:
            raise _Undefined("ray color conflict")
    return _freeze(canvas)


def _translate_object(obj: Obj, dr: int, dc: int) -> tuple[tuple[int, int, int], ...]:
    return tuple((r + dr, c + dc, color) for r, c, color in obj.cells)


def _nearest_anchor(obj: Obj, objects: Sequence[Obj]) -> Obj:
    others = [other for other in objects if other != obj]
    if not others:
        raise _Undefined("relative motion needs an anchor")
    distance = min(_cell_distance(obj, other) for other in others)
    tied = [other for other in others if _cell_distance(obj, other) == distance]
    if len(tied) != 1:
        raise _Undefined("nearest anchor is ambiguous")
    return tied[0]


def _touch_vector(obj: Obj, anchor: Obj) -> Cell:
    """Move toward a uniquely axis-aligned anchor until cardinally touching."""

    row_overlap = not (obj.max_r < anchor.min_r or anchor.max_r < obj.min_r)
    col_overlap = not (obj.max_c < anchor.min_c or anchor.max_c < obj.min_c)
    candidates: list[Cell] = []
    if row_overlap and obj.max_c < anchor.min_c:
        candidates.append((0, anchor.min_c - obj.max_c - 1))
    if row_overlap and anchor.max_c < obj.min_c:
        candidates.append((0, anchor.max_c - obj.min_c + 1))
    if col_overlap and obj.max_r < anchor.min_r:
        candidates.append((anchor.min_r - obj.max_r - 1, 0))
    if col_overlap and anchor.max_r < obj.min_r:
        candidates.append((anchor.max_r - obj.min_r + 1, 0))
    candidates = [vector for vector in candidates if vector != (0, 0)]
    if len(candidates) != 1:
        raise _Undefined("touch vector is absent or ambiguous")
    return candidates[0]


def _alignment_vector(obj: Obj, anchor: Obj, relation: str) -> Cell:
    if relation == "align_top":
        return anchor.min_r - obj.min_r, 0
    if relation == "align_bottom":
        return anchor.max_r - obj.max_r, 0
    if relation == "align_left":
        return 0, anchor.min_c - obj.min_c
    if relation == "align_right":
        return 0, anchor.max_c - obj.max_c
    if relation == "align_center_row":
        delta = anchor.center2[0] - obj.center2[0]
        if delta % 2:
            raise _Undefined("half-cell row alignment")
        return delta // 2, 0
    if relation == "align_center_col":
        delta = anchor.center2[1] - obj.center2[1]
        if delta % 2:
            raise _Undefined("half-cell column alignment")
        return 0, delta // 2
    raise _Undefined("unknown transported relation")


def _motion_vectors(
    selected: Sequence[Obj], objects: Sequence[Obj], vector: Mapping[str, Any]
) -> tuple[tuple[Obj, int, int], ...]:
    kind = vector.get("kind")
    result: list[tuple[Obj, int, int]] = []
    for obj in selected:
        if kind == "fixed":
            dr, dc = vector.get("dr"), vector.get("dc")
            if isinstance(dr, bool) or isinstance(dc, bool) or not isinstance(dr, int) or not isinstance(dc, int):
                raise _Undefined("invalid fixed vector")
        else:
            anchor = _nearest_anchor(obj, objects)
            if kind == "toward_nearest_touch":
                dr, dc = _touch_vector(obj, anchor)
            elif kind == "transport_relation":
                dr, dc = _alignment_vector(obj, anchor, str(vector.get("relation")))
            else:
                raise _Undefined("unknown motion vector")
        if (dr, dc) == (0, 0):
            raise _Undefined("zero motion")
        result.append((obj, dr, dc))
    return tuple(result)


def _execute_motion(grid: Grid, program: Mapping[str, Any], limits: Mapping[str, int]) -> Grid:
    background, objects = _object_context(grid, program, limits)
    selected = _select(objects, program["selector"])
    motions = _motion_vectors(selected, objects, program["vector"])
    height, width = _shape(grid)
    moving_positions = frozenset(cell for obj in selected for cell in obj.positions)
    destinations: dict[Cell, int] = {}
    for obj, dr, dc in motions:
        for nr, nc, color in _translate_object(obj, dr, dc):
            if not (0 <= nr < height and 0 <= nc < width):
                raise _Undefined("motion leaves canvas")
            if (nr, nc) not in moving_positions and grid[nr][nc] != background:
                raise _Undefined("motion collides with stationary object")
            prior = destinations.get((nr, nc))
            if prior is not None and prior != color:
                raise _Undefined("moving objects collide")
            destinations[(nr, nc)] = color
    canvas = _mutable(grid)
    if program["op"] == "translate":
        for r, c in moving_positions:
            canvas[r][c] = background
    elif program["op"] != "copy":
        raise _Undefined("invalid motion operation")
    for (r, c), color in sorted(destinations.items()):
        canvas[r][c] = color
    return _freeze(canvas)


def _reflection_destination(obj: Obj, axis: str, height: int, width: int) -> tuple[tuple[int, int, int], ...]:
    result: list[tuple[int, int, int]] = []
    for r, c, color in obj.cells:
        if axis == "canvas_horizontal":
            nr, nc = height - 1 - r, c
        elif axis == "canvas_vertical":
            nr, nc = r, width - 1 - c
        elif axis == "canvas_main_diagonal":
            nr, nc = c, r
        elif axis == "canvas_anti_diagonal":
            nr, nc = width - 1 - c, height - 1 - r
        elif axis == "bbox_horizontal":
            nr, nc = obj.min_r + obj.max_r - r, c
        elif axis == "bbox_vertical":
            nr, nc = r, obj.min_c + obj.max_c - c
        else:
            raise _Undefined("unknown reflection axis")
        result.append((nr, nc, color))
    return tuple(result)


def _execute_reflect(grid: Grid, program: Mapping[str, Any], limits: Mapping[str, int]) -> Grid:
    background, objects = _object_context(grid, program, limits)
    selected = _select(objects, program["selector"])
    axis = str(program["axis"])
    height, width = _shape(grid)
    if axis in ("canvas_main_diagonal", "canvas_anti_diagonal") and height != width:
        raise _Undefined("diagonal canvas reflection requires a square")
    moving = frozenset(cell for obj in selected for cell in obj.positions)
    destinations: dict[Cell, int] = {}
    for obj in selected:
        for nr, nc, color in _reflection_destination(obj, axis, height, width):
            if not (0 <= nr < height and 0 <= nc < width):
                raise _Undefined("reflection leaves canvas")
            if (nr, nc) not in moving and grid[nr][nc] != background:
                raise _Undefined("reflection collides")
            if (nr, nc) in destinations and destinations[(nr, nc)] != color:
                raise _Undefined("reflection color collision")
            destinations[(nr, nc)] = color
    canvas = _mutable(grid)
    if not bool(program.get("copy", False)):
        for r, c in moving:
            canvas[r][c] = background
    for (r, c), color in sorted(destinations.items()):
        canvas[r][c] = color
    return _freeze(canvas)


def _execute_growth(grid: Grid, program: Mapping[str, Any], limits: Mapping[str, int]) -> Grid:
    background, objects = _object_context(grid, program, limits)
    selected = _select(objects, program["selector"])
    selected_positions = frozenset(cell for obj in selected for cell in obj.positions)
    current: dict[Cell, int] = {
        (r, c): color for obj in selected for r, c, color in obj.cells
    }
    height, width = _shape(grid)
    steps_spec = program["steps"]
    if steps_spec == "stable":
        maximum = limits["max_growth_steps"]
        require_stable = True
    elif isinstance(steps_spec, int) and not isinstance(steps_spec, bool) and 1 <= steps_spec <= limits["max_growth_steps"]:
        maximum = steps_spec
        require_stable = False
    else:
        raise _Undefined("invalid growth bound")
    neighbors = _D4 if int(program["connectivity"]) == 4 else _D8
    canvas = _mutable(grid)
    changed_any = False
    stable = False
    for _ in range(maximum):
        proposals: dict[Cell, set[int]] = {}
        for (r, c), source_color in sorted(current.items()):
            for dr, dc in neighbors:
                nr, nc = r + dr, c + dc
                if not (0 <= nr < height and 0 <= nc < width):
                    continue
                if (nr, nc) in current:
                    continue
                # All original non-selected foreground is an immutable obstacle.
                if (nr, nc) not in selected_positions and grid[nr][nc] != background:
                    continue
                if canvas[nr][nc] != background:
                    continue
                paint = source_color if program["paint"] == "source" else _paint_value(program["paint"])
                proposals.setdefault((nr, nc), set()).add(paint)
        accepted: dict[Cell, int] = {}
        conflict = str(program["conflict"])
        for cell, colors in sorted(proposals.items()):
            if len(colors) == 1:
                accepted[cell] = next(iter(colors))
            elif conflict == "min":
                accepted[cell] = min(colors)
            elif conflict == "leave":
                continue
            else:
                raise _Undefined("growth conflict")
        if not accepted:
            stable = True
            break
        changed_any = True
        for (r, c), color in accepted.items():
            canvas[r][c] = color
        current.update(accepted)
    if require_stable and not stable:
        raise _Undefined("growth did not stabilize inside bound")
    if not changed_any:
        raise _Undefined("growth makes no change")
    return _freeze(canvas)


def _execute(grid: Grid, program: Mapping[str, Any], limits: Mapping[str, int]) -> Grid | None:
    try:
        op = program.get("op")
        if op in ("connect", "shortest_path"):
            return _execute_connect(grid, program, limits)
        if op in ("ray", "project"):
            return _execute_ray(grid, program, limits)
        if op in ("translate", "copy"):
            return _execute_motion(grid, program, limits)
        if op == "reflect":
            return _execute_reflect(grid, program, limits)
        if op == "grow":
            return _execute_growth(grid, program, limits)
        raise _Undefined("unknown operation")
    except (_Undefined, KeyError, TypeError, ValueError, IndexError):
        return None


def _selector_specs(task: Mapping[str, Sequence[Mapping[str, Grid]]]) -> tuple[dict[str, Any], ...]:
    dynamic = [
        {"kind": "all"},
        {"kind": "largest"},
        {"kind": "smallest"},
        {"kind": "unique_largest"},
        {"kind": "unique_smallest"},
        {"kind": "singletons"},
        {"kind": "non_largest"},
        {"kind": "non_smallest"},
    ]
    palettes = [set(cell for row in example["input"] for cell in row) for example in task["train"]]
    common = set.intersection(*palettes) if palettes else set()
    backgrounds = {_background(example["input"], "modal") for example in task["train"]}
    colors = sorted(common - backgrounds)[:5]
    return tuple(dynamic + [{"kind": "color", "color": color} for color in colors])


def _paint_colors(task: Mapping[str, Sequence[Mapping[str, Grid]]]) -> tuple[int, ...]:
    changed: Counter[int] = Counter()
    foreground: Counter[int] = Counter()
    for example in task["train"]:
        source, target = example["input"], example["output"]
        if _shape(source) != _shape(target):
            continue
        bg = _background(source, "modal")
        for r, row in enumerate(target):
            for c, color in enumerate(row):
                if color != source[r][c] and color != bg:
                    changed[color] += 1
                if color != bg:
                    foreground[color] += 1
    ordered = sorted(changed, key=lambda color: (-changed[color], color))
    ordered.extend(
        color for color in sorted(foreground, key=lambda value: (-foreground[value], value))
        if color not in ordered
    )
    return tuple(ordered[:4])


def _normalized_signature(obj: Obj) -> tuple[Any, ...]:
    return tuple(sorted((r - obj.min_r, c - obj.min_c, color) for r, c, color in obj.cells))


def _delta_hints(
    task: Mapping[str, Sequence[Mapping[str, Grid]]], limits: Mapping[str, int]
) -> tuple[Cell, ...]:
    values: set[Cell] = set()
    # Small local motions remain available even when output components merge.
    for distance in range(1, 4):
        for dr in range(-distance, distance + 1):
            dc_abs = distance - abs(dr)
            if dc_abs == 0:
                values.add((dr, 0))
            else:
                values.add((dr, -dc_abs))
                values.add((dr, dc_abs))
    for example in task["train"]:
        source, target = example["input"], example["output"]
        if _shape(source) != _shape(target):
            continue
        for connectivity in (4, 8):
            source_bg = _background(source, "modal")
            target_bg = _background(target, "modal")
            try:
                source_objects = _components(source, source_bg, connectivity, "mono", limits["max_objects"])
                target_objects = _components(target, target_bg, connectivity, "mono", limits["max_objects"])
            except _Undefined:
                continue
            target_by_signature: dict[tuple[Any, ...], list[Obj]] = {}
            for obj in target_objects:
                target_by_signature.setdefault(_normalized_signature(obj), []).append(obj)
            for obj in source_objects:
                for other in target_by_signature.get(_normalized_signature(obj), []):
                    vector = (other.min_r - obj.min_r, other.min_c - obj.min_c)
                    if vector != (0, 0):
                        values.add(vector)
        # Residual bounding-box displacement catches a copy joined to its source.
        removed_by_color: dict[int, list[Cell]] = {}
        added_by_color: dict[int, list[Cell]] = {}
        for r, row in enumerate(source):
            for c, value in enumerate(row):
                if target[r][c] == value:
                    continue
                removed_by_color.setdefault(value, []).append((r, c))
                added_by_color.setdefault(target[r][c], []).append((r, c))
        for color in sorted(set(removed_by_color) & set(added_by_color)):
            old, new = removed_by_color[color], added_by_color[color]
            if len(old) != len(new) or not old:
                continue
            values.add((min(r for r, _ in new) - min(r for r, _ in old),
                        min(c for _, c in new) - min(c for _, c in old)))
    values.discard((0, 0))
    # Structural hints precede very long jumps, but all retained entries are stable.
    return tuple(sorted(values, key=lambda item: (abs(item[0]) + abs(item[1]), item[0], item[1]))[:64])


def _search_axes(
    task: Mapping[str, Sequence[Mapping[str, Grid]]], limits: Mapping[str, int]
) -> tuple[tuple[dict[str, Any], tuple[dict[str, Any], ...]], ...]:
    """Quotient object grammars and selectors by behavior on visible inputs."""

    inputs = tuple(example["input"] for example in task["train"]) + tuple(
        example["input"] for example in task["test"]
    )
    raw_configs = tuple(
        {"background": "modal", "connectivity": connectivity, "object_mode": mode}
        for connectivity in (4, 8)
        for mode in ("mono", "multicolor")
    )
    configurations: dict[str, tuple[dict[str, Any], tuple[tuple[Obj, ...], ...]]] = {}
    for config in raw_configs:
        try:
            scenes = tuple(
                _components(
                    grid, _background(grid, config["background"]), config["connectivity"],
                    config["object_mode"], limits["max_objects"],
                )
                for grid in inputs
            )
        except _Undefined:
            continue
        signature = _canonical(tuple(tuple(obj.cells for obj in scene) for scene in scenes))
        incumbent = configurations.get(signature)
        rank = (int(config["connectivity"] == 8) + int(config["object_mode"] == "multicolor"), _canonical(config))
        if incumbent is None:
            configurations[signature] = (config, scenes)
        else:
            old = incumbent[0]
            old_rank = (int(old["connectivity"] == 8) + int(old["object_mode"] == "multicolor"), _canonical(old))
            if rank < old_rank:
                configurations[signature] = (config, scenes)

    result: list[tuple[dict[str, Any], tuple[dict[str, Any], ...]]] = []
    for config, scenes in sorted(configurations.values(), key=lambda item: _canonical(item[0])):
        selectors: dict[str, dict[str, Any]] = {}
        for selector in _selector_specs(task):
            try:
                selections = tuple(_select(scene, selector) for scene in scenes)
            except _Undefined:
                continue
            signature = _canonical(tuple(tuple(obj.cells for obj in selection) for selection in selections))
            incumbent = selectors.get(signature)
            if incumbent is None or (_selector_cost(selector), _canonical(selector)) < (
                _selector_cost(incumbent), _canonical(incumbent)
            ):
                selectors[signature] = selector
        ordered = tuple(sorted(selectors.values(), key=lambda item: (_selector_cost(item), _canonical(item))))
        if ordered:
            result.append((config, ordered))
    return tuple(result)


def _base_programs(
    task: Mapping[str, Sequence[Mapping[str, Grid]]], limits: Mapping[str, int]
) -> Iterator[dict[str, Any]]:
    if any(_shape(example["input"]) != _shape(example["output"]) for example in task["train"]):
        return
    constants = _paint_colors(task)
    axes = _search_axes(task, limits)
    if not axes:
        return
    additive = all(
        all(
            source[r][c] == background or source[r][c] == target[r][c]
            for r in range(len(source)) for c in range(len(source[0]))
        )
        for example in task["train"]
        for source, target, background in ((example["input"], example["output"], _background(example["input"], "modal")),)
    )
    color_conserving = all(
        Counter(cell for row in example["input"] for cell in row)
        == Counter(cell for row in example["output"] for cell in row)
        for example in task["train"]
    )

    # Object-graph edges: direct aligned joins and obstacle-aware shortest paths.
    if additive:
        for config, selectors in axes:
            for selector in selectors:
                for pairing in (
                    "nearest", "nearest_each", "farthest", "aligned", "row_aligned",
                    "col_aligned", "touching", "containment", "all",
                ):
                    for route in ("straight", "shortest4", "shortest8"):
                        paints: tuple[Any, ...] = constants + ("first", "second")
                        for paint in paints:
                            yield {
                                "version": 1,
                                "op": "connect" if route == "straight" else "shortest_path",
                                **config,
                                "selector": selector,
                                "pairing": pairing,
                                "route": route,
                                "paint": paint,
                            }

    # Directional projections.  "obstacle" requires a terminal object, while
    # "boundary" grows to whichever obstacle/boundary is encountered first.
    if additive:
        for config, selectors in axes:
            for selector in selectors:
                for directions in ("n", "s", "w", "e", "nw", "ne", "sw", "se", "cardinal", "diagonal", "eight"):
                    for stop in ("boundary", "obstacle"):
                        for paint in ("source",) + constants:
                            conflicts = (
                                ("fail", "leave", "min")
                                if paint == "source" and directions in ("cardinal", "diagonal", "eight")
                                else ("fail",)
                            )
                            for conflict in conflicts:
                                yield {
                                    "version": 1,
                                    "op": "project" if stop == "boundary" else "ray",
                                    **config,
                                    "selector": selector,
                                    "directions": directions,
                                    "stop": stop,
                                    "paint": paint,
                                    "conflict": conflict,
                                }

    # Fixed translation/duplication plus relation-derived motion.
    vector_specs: list[dict[str, Any]] = [
        {"kind": "fixed", "dr": dr, "dc": dc}
        for dr, dc in _delta_hints(task, limits)
    ]
    vector_specs.append({"kind": "toward_nearest_touch"})
    vector_specs.extend(
        {"kind": "transport_relation", "relation": relation}
        for relation in (
            "align_top", "align_bottom", "align_left", "align_right",
            "align_center_row", "align_center_col",
        )
    )
    for config, selectors in axes:
        for selector in selectors:
            for vector in vector_specs:
                operations = tuple(
                    op for op, possible in (("translate", color_conserving), ("copy", additive))
                    if possible
                )
                for op in operations:
                    yield {
                        "version": 1,
                        "op": op,
                        **config,
                        "selector": selector,
                        "vector": vector,
                    }

    # Reflections can replace the source or preserve it as a reflected copy.
    for config, selectors in axes:
        for selector in selectors:
            for axis in (
                "canvas_horizontal", "canvas_vertical", "canvas_main_diagonal",
                "canvas_anti_diagonal", "bbox_horizontal", "bbox_vertical",
            ):
                for copy in tuple(
                    value for value in (False, True)
                    if (value and additive) or (not value and color_conserving)
                ):
                    yield {
                        "version": 1,
                        "op": "reflect",
                        **config,
                        "selector": selector,
                        "axis": axis,
                        "copy": copy,
                    }

    # Synchronous cellular growth is explicitly step-bounded.  Stable growth is
    # admitted only if stabilization is witnessed within the configured limit.
    maximum_dimension = max(
        max(_shape(example["input"])) for example in task["train"]
    )
    numeric_steps = range(1, min(maximum_dimension, limits["max_growth_steps"]) + 1)
    if additive:
        for config, selectors in axes:
            for selector in selectors:
                for steps in tuple(numeric_steps) + ("stable",):
                    for paint in ("source",) + constants:
                        conflicts = ("fail", "leave", "min") if paint == "source" else ("fail",)
                        for conflict in conflicts:
                            yield {
                                "version": 1,
                                "op": "grow",
                                **config,
                                "selector": selector,
                                "steps": steps,
                                "paint": paint,
                                "conflict": conflict,
                            }


def _selector_cost(selector: Mapping[str, Any]) -> int:
    return {
        "all": 0, "color": 1, "largest": 1, "smallest": 1,
        "singletons": 1, "unique_largest": 2, "unique_smallest": 2,
        "non_largest": 2, "non_smallest": 2,
    }.get(str(selector.get("kind")), 4)


def _complexity(program: Mapping[str, Any]) -> int:
    op = str(program.get("op"))
    base = {
        "connect": 5, "shortest_path": 7, "project": 5, "ray": 6,
        "translate": 4, "copy": 5, "reflect": 4, "grow": 6,
    }.get(op, 20)
    cost = base + _selector_cost(program.get("selector", {}))
    cost += int(program.get("connectivity", 4) == 8)
    cost += int(program.get("object_mode") == "multicolor")
    paint = program.get("paint")
    if isinstance(paint, int):
        cost += 1
    if program.get("pairing") not in (None, "nearest", "aligned"):
        cost += 1
    if op in ("translate", "copy"):
        vector = program.get("vector", {})
        if vector.get("kind") == "fixed":
            cost += min(4, abs(int(vector["dr"])) + abs(int(vector["dc"])))
        else:
            cost += 3
    if op == "grow":
        steps = program.get("steps")
        cost += 3 if steps == "stable" else min(4, int(steps))
        cost += int(program.get("conflict") != "fail")
    if op == "reflect":
        cost += int(bool(program.get("copy")))
    return cost


def _programs(
    task: Mapping[str, Sequence[Mapping[str, Grid]]], limits: Mapping[str, int]
) -> tuple[dict[str, Any], ...]:
    unique: dict[str, dict[str, Any]] = {}
    for program in _base_programs(task, limits):
        key = _canonical(program)
        unique.setdefault(key, program)
        if len(unique) > limits["max_programs"]:
            raise _Undefined("program enumeration truncated")
    return tuple(sorted(unique.values(), key=lambda item: (_complexity(item), _canonical(item))))


def _relations_used(program: Mapping[str, Any]) -> list[str]:
    values: list[str] = []
    pairing = program.get("pairing")
    if pairing in (
        "nearest", "nearest_each", "aligned", "row_aligned", "col_aligned",
        "touching", "containment", "farthest",
    ):
        values.append(str(pairing))
    vector = program.get("vector")
    if isinstance(vector, Mapping):
        if vector.get("kind") == "toward_nearest_touch":
            values.extend(("nearest", "touching"))
        elif vector.get("kind") == "transport_relation":
            values.extend(("nearest", str(vector.get("relation"))))
    return sorted(set(values))


def _candidate(
    program: Mapping[str, Any],
    train_inputs: Sequence[Grid],
    train_outputs: Sequence[Grid],
    test_outputs: Sequence[Grid],
    limits: Mapping[str, int],
) -> dict[str, Any]:
    behavior_hash = _digest(test_outputs)
    changed = [
        sum(
            source[r][c] != target[r][c]
            for r in range(len(source))
            for c in range(len(source[0]))
        )
        for source, target in zip(train_inputs, train_outputs)
    ]
    object_counts: list[int] = []
    for grid in train_inputs:
        background = _background(grid, program.get("background", "modal"))
        objects = _components(
            grid, background, int(program.get("connectivity", 4)),
            str(program.get("object_mode", "mono")), limits["max_objects"],
        )
        object_counts.append(len(objects))
    return {
        "family": "graph_dynamics",
        "program": _jsonable(dict(program)),
        "train_outputs": _jsonable(tuple(train_outputs)),
        "test_outputs": _jsonable(tuple(test_outputs)),
        "complexity": _complexity(program),
        "evidence": {
            "exact_replay": True,
            "all_demos_exact": True,
            "all_demonstrations_exact": True,
            "label_access": "training_outputs_only",
            "train_examples": len(train_inputs),
            "test_examples": len(test_outputs),
            "changed_cells": changed,
            "object_counts": object_counts,
            "relations_used": _relations_used(program),
            "behavior_hash": behavior_hash,
        },
    }


def compile_task(task: Any, limits: Any = None) -> list[dict[str, Any]]:
    """Return deterministic, behavior-deduplicated exact graph programs.

    ``task`` is defensively reduced to training inputs/outputs and test inputs.
    Every emitted program exactly reproduces every training output.  Any invalid
    input, resource-bound truncation, undefined execution, or internal error fails
    closed with an empty list.
    """

    try:
        bounded = _limits(limits)
        safe = _sanitize(task, bounded)
        train_inputs = tuple(example["input"] for example in safe["train"])
        targets = tuple(example["output"] for example in safe["train"])
        test_inputs = tuple(example["input"] for example in safe["test"])
        exact_by_behavior: dict[str, dict[str, Any]] = {}
        for program in _programs(safe, bounded):
            replay: list[Grid] = []
            exact = True
            for source, target in zip(train_inputs, targets):
                predicted = _execute(source, program, bounded)
                if predicted is None or predicted != target:
                    exact = False
                    break
                replay.append(predicted)
            if not exact or len(replay) != len(targets):
                continue
            predictions: list[Grid] = []
            for source in test_inputs:
                predicted = _execute(source, program, bounded)
                if predicted is None:
                    exact = False
                    break
                predictions.append(predicted)
            if not exact:
                continue
            candidate = _candidate(program, train_inputs, tuple(replay), tuple(predictions), bounded)
            behavior_key = candidate["evidence"]["behavior_hash"]
            incumbent = exact_by_behavior.get(behavior_key)
            rank = (candidate["complexity"], _canonical(candidate["program"]))
            if incumbent is None or rank < (incumbent["complexity"], _canonical(incumbent["program"])):
                exact_by_behavior[behavior_key] = candidate
        ordered = sorted(
            exact_by_behavior.values(),
            key=lambda item: (item["complexity"], item["evidence"]["behavior_hash"], _canonical(item["program"])),
        )
        return ordered[: bounded["max_candidates"]]
    except Exception:
        return []


__all__ = ["compile_task"]
