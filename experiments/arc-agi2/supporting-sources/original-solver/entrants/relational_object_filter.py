"""Replayable relational object filtering entrant for PR-LASM Block 14.

This entrant searches a finite, label-blind grammar over connected components.
Programs select object sets using dynamic structural roles: size extrema,
topology, repeated shape, rare-marker counts, containment, alignment, and
reference-object shape correspondence.  Selected sets can be deleted,
retained, or recolored with a dynamically resolved color role.

Every admitted program exactly replays all demonstrations, is executable from
its JSON record, survives leave-one-demonstration-out reinduction, and commutes
with D4 and bounded palette gauges.  Search exhaustion, structural ties, or
near-MDL test disagreement cause abstention.  Task identities and test labels
are never inspected by compilation or replay.

Author: Komorebi P.
"""
from __future__ import annotations

import argparse
from collections import Counter, deque
from dataclasses import dataclass
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


Grid = tuple[tuple[int, ...], ...]
Cell = tuple[int, int]
SCHEMA = "komorebi.pr_lasm.block14.relational_object_filter.program.v1"
SCAN_SCHEMA = "komorebi.pr_lasm.block14.relational_object_filter.scan_freeze.v1"
AUTHOR = "Komorebi P."
ORTHOGONAL: tuple[Cell, ...] = ((-1, 0), (0, -1), (0, 1), (1, 0))
EIGHT: tuple[Cell, ...] = tuple(
    (dr, dc)
    for dr in (-1, 0, 1)
    for dc in (-1, 0, 1)
    if (dr, dc) != (0, 0)
)

DEFAULTS = {
    "max_candidates": 1,
    "max_programs": 2_048,
    "max_evaluations": 16_000,
    "max_grid_cells": 900,
    "max_components": 128,
    "max_gauge_checks": 1_024,
    "mdl_slack": 1,
    "loo_slack": 0,
    "min_demos": 2,
}
HARD_CAPS = {
    "max_candidates": 16,
    "max_programs": 4_096,
    "max_evaluations": 80_000,
    "max_grid_cells": 3_600,
    "max_components": 256,
    "max_gauge_checks": 2_048,
    "mdl_slack": 3,
    "loo_slack": 2,
    "min_demos": 10,
}


class Undefined(ValueError):
    """A structural role is absent, tied, or inapplicable."""


def _canonical(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


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
    aliases = {"candidate_cap": "max_candidates"}
    for raw_name, candidate in value.items():
        name = aliases.get(str(raw_name), str(raw_name))
        if name not in DEFAULTS:
            continue
        if isinstance(candidate, bool) or not isinstance(candidate, int):
            raise Undefined(f"invalid limit {raw_name}")
        minimum = 0 if name in {"mdl_slack", "loo_slack"} else 1
        if candidate < minimum:
            raise Undefined(f"invalid limit {raw_name}")
        result[name] = min(candidate, HARD_CAPS[name])
    return result


def _sanitize(
    task: Any, limits: Mapping[str, int]
) -> tuple[tuple[tuple[Grid, Grid], ...], tuple[Grid, ...]]:
    if not isinstance(task, Mapping):
        raise Undefined("task must be a mapping")
    train = task.get("train")
    test = task.get("test")
    if (
        not isinstance(train, Sequence)
        or isinstance(train, (str, bytes))
        or not train
        or not isinstance(test, Sequence)
        or isinstance(test, (str, bytes))
        or not test
    ):
        raise Undefined("task needs nonempty train and test splits")
    demonstrations: list[tuple[Grid, Grid]] = []
    tests: list[Grid] = []
    for example in train:
        if not isinstance(example, Mapping):
            raise Undefined("invalid demonstration")
        try:
            source = _grid(example["input"], limits["max_grid_cells"])
            target = _grid(example["output"], limits["max_grid_cells"])
        except (KeyError, TypeError) as error:
            raise Undefined("invalid demonstration") from error
        demonstrations.append((source, target))
    for example in test:
        if not isinstance(example, Mapping) or "input" not in example:
            raise Undefined("invalid test input")
        tests.append(_grid(example["input"], limits["max_grid_cells"]))
    return tuple(demonstrations), tuple(tests)


def _shape(grid: Grid) -> tuple[int, int]:
    return len(grid), len(grid[0])


def _unique_extreme(values: Mapping[int, int], *, maximum: bool) -> int:
    if not values:
        raise Undefined("empty role population")
    wanted = max(values.values()) if maximum else min(values.values())
    winners = sorted(key for key, value in values.items() if value == wanted)
    if len(winners) != 1:
        raise Undefined("role extreme is tied")
    return winners[0]


def _background(grid: Grid, role: str) -> int:
    height, width = _shape(grid)
    if role == "mode":
        counts = Counter(cell for row in grid for cell in row)
    elif role == "border_mode":
        counts = Counter(
            grid[row][col]
            for row in range(height)
            for col in range(width)
            if row in {0, height - 1} or col in {0, width - 1}
        )
    elif role == "corners":
        corners = (grid[0][0], grid[0][-1], grid[-1][0], grid[-1][-1])
        if len(set(corners)) != 1:
            raise Undefined("corner background is not unique")
        return corners[0]
    else:
        raise Undefined("unknown background role")
    return _unique_extreme(dict(counts), maximum=True)


def _normalize_positions(cells: Iterable[Cell]) -> tuple[Cell, ...]:
    points = tuple(cells)
    top = min(row for row, _ in points)
    left = min(col for _, col in points)
    return tuple(sorted((row - top, col - left) for row, col in points))


def _d4_shape(cells: Iterable[Cell]) -> tuple[Cell, ...]:
    base = _normalize_positions(cells)
    variants: list[tuple[Cell, ...]] = []
    current = base
    for _ in range(4):
        variants.append(_normalize_positions(current))
        variants.append(_normalize_positions((row, -col) for row, col in current))
        current = _normalize_positions((col, -row) for row, col in current)
    return min(variants)


@dataclass(frozen=True, slots=True)
class Component:
    cells: tuple[tuple[int, int, int], ...]
    grid_height: int
    grid_width: int

    @property
    def positions(self) -> frozenset[Cell]:
        return frozenset((row, col) for row, col, _ in self.cells)

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
    def perimeter(self) -> int:
        positions = self.positions
        return sum(
            (row + dr, col + dc) not in positions
            for row, col in positions
            for dr, dc in ORTHOGONAL
        )

    @property
    def colors(self) -> tuple[int, ...]:
        return tuple(sorted({color for _, _, color in self.cells}))

    @property
    def color_counts(self) -> Counter[int]:
        return Counter(color for _, _, color in self.cells)

    @property
    def center2(self) -> tuple[int, int]:
        return self.top + self.bottom, self.left + self.right

    @property
    def solid_rectangle(self) -> bool:
        return self.area == self.bbox_area

    @property
    def line(self) -> bool:
        return self.height == 1 or self.width == 1

    @property
    def square(self) -> bool:
        return self.height == self.width

    @property
    def touches_border(self) -> bool:
        return (
            self.top == 0
            or self.left == 0
            or self.bottom == self.grid_height - 1
            or self.right == self.grid_width - 1
        )

    @property
    def shape(self) -> tuple[Cell, ...]:
        return _normalize_positions(self.positions)

    @property
    def d4_shape(self) -> tuple[Cell, ...]:
        return _d4_shape(self.positions)

    @property
    def hole_count(self) -> int:
        occupied = self.positions
        empty = {
            (row, col)
            for row in range(self.top, self.bottom + 1)
            for col in range(self.left, self.right + 1)
            if (row, col) not in occupied
        }
        holes = 0
        while empty:
            seed = min(empty)
            queue = deque([seed])
            empty.remove(seed)
            region = {seed}
            while queue:
                row, col = queue.popleft()
                for dr, dc in ORTHOGONAL:
                    neighbor = row + dr, col + dc
                    if neighbor in empty:
                        empty.remove(neighbor)
                        region.add(neighbor)
                        queue.append(neighbor)
            if all(
                self.top < row < self.bottom and self.left < col < self.right
                for row, col in region
            ):
                holes += 1
        return holes

    def contains_bbox(self, other: "Component") -> bool:
        return (
            self.top <= other.top
            and self.left <= other.left
            and self.bottom >= other.bottom
            and self.right >= other.right
            and (self.top, self.left, self.bottom, self.right)
            != (other.top, other.left, other.bottom, other.right)
        )

    def record(self, index: int) -> dict[str, Any]:
        return {
            "index": index,
            "area": self.area,
            "bbox": [self.top, self.left, self.bottom, self.right],
            "bbox_area": self.bbox_area,
            "colors": list(self.colors),
            "holes": self.hole_count,
            "solid_rectangle": self.solid_rectangle,
            "touches_border": self.touches_border,
            "shape_hash": _digest(self.shape),
            "d4_shape_hash": _digest(self.d4_shape),
        }


@dataclass(frozen=True, slots=True)
class Scene:
    grid: Grid
    background: int
    components: tuple[Component, ...]

    @property
    def foreground_counts(self) -> Counter[int]:
        return Counter(
            cell for row in self.grid for cell in row if cell != self.background
        )

    def record(self, *, background_role: str, connectivity: int, partition: str) -> dict[str, Any]:
        return {
            "kind": "component_scene",
            "background_role": background_role,
            "background": self.background,
            "connectivity": connectivity,
            "partition": partition,
            "component_count": len(self.components),
            "components": [
                component.record(index) for index, component in enumerate(self.components)
            ],
        }


SceneCache = dict[tuple[Grid, str, int, str, int], Scene]


def _scene(
    grid: Grid,
    background_role: str,
    connectivity: int,
    partition: str,
    max_components: int,
    cache: SceneCache | None = None,
) -> Scene:
    key = grid, background_role, connectivity, partition, max_components
    if cache is not None and key in cache:
        return cache[key]
    if connectivity not in {4, 8} or partition not in {"mono", "foreground"}:
        raise Undefined("invalid component grammar")
    background = _background(grid, background_role)
    steps = ORTHOGONAL if connectivity == 4 else EIGHT
    height, width = _shape(grid)
    seen: set[Cell] = set()
    components: list[Component] = []
    for row in range(height):
        for col in range(width):
            if (row, col) in seen or grid[row][col] == background:
                continue
            seed_color = grid[row][col]
            queue = deque([(row, col)])
            seen.add((row, col))
            cells: list[tuple[int, int, int]] = []
            while queue:
                current_row, current_col = queue.popleft()
                cells.append((current_row, current_col, grid[current_row][current_col]))
                for dr, dc in steps:
                    next_row, next_col = current_row + dr, current_col + dc
                    if not (0 <= next_row < height and 0 <= next_col < width):
                        continue
                    if (next_row, next_col) in seen:
                        continue
                    color = grid[next_row][next_col]
                    if color == background or (partition == "mono" and color != seed_color):
                        continue
                    seen.add((next_row, next_col))
                    queue.append((next_row, next_col))
            components.append(
                Component(tuple(sorted(cells)), grid_height=height, grid_width=width)
            )
            if len(components) > max_components:
                raise Undefined("component count exceeds declared budget")
    if not components:
        raise Undefined("scene has no foreground components")
    result = Scene(grid, background, tuple(components))
    if cache is not None:
        cache[key] = result
    return result


def _rare_color(scene: Scene) -> int:
    return _unique_extreme(dict(scene.foreground_counts), maximum=False)


def _common_color(scene: Scene) -> int:
    return _unique_extreme(dict(scene.foreground_counts), maximum=True)


def _component_attribute(component: Component, name: str) -> int:
    values = {
        "area": component.area,
        "bbox_area": component.bbox_area,
        "height": component.height,
        "width": component.width,
        "perimeter": component.perimeter,
        "holes": component.hole_count,
        "color_count": len(component.colors),
    }
    if name not in values:
        raise Undefined("unknown component attribute")
    return values[name]


def _require_contrast(
    components: Sequence[Component], selected: Sequence[int]
) -> tuple[int, ...]:
    result = tuple(sorted(set(selected)))
    if not result or len(result) == len(components):
        raise Undefined("selector lacks positive/negative contrast")
    return result


def _unique_singleton_marker(scene: Scene) -> int:
    counts = scene.foreground_counts
    rare = _unique_extreme(dict(counts), maximum=False)
    candidates = [
        index
        for index, component in enumerate(scene.components)
        if component.area == 1 and component.colors == (rare,)
    ]
    if len(candidates) != 1:
        raise Undefined("singleton marker role is absent or tied")
    return candidates[0]


def _cell_distance(left: Component, right: Component) -> int:
    return min(
        abs(a_row - b_row) + abs(a_col - b_col)
        for a_row, a_col in left.positions
        for b_row, b_col in right.positions
    )


def _select_general(scene: Scene, selector: Mapping[str, Any]) -> tuple[int, ...]:
    components = scene.components
    if len(components) < 2:
        raise Undefined("general filter needs at least two components")
    kind = selector.get("kind")
    if kind == "extreme":
        attribute = str(selector.get("attribute"))
        order = selector.get("order")
        values = [_component_attribute(component, attribute) for component in components]
        wanted = min(values) if order == "min" else max(values) if order == "max" else None
        if wanted is None:
            raise Undefined("invalid extreme direction")
        selected = tuple(index for index, value in enumerate(values) if value == wanted)
        if len(selected) != 1:
            raise Undefined("extreme selector is tied")
        return selected
    if kind == "predicate":
        name = selector.get("name")
        tests = {
            "has_hole": lambda item: item.hole_count > 0,
            "solid_rectangle": lambda item: item.solid_rectangle,
            "non_solid": lambda item: not item.solid_rectangle,
            "line": lambda item: item.line,
            "square": lambda item: item.square,
            "touches_border": lambda item: item.touches_border,
            "interior": lambda item: not item.touches_border,
            "multicolor": lambda item: len(item.colors) > 1,
        }
        if name not in tests:
            raise Undefined("unknown topology predicate")
        return _require_contrast(
            components,
            [index for index, component in enumerate(components) if tests[name](component)],
        )
    if kind == "shape_frequency":
        signatures = [component.d4_shape for component in components]
        counts = Counter(signatures)
        relation = selector.get("relation")
        if relation == "singleton":
            selected = [index for index, signature in enumerate(signatures) if counts[signature] == 1]
        elif relation == "repeated":
            selected = [index for index, signature in enumerate(signatures) if counts[signature] > 1]
        elif relation == "unique_modal_class":
            maximum = max(counts.values())
            classes = [signature for signature, count in counts.items() if count == maximum]
            if len(classes) != 1:
                raise Undefined("modal shape class is tied")
            selected = [index for index, signature in enumerate(signatures) if signature == classes[0]]
        else:
            raise Undefined("unknown shape-frequency relation")
        return _require_contrast(components, selected)
    if kind == "containment":
        relation = selector.get("relation")
        if relation == "contains":
            selected = [
                index
                for index, component in enumerate(components)
                if any(
                    index != other_index and component.contains_bbox(other)
                    for other_index, other in enumerate(components)
                )
            ]
        elif relation == "contained":
            selected = [
                index
                for index, component in enumerate(components)
                if any(
                    index != other_index and other.contains_bbox(component)
                    for other_index, other in enumerate(components)
                )
            ]
        else:
            raise Undefined("unknown containment relation")
        return _require_contrast(components, selected)
    if kind == "marker_relation":
        marker_index = _unique_singleton_marker(scene)
        marker = components[marker_index]
        universe = [index for index in range(len(components)) if index != marker_index]
        relation = selector.get("relation")
        if relation in {"nearest", "farthest"}:
            distances = {index: _cell_distance(components[index], marker) for index in universe}
            wanted = min(distances.values()) if relation == "nearest" else max(distances.values())
            selected = [index for index, value in distances.items() if value == wanted]
            if len(selected) != 1:
                raise Undefined("marker distance relation is tied")
            return tuple(selected)
        if relation == "aligned":
            marker_row, marker_col = next(iter(marker.positions))
            selected = [
                index
                for index in universe
                if any(row == marker_row or col == marker_col for row, col in components[index].positions)
            ]
            relative = _require_contrast(
                [components[index] for index in universe],
                [universe.index(index) for index in selected],
            )
            return tuple(universe[index] for index in relative)
        if relation == "contains":
            selected = [
                index for index in universe if components[index].contains_bbox(marker)
            ]
            if not selected:
                raise Undefined("no object contains the marker")
            return tuple(selected)
        raise Undefined("unknown marker relation")
    raise Undefined("unknown selector kind")


def _apply_action(
    scene: Scene,
    selected: Sequence[int],
    *,
    universe: Sequence[int],
    action: str,
    paint: int | None = None,
) -> Grid:
    selected_set = set(selected)
    universe_set = set(universe)
    if not selected_set or not selected_set <= universe_set:
        raise Undefined("invalid selected component set")
    mutable = [list(row) for row in scene.grid]
    if action == "delete":
        edited = selected_set
        color = scene.background
    elif action == "retain":
        edited = universe_set - selected_set
        color = scene.background
        if not edited:
            raise Undefined("retain action removes nothing")
    elif action == "recolor":
        if paint is None or paint == scene.background:
            raise Undefined("invalid recolor role")
        edited = selected_set
        color = paint
    else:
        raise Undefined("unknown set action")
    changed = False
    for index in edited:
        for row, col, _ in scene.components[index].cells:
            if mutable[row][col] != color:
                mutable[row][col] = color
                changed = True
    if not changed:
        raise Undefined("action is an identity")
    return tuple(tuple(row) for row in mutable)


def _execute_general(
    program: Mapping[str, Any], grid: Grid, limits: Mapping[str, int], cache: SceneCache
) -> tuple[Grid, Scene, tuple[int, ...], int | None]:
    scene = _scene(
        grid,
        str(program["background"]),
        int(program["connectivity"]),
        str(program["partition"]),
        limits["max_components"],
        cache,
    )
    selected = _select_general(scene, program["selector"])
    paint_role = program.get("paint")
    paint = None
    if paint_role == "rarest_foreground":
        paint = _rare_color(scene)
    elif paint_role == "most_frequent_foreground":
        paint = _common_color(scene)
    elif paint_role is not None:
        raise Undefined("unknown paint role")
    output = _apply_action(
        scene,
        selected,
        universe=tuple(range(len(scene.components))),
        action=str(program["action"]),
        paint=paint,
    )
    return output, scene, selected, paint


def _execute_rare_count(
    program: Mapping[str, Any], grid: Grid, limits: Mapping[str, int], cache: SceneCache
) -> tuple[Grid, Scene, tuple[int, ...], int | None]:
    scene = _scene(
        grid,
        str(program["background"]),
        int(program["connectivity"]),
        "foreground",
        limits["max_components"],
        cache,
    )
    if len(scene.components) < 3 or len(scene.foreground_counts) != 2:
        raise Undefined("rare-count filtering needs multiple two-color compound objects")
    if not all(component.solid_rectangle for component in scene.components):
        raise Undefined("rare-count filtering requires solid rectangular supports")
    rare = _rare_color(scene)
    common = next(color for color in scene.foreground_counts if color != rare)
    counts = [component.color_counts[rare] for component in scene.components]
    relation = program["relation"]
    if relation in {"unique_min", "unique_max"}:
        wanted = min(counts) if relation == "unique_min" else max(counts)
        selected = tuple(index for index, value in enumerate(counts) if value == wanted)
        if len(selected) != 1:
            raise Undefined("rare-count extreme is tied")
    elif relation == "greater_than_one":
        selected = tuple(index for index, value in enumerate(counts) if value > 1)
    elif relation == "at_most_one":
        selected = tuple(index for index, value in enumerate(counts) if value <= 1)
    elif relation == "zero":
        selected = tuple(index for index, value in enumerate(counts) if value == 0)
    elif relation == "one":
        selected = tuple(index for index, value in enumerate(counts) if value == 1)
    else:
        raise Undefined("unknown rare-count relation")
    selected = _require_contrast(scene.components, selected)
    paint_role = program.get("paint")
    paint = rare if paint_role == "rare" else common if paint_role == "common" else None
    output = _apply_action(
        scene,
        selected,
        universe=tuple(range(len(scene.components))),
        action=str(program["action"]),
        paint=paint,
    )
    return output, scene, selected, paint


def _reference_component(scene: Scene, role: str) -> int:
    if role == "rarest_color":
        color = _rare_color(scene)
        candidates = [
            index for index, component in enumerate(scene.components) if component.colors == (color,)
        ]
    elif role == "contained":
        candidates = [
            index
            for index, component in enumerate(scene.components)
            if any(
                index != other_index
                and other.contains_bbox(component)
                and other.colors != component.colors
                for other_index, other in enumerate(scene.components)
            )
        ]
    elif role == "unique_min_area":
        minimum = min(component.area for component in scene.components)
        candidates = [
            index for index, component in enumerate(scene.components) if component.area == minimum
        ]
    else:
        raise Undefined("unknown reference role")
    if len(candidates) != 1:
        raise Undefined("reference object role is absent or tied")
    return candidates[0]


def _execute_reference_shape(
    program: Mapping[str, Any], grid: Grid, limits: Mapping[str, int], cache: SceneCache
) -> tuple[Grid, Scene, tuple[int, ...], int | None]:
    scene = _scene(
        grid,
        str(program["background"]),
        int(program["connectivity"]),
        "mono",
        limits["max_components"],
        cache,
    )
    reference_index = _reference_component(scene, str(program["reference_role"]))
    reference = scene.components[reference_index]
    component_counts = Counter(
        component.colors[0]
        for index, component in enumerate(scene.components)
        if index != reference_index and len(component.colors) == 1
    )
    if not component_counts:
        raise Undefined("reference has no target population")
    target_color = _unique_extreme(dict(component_counts), maximum=True)
    universe = tuple(
        index
        for index, component in enumerate(scene.components)
        if index != reference_index and component.colors == (target_color,)
    )
    if len(universe) < 2:
        raise Undefined("shape correspondence needs target contrast")
    signature_name = str(program["shape_match"])
    signature = reference.shape if signature_name == "exact" else reference.d4_shape
    selected = tuple(
        index
        for index in universe
        if (
            scene.components[index].shape
            if signature_name == "exact"
            else scene.components[index].d4_shape
        )
        == signature
    )
    if not selected or len(selected) == len(universe):
        raise Undefined("reference shape lacks matched/unmatched target contrast")
    paint = reference.colors[0]
    output = _apply_action(
        scene,
        selected,
        universe=universe,
        action=str(program["action"]),
        paint=paint,
    )
    return output, scene, selected, paint


def _execute_anchor_key(
    program: Mapping[str, Any], grid: Grid, limits: Mapping[str, int], cache: SceneCache
) -> tuple[Grid, Scene, tuple[int, ...], int | None]:
    scene = _scene(
        grid,
        str(program["background"]),
        int(program["connectivity"]),
        "mono",
        limits["max_components"],
        cache,
    )
    maximum = max(component.area for component in scene.components)
    anchors = [
        index for index, component in enumerate(scene.components) if component.area == maximum
    ]
    if len(anchors) != 1:
        raise Undefined("anchor is not uniquely largest")
    anchor_index = anchors[0]
    anchor = scene.components[anchor_index]
    if anchor.solid_rectangle or anchor.area < 3:
        raise Undefined("anchor must expose an interior key region")
    keys = [
        index
        for index, component in enumerate(scene.components)
        if index != anchor_index and component.area == 1 and anchor.contains_bbox(component)
    ]
    if len(keys) != 1:
        raise Undefined("anchor key is absent or tied")
    key_index = keys[0]
    key_color = scene.components[key_index].colors[0]
    selected = tuple(
        index
        for index, component in enumerate(scene.components)
        if index not in {anchor_index, key_index} and component.colors == (key_color,)
    )
    if not selected:
        raise Undefined("anchor key has no external matches")
    output = _apply_action(
        scene,
        selected,
        universe=selected,
        action="delete",
    )
    return output, scene, selected, None


def _execute_directional_marker(
    program: Mapping[str, Any], grid: Grid, limits: Mapping[str, int], cache: SceneCache
) -> tuple[Grid, Scene, tuple[int, ...], int | None]:
    scene = _scene(
        grid,
        str(program["background"]),
        4,
        "mono",
        limits["max_components"],
        cache,
    )
    counts = scene.foreground_counts
    pairs: list[tuple[int, int, int, int]] = []
    for bar_index, bar in enumerate(scene.components):
        if not bar.line or bar.area < 3 or bar.area % 2 == 0 or len(bar.colors) != 1:
            continue
        if counts[bar.colors[0]] != bar.area:
            continue
        center_row2, center_col2 = bar.center2
        if center_row2 % 2 or center_col2 % 2:
            continue
        center_row, center_col = center_row2 // 2, center_col2 // 2
        for marker_index, marker in enumerate(scene.components):
            if marker_index == bar_index or marker.area != 1 or len(marker.colors) != 1:
                continue
            if counts[marker.colors[0]] != 1 or marker.colors == bar.colors:
                continue
            marker_row, marker_col = next(iter(marker.positions))
            dr, dc = marker_row - center_row, marker_col - center_col
            if abs(dr) + abs(dc) != 1:
                continue
            if (bar.height == 1 and dc != 0) or (bar.width == 1 and dr != 0):
                continue
            pairs.append((bar_index, marker_index, dr, dc))
    if len(pairs) != 1:
        raise Undefined("directional bar/marker role is absent or tied")
    bar_index, marker_index, dr, dc = pairs[0]
    excluded_colors = {
        scene.components[bar_index].colors[0], scene.components[marker_index].colors[0]
    }
    target_colors = sorted(set(counts) - excluded_colors)
    if len(target_colors) != 1:
        raise Undefined("directional marker target color is ambiguous")
    target_color = target_colors[0]
    center_row2, center_col2 = scene.components[bar_index].center2
    center_row, center_col = center_row2 // 2, center_col2 // 2
    universe = tuple(
        index
        for index, component in enumerate(scene.components)
        if component.colors == (target_color,)
    )
    selected: list[int] = []
    for index in universe:
        positions = scene.components[index].positions
        if dr > 0 and any(col == center_col and row < center_row for row, col in positions):
            selected.append(index)
        elif dr < 0 and any(col == center_col and row > center_row for row, col in positions):
            selected.append(index)
        elif dc > 0 and any(row == center_row and col < center_col for row, col in positions):
            selected.append(index)
        elif dc < 0 and any(row == center_row and col > center_col for row, col in positions):
            selected.append(index)
    selected_tuple = _require_contrast(
        [scene.components[index] for index in universe],
        [universe.index(index) for index in selected],
    )
    selected_indices = tuple(universe[index] for index in selected_tuple)
    output = _apply_action(
        scene,
        selected_indices,
        universe=universe,
        action="delete",
    )
    return output, scene, selected_indices, None


def _execute(
    program: Mapping[str, Any],
    grid: Grid,
    limits: Mapping[str, int],
    cache: SceneCache | None = None,
) -> tuple[Grid, Scene, tuple[int, ...], int | None]:
    if not isinstance(program, Mapping) or program.get("schema") != SCHEMA:
        raise Undefined("invalid relational-filter program")
    op = program.get("op")
    scene_cache = {} if cache is None else cache
    if op == "component_filter":
        return _execute_general(program, grid, limits, scene_cache)
    if op == "rare_marker_count_filter":
        return _execute_rare_count(program, grid, limits, scene_cache)
    if op == "reference_shape_filter":
        return _execute_reference_shape(program, grid, limits, scene_cache)
    if op == "anchor_key_color_delete":
        return _execute_anchor_key(program, grid, limits, scene_cache)
    if op == "directional_marker_delete":
        return _execute_directional_marker(program, grid, limits, scene_cache)
    raise Undefined("unknown relational-filter operation")


def execute_program(program: Mapping[str, Any], value: Any) -> list[list[int]]:
    """Execute one serialized program on one grid."""

    limits = dict(DEFAULTS)
    grid = _grid(value, limits["max_grid_cells"])
    output, _, _, _ = _execute(program, grid, limits)
    return _plain(output)


def replay_program(program: Mapping[str, Any], value: Any) -> dict[str, Any]:
    """Tournament replay hook with a complete parse/select/render trace."""

    limits = dict(DEFAULTS)
    grid = _grid(value, limits["max_grid_cells"])
    output, scene, selected, paint = _execute(program, grid, limits)
    scene_record = scene.record(
        background_role=str(program["background"]),
        connectivity=int(program.get("connectivity", 4)),
        partition=(
            "foreground"
            if program["op"] == "rare_marker_count_filter"
            else str(program.get("partition", "mono"))
        ),
    )
    selection_record = {
        "kind": "component_selection",
        "operation": program["op"],
        "background": scene.background,
        "selected_component_indices": list(selected),
        "selected_cell_count": sum(scene.components[index].area for index in selected),
        "paint": paint,
    }
    return {
        "output": _plain(output),
        "stages": [
            {"name": "parse_components", "input": _plain(grid), "output": scene_record},
            {"name": "select_relational_set", "input": scene_record, "output": selection_record},
            {"name": "render_set_action", "input": selection_record, "output": _plain(output)},
        ],
    }


def _program(
    op: str,
    background: str,
    **fields: Any,
) -> dict[str, Any]:
    return {"schema": SCHEMA, "op": op, "background": background, **fields}


def _programs() -> tuple[dict[str, Any], ...]:
    result: list[dict[str, Any]] = []
    backgrounds = ("mode", "border_mode", "corners")
    connectivities = (4, 8)
    selectors: list[dict[str, Any]] = []
    for attribute in ("area", "bbox_area", "height", "width", "perimeter", "holes"):
        for order in ("min", "max"):
            selectors.append({"kind": "extreme", "attribute": attribute, "order": order})
    for name in (
        "has_hole",
        "solid_rectangle",
        "non_solid",
        "line",
        "square",
        "touches_border",
        "interior",
        "multicolor",
    ):
        selectors.append({"kind": "predicate", "name": name})
    for relation in ("singleton", "repeated", "unique_modal_class"):
        selectors.append({"kind": "shape_frequency", "relation": relation})
    for relation in ("contains", "contained"):
        selectors.append({"kind": "containment", "relation": relation})
    for relation in ("nearest", "farthest", "aligned", "contains"):
        selectors.append({"kind": "marker_relation", "relation": relation})

    actions = (
        ("delete", None),
        ("retain", None),
        ("recolor", "rarest_foreground"),
        ("recolor", "most_frequent_foreground"),
    )
    for background, connectivity, partition, selector, (action, paint) in itertools.product(
        backgrounds, connectivities, ("mono", "foreground"), selectors, actions
    ):
        fields: dict[str, Any] = {
            "connectivity": connectivity,
            "partition": partition,
            "selector": selector,
            "action": action,
        }
        if paint is not None:
            fields["paint"] = paint
        result.append(_program("component_filter", background, **fields))

    for background, connectivity, relation, (action, paint) in itertools.product(
        backgrounds,
        connectivities,
        ("unique_min", "unique_max", "greater_than_one", "at_most_one", "zero", "one"),
        (("delete", None), ("retain", None), ("recolor", "rare"), ("recolor", "common")),
    ):
        fields = {"connectivity": connectivity, "relation": relation, "action": action}
        if paint is not None:
            fields["paint"] = paint
        result.append(_program("rare_marker_count_filter", background, **fields))

    for background, connectivity, reference_role, shape_match, action in itertools.product(
        backgrounds,
        connectivities,
        ("rarest_color", "contained", "unique_min_area"),
        ("exact", "d4"),
        ("delete", "retain", "recolor"),
    ):
        result.append(
            _program(
                "reference_shape_filter",
                background,
                connectivity=connectivity,
                reference_role=reference_role,
                shape_match=shape_match,
                action=action,
            )
        )
    for background, connectivity in itertools.product(backgrounds, connectivities):
        result.append(
            _program(
                "anchor_key_color_delete", background, connectivity=connectivity
            )
        )
    for background in backgrounds:
        result.append(_program("directional_marker_delete", background, connectivity=4))
    unique = {_canonical(program): program for program in result}
    return tuple(unique[key] for key in sorted(unique))


def _complexity(program: Mapping[str, Any]) -> int:
    op = program["op"]
    background_cost = {"mode": 0, "border_mode": 1, "corners": 1}[program["background"]]
    connectivity_cost = int(program.get("connectivity", 4) == 8)
    if op == "component_filter":
        selector = program["selector"]
        selector_cost = {
            "extreme": 1,
            "predicate": 1,
            "shape_frequency": 2,
            "containment": 2,
            "marker_relation": 3,
        }[selector["kind"]]
        action_cost = 1 if program["action"] in {"delete", "retain"} else 2
        return 3 + background_cost + connectivity_cost + selector_cost + action_cost
    if op == "rare_marker_count_filter":
        relation_cost = 1 if program["relation"] in {"unique_min", "unique_max"} else 2
        action_cost = 1 if program["action"] in {"delete", "retain"} else 2
        return 5 + background_cost + connectivity_cost + relation_cost + action_cost
    if op == "reference_shape_filter":
        return (
            6
            + background_cost
            + connectivity_cost
            + int(program["reference_role"] != "rarest_color")
            + int(program["shape_match"] == "d4")
            + int(program["action"] == "recolor")
        )
    if op == "anchor_key_color_delete":
        return 7 + background_cost + connectivity_cost
    if op == "directional_marker_delete":
        return 8 + background_cost
    raise Undefined("unknown operation complexity")


@dataclass(frozen=True, slots=True)
class Evaluation:
    program: Mapping[str, Any]
    complexity: int
    train_outputs: tuple[Grid | None, ...]
    test_outputs: tuple[Grid | None, ...]


def _evaluate(
    program: Mapping[str, Any],
    demonstrations: Sequence[tuple[Grid, Grid]],
    tests: Sequence[Grid],
    limits: Mapping[str, int],
    cache: SceneCache,
) -> Evaluation:
    train_outputs: list[Grid | None] = []
    test_outputs: list[Grid | None] = []
    for source, _ in demonstrations:
        try:
            train_outputs.append(_execute(program, source, limits, cache)[0])
        except Undefined:
            train_outputs.append(None)
    for source in tests:
        try:
            test_outputs.append(_execute(program, source, limits, cache)[0])
        except Undefined:
            test_outputs.append(None)
    return Evaluation(program, _complexity(program), tuple(train_outputs), tuple(test_outputs))


def _loo_stable(
    evaluations: Sequence[Evaluation],
    targets: Sequence[Grid],
    *,
    slack: int,
) -> tuple[bool, int]:
    if len(targets) < 2:
        return False, 0
    checked = 0
    for held_out in range(len(targets)):
        fits = [
            evaluation
            for evaluation in evaluations
            if all(
                index == held_out or evaluation.train_outputs[index] == target
                for index, target in enumerate(targets)
            )
        ]
        if not fits:
            return False, checked
        best = min(evaluation.complexity for evaluation in fits)
        near = [evaluation for evaluation in fits if evaluation.complexity <= best + slack]
        predictions = {evaluation.train_outputs[held_out] for evaluation in near}
        checked += len(near)
        if None in predictions or predictions != {targets[held_out]}:
            return False, checked
    return True, checked


def _rotate90(grid: Grid) -> Grid:
    return tuple(tuple(row) for row in zip(*grid[::-1]))


def _d4_grids(grid: Grid) -> tuple[Grid, ...]:
    variants: list[Grid] = []
    current = grid
    for _ in range(4):
        variants.append(current)
        variants.append(tuple(tuple(reversed(row)) for row in current))
        current = _rotate90(current)
    unique = {_canonical(_plain(item)): item for item in variants}
    return tuple(unique[key] for key in sorted(unique))


def _palette_swap(grid: Grid, left: int, right: int) -> Grid:
    return tuple(
        tuple(right if cell == left else left if cell == right else cell for cell in row)
        for row in grid
    )


def _gauge_guard(
    program: Mapping[str, Any],
    demonstrations: Sequence[tuple[Grid, Grid]],
    limits: Mapping[str, int],
) -> tuple[bool, int, int]:
    d4_checks = 0
    palette_checks = 0
    required = sum(len(_d4_grids(source)) for source, _ in demonstrations)
    required += 45 * len(demonstrations)
    if required > limits["max_gauge_checks"]:
        return False, 0, 0
    for source, target in demonstrations:
        source_variants = _d4_grids(source)
        target_variants = _d4_grids(target)
        # Canonical sort is applied independently, so use the direct ordered
        # construction to preserve transform pairing instead.
        source_raw: list[Grid] = []
        target_raw: list[Grid] = []
        source_current, target_current = source, target
        for _ in range(4):
            source_raw.extend(
                (source_current, tuple(tuple(reversed(row)) for row in source_current))
            )
            target_raw.extend(
                (target_current, tuple(tuple(reversed(row)) for row in target_current))
            )
            source_current = _rotate90(source_current)
            target_current = _rotate90(target_current)
        paired: dict[str, tuple[Grid, Grid]] = {}
        for transformed_source, transformed_target in zip(source_raw, target_raw):
            paired.setdefault(_canonical(_plain(transformed_source)), (transformed_source, transformed_target))
        for transformed_source, transformed_target in paired.values():
            try:
                prediction = _execute(program, transformed_source, limits)[0]
            except Undefined:
                return False, d4_checks, palette_checks
            d4_checks += 1
            if prediction != transformed_target:
                return False, d4_checks, palette_checks
        # Every transposition on the ten-color alphabet includes background
        # movement and absent-color canaries while remaining finitely bounded.
        for left, right in itertools.combinations(range(10), 2):
            transformed_source = _palette_swap(source, left, right)
            transformed_target = _palette_swap(target, left, right)
            try:
                prediction = _execute(program, transformed_source, limits)[0]
            except Undefined:
                return False, d4_checks, palette_checks
            palette_checks += 1
            if prediction != transformed_target:
                return False, d4_checks, palette_checks
    return True, d4_checks, palette_checks


def compile_task(task: Any, limits: Any = None) -> list[dict[str, Any]]:
    """Compile at most one behaviorally unique, replayable object filter."""

    try:
        normalized_limits = _read_limits(limits)
        demonstrations, tests = _sanitize(task, normalized_limits)
    except Undefined:
        return []
    if len(demonstrations) < normalized_limits["min_demos"]:
        return []
    if any(_shape(source) != _shape(target) or source == target for source, target in demonstrations):
        return []
    programs = _programs()
    if len(programs) > normalized_limits["max_programs"]:
        return []
    required_evaluations = len(programs) * (len(demonstrations) + len(tests))
    if required_evaluations > normalized_limits["max_evaluations"]:
        return []
    cache: SceneCache = {}
    evaluations = [
        _evaluate(program, demonstrations, tests, normalized_limits, cache)
        for program in programs
    ]
    targets = tuple(target for _, target in demonstrations)
    exact = [
        evaluation
        for evaluation in evaluations
        if evaluation.train_outputs == targets and None not in evaluation.test_outputs
    ]
    if not exact:
        return []
    loo_stable, loo_programs_checked = _loo_stable(
        evaluations, targets, slack=normalized_limits["loo_slack"]
    )
    if not loo_stable:
        return []
    best_complexity = min(evaluation.complexity for evaluation in exact)
    near = [
        evaluation
        for evaluation in exact
        if evaluation.complexity <= best_complexity + normalized_limits["mdl_slack"]
    ]
    behaviors: dict[str, list[Evaluation]] = {}
    for evaluation in near:
        behavior = tuple(output for output in evaluation.test_outputs if output is not None)
        behaviors.setdefault(_digest([_plain(output) for output in behavior]), []).append(evaluation)
    if len(behaviors) != 1:
        return []
    behavior_hash, equivalent = next(iter(sorted(behaviors.items())))
    equivalent.sort(key=lambda item: (item.complexity, _canonical(item.program)))
    representative: Evaluation | None = None
    gauge_counts = (0, 0)
    for evaluation in equivalent:
        guarded, d4_checks, palette_checks = _gauge_guard(
            evaluation.program, demonstrations, normalized_limits
        )
        if guarded:
            representative = evaluation
            gauge_counts = d4_checks, palette_checks
            break
    if representative is None:
        return []
    candidate = {
        "family": "relational_object_filter",
        "program": json.loads(_canonical(representative.program)),
        "train_outputs": [_plain(output) for output in representative.train_outputs if output is not None],
        "test_outputs": [_plain(output) for output in representative.test_outputs if output is not None],
        "complexity": representative.complexity,
        "evidence": {
            "all_demos_exact": True,
            "exact_replay": True,
            "enumeration_complete": True,
            "programs_enumerated": len(programs),
            "program_evaluations": required_evaluations,
            "exact_programs": len(exact),
            "near_mdl_programs": len(near),
            "test_behavior_classes": len(behaviors),
            "equivalent_programs": len(equivalent),
            "behavior_hash": behavior_hash,
            "leave_one_out_stable": True,
            "leave_one_out_programs_checked": loo_programs_checked,
            "d4_equivariance_checks": gauge_counts[0],
            "palette_bijection_checks": gauge_counts[1],
            "task_identity_observed": False,
            "test_labels_observed": False,
        },
    }
    candidate["evidence"]["candidate_semantic_hash"] = _digest(candidate)
    return [candidate][: normalized_limits["max_candidates"]]


def _safe_task(task: Mapping[str, Any]) -> dict[str, Any]:
    """Create the exact challenge-only payload used by a scan freeze."""

    if not isinstance(task, Mapping):
        raise Undefined("task must be a mapping")
    train = task.get("train")
    test = task.get("test")
    if not isinstance(train, list) or not isinstance(test, list):
        raise Undefined("task splits are malformed")
    return {
        "train": [
            {"input": example["input"], "output": example["output"]}
            for example in train
        ],
        "test": [{"input": example["input"]} for example in test],
    }


def freeze_scan(
    challenges: Mapping[str, Mapping[str, Any]],
    *,
    limits: Mapping[str, Any] | None = None,
    source_hash: str | None = None,
    run_name: str = "relational-object-filter-scan",
) -> dict[str, Any]:
    """Freeze a deterministic challenge-only activation scan without baseline or labels."""

    records: dict[str, Any] = {}
    activated = 0
    for raw_task_id, task in sorted(challenges.items(), key=lambda item: str(item[0])):
        task_id = str(raw_task_id)
        safe = _safe_task(task)
        candidates = compile_task(safe, limits=limits)
        if len(candidates) > 1:
            raise AssertionError("compile_task violated its one-candidate contract")
        if candidates:
            activated += 1
        record = {
            "task_semantic_hash": _digest(safe),
            "status": "candidate" if candidates else "abstention",
            "candidates": candidates,
        }
        record["content_hash"] = _digest(record)
        records[task_id] = record
    body = {
        "schema": SCAN_SCHEMA,
        "schema_version": 1,
        "author": AUTHOR,
        "phase": "prediction_freeze_before_solution_open",
        "label_access": "none",
        "run_name": run_name,
        "source_hash": source_hash,
        "source_task_count": len(challenges),
        "activation_count": activated,
        "records": records,
        "claim_boundary": (
            "Challenge-only deterministic scan. Compilation received demonstrations and "
            "test inputs; no solution, score, baseline, or result artifact was opened."
        ),
    }
    body["semantic_hash"] = _digest(body)
    body["content_hash"] = _digest(body)
    return body


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".partial")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    temporary.replace(path)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--challenges", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--run-name", default="relational-object-filter-scan")
    args = parser.parse_args(argv)
    raw = args.challenges.read_bytes()
    challenges = json.loads(raw.decode("utf-8-sig"))
    if not isinstance(challenges, Mapping):
        raise ValueError("challenges JSON must contain an object")
    frozen = freeze_scan(
        challenges,
        source_hash=hashlib.sha256(raw).hexdigest(),
        run_name=args.run_name,
    )
    _write_json(args.output, frozen)
    print(
        _canonical(
            {
                "activation_count": frozen["activation_count"],
                "content_hash": frozen["content_hash"],
                "source_task_count": frozen["source_task_count"],
            }
        )
    )
    return 0


__all__ = [
    "AUTHOR",
    "DEFAULTS",
    "SCHEMA",
    "Undefined",
    "compile_task",
    "execute_program",
    "freeze_scan",
    "replay_program",
]


if __name__ == "__main__":
    raise SystemExit(main())
