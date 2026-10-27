"""Proof-carrying topology and residual-shape compiler for Block 15.

The compiler treats a raster as a collection of connected supports, cavities,
rectilinear skeletons, and finite geometric stencils.  Every emitted program is
derived only from labelled demonstrations and held-input rasters.  There is no
task identity, corpus fingerprint, score, solution-store, or held-label access.

The deliberately small grammar covers line defects, local consensus crosses,
solid rectangular cores, balanced diagonal components, partial-cross repair,
stencil replication, topology-preserving orthogonal stretch, and a dynamic
largest-component symmetry repair.  Programs fail closed on ambiguity and are
checked by exact replay, isolated leave-one-demonstration-out re-proposal, and
D4 counterfactuals before a prediction is exposed.

Author: Komorebi P.
"""

from __future__ import annotations

from collections import Counter, deque
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import hashlib
import json
from typing import Any, Callable, Iterable


Grid = tuple[tuple[int, ...], ...]
Cell = tuple[int, int]
Pair = tuple[Grid, Grid]
SCHEMA = "komorebi.pr_lasm.block15.topology_shape_compiler.program.v1"
AUTHOR = "Komorebi P."


class Undefined(ValueError):
    """A structural role, program, or behavior is absent or ambiguous."""


@dataclass(frozen=True, slots=True)
class Limits:
    max_side: int = 40
    max_examples: int = 20
    max_cells: int = 120_000
    max_programs: int = 1_024
    max_candidates: int = 1
    max_counterfactuals: int = 128
    max_partition_states: int = 60_000

    @classmethod
    def parse(cls, raw: Any) -> "Limits":
        if raw is None:
            return cls()
        if not isinstance(raw, Mapping):
            raise Undefined("limits must be a mapping")
        aliases = {
            "candidate_cap": "max_candidates",
            "max_grid_cells": "max_cells",
            "max_replay_calls": None,
            "max_replay_stages": None,
            "max_trace_bytes": None,
            "time_limit": None,
            "time_limit_seconds": None,
            "ambiguity_slack": None,
        }
        fields = set(cls.__dataclass_fields__)
        values: dict[str, int] = {}
        for raw_name, raw_value in raw.items():
            name = aliases.get(str(raw_name), str(raw_name))
            if name is None or name not in fields:
                continue
            if isinstance(raw_value, bool) or not isinstance(raw_value, int) or raw_value < 1:
                raise Undefined("finite limits must be positive integers")
            values[name] = raw_value
        return cls(**values)


@dataclass(frozen=True, slots=True)
class Proposal:
    family: str
    program: Mapping[str, Any]
    complexity: int


_N4 = ((-1, 0), (0, -1), (0, 1), (1, 0))
_N8 = tuple(
    (dr, dc)
    for dr in (-1, 0, 1)
    for dc in (-1, 0, 1)
    if dr or dc
)
_PLUS = frozenset({(0, 1), (1, 0), (1, 1), (1, 2), (2, 1)})


def _canonical(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _grid(value: Any, max_side: int = 40) -> Grid:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise Undefined("grid must be a row sequence")
    if not value or len(value) > max_side:
        raise Undefined("invalid grid height")
    width: int | None = None
    rows: list[tuple[int, ...]] = []
    for raw_row in value:
        if not isinstance(raw_row, Sequence) or isinstance(
            raw_row, (str, bytes, bytearray)
        ):
            raise Undefined("grid row must be a sequence")
        if width is None:
            width = len(raw_row)
        if width is None or width < 1 or width > max_side or len(raw_row) != width:
            raise Undefined("grid must be nonempty and rectangular")
        row: list[int] = []
        for cell in raw_row:
            if isinstance(cell, bool) or not isinstance(cell, int) or not 0 <= cell <= 9:
                raise Undefined("ARC colors must be integers in [0, 9]")
            row.append(int(cell))
        rows.append(tuple(row))
    return tuple(rows)


def _plain(grid: Grid) -> list[list[int]]:
    return [list(row) for row in grid]


def _shape(grid: Grid) -> tuple[int, int]:
    return len(grid), len(grid[0])


def _sanitize(task: Any, limits: Limits) -> tuple[tuple[Pair, ...], tuple[Grid, ...]]:
    if not isinstance(task, Mapping):
        raise Undefined("task must be a mapping")
    train, test = task.get("train"), task.get("test")
    if (
        not isinstance(train, Sequence)
        or isinstance(train, (str, bytes, bytearray))
        or len(train) < 2
        or not isinstance(test, Sequence)
        or isinstance(test, (str, bytes, bytearray))
        or not test
        or len(train) + len(test) > limits.max_examples
    ):
        raise Undefined("invalid task arity")
    demonstrations: list[Pair] = []
    tests: list[Grid] = []
    cells = 0
    for record in train:
        if not isinstance(record, Mapping):
            raise Undefined("invalid demonstration")
        source = _grid(record.get("input"), limits.max_side)
        target = _grid(record.get("output"), limits.max_side)
        cells += len(source) * len(source[0]) + len(target) * len(target[0])
        demonstrations.append((source, target))
    for record in test:
        if not isinstance(record, Mapping):
            raise Undefined("invalid test record")
        # The label-blind contract deliberately permits this key and no other.
        source = _grid(record.get("input"), limits.max_side)
        cells += len(source) * len(source[0])
        tests.append(source)
    if cells > limits.max_cells:
        raise Undefined("cell budget exhausted")
    return tuple(demonstrations), tuple(tests)


def _components(grid: Grid, color: int, connectivity: int) -> tuple[frozenset[Cell], ...]:
    neighbors = _N4 if connectivity == 4 else _N8 if connectivity == 8 else None
    if neighbors is None:
        raise Undefined("connectivity must be four or eight")
    unseen = {
        (row, column)
        for row in range(len(grid))
        for column in range(len(grid[0]))
        if grid[row][column] == color
    }
    result: list[frozenset[Cell]] = []
    while unseen:
        root = min(unseen)
        unseen.remove(root)
        queue = deque([root])
        component = {root}
        while queue:
            row, column = queue.popleft()
            for dr, dc in neighbors:
                other = row + dr, column + dc
                if other in unseen:
                    unseen.remove(other)
                    component.add(other)
                    queue.append(other)
        result.append(frozenset(component))
    return tuple(sorted(result, key=lambda cells: (min(cells), len(cells))))


def _all_monochrome_components(
    grid: Grid, connectivity: int
) -> tuple[tuple[int, frozenset[Cell]], ...]:
    return tuple(
        (color, component)
        for color in sorted({cell for row in grid for cell in row})
        for component in _components(grid, color, connectivity)
    )


def _bbox(cells: Iterable[Cell]) -> tuple[int, int, int, int]:
    materialized = tuple(cells)
    if not materialized:
        raise Undefined("empty support")
    return (
        min(row for row, _ in materialized),
        max(row for row, _ in materialized),
        min(column for _, column in materialized),
        max(column for _, column in materialized),
    )


def _normalize(cells: Iterable[Cell]) -> frozenset[Cell]:
    materialized = frozenset(cells)
    top, _, left, _ = _bbox(materialized)
    return frozenset((row - top, column - left) for row, column in materialized)


def _mask(cells: Iterable[Cell]) -> tuple[tuple[int, ...], ...]:
    materialized = frozenset(cells)
    top, bottom, left, right = _bbox(materialized)
    return tuple(
        tuple(int((row, column) in materialized) for column in range(left, right + 1))
        for row in range(top, bottom + 1)
    )


def _rotate(grid: Grid) -> Grid:
    height, width = _shape(grid)
    return tuple(
        tuple(grid[height - 1 - row][column] for row in range(height))
        for column in range(width)
    )


def _d4(grid: Grid, operation: str) -> Grid:
    if operation == "identity":
        return grid
    if operation == "rot90":
        return _rotate(grid)
    if operation == "rot180":
        return _rotate(_rotate(grid))
    if operation == "rot270":
        return _rotate(_rotate(_rotate(grid)))
    if operation == "flip_h":
        return tuple(tuple(reversed(row)) for row in grid)
    raise Undefined("unknown D4 operation")


def _shape_orbit(cells: Iterable[Cell], *, reflections: bool) -> frozenset[frozenset[Cell]]:
    source = _normalize(cells)
    operations: tuple[Callable[[int, int], Cell], ...] = (
        lambda row, column: (row, column),
        lambda row, column: (column, -row),
        lambda row, column: (-row, -column),
        lambda row, column: (-column, row),
    )
    if reflections:
        operations += (
            lambda row, column: (row, -column),
            lambda row, column: (-row, column),
            lambda row, column: (column, row),
            lambda row, column: (-column, -row),
        )
    return frozenset(
        _normalize(operation(row, column) for row, column in source)
        for operation in operations
    )


def _compress_mask(mask: tuple[tuple[int, ...], ...]) -> tuple[tuple[int, ...], ...]:
    current = mask
    previous: tuple[tuple[int, ...], ...] | None = None
    while current != previous:
        previous = current
        current = tuple(
            row for index, row in enumerate(current) if index == 0 or row != current[index - 1]
        )
        columns = tuple(zip(*current))
        columns = tuple(
            column
            for index, column in enumerate(columns)
            if index == 0 or column != columns[index - 1]
        )
        current = tuple(tuple(row) for row in zip(*columns))
    return current


def _mask_orbit(mask: tuple[tuple[int, ...], ...]) -> frozenset[tuple[tuple[int, ...], ...]]:
    result: set[tuple[tuple[int, ...], ...]] = set()
    current = mask
    for _ in range(4):
        result.add(_compress_mask(current))
        result.add(_compress_mask(tuple(tuple(reversed(row)) for row in current)))
        height, width = len(current), len(current[0])
        current = tuple(
            tuple(current[height - 1 - row][column] for row in range(height))
            for column in range(width)
        )
    return frozenset(result)


def _program(operator: str, **parameters: Any) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "operator": operator,
        "root_scope": "immutable_input",
        **parameters,
    }


def _full_monochrome_lines(grid: Grid, program: Mapping[str, Any]) -> Grid:
    source, paint = int(program["source"]), int(program["paint"])
    height, width = _shape(grid)
    rows = [row for row in range(height) if all(grid[row][column] == source for column in range(width))]
    columns = [
        column
        for column in range(width)
        if all(grid[row][column] == source for row in range(height))
    ]
    if not rows and not columns:
        raise Undefined("no complete monochrome line")
    output = [list(row) for row in grid]
    changed = False
    for row in rows:
        for column in range(width):
            output[row][column] = paint
            changed = True
    for column in columns:
        for row in range(height):
            output[row][column] = paint
            changed = True
    if not changed:
        raise Undefined("line repair emitted nothing")
    return tuple(tuple(row) for row in output)


def _solid_plus_consensus(grid: Grid, program: Mapping[str, Any]) -> Grid:
    source, paint = int(program["source"]), int(program["paint"])
    height, width = _shape(grid)
    selected: set[Cell] = set()
    for top in range(height - 2):
        for left in range(width - 2):
            cells = {(top + row, left + column) for row, column in _PLUS}
            if all(grid[row][column] == source for row, column in cells):
                selected.update(cells)
    if not selected:
        raise Undefined("no solid plus stencil")
    output = [list(row) for row in grid]
    for row, column in selected:
        output[row][column] = paint
    return tuple(tuple(row) for row in output)


def _largest_rectangle_cores(grid: Grid, program: Mapping[str, Any]) -> Grid:
    source, paint = int(program["source"]), int(program["paint"])
    height, width = _shape(grid)
    selected: set[Cell] = set()
    for component in _components(grid, source, 4):
        best_area = 0
        rectangles: list[frozenset[Cell]] = []
        for top in range(height - 1):
            valid = [True] * width
            for bottom in range(top, height):
                for column in range(width):
                    valid[column] = valid[column] and (bottom, column) in component
                if bottom == top:
                    continue
                left = 0
                while left < width:
                    if not valid[left]:
                        left += 1
                        continue
                    right = left
                    while right < width and valid[right]:
                        right += 1
                    if right - left >= 2:
                        cells = frozenset(
                            (row, column)
                            for row in range(top, bottom + 1)
                            for column in range(left, right)
                        )
                        area = len(cells)
                        if area > best_area:
                            best_area, rectangles = area, [cells]
                        elif area == best_area:
                            rectangles.append(cells)
                    left = right
        if rectangles:
            for rectangle in rectangles:
                selected.update(rectangle)
    if not selected:
        raise Undefined("no two-dimensional rectangle core")
    output = [list(row) for row in grid]
    for row, column in selected:
        output[row][column] = paint
    return tuple(tuple(row) for row in output)


def _balanced_diagonal_components(grid: Grid, program: Mapping[str, Any]) -> Grid:
    source, paint = int(program["source"]), int(program["paint"])
    selected: list[frozenset[Cell]] = []
    for component in _components(grid, source, 8):
        top, bottom, left, right = _bbox(component)
        height, width = bottom - top + 1, right - left + 1
        if min(height, width) >= 3 and 2 * max(height, width) < 3 * min(height, width):
            selected.append(component)
    if not selected:
        raise Undefined("no balanced diagonal component")
    output = [list(row) for row in grid]
    for component in selected:
        for row, column in component:
            output[row][column] = paint
    return tuple(tuple(row) for row in output)


def _partial_unit_plus(grid: Grid, program: Mapping[str, Any]) -> Grid:
    marker = int(program["marker"])
    source = int(program["source"])
    paint = int(program["paint"])
    height, width = _shape(grid)
    output = [list(row) for row in grid]
    active = 0
    for component in _components(grid, marker, 8):
        behaviors: set[frozenset[Cell]] = set()
        for center_row in range(height):
            for center_column in range(width):
                support = {
                    (center_row, center_column),
                    (center_row - 1, center_column),
                    (center_row + 1, center_column),
                    (center_row, center_column - 1),
                    (center_row, center_column + 1),
                }
                support = {
                    cell
                    for cell in support
                    if 0 <= cell[0] < height and 0 <= cell[1] < width
                }
                if component <= support and all(
                    grid[row][column] in {marker, source} for row, column in support
                ):
                    behaviors.add(frozenset(support - set(component)))
        if len(behaviors) != 1:
            raise Undefined("partial plus alignment is ambiguous")
        for row, column in next(iter(behaviors)):
            if output[row][column] == source:
                output[row][column] = paint
                active += 1
    if not active:
        raise Undefined("partial plus completion emitted nothing")
    return tuple(tuple(row) for row in output)


def _exact_cover_crosses(
    grid: Grid, marker: int, minimum_markers: int, state_cap: int
) -> frozenset[Cell]:
    height, width = _shape(grid)
    markers = frozenset(
        (row, column)
        for row in range(height)
        for column in range(width)
        if grid[row][column] == marker
    )
    if not minimum_markers <= len(markers) <= 64:
        raise Undefined("marker inventory is outside cross grammar")

    for radius in range(1, 7):
        candidates: list[tuple[frozenset[Cell], frozenset[Cell]]] = []
        seen: set[tuple[frozenset[Cell], frozenset[Cell]]] = set()
        for center_row in range(height):
            for center_column in range(width):
                support = frozenset(
                    cell
                    for cell in (
                        {(center_row + delta, center_column) for delta in range(-radius, radius + 1)}
                        | {(center_row, center_column + delta) for delta in range(-radius, radius + 1)}
                    )
                    if 0 <= cell[0] < height and 0 <= cell[1] < width
                )
                covered = frozenset(markers & support)
                candidate = support, covered
                if len(covered) >= minimum_markers and candidate not in seen:
                    seen.add(candidate)
                    candidates.append(candidate)
        if len(candidates) > 256:
            continue
        by_marker: dict[Cell, list[int]] = {cell: [] for cell in markers}
        for index, (_, covered) in enumerate(candidates):
            for cell in covered:
                by_marker[cell].append(index)
        if any(not choices for choices in by_marker.values()):
            continue

        best_count: int | None = None
        solutions: list[tuple[int, ...]] = []
        states = 0

        def search(remaining: frozenset[Cell], chosen: tuple[int, ...]) -> None:
            nonlocal best_count, states
            states += 1
            if states > state_cap:
                raise Undefined("cross exact-cover state budget exhausted")
            if not remaining:
                if best_count is None or len(chosen) < best_count:
                    best_count = len(chosen)
                    solutions.clear()
                    solutions.append(chosen)
                elif len(chosen) == best_count:
                    solutions.append(chosen)
                return
            if best_count is not None and len(chosen) >= best_count:
                return
            pivot = min(
                remaining,
                key=lambda cell: sum(
                    candidates[index][1] <= remaining for index in by_marker[cell]
                ),
            )
            for index in by_marker[pivot]:
                covered = candidates[index][1]
                if covered <= remaining:
                    search(remaining - covered, chosen + (index,))

        search(markers, ())
        if not solutions:
            continue
        behaviors = {
            frozenset().union(*(candidates[index][0] for index in solution))
            for solution in solutions
        }
        if len(behaviors) != 1:
            raise Undefined("minimum cross cover has multiple support behaviors")
        return next(iter(behaviors))
    raise Undefined("no finite cross cover")


def _fragment_cross_cover(grid: Grid, program: Mapping[str, Any]) -> Grid:
    marker = int(program["marker"])
    source = int(program["source"])
    paint = int(program["paint"])
    minimum_markers = int(program.get("minimum_markers", 3))
    state_cap = int(program.get("state_cap", 60_000))
    support = _exact_cover_crosses(grid, marker, minimum_markers, state_cap)
    output = [list(row) for row in grid]
    active = 0
    for row, column in support:
        if output[row][column] == source:
            output[row][column] = paint
            active += 1
    if not active:
        raise Undefined("cross cover emitted nothing")
    return tuple(tuple(row) for row in output)


def _c4_exemplar_stencil(grid: Grid, program: Mapping[str, Any]) -> Grid:
    source = int(program["source"])
    exemplar = int(program["exemplar"])
    paint = int(program["paint"])
    components = _components(grid, exemplar, 8)
    if len(components) != 1 or len(components[0]) < 3:
        raise Undefined("one nontrivial exemplar is required")
    stencils = _shape_orbit(components[0], reflections=False)
    height, width = _shape(grid)
    selected: set[Cell] = set()
    for stencil in stencils:
        stencil_height = max(row for row, _ in stencil) + 1
        stencil_width = max(column for _, column in stencil) + 1
        for top in range(height - stencil_height + 1):
            for left in range(width - stencil_width + 1):
                cells = {
                    (top + row, left + column) for row, column in stencil
                }
                if all(grid[row][column] == source for row, column in cells):
                    selected.update(cells)
    if not selected:
        raise Undefined("exemplar has no rendered source-color copies")
    output = [list(row) for row in grid]
    for row, column in selected:
        output[row][column] = paint
    return tuple(tuple(row) for row in output)


def _rectilinear_topology_match(grid: Grid, program: Mapping[str, Any]) -> Grid:
    source = int(program["source"])
    exemplar = int(program["exemplar"])
    paint = int(program["paint"])
    reference_masks: set[tuple[tuple[int, ...], ...]] = set()
    for component in _components(grid, exemplar, 4):
        reference_masks.update(_mask_orbit(_compress_mask(_mask(component))))
    if not reference_masks:
        raise Undefined("topology exemplar is absent")
    selected = [
        component
        for component in _components(grid, source, 4)
        if _compress_mask(_mask(component)) in reference_masks
    ]
    if not selected:
        raise Undefined("no component has the exemplar topology")
    output = [list(row) for row in grid]
    for component in selected:
        for row, column in component:
            output[row][column] = paint
    return tuple(tuple(row) for row in output)


def _largest_component_horizontal_closure(grid: Grid, program: Mapping[str, Any]) -> Grid:
    components = _all_monochrome_components(grid, 4)
    maximum = max(len(component) for _, component in components)
    winners = [(color, component) for color, component in components if len(component) == maximum]
    if len(winners) != 1:
        raise Undefined("largest monochrome component is tied")
    color, component = winners[0]
    height, width = _shape(grid)
    axis = str(program.get("axis", "left_right"))
    if axis == "left_right":
        reflected = {(row, width - 1 - column) for row, column in component}
    elif axis == "top_bottom":
        reflected = {(height - 1 - row, column) for row, column in component}
    else:
        raise Undefined("unknown component-symmetry axis")
    if reflected <= component:
        raise Undefined("largest component is already symmetric on the requested axis")
    output = [list(row) for row in grid]
    for row, column in reflected:
        output[row][column] = color
    return tuple(tuple(row) for row in output)


_EXECUTORS: dict[str, Callable[[Grid, Mapping[str, Any]], Grid]] = {
    "full_monochrome_line_repair": _full_monochrome_lines,
    "solid_plus_consensus": _solid_plus_consensus,
    "largest_rectangle_core_per_component": _largest_rectangle_cores,
    "balanced_diagonal_component_filter": _balanced_diagonal_components,
    "partial_unit_plus_completion": _partial_unit_plus,
    "fragment_cross_exact_cover": _fragment_cross_cover,
    "c4_exemplar_stencil_recolor": _c4_exemplar_stencil,
    "rectilinear_topology_exemplar_recolor": _rectilinear_topology_match,
    "largest_component_horizontal_closure": _largest_component_horizontal_closure,
}


def execute_program(program: Mapping[str, Any], grid: Any) -> list[list[int]]:
    """Execute one finite serialized topology program."""

    if not isinstance(program, Mapping) or program.get("schema") != SCHEMA:
        raise Undefined("unknown program schema")
    executor = _EXECUTORS.get(str(program.get("operator")))
    if executor is None:
        raise Undefined("unknown topology operator")
    return _plain(executor(_grid(grid), program))


def replay_program(program: Mapping[str, Any], grid: Any) -> list[list[int]]:
    """Tournament replay hook.  Neither argument is mutated."""

    return execute_program(program, grid)


def _same_shape_nonidentity(train: Sequence[Pair]) -> bool:
    return all(_shape(source) == _shape(target) and source != target for source, target in train)


def _changed_pairs(source: Grid, target: Grid) -> set[tuple[int, int]]:
    return {
        (before, after)
        for before_row, after_row in zip(source, target)
        for before, after in zip(before_row, after_row)
        if before != after
    }


def _exact(program: Mapping[str, Any], train: Sequence[Pair]) -> bool:
    try:
        return all(_grid(execute_program(program, source)) == target for source, target in train)
    except (Undefined, KeyError, TypeError, ValueError, IndexError, ZeroDivisionError):
        return False


def _enumerate(train: Sequence[Pair], limits: Limits) -> tuple[Proposal, ...]:
    if not _same_shape_nonidentity(train):
        return ()
    pair_sets = [_changed_pairs(source, target) for source, target in train]
    common_pairs = sorted(set.intersection(*pair_sets)) if pair_sets else []
    common_input_colors = sorted(
        set.intersection(
            *[
                {cell for row in source for cell in row}
                for source, _ in train
            ]
        )
    )
    proposals: dict[str, Proposal] = {}
    attempts = 0

    def add(family: str, program: Mapping[str, Any], complexity: int) -> None:
        nonlocal attempts
        attempts += 1
        if attempts > limits.max_programs:
            raise Undefined("program enumeration bound exhausted")
        key = _canonical(program)
        if key not in proposals and _exact(program, train):
            proposals[key] = Proposal(family, dict(program), complexity)

    for axis in ("left_right", "top_bottom"):
        add(
            "topology.dynamic_largest_component_symmetry",
            _program("largest_component_horizontal_closure", axis=axis),
            7,
        )

    for source, paint in common_pairs:
        add(
            "topology.full_line_defect_repair",
            _program("full_monochrome_line_repair", source=source, paint=paint),
            6,
        )
        add(
            "topology.solid_plus_consensus",
            _program("solid_plus_consensus", source=source, paint=paint),
            7,
        )
        add(
            "topology.rectangle_core_extraction",
            _program("largest_rectangle_core_per_component", source=source, paint=paint),
            10,
        )
        add(
            "topology.balanced_diagonal_components",
            _program("balanced_diagonal_component_filter", source=source, paint=paint),
            10,
        )
        for marker in common_input_colors:
            if marker == source:
                continue
            add(
                "topology.partial_unit_plus",
                _program(
                    "partial_unit_plus_completion",
                    marker=marker,
                    source=source,
                    paint=paint,
                ),
                11,
            )
            add(
                "topology.fragment_cross_cover",
                _program(
                    "fragment_cross_exact_cover",
                    marker=marker,
                    source=source,
                    paint=paint,
                    minimum_markers=3,
                    state_cap=limits.max_partition_states,
                ),
                15,
            )
        if paint in common_input_colors:
            add(
                "topology.c4_exemplar_stencil",
                _program(
                    "c4_exemplar_stencil_recolor",
                    source=source,
                    exemplar=paint,
                    paint=paint,
                ),
                12,
            )
            add(
                "topology.rectilinear_exemplar",
                _program(
                    "rectilinear_topology_exemplar_recolor",
                    source=source,
                    exemplar=paint,
                    paint=paint,
                ),
                13,
            )
    return tuple(
        sorted(proposals.values(), key=lambda proposal: (proposal.complexity, _canonical(proposal.program)))
    )


def _loo_exact(proposal: Proposal, train: Sequence[Pair], limits: Limits) -> bool:
    key = _canonical(proposal.program)
    for held_index in range(len(train)):
        retained = train[:held_index] + train[held_index + 1 :]
        if not retained:
            return False
        try:
            alternatives = _enumerate(retained, limits)
        except Undefined:
            return False
        if key not in {_canonical(other.program) for other in alternatives}:
            return False
        try:
            prediction = _grid(execute_program(proposal.program, train[held_index][0]))
        except (Undefined, KeyError, TypeError, ValueError, IndexError, ZeroDivisionError):
            return False
        if prediction != train[held_index][1]:
            return False
    return True


def _transform_program(program: Mapping[str, Any], operation: str) -> Mapping[str, Any]:
    transformed = dict(program)
    if (
        program.get("operator") == "largest_component_horizontal_closure"
        and operation in {"rot90", "rot270"}
    ):
        transformed["axis"] = (
            "top_bottom" if program.get("axis") == "left_right" else "left_right"
        )
    return transformed


def _counterfactual_exact(proposal: Proposal, train: Sequence[Pair], limits: Limits) -> int:
    probes = 0
    for source, target in train:
        for operation in ("rot90", "flip_h"):
            if probes >= limits.max_counterfactuals:
                raise Undefined("counterfactual budget exhausted")
            transformed_source = _d4(source, operation)
            transformed_target = _d4(target, operation)
            prediction = _grid(
                execute_program(
                    _transform_program(proposal.program, operation), transformed_source
                )
            )
            if prediction != transformed_target:
                raise Undefined("topology D4 counterfactual failed")
            probes += 1
    return probes


def compile_task(task: Any, limits: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    """Compile one uniquely supported topology behavior, or abstain."""

    try:
        bounds = Limits.parse(limits)
        train, tests = _sanitize(task, bounds)
        proposals = _enumerate(train, bounds)
        guarded: list[tuple[Proposal, tuple[Grid, ...], int]] = []
        for proposal in proposals:
            if not _loo_exact(proposal, train, bounds):
                continue
            try:
                probes = _counterfactual_exact(proposal, train, bounds)
                predictions = tuple(
                    _grid(execute_program(proposal.program, source)) for source in tests
                )
            except (Undefined, KeyError, TypeError, ValueError, IndexError, ZeroDivisionError):
                continue
            if all(prediction == source for prediction, source in zip(predictions, tests)):
                continue
            guarded.append((proposal, predictions, probes))
        if not guarded:
            return []
        behaviors: dict[str, list[tuple[Proposal, tuple[Grid, ...], int]]] = {}
        for item in guarded:
            behavior = _digest([_plain(output) for output in item[1]])
            behaviors.setdefault(behavior, []).append(item)
        if len(behaviors) != 1:
            return []
        behavior_hash, equivalent = next(iter(behaviors.items()))
        proposal, predictions, probes = min(
            equivalent,
            key=lambda item: (item[0].complexity, _canonical(item[0].program)),
        )
        return [
            {
                "family": proposal.family,
                "program": dict(proposal.program),
                "train_outputs": [_plain(target) for _, target in train],
                "test_outputs": [_plain(output) for output in predictions],
                "complexity": proposal.complexity,
                "evidence": {
                    "author": AUTHOR,
                    "all_demonstrations_exact": True,
                    "leave_one_demonstration_out_exact": True,
                    "loo_mode": "isolated_reproposal_then_held_execution",
                    "d4_counterfactual_exact": True,
                    "counterfactual_families": ["rot90_covariance", "horizontal_reflection_covariance"],
                    "counterfactual_probe_count": probes,
                    "bounded_program_enumeration": True,
                    "program_attempt_cap": bounds.max_programs,
                    "bounded_cross_exact_cover": True,
                    "cross_partition_state_cap": bounds.max_partition_states,
                    "unique_test_behavior": True,
                    "equivalent_guarded_program_count": len(equivalent),
                    "ambiguity_abstention": True,
                    "test_access": "input_key_only",
                    "task_identity_access": "none",
                    "behavior_hash": behavior_hash,
                },
            }
        ][: bounds.max_candidates]
    except (Undefined, KeyError, TypeError, ValueError, IndexError, ZeroDivisionError):
        return []


__all__ = ["Limits", "compile_task", "execute_program", "replay_program"]
