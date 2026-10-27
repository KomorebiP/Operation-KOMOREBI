"""Finite relational repair programs for same-canvas ARC transformations.

The entrant derives a small executable program from demonstrations.  Its
programs remove or repair cells only through palette-relative roles,
object-local coordinates, containment relations, and region geometry.  The
finite grammar contains no task identities, absolute resolved coordinates, or
literal color labels.  A task activates only when every demonstration replays
exactly, every leave-one-demonstration-out version space predicts the omitted
pair uniquely, and the complete version space has one held-out behavior.

Author: Komorebi P.
"""
from __future__ import annotations

import argparse
from collections import Counter, deque
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any


Grid = tuple[tuple[int, ...], ...]
Cell = tuple[int, int]
Pair = tuple[Grid, Grid]
SCHEMA = "komorebi.pr_lasm.block14.relational_subtractive_repair.program.v1"
SCAN_SCHEMA = "komorebi.pr_lasm.block14.relational_subtractive_repair.scan_freeze.v1"
AUTHOR = "Komorebi P."
ORTHOGONAL: tuple[Cell, ...] = ((-1, 0), (0, -1), (0, 1), (1, 0))
OCTAGONAL: tuple[Cell, ...] = tuple(
    (dr, dc)
    for dr in (-1, 0, 1)
    for dc in (-1, 0, 1)
    if (dr, dc) != (0, 0)
)


class Undefined(ValueError):
    """The requested palette or geometry role is absent, tied, or unsafe."""


@dataclass(frozen=True, slots=True)
class Limits:
    max_grid_cells: int = 900
    max_examples: int = 10
    max_components: int = 256
    max_programs: int = 128
    max_executor_calls: int = 8_192
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
            "max_examples": 20,
            "max_components": 900,
            "max_programs": 512,
            "max_executor_calls": 100_000,
            "max_candidates": 1,
        }
        normalized: dict[str, int] = {}
        for name in cls.__dataclass_fields__:
            fallback = value.get("candidate_cap", getattr(defaults, name)) if name == "max_candidates" else getattr(defaults, name)
            raw = value.get(name, fallback)
            if isinstance(raw, bool) or not isinstance(raw, int) or raw < 1:
                raise Undefined(f"limits.{name} must be a positive integer")
            normalized[name] = min(raw, ceilings[name])
        return cls(**normalized)


@dataclass(frozen=True, slots=True)
class Component:
    color: int
    cells: frozenset[Cell]
    bbox: tuple[int, int, int, int]

    @property
    def area(self) -> int:
        return len(self.cells)


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _plain(grid: Grid) -> list[list[int]]:
    return [list(row) for row in grid]


def _shape(grid: Grid) -> tuple[int, int]:
    return len(grid), len(grid[0])


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
                raise Undefined("ARC color must be an integer in [0, 9]")
            row.append(int(raw_cell))
        if width is None:
            width = len(row)
        elif len(row) != width:
            raise Undefined("grid is ragged")
        rows.append(tuple(row))
    if len(rows) * int(width or 0) > limits.max_grid_cells:
        raise Undefined("grid exceeds the finite cell cap")
    return tuple(rows)


def _sanitize(task: Any, limits: Limits) -> tuple[tuple[Pair, ...], tuple[Grid, ...]]:
    if not isinstance(task, Mapping):
        raise Undefined("task must be a mapping")
    train, test = task.get("train"), task.get("test")
    if (
        not isinstance(train, Sequence)
        or isinstance(train, (str, bytes))
        or len(train) < 2
        or not isinstance(test, Sequence)
        or isinstance(test, (str, bytes))
        or not test
        or len(train) + len(test) > limits.max_examples
    ):
        raise Undefined("task arity is outside the finite contract")
    demonstrations: list[Pair] = []
    for example in train:
        if not isinstance(example, Mapping):
            raise Undefined("demonstration must be a mapping")
        source = _grid(example.get("input"), limits)
        target = _grid(example.get("output"), limits)
        if _shape(source) != _shape(target) or source == target:
            raise Undefined("repair requires a changed same-canvas pair")
        demonstrations.append((source, target))
    tests: list[Grid] = []
    for example in test:
        if not isinstance(example, Mapping):
            raise Undefined("test example must be a mapping")
        tests.append(_grid(example.get("input"), limits))
    return tuple(demonstrations), tuple(tests)


def _unique_mode(values: Sequence[int] | list[int]) -> int:
    counts = Counter(values)
    if not counts:
        raise Undefined("empty palette role")
    maximum = max(counts.values())
    winners = sorted(color for color, count in counts.items() if count == maximum)
    if len(winners) != 1:
        raise Undefined("palette role is tied")
    return winners[0]


def _unique_minority(values: Sequence[int] | list[int]) -> int:
    counts = Counter(values)
    if len(counts) < 2:
        raise Undefined("minority role requires multiple colors")
    minimum = min(counts.values())
    winners = sorted(color for color, count in counts.items() if count == minimum)
    if len(winners) != 1:
        raise Undefined("minority role is tied")
    return winners[0]


def _background(grid: Grid, role: str) -> int:
    height, width = _shape(grid)
    if role == "mode":
        return _unique_mode([cell for row in grid for cell in row])
    if role == "border_mode":
        return _unique_mode(
            [
                grid[row][column]
                for row in range(height)
                for column in range(width)
                if row in {0, height - 1} or column in {0, width - 1}
            ]
        )
    if role == "corners":
        corners = [grid[0][0], grid[0][-1], grid[-1][0], grid[-1][-1]]
        if len(set(corners)) != 1:
            raise Undefined("corner background is not unique")
        return corners[0]
    raise Undefined("unknown background role")


def _bbox(cells: Sequence[Cell] | frozenset[Cell] | set[Cell]) -> tuple[int, int, int, int]:
    if not cells:
        raise Undefined("empty component")
    return (
        min(row for row, _ in cells),
        max(row for row, _ in cells),
        min(column for _, column in cells),
        max(column for _, column in cells),
    )


def _components(
    grid: Grid,
    *,
    background: int,
    connectivity: int,
    merge_colors: bool,
    limits: Limits,
) -> tuple[Component, ...]:
    height, width = _shape(grid)
    directions = ORTHOGONAL if connectivity == 4 else OCTAGONAL
    remaining = {
        (row, column)
        for row in range(height)
        for column in range(width)
        if grid[row][column] != background
    }
    found: list[Component] = []
    while remaining:
        seed = min(remaining)
        seed_color = grid[seed[0]][seed[1]]
        remaining.remove(seed)
        cells = {seed}
        queue = deque([seed])
        while queue:
            row, column = queue.popleft()
            for dr, dc in directions:
                point = row + dr, column + dc
                if point not in remaining:
                    continue
                if not merge_colors and grid[point[0]][point[1]] != seed_color:
                    continue
                remaining.remove(point)
                cells.add(point)
                queue.append(point)
        if len(found) >= limits.max_components:
            raise Undefined("component cap exhausted")
        found.append(Component(seed_color, frozenset(cells), _bbox(cells)))
    return tuple(sorted(found, key=lambda item: (item.bbox, item.color, item.area)))


def _mutable(grid: Grid) -> list[list[int]]:
    return [list(row) for row in grid]


def _frozen(grid: list[list[int]]) -> Grid:
    return tuple(tuple(row) for row in grid)


def _object_strip(program: Mapping[str, Any], grid: Grid, limits: Limits) -> Grid:
    background = _background(grid, str(program["background_role"]))
    side = str(program["side"])
    thickness = int(program["thickness"])
    components = _components(
        grid,
        background=background,
        connectivity=4,
        merge_colors=False,
        limits=limits,
    )
    if len(components) < 2:
        raise Undefined("strip repair requires an object cohort")
    output = _mutable(grid)
    changed = 0
    for component in components:
        row0, row1, column0, column1 = component.bbox
        for row, column in component.cells:
            selected = {
                "top": row < row0 + thickness,
                "bottom": row > row1 - thickness,
                "left": column < column0 + thickness,
                "right": column > column1 - thickness,
            }.get(side)
            if selected is None:
                raise Undefined("unknown strip side")
            if selected:
                output[row][column] = background
                changed += 1
    if changed == 0:
        raise Undefined("strip selected no cells")
    return _frozen(output)


def _checker_carve(program: Mapping[str, Any], grid: Grid, limits: Limits) -> Grid:
    background = _background(grid, str(program["background_role"]))
    phase = int(program["phase"])
    components = _components(
        grid,
        background=background,
        connectivity=4,
        merge_colors=False,
        limits=limits,
    )
    if not components:
        raise Undefined("checker carving found no rectangles")
    output = _mutable(grid)
    changed = 0
    for component in components:
        row0, row1, column0, column1 = component.bbox
        height, width = row1 - row0 + 1, column1 - column0 + 1
        if height < 3 or width < 3 or component.area != height * width:
            raise Undefined("checker carving requires solid rectangles")
        for row in range(row0 + 1, row1):
            for column in range(column0 + 1, column1):
                if ((row - row0) + (column - column0)) % 2 == phase:
                    output[row][column] = background
                    changed += 1
    if changed == 0:
        raise Undefined("checker carving selected no cells")
    return _frozen(output)


def _partition_defect_lines(program: Mapping[str, Any], grid: Grid, limits: Limits) -> Grid:
    del program, limits
    height, width = _shape(grid)
    defect = _unique_minority([cell for row in grid for cell in row])
    region_colors = sorted({cell for row in grid for cell in row} - {defect})
    if not region_colors:
        raise Undefined("partition has no region colors")
    boxes: list[tuple[int, int, int, int, tuple[Cell, ...]]] = []
    total_defects = 0
    for color in region_colors:
        cells = [
            (row, column)
            for row in range(height)
            for column in range(width)
            if grid[row][column] == color
        ]
        row0, row1, column0, column1 = _bbox(cells)
        box = [
            (row, column)
            for row in range(row0, row1 + 1)
            for column in range(column0, column1 + 1)
        ]
        if any(grid[row][column] not in {color, defect} for row, column in box):
            raise Undefined("partition color does not define a clean rectangle")
        if len(cells) * 10 < len(box) * 7:
            raise Undefined("partition rectangle is too sparse")
        box_height, box_width = row1 - row0 + 1, column1 - column0 + 1
        if box_height == box_width:
            raise Undefined("square partition has no unique line direction")
        defects = tuple((row, column) for row, column in box if grid[row][column] == defect)
        total_defects += len(defects)
        boxes.append((row0, row1, column0, column1, defects))
    if total_defects == 0:
        raise Undefined("partition contains no defects")
    output = _mutable(grid)
    for row0, row1, column0, column1, defects in boxes:
        if row1 - row0 < column1 - column0:
            for _, column in defects:
                for row in range(row0, row1 + 1):
                    output[row][column] = defect
        else:
            for row, _ in defects:
                for column in range(column0, column1 + 1):
                    output[row][column] = defect
    return _frozen(output)


def _contained_intruders(program: Mapping[str, Any], grid: Grid, limits: Limits) -> Grid:
    background = _background(grid, str(program["background_role"]))
    components = _components(
        grid,
        background=background,
        connectivity=8,
        merge_colors=False,
        limits=limits,
    )
    selected: set[Cell] = set()
    witnesses = 0
    for container in components:
        if container.area < 4:
            continue
        row0, row1, column0, column1 = container.bbox
        if row0 == row1 or column0 == column1:
            continue
        box = {
            (row, column)
            for row in range(row0, row1 + 1)
            for column in range(column0, column1 + 1)
        }
        for intruder in components:
            if intruder.color != container.color and intruder.cells <= box:
                selected.update(intruder.cells)
                witnesses += 1
    if not selected or witnesses == 0:
        # A nearly closed host can itself be the modal color (for example, a
        # compact frame with one boundary gap).  In that case the ordinary
        # background parse suppresses the host.  Recover the relation without
        # naming a color: the modal component must span the canvas, exactly one
        # nonmodal component must be strictly internal, and exactly one other
        # nonmodal color must provide a boundary gap.  The latter is the local
        # empty-space role used to remove the former.
        height, width = _shape(grid)
        modal = _unique_mode([cell for row in grid for cell in row])
        modal_cells = frozenset(
            (row, column)
            for row in range(height)
            for column in range(width)
            if grid[row][column] == modal
        )
        if _bbox(modal_cells) != (0, height - 1, 0, width - 1):
            raise Undefined("no fully contained intruder component")
        all_components: list[Component] = []
        for color in sorted({cell for row in grid for cell in row} - {modal}):
            mask_grid = tuple(
                tuple(color if cell == color else modal for cell in row)
                for row in grid
            )
            all_components.extend(
                _components(
                    mask_grid,
                    background=modal,
                    connectivity=8,
                    merge_colors=False,
                    limits=limits,
                )
            )
        internal = [
            component
            for component in all_components
            if all(0 < row < height - 1 and 0 < column < width - 1 for row, column in component.cells)
        ]
        boundary = [
            component
            for component in all_components
            if any(row in {0, height - 1} or column in {0, width - 1} for row, column in component.cells)
        ]
        if len(internal) != 1 or len(boundary) != 1 or internal[0].color == boundary[0].color:
            raise Undefined("modal-frame fallback is ambiguous")
        output = _mutable(grid)
        for row, column in internal[0].cells:
            output[row][column] = boundary[0].color
        return _frozen(output)
    output = _mutable(grid)
    for row, column in selected:
        output[row][column] = background
    return _frozen(output)


def _host_occlusion_repair(program: Mapping[str, Any], grid: Grid, limits: Limits) -> Grid:
    background = _background(grid, str(program["background_role"]))
    height, width = _shape(grid)
    frequencies = Counter(cell for row in grid for cell in row)
    assignments: dict[Cell, int] = {}
    intrusion_colors: set[int] = set()
    for row in range(height):
        for column in range(width):
            source = grid[row][column]
            if source == background:
                continue
            neighbors = Counter(
                grid[row + dr][column + dc]
                for dr, dc in ORTHOGONAL
                if 0 <= row + dr < height
                and 0 <= column + dc < width
                and grid[row + dr][column + dc] not in {background, source}
            )
            hosts = sorted(
                color
                for color, count in neighbors.items()
                if count >= 2 and frequencies[source] < frequencies[color]
            )
            if len(hosts) == 1:
                assignments[(row, column)] = hosts[0]
                intrusion_colors.add(source)
    if not assignments:
        raise Undefined("no locally bracketed minority occlusion")
    output = _mutable(grid)
    for row in range(height):
        for column in range(width):
            if output[row][column] in intrusion_colors:
                output[row][column] = background
    for (row, column), color in assignments.items():
        output[row][column] = color
    return _frozen(output)


def _seeded_x_frames(program: Mapping[str, Any], grid: Grid, limits: Limits) -> Grid:
    background = _background(grid, str(program["background_role"]))
    height, width = _shape(grid)
    regions = _components(
        grid,
        background=background,
        connectivity=4,
        merge_colors=True,
        limits=limits,
    )
    if not regions:
        raise Undefined("no seeded frame region")
    parsed: list[tuple[int, int, int, int, int, int]] = []
    for region in regions:
        row0, row1, column0, column1 = region.bbox
        box_height, box_width = row1 - row0 + 1, column1 - column0 + 1
        if box_height < 5 or box_width < 5 or region.area != box_height * box_width:
            raise Undefined("seeded frame input must be a filled rectangle")
        counts = Counter(grid[row][column] for row, column in region.cells)
        if len(counts) != 2:
            raise Undefined("seeded frame requires exactly two colors")
        ordered = counts.most_common()
        host, host_count = ordered[0]
        seed, seed_count = ordered[1]
        if seed_count != 1 or host_count != region.area - 1:
            raise Undefined("seeded frame minority must be a singleton")
        parsed.append((row0, row1, column0, column1, host, seed))
    output = [[background for _ in range(width)] for _ in range(height)]
    for row0, row1, column0, column1, host, seed in parsed:
        box_height, box_width = row1 - row0 + 1, column1 - column0 + 1
        inner_height, inner_width = box_height - 2, box_width - 2
        for row in range(row0, row1 + 1):
            for column in range(column0, column1 + 1):
                local_row, local_column = row - row0, column - column0
                if local_row in {0, box_height - 1} or local_column in {0, box_width - 1}:
                    output[row][column] = host
                    continue
                inner_row, inner_column = local_row - 1, local_column - 1
                depth = min(inner_row, inner_height - 1 - inner_row, (inner_width - 1) // 2)
                left, right = depth, inner_width - 1 - depth
                on_diagonal = inner_column in {left, right}
                on_short_axis_bridge = inner_row == inner_height - 1 - inner_row and left <= inner_column <= right
                if on_diagonal or on_short_axis_bridge:
                    output[row][column] = seed
    return _frozen(output)


def _regular_lattice(program: Mapping[str, Any], grid: Grid, limits: Limits) -> Grid:
    background = _background(grid, str(program["background_role"]))
    height, width = _shape(grid)
    foreground = sorted({cell for row in grid for cell in row} - {background})
    if len(foreground) != 2:
        raise Undefined("lattice repair requires two foreground roles")
    candidates: list[Grid] = []
    for base in foreground:
        marker = next(color for color in foreground if color != base)
        rows = tuple(
            row
            for row in range(height)
            if sum(grid[row][column] == base for column in range(width)) >= max(2, width // 2)
        )
        columns = tuple(
            column
            for column in range(width)
            if sum(grid[row][column] == base for row in range(height)) >= max(2, height // 2)
        )
        if len(rows) < 2 or not columns:
            continue
        output = [[background for _ in range(width)] for _ in range(height)]
        for row in rows:
            for column in range(width):
                output[row][column] = base
        for column in columns:
            for row in range(height):
                output[row][column] = base
        for row in rows:
            for column in columns:
                output[row][column] = marker
        candidates.append(_frozen(output))
    unique = sorted(set(candidates), key=_canonical)
    if len(unique) != 1:
        raise Undefined("lattice role is absent or behaviorally ambiguous")
    return unique[0]


EXECUTORS = {
    "object_local_strip": _object_strip,
    "solid_rectangle_checker_carve": _checker_carve,
    "partition_defect_line_extension": _partition_defect_lines,
    "contained_intruder_erasure": _contained_intruders,
    "host_occlusion_repair": _host_occlusion_repair,
    "seeded_x_frame_carve": _seeded_x_frames,
    "regular_lattice_cleanup": _regular_lattice,
}


def _programs(limits: Limits) -> tuple[dict[str, Any], ...]:
    programs: list[dict[str, Any]] = []
    for background_role in ("mode", "border_mode", "corners"):
        for side in ("top", "bottom", "left", "right"):
            for thickness in range(1, 5):
                programs.append(
                    {
                        "schema": SCHEMA,
                        "macro": "object_local_strip",
                        "background_role": background_role,
                        "side": side,
                        "thickness": thickness,
                        "description_length": 8 + thickness,
                    }
                )
        for phase in (0, 1):
            programs.append(
                {
                    "schema": SCHEMA,
                    "macro": "solid_rectangle_checker_carve",
                    "background_role": background_role,
                    "phase": phase,
                    "description_length": 12,
                }
            )
        for macro, length in (
            ("contained_intruder_erasure", 14),
            ("host_occlusion_repair", 16),
            ("seeded_x_frame_carve", 18),
            ("regular_lattice_cleanup", 18),
        ):
            programs.append(
                {
                    "schema": SCHEMA,
                    "macro": macro,
                    "background_role": background_role,
                    "description_length": length,
                }
            )
    programs.append(
        {
            "schema": SCHEMA,
            "macro": "partition_defect_line_extension",
            "defect_role": "unique_global_minority",
            "description_length": 14,
        }
    )
    programs.sort(key=lambda item: (int(item["description_length"]), _canonical(item)))
    if len(programs) > limits.max_programs:
        raise Undefined("program enumeration cap exhausted")
    return tuple(programs)


def _execute_internal(program: Mapping[str, Any], grid: Grid, limits: Limits) -> Grid:
    if not isinstance(program, Mapping) or program.get("schema") != SCHEMA:
        raise Undefined("program schema mismatch")
    macro = program.get("macro")
    executor = EXECUTORS.get(str(macro))
    if executor is None:
        raise Undefined("unknown repair macro")
    output = executor(program, grid, limits)
    if _shape(output) != _shape(grid) or output == grid:
        raise Undefined("program did not produce a changed same-canvas output")
    return output


def execute_program(program: Mapping[str, Any], value: Any, limits: Mapping[str, Any] | None = None) -> list[list[int]]:
    bounds = Limits.from_value(limits)
    grid = _grid(value, bounds)
    return _plain(_execute_internal(program, grid, bounds))


def replay_program(program: Mapping[str, Any], value: Any) -> dict[str, Any]:
    bounds = Limits()
    source = _grid(value, bounds)
    target = _execute_internal(program, source, bounds)
    plain_source, plain_target = _plain(source), _plain(target)
    return {
        "output": plain_target,
        "stages": [
            {"name": "parse-relational-scene", "input": plain_source, "output": plain_source},
            {"name": f"apply-{program['macro']}", "input": plain_source, "output": plain_target},
            {"name": "preserve-canvas-and-emit", "input": plain_target, "output": plain_target},
        ],
    }


def _fit(program: Mapping[str, Any], demonstrations: Sequence[Pair], limits: Limits, calls: list[int]) -> bool:
    for source, target in demonstrations:
        calls[0] += 1
        if calls[0] > limits.max_executor_calls:
            raise Undefined("executor call cap exhausted")
        try:
            prediction = _execute_internal(program, source, limits)
        except Undefined:
            return False
        if prediction != target:
            return False
    return True


def _exact_programs(demonstrations: Sequence[Pair], limits: Limits, calls: list[int]) -> tuple[dict[str, Any], ...]:
    return tuple(program for program in _programs(limits) if _fit(program, demonstrations, limits, calls))


def _behavior(program: Mapping[str, Any], inputs: Sequence[Grid], limits: Limits, calls: list[int]) -> tuple[Grid, ...]:
    outputs: list[Grid] = []
    for grid in inputs:
        calls[0] += 1
        if calls[0] > limits.max_executor_calls:
            raise Undefined("executor call cap exhausted")
        outputs.append(_execute_internal(program, grid, limits))
    return tuple(outputs)


def _leave_one_out(demonstrations: Sequence[Pair], limits: Limits, calls: list[int]) -> tuple[bool, int, list[int]]:
    class_counts: list[int] = []
    checks = 0
    for omitted in range(len(demonstrations)):
        retained = tuple(pair for index, pair in enumerate(demonstrations) if index != omitted)
        programs = _exact_programs(retained, limits, calls)
        if not programs:
            return False, checks, class_counts
        source, target = demonstrations[omitted]
        predictions: set[Grid] = set()
        for program in programs:
            try:
                predictions.update(_behavior(program, (source,), limits, calls))
            except Undefined:
                continue
        checks += len(programs)
        class_counts.append(len(predictions))
        if predictions != {target}:
            return False, checks, class_counts
    return True, checks, class_counts


def compile_task(task: Any, limits: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    """Compile one unique finite repair behavior, or abstain."""

    try:
        bounds = Limits.from_value(limits)
        demonstrations, tests = _sanitize(task, bounds)
        calls = [0]
        exact = _exact_programs(demonstrations, bounds, calls)
        if not exact:
            return []
        behaviors: dict[str, list[tuple[dict[str, Any], tuple[Grid, ...]]]] = {}
        for program in exact:
            try:
                outputs = _behavior(program, tests, bounds, calls)
            except Undefined:
                continue
            behaviors.setdefault(_digest([_plain(grid) for grid in outputs]), []).append((program, outputs))
        if len(behaviors) != 1:
            return []
        behavior_hash, equivalent = next(iter(sorted(behaviors.items())))
        equivalent.sort(key=lambda item: (int(item[0]["description_length"]), _canonical(item[0])))
        representative, test_outputs = equivalent[0]
        loo_ok, loo_checks, loo_classes = _leave_one_out(demonstrations, bounds, calls)
        if not loo_ok:
            return []
        train_outputs = _behavior(representative, tuple(source for source, _ in demonstrations), bounds, calls)
        if train_outputs != tuple(target for _, target in demonstrations):
            return []
    except (Undefined, TypeError, ValueError, KeyError):
        return []
    candidate = {
        "family": "relational_subtractive_repair",
        "program": json.loads(_canonical(representative)),
        "train_outputs": [_plain(grid) for grid in train_outputs],
        "test_outputs": [_plain(grid) for grid in test_outputs],
        "complexity": int(representative["description_length"]),
        "evidence": {
            "all_demos_exact": True,
            "exact_replay": True,
            "leave_one_demo_out_reinduction": True,
            "leave_one_out_program_checks": loo_checks,
            "leave_one_out_behavior_classes": loo_classes,
            "finite_grammar_complete": True,
            "programs_enumerated": len(_programs(bounds)),
            "exact_programs": len(exact),
            "equivalent_test_programs": len(equivalent),
            "full_test_behavior_classes": len(behaviors),
            "full_test_behavior_hash": behavior_hash,
            "executor_calls": calls[0],
            "hard_caps_exhausted": False,
            "palette_roles_are_relative": True,
            "object_coordinates_are_local": True,
            "serialized_literal_colors": False,
            "serialized_resolved_coordinates": False,
            "task_identity_observed": False,
            "test_labels_observed": False,
            "external_labels_observed": False,
        },
    }
    candidate["evidence"]["candidate_semantic_hash"] = _digest(candidate)
    return [candidate][: bounds.max_candidates]


def _safe_task(task: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(task, Mapping) or not isinstance(task.get("train"), list) or not isinstance(task.get("test"), list):
        raise Undefined("task splits are malformed")
    return {
        "train": [
            {"input": example["input"], "output": example["output"]}
            for example in task["train"]
        ],
        "test": [{"input": example["input"]} for example in task["test"]],
    }


def freeze_scan(
    challenges: Mapping[str, Mapping[str, Any]],
    *,
    limits: Mapping[str, Any] | None = None,
    source_hash: str | None = None,
    entrant_source_hash: str | None = None,
    run_name: str = "relational-subtractive-repair-scan",
) -> dict[str, Any]:
    records: dict[str, Any] = {}
    activated = 0
    for raw_identity, task in sorted(challenges.items(), key=lambda item: str(item[0])):
        safe = _safe_task(task)
        candidates = compile_task(safe, limits=limits)
        if len(candidates) > 1:
            raise AssertionError("compile_task violated its one-candidate contract")
        activated += bool(candidates)
        record = {
            "task_semantic_hash": _digest(safe),
            "status": "candidate" if candidates else "abstention",
            "candidates": candidates,
        }
        record["content_hash"] = _digest(record)
        records[str(raw_identity)] = record
    body = {
        "schema": SCAN_SCHEMA,
        "schema_version": 1,
        "author": AUTHOR,
        "phase": "challenge_only_prediction_freeze",
        "label_access": "demonstrations_only",
        "run_name": run_name,
        "source_hash": source_hash,
        "entrant_source_hash": entrant_source_hash,
        "source_task_count": len(challenges),
        "activation_count": activated,
        "records": records,
        "claim_boundary": (
            "Programs use demonstration pairs and sanitized test inputs only. "
            "No external answer labels or performance records are consulted."
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
    parser.add_argument("--run-name", default="relational-subtractive-repair-scan")
    args = parser.parse_args(argv)
    raw = args.challenges.read_bytes()
    challenges = json.loads(raw.decode("utf-8-sig"))
    if not isinstance(challenges, Mapping):
        raise ValueError("challenge file must contain an object")
    frozen = freeze_scan(
        challenges,
        source_hash=hashlib.sha256(raw).hexdigest(),
        entrant_source_hash=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
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
    "Limits",
    "SCHEMA",
    "Undefined",
    "compile_task",
    "execute_program",
    "freeze_scan",
    "replay_program",
]


if __name__ == "__main__":
    raise SystemExit(main())
