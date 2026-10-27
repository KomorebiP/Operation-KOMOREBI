"""Task-local contextual recolor induction for PR-LASM Block 14.

The entrant handles same-footprint transformations whose output color depends
on local topology or object context.  It learns a small categorical rule table
over role-valued component/pixel features, requires exact demonstration replay,
leave-one-demonstration-out reconstruction, D4 and padding counterfactuals, and
unique minimum-description test behavior.

No task identifier, test label, solution, score, or corpus fingerprint is an
input to compilation or replay.

Author: Komorebi P.
"""
from __future__ import annotations

from collections import Counter, deque
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from fractions import Fraction
import hashlib
import itertools
import json
from typing import Any, Iterable


Grid = tuple[tuple[int, ...], ...]
Cell = tuple[int, int]
SCHEMA = "komorebi.pr_lasm.block14.contextual_recolor.v1"
AUTHOR = "Komorebi P."


class Undefined(ValueError):
    """A role, feature, or program is undefined on a supplied grid."""


@dataclass(frozen=True, slots=True)
class Limits:
    max_side: int = 30
    max_examples: int = 16
    max_entities: int = 6_000
    max_feature_depth: int = 2
    max_feature_sets: int = 12_000
    max_models: int = 384
    max_action_products: int = 64
    min_rule_demo_witnesses: int = 2
    ambiguity_slack: int = 1
    max_candidates: int = 1

    @classmethod
    def from_value(cls, value: Mapping[str, Any] | None) -> "Limits":
        if value is None:
            return cls()
        if not isinstance(value, Mapping):
            raise TypeError("limits must be a mapping")
        defaults = cls()
        fields = {
            name: int(value.get(name, getattr(defaults, name)))
            for name in cls.__dataclass_fields__
        }
        result = cls(**fields)
        for name in cls.__dataclass_fields__:
            minimum = 0 if name == "ambiguity_slack" else 1
            if getattr(result, name) < minimum:
                raise ValueError(f"limits.{name} is below {minimum}")
        return result


@dataclass(frozen=True, slots=True)
class Component:
    color: int
    cells: frozenset[Cell]
    bbox: tuple[int, int, int, int]
    area: int
    holes: int
    perimeter: int
    degree_histogram: tuple[int, ...]
    symmetry_order: int
    d4_shape_value: tuple[Cell, ...]

    @property
    def height(self) -> int:
        return self.bbox[1] - self.bbox[0] + 1

    @property
    def width(self) -> int:
        return self.bbox[3] - self.bbox[2] + 1

    @property
    def density(self) -> Fraction:
        return Fraction(self.area, self.height * self.width)

    @property
    def topology(self) -> tuple[Any, ...]:
        return (
            self.area,
            tuple(sorted((self.height, self.width))),
            (self.density.numerator, self.density.denominator),
            self.holes,
            self.perimeter,
            self.degree_histogram,
            self.symmetry_order,
        )

    @property
    def d4_shape(self) -> tuple[Cell, ...]:
        return self.d4_shape_value


@dataclass(slots=True)
class Scene:
    grid: Grid
    background: int
    background_tied: bool
    components: tuple[Component, ...]
    support_components: tuple[Component, ...]
    cell_component: dict[Cell, int]
    cell_support: dict[Cell, int]
    component_features: tuple[dict[str, Any], ...]
    component_action_values: tuple[dict[str, int | None], ...]
    color_counts: Counter[int]


@dataclass(frozen=True, slots=True)
class Entity:
    component_index: int
    cells: tuple[Cell, ...]
    pixel: Cell | None


@dataclass(frozen=True, slots=True)
class Observation:
    demo: int
    scene: Scene
    entity: Entity
    source: int
    target: int
    features: Mapping[str, Any]
    action_values: Mapping[str, int | None]


COMPONENT_FEATURE_COSTS: dict[str, int] = {
    "mono_area": 1,
    "mono_bbox": 1,
    "mono_density": 1,
    "mono_holes": 1,
    "mono_perimeter": 2,
    "mono_degree_histogram": 2,
    "mono_endpoint_count": 1,
    "mono_junction_count": 1,
    "mono_turn_count": 1,
    "mono_symmetry_order": 2,
    "mono_area_role": 1,
    "mono_same_color_area_role": 2,
    "mono_topology_peer_count": 2,
    "d4_shape_peer_count": 2,
    "d4_shape_other_color_peer_count": 2,
    "matches_rarest_graph_prototype": 2,
    "matches_rarest_d4_prototype": 2,
    "color_frequency_role": 1,
    "color_component_role": 2,
    "nearest_component_distance": 2,
    "nearest_component_relation": 3,
    "nearest_different_relation": 3,
    "support_area": 1,
    "support_bbox": 2,
    "support_mono_count": 2,
    "support_color_count": 2,
    "support_holes": 2,
}


PIXEL_FEATURE_COSTS: dict[str, int] = {
    **COMPONENT_FEATURE_COSTS,
    "same_degree4": 1,
    "same_degree8": 1,
    "support_degree4": 1,
    "support_degree8": 1,
    "neighbor_profile": 2,
    "local_same_topology": 2,
    "local_support_topology": 2,
    "bbox_distance_role": 2,
    "center_distance_role": 2,
    "row_column_same_role": 2,
    "row_column_support_role": 2,
    "nearest_other_color_distance": 2,
    "ray_foreground_role": 3,
}


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


def _jsonable(value: Any) -> Any:
    if isinstance(value, Fraction):
        return [value.numerator, value.denominator]
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in sorted(value.items())}
    return value


def _grid(value: Any, limits: Limits | None = None) -> Grid:
    bounds = limits or Limits()
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise TypeError("grid must be a sequence")
    if not value or len(value) > bounds.max_side:
        raise ValueError("invalid grid height")
    rows: list[tuple[int, ...]] = []
    width: int | None = None
    for raw_row in value:
        if not isinstance(raw_row, Sequence) or isinstance(raw_row, (str, bytes, bytearray)):
            raise TypeError("grid row must be a sequence")
        if not raw_row or len(raw_row) > bounds.max_side:
            raise ValueError("invalid grid width")
        row: list[int] = []
        for raw_cell in raw_row:
            if isinstance(raw_cell, bool) or not isinstance(raw_cell, int) or not 0 <= raw_cell <= 9:
                raise ValueError("invalid ARC color")
            row.append(int(raw_cell))
        if width is None:
            width = len(row)
        elif len(row) != width:
            raise ValueError("grid is not rectangular")
        rows.append(tuple(row))
    return tuple(rows)


def _plain(value: Grid) -> list[list[int]]:
    return [list(row) for row in value]


def _shape(value: Grid) -> tuple[int, int]:
    return len(value), len(value[0])


def _border_colors(value: Grid) -> list[int]:
    height, width = _shape(value)
    colors = list(value[0])
    if height > 1:
        colors.extend(value[-1])
    if height > 2:
        colors.extend(value[row][0] for row in range(1, height - 1))
        if width > 1:
            colors.extend(value[row][-1] for row in range(1, height - 1))
    return colors


def _background(value: Grid) -> tuple[int, bool]:
    counts = Counter(_border_colors(value))
    maximum = max(counts.values())
    winners = sorted(color for color, count in counts.items() if count == maximum)
    return winners[0], len(winners) != 1


def _neighbors(cell: Cell, connectivity: int) -> tuple[Cell, ...]:
    row, column = cell
    result = [(row - 1, column), (row + 1, column), (row, column - 1), (row, column + 1)]
    if connectivity == 8:
        result.extend(
            (
                (row - 1, column - 1), (row - 1, column + 1),
                (row + 1, column - 1), (row + 1, column + 1),
            )
        )
    return tuple(result)


def _hole_count(cells: frozenset[Cell], bbox: tuple[int, int, int, int]) -> int:
    top, bottom, left, right = bbox
    exterior: set[Cell] = set()
    queue: deque[Cell] = deque()
    for row in range(top - 1, bottom + 2):
        for column in (left - 1, right + 1):
            queue.append((row, column))
    for column in range(left - 1, right + 2):
        for row in (top - 1, bottom + 1):
            queue.append((row, column))
    bounds = (top - 1, bottom + 1, left - 1, right + 1)
    while queue:
        point = queue.popleft()
        if point in exterior or point in cells:
            continue
        row, column = point
        if not (bounds[0] <= row <= bounds[1] and bounds[2] <= column <= bounds[3]):
            continue
        exterior.add(point)
        queue.extend(_neighbors(point, 4))
    unseen = {
        (row, column)
        for row in range(top, bottom + 1)
        for column in range(left, right + 1)
        if (row, column) not in cells and (row, column) not in exterior
    }
    holes = 0
    while unseen:
        holes += 1
        root = min(unseen)
        unseen.remove(root)
        queue = deque([root])
        while queue:
            for other in _neighbors(queue.popleft(), 4):
                if other in unseen:
                    unseen.remove(other)
                    queue.append(other)
    return holes


def _normalize_points(points: Iterable[Cell]) -> frozenset[Cell]:
    values = tuple(points)
    row0 = min(row for row, _ in values)
    column0 = min(column for _, column in values)
    return frozenset((row - row0, column - column0) for row, column in values)


def _d4_point_sets(cells: frozenset[Cell]) -> tuple[frozenset[Cell], ...]:
    normalized = _normalize_points(cells)
    transforms: list[frozenset[Cell]] = []
    for swap in (False, True):
        for row_sign, column_sign in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
            transformed = []
            for row, column in normalized:
                first, second = (column, row) if swap else (row, column)
                transformed.append((row_sign * first, column_sign * second))
            transforms.append(_normalize_points(transformed))
    return tuple(transforms)


def _make_component(color: int, cells: set[Cell]) -> Component:
    frozen = frozenset(cells)
    rows = [row for row, _ in cells]
    columns = [column for _, column in cells]
    bbox = min(rows), max(rows), min(columns), max(columns)
    degrees = Counter(
        sum(other in frozen for other in _neighbors(cell, 4))
        for cell in frozen
    )
    degree_histogram = tuple(degrees.get(index, 0) for index in range(5))
    perimeter = sum(4 - sum(other in frozen for other in _neighbors(cell, 4)) for cell in frozen)
    normalized = _normalize_points(frozen)
    symmetry_order = sum(transformed == normalized for transformed in _d4_point_sets(frozen))
    d4_shape_value = min(tuple(sorted(points)) for points in _d4_point_sets(frozen))
    return Component(
        color=color,
        cells=frozen,
        bbox=bbox,
        area=len(frozen),
        holes=_hole_count(frozen, bbox),
        perimeter=perimeter,
        degree_histogram=degree_histogram,
        symmetry_order=symmetry_order,
        d4_shape_value=d4_shape_value,
    )


def _components(value: Grid, background: int, *, monochrome: bool) -> tuple[Component, ...]:
    height, width = _shape(value)
    unseen = {
        (row, column)
        for row in range(height)
        for column in range(width)
        if value[row][column] != background
    }
    result: list[Component] = []
    while unseen:
        root = min(unseen)
        unseen.remove(root)
        color = value[root[0]][root[1]]
        cells = {root}
        queue = deque([root])
        while queue:
            point = queue.popleft()
            for other in _neighbors(point, 4):
                if other not in unseen:
                    continue
                if monochrome and value[other[0]][other[1]] != color:
                    continue
                unseen.remove(other)
                cells.add(other)
                queue.append(other)
        result.append(_make_component(color if monochrome else -1, cells))
    return tuple(sorted(result, key=lambda item: (min(item.cells), item.color, item.area)))


def _rank_role(values: Sequence[int], selected: int) -> tuple[int, int, int]:
    return (
        sum(value < selected for value in values),
        sum(value == selected for value in values),
        sum(value > selected for value in values),
    )


def _component_distance(left: Component, right: Component) -> int:
    return min(abs(ar - br) + abs(ac - bc) for ar, ac in left.cells for br, bc in right.cells) - 1


def _relation(left: Component, right: Component, distance: int) -> tuple[Any, ...]:
    return (
        distance,
        (left.area > right.area) - (left.area < right.area),
        (left.height * left.width > right.height * right.width)
        - (left.height * left.width < right.height * right.width),
        int(left.topology == right.topology),
    )


def _turn_count(component: Component) -> int:
    result = 0
    for cell in component.cells:
        adjacent = [other for other in _neighbors(cell, 4) if other in component.cells]
        if len(adjacent) != 2:
            continue
        first = adjacent[0][0] - cell[0], adjacent[0][1] - cell[1]
        second = adjacent[1][0] - cell[0], adjacent[1][1] - cell[1]
        if (first[0] + second[0], first[1] + second[1]) != (0, 0):
            result += 1
    return result


def _graph_class(component: Component) -> tuple[int, int, int, int]:
    return (
        component.degree_histogram[1],
        sum(component.degree_histogram[3:]),
        _turn_count(component),
        component.holes,
    )


def _scene(value: Grid) -> Scene:
    background, tied = _background(value)
    components = _components(value, background, monochrome=True)
    support_components = _components(value, background, monochrome=False)
    cell_component = {
        cell: index for index, component in enumerate(components) for cell in component.cells
    }
    cell_support = {
        cell: index for index, component in enumerate(support_components) for cell in component.cells
    }
    color_counts = Counter(cell for row in value for cell in row if cell != background)
    color_component_counts = Counter(component.color for component in components)
    areas = [component.area for component in components]
    topology_counts = Counter(component.topology for component in components)
    shape_counts = Counter(component.d4_shape for component in components)
    features: list[dict[str, Any]] = []
    action_values: list[dict[str, int | None]] = []
    most_color: int | None = None
    least_color: int | None = None
    if color_counts:
        most_count, least_count = max(color_counts.values()), min(color_counts.values())
        most = [color for color, count in color_counts.items() if count == most_count]
        least = [color for color, count in color_counts.items() if count == least_count]
        most_color = most[0] if len(most) == 1 else None
        least_color = least[0] if len(least) == 1 else None
    rarest_prototype: Component | None = None
    if least_color is not None:
        rarest_components = [item for item in components if item.color == least_color]
        if len(rarest_components) == 1:
            rarest_prototype = rarest_components[0]
    for index, component in enumerate(components):
        support = support_components[cell_support[min(component.cells)]]
        support_members = {
            cell_component[cell] for cell in support.cells if cell in cell_component
        }
        support_colors = {components[item].color for item in support_members}
        others = [
            (_component_distance(component, other), other_index, other)
            for other_index, other in enumerate(components)
            if other_index != index
        ]
        nearest = min((item[0] for item in others), default=-1)
        nearest_items = [item for item in others if item[0] == nearest]
        different = [item for item in others if item[2].color != component.color]
        nearest_different = min((item[0] for item in different), default=-1)
        nearest_different_items = [item for item in different if item[0] == nearest_different]

        def unique_color(items: Sequence[Component]) -> int | None:
            colors = {item.color for item in items}
            return next(iter(colors)) if len(colors) == 1 else None

        def unique_relation(items: Sequence[tuple[int, int, Component]]) -> Any:
            relations = {_relation(component, item[2], item[0]) for item in items}
            return next(iter(relations)) if len(relations) == 1 else ("ambiguous", len(items))

        turn_count = _turn_count(component)

        features.append(
            {
                "mono_area": component.area,
                "mono_bbox": tuple(sorted((component.height, component.width))),
                "mono_density": (component.density.numerator, component.density.denominator),
                "mono_holes": component.holes,
                "mono_perimeter": component.perimeter,
                "mono_degree_histogram": component.degree_histogram,
                "mono_endpoint_count": component.degree_histogram[1],
                "mono_junction_count": sum(component.degree_histogram[3:]),
                "mono_turn_count": turn_count,
                "mono_symmetry_order": component.symmetry_order,
                "mono_area_role": _rank_role(areas, component.area),
                "mono_same_color_area_role": _rank_role(
                    [item.area for item in components if item.color == component.color], component.area
                ),
                "mono_topology_peer_count": topology_counts[component.topology],
                "d4_shape_peer_count": shape_counts[component.d4_shape],
                "d4_shape_other_color_peer_count": sum(
                    item.d4_shape == component.d4_shape and item.color != component.color
                    for item in components
                ),
                "matches_rarest_graph_prototype": int(
                    rarest_prototype is not None
                    and _graph_class(component) == _graph_class(rarest_prototype)
                ),
                "matches_rarest_d4_prototype": int(
                    rarest_prototype is not None
                    and component.d4_shape == rarest_prototype.d4_shape
                ),
                "color_frequency_role": _rank_role(list(color_counts.values()), color_counts[component.color]),
                "color_component_role": _rank_role(
                    list(color_component_counts.values()), color_component_counts[component.color]
                ),
                "nearest_component_distance": nearest,
                "nearest_component_relation": unique_relation(nearest_items),
                "nearest_different_relation": unique_relation(nearest_different_items),
                "support_area": support.area,
                "support_bbox": tuple(sorted((support.height, support.width))),
                "support_mono_count": len(support_members),
                "support_color_count": len(support_colors),
                "support_holes": support.holes,
            }
        )
        action_values.append(
            {
                "most_frequent_foreground": most_color,
                "least_frequent_foreground": least_color,
                "nearest_component_color": unique_color([item[2] for item in nearest_items]),
                "nearest_different_color": unique_color(
                    [item[2] for item in nearest_different_items]
                ),
                "topology_peer_color": unique_color(
                    [
                        item
                        for other_index, item in enumerate(components)
                        if other_index != index and item.topology == component.topology
                    ]
                ),
                "d4_shape_peer_color": unique_color(
                    [
                        item
                        for other_index, item in enumerate(components)
                        if other_index != index and item.d4_shape == component.d4_shape
                    ]
                ),
                "area_peer_color": unique_color(
                    [
                        item
                        for other_index, item in enumerate(components)
                        if other_index != index and item.area == component.area
                    ]
                ),
                "support_unique_other_color": (
                    next(iter(support_colors - {component.color}))
                    if len(support_colors - {component.color}) == 1
                    else None
                ),
            }
        )
    return Scene(
        grid=value,
        background=background,
        background_tied=tied,
        components=components,
        support_components=support_components,
        cell_component=cell_component,
        cell_support=cell_support,
        component_features=tuple(features),
        component_action_values=tuple(action_values),
        color_counts=color_counts,
    )


def _canonical_local_mask(scene: Scene, cell: Cell, *, same_only: bool) -> int:
    row, column = cell
    source = scene.grid[row][column]
    points: set[Cell] = set()
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            rr, cc = row + dr, column + dc
            if not (0 <= rr < len(scene.grid) and 0 <= cc < len(scene.grid[0])):
                continue
            value = scene.grid[rr][cc]
            active = value == source if same_only else value != scene.background
            if active:
                points.add((dr + 1, dc + 1))
    masks: list[int] = []
    for transformed in _d4_point_sets(frozenset(points)):
        masks.append(sum(1 << (3 * rr + cc) for rr, cc in transformed))
    return min(masks)


def _degree(scene: Scene, cell: Cell, connectivity: int, *, same_only: bool) -> int:
    source = scene.grid[cell[0]][cell[1]]
    return sum(
        0 <= row < len(scene.grid)
        and 0 <= column < len(scene.grid[0])
        and scene.grid[row][column] != scene.background
        and (not same_only or scene.grid[row][column] == source)
        for row, column in _neighbors(cell, connectivity)
    )


def _ray_distances(scene: Scene, cell: Cell) -> tuple[int, ...]:
    height, width = _shape(scene.grid)
    distances: list[int] = []
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        distance = 1
        row, column = cell[0] + dr, cell[1] + dc
        while 0 <= row < height and 0 <= column < width:
            if scene.grid[row][column] != scene.background:
                break
            distance += 1
            row += dr
            column += dc
        distances.append(distance if 0 <= row < height and 0 <= column < width else 0)
    return tuple(sorted(distances))


def _features(scene: Scene, entity: Entity, granularity: str) -> dict[str, Any]:
    base = dict(scene.component_features[entity.component_index])
    if granularity == "component4":
        return base
    if granularity != "pixel" or entity.pixel is None:
        raise Undefined("invalid granularity")
    row, column = entity.pixel
    component = scene.components[entity.component_index]
    source = scene.grid[row][column]
    top, bottom, left, right = component.bbox
    orthogonal = _neighbors((row, column), 4)
    diagonal = tuple(point for point in _neighbors((row, column), 8) if point not in orthogonal)

    def neighbor_counts(points: Sequence[Cell]) -> tuple[int, int, int]:
        same = different = background = 0
        for rr, cc in points:
            if not (0 <= rr < len(scene.grid) and 0 <= cc < len(scene.grid[0])):
                background += 1
            elif scene.grid[rr][cc] == scene.background:
                background += 1
            elif scene.grid[rr][cc] == source:
                same += 1
            else:
                different += 1
        return same, different, background

    row_same = sum(value == source for value in scene.grid[row])
    column_same = sum(scene.grid[rr][column] == source for rr in range(len(scene.grid)))
    row_support = sum(value != scene.background for value in scene.grid[row])
    column_support = sum(
        scene.grid[rr][column] != scene.background for rr in range(len(scene.grid))
    )
    other_color_cells = [
        (rr, cc)
        for rr, values in enumerate(scene.grid)
        for cc, value in enumerate(values)
        if value != scene.background and value != source
    ]
    base.update(
        {
            "same_degree4": _degree(scene, (row, column), 4, same_only=True),
            "same_degree8": _degree(scene, (row, column), 8, same_only=True),
            "support_degree4": _degree(scene, (row, column), 4, same_only=False),
            "support_degree8": _degree(scene, (row, column), 8, same_only=False),
            "neighbor_profile": tuple(sorted((neighbor_counts(orthogonal), neighbor_counts(diagonal)))),
            "local_same_topology": _canonical_local_mask(scene, (row, column), same_only=True),
            "local_support_topology": _canonical_local_mask(scene, (row, column), same_only=False),
            "bbox_distance_role": tuple(sorted((row - top, bottom - row, column - left, right - column))),
            "center_distance_role": tuple(
                sorted((abs(2 * row - top - bottom), abs(2 * column - left - right)))
            ),
            "row_column_same_role": tuple(sorted((row_same, column_same))),
            "row_column_support_role": tuple(sorted((row_support, column_support))),
            "nearest_other_color_distance": min(
                (abs(row - rr) + abs(column - cc) for rr, cc in other_color_cells),
                default=-1,
            ),
            "ray_foreground_role": _ray_distances(scene, (row, column)),
        }
    )
    return base


def _entities(scene: Scene, granularity: str) -> tuple[Entity, ...]:
    if granularity == "component4":
        return tuple(
            Entity(index, tuple(sorted(component.cells)), None)
            for index, component in enumerate(scene.components)
        )
    if granularity == "pixel":
        return tuple(
            Entity(index, (cell,), cell)
            for index, component in enumerate(scene.components)
            for cell in sorted(component.cells)
        )
    raise Undefined("unknown granularity")


def _entity_source(scene: Scene, entity: Entity) -> int:
    row, column = entity.cells[0]
    return scene.grid[row][column]


def _entity_target(target: Grid, entity: Entity) -> int:
    values = {target[row][column] for row, column in entity.cells}
    if len(values) != 1:
        raise Undefined("component output is not uniform")
    return next(iter(values))


def _observations(
    scenes: Sequence[Scene], targets: Sequence[Grid], granularity: str, limits: Limits
) -> tuple[Observation, ...]:
    result: list[Observation] = []
    for demo, (scene, target) in enumerate(zip(scenes, targets)):
        for entity in _entities(scene, granularity):
            source = _entity_source(scene, entity)
            action_values: dict[str, int | None] = {}
            for action in _action_pool():
                try:
                    action_values[_canonical(action)] = _resolve_action(action, scene, entity)
                except (KeyError, TypeError, ValueError, IndexError):
                    action_values[_canonical(action)] = None
            result.append(
                Observation(
                    demo=demo,
                    scene=scene,
                    entity=entity,
                    source=source,
                    target=_entity_target(target, entity),
                    features=_features(scene, entity, granularity),
                    action_values=action_values,
                )
            )
            if len(result) > limits.max_entities:
                raise Undefined("entity bound exhausted")
    return tuple(result)


def _unique_frequency_color(scene: Scene, *, largest: bool) -> int:
    if not scene.color_counts:
        raise Undefined("foreground palette is empty")
    desired = max(scene.color_counts.values()) if largest else min(scene.color_counts.values())
    winners = [color for color, count in scene.color_counts.items() if count == desired]
    if len(winners) != 1:
        raise Undefined("frequency role is tied")
    return winners[0]


def _related_components(scene: Scene, entity: Entity, kind: str) -> list[Component]:
    source = scene.components[entity.component_index]
    others = [
        component
        for index, component in enumerate(scene.components)
        if index != entity.component_index
    ]
    if kind == "nearest_component_color":
        if not others:
            return []
        distance = min(_component_distance(source, other) for other in others)
        return [other for other in others if _component_distance(source, other) == distance]
    if kind == "nearest_different_color":
        others = [other for other in others if other.color != source.color]
        if not others:
            return []
        distance = min(_component_distance(source, other) for other in others)
        return [other for other in others if _component_distance(source, other) == distance]
    if kind == "topology_peer_color":
        return [other for other in others if other.topology == source.topology]
    if kind == "area_peer_color":
        return [other for other in others if other.area == source.area]
    raise Undefined("unknown relation action")


def _resolve_action(action: Mapping[str, Any], scene: Scene, entity: Entity) -> int:
    kind = str(action.get("kind"))
    if kind == "literal":
        color = int(action["color"])
        if not 0 <= color <= 9:
            raise Undefined("literal color outside ARC palette")
        return color
    if kind in {
        "most_frequent_foreground", "least_frequent_foreground",
        "nearest_component_color", "nearest_different_color",
        "topology_peer_color", "d4_shape_peer_color", "area_peer_color",
        "support_unique_other_color",
    }:
        color = scene.component_action_values[entity.component_index].get(kind)
        if color is None:
            raise Undefined("relational color role is ambiguous")
        return color
    raise Undefined("unknown action")


def _action_cost(action: Mapping[str, Any]) -> int:
    kind = str(action["kind"])
    if kind in {"most_frequent_foreground", "least_frequent_foreground"}:
        return 1
    if kind == "literal":
        return 3
    return 2


def _action_pool() -> tuple[dict[str, Any], ...]:
    actions = [
        {"kind": "most_frequent_foreground"},
        {"kind": "least_frequent_foreground"},
        {"kind": "nearest_component_color"},
        {"kind": "nearest_different_color"},
        {"kind": "topology_peer_color"},
        {"kind": "d4_shape_peer_color"},
        {"kind": "area_peer_color"},
        {"kind": "support_unique_other_color"},
    ]
    actions.extend({"kind": "literal", "color": color} for color in range(10))
    return tuple(sorted(actions, key=lambda action: (_action_cost(action), _canonical(action))))


def _feature_key(observation: Observation, names: Sequence[str]) -> str:
    return _canonical([_jsonable(observation.features[name]) for name in names])


def _fit_rule_sets(
    observations: Sequence[Observation],
    feature_names: Sequence[str],
    limits: Limits,
    *,
    minimum_witnesses: int,
) -> tuple[tuple[dict[str, Any], ...], ...]:
    groups: dict[str, list[Observation]] = {}
    for observation in observations:
        groups.setdefault(_feature_key(observation, feature_names), []).append(observation)
    choices: list[tuple[str, list[dict[str, Any]], int]] = []
    for key in sorted(groups):
        group = groups[key]
        changed = [item for item in group if item.source != item.target]
        if not changed:
            continue
        witnesses = len({item.demo for item in changed})
        if witnesses < minimum_witnesses:
            return ()
        compatible: list[dict[str, Any]] = []
        for action in _action_pool():
            action_key = _canonical(action)
            if all(item.action_values.get(action_key) == item.target for item in group):
                compatible.append(action)
        if not compatible:
            return ()
        best_cost = min(_action_cost(action) for action in compatible)
        compatible = [action for action in compatible if _action_cost(action) == best_cost]
        choices.append((key, compatible, witnesses))
    if not choices:
        return ()
    product_size = 1
    for _, actions, _ in choices:
        product_size *= len(actions)
        if product_size > limits.max_action_products:
            raise Undefined("action ambiguity bound exhausted")
    result: list[tuple[dict[str, Any], ...]] = []
    for product in itertools.product(*(actions for _, actions, _ in choices)):
        rules = tuple(
            {
                "key": json.loads(key),
                "action": dict(action),
                "changed_demo_witnesses": witnesses,
            }
            for (key, _, witnesses), action in zip(choices, product)
        )
        result.append(rules)
    return tuple(result)


def _rule_map(rules: Sequence[Mapping[str, Any]]) -> dict[str, Mapping[str, Any]]:
    result: dict[str, Mapping[str, Any]] = {}
    for rule in rules:
        key = _canonical(rule["key"])
        if key in result:
            raise Undefined("duplicate rule key")
        result[key] = rule["action"]
    return result


def _execute_scene(program: Mapping[str, Any], scene: Scene) -> Grid:
    if program.get("schema") != SCHEMA or program.get("operator") != "contextual_feature_recolor":
        raise Undefined("unknown contextual recolor program")
    granularity = str(program["granularity"])
    features = tuple(str(name) for name in program["features"])
    costs = COMPONENT_FEATURE_COSTS if granularity == "component4" else PIXEL_FEATURE_COSTS
    if not features or len(features) > 3 or any(name not in costs for name in features):
        raise Undefined("feature program outside grammar")
    rules = _rule_map(program["rules"])
    output = [list(row) for row in scene.grid]
    for entity in _entities(scene, granularity):
        feature_values = _features(scene, entity, granularity)
        key = _canonical([_jsonable(feature_values[name]) for name in features])
        action = rules.get(key)
        if action is None:
            continue
        color = _resolve_action(action, scene, entity)
        for row, column in entity.cells:
            output[row][column] = color
    return tuple(tuple(row) for row in output)


def replay_program(program: Mapping[str, Any], grid: Any) -> list[list[int]]:
    """Replay one serialized contextual rule program on a grid."""

    value = _grid(grid)
    return _plain(_execute_scene(program, _scene(value)))


def _program(
    granularity: str,
    feature_names: Sequence[str],
    rules: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "operator": "contextual_feature_recolor",
        "role_scope": "immutable_root_input",
        "background_role": "border_frequency_mode_min_tie_normal_form",
        "granularity": granularity,
        "features": list(feature_names),
        "rules": [dict(rule) for rule in rules],
        "default_action": "identity",
    }


def _predict_observations(
    rules: Sequence[Mapping[str, Any]],
    feature_names: Sequence[str],
    observations: Sequence[Observation],
) -> tuple[int, ...]:
    mapping = _rule_map(rules)
    result: list[int] = []
    for observation in observations:
        action = mapping.get(_feature_key(observation, feature_names))
        if action is None:
            result.append(observation.source)
        else:
            result.append(_resolve_action(action, observation.scene, observation.entity))
    return tuple(result)


def _loo_exact(
    observations: Sequence[Observation],
    feature_names: Sequence[str],
    demo_count: int,
    limits: Limits,
) -> bool:
    for held_out in range(demo_count):
        retained = [item for item in observations if item.demo != held_out]
        held = [item for item in observations if item.demo == held_out]
        try:
            alternatives = _fit_rule_sets(
                retained, feature_names, limits, minimum_witnesses=1
            )
        except Undefined:
            return False
        if not alternatives:
            return False
        expected = tuple(item.target for item in held)
        try:
            forecasts = {
                _predict_observations(rules, feature_names, held)
                for rules in alternatives
            }
        except (KeyError, TypeError, ValueError, IndexError):
            return False
        if forecasts != {expected}:
            return False
    return True


def _d4(value: Grid, operation: str) -> Grid:
    if operation == "flip_h":
        return tuple(tuple(reversed(row)) for row in value)
    if operation == "rot90":
        return tuple(
            tuple(value[len(value) - 1 - row][column] for row in range(len(value)))
            for column in range(len(value[0]))
        )
    raise Undefined("unknown D4 operation")


def _pad(value: Grid, color: int) -> Grid:
    width = len(value[0]) + 2
    blank = (color,) * width
    return (blank,) + tuple((color,) + row + (color,) for row in value) + (blank,)


def _counterfactual_exact(
    program: Mapping[str, Any],
    train: Sequence[tuple[Grid, Grid]],
) -> tuple[tuple[str, ...], int] | None:
    probes = 0
    for source, target in train:
        for operation in ("flip_h", "rot90"):
            try:
                actual = _execute_scene(program, _scene(_d4(source, operation)))
            except (KeyError, TypeError, ValueError, IndexError):
                return None
            if actual != _d4(target, operation):
                return None
            probes += 1
        background, _ = _background(source)
        if max(len(source), len(source[0])) < 30:
            try:
                actual = _execute_scene(program, _scene(_pad(source, background)))
            except (KeyError, TypeError, ValueError, IndexError):
                return None
            if actual != _pad(target, background):
                return None
            probes += 1
    return ("d4_covariance", "background_padding_translation"), probes


def _feature_set_candidates(names: Sequence[str], limits: Limits) -> Iterable[tuple[str, ...]]:
    count = 0
    for depth in range(1, limits.max_feature_depth + 1):
        for combination in itertools.combinations(names, depth):
            count += 1
            if count > limits.max_feature_sets:
                raise Undefined("feature-set bound exhausted")
            yield combination


def _model_complexity(
    granularity: str,
    feature_names: Sequence[str],
    rules: Sequence[Mapping[str, Any]],
) -> int:
    costs = COMPONENT_FEATURE_COSTS if granularity == "component4" else PIXEL_FEATURE_COSTS
    return (
        4
        + (0 if granularity == "component4" else 2)
        + sum(costs[name] for name in feature_names)
        + 2 * len(rules)
        + sum(_action_cost(rule["action"]) for rule in rules)
    )


def _same_footprint_contextual(train: Sequence[tuple[Grid, Grid]]) -> bool:
    contextual = False
    for source, target in train:
        if _shape(source) != _shape(target) or source == target:
            return False
        background, _ = _background(source)
        mapping: dict[int, int] = {}
        local_contextual = False
        for source_row, target_row in zip(source, target):
            for before, after in zip(source_row, target_row):
                if (before == background) != (after == background):
                    return False
                if before in mapping and mapping[before] != after:
                    local_contextual = True
                mapping.setdefault(before, after)
        contextual |= local_contextual
    return contextual


def _behavior_hash(outputs: Sequence[Grid]) -> str:
    return hashlib.sha256(_canonical([_plain(output) for output in outputs]).encode("utf-8")).hexdigest()


def _domain_covers_tests(
    feature_names: Sequence[str],
    observations: Sequence[Observation],
    test_scenes: Sequence[Scene],
    granularity: str,
) -> bool:
    witnessed = {_feature_key(observation, feature_names) for observation in observations}
    for scene in test_scenes:
        for entity in _entities(scene, granularity):
            values = _features(scene, entity, granularity)
            key = _canonical([_jsonable(values[name]) for name in feature_names])
            if key not in witnessed:
                return False
    return True


def compile_task(task: Any, limits: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    """Compile at most one guarded contextual recolor candidate."""

    try:
        bounds = Limits.from_value(limits)
        if not isinstance(task, Mapping):
            return []
        raw_train, raw_test = task["train"], task["test"]
        if (
            not isinstance(raw_train, Sequence)
            or isinstance(raw_train, (str, bytes, bytearray))
            or len(raw_train) < 2
            or not isinstance(raw_test, Sequence)
            or isinstance(raw_test, (str, bytes, bytearray))
            or not raw_test
            or len(raw_train) + len(raw_test) > bounds.max_examples
        ):
            return []
        train = tuple(
            (_grid(example["input"], bounds), _grid(example["output"], bounds))
            for example in raw_train
        )
        # Deliberately observe exactly one member of every test record.
        tests = tuple(_grid(example["input"], bounds) for example in raw_test)
        if not _same_footprint_contextual(train):
            return []
        scenes = tuple(_scene(source) for source, _ in train)
        targets = tuple(target for _, target in train)
        test_scenes = tuple(_scene(source) for source in tests)
        raw_best: int | None = None
        raw_models: dict[str, tuple[int, dict[str, Any], tuple[Observation, ...]]] = {}
        for granularity, feature_costs in (
            ("component4", COMPONENT_FEATURE_COSTS),
            ("pixel", PIXEL_FEATURE_COSTS),
        ):
            if granularity == "pixel" and raw_models:
                # Whole-component explanations are the more abstract grammar
                # phase.  Pixel masks are searched only when no component
                # program survives exact replay and LOO induction.
                break
            try:
                observations = _observations(scenes, targets, granularity, bounds)
            except Undefined:
                continue
            names = tuple(sorted(feature_costs, key=lambda name: (feature_costs[name], name)))
            exact_feature_sets: list[frozenset[str]] = []
            for feature_names in _feature_set_candidates(names, bounds):
                feature_name_set = frozenset(feature_names)
                # The grammar is irredundant: once a feature subset already
                # separates every required action, refinements of that same
                # partition are excluded rather than treated as new programs.
                if any(prior < feature_name_set for prior in exact_feature_sets):
                    continue
                try:
                    rule_sets = _fit_rule_sets(
                        observations,
                        feature_names,
                        bounds,
                        minimum_witnesses=bounds.min_rule_demo_witnesses,
                    )
                except Undefined:
                    return []
                if not rule_sets:
                    continue
                exact_feature_sets.append(feature_name_set)
                if not _loo_exact(observations, feature_names, len(train), bounds):
                    continue
                for rules in rule_sets:
                    program = _program(granularity, feature_names, rules)
                    complexity = _model_complexity(granularity, feature_names, rules)
                    if raw_best is None or complexity < raw_best:
                        raw_best = complexity
                        raw_models = {
                            key: item
                            for key, item in raw_models.items()
                            if item[0] <= complexity + bounds.ambiguity_slack
                        }
                    if complexity <= raw_best + bounds.ambiguity_slack:
                        raw_models.setdefault(
                            _canonical(program), (complexity, program, observations)
                        )
                    if len(raw_models) > bounds.max_models:
                        return []
        if not raw_models:
            return []
        proposals: list[
            tuple[int, str, dict[str, Any], tuple[Grid, ...], tuple[str, ...], int]
        ] = []
        for complexity, program, observations in sorted(
            raw_models.values(), key=lambda item: (item[0], _canonical(item[1]))
        ):
            granularity = str(program["granularity"])
            feature_names = tuple(str(name) for name in program["features"])
            if not _domain_covers_tests(
                feature_names, observations, test_scenes, granularity
            ):
                # An equally simple but out-of-domain explanation is evidence
                # of underdetermination, not permission to ignore it.
                return []
            try:
                replay = tuple(_execute_scene(program, scene) for scene in scenes)
                forecasts = tuple(_execute_scene(program, scene) for scene in test_scenes)
            except (KeyError, TypeError, ValueError, IndexError):
                return []
            if replay != targets:
                return []
            certificate = _counterfactual_exact(program, train)
            if certificate is None:
                return []
            if all(output == source for output, source in zip(forecasts, tests)):
                return []
            proposals.append(
                (
                    complexity,
                    _canonical(program),
                    program,
                    forecasts,
                    certificate[0],
                    certificate[1],
                )
            )
        if not proposals:
            return []
        proposals.sort(key=lambda item: (item[0], item[1]))
        minimum = proposals[0][0]
        near = [item for item in proposals if item[0] <= minimum + bounds.ambiguity_slack]
        behaviors = {_behavior_hash(item[3]) for item in near}
        if len(behaviors) != 1:
            return []
        best = proposals[0]
        equivalent_minimum = sum(item[0] == minimum for item in proposals)
        candidate = {
            "family": "contextual_recolor_induction",
            "program": best[2],
            "train_outputs": [_plain(target) for target in targets],
            "test_outputs": [_plain(output) for output in best[3]],
            "complexity": best[0],
            "evidence": {
                "author": AUTHOR,
                "all_demonstrations_exact": True,
                "same_footprint_contextual_gate": True,
                "leave_one_demonstration_out_exact": True,
                "demonstration_permutation_invariant": True,
                "counterfactual_families": list(best[4]),
                "counterfactual_probe_count": best[5],
                "minimum_equivalent_programs": equivalent_minimum,
                "near_mdl_programs": len(near),
                "near_mdl_behavior_agreement": True,
                "ambiguity_abstention": True,
                "behavior_hash": _behavior_hash(best[3]),
            },
        }
        return [candidate][: bounds.max_candidates]
    except (KeyError, TypeError, ValueError, IndexError, ZeroDivisionError):
        return []


__all__ = ["Limits", "compile_task", "replay_program"]
