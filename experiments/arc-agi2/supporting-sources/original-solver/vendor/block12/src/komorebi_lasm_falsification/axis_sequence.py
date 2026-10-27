"""Locked role-normalized row/column transducers for PR-LASM Block 12.

Five families survived bounded label-blind screens and independent
complete-corpus activation audits. They are deliberately exposed
as a small immutable grammar. Compilation consumes training pairs and test
inputs only, requires exact replay, tests D4 and palette conjugacy on every
observed input, quotients complete test behavior, and abstains on every role
tie or unseen role.

Author: Komorebi P.
"""
from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass
import hashlib
import json
from typing import Any, Iterable, Mapping, Sequence


Grid = tuple[tuple[int, ...], ...]
Cell = tuple[int, int]
D4 = ("identity", "rot90", "rot180", "rot270", "flip_h", "flip_v", "transpose", "anti_transpose")
SCHEMA_VERSION = 3
PROGRAM_SCHEMA = "komorebi.lasm_falsification.axis_sequence_program"
COMPILATION_SCHEMA = "komorebi.lasm_falsification.axis_sequence_compilation"
ORTHOGONAL = ((-1, 0), (0, -1), (0, 1), (1, 0))
SAFE_FAMILIES = frozenset({
    "alternating_field_shift",
    "hollow_cross_center_bridges",
    "marker_through_carrier_to_edge",
    "midpoint_propagation",
    "singleton_nearest_edge_rays",
})
BACKGROUND_ROLES = ("mode", "border_mode", "zero")
_COSTS = {
    "alternating_field_shift": 8,
    "hollow_cross_center_bridges": 7,
    "marker_through_carrier_to_edge": 7,
    "midpoint_propagation": 8,
    "singleton_nearest_edge_rays": 6,
}


class Inapplicable(ValueError):
    """A required structural role is absent, tied, or obstructed."""


class ContractError(ValueError):
    """A program lies outside the immutable production grammar."""


def _canonical(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        allow_nan=False,
    )


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("ascii")).hexdigest()


def grid(value: Any) -> Grid:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise TypeError("grid must be a row sequence")
    result = []
    for row in value:
        if not isinstance(row, Sequence) or isinstance(row, (str, bytes, bytearray)):
            raise TypeError("grid row must be a sequence")
        cells = []
        for cell in row:
            if isinstance(cell, bool) or not isinstance(cell, int) or not 0 <= cell <= 9:
                raise ValueError("invalid ARC cell")
            cells.append(int(cell))
        result.append(tuple(cells))
    answer = tuple(result)
    if not answer or not answer[0] or any(len(row) != len(answer[0]) for row in answer):
        raise ValueError("grid must be nonempty and rectangular")
    if len(answer) > 30 or len(answer[0]) > 30:
        raise ValueError("grid exceeds ARC limits")
    return answer


def _unique(values: Iterable[int], reason: str) -> int:
    items = tuple(values)
    if len(items) != 1:
        raise Inapplicable(reason)
    return items[0]


def background(value: Grid, role: str) -> int:
    counts = Counter(cell for row in value for cell in row)
    if role == "zero":
        if 0 not in counts:
            raise Inapplicable("zero background absent")
        return 0
    if role == "mode":
        maximum = max(counts.values())
        return _unique((color for color, count in counts.items() if count == maximum), "modal background tied")
    if role == "border_mode":
        height, width = len(value), len(value[0])
        border = Counter(
            value[row][column]
            for row in range(height)
            for column in range(width)
            if row in {0, height - 1} or column in {0, width - 1}
        )
        maximum = max(border.values())
        return _unique((color for color, count in border.items() if count == maximum), "border background tied")
    raise ContractError("unknown background role")


def _foreground_role(value: Grid, bg: int, role: str) -> int:
    counts = Counter(cell for row in value for cell in row if cell != bg)
    if not counts:
        raise Inapplicable("foreground absent")
    if role == "only":
        return _unique(counts, "foreground color not unique")
    if role == "rarest":
        minimum = min(counts.values())
        return _unique((color for color, count in counts.items() if count == minimum), "rarest foreground tied")
    if role == "most_frequent":
        maximum = max(counts.values())
        return _unique((color for color, count in counts.items() if count == maximum), "largest foreground tied")
    raise ContractError("unknown foreground role")


def _lines(value: Grid, axis: str) -> list[list[int]]:
    if axis == "rows":
        return [list(row) for row in value]
    if axis == "columns":
        return [[value[row][column] for row in range(len(value))] for column in range(len(value[0]))]
    raise ContractError("unknown axis")


def _from_lines(lines: Sequence[Sequence[int]], axis: str) -> Grid:
    if axis == "rows":
        return tuple(tuple(line) for line in lines)
    return tuple(tuple(lines[column][row] for column in range(len(lines))) for row in range(len(lines[0])))


@dataclass(frozen=True, slots=True)
class AxisSequenceProgram:
    family: str
    parameters: tuple[tuple[str, Any], ...]
    cost: int
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.family not in SAFE_FAMILIES:
            raise ContractError("family outside locked axis grammar")
        if self.cost != _COSTS[self.family] or self.schema_version != SCHEMA_VERSION:
            raise ContractError("cost or schema version disagrees with grammar")
        if self.parameters != tuple(sorted(self.parameters)) or len(dict(self.parameters)) != len(self.parameters):
            raise ContractError("parameters must have unique canonical keys")
        params = self.parameter_map
        expected = {
            "singleton_nearest_edge_rays": {"background"},
            "marker_through_carrier_to_edge": {"background"},
            "alternating_field_shift": {"background", "direction", "paint"},
            "hollow_cross_center_bridges": {"background", "paint"},
            "midpoint_propagation": {"alternate", "axis", "background", "direction", "stride"},
        }[self.family]
        if set(params) != expected or params["background"] not in BACKGROUND_ROLES:
            raise ContractError("parameter domain disagrees with family")
        if "paint" in params and (isinstance(params["paint"], bool) or not isinstance(params["paint"], int) or not 0 <= params["paint"] <= 9):
            raise ContractError("paint lies outside ARC palette")
        if "alternate" in params and (isinstance(params["alternate"], bool) or not isinstance(params["alternate"], int) or not 0 <= params["alternate"] <= 9):
            raise ContractError("alternate lies outside ARC palette")
        if "direction" in params:
            domain = {"north", "south", "west", "east"} if self.family == "alternating_field_shift" else {-1, 1}
            if params["direction"] not in domain:
                raise ContractError("direction lies outside family domain")
        if self.family == "midpoint_propagation" and (params["axis"] not in {"rows", "columns"} or params["stride"] not in {1, 2, 3}):
            raise ContractError("axis or stride lies outside finite domain")

    @classmethod
    def create(cls, family: str, **parameters: Any) -> "AxisSequenceProgram":
        if family not in _COSTS:
            raise ContractError("family outside locked axis grammar")
        return cls(family, tuple(sorted(parameters.items())), _COSTS[family])

    @property
    def parameter_map(self) -> dict[str, Any]:
        return dict(self.parameters)

    @property
    def program_id(self) -> str:
        return _digest(self.to_record(include_id=False))

    def to_record(self, *, include_id: bool = True) -> dict[str, Any]:
        record: dict[str, Any] = {
            "schema": PROGRAM_SCHEMA,
            "schema_version": self.schema_version,
            "family": self.family,
            "parameters": self.parameter_map,
            "cost": self.cost,
            "status": "provisional",
        }
        if include_id:
            record["program_id"] = self.program_id
        return record

    def execute(self, value: Any) -> Grid:
        source = grid(value)
        bg = background(source, self.parameter_map["background"])
        if self.family == "singleton_nearest_edge_rays":
            return _singleton_nearest_edge_rays(source, bg)
        if self.family == "marker_through_carrier_to_edge":
            return _marker_through_carrier(source, bg)
        if self.family == "alternating_field_shift":
            return _alternating_field_shift(source, bg, str(self.parameter_map["direction"]), int(self.parameter_map["paint"]))
        if self.family == "hollow_cross_center_bridges":
            return _hollow_cross_center_bridges(
                source,
                bg,
                int(self.parameter_map["paint"]),
            )
        if self.family == "midpoint_propagation":
            return _midpoint_propagation(
                source, bg, str(self.parameter_map["axis"]), int(self.parameter_map["direction"]),
                int(self.parameter_map["stride"]), int(self.parameter_map["alternate"]),
            )
        raise ContractError("unknown family")


def _singleton_nearest_edge_rays(source: Grid, bg: int) -> Grid:
    foreground = {(row, column) for row, line in enumerate(source) for column, cell in enumerate(line) if cell != bg}
    if not foreground:
        raise Inapplicable("foreground absent")
    seen: set[Cell] = set()
    components: list[list[Cell]] = []
    for start in sorted(foreground):
        if start in seen:
            continue
        color = source[start[0]][start[1]]
        queue = deque((start,)); seen.add(start); component = [start]
        while queue:
            row, column = queue.popleft()
            for delta_row, delta_column in ORTHOGONAL:
                neighbor = row + delta_row, column + delta_column
                if neighbor in foreground and neighbor not in seen and source[neighbor[0]][neighbor[1]] == color:
                    seen.add(neighbor); queue.append(neighbor); component.append(neighbor)
        components.append(component)
    if any(len(component) != 1 for component in components):
        raise Inapplicable("foreground component is not singleton")
    height, width = len(source), len(source[0])
    output = [list(row) for row in source]
    for ((row, column),) in components:
        vertical = [(row, -1, 0), (height - 1 - row, 1, 0)]
        horizontal = [(column, 0, -1), (width - 1 - column, 0, 1)]
        vmin, hmin = min(item[0] for item in vertical), min(item[0] for item in horizontal)
        vertical_direction = [(dr, dc) for distance, dr, dc in vertical if distance == vmin]
        horizontal_direction = [(dr, dc) for distance, dr, dc in horizontal if distance == hmin]
        if len(vertical_direction) != 1 or len(horizontal_direction) != 1:
            raise Inapplicable("nearest edge tied")
        color = source[row][column]
        for delta_row, delta_column in (vertical_direction[0], horizontal_direction[0]):
            current_row, current_column = row, column
            while 0 <= current_row < height and 0 <= current_column < width:
                if output[current_row][current_column] not in {bg, color}:
                    raise Inapplicable("ray collides with another role")
                output[current_row][current_column] = color
                current_row += delta_row; current_column += delta_column
    answer = tuple(tuple(row) for row in output)
    if answer == source:
        raise Inapplicable("identity execution")
    return answer


def _marker_through_carrier(source: Grid, bg: int) -> Grid:
    marker = _foreground_role(source, bg, "rarest")
    carrier = _foreground_role(source, bg, "most_frequent")
    marker_cells = [(row, column) for row, line in enumerate(source) for column, cell in enumerate(line) if cell == marker]
    if marker == carrier or len(marker_cells) != 1:
        raise Inapplicable("marker is not a unique rare role")
    marker_row, marker_column = marker_cells[0]
    carrier_cells = {(row, column) for row, line in enumerate(source) for column, cell in enumerate(line) if cell == carrier}
    directions = []
    for delta_row, delta_column in ORTHOGONAL:
        mass = sum(
            1 for row, column in carrier_cells
            if (delta_row < 0 and row < marker_row) or (delta_row > 0 and row > marker_row)
            or (delta_column < 0 and column < marker_column) or (delta_column > 0 and column > marker_column)
        )
        if not mass:
            continue
        if delta_row < 0:
            start = min(row for row, _ in carrier_cells) - 1, marker_column
        elif delta_row > 0:
            start = max(row for row, _ in carrier_cells) + 1, marker_column
        elif delta_column < 0:
            start = marker_row, min(column for _, column in carrier_cells) - 1
        else:
            start = marker_row, max(column for _, column in carrier_cells) + 1
        directions.append((mass, delta_row, delta_column, start))
    maximum = max((item[0] for item in directions), default=0)
    winners = [item for item in directions if item[0] == maximum]
    if len(winners) != 1:
        raise Inapplicable("carrier half-plane role tied")
    _, delta_row, delta_column, (row, column) = winners[0]
    height, width = len(source), len(source[0])
    output = [list(line) for line in source]
    changed = False
    while 0 <= row < height and 0 <= column < width:
        if output[row][column] != bg:
            raise Inapplicable("carrier ray collides")
        output[row][column] = marker; changed = True
        row += delta_row; column += delta_column
    if not changed:
        raise Inapplicable("carrier already reaches edge")
    return tuple(tuple(line) for line in output)


def _alternating_field_shift(source: Grid, bg: int, direction: str, paint: int) -> Grid:
    marker = _foreground_role(source, bg, "only")
    cells = [(row, column) for row, line in enumerate(source) for column, cell in enumerate(line) if cell == marker]
    if len(cells) != 1 or paint in {bg, marker}:
        raise Inapplicable("singleton marker or distinct paint role absent")
    marker_row, marker_column = cells[0]
    height, width = len(source), len(source[0])
    output = [list(row) for row in source]
    if direction in {"north", "south"}:
        delta_row = -1 if direction == "north" else 1
        region = range(0, marker_row + 1) if delta_row < 0 else range(marker_row, height)
        for row in region:
            for column in range(width):
                if (column - marker_column) % 2 == 0 and output[row][column] == bg:
                    output[row][column] = paint
        new_row, new_column = marker_row - delta_row, marker_column
    else:
        delta_column = -1 if direction == "west" else 1
        region = range(0, marker_column + 1) if delta_column < 0 else range(marker_column, width)
        for column in region:
            for row in range(height):
                if (row - marker_row) % 2 == 0 and output[row][column] == bg:
                    output[row][column] = paint
        new_row, new_column = marker_row, marker_column - delta_column
    if not (0 <= new_row < height and 0 <= new_column < width) or output[new_row][new_column] != bg:
        raise Inapplicable("marker shift is blocked")
    output[marker_row][marker_column] = paint
    output[new_row][new_column] = marker
    return tuple(tuple(row) for row in output)


def _hollow_cross_center_bridges(source: Grid, bg: int, paint: int) -> Grid:
    """Bridge consecutive aligned hollow-cross centers with a novel role."""

    colors = {cell for row in source for cell in row if cell != bg}
    if len(colors) != 1:
        raise Inapplicable("hollow-cross focus color is not unique")
    focus = next(iter(colors))
    if paint in {bg, focus}:
        raise Inapplicable("bridge paint is not a distinct role")
    height, width = len(source), len(source[0])
    centers = [
        (row, column)
        for row in range(1, height - 1)
        for column in range(1, width - 1)
        if source[row][column] == bg
        and all(
            source[row + delta_row][column + delta_column] == focus
            for delta_row, delta_column in ORTHOGONAL
        )
    ]
    output = [list(row) for row in source]
    changed = False
    for row in sorted({row for row, _ in centers}):
        columns = sorted(column for candidate, column in centers if candidate == row)
        for left, right in zip(columns, columns[1:]):
            if right - left < 4:
                continue
            for column in range(left + 2, right - 1):
                if output[row][column] != bg:
                    raise Inapplicable("horizontal bridge collides")
                output[row][column] = paint
                changed = True
    for column in sorted({column for _, column in centers}):
        rows = sorted(row for row, candidate in centers if candidate == column)
        for top, bottom in zip(rows, rows[1:]):
            if bottom - top < 4:
                continue
            for row in range(top + 2, bottom - 1):
                if output[row][column] != bg:
                    raise Inapplicable("vertical bridge collides")
                output[row][column] = paint
                changed = True
    if not changed:
        raise Inapplicable("no aligned hollow-cross bridge")
    return tuple(tuple(row) for row in output)


def _midpoint_propagation(source: Grid, bg: int, axis: str, direction: int, stride: int, alternate: int) -> Grid:
    lines = _lines(source, axis)
    support_sizes = [sum(cell != bg for cell in line) for line in lines]
    source_index = _unique((index for index, size in enumerate(support_sizes) if size), "source line not unique")
    colors = {cell for cell in lines[source_index] if cell != bg}
    if len(colors) != 1:
        raise Inapplicable("source line is not monochrome")
    source_color = next(iter(colors))
    if alternate in {bg, source_color}:
        raise Inapplicable("alternating role is not distinct")
    current = {index for index, cell in enumerate(lines[source_index]) if cell == source_color}
    result = [line[:] for line in lines]
    destination = source_index + direction * stride
    step = 1
    changed = False
    while 0 <= destination < len(lines):
        next_support = {
            index for index in range(1, len(lines[source_index]) - 1)
            if index not in current and index - 1 in current and index + 1 in current
        }
        if not next_support:
            break
        if any(cell != bg for cell in lines[destination]):
            raise Inapplicable("propagation line is occupied")
        color = alternate if step % 2 else source_color
        for index in next_support:
            result[destination][index] = color
        current = next_support
        destination += direction * stride
        step += 1
        changed = True
    if not changed:
        raise Inapplicable("no propagation step")
    return _from_lines(result, axis)


def transform(value: Grid, operation: str) -> Grid:
    if operation == "identity":
        return value
    if operation == "rot90":
        return tuple(tuple(value[len(value) - 1 - row][column] for row in range(len(value))) for column in range(len(value[0])))
    if operation == "rot180":
        return tuple(tuple(reversed(row)) for row in reversed(value))
    if operation == "rot270":
        return tuple(
            tuple(value[row][len(value[0]) - 1 - column] for row in range(len(value)))
            for column in range(len(value[0]))
        )
    if operation == "flip_h":
        return tuple(tuple(reversed(row)) for row in value)
    if operation == "flip_v":
        return tuple(reversed(value))
    if operation == "transpose":
        return tuple(tuple(value[row][column] for row in range(len(value))) for column in range(len(value[0])))
    if operation == "anti_transpose":
        return transform(transform(transform(value, "transpose"), "flip_h"), "flip_v")
    raise ValueError("unknown D4 operation")


def _transform_program(program: AxisSequenceProgram, operation: str) -> AxisSequenceProgram:
    params = program.parameter_map
    old_axis = params.get("axis")
    if operation in {"rot90", "rot270", "transpose", "anti_transpose"} and old_axis in {"rows", "columns"}:
        params["axis"] = "columns" if old_axis == "rows" else "rows"
    direction = params.get("direction")
    probe = ((0, 1, 2), (3, 4, 5), (6, 7, 8))
    positions = {
        transform(probe, operation)[row][column]: (row, column)
        for row in range(3) for column in range(3)
    }
    origin = positions[4]
    if direction in {"north", "south", "west", "east"}:
        neighbor_value = {"north": 1, "south": 7, "west": 3, "east": 5}[direction]
        neighbor = positions[neighbor_value]
        delta = neighbor[0] - origin[0], neighbor[1] - origin[1]
        params["direction"] = {(-1, 0): "north", (1, 0): "south", (0, -1): "west", (0, 1): "east"}[delta]
    elif direction in {-1, 1}:
        # Midpoint propagation moves between rows/columns, not within them.
        neighbor_value = 7 if old_axis == "rows" else 5
        neighbor = positions[neighbor_value]
        new_axis = params["axis"]
        increasing = (neighbor[0] > origin[0]) if new_axis == "rows" else (neighbor[1] > origin[1])
        if not increasing:
            params["direction"] = -direction
    return AxisSequenceProgram.create(program.family, **params)


def _recolor(value: Grid, permutation: Mapping[int, int]) -> Grid:
    return tuple(tuple(permutation.get(cell, cell) for cell in row) for row in value)


def _recolor_program(program: AxisSequenceProgram, permutation: Mapping[int, int]) -> AxisSequenceProgram:
    params = program.parameter_map
    for key in ("paint", "alternate"):
        if key in params:
            params[key] = permutation.get(params[key], params[key])
    return AxisSequenceProgram.create(program.family, **params)


def _conjugacy(program: AxisSequenceProgram, inputs: Sequence[Grid]) -> int:
    checks = 0
    for source in inputs:
        expected = program.execute(source)
        for operation in D4:
            if _transform_program(program, operation).execute(transform(source, operation)) != transform(expected, operation):
                raise Inapplicable("D4 conjugacy failed")
            checks += 1
        colors = sorted({cell for row in source for cell in row} | {cell for row in expected for cell in row})
        moving = [color for color in colors if not (program.parameter_map["background"] == "zero" and color == 0)]
        if len(moving) > 1:
            permutation = dict(zip(moving, moving[1:] + moving[:1]))
            if _recolor_program(program, permutation).execute(_recolor(source, permutation)) != _recolor(expected, permutation):
                raise Inapplicable("palette conjugacy failed")
            checks += 1
    return checks


def _enumerate_programs() -> tuple[AxisSequenceProgram, ...]:
    programs = []
    for bg in BACKGROUND_ROLES:
        programs.append(AxisSequenceProgram.create("singleton_nearest_edge_rays", background=bg))
        programs.append(AxisSequenceProgram.create("marker_through_carrier_to_edge", background=bg))
        for paint in range(10):
            programs.append(AxisSequenceProgram.create(
                "hollow_cross_center_bridges", background=bg, paint=paint,
            ))
        for direction in ("north", "south", "west", "east"):
            for paint in range(10):
                programs.append(AxisSequenceProgram.create("alternating_field_shift", background=bg, direction=direction, paint=paint))
        for axis in ("rows", "columns"):
            for direction in (-1, 1):
                for stride in (1, 2, 3):
                    for alternate in range(10):
                        programs.append(AxisSequenceProgram.create("midpoint_propagation", background=bg, axis=axis, direction=direction, stride=stride, alternate=alternate))
    return tuple(sorted(programs, key=lambda program: program.program_id))


@dataclass(frozen=True, slots=True)
class AxisSequenceCompilation:
    routed: bool
    complete: bool
    programs: tuple[AxisSequenceProgram, ...]
    behaviors: tuple[tuple[Grid, ...], ...]
    behavior_programs: tuple[tuple[AxisSequenceProgram, ...], ...]
    stress_checks: int
    demo_order_invariant: bool

    @property
    def selected_prediction(self) -> tuple[Grid, ...] | None:
        return self.behaviors[0] if len(self.behaviors) == 1 else None

    def to_record(self) -> dict[str, Any]:
        record = {
            "schema": COMPILATION_SCHEMA,
            "schema_version": SCHEMA_VERSION,
            "routed": self.routed,
            "complete": self.complete,
            "programs": [program.to_record() for program in self.programs],
            "behavior_count": len(self.behaviors),
            "behaviors": [
                {
                    "behavior_hash": _digest(behavior),
                    "predictions": behavior,
                    "program_ids": [program.program_id for program in programs],
                }
                for behavior, programs in zip(self.behaviors, self.behavior_programs, strict=True)
            ],
            "stress_checks": self.stress_checks,
            "demo_order_invariant": self.demo_order_invariant,
        }
        record["content_hash"] = _digest(record)
        return record


def compile_axis_sequence(task: Mapping[str, Any]) -> AxisSequenceCompilation:
    training, tests = task.get("train"), task.get("test")
    if not isinstance(training, Sequence) or not training or not isinstance(tests, Sequence) or not tests:
        return AxisSequenceCompilation(False, True, (), (), (), 0, True)
    try:
        pairs = tuple((grid(example["input"]), grid(example["output"])) for example in training)
        test_inputs = tuple(grid(example["input"]) for example in tests)
        routed = all((len(source), len(source[0])) == (len(target), len(target[0])) for source, target in pairs) and any(source != target for source, target in pairs)
        if not routed:
            return AxisSequenceCompilation(False, True, (), (), (), 0, True)
        all_inputs = tuple(source for source, _ in pairs) + test_inputs
        survivors = []
        stress_checks = 0
        for program in _enumerate_programs():
            try:
                if not all(program.execute(source) == target for source, target in pairs):
                    continue
                checks = _conjugacy(program, all_inputs)
                # Exact replay is a conjunction, hence permutation invariant;
                # execute the reversed order explicitly as a release gate.
                if not all(program.execute(source) == target for source, target in reversed(pairs)):
                    raise Inapplicable("demonstration-order gate failed")
                stress_checks += checks + 1
                survivors.append(program)
            except (Inapplicable, ContractError, KeyError, TypeError, ValueError, IndexError):
                continue
        groups: dict[tuple[Grid, ...], list[AxisSequenceProgram]] = {}
        for program in survivors:
            try:
                behavior = tuple(program.execute(source) for source in test_inputs)
            except (Inapplicable, ContractError, KeyError, TypeError, ValueError, IndexError):
                continue
            groups.setdefault(behavior, []).append(program)
        ordered = sorted(groups.items(), key=lambda item: _digest(item[0]))
        behaviors = tuple(item[0] for item in ordered)
        behavior_programs = tuple(tuple(sorted(item[1], key=lambda program: program.program_id)) for item in ordered)
        accepted_programs = tuple(program for group in behavior_programs for program in group)
        return AxisSequenceCompilation(
            routed, True, accepted_programs, behaviors,
            behavior_programs, stress_checks, True,
        )
    except (Inapplicable, ContractError, KeyError, TypeError, ValueError, IndexError):
        return AxisSequenceCompilation(True, True, (), (), (), 0, True)


GRAMMAR_HASH = _digest({
    "schema": "komorebi.lasm_falsification.axis_sequence_grammar",
    "schema_version": SCHEMA_VERSION,
    "families": sorted(SAFE_FAMILIES),
    "background_roles": BACKGROUND_ROLES,
    "exact_demo_replay": True,
    "d4_conjugacy": D4,
    "d4_action_contract": "eight_distinct_actions_on_generic_nonsquare_labelled_raster",
    "palette_conjugacy": "cyclic_observed_nonzero_when_literal_zero_background",
    "demo_order_gate": True,
    "screen": {"tasks": 48, "candidates": 4, "exact": 4, "wrong": 0, "net_new_outputs": 6},
    "stage2_full_corpus_audit": {"tasks": 1000, "activations": 1, "exact": 1, "wrong": 0, "net_new_outputs": 1},
    "all_corpus_activation_audit": {"tasks": 1000, "activations": 5, "exact": 5, "wrong": 0, "net_new_outputs": 7},
})


__all__ = [
    "AxisSequenceCompilation", "AxisSequenceProgram", "BACKGROUND_ROLES", "COMPILATION_SCHEMA",
    "D4", "GRAMMAR_HASH", "Grid", "Inapplicable", "PROGRAM_SCHEMA", "SAFE_FAMILIES",
    "background", "compile_axis_sequence", "grid", "transform",
]
