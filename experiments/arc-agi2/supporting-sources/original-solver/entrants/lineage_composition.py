"""Label-blind lineage composition entrant for Block 15.

The entrant compiles two generic, two-stage object programs:

``classify -> dock -> recolor``
    Persistent shapes are classified by whether their bounding-box complement
    is solid/enclosed or purely open.  The two roles dock to opposite horizontal
    borders and receive demonstration-derived colors.

``match -> translate -> recolor``
    External inventory pieces retain their exact cell ancestry while a unique
    bounded exact-cover search translates them into a scaffold's cavities.

Programs contain no task identifiers, absolute held-out coordinates, cached
test rasters, or solution references.  Compilation reads labelled
demonstrations and test inputs only.  Every candidate exactly replays all
demonstrations, survives genuine leave-one-demonstration-out re-induction,
passes palette-transport counterfactuals, has one supported held-out behavior,
and exposes deterministic replay stages.

Author: Komorebi P.
"""

from __future__ import annotations

from collections import Counter, deque
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
import hashlib
import json
from typing import Any


Grid = tuple[tuple[int, ...], ...]
Cell = tuple[int, int]
Pair = tuple[Grid, Grid]
AUTHOR = "Komorebi P."
SCHEMA = "komorebi.pr_lasm.block15.lineage_composition.program.v1"
MAX_SIDE = 30


class Undefined(ValueError):
    """A role, program, placement, or unique behavior is unsupported."""


@dataclass(frozen=True, slots=True)
class Limits:
    max_side: int = MAX_SIDE
    max_examples: int = 20
    max_executor_calls: int = 4096
    max_search_nodes: int = 200_000
    max_candidates: int = 1

    @classmethod
    def from_value(cls, value: Any) -> "Limits":
        if value is None:
            return cls()
        if isinstance(value, cls):
            return value
        if not isinstance(value, Mapping):
            raise Undefined("limits must be a mapping")
        defaults = cls()
        raw_candidates = value.get("candidate_cap", value.get("max_candidates", 1))

        def bounded(name: str, default: int, ceiling: int) -> int:
            raw = value.get(name, default)
            if isinstance(raw, bool) or not isinstance(raw, int) or raw < 1:
                raise Undefined(f"{name} must be a positive integer")
            return min(raw, ceiling)

        if (
            isinstance(raw_candidates, bool)
            or not isinstance(raw_candidates, int)
            or raw_candidates < 1
        ):
            raise Undefined("candidate cap must be positive")
        return cls(
            max_side=bounded("max_side", defaults.max_side, MAX_SIDE),
            max_examples=bounded("max_examples", defaults.max_examples, 40),
            max_executor_calls=bounded(
                "max_executor_calls", defaults.max_executor_calls, 100_000
            ),
            max_search_nodes=bounded(
                "max_search_nodes", defaults.max_search_nodes, 2_000_000
            ),
            max_candidates=min(raw_candidates, 1),
        )


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


def _grid(value: Any, max_side: int = MAX_SIDE) -> Grid:
    if (
        not isinstance(value, Sequence)
        or isinstance(value, (str, bytes, bytearray))
        or not value
        or len(value) > max_side
    ):
        raise Undefined("grid has invalid height")
    rows: list[tuple[int, ...]] = []
    width: int | None = None
    for raw_row in value:
        if (
            not isinstance(raw_row, Sequence)
            or isinstance(raw_row, (str, bytes, bytearray))
            or not raw_row
            or len(raw_row) > max_side
        ):
            raise Undefined("grid row is invalid")
        row: list[int] = []
        for cell in raw_row:
            if isinstance(cell, bool) or not isinstance(cell, int) or not 0 <= cell <= 9:
                raise Undefined("ARC colors must be integers in [0, 9]")
            row.append(int(cell))
        if width is None:
            width = len(row)
        elif len(row) != width:
            raise Undefined("grid is ragged")
        rows.append(tuple(row))
    return tuple(rows)


def _plain(grid: Grid) -> list[list[int]]:
    return [list(row) for row in grid]


def _shape(grid: Grid) -> tuple[int, int]:
    return len(grid), len(grid[0])


def _sanitize(task: Any, limits: Limits) -> tuple[tuple[Pair, ...], tuple[Grid, ...]]:
    if not isinstance(task, Mapping):
        raise Undefined("task must be a mapping")
    train, tests = task.get("train"), task.get("test")
    if (
        not isinstance(train, Sequence)
        or isinstance(train, (str, bytes, bytearray))
        or len(train) < 2
        or not isinstance(tests, Sequence)
        or isinstance(tests, (str, bytes, bytearray))
        or not tests
        or len(train) + len(tests) > limits.max_examples
    ):
        raise Undefined("task needs at least two demonstrations and one test input")
    pairs: list[Pair] = []
    test_inputs: list[Grid] = []
    for index, example in enumerate(train):
        if not isinstance(example, Mapping):
            raise Undefined(f"train[{index}] is invalid")
        pairs.append(
            (
                _grid(example.get("input"), limits.max_side),
                _grid(example.get("output"), limits.max_side),
            )
        )
    for index, example in enumerate(tests):
        if not isinstance(example, Mapping):
            raise Undefined(f"test[{index}] is invalid")
        # Deliberately fetch only the held-out input member.
        test_inputs.append(_grid(example.get("input"), limits.max_side))
    return tuple(pairs), tuple(test_inputs)


def _mode(grid: Grid) -> int:
    counts = Counter(cell for row in grid for cell in row)
    peak = max(counts.values())
    winners = sorted(color for color, count in counts.items() if count == peak)
    if len(winners) != 1:
        raise Undefined("background mode is ambiguous")
    return winners[0]


def _palette(grid: Grid) -> frozenset[int]:
    return frozenset(cell for row in grid for cell in row)


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


@dataclass(frozen=True, slots=True)
class Component:
    color: int
    cells: frozenset[Cell]

    @property
    def bbox(self) -> tuple[int, int, int, int]:
        return _bbox(self.cells)

    @property
    def area(self) -> int:
        return len(self.cells)

    @property
    def normalized(self) -> tuple[Cell, ...]:
        row0, _, column0, _ = self.bbox
        return tuple(sorted((row - row0, column - column0) for row, column in self.cells))

    @property
    def signature(self) -> str:
        return _digest({"normalized_cells": [list(cell) for cell in self.normalized]})


def _components(grid: Grid, *, include_colors: Iterable[int]) -> tuple[Component, ...]:
    allowed = frozenset(include_colors)
    height, width = _shape(grid)
    remaining = {
        (row, column)
        for row in range(height)
        for column in range(width)
        if grid[row][column] in allowed
    }
    result: list[Component] = []
    while remaining:
        seed = min(remaining)
        color = grid[seed[0]][seed[1]]
        remaining.remove(seed)
        queue = deque([seed])
        cells = {seed}
        while queue:
            row, column = queue.popleft()
            for row_delta, column_delta in ((-1, 0), (0, -1), (0, 1), (1, 0)):
                neighbor = row + row_delta, column + column_delta
                if neighbor in remaining and grid[neighbor[0]][neighbor[1]] == color:
                    remaining.remove(neighbor)
                    cells.add(neighbor)
                    queue.append(neighbor)
        result.append(Component(color, frozenset(cells)))
    return tuple(sorted(result, key=lambda item: (item.bbox, item.color, item.signature)))


def _root_pixel_id(root_hash: str, grid: Grid, cell: Cell) -> str:
    row, column = cell
    return _digest(
        {
            "kind": "root_pixel",
            "root_hash": root_hash,
            "coordinate": [row, column],
            "color": grid[row][column],
        }
    )


def _entity_record(root_hash: str, grid: Grid, component: Component) -> dict[str, Any]:
    root_ids = tuple(
        _root_pixel_id(root_hash, grid, cell) for cell in sorted(component.cells)
    )
    entity_id = _digest(
        {
            "kind": "persistent_entity",
            "root_hash": root_hash,
            "root_pixel_ids": list(root_ids),
        }
    )
    return {
        "entity_id": entity_id,
        "source_bbox": list(component.bbox),
        "area": component.area,
        "color": component.color,
        "shape_signature": component.signature,
        "root_pixel_ids": list(root_ids),
    }


def _has_enclosed_void_or_is_solid(normalized: Sequence[Cell]) -> bool:
    support = set(normalized)
    if not support:
        raise Undefined("empty shape")
    height = max(row for row, _ in support) + 1
    width = max(column for _, column in support) + 1
    remaining = {
        (row, column)
        for row in range(height)
        for column in range(width)
        if (row, column) not in support
    }
    if not remaining:
        return True
    while remaining:
        seed = min(remaining)
        remaining.remove(seed)
        queue = deque([seed])
        region = {seed}
        while queue:
            row, column = queue.popleft()
            for row_delta, column_delta in ((-1, 0), (0, -1), (0, 1), (1, 0)):
                neighbor = row + row_delta, column + column_delta
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    region.add(neighbor)
                    queue.append(neighbor)
        if all(
            row not in (0, height - 1) and column not in (0, width - 1)
            for row, column in region
        ):
            return True
    return False


def _require_color_field(program: Mapping[str, Any], name: str) -> int:
    value = program.get(name)
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 9:
        raise Undefined(f"invalid program color {name}")
    return value


def _dock_execute(program: Mapping[str, Any], grid: Grid) -> tuple[Grid, dict[str, Any]]:
    background = _require_color_field(program, "background_color")
    source_color = _require_color_field(program, "source_color")
    closed_color = _require_color_field(program, "closed_color")
    open_color = _require_color_field(program, "open_color")
    if len({background, source_color, closed_color, open_color}) != 4:
        raise Undefined("dock roles must use distinct colors")
    if _palette(grid) != frozenset((background, source_color)):
        raise Undefined("dock input palette violates the learned roles")
    components = _components(grid, include_colors=(source_color,))
    if len(components) < 2 or len({item.signature for item in components}) != len(components):
        raise Undefined("dock input needs distinct persistent shapes")
    height, width = _shape(grid)
    result = [[background for _ in range(width)] for _ in range(height)]
    root_hash = _digest({"schema": f"{SCHEMA}.root", "grid": _plain(grid)})
    placements: list[dict[str, Any]] = []
    branch_counts = {"closed": 0, "open": 0}
    occupied: set[Cell] = set()
    for component in components:
        row0, row1, column0, column1 = component.bbox
        object_width = column1 - column0 + 1
        closed = _has_enclosed_void_or_is_solid(component.normalized)
        role = "closed" if closed else "open"
        branch_counts[role] += 1
        target_column = 0 if closed else width - object_width
        if target_column == column0:
            raise Undefined("dock transition must move every persistent shape")
        delta = 0, target_column - column0
        target_cells = frozenset(
            (row + delta[0], column + delta[1]) for row, column in component.cells
        )
        if target_cells & occupied:
            raise Undefined("dock placements collide")
        if any(not 0 <= row < height or not 0 <= column < width for row, column in target_cells):
            raise Undefined("dock placement leaves the canvas")
        occupied |= target_cells
        output_color = closed_color if closed else open_color
        for row, column in target_cells:
            result[row][column] = output_color
        entity = _entity_record(root_hash, grid, component)
        placements.append(
            {
                **entity,
                "role": role,
                "delta": list(delta),
                "target_bbox": list(_bbox(target_cells)),
                "target_cells": [list(cell) for cell in sorted(target_cells)],
                "output_color": output_color,
            }
        )
    if set(branch_counts.values()) & {0}:
        raise Undefined("dock test does not exercise both supported role branches")
    output = tuple(tuple(row) for row in result)
    return output, {
        "root_hash": root_hash,
        "operator": "dock_closed_open_horizontal",
        "classification": "solid_or_enclosed_void_vs_open_complement",
        "branch_counts": branch_counts,
        "entities": placements,
        "output_hash": _digest(_plain(output)),
    }


def _match_unique_shapes(
    source: Sequence[Component], target: Sequence[Component]
) -> tuple[tuple[Component, Component], ...]:
    source_by_signature: dict[str, list[Component]] = {}
    target_by_signature: dict[str, list[Component]] = {}
    for item in source:
        source_by_signature.setdefault(item.signature, []).append(item)
    for item in target:
        target_by_signature.setdefault(item.signature, []).append(item)
    if set(source_by_signature) != set(target_by_signature):
        raise Undefined("source and target shape inventories differ")
    matches: list[tuple[Component, Component]] = []
    for signature in sorted(source_by_signature):
        left, right = source_by_signature[signature], target_by_signature[signature]
        if len(left) != 1 or len(right) != 1:
            raise Undefined("shape identity is ambiguous")
        matches.append((left[0], right[0]))
    return tuple(matches)


def _infer_dock_program(pairs: Sequence[Pair]) -> dict[str, Any]:
    parameter_sets: set[tuple[int, int, int, int]] = set()
    for source_grid, target_grid in pairs:
        if _shape(source_grid) != _shape(target_grid):
            raise Undefined("dock preserves canvas shape")
        background = _mode(source_grid)
        if _mode(target_grid) != background:
            raise Undefined("dock background changed")
        source_palette = _palette(source_grid) - {background}
        target_palette = _palette(target_grid) - {background}
        if len(source_palette) != 1 or len(target_palette) != 2:
            raise Undefined("dock needs one source role and two output roles")
        source_color = next(iter(source_palette))
        sources = _components(source_grid, include_colors=(source_color,))
        targets = _components(target_grid, include_colors=target_palette)
        if len(sources) < 2 or len(sources) != len(targets):
            raise Undefined("dock object inventory changed")
        matches = _match_unique_shapes(sources, targets)
        colors_by_role: dict[str, set[int]] = {"closed": set(), "open": set()}
        width = len(source_grid[0])
        for source, target in matches:
            source_top, _, source_left, _ = source.bbox
            target_top, _, target_left, target_right = target.bbox
            if target_top != source_top:
                raise Undefined("dock moved an object vertically")
            if target_left == 0 and target_right != width - 1:
                side = "closed"
            elif target_right == width - 1 and target_left != 0:
                side = "open"
            else:
                raise Undefined("dock target is not on exactly one horizontal border")
            predicted = (
                "closed"
                if _has_enclosed_void_or_is_solid(source.normalized)
                else "open"
            )
            if side != predicted or target_left == source_left:
                raise Undefined("intrinsic role does not explain the dock direction")
            colors_by_role[side].add(target.color)
        if any(len(colors) != 1 for colors in colors_by_role.values()):
            raise Undefined("both dock role branches need one supported color")
        closed_color = next(iter(colors_by_role["closed"]))
        open_color = next(iter(colors_by_role["open"]))
        if len({background, source_color, closed_color, open_color}) != 4:
            raise Undefined("dock colors are not role-distinct")
        parameter_sets.add((background, source_color, closed_color, open_color))
    if len(parameter_sets) != 1:
        raise Undefined("dock parameters vary across demonstrations")
    background, source_color, closed_color, open_color = next(iter(parameter_sets))
    program = {
        "schema": SCHEMA,
        "operator": "dock_closed_open_horizontal",
        "background_color": background,
        "source_color": source_color,
        "closed_color": closed_color,
        "open_color": open_color,
        "connectivity": 4,
        "classification": "solid_or_enclosed_void_vs_open_complement",
        "coordinate_frame": "root_horizontal_outer_borders",
        "description_length": 19,
    }
    for source, target in pairs:
        if _dock_execute(program, source)[0] != target:
            raise Undefined("dock program failed exact demonstration replay")
    return program


@dataclass(frozen=True, slots=True)
class CavityScene:
    background: int
    scaffold_color: int
    inventory_color: int
    scaffold: frozenset[Cell]
    scaffold_bbox: tuple[int, int, int, int]
    holes: frozenset[Cell]
    pieces: tuple[Component, ...]


def _cavity_scene(
    grid: Grid,
    *,
    background: int,
    scaffold_color: int,
    inventory_color: int,
) -> CavityScene:
    if len({background, scaffold_color, inventory_color}) != 3:
        raise Undefined("cavity input roles must use distinct colors")
    if _palette(grid) != frozenset((background, scaffold_color, inventory_color)):
        raise Undefined("cavity input palette violates the learned roles")
    height, width = _shape(grid)
    scaffold = frozenset(
        (row, column)
        for row in range(height)
        for column in range(width)
        if grid[row][column] == scaffold_color
    )
    if not scaffold or any((0, column) not in scaffold for column in range(width)):
        raise Undefined("scaffold must span the complete top border")
    scaffold_components = _components(grid, include_colors=(scaffold_color,))
    if len(scaffold_components) != 1 or scaffold_components[0].cells != scaffold:
        raise Undefined("scaffold identity is disconnected")
    bounds = _bbox(scaffold)
    row0, row1, column0, column1 = bounds
    if row0 != 0 or column0 != 0 or column1 != width - 1 or row1 < 1:
        raise Undefined("scaffold frame is not a nontrivial top strip")
    holes = frozenset(
        (row, column)
        for row in range(row0, row1 + 1)
        for column in range(column0, column1 + 1)
        if (row, column) not in scaffold
    )
    if not holes:
        raise Undefined("scaffold has no cavities")
    pieces = _components(grid, include_colors=(inventory_color,))
    if len(pieces) < 2 or len({piece.signature for piece in pieces}) != len(pieces):
        raise Undefined("inventory needs at least two shape-distinct pieces")
    if any(min(row for row, _ in piece.cells) <= row1 + 1 for piece in pieces):
        raise Undefined("inventory is not separated from the scaffold")
    return CavityScene(
        background,
        scaffold_color,
        inventory_color,
        scaffold,
        bounds,
        holes,
        pieces,
    )


def _piece_options(
    piece: Component,
    scene: CavityScene,
    shape: tuple[int, int],
) -> tuple[frozenset[Cell], ...]:
    height, width = shape
    normalized = piece.normalized
    piece_height = max(row for row, _ in normalized) + 1
    piece_width = max(column for _, column in normalized) + 1
    options: list[frozenset[Cell]] = []
    for top in range(height - piece_height + 1):
        for left in range(width - piece_width + 1):
            placement = frozenset(
                (top + row, left + column) for row, column in normalized
            )
            if placement & scene.scaffold or not placement & scene.holes:
                continue
            options.append(placement)
    return tuple(sorted(set(options), key=lambda cells: tuple(sorted(cells))))


def _unique_cavity_assignment(
    grid: Grid,
    scene: CavityScene,
    *,
    max_search_nodes: int,
) -> tuple[tuple[int, frozenset[Cell]], ...]:
    options = tuple(_piece_options(piece, scene, _shape(grid)) for piece in scene.pieces)
    if any(not choices for choices in options):
        raise Undefined("an inventory piece has no cavity-compatible translation")
    order = tuple(
        sorted(
            range(len(scene.pieces)),
            key=lambda index: (
                len(options[index]),
                -scene.pieces[index].area,
                scene.pieces[index].signature,
            ),
        )
    )
    solutions: list[tuple[tuple[int, frozenset[Cell]], ...]] = []
    nodes = 0

    def search(
        depth: int,
        occupied: frozenset[Cell],
        covered: frozenset[Cell],
        placements: tuple[tuple[int, frozenset[Cell]], ...],
    ) -> None:
        nonlocal nodes
        nodes += 1
        if nodes > max_search_nodes:
            raise Undefined("cavity exact-cover search exhausted its node cap")
        if len(solutions) > 1:
            return
        if depth == len(order):
            if covered == scene.holes:
                solutions.append(tuple(sorted(placements)))
            return
        missing = scene.holes - covered
        possible_cover: set[Cell] = set()
        for later in order[depth:]:
            for choice in options[later]:
                if not choice & occupied:
                    possible_cover.update(choice & scene.holes)
        if not missing <= possible_cover:
            return
        index = order[depth]
        for placement in options[index]:
            if placement & occupied:
                continue
            search(
                depth + 1,
                occupied | placement,
                covered | (placement & scene.holes),
                placements + ((index, placement),),
            )

    search(0, frozenset(), frozenset(), ())
    if len(solutions) != 1:
        raise Undefined("cavity lineage assignment is absent or ambiguous")
    return solutions[0]


def _cavity_execute(
    program: Mapping[str, Any], grid: Grid, *, max_search_nodes: int
) -> tuple[Grid, dict[str, Any]]:
    background = _require_color_field(program, "background_color")
    scaffold_color = _require_color_field(program, "scaffold_color")
    inventory_color = _require_color_field(program, "inventory_color")
    fill_color = _require_color_field(program, "fill_color")
    if len({background, scaffold_color, inventory_color, fill_color}) != 4:
        raise Undefined("cavity roles must use distinct colors")
    scene = _cavity_scene(
        grid,
        background=background,
        scaffold_color=scaffold_color,
        inventory_color=inventory_color,
    )
    assignment = _unique_cavity_assignment(
        grid, scene, max_search_nodes=max_search_nodes
    )
    height, width = _shape(grid)
    result = [[background for _ in range(width)] for _ in range(height)]
    for row, column in scene.scaffold:
        result[row][column] = scaffold_color
    root_hash = _digest({"schema": f"{SCHEMA}.root", "grid": _plain(grid)})
    placements: list[dict[str, Any]] = []
    for index, target_cells in assignment:
        piece = scene.pieces[index]
        for row, column in target_cells:
            if result[row][column] != background:
                raise Undefined("cavity assignment overlaps preserved structure")
            result[row][column] = fill_color
        source_top, _, source_left, _ = piece.bbox
        target_top, _, target_left, _ = _bbox(target_cells)
        entity = _entity_record(root_hash, grid, piece)
        placements.append(
            {
                **entity,
                "role": "inventory_piece",
                "delta": [target_top - source_top, target_left - source_left],
                "target_bbox": list(_bbox(target_cells)),
                "target_cells": [list(cell) for cell in sorted(target_cells)],
                "output_color": fill_color,
            }
        )
    output = tuple(tuple(row) for row in result)
    return output, {
        "root_hash": root_hash,
        "operator": "unique_scaffold_cavity_assignment",
        "scaffold_bbox": list(scene.scaffold_bbox),
        "scaffold_hash": _digest([list(cell) for cell in sorted(scene.scaffold)]),
        "cavity_hash": _digest([list(cell) for cell in sorted(scene.holes)]),
        "cavity_cells": len(scene.holes),
        "entities": sorted(placements, key=lambda item: item["entity_id"]),
        "assignment_unique": True,
        "output_hash": _digest(_plain(output)),
    }


def _infer_cavity_program(
    pairs: Sequence[Pair], *, max_search_nodes: int
) -> dict[str, Any]:
    parameter_sets: set[tuple[int, int, int, int]] = set()
    for source, target in pairs:
        if _shape(source) != _shape(target):
            raise Undefined("cavity composition preserves canvas shape")
        background = _mode(source)
        colors = _palette(source) - {background}
        if len(colors) != 2:
            raise Undefined("cavity input needs scaffold and inventory colors")
        width = len(source[0])
        top_colors = {source[0][column] for column in range(width)}
        if len(top_colors) != 1:
            raise Undefined("cavity scaffold does not span the top border")
        scaffold_color = next(iter(top_colors))
        if scaffold_color == background or scaffold_color not in colors:
            raise Undefined("top border does not identify the scaffold role")
        inventory_color = next(iter(colors - {scaffold_color}))
        target_other = _palette(target) - {background, scaffold_color}
        if len(target_other) != 1:
            raise Undefined("cavity target needs one translated fill role")
        fill_color = next(iter(target_other))
        if len({background, scaffold_color, inventory_color, fill_color}) != 4:
            raise Undefined("cavity colors are not role-distinct")
        source_scaffold = {
            (row, column)
            for row in range(len(source))
            for column in range(len(source[0]))
            if source[row][column] == scaffold_color
        }
        target_scaffold = {
            (row, column)
            for row in range(len(target))
            for column in range(len(target[0]))
            if target[row][column] == scaffold_color
        }
        if source_scaffold != target_scaffold:
            raise Undefined("cavity scaffold is not preserved exactly")
        parameter_sets.add((background, scaffold_color, inventory_color, fill_color))
    if len(parameter_sets) != 1:
        raise Undefined("cavity role colors vary across demonstrations")
    background, scaffold_color, inventory_color, fill_color = next(iter(parameter_sets))
    program = {
        "schema": SCHEMA,
        "operator": "unique_scaffold_cavity_assignment",
        "background_color": background,
        "scaffold_color": scaffold_color,
        "inventory_color": inventory_color,
        "fill_color": fill_color,
        "connectivity": 4,
        "orientation_policy": "translation_only",
        "coverage_policy": "cover_every_scaffold_bbox_cavity",
        "collision_policy": "exact_nonoverlap",
        "description_length": 23,
    }
    for source, target in pairs:
        if _cavity_execute(program, source, max_search_nodes=max_search_nodes)[0] != target:
            raise Undefined("cavity program failed exact demonstration replay")
    return program


def _execute_internal(
    program: Mapping[str, Any], grid: Grid, *, max_search_nodes: int = 200_000
) -> tuple[Grid, dict[str, Any]]:
    if not isinstance(program, Mapping) or program.get("schema") != SCHEMA:
        raise Undefined("invalid lineage-composition program")
    operator = program.get("operator")
    if operator == "dock_closed_open_horizontal":
        return _dock_execute(program, grid)
    if operator == "unique_scaffold_cavity_assignment":
        return _cavity_execute(program, grid, max_search_nodes=max_search_nodes)
    raise Undefined("unknown lineage-composition operator")


def execute_program(program: Mapping[str, Any], value: Any) -> list[list[int]]:
    """Execute one serialized lineage program deterministically."""

    grid = _grid(value)
    return _plain(_execute_internal(program, grid)[0])


def replay_program(program: Mapping[str, Any], value: Any) -> dict[str, Any]:
    """Replay through explicit lift, transition, and lineage render stages."""

    grid = _grid(value)
    output, receipt = _execute_internal(program, grid)
    lifted = {
        "schema": f"{SCHEMA}.lift.v1",
        "root_hash": receipt["root_hash"],
        "entity_count": len(receipt["entities"]),
        "entities": [
            {
                key: entity[key]
                for key in (
                    "entity_id",
                    "source_bbox",
                    "area",
                    "color",
                    "shape_signature",
                    "root_pixel_ids",
                )
            }
            for entity in receipt["entities"]
        ],
    }
    transitioned = {
        "schema": f"{SCHEMA}.transition.v1",
        "operator": receipt["operator"],
        "placements": [
            {
                key: entity[key]
                for key in (
                    "entity_id",
                    "role",
                    "delta",
                    "target_bbox",
                    "target_cells",
                    "output_color",
                )
            }
            for entity in receipt["entities"]
        ],
        "lineage_preserved": True,
        "output_hash": receipt["output_hash"],
    }
    return {
        "output": _plain(output),
        "stages": [
            {"name": "lift-lineage-state", "input": _plain(grid), "output": lifted},
            {
                "name": "compose-role-transitions",
                "input": lifted,
                "output": transitioned,
            },
            {
                "name": "render-with-exact-provenance",
                "input": transitioned,
                "output": _plain(output),
            },
        ],
    }


def _infer_operator(
    operator: str, pairs: Sequence[Pair], limits: Limits
) -> dict[str, Any]:
    if operator == "dock_closed_open_horizontal":
        return _infer_dock_program(pairs)
    if operator == "unique_scaffold_cavity_assignment":
        return _infer_cavity_program(pairs, max_search_nodes=limits.max_search_nodes)
    raise Undefined("unknown inference operator")


def _loo(
    operator: str, pairs: Sequence[Pair], limits: Limits
) -> tuple[bool, list[dict[str, Any]]]:
    witnesses: list[dict[str, Any]] = []
    for held_index, (source, target) in enumerate(pairs):
        subset = tuple(pair for index, pair in enumerate(pairs) if index != held_index)
        try:
            program = _infer_operator(operator, subset, limits)
            output = _execute_internal(
                program, source, max_search_nodes=limits.max_search_nodes
            )[0]
        except (Undefined, TypeError, ValueError, KeyError, IndexError):
            return False, witnesses
        exact = output == target
        witnesses.append(
            {
                "held_out_index": held_index,
                "proposal_demo_count": len(subset),
                "held_out_exact": exact,
                "held_out_output_hash": _digest(_plain(output)),
            }
        )
        if not exact:
            return False, witnesses
    return True, witnesses


def _swap_grid(grid: Grid, left: int, right: int) -> Grid:
    return tuple(
        tuple(right if cell == left else left if cell == right else cell for cell in row)
        for row in grid
    )


def _transport_program_palette(
    program: Mapping[str, Any], left: int, right: int
) -> dict[str, Any]:
    transported = json.loads(_canonical(program))
    for key in (
        "background_color",
        "source_color",
        "closed_color",
        "open_color",
        "scaffold_color",
        "inventory_color",
        "fill_color",
    ):
        if key not in transported:
            continue
        value = transported[key]
        transported[key] = right if value == left else left if value == right else value
    return transported


def _palette_counterfactuals(
    program: Mapping[str, Any], pairs: Sequence[Pair], limits: Limits
) -> tuple[bool, int]:
    used = sorted(
        {
            cell
            for source, target in pairs
            for grid in (source, target)
            for row in grid
            for cell in row
        }
    )
    absent = next((color for color in range(10) if color not in used), None)
    if absent is None:
        return False, 0
    checks = 0
    for color in used:
        transported = _transport_program_palette(program, color, absent)
        for source, target in pairs:
            try:
                actual = _execute_internal(
                    transported,
                    _swap_grid(source, color, absent),
                    max_search_nodes=limits.max_search_nodes,
                )[0]
            except (Undefined, TypeError, ValueError, KeyError, IndexError):
                return False, checks
            checks += 1
            if actual != _swap_grid(target, color, absent):
                return False, checks
    return checks > 0, checks


def _candidate_for_program(
    program: Mapping[str, Any], pairs: Sequence[Pair], tests: Sequence[Grid], limits: Limits
) -> dict[str, Any] | None:
    operator = str(program["operator"])
    try:
        train_outputs = tuple(
            _execute_internal(program, source, max_search_nodes=limits.max_search_nodes)[0]
            for source, _ in pairs
        )
        if train_outputs != tuple(target for _, target in pairs):
            return None
        test_outputs = tuple(
            _execute_internal(program, grid, max_search_nodes=limits.max_search_nodes)[0]
            for grid in tests
        )
    except (Undefined, TypeError, ValueError, KeyError, IndexError):
        return None
    loo_ok, loo_witnesses = _loo(operator, pairs, limits)
    if not loo_ok:
        return None
    palette_ok, palette_checks = _palette_counterfactuals(program, pairs, limits)
    if not palette_ok:
        return None
    candidate = {
        "family": "lineage_composition",
        "program": json.loads(_canonical(program)),
        "train_outputs": [_plain(grid) for grid in train_outputs],
        "test_outputs": [_plain(grid) for grid in test_outputs],
        "complexity": int(program["description_length"]),
        "evidence": {
            "all_demonstrations_exact": True,
            "exact_replay": True,
            "persistent_entity_identity": True,
            "exact_root_pixel_provenance": True,
            "two_stage_composition": True,
            "leave_one_demo_out_reinduction": True,
            "leave_one_out_witnesses": loo_witnesses,
            "palette_transport_counterfactuals": palette_checks,
            "test_behavior_classes": 1,
            "trace_support_complete": True,
            "bounded_search": True,
            "hard_caps_exhausted": False,
            "task_identity_observed": False,
            "test_labels_observed": False,
            "solution_store_observed": False,
        },
    }
    candidate["evidence"]["candidate_semantic_hash"] = _digest(candidate)
    return candidate


def compile_task(task: Any, limits: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    """Compile one unique label-blind lineage behavior or abstain."""

    try:
        bounds = Limits.from_value(limits)
        pairs, tests = _sanitize(task, bounds)
    except (Undefined, TypeError, ValueError, KeyError, IndexError):
        return []
    candidates: list[dict[str, Any]] = []
    calls = 0
    for operator in (
        "dock_closed_open_horizontal",
        "unique_scaffold_cavity_assignment",
    ):
        try:
            program = _infer_operator(operator, pairs, bounds)
            calls += len(pairs)
            if calls > bounds.max_executor_calls:
                return []
            candidate = _candidate_for_program(program, pairs, tests, bounds)
        except (Undefined, TypeError, ValueError, KeyError, IndexError):
            candidate = None
        if candidate is not None:
            candidates.append(candidate)
    if not candidates:
        return []
    behaviors: dict[str, list[dict[str, Any]]] = {}
    for candidate in candidates:
        behaviors.setdefault(_digest(candidate["test_outputs"]), []).append(candidate)
    if len(behaviors) != 1:
        return []
    equivalent = next(iter(behaviors.values()))
    equivalent.sort(
        key=lambda item: (item["complexity"], _canonical(item["program"]))
    )
    return equivalent[: bounds.max_candidates]


def predict_task(task_id: Any, task: Any) -> list[list[list[int]]]:
    """Return held-out rasters for the unique behavior; task identity is ignored."""

    del task_id
    candidates = compile_task(task)
    return candidates[0]["test_outputs"] if len(candidates) == 1 else []


__all__ = [
    "AUTHOR",
    "Limits",
    "SCHEMA",
    "Undefined",
    "compile_task",
    "execute_program",
    "predict_task",
    "replay_program",
]

