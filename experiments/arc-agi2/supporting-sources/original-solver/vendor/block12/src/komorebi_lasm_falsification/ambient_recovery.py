"""Locked recovery grammar for four rejected Block 11 ambient families.

The broad ``component_corridors``, ``object_bbox_fill``, ``crop_container``,
and ``span_closure`` families were unsafe.  This module does not restore those
families.  It replaces them with nine disjoint action schemas whose observable
effect coordinates survived a complete 499-task label-blind freeze followed
by separate scoring.

Every candidate is inferred only from training demonstrations and test inputs,
must replay all demonstrations exactly, must pass a transpose-conjugacy probe,
and enters the policy only when every executable program has one exact-raster
test behavior.  Ambiguity and incomplete work are abstentions.

Author: Komorebi P.
"""
from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass
import hashlib
import json
from typing import Any, Iterable, Mapping, Sequence

from komorebi_lasm_composition.task import sanitized_task_mapping
from komorebi_lasm_transfer.ambient_topology import (
    Grid,
    Inapplicable,
    ObjectPacket,
    bounding_box,
    objects,
    rectangle_frames,
    shape,
    thaw,
    validate_grid,
)


SCHEMA_VERSION = 1
MAXIMUM_PROGRAMS = 128
PROGRAM_SCHEMA = "komorebi.lasm_falsification.ambient_recovery_program"
COMPILATION_SCHEMA = "komorebi.lasm_falsification.ambient_recovery_compilation"
ORTHOGONAL = ((-1, 0), (1, 0), (0, -1), (0, 1))
KING = tuple(
    (delta_row, delta_column)
    for delta_row in (-1, 0, 1)
    for delta_column in (-1, 0, 1)
    if (delta_row, delta_column) != (0, 0)
)

STABLE_FAMILIES = frozenset({
    "corridor_anchor_markers",
    "corridor_same_color_closure",
    "corridor_singleton_graph",
    "crop_modal_largest_frame_hole",
    "span_same_color_closure",
})
PROVISIONAL_FAMILIES = frozenset({
    "bbox_count_conserved_diagonal",
    "bbox_l_tromino_completion",
    "bbox_single_object_completion",
    "span_diagonal_closure",
})
SAFE_FAMILIES = STABLE_FAMILIES | PROVISIONAL_FAMILIES
REJECTED_BROAD_FAMILIES = frozenset({
    "component_corridors", "object_bbox_fill", "crop_container", "span_closure",
})
_FAMILY_COSTS = {
    "corridor_same_color_closure": 6,
    "corridor_singleton_graph": 6,
    "corridor_anchor_markers": 7,
    "span_same_color_closure": 5,
    "span_diagonal_closure": 7,
    "bbox_l_tromino_completion": 6,
    "bbox_single_object_completion": 6,
    "bbox_count_conserved_diagonal": 8,
    "crop_modal_largest_frame_hole": 6,
}


class ContractError(ValueError):
    """A program lies outside the frozen grammar contract."""


def canonical_json(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        allow_nan=False,
    )


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def modal_background(grid: Grid) -> int:
    counts = Counter(value for row in grid for value in row)
    maximum = max(counts.values())
    winners = [color for color, count in counts.items() if count == maximum]
    if len(winners) != 1:
        raise Inapplicable("modal background is ambiguous")
    return winners[0]


@dataclass(frozen=True, slots=True)
class AmbientRecoveryProgram:
    family: str
    parameters: tuple[tuple[str, Any], ...]
    cost: int
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.family not in SAFE_FAMILIES:
            raise ContractError("family is outside the locked ambient-recovery grammar")
        if self.schema_version != SCHEMA_VERSION or self.cost != _FAMILY_COSTS[self.family]:
            raise ContractError("program version or cost disagrees with the grammar")
        if self.parameters != tuple(sorted(self.parameters)):
            raise ContractError("parameters must use canonical key order")
        params = self.parameter_map
        if len(params) != len(self.parameters):
            raise ContractError("parameter keys must be unique")
        keys = {
            "corridor_same_color_closure": {"intersection_priority"},
            "corridor_singleton_graph": {"paint_color"},
            "corridor_anchor_markers": set(),
            "span_same_color_closure": {"axis", "paint_mode", "paint_color"},
            "span_diagonal_closure": {"paint_mode", "paint_color"},
            "bbox_l_tromino_completion": {"connectivity", "selector", "paint_color"},
            "bbox_single_object_completion": {"connectivity", "selector", "paint_color"},
            "bbox_count_conserved_diagonal": {"connectivity", "selector", "paint_color"},
            "crop_modal_largest_frame_hole": set(),
        }[self.family]
        if set(params) != keys:
            raise ContractError("parameter domain disagrees with the family")
        if "paint_color" in params:
            color = params["paint_color"]
            if isinstance(color, bool) or not isinstance(color, int) or not -1 <= color <= 9:
                raise ContractError("paint color lies outside the finite domain")
        if self.family == "corridor_same_color_closure" and params["intersection_priority"] not in {
            "horizontal", "vertical"
        }:
            raise ContractError("unknown crossing priority")
        if self.family.startswith("span_"):
            if params["paint_mode"] not in {"endpoint", "literal"}:
                raise ContractError("unknown span paint mode")
            if (params["paint_mode"] == "endpoint") != (params["paint_color"] == -1):
                raise ContractError("span paint role and color disagree")
        elif "paint_color" in params and params["paint_color"] < 0:
            raise ContractError("non-span paint colors must be raster colors")
        if self.family == "span_same_color_closure" and params["axis"] not in {
            "row", "column", "both"
        }:
            raise ContractError("unknown span axis")
        bbox_contracts = {
            "bbox_l_tromino_completion": (4, "all_l_trominoes"),
            "bbox_single_object_completion": (4, "single"),
            "bbox_count_conserved_diagonal": (8, "all_count_conserved"),
        }
        if self.family in bbox_contracts and (
            params["connectivity"], params["selector"]
        ) != bbox_contracts[self.family]:
            raise ContractError("bbox coordinates disagree with the family")

    @classmethod
    def create(cls, family: str, **parameters: Any) -> "AmbientRecoveryProgram":
        if family not in _FAMILY_COSTS:
            raise ContractError("family is outside the locked ambient-recovery grammar")
        return cls(family, tuple(sorted(parameters.items())), _FAMILY_COSTS[family])

    @property
    def parameter_map(self) -> dict[str, Any]:
        return dict(self.parameters)

    @property
    def provisional(self) -> bool:
        return self.family in PROVISIONAL_FAMILIES

    @property
    def program_id(self) -> str:
        return digest(self.to_record(include_id=False))

    def to_record(self, *, include_id: bool = True) -> dict[str, Any]:
        record: dict[str, Any] = {
            "schema": PROGRAM_SCHEMA,
            "schema_version": self.schema_version,
            "family": self.family,
            "parameters": dict(self.parameters),
            "cost": self.cost,
            "status": "provisional" if self.provisional else "stable",
        }
        if include_id:
            record["program_id"] = self.program_id
        return record


def _effect_coordinate(pairs: Sequence[tuple[Grid, Grid]]) -> dict[str, Any]:
    if not all(shape(source) == shape(target) for source, target in pairs):
        return {
            "kind": "shape_reduction",
            "source_shapes": [list(shape(source)) for source, _ in pairs],
            "target_shapes": [list(shape(target)) for _, target in pairs],
        }
    added_colors: set[int] = set()
    changed_counts: list[int] = []
    for source, target in pairs:
        try:
            bg = modal_background(source)
        except (Inapplicable, TypeError, ValueError):
            return {"kind": "ambiguous_background"}
        changed = 0
        for row in range(len(source)):
            for column in range(len(source[0])):
                before, after = source[row][column], target[row][column]
                if before == after:
                    continue
                changed += 1
                if before != bg or after == bg:
                    return {"kind": "mixed_same_shape"}
                added_colors.add(after)
        if changed == 0:
            return {"kind": "identity"}
        changed_counts.append(changed)
    return {
        "kind": "support_addition",
        "added_colors": sorted(added_colors),
        "changed_counts": changed_counts,
    }


def _aligned_corridor(first: ObjectPacket, second: ObjectPacket) -> tuple[str, frozenset[tuple[int, int]]]:
    result: set[tuple[int, int]] = set()
    axis = ""
    row_low, row_high = max(first.top, second.top), min(first.bottom, second.bottom)
    if row_low <= row_high:
        if first.right < second.left:
            axis = "horizontal"
            result.update(
                (row, column)
                for row in range(row_low, row_high + 1)
                for column in range(first.right + 1, second.left)
            )
        elif second.right < first.left:
            axis = "horizontal"
            result.update(
                (row, column)
                for row in range(row_low, row_high + 1)
                for column in range(second.right + 1, first.left)
            )
    column_low, column_high = max(first.left, second.left), min(first.right, second.right)
    if column_low <= column_high:
        if first.bottom < second.top:
            if axis:
                raise Inapplicable("corridor axis is ambiguous")
            axis = "vertical"
            result.update(
                (row, column)
                for row in range(first.bottom + 1, second.top)
                for column in range(column_low, column_high + 1)
            )
        elif second.bottom < first.top:
            if axis:
                raise Inapplicable("corridor axis is ambiguous")
            axis = "vertical"
            result.update(
                (row, column)
                for row in range(second.bottom + 1, first.top)
                for column in range(column_low, column_high + 1)
            )
    return axis, frozenset(result)


def _execute_same_color_corridors(program: AmbientRecoveryProgram, grid: Grid) -> Grid:
    bg = modal_background(grid)
    packets = objects(grid, bg)
    proposals: dict[tuple[int, int], list[tuple[str, int]]] = {}
    for index, first in enumerate(packets):
        for second in packets[index + 1:]:
            if first.color != second.color:
                continue
            axis, corridor = _aligned_corridor(first, second)
            for cell in corridor:
                proposals.setdefault(cell, []).append((axis, first.color))
    if not proposals:
        raise Inapplicable("same-color closure has no corridors")
    priority = program.parameter_map["intersection_priority"]
    canvas = thaw(grid)
    changed = 0
    for (row, column), candidates in sorted(proposals.items()):
        colors = {color for _, color in candidates}
        if len(colors) == 1:
            color = next(iter(colors))
        else:
            preferred = {color for axis, color in candidates if axis == priority}
            if len(preferred) != 1:
                raise Inapplicable("crossing priority does not resolve color")
            color = next(iter(preferred))
        if canvas[row][column] == bg:
            canvas[row][column] = color
            changed += 1
    if changed == 0:
        raise Inapplicable("same-color corridor closure is a no-op")
    return validate_grid(canvas)


def _execute_singleton_graph(program: AmbientRecoveryProgram, grid: Grid) -> Grid:
    bg = modal_background(grid)
    packets = objects(grid, bg)
    if not packets or any(packet.area != 1 for packet in packets):
        raise Inapplicable("singleton graph contains a nonsingleton object")
    color = program.parameter_map["paint_color"]
    cells: set[tuple[int, int]] = set()
    for index, first in enumerate(packets):
        for second in packets[index + 1:]:
            _, corridor = _aligned_corridor(first, second)
            cells.update(corridor)
    if not cells:
        raise Inapplicable("singleton graph has no corridors")
    canvas = thaw(grid)
    changed = 0
    for row, column in cells:
        if canvas[row][column] == bg:
            canvas[row][column] = color
            changed += 1
    if changed == 0:
        raise Inapplicable("singleton graph is a no-op")
    return validate_grid(canvas)


def _execute_anchor_markers(grid: Grid) -> Grid:
    bg = modal_background(grid)
    packets = objects(grid, bg)
    if len(packets) < 2:
        raise Inapplicable("anchor corridors require at least two objects")
    maximum = max(packet.area for packet in packets)
    anchors = [packet for packet in packets if packet.area == maximum]
    if len(anchors) != 1 or maximum < 4:
        raise Inapplicable("anchor must be unique and sufficiently large")
    anchor = anchors[0]
    if anchor.area != anchor.height * anchor.width:
        raise Inapplicable("anchor must be a solid rectangle")
    markers = [packet for packet in packets if packet is not anchor]
    if not markers or any(marker.area != 1 for marker in markers):
        raise Inapplicable("non-anchor objects must be singleton markers")
    if anchor.color in {marker.color for marker in markers}:
        raise Inapplicable("marker colors must differ from the anchor")
    canvas = thaw(grid)
    changed = 0
    for marker in markers:
        _, corridor = _aligned_corridor(anchor, marker)
        for row, column in corridor:
            if canvas[row][column] == bg:
                canvas[row][column] = marker.color
                changed += 1
    if changed == 0:
        raise Inapplicable("anchor-marker closure is a no-op")
    return validate_grid(canvas)


def _line_segments(values: Sequence[int], bg: int) -> list[tuple[int, int, int]]:
    answer = []
    index = 0
    while index < len(values):
        if values[index] == bg:
            index += 1
            continue
        color = values[index]
        stop = index
        while stop + 1 < len(values) and values[stop + 1] == color:
            stop += 1
        answer.append((index, stop, color))
        index = stop + 1
    return answer


def _execute_same_color_span(program: AmbientRecoveryProgram, grid: Grid) -> Grid:
    params = program.parameter_map
    bg = modal_background(grid)
    canvas = thaw(grid)
    height, width = shape(grid)
    axes = ("row", "column") if params["axis"] == "both" else (params["axis"],)
    changed = 0
    for axis in axes:
        line_count = height if axis == "row" else width
        line_length = width if axis == "row" else height
        for line_index in range(line_count):
            values = [
                canvas[line_index][offset] if axis == "row" else canvas[offset][line_index]
                for offset in range(line_length)
            ]
            segments = _line_segments(values, bg)
            for left, right in zip(segments, segments[1:]):
                if left[2] != right[2] or left[1] + 1 >= right[0]:
                    continue
                color = left[2] if params["paint_mode"] == "endpoint" else params["paint_color"]
                for offset in range(left[1] + 1, right[0]):
                    row, column = (line_index, offset) if axis == "row" else (offset, line_index)
                    if canvas[row][column] == bg:
                        canvas[row][column] = color
                        changed += 1
    if changed == 0:
        raise Inapplicable("same-color span is a no-op")
    return validate_grid(canvas)


def _execute_diagonal_span(program: AmbientRecoveryProgram, grid: Grid) -> Grid:
    params = program.parameter_map
    bg = modal_background(grid)
    height, width = shape(grid)
    material = [
        (row, column, grid[row][column])
        for row in range(height)
        for column in range(width)
        if grid[row][column] != bg
    ]
    proposals: dict[tuple[int, int], set[int]] = {}
    for index, (first_row, first_column, first_color) in enumerate(material):
        for second_row, second_column, second_color in material[index + 1:]:
            delta_row = second_row - first_row
            delta_column = second_column - first_column
            if first_color != second_color or abs(delta_row) != abs(delta_column) or abs(delta_row) < 2:
                continue
            step_row = 1 if delta_row > 0 else -1
            step_column = 1 if delta_column > 0 else -1
            between = [
                (first_row + offset * step_row, first_column + offset * step_column)
                for offset in range(1, abs(delta_row))
            ]
            if any(grid[row][column] not in {bg, first_color} for row, column in between):
                continue
            color = first_color if params["paint_mode"] == "endpoint" else params["paint_color"]
            for cell in between:
                if grid[cell[0]][cell[1]] == bg:
                    proposals.setdefault(cell, set()).add(color)
    if not proposals:
        raise Inapplicable("diagonal span has no gaps")
    canvas = thaw(grid)
    for (row, column), colors in sorted(proposals.items()):
        if len(colors) != 1:
            raise Inapplicable("diagonal span has a color collision")
        canvas[row][column] = next(iter(colors))
    return validate_grid(canvas)


def _components(grid: Grid, bg: int, connectivity: int) -> tuple[frozenset[tuple[int, int]], ...]:
    height, width = shape(grid)
    steps = ORTHOGONAL if connectivity == 4 else KING
    answer: list[frozenset[tuple[int, int]]] = []
    for color in sorted({value for row in grid for value in row} - {bg}):
        remaining = {
            (row, column)
            for row in range(height)
            for column in range(width)
            if grid[row][column] == color
        }
        while remaining:
            seed = min(remaining)
            remaining.remove(seed)
            queue = deque((seed,))
            component = {seed}
            while queue:
                row, column = queue.popleft()
                for delta_row, delta_column in steps:
                    neighbor = row + delta_row, column + delta_column
                    if neighbor in remaining:
                        remaining.remove(neighbor)
                        component.add(neighbor)
                        queue.append(neighbor)
            answer.append(frozenset(component))
    return tuple(sorted(answer, key=lambda cells: (min(cells), len(cells))))


def _execute_bbox(program: AmbientRecoveryProgram, grid: Grid) -> Grid:
    params = program.parameter_map
    bg = modal_background(grid)
    packets = _components(grid, bg, params["connectivity"])
    if params["selector"] == "single":
        if len(packets) != 1:
            raise Inapplicable("single-object bbox requires one object")
    elif params["selector"] == "all_l_trominoes":
        if not packets:
            raise Inapplicable("L-tromino bbox has no objects")
        for cells in packets:
            top, left, bottom, right = bounding_box(cells)
            if len(cells) != 3 or bottom - top != 1 or right - left != 1:
                raise Inapplicable("every object must be an L tromino")
    elif params["selector"] == "all_count_conserved":
        if len(packets) < 2:
            raise Inapplicable("count-conserved bbox requires multiple objects")
    else:
        raise Inapplicable("unknown bbox selector")
    canvas = thaw(grid)
    changed = 0
    for cells in packets:
        top, left, bottom, right = bounding_box(cells)
        for row in range(top, bottom + 1):
            for column in range(left, right + 1):
                if canvas[row][column] == bg:
                    canvas[row][column] = params["paint_color"]
                    changed += 1
    if changed == 0:
        raise Inapplicable("bbox completion is a no-op")
    return validate_grid(canvas)


def _execute_crop(grid: Grid) -> Grid:
    bg = modal_background(grid)
    frames = rectangle_frames(grid, bg)
    if not frames:
        raise Inapplicable("crop has no frames")
    maximum = max(frame.area for frame in frames)
    selected = [frame for frame in frames if frame.area == maximum]
    if len(selected) != 1:
        raise Inapplicable("largest frame is not unique")
    frame = selected[0]
    result = tuple(
        tuple(grid[row][frame.left + 1:frame.right])
        for row in range(frame.top + 1, frame.bottom)
    )
    if not result or not result[0] or shape(result) == shape(grid):
        raise Inapplicable("crop is empty or a no-op")
    return validate_grid(result)


def execute_program(program: AmbientRecoveryProgram, grid_value: Any) -> Grid:
    grid = validate_grid(grid_value)
    if program.family == "corridor_same_color_closure":
        return _execute_same_color_corridors(program, grid)
    if program.family == "corridor_singleton_graph":
        return _execute_singleton_graph(program, grid)
    if program.family == "corridor_anchor_markers":
        return _execute_anchor_markers(grid)
    if program.family == "span_same_color_closure":
        return _execute_same_color_span(program, grid)
    if program.family == "span_diagonal_closure":
        return _execute_diagonal_span(program, grid)
    if program.family.startswith("bbox_"):
        return _execute_bbox(program, grid)
    if program.family == "crop_modal_largest_frame_hole":
        return _execute_crop(grid)
    raise Inapplicable("unknown ambient-recovery family")


def _count_conservation_gate(sources: Sequence[Grid], tests: Sequence[Grid]) -> bool:
    grids = tuple(sources) + tuple(tests)
    try:
        if any(
            len({value for row in grid for value in row} - {modal_background(grid)}) != 1
            for grid in grids
        ):
            return False
        train4 = [len(_components(grid, modal_background(grid), 4)) for grid in sources]
        train8 = [len(_components(grid, modal_background(grid), 8)) for grid in sources]
        test4 = [len(_components(grid, modal_background(grid), 4)) for grid in tests]
        test8 = [len(_components(grid, modal_background(grid), 8)) for grid in tests]
    except (Inapplicable, TypeError, ValueError):
        return False
    return (
        len(set(train8)) == 1
        and train8[0] >= 2
        and all(value == train8[0] for value in test8)
        and any(value != train8[0] for value in (*train4, *test4))
    )


def enumerate_programs(
    pairs: Sequence[tuple[Grid, Grid]], tests: Sequence[Grid]
) -> tuple[AmbientRecoveryProgram, ...]:
    effect = _effect_coordinate(pairs)
    sources = tuple(source for source, _ in pairs)
    programs: dict[str, AmbientRecoveryProgram] = {}

    def add(program: AmbientRecoveryProgram) -> None:
        programs[program.program_id] = program

    if effect["kind"] == "support_addition":
        colors = tuple(effect["added_colors"])
        for priority in ("horizontal", "vertical"):
            add(AmbientRecoveryProgram.create(
                "corridor_same_color_closure", intersection_priority=priority,
            ))
        add(AmbientRecoveryProgram.create("corridor_anchor_markers"))
        for color in colors:
            add(AmbientRecoveryProgram.create("corridor_singleton_graph", paint_color=color))
        for axis in ("row", "column", "both"):
            add(AmbientRecoveryProgram.create(
                "span_same_color_closure", axis=axis,
                paint_mode="endpoint", paint_color=-1,
            ))
            for color in colors:
                add(AmbientRecoveryProgram.create(
                    "span_same_color_closure", axis=axis,
                    paint_mode="literal", paint_color=color,
                ))
        add(AmbientRecoveryProgram.create(
            "span_diagonal_closure", paint_mode="endpoint", paint_color=-1,
        ))
        for color in colors:
            add(AmbientRecoveryProgram.create(
                "span_diagonal_closure", paint_mode="literal", paint_color=color,
            ))
            add(AmbientRecoveryProgram.create(
                "bbox_l_tromino_completion",
                connectivity=4, selector="all_l_trominoes", paint_color=color,
            ))
            add(AmbientRecoveryProgram.create(
                "bbox_single_object_completion",
                connectivity=4, selector="single", paint_color=color,
            ))
            if _count_conservation_gate(sources, tests):
                add(AmbientRecoveryProgram.create(
                    "bbox_count_conserved_diagonal",
                    connectivity=8, selector="all_count_conserved", paint_color=color,
                ))
    elif effect["kind"] == "shape_reduction":
        add(AmbientRecoveryProgram.create("crop_modal_largest_frame_hole"))
    return tuple(sorted(programs.values(), key=lambda program: (program.cost, program.program_id)))


def _transpose(grid: Grid) -> Grid:
    return tuple(tuple(grid[row][column] for row in range(len(grid))) for column in range(len(grid[0])))


def _transpose_program(program: AmbientRecoveryProgram) -> AmbientRecoveryProgram:
    params = program.parameter_map
    if program.family == "corridor_same_color_closure":
        params["intersection_priority"] = {
            "horizontal": "vertical", "vertical": "horizontal",
        }[params["intersection_priority"]]
    if program.family == "span_same_color_closure":
        params["axis"] = {"row": "column", "column": "row", "both": "both"}[params["axis"]]
    return AmbientRecoveryProgram.create(program.family, **params)


def _probe(program: AmbientRecoveryProgram, pairs: Sequence[tuple[Grid, Grid]]) -> tuple[bool, int]:
    transformed = _transpose_program(program)
    executions = 0
    for source, target in pairs:
        executions += 1
        try:
            prediction = execute_program(transformed, _transpose(source))
        except (AssertionError, IndexError, KeyError, RuntimeError, TypeError, ValueError):
            return False, executions
        if prediction != _transpose(target):
            return False, executions
    return True, executions


GRAMMAR_CONTRACT = {
    "schema": "komorebi.lasm_falsification.ambient_recovery_grammar",
    "schema_version": SCHEMA_VERSION,
    "stable_families": sorted(STABLE_FAMILIES),
    "provisional_families": sorted(PROVISIONAL_FAMILIES),
    "rejected_broad_families": sorted(REJECTED_BROAD_FAMILIES),
    "maximum_programs": MAXIMUM_PROGRAMS,
    "selection": "exact demo replay, transpose conjugacy, complete exact-raster quotient",
    "frozen_cohort": 499,
    "frozen_unique_exact": 14,
    "frozen_wrong": 0,
    "frozen_ambiguous": 0,
    "net_new_over_block11": 2,
}
GRAMMAR_HASH = digest(GRAMMAR_CONTRACT)


@dataclass(frozen=True, slots=True)
class AmbientRecoveryLimits:
    max_training_examples: int = 10
    max_test_examples: int = 10
    maximum_programs: int = MAXIMUM_PROGRAMS

    def __post_init__(self) -> None:
        for field in ("max_training_examples", "max_test_examples", "maximum_programs"):
            value = getattr(self, field)
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ValueError(f"{field} must be a positive integer")
        if self.maximum_programs != MAXIMUM_PROGRAMS:
            raise ValueError(f"maximum_programs is frozen at {MAXIMUM_PROGRAMS}")


@dataclass(frozen=True, slots=True)
class AmbientRecoveryBehavior:
    behavior_hash: str
    predictions: tuple[Grid, ...]
    programs: tuple[AmbientRecoveryProgram, ...]

    def __post_init__(self) -> None:
        if not self.programs:
            raise ValueError("a behavior requires at least one program")
        if self.behavior_hash != digest(self.predictions):
            raise ValueError("behavior hash does not authenticate predictions")
        if self.programs != tuple(sorted(
            self.programs, key=lambda program: (program.cost, program.program_id)
        )):
            raise ValueError("behavior programs must use canonical order")

    @property
    def representative(self) -> AmbientRecoveryProgram:
        return self.programs[0]

    def to_record(self) -> dict[str, Any]:
        return {
            "behavior_hash": self.behavior_hash,
            "predictions": self.predictions,
            "representative_program": self.representative.to_record(),
            "equivalent_program_count": len(self.programs),
            "equivalent_program_ids": [program.program_id for program in self.programs],
        }


@dataclass(frozen=True, slots=True)
class AmbientRecoveryReceipt:
    routed: bool
    complete: bool
    effect_coordinate: Mapping[str, Any]
    programs_enumerated: int
    demonstration_executions: int
    exact_programs: int
    probe_executions: int
    probe_rejections: int
    admitted_programs: int
    test_program_executions: int
    test_grid_executions: int
    runtime_failures: int
    behavior_classes: int
    limit_reached: str = ""

    def to_record(self) -> dict[str, Any]:
        return {
            "routed": self.routed,
            "complete": self.complete,
            "grammar_hash": GRAMMAR_HASH,
            "effect_coordinate": dict(self.effect_coordinate),
            "maximum_programs": MAXIMUM_PROGRAMS,
            "programs_enumerated": self.programs_enumerated,
            "demonstration_executions": self.demonstration_executions,
            "exact_programs": self.exact_programs,
            "probe_executions": self.probe_executions,
            "probe_rejections": self.probe_rejections,
            "admitted_programs": self.admitted_programs,
            "test_program_executions": self.test_program_executions,
            "test_grid_executions": self.test_grid_executions,
            "runtime_failures": self.runtime_failures,
            "behavior_classes": self.behavior_classes,
            "limit_reached": self.limit_reached,
        }


@dataclass(frozen=True, slots=True)
class AmbientRecoveryCompilation:
    exact_programs: tuple[AmbientRecoveryProgram, ...]
    surviving_programs: tuple[AmbientRecoveryProgram, ...]
    behaviors: tuple[AmbientRecoveryBehavior, ...]
    receipt: AmbientRecoveryReceipt
    allow_provisional: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.allow_provisional, bool):
            raise TypeError("allow_provisional must be Boolean")
        if self.receipt.behavior_classes != len(self.behaviors):
            raise ValueError("receipt behavior count is inconsistent")

    @property
    def selected_behavior(self) -> AmbientRecoveryBehavior | None:
        return self.behaviors[0] if len(self.behaviors) == 1 else None

    @property
    def selected_prediction(self) -> tuple[Grid, ...] | None:
        return None if self.selected_behavior is None else self.selected_behavior.predictions

    @property
    def ambiguous(self) -> bool:
        return len(self.behaviors) > 1

    @property
    def status(self) -> str:
        if not self.receipt.complete:
            return "limit_abstention"
        if not self.receipt.routed:
            return "not_routed"
        if self.ambiguous:
            return "ambiguous_abstention"
        return "unique" if self.selected_behavior is not None else "no_candidate"

    def to_record(self) -> dict[str, Any]:
        body: dict[str, Any] = {
            "schema": COMPILATION_SCHEMA,
            "schema_version": SCHEMA_VERSION,
            "status": self.status,
            "allow_provisional": self.allow_provisional,
            "exact_programs": [program.to_record() for program in self.exact_programs],
            "surviving_program_ids": [program.program_id for program in self.surviving_programs],
            "behaviors": [behavior.to_record() for behavior in self.behaviors],
            "selected_behavior_hash": (
                self.selected_behavior.behavior_hash if self.selected_behavior else ""
            ),
            "ambiguous": self.ambiguous,
            "receipt": self.receipt.to_record(),
        }
        body["content_hash"] = digest(body)
        return body


_EXECUTION_ERRORS = (
    AssertionError, IndexError, KeyError, OverflowError, RuntimeError,
    TypeError, ValueError, ZeroDivisionError,
)


def _empty_compilation(
    *, routed: bool, complete: bool, effect: Mapping[str, Any],
    allow_provisional: bool, programs_enumerated: int = 0, limit_reached: str = "",
) -> AmbientRecoveryCompilation:
    return AmbientRecoveryCompilation(
        (), (), (),
        AmbientRecoveryReceipt(
            routed, complete, effect, programs_enumerated, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            limit_reached,
        ),
        allow_provisional,
    )


def compile_ambient_recovery(
    task: Mapping[str, Any], *, allow_provisional: bool = False,
    limits: AmbientRecoveryLimits | None = None,
) -> AmbientRecoveryCompilation:
    """Compile the complete locked grammar without observing test targets."""
    if not isinstance(allow_provisional, bool):
        raise TypeError("allow_provisional must be Boolean")
    limits = limits or AmbientRecoveryLimits()
    if isinstance(task, Mapping) and (
        isinstance(task.get("train"), Sequence)
        and len(task["train"]) == 0
        or isinstance(task.get("test"), Sequence)
        and len(task["test"]) == 0
    ):
        return _empty_compilation(
            routed=False, complete=True, effect={"kind": "empty_task"},
            allow_provisional=allow_provisional,
        )
    safe_task = sanitized_task_mapping(task)
    training = safe_task["train"]
    tests = safe_task["test"]
    if not training or not tests:
        return _empty_compilation(
            routed=False, complete=True, effect={"kind": "empty_task"},
            allow_provisional=allow_provisional,
        )
    if len(training) > limits.max_training_examples:
        return _empty_compilation(
            routed=False, complete=False, effect={"kind": "limit"},
            allow_provisional=allow_provisional, limit_reached="training_example_limit",
        )
    if len(tests) > limits.max_test_examples:
        return _empty_compilation(
            routed=False, complete=False, effect={"kind": "limit"},
            allow_provisional=allow_provisional, limit_reached="test_example_limit",
        )
    pairs = tuple(
        (validate_grid(example["input"]), validate_grid(example["output"]))
        for example in training
    )
    test_inputs = tuple(validate_grid(example["input"]) for example in tests)
    effect = _effect_coordinate(pairs)
    programs = enumerate_programs(pairs, test_inputs)
    routed = bool(programs)
    if not routed:
        return _empty_compilation(
            routed=False, complete=True, effect=effect,
            allow_provisional=allow_provisional,
        )
    if len(programs) > MAXIMUM_PROGRAMS:
        return _empty_compilation(
            routed=True, complete=False, effect=effect,
            allow_provisional=allow_provisional,
            programs_enumerated=len(programs), limit_reached="program_enumeration_limit",
        )

    exact: list[AmbientRecoveryProgram] = []
    demonstration_executions = 0
    for program in programs:
        accepted = True
        for source, target in pairs:
            demonstration_executions += 1
            try:
                observed = execute_program(program, source)
            except _EXECUTION_ERRORS:
                accepted = False
                break
            if observed != target:
                accepted = False
                break
        if accepted:
            exact.append(program)

    probed: list[AmbientRecoveryProgram] = []
    probe_executions = 0
    probe_rejections = 0
    for program in exact:
        passed, work = _probe(program, pairs)
        probe_executions += work
        if passed:
            probed.append(program)
        else:
            probe_rejections += 1
    admitted = [
        program for program in probed
        if allow_provisional or not program.provisional
    ]

    groups: dict[str, dict[str, Any]] = {}
    surviving: list[AmbientRecoveryProgram] = []
    test_program_executions = 0
    test_grid_executions = 0
    runtime_failures = 0
    for program in admitted:
        test_program_executions += 1
        outputs = []
        try:
            for grid in test_inputs:
                test_grid_executions += 1
                outputs.append(execute_program(program, grid))
        except _EXECUTION_ERRORS:
            runtime_failures += 1
            continue
        surviving.append(program)
        predictions = tuple(outputs)
        behavior_hash = digest(predictions)
        group = groups.setdefault(behavior_hash, {"predictions": predictions, "programs": []})
        if group["predictions"] != predictions:
            raise AssertionError("behavior hash collision")
        group["programs"].append(program)

    behaviors = []
    for behavior_hash, group in sorted(groups.items()):
        behavior_programs = tuple(sorted(
            group["programs"], key=lambda program: (program.cost, program.program_id)
        ))
        behaviors.append(AmbientRecoveryBehavior(
            behavior_hash, group["predictions"], behavior_programs,
        ))
    receipt = AmbientRecoveryReceipt(
        routed=True,
        complete=True,
        effect_coordinate=effect,
        programs_enumerated=len(programs),
        demonstration_executions=demonstration_executions,
        exact_programs=len(exact),
        probe_executions=probe_executions,
        probe_rejections=probe_rejections,
        admitted_programs=len(admitted),
        test_program_executions=test_program_executions,
        test_grid_executions=test_grid_executions,
        runtime_failures=runtime_failures,
        behavior_classes=len(behaviors),
    )
    return AmbientRecoveryCompilation(
        tuple(exact), tuple(surviving), tuple(behaviors), receipt, allow_provisional,
    )


__all__ = [
    "AmbientRecoveryBehavior", "AmbientRecoveryCompilation", "AmbientRecoveryLimits",
    "AmbientRecoveryProgram", "AmbientRecoveryReceipt", "ContractError",
    "GRAMMAR_CONTRACT", "GRAMMAR_HASH", "MAXIMUM_PROGRAMS", "PROVISIONAL_FAMILIES",
    "REJECTED_BROAD_FAMILIES", "SAFE_FAMILIES", "STABLE_FAMILIES",
    "compile_ambient_recovery", "enumerate_programs", "execute_program",
]
